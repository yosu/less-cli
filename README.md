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
poetry run less index <ディレクトリパス>
```

### 検索

インデックス済みドキュメントに対してセマンティック検索を実行します。

```bash
poetry run less search "<検索クエリ>"
```

## 開発

```bash
# テストの実行
poetry run pytest

# リンターの実行
poetry run ruff check .
```
