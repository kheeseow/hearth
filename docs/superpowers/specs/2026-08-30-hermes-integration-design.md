# Product Slice 14: Hermes Integration Design

## Outcome

Hermes can use Hearth as the household Guide library without a person entering
Guides one at a time. It can search and read Guides, create complete Guides in
batches, update existing Guides, attach available images, and delete a Guide
only after explicit confirmation.

## Approved product decisions

- Write access is available at launch; this is not a read-only trial.
- Batch creation is the primary write path because Hearth may start empty.
- Deletion always uses a two-step confirmation flow.
- Duplicate protection skips an exact normalized title match by default and
  reports the existing Guide rather than creating another copy.
- One failed item does not cancel an otherwise valid batch. Results identify
  every created, skipped, and failed item.
- Hermes uses Hearth's existing authenticated REST API. A separate MCP server
  would duplicate authentication, validation, and transport without adding a
  second known consumer.
- The integration is additive. It does not change Recipe tables, remove Mealie
  routes, or create a competing Hearth API.

## System boundary

The implementation belongs in the Hermes deployment repository as a standalone
`meg-hearth` plugin. Hearth remains the source of truth for validation,
household scoping, slugs, category and tag creation, related Guide rules, media
processing, and lifecycle notifications.

The plugin reads two runtime settings:

- `HEARTH_URL`: the reachable Hearth origin, without a trailing slash.
- `HEARTH_TOKEN`: a long-lived bearer token issued to a dedicated Hearth user.

The token inherits that user's household and permissions. Hearth currently has
no per-token scopes, so the dedicated user is the security boundary. The token
must never be logged or returned by a tool.

## Hermes tools

### `hearth_search_guides`

Passes text and supported Guide filters to `GET /api/guides`. Returns Hearth's
pagination response with compact Guide summaries.

### `hearth_get_guide`

Accepts a Guide slug or UUID and calls `GET /api/guides/{slug_or_id}`. Returns
the complete Guide, including category, tags, requirements, callouts, steps,
sources, related Guides, and review date.

### `hearth_create_guides`

Accepts `guides`, an array of 1 to 50 complete Guide candidates. Each candidate
uses Hearth's camel-case API fields and may additionally contain:

- `coverImageUrl`
- per-step `images`, each with `url`, optional `caption`, and optional `altText`

For each candidate the plugin:

1. validates the title and step/image wrapper shape;
2. searches for an exact title after Unicode normalization, whitespace
   collapsing, and case folding;
3. skips a duplicate unless `duplicatePolicy` is `create`;
4. creates the Guide through `POST /api/guides`;
5. optionally downloads and uploads the cover and step images; and
6. reports the created Guide even when a later image attachment fails.

Batch execution is sequential and independent. This keeps load predictable and
produces a truthful item-level result instead of pretending the remote API can
provide a transaction across multiple Guides.

### `hearth_update_guide`

Accepts a slug or UUID and a non-empty `changes` object. It sends only the
provided Hearth fields to `PATCH /api/guides/{slug_or_id}`. Optional cover and
step images use the same post-write attachment path as creation. Existing
fields are not silently replaced with defaults.

### `hearth_delete_guide`

Without `confirm: true`, fetches the Guide and returns a pending-confirmation
result naming the exact Guide. With `confirm: true`, deletes it through
`DELETE /api/guides/{slug_or_id}` and reports the deleted identity.

## Image safety

Only `http` and `https` image URLs are accepted. Redirects are limited, DNS is
resolved before download, and loopback, private, link-local, multicast,
reserved, and unspecified addresses are rejected. The response must be an
image and must not exceed 10 MiB. Hearth remains responsible for decoding and
normalizing the image. Image failures are isolated to the relevant Guide and
are clearly reported.

## Error and result contract

- Authentication and permission failures use plain messages that name the
  configuration or permission problem without exposing credentials.
- Validation errors from Hearth are preserved in concise form.
- Bulk results contain `created`, `skipped`, and `failed` counts plus ordered
  item results with the input title and outcome.
- A successful Guide creation followed by a media failure is reported as
  `created_with_media_errors`, never as an entirely failed creation.

## Deployment and verification

The plugin is covered by standalone unit tests with a fake Hermes registry and
stubbed HTTP calls, matching the existing Hermes plugin test style. A contract
test in Hearth protects the exact routes and field aliases used by the plugin.

Production activation requires a deployed Hearth URL reachable from the Hermes
NAS and a dedicated bearer token. Plugin files and configuration are backed up
before any NAS change. The live token is supplied through the existing secret
environment mechanism and is never committed.

## Deferred work

- No general-purpose Hearth MCP server until another client demonstrates a
  concrete need for shared discovery or transport.
- No token-scope system in Slice 14; use a dedicated least-privilege user.
- No public Guide sharing or QR behavior; QR remains the final optional slice.
