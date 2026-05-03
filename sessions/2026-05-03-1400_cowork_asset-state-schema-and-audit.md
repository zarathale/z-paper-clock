---
date: 2026-05-03
start_time: "14:00"
end_time: "15:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Settle the per-piece asset-state schema and hand a `CODE_PROMPT` to Code for the v0 audit script. Ship a parallel `LAYER-CONVENTIONS.md` cheat sheet so authoring conventions are reachable without scrolling through `CLAUDE.md`. Advance the **Asset-state / audit tooling** track from `queued` → `active`.

This session restarts a Cowork pass that was interrupted partway through (no session log was opened before the prior turn ended). Alan's original ask: organize the asset-management workflow — `.af` and `.svg` files scattered across `source/`, `work/`, and `inbox/`, with no easy way to see what state each piece is in. Pain underneath: as `preview.html` matures, authoring conventions evolve and pieces need to be "uplifted" to the new standard. Standard PM problem (standards-conformance-with-regression-risk) — handled here via per-convention linter-style checks rather than a single SVG version stamp.

## Recon (carried forward from interrupted turn)

- `.af` files: 14 in `source/pieces/` (001, 002, 058, 059, 065, 066, 067, 067-full, 068, 069, 070, 071, 072, 097), 1 in `inbox/` (069 — duplicate of `source/pieces/069.af`).
- `.svg` files (live, ignoring `work/_archive/`): 8 in `inbox/` (001, 065, 066, 067, 069, 070, 071, 072). No SVGs in `source/pieces/`.
- `share/` folder: existed at the time the prior turn started recon; no longer present at session restart. Treating as resolved-by-cleanup.
- `work/pieces/` has one entry: `069/piece-069-viewer.html` — a per-piece HTML viewer artifact from earlier exploration before `preview.html` became the convention substrate.
- `source/pieces/README.md` is explicit: SVGs/JSONs/layered crops live in `work/pieces/NNN/`, not in `source/pieces/`. So the `.af` files in `source/pieces/` are drift, not deliberate.

Open questions Alan answered before the interruption:

1. The "uplift to new authoring standard" cycle is a recognized pain point. Look for a flexible/agile/governed mechanic, not a one-shot stamp.
2. Yes to a `CODE_PROMPT` for the audit.
3. Order is: schema → audit prompt → run audit → cheat sheet (parallel) → sidecar/dashboard downstream.

## What Was Done

### 1. Asset-state schema settled

The schema is captured inline in `CODE_PROMPT_asset-state-audit.md` (the spec the script implements). Key decisions:

- **Single fat `work/state.json` for v0.** Migration to per-piece sidecars is open, deferred until the dashboard work surfaces concrete reasons.
- **Computed every run.** Audit walks the filesystem and reflects what's actually there. Nothing is hand-maintained. `pieces.csv`'s `status` column stays as a manual editorial signal; the audit is the machine-truth.
- **Convention checks as independent linter rules.** Each authoring convention (silhouette layer present, cutaway id present, axles + north format, canonical layer names only, etc.) is its own function in a registry. New convention = add a function and a row. Existing SVGs auto-flag at the next run. **No migration step on convention bumps.** This is the mechanic for Alan's "uplift to new authoring standard" pain point.
- **Lifecycle stage is derived.** `pending_capture | captured_only | affinity_started | svg_drafted | svg_layered | svg_validated | sidecared | in_viewer` is computed from booleans on each piece's record.
- **Anomaly detection is per-piece + repo-level.** Duplicate `.af` files across folders, SVGs in the wrong folder, chunk files lost in `inbox/`, etc.
- **`work/state.json` is committed.** Small file, useful as a queryable history. `.gitignore` is intentionally not updated to exclude it.

### 2. `CODE_PROMPT_asset-state-audit.md` authored at repo root

