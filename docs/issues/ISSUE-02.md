# ISSUE-02: Implementación de "Personalidad de Copiloto" en archivos YAML

**Estado:** Abierto
**Etiquetas:** `feature`, `cognitive-core`, `personality-matrix`

## Descripción
De momento, el archivo `profiles/paco_boxes.yaml` define la estructura de comportamiento léxico (The Pit Wall) enfocada puramente a ser un comentarista de carrera (Broadcast style). 
Sin embargo, el núcleo cognitivo (`gemini_engine.py`) es agnóstico y permite inyectar otro tipo de personalidades, como un "Copiloto" (Spotter style) que no comenta para un público, sino que le habla directamente al piloto dándole indicaciones y alertas críticas.

## Objetivo
Ampliar el *Personality Matrix* (YAML) para soportar múltiples arquitecturas de Prompt de Sistema (Pit Wall vs. Copiloto).

## Tareas a Ejecutar
1. **Crear `profiles/copilot.yaml`:** Redactar un nuevo manifiesto de personalidad para Gemini. Regla estricta: *frases cortas ("Clear left", "Push here", "Tires hot")*, omitiendo descripciones pintorescas.
2. **Refactorizar `gemini_engine.py`:** Leer dinámicamente el `yaml` a integrar en base a una variable de entorno `ACTIVE_PERSONA`.
3. **Ajuste del Topic Roulette:** Si el Copiloto está activo, el *Topic Roulette* debe deshabilitarse o limitarse a alertas críticas (tráfico/llantas) para no distraer al piloto.
