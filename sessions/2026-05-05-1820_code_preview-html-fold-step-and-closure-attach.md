---
date: 2026-05-05
start_time: "18:20"
end_time: "18:20"
mode: code
participant: Zarathale (Alan)
target: preview-html-fold-step-and-closure-attach
orchestration_prompt: CODE_PROMPT_preview-html-fold-step-and-closure-attach.md
---

## Goal

Land the panels-first parser extensions in `preview.html` that mirror the two convention additions ratified earlier in the day on the Python audit script (`build_assembly_graph.py`): fold-step ordinal prefix (`<step>-fold-...`) with Affinity's leading-`_` normalization, and same-piece closure attach via panel-id (`attach-<panel-id>` / `back-attach-<panel-id>`).

## What was done

Five surgical edits in `preview.html`:

- **`parsePanelsFirstFolds`** — strip leading `_` (Affinity SVG-spec compliance for digit-leading ids), regex-extract optional `<step>-fold-` ordinal, add `step` field to each fold record. Two-panel resolution and curved/descriptive fallback unchanged.
- **Slider label synthesis** — replace raw `fold.id` in the per-fold-slider label with a synthesized `<step>-fold-<a>-<b>` (or `fold-<a>-<b>` when no step). Descriptive folds fall back to the underscore-stripped raw id. Datasets and `pathHingeMap` lookups still use the literal `fold.id` so the render-side wiring is unaffected.
- **`parsePanelsFirstAttachPoints`** — function now takes `panels` Map. After side-stripping (`back-` + recognized prefix), classifies `attach-<suffix>` / `landing-<suffix>` as same-piece closure (`attach-same-piece` / `landing-same-piece`) when `<suffix>` matches a known panel of the piece. Otherwise the entry falls through with no `kind` (cross-piece resolution remains the next prompt's responsibility). Returns `{ attachPoints, closureAttaches }`.
- **Bundle wiring** — the panels-first parsed bundle gains a `closureAttaches: [...]` array alongside `attachPoints` / `marks`.
- **Console summary** — emit `fold-steps: [...]` when any fold has a step; emit `closure-attaches: N (id, ...)` when any are present.

Mirrors the Python parser at `claude-work/scripts/build_assembly_graph.py` (`parse_fold_bindings`, `parse_connection_id`); Python is unchanged.

### Verification (browser, http://localhost:8770/preview.html?piece=...)

| Piece | Banner | Notes |
|---|---|---|
| 095 | `panels-first ✓ — 6 panels, 5 folds, root: pane2` | Sliders labeled `1-fold-pane3-pane4`, `2-fold-pane2-pane3`, `2-fold-pane4-pane5`, `3-fold-pane1-pane2`, `3-fold-pane5-pane6`. Console: `fold-steps: [1, 2, 3]`, `closure-attaches: 3 (back-attach-pane3, back-attach-pane2, back-attach-pane1)`. |
| 094 | `panels-first ✓ — 7 panels, 6 folds, root: pane2` | 6 sliders, all `fold-<a>-<b>` (no step prefix). No `fold-steps` / `closure-attaches` lines. Cross-piece `attach-a95` correctly stays cross-piece (suffix doesn't match a panel of 094). |
| 069 | `panels-first ✓ — 11 panels, 10 folds, root: abc` | 10 sliders with `fold-<a>-<b>` form. No regressions. |
| 058 | `cut-line-first (legacy) parser` | Legacy pathway untouched. |

No console errors or warnings across all four loads.

Note: 095 reports 6 panels (not 7 as the prompt anticipated) — the SVG no longer contains `main-alan-to-delete`. The prompt allowed for either count and any BFS root choice.

## Branch / commit

- Branch: `claude/preview-html-fold-step-and-closure-attach` (renamed from worktree-default `claude/youthful-kilby-5f1012` before first commit, per CLAUDE.md naming rules)
- Commit SHA: TBD (filled by post-commit ritual)

## Open questions

None.

## Next-session handoff

The next prompt in this thread is the multi-piece scene assembler that will consume `closureAttaches` + cross-piece edges out of `attachPoints` to wire neighbors together in the same scene. The data is now exposed on the panels-first bundle; renderer changes belong in that prompt.

Closure constraint authoring (the cylinder wrap-around so `tab-aa` lands on `landing-aa`) remains in design — three options on the table per CLAUDE.md (author-most/derive-one; author-shape; closure-as-slider). Not blocked by this work.
