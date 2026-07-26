"""
FastAPI 서버 테스트 — WarshipAgent mock 사용 (API 키 불필요)
"""
import os
import pytest
from unittest.mock import patch, MagicMock

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ["WARSHIPS_CSV"] = str(
    __import__("pathlib").Path(__file__).parent.parent / "data" / "warships.sample.csv"
)


@pytest.fixture
def client():
    with patch("agent.WarshipAgent.__init__", return_value=None):
        with patch("agent.WarshipAgent.chat", return_value="DDH-975는 충무공이순신함입니다."):
            from fastapi.testclient import TestClient
            import importlib
            import server as srv
            importlib.reload(srv)
            yield TestClient(srv.app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_chat_success(client):
    res = client.post("/chat", json={"message": "DDH-975가 뭐야?"})
    assert res.status_code == 200
    assert "reply" in res.json()


def test_chat_empty_message(client):
    res = client.post("/chat", json={"message": "   "})
    assert res.status_code == 422


def test_chat_invalid_history_role(client):
    res = client.post("/chat", json={
        "message": "테스트",
        "history": [{"role": "admin", "content": "해킹"}]
    })
    assert res.status_code == 422
