---
date: 2026-04-29
start_time: "14:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

> Updated mid-session to capture two follow-on passes after the initial spec + CLAUDE.md draft: Z/Zara nickname clarification rolled into CLAUDE.md, and the transcription audit log onboarded into the sessions/ convention.

# Goal

Pick up after the auto-trace v2 + pre-processing work, write the 3D viewer build spec, and bootstrap cross-session coaching by surveying ScaenaShows and arc-qb-sync for working conventions and writing a CLAUDE.md for this repo.

# What was done

**Verified pre-processing + auto-trace v2.** Looked through `work/auto-trace-test-v2/compare/` for the five test pieces. Pieces 33, 92, 99, and 122 trace cleanly on the pre-processed scans — bleed-through on plate M is fully eliminated, and the piece-33 top-edge artifact is gone. Piece 1 (frame strip) is still porous but stays in the hand-trace bucket as planned per `RESCAN_FINDINGS.md`. No rescans required to proceed.

**Wrote `work/SPEC-3D-VIEWER.md`.** Full build spec covering: per-piece data model (layered SVG + JSON sidecar), authoring pipeline (crop → trace → layer-split → sidecar → validate), SVG-to-3D extrusion using three.js `SVGLoader` + `ExtrudeGeometry`, assembly tree organized by §II sections of `instructions.md`, viewer behavior (orbit, hover, click, exploded slider, layer toggles), inspect-panel content driven from a built `manifest.json`, tech stack (TS + Vite + three.js, Python pipeline behind a Makefile), folder layout, and six phased milestones M1–M6. Five open product decisions flagged inline at the end.

**Surveyed ScaenaShows and arc-qb-sync** for Zarathale's working conventions. ScaenaShows contributed: status-table-at-the-top pattern, closed-architectural-decisions table, open-questions table, file naming conventions for audits and dept-prefixed sub-docs, theatre metaphor as collaboration tone. arc-qb-sync contributed: per-version orchestration prompt format with eight required sections, sessions/ folder convention with required front matter and body, end-of-session discipline split between Cowork and Code, three-agents-three-lanes git workflow, `gh` CLI as a locked assumption, post-merge cleanup recipe, lock-recovery recipe.

**Wrote `CLAUDE.md`.** Bootstrap the repo's cross-session coaching with: project identity (Z = Zarathale), Cowork/Code division, session-startup ritual, status table, orchestration prompt format adapted for milestone-based work (`CODE_PROMPT_M1-...md`) and version-numbered ships (`CODE_PROMPT_v0.1.0.md`), sessions/ convention, viewer-specific SemVer policy (no version on the study side; SemVer once viewer ships), repo structure tree (with NEW entries reserved by name from the SPEC), git workflow with three-lane Cowork/Code/GitHub-Desktop split, mac-specific lock recovery (less aggressive than the Windows + OneDrive recipe), post-merge cleanup, closed architectural decisions, open questions table cross-referenced to the SPEC, known issues, file naming conventions.

**Created `sessions/`** as a folder; this file is the first entry.

# Files Changed

- `work/SPEC-3D-VIEWER.md` (NEW) — 3D viewer build spec
- `CLAUDE.md` (NEW; later edited in-session for Z/Zara/Zarathale clarification + audit-log redirect)
- `sessions/` (NEW) — folder
- `sessions/2026-04-29-1400_cowork_3d-viewer-spec-and-claude-md.md` (NEW) — this file
- `sessions/2026-04-29-0900_cowork_transcription-audit.md` (NEW) — retroactive session note onboarding the prior audit log
- `work/audit-session-log.md` (DELETED) — content fully captured in the retroactive session note above; deletion permission granted via `allow_cowork_file_delete`.

# Open Questions / Flags

- Five open product decisions in the SPEC (layer-toggle visual, aesthetic target, mobile depth, hosting, animation timing) await Zarathale's calls before M3+. None block M1 or M2.
- The audit-session-log convention used by `work/audit-session-log.md` predates the new `sessions/` convention. Left in place — it's a perfectly good record of the transcription audit, not worth retroactively renaming.
- The repo doesn't have a CHANGELOG yet. Defer creation until M1 ships actual code; the SPEC itself is sufficient narrative for now.

# Next Session Handoff

Two reasonable next moves:

1. **Cowork pass to write `CODE_PROMPT_M1-pipeline-plate-d.md`** — the orchestration prompt for the first Code session. M1 builds the pipeline scripts (`01-crop.py` through `04-validate-sidecars.py`) and runs them end-to-end on plate D's 9 pieces. The SPEC has the algorithmic detail; the prompt translates it into Code-ready tasks.

2. **Quick Cowork pass to settle the five open SPEC decisions.** Even tentative answers unblock the inspect-panel layout sketches in M3. Could be a 20-minute session.

Either is a good first move. (1) is the larger payoff but assumes the open decisions stay open; (2) clears the deck.

# Commit message (copy/paste)

Subject:

```
add SPEC-3D-VIEWER.md and CLAUDE.md; bootstrap sessions/
```

Body:

```
work/SPEC-3D-VIEWER.md (new): build spec for the 3D paper-clock
viewer. Per-piece data model (layered SVG + JSON sidecar), authoring
pipeline, SVG-to-3D extrusion via three.js, assembly tree by §II
sections, viewer behavior, inspect-panel content, tech stack, folder
layout, and six phased milestones. Five open product decisions
flagged inline.

CLAUDE.md (new): cross-session coaching — project identity,
Cowork/Code division, session-startup ritual, orchestration prompt
format, sessions/ convention, versioning policy, repo structure,
three-lane git workflow with GitHub Desktop, mac lock recovery,
post-merge cleanup, closed decisions + open questions tables.
Cross-pollinated from ScaenaShows and arc-qb-sync conventions.
Z/Zara/Zarathale all embraced; casual forms preferred in chat.
Two-block commit-message display convention captured.

sessions/ (new): folder + two entries.
sessions/2026-04-29-0900_cowork_transcription-audit.md is a
retroactive note onboarding the transcription audit (originally in
work/audit-session-log.md) into the new convention.
sessions/2026-04-29-1400_cowork_3d-viewer-spec-and-claude-md.md is
this session's record.

work/audit-session-log.md (deleted): canonical record moved to
sessions/2026-04-29-0900_cowork_transcription-audit.md.
```
