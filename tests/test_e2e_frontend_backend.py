import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app

client = TestClient(app)

def test_frontend_static_serving():
    print("\n--- Testing Frontend Static Files Serving ---")
    resp = client.get("/")
    assert resp.status_code == 200, f"Expected 200 for root HTML, got {resp.status_code}"
    assert "DarGlobal × Wasalt AI Assistant" in resp.text
    print("[PASS] Root '/' serves React SPA index.html successfully.")
    
    # Check JS bundle
    assets_dir = BASE_DIR / "backend" / "static" / "assets"
    js_files = list(assets_dir.glob("*.js"))
    assert len(js_files) > 0, "No JS bundle found in backend/static/assets"
    js_route = f"/assets/{js_files[0].name}"
    resp_js = client.get(js_route)
    assert resp_js.status_code == 200
    assert len(resp_js.content) > 50000
    print(f"[PASS] Static asset {js_route} served successfully ({len(resp_js.content):,} bytes).")

def test_api_health_endpoint():
    print("\n--- Testing /api/v1/health ---")
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["vector_store_ready"] is True
    assert data["total_chunks"] >= 24
    print(f"[PASS] Health check returns status={data['status']}, total_chunks={data['total_chunks']}")

def test_arabic_chat_integration():
    print("\n--- Testing Arabic Chat (RTL) Integration ---")
    resp = client.post("/api/v1/chat", json={
        "message": "ما هي منصة وصلت؟",
        "top_k": 3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["grounded"] is True
    assert len(data["citations"]) > 0
    assert data["citations"][0]["domain"] == "wasalt.sa"
    assert "وصلت" in data["answer"]
    print(f"[PASS] Arabic chat response verified with citation: {data['citations'][0]['chunk_id']}")

def test_english_chat_integration():
    print("\n--- Testing English Chat (LTR) Integration ---")
    resp = client.post("/api/v1/chat", json={
        "message": "What is DAR Global and who founded it?",
        "top_k": 3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["grounded"] is True
    assert len(data["citations"]) > 0
    assert data["citations"][0]["domain"] == "darglobal.com"
    assert ("DAR" in data["answer"] or "Утемуратов" in data["answer"] or "Utemuratov" in data["answer"])
    print(f"[PASS] English chat response verified with citation: {data['citations'][0]['chunk_id']}")

def test_out_of_scope_rejection():
    print("\n--- Testing Out-of-Scope Query Rejection ---")
    resp = client.post("/api/v1/chat", json={
        "message": "What is the capital of Mars?",
        "top_k": 3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["grounded"] is False
    assert len(data["citations"]) == 0
    print("[PASS] Out-of-scope query correctly rejected without hallucination.")

if __name__ == "__main__":
    print("==================================================")
    print("STARTING FULL END-TO-END FRONTEND + BACKEND TESTS")
    print("==================================================")
    test_frontend_static_serving()
    test_api_health_endpoint()
    test_arabic_chat_integration()
    test_english_chat_integration()
    test_out_of_scope_rejection()
    print("\n==================================================")
    print("ALL END-TO-END TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")
