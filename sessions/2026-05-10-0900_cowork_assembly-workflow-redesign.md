---
date: 2026-05-10
start_time: "09:00"
end_time: "10:28"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Session orientation after a high-velocity morning (PR A + marks-lookup both shipped while
offline); then address assembly workflow friction Alan hit trying to position anchor cluster
pieces in Cluster mode.

## What was done

### Orientation pass

Read STATUS.md, QUEUE.md, last session note (2026-05-09-2230), and live CODE_PROMPTs.
Confirmed state at session start:
- PR A (bench-cluster-foundation) shipped 2026-05-10 00:30 — pending merge
- Parser-marks-lookup shipped 2026-05-10 08:20 — pending merge
- 069 sidecar was the only anchor cluster sidecar in the repo
- 068 fold authoring bug (2-component fold graph) still open
- QUEUE.md stale — Now #1 (tagging) done since 2026-05-07

### STATUS + QUEUE updated

Full STATUS.md refresh: preview.html iteration track (next_action, What's shipped,
Open questions, recent log entries for both today's ships), asset-state track (marks-lookup
graph impact), SVG layer authoring track (LAYER-CONVENTIONS.md drift noted). Footer updated.

QUEUE.md fully rewritten: tagging struck through to Recently shipped; build-graph
split-pieces struck through (done by marks-lookup ship); three new Now entries (merge+visual
check, 068 fold fix, anchor cluster pose capture). PR C cluster-mode and 097 period-suffix
added to Soon. New Recently shipped tail.

### Bridge read confirmed working

Alan ran `python3.12 claude-work/scripts/preview_bridge.py` and pressed the → Claude button
for piece 067. Claude read `claude-work/state/preview-dump.json` directly — first successful
bridge round-trip. No copy-paste.

067 dump analysis: single panel (`main`), no folds, no cutouts, no sidecar. Correct — 067
is a flat anchor frame plate. Its sidecar will be transform-only (no fold state).

### PR C (Cluster mode) finalized and shipped

Reviewed `CODE_PROMPT_preview-html-cluster-mode.md` — body complete but `status: draft`,
`blocked_by` stale, prerequisite about sidecars too strict, transitive cluster lookup not
specified as a task. Fixed all four:
- Cleared `blocked_by`; bumped to `ready-for-code` once Alan confirmed A+B merged
- Relaxed sidecar prereq (069 alone is sufficient; others load at default with banner)
- Added Task 1 transitive edge-walk (seed [067, 069] → full anchor cluster via graph edges)
Alan merged PR C. Cluster mode is now live.

### Assembly workflow redesign — brainstorm and design

Alan hit two blockers in Cluster mode:
1. **Persistence** — every reload loses in-progress transforms (save requires copy-paste JSON hand-merge)
2. **Assembly model wrong** — manual slider dragging can't realistically position pieces that have authored connection constraints. 065+066+067 form a physical unit; you can't dial in 065's position without seeing it relative to 066.

**Design insight:** the connection graph already encodes the assembly constraints (tab-b on
065 meets landing-b65 on 066 — seven such pairs). The viewer should use those constraints to
place pieces, not make the user estimate mm offsets. Assembly should be constraint-based, not
drag-based.

Two CODE_PROMPTs written:

**`CODE_PROMPT_preview-bridge-save.md`** — fixes persistence.
- `/save` endpoint added to `preview_bridge.py`: reads existing sidecar, merges `assembled`
  block, writes back. Preserves all other sidecar fields.
- Save button in preview.html POSTs to `/save`; flashes "Saved ✓". Falls back to copy modal
  if bridge offline.
- Auto-save on piece switch in Bench mode (silent, skips identity poses).

**`CODE_PROMPT_preview-html-snap.md`** — smart snap-to-connection-point.
- Snap mode toggle in Cluster toolbar.
- Click any connection sphere → system looks up partners in connection graph → highlights
  them gold. No manual pair identification.
- Sidebar lists known pairs with [Snap] per row + "Snap all N pairs" button.
- Single-pair snap: translates tab piece so its point meets the landing point exactly
  (convention: landing piece is anchor, tab piece moves).
- Snap-all: median translation across all known pairs between two pieces — more robust
  than single-pair, reports max residual so geometry consistency is visible.
