from pathlib import Path

import chromadb


def search(query, db_path, n_results=5):
    db_path = Path(db_path)
    if not db_path.exists():
        return []

    client = chromadb.PersistentClient(path=str(db_path))
    collection_names = [c.name for c in client.list_collections()]
    if "documents" not in collection_names:
        return []

    collection = client.get_collection(name="documents")
    if collection.count() == 0:
        return []

    results = collection.query(query_texts=[query], n_results=n_results)

    return [
        {
            "document": doc,
            "source": meta["source"],
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]
