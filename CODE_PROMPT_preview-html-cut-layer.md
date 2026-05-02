---
status: ready-for-code
started: 2026-05-02
owner: Zarathale (Alan)
target: preview-html-cut-layer
---

## What You Are Doing and Why

v1a's silhouette extractor reads the embedded PNG's alpha channel as the cut whenever the PNG has any transparency, and only falls back to a colored-path heuristic when the PNG is fully opaque. In practice the cut is authored as a vector path inside the SVG body — proven on 067.svg, where the orange-filled `<path>` (`fill:#ff5f40; stroke:#000`) traces the drawn cut tightly while the PNG alpha is a much looser mask. v1a is silently re-cutting the piece based on alpha, ignoring the authored intent.

The cut-layer convention was settled in the Cowork session 2026-05-02 (see session note `2026-05-02-1500_cowork_preview-html-cut-layer-spec.md`): going forward, the cut is authored inside `<g id="silhouette">`. `silhouette` is already the canonical layer name in CLAUDE.md's File Naming Conventions, so this is settling existing convention rather than inventing it.

**Per-element id naming inside the silhouette layer (settled with Alan after reviewing his 069.svg authoring pattern and piece 071's two-cut topology):**

| Layer | Child `id` pattern | Meaning | Parser action |
|---|---|---|---|
| `silhouette` | `cutaway` | The outer boundary of a single-piece SVG | take as the silhouette polygon |
| `silhouette` | `cutaway-1`, `cutaway-2`, … | Multiple disconnected outer pieces on one SVG | each is a separate silhouette polygon (multi-slab is a v1b+ concern; v1a-fix renders only the first and warns) |
| `silhouette` | `mask`, `mask-1`, … | Visual frame for authoring (rect-minus-cutaway with even-odd fill) | ignored silently |
| `silhouette` | anything else | unrecognised | ignored with a `console.warn` so typos don't disappear |
| `cutouts` (sibling layer) | `cutout-1`, `cutout-2`, … | Interior holes / windows (e.g. piece 71's center cell) | reserved — v1a-fix does NOT consume; later fix subtracts these from the extrusion |

This prompt rewires `extractSilhouette` to read the silhouette layer first and only fall through to the alpha and path-by-color heuristics when the layer is absent — with a clear banner each time fallback kicks in. The `cutouts` layer is reserved-but-untouched here; once authored, it carries forward forward-compatibly into a later fix.

## Prerequisites — confirm before starting

- `preview.html` exists at repo root and runs cleanly under v1a (commit `d01dfc3`).
- **069.svg in `inbox/` is the canonical Tier-1 test piece** — re-authored 2026-05-02 with `<g id="silhouette">` containing `<rect id="mask">` + `<path id="cutaway">` (Affinity wraps both in an unnamed `<g>`). Visually verified: cutaway path traces the drawn cut tightly (see `work/_diag/069_v2_cutaway_overlay.png`).
- 067.svg may or may not be re-authored yet. If re-authored to the convention (orange path → `<path id="cutaway">` inside `<g id="silhouette">`), it's a second Tier-1 test piece; otherwise it tests the Tier-2 fallback.
- 066.svg and 070.svg still in `inbox/` as legacy SVGs (no silhouette layer) for Tier-2 / Tier-3 fallback-chain testing.
- No version bump (preview-html is pre-viewer; the milestone identifier in this prompt's front matter is the only label).

## Read These Files First

1. `CLAUDE.md` — top sections + "File Naming Conventions" (Layered SVG groups).
2. `sessions/2026-05-02-1400_code_preview-html-v1a.md` — what shipped in v1a.
3. `sessions/2026-05-02-1500_cowork_preview-html-cut-layer-spec.md` — the design discussion that surfaced this fix (banner copy, fallback chain, retro-fit plan).
4. `preview.html` lines 473–569 (`extractSilhouette` + `extractSilhouettePath`) — existing logic.
5. `preview.html` lines 430–450 (`parsePathVertices`) — currently handles only `M / L / l / m`. Needs extension (Task 3).

## Target File Structure Changes

```
z-paper-clock/
├── preview.html                                        ← update: silhouette extraction, parsePathVertices
├── CODE_PROMPT_preview-html-cut-layer.md               ← update: status flips to shipped on PR open
└── sessions/
    └── 2026-05-02-HHMM_code_preview-html-cut-layer.md  ← NEW: ship session note
```

No source SVGs, no pipeline scripts, no v1b work touched.

## Numbered Tasks

### 1. Extend `parsePathVertices` to handle the commands a real silhouette path uses

Current parser handles `M / L / l / m` only. The 067 cut path uses `M l l l c c l l Z`. Box-cut paths in general will hit `H / h / V / v` (horizontal/vertical line shorthand) too. Extend to handle the full minimum set: `M / m / L / l / H / h / V / v / C / c / Q / q / Z / z`.

For `C / c` (cubic) and `Q / q` (quadratic) curves: sample the curve at evenly-spaced t values and emit interior points + endpoint. Use **8 samples for cubics, 6 for quadratics** (enough fidelity for the silhouette while staying cheap). The existing RDP simplification step (already in `extractSilhouette` for the alpha branch — apply the same step to layer-derived polygons in Task 2) will collapse straight runs of samples back down.

For `Z / z`: close the subpath by emitting the start point of the current subpath as the final vertex.

For multi-subpath `d=` strings (multiple `M` commands): the existing parser implicitly concatenates subpaths into one vertex list. **Keep that behavior** — for a closed silhouette there should only be one subpath in practice, and concatenation is harmless if a stray subpath sneaks in.

Add an inline comment explaining the curve-sample density choice.

### 2. Add `extractSilhouetteFromLayer(p)` helper + `shapeToPolygon(el)` helper

Place near `extractSilhouettePath()`. Walks the descendants of `<g id="silhouette">` (recursing through any wrapper `<g>`s that Affinity adds), classifies each leaf shape by `id`, and returns the first cutaway polygon. Multiple cutaways emit a banner and only the first is rendered in v1a-fix; multi-slab support is a v1b+ concern.

```js
// Tier 1 silhouette source: the authored <g id="silhouette"> layer.
// Convention (settled 2026-05-02 after authoring 069.svg + reviewing piece 071):
//   inside <g id="silhouette">:
//     id="cutaway"   or id="cutaway-N"  → silhouette polygon
//     id="mask"      or id="mask-N"     → visual frame, ignored
//     anything else                       → unrecognised, console.warn
//   <g id="cutouts"> is a SIBLING layer (interior holes); v1a-fix does NOT consume it.
//
// Returns array of [vx, vy] in viewBox coords, or null if layer absent / no
// cutaways found.
function extractSilhouetteFromLayer(p) {
  const dom = new DOMParser().parseFromString(p._svgText, 'image/svg+xml');
  const layer = dom.querySelector('g#silhouette');
  if (!layer) return null;

  const cutawayRe = /^cutaway(-\d+)?$/;
  const maskRe    = /^mask(-\d+)?$/;

  const cutaways = [];
  // querySelectorAll('*') returns all element descendants in document order,
  // which transparently handles Affinity's wrapper <g> elements.
  for (const el of layer.querySelectorAll('*')) {
    const tag = el.tagName.toLowerCase();
    if (tag === 'g') continue;  // structural; descendants iterated separately

    const id = el.getAttribute('id') || '';
    if (cutawayRe.test(id)) {
      const poly = shapeToPolygon(el);
      if (poly && poly.length >= 3) {
        cutaways.push({ id, poly });
      } else {
        addBanner(`<g id="silhouette"> #${id} could not be parsed as a closed shape.`, 'warn');
      }
    } else if (maskRe.test(id)) {
      // visual frame, ignore silently
    } else {
      console.warn('[preview.html] <g id="silhouette"> contains <' + tag + '>' +
                   (id ? ' id="' + id + '"' : '') +
                   ' — unrecognised, ignoring. Use id="cutaway" / "cutaway-N" or "mask".');
    }
  }

  if (cutaways.length === 0) return null;

  if (cutaways.length > 1) {
    addBanner(
      `Found ${cutaways.length} cutaways (${cutaways.map(c => c.id).join(', ')}); ` +
      `v1a renders only the first. Multi-slab support is pending.`,
      'warn'
    );
  }

  const chosen = cutaways[0];
  const simplified = rdp(chosen.poly, 1.0);
  console.log('[preview.html] Silhouette: from <g id="silhouette"> #' + chosen.id + ',',
              chosen.poly.length, 'verts →', simplified.length,
              'simplified, area', polyArea(simplified).toFixed(0), 'units²',
              '(source: layer)');
  return simplified;
}

