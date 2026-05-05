---
date: 2026-05-04
start_time: "14:30"
end_time: "15:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Define and sign the charter that pivots project leadership from Alan to Claude; create `claude-work/` as Claude's lead zone.

## What was done

Mid-conversation co-authored `claude-work/CHARTER.md` (signed v1.0, effective 2026-05-04) — the kick-off doc that flips project leadership.

Reading pass at the start: re-read inherited context cold so the charter would sit on top of the existing work rather than orbiting around it. Files read: `work/SPEC-3D-VIEWER.md`, `PROJECT-STATE.md`, `ROADMAP.md`, `WORKPLAN.md`, `README.md`, `LAYER-CONVENTIONS.md`.

Four scoping AskUserQuestion items up front: definition of "working clock," physical-build-alongside scope, ownership rules, education angle. Alan's answers grounded the rest of the conversation — most pivotal: he built the physical clock in the 90s and is "giving the book to Claude" as the remake; ownership is read-only for Claude on the rest of the repo with this charter as the one-time exception; education is bonus, not a deliverable.

Drafted v0 of the charter; revised through three rounds of Alan's mid-task feedback into v1:

- v0 → v1a: Alan owns cuts and labels (folded into §3 as authoritative scope on the SVG side).
- v1a → v1b: `LAYER-CONVENTIONS.md` is co-authoring territory, ongoing (resolved §10 row 2 directly; updated §3 / §5).
- v1b → v1: clean-break rename (`work/` archived in place; new `alan-work/` clean), pipeline scripts move to `claude-work/`, sidecar JSON colocates in `alan-work/pieces/NNN/NNN.json`, "re-deriving conventions" scope item refined (Claude leads on conventions still in motion; only truly settled foundations are out of scope), iteration discipline / human-manageable authoring added to §9 (no 99 edits per piece; queue stays modest; lessons stack), `WORKPLAN.md` becomes legacy and is replaced by `claude-work/STATUS.md` going forward.

Alan's question about charter modification was the prompt for §12 (amendment policy): clarifying edits are silent; substantive amendments stack as decision-record rows below §10 with both initials. Calibration table included to make the substantive line concrete.

Both signed v1.0 at kick-off.

## Files touched

- `claude-work/CHARTER.md` — created. New folder `claude-work/` created with this file as its first entry.
- `sessions/2026-05-04-1430_cowork_claude-work-charter.md` — this note.

No other files touched. Per the charter's §3 "What this means for existing project artifacts," the inherited root-level docs (`CLAUDE.md`, `ROADMAP.md`, `WORKPLAN.md`, `PROJECT-STATE.md`, `README.md`, `work/SPEC-3D-VIEWER.md`) are intentionally preserved as-is — they're the inherited-as-of-charter record of pre-charter state. Post-charter live truth lives under `claude-work/`.

## Doc-sweep result

Light. The charter explicitly designates the inherited docs as legacy / inherited-as-of-charter, so no rewrite is required. Optional follow-up Alan may want at his discretion (root-level docs are read-only for Claude post-charter, so these are Alan's pen):

- One-line header on `WORKPLAN.md` noting it's frozen as of charter sign-off 2026-05-04; live status is in `claude-work/STATUS.md` going forward.
- Optional one-line nod in `README.md` to the new project framing for fresh visitors.

Neither is blocking.

## Open questions

None from this session — all eight §10 open items resolved during drafting.

## Next-session handoff

Day-one buildout of `claude-work/`. The §10 row-6 commitment was: build `CHARTER.md` + `STATUS.md` + `QUEUE.md` + `DECISIONS.md` + `to-alan/` skeleton on day one. CHARTER landed this session; the rest is the next session's job.

After day-one structure: settle the open `preview.html` ↔ `work/viewer/` architecture decision (M0.6.13 in the inherited roadmap; now Claude's call per charter §3). Then queue the first end-to-end piece — pendulum bob is the candidate per `WORKPLAN.md`'s POC track. Per charter §9 (iteration discipline), queue stays modest: one piece, learn from it, adjust, next piece.
