"""
RAGロジック（ツール⑥共通）: インデックス作成・検索
"""

import os
import fitz
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./chroma_db"
COLLECTION = "knowledge_base"
CHUNK_SIZE = 500


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def extract_text(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def split_chunks(text: str, source: str) -> list[dict]:
    words = text.split()
    chunks, current, length, idx = [], [], 0, 0
    for word in words:
        current.append(word)
        length += len(word) + 1
        if length >= CHUNK_SIZE:
            chunks.append(
                {"id": f"{source}_{idx}", "text": " ".join(current), "source": source}
            )
            current, length, idx = [], 0, idx + 1
    if current:
        chunks.append(
            {"id": f"{source}_{idx}", "text": " ".join(current), "source": source}
        )
    return chunks


def index_document(filepath: str) -> int:
    col = get_collection()
    source = os.path.basename(filepath)
    existing = col.get(where={"source": source})
    if existing["ids"]:
        col.delete(ids=existing["ids"])
    text = extract_text(filepath)
    chunks = split_chunks(text, source)
    col.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    return len(chunks)


def search(query: str, n_results: int = 4) -> list[dict]:
    col = get_collection()
    results = col.query(query_texts=[query], n_results=n_results)
    return [
        {
            "text": doc,
            "source": results["metadatas"][0][i].get("source", "不明"),
            "score": results["distances"][0][i],
        }
        for i, doc in enumerate(results["documents"][0])
    ]