// Convert a leaf shape element to [[vx, vy], ...] in its own local viewBox coords.
// (Per-element transforms are NOT applied — current SVGs don't author them on
// silhouette children; future authoring change would need to extend this.)
function shapeToPolygon(el) {
  const tag = el.tagName.toLowerCase();
  if (tag === 'path') {
    const d = el.getAttribute('d') || '';
    return d ? parsePathVertices(d) : null;
  }
  if (tag === 'polygon') {
    const pts = (el.getAttribute('points') || '').trim().split(/[\s,]+/).map(Number);
    const verts = [];
    for (let i = 0; i + 1 < pts.length; i += 2) verts.push([pts[i], pts[i + 1]]);
    return verts;
  }
  if (tag === 'rect') {
    const x = parseFloat(el.getAttribute('x') || '0');
    const y = parseFloat(el.getAttribute('y') || '0');
    const w = parseFloat(el.getAttribute('width') || '0');
    const h = parseFloat(el.getAttribute('height') || '0');
    if (w > 0 && h > 0) return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
  }
  return null;
}
```

The id-prefix matching is what makes this robust to Alan's authoring pattern: an `<rect id="mask">` and `<path id="cutaway">` can sit as siblings (in any order, inside any wrapper `<g>`), and the parser picks the cutaway by id rather than relying on document order or element type.

### 3. Reorder `extractSilhouette(p)` — layer first, then alpha, then path-by-color

Replace the current entry-point logic in `extractSilhouette` (currently lines ~474–528) with a tiered chain. The existing alpha-extraction body and `extractSilhouettePath()` body **stay intact** — only the routing changes:

```js
async function extractSilhouette(p) {
  // Tier 1: authored <g id="silhouette"> layer (canonical, per CLAUDE.md)
  const fromLayer = extractSilhouetteFromLayer(p);
  if (fromLayer) return fromLayer;

  // Layer is absent or empty — fall through with a clear banner so authoring misses
  // never silently corrupt a render.
  if (p.scanPng) {
    addBanner('No <g id="silhouette"> layer — falling back to PNG alpha mask. ' +
              'Author a silhouette layer to make the cut authoritative.', 'warn');
    // Tier 2: PNG alpha (legacy, less authoritative)
    // ── existing alpha-extraction code, unchanged ──
    // (decode PNG, count opaque, marching-squares at threshold 0.5, scale to viewBox, RDP)
    // If opaque-fraction ≥ 0.99 (no real alpha), fall through to Tier 3 below.
  }

  // Tier 3: largest closed colored path in the SVG body (heuristic)
  addBanner('No <g id="silhouette"> and no usable PNG alpha — falling back to ' +
            'largest colored path heuristic. This may pick the wrong shape.', 'warn');
  return extractSilhouettePath(p);
}
```

Notes:
- Keep the existing `extractSilhouettePath()` body mostly unchanged — its `skipIds` set already excludes metadata layers; it will continue to work as a last-resort heuristic.
- **Add `silhouette` and `cutouts` to that `skipIds` set.** Once the new authoring convention is in use, the silhouette layer's `<rect id="mask">` and `<path id="cutaway">` are colored fills that the path-fallback heuristic would otherwise match. The set should become `{'folds-valley', 'folds-mountain', 'axles', 'marks', 'root', 'thickness', 'Background', 'silhouette', 'cutouts'}`.
- The "no scanPng → path fallback" case in the existing code (`if (!p.scanPng) return extractSilhouettePath(p);`) is now redundant with Tier 3 — drop that line.
- When all three tiers fail, the existing red banner in `extractSilhouettePath` (`'No silhouette found — SVG needs an alpha-bearing scan or a colored silhouette path.'`) needs its copy updated to: `'No silhouette source found — author <g id="silhouette"> with a <path id="cutaway"> (or polygon/rect with id starting "cutaway"), or provide an alpha-bearing scan.'`

### 4. Add a `(source: …)` tag to the existing alpha-branch console line

The Tier-1 helper above already emits `(source: layer)`. Update the alpha-branch's `console.log('[preview.html] Silhouette: raw …')` line to end with `(source: alpha)`, and the `extractSilhouettePath()` line to end with `(source: path-fallback)`. Three consistent tags so the source tier is obvious in DevTools.

### 5. Note the rotation-matrix bug in a comment (do NOT fix)

In `parseSVG`, near both lines that compute `imageScale` (currently ~277 and ~297), if a comment doesn't already exist, add:

```js
// TODO(070): handle rotated/skewed transforms (b ≠ 0 or c ≠ 0).
// Current code only reads sx=a, sy=d, tx=e, ty=f and silently drops rotation.
```

This is documentation only. The fix lives in a separate prompt; out of scope here.

## Verification Checklist

1. `preview.html` opens in a browser without console errors. Drop zone responds to file picks and drag-drops.
2. **Tier 1 — authored layer (canonical case):** drop the current `069.svg` (which has `<rect id="mask">` + `<path id="cutaway">` inside `<g id="silhouette">`, wrapped by an unnamed `<g>`). Render shows the cut tracing the drawn line tightly — top closure tab now agrees with the drawing (no 83 px overshoot). Console: `Silhouette: from <g id="silhouette"> #cutaway, <N> verts → <M> simplified … (source: layer)`. **No yellow or red banners.** The mask is silently ignored.
3. **Tier 1 — Affinity wrapper handling:** the unnamed `<g>` between `silhouette` and the rect+path siblings is transparent to the parser (descendant walk, not child walk). Confirmed by step 2 succeeding without manual unwrapping.
4. **Tier 1 — multi-cutaway warning:** construct or modify a test SVG to have two paths inside `<g id="silhouette">` with `id="cutaway-1"` and `id="cutaway-2"`. Drop it. Yellow banner: `Found 2 cutaways (cutaway-1, cutaway-2); v1a renders only the first. Multi-slab support is pending.` Render shows only the first. Console: `(source: layer)` with `#cutaway-1` in the path.
5. **Tier 1 — unrecognised id:** add a `<path id="experiment" …/>` inside `<g id="silhouette">`. Drop the SVG. The cutaway still renders correctly; DevTools console shows a single `console.warn` line about the unrecognised element. No banner (warn-level only, not user-facing).
6. **Tier 2 — alpha fallback:** drop a 069/067 variant without the silhouette layer (or original pre-2026-05-02 069.svg). Render shows the v1a alpha-based silhouette. Yellow banner: `No <g id="silhouette"> layer — falling back to PNG alpha mask. …`. Console: `(source: alpha)`.
7. **Tier 3 — path-fallback:** drop `066.svg` (fully-opaque PNG, no silhouette layer). Render shows the v1a path-fallback silhouette — and confirm the new `silhouette` / `cutouts` entries in `skipIds` don't break it (they shouldn't; 066 doesn't have those layers). Two yellow warn banners (one per fallthrough). Console: `(source: path-fallback)`.
8. **Empty layer:** construct a test SVG with `<g id="silhouette"></g>` and no scan. Falls through Tier 1 (returns null) → Tier 2 if alpha exists, else Tier 3, else red error banner with the updated copy.
9. **Curve handling:** the 067 authored path (when re-authored to the convention) has two `c` cubic commands. After the parser extension, the simplified vertex count should be ≥ 8 but small. Eyeball the rendered cut against `work/_diag/067_orangepath_overlay.png` — boundaries should agree within a few viewBox units.
10. **Cutouts layer reservation:** if 069.svg gets a `<g id="cutouts"><path id="cutout-1" …/></g>` added (forward-compatible authoring), v1a-fix should ignore it entirely — same render as without cutouts. The `cutouts` entry in `skipIds` ensures the path-fallback won't accidentally pick up cutout paths either.
11. **Thickness slider** still rebuilds geometry from the cached polygon (no re-extraction on slider changes).
12. **Camera framing** still adapts to the (potentially smaller) Tier-1 polygon bbox.
13. `parseSVG` emits the `TODO(070)` comment near both `imageScale` assignments.

