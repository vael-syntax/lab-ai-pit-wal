import asyncio
import os
import time
import base64
from typing import List
from dotenv import load_dotenv

from google import genai
from google.genai import types

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
        
        # Configuración base del sistema
        self.system_instruction = self._build_system_prompt()
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            # Le damos creatividad pero lo mantenemos enfocado
            temperature=0.7, 
        )
        
        # Máquina de Estados (Contexto y Memoria Corto Plazo)
        self.last_spoken_time = 0.0
        self.speak_cooldown = 12.0 # Segundos mínimos de silencio entre comentarios
        self.chat_buffer: List[str] = []

    def _build_system_prompt(self) -> str:
        prompt = f"Eres un streamer virtual de inteligencia artificial llamado '{self.profile.name}'. "
        prompt += f"Tu especialidad o estilo es: '{self.profile.specialty}'. "
        prompt += f"Tu personalidad es: '{self.profile.personality_prompt}'. "
        if self.profile.catchphrases:
            phrases = ", ".join(self.profile.catchphrases)
            prompt += f"Tus muletillas y frases típicas son: {phrases}. Úsalas de vez en cuando, pero no siempre. "
            
        prompt += "\nINSTRUCCIONES CLAVE:\n"
        prompt += "- Responde SIEMPRE de manera breve, de 1 a 3 oraciones máximo. Eres un streamer hablando rápido, no estás escribiendo un ensayo.\n"
        prompt += "- Habla en primera persona.\n"
        prompt += "- El sistema te enviará fotos de lo que estás 'jugando' o 'viendo' en tu pantalla, y también te enviará comentarios de tu Chat.\n"
        prompt += "- Cuando leas el chat, prioriza contestar a la gente simulando que estás jugando al mismo tiempo.\n"
        prompt += "- No seas robótico. Reacciona emocionalmente a lo que ves. Si mueres en el juego, quéjate. Si un usuario del chat te insulta, responde con humor o sarcasmo.\n"
        return prompt

    async def start(self):
        self._running = True
        self.bus.subscribe("frame_captured", self._on_frame_captured)
        self.bus.subscribe("chat_message_received", self._on_chat_message)
        print(f"[Cerebro Gemini] 🧠 Activado para {self.profile.name} usando el motor real {self.model_name}.")

    async def _on_chat_message(self, payload):
        user = payload.get("username", "Anon")
        msg = payload.get("message", "")
        self.chat_buffer.append(f"{user}: {msg}")

    async def _on_frame_captured(self, payload):
        if not self._running:
            return
            
        current_time = time.time()
        
        has_chat = len(self.chat_buffer) > 0
        silence_too_long = (current_time - self.last_spoken_time) > 25.0
        
        # El cerebro real evaluará cada frame si hay chat o si hubo mucho silencio.
        # Podríamos hacer que evalúe CADA frame, pero gastaríamos muchos tokens por minuto.
        # Por ahora mantendremos la regla de "Hablar si hay interacción o silencio".
        should_speak = has_chat or silence_too_long
        
        if not should_speak and (current_time - self.last_spoken_time) > self.speak_cooldown:
            return

        if not should_speak:
            return
            
        self.last_spoken_time = current_time
        
        print("\n🧠 [Cerebro Gemini] Procesando multimodal (Imagen + Chat)...")
        
        # Preparar el contexto de texto
        if has_chat:
            chat_summary = " \n ".join(self.chat_buffer[-5:])
            prompt_text = f"Aquí está lo que acaba de comentar el chat en vivo:\n{chat_summary}\n"
            prompt_text += "Reacciona o responde al chat mientras comentas rápidamente sobre lo que ves en la pantalla."
            self.chat_buffer.clear()
        else:
            prompt_text = "El chat está silenciado. Mira la pantalla e inventa un comentario espontáneo sobre la situación."

        # Extraer la imagen base64 del payload
        b64_image = payload.get("image_b64")
        if not b64_image:
            print("   [Cerebro Gemini] Error: No se recibió imagen Base64.")
            return

        # Construir el contenido multimodal para la API
        # Pydantic (usado por google-genai) requiere este formato para imágenes base64 pasadas crudas
        try:
            # Decodificar el base64 a bytes crudos para Gemini
            image_bytes = base64.b64decode(b64_image)
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg' 
            )
            
            # Ejecutar llamada asíncrona a Gemini
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt_text],
                config=self.config
            )
            
            generated_text = response.text
            print(f"   [Gemini Responde] '{generated_text}'")
            
            # Enviar la salida a los módulos (Voz, OBS)
            await self.bus.publish("text_generated", {"text": generated_text, "voice_config": self.profile.voice.dict()})
            
            await self.bus.publish("speak_avatar", {"is_speaking": True})
            # El tiempo de hablar dependerá del largo del texto (estimación burda)
            habla_estimada = len(generated_text) * 0.08
            await asyncio.sleep(habla_estimada)
            await self.bus.publish("speak_avatar", {"is_speaking": False})
            
        except Exception as e:
            print(f"   [Cerebro Gemini] Error en la API de Google: {e}")

    async def stop(self):
        self._running = False
        print("[Cerebro Gemini] Apagado.")
