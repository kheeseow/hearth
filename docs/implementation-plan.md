# Hearth Implementation Plan

## Purpose

Build Hearth as a standalone, self-hosted household how-to product while
remaining an upstream-friendly Mealie codebase.

The core rule for this work is:

> Add Guide as a real domain. Do not rename Recipe or reuse recipe tables as
> disguised guide tables.

This document is the working implementation plan. It should be updated when a
phase uncovers new dependencies or changes a later decision.

"Standalone" describes the product and Guide domain, not a requirement to
rewrite Mealie's platform or erase its repository history.

## Current status

- Phase 1 architecture research is complete.
- The Hearth fork is checked out from Mealie `v3.24.0` at commit
  `2c04da733f88836f788234a4bf1127599fbc1294`.
- `origin` points to `kheeseow/hearth`; `upstream` points to
  `mealie-recipes/mealie`.
- The unchanged SQLite application, backend suite, frontend suite, and frontend
  lint have passed. Detailed results are in `docs/baseline.md`.
- No application code or database schema has been changed.
- The repository is ready for the Phase 2 minimal Guide backend vertical slice.

## Product outcome

A user should be able to open Hearth on a phone, search using ordinary words,
open a concise Guide, and follow clear ordered steps within seconds.

The initial product supports:

- Guide cards and search
- Guide viewing and editing
- Categories and tags
- Guide type, difficulty, duration, and frequency
- Tools and materials
- Safety warnings and things to avoid
- Ordered steps with tips and images
- Notes, sources, related guides, and review dates
- Existing user, household, and authentication infrastructure

The initial product does not include:

- AI answers
- OCR or image recognition
- Maintenance reminders
- Full offline Guide synchronization
- Automatic conversion of every Recipe into a Guide
- QR codes before the core Guide experience is stable

## Architectural direction

Hearth will initially remain a modular monolith:

```text
Nuxt/Vue frontend
        |
        v
FastAPI REST API
        |
        v
Guide service and repository
        |
        v
SQLAlchemy + SQLite/PostgreSQL
```

Guide code will be kept in a separate vertical domain:

```text
Backend
  mealie/db/models/guide/
  mealie/schema/guide/
  mealie/routes/guide/
  mealie/services/guide/
  mealie/repos/repository_guides.py

Frontend
  frontend/app/components/Domain/Guide/
  frontend/app/composables/guides/
  frontend/app/lib/api/user/guides/
  frontend/app/pages/g/[groupSlug]/guides/
```

Keep the existing `mealie` package name, application layering, build commands,
and deployment paths unless a concrete product requirement forces a change.
Hearth should become a distinct product without needlessly reorganizing the
repository. This is important because a familiar tree and small integration
surface make future Mealie merges substantially easier.

## Upstream compatibility policy

Hearth is a product fork, but it should remain an upstream-friendly fork. The
goal is not zero divergence; it is deliberate, bounded divergence.

### Structural rules

- Mirror Mealie's route -> controller -> service -> repository -> SQLAlchemy
  model flow for Guide.
- Mirror Mealie's Pydantic schema and generated TypeScript conventions.
- Add Guide modules beside Recipe modules rather than moving or renaming
  existing Mealie modules.
- Prefer new files over broad edits to existing files.
- In shared registry files, append Guide registrations without restructuring
  unrelated imports or code.
- Keep Mealie's formatter, test runner, package manager, migration system,
  configuration approach, and container layout.
- Do not rename the Python package, API prefix, app-data root, or core
  environment variables merely for branding.
- Keep generated files generated; update their source definitions and run the
  existing generator.
- Avoid speculative "universal content" abstractions. Extract a shared helper
  only after both Recipe and Guide genuinely use the same behavior.
- Hide unused Recipe features through capabilities and navigation policy before
  considering deletion.

### Small shared integration surface

Guide should normally require changes to only these existing integration
points:

- SQLAlchemy all-model registration
- Repository factory registration
- Top-level API router registration
- App capability/configuration response
- Type-generation inputs or exports
- Frontend API client exports
- Default navigation
- Backup/export registration
- Translation catalogs

