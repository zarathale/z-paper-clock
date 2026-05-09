# to-alan/gear-train/ — §II.B + §II.D mechanism authoring brief

**Opened:** 2026-05-09
**Driving:** CHARTER §6 commitment #4 (bring authoring to a sustainable rate). Anchor cluster (065–072) shipped as the first end-to-end batch; the gear-train stacks are the next coherent block.
**Stakes:** ~50 pieces, the largest authoring block to date. This brief is the top-down map; per-stack cheat sheets land as separate `to-alan/` drops when each stack comes off the bench.

---

## What this brief is, and isn't

This is **the kinematic + naming map of the gear train** — what the train does, which pieces are in it, what depends on what, what to author in what order, and which pieces will need the optional `function` block in their JSON sidecar (per the "Faithful trace + functional sidecar" decision in CLAUDE.md).

It is **not** a per-piece cheat sheet like `to-alan/cheats/066-068.md`, and per Alan's call no per-stack cheat sheets are coming behind it either. The kinematic map + naming-truth corrections + recommended order are the planning artifact for the gear train; the panel-by-panel authoring lives at the bench against the print, without an intermediate speculation layer.

## Naming truth — corrections to surface up front

Per your directive that the project should show truth, four things didn't survive contact with the sources:

1. **"087 is the escape wheel" is wrong.** Embedded-labels panel F has *"Piece 87 — Reduction-gear disc. cut out: center. No fold lines."* Instructions §II.D: *"Assemble the reduction gear, pieces 81, 82, 83, 84, 85, 86, and 87."* So 087 is the last piece of the reduction-gear stack — kinematically in the display branch (drives the hand mechanism), not the timing branch. The **actual escape wheel is 058 + 059 glued back to back** (instructions §II.B.3, embedded-labels panel F). The "escape wheel" wording in `STATUS.md` SVG-layer-authoring next-action and `QUEUE.md` recently-shipped #1 was inherited from bench shorthand and should be corrected when those files next get a pass — I'll fold the fix into the next planning beat.

2. **"§II.B = the gear train" is wrong.** The book's §II.B Mechanism is *only* the three wheels: motor (33–49), middle (50–57), and escapement (58–64) — 32 pieces. The reduction gear (81–87), the hand-mechanism pulley (88–90), and the minute/hour hand wheels (73–80) are all in **§II.D Mechanism of the Hands**. So the colloquial "gear train" actually spans **§II.B + §II.D** — split across two book sections because the timing chain (B) and the display chain (D) are kinematically separate, joined only by a crossed rubber band between pulley 48 (front of motor-wheel pinion) and pulley 89 (back of minute-hand axle). The brief below treats both as one block because that's how authoring practically goes; just don't be confused that "§II.B" doesn't actually cover all of it.

3. **103 is in the wrong section in `pieces.csv`.** `pieces.csv` row: *"103,E,reduction-gear,,captured,Small reduction gear with central spiral pattern."* Embedded-labels panel E echoes the same description. **But instructions §II.E prose says: "Form a tube from piece 101… Glue in the bottom, piece 103."** That's the weight-cylinder bottom disc. The visual description (small disc with spiral pattern) and the prose role (cylinder bottom) can both be true — a disc with a spiral pattern can absolutely be a cylinder bottom — but the `section: reduction-gear` tag and the "small reduction gear" wording are misleading either way. **Need your bench eye to confirm what 103 actually is.** If it's the weight-cylinder bottom, flip `pieces.csv` row 103 to `section: weight` and rewrite the description. If it actually is a reduction gear and the prose is using "103" inconsistently, flag and we figure out where it really lives.

