# Implementation Plan: QuickQuiz Studio MVP

## Overview

requirements.md と design.md に基づき、QuickQuiz Studio MVP を段階的に実装します。
コアロジック（`src/quiz_engine.py`）を先行して実装・テストし、その後 Streamlit UI（`app.py`）を組み上げることで、各ステップで動作確認可能な構成にします。
テスト関連サブタスクは optional（`*`）とし、スキップして MVP を素早く確認することもできます。

---

## Tasks

- [ ] 1. Steering 作成（Lesson 2）
  - [ ] 1.1 `.kiro/steering/coding-standards.md` を作成する
    - Python 3.10 以上、型アノテーション必須、`dataclass` 使用のルールを記述する
    - UI（`app.py`）とビジネスロジック（`src/quiz_engine.py`）の分離ルールを明文化する
    - `quiz_engine.py` での `streamlit` インポート禁止ルールを記述する
    - `st.session_state` キーは `get_session_key(quiz_id)` 経由で生成するルールを記述する
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 2. コアロジック実装（`src/quiz_engine.py`）と単体テスト
  - [ ] 2.1 `Quiz`・`QuizSet`・`Score` データクラスを `src/quiz_engine.py` に定義する
    - `Quiz`: `id: int`, `question: str`, `choices: list[str]`, `correct_index: int`, `explanation: str`
    - `QuizSet`: `title: str`, `source_topic: str`, `questions: list[Quiz]`
    - `Score`: `correct_count: int`, `total_questions: int`, `percentage: float`
    - _Requirements: 1.2, 2.1, 3.4_
  - [ ] 2.2 `ValidationError` 例外クラスを実装する
    - `__init__(self, quiz_id: int | str, field: str, reason: str)` シグネチャで実装する
    - `__str__` は `Quiz id={quiz_id}: '{field}' {reason}` 形式で返す
    - _Requirements: 5.4_
  - [ ] 2.3 `validate_quiz(quiz: Quiz) -> None` を実装する
    - `choices` の要素数が 4 以外、または空文字列を含む場合は `ValidationError` を送出する
    - `correct_index` が `[0, 3]` 範囲外の場合は `ValidationError` を送出する
    - `id`・`question`・`explanation` が非空でない場合は `ValidationError` を送出する
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [ ] 2.4 `parse_quiz_set(data: dict) -> QuizSet` を実装する
    - `dict` から `QuizSet` オブジェクトを生成し、各 `Quiz` に `validate_quiz` を呼び出す
    - `ValidationError` は呼び出し元へ伝播させる
    - _Requirements: 1.2, 7.1_
  - [ ] 2.5 `serialize_quiz_set(quiz_set: QuizSet) -> dict` を実装する
    - `QuizSet` を JSON 互換の `dict` に変換する
    - シリアライズ前に `validate_quiz` を呼び出し、無効データは `ValidationError` を送出する
    - _Requirements: 7.2, 7.4_
  - [ ] 2.6 `calculate_score(quizzes: list[Quiz], answers: dict[int, int]) -> Score` を実装する
    - `answers` に存在しない `quiz_id` は不正解として扱う
    - `quizzes` が空の場合は `Score(0, 0, 0.0)` を返す
    - `percentage` は `round(correct_count / total_questions * 100, 1)` で計算する
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [ ]* 2.7 `tests/test_quiz.py` に pytest 単体テストを実装する
    - `preset_quiz.json` の正常ロードと全フィールド検証
    - 選択肢が 3 個のデータで `ValidationError` が送出されることを確認する
    - `correct_index=4` で `ValidationError` が送出されることを確認する
    - `question` が空文字列で `ValidationError` が送出されることを確認する
    - 全問正解・全問不正解・未回答含む場合のスコア計算
    - 0 問 `QuizSet` のスコア計算 → `Score(0, 0, 0.0)` を確認する
    - _Requirements: 1.2, 3.1, 3.2, 3.5, 5.1, 5.2, 5.3, 5.4_

