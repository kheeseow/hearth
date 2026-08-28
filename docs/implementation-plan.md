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
- Product Slices 1 through 11 are implemented and validated locally.
- The Hearth fork is checked out from Mealie `v3.24.0` at commit
  `2c04da733f88836f788234a4bf1127599fbc1294`.
- `origin` points to `kheeseow/hearth`; `upstream` points to
  `mealie-recipes/mealie`.
- The unchanged SQLite application, backend suite, frontend suite, and frontend
  lint have passed. Detailed results are in `docs/baseline.md`.
- The first additive Guide migration introduces only `guides` and
  `guide_steps`; Recipe tables remain untouched.
- The first usable UI supports Guide cards, title/description search, reading,
  creation, editing, deletion, and ordered plain-text steps.
- Guide classification, timing, group-scoped category/tags, safety callouts,
  expanded search, and exact metadata filters are now usable end to end.
- Guide frequency, ordered tools and materials, requirement notes, and optional
  per-step tips are now usable end to end.
- Guide cover images and ordered step images with captions and alternative text
  are now usable end to end.
- Guide notes, ordered references, related Guides, review dates, and visible
  stale-review states are now usable end to end.
- Guide libraries can be exported as readable JSON with their complete media,
  and full installation backups restore all Guide fields and files.
- Fresh Hearth installations now present Guides as the sole product workflow,
  while upgraded Mealie installations retain their existing Recipe, meal-plan,
  shopping-list, and nutrition entry points.
- Shared application chrome, install metadata, and the Guide library now use a
  centralized Hearth identity and a warm, Guide-first presentation.
- The Guide reader now has a responsive reading hierarchy and a complete,
  browser-native print layout without introducing a second content model.
- Fresh-install setup and shared settings now expose only Hearth-relevant
  choices, while upgraded installations retain their full Mealie-compatible
  settings, notification tools, data management, and administration routes.
- Core Guide, setup, and shared-navigation flows now provide keyboard focus,
  accessible names and status feedback, correct document language and
  direction, reduced-motion support, and verified 320-pixel reflow.
- Phase 4 is complete. Its Guide domain, export, and backup checkpoint remains
  additive and does not alter Recipe persistence.
- Phase 2 remains open for Guide events. Phase 3 is complete. Phase 5 product
  polish and capability isolation is underway.
- QR codes are deferred to the final optional phase and do not block the first
  complete Hearth release.

## Product Slice 1 — Minimal Guide CRUD (complete)

This slice deliberately crosses the backend/frontend phase boundary to produce
a small usable outcome before adding richer fields.

Included:

- Title and description
- Ordered plain-text steps
- Stable group-unique slug
- Group-wide reading and discovery
- Owning-household-only update and delete
- Authenticated CRUD API
- Normalized title and description search
- Generated TypeScript contracts and user API client
- Searchable Guide cards, reader, create form, and editor
- Header search and `/` shortcut search Guides and open the selected Guide
- Add, remove, and move step controls
- Sidebar navigation

Deferred to later slices:

- Cover and step media
- Categories, tags, tools, and materials
- Guide type, difficulty, frequency, and duration
- Warnings, notes, sources, and review dates
- Domain events and backup/export integration
- Capability-driven hiding of legacy Recipe UI
- Step-text search

Validation completed on 2026-08-26:

- Full backend suite: 2,648 passed and 16 skipped by existing upstream markers
- Fresh SQLite migration: upgrade, downgrade, and re-upgrade passed
- Fresh PostgreSQL 16 migration: upgrade, downgrade, and re-upgrade passed
- Frontend ESLint: passed
- Full frontend suite: 28 files and 274 tests passed
- Nuxt production build: passed
- Phone-width browser smoke check: Guide list and editor render at 390 x 844;
  add-step and reorder controls respond correctly
- Browser search check: the header search and `/` shortcut find Guides by title
  and open the selected Guide
- User acceptance test: completed successfully
- Guide-to-Recipe import boundary check: no imports found

`RepositoryGuides` extends Mealie's generic household repository for ordered
child reconciliation, group-scoped metadata reuse, the combined search
document, and Guide-specific filters. It continues to use Mealie's generic
pagination, query, and group/household scoping primitives.

## Product Slice 2 — Classification and safety (complete)

Included:

- Guide type: cleaning, maintenance, setup, emergency, troubleshooting, or
  care instructions
- Difficulty: beginner, intermediate, or advanced
- Preparation and execution durations stored as integer minutes
- One reusable group-scoped category and reusable group-scoped tags
- Ordered warnings and things to avoid
- Search across title, description, type, difficulty, category, tags, step
  text, warnings, and things to avoid
- Exact list filters for type, difficulty, category, and tag
- Metadata chips on cards and the reader
- Safety callouts displayed before procedure steps
- Additive backfill of existing Guide search documents

The Slice 2 migration adds Guide-only tables and nullable Guide columns. It
does not alter Recipe tables. SQLite and PostgreSQL 16 upgrade, downgrade, and
re-upgrade paths pass from fresh databases.

Validation completed on 2026-08-26:

- Guide API integration suite: 5 passed
- Full backend suite: 2,649 passed and 16 skipped by existing upstream markers
- Python type check: 469 source files passed
- Frontend ESLint: passed
- Full frontend suite: 28 files and 274 tests passed
- Nuxt production build: passed
- SQLite and PostgreSQL 16 migration round trips: passed
- Desktop browser flow: create, edit, read, safety-content search, and type
  filter passed
- Phone-width reader check at 390 x 844: passed
- A sample “Monthly washing machine clean” Guide is available in local
  development for acceptance testing

## Product Slice 3 — Requirements and richer steps (complete)

Included:

- Frequency: one time, weekly, monthly, yearly, or as needed
- Exact frequency filtering on the Guide list
- Ordered tools and materials with optional preparation notes
- Add, remove, edit, and reorder controls for Guide requirements
- Optional tips attached directly to individual steps
- Search across frequency, tool and material names, requirement notes, and
  step tips
- Frequency chips on Guide cards and the reader
- An ordered “What you'll need” section before the procedure
- Tip callouts displayed beneath their associated steps

The Slice 3 migration adds one nullable Guide column, one nullable Guide-step
column, and the Guide-owned `guide_requirements` table. It does not alter Recipe
tables or modify the released Slice 1 and Slice 2 migrations. SQLite and
PostgreSQL 16 upgrade, downgrade, and re-upgrade paths pass from fresh
databases.

Validation completed on 2026-08-26:

- Guide API integration suite: 6 passed
- Full backend suite: 2,650 passed and 16 skipped by existing upstream markers
- Python type check: 470 source files passed
- Frontend ESLint: passed
- Full frontend suite: 28 files and 274 tests passed
- Nuxt production build: passed
- SQLite and PostgreSQL 16 migration round trips: passed
- Desktop browser flow: edit, reorder, save, read, requirement-note search,
  and exact frequency filtering passed
- Phone-width reader check at 390 x 844: passed
- The local “Monthly washing machine clean” acceptance Guide now demonstrates
  monthly frequency, ordered requirements, requirement notes, and a step tip

## Product Slice 4 — Guide media (complete)

Included:

- One replaceable Guide cover image
- Up to 20 ordered images per persisted Guide step
- Optional captions and useful alternative text for every step image
- Upload, replace, reorder, metadata-edit, and delete controls in the Guide
  editor
- Responsive cover and step-image presentation in the Guide reader
- Cover thumbnails on Guide cards
- Authenticated media reads so private Guide images are not exposed as public
  files
- Three generated WebP sizes using Mealie's domain-neutral image primitives
- File cleanup when an image, step, or complete Guide is deleted

The Slice 4 migration adds one nullable Guide cover-version column and the
Guide-owned `guide_step_images` table. Files live beneath immutable Guide and
image IDs in a separate Guide data directory. The implementation does not
import Recipe models, schemas, repositories, routes, or services, and it does
not alter Recipe tables or earlier Guide migrations.

Validation completed on 2026-08-27:

- Guide API integration suite: 8 passed
- Full backend suite: 2,652 passed and 16 skipped by existing upstream markers
- Python lint and type check: 472 source files passed
- Frontend ESLint: passed
- Full frontend suite: 28 files and 274 tests passed
- Nuxt production build: passed
- SQLite and PostgreSQL 16 migration upgrade, downgrade, and re-upgrade paths:
  passed