Large edits outside those points require a written justification in the
decision log.

### Upstream merge workflow

Maintain both remotes and preserve upstream history:

```text
upstream  -> mealie-recipes/mealie
origin    -> Hearth repository
```

For every supported Mealie release adopted by Hearth:

1. Create an `upstream-sync/<version>` branch from Hearth's main branch.
2. Fetch tags and merge the selected upstream release or commit; do not copy
   upstream as an untracked source snapshot.
3. Resolve conflicts without redesigning the affected upstream module.
4. Regenerate API types and translations using upstream tooling.
5. Run upstream baseline tests first, then Hearth Guide tests.
6. Exercise SQLite and PostgreSQL migration paths.
7. Perform a mobile smoke test of login, Guide list, Guide view, edit, search,
   media, and legacy feature gating.
8. Record the adopted upstream version, conflicts, and any deferred upstream
   migrations in the compatibility log.
9. Merge the sync branch only when the complete suite passes.

Perform an upstream merge checkpoint at the end of every Hearth phase. This
prevents hundreds of product commits from accumulating before compatibility is
tested.

### Fork-delta controls

- Keep a machine-readable list of Hearth-owned modules and expected shared-file
  touchpoints under `docs/` or CI configuration once the repository exists.
- Add an import-boundary check: Guide may use platform modules but must not
  import Recipe schemas, services, repositories, or database models.
- Add a CI check that reports unexpected Hearth modifications to designated
  high-churn upstream files. Reporting should begin as advisory and become
  blocking after the expected touchpoint list stabilizes.
- Preserve upstream tests for hidden Recipe features. Hidden does not mean
  broken.
- Review the fork delta after each upstream merge and retire local patches when
  upstream now provides equivalent behavior.
- Keep implementation commits narrowly scoped and avoid drive-by formatting or
  renames in upstream-owned files.
- Keep Hearth migrations append-only in the shared Alembic chain and never
  rewrite an already released upstream migration.

## Reuse boundaries

### Reuse with minimal changes

- FastAPI application and middleware
- SQLAlchemy sessions, GUIDs, and Alembic
- SQLite and PostgreSQL support
- Users, groups, households, invitations, and API tokens
- Local login, LDAP, and OIDC
- Base authenticated routers and controllers
- Generic repository conventions
- Event bus and scheduler infrastructure
- Image processing primitives
- Nuxt, Vue, Vuetify, layouts, themes, and i18n
- Pydantic-to-TypeScript generation
- Backend and frontend test infrastructure
- Docker and single-container production packaging

### Extract or adapt before reuse

- Recipe media storage paths and cleanup
- Recipe share tokens
- Permission checks containing direct recipe SQL
- URL generation
- Backup and export services
- Category, tag, and tool UI patterns
- Search query infrastructure
- Domain event payloads

### Keep isolated as legacy

- Ingredients, foods, and units
- Scaling, servings, yield, and nutrition
- Recipe scraping and schema.org Recipe parsing
- Meal planning and plan rules
- Shopping lists and recipe references
- Ratings, favorites, and "last made"
- Recipe-specific timeline behavior

## Proposed Guide data model

Use UUID primary keys, explicit ordering columns for all ordered content, and
foreign-key cascades for owned child records.

### `guides`

- `id`
- `group_id`
- `household_id`
- `author_id`
- `slug`, unique within a group
- `title`
- `description`
- `guide_type`
- `difficulty`
- `frequency`
- `preparation_minutes`
- `execution_minutes`
- `category_id`
- `cover_image_id`, nullable
- `notes`, nullable
- `last_reviewed`, nullable date
- `search_document_normalized`
- `created_at`
- `updated_at`

Use string-backed application enums with database check constraints:

- Guide type: `cleaning`, `maintenance`, `setup`, `emergency`,
  `troubleshooting`, `care_instructions`
