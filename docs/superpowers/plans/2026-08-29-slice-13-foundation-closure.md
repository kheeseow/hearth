# Product Slice 13: Foundation Closure Implementation Plan

> **For Codex:** Execute this plan with the subagent-driven-development workflow. Keep all changes additive and preserve Mealie's architecture and retained legacy behavior.

**Goal:** Close the remaining Guide foundation work by adding Guide lifecycle notifications, publishing operator compatibility and rollback guidance, proving Guide/Recipe isolation, and recording a fresh upstream merge checkpoint.

**Architecture:** Extend Mealie's existing event types, notifier options, event bus, URL helpers, and notifier UI rather than creating a Guide-specific notification system. Keep Guide code isolated from Recipe-domain modules. Treat the upstream checkpoint as a read-only synthetic merge; do not merge upstream into the working branch during this slice.

**Tech stack:** FastAPI, Pydantic, SQLAlchemy/Alembic, Nuxt 4, Vue 3, TypeScript, Vuetify, pytest, Vitest.

---

## Task 1: Add the Guide event contract and persistence

**Files:**
- Modify: `mealie/services/event_bus_service/event_types.py`
- Modify: `mealie/schema/household/group_events.py`
- Modify: `mealie/db/models/household/events.py`
- Create: `mealie/alembic/versions/2026-08-29-*.py`
- Modify: `tests/unit_tests/test_alembic.py`
- Modify: `tests/integration_tests/user_household_tests/test_group_notifications.py`

**Steps:**
1. Add failing tests for three Guide notifier preferences and migration upgrade/downgrade behavior.
2. Add `guide_created`, `guide_updated`, and `guide_deleted` event types.
3. Add a Guide document type and typed event payload containing the stable Guide slug.
4. Add matching false-by-default notifier fields to Pydantic and SQLAlchemy models.
5. Add one additive Alembic migration with reversible boolean columns; alter no Recipe table.
6. Run the targeted event, notifier, and migration tests.

## Task 2: Publish Guide lifecycle events

**Files:**
- Modify: `mealie/routes/guide/guide_crud_routes.py`
- Modify: `mealie/services/urls/url_constructors.py`
- Modify: `tests/integration_tests/user_guide_tests/test_guide_crud.py`

**Steps:**
1. Add failing tests that capture create, update, and delete dispatches after successful Guide mutations.
2. Reuse the existing base controller event-bus support.
3. Add the canonical group-scoped Guide URL constructor.
4. Publish localized create/update/delete messages and typed Guide event data only after successful persistence.
5. Treat cover and step-image changes as Guide updates if they use the same successful mutation path; avoid duplicate notifications.
6. Run the Guide CRUD integration suite.

## Task 3: Expose Guide events in notification settings

**Files:**
- Modify: `frontend/app/pages/household/notifiers.vue`
- Modify: `frontend/app/lang/messages/en-US.json`
- Regenerate: generated API types and route helpers through `task dev:generate`

**Steps:**
1. Regenerate the frontend contracts from the backend schema.
2. Add a Guide event section with create, update, and delete controls.
3. Keep Recipe and other retained event controls intact for upgraded installations.
4. Add only the English Guide event heading; do not edit Crowdin-managed locales.
5. Run frontend lint, types/tests, and production build.

## Task 4: Publish operator guidance and enforce the domain boundary

**Files:**
- Create: `docs/operator-compatibility.md`
- Create or modify: a focused Guide/Recipe import-boundary test under `tests/unit_tests/`
- Modify: `docs/fork-delta.md`

**Steps:**
1. Add a repeatable test that fails when Guide backend or frontend production files import Recipe-domain modules.
2. Document fresh-install versus upgraded-install behavior and `HEARTH_LEGACY_FEATURES` override precedence.
3. Document backup-first upgrades, validation, application rollback, schema downgrade limits, and Guide-data preservation.
4. Document the retained Recipe code/database policy and exact supported ports/configuration.
5. Run the boundary test and check all documented commands and paths against the repository.

## Task 5: Record the Phase 5 upstream checkpoint

**Files:**
- Modify: `docs/fork-delta.md`
- Modify: `docs/implementation-plan.md`

**Steps:**
1. Fetch `upstream` without changing the working tree.
2. Record the exact upstream target commit and ahead/behind counts.
3. Run Git's synthetic merge-tree check against the current branch.
4. Record any conflict paths, or explicitly record a clean synthetic merge.
5. Mark Phase 2 events and Phase 5 complete only after implementation and verification pass.
6. Set the next action to Hermes integration design/API scope before Phase 6 release hardening; do not implement Hermes integration in this slice.

## Task 6: Whole-slice verification and review

**Steps:**
1. Inspect the complete diff for unintended generated or non-English locale changes.
2. Run Python formatting, lint, type checking, targeted tests, and the full backend suite.
3. Run frontend lint, full tests, and production build.
4. Run fresh SQLite and PostgreSQL migration upgrade/downgrade/re-upgrade checks.
5. Repeat the Guide-to-Recipe boundary audit and synthetic upstream merge check on the final tree.
6. Ask a fresh review agent to compare the implementation with this plan and fix any blocking findings.
7. Update validation evidence in `docs/implementation-plan.md` and commit the completed slice.
