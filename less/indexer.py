from pathlib import Path

import chromadb
import spacy
from pypdf import PdfReader


def find_pdfs(directory):
    return sorted(Path(directory).rglob("*.pdf"))


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.strip()


def chunk_text(text):
    if not text:
        return []
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def store_chunks(chunks, pdf_path, collection):
    if not chunks:
        return
    ids = [f"{pdf_path.stem}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": str(pdf_path), "chunk_index": i} for i in range(len(chunks))]
    batch_size = 5000
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.add(
            documents=chunks[start:end],
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
        text = extract_text(pdf_path)
        if not text:
            continue
        chunks = chunk_text(text)
        store_chunks(chunks, pdf_path, collection)
        total_chunks += len(chunks)

    return {"files": len(pdfs), "chunks": total_chunks}
