# ISSUE-03: Benchmarking de latencia entre Gemini 1.5 Flash vs Pro

**Estado:** Abierto
**Etiquetas:** `research`, `benchmarking`, `latency`

## Descripción
En un entorno de Sim Racing de alta densidad y velocidad (e.g. Assetto Corsa Competizione), la latencia es inaceptable. El sistema actualmente invoca a `Google Gemini 1.5 Pro`, lo cual ofrece un análisis visual sobresaliente pero introduce un retardo de entre `2.5s - 4.5s` desde la captura de pantalla (Optical Nerve) hasta el play del TTS (Vocal Tract).

## Objetivo
Ejecutar un análisis de latencia comparativo directo entre la capacidad analítica multivariada de `1.5 Pro` y la velocidad extrema de `1.5 Flash` para determinar el estándar arquitectónico de *The Pit Wall*.

## Análisis Requerido
1. **Medición End-to-End:** Capturar el *timestamp* de emisión de `capture.py`, paso por Event Bus, generación LLM, y retorno del script de voz.
2. **Evaluación Cognitiva:** Documentar si `Gemini 1.5 Flash` es capaz de entender el *Topic Roulette* y la telemetría visual (Base64) con la misma precisión descriptiva (sin halucinaciones de trazada).
3. **Decisión Arquitectónica:** Si `1.5 Flash` es capaz, se convertirá en el modelo por defecto. `1.5 Pro` quedará reservado solo para *Debriefings* post-carrera o análisis profundos donde la latencia no sea crítica.
