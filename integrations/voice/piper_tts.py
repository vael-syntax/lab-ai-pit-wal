import asyncio
import numpy as np
import sounddevice as sd
from piper import PiperVoice
from core.event_bus import EventBus

class PiperTTS:
    def __init__(self, event_bus: EventBus, model_path: str, config_path: str):
        self.bus = event_bus
        self.queue = asyncio.Queue()
        self._running = False
        
        # Cargar el modelo de voz optimizado
        print("[Piper TTS] ⏳ Cargando modelo de voz local...")
        self.voice = PiperVoice.load(model_path, config_path)
        self.sample_rate = self.voice.config.sample_rate
        print(f"[Piper TTS] ✅ Modelo cargado (Sample Rate: {self.sample_rate})")

    async def start(self):
        self._running = True
        self.bus.subscribe("text_generated", self._on_text_generated)
        print("[Piper TTS] 🎙️ Escuchando textos para sintetizar...")
        # Iniciar el worker que procesa la cola de audio
        asyncio.create_task(self._audio_worker())

    async def _on_text_generated(self, payload):
        text = payload.get("text", "").strip()
        if text:
            # Ponemos el texto en la cola en lugar de bloquear
            await self.queue.put(text)

    async def _audio_worker(self):
        while self._running:
            text = await self.queue.get()
            
            # Avisamos al sistema (y a Gemini) que vamos a hablar
            await self.bus.publish("speak_avatar", {"is_speaking": True})
            
            try:
                print(f"\n🎙️ [Piper TTS] Hablando: '{text}'")
                
                # Sintetizar audio crudo y reproducirlo en tiempo real
                audio_stream = self.voice.synthesize(text)
                
                # Reproducir usando sounddevice (bloquea solo este hilo hasta que termina la frase)
                with sd.RawOutputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
                    for chunk in audio_stream:
                        stream.write(chunk.audio_int16_bytes)
                        
            except Exception as e:
                print(f"[Piper TTS] ❌ Error reproduciendo audio: {e}")
            finally:
                # Avisamos que terminamos de hablar
                await self.bus.publish("speak_avatar", {"is_speaking": False})
                self.queue.task_done()

    async def stop(self):
        self._running = False
        print("[Piper TTS] Apagado.")
