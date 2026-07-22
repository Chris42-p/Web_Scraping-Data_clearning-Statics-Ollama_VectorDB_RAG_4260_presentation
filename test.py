import chromadb

client = chromadb.PersistentClient(path="Modules/engine_embedding/data_base/chroma_db")

print(client.list_collections())

c = client.get_collection("documents")

print(c.count())
