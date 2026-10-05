# Kiro Task 01: MVP Spec

Kiro IDEでこのリポジトリを開き、Specsの「+」またはチャットのSpecからFeature Specを開始する。通常のRequirements-Firstを選ぶ。以下の起動プロンプトを最初に一度貼り付ける。詳細指示はこのファイルからKiroが読み取る。

requirements、designの各段階で内容を確認し、要件を満たしていればIDEの次へ進む操作で承認する。追加の相談プロンプトは不要。`tasks.md`までできたら停止し、実装の「Run all」などはまだ実行しない。UI表示はIDEの版によって異なる。[公式手順](https://kiro.dev/docs/specs/feature-specs/requirements-first/)

## IDEに貼る起動プロンプト

```text
このリポジトリの docs/kiro-task-01-spec.md を読み、「Spec作成の詳細指示」を今回の作業指示として適用してください。
KiroのFeature Spec / Requirements-Firstで、ChangeLensのMVP Specを作成します。
成果物は .kiro/specs/changelens-mvp/ の requirements.md、design.md、tasks.md の3ファイルです。
既存の pyproject.toml、README.md、sample_data/event_old.txt、sample_data/event_new.txt も確認してください。
UIと比較・抽出ロジックの分離、日付・金額・数値・URLの強調、原文保持、pytest/Hypothesisを含む最小MVPに限定します。
requirementsとdesignの段階確認はIDEの操作に従って進めます。
tasks.mdまで生成したら停止してください。今回はアプリ・テストの実装、他Lessonの設定、依存追加、Git commit/pushを行わないでください。
完了時は3ファイルのパス、主要タスク、設計上の制限だけを簡潔に報告してください。
```

## Spec作成の詳細指示

```text
ChangeLensのMVPを、KiroのFeature Spec / Requirements-Firstワークフローで仕様化してください。
今回はSpecの作成だけです。requirements.md、design.md、tasks.mdの生成が完了したら停止し、アプリやテストの実装は開始しないでください。各段階はIDEの確認操作に従って進めます。

プロジェクト名: ChangeLens
Spec名: changelens-mvp
成果物: .kiro/specs/changelens-mvp/requirements.md、design.md、tasks.md

目的:
旧文書と新文書を比較し、人間に重要な変更を分かりやすく示す小さなWebアプリ。
募集要項、料金案内、イベント案内、READMEなどを想定します。
文字単位の差分だけでなく「申込期限: 10月10日 → 10月15日」のようにラベルと旧値・新値が分かる表示を目指します。

確認する既存ファイル:
pyproject.toml、README.md、sample_data/event_old.txt、sample_data/event_new.txt。
開発環境とsrc/__init__.pyのみ準備済みです。app.py、比較ロジック、テストはまだありません。
既存の依存設定とサンプルは再生成しないでください。

技術・構成:
- Python 3.10以上、Streamlit、標準ライブラリdifflib/re/dataclassesなど。
- pytestとHypothesis。依存はpyproject.tomlに設定済みです。
- app.pyはUIのみ、src/diff.pyは比較、src/extract.pyは重要な値の抽出。
- 比較と抽出は型ヒントのある、副作用の少ない関数。Streamlitへの依存はUIに限定。
- 比較の公開入口は compare(old: str, new: str)。内部の結果型は小さく設計する。
- tests/test_diff.pyは具体例、tests/test_properties.pyはHypothesisの性質。
- 不要な依存、外部LLM、DB、React、Docker、ログイン、PDF解析、アップロードは追加しない。

MVPの受入条件:
1. OLDとNEWの複数行入力欄とCompareボタンがある。
2. 追加・削除・変更を日本語のラベルで区別し、旧文と新文を読める。
3. 同一入力は空文字列も含め「変更なし」と表示する。
4. 空文字列から非空文字列への比較は追加のみ。逆は削除のみ。
5. 日付（例: 10月10日、2026-10-10、2026/10/10）、金額（例: 1,000円、¥1,000、$10.00）、数値（例: 30名、50%）、http/https URLの変更を見つけやすく表示する。
6. 行頭の「項目名: 値」または「項目名：値」で同じ項目名の値が変わった場合は、項目名と旧値→新値を表示する。重複ラベルの精密な対応付けは対象外。通常の文言変更も省略せず確認できる。
7. 固有名詞らしい文言の変更も通常の差分で見える。固有名詞の自動意味理解や辞書はMVPに不要。
8. 日付・金額・URL内の数字を別の一般数値として過剰に重複表示しない。
9. 比較結果は未変更部分も含む順序付きblock/segmentなどで原文を保持する。旧側を連結すればOLD、新側を連結すればNEWと完全一致する。UIは変更部分を表示する。
10. 比較ロジックで入力をstripしたり改行を正規化したりして原文を失わない。空白のみ、日本語、Unicode、末尾改行、複数行を扱える。
11. 同じ入力で結果が一定。結果の種別と重要値の分類はテスト可能な構造にする。
12. sample_dataの案内で期限・金額・定員・URL・会場の変更と、注意事項の削除、特典の追加を確認できる。
13. pytestが通り、Hypothesisで同一入力・空入力の追加/削除・原文の再構成を検証できる。
14. 入力は保存・外部送信しない。通常の入力文字列を実行可能なHTMLとして描画しない。

設計の方向:
difflibの行単位比較を基本にし、必要な変更箇所だけ行内の値を抽出します。
元テキストを保つ小さなデータ構造を使い、表示用の要約と原文を分離します。
高度な自然言語の意味比較、完全な移動検出、関係のない行の精密な対応付けは対象外です。
複雑な独自アルゴリズムを増やすより、説明できる制限と正しい原文表示を優先します。

Spec文書:
- requirements.md: 日本語のuser storyと検証可能なEARS形式の受入条件。
- design.md: UI/比較/抽出の分離、データ構造、比較と値抽出の方針、制限、テスト方針。
- tasks.md: 6〜8個程度の小さな主要タスク。要件との対応と検証方法を明記。必須テストをoptionalにしない。

tasksの順序:
A. KiroでSteeringを作成し、Python/Streamlit、UI分離、副作用の少ない関数、型ヒント、新機能のテスト、最小依存、小さな変更の方針を設定する。
B. そのSteeringとSpecを使い、比較・抽出ロジック、Streamlit UI、通常のpytest、サンプル確認までのMVP主要実装をKiroが担当する。
C. KiroでPython変更時のpytest Hookを作成し、一度実際に発火させる。
D. Kiro IDEでHypothesisのProperty-based testsを生成・実行し、失敗があれば修正する。
Power、MCP、Custom Agentの実利用はMVP確認後の別工程とし、今回は設定・実行しない。

完了時に、作成した3ファイルのパス、主要タスク、設計上の制限を簡潔に報告してください。
Git commit/push、依存の追加インストール、MVP実装、他Lessonの設定作成は今回は行わないでください。
```

## 完了後に確認するもの

- Kiro IDEが生成した3つのSpec文書。
- MVPの範囲、原文保持、通常テストとProperty-based tests、Steering利用の実装タスク。
- Kiroの完了メッセージと、確認できる場合は実行前後のcredits。
- この段階ではアプリ実装、他Lessonの設定、Lesson全体の完了宣言がないこと。

生成したファイルがこの共有リポジトリにあれば、Codexが内容を確認して次の工程を用意する。
