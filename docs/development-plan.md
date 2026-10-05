# QuickQuiz Studio 開発・提出手順書

## 全体スケジュール（締切: 2026年10月6日 15:59 JST）

| 時間帯目安 | 工程 | 担当と作業内容 | 成果物 / チェック |
| :--- | :--- | :--- | :--- |
| **00:30 - 01:30** | **準備 & Spec策定 (Lesson 1)** | Codex: プロンプト準備<br>Kiro IDE: Feature Spec生成 | `.kiro/specs/quiz-studio/` (requirements, design, tasks) |
| **01:30 - 02:30** | **Steering & MVP実装 (Lesson 2)** | Kiro IDE: Steering作成 → コアロジック・UI・通常テスト実装 | `.kiro/steering/coding-standards.md`, `src/quiz_engine.py`, `app.py`, `tests/test_quiz.py` |
| **02:30 - 03:30** | **Hooks & Property Tests (Lesson 3 & 4)** | Kiro IDE: pytest Hook設定・発火<br>Hypothesisテスト生成・実行 | `.kiro/hooks/run-tests-on-save.json`, `tests/test_properties.py` |
| **03:30 - 04:30** | **Powers, MCP, Custom Agent (Lesson 5, 6, 7)** | Kiro: Power使用、MCP設定（Webフェッチ）、Custom Agent（クイズ品質校正）作成・実行 | `.kiro/settings/mcp.json`, `.kiro/agents/quiz-reviewer.json`, 使用記録 |
| **04:30 - 05:30** | **検証 & ドキュメント整備** | Codex: 全体動作検証、Git commit/push確認、README更新 | 全テストPASS、正常起動確認 |
| **昼以降 (13:00〜)** | **デモ動画撮影・SNS投稿・提出** | ユーザー: 3分以内のデモ動画撮影、X/LinkedIn投稿、提出フォーム送信 | 提出完了（15:59 JST厳守） |

---

## 7つのレッスンの実装詳細

### Lesson 1: Feature Specs
- **配置**: `.kiro/specs/quiz-studio/`
- **内容**: EARS記法でクイズアプリの要件（requirements.md）、アーキテクチャ設計（design.md）、タスク分解（tasks.md）をKiroで生成。

### Lesson 2: Steering Documents
- **配置**: `.kiro/steering/coding-standards.md`
- **内容**: 型定義（TypedDict / Pydantic）、Streamlitのステート管理ルール、ビジネスロジックのUI分離ルールをKiroに適用。

### Lesson 3: Hooks
- **配置**: `.kiro/hooks/run-tests-on-save.json`
- **内容**: Pythonファイル保存時に `pytest` を自動実行するフックを作成し、実際に発火させる。

### Lesson 4: Property-Based Testing
- **配置**: `tests/test_properties.py`
- **内容**: Hypothesisを利用し、採点計算ロジック（スコア範囲、全正解/全不正解の整合性）やクイズスキーマの不変性を検証。

### Lesson 5: Powers
- **配置**: `docs/kiro-usage.md` にログ記録
- **内容**: Kiro Power（Web FetcherやPython関連Power）を有効化し、開発やデータ取得に活用。

### Lesson 6: MCP (Model Context Protocol)
- **配置**: `.kiro/settings/mcp.json`
- **内容**: 外部Webページ取得用のMCPサーバーを定義し、Kiroが技術記事を取得してクイズを生成するパイプラインを実演。

### Lesson 7: Custom Agents
- **配置**: `.kiro/agents/quiz-reviewer.json`
- **内容**: クイズの品質レビュー（選択肢の重複チェック、解説の妥当性、難易度判定）を行うカスタムエージェントを作成し、レビュー結果を反映。

---

## 最終提出チェックリスト

- [ ] 正常に起動するStreamlitアプリ（`python -m streamlit run app.py`）
- [ ] pytestおよびHypothesisテストがすべて成功（`python -m pytest`）
- [ ] GitHubの公開リポジトリ（最初のコミットが2026年9月21日09:00 PT以降）
- [ ] `.kiro` フォルダに必要な全レッスン成果物が存在（specs, steering, hooks, agents, settings/mcp.json）
- [ ] 30秒〜3分のデモ動画（YouTube、Google Drive、またはSNS直接アップロード）
  - アプリの動作（プリセットロード、回答、採点アニメーション、解説）
  - Kiroでの開発（Spec、Hook発火、MCP連携、Agentレビューの様子）
- [ ] XまたはLinkedInでの公開投稿
  - ハッシュタグ: `#KiroUniversity` `#BuildWithKiro`
  - メンション: Xなら `@kirodotdev`、LinkedInなら `@kiro`
  - リポジトリURL、2〜3文の説明、デモ動画
- [ ] [公式提出フォーム](https://kiro.dev/2026/university/)から送信（2026年10月6日 15:59 JST締切）
