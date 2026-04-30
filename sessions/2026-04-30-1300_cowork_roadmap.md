---
date: 2026-04-30
start_time: "13:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

# Goal

Design and write `ROADMAP.md` — the detail-layer build plan that sits between `work/SPEC-3D-VIEWER.md` (high-level design) and the per-task `CODE_PROMPT_*.md` files (executable handoffs). Settle the five open product decisions from the SPEC along the way so the roadmap can be drafted against firm ground.

# What was done

**Settled the five open SPEC product decisions.** Walked each in turn with recommendations and rationale; Alan agreed with all five recommendations:

1. Layer-toggle visual: translucent (~20% opacity) default, single global "hide instead" switch in a settings menu. Per-toggle 3-state UI rejected.
2. Aesthetic: illustrative first in M3 (flat viewer), iterate toward photographic in M5 (polish) if time permits. No runtime toggle.
3. Mobile interactivity depth: defer entirely. Desktop-only for v0.1.0; mobile becomes a Post-M5 milestone.
4. Hosting: GitHub Pages off this repo (the repo is public). Source-vs-derivative split enforced by what gets copied into the build artifact, not by repo-splitting.
5. Mechanism animation timing: keep animation in M6 stretch; add a gear-ratio validation script as a sub-task of M2 (all pieces traced) so transcription tooth-count inconsistencies surface before M4 (assemblies) work begins.

**Wrote `ROADMAP.md` at repo root.** Comprehensive plan covering: status legend; milestone index with rough estimates and dependencies; resolved-decisions table; per-milestone task tables for M1 through M6 plus Post-M5 mobile; per-piece M2 rows organized by source plate (one row per piece per Alan's instruction, ~119 rows pre-populated from `source/transcriptions/embedded-labels.md` panel listings, with cross-panel overlaps flagged); a model selection guide (added per Alan's mid-draft request) recommending Haiku 4.5 for M2's per-piece sidecar batch, Sonnet 4.6 as the default for most coding and authoring, Opus 4.6 for `pieces.ts`, `assembly.ts`, escapement tick animation, and roadmap/spec maintenance; an "Open items" capture for things not yet planned (CHANGELOG, CI, license/attribution); update conventions (Cowork edits structure + status, Code flips closed tasks to done at PR-merge with session-note links, CLAUDE.md status table stays as the high-level mirror).

**Discrepancy surfaced.** SPEC §M1 says "all 9 pieces" of plate D; `embedded-labels.md` Panel D lists 11 (4, 10, 18, 19, 26, 29, 30, 31, 32, 91, 92). Roadmap defers to embedded-labels.md as the post-audit source. SPEC text should be corrected on a future pass.

**Cross-plate piece-listing overlaps flagged.** Several pieces appear in multiple panel listings (27 in C and G; 32 in D and G; 49 in F and G; 53 in G and H; 67 in F and H; 74 in E, F, and H; 89 in F and H; 112 in B and E; 117 in B and J; 118 in B and I). The roadmap lists each piece exactly once under its earliest-occurring panel and flags cross-references in the Notes column. Authoritative resolution is the `pieces.csv` deliverable in M1.

**Letter-variant pieces.** 92a (anchor-and-pendulum group, primary plate likely D or H — needs disambiguation in M1) and 112a (face-and-case group, listed under E in the roadmap pending confirmation).

# Files Changed

- `ROADMAP.md` (NEW) — repo-root build plan; the detail layer for the SPEC's M1–M6 plus Post-M5 mobile.
- `sessions/2026-04-30-1300_cowork_roadmap.md` (NEW) — this file.

# Open Questions / Flags

- SPEC §M1 says 9 pieces on plate D; embedded-labels.md says 11. Update SPEC during M1 or in a small Cowork pass.
- Several pieces appear in multiple panel listings (see "Cross-plate piece-listing overlaps" above). Resolve in M1's pieces.csv build.
- Piece 92a needs primary-plate confirmation (D or H likely).
- v1.0.0 target — when does the project graduate to 1.0? Not addressed in this session; defer until after M5 ships.
- CHANGELOG.md for the viewer — flagged as an Open Items entry; create when M3 first ships.
- CI / GitHub Actions — flagged as Open Items; consider adding in M2 or M3.

# Next Session Handoff

The roadmap is the working source of truth for build sequencing. The previous handoff suggested two next moves; given today's work, those refine to:

1. **Cowork pass to write `CODE_PROMPT_M1-pipeline-plate-d.md`** — the orchestration prompt for the first Code session. Now grounded in the roadmap's M1 task list (1.1 through 1.9). Should be a focused 30–60 minute Cowork session.
2. **Quick Cowork pass to update `CLAUDE.md`'s "Where We Are" status table** to mirror the new roadmap status. Five-minute task; can fold into option (1).
3. **Quick Cowork pass to update SPEC §M1's "9 pieces" → "11 pieces"** and resolve the SPEC's "Open product decisions" section as closed (referencing the roadmap's resolved-decisions table). Five-minute task; can also fold into (1).

Recommend doing (1) next, with (2) and (3) folded in as small bookkeeping at the start of the same session.

# Commit message (copy/paste)

Subject:

```
add ROADMAP.md; resolve five open SPEC product decisions
```

Body:

```
ROADMAP.md (new): detail-layer build plan at repo root, sitting
between SPEC-3D-VIEWER.md (high-level design) and the per-task
CODE_PROMPT_*.md files (executable handoffs). Status legend,
milestone index with effort estimates and dependencies, resolved-
decisions table, per-milestone task tables for M1 through M6 plus
Post-M5 mobile, ~119 per-piece rows for M2 organized by source
plate (with cross-panel overlap flags), a model selection guide
(Haiku 4.5 / Sonnet 4.6 / Opus 4.6 recommendations per task type),
an Open Items capture, and update conventions. CLAUDE.md status
table stays as the high-level mirror; this doc is the detail.

Resolves the five open SPEC product decisions: layer-toggle
visual = translucent default with global hide-instead switch;
aesthetic = illustrative first in M3, photographic in M5 if time;
mobile = defer to Post-M5; hosting = GitHub Pages off this repo;
animation = keep in M6 stretch but add gear-ratio validation to
M2.

Surfaces a discrepancy: SPEC §M1 says 9 pieces on plate D;
embedded-labels.md Panel D lists 11. Roadmap defers to
embedded-labels.md; SPEC text needs a small follow-up correction.

sessions/2026-04-30-1300_cowork_roadmap.md (new): this session's
record.
```
