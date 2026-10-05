"""
tests/test_properties.py — Hypothesis property-based tests for quiz_engine.py
==============================================================================
Each test is annotated with the property number it verifies, matching the
"Correctness Properties" section of .kiro/specs/quiz-studio/design.md.

Reference format:
    # Feature: quiz-studio, Property N: <property name>

Run with:
    python -m pytest tests/test_properties.py -v
"""

from __future__ import annotations

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

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
# Custom Strategies (tasks.md 7.1)
# ---------------------------------------------------------------------------

# A strategy that generates a single non-empty, non-whitespace-only string
_nonempty_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=200,
).filter(lambda s: s.strip())


def valid_quiz_strategy(quiz_id: int | None = None) -> st.SearchStrategy[Quiz]:
    """Generate a valid Quiz with all constraints satisfied.

    Parameters
    ----------
    quiz_id : int | None
        When provided the quiz id is fixed; otherwise drawn from integers.
    """
    id_strategy = st.just(quiz_id) if quiz_id is not None else st.integers(min_value=1, max_value=10_000)
    return st.builds(
        Quiz,
        id=id_strategy,
        question=_nonempty_text,
        choices=st.lists(_nonempty_text, min_size=4, max_size=4),
        correct_index=st.integers(min_value=0, max_value=3),
        explanation=_nonempty_text,
    )


def valid_quiz_set_strategy() -> st.SearchStrategy[QuizSet]:
    """Generate a valid QuizSet with unique quiz ids.

    Uses a flat_map to first draw the number of questions, assign unique ids
    1..n, then build each Quiz with that fixed id.
    """
    def build_quiz_set(n: int) -> st.SearchStrategy[QuizSet]:
        ids = list(range(1, n + 1))
        quiz_strategies = [valid_quiz_strategy(quiz_id=qid) for qid in ids]
        return st.tuples(
            _nonempty_text,  # title
            _nonempty_text,  # source_topic
            st.tuples(*quiz_strategies).map(list),
        ).map(lambda t: QuizSet(title=t[0], source_topic=t[1], questions=t[2]))

    return st.integers(min_value=1, max_value=10).flatmap(build_quiz_set)


# ---------------------------------------------------------------------------
# Property 1: parse / serialize round-trip identity (tasks.md 7.2)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 1: parse/serialize ラウンドトリップ同一性


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_parse_serialize_roundtrip(quiz_set: QuizSet) -> None:
    """For every valid QuizSet q: parse_quiz_set(serialize_quiz_set(q)) == q.

    Validates: Requirements 7.1, 7.2, 7.3
    """
    serialized = serialize_quiz_set(quiz_set)
    restored = parse_quiz_set(serialized)

    assert restored.title == quiz_set.title
    assert restored.source_topic == quiz_set.source_topic
    assert len(restored.questions) == len(quiz_set.questions)

    for orig, rest in zip(quiz_set.questions, restored.questions):
        assert rest.id == orig.id
        assert rest.question == orig.question
        assert rest.choices == orig.choices
        assert rest.correct_index == orig.correct_index
        assert rest.explanation == orig.explanation


# ---------------------------------------------------------------------------
# Property 2: choices count validation (tasks.md 7.3)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 2: choices 数バリデーション


@given(
    base_quiz=valid_quiz_strategy(),
    bad_choices=st.lists(
        _nonempty_text,
        min_size=0,
        max_size=10,
    ).filter(lambda c: len(c) != 4),
)
@settings(max_examples=100)
def test_validate_choices_count_wrong_size(base_quiz: Quiz, bad_choices: list[str]) -> None:
    """When choices has != 4 items, validate_quiz must raise ValidationError.

    Validates: Requirements 5.1
    """
    bad_quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=bad_choices,
        correct_index=base_quiz.correct_index,
        explanation=base_quiz.explanation,
    )
    with pytest.raises(ValidationError) as exc_info:
        validate_quiz(bad_quiz)
    assert exc_info.value.field == "choices"