- SQLite migration drift check: passed
- Existing local development data: all 15 seeded Guides preserved
- Guide-to-Recipe import boundary check: no imports found
- Desktop browser flow: cover and step images render in cards, reader, and
  editor; media controls and accessible labels are present
- Phone-width editor and reader check at 390 x 844: passed
- The local “Monthly washing machine clean” acceptance Guide now demonstrates
  a cover image and two captioned step images with alternative text

## Product Slice 5 — Knowledge upkeep (complete)

Included:

- Optional Guide notes and a nullable last-reviewed date
- A visible review state in the reader and a card warning after 365 days
- Up to 50 ordered reference links with required labels and HTTP/HTTPS URL
  validation
- Up to 20 directed related-Guide links within the same group
- Self-link, duplicate-link, missing-Guide, and cross-group safeguards
- Mutual related links remain valid for ordinary “see also” relationships;
  responses use shallow summaries and never recurse through the relation graph
- Search across notes, reference labels, and reference URLs
- Add, remove, edit, reorder, and clear controls in the Guide editor
- Reader sections for notes, references, and related Guides

The Slice 5 migration adds two nullable Guide columns, the ordered
`guide_sources` table, and the `guide_relations` association table. It changes
no Recipe table or prior Guide migration.

Validation completed on 2026-08-27:

- Guide API integration suite: 10 passed
- Full backend suite: 2,654 passed and 16 skipped by existing upstream markers
- Python lint and type check: 473 source files passed
- Frontend ESLint: passed
- Full frontend suite: 29 files and 277 tests passed
- Nuxt production build: passed
- SQLite and PostgreSQL 16 migration upgrade, downgrade, and re-upgrade paths:
  passed
- SQLite migration drift check: passed
- Desktop browser flow: stale card state, reader content, editor controls, and
  related-Guide labels passed
- Phone-width editor and reader check at 390 x 844: passed after correcting the
  responsive reader header
- The local “Monthly washing machine clean” acceptance Guide now demonstrates
  an overdue review, notes, two ordered references, and two related Guides

## Product Slice 6 — Guide export and backup (complete)

Included:

- Export all Guides currently shown in the Guide library with one action
- Human-readable, camel-case JSON containing the full Guide response contract
- Self-contained cover and step-image directories beneath each exported Guide
- Group-scoped export validation and download authorization
- Reuse of Mealie's tracked group-export ZIP and file-token flow
- Full installation backup and restore coverage for every Guide field,
  relationship, media reference, and generated media file
- PostgreSQL-safe conversion of the Guide last-reviewed date during restore
- Continued restoration coverage for all existing pre-Guide Mealie backup
  fixtures

The Slice 6 implementation adds one Guide-specific exporter and one narrow
orchestration service. Mealie's generic backup format, Recipe exporter, data
directories, and database schema remain structurally unchanged. A small
backward-compatible extension point lets individual exporters choose their JSON
serialization while preserving Recipe export behavior.

Validation completed on 2026-08-27:

- Guide API and backup/export suites: 19 passed
- Full backend suite: 2,656 passed and 16 skipped by existing upstream markers
- Complete Guide export contract, group boundary, media archive, and download
  token checks: passed
- Full Guide server-backup mutation and restore round trip: passed
- All nine historical Mealie backup fixtures restored successfully
- Python lint and type check: 475 source files passed
- Frontend ESLint: passed
- Full frontend suite: 29 files and 277 tests passed
- Nuxt production build: passed
- Browser flow: the Guide library export action created a tracked ZIP, issued
  an authorized download token, and returned the archive successfully
- Guide-to-Recipe import boundary check: no imports found
- Phase-end upstream checkpoint: a virtual merge with upstream `mealie-next`
  at `8d6027770ce366e9a283254c43be896d9f507935` completed without conflicts;
  the fork was 10 commits ahead and 18 commits behind at the checkpoint

## Product Slice 7 — Fresh-install product isolation (complete)

Included:

- One typed application-capability response for Guides, legacy Recipes, meal
  planning, shopping lists, and nutrition
- A persisted installation profile created by an additive migration
- Fresh-install detection before the default user is seeded, so new Hearth
  databases disable legacy workflows without inspecting data on every startup
- Upgrade-safe detection that leaves all Mealie workflows enabled when the
  database already contains users
- A single `HEARTH_LEGACY_FEATURES` operator override for temporarily enabling
  or disabling the complete legacy bundle without deleting data
