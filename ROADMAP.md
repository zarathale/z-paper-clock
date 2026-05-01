# ROADMAP.md — Build Sequence for the 3D Paper-Clock Viewer

This is the detail-layer plan for building the 3D viewer described in `work/SPEC-3D-VIEWER.md`. It tracks every concrete unit of work across the six SPEC milestones plus a follow-on mobile milestone, with status, effort estimates (revised as we learn), dependencies, and pointers to the orchestration prompt or session note that closed each unit. Read it at session start to know what's in flight, what's blocked, and what's next.

Companion docs:

- `work/SPEC-3D-VIEWER.md` — design source of truth (per-piece data model, viewer behavior, tech stack, milestones at a high level).
- `CLAUDE.md` — working conventions (Cowork/Code lanes, sessions/, git workflow, versioning). The status table in CLAUDE.md is the high-level mirror of this roadmap; this doc is the detail.
- `CODE_PROMPT_*.md` (per task) — the per-milestone or per-version handoff to Code mode. Not a substitute for this doc; it's the executable form of one row.
- `sessions/` — chronological record of what actually happened.

---

## Status legend

- **not-started** — no work yet
- **in-progress** — actively underway in one or both modes
- **blocked** — waiting on a dependency or open question
- **done** — finished and merged
- **deferred** — intentionally pushed to a later milestone or version

When a row flips to **done**, append a pointer to the closing session note in the Notes column (`see sessions/YYYY-MM-DD-HHMM_…`).

---

## Milestone index

Plain-text labels alongside the M-numbers. Use the long form on first reference in any communication.

| ID | Name | Status | Est. h | Actual h | Depends on | Notes |
|---|---|---|---|---|---|---|
| M0.5 | Chunk-and-crop onboarding + pipeline reshape | in-progress | 12 | — | none | **Reshaped 2026-04-30** (later same day) from "rescan + re-bring-up" to "chunk-and-crop" after confirming the home scanner can't fit a whole plate. Workflow: capture multi-piece chunks → archive to `source/scans-chunks/` → hand-crop pieces in editor → save to `source/pieces/NNN.png`. Pipeline starts at `02-trace.py` reading `source/pieces/` directly. `01-crop.py` archived. `pieces.csv` expanded to 123-row master index (bbox columns dropped). Includes authoring the piece-scan ingest skill. See `sessions/2026-04-30-1900_cowork_chunk-and-crop-pivot.md`. |
| M1 | Pipeline end-to-end on plate D (gen-1) | archived | 6.5 | ~6 | none | **Shipped against gen-1 phone scans 2026-04-30; archived to `work/_archive/m1-plate-d-phone/` same day.** Pipeline (`01-crop` through `04-validate` + Makefile) shipped clean and 11 sidecars passed lint, but underlying SVG silhouettes inherit the gen-1 gutter warp. To be re-run against gen-2 input as part of M0.5. |
| M2 | All pieces traced + gear-ratio validation | not-started | 27 | — | M0.5 | Bulk authoring; per-piece rows below. Gear-ratio validation added per resolved decision #5. |
| M3 | Flat viewer (illustrative aesthetic) | not-started | 30 | — | M2 | First runnable viewer. Tag v0.1.0 at completion. |
| M4 | Assemblies (clock takes its real shape) | not-started | 30 | — | M3 | Long pole — per-group transform authoring, ~8 groups. |
| M5 | Polish + inspect-panel content | not-started | 12 | — | M4 | Figure refs, instruction blockquotes, photographic aesthetic if time. |
| M6 | Mechanism animation (stretch) | deferred | 15 | — | M5 (preferred) or M3 (early-validation pull-forward) | SPEC stretch goal. Currently held; gear-ratio data sanity-checked in M2. |
| Post-M5 | Mobile interactivity | deferred | 12 | — | M5 | Not in v0.1.0; ships as a follow-on after the polished desktop viewer. |

Aggregate estimate through M5: **~106 hours** of focused work. Through M6 + mobile: **~133 hours**.

---

## Resolved product decisions (this session, 2026-04-30)

These were the five open SPEC decisions. All five are now closed; the SPEC's "Open product decisions" section can be marked resolved on the next pass.

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| 1 | Layer-toggle visual: hide vs. translucent | **Translucent (~20% opacity) as default; single global "hide instead" switch in a settings menu.** Per-toggle 3-state UI rejected. | Translucent keeps spatial reference; one mode for all toggles is less UI debt. Revisit if it feels wrong in M3. |
| 2 | Aesthetic: photographic vs. illustrative | **Illustrative first in M3; iterate toward photographic in M5 if time. No runtime toggle.** | M3's job is the geometry gut-check; aesthetic is M5 polish. Avoids doubling material/lighting work. |
| 3 | Mobile interactivity depth | **Defer mobile entirely. Desktop-only for v0.1.0. Mobile is a Post-M5 milestone.** | Hobby-project audience is desktop-first; ships sooner; validates desktop UX before doubling surface. |
| 4 | Hosting | **GitHub Pages off this repo.** Repo is public; viewer deploys from `work/viewer/dist/` only — `source/` stays in-repo as personal-reference but isn't republished as a deployed site. | Simplest. Source-vs-derivative split is enforced by what gets copied into the build artifact, not by repo-splitting. |
| 5 | Mechanism animation timing | **Animation stays in M6 stretch. Add a gear-ratio validation script to M2** as a JSON-data sanity check. | Animation needs M4's assembly transforms anyway. Gear-ratio validation catches inconsistencies in `embedded-labels.md` tooth counts before M4 work begins. |

