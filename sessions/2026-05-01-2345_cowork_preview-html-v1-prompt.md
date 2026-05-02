---
date: 2026-05-01
start_time: "23:45"
end_time: "01:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Close the three architecture questions left open at the end of the prior 23:00 session, run the Affinity SVG round-trip test that the v2 writeback model depends on, and produce `CODE_PROMPT_preview-html-v1.md` for the next Code session.

---

## What was done

**Three architecture questions resolved.**

1. *v1 scope* — confirmed v1 ships **read-only first**. Writeback (v2) is a separate prompt after v1.
2. *Fold-tree validation* — folded into v1 by construction (the viewer can't render at all without building a fold tree). Original "axles → root" convention had already been replaced in the prior session by `<g id="root">` marker (with largest-by-area fallback); on 069 the largest-by-area heuristic resolves to BASE with a 2.4× margin over the next panel, so the fallback is robust there.
3. *Fold-tree algorithm pinned.* BFS from root over the panel adjacency graph. Adjacency = two polygons sharing a fold-line segment of nonzero length. Each polygon edge gets tagged with its source (silhouette-boundary or fold-line F_k) at cut time, not reconstructed post-hoc. One SVG path can drive multiple hinges at the same angle — confirmed as the intended encoding for 069 paths 2 and 3, which physically *are* one continuous crease bisected by the BASE-row horizontal fold and produce two parent-child relationships in the tree (BASE↔L_WALL lower, T_WALL↔TL_CORNER upper). Algorithm handles this without special logic.

**Affinity round-trip test executed.** Created `_roundtrip-test-069.svg` at repo root by inserting two test layers into a copy of `inbox/069.svg`:

- `<g id="thickness"><text x="0" y="0" visibility="hidden">1.5</text></g>`
- `<g id="root"><ellipse id="root-marker" cx="1760" cy="1746" rx="40" ry="40" style="fill:#00ffff;"/></g>`

Alan opened in Affinity Designer (both layers visible in the Layers panel with correct names), re-exported as `_roundtrip-test-069-exported.svg`, and Claude diffed the two files. Findings:

| Element | Verdict |
|---|---|
| `<g id="thickness">` and `<g id="root">` group structure + IDs | ✓ preserved |
| `id="root-marker"` on the marker | ✓ preserved |
| Text content `1.5` | ✓ preserved |
| Marker fill color (`#00ffff` → `#0ff`, CSS short-form equivalent) | ✓ preserved |
| Marker shape (`<ellipse rx=40 ry=40>` → `<circle r=166.667>`, auto-normalized when rx=ry) | ✓ preserved (geometry intact) |
| `visibility="hidden"` on `<text>` | ✗ stripped; Affinity adds default font styling and the text becomes visible at viewBox (0,0) |
| Coordinate system | rescaled 4.166667× across the entire document (viewBox grew from 3417×3342 → 14238×13925, all paths/ellipses/stroke-widths scaled proportionally). Cosmetic — visually identical render, doesn't break viewer (works in viewBox space at any scale). |

Alan called the visibility loss a non-issue: the meta layers (folds, marks, axles) all render in bright authoring colors and get toggled off in Affinity's layer panel as needed. Thickness fits the same pattern; the visible "1.5" is acceptable as authoring noise. v1 ships with the encoding as designed. Test files cleaned up by Alan.

**Sliver filter strategy confirmed.** v1 uses the geometric signature ("drop regions whose vertices all sit within Δ of a single fold line") not the size-based 1% threshold from the validation passes. Δ = 0.5% of the silhouette-bbox diagonal. The size-based filter was confirmed fragile in the 066 validation pass (smallest-real-panel : largest-sliver gap was only 2× on 066 vs. 12× on 069); the geometric filter is scale-invariant.

**`CODE_PROMPT_preview-html-v1.md` written** at repo root. 12 numbered tasks, 10-step verification checklist, scope exclusions, branch/commit/PR conventions, manual tests. Targets Code mode (branch `claude/preview-html-v1`, `gh pr create` flow). Front matter `status: ready-for-code`. Path: `/Users/mainstage/Documents/GitHub/z-paper-clock/CODE_PROMPT_preview-html-v1.md`.

The prompt covers: drag-drop SVG load on `file://`; canonical-layer parsing (folds-valley, folds-mountain, axles, marks-skip, root, thickness); silhouette extraction with both branches (alpha-based primary, SVG-path fallback for fully-opaque PNGs like 066); polygon cut via half-plane intersections with edge tagging at cut time; geometric sliver filter; adjacency graph + BFS fold tree; three.js setup with the three-material slab split (front/back/edges) that resolved the 069 cream-bleed bug; hinge hierarchy with `pathId → [hinge, hinge, ...]` map for the multi-hinge-per-path case; axle marker spheres; live rebuild on slider changes (cheap for fold, debounced for thickness); console diagnostics block. CDN choices: three.js r128 (matches 069 viewer precedent), OrbitControls r128 from jsdelivr, polygon-clipping@0.15.7 from unpkg.

**Doc-sweep.** No renames, retirements, or replacements this session — only additive (new prompt file, new session note, no edits to CLAUDE.md, ROADMAP.md, SPEC, or any existing file). No downstream references to update.

---

## Files touched

- `CODE_PROMPT_preview-html-v1.md` — NEW (~25 KB, ready-for-code)
- `sessions/2026-05-01-2345_cowork_preview-html-v1-prompt.md` — NEW (this file)

Test artifacts created and deleted within the session:
- `_roundtrip-test-069.svg` — created from `inbox/069.svg` + 2 hand-inserted layers; deleted by Alan after diff
- `_roundtrip-test-069-exported.svg` — produced by Alan's Affinity re-export; deleted by Alan after diff

---

## Open questions

- **Two SPEC revisions still queued** (held since the prior session A run, before the architecture conversation expanded). Do not block this prompt.
  - Layer model: marks / tab-X / landing-X naming convention pinning in `work/SPEC-3D-VIEWER.md`.
  - Scan-as-texture material model + "downsample-for-viewer" pipeline stage (the "viewer needs a smaller texture than the archive scan" question).
- **v2 writeback prompt** (separate; comes after v1 ships and we've seen what we want to be able to author back into the SVG via the viewer). Encoding is real per the round-trip test; no remaining encoding-design risk.
- **Convention question about `folds-mountain` on 069.** Not authored yet on 069 (legitimately empty — no mountain fold on this piece), but worth a book check during the v1 session in case the convention has been missed.
- **Tabs c–g connectivity** for the eventual M4 assembly graph. Not needed for v1.

---

## Next-session handoff

The very next session should be a Code session running `CODE_PROMPT_preview-html-v1.md`. Expected length: substantial — this is the largest single CODE_PROMPT to date and ships a piece-agnostic 3D viewer prototype. Code mode opens the branch, builds preview.html, runs the verification checklist against `inbox/069.svg` and `inbox/066.svg`, writes its own session note, and opens the PR.

If Alan flips to Cowork-direct (precedent from the 069 viewer build), the prompt body still applies as the implementation spec — just strip the branch/commit/PR/end-of-session sections.

After v1 ships and Alan has used it on a few pieces, follow up:

1. Write `CODE_PROMPT_preview-html-v2-writeback.md` (Export-Updated-SVG button, surgical write-back of path id and thickness text-content).
2. Settle the two queued SPEC revisions in a Cowork session.
3. Re-evaluate whether the prototype graduates into `work/viewer/` (the production Vite app, M3) or stays at repo root indefinitely as a tool.
