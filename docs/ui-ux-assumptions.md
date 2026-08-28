# Hearth UI/UX Assumptions and Experiments

## Purpose

This register separates what the audit observed from what the team merely
believes. A design moves into production only when the smallest useful test
supports it. Accessibility, safety, security, and upstream compatibility are
requirements, not experiments.

## What is known

- A fresh Hearth profile can show only Guides and relevant Settings.
- An upgraded installation can retain the full Mealie navigation.
- The seeded library contains 15 realistic Guides.
- Ordinary-language search can find the correct seeded Guide quickly.
- The current library, reader, and editor reflow without horizontal scrolling
  at 320 pixels.
- Safety notes can be shown before requirements and steps.
- The complete Guide data model can be created, edited, exported, restored, and
  printed.

## Assumption register

| ID | Assumption | Risk if wrong | Confidence | Smallest useful test |
|---|---|---:|---:|---|
| H01 | Most visits begin with finding an existing procedure | High | Medium | Ask five household users to choose their first action from a cold library screen |
| H02 | One prominent library search plus a compact global trigger is clearer than two full search models | High | Medium | Compare the current build and revised prototype on three find-an-answer tasks |
| H03 | Hiding advanced filters initially will not harm normal Guide discovery | Medium | Medium | Run three ordinary-language queries and one browse task without exposing filters |
| H04 | Showing fewer card details improves recognition without hiding needed context | High | Low | Test current and simplified cards with six realistic Guides and ask which one solves each scenario |
| H05 | Safety, requirements, and steps matter more during use than classification and tags | High | Medium | Time warning and first-step identification on current and revised readers |
| H06 | A basic-first editor will increase successful first-time Guide creation | High | Medium | Give five participants a text-only Guide task; record help requests, advanced sections opened, and completion |
| H07 | A sticky save-state area will increase confidence without obstructing content | Medium | Medium | Interrupt save, fail save, and complete save in the prototype at phone and desktop widths |
| H08 | The warm Hearth palette can feel distinctive without a custom font or broad theme rewrite | Medium | High | Test Guide-scoped tokens in light/dark themes with real content and measure contrast and payload |
| H09 | Upgraded Mealie users prefer retained familiar navigation over a forced Hearth-only shell | High | High | Preserve by default; interview upgraded users before proposing a change |
| H10 | Multi-home controls would be noise for current users | Medium | High | Keep absent until the trigger in the Future Homes Plan is observed |

## First-cycle hypotheses

### Hypothesis 1 — Results sooner

We believe people looking for household instructions will open the correct
Guide faster if the library places results and feedback directly below one
prominent search field and hides advanced filters until requested.

Success means:

- At least 9 of 10 realistic search trials open the intended Guide within 10
  seconds.
- No participant looks for a second search surface.
- Loading, no-result, and failed-load feedback is visible in the current phone
  viewport.
- Browse-only participants can still find category and filter controls.

Invalidation means two or more participants need exposed advanced filters for
ordinary discovery, or the correct-result rate falls below the current search
baseline.

### Hypothesis 2 — Preparation-first reader

We believe people will follow Guides more safely if the reader reduces header
metadata and makes outcome, trust, safety, requirements, and steps the dominant
sequence.

Success means:

- Every participant identifies the main warning before starting.
- At least 9 of 10 trials identify the first action within 10 seconds.
- Participants can still find classification and tags when asked.
- Phone, print, keyboard, screen-reader, and 200% zoom order agree.

Invalidation means reduced metadata causes participants to choose the wrong
Guide or misunderstand whether they have enough time or skill.

### Hypothesis 3 — Basic-first authoring

We believe household members will create more complete and accurate Guides if
the editor starts with essential content and reveals classification, upkeep,
references, relationships, and media only on request.

Success means:

- At least 4 of 5 first-time participants save a useful text-only Guide without
  help.
- No required safety or procedural field is missed because it was hidden.
- The median participant opens no irrelevant advanced section.
- Save failure preserves all entered work and is understood without support.

Invalidation means users consistently miss important fields, cannot find an
advanced field when asked, or take longer than in the current editor.

## Experiment order

Use the lowest-cost test that can answer each question:

1. Update the existing disposable concept with the audit's three priorities.
2. Use the 15 seeded Guides and three fixed scenarios:
   - restart a router without erasing settings
   - remove a cooking-oil stain from clothing
   - respond safely to a small cooking-oil fire
3. Test at 390-pixel phone and desktop widths in light and dark themes.
4. Run five short observed sessions with people who did not build Hearth.
5. Record completion time, wrong turns, help requests, missed warnings, and
   comments made while acting.
6. Mark each hypothesis supported, unsupported, or inconclusive before
   production implementation.

Do not use preference questions such as “Which design do you like?” as the main
evidence. Observe whether the person completes the task.

## Slice 12B prototype check

The revised disposable concept passed the checks it can answer without real
participants:

- The library was inspected at 1280, 390, and 320 pixels in light and dark
  themes; a Guide result begins in the first phone view.
- `router` leaves only the router Guide visible. A category can be disclosed,
  applied, seen after the disclosure closes, and cleared.
- Result count, no-result, loading, and failed-load recovery appear directly
  below search.
- The reader's DOM and visual order is outcome, trust, safety, preparation,
  then steps. Decorative media is removed from the phone path.
- The editor keeps safety visible, places classification under **More
  details**, reports editing/saving/saved/failed states, and retains edited
  text after a simulated failure.
- The browser reported no console errors.

This is an internal interaction and reflow check, not user evidence. H01–H08
remain unconfirmed until the planned task sessions are observed. H09 and H10
remain protected product constraints rather than prototype experiments.

## Current process score

Lean UX process: **7/10**.

The project now has declared assumptions, testable hypotheses, pre-committed
thresholds, a low-cost interactive concept, outcome measures, and a staged
discovery/delivery plan. It is not yet 10/10 because independent user sessions
have not run and no hypothesis has yet been invalidated. Those are evidence
gaps, not reasons to add more documentation.

## Decision rules

- Supported hypothesis: implement the smallest change that produced the
  outcome.
- Unsupported hypothesis: remove or revise the idea; do not move it to a vague
  future backlog.
- Inconclusive result: change the experiment, not the success threshold.
- Accessibility failure: fix before further preference testing.
- New API or data need: stop and make a separate product decision.
- New shared Mealie touchpoint: document why the Guide-owned path is
  insufficient before editing it.
- Multi-home request: use the trigger and scope in
  [Future Homes Plan](future-homes.md); do not repurpose Household.
