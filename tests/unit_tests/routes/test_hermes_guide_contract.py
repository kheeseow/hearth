"""Protect the authenticated Guide API contract consumed by Hermes."""

from fastapi.testclient import TestClient

from mealie.schema.guide import GuideCreate, GuidePatch

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

GUIDE_ENUMS = {
    "GuideType": ["cleaning", "maintenance", "setup", "emergency", "troubleshooting", "care_instructions"],
    "GuideDifficulty": ["beginner", "intermediate", "advanced"],
    "GuideFrequency": ["one_time", "weekly", "monthly", "yearly", "as_needed"],
    "GuideCalloutKind": ["warning", "avoid"],
    "GuideRequirementKind": ["tool", "material"],
}

NESTED_INPUTS = {
    "steps": ("GuideStepIn", ["text"]),
    "callouts": ("GuideCalloutIn", ["kind", "text"]),
    "requirements": ("GuideRequirementIn", ["kind", "name"]),
    "sources": ("GuideSourceIn", ["label", "url"]),
}


def _request_schema(operation: dict, content_type: str) -> dict:
    request_body = operation["requestBody"]["content"][content_type]["schema"]
    reference = request_body["$ref"]
    return {"$ref": reference}


def _response_schema(operation: dict, status_code: str) -> dict:
    response = operation["responses"][status_code]["content"]["application/json"]["schema"]
    reference = response["$ref"]
    return {"$ref": reference}


def _reference(name: str) -> dict:
    return {"$ref": f"#/components/schemas/{name}"}


def _non_null_branch(schema: dict) -> dict:
    branches = schema.get("anyOf")
    assert isinstance(branches, list)
    assert {"type": "null"} in branches
    non_null = [branch for branch in branches if branch != {"type": "null"}]
    assert len(non_null) == 1
    return non_null[0]


def _assert_field_shape(schema: dict, **expected: object) -> None:
    for key, value in expected.items():
        assert schema[key] == value


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
    assert schemas["GuideCreate"]["required"] == ["title"]
    assert "required" not in schemas["GuidePatch"]

    for schema_name, values in GUIDE_ENUMS.items():
        _assert_field_shape(schemas[schema_name], type="string", enum=values)

    create_properties = schemas["GuideCreate"]["properties"]
    patch_properties = schemas["GuidePatch"]["properties"]
    for field, enum_name in (
        ("guideType", "GuideType"),
        ("difficulty", "GuideDifficulty"),
        ("frequency", "GuideFrequency"),
    ):
        assert _non_null_branch(create_properties[field]) == _reference(enum_name)
        assert _non_null_branch(patch_properties[field]) == _reference(enum_name)

    for field, (schema_name, required) in NESTED_INPUTS.items():
        assert create_properties[field]["items"] == _reference(schema_name)
        assert _non_null_branch(patch_properties[field])["items"] == _reference(schema_name)
        assert schemas[schema_name]["required"] == required

    nullable_uuid4 = {"type": "string", "format": "uuid4"}
    assert _non_null_branch(schemas["GuideStepIn"]["properties"]["id"]) == nullable_uuid4
    _assert_field_shape(
        _non_null_branch(schemas["GuideStepIn"]["properties"]["tip"]),
        type="string",
        minLength=1,
        maxLength=2000,
    )
    assert _non_null_branch(schemas["GuideCalloutIn"]["properties"]["id"]) == nullable_uuid4
    assert _non_null_branch(schemas["GuideRequirementIn"]["properties"]["id"]) == nullable_uuid4
    _assert_field_shape(
        _non_null_branch(schemas["GuideRequirementIn"]["properties"]["note"]),
        type="string",
        minLength=1,
        maxLength=500,
    )
    assert _non_null_branch(schemas["GuideSourceIn"]["properties"]["id"]) == nullable_uuid4

    tag_items = {"type": "string", "minLength": 1, "maxLength": 50}
    related_items = {"type": "string", "format": "uuid4"}
    assert create_properties["tags"]["items"] == tag_items
    assert _non_null_branch(patch_properties["tags"])["items"] == tag_items
    assert create_properties["sources"]["maxItems"] == 50
    assert create_properties["relatedGuideIds"]["items"] == related_items
    assert _non_null_branch(patch_properties["relatedGuideIds"])["items"] == related_items

    # Hermes never submits more than these values. Bind that Hearth accepts the
    # advertised upper edge, including limits enforced by model validators that
    # are not represented as maxItems in OpenAPI.
    limit_payload = {
        "tags": ["tag"] * 20,
        "requirements": [{"kind": "tool", "name": "Tool"}] * 50,
        "sources": [{"label": "Source", "url": "https://example.com"}] * 50,
        "relatedGuideIds": ["123e4567-e89b-42d3-a456-426614174000"] * 20,
    }
    GuideCreate.model_validate({"title": "Hermes limit contract", **limit_payload})
    GuidePatch.model_validate(limit_payload)

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
    assert schemas["GuideRead"]["properties"]["steps"]["items"] == {"$ref": "#/components/schemas/GuideStepOut"}
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
