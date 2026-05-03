---
date: 2026-05-03
start_time: "02:00"
end_time: "02:45"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Re-tighten `CODE_PROMPT_preview-html-v1b.md` against v1a's actual function signatures and flip status to `ready-for-code` (per the WORKPLAN preview.html-iteration track's recorded next action). Pivoted mid-session into archiving the prompt and handing off to a clean-start authoring pass.

## What Was Done

### Recon

- Read the current `CODE_PROMPT_preview-html-v1b.md` (status: draft; presumes only v1a structure).
- Read v1a's session note (`sessions/2026-05-02-1400_code_preview-html-v1a.md`) for the function signatures the prompt's placeholders were waiting on (`buildSlab(polygon, thicknessMm) → THREE.Group`, the `parsed` object shape, the `currentSlabGroup` / `currentAxleMarkers` globals).
- Read the head of `preview.html` (current state at repo root).
- Read `work/SPEC-REGIONS.md` (drafted earlier today; explicitly names this prompt as its first implementation).
- Listed `sessions/*preview-html*` to see the cumulative drift since v1a — six follow-up passes (cut-layer, texture-flip, back-face-mirror, perf, thickness-fix, axle-rotation).

### Pivot point

Surfaced three changes-since-v1a that the prompt didn't anticipate, and asked Alan to settle scope before re-tightening:

1. The axle-rotation pass added a rotation-pivot wrapping `THREE.Group` that v1b's hinge hierarchy must coexist with (proposed: pivot wraps the whole fold tree).
2. SPEC-REGIONS.md now exists and explicitly names this prompt as its first implementation (proposed: add as upstream concept doc; prompt's algorithm description stays authoritative).
3. Several since-v1a constraints (texture flip on front face, back-face mirror via `BackSide`, render-on-demand perf loop, silver-cylinder axles + brass-gold north sphere, thickness via `MM_PER_UNIT`, 0.4 mm default) need to be either preserved as "What NOT to Change" entries or threaded through the new tasks.

Alan's response: cancel the re-tightening, archive the v1b draft, start clean.

### Archival

- Updated `CODE_PROMPT_preview-html-v1b.md` front matter: `status: archived`, `archived: 2026-05-03`, `archived_reason: superseded by clean-start v1b restart`.
- Replaced the original draft caveat (italic header below front matter) with an archive header explaining: cumulative drift since v1a outpaced the prompt's design assumptions; the body is preserved as the design record of the original v1b approach; refer to `CLAUDE.md` / `ROADMAP.md` / `WORKPLAN.md` for current state and to the new v1b prompt (when authored) for the active task list.
- Created `_archive/code-prompts/` at repo root (new directory; no archive folder existed at root previously — `work/_archive/` and `source/_archive/` are scoped to their subtrees).
- Moved the prompt: `CODE_PROMPT_preview-html-v1b.md` → `_archive/code-prompts/CODE_PROMPT_preview-html-v1b.md`. Used `mv` so git can detect the rename.

### Downstream doc-sweep

- **`WORKPLAN.md` — preview.html iteration track:** rewrote `next_action` from "re-tighten…" to "author a clean-start v1b CODE_PROMPT against the current state of preview.html — not the v1a session note alone…" Added a new recent-log entry pointing at this session note.
- **`WORKPLAN.md` — regions track:** rewrote `next_action` from "add SPEC-REGIONS.md reference to CODE_PROMPT_preview-html-v1b.md" to "bake SPEC-REGIONS.md into the clean-start v1b prompt (when authored) as upstream conceptual context."
- **`ROADMAP.md` — M0.6 task table row 0.6.9:** updated the Notes column from "is `status: draft` and depends on v1a's actual function signatures…" to "the original draft prompt was archived 2026-05-03 to `_archive/code-prompts/`… after the cumulative drift on `preview.html` since v1a outpaced its design assumptions. Author a clean-start prompt against the current `preview.html`, with `work/SPEC-REGIONS.md` as the upstream concept doc."
- **`work/SPEC-REGIONS.md` — Relation-to-other-docs section:** softened the explicit filename pointer. Was "`CODE_PROMPT_preview-html-v1b.md` — v1b's polygon-cut … is the first implementation of this spec. That prompt should reference this document." Now refers to "the v1b prompt for `preview.html` (clean-start authoring pending; the original draft was archived…)".
- Did **not** edit: `CLAUDE.md` (status table row "v1b (polygon cut + hinge animation) … pending" remains accurate — the work is still pending, just under a different prompt). `PROJECT-STATE.md` ("v1b queued" line remains accurate). `work/SPEC-3D-VIEWER.md` ("v1b territory" / "v1b+ concern" — abstract enough not to drift).

### Constraints the clean-start prompt must address

Captured here so the next Cowork session that authors the new prompt has them all in one place:

- **Axle rotation pivot composition.** v1a's per-piece axle rotation slider attaches a `THREE.Group` between the scene root and the slab. Whatever the new v1b does about hinge hierarchy must compose with that; my reading is the rotation pivot wraps the whole fold tree (pivot above the root slab, hinges below), so the entire folded assembly rotates as one rigid body around the active axle. Alan's first response on the AskUserQuestion poll picked that option before the pivot to archive — useful signal but not a closed decision; revisit when authoring the new prompt.
- **Silhouette extraction priority chain.** Tier 1 = `<g id="silhouette">` with `cutaway` / `cutaway-N` ids; Tier 2 = PNG alpha; Tier 3 = largest-colored-path heuristic. The new prompt's polygon-cut step needs to feed off whatever Tier returned the silhouette polygon, not assume the alpha-marching-squares path of v1a.
- **Axle marker convention.** Magenta sphere (v1a) → silver cylinder anchored *outside* the rotation pivot (axle wire is fixed to framework); optional brass-gold sphere `id="north"` anchored *inside* the pivot for orientation. v1b's "re-route axle markers to the panel containing them" (Task 6 in the archived prompt) needs to know about this distinction.
- **Texture flip on front face.** The `tex.flipY = false` line was dropped on 2026-05-02; UVs are recovered from the shape coords via bbox offset + Y-un-flip. v1b's per-panel `buildSlab` already inherits this; preserve it.
- **Back-face mirroring.** `BackSide` material on a single back-cap geometry; do NOT introduce a Y-rotation that flips coordinates. v1b's per-panel slabs inherit; preserve.
- **Render-on-demand performance loop.** `requestRender` flag-driven render, not `requestAnimationFrame` always-on. Per-fold and global fold sliders should mark `requestRender = true` on input but not rebuild geometry.
- **Thickness extrusion semantics.** `T = thicknessMm` directly (after the 2026-05-02 rename of `UNITS_PER_MM` → `MM_PER_UNIT`). Default 0.4 mm. v1b's per-panel rebuild on thickness-slider change needs to operate on N geometries instead of 1; the original prompt's Task 7 already noted this but the rename is post-prompt.
- **Sliver filter calibration.** The archived prompt's Δ = 0.5% of silhouette-bbox diagonal is geometric and scale-invariant; carry forward unless the cut-layer pass introduced a reason to revisit (it didn't).
- **Test SVGs.** `inbox/069.svg` and `inbox/066.svg` were the original test inputs. Verify these still exist and have the expected fold-line content before authoring the new verification checklist (didn't verify in this session).

### V1 unified prompt status (parked)

The `CODE_PROMPT_preview-html-v1.md` unified prompt was split into v1a + v1b on 2026-05-02. v1a shipped; v1b is now archived without shipping. The unified prompt's status is technically "half-shipped, half-superseded" and arguably also wants an archival/decision-record pass. Did not touch in this session — parking for the planning beat to handle if it surfaces.

## Open Questions

- The clean-start v1b prompt's authoring is the next-action on the preview.html iteration track. Open scope question: does the new prompt also fold in the axle-rotation composition decision (rotation pivot wraps the fold tree as Alan's poll-pick suggested), or does that get its own decision row?
- Is `_archive/code-prompts/` the right home for never-shipped CODE_PROMPT drafts, or should it just be `_archive/` flat (since the volume is low)? Easy to revisit later if a second one accumulates.
- `share/` directory contains hand-curated snapshots (`ROADMAP.md`, `SPEC-3D-VIEWER.md`, `preview.html`, README, a few SVGs). These predate today's PROJECT-STATE / WORKPLAN / SPEC-REGIONS work and reference the old v1b prompt path. Did **not** update `share/` in this session — it's already lagging on other doc work, refreshing it should be its own deliberate pass. Flag for the next planning beat.

## Next-Session Handoff

1. (Cowork) Author the clean-start v1b CODE_PROMPT against the current `preview.html`. Reads from: this note's "Constraints the clean-start prompt must address" section, `work/SPEC-REGIONS.md`, and the actual current `preview.html` file (not just v1a's session note). Possible filename: keep `CODE_PROMPT_preview-html-v1b.md` at repo root as the new clean-start (the archived original lives at `_archive/code-prompts/` with the same name — that's fine, paths differ).
2. (Cowork, optional) Decide whether `CODE_PROMPT_preview-html-v1.md` (the unified-then-split prompt) wants its own front-matter status update / archival pass. Currently still at repo root with `status: superseded` (or whatever it was set to during the 2026-05-02 split — verify).
