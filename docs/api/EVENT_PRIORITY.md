# 📡 System Priority API (Event Bus)

La arquitectura de `lab-ai-pit-wal` es asíncrona y está dirigida por eventos (`Interrupt-Driven`). Dado que la IA se conecta a múltiples capas de percepción (Visión, Telemetría, Chat), es imperativo que el sistema de salida (Vocal Tract) y el Orquestador sepan qué información tiene precedencia.

Para evitar colisiones de buffer en el audio y garantizar una latencia virtual cero en sistemas críticos, todas las inyecciones de texto y comandos deben adherirse a esta API de Prioridades.

## El Payload Estándar
Cuando cualquier módulo (ej. `capture.py`, `telemetry.py`) o el Cerebro (`gemini_engine.py`) publican un evento destinado a la cola de audio (`text_generated`), el diccionario **siempre** debe incluir el _flag_ `priority`.

```json
{
  "text": "Comentario o alerta para ser sintetizada",
  "priority": "low | high"
}
```

---

## 🚦 Niveles de Prioridad

### 1. Nivel `low` (Contextual y Descriptivo)
**Uso previsto:** Comentarios generales de la carrera, lectura de temperaturas estables, análisis de tiempos de vuelta rutinarios, monólogos del "Topic Roulette".

*   **Comportamiento del Event Bus:** Estos mensajes se encolan secuencialmente en un hilo asíncrono (`asyncio.Queue()`).
*   **Gestión del TTS:** El motor `PiperTTS` bloqueará el hilo de salida de sonido de forma natural hasta que termine de recitar la frase completa.  Si llega otro mensaje `low` mientras este se reproduce, esperará pacientemente en la cola.

**Ejemplo de Inyección:**
```python
await bus.publish("text_generated", {
    "text": "The tire temperature on the front left is optimal.",
    "priority": "low"
})
```

---

### 2. Nivel `high` (Crítico y Emergente)
**Uso previsto:** Eventos repentinos que exigen atención inmediata. **Crash/Choque**, **Bandera Roja**, **Penalizaciones Críticas**, o desconexión inminente.

*   **Comportamiento del Event Bus:** Al identificar esta anomalía, el sensor de percepción **siempre** debe aislar la alerta emitiendo **dos** eventos simultáneos de manera atómica:
    1.  El comando de interrupción mecánica: `audio_interrupt`.
    2.  El mensaje de voz con el flag visual de `priority: high`.

*   **Gestión del TTS (< 100ms Action):**
    1.  Al recibir `audio_interrupt`, el motor rompe de inmediato el loop del buffer en la RAM (`sd.RawOutputStream`), silenciando la frase aburrida que se esté diciendo.
    2.  El motor drena/purga todo lo que haya en la cola (removiendo cualquier otro evento `low` estancado).
    3.  Acepta e inyecta inmediatamente el nuevo mensaje `high`.

**Ejemplo de Inyección (El Estándar Vael):**
```python
# 1. Detonar el Kill Switch
await bus.publish("audio_interrupt", {"reason": "visual_critical_anomaly"})

# 2. Inyectar la alerta de latencia extrema
await bus.publish("text_generated", {
    "text": "CRASH ON TURN 3! YELLOW FLAG!",
    "priority": "high"
})
```

---

## 🛠️ Reglas de Arquitectura
1. **Zero Abuse:** Jamás usar `high` priority para comentarios normales o forzar a la IA a hablar más rápido. Hacerlo causará una denegación de servicio (DoS) en el motor TTS, provocando tartamudeo auditivo (`audio stutter`).
2. **Atomicidad:** Nunca asumas que `audio_interrupt` pasará el texto por sí solo. Es un _hardware switch_, el texto debe ir separado en `text_generated`.
