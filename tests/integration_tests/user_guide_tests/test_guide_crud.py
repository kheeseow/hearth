import json
from pathlib import Path
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from mealie.core.dependencies.dependencies import validate_file_token
from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import EventGuideData, EventOperation, EventTypes
from mealie.services.guide import GuideDataService
from tests import data
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

GUIDES = "/api/guides"


@pytest.fixture
def dispatched_events(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    events: list[dict] = []

    def capture_event(_event_bus: EventBusService, **kwargs) -> None:
        events.append(kwargs)

    monkeypatch.setattr(EventBusService, "dispatch", capture_event)
    return events


def guide_payload(title: str | None = None) -> dict:
    return {
        "title": title or f"Guide {random_string(8)}",
        "description": "A practical description for finding this guide",
        "steps": [{"text": "First step"}, {"text": "Second step"}],
    }


def test_guide_create_dispatches_lifecycle_event(
    api_client: TestClient, unique_user: TestUser, dispatched_events: list[dict]
) -> None:
    response = api_client.post(GUIDES, json=guide_payload("Test the smoke alarm"), headers=unique_user.token)

    assert response.status_code == 201
    assert len(dispatched_events) == 1
    event = dispatched_events[0]
    assert event["event_type"] is EventTypes.guide_created
    assert event["group_id"] == unique_user._group_id
    assert event["household_id"] == unique_user._household_id
    assert event["document_data"] == EventGuideData(
        operation=EventOperation.create,
        guide_slug="test-the-smoke-alarm",
    )
    assert "/g/" in event["message"]
    assert "/guides/test-the-smoke-alarm" in event["message"]


def test_guide_update_dispatches_lifecycle_event(
    api_client: TestClient, unique_user: TestUser, dispatched_events: list[dict]
) -> None:
    guide = api_client.post(GUIDES, json=guide_payload("Test the fuse box"), headers=unique_user.token).json()
    dispatched_events.clear()

    response = api_client.put(
        f"{GUIDES}/{guide['slug']}",
        json=guide_payload("Label the fuse box"),
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert len(dispatched_events) == 1
    event = dispatched_events[0]
    assert event["event_type"] is EventTypes.guide_updated
    assert event["document_data"] == EventGuideData(
        operation=EventOperation.update,
        guide_slug=guide["slug"],
    )


def test_guide_patch_dispatches_lifecycle_event(
    api_client: TestClient, unique_user: TestUser, dispatched_events: list[dict]
) -> None:
    guide = api_client.post(GUIDES, json=guide_payload("Inspect the roof"), headers=unique_user.token).json()
    dispatched_events.clear()

    response = api_client.patch(
        f"{GUIDES}/{guide['slug']}",
        json={"description": "Inspect it safely"},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert len(dispatched_events) == 1
    assert dispatched_events[0]["event_type"] is EventTypes.guide_updated


def test_guide_delete_dispatches_lifecycle_event(
    api_client: TestClient, unique_user: TestUser, dispatched_events: list[dict]
) -> None:
    guide = api_client.post(GUIDES, json=guide_payload("Retire an old appliance"), headers=unique_user.token).json()
    dispatched_events.clear()

    response = api_client.delete(f"{GUIDES}/{guide['slug']}", headers=unique_user.token)

    assert response.status_code == 200
    assert len(dispatched_events) == 1
    event = dispatched_events[0]
    assert event["event_type"] is EventTypes.guide_deleted
    assert event["document_data"] == EventGuideData(
        operation=EventOperation.delete,
        guide_slug=guide["slug"],
    )


def test_guide_media_mutations_dispatch_one_update_after_success(
    api_client: TestClient, unique_user: TestUser, dispatched_events: list[dict]
) -> None:
    guide = api_client.post(GUIDES, json=guide_payload("Document a repair"), headers=unique_user.token).json()
    step_id = guide["steps"][0]["id"]
    dispatched_events.clear()

    invalid = api_client.put(
        f"{GUIDES}/{guide['slug']}/image",
        data={"extension": "txt"},
        files={"image": ("bad.txt", b"not an image", "text/plain")},
        headers=unique_user.token,
    )
    assert invalid.status_code == 400
    assert dispatched_events == []

    cover = api_client.put(
        f"{GUIDES}/{guide['slug']}/image",
        data={"extension": "jpg"},
        files={"image": ("cover.jpg", data.images_test_image_1.read_bytes(), "image/jpeg")},
        headers=unique_user.token,
    )
    assert cover.status_code == 200
    assert len(dispatched_events) == 1
    assert dispatched_events[0]["event_type"] is EventTypes.guide_updated

    dispatched_events.clear()
    step_image = api_client.post(
        f"{GUIDES}/{guide['slug']}/steps/{step_id}/images",
        data={"extension": "png"},
        files={"image": ("step.png", data.images_test_image_2.read_bytes(), "image/png")},
        headers=unique_user.token,
    )
    assert step_image.status_code == 200
    assert len(dispatched_events) == 1
    assert dispatched_events[0]["event_type"] is EventTypes.guide_updated


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


def test_guide_notes_sources_relations_and_review_date(api_client: TestClient, unique_user: TestUser) -> None:
    marker = random_string(12)
    related_create = api_client.post(
        GUIDES,
        json=guide_payload(f"Check the {marker} shut-off valve"),
        headers=unique_user.token,
    )
    assert related_create.status_code == 201
    related = related_create.json()

    payload = guide_payload("Prepare the home for a long trip")
    payload.update(
        {
            "notes": f"Keep the {marker} spare key with the neighbour",
            "lastReviewed": "2025-07-15",
            "sources": [
                {"label": "Manufacturer checklist", "url": "https://example.com/checklist"},
                {"label": "Water safety reference", "url": "https://example.org/water"},
            ],
            "relatedGuideIds": [related["id"]],
        }
    )
    create = api_client.post(GUIDES, json=payload, headers=unique_user.token)
    assert create.status_code == 201
    guide = create.json()
    assert guide["notes"] == payload["notes"]
    assert guide["lastReviewed"] == "2025-07-15"
    assert [source["position"] for source in guide["sources"]] == [0, 1]
    assert [source["label"] for source in guide["sources"]] == [
        "Manufacturer checklist",
        "Water safety reference",
    ]
    assert [item["id"] for item in guide["relatedGuides"]] == [related["id"]]

    for search_term in (marker, "manufacturer checklist", "example.org"):
        response = api_client.get(GUIDES, params={"search": search_term, "perPage": -1}, headers=unique_user.token)
        assert response.status_code == 200
        assert guide["id"] in {item["id"] for item in response.json()["items"]}

    sources = guide["sources"]
    update_payload = {
        **payload,
        "sources": [
            {"id": sources[1]["id"], "label": "Updated water reference", "url": "https://example.org/new"},
            {"id": sources[0]["id"], "label": sources[0]["label"], "url": sources[0]["url"]},
        ],
    }
    update = api_client.put(f"{GUIDES}/{guide['id']}", json=update_payload, headers=unique_user.token)
    assert update.status_code == 200
    assert [source["id"] for source in update.json()["sources"]] == [sources[1]["id"], sources[0]["id"]]
    assert [source["position"] for source in update.json()["sources"]] == [0, 1]

    mutual = api_client.patch(
        f"{GUIDES}/{related['id']}",
        json={"relatedGuideIds": [guide["id"]]},
        headers=unique_user.token,
    )
    assert mutual.status_code == 200

    cleared = api_client.patch(
        f"{GUIDES}/{guide['id']}",
        json={"notes": None, "lastReviewed": None, "sources": [], "relatedGuideIds": []},
        headers=unique_user.token,
    )
    assert cleared.status_code == 200
    assert cleared.json()["notes"] is None
    assert cleared.json()["lastReviewed"] is None
    assert cleared.json()["sources"] == []
    assert cleared.json()["relatedGuides"] == []


def test_guide_sources_and_relations_are_validated(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
) -> None:
    guide_create = api_client.post(GUIDES, json=guide_payload(), headers=unique_user.token)
    other_create = api_client.post(GUIDES, json=guide_payload(), headers=unique_user.token)
    outside_group_create = api_client.post(GUIDES, json=guide_payload(), headers=g2_user.token)
    assert guide_create.status_code == other_create.status_code == outside_group_create.status_code == 201
    guide = guide_create.json()
    other = other_create.json()
    outside_group = outside_group_create.json()

    invalid_url = api_client.post(
        GUIDES,
        json={**guide_payload(), "sources": [{"label": "Unsafe link", "url": "javascript:alert(1)"}]},
        headers=unique_user.token,
    )
    assert invalid_url.status_code == 422

    duplicate = api_client.patch(
        f"{GUIDES}/{guide['id']}",
        json={"relatedGuideIds": [other["id"], other["id"]]},
        headers=unique_user.token,
    )
    assert duplicate.status_code == 400

    self_relation = api_client.patch(
        f"{GUIDES}/{guide['id']}", json={"relatedGuideIds": [guide["id"]]}, headers=unique_user.token
    )
    assert self_relation.status_code == 400

    outside_group_relation = api_client.patch(
        f"{GUIDES}/{guide['id']}",
        json={"relatedGuideIds": [outside_group["id"]]},
        headers=unique_user.token,
    )
    assert outside_group_relation.status_code == 400


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


def test_guide_export_contains_full_document_and_media(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
) -> None:
    related_response = api_client.post(
        GUIDES,
        json=guide_payload("Check the water shut-off valve"),
        headers=unique_user.token,
    )
    assert related_response.status_code == 201
    related = related_response.json()

    payload = guide_payload("Prepare the home for a long trip")
    payload.update(
        {
            "guideType": "maintenance",
            "difficulty": "intermediate",
            "frequency": "as_needed",
            "preparationMinutes": 15,
            "executionMinutes": 45,
            "notes": "Leave a copy with the house sitter.",
            "lastReviewed": "2026-07-15",
            "category": "Travel",
            "tags": ["Home A", "Before leaving"],
            "steps": [{"text": "Turn off the water", "tip": "Photograph the valve position"}],
            "callouts": [{"kind": "warning", "text": "Do not turn off fire suppression water"}],
            "requirements": [{"kind": "tool", "name": "Valve key", "note": "Keep near the meter"}],
            "sources": [{"label": "Utility guidance", "url": "https://example.com/water"}],
            "relatedGuideIds": [related["id"]],
        }
    )
    create = api_client.post(GUIDES, json=payload, headers=unique_user.token)
    assert create.status_code == 201
    guide = create.json()
    step_id = guide["steps"][0]["id"]

    cover = api_client.put(
        f"{GUIDES}/{guide['id']}/image",
        data={"extension": "jpg"},
        files={"image": ("cover.jpg", data.images_test_image_1.read_bytes(), "image/jpeg")},
        headers=unique_user.token,
    )
    assert cover.status_code == 200
    image = api_client.post(
        f"{GUIDES}/{guide['id']}/steps/{step_id}/images",
        data={"extension": "png", "caption": "Valve location", "alt_text": "Blue valve beside the meter"},
        files={"image": ("valve.png", data.images_test_image_2.read_bytes(), "image/png")},
        headers=unique_user.token,
    )
    assert image.status_code == 200
    exported_guide = image.json()
    image_id = exported_guide["steps"][0]["images"][0]["id"]

    denied = api_client.post(
        f"{GUIDES}/export",
        json={"guideIds": [guide["id"]]},
        headers=g2_user.token,
    )
    assert denied.status_code == 404

    duplicate = api_client.post(
        f"{GUIDES}/export",
        json={"guideIds": [guide["id"], guide["id"]]},
        headers=unique_user.token,
    )
    assert duplicate.status_code == 400

    response = api_client.post(
        f"{GUIDES}/export",
        json={"guideIds": [guide["id"], related["id"]]},
        headers=unique_user.token,
    )
    assert response.status_code == 201
    export = response.json()
    assert export["name"] == "Guide Export (2)"

    export_path = Path(export["path"])
    try:
        with ZipFile(export_path) as archive:
            document_path = f"guides/{guide['slug']}/{guide['slug']}.json"
            document = json.loads(archive.read(document_path))
            assert document["title"] == payload["title"]
            assert document["guideType"] == payload["guideType"]
            assert document["notes"] == payload["notes"]
            assert document["lastReviewed"] == payload["lastReviewed"]
            assert document["category"]["name"] == payload["category"]
            assert {tag["name"] for tag in document["tags"]} == set(payload["tags"])
            assert document["steps"][0]["tip"] == payload["steps"][0]["tip"]
            assert document["steps"][0]["images"][0]["caption"] == "Valve location"
            assert document["callouts"][0]["text"] == payload["callouts"][0]["text"]
            assert document["requirements"][0]["note"] == payload["requirements"][0]["note"]
            assert document["sources"][0]["url"] == payload["sources"][0]["url"]
            assert document["relatedGuides"][0]["id"] == related["id"]

            paths = set(archive.namelist())
            assert f"guides/{guide['slug']}/media/cover/original.webp" in paths
            assert f"guides/{guide['slug']}/media/step-images/{image_id}/original.webp" in paths

        token_response = api_client.get(
            f"{GUIDES}/export/{export['id']}/download",
            headers=unique_user.token,
        )
        assert token_response.status_code == 200, token_response.json()
        assert validate_file_token(token_response.json()["fileToken"]) == export_path.resolve()
    finally:
        export_path.unlink(missing_ok=True)
        with session_context() as session:
            repos = get_repositories(session, group_id=unique_user.group_id, household_id=None)
            if repos.group_exports.get_one(export["id"]):
                repos.group_exports.delete(export["id"])
