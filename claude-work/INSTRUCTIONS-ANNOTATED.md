# Annotated Assembly Instructions

*Source: `source/transcriptions/instructions.md` — James Smith Rudolph,*
*Make Your Own Working Paper Clock* (Harper & Row 1983; Perennial 2003 reprint), pp. 34–40.

*Annotated: 2026-05-10, Cowork session `2026-05-10-1040_cowork_guided-assembly-design.md`.*
*Purpose: permanent reference for guided-assembly design; eliminates re-reading the source
on each relevant session. Cross-references use our 3-digit piece IDs throughout.*

---

## Annotation Legend

| Tag | Meaning |
|---|---|
| `[RULE]` | A general rule that applies across all assembly steps |
| `[STEP type]` | A discrete assembly action — type is one of: `add-piece`, `fold`, `glue-self`, `glue-cross`, `glue-no` (explicit do-not-glue), `lock-shape`, `insert-axle`, `install-bearing`, `snap-connection`, `lock`, `check`, `orient`, `string`, `fill`, `pin` |
| `[GRAPH]` | Cross-reference to connection-graph.json edges |
| `[GAP]` | Something the book does not specify — requires authoring judgment or human calibration |
| `[HUMAN]` | Requires Alan's eyes or hands — can't be derived from text |
| `[WARN]` | An explicit caution in the book |
| `[MECH]` | A mechanical/functional constraint or relationship |
| `[ORDER]` | Sequencing constraint — this must happen before or after something else |

---

## §I. General Directions

### §I.A — The Letter-Label System

> *To make any individual piece, spaces on that piece bearing identical letters should be
> glued together.*
>
> *Certain spaces on some pieces are labeled with a letter and a number. This means that
> the space with that letter on the piece with that number should be glued there.*
> **Example:** On piece 3, the space marked "b₄" should be covered by space "b" of piece 4,
> and glued together in that position.

`[RULE]` Two connection types exist in the book's notation:

1. **Same-piece self-attachment** — identical letters on the same piece, glued together after
   folding. In our SVG schema these are closure-form landing markers:
   `landing-<panel-id>` (e.g., `landing-aa`, `landing-taba`).

2. **Cross-piece attachment** — `letter + number` notation (e.g., "b₄") meaning: the space
   marked "b" on piece 4 goes here. In our SVG schema the receiving piece has
   `landing-b4` in `<g id="marks">` and piece 4 has a corresponding attach point or tab-b.
   The connection graph encodes these as directed edges with `tab` and `letter` fields.

`[RULE]` The letter labels on the pieces themselves are the primary guide; the prose
instructions only call out special cases. The connection graph is the digital equivalent of
reading all the letter labels off all 123 pieces.

---

### §I.B — Cutting and Folding

> *Broken lines (- - - -) indicate where you should fold away from yourself.*
> *Lines indicated like this (+ + + + + + +) are those that you should fold toward yourself.*
> *Score the line accurately and lightly with the dull side of your X-acto knife.*
> *On the blank side of the paper, make small pin holes on each end of the line to locate
> scoring lines.*

`[RULE]` Fold direction mapping to our SVG layers:

| Book notation | Physical direction | Our SVG layer |
|---|---|---|
| Dashed `- - -` | Fold **away** from yourself (piece faces away) | `folds-valley` |
| Plus `+ + + + +` | Fold **toward** yourself (piece faces you) | `folds-mountain` |

`[RULE]` Score before folding. This is a physical step with no digital equivalent, but it
establishes that the fold line is the exact authored path in the SVG — not an approximation.

`[GAP]` The book never specifies fold angles in degrees. Every fold step requires
`[HUMAN]` visual calibration against the scans and figures.

---

### §I.C — Gluing

> *Use latex glue. Spread it thinly and avoid heavy build-ups. Let each piece dry
> thoroughly after it is glued.*

`[RULE]` Dry state is a hard prerequisite. In the guided assembly, every `[STEP glue-self]`
and `[STEP glue-cross]` is followed by an implied `[STEP lock-shape]` that must complete before
the next attachment step begins.

`[RULE]` Thin application — glue that builds up at joints will cause pieces to misalign.
In the viewer, this is modeled by snapping to connection point exactly (zero-gap), not
by leaving offset.

---

### §I.D — Mounting (THE CORE SEQUENCING RULE)

> *Each piece or part of a piece should be folded, glued, and allowed to dry before it
> is attached to another piece. Assembly of the various pieces should be done in strict
> numerical order, and only when the different pieces of the element you are constructing
> have been folded and glued.*