- Difficulty: `beginner`, `intermediate`, `advanced`
- Frequency: `one_time`, `weekly`, `monthly`, `yearly`, `as_needed`

Store durations as integer minutes. Formatting such as "1 hour 20 minutes" is
a presentation concern.

### Child and relationship tables

- `guide_steps`: ordered title, text, and optional tip
- `guide_step_images`: ordered image, caption, and alt text
- `guide_requirements`: ordered name, note, and `tool`/`material` kind
- `guide_callouts`: ordered text and `warning`/`avoid` kind
- `guide_categories`: group-scoped categories
- `guide_tags`: group-scoped tags
- `guides_to_tags`: Guide/tag association
- `guide_sources`: ordered label and URL
- `guide_relations`: directed related-Guide association
- `guide_assets`: optional general attachments
- `guide_media`: stored media metadata if a common media abstraction is ready

The final media table split should be decided during Phase 2 after inspecting
the fork's current media routes. Avoid polymorphic foreign keys without real
database constraints.

## API contract

Initial endpoints:

```text
GET    /api/guides
POST   /api/guides
GET    /api/guides/{slug-or-id}
PUT    /api/guides/{slug-or-id}
PATCH  /api/guides/{slug-or-id}
DELETE /api/guides/{slug-or-id}

POST   /api/guides/{slug-or-id}/cover
PUT    /api/guides/{slug-or-id}/cover
DELETE /api/guides/{slug-or-id}/cover

POST   /api/guides/{slug-or-id}/steps/{step-id}/images
DELETE /api/guides/{slug-or-id}/steps/{step-id}/images/{image-id}
```

Use separate Pydantic contracts:

- `GuideCreate`: minimum valid creation input
- `GuideUpdate`: complete editable state
- `GuidePatch`: partial update fields
- `GuideSummary`: list/card/search response
- `GuideRead`: complete Guide response

Do not make clients send a full read model to change one field.

## Search contract

The searchable document must include:

1. Title, highest weight
2. Description
3. Category and tags
4. Tools and materials
5. Step titles, text, and tips
6. Warnings and things to avoid
7. Source labels

Create a `GuideSearchService` boundary even if the first implementation uses
SQL only. This permits later full-text or semantic retrieval without changing
Guide routes and UI consumers.

Initial implementation:

- Maintain normalized title, description, and combined search document values
  whenever a Guide or searchable child changes.
- Support tokenized substring matching on both SQLite and PostgreSQL.
- Retain PostgreSQL trigram matching as an optional ranking enhancement.
- Add tests proving common searches such as `towel`, `washing machine`,
  `battery`, `router reset`, and `remove oil stain`.
- Keep ranking deterministic enough for pagination.

## Feature isolation

Introduce application capabilities rather than hiding links ad hoc:

- `GUIDES_ENABLED`
- `LEGACY_RECIPES_ENABLED`
- `MEAL_PLANNING_ENABLED`
- `SHOPPING_LISTS_ENABLED`
- `NUTRITION_ENABLED`

Each capability must control:

- Backend route exposure or rejection
- Frontend navigation
- Direct route access
- Related actions and dialogs

Migration defaults:

- Existing Mealie installation: legacy features remain enabled initially.
- Fresh Hearth installation: Guides enabled; recipe-only workflows disabled.

## Delivery phases

### Phase 0 — Establish the real baseline (complete)

Goal: make this plan safe to execute against the intended repository.

Tasks:

- Place the intended fork in the Hearth workspace.
- Record its branch, commit, Mealie version, and upstream remote.
- Read repository-specific `AGENTS.md` and contribution instructions.
- Compare its frontend, backend, migrations, media, auth, and search code with
  the researched upstream commit.
- Identify existing local changes and preserve them.
- Confirm supported upgrade origins: fresh install only, existing Mealie
  databases, or both.
- Confirm the intended public project name and package-renaming policy.
- Run the existing backend, frontend, and migration test suites unchanged.
- Document baseline failures before changing code.

Files affected:

- Documentation and CI configuration only, unless baseline repair is
  separately approved.

Exit criteria:

