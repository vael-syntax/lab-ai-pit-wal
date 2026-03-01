import asyncio
import time

from typing import List

class BrainLLMMock:
    def __init__(self, event_bus, profile):
        self.bus = event_bus
        self.profile = profile
        self._running = False
        
        # Máquina de Estados (Contexto y Memoria Corto Plazo)
        self.last_spoken_time = 0.0
        self.speak_cooldown = 10.0 # Segundos mínimos entre comentarios para no ser molesto
        self.chat_buffer: List[str] = []

    async def start(self):
        self._running = True
        self.bus.subscribe("frame_captured", self._on_frame_captured)
        self.bus.subscribe("chat_message_received", self._on_chat_message)
        print(f"[Cerebro] Activado para {self.profile.name}. (Comportamiento Avanzado: Buffer y Silencio Dinámico)")

    async def _on_chat_message(self, payload):
        user = payload.get("username", "Anon")
        msg = payload.get("message", "")
        self.chat_buffer.append(f"{user}: {msg}")
        # print(f"   [Cerebro] Nuevo mensaje en buffer ({len(self.chat_buffer)} pendientes)")

    async def _on_frame_captured(self, payload):
        if not self._running:
            return
            
        current_time = time.time()
        
        # 1. ¿Vale la pena hablar ahora? (Leer la mesa)
        has_chat_to_read = len(self.chat_buffer) > 0
        silence_too_long = (current_time - self.last_spoken_time) > 25.0
        
        # Simulamos que la IA revisa si en la imagen pasó algo "crítico" (10% de probabilidad o similar en un mock)
        # Para el mock, solo hablaremos si hay chat acumulado o mucho silencio
        should_speak = has_chat_to_read or silence_too_long
        
        if not should_speak and (current_time - self.last_spoken_time) > self.speak_cooldown:
            # En modo "quieto" simplemente observa la imagen pero no dice nada
            return

        if not should_speak:
            return
            
        # Si decidimos hablar, actualizamos el cooldown para no spamear
        self.last_spoken_time = current_time
        
        print(f"\n🧠 [Cerebro LLM] Actuando... Analizando Frame visual y Contexto Social.")
        await asyncio.sleep(1.0) # Simulamos tiempo de inferencia de la API
        
        # 2. Resumir el chat
        chat_context = ""
        has_chat = len(self.chat_buffer) > 0
        
        if has_chat:
            chat_summary = " | ".join(self.chat_buffer[-5:]) # Máximo lee 5 mensajes
            chat_context = f"El chat dice: {chat_summary}"
            self.chat_buffer.clear() # Limpiamos porque ya los procesó
        else:
            chat_context = "El chat está silenciado. Comenta sobre el juego."
            
        print(f"   [Contexto Interno] {chat_context}")
        
        # 3. Generar respuesta
        simulated_response = ""
        if has_chat:
             # Respuesta al chat + muletilla
             catchphrase = self.profile.catchphrases[0] if self.profile.catchphrases else ""
             simulated_response = f"{catchphrase} Respondiendo al chat... chicos, estoy leyendo la pantalla."
        else:
             # Respuesta "Icebreaker" de silencio largo
             catchphrase = self.profile.catchphrases[-1] if len(self.profile.catchphrases) > 1 else ""
             simulated_response = f"{catchphrase} Mucho silencio por aquí, pero sigo atento a la jugada."
            
        print(f"   [Respuesta Generada] '{simulated_response}'")
        
        # 4. Enviar a Módulos de Salida (ElevenLabs)
        await self.bus.publish("text_generated", {"text": simulated_response, "voice_config": self.profile.voice.dict()})
        
        # 5. Activar Animación
        await self.bus.publish("speak_avatar", {"is_speaking": True})
        await asyncio.sleep(2) # Tiempo simulado hablando
        await self.bus.publish("speak_avatar", {"is_speaking": False})

    async def stop(self):
        self._running = False
        print("[Cerebro] Apagado.")
