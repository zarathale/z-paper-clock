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
last_updated: 2026-05-06
next_action: Multi-piece scene (PR #17) + inferred-connections audit (PR #18) shipped. CHARTER §6 commitment #2 (first piece end-to-end) closed for the anchor cluster; the connection graph now has provenance and is ready to absorb learned cross-piece knowledge from sidecars. Architecture decision (DECISIONS #4: preview.html ↔ work/viewer/) still deferred — assembled-pose ship (Now #1) will likely tip it.
```

**Hypothesis.** Day-one for Claude-as-lead. The skeleton (CHARTER + STATUS + QUEUE + DECISIONS + to-alan/) needs to land before any new building work, so Alan has a coherent surface to read and pull from. After that, the four "first moves" from CHARTER §10 row 8 sequence: (a) skeleton ✅, (b) LAYER-CONVENTIONS co-maintenance routine ✅ (DECISIONS #3), (c) preview.html ↔ work/viewer/ architecture pick ⏸ (deferred per DECISIONS #4), (d) first piece end-to-end ✅ — multi-piece scene assembly shipped (PR #17), anchor cluster places 5 pieces with 067+069 pivot-aligned.

**Recent log.**

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
next_action: Bob batch continuation — 093a/093b (add fold paths, fix cutaway hyphenation, retire combined 093.svg); 097 Affinity collision-suffix decision (convention #16 tolerance vs. per-instance ids); escape wheel 087. Pull when bench time happens. Convention stable.
```

**Hypothesis.** The actual current bottleneck. Conventions now stable post-DECISIONS #7. Each new piece applies the convention and stress-tests it; LAYER-CONVENTIONS.md is the live reference.

**Status detail.** Panels-first SVGs authored: 065 / 066 / 067 / 068 / 069 / 070 / 071 / 072 / 094 / 095 / 096 / 097 / 098 / 099 / 100 / 110. Connection graph at `claude-work/state/connection-graph.{md,json}` resolves 24/24 cross-piece edges across the anchor-pendulum-bob cluster. Pre-pivot cut-line-first pieces (001 / 002 / 058 / 113–116) stay as legacy; no bulk re-authoring planned.

**Open questions.**

- **097 Affinity collision-suffix** — 5 visually-distinct landings on 099 came out as duplicate `attach-a99` ids + Affinity auto-suffixed `attach-a991`/`a992`/`a993`/`a994`. Parser reads those as cross-piece partners 991-994 (non-existent). Fix: either convention #16 tolerance (strip the digit suffix when the base id already resolves) or author per-instance ids from the start. Alan deferred; still open.
- **093a/093b fold paths** — both halves have `panels` scaffolding but no fold paths yet. Need valley/mountain fold lines authored before the braces can fold in preview.html.
- **`attach-x<piece-id>` convention** — the 093 session surfaced a glue-only inter-piece attach form (no printed tab letter) not yet in LAYER-CONVENTIONS.md. Worth a small conventions pass before more pieces follow the pattern.
- Whether existing pre-pivot pieces ever get re-authored panels-first (vs. staying cut-line-first as legacy) — answered piece-by-piece on touch, not as a bulk decision.

**Blockers.** None.

**Recent log.**

- 2026-05-05 (late night): 093 split into 093a + 093b. `pieces.csv` replaced single 093 row with two rows (status: traced). `build_master_list.py` + `piece_characters_v2.yaml` + `expected_layers.yaml` updated. Combined `093.svg` retired to `_attic/` pending Alan's Affinity pass. See `sessions/2026-05-05-2355_cowork_piece-093-split-and-pieces-csv-cleanup.md`.
- 2026-05-05 (afternoon-evening): anchor-pendulum batch panels-first authoring landed across 9 pieces (065/066/067/068/069/070/071/072 + 099). Bob batch authored same session: 094 ✓, 095 ✓, 096 ✓, 097 ⚠ (collision question open), 098 ✓, 100 (silhouette + marks only; no panels yet). Conventions ratified via DECISIONS #7 (21 specific elements). LAYER-CONVENTIONS.md rewritten as the single canonical reference. See `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md` and `sessions/2026-05-05-1630_cowork_env-buildup-and-fold-step-convention.md`.
- 2026-05-05 (~01:15): orientation/awareness model decision landed (DECISIONS #6: panels-first + authored-vs-derived). Cut-line-first becomes legacy parser. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.

---

## Track: preview.html iteration

```yaml
status: active
last_updated: 2026-05-06
next_action: One CODE_PROMPT queued ready-for-code at repo root: `CODE_PROMPT_preview-html-assembled-pose.md` (per-fold assembled-state load + save; preview-side, DECISIONS #11). Inferred-connections audit-side companion shipped via PR #18 — sidecars are ready to be read by the audit; no preview-side change needed. Architecture call (DECISIONS #4) still deferred — assembled-pose ship will likely tip it.
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
last_updated: 2026-05-04
next_action: tag-pieces.html v2 schema — Alan ships CODE_PROMPT_tag-pieces-v2-schema.md via a Code session, then tags 123 pieces. Cowork follow-up: merge `character` + `subtype` into pieces.csv, author expected_layers.yaml v1 keyed by character, draft CODE_PROMPT_dashboard-and-audit-v2.md.
```

**Hypothesis.** Carried forward from WORKPLAN. Per-piece state needs its own surface, separate from work-state. `work/scripts/audit_state.py` reads the filesystem and emits `work/state.json` reflecting per-piece lifecycle. Generated, never hand-maintained.

**Status detail.** v0 audit script shipped 2026-05-03 (`work/state.json` exists with rich per-piece data). v1 of the schema sharpened during 2026-05-03 evening; tag-pieces.html v2 prompt drafted (`CODE_PROMPT_tag-pieces-v2-schema.md`, ready-for-code). Tagging session pending Alan's bench time.

**Charter note.** Audit script + dashboard + new tooling-side standards eventually move under `claude-work/standards/` per CHARTER §5. Existing `work/scripts/audit_state.py` stays in the frozen archive; the next iteration lands under `claude-work/`. Not today — wait until there's a real schema bump or a dashboard ship to do the move.

**Recent log.**

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

*Last updated: 2026-05-06 (late evening) — inferred-connections audit-side merge shipped via PR #18 (`claude-work/scripts/build_assembly_graph.py` reads `connections.inferred[]` from per-piece sidecars; every edge tagged `provenance`; soft conflict warnings; legacy `pivot_clusters` shape preserved). Charter rollout + preview.html iteration tracks updated. Now-queue narrows from two Code prompts to one — assembled-pose (Now #1) is the next preview-side pull.*

*Earlier 2026-05-06 (evening) — assembled-pose + inferred-connections design conversation. Two new CODE_PROMPTs queued (assembled-pose preview-side, inferred-connections audit-side; DECISIONS #10 + #11 closed). LAYER-CONVENTIONS extended with "Per-piece JSON sidecar" + "Lane discipline" sections. Procedural cleanup of PR #17 (retroactive session note + flipped multi-piece-scene CODE_PROMPT to shipped). Charter rollout track flipped: CHARTER §6 commitment #2 effectively closed (anchor cluster places end-to-end).*

*Earlier 2026-05-06 (morning) — doc-cleanup pass post-2026-05-05 sprint. Charter rollout, SVG layer authoring, preview.html iteration, and orientation/awareness model tracks updated to reflect: panels-aware parser shipped (PR #15), fold-step/closure-attach shipped (PR #16), anchor-pendulum batch done, bob batch partial, 093 split, source capture closed 123/123. Pendulum POC track killed (absorbed into authoring + multi-piece scene tracks). CODE_PROMPT_preview-html-multi-piece-scene.md drafted ready-for-code; shipped same morning as PR #17.*

*Earlier 2026-05-05 (evening–midnight) — anchor-pendulum batch, panels-aware + fold-step ships, 093 split. See session notes `2026-05-05-2330`, `2026-05-05-2345`, `2026-05-05-2355`, `2026-05-05-1820`, `2026-05-05-1630`.*

*Earlier 2026-05-05 (morning) — plate B brackets resolved; source capture closed 123/123; lock-file verification clean; DECISIONS #6 panels-first orientation model landed.*

*Earlier 2026-05-04 — charter signed; day-one skeleton; cut-trim + face-graph-diagnostics shipped.*
