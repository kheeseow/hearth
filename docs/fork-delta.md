# Hearth Fork Delta

This file records the expected Hearth-owned paths and the small set of shared
Mealie files touched by Product Slice 1. Use it when reviewing upstream merges.

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
```

## Shared Mealie integration points

```text
Taskfile.yml                                      additive Hearth dev tasks only
mealie/db/models/_all_models.py                   model registration only
mealie/repos/repository_factory.py                repository registration only
mealie/routes/__init__.py                         router registration only
frontend/app/lib/api/client-user.ts               API client registration only
frontend/app/components/Layout/DefaultLayout.vue  Guide navigation only
frontend/app/components/Layout/LayoutParts/AppHeader.vue  Guide header search only
frontend/app/lang/messages/en-US.json             Guide strings only
frontend/app/lib/api/types/response.ts            generated output
tests/utils/api_routes/__init__.py                 generated output
```

## Additive migration

```text
mealie/alembic/versions/2026-08-25-10.42.23_39ee4257d98e_add_guides.py
```

The migration creates `guides` and `guide_steps`. It does not alter Recipe
tables. Its upgrade and downgrade paths have been exercised on fresh SQLite and
PostgreSQL 16 databases.

## Boundary rule

Guide-owned backend modules may import platform infrastructure, but must not
import Recipe models, schemas, repositories, routes, or services. The same
principle applies to Guide frontend domain components.
