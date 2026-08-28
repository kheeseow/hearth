# Hearth UI/UX Audit

## Status

Product Slice 12A established the baseline. Product Slice 12 implementation
and the engineering validation checkpoint were completed on 2026-08-28. The
only remaining evidence gate is the independent household-user trial described
at the end of this document.

The audit was run against the working Hearth application on 2026-08-28 using
the 15 seeded Guides. It covered the fresh Hearth profile and the upgraded
Mealie-compatible profile, desktop and phone layouts, light and dark themes,
search, no-result and failed-load recovery, a safety-critical reader, and the
full editor.

## Product promise

Hearth's one essential job is:

> Help someone find and safely follow the right household procedure within
> seconds, without needing to solve the same problem again.

The product keeps this promise functionally, but the library and editor make
people process more interface than the task requires.

## Evidence collected

| Check | Evidence | Result |
|---|---|---|
| Fresh profile | Temporary capability override with the existing data; navigation contained Guides and Settings | Passed |
| Upgraded profile | Normal recorded capability profile; Recipes, Recipe Finder, Guides, Meal Planner, Shopping Lists, Timeline, Cookbooks, Organizers, and Settings remained available | Passed |
| Known-answer search | `router reset` returned two relevant Guides, including “Restart a home router safely,” in about 1.1 seconds | Passed |
| No-result search | `zzqvxyz` returned “No matching guides” with Clear filters recovery | Passed |
| Failed load | With the local API stopped, the library showed “Guides could not be loaded” and Try again | Passed with placement issue |
| Small phone | Library at 320 pixels reported a 320-pixel document width with no horizontal overflow | Passed |
| Reader | “Handle a small cooking-oil fire” placed warnings before requirements and steps | Passed |
| Editor | The same Guide exposed the complete classification, upkeep, source, requirement, safety, media, and five-step model | Functionally complete; too much at once |
| Themes | Library and reader were inspected in dark and light themes | Passed |
| Accessibility baseline | Slice 11 passed the full frontend suite, semantic browser checks, named controls, focus treatment, reduced motion, and 320-pixel reflow | Passed; repeat after redesign |

The temporary fresh-profile override was removed after inspection. The normal
upgraded profile is running again. Seeded Guides and stored application data
were not changed.

## Main findings

Severity uses this scale:

- **4 — Blocking:** prevents the task
- **3 — Major:** regularly causes task failure or loss of confidence
- **2 — Moderate:** slows the task or makes the next action unclear
- **1 — Minor:** visible friction that does not threaten completion

| ID | Severity | Finding | Evidence and effect | Fix direction | Upstream risk |
|---|---:|---|---|---|---|
| A01 | 3 | Load failure feedback is far from the search action on phones | The error appears after the library heading, actions, and five filters, outside the first screen. A person may think Search did nothing. | Put result status and errors directly below search; keep retry beside the error. | Low: Guide page only |
| A02 | 3 | Simple editing exposes nearly the whole data model | A basic edit starts with cover media and seven classification/timing fields before upkeep, references, requirements, safety, and steps. Save and Cancel are only at the bottom. | Keep title, outcome, safety, requirements, and steps in the main path. Put classification, upkeep, references, and related Guides behind clear optional sections. Keep save state visible. | Low: Guide components only |
| A03 | 2 | Hearth has two different Guide search surfaces | The header opens an instant dialog while the library has a separate form and Search button. Results and recovery behave differently. | Define one shared search behavior and use the library search as the visible home-page entry. Keep a compact global trigger for other pages. | Medium: Guide search plus one shared header seam |
| A04 | 2 | The first phone screen contains no Guide result | At 320 and 390 pixels, the large introduction, search form, library introduction, New guide, Export, and filters push results below the fold. | Compress the introduction after first use; place results immediately after search; hide filters behind one clear control. | Low: Guide page only |
| A05 | 2 | Filters demand attention before they are needed | Guide type, difficulty, frequency, category, and tag are always visible. Filter state is not represented in the URL. | Collapse advanced filters, show active filters as removable chips, and serialize the state in the URL. | Low: Guide page and composable |
| A06 | 2 | Guide cards give too many metadata items equal weight | Cards may show type, difficulty, frequency, category, review state, description, and several tags. Titles and outcomes compete with chips. | Lead with title and outcome. Show only the two or three details that help recognition; move the rest to the reader or an expanded state. | Low: Guide card only |
| A07 | 2 | Reader preparation is correct but its header is crowded | Safety is correctly first, but up to six metadata chips and all tags appear before it. On phones this delays the warning and first step. | Keep outcome, duration, and trust state near the title; demote classification and tags. Preserve safety before procedure. | Low: Guide reader only |
| A08 | 2 | Edit mode is named but save state is not continuously visible | “Edit guide” is clear, yet a long edit gives no persistent reminder of unsaved work or nearby Save action. | Add a restrained sticky action area with Editing, Saving, Saved, or Failed state; preserve input on failure. | Low: Guide page and editor |
| A09 | 2 | No-result recovery arrives after unused controls | The message is specific and Clear filters works, but the empty result is below the complete filter form. | Place the result state immediately below search and keep filter controls secondary. | Low: Guide page only |
| A10 | 1 | Export competes with the main library tasks | “Export shown guides” sits beside New guide and remains prominent on phone. Export is occasional administration, not a common find-or-create action. | Move export to a clearly labelled secondary menu without hiding it. | Low: Guide page only |
| A11 | 1 | Upgraded navigation competes with Hearth's Guide focus | The complete Mealie navigation is visible by design. This is required for upgraded installations, not a deletion target. | Improve the active Guide state and content hierarchy; do not remove retained Mealie routes. | Medium: shared shell if changed |
| A12 | 1 | The visual language is functional rather than coherent | Vuetify defaults, many outlined fields, tonal chips, and similar card surfaces do not yet form a distinctive reading system. | Introduce a small Hearth-owned token layer for Guide surfaces only, then expand only with evidence. | Low if Guide-scoped |

