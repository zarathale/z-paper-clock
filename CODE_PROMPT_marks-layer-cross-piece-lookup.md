---
status: ready-for-code
started: 2026-05-07
owner: Zarathale (Alan)
target: parser-marks-lookup
---

## What You Are Doing and Why

Extend the cross-piece feature-lookup chain in `claude-work/scripts/build_assembly_graph.py` (and the parallel parser in `preview.html`) to consult the partner's `marks` layer in addition to `panels` and `attach-points`. This codifies the **mark-first attach pattern** that LAYER-CONVENTIONS.md has documented since the 2026-05-07 morning pass but that the parser never implemented — partner-side marks like 093a's `x`, 095's `mark-a`, and 099's 12×`a` multi-instance markers are currently invisible to cross-piece resolution, so today's "successful" resolutions through panel-substring fallback are accidental and sometimes point at the wrong feature (094 → `pane1` instead of `mark-a`; 097 → `main` instead of one of 099's `a` marks). 093b's `attach-x093a` won't resolve to anything when the connection-graph next regenerates because 093a has no panel matching `x` — that's the case that forced this change.

The convention text in LAYER-CONVENTIONS.md already describes the new behavior; this Code session is the implementation step. See DECISIONS #12 for the full design rationale and session note `2026-05-07-2200_cowork_attach-convention-sweep.md` for the sweep that surfaced the problem.

## Prerequisites — confirm before starting

- `claude-work/scripts/build_assembly_graph.py` exists and has the `find_partner_feature` function around lines ~490-545.
- `preview.html` exists at repo root and has its own panels-first SVG parser with cross-piece lookup logic (search for `attach-points` and the equivalent of `findPartnerFeature` / `resolveCrossPieceLetter` — exact name may differ).
- `python3.12` available; venv at `.venv/`.
- Authored panels-first SVGs at `work/pieces/065/065.svg`, `066/066.svg`, `068/068.svg`, `093/093a.svg`, `093/093b.svg`, `094/094.svg`, `095/095.svg`, `097/097.svg`, `099/099.svg` — these will be the verification targets.
- Read access to `claude-work/state/connection-graph.{md,json}` (the script writes to these — back up the current versions if you want a diff comparison post-change).

## Read These Files First

1. `LAYER-CONVENTIONS.md` — full file. Pay particular attention to the Parser-rules section (the new 8-step lookup chain), the "Mark-first attach pattern" subsection in Patterns, and the "066 cluster — worked exemplar" subsection.
2. `claude-work/DECISIONS.md` — row #12 specifically (the full design rationale including the tiebreaker behavior and multi-instance handling).
3. `claude-work/scripts/build_assembly_graph.py` — full file. The function to extend is `find_partner_feature`. Existing `parse_marks` (line ~368) already extracts marks-layer data — the structure each piece's record returns includes a `marks` list (line ~478).
4. `sessions/2026-05-07-1700_cowork_architecture-and-attach-convention.md` — the session that introduced the mark-first pattern in the docs (background context).
5. `preview.html` — search for the existing cross-piece resolver. It will likely be inline in the SVG-loading flow; locate it before editing.

## Target File Structure Changes

```
claude-work/scripts/build_assembly_graph.py    ← update: find_partner_feature gains 3 new lookup steps; emit `via` values for new steps; multi-instance handling
preview.html                                    ← update: equivalent cross-piece resolver gains marks-layer lookup
claude-work/state/connection-graph.md           ← regenerate (script output)
claude-work/state/connection-graph.json         ← regenerate (script output)
```

No new files. No file moves.

## Numbered Tasks

### Task 1 — Extend `find_partner_feature` in `build_assembly_graph.py`

Locate the function (currently ~6 numbered steps, lines ~490-545). Replace the body with the 8-step chain below. Keep the existing function signature and return shape (`{"id": <matched id>, "via": <which step>}` or `None`).

New chain (insert mark steps after panel-tab and after attach-points letter-field, before fuzzy):

```python
def find_partner_feature(letter: str, partner: dict) -> dict | None:
    """
    Find letter X on partner piece. Order:
      1. Exact panel id == letter            → via "panel-exact"
      2. Panel id == "tab" + letter          → via "panel-tab"
      3. Partner attach-points: parsed letter field == letter
                                             → via "attach-{kind}-letter"
      4. Partner marks: id == letter (exact bare-letter match; covers multi-instance)
                                             → via "marks-exact"
      5. Partner marks: id == "mark-" + letter, OR id matches "landing-<letter><self>"
                                             → via "marks-mark-prefix" / "marks-landing-self"
      6. Fuzzy substring on panel id         → via "panel-substring"
      7. Fuzzy substring on attach-points semantic part
                                             → via "attach-substring"
      8. Fuzzy substring on marks semantic part (after stripping mark-/landing-/back- prefixes)
                                             → via "marks-substring"
    Tiebreaker for substring steps: shortest matching id wins; alphabetical tie-break.
    Multi-instance marks (N≥2 same id): return one match record but stamp via "marks-exact-multi"
    so the connection-graph md report can show "→ a (×N)".
    """
```

Implementation notes:

- The piece record returned by `parse_marks(svg_text)` (line ~368) is a list of dicts; each has `id` (the raw element id), `kind` (parsed kind from `parse_marks_id` if present, else `None`), `letter` field if applicable, etc. Inspect what the existing parser returns and use it; don't re-parse the SVG.
- For step 4 (exact bare-letter match): walk `partner["marks"]` looking for any mark whose raw id equals the letter exactly. If multiple match (multi-instance), it's a set match; record `via="marks-exact"` and append `(× N)` info into the return dict (new optional `count` field, default 1) so the renderer can show it.
- For step 5: same walk but match `id == f"mark-{letter}"` first, then any mark whose semantic part (stripping `landing-`, `mark-`, `back-` prefixes) equals letter.
- For step 8: same walk; substring match on the stripped semantic part.

