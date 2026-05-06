from click.testing import CliRunner

from less.cli import main


def test_main_shows_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "LESS" in result.output


def test_index_requires_directory():
    runner = CliRunner()
    result = runner.invoke(main, ["index"])
    assert result.exit_code != 0


def test_search_requires_query():
    runner = CliRunner()
    result = runner.invoke(main, ["search"])
    assert result.exit_code != 0
