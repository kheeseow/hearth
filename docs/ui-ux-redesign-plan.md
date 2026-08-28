# Hearth UI/UX Redesign Plan

## Status

Planning only. Product Slice 12 has not started.

This plan defines the redesign direction, evidence-gathering method, delivery
sequence, and upstream-compatibility boundaries that must be agreed before UI
implementation begins.

## Executive decision

Hearth should become **visually distinctive and behaviorally purpose-built,
while remaining structurally conservative**.

The redesign will not skin every inherited Mealie screen or replace its
frontend foundations. It will create a coherent Hearth experience around the
small number of journeys that make the product valuable, then connect that
experience to Mealie through narrow, documented seams.

The One Thing Hearth must do is:

> Help someone find and safely follow the right household procedure within
> seconds, without needing to solve the same problem again.

The corresponding product model is **a household instruction manual**, not a
dashboard, wiki, notes app, or generic content manager.

## Why a redesign makes sense now

The Guide domain is complete enough to represent real household procedures,
and Slice 11 established the accessibility and small-screen baseline. The
remaining weakness is coherence: the Guide experience is capable, but much of
its shell, density, component treatment, and interaction language still feels
inherited from a recipe-management application.

The redesign should solve that at the experience level rather than through a
large cosmetic rewrite.

## Provisional baseline

These scores are planning estimates based on the working product, code
inspection, desktop and phone-width checks, and seeded Guide content. Slice 12A
will replace them with a recorded, repeatable audit.

| Lens | Current estimate | Main gap |
|---|---:|---|
| Product focus and simplicity | 7/10 | The Guide promise is clear, but inherited navigation and secondary actions still compete with it |
| Discoverability and conceptual model | 7/10 | Search and creation are visible, but the product does not yet feel like one coherent household manual |
| Heuristic usability | 8/10 | Slice 11 resolved accessibility blockers; workflow clarity, recovery, and prioritization still need review |
| Visual system | 5/10 | Color exists, but hierarchy, spacing, component density, surfaces, and image treatment are not yet a complete system |
| Typography | 6/10 | Text is functional, but the reader and application chrome do not yet have deliberate roles, measures, and responsive scales |
| Microinteractions | 6/10 | Loading and error states exist, but saving, editing, filtering, uploads, and transitions do not yet feel like one product |
| Lean UX process | 4/10 | Product decisions have been incremental, but assumptions, hypotheses, success thresholds, and lightweight user testing are not yet recorded |

The current product is usable. The redesign goal is not to decorate it; it is
to make its purpose self-evident and its main journeys feel inevitable.

## Experience principles

### 1. The library is home

Do not add a dashboard between the user and their Guides. The default Hearth
destination should be the searchable Guide library. A person opening Hearth is
usually trying to answer a question, not inspect product metrics.

### 2. Search first, browse second

Search is the fastest route for a known problem. Browsing remains important
for recognition and discovery, but advanced filters should use progressive
disclosure instead of occupying the first visual tier.

### 3. Reading is not editing

The reader should feel calm, authoritative, and safe. The editor should make
its mode unmistakable, preserve work, and reveal advanced fields only when
needed. Controls should never make a Guide feel like a blank document editor.

### 4. Safety before procedure

Warnings, prerequisites, tools, and materials must be understood before the
first procedural action. Safety hierarchy is functional, not ornamental.

### 5. One intent per screen

Every screen must have one sentence that explains its purpose and one dominant
action. Secondary actions remain available without competing visually.

### 6. Prefer recognition to recall

Use clear categories, recent or relevant Guides, visible selections, example
queries, and human language. Do not require users to remember taxonomy terms or
internal system concepts.

### 7. Feedback should live where the action happened

Saving, filtering, uploading, retrying, and deleting should provide immediate,
local, honest feedback. Use global notifications only when the result is not
owned by a visible control or field.

### 8. Calm utility over novelty

Hearth should feel warm and crafted, but never theatrical. Motion must explain
state or continuity. Decorative animation, engagement mechanics, and interface
novelty are outside the goal.

## Core journeys

Slice 12 will evaluate and redesign complete journeys rather than isolated
screens.

### Journey A — First run to first useful Guide

1. Start Hearth.
2. Understand what it is without explanatory documentation.
3. Reach a useful example Guide or create the first Guide.
4. Recognize that this is shared household knowledge.

Success target: one recommended path, no irrelevant configuration, and first
value within three decisions after account creation.

