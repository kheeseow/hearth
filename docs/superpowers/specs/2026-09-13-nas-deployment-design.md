# Hearth NAS Deployment Design

## Outcome

Run Hearth as a durable, browser-accessible application on Andrew's Synology
NAS without sharing a host port or lifecycle with Olympus or Hermes.

## Approved shape

- Hearth is a separate Docker Compose stack rooted at
  `/volume2/docker/hearth`.
- The production container remains Mealie-compatible and serves its bundled
  frontend and API on container port `9000`.
- NAS port `9091` maps to Hearth for browser access. Live inspection confirmed
  that Olympus already owns port `3010` and that `9091` is free.
- Hearth joins the existing external Docker network `meg_net`. Hermes reaches
  it by service name at `http://hearth:9000`, never through the host port.
- SQLite is the first production database. All application data, media, and
  the database persist under `/volume2/docker/hearth/data`.
- Legacy Recipe features remain hidden for the fresh Hearth installation via
  `HEARTH_LEGACY_FEATURES=false`; the underlying Mealie-compatible structures
  remain intact.

## Delivery

The public Hearth repository builds one Linux AMD64 production image in GitHub
Actions and publishes immutable `nas-<commit>` and moving `nas-latest` tags to
GitHub Container Registry. The private Hermes deployment repository owns a
manual NAS deployment workflow because it already holds the NAS/Tailscale
deployment credentials. That workflow manages only `/volume2/docker/hearth`
and the `hearth` container; it does not rewrite or restart Hermes, Residence,
the Mac worker, or Olympus.

## First deployment

The workflow verifies that `meg_net` exists and that port `9091` is unused,
backs up any existing Hearth compose file, stages the reviewed compose file,
pulls the requested image, and starts Hearth. It waits for Docker health and
checks `/api/app/about` through both the container and NAS host port.

The initial browser address is
`http://jollyroger.lowpew.com:9091`, intended for LAN/Tailscale access. A TLS
reverse proxy and public domain are deliberately deferred until the private
installation is working.

## Security and recovery

- No Hearth or Hermes token is stored in either repository or deployment
  workflow.
- New registrations are disabled. The built-in first administrator must change
  the default credentials immediately.
- The workflow will not replace an existing non-Hearth listener on port 9091.
- Existing Hearth compose configuration is copied to a timestamped backup
  before replacement.
- Persistent data is not deleted by deployment or rollback. Rolling back means
  selecting a previous immutable image tag and redeploying it; database
  downgrade compatibility must be checked before rolling back across a schema
  migration.

## Hermes activation after first login

Once Hearth is healthy, create a dedicated non-admin Hearth user and long-lived
API token. Then back up and update only the live main Hermes profile with
`HEARTH_URL=http://hearth:9000`, the token, the `hearth` toolset entries, and
the `meg-hearth` plugin. Recreate only the main gateway and run the Slice 14
read/write smoke tests. This credential step is separate because a token cannot
exist before Hearth's first login.
