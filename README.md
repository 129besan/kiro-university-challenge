# QuickQuiz Studio 🎓

QuickQuiz Studio is an interactive AI study & quiz generator built with Streamlit. It transforms technical articles, documentation, or topic notes into engaging 4-choice interactive quizzes with instant grading, visual progress tracking, and detailed explanations.

Built with **Kiro** for the **Kiro University Challenge** (AWS).

---

## Features

- **Interactive Quiz Player**: Answer multiple-choice questions with dynamic radio selections, instant score cards, and congratulatory animations.
- **Instant Offline Preset Mode**: Zero-latency preset loading for smooth demonstration and offline testing without API overhead.
- **AI-Powered Generation (OpenRouter / Gemini compatible)**: Real-time generation from custom text or URLs via configurable API keys.
- **Educational Explanations**: Detailed reasoning for each answer to reinforce learning.
- **Robust & Type-Safe Core**: Business logic and grading completely separated from UI, verified by unit tests and property-based testing (Hypothesis).

---

## Quick Start

### 1. Setup Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

### 2. Run Application

```bash
python -m streamlit run app.py
```

### 3. Run Tests

```bash
# Unit & Property-based tests
python -m pytest
```

---

## Kiro University Challenge Implementation Status

This repository demonstrates the complete 7-lesson syllabus of the Kiro University Challenge:

| Lesson | Topic | Configuration / Artifact | Status |
| :--- | :--- | :--- | :---: |
| **Lesson 1** | **Spec-driven development** | `.kiro/specs/quiz-studio/` (`requirements.md`, `design.md`, `tasks.md` in EARS syntax) | Completed |
| **Lesson 2** | **Steering documents** | `.kiro/steering/coding-standards.md` (Type safety, state management, UI separation) | Completed |
| **Lesson 3** | **Hooks** | `.kiro/hooks/run-tests-on-save.json` (Automated pytest trigger on save) | Planned |
| **Lesson 4** | **Property-based testing** | `tests/test_properties.py` (Hypothesis invariant validation for score & schema) | Planned |
| **Lesson 5** | **Powers** | Kiro Power integration (Context & tool usage recorded in docs) | Planned |
| **Lesson 6** | **MCP** | `.kiro/settings/mcp.json` (Web Fetch MCP integration for article sourcing) | Planned |
| **Lesson 7** | **Custom agents** | `.kiro/agents/quiz-reviewer.json` (Automated quiz quality & hallucination reviewer) | Planned |

---

## Architecture

- `app.py`: Streamlit frontend UI, reactive session state, quiz navigation, and score presentation.
- `src/quiz_engine.py`: Pure, side-effect-free business logic for quiz parsing, score calculation, and schema validation.
- `sample_data/`: Verified sample articles and pre-built quiz presets for reliable demonstration.
- `tests/`: Pytest suite including example-based test cases and Hypothesis property invariants.