`status: ready-for-code`. Twelve numbered tasks: CLI shape, master-list reader, filename regexes, per-piece dataclass, filesystem walk, SVG analysis, convention checks (linter registry), lifecycle stage derivation, anomaly detection, output JSON, stdout summary, `--piece NNN` query mode. Verification checklist with seven concrete checks against current repo state (e.g., piece 069's `duplicate-affinity-file` anomaly should appear; piece 067 should list both `.af` files without anomaly). What-NOT-to-change locked down: never write to `pieces.csv`, `source/`, `inbox/`, `work/pieces/`. Manual tests scoped to running from repo root with `.venv/bin/python`.

### 3. `LAYER-CONVENTIONS.md` shipped at repo root

The parallel low-cost deliverable. Distilled scannable cheat sheet for SVG authoring: canonical layer names, the cut-layer convention (cutaway / cutaway-N / mask / mask-N inside `<g id="silhouette">`), the cutouts convention (cutout-N inside `<g id="cutouts">`), the axles + `id="north"` convention, the folds-valley / folds-mountain convention, the faithful-trace direction, and a short "common authoring slips the audit catches" section. Designed to stay open on a second window while editing in Affinity.

### 4. `WORKPLAN.md` updated

- **Asset-state / audit tooling** track flipped `queued` → `active`. Next-action updated to "Hand the prompt to a Code session." Recent log entry added.
- **Repo hygiene** track recent log: noted `share/` cleanup-between-sessions; `inbox/` still has 1 `.af` + 8 `.svg` awaiting audit-driven triage.
- **Operations layer** track recent log: cross-reference to this work.
- **SVG layer authoring** track recent log: `LAYER-CONVENTIONS.md` shipped.

### 5. `CLAUDE.md` updated

Added a one-line cross-reference at the top of the "File Naming Conventions" section pointing to `LAYER-CONVENTIONS.md`. Added a new Last-updated entry.

### 6. Files created / modified

| File | Action | Notes |
|---|---|---|
| `CODE_PROMPT_asset-state-audit.md` | created | ready-for-code; ~12 tasks; v0 schema embedded |
| `LAYER-CONVENTIONS.md` | created | scannable authoring cheat sheet |
| `WORKPLAN.md` | edited | asset-state track active; cross-track log entries |
| `CLAUDE.md` | edited | LAYER-CONVENTIONS.md cross-reference + last-updated |
| `sessions/2026-05-03-1400_*.md` | created | this note |

No file renames, no folder restructures, no architectural decisions reopened. `share/` deletion was Zarathale's between-session cleanup, observed and noted but not driven by this session.

## Open Questions

- Should `work/state.json` be gitignored? Decided "no" for v0 (small file, useful as history). Revisit if it bloats or churns aggressively.
- Should the asset-state audit and the M0.5.2 piece-scan-ingest skill collapse into one tool? They have overlapping logic (filename validation, master-list reconciliation). For v0 they stay separate (different output formats, different invocation contexts). Revisit after both have been used in anger.
- Should `LAYER-CONVENTIONS.md` move under `source/transcriptions/` or `work/`, or stay at repo root? Stayed at repo root because it's a working-time reference (similar tier to `CLAUDE.md` and `WORKPLAN.md`); the source documents in `source/transcriptions/` are stable reference, this one will iterate.
- The `--check` mode (CI-style exit-code-on-failure) is documented in the prompt as optional v0. If Code doesn't ship it, that's fine — log it as a v0.1 feature and revisit.

## Next-Session Handoff

1. Hand `CODE_PROMPT_asset-state-audit.md` to a Code session. The prompt is self-contained — no other reading required beyond the listed prerequisites.
2. After Code ships and Alan merges, run the audit: `.venv/bin/python work/scripts/audit_state.py`. The first run is the empirical test of the schema — read `work/state.json` and look for surprises (pieces in unexpected stages, anomalies that don't match intuition).
3. The audit's output then feeds the **Repo hygiene** track's open question (what to do with `inbox/`'s leftover files). Likely a follow-up cleanup session moves the right `.af` files into `source/pieces/` (or `work/pieces/NNN/` once that path is conventionalized for working files), promotes inbox PNGs that should have landed in `source/pieces/`, etc.
4. The asset-state track's downstream items (per-piece sidecar files, browser dashboard) stay queued until v0 has been used for a few sessions and the schema has had a chance to be wrong.
5. Step 4 of the original plan (cheat sheet) shipped this session. Step 5 (per-piece sidecars + dashboard) is intentionally not started.

## Addendum (~15:00) — piece 071 review surfaced two convention corrections

Alan re-exported `inbox/071.svg` after adding `folds-valley` and `marks` layers in Affinity. Reviewing the export flushed out two errors in the docs that had to be fixed in this same session before the audit prompt is handed to Code:

1. **Layer name was wrong in the docs.** The canonical "everything else from the print" layer is `marks`, not `marks-other`. `preview.html` already used `marks` (line 840 skipIds set), but `CLAUDE.md`, `LAYER-CONVENTIONS.md`, `work/SPEC-3D-VIEWER.md`, the asset-state CODE_PROMPT, and `work/pipeline/03-layer-split.py` all carried the wrong name. Fixed across all live files in one pass. Historical files (sessions/, archived prompts, `work/_archive/`) intentionally not touched. Worktree copies under `.claude/worktrees/` ignored.

2. **Landing markers are settled language.** Alan's SVG had `<g id="marks">` with two child ellipses: `id="landing-c70"` and `id="landing-b70"`. These mark the panels on this piece that *receive* a tab from another piece (the inverse of a glue tab). The convention is now in `CLAUDE.md` Architectural Decisions table + File Naming Conventions section, broken out as a new section in `LAYER-CONVENTIONS.md`, and added as two checks in the asset-state CODE_PROMPT (`landing-marker-id-format` + `landing-markers-in-marks-only`). ID grammar: `landing-<tab-letter><piece-number>` where `<tab-letter>` is the lowercase letter from the print and `<piece-number>` is the bare numeric id (no zero-padding) to match the in-print notation. Letter-variant pieces format as `landing-a92a`.

The cross-piece pairing — tab `c` on piece 70's `glue-zones` ⟷ `landing-c70` on piece 71's `marks` — is the connection-graph primitive the assembly engine (M4) will read. Nothing consumes it today, but it's worth authoring as you go because re-deriving it later is harder than capturing it once.

This addendum is also a good real test of the linter-rule pattern the asset-state audit is built around: a new convention landed (landings) + an existing convention name was corrected (marks). Both changes propagated to docs + the audit's check registry without any per-piece migration. Existing SVGs will get re-flagged at next audit run.

Files changed in the addendum:

| File | Change |
|---|---|
| `CLAUDE.md` | rename marks-other → marks (2 spots); new Architectural Decisions row for marks-layer + landing convention; File Naming Conventions list extended with per-element ids inside `<g id="marks">` |
| `LAYER-CONVENTIONS.md` | rename marks-other → marks (3 spots); broke out `marks` into its own section; added landing-marker grammar and cross-piece-pairing note |
| `work/SPEC-3D-VIEWER.md` | rename marks-other → marks (2 spots in convention table + decal-bake step) |
| `WORKPLAN.md` | rename marks-other → marks (1 spot in SVG-layer-authoring track) |
| `CODE_PROMPT_asset-state-audit.md` | rename marks-other → marks in CANONICAL_LAYERS; added two landing-marker checks; added verification item 7a (071 has landing-c70 and landing-b70) |
| `work/pipeline/03-layer-split.py` | rename marks-other → marks (3 spots: docstring, CANONICAL_LAYERS list, fallback assignment) |

## Commit Message

See bottom of cowork response.
