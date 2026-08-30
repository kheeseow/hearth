# Product Slice 14: Hermes Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Hermes safe, immediate read/write access to Hearth Guides, including reliable bulk creation and optional media attachment.

**Architecture:** Add one standalone `meg-hearth` plugin to the Hermes deployment repository and reuse Hearth's authenticated Guide REST routes. Add only a narrow Hearth contract test and documentation; do not add another server, database table, or frontend flow.

**Tech Stack:** Python 3, `httpx`, Hermes plugin registry, FastAPI/Pydantic REST contracts, standalone Python tests, pytest.

**Spec:** `docs/superpowers/specs/2026-08-30-hermes-integration-design.md`

## Global Constraints

- Keep the integration additive and preserve Mealie-compatible Recipe code and database structures.
- Add no dependency: use the `httpx` already present in Hermes.
- Never print, return, or commit `HEARTH_TOKEN`.
- Use Hearth's camel-case JSON aliases and existing `/api/guides` routes.
- Batch size is 1 to 50; image size is at most 10 MiB.
- Exact-title duplicate matches are skipped unless `duplicatePolicy` is `create`.
- Deletion requires `confirm: true`.
- Modify no non-English locale.

---

### Task 1: Core Hearth client and read tools

**Files:**
- Create: `/Users/andrewtay/Engineering/meg-hermes-deploy/plugins/meg-hearth/__init__.py`
- Create: `/Users/andrewtay/Engineering/meg-hermes-deploy/plugins/meg-hearth/plugin.yaml`
- Create: `/Users/andrewtay/Engineering/meg-hermes-deploy/tests/test_meg_hearth.py`

**Interfaces:**
- Produces: `_request(method, path, *, params=None, json_body=None, files=None, data=None) -> Any`
- Produces: `_handle_search_guides(args, **_) -> str` and `_handle_get_guide(args, **_) -> str`
- Produces: `register(ctx) -> None` with a `hearth` availability check using `HEARTH_URL` and `HEARTH_TOKEN`.

- [ ] Write failing tests that verify the bearer header, camel-case query forwarding, readable 401/403/404 errors, slug/UUID lookup, and tool registration.
- [ ] Run `uv run pytest tests/test_meg_hearth.py -q` in the Hermes repository and confirm the new tests fail because the plugin is absent.
- [ ] Implement the minimal client, availability gate, read handlers, schemas, and manifest for `hearth_search_guides` and `hearth_get_guide`.
- [ ] Run `uv run pytest tests/test_meg_hearth.py -q` and confirm the Task 1 tests pass.
- [ ] Commit the tested read contract.

### Task 2: Bulk Guide creation and duplicate protection

**Files:**
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/plugins/meg-hearth/__init__.py`
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/plugins/meg-hearth/plugin.yaml`
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/tests/test_meg_hearth.py`

**Interfaces:**
- Consumes: `_request(...)` from Task 1.
- Produces: `_normalized_title(value: str) -> str` using NFKC, collapsed whitespace, and `casefold()`.
- Produces: `_handle_create_guides(args, **_) -> str`, accepting `guides: list[dict]` and `duplicatePolicy: "skip" | "create"`.
- Produces: an ordered result with integer `created`, `skipped`, `failed` and `items` entries.

- [ ] Add failing tests for empty/oversized batches, missing titles, exact normalized duplicates, explicit duplicate creation, complete Guide payload forwarding, partial batch failure, and concise ordered counts.
- [ ] Run the focused test file and confirm the new creation tests fail.
- [ ] Implement validation, exact-title lookup through `GET /api/guides`, wrapper-field stripping, `POST /api/guides`, and independent item results.
- [ ] Run the focused test file and confirm all creation tests pass.
- [ ] Commit bulk creation and duplicate protection.

### Task 3: Update, protected delete, and safe media

**Files:**
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/plugins/meg-hearth/__init__.py`
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/plugins/meg-hearth/plugin.yaml`
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/tests/test_meg_hearth.py`

**Interfaces:**
- Consumes: `_request(...)` and bulk result contract.
- Produces: `_download_image(url: str) -> tuple[bytes, str]` with public-address and 10 MiB checks.
- Produces: `_attach_media(guide: dict, media: dict) -> list[str]` returning media error messages.
- Produces: `_handle_update_guide(args, **_) -> str` and `_handle_delete_guide(args, **_) -> str`.

- [ ] Add failing tests for partial PATCH, empty changes, two-step delete, cover upload, step image mapping by returned step position, non-image/oversized/private-address rejection, and creation that survives a media failure.
- [ ] Run the focused test file and confirm the new tests fail.
- [ ] Implement PATCH and DELETE handlers, public image URL validation/download, multipart cover/step uploads, and truthful media-error results.
- [ ] Run the focused test file and confirm all plugin tests pass.
- [ ] Commit update, deletion, and media support.

### Task 4: Hearth contract, operations guide, and whole-slice verification

**Files:**
- Create: `tests/unit_tests/routes/test_hermes_guide_contract.py`
- Create: `docs/hermes-integration.md`
- Modify: `docs/implementation-plan.md`
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/config.yaml`
- Modify: `/Users/andrewtay/Engineering/meg-hermes-deploy/tests/test_meg_hearth.py`

**Interfaces:**
- Consumes: all tool names and REST fields from Tasks 1–3.
- Produces: an operator setup path for a dedicated Hearth user/token and the `HEARTH_URL`/`HEARTH_TOKEN` runtime settings.

- [ ] Add a failing Hearth contract test that inspects the FastAPI OpenAPI document for authenticated Guide list/get/create/patch/delete plus cover and step-image upload routes and verifies camel-case Guide fields.
- [ ] Run `uv run pytest tests/unit_tests/routes/test_hermes_guide_contract.py -q` and confirm any contract mismatch is visible.
- [ ] Add the operator guide, add `meg-hearth` to the Hermes main profile configuration, and update the roadmap/decision log with Slice 14's final evidence.
- [ ] Run the new Hearth contract test, all Guide backend tests, the full Hermes plugin test file, and the Hermes tests affected by plugin loading/configuration.
- [ ] Run Hearth lint/type checks relevant to the new contract test and Markdown checks available in the repository.
- [ ] Ask a fresh review agent to compare both repository diffs with the spec; fix blocking findings and rerun affected tests.
- [ ] Commit the completed Slice 14 changes in each repository.
- [ ] Back up live Hermes plugin/config files, stage the verified plugin, compare hashes and ownership, and activate only when `HEARTH_URL` and `HEARTH_TOKEN` are present and Hearth is reachable from the NAS.
