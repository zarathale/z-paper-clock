---
date: 2026-05-04
start_time: "22:00"
end_time: "22:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Reset and refresh thinking about how to handle orientation and awareness of paper pieces as they get folded, cut, and glued. Set up for a design conversation by reading the most recent code session (cut-trim ship), the spec / conventions / regions docs, and the actual authored SVG state of the priority pieces (001, 002, 066, 067, 069, 070, 113). Pure research turn — no files changed beyond this note.

## What was done

Read end-to-end:

- `sessions/2026-05-04-2103_code_preview-html-cut-trim.md` — most recent code session. Cut-trim algorithm shipped: each fold cuts only its own segment, extended only to the *nearest* silhouette boundary in each direction (not infinity). 066 result: 27 regions, 20/21 expected fold-edges, 13 still orphan. Residual failure mode is extension over-reach when the silhouette is concave-but-far along a near-vertical fold line. Marker→region map (`markerToRegionId`) added as forward-look infrastructure for the assembly engine (M4); not consumed yet.
- `sessions/2026-05-04-1100_cowork_face-graph-diagnostics.md` + `…1145_code_…` — the diagnose-first pivot. Diagnostic harness (Dump button + 2D overlay + console summary) is now permanent in `preview.html`.
- `CLAUDE.md`, `WORKPLAN.md`, `LAYER-CONVENTIONS.md`, `work/SPEC-3D-VIEWER.md`, `work/SPEC-REGIONS.md`.
- `preview.html`'s `parseSVG`, `parseFoldLayer`, `parseMarkerBoundFoldId`, `extendFoldsToSilhouette`, and `buildFaceGraph` (~lines 635–2132) to confirm what's actually consumed vs ignored.

Authored layer/id inventories pulled (via grep) for pieces 001, 002, 066, 067, 069, 070, 113. Layer-membership confirmed by walking nesting structure for 001 / 002 / 113.

## Key observations from the SVG inventory

The SVGs are accumulating concepts the convention doesn't yet name. Specific drift, piece by piece:

**001 and 002.** The `axles` layer carries `hole-f115`, `hole-g115`, `hole-f116`, `hole-g116` on 001 (and `hole-f113`, `hole-g113`, `hole-f114`, `hole-g114` on 002). These are *pin-holes* — static through-holes that accept *another piece's* wire. They're not rotation centers; conceptually they're closer to landings (cross-piece references) than to axles. The convention has no `pinholes` layer, so they live in `axles`.

**002.** Has `landing-tab-aa` in `marks`, mixing the documented `landing-<tab-letter><piece-number>` format. Plausibly a closure-constraint landing (the wrap-around where tab-aa lands on landing-aa within the same piece), plausibly a different concept, plausibly an authoring miss. Worth naming explicitly.

**066.** The canonical-but-difficult case. After cut-trim still 13 orphans. 14 marker-bound side folds at two shared x-coordinates; the residual failure mode is extension over-reach across the long strip.

**067.** Flat anchor body — no fold layer at all. Has `landing-c69`, `landing-d69`, `landing-e69`, `landing-f69` (cross-piece refs to 069) plus an `anchor-pivot` ID outside the canonical layer set. With no folds, `buildFaceGraph` doesn't run → marker→region resolution doesn't happen → the landings get no region assignment for the future assembly graph to read. Flat pieces *do* participate in assembly but the current face-graph-only pipeline silently skips them.

**069.** Anchor pendulum arm. 8 valley folds, all unidentified, working clean (14 regions, 11/11 markers resolved). Has `landing-a`/`landing-b` (canonical) AND `mark-h`/`mark-i` — a different category, probably construction / registration marks that aren't connection points. Plus another `anchor-pivot` outside canonical.

**070.** Has `id="tab"` in `folds-mountain` (no letter, non-canonical). Only `folds-mountain`, no valley.

**113 (and identical 114/115/116).** Layer names `mountain-folds` / `valley-folds` (reversed from canonical `folds-mountain` / `folds-valley`). `cutout` singular without `-N` suffix. `hole-f` / `hole-g` *bare*, no piece number — because the four pieces share one shape, the suffix gets resolved by which instance uses it. Plus Affinity-auto-renamed siblings (`fold-tab-a` × 4, `tab-e1`).

## The reset framing I surfaced

The current model is **cut-line-first**: silhouette + fold lines → derive regions → derive hinge tree. The strain isn't really algorithmic — it's that the SVGs are accumulating concepts the model doesn't name. A piece in this clock has at least four kinds of "orientation/awareness," and they're getting collapsed into the two bins the parser has (folds, and marks-or-axles):

