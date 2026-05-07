# Subtype dictionary

Definition + pieces using it, for every subtype currently in the data. Cross-checked against `INITIAL_STATE` in `tag-pieces.html` (the post-2026-05-06 patch state).

The slug list in `tag-pieces.html`'s autocomplete is the authoritative spelling. The definitions below are reverse-engineered from the pieces using each subtype + the canonical embedded labels and book references — they're descriptive, not prescriptive.

**How to use:** when tagging a piece, scan the relevant character's section, find the subtype whose definition + example pieces best fit what you're looking at. If nothing fits, coin a new slug (lowercase, hyphenated, follow the existing pattern: `<category>-<descriptor>` or `<role>-<location>`).

---

## Frame rails (folded family)

**`frame-rail`** — Folded U-channel running as a structural rail. Long, narrow profile; valley folds along the length form the U; located in the framework section.

Used: 001, 002, 003, 005, 006, 007, 008, 009, 011, 020.

**`frame-rail-axle`** — A frame rail that also bears an axle pass-through. Used for the two long main frame columns that carry the axle hubs for the gear train.

Used: 004 (front center column), 010 (back center column).

**`frame-rail-face`** — A frame rail belonging to the face frame on plate A/E — the front of the case where the clock face mounts.

Used: 110, 111, 112, 112a.

---

## Brackets (folded family)

**`bracket-tab`** — A short folded bracket with at least one tab; typically connects two perpendicular framework members.

Used: 012, 013, 014, 015, 016, 017 (the six byte-identical bracket clones in the framework section).

**`bracket-l`** — An L-shaped folded bracket. Pinches another piece between the L's two faces.

Used: 018, 019 (the back-of-frame brackets that pinch the pendulum blade).

**`bracket-wall`** — A folded bracket destined to mount on a wall-bracket assembly (the unit the clock hangs from).

Used: 021, 022 (022 has a `+` center mark).

---

## Boxes (folded family)

**`box-cross`** — Folded development of a small cross-shaped box. Cross-form lid or end cap.

Used: 029 (connects 4 and 10).

**`box-small`** — Folded development of a small generic box; no specific functional pattern beyond "small box."

Used: 030.

**`box-wall-bracket`** — Folded development that becomes part of the wall-bracket box (the assembly that mounts the whole clock to a wall).

Used: 023, 024 (developments that tab into 25), 025 (the tall main panel that receives tabs from 23/24).

**`box-anchor-bearing`** — Folded box that holds the anchor's axle bearing. *(folded-axle character because the bearing axle passes through.)*

Used: 069 (`+` center mark = axle landing).

**`box-case-top`** — Folded development of the case top. Typically with chamfered corners and a central front-locating tab.

Used: 117.

**`triangle-spacer-motor`** — Folded triangle-shaped spacer between the two motor-wheel discs. Folds onto itself; could be read as a folded box but kept as plain folded with this subtype because the shape is unambiguous.

Used: 035.

---

## Tubes (folded family)

Tubes are folded developments that become cylindrical (or near-cylindrical) when assembled.

**`tube-pulley`** — Folded cylinder forming the pulley body. Glue the ends together; slip over the pulley's string-wind shaft.

Used: 040 (slip over 39 with arrow toward motor wheel).

**`tube-pulley-drum`** — Folded cylinder forming the pulley drum, covering the wrapped end of the string-wind shaft.

Used: 042 (covers wrapped end of 41; arrow toward motor wheel).

**`tube-pulley-string-wind`** — Folded tube whose smooth outer surface is what the weight string winds around. *Not* a teeth strip — the zigzag teeth at edges are anchoring tabs between the motor wheels, not gear teeth.

Used: 034.

**`tube-pendulum-blade`** — Folded development that forms the tube/casing of the pendulum blade.

Used: 066.

**`tube-bob-casing`** — Folded development of the long tapered tube that forms the pendulum bob's outer casing.

Used: 094.

**`tube-weight-cylinder`** — Folded development of the weight cylinder body. Rectangular sheet with multiple horizontal folds that wrap into the cylinder shape.

