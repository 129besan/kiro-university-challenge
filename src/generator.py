"""
src/generator.py — Quiz Generation Engine
==========================================
Generates 4-choice technical quizzes from article text.
Supports OpenRouter / LLM generation when an API key is provided,
and features a robust heuristic rule-based generator as an instant offline fallback.
"""

from __future__ import annotations

import json
import re
import requests

from src.quiz_engine import Quiz, QuizSet, validate_quiz, parse_quiz_set


def generate_quiz_from_text(
    title: str,
    text: str,
    api_key: str | None = None,
    source_url: str = "Web Article",
    model: str = "nvidia/llama-3.1-nemotron-70b-instruct:free",
) -> QuizSet:
    """Generate a QuizSet from article text.

    If api_key is provided, attempts LLM-based generation via OpenRouter using the selected model.
    Otherwise, uses an intelligent heuristic extractor to build a 3-question quiz.
    """
    if api_key and api_key.strip():
        try:
            return _generate_via_llm(title, text, api_key.strip(), source_url, model=model)
        except Exception as e:
            # Fallback to heuristic on LLM failure
            print(f"[Warning] LLM generation failed ({e}), falling back to heuristic engine.")
            pass

    return _generate_via_heuristic(title, text, source_url)


def _generate_via_llm(
    title: str,
    text: str,
    api_key: str,
    source_url: str,
    model: str = "nvidia/llama-3.1-nemotron-70b-instruct:free",
) -> QuizSet:
    """Call OpenRouter API to generate high-quality quiz JSON."""
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    truncated_text = text[:4000]  # keep prompt concise

    prompt = f"""You are an educational quiz creator. Based on the following technical article, generate exactly 3 multiple-choice questions.

Article Title: {title}
Article Text:
{truncated_text}

Output ONLY valid JSON matching this schema:
{{
  "title": "{title} Quiz",
  "source_topic": "{title}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "choices": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Detailed explanation of why this answer is correct."
    }}
  ]
}}
Rules:
- Exactly 4 choices per question.
- correct_index must be an integer between 0 and 3.
- Questions must be factual and directly test understanding of the article.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/129besan/kiro-university-challenge",
        "X-Title": "QuickQuiz Studio",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(endpoint, headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    res_data = resp.json()
    content = res_data["choices"][0]["message"]["content"]
    
    # Parse json block if markdown wrapped
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    data = json.loads(content)
    return parse_quiz_set(data)


def _generate_via_heuristic(title: str, text: str, source_url: str) -> QuizSet:
    """Intelligently extract key sentences and build a verified 3-question quiz."""
    # Split text into meaningful sentences
    raw_sentences = [
        s.strip()
        for s in re.split(r"[。\n\.\!\?]+", text)
        if len(s.strip()) > 30 and not s.strip().startswith("http")
    ]

    # Pick candidate sentences
    candidates = []
    for s in raw_sentences:
        # Prefer sentences with technical numbers, colons, or key terms
        if any(keyword in s for keyword in ["機能", "クレジット", "提出", "必須", "Kiro", "Python", "AWS", "最大", "サポート", "作成", "提供", "使", "利用"]):
            candidates.append(s)

    if len(candidates) < 3:
        candidates = raw_sentences[:3] if len(raw_sentences) >= 3 else [
            f"{title} provides technical features and architecture documentation.",
            f"The system is designed for interactive learning and hands-on validation.",
            f"Key guidelines emphasize clean separation and test-driven standards."
        ]

    # Limit to top 3
    selected = candidates[:3]
    questions: list[Quiz] = []

    for i, sentence in enumerate(selected, start=1):
        # Create an engaging question from the sentence
        if "クレジット" in sentence or "credit" in sentence.lower():
            q_text = f"【問題 {i}】この記事で言及されているクレジットや特典の条件として正しいものはどれですか？"
            correct_choice = f"{sentence[:70]}..."
            wrong_choices = [
                "すべての参加者に無条件で全額の現金が支給される",
                "有料プランへの課金のみが獲得の唯一の条件である",
                "事前の登録なしで自動的にポイントが付与される"
            ]
        elif "レッスン" in sentence or "lesson" in sentence.lower() or "提出" in sentence:
            q_text = f"【問題 {i}】この記事に記載された課題・要件についての正しい記述はどれですか？"
            correct_choice = f"{sentence[:70]}..."
            wrong_choices = [
                "静的なモックアップ画像のみの提出で合格となる",
                "SNSへの投稿や動画の提出は一切不要である",
                "過去に作成済みの既存プロジェクトをそのまま提出できる"
            ]
        else:
            q_text = f"【問題 {i}】記事「{title[:30]}...」の要点として最も適切なものはどれですか？"
            correct_choice = f"{sentence[:70]}..."
            wrong_choices = [
                "公式仕様とは無関係な第三者による非公式推測情報",
                "将来的に廃止される予定の非推奨な機能群",
                "特定の古いOS環境でのみ動作する実験的ツール"
            ]

        choices = [
            correct_choice,
            wrong_choices[0],
            wrong_choices[1],
            wrong_choices[2],
        ]
        # Place correct choice at index (i - 1) % 4 for variation
        target_idx = (i - 1) % 4
        if target_idx != 0:
            choices[0], choices[target_idx] = choices[target_idx], choices[0]

        quiz = Quiz(
            id=i,
            question=q_text,
            choices=choices,
            correct_index=target_idx,
            explanation=f"記事本文より: 「{sentence}」に基づいています。",
        )
        validate_quiz(quiz)
        questions.append(quiz)

    quiz_set = QuizSet(
        title=f"{title[:40]} クイズ",
        source_topic=title[:60],
        questions=questions,
    )
    return quiz_set
