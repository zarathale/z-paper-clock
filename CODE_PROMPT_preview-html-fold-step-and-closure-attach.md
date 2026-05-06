---
status: shipped
started: 2026-05-05
shipped: 2026-05-05
owner: Zarathale (Alan)
target: preview-html-fold-step-and-closure-attach
---

_Shipped 2026-05-05; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

# CODE_PROMPT — fold-step prefix + same-piece closure attach in `preview.html`

Surgical addition. Two parser extensions to the panels-first pathway in `preview.html`, mirroring the same changes already shipped on `claude-work/scripts/build_assembly_graph.py`. Single file touched.

---

## What You Are Doing and Why

The 2026-05-05 bob-batch authoring session ratified two new panels-first convention elements (DECISIONS row #9, LAYER-CONVENTIONS.md updated):

**A — Fold-step ordinal prefix.** Fold ids may carry an optional leading `<step>-` before `fold-`, encoding the order in which the fold fires during a phased fold sequence. Same step = simultaneous. Example from 095: `1-fold-pane3-pane4` (valley, central, step 1), `2-fold-pane2-pane3` (mountain, step 2), `3-fold-pane5-pane6` (valley, step 3). Affinity Designer prefixes digit-leading ids with `_` for SVG-spec compliance, so `1-fold-pane3-pane4` arrives in the SVG as `id="_1-fold-pane3-pane4"`. The author's literal sits in the `serif:id` attribute on the same element.

**B — Same-piece closure attach via panel-id.** The `attach-points` layer gains the form `attach-<panel-id>` (and `back-attach-<panel-id>`) where the suffix matches a panel id of the SAME piece. Distinguished from cross-piece `attach-<letter><piece>` by panel-set lookup. Example from 095: `back-attach-pane1`, `back-attach-pane2`, `back-attach-pane3`.

Both extensions need to land in `preview.html`'s panels-first parser so that 095 (and future pieces using these forms) renders the way the audit script already understands them.

---

## Prerequisites — confirm before starting

- `claude-work/scripts/build_assembly_graph.py` recognizes both extensions and produces the expected output for piece 095 (5 folds resolved, all with `step` populated; 3 closure-attaches in `graph.closure_attaches`). Run `python3 claude-work/scripts/build_assembly_graph.py` to confirm.
- `LAYER-CONVENTIONS.md` reflects both extensions (folds section gains `<step>-fold-` form; attach-points section gains `attach-<panel-id>` form; Parser rules section gains the fold-step rule and the Affinity-underscore rule).
- `claude-work/DECISIONS.md` row #9 captures both convention extensions.
- `work/pieces/095/095.svg` exists and contains both convention forms (5 folds, 3 attach-points). The headless preview-render daemon at `claude-work/scripts/watch_and_render.py` is the easiest verification path.

---

## Read These Files First

1. `LAYER-CONVENTIONS.md` — folds-valley/folds-mountain section (the `<step>-fold-` form), attach-points section (the `attach-<panel-id>` form), Parser rules section (fold-step prefix rule + Affinity underscore prefix rule).
2. `claude-work/DECISIONS.md` row #9 — full reasoning + downstream effects.
3. `claude-work/scripts/build_assembly_graph.py` — `parse_fold_bindings` (lines ~107-177; mirror its step-extraction logic) and `parse_connection_id` (lines ~190-260; mirror its same-piece resolution logic). The Python implementation is reference-quality for the JS port.
4. `preview.html` — `parsePanelsFirstFolds` (the function to extend for fold-step parsing) and `parseConnectionGraph` / `parsePanelsFirst` / wherever attach-points are extracted (the function to extend for same-piece closure resolution).
5. `work/pieces/095/095.svg` — the canonical test piece with both convention forms in real authored use.
6. `work/pieces/094/094.svg` — the regression check; doesn't use either new form, must continue to render the same way.

---

## Target File Structure Changes

```
preview.html                                                   ← UPDATE: extend parsePanelsFirstFolds + attach-points parser
CODE_PROMPT_preview-html-fold-step-and-closure-attach.md       ← (this file; status flips to shipped on merge)
```

No new files. No new dependencies.

---

## Numbered Tasks

### 1. Extend `parsePanelsFirstFolds` for fold-step prefix + Affinity underscore

In `parsePanelsFirstFolds`, before the existing `fold-` prefix check, normalize the id and extract optional fold-step.

Replace the existing:
```js
if (!id.startsWith('fold-')) continue;
const rest = id.slice('fold-'.length);
```

With:
```js
// Affinity Designer prefixes ids that start with a digit with `_` (SVG-spec
// compliance — ids must begin with letter or underscore). Strip the leading
// `_` to recover the authored form. (`serif:id` on the same element preserves
// Alan's literal, but normalizing the `id` is sufficient.)
const normalized = id.startsWith('_') ? id.slice(1) : id;

// Optional leading `<step>-` prefix (positive integer ordinal). Same step
// number across multiple folds means "fire simultaneously" during a phased
// fold sequence. Strip before applying the `fold-` prefix check.
let step = null;
let rest;
const stepMatch = normalized.match(/^(\d+)-fold-(.*)$/);
if (stepMatch) {
  step = parseInt(stepMatch[1], 10);
  rest = stepMatch[2];
} else if (normalized.startsWith('fold-')) {
  rest = normalized.slice('fold-'.length);
} else {
  continue;
}
```

Then in the `fold` object construction (the one with `id, polarity, a, b, descriptive, defaultAngle, geometry, sourceIndex`), add `step`:
```js
const fold = {
  id, polarity,
  a: pair ? pair.a : null,
  b: pair ? pair.b : null,
  descriptive: pair ? null : rest,
  defaultAngle: pair ? pair.defaultAngle : null,
  geometry: null,
  step,                             // NEW
  sourceIndex: out.length
};
```

The existing `id` field in the fold record stays the literal SVG id (with `_` prefix if Affinity added it); `step` and `rest` are derived from the normalized form. Downstream renderers consuming `fold.id` for display should keep working as-is; nothing currently displays the id.

### 2. Wire fold-step into the slider UI label

The hinge-tree fold sliders are listed in the left panel (one per fold; labels read e.g. `fold-pane1-pane2`). Update the label to include the step when present:

- If `fold.step != null`: label as `<step>-fold-<a>-<b>` (e.g. `1-fold-pane3-pane4`).
- If `fold.step == null`: label as `fold-<a>-<b>` (current behavior).

The label is a UI nicety — it makes 095's three-step pattern visible at a glance. No behavioral change to slider semantics.

### 3. Extend the attach-points parser for same-piece closure

Find where attach-points are parsed in the panels-first pathway (likely inside `parsePanelsFirst` or a sibling function that walks `<g id="attach-points">`). The current logic produces records with `kind: 'attach' | 'landing' | 'pivot' | 'hole' | 'letter-target' | 'unknown'` and `partner: <piece-id>` for cross-piece kinds.

Add same-piece resolution. The parser already has access to the panels map (`panels` in `parsePanelsFirst`). When parsing an attach-point id of the form `attach-<rest>` (or `back-attach-<rest>` after side-stripping), check whether `<rest>` is a key in the panels map. If yes, classify as `attach-same-piece` with `panel: <rest>`, no partner. If no, fall through to the existing cross-piece `<letter><piece>` parsing.

Mirror the same logic for `landing-<rest>`: if `<rest>` in panels, classify as `landing-same-piece` with `panel: <rest>`.

Reference implementation in `claude-work/scripts/build_assembly_graph.py` `parse_connection_id` (after the side-stripping block, in the `attach-` and `landing-` branches). The Python version takes `panels` as a parameter; mirror that in JS.

### 4. Surface closure attaches inert in the parsed bundle

Add a `closureAttaches: [...]` array to the panels-first parsed bundle (alongside `attachPoints`, `marks`, etc.). Populate from the attach-points walk: each entry `{id, side, panel, kind: 'attach-same-piece' | 'landing-same-piece'}`.

The renderer doesn't need to draw anything new today — this data is captured for the multi-piece scene assembly prompt that comes next. For now, just log the count in the panels-first console diagnostics.

### 5. Update the panels-first console summary

Where the current console.log emits panel count, fold count, hinge sub-roots, attach-points count, and marks count, also emit:

- Distinct fold-step set (e.g. `fold-steps: [1, 2, 3]`) — only when at least one fold has a step.
- Closure-attaches count (e.g. `closure-attaches: 3 (back-attach-pane1, back-attach-pane2, back-attach-pane3)`).

This makes the new convention forms visible in the daemon's `<NNN>.log` output.

---

## Verification Checklist

Run the daemon (`watch_and_render.py`) on Alan's bench and trigger renders by writing to `claude-work/state/render-triggers/`.

1. **095 — both extensions exercised.** Render `preview.html?piece=095`. Banner reads `panels-first ✓ — 7 panels, 5 folds, root: pane1` (or whichever root the BFS picks; 7 panels from authored set after `main-alan-to-delete` removal). Sliders should be labeled with steps: `1-fold-pane3-pane4`, `2-fold-pane2-pane3`, `2-fold-pane4-pane5`, `3-fold-pane1-pane2`, `3-fold-pane5-pane6`. Console log includes `fold-steps: [1, 2, 3]` and `closure-attaches: 3`. Folding all sliders to 90° produces the accordion-wrap-around-bob shape.
2. **094 — regression check.** Render `preview.html?piece=094`. Banner reads `panels-first ✓ — 7 panels, 6 folds, root: pane2` (existing behavior). No `fold-steps` line in console (no fold-step authored on 094). Closure-attaches count is 0. Visual render unchanged from current behavior.
3. **069 — regression check.** Render `preview.html?piece=069`. Banner reads `panels-first ✓ — 11 panels, 10 folds, root: abc`. No regressions.
4. **058 — cut-line-first regression.** Render `preview.html?piece=058`. Banner reads `cut-line-first (legacy) parser`. Legacy pathway untouched.
5. **No console errors** anywhere across the verification renders.

---

## What NOT to Change

- The existing cut-line-first parser (`buildFaceGraph`, `extendFoldsToSilhouette`, cut-trim, the diagnostic harness). This work touches panels-first only.
- The piece-id loader (M0.6.14) — reused as-is.
- The render-on-demand `requestRender()` loop, three.js material setup, lighting, camera controls — all reused.
- `claude-work/scripts/build_assembly_graph.py` — the Python parser is read-only here; mirror its logic, don't import or shell out to it.
- `LAYER-CONVENTIONS.md` and `DECISIONS.md` — convention work is already done in chat (DECISIONS row #9). Don't restate.
- The panels-first dispatch banner format — keep `panels-first ✓ — N panels, M folds, root: X`. The fold-step set lives in the per-piece console diagnostic, not the banner.

---

## Manual tests (post-merge)

| Test | Pre-condition | Action | Expected |
|---|---|---|---|
| Fold-step labels on 095 | 095 panels-first authored with fold-step ids | Open `preview.html?piece=095` | 5 sliders labeled with `<step>-fold-<a>-<b>` form |
| Closure-attaches console | 095 has 3 `back-attach-<panel-id>` | Open browser console after loading 095 | `closure-attaches: 3` line printed |
| Affinity underscore tolerance | 095's fold ids start with `_` per SVG-spec compliance | Open 095 | Folds parse cleanly; no "no matching marker" or "could not be parsed" banners |
| Cross-piece attach unaffected | 094's `attach-a95` form is cross-piece | Open `preview.html?piece=094` | `attach-a95` still resolves as cross-piece (partner = 95); no false "same-piece" classification |
| 069 unchanged | 069 uses the original `fold-<a>-<b>` form | Open `preview.html?piece=069` | 10 fold sliders, all without step prefix |

---

*Drafted 2026-05-05 in cowork session continuation. Conventions ratified in DECISIONS row #9. Audit script reference implementation at `claude-work/scripts/build_assembly_graph.py`.*
