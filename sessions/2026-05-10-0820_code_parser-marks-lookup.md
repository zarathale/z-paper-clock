---
date: 2026-05-10
start_time: "08:20"
end_time: "08:45"
mode: code
participant: Zarathale (Alan)
target: parser-marks-lookup
orchestration_prompt: CODE_PROMPT_marks-layer-cross-piece-lookup.md
---

## Goal

Ship DECISIONS #12 — extend the cross-piece feature-lookup chain in `claude-work/scripts/build_assembly_graph.py` to consult the partner's `marks` layer, codifying the mark-first attach pattern that LAYER-CONVENTIONS.md has documented since 2026-05-07 morning but the parser never implemented.

## What was done

`claude-work/scripts/build_assembly_graph.py`:

- Renamed `_find_letter_match` → `find_partner_feature(letter, partner, self_id)`. Old name kept as a backwards-compat alias. Added optional `self_id` parameter so step 5b can match `landing-<letter><self>` typed marks on the partner.
- Replaced the 6-step lookup chain with the 8-step chain from LAYER-CONVENTIONS:
  - Step 4: partner marks bare-letter exact match → `marks-exact` (or `marks-exact-multi` when count ≥ 2). Includes Affinity collision-collapse: when partner has base `<letter>` mark AND `<letter>\d+` siblings (e.g. 099's `a, a1, a2, …, a11`), they sum to one logical multi-instance match. parse_marks itself was not modified per the prompt's "What NOT to Change"; collapse happens on-the-fly inside the resolver.
  - Step 5a: partner marks id == `mark-<letter>` → `marks-mark-prefix`.
  - Step 5b: partner marks typed-landing whose tab == letter and partner == self_id → `marks-landing-self`. Self-id normalized (strip leading zeros from numeric portion) so "094" matches partner-suffix "94".
  - Step 8: fuzzy substring on marks semantic part (after stripping `mark-`/`landing-`/`back-` prefixes), shortest-match tiebreaker → `marks-substring`.
  - Steps 1, 2, 3 (panel-exact, panel-tab, attach-points letter field) and 6, 7 (panel-substring, attach-substring) preserved verbatim. Order matters: marks steps 4-5 fall after step 3 (attach-points), before step 6 (panel-substring fuzzy).
- Updated both call sites in `build_connection_graph` to pass `edge["from"]` as `self_id`. When the match record carries `count > 1`, the validated edge gains `matched_panel_count`.
- Markdown emission: cross-piece edges and inferred-edges tables render `<id> (×N)` in the `partner match` column when count > 1.

Script-loop change (necessary for the motivating 093b → 093a case to even be reachable — the script previously only loaded `<dir>/<dir>.svg`, missing letter variants):

- `parse_piece` now uses `svg_path.stem` for piece id (was `svg_path.parent.name`).
- `parse_sidecar` now takes the SVG path and reads its sibling `.json` (was: parent dir + dir name + `.json`).
- `main()` now globs `*.svg` per piece directory, accepting stems matching `<dir>` or `<dir><single-lowercase-letter>`. Stray Affinity untitled exports (`Document.svg` etc.) are skipped.

`preview.html`: not modified. preview.html consumes `connection-graph.json` read-only — it reads `pivot_clusters` (line 803, 1310) and counts `edges[].valid` (line 1403) but does no per-piece letter resolution of its own. The regenerated JSON automatically flows through.

`claude-work/state/connection-graph.{json,md}`: regenerated.

Verification (Task 4 expected diffs):

- ✅ NEW edge: 093b → 093a, `attach front x → x, marks-exact`. Motivating bug fixed.
- ✅ 094 → 095 attach front a: was `pane1, panel-substring` → now `mark-a, marks-mark-prefix`.
- ✅ 097 → 099 attach front a: was `main, panel-substring` → now `a (×12), marks-exact-multi`. Multi-instance count surfaces correctly.
- 066-cluster: 3 edges shifted from panel-substring to mark-anchored — `065→066 attach h` (now `landing-h65, marks-landing-self`); `068→069 attach h/i` (now `h, marks-exact` / `i, marks-exact`). The prompt's "no via shifts" check was overly strict; per DECISIONS #12 mark-anchored matches are the documented intent and should win over panel-substring fallback. All edges remain `valid ✓`.
- 30 valid authored edges total (was 24). Unrelated new pieces 001/038/041/044/045/047/090/100/113 entered the graph too (their SVGs have been authored since the previous regen).

## Branch / commit

Branch: `claude/parser-marks-lookup` (renamed from auto-generated `claude/romantic-joliot-6552e6` per CLAUDE.md "branch name (strict)" rule before first commit).

Commit SHA: TBD — will be added after the commit lands.

## Open questions

None blocking. Two follow-ups parked:

- 097 period-suffix `attach-a99.{1..5}` pattern (mentioned in DECISIONS #12 follow-up) — Option A (this PR) might already cover the registration ambiguity that motivated the period-suffix proposal, since multi-instance marks return as a logical set. Worth a Cowork beat to decide before authoring the suffix convention.
- The 066-cluster exemplar table in LAYER-CONVENTIONS.md still describes 068 → 069 'h'/'i' as `panel-substring (×2)` matching `bh`/`ai`; that's now `marks-exact` matching bare `h`/`i` marks on 069. The convention text drifted slightly behind the SVG state (069's marks were `mark-h, mark-i` at write time, now `h, i`). Worth a doc refresh in a future Cowork pass.

## Next-session handoff

PR should land cleanly. After merge, the regenerated graph stays in tree (committed as part of this PR). Pose-capture + scene-mode work (preview.html PR B, C) can now rely on the graph having the new mark-anchored resolutions; in particular 095's bob-cluster work has `mark-a` as a clean target rather than the accidental `pane1` substring match.
