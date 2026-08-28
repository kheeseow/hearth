# Hearth Fork Delta

This file records the expected Hearth-owned paths and the small set of shared
Mealie files touched by Product Slices 1 through 12. Use it when reviewing
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
frontend/app/composables/use-default-activity.ts
mealie/core/settings/branding.py
frontend/app/lib/app-brand.ts
frontend/app/lib/guide-reader.ts
frontend/app/lib/guide-editor.ts
frontend/app/lib/locale-head.ts
frontend/app/plugins/i18n-head.client.ts
frontend/app/components/Layout/LayoutParts/AppSkipLink.vue
frontend/app/composables/use-app-brand.ts
frontend/public/icons/hearth-mark.svg
```

## Shared Mealie integration points

```text
.gitignore                                        local Guide media only
Taskfile.yml                                      additive Hearth dev tasks only
mealie/db/models/_all_models.py                   model registration only
mealie/repos/repository_factory.py                repository registration only
mealie/routes/__init__.py                         router registration only
mealie/core/settings/directories.py               Guide media directory only
mealie/core/settings/settings.py                  brand and capability settings registration only
mealie/app.py                                     branded API metadata only
mealie/core/settings/themes.py                    Hearth default palette only
mealie/db/models/server/                          additive capability profile only
mealie/schema/admin/about.py                      typed app capabilities only
mealie/routes/app/app_about.py                    capability response only
mealie/routes/admin/admin_about.py                capability response only
mealie/routes/spa/manifest.py                     branded, capability-aware install metadata
mealie/services/backups_v2/alchemy_exporter.py    Guide review-date restoration only
frontend/app/lib/api/client-user.ts               API client registration only
frontend/app/components/Layout/DefaultLayout.vue  route-preserving Hearth shell, capability-filtered navigation, phone navigation
frontend/app/layouts/basic.vue                    accessible main-content target only
frontend/app/layouts/blank.vue                    accessible main-content target only
frontend/app/components/Layout/LayoutParts/AppSidebar.vue  capability-safe navigation, Hearth identity, spaced settings/profile footer
frontend/app/components/Domain/Admin/Setup/EndPageContent.vue  Guide-first fresh setup action; upgraded setup retained
frontend/app/pages/admin/setup.vue                 capability-aware first-run steps
frontend/app/layouts/admin.vue                     capability-filtered Recipe debug links and accessible main target
frontend/app/pages/admin/site-settings.vue         capability-filtered Recipe statistics
frontend/app/pages/admin/maintenance/index.vue     capability-filtered Recipe maintenance
frontend/app/pages/admin/backups.vue               capability-filtered Recipe migration link
frontend/app/pages/group/index.vue                 capability-filtered Recipe AI settings
frontend/app/components/Domain/Group/GroupPreferencesEditor.vue  capability-filtered announcements
frontend/app/components/Domain/Household/HouseholdPreferencesEditor.vue  capability-filtered legacy preferences
frontend/app/pages/user/profile/index.vue          capability-filtered Recipe cards
frontend/app/pages/user/profile/edit.vue           Guide-first landing preference
frontend/app/composables/use-groups.ts             capability guard for Recipe AI preferences
frontend/app/components/Layout/LayoutParts/AppHeader.vue  Guide search, household context, theme/create actions, and Hearth identity
frontend/app/components/Layout/LayoutParts/AppFooter.vue  Hearth product identity only
frontend/app/components/global/AppLogo.vue         Hearth product mark only
frontend/app/pages/login.vue                       configured product name only
frontend/app/pages/register/index.vue              configured product name only
frontend/app/pages/admin/setup.vue                 configured product name only
frontend/app/plugins/app-info.client.ts            configured browser metadata only
frontend/app/plugins/theme.ts                      Hearth fallback palette and surface-role tokens only
frontend/app/assets/style-overrides.scss           small shared spacing, focus, surface, menu, and reduced-motion layer
frontend/nuxt.config.ts                            Hearth static metadata and theme defaults only
frontend/app/lang/messages/en-US.json             Guide and Hearth product strings only
mealie/lang/messages/en-US.json                    Hearth email wording only
mealie/services/email/email_service.py             centralized email brand rendering only
mealie/services/email/templates/default.html       Hearth email header and attribution only
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

## Slice 12 shared-shell rationale

Slice 12 intentionally exceeds the redesign plan's provisional three-file
shared-shell budget. Keeping the implementation close to Mealie was safer than
introducing a parallel layout or navigation stack:

| Shared file | Why a Guide-owned wrapper was insufficient | Compatibility rule |
|---|---|---|
| `DefaultLayout.vue` | It owns the existing drawer, route list, app bar, and page region. | Retain the layout, route builders, capability filters, and auth state; add only Hearth presentation and phone navigation. |
| `AppHeader.vue` | Global search, session actions, and responsive app-bar behavior already live here. | Preserve search and logout behavior; add context, theme, and Guide creation without new state. |
| `AppSidebar.vue` | Active navigation, settings, announcements, and profile are Mealie-owned shared behavior. | Preserve every link and menu; change order, spacing, identity, and profile placement only. |
| `theme.ts` | Vuetify's theme must know canvas, surface, ink, muted, and outline roles for both modes. | Keep the existing operator-provided action colors; add fallback surface roles only. |
| `style-overrides.scss` | Focus, menu spacing, radii, system typography, and reduced motion cross component boundaries. | Keep the layer small and declarative; no selector may hide a legacy workflow. |
| `EndPageContent.vue` | This is the existing capability-aware final setup step. | Fresh profiles lead with New guide; upgraded profiles keep Mealie migration and Recipe choices. |

The redesign did not replace Vuetify, duplicate routing, add a state store,
change an API, or hide upgraded routes. Review these seams as presentation
conflicts during upstream merges, not as a forked frontend architecture.

## Latest upstream checkpoint

On 2026-08-28, the current Hearth branch was checked against
`upstream/mealie-next` at
`2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` using Git's synthetic merge-tree
operation. It produced a merged tree without unresolved conflicts. At that
checkpoint Hearth was 29 commits ahead and 29 commits behind upstream. The
Slice 12 shared-shell seams listed above therefore remain review costs, but do
not currently prevent taking a Mealie update.
