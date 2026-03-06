<div align="center">

# `[ ARCHITECTURE BLUEPRINT ]`
*— Autonomous Multi-Modal Cognitive Engine —*

> "Mapping the flow of kinetic data from optical perception to audio generation."

</div>

---

## 1. System Data Flow (The Nervous System)

This diagram illustrates the asynchronous, decoupled event-driven architecture that powers the AI commentator. The entire system is built around a central memory bus, allowing perception, cognition, and execution to operate independently at their maximum clock speeds.

```mermaid
graph TD
    %% Define Nodes
    Sim([Sim Racing Title])
    
    subgraph Perception Layer ["Optical Nerve & Telemetry"]
        CV[capture.py<br>Direct-to-RAM Vision]
        Tele[Telemetry Reader]
    end
    
    subgraph Event Router ["Memory Event Bus"]
        Bus[(AsyncIO Event Loop)]
    end
    
    subgraph Cognitive Core ["The Pit Wall Engine"]
        TR{Topic Roulette<br>Injector}
        PB[paco_boxes.yaml<br>Personality Matrix]
        Gemini[gemini_engine.py<br>Google Gemini 1.5]
    end
    
    subgraph Output Layer ["Vocal Tract"]
        Orch[orchestrator.py<br>Queue Manager]
        TTS[piper_tts.py / macos_tts.py<br>Zero-Latency Synthesis]
    end
    
    %% Define Edges & Flow
    Sim -- Live Screen --> CV
    Sim -- Raw Data --> Tele
    
    CV -- Base64 Frame Array --> Bus
    Tele -- JSON State --> Bus
    
    Bus -- Context Stream --> Gemini
    TR -- "Focus on Tires/Traffic" --> Gemini
    PB -- "Constraint: No repetition" --> Gemini
    
    Gemini -- Async Chunked Text --> Orch
    Orch -- Audio Payload --> TTS
    TTS -- Real-Time Commentary --> Speaker((Speaker / Stream))

    %% Styling
    classDef default fill:#000,stroke:#555,stroke-width:1px,color:#fff;
    classDef bus fill:#111,stroke:#0A66C2,stroke-width:2px,color:#fff;
    classDef core fill:#111,stroke:#BB86FC,stroke-width:2px,color:#fff;
    
    class Bus bus;
    class Gemini,TR,PB core;
```

---

## 2. Advanced Subsystems

### 2.1 The "Topic Roulette" (Anti-Fatigue Architecture)
A fundamental flaw in traditional AI commentary is **cognitive loop fatigue**: LLMs default to safely describing the most obvious visual element repeatedly (e.g., "He is turning left"). 

To eliminate this friction, Vael designed the **Topic Roulette**.
*   **Mechanism:** An asynchronous loop that injects a highly specific, randomized systemic prompt into the LLM's context window every few seconds automatically (e.g., `FORCED_FOCUS: Analyze Tire Thermals only`, `FORCED_FOCUS: Critique Race Craft`).
*   **Result:** The AI is forced to shift its analytical lens dynamically, creating a multi-dimensional, human-like narration without relying on hardcoded pre-recorded lines.

### 2.2 Direct-to-RAM Optical Perception
*   **Problem:** Writing screenshots to disk (`.png`, `.jpg`) creates catastrophic I/O bottlenecks in a sub-second loop.
*   **Vael Solution:** `capture.py` grabs the memory buffer of the selected monitor, uses `PIL` to construct an image array natively in RAM, compresses it, and encodes it directly to Base64 in a single volatile pass. Disk I/O equates to exactly 0 bytes per frame.
