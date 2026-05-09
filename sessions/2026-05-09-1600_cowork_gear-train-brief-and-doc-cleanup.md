---
date: 2026-05-09
start_time: "16:00"
end_time: "16:45"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Drop a top-down authoring brief for the gear train into `to-alan/`, then sweep the stale doc references the brief surfaces.

## What was done

**Gear-train brief.** New file at `claude-work/to-alan/gear-train/README.md`. ~330 lines covering the §II.B + §II.D mechanism block (~50 pieces — the colloquial "gear train" actually spans both book sections, joined only by the crossed rubber band from motor-pinion pulley 48 to hand-mechanism pulley 89). Sections: kinematic chain diagram with timing vs. display branches; shared-axles table (with two real ambiguities flagged); five sub-stack maps (motor / middle / escape / reduction-gear / hands) each with piece inventory by role, function-block candidates, and per-stack author-time notes; function-block schema draft (`type` / `teeth` / `diameter_mm` / `drives` / `driven_by` / `engagement`); recommended authoring order respecting Alan's priority (hands before drive weight, after reduction gear). Stand-alone planning brief — Alan opted out of per-piece cheat sheets, so no follow-on cheat-sheet drops are coming behind it.

**Naming-truth corrections surfaced** (in the brief as questions for bench-eye confirmation, not unilateral renames):

1. **087 is not the escape wheel.** Per embedded-labels panel F: *"Piece 87 — Reduction-gear disc."* Per instructions §II.D it's the last piece in the reduction-gear assembly (81–87). The actual escape wheel is **058 + 059** glued back to back. STATUS / QUEUE / PROJECT-STATE wording inherited from bench shorthand has been corrected (see below).
2. **§II.B is only the three wheels.** The book's §II.B Mechanism is motor + middle + escape (33–64) only. Reduction gear (81–87), hand-mechanism pulley (88–90), minute / hour hand wheels (73–80) are all in §II.D Mechanism of the Hands. The "§II.B gear train" framing in next-actions was wrong.
3. **103 contradiction.** `pieces.csv` (`section: reduction-gear`) and embedded-labels (*"Small reduction gear with central spiral pattern"*) vs. instructions §II.E prose (*"Glue in the bottom, piece 103"* — weight-cylinder bottom disc). Both could technically be true (a disc with spiral pattern can be a cylinder bottom) but the section tag is wrong if so. Bench-eye confirmation needed before flipping `pieces.csv`.
4. **074 contradiction.** `pieces.csv` (`section: anchor-pendulum`, *"Thin strip (hook form)"*) vs. instructions §II.D (*"Assemble pieces 73, 74, 75, and 76 to produce the wheel of the minute hand"*). Bench-eye confirmation needed.

**Doc cleanup pass** (six edits, three files plus the brief):

- **CLAUDE.md ¶3 of "What This Repo Is"**: dropped the stage-production metaphor sentence (it contradicted the operating-stance section added 2026-05-07). Lead-in clause "Lean into the metaphor when it helps" went with it.
- **CLAUDE.md Session Startup step 2**: `WORKPLAN.md` → `claude-work/STATUS.md` (+ parenthetical pointer to `claude-work/QUEUE.md` for what's queued). Per `claude-work/DECISIONS.md` #2, WORKPLAN was frozen at charter sign-off and replaced by STATUS.md; the startup checklist hadn't caught up.
- **STATUS.md Charter rollout next_action**: "087 escape wheel is next" → "gear train next, brief at `claude-work/to-alan/gear-train/`; 087 reduction-gear disc currently on the bench."
- **STATUS.md SVG layer authoring next_action**: "(escape-wheel — first gear-disc piece...)" → "(reduction-gear disc — first gear-disc piece authored...)"; "§II.B gear train (087 unblocks the rest of the train)" rewritten to point at the brief and acknowledge the §II.B + §II.D split with kinematic-independence note (timing chain and display chain are kinematically separate, so stack ordering has flex).
- **PROJECT-STATE.md In Progress block, SVG layer authoring line**: same correction pattern — "087 escape-wheel" → "087 reduction-gear disc"; gear-train brief link added; §II.B-only framing dropped.
- **gear-train brief itself**: three spots updated to remove cheat-sheet promises since Alan said no cheats. "What this brief is, and isn't" second paragraph rewritten; "What I'm not including" first bullet rewritten; footer reframed as stand-alone planning brief.

Verification grep across the repo: no remaining "087 escape-wheel" claims in live docs. Remaining matches are all in historical session notes (which stay as written per doc-sweep convention) and in the brief itself where the corrections are appropriately discussed.

## Open questions

- **Naming-truth corrections to source-of-truth files.** The brief flags 074 / 103 / 087 / `pieces.csv` section tags for `088`/`089`/`090` (currently `reduction-gear`, but per book §II.D they're the hand-mechanism pulley). All deferred to bench-eye confirmation before rolling into `pieces.csv` + embedded-labels. Once confirmed, follow-on doc-sweep pulls them through.
- **Function-block schema lock-in.** Drafted in the brief as a JSON sketch but not formally specced. Probably gets settled at the bench when 058/059 escape wheel ships and the first function block is populated. May or may not need a CODE_PROMPT — if the schema lands clean at the bench, a chat-side settling is enough; if it surfaces edge cases (e.g. pinion leaf counts, the escape↔anchor engagement geometry) the schema deserves a SPEC-side update.
- **Free-swinging-element physics** (pulley 42 free-spinning rewind, pendulum bob, drive weight on string). Surfaced in the brief's motor-wheel section; deferred to Alan's timing for a separate design conversation.
- **Brief format reaction.** This is the first per-block planning brief (vs. per-piece cheat sheet). Length is ~330 lines for ~50 pieces, mostly the per-stack maps. Future-block briefs (drive weight, face/case) inherit this format unless Alan pushes back.

## Next-session handoff

If picking up next: Alan's reaction to the brief is the starting point — accept / push back / reorder the stacks. If Alan starts at the bench instead, no Cowork side-work is owed unless a stack surfaces a convention question or 058/059 lands and the function-block schema needs a real lock-in.

The two stale `CLAUDE.md` spots flagged in `sessions/2026-05-07-2030_cowork_claude-md-operating-stance.md` are now closed. Several `pieces.csv` + embedded-labels corrections are queued (074, 103, possibly 088/089/090 section reorg) pending bench-eye confirmation; if Alan resolves any of them in chat, the doc-sweep is small and can fold into any pass that touches `pieces.csv`.

QUEUE.md was not touched this session — its Now slot is empty (tagging closed 2026-05-07; the gear-train brief lives in to-alan/, not QUEUE) and Soon entries are unchanged. Worth a small QUEUE refresh next session to surface the gear-train block as a Now or Soon item depending on how the bench cadence shapes up.
