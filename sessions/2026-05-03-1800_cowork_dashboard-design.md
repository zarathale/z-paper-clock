---
date: 2026-05-03
start_time: "18:00"
end_time: "18:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Settle the design for `dashboard.html` — a static HTML viewer over `work/state.json`, parallel to `preview.html`. Talk-through session, no files shipped (beyond this note + a small `WORKPLAN.md` update). Two follow-ups queued: a session to author `work/expected_layers.yaml` defaults, then a CODE_PROMPT to extend `audit_state.py` and ship the dashboard.

## Context

Asset-state audit shipped earlier today (`sessions/2026-05-03-1600_code_asset-state-audit-v0.md`); `work/state.json` now exists with rich per-piece data — file paths, layer inventories, convention checks, derived stage, anomalies. Alan opened a thread to design the dashboard that visualizes it. He led with concrete thoughts (kanban-style buckets → bucket selector → scrollable piece list → detail panel with thumbnail + layer info + .af/.svg links + a "needed but missing" layer flag) and asked to talk it through.

## Decisions Settled

**Layout — filter-and-list, not kanban.** "Kanban" was the entry framing but evolved during conversation. Three-pane: bucket menu (top or side, TBD at build time) → scrollable list of pieces in that bucket → detail panel for the selected piece. Single bucket visible at a time, not multi-column.

**Substrate — `dashboard.html` at repo root, parallel to `preview.html`.** Single static HTML file, fetches `work/state.json`, opens with `file://`. Same authoring story as `preview.html`. No build step. `.af` / `.svg` links become `file:///abs/...` URLs that open in Affinity / browser locally.

**Bucket menu — derived from state.json, not hardcoded.** This addresses Alan's "varies over time as we add new layer requirements" requirement. Bucket chips fall into three groups, all auto-generated:

- **Lifecycle** (8 chips, derived from `summary.by_stage`): pending_capture, captured_only, affinity_started, svg_drafted, svg_layered, svg_validated, sidecared, in_viewer.
- **Convention uplift** (N chips, derived from `summary.convention_pass_rates`): one chip per check id with `fail > 0`. Menu shrinks as fixes land, grows when a new check is added or a non-conforming piece lands. Each chip filters to the failing pieces for that check.
- **Anomalies** (1 chip): every piece with non-empty `anomalies`.

Plus an "All pieces" catch-all. Section / plate cross-cuts deferred from v0.

**Thumbnails — live inline SVG.** SVG injected into the detail panel; CSS hides `[id^="mask"]` so visual frames disappear and silhouette + folds + axles + glue-zones + labels + marks all render. Cheap, see-what-you-authored, no second pipeline step. Pre-generated PNGs stay as a future option if perf bites at 123 inline SVGs.

**Expected-layers hints — `work/expected_layers.yaml`, hand-maintained.** Format:

```yaml
defaults_by_section:
  framework:        [silhouette, folds-mountain, folds-valley, glue-zones, marks]
  mechanism:        [silhouette, axles, glue-zones, marks]
  anchor-pendulum:  [silhouette, axles, folds-valley, folds-mountain, glue-zones, marks]
  hands:            [silhouette]
  weight:           [silhouette]
  face-case:        [silhouette, folds-valley, folds-mountain, glue-zones, marks]

per_piece:
  "045": { remove: [folds-valley] }
  "094": { add: [labels] }
```

Section defaults do the heavy lifting (one row buys 25–30 pieces); per-piece `add` / `remove` handles exceptions. Carries the same time-varying property as the convention checks: add `marks` to a section's default and every piece in that section without a marks layer instantly flags.

**Diff is computed in `audit_state.py`, not in the dashboard.** The audit grows a small expected-layers reader and adds two new fields per piece: `expected_layers` (resolved) and `missing_layers` (expected − present). Plus a new convention check (e.g. `expected-layers-present`) so the failure surfaces in the convention-uplift bucket-chip group automatically. Dashboard stays a pure viewer.

This bends the audit's "nothing is hand-maintained" purity slightly, but it's symmetrical with the existing `pieces.csv` `status` column: state is filesystem-derived, expectations are hand-maintained, diff is computed.

**Format — YAML.** Reads better when hand-edited. Adds one pip dep (`pyyaml`) to the audit's toolchain; acceptable.

