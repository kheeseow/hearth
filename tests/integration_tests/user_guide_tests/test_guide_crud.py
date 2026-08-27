from fastapi.testclient import TestClient

from mealie.services.guide import GuideDataService
from tests import data
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


def test_guide_classification_safety_search_and_filters(api_client: TestClient, unique_user: TestUser) -> None:
    payload = guide_payload("Clean the washing machine")
    payload.update(
        {
            "guideType": "cleaning",
            "difficulty": "beginner",
            "preparationMinutes": 10,
            "executionMinutes": 30,
            "category": "Laundry",
            "tags": ["Appliances", "Monthly"],
            "steps": [{"text": "Remove the detergent drawer"}, {"text": "Run a hot drum cycle"}],
            "callouts": [
                {"kind": "warning", "text": "Unplug before cleaning the filter"},
                {"kind": "avoid", "text": "Never mix bleach with vinegar"},
            ],
        }
    )
    create = api_client.post(GUIDES, json=payload, headers=unique_user.token)
    assert create.status_code == 201
    guide = create.json()
    assert guide["guideType"] == "cleaning"
    assert guide["difficulty"] == "beginner"
    assert guide["preparationMinutes"] == 10
    assert guide["executionMinutes"] == 30
    assert guide["category"]["name"] == "Laundry"
    assert {tag["name"] for tag in guide["tags"]} == {"Appliances", "Monthly"}
    assert [callout["kind"] for callout in guide["callouts"]] == ["warning", "avoid"]

    for search_term in ("detergent drawer", "bleach", "appliances", "laundry"):
        response = api_client.get(GUIDES, params={"search": search_term, "perPage": -1}, headers=unique_user.token)
        assert guide["id"] in {item["id"] for item in response.json()["items"]}

    for filters in (
        {"guideType": "cleaning"},
        {"difficulty": "beginner"},
        {"category": "laundry"},
        {"tag": "monthly"},
    ):
        response = api_client.get(GUIDES, params={**filters, "perPage": -1}, headers=unique_user.token)
        assert response.status_code == 200
        assert guide["id"] in {item["id"] for item in response.json()["items"]}

    updated_payload = {**payload, "category": "Appliance care", "tags": ["Monthly", "monthly"]}
    updated_payload["callouts"] = [
        {"id": guide["callouts"][1]["id"], "kind": "avoid", "text": "Do not combine cleaning chemicals"}
    ]
    update = api_client.put(f"{GUIDES}/{guide['id']}", json=updated_payload, headers=unique_user.token)
    assert update.status_code == 200
    updated = update.json()
    assert updated["category"]["name"] == "Appliance care"
    assert [tag["name"] for tag in updated["tags"]] == ["Monthly"]
    assert updated["callouts"][0]["id"] == guide["callouts"][1]["id"]

    cleared = api_client.patch(
        f"{GUIDES}/{guide['id']}",
        json={"category": None, "difficulty": None, "preparationMinutes": None},
        headers=unique_user.token,
    )
    assert cleared.status_code == 200
    assert cleared.json()["category"] is None
    assert cleared.json()["difficulty"] is None
    assert cleared.json()["preparationMinutes"] is None


def test_guide_frequency_requirements_and_step_tips(api_client: TestClient, unique_user: TestUser) -> None:
    payload = guide_payload("Replace an air-conditioner filter")
    payload.update(
        {
            "frequency": "monthly",
            "requirements": [
                {"kind": "tool", "name": "Phillips screwdriver", "note": "A short handle works best"},
                {"kind": "material", "name": "Lint-free cloth", "note": "Use a clean, dry cloth"},
            ],
            "steps": [
                {"text": "Turn off the air conditioner", "tip": "Use the isolator switch if fitted"},
                {"text": "Remove and replace the filter", "tip": None},
            ],
        }
    )
    create = api_client.post(GUIDES, json=payload, headers=unique_user.token)
    assert create.status_code == 201
    guide = create.json()
    assert guide["frequency"] == "monthly"
    assert [item["position"] for item in guide["requirements"]] == [0, 1]
    assert [item["kind"] for item in guide["requirements"]] == ["tool", "material"]
    assert guide["steps"][0]["tip"] == "Use the isolator switch if fitted"

    for search_term in ("screwdriver", "dry cloth", "isolator switch"):
        response = api_client.get(GUIDES, params={"search": search_term, "perPage": -1}, headers=unique_user.token)
        assert response.status_code == 200
        assert guide["id"] in {item["id"] for item in response.json()["items"]}

    filtered = api_client.get(GUIDES, params={"frequency": "monthly", "perPage": -1}, headers=unique_user.token)
    assert filtered.status_code == 200
    assert guide["id"] in {item["id"] for item in filtered.json()["items"]}

    updated_payload = {
        **payload,
        "requirements": [
            {
                "id": guide["requirements"][1]["id"],
                "kind": "material",
                "name": "Microfibre cloth",
                "note": "Use it dry",
            },
            {"kind": "tool", "name": "Step ladder", "note": None},
        ],
        "steps": [
            {
                "id": guide["steps"][0]["id"],
                "text": "Switch off the air conditioner",
                "tip": "Confirm the power light is off",
            }
        ],
    }
    update = api_client.put(f"{GUIDES}/{guide['id']}", json=updated_payload, headers=unique_user.token)
    assert update.status_code == 200
    updated = update.json()
    assert [item["position"] for item in updated["requirements"]] == [0, 1]
    assert updated["requirements"][0]["id"] == guide["requirements"][1]["id"]
    assert updated["requirements"][0]["name"] == "Microfibre cloth"
    assert updated["steps"][0]["id"] == guide["steps"][0]["id"]
    assert updated["steps"][0]["tip"] == "Confirm the power light is off"

    cleared = api_client.patch(
        f"{GUIDES}/{guide['id']}",
        json={"frequency": None, "requirements": []},
        headers=unique_user.token,
    )
    assert cleared.status_code == 200
    assert cleared.json()["frequency"] is None
    assert cleared.json()["requirements"] == []


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


