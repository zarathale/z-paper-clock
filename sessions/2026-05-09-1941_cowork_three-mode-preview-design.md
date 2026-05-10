---
date: 2026-05-09
start_time: "19:00"
end_time: "19:55"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Capture per-piece assembled folds for the pendulum cluster. Surfaced three preview.html issues mid-session that grew into a design conversation; landed DECISIONS #13 (three-mode preview.html + sidecar `assembled.transform`) and drafted three CODE_PROMPTs implementing it. Pose capture itself didn't progress — the design that was blocking it did.

## What was done

**Triage.** Opened the session intending to walk through `assembled.folds` capture for the pendulum cluster (15 pieces, ~47 fold sliders). Started on 071 (square ring, 3 valley folds) as the warmup. Three issues surfaced before any pose was captured:

1. Sliders need text-entry input — drag-only is imprecise.
2. Cutouts in piece 071 don't render as holes — the `<g id="cutouts">` layer is parsed but not consumed (preview.html line 1435 explicitly notes the gap, deferred since 2026-05-02).
3. Pieces load in their authored 2D orientation, which is meaningless in world space — no way to look at a piece and see "this is how it sits in the assembled clock."

The third issue was the substantive one. What started as "add a per-piece transform" evolved through three iterations:

- v1 (initial proposal): per-piece `assembled.transform` block parallel to `assembled.folds`; world coordinate convention; rotation around auto-detected pivot/axle/centroid; preview.html UI with sliders.
- v2 (Alan's hunch): per-piece is canonical, M4 groups derived; RGB world axes as visual reference; click-drag manipulates the piece (camera lock with toggle).
- v3 (Alan's refinement): a wall-with-hook backdrop as physical grounding; two-mode preview.html — single-piece "assembly" mode + multi-piece "orientation" mode.
- v4 (final): three modes, not two. Mode 1 (Bench, single piece) → Mode 2 (Cluster, multi-piece subassembly) → Mode 3 (Wall, multi-subassembly clock composition). Wall is deferred until subassemblies exist to mount. The wall is *only* meaningful when something's being mounted to it.

The three-mode model maps cleanly to:
- The book's hierarchy (each §II.A–§II.F is essentially a subassembly).
- The existing `pivot_clusters` data in `connection-graph.json` (clusters were already a thing; we just hadn't named the workflow tier they correspond to).
- The CLAUDE.md "Assembly model" decision (hierarchical Object3D groups, one per book section). Per-piece poses now compose into clusters compose into the clock.

**DECISIONS.md #13 closed.** Three-mode preview.html (Bench / Cluster / Wall) + sidecar `assembled.transform` for piece pose in cluster-local space. Supersedes #11's "out of scope (deliberately)" speculation about per-edge SE(3) transforms or a top-level `assembled.json` — the actual shape is per-piece in cluster-local frame, not per-edge in world frame. #11's `assembled.folds` block stays exactly as shipped; `transform` sits parallel to it. Frame field (`cluster | world`) auto-detects via `connection-graph.json` `pivot_clusters` membership. Origin auto-detects: `pivot-anchor` mark > `axles[0]` line > authored centroid.

**Three CODE_PROMPTs drafted at repo root.** Honoring Alan's "create a, b, c into separate code prompts" directive (originally said "one combined" earlier in session; revised after seeing the scope split):

- `CODE_PROMPT_preview-html-bench-cluster-foundation.md` — **PR A, status: ready-for-code.** Foundational interaction + cutouts. Cutouts as Shape holes; slider+text-entry pattern (universal); camera-lock-with-toggle; click-drag-on-piece via TransformControls (visual only, no save); RGB axes (origin AxesHelper + corner mini-gizmo); worktable backdrop; Bench/Cluster mode toggle UI scaffold (Bench functional, Cluster stubbed).
- `CODE_PROMPT_preview-html-bench-transform.md` — **PR B, status: draft, blocked_by PR A.** Per-piece transform sliders (3 translation, 3 rotation, all with text-entry); auto-detect origin and cluster frame; sidecar `assembled.transform` read on load; save extension emits `folds` + `transform` together; TransformControls drag ↔ sliders bidirectional. **Pose capture for the pendulum cluster resumes here.**
- `CODE_PROMPT_preview-html-cluster-mode.md` — **PR C, status: draft, blocked_by PR B.** Cluster mode functional (replaces PR A stub); cluster-id load; per-piece selection with outline; selected-piece transform UI; click-to-pin distance readouts between attach/landing points; per-piece save in cluster context; backward-compat for comma-separated scene URLs from PR #17.

PR D (Wall mode + wall+hook geometry + `work/assemblies/<cluster>.json`) is deferred until subassembly authoring is far enough along to make it useful — captured in DECISIONS #13 but no CODE_PROMPT drafted.

**Files touched.**

- `claude-work/DECISIONS.md` — added #13 (substantial entry; supersedes #11's punt on inter-piece transforms).
- `CODE_PROMPT_preview-html-bench-cluster-foundation.md` — NEW (repo root).
- `CODE_PROMPT_preview-html-bench-transform.md` — NEW (repo root).
- `CODE_PROMPT_preview-html-cluster-mode.md` — NEW (repo root).
- `claude-work/STATUS.md` — recent-log entries on charter rollout + preview.html iteration tracks (this session note pass).

## Open questions

- **PR A is ready for Code session.** When Alan has bench time for a Code session, pull PR A. PR B's status flips ready-for-code on PR A's merge; same for PR C → PR B.
- **Pose capture pendulum cluster.** Still queued (12-task list intact). Resumes against PR B's Bench mode once that ships. The original 9 pose-capture tasks (071/070/098/095/094/069/068/066/099) become executable end-to-end at that point. 093a/093b still need fold-path authoring before they can pose-capture (independent track per QUEUE #5).
- **PR A vs combined PR A+B question.** Alan resolved this in-session ("create a, b, c into separate code prompts") — three separate CODE_PROMPTs. Decision recorded in front-matter `blocked_by` chain.
- **LAYER-CONVENTIONS.md "Per-piece JSON sidecar" section** — DECISIONS #13 says "next pass" for the `transform` subsection. Land in a follow-up Cowork pass once PR A's interaction patterns are stable.
- **Wall+hook geometry choices.** Deferred per DECISIONS #13 explicit non-goals. Will surface as design conversation when PR D is drafted (e.g., what "hook" looks like; how the wall bracket pieces 23-26 attach to the wall plane).

## Next-session handoff

If next session is **Cowork**: review the three CODE_PROMPTs in light of any second thoughts; consider promoting LAYER-CONVENTIONS.md's "Per-piece JSON sidecar" section update to active. Or pull a different track (gear-train authoring brief at `claude-work/to-alan/gear-train/` is still alive).

If next session is **Code**: pull `CODE_PROMPT_preview-html-bench-cluster-foundation.md`. Read DECISIONS #13 first. Verify cutouts test target (071 has both `cutout-1` and `cutout-2` in `<g id="cutouts">`). Branch name `claude/preview-html-bench-cluster-foundation`.
