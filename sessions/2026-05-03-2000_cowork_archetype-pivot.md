---
date: 2026-05-03
start_time: "20:00"
end_time: "21:00"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Author `work/expected_layers.yaml` (section defaults + initial per-piece overrides) and tee up the CODE_PROMPT for the asset-state audit extension + `dashboard.html` ship. Picked up from `sessions/2026-05-03-1800_cowork_dashboard-design.md`.

Outcome diverged from the original goal: organizing principle pivoted mid-session, no CODE_PROMPT teed up. Tagging tool shipped instead.

## What was done

**Drafted `work/expected_layers.yaml` v0 with section-based defaults.** Used the 10 section values from `work/pieces.csv` as keys (`framework`, `motor-wheel`, `middle-wheel`, `escapement`, `reduction-gear`, `anchor-pendulum`, `hands`, `weight`, `face-case`, plus `reference` excluded from defaults entirely). Heavy comments. ~50 per-piece overrides pre-populated for known exceptions (flat pieces in fold-heavy sections, axle holders in framework, star-cut pinion stacks, accordion strips, hand silhouettes, etc.). Schema kept narrow: `add` and `remove` keys only; `reference` pieces (107, 120) handled by bottoming at empty default and using `add: [silhouette]`.

**Surfaced uncertainty during walkthrough.** When framing the section defaults to Alan I flagged ~3 calls I wasn't confident about — motor-wheel keeping folds in default, hands excluding folds despite tube pieces, anchor-pendulum including axles despite four flat exceptions. Each was 50/50.

**Pivoted: section axis → physical-character axis.** Alan pushed back: when defaults split 50/50, they're noise, not signal. The book-section axis is the wrong organizing principle for layer expectations. Sections describe *which sub-assembly a piece serves* — that's transform-hierarchy / functional-purpose work. What predicts the layer set is the piece's *physical character as a printed object* — which construction operations it participates in. Different axis. The section taxonomy was fighting us.

**Sketched 10 archetypes, mapped to keys 1–9, 0:**

1. flat-laminate — flat, glued back-to-back or onto cardboard
2. flat-decorative — flat, visible final surface
3. folded-tube — flat → cylinder
4. folded-box — flat → 3D enclosure
5. frame-channel — long strip, U/L cross-section
6. gear-disc — flat disc, gear/wheel stack, axle hole
7. pinion-stack-disc — small star-cut disc on rolled pinion
8. gear-teeth-strip — long strip wrapping for teeth (mountain peaks)
9. anchor-pendulum-mixed — heterogeneous §II.C piece
0. reference — non-build (107, 120)

Defaults inside each archetype are sharp — most pieces in an archetype share the same layer set; per-piece add/remove handles the rare hybrids (e.g. piece 069 = folded-box + axle pivot → `add: [axles]`).

**Decided data home.** A new `character` column on `work/pieces.csv` (door open for additional orthogonal-trait columns if tagging surfaces them — `has-axle`, `has-cutouts`, etc., though the primary archetype usually predicts those). Master index stays the source of truth for piece-level metadata; `expected_layers.yaml` stays a pure rule table keyed off that column.

**Built `tag-pieces.html`** at repo root, parallel to `preview.html`. Single-file tool. Pattern matches preview.html's file://-friendly approach: pieces.csv data embedded as JS const (no fetch / no file picker), relative `<img src>` for PNGs (file:// permits). UI: 10 archetype buttons in a row at top (always-visible legend), large piece image, plate/section/csv-status pills, csv notes block, current-tag indicator, optional per-piece note textarea, nav buttons. Keys: `1`–`0` tag with archetype, `u` uncertain, `s` skip, `x` clear, `j` jump-to-ID, `n` focus note, `←` `→` prev/next. localStorage-backed, auto-saves on every action. Filter chips (untagged / uncertain / tagged / skipped) + section dropdown. Pieces without PNGs (013, 014, 016, 017, 090, 110) show a "pending capture — tag from notes or skip" placeholder. Export modal produces `piece_characters.yaml`-shaped output via copy-to-clipboard or download.

**Bug caught at build time:** `tagCurrent` and `skipCurrent` originally called `advance(1)` after persisting state. That skipped one piece when the filter was "untagged only" — the just-tagged piece dropped out of the visible list, and the cursor advance double-counted. Replaced both with a shared `advanceAfterMutation(prevId)` helper that recomputes the filter, then advances only if the previous piece is still visible. Otherwise the cursor naturally points at the next piece.

## Files Created / Modified