def test_guide_cover_and_ordered_step_images(api_client: TestClient, unique_user: TestUser) -> None:
    create = api_client.post(GUIDES, json=guide_payload("Photograph a maintenance task"), headers=unique_user.token)
    assert create.status_code == 201
    guide = create.json()
    step_id = guide["steps"][0]["id"]
    guide_data = GuideDataService(guide["id"])

    cover = api_client.put(
        f"{GUIDES}/{guide['slug']}/image",
        data={"extension": "jpg"},
        files={"image": ("cover.jpg", data.images_test_image_1.read_bytes(), "image/jpeg")},
        headers=unique_user.token,
    )
    assert cover.status_code == 200
    assert cover.json()["coverImageVersion"]
    assert guide_data.cover_image_path().exists()
    assert api_client.get(f"{GUIDES}/{guide['slug']}/image/tiny", headers=unique_user.token).status_code == 200
    assert api_client.get(f"{GUIDES}/{guide['slug']}/image/tiny").status_code == 401

    first = api_client.post(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images",
        data={"extension": "jpg", "caption": "Before cleaning", "alt_text": "Dust on the filter"},
        files={"image": ("before.jpg", data.images_test_image_1.read_bytes(), "image/jpeg")},
        headers=unique_user.token,
    )
    assert first.status_code == 200
    first_image = first.json()["steps"][0]["images"][0]
    assert first_image["caption"] == "Before cleaning"
    assert first_image["altText"] == "Dust on the filter"
    assert guide_data.step_image_path(first_image["id"]).exists()

    second = api_client.post(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images",
        data={"extension": "png", "caption": "After cleaning", "alt_text": "Clean filter"},
        files={"image": ("after.png", data.images_test_image_2.read_bytes(), "image/png")},
        headers=unique_user.token,
    )
    assert second.status_code == 200
    images = second.json()["steps"][0]["images"]
    second_image = images[1]
    assert [item["position"] for item in images] == [0, 1]

    reordered = api_client.put(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images/order",
        json={"imageIds": [second_image["id"], first_image["id"]]},
        headers=unique_user.token,
    )
    assert reordered.status_code == 200
    assert [item["id"] for item in reordered.json()["steps"][0]["images"]] == [
        second_image["id"],
        first_image["id"],
    ]

    updated = api_client.patch(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images/{first_image['id']}",
        json={"caption": "Updated caption", "altText": "Updated alternative text"},
        headers=unique_user.token,
    )
    assert updated.status_code == 200
    assert updated.json()["steps"][0]["images"][1]["caption"] == "Updated caption"

    replaced = api_client.put(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images/{first_image['id']}/file",
        data={"extension": "png"},
        files={"image": ("replacement.png", data.images_test_image_2.read_bytes(), "image/png")},
        headers=unique_user.token,
    )
    assert replaced.status_code == 200
    replaced_image = next(item for item in replaced.json()["steps"][0]["images"] if item["id"] == first_image["id"])
    assert replaced_image["version"] != first_image["version"]

    media = api_client.get(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images/{first_image['id']}/small",
        headers=unique_user.token,
    )
    assert media.status_code == 200
    assert media.headers["content-type"] == "image/webp"

    deleted_image = api_client.delete(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images/{first_image['id']}", headers=unique_user.token
    )
    assert deleted_image.status_code == 200
    assert not guide_data.step_image_dir(first_image["id"]).exists()

    removed_step = api_client.put(
        f"{GUIDES}/{guide['slug']}",
        json={
            "title": guide["title"],
            "description": guide["description"],
            "steps": [{"id": guide["steps"][1]["id"], "text": guide["steps"][1]["text"]}],
        },
        headers=unique_user.token,
    )
    assert removed_step.status_code == 200
    assert not guide_data.step_image_dir(second_image["id"]).exists()

    deleted_guide = api_client.delete(f"{GUIDES}/{guide['slug']}", headers=unique_user.token)
    assert deleted_guide.status_code == 200
    assert not guide_data.guide_dir.exists()


def test_guide_media_rejects_invalid_images_and_non_owner_changes(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
) -> None:
    create = api_client.post(GUIDES, json=guide_payload(), headers=h2_user.token)
    assert create.status_code == 201
    guide = create.json()

    invalid = api_client.put(
        f"{GUIDES}/{guide['slug']}/image",
        data={"extension": "txt"},
        files={"image": ("bad.txt", b"not an image", "text/plain")},
        headers=h2_user.token,
    )
    assert invalid.status_code == 400

    forbidden = api_client.put(
        f"{GUIDES}/{guide['slug']}/image",
        data={"extension": "jpg"},
        files={"image": ("cover.jpg", data.images_test_image_1.read_bytes(), "image/jpeg")},
        headers=unique_user.token,
    )
    assert forbidden.status_code == 403
