# LAYER-CONVENTIONS.md — panels-first authoring reference

_The authoritative reference for SVG authoring conventions on z-paper-clock per-piece SVGs. Post-2026-05-05 panels-first pivot per `claude-work/DECISIONS.md` row #6 (and the comprehensive convention pass row #7). Keep open while authoring in Affinity. Replaces the prior cut-line-first-era version of this doc — cut-line-first remains as the legacy parser pathway in `preview.html` for pre-pivot pieces, but new authoring is panels-first._

This file is **co-authored** per CHARTER §3 + DECISIONS #3 — both Alan and Claude write to it. Settled-and-shipped conventions get unilateral edits (typos, examples, wording) with a one-line dated footer note. New conventions or changes to settled ones get talked through in chat first; the agreed shape lands as a DECISIONS.md row, and this file gets updated in the same pass.

---

## The eight canonical layers (top-level `<g id="...">`)

```
silhouette       outer cut path  (extruded as the slab)
cutouts          interior holes  (subtracted from the slab)
panels           closed polygon per region of the piece  (mandatory, even on flat pieces)
folds-valley     dashed-in-print folds  (paper folds toward you)
folds-mountain   plus-sign-in-print folds  (paper folds away from you)
axles            rotation centers  (the wires the piece spins on)
attach-points    cross-piece structural references  (pivots, attaches, holes, typed landings, letter targets)
labels           printed text + numerals  (decorative)
marks            same-piece markers  (decorative letters, multi-instance, alignments, cuts, untyped/closure landings)
```

