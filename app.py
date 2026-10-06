"""
app.py — QuickQuiz Studio Streamlit UI
=======================================
Responsibilities:
  - Page routing via st.session_state["page"]
  - File I/O (loading preset_quiz.json)
  - Rendering quiz form, results, and visual feedback
  - Error display for ValidationError / IOError

This module must NOT contain any business logic.
All scoring, parsing, and validation are delegated to src/quiz_engine.py.
"""

from __future__ import annotations

import json
import pathlib

import streamlit as st

from src.quiz_engine import (
    Quiz,
    QuizSet,
    Score,
    ValidationError,
    calculate_score,
    parse_quiz_set,
)
import importlib
import src.generator
import src.web_fetcher

importlib.reload(src.generator)
importlib.reload(src.web_fetcher)

from src.generator import generate_quiz_from_text
from src.web_fetcher import fetch_article_content

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRESET_PATH = pathlib.Path("sample_data/preset_quiz.json")

PAGE_SELECT = "select"
PAGE_QUIZ = "quiz"
PAGE_RESULTS = "results"


# ---------------------------------------------------------------------------
# Session-state helpers  (Steering Rule 4)
# ---------------------------------------------------------------------------


def get_session_key(quiz_id: int) -> str:
    """Return the st.session_state key for a given quiz id.

    Always use this helper — never hard-code key strings inline.
    """
    return f"answer_{quiz_id}"


def clear_quiz_answers(quiz_set: QuizSet) -> None:
    """Remove only the answer keys belonging to quiz_set from session_state.

    Does not touch any other session_state entries (Req 6.3).
    """
    for quiz in quiz_set.questions:
        st.session_state.pop(get_session_key(quiz.id), None)


def all_answered(quiz_set: QuizSet) -> bool:
    """Return True only when every question has a non-None answer."""
    return all(
        st.session_state.get(get_session_key(q.id)) is not None
        for q in quiz_set.questions
    )


def _init_page() -> None:
    """Initialise routing key on first render."""
    if "page" not in st.session_state:
        st.session_state["page"] = PAGE_SELECT


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_preset_quiz() -> QuizSet | None:
    """Read preset_quiz.json and parse it.

    Returns None and displays a st.error on any failure so the app never
    raises an unhandled exception (Req 1.3, 5.5).
    """
    try:
        raw = json.loads(PRESET_PATH.read_text(encoding="utf-8"))
        return parse_quiz_set(raw)
    except FileNotFoundError:
        st.error(
            f"Preset quiz file not found: `{PRESET_PATH}`\n\n"
            "Make sure `sample_data/preset_quiz.json` exists in the project root."
        )
    except PermissionError as exc:
        st.error(f"Cannot read `{PRESET_PATH}`: permission denied.\n\n{exc}")
    except OSError as exc:
        st.error(f"Failed to read `{PRESET_PATH}`: {exc}")
    except (KeyError, TypeError) as exc:
        st.error(
            f"Preset quiz file has an unexpected structure.\n\n"
            f"Detail: {exc}"
        )
    except ValidationError as exc:
        st.error(f"Preset quiz data is invalid.\n\n{exc}")
    return None


# ---------------------------------------------------------------------------
# View: Mode selection
# ---------------------------------------------------------------------------


