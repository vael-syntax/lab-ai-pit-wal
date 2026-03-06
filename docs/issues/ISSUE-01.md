# ISSUE-01: Optimización de la serialización Base64 para reducir carga de CPU

**Estado:** Abierto
**Etiquetas:** `enhancement`, `performance`, `perception-layer`

## Descripción
Actualmente, el módulo `perception/vision/capture.py` realiza la captura y compresión de frames usando `PIL` para transformarlos a JPEG y luego a encriptación Base64 directamente en la RAM. 
Si bien la latencia de disco (I/O) se ha eliminado, este proceso bloquea el hilo principal momentáneamente y genera picos en la CPU al codificar grandes matrices de píxeles (`1280x720`).

## Objetivo
Refactorizar el pipeline de serialización Base64 para que sea menos costoso computacionalmente, sin sacrificar la topología Zero-I/O actual.

## Propuesta de Solución Arquitectónica
1. **Asincronía total:** Extraer la rutina de compresión `PIL` y conversión B64 a un hilo secundario empleando `asyncio.to_thread()`, liberando el loop principal del Event Bus.
2. **Reducción de Frame Size:** Bajar el thumbnail de captura a `640x360`. Gemini 1.5 es extremadamente bueno deduciendo contexto a menores resoluciones.
3. **OpenCV Swap:** Evaluar si `cv2.imencode('.jpg', frame)` arroja menores tiempos de ciclo (CPU time) frente a `PIL.Image.save()` en este entorno específico.
