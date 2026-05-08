---
date: 2026-05-07
start_time: "17:00"
end_time: "17:50"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Close DECISIONS #4 (preview.html ↔ work/viewer/ architecture) and clarify the attach-point convention surfaced by 093b's `attach-x093a`.

## What was done

### Architecture — DECISIONS #4 locked

Reviewed the project state (STATUS.md, QUEUE.md, CHARTER.md) and discussed the three architecture options: (A) graduate `preview.html` into the viewer, (B) parallel tools with viewer deferred, (C) `preview.html` as the permanent viewer.

**Decision: Option B.** `preview.html` is permanently the authoring/QA tool — single-file HTML, `file://`, no build step. `claude-work/viewer/` will be built fresh in TypeScript + Vite when M3 is genuinely imminent (i.e., bulk authoring is done and the viewer is the actual bottleneck). No code sharing between the two for now; the SVG parser will get a clean TypeScript rewrite at M3 time when the conventions are fully mature.

Why not A: module extraction before any viewer work is a Code session with no new capability. Why not C: the charter mission (GitHub Pages static site, 123 pieces, inspect panel) needs a build system. Option B honours the charter and the §9 iteration discipline — don't build infrastructure ahead of the need.

CHARTER §6 commitment #3 (decide architecture) closed.

### attach-x convention clarified — mark-first attach pattern documented

Alan pushed back on the "glue-only inter-piece attach" framing in the prior session's QUEUE entry. Correct: virtually all `attach-` connections are glue; that's not a meaningful distinction. The real issue with `attach-x093a` on 093b was that `x` was invented and doesn't exist on 093a, so the parser can't resolve it.

Alan then surfaced the underlying convention that wasn't well documented: **mark-first attach pattern** — `attach-<letter><piece>` should reference a *mark* (small shape in the partner's `marks` layer, centroid = connection point) rather than a panel, because attach points are often a sub-portion of a panel. Marks pin the geometry precisely. The centroid of the authored mark shape is the default connection point; registration can be refined by testing placement in `preview.html` and adjusting the mark.

Printed tab letters from the book are the natural case (the letter is already a mark on the plate). When no printed letter exists, author a small mark on the partner at the joint and give it any unambiguous id.

**For 093b:** on next touch, place a mark on 093a at the joint edge (e.g. id `joint`), then change 093b's `attach-x093a` → `attach-joint093a`.

### Files changed

- `claude-work/DECISIONS.md` — #4 locked (Option B, full rationale)
- `claude-work/STATUS.md` — Charter rollout track next_action updated; preview.html track next_action updated; SVG layer authoring open-questions updated (attach-x rework guidance); log entries added to both tracks
- `claude-work/QUEUE.md` — Soon #2 (architecture call) struck through; Soon #4 (attach-x) struck through and rewritten with mark-first guidance; footer updated
- `LAYER-CONVENTIONS.md` — `attach-<letter><piece>` entry rewritten (mark-first preferred; centroid as connection point; never invent letters); new "Mark-first attach pattern" section in Patterns; two new entries in Common slips; footer updated

## Open questions

- 093a's panels: what id should the joint-edge mark carry? `joint` is the working suggestion; Alan decides on next 093 touch.
- Do the existing anchor-pendulum attach ids (e.g. `attach-g69` on 068) already resolve against marks in 069's `marks` layer, or against panels? Worth confirming that the mark-first pattern is already how those pieces are authored.

## Next-session handoff

- **087** (escape wheel) is the next authoring priority — first gear-disc piece, unlocks the §II.B gear train.
- 093a/093b fold paths still pending; 093b attach rework pending.
- DECISIONS.md, STATUS.md, QUEUE.md, LAYER-CONVENTIONS.md all updated this session.
