---
date: 2026-05-10
start_time: "18:18"
end_time: "18:18"
mode: code
participant: Zarathale (Alan)
target: preview-html-closure-derive
orchestration_prompt: CODE_PROMPT_preview-html-closure-derive.md
---

## Goal

Implement derive-one closure folding for piece 066's wrap strip in `preview.html`:
geometrically compute the `fold-tabaa-pane7` angle so the tabaa centroid lands on
the `landing-tabaa` mark in world space whenever pane-strip folds change. Add a
**Lock ⊗** toggle gating the derivation (off by default, no regression for
pieces with no landing mark). Fix the pane-strip Σ readout + Equal button to
target ±360° instead of always +360°, since valley-fold strips close at −360°.

## What was done

- **Task 1:** added module-level `panelSlabMap`, `closureSliderRef`,
  `closureDerivationEnabled` declarations directly after `let pathHingeMap =
  new Map();` (preview.html:656). Mirrored the resets into `teardownBenchScene`
  alongside the existing `pathHingeMap = new Map();` reset (preview.html:1049).
- **Task 2:** populated `panelSlabMap` inside the slab-build loop in
  `renderPanelsFirstScene` (preview.html:5686). Bench mode resets the map at
  the top of the loop; scene mode is opt-out per the prompt (caller resets
  once across pieces).
- **Task 3:** added the `deriveClosureFold()` function just above
  `renderPanelsFirstScene` (preview.html:5630). Walks `parsed.panelsFirst.folds`
  for the closure-classified id, finds the tabaa child via `hingeTree.nodes`,
  grabs the hinge from `pathHingeMap`, finds the landing panel by bbox
  containment of the `landing-tabaa` centroid, resets the hinge to θ=0,
  measures the tabaa centroid in world space, computes the landing-tabaa
  world position via `landingSlab.localToWorld`, projects both onto the plane
  ⊥ world-axis, and computes the signed atan2 angle. Applies the rotation +
  syncs the slider value (and any sibling number input) without re-dispatching
  `input` to avoid a feedback loop.
- **Task 4 (4a):** added a **Lock ⊗** button to the closure group's `ctrlRow`,
  appended right after the master sub-slider for `g === 'closure'`
  (preview.html:~6177). Click toggles `closureDerivationEnabled`, updates
  button text/background, disables + dims `closureSliderRef`, and immediately
  calls `deriveClosureFold()` on enable so the strip jumps to the right pose.
  Captured `closureSliderRef` in the per-member loop for the closure bucket
  (preview.html:~6209). `buildFoldSliderRow` already returned `{ row, slider }`
  (line 6013) — no change needed to the return shape.
- **Task 4 (4b):** replaced the `body.addEventListener('input', updateSum)`
  call with an arrow that fires `updateSum()` then `deriveClosureFold()` when
  the toggle is on (preview.html:~6231). Derivation runs after every pane-
  strip slider change.
- **Task 5 (5a):** Σ readout now picks the nearer of `s − 360` and `s + 360`
  for the diff (preview.html:~6224). Title text updated to "target ≈ ±360°
  (sign follows fold polarity)" (preview.html:~6072).
- **Task 5 (5b):** **Equal (÷±360°)** button measures the current slider mean
  and distributes `sign * 360 / members.length` (sign = −1 if `currentSum <
  −1`, else +1). Defaults to +360° at rest (preview.html:~6101).

## Verification (code-side; commit gate)

1. **`node --check`** — extracted the inline `<script>` body via a 5-line
   Python helper (`/tmp/extract_script.py`); `node --check` on the
   `/tmp/preview_extracted.js` artifact exits 0.
2. **Grep counts** (all match prompt expectations):
   - `let panelSlabMap` → 1
   - `panelSlabMap.set` → 1
   - `function deriveClosureFold` → 1
   - `closureSliderRef = slider` → 1
   - `closureDerivationEnabled.*deriveClosureFold|deriveClosureFold.*closureDerivationEnabled` → 2 (≥1 expected)
   - `Lock ⊗|Unlock ⊗` → 4 (≥2 expected)
   - `buildFoldSliderRow` return — `return { row, slider };` at preview.html:6147 (pre-existing; unchanged)
   - `diffPos|diffNeg` → 3 (≥2 expected)

Browser-side checks (interactive piece-066 load + Lock toggle + drag-pane-slider
+ Save-pose roundtrip + 069-no-landing regression) deferred to Alan post-merge
per the two-tier verification protocol — Code never starts an HTTP server.

## Branch / commit

- Branch: `claude/preview-html-closure-derive` (renamed from auto-generated
  `claude/thirsty-agnesi-d08c0c` per CLAUDE.md before the first commit)
- Commits: see git log on the branch after push.

## Open questions

- The closure hinge's world-axis transformation uses
  `hinge.parent.getWorldQuaternion()` to convert the local axis. If the
  closure hinge sits inside a chain of pane-strip hinges with rotations
  applied (which it does — pane-strip parent panel is rotated via its own
  hinge before the closure hinge sees it), the parent quaternion captures
  that automatically. Worth a visual sanity check on 066 with the strip
  partially closed to confirm the derived angle tracks correctly through
  pane-strip motion.
- The 1° "✓ green" tolerance band in the Σ readout uses
  `Math.abs(diff) > 1`; with the new sign-aware diff this still flips green
  within 1° of either ±360°. No change to band semantics.
- Multi-piece scene mode is unaffected (derivation is Bench-only by the
  `if (!sceneMode) panelSlabMap = new Map();` guard); a scene-mode flavor
  would need per-piece closureSliderRef tracking and is out of scope.

## Next-session handoff

- Alan: pull `main` after merge, open `preview.html?piece=066`, verify the
  9-step browser checklist from the orchestration prompt (now archived at
  `_archive/code-prompts/CODE_PROMPT_preview-html-closure-derive.md`).
- If the derived angle visually drifts as pane-strip sliders move, file a
  follow-up noting which slider configuration broke the world-axis assumption;
  likely fix is to recompute `worldAxis` after `scene.updateMatrixWorld(true)`
  rather than relying on cached parent quaternion at hinge-creation time.
