---
date: 2026-05-04
start_time: "11:00"
end_time: "11:35"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Pick up the fold-mechanism workstream where the 0815 session ended (design pivot to "shared-edge polygon topology" as the next refactor). Read the last session note, fold piece 001 into the test bench alongside 066/069, and decide concretely how to approach the next iteration.

## What was done

### Read-in + scan

- Read `sessions/2026-05-04-0815_cowork_marker-bound-fold-ids.md` end-to-end. State of play: marker-bound fold ids convention shipped (with `fold-` prefix to dodge Affinity's cross-layer id-collision auto-rename); piece 066 improved 19 → 5 orphans; cylinder still folds into shards/slivers; design pivot was "shared-edge topology" but not yet specced.
- Inspected fold structure across the three test pieces:
  - **001**: long horizontal strip (28975 × 4871). 6 valley + 2 mountain folds. All marker-bound but with Affinity-renamed ids (`fold-tab-a` / `-a1` / `-a2` / `-a3`, `fold-tab-d` / `-d1`) — duplicate ids on multiple fold paths got auto-numbered.
  - **066**: long vertical saw-tooth strip (2963 × 18867). 19 valley (15 named + 4 unnamed) + 2 mountain (unnamed). 15 fold-paths bound to tabs/landings sharing x-coords. The hardest case.
  - **069**: compact 1:1 piece (3417 × 3342). 8 valley folds, **all unidentified**. Existing geometric adjacency works fine on it — the unidentified-fold path isn't broken; co-linear-marker-bound is the broken case.
- Spotted a stray duplicate at `work/pieces/066/001.svg` (byte-identical copy of `001/001.svg`, mtime 17:46 vs 17:47 May 4 — likely a misfiled Save-As). Deleted; canonical `066/066.svg` untouched.

### Decision pass: shared-edge topology, drilled in

Drafted a shared-edge topology refactor as `CODE_PROMPT_preview-html-shared-edge-topology.md` (replace step 5 of `buildFaceGraph` with polygon-edge-sharing lookup; index region edges by canonicalized endpoint pair; for marker-bound folds search only the marker's region's shared edges; for unidentified folds search the full list). Two reservations surfaced before handing it off:

1. **`passive` semantic narrowing** — the field bundles "no driven slider" with "inherits fold metadata" today; under shared-edge it'd narrow to "structural seam, no metadata." Reviewing all four `passive` consumers (BFS pass-1 filter, hinge `targetAngle` setter, slider registration, the buildFaceGraph step itself), the narrowing turned out to be a *tightening*, not a regression — every consumer already wanted "no slider, no metadata," and the old "fold-overflow into arm sub-region" subcase just dissolves. So this reservation is mostly cosmetic; a `kind: 'driven' | 'structural'` rename would be nice for honesty but isn't load-bearing.

2. **Wrong-shared-edge picker** — `pickClosestSharedEdge` scoring by minimum distance from edge midpoint to the fold's *infinite line* is one-criterion and silently mis-picks when an interior seam coincidentally crosses near a fold line, or when a corner-touch shared edge sits close to one. Mitigation: tighten the picker with direction-alignment, authored-segment-distance, and length filters. ~15 extra lines.

### Option-space honest sweep

Surfaced more alternatives than the original "shared-edge as drafted" framing acknowledged:

- **(α) Multi-tag during cuts.** Smaller diff: keep tag-based adjacency but allow each edge to carry multiple fold pathIds (post-cut tagging pass against ALL extended folds). Builds on existing infrastructure. Still EPS-tuning fragile.
- **(β) Cut-trim + shared-edge.** Address half-plane over-extension at source — each fold cuts only its authored extent, not the whole silhouette. Phantom strips disappear; shared-edge has fewer ambiguous candidates. Bigger refactor (~150–200 lines), needs careful polygon-clipping for thin-trapezoid or polyline cuts. Highest-confidence path to clean 066.
- **(γ) Diagnose-first.** Instrument `buildFaceGraph` to expose the face graph for inspection (JSON dump + 2D debug overlay rendering regions/shared-edges/folds in unique colors). Look at 066's actual graph before picking the algorithm. ~30 lines + UI plumbing. Smaller commitment; bigger informational payoff.
- **(δ) Panels-layer authoring.** Long-term direction: panels authored as closed polygons; cut step disappears. Out of scope for this round.

### Direction settled

Alan picked **(γ) diagnose-first**, with all three independent cleanups (passive→`kind`, tightened picker, debug instrumentation) acknowledged as worthwhile in their natural homes. Diagnostic harness lands first; algorithm refactor (with the cleanups bundled) lands second, informed by what the harness shows on 066.

The diagnostic CODE_PROMPT was drafted, then tightened with concrete DOM mount points (insert `#diagnostics-section` between `#rotation-section` and `#help`; mount overlay SVG inside `#canvas-host` after `renderer.domElement` with `position:absolute; inset:0; pointer-events:none; background:rgba(26,26,26,0.88)` so the 3D view fades behind a clearly-different 2D viewBox-space chart rather than looking like a misaligned projection). Sizes scale relative to viewBox diagonal so 069's compact piece and 001's long-strip piece both render readably. Top-right legend explicitly disclaims "2D viewBox-space; not aligned to 3D camera."

## Files touched

- `CODE_PROMPT_preview-html-face-graph-diagnostics.md` — NEW. ready-for-code. Six tasks: build shared-edge index post-sliver-filter (diagnostic only — adjacency unchanged), annotate each fold with top-3 candidate shared edges, attach `_diag` payload to `buildFaceGraph` return, add Dump button in new `#diagnostics-section` panel block, mount 2D SVG overlay in `#canvas-host` with seven render layers + legend, structured console summary per fold (`✓` / `✗` / `⊘`).
- `WORKPLAN.md` — `preview.html iteration` track: `next_action` repointed at the diagnostic CODE_PROMPT (was: marker-bound-fold-ids prompt, which already shipped); new recent-log entry for this session; footer last-updated note added.
- `work/pieces/066/001.svg` — DELETED. Byte-identical duplicate of `001/001.svg` (md5 `2abc30bb35625c7ef7f4750370ae7aa4`); canonical `066/066.svg` untouched.
- `CODE_PROMPT_preview-html-shared-edge-topology.md` — created mid-session as the original shared-edge refactor draft, then deleted when the direction pivoted to diagnose-first. Never committed; no decision-record value at this stage. The shared-edge name remains free for the post-diagnosis algorithm prompt.
- `sessions/2026-05-04-1100_cowork_face-graph-diagnostics.md` — this note.

No CLAUDE.md / LAYER-CONVENTIONS.md / SPEC-3D-VIEWER.md / ROADMAP.md changes — diagnostic harness is implementation, not convention. The Architectural-Decisions row for shared-edge topology will land with the algorithm refactor, not now.

## Open questions

1. **The actual decision the diagnostic harness should resolve.** What does 066's face graph look like once Alan can inspect it directly? Does the failure dominantly come from over-broad adjacency (→ shared-edge with tightened picker is the right next move) or from phantom strips between co-linear infinite-line cuts (→ cut-trim is primary, shared-edge follows)? The post-merge cowork session reading the diagnostic output picks the algorithm.

2. **Where the cleanups land.** `passive` → `kind: 'driven' | 'structural'` rename and the direction/segment/length filters in `pickClosestSharedEdge` both ride along with the algorithm refactor (the second prompt). The diagnostic harness deliberately doesn't touch them — one variable at a time.

3. **The 001 `fold-tab-a` / `-a1` / `-a2` / `-a3` cluster.** Acknowledged as authoring error. The diagnostic overlay will show how many of them resolve into ✓ vs ✗ once Code ships the harness — that's the information needed to decide whether 001 needs a re-author pass or whether the parser should grow tolerance for sibling auto-renames. Likely the former, but data first.

4. **Closure constraint** (the cylinder wrap-around so tab-aa lands on landing-aa). Still parked. Three options on the table from the 0815 session (author-most/derive-one, author-shape, closure-as-slider). Becomes the next thing to settle once the topology question is resolved on 066.

## Next-session handoff

**Likely next move:** Code session that ships `CODE_PROMPT_preview-html-face-graph-diagnostics.md`. Tasks 1–6 in the prompt; verification against all three test pieces (069 baseline, 001 with auto-rename cluster, 066 the point of the prompt); manual tests where Alan loads each, dumps JSON, toggles overlay, and posts the per-piece findings back into Cowork.

**After that ships, the next Cowork session:**
- Read 066's debug overlay screenshot or exported JSON.
- Pick between: shared-edge with tightened picker (algorithm-only, expecting cut-trim later), shared-edge AND cut-trim together, or multi-tag if the diagnostic surfaces evidence that's the right floor.
- Bundle the cleanups (`passive` rename, picker filters) into that algorithm prompt.
- Settle the closure constraint design as a parallel concern.

**Don't forget:** the diagnostic harness is permanent — it stays in `preview.html` as a debugging tool for any future piece's fold topology. Even after the algorithm refactor lands, the dump button + overlay keep their value.