Used: 101.

**`tube-weight-label-wrap`** — Wide labeled strip that wraps around the weight cylinder (101). The labeled wrap is the visible decoration on the assembled weight.

Used: 102.

**`tube-minute-hand-holder`** — Folded development of the tube that bears the minute-hand pin. The tube IS the bearing — no separate authored axle hole on this piece (axle relationship is captured by the OTHER piece, the minute-hand assembly itself).

Used: 077.

**`tube-strap`** — A short folded strap/strip that wraps around a cylinder or assembly. Generic small wrap.

Used: 045 (between 43 and 44), 076 (small rectangle for minute-hand assembly).

**`tube-wheel-cover`** — Folded strip/tube that covers a wheel face; zigzag tabs glue to the wheel disc.

Used: 052 (covers middle wheel).

**`tube-rolled-pinion`** — Folded sheet rolled into a cylindrical pinion shaft. Distinct from `pinion-mount-*` (which are flat star-cut discs); this is the rolled cylinder that the star-cut discs mount around.

Used: 055 (middle-wheel pinion shaft; pushes through the star-shaped hole in 53/54/56/57), 060 (escapement-wheel pinion shaft).

---

## Teeth strips (folded family)

Teeth strips are folded zigzag strips that wrap around a wheel disc to form gear teeth.

**`teeth-strip-motor`** — Folded zigzag strip forming motor-wheel teeth.

Used: 037 (long thin strip with vertical-hatch).

**`teeth-strip-reduction`** — Folded strip forming reduction-gear teeth.

Used: 082, 083 (reduction-gear stage strips), 085 (rectangular strip with `+++` along length).

**`teeth-strip-hook`** — Thin folded strip that ends in a hook form.

Used: 074 (bottom of plate E; small fragment also visible on H).

**`teeth-strip-accordion-pulley`** — Accordion-pleated strip that wraps into a pulley column (rather than gear teeth).

Used: 039 (glues to 38).

**`teeth-strip-sawtooth-weight`** — Sawtooth gear-teeth strip that wraps around the weight cylinder, forming the ratchet teeth.

Used: 105.

---

## Discs (flat-axle and flat-axle-cutout families)

Discs are flat circular pieces, almost always with an axle. Cutout-or-not is what splits them between flat-axle and flat-axle-cutout — see decision tree in `README.md`.

**`motor-wheel-face`** — Front face of the motor wheel.

Used: 036 (large disc with crown-band of vertical hatching = teeth band; perimeter teeth, no interior cutout → flat-axle), 038 (large disc with central star cut out → flat-axle-cutout).

**`motor-wheel-back`** — Back face of the motor wheel.

Used: 033 (large disc with internal triangle; the triangle is a landing marker for piece 35 on the marks layer, *not* a cutout → flat-axle).

**`escape-wheel`** / **`escape-wheel-back`** — Escapement wheel front / back face. Glued back-to-back before cutting teeth on the perimeter.

Used: 058 (escape-wheel; perimeter teeth, no interior cutout → flat-axle), 059 (escape-wheel-back; partner to 58).

**`middle-wheel`** / **`middle-wheel-back`** — Middle-wheel front / back face. Glued back-to-back.

Used: 050 (middle-wheel-back), 051 (middle-wheel).

**`reduction-gear`** — A reduction-gear disc. May or may not have an interior cutout — character distinguishes (`flat-axle` vs `flat-axle-cutout`).

Used: 081, 084, 086 (no cutout → flat-axle), 087 ("cut out center" → flat-axle-cutout), 103 (small reduction gear; central spiral pattern is decorative on labels/marks layer, *not* a cutout → flat-axle).

**`pulley-disc`** — Pulley/gear-stack disc, no interior cutout.

Used: 088, 089, 090 (speculative tag pending visual confirmation).

**`pulley-plate`** / **`pulley-plate-back`** — Pulley plate front / back; glued back-to-back; has star/pinion cutout in addition to the axle.

Used: 046 (pulley-plate → flat-axle-cutout), 047 (pulley-plate-back; partner to 46).