- Capability-driven sidebar, create-menu, favorites, profile, and setup-page
  entry points
- A Guide-first group landing redirect for fresh Hearth installations
- Frontend redirects away from disabled Recipe, cookbook, meal-plan,
  shopping-list, and Recipe-favorites routes
- Fail-open behavior when a capability record is unexpectedly absent, avoiding
  accidental loss of access during an incomplete upgrade
- No removal or modification of Recipe, meal-plan, shopping-list, or nutrition
  backend modules

The capability table is server-wide rather than household-specific because it
describes the installed product profile, not authorization or content
ownership. Individual legacy capabilities remain separate in the public
contract so later slices can isolate their related actions and backend routes
without changing frontend consumers again.

Validation completed on 2026-08-28:

- Fresh SQLite migration profile: Guides on; all legacy capabilities off
- Upgraded SQLite migration profile: all existing capabilities remain on
- Fresh PostgreSQL 16 migration profile: Guides on; all legacy capabilities off
- Upgraded PostgreSQL 16 migration profile: all existing capabilities remain on
- Capability service, public configuration response, fallback, override, and
  route-policy tests: passed
- Full backend suite: 2,661 passed and 16 skipped by existing upstream markers
- Python lint and type check: 478 source files passed
- Frontend ESLint: passed
- Full frontend suite: 30 files and 286 tests passed
- Nuxt production build: passed
- Browser fresh-install check: only Guides remained in primary navigation; the
  Recipe create menu and favorites link were absent
- Browser direct-route check: Recipe creation returned to Guides, and disabled
  meal-planning and shopping-list pages returned to the application landing
- Browser upgraded-install check: all legacy navigation returned after the
  persisted compatibility profile was restored
- A synthetic merge with upstream `mealie-next` at
  `1ff92450a32cbe7edc3a25792a88208e84099788` completed without conflicts;
  the fork was 11 commits ahead and 28 commits behind at the checkpoint

## Product Slice 8 — Hearth identity and Guide-first landing (complete)

Included:

- A small typed brand configuration with Hearth name, short name, and product
  description, exposed through the existing public and admin app-info responses
- Optional `HEARTH_BRAND_NAME`, `HEARTH_BRAND_SHORT_NAME`, and
  `HEARTH_BRAND_DESCRIPTION` operator overrides
- Centralized frontend brand defaults and a composable used by shared product
  chrome instead of scattering new literal names through components
- Hearth identity on the browser title, metadata, application header, footer,
  sign-in, registration, and first-run setup screens
- A simple open-book Hearth mark used by application chrome and install metadata
- A warm terracotta, sage, and ochre default palette through Mealie's existing
  theme configuration seam; all existing theme environment overrides remain
  valid
- A versioned theme request that bypasses the week-long cached Mealie palette
  immediately after an upgrade
- A Hearth PWA manifest that removes stale Recipe screenshots and only exposes
  Recipe import, meal-planning, and shopping-list actions when their persisted
  capabilities are enabled
- A prominent search-first Guide library header, followed by secondary browse,
  filter, create, and export controls
- No changes to Python package names, API paths, authentication identifiers,
  data directories, database tables, or Mealie-compatible environment names

This is intentionally a shallow brand layer. References that describe retained
Mealie compatibility features, migrations, APIs, or upstream announcements are
not rewritten. A broader wording and notification audit remains a separate
Phase 5 task.

Validation completed on 2026-08-28:

- Typed public and admin brand response tests: passed
- Fresh and legacy-enabled manifest behavior tests: passed
- Branding environment override test: passed
- Full backend suite: 2,664 passed and 16 skipped by existing upstream markers
- Python lint and type check: 479 source files passed
- Frontend ESLint: passed
- Full frontend suite: 30 files and 286 tests passed
- Nuxt production build and PWA generation: passed
- Browser title and shared header both displayed Hearth
- Browser upgrade check: the versioned theme request immediately loaded the new
  Hearth palette instead of the previously cached Mealie colors
- Browser Guide landing check: search was the primary action and returned only
  matching Guide cards for a realistic `router` query
- A synthetic merge with upstream `mealie-next` at
  `2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` completed without conflicts;
  the fork was 12 commits ahead and 29 commits behind at the checkpoint