- Repository is present and understood.
- Existing changes are accounted for.
- Baseline tests and database targets are recorded.
- Upgrade-support decision is explicit.

### Phase 1 — Architecture research (complete)

The upstream architecture, Recipe coupling, reuse boundaries, migration risks,
and upstream-compatibility strategy have been assessed. The verified baseline
is recorded in `docs/baseline.md`.

Platform seams will now be introduced only when the Phase 2 Guide slice needs
them. This avoids a broad refactor before there is a concrete second consumer.

### Phase 2 — Add the Guide backend vertical slice

Goal: create, read, update, list, search, and delete a minimal Guide.

Initial scope:

- Title
- Description
- Cover image
- One category
- Tags
- Ordered plain-text steps
- Ownership and timestamps

Tasks:

- Create Guide directories that mirror the current Recipe directories and
  follow their local naming and dependency-injection conventions.
- Add the typed `GUIDES_ENABLED` capability and expose it through the existing
  app configuration response. Defer legacy feature flags until the frontend
  begins hiding those features.
- Add domain-neutral Guide media storage using existing image primitives. Do
  not refactor Recipe media unless a small shared helper clearly reduces both
  implementations.
- Extract URL, ownership, or event helpers only where the Guide implementation
  demonstrates the same requirement.
- Add Guide SQLAlchemy models and model registration.
- Add a single additive Alembic revision.
- Add Pydantic request and response schemas.
- Add `RepositoryGuides` with group/household scoping.
- Add `GuideService` for ownership, slug, and child ordering rules.
- Add authenticated `/api/guides` routes.
- Add media paths based on immutable Guide IDs.
- Add normalized lexical search.
- Register Guide domain events.
- Extend TypeScript type generation.
- Add SQLite and PostgreSQL migration tests.
- Add permission and multitenancy tests.
- Limit edits to shared upstream files to registrations and imports wherever
  possible.
- Record every shared upstream file changed by the phase.

Expected database impact:

- New Guide tables, indexes, constraints, and association tables.
- No updates to or deletions from Recipe tables.

Exit criteria:

- A Guide can complete the full CRUD lifecycle through the API.
- Search finds title, description, tags, and step text.
- One household cannot mutate another household's Guide without policy
  permission.
- Migration succeeds on empty and representative existing databases.
- Downgrade behavior is documented and tested where supported.
- Guide has no imports from Recipe domain modules.
- The current target Mealie version can be merged after the Guide change with
  the full baseline and Guide suites passing.

Implementation sequence:

1. Add the minimal Guide model and migration.
2. Add schema generation and repository access.
3. Add service rules and permission checks.
4. Add CRUD routes.
5. Add lexical search.
6. Add cover-media handling through the smallest reusable media seam.
7. Add tests and migration fixtures.
8. Perform the phase-end upstream merge checkpoint.

Do not add every future field in the first migration merely to avoid later
migrations. A small, verified vertical slice is easier to review and easier to
carry across upstream changes.

### Phase 3 — Build the Guide frontend vertical slice

Goal: make Guides usable without exposing Recipe UI concepts.

Tasks:

- Add Guide API client classes and generated types.
- Use Recipe list/card/page components as behavioral and visual references,
  but create Guide components in the parallel Guide directory.
- Add Guide list/card components using the same Vuetify and layout conventions
  as Mealie.
- Add a mobile-first Guide reader using existing global components where their
  APIs are domain-neutral.
- Add a structured Guide editor without modifying Recipe editor behavior.
- Add step reordering.
- Add cover and step-image upload flows.
- Add search, category, and tag filters.
- Add empty, loading, unavailable, and permission-denied states.
- Add Guide navigation as the primary Hearth entry point.
- Preserve legacy screens behind capability flags.
- Keep Nuxt route shapes parallel to Mealie's group-scoped route style.
- Avoid changes to global components unless Guide proves a missing generic
  capability; prefer a Guide wrapper first.

UX requirements:

