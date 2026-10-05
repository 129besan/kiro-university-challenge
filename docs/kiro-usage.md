# Kiro 実施記録

この表はKiroの実利用を確認してから更新する。作成予定のファイルやCodexの作業をKiroの実績として記録しない。

## 開始時点

- Kiro IDE: ローカルのインストール情報は1.2.4。IDE画面での確認は未実施。
- Kiro CLI: 実行ファイルあり。IDEの作業をCLIへ置き換えていない。
- Credits: 開始残高・消費量とも未確認。Codexの準備ではKiroへAIリクエストを送っていない。
- リポジトリ: ローカルは開始時にcommitなし。`origin`は`git@github.com:129besan/kiro-university-challenge.git`。
- GitHub: 2026年10月5日JSTの確認でpublic、2026年10月3日作成、refs/branchesなし。開始前の履歴は確認されていない。
- Git操作: 初期は`.git`が読み取り専用だったが、2026年10月5日の設定更新で書き込み可能になった。以降のGit操作はCodexで担当する。SSH接続は失敗したが、HTTPSと認証済みghでremoteの読み取りを確認した。pushは未実施。

## Lessonごとの証拠

| Lesson | 状態 | 設定・成果物 | 実使用の確認 |
| --- | --- | --- | --- |
| 1 Specs | 実施済み | `.kiro/specs/quiz-studio/` | IDEで3文書（requirements, design, tasks）を生成。commit: 74fdce6 |
| 2 Steering | 実施済み | `.kiro/steering/coding-standards.md` | 型安全・UI分離の規約作成、MVP実装（app.py, src/quiz_engine.py, 43 pytest通過）。commit: 2f73ee4 |
| 3 Hooks | 未実施 | `.kiro/hooks/` | Python変更イベント、Hookのpytest実行、結果 |
| 4 PBT | 未実施 | `tests/test_properties.py` | Kiro IDEによるHypothesisの生成・実行・パス確認 |
| 5 Powers | 未実施 | 導入したPower名・利用記録 | 実行したPowerと、開発にどう役立ったか |
| 6 MCP | 未実施 | `.kiro/settings/mcp.json` | KiroからのMCPツール（Webフェッチ等）呼び出しと利用先 |
| 7 Custom agents | 未実施 | `.kiro/agents/`、レビュー記録 | `quiz-reviewer`選択、クイズ品質への指摘、反映したcommit |

## 実行ログ

まだKiroの実行ログはない。完了した工程ごとに次の項目を実測して追加する。

```text
実行日時:
Kiroの版・使用した画面・モデル:
Lessonと実施目的:
渡したプロンプトのファイル:
実行前のcredits / 実行後のcredits:
生成・変更したファイル:
実際に実行したコマンドまたはtool:
観測した結果と終了コード:
必要だった修正:
実行記録または個人情報を除いたスクリーンショットへのリンク:
対応するcommit:
```

スクリーンショットやログにメール、アカウント情報、トークン、実在する個人情報を含めない。MCPには秘密情報を含まない公開資料の取得を優先する。記録がない項目は推測で埋めない。
