---
date: 2026-05-10
start_time: "16:00"
end_time: "16:21"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Pick up the guided assembly work from the 10:40 session; orient on what shipped during the
day; record the charter amendment for the alan-work/ drift; draft and review the guided
stepper CODE_PROMPT.

## What was done

### Orientation

Read all eight session notes from today. Confirmed both snap (PR #25) and bridge-save
(PR #26) merged. Found two additional commits Alan pushed on top: `4aeecc9` (068 cleanup)
and `53647fc` (save-pose button fix for zero-fold pieces + 067 sidecar created). 067 now
has a sidecar — closes the last blocker before anchor cluster snap can run end-to-end.

### Charter amendment A3

Reviewed `claude-work/CHARTER.md`. Found that `alan-work/` was never created and all piece
authoring continued in `work/pieces/` through and after charter sign-off — consistent with
an in-chat agreement that was never recorded. Alan confirmed. Amendment A3 recorded:
- §4 folder tree: `alan-work/` removed; `work/` unfrozen for piece work
- §4 read/write rules: `work/pieces/` is Alan-writes (af, svg) + Claude-writes (json,
  pipeline outputs)
- §4 rename policy: struck through and retired
- §5 sidecar JSON path: updated from `alan-work/pieces/NNN/NNN.json` →
  `work/pieces/NNN/NNN.json`
- Amendment log A3 added; footer updated. Both sides initialled.

### Design decisions for guided stepper

Retired the 4 design questions sent to Alan earlier in the session — all were architecture
calls per charter §3, Claude's pen. Settled:
- Guided = Cluster mode + stepper layer (already decided in 10:40 session; no new mode)
- Sequence loads via `fetch('claude-work/state/guided_sequence_anchor.json')`
- Completion: auto-advance for `snap-connection` (when `snapAllPairs` fires); explicit
  Done ✓ for all other types including `add-piece`
- Lock-shape confirmation popup text already settled at 10:40

### CODE_PROMPT_preview-html-guided-stepper.md drafted

12 tasks, 636 lines, `ready-for-code` at repo root. Covers:
- Task 1: "Guide" button in `#cluster-controls` topbar
- Task 2: `#guided-panel-section` in `#cluster-panel` (above Measurements)
- Task 3: State variables (`guidedMode`, `guidedSequence`, `guidedStepIndex`)
- Task 4: `loadGuidedSequence(clusterName)` — fetch with cache-bust
- Task 5: `setGuidedMode(on)` — toggle, load, render, apply behavior
- Task 6: Navigation helpers (`currentGuidedStep`, `advanceGuidedStep`,
  `retreatGuidedStep`, `markGuidedStepDone`)
- Task 7: `renderGuidedPanel()` — step card, type-badge color map, piece context
  header ("065 → 066" for snap-connection; "065 + 066" for others), `doneBtn`
  disabled for add-piece when piece not yet in scene
- Task 8: `applyGuidedStepBehavior(step)` — snap-connection activates snap tool;
  fold selects piece; non-snap clears snap mode if active
- Task 9: `highlightGuidedPieces` / `clearGuidedHighlights` — amber emissive on
  current step's `ui.highlight_pieces`; zero-emissive on others
- Task 10: `showGuidedConfirmModal` — promise-based overlay for lock-shape steps
- Task 11: Auto-advance hooks in `snapAllPairs` + `loadClusterPieces`; teardown
  hook in `teardownClusterScene`
- Task 12: Bench-switch cleanup (covered by teardown hook; Code to confirm)

### CODE_PROMPT review — 5 issues found, all fixed

1. **Snap mode sticks on auto-advance** (Bug): else branch in `applyGuidedStepBehavior`
   now calls `setClusterTool('select')` when `clusterInteractionMode === 'snap'`.
2. **`guidedCompleted` Set dead state** (Bug): removed entirely from state vars,
   `loadGuidedSequence`, and `markGuidedStepDone`. Verification check added to assert
   it's absent from the output file.
3. **`doneBtn` unused** (minor): now used — disabled for `add-piece` steps until piece
   is in the scene; tooltip explains why.
4. **`piecesLabel` missing `to_piece`** (minor): snap-connection steps now show
   "065 → 066"; others join with " + ".
5. **`escHtml` note wrong** (clarification): file has `escapeHtml` locally scoped
   inside `showAssembledPoseModal`; not reusable. Clarified: add `escHtml` at module
   scope as specified.

Verification checklist updated: 9 checks total, including new checks for `guidedCompleted`
absence, `escHtml` module-scope definition, and the snap-mode-clear fix.

### STATUS.md + QUEUE.md updated

- STATUS.md: preview.html iteration track `next_action` updated; log entry added.
- QUEUE.md: guided stepper added as Now #1; footer updated (sixth pass).

## Open questions

- **Gap G4** (067↔065/066): 067 now has a sidecar but the SVG connection question is
  unresolved. Once the guided stepper ships and Alan walks through step c-265, the
  physical assembly will surface whether 067 connects directly or only via 069. If
  direct tabs exist, SVG authoring pass + graph regen + insert snap-connection step
  between c-260 and c-270 in the sequence JSON.
- **093a/093b**: Which variant(s) make up the bob braces? Verify against plate G scan
  when the bob cluster comes up in guided mode.
- **pivot_clusters.anchor** still only seeds [067, 069]: after anchor cluster pose
  sidecars are captured for 065/066/068, regenerate connection-graph.json so the full
  five-piece cluster loads via `?cluster=anchor`.

## Next-session handoff

**For Code (immediately):**
Send `CODE_PROMPT_preview-html-guided-stepper.md` to a Code session. It's
`ready-for-code` at repo root; no blockers. Branch name: `claude/preview-html-guided-stepper`.

**For the next Cowork session (after Code ships and Alan does the browser walk-through):**
1. Browser-check the guided stepper per the 10-step manual test in the prompt.
2. Fix 068 fold authoring — missing pane→c1 fold line (see QUEUE Now #2 for console
   diagnostic command).
3. Once 068 is fixed and the guided stepper is live: walk through the anchor cluster
   sequence in Guided mode. Each snap-connection step auto-fires snap; each lock-shape
   step shows the confirmation popup. The goal is to arrive at a fully positioned anchor
   cluster with all five pieces snapped into place and sidecars saved via the bridge.
4. After anchor cluster is positioned: regenerate connection-graph.json, update
   `pivot_clusters.anchor` to the full five-piece membership.
