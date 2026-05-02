---
date: 2026-05-02
start_time: "15:00"
end_time: "16:00"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Triage v1a rendering bugs across pieces 066, 067, 069, 070; settle the silhouette-source-of-truth convention; produce a ready-for-code prompt for the v1a silhouette fix.

## What was done

### Bugs found in v1a's silhouette extraction

1. **Wrong source of truth (the main bug, surfaced via 067).** v1a's `extractSilhouette` runs marching-squares on the embedded PNG's alpha channel whenever the PNG has any transparency, only falling back to a colored-path heuristic when the PNG is fully opaque. But Alan authors the cut as a vector path inside the SVG body — proven on 067.svg, where the orange-filled `<path>` (`fill:#ff5f40; stroke:#000;`) traces the drawn cut tightly while the PNG alpha is a much looser bounding mask. v1a was silently re-cutting the piece based on alpha, ignoring the authored intent.

   Confirmed visually by rasterizing 067's `<path d="…">` directly onto the PNG: the path coincides with the drawn cut-line throughout. Overlay archived at `work/_diag/067_orangepath_overlay.png`.

2. **Rotation-matrix bug (070).** `parseSVG` reads only `a` and `d` from the `<use>` transform matrix, treating it as `[a 0 tx; 0 d ty]`. 070.svg uses `matrix(0, 4.166667, -4.166667, 0, 20462.5, 0)` — a 90° rotation. v1a's parsing produces `sx=0, sy=0, tx=20462.5, ty=0`, collapsing the silhouette polygon to a single point. The texture UV math also ignores rotation. Affects any piece whose source SVG places the scan with a non-axis-aligned matrix. **Out of scope for the cut-layer fix prompt.** A TODO comment will mark the location; a separate fix prompt covers it later.

3. **Authoring inconsistency across existing pieces (not a v1a bug, surfaced during triage).** 067 has an authored cut path. 069 has only the PNG alpha as a cut source. 066 and 070 have neither named cut layer nor real alpha. Treating "the cut" as one consistent thing requires settling a layer convention.

### Cut-layer convention — settled (initial pass)

Going forward, the cut is authored inside `<g id="silhouette">`. `silhouette` is already the canonical name in CLAUDE.md's File Naming Conventions ("Layered SVG groups"). This is settling existing convention, not inventing.

Path may use `M / m / L / l / H / h / V / v / C / c / Q / q / Z / z`. v1a's existing `parsePathVertices` only handles `M / L / l / m`; the v1a fix prompt extends it.

### Per-element id naming inside the silhouette layer — settled (refinement pass)

Refined later in the same session after Alan authored the new 069.svg and we walked through piece 071's two-cut topology.

Alan's authoring pattern (Affinity → SVG export):

```xml
<g id="silhouette">
  <g>                                        ← Affinity wrapper, parser ignores
    <rect id="mask" x="…" y="…"
          width="…" height="…"
          style="fill:#fa0b0b;"/>             ← visual frame (rect minus cutaway = red border around the piece-shaped hole, via even-odd fill)
    <path id="cutaway" d="M…Z"
          style="fill:#fa0b0b;"/>             ← the silhouette polygon
  </g>
</g>
```

Visually verified on 069.svg: the cutaway path traces the drawn cut tightly across all 26 vertices, including the top closure tab that v1a's alpha-based extractor was getting wrong. Overlay at `work/_diag/069_v2_cutaway_overlay.png`.

**Per-element id convention (signed off by Alan):**