Tiebreaker across steps that find candidates: keep the existing "shortest matching id wins" rule. Compare candidates within a single step; **don't** compare candidates across steps — the step ordering is the priority.

### Task 2 — Update the connection-graph emission to surface multi-instance matches

In the section that builds the `cross-piece edges` markdown table (search for the table headers `from | → | to | kind | side | tab/letter | partner match | matched via | valid? | prov | note`), update the row formatter so that when `find_partner_feature` returns a result with `count > 1`, the `partner match` cell renders as `<id> (×<count>)` instead of just `<id>`. The `matched via` cell renders as `marks-exact-multi` for those rows.

Same change to the JSON emission — every edge in `connection-graph.json` already has `partner_match` and `matched_via` fields; add `partner_match_count` (default 1) when applicable.

### Task 3 — Implement the equivalent in `preview.html`

`preview.html` has its own SVG parser used by the per-piece preview renderer. Find the function that resolves cross-piece letters in the panels-first parser (search for `attach-points` adjacent to a function that walks panels). Apply the same 8-step lookup. The preview's data structures may differ from the script's; keep the steps semantically identical, even if the implementation diverges.

The preview uses cross-piece resolution to (a) draw connection-graph edges in the side panel diagnostics, (b) flag unresolved attach-points with a banner. Both surfaces should now show marks-anchored resolutions.

### Task 4 — Regenerate the connection graph and visually diff

After the script change:

```bash
cd ~/Documents/GitHub/z-paper-clock
.venv/bin/python claude-work/scripts/build_assembly_graph.py
```

Expected diffs in `claude-work/state/connection-graph.md`:

- **NEW edge: 093 → 093a, attach front x, matches `x`, via `marks-exact`.** This row didn't exist before; with the change, it appears.
- **CHANGED edge: 094 → 095, attach front a.** Was `pane1, panel-substring`. Should now be `mark-a, marks-mark-prefix` (matches step 5 because mark id is `mark-a`).
- **CHANGED edge: 097 → 099, attach front a.** Was `main, panel-substring`. Should now be `a (×12), marks-exact-multi` (matches step 4 with multi-instance).
- **CHANGED edges: 097 → 098, attach front a/b.** Was `panea/paneb, panel-substring`. May or may not change depending on whether 098 has letter-`a`/`b` marks (it doesn't currently — these stay panel-substring).
- **097 → 991/992/993/994 partial-resolves.** Will continue to fail until 097 is re-uplifted (Affinity collision-suffix issue is separate from this change). Expected to remain in their current state.
- **No regressions on 066-cluster edges:** every 065→066, 066→065, 066→068, 067→069, 068→069 edge should still resolve via the same `via` it does today. The new mark steps come AFTER attach-points letter-field (step 3) and AFTER panel-tab (step 2), so existing high-priority matches don't shift.

If a 066-cluster edge changes its `matched via`, that's a regression — investigate and fix step ordering.

## Verification Checklist

1. `.venv/bin/python claude-work/scripts/build_assembly_graph.py` runs to completion with no exceptions.
2. `claude-work/state/connection-graph.md` regenerated; diff shows the expected changes from Task 4 (and only those).
3. The new edge `093 → 093a` appears with `via marks-exact`.
4. 094 → 095 now points at `mark-a` not `pane1`.
5. 097 → 099 now points at the multi-instance `a` set with `(×12)` annotation.
6. All 066-cluster edges (15 total per the current graph) still resolve and their `via` values are unchanged.
7. The closure-attach section (095's `back-attach-pane1/2/3`) is unchanged.
8. The pivots and untyped-landings sections are unchanged.
9. `preview.html` — open it locally, drag-drop `093a.svg` and confirm 093b's attach to it now resolves in the side-panel diagnostics. Repeat for `094.svg` (should show `mark-a` resolution).
10. Run the existing connection-graph regen smoke check: every edge with `valid? ✓` should still be `✓`; no `?` should turn into `✗`.

## What NOT to Change

- Do NOT modify any authored SVG files in `work/pieces/`. The convention text says "no re-authoring required" — that's load-bearing.
- Do NOT change the existing `parse_marks` / `parse_attach_points` / `parse_panels` parsers — the change is purely in the `find_partner_feature` resolver.
- Do NOT touch the closure-attach logic (same-piece `back-attach-<panel-id>`). Different code path.
- Do NOT touch the inferred-connections merger (`connections.inferred[]` from sidecar). Orthogonal.
- Do NOT bump any version numbers — this is pipeline tooling, not a viewer change.
- Do NOT alter the connection-graph markdown structure (table headers, section ordering) beyond what Task 2 requires.
- Do NOT solve the 097 period-suffix or Affinity-collision-suffix problem in this PR. That's a separate decision parked in DECISIONS #12 follow-up; surfacing it now would expand scope.

## Manual tests

After merge:

| Pre-condition | Action | Expected post-condition |
|---|---|---|
| Connection-graph is the post-Option-A version | Visit `LAYER-CONVENTIONS.md` "066 cluster — worked exemplar" table | Every row's "via" column matches what the regenerated graph says for that edge |
| 093 SVGs unchanged | Open `preview.html`, drop `093b.svg` | Cross-piece diagnostics show resolution to mark `x` on 093a (no banner) |
| 094 SVG unchanged | Open `preview.html`, drop `094.svg` | Cross-piece diagnostics show `attach-a95 → mark-a` (not `pane1`) |
| 097 SVG unchanged | Open `preview.html`, drop `097.svg` | Cross-piece diagnostics show `attach-a99 → a (×12 multi-instance on 099)` |

Branch name suggestion: `claude/parser-marks-lookup`.