## What NOT to Change

- `buildSlab`, `ShapeGeometry`, custom UVs, scan texture pipeline. Cut comes from the new layer; texture mapping is unchanged.
- `parseFoldPath` and the fold-line parsing. v1b will rewire fold rendering; this prompt is silhouette-only.
- **`<g id="cutouts">` consumption.** Reserve in `skipIds` so the path-fallback ignores it, but do NOT extract or render interior holes here. Cutouts → ExtrudeGeometry holes is a separate later fix once silhouette source-of-truth is settled. Forward-compatible: any cutouts authored before that fix lands are simply ignored.
- Multi-slab rendering when more than one cutaway is found. v1a-fix renders only the first cutaway (with a banner). Multi-slab is v1b+.
- The rotation-matrix bug in `parseSVG`'s `imageScale` parsing (the `b ≠ 0, c ≠ 0` case for 070). Document with a TODO comment per Task 5; do not fix here.
- Per-piece pipeline scripts in `work/pipeline/`. Preview-html only.
- Source SVGs in `inbox/` or `source/pieces/`. Alan authors silhouette layers separately.
- `pieces.csv` or any of the gen-2 ingest paths. Unrelated.
- Auto-generated branch name. Use `claude/preview-html-cut-layer` from the first commit (rename if Claude Code starts on an auto-generated name).

