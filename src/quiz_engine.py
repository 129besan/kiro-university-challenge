"""
QuickQuiz Studio — Pure Business Logic Layer
=============================================
This module contains ONLY pure functions and data models.
It must never import streamlit or perform any I/O.

All validation, parsing, serialization, and scoring logic lives here.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ValidationError(Exception):
    """Raised when a Quiz fails schema validation.

    Attributes
    ----------
    quiz_id : int | str
        The ``id`` of the failing Quiz, or a positional index string
        (e.g. ``"pos=0"``) when ``id`` is absent or not an integer.
    field : str
        Name of the invalid field (e.g. ``"choices"``, ``"correct_index"``).
    reason : str
        Human-readable description of the violation.
    """

    def __init__(self, quiz_id: int | str, field: str, reason: str) -> None:
        self.quiz_id = quiz_id
        self.field = field
        self.reason = reason
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"Quiz id={self.quiz_id}: '{self.field}' {self.reason}"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class Quiz:
    """A single quiz question with 4 choices and a correct answer index."""

    id: int
    question: str
    choices: list[str]   # exactly 4 non-empty strings
    correct_index: int   # 0 <= correct_index <= 3
    explanation: str


@dataclass
class QuizSet:
    """A titled collection of Quiz objects."""

    title: str
    source_topic: str
    questions: list[Quiz]


@dataclass(frozen=True)
class Score:
    """Immutable scoring result."""

    correct_count: int
    total_questions: int
    percentage: float    # round(correct_count / total_questions * 100, 1); 0.0 when total == 0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_quiz(quiz: Quiz) -> None:
    """Validate a Quiz object against all schema rules.

    Raises
    ------
    ValidationError
        If any field violates its constraint.  The error message includes
        the quiz id (or positional placeholder), the field name, and the
        specific violation description.
    """
    qid: int | str = quiz.id  # id was already parsed as int by parse_quiz_set

    # question — non-empty string
    if not isinstance(quiz.question, str) or not quiz.question.strip():
        raise ValidationError(qid, "question", "must be a non-empty string")

    # choices — exactly 4 non-empty strings
    if not isinstance(quiz.choices, list) or len(quiz.choices) != 4:
        count = len(quiz.choices) if isinstance(quiz.choices, list) else "?"
        raise ValidationError(
            qid,
            "choices",
            f"must have exactly 4 non-empty strings, got {count}",
        )
    for i, choice in enumerate(quiz.choices):
        if not isinstance(choice, str) or not choice.strip():
            raise ValidationError(
                qid,
                "choices",
                f"element at index {i} must be a non-empty string",
            )

    # correct_index — integer in [0, 3]
    if not isinstance(quiz.correct_index, int) or not (0 <= quiz.correct_index <= 3):
        raise ValidationError(
            qid,
            "correct_index",
            f"must be in [0, 3], got {quiz.correct_index!r}",
        )

    # explanation — non-empty string
    if not isinstance(quiz.explanation, str) or not quiz.explanation.strip():
        raise ValidationError(qid, "explanation", "must be a non-empty string")


# ---------------------------------------------------------------------------
# Parse / Serialize
# ---------------------------------------------------------------------------


def parse_quiz_set(data: dict) -> QuizSet:
    """Deserialize a JSON-compatible dict into a QuizSet object.

    Each Quiz is validated via ``validate_quiz`` before being included.
    Any ValidationError is propagated to the caller (app.py catches it).

    Parameters
    ----------
    data : dict
        A dict with keys ``title``, ``source_topic``, and ``questions``
        (list of dicts matching the Quiz schema).

    Returns
    -------
    QuizSet

    Raises
    ------
    ValidationError
        If any Quiz fails validation.
    KeyError | TypeError
        If the top-level dict structure is malformed (propagated to caller).
    """
    title: str = data["title"]
    source_topic: str = data["source_topic"]
    raw_questions: list[dict] = data["questions"]

    questions: list[Quiz] = []
    for pos, raw in enumerate(raw_questions):
        # Resolve quiz_id for error messages before full parsing
        raw_id = raw.get("id")
        if not isinstance(raw_id, int):
            quiz_id_label: int | str = f"pos={pos}"
            raise ValidationError(quiz_id_label, "id", "is missing or not an integer")

        quiz = Quiz(
            id=raw_id,
            question=raw.get("question", ""),
            choices=raw.get("choices", []),
            correct_index=raw.get("correct_index", -1),
            explanation=raw.get("explanation", ""),
        )
        validate_quiz(quiz)
        questions.append(quiz)

    return QuizSet(title=title, source_topic=source_topic, questions=questions)


def serialize_quiz_set(quiz_set: QuizSet) -> dict:
    """Serialize a QuizSet object into a JSON-compatible dict.

    Each Quiz is validated before serialization.  Raises ValidationError
    for any invalid Quiz so that partial/corrupt dicts are never returned.

    Parameters
    ----------
    quiz_set : QuizSet

    Returns
    -------
    dict

    Raises
    ------
    ValidationError
        If any Quiz in the QuizSet fails validation.
    """
    for quiz in quiz_set.questions:
        validate_quiz(quiz)

    return {
        "title": quiz_set.title,
        "source_topic": quiz_set.source_topic,
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "choices": list(q.choices),
                "correct_index": q.correct_index,
                "explanation": q.explanation,
            }
            for q in quiz_set.questions
        ],
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def calculate_score(quizzes: list[Quiz], answers: dict[int, int]) -> Score:
    """Calculate the score for a completed quiz session.

    Parameters
    ----------
    quizzes : list[Quiz]
        The ordered list of Quiz objects from the QuizSet.
    answers : dict[int, int]
        Mapping of ``quiz.id`` → selected choice index (0-based).
        Questions absent from this dict are treated as unanswered (incorrect).

    Returns
    -------
    Score
        ``Score(0, 0, 0.0)`` when ``quizzes`` is empty.
    """
    total = len(quizzes)
    if total == 0:
        return Score(correct_count=0, total_questions=0, percentage=0.0)

    correct = sum(
        1
        for quiz in quizzes
        if answers.get(quiz.id) == quiz.correct_index
    )
    percentage = round(correct / total * 100, 1)
    return Score(correct_count=correct, total_questions=total, percentage=percentage)