- Primary actions remain reachable with one thumb on a phone.
- Warnings appear before procedure steps.
- Step numbering is prominent and stable.
- Images do not shift the page unexpectedly while loading.
- Viewing a Guide does not resemble editing a free-form document.

Exit criteria:

- A mobile user can create, find, open, edit, and complete a Guide.
- Core pages pass keyboard and screen-reader checks.
- Card and reader layouts work at phone, tablet, and desktop widths.
- No Recipe terminology appears in Guide routes or components.
- Existing Recipe pages still render and pass their upstream tests when legacy
  capabilities are enabled.
- A phase-end upstream merge checkpoint passes.

Implementation sequence:

1. API client and generated Guide types.
2. Read-only Guide list, card, and reader.
3. Minimal create/edit form.
4. Ordered-step editing.
5. Cover and step media.
6. Search/filter UI and navigation.
7. Accessibility and responsive verification.
8. Phase-end upstream merge checkpoint.

### Phase 4 — Add the full Guide domain

Goal: implement all Guide-specific fields from the product brief.

Tasks:

- Add type, difficulty, frequency, and duration fields.
- Add tools and materials.
- Add safety warnings and things to avoid.
- Add per-step tips and multiple images.
- Add Guide notes.
- Add source/reference links with URL validation.
- Add related Guides and self/cycle safeguards appropriate to the relation.
- Add last-reviewed date and a visible stale-review state.
- Extend search-document refresh logic for all searchable child content.
- Extend import/export and backup coverage.
- Extend existing backup/export orchestration through Guide-specific handlers;
  do not rewrite the complete upstream backup system.
- Keep each new field represented consistently across database model, Pydantic
  schema, generated TypeScript type, API client, editor, reader, search, export,
  and tests.

Expected database impact:

- Additive columns and child tables if not already created in Phase 2.
- Search-document backfill for existing Guides.

Exit criteria:

- Both example Guides from the brief can be represented without abusing notes
  or tags.
- All child collections preserve order after repeated edits.
- Backup and restore preserve every Guide field and media reference.
- Existing Mealie backup restoration remains covered.
- A phase-end upstream merge checkpoint passes.

Implementation sequence:

1. Metadata enums and typed durations.
2. Requirements and callouts.
3. Step tips and multiple images.
4. Sources, notes, related Guides, and review dates.
5. Search-document expansion and backfill.
6. Backup/export integration.
7. Full-domain migration and round-trip tests.
8. Phase-end upstream merge checkpoint.

### Phase 5 — Product polish and legacy isolation

Goal: make Hearth feel purpose-built rather than like a renamed recipe app.

Tasks:

- Apply branding through existing configuration, assets, and shallow metadata
  changes. Do not rename core packages or reorganize upstream directories.
- Refine information hierarchy, typography, and image treatment.
- Add quick search to the default landing screen.
- Improve search ranking using recorded realistic queries.
- Add printable Guide layout.
- Audit all menus, settings, notifications, translations, and emails.
- Disable legacy modules by default for fresh Hearth installations.
- Measure remaining imports from Guide code into Recipe code; target zero.
- Document operator migration and rollback procedures.
- Keep legacy backend modules functional and tested while their frontend entry
  points are hidden.
- Maintain a small Hearth theme/branding layer instead of scattering product
  conditionals throughout upstream components.

Exit criteria:

- A fresh install exposes no meal-planning, nutrition, scaling, or shopping UI.
- Existing installations can re-enable legacy features during the compatibility
  window.
- Guide domain has no imports from recipe schemas, repositories, or services.
- Branding changes remain confined to the documented touchpoint set.
- A phase-end upstream merge checkpoint passes.

Implementation sequence:

1. Complete feature-capability behavior for fresh and upgraded installs.
2. Centralize branding and Hearth defaults.
3. Polish search-first landing and Guide presentation.
4. Audit settings, notifications, emails, routes, and translations.
5. Complete accessibility, performance, and responsive passes.
6. Publish operator compatibility and rollback guidance.
7. Phase-end upstream merge checkpoint.

