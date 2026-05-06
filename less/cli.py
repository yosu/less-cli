from pathlib import Path

import click

from less.indexer import find_pdfs, extract_pages, chunk_text, create_collection, store_chunks
from less.searcher import search as do_search

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
        pages = extract_pages(pdf_path)
        if not pages:
            click.echo("    テキストを抽出できませんでした。スキップします。")
            continue
        chunks = chunk_text(pages)
        click.echo(f"    {len(chunks)}チャンクを抽出しました。")
        store_chunks(chunks, pdf_path, collection)
        total_chunks += len(chunks)

    click.echo(f"完了: {len(pdfs)}ファイル, {total_chunks}チャンクをインデックスしました。")


@main.command()
@click.argument("query")
@click.option("--db-path", default=str(DEFAULT_DB_PATH), help="ChromaDBの保存先パス")
@click.option("-n", "--n-results", default=5, help="返す結果の最大件数")
def search(query, db_path, n_results):
    """インデックス済みドキュメントをセマンティック検索する。"""
    click.echo(f"検索クエリ: {query}")
    click.echo("検索中...")

    results = do_search(query, db_path, n_results=n_results)

    if not results:
        click.echo("結果が見つかりませんでした。")
        return

    click.echo(f"{len(results)}件の結果が見つかりました。\n")

    for i, result in enumerate(results, 1):
        source = Path(result["source"]).name
        distance = result["distance"]
        pages = result["pages"]
        document = result["document"]
        click.echo(f"[{i}] ({source}, p.{pages}, スコア: {distance:.4f})")
        click.echo(f"    {document}")
        click.echo()