| File | Action | Notes |
|---|---|---|
| `work/expected_layers.yaml` | created | Section-based v0 draft. Stays in place pending the post-tagging restructure (will be replaced with a `defaults_by_character` version). |
| `tag-pieces.html` | created | Tagging tool at repo root. |
| `sessions/2026-05-03-2000_cowork_archetype-pivot.md` | created | this note |
| `WORKPLAN.md` | edited | Asset-state track next-action updated + recent-log entry added |

## Open questions

- The 10-archetype taxonomy is provisional and built from `pieces.csv` notes, not by eyeballing the print. `anchor-pendulum-mixed` feels like a catch-all and might split or absorb during tagging. `gear-teeth-strip` might collapse into another archetype if its shared traits (silhouette + folds-mountain + glue-zones) match an existing one. Tagging will surface where the taxonomy needs to flex.
- Whether to delete `work/expected_layers.yaml` outright or keep it as reference until the post-tagging restructure produces the replacement. Leaning delete-after, but no urgency.
- Whether tagging surfaces additional orthogonal traits worth their own column (has-axle, has-cutouts, has-printed-labels, etc.) beyond the primary character. Alan's reply ("character column ... and/or additional columns there, if warranted") leaves the door open. Decide post-tagging.
- The CODE_PROMPT for dashboard + audit extension still needs to be authored. Original plan stands — the character-column read is a small addition to the audit's logic, no shape change. Author after the YAML restructure settles.

## Next-session handoff

1. Alan opens `tag-pieces.html` locally (file://) and tags 123 pieces. Estimate ~1 hour total, splittable across sittings (localStorage persists).
2. **Cowork session** — review export, settle final taxonomy (rename / merge / split if tagging surfaced new shapes), merge `character` column into `work/pieces.csv`. Update the comment block at the top of `pieces.csv` to document the new column. If additional orthogonal traits surfaced, add columns then. Optionally delete `work/expected_layers.yaml` v0.
3. **Cowork session** — author `work/expected_layers.yaml` v1 around `defaults_by_character`. Per-piece overrides expected to shrink dramatically vs. the section-based v0.
4. **Cowork session** — finalize `CODE_PROMPT_dashboard-and-audit-v2.md`. Audit extension reads `pieces.csv` `character` column + `expected_layers.yaml`, adds `expected_layers` / `missing_layers` fields per piece, adds `expected-layers-present` advisory check, normalizes `repo_root` (strips worktree path), bumps `schema_version` to 2, adds `pyyaml` dep. Dashboard ships filter-and-list view with bucket chips derived from state.json (lifecycle stages + per-failing-check chips + anomalies), live inline SVG thumbnails, file:// `.af`/`.svg` links.
5. **Code session** — ship audit extension + dashboard.

## Cowork Commit Message

Subject:

```
pivot expected-layers from sections to construction archetypes; ship tag-pieces.html
```

Body:

```
This Cowork session set out to author work/expected_layers.yaml with section
defaults + per-piece overrides, then tee up a CODE_PROMPT for the asset-state
audit extension + dashboard. The YAML draft hit a wall: many section-default
calls split 50/50 between fold-heavy and flat-heavy pieces, which isn't a
useful default — it's noise.

Pivoted the organizing principle: section describes which sub-assembly a piece
serves (transform-hierarchy work); what predicts the layer set is the piece's
physical character as a printed object — which construction operations it
participates in. Different axis. Sketched 10 archetypes (flat-laminate,
flat-decorative, folded-tube, folded-box, frame-channel, gear-disc,
pinion-stack-disc, gear-teeth-strip, anchor-pendulum-mixed, reference) that
each have a sharp default. Per-piece add/remove still handles hybrids
(e.g. 069 folded-box + axle pivot).

Data home for the new dimension: a `character` column on work/pieces.csv
(door open for additional orthogonal-trait columns if tagging surfaces them).

Shipped tag-pieces.html at repo root, parallel to preview.html. Single-file
file://-friendly tagging tool: 10-key archetype mapping, large piece image
loaded via relative <img>, csv notes block, optional per-piece note,
localStorage persistence, filter chips, jump-to-ID, YAML export. Pieces
without PNGs show a placeholder; can still be tagged from notes.

work/expected_layers.yaml v0 (section-based) stays in place pending the
post-tagging restructure. CODE_PROMPT teeing-up parked until the YAML's
new shape is settled.

WORKPLAN.md asset-state track next-action updated to point at the tagging
session + post-tagging YAML restructure.

See sessions/2026-05-03-2000_cowork_archetype-pivot.md for the full pivot
discussion, archetype sketch, and tool design choices.
```
