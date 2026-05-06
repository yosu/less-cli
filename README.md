# LESS — LLM Empowered Semantic Search

PDFドキュメントをセマンティック検索できるコマンドラインツール。

## キーテクノロジー

- **Python** — AI関連のデファクトスタンダード
- **ChromaDB** — 軽量・高性能なオープンソースベクターデータベース
- **PyPDF** — PDFからのテキスト抽出
- **spaCy** — テキストパースとセンテンスレベルのチャンク抽出

## セットアップ

```bash
# 依存関係のインストール
poetry install

# spaCyの日本語モデルをダウンロード（必要に応じて）
poetry run python -m spacy download en_core_web_sm
```

## 使い方

### インデックス作成

指定ディレクトリ内の全PDFファイルをベクターデータベースにインデックスします。

```bash
make index DIR=<ディレクトリパス>
```

### 検索

インデックス済みドキュメントに対してセマンティック検索を実行します。

```bash
make search Q="<検索クエリ>"
```

## Makeコマンド一覧

| コマンド | 説明 |
|---|---|
| `make index DIR=<パス>` | 指定ディレクトリのPDFをインデックスする |
| `make search Q="<クエリ>"` | インデックス済みドキュメントを検索する |
| `make test` | テストを実行する |
| `make lint` | リンター（ruff）を実行する |
| `make clean-db` | ChromaDBのデータを削除する |