1. **Internal subdivision** — fold lines partition the cut silhouette into panels (hinge tree, valley/mountain, adjacency). What `buildFaceGraph` is trying to do.
2. **Cross-piece connections** — tabs glue into landings on other pieces; pinholes accept other pieces' axles; pivots accept shared wires. NOT folds; they're points or panels with identity that some other piece refers to.
3. **Per-piece axes** — axles for rotation, pivots for swing, north for +0°. Local to the piece, drives how it animates.
4. **Assembly placement** — where this piece sits in the full clock. From `assembly.json` later, separate concern.

Four candidate framings put on the whiteboard:

**A. Sharper layer/id ontology.** Add categories: `pinholes` (static through-holes), `pivots` (anchor-style rotation that isn't a framework axle), `references` (mark-h type construction marks that aren't connection points). Audit catches `id="tab"`, `mountain-folds`, `cutout` (no suffix), `landing-tab-aa`, `anchor-pivot` as drift to uplift.

**B. Author panels directly.** Closed-polygon `panels` layer; folds become the shared edges between panels; the cut step disappears. Was option (δ) in the 2026-05-04 11:00 sweep, deferred as out-of-scope. Would also let 067 (no folds) participate trivially — panels-without-folds is just one panel.

**C. The unit of orientation is the panel, not the piece.** Today rotation+north drives the piece's slab around its axle. Once a piece has hinged panels, every panel has its own world frame from its parent. Cross-piece glue is panel-to-panel, not piece-to-piece. Matters for assembly transforms.

**D. Separate authored data from derived geometry.** Faithful-trace already decided this for *trace* vs *function*. Parallel case for connectivity: SVG authoritatively names connection points; the geometric inference (which region contains which marker, which panels are adjacent) stops trying to outsmart authoring.

Five questions for the next design conversation:

1. Does `axles` split (rotation / pinholes / pivots), or is the right move a single `attach-points` layer with id prefixes (`axle-`, `hole-`, `pivot-`)?
2. Try panels-as-polygons on one test piece (069 candidate — already mostly clean)?
3. What ARE `landing-tab-aa` (002) and `anchor-pivot` (067/069)? Both real artifacts that need names.
4. For 113–116 sharing one shape — does the SVG clone per piece (today) or does instance-id live in `assembly.json` with shared geometry? `hole-f` / `hole-g` (no piece suffix) suggest the shape doesn't know which of 113/114/115/116 it is.
5. Closure constraint on long strips (066, 001, 002 all have `tab-aa` ↔ `landing-aa` wraparound semantics) — its own kind of edge in the panel graph, sidecar field, or per-edge id on the panels layer?

## Open questions

Alan flagged a course change incoming after this session. The framings and questions above may or may not survive the pivot. Capturing them here so future-Alan or a future cowork session can either pick up the trail (if useful) or skip cleanly (if the new direction obsoletes them).

## Next-session handoff

Whatever direction lands next, this note is the snapshot of where the reset thinking got to before the pivot. Readable as either "useful context" or "abandoned line, skip" depending on where the new course goes. The diagnostic harness in `preview.html` (Dump + Overlay + console summary) is permanent regardless — any future fold-topology approach can use it to inspect what's happening on a per-piece basis.

No file changes this session beyond this note plus a small `.gitignore` tack-on (below). No commit-worthy code or doc work. Cowork commit will carry both.

## Addendum — `.gitignore` Affinity-lock pattern

Alan flagged Affinity lock-file clutter showing up in git status. Investigation: the existing `.gitignore` carried `.~lock.*.af#` (macOS / Linux Affinity / LibreOffice-style) and `*.af~` (editor backup). On Windows, Affinity Designer creates lock files named `<filename>.af~lock~` instead — neither existing pattern catches that form.

Five `<NNN>.af~lock~` files are currently *tracked* in git (`work/pieces/001`, `002`, `058`, `066`, `113`). Adding the pattern to `.gitignore` prevents *new* lock files from being staged, but the already-tracked ones will keep showing as modified until they're removed from the index.

Changes:

- `.gitignore` — added `*.af~lock~` (Windows pattern) alongside the existing `.~lock.*.af#` (mac/Linux) and `*.af~` (editor backup). Comment block above the patterns documents which pattern matches which platform so future-Alan / future-cowork can extend cleanly.

Follow-up Alan needs to run on his side (Cowork doesn't run git):

```
git rm --cached work/pieces/001/001.af~lock~ \
                work/pieces/002/002.af~lock~ \
                work/pieces/058/058.af~lock~ \
                work/pieces/066/066.af~lock~ \
                work/pieces/113/113.af~lock~
```

After the `git rm --cached`, the lock files stay on disk (Affinity needs them while documents are open) but stop being tracked. Subsequent `git status` will show them gone from the index; future lock-file appearances will be ignored on sight.
