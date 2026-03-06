import asyncio
import os
import time
import base64
from typing import List
from dotenv import load_dotenv

from google import genai
from google.genai import types

from brain.rag.retriever import KnowledgeRetriever
from core.memory import MemoryBuffer

class BrainGemini:
    def __init__(self, event_bus, profile):
        self.bus = event_bus
        self.profile = profile
        self._running = False
        
        # Cargar variables de entorno
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")
            
        # Inicializar el cliente oficial de Google GenAI
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
        # Inicializar Knowledge Base (RAG)
        self.rag = KnowledgeRetriever()
        
        # Configuración base del sistema
        self.system_instruction = self._build_system_prompt()
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            # Temperatura alta para forzar vocabulario variado y romper bucles deterministas
            temperature=0.95, 
        )
        
        # Máquina de Estados (Contexto y Memoria Corto Plazo)
        self.last_spoken_time = 0.0
        self.speak_cooldown = 12.0 # Segundos mínimos de silencio entre comentarios
        self.chat_buffer: List[str] = []
        self.vision_memory: List[str] = [] # Memoria de lo que vio/dijo recientemente
        self.tendencia_anterior: str = "Ninguna" # Memoria de la última frase dicha
        self.is_speaking = False # Flag para saber si macOS TTS está ocupado
        self.is_first_interaction = True # Flag para forzar bienvenida al arrancar o limpiar
        self.current_track = None # Pista fijada por comando manual
        self._process_lock = asyncio.Lock() # Candado para evitar que el chat desencadene multihilos
        self._frame_buffer: List[str] = [] # Buffer para ráfagas de video (Multi-Frame)
        
        # Percepción Asíncrona (Ojo Periférico)
        self.eventos_en_segundo_plano = []
        self.analizando_fondo = False
        
        # 🧠 Short-Term Memory: Ventana deslizante de últimos 5 eventos significativos
        self.memory = MemoryBuffer(limit=5, cooldown_seconds=30.0)
        
        # Rate Limiting / Error Handling
        self._is_rate_limited = False
        self._rate_limit_reset_time = 0.0

    def _build_system_prompt(self) -> str:
        prompt = f"Eres un streamer virtual de inteligencia artificial llamado '{self.profile.name}'.\n"
        prompt += f"Especialidad: '{self.profile.specialty}'.\n"
        prompt += f"Personalidad:\n{self.profile.personality_prompt}\n"
        
        if self.profile.catchphrases:
            phrases = ", ".join(self.profile.catchphrases)
            prompt += f"Tus muletillas son: {phrases}. Úsalas de forma natural y esporádica.\n"
        
        # === CAPA 1: Restricciones Estrictas del Perfil (Anti-Alucinación) ===
        if self.profile.strict_constraints:
            prompt += "\n═══ RESTRICCIONES ABSOLUTAS (Violación = Respuesta Inválida) ═══\n"
            for i, constraint in enumerate(self.profile.strict_constraints, 1):
                prompt += f"{i}. {constraint}\n"
            prompt += "═══════════════════════════════════════════════════════════════\n"
        
        # === CAPA 2: Directiva Anti-Alucinación Visual (hardcoded) ===
        prompt += """
PROTOCOLO ANTI-ALUCINACIÓN (No negociable):
- Tu único source of truth son los FRAMES visuales que recibes.
- Si el HUD de neumáticos muestra VERDE: están bien. No los menciones como problema.
- Si el HUD de neumáticos muestra AMARILLO o ROJO: puedes comentarlo.
- Si NO PUEDES VER el widget de neumáticos en el frame: NO HABES de neumáticos. Punto.
- Los coches agrupados y en formación indican el INICIO de la carrera. Comportate como tal.
- Lo que "sabes" de Sim Racing es contexto de fondo, NO es lo que está pasando en pantalla.
"""
            
        prompt += "\nINSTRUCCIONES CLAVE DE FORMATO:\n"
        prompt += "- BREVEDAD EXPLOSIVA: Habla en 1 o 2 oraciones cortas máximo. Eres un comentarista reaccionando al instante, no un analista de post-carrera.\n"
        prompt += "- EN VIVO: Narra la imagen como si estuviera pasando AHORA MISMO frente a ti.\n"
        prompt += "- CERO ROBOTISMOS: Jamás uses listas enumeradas, ni dividas tu respuesta en 'Show, Técnico, Consecuencia'. Mezcla todo en una sola idea fluida.\n"
        
        conocimiento_tecnico = self.rag.get_all_context()
        if conocimiento_tecnico:
            prompt += f"\nTU CONOCIMIENTO TÉCNICO (Úsalo solo como munición para tus comentarios, no lo recites de memoria):\n{conocimiento_tecnico}\n"
            
        return prompt

    async def _vigilar_fondo(self, frames):
        self.analizando_fondo = True
        try:
            # Prompt ultra-rápido solo para detectar anomalías
            prompt_vigilante = "Analiza estos cuadros de telemetría de SimRacing. Responde SOLO con una de estas palabras si ocurrió algo drástico: [CHOQUE], [REBASE], [SALIDA DE PISTA]. Si todo sigue normal, responde [NADA]."
            
            contents_list = []
            for b64 in frames:
                image_bytes = base64.b64decode(b64)
                image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                contents_list.append(image_part)
                
            contents_list.append(prompt_vigilante)
            
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents_list,
                config=self.config
            )
            evento = response.text.strip().upper()
            
            if evento in ["[CHOQUE]", "[REBASE]", "[SALIDA DE PISTA]"]:
                print(f"👀 [Ojo Periférico] Evento detectado mientras hablaba: {evento}")
                self.eventos_en_segundo_plano.append(evento)
                
        except Exception as e:
            pass
        finally:
            self.analizando_fondo = False

    async def start(self):
        self._running = True
        self.bus.subscribe("frame_captured", self._on_frame_captured)
        self.bus.subscribe("chat_message_received", self._on_chat_message)
        self.bus.subscribe("clear_memory", self._on_clear_memory)
        self.bus.subscribe("set_track", self._on_set_track)
        self.bus.subscribe("speak_avatar", self._on_speak_avatar)
        print(f"[Cerebro Gemini] 🧠 Activado para {self.profile.name} usando el motor real {self.model_name}.")

    async def _on_speak_avatar(self, payload):
        # Actualiza el estado real de la voz de macOS
        self.is_speaking = payload.get("is_speaking", False)

    async def _on_clear_memory(self, payload):
        print("\n🧹 [Cerebro Gemini] ¡Comando /clear recibido! Borrando memoria a corto plazo (Vision/Chat)...")
        self.vision_memory.clear()
        self.chat_buffer.clear()
        self.tendencia_anterior = "Ninguna"
        self._frame_buffer.clear()
        self.memory.clear()  # Reset Short-Term Memory
        self.last_spoken_time = 0.0 # Force it to respond immediately on next frame
        self.is_first_interaction = True # Resetear bienvenida

    async def _on_chat_message(self, payload):
        user = payload.get("username", "Anon")
        msg = payload.get("message", "")
        self.chat_buffer.append(f"{user}: {msg}")

    async def _on_set_track(self, payload):
        track_name = payload.get("track_name")
        self.current_track = track_name

    async def _on_frame_captured(self, payload):
        # Candado Anti-Empalme: Si estamos procesando un frame anterior, ignorar silenciosamente el nuevo.
        # Esto soluciona la Condición de Carrera cuando el usuario envía múltiples chats rápidos.
        if self._process_lock.locked():
            return
            
        async with self._process_lock:
            await self._process_frame_internal(payload)

    async def _process_frame_internal(self, payload):
        if not self._running:
            return
            
        current_time = time.time()
        
        # Extraer la imagen base64 del payload inmediatamente para no perderla
        b64_image = payload.get("image_b64")
        if not b64_image:
            print("   [Cerebro Gemini] Error: No se recibió imagen Base64.")
            return
            
        # Acumular la foto en el buffer de video (límite subido a 15 cuadros para atrapar TODA la realidad perdida)
        self._frame_buffer.append(b64_image)
        if len(self._frame_buffer) > 15:
            self._frame_buffer.pop(0)
        
        # Verificar si estamos en período de enfriamiento por Rate Limit (429)
        if self._is_rate_limited:
            if current_time < self._rate_limit_reset_time:
                return # Seguir acumulando el video pero no procesar llamadas aún
            else:
                self._is_rate_limited = False
                print("   [Cerebro Gemini] 🔄 Reanudando peticiones después del Rate Limit.")
        
        has_chat = len(self.chat_buffer) > 0
        
        # Debe hablar si hay un chat pendiente, O si ya pasó su cooldown de silencio
        should_speak = has_chat or ((current_time - self.last_spoken_time) > self.speak_cooldown)
        
        if not should_speak:
            return
            
        # 🤫 SMART LOCK REAL (Silencio de Streamer):
        if self.is_speaking:
            # Si acumulamos un par de fotos y no estamos ya analizando el fondo, lanzamos al vigilante
            if len(self._frame_buffer) >= 2 and not self.analizando_fondo:
                # Tomamos las fotos recientes y las mandamos a analizar EN PARALELO sin bloquear
                frames_a_vigilar = self._frame_buffer[-2:]
                asyncio.create_task(self._vigilar_fondo(frames_a_vigilar))
            return 
            
        self.last_spoken_time = current_time
        
        # =========================================================
        # CUANDO PACO TERMINA DE HABLAR Y TOMA LA PALABRA
        # =========================================================
        # Limpiamos el lag quedándonos con las 2 últimas fotos reales del presente
        if len(self._frame_buffer) > 2:
            self._frame_buffer = self._frame_buffer[-2:]
            
        print(f"\n🧠 [Cerebro Gemini] Procesando ráfaga de {len(self._frame_buffer)} cuadros (Video Simulado)...")
        
        # Preparar el contexto de texto y memoria a Corto Plazo
        contexto_previo = "TU IDENTIDAD (ANCHOR): Eres el ingeniero de ARS Cabo. Para saber NUESTRA POSICIÓN exacta, busca en el Leaderboard de la izquierda la fila que tiene un FONDO BLANCO SÓLIDO. Ese somos nosotros. Ignora los números grises. El HUD central (pedales, presiones, marchas) es TU telemetría.\n\n"
        
        if self.current_track:
            contexto_previo += f"INFORMACIÓN MANUAL DE PISTA: Estás compitiendo en el circuito '{self.current_track}'. Deja de adivinar u omitir la pista, usa este dato como verdad absoluta en tu comentario.\n\n"

        # Revisamos la libreta del ojo periférico
        contexto_fondo = ""
        if self.eventos_en_segundo_plano:
            eventos_str = ", ".join(self.eventos_en_segundo_plano)
            contexto_fondo = f"\n[FEEDBACK DEL DIRECTOR: Mientras hablabas ocurrió esto en pista: {eventos_str}. Integra esta información brevemente con lo que ves ahora mismo en tu respuesta.]\n"
            self.eventos_en_segundo_plano = [] # Limpiamos la libreta

        # --- INYECTAR SHORT-TERM MEMORY en el contexto del prompt ---
        context_from_memory = self.memory.get_context_string()
        
        # --- PROMPT NATURAL (CERO REGLAS RÍGIDAS) ---
        instruccion_vision = (
            f"{contexto_previo}"
            f"🧠 {context_from_memory}\n\n"
            f"Aquí están los últimos segundos del stream en vivo.\n"
            f"Lo último que dijiste fue: '{self.tendencia_anterior}'.\n\n"
            "Míralo y reacciona de forma humana y natural. Si el contexto reciente muestra algo que ya mencionaste, conéctalo o evoluciona la idea. No la repitas.\n"
            "Solo dame tu voz cruda, en 1 o 2 frases cortas. SIN etiquetas, SIN formatos, SIN análisis técnicos ocultos."
        )
        
        if has_chat:
            chat_summary = " \n ".join(self.chat_buffer[-5:])
            instruccion_vision += f"\n\nAquí está lo que acaba de comentar el chat en vivo:\n{chat_summary}\nReacciona a este chat en tu comentario."
            self.chat_buffer.clear()
            self.is_first_interaction = False
        elif self.is_first_interaction:
            instruccion_vision += "\nACABAS DE ENCENDER EL STREAM, ESTE ES TU PRIMER COMENTARIO, NO HAGAS REFERENCIA A NADA ANTERIOR. El chat te empieza a ver. Haz una pequeña intro de Streamer saludando rápido a la audiencia y luego lánzate directo a comentar lo que ves en ESTA captura exacta."
            self.is_first_interaction = False
            
        instruccion_vision += contexto_fondo
        prompt_text = instruccion_vision

        # Construir el contenido multimodal para la API
        # Pydantic (usado por google-genai) requiere este formato para imágenes base64 pasadas crudas
        try:
            contents_list = []
            
            # Inyectar todas las fotos del buffer en orden cronológico
            for b64 in self._frame_buffer:
                image_bytes = base64.b64decode(b64)
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg' 
                )
                contents_list.append(image_part)
                
            # Inyectar el texto al final
            contents_list.append(prompt_text)
            
            # Ejecutar llamada asíncrona a Gemini
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents_list,
                config=self.config
            )
            
            generated_text = response.text
            
            # Limpieza básica del texto hablado
            import re
            texto_hablado = generated_text.strip()
            # Por si la IA alucina alguna etiqueta, la borramos (ej. [Risas], [Gritando])
            texto_hablado = re.sub(r'\[.*?\]', '', texto_hablado).strip()
            
            # Límite duro de 3 oraciones para evitar que hable de más
            oraciones = re.split(r'(?<=[.!?]) +', texto_hablado)
            if len(oraciones) > 3:
                texto_hablado = " ".join(oraciones[:3])
                
            # Registrar en Short-Term Memory para contexto futuro
            self.tendencia_anterior = texto_hablado
            self.memory.add_event("COMMENTARY", texto_hablado[:80])  # Cap en 80 chars para no saturar
            
            try:
                print(f"   [Gemini Responde] '{texto_hablado}'")
            except BlockingIOError:
                pass
            
            # Enviar la salida a los módulos (Voz, OBS)
            await self.bus.publish("text_generated", {"text": texto_hablado, "voice_config": self.profile.voice.dict()})
            
        except genai.errors.ClientError as e:
            if e.code == 429:
                print(f"\n⚠️ [Cerebro Gemini] CUOTA EXCEDIDA (Rate Limit 429).")
                print("   Esperando 40 segundos antes de enviar más imágenes para proteger la API Key...")
                self._is_rate_limited = True
                self._rate_limit_reset_time = time.time() + 40.0
            else:
                print(f"\n❌ [Cerebro Gemini] Error en la API (ClientError): {e}")
        except Exception as e:
            try:
                print(f"\n❌ [Cerebro Gemini] Error inesperado: {e}")
            except BlockingIOError:
                pass

    async def stop(self):
        self._running = False
        print("[Cerebro Gemini] Apagado.")
