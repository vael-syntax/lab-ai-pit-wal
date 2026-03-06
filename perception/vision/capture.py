import asyncio
import base64
from mss import mss
from io import BytesIO
from PIL import Image

class VisionCapture:
    def __init__(self, event_bus, targets, interval=5.0):
        self.bus = event_bus
        self.targets = targets
        self.interval = interval
        self._running = False
        self.sct = mss()

    async def start(self):
        self._running = True
        print(f"[Vision] Iniciando captura de pantalla periódica ({self.interval}s) en RAM...")
        asyncio.create_task(self._capture_loop())

    async def stop(self):
        self._running = False
        print("[Vision] Captura detenida.")

    async def _capture_loop(self):
        while self._running:
            try:
                # 1. Tomar screenshot (la primera pantalla por defecto)
                monitor = self.sct.monitors[1]
                screenshot = self.sct.grab(monitor)
                
                # 2. Convertir a imagen PIL (Procesamiento directo en Memoria)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Opcional: Redimensionar para no enviar tanta data al LLM y ahorrar RAM/Ancho de banda
                img.thumbnail((1280, 720))
                
                # 3. Guardar en memoria (BytesIO) y codificar a Base64
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=75) # Compresión JPEG ligera
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # 4. Evaluación de Prioridad (Simulada para Interrupt Demo)
                # En un entorno real, aquí se procesaría telemetría o bbox del yolo.
                priority_flag = "low"
                if "roja" in [t.lower() for t in self.targets] or "choque" in [t.lower() for t in self.targets]:
                    priority_flag = "high"
                    print("[Vision] ⚠️ CRÍTICO: Objetivo prioritario en mira. Pidiendo interrupción global.")
                    await self.bus.publish("audio_interrupt", {"reason": "visual_critical_anomaly"})

                payload = {
                    "image_b64": base64_image,
                    "targets_expected": self.targets,
                    "priority": priority_flag
                }
                
                # print("[Vision] Captura en RAM completada, publicando evento 'frame_captured'...")
                await self.bus.publish("frame_captured", payload)
                
            except Exception as e:
                print(f"[Vision] Error capturando pantalla: {e}")
            
            # Esperar el intervalo (sin bloquear)
            await asyncio.sleep(self.interval)
