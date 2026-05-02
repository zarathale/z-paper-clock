---
date: 2026-05-02
start_time: "21:00"
end_time: "21:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Diagnose why `preview.html` (post-texture-flip ship) bogs down Chrome and the whole system even when the page is sitting idle, and queue a tight CODE_PROMPT for the smallest fix that resolves the dominant cost.

## What was done

Read the current `preview.html` end-to-end and the most recent code session notes (texture-flip ship at 19:00, cut-layer ship at 16:00, v1a ship at 14:00). Identified the root cause and three surgical fixes; deferred two larger fixes to separate prompts.

**Root cause.** The animation IIFE in `initScene` runs every display frame forever:

```js
(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();
```

There is no gate on whether the camera or scene actually changed. With `antialias: true` and `setPixelRatio(window.devicePixelRatio)` (DPR=2 on Alan's Retina mac), the renderer is doing roughly 4× the visible pixel count of fragment-shader work per frame at 60 Hz on a static textured slab. That's the sustained idle cost. Alan confirmed the symptom is "sustained while idle" via AskUserQuestion.

**Picked three fixes** (matching Alan's "top 2–3 highest-leverage wins" scope answer):

1. **Render-on-demand.** Gate `renderer.render()` behind a `needsRender` flag set on OrbitControls' `change` event and after every scene mutation. `controls.update()` returns truthy while damping is still settling, which preserves the orbit-and-release glide. Idle CPU/GPU should drop to near zero.

2. **Cap pixel ratio at 2.0.** `Math.min(window.devicePixelRatio, 2)`. No-op on Alan's primary Retina display (DPR=2 already); cuts fragment work materially on any external where DPR>2 (some 4K configs, fractional-scaling).

3. **Dispose geometry + materials on rebuild.** Each thickness-slider tick currently leaks ~3 BufferGeometries + 3 MeshStandardMaterials + (worst case) a re-uploaded GPU texture. Folded "stop re-creating the THREE.Texture every rebuild" into the same task via an `_scanTexCacheSrc` identity check on `buildScanTexture`. Also consolidated the duplicated cleanup pass between `renderScene` and `debouncedRebuild` into a single canonical pass at the top of `renderScene`.

**Deliberately deferred** (separate prompts if needed after these three ship and Alan re-measures):

- **Texture downsampling.** The embedded scan PNGs in each SVG are ~600 DPI source quality (a full-bleed piece can be ~2500×4000 px = ~40 MB GPU texture). Resizing to 1024–2048 max dimension before upload would cut texture memory ~4–16×, but it touches the texture pipeline that the texture-flip ship just stabilized. Worth doing only if memory pressure persists after the three picked fixes.
- **`antialias: false`.** Legitimate tradeoff. Defer until after the pixel-ratio cap is measured — the cap alone may be enough.

**Files produced.**

- `CODE_PROMPT_preview-html-perf.md` (new, status `ready-for-code`).

**Files NOT produced.** Did not touch `preview.html` directly per Alan's "Cowork diagnosis writeup + CODE_PROMPT handoff" workflow answer.

## Open questions

None blocking the Code session. After the Code session ships and Alan re-measures, two open questions surface:

1. Does memory pressure remain after the three fixes? If yes → queue texture-downsampling prompt.
2. Does CPU on the GPU process stay near-zero during sustained idle, or is there a residual spike from `controls.update()` itself? If the latter is non-trivial → consider a longer-running idle-detection that pauses the requestAnimationFrame loop entirely after damping fully settles.

## Next-session handoff

1. Code session: read `CODE_PROMPT_preview-html-perf.md` start-to-finish, then implement Tasks 1/2/3 in order. The prompt is self-contained — no further Cowork input required.
2. Branch: `claude/preview-html-perf` (strict naming per CLAUDE.md).
3. Verification is Alan's manual check step using Chrome's Task Manager (Window → Task Manager) — see prompt's Verification Checklist for specific steps and expected before/after.
4. After ship: flip prompt status to `shipped` per the standard convention; this Cowork session note pairs with whatever the Code session writes (e.g. `2026-05-02-HHMM_code_preview-html-perf.md`).
