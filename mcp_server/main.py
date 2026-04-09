import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .memory_schemas import (
    MemoryWriteRequest, MemoryWriteResponse,
    MemoryReadRequest, MemoryReadResponse,
    MemoryRetrieveRequest, MemoryRetrieveResponse,
    TOOL_DEFINITIONS,
)
from .tools import memory_write, memory_read, memory_retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    logger.info("MCP server ready.")
    yield


app = FastAPI(
    title="AI Academic Advisor — MCP Server",
    version="1.0.0",
    description="Memory, Control, Process server for the AI Academic Advisor",
    lifespan=lifespan,
)


# ---- Core endpoints ----

@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "mcp-server"}


@app.get("/tools")
def list_tools() -> dict:
    return {"tools": TOOL_DEFINITIONS}


# ---- Memory tools ----

@app.post("/memory/write", response_model=MemoryWriteResponse)
def handle_memory_write(req: MemoryWriteRequest, db: Session = Depends(get_db)):
    try:
        return memory_write.execute(req, db)
    except Exception as e:
        logger.exception("memory_write failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/read", response_model=MemoryReadResponse)
def handle_memory_read(req: MemoryReadRequest, db: Session = Depends(get_db)):
    try:
        return memory_read.execute(req, db)
    except Exception as e:
        logger.exception("memory_read failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/retrieve", response_model=MemoryRetrieveResponse)
def handle_memory_retrieve(req: MemoryRetrieveRequest):
    try:
        return memory_retrieve.execute(req)
    except Exception as e:
        logger.exception("memory_retrieve failed")
        raise HTTPException(status_code=500, detail=str(e))