## Manual tests

After merge and pull on the mac:

| Pre-condition | Action | Expected |
|---|---|---|
| Current 069.svg (silhouette layer with mask + cutaway) | Drop into preview | Tight cut tracing the drawn line. Top closure tab now agrees. No yellow/red banners. |
| 067.svg re-authored with `<g id="silhouette"><path id="cutaway"…/></g>` | Drop into preview | Tight cut tracing the orange line. No banners. |
| 067.svg without the silhouette layer | Drop into preview | Yellow Tier-2 banner. Loose S-shape (still wrong; expected during retro-fit). |
| 066.svg (fully-opaque PNG, no silhouette layer) | Drop into preview | Two yellow banners. Same path-fallback render as v1a. |
| Hand-crafted SVG with two `cutaway-1` + `cutaway-2` paths inside silhouette | Drop into preview | Yellow banner: `Found 2 cutaways …`. First cutaway rendered. |
| 069.svg with a forward-authored `<g id="cutouts"><path id="cutout-1"…/></g>` | Drop into preview | Identical render to current 069.svg. Cutouts ignored silently. |
| Hand-crafted SVG with empty `<g id="silhouette"></g>` and no scan | Drop into preview | Two yellow warn banners + final red error banner with updated copy. |

End of prompt. Cowork session note for this design discussion: `sessions/2026-05-02-1500_cowork_preview-html-cut-layer-spec.md`.
