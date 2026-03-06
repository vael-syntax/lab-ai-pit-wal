import asyncio
from aioconsole import ainput

class LocalChatCLI:
    def __init__(self, event_bus):
        self.bus = event_bus
        self._running = False
        self._worker_task = None
        
    async def start(self):
        self._running = True
        self._worker_task = asyncio.create_task(self._input_loop())
        print("[Chat Local] 💬 Conectado. (Escribe en esta consola para interactuar con el Streamer)")

    async def _input_loop(self):
        # Le damos un pequeño delay para que el texto de inicio no se pegue con el prompt
        await asyncio.sleep(2)
        while self._running:
            try:
                msg = await ainput("Tú (Chat): ")
                if msg.strip():
                    if msg.strip().lower() == "/clear":
                        print("[Chat Local] 🧹 Solicitando limpieza de memoria del cerebro...")
                        await self.bus.publish("clear_memory", {})
                    elif msg.strip().lower().startswith("/pista "):
                        # Comando para setear la pista manualmente
                        pista_name = msg.strip()[7:].strip()
                        print(f"[Chat Local] 🏎️ Forzando detector de pista a: {pista_name}")
                        await self.bus.publish("set_track", {"track_name": pista_name})
                    else:
                        await self.bus.publish("chat_message_received", {
                            "username": "UsuarioLocal",
                            "message": msg.strip()
                        })
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Chat Local] Error leyendo entrada: {e}")

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
        print("[Chat Local] 💬 Desconectado.")