---

## Model selection guide

The roadmap doesn't dictate which Claude model handles which task — that's a per-session call — but some chunks of this project are clearly cheaper to run with a lighter model and just as good in output quality. This section calls out where the downshifts are safe, where they're risky, and which model to reach for. Update this section as we learn from real runs.

Available models:

- **Claude Opus 4.7** — most capable. Reach for it when judgment, ambiguity, or cross-file reasoning is the bottleneck.
- **Claude Sonnet 4.6** — strong for most coding and structured authoring. Sensible default for the bulk of this project.
- **Claude Haiku 4.5** — fast and cheap. Reach for it when each unit of work is small, well-specified, repetitive, and the failure mode is "wrong-then-corrected" rather than "silently broken."

### Where Haiku 4.5 is a clear win

- **M2 (all pieces traced) per-piece sidecar authoring — 123 pieces, ~4 hours of work.** Each sidecar is a small structured JSON with a fixed schema, sourced from `embedded-labels.md` and `instructions.md` (both already structured). Each piece is independent. This is the **highest-leverage downshift in the whole project** — likely a 5–10× speed/cost improvement with no quality loss if the prompt template is solid. Recommend running them in batches by plate, with a Sonnet pass to spot-check a sample from each plate.
- **Version-bump and CHANGELOG-entry tasks (M3 task 3.10, M4 task 4.14, M5 task 5.8, M6 task 6.6, Post-M5 task 7.5).** Mechanical edits with a clear pattern.
- **`Makefile` authoring (M1 task 1.9).** Boilerplate driven by pre-existing scripts.
- **Glue/run-and-check loops (M2 tasks 2.2–2.4).** When the work is "run this script, eyeball the output, move on," Haiku is fine.

### Where Sonnet 4.6 is the right default

- **Most of M3 (flat viewer) except `pieces.ts`.** Vite scaffolding, scene setup, hover/click, layer toggles, keyboard nav, GitHub Pages deploy — Sonnet handles the three.js patterns well and the codebase stays small enough that long-context isn't a factor.
- **All of M5 (polish + inspect-panel content).** Wiring tasks against an existing manifest schema; copywriting for the README. Squarely in Sonnet's wheelhouse.
- **The pipeline scripts in M1 (tasks 1.2, 1.3, 1.4, 1.7).** Particularly `03-layer-split.py` — its classification heuristics need a bit of judgment that Haiku could miss on edge cases.
- **M2 setup tasks (2.5 manifest builder, 2.6 gear-ratio validator).**
- **Per-group assembly authoring in M4 if you want Claude assistance** — but most of M4 is hand-fitting against figures, which is human work and can't be delegated regardless of model.

### Where Opus 4.7 earns its keep

- **`pieces.ts` (M3 task 3.3) — SVG → mesh extrusion + canvas-decal baking + hinge sub-mesh partitioning.** The gnarliest single piece of code in the project. Cross-cutting concerns and a long debugging tail; Opus's reasoning depth pays for itself.
- **`assembly.ts` engine (M4 task 4.1).** Hierarchical group composition with hinge parenting, transform JSON loading, exploded-slider math. Design-heavy.
- **Escapement tick animation (M6 task 6.5).** Geometry-complex; pallet-and-anchor engagement timing.
- **Reconciling gear-ratio inconsistencies (M2 task 2.7) if any are surfaced.** Requires reading across `embedded-labels.md`, `instructions.md`, and the relevant figures — multi-source synthesis.
- **Roadmap and SPEC maintenance — this kind of work.** Cross-document consistency, decision-tracking, judgment about what's underspecified.

### Rule of thumb

If the task definition fits in a paragraph and the output is a single file you'd verify with a glance — **Haiku**. If it's "code this thing" with a clear spec and one or two files in scope — **Sonnet**. If you're writing the spec, untangling a question, or building the scaffolding others will sit on — **Opus**.

When in doubt, start one tier lower than feels safe and let the output tell you whether to escalate. The cost of a Haiku failure is a re-run; the cost of an Opus over-spend is the same work at higher cost.

---

## M0.5 — Chunk-and-crop onboarding + pipeline reshape

**Goal.** Establish the chunk-and-crop source-archive workflow, populate `source/pieces/` with a complete per-piece PNG archive, and reshape the pipeline so it reads from `source/pieces/` directly (no more plate slicing). Then re-run the M1 trace pass on gen-2 plate D and confirm rectilinear silhouettes (no gutter bow). Outputs: `source/scans-chunks/` and `source/pieces/` populated; expanded `pieces.csv` (123-row master index, bbox columns dropped); piece-scan ingest skill authored; pipeline `02-trace.py` repointed at `source/pieces/`; `01-crop.py` archived; gen-2 plate-D pieces re-traced under `work/pieces/`.