4. **074 has a similar split.** `pieces.csv`: *"074,E,anchor-pendulum,,captured,Thin strip (hook form) at bottom of plate E; small fragment also visible on H."* Embedded-labels panel E: *"Piece 74 — Thin strip (hook form) at bottom of plate. ---: along length."* **Instructions §II.D: "Assemble pieces 73, 74, 75, and 76 to produce the wheel of the minute hand."** A thin strip with one fold line doesn't read like a wheel piece; the prose may be conflating two different "74"s, or 074 may actually be a strap/registration piece consumed by the minute-hand wheel assembly. **Need your bench eye to confirm.** If 074 is in the minute-hand wheel, flip `pieces.csv` row 074 to `section: hands` and rewrite the description.

These are surfaced as questions, not unilateral renames — both touch source-of-truth files (`pieces.csv`, embedded-labels) and your in-hand visual is the tiebreaker. Once resolved, the corrections roll back into `pieces.csv` + embedded-labels in a follow-up doc-sweep.

## The kinematic chain (what drives what)

Reading the book's §II.B + §II.D + §II.E end-to-end, the chain works like this:

```
[drive weight 101+contents]
        │ (string over pulley 40/41/42 throat)
        ▼
[MOTOR WHEEL stack 33–47]            ← timing chain head
        │ teeth (37) engage pinion (54–57)
        ▼
[MIDDLE WHEEL stack 50–57]
        │ teeth (50/51) engage pinion (60–64)
        ▼
[ESCAPE WHEEL stack 58–64]           ← timing chain tail
        ↑↓ (anchor 065–069 already built — this is where the pendulum gates the train)

[MOTOR WHEEL pinion front: pulley 48]
        │ crossed rubber band
        ▼
[HAND-PULLEY 89 → REDUCTION GEAR 81–87]   ← display chain
        │ drives
        ▼
[MINUTE HAND WHEEL 73–77]
        │ concentric on minute-hand tube 77
        ▼
[HOUR HAND WHEEL 78–80]
        │ tube 80 holds
        ▼
[HOUR HAND silhouette 109]  +  [MINUTE HAND silhouette 108 on tube 77]
```

Three things worth pinning from this picture:

- **Two branches off the motor-wheel pinion.** The back of the pinion drives the timing chain (middle wheel → escape wheel → anchor → pendulum). The front of the pinion drives the display chain via pulley 48 → crossed rubber band → pulley 89 → reduction gear → hand wheels. Same pinion, two outputs, different speeds.
- **The escape wheel is where the timing chain meets the anchor.** The anchor cluster (065–069) is already authored. Once the escape wheel ships, the timing chain has a clean 1-tick = 2π/N(escape) cadence to validate against — the anchor unit per the faithful-trace decision. Everything else in the chain (motor wheel, middle wheel) derives its speed by gear ratio backward from the escape wheel.
- **The hands are paced from the motor-wheel pinion, not the middle/escape branch.** This is why the gear ratios on the display side (pulley 48 ↔ pulley 89, then reduction gear 81–87) matter independently of the timing-chain ratios. The minute hand makes one revolution per hour because of those ratios, not because of the pendulum period.

## Shared axles (per embedded-labels panel E axle legend + prose)

| Axle (material) | Role | Pieces it passes through |
|---|---|---|
| Knitting needle (2 mm) | Motor-wheel axle | Through frame columns 4 + 10; wheel discs 33, 36; pulleys 38, 46/47, 48, 49; pinions 39, 40, 41, 42 |
| Wire | Middle-wheel axle | Through frame; wheels 50/51; pinion 53–57 |
| Wire | Escape-wheel + reduction-gear-stage axle | "axle: wheel 81, 84" per legend = the same axle carries reduction-gear stage 81/84 and (per layout) the escape-wheel pinion. Need to verify against frame geometry. |
| Wire | Anchor axle (already in-place) | Through beam 9; bearings on 65 + 69 |
| Knitting needle (2 mm) | Minute-hand axle | Through frame column 4; minute-hand wheel 75/76; cylinder 77; spacers 91/92/92a; pulley 89 (back end) |
| Wire | Hands' carriage axle | "axle for the hands" per legend; hour-hand wheel 78 + tube 80 turn freely around the minute-hand cylinder 77, so this is concentric, not separate. May be the same axle as minute-hand. Verify. |

