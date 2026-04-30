---
date: 2026-04-30
start_time: "16:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Close out M1's Cowork-owned sidecar drafting (task 1.6) and bake in the Code-session friction lessons from PR #1 so the next Code session is substantially smoother. Also recover from a same-session branch-deletion mishap.

## What was done

**Recovery from accidental branch deletion.** PR #1's branch (`claude/vigorous-rhodes-06b447`, two commits at `60a9fb6` and `65f49c8`) was deleted via GitHub Desktop mid-session. Confirmed local branch refs were intact, walked Zarathale through `git push origin claude/vigorous-rhodes-06b447` to re-publish; PR #1 was then merged via the GitHub UI and pulled to local `main` (merge commit `9a7584b`).

**Authored 11 plate-D sidecars (M1 task 1.6).** Drafted `piece-NNN.json` for all 11 plate-D pieces (4, 10, 18, 19, 26, 29, 30, 31, 32, 91, 92), sourced from `source/transcriptions/embedded-labels.md` Panel D + `source/transcriptions/instructions.md` §II.A and §II.D. `make validate` (run as `python3 04-validate-sidecars.py` from the sandbox) reports 11 pass / 0 fail / 4 warn; all four warnings are expected cross-plate cases (4× connections to piece 25 on plate C from pieces 4/10/26; 2× connections to piece 41 on plate F from piece 92), each documented in the affected sidecar's `notes` field.

**Documented assumptions in the sidecars.** The Panel D phrasing "each [of pieces 4 and 10] carries a₂₉…h₂₉" is physically ambiguous — piece 29 only has a single set of a–h tabs. Resolved this by splitting tabs a–d to piece 4 and e–h to piece 10, with the assumption flagged in piece-004.json, piece-010.json, and piece-029.json notes for confirmation during M1 task 1.5 (Inkscape pass). The `a₄₁`/`b₄₁` labels on piece 92 are flagged as suspicious in that piece's notes — piece 41 is a motor-wheel pulley strip with no obvious physical relationship to a hand-mechanism spacer; likely a transcription artifact, but reproduced faithfully pending scan re-inspection. Pieces 91 and 92 share a single declared axle id (`minute-hand-axle`), which lets the linter's axle-cross-reference check pass within plate D without dependence on piece 92a (which lives on a different plate).

**Three Code-session friction fixes.**

1. **Pre-approved tool patterns at `.claude/settings.json` (committed).** Drafted in the outputs folder because Cowork can't write to `.claude/` directly. Pre-approves the Bash patterns Code reaches for in this repo (`git`, `make`, `python`/`python3`/`python3.12`, the venv binaries, `pip`/`pip3`, `brew`, `potrace`, `gh`, `node`/`npm`/`pnpm`/`npx`, plus read-only inspection: `ls`, `cat`, `rg`, `find`, `grep`, `head`, `tail`, `wc`, `diff`, `awk`, `sed`, `jq`, `tree`). Destructive ops (`rm`, `mv`, `cp`) and WebFetch are deliberately left out so they continue to prompt. Per-machine overrides go in `.claude/settings.local.json` (gitignored). The file needs to be moved from outputs to `.claude/settings.json` by Zarathale; instructions in the closing message.
2. **`.gitignore` updated** to add `.claude/worktrees/` (Claude Code internal worktree state) and `.claude/settings.local.json` (per-machine overrides), so neither leaks into commits.
3. **CLAUDE.md updated** with two changes: (a) a new "Dev environment (mac)" section documenting what Code can assume is installed (Python 3.12, native potrace, gh CLI authenticated, Inkscape, the venv package list, plus what's NOT installed yet) so Code stops re-probing the env at session start; (b) a strengthened branch-naming callout in the Code Git Workflow section explicitly forbidding the `claude/vigorous-rhodes-…` auto-generated names and giving the rename command if Claude Code starts on one.

**ROADMAP + CLAUDE.md status sync.** ROADMAP M1 task 1.6 flipped to `done`; M1 milestone-index row updated to note only task 1.5 (Inkscape pass) remains. CLAUDE.md "Where We Are" row mirrored the same.

## Branch / commit

Cowork session — no branch. Commit message provided to Zarathale at end of session for GitHub Desktop.

## Open questions

- **Piece 92's `a₄₁`/`b₄₁` labels.** Sidecar takes the labels at face value but flags them as suspicious. Resolution can wait for M1 task 1.5 (when piece-092.svg is open in Inkscape and Zarathale can read the actual glyphs) or for a dedicated scan-cross-check pass. If the labels really are `a₄`/`b₄` (connecting to piece 4 instead of piece 41), the fix is a one-line edit in piece-092.json.
- **The a₂₉…h₂₉ tab split between pieces 4 and 10.** Same disposition — confirm during the Inkscape pass.
- **Plain `a` tab on piece 30.** Panel D lists `a, b, c` on piece 30; `b` and `c` reciprocate cleanly to piece 29's `b₃₀`/`c₃₀`, but `a`'s counterpart isn't documented in any other plate-D piece. Likely connects to piece 4, but no `a₃₀` subscripted label was transcribed there. Left out of connections; same Inkscape-pass disposition.

None of these block M2.

## Next-session handoff

The next Cowork session can pick up M1 task 1.5 (the Inkscape hand-edit pass on the 11 plate-D piece SVGs). Per the Code-session note (`sessions/2026-04-30-1500_code_M1-pipeline-plate-d.md`), pieces 004 and 010 (the tall hand-trace-bucket strips) need significant cleanup; auto-trace-clean pieces (26, 31, 32, 91, 92) need the lightest touch. The Inkscape pass is also the natural place to resolve the three open-question items above.

After 1.5 ships, M1 closes and M2 begins (per ROADMAP §"M2 setup tasks", starting with task 2.1: full bucket triage across all remaining plates).
