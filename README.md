<div align="center">

# `[ lab-ai-pit-wall ]`
*— Autonomous Multi-Modal Sim Racing Commentator Engine —*

> "Real-time perception meets asynchronous cognitive audio generation. Zero friction."

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

#### 2. Cognitive Core (LLM & Logic)
*   **`brain/llm/gemini_engine.py`**: The cognitive engine. It ingests the multi-modal streams (vision + context) and processes them through Google Gemini. The engine features our proprietary **Topic Roulette**—a dynamic prompt injector that asynchronously forces the AI to focus on varying race aspects (traffic, tire thermals, race craft) to guarantee unscripted variance.
*   **`profiles/paco_boxes.yaml`**: The personality matrix. Instead of hardcoded phrases, this defines structural flow rules and constraints, allowing the engine to generate organic, constraint-bound commentary.

#### 3. Output Layer (Zero-Latency Audio)
*   **`integrations/voice/`**: The local vocal tract. The system bypasses slow cloud-TTS by integrating directly with a local ONNX instance of Piper TTS (`piper_tts.py`), falling back natively to macOS OS-level synthesis (`macos_tts.py`) when immediate friction reduction is required.

#### 4. Orchestrator
*   **`core/orchestrator.py`**: The asynchronous event loop that synchronizes the optical nerve, the cognitive core, and the output layer.

---

### 🧬 Vael Taxonomic Origin: `Lab`
This project sits firmly in the **Sandbox/Lab** zone. It represents aggressive experimentation with continuous visual tracking, local inference loops, and sub-second multi-thread synchronization.

**Stack:** `Python` | `asyncio` | `mss` | `OpenCV/PIL` | `Google Gemini API` | `Piper TTS (ONNX)`

---
<div align="center">
  <i>"Let the algorithms narrate the speed."</i>
</div>
