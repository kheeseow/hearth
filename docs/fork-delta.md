# Hearth Fork Delta

This file records the expected Hearth-owned paths and the small set of shared
Mealie files touched by Product Slices 1 through 7. Use it when reviewing
upstream merges.

## Hearth-owned paths

```text
mealie/db/models/guide/
mealie/schema/guide/
mealie/services/guide/
mealie/routes/guide/
mealie/repos/repository_guides.py
tests/integration_tests/user_guide_tests/
frontend/app/components/Domain/Guide/
frontend/app/composables/guides/
frontend/app/lib/api/user/guides.ts
frontend/app/lib/api/types/guide.ts
frontend/app/pages/g/[groupSlug]/guides/
mealie/services/app_capabilities_service.py
frontend/app/composables/use-app-capabilities.ts
frontend/app/lib/app-capability-routes.ts
frontend/app/middleware/app-capabilities.global.ts
```

## Shared Mealie integration points

```text
.gitignore                                        local Guide media only
Taskfile.yml                                      additive Hearth dev tasks only
mealie/db/models/_all_models.py                   model registration only
mealie/repos/repository_factory.py                repository registration only
mealie/routes/__init__.py                         router registration only
mealie/core/settings/directories.py               Guide media directory only
mealie/core/settings/settings.py                  one optional Hearth compatibility override
mealie/db/models/server/                          additive capability profile only
mealie/schema/admin/about.py                      typed app capabilities only
mealie/routes/app/app_about.py                    capability response only
mealie/routes/admin/admin_about.py                capability response only
mealie/services/backups_v2/alchemy_exporter.py    Guide review-date restoration only
frontend/app/lib/api/client-user.ts               API client registration only
frontend/app/components/Layout/DefaultLayout.vue  capability-filtered navigation
frontend/app/components/Layout/LayoutParts/AppSidebar.vue  capability-filtered favorites link
frontend/app/components/Domain/Admin/Setup/EndPageContent.vue  Guide-first setup links
frontend/app/pages/user/profile/index.vue          capability-filtered Recipe cards
frontend/app/components/Layout/LayoutParts/AppHeader.vue  Guide header search only
frontend/app/lang/messages/en-US.json             Guide strings only
frontend/app/lib/api/types/admin.ts               generated capability output
frontend/app/lib/api/types/response.ts            generated output
tests/utils/api_routes/__init__.py                 generated output
```

## Additive migration

```text
mealie/alembic/versions/2026-08-25-10.42.23_39ee4257d98e_add_guides.py
mealie/alembic/versions/2026-08-26-11.26.02_e5564b5892ae_add_guide_classification_and_safety.py
mealie/alembic/versions/2026-08-26-15.57.59_de0599e50a71_add_guide_frequency_requirements_and_.py
mealie/alembic/versions/2026-08-27-14.10.45_f5ba4484ce44_add_guide_media.py
mealie/alembic/versions/2026-08-27-15.49.15_11a81b5bc6c5_add_guide_knowledge_metadata.py
mealie/alembic/versions/2026-08-27-22.54.52_ed9f015280d3_add_app_capabilities.py
```

The first migration creates `guides` and `guide_steps`. The second adds Guide
classification and timing columns plus `guide_categories`, `guide_tags`,
`guides_to_tags`, and `guide_callouts`. The third adds Guide frequency,
per-step tips, and the ordered `guide_requirements` table. The fourth adds a
nullable Guide cover-version column and the ordered `guide_step_images` table.
The fifth adds nullable notes and last-reviewed columns, the ordered
`guide_sources` table, and the directed `guide_relations` association table.
None alters Recipe tables. Upgrade and downgrade paths have been exercised on
fresh SQLite and PostgreSQL 16 databases.

The sixth migration adds a singleton, server-wide application-capability
profile. It initializes fresh databases with Guides only and databases with
existing users with every legacy capability preserved. It does not gate or
alter legacy backend data.

## Boundary rule

Guide-owned backend modules may import platform infrastructure, but must not
import Recipe models, schemas, repositories, routes, or services. The same
principle applies to Guide frontend domain components.
