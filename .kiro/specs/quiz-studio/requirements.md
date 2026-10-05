# Requirements Document

## Introduction

QuickQuiz Studio は、技術ドキュメントや記事から4択のインタラクティブ学習クイズを生成し、ブラウザ上で学習・即時採点・解説確認ができる Streamlit Web アプリケーションです。

MVP の範囲は次の2つのモードに限定します。

1. **プリセットモード**: `sample_data/preset_quiz.json` をオフラインで即時ロードし、ネットワーク遅延なしにデモおよびオフラインテストを可能にします。
2. **クイズ受答モード**: ロードされたクイズを画面に描画し、ユーザーが回答を入力・送信して即時採点・解説確認ができます。

UI と採点ロジックは完全に分離し、将来的な LLM API 生成機能の追加を容易にする設計を採用します。

---

## Glossary

- **System**: QuickQuiz Studio アプリケーション全体（`app.py` + `src/quiz_engine.py` の組み合わせ）
- **Quiz_Engine**: `src/quiz_engine.py` に実装する副作用のない純粋関数群。クイズ JSON のパース・バリデーション・採点計算を担当する。
- **UI**: `app.py` に実装する Streamlit フロントエンド。セッション状態管理・フォーム描画・採点演出を担当する。
- **Quiz**: `id`・`question`・`choices`・`correct_index`・`explanation` の5フィールドを持つ単一の問題オブジェクト。
- **Quiz_Set**: タイトル・ソーストピック・`Quiz` の配列を持つクイズ全体のオブジェクト。
- **Preset_Quiz**: `sample_data/preset_quiz.json` に格納された既製の `Quiz_Set`。
- **Score**: ユーザーの正解数と全問題数の組、および正解率パーセンテージの組み合わせ。
- **Session_State**: Streamlit の `st.session_state` を利用して再レンダリングをまたいで保持するユーザー回答データ。
- **Validation_Error**: クイズデータがスキーマ要件を満たさない場合に `Quiz_Engine` が送出する例外。

---

## Requirements

### Requirement 1: プリセットクイズのロード

**User Story:** As a demo presenter, I want to load the preset quiz instantly without any network calls, so that the demonstration runs smoothly even in offline environments.

#### Acceptance Criteria

1. WHEN a user selects the preset quiz option, THE System SHALL load `sample_data/preset_quiz.json` from the local filesystem without making any network requests.
2. WHEN the preset quiz file is loaded, THE Quiz_Engine SHALL parse the JSON into a `Quiz_Set` object containing a title, a source topic, and a list of at least 1 `Quiz` object, where each `Quiz` has non-empty question text, at least 2 answer choices, and a correct answer indicator.
3. IF the preset quiz file is missing or unreadable, THEN THE System SHALL display an error message that includes the file path and the reason for the failure, and shall leave the UI in an interactive state so the user can return to the selection screen without the application raising an unhandled exception.

---

### Requirement 2: クイズ画面の描画

**User Story:** As a learner, I want to see each question rendered with exactly 4 radio-button choices, so that I can select my answer without ambiguity.

#### Acceptance Criteria

1. WHEN a `Quiz_Set` is loaded, THE UI SHALL render each `Quiz` as a visually distinct block containing the question text and exactly 4 single-choice radio button options, with each block separated from adjacent blocks by a visible boundary.
2. WHEN a `Quiz_Set` is loaded, THE UI SHALL display the quiz title and source topic at the top of the page.
3. WHILE a quiz session is active, THE System SHALL maintain each user's selected radio button value in `Session_State` across Streamlit re-renders.
4. WHILE a quiz session is active, THE UI SHALL display a submit button that is visible but disabled until the user has selected an answer for every question in the `Quiz_Set`, at which point the submit button SHALL become enabled.
5. IF a `Quiz` in the loaded `Quiz_Set` contains fewer or more than 4 answer options, THEN THE UI SHALL display an error message indicating the quiz data is invalid and SHALL NOT render that `Quiz` as an answerable question.

---

### Requirement 3: 採点計算

**User Story:** As a learner, I want to receive an accurate score after submitting my answers, so that I can understand how well I understood the material.

#### Acceptance Criteria

1. WHEN the user submits answers, THE Quiz_Engine SHALL calculate the `Score` as the count of answers where the user's selected index equals the `correct_index` of the corresponding `Quiz`; any question without a selected answer SHALL be counted as incorrect.
2. WHEN the user submits answers and `total_questions` is greater than 0, THE Quiz_Engine SHALL calculate the score percentage as `(correct_count / total_questions) * 100`, rounded to one decimal place.
3. THE Quiz_Engine SHALL treat each question independently; the score of one question SHALL NOT affect the evaluation of any other question.
4. WHEN scoring is complete, THE Quiz_Engine SHALL return the `Score` object (containing correct_count, total_questions, and percentage) to the caller.
5. IF a `Quiz_Set` contains 0 questions, THEN THE Quiz_Engine SHALL return a `Score` with correct_count of 0, total_questions of 0, and percentage of 0.0 without raising an exception.