def render_mode_selection() -> None:
    """Landing page — let the user choose a quiz mode."""
    # Sidebar configurations
    with st.sidebar:
        st.header("⚙️ Studio Settings")
        api_key = st.text_input(
            "OpenRouter API Key (Optional)",
            type="password",
            help="Optional: Enter an API key for high-end LLM generation. If omitted, built-in heuristic extractor will generate quizzes instantly for free.",
        )
        st.session_state["api_key"] = api_key

        model_input = st.text_input(
            "LLM Model (OpenRouter)",
            value="openrouter/free",
            help="Default: 'openrouter/free' automatically routes to the best available free model. You can also specify any custom model slug.",
        )
        st.session_state["model"] = model_input.strip() or "openrouter/free"

        st.divider()
        st.subheader("⚡ Kiro Capabilities")
        st.success("Power: `web-quiz-power` Active")
        st.info("MCP: `fetch` tool enabled")
        st.info("Agent: `@quiz-reviewer` ready")

    st.title("🎓 QuickQuiz Studio")
    st.markdown(
        "Transform technical articles into interactive 4-choice quizzes "
        "with instant grading and detailed explanations."
    )
    st.divider()

    tab_url, tab_preset, tab_text = st.tabs([
        "🌐 Fetch from Blog URL",
        "⚡ Instant Preset",
        "📝 Paste Article Text",
    ])

    with tab_url:
        st.subheader("Generate Quiz from Live Technical Blog")
        st.write("Enter a public article URL. The system will fetch the content and automatically build a 4-choice quiz.")

        # Preset suggestion buttons for 1-click video demo
        col_btn1, col_btn2 = st.columns(2)
        target_url = "https://aws.amazon.com/jp/blogs/news/kiro-university-challenge/"
        with col_btn1:
            if st.button("📌 Example: AWS Kiro Challenge Blog", use_container_width=True):
                st.session_state["input_url"] = target_url
        with col_btn2:
            if st.button("📌 Example: Python 3.14 Highlights", use_container_width=True):
                st.session_state["input_url"] = "https://docs.python.org/3/whatsnew/3.14.html"

        input_url = st.text_input(
            "Article or Blog URL",
            value=st.session_state.get("input_url", target_url),
            placeholder="https://example.com/blog/article",
        )

        if st.button("🚀 Generate Quiz from URL", type="primary", use_container_width=True):
            if not input_url.strip():
                st.error("Please enter a valid URL.")
            else:
                with st.spinner("Fetching article and synthesizing quiz..."):
                    try:
                        title, body = fetch_article_content(input_url.strip())
                        quiz_set = generate_quiz_from_text(
                            title=title,
                            text=body,
                            api_key=st.session_state.get("api_key"),
                            source_url=input_url.strip(),
                            model=st.session_state.get("model", "nvidia/llama-3.1-nemotron-70b-instruct:free"),
                        )
                        st.session_state["quiz_set"] = quiz_set
                        st.session_state["page"] = PAGE_QUIZ
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate quiz: {e}")

    with tab_preset:
        st.subheader("Offline Preset Mode")
        st.write("Loads the verified local preset (`sample_data/preset_quiz.json`) instantly without network requests.")
        if st.button("⚡ Load Preset Quiz", type="secondary", use_container_width=True):
            quiz_set = load_preset_quiz()
            if quiz_set is not None:
                st.session_state["quiz_set"] = quiz_set
                st.session_state["page"] = PAGE_QUIZ
                st.rerun()

    with tab_text:
        st.subheader("Paste Custom Documentation Text")
        custom_title = st.text_input("Article Title", value="My Technical Notes")
        custom_text = st.text_area(
            "Article Content",
            height=200,
            placeholder="Paste technical documentation or notes here...",
        )
        if st.button("Generate from Text", type="secondary", use_container_width=True):
            if len(custom_text.strip()) < 50:
                st.warning("Please provide at least 50 characters of technical text.")
            else:
                with st.spinner("Analyzing text and creating quiz..."):
                    quiz_set = generate_quiz_from_text(
                        title=custom_title,
                        text=custom_text,
                        api_key=st.session_state.get("api_key"),
                        model=st.session_state.get("model", "nvidia/llama-3.1-nemotron-70b-instruct:free"),
                    )
                    st.session_state["quiz_set"] = quiz_set
                    st.session_state["page"] = PAGE_QUIZ
                    st.rerun()


# ---------------------------------------------------------------------------
# View: Quiz form
# ---------------------------------------------------------------------------


def render_quiz_form(quiz_set: QuizSet) -> None:
    """Render each question as a radio-button form.

    - Maintains answer state in st.session_state across re-renders (Req 2.3, 6.2).
    - Submit button is disabled until all questions answered (Req 2.4).
    """
    st.title(f"📝 {quiz_set.title}")
    st.caption(f"Topic: {quiz_set.source_topic}")
    st.divider()

    total = len(quiz_set.questions)

    for idx, quiz in enumerate(quiz_set.questions, start=1):
        key = get_session_key(quiz.id)

        # Initialise key to avoid KeyError on first render (Steering Rule 4-2)
        if key not in st.session_state:
            st.session_state[key] = None

        # Validate choice count defensively — show error for malformed data (Req 2.5)
        if len(quiz.choices) != 4:
            st.error(
                f"Question {idx} has invalid data "
                f"({len(quiz.choices)} choices instead of 4). Skipping."
            )
            continue

        with st.container(border=True):
            st.markdown(f"**Question {idx} of {total}**")
            st.markdown(quiz.question)

            # Build option list with a sentinel "— select an answer —" at index 0
            options: list[str | None] = [None] + quiz.choices
            labels = ["— select an answer —"] + quiz.choices

            current_val = st.session_state[key]
            current_idx = (quiz.choices.index(current_val) + 1) if current_val in quiz.choices else 0

            selected_label = st.radio(
                label="Your answer",
                options=labels,
                index=current_idx,
                key=f"_radio_{quiz.id}",
                label_visibility="collapsed",
            )

            # Persist the raw choice text (or None) in session_state
            if selected_label == "— select an answer —":
                st.session_state[key] = None
            else:
                st.session_state[key] = selected_label

    st.divider()

    # Progress indicator
    answered_count = sum(
        1 for q in quiz_set.questions
        if st.session_state.get(get_session_key(q.id)) is not None
    )
    st.caption(f"Answered: {answered_count} / {total}")

    col_submit, col_cancel = st.columns([1, 4])
    with col_submit:
        submit_disabled = not all_answered(quiz_set)
        if st.button(
            "✅ Submit",
            disabled=submit_disabled,
            use_container_width=True,
            type="primary",
        ):
            # Build answers dict: quiz_id → selected index
            answers: dict[int, int] = {}
            for quiz in quiz_set.questions:
                selected_text = st.session_state.get(get_session_key(quiz.id))
                if selected_text is not None and selected_text in quiz.choices:
                    answers[quiz.id] = quiz.choices.index(selected_text)
                # absent keys → unanswered → treated as wrong in calculate_score

            score = calculate_score(quiz_set.questions, answers)
            st.session_state["score"] = score
            st.session_state["answers"] = answers
            st.session_state["page"] = PAGE_RESULTS
            st.rerun()

    if submit_disabled:
        st.caption("Answer all questions to enable Submit.")