Two layers are NEW since the panels-first pivot: **`panels`** (closed polygon per region) and **`attach-points`** (cross-piece structural references — was previously split across `axles` + `marks`). Two layers narrowed: **`axles`** to rotation-only (pin-holes moved to `attach-points`); **`marks`** to same-piece-or-decorative (typed cross-piece structural refs moved to `attach-points`, though typed landings can still live in either layer — parser reads both).

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
id="cutout"                     single hole
id="cutout-1", id="cutout-2"    multi-hole; one per interior hole
```

### panels (mandatory)

Panel ids are **bare aliases** — no `panel-` prefix. The parser does `getElementById(<id>)` directly.

```
id="<descriptive>"              e.g. main, stem, base, sider, sidel, flap1, flap2
id="<letter>"                   single letter from print labels  (a, b, c, d, g)
id="<letters>"                  composite letter clusters  (bh, ai, abc — multiple letters glued, no separator)
id="tab<letter>"                tab panel  (taba, tabb, ..., tabaa for closure tab)
id="<letter><partner-piece>"    landing region as panel  (b65 = "the b region for partner piece 65"; pairs with a marks-side `landing-b65` — see dual-presence pattern below)
id="paneN"                      numbered panel  (pane1, pane2, ... — fine when descriptive name doesn't apply)
id="tabff"                      double-letter tab from the print  (intentional artifact; suffix matches the printed label)
```

Suffix rules: **lowercase**, **no hyphens** in the panel-id suffix (the hyphen is the fold-id delimiter). Use `tabA` only if the print label is uppercase; otherwise lowercase letters.

### folds-valley / folds-mountain

```
id="fold-<a>-<b>"               binds the fold to panel-<a> and panel-<b>
                                e.g. fold-pane1-pane2, fold-main-tabb
                                — order doesn't matter; parser treats it symmetrically
                                — references panel ids directly (bare aliases)

id="fold-<a>-<b>-<deg>"         optional default angle in degrees
                                e.g. fold-stem-tabA-90
                                — positive = layer's natural direction (valley = dashed; mountain = plus-sign)

id="fold-<descriptive>"         single-panel folds, curved folds, or folds against unmodelled clusters
                                e.g. fold-insidetabs, fold-outsidetabs (concentric circle folds on 099)

<circle id="fold-...">          curved fold path; parser reads cx/cy/r directly
<ellipse id="fold-...">         elliptical fold path
```

Polarity is encoded by the layer the fold lives in. To flip polarity for a specific fold, move the path to the other layer. Sign of the optional default angle: positive = layer's natural direction.

### axles (rotation-only)

```
unidentified <ellipse>/<circle> axle markers — no id needed
id="<descriptive>-pivot"        e.g. anchor-pivot — names the axle/pin-hole on this piece
id="north"                      optional orientation cue: +0° points from axle to this marker
                                slider sign: +deg = CW (clock convention) viewed from front
```

The `axles` layer holds the actual axle pin-hole markers on this piece. The cross-piece reference to a *shared* pivot lives in `attach-points` as `pivot-<name>` — the two layers can use slightly different naming (`anchor-pivot` in `axles` vs. `pivot-anchor` in `attach-points`) because layer membership disambiguates the role.

### attach-points (cross-piece structural references)

Anything that's structurally part of the cross-piece connection graph. The parser builds the connection graph from this layer plus typed landings in `marks`.

```
id="attach-<letter><piece>"     this piece glues onto letter <letter> on piece <piece>
                                e.g. attach-g69, attach-h69, attach-i69 (068's attaches to 069's body cells)
                                e.g. attach-b66, attach-c66, ..., attach-h66 (065's attaches to 066's letter regions)

id="landing-<tab><piece>"       this piece receives tab <tab> from piece <piece>
                                e.g. landing-c69 (067 receives tab c from 069)
                                e.g. landing-j68 (066 receives j from 068)
                                — typed landings can also live in `marks`; parser reads both layers

id="pivot-<name>"               shared rotation pivot with peer pieces
                                e.g. pivot-anchor (067 + 069 share the anchor cluster pivot)

id="hole"                       bare = same-piece generic hardware-pin hole, no cross-piece partner
id="hole-<letter><piece>"       cross-piece pin hole receiving wire/pin from another piece

id="<letter>"                   bare letter = "letter <letter> is structurally referenced here on this piece"
                                e.g. j on 068 — the partner-side reference target for 066's `landing-j68`

id="back-<form>"                back-side annotation; the rest follows the standard form
                                e.g. back-landing-d, back-attach-X69, back-pivot-Y
                                — parser dispatches on leading token: `back-` first → side="back", rest standard
                                — distinct from `landing-back-g`: there `back-g` is the tab letter, not a side annotation
```

### marks (same-piece markers)

Everything that's not a typed cross-piece structural reference. Per-piece metadata only.

```
id="<letter>"                   bare letter = printed letter from the book; decorative
                                — duplicates allowed: 12 ellipses with id="a" = 12 instances of the same logical marker

id="landing-<panel-id>"         same-piece closure landing  (tab wraps around to land here on the same piece)
                                e.g. landing-taba, landing-tabb (closures on 069); landing-tabaa (066 closure)
                                — uses the panel-id form (matching the closure tab's panel id)

id="landing-<tab><piece>"       typed cross-piece landing (alternative to placement in attach-points; both OK)
                                e.g. landing-c69, landing-h65 (parser reads both layers for the connection graph)

id="align-<letter><partner-piece>"   cross-piece registration marker (paired symmetric form)
                                e.g. align-a99 on 100; align-a100 on 099

id="cut-<descriptive>"          cuts (prefix form, not suffix)
                                e.g. cut-lower, cut-upper (passage cuts on 100 — a strip passes through)
                                e.g. cut-a72 (accommodation cut on 070 — tab a is trimmed to make room for piece 72)

id="back-<id>"                  back-side variant of any of the above
```

### labels

```
no required ids                 printed text/numerals captured for decal rendering
```

---

## Quick mental model

> **The SVG names what panels ARE, what folds JOIN, what pieces ATTACH where, and what markers reference what. The parser doesn't try to derive any of these from geometry.**

If the parser would have to guess, the SVG is missing an id.

---

## Parser rules (panels-aware preview.html / connection-graph script)

These are the rules the parser follows when consuming a panels-first SVG. They're the formal counterpart of the conventions above.

**Panel resolution.** Direct lookup via `getElementById(<id>)`. Bare aliases enable this.

**Fold binding.** Parse `fold-<a>-<b>` ids by trying every possible split point; the first split where both sides are panel ids resolves the binding. Order of (a, b) is symmetric. Descriptive form `fold-<x>` (single token, no panel pair) uses single-panel-or-curved fallback.

**Cross-piece feature lookup (fuzzy substring + tiebreaker).** When piece A references letter `X` on piece B (e.g., `attach-X<B>` or `landing-X<B>`), find the matching feature on B by:

1. Exact panel id == `X`
2. Exact panel id == `tab<X>`
3. Partner attach-points: parsed letter field == `X`
4. Fuzzy substring on panel id (composite letter clusters like `bh`/`ai` match this way)
5. Fuzzy substring on attach-points semantic part (after stripping prefixes like `attach-`/`landing-`/etc., so the prefix word doesn't leak into the match)

When multiple panels match by substring, **prefer the shortest panel id** (`ai` beats `main` for letter `i`). Ties broken alphabetically.

**Side annotation.** Id starting with `back-` followed by a recognized prefix (`landing-`, `tab-`, `attach-`, `hole-`, `pivot-`) means the annotation is on the back side of the paper. Strip the `back-` and parse the rest as standard.

**Multi-instance markers.** In `marks` (and only `marks`), an id appearing on multiple elements is an intentional multi-instance marker. The parser treats them as a SET of points sharing one logical id. For N≥2 instances, the set defines an oriented frame (vector + rotation), not just a position.

**Affinity collision-suffix tolerance.** When Affinity auto-renames duplicate ids on export (e.g., `cutaway` + `cutaway1`, or `landing-d` + `landing-d` + `landing-d1`), treat `<id><digits>` (no hyphen separator) as the same logical id as the base.

**Parser tolerance.** Inside `<g id="panels">`, ignore any element with id starting with `cutaway` or `cutout-` (these belong in silhouette/cutouts; treat as authoring slip). Author's stated goal is to delete them on sight, but parser doesn't break.

**Panels mandatory.** Every piece must have `<g id="panels">` with at least one panel — even flat pieces (`<panel id="main">`). Pieces without a panels layer fall back to the legacy cut-line-first parser.

---

## Patterns and design rules

### Dual-presence pattern (typed landing as both panel and mark)

When a typed landing region is itself a folding panel — meaning it has its own fold relationships and is a distinct material area — author **both**:

- Panel `<letter><piece>` in `<g id="panels">` (the folding/material region, e.g. `b65` on 066)
- Mark `landing-<letter><piece>` in `<g id="marks">` *or* `<g id="attach-points">` (the connection-graph entry, e.g. `landing-b65`)

When the landing is just a point on a larger panel (no own folds, no distinct material area), only the mark is needed.

The parser handles both cases uniformly — for connection-graph purposes, the mark is the edge; the panel (when present) provides the geometric region for decals/material.

### Derived pivots

Not every piece in a rotating assembly needs its own `pivot-<name>`. Pieces *rigidly attached* to a pivot-bearing piece **inherit** the rotation through their cross-piece attach/landing edges. The assembly engine resolves any piece's rotation by walking the rigid-attachment edges back to a pivot-bearing piece.

Example: in the anchor cluster (065/066/067/068/069), 065 carries the actual axle pin-hole (`anchor-pivot` in `axles`); 067 and 069 carry the cross-piece pivot (`pivot-anchor` in `attach-points`); 068 inherits rotation through `attach-g69`/`attach-h69`/`attach-i69` (rigid attachment to 069); 066 inherits rotation through 7 typed landings to 065 plus 1 to 068. Only the pivot-bearing pieces need `pivot-<name>` markers.

### Composite letter panels

A single panel can carry multiple letter labels in the print (e.g., 069 has panel `bh` carrying letters b and h, and panel `ai` carrying letters a and i). The convention is to use the concatenated form as the panel id. Cross-piece references then use fuzzy substring matching to resolve to these composite ids — `attach-h69` matches `bh`; `attach-i69` matches `ai`.

When fuzzy match has multiple candidates, the parser prefers the shortest panel id (so `ai` beats `main` for letter `i`).

### Closure landings

When a tab wraps around the piece itself and lands within the same piece (e.g., the closure tab on a tube), use the panel-id form `landing-<panel-id>` (no piece number) in `marks`. The matching closure tab is `tab<letter>` (or `taba`/`tabaa` for a long closure tab).

Example: 066 has tab `tabaa` (the closure tab that wraps the cylinder) which lands on `landing-tabaa` within 066 itself. 069 has closure landings `landing-taba` and `landing-tabb` for tabs `taba` and `tabb`.

---

## Common slips to avoid

- **Hyphens inside panel suffixes.** `panel-tab-a` would break `fold-tab-a-stem` parsing. Use `tabA` or just `taba`.
- **`panel-` prefix on panel ids.** Panel ids are bare aliases. Direct ids: `main`, `tabb`, `bh`. Not `panel-main`.
- **Bare untyped landings still in `attach-points`.** Untyped (no piece suffix) landings like `landing-h` or `back-landing-d` are reference markers and live in `marks`. Cross-piece typed landings like `landing-c69` can live in either layer; parser reads both.
- **Pin-holes still in `axles`.** Pin-holes moved to `attach-points` as `hole` (bare) or `hole-<letter><piece>` (typed). `axles` is rotation-only.
- **Reversed fold layer names.** Canonical is `folds-valley` and `folds-mountain` (plural-first). `mountain-folds` is wrong.
- **Cut suffix instead of prefix.** `cut-lower` not `lower-cut`. Reads as "cut: [for what]."
- **Affinity auto-rename suffixes.** If you see `tab-c1` / `panel-stem1` / `landing-d1` after export, two elements had the same id and Affinity disambiguated. Parser tolerates these as same logical id, but cleanest is to fix the duplicate.
- **`cutaway` slipping into `panels` layer.** Parser-tolerated (ignored), but author's goal is to delete on sight.
- **Forgetting `<g id="panels">` on flat pieces.** Required even with one `main` panel.

---

## Cross-references

- `claude-work/DECISIONS.md` — decision records (row #6 panels-first pivot; row #7 comprehensive convention lock-in 2026-05-05).
- `claude-work/scripts/build_assembly_graph.py` — connection-graph extraction script; the formal parser of these conventions.
- `claude-work/state/connection-graph.{md,json}` — current cross-piece graph + per-piece state (regenerate via the script).
- `claude-work/CHARTER.md` — collaboration charter.
- `CLAUDE.md` — repo working conventions (some entries are pre-pivot; defer to this doc when in conflict).

---

*Last updated: 2026-05-05 — comprehensive panels-first lock-in pass after the anchor-pendulum batch (065/066/067/068/069 + 070/071/072 + 099/100). Replaces the prior cut-line-first-era version of this doc; LAYERS.md (the v0 cheat sheet from earlier the same day) consolidated and removed in the same pass. Conventions ratified by 24/24 cross-piece edges resolving cleanly across the batch.*
