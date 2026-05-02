---
status: shipped
started: 2026-05-02
shipped: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-back-face-mirror
---

_Shipped 2026-05-02; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

## What You Are Doing and Why

After the texture-flip fix shipped (`CODE_PROMPT_preview-html-texture-flip.md`), the front face of every slab in `preview.html` renders right-side-up. Orbiting around to view the slab from −Z surfaced a separate, long-standing bug: the **back face is X-mirrored** relative to the front. On any piece whose silhouette isn't bilaterally symmetric across X (which is most of them — 067 in particular, with the anchor-pivot offset to one side), the back-face cap is rendered as the left-right mirror of the front cap.

Root cause is in `buildSlab`. The back mesh reuses the same `ShapeGeometry` as the front, then is rotated `Math.PI` around Y to point its `FrontSide` normals toward −Z. The rotation flips world-space X — a polygon vertex at world `(X, Y, +T/2)` on the front becomes `(−X, Y, −T/2)` on the back. For symmetric pieces (069 is near-symmetric across X, so it hid the bug for the same reason it hid the texture flip), the result looks fine. For asymmetric pieces it's unmistakable.

Quiet secondary effect of the same bug: the side-wall BufferGeometry builds its bottom edge from the un-flipped polygon at `z=−T/2`, so the back-face cap and the side walls' bottom edge **disagree on XY** for asymmetric pieces. Cream-on-cream blending hides the geometric inconsistency visually, but it's there. Fixing the mirror fixes this in one motion.

Cleanest fix: drop `backMesh.rotation.y = Math.PI` and switch `backMat`'s `side` from `THREE.FrontSide` to `THREE.BackSide`. Same geometry, no rotation, rendered from behind. Two-line change. A larger refactor to `THREE.ExtrudeGeometry` would also work and is the right end-state, but it's already queued under the cutouts → holes follow-up prompt — let that one absorb it.

## Prerequisites — confirm before starting

- The texture-flip prompt (`CODE_PROMPT_preview-html-texture-flip.md`) has shipped to `main`. Confirm: `buildScanTexture` no longer sets `tex.flipY = false`; both `TODO(070)` markers in `parseSVG` are followed by a `TODO(uv-offsets)` line; `extractSilhouetteFromLayer` banners on "no cutaway found, ≥1 unrecognised sibling".
- `inbox/067.svg` is re-authored to the cut-layer convention (rect = `id="mask"`, path = `id="cutaway"`).
- `inbox/069.svg` available as the near-symmetric reference (sanity check that nothing regressed on a piece that didn't visibly trigger the bug).
- No new branch from a prior attempt (`claude/preview-html-back-face-mirror` is clean).
- No version bump — preview-html is pre-viewer; the milestone identifier in this prompt's front matter is the only label.

## Read These Files First

1. `CLAUDE.md` — top sections.
2. `sessions/2026-05-02-1700_cowork_067-svg-id-swap.md` — context for why texture-flip and back-face-mirror were diagnosed in close sequence.
3. `sessions/2026-05-02-HHMM_code_preview-html-texture-flip.md` — what shipped immediately before this prompt.
4. `preview.html` lines ~997–1078 (`buildSlab`) — the fix site. The header comment on line ~1001 needs updating in addition to the code change.

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                              ← update: 3 small edits in buildSlab
├── CODE_PROMPT_preview-html-back-face-mirror.md              ← update: status flips to "shipped" on PR open
└── sessions/
    └── 2026-05-02-HHMM_code_preview-html-back-face-mirror.md ← NEW: ship session note
```

No SVGs touched. No pipeline scripts touched. No v1b work touched.

## Numbered Tasks

### 1. Switch `backMat` to `THREE.BackSide`

Current (around line 1022–1024):

```js
const backMat = new THREE.MeshStandardMaterial({
  color: 0xf0e0c8, side: THREE.FrontSide
});
```

Replace with:

```js
const backMat = new THREE.MeshStandardMaterial({
  color: 0xf0e0c8, side: THREE.BackSide
});
```

`MeshStandardMaterial` with `BackSide` auto-flips the surface normal during shading in three.js's built-in shader, so lighting still reads correctly when the camera is on the −Z side looking at +Z.

### 2. Drop the back-mesh Y-rotation

Current (around lines 1046–1050):

```js
// ── Back face (cream, z = -T/2, rotated to face -Z) ────────────────────────
const bgeo     = new THREE.ShapeGeometry(shape);
const backMesh = new THREE.Mesh(bgeo, backMat);
backMesh.rotation.y = Math.PI;
backMesh.position.z = -T / 2;
```

Replace with:

```js
// ── Back face (cream, z = -T/2, BackSide so it's only visible from -Z) ─────
const bgeo     = new THREE.ShapeGeometry(shape);
const backMesh = new THREE.Mesh(bgeo, backMat);
backMesh.position.z = -T / 2;
```

The rotation is what produced the X-mirror; with BackSide, the geometry stays in the original polygon's XY at `z=−T/2`, matching the side-wall bottom edge exactly.

### 3. Update the `buildSlab` header comment to match

Current (around line 1001):

```js
//   - backMesh:  ShapeGeometry at z=-T/2, cream, FrontSide (rotated to face -Z)
```

Replace with:

```js
//   - backMesh:  ShapeGeometry at z=-T/2, cream, BackSide (visible from -Z, no rotation)
```

The doc-block above `buildSlab` is one of the entry points the v1b prompt reads from; keeping it accurate matters.

## Verification Checklist

1. `preview.html` opens cleanly via `file://`. No console errors at load.
2. Drop `inbox/067.svg`. Front face renders right-side-up (texture-flip fix still effective). Orbit camera around to view from −Z. The cream-colored back-face silhouette outline matches the front-face silhouette outline in shape — same handedness, **not** an X-mirror.
3. Drop `inbox/069.svg`. Same orbit check. Should look correct (was already near-symmetric, so a regression here would mean the new geometry path broke it for symmetric pieces too — a useful negative test).
4. Side walls remain seamless: orbit to a glancing angle and verify there's no visible gap or overhang at the slab's bottom rim where the side walls meet the back face.
5. Thickness slider still rebuilds the slab correctly — drag it; back face shouldn't mirror as the slab thickens or thins.
6. `git diff` against `main` shows changes ONLY in `preview.html` (plus the new session note + this prompt's status flip). No other files touched.

## What NOT to Change

- `buildSlab`'s `THREE.Shape` construction or front-face UV math. Both were settled in the previous two prompts and are correct.
- The side-wall BufferGeometry. Its bottom-edge XY agreed with the polygon all along; this fix simply makes the back-face cap finally agree with it too.
- `frontMesh`'s material or rotation. Front face is unchanged.
- `THREE.ExtrudeGeometry` refactor. That's queued under the cutouts → holes prompt; let it absorb this naturally rather than duplicating the work here.
- The `_scanTexCache` machinery in `buildScanTexture`. Untouched.

## Manual tests

| Pre | Action | Post |
|---|---|---|
| 067 in `inbox/` re-authored to cut-layer | Drop 067.svg into preview.html, orbit to −Z view | Back-face silhouette matches front in handedness; anchor-pivot side of the piece appears on the **same** side as on the front (not mirrored) |
| 069 in `inbox/` | Drop 069.svg, orbit to −Z view | Back face looks correct (was near-symmetric; this confirms no regression) |
| Any piece, default thickness | Orbit at glancing angle through XY plane | No visible gap at slab bottom rim where side walls meet back face |
| Any piece | Drag thickness slider | Slab thickens/thins; back face stays aligned with side walls; no mirror reappears |
