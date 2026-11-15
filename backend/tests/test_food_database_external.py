from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.domains.food import database_router
from app.main import app


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class _FakeAsyncClient:
    calls = []
    response = _FakeResponse(200, {})

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url, params=None, timeout=None):
        _FakeAsyncClient.calls.append((url, params))
        return _FakeAsyncClient.response


def _client(monkeypatch, response, cached=None):
    _FakeAsyncClient.calls = []
    _FakeAsyncClient.response = response
    monkeypatch.setattr(database_router.httpx, "AsyncClient", _FakeAsyncClient)
    monkeypatch.setattr(database_router, "_search_food_cache", lambda q, limit: list(cached or []))
    monkeypatch.setattr(database_router, "_save_to_food_cache", lambda items, q: None)
    app.dependency_overrides[get_current_user] = lambda: {"id": "user-1"}
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.pop(get_current_user, None)


def test_barcode_lookup_returns_normalized_product(monkeypatch):
    client = _client(monkeypatch, _FakeResponse(200, {
        "status": 1,
        "product": {
            "product_name": "Greek Yogurt",
            "brands": "Fage",
            "serving_size": "170g",
            "nutriments": {"energy-kcal_100g": "97.25", "proteins_100g": 9, "fat_100g": None},
        },
    }))

    res = client.get("/api/food-database/barcode/5201054017371")

    assert res.status_code == 200
    body = res.json()
    assert body["food_name"] == "Greek Yogurt"
    assert body["brand"] == "Fage"
    assert body["nutrition_per_100g"]["calories"] == 97.2
    assert body["nutrition_per_100g"]["protein"] == 9.0
    assert body["nutrition_per_100g"]["fat"] == 0.0
    assert _FakeAsyncClient.calls[0][0].endswith("/api/v2/product/5201054017371.json")


def test_barcode_lookup_unknown_product_is_404(monkeypatch):
    client = _client(monkeypatch, _FakeResponse(200, {"status": 0}))
    assert client.get("/api/food-database/barcode/12345678").status_code == 404


def test_barcode_lookup_rejects_non_numeric_codes(monkeypatch):
    client = _client(monkeypatch, _FakeResponse(200, {"status": 1}))
    assert client.get("/api/food-database/barcode/abc123").status_code == 422
    assert _FakeAsyncClient.calls == []


def test_barcode_lookup_requires_auth():
    app.dependency_overrides.pop(get_current_user, None)
    res = TestClient(app).get("/api/food-database/barcode/12345678")
    assert res.status_code in (401, 403)


def test_search_external_is_not_shadowed_by_food_id_route(monkeypatch):
    client = _client(monkeypatch, _FakeResponse(200, {
        "products": [
            {"code": "111", "product_name": "Oat Milk", "brands": "Oatly", "nutriments": {"energy-kcal_100g": 46}},
            {"code": "222", "product_name": "", "nutriments": {}},
        ],
    }))

    res = client.get("/api/food-database/search-external", params={"q": "oat milk", "limit": 5})

    assert res.status_code == 200
    body = res.json()
    assert body["source"] == "openfoodfacts"
    assert [r["food_name"] for r in body["results"]] == ["Oat Milk (Oatly)"]
    assert body["results"][0]["nutrition_per_100g"]["calories"] == 46.0


def test_search_external_uses_cache_when_enough_hits(monkeypatch):
    cached = [{"id": f"off_{i}", "food_name": f"Food {i}", "nutrition_per_100g": {"calories": 1}} for i in range(3)]
    client = _client(monkeypatch, _FakeResponse(200, {"products": []}), cached=cached)

    res = client.get("/api/food-database/search-external", params={"q": "food"})

    assert res.status_code == 200
    assert res.json()["source"] == "cache"
    assert _FakeAsyncClient.calls == []
