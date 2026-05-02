---
status: shipped
shipped: 2026-05-02
started: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-perf
---

_Shipped 2026-05-02; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

## What You Are Doing and Why

`preview.html` (v1a + cut-layer + texture-flip ship) functions correctly on every piece tested today, but Chrome consumes a lot of memory and CPU even when the page is sitting idle — Alan reports the entire system bogs down with the page open. This was diagnosed in a Cowork session (`sessions/2026-05-02-2100_cowork_preview-html-perf-diagnosis.md`) as a render-loop problem: the animation IIFE in `initScene` runs `requestAnimationFrame(animate)` → `controls.update()` → `renderer.render(scene, camera)` every display frame forever, regardless of whether anything in the scene or camera changed. With `antialias: true` and `setPixelRatio(window.devicePixelRatio)` (likely 2 on Alan's Retina mac), the GPU is doing roughly 4× the visible pixel count of fragment-shader work per frame at 60 Hz on a textured slab that hasn't moved. That's the bog.

Three surgical changes fix the dominant cost without touching what the viewer renders or how the v1a/cut-layer/texture-flip semantics work. None of them affect the visual output, the parser, or the silhouette tier chain. Pre-emptively narrow scope: this is **not** the prompt for texture downsampling, antialias-off, mipmap tuning, or any v1b work — those are separate prompts if and when they're needed.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly under v1a + cut-layer + texture-flip (i.e. `extractSilhouetteFromLayer` is present, multi-tier silhouette extraction is wired up, `buildScanTexture` does NOT set `tex.flipY = false`).
- `inbox/067.svg`, `inbox/069.svg`, and `inbox/070.svg` are available for verification (re-authored to cut-layer convention as of today).
- No version bump — `preview.html` is pre-viewer; the milestone identifier in this prompt's front matter is the only label.
- No new branch from a prior attempt (`claude/preview-html-perf` is clean).
- macOS Activity Monitor or Chrome's built-in Task Manager (Window → Task Manager) is available to compare before/after CPU and memory.

## Read These Files First

1. `CLAUDE.md` — top sections + "Architectural Decisions" (texture-flip + cut-layer rows).
2. `sessions/2026-05-02-2100_cowork_preview-html-perf-diagnosis.md` — full diagnosis and rationale for the three picked fixes (and what was deliberately deferred).
3. `sessions/2026-05-02-1900_code_preview-html-texture-flip.md` — most recent ship; do not reintroduce `tex.flipY = false`.
4. `preview.html` lines ~94–168 (`initScene` + `onResize` + the animation IIFE) — Task 1 site.
5. `preview.html` lines ~127–131 (the `setPixelRatio` call) — Task 2 site.
6. `preview.html` lines ~936–995 (`renderScene`) and lines ~1083–1096 (`buildScanTexture`) and lines ~1099–1110 (`debouncedRebuild`) — Task 3 sites.

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                      ← update: 3 perf edits (render-on-demand, pixel-ratio cap, dispose-on-rebuild)
├── CODE_PROMPT_preview-html-perf.md                  ← update: status flips to "shipped" on PR open
└── sessions/
    └── 2026-05-02-HHMM_code_preview-html-perf.md     ← NEW: ship session note
```

No SVGs touched. No pipeline scripts touched. No v1b work touched.

## Numbered Tasks

### 1. Render-on-demand

Switch from "render every frame forever" to "render only when something changed." OrbitControls fires a `change` event whenever the camera moves, and `controls.update()` returns truthy while damping is still settling — together they cover every legitimate "render now" trigger. Programmatic scene mutations (file load, thickness rebuild, axle add/remove, resize) get a manual `requestRender()` call.

**Step 1a.** At the top of the script (around line 99, immediately after the existing globals declaration), add the flag and helper:

```js
// ─── Three.js scene globals ───────────────────────────────────────────────────
let renderer, camera, scene, controls;
let currentSlabGroup = null;
let currentAxleMarkers = [];

// Render-on-demand: only call renderer.render() when the scene or camera changed.
// Set true via requestRender() after any scene mutation; OrbitControls' 'change'
// event also flips it. Damping is preserved because controls.update() returns
// truthy while damping is still settling, and that path also triggers a render.
let needsRender = true;
function requestRender() { needsRender = true; }
```

**Step 1b.** In `initScene` (around lines 148–151), wire OrbitControls' `change` event:

```js
controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.addEventListener('change', requestRender);    // NEW
```

**Step 1c.** Replace the animation IIFE at the end of `initScene` (around lines 155–159):

Current:
```js
(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();
```

Replace with:
```js
(function animate() {
  requestAnimationFrame(animate);
  // controls.update() returns true while damping is still settling.
  const damping = controls.update();
  if (needsRender || damping) {
    renderer.render(scene, camera);
    needsRender = false;
  }
})();
```

**Step 1d.** Add `requestRender()` at the end of `onResize` (around line 168):

```js
function onResize() {
  const w = canvasHost.clientWidth;
  const h = canvasHost.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  requestRender();   // NEW
}
```

**Step 1e.** Add `requestRender()` at the end of `renderScene` (after the existing `controls.update();` around line 982 and before the `// Console diagnostics` block):

```js
  controls.target.set(0, 0, 0);
  controls.update();
  requestRender();   // NEW

  // Console diagnostics
  ...
```

**Step 1f.** In `buildScanTexture` (around lines 1083–1096), add an image-load listener so async PNG decode triggers a render. This is essential under render-on-demand: the PNG decode often completes after the first render call, and without an explicit nudge the texture would never appear.

Replace the function body with:

```js
let _scanTexCache = null;
let _scanTexCacheSrc = null;   // NEW: identity of the Image used for the cached texture
function buildScanTexture(scanPng) {
  if (!scanPng) return null;
  // Reuse the cached texture when the same Image is requested (e.g. thickness-slider
  // rebuilds): three.js's GPU upload is one-shot per Texture; re-creating it on every
  // rebuild was wasted work even before render-on-demand.
  if (_scanTexCache && _scanTexCacheSrc === scanPng) return _scanTexCache;
  if (_scanTexCache) { _scanTexCache.dispose(); _scanTexCache = null; }
  const tex = new THREE.Texture(scanPng);
  tex.needsUpdate = true;
  // tex.flipY defaults to true: HTML image row 0 (visual top) lands at UV v=1.
  // buildSlab's front-face UV uses `v = 1 - vy/VB.h`, which puts viewBox-top
  // (vy=0) at UV v=1 — i.e. the visual top of the scan. The two pair correctly
  // only when flipY is left at its default; setting it false here was the v1a
  // texture-flip bug (diagnosed in sessions/2026-05-02-1700_cowork_067-svg-id-swap.md).
  if (!scanPng.complete) {
    // PNG decode hasn't finished yet — under render-on-demand we need an explicit
    // nudge once the image is ready, otherwise the texture would never upload.
    scanPng.addEventListener('load', () => {
      tex.needsUpdate = true;
      requestRender();
    }, { once: true });
  }
  _scanTexCache = tex;
  _scanTexCacheSrc = scanPng;
  return tex;
}
```

The `_scanTexCacheSrc` identity check folds Task 3's "stop re-creating the texture every thickness-slider tick" cleanup into this function — it's the natural place for it.

### 2. Cap pixel ratio at 2

Single-line change in `initScene` (line ~129):

Current:
```js
renderer.setPixelRatio(window.devicePixelRatio);
```

Replace with:
```js
// On Retina macs DPR is already 2; on 4K externals or fractional-scaling configs
// it can be 3+, which makes the fragment shader 2.25× more expensive per frame
// for no perceptible quality gain on a static slab render.
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

No behavioral change on Alan's primary display (DPR=2). Cuts fragment work materially on any external where DPR>2.

### 3. Dispose geometry + materials on rebuild

The current `renderScene` removes `currentSlabGroup` and `currentAxleMarkers` from the scene but never calls `.dispose()` on their geometries or materials. Each thickness-slider tick (debounced to 80ms, but easy to fire 5–10 times during a single drag) leaks ~3 BufferGeometries + 3 MeshStandardMaterials + (pre-Task-1f) a re-uploaded GPU texture. Over a session of fiddling, this compounds.

Also: `debouncedRebuild` does its own scene-remove pass before calling `renderScene`, which itself does the same pass at the top. Consolidate the cleanup into `renderScene` only.

**Step 3a.** Replace the cleanup block at the top of `renderScene` (around lines 938–940):

Current:
```js
async function renderScene(p) {
  // Clear previous slab + axle markers
  if (currentSlabGroup) { scene.remove(currentSlabGroup); currentSlabGroup = null; }
  for (const m of currentAxleMarkers) scene.remove(m);
  currentAxleMarkers = [];
```

Replace with:
```js
async function renderScene(p) {
  // Clear previous slab + axle markers, disposing their GPU resources.
  // The scan texture is cached in _scanTexCache and disposed there; the slab's
  // material references it via `map`, so we don't dispose the texture here —
  // disposing the material is enough to release the JS-side reference.
  if (currentSlabGroup) {
    scene.remove(currentSlabGroup);
    currentSlabGroup.traverse(obj => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    currentSlabGroup = null;
  }
  for (const m of currentAxleMarkers) {
    scene.remove(m);
    if (m.geometry) m.geometry.dispose();
    if (m.material) m.material.dispose();
  }
  currentAxleMarkers = [];
```

**Step 3b.** Simplify `debouncedRebuild` (around lines 1099–1110), since the cleanup now lives entirely in `renderScene`:

Current:
```js
const debouncedRebuild = debounce(() => {
  if (!parsed) return;
  parsed.thicknessMm = parseFloat(thickSlider.value);
  if (currentSlabGroup) {
    scene.remove(currentSlabGroup);
    currentSlabGroup = null;
  }
  for (const m of currentAxleMarkers) scene.remove(m);
  currentAxleMarkers = [];
  // re-render (silhouette already known; rebuild only geometry)
  renderScene(parsed);
}, 80);
```

Replace with:
```js
const debouncedRebuild = debounce(() => {
  if (!parsed) return;
  parsed.thicknessMm = parseFloat(thickSlider.value);
  // renderScene handles slab + axle teardown (with disposal) at the top.
  renderScene(parsed);
}, 80);
```

## Verification Checklist

1. `preview.html` opens cleanly in a browser via `file://`. No console errors at load.
2. **Idle CPU/GPU drops to near-zero.** Open Chrome's Task Manager (Window → Task Manager) and watch the "GPU Process" CPU column. Before this fix: persistent 5–25% on the GPU process even with the page idle. After this fix: drops to near zero within a couple seconds of any motion stopping. The renderer should resume rendering immediately on any orbit / scroll-zoom / right-drag-pan.
3. **Damping still feels right.** Orbit, then release. The camera should still glide to a stop over ~0.5 s (dampingFactor 0.08, ~10–15 frames). It should NOT snap immediately; it should NOT keep rendering forever after settling.
4. **Drop 069.svg.** Front-face scan texture renders right-side-up on first paint (no perceptible delay between geometry appearing and texture appearing — but if there is a brief gap, that's the async PNG decode + load-listener doing its job).
5. **Drop 067.svg, then 070.svg, then back to 069.svg in sequence.** No console warnings about texture leaks; Chrome Task Manager "GPU memory" column should stay roughly flat across the 3 swaps (each new file's texture replaces the previous one cleanly).
6. **Thickness slider exercise.** Drag the thickness slider rapidly back and forth ~20 times. Memory should stay roughly flat after each release (the dispose pass in renderScene reclaims the rebuilt geometry, and the texture is cached not recreated). Before this fix, memory grew with each rebuild.
7. **Hand-modified SVG with a missing scan (e.g. delete the `<image>` data URL).** Should still render the silhouette + axle markers without throwing. The `if (!scanPng) return null;` early-return in `buildScanTexture` covers this.
8. **Resize the browser window.** Camera framing should adjust and a render should fire (Step 1d's `requestRender()` in `onResize`).
9. `git diff` against `main` shows changes ONLY in `preview.html` (plus the new session note + this prompt's front-matter flip). No other files touched.

## What NOT to Change

- The animation IIFE's `requestAnimationFrame` pattern — keep the loop alive and just gate the actual `renderer.render()` call. Some render-on-demand patterns kill the loop entirely, but with damping the loop has to keep running so `controls.update()` can advance the dampened motion.
- `controls.enableDamping` or `controls.dampingFactor` — keep both as-is. They're what produces the smooth orbit-and-release behavior; switching to `enableDamping = false` would also reduce idle work but at a real UX cost.
- `buildScanTexture`'s `tex.flipY` (must remain default `true`) or the comment block above it. The texture-flip ship just stabilized this; do not reintroduce `tex.flipY = false`.
- `buildSlab`'s UV formula or geometry construction. Performance comes from rendering less often, not from rendering different geometry.
- `extractSilhouette` / `extractSilhouetteFromLayer` / `extractSilhouettePath` / the marching-squares + chaining + RDP path. The silhouette pipeline is one-time per file, not a per-frame cost.
- Anti-aliasing (`antialias: true`). Legitimate tradeoff but defer until after pixel-ratio cap is shipped and measured.
- Texture downsampling. The embedded scan PNGs are ~600 DPI source quality and could easily be resized to 1024–2048 max dimension before GPU upload, but that's a separate prompt — touches the texture pipeline that the texture-flip ship just stabilized.
- Any v1b work — fold rendering, polygon-cut algorithm, hinge hierarchy.

## Manual tests

| Pre | Action | Post |
|---|---|---|
| Page open with a piece loaded, idle | Open Chrome Task Manager, watch GPU Process CPU | Drops to near-zero within ~1s of last interaction; resumes immediately on orbit |
| Page open with a piece loaded | Orbit camera, then release | Camera dampens to a stop over ~0.5s; rendering stops thereafter (Task Manager shows GPU process idle) |
| 069 → 067 → 070 → 069 file swaps | Drop each, watch Task Manager "GPU memory" | Roughly flat; no growth across swaps |
| Slab loaded | Drag thickness slider 20× rapidly | Chrome process memory roughly flat after each release; no growth pattern |
| Slab loaded | Resize the browser window (drag corner) | Slab re-frames correctly; render fires on each meaningful size change |