### Phase 6 — Add QR codes

Goal: make every Guide accessible from a safe, durable QR code.

Design rules:

- QR code represents a stable URL, not stored Guide content.
- Use immutable Guide ID in URL resolution; slug is cosmetic.
- Generate SVG and PNG on demand.
- Authentication is required by default.
- Public access uses a separate, revocable, optionally expiring share token.
- Never place bearer tokens or household secrets in QR payloads.
- Deleted, private, expired, and revoked Guides have deliberate landing states.

Tasks:

- Add a domain-neutral QR renderer.
- Add authenticated Guide QR endpoints.
- Add Guide share-token tables and management endpoints if public QR access is
  included.
- Add download and print-sticker UI.
- Test scanning, URL changes, token revocation, and unauthorized access.

Exit criteria:

- Printed QR remains valid after Guide title/slug changes.
- Revocation works immediately.
- QR output is legible at intended sticker sizes.
- QR implementation is contained in Guide and shared utility modules rather
  than modifying Recipe sharing behavior.
- A phase-end upstream merge checkpoint passes.

Implementation sequence:

1. Stable Guide URL resolution.
2. Domain-neutral QR rendering utility.
3. Authenticated download endpoints and UI.
4. Optional Guide-specific public share tokens.
5. Sticker print layouts and scan tests.
6. Security and revocation tests.
7. Phase-end upstream merge checkpoint.

### Phase 7 — Upgrade, compatibility, and release hardening

Goal: prove that Hearth is a complete product and a maintainable Mealie fork.

Tasks:

- Select and merge a current stable Mealie release using the documented sync
  workflow.
- Inventory every merge conflict and reduce Hearth changes in recurring
  high-conflict files where possible.
- Verify new upstream authentication, security, dependency, deployment,
  backup, PWA, and UI improvements in Hearth.
- Run full fresh-install and Mealie-upgrade test matrices for SQLite and
  PostgreSQL.
- Run backup/restore tests across pre-Guide and Guide-aware backups.
- Audit authorization and public-sharing behavior.
- Test supported browsers and representative mobile devices.
- Establish versioning that records both Hearth version and adopted Mealie
  baseline.
- Publish an upstream compatibility log and upgrade runbook.
- Publish contributor rules for changes to shared upstream files.
- Decide whether optional Recipe-to-Guide conversion is needed. If built, it
  must support dry run, backup, idempotency, and a validation report.
- Keep legacy Recipe tables and modules during the compatibility period unless
  their ongoing presence creates a measured security or maintenance problem.

Exit criteria:

- Guide runtime does not depend on Recipe domain modules.
- Hidden legacy modules still pass upstream tests when enabled.
- A documented Mealie release can be merged reproducibly.
- Fresh install, upgrade, backup, restore, and rollback paths pass.
- Security, accessibility, performance, and mobile acceptance checks pass.
- Release documentation identifies the exact Mealie baseline.

### Phase 8 — Completion and sustainable maintenance

Goal: release Hearth without turning the fork into an unmergeable codebase.

Tasks:

- Cut a release candidate from the hardened compatibility baseline.
- Run real household beta testing with representative Cleaning, Maintenance,
  Setup, Emergency, Troubleshooting, and Care Instruction Guides.
- Fix release blockers within the established Guide modules and shared-file
  touchpoint policy.
- Perform one final upstream security and dependency review.
- Publish container images, source, installation documentation, data migration
  guidance, backup guidance, and AGPL notices.
- Tag the Hearth release and record its Mealie baseline.
- Set an upstream review cadence, initially monthly and immediately for relevant
  security releases.
- For each future Mealie release, classify changes as adopt, defer with reason,
  or not applicable.
- Continue retiring local patches when equivalent upstream features become
  available.

Completion criteria:

- The complete Guide product scope is available and documented.
- Recipe-only functionality is absent from the default Hearth experience.
- No destructive Recipe data migration is required for ordinary upgrades.
- Hearth-owned code is concentrated in Guide modules and documented shallow
  integration points.
