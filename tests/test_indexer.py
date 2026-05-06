from pathlib import Path

import pytest
from pypdf import PdfWriter

from less.indexer import chunk_text, extract_pages, find_pdfs, index_directory

SAMPLE_PDF = Path(__file__).parent / "Textbook.pdf"


def _create_pdf(path, text):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    page = writer.pages[0]
    page.merge_page(
        PdfWriter()
        ._add_page_with_text(text)
    ) if False else None
    # PyPDF cannot easily write text to a page, so we use a minimal approach:
    # Create a PDF with annotations that contain text for extraction testing.
    # Instead, let's write a real PDF using reportlab-free approach.
    writer.close()


def _make_test_pdf(path, text):
    """Create a minimal PDF with extractable text using raw PDF operators."""
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length {len(text) + 30} >>
stream
BT /F1 12 Tf 100 700 Td ({text}) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
0
%%EOF"""
    Path(path).write_text(pdf_content)


class TestFindPdfs:
    def test_finds_pdf_files_in_directory(self, tmp_path):
        (tmp_path / "doc1.pdf").touch()
        (tmp_path / "doc2.pdf").touch()
        (tmp_path / "notes.txt").touch()

        result = find_pdfs(tmp_path)

        assert len(result) == 2
        assert all(p.suffix == ".pdf" for p in result)

    def test_returns_empty_list_when_no_pdfs(self, tmp_path):
        (tmp_path / "notes.txt").touch()

        result = find_pdfs(tmp_path)

        assert result == []

    def test_finds_pdfs_in_subdirectories(self, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        (tmp_path / "top.pdf").touch()
        (sub / "nested.pdf").touch()

        result = find_pdfs(tmp_path)

        assert len(result) == 2


class TestExtractPages:
    def test_extracts_pages_from_pdf(self, tmp_path):
        pdf_path = tmp_path / "sample.pdf"
        _make_test_pdf(pdf_path, "Hello world this is a test document.")

        pages = extract_pages(pdf_path)

        assert len(pages) == 1
        assert pages[0]["page"] == 1
        assert "Hello world" in pages[0]["text"]

    def test_returns_empty_list_for_empty_pdf(self, tmp_path):
        pdf_path = tmp_path / "empty.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, "wb") as f:
            writer.write(f)

        pages = extract_pages(pdf_path)

        assert pages == []


def _pages(text, page=1):
    return [{"page": page, "text": text}]


def _multi_pages(page_texts):
    return [{"page": i, "text": t} for i, t in enumerate(page_texts, 1)]


class TestChunkText:
    def test_chunks_are_at_least_min_size(self):
        sentences = ["This is sentence number %d." % i for i in range(50)]
        text = " ".join(sentences)

        chunks = chunk_text(_pages(text))

        for chunk in chunks:
            assert len(chunk["text"]) >= 500

    def test_short_text_returns_single_chunk(self):
        pages = _pages("Machine learning is powerful. It can classify documents.")

        chunks = chunk_text(pages)

        assert len(chunks) == 1
        assert "Machine learning" in chunks[0]["text"]
        assert "classify documents" in chunks[0]["text"]

    def test_returns_empty_list_for_empty_input(self):
        assert chunk_text([]) == []

    def test_preserves_content(self):
        sentences = ["Sentence %d has some content here." % i for i in range(30)]
        text = " ".join(sentences)

        chunks = chunk_text(_pages(text))
        combined = " ".join(c["text"] for c in chunks)

        for sentence in sentences:
            assert sentence in combined

    def test_respects_custom_min_chunk_size(self):
        pages = _pages("First sentence here. Second sentence here. Third sentence here. Fourth sentence here.")

        chunks = chunk_text(pages, min_chunk_size=40)

        assert len(chunks) >= 2

    def test_remainder_appended_to_last_chunk(self):
        pages = _pages("A" * 500 + ". " + "B" * 100 + ".")

        chunks = chunk_text(pages)

        assert len(chunks) == 1

    def test_tracks_page_numbers(self):
        pages = _multi_pages([
            "First page content here. " * 30,
            "Second page content here. " * 30,
        ])

        chunks = chunk_text(pages)

        all_pages = set()
        for chunk in chunks:
            assert "pages" in chunk
            all_pages.update(chunk["pages"])
        assert 1 in all_pages
        assert 2 in all_pages

    def test_chunk_spanning_pages(self):
        pages = _multi_pages([
            "Short page one.",
            "Short page two.",
        ])

        chunks = chunk_text(pages)

        assert len(chunks) == 1
        assert sorted(chunks[0]["pages"]) == [1, 2]


class TestIndexDirectory:
    def test_indexes_pdfs_into_chromadb(self, tmp_path):
        pdf_path = tmp_path / "test.pdf"
        _make_test_pdf(pdf_path, "Artificial intelligence is transforming the world.")

        db_path = tmp_path / "chroma_db"
        stats = index_directory(tmp_path, db_path)

        assert stats["files"] == 1
        assert stats["chunks"] > 0

    def test_skips_directory_with_no_pdfs(self, tmp_path):
        (tmp_path / "readme.txt").touch()

        db_path = tmp_path / "chroma_db"
        stats = index_directory(tmp_path, db_path)

        assert stats["files"] == 0
        assert stats["chunks"] == 0


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="サンプルPDFが見つかりません")
class TestWithRealPdf:
    def test_extract_pages_from_real_pdf(self):
        pages = extract_pages(SAMPLE_PDF)

        assert len(pages) > 0
        assert all(p["page"] >= 1 for p in pages)
        combined = " ".join(p["text"] for p in pages)
        assert "Sensory Systems" in combined

    def test_chunk_real_pdf(self):
        pages = extract_pages(SAMPLE_PDF)
        chunks = chunk_text(pages)

        assert len(chunks) > 1
        assert all(len(c["text"]) >= 500 for c in chunks)
        assert all(len(c["pages"]) > 0 for c in chunks)

    def test_index_real_pdf(self, tmp_path):
        db_path = tmp_path / "chroma_db"
        stats = index_directory(SAMPLE_PDF.parent, db_path)

        assert stats["files"] == 1
        assert stats["chunks"] > 1
