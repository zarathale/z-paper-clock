---
date: 2026-05-02
start_time: "07:30"
end_time: "08:00"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Split the unified `CODE_PROMPT_preview-html-v1.md` into two execution-sized prompts after two Code sessions failed to ship the unified prompt — one ran for 30 minutes of thinking with no output (2026-05-01 evening), the second hit the 32000-output-token ceiling and burned remaining usage budget while continuing to think (2026-05-02 morning).

## What was done

- Surveyed repo state: `claude/preview-html-v1` branch exists locally but is at `34c8855` (zero commits ahead of `main`); no `preview.html` was ever written; stale prunable worktree at `.claude/worktrees/magical-rosalind-9811e1`; nothing pushed to origin; no PR; no session note from either failed Code attempt. Nothing salvageable. Diagnosis (inference, not certain): the unified prompt asked for ~12 dense tasks producing a single ~1000-line HTML file in one Code response, which exceeded the output-token budget. The 30-minute think loop with no output is unexplained.
- Drafted `CODE_PROMPT_preview-html-v1a.md` (`ready-for-code`): file skeleton + CDN imports + UI shell (with v1b-fold-sliders placeholder) + full SVG parsing (folds parsed but unused) + silhouette extraction + three.js scene setup + single-slab geometry + axle markers + thickness slider + console diagnostics. Ships a checkable artifact: drop 069/066, see flat single-slab render with scan texture mapped.
- Drafted `CODE_PROMPT_preview-html-v1b.md` (`draft`): extends v1a with global + per-fold sliders, polygon cut, adjacency + BFS, multi-panel slab build via the v1a slab-builder function, hinge hierarchy, axle re-routing by point-in-polygon, fold animation. Status held at `draft` because v1a's actual function signatures and `parsed` object shape are unknown until v1a ships; v1b should be re-tightened against v1a's session note before flipping to `ready-for-code`.
- Edited `CODE_PROMPT_preview-html-v1.md` front matter: `status: ready-for-code` → `status: superseded`; added `superseded_by: preview-html-v1a + preview-html-v1b`; added italic header explaining the split. Body preserved as-is as the unified architectural vision and decision record.
- Inlined the algorithm-dense task content (silhouette extraction in v1a; polygon cut, adjacency + BFS, hinges in v1b) verbatim from the original prompt, so each split prompt is operationally self-contained — no jumping between files mid-task.

No code written. No SVG files touched. No CLAUDE.md or SPEC updates needed (this prototype isn't tracked in the status table).

## Open questions

- v1b's edit targets in Tasks 1, 4, 6, 7 reference `buildSlab` and `parsed.folds` as placeholder names. v1a's session note must capture the actual ship-time names so v1b can be tightened before its Code session.
- Why the first Code attempt thought for 30 minutes with no output is still unexplained. If v1a hits the same wall, that's a signal the issue isn't just output-token budget and we need a different diagnosis.

## Next-session handoff

1. Cleanup the residue from the failed attempts on Alan's mac. From repo root in Terminal:
   ```
   git branch -D claude/preview-html-v1
   git worktree prune
   ```
2. Commit the three CODE_PROMPT changes + this session note via GitHub Desktop using the message below.
3. Open a Code session against `CODE_PROMPT_preview-html-v1a.md`. Branch will be `claude/preview-html-v1a`.
4. After v1a ships, return to Cowork briefly to re-tighten `CODE_PROMPT_preview-html-v1b.md` against v1a's actual API (function signatures, `parsed` object shape). Then flip v1b to `ready-for-code` and run a second Code session.
