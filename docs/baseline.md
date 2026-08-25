# Hearth Baseline

## Baseline identity

- Recorded: 2026-08-25 (Asia/Kuala_Lumpur)
- Upstream project: `mealie-recipes/mealie`
- Upstream release: `v3.24.0`
- Upstream commit: `2c04da733f88836f788234a4bf1127599fbc1294`
- Local branch: `hearth-main`
- Origin: `git@github.com:kheeseow/hearth.git`
- Upstream: `https://github.com/mealie-recipes/mealie.git`

This is the reference point for Hearth development. Guide work must remain
separable from the Recipe domain and should be checked against upstream at the
end of each implementation phase.

## Local toolchain

- macOS on Apple Silicon
- Python 3.12.12, managed by `uv`
- `uv` 0.10.0
- Node.js 22.23.1
- pnpm 11.23.0
- Task 3.53.1
- Docker 29.4.0

Task was installed through Homebrew because it was the only missing declared
development prerequisite.

## Setup result

Backend dependency setup succeeded using the committed `uv.lock`. Frontend
dependency setup succeeded using the committed `pnpm-lock.yaml` after applying
the environment workaround below. No upstream application source was changed
to make setup pass.

### Upstream pnpm declaration defect

The `v3.24.0` `frontend/package.json` declares this development package-manager
version:

```json
"devEngines": {
  "packageManager": {
    "name": "pnpm",
    "version": "3.24.0",
    "onFail": "warn"
  }
}
```

Corepack consequently attempts to download the nonexistent pnpm `3.24.0` and
the unmodified `task setup` command fails during `setup:ui`. The lockfile
declares pnpm `11.23.0`, which works.

Baseline workaround:

```bash
corepack prepare pnpm@11.23.0 --activate
COREPACK_ENABLE_PROJECT_SPEC=0 task setup:ui
```

Use `COREPACK_ENABLE_PROJECT_SPEC=0` for frontend Task commands until the
upstream declaration is corrected or Hearth deliberately carries a minimal
fix.

## SQLite smoke test

A fresh SQLite development database successfully:

- Connected
- Applied all Alembic migrations through the `v3.24.0` head
- Created the default group, household, and user
- Started FastAPI on port 9000
- Returned HTTP 200 from `/api/app/about`
- Returned HTTP 200 from `/api/app/about/startup-info`
- Shut down cleanly

The Nuxt development server successfully:

- Generated `.nuxt/tsconfig.json` using `pnpm exec nuxt prepare`
- Started on port 3000
- Returned HTTP 200 and the Mealie HTML shell from `/login`
- Shut down cleanly

On this machine, `127.0.0.1:3000` is already occupied by an OrbStack listener.
The Nuxt server binds to IPv6 localhost, so frontend smoke checks must use
`http://localhost:3000`, not `http://127.0.0.1:3000`.

## Baseline validation

### Backend

Command:

```bash
task py:test
```

Result:

- 2,644 passed
- 16 skipped by upstream markers
- 0 failed
- Duration: 11 minutes 36 seconds

The skipped tests are the explicitly marked long-running scraper/parser tests
and LDAP tests that require the CI LDAP service.

### Frontend

Preparation and test commands:

```bash
COREPACK_ENABLE_PROJECT_SPEC=0 pnpm exec nuxt prepare
COREPACK_ENABLE_PROJECT_SPEC=0 task ui:test
COREPACK_ENABLE_PROJECT_SPEC=0 task ui:lint
```

Result:

- 28 test files passed
- 274 tests passed
- 0 failed
- ESLint passed with zero warnings

The first frontend test attempt failed before test collection because the
generated `.nuxt/tsconfig.json` did not yet exist. After the standard Nuxt
prepare step, the unchanged suite passed.

Vitest emits a non-failing warning that `vitest.config.js` uses ESM syntax in a
file loaded as CommonJS. This is an upstream warning and is not a baseline
failure.

## Baseline conclusion

Mealie `v3.24.0` is a working Hearth foundation on SQLite. The backend and
frontend tests are green after environment preparation. The pnpm declaration
and missing automatic Nuxt preparation are documented baseline setup issues;
they are not Hearth regressions.

The next implementation milestone is the Phase 2 minimal Guide backend vertical
slice described in `docs/implementation-plan.md`.
