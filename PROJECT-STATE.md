# PROJECT-STATE.md — z-paper-clock

_Slow-moving framing doc. The point of this file is to ground a reader (Zarathale, Claude, or anyone else who lands on the repo) in where the project actually is, not where the design documents project it eventually being. Updated when the framing changes — not session-by-session._

_Companion docs: `CLAUDE.md` (working conventions, every-session entry), `ROADMAP.md` (the long milestone arc), `claude-work/STATUS.md` (the live per-track surface — replaced `WORKPLAN.md` at charter sign-off 2026-05-04 per `claude-work/DECISIONS.md` #2), `work/SPEC-3D-VIEWER.md` (the design source-of-truth for the build)._

---

## What this project is

z-paper-clock is a personal study and reinterpretation of *Make Your Own Working Paper Clock* by James Smith Rudolph. The long-term goal is a digital system that allows the clock to be explored, inspected, and eventually experienced — its individual pieces, the way they fold and glue, and (eventually) the way the mechanism actually ticks.

The collaboration with Claude is part of the point. Pace is hobby-project, not delivery-project.

---

## Current reality

The project is in an **early build / discovery phase**. Some surfaces are solid; large parts of what the design documents describe are not yet built and won't be for a while.

The repository is honest about this in places (the `pieces.csv` `status` column, session notes flagged `superseded`, the M1 archive) and aspirational in others (the SPEC describes pipeline stages and viewer behaviors that don't exist yet). Read accordingly: pipeline scripts named in the SPEC may or may not have been written; viewer behaviors described in detail are mostly proposed; per-piece data models exist on a small handful of pieces and are still iterating.

The right frame: most build-side documents are **working hypotheses** that get refined as the work touches them. The study side (`source/`) is stable and not under active design.

---

## What actually exists today

### Working

- **`source/transcriptions/`** — five markdown files (prose, embedded labels, instructions) covering the entire book. Audited 2026-04-29. This is the most reliable artifact in the repo and is scan-independent.
- **`source/pieces/`** — per-piece PNG archive captured via the chunk-and-crop workflow. **123 of 123 pieces captured (closed 2026-05-05).** Effective DPI ~613 (verified above the 600 spec).
- **`source/scans-chunks/`** — multi-piece chunks kept as recovery references for the per-piece PNGs (including a few programmatically stitched composites for pieces too wide to fit the scanner bed).
- **Chunk-and-crop scan-intake workflow** — capture standard, per-file QC, and intake-to-archive promotion are documented in `source/SCAN-INTAKE-CHECKLIST.md` and have been exercised across three ingest passes.
- **`work/pieces.csv`** — 123-row master index (1–121 contiguous + 092a + 112a). Schema: `id, plate, section, bucket, status, notes`. Status flips manually as pieces flow through the pipeline.
- **`preview.html`** — single-file HTML viewer at repo root, M0.6 active milestone. Loads any piece by id (`?piece=NNN`) from `work/pieces/NNN/NNN.svg`. Panels-first parser (closed polygons + explicit fold edges between named panels) drives a face graph + hinge tree + per-fold sliders. Multi-piece scene mode (PR #17) co-locates pivot-clusters; assembled-pose load + save (PR #19) reads/writes per-fold angles via the per-piece JSON sidecar's `assembled.folds` block. Cut-line-first parser preserved as legacy for pre-pivot pieces. Inferred-connections audit (PR #18) and the pre-built `connection-graph.{md,json}` at `claude-work/state/` ride alongside.
- **Pipeline (gen-1, archived)** — `01-crop.py` through `04-validate-sidecars.py` shipped against gen-1 phone scans, archived to `work/_archive/m1-plate-d-phone/`. The shipped pipeline scripts (`02-trace.py` onward) carry forward; `01-crop.py` is being retired in the chunk-and-crop pivot.

### In progress

- **SVG layer authoring (panels-first).** The actual current bottleneck. 17 panels-first SVGs authored across the anchor / pendulum / bob clusters (065-072 + 094-100 + 110); next pulls in the gear train per the brief at `claude-work/to-alan/gear-train/` (covers §II.B motor/middle/escape + §II.D reduction-gear/hands; 087 reduction-gear disc currently on the bench). Conventions stable post-DECISIONS #7; LAYER-CONVENTIONS.md is the live reference. Per-piece sidecars now carry `function` (mechanism geometry), `connections.inferred[]` (learned cross-piece edges, DECISIONS #10), and `assembled.folds` (per-fold assembled angles, DECISIONS #11) blocks.
- **`preview.html` iteration.** Three substantive ships piled on through May 2026: PR #17 multi-piece scene assembly, PR #18 inferred-connections audit-side merge, PR #19 assembled-pose load + save. Architecture decision (DECISIONS #4 — graduate into `work/viewer/`, stay separate, or replace) is the next Cowork beat now that the preview has enough on-the-table to settle it. v1b end-to-end verification quietly closed in the panels-first batch; cutouts subtraction (0.6.10) and multi-cutaway slabs (0.6.11) remain not-started but unblocked.
- **Pipeline reshape.** `01-crop.py` archival pending; `02-trace.py` repoint at `source/pieces/` pending.

### Not yet real

The following are described in the SPEC and ROADMAP but do not yet exist in working form:

- **End-to-end geometry pipeline** at scale (PNG → clean SVG across all 123 pieces).
- **Structured per-piece data model** (SVG + JSON sidecar) populated across the project.
- **Assembly / transform system** (per-group transforms, exploded slider, clock takes its real shape).
- **Three.js viewer application** at `work/viewer/` (Vite + TS + three.js scaffolding).
- **Mechanical simulation** (gear ratios, pendulum period, escapement tick).
- **Public deploy** to GitHub Pages.

These are real intentions, but each is still upstream of work that hasn't been done.

---

## How to read the repository

### `CLAUDE.md`

Working conventions for every Cowork and Code session. Authoritative on Cowork/Code lane separation, sessions/ format, git workflow, file-naming conventions, dev environment assumptions, and architectural decisions that have been settled (don't reopen without Zarathale). The status table near the top is the high-level mirror of ROADMAP.md.

### `ROADMAP.md`

The long milestone arc. Per-task tables with status, hours, dependencies, and pointers to closing session notes. Captures the conceptual sequence from M0.5 (chunk-and-crop onboarding) through M6 (mechanism animation, deferred). Also houses the resolved-decisions table, model-selection guide, and "Open items not yet planned." This is the **direction**.

The roadmap is sequential by milestone. Real work is currently happening across **parallel** tracks (M0.5 and M0.6 have been advancing in lockstep, not in sequence). That's fine — the roadmap captures where we're trying to get; WORKPLAN.md captures the active stance through the parallel work.

### `claude-work/STATUS.md` (live) and `WORKPLAN.md` (legacy)

`claude-work/STATUS.md` is the **active stance**: one section per open track, each with status / hypothesis / next action / recent log. Updated regularly (target cadence: when ~3+ session notes have accumulated since the last review). Replaced `WORKPLAN.md` at charter sign-off (2026-05-04) per `claude-work/DECISIONS.md` #2.

`WORKPLAN.md` (still at repo root) is **frozen as the pre-charter record** — preserved for historical reference but no longer updated. Don't mistake its dated next-actions for current state.

ROADMAP says where we're going. STATUS says what we're doing.

### `work/SPEC-3D-VIEWER.md`

The design source-of-truth for the build. **Mixed reality**: parts describe shipped decisions (cut-layer authoring convention, axle rotation, faithful trace + functional sidecar, the resolved product decisions for the eventual viewer), and parts describe intended-but-not-yet-built systems (assembly engine, exploded slider, photographic aesthetic). Approach as a design direction with shipped components scattered throughout — not as a description of a finished architecture.

### `source/`

Reference archive. Personal-use; not redistributed. This is the most stable part of the repo and is rarely under active design. Contains:

- `transcriptions/` — five markdown files (prose + labels + instructions). Stable.
- `pieces/` — per-piece PNG archive (canonical pipeline input). Active under M0.5 capture.
- `scans-chunks/` — recovery references. Active under M0.5 capture.
- `SCAN-INTAKE-CHECKLIST.md` — the chunk-and-crop standard.
- `_archive/phone-scans-2025/` — gen-1 scan archive (pre-rescan).

### `work/`

Active build area. Fluid. Contains:

- `pieces.csv` — master index of all 123 pieces.
- `piece_characters_v2.yaml`, `expected_layers.yaml` — per-piece archetype + expected-layer overrides for the audit (asset-state v2).
- `pipeline/` — pipeline scripts (gen-1 era; under reshape).
- `scripts/` — utility scripts (`build_master_list.py`, `audit_state.py`, `preprocess_scans.py`).
- `state.json` — generated by `audit_state.py`; per-piece lifecycle + convention-check results.
- `pieces/` — per-piece working folder (`NNN/{NNN.af, NNN.svg, NNN.json}`); populates piece-by-piece as authoring proceeds. Optional `_attic/` per piece for retired authoring variants.
- `SPEC-3D-VIEWER.md`, `SPEC-REGIONS.md` — design specs (the regions one is paused per DECISIONS #6).
- `_archive/m1-plate-d-phone/` — frozen M1 outputs against gen-1.

### `claude-work/`

Claude-led working surfaces post-charter. `CHARTER.md` (collaboration charter), `STATUS.md` (live per-track surface), `QUEUE.md` (pull-based queue for Alan), `DECISIONS.md` (Claude-led decision record), `scripts/` (audit + automation, including `build_assembly_graph.py` and `preview_render.py`), `standards/` (`ENVIRONMENT.md`), `state/` (generated outputs like `connection-graph.{md,json}` and `preview-renders/`), `to-alan/` (cheat sheets + per-piece briefs from Claude to Alan).

### `sessions/` and `CODE_PROMPT_*.md`

Per-session working records and per-task Cowork→Code orchestration prompts. Both follow conventions documented in CLAUDE.md. In-flight prompts (`status: draft | in-development | ready-for-code`) live at repo root; on ship they move to `_archive/code-prompts/` as the decision record. `inbox/` was retired 2026-05-03 — chunk scans land directly in `source/scans-chunks/` and SVG exports land directly in `work/pieces/NNN/`.

---

## Active exploration tracks (high-level)

Detailed track state lives in WORKPLAN.md. At time of writing, the open tracks split into roughly three concerns:

**Build the digital model.** Source-side capture closed at 123/123 (M0.5). Active focus: panels-first SVG authoring (the bottleneck) and `preview.html` iteration (M0.6). The pipeline itself is iterating as new pieces reveal new authoring requirements.

**Decide how a piece behaves.** Define what a "region" of a piece is (the face-graph problem) and use that to drive both folding and grouping. The pendulum bob + pendulum arm are the proof-of-concept pieces — folding-onto-self plus glue-to-sibling exercises both halves.

**Operate the project.** Maintain the operating documents (this file, CLAUDE.md, ROADMAP.md, WORKPLAN.md), keep the asset state legible (audit script + per-piece JSON, deferred), keep the repo tidy.

The three concerns are not strictly sequential — they advance in parallel as time and interest allow.

---

## Working approach

This project is being developed through **incremental proofs**, not full-system builds.

A typical cycle:

1. Choose a narrow problem.
2. Build the smallest possible test.
3. Evaluate what was learned.
4. Adjust direction.

Progress is partly measured by **reduced uncertainty** — what was foggy is now decided, what was open is now resolved — not only by feature completion. The roadmap's milestone scaffolding tracks the latter; this discovery-mode framing tracks the former. Both views matter.

Concretely: shipped features get tracked in `claude-work/STATUS.md` per-track logs (with ROADMAP.md as historical milestone reference and CHANGELOG entries when the viewer starts versioning); resolved questions get tracked in CLAUDE.md's "Architectural Decisions (Closed)" table for inherited decisions and in `claude-work/DECISIONS.md` for Claude-led decisions post-charter; open questions and exploration directions get tracked in `claude-work/STATUS.md`.

---

## Important context

The project is informed by prior firsthand experience building the physical clock (mid-1990s). That experience supplies:

- intuition about what matters mechanically (where the design is fragile or unclear)
- a reference point for what "working" actually means
- some humility about what's worth simulating vs. what's worth abstracting

That experience isn't formally encoded in the repo today, but it shapes design decisions throughout — particularly the *Faithful trace + functional sidecar* direction (artifact stays human-drawn-and-scanned, mechanism geometry captured separately) and the choice to keep the pendulum at the center of the early POC work.

---

## What this document is for

This document exists to:

- ground the project in its actual current state, especially for fresh-context readers (including Claude at session start);
- prevent overconfidence in unbuilt systems described in the SPEC and ROADMAP;
- clarify how to interpret other documents in the repo.

Update when the framing changes — when a major track ships, a major direction settles, or a significant rework happens. Don't update for incremental session-level changes; that's what `claude-work/STATUS.md` and `sessions/` are for.

---

*Last updated: 2026-05-06 (post-PR-19 review, root-folder reorg pass) — refreshed for stale facts: 123/123 source captured (was 117); preview.html capability picture (panels-first parser + multi-piece scene + assembled-pose + inferred-connections audit, was the v1a foundation snapshot); WORKPLAN.md noted as frozen pre-charter record (replaced by `claude-work/STATUS.md` per DECISIONS #2); `inbox/` reference retired (folded into the "sessions/CODE_PROMPT" subsection per the 2026-05-03 filesystem restructure); `claude-work/` directory section added; per-piece sidecar `connections.inferred[]` + `assembled.folds` blocks called out (DECISIONS #10, #11). The doc-rewrite is targeted: stale facts replaced; framing prose untouched.*

*Earlier 2026-05-03 (session-start sweep) — updated "In progress" section: v1b (face graph + hinge tree) noted as shipped (not queued); end-to-end browser verification still pending. See current session note.*

*Earlier 2026-05-03 — initial authoring. Created as part of a multi-session design conversation that introduced PROJECT-STATE.md + WORKPLAN.md as the two missing operating-layer documents. See `sessions/2026-05-03-0000_cowork_project-state-and-workplan.md` for the design discussion and the asset-state vs. work-state distinction that drove the two-doc split.*
