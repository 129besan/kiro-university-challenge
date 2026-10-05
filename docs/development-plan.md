# ChangeLens 開発手順

## 進め方

Codexによる準備を終えたら、まずKiro IDEでMVPのSpecを作成する。Codexは`.kiro`以下の成果物やProperty-based testsを代わりに生成しない。Kiroの結果を各段階で確認し、次のプロンプトはその時点の実ファイルに合わせて作る。

初期のCodex環境では`.git`が読み取り専用だったが、2026年10月5日の設定更新で書き込み可能になった。以降のGit操作はCodexで進める。準備ファイルのcommitでは対象を明示する。これはKiroへのAIリクエストを必要としない。

```bash
git add .gitignore README.md pyproject.toml requirements.lock.txt src/__init__.py sample_data docs
git commit -m "chore: prepare ChangeLens development environment"
```

この環境ではSSHでのremote接続も失敗した。HTTPSとghによる読み取りは成功したが、pushはまだ行っていない。後の公開工程で適切な接続方法を使う。

| 段階 | 担当と作業 | 完了条件 |
| --- | --- | --- |
| 0 | Codex: Git・Python確認、依存導入、架空サンプル、プロンプト準備 | 環境を確認し、最初のKiro作業を具体化 |
| 1 | Kiro IDE: MVPのSpecを生成 | requirements/design/tasksが`.kiro/specs/`に存在。実装はまだ開始しない |
| 2 | Kiro IDE: Steeringを作成し、Specを用いてMVPの主要実装と通常テストを実施 | 型付きの副作用の少ない比較関数、UI分離、主要な変更を表示、pytest成功。Steering利用を記録 |
| 3 | Kiro: pytestを実行するHookを作成し、Pythonの小さな実変更で発火 | Hook設定と実行結果を保存。可能ならagent処理を伴わないshell actionを選ぶ |
| 4 | Kiro IDE: Hypothesisの性質を生成し、実行・必要な修正を実施 | 同一入力、空入力の追加/削除、入力の再構成の性質が通る |
| 5 | Kiro: 適切なPowerを導入して利用、MCPで公開資料を取得 | 実際のPower起動とMCP tool callを記録。取得結果を仕様確認またはサンプルに利用 |
| 6 | Kiro: `diff-reviewer`を作成し、実コードをレビュー | 指摘を最低1件コード・テストなどに反映し、検証結果を保存 |
| 7 | Codex: UI確認、README完成、GitHub、デモ・提出準備 | 全Lessonの証拠と動く製品が確認可能 |

段階5のPowerとMCPは、一緒に利用できる実用的なPowerが見つかればまとめる。候補は実装後に、実際のKiro環境で導入可能なものから選ぶ。

Power内のMCP設定はprojectの`.kiro/settings/mcp.json`に保存されない場合がある。ユーザー指定のproject設定を残せる方法を選び、必要ならKiroにproject MCPを別途設定させる。

## MVPの範囲

- OLD/NEW入力、Compareボタン、追加・削除・変更、同一入力の「変更なし」。
- 日付・金額・数値を強調し、URLの変更も識別する。
- `申込期限: 10月10日 → 10月15日`のようなラベルと旧値・新値。通常の文言変更も元の文章で確認できる。
- 原文を保持した比較結果と、UIから独立した比較・抽出関数。
- pytestの具体例、Hypothesisの性質、架空サンプル。

意味解析モデル、外部LLM、DB、ログイン、アップロード、文書形式の変換、PDF解析、履歴保存はMVPに含めない。入力の保存や外部送信も行わない。

## Credits

予算はユーザー指定の50 credits以内。開始残高はまだ確認していない。1プロンプトを1 creditと仮定せず、各Kiro段階の前後でUsage表示を確認して[実施記録](kiro-usage.md)に残す。

各プロンプトで目的・変更対象・完了条件・停止条件を指定する。相談の往復や全体の再生成を避け、失敗はCodexが先に原因を調べる。50以内を実測するまでは達成したと記載しない。

## 提出チェック

[公式Challenge](https://kiro.dev/2026/university/)と[公式規約](https://kiro.dev/2026/university/terms/)を確認した。締切は2026年10月5日23:59 PDT、**日本時間2026年10月6日15:59**。

- [ ] 正常に起動するMVP、UI操作の確認、pytest・Hypothesis成功。
- [ ] Kiroを主要な開発ツールとして使用した実装と7 Lessonの実施記録。
- [ ] 自分が所有する新規public GitHub repo。最初のcommitが2026年9月21日09:00 PT以降で、それ以前のcommitがない。
- [ ] `.kiro/specs/`、`steering/`、`hooks/`、`agents/`、秘密情報を除いた`settings/mcp.json`、Powerの実使用証拠。
- [ ] README、サンプル、Lessonごとの説明、50 credits以内の実測記録。
- [ ] 製品の動作と7 Lessonを紹介する30秒〜3分の公開デモ動画。
- [ ] XまたはLinkedInでの公開投稿。説明2〜3文、repo・動画リンク、`#KiroUniversity`と`#BuildWithKiro`、Xは`@kirodotdev`、LinkedInは`@kiro`。
- [ ] [提出フォーム](https://kiro.dev/2026/university/submit/)にrepo、動画、投稿の各リンクとLesson説明を入力して期限内に提出。

参加資格には18歳以上、GitHubアカウント開設から3か月以上などの条件がある。参加者自身が公式規約で確認する。投稿・フォーム送信は提出内容を用意した後の工程で扱う。

公式規約では締切後、2026年10月19日23:59 PTまたはaward通知受領の早い方までrepoへのcommitを禁止している。提出後の修正はこの期間を考慮する。
