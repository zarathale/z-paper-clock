---
date: 2026-05-02
start_time: "22:00"
end_time: "22:30"
mode: code
participant: Zarathale (Alan)
target: preview-html-perf
orchestration_prompt: CODE_PROMPT_preview-html-perf.md
---

## Goal

Apply three surgical performance fixes to `preview.html` to eliminate sustained idle CPU/GPU drain (render loop running every frame even when nothing changed).

## What was done

Implemented all three tasks from `CODE_PROMPT_preview-html-perf.md` in order:

**Task 1 — Render-on-demand (6 sub-steps):**
- Added `needsRender = true` flag + `requestRender()` helper after the globals block.
- Wired `controls.addEventListener('change', requestRender)` so any camera orbit/pan/zoom sets the flag.
- Replaced the unconditional animate IIFE with a gated version: `renderer.render()` only fires when `needsRender || damping` (where `damping` is the truthy return from `controls.update()` while damping is settling — preserves the glide-to-stop UX).
- Added `requestRender()` at end of `onResize` so window resize triggers a render.
- Added `requestRender()` after `controls.update()` in `renderScene` so every programmatic scene rebuild triggers a render.
- Added async `load` event listener in `buildScanTexture` for the case where the PNG hasn't decoded yet by the time `buildScanTexture` is called — fires `requestRender()` once it's ready.

**Task 2 — Pixel ratio cap:**
- Changed `renderer.setPixelRatio(window.devicePixelRatio)` → `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`. No-op on Alan's Retina primary display; cuts fragment work on any external where DPR > 2.

**Task 3 — Dispose geometry + materials on rebuild:**
- Replaced the bare `scene.remove()` teardown at the top of `renderScene` with a `traverse()` pass that calls `.dispose()` on every geometry and material in the outgoing slab group, plus explicit disposal on each axle marker.
- Folded "stop re-creating the THREE.Texture every thickness-slider tick" into `buildScanTexture` via an `_scanTexCacheSrc` identity check — returns the existing cached texture when the same `scanPng` Image is passed again (thickness-slider rebuilds), and only creates a new `THREE.Texture` when a new file is loaded.
- Simplified `debouncedRebuild` by removing its duplicate scene-remove pass (now handled entirely by `renderScene`).

**Files touched:** `preview.html` only (plus this session note and the prompt front-matter flip).

## Branch / commit

Branch: `claude/preview-html-perf`
Commit: see below after push.

## Open questions

Per the diagnosis session note (`2026-05-02-2100_cowork_preview-html-perf-diagnosis.md`), two post-ship questions for Alan to measure:
1. Does memory pressure remain after these fixes? If yes → queue texture-downsampling prompt.
2. Does the GPU process CPU stay near-zero during sustained idle, or is there a residual spike from `controls.update()` itself?

## Next-session handoff

1. Alan verifies with Chrome Task Manager (Window → Task Manager) per the Verification Checklist in the prompt.
2. If both open questions above are "no issue" → move to next viewer milestone.
3. If texture memory pressure persists → queue `CODE_PROMPT_preview-html-texture-downsampling.md`.