## Product Slice 9 — Responsive Guide reader and print layout (complete)

Included:

- Extract the read-only Guide presentation from the route page into one
  Guide-domain component while leaving loading, editing, saving, and deletion
  orchestration in the page
- Give safety callouts full-width priority before procedural content
- Present requirements and notes as supporting context beside steps on wide
  screens and before steps on narrow screens
- Turn each step into a clearly numbered reading block with tips, images,
  captions, and sensible page-break behavior
- Add a visible print action that uses the browser's native print workflow
- Add print-only rules for paper margins, readable typography, flattened cards,
  visible source URLs, restrained images, and avoided breaks inside steps and
  safety callouts
- Preserve the existing Guide API, schema, media endpoints, editor, and saved
  data shape

Validation completed on 2026-08-28:

- Guide reader helper tests: passed
- Frontend ESLint: passed
- Full frontend suite: 31 files and 289 tests passed
- Nuxt production build: passed
- Wide browser check: the seeded washing-machine Guide presents safety first,
  a sticky supporting column, and readable numbered steps at 1280 x 900
- Phone-width browser check: requirements and notes move before steps and the
  reader remains usable at 390 x 844
- Semantic browser check: one labelled article, ordered heading levels, safety
  before steps, and complementary requirements and notes were present
- Print-tree check: all 5 steps, 2 figures, 2 references, 2 related Guides, and
  the print footer remained present with page and break-control rules
- Edit and cancel interaction check: the existing editor opened and returned to
  the reader without changing saved data; delete permission handling is unchanged
- No backend API, schema, database migration, or saved Guide shape changed
- A synthetic merge with upstream `mealie-next` at
  `2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` completed without conflicts;
  the fork was 13 commits ahead and 29 commits behind at the checkpoint

## Product Slice 10 — Fresh-mode wording and settings isolation (complete)

Included:

- A Guide-first default landing fallback that ignores stored Recipe, meal-plan,
  or shopping-list preferences when those capabilities are disabled
- A four-step fresh-install setup flow that omits Recipe privacy, seed-data, and
  AI-provider configuration while retaining the complete upgraded flow
- Capability-aware profile, group, household, notifier, webhook, migration,
  data-management, administrator-debug, maintenance, backup, and statistics UI
- Direct-route guards for legacy-only shared settings so hidden links cannot be
  recovered by typing their URLs
- Hearth-branded OpenAPI metadata, SMTP sender default, English email subjects,
  and a text-based email header without the remote Mealie banner asset
- Hearth source and explicit Mealie-upstream attribution on sign-in and in
  transactional email footers
- Generic fresh-facing account, backup, language, setup, and administration
  wording; Mealie remains named where it identifies upstream compatibility,
  authentication, imports, or retained Recipe behavior
- No backend legacy API removal, package rename, database migration, or changes
  to persisted Guide data

Validation completed on 2026-08-28:

- Capability route and default-activity tests: passed
- Email rendering, branding configuration, and OpenAPI metadata tests: passed
- Frontend ESLint: passed
- Full frontend suite: 32 files and 297 tests passed
- Nuxt production build and PWA generation: passed
- Python lint and type check: 479 source files passed
- Full backend suite: 2,664 passed and 16 skipped by existing upstream markers
- Fresh browser check: primary navigation contained Guides and Settings only;
  profile/settings contained no Recipe-era cards; site statistics omitted
  Recipe counts; administrator debug navigation was absent
- Fresh setup browser check: Start, Account Details, Summary, and Setup Complete
  were the only steps; valid account details advanced directly to Summary
- Fresh direct-route browser check: data management, migrations, household
  preferences, notifiers, webhooks, and administrator Recipe debugging returned
  safely to the user profile
- Upgraded browser check: Recipe statistics, Cookbooks, household settings,
  notifiers, data management, migrations, full setup, and direct legacy routes
  all remained available
- The local development capability profile was restored to upgraded mode after
  testing; seeded Guides and application data were not changed
- A synthetic merge with upstream `mealie-next` at
  `2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` completed without conflicts;
  the fork was 14 commits ahead and 29 commits behind at the checkpoint

## Product Slice 11 — Accessibility, reflow, and measured performance (complete)

Included:

- A shared skip link and focusable main-content target across default, admin,
  basic, and blank layouts
