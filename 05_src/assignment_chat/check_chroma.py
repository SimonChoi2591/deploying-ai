import chromadb

client = chromadb.PersistentClient(
    path="knowledge_base/chroma_db"
)

collections = client.list_collections()

for collection in collections:
    print("Collection:", collection.name)
    print("Documents:", collection.count())

    data = collection.get(
        limit=2,
        include=["documents", "embeddings"]
    )

    for i, doc in enumerate(data["documents"]):
        print(f"\nDocument {i+1}:")
        print(doc[:200])
        print("Embedding dimensions:", len(data["embeddings"][i]))