# LAYER-CONVENTIONS.md — z-paper-clock SVG authoring cheat sheet

Quick reference for naming layers and elements while editing per-piece SVGs in Affinity Designer (or Inkscape). Authoritative source: `CLAUDE.md` §"File Naming Conventions" + the resolved-decision rows for cut-layer and axles. This file is the distilled scannable version, kept short on purpose so it can stay open on a second window while authoring.

The audit script (`work/scripts/audit_state.py`) checks every SVG against these conventions on every run; new conventions are added there as separate checks. Don't be precious about getting everything right on the first pass — convention drift is detected, not enforced.

---

## Canonical layer names

Every per-piece SVG contains zero or more of these as top-level `<g>` elements. Names match exactly (lowercase, hyphenated). In Affinity, layer-name → `id` on export. In Inkscape, layer name lands as `inkscape:label`; either works.

| Layer | What goes in it | Required? |
|---|---|---|
| `silhouette` | The outer cut-line of the piece. The only layer that extrudes. | **Required for every piece** |
| `cutouts` | Interior holes punched out of the silhouette (e.g. piece 71's center cell). | Only if the piece has interior cuts |
| `folds-valley` | Open paths along dashed fold lines (valley creases). | Only if the piece folds |
| `folds-mountain` | Open paths along plus-sign fold lines (mountain creases). | Only if the piece folds |
| `axles` | Point markers (ellipse / circle) at axle / pin-hole centers. | Only on rotating pieces (gear train, anchor, hands) |
| `glue-zones` | Closed paths for hatched glue-reception rectangles. | Only if the piece glues to another |
| `labels` | Text labels and piece numbers as printed. | Optional; informational |
| `marks-other` | Construction dotted lines, registration marks, anything else from the print. | Optional; informational |

Anything outside this list will be flagged as off-spec by the audit. Extending the canonical set is a CLAUDE.md decision-table edit, not a unilateral one.

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

## `axles` layer — rotation centers + orientation

Inside `<g id="axles">`:

- Plain ellipses / circles / paths — axle markers (the existing convention). No id required on these.
- `id="north"` — *optional*, one per piece. Defines the +0° rotation direction via the vector from the active axle (currently `axles[0]`) to this element's centroid.

Sign convention for any rotation slider that consumes axles: **+deg = clockwise** when viewed from the front (clock convention). `id="north"` renders in `preview.html` as a brass-gold sphere; the framework wire is silver. The two are deliberately distinct so they read as separate roles.

If `id="north"` exists without an axle, the audit flags it (banner-warned + ignored at render time).

---

## `folds-valley` and `folds-mountain` — creases

Open paths. Each path is a single fold line (start → end). Affinity exports as `<path d="M..L.." />`.

- Valley = dashed in print → goes in `folds-valley`.
- Mountain = plus-sign in print → goes in `folds-mountain`.

Don't merge multiple fold lines into one multi-segment path. One fold = one path.

If a fold has an authored "default angle" (e.g. 90° for a folded-up sidewall), encode it as a path id of the form `valley-90` or `mountain-90`. The v1b face-graph reader looks at the trailing `-N` of the id for an initial angle; missing → 0°.

---

## `glue-zones`, `labels`, `marks-other` — purely visual layers

These layers are rendered into the front-face decal but don't drive geometry. Author them as you see them in the print — closed paths for glue-zones (so the hatch is the fill), text or text-as-paths for labels, anything else in `marks-other`.

---

## "Faithful trace" direction

The default for the build is to trace each piece **faithfully** — the SVG geometry preserves the human-drawn, human-scanned messiness as the artifact. Don't "clean up the gear teeth" against the SVG. If mechanism geometry needs to be captured (gear-train pieces in §II.B + escapement in §II.C), it goes in the per-piece JSON sidecar's optional `function` block, not back into the SVG.

This means a piece that looks slightly bowed or off-tooth in the SVG is correct as long as it matches the print. The mechanism animation (M6, deferred) reads from the `function` block, not the trace.

---

## Common authoring slips the audit will catch

- Top-level `<g>` with a name that isn't on the canonical list (typos like `silhoutte`, `axle`, `fold-valley`)
- An `<g id="silhouette">` with no `cutaway` or `cutaway-N` child
- A bare `<path>` directly under `<svg>` (everything should live in a layered group)
- An SVG saved into `source/pieces/` (per `source/pieces/README.md`, SVGs belong in `work/pieces/NNN/` or transiently in `inbox/`)
- A `cutout-letter-suffix` instead of `cutout-N` (audit currently advises numeric)
- An `id="north"` without an axle in the same SVG

Run `python work/scripts/audit_state.py --piece NNN` to see what the audit thinks of any specific piece.

---

## When conventions change

When a new authoring convention lands (e.g. the cut-layer / axles-with-north conventions both shipped 2026-05-02), the change shows up in three places:

1. A new row in `CLAUDE.md` §"Architectural Decisions (Closed)" describing the rule.
2. An updated section in this file (or a new section) describing the rule in scannable form.
3. A new check in `work/scripts/audit_state.py`.

Existing pieces don't migrate at convention-change time. The next audit run flags them as failing the new check; pieces get uplifted on the next time they're touched (or in a deliberate uplift pass). This keeps convention evolution and authoring throughput decoupled.

---

*Last updated: 2026-05-03 — initial authoring. Distilled from `CLAUDE.md` cut-layer convention row (2026-05-02), axles + north convention row (2026-05-02), faithful-trace direction (2026-04-30), and `work/SPEC-3D-VIEWER.md` §"Authoring/QA preview tool".*