`[RULE]` This is the template for every piece throughout the entire build:

```
add-piece → fold (all folds) → glue-self (self-connections) → lock-shape
→ snap-connection (to growing assembly) → glue-cross → lock-shape
→ next piece
```

`[ORDER]` Strict numerical order within each section (A–F). Do not skip ahead.

`[RULE]` "Folded and glued" means self-contained first. A piece is not ready to join the
assembly until all its own folds are set and its own self-connections are glued and dry.
This is the physical reason the guided mode must include fold steps per piece, not just
snap steps between pieces.

---

### §I.E — Axles

> *Axles can be made of pieces of wire or paper clips that have been carefully straightened.*
> *The axle of the motor wheel and the axle of the minute hand should be fashioned from a
> No. 1 U.S. knitting needle, or a similar needle of a diameter of 2 mm.*
> *Bearings can be fashioned from glass, wood, or plastic beads. These beads should be
> glued in or wedged in at the points marked +.*
> *These bearings should not permit excessive play of the axles, but even more important,
> they should not squeeze the axles. It is essential that the bearings be placed in the
> exact center of the moving parts. The axle holes marked + do not require a bearing.
> These axles [are] stationary at these points.*

`[RULE]` Two axle materials:
- **Standard axles:** straightened wire or paper clips — used for middle wheel, escapement
  wheel, anchor, hand mechanism
- **Heavy axles (2mm knitting needle):** motor wheel + minute hand only

`[RULE]` Two hole types in the book:
- **`+` marked holes:** require a bead bearing; axle rotates here; bead glued/wedged in,
  centered exactly; must not squeeze axle
- **Non-`+` holes:** axle is stationary (fixed); no bearing

`[RULE]` The `+` marks in the book correspond to axle holes in the SVG `<g id="axles">`
layer. The distinction between rotating and stationary axle points is carried by whether
a bearing is specified.

`[MECH]` Bearing fit is a functional constraint, not just assembly: too tight = axle won't
turn; too loose = wheel wobbles and clock won't keep time.

`[ORDER]` Pre-drill center pin holes in: **027, 028, 033, 047, 048, 049, 050, 051, 057,
062, 064, 065, 067, 069, 087, 088, 089, 090, 091, 092, 104, 106, 120** — all before
assembly begins. This is called out in §II.A and applies before any piece is attached.

---

## §II. Construction

> *Assembly of the following five elements of the clock should be made in the strict
> numerical order of the components.*
> A. Framework and wall bracket
> B. The mechanism (three wheels + weight)
> C. The anchor and the pendulum
> D. Mechanism of the hands
> E. The weight
> F. The face and the case

`[RULE]` Sections A → F are the top-level assembly order. Never start a section before
the previous section's pieces are fully assembled, glued, and dry. (Exception: §II.A
instructs you to leave the mechanism assembly slot open — "The mechanism is assembled in
place after the entire framework is glued together.")

*(Note: The book says "five elements" but lists six (A–F). This is preserved as printed.)*

---

## §II.A — The Framework

**Pieces:** 001–022 (framework) + 023–026 (wall bracket) + 029–032 (hand-wheel mount)

**Referenced in figures:** Fig. 1 (frame, includes 029–031 for context), Fig. 2 (pendulum
support detail: 018, 019, 027, 028), Fig. 3 (wall bracket: 023–026), Fig. 4 (hand-wheel
mount: 029–032).

> *Cut, glue, and assemble following the general directions above.*

`[GAP]` The book gives no piece-by-piece sequence within §II.A beyond "numerical order."
Every piece 001 through 032 follows the §I.D template: fold → glue-self → dry → attach
→ glue-cross → dry. The connection graph and authored SVGs provide the specific tab/landing
pairings the prose omits.

> *Piece 3 hangs from the forward arms of the wall bracket (Fig. 3).*

`[STEP snap-connection]` Piece **003** attaches to wall bracket (pieces **023**–**026**);
specific connection via tab/landing labels on pieces.
`[GRAPH]` Edge(s) from 003 to wall bracket pieces not yet authored (partner pieces
023–026 are `status: pending`).

> *Pieces 31 and 32 are to be glued back to back and then inserted without glue into the
> slot between pieces 29 and 30 (Fig. 4).*

`[STEP glue-cross]` **031 + 032** glued back-to-back as a combined unit first.
`[STEP glue-no]` The combined 031/032 unit then slides into slot between **029** and **030**
**without glue** — it must be removable (see §II.D: this tongue is what locks the hand
wheels in place and needs to be re-seated when installing them).
`[ORDER]` 031/032 are installed after 029/030 are in place, but the mechanism (§II.B)
and hand wheels (§II.D) must be installed before 031/032 are finally seated.

