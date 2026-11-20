import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root workspace is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from backend.rag.retriever import retriever
from backend.rag.vector_store import vector_store

client = TestClient(app)

def test_health_endpoint():
    """Verify health endpoint returns status, version, and indexed chunks."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["vector_store_ready"] is True
    assert data["total_chunks"] >= 24
    print(f"\n[PASS] Health check verified. Total indexed chunks: {data['total_chunks']}")

def test_wasalt_rega_license_retrieval():
    """Verify accurate retrieval of Wasalt's official REGA license number."""
    query = "ما هو رقم ترخيص الهيئة العامة للعقار لمنصة وصلت؟"
    results = retriever.retrieve(query=query, top_k=2)
    assert len(results) > 0
    top = results[0]
    assert top["domain"] == "wasalt.sa"
    assert "1200016591" in top["text"]
    assert "الهيئة العامة للعقار" in top["text"]
    print(f"\n[PASS] Wasalt REGA license retrieval verified: {top['chunk_id']} (score: {top['score']})")

def test_wasalt_auctions_retrieval():
    """Verify retrieval of Wasalt real estate electronic auctions."""
    query = "كيف تعمل مزادات وصلت العقارية الإلكترونية؟"
    results = retriever.retrieve(query=query, top_k=2)
    assert len(results) > 0
    # Must retrieve auctions document
    found_auction = any("مزادات" in r["text"] for r in results)
    assert found_auction is True
    print(f"\n[PASS] Wasalt auctions retrieval verified.")

def test_darglobal_projects_retrieval():
    """Verify accurate retrieval of DAR Ecosystem projects (Naiza, DAR U, Darlean)."""
    query = "What IT education and sports projects does DAR Group have?"
    results = retriever.retrieve(query=query, top_k=3)
    assert len(results) > 0
    domains = [r["domain"] for r in results]
    assert "darglobal.com" in domains
    combined_text = " ".join([r["text"] for r in results])
    assert ("DAR U" in combined_text or "Naiza" in combined_text)
    print(f"\n[PASS] DarGlobal projects retrieval verified: {[r['chunk_id'] for r in results]}")

def test_darglobal_tns_news_retrieval():
    """Verify retrieval of TNS Plus acquisition from VEON."""
    query = "Did DAR Group acquire TNS Plus telecom operator?"
    results = retriever.retrieve(query=query, top_k=2)
    assert len(results) > 0
    top = results[0]
    assert top["domain"] == "darglobal.com"
    assert "TNS Plus" in top["text"]
    assert "VEON" in top["text"]
    print(f"\n[PASS] Corporate news acquisition retrieval verified: {top['chunk_id']}")

def test_search_api_endpoint():
    """Verify the /api/v1/search API endpoint."""
    response = client.post(
        "/api/v1/search",
        json={"query": "منصة وصلت", "top_k": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] == 3
    assert len(data["results"]) == 3
    assert data["results"][0]["domain"] == "wasalt.sa"
    print(f"\n[PASS] /api/v1/search endpoint verified.")

def test_out_of_scope_query_handling():
    """Verify that queries unrelated to the knowledge base are flagged as ungrounded."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "Who was the Roman emperor in 44 BC?", "top_k": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grounded"] is False
    assert len(data["citations"]) == 0
    assert "not available" in data["answer"].lower() or "غير متوفرة" in data["answer"]
    print(f"\n[PASS] Out-of-scope query guardrail verified. Answer: {data['answer'][:80]}...")

def test_chat_api_endpoint_factual():
    """Verify /api/v1/chat returns structured answer and citations for in-scope query."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "What is Wasalt and who licenses it?", "top_k": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grounded"] is True
    assert len(data["citations"]) > 0
    assert data["citations"][0]["domain"] == "wasalt.sa"
    assert "wasalt.sa" in data["citations"][0]["source_url"]
    print(f"\n[PASS] /api/v1/chat endpoint verified with citation: {data['citations'][0]['chunk_id']}")

if __name__ == "__main__":
    print("--- Running Backend Verification Tests ---")
    test_health_endpoint()
    test_wasalt_rega_license_retrieval()
    test_wasalt_auctions_retrieval()
    test_darglobal_projects_retrieval()
    test_darglobal_tns_news_retrieval()
    test_search_api_endpoint()
    test_out_of_scope_query_handling()
    test_chat_api_endpoint_factual()
    print("\n==========================================")
    print("ALL 8 BACKEND TESTS PASSED SUCCESSFULLY!")
    print("==========================================")
