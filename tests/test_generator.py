"""
tests/test_generator.py — Unit tests for web_fetcher and generator modules
"""

import pytest
from src.generator import generate_quiz_from_text
from src.quiz_engine import QuizSet, validate_quiz


def test_heuristic_generator_creates_valid_quiz():
    title = "AWS Serverless Architecture Highlights"
    sample_text = (
        "AWS Lambda enables running code without provisioning servers. "
        "The system scales automatically in response to incoming events. "
        "Billing is strictly based on request count and execution duration. "
        "Participants can earn up to 5250 credits by completing all required challenge lessons."
    )
    quiz_set = generate_quiz_from_text(title, sample_text)

    assert isinstance(quiz_set, QuizSet)
    assert len(quiz_set.questions) == 3
    for q in quiz_set.questions:
        assert len(q.choices) == 4
        assert 0 <= q.correct_index <= 3
        assert q.explanation != ""
        # Validate that each generated quiz passes standard schema validation
        validate_quiz(q)
