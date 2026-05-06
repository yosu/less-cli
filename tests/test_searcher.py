from pathlib import Path

import pytest

from less.indexer import index_directory
from less.searcher import search

SAMPLE_PDF = Path(__file__).parent / "Textbook.pdf"


class TestSearch:
    def test_returns_results_with_expected_fields(self, tmp_path):
        db_path = tmp_path / "chroma_db"
        _index_sample_text(db_path)

        results = search("gravity", db_path)

        assert len(results) > 0
        first = results[0]
        assert "document" in first
        assert "source" in first
        assert "distance" in first

    def test_returns_most_relevant_result_first(self, tmp_path):
        db_path = tmp_path / "chroma_db"
        _index_sample_text(db_path)

        results = search("gravity and physics", db_path)

        assert "gravity" in results[0]["document"].lower()

    def test_respects_n_results(self, tmp_path):
        db_path = tmp_path / "chroma_db"
        _index_sample_text(db_path)

        results = search("science", db_path, n_results=2)

        assert len(results) <= 2

    def test_returns_empty_list_when_no_documents(self, tmp_path):
        db_path = tmp_path / "chroma_db"

        results = search("anything", db_path)

        assert results == []


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="サンプルPDFが見つかりません")
class TestSearchWithRealPdf:
    def test_search_real_pdf(self, tmp_path):
        db_path = tmp_path / "chroma_db"
        index_directory(SAMPLE_PDF.parent, db_path)

        results = search("sensory receptors", db_path)

        assert len(results) > 0
        combined = " ".join(r["document"] for r in results)
        assert "receptor" in combined.lower()

    def test_search_returns_source_metadata(self, tmp_path):
        db_path = tmp_path / "chroma_db"
        index_directory(SAMPLE_PDF.parent, db_path)

        results = search("muscle spindle", db_path)

        assert len(results) > 0
        assert "Textbook.pdf" in results[0]["source"]


def _index_sample_text(db_path):
    import chromadb

    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_or_create_collection(name="documents")
    collection.add(
        documents=[
            "Gravity is a fundamental force of physics.",
            "Photosynthesis converts sunlight into energy.",
            "The ocean covers most of the Earth surface.",
        ],
        ids=["doc_0", "doc_1", "doc_2"],
        metadatas=[
            {"source": "science.pdf", "chunk_index": 0},
            {"source": "biology.pdf", "chunk_index": 0},
            {"source": "geography.pdf", "chunk_index": 0},
        ],
    )
