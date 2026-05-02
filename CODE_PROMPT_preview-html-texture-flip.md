---
status: ready-for-code
started: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-texture-flip
---

## What You Are Doing and Why

`preview.html` (v1a + cut-layer fix) has been rendering the front-face scan texture upside-down on every piece since v1a shipped. The bug was diagnosed in `sessions/2026-05-02-1700_cowork_067-svg-id-swap.md` after re-authoring 067.svg exposed it: 067 is a tall portrait with a strong vertical cue (anchor-pivot + four landing circles clustered in the upper third), and the flip is unmistakable on it. Earlier pieces hid it — 069 is near-square and roughly rotation-symmetric, 066/070 had Tier-2/3 silhouette noise masking everything else, and 071 wasn't textured-checked.

Two pieces of Y-handling don't cancel: `buildScanTexture` sets `tex.flipY = false`, while `buildSlab` already maps viewBox-top to UV-top via `v = 1 - vy / VB.h`. Both push the same direction, so the geometric top of the slab samples the visual bottom of the PNG. The fix is to drop `tex.flipY = false` (default `true`), which makes `UV(u, 1)` sample the visual top — exactly what the existing UV formula was written for. One line removed; UV math unchanged.

Two smaller items get folded into the same prompt because they were flagged in the same session note and they're trivial:

1. The UV math doesn't consult `imageScale` (`sx, sy, tx, ty`) or the `<use>` element's `x`/`y` — it assumes the PNG covers exactly `[0, VB.w] × [0, VB.h]`. True for 069, slightly off (a few px) for 067. Cosmetic, but worth a `TODO` next to the existing `TODO(070)` markers so it surfaces when alignment-precision matters.
2. `extractSilhouetteFromLayer` currently returns `null` silently when `<g id="silhouette">` exists but contains no `cutaway`-id'd child (only mask-id'd or unrecognised-id'd children). That's the exact failure mode 067 hit before re-authoring — the visible render was a full-viewBox slab with no UI indication that the silhouette layer had been authored wrong. Escalate to a yellow banner so authoring slips don't hide.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly under v1a + cut-layer (i.e. `extractSilhouetteFromLayer` is present, multi-tier silhouette extraction is wired up).
- `inbox/067.svg` is re-authored to the cut-layer convention (`<g id="silhouette">` containing `<rect id="mask">` + `<path id="cutaway">`). If 067 still has the swapped-id authoring from earlier today, fix that first or use 069 alone for verification.
- `inbox/069.svg` is the canonical Tier-1 reference — silhouette layer present, near-square aspect, scan texture covers full viewBox.
- No version bump — preview-html is pre-viewer; the milestone identifier in this prompt's front matter is the only label.
- No new branch from a prior attempt (`claude/preview-html-texture-flip` is clean).

## Read These Files First

1. `CLAUDE.md` — top sections + "Architectural Decisions" (cut-layer authoring convention row).
2. `sessions/2026-05-02-1700_cowork_067-svg-id-swap.md` — diagnosis section "Texture is upside-down on every piece" and "Related secondary issue worth flagging in the same fix".
3. `sessions/2026-05-02-1600_code_preview-html-cut-layer.md` — what shipped in cut-layer (Tier 1/2/3 chain, `extractSilhouetteFromLayer` structure).
4. `preview.html` lines ~1011–1074 (`buildSlab` front-face UV loop + `buildScanTexture`) — the actual fix site.
5. `preview.html` lines ~258–305 (the two `TODO(070)` markers + `imageScale` assignments in `parseSVG`) — for Task 2.
6. `preview.html` lines ~566–625 (`extractSilhouetteFromLayer`) — for Task 3.

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                          ← update: 3 small edits (texture flip, UV TODO, silhouette banner)
├── CODE_PROMPT_preview-html-texture-flip.md              ← update: status flips to "shipped" on PR open
└── sessions/
    └── 2026-05-02-HHMM_code_preview-html-texture-flip.md ← NEW: ship session note
