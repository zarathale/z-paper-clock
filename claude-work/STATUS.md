# STATUS.md — z-paper-clock, Claude-led

_The live working surface, post-charter. What tracks are open right now, what's next on each, what's blocked, what was just learned. Updated regularly. The charter (`claude-work/CHARTER.md`) is the standing context; this is what's actually moving._

> **Succession.** This file replaces `WORKPLAN.md` as of charter sign-off (2026-05-04). `WORKPLAN.md` is now legacy — frozen as the pre-charter record. The eight tracks below are carried forward (most reshaped, one closed). For pre-2026-05-04 history on any track, the WORKPLAN log is still the source.

---

## How this works

Each section below is a **track** — chunkier than a task, finer than a milestone. Tracks have:

- **Status** — `active` (being touched now or this week), `queued` (next-up), `blocked`, `paused`, `killed` (closed but kept as record).
- **Hypothesis** — what we're trying to learn or build.
- **Next action** — exactly one line; the thing that would move the track if a session started right now.
- **Recent log** — append a one-line entry at the end of each session that touches the track.

When ~3 session notes have stacked since the last review, run a planning beat (see CHARTER §9 on iteration discipline) and prune.

For per-piece lifecycle state (which pieces are scanned vs. authored vs. sidecared), the source of truth is `work/state.json` produced by `work/scripts/audit_state.py` — that's the asset-state surface, distinct from this work-state surface.

---

## Track: Charter rollout

```yaml
status: active
last_updated: 2026-05-07
next_action: DECISIONS #4 closed (2026-05-07) — Option B: preview.html stays as permanent authoring/QA tool; claude-work/viewer/ deferred until M3 imminent. CHARTER §6 commitments #1 (onboarding) + #2 (first end-to-end piece) + #3 (architecture call) all closed. Active: §6 #4 (bring authoring to sustainable rate — gear train next, brief at `claude-work/to-alan/gear-train/`; 087 reduction-gear disc currently on the bench) and §6 #5 (assemble the clock, M4).
```

