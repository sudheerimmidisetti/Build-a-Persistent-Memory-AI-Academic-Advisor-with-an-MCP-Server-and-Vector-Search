import uuid
from sqlalchemy.orm import Session

from ..models import Conversation
from ..memory_schemas import MemoryWriteRequest, MemoryWriteResponse
from .. import vector_store


def execute(req: MemoryWriteRequest, db: Session) -> MemoryWriteResponse:
    """Write a message to both SQLite and ChromaDB."""

    # persist to relational store
    record = Conversation(
        session_id=req.session_id,
        role=req.role,
        content=req.content,
        metadata_=req.metadata,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # persist to vector store
    vec_id = f"{req.session_id}_{record.id}_{uuid.uuid4().hex[:8]}"
    meta = {
        "session_id": req.session_id,
        "role": req.role,
        "conversation_id": record.id,
    }
    if req.metadata:
        # ChromaDB values can only be str, int, float, or bool
        for k, v in req.metadata.items():
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v

    vector_store.add_document(doc_id=vec_id, content=req.content, metadata=meta)

    return MemoryWriteResponse(
        conversation_id=record.id,
        vector_id=vec_id,
    )