### Journey B — Find an answer

1. Open Hearth on a phone.
2. Search using ordinary language such as “router reset” or “oil stain”.
3. Recognize the correct result.
4. Open the Guide.

Success target: the correct seeded Guide can be reached within 10 seconds and
without opening advanced filters.

### Journey C — Safely complete a procedure

1. Understand title, outcome, duration, difficulty, and review state.
2. Read warnings and requirements.
3. Follow ordered steps with supporting images and tips.
4. Recover position after interruption.

Success target: no ambiguity about preparation, current step, safety, or what
to do next at phone width and 200% zoom.

Remembering completed steps or resuming across devices would require a product
and data-model decision. Slice 12 must not introduce that behavior implicitly.

### Journey D — Capture household knowledge

1. Start a new Guide from the library.
2. Enter the minimum useful information.
3. Add steps and optional supporting detail.
4. Preview or save confidently.

Success target: a simple text-only Guide can be created without confronting
every advanced field, while the complete Guide model remains available through
progressive disclosure.

### Journey E — Maintain trusted knowledge

1. Notice that a Guide needs review.
2. Enter a clearly signified edit mode.
3. Update content or media without losing work.
4. Save, cancel, retry, or delete with predictable outcomes.

Success target: current mode and save state are always visible; errors preserve
input; destructive actions are separated from routine editing.

### Journey F — Administer Hearth without seeing recipe-era complexity

1. Change account, language, appearance, backup, or server settings.
2. Understand whether the setting affects the person, household, or server.
3. Return to the Guide library easily.

Success target: fresh installations expose only relevant choices. Upgraded
installations retain complete Mealie-compatible controls without forcing them
into the fresh Hearth experience.

## Proposed information architecture

### Fresh Hearth profile

The primary navigation should contain:

1. **Guides** — the library and default destination
2. **Create Guide** — a strong contextual action, not a separate product area
3. **Settings** — secondary, containing account, household, language,
   appearance, backup, and administration according to permissions

Search remains globally reachable and visually prominent on the Guide library.
It does not need to compete with a separate “Home” dashboard.

### Upgraded Mealie profile

Retain current Recipe, meal-plan, shopping-list, and organizer navigation. Add
the improved Guide experience as a peer capability. Do not redesign legacy
domains during Slice 12.

### Guide library

Recommended hierarchy:

1. Search and clear statement of purpose
2. Contextual primary action to add a Guide
3. Relevant or recent Guide results
4. Compact browse controls
5. Advanced filters disclosed on request

Category, type, frequency, difficulty, tags, and future home/space dimensions
must not all become equal top-level navigation. The current single-home model
remains unchanged; tags continue to test additional taxonomy needs.

### Guide reader

Recommended hierarchy:

1. Identity and outcome
2. Safety
3. What is needed
4. Ordered procedure
5. Notes and sources
6. Related Guides and maintenance information

Edit, print, and other utilities should be findable but visually subordinate to
the procedure itself.

### Guide editor

Recommended hierarchy:

1. Essential information
2. Steps
3. Safety and requirements
4. Images
5. Classification and maintenance metadata
6. Relationships and sources

This is presentation order, not a database change. Existing Guide fields and
API contracts remain intact.

## Visual direction

The intended character is **a calm, warm, practical household manual**:

- IKEA-like instructional clarity
- the scanability and familiarity of a good recipe application
- the confidence of a maintained appliance manual
- the warmth of a personal household object rather than enterprise software

### Hierarchy

- One dominant heading and primary action per screen
- Supporting metadata visibly quieter than the procedure
- Fewer simultaneous outlined boxes
- Grouping expressed primarily through spacing, then surface and border
- Safety and destructive states use semantic prominence, never brand color
  alone

### Spacing and layout

- Adopt one explicit 4/8/16/24/32/48/64-pixel spacing scale
- Keep prose near 65 characters per line
- Keep routine forms within a readable 300–600-pixel working width
- Design at 320, 390, 768, 1280, and wide desktop widths
- Use the same content order in responsive layouts unless the task requires a
  deliberate priority change

### Typography

Before choosing a new typeface, compare a system-first workhorse stack with at
most two locally served variable-font candidates using real Guide content.

Requirements:

- One family is preferred; two is the maximum
- Body text is at least 16 pixels; Guide procedure text targets 17–18 pixels
- Body line height is 1.5–1.7; headings use 1.1–1.25
- Type roles use a fixed responsive scale rather than individual component
  guesses