# ---------------------------------------------------------------------------
# View: Results
# ---------------------------------------------------------------------------


def render_results(quiz_set: QuizSet, score: Score, answers: dict[int, int]) -> None:
    """Display score summary, visual feedback, and per-question explanation cards.

    - Balloons + success message when percentage >= 80 (Req 4.2).
    - Encouraging message below 80% (Req 4.3).
    - Educational cards with user answer vs correct answer (Req 4.4, 4.5, 4.6).
    """
    # --- Score summary (Req 4.1) ---
    st.title("🏆 Results")
    st.caption(f"{quiz_set.title}  ·  {quiz_set.source_topic}")
    st.divider()

    col_score, col_msg = st.columns([1, 2])
    with col_score:
        st.metric(
            label="Score",
            value=f"{score.correct_count} / {score.total_questions}",
            delta=f"{score.percentage}%",
        )

    with col_msg:
        if score.percentage >= 80:
            st.success(
                f"🎉 Excellent! You scored **{score.percentage}%** — "
                "great understanding of the material!"
            )
            st.balloons()
        else:
            st.info(
                f"📖 You scored **{score.percentage}%** "
                f"({score.correct_count}/{score.total_questions} correct). "
                "Review the explanations below to reinforce your learning."
            )

    st.divider()
    st.subheader("Explanations")

    # --- Educational cards (Req 4.4, 4.5, 4.6) ---
    for idx, quiz in enumerate(quiz_set.questions, start=1):
        user_choice_idx: int | None = answers.get(quiz.id)
        is_correct = user_choice_idx == quiz.correct_index

        if is_correct:
            verdict_icon = "✅"
            verdict_label = "Correct"
            card_border = True
        else:
            verdict_icon = "❌"
            verdict_label = "Incorrect"
            card_border = True

        with st.container(border=card_border):
            st.markdown(
                f"**Q{idx}.** {quiz.question}  &nbsp; {verdict_icon} **{verdict_label}**"
            )

            # User answer vs correct answer (Req 4.6)
            if user_choice_idx is not None:
                user_text = quiz.choices[user_choice_idx]
            else:
                user_text = "_No answer given_"

            correct_text = quiz.choices[quiz.correct_index]

            col_user, col_correct = st.columns(2)
            with col_user:
                if is_correct:
                    st.markdown(f"**Your answer:** {user_text}")
                else:
                    st.markdown(f"**Your answer:** ~~{user_text}~~")
            with col_correct:
                st.markdown(f"**Correct answer:** {correct_text}")

            # Explanation accordion (Req 4.4)
            with st.expander("📖 Explanation"):
                st.markdown(quiz.explanation)

    st.divider()

    # --- Navigation controls (Req 6.3) ---
    col_restart, col_home, _ = st.columns([1, 1, 3])
    with col_restart:
        if st.button("🔄 Restart Quiz", use_container_width=True):
            clear_quiz_answers(quiz_set)
            st.session_state["page"] = PAGE_QUIZ
            st.rerun()
    with col_home:
        if st.button("🏠 Choose Another Quiz", use_container_width=True):
            clear_quiz_answers(quiz_set)
            st.session_state.pop("quiz_set", None)
            st.session_state.pop("score", None)
            st.session_state.pop("answers", None)
            st.session_state["page"] = PAGE_SELECT
            st.rerun()


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Route to the correct view based on st.session_state["page"]."""
    st.set_page_config(
        page_title="QuickQuiz Studio",
        page_icon="🎓",
        layout="centered",
    )

    _init_page()

    page = st.session_state["page"]

    if page == PAGE_SELECT:
        render_mode_selection()

    elif page == PAGE_QUIZ:
        quiz_set: QuizSet | None = st.session_state.get("quiz_set")
        if quiz_set is None:
            st.error("No quiz loaded. Returning to selection.")
            st.session_state["page"] = PAGE_SELECT
            st.rerun()
        else:
            render_quiz_form(quiz_set)

    elif page == PAGE_RESULTS:
        quiz_set = st.session_state.get("quiz_set")
        score: Score | None = st.session_state.get("score")
        answers: dict[int, int] = st.session_state.get("answers", {})
        if quiz_set is None or score is None:
            st.error("Session data missing. Returning to selection.")
            st.session_state["page"] = PAGE_SELECT
            st.rerun()
        else:
            render_results(quiz_set, score, answers)

    else:
        st.session_state["page"] = PAGE_SELECT
        st.rerun()


if __name__ == "__main__":
    main()
