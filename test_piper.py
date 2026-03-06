import os
import sounddevice as sd
from piper import PiperVoice

model_path = os.path.join(os.getcwd(), "models", "voice", "es_model.onnx")
config_path = os.path.join(os.getcwd(), "models", "voice", "es_model.onnx.json")

voice = PiperVoice.load(model_path, config_path)
text = "Probando la voz uno dos tres"
print(f"Sample Rate: {voice.config.sample_rate}")

audio_stream = voice.synthesize(text)
with sd.RawOutputStream(samplerate=voice.config.sample_rate, channels=1, dtype='int16') as stream:
    for chunk in audio_stream:
        stream.write(chunk.audio_int16_bytes)
print("¡Hablando completado!")