> *The mechanism is assembled in place after the entire framework is glued together.*

`[ORDER]` **Do not start §II.B until all of §II.A (001–032) is fully glued and dry.**

> *Locate pieces 27, 28, 33, 47, 48, 49, 50, 51, 57, 62, 64, 65, 67, 69, 87, 88, 89,
> 90, 91, 92, 104, 106, and 120 and make a small pin hole in the center of each as
> indicated, so that you can locate the exact center on the reverse side and insert the
> axles later.*

`[STEP pin]` Pre-drill before assembly: **027, 028, 033, 047, 048, 049, 050, 051, 057,
062, 064, 065, 067, 069, 087, 088, 089, 090, 091, 092, 104, 106, 120**.
`[ORDER]` This must happen while the pieces are still flat, before any folding or
attachment. In the guided assembly, this is step zero for each of these pieces (before
even the first fold step).
`[HUMAN]` The pin hole must be at the exact center of the marked point — a visual judgment.

---

## §II.B — The Mechanism

### Motor Wheel (033–049)

**Figures:** Fig. 5 (motor wheel detail), Fig. 6 (tooth strip placement), Fig. 7 (pulley
and rewinding).

> *When cutting out pieces 33 and 36, cut around the perimeters first and then remove
> the excess paper between the teeth.*

`[STEP fold/cut]` **033, 036**: perimeter cut first, then teeth. (Physical cutting step;
no digital equivalent, but the SVG cutout layer encodes this geometry.)

> *The tabs of pieces 33 and 36 should be lined up so that pairs of teeth are directly
> opposite each other, thereby permitting each tooth from piece 37 to be extended from
> one tab to its corresponding member on the other piece.*

`[STEP snap-connection]` **033** ↔ **036**: tabs align tooth-to-tooth. Piece **037** (tooth
strip) bridges each tab pair — one strip per pair.
`[WARN]` Must be placed with precision — misalignment throws the wheel out of balance.
`[WARN]` Weight pieces down with a rigid book while glue dries to prevent warpage.

**Pulley sub-assembly (detailed):**

| Step | Action |
|---|---|
| `[STEP fold]` | **039**: accordion-shaped, fold closed and glue |
| `[STEP glue-cross]` | **039** → **038** as indicated |
| `[STEP fold]` | **040**: form cylinder (glue ends together) |
| `[STEP glue-no]` | Apply glue inside **040**, slip over **039** with arrow toward motor wheel |
| `[STEP glue-cross]` | Glue marked end of **041** to **040** — match a-to-a, b-to-b |
| `[STEP glue-no]` | Roll other end of **041** around cylinder **without gluing** |
| `[STEP glue-cross]` | Cover rolled end of **041** with **042**; arrow toward motor wheel |
| `[STEP glue-cross]` | **043** + **044** form throat (see Fig. 13) |
| `[STEP glue-cross]` | Wrap **045** around cylinder between **043** and **044**, glue |
| `[STEP glue-cross]` | **046** + **047** back to back, then attach to exposed end of **039** |
| `[WARN]` | Keep glue away from **042** — it must turn freely |
| `[STEP glue-cross]` | **048** (double cardboard) attached to pulley end |
| `[STEP glue-cross]` | **049** (plate) covers **048** |
| `[STEP glue-cross]` | **038** → **036** (motor wheel) as indicated |

`[MECH]` Pulley mechanism: CW = free (rewinding); CCW = **041** catches between drums,
drives motor wheel. **042** must rotate freely or the ratchet fails.

---

### Middle Wheel (050–057)

| Step | Action |
|---|---|
| `[STEP glue-cross]` | **050** + **051** back to back |
| `[STEP fold/cut]` | Cut teeth through both pieces following lines on **050** |
| `[STEP glue-cross]` | **052** → **051** |
| `[STEP glue-cross]` | **053** + **054** back to back; remove center section |
| `[STEP glue-cross]` | **053** → **052** |
| `[STEP insert-axle]` | **055** (pinion): push into star-shaped hole in **054**, up against **051** (wheel) |
| `[STEP glue-cross]` | **056**: remove center, slip over **055** |
| `[STEP orient]` | Insert wire through center of **050**; lay flat on table |
| `[STEP glue-cross]` | Apply glue to end of **055** and top of **056** |
| `[STEP glue-cross]` | **057** on wire; press against **055**; lift **056** against **057** |
| `[STEP check]` | Spin on wire before glue dries — verify no eccentricity |
| `[HUMAN]` | Adjust **057** before glue dries to correct any wobble |

