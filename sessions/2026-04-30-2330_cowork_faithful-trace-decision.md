---
date: 2026-04-30
start_time: "23:30"
end_time: "23:55"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Settle the build's stance on "by-the-numbers vs. faithful-to-the-messiness" tracing, capture the decision in CLAUDE.md, and update the SPEC sidecar schema to match.

## What was done

Brainstormed the framing. Landed on a hybrid that's also the simpler path: trace each piece **faithfully** — the SVG geometry preserves the human-drawn, human-scanned messiness as the artifact, and no "clean up the gear teeth" pass ever runs against the SVG. Mechanism geometry (tooth counts, axle positions, drive relationships) is captured separately as an optional `function` block in the JSON sidecar, so the M6 stretch animation can read intended values without modifying the trace. Two open questions resolved in the conversation:

1. **Scope of the `function` block.** Populated only on §II.B (gear train) + §II.C (anchor / pendulum / escapement) sidecars — the ~25–30 mechanism pieces that have to satisfy the ticking constraint. All other pieces (framework, hands, weight, face, case) stay purely artifact-faithful with no `function` block. Hand rotation rates inherit from the gear chain at animation time; nothing about a hand's *shape* is functional.
2. **Anchor unit.** Escape-wheel advance per tick. One tick = the escape wheel rotates `2π/N` rad, where `N` is its tooth count. Every other rotation in the mechanism is derived from this. The book's stated pendulum period (from `instructions.md`) becomes a sanity-check input to the M2 gear-ratio validation script, not a primary input.

Files touched:

- `CLAUDE.md` — added a new row to the "Architectural Decisions (Closed)" table: *Faithful trace + functional sidecar*. Footer updated with an evening-pass entry summarizing the decision and naming this session note.
- `work/SPEC-3D-VIEWER.md` — JSON sidecar example gained an optional `function` block (`type`, `toothCount`, `pinionToothCount`, `axleCentroidSvg`, `drives`). Added a paragraph below the example explaining scope, anchor unit, the cross-link to CLAUDE.md, and the expectation that the M2 validation script (resolved product decision #5) reads `function` blocks.
- `ROADMAP.md` — refined M2 task 2.6 (`06-validate-gear-ratios.py`) so the description matches the new anchor: validator reads `function` blocks; escape-wheel advance per tick is the anchor; book's pendulum period is a sanity check, not a primary input. Footer updated.

No code authored. No tests run. Decision-and-doc work only.

## Open questions

None from this session. The two questions surfaced during the brainstorm both got resolved before commit.

A residual to flag for whoever runs M2: when populating `function` blocks during sidecar authoring, the pinion / compound-gear distinction needs a small judgment call per piece (a wheel with both a rim gear and a pinion on the same arbor is one sidecar with both `toothCount` and `pinionToothCount`, not two sidecars). `embedded-labels.md` already records the relevant tooth counts; the M2 task is mostly transcription, not new analysis.

## Next-session handoff

The faithful-trace decision is fully landed and downstream-aligned. The next concrete step on the build remains M0.5.2 — finishing the piece-scan ingest skill helper (queued via `CODE_PROMPT_M0.5.2-piece-scan-ingest.md`, drafted at `sessions/2026-04-30-2300_cowork_M0.5.2-ingest-skill-draft.md`). After M0.5 closes, M2's per-piece sidecar pass is where this decision becomes visible: §II.B and §II.C sidecars carry `function` blocks; everything else doesn't.

Commit message for Zarathale to paste into GitHub Desktop is at the end of the closing chat message (subject and body in two separate code blocks).
