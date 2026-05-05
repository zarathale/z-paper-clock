# LAYER-CONVENTIONS.md — z-paper-clock SVG authoring cheat sheet

Quick reference for naming layers and elements while editing per-piece SVGs in Affinity Designer (or Inkscape). Authoritative sources: `CLAUDE.md` §"File Naming Conventions" + the resolved-decision rows for cut-layer and axles (pre-charter conventions); `claude-work/DECISIONS.md` rows (post-charter conventions; row #6 onward). This file is the distilled scannable version, kept short on purpose so it can stay open on a second window while authoring.

This file is **co-authored** per CHARTER §3 + DECISIONS #3 — both Alan and Claude write to it. Settled-and-shipped conventions get unilateral edits (typos, examples, wording) with a one-line dated footer note. New conventions or changes to settled ones get talked through in chat first; the agreed shape lands as a CLAUDE.md / DECISIONS.md row, and this file gets updated in the same pass.

The audit script (`work/scripts/audit_state.py`) checks every SVG against these conventions on every run; new conventions are added there as separate checks. Don't be precious about getting everything right on the first pass — convention drift is detected, not enforced. (Audit lives in frozen `work/`; next iteration migrates to `claude-work/` per CHARTER §5. New panels-first checks below are documented but not yet wired into the audit.)

---

## Canonical layer names

Every per-piece SVG contains zero or more of these as top-level `<g>` elements. Names match exactly (lowercase, hyphenated). In Affinity, layer-name → `id` on export. In Inkscape, layer name lands as `inkscape:label`; either works.

| Layer | What goes in it | Required? |
|---|---|---|
| `silhouette` | The outer cut-line of the piece. The only layer that extrudes. | **Required for every piece** |
| `cutouts` | Interior holes punched out of the silhouette (e.g. piece 71's center cell). | Only if the piece has interior cuts |
| `panels` | One closed polygon per region of the piece (NEW post-2026-05-05; replaces cut-line-first region derivation). | Required for new pieces; not present on legacy/pre-2026-05-05 pieces |
| `folds-valley` | Open paths along dashed fold lines (valley creases). | Only if the piece folds |
| `folds-mountain` | Open paths along plus-sign fold lines (mountain creases). | Only if the piece folds |
| `axles` | Point markers (ellipse / circle) at *rotation* axle centers — the points this piece pivots around. Plus optional `id="north"` for orientation. | Only on rotating pieces (gear train, anchor, hands) |
| `attach-points` | Pin-holes, mechanical pivots, and landing markers — places where *other* pieces connect to this one (NEW post-2026-05-05; previously these were collapsed into `axles` and `marks`). | Only if the piece has cross-piece connections |
| `glue-zones` | Closed paths for hatched glue-reception rectangles. | Only if the piece glues to another |
| `labels` | Text labels and piece numbers as printed. | Optional; informational |
| `marks` | Construction dotted lines, registration marks, anything else from the print. (Landing markers moved OUT to `attach-points` post-2026-05-05.) | Optional |

Anything outside this list will be flagged as off-spec by the audit. Extending the canonical set is a CLAUDE.md decision-table or `claude-work/DECISIONS.md` row, not a unilateral one.

**Convention age note.** `panels` and `attach-points` are new as of `claude-work/DECISIONS.md` row #6 (2026-05-05). Pre-2026-05-05 pieces (001/002/058/065/066/067/070/071/072/113) live under the older "cut-line-first" convention where regions were derived from silhouette + fold lines, pin-holes lived in `axles`, and landings lived in `marks`. Both conventions are valid; the audit understands which a given piece is on by which layers it carries. Existing pieces don't migrate at convention-change time; they get uplifted on the next time they're touched (per the existing decoupling at the bottom of this file).

---

## `silhouette` layer — the cut

Inside `<g id="silhouette">`:

- `id="cutaway"` — the single outer cut polygon. Use this when the piece has one connected outline.
- `id="cutaway-1"`, `id="cutaway-2"`, `…` — multiple disconnected outer pieces sharing a single SVG (numeric suffix, scales past 26).
- `id="mask"` or `id="mask-N"` — visual authoring frame. Parser ignores. Use for an artboard outline you want visible while editing without it leaking into the geometry.

Affinity wraps silhouette children in an unnamed `<g>` on export. The parser walks descendants, so the wrapper is transparent — no need to flatten.

`cutaway-N` ≠ `cutout-N`. `cutaway-N` is "another disconnected outer piece" (becomes its own slab). `cutout-N` is "another interior hole in the same piece" (subtracted from the slab). They live in different top-level layers.

---

## `cutouts` layer — interior holes

Inside `<g id="cutouts">`:

- `id="cutout-1"`, `id="cutout-2"`, `…` — interior holes punched out of the silhouette. Numeric suffix.

Each `cutout-N` is a closed path that gets subtracted from the silhouette extrusion. Convention is locked in; the implementation in `preview.html` lands in M0.6.10.

---

## `panels` layer — explicit region authoring (NEW 2026-05-05)

Inside `<g id="panels">`:

- One closed polygon per panel of the piece. Each panel polygon gets a descriptive `id` of the form `panel-<descriptive>` (e.g. `panel-stem`, `panel-tab-c`, `panel-base`). Names are unique within the SVG and chosen to make sense when looking at the piece — they don't need to match any external convention; they just need to be unique.
- The panels collectively tile the piece. A piece with N regions has N panel polygons.

**Why this exists.** Pre-2026-05-05, region structure was *derived* from silhouette + fold geometry by a cut-line-first algorithm in `preview.html` (`buildFaceGraph` + `extendFoldsToSilhouette`). That algorithm worked well on simple pieces but failed on long strips with co-linear folds (piece 066) and trivially on pieces with no folds at all (piece 067). Panels-first inverts: the SVG names what the panels ARE; the parser stops trying to derive what the author already knows.

**What pieces need this.** New pieces author panels. Pre-2026-05-05 pieces stay on cut-line-first as legacy until they're being touched anyway — no bulk migration. The audit knows which convention a given piece is on by whether `panels` is present.

**Status:** convention is provisional. **Piece 069 is the test piece** — see `claude-work/to-alan/069-panels-first/`. If 069 authoring proves panels-first workable in Affinity, the convention rolls forward. If it's painful, we either build an authoring helper (preview.html grows a "propose panels from cut-line-first, accept/edit" tool) or revisit the form.

---

## `axles` layer — rotation centers + orientation

Inside `<g id="axles">`:

- Plain ellipses / circles / paths — *rotation* axle markers. The points around which this piece itself pivots (gear axles, anchor axles, hand axles). One per piece in current pieces; multi-axle support deferred. No id required on these.
- `id="north"` — *optional*, one per piece. Defines the +0° rotation direction via the vector from the active axle (currently `axles[0]`) to this element's centroid.

Sign convention for any rotation slider that consumes axles: **+deg = clockwise** when viewed from the front (clock convention). `id="north"` renders in `preview.html` as a brass-gold sphere; the framework wire is silver. The two are deliberately distinct so they read as separate roles.

If `id="north"` exists without an axle, the audit flags it (banner-warned + ignored at render time).

**Convention narrowing 2026-05-05:** `axles` is now rotation-only. Pin-holes (static through-holes that accept *other* pieces' wires, previously authored as `id="hole-..."` here on pieces 001/002/113) move to the new `attach-points` layer. Mechanical pivots (`anchor-pivot` on pieces 067/069) also move to `attach-points`. Pre-2026-05-05 pieces still carry these in `axles`; the audit understands the legacy form.

---

## `attach-points` layer — where other pieces connect (NEW 2026-05-05)

Inside `<g id="attach-points">`:

- `id="pin-<descriptive>"` — pin-holes. Static through-holes that accept *another* piece's wire. Examples: `pin-f115` ("hole for the wire from piece 115's f-axle"), `pin-g116`. Pre-2026-05-05 these lived in `axles` as `hole-f...` / `hole-g...`.
- `id="pivot-<descriptive>"` — mechanical pivots. Where another piece physically rocks/swings around a point on this piece (the anchor escapement is the canonical case). Example: `pivot-anchor`. Distinct from `pin-` — pivots imply motion that's part of the function block; pins are static structural.
- `id="landing-<tab-letter><piece-number>"` — landing markers. The panel on this piece that *receives* a tab from another piece. Format: `landing-c70` reads as "this piece's landing for tab `c` from piece 70." Pre-2026-05-05 these lived in `marks`. (See "Cross-piece pairing" below.)

Authored as small ellipse / circle / path elements; the centroid is the connection point. All three categories are points (not regions) for now.

**Why this exists.** Pre-2026-05-05, three genuinely different concepts were collapsed into the wrong bins: pin-holes lived in `axles` (which is supposed to be rotation centers, not static holes), mechanical pivots had nowhere clean to live (some pieces just had `id="anchor-pivot"` outside any canonical layer), and landings lived in `marks` alongside construction dotted lines. The 22:00 inventory (`sessions/2026-05-04-2200_cowork_orientation-reset-research.md`) showed this as a real source of authoring drift across pieces 001/002/067/069/113. The split: `axles` = rotation centers for *this* piece; `attach-points` = connection points for *other* pieces.

**Cross-piece pairing.** A tab `c` on piece 70's `glue-zones` layer ⟷ `landing-c70` on piece 71's `attach-points` layer. That pairing is the connection-graph primitive the assembly engine (M4) will read; nothing consumes it today, but it's worth authoring as you go — re-deriving it later from scanned annotations is harder than capturing it once.

---

## `folds-valley` and `folds-mountain` — creases

Open paths. Each path is a single fold line (start → end). Affinity exports as `<path d="M..L.." />`.

- Valley = dashed in print → goes in `folds-valley`.
- Mountain = plus-sign in print → goes in `folds-mountain`.

Don't merge multiple fold lines into one multi-segment path. One fold = one path.

### Per-element ids inside fold layers — panels-first form (NEW 2026-05-05)

When the SVG carries a `panels` layer, each fold path's id declares the two panels it joins:

- **`id="fold-<a>-<b>"`** — the fold sits between panels `panel-<a>` and `panel-<b>`. Example: `id="fold-stem-tabA"` joins `panel-stem` and `panel-tabA`. Order doesn't matter; the parser treats it symmetrically. The `fold-` prefix gives every fold path a unique id within the SVG, sidestepping Affinity's cross-layer id-collision auto-rename. Note: in the v0 form, **panel id suffixes should not contain hyphens** (use `panel-tabA` not `panel-tab-a`) — the hyphen is the parser's delimiter between the two panel-name halves of the fold id. If hyphenated suffixes prove necessary at the canvas, the convention adapts (sidecar JSON edge list, or a different separator).

- **`id="fold-<a>-<b>-<N>"`** — same plus an optional default-angle suffix in degrees. Example: `id="fold-stem-tabA-40"` (default 40° fold). Parsing rule: after stripping the `fold-` prefix, if the trailing token parses as a non-negative integer, treat it as the angle; the remaining two tokens name the two panels.

Polarity: positive angle means "fold in the layer's natural direction" (valley = dashed-in-print direction; mountain = plus-sign-in-print direction). Polarity is encoded by which layer the path lives in, not by the sign of the angle. Override polarity by moving the path to the other layer.

If a fold path's id names a panel pair that doesn't resolve (one or both panels missing), the audit flags it (banner warning) and the parser falls through to unidentified-path behavior.

**Status note on the form.** This shape is provisional — it's what the 069 panels-first authoring brief at `claude-work/to-alan/069-panels-first/` proposes. If Affinity collision-renames any (rare; only when two folds bind the same pair), or the no-hyphens-in-panel-ids constraint feels awkward at the canvas, or the form feels awkward in any other way, the convention may evolve to a sidecar JSON edge list (fold paths get arbitrary ids; bindings live in per-piece JSON) or a hybrid. The 069 experiment is the test.

### Per-element ids inside fold layers — cut-line-first form (LEGACY pre-2026-05-05)

For pieces authored before 2026-05-05 that don't carry a `panels` layer, the older marker-bound fold convention applies. Three flavors of fold-path id, in increasing specificity:

1. **Unidentified path** — no `id` (or an Affinity-auto id like `path123`). Parser uses the layer-default angle for any region split this fold creates. This is the right choice for column-internal folds whose location alone is enough to identify them geometrically.

2. **Marker-bound id** — `id="fold-<marker-id>"` where `<marker-id>` matches an element in `<g id="marks">` (landings) or otherwise identifies a region by an authored marker. The parser strips the `fold-` prefix, looks up the rest in the marks centroid map, and binds the fold to the region containing that marker's centroid. Examples: `id="fold-tab-c"`, `id="fold-landing-h65"`. (Tab markers `tab-<letter>` historically lived in `glue-zones`; the parser walked all marks-bearing layers.)

3. **Marker-bound id with default angle** — append `-<N>`. Examples: `id="fold-tab-c-40"`, `id="fold-landing-h65-90"`. The marker id `landing-h65` ends in `h65` (digits glued to letters), so stripping doesn't see a numeric suffix — `id="fold-landing-h65"` parses as marker only, no angle.

Sign of the default angle: same convention as panels-first form (positive = layer's natural direction; polarity by layer membership).

A `fold-` prefix without a matching marker triggers a banner warning. The legacy `fold-<digits>` / `fold+<digits>` angle-only form (e.g. `fold-90`, `fold+45`) is preserved as a backward-compat fallback — pre-2026-05-04 SVGs still parse.

**Migration:** legacy pieces stay legacy until they're being touched. When a legacy piece is re-authored panels-first, fold-path ids change shape from `fold-<marker-id>` to `fold-<panel-a>-<panel-b>`; the marker side moves out of `marks` into `attach-points`.

---

## `marks` layer — construction marks only (post-2026-05-05)

Inside `<g id="marks">`:

- Unidentified ellipse / circle / path / line elements — construction lines, dotted alignment guides, registration marks, anything else carried from the print that's neither cut nor fold nor connection. No id required.
- `mark-<descriptive>` ids are also fine — `mark-h`, `mark-i` on piece 069 are examples of construction marks the author chose to id.

**Convention narrowing 2026-05-05:** landings moved out of `marks` into `attach-points`. Pre-2026-05-05 pieces still carry `landing-<tab-letter><piece-number>` ids inside `<g id="marks">`; the audit understands the legacy form. New pieces author landings in `attach-points`.

---

## `glue-zones`, `labels` — purely visual layers

These layers are rendered into the front-face decal but don't drive geometry. Author them as you see them in the print — closed paths for glue-zones (so the hatch is the fill), text or text-as-paths for labels.

---

## "Faithful trace" direction

The default for the build is to trace each piece **faithfully** — the SVG geometry preserves the human-drawn, human-scanned messiness as the artifact. Don't "clean up the gear teeth" against the SVG. If mechanism geometry needs to be captured (gear-train pieces in §II.B + escapement in §II.C), it goes in the per-piece JSON sidecar's optional `function` block, not back into the SVG.

This means a piece that looks slightly bowed or off-tooth in the SVG is correct as long as it matches the print. The mechanism animation (M6, deferred) reads from the `function` block, not the trace.

---

## Common authoring slips the audit will catch

- Top-level `<g>` with a name that isn't on the canonical list (typos like `silhoutte`, `axle`, `fold-valley`, reversed `mountain-folds` / `valley-folds`)
- An `<g id="silhouette">` with no `cutaway` or `cutaway-N` child
- A bare `<path>` directly under `<svg>` (everything should live in a layered group)
- An SVG saved into `source/pieces/` (per `source/pieces/README.md`, SVGs belong in `work/pieces/NNN/` — there is no inbox)
- A `cutout-letter-suffix` instead of `cutout-N` (audit currently advises numeric)
- An `id="north"` without an axle in the same SVG
- (Post-2026-05-05) `id="hole-..."` inside `<g id="axles">` — should be in `attach-points` as `pin-...`
- (Post-2026-05-05) `id="landing-..."` inside `<g id="marks">` — should be in `attach-points`
- (Post-2026-05-05) `id="anchor-pivot"` outside `<g id="attach-points">` — should be in `attach-points` as `pivot-anchor`
- (Post-2026-05-05) A `panels` layer where panel polygons aren't fully closed, or where panel-ids aren't unique within the SVG, or where a fold path's `fold-<a>-<b>` id names a panel that doesn't exist

Run `python work/scripts/audit_state.py --piece NNN` to see what the audit thinks of any specific piece. (Audit script is in the now-frozen `work/`; the next iteration migrates to `claude-work/` per CHARTER §5 — the new panels-first checks above are not yet in the audit; they land when the audit moves.)

---

## When conventions change

When a new authoring convention lands (e.g. the cut-layer / axles-with-north conventions both shipped 2026-05-02), the change shows up in three places:

1. A new row in `CLAUDE.md` §"Architectural Decisions (Closed)" describing the rule.
2. An updated section in this file (or a new section) describing the rule in scannable form.
3. A new check in `work/scripts/audit_state.py`.

Existing pieces don't migrate at convention-change time. The next audit run flags them as failing the new check; pieces get uplifted on the next time they're touched (or in a deliberate uplift pass). This keeps convention evolution and authoring throughput decoupled.

---

*Last updated: 2026-05-05 — panels-first convention added per `claude-work/DECISIONS.md` row #6. New `panels` layer (closed polygon per region, `id="panel-<descriptive>"`); new `attach-points` layer (pin-holes / pivots / landings, previously collapsed into `axles` and `marks`). `axles` narrows to rotation-only; `marks` narrows to construction/registration only. Fold-path id form gains a panels-first variant `fold-<panel-a>-<panel-b>` (with optional `-<N>` angle suffix); the cut-line-first marker-bound form is preserved as legacy for pre-2026-05-05 pieces. Provisional status — piece 069 is the test piece (brief at `claude-work/to-alan/069-panels-first/`); convention rolls forward if 069 authoring proves workable, otherwise we revisit the form. Co-authored update per CHARTER §3 + DECISIONS #3.*

*Earlier 2026-05-04 — marker-bound fold ids subsection added under `folds-valley` / `folds-mountain`. Pattern: `fold-<marker-id>` with optional default-angle suffix (`fold-tab-c-40`, `fold-landing-h65-90`). The `fold-` prefix sidesteps Affinity's cross-layer id-collision auto-rename. Parser implementation is in flight in `preview.html`; geometric-adjacency-based, with a known follow-up to migrate to shared-edge polygon topology in the next iteration. (Note 2026-05-05: this form is now LEGACY; new pieces use the panels-first form above.)*

*Earlier 2026-05-03 — landing-marker convention added; `marks` layer broken out into its own section (it's no longer purely visual now that it carries landings). The "everything else from the print" layer is named `marks` (not `marks-other`; that was an incorrect name in earlier drafts and has been corrected throughout the docs).*

*Earlier 2026-05-03 — initial authoring. Distilled from `CLAUDE.md` cut-layer convention row (2026-05-02), axles + north convention row (2026-05-02), faithful-trace direction (2026-04-30), and `work/SPEC-3D-VIEWER.md` §"Authoring/QA preview tool".*
