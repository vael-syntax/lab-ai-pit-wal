import sys
import yaml
import argparse
from pathlib import Path

# Ajustar PYTHONPATH temporalmente asumiendo ejecución desde directorio raíz
sys.path.append(str(Path(__file__).parent.parent))
from profiles.schema import ProfileSchema
import asyncio
from core.event_bus import EventBus
from perception.vision.capture import VisionCapture
from integrations.obs.controller import ObsMockController
from brain.llm.gemini_engine import BrainGemini
from integrations.voice.macos_tts import MacOSTTS
from integrations.chat.local_cli import LocalChatCLI

def load_profile(profile_path: str) -> ProfileSchema:
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(f"Profile {profile_path} no encontrado.")
    
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    
    # Validar con Pydantic
    profile = ProfileSchema(**data)
    return profile

async def main():
    parser = argparse.ArgumentParser(description="Galan AI Streamer Hub Orchestrator")
    parser.add_argument("profile", help="Ruta al archivo YAML del perfil a cargar (ej. profiles/tony.yaml)")
    args = parser.parse_args()

    print(f"[*] Inicializando AI Streamer Hub...")
    try:
        profile = load_profile(args.profile)
        print(f"[+] Perfil de '{profile.name}' cargado exitosamente.")
        print(f"    - Especialidad: {profile.specialty}")
        print(f"    - Módulo Visión: {profile.vision.model_type} ({'Activado' if profile.vision.enabled else 'Desactivado'})")
        print(f"    - Objetivos Visión: {', '.join(profile.vision.targets)}")
        print(f"    - Módulo Voz: {profile.voice.provider} (Estabilidad: {profile.voice.stability})")
        
        # Inicializar EventBus
        bus = EventBus()
        await bus.start()
        
        # Suscribirse a eventos básicos de ejemplo (ahora lo harán los módulos)
        # async def on_vision_event(payload):
        #    print(f"[Core] EVENTO VISIÓN RECIBIDO: {payload}")
        # bus.subscribe("vision_detected", on_vision_event)
        
        # ----------------------------------------------------
        # Inicializar Módulos Mock (OBS, Cerebro y Voz)
        # ----------------------------------------------------
        obs_module = ObsMockController(bus)
        await obs_module.start()
        
        # ! CAMBIO A CEREBRO REAL GEMINI API
        brain_module = BrainGemini(bus, profile)
        await brain_module.start()
        
        # ! CAMBIO A VOZ REAL MAC OS
        voice_module = MacOSTTS(bus)
        await voice_module.start()
        
        chat_module = LocalChatCLI(bus)
        await chat_module.start()
        
        # Simular que al cargar el programa, le decimos a OBS que cambie de escena al Streamer
        await bus.publish("load_scene", {"scene_name": f"Escena_{profile.name.replace(' ', '_')}"})

        # ----------------------------------------------------
        # Inicializar Módulo de Visión (Modo RAM/Base64)
        # ----------------------------------------------------
        vision_module = None
        if profile.vision.enabled:
            # En nuestro orquestador real, pasaremos los objetivos del YAML
            vision_module = VisionCapture(
                event_bus=bus, 
                targets=profile.vision.targets,
                interval=3.0 # Capturar cada 3 segundos
            )
            
            # Suscribirnos temporalmente para ver que sí está emitiendo
            async def on_frame_captured(payload):
                # Extraemos y recortamos el base64 solo para no inundar la consola
                b64_preview = payload["image_b64"][:30] + "... (Recortado)"
                print(f"[Core] -> RECIBIDO frame_captured. Objetivos: {payload['targets_expected']}, Imagen (B64): {b64_preview}")
            
            bus.subscribe("frame_captured", on_frame_captured)
            await vision_module.start()

        print(f"\n[*] Configuración de contexto completada. Esperando eventos...")
        
        # Mantener el orquestador corriendo
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[*] Apagando Orquestador...")
        if 'vision_module' in locals() and vision_module:
            await vision_module.stop()
        if 'chat_module' in locals():
            await chat_module.stop()
        if 'brain_module' in locals():
            await brain_module.stop()
        if 'voice_module' in locals():
            await voice_module.stop()
        if 'obs_module' in locals():
            await obs_module.stop()
        if 'bus' in locals():
            await bus.stop()
    except Exception as e:
        print(f"[!] Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
