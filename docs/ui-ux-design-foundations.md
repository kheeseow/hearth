# Hearth UI/UX Design Foundations

## Status

Approved Slice 12 production foundation. The revised
[interactive concept](prototypes/hearth-ui-concept.html) remains the design
reference, and the production Guide library, reader, editor, and shared shell
now apply this direction.

## What the prototype decides

- **Library:** one visible search model, feedback directly below it, results
  before optional controls, and filters in a native disclosure.
- **Reader:** outcome, time, difficulty, and review trust in the header; then
  safety, preparation, and steps. Tags and classification do not compete with
  the task.
- **Editor:** recognition, safety, preparation, and steps form the basic path.
  Classification and specialist fields live under **More details**. Save state
  remains visible and entered work survives a failed save.

No second variant is needed for these three decisions. The audit already
identified the competing layouts as the source of delay. The next useful
comparison is task performance against the current product, not another visual
preference test.

## Small foundation

| Part | Candidate rule |
|---|---|
| Type | Use the existing system font stack. Body text is 16–17 px with a 1.55–1.65 line height; task text is limited to about 65 characters per line. |
| Spacing | Use a 4 px base with 8, 12, 16, 20, 24, 32, 48, 64, and 96 px steps. Peer controls use a 12 px gap; the compact mobile bar keeps at least 6 px between highlights. Use fewer, larger gaps between sections than within them. |
| Surfaces | Canvas, flat surface, raised surface, soft surface, and border are the complete depth set. Use borders first and shadows only for raised or sticky elements. |
| Colour | Warm neutrals carry the layout. Hearth rust marks primary actions, green marks positive/trust information, amber marks caution, and red is reserved for danger or failure. Meaning must also appear in words or icons. |
| Corners | 10 px for controls, 16 px for cards, and 24 px only for large media. Pills are limited to short states and removable filters. |
| Icons | Use the existing icon source in production. Pair unfamiliar icons with text; never use a lone icon for a destructive or safety action. |
| Images | Images help recognition but are optional. They must not delay warnings or the first step on a phone. Missing images leave a complete, readable Guide. |
| Focus | Every action uses a visible 3 px focus ring. Use an outward offset where space permits and an inset ring on full-card links so overflow cannot clip it. DOM, visual, and reading order stay aligned. |
| Motion | Use 120–180 ms for direct feedback and at most 220 ms for a screen change. Respect reduced motion; never animate safety content or hide progress behind motion. |
| Feedback | Loading, no-result, error, editing, saving, saved, and failed states appear beside the action that caused them and use plain language. |

## Minimal component contracts

These are behavioral contracts, not a new component library:

- `GuideSearch`: one query field; local live status; retry and clear recovery.
- `GuideFilterDisclosure`: closed initially; active count and removable active
  value remain visible after it closes.
- `GuideCard`: title, outcome, at most two recognition details, and review state.
- `GuideReaderHeader`: title, outcome, time, difficulty, and trust only.
- `GuideSafety`: appears before procedural steps whenever safety content exists.
- `GuideStep`: one numbered action, supporting text, and optional tip or image.
- `GuideEditorSaveBar`: editing, saving, saved, or failed; cancel and retry remain
  available without losing work.
- `GuideAdvancedFields`: native disclosure around the complete existing Guide
  contract; it does not remove data or invent a second model.

## Upstream boundary

Most product-specific work stays inside Guide pages, Guide components, and
Guide composables. The approved shared-shell boundary also includes the app
header, sidebar, mobile navigation, theme tokens, and a thin global style
override. It does not change Vuetify or Nuxt internals, the Guide API,
generated types, route paths, or upgraded Mealie capabilities.

## Evidence still required

The production UI's key text/background pairs measure from 4.76:1 to 15.92:1 in
both themes, meeting the WCAG AA target for normal text. Browser checks also
covered 1280-, 390-, and 320-pixel widths, Firefox at 200% zoom, and reported
no console errors.

Engineering checks can prove reflow, visibility, interaction states, and theme
behavior. They cannot prove that real household users finish faster. H01–H08 in
the [assumptions register](ui-ux-assumptions.md) remain hypotheses until the
planned household-user task trials are observed.
