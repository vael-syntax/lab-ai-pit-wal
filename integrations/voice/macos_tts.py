import asyncio
import sys

class MacOSTTS:
    """
    Integrador de voz utilizando el comando nativo `say` de macOS.
    Sirve como alternativa local y gratuita a motores de pago como ElevenLabs.
    """
    def __init__(self, event_bus):
        self.bus = event_bus
        self._running = False
        
        # Validar que estamos en una Mac
        if sys.platform != "darwin":
            print("[Voz macOS] ADVERTENCIA: Este módulo está diseñado para macOS. Puede no funcionar.")

    async def start(self):
        self._running = True
        self.bus.subscribe("text_generated", self._on_text_generated)
        print("[Voz local] 🎙️ Conectado usando 'say' (macOS Nativo). Listo para hablar.")

    async def _on_text_generated(self, payload):
        if not self._running:
            return
            
        text = payload.get("text")
        if not text:
            return

        print(f"\n🎙️ [Voz macOS] Hablando texto: '{text}'...")
        await self.bus.publish("speak_avatar", {"is_speaking": True})
        
        try:
            # Seleccionamos una voz española para el comando nativo
            # Si quieres cambiarla: Paulina, Mónica, Jorge o Diego
            import subprocess
            voz = "Jorge" 
            
            # Ejecutamos el comando 'say' de forma asíncrona para no bloquear el Bus de Eventos
            proc = await asyncio.create_subprocess_exec(
                "say", "-v", voz, text,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Esperamos a que termine de hablar antes de apagar el avatar
            await proc.wait()
            
        except Exception as e:
            print(f"   [Voz macOS] Error al ejecutar 'say': {e}")
            
        finally:
            await self.bus.publish("speak_avatar", {"is_speaking": False})

    async def stop(self):
        self._running = False
        print("[Voz macOS] Apagado.")
