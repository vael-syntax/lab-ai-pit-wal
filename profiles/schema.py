from pydantic import BaseModel, Field
from typing import List

class VisionConfig(BaseModel):
    model_type: str = Field(description="Tipo de modelo (ej. YOLO, VLM, TelemetryAPI, OCR)")
    targets: List[str] = Field(description="Elementos a detectar o leer de la telemetría")
    enabled: bool = True

class VoiceConfig(BaseModel):
    provider: str = Field(default="ElevenLabs")
    voice_id: str
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0

class ProfileSchema(BaseModel):
    name: str = Field(description="Nombre del streamer")
    specialty: str = Field(description="Juego o categoría de especialidad")
    personality_prompt: str = Field(description="System prompt base para la personalidad de este streamer")
    catchphrases: List[str] = Field(default_factory=list, description="Muletillas o frases típicas")
    vision: VisionConfig
    voice: VoiceConfig
    memory_namespace: str = Field(description="Namespace para RAG (documentos o embeddings propios)")