**Why this milestone exists.** M1 pipeline shipped on 2026-04-30 against gen-1 phone scans. Visible in Inkscape post-merge (piece 31): top edge bows from gutter warp that survived pre-processing. First-pass response was a whole-plate gen-2 rescan (see `sessions/2026-04-30-1800_cowork_rescan-restructure.md`). Same-day refinement: the home flat-bed scanner can't fit a whole plate — captures arrive as multi-piece chunks instead. The chunk-and-crop loop replaces plate-scan-then-bbox-slice as the source-of-pieces path. See `sessions/2026-04-30-1900_cowork_chunk-and-crop-pivot.md`.

**Dependencies.** None upstream. Blocks M2.

**Strategy.** The big shift is conceptual: `source/pieces/NNN.png` becomes the canonical pipeline input, not `source/scans-prepped/p00x-plate-X.jpg`. That collapses two pipeline stages (whole-plate prepping + bbox-driven cropping) into a single hand-cropping step in Zarathale's image editor. The trade is one-time tedium (cropping ~123 pieces by hand) for stable downstream behavior (`02-trace.py` onward stays unchanged). Pre-processing becomes per-piece if/when needed — flat-bed home scans are typically clean enough that it may be a no-op on most pieces. The piece-scan ingest skill closes the loop by auditing `source/pieces/` against the master `pieces.csv` and surfacing what's still pending.

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 0.5.1 | Settle chunk-and-crop design; expand `pieces.csv` to 123-row master index | done | 1.0 | ~1.0 | Cowork | `pieces.csv` (123 rows), `build_master_list.py`, `SCAN-INTAKE-CHECKLIST.md` rewritten, CLAUDE.md + ROADMAP.md updated | See `sessions/2026-04-30-1900_cowork_chunk-and-crop-pivot.md`. |
| 0.5.2 | Author piece-scan ingest skill (`SKILL.md` + Python helper at `.claude/skills/piece-scan-ingest/`) | in-progress | 1.5 | — | Cowork (SKILL.md draft) + Code (helper) | Skill validates filenames against `pieces.csv`; runs image-health checks (DPI, dims, color mode); reports captured-vs-pending status; flags anomalies. Read-only by contract. | SKILL.md drafted 2026-04-30 (see `sessions/2026-04-30-2300_cowork_M0.5.2-ingest-skill-draft.md`); helper queued via `CODE_PROMPT_M0.5.2-piece-scan-ingest.md`. |
| 0.5.3 | Capture remaining chunks on flat-bed home scanner; promote inbox → `source/scans-chunks/` | in-progress | 3.0 | — | Cowork (Zarathale at the scanner) | Coverage of all 13 plates as multi-piece chunks. | 8 chunks landed 2026-04-30 (most of plate D + parts of E/F/G/H). Per `SCAN-INTAKE-CHECKLIST.md`. |
| 0.5.4 | Hand-crop pieces in editor → `source/pieces/NNN.png` (lossless, three-digit zero-padded) | in-progress | 2.5 | — | Cowork (Zarathale in Affinity/Photoshop/Preview) | Up to 123 PNG files in `source/pieces/`. | Letter variants `092a.png`, `112a.png`. Per `SCAN-INTAKE-CHECKLIST.md` "Per-piece crop" section. **117 of 123 captured (115 numeric + 092a + 112a). 6 still pending: 013, 014, 016, 017 (plate B brackets), 090 (plate F reduction-gear pulley/disc), 110 (plate A face-frame end rail).** First batch (97) ingested 2026-04-30. Second batch (4 + L/R stitching for 34/35/94) ingested 2026-05-01 (`sessions/2026-05-01-0030_*`). Third batch (16 more, including the editor crops of 34/35 and 94 from the stitched composites) ingested 2026-05-01 (`sessions/2026-05-01-0130_*`). Effective capture DPI verified ~613 (above 600 spec). |
| 0.5.5 | Run ingest skill audit; iterate on captures/crops until master list is satisfied | not-started | 0.5 | — | Cowork | Clean ingest report; `pieces.csv` `status` column reflects `captured` for all pieces. | Skill reports surface gaps; address by re-capturing or re-cropping. |
| 0.5.6 | Reshape pipeline: archive `01-crop.py`, repoint `02-trace.py` at `source/pieces/`, update `Makefile` | not-started | 1.0 | — | Code | `01-crop.py` → `work/_archive/`; `02-trace.py` reads `source/pieces/NNN.png`; `Makefile` targets adjusted | Needs a `CODE_PROMPT_*.md` handoff. |
| 0.5.7 | Re-run trace + layer-split on gen-2 plate D's 11 pieces | not-started | 0.5 | — | Code | 11 fresh piece directories in `work/pieces/` | Sidecars copy forward verbatim from `work/_archive/m1-plate-d-phone/pieces/0NN/piece-0NN.json` (scan-independent). |
| 0.5.8 | Open piece 031 (and 1–2 others) in Inkscape; confirm rectilinear silhouettes | not-started | 0.5 | — | Cowork | Visual confirmation | Pass criterion for M0.5. |
| 0.5.9 | Session note + commit; flip M1 row in this roadmap to `superseded`; flip M0.5 row to `done` | not-started | 0.25 | — | Cowork | sessions note | M2 unblocks once this row closes. |