| Layer | Child `id` | Means | Parser action |
|---|---|---|---|
| `silhouette` | `cutaway` | Outer boundary of a single-piece SVG | take as the silhouette polygon |
| `silhouette` | `cutaway-1`, `cutaway-2`, … | Multiple disconnected outer pieces on one SVG | each is a separate slab; v1a-fix renders only the first with a banner |
| `silhouette` | `mask`, `mask-1`, … | Authoring frame | ignored silently |
| `silhouette` | anything else | Unrecognised | ignored with a `console.warn` |
| `cutouts` (sibling layer) | `cutout-1`, `cutout-2`, … | Interior holes (e.g. piece 71's center cell) | reserved; v1a-fix does NOT consume; later fix subtracts from the extrusion |

Numeric suffix (rather than alphabetic) so it scales past 26 and sorts naturally.

**Topology distinction worth being explicit about:**

- `cutaway-N` = "another disconnected outer piece on the same SVG" → becomes its own slab.
- `cutout-N` = "another interior hole inside one outer piece" → becomes a hole subtracted from a slab.

These are not interchangeable; they live in different top-level layers because the renderer treats them differently (extrude vs. subtract). Piece 71 is the canonical multi-cut example: one outer hourglass (`cutaway`) plus one interior square (`cutout-1`). When it gets authored, both layers exist as siblings under the SVG root.

### Path-fallback `skipIds` extension

`extractSilhouettePath()` is the Tier-3 heuristic that picks "the largest closed colored path outside metadata layers" when neither the silhouette layer nor the alpha is available. Once the new convention is in use, the `mask` rect and `cutaway` path inside `<g id="silhouette">` are colored fills that the heuristic would otherwise match. The fix prompt extends the `skipIds` set from `{folds-valley, folds-mountain, axles, marks, root, thickness, Background}` to also include `silhouette` and `cutouts`. Forward-compatible with any future authoring inside either layer.

### Fallback chain during the retro-fit window

Alan retro-fits one piece at a time. v1a should not break on un-retro-fitted pieces, so the fix uses a tiered chain:

1. **Tier 1:** `<g id="silhouette">` if present.
2. **Tier 2:** PNG alpha (legacy; warn banner — "no silhouette layer, falling back to alpha").
3. **Tier 3:** largest closed colored path heuristic (legacy; warn banner).

Each fallback emits a clear yellow banner, and the final-fail case emits an updated red error banner. The `(source: layer | alpha | path-fallback)` tag goes into the silhouette console line so the active tier is obvious in DevTools.

### Diagnostic artifacts produced this session

In `work/_diag/` (untracked / temporary; safe to clean later):

- `069_alpha-mask.png` — the alpha-only silhouette of the original 069.svg.
- `069_alpha-vs-drawing.png` — alpha boundary overlaid on RGB; shows alpha tracks drawing reasonably for the original 069.svg.
- `069_v2_cutaway_overlay.png` — the **new authored cutaway path** (post-convention) overlaid on the PNG. Confirms the cutaway traces the drawn cut tightly, including the top closure tab where v1a's alpha-based extractor previously overshot.
- `067_alpha.png` and `067_overlay.png` — the loose alpha mask v1a was using, overlaid on RGB.
- `067_orangepath_overlay.png` — the **authored cut path** (orange `<path>`) overlaid on the PNG. This is the diagnostic that originally surfaced the source-of-truth bug.
- `070_overlay.png` — alpha-vs-drawing for 070; secondary, the rotation bug dominates.
- `071_source.png` — copy of `source/pieces/071.png`, used to confirm piece 71's two-cut topology (outer hourglass + interior square cutout) when proposing the cutaway/cutout naming distinction.

### Files produced for the next Code session

- `CODE_PROMPT_preview-html-cut-layer.md` (status: ready-for-code) — the v1a silhouette fix.
- This session note.

## Open Questions

- Whether to remove the orange full-viewBox `<rect fill="#ff7b1a">` underneath 067's cut path. Stray paint shape Alan can clean during retro-fit. Doesn't affect the v1a fix.
- Whether `cutouts` consumption (interior holes → ExtrudeGeometry holes) is its own follow-up prompt or rolls into v1b's fold work. Decision deferred — either way, authoring forward-compatibly into `<g id="cutouts">` is fine and won't break.
- Whether per-element transforms ever get applied to silhouette children. Current `shapeToPolygon` ignores them (matches existing v1a assumptions). If Affinity ever exports a transform on a `cutaway-N` path, the helper will need extending.

## Next-session handoff

1. Alan optionally re-authors 067.svg to the convention (orange path → `<path id="cutaway">` inside `<g id="silhouette">`). Strictly optional for the v1a-fix Code session — 069.svg alone is enough to verify Tier 1.
2. Alan optionally re-authors 071.svg now that the cutout convention is settled, even though v1a-fix won't consume the cutout layer yet (forward-compatible).
3. Code session executes `CODE_PROMPT_preview-html-cut-layer.md` against current `inbox/`. Tier 1 verified on 069; Tiers 2/3 verified on 066/070 (and 067 if not re-authored yet).
4. Post-ship, Alan retro-fits 066, 070 silhouette layers at his own pace.
5. Separate fix prompt for the 070 rotation-matrix bug — to be drafted after the cut-layer fix lands.
6. Separate fix prompt for cutouts → ExtrudeGeometry holes — drafted whenever piece 71 (or another cutouts-bearing piece) goes through the pipeline.
