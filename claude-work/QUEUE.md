# QUEUE.md — what Alan should author next

_Pull-based per CHARTER §3 + §9. Alan checks this when there's bench time. Claude maintains the ordering; Alan can reorder or push back. Kept modest in size on purpose — fewer asks, more thinking per ask. When a queue entry ships, it gets struck through here and migrates to the relevant STATUS track's recent log._

---

## Now

### 1. ~~Bridge button in preview.html~~ — shipped 2026-05-10

~~`CODE_PROMPT_preview-bridge-button.md` is at repo root, `ready-for-code`. Small, self-contained, no blockers.~~ Shipped via PR `claude/preview-bridge-button`. The "→ Claude" button now lives in `preview.html` between the sidecar block and the dropzone; pressing it POSTs the current piece's parsed state to `http://localhost:7777/dump/preview` (the bridge server `claude-work/scripts/preview_bridge.py` writes it to `claude-work/state/preview-dump.json`). The page-load ping detects offline state and dims the button. Prompt archived to `_archive/code-prompts/CODE_PROMPT_preview-bridge-button.md`. See `sessions/2026-05-10-0915_code_preview-bridge-button.md`.

### 2. Merge pending PRs + manual visual check on PR A

Two branches are sitting in PRs waiting for review:

- `claude/preview-html-bench-cluster-foundation` (PR A) — cutouts as holes, slider+number-entry, camera lock, TC click-drag, RGB axes + corner gizmo, worktable, Bench/Cluster scaffold.
- `claude/parser-marks-lookup` — marks-aware 8-step cross-piece resolution in `build_assembly_graph.py`; split-piece globbing now included.

After merging PR A, do a quick manual eyes-on in a real browser against piece 071 (`?piece=071`): confirm the two interior holes are visible, the corner gizmo paints and orbits, the TransformControls handles appear, and the worktable shows beneath the piece. The headless Code session couldn't verify the rAF-dependent rendering. See `sessions/2026-05-10-0335_code_preview-html-bench-cluster-foundation.md` §Open questions for the full checklist.

### 2. Fix 068 fold authoring — missing pane→c1 fold line

068's fold graph has two disconnected components: the main pane chain (pane1–pane8, flap1, flap2, taba, tabb, tabff, b, g) and the slot cluster (c1, c2, sidel, sider) are not connected. A fold line is missing on the boundary between the slot panels and the adjacent pane.

To diagnose before opening Affinity: load 068 in preview.html Bench mode and run in the console:
```js
parsed.panelsFirst.folds.filter(f => f.a === 'c1' || f.b === 'c1' || f.a === 'sidel' || f.b === 'sidel')
```
This shows which folds currently touch c1/sidel — confirming the gap. Then add the missing valley/mountain fold line in `068.af` and re-export. The "Disconnected fold components: 2 sub-trees" banner in preview.html should clear.

### 3. Capture anchor cluster pose sidecars (067 → 066 → 065 → 068)

069 sidecar is done (all 10 folds at −90°, transform Y=7.1/rX=99.5, frame cluster/pivot-anchor). The remaining four:

- **067 first** — it's the pivot-anchor reference piece; its transform is the cluster origin. Load in Bench mode, fold to assembled pose, save. Expect frame: cluster, origin: pivot-anchor.
- **066, 065, 068** — in any order after 068's fold bug is fixed. 068 can't be Bench-folded until the two-component issue clears.

Once all five sidecars exist, regenerate `connection-graph.json` (the anchor `pivot_clusters` entry currently only lists [067, 069] — all five need to be there before PR C's cluster-load is testable). Regenerate with: `python3.12 claude-work/scripts/build_assembly_graph.py` from repo root.

---

## Soon (Claude-side work or decision pending)

### 1. PR C finalization (cluster mode) — Cowork then Code

`CODE_PROMPT_preview-html-cluster-mode.md` is at repo root as `status: draft`. It's unblocked on the Code side (PR A + B both shipped) but needs all five anchor cluster sidecars + an updated connection-graph.json before its verification checklist is runnable. Once Now #3 is done, the Cowork step is: confirm the open questions in the prompt are answered, bump status to `ready-for-code`, and hand to Code.

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

*Last updated: 2026-05-10 (third pass) — bridge button shipped. Now #1 struck through; the prompt moved from repo root to `_archive/code-prompts/CODE_PROMPT_preview-bridge-button.md`. preview.html iteration track in STATUS.md gained a 09:15 recent-log entry covering the implementation + verification. The copy-paste console-dump workflow is now replaced — Claude reads `claude-work/state/preview-dump.json` whenever Alan presses the button.*

*Earlier 2026-05-10 (second pass) — bridge button CODE_PROMPT drafted and added as Now #1. Alan requested a one-button workflow to send preview.html face graph / piece state to Claude; bridge server (`claude-work/scripts/preview_bridge.py`) written in Cowork; `CODE_PROMPT_preview-bridge-button.md` ready-for-code at repo root. Replaces the copy-paste console-dump workflow.*

*Earlier 2026-05-10 — Now section fully refreshed. PR A + parser-marks-lookup both shipped today (need merge + PR A visual check). Tagging struck through. Build-graph split-pieces extension struck through (done by marks-lookup ship). Three new Now entries: merge + visual check, 068 fold fix, anchor cluster pose capture. PR C finalization promoted to Soon #1. 097 period-suffix convention and LAYER-CONVENTIONS drift added as Soon #2 + #3.*

*Earlier 2026-05-07 — DECISIONS #4 closed (architecture Option B); struck from Soon #2. `attach-x` clarified: no new convention, rework to `attach-<panel-id><piece>` form; struck from Soon #4.*
