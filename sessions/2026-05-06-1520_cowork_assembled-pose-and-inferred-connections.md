---
date: 2026-05-06
start_time: "15:20"
end_time: "16:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Two threads in one session. (1) Review what shipped via PR #17 (multi-piece scene assembly) and discuss where the 3D folding/modeling process actually stands. (2) Drive the conversation to two concrete pieces of infrastructure Alan's instinct surfaced: a place to lock in per-fold assembled poses, and a place to record cross-piece connections that aren't literally printed on the piece.

## What was done

### Discussion phase

Reviewed PR #17 (commit `101f233`, "add scene mode to preview.html for multi-piece assembly"). Confirmed: scene mode shipped, anchor cluster (065/066/067/068/069) places in one scene with 067+069 pivot-aligned via `pivot-anchor` from the connection graph. 405 insertions, 50 deletions, all in `preview.html`. Three procedural slips flagged: branch was auto-named (`claude/romantic-hofstadter-34b4b3`), no session note was written, CODE_PROMPT didn't flip to `shipped`. None of these affect the merged code; all addressed in this session's procedural cleanup.

Surfaced two real gaps in the current state of the build:

1. **Per-fold assembled pose has no durable home.** Today the preview's fold sliders reset to 0 on every load. Alan can scrub to a pose that physically makes sense, but the result evaporates. The `-<deg>` suffix on fold ids is the only existing mechanism, and it's only used as the global slider's target — not as the per-fold initial value.
2. **Learned-but-not-printed connections have no structured home.** The connection graph only sees what's authored as SVG markup. Knowledge from the instructions text or from physical assembly lands in chat, in cheat sheets, or in Alan's head. With 16 panels-first pieces graphed and the gear-train ahead, the gap will widen.

Settled the lane discipline: SVG = originally-authored printed content (Alan's lane). Sidecar (per-piece JSON) = everything learned afterward (Claude's lane on schema). Re-authoring the SVG to capture inferred or assembled-state knowledge is explicitly out — that goes in the sidecar.

### Decisions landed

- **DECISIONS #10 — `connections.inferred[]`.** Per-piece sidecars (`work/pieces/NNN/NNN.json`) gain an optional `connections.inferred[]` array for cross-piece + same-piece relationships not explicitly marked on the printed piece. Each entry mirrors the existing connection-graph edge shape (kind/side/letter/tab/name/partner/panel) plus a mandatory `source` field. `build_assembly_graph.py` merges these alongside SVG-derived edges; every merged edge carries `provenance: "authored" | "inferred"`. Conflict detection on duplicate `(from, to, kind, key)` runs as soft warnings; the script never fails.
- **DECISIONS #11 — `assembled.folds`.** Per-piece sidecars gain an optional `assembled.folds` map of literal SVG fold-id → angle in degrees. The preview reads it on piece load and uses it as the per-fold slider's initial value, applying the rotation immediately so the piece appears in its assembled pose. Precedence: `assembled.folds[id]` > fold-id `-<deg>` suffix > 0. A "Save assembled pose" affordance emits the current slider state as a JSON snippet (copy + download) for Alan to merge into the sidecar by hand — browsers can't write to disk. Inter-piece assembled transforms are deliberately out of scope (M4 work; lives separately, likely on connection-graph edges).

### Files updated