The two "Verify" rows are real ambiguities — the panel E legend lists four axle dimensions, but the prose mentions five distinct mechanical axles. Either the legend is a subset (most-common-dimensions only), or one of the "axles" in the prose is actually a tube concentric over another (the hour-hand-on-minute-hand-tube is a known case of this).

The framework pieces 4 + 10 (the long center columns) are the bearing block for almost every gear axle; the cardboard-square pieces 120 are the per-axle mounting that lets you tweak gear engagement. Both already authored / captured — not in scope here, but worth knowing the gear stacks all anchor to them.

## Sub-stack maps

Reading order matches the recommended authoring order at the bottom. Each entry: piece IDs, what the sub-stack does, function-block candidates, anything pre-flag-worthy.

### 1. Motor wheel — pieces 33–49 (17 pieces)

**What it does:** the largest wheel in the clock, driven by the falling weight via a string over the pulley throat. Carries the input torque for both the timing chain and (via pulley 48 on the front of its pinion) the display chain.

**Pieces by role:**

- Wheel proper (front + back faces and the teeth band): **033** (back face, large disc with internal triangle bracing 35), **036** (front face, crown band), **037** (long tooth-strip glued around the crown to form the teeth)
- Tooth-strip braces (zig-zag pieces that fold to engage between 33 and 36): **034**, **035**
- Pulley assembly (the rewinding mechanism — pulley turns one way to wind, locks the other to drive): **038** (large pulley front face), **039** (accordion-pleated pulley column), **040** (cylinder over 39), **041** (pulley shaft), **042** (pulley drum), **043** + **044** (pulley throat), **045** (wrap strip between 43/44), **046** + **047** (pulley plates back-to-back), **048** (rubber-band pulley to hand mechanism — small disc), **049** (cap plate)

**Function-block candidates** (pieces with tooth/diameter values that the M6 mechanism animation would consume):

- **037** — N teeth on the motor wheel. This is the count that sets the whole timing-chain ratio against the middle-wheel pinion.
- **048** — diameter of the rubber-band pulley to the hand mechanism. Pairs with 089's diameter to set the drive ratio into the reduction gear.

Everything else in the stack (33/36 are the structural face plates; 39–47 form the pulley/rewind cylinder) is artifact-faithful only — no `function` block.

**Author-time things to know:**
- Pieces 33 and 36 must be cut so the tab pairs line up — *embedded-labels says "tabs of 33 and 36 lined up so pairs of teeth are directly opposite"*. The teeth-band positions matter for the eventual M6 animation. Worth marking the tab positions explicitly in the SVG (probably as `marks` with ids like `tab-pair-N`) so the function block can reference them.
- Pulley 42 must turn freely on the cylinder formed by 40 — that's the rewinding ratchet. Author 42 with its own `axle` and a clear note in the sidecar that it's a free-spinning element relative to 40, not glued. (This is the same "swing-free element" concept you flagged for the pendulum bob — three things in this clock spin or hang independently of the rest of their assembly: pulley 42, the pendulum bob, and the drive weight on its string. Worth a separate conversation when we get to the physics.)
- The triangle inside 033 is a *brace* for piece 035's cone shape, not a face feature. Authoring it as `marks` with id `brace-35` is probably right; it's a registration/structural reference, not a fold or attach.

### 2. Middle wheel — pieces 50–57 (8 pieces)

**What it does:** couples motor-wheel teeth to escape-wheel pinion. One reduction stage in the timing chain.

**Pieces by role:**

- Wheel proper (large teeth disc, glued back-to-back): **050** (back face), **051** (front face)
- Wheel-side cap: **052** (glues to 51, finishes the wheel face)
- Pinion stack (small star-cut discs that grip the rolled pinion cylinder, transferring torque from the wheel to the next axle): **053** (small disc, panel H — cross-listed), **054** (star-cut, sized for the pinion top), **055** (the pinion proper — rolled cylinder), **056** (star-cut, slips over the pinion mid-length), **057** (star-cut, presses against pinion top — tightens the stack)

