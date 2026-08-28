# Future Homes Plan

## Status

Deferred. Hearth remains a single-home product for now.

This document reserves a clean path to multiple physical homes without
repurposing Mealie's existing Household model or adding speculative complexity
to the current Guide experience.

## Decision

Use these concepts consistently:

- **Mealie Household** remains a people, ownership, and permission boundary.
- **Home** will mean a physical property or place whose procedures a Guide may
  apply to.
- **Group** remains the broad sharing boundary inherited from Mealie.

Do not use Mealie Household to represent a physical home unless the people and
permission boundary genuinely matches that property. A user currently belongs
to one Mealie Household, so repurposing it would not naturally support one
person managing several physical homes.

The intended future relationship is:

```text
Group
├── Households     people, ownership, permissions
├── Homes          Main Home, Rental Apartment, Parents' House
└── Guides
    ├── applies to all Homes
    └── applies to one or more selected Homes
```

## Implementation trigger

Do not implement Homes merely because the model is plausible. Start the Home
slice when at least one of these becomes a recurring real need:

- A user repeatedly uses `home:` tags to separate two or more properties.
- Users need to browse or search Guides within a selected property.
- A Guide must explicitly apply everywhere or only at named properties.
- Property context must become a default during Guide creation.
- Property-specific rooms, assets, manuals, or maintenance history are blocked
  by the lack of a stable Home identifier.

One isolated request or one namespaced tag is not enough. The trigger should be
observed use, not architectural neatness.

## What to preserve now

Current design and implementation work should preserve these future seams
without building the feature:

1. Keep Guide URLs group-scoped and independent of Home identity.
2. Do not bake the phrase "single home" into Guide API contracts or component
   names.
3. Keep the library's context area capable of accepting a future selector, but
   show no selector while only one implicit Home exists.
4. Keep card metadata composable so a Home label can be added contextually
   without redesigning every card.
5. Keep Guide editor sections extensible so a future "Where this applies"
   control can sit with essential metadata.
6. Keep search and filter state serializable so a future Home filter can use a
   URL query parameter.
7. Continue using `home:` tags only as an explicit experiment, not as hidden
   foreign keys or permission controls.

These are interface and naming constraints, not requirements to add empty
tables, dormant feature flags, generic taxonomy engines, or unused abstractions.

## Future MVP scope

When the trigger is met, the smallest complete Home feature should include:

- Create, rename, order, and archive Homes.
- Let a Guide apply to every Home or to one or more selected Homes.
- Filter the Guide library by `All Homes` or one Home.
- Show Home context on Guide cards and readers only when it disambiguates the
  content.
- Add "Where this applies" to Guide creation and editing.
- Include Home names in relevant search behavior.
- Preserve Homes and Guide assignments in Guide export and full backups.
- Preserve stable Guide URLs when the selected Home changes.
- Archive Homes safely without deleting Guides.

## Future non-goals

The first Home slice should not include:

- Per-Home user membership or permissions.
- Postal addresses, coordinates, valuations, tenancy, or other sensitive
  property records.
- Rooms or Spaces.
- Assets, equipment inventories, serial numbers, or service history.
- Maintenance schedules or reminders.
- Separate copies of a Guide for every Home.
- Automatic conversion of Mealie Households into Homes.
- A generic custom-taxonomy builder.

## Proposed data shape

Use an additive, group-scoped domain parallel to Guide:

```text
homes
  id                 UUID primary key
  group_id           UUID foreign key, indexed
  name               display name
  normalized_name    group-unique normalized name
  position           stable display order
  archived_at        nullable timestamp
  created_at
  updated_at

guides_to_homes
  guide_id           UUID foreign key
  home_id            UUID foreign key
  position           optional stable presentation order
```

Guide applicability also needs an explicit scope:

```text
home_scope = all | selected
```

Do not overload an empty join table to mean both "all Homes" and "not assigned
yet". Explicit scope avoids ambiguity during imports, migrations, validation,
and future automation.

## Data ownership and permissions

Initial permissions should remain deliberately simple:

- Homes are visible to authenticated members of their Group.
- Group managers can create, rename, order, and archive Homes.
- Guide read access remains group-wide as it is today.
- Guide edit and delete permissions remain with the owning Mealie Household.
- Assigning a Guide to a Home does not transfer Guide ownership.
- Home selection is never used as an authorization check in the first slice.

If real users later need separate people or permissions per property, treat
that as a distinct membership project. Do not quietly turn Home filtering into
security.