- `claude-work/DECISIONS.md` — rows #10 and #11 added; footer dated 2026-05-06.
- `LAYER-CONVENTIONS.md` (co-authored per DECISIONS #3) — new "Per-piece JSON sidecar" section documenting the existing `function` block (previously undocumented in this file) plus the two new blocks. New "Lane discipline" section codifying SVG-vs-sidecar split. Cross-references and footer updated.
- `claude-work/STATUS.md` — Charter rollout track flipped to reflect CHARTER §6 commitment #2 effectively closed (multi-piece scene shipped) plus the two new CODE_PROMPTs queued. preview.html iteration track updated with PR #17 in the shipped list, two new prompts in the next-action, and a new open-question on inter-piece assembled pose. Footer dated.
- `claude-work/QUEUE.md` — old Now #1 (multi-piece scene) struck through to Recently shipped; new Now #1 (assembled-pose Code session) and Now #2 (inferred-connections Code session). Bob batch + tag-pieces renumbered to #3/#4; Soon section renumbered #5/#6.

### Files created

- `CODE_PROMPT_preview-html-assembled-pose.md` (status: ready-for-code) — preview-side load + save for `assembled.folds`. Implementation breakdown: state plumbing for `currentAssembledFolds`, extension of `maybeLoadSidecar`, ordering flip in `loadPieceById` so the sidecar fetches before SVG render, slider initial-value precedence in `renderPanelsFirstScene`, "Save assembled pose" button + modal with copy + download. Verification matrix covers: regression no-sidecar, sidecar happy-path, save round-trip, Affinity-prefix fold ids (095), malformed sidecar resilience, scene-mode opt-out, R-key reload.
- `CODE_PROMPT_build-assembly-graph-inferred.md` (status: ready-for-code) — audit-side merge of `connections.inferred[]` from sidecars into the graph. Implementation breakdown: `parse_sidecar` + `extract_inferred_connections` helpers, `provenance` tagging on authored edges, merge step (handles attach/landing/hole/pivot/closure/inferred-pivot via parallel `pivot_clusters_provenance` shape so `preview.html`'s existing flat-list reader doesn't break), conflict detection emitting `inferred_warnings`, new markdown sections for inferred edges + conflicts, summary print updated. Verification matrix covers: baseline regression, sidecar happy-path, conflict detection, same-piece closure inferred entry, inferred pivot, malformed sidecar resilience, no preview.html regression.

### Procedural cleanup of PR #17

- `CODE_PROMPT_preview-html-multi-piece-scene.md` front-matter flipped from `ready-for-code` → `shipped` with `shipped: 2026-05-06` and the standard italic header noting state-at-ship-time.
- `sessions/2026-05-06-0847_code_preview-html-multi-piece-scene.md` written as a retroactive session note — assembled from commit `101f233`, the morning's prompt-drafting note, and the diff. Three process slips flagged in its body for future iterations to absorb (auto-named branch, missing session note, missing front-matter flip).

## Open questions

None blocking. The two queued CODE_PROMPTs are independent and either can land first; they touch different files (`claude-work/scripts/build_assembly_graph.py` vs. `preview.html`). Pulling both in sequence over the next bench-time window is the natural path.

A larger open question parked for later: **inter-piece assembled transforms** — where each piece sits in 3D space relative to its partners once folded. Today scene mode does pivot-cluster co-location (one cluster: `anchor`). Per-edge transforms (tab `c` on 70 lands at this SE(3) pose on 71's `landing-c70`) is the M4 work; no decision needed yet. Worth surfacing as its own track once assembled-pose ships per-piece.

Charter rollout track flipped at the §6 commitment #2 line: anchor cluster places end-to-end now, so the literal commitment is met. The richer commitment ("the build looks like the clock") keeps maturing as assembled-fold authoring + inferred-connection authoring + per-edge transforms compose. Track stays active.

## Next-session handoff

**For Alan:** open a Code session, hand it either CODE_PROMPT first (assembled-pose probably has higher per-bench-session ROI since it changes the authoring flow directly). After whichever lands, the other is independently shippable.

**Parallel:** bench-side authoring (Now #3 — bob batch continuation, 087 escape wheel surfacing gear conventions) and tag-pieces (Now #4) are pull-when-ready.

**Sequence convention worth holding to:** flip the relevant CODE_PROMPT's status to `shipped` at end of every Code session, and add the standard italic state-at-ship header. Three slips on the same prompt this week (PR #17) suggest the convention deserves more friction at end-of-session — maybe surface in CHARTER §9 or a checklist somewhere visible.

## Cowork commit message

(See below in two code blocks per CLAUDE.md display convention.)
