"""Protect the authenticated Guide API contract consumed by Hermes."""

from fastapi.testclient import TestClient

GUIDE_OPERATIONS = (
    ("/api/guides", "get"),
    ("/api/guides", "post"),
    ("/api/guides/{slug_or_id}", "get"),
    ("/api/guides/{slug_or_id}", "patch"),
    ("/api/guides/{slug_or_id}", "delete"),
    ("/api/guides/{slug_or_id}/image", "put"),
    ("/api/guides/{slug_or_id}/steps/{step_id}/images", "post"),
)

GUIDE_CREATE_FIELDS = {
    "title",
    "description",
    "guideType",
    "difficulty",
    "frequency",
    "preparationMinutes",
    "executionMinutes",
    "notes",
    "lastReviewed",
    "category",
    "tags",
    "steps",
    "callouts",
    "requirements",
    "sources",
    "relatedGuideIds",
}

GUIDE_SUMMARY_FIELDS = {
    "id",
    "groupId",
    "householdId",
    "authorId",
    "slug",
    "title",
    "description",
    "guideType",
    "difficulty",
    "frequency",
    "preparationMinutes",
    "executionMinutes",
    "lastReviewed",
    "coverImageVersion",
    "category",
    "tags",
    "createdAt",
    "updatedAt",
}

GUIDE_READ_FIELDS = GUIDE_SUMMARY_FIELDS | {
    "notes",
    "steps",
    "callouts",
    "requirements",
    "sources",
    "relatedGuides",
}

LIST_QUERY_FIELDS = {
    "search",
    "guideType",
    "difficulty",
    "frequency",
    "category",
    "tag",
    "page",
    "perPage",
    "orderBy",
    "orderDirection",
    "orderByNullPosition",
    "paginationSeed",
}


def _request_schema(operation: dict, content_type: str) -> dict:
    request_body = operation["requestBody"]["content"][content_type]["schema"]
    reference = request_body["$ref"]
    return {"$ref": reference}


def _response_schema(operation: dict, status_code: str) -> dict:
    response = operation["responses"][status_code]["content"]["application/json"]["schema"]
    reference = response["$ref"]
    return {"$ref": reference}


def test_hermes_guide_openapi_contract(api_client: TestClient) -> None:
    """Keep Hermes's authenticated Guide routes, aliases, and multipart fields stable."""
    response = api_client.get("/openapi.json")

    assert response.status_code == 200
    document = response.json()
    paths = document["paths"]

    for path, method in GUIDE_OPERATIONS:
        assert paths[path][method]["security"] == [{"OAuth2PasswordBearer": []}]

    list_operation = paths["/api/guides"]["get"]
    assert LIST_QUERY_FIELDS.issubset({parameter["name"] for parameter in list_operation["parameters"]})
    assert _request_schema(paths["/api/guides"]["post"], "application/json") == {
        "$ref": "#/components/schemas/GuideCreate"
    }
    assert _request_schema(paths["/api/guides/{slug_or_id}"]["patch"], "application/json") == {
        "$ref": "#/components/schemas/GuidePatch"
    }

    schemas = document["components"]["schemas"]
    assert set(schemas["GuideCreate"]["properties"]) == GUIDE_CREATE_FIELDS
    assert set(schemas["GuidePatch"]["properties"]) == GUIDE_CREATE_FIELDS

    assert _response_schema(list_operation, "200") == {"$ref": "#/components/schemas/GuidePagination"}
    for path, method, status_code in (
        ("/api/guides", "post", "201"),
        ("/api/guides/{slug_or_id}", "get", "200"),
        ("/api/guides/{slug_or_id}", "patch", "200"),
        ("/api/guides/{slug_or_id}", "delete", "200"),
        ("/api/guides/{slug_or_id}/image", "put", "200"),
        ("/api/guides/{slug_or_id}/steps/{step_id}/images", "post", "200"),
    ):
        assert _response_schema(paths[path][method], status_code) == {"$ref": "#/components/schemas/GuideRead"}

    pagination_items = schemas["GuidePagination"]["properties"]["items"]["items"]
    assert pagination_items == {"$ref": "#/components/schemas/GuideSummary"}
    assert set(schemas["GuideSummary"]["properties"]) == GUIDE_SUMMARY_FIELDS
    assert set(schemas["GuideRead"]["properties"]) == GUIDE_READ_FIELDS
    assert {"id", "slug"}.issubset(schemas["GuideRead"]["required"])
    assert {"id", "position"}.issubset(schemas["GuideStepOut"]["required"])

    cover_schema = _request_schema(paths["/api/guides/{slug_or_id}/image"]["put"], "multipart/form-data")
    step_schema = _request_schema(
        paths["/api/guides/{slug_or_id}/steps/{step_id}/images"]["post"], "multipart/form-data"
    )
    assert set(schemas[cover_schema["$ref"].rsplit("/", 1)[-1]]["properties"]) == {"image", "extension"}
    assert set(schemas[step_schema["$ref"].rsplit("/", 1)[-1]]["properties"]) == {
        "image",
        "extension",
        "caption",
        "alt_text",
    }
