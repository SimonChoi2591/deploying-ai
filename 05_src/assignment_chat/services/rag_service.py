"""Persistent ChromaDB retrieval and grounded response construction."""
import json
from pathlib import Path

from services.semantic_embedding import encode

DB_DIR = Path(__file__).resolve().parents[1] / "knowledge_base" / "chroma_db"
DOCS_FILE = Path(__file__).resolve().parents[1] / "knowledge_base" / "documents.json"
COLLECTION = "techwise_knowledge_v1"


class KnowledgeBaseError(Exception):
    pass


def get_collection():
    try:
        import chromadb
    except ImportError as exc:
        raise KnowledgeBaseError(
            "ChromaDB is missing from this Python environment. "
            "Check the course environment; do not install packages for grading."
        ) from exc

    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(name=COLLECTION, metadata={"hnsw:space": "cosine"})
    # Initialize persistent collection from packaged data on first use.
    # No embedding API call or separate embedding-generation step is needed.
    if collection.count() == 0:
        records = json.loads(DOCS_FILE.read_text(encoding="utf-8"))
        collection.add(
            ids=[r["id"] for r in records],
            documents=[r["text"] for r in records],
            metadatas=[{"title": r["title"]} for r in records],
            embeddings=[encode(r["title"] + " " + r["text"], r["concepts"]) for r in records],
        )
    return collection


def retrieve(question: str, n_results: int = 3, max_distance: float = 0.72):
    """Return relevant source passages, or [] for out-of-domain queries."""
    vector = encode(question)
    if not any(vector):
        return []
    try:
        collection = get_collection()
        result = collection.query(
            query_embeddings=[vector],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
    except KnowledgeBaseError:
        raise
    except Exception as exc:
        raise KnowledgeBaseError("Persistent knowledge-base query failed") from exc
    hits = []
    for doc, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        if distance <= max_distance:
            hits.append({"title": meta["title"], "text": doc, "distance": round(distance, 3)})
    return hits


def format_context(hits):
    return "\n\n".join(
        f"Source {i}: {hit['title']}\n{hit['text']}"
        for i, hit in enumerate(hits, 1)
    )
