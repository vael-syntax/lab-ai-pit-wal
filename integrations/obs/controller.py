import asyncio

class ObsMockController:
    def __init__(self, event_bus):
        self.bus = event_bus
        self._running = False
        
    async def start(self):
        self._running = True
        # Nos suscribimos al evento general de cargar escena que orquestará el programa principal
        self.bus.subscribe("load_scene", self._on_load_scene)
        self.bus.subscribe("speak_avatar", self._on_speak_avatar)
        print("[OBS Dummy] Conectado (Modo Simulación). Esperando comandos...")

    async def _on_load_scene(self, payload):
        target_scene = payload.get("scene_name", "Desconocida")
        print(f"\n📺 [OBS Dummy] ---> ¡CAMBIO DE ESCENA! Activando: '{target_scene}'")
        
    async def _on_speak_avatar(self, payload):
        is_speaking = payload.get("is_speaking", False)
        state = "HABLANDO 🗣️" if is_speaking else "CALLADO 🤐"
        print(f"🎬 [OBS Dummy] ---> Estado del VTube/Avatar: {state}")

    async def stop(self):
        self._running = False
        print("[OBS Dummy] Desconectado.")
