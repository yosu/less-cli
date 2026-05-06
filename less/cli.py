from pathlib import Path

import click

from less.indexer import find_pdfs, extract_text, chunk_text, create_collection, store_chunks

DEFAULT_DB_PATH = Path.cwd() / "chroma_data"


@click.group()
def main():
    """LESS — LLM Empowered Semantic Search"""
    pass


@main.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--db-path", default=str(DEFAULT_DB_PATH), help="ChromaDBの保存先パス")
def index(directory, db_path):
    """指定ディレクトリの全PDFをインデックスする。"""
    click.echo(f"対象ディレクトリ: {directory}")

    pdfs = find_pdfs(directory)
    if not pdfs:
        click.echo("PDFファイルが見つかりません。")
        return

    click.echo(f"{len(pdfs)}件のPDFファイルを検出しました。")

    collection = create_collection(db_path)
    total_chunks = 0

    for pdf_path in pdfs:
        click.echo(f"  処理中: {pdf_path.name}")
        text = extract_text(pdf_path)
        if not text:
            click.echo(f"    テキストを抽出できませんでした。スキップします。")
            continue
        chunks = chunk_text(text)
        click.echo(f"    {len(chunks)}チャンクを抽出しました。")
        store_chunks(chunks, pdf_path, collection)
        total_chunks += len(chunks)

    click.echo(f"完了: {len(pdfs)}ファイル, {total_chunks}チャンクをインデックスしました。")


@main.command()
@click.argument("query")
def search(query):
    """インデックス済みドキュメントをセマンティック検索する。"""
    click.echo(f"検索クエリ: {query}")