---

### Escapement Wheel (058–064)

| Step | Action |
|---|---|
| `[STEP glue-cross]` | **058** + **059** back to back — do this **before** cutting teeth or center hole |
| `[STEP fold/cut]` | Cut teeth and center hole through both |
| `[STEP insert-axle]` | **060** (pinion): hold with arrow pointing away; push through star hole in **058** until **058** is exactly between dotted lines on **060**; teeth must point in direction shown in Fig. 11; wheel must be perfectly perpendicular to pinion |
| `[STEP glue-cross]` | **061, 062, 063, 064**: same method as middle wheel (055–057) |

`[HUMAN]` Perpendicularity of the escapement wheel to its pinion is critical — visual
check required.

---

### Mounting the Wheels

> *See the drawing of pieces 107 for the dimensions of the axles.*
> *First, pass the axle of the middle wheel through the holes of the frame and turn the
> wheel gently to make sure the wheel turns true. Then pass the axle of the motor wheel
> (the knitting needle) through the holes in the frame, and check to be sure the teeth of
> the motor wheel engage the pinion of the middle wheel.*

`[ORDER]` Middle wheel axle inserted **before** motor wheel axle.

`[STEP insert-axle]` **Middle wheel** axle: wire or paper clip, through frame holes.
`[STEP check]` Turn gently — must run true with no wobble.
`[STEP insert-axle]` **Motor wheel** axle: 2mm knitting needle, through frame.
`[STEP check]` Verify motor wheel teeth engage middle wheel pinion.

> *If the pieces of the wheels have been cut accurately, the gears will mesh without
> further adjustment. If the gears mesh too tightly or too loosely, enlarge the axle
> holes in the frame slightly.*

`[HUMAN]` Mesh fit is a tactile judgment. The fix is enlarging frame axle holes — a
physical step with no digital equivalent.

> *Cut cardboard squares like piece 120, shown as a model. Pierce the center of the
> square with the axle, and after spreading glue on one side of the square, position it
> on piece 4 or piece 10 in the appropriate place. Before the glue dries, raise or lower
> the axle until the gears mesh properly and the wheels turn without resistance.*

`[STEP glue-cross]` **120** (cardboard bearing square): glue to **004** or **010**;
position with axle before glue sets.
`[HUMAN]` Axle height is adjusted by raising/lowering before glue dries. This is the
primary vertical alignment control for gear mesh.
`[WARN]` Better if gears mesh slightly too loosely rather than too tightly.
`[WARN]` Don't turn the wheels fast.

---

## §II.C — The Anchor and the Pendulum

**Pieces:**
- Anchor: **065, 066, 067, 068, 069**
- Pendulum: **070** (rod), **071** (square ring), **072** (blade)
- Bob casing: **093** (×6 pieces → 3 braces), **094** (casing), **095**
- Bob holder: **097, 098**

**Figure:** Fig. 9 (anchor assembly), Fig. 10 (bob casing with braces), Fig. 11 (anchor/
escapement wheel relationship).

> *Assemble the anchor, pieces 65, 66, 67, 68, and 69.*

`[RULE]` Per §I.D, strict numerical order: each piece folded/glued/dry before attaching
to the next. The sequence is:

**065:**
- `[STEP add-piece]` Bring **065** (anchor side panel A) into field
- `[STEP pin]` Pre-drill center pin hole (called out in §II.A pre-drill list)
- `[STEP fold]` Apply all folds on **065**
- `[GAP]` No fold angles specified — `[HUMAN]` set by visual inspection
- `[STEP glue-self]` Glue any self-connections on **065**
- `[STEP lock-shape]` Allow to dry completely before attaching to **066**

**066:**
- `[STEP add-piece]` Bring **066** into field
- `[STEP fold]` Apply all folds on **066**
- `[STEP glue-self]` Glue self-connections
- `[STEP lock-shape]` Allow to dry

**065 → 066:**
- `[STEP snap-connection]` Attach **065** to **066**
- `[GRAPH]` 7 valid attach edges from 065 to 066, letters b, c, d, e, f, g, h
  (raw_ids: attach-b66 through attach-h66). Reciprocal landing edges on 066→065
  confirm the same 7 physical joints. Snap all 7 pairs; the book gives no sub-ordering
  within this set.
- `[STEP glue-cross]` Glue the attachment
- `[STEP lock-shape]`

