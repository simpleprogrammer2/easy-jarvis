# Easy Jarvis Project Instructions

This document defines the foundational mandates for development and maintenance of the `easy-jarvis` project.

## 🛠 Development Lifecycle
- **Test-First Mentality**: Every new feature or bug fix MUST be accompanied by corresponding tests in the `tests/` directory.
- **Continuous Validation**: Before any commit, run local linting (`ruff`) and tests (`pytest`) to ensure parity with the GitHub Actions CI environment.
- **Surgical Edits**: Maintain code quality by following existing patterns and avoiding unnecessary refactors in unrelated files.

## 🔒 Security & Privacy (MANDATORY)
- **Zero-Data Policy**: NEVER commit personal data, user-specific memories, or sensitive configurations. 
- **Secret Protection**: Keep `.env` files and API keys strictly ignored.
- **Scope**: Only commit technical modules, logic improvements, and reusable "skills". 
- **Git Hygiene**: Always check `git diff` before committing to ensure no private information has leaked into the codebase.

## 🏗 Infrastructure
- **System Dependencies**: Any change requiring new system-level libraries (e.g., audio drivers) must be reflected in both `Dockerfile` and `.github/workflows/main.yml`.
- **Mocking**: For modules that interact with hardware (Ear, Voice), ensure a robust "Mock" fallback exists for CI and remote execution environments.
