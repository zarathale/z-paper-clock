---
date: 2026-05-02
start_time: "19:00"
end_time: "19:30"
mode: code
participant: Zarathale (Alan)
target: preview-html-texture-flip
orchestration_prompt: CODE_PROMPT_preview-html-texture-flip.md
---

## Goal

Fix the v1a texture-flip bug in `preview.html`: front-face scan textures were rendering upside-down on every piece because `tex.flipY = false` and the `1 - vy/VB.h` UV formula both pushed Y in the same direction. Also: add `TODO(uv-offsets)` markers and escalate the "silhouette layer present, no cutaway found" case from a silent return to a yellow banner.

## What was done

Three changes to `preview.html`, all scoped per `CODE_PROMPT_preview-html-texture-flip.md`:

**Task 1 — Drop `tex.flipY = false` in `buildScanTexture` (line ~1089).**
Removed the explicit `tex.flipY = false` and replaced the stale comment with the accurate explanation. With `flipY` at its default (`true`), HTML image row 0 (visual top) lands at UV v=1, which pairs correctly with the existing `v = 1 - vy/VB.h` formula. The formula itself is unchanged. The old comment ("UV Y already accounted for in the 1-vy/h formula") was what made the bug invisible during v1a code review — replaced.

**Task 2 — Add `TODO(uv-offsets)` at both `TODO(070)` sites (lines 279, 304).**
Both `imageScale` assignment sites in `parseSVG` now carry a sibling `TODO(uv-offsets)` comment noting that the front-face UV formula assumes the PNG covers exactly `[0, VB.w] × [0, VB.h]` (~7px slip on 067, sub-pixel on 069). No code change — marker only, to surface when alignment-precision matters.

**Task 3 — Yellow banner when silhouette layer present but no cutaway found (lines 592–626).**
Added `unrecognisedCount` tracking inside `extractSilhouetteFromLayer`. When `cutaways.length === 0` and at least one unrecognised-id sibling was seen, fires `addBanner('warn', …)` before returning `null`. Per-element `console.warn`s preserved. An entirely empty `<g id="silhouette">` (no children) still returns `null` silently — only the "something is there but wrong id" case gets the banner.

## Branch / Commit

Branch: `claude/preview-html-texture-flip`
Commit: (see git log after push)

## Open Questions

None from this session. Verification (069 right-side-up, 067 anchor-pivot alignment, Task-3 banner exercise) is Alan's manual check step per the prompt's verification checklist.

## Next-session handoff

1. Alan drops `inbox/069.svg` into preview.html — confirm front-face texture is right-side-up, no new banners.
2. Alan drops `inbox/067.svg` — confirm anchor-pivot + landing circles align on the front face.
3. Optional: hand-edit a copy of 067 to rename cutaway id → `path1`, drop into preview — confirm yellow banner fires.
4. After verification, merge PR and run post-merge cleanup.
5. Next queued work: 070 rotation-matrix bug and cutouts → ExtrudeGeometry holes (separate prompts).