**067:**
- `[STEP add-piece]` Bring **067** (anchor body/hub) into field
- `[STEP pin]` Pre-drill center pin hole (§II.A list)
- `[STEP fold]` Apply all folds on **067**
- `[GAP]` No fold angles — `[HUMAN]`
- `[STEP glue-self]` Glue self-connections
- `[STEP lock-shape]`

**067 → (065+066):**
- `[STEP snap-connection]` Attach **067** to the 065+066 unit
- `[GRAPH]` 4 valid landing edges from 067 to 069 (letters c, d, e, f). Note: the graph
  records these as 067→069 edges, not 067→065/066. This suggests **067** connects
  directly to **069** once 069 is in place, not to the 065+066 sub-unit. Re-examine
  this when authored SVG geometry for 067 is fully resolved.
  `[GAP]` The specific attachment of 067 to 065/066 is not in current valid edges — either
  the connection is via 069 as intermediary, or 067-to-065/066 edges need authoring.
- `[STEP glue-cross]`
- `[STEP lock-shape]`

**068:**
- `[STEP add-piece]` Bring **068** (the fork) into field
- `[STEP fold]` Apply all folds on **068** — forms the Y-fork shape
- `[STEP glue-self]` Glue self-connections
- `[STEP lock-shape]`

**068 → assembly:**
- `[STEP snap-connection]` Attach **068** to growing assembly
- `[GRAPH]` 3 valid attach edges from 068 to 069: letters g, h, i
  (raw_ids: attach-g69, attach-h69, attach-i69). **068** connects to **069**, not to
  065/066/067 directly.
- `[STEP glue-cross]`
- `[STEP lock-shape]`

**069:**
- `[STEP add-piece]` Bring **069** into field
- `[STEP pin]` Pre-drill center pin hole (§II.A list)
- `[STEP fold]` Apply all folds on **069**
- `[STEP glue-self]` Glue self-connections
- `[STEP lock-shape]`

**069 → assembly:**
- `[STEP snap-connection]` Attach **069** to assembly (connects to both **067** and **068**)
- `[GRAPH]` 069 receives: 4 edges from 067 (landing c/d/e/f) + 3 edges from 068 (attach g/h/i)
- `[STEP glue-cross]`
- `[STEP lock-shape]`

---

**Axle insertion:**

> *Put enough beads on the anchor axle, on both sides of the anchor, to prevent the fork,
> piece 68, from binding against the frame as it swings. Put beads on pieces 65 and 69, only.
> The axle hole in piece 67 should be large enough to permit play.*

`[STEP insert-axle]` Single anchor axle passes through **065**, **067**, **069** (in
that order along the axle).
`[STEP install-bearing]` Beads (bearings) on **both sides** of the full anchor assembly,
seated in **065** and **069** only. Not in **067**.
`[MECH]` **067**'s axle hole is intentionally loose — no bearing, deliberate play allowed.
This is a functional requirement, not an oversight.
`[HUMAN]` Bead count determined by feel: enough to prevent **068** (fork) binding against
frame during swing; not so many that they squeeze the axle.
`[CHECK]` Fork swings freely side to side without contacting frame.

---

**Integration into framework:**

> *The fork, piece 68, passes over the beam, piece 9, of the frame and will swing between
> the wall and the frame.*

`[STEP orient]` **068** (fork) must pass over **009** (beam) of the framework.
`[MECH]` The fork's swing plane is between wall and frame — clearance is a spatial
constraint that can't be verified from geometry alone.
`[HUMAN]` Verify physical clearance after installation.

> *The blade, piece 72, from which the pendulum hangs, is held in place by a horizontal
> pin passing through the hole drawn on the blade, and resting on top of pieces 18 and 19
> on the back of the frame. Pieces 18 and 19 should pinch the blade between themselves.*

`[STEP pin]` **072** (blade) installed via horizontal pin through its hole.
`[STEP glue-no]` **072** is NOT glued — held by pin resting on **018**+**019**, pinched
between them. It must be removable (held by friction/pin, not adhesive).
`[MECH]` The pinch from **018**+**019** is the retention mechanism. Too loose = blade
falls; too tight = pendulum can't swing correctly.

> *Squeeze the lower end of the blade into the slot on the upper end of the pendulum rod,
> piece 70, and glue securely.*

`[STEP glue-cross]` Lower end of **072** → slot on upper end of **070** (pendulum rod).
Glue securely — this joint is permanent.

> *The pendulum rod passes through the end of the fork, piece 68. It must fit between the
> prongs of the fork without binding. If it binds, widen the gap in the fork with your
> X-acto knife.*

