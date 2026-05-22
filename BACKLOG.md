# 📋 Easy-Jarvis Backlog

This backlog is used by the **Night-Shift Autonomous Teammate** to prioritize overnight work.

## 🔴 Priority: High
- [ ] **Logging Refactor**: Move all `print()` statements in `src/` to a structured `logging` module.
- [ ] **Test Coverage**: Add unit tests for `src/voice.py` (using mocks for `edge-tts`).

## 🟡 Priority: Medium
- [ ] **Brain Memory**: Implement a simple JSON file to store long-term session context for the Brain.
- [ ] **Clap Sensitivity**: Add a dynamic threshold adjustment to `Ear` based on ambient noise.

## 🟢 Priority: Low
- [ ] **CLI Polish**: Add colorized output to the terminal using `rich` or `colorama`.
- [ ] **Documentation**: Create an `ARCHITECTURE.md` file explaining the module interactions.

## 🦾 Project J.A.R.V.I.S. (Just A Rather Very Intelligent System)

### Phase 1: The Vocal Interface
- [ ] **[Feature] Voice Synthesis:** Integrate a text-to-speech engine with a polite, sophisticated British accent (the Bettany Protocol).
- [ ] **[Feature] Wake Word Detection:** Configure offline wake-word activation (listening for "Jarvis" or "Sir").

### Phase 2: Diagnostics & HUD
- [ ] **[Feature] System Diagnostic Dashboard:** Build a terminal-based monitoring dashboard (CPU, RAM, Temperatures) styled like the Mark III armor HUD.
- [ ] **[Task] Sound Effects:** Add retro-futuristic audio cues on successful deployment or command failures.

### Phase 3: Personality & Wit
- [ ] **[Feature] Sarcasm Engine:** Program contextual roasts for when code compilation fails, balanced with encouraging pep-talks.
- [ ] **[Command] Clean Slate Protocol:** A custom command to safely purge all cache, build artifacts, and temporary files.

### Phase 4: House Party Automation
- [ ] **[Feature] Home Automation:** Connect local smart plugs/lights to trigger 'Work Mode' (bright lights) or 'Relax Mode' (dim lights).
