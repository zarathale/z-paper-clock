---
date: 2026-05-02
start_time: "23:59"
end_time: "00:45"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Surface the `preview.html` work shipped on 2026-05-01..2026-05-02 into the SPEC and ROADMAP so a fresh session can pick up the project without having to assemble the picture from session notes alone. Update CLAUDE.md's status table to point at the new artifacts. Open the architectural question — does preview.html graduate into `work/viewer/`, stay separate, or replace `work/viewer/`? — without resolving it.

## What was done

**Asked Alan four clarifying questions** before drafting:

1. **Primary doc:** SPEC-3D-VIEWER.md (with cross-references in CLAUDE.md / ROADMAP.md).
2. **Tool role:** "starting as authoring/QA but becoming the foundation for the production viewer; open for discussion on whether HTML continues to be the right path."
3. **Depth:** Full pass + open TODOs.
4. **Roadmap:** Yes — add an M0.6 row.

**Read** (so the writeup wasn't speculative): `preview.html` end-to-end (~1360 lines), `work/SPEC-3D-VIEWER.md`, `ROADMAP.md`, the v1 / v1a / v1b / cut-layer / texture-flip / back-face-mirror / perf orchestration prompts (front matter and openers), and `sessions/2026-05-02-2100_cowork_preview-html-perf-diagnosis.md` (for the architectural commentary on render-on-demand).

**Edits.**

- `work/SPEC-3D-VIEWER.md` — added a new top-level section "Authoring/QA preview tool (`preview.html`)" as the final section, after "Sequence". Five subsections: *What it consumes* (table of layers + their parser behavior), *Silhouette source chain* (Tier 1 layer → Tier 2 PNG alpha → Tier 3 path heuristic, with the banner-on-fallback contract), *Current feature set* (slab rendering, thickness control, axle rotation, orientation cue, performance, diagnostics — each with the implementation detail that distinguishes it from a sketch), *What's not yet there* (v1b queued; cutouts subtraction, multi-cutaway slabs, rotated/skewed `<use>` transforms, UV offsets all deferred — with TODO marker references in code), *Path forward — preview.html vs. `work/viewer/`* (open question; three options laid out — port-into / keep-separate / replace; recommended next step is to ship v1b first and let the polygon-cut + hinge complexity guide the call). Also amended the "Sequence" paragraph at the top of the Sequence section to mention M0.6 as a parallel track to M0.5.
- `ROADMAP.md` — added M0.6 row to the milestone-index table (between M0.5 and M1) with a one-line summary; added a full M0.6 section in the body (between M0.5 and M1) with goal / why-this-milestone / dependencies / strategy / a 13-task table covering everything shipped (0.6.1 through 0.6.8) plus what's queued (0.6.9 v1b, 0.6.10 cutouts, 0.6.11 multi-cutaway, 0.6.12 the two TODO markers) plus the decision row (0.6.13 graduate-or-keep-separate). Updated the aggregate-hours line (~106 → ~120 through M5; ~133 → ~147 through M6 + mobile). Added a trailing dated note at the bottom describing this pass.
- `CLAUDE.md` — added an M0.6 status row in the "Where We Are" table (between M0.5 and M1), pointing at the new SPEC section and the new ROADMAP M0.6. Added a new lead `*Last updated:*` paragraph at the bottom describing this doc pass; the previous "Last updated" became "Earlier 2026-05-02 (late evening / midnight pass)".

**Doc-sweep.** Grepped `preview\.html|preview-html` across `*.md` (23 files matched, all expected — the three docs I just edited plus the session-note + CODE_PROMPT trail). Grepped `work/viewer` in README.md (no references — README doesn't currently mention either viewer, no cross-reference needed there). Grepped `M0\.6` (now appears in CLAUDE.md, ROADMAP.md, and SPEC-3D-VIEWER.md, as intended). No contradictions surfaced.

**What was NOT done.** No code changes — `preview.html` itself untouched. No new orchestration prompt — v1b's prompt was discussed in the SPEC text but not re-tightened (that's the next Cowork step on the M0.6 track). The architecture decision (0.6.13) was framed but not resolved.

## Open questions

1. **The graduate-or-keep-separate decision (M0.6.13).** Three options enumerated in the SPEC § "Path forward". Recommended sequencing: ship v1b first, then decide. The polygon-cut + adjacency BFS + hinge hierarchy is the largest remaining piece of architectural risk, and how cleanly it implements in plain JS at preview.html scope is a fair predictor of whether porting into `work/viewer/` is straightforward (option 1) or warrants a fresh TS/Vite rebuild (option 2) — or whether preview.html is already shaped enough to be the production viewer with minor extensions (option 3).
2. **v1b prompt re-tightening.** `CODE_PROMPT_preview-html-v1b.md` is `status: draft`. Its task numbering and edit-target line ranges presume v1a's structure but were authored before v1a shipped. Before flipping to `ready-for-code`, it needs a Cowork pass that grounds it in the shipped function names (`extractSilhouette`, `extractSilhouetteFromLayer`, `parseSVG`'s output `parsed` shape, `renderScene`'s teardown structure, `buildSlab`'s material setup, etc.).
3. **Cutouts authoring stock.** No piece in `inbox/` currently authors a `<g id="cutouts">` layer with `cutout-N` children. When 0.6.10 lands, an authored test piece will need to land alongside it.

## Next-session handoff

Whichever Cowork session picks this up next:

1. Read the new SPEC § "Authoring/QA preview tool (`preview.html`)" and the new ROADMAP § M0.6 to internalise the framing.
2. Either: re-tighten `CODE_PROMPT_preview-html-v1b.md` against v1a's shipped state (next M0.6 task), or: continue M0.5 chunk-and-crop ingest if more inbox content has landed.
3. Don't touch `work/viewer/` — that's still M3 unless / until 0.6.13 says otherwise.

## Commit message

Subject:

```
add preview.html to spec + roadmap; track as M0.6
```

Body:

```
Surface the preview.html authoring/QA tool work shipped 2026-05-01..2026-05-02
into the design docs.

work/SPEC-3D-VIEWER.md gains a new final section "Authoring/QA preview tool
(preview.html)": what it consumes (per-piece SVG with embedded scan + canonical
layered structure), the three-tier silhouette source chain (authored layer →
PNG alpha → largest-colored-path), the current feature set (slab rendering,
thickness control, axle rotation with silver-wire framework + brass-gold north
sphere, render-on-demand perf), what's not yet there (v1b polygon-cut + hinge
animation queued; cutouts subtraction, multi-cutaway slabs, rotated-use
transforms and UV offsets all deferred), and an open path-forward discussion
(does preview.html graduate into work/viewer/, stay separate, or replace
work/viewer/?). The "Sequence" paragraph at the top notes M0.6 as a parallel
track to M0.5.

ROADMAP.md gains an M0.6 row in the milestone index and a full M0.6 section
between M0.5 and M1 in the body. The 13 sub-tasks cover everything shipped
(0.6.1 through 0.6.8: v1 design / v1a foundation / cut-layer / texture-flip /
back-face-mirror / perf / thickness-fix / axle-rotation), what's queued (v1b /
cutouts / multi-cutaway / TODO(070)+TODO(uv-offsets)), and the
graduate-or-keep-separate decision (0.6.13). Aggregate-hours line bumped
from ~106 to ~120 through M5.

CLAUDE.md status table gains a matching M0.6 row pointing at the SPEC and
ROADMAP sections. New "Last updated" paragraph describes this pass.

No code changes — preview.html itself untouched. Session note at
sessions/2026-05-02-2359_cowork_preview-html-spec-and-roadmap.md.
```
