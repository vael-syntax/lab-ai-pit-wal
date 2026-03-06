import asyncio
import time
import psutil
from perception.vision.capture import VisionCapture
from core.event_bus import EventBus

async def run_benchmark(duration_seconds: int = 10, fps_target: int = 30):
    print(f"===================================================")
    print(f"🏎️ Vael Benchmarking Tactic: RAM Capture Stress Test")
    print(f"===================================================")
    print(f"Pauta: {duration_seconds} segundos apilando frames a {fps_target} FPS.")
    print("Midiendo latencia de ciclo y degradación de memoria...\n")

    bus = EventBus()
    await bus.start()
    
    # Reducimos intervalo a lo equivalente al FPS target
    interval = 1.0 / fps_target
    vision = VisionCapture(event_bus=bus, targets=["benchmark"], interval=interval)
    
    frames_captured = 0
    start_time = time.time()
    
    # Monitor de consumo
    process = psutil.Process()
    ram_start = process.memory_info().rss / (1024 * 1024)

    async def on_frame(payload):
        nonlocal frames_captured
        frames_captured += 1

    bus.subscribe("frame_captured", on_frame)
    await vision.start()

    # Dejar correr el motor
    await asyncio.sleep(duration_seconds)
    
    await vision.stop()
    await bus.stop()

    end_time = time.time()
    elapsed = end_time - start_time
    ram_end = process.memory_info().rss / (1024 * 1024)
    
    real_fps = frames_captured / elapsed

    print(f"\n[ Resultado Final del Stress Test ]")
    print(f"▶ Frames Generados: {frames_captured}")
    print(f"▶ FPS Teórico: {fps_target} | FPS Real Sostenido: {real_fps:.2f}")
    if real_fps < (fps_target * 0.8):
        print(f"⚠️ ALERTA: Rendimiento I/O por debajo del 80% esperado. Posible saturación del Event Thread por PIL.")
    print(f"▶ Memoria Inicial: {ram_start:.2f} MB | Memoria Final: {ram_end:.2f} MB (Delta: {ram_end - ram_start:.2f} MB)")
    print(f"===================================================")

if __name__ == "__main__":
    asyncio.run(run_benchmark(duration_seconds=5, fps_target=15))