**M0.5 verification.** `source/pieces/` contains a PNG for every row in `pieces.csv`; the ingest skill reports zero anomalies; piece 031's silhouette top edge runs east–west in Inkscape; no visible bow on any plate-D piece; `04-validate-sidecars.py` passes against the gen-2 plate-D outputs.

**What NOT to do in M0.5.** Don't re-author sidecars from scratch — the gen-1 sidecars are scan-independent and copy forward. Don't pre-trace pieces beyond plate D — that's M2's bulk authoring pass. Don't tackle the viewer. Don't try to scan whole plates — that assumption was retired this milestone.

---

## M1 — Pipeline end-to-end on plate D

**Status (2026-04-30): archived against gen-1 phone scans.** This section is preserved as a decision record. The work happened; its outputs are at `work/_archive/m1-plate-d-phone/`. M0.5 above is the active follow-on.

**Goal (as shipped).** Build the per-piece authoring pipeline (`01-crop.py` through `04-validate-sidecars.py`) and run it end-to-end on plate D's 11 pieces. Output: 11 piece directories under `work/pieces/`, each with `crop.png`, `piece-NNN.svg` (layered), `piece-NNN.json` (sidecar), passing the linter. Plus a partial `pieces.csv` with plate-D rows.

**Dependencies.** None — `source/scans-prepped/p00x-plate-D-...jpg` exists, the auto-trace v2 test confirmed the pipeline approach, all five product decisions are resolved.

**Plate D piece count.** 11 pieces (4, 10, 18, 19, 26, 29, 30, 31, 32, 91, 92) per `embedded-labels.md` Panel D.

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 1.1 | Author bbox-by-hand for plate D's 11 pieces; populate `work/pieces.csv` (plate-D rows) | done | 1.0 | ~1.0 | Cowork | `pieces.csv` (partial, 11 rows) | One-time hand pass per piece. Schema at ship time: `id,plate,bucket,bbox_x,bbox_y,bbox_w,bbox_h`. Bbox columns dropped in the chunk-and-crop pivot (see M0.5 row above); plate-D rows carried forward into the 123-row master. |
| 1.2 | Code `work/pipeline/01-crop.py` (reads pieces.csv, crops from prepped scan) | done | 0.5 | — | Code | `01-crop.py`, `crop.png` × 11 | see sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md |
| 1.3 | Code `work/pipeline/02-trace.py` (native potrace if available; potracer fallback) | done | 1.0 | — | Code | `02-trace.py`, single-layer SVG × 11 | see sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md |
| 1.4 | Code `work/pipeline/03-layer-split.py` (path → canonical layer by stroke style + area) | done | 1.5 | — | Code | `03-layer-split.py`, layered SVG × 11 | see sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md |
| 1.5 | Light hand-edit in Inkscape on auto-trace+edit bucket pieces | not-started | 1.0 | — | Cowork | Refined SVGs | 30–60 sec per piece per SPEC. Plate D bucket distribution TBD until 1.4 ships. |
| 1.6 | Author 11 sidecars (`piece-NNN.json`) by hand from `embedded-labels.md` Panel D + `instructions.md` | done | 0.5 | — | Cowork | 11 JSON sidecars | see sessions/2026-04-30-1600_cowork_M1-sidecars-and-codesession-improvements.md — 11/11 pass linter; 4 expected WARNs for cross-plate connections to pieces 25 (plate C, 2× from 4/10 + 2× from 26) and 41 (plate F, 2× from 92, flagged as suspicious in piece-92.json notes). |
| 1.7 | Code `work/pipeline/04-validate-sidecars.py` (linter: silhouette closed, folds open, tab/axle cross-refs) | done | 1.0 | — | Code | `04-validate-sidecars.py`, lint pass | see sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md |
| 1.8 | Run linter on plate D's 11 sidecars; iterate until clean | done | 0.5 | — | Code | Clean lint output (no sidecars yet — expected) | see sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md |
| 1.9 | Add `work/pipeline/Makefile` with crop / trace / layer-split / validate targets | done | 0.5 | — | Code | `Makefile` | see sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md |

**M1 verification (after merge).** `make pieces` from `work/pipeline/` produces 11 piece directories; linter passes; spot-check piece 92 (a known-clean auto-trace) and piece 91 (an accordion piece) in Inkscape and confirm layers are correctly classified.

**What NOT to change in M1.** Don't touch the viewer (`work/viewer/`) — M3 territory. Don't write assembly transforms — M4 territory. Don't extend `pieces.csv` beyond plate D — M2 territory.

---

## M2 — All pieces traced + gear-ratio validation

