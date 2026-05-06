import click


@click.group()
def main():
    """LESS — LLM Empowered Semantic Search"""
    pass


@main.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
def index(directory):
    """指定ディレクトリの全PDFをインデックスする。"""
    click.echo(f"インデックス対象: {directory}")


@main.command()
@click.argument("query")
def search(query):
    """インデックス済みドキュメントをセマンティック検索する。"""
    click.echo(f"検索クエリ: {query}")
