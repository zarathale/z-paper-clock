---
date: 2026-05-03
start_time: "23:00"
end_time: "23:30"
mode: cowork
participant: Zarathale (Alan)
source: retroactive — assembled from the 23:00 session that hit the usage cap mid-handoff plus the resumed pass that closed it out
---

# v2 schema lock-in + CODE_PROMPT for tag-pieces.html

## Goal

Close out the v1 → v2 schema sharpen for piece classification: walk through the 11 pair-tags surfaced in the v2 draft, resolve each from `embedded-labels.md` + `instructions.md`, bake any schema-level clarifications into the YAML header, and tee up a Code session to update `tag-pieces.html` to read/write the v2 shape.

## What was done

**Closed 10 of 11 pair-tags in `work/piece_characters_v2.yaml`** via embedded-label review. The eleventh (piece **041**) deferred — Alan re-reading the instructions to determine whether it's a flat strip glued onto pulley 40 or a rolled paper shaft. That one row stays at `status: pair-tag` with a deferral note in the YAML and is the only outstanding item before merge into `pieces.csv`.

**Three character changes from the v2 draft, baked into the YAML:**

- **077** dropped `folded-axle` → `folded`. The tube IS the bearing for the minute-hand pin; no separate axle authored on the piece itself.
- **080** moved `flat` (uncertain) → `folded` with new subtype `push-tab-wheel`. The embedded fold-line annotation plus the "Push into wheel 78" label settled it.
- **100** moved `flat` → `flat-axle` per the new sliding-axles convention, AND gained the first `controls:` block in the corpus — capturing the master-control plan for the bob position parameter.
- **120** moved `reference` → `flat-axle`. §II.A explicitly lists 120 in the "make a small pin hole in the center" list, so it's a build-grade piece, not pure template.

**Three schema additions baked into the YAML header**, each in its own section so future edits don't lose the rationale:

1. **`controls:` field** — optional list block for UI-bound parameters. Forward-looking (full schema settles in M6 mechanism animation), but the skeleton is captured now and 100 is the first user. Audit ignores it for now.
2. **Glue-agnostic clarification** — `flat` and `folded` don't care whether glue is structural or laminate; the distinction lives in subtype/notes. v1's `flat-decorative` vs `flat-laminate` split correctly collapses into a single `flat` character.
3. **Sliding-axles clarification** — any wire/pin/rod passing through a piece is on the axles layer regardless of motion type (pivot/slide/static). Motion semantics live in `controls:` or the M2+ JSON sidecar `function:` block. This is what justified moving 100 from `flat` to `flat-axle`.

**Drafted `CODE_PROMPT_tag-pieces-v2-schema.md` at repo root** (status: `ready-for-code`) per the CLAUDE.md orchestration-prompt format. Twelve numbered tasks: replace the `ARCHETYPES` constant with `CHARACTERS` + `SUBTYPE_VOCABULARY`; bump `STORAGE_KEY` from v1 → v2 so old localStorage doesn't poison v2; embed `INITIAL_STATE` from `work/piece_characters_v2.yaml` so first-load shows Alan's existing work; add a free-form subtype text input wired to a `<datalist>` autocomplete; add a `pair-tag` status + `p` keyboard binding + filter chip; show a read-only `controls:` badge on pieces that have one (only 100 today); render a `v1 was: …` annotation when a piece changed character during the migration; rewrite the Export YAML emitter for the v2 shape; add a paste-and-load Import YAML modal with a targeted regex parser (no general YAML library — the file runs from `file://`); update progress and filter UI for the new statuses; init wiring + standard session-note stub.

**QA pass on the prompt** (Alan asked for one before declaring final). Two real bugs and one inconsistency caught and folded back in:

- **Bug A (silent data loss on every non-tag mutator).** Original prompt updated `tagCurrent` to preserve subtype + v1_was via explicit-field rebuild, but left `markUncertain`, `skipCurrent`, `clearCurrent`, and the `perPieceNote` debounce alone — all four use the same explicit-field rebuild pattern that would silently strip subtype, v1_was, and controls after v2. Fix: switched all five to `{ ...prev, character, status }` spread so unknown fields ride along automatically. Worst kind of bug because the primary action would still appear to work.
- **Bug B (parser dead-end on post-controls fields).** Targeted YAML parser in Task 9 had a falling-out-of-controls-block branch that consumed the `note: |` line of piece 100 (the line after its controls block) without re-running the inline-field check. Fix: restructured the parser so the controls-block check sits BETWEEN block-scalar continuation and inline-field, with explicit fall-through (no `continue`) when a line is recognised as not-a-controls-list-item. Also fixed `flushControls` to consume any trailing `currentControlItem` automatically.
- **Inconsistency (8 vs 7 characters).** Body said "8 characters mapped to keys 1–8", Task 1 had 7 entries plus a "Key 8 reserved" placeholder, verification checklist said "8 buttons render", help text said "1–7." The schema is genuinely 7 (the 2×2 of axle/cutout for flat plus folded/folded-axle/reference). Dropped the reserved-8th-key idea: 7 buttons, keys 1–7, 7-column legend grid, no dead UI. The v2 YAML's "CHARACTER (8 values)" header is wrong too but stays in place — the YAML lists 7 and is the authoritative reference.