`[STEP check]` **070** must pass freely through the prongs of **068** (fork) — no binding.
`[HUMAN]` If binding: widen fork gap with knife. Physical adjustment; no digital equivalent.

---

**Escapement geometry check (functional verification):**

> *With the clock upright and facing you, and holding the pendulum stationary, apply a
> slight pressure to turn the motor wheel counterclockwise. As in Fig. 11, point "a" of
> the anchor should engage tooth "d" no more than 1 to 1.5 mm from the point of the tooth.*

`[STEP check]` `[HUMAN]` Engagement depth: anchor point "a" meets escapement tooth "d"
at 1.0–1.5 mm from tooth tip. Visual measurement required.

> *Then verify the proper operation of the escapement by removing the pendulum and slowly
> moving the fork from side to side. One point of the escapement wheel should pass point
> "a" on the anchor every time the pendulum makes a complete circuit — from one side to the
> other and back again.*

`[STEP check]` `[HUMAN]` Escapement timing verification: one tooth passes per full
pendulum circuit (left → right → left). Must be done slowly by hand before clock runs.
`[MECH]` If escapement fails: raise or lower the anchor axle using the same cardboard-
square method as the gear wheels (§II.B mounting). The anchor axle height is the primary
escapement tuning parameter.

---

**Bob casing sub-assembly:**

> *Glue the six pieces designated 93 together to form three separate braces, which will
> establish and maintain the shape of piece 94 (see Fig. 10). After the glue has dried,
> glue these braces inside piece 94, one in the middle, one five inches above the middle,
> and one five inches below. After assembling pieces 94 and 95, glue piece 95 to piece 94.*
> *Piece 98 should be bowed when glued onto piece 97, so it will hold the pendulum bob in
> place on the pendulum rod, piece 94.*

| Step | Action |
|---|---|
| `[STEP glue-cross]` | Pair six **093** pieces into **three separate** braces (2 pieces per brace, glued together) |
| `[STEP lock-shape]` | |
| `[STEP glue-cross]` | Brace 1 → inside **094** at midpoint of its length |
| `[STEP glue-cross]` | Brace 2 → inside **094** five inches above midpoint |
| `[STEP glue-cross]` | Brace 3 → inside **094** five inches below midpoint |
| `[STEP lock-shape]` | Braces must be dry before closing with **095** |
| `[STEP glue-cross]` | **095** → **094** (closes/completes the casing) |
| `[STEP lock-shape]` | |
| `[STEP fold]` | **098**: bow it (introduce a curve) before gluing — spring tension is intentional |
| `[STEP glue-cross]` | **098** (bowed) → **097** — the bow creates spring force that holds the bob on the rod |

`[MECH]` The three-brace spacing (mid, +5", −5") is a physical measurement — the only
dimension the book gives in inches. **094** is the pendulum rod casing; brace placement
maintains its cylindrical shape over the rod's length.
`[MECH]` **098**'s bow is functional: it must press against the bob to keep it from sliding.
`[HUMAN]` Bow amount is a tactile judgment — enough spring to hold, not so much it makes
the bob impossible to slip on or position.

---

## §II.D — Mechanism of the Hands (073–092a)

**Pieces:** 073–092a

> *Assemble pieces 73, 74, 75, and 76 to produce the wheel of the minute hand.*

**Minute hand wheel (073–077):**

| Step | Action |
|---|---|
| `[STEP glue-cross]` | **076**: form cylinder; glue to fit into hole in **075** (wheel) |
| `[STEP glue-cross]` | Push **077** into **076** to dotted line, glue in place |
| `[STEP fill]` | Fill **077** through half its length with a single piece of cork shaped with X-acto knife |
| `[STEP glue-cross]` | Push **077** into **076** — **077** extends forward and holds minute hand |

**Hour hand wheel (078–080):**

| Step | Action |
|---|---|
| `[STEP glue-cross]` | **078** + **079** back to back; after dry, cut teeth |
| `[STEP fold]` | **080**: form another tube, glue together so it turns freely around **077** |
| `[STEP snap-connection]` | Insert **080** into **078** to dotted lines — **080** holds hour hand (**108**) |

`[MECH]` **080** must turn freely around **077** — the two tubes are the hour/minute hand
drive shafts, concentric.

**Reduction gear (081–087):** Book provides no detailed sub-steps — just "assemble" in
numerical order per §I.D. `[GAP]` Individual step sequence within 081–087 must be
derived from piece geometry and letter labels.