- Total additional font payload must stay below 200 KB, use WOFF2 and
  `font-display: swap`, and retain complete supported-language coverage
- The system must survive 200% zoom without truncation or horizontal scrolling

The plan does not pre-approve a web font. If a candidate does not materially
improve Hearth at real sizes, keep the system stack and spend the performance
budget elsewhere.

### Color and surfaces

- Preserve Hearth's warm terracotta, green, and amber direction, but define
  complete light and dark role-based scales rather than isolated brand values
- Establish tokens for canvas, surface, raised surface, strong text, muted text,
  borders, primary action, focus, success, caution, warning, and danger
- Verify WCAG AA contrast in both themes
- Use elevation consistently: page, card, dropdown, and dialog must not all
  appear at the same depth
- Design the hierarchy in grayscale before approving the final palette

### Images and icons

- Use one consistent icon family and stroke/weight behavior
- Treat cover images as orientation aids, not decorative banners
- Reserve step images for information that improves task completion
- Preserve explicit alternative-text authoring and useful crop behavior
- Avoid visual treatment that makes image-free Guides feel incomplete

## Microinteraction plan

Each important interaction will receive a state model with trigger, rules,
feedback, and loop/mode behavior.

| Interaction | Required states and behavior |
|---|---|
| Search | idle, typing, loading, results, no match, failure, clear; results must not jump unpredictably |
| Filters | inactive, active, changed, applying, cleared; active constraints must remain visible |
| Save | clean, dirty, validating, saving, saved, failed; input survives failure |
| Edit mode | visually explicit entry, current mode, cancel, save, leave-with-unsaved-work handling |
| Image upload | selected, uploading, progress/indeterminate, complete, failed, retry, remove, alternative-text state |
| Delete | separated trigger, clear consequence, confirmation or recoverable undo according to technical feasibility |
| Loading | skeleton or progress chosen by content predictability; no fake percentages |
| Errors | local cause, preserved work, direct recovery action, optional diagnostic detail |

Motion should normally complete in 150–250 ms, use transform and opacity where
appropriate, and respect reduced-motion preferences. Hearth may have one
restrained signature moment later, but Slice 12 will not add decorative
celebration merely to create personality.

## Lean UX hypotheses

These are design bets, not pre-approved solutions.

| Hypothesis | Signal | Initial success threshold | Smallest useful experiment |
|---|---|---:|---|
| A search-dominant library with progressive filters helps people find the right Guide faster | Time and wrong turns for five realistic queries | Correct Guide within 10 seconds for at least 90% of trials | Two low-fidelity library variants, then a browser prototype |
| A preparation-first reader improves safety and confidence | Missed warnings/requirements and confidence rating | No critical warning missed; users can state preparation before step 1 | Reorder a representative Guide in a disposable prototype |
| Progressive disclosure makes Guide creation feel simpler without reducing completeness | Time, abandonment, fields visited, final Guide completeness | All participants create a valid simple Guide without help; advanced fields remain discoverable | Clickable editor prototype with basic and advanced sections |
| A focused fresh-profile shell makes Hearth understandable without harming upgraded installs | Trunk Test answers and navigation task completion | All six Trunk Test questions answered; upgraded Mealie tasks remain reachable | Capability-profile walkthroughs using the real app |
| A constrained token system improves perceived cohesion without a framework rewrite | Visual diagnostic score and shared-file delta | Visual score reaches at least 9/10 while the upstream shared-file budget holds | Apply tokens to library and reader prototypes before global adoption |

Metrics will be agreed before each experiment. Failed hypotheses are removed or
reframed rather than carried into delivery as deferred work.

## Upstream-compatible implementation architecture

### Layer 1 — Hearth design tokens: broad freedom, low risk

Create a small Hearth-owned token layer for color roles, spacing, type roles,
radii, elevation, content widths, and motion. Map tokens into Vuetify's
existing theme and defaults instead of adding another CSS framework.

Potential Hearth-owned paths:

```text
frontend/app/assets/hearth-tokens.css
frontend/app/lib/hearth-design-tokens.ts
frontend/app/plugins/hearth-ui.ts
```

Exact files are decided during technical design; the important rule is one
source of truth rather than page-specific values.

### Layer 2 — Guide-domain components: broad freedom, low risk

Redesign within the existing Guide domain:

```text
frontend/app/components/Domain/Guide/
frontend/app/pages/g/[groupSlug]/guides/
frontend/app/composables/guides/
```

Prefer composition of existing Vuetify primitives. New reusable Guide
components should express Guide concepts, not copy Recipe components.

### Layer 3 — Hearth shell adapters: controlled freedom, medium risk

Shared header, navigation, and layout changes must occur through a small
capability-aware contract. Prefer configuration, props, slots, or a focused
Hearth wrapper over scattered conditional markup.

Expected integration seams remain limited to:

```text
frontend/app/components/Layout/DefaultLayout.vue
frontend/app/components/Layout/LayoutParts/AppHeader.vue
frontend/app/components/Layout/LayoutParts/AppSidebar.vue
frontend/app/plugins/theme.ts
frontend/nuxt.config.ts
```

Not every file must change. The technical-design step must attempt to reduce
this list before implementation.

### Layer 4 — Retained Mealie screens: narrow styling only

Recipe, meal-plan, shopping-list, authentication, administration, and shared
settings screens should inherit safe tokens and global component defaults.
Do not fork their layouts merely to make screenshots match Hearth.

### Layer 5 — Platform foundations: do not redesign

Avoid redesign-driven changes to authentication, route conventions, API client
bases, generated types, state infrastructure, database schemas, or backend
domain behavior.

## Upgrade guardrails

1. Do not introduce a second component framework, router, state store, or icon
   system.
2. Do not copy whole upstream pages or components to customize their visuals.
3. Do not reorganize upstream directories or rename Recipe-era packages.
4. Keep Guide and Hearth presentation code additive and parallel.
5. Prefer theme tokens and component props over deep global CSS selectors.
6. Keep capability logic centralized; do not scatter fresh/upgraded checks
   through presentation components.
7. Preserve upgraded Mealie workflows and run their existing tests.
8. Change only `en-US` when new interface strings are required.
9. Record every shared upstream file in `docs/fork-delta.md`.
10. Run a synthetic merge with `upstream/mealie-next` after every redesign
    sub-slice, not only at the end.
11. Reject broad formatting churn in shared files.
12. Any API or persistence change discovered during the redesign becomes a
    separate product decision; it does not ride inside a UI commit.

### Change budget

For each redesign sub-slice:

- Hearth-owned Guide and token files may change as needed.
- Aim to touch no more than three shared Mealie UI files.
- A fourth shared file requires an explicit explanation in the slice notes.
- A new upstream merge conflict in a previously clean seam must be either
  designed out or documented with its ongoing maintenance cost.

This budget is a forcing function, not an excuse to leave a broken experience.
If a high-value improvement truly needs a broader seam, decide deliberately.

## Product Slice 12 sequence

Slice 12 should be delivered as reviewable sub-slices, each ending in a working
demo and an upstream merge check.

### Slice 12A — Evidence baseline and cut list

Planning and evaluation only.

- Cold-walk the six core journeys in fresh and upgraded profiles
- Apply the Trunk Test, Nielsen heuristics, two-gulfs analysis, seven stages of
  action, accessibility checks, visual diagnostic, typography diagnostic, and
  microinteraction state review
- Test wide desktop, 320/390-pixel phones, keyboard-only, 200% zoom, light and
  dark themes, representative empty/error/loading states, and realistic data
- Record severity 0–4, frequency, impact, persistence, evidence, affected user
  goal, fix direction, and upstream-risk tier
- Produce the formal product review: verdict, One Thing, promise evidence, cut
  list, ranked fix list, and neglected “back of the fence” surfaces
- Select at most three redesign priorities for the first delivery cycle

Deliverables:

```text
docs/ui-ux-audit.md
docs/ui-ux-journey-map.md
docs/ui-ux-assumptions.md
```

No product code changes occur in 12A.

### Slice 12B — Design foundation prototypes

- Create the smallest token and component-contract proposal
- Produce grayscale library, reader, and editor prototypes using real Guide
  content
- Compare no more than two variants for each genuinely uncertain interaction
- Test hypotheses before adopting global styling
- Decide type, spacing, surface, color-role, icon, image, focus, and motion
  rules

Deliverable: a working, reviewable prototype and a short decision record. Do
not begin broad rollout until one direction is explicitly selected.

### Slice 12C — Library and search

