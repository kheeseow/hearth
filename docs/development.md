# Hearth Local Development

Hearth uses dedicated local ports so it can run alongside Olympus and other
projects:

- Frontend: `http://localhost:3010`
- Backend API: `http://localhost:9010`

Start the two processes in separate terminals:

```bash
task hearth:py
```

```bash
COREPACK_ENABLE_PROJECT_SPEC=0 task hearth:ui
```

After signing in, open Guides from the sidebar or use:

```text
http://localhost:3010/g/<your-group-slug>/guides
```

The original Mealie `task py` and `task ui` commands are intentionally left
unchanged to reduce friction when merging upstream changes.
