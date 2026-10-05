# QuickQuiz Studio — Coding Standards

This steering document is **always included** in every Kiro session for this workspace.
All generated code must conform to the rules below.

---

## 1. Python Version & Type Safety

- Target **Python 3.10 or later**. Use modern syntax (`match`, `X | Y` union types, etc.) where appropriate.
- **All public functions and methods must have full type annotations** on every parameter and the return type.
- Use `from __future__ import annotations` only when needed for forward references; otherwise rely on built-in generics (`list[str]`, `dict[int, int]`, etc.).
- Use `@dataclass` (from `dataclasses`) for all data-carrier objects. Do **not** use plain dicts or tuples as substitutes for typed data models.
- Prefer `dataclass(frozen=True)` for value objects that should be immutable (`Score`).

```python
# ✅ correct
from dataclasses import dataclass

@dataclass(frozen=True)
class Score:
    correct_count: int
    total_questions: int
    percentage: float

# ❌ wrong — untyped dict as data model
score = {"correct": 2, "total": 3}
```

---

## 2. UI / Business-Logic Separation

### Rule 2-1 — `quiz_engine.py` must be a pure-function module

- `src/quiz_engine.py` **must never import `streamlit`** or any UI framework.
- Every function in `quiz_engine.py` must be a **pure function**: given the same inputs it always returns the same output, with no side effects (no file I/O, no network calls, no mutations of global state).
- File I/O (e.g. reading `preset_quiz.json`) is performed in `app.py`, which then passes the parsed `dict` to `quiz_engine.parse_quiz_set`.

```python
# ✅ correct — app.py handles I/O, engine handles logic
import json
from src.quiz_engine import parse_quiz_set

with open("sample_data/preset_quiz.json", encoding="utf-8") as f:
    data = json.load(f)
quiz_set = parse_quiz_set(data)   # pure function call

# ❌ wrong — engine reads file itself
def parse_quiz_set_from_file(path: str) -> QuizSet:
    with open(path) as f:         # side effect inside engine
        ...
```

### Rule 2-2 — `app.py` owns all Streamlit state

- All references to `st.session_state` live exclusively in `app.py`.
- Use the helper `get_session_key(quiz_id: int) -> str` (returns `"answer_{quiz_id}"`) to generate every session-state key. Never hard-code key strings inline.

---

## 3. Quiz Data Model & Validation Rules

### Canonical data model

```python
@dataclass
class Quiz:
    id: int
    question: str
    choices: list[str]   # exactly 4 non-empty strings
    correct_index: int   # 0 <= correct_index <= 3
    explanation: str

@dataclass
class QuizSet:
    title: str
    source_topic: str
    questions: list[Quiz]

@dataclass(frozen=True)
class Score:
    correct_count: int
    total_questions: int
    percentage: float    # round(correct_count / total_questions * 100, 1); 0.0 when total == 0
```

### Validation rules (enforced by `validate_quiz`)

| Field | Rule | Example violation message |
|---|---|---|
| `choices` | `len == 4` and every element is a non-empty `str` | `Quiz id=2: 'choices' must have exactly 4 non-empty strings, got 3` |
| `correct_index` | `0 <= correct_index <= 3` | `Quiz id=2: 'correct_index' must be in [0, 3], got 5` |
| `id` | present and is an `int` | `Quiz pos=0: 'id' is missing or not an integer` |
| `question` | non-empty `str` | `Quiz id=2: 'question' must be a non-empty string` |
| `explanation` | non-empty `str` | `Quiz id=2: 'explanation' must be a non-empty string` |

- `ValidationError` must carry `quiz_id` (or positional index as `str` when `id` is absent), `field`, and `reason`.
- `validate_quiz` is called from both `parse_quiz_set` and `serialize_quiz_set`.
- `ValidationError` is propagated to `app.py`, which catches it and displays the message — the engine never calls `st.error`.

---

## 4. Streamlit Session-State Conventions

### Rule 4-1 — Key generation

Always use the `get_session_key` helper. Never write `st.session_state["answer_1"]` inline.

```python
def get_session_key(quiz_id: int) -> str:
    return f"answer_{quiz_id}"
```

### Rule 4-2 — Re-render safety

Initialise every session-state key with a default before the first widget that reads it to avoid `KeyError` on re-render:

```python
key = get_session_key(quiz.id)
if key not in st.session_state:
    st.session_state[key] = None
```

### Rule 4-3 — Restart scope

`clear_quiz_answers(quiz_set)` must delete **only** the keys that belong to the current quiz. It must not touch unrelated `session_state` entries.

```python
def clear_quiz_answers(quiz_set: QuizSet) -> None:
    for quiz in quiz_set.questions:
        key = get_session_key(quiz.id)
        st.session_state.pop(key, None)
```

### Rule 4-4 — Page routing via session state

Use a single `st.session_state["page"]` key (values: `"select"`, `"quiz"`, `"results"`) to control which view is rendered. Never use `st.experimental_rerun` with side effects.

---

## 5. Testing Standards

- **Unit tests** live in `tests/test_quiz.py` and use `pytest`.
- **Property-based tests** live in `tests/test_properties.py` and use `hypothesis`.
- Every Hypothesis test must carry a reference comment:
  ```python
  # Feature: quiz-studio, Property N: <property name>
  ```
- Use `@settings(max_examples=100)` on every `@given` test.
- `src/quiz_engine.py` functions must be testable **without** a running Streamlit server.

---

## 6. File-Naming & Import Conventions

| File | Role |
|---|---|
| `app.py` | Streamlit entry point — UI only |
| `src/quiz_engine.py` | Pure business logic — no Streamlit |
| `tests/test_quiz.py` | Concrete example-based tests |
| `tests/test_properties.py` | Hypothesis property-based tests |
| `sample_data/preset_quiz.json` | Preset quiz fixture |

- Import `quiz_engine` as: `from src.quiz_engine import parse_quiz_set, ...`
- Do not use relative imports (`from .quiz_engine import ...`) from `app.py`.
