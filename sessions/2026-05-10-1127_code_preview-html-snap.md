---
date: 2026-05-10
start_time: "11:27"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: preview-html-snap
orchestration_prompt: CODE_PROMPT_preview-html-snap.md
---

## Goal

Implement smart snap in Cluster mode of `preview.html` per
`CODE_PROMPT_preview-html-snap.md` — graph-driven partner highlighting,
median-translation snap, rigid-group lock, and `assembled.snapped_connections`
in the save payload.

## What was done

All eight tasks in the orchestration prompt landed in `preview.html` on
branch `claude/preview-html-snap` (renamed from the auto-generated
`claude/distracted-bardeen-4e8117` per CLAUDE.md branch-name rule).

- **Task 1** — `makeConnectionSphere` now stamps `userData.type =
  'connection-point'`, `pointKind` (alias of `kind`), and stashes the base
  color + radius so highlight states can be restored cleanly. The legacy
  `userData.connection = true` flag is preserved so the measure-mode hit
  handler keeps working.
- **Task 2** — Snap toggle button added to `#cluster-controls` alongside
  Measure (`[Select] [Measure] [Snap]` mutex). Refactored
  `setMeasureMode` to delegate to a new `setClusterTool(tool)` that owns
  the three-way mutex, brightens spheres on snap activation, dims them off,
  and switches canvas cursor to crosshair while a sphere-targeting tool is
  active. Added `#snap-panel-section` with Zone A (progress), Zone B (active
  snap), Zone C (locked groups), and the snap log.
- **Task 3** — `findPartners(pieceId, rawPointId)` walks `connectionGraph`
  edges, locates "our side" via `edge.raw_id === rawPointId && from ===
  pieceId`, then finds the symmetric partner edge by reversing
  `from`/`to` with the same letter. Critically respects the
  `kind="attach"` → `letter` vs. `kind="landing"` → `tab` asymmetry via
  helper `snapEdgeLetter(edge)`. Edges with no symmetric partner are still
  surfaced (with `partnerEdgeMissing: true`) so the user sees them; the
  [Snap] button on those rows is disabled if the partner sphere isn't in
  the scene. First click colors the source sphere big + base, paints
  partner spheres gold, dims everything else.
- **Task 4** — `refreshSnapPanel()` renders three zones. Progress list
  uses `listClusterConnectionPairs()` (groups edges by piece-pair, dedups
  bidirectional, sorts by piece id) and `pairSnapState()` to pick the dot
  glyph (`○ ◐ ● 🔒`). Active zone shows partners with `matched_via` tag
  per row, a bulk "Snap all N pairs → P" button per direction, and a
  custom-snap row when a non-partner second sphere is clicked. Locked
  zone lists `rigidGroups` with per-group [Unlock] buttons.
- **Task 5** — `snapPair(partner)` resolves the tab + landing spheres,
  translates the tab piece's `pieceGroup` by the world-space delta,
  applies the same delta to any rigid-group siblings, draws a persistent
  green confirmation line, and pushes a record into `snappedPairs`.
- **Task 6** — `snapAllPairs(tab, landing, partners)` computes per-axis
  median translation across all located pair deltas (robust against one
  outlier letter), applies it to the tab piece, and reports per-letter
  residuals. Fires a yellow banner with rotation advice when
  `maxResidual > 1.5 mm`. Each pair is recorded with its individual
  `residual_mm`.
- **Task 7** — `rigidGroups` (array of `Set<pieceId>`) with `lockTogether
  (a, b)` for merge + add semantics. Rigid sync rides on
  `_rigidLastPos` snapshots stored on each pieceGroup's `userData`;
  `syncRigidGroupFromActivePiece` fires from both
  `onTransformControlsChange` and `onTransformSliderInput` so TC drags
  AND slider edits both propagate to siblings. Baselines re-seeded
  after every snap (`snapshotRigidBaselines`) and on cluster load.
- **Task 8** — Cluster-mode save handler now appends
  `assembled.snapped_connections` if any pairs touch the selected piece:
  letter, tab_piece + tab_raw_id, landing_piece + landing_raw_id,
  residual_mm. The "empty save" guard widened to allow saves that
  contain only snapped_connections.

### Other touches

- `teardownClusterScene` now also calls `teardownSnapVisuals()` —
  removes confirmation lines, clears `snappedPairs` + `rigidGroups`,
  and resets snap state. Prevents stale snap state leaking between
  clusters.
- `refreshClusterPanel` extended to update the snap-button active
  class and the canvas cursor for both measure and snap tools.
- Empty-space click in snap mode clears the active snap selection
  (matches the "click another sphere" hint).

## Branch / commit

- Branch: `claude/preview-html-snap`
- Commit: pending at time of session-note write.

## Open questions

1. **Custom-snap entry point** — currently triggered by clicking a
   non-partner sphere after `snapFrom` is set. The CODE_PROMPT also
   suggests offering Snap as an explicit "custom" affordance regardless.
   Today's behavior: if the second click hits a known partner, it
   executes that snap immediately (treating it as a confirmation);
   otherwise it surfaces the custom-snap row. The "second click =
   confirm" shortcut is a small departure from the prompt's spec but
   feels natural enough — flag if Alan dislikes.
2. **Reload pre-populates progress dots** — the save payload now
   carries `snapped_connections`, but cluster-load doesn't yet replay
   that data into `snappedPairs` to mark the progress dots ● on
   reload. The CODE_PROMPT calls this out as a "future session" item;
   not implemented in this PR.
3. **Rotation snap** — out of scope for v1 per CODE_PROMPT § "What
   NOT to Change". Large-residual banner gives the user the
   rotation-needed hint instead.

## Verification

Static-only verification this session:

- `node --check` on the extracted inline `<script>` block (274,126
  bytes, 6,657 lines) — passes.
- Brace balance: 1209 `{` / 1209 `}` — balanced.
- Symbol presence: 158 references to the new snap symbols across the
  file (button id, panel ids, helper functions, state vars). All
  insertions sit in the right scope.

**Browser-side smoke test was NOT run.** The Cowork sandbox can't
bind ports for `python3 -m http.server`; the previously-running
preview server (port 8770) is rooted in a different worktree
(`hungry-leakey-57577b`), so it serves a stale `preview.html`
without these edits. Alan should:

1. Stop the stale `python3 -m http.server 8770` if it's still
   running (or just open a different port from the new worktree
   path).
2. Start `python3 -m http.server 8770` (or 8780 per launch.json)
   from `~/Documents/GitHub/z-paper-clock` on the merged main, then
   open `http://localhost:8770/preview.html?cluster=anchor`.
3. Walk through the 10-step Verification Checklist in
   `CODE_PROMPT_preview-html-snap.md` — particularly steps 2/3 (snap
   all on 067↔069), 4/5 (snap all 7 on 065↔066), 6 (lock-together
   and move via TC), and 8 (save and reload).

## Next-session handoff

After Alan's browser walk-through:

- If everything works as spec'd, this is shipped. Flip
  `CODE_PROMPT_preview-html-snap.md` front matter to `shipped`, add
  `shipped: 2026-05-10`, and move it to `_archive/code-prompts/`
  (per the post-2026-05-06 archive convention).
- If issues surface, capture them in the PR comments and we iterate
  on this branch.
- Loading the saved `snapped_connections` back into `snappedPairs`
  on cluster-load is a clean follow-up: walk every member piece's
  sidecar, push valid entries, refresh the progress panel.