- Correct document language and text direction derived from the active locale
- Visible keyboard focus and reduced-motion behavior at the shared stylesheet
  layer
- Accessible names and state for navigation, Guide search, profile, mobile,
  setup-stepper, loading, result-count, empty, error, retry, edit, and print
  controls
- Semantic Guide library search with clear-filter recovery, differentiated
  empty states, and stale-result removal after failures
- Guide reader, editor, media controls, setup, and shared navigation reflow at
  a 320-pixel viewport without horizontal scrolling or clipped actions
- Removal of editor autofocus and positive result tabindex values so native
  keyboard and phone behavior remains predictable
- Focused component and locale-head tests without adding a parallel component
  system or altering the Guide API, schema, or stored data

Validation completed on 2026-08-28:

- Frontend ESLint: passed
- Full frontend suite: 33 files and 299 tests passed
- Nuxt production build and PWA generation: passed
- Guide backend integration suite: 11 passed
- Fresh-install browser check: Guide-only navigation, four-step setup,
  accessible control names, loading and recovery states, and 320-pixel reflow
  passed
- Upgraded browser check: Recipes, Guides, Meal Planner, and Shopping Lists
  remained available and the complete six-step setup remained intact
- Guide library search check: a no-match query produced a specific empty state
  and Clear filters restored all 15 seeded Guides
- Semantic browser check: the document reported `en-US` and left-to-right
  direction; layouts exposed a first skip link and named main region; Guide
  list, create, edit, and reader pages each retained a clear primary heading
- Phone-width browser check: Guide library, reader, editor, and setup matched
  their viewport width at 320 pixels with no horizontal overflow
- Measured production Guide JavaScript remained small: library 3.9 KB, reader
  4.2 KB, editor 4.9 KB, and search dialog 4.1 KB compressed. The larger shared
  Nuxt/Vuetify chunk is upstream platform code, so no speculative Guide-specific
  splitting or shared-framework rewrite was introduced
- The local development capability profile was restored to upgraded mode after
  testing; seeded Guides and application data were not changed
- A synthetic merge with upstream `mealie-next` at
  `2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` completed without conflicts;
  the fork was 17 commits ahead and 29 commits behind at the checkpoint

## Product Slice 12C — Guide library and search (complete)

Included:

- Replaced the large promotional Guide hero with a compact, search-first
  library heading and one dominant search form
- Kept result count, loading, failure, retry, and no-result recovery directly
  beside the search that caused them
- Moved type, difficulty, frequency, category, and tag filters behind one
  progressively disclosed control
- Added an active-filter count, visible removable filter values, and a clear
  recovery path without making filters permanent navigation
- Serialized valid search and filter state into the existing Guide URL so a
  result set survives refresh, back/forward navigation, and sharing; invalid
  select values are removed while unrelated URL state is preserved
- Kept advanced choices as drafts until Done is selected, and prevented a
  slower earlier request from replacing a newer result set
- Simplified Guide cards to recognition media, title, outcome, classification,
  at most two task details, and review state
- Reduced the existing header Guide search to its compact shortcut on the
  library page, while retaining the full global search affordance everywhere
  else
- Preserved the Guide API, generated types, saved data, current routes, seeded
  content, and upgraded Mealie navigation

Validation completed on 2026-08-28:

- Frontend ESLint: passed
- Full frontend suite: 34 files and 305 tests passed
- New URL, filter-state, and request-ordering tests: 6 passed, including
  malformed-query recovery and an out-of-order response
- Nuxt production build and PWA generation: passed
- Browser search check: `router reset` produced the correct router Guide first
  and wrote the search to the URL
- Browser no-result check: a no-match query displayed the local empty state;
  Clear filters restored all 15 seeded Guides and the clean library URL
- Browser filter check: `type=cleaning` restored four matching Guides, exposed
  one active filter with a specific accessible remove label, and clearing it
  restored all Guides
- Browser filter-draft check: closing the panel discarded unapplied type and
  difficulty choices; selecting Done committed the choice and updated the URL
- Browser malformed-link check: invalid type and difficulty values were
  removed while an unrelated query value was retained
- Responsive browser check: the library reflowed at 1280, 390, and 320 pixels;
  the first Guide began in the first phone screen and no control was clipped
- Light and dark browser checks passed for search, cards, filters, active
  states, and no-result recovery
