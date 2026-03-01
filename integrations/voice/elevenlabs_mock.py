import asyncio

class ElevenLabsMock:
    def __init__(self, event_bus):
        self.bus = event_bus
        self._running = False
        
    async def start(self):
        self._running = True
        # Se suscribe a los textos generados por el cerebro
        self.bus.subscribe("text_generated", self._on_text_generated)
        print("[Voz Dummy] Conectado a ElevenLabs (Modo Simulación). Listo para sintetizar audio.")

    async def _on_text_generated(self, payload):
        if not self._running:
            return
            
        text = payload.get("text", "")
        voice_config = payload.get("voice_config", {})
        
        provider = voice_config.get("provider", "ElevenLabs")
        voice_id = voice_config.get("voice_id", "Desconocido")
        stability = voice_config.get("stability", 0.5)
        
        print(f"\n🎙️ [Módulo de Voz - {provider}] Recibí texto para el Cerebro.")
        print(f"   [Voz] Parámetros -> VoiceID: {voice_id} | Stability: {stability}")
        print(f"   [Voz] Sintetizando audio para: '{text}'...")
        
        # Simular delay de la API al generar TTS (Text-To-Speech)
        await asyncio.sleep(1) 
        print(f"   [Voz] Audio generado y 'reproduciéndose' en altavoz virtual 🔊")

    async def stop(self):
        self._running = False
        print("[Módulo de Voz] Desconectado.")