Four spec gaps closed: field ordering on Export YAML (character → subtype → v1_was → [status] → [controls] → [note], matches the canonical YAML for clean diff), multi-line note collapse rule for INITIAL_STATE (newline → space → trim → collapse runs), explicit JS shape for the controls block (`controls: [{ parameter: ..., type: ..., semantics: ..., ui_hint: ... }]`), code sketches for the multi-line block-scalar emitter and the controls emitter on export. Added a "pending only" filter chip (without it, status:"pending" pieces fall through every filter except "all"). Verification checklist gained two regression items targeted at Bugs A and B (item 7: cycle through `u`/`s`/`x`/note-edits on piece 100 and verify subtype/v1_was/controls still present; item 9: import/export round-trip and diff against source). Manual tests made browser-agnostic and gained a piece-100 cycle test.

Net: 13 tasks (Task 6 expanded to cover all five mutators, Task 8 expanded with field order + emitter sketches, Task 9 parser restructured, Task 10 has both pair-tag and pending filters), 13 verification items (was 11), 9-row manual test table. Status stays `ready-for-code`.

## Open questions

- **Piece 041.** Awaiting Alan's instructions re-read to settle flat strip vs rolled cylinder. Single deferred item; doesn't block the Code session (the prompt embeds 041's current `pair-tag` state and Code will surface it as a pair-tag row in the tool, ready for Alan to flip once he's decided).
- **Six pending-capture speculatives** (013, 014, 016, 017, 090, 110). Tagged speculatively in v2 YAML; confirm at capture, not pair-tag. Those rows surface in tag-pieces.html as `pending` after the v2 ship, exactly as they should.
- **Downstream tracks** once the v2 ship lands: (a) merge `character` + `subtype` columns into `work/pieces.csv` (separate Cowork session — touches the CSV schema, so it earns its own decision row in CLAUDE.md's Architectural Decisions table); (b) author `work/expected_layers.yaml` v1 keyed by character with section/subtype overrides; (c) extend the asset-state audit + `dashboard.html` against the v2-keyed expected_layers. None of those are for this session.

## Next-session handoff

**Code session.** Hand `CODE_PROMPT_tag-pieces-v2-schema.md` to a fresh Code session. Expected scope ~half a day — the targeted YAML parser in Task 9 and the INITIAL_STATE migration in Task 3 are the chunkiest pieces; everything else is mechanical. Branch name `claude/tag-pieces-v2-schema` (not an auto-generated `claude/<adjective>-<name>-<hash>`). Code ships, Alan opens the file, confirms the 122 v2 entries seed correctly, refines subtype assignments in a working pass, exports back to `work/piece_characters.yaml`. Then Cowork pickup for the pieces.csv merge.

## Commit message

Subject:

```
draft + QA CODE_PROMPT for v2 schema in tag-pieces.html; close pair-tags
```

Body:

```
Locked in work/piece_characters_v2.yaml after the pair-tag walkthrough:
10 of 11 pair-tags resolved from embedded-labels + instructions; piece
041 deferred pending Alan's re-read. Three character changes from the
v2 draft (077 folded-axle → folded; 080 flat → folded/push-tab-wheel;
100 flat → flat-axle with first controls: block; 120 reference →
flat-axle). Three schema additions in the YAML header (controls: field,
glue-agnostic clarification, sliding-axles clarification).

Drafted CODE_PROMPT_tag-pieces-v2-schema.md at repo root (status:
ready-for-code) and ran a QA pass on it before declaring final. The
prompt updates tag-pieces.html for v2: 7 characters mapped to keys 1–7
instead of 10 mapped to 1–0; free-form subtype input with autocomplete
from the v2 vocabulary; pair-tag + pending status filters; controls:
read-only badge; v1_was annotation on reclassified pieces; Export YAML
rewritten for v2 shape with explicit field ordering; paste-and-load
Import YAML modal with a targeted regex parser (no YAML library —
file:// constraint). Embeds INITIAL_STATE from piece_characters_v2.yaml
so Alan re-opens the tool with all 122 v2 entries already seeded.

QA pass caught two real bugs and one inconsistency. Bug A: the original
prompt updated tagCurrent to preserve subtype + v1_was but left four
sibling mutators (markUncertain, skipCurrent, clearCurrent, perPieceNote
debounce) using the v1 explicit-field-rebuild that would silently strip
subtype/v1_was/controls — switched all five to {...prev, ...} spread.
Bug B: the targeted YAML parser had a falling-out-of-controls-block
branch that consumed piece 100's note: | line without recording it —
restructured so the controls-block check sits between block-scalar and
inline-field with explicit fall-through. Inconsistency: prompt body said
"8 characters mapped to keys 1–8" but Task 1 had 7 entries plus a
reserved-8th-key placeholder; dropped the placeholder, 7 keys clean.
Four spec gaps closed: export field ordering, multi-line note collapse
rule, controls JS shape, block-scalar emitter sketch.

Session note at sessions/2026-05-03-2300_cowork_v2-schema-and-tag-
pieces-prompt.md. WORKPLAN.md asset-state track recent log appended +
next_action bumped to reflect the v2 ship as the current next move.
```
