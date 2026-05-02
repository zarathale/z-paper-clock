---
date: 2026-05-02
start_time: "23:30"
end_time: "00:15"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Add axle-driven rotation to `preview.html`: pieces with an axle point should be rotatable around that axle in the 3D model window, as though sitting on a physical axle. Render the axle itself visibly so it reads as a fixed wire that the piece pivots on, sized and styled to match the eventual physical build (thin steel wire, ~1 mm diameter). Structure the implementation so a future bearing (knitting-needle segment glued to the piece, rotates with it, axle wire passes through) slots in cleanly later.

## What was done

Five changes to `preview.html`. All shipped end-to-end in this session — no CODE_PROMPT handoff needed (small surgical addition, well-scoped).

**1. New "Rotation" UI section.** Side panel gains a Rotation slider (−180° to +180°, step 1°, default 0°), value readout in degrees, and a "Reset rotation" button. Mirrors the existing Thickness section's styling. Hidden by default via `hidden` attribute; un-hidden in `renderScene` when the loaded piece has at least one axle parsed.

**2. Pivot Group wraps the slab.** The slab from `buildSlab` is now added as a child of a `THREE.Group` "pivot" instead of directly to the scene. The pivot sits at the active axle's world position, and the slab inside has a compensating local offset so visually nothing moves at rotation = 0. Setting `pivot.rotation.z` then swings the slab around the axle line (Z-axis through the axle point — perpendicular to the slab, matching how paper-clock pieces sit on their physical wire axles). Single-axle assumption per Alan's design call: `axles[0]` is the active rotation axle. Multi-axle support deferred until a piece actually surfaces with multiple axles in §II.B.

**3. Axles render as silver wires.** Replaced the magenta sphere markers with `THREE.CylinderGeometry` cylinders, 1 mm diameter (0.5 mm radius), oriented along the Z-axis (perpendicular to slab). Length = `slabT + 2 × overhang` where `overhang = 4 mm`, so the wire visibly pokes through both the front and back face of the slab regardless of thickness slider position. Material: `MeshStandardMaterial` with `metalness: 0.9, roughness: 0.25, color: 0xc8cdd0` — reads as shiny silver under the existing scene lighting. Code lives in a new `buildAxleWire(axleX_3js, axleY_3js, slabT_mm)` helper above `renderScene`.

**4. Wires are world-anchored, not pivot-children.** Wires sit OUTSIDE the rotation pivot Group, attached directly to the scene. They do NOT rotate when the slab rotates — matching the physical clock: the wire is a fixed shaft mounted in the framework, and the piece (with its glued-on bearing, eventually) rotates around it. The structural separation also future-proofs cleanly for bearings: a `buildBearing(...)` paired with `buildAxleWire` and added INSIDE the pivot Group will render the knitting-needle bushing — hollow tube around the wire, glued to the piece, rotating with it.

**5. Slider event wiring + state.** `rotateSlider`'s `input` event updates `pivot.rotation.z` in place (no geometry rebuild, no debounce — much cheaper than thickness rebuilds) and calls `requestRender()`. `resetRotateBtn` snaps the slider and pivot to 0°. `loadSVG` resets the slider to 0° on every new file load; the thickness rebuild path (`debouncedRebuild` → `renderScene`) preserves whatever the slider is currently at, so an in-progress rotation doesn't jump when the user tweaks thickness mid-rotation.

**Renames** (non-behavioral): `currentSlabGroup` → `currentSlabPivot` (the variable now holds the pivot Group, not the bare slab); `currentAxleMarkers` → `currentAxleWires`. Both `replace_all` against `preview.html`.

**Files touched.** `preview.html` only.

## Continued — orientation cue / `north` marker

Alan flagged the orientation-cue question mid-session ("we need a convention for me to include in authoring the svg to cue to the orientation... which way is 0°?") then proposed a clean form for it ("place a dot/shape/centroid on the piece in the axle layer that gets used as the anchor. perhaps label the piece 'north' or 'anchor'... that grounds as 0°"). Both choices answered via AskUserQuestion: marker id = `north` (avoids conflict with the clock's anchor escapement part name), slider sign = CW positive (clock convention).

Convention settled (added to CLAUDE.md Architectural Decisions + File Naming Conventions):

- **Layer:** existing `<g id="axles">` (no new layer).
- **Marker:** an optional single element with `id="north"`. Type = ellipse / circle / rect / path — anything `elementCentroid()` parses (ellipse/circle via `cx,cy`; rect via bbox midpoint; path via mean of sampled vertices).
- **Semantics:** vector from the active axle (`axles[0]`) to the north marker's centroid defines the +0° direction. Slider 0° = piece-as-authored; the marker visualises which way "0°" points.
- **Optional:** pieces without it still rotate, just no orientation cue rendered. North-without-axle is banner-warned and ignored.
- **Sign:** +deg = CW when viewed from the front (clock convention). three.js's `rotation.z` is CCW-positive, so the slider handler and `renderScene` apply-rotation block both negate.

Implementation in `preview.html`:

- New `elementCentroid(el)` helper at module scope (used for north; mirrors logic that exists inline in the root parser, kept duplicate for now to minimise churn).
- `parseSVG` axles block detects `id="north"` first via `querySelector('[id="north"]')`, parses its centroid, then proceeds with the existing axle ellipse/circle pass excluding any element id'd `"north"`. New `north` field on the parsed object.
- `renderScene` renders the north marker as a small brass-gold sphere (R = 1.0 mm, color 0xb89e5b, metalness 0.7, roughness 0.35) INSIDE the rotation pivot Group at the marker's local position relative to the active axle. Disposed automatically via the existing `currentSlabPivot.traverse()` teardown pass.
- Sign flip applied at both the slider's `input` handler and in `renderScene`'s post-build apply-rotation block, so reload + drag both honour CW-positive.

Banner messages:
- `north marker found but its centroid could not be parsed.` — when the element exists but is an unrecognised tag or has malformed geometry.
- `north marker authored without an axle — orientation cue ignored.` — when the marker is present but the layer has zero axle ellipses/circles.

## Open questions

1. **Camera target during rotation.** OrbitControls' target stays at world origin. For a centered axle this is invisible; for an off-center axle the piece visibly swings around the axle point while the camera orbits a different (centroid-ish) point. May or may not feel off — Alan to evaluate live. If it feels off, easy follow-up: move `controls.target` to the active axle's world position whenever there's an axle.

## Next-session handoff

1. **Alan: live test.** Reload `preview.html`, drag in pieces 067, 069 from `inbox/`. Confirm: silver wire visible at axle, slab rotates CW around it via Rotation slider for positive degrees, slider hidden on no-axle pieces, thickness slider preserves rotation when tweaked.
2. **Author a `north` marker on a real piece** (e.g. piece 067) inside `<g id="axles">` — any small ellipse / circle / rect / path with `id="north"`. Confirm the brass-gold sphere appears at the authored position and rotates with the piece as the slider moves.
3. **If the camera-target-stays-at-origin behaviour feels off during live test**, we move `controls.target` to the active axle in a separate small follow-up.