**Goal.** Run the M1 pipeline across plates A, B, C, E, F, G, H, I, J, M (plates K and L are figure references, not pieces). All 123 pieces have a directory under `work/pieces/` with crop, layered SVG, and validated sidecar. The full `pieces.csv` is canonical. A new gear-ratio validation script confirms the tooth-count math in `embedded-labels.md` is internally consistent. `manifest.json` builds cleanly.

**Dependencies.** M1 (pipeline scripts must exist).

**Per-piece authoring.** Tracked per row in `work/pieces.csv`. Bucket assignments (auto-trace-clean / auto-trace-edit / hand-trace) are populated only for plate D's 11 pieces (carried forward from M1); blank elsewhere until the M2 task 2.1 visual triage. Effort estimates per piece are placeholder until bucket is known. Letter variants (092a, 112a) get their own rows in `pieces.csv`. The summary table below records plate-level counts only.

### M2 setup tasks (do once, before per-piece work)

| # | Task | Status | Est. h | Actual h | Owner | Notes |
|---|---|---|---|---|---|---|
| 2.1 | Triage all remaining pieces into buckets; finalize `pieces.csv` | not-started | 2.0 | — | Cowork | Visual pass over the prepped scans; assign auto-trace-clean / auto-trace+edit / hand-trace per piece. |
| 2.2 | Crop all remaining plates via `01-crop.py` | not-started | 0.5 | — | Code | Driven by the finalized `pieces.csv`. |
| 2.3 | Run `02-trace.py` across auto-trace bucket pieces | not-started | 1.0 | — | Code | Native potrace; batch run. |
| 2.4 | Run `03-layer-split.py` across auto-trace bucket pieces | not-started | 0.5 | — | Code | Batch. |
| 2.5 | Code `work/pipeline/05-build-manifest.py` (union per-piece JSON + assembly JSON + transcription refs into `manifest.json`) | not-started | 1.5 | — | Code | One-time; runs after all sidecars exist. Adds `viewerVersion` field. |
| 2.6 | Code `work/pipeline/06-validate-gear-ratios.py` (resolved decision #5) | not-started | 1.5 | — | Code | Reads the optional `function` block from §II.B + §II.C sidecars (per the *Faithful trace + functional sidecar* decision in CLAUDE.md). Anchor unit: escape-wheel advance per tick (one tick = 2π/N rad, N = `toothCount` on the escape-wheel `function` block). Walks the `drives` chain from escape wheel back through middle wheel and motor wheel, confirming each tooth-count ratio resolves to an internally consistent rotation per tick. Cross-checks the book's stated pendulum period from `instructions.md` as a sanity check, not a primary input. Surfaces inconsistencies. |
| 2.7 | Run gear-ratio validation; reconcile any inconsistencies with `embedded-labels.md` | not-started | 1.0 | — | Cowork | Could surface a transcription error that needs an audit-style fix. |

### M2 per-plate piece distribution

The canonical per-piece list (with status, plate, section, bucket, and notes) lives in [`work/pieces.csv`](work/pieces.csv); the generator is [`work/scripts/build_master_list.py`](work/scripts/build_master_list.py). All updates flow through `pieces.csv` first — this section is an executive summary, not a second source of truth.

| Plate | Numbered pieces | Letter variants | Notes |
|---|---|---|---|
| A | 5 | — | Long horizontal frame strips |
| B | 14 | — | Frame and bracket pieces |
| C | 10 | — | Frame pieces, small triangles |
| D | 11 | — | Re-runs through pipeline in M0.5 against gen-2 (M1 ran on gen-1; archived) |
| E | 14 | 112a | Gears, axles, weight wire reference; 112a face-frame mirror partner |
| F | 28 | — | Escapement-related toothed wheels and stars |
| G | 18 | — | Main wheels (motor, middle, escapement) and long bottom strips |
| H | 13 | 092a | Anchor, pendulum, weight, directional disc; 092a anchor-and-pendulum hands tongue |
| I | 2 | — | Case sides |
| J | 5 | — | Clock hands, face frame backing |
| M | 1 | — | Clock face. Tracked as piece **121** (assigned for build authoring; not numbered in print) |
| **Total** | **121** | **2** | **123 unique pieces** |

Cross-plate references (pieces appearing physically on more than one plate as duplicate copies) are recorded in the Notes column of `pieces.csv`. The plate column records the primary detailed-description plate from `embedded-labels.md`.

Bucket assignments (auto-trace-clean / auto-trace-edit / hand-trace) are populated for plate D (carried forward from M1); blank elsewhere pending the M2 task 2.1 visual triage. Status flips `pending` → `captured` (chunk-and-crop ingest, M0.5) → `traced` (pipeline, M2) per piece.

**M2 verification (after merge).** `make pieces` runs cleanly across all plates. `04-validate-sidecars.py` passes for all 123 sidecars. `06-validate-gear-ratios.py` reports consistent ratios (or surfaces a documented inconsistency for follow-up). `manifest.json` builds.

---

## M3 — Flat viewer (illustrative aesthetic)

**Goal.** Bring up the three.js viewer with all pieces rendered flat, in a grid laid out by plate. Hover, click, and inspect-panel work. No assembly transforms yet — that's M4. Aesthetic: illustrative (clean diagrammatic look) per resolved decision #2. Layer toggles use translucent default with a global hide-instead switch per resolved decision #1. Deploys to GitHub Pages off this repo per resolved decision #4. Tag **v0.1.0** at completion.

**Dependencies.** M2 (all pieces traced + manifest.json exists).

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 3.1 | Scaffold `work/viewer/` (Vite + TypeScript + three.js r160+, pnpm, Tailwind) | not-started | 1.0 | — | Code | Empty-but-runnable viewer | `package.json`, `vite.config.ts`, basic `index.html` and `src/main.ts`. |
| 3.2 | Implement `scene.ts` (renderer, camera, lighting, OrbitControls with damping) | not-started | 3.0 | — | Code | Empty 3D scene | Neutral lighting; auto-rotate off. |
| 3.3 | Implement `pieces.ts` (SVG → mesh: SVGLoader, ExtrudeGeometry, canvas-decal baking) | not-started | 6.0 | — | Code | Per-piece mesh factory | Front face: cream + decal texture. Back face: plain cream. Edges: slightly darker. Cardboard pieces use brown-board diffuse. |
| 3.4 | Implement plate-grid layout (all pieces flat, organized by source plate) | not-started | 2.0 | — | Code | Browsable grid | M3 is flat-only; assembly composition is M4. |
| 3.5 | Implement hover state (emissive edge outline + floating piece number) | not-started | 1.5 | — | Code | Hover behavior | Per SPEC §"Viewer behavior". |
| 3.6 | Implement click selection + inspect side panel (data-driven from manifest.json) | not-started | 6.0 | — | Code | Working inspect panel | Header, reference crop, embedded labels, folds count, connections, axles, instructions blockquote. Figure thumbnails are M5 polish. |
| 3.7 | Implement layer toggles with translucent default + global "hide instead" settings switch (resolved decision #1) | not-started | 2.0 | — | Code | Toggle UI | Settings menu in corner. |
| 3.8 | Implement keyboard navigation (Tab cycles, arrows orbit, Esc closes inspect) + reset-camera button | not-started | 2.0 | — | Code | Accessible controls | |
| 3.9 | Set up GitHub Pages deploy (`gh-pages` branch or `/docs` from `main`); first deployment | not-started | 2.0 | — | Code | Live URL | Repo is public per resolved decision #4. Deploy artifact = `work/viewer/dist/`. |
| 3.10 | Bump version to `0.1.0` in `work/viewer/package.json` and `manifest.json`'s `viewerVersion`; smoke test live URL | not-started | 0.5 | — | Code | v0.1.0 tag, CHANGELOG entry | First viewer ship. |

**M3 verification (after merge).** Live URL renders all 123 pieces flat. Hover highlights any piece. Click opens inspect panel with the piece's number, label text, fold counts, and connection chips. Layer toggles fade groups to translucent; settings switch flips them to fully hidden. Keyboard shortcuts work. No console errors.

**Out of scope for M3.** Assembly transforms (M4). Photographic aesthetic (M5). Mobile responsiveness (Post-M5). Mechanism animation (M6).

---

## M4 — Assemblies (clock takes its real shape)

**Goal.** Author the per-group transforms so the clock assembles in 3D. Eight assembly groups, in book-section order. Implement the exploded slider so the reader can fan the assembly out. Tag **v0.2.0** at completion (or whatever minor version follows v0.1.0 at the time).

**Dependencies.** M3 (flat viewer must exist; hinge sub-mesh code in `pieces.ts` is the substrate for fold-angle authoring).

**Strategy.** Author one group at a time, in approximate book order. Each group is iterated against Fig. 1 (frame perspective on plate K), Fig. 13 (schematic cross-section on plate L), and the §II prose in `instructions.md`. Estimate per group: 2–6 hours. The framework is the largest; the wall-bracket and weight are smallest.

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 4.1 | Implement `work/viewer/src/assembly.ts` (group composition, transform JSON loader, hinge `Object3D` parenting) | not-started | 4.0 | — | Code | Assembly engine | Reads `assemblies/<group>.json` per group + top-level `assembly.json`. |
| 4.2 | Implement exploded slider (range 0→1; per-group factor; hinged sub-pieces unfold to flat at 1.0) | not-started | 3.0 | — | Code | Working slider | Slider=0: assembled. Slider=1: every piece flat in its development form. |
| 4.3 | Author `assemblies/framework.json` (§II.A, ~22 pieces) | not-started | 5.0 | — | Cowork | Framework group | Largest group. Iterate against Fig. 1 + prose. |
| 4.4 | Author `assemblies/wall-bracket.json` (§II.A, 4 pieces) | not-started | 1.5 | — | Cowork | Wall-bracket group | |
| 4.5 | Author `assemblies/motor-wheel.json` (§II.B.1, ~7 pieces) | not-started | 3.0 | — | Cowork | Motor-wheel group | Validates gear-positioning approach for the other wheels. |
| 4.6 | Author `assemblies/middle-wheel.json` (§II.B.2, ~8 pieces) | not-started | 2.5 | — | Cowork | Middle-wheel group | |
| 4.7 | Author `assemblies/escapement-wheel.json` (§II.B.3, ~7 pieces) | not-started | 2.5 | — | Cowork | Escapement-wheel group | |
| 4.8 | Author `assemblies/wheel-mounting.json` (§II.B.4, 4 pieces) | not-started | 1.5 | — | Cowork | Mounting group | |
| 4.9 | Author `assemblies/anchor-and-pendulum.json` (§II.C, ~15 pieces incl. 92a) | not-started | 4.0 | — | Cowork | Anchor + pendulum group | |
| 4.10 | Author `assemblies/hands-mechanism.json` (§II.D, ~10 pieces) | not-started | 3.0 | — | Cowork | Hands group | |
| 4.11 | Author `assemblies/weight.json` (§II.E, 2 pieces) | not-started | 1.0 | — | Cowork | Weight group | |
| 4.12 | Author `assemblies/face-and-case.json` (§II.F, ~12 pieces incl. 112a) | not-started | 3.0 | — | Cowork | Face + case group | |
| 4.13 | Author top-level `assemblies/assembly.json` placing each group in clock-coordinate space | not-started | 1.5 | — | Cowork | Composition | |
| 4.14 | Bump version (likely to `0.2.0`); CHANGELOG entry | not-started | 0.5 | — | Code | Versioned ship | |

**M4 verification (after merge).** Live URL renders the assembled clock face-on. Exploded slider fans the assembly outward; at 1.0, every piece is flat. Layer toggles still work post-assembly. Cross-checks against Fig. 13 (assembled schematic) for visual fidelity.

**Note on iteration cost.** Per-group transform authoring is hand-fitting against figures. Each group will need 1–3 iteration passes. The estimates above are first-pass; a separate "iterate-against-figures" allowance of ~6 hours is built into the milestone total but not split per group.

---

## M5 — Polish + inspect-panel content

**Goal.** Wire the figure references, instruction-step blockquotes, plate-thumbnail highlighting. Tune lighting and material toward the photographic aesthetic if time allows (resolved decision #2). Implement the settings panel housing the hide-vs-translucent toggle. Write the user-facing README/about. Tag **v0.3.0** at completion.

**Dependencies.** M4 (assembled clock exists for screenshots and the polished panel content).

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 5.1 | Wire figure references (K/L thumbnails + click-to-zoom) into inspect panel | not-started | 2.0 | — | Code | Figure-ref UI | `figureRefs` field already in sidecar. |
| 5.2 | Wire instruction-step blockquotes (matched by `introducedInStep`) + "View full step" scrolls a separate instructions panel | not-started | 2.0 | — | Code | Instructions UX | |
| 5.3 | Wire plate-thumbnail highlighting in inspect panel header (small thumb of the source plate with the piece highlighted) | not-started | 1.5 | — | Code | Plate-thumb UI | |
| 5.4 | Tune lighting + camera defaults; add per-piece edge contrast pass | not-started | 1.5 | — | Code | Polished look | |
| 5.5 | Implement settings panel (homes the hide-instead-of-translucent switch and any future preferences) | not-started | 1.0 | — | Code | Settings UI | Resolved decision #1 housing. |
| 5.6 | Iterate toward photographic aesthetic (cream-paper texture, real-glyph labels at scale) — time-permitting | not-started | 3.0 | — | Code | Photographic look (or note deferred) | Decision #2 said "if time"; may slip to a later patch. |
| 5.7 | Write project README/about for the deployed viewer | not-started | 1.0 | — | Cowork | About page or in-viewer panel | Public-facing; explains the source-vs-derivative split per resolved decision #4. |
| 5.8 | Bump version (likely to `0.3.0`); CHANGELOG entry; smoke test | not-started | 0.5 | — | Code | Versioned ship | |

**M5 verification (after merge).** Inspect panel shows figure thumbnails, instruction blockquotes, plate thumbs. Settings panel works. Photographic look ships or is documented as deferred. README is public.

---

## M6 — Mechanism animation (stretch)

**Goal.** Compute gear ratios and angular velocities from `embedded-labels.md` tooth counts (already validated in M2). Rotate the mechanism. Pendulum amplitude/period from rod length. Hands advance on real time. Tag **v0.4.0** at completion.

**Dependencies.** M5 (polished viewer; gear-ratio data validated in M2).

**Status:** **deferred.** This is a stretch goal. Not committed; will be evaluated post-M5 against time and interest.

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 6.1 | Implement rotation drivers (per axle; pieces sharing an axle rotate together) | not-started | 3.0 | — | Code | Animation engine | |
| 6.2 | Wire gear ratios computed from sidecar tooth counts | not-started | 2.0 | — | Code | Mechanism turns | Sourced from M2 gear-ratio validation output. |
| 6.3 | Implement pendulum animation (period from rod length) | not-started | 2.5 | — | Code | Pendulum swings | |
| 6.4 | Implement hands advancing on real time | not-started | 2.0 | — | Code | Hands move | |
| 6.5 | Implement escapement tick (anchor/pallets engagement) | not-started | 4.0 | — | Code | Realistic ticking | Most complex piece; geometry is in the SPEC's anchor-and-pendulum group. |
| 6.6 | Bump version; CHANGELOG entry | not-started | 0.5 | — | Code | Versioned ship | |
| 6.7 | Update README to mention "it's a clock" | not-started | 0.5 | — | Cowork | Public-facing | |

**M6 verification.** It's a clock.

---

## Post-M5 — Mobile interactivity

**Goal.** Adapt the desktop viewer for mobile. Bottom-sheet inspect panel, pinch zoom, touch-friendly orbit/explode. Test on iOS Safari and Android Chrome. Tag a follow-on minor version (e.g., **v0.5.0** if it ships after M6, or **v0.4.0** if M6 stays deferred).

**Dependencies.** M5 (polished viewer must exist as the desktop baseline).

**Status:** **deferred** per resolved decision #3. Not in v0.1.0; ships as a follow-on milestone.

| # | Task | Status | Est. h | Actual h | Owner | Output | Notes |
|---|---|---|---|---|---|---|---|
| 7.1 | Mobile-responsive UI: bottom-sheet inspect panel | not-started | 4.0 | — | Code | Mobile layout | Tailwind responsive utilities. |
| 7.2 | Pinch zoom + touch orbit | not-started | 3.0 | — | Code | Touch controls | OrbitControls touch support. |
| 7.3 | Touch-friendly exploded slider + layer toggles | not-started | 2.0 | — | Code | Mobile UI | Larger hit targets. |
| 7.4 | Test on iOS Safari + Android Chrome; fix per-device issues | not-started | 2.5 | — | Cowork + Code | Mobile-tested viewer | |
| 7.5 | Bump version; CHANGELOG entry | not-started | 0.5 | — | Code | Versioned ship | |

---

## Open items (not yet planned)

These aren't milestones — they're things to flag so they don't get lost.

- **Documentation: "About the project" page or section** for the deployed viewer. Currently a sub-task of M5 (5.7) but if the public viewer wants more story (the book, the auto-trace pipeline, the assembly process), that could grow into its own pass.
- **CHANGELOG.md** for the viewer. CLAUDE.md says "the viewer has its own [CHANGELOG]; the repo doesn't yet" — create when M3 first ships.
- **`work/viewer/` README** — separate from the public README; for contributors / future-Zarathale.
- **Cosmetic rescans:** **closed.** Originally meant plate L thumb and plate A higher-resolution as deferred per gen-1 `RESCAN_FINDINGS.md`. Subsumed by M0.5's full gen-2 rescan, which captures every plate to the same standard.
- **CI** — currently no CI. CLAUDE.md says the linter should run in CI before manifest build. Consider adding GitHub Actions in M2 or M3 (lint + build dist + deploy to gh-pages on merge to main).
- **License/attribution** — repo public, source still personal-reference. Confirm the repo's LICENSE file (or its absence) reflects what you want; consider adding a NOTICE about the book's copyright.

---

## How to update this document

**Cowork at session start:** read this doc. Re-confirm the milestone-index table reflects current reality. Adjust task status, est/actual hours, or notes as needed. Surface anything new in "Open items."

**Cowork during a session:** when settling a decision, add it to the resolved-decisions table with a short rationale. When refining a task estimate based on what you learned, edit the est-hours column and note the change in Notes.

**Code at PR-merge time:** flip closed tasks to **done** and add `see sessions/YYYY-MM-DD-HHMM_…` in the Notes column. Update Actual h with the real time spent. Bump version where applicable.

**Mirror to CLAUDE.md status table.** When a milestone closes (status → done), update the high-level row in CLAUDE.md's "Where We Are" status table. The roadmap is the detail; CLAUDE.md's table is the executive summary.

**Don't:** delete old rows or rewrite history. If a milestone scope changes, add a new row or strike through the obsolete one with a note. The roadmap is also a decision record.

---

*Last updated: 2026-04-30 (evening pass) — refined M2 task 2.6 description to align with the *Faithful trace + functional sidecar* decision (CLAUDE.md): validator reads the optional `function` block; anchor unit is escape-wheel advance per tick; book's pendulum period is a sanity check, not a primary input. See `sessions/2026-04-30-2330_cowork_faithful-trace-decision.md`.*

*Earlier 2026-04-30 (later same day) — reshaped M0.5 from "gen-2 rescan + pipeline re-bring-up" to "chunk-and-crop onboarding + pipeline reshape" after confirming the home scanner can't fit a whole plate. See `sessions/2026-04-30-1900_cowork_chunk-and-crop-pivot.md`. Earlier 2026-04-30 entry (gen-2 rescan + M1 archived) at `sessions/2026-04-30-1800_cowork_rescan-restructure.md`.*

*Earlier: 2026-04-30 — initial authoring; see `sessions/2026-04-30-1300_cowork_roadmap.md`.*
