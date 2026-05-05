# to-alan/069-panels-first/ — author piece 069 with the new panels-first convention

**Opened:** 2026-05-05
**Decision driving this:** `claude-work/DECISIONS.md` row #6 — orientation/awareness model lands as panels-first (B) + authored-vs-derived (D).
**Stakes:** this is the test piece. If panels-first authoring is workable in Affinity, we roll the convention out; if it's painful, we step back and build an authoring helper first.

---

## What

Author a panels-first version of piece 069 in Affinity, alongside the existing canonical `069.svg`. Three new things you're doing:

1. **Add a `panels` layer.** Draw a closed polygon for each panel (region) of the piece. 069 has 14 regions today under cut-trim; the panels layer is you saying explicitly "these are the 14 panels." Each polygon gets an `id` of the form `panel-<descriptive>` (e.g. `panel-stem`, `panel-tab-a`, `panel-base`) — pick names that make sense when looking at the piece; they don't have to match anything else, they just need to be unique within the SVG.
2. **Bind folds to the two panels they join.** Each fold path in `folds-valley` / `folds-mountain` gets an id of the form `fold-<a>-<b>` where `panel-<a>` and `panel-<b>` are the two panels the fold sits between. Example: a fold between `panel-stem` and `panel-tabA` gets `id="fold-stem-tabA"`. Order doesn't matter; the parser treats it symmetrically. Heads-up: panel-id suffixes should not contain hyphens in this v0 form (use `panel-tabA` not `panel-tab-a`) — the hyphen is the parser's delimiter between the two halves of the fold id. If hyphenated suffixes feel more natural at the canvas, flag it; the convention adapts. If Affinity collision-renames any of these (rare — only if two folds happen to bind the same pair), we'll see it and adapt.
3. **Move landings out of `marks` into a new `attach-points` layer.** 069's `landing-a` and `landing-b` (currently in `marks`) move into `<g id="attach-points">`. While you're there, drop the `anchor-pivot` element into `attach-points` too with `id="pivot-anchor"` (it's a mechanical pivot — distinct from the rotation axle wires that live in `axles`). `mark-h` / `mark-i` stay in `marks` (those are construction marks, not connection points).

What stays the same: silhouette, cutouts, fold paths themselves (just gain ids), axles + north (069 doesn't have axles right now, but the convention is unchanged), labels, marks (now narrowed to construction/registration only).

## Why

The cut-line-first algorithm in `preview.html` reverse-engineers panels from silhouette + fold geometry. It works clean on 069 today (14 regions, 11/11 markers) but fails on harder pieces (066's co-linear folds → 13 orphan regions; 067's no-folds → no graph at all). The 22:00 inventory across 7 pieces showed the SVGs are accumulating concepts the convention doesn't name — pin-holes living in `axles`, mechanical pivots living nowhere, landings sometimes in `marks`. Panels-first inverts: the SVG names what it IS; the parser stops trying to derive what the author already knows.

069 is the test piece because it's small, mostly-clean, and anchor-related (high-value for the eventual M4 assembly work). If panels-first authoring in Affinity is "small extra step per panel," we know we can roll the convention out across the remaining pieces. If it's "this doubles my time per piece," we step back and either build an authoring helper (preview.html could grow a "propose panels from cut-trim, accept/edit" tool) or stay cut-line-first and ship the snap-only-extension follow-up.

## Where

Two files, both in `work/pieces/069/`:

- **`069-panels.af`** — Affinity source. Easiest start: duplicate `069.af`, rename, then add the `panels` layer + bind folds + relocate landings as above.
- **`069-panels.svg`** — exported SVG.

The existing `069.af` / `069.svg` stay untouched as the cut-line-first reference. After we evaluate, if panels-first wins, the panels variant gets promoted to canonical (`069.af` / `069.svg`) and the cut-line-first version gets archived to `work/pieces/069/_attic/`. If panels-first loses, we delete `069-panels.*` and the canonical stays as-is.

(The audit will flag the variant filenames as "informational" per the filename convention — that's expected during this experiment.)

## Verifies via

When you've authored `069-panels.svg`, drop a one-liner in chat ("069-panels is up") and I'll:

1. Eyeball the SVG against the brief — panels layer present, folds bind to panel pairs, landings + pivot in attach-points.
2. Load it in `preview.html` to see whether the existing parser at least doesn't choke (cut-trim should still find regions even with panels layer present; the panels layer is purely additive at this stage — the panels-aware parser is its own work, downstream of authoring landing).
3. Capture the result in a follow-up session note + decide whether to ship the panels-aware parser pathway in `preview.html` next.

## Feedback I want from you (the most valuable thing in this brief)

The result of the experiment isn't really "did the SVG export correctly." It's: **what was authoring like?** When you push back through chat, I want to hear:

- **Time:** roughly how long did it take vs. authoring 069 the cut-line-first way? (Ballpark; not a stopwatch.)
- **Friction:** where did Affinity fight you? Drawing closed polygons that share edges with existing fold paths — did you have to retrace, or could you snap to / reuse?
- **Naming:** did `panel-<descriptive>` feel natural, or annoying? Same for `fold-<panel-a>-<panel-b>`.
- **Anything you want to redesign:** if panels-first feels like it wants a different authoring shape (e.g. "I'd rather draw the panels as a single multi-path, or use Affinity boolean ops, or…"), tell me. The convention is co-authored per CHARTER §3 — your hand at the canvas is the source of truth on what works.

If it's a slog, say so loudly. We'll either build the helper or back out. Iteration discipline (CHARTER §9) means we learn from one piece before scaling.

---

*Created 2026-05-05 from cowork session `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`. Tracked in QUEUE.md as #1 and STATUS.md "SVG layer authoring" track.*
