# QUEUE.md — what Alan should author next

_Pull-based per CHARTER §3 + §9. Alan checks this when there's bench time. Claude maintains the ordering; Alan can reorder or push back. Kept modest in size on purpose — fewer asks, more thinking per ask. When a queue entry ships, it gets struck through here and migrates to the relevant STATUS track's recent log._

---

## Now

### 1. ~~Bridge button in preview.html~~ — shipped 2026-05-10

~~`CODE_PROMPT_preview-bridge-button.md` is at repo root, `ready-for-code`. Small, self-contained, no blockers.~~ Shipped via PR `claude/preview-bridge-button`. The "→ Claude" button now lives in `preview.html` between the sidecar block and the dropzone; pressing it POSTs the current piece's parsed state to `http://localhost:7777/dump/preview` (the bridge server `claude-work/scripts/preview_bridge.py` writes it to `claude-work/state/preview-dump.json`). The page-load ping detects offline state and dims the button. Prompt archived to `_archive/code-prompts/CODE_PROMPT_preview-bridge-button.md`. See `sessions/2026-05-10-0915_code_preview-bridge-button.md`.

### ~~2. Direct save via bridge — send to Code (`CODE_PROMPT_preview-bridge-save.md`)~~

→ **Closed 2026-05-10** by the preview-bridge-save ship. `POST /save` endpoint added
to `preview_bridge.py`; bench + cluster save buttons POST `payload.assembled` directly
and fall back to the existing copy modal when the bridge is offline; Bench-mode piece
switch auto-saves the outgoing piece silently. Prompt archived to
`_archive/code-prompts/CODE_PROMPT_preview-bridge-save.md`. See
`sessions/2026-05-10-1546_code_preview-bridge-save.md`.

### ~~3. Snap-to-connection-point in Cluster mode — send to Code (`CODE_PROMPT_preview-html-snap.md`)~~

→ **Closed 2026-05-10** by the preview-html-snap ship. Snap toggle + graph-driven
partner highlighting + snapPair / snapAllPairs (median translation) + rigid-group
lock + `assembled.snapped_connections` save payload all landed. Prompt moved to
`_archive/code-prompts/`. See `sessions/2026-05-10-1127_code_preview-html-snap.md`.

### ~~1. Guided assembly stepper — send to Code (`CODE_PROMPT_preview-html-guided-stepper.md`)~~

→ **Closed 2026-05-10** by the preview-html-guided-stepper ship. "Guide" toggle in cluster
controls, guided panel in `#cluster-panel`, 12-task sequence loader + step card + type badges +
`applyGuidedStepBehavior` + amber highlight + lock-shape modal + auto-advance hooks in
`snapAllPairs` / `loadClusterPieces`. Prompt archived to `_archive/code-prompts/`.
See sessions for the code ship and the 16:00 Cowork design session.

### 1. Fold panel group-aware redesign — send to Code (`CODE_PROMPT_preview-html-fold-groups.md`)

`CODE_PROMPT_preview-html-fold-groups.md` is at repo root, `ready-for-code`. Adds automatic
fold-group detection and grouped rendering to the Bench-mode fold slider panel. Groups detected
from fold id naming patterns: **pane-strip** (sum readout + Equal/Flat buttons), **closure**
(master sub-slider), **tab-flap** (master sub-slider + Flat/90° buttons), **cross-piece**
(collapsible, starts collapsed). Pieces with no recognised patterns fall back to flat rendering
— no regression. Driving use case: piece 066 (22 folds across four groups).

No blockers. No SVG authoring prereqs — pure preview.html JS/CSS change.

### 2. Fix 068 fold authoring — missing pane→c1 fold line

068's fold graph has two disconnected components: the main pane chain (pane1–pane8, flap1, flap2, taba, tabb, tabff, b, g) and the slot cluster (c1, c2, sidel, sider) are not connected. A fold line is missing on the boundary between the slot panels and the adjacent pane.

