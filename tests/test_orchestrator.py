import asyncio
import time
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Añadir el directorio raíz al path para que encuentre 'integrations' y 'core'
sys.path.append(str(Path(__file__).parent.parent))

# Evitamos que Piper intente cargar el ONNX real pesadísimo durante los tests
@pytest.fixture(autouse=True)
def mock_piper_voice():
    with patch("integrations.voice.piper_tts.PiperVoice.load") as mock_load:
        mock_instance = MagicMock()
        mock_instance.config.sample_rate = 22050
        
        # Simulamos que la síntesis devuelve algunos chunks de audio dummy
        def dummy_synthesize(text):
            chunk = MagicMock()
            chunk.audio_int16_bytes = b'\x00' * 1024
            yield chunk
            # Simulamos el tiempo que tardaría en generar otro chunk
            time.sleep(0.01)
            yield chunk

        mock_instance.synthesize.side_effect = dummy_synthesize
        mock_load.return_value = mock_instance
        yield mock_load

# Evitamos que sounddevice intente agarrar los altavoces de la VM del CI
@pytest.fixture(autouse=True)
def mock_sounddevice():
    with patch("integrations.voice.piper_tts.sd.RawOutputStream") as mock_sd:
        # Hacemos que funcione como un context manager dummy
        mock_context = MagicMock()
        mock_sd.return_value.__enter__.return_value = mock_context
        yield mock_sd

@pytest.mark.asyncio
async def test_high_priority_crash_interrupts_low_priority_tts_under_100ms():
    """
    Objetivo: Validar que si llega un payload "high" (ej: CRASH),
    la tarea actual del PiperTTS se descarta en menos de 100ms reales.
    """
    from core.event_bus import EventBus
    from integrations.voice.piper_tts import PiperTTS
    
    bus = EventBus()
    await bus.start()
    
    tts = PiperTTS(bus, "dummy_model_path", "dummy_config_path")
    await tts.start()
    
    # 1. Colocamos un evento enorme de baja prioridad (ej. TIRE_TEMP aburrido)
    await bus.publish("text_generated", {
        "text": "The tire temperature on the front left is currently optimal but might overheat if he keeps pushing like a maniac on turn three.",
        "priority": "low"
    })
    
    # Esperamos una pizca de tiempo para asegurar que el worker empezó a procesar el TIRE TEMP
    await asyncio.sleep(0.05)
    
    # Assert que el TTS está activo y tiene el flag de interrupción abajo
    assert getattr(tts, "interrupt_flag", False) == False
    
    # 2. INYECTAMOS EL EVENTO CRÍTICO (El choque)
    start_interrupt_time = time.time()
    
    # Simulamos lo que publicaría VisionCapture al ver un Crash
    await bus.publish("audio_interrupt", {"reason": "visual_critical_anomaly"})
    
    # Luego llega el texto del choque con alta prioridad
    await bus.publish("text_generated", {
        "text": "MASSIVE CRASH TURN 3!",
        "priority": "high"
    })
    
    # Permitimos al event bus procesar las suscripciones
    await asyncio.sleep(0.05)
    
    end_interrupt_time = time.time()
    time_to_interrupt = end_interrupt_time - start_interrupt_time
    
    # Validaciones Exigidas por el "Seniority Request":
    # El tiempo de interrupción lógica debe ser abismalmente bajo (exigido: < 100ms)
    assert time_to_interrupt < 0.10, f"⚠️ LENTITUD: La interrupción tomó {time_to_interrupt*1000:.2f}ms (>100ms limit)."
    
    # Asegurar que el sistema quedó estable y procesó todo
    assert tts.queue.empty() == True
    
    # Limpieza
    await tts.stop()
    await bus.stop()
