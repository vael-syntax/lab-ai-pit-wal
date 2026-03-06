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
        self.interrupt_flag = False
        self.bus.subscribe("text_generated", self._on_text_generated)
        self.bus.subscribe("audio_interrupt", self._on_interrupt)
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
            payload = await self.queue.get()
            text = payload.get("text", "")
            priority = payload.get("priority", "low")
            
            # Si se activó la interrupción global y este mensaje no es de alta prioridad, lo descartamos
            if getattr(self, "interrupt_flag", False) and priority != "high":
                self.queue.task_done()
                continue
                
            await self.bus.publish("speak_avatar", {"is_speaking": True})
            
            try:
                print(f"\n🎙️ [Piper TTS] Hablando ({priority}): '{text}'")
                audio_stream = self.voice.synthesize(text)
                
                # Reseteamos flag temporalmente al empezar a hablar (a menos que siga activo)
                self.interrupt_flag = False
                
                with sd.RawOutputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
                    for chunk in audio_stream:
                        # Si en medio de la reproducción nos interrumpen, cortamos en seco
                        if getattr(self, "interrupt_flag", False) and priority != "high":
                            print(f"[Piper TTS] 🛑 Interrupción de emergencia. Cortando frase actual.")
                            break
                        stream.write(chunk.audio_int16_bytes)
                        # Yield control al event loop sin matar la RAM para permitir lectura de interrupciones
                        await asyncio.sleep(0.001)
                        
            except Exception as e:
                print(f"[Piper TTS] ❌ Error reproduciendo audio: {e}")
            finally:
                await self.bus.publish("speak_avatar", {"is_speaking": False})
                self.queue.task_done()

    async def _on_interrupt(self, payload):
        """Callback for high-priority events that demand immediate silence from the TTS."""
        print("[Piper TTS] ⚠️ Recibida señal de interrupción global. Purgando buffer de audio.")
        self.interrupt_flag = True
        # Purgamos los mensajes de baja prioridad pendientes en la cola
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except asyncio.QueueEmpty:
                break

    async def stop(self):
        self._running = False
        print("[Piper TTS] Apagado.")