**Hypothesis.** Day-one for Claude-as-lead. The skeleton (CHARTER + STATUS + QUEUE + DECISIONS + to-alan/) needs to land before any new building work, so Alan has a coherent surface to read and pull from. After that, the four "first moves" from CHARTER §10 row 8 sequence: (a) skeleton ✅, (b) LAYER-CONVENTIONS co-maintenance routine ✅ (DECISIONS #3), (c) preview.html ↔ work/viewer/ architecture pick ⏸ (deferred per DECISIONS #4), (d) first piece end-to-end ✅ — multi-piece scene assembly shipped (PR #17), anchor cluster places 5 pieces with 067+069 pivot-aligned, and per-fold assembled poses are now durable across reload (PR #19).

**Recent log.**

- 2026-05-09 (evening): DECISIONS #13 closed — three-mode preview.html design + sidecar `assembled.transform`. Three CODE_PROMPTs (PR A/B/C) drafted at repo root; PR D Wall mode deferred. Originated from a session that opened intending to capture pendulum-cluster fold poses; surfaced three preview.html issues that grew into a design pass. Pose capture itself didn't progress — the design that was blocking it did. See `sessions/2026-05-09-1941_cowork_three-mode-preview-design.md`.
- 2026-05-07: DECISIONS #4 closed — architecture Option B (clean separation; `claude-work/viewer/` deferred until M3). `attach-x` convention clarified (see SVG layer authoring track + LAYER-CONVENTIONS.md). CHARTER §6 commitment #3 closed. See `sessions/2026-05-07-1700_cowork_architecture-and-attach-convention.md`.
- 2026-05-06 (post-PR-19 review): assembled-pose shipped via PR #19. `preview.html` reads `assembled.folds` from the per-piece sidecar at load time (precedence `assembled.folds[id]` > fold-id `-<deg>` suffix > 0) and applies the fold rotations immediately so the piece appears in its assembled pose; new "Save assembled pose" button emits a JSON snippet (copy + download) for hand-merge into `work/pieces/NNN/NNN.json`. Scene mode opted out for v1. All 9 verification checks green. Bob batch continuation verified at the same bench: 070 stale fold-ids renamed (panelside* → side*); 093a + 093b refreshed (cutaway hyphenation, combined 093.svg retired to `work/pieces/093/_attic/`, cross-half `attach-x093a` in 093b); 087 .af authoring underway (SVG not yet exported); 097 Affinity collision-suffix left as authoring choice per Alan ("author uniquely if it ever truly matters; otherwise leave"). Fresh `build_assembly_graph.py` run: 17 panels-first pieces, 24 valid authored cross-piece edges. See `sessions/2026-05-06-1900_code_preview-html-assembled-pose.md` (Code) + the post-review session note (Cowork).
- 2026-05-06 (late evening): inferred-connections audit shipped via PR #18. `claude-work/scripts/build_assembly_graph.py` now reads `connections.inferred[]` from per-piece sidecars and merges with SVG-derived edges; every edge carries `provenance: "authored" | "inferred"`. Conflict detection produces soft `inferred_warnings`; never blocks. Legacy `pivot_clusters` flat-list shape preserved (preview.html scene-mode read path unaffected); new parallel `pivot_clusters_provenance`. Markdown report grew `prov` column + "Inferred connections" + "Inferred conflicts" sections. All 7 verification checks passed; `connection-graph.{json,md}` regenerated. See `sessions/2026-05-06-1700_code_build-assembly-graph-inferred.md`.
- 2026-05-06 (evening): assembled-pose + inferred-connections design conversation. Two new sidecar blocks settled (DECISIONS #10 connections.inferred[]; #11 assembled.folds), LAYER-CONVENTIONS extended with "Per-piece JSON sidecar" + "Lane discipline" sections, two CODE_PROMPTs handed off (`CODE_PROMPT_build-assembly-graph-inferred.md`, `CODE_PROMPT_preview-html-assembled-pose.md`). Procedural cleanup of PR #17 (retroactive session note + flipped multi-piece-scene CODE_PROMPT to shipped). See `sessions/2026-05-06-1520_cowork_assembled-pose-and-inferred-connections.md`.
- 2026-05-06 (morning): multi-piece scene assembly shipped via PR #17. Anchor cluster (065/066/067/068/069) places in one scene with 067+069 pivot-aligned on `pivot-anchor`. See `sessions/2026-05-06-0847_code_preview-html-multi-piece-scene.md` (retroactive).
- 2026-05-06 (morning): doc-cleanup pass + multi-piece scene assembly CODE_PROMPT drafted. STATUS/QUEUE/DECISIONS updated; snap-extension CODE_PROMPT archived. CHARTER §6 commitment #2 in reach.
- 2026-05-05 (afternoon-evening): panels-aware parser shipped via PR #15. 069 experiment proved out + scaled to a 9-piece anchor-pendulum batch (DECISIONS #7). First piece end-to-end candidate is now the full anchor cluster, not just a single piece.
- 2026-05-05 (~01:15): orientation/awareness reset conversation landed (DECISIONS #6 closed). LAYER-CONVENTIONS.md updated co-authored; first to-alan/ dropbox entry created. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-05 (~00:30): day-one skeleton reconciliation pass. See `sessions/2026-05-05-0030_cowork_claude-work-reconcile.md`.
- 2026-05-04 (afternoon): charter signed; day-one skeleton landed. See `sessions/2026-05-04-1500_cowork_charter-signed-day-one.md`.

---

## Track: Piece capture (chunk-and-crop)

```yaml
status: complete
last_updated: 2026-05-05
next_action: None — source-side capture closed at 123/123. Track stays open as decision record; flip to `killed` at next planning beat if no new captures surface.
```

**Hypothesis.** Carried forward from WORKPLAN. The chunk-and-crop workflow is reliable; quality is better than gen-1 phone scans. **Capture closed 2026-05-05 at 123/123.** Plate B brackets 013/014/015/016/017 resolved as clones of 012; 090 + 110 captured the same day.

**Blockers.** None — track closed.

**Recent log.**

- 2026-05-05 (afternoon): piece 110 (plate A face-frame end rail) captured. PNG in `source/pieces/110.png`; `work/pieces/110/` initialized with 110.af + starter 110.svg. Authoring in progress alongside the anchor-pendulum batch. **Source-side capture closed at 123/123.**
- 2026-05-05 (afternoon): piece 090 (plate F reduction-gear pulley/disc) captured. PNG in `source/pieces/090.png`; `work/pieces/090/` initialized with 090.af + starter 090.svg.
- 2026-05-05 (morning): plate B brackets 013-017 resolved as clones of 012. Alan flagged the six bracket pieces (012-017) are all identical drawings — same artwork, different positions on the print. Replicated `source/pieces/012.png` → 013/014/015/016/017 (overwriting the redundant separate 015 scan; MD5-verified all six identical). `work/pieces.csv` updated: 013/014/016/017 flipped pending → captured; 012 + 015 notes amended.
- 2026-05-04: track inherited at charter sign-off, no new captures since 2026-05-01. See WORKPLAN entries for 2026-04-30 → 2026-05-01 batches.

---

## Track: SVG layer authoring

```yaml
status: active
last_updated: 2026-05-06
next_action: 087 export landing in `work/pieces/087/` (reduction-gear disc — first gear-disc piece authored, will surface any gear-specific convention needs). 093a/093b fold paths still pending. After that: pull pieces from the gear train per the brief at `claude-work/to-alan/gear-train/` (covers §II.B motor/middle/escape + §II.D reduction-gear/hands; the timing chain and display chain are kinematically separate so stack ordering has flex). Convention stable.
```

**Hypothesis.** The actual current bottleneck. Conventions now stable post-DECISIONS #7. Each new piece applies the convention and stress-tests it; LAYER-CONVENTIONS.md is the live reference.

**Status detail.** Panels-first SVGs authored: 065 / 066 / 067 / 068 / 069 / 070 / 071 / 072 / 094 / 095 / 096 / 097 / 098 / 099 / 100 / 110. Connection graph at `claude-work/state/connection-graph.{md,json}` resolves 24/24 cross-piece edges across the anchor-pendulum-bob cluster. Pre-pivot cut-line-first pieces (001 / 002 / 058 / 113–116) stay as legacy; no bulk re-authoring planned. 093a/093b live under `work/pieces/093/` but `build_assembly_graph.py`'s main loop only globs `<dirname>.svg`, so the split halves are silently absent from the graph today (script extension queued in QUEUE Soon #4 — not blocking).

**Open questions.**

- **093a/093b fold paths** — both halves have `panels` scaffolding but no fold paths yet. Need valley/mountain fold lines authored before the braces can fold in preview.html. (Cutaway hyphenation + combined-093.svg retirement done in the 2026-05-06 bench pass.)
- **093b `attach-x093a` needs rework** — `x` was invented and doesn't resolve to anything on 093a. Correct approach (mark-first pattern): place a small mark shape on 093a at the joint edge (give it an id, e.g. `joint`), then author `attach-joint093a` on 093b. The mark's centroid becomes the connection point geometry. Alan to rework in Affinity on next touch. LAYER-CONVENTIONS.md updated with the mark-first attach pattern.
- Whether existing pre-pivot pieces ever get re-authored panels-first (vs. staying cut-line-first as legacy) — answered piece-by-piece on touch, not as a bulk decision.

**Closed (post-PR-19 bench pass).**

- ~~**070 stale panel ids**~~ — `panelsideb`/`panelsidec` renamed to `sideb`/`sidec` in `070.af`/`070.svg`; both folds now resolve cleanly in the fresh graph (2/2).
- ~~**097 Affinity collision-suffix**~~ — Alan's call: leave the `attach-a99` + auto-suffixed `attach-a991`/`a992`/`a993`/`a994` state as authored. The parser-tolerance recommendation (strip the digit suffix when the base id already resolves) is logged informationally only — if it ever truly matters, Alan will author each instance with a unique id rather than promote a parser rule. No new convention row.

**Blockers.** None.

**Recent log.**

- 2026-05-09 (23:50): 068 two-component fold graph identified in Bench mode — c1/c2/sidel/sider slot cluster has no fold connecting to main pane chain. Missing fold line on the pane→c1 boundary in `068.af`. Fix deferred to next session.
- 2026-05-07: `attach-x093a` on 093b flagged as a bad invented letter — rework to `attach-<panel-id>093a` form. LAYER-CONVENTIONS.md updated; no new convention needed. See session note `2026-05-07-1700_cowork_architecture-and-attach-convention.md`.
- 2026-05-06 (post-PR-19 bench): 070 stale panel ids renamed (`panelsideb`/`panelsidec` → `sideb`/`sidec`); 093a + 093b refreshed (clean `cutaway` ids; combined `093.svg` retired to `work/pieces/_attic/`; 093b carries cross-half `attach-x093a`); 087 .af authoring underway (no SVG export yet); 097 Affinity collision-suffix left as authoring choice. Fresh graph: 17 panels-first pieces, 24 valid authored edges, 070 folds clean. See `sessions/2026-05-06-1900_code_preview-html-assembled-pose.md` (Code) and the post-review session note (Cowork).
- 2026-05-05 (late night): 093 split into 093a + 093b. `pieces.csv` replaced single 093 row with two rows (status: traced). `build_master_list.py` + `piece_characters_v2.yaml` + `expected_layers.yaml` updated. Combined `093.svg` retired to `_attic/` pending Alan's Affinity pass. See `sessions/2026-05-05-2355_cowork_piece-093-split-and-pieces-csv-cleanup.md`.
- 2026-05-05 (afternoon-evening): anchor-pendulum batch panels-first authoring landed across 9 pieces (065/066/067/068/069/070/071/072 + 099). Bob batch authored same session: 094 ✓, 095 ✓, 096 ✓, 097 ⚠ (collision question open), 098 ✓, 100 (silhouette + marks only; no panels yet). Conventions ratified via DECISIONS #7 (21 specific elements). LAYER-CONVENTIONS.md rewritten as the single canonical reference. See `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md` and `sessions/2026-05-05-1630_cowork_env-buildup-and-fold-step-convention.md`.
- 2026-05-05 (~01:15): orientation/awareness model decision landed (DECISIONS #6: panels-first + authored-vs-derived). Cut-line-first becomes legacy parser. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.

---

## Track: preview.html iteration

```yaml
status: active
last_updated: 2026-05-09
next_action: PR B shipped 2026-05-09 (`_archive/code-prompts/CODE_PROMPT_preview-html-bench-transform.md`) — Bench transform capture loop (per-piece origin auto-detect, transform sliders + TC bidirectional sync, sidecar `assembled.transform` read+write, frame-aware badges). Pose capture for the pendulum cluster (071/070/098/095/094/069/068/066/099) is now executable in Bench mode after merge. PR C `CODE_PROMPT_preview-html-cluster-mode.md` is unblocked at repo root (Cluster mode multi-piece). PR D Wall mode deferred until subassembly authoring is far enough along to need it.
```

**Hypothesis.** A single-file HTML preview tool is the right substrate for testing SVG authoring conventions while the eventual viewer is still upstream. Each new capability gets its own CODE_PROMPT and ships independently. Architecture call (DECISIONS #4) deferred until enough capabilities pile up to force the question.

**What's shipped (relevant to current state).**

- **Multi-piece scene mode** (PR #17) — `loadScene(rawIds)`, `renderSceneMulti(parsedArray)`, side-by-side baseline + pivot-cluster co-location from `connection-graph.json`. Anchor cluster (065/066/067/068/069) renders in one scene with 067+069 pivot-aligned on `pivot-anchor`. Single-piece mode unchanged.
- **Panels-aware parser + hinge forest** (PR #15) — `parsePanelsLayer`, `parsePanelsFirstFolds`, `buildHingeTree`, `renderPanelsFirstScene`. Dispatch banner ("panels-first ✓" / "cut-line-first (legacy)"). `parsed.panelsFirst.{panels, folds, hingeTree, attachPoints, closureAttaches, marks}` fully populated; attachPoints consumed by scene mode.
- **Fold-step + closure-attach** (PR #16) — `<step>-fold-<a>-<b>` ordinal prefix in slider labels; same-piece `attach-<panel-id>` classified as `attach-same-piece`; `closureAttaches` bundle. Console diagnostics for both.
- **Face-graph diagnostic harness** (PR #13), **cut-trim** (PR #14), **source-of-truth piece loader** (PR M0.6.14) — all legacy-path or additive, still present.
- **snap-only-extension** — killed (DECISIONS #6).

**Open questions.**

- Architecture call (DECISIONS #4: graduate into `work/viewer/`, stay separate, or replace) — deferred. Multi-piece scene + assembled-pose will likely settle it.
- **Inter-piece assembled pose** — today scene mode places pieces relative to each other only via shared pivots (one cluster: `anchor`, joining 067+069). General per-edge transforms (tab/landing pose registration) is the M4 work and lives separately. Worth surfacing as a fresh track once assembled-pose ships per-piece.
- 070 has 2 unresolved folds (`fold-panelsideb-tabb`, `fold-panelsidec-tabc`) — panel ids reference stale names from before the convention settled. Alan needs to rename `panelsideb`/`panelsidec` → `sideb`/`sidec` in 070.af.
- 099's curved-fold sliders (`fold-insidetabs`, `fold-outsidetabs`) produce approximate movement — the sketch noted as M6-territory in the session note.

**Recent log.**

- 2026-05-09 (23:50): 069 sidecar created (`work/pieces/069/069.json`) — first in the repo. All 10 folds at −90°, transform Y=7.1/rX=99.5, frame cluster/pivot-anchor. R key dual-listener bug fixed in `preview.html` (R was switching TC to rotate mode AND reloading the piece; `e.defaultPrevented` guard added to reload listener). 068 has a 2-sub-trees authoring problem: c1/c2/sidel/sider slot cluster has no fold connecting it to the main pane chain — deferred to next session. See `sessions/2026-05-09-2230_cowork_bench-pose-capture-069.md`.
- 2026-05-09 (22:19): PR B shipped — Bench mode transform capture loop in `preview.html`. New `computePieceOrigin` (precedence: `pivot-anchor` > `axles[0]` > centroid) + `findPieceCluster` against `connection-graph.json` `pivot_clusters`; new Transform panel with 6 sliders (X/Y/Z mm, rX/rY/rZ deg) + origin badge + frame badge + Reset button; `wrapForTransform` refactored to use an inner group offset by `-origin3js` so `pieceGroup`'s local (0,0,0) = piece's natural rotation pivot; `maybeLoadSidecar` reads `assembled.transform` and applies it on load with origin-mismatch warning; save handler emits `transform` block alongside `folds` (suppressed when pose is identity within ε=0.01); bidirectional slider↔TC sync with rAF throttle. Cluster mode hides the panel; scene mode tears down all per-piece transform context. Verified end-to-end against 069 (pivot-anchor + cluster anchor), 065 (axles[0] + world), 071 (centroid + world), sidecar load+save, identity suppression, mismatch warning, mode toggle. Zero console errors. See `sessions/2026-05-09-2219_code_preview-html-bench-transform.md`.
- 2026-05-09 (evening): DECISIONS #13 closed — three-mode preview.html (Bench / Cluster / Wall) + sidecar `assembled.transform` block for per-piece pose in cluster-local space. Supersedes #11's "out of scope" punt on inter-piece transforms (per-piece in cluster-local replaces per-edge SE(3)). Three CODE_PROMPTs drafted at repo root: PR A (foundational interaction + cutouts) ready-for-code; PR B (Bench transform capture) draft blocked-by PR A; PR C (Cluster mode multi-piece) draft blocked-by PR B. PR D Wall mode deferred. Pose capture for pendulum cluster (this session's opening ask) resumes against PR B's Bench mode. See `sessions/2026-05-09-1941_cowork_three-mode-preview-design.md`.
- 2026-05-06 (late evening): inferred-connections audit-side merge shipped via PR #18. Lives in `claude-work/scripts/build_assembly_graph.py`, not `preview.html`, but tracked here because it's the audit companion to the preview-side assembled-pose CODE_PROMPT (still queued). Sidecars are now a real read surface. See `sessions/2026-05-06-1700_code_build-assembly-graph-inferred.md`.
- 2026-05-06 (evening): two new CODE_PROMPTs drafted ready-for-code — `CODE_PROMPT_preview-html-assembled-pose.md` and `CODE_PROMPT_build-assembly-graph-inferred.md`. Settle the per-piece sidecar's role for assembled-state poses (preview load + save) and learned-but-not-printed cross-piece connections (audit merger with provenance). See `sessions/2026-05-06-1520_cowork_assembled-pose-and-inferred-connections.md`.
- 2026-05-06 (morning): multi-piece scene assembly shipped via PR #17. See `sessions/2026-05-06-0847_code_preview-html-multi-piece-scene.md`.
- 2026-05-06 (morning): `CODE_PROMPT_preview-html-multi-piece-scene.md` drafted ready-for-code. Connection-graph.json is the data source; `parsed.panelsFirst.attachPoints` is the per-piece consumer.
- 2026-05-05 (late night): panels-aware parser + fold-step/closure-attach shipped. PR #15 (23:45) + PR #16 (18:20). See `sessions/2026-05-05-2345_code_preview-html-panels-aware.md` and `sessions/2026-05-05-1820_code_preview-html-fold-step-and-closure-attach.md`.
- 2026-05-05 (~01:15): snap-only-extension killed; panels-aware parser pathway queued. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-04: face-graph diagnostics (PR #13) + cut-trim (PR #14) shipped. Pre-charter log in WORKPLAN for earlier.

---

## Track: Asset-state / audit tooling

```yaml
status: active
last_updated: 2026-05-07
next_action: Cowork follow-up to tagging — merge `character` + `subtype` into pieces.csv, author expected_layers.yaml v1 keyed by character, draft CODE_PROMPT_dashboard-and-audit-v2.md.
```

**Hypothesis.** Carried forward from WORKPLAN. Per-piece state needs its own surface, separate from work-state. `work/scripts/audit_state.py` reads the filesystem and emits `work/state.json` reflecting per-piece lifecycle. Generated, never hand-maintained.

**Status detail.** v0 audit script shipped 2026-05-03 (`work/state.json` exists with rich per-piece data). v1 of the schema sharpened during 2026-05-03 evening; tag-pieces.html v2 prompt drafted. **Tagging pass complete 2026-05-07**: all 124 pieces tagged in `work/piece_characters_v2.yaml` — 0 pair-tags remaining, 0 pending captures. Character distribution: flat=12, flat-axle=29, flat-axle-cutout=11, folded=59, folded-axle=12, reference=1. Bracket corrections from Alan's overnight triage applied; notes cleaned of all audit-trail preambles.

**Charter note.** Audit script + dashboard + new tooling-side standards eventually move under `claude-work/standards/` per CHARTER §5. Existing `work/scripts/audit_state.py` stays in the frozen archive; the next iteration lands under `claude-work/`. Not today — wait until there's a real schema bump or a dashboard ship to do the move.

**Recent log.**

- 2026-05-07: tagging pass complete. All 124 pieces in `work/piece_characters_v2.yaml` — characters, subtypes, notes. 041 pair-tag resolved; 093 split to 093a+093b; bracket corrections applied (038/046/047/062/064/087 → flat-axle; 058/059 → flat-axle-cutout; 079 → flat; 100 → flat-axle). See `sessions/2026-05-07-1030_cowork_piece-characters-v2-cleanup.md`.
- See WORKPLAN asset-state track for the 2026-05-03 history (v0 audit ship, v1→v2 schema sharpen, tag-pieces.html, archetype pivot, dashboard design).

---

## Track: Regions / face-graph design (SPEC-REGIONS.md)

```yaml
status: paused (cut-line-first becomes legacy; panels-first replaces it)
last_updated: 2026-05-05
next_action: No active work until panels-first surfaces specific design needs. SPEC-REGIONS.md captures cut-line-first as the legacy path for already-authored pieces. If panels-first proves out across enough pieces, the successor concept doc lands fresh in `claude-work/standards/` rather than evolving SPEC-REGIONS.md.
```

**Status:** paused per DECISIONS #6. Cut-line-first stays alive in `preview.html` as the legacy parser for pre-pivot pieces (001/002/058/065/066/067/070/071/072/113), but new design work happens panels-first. SPEC-REGIONS.md (in frozen `work/`) is the decision record of the cut-line-first thinking, including how far it got and where the ceiling was.

**What changes when:** if 069 panels-first authoring proves out, and the panels-aware parser pathway in preview.html ships, this track stays paused. If panels-first hits a wall on harder pieces and we end up wanting a hybrid (e.g. panels-first for top-level subdivision + cut-line-first for sub-subdivision within a panel), this track reopens.

**Recent log.**

- 2026-05-05 (~01:15): track paused per DECISIONS #6. Cut-line-first becomes legacy parser; panels-first is the new direction. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-04 (evening): cut-trim refactor of `buildFaceGraph` shipped. SPEC-REGIONS.md's step-1 algorithm validated in milder form — authored-segment cuts with extension-to-nearest-silhouette beat half-plane-to-bigBox. Phantom-strip dynamic re-emerged in residual form (066 has 13 orphans). See preview.html iteration track recent log.
- 2026-05-03: SPEC-REGIONS.md drafted in `work/` (frozen). See `sessions/2026-05-03-0100_cowork_spec-regions.md`.

---

## Track: Orientation / awareness model

```yaml
status: active (executing)
last_updated: 2026-05-06
next_action: No Claude-side blockers. Convention is stable and proven across 16 panels-first pieces. Continue into each new authoring batch as it lands. Reopen for design if a new piece-type surfaces something the 21-point lock-in doesn't cover.
```

**Decision landed: panels-first (B) + authored-vs-derived (D).** See DECISIONS #6 + #7 for full shape. Proved out across a 9-piece anchor-pendulum batch; 24/24 cross-piece edges valid. Multi-piece scene assembly (next Code session) is the execution milestone that shows the model working end-to-end.

**Recent log.**

- 2026-05-05 (afternoon-evening): decision proved out across 9-piece anchor-pendulum batch + bob batch. DECISIONS #7 ratifies 21 convention elements. Connection graph resolves 24/24 edges. See `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md`.
- 2026-05-05 (~01:15): orientation-reset conversation landed. DECISIONS #6 closed. LAYER-CONVENTIONS.md updated. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-04 (~22:00): track opened. See `sessions/2026-05-04-2200_cowork_orientation-reset-research.md`.

---

## Track: Pendulum folding & grouping POC

```yaml
status: killed
closed: 2026-05-06
closed_reason: Absorbed into main authoring + multi-piece scene tracks. 069 (pendulum arm) and 094-098 (pendulum bob) are authored panels-first and in the connection graph. The "first end-to-end" milestone is now the anchor cluster in multi-piece scene assembly — a richer proof than the original pendulum-only POC. G1/G2 grouping + F1 folding still come through the same pathway; they just don't need their own track.
```

---

## Track: Repo hygiene

```yaml
status: paused
last_updated: 2026-05-05
next_action: Watch-and-react. No active asks.
```

**Hypothesis.** Carried forward from WORKPLAN, status downgraded to `paused`. Velocity has come down enough that proactive hygiene work would be premature. The asset-state audit catches the things it can; doc-sweep catches the rest.

**Recent log.**

- 2026-05-05 (morning): lock-file verification closed. Alan ran `git ls-files | grep -F "af~lock~"` and it returned empty — no tracked Windows Affinity lock files to clean up. The `.gitignore` pattern from the 22:00 session prevents recurrence. QUEUE #4 struck.
- 2026-05-04 (~22:00): `.gitignore` extended with the Windows Affinity lock pattern (`*.af~lock~`) alongside the existing macOS/Linux `.~lock.*.af#` and editor-backup `*.af~`. Comment block above the patterns documents which pattern matches which platform. The 22:00 session note flagged 5 tracked lock files (`work/pieces/{001,002,058,066,113}/NNN.af~lock~`) needing `git rm --cached`; verified clean on 2026-05-05.
- 2026-05-03 (evening): filesystem restructure shipped (`.af` + `.svg` colocation; `inbox/` retired). See `sessions/2026-05-03-2345_cowork_filesystem-restructure.md`.

---

## Track: Operations layer

```yaml
status: killed
closed: 2026-05-04
closed_reason: Superseded by claude-work/. The operations-layer goal — give the project a single live working surface — is now answered by the charter + STATUS.md + QUEUE.md + DECISIONS.md. PROJECT-STATE.md and the WORKPLAN.md → STATUS.md migration both came out of this track.
```

**Closing note.** The track did its job. The deliverables (PROJECT-STATE.md, WORKPLAN.md as a v1, the asset-state schema, the LAYER-CONVENTIONS.md cheat sheet) are all in place. The dashboard work continues under the asset-state / audit tooling track. The future-browser-rendered-dashboard idea + the GitHub Projects parking-lot question are now charter-amendment material if they ever come back.

---

*Last updated: 2026-05-09 (late night) — 069 sidecar captured (first in repo); R key dual-listener bug fixed in `preview.html`; 068 two-component fold graph authoring issue identified. Anchor cluster pose capture continues next session: 068 fold fix first, then 067/066/065/068 sidecars, then PR C. See `sessions/2026-05-09-2230_cowork_bench-pose-capture-069.md`.*

*Earlier 2026-05-09 (evening) — DECISIONS #13 closed: three-mode preview.html (Bench / Cluster / Wall) + sidecar `assembled.transform` block for per-piece pose in cluster-local space. Three CODE_PROMPTs drafted at repo root (PR A foundational ready-for-code; PR B Bench transform draft; PR C Cluster mode draft); PR D Wall mode deferred. Charter rollout + preview.html iteration tracks updated. Pose capture for the pendulum cluster (the session's opening ask) didn't progress — the design that was blocking it did. Resumes against PR B's Bench mode once that ships. See `sessions/2026-05-09-1941_cowork_three-mode-preview-design.md`.*

*Earlier 2026-05-06 (post-PR-19 review) — assembled-pose load + save shipped via PR #19; bob batch continuation verified at the same bench (070 stale fold-ids renamed, 093a/093b cutaway hyphenation + combined 093 retired to nested `_attic/`, 087 .af underway, 097 collision left as authoring choice — informational, not a convention). Charter rollout + preview.html iteration + SVG layer authoring tracks updated. Now-queue cleared of preview-side Code work; tag-pieces.html promoted to Now #1; architecture decision (DECISIONS #4) is the next Cowork beat.*

*Earlier 2026-05-06 (late evening) — inferred-connections audit-side merge shipped via PR #18 (`claude-work/scripts/build_assembly_graph.py` reads `connections.inferred[]` from per-piece sidecars; every edge tagged `provenance`; soft conflict warnings; legacy `pivot_clusters` shape preserved). Charter rollout + preview.html iteration tracks updated. Now-queue narrows from two Code prompts to one — assembled-pose (Now #1) is the next preview-side pull.*

*Earlier 2026-05-06 (evening) — assembled-pose + inferred-connections design conversation. Two new CODE_PROMPTs queued (assembled-pose preview-side, inferred-connections audit-side; DECISIONS #10 + #11 closed). LAYER-CONVENTIONS extended with "Per-piece JSON sidecar" + "Lane discipline" sections. Procedural cleanup of PR #17 (retroactive session note + flipped multi-piece-scene CODE_PROMPT to shipped). Charter rollout track flipped: CHARTER §6 commitment #2 effectively closed (anchor cluster places end-to-end).*

*Earlier 2026-05-06 (morning) — doc-cleanup pass post-2026-05-05 sprint. Charter rollout, SVG layer authoring, preview.html iteration, and orientation/awareness model tracks updated to reflect: panels-aware parser shipped (PR #15), fold-step/closure-attach shipped (PR #16), anchor-pendulum batch done, bob batch partial, 093 split, source capture closed 123/123. Pendulum POC track killed (absorbed into authoring + multi-piece scene tracks). CODE_PROMPT_preview-html-multi-piece-scene.md drafted ready-for-code; shipped same morning as PR #17.*

*Earlier 2026-05-05 (evening–midnight) — anchor-pendulum batch, panels-aware + fold-step ships, 093 split. See session notes `2026-05-05-2330`, `2026-05-05-2345`, `2026-05-05-2355`, `2026-05-05-1820`, `2026-05-05-1630`.*

*Earlier 2026-05-05 (morning) — plate B brackets resolved; source capture closed 123/123; lock-file verification clean; DECISIONS #6 panels-first orientation model landed.*

*Earlier 2026-05-04 — charter signed; day-one skeleton; cut-trim + face-graph-diagnostics shipped.*
