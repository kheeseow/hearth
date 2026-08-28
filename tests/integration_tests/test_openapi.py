from fastapi.testclient import TestClient


def test_openapi_returns_json(api_client: TestClient):
    response = api_client.get("openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Hearth"
    assert "Mealie-compatible platform APIs" in response.json()["info"]["description"]
