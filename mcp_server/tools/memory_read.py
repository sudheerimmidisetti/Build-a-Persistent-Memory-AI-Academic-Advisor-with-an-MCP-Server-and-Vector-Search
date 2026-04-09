from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import Conversation
from ..memory_schemas import MemoryReadRequest, MemoryReadResponse, ConversationOut


def execute(req: MemoryReadRequest, db: Session) -> MemoryReadResponse:
    """Read conversation history for a given session."""

    stmt = (
        select(Conversation)
        .where(Conversation.session_id == req.session_id)
        .order_by(Conversation.created_at.desc())
        .limit(req.limit)
    )
    rows = db.execute(stmt).scalars().all()

    messages = [
        ConversationOut(
            id=r.id,
            session_id=r.session_id,
            role=r.role,
            content=r.content,
            metadata=r.metadata_,
            created_at=r.created_at,
        )
        for r in reversed(rows)  # chronological order
    ]

    return MemoryReadResponse(
        session_id=req.session_id,
        count=len(messages),
        messages=messages,
    )