@given(
    base_quiz=valid_quiz_strategy(),
    empty_idx=st.integers(min_value=0, max_value=3),
    empty_val=st.just("") | st.text(
        alphabet=st.characters(whitelist_categories=("Zs",)),
        min_size=1,
        max_size=5,
    ),
)
@settings(max_examples=100)
def test_validate_choices_empty_element(
    base_quiz: Quiz,
    empty_idx: int,
    empty_val: str,
) -> None:
    """When any choice is empty or whitespace-only, validate_quiz must raise.

    Validates: Requirements 5.3
    """
    bad_choices = list(base_quiz.choices)
    bad_choices[empty_idx] = empty_val
    bad_quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=bad_choices,
        correct_index=base_quiz.correct_index,
        explanation=base_quiz.explanation,
    )
    with pytest.raises(ValidationError) as exc_info:
        validate_quiz(bad_quiz)
    assert exc_info.value.field == "choices"


# ---------------------------------------------------------------------------
# Property 3: correct_index range validation (tasks.md 7.4)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 3: correct_index 範囲バリデーション


@given(
    base_quiz=valid_quiz_strategy(),
    bad_index=st.integers().filter(lambda x: not (0 <= x <= 3)),
)
@settings(max_examples=100)
def test_validate_correct_index_out_of_range(base_quiz: Quiz, bad_index: int) -> None:
    """When correct_index is outside [0, 3], validate_quiz must raise ValidationError.

    Validates: Requirements 5.2
    """
    bad_quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=base_quiz.choices,
        correct_index=bad_index,
        explanation=base_quiz.explanation,
    )
    with pytest.raises(ValidationError) as exc_info:
        validate_quiz(bad_quiz)
    assert exc_info.value.field == "correct_index"
    # The bad value should appear somewhere in the error message
    assert str(bad_index) in str(exc_info.value)


@given(
    base_quiz=valid_quiz_strategy(),
    good_index=st.integers(min_value=0, max_value=3),
)
@settings(max_examples=100)
def test_validate_correct_index_valid_range_passes(base_quiz: Quiz, good_index: int) -> None:
    """When correct_index is in [0, 3], validate_quiz must not raise for that field.

    Validates: Requirements 5.2
    """
    quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=base_quiz.choices,
        correct_index=good_index,
        explanation=base_quiz.explanation,
    )
    # Should not raise ValidationError for correct_index
    # (may still raise for other fields if base_quiz had issues — but valid_quiz_strategy guarantees it won't)
    validate_quiz(quiz)  # must not raise


# ---------------------------------------------------------------------------
# Property 4: ValidationError message completeness (tasks.md 7.5)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 4: ValidationError メッセージの完全性


@given(
    base_quiz=valid_quiz_strategy(),
    bad_index=st.integers().filter(lambda x: not (0 <= x <= 3)),
)
@settings(max_examples=100)
def test_validation_error_message_contains_quiz_id(base_quiz: Quiz, bad_index: int) -> None:
    """ValidationError message must include the quiz id.

    Validates: Requirements 5.4
    """
    bad_quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=base_quiz.choices,
        correct_index=bad_index,
        explanation=base_quiz.explanation,
    )
    with pytest.raises(ValidationError) as exc_info:
        validate_quiz(bad_quiz)
    err = exc_info.value
    msg = str(err)
    # quiz_id must appear
    assert str(err.quiz_id) in msg
    # field name must appear
    assert err.field in msg
    # reason must be non-empty and in message
    assert err.reason
    assert err.reason in msg


@given(
    bad_choices=st.lists(
        _nonempty_text,
        min_size=0,
        max_size=10,
    ).filter(lambda c: len(c) != 4),
    quiz_id=st.integers(min_value=1, max_value=9999),
)
@settings(max_examples=100)
def test_validation_error_message_choices_field_name(
    bad_choices: list[str],
    quiz_id: int,
) -> None:
    """ValidationError for choices violation must name the 'choices' field.

    Validates: Requirements 5.4
    """
    bad_quiz = Quiz(
        id=quiz_id,
        question="Q?",
        choices=bad_choices,
        correct_index=0,
        explanation="E.",
    )
    with pytest.raises(ValidationError) as exc_info:
        validate_quiz(bad_quiz)
    err = exc_info.value
    assert "choices" in str(err)
    assert str(quiz_id) in str(err)