**`plate-cap`** — Plain disc, no axle, no cutout. Glued to double cardboard.

Used: 048 (no axle hole per pieces.csv), 049 (small disc; also appears on plate G).

**`lid-weight`** — Weight-cylinder lid disc; glued back-to-back with its partner to make a 2-layer lid.

Used: 104, 106 (back-to-back partners).

**`hands-wheel-hour`** / **`hands-wheel-hour-back`** — Hour-hand wheel front / back. Cutouts cut through both layers as a stack (so back inherits the cutouts of the front).

Used: 078 (front), 079 (back).

**`hands-wheel-star`** — Star-shaped hands-assembly wheel. The star is the silhouette outline (visible 5- or 6-pointed star edge), *not* a cutout — unless the piece *also* has a cut-out center, in which case it goes flat-axle-cutout.

Used: 073 (no cut-out center → flat-axle), 075 (has cut-out center → flat-axle-cutout).

**`spacer-disc`** — Small disc spacer; typically glued to 1mm cardboard. Has an axle pass-through (axle inferred from "aligns to piece 4" or similar).

Used: 092 (aligns to piece 4).

**`indicator-bob`** — The bob-position indicator disc. Slides along the pendulum rod (070); the rod-pass-through hole is an axle marker per the sliding-axles convention.

Used: 100.

---

## Pinion mounts (flat-axle-cutout family)

These are the star-cut discs that stack around a rolled-pinion shaft. Always have an axle (the shaft) AND a cutout (the star). The category groups them by which wheel's pinion stack they belong to.

**`pinion-mount-middle`** — Star-cut pinion-mount disc for the middle-wheel pinion stack.

Used: 053, 054, 056, 057.

**`pinion-mount-escape`** — Star-cut pinion-mount disc for the escapement-wheel pinion stack.

Used: 061, 062, 063, 064.

`pinion-mount-motor` and `pinion-mount-hands` exist in the autocomplete but aren't currently assigned to any piece — reserved slots in case the build surfaces a star-cut pinion mount on the motor or hands stacks.

---

## Anchor / pendulum parts (mixed characters)

**`anchor-arm`** — The flat zig-zag anchor arm; pivots on the rear axle. Character: flat-axle.

Used: 065 (`axe R` label = rear axle).

**`anchor-fork`** — The flat anchor fork; passes over a beam piece. Character: flat-axle.

Used: 068 (passes over beam piece 9).

**`plate-anchor-rear`** — The folded rear plate of the anchor; valley folds along all flanges; flap labels a-f. Character: folded.

Used: 067.

**`blade-pendulum`** — The pendulum blade; mounting-pin hole = axle. Character: flat-axle.