- Make the Guide library the clear product home for fresh Hearth
- Establish search-first hierarchy and progressively disclosed filters
- Improve result recognition, active-filter visibility, empty states, and
  recovery
- Preserve stable URLs, current search API, seeded data, and upgraded profile
  navigation

### Slice 12D — Reader

- Apply the preparation-first reading hierarchy
- Refine long-form measure, typography, imagery, steps, safety, notes, sources,
  related Guides, review state, and print continuity
- Validate interruption, zoom, small phones, long content, missing images, and
  stale review states

### Slice 12E — Authoring

- Separate basic authoring from advanced metadata through progressive
  disclosure
- Make edit mode and save state explicit
- Improve step ordering, media feedback, validation, failure recovery, cancel,
  and destructive-action placement
- Preserve the complete current Guide contract and ordering behavior

### Slice 12F — First run and shared shell

- Make first run explain Hearth through one useful action rather than a tour
- Refine the fresh-profile navigation and settings hierarchy
- Apply the selected safe token layer to shared chrome
- Verify upgraded Mealie navigation remains complete and recognizable

### Slice 12G — Whole-product detail pass

- Resolve remaining severity 3 and 4 findings
- Review every loading, empty, error, offline/PWA, permission, setup, backup,
  and exit surface against the hero-screen quality bar
- Align copy, feedback timing, focus, touch targets, and responsive behavior
- Keep severity 1 cosmetic ideas in a separate backlog unless they complete a
  system already being changed

### Slice 12H — Validation and checkpoint

- Repeat every baseline journey and diagnostic
- Run frontend lint, full frontend tests, production build/PWA, relevant
  backend tests, and fresh/upgraded browser checks
- Verify keyboard, screen-reader semantics, contrast, reduced motion, 200%
  zoom, 320-pixel reflow, light/dark themes, print, and Firefox
- Measure route and font payloads against the Slice 11 baseline
- Run the upstream synthetic merge and update `docs/fork-delta.md`
- Issue a binary ship/not-done verdict and record all remaining severity 1–2
  items separately

## Definition of done

Slice 12 is complete only when:

- The One Thing is apparent within 10 seconds of a cold first view
- A realistic query reaches the correct Guide within 10 seconds in at least
  90% of the planned trials
- Fresh Hearth reaches first value within three post-account decisions
- All six Trunk Test questions can be answered from the Guide library and reader
- No severity 4 or severity 3 usability findings remain
- Heuristic, visual, typography, and microinteraction diagnostics each score at
  least 9/10
- Core flows work at 320 pixels and 200% zoom without horizontal scrolling
- Keyboard, accessible names, headings, focus order, live feedback, contrast,
  reduced motion, and error recovery pass
- Light and dark themes both feel intentionally designed
- A text-only Guide, image-heavy Guide, long Guide, empty library, no-result
  search, failed load, failed save, and permission failure have all been tested
- Upgraded Mealie navigation and retained workflows still pass
- Guide-specific route and font payloads stay within agreed budgets
- The current upstream branch merges synthetically without unresolved conflict
- Every shared integration file and maintenance reason is documented

## Explicit no list

Slice 12 will not:

- Add a dashboard between users and the Guide library
- Add AI, OCR, QR codes, reminders, completion tracking, streaks, engagement
  notifications, or a new taxonomy
- Redesign Recipe, meal-plan, nutrition, shopping-list, or cookbook workflows
- Change the Guide database, API, export, or backup model merely for layout
- Replace Vuetify, Nuxt, Mealie authentication, routing, or state foundations
- Introduce a large animation system or decorative motion
- Add a custom font without real-content, multilingual, accessibility, and
  payload evidence
- Attempt to make every inherited administration screen look custom
- Hide necessary complexity without providing a discoverable path to it

Habit-formation and retention-loop frameworks are intentionally excluded. A
household safety and reference product should minimize time and attention, not
manufacture engagement. Success is a correct answer and a completed task, not
daily active use.

## Approval gate before implementation

Before starting Slice 12A, confirm these decisions:

1. The Guide library, not a dashboard, is Hearth's home.
2. The One Thing and six core journeys are the correct product scope.
3. Fresh Hearth may receive a more focused shell while upgraded Mealie keeps
   its complete legacy navigation.
4. The redesign will be delivered as sub-slices with evidence and merge checks,
   not as one visual rewrite.
5. The explicit no list is accepted.

Once these are approved, begin with Slice 12A only. Do not jump directly to
visual implementation.