- Only one shared Mealie UI file was touched: the header condition that chooses
  the existing compact or full Guide-search trigger. All other production logic
  remains Guide-owned
- A synthetic merge with upstream `mealie-next` at
  `2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` completed without conflicts;
  the fork was 28 commits ahead and 29 commits behind at the checkpoint

## Product Slice 12D–12H — Complete Guide experience (implementation complete)

Included:

- Rebuilt the Guide reader around outcome, trust, safety, preparation, and
  procedure, with secondary knowledge moved below the active task
- Rebuilt authoring around essentials, safety/preparation, and steps, with one
  semantic disclosure for classification, upkeep, relations, and references
- Added explicit unchanged, unsaved, saving, and failed editor states without
  changing the Guide API, schema, media, or ordering contract
- Applied the approved warm-neutral system-font foundation to the shared shell,
  including household context, focused creation, theme/search actions, spaced
  navigation states, profile placement, and a three-action phone navigation
- Kept the complete upgraded Mealie navigation and routes while making fresh
  Hearth setup and navigation Guide-first
- Added the reduced-motion, focus, contrast, dark-theme, phone, print, missing
  media, stale review, failure-recovery, and semantic detail pass

Validation completed on 2026-08-28:

- Frontend ESLint and all 35 frontend test files / 311 tests passed
- Guide editor helper tests passed and cover save-state precedence, dirty
  detection, discard confirmation, duplicate saves, and in-flight navigation
- Nuxt static production build and PWA generation passed without a new font or
  dependency; Guide reader and editor CSS remained route-scoped
- Fourteen relevant backend Guide CRUD and capability-profile tests passed
- Desktop and 320-pixel library, reader, and editor checks passed in light and
  dark themes, with no document overflow
- Firefox loaded the library, reader, and editor without the earlier
  `$globals` failure; the editor remained usable at a real 200% Firefox zoom
  and the browser was restored to 100% afterwards
- Semantic inspection found one main region, named navigation, one H1 per task,
  ordered H2/H3 content, no unnamed buttons or links, and meaningful Guide
  media alternatives
- Light/dark body, muted, and primary text pairs all measured at or above 5.12:1
- Upgraded Recipes, Recipe Finder, Guides, Meal Planner, Shopping Lists,
  Timeline, Cookbooks, Organizers, announcements, settings, and profile links
  remained present
- The final upstream merge and fork counts are recorded in
  [`fork-delta.md`](fork-delta.md)

Rollout gate:

- Engineering is complete and suitable for controlled trials
- Broad rollout remains blocked only by the five independent household-user
  sessions and thresholds in [`ui-ux-assumptions.md`](ui-ux-assumptions.md)

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
- QR codes; they remain a final optional enhancement after the core release

## Taxonomy strategy

Use the existing group-scoped Guide tags to test additional ways of organizing
Guides before introducing more database entities. A short namespace keeps these
experimental dimensions recognizable without changing how ordinary tags work:

- `home: Main`, `home: Rental Apartment`, or `home: Parents' House`
- `space: Kitchen`, `space: Bathroom`, or `space: Garden`
- ordinary descriptive tags such as `monthly`, `outdoor`, or `rental-safe`

Category remains the Guide's primary subject classification, such as Appliance
Care or Home Maintenance. Mealie Household remains an ownership and access
boundary; it should not represent a physical property unless that property
genuinely needs separate users or permissions.

Deferred taxonomy scope:

- Consider first-class Homes when users need dedicated property filters,
  defaults, or an explicit “applies everywhere” state. The deferred model,
  trigger, permissions, migration, and UI seams are defined in the
  [Future Homes Plan](future-homes.md).
- Consider Spaces when property-specific room or area browsing becomes useful.
- Consider Assets or Equipment when Guides need to attach to individual models,
  serial numbers, service history, or manuals.
- Consider custom taxonomy definitions only after multiple recurring dimensions
  demonstrate the same editing, filtering, and permission needs.
- Keep future terms group-scoped and Guide relationships many-to-many. Decide
  hierarchy, inheritance, and namespaced-tag migration only when real usage
  establishes the required shape.

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

### Phase 6 — Upgrade, compatibility, and release hardening

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

### Phase 7 — Completion and sustainable maintenance

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

Core-release completion criteria:

