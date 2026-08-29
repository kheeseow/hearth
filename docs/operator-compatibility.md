# Hearth Operator Compatibility and Rollback

Hearth keeps Mealie's application structure, API paths, database tables, and
legacy Recipe code so an existing Mealie installation can be upgraded without
discarding its data. Legacy features may be hidden in a fresh Hearth profile,
but their code and stored data are retained.

## Installation profiles

The `app_capabilities` database row records the installation profile when its
migration first runs:

- **Fresh Hearth database:** Guides are enabled. Recipes, meal planning,
  shopping lists, and nutrition are disabled in the user interface.
- **Existing Mealie database:** if the database already has a user, Guides and
  all legacy features are enabled initially.
- **Missing capability row:** Hearth fails open and exposes the legacy features
  rather than unexpectedly hiding access during an incomplete upgrade.

`HEARTH_LEGACY_FEATURES` has the following precedence:

| Value | Result |
|---|---|
| Unset | Use the profile stored in `app_capabilities`. |
| `true` | Enable Recipes, meal planning, shopping lists, and nutrition. |
| `false` | Disable those legacy features in the Hearth interface. |

The override does not disable Guides and does not alter or delete legacy data.
Restart the application after changing it because environment settings are
loaded when the process starts.

## Supported ports and configuration

Production remains Mealie-compatible: the single container serves the API and
the built frontend on container port `9000`. The repository's production
compose example maps host port `9091` to container port `9000`; a different
host port is safe, but `API_PORT` should remain `9000` inside Docker. Set
`BASE_URL` to the externally reachable Hearth URL.

Local development has two supported pairs:

| Workflow | Frontend | Backend | Commands |
|---|---:|---:|---|
| Standard Mealie development | `3000` | `9000` | `task ui` and `task py` |
| Hearth collision-free development | `3010` | `9010` | `COREPACK_ENABLE_PROJECT_SPEC=0 task hearth:ui` and `task hearth:py` |

The Hearth tasks set `API_URL=http://localhost:9010` for Nuxt and
`BASE_URL=http://localhost:3010` for the backend. The standard Taskfile values
remain unchanged for upstream compatibility.

SQLite remains the default (`DB_ENGINE=sqlite`). PostgreSQL remains supported
with `DB_ENGINE=postgres` and the existing `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_SERVER`, `POSTGRES_PORT`, and `POSTGRES_DB`
settings. Keep the container data mount at `/app/data/`: Guide media is stored
under `/app/data/guides/`, alongside Mealie's retained data directories.

## Upgrade procedure

1. Read the Hearth and adopted Mealie release notes for every version being
   crossed.
2. Create a full backup from **Settings → Admin Settings → Backups**
   (`/admin/backups`), download the ZIP, and store it outside the application
   server or mounted data volume.
3. Also take an infrastructure backup:
   - For SQLite, stop the container and copy the complete `/app/data/` volume.
   - For PostgreSQL, back up the PostgreSQL database and `/app/data/` volume as
     one recovery point.
4. Record the current application image or commit and the current
   `HEARTH_LEGACY_FEATURES`, database, `BASE_URL`, and port configuration.
5. Deploy the new application and allow its normal Alembic startup migrations
   to finish. Do not interrupt the process or run migrations concurrently.
6. Validate the result before allowing normal use:
   - `GET /api/app/about` reports the expected `capabilities` values.
   - `/g/<group-slug>/guides` opens and existing Guides can be read.
   - Guide cover and step images load.
   - A Guide can be created, edited, exported, and found through search.
   - On an upgraded installation, retained Recipe and related screens remain
     available when legacy features are enabled.
   - A new full backup can be created and downloaded.

The application backup contains the database as `database.json` and Guide
media beneath `data/guides/`. Keep the pre-upgrade backup until the upgraded
installation has passed validation and a post-upgrade backup has been tested.

## Rollback procedure

Changing `HEARTH_LEGACY_FEATURES=true` is the quickest compatibility fallback
when the problem is only that a retained legacy screen is hidden. It is not an
application or database rollback.

For an application rollback:

1. Stop Hearth so no writes occur during recovery.
2. Preserve the failed upgraded state separately for diagnosis.
3. If the release notes explicitly confirm backward schema compatibility,
   redeploy the previously recorded image against the existing database.
4. Otherwise, restore the pre-upgrade database and `/app/data/` snapshot, then
   redeploy the matching previous image.
5. Start Hearth and repeat the validation checks above before reopening it to
   users.

The integrated ZIP restore requires a backup whose schema version matches the
running application. PostgreSQL ZIP restoration also requires the configured
database user to be a PostgreSQL superuser for the duration of the restore, as
documented in [Backups and restoring](docs/documentation/getting-started/usage/backups-and-restoring.md).

Alembic `downgrade` is a development and migration-verification tool, not the
normal production rollback path. Downgrading before a Guide migration can drop
Guide columns or tables and therefore destroy Guide records or relationships.
Never use schema downgrade as a substitute for restoring a verified backup.

## Retained Recipe boundary

Hearth does not remove Recipe models, schemas, services, repositories, routes,
tables, media, or tests. Fresh-install capability flags hide legacy workflows;
they do not rewrite the database. This keeps upgraded installations usable and
limits divergence when adopting later Mealie releases.

Guide production modules must stay independent of Recipe-domain imports in both
the backend and frontend. Run the repeatable boundary check with:

```bash
uv run pytest tests/unit_tests/test_guide_recipe_import_boundary.py -q
```

The check automatically discovers Guide-named production files under `mealie/`
and `frontend/app/`, so new Guide modules are covered without updating an
allowlist.
