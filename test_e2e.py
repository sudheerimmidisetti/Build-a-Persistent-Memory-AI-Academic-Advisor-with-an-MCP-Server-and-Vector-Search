import time
from fastapi.testclient import TestClient
from mcp_server.main import app

client = TestClient(app)

def run_tests():
    print("--- Starting End-to-End Tests ---")

    # 1. Test Health Endpoint
    print("\nTesting GET /health...")
    t0 = time.time()
    response = client.get("/health")
    dur = time.time() - t0
    assert response.status_code == 200, f"Health check failed: {response.text}"
    print(f"✅ /health passed in {dur:.4f}s. Response: {response.json()}")

    # 2. Test Tools Endpoint
    print("\nTesting GET /tools...")
    t0 = time.time()
    response = client.get("/tools")
    dur = time.time() - t0
    assert response.status_code == 200, f"Tools check failed: {response.text}"
    tools = response.json().get("tools", [])
    assert len(tools) >= 3, "Missing tools definition"
    print(f"✅ /tools passed in {dur:.4f}s. Recognized {len(tools)} tools.")

    # 3. Test Memory Write
    print("\nTesting POST /memory/write...")
    payload_user = {
        "session_id": "test_session_99",
        "role": "user",
        "content": "I am thinking about switching my major to Data Science. What are the math prerequisites?",
        "metadata": {"user_mood": "curious"}
    }
    t0 = time.time()
    response = client.post("/memory/write", json=payload_user)
    dur = time.time() - t0
    assert response.status_code == 200, f"Write check failed: {response.text}"
    print(f"✅ /memory/write (User) passed in {dur:.4f}s. (Embeddings might take time to initialize on first run). Response: {response.json()}")

    payload_assistant = {
        "session_id": "test_session_99",
        "role": "assistant",
        "content": "To switch to Data Science, you'll generally need Calculus I and II, Linear Algebra, and introductory Statistics.",
        "metadata": {"confidence": 0.98}
    }
    response = client.post("/memory/write", json=payload_assistant)
    assert response.status_code == 200, f"Write check failed: {response.text}"
    print(f"✅ /memory/write (Assistant) passed.")

    # 4. Test Memory Read
    print("\nTesting POST /memory/read...")
    payload_read = {
        "session_id": "test_session_99",
        "limit": 10
    }
    t0 = time.time()
    response = client.post("/memory/read", json=payload_read)
    dur = time.time() - t0
    assert response.status_code == 200, f"Read check failed: {response.text}"
    msgs = response.json().get("messages", [])
    assert len(msgs) >= 2, "Should have retrieved at least 2 messages."
    print(f"✅ /memory/read passed in {dur:.4f}s. Retrieved {len(msgs)} messages.")

    # 5. Test Memory Retrieve (Semantic Search)
    print("\nTesting POST /memory/retrieve...")
    payload_search = {
        "query": "What math classes do I need?",
        "top_k": 2
    }
    t0 = time.time()
    response = client.post("/memory/retrieve", json=payload_search)
    dur = time.time() - t0
    assert response.status_code == 200, f"Retrieve check failed: {response.text}"
    results = response.json().get("results", [])
    assert len(results) > 0, "No semantic matches found."
    print(f"✅ /memory/retrieve passed in {dur:.4f}s. Found {len(results)} matches.")
    
    for idx, r in enumerate(results):
        score = r.get('score', 0)
        content = r.get('content', '')[:50]
        print(f"   Match {idx+1}: Score={score} - '{content}...'")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The MCP architecture is functioning perfectly.")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        import traceback
        print("\n❌ UNEXPECTED ERROR:")
        traceback.print_exc()
