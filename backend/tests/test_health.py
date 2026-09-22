"""健康检查测试。"""


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["app"]


def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


def test_llm_health_no_keys(client):
    """未配置 Key 时可用 Provider 列表应为空（测试环境无 .env）。"""
    resp = client.get("/api/v1/health/llm")
    assert resp.status_code == 200
    assert resp.json()["available_providers"] == []
