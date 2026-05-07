# tag-pieces.html — quick reference

A scrollable cheat sheet for the tagging UI. Distilled from `work/piece_characters_v2.yaml` (lines 1-175 schema header — that's the canonical source if anything here disagrees).

Open this alongside `tag-pieces.html` in a second editor pane or rendered Markdown view.

---

## What you're doing

For each piece, assign a **character** (one of 7) and a **subtype** (free-form, autocompleted). The character is determined by what *layers* the piece will need in its eventual SVG; the subtype is the descriptive flavor.

The fundamental insight of v2: characters are determined by three binary properties, not by visual shape.

- Does it **fold**?
- Does it have an **axle** (any pin / wire / rod pass-through)?
- Does it have an **interior cutout** (separate from the axle)?

That's it. A "gear-disc" and a "decorative-laminate-square" can both be plain `flat` if neither folds nor has an axle nor has a cutout. Visual shape lives in subtype.

---

## Decision tree (the 7 characters)

```
Is it a non-build reference (dimension legend, calibration)?
  YES → reference                  (today: just 107)
  NO  ↓
       Does it fold?
         YES                                  NO
          ↓                                    ↓
       Has an axle?                      Has an axle?
         YES        NO                     YES        NO
          ↓          ↓                      ↓          ↓
      folded-axle  folded             Has a cutout?  Has a cutout?
                                        YES   NO       YES   NO
                                         ↓     ↓        ↓     ↓
                                  flat-axle-  flat-  flat-   flat
                                    cutout    axle  cutout
```

The 7 leaves, with examples:

| character | layer signature | when | examples |
|---|---|---|---|
| **flat** | silhouette + (glue) + labels + marks | no folds, no axles, no cutouts | hands (108, 109), clock face (121), decorative crescent (099), spacers (091, 026, 027, 028) |
| **flat-cutout** | + cutouts | flat with interior hole(s) only | square ring (071), tab-rings (043, 044), face brace with hole (113) |
| **flat-axle** | + axles | flat with axle pass-through | most gear-discs (036, 050, 051), escape-wheel (058), anchor arm (065), pendulum blade (072), pulley discs (088, 089) |
| **flat-axle-cutout** | + axles + cutouts | flat with axle AND interior cutout | pinion-mount discs (053, 054, 056, 057, 061-064), motor-wheel face (038), hands wheels with cutout (075, 078, 087), pulley plates (046, 047) |
| **folded** | + folds-V + folds-M | folds, no axles, no cutouts | frame rails (001-008), brackets (012-017), tubes (040, 052, 094, 101), boxes (023-025, 029, 030, 117), teeth strips (034, 037, 074, 082, 083, 085, 105) |
| **folded-axle** | + folds + axles | folds AND has an axle | frame columns (004, 010), anchor-bearing box (069), face-frame braces with axle (115, 116) |
| **reference** | (no layer expectations) | non-build | 107 (axle-dimension legend) |

---

## Two clarifications worth knowing

**1. Glue is agnostic.** Whether the glue is structural (binds folds, holds tabs) or laminate (back-to-back, onto cardboard) doesn't affect the character — both collapse into the same family. v1's `flat-decorative` vs `flat-laminate` distinction goes away in v2: a flat-laminated-to-cardboard piece and a flat-decorative piece both tag as plain `flat`. The laminate-vs-decorative read lives in subtype + note.

**2. Sliding axles count as axles.** Any pin / wire / rod that passes through a piece counts as an axle marker, regardless of whether the piece pivots around it, slides along it, or sits static on it. Test case: piece 100 (bob-position indicator disc) slides up and down the pendulum rod — its rod-pass-through hole is an axle marker, so it's `flat-axle`. The sliding behavior is captured in the controls block (forward-looking M6 thing), not in the character.

---

## Subtype — the dropdown field

Subtype is the descriptive flavor under the character. Two `folded` pieces can have wildly different subtypes (`frame-rail` vs `bracket-tab` vs `tube-pulley`) and serve totally different roles in the build.

**What subtype is for downstream:**

- Viewer grouping (M3+) — "show me all frame-rails together"
- Tracing-strategy hints (M2 pipeline) — pieces with similar subtypes likely need similar trace approaches
- Human comprehension — when scrolling the tagged list, subtype tells you what you're looking at without re-opening the image

**UI** (post-2026-05-06 patch): the subtype field is a dropdown populated alphabetically from the full vocabulary, with an "Other (type below)…" escape hatch at the bottom for coining a new slug. Native `<select>` typeahead works — focus the dropdown and start typing (e.g., `tube-`) to jump to the matching options.

**Discipline:** scroll or typeahead to find the closest fit. Coin a new slug (via "Other") only when no existing option fits. When in doubt, pick the closest existing one and use the per-piece **note** field to explain.

**For definitions of every existing subtype + which pieces use it,** see the sibling `subtypes.md` in this folder.

**The vocabulary, organized by visual category:**

- **Frame rails** — `frame-rail`, `frame-rail-axle`, `frame-rail-face`
- **Brackets** — `bracket-tab`, `bracket-l`, `bracket-wall`, `bracket-cross`
- **Boxes** — `box-cross`, `box-small`, `box-wall-bracket`, `box-anchor-bearing`, `box-case-top`, `triangle-spacer-motor`
- **Tubes** — `tube-pulley`, `tube-pulley-drum`, `tube-pulley-string-wind`, `tube-pendulum-blade`, `tube-bob-casing`, `tube-weight-cylinder`, `tube-weight-label-wrap`, `tube-minute-hand-holder`, `tube-strap`, `tube-wheel-cover`, `tube-rolled-pinion`
- **Teeth strips** — `teeth-strip-motor`, `teeth-strip-reduction`, `teeth-strip-hook`, `teeth-strip-accordion-pulley`, `teeth-strip-sawtooth-weight`
- **Discs** — `gear-face`, `gear-back`, `motor-wheel-face`, `motor-wheel-back`, `escape-wheel`, `escape-wheel-back`, `middle-wheel`, `middle-wheel-back`, `reduction-gear`, `pulley-disc`, `pulley-plate`, `pulley-plate-back`, `plate-cap`, `lid-weight`, `hands-wheel-hour`, `hands-wheel-hour-back`, `hands-wheel-star`, `spacer-disc`, `indicator-bob`
- **Pinion mounts** — `pinion-mount-middle`, `pinion-mount-escape`, `pinion-mount-motor`, `pinion-mount-hands`
- **Anchor / pendulum parts** — `anchor-arm`, `anchor-fork`, `plate-anchor-rear`, `blade-pendulum`, `ring-square-pendulum`, `pendulum-rod`, `hook-pendulum`
- **Bob parts** — `bob-face`, `bob-retainer`, `bob-brace`, `reinforcement-cardboard`, `crescent-decorative`
- **Frame braces / spacers** — `face-brace-cross`, `face-brace-cross-axle`, `face-brace-cross-hole`, `spacer-pendulum-support`, `wedge-wall-bracket`, `spacer-cardboard`
- **Hands** — `hand-minute`, `hand-hour`
- **Case** — `case-side`, `face-clock`
- **Misc rings** — `ring-tab-pulley`
- **Other** — `tongue-oval`, `oval-elongated`, `tongue-narrow-hands`, `push-tab-wheel`, `axle-mount-square`

---

## Status values (the badge in the upper-right of each card)

- **pristine** — never tagged. Default for fresh pieces.
- **tagged** — you've assigned a character + subtype. Done.
- **uncertain** — historical: marked from the v1 export as "needs pair-tag review." Promote to `tagged` once you've decided. (Should be empty after the 2026-05-03 walkthrough — flag any you find.)
- **pair-tag** — historical artifact from the 2026-05-03 walkthrough where Alan + Claude reviewed ambiguous pieces together. Today only piece 041 sits here ("Alan re-reading instructions" about the pulley shaft question). **For net-new tagging, ignore.** If you hit a pair-tag piece, ping me, we'll resolve in chat, then promote to `tagged`.
- **pending** — historical: piece not yet captured. After the 2026-05-06 patch, no live pieces are at this status; the filter still exists in the UI but matches nothing.
- **skipped** — you skipped this piece. Comes back later.

---

## Navigating directly to a piece

Press **`j`** anywhere outside an input field, or click the **Jump** button in the nav row. A prompt asks for a piece ID (`069`, `092a`, `112a` — match the source-archive filename). Unknown IDs toast a warning; valid IDs load that piece, resetting filters if needed.

Useful for: re-reviewing specific pieces during a triage pass; pulling up a piece referenced in a note or conversation; spot-checking a pair (jump 78, jump 79) without scrolling.

---

## What to trust on each card, in priority order

1. **The image** — primary signal. It's the piece itself.
2. **`v1_was`** (the small annotation when present) — the legacy archetype is a useful breadcrumb. The v1→v2 retag often just adds axle/cutout discrimination on top of the v1 read.
3. **Your per-piece note** (if a previous pass left one) — tagging-relevant context.
4. **`pieces.csv` notes** (the gray inventory block) — **background only.** These are plate-location and book-cross-reference notes ("Thin strip (hook form) at bottom of plate E; small fragment also visible on H.") that exist to help you *find* the piece in the book, not to help you *tag* it. Most of the prose is irrelevant during tagging. Occasionally a phrase hints at subtype ("hook form" → `teeth-strip-hook`), but always trust the image over the prose.

---

## Edge cases that have come up

- **A piece is laminated to cardboard but otherwise flat with no axle, no cutout.** → `flat`. The lamination is a glue-zone detail, not a character.
- **A piece has visible "fold lines" in the print but they're really alignment guides for gluing onto another piece.** → `flat`. Read the print carefully; not everything that looks like a fold line is a fold. The 026 case from 2026-05-03 (alignment marks misread as folds) is the canonical example.
- **A piece pairs back-to-back with another (e.g. 78/79, 104/106, 058/059).** → tag each independently. Both get the same character; subtype often differs slightly to mark front vs. back (`hands-wheel-hour` / `hands-wheel-hour-back`).
- **A piece has multiple axle holes (e.g. anchor-bearing box 069 with axle landing).** → still `folded-axle` (or `flat-axle`). The presence-of-axle test is a binary; quantity goes in the note.
- **You really can't decide.** → mark `uncertain` and move on. We'll resolve in chat in a focused pair-tag pass.

---

## If something feels off

If you find the cheat sheet doesn't match what the schema actually says, trust `work/piece_characters_v2.yaml` lines 1-175 — that's canonical. Flag any disagreement back so I can update this doc.

---

*Drafted 2026-05-06 in response to "i'm struggling to know precisely how to tag items." Lifecycle: this folder gets cleared from `to-alan/` once the 123-piece tagging session ships; the substance lives on in `work/piece_characters_v2.yaml`.*
