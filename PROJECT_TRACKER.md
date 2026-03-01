# Galan AI Streamer Hub v2.0 - Tracker de Proyecto

Este documento sirve como "Punto de Guardado" 💾 para retomar el proyecto en cualquier momento. Aquí registramos lo que ya funciona, lo que está pendiente y cualquier nota técnica relevante.

## 🚀 Estado Actual (Avances)
**Fecha de última actualización:** 28 de Febrero de 2026

*   **Estructura Base Creada:** Toda la jerarquía de carpetas (`core`, `profiles`, `perception`, `brain`, `integrations`) está lista.
*   **Entorno Virtual:** Creado e instalado con dependencias iniciales (`pydantic`, `PyYAML`).
*   **Gestor de Perfiles:** 
    *   Definido el esquema base con Pydantic (`profiles/schema.py`).
    *   Perfiles de prueba funcionales: `tony.yaml` y `paco_boxes.yaml`.
*   **Orquestador Central:** Script asíncrono funcional (`core/orchestrator.py`) que lee perfiles por terminal y carga dependencias.
*   **EventBus Asíncrono:** Sistema Pub/Sub implementado (`core/event_bus.py`) manejando eventos asíncronos para comunicar los diferentes módulos sin bloqueos de hilo principal.

## 📝 Pendientes (Siguientes Pasos)
Lista priorizada de tareas que siguen para continuar el desarrollo:

- [x] **1. Integración Chat Local (Prueba sin OBS/Twitch)**
    - [x] Crear módulo `integrations/chat/local_cli.py` con `aioconsole` para capturar teclado asíncronamente.
    - [x] Publicar eventos `chat_message_received` al EventBus.
- [x] **2. Integración con OBS (Salidas)**
    - [x] Configurar cliente `obs-websocket-py` dentro de `integrations/obs/`.
    - [x] Crear listeners en el Orquestador para que cuando se cargue un perfil, mande un evento al bus "load_scene" y el módulo de OBS cambie la escena del avatar automáticamente.
- [x] **3. Cerebro Inteligente (Integración Gemini Real)**
    - [x] Instalar dependencias (`google-genai`, `python-dotenv`).
    - [x] Configurar variables de entorno seguras (`.env`).
    - [x] Programar `brain/llm/gemini_engine.py` para analizar el Base64 visual asíncronamente junto con el chat y devolver análisis narrativos.
    - [x] Integrar en `core/orchestrator.py`.
- [x] **2. Módulo de Visión (Zero-Disk Writes)**
    - [x] Crear script que tome capturas usando `mss` y las mantenga **directamente en memoria RAM (Base64)** sin guardar en el disco de la Mac.
    - [ ] Integrar un VLM en la nube (OpenAI/Gemini Vision API) para analizar la pantalla enviando el *stream* Base64 directamente.
    - [ ] Opcional: Integrar YOLO para detección en tiempo real.
- [x] **4. Cerebro (RAG y LLM) - Módulo Mock**
    - [x] Configurar cliente de LLM en `brain/llm/`.
    - [x] **IA Avanzada:** Implementar la "Máquina de Estados de Comportamiento".
    - [x] **Silencio Dinámico:** No hablar con cada frame, solo si la situación lo amerita (leer la mesa).
    - [x] **Buffer de Chat:** Agrupar mensajes de chat recibidos para responder al chat y al video al mismo tiempo.
- [ ] **5. Módulo de Voz (macOS Native TTS)**
    - Crear `integrations/voice/macos_tts.py` usando el comando asíncrono `say` nativo de Mac.
    - Omitir depender de ElevenLabs por ahora para pruebas 100% locales y gratuitas.
    - Reproducir el audio resultante.

## 🧠 Notas Arquitectónicas Clave
*   **Ejecución:** Todo el núcleo debe usarse usando `asyncio`. Evitar el uso de librerías bloqueantes (`time.sleep()`, requests sincrónicas sin wrappers).
*   **Eventos:** Cualquier nuevo sistema no debe llamar directamente a otros. Debe publicar en el Event Bus (`test_bus.publish('evento_xyz', data)`).
*   **Zero-Disk Writes:** Por restricción de hardware de la Mac (almacenamiento limitado), **NUNCA** se deben guardar imágenes de la visión en disco (`.png`, `.jpg`). Todo el procesamiento visual (Screenshots de MSS, frames de OBS o lectura de YOLO) debe manejarse exclusivamente como bytes en RAM y enviarse como Payload (ej. Base64) al Orquestador y a los LLMs.

---
*Si cerramos el chat, la próxima vez que abramos uno nuevo dile al agente que lea este archivo `PROJECT_TRACKER.md` para recuperar todo su contexto automáticamente.*