**Pulley for hand mechanism:**

| Step | Action |
|---|---|
| `[STEP glue-cross]` | **089**: two pieces of cardboard same size, sandwiched between **088** and **090** |
| `[MECH]` | **048** (motor wheel pinion, front end) ↔ **089** (hand pulley) via crossed rubber band |

**Final mounting (on framework):**

| Step | Action |
|---|---|
| `[STEP glue-cross]` | **091** + **092** glued in place — separate **004** (front center column) from minute hand wheel and reduction gear |
| `[STEP glue-cross]` | **092a** on top of **091**+**092**; axle holes coincide; narrow end up |
| `[STEP snap-connection]` | Mount minute hand wheel, hour hand wheel, reduction gear onto frame per Fig. 12+13 |
| `[STEP lock]` | **031** (tongue) slipped into slot between **029**+**030** — this is the lock; no glue |
| `[STEP check]` | Wheels must move freely when rotating minute hand either direction |
| `[STEP snap-connection]` | **089** onto back end of minute hand axle |
| `[STEP string]` | Rubber band through **048** and **089** (crossed) |

`[MECH]` The tongue **031** is the retention mechanism for all three hand-drive wheels.
It's removable by design — the hand wheels must be installable and removable for
adjustment. This is why 031/032 are inserted without glue.

---

## §II.E — The Weight (101–106)

| Step | Action |
|---|---|
| `[STEP fold]` | **101**: form tube |
| `[STEP glue-self]` | Glue **101** "a" to "a" |
| `[STEP fold/cut]` | **102**: cut four strips |
| `[STEP glue-cross]` | **102** strips wrapped and glued around **101** |
| `[STEP glue-cross]` | **103**: bottom of cylinder |
| `[STEP glue-cross]` | **104** + **105** + **106**: form lid assembly |
| `[STEP insert-axle]` | Wire: bent per Fig. 107; push through bottom of cylinder, then through lid (before making final hook bend) |
| `[STEP fill]` | Fill cylinder with 10–12 oz of dry sand, lead shot, or nails |

`[HUMAN]` Fill material and amount: 10–12 oz is a range, not a precise spec. The weight
drives the whole clock — more weight = more driving force but more wear.

**String mounting:**

| Step | Action |
|---|---|
| `[STEP string]` | Two strings, 4 ft long, tied around the two separate pulley throats on the motor wheel pulley, glued |
| `[MECH]` | Back string: left side of pulley; front string: right side — these must not be swapped |
| `[STEP lock-shape]` | Wait for string glue to dry |
| `[STEP string]` | Wrap front string around pulley in **clockwise** direction |
| `[STEP string]` | Tie small object to front string end to keep it taut |
| `[STEP string]` | Attach weight to back string (still unwound) |

**Starting the clock:**

| Step | Action |
|---|---|
| `[STEP wind]` | Wind clock: pull front string while supporting weight in left hand |
| `[STEP orient]` | Set hands to correct time |
| `[STEP string]` | Let weight hang |
| `[STEP snap-connection]` | Attach pendulum to rod with hook facing wall |
| `[STEP snap-connection]` | Slip bob onto pendulum with letters facing forward |
| `[STEP check]` | Push pendulum gently in one direction → clock should run |

---

## §II.F — The Face and the Case (110–121)

**Pieces:** 110, 111, 112, 112a, 113, 114, 115, 116 (face frame) + 117, 118, 119 (case)
+ 121 (clock face — not numbered in print; our assigned ID)

**Face frame:**

| Step | Action |
|---|---|
| `[STEP glue-cross]` | Assemble frame from **110, 111, 112, 112a, 113, 114, 115, 116** |
| `[STEP glue-cross]` | Glue frame to exact center of back of face (**121**) |
| `[STEP pin]` | Attach assembly to clock with four pins through dots on **113**–**116** — NOT glue |

`[WARN]` If glue doesn't adhere to glossy back of face, use transparent plastic tape.

**Case:**

| Step | Action |
|---|---|
| `[STEP glue-cross]` | Assemble case from **117, 118, 119** |
| `[STEP snap-connection]` | Lower case onto framework |
| `[STEP pin]` | Hold with pins through "*" marks on **118** and **119** — NOT glue |

`[MECH]` Both the face and case are removable by design (pins, not glue). This allows
access to the mechanism for maintenance and escapement adjustment.

---

## §III. Adjustments

> *Make sure the clock hangs on a vertical wall so that the clock is perfectly vertical.
> Otherwise the strings will jump their throats.*

`[CHECK]` `[HUMAN]` Plumb verification after hanging.

