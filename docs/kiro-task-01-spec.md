# Kiro Task 01: QuickQuiz Studio MVP Spec

Kiro IDEでこのリポジトリを開き、Specsの「+」またはチャットからFeature Specを開始します。通常のRequirements-Firstを選択し、以下の起動プロンプトを最初に一度貼り付けてください。

---

## Kiro IDEに貼る起動プロンプト

```text
このリポジトリの docs/kiro-task-01-spec.md を読み、「Spec作成の詳細指示」を今回の作業指示として適用してください。
KiroのFeature Spec / Requirements-Firstワークフローで、QuickQuiz StudioのMVP Specを作成します。
成果物は .kiro/specs/quiz-studio/ の requirements.md、design.md、tasks.md の3ファイルです。
既存の pyproject.toml、README.md、sample_data/sample_article.txt、sample_data/preset_quiz.json も確認してください。
UIとクイズロジック（採点・バリデーション）の分離、プリセット即答モード、4択クイズ仕様、pytest/Hypothesisを含む最小MVPに限定します。
requirementsとdesignの段階確認はIDEの操作に従って進めます。
tasks.mdまで生成したら停止してください。今回はアプリ・テストの実装、他Lessonの設定、Git操作を行わないでください。
完了時は3ファイルのパス、主要タスク、設計上の制限だけを簡潔に報告してください。
```

---

## Spec作成の詳細指示

```text
QuickQuiz StudioのMVPを、KiroのFeature Spec / Requirements-Firstワークフローで仕様化してください。
今回はSpecの作成（Lesson 1）のみです。requirements.md、design.md、tasks.mdの生成が完了したら停止し、アプリやテストの実装は開始しないでください。

プロジェクト名: QuickQuiz Studio
Spec名: quiz-studio
成果物ディレクトリ: .kiro/specs/quiz-studio/ (requirements.md, design.md, tasks.md)

【目的】
技術ドキュメントや記事から4択のインタラクティブ学習クイズを生成し、ブラウザ上で学習・即時採点・解説確認ができるStreamlit Webアプリケーション。
デモ動画でスムーズに動く「プリセットモード（オフライン即答）」と、将来的なLLM API生成の両方を見据えた堅牢な設計を目指します。

【確認する既存ファイル】
- pyproject.toml
- README.md
- sample_data/sample_article.txt
- sample_data/preset_quiz.json
※依存パッケージ（streamlit, requests, pytest, hypothesis）は導入済みです。

【技術・アーキテクチャ要件】
- Python 3.10以上、Streamlit。
- UIとビジネスロジックの完全分離:
  - app.py: Streamlit UI、セッション状態管理、クイズ回答フォーム、採点演出。
  - src/quiz_engine.py: クイズJSONのパース、バリデーション、採点計算ロジック（副作用のない純粋関数）。
- クイズデータ構造（型定義）:
  - id: int
  - question: str
  - choices: list[str] (厳密に4個の選択肢)
  - correct_index: int (0 <= correct_index <= 3)
  - explanation: str
- テスト方針:
  - tests/test_quiz.py: 通常の単体テスト（具体例のパース、採点計算）。
  - tests/test_properties.py: Hypothesisを用いたプロパティベーステスト（不変条件の検証）。

【MVPの受入条件（EARS記法準拠）】
1. WHEN a user selects the preset quiz option, THE SYSTEM SHALL load sample_data/preset_quiz.json without network latency.
2. WHEN a quiz is loaded, THE SYSTEM SHALL render each question with exactly 4 single-choice radio options.
3. WHEN the user submits answers, THE SYSTEM SHALL calculate the score (correct count / total questions) and percentage.
4. WHEN results are displayed, THE SYSTEM SHALL show visual feedback (balloons/success message for high scores, educational cards) and reveal explanations for each question.
5. WHEN invalid quiz data (e.g. fewer than 4 choices, out-of-range correct_index) is supplied, THE SYSTEM SHALL raise a clear validation error without crashing the application.
6. THE SYSTEM SHALL maintain user answer state across Streamlit re-renders using st.session_state.

【Spec文書の構成】
- requirements.md: ユーザーストーリーとEARS形式の受入条件。
- design.md: UI設計、コンポーネント構造、データモデル、バリデーション方針、Hypothesisテスト設計。
- tasks.md: 実装タスク一覧。
  1. Steering作成（Lesson 2）
  2. コアロジック（src/quiz_engine.py）実装と通常テスト
  3. Streamlit UI（app.py）実装とプリセット動作確認
  4. pytest Hook設定と発火（Lesson 3）
  5. Hypothesisプロパティテスト実装と検証（Lesson 4）
  6. Power/MCP連携（Lesson 5 & 6）
  7. Custom Agentによるクイズ品質レビュー（Lesson 7）

tasks.mdの生成完了まで進め、実装コードの出力は行わないでください。
```

---

## 完了後に確認するもの

1. `.kiro/specs/quiz-studio/requirements.md`
2. `.kiro/specs/quiz-studio/design.md`
3. `.kiro/specs/quiz-studio/tasks.md`
上記3ファイルが生成されていることを確認してください。