- Lock-together: after snapping, makes tab pieceGroup a child of landing pieceGroup in
  the THREE.js scene graph — moving the landing piece carries the tab piece.
- Green lines confirm snapped pairs; residual readout shows SVG geometry health.
- The system is active: it offers the pairings, user confirms. Never auto-moves without
  explicit [Snap] click.

Both prompts ready-for-code; independent of each other, can go to Code concurrently.

### QUEUE.md second refresh

Now section updated: #1 bridge-save (Code), #2 snap (Code), #3 068 fold fix (bench),
#4 anchor cluster pose capture. Footer updated. PR C added to Recently shipped.

## Design pivot — from manual positioning to constraint-based assembly

This session surfaced a fundamental mismatch between what the tool was built to do and
what the assembly task actually requires. Worth recording as a decision reference.

**What the tool assumed:** Alan positions each piece in Bench mode (one at a time, using
xyz/rotation sliders), saves the transform, and Cluster mode shows them together. The
connection graph is informational — it tells you what connects to what, but you still do
the spatial work manually.

**Why that doesn't work:** 065, 066, and 067 form a physical unit — 066 is a folded wrap
strip, 065 and 067 are the two flat frame plates on either side of it. Seven tab pairs link
065 into 066; the axle runs through 065 and 067. You cannot know where 065 sits in space
until you can see it relative to 066. Trying to eyeball a translation offset in isolation,
with no visual reference, isn't viable — especially at cardstock precision.

The deeper problem: the tool treated assembly as a *display* problem (where should I put
this piece so it looks right?) when it's actually a *constraint* problem (given that tab-b
on 065 inserts into landing-b65 on 066, what is 065's transform?). The second question
has a deterministic answer. The first requires guessing.

**The pivot:** the connection graph is not metadata — it is the assembly specification.
Every valid authored edge encodes a geometric constraint. The viewer's job is to use those
constraints to derive piece positions, not to make the user re-derive them by eye.

**The new model:**
- Snap-to-point replaces slider dragging as the primary assembly gesture.
- The system knows the pairings (from the graph) and offers them; the user confirms.
- "Snap all N pairs" gives the best-fit translation across multiple constraints at once.
- Rigid groups (lock-together) emerge from confirmed snaps, not from manual grouping.
- The connection graph goes from read-only audit data to the active driver of assembly.

This is a pull-forward of M4 thinking into M0.6. The full M4 (arbitrary transform graphs,
rotation alignment, tolerance fitting) is still M4 territory — but the translation snap on
authored tab/landing centroid pairs is tractable now and unblocks everything.

**What this means for the authoring workflow:** fold-state capture (Bench mode, per-piece)
stays the same — Alan dials in fold angles for each piece and saves. Transform capture
changes: instead of guessing offsets in Bench mode, Alan uses Cluster mode snap. The snap
result is saved per-piece as `assembled.transform`, same sidecar shape as before. Nothing
in the data model changes; only the UI gesture changes.

## Open questions

- Anchor cluster pose capture (Now #5 in queue) is now less urgent for the transform side
  — snap will position pieces correctly once it ships. Fold-state sidecars (Bench mode)
  still needed for pieces that fold (069 ✓, 066 needs it).
- 068 fold authoring bug: still pending. 068 won't fold correctly in either Bench or
  Cluster mode until the missing pane→c1 boundary fold is authored in Affinity.
- LAYER-CONVENTIONS.md 066-cluster exemplar table: doc drift from marks-lookup ship. Worth
  a targeted refresh (match types changed from panel-substring to marks-exact/marks-landing-self).
- 097 period-suffix convention: parked in Soon. Worth a Cowork beat before authoring.

## Next-session handoff

1. Send `CODE_PROMPT_preview-bridge-save.md` and `CODE_PROMPT_preview-html-snap.md` to Code
   (can run concurrently).
2. Fix 068 fold authoring (Affinity — add missing pane→c1 boundary fold, re-export).
3. After snap ships: use Cluster mode to snap anchor cluster into assembled position, then
   save sidecars per piece via the direct-write save.
4. Fold-state capture for 066 (Bench mode) — the wrap strip is the only anchor cluster
   piece with meaningful fold geometry to capture.