> *If the sound is not regular, move the clock slightly to right or left until it is.*

`[CHECK]` `[HUMAN]` Regular tick-tock sound = correct vertical + escapement function.
This is the final functional verification — if it's ticking irregularly, the escapement
geometry or vertical alignment needs adjustment, not the clock itself.

> *The speed of the clock can be adjusted by sliding the bob. Raising the bob will speed
> up the clock; lowering the bob will slow it down.*

`[MECH]` Bob position = period tuning. This is the only post-assembly user control.
`[HUMAN]` Set to correct period by comparison with a known time source.

---

## Summary: Section → Piece Mapping

| Section | Pieces | Notes |
|---|---|---|
| §II.A Framework | 001–022 | Main frame; strict numerical |
| §II.A Wall bracket | 023–026 | Piece 003 hangs from it |
| §II.A Hand-wheel mount | 029–032 | 031/032 without glue |
| §II.B Motor wheel | 033–049 | Knitting needle axle |
| §II.B Middle wheel | 050–057 | Wire axle |
| §II.B Escapement wheel | 058–064 | Wire axle |
| §II.B Axle mount | 120 | Cardboard bearing square; glued to 004 or 010 |
| §II.C Anchor | 065, 066, 067, 068, 069 | Our current authoring focus |
| §II.C Pendulum | 070, 071, 072 | 072 pinned (not glued) to frame |
| §II.C Bob casing | 093 (×6), 094, 095 | Braces at mid/+5"/−5" |
| §II.C Bob holder | 097, 098 | 098 intentionally bowed |
| §II.D Minute hand wheel | 073, 074, 075, 076, 077 | Cork fill in 077 |
| §II.D Hour hand wheel | 078, 079, 080 | 080 turns freely around 077 |
| §II.D Reduction gear | 081–087 | No detail in text; numerical order |
| §II.D Hand pulley | 088, 089, 090 | Crossed rubber band with 048 |
| §II.D Separators | 091, 092, 092a | Axle holes must coincide |
| §II.D Hands | 108, 109 | Hour and minute hands |
| §II.E Weight cylinder | 101, 102, 103 | 10–12 oz fill |
| §II.E Weight lid | 104, 105, 106 | Wire through before fill |
| §II.F Face frame | 110, 111, 112, 112a, 113–116 | Pinned to clock |
| §II.F Clock face | 121 | Our ID (unlabeled in print) |
| §II.F Case | 117, 118, 119 | Pinned; removable |

---

## Key Gaps (for Guided Assembly Authoring)

| # | Gap | Where | Implication |
|---|---|---|---|
| G1 | No fold angles specified anywhere | §I.B | Every `[STEP fold]` is `[HUMAN]` calibrated |
| G2 | No sub-sequence within §II.A framework (001–022) | §II.A | Derive from numerical order + connection graph |
| G3 | No detail on reduction gear assembly (081–087) | §II.D | Derive from numerical order + piece geometry |
| G4 | 067's connections to 065/066 not in current valid graph edges | §II.C | Either 067 connects via 069, or edges need authoring |
| G5 | Bead count on anchor axle | §II.C | `[HUMAN]` — "enough to prevent binding" |
| G6 | Engagement depth (1–1.5mm) requires physical measurement | §II.C | `[HUMAN]` — no digital proxy |
| G7 | Bob bowing amount for 098 | §II.C | `[HUMAN]` — tactile judgment |
| G8 | Fill weight within 10–12 oz range | §II.E | `[HUMAN]` — functional choice |
| G9 | Bob position for period accuracy | §III | `[HUMAN]` — calibrated against time source |

---

## Connection Graph Coverage (§II.C Anchor Cluster)

Valid edges in `claude-work/state/connection-graph.json` for pieces 065–069:

| From | To | Kind | Letters | Count | Notes |
|---|---|---|---|---|---|
| 065 | 066 | attach | b,c,d,e,f,g,h | 7 | Reciprocal landing edges 066→065 confirm same 7 joints |
| 067 | 069 | landing | c,d,e,f | 4 | 067 receives tabs from 069 |
| 068 | 069 | attach | g,h,i | 3 | 068's attach points on 069 |
| 066 | 068 | landing | j | 1 | 066 receives tab j from 068 |

Missing: any direct edge between 067 and 065/066. Either this joint is mediated through
069 (067 and 065/066 don't touch directly) or it needs authoring in 067's SVG.

*Total valid edges for anchor cluster: 15 directed (7+4+3+1) = 11 distinct physical joints.*
