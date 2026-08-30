# Hermes integration

Hermes uses Hearth's authenticated Guide API through the standalone
`meg-hearth` plugin. Hearth remains the source of truth for Guide validation,
household boundaries, media processing, and events; Hermes does not need an
MCP server or a separate database.

## What it can do

The plugin provides `hearth_search_guides`, `hearth_get_guide`,
`hearth_create_guides`, `hearth_update_guide`, and `hearth_delete_guide`.
Creation accepts batches of 1 to 50 Guides. By default, it skips an exact
normalized title match; pass the plugin's `duplicatePolicy: "create"` only
when a second copy is intentional. Delete is a two-step flow: Hermes first
shows the matching Guide, then sends the deletion only with `confirm: true`.

Cover and step images are optional post-write attachments. A successfully
created Guide remains created if an image cannot be attached, and the result
reports the media error. Image URLs must be public `http` or `https` images;
the plugin rejects private, local, oversized, and non-image downloads.

## One-time Hearth setup

1. Create a dedicated Hearth user for Hermes and place it in the household
   whose Guides Hermes should manage. Do not reuse a personal administrator
   account.
2. In that user's profile, open **API Tokens** (`/user/profile/api-tokens`) and
   create a long-lived token. Copy it only into the Hermes secret environment;
   it is shown once.
3. When creating a token through the API, set `integrationId` to `hermes`.
   This is event attribution context for changes made through that token, not a
   permission scope. The profile UI may use Hearth's default value when it
   does not expose that field.

Tokens inherit the user's group, household, and permissions. Hearth has no
per-token scopes. The dedicated user is therefore the security boundary: it
must belong to the target household, and it can modify or delete only Guides
owned by that household. Reading remains group-scoped. Revoke this token from
the same API Tokens screen if it is exposed or no longer needed.

## Hermes configuration

On the Hermes host, set these values in the deployment's ignored `.env` file:

```dotenv
HEARTH_URL=
HEARTH_TOKEN=
```

`HEARTH_URL` is the base address Hermes can reach, with no trailing slash or
`/api` suffix. `HEARTH_TOKEN` is the dedicated user's token. Never commit,
paste into chat, or put a real token in `config.yaml`. The checked-in
`.env.example` documents the variables, and `config/config.yaml.example`
enables both the `hearth` toolset and `meg-hearth` plugin for the main profile.
Residence and the isolated Mac worker configuration are intentionally not
changed.

For an internal deployment, the gateway container must be able to resolve and
connect to the chosen Hearth address. A public URL is acceptable only if its
network and TLS policy permit the NAS gateway to reach it. Check that route
from the gateway before activating the plugin; a browser check from another
machine is not sufficient.

After adding the environment values and configuration on a future deployment,
recreate the gateway so it receives the new environment. Do not activate from
this repository alone.

## Smoke test

After the gateway is running with reachable Hearth credentials:

1. Ask Hermes to search Guides, for example: “Search Hearth for smoke alarm.”
2. Ask it to fetch a returned Guide by slug.
3. Create a harmless test Guide, then patch it and attach a small public test
   image if media is in scope.
4. Ask Hermes to delete the test Guide and verify that it requests
   confirmation before the second call.
5. Confirm the token's user and `integrationId` are visible as expected in
   Hearth's resulting activity or notifications.

Typical failures are direct: 401 means the token is wrong or revoked; 403
means the dedicated user lacks the necessary household access; and connection
errors mean the gateway cannot reach `HEARTH_URL`.

## Rollback

To stop access immediately, remove `HEARTH_URL` or `HEARTH_TOKEN` from the
gateway environment and recreate the gateway. For a stronger cutoff, revoke
the Hearth API token. To fully remove the integration, remove `hearth` from
the main profile toolsets and `meg-hearth` from enabled plugins, then recreate
the gateway. These steps do not delete Guides already created in Hearth.
