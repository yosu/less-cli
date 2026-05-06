from pathlib import Path

import chromadb
import spacy
from pypdf import PdfReader


def find_pdfs(directory):
    return sorted(Path(directory).rglob("*.pdf"))


def extract_pages(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and text.strip():
            pages.append({"page": i, "text": text.strip()})
    return pages


MIN_CHUNK_SIZE = 500


def chunk_text(pages, min_chunk_size=MIN_CHUNK_SIZE):
    if not pages:
        return []

    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    sentences = []
    for page in pages:
        doc = nlp(page["text"])
        for sent in doc.sents:
            text = sent.text.strip()
            if text:
                sentences.append({"text": text, "page": page["page"]})

    chunks = []
    current_texts = []
    current_pages = set()
    current_len = 0

    for sentence in sentences:
        current_texts.append(sentence["text"])
        current_pages.add(sentence["page"])
        current_len += len(sentence["text"])
        if current_len >= min_chunk_size:
            chunks.append({
                "text": " ".join(current_texts),
                "pages": sorted(current_pages),
            })
            current_texts = []
            current_pages = set()
            current_len = 0

    if current_texts:
        if chunks:
            chunks[-1]["text"] += " " + " ".join(current_texts)
            chunks[-1]["pages"] = sorted(set(chunks[-1]["pages"]) | current_pages)
        else:
            chunks.append({
                "text": " ".join(current_texts),
                "pages": sorted(current_pages),
            })

    return chunks


def store_chunks(chunks, pdf_path, collection):
    if not chunks:
        return
    documents = [c["text"] for c in chunks]
    ids = [f"{pdf_path.stem}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": str(pdf_path),
            "chunk_index": i,
            "pages": ",".join(str(p) for p in c["pages"]),
        }
        for i, c in enumerate(chunks)
    ]
    batch_size = 5000
    for start in range(0, len(documents), batch_size):
        end = start + batch_size
        collection.add(
            documents=documents[start:end],
            ids=ids[start:end],
            metadatas=metadatas[start:end],
        )


def create_collection(db_path):
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(name="documents")


def index_directory(directory, db_path):
    pdfs = find_pdfs(directory)
    if not pdfs:
        return {"files": 0, "chunks": 0}

    collection = create_collection(db_path)

    total_chunks = 0
    for pdf_path in pdfs:
        pages = extract_pages(pdf_path)
        if not pages:
            continue
        chunks = chunk_text(pages)
        store_chunks(chunks, pdf_path, collection)
        total_chunks += len(chunks)

    return {"files": len(pdfs), "chunks": total_chunks}