To diagnose before opening Affinity: load 068 in preview.html Bench mode and run in the console:
```js
parsed.panelsFirst.folds.filter(f => f.a === 'c1' || f.b === 'c1' || f.a === 'sidel' || f.b === 'sidel')
```
This shows which folds currently touch c1/sidel — confirming the gap. Then add the missing valley/mountain fold line in `068.af` and re-export. The "Disconnected fold components: 2 sub-trees" banner in preview.html should clear.

### 5. Capture anchor cluster pose sidecars (067 → 066 → 065 → 068)

069 sidecar is done (all 10 folds at −90°, transform Y=7.1/rX=99.5, frame cluster/pivot-anchor). The remaining four:

- **067 first** — it's the pivot-anchor reference piece; its transform is the cluster origin. Load in Bench mode, fold to assembled pose, save. Expect frame: cluster, origin: pivot-anchor.
- **066, 065, 068** — in any order after 068's fold bug is fixed. 068 can't be Bench-folded until the two-component issue clears.

Once all five sidecars exist, regenerate `connection-graph.json` (the anchor `pivot_clusters` entry currently only lists [067, 069] — all five need to be there before PR C's cluster-load is testable). Regenerate with: `python3.12 claude-work/scripts/build_assembly_graph.py` from repo root.

---

## Soon (Claude-side work or decision pending)

### 1. Cluster-pose authoring loop (post-PR-C) — Alan

PR C (preview-html-cluster-mode) shipped 2026-05-10 — `_archive/code-prompts/CODE_PROMPT_preview-html-cluster-mode.md` is the decision record. The cluster-mode authoring loop is now the next-up Alan-side task: load Cluster → `anchor`, manually adjust 065/066/067/068's transforms (only 069 has a saved sidecar), Save selected piece → merge each JSON snippet by hand → reload to confirm. Distance readouts between authored attach/landing pairs guide the alignment. After all five anchor sidecars land, regenerate connection-graph.json so `pivot_clusters.anchor` reflects the full transitive membership (currently still seeded `[067, 069]`).

### 2. 097 period-suffix convention — Cowork beat

`attach-a99.{1..5}` Affinity collision pattern: the marks-lookup session note flags this as worth a Cowork conversation before committing to a new suffix convention. The multi-instance `marks-exact-multi` resolution may already handle the ambiguity (097→099 now resolves to `a (×12)` cleanly). Decide: do we need a new authoring convention for multi-instance attach disambiguation, or does the current behavior suffice? Not blocking anything actively.

### 3. LAYER-CONVENTIONS.md doc refresh — Cowork

The 066-cluster exemplar table in LAYER-CONVENTIONS.md still describes some edges as `panel-substring` where the actual match type is now `marks-landing-self` or `marks-exact` after the 2026-05-10 marks-lookup ship. Worth a targeted refresh so the table doesn't mislead anyone authoring new pieces.

### 4. 093a / 093b fold paths + 093b attach rework (bench authoring)

Two related items deferred until the next anchor/pendulum/bob touch-up pass:
- Both halves have `panels` scaffolding but no fold paths yet — the bob brace can't fold in preview.html until valley/mountain folds are authored.
- 093b's `attach-x093a` uses an invented `x` that doesn't resolve on 093a. The fix: place a small mark on 093a at the joint edge (e.g. `id="joint"`), then rework 093b to `attach-joint093a`. See LAYER-CONVENTIONS.md "Mark-first attach pattern."

Pure bench work; no Code prereq.

### 5. Audit-v2 + dashboard CODE_PROMPT (Cowork drafts; Code ships)

Post-tagging follow-on: merge `character` + `subtype` from `work/piece_characters_v2.yaml` into `pieces.csv`; author `expected_layers.yaml` v1 keyed by character; draft `CODE_PROMPT_dashboard-and-audit-v2.md`. Per CHARTER §5, audit script + dashboard land under `claude-work/` rather than evolving `work/scripts/audit_state.py` in place.

### ~~2. Architecture call: preview.html ↔ work/viewer/ (DECISIONS #4, Cowork)~~

→ **Closed 2026-05-07.** Option B locked in: `preview.html` stays as the permanent authoring/QA tool; `claude-work/viewer/` built fresh (TypeScript + Vite) when M3 is imminent. See DECISIONS #4.

### ~~4. `attach-x<piece-id>` convention formalization (Cowork)~~

→ **Clarified 2026-05-07 — no new convention needed; mark-first pattern documented.** See LAYER-CONVENTIONS.md "Mark-first attach pattern."

### ~~6. Build-graph script: support split pieces (093a/093b)~~

→ **Closed 2026-05-10** by the parser-marks-lookup ship. `build_assembly_graph.py` now globs `*.svg` per piece directory and derives piece id from the filename stem — 093a + 093b are in the graph. See `sessions/2026-05-10-0820_code_parser-marks-lookup.md`.

---

## Recently shipped

- ~~**Direct sidecar save via bridge**~~ → `claude/preview-bridge-save`, 2026-05-10. `POST /save` on `preview_bridge.py` merges `{piece, assembled}` into `work/pieces/NNN/<id>.json`, preserving other top-level fields. Bench + cluster save buttons POST directly with copy-modal fallback when the bridge is offline. Bench-mode piece switch auto-saves the outgoing piece silently. See `sessions/2026-05-10-1546_code_preview-bridge-save.md`.
- ~~**Snap-to-connection-point in Cluster mode**~~ → `claude/preview-html-snap`, 2026-05-10. Snap tool added to Cluster mode (Select/Measure/Snap mutex). Click a sphere → graph-driven partner lookup highlights partners gold; [Snap] / [Snap all] translates tab piece to landing (median per-axis translation for "snap all"); large-residual yellow banner; rigid-group lock; persistent green confirmation lines; `assembled.snapped_connections` recorded in save payload. See `sessions/2026-05-10-1127_code_preview-html-snap.md`.
- ~~**Parser-marks-lookup (DECISIONS #12)**~~ → `claude/parser-marks-lookup`, 2026-05-10. 8-step marks-aware cross-piece resolution in `build_assembly_graph.py`; split-piece globbing. Graph now at 30 valid authored edges; 093b→093a resolves; 094→095 and 097→099 shift to mark-anchored. See `sessions/2026-05-10-0820_code_parser-marks-lookup.md`.
- ~~**PR A — foundational interaction + cutouts (DECISIONS #13)**~~ → `claude/preview-html-bench-cluster-foundation`, 2026-05-10. Cutouts as Shape holes, slider+number-entry, camera lock, TC click-drag, RGB axes + corner gizmo, worktable, Bench/Cluster scaffold. See `sessions/2026-05-10-0335_code_preview-html-bench-cluster-foundation.md`.
- ~~**PR B — Bench mode transform capture (DECISIONS #13)**~~ → `claude/preview-html-bench-transform`, 2026-05-09. Transform panel, sidecar `assembled.transform` read+write, TC↔slider sync. See `sessions/2026-05-09-2219_code_preview-html-bench-transform.md`.
- ~~**Tag 123 pieces in tag-pieces.html**~~ → 2026-05-07. All 124 pieces tagged in `work/piece_characters_v2.yaml`. See `sessions/2026-05-07-1030_cowork_piece-characters-v2-cleanup.md`.
- ~~**Per-fold assembled-pose load + save in preview.html**~~ → PR #19, 2026-05-06. See `sessions/2026-05-06-1900_code_preview-html-assembled-pose.md`.
- ~~**Inferred cross-piece connections in the audit**~~ → PR #18, 2026-05-06. See `sessions/2026-05-06-1700_code_build-assembly-graph-inferred.md`.

---

## Conventions for this file

- **Format:** numbered entries with a 1-paragraph "what / why next / how to pull."
- **Order:** most-actionable first. Items that need Claude conversation before they can be pulled go in "Soon," not "Now."
- **Modesty:** keep "Now" to 3–5 entries. Pulling everything onto the queue at once defeats the iteration discipline (CHARTER §9).
- **Throughput floor:** none. Pull-based — when bench time happens, it happens.
- **Strikethrough on ship:** when something ships, strike the entry through and add a one-liner pointing at the session note. Periodically clean ship'd entries when they go stale enough to clutter.
- **Recently shipped:** keep a short tail of recent ships at the bottom for context. Trim aggressively once they're more than ~3 sessions old.

---

*Last updated: 2026-05-10 (seventh pass) — guided stepper shipped; Now #1 struck through. Fold panel group-aware redesign added as new Now #1: `CODE_PROMPT_preview-html-fold-groups.md` ready-for-code at repo root. Groups: pane-strip (sum readout + Equal), closure (master slider), tab-flap (master slider + 90° quick-set), cross-piece (collapsed by default). Driving use case: piece 066 (22 folds). No SVG authoring prereqs; pure preview.html change.*

*Earlier 2026-05-10 (sixth pass) — guided stepper CODE_PROMPT drafted, added as Now #1. `CODE_PROMPT_preview-html-guided-stepper.md` ready-for-code at repo root. 12 tasks: Guide toggle, guided panel, sequence loader, step card + type badges, step behavior dispatch, piece highlighting, lock-shape modal, auto-advance hooks. Charter amendment A3 recorded (alan-work/ retired; work/pieces/ canonical).*

*Earlier 2026-05-10 (fifth pass) — preview-bridge-save shipped. Now #2 struck through; the prompt moved from repo root to `_archive/code-prompts/CODE_PROMPT_preview-bridge-save.md`. Save buttons now POST directly to the bridge → copy-paste sidecar merge eliminated; copy modal preserved as offline fallback; Bench-mode piece switch auto-saves the outgoing piece. Recently shipped tail bumped.*

*Earlier 2026-05-10 (fourth pass) — two new CODE_PROMPTs drafted after Alan flagged assembly workflow as a blocker: `CODE_PROMPT_preview-bridge-save.md` (direct sidecar save, fixes persistence) and `CODE_PROMPT_preview-html-snap.md` (smart snap with auto-partner detection from connection graph, snap-all median translation, rigid group lock). Both ready-for-code; can go to Code concurrently. Now renumbered to 1–5; PR C cluster-mode added to Recently shipped.*

*Earlier 2026-05-10 (third pass) — bridge button shipped. Now #1 struck through; the prompt moved from repo root to `_archive/code-prompts/CODE_PROMPT_preview-bridge-button.md`. The copy-paste console-dump workflow replaced — Claude reads `claude-work/state/preview-dump.json` whenever Alan presses the button.*

*Earlier 2026-05-10 (second pass) — bridge button CODE_PROMPT drafted and added as Now #1. Alan requested a one-button workflow to send preview.html face graph / piece state to Claude; bridge server (`claude-work/scripts/preview_bridge.py`) written in Cowork; `CODE_PROMPT_preview-bridge-button.md` ready-for-code at repo root. Replaces the copy-paste console-dump workflow.*

*Earlier 2026-05-10 — Now section fully refreshed. PR A + parser-marks-lookup both shipped today (need merge + PR A visual check). Tagging struck through. Build-graph split-pieces extension struck through (done by marks-lookup ship). Three new Now entries: merge + visual check, 068 fold fix, anchor cluster pose capture. PR C finalization promoted to Soon #1. 097 period-suffix convention and LAYER-CONVENTIONS drift added as Soon #2 + #3.*

*Earlier 2026-05-07 — DECISIONS #4 closed (architecture Option B); struck from Soon #2. `attach-x` clarified: no new convention, rework to `attach-<panel-id><piece>` form; struck from Soon #4.*