```

No SVGs touched. No pipeline scripts touched. No v1b work touched.

## Numbered Tasks

### 1. Drop `tex.flipY = false` in `buildScanTexture`

Current code (around line 1066–1074):

```js
function buildScanTexture(scanPng) {
  if (!scanPng) return null;
  if (_scanTexCache) { _scanTexCache.dispose(); _scanTexCache = null; }
  const tex = new THREE.Texture(scanPng);
  tex.needsUpdate = true;
  tex.flipY = false;  // UV Y already accounted for in the 1-vy/h formula
  _scanTexCache = tex;
  return tex;
}
```

Replace with:

```js
function buildScanTexture(scanPng) {
  if (!scanPng) return null;
  if (_scanTexCache) { _scanTexCache.dispose(); _scanTexCache = null; }
  const tex = new THREE.Texture(scanPng);
  tex.needsUpdate = true;
  // tex.flipY defaults to true: HTML image row 0 (visual top) lands at UV v=1.
  // buildSlab's front-face UV uses `v = 1 - vy/VB.h`, which puts viewBox-top
  // (vy=0) at UV v=1 — i.e. the visual top of the scan. The two pair correctly
  // only when flipY is left at its default; setting it false here was the v1a
  // texture-flip bug (diagnosed in sessions/2026-05-02-1700_…_067-svg-id-swap.md).
  _scanTexCache = tex;
  return tex;
}
```

The behavior change is the deletion of `tex.flipY = false`. The replacement comment is the explanation; pick whatever wording feels right at the keyboard, but don't leave the original "UV Y already accounted for" line — that comment is what made the bug invisible during cut-layer code review.

Do **not** change `buildSlab`'s UV formula. The math at lines ~1019–1022 is correct as written:

```js
const vx = posX / UNITS_PER_MM + bb.cx;
const vy = bb.cy - posY / UNITS_PER_MM;
fuvs[i * 2]     = vx / VB.w;
fuvs[i * 2 + 1] = 1.0 - vy / VB.h;
```

### 2. Add a UV-offsets `TODO` next to each `TODO(070)` marker in `parseSVG`

Two sites in `parseSVG` (around lines 275–280 and 297–302). The current pattern at each:

```js
// TODO(070): handle rotated/skewed transforms (b ≠ 0 or c ≠ 0).
imageScale = { sx: a, sy: d, tx: e || 0, ty: f || 0 };
```

Add a sibling `TODO` line directly below each `TODO(070)`, identically at both sites:

```js
// TODO(070): handle rotated/skewed transforms (b ≠ 0 or c ≠ 0).
// TODO(uv-offsets): account for <use> x/y/width/height and imageScale offsets
// in buildSlab's front-face UVs (currently assumes PNG covers exactly
// [0, VB.w] × [0, VB.h]; ~7px slip on 067, sub-pixel on 069).
imageScale = { sx: a, sy: d, tx: e || 0, ty: f || 0 };
```

No code change at the UV site itself — just the marker, so it surfaces when alignment-precision becomes the active concern.

### 3. Escalate "silhouette layer present, no cutaway found" from silent return to a yellow banner

Current `extractSilhouetteFromLayer` (around lines 577–625) loops `<g id="silhouette">` descendants, classifies each by `id`, and:

- pushes recognised `cutaway`/`cutaway-N` into `cutaways[]`,
- silently ignores `mask`/`mask-N`,
- `console.warn`s on anything else.

When `cutaways.length === 0` it returns `null` and the caller falls through to Tier 2 / Tier 3. That fall-through is right; the silence is wrong. Add a yellow banner before the `return null` so authoring slips like 067's pre-fix state are visible in the UI rather than only in DevTools.

Track whether any unrecognised-id element was seen, then banner if so. The minimal change inside the function:

```js
const cutaways = [];
let unrecognisedCount = 0;  // NEW
for (const el of layer.querySelectorAll('*')) {
  const tag = el.tagName.toLowerCase();
  if (tag === 'g') continue;

  const id = el.getAttribute('id') || '';
  if (cutawayRe.test(id)) {
    // … existing block, unchanged
  } else if (maskRe.test(id)) {
    // ignore silently
  } else {
    unrecognisedCount++;  // NEW
    console.warn('[preview.html] <g id="silhouette"> contains <' + tag + '>' +
                 (id ? ' id="' + id + '"' : '') +
                 ' — unrecognised, ignoring. Use id="cutaway" / "cutaway-N" or "mask".');
  }
}