**Function-block candidates:**

- **050 (or 051)** — N teeth on the middle wheel. Together with 037's tooth count this sets the motor → middle reduction ratio.
- **055** — N teeth on the pinion. Combined with the next stage (escape-wheel pinion) determines the middle → escape ratio. (Pinion teeth are usually called "leaves" in clockmaking, often 6–8 leaves, much fewer than wheel teeth — that's how reduction works.)

054/056/057 are pure structural — they grip the pinion to the wheel face. No function block.

**Author-time things to know:**
- 050 and 051 are glued back-to-back *before* cutting the teeth — same convention as 058/059 escape wheel. Author them as a paired piece in `pieces.csv` notes (already done — *"glue back to back with 51"*).
- The star-cut discs (054, 056, 057) all have the same hole shape because they all slip over the same pinion cylinder. Probably the same SVG geometry repeated three times with different sidecars — worth checking if a "shared template" pattern is worth introducing.

### 3. Escape wheel — pieces 58–64 (7 pieces)

**What it does:** tail of the timing chain. The escape wheel's tooth pattern is what the anchor (065/067) gates one tooth at a time per pendulum half-cycle. **This is the kinematic anchor for the whole timing chain** — per the faithful-trace decision, one tick = 2π/N(escape) and every other rotation derives from that.

**Pieces by role:**

- Escape wheel proper: **058** + **059** (glued back-to-back before cutting teeth — explicit embedded-labels note)
- Pinion: **060** (rolled cylinder, fan-folded rectangular development with `+++` and `---` alternating)
- Pinion stack (same pattern as middle wheel): **061**, **062**, **063**, **064** (four star-cutout discs that grip the pinion through the wheel)

**Function-block candidates:**

- **058 + 059** — **N teeth** (the master count for the entire timing chain — every other tooth count in the train derives from this). Plus the geometric relationship to the anchor's "a-d" engagement points (per Fig. 11 prose: *"point 'a' of the anchor should engage tooth 'd' no more than 1 to 1.5 mm from the point of the tooth"*). The function block here probably needs both the tooth count AND the engagement-geometry parameter.
- **060** — N leaves on the escape-wheel pinion. Combined with middle-wheel teeth count (050) sets the middle → escape ratio.

061–064 are structural pinion-grip discs. No function block.

**Author-time things to know:**
- The escape wheel mates to the already-authored anchor (065/067/068/069). The anchor cluster has `pivot-anchor` marks on 065/067/069 and a north-orientation cue on the rear plate. Once the escape wheel ships with its tooth count, the next thing is to author the *engagement geometry* — probably as a `marks` element on 058/059 with id `engages-anchor-a` at the point Fig. 11 references, paired with a corresponding `engages-escape-d` mark on 067. That's a connection-graph primitive M4 will read.
- Per the panel E axle legend: middle-wheel axle and escape-wheel axle are listed separately ("axle: wheel 50, 58"). So 050 and 058 share an axle? That contradicts what I'd expect (separate axles for separate wheels). Worth verifying — this might be a mistake in the legend, or they might literally share a wire that runs the full depth of the frame. Looking at Fig. 1 of the embedded labels would help; alternatively your bench knowledge of how the frame holes line up.

### 4. Reduction gear — pieces 81–87 (7 pieces)

**What it does:** display branch. Driven by pulley 89 (which is driven by pulley 48 on the motor pinion via a crossed rubber band). Reduces the rubber-band-driven speed down to the minute-hand revolution rate (1 rev / hour).

**Pieces by role:**

- Stage 1 stack: **081** (star-cutout disc, mates to axle that also carries 084), **082** (accordion strip — one of two; pairs with 083), **083** (accordion strip — pinion development?)
- Stage 2 stack: **084** (star-cutout disc, same axle as 081), **085** (rectangular `+++` strip — accordion fold), **086** (star-cutout disc)
- Stage 3 disc: **087** (the disc you have on the bench — reduction-gear disc, cut-out center)

**Function-block candidates:**

- **081** + **084** — N teeth each (these are the intermediate gear discs in the reduction stages; they pair with whatever pinion strips 082/083/085 form when rolled).
- **087** — N teeth on the final stage; sets the last reduction ratio into the minute-hand wheel.

082/083/085/086 are pinion/strip components — they roll into cylinders or accordion-folded structural elements. The pinion ones (082/083 pair likely; 085 standalone) might need a leaf count if the leaf count matters for the ratio, but more likely they're just transmission elements with no independent tooth count.

**Author-time things to know:**
- 087 is what's currently on your bench. Per the embedded-labels panel F: *"Piece 87 — Reduction-gear disc. cut out: center. No fold lines."* So it's a cut-only piece — no folds, no panels-first complexity. Should be a quick author. The cutout center is the axle hole.
- The "axle: wheel 81, 84" entry in the panel E legend means 081 and 084 share an axle — the reduction-gear stages are stacked on a single shared shaft. This means the pivot-cluster pattern (like `pivot-anchor` on the anchor) applies: author all stage-shared pieces with `pivot-reduction-gear-axle` (or similar) in their `attach-points` so the multi-piece scene assembly co-locates them.

### 5. Hands assembly (your priority) — pieces 73–80, 88–92a (~13 pieces, plus 108/109 silhouettes in §II.D-adjacent §II.F)

**What it does:** display branch endpoint. Takes the reduction-gear output and rotates two concentric tubes — minute hand on tube 77 (knitting-needle-driven), hour hand on tube 80 (concentric over 77, gear-coupled at slower rate). The hands are silhouettes (108 minute, 109 hour) glued to the front ends of the tubes.

**Pieces by role:**

- Minute-hand wheel: **073** (small star-shaped disc, cut-out center), **074** (?? — see naming-truth #4 above), **075** (star-shaped disc, cut-out center), **076** (small rectangular piece, fold lines)
- Minute-hand holder cylinder: **077** (rolled tube — extends forward from 76 to hold the minute hand silhouette)
- Hour-hand wheel: **078** (gear with four sectors — one carries hub label, three are "cut out") + **079** (back-face blank disc, glued behind 078 before cutting teeth)
- Hour-hand holder tube: **080** (rolled tube, concentric over 077, holds the hour hand silhouette; "rear" labeled face)
- Hand-mechanism pulley (driven side of the rubber band, mounted on minute-hand axle): **088** (pulley/gear stack disc), **089** (pulley disc — embedded-labels: *"+ center mark"*), **090** (pulley/gear stack disc)
- Spacers (separate frame column 4 from minute-hand wheel + reduction gear): **091** (small square spacer, glue to 1 mm cardboard), **092** (disc spacer, glue to 1 mm cardboard), **092a** (narrow tongue piece, glues over 92 + 91, axle holes coincide)
- Hand silhouettes (technically §II.F, but kinematically downstream of the hands assembly): **108** (minute hand), **109** (hour hand) — both solid black silhouettes glued on heavy cardboard, no folds.

**Function-block candidates:**

- **078** — N teeth on the hour-hand wheel. The hour-hand-wheel-to-minute-hand-pinion ratio is fixed at 12:1 (one hour-hand rev per twelve minute-hand revs); whatever tooth counts produce that ratio is what's printed.
- **073 / 075** — N teeth on the minute-hand wheel (probably the same since they're both star-shaped wheels in the assembly).
- **089** — diameter of the rubber-band pulley on the minute-hand axle. Pairs with 048's diameter to set the motor-pinion → minute-hand drive ratio.

Spacers 091/092/092a, the holder tubes 077/080, and the silhouettes 108/109 are all artifact-faithful only.

**Author-time things to know:**
- The hour-hand wheel 078 has *"three sectors marked 'cut out' (the fourth carries a hub label)"* per embedded-labels — so it's a four-sector wheel with three sectors cut away to leave a thin spoke pattern. Authoring this: silhouette + 3 cutouts (`cutout-1/2/3`) + 1 axle in the central hub. The "hub label" sector is where the axle is centered and remains solid.
- 092a's connection labels are interesting: per embedded-labels *"a₁₀₀, d₁₀₀, b"* — references piece 100 (the pendulum-bob position disc). Need to confirm what 92a actually attaches to; it sounds like it's a cross-piece between the hands assembly and *something* on the pendulum bob, which is mechanically odd. Possibly a mislabeled `a`/`d` reference; possibly a real bridge piece. Bench eye needed.
- 077 + 080 are concentric tubes. Authoring as paired pieces with shared axle, with `attach-points` like `concentric-77` on 080 to indicate the geometric relationship. The hour hand turns *around* the minute hand.

### 6. Escape wheel revisited — relationship to the anchor

Already covered in stack 3 above; surfacing again because once the escape wheel ships, the **first end-to-end mechanism animation becomes possible**: a slider that ticks the escape wheel one tooth at a time and rotates the anchor accordingly. That's not M6 yet, but it's the first concrete proof that the function-block pattern works. Worth pre-thinking what the demo would look like in `preview.html` — probably a multi-piece scene of `[anchor cluster] + [escape wheel 058+059+060+061-064]` with a "tick" button driving the rotation forward.

## Function-block schema reminder

Per the *"Faithful trace + functional sidecar"* row in `CLAUDE.md`'s Architectural Decisions: each piece's `NNN.json` sidecar may carry an optional top-level `function` block. Populated only for pieces in the timing/drive chain — roughly the 13–18 pieces called out as function-block candidates above.

The exact schema isn't fully specced in `SPEC-3D-VIEWER.md` yet (the sidecar schema section there sketches the broader sidecar but doesn't lock the `function` shape). Proposed shape based on the decision row's content:

```json
{
  "function": {
    "type": "wheel" | "pinion" | "pulley" | "engagement",
    "teeth": <int>,                         // for wheel/pinion
    "diameter_mm": <float>,                 // for pulley
    "drives": ["057", "060"],               // ids of pieces this engages
    "driven_by": ["037"],                   // ids of pieces that engage this
    "engagement": {                         // for the escape-wheel + anchor pair
      "tooth_label": "d",
      "anchor_point_label": "a",
      "clearance_mm": 1.0
    }
  }
}
```

This is a draft — the actual lock-in should happen the first time you author a function block at the bench (probably for 058/059, the escape wheel, since it's the master of the chain). I'll bring a more concrete schema CODE_PROMPT (or just a hand-written schema settled in chat) when you're ready to start populating one.

## Recommended authoring order

Per your priority direction (hands before drive weight, after reduction gear stack), and respecting kinematic dependencies:

1. **Motor wheel (33–49)** — large stack but it's the input to everything; getting it shipped unblocks both branches. The wheel proper (33/36/37) plus the pulley assembly (38–47) plus pulleys 48/49 are mostly cut-only or simple-fold pieces, faster per-piece than the anchor cluster was.
2. **Middle wheel (50–57)** — small stack (8 pieces), mostly small star-cuts + the rolled pinion. Probably one bench session.
3. **Escape wheel (58–64)** — small stack (7 pieces), same shape as middle wheel. Once this ships, the first function-block conversation becomes concrete and the escape-wheel + anchor demo becomes possible.
4. **Reduction gear (81–87)** — 7 pieces, all small. 087 is already underway on your bench so this stack has natural momentum.
5. **Hands assembly (73–80, 088–092a, 108, 109)** — your priority. ~13–15 pieces depending on how 074/092a sort out. Once shipped, the display branch is end-to-end and the **whole gear train becomes one connected scene** in `preview.html` (motor wheel → middle wheel → escape wheel → anchor → pendulum on the timing side; motor wheel → pulley → reduction gear → minute-hand wheel → hour-hand wheel on the display side).
6. **Drive weight (101–106)** — out of scope for this brief but the next thing after hands. §II.E. Includes the resolution of 103.

Alternative ordering if a stack gets blocked: motor wheel and middle wheel are kinematically coupled (motor's teeth engage middle's pinion), so they're nice to do back-to-back for the verification value. Reduction gear and hands are similarly coupled (reduction drives the minute-hand wheel directly), so doing them as a pair is natural. Escape wheel can slot in either before or after the reduction-gear/hands pair without dependency loss — it ties to the already-authored anchor, which is its own self-contained subgraph.

## What I'm not including (and why)

- **Per-piece cheat sheets** — explicitly out of scope per Alan's call. The 066–068 sheet's value was the open-questions sections naming what *I* couldn't guess from book + label data; for the gear train Alan operates from the print + this brief without the speculation layer.
- **Drive weight (§II.E, 101–106)** — out of scope for the gear-train block. Comes after hands per your priority, and is mechanically distinct from the gear train (it's the input to the chain, not part of it). Will get its own brief.
- **Hand silhouettes 108/109** — listed in the hands stack above for completeness because they're kinematically downstream of the hands assembly, but they're trivial to author (solid black silhouettes, no folds, no panels). Mention them in the per-stack cheat sheet when hands come up; no separate brief needed.
- **Free-swinging-element physics** (pulley 42, pendulum bob, drive weight on string) — separate conversation, your call on timing. The brief above flags the three pieces that will need this thinking; the actual model is its own design beat.
- **Frame mounting + axle-hole geometry** — pieces 4, 10, 120 are already authored or captured. The gear stacks bolt onto these via the axle-mount squares (120 is the model). Won't author against them in this brief, but they're the "ground" the chain hangs from.

## Verifies via

This is a planning brief, not a per-piece authoring task — there's no "this lands" checkpoint. Three things I'll watch for as you work through the stacks:

1. **`pieces.csv` corrections** for 074 + 103 (and probably section reorg for 081–087 → `hands-mechanism` or stay `reduction-gear` once we settle whether `reduction-gear` is its own bucket or a sub-bucket of hands).
2. **First function block landing** — probably on 058/059 once the escape wheel ships. That's the moment we lock the `function` schema for real.
3. **Connection graph growth** — every new piece authored panels-first with `attach-points` adds edges to `connection-graph.json`. After the motor wheel lands I expect `pivot-motor-wheel-axle` to start showing up as a new pivot cluster joining motor/pulley/pinion pieces; same pattern as `pivot-anchor` joins 067+069. By the time all five stacks are authored, the full chain should be one or two connected components in the graph.

## Feedback I want from you

- **Order priority within a stack:** I've recommended motor wheel first because it unblocks both branches, but if any other stack feels more natural to start with at the bench (e.g. escape wheel because it's small and high-value for the function-block conversation), say so and I'll re-sort.
- **The 074 + 103 + "087 = escape wheel" corrections** — agree these should land in `pieces.csv` + embedded-labels + STATUS/QUEUE? Or want me to dig further before we touch source-of-truth files?
- **Function-block schema draft** — does the JSON shape above look right? Want a more rigorous proposal as its own design beat, or settle it informally at the bench when you author the first one?
- **Brief length** — this is ~330 lines vs. 066-068's ~140 lines for two pieces. The per-stack maps are the bulk of it. Acceptable for a once-per-block planning brief, or compress further?

---

*Created 2026-05-09 from cowork session 2026-05-09-XXXX_cowork_gear-train-brief.md (forthcoming at session-close). Stand-alone planning brief — no per-piece cheat sheets follow; refine the format per Alan's reaction before producing the next-block equivalent for the drive weight + face/case.*