---

### Requirement 4: 結果表示とフィードバック

**User Story:** As a learner, I want to see visual feedback and explanations after submitting, so that I can learn from both correct and incorrect answers.

#### Acceptance Criteria

1. WHEN results are displayed, THE UI SHALL show the `Score` (correct count, total count, and percentage) in a summary section at the top of the results view.
2. WHEN the score percentage is 80% or higher, THE UI SHALL trigger Streamlit balloons animation and display a congratulatory success message indicating the score threshold was met.
3. IF the score percentage is below 80%, THEN THE UI SHALL display an encouraging message indicating the score and prompting the user to review the explanations, without triggering the balloons animation.
4. WHEN results are displayed, THE UI SHALL render an educational card for each `Quiz` that reveals the correct answer and the full `explanation` text.
5. WHEN results are displayed, THE UI SHALL visually distinguish correct answers from incorrect answers for each question in the educational cards using a distinct label or icon (e.g., a checkmark indicator for correct and a cross indicator for incorrect), such that the distinction is identifiable without relying solely on color.
6. WHEN results are displayed, THE UI SHALL show the user's selected answer alongside the correct answer in each educational card, so the user can compare their response to the correct one.

---

### Requirement 5: クイズデータのバリデーション

**User Story:** As a developer, I want invalid quiz data to produce a clear validation error instead of a runtime crash, so that the application remains stable when unexpected data is provided.

#### Acceptance Criteria

1. WHEN quiz data is parsed, THE Quiz_Engine SHALL validate that each `Quiz` contains exactly 4 items in the `choices` list.
2. WHEN quiz data is parsed, THE Quiz_Engine SHALL validate that `correct_index` is an integer in the range 0 to 3 inclusive.
3. WHEN quiz data is parsed, THE Quiz_Engine SHALL validate that `id`, `question`, and `explanation` are present and non-empty, and that each item in the `choices` list is a non-empty string.
4. IF any `Quiz` fails validation, THEN THE Quiz_Engine SHALL raise a `Validation_Error` that includes the `id` of the failing question (or a positional index if `id` is absent or empty), the name of the invalid field, and the nature of the violation.
5. IF a `Validation_Error` is raised during quiz loading, THEN THE UI SHALL catch the error, display the error message to the user, and remain on the current screen in an interactive state without proceeding to quiz rendering.

---

### Requirement 6: セッション状態の管理

**User Story:** As a learner, I want my selected answers to be preserved across page interactions, so that Streamlit re-renders do not reset my progress unexpectedly.

#### Acceptance Criteria

1. THE System SHALL store all user-selected answers in `Session_State` using unique keys derived from each `Quiz` id, where no two distinct `Quiz` items in the same `Quiz_Set` produce the same key.
2. WHEN the user navigates between questions or the page is re-rendered, THE UI SHALL restore each radio button to the previously selected value from `Session_State`; IF no entry exists for a question, THE UI SHALL render that radio button in an unselected state.
3. WHEN the user clicks a "Restart Quiz" control, THE System SHALL clear only the answer entries associated with the current quiz from `Session_State` and SHALL return the UI to the first question at index 0, leaving any unrelated `Session_State` entries intact.

---

### Requirement 7: クイズデータのパースとシリアライズの整合性

**User Story:** As a developer, I want the Quiz_Engine's parse and serialize functions to be round-trip consistent, so that data integrity is guaranteed and property-based tests can verify correctness.

#### Acceptance Criteria

1. THE Quiz_Engine SHALL provide a `parse_quiz_set` function that accepts a dict containing all `Quiz_Set` fields (title, source_topic, questions) and deserializes it into a `Quiz_Set` object, mapping each entry in the questions array to a `Quiz` object with all five fields (id, question, choices, correct_index, explanation).
2. THE Quiz_Engine SHALL provide a `serialize_quiz_set` function that accepts a `Quiz_Set` object and produces a JSON-compatible dict containing all `Quiz_Set` fields and all five `Quiz` fields for each question, preserving the types and values of all fields.
3. THE Quiz_Engine serialize and parse functions SHALL satisfy the round-trip property: for any valid `Quiz_Set` object q, invoking `parse_quiz_set(serialize_quiz_set(q))` SHALL produce a `Quiz_Set` object whose title, source_topic, and every field of every `Quiz` are equal to those of q.
4. IF `serialize_quiz_set` is called with an invalid `Quiz_Set` object (one that would fail the validation rules in Requirement 5), THEN THE Quiz_Engine SHALL raise a `Validation_Error` without returning a partial dict.