## Decisions Deferred

- **Section default values themselves** — Alan wants to author these in a session of their own before the CODE_PROMPT. Working list will be populated against §II.A framework / §II.B mechanism / §II.C anchor+pendulum / §II.D hands / §II.E weight / §II.F face+case (drawing on `source/transcriptions/instructions.md`).
- **Element-id-level expectations** — e.g. "this piece has tabs labeled a, b, c per pieces.csv notes, so glue-zones should contain `tab-a`, `tab-b`, `tab-c`." Real future want, much richer than layer-presence. Held for v1; v0 is layer-presence only.
- **Where `expected_layers.yaml` lives** — repo root vs. `work/`. Will fall out naturally during the YAML-authoring session. Leaning `work/expected_layers.yaml` since it's audit-script input, not a doc.
- **Bucket menu placement** — top tabs vs. side bar. Decide at build time (either works; Alan's call when he sees a draft).
- **Whether the dashboard ever ships to GitHub Pages.** Architecturally compatible (state.json + dashboard.html are static). Path-stripping pass on state.json + conditioning the local-file links on hostname is the work it would take. Out of scope for v0.

## Flagged for the CODE_PROMPT

- **`repo_root` path normalization.** Current `state.json` shows `repo_root: /Users/.../.claude/worktrees/loving-davinci-3f38a4/...` because the audit ran inside a worktree. The dashboard needs the *real* repo root for `file://` links to resolve. Fix in audit (resolve worktree symlinks before writing repo_root) or in dashboard (pass it in via a sibling config). Audit-side is cleaner.
- **Two state.json schema additions** (bumps `schema_version` to 2): `pieces.<id>.expected_layers: [layer-name, ...]` and `pieces.<id>.missing_layers: [layer-name, ...]`.
- **One new check function**: `expected-layers-present` (severity advisory; passes when `missing_layers` is empty). Auto-flows into the convention-uplift bucket chips because the dashboard reads from `summary.convention_pass_rates`.
- **One new pip dep**: `pyyaml`. Add to whatever the project's "install fresh" instructions reference (currently the README's dev-environment section in CLAUDE.md doesn't list it, since YAML wasn't a project dep until now).

## Files Created / Modified

| File | Action | Notes |
|---|---|---|
| `sessions/2026-05-03-1800_*.md` | created | this note |
| `WORKPLAN.md` | edited | Asset-state track next-action updated; recent-log entry added |

No CLAUDE.md edits; no architectural decision finalized this session (the YAML format choice + bucket-menu pattern get codified when the CODE_PROMPT lands and ships). No ROADMAP edits.

## Next-Session Handoff

Alan's plan, in order:

1. **Cowork session** to author `work/expected_layers.yaml` (section defaults + initial per-piece overrides for known exceptions) and **finalize the CODE_PROMPT** for the audit extension + dashboard.
2. **Code session** to ship the audit-script extension and `dashboard.html`.

Open the next Cowork session against this note + `work/state.json` + `source/transcriptions/instructions.md` (for section anatomy). The CODE_PROMPT should reference this note as the design record.

## Cowork Commit Message

Subject:

```
add dashboard design session note; update workplan asset-state track
```

Body:

```
Talk-through Cowork session that designed dashboard.html as a static-HTML
viewer over work/state.json, parallel to preview.html. Settled the bucket
model (filter-and-list, derived from state.json — lifecycle stages +
per-failing-check chips + anomalies), the thumbnail strategy (live inline
SVG), and the expected-layers hints mechanism (work/expected_layers.yaml
with section defaults + per-piece overrides; diff computed in audit_state.py
and exposed as new state.json fields + a new convention check). Format:
YAML. Deferred: section default values (next session), element-id-level
expectations (v1), bucket placement (build time). Flagged for the
CODE_PROMPT: repo_root path normalization, two state.json schema additions,
one new check function, one new pip dep (pyyaml).

WORKPLAN.md Asset-state track next-action updated to point at the upcoming
YAML-authoring session; recent-log entry added.

See sessions/2026-05-03-1800_cowork_dashboard-design.md for the full design
walkthrough including the bucket-menu sketch and the YAML schema sketch.
```
