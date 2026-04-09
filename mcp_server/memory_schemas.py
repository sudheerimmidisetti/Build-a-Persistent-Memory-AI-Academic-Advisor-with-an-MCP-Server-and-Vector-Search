from datetime import datetime
from pydantic import BaseModel, Field


# --- Request schemas ---

class MemoryWriteRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str = Field(..., min_length=1)
    metadata: dict | None = None


class MemoryReadRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    limit: int = Field(default=20, ge=1, le=100)


class MemoryRetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    session_id: str | None = None  # optional filter


# --- Response schemas ---

class ConversationOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MemoryWriteResponse(BaseModel):
    status: str = "ok"
    conversation_id: int
    vector_id: str


class MemoryReadResponse(BaseModel):
    session_id: str
    count: int
    messages: list[ConversationOut]


class VectorMatch(BaseModel):
    content: str
    session_id: str
    role: str
    score: float
    metadata: dict | None = None


class MemoryRetrieveResponse(BaseModel):
    query: str
    results: list[VectorMatch]


# --- User Preferences ---

class UserPreferencesIn(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    major: str | None = None
    year: int | None = Field(default=None, ge=1, le=8)
    interests: list[str] | None = None
    learning_style: str | None = None


class UserPreferencesOut(BaseModel):
    user_id: str
    major: str | None
    year: int | None
    interests: dict | None
    learning_style: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Milestones ---

class MilestoneIn(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    category: str = Field(..., pattern=r"^(course|project|career)$")
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    target_date: datetime | None = None


class MilestoneOut(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    category: str
    progress: float
    target_date: datetime | None
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Tool descriptors (for /tools endpoint) ---

TOOL_DEFINITIONS = [
    {
        "name": "memory_write",
        "description": "Store a conversation message in both SQLite and ChromaDB vector store.",
        "parameters": MemoryWriteRequest.model_json_schema(),
    },
    {
        "name": "memory_read",
        "description": "Read conversation history for a session from SQLite.",
        "parameters": MemoryReadRequest.model_json_schema(),
    },
    {
        "name": "memory_retrieve_by_context",
        "description": "Semantic search over stored conversations using ChromaDB embeddings.",
        "parameters": MemoryRetrieveRequest.model_json_schema(),
    },
]
