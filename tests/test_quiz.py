"""
tests/test_quiz.py — Concrete example-based unit tests for quiz_engine.py
==========================================================================
Covers:
  - Parsing sample_data/preset_quiz.json (happy path)
  - ValidationError on malformed quiz data
  - Score calculation: all correct, all wrong, unanswered questions
"""

from __future__ import annotations

import json
import pathlib
import pytest

from src.quiz_engine import (
    Quiz,
    QuizSet,
    Score,
    ValidationError,
    calculate_score,
    parse_quiz_set,
    serialize_quiz_set,
    validate_quiz,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PRESET_PATH = pathlib.Path("sample_data/preset_quiz.json")


@pytest.fixture
def preset_data() -> dict:
    """Load preset_quiz.json as a raw dict."""
    return json.loads(PRESET_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def preset_quiz_set(preset_data: dict) -> QuizSet:
    """Parsed QuizSet from preset_quiz.json."""
    return parse_quiz_set(preset_data)


def _minimal_valid_quiz(
    *,
    qid: int = 1,
    question: str = "What is 1 + 1?",
    choices: list[str] | None = None,
    correct_index: int = 0,
    explanation: str = "Because math.",
) -> Quiz:
    """Helper: build a valid Quiz with overridable fields."""
    return Quiz(
        id=qid,
        question=question,
        choices=choices if choices is not None else ["2", "3", "4", "5"],
        correct_index=correct_index,
        explanation=explanation,
    )


# ---------------------------------------------------------------------------
# Requirement 1 — parse preset_quiz.json (happy path)
# ---------------------------------------------------------------------------


class TestParsePresetQuizJson:
    """Req 1.2 — parse_quiz_set deserializes preset_quiz.json correctly."""

    def test_title_and_source_topic(self, preset_quiz_set: QuizSet) -> None:
        assert preset_quiz_set.title == "Python 3.14 Key Features Quiz"
        assert preset_quiz_set.source_topic == "Python 3.14 Highlights"

    def test_question_count(self, preset_quiz_set: QuizSet) -> None:
        assert len(preset_quiz_set.questions) == 3

    def test_all_ids_are_ints(self, preset_quiz_set: QuizSet) -> None:
        for quiz in preset_quiz_set.questions:
            assert isinstance(quiz.id, int)

    def test_all_questions_have_exactly_4_choices(self, preset_quiz_set: QuizSet) -> None:
        for quiz in preset_quiz_set.questions:
            assert len(quiz.choices) == 4, f"Quiz id={quiz.id} has {len(quiz.choices)} choices"

    def test_all_correct_indices_in_range(self, preset_quiz_set: QuizSet) -> None:
        for quiz in preset_quiz_set.questions:
            assert 0 <= quiz.correct_index <= 3, f"Quiz id={quiz.id} correct_index out of range"

    def test_no_empty_fields(self, preset_quiz_set: QuizSet) -> None:
        for quiz in preset_quiz_set.questions:
            assert quiz.question.strip()
            assert quiz.explanation.strip()
            for choice in quiz.choices:
                assert choice.strip()

    def test_first_question_correct_index(self, preset_quiz_set: QuizSet) -> None:
        # preset_quiz.json Q1 correct_index == 0
        assert preset_quiz_set.questions[0].correct_index == 0

    def test_second_question_correct_index(self, preset_quiz_set: QuizSet) -> None:
        # preset_quiz.json Q2 correct_index == 1
        assert preset_quiz_set.questions[1].correct_index == 1

    def test_third_question_correct_index(self, preset_quiz_set: QuizSet) -> None:
        # preset_quiz.json Q3 correct_index == 2
        assert preset_quiz_set.questions[2].correct_index == 2


# ---------------------------------------------------------------------------
# Requirement 5 — ValidationError on invalid quiz data
# ---------------------------------------------------------------------------


class TestValidationErrorChoices:
    """Req 5.1 — choices must have exactly 4 non-empty strings."""

    def test_three_choices_raises(self) -> None:
        quiz = _minimal_valid_quiz(choices=["a", "b", "c"])
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        err = exc_info.value
        assert err.field == "choices"
        assert "3" in str(err)

    def test_five_choices_raises(self) -> None:
        quiz = _minimal_valid_quiz(choices=["a", "b", "c", "d", "e"])
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        err = exc_info.value
        assert err.field == "choices"
        assert "5" in str(err)

    def test_empty_choice_string_raises(self) -> None:
        quiz = _minimal_valid_quiz(choices=["a", "", "c", "d"])
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert exc_info.value.field == "choices"

    def test_whitespace_only_choice_raises(self) -> None:
        quiz = _minimal_valid_quiz(choices=["a", "   ", "c", "d"])
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert exc_info.value.field == "choices"

    def test_exactly_4_valid_choices_passes(self) -> None:
        quiz = _minimal_valid_quiz(choices=["a", "b", "c", "d"])
        validate_quiz(quiz)  # must not raise


class TestValidationErrorCorrectIndex:
    """Req 5.2 — correct_index must be 0 <= value <= 3."""

    @pytest.mark.parametrize("bad_index", [-1, 4, 5, 100, -99])
    def test_out_of_range_raises(self, bad_index: int) -> None:
        quiz = _minimal_valid_quiz(correct_index=bad_index)
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        err = exc_info.value
        assert err.field == "correct_index"
        assert str(bad_index) in str(err)

    @pytest.mark.parametrize("good_index", [0, 1, 2, 3])
    def test_valid_indices_pass(self, good_index: int) -> None:
        quiz = _minimal_valid_quiz(correct_index=good_index)
        validate_quiz(quiz)  # must not raise


class TestValidationErrorEmptyFields:
    """Req 5.3 — id, question, explanation must be present and non-empty."""

    def test_empty_question_raises(self) -> None:
        quiz = _minimal_valid_quiz(question="")
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert exc_info.value.field == "question"

    def test_whitespace_question_raises(self) -> None:
        quiz = _minimal_valid_quiz(question="   ")
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert exc_info.value.field == "question"

    def test_empty_explanation_raises(self) -> None:
        quiz = _minimal_valid_quiz(explanation="")
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert exc_info.value.field == "explanation"

    def test_whitespace_explanation_raises(self) -> None:
        quiz = _minimal_valid_quiz(explanation="  ")
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert exc_info.value.field == "explanation"


class TestValidationErrorMessage:
    """Req 5.4 — ValidationError message must include quiz_id, field, and reason."""

    def test_error_message_contains_quiz_id(self) -> None:
        quiz = _minimal_valid_quiz(qid=42, correct_index=9)
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert "42" in str(exc_info.value)

    def test_error_message_contains_field_name(self) -> None:
        quiz = _minimal_valid_quiz(choices=["x", "y"])
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        assert "choices" in str(exc_info.value)

    def test_error_message_contains_reason(self) -> None:
        quiz = _minimal_valid_quiz(correct_index=99)
        with pytest.raises(ValidationError) as exc_info:
            validate_quiz(quiz)
        # reason should include the bad value
        assert "99" in str(exc_info.value)

    def test_missing_id_uses_positional_index(self) -> None:
        """Req 5.4 — when id field is absent, positional index is used."""
        bad_data = {
            "title": "T",
            "source_topic": "S",
            "questions": [
                {
                    # 'id' intentionally omitted
                    "question": "Q?",
                    "choices": ["a", "b", "c", "d"],
                    "correct_index": 0,
                    "explanation": "E",
                }
            ],
        }
        with pytest.raises(ValidationError) as exc_info:
            parse_quiz_set(bad_data)
        assert "pos=0" in str(exc_info.value)


class TestValidationErrorPropagation:
    """Req 5.5 — ValidationError raised in parse_quiz_set propagates to caller."""

    def test_invalid_data_raises_from_parse(self) -> None:
        bad_data = {
            "title": "T",
            "source_topic": "S",
            "questions": [
                {
                    "id": 1,
                    "question": "Q?",
                    "choices": ["only", "three", "choices"],  # invalid
                    "correct_index": 0,
                    "explanation": "E",
                }
            ],
        }
        with pytest.raises(ValidationError):
            parse_quiz_set(bad_data)


# ---------------------------------------------------------------------------
# Requirement 7 — serialize round-trip
# ---------------------------------------------------------------------------


class TestSerializeRoundTrip:
    """Req 7.3 — parse(serialize(q)) == q for preset quiz."""

    def test_round_trip_preset(self, preset_quiz_set: QuizSet) -> None:
        serialized = serialize_quiz_set(preset_quiz_set)
        restored = parse_quiz_set(serialized)
        assert restored.title == preset_quiz_set.title
        assert restored.source_topic == preset_quiz_set.source_topic
        assert len(restored.questions) == len(preset_quiz_set.questions)
        for orig, rest in zip(preset_quiz_set.questions, restored.questions):
            assert orig.id == rest.id
            assert orig.question == rest.question
            assert orig.choices == rest.choices
            assert orig.correct_index == rest.correct_index
            assert orig.explanation == rest.explanation

    def test_serialize_invalid_raises(self) -> None:
        """Req 7.4 — serialize invalid QuizSet raises ValidationError."""
        bad_quiz_set = QuizSet(
            title="T",
            source_topic="S",
            questions=[
                Quiz(
                    id=1,
                    question="Q?",
                    choices=["a", "b"],  # only 2 choices — invalid
                    correct_index=0,
                    explanation="E",
                )
            ],
        )
        with pytest.raises(ValidationError):
            serialize_quiz_set(bad_quiz_set)


# ---------------------------------------------------------------------------
# Requirement 3 — Score calculation
# ---------------------------------------------------------------------------


class TestCalculateScore:
    """Req 3.x — calculate_score accuracy."""

    @pytest.fixture
    def three_quizzes(self) -> list[Quiz]:
        return [
            _minimal_valid_quiz(qid=1, correct_index=0),
            _minimal_valid_quiz(qid=2, correct_index=1),
            _minimal_valid_quiz(qid=3, correct_index=2),
        ]

    def test_all_correct(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.1, 3.2 — perfect score."""
        answers = {1: 0, 2: 1, 3: 2}
        score = calculate_score(three_quizzes, answers)
        assert score.correct_count == 3
        assert score.total_questions == 3
        assert score.percentage == 100.0

    def test_all_wrong(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.1, 3.2 — zero score."""
        answers = {1: 3, 2: 3, 3: 3}
        score = calculate_score(three_quizzes, answers)
        assert score.correct_count == 0
        assert score.total_questions == 3
        assert score.percentage == 0.0

    def test_partial_correct(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.2 — percentage rounded to 1 decimal place."""
        answers = {1: 0, 2: 3, 3: 3}  # only Q1 correct → 1/3
        score = calculate_score(three_quizzes, answers)
        assert score.correct_count == 1
        assert score.total_questions == 3
        assert score.percentage == 33.3  # round(1/3 * 100, 1)

    def test_unanswered_counted_as_wrong(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.1 — missing key in answers dict counts as incorrect."""
        answers: dict[int, int] = {}  # all unanswered
        score = calculate_score(three_quizzes, answers)
        assert score.correct_count == 0
        assert score.total_questions == 3

    def test_partial_unanswered(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.1 — mix of answered and unanswered."""
        answers = {1: 0}  # Q1 correct, Q2 and Q3 unanswered
        score = calculate_score(three_quizzes, answers)
        assert score.correct_count == 1
        assert score.total_questions == 3

    def test_empty_quiz_set(self) -> None:
        """Req 3.5 — empty quiz list returns Score(0, 0, 0.0)."""
        score = calculate_score([], {})
        assert score == Score(correct_count=0, total_questions=0, percentage=0.0)

    def test_score_independence(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.3 — changing one answer changes correct_count by exactly 1."""
        answers_before = {1: 0, 2: 1, 3: 3}  # Q1, Q2 correct
        answers_after = {1: 0, 2: 3, 3: 3}   # Q1 correct, Q2 now wrong
        score_before = calculate_score(three_quizzes, answers_before)
        score_after = calculate_score(three_quizzes, answers_after)
        assert abs(score_before.correct_count - score_after.correct_count) == 1

    def test_score_returns_score_dataclass(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.4 — calculate_score returns a Score object."""
        result = calculate_score(three_quizzes, {1: 0, 2: 1, 3: 2})
        assert isinstance(result, Score)

    def test_percentage_two_out_of_three(self, three_quizzes: list[Quiz]) -> None:
        """Req 3.2 — 2/3 ≈ 66.7%."""
        answers = {1: 0, 2: 1, 3: 3}  # Q3 wrong
        score = calculate_score(three_quizzes, answers)
        assert score.correct_count == 2
        assert score.percentage == 66.7
