---
date: 2026-05-02
start_time: "20:00"
end_time: "20:15"
mode: code
participant: Zarathale (Alan)
target: preview-html-back-face-mirror
orchestration_prompt: CODE_PROMPT_preview-html-back-face-mirror.md
---

## Goal

Fix the X-mirrored back face on `buildSlab` slabs in `preview.html`.

## What was done

Two-line change in `preview.html`'s `buildSlab` function:

1. `backMat` — switched `side` from `THREE.FrontSide` to `THREE.BackSide`.
2. `backMesh` — removed `backMesh.rotation.y = Math.PI`.
3. Header comment on line ~1001 updated to match.

Root cause was the Y-rotation that flipped world-space X: a vertex at `(X, Y, +T/2)` on the front became `(−X, Y, −T/2)` on the back, mirroring the entire cap for asymmetric pieces. `BackSide` renders the same geometry from behind without any rotation, so world-space XY is preserved and the back cap aligns with the side-wall bottom edge correctly.

## Branch / commit

Branch: `claude/goofy-ramanujan-9e462b` (worktree branch — PR to be opened against `main`)

Commit: pending (staged and committed by Zarathale after review)

## Open questions

None. The `THREE.ExtrudeGeometry` refactor (which would unify front/back/side into one geometry) remains queued under the cutouts → holes follow-up prompt as intended.

## Next-session handoff

- Verify in browser: drop `inbox/067.svg`, orbit to −Z, confirm back-face silhouette matches front in handedness.
- Drop `inbox/069.svg` as the symmetric regression check.
- Glancing-angle orbit to confirm side walls are flush with back face.
- If clean: commit, push, open PR.
