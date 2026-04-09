from ..memory_schemas import MemoryRetrieveRequest, MemoryRetrieveResponse, VectorMatch
from .. import vector_store


def execute(req: MemoryRetrieveRequest) -> MemoryRetrieveResponse:
    """Semantic search over stored conversations using embeddings."""

    where_filter = None
    if req.session_id:
        where_filter = {"session_id": req.session_id}

    results = vector_store.query_similar(
        query_text=req.query,
        top_k=req.top_k,
        where=where_filter,
    )

    matches = []
    ids = results.get("ids") or [[]]
    docs = results.get("documents") or [[]]
    metas = results.get("metadatas") or [[]]
    dists = results.get("distances") or [[]]
    
    ids_list = ids[0] if ids else []
    docs_list = docs[0] if docs else []
    metas_list = metas[0] if metas else []
    dists_list = dists[0] if dists else []

    for i, doc_id in enumerate(ids_list):
        meta = metas_list[i] if i < len(metas_list) and metas_list[i] is not None else {}
        doc = docs_list[i] if i < len(docs_list) and docs_list[i] is not None else ""
        
        # chromadb cosine distance -> similarity score
        score = round(1.0 - dists_list[i], 4) if i < len(dists_list) else 0.0

        matches.append(
            VectorMatch(
                content=doc,
                session_id=meta.get("session_id", ""),
                role=meta.get("role", ""),
                score=score,
                metadata=meta,
            )
        )

    return MemoryRetrieveResponse(query=req.query, results=matches)