## API direction

Follow existing repository-service-controller conventions with a parallel Home
domain. A future API would likely provide:

```text
GET    /api/homes
POST   /api/homes
PUT    /api/homes/{id}
DELETE /api/homes/{id}        archive by default
```

Guide create/update contracts would add:

```text
homeScope: "all" | "selected"
homeIds: UUID[]
```

Guide list/search would accept an optional Home filter. Omitting it means all
accessible Guides, preserving current behavior and stable existing clients.
Exact route prefixes should be reconciled with the current Mealie version at
implementation time rather than frozen prematurely here.

## UI direction

### Library

- No Home selector appears while Hearth has only one implicit Home.
- With multiple Homes, the current context area may become an `All Homes`
  selector.
- Selection filters the library but does not change the person's account or
  Mealie Household.
- The selected Home should be represented in the URL so browser back, refresh,
  and sharing behave predictably.

### Cards and reader

- When viewing `All Homes`, show a compact Home label when a Guide has selected
  applicability.
- When already filtered to one Home, avoid repeating that Home on every card.
- An `All Homes` Guide should read as universally applicable, not unassigned.

### Editor

Add one control near essential metadata:

```text
Where does this apply?
● All homes
○ Selected homes…
```

Default existing and newly created Guides to `All homes` unless user evidence
supports a different default. Advanced Spaces or Assets must not appear here.

### Settings

Home management belongs in household/group settings according to the final
permission decision. It should not become a permanent primary-navigation area.

## Search and URL behavior

Home is a filter and applicability dimension, not a replacement for Guide
category or tags.

Recommended future query shape:

```text
/g/{groupSlug}/guides?home={homeId}
```

Guide URLs remain independent of Home context:

```text
/g/{groupSlug}/guides/{guideSlug}
```

Search may match Home names for discovery, but a query should not silently
change the selected Home context.

## Migration strategy

### Existing installations

- Do not require a named Home record to preserve current Guide behavior.
- Backfill existing Guides with explicit `home_scope = all`.
- Create no named Home automatically unless the product requires one for the
  first usable screen.
- If a default named Home is necessary, let an administrator name it during a
  clear migration step instead of inventing property information.

### Namespaced tags

If `home:` tags have become common by implementation time:

1. Detect distinct normalized `home:` tag values.
2. Preview proposed Home records and Guide assignments.
3. Require explicit administrator confirmation.
4. Preserve original tags until the migration is verified.
5. Make the migration idempotent and reversible where practical.

Never interpret ordinary tags as Homes automatically.

## Export and backup

- Guide export includes Home applicability using stable names and identifiers
  suitable for round trips.
- Full backup includes Home records, archived state, order, explicit Guide
  scope, and associations.
- Imports resolve by stable identifier first and normalized group-scoped name
  only as a controlled fallback.
- Restore order must create Homes before Guide associations.
- Existing exports without Home data import as `all`.

## Upstream compatibility

Implement Home as an additive Hearth domain. Expected ownership:

```text
mealie/db/models/home/
mealie/schema/home/
mealie/services/home/
mealie/routes/home/
mealie/repos/repository_homes.py
frontend/app/components/Domain/Home/
frontend/app/composables/homes/
frontend/app/lib/api/user/homes.ts
```

Shared Mealie touchpoints should remain limited to registration, generated
types, Guide integration, backup/export orchestration, and a small library
context seam. Do not modify Mealie Household membership or authentication to
ship the first Home slice.

## Validation requirements

Before a future Home slice is complete, verify:

- Existing single-home installations behave exactly as before.
- `All Homes` and each selected Home return the correct Guides.
- Guides can apply to multiple Homes without duplication.
- Archived Homes do not break Guide readers, exports, or backups.
- Group boundaries prevent cross-group Home access.
- Guide ownership remains unchanged after Home assignment.
- Search, URL refresh, browser back, and deep links preserve context.
- SQLite and PostgreSQL migrations and round trips pass.
- Fresh and upgraded capability profiles retain their expected navigation.
- The current upstream branch merges synthetically without unresolved conflict.

## Relationship to the UI/UX redesign

The redesign remains single-home. It should reserve a context slot and flexible
metadata treatment, but it must not display dormant multi-home controls.

If the implementation trigger is met before the redesign is complete, pause at
a sub-slice boundary, implement the Home foundation as its own product slice,
update the prototype with real Home behavior, and then continue the redesign.