- The complete core Guide product scope is available and documented; QR codes
  are not a release requirement.
- Recipe-only functionality is absent from the default Hearth experience.
- No destructive Recipe data migration is required for ordinary upgrades.
- Hearth-owned code is concentrated in Guide modules and documented shallow
  integration points.
- A maintainer can adopt a new Mealie release using the runbook without
  rediscovering the fork architecture.
- CI continuously validates Hearth behavior and retained upstream behavior.
- The release is reproducible from the tagged source.

### Phase 8 — Optional QR codes (final planned enhancement)

Goal: add safe, durable Guide QR access only after the core Hearth release is
complete and real usage shows that stickers or scan-to-open access are useful.

This phase is optional. Deferring or removing it does not make the core Hearth
release incomplete.

Design rules:

- QR code represents a stable URL, not stored Guide content.
- Use immutable Guide ID in URL resolution; slug is cosmetic.
- Generate SVG and PNG on demand.
- Authentication is required by default.
- Public access uses a separate, revocable, optionally expiring share token.
- Never place bearer tokens or household secrets in QR payloads.
- Deleted, private, expired, and revoked Guides have deliberate landing states.

Tasks:

- Confirm a recurring real-world need for QR access before implementation.
- Add a domain-neutral QR renderer.
- Add authenticated Guide QR endpoints.
- Add Guide share-token tables and management endpoints only if public QR
  access is separately approved.
- Add download and print-sticker UI.
- Test scanning, URL changes, token revocation, and unauthorized access.

Exit criteria:

- The usage trigger and intended sticker or scan workflow are documented.
- Printed QR remains valid after Guide title/slug changes.
- Revocation works immediately when public access is included.
- QR output is legible at intended sticker sizes.
- QR implementation is contained in Guide and shared utility modules rather
  than modifying Recipe sharing behavior.
- A phase-end upstream merge checkpoint passes.

Implementation sequence:

1. Confirm the usage trigger and access policy.
2. Stable Guide URL resolution.
3. Domain-neutral QR rendering utility.
4. Authenticated download endpoints and UI.
5. Optional Guide-specific public share tokens.
6. Sticker print layouts and scan tests.
7. Security and revocation tests.
8. Phase-end upstream merge checkpoint.

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
| 2026-08-26 | Use tags to test additional taxonomies | Avoid premature entities while allowing homes, spaces, and other dimensions to emerge from use |
| 2026-08-28 | Persist a server-wide fresh-or-upgraded capability profile | Give new Hearth installs a Guide-first product while preserving all legacy Mealie entry points on upgrade |
| 2026-08-28 | Print the responsive Guide reader directly | Keep one presentation model and use native browser printing instead of adding a PDF service |
| 2026-08-28 | Gate shared legacy settings instead of deleting them | Keep fresh Hearth focused while allowing upgraded installations and upstream tests to retain complete Mealie behavior |
| 2026-08-28 | Run a whole-product UI/UX audit after Slice 11 | Audit stable, accessible, responsive core flows before another major feature expands the interface |
| 2026-08-28 | Keep current Guide route chunks after measuring them | The four main Guide flows are only 3.9–4.9 KB compressed; changing shared Nuxt/Vuetify loading would add upstream merge risk without a demonstrated Guide performance problem |
| 2026-08-28 | Plan Home separately from Mealie Household | Preserve Mealie's people and permission boundary while reserving an additive, group-scoped physical-property model only when real multi-home use emerges |
| 2026-08-28 | Keep Slice 12 foundations Guide-scoped and system-font based | Improve the core Guide experience without replacing Mealie's frontend foundations or adding a font and theme migration |
| 2026-08-28 | Make Guide library state URL-addressable | Preserve search and filters across refresh and sharing without changing the Guide API or router shape |
| 2026-08-29 | Move QR codes to the final optional phase | The core household Guide product and first release do not depend on QR access; compatibility and release readiness provide more immediate value |

## Immediate next action

Do not begin another implementation slice until it is approved. The next
planned slice should close the remaining foundation and release-readiness work:
Guide event registration, operator compatibility and rollback guidance, and
the Phase 5 upstream merge checkpoint. Phase 6 then performs the complete
upgrade and release-hardening matrix. QR codes remain the final optional Phase
8 enhancement and do not block the core release.