- [ ] 3. Checkpoint — コアロジックの動作確認
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Streamlit UI 実装（`app.py`）とプリセット動作確認
  - [ ] 4.1 `get_session_key`・`clear_quiz_answers`・`all_answered` ヘルパー関数を実装する
    - `get_session_key(quiz_id: int) -> str` は `"answer_{quiz_id}"` 形式でキーを返す
    - `clear_quiz_answers(quiz_set: QuizSet) -> None` は現在のクイズに属するキーのみ削除する
    - `all_answered(quiz_set: QuizSet) -> bool` は全問に回答があるかを判定する
    - _Requirements: 6.1, 6.2, 6.3_
  - [ ] 4.2 `load_preset_quiz() -> QuizSet | None` を実装する
    - `sample_data/preset_quiz.json` を読み込み、`parse_quiz_set` を呼び出す
    - `ValidationError`・`FileNotFoundError`・`OSError` をキャッチし、エラーメッセージを表示して `None` を返す
    - _Requirements: 1.1, 1.3, 5.5_
  - [ ] 4.3 `render_mode_selection()` を実装する
    - プリセットクイズ選択ボタンを描画する（MVP: プリセットのみ）
    - _Requirements: 1.1_
  - [ ] 4.4 `render_quiz_form(quiz_set: QuizSet) -> None` を実装する
    - 各 `Quiz` をラジオボタンフォームとして描画し、回答を `st.session_state` に保存する
    - クイズタイトルとソーストピックをページ上部に表示する
    - 全問回答済みの場合のみ Submit ボタンを有効化する
    - 再レンダリング時に `st.session_state` から前回の回答を復元する
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ] 4.5 `render_results(quiz_set: QuizSet, score: Score, answers: dict[int, int]) -> None` を実装する
    - スコアのサマリー（正解数・全問数・パーセンテージ）を表示する
    - `score.percentage >= 80` の場合は `st.balloons()` とおめでとうメッセージを表示する
    - `score.percentage < 80` の場合は励ましメッセージを表示する
    - 各問題の解説カードを表示し、正解・不正解をラベルで区別する
    - 各問題カードにユーザーの回答と正解の両方を表示する
    - "Restart Quiz" と "別のクイズを選ぶ" のコントロールを実装する
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - [ ] 4.6 `main()` エントリーポイントを実装してコンポーネントを結合する
    - `st.session_state` のページ状態に基づいてルーティングする（ModeSelection → Loading → QuizForm → Results）
    - _Requirements: 1.1, 2.3, 6.2_
  - [ ]* 4.7 `app.py` の Streamlit AppTest を `tests/test_quiz.py` に追加する
    - `ValidationError` 時の UI エラーメッセージ表示を確認する
    - スコア 80% 以上でおめでとうメッセージが表示されることを確認する
    - スコア 80% 未満で励ましメッセージが表示されることを確認する
    - _Requirements: 4.2, 4.3, 5.5_

- [ ] 5. Checkpoint — UI とプリセット動作の確認
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. pytest Hook 設定（Lesson 3）
  - [ ] 6.1 `.kiro/hooks/run-tests-on-save.json` を作成する
    - `PostFileSave` トリガーで `*.py` ファイル保存時に `pytest` を自動実行するフックを設定する
    - フック設定は `v1` 形式の JSON で記述する
    - _Requirements: （テスト自動化の開発品質要件）_

