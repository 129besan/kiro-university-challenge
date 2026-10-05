# ChangeLens

旧文書と新文書を比較し、期限・料金・定員などの重要な変更を見つけやすくするWebアプリです。募集要項、イベント案内、READMEなどを想定しています。

**開発状況:** 開発環境とサンプルを準備済みです。アプリ本体はKiroによるSpec作成後に実装します。

目標とする表示:

```text
変更  申込期限: 10月10日 → 10月15日  [日付]
変更  参加費: 1,000円 → 1,500円      [金額]
変更  定員: 30名 → 50名              [数値]
```

Python、Streamlit、標準ライブラリのdifflibを使います。UIは`app.py`、比較と抽出のロジックは`src/`に分離します。外部LLM APIやDBは使用しません。固有名詞は文言の変更として表示し、自動の意味理解は前提にしません。

## 開発環境

Python 3.10以上。現在の確認対象はPython 3.14.7です。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Python 3.14.7でStreamlit 1.65.0、pytest 9.1.1、Hypothesis 6.168.3の導入・importと`pip check`の成功を確認しました。アプリの動作・テストはまだ未検証です。

直接依存の確認済みバージョンは`pyproject.toml`、推移的な依存まで含む確認環境は`requirements.lock.txt`に記録しています。確認環境を揃える場合はlockファイルを先にインストールします。

```bash
python -m pip install -r requirements.lock.txt
python -m pip install -e '.[dev]' --no-deps
```

MVP実装後の起動・テストコマンド:

```bash
python -m streamlit run app.py
python -m pytest
```

現時点では`app.py`とテストは未作成です。起動・テストの成功は実装後に記録します。

## サンプル

[旧版](sample_data/event_old.txt)と[新版](sample_data/event_new.txt)に、期限・金額・人数・URL・会場の変更、行の追加と削除を含めています。架空のデータです。[想定変更一覧](sample_data/README.md)を使って動作を確認します。

## 開発と提出

KiroがSpec、Steering、MVPの主要実装、Hook、Property-based tests、Power、MCP、Custom Agentを担当します。Codexは事前準備、検証、原因分析、Git操作、ドキュメント整備を担当します。

- [開発手順と提出チェック](docs/development-plan.md)
- [Kiro実施記録](docs/kiro-usage.md)
- [最初にKiroへ渡すSpec作成プロンプト](docs/kiro-task-01-spec.md)

## Kiro University Challenge

以下は実施状況です。ファイルの存在だけでは完了とせず、Kiroでの実行を確認して更新します。

### Lesson 1: Specs

未実施。Kiro IDEでrequirements/design/tasksを生成し、MVP実装で利用します。

### Lesson 2: Steering

未実施。Kiroが作成した開発方針をMVP実装に反映します。

### Lesson 3: Hooks

未実施。Python変更時にpytestを実行するHookをKiroで作成し、一度発火させます。

### Lesson 4: Property-based testing

未実施。Kiro IDEでHypothesisのテストを生成・実行し、失敗した場合は修正します。

### Lesson 5: Powers

未実施。ChangeLensの開発に適したPowerを導入・利用し、利用前後を記録します。

### Lesson 6: MCP

未実施。Kiroから公開資料を実際に取得し、仕様確認またはサンプル作成に利用します。

### Lesson 7: Custom agents

未実施。Kiroで`diff-reviewer`を作成し、レビュー結果を少なくとも1件反映します。
