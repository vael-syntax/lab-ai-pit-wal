<div align="center">

# `[ lab-ai-pit-wall ]`
*— Autonomous Multi-Modal Sim Racing Commentator Engine —*

> "Real-time perception meets asynchronous cognitive audio generation. Zero friction."

[![▶ Watch the system in action](https://img.shields.io/badge/▶%20DEMO%20EN%20VIVO-Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1eAwEMtHuCkDBIkmTNpT6SGBZ7qi_ewsa/view?usp=sharing)

</div>

---

### [ System Blueprint ]

This is not a text wrapper. This is **The Pit Wall**: an autonomous, multi-modal cognitive engine designed to ingest raw telemetry and visual data from a live Sim Racing environment, and output dynamic, human-like commentary with near-zero latency.

Built as a highly decoupled event-driven architecture, this system eliminates the static, repetitive loops of traditional AI bots by unifying **Computer Vision**, **Asynchronous LLM Orchestration**, and **Hardware-Native TTS**.

---

### ⚙️ Core Architecture & Subsystems

The repository is structured around independent nervous systems communicating via an internal asynchronous event bus.

#### 1. Perception Layer (Vision & Telemetry)
*   **`perception/vision/capture.py`**: The optical nerve. A direct-to-RAM screen capture module (via `mss` and `PIL`) that continuously grabs live frames from the simulation, resizes them, and encodes them directly to base64 streams without ever touching the disk. It publishes visual context arrays down the pipeline.

#### 2. The Cognitive Core (The Pit Wall)
*   **`brain/llm/gemini_engine.py`**: A specialized, low-latency Google Gemini integration.
*   **`Topic Roulette`**: Injects randomized, systemic constraints every few seconds to prevent LLM fatigue.
*   **`profiles/`**: The personality matrix. YAML files that structurally define rules, limits, and jargon for the agent.

#### 3. Output Layer (Zero-Latency Audio & APIs)
*   **`integrations/voice/`**: The local vocal tract. The system bypasses slow cloud-TTS by integrating directly with a local ONNX instance of Piper TTS (`piper_tts.py`), falling back natively to macOS OS-level synthesis (`macos_tts.py`) when immediate friction reduction is required.
*   **`docs/api/EVENT_PRIORITY.md`**: Definición oficial de la **API de Prioridades** para inyección de eventos (`high` / `low`) y control asíncrono sobre el modelo TTS.

---

### ⚠️ Known Limitations & Bottlenecks (The Reality Check)
A Virtual Architect does not sell smoke. This system has known technical constraints that are actively being mitigated:
1. **TTS Blocking:** While the architecture is decoupled, local TTS execution (`sd.RawOutputStream`) can block the audio thread. Eventual collision handles exist (interrupt flags), but rapid consecutive high-priority events can still cause micro-stutters.
2. **CPU Spikes on Base64:** Capturing `1280x720` frames and encoding them in base64 within RAM (zero-disk I/O) saves latency but induces momentary CPU spikes on Apple Silicon. Benchmarking shows degradation if the interval drops below `0.5s` (2 FPS).
3. **LLM Cognitive Latency:** Generating dynamic tokens with `Gemini 1.5 Pro` takes between `2.5s` to `4.0s` depending on Google's endpoint traffic. This means commentary is inherently "reactive" to the past 3 seconds, not predictive.

---

### 🧬 Vael Taxonomic Origin: `Lab`
This project sits firmly in the **Sandbox/Lab** zone. It represents aggressive experimentation with continuous visual tracking, local inference loops, and sub-second multi-thread synchronization.

**Stack:** `Python` | `asyncio` | `mss` | `OpenCV/PIL` | `Google Gemini API` | `Piper TTS (ONNX)`

---
<div align="center">
  <i>"Let the algorithms narrate the speed."</i>
</div>
