import os
import logging
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "academic_advisor")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
USE_PERSISTENT = os.getenv("CHROMA_PERSISTENT", "true").lower() == "true"


_embedding_fn = None
_client = None

def _get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
    return _embedding_fn

def get_chroma_client():
    global _client
    if _client is None:
        if USE_PERSISTENT:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
            os.makedirs(persist_dir, exist_ok=True)
            _client = chromadb.PersistentClient(path=persist_dir)
        else:
            _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=_get_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


def add_document(doc_id: str, content: str, metadata: dict) -> str:
    """Add a single document to the vector store."""
    collection = get_collection()
    collection.add(
        ids=[doc_id],
        documents=[content],
        metadatas=[metadata],
    )
    return doc_id


def query_similar(query_text: str, top_k: int = 5, where: dict | None = None) -> dict:
    """Query the vector store for semantically similar documents."""
    collection = get_collection()
    
    count = collection.count()
    if count == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    kwargs = {
        "query_texts": [query_text],
        "n_results": min(top_k, count),
        "include": ["documents", "metadatas", "distances"],
    }
    
    if where:
        kwargs["where"] = where

    try:
        return collection.query(**kwargs)
    except Exception as e:
        logger.warning("ChromaDB query failed: %s", e)
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
