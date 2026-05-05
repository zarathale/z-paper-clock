# LAYERS.md — panels-first authoring cheat sheet

_Concise, just the models. Post-2026-05-05 (panels-first per DECISIONS #6). Pair with `LAYER-CONVENTIONS.md` for the long version + rationale + slip-checks. Keep this open while authoring._

---

## The eight canonical layers (top-level `<g id="...">`)

```
silhouette       outer cut path  (this is what extrudes as the slab)
cutouts          interior holes  (subtracted from the slab)
panels           closed polygon per region of the piece  (NEW — the authoring shift)
folds-valley     dashed-in-print folds  (paper folds toward you)
folds-mountain   plus-sign-in-print folds  (paper folds away from you)
axles            rotation centers  (the wires the piece spins on — narrowed: rotation only)
attach-points    pin-holes, mechanical pivots, tab landings  (NEW — was previously split across axles + marks)
labels           printed text + numerals  (decorative)
marks            construction lines, registration, alignment guides  (narrowed: not landings, not pivots)
```

---

## Per-element ids inside each layer

### silhouette

```
id="cutaway"                    single piece
id="cutaway-1", id="cutaway-2"  multiple disconnected outer pieces (rare)
id="mask", id="mask-N"          visual authoring frame; parser ignores
```

### cutouts

```
id="cutout-1", id="cutout-2"    one per interior hole
```

### panels

```
id="panel-<descriptive>"        e.g. panel-stem, panel-tabA, panel-base
                                — suffixes lowercase, NO HYPHENS
                                  (hyphen is the fold-id delimiter — see folds)
                                — names just need to be unique within the SVG
```

### folds-valley / folds-mountain

```
id="fold-<a>-<b>"               binds the fold to panel-<a> and panel-<b>
                                e.g. fold-stem-tabA   joins panel-stem ↔ panel-tabA
                                — order doesn't matter; parser treats it symmetrically

id="fold-<a>-<b>-<deg>"         optional default angle in degrees
                                e.g. fold-stem-tabA-90
                                — positive = layer's natural direction
                                  (valley = dashed direction; mountain = plus-sign direction)
```

Polarity is the layer the fold lives in. To flip, move the path to the other layer.

### axles

```
unidentified ellipse / circle   the axle marker(s) — no id needed
id="north"                      optional orientation cue:
                                +0° points from active axle (axles[0]) to this marker
                                slider sign: +deg = CW (clock convention) viewed from front
```

### attach-points

```
id="pivot-<name>"               mechanical pivot   e.g. pivot-anchor
id="hole-<letter><piece>"       pin-hole receiving wire/pin from another piece
                                e.g. hole-f70 = "this piece's hole for pin f from piece 70"
id="landing-<tab><piece>"       panel that receives a tab from another piece
                                e.g. landing-c70 = "this piece's landing for tab c from piece 70"
```

The `<piece>` suffix is the bare numeric id (no zero-padding) — matches the in-print notation. Letter-variant pieces format as `landing-a92a`.

### labels

```
no required ids                 printed text/numerals captured for decal rendering
```

### marks

```
no required ids                 construction lines, registration marks, dotted alignment guides
                                — landings moved to attach-points
                                — mechanical pivots moved to attach-points
```

---

## Quick mental model

> **The SVG names what panels ARE, what folds JOIN, and what pieces ATTACH where. The parser doesn't try to derive any of those from geometry.**

If the parser would have to guess, the SVG is missing an id.

---

## Common slips to avoid

- **Hyphens inside panel names.** `panel-tab-a` breaks `fold-tab-a-stem` parsing. Use `panel-tabA`.
- **Landings still in `marks`.** They moved. `landing-c70` lives in `attach-points` now.
- **Pin-holes still in `axles`.** They moved too. `hole-f` lives in `attach-points`.
- **Reversed fold layer names.** Canonical is `folds-valley` and `folds-mountain` (plural-first). `mountain-folds` is wrong.
- **Cut without `-N` suffix on multi-cut pieces.** `cutout` alone is OK for a single hole if the parser tolerates it, but `cutout-1` is the convention. Same for `cutaway-N`.
- **Affinity auto-rename suffixes.** If you see `tab-c1` / `panel-stem1` after export, two layers had the same id and Affinity disambiguated. Fix by renaming the duplicate.

---

*Created 2026-05-05 from the panels-first pivot. See `claude-work/DECISIONS.md` row #6 for the why; `LAYER-CONVENTIONS.md` for the long version.*
