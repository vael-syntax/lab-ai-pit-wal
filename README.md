<div align="center">

# `[ lab-ai-pit-wall ]`
*— Autonomous Sim Racing Commentator Engine —*

> "Real-time telemetry meets asynchronous AI."

</div>

---

### [ Module Overview ]

This repository contains the core logic for an **Autonomous AI Commentator** (The Pit Wall) designed to analyze real-time context from Sim Racing telemetry and generate dynamic, non-repetitive narration using LLMs (Google Gemini) and local/cloud TTS (Piper TTS/macOS).

Instead of relying on sterile, pre-programmed responses, this module uses a dynamic *Topic Roulette* architecture to inject varied perspectives (Track condition, Traffic, Tire thermals, Race craft) into the AI's prompt stream asynchronously.

### ⚙️ Core Architecture

*   `brain/llm/gemini_engine.py`: The nerve center. Manages prompt generation, contextual awareness, and the *Topic Roulette* system to ensure the AI doesn't fall into repetitive loops.
*   `profiles/paco_boxes.yaml`: The personality matrix. Defines the structural rules, constraints, and dynamic tags that guide the AI's commentary style without forcing hardcoded phrases.
*   `integrations/voice/`: The vocal cords. Integrations with lightweight TTS models (Piper ONNX) and fallback OS-level synthesis (macOS `say`) for zero-latency audio delivery.
*   `core/orchestrator.py`: The event loop. Synchronizes telemetry ingestion with the LLM generation and TTS playback queues.

---

### 🧬 Vael Taxonomic Origin: `Lab`
This is a **Sandbox/Lab** project. It represents extreme experimentation with asynchronous LLM control and real-time audio synthesis. Expect friction, rapid iteration, and raw code.

*Code is kinetic. Friction is the enemy.*
