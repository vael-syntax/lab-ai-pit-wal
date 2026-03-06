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
        self._current_process = None # Puntero al proceso de voz actual para permitir Interrupciones (Kill)
        
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

        # Palabras que justifican interrumpir al Streamer (Modo Crónica/Crisis)
        urgent_keywords = ["¡", "CHOQUE", "ACCIDENTE", "REBASE", "ADELANTAMIENTO", "CUIDADO", "URGENTE", "DIOS", "CRIMINAL"]
        is_urgent = any(word in text.upper() for word in urgent_keywords)

        # 🚀 INTERRUPT SELECTIVO & DROP QUEUE (Anti-Lag):
        if self._current_process is not None and self._current_process.returncode is None:
            if is_urgent:
                print("   [Voz macOS] ⚡ [Interrupt & Merge] Interrumpiendo audio viejo por evento de CRISIS...")
                try:
                    self._current_process.kill()
                except Exception:
                    pass
            else:
                # El audio actual no ha terminado y la nueva frase NO es urgente.
                # Hacemos Drop Queue: descartamos el nuevo análisis para no generar lag.
                print("   [Voz macOS] 🚮 [Drop Queue] Audio ocupado y texto NO urgente. Descartando análisis para Cero Lag.")
                return

        try:
            # Imprimir de forma segura ignorando errores de buffer de la terminal
            sys.stdout.write(f"\n🎙️ [Voz macOS] Hablando texto: '{text}'...\n")
            sys.stdout.flush()
        except BlockingIOError:
            pass # Si la terminal se bloquea, ignoramos el print pero seguimos hablando
        await self.bus.publish("speak_avatar", {"is_speaking": True})
        
        try:
            import subprocess
            voz = "Jorge" 
            
            # Ejecutamos 'say' guardando el puntero
            self._current_process = await asyncio.create_subprocess_exec(
                "say", "-v", voz, text,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Esperamos a que termine (o a que sea asesinado)
            await self._current_process.wait()
            
        except Exception as e:
            print(f"   [Voz macOS] Error al ejecutar 'say': {e}")
            
        finally:
            # Apagamos el flag visual solo si nuestro proceso es el que terminó
            await self.bus.publish("speak_avatar", {"is_speaking": False})

    async def stop(self):
        self._running = False
        print("[Voz macOS] Apagado.")
