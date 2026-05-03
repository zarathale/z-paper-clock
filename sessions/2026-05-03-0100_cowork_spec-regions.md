---
date: 2026-05-03
start_time: "01:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Draft `work/SPEC-REGIONS.md` — the design artifact that defines what a "region" is, how the face graph is derived from the layered SVG, and what that unlocks for folding and grouping. Identified as a queued track in WORKPLAN.md; unblocks the pendulum POC.

## What was done

**Read WORKPLAN.md** as the session entry point (new convention from 2026-05-03-0000 session). Confirmed that the Regions track was `status: queued` with `next_action: Draft work/SPEC-REGIONS.md`.

**Clarified four design decisions** before drafting:

1. **Moving-side convention:** root marker (`id="root"`, already reserved in preview.html) drives the BFS tree. The region containing the root marker centroid is the fixed base; all others are moving relative to their BFS parent. No new per-fold hint authoring needed.
2. **Region storage:** computed live at load time (not stored in the JSON sidecar). No pipeline stage added. SVG edits are immediately reflected on next preview load.
3. **Algorithm specificity:** spec names `polygon-clipping` (JS, already in preview.html CDN) and Shapely (Python, already in .venv), and sketches the steps (extend fold lines to boundary → clip → collect faces → build adjacency).
4. **Pendulum stress case:** flagged as an open question to resolve empirically during the pendulum POC; not over-specced now.

**Drafted and wrote `work/SPEC-REGIONS.md`.** Sections: purpose, definition (vertices/edges/faces), algorithm sketch, moving-side convention, runtime data shape (TypeScript interfaces), downstream capabilities table, v1 out-of-scope list, known stress case (pendulum arm self-fold), relation to other docs.

## Files touched

- `work/SPEC-REGIONS.md` — new file (created this session)
- `sessions/2026-05-03-0100_cowork_spec-regions.md` — this file

## Open questions

- Pendulum arm exact piece ID (§II.C) — not yet looked up; deferred to start of pendulum POC track.
- Self-fold resolution rule (which half is fixed when the arm folds onto itself) — flagged in SPEC; will be resolved during POC and the SPEC updated.
- Whether `CODE_PROMPT_preview-html-v1b.md` should reference SPEC-REGIONS.md explicitly — yes, but that prompt is still `status: draft`; add the reference when tightening v1b against v1a's actual signatures.

## Next-session handoff

1. Update `WORKPLAN.md` Regions track: flip `status` to `active`, append log entry, update `next_action` to "Review SPEC-REGIONS.md against pendulum arm piece ID; confirm fold-line authoring convention is sufficient to produce the face graph."
2. Advance the pendulum POC track: look up exact §II.C piece IDs in `embedded-labels.md`, confirm which pieces are the arm + bob, queue SVG authoring on them.
3. Tighten `CODE_PROMPT_preview-html-v1b.md` against v1a's actual function signatures; add a reference to SPEC-REGIONS.md in the "Read These Files First" section; flip to `ready-for-code`.
