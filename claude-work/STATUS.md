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
last_updated: 2026-05-05
next_action: Watch how 069 authoring lands as the first real test of panels-first + the to-alan/ dropbox protocol in actual use. After 069 cycles back, the next charter rollout move is either (a) "first piece end-to-end" lands as 069 itself if panels-first wins (close to commitment #2 in CHARTER §6), or (b) reset back to picking a different first-end-to-end piece. Architecture decision (DECISIONS #4) still deferred, now informed by what panels-aware parsing surfaces.
```

**Hypothesis.** Day-one for Claude-as-lead. The skeleton (CHARTER + STATUS + QUEUE + DECISIONS + to-alan/) needs to land before any new building work, so Alan has a coherent surface to read and pull from. After that, the four "first moves" from CHARTER §10 row 8 sequence: (a) skeleton ✅, (b) LAYER-CONVENTIONS co-maintenance routine ✅ (DECISIONS #3), (c) preview.html ↔ work/viewer/ architecture pick ⏸ (deferred per DECISIONS #4), (d) first piece end-to-end ⏸ (queued, but 069 is now a strong candidate via panels-first).

**Open questions.**

- Pendulum POC (piece 094) vs. piece 069 (now the panels-first test piece) for "first end-to-end." 069 is in motion via QUEUE.md #1 anyway; folding it through to preview.html would double as the panels-aware parser proof. Earmark for after 069 authoring lands.

**Recent log.**

- 2026-05-05 (~01:15): orientation/awareness reset conversation landed (DECISIONS #6 closed: panels-first + authored-vs-derived). LAYER-CONVENTIONS.md updated co-authored; first to-alan/ dropbox entry created (`069-panels-first/`). See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`. Charter §6 commitment #2 (first piece end-to-end) gains 069 as a strong candidate.
- 2026-05-05 (~00:30): reconciliation pass against on-disk state of `claude-work/`. Skeleton confirmed present (Code session that "saw only CHARTER.md" was running in a worktree). STATUS / QUEUE / DECISIONS updated for cut-trim + orientation-reset outflows. See `sessions/2026-05-05-0030_cowork_claude-work-reconcile.md`.
- 2026-05-04 (afternoon): charter signed; day-one skeleton landed. STATUS / QUEUE / DECISIONS / `to-alan/README.md` written. WORKPLAN.md flagged as legacy (kept in place). See `sessions/2026-05-04-1500_cowork_charter-signed-day-one.md`. Skeleton files are untracked at time of writing — they ride on the next cowork commit (this reconciliation pass).

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
last_updated: 2026-05-05
next_action: With the anchor-pendulum batch landed and conventions ratified (DECISIONS #7), the next authoring batch is the bob pieces (094 + 095 + 096 + 097 + 098 + 093a/093b) and the escape wheel (likely 087 in the reduction-gear cluster). 093 was split into 093a + 093b on 2026-05-05 — the (a+b) pair is the brace template, instantiated 6 times in piece 94. No urgency; pull when bench time happens. The convention is stable; new pieces should drop into the established pattern.
```

**Hypothesis.** The actual current bottleneck. Conventions are still iterating as new piece-types reveal new authoring requirements (cut-layer + axles-with-north + marker-bound fold ids all shipped in the past week). Each new piece both applies the conventions and stress-tests them.

**Status detail.** A small handful of pieces authored end-to-end (001 / 002 / 058 / 065 / 066 / 067 / 069 / 070 / 071 / 072 / 113). 066's failure mode (co-linear marker-bound folds + Affinity cross-layer id collision) drove the morning convention revision; cut-trim ship that evening (preview.html track) improved 066 from 19 → 13 orphans + 17/17 markers resolving but didn't fully resolve it. 22:00 SVG inventory pulled across 001/002/066/067/069/070/113 and surfaced specific drift items — see Recent log.

**Authoring drift surfaced 22:00 (needs naming).**

- `axles` layer carrying `hole-f<piece>` / `hole-g<piece>` ids on 001/002 — pin-holes, not rotation centers; closer to landings than axles.
- `landing-tab-aa` on 002 — mixes the documented `landing-<tab-letter><piece-number>` format. Plausibly closure-constraint, plausibly something else.
- `anchor-pivot` ids on 067 + 069 — outside the canonical layer set.
- `mark-h` / `mark-i` on 069 — construction or registration marks, not connection points.
- `id="tab"` (no letter) on 070 in `folds-mountain`.
- 113/114/115/116 carry `mountain-folds` / `valley-folds` (reversed from canonical), `cutout` singular without `-N` suffix, and bare `hole-f` / `hole-g` (no piece suffix — shape is shared across four pieces).
- Affinity auto-rename clusters: `fold-tab-a` × 4 on 001, `tab-e1` etc.

**Open questions.**

- Whether 069's panels-first authoring is workable in Affinity at acceptable effort. The experiment that answers this is QUEUE.md #1.
- The fold-binding shape sub-decision: the brief proposes `id="fold-<panel-a>-<panel-b>"` on the fold path; if Affinity collision-renames any (rare; only when two folds bind the same pair), or the form feels awkward in Affinity, we adapt to a sidecar JSON edge list or a hybrid.
- Whether existing pieces ever get re-authored panels-first (vs. staying on cut-line-first as legacy) — answered piece-by-piece on touch, not as a bulk decision.
- Which pieces are simple enough to delegate to a Haiku-class model with a tight prompt, vs. needing Sonnet-or-better hand-attention.

**Blockers.** None for the next move (069 authoring brief is in `claude-work/to-alan/`). The panels-aware parser pathway in preview.html is downstream and waits for 069 authoring to land.

**Recent log.**

- 2026-05-05 (afternoon-evening): anchor-pendulum batch panels-first authoring landed across 9 pieces (065/066/067/068/069/070/071/072 + 099). Conventions ratified end-to-end via DECISIONS #7 (21 specific convention elements). LAYER-CONVENTIONS.md rewritten as the single canonical reference; LAYERS.md (the v0 cheat sheet) deleted. Cross-piece audit script `claude-work/scripts/build_assembly_graph.py` produces `claude-work/state/connection-graph.{md,json}` with 24/24 cross-piece edges valid. See `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md`.
- 2026-05-05 (~01:15): orientation/awareness model decision landed (DECISIONS #6: panels-first + authored-vs-derived). LAYER-CONVENTIONS.md updated; 069 brief drafted; cut-line-first becomes legacy parser. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-04 (morning): marker-bound fold ids convention settled — and revised within the same session for the `fold-` prefix (Affinity collision). Parser landed in preview.html. 066 improved 19 → 5 orphan regions; cylinder still folds into shards. Closure constraint still parked. See `sessions/2026-05-04-0815_cowork_marker-bound-fold-ids.md`.
- 2026-05-04 (late morning): diagnose-first pivot — see preview.html iteration track.
- 2026-05-04 (~22:00): orientation/awareness reset research session. SVG inventory across 7 priority pieces surfaced authoring drift; four candidate framings + five design questions on the whiteboard. See `sessions/2026-05-04-2200_cowork_orientation-reset-research.md`. Alan flagged a course change incoming after the session — that course change WAS this conversation; the framings did get walked through and panels-first won.

---

## Track: preview.html iteration

```yaml
status: active
last_updated: 2026-05-05
next_action: Code session against `CODE_PROMPT_preview-html-panels-aware.md` (drafted, ready-for-code at repo root). Adds the panels-aware parser pathway alongside the legacy cut-line-first path. Single-piece scope; multi-piece scene assembly comes in a follow-up prompt. Verification across 069/068/071/099.
```

**Hypothesis.** Carried forward from WORKPLAN. A single-file HTML preview tool at repo root is the right substrate for testing SVG authoring conventions piece-by-piece, while the eventual viewer is still upstream. Each new convention or fix gets its own CODE_PROMPT and ships independently. The architecture decision (graduate / stay separate / replace) is intentionally deferred until the reset conversation settles.

**Charter note.** The architecture call (preview.html ↔ work/viewer/) is one of the four first-moves I committed to in §10 row 8. It's open question 0.6.13 in the inherited SPEC and DECISIONS #4 in this folder. I'm not making it today — the orientation/awareness reset will reshape what preview.html needs to do before the architecture answer becomes obvious.

**What shipped today (Code, 2026-05-04).**

- **Face-graph diagnostic harness** (PR #13, commit `6ecdb45`) — `_diag` payload, JSON dump button, 2D viewBox-space overlay, console summary. Permanent fixture in preview.html. See `sessions/2026-05-04-1145_code_preview-html-face-graph-diagnostics.md`.
- **Cut-trim algorithm refactor** (PR #14, commit `e0cb5cb`) — replaced half-plane infinite-line cuts with authored-segment cuts using `fold.start`/`fold.end` (extend-to-nearest-silhouette, NOT to bigBox). Dropped the `passive` field; collapsed two-pass BFS to a single pass. Added `markerToRegionId` map as forward-look infrastructure for the M4 assembly engine. Deviation from the prompt's `authoredStart`/`authoredEnd` documented inline — keeping `fold.start`/`fold.end` is strictly better for normal pieces and partially-better for 066. See `sessions/2026-05-04-2103_code_preview-html-cut-trim.md`.

**Cut-trim residual on 066.** 27 regions, 20 fold-edges (of 21 expected), 17/17 markers resolve, 13 orphan regions still. The phantom-strip dynamic re-emerges in milder form when "extend to nearest silhouette boundary" still reaches across the strip on near-vertical fold lines. A "snap-only" extension tolerance (`0.005 * diagLen`) is the queued small follow-up; not implemented because the reset conversation may obsolete it. Dead code (`bigBox`, `halfPlanePoly`, `toRing`/`toPCPoly`/`fromRing`, `edgeMidpoint`, `ADJ_EPS`, the `extendedStart`/`extendedEnd` paths) intentionally left in per the cut-trim prompt's minimal-surface-area principle.

**Open questions.**

- Whether the architecture decision (DECISIONS #4) can still wait. Reset conversation landed on panels-first; preview.html now grows a panels-aware path alongside cut-trim. That additional surface area informs but doesn't force the architecture call.
- Snap-only extension question is closed — killed by DECISIONS #6.

**Recent log.**

- 2026-05-05 (late evening): `CODE_PROMPT_preview-html-panels-aware.md` drafted ready-for-code. Conventions stable (DECISIONS #7); `claude-work/scripts/build_assembly_graph.py` provides reference parser implementation in Python. Ships when Alan opens a Code session against the prompt. See `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md`.
- 2026-05-05 (~01:15): orientation/awareness reset landed; snap-only-extension follow-up killed; panels-aware parser pathway queued, blocked on 069 authoring. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-04 (~21:00): cut-trim shipped via PR #14. See above.
- 2026-05-04 (~11:45): face-graph diagnostic harness shipped via PR #13. See above.
- 2026-05-04 (late morning): diagnose-first pivot. `CODE_PROMPT_preview-html-face-graph-diagnostics.md` drafted ready-for-code. Stray `work/pieces/066/001.svg` cleaned up. See `sessions/2026-05-04-1100_cowork_face-graph-diagnostics.md`.
- 2026-05-04 (morning) and earlier: marker-bound fold ids implementation, M0.6.14 source-of-truth ship, v1b clean-start prompt, etc. See WORKPLAN preview.html iteration track for full pre-charter log.

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
last_updated: 2026-05-05
next_action: Alan pulls the 069 panels-first authoring brief at `claude-work/to-alan/069-panels-first/README.md` (also QUEUE.md #1). When `069-panels.svg` lands, I review + draft the CODE_PROMPT for the panels-aware parser pathway in preview.html. Until then, the track is waiting on Alan's bench time, not on Claude's thinking.
```

**Decision landed: panels-first (B) + authored-vs-derived (D).** See DECISIONS #6 for the full shape — concrete-decision body has 8 numbered points (new `panels` layer, fold-binding shape, `axles` split into rotation-only + new `attach-points`, `marks` narrows to construction/registration only, closure as edge attribute, 113–116 stays clone-per-piece for now, cut-line-first stays as legacy, snap-only-extension killed). The course change Alan flagged at the close of the 22:00 session was this conversation; the four framings + five questions did survive and got walked through.

**What this means downstream.**

- **SVG layer authoring track:** unblocks — concrete next move is Alan authors 069 panels-first.
- **preview.html iteration track:** snap-only-extension killed; panels-aware parser pathway queued (Code session, blocked on 069 authoring).
- **Regions / face-graph design track:** cut-line-first becomes legacy. The SPEC-REGIONS.md doc (in frozen `work/`) captures cut-line-first as it existed; whatever evolves next gets a fresh home in `claude-work/standards/`. Probably doesn't get drafted until panels-first proves out on multiple pieces.
- **DECISIONS #4 (preview.html ↔ work/viewer/):** still deferred, but the parser surface preview.html now grows a panels-aware path, which informs the eventual architecture call.
- **DECISIONS #5 (cut-trim implementation deviation):** closes as historical record once panels-first dominates. Cut-trim stays alive for legacy pieces.
- **LAYER-CONVENTIONS.md:** gains `panels` and `attach-points` layers; `axles` and `marks` narrow. Co-authored update follows in this same commit.

**Open dependencies.**

- 069 authoring needs to actually happen — Alan's bench, pull-based.
- The fold-binding shape (`fold-<panel-a>-<panel-b>` id form vs. JSON sidecar edge list vs. hybrid) is sub-decided once 069 authoring teaches us which is least painful. The brief proposes the id-form as the v0 starting point.

**Recent log.**

- 2026-05-05 (~01:15): orientation-reset conversation landed. Decision locked: panels-first (B) + authored-vs-derived (D). DECISIONS row #6 closed. LAYER-CONVENTIONS.md updated; 069 authoring brief at `claude-work/to-alan/069-panels-first/`; QUEUE.md #1 replaced. See `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`.
- 2026-05-04 (~22:00): track opened by the orientation-reset research session. SVG inventory across 7 priority pieces (001/002/066/067/069/070/113); four framings on the whiteboard; five questions waiting. `.gitignore` Affinity-lock pattern tacked on (Windows `*.af~lock~`) — see Repo hygiene track. See `sessions/2026-05-04-2200_cowork_orientation-reset-research.md`.

---

## Track: Pendulum folding & grouping POC

```yaml
status: queued
last_updated: 2026-05-04
next_action: In the next cowork session, confirm exact piece IDs for the pendulum bob + arm against source/transcriptions/embedded-labels.md §II.C. Decide whether this is "the first end-to-end piece" per CHARTER §6 #2, or whether a simpler piece earns that slot first.
```

**Hypothesis.** Carried forward from WORKPLAN. A small, mechanically-real two-piece subsystem (pendulum bob + arm) is the right first proof for folding + grouping primitives. Arm folds onto itself (tests F1 + the regions concept directly). Arm glues to bob (tests G1 + G2 via embedded-labels glue references). Both sit in §II.C — also where the function-block sidecar work surfaces, so they double as future mechanism-animation candidates.

**Charter note.** This is the obvious candidate for "first piece end-to-end" (CHARTER §6 #2), but the candidacy isn't locked. Worth a deliberate cowork pass to pick the right first piece.

**Blockers.**

- The face-graph diagnostic ship (preview.html iteration track) — surfaces information that affects whether the pendulum's self-fold is the right first stress test or too much for v0.
- Authored SVGs for the pendulum pieces — they don't exist yet.

**Recent log.**

- 2026-05-03: track opened in WORKPLAN. No work since.

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

*Last updated: 2026-05-05 (late evening) — anchor-pendulum batch panels-first authoring landed across 9 pieces; conventions ratified via DECISIONS #7 (21 specific elements); LAYER-CONVENTIONS.md rewritten as the single canonical reference (LAYERS.md deleted); cross-piece audit script `claude-work/scripts/build_assembly_graph.py` shipped resolving 24/24 cross-piece edges; CODE_PROMPT_preview-html-panels-aware.md drafted ready-for-code. SVG layer authoring track unblocks for the bob pieces + escape wheel batch. preview.html iteration track unblocks for the panels-aware Code session. Source-side capture closed at 123/123 earlier the same day.*

*Earlier 2026-05-05 (morning) — piece capture track: plate B brackets 013-017 resolved as clones of 012 (Alan's clarification: six bracket pieces are all the same drawing). Replicated 012.png → 013/014/015/016/017 (MD5-verified); pieces.csv updated; QUEUE.md #2 narrowed to piece 090 only; lock-file verification (#4) closed (`git ls-files | grep -F "af~lock~"` returned empty). Repo hygiene track: lock-file ask resolved. Source-side capture is now 122/123, pending only 090 (and possibly 110 TBD).*

*Earlier 2026-05-05 (~01:15) — orientation/awareness reset landed (DECISIONS #6 closed: panels-first + authored-vs-derived). Six tracks updated: orientation/awareness model (now executing, waiting on Alan), SVG layer authoring (unblocks for 069), preview.html iteration (snap-only killed; panels-aware parser pathway queued), regions/face-graph design (paused; cut-line-first becomes legacy), charter rollout (the conversation landed; 069 becomes a strong "first end-to-end" candidate), repo hygiene (unchanged). LAYER-CONVENTIONS.md updated co-authored in the same pass; first to-alan/ dropbox entry created at `to-alan/069-panels-first/`.*

*Earlier 2026-05-05 (~00:30) — reconciliation pass against on-disk state. Day-one skeleton confirmed present (Code session that "saw only CHARTER.md" was running in a worktree). Tracks updated for the two sessions that ran after the kickoff drafted its plan: cut-trim ship (PR #14) and orientation-reset research. New "Orientation / awareness model" track opened to hold the four framings + five questions surfaced at 22:00 — that's the live conversation. Charter rollout, SVG layer authoring, preview.html iteration, regions/face-graph design, and repo hygiene all updated. Pre-charter history still lives in WORKPLAN.md.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Eight tracks carried forward from WORKPLAN.md; one (Operations layer) closed; one (Charter rollout) opened.*