# ---------------------------------------------------------------------------
# Property 5: calculate_score correctness invariants (tasks.md 7.6)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 5: calculate_score の正確性（スコア計算不変条件）


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_calculate_score_invariants_all_correct(quiz_set: QuizSet) -> None:
    """When all answers match correct_index, score == total and percentage == 100.0.

    Validates: Requirements 3.1, 3.2, 3.4
    """
    answers = {q.id: q.correct_index for q in quiz_set.questions}
    score = calculate_score(quiz_set.questions, answers)

    assert isinstance(score, Score)
    assert score.total_questions == len(quiz_set.questions)
    assert score.correct_count == score.total_questions
    assert score.percentage == 100.0


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_calculate_score_invariants_all_wrong(quiz_set: QuizSet) -> None:
    """When no answer matches, correct_count == 0 and percentage == 0.0.

    Validates: Requirements 3.1, 3.2
    """
    # Pick an answer that is always wrong: (correct_index + 1) % 4
    answers = {q.id: (q.correct_index + 1) % 4 for q in quiz_set.questions}
    score = calculate_score(quiz_set.questions, answers)

    assert score.total_questions == len(quiz_set.questions)
    assert score.correct_count == 0
    assert score.percentage == 0.0


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_calculate_score_bounds(quiz_set: QuizSet) -> None:
    """0 <= correct_count <= total and 0.0 <= percentage <= 100.0 always hold.

    Validates: Requirements 3.1, 3.2, 3.4
    """
    # Mix: answer every other question correctly
    answers = {
        q.id: q.correct_index if i % 2 == 0 else (q.correct_index + 1) % 4
        for i, q in enumerate(quiz_set.questions)
    }
    score = calculate_score(quiz_set.questions, answers)

    assert 0 <= score.correct_count <= score.total_questions
    assert 0.0 <= score.percentage <= 100.0


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_calculate_score_percentage_formula(quiz_set: QuizSet) -> None:
    """percentage == round(correct_count / total * 100, 1) for any non-empty input.

    Validates: Requirements 3.2
    """
    answers = {q.id: q.correct_index for q in quiz_set.questions[:len(quiz_set.questions) // 2]}
    score = calculate_score(quiz_set.questions, answers)

    expected_pct = round(score.correct_count / score.total_questions * 100, 1)
    assert score.percentage == expected_pct


# ---------------------------------------------------------------------------
# Property 6: score calculation independence (tasks.md 7.7)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 6: スコア計算の独立性（メタモルフィックプロパティ）


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_score_independence_flip_one_answer(quiz_set: QuizSet) -> None:
    """Flipping exactly one answer between correct and wrong changes correct_count by ±1.

    Validates: Requirements 3.3
    """
    assume(len(quiz_set.questions) >= 2)

    quizzes = quiz_set.questions
    # Start with all correct
    answers_before: dict[int, int] = {q.id: q.correct_index for q in quizzes}
    # Flip the first question to wrong
    first = quizzes[0]
    answers_after = dict(answers_before)
    answers_after[first.id] = (first.correct_index + 1) % 4

    score_before = calculate_score(quizzes, answers_before)
    score_after = calculate_score(quizzes, answers_after)

    # Exactly one question changed
    assert abs(score_before.correct_count - score_after.correct_count) == 1
    # Total must not change
    assert score_before.total_questions == score_after.total_questions


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_score_independence_other_questions_unaffected(quiz_set: QuizSet) -> None:
    """Changing one question's answer does not affect others' individual correctness.

    Validates: Requirements 3.3
    """
    assume(len(quiz_set.questions) >= 2)

    quizzes = quiz_set.questions
    # All correct except first (wrong)
    answers_v1: dict[int, int] = {q.id: q.correct_index for q in quizzes}
    answers_v1[quizzes[0].id] = (quizzes[0].correct_index + 1) % 4

    # All correct except second (wrong)
    answers_v2: dict[int, int] = {q.id: q.correct_index for q in quizzes}
    answers_v2[quizzes[1].id] = (quizzes[1].correct_index + 1) % 4

    score_v1 = calculate_score(quizzes, answers_v1)
    score_v2 = calculate_score(quizzes, answers_v2)

    # Both have exactly (n-1) correct since only one wrong each
    assert score_v1.correct_count == len(quizzes) - 1
    assert score_v2.correct_count == len(quizzes) - 1


# ---------------------------------------------------------------------------
# Property 7: session key uniqueness (tasks.md 7.8)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 7: セッションキーの一意性


def _get_session_key(quiz_id: int) -> str:
    """Local copy of get_session_key logic — avoids importing streamlit in tests.

    Must stay in sync with app.py:get_session_key.
    """
    return f"answer_{quiz_id}"


@given(quiz_set=valid_quiz_set_strategy())
@settings(max_examples=100)
def test_session_key_uniqueness(quiz_set: QuizSet) -> None:
    """For a QuizSet with unique ids, generated session keys must all be distinct.

    Validates: Requirements 6.1
    """
    keys = [_get_session_key(q.id) for q in quiz_set.questions]
    assert len(keys) == len(set(keys)), (
        f"Duplicate session keys found: {keys}"
    )


@given(
    ids=st.lists(
        st.integers(min_value=1, max_value=100_000),
        min_size=1,
        max_size=50,
        unique=True,
    )
)
@settings(max_examples=100)
def test_session_key_format(ids: list[int]) -> None:
    """Each key follows the 'answer_{id}' format and uniquely identifies the quiz.

    Validates: Requirements 6.1
    """
    keys = [_get_session_key(qid) for qid in ids]
    for qid, key in zip(ids, keys):
        assert key == f"answer_{qid}"
    # All keys are distinct when ids are distinct
    assert len(set(keys)) == len(ids)


# ---------------------------------------------------------------------------
# Property 9: serialize rejects invalid QuizSet (tasks.md 7.10)
# ---------------------------------------------------------------------------

# Feature: quiz-studio, Property 9: serialize 時の無効データ拒否


@given(
    base_quiz=valid_quiz_strategy(),
    bad_index=st.integers().filter(lambda x: not (0 <= x <= 3)),
)
@settings(max_examples=100)
def test_serialize_invalid_correct_index_raises(base_quiz: Quiz, bad_index: int) -> None:
    """serialize_quiz_set with an invalid Quiz raises ValidationError, returns no partial dict.

    Validates: Requirements 7.4
    """
    bad_quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=base_quiz.choices,
        correct_index=bad_index,
        explanation=base_quiz.explanation,
    )
    bad_quiz_set = QuizSet(title="T", source_topic="S", questions=[bad_quiz])

    with pytest.raises(ValidationError):
        serialize_quiz_set(bad_quiz_set)


@given(
    base_quiz=valid_quiz_strategy(),
    bad_choices=st.lists(_nonempty_text, min_size=0, max_size=10).filter(
        lambda c: len(c) != 4
    ),
)
@settings(max_examples=100)
def test_serialize_invalid_choices_raises(
    base_quiz: Quiz, bad_choices: list[str]
) -> None:
    """serialize_quiz_set with wrong choices count raises ValidationError.

    Validates: Requirements 7.4
    """
    bad_quiz = Quiz(
        id=base_quiz.id,
        question=base_quiz.question,
        choices=bad_choices,
        correct_index=base_quiz.correct_index,
        explanation=base_quiz.explanation,
    )
    bad_quiz_set = QuizSet(title="T", source_topic="S", questions=[bad_quiz])

    with pytest.raises(ValidationError):
        serialize_quiz_set(bad_quiz_set)
