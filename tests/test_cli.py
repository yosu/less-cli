from pathlib import Path

from click.testing import CliRunner

from less.cli import main

SAMPLE_PDF = Path(__file__).parent / "Textbook.pdf"


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


class TestIndexCommand:
    def test_indexes_pdfs_and_shows_progress(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["index", str(SAMPLE_PDF.parent), "--db-path", str(tmp_path / "db")])

        assert result.exit_code == 0
        assert "PDF" in result.output
        assert "完了" in result.output

    def test_reports_no_pdfs_found(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(main, ["index", str(empty_dir)])

        assert result.exit_code == 0
        assert "見つかりません" in result.output

    def test_shows_file_count(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["index", str(SAMPLE_PDF.parent), "--db-path", str(tmp_path / "db")])

        assert result.exit_code == 0
        assert "1" in result.output