Used: 072 (squeeze into 70's slot).

**`ring-square-pendulum`** — Square ring with cut-out center; glue between b/c of piece 70. Character: flat-cutout.

Used: 071.

**`pendulum-rod`** — Long vertical strip serving as the pendulum rod; receives 71 at the bottom; 100 slides along it. The rod itself doesn't have an axle pass-through; pieces that interact with it carry the axle markers. Character: flat.

Used: 070.

**`hook-pendulum`** — Folded pendulum hook outer shape. Glue 96 in the bottom of the hook. Character: folded.

Used: 095.

---

## Bob parts (mixed characters)

**`bob-face`** — Large round flat front face of the pendulum bob. The "apply no glue here" inner rectangle is a glue-zone exclusion (negative zone on the glue layer), *not* a cutout.

Used: 097.

**`bob-retainer`** — Bowed retainer that glues to 97; the bow is the visual outcome of fold-and-glue (not a third state). Character: folded.

Used: 098.

**`bob-brace`** — Inner brace for the pendulum bob; printed as 6 copies, glued in pairs to make 3 laminated braces. Character: flat.

Used: 093 (split into 093a + 093b in the SVG authoring layer; same v2 character/subtype assignment).

**`reinforcement-cardboard`** — Narrow cardboard reinforcement; glue to 1mm cardboard. Character: flat.

Used: 096.

**`crescent-decorative`** — Saw-toothed crescent (decorative trim). Character: flat.

Used: 099.

---

## Frame braces / spacers (mixed characters)

**`face-brace-cross`** — Cross-shaped face-frame brace, no axle, no interior cutout. Character: flat.

Used: 114.

**`face-brace-cross-axle`** — Cross-shaped face-frame brace with an axle hole through it. Character: flat-axle.

Used: 115, 116.

**`face-brace-cross-hole`** — Cross-shaped face-frame brace with a non-axle hole through it. Character: flat-cutout.

Used: 113.

**`spacer-pendulum-support`** — Small flat pendulum-support spacer. *(Lives in framework section, not anchor-pendulum — pieces.csv places it there.)*

Used: 027, 028.

**`wedge-wall-bracket`** — Wedge-shaped flat piece glued to strong cardboard; serves as alignment for the wall-bracket assembly. The visible lines on this piece are alignment-to-case-top marks (marks layer), *not* folds — character is plain flat.

Used: 026.

**`spacer-cardboard`** — Small square spacer; glue to 1mm cardboard.

Used: 091.

---

## Hands

**`hand-minute`** — Minute hand silhouette (solid black); glue on heavy cardboard.

Used: 108.

**`hand-hour`** — Hour hand silhouette (solid black); glue on heavy cardboard.

Used: 109.

---

## Case

**`case-side`** — Flat case-side panel; `*` pin-hole markers; glues to b/c regions on the underside of the case top (117).

Used: 118, 119 (paired; 118 mates with 119's b/c, 119 mates with 118's b/c).

**`face-clock`** — The clock face itself. Tan/brown border, off-white field, numbers 1-12, minute marks. Not numbered in the print — assigned ID 121 for build authoring.

Used: 121.

---

## Misc rings

**`ring-tab-pulley`** — Flat ring with tabs that glue it into one end of a tube. Has interior cutout (the ring's hole). Character: flat-cutout.

Used: 043, 044 (same family).

---

## Other / shape-named

These are the slugs that describe a *shape* rather than a *role* — used when the piece doesn't fit neatly into a functional category.

**`tongue-oval`** — Flat oval/leaf-tongue shape.

Used: 031 (glue back-to-back to 32), 041 (currently pair-tag; pending re-read of instructions about whether it's a flat strip on pulley 40 or a rolled paper shaft).

**`oval-elongated`** — Flat elongated oval shape; pairs with `tongue-oval`.

Used: 032 (pairs with 31).

**`tongue-narrow-hands`** — Narrow tongue piece for the hands assembly; glues on top of 92 and 91 with axle holes coinciding.

Used: 092a.

**`push-tab-wheel`** — Small folded tab that slots into a wheel as a drive engagement. "Push into wheel 78" type pieces.

Used: 080.

**`axle-mount-square`** — Flat-axle small square; serves as an axle-mounting cardboard square. The model for all unnamed mounting squares around the build.

Used: 120.

---

## Unused vocabulary (autocomplete-only)

These slugs appear in the autocomplete but aren't currently assigned to any piece. They're reserved for cases that may surface during tagging:

- **`gear-face`**, **`gear-back`** — generic gear-disc face/back. Use if a disc doesn't fit any of the named wheels (motor / escape / middle / reduction / pulley / hands).
- **`pinion-mount-motor`** — star-cut pinion-mount for a motor-wheel pinion stack.
- **`pinion-mount-hands`** — star-cut pinion-mount for a hands-wheel pinion stack.

If you find a piece that fits one of these, use it. If a fresh case surfaces and none of the existing slugs fit, coin a new one in the per-piece `note` field and we'll formalize at the next pass.

---

*Drafted 2026-05-06 in response to "If I'm being asked to audit or contribute to this in my tagging session, then I would need to know how these subtypes are defined." Lifecycle: this file gets cleared from `to-alan/` once the 123-piece tagging session ships; the substance can fold back into `work/piece_characters_v2.yaml`'s subtype section if the dictionary proves valuable to keep.*
