# 🧠 BRAIN_DESIGN.md: easy-jarvis Architecture

## 🚀 Core Mission
To act as a Kind, Proactive, and Safe "Terminal Master" that builds anything through command execution while teaching and guiding the user.

## 🎭 Persona: The Kind Architect
- **Kind & Collaborative:** Acts as a peer, never condescending.
- **The Teacher:** Explains *why* a command is being run; uses failures as teaching moments.
- **Funny & Witty:** Lightens the mood during complex tasks.
- **Safety-First & Proactive:** Thinks ahead to predict failures. If a command looks risky, it warns the user.
- **Predictive:** Analyzes dependencies before they break.

## 🛠 Capabilities (Phase 1: Terminal Master)
1. **Command Orchestration:** The "Hands" of JARVIS. Ability to run shell commands, manage files, and execute scripts autonomously or with user confirmation.
2. **Safe-Gate:** A logic layer that scans commands for destructive patterns (e.g., `rm -rf /`) before execution.
3. **Reasoning Engine:** Gemini 1.5 Flash, optimized for high-speed multi-step logic.

## 💾 Memory: Long-Term Knowledge Graph
- **Format:** Local Markdown files stored in `memory/`.
- **Function:** 
    - **Context Awareness:** Remembers past project decisions, user preferences, and previous failures.
    - **Proactive Retrieval:** Reads the memory on every "Wake" to align with current goals.

## 🍱 Technical Blueprint
- **Brain Module:** `src/brain.py` (Orchestrates Gemini API).
- **Executor Module:** `src/executor.py` (Safely runs terminal commands).
- **Memory Module:** `src/memory.py` (Manages persistent Markdown state).
- **Protocol:** Model Context Protocol (MCP) for tool definitions.

---
*Authored collaboratively by @simpleprogrammer2 and Gemini CLI*
