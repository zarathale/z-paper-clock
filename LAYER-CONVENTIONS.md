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

id="<step>-fold-<a>-<b>"        optional fold-step ordinal (positive integer, prefix form)
                                e.g. 1-fold-pane3-pane4, 2-fold-pane4-pane5, 3-fold-pane5-pane6
                                — same step number across multiple folds = "fire simultaneously"
                                — phased fold sequence: step 1 first, step 2 second, etc.
                                — combinable with default-angle suffix: <step>-fold-<a>-<b>-<deg>
                                — Affinity exports the id as "_<step>-fold-..." (SVG-spec underscore prefix
                                  on digit-leading ids); parser strips the leading "_" to recover the form

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
id="attach-<letter><piece>"     this piece attaches onto <letter> on piece <piece>
                                <letter> must reference something AUTHORED on the partner — preferably a
                                mark (small shape in the partner's `marks` layer), because marks locate the
                                exact connection point (centroid of the shape) rather than a whole panel.
                                Prefer marks over panels: attach points are often a sub-portion of a panel,
                                and the mark's centroid is the default connection point geometry. Register
                                position by testing in preview.html and adjusting the mark placement if needed.
                                A printed tab letter from the book is the most natural mark id; when no
                                printed letter exists, author a small mark on the partner at the connection
                                location and give it any unambiguous id — then use that id here.
                                Do NOT invent letters that don't resolve to anything authored on the partner.
                                e.g. attach-g69, attach-h69, attach-i69 (068 → 069's marks g/h/i)
                                e.g. attach-b66, attach-c66, ..., attach-h66 (065 → 066's mark letters)
                                — for 093b → 093a: author a mark on 093a at the joint; use its id here

id="landing-<tab><piece>"       this piece receives tab <tab> from piece <piece>
                                e.g. landing-c69 (067 receives tab c from 069)
                                e.g. landing-j68 (066 receives j from 068)
                                — typed landings can also live in `marks`; parser reads both layers

id="pivot-<name>"               shared rotation pivot with peer pieces
                                e.g. pivot-anchor (067 + 069 share the anchor cluster pivot)

id="hole"                       bare = same-piece generic hardware-pin hole, no cross-piece partner
id="hole-<letter><piece>"       cross-piece pin hole receiving wire/pin from another piece

id="attach-<panel-id>"          same-piece closure attach: this attach surface mates to <panel-id> of THIS piece
                                e.g. back-attach-pane1, back-attach-pane2, back-attach-pane3 (095 closure attaches —
                                bob-casing strip wraps around and glues back onto pane1/2/3)
                                — distinguished from cross-piece `attach-<letter><piece>` by the suffix:
                                  if it matches a panel of this piece, it's same-piece; otherwise cross-piece
                                — typically pairs with `back-` side annotation (closures usually on the back)
                                — parallel to `landing-<panel-id>` in marks (same suffix grammar, different layer
                                  for "structural attach surface" vs. "registration mark")

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

**Fold-step prefix.** Optional leading `<step>-` (positive integer + hyphen) before `fold-` is the fold-step ordinal — when this fold fires in a phased fold sequence. Same step across multiple folds = simultaneous. Stripped before panel-pair resolution. The trailing `-<deg>` default-angle suffix is independent and combinable.

**Affinity underscore prefix.** Affinity Designer prefixes ids that start with a digit with `_` for SVG-spec compliance (`_3-fold-pane1-pane2`); the author's literal is preserved in the `serif:id` attribute. Parser strips a leading `_` from the id before applying fold-id parsing, recovering the authored form. (Parallel to convention #16 collision-suffix tolerance, but for digit-leading ids rather than duplicate ids.)

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

## Per-piece JSON sidecar (`NNN.json`)

Per-piece JSON lives at `work/pieces/NNN/NNN.json` alongside the SVG (location tracks the SVG; would migrate with any future authoring-tree migration). The sidecar is **optional** — pieces without a sidecar render fine. Claude is the author for everything except `assembled.folds`, which the preview generates from slider state and Alan merges in by hand.

Top-level keys: `function`, `assembled`, `connections`. All optional; pieces without any of them simply omit the file.

### `function` block (mechanism geometry; pre-charter convention)

Optional. Captures mechanism geometry — gear tooth counts, axle positions, drive relationships — for §II.B (gear train) and §II.C (anchor / pendulum / escapement) pieces only. Settled 2026-04-30 ("faithful trace + functional sidecar" — see `CLAUDE.md` Architectural Decisions). Pieces in other sections (framework, hands, weight, face, case) stay artifact-faithful with no `function` block.

```json
{
  "function": {
    "teeth": 60,
    "drives": "069",
    "anchor_unit": "escape-wheel-advance",
    "...": "..."
  }
}
```

The preview surfaces this as a read-only summary in the side panel (existing behavior in `maybeLoadSidecar` / `renderFunctionBlock`). The validation script that operates on `function` blocks is queued under M2.

### `assembled.folds` block (per-fold assembled-state angles)

Optional. A map of fold-id → angle in degrees, capturing the assembled-state pose for each fold of this piece. The preview reads this on load and uses it as the per-fold slider's default; the preview's "Save assembled pose" affordance emits a JSON snippet that Alan merges back into the sidecar.

```json
{
  "assembled": {
    "folds": {
      "fold-pane1-pane2": 90,
      "fold-tabaa-pane7": 180,
      "_3-fold-pane1-pane2": 180
    },
    "captured": "2026-05-06T15:30:00",
    "note": "Final assembled state per book figure 14."
  }
}
```

Rules:

- **Keys are the literal SVG fold ids.** Includes any Affinity `_<digit>` underscore prefix (`_3-fold-pane1-pane2`). Don't strip; the parser's `_`-strip normalization is for fold-id parsing, not for sidecar keying.
- **Values are signed integers or floats** in degrees. Sign convention matches the existing default-angle suffix: positive = layer's natural direction (valley = dashed-in-print direction; mountain = plus-sign direction). To flip polarity for a fold, move the path to the other layer in the SVG; the sidecar value stays positive.
- **Precedence for the slider default** (highest first): `assembled.folds[id]` > fold-id `-<deg>` suffix > 0.
- **Sibling fields** `captured` (ISO 8601 timestamp; informational) and `note` (free-form) are optional.

Inter-piece assembled transforms (where each piece sits in 3D space relative to its neighbors) are NOT in scope here — that's M4 assembly-transform work and lives separately. `assembled.folds` is one piece's internal geometry only.

See DECISIONS #11 for the full rationale.

### `connections.inferred[]` block (learned-but-not-printed connections)

Optional. An array of cross-piece (or same-piece) relationships that the printed piece doesn't explicitly mark — connections learned from the book's instructions text, from physically assembling pieces, or from any source other than the SVG itself. `build_assembly_graph.py` reads this list during piece extraction and merges it into the cross-piece graph alongside SVG-derived edges, tagging each merged edge with `provenance: "authored" | "inferred"`.

```json
{
  "connections": {
    "inferred": [
      {
        "kind": "attach",
        "side": "front",
        "letter": "x",
        "partner": "099",
        "source": "instructions §II.B p. 14",
        "note": "Pin from 097 actually slots through 099's main panel near landing-c, not through the printed letter location."
      },
      {
        "kind": "attach-same-piece",
        "side": "back",
        "panel": "pane2",
        "source": "bench: figured out during cylinder roll",
        "note": "..."
      },
      {
        "kind": "pivot",
        "name": "anchor",
        "source": "instructions §II.B",
        "note": "068 also rotates around the anchor pivot; not printed on 068."
      }
    ]
  }
}
```

Per-entry shape:

- **`kind`** (mandatory) — one of: `attach`, `landing`, `hole`, `pivot`, `attach-same-piece`, `landing-same-piece`. Same kinds the existing connection-graph uses.
- **`side`** — `"front"` or `"back"`; default `"front"`.
- **`letter`** — for `attach` / `hole` / `landing` (when partner has a letter form); else null.
- **`tab`** — for `landing`; else null.
- **`name`** — for `pivot`; else null.
- **`panel`** — for `*-same-piece`; the panel id of THIS piece the inferred attach mates to; else null.
- **`partner`** — partner piece id (numeric, zero-padded or bare; merger normalizes). Null for `pivot` and same-piece kinds.
- **`source`** (MANDATORY) — free-form string identifying where the knowledge came from (`"instructions §II.B p. 14"`, `"bench: cylinder closure"`, `"derived from gear-train ratios"`).
- **`note`** — optional free-form context.

Conflict policy: if an inferred entry duplicates an authored edge (same `{from, to, kind, letter|tab|name|panel}`), the authored entry wins and the merger flags the duplicate with a warning. The script does not fail — duplicates can mean Alan authored the connection on the SVG after the inferred entry was captured, in which case the inferred entry should be removed manually.

See DECISIONS #10 for the full rationale.

### Where this fits in the parser pipeline

The audit script reads SVG → produces authored edges → reads sidecar → produces inferred edges → merges → emits a single connection graph keyed by provenance. The preview reads SVG for geometry and sidecar for assembled-pose defaults + function-block surface. Neither Cowork nor Code modifies authored SVG-derived data based on sidecar contents — the SVG is always artifact-truth and inferred is always overlay.

---

## Patterns and design rules

### Mark-first attach pattern (preferred for all cross-piece attaches)

When piece A attaches to piece B, the preferred form is:

- **Piece B** (`marks` layer): a small shape (circle, polygon, ellipse) at the exact connection location. Its centroid is the default connection point geometry. Give it an unambiguous id — a printed tab letter if one exists, otherwise any descriptive label unique within B's marks.
- **Piece A** (`attach-points` layer): `attach-<that-id>B` referencing the mark.

Why marks over panels: the attachment is often a sub-portion of a panel, not the whole panel. The mark pins the geometry precisely. Panel ids resolve as a fallback (parser's cross-piece lookup checks marks before panels), but a mark-first approach gives the assembly engine and preview a real point to work from. Once the mark is placed, test the connection in `preview.html` and adjust the mark's position to refine registration before saving.

The printed tab letter from the book is the canonical case — the letter is already a printed mark on the plate. When no printed letter exists at the connection (e.g., two halves of the same piece, or an unlettered glue edge), author a small shape on the partner piece at the joint and assign it an id. What id? Anything unambiguous and lowercase: a descriptive word (`joint`, `seam`, `edge-left`), or a new single letter not used elsewhere on that piece.

**For 093b → 093a specifically:** place a mark on 093a at the joint edge, give it an id (e.g. `joint`), then author `attach-joint093a` on 093b.

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

- **Invented attach letter with no authored mark on the partner.** If `attach-x093a` is authored on 093b but piece 093a has no mark or element with id `x`, the parser can't resolve the connection. Always verify the referenced id actually exists on the partner before export.
- **Attaching to a panel when a mark would be more precise.** Panel ids work as a fallback, but marks are preferred — they give the assembly engine a point, not a region.
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

## Lane discipline (sidecar vs. SVG)

**The SVG carries originally-authored content from the printed piece** — silhouette, cuts, panels, folds, printed labels, printed connection markers (tabs, landings, attaches, pivots). That's Alan's authoring lane and it stays artifact-faithful.

**The sidecar carries everything else** — assembled-state poses, learned cross-piece connections, mechanism geometry, anything we figure out from the instructions text or by physically assembling. Schema is Claude's call (with co-authoring on shape changes per DECISIONS #3); Alan reads. New blocks land here, never in the SVG.

The rule keeps the two halves cleanly separable: regenerate the SVG (Affinity export) without losing any learned context; regenerate the sidecar (audit script, preview save) without retouching authored geometry.

---

## Cross-references

- `claude-work/DECISIONS.md` — decision records (row #6 panels-first pivot; row #7 comprehensive convention lock-in 2026-05-05; rows #10–#11 sidecar `connections.inferred[]` + `assembled.folds`).
- `claude-work/scripts/build_assembly_graph.py` — connection-graph extraction script; the formal parser of these conventions, also the merger for `connections.inferred[]`.
- `claude-work/state/connection-graph.{md,json}` — current cross-piece graph + per-piece state (regenerate via the script).
- `claude-work/CHARTER.md` — collaboration charter.
- `CLAUDE.md` — repo working conventions (some entries are pre-pivot; defer to this doc when in conflict).

---

*Last updated: 2026-05-07 — documented the mark-first attach pattern: `attach-<letter><piece>` should reference a mark on the partner (centroid = connection point geometry), not a panel; marks are preferred because they locate the exact sub-panel connection point. Added "Mark-first attach pattern" to Patterns section; updated `attach-<letter><piece>` entry; added two entries to Common slips.*

*Earlier 2026-05-06 — added "Per-piece JSON sidecar" section documenting the existing `function` block plus two new blocks (`assembled.folds` per DECISIONS #11; `connections.inferred[]` per DECISIONS #10). Added "Lane discipline" section codifying SVG-vs-sidecar split: SVG = originally-authored printed content (Alan's lane); sidecar = everything learned afterward (Claude's lane on schema). Re-authoring the SVG to capture inferred or assembled-state knowledge is explicitly out — that goes in the sidecar.*

*Earlier 2026-05-05 — comprehensive panels-first lock-in pass after the anchor-pendulum batch (065/066/067/068/069 + 070/071/072 + 099/100). Replaces the prior cut-line-first-era version of this doc; LAYERS.md (the v0 cheat sheet from earlier the same day) consolidated and removed in the same pass. Conventions ratified by 24/24 cross-piece edges resolving cleanly across the batch.*