There are no severity 4 findings. A01 and A02 are the only severity 3 findings
and must be fixed before Slice 12 can ship.

### Frequency, persistence, and affected goal

| Findings | Frequency | Persistence | Affected goal |
|---|---|---|---|
| A01, A04, A05, A09, A10 | Every phone visit or every affected search state | Repeats until the library layout changes | Find an answer |
| A03 | Every library visit and every global search decision | Repeats across sessions | Find an answer |
| A06 | Every result card with normal metadata | Repeats throughout browsing | Recognize the right Guide |
| A07 | Every metadata-rich Guide | Repeats each time the Guide is opened | Follow safely |
| A02, A08 | Every create or edit session, with greater impact on long Guides | Persists for the full authoring session | Capture and maintain knowledge |
| A11 | Every upgraded-profile visit | Intentional until a safe shared-shell improvement exists | Navigate without losing Mealie features |
| A12 | Most Guide screens | Persistent but mainly affects clarity and cohesion | Understand Hearth quickly |

## Diagnostic scores

These scores describe the current product, not the approved concept.

| Lens | Score | What prevents a higher score |
|---|---:|---|
| Product focus | 7/10 | The fresh profile is focused, but the library delays content and the complete editor does not make the simple path feel simple. |
| Discoverability and mental model | 6/10 | Actions are labelled and recovery exists, but duplicate search models and distant failure feedback widen the gap between action and result. |
| Usability | 8/10 | Core tasks work and controls are named. Major issues remain in failed-search feedback and authoring complexity. |
| Visual system | 5/10 | Spacing and contrast are serviceable, but hierarchy depends on many similar Vuetify surfaces and chips. |
| Typography | 8/10 | Text is readable and reflows, but library cards and reader metadata do not yet have a calm, deliberate hierarchy. |
| Microinteractions | 6/10 | Loading, retry, and empty states exist; save state, filter continuity, and locally placed feedback are incomplete. |
| Lean UX process | 7/10 | Assumptions and thresholds are now recorded. Real household-user trials and an invalidated hypothesis are still missing. |

### Framework checks

- **Trunk test:** Hearth identity, Guide page title, main sections, current
  navigation item, available actions, and search were identifiable. Fresh
  navigation was focused; upgraded navigation was complete but busier.
- **Usability rules:** visibility of system status and consistency are the main
  failures. Search feedback and authoring complexity account for the two major
  findings.
- **Action and feedback:** Search and Edit have clear controls. Failed search
  feedback is mapped too far from Search, while Save is mapped too far from
  most editor fields.
- **Error prevention and recovery:** Clear filters, Try again, Cancel, named
  move/remove controls, and constrained numeric fields exist. Failed-save work
  preservation still needs direct testing during authoring redesign.
- **Visual hierarchy:** the main tasks are labelled, but chips, fields, cards,
  and secondary actions compete at similar strength.
- **Typography:** base reading is comfortable and responsive. Card metadata and
  the reader header need fewer simultaneous type levels.
- **Interaction feedback:** loading and retry states are present. Filtering and
  saving need continuous, local, and honest state feedback.

## Formal product review

### Verdict: NOT DONE — 7/10

**The One Thing:** Find and safely follow the right household procedure within
seconds.

**Keeps its promise?** Partly. A realistic search finds the correct Guide
quickly, the reader puts safety before steps, and the fresh profile is focused.
The first phone screen delays actual Guides, failed search feedback is too far
from Search, and authoring asks for too much information before the essential
procedure is clear.

**Cut list:** always-visible advanced filters; equal-weight card metadata;
prominent library export; always-open advanced authoring sections; decorative
motion; a dormant Home selector.

**Fix list:**

1. Make search results and recovery immediate and visible.
2. Make the reader's safety, preparation, and steps faster to scan.
3. Give authoring a clear basic path with persistent save state and optional
   advanced sections.

**Back of the fence:** failed load, no-result search, empty library, failed
save, missing media, long Guides, print, permission failures, and upgraded
navigation must receive the same care as the main screenshots.

## First implementation-cycle priorities

Only these three priorities move forward:

1. **Library and search:** useful results sooner, one clear search model,
   secondary filters, visible result/error state.
2. **Reader hierarchy:** preparation first, restrained metadata, readable steps,
   strong interruption recovery.
3. **Authoring clarity:** essential fields first, optional details disclosed on
   demand, persistent and local save feedback.

Shared shell styling, first-run refinement, and whole-product detail work remain
later Slice 12 sub-slices. They must not expand the first cycle.

## Remaining evidence gap

The audit used the developer, the seeded data, source inspection, and automated
checks. It did not observe independent household users. Before broad rollout,
run the tasks in [UI/UX Assumptions](ui-ux-assumptions.md) with at least five
people who did not help build Hearth.

The in-app browser supported exact 320- and 390-pixel viewport checks but did
not expose a reliable browser-zoom control. A true 200% browser-zoom run was
therefore not counted as passed. Repeat it manually in Firefox and Chromium
before production rollout; a narrow viewport is not a substitute for zoom.

## Slice 12 final checkpoint

The production UI now uses the approved search-first library, preparation-first
reader, basic-first editor, focused shell, and guide-first fresh setup. The
upgraded capability profile still exposes every retained Mealie route.

| Finding | Resolution |
|---|---|
| A01, A09 | Load, result, empty, and recovery feedback now sits directly beside search. |
| A02, A08 | Essentials, safety/preparation, and steps form the primary editor path; advanced metadata is disclosed on request and the save state remains visible. |
| A03–A06 | The library uses one dominant search, disclosed filters, URL-restored state, and recognition-first cards. |
| A07 | The reader leads with outcome and trust, then safety, preparation, and procedure; secondary metadata is below the task. |
| A10 | Export remains available but is visually secondary. |
| A11 | Fresh navigation is Guide-focused; upgraded navigation remains complete and recognizable. |
| A12 | A small warm-neutral token layer now aligns the Guide surfaces and shared shell without replacing Vuetify or adding a custom font. |

There are no open severity 3 or 4 findings. Remaining severity 1–2 work is
limited to later evidence-led refinements, such as deciding whether upgraded
users want a more compact legacy navigation and replacing mismatched seeded
demo cover images.

### Final diagnostic scores

| Lens | Score | Evidence |
|---|---:|---|
| Product focus | 9/10 | The library is home, search is dominant, reader and editor each have one clear purpose, and fresh first run points to one useful action. |
| Discoverability and mental model | 9/10 | Household context, active navigation, search feedback, preparation order, and progressive disclosure match the household-manual model. |
| Usability | 9/10 | No major findings remain; recovery, validation, save state, destructive actions, and complete upgraded routes remain available. |
| Visual system | 9/10 | Spacing, warm surfaces, rust action color, green trust state, red safety state, radii, focus, and restrained depth form one small system. |
| Typography | 9/10 | System fonts, responsive headings, readable measures, restrained metadata, and print hierarchy passed real-content checks. |
| Microinteractions | 9/10 | Search, filters, save status, failure preservation, hover spacing, theme switching, and reduced motion give local and honest feedback. |
| Lean UX process | 8/10 | Assumptions, thresholds, prototype, implementation, and repeatable checks exist; independent user observations remain outstanding. |

### Final engineering evidence

- Full frontend lint and all 311 frontend tests passed.
- The Nuxt static production build and PWA generation passed.
- Fourteen relevant backend Guide and capability tests passed.
- Library, reader, and editor passed in the in-app browser and Firefox; the
  earlier Firefox `$globals` failure was reproduced during development and
  removed before the checkpoint.
- The editor passed a real Firefox 200% zoom check and restored to 100%
  afterwards. The 320-pixel library, reader, and editor reflowed without
  document overflow.
- Light and dark themes, stale review data, safety callouts, requirements,
  step images, text-only states, progressive disclosure, unsaved feedback,
  and semantic heading/control names were checked with seeded content.
- Measured text contrast ratios are 14.28:1 for light body, 5.12:1 for light
  muted text, 5.33:1 for light primary, 15.92:1 for dark body, 8.29:1 for dark
  muted text, and 5.72:1 for dark primary.
- No dependency, custom font, route, API, database, generated type, or legacy
  workflow was added or changed for the redesign.
- The final system-font build reduced shared entry CSS from 201.55 KB to
  192.46 KB and the PWA precache from 13,562.94 KiB to 13,554.19 KiB compared
  with the accidental Inter-fetch build; no font download remained.
- A synthetic merge with `upstream/mealie-next` at
  `2b81b6b0a3e591a017e009cad9a92b3ad7a3b837` produced a merged tree without
  conflicts; Hearth was 29 commits ahead and 29 commits behind.

### Remaining evidence gate

The engineering work is ship-ready, but the formal Slice 12 definition of done
still requires five independent household users to run the timed tasks in
[UI/UX Assumptions](ui-ux-assumptions.md). Until those trials meet the recorded
90% find-and-open threshold and 4-of-5 authoring threshold, the evidence verdict
is **NOT DONE FOR BROAD ROLLOUT** even though no implementation blocker remains.
