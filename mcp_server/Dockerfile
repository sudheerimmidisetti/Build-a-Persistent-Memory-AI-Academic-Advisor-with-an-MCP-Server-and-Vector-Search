FROM python:3.11-slim

WORKDIR /app

# system deps for chromadb / sentence-transformers
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source into a proper package directory
COPY . ./mcp_server/

# pre-download embedding model at build time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8080

CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8080"]
