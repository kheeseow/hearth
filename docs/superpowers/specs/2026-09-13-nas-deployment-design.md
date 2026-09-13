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
- Hearth owns its Docker network and does not join another application's
  network. External clients reach it through the NAS endpoint on port `9091`.
- SQLite is the first production database. All application data, media, and
  the database persist under `/volume2/docker/hearth/data`.
- Legacy Recipe features remain hidden for the fresh Hearth installation via
  `HEARTH_LEGACY_FEATURES=false`; the underlying Mealie-compatible structures
  remain intact.

## Delivery

The public Hearth repository owns both workflows. It builds one Linux AMD64
production image in GitHub Actions and publishes immutable `nas-<commit>` and
moving `nas-latest` tags to GitHub Container Registry. Its manual production
workflow uses credentials stored only in Hearth to connect to the NAS. The NAS
pulls the requested Hearth commit through Git, then pulls its matching image.
No Hearth file, workflow, or credential is placed in another repository.

## First deployment

The workflow verifies that port `9091` is unused, updates the dedicated checkout
at `/volume2/docker/hearth/repo` to the requested commit, validates the Compose
file from that checkout, pulls the matching immutable image, and starts Hearth.
It waits for Docker health and checks `/api/app/about` through the NAS host port.

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

Once Hearth is healthy, a separate client application may be configured against
`http://jollyroger.lowpew.com:9091` using Hearth's documented API. Hearth does
not own or deploy that client's configuration.