- [ ] 7. Hypothesis プロパティテスト実装と検証（Lesson 4）
  - [ ] 7.1 `tests/test_properties.py` を作成し、カスタムストラテジーを実装する
    - `valid_quiz_strategy()` を実装する（`id`・`question`・`choices`・`correct_index`・`explanation` を生成）
    - `valid_quiz_set_strategy()` を実装する（一意の `id` を持つ `QuizSet` を生成）
    - _Requirements: 7.3_
  - [ ]* 7.2 Property 1 のテスト `test_parse_serialize_roundtrip` を実装する
    - **Property 1: parse/serialize ラウンドトリップ同一性**
    - **Validates: Requirements 7.3, 7.1, 7.2**
    - `# Feature: quiz-studio, Property 1: parse/serialize ラウンドトリップ同一性` コメントを付与する
  - [ ]* 7.3 Property 2 のテスト `test_validate_choices_count` を実装する
    - **Property 2: choices 数バリデーション**
    - **Validates: Requirements 5.1, 5.3**
    - `# Feature: quiz-studio, Property 2: choices 数バリデーション` コメントを付与する
  - [ ]* 7.4 Property 3 のテスト `test_validate_correct_index_range` を実装する
    - **Property 3: correct_index 範囲バリデーション**
    - **Validates: Requirements 5.2**
    - `# Feature: quiz-studio, Property 3: correct_index 範囲バリデーション` コメントを付与する
  - [ ]* 7.5 Property 4 のテスト `test_validation_error_message_completeness` を実装する
    - **Property 4: ValidationError メッセージの完全性**
    - **Validates: Requirements 5.4**
    - `# Feature: quiz-studio, Property 4: ValidationError メッセージの完全性` コメントを付与する
  - [ ]* 7.6 Property 5 のテスト `test_calculate_score_correctness` を実装する
    - **Property 5: calculate_score の正確性（スコア計算不変条件）**
    - **Validates: Requirements 3.1, 3.2, 3.4**
    - `# Feature: quiz-studio, Property 5: calculate_score の正確性` コメントを付与する
  - [ ]* 7.7 Property 6 のテスト `test_score_independence` を実装する
    - **Property 6: スコア計算の独立性（メタモルフィックプロパティ）**
    - **Validates: Requirements 3.3**
    - `# Feature: quiz-studio, Property 6: スコア計算の独立性` コメントを付与する
  - [ ]* 7.8 Property 7 のテスト `test_session_key_uniqueness` を実装する
    - **Property 7: セッションキーの一意性**
    - **Validates: Requirements 6.1**
    - `# Feature: quiz-studio, Property 7: セッションキーの一意性` コメントを付与する
  - [ ]* 7.9 Property 8 のテスト `test_restart_clears_only_quiz_keys` を実装する
    - **Property 8: Restart Quiz のスコープ限定削除**
    - **Validates: Requirements 6.3**
    - `# Feature: quiz-studio, Property 8: Restart Quiz のスコープ限定削除` コメントを付与する
  - [ ]* 7.10 Property 9 のテスト `test_serialize_invalid_raises_validation_error` を実装する
    - **Property 9: serialize 時の無効データ拒否**
    - **Validates: Requirements 7.4**
    - `# Feature: quiz-studio, Property 9: serialize 時の無効データ拒否` コメントを付与する

- [ ] 8. Checkpoint — プロパティテストの確認
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Power/MCP 連携（Lesson 5 & 6）
  - [ ] 9.1 `.kiro/settings/mcp.json` に Web Fetch MCP の設定を追加する
    - MCP サーバー設定を JSON 形式で記述する
    - _Requirements: （将来の URL 取得拡張のための基盤）_

- [ ] 10. Custom Agent によるクイズ品質レビュー（Lesson 7）
  - [ ] 10.1 `.kiro/agents/quiz-reviewer.json` を作成する
    - クイズ品質・ハルシネーション検出レビューエージェントの設定を記述する
    - レビュー対象フィールド（`question`・`choices`・`explanation`）と評価基準を定義する
    - _Requirements: 1.2, 5.3_

---

## Notes

- タスク `*` 付きサブタスクは optional です。MVP を素早く確認したい場合はスキップできます
- 各タスクは requirements.md の特定の受入条件を参照しています（トレーサビリティ確保）
- チェックポイントタスクはインクリメンタルな動作確認のために設置しています
- プロパティテストは Hypothesis `@settings(max_examples=100)` で実行します
- タスク 1（Steering）はエージェントの動作指針を設定するため、コーディングタスクより先に実行することを推奨します

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3"] },
    { "id": 3, "tasks": ["2.4", "2.5", "2.6"] },
    { "id": 4, "tasks": ["2.7", "4.1"] },
    { "id": 5, "tasks": ["4.2", "4.3", "7.1"] },
    { "id": 6, "tasks": ["4.4", "4.5", "6.1"] },
    { "id": 7, "tasks": ["4.6", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8", "7.9", "7.10"] },
    { "id": 8, "tasks": ["4.7"] },
    { "id": 9, "tasks": ["9.1"] },
    { "id": 10, "tasks": ["10.1"] }
  ]
}
```