- A maintainer can adopt a new Mealie release using the runbook without
  rediscovering the fork architecture.
- CI continuously validates Hearth behavior and retained upstream behavior.
- The release is reproducible from the tagged source.

## Validation strategy

Every implementation phase must include proportionate verification.

### Backend

- Unit tests for schemas, slug generation, ordering, and search normalization
- Repository tests for scoping and relationships
- Service tests for ownership and media cleanup
- Route tests for validation, authentication, and response contracts
- Multitenant tests across groups and households
- SQLite and PostgreSQL migration tests
- Backup/export round-trip tests

### Frontend

- Component tests for cards, steps, warnings, and editor state
- Composable tests for search and mutations
- API route contract tests
- Responsive visual checks at phone, tablet, and desktop sizes
- Keyboard navigation and accessible labels
- Error, loading, empty, offline, and permission states

### End-to-end scenarios

1. Create and find "How to Restore Turkish Cotton Towels."
2. Create and find "How to Jump Start a Car."
3. Search for `towel`, `washing machine`, `battery`, and `correct polarity`.
4. Reorder steps and confirm the order persists.
5. Add, replace, and delete cover and step images.
6. Attempt cross-household read, update, and delete operations.
7. Upgrade an existing database with legacy data intact.
8. Back up and restore Guides and media.
9. Change a Guide title and confirm durable URLs still resolve.

## Migration safety rules

- Make schema changes additive until the final extraction phase.
- Never mutate Recipe rows automatically on normal startup.
- Back up before any opt-in data conversion.
- Give data migrations stable identifiers and make them idempotent where
  possible.
- Test migrations from the oldest explicitly supported version, not only from
  the immediately previous revision.
- Verify foreign keys, unique constraints, ordering, and search backfills on
  both supported databases.
- Do not delete media until the owning database transaction is known to have
  succeeded, or provide cleanup reconciliation.
- Treat downgrade support honestly; document when a migration is intentionally
  irreversible.

## Risk register

| Risk | Mitigation |
|---|---|
| Actual fork differs from researched upstream | Phase 0 reconciliation gate |
| Recipe coupling leaks into Guide | Parallel domain and import-boundary tests |
| SQLite/PostgreSQL behavior diverges | Dual-database CI and migration tests |
| Search becomes slow after indexing step text | Denormalized search document and measured query plans |
| Search results differ greatly by database | Portable token baseline; trigram only as enhancement |
| Step or cover media is orphaned | Immutable IDs, constrained metadata, reconciliation tests |
| Public QR exposes household information | Private default and revocable share tokens |
| Feature flags hide UI but leave unsafe API access | Gate backend and frontend separately |
| Generated TypeScript contracts go stale | Regeneration check in CI |
| Upstream updates repeatedly break the fork | Pin baseline and cherry-pick selectively |
| AGPL or branding obligations are missed | License review before public release |
| Package rename breaks deployments | Delay rename; support compatibility aliases |

## Decision log

Record material decisions here as they are made.

| Date | Decision | Reason |
|---|---|---|
| 2026-08-23 | Create Guide beside Recipe | Avoid destructive rename and recipe-domain coupling |
| 2026-08-23 | Keep modular monolith initially | Reuses stable deployment and authentication infrastructure |
| 2026-08-23 | Use additive migrations | Protect existing installations and simplify rollback |
| 2026-08-23 | Store durations as integer minutes | Typed, searchable, and presentation-independent |
| 2026-08-23 | Delay QR until core UX is stable | QR depends on durable URLs and sharing policy |
| 2026-08-23 | Delay package rename | Avoid mixing domain work with deployment migration |
| 2026-08-23 | Remain structurally close to Mealie | Preserve the ability to adopt upstream features and fixes |
| 2026-08-23 | Keep hidden Recipe modules tested | Product independence does not require destructive code removal |

## Immediate next action

Start Phase 2 with the minimal Guide model and additive Alembic migration, then
complete repository, service, CRUD route, search, permission, and migration
tests before beginning the frontend slice.
