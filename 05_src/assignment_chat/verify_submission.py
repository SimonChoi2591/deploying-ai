"""Local pre-submission checks; does not call the OpenAI API."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    errors = []
    required = ["app.py", "config.py", "prompts.py", "memory.py",
                "guardrails.py", "services/book_service.py",
                "services/rag_service.py", "services/calculator_service.py",
                "knowledge_base/documents.json", "README.md"]
    for item in required:
        if not (ROOT / item).is_file():
            errors.append(f"Missing file: {item}")
    docs_file = ROOT / "knowledge_base" / "documents.json"
    docs = []
    if docs_file.is_file():
        try:
            docs = json.loads(docs_file.read_text(encoding="utf-8"))
            print(f"Knowledge base source documents: {len(docs)}")
            if not docs or len({d['id'] for d in docs}) != len(docs):
                errors.append("Knowledge-base records empty or IDs not unique")
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"Invalid knowledge base: {exc}")
    db_dir = ROOT / "knowledge_base" / "chroma_db"
    if not db_dir.is_dir() or not any(db_dir.iterdir()):
        errors.append("Persistent ChromaDB directory is missing or empty. "
                      "Run a knowledge-base query in your local app first, "
                      "then include that directory in Git.")
    else:
        size = sum(p.stat().st_size for p in db_dir.rglob('*') if p.is_file())
        print(f"ChromaDB directory: {db_dir} ({size:,} bytes)")
        try:
            import chromadb
            from services.rag_service import COLLECTION
            client = chromadb.PersistentClient(path=str(db_dir))
            collection = client.get_collection(COLLECTION)
            count = collection.count()
            print(f"ChromaDB collection: {COLLECTION}; records: {count}")
            if docs and count != len(docs):
                errors.append(f"Expected {len(docs)} stored records; found {count}")
        except ImportError:
            errors.append("ChromaDB package unavailable: cannot verify persistence")
        except Exception as exc:
            errors.append(f"Cannot open persistent collection: {exc}")
    total = sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    print(f"Total project file size: {total / (1024 * 1024):.2f} MiB")
    if total > 40 * 1024 * 1024:
        errors.append("Project files exceed 40 MiB; inspect generated assets")
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: Local submission checks passed (live API testing still required).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