if (cutaways.length === 0) {
  if (unrecognisedCount > 0) {
    addBanner(
      `<g id="silhouette"> found, but no <path id="cutaway"> inside ` +
      `(${unrecognisedCount} unrecognised element${unrecognisedCount > 1 ? 's' : ''} ignored). ` +
      `Falling through to alpha/path-fallback. Tag the cut polygon id="cutaway".`,
      'warn'
    );
  }
  return null;
}
```

Two important notes:

- The banner only fires when **at least one unrecognised sibling** was present alongside zero cutaways. An entirely empty `<g id="silhouette">` (no children at all) still returns `null` silently — that's not a likely failure mode in practice and doesn't deserve a banner.
- Do NOT remove the per-element `console.warn`. Granular per-id diagnostics in DevTools are still useful when chasing typos; the banner is a visible summary on top.

## Verification Checklist

1. `preview.html` opens cleanly in a browser via `file://`. No console errors at load.
2. Drop `inbox/069.svg`. Front face renders with the scan texture **right-side-up** (visual top of the PNG at the geometric top of the slab). No banner regression — no new yellow/red banners that didn't appear before this fix.
3. Drop `inbox/067.svg` (re-authored cut-layer version). Front face renders right-side-up. Anchor-pivot magenta sphere and landing-circles printed on the scan texture coincide visually (Alan eyeballs).
4. Both `TODO(070)` markers in `parseSVG` are immediately followed by a `TODO(uv-offsets)` line with the comment text from Task 2.
5. To exercise Task 3: take a copy of `inbox/067.svg`, hand-edit the cutaway path's id from `cutaway` back to something unrecognised (e.g. `id="path1"`), drop the modified SVG. Expect a yellow banner reading something like `<g id="silhouette"> found, but no <path id="cutaway"> inside (1 unrecognised element ignored). Falling through to alpha/path-fallback. Tag the cut polygon id="cutaway".` Discard the modified file after the check; do not commit.
6. `git diff` against `main` shows changes ONLY in `preview.html` (plus the new session note + this prompt's front-matter flip). No other files touched.

## What NOT to Change

- `buildSlab`'s UV formula. The `1 - vy / VB.h` line is correct once `tex.flipY` is left at its default; do not "tidy" it.
- `imageScale` consumption at the UV site. The TODO marker is the deliverable here; do not also implement the offset logic — that's a follow-up sized for a piece where the alignment slip becomes visible.
- `extractSilhouetteFromLayer`'s `cutawayRe` / `maskRe` regexes, the `<g>` skip, or the multi-cutaway warning. Only the new `unrecognisedCount` tracking + final banner are in scope.
- Any v1b work — fold rendering, polygon-cut algorithm, hinge hierarchy. `CODE_PROMPT_preview-html-v1b.md` is a separate effort.
- `inbox/*.svg` source files. The grep audit suggested in the session note is a Cowork-side task, deferred.

## Manual tests

| Pre | Action | Post |
|---|---|---|
| 069 in `inbox/` re-authored to cut-layer convention | Drop 069.svg into preview.html | Front-face scan texture renders right-side-up; no new banners; `(source: layer)` in console |
| 067 in `inbox/` re-authored to cut-layer convention | Drop 067.svg into preview.html | Front-face scan texture right-side-up; anchor-pivot + landing circles align; `(source: layer)` in console |
| Hand-modified 067 with cutaway id renamed to `path1` | Drop modified 067.svg | Yellow banner about missing `<path id="cutaway">`; falls through to alpha (Tier 2) |
| Both TODO(070) markers visible in `parseSVG` | `grep -n 'TODO(uv-offsets)' preview.html` | 2 hits, immediately following each TODO(070) |
