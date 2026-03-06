# 🛡️ Protocolo Anti-Alucinación de Telemetría

## El Problema: "Desalineación de Telemetría"

El LLM tiene conocimiento generalizado de Sim Racing. Si no se le ancla, su instinto narrativo lo lleva a comentar lo que **"sabe"** que suele pasar (e.g., desgaste de neumáticos), en lugar de lo que **"ve"** en el frame actual.

**Caso documentado:** Paco comentó *"las gomas ya no tienen la misma adherencia"* en la **vuelta 2**, sin ninguna evidencia visual en el HUD. Esto es una alucinación crítica. Un ingeniero de pista que se queja de las gomas en la vuelta 2 está pidiendo a gritos que lo despidan.

---

## Solución: Protocolo Anti-Alucinación en Dos Capas

### Capa 1: `strict_constraints` en el Perfil YAML
El archivo `profiles/paco_boxes.yaml` ahora acepta un bloque `strict_constraints`. Cada ítem es una restricción absoluta que se inyecta directamente en el System Prompt del LLM, antes de cualquier comentario.

```yaml
strict_constraints:
  - "NEVER assume tire wear UNLESS HUD shows YELLOW or RED."
  - "Dense traffic = early race. DO NOT mention tire fatigue."
  - "Never invent car damage without visual evidence."
```

**Regla de oro:** Si una restricción no está documentada en el YAML, el LLM puede ignorarla. El YAML es el contrato.

---

### Capa 2: Directiva Visual Hardcoded (Anti-Alucinación Absoluta)
En `brain/llm/gemini_engine.py`, el método `_build_system_prompt()` inyecta este bloque como parte infrangible de cada petición:

```
PROTOCOLO ANTI-ALUCINACIÓN (No negociable):
- Tu ÚNICO source of truth son los FRAMES visuales recibidos.
- HUD neumáticos VERDE = bien. No los menciones como problema.
- HUD neumáticos AMARILLO/ROJO = puedes comentarlo.
- Si NO VES el widget de neumáticos: NO HABLES de neumáticos.
- Coches agrupados = inicio de carrera. Comportate como tal.
```

Este bloque no puede ser sobrescrito por el perfil ni por el Topic Roulette.

---

## Hoja de Ruta: La Bala de Plata (Vision SDK)
El protocolo actual es preventivo (restricciones verbales al LLM). La solución definitiva es **determinista**: que OpenCV recorte el HUD del juego pixel a pixel y le pase el estado real como dato estructurado.

```
HUD Pixel Analysis:
  pixel_color → green  = tire_status: "optimal"
  pixel_color → yellow = tire_status: "warning" → fire Event
  pixel_color → red    = tire_status: "critical" → fire high-priority Event
```

El LLM no tendría opción de adivinar: recibiría el estado como JSON. Esto forma parte del roadmap de `vael-vision-sdk`.
