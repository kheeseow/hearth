# Hearth UI/UX Journey Map

## Purpose

This map keeps Slice 12 focused on what a person is trying to accomplish. It is
not a screen inventory. Each journey starts with a real need and ends when that
need is satisfied.

## Journey overview

| Journey | Start | Successful end | Current state | Target |
|---|---|---|---|---|
| Find an answer | “Something is wrong or I need instructions” | Correct Guide open | Search works, but results begin too low on phones | Correct Guide open within 10 seconds |
| Follow safely | Guide open, often on a phone | Procedure completed without missing preparation or warnings | Safety order is good; metadata and long headers slow entry | Safety and first action understood within 10 seconds |
| Capture knowledge | A household member knows a repeatable procedure | Useful Guide saved | Complete but intimidating editor | Simple text Guide saved without opening advanced details |
| Maintain trust | Existing Guide is stale or wrong | Change saved and trust state clear | Edit mode is clear; save state is distant | Mode and save state visible throughout |
| First run | New account or fresh installation | First useful Guide found or created | Fresh navigation is focused | First value within three decisions |
| Administer | Need to change account, appearance, backup, or server settings | Setting changed and return path clear | Fresh and upgraded profiles preserve their intended scope | Scope of setting and return to Guides are obvious |

## Journey 1 — Find an answer

### Person's question

“How do I solve this household problem right now?”

### Current path

1. Open the Guide library.
2. Choose between the header search and the library search.
3. Enter ordinary words.
4. Submit or wait, depending on the chosen search surface.
5. Pass the large introduction, actions, and filters.
6. Recognize and open the correct card.

### Evidence

- `router reset` returned the correct router Guide in about 1.1 seconds.
- At 320 and 390 pixels, no Guide card appeared in the first screen.
- Five filters appeared before results even when none was requested.
- A failed load produced a useful retry message, but it appeared below those
  filters.

### Better path

1. Open Hearth directly to the Guide library.
2. Search in one obvious field or browse immediately visible Guides.
3. See results, result count, loading, or failure directly below that field.
4. Open the correct Guide.

### Measures

- At least 90% of five-person trials open the correct seeded Guide in 10
  seconds.
- Search feedback appears within the current phone viewport.
- Advanced filters are not required for the three agreed ordinary-language
  queries.

## Journey 2 — Follow safely

### Person's question

“What do I need, what must I avoid, and what do I do next?”

### Current path

1. Read the Guide title and outcome.
2. Pass type, difficulty, frequency, category, duration, review state, and tags.
3. Read safety warnings.
4. Gather requirements.
5. Follow the numbered steps.

### Evidence

- The cooking-oil-fire Guide correctly places warning and avoid notes before
  requirements and procedure.
- The phone header can show six metadata chips plus tags before safety.
- Steps have semantic headings and clear numbering.
- Slice 11 verified 320-pixel reflow, accessible names, print, and reduced
  motion.

### Better path

1. Confirm the Guide and intended outcome.
2. See only time and trust information needed for the decision to proceed.
3. Read safety and preparation.
4. Follow a calm, legible sequence of steps.
5. Recover position easily after an interruption.

### Measures

- All trial participants identify the main warning before starting step one.
- All identify the first action within 10 seconds.
- No horizontal scroll at 320 pixels or 200% zoom.
- Print order matches the on-screen safety and procedure order.

## Journey 3 — Capture knowledge

### Person's question

“How can I save this procedure for the household without documenting
everything?”

### Current path

1. Select New guide.
2. Enter title and description.
3. Consider cover image.
4. Consider type, difficulty, frequency, category, tags, and two durations.
5. Consider review date, notes, and related Guides.
6. Consider references, tools, materials, safety notes, steps, tips, and media.
7. Reach Save at the bottom.

### Evidence

- The editor supports the complete Guide model.
- Optional and essential inputs share the same visual level.
- Save and Cancel follow all sections, so a long Guide has no continuously
  visible save state.

### Better path

1. Enter title and intended outcome.
2. Add warnings or requirements when relevant.
3. Add the steps.
4. Save confidently.
5. Open clearly named optional sections for classification, upkeep, references,
   relations, or media only when needed.

### Measures

- At least 4 of 5 first-time participants create a useful text-only Guide
  without help.
- The median participant does not open an advanced section unnecessarily.
- Editing, Saving, Saved, and Failed states remain visible.
- Failed saves preserve every entered value.

## Journey 4 — Maintain trust

### Person's question

“Is this still correct, and can I update it without losing work?”

### Current path

1. Notice Not reviewed or Review needed among metadata.
2. Select Edit.
3. Find the field that needs changing in the full editor.
4. Scroll to Save.
5. Return to the reader.

### Better path

1. See trust state near the Guide outcome.
2. Enter an unmistakable edit mode.
3. Change the relevant section.
4. See honest local save progress and success or failure.
5. Return to the same reading context.

### Measures

- All participants can explain whether the Guide has been reviewed.
- A failed save never loses changes.
- Cancel clearly returns without silently applying edits.

## Journey 5 — First run

### Person's question

“What is Hearth, and what useful thing can I do now?”

### Current path and evidence

The fresh capability profile exposes Guides and Settings only. The upgraded
profile correctly retains Mealie features. The Guide library explains Hearth,
but its introduction occupies most of the first phone screen.

### Better path

1. Land directly in the Guide library.
2. Recognize Hearth as the household instruction manual.
3. Open a useful example or create the first Guide.

### Measures

- First value within three decisions after account setup.
- No recipe-era choice appears in a fresh Hearth profile.
- No tutorial is required to understand the first action.

## Journey 6 — Administer without losing context

### Person's question

“Where do I change this, what will it affect, and how do I get back?”

### Current path and evidence

Fresh Hearth offers language, appearance, user settings, and admin settings
from a compact Settings menu. Upgraded installations retain the wider Mealie
navigation and settings. Both modes worked in the audit.

### Better path

Keep this behavior stable during the first redesign cycle. Later shell work may
clarify personal, household, group, and server scope, but must not remove
upgraded Mealie workflows.

## Shared state requirements

Every core journey must explicitly handle:

| State | Required behavior |
|---|---|
| Loading | Show progress where the result will appear; keep repeated actions from creating duplicate work |
| Empty library | Explain that there are no Guides and offer New guide |
| No search result | Preserve the query, explain the result, and offer Clear filters |
| Load failure | Explain that Guides could not load and keep Try again beside the message |
| Save failure | Preserve work and show Failed with a direct retry path |
| Missing image | Keep the Guide and step understandable without the image |
| Permission failure | Explain that the action is unavailable without implying that content disappeared |
| Stale review | Show trust state without making the Guide unusable |
| Offline/PWA | Keep already available content readable where supported; never pretend a change was saved |

## Sequence for Slice 12

The journey order defines delivery order:

1. Library and search
2. Reader
3. Authoring and trust maintenance
4. First run and shared shell
5. Whole-product edge-state pass
6. Final validation

This order matches the existing Slice 12C–12H structure. Slice 12B first turns
the evidence into a small token and component decision record.
