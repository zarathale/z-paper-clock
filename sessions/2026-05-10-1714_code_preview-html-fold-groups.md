---
date: 2026-05-10
start_time: "17:14"
end_time: "17:14"
mode: code
participant: Zarathale (Alan)
target: preview-html-fold-groups
orchestration_prompt: CODE_PROMPT_preview-html-fold-groups.md
---

## Goal

Add automatic fold-group detection and grouped rendering to the Bench-mode fold
slider panel in `preview.html`, driven by the piece-066 use case (22-slider flat
list → 4 labelled collapsible group sections with group-level controls).

## What was done

- **Task 1 (diagnostic):** confirmed piece 066's fold ids via
  `grep -o 'id="fold-[^"]*"' work/pieces/066/066.svg | sort -u` — 21 ids across
  4 groups, matching the prompt's regex patterns exactly. (Prompt header says
  "22 folds" but the per-group breakdown sums to 21; the regex coverage is
  what matters and was unaffected.)
- **Task 2:** added `classifyFoldId(foldId)` helper just before
  `renderPanelsFirstScene` (preview.html:5606). Four regex patterns return one
  of `'pane-strip' | 'closure' | 'tab-flap' | 'cross-piece' | null`. Null is the
  flat-fallback signal.
- **Task 3:** added 12 CSS rules to the `#fold-controls` block at
  preview.html:48 covering `.fold-group`, `.fold-group-header`, `.fold-group-toggle`,
  `.fold-group-label`, `.fold-group-sum`, `.fold-group-body`,
  `.fold-group-controls`, and `.fold-master-row`.
- **Task 4:** replaced the entire `if (pathHingeMap.size > 0) { ... }` block
  inside `renderPanelsFirstScene` (now preview.html:~5885–6190). The new shape:
  collect slider descriptors → `hasGroups = !sceneMode && some(classify)` →
  branch into FLAT path (existing behavior) or GROUPED path (4 group sections
  in fixed order, each with header / collapse toggle / optional sum readout for
  `pane-strip` / optional master sub-slider for `tab-flap` + `closure` / per-
  member rows). Pane-strip group ships with **Equal (÷360°)** + **Flat** buttons
  + live Σ readout (turns green within ±5° of 360°). Tab-flap + closure groups
  ship with a master `−180°…+180°` sub-slider + Flat + 90° quick buttons.
  Cross-piece group starts collapsed.
- **One faithful clarification to Task 4:** gated `hasGroups` on `!sceneMode` to
  satisfy the prompt's "What NOT to Change" → "groups are only rendered in
  Bench mode (sceneMode = false); In sceneMode, perFoldSliders is cleared +
  appended-to per piece as before, with no group detection." The literal Task 4
  code did not include this gate; adding it preserves cluster-mode behavior
  unchanged, as the prompt explicitly states it should be.
- **Task 5 (verify-only):** confirmed `querySelectorAll('#per-fold-sliders .slider-row')`
  is used in all four places (lines 6651, 6775, 7005, 7094) — descendant
  selectors, no `>`. Grouped `.slider-row` rows nested inside `.fold-group-body`
  are still found.
- **Task 6 (verify-only):** confirmed `createSliderRow`'s
  `for (const k of Object.keys(dataset)) row.dataset[k] = ...` loop maps
  camelCase `pathId` → HTML attribute `data-path-id` (standard JS dataset API),
  so master-sub-slider queries `[data-path-id="..."]` will resolve.
- **Verification (code-side):** all 8 checklist items pass.
  1. JS syntax (extracted-script `node --check`) — clean.
  2. `grep -c classifyFoldId` → 3 (def + 2 calls).
  3. `grep -c fold-group` → 17 (CSS + JS).
  4. `grep -c pane-strip` → 10.
  5. `grep -c hasGroups` → 2 (decl + branch).
  6. No `per-fold-sliders >` direct-child selector exists.
  7. `grep -c buildFoldSliderRow` → 3.
  8. `classifyFoldId` (5606) defined before `renderPanelsFirstScene` (5630).

## Notes on the verification approach

CLAUDE.md says "use `node --check preview.html`" but Node 24+ rejects `.html`
extensions outright (`ERR_UNKNOWN_FILE_EXTENSION`). Fell back to extracting the
`<script>` body to a temp `.js` file and running `node --check` on that — same
syntax-correctness guarantee. Worth noting for future preview.html prompts so
they don't burn time on the wrong invocation.

Per CLAUDE.md "Notes for Every Session" + the prompt's verification protocol:
no HTTP server started. Browser-side checks are deferred to Alan post-merge —
captured below in the **Manual Tests** of the orchestration prompt + the PR
description.

## Branch / commit

- Branch: `claude/preview-html-fold-groups` (renamed from auto-generated
  `claude/infallible-jennings-830913` before first commit per CLAUDE.md
  branch-name convention).
- Commit SHA: (filled by Git on commit — see PR description).

## Open questions

None blocking. Two micro-observations Alan may want to confirm in the browser:

1. The prompt's expected fold-id list shows 7 tab folds (`taba`–`tabg`) +
   1 closure (`tabaa`) — 22 ids total — but the section header says
   "Tab-flap (6)" while listing 7 entries. The regex `^fold-tab[a-z]+-pane/`
   in `classifyFoldId` captures all 7 single-letter tabs (taba…tabg) into
   `tab-flap`, and `^fold-tabaa-/` captures the closure into `closure` first
   (the order matters — closure check runs before tab-flap check). So the
   grouping should be correct regardless of the prompt's count typo. Verify in
   browser: Tab flaps group should show 7 sliders, Closure should show 1.

2. The master sub-slider for `tab-flap` and `closure` groups uses a fresh
   `0°` default at render time — it does NOT reflect the current per-slider
   values. Adjusting individual tab sliders doesn't move the master. This
   matches the prompt spec; flagging for awareness only.

## Next-session handoff

- Alan: review PR, run the **Manual Tests** (browser, piece 066 in Bench mode)
  in the orchestration prompt, merge.
- Post-merge: orchestration prompt moves alongside this commit to
  `_archive/code-prompts/CODE_PROMPT_preview-html-fold-groups.md` with
  `status: shipped` + `shipped: 2026-05-10` already set; the bare filename is
  the only place it'll live, so the session note's `orchestration_prompt:`
  reference resolves correctly there.
- If `preview.html` ever stops loading 066 successfully, this prompt's CSS +
  helper + grouped-builder are all additive and safe to roll back as a unit —
  the FLAT-fallback path duplicates the pre-change behavior with no shared
  state with the new groups.
