from fastapi.testclient import TestClient

from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

GUIDES = "/api/guides"


def guide_payload(title: str | None = None) -> dict:
    return {
        "title": title or f"Guide {random_string(8)}",
        "description": "A practical description for finding this guide",
        "steps": [{"text": "First step"}, {"text": "Second step"}],
    }


def test_guide_crud_preserves_step_order_and_slug(api_client: TestClient, unique_user: TestUser) -> None:
    create = api_client.post(GUIDES, json=guide_payload("Set up the coffee maker"), headers=unique_user.token)
    assert create.status_code == 201
    guide = create.json()
    assert guide["slug"] == "set-up-the-coffee-maker"
    assert [step["position"] for step in guide["steps"]] == [0, 1]

    read = api_client.get(f"{GUIDES}/{guide['id']}", headers=unique_user.token)
    assert read.status_code == 200
    assert [step["text"] for step in read.json()["steps"]] == ["First step", "Second step"]

    update_payload = {
        "title": "Use the coffee maker",
        "description": "Updated description",
        "steps": [
            {"id": guide["steps"][1]["id"], "text": "Second step, updated"},
            {"text": "A new final step"},
        ],
    }
    update = api_client.put(f"{GUIDES}/{guide['slug']}", json=update_payload, headers=unique_user.token)
    assert update.status_code == 200
    updated = update.json()
    assert updated["slug"] == guide["slug"]
    assert [step["position"] for step in updated["steps"]] == [0, 1]
    assert [step["text"] for step in updated["steps"]] == ["Second step, updated", "A new final step"]
    assert updated["steps"][0]["id"] == guide["steps"][1]["id"]

    patch = api_client.patch(
        f"{GUIDES}/{guide['id']}", json={"description": "Patched description"}, headers=unique_user.token
    )
    assert patch.status_code == 200
    assert patch.json()["description"] == "Patched description"
    assert patch.json()["slug"] == guide["slug"]

    delete = api_client.delete(f"{GUIDES}/{guide['id']}", headers=unique_user.token)
    assert delete.status_code == 200
    assert api_client.get(f"{GUIDES}/{guide['slug']}", headers=unique_user.token).status_code == 404


def test_guide_searches_title_and_description(api_client: TestClient, unique_user: TestUser) -> None:
    marker = random_string(12)
    title_create = api_client.post(GUIDES, json=guide_payload(f"Replace {marker} filter"), headers=unique_user.token)
    description_payload = guide_payload()
    description_payload["description"] = f"This text contains {marker} in its description"
    description_create = api_client.post(GUIDES, json=description_payload, headers=unique_user.token)
    assert title_create.status_code == description_create.status_code == 201

    response = api_client.get(GUIDES, params={"search": marker, "perPage": -1}, headers=unique_user.token)
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert title_create.json()["id"] in ids
    assert description_create.json()["id"] in ids


def test_guides_are_group_readable_but_household_owned(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
) -> None:
    create = api_client.post(GUIDES, json=guide_payload(), headers=h2_user.token)
    assert create.status_code == 201
    guide = create.json()

    assert api_client.get(f"{GUIDES}/{guide['slug']}", headers=unique_user.token).status_code == 200
    listing = api_client.get(GUIDES, params={"perPage": -1}, headers=unique_user.token)
    assert guide["id"] in {item["id"] for item in listing.json()["items"]}

    payload = guide_payload("Attempted edit")
    assert api_client.put(f"{GUIDES}/{guide['slug']}", json=payload, headers=unique_user.token).status_code == 403
    assert api_client.delete(f"{GUIDES}/{guide['slug']}", headers=unique_user.token).status_code == 403


def test_guide_requires_authentication(api_client: TestClient) -> None:
    assert api_client.get(GUIDES).status_code == 401
