---
date: 2026-05-05
start_time: "07:00"
end_time: "23:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Long-form working session running the day after the panels-first orientation reset (DECISIONS #6). Started as a "first day on the job" briefing requesting state-of-the-project; expanded into a full anchor-pendulum batch authoring pass with Alan at the bench and Claude doing convention-side QA + scripting + decision-locking on each piece. Goal: take panels-first from a 1-piece experiment (069 from the previous evening) to a stress-tested convention across a coherent multi-piece subassembly, and tee up the panels-aware parser pathway in `preview.html`.

## What was done

### Session arc

The day ran in three roughly-overlapping phases:

**Phase 1 — onboarding + housekeeping (morning).** "First day on the job" briefing covered project state, charter, current tracks, decision-record state. Alan flagged that plate B brackets 013-017 are all clones of 012 (six bracket pieces, identical drawings) — replicated `source/pieces/012.png` → `013/014/015/016/017.png` (overwriting redundant 015 scan), MD5-verified. Pieces.csv updated. Source-side capture closed at 123/123 after Alan also captured + initialized 090 + 110 in `work/pieces/` during the day. Lock-file verification (`git ls-files | grep -F "af~lock~"`) returned empty.

**Phase 2 — anchor-pendulum batch authoring (afternoon-evening).** Alan authored 8 panels-first pieces over the course of the bench session: 067 (anchor rear plate), 068 (anchor fork), 069 already from the previous evening, 070 (pendulum rod), 071 (square ring), 072 (pendulum blade), 099 (saw-toothed crescent), 100 (bob-position disc — flat, no panels). Then 065 (zig-zag anchor arm) and 066 (pendulum-blade tube/casing — the co-linear-fold acid test) landed late in the session. Each piece got a Claude QA pass after Alan exported; convention refinements surfaced piece-by-piece. The QA dynamic worked well: Alan would author + export, Claude would read the SVG, surface issues + name conventions, Alan would respond + iterate.

**Phase 3 — connection-graph audit + lock-in (evening).** Built `claude-work/scripts/build_assembly_graph.py` to read panels-first SVGs and produce the cross-piece connection graph at `claude-work/state/connection-graph.{md,json}`. Several bug-fix iterations to handle: bare `<letter><piece>` form on 065's attach-points (renamed to `attach-<letter><piece>` for clarity), bare letter targets like `j` on 068 (Alan moved from marks to attach-points), fuzzy substring matching across composite letter panels (`bh`/`ai`), prefix-stripping to avoid false-positive matches like "h" in "atta**c**h-d66", shortest-match tiebreaker (so `ai` beats `main` for letter `i`). Final state: **24/24 cross-piece edges valid** across the 9 panels-first pieces. Conventions ratified by the audit; DECISIONS row #7 captures the 21 specific convention elements locked.

### Convention elements locked (the 21-point list)

Compactly:

1. Bare-alias panel ids (no `panel-` prefix)
2. `fold-<a>-<b>` direct binding to two panel ids
3. `fold-<descriptive>` for single-panel/curved folds
4. Curved fold elements (`<circle>`/`<ellipse>` inside fold layers)
5. Composite letter panels (`bh`, `ai`)
6. `attach-points` = structural cross-piece refs only
7. `marks` = same-piece-or-decorative
8. `attach-<letter><piece>` distinct from `landing-<tab><piece>`
9. `landing-<panel-id>` (no piece suffix) = same-piece closure landing
10. `align-<letter><partner-piece>` paired symmetric registration
11. `cut-<descriptive>` prefix form (passage + accommodation)
12. Bare `hole` semantics (same-piece hardware pin)
13. `back-<form>` prefix = back-side annotation
14. `landing-back-X` vs `back-landing-X` disambiguation by leading token
15. Multi-instance markers in `marks` (oriented frame for N≥2)
16. Affinity collision-suffix tolerance (`<id><digits>` = same logical id)
17. Parser tolerance for `cutaway`/`cutout-` in panels layer
18. Panels mandatory on every piece
19. Derived pivots (rigidly attached pieces inherit rotation)
20. Dual-presence pattern (typed landing as both panel and mark)
21. Fuzzy substring matching with prefix-stripping + shortest-match tiebreaker

Full reference at `LAYER-CONVENTIONS.md` (rewritten this session as the single canonical doc). DECISIONS row #7 captures the lock formally.

### Files changed

- `LAYER-CONVENTIONS.md` — full rewrite as the panels-first canonical reference. Covers 8 layers, per-element id conventions, parser rules, patterns (dual-presence, derived pivots, composite letters, closure landings), common slips. Co-authored per Decision #3.
- `LAYERS.md` — **deleted.** The v0 cheat sheet from earlier the same day was redundant with the rewritten LAYER-CONVENTIONS.md.
- `claude-work/scripts/build_assembly_graph.py` — new. Reads panels-first SVGs in `work/pieces/`, extracts panels + folds + attach-points + marks, builds typed cross-piece connection graph with fuzzy substring matching and shortest-match tiebreaker. Outputs `claude-work/state/connection-graph.{md,json}`.
- `claude-work/state/connection-graph.md` + `connection-graph.json` — new. The current state of the cross-piece graph: 10 panels-first pieces processed, 24/24 cross-piece edges valid, 1 pivot cluster (anchor), 10 untyped landings (closures + back-side, intentional).
- `claude-work/DECISIONS.md` — added row #7 (comprehensive panels-first convention lock-in).
- `claude-work/QUEUE.md` — moved Soon #6 (panels-aware parser pathway) status to "ready-for-code" with the prompt drafted; added 2 entries to Recently shipped (anchor-pendulum batch + connection-graph audit script).
- `claude-work/STATUS.md` — updated SVG layer authoring track (next move is bob pieces + escape wheel batch); preview.html iteration track (next move is the Code session against the new prompt); top-of-file summary.
- `CODE_PROMPT_preview-html-panels-aware.md` — new at repo root. Hand-off prompt for the next Code session: adds the panels-aware parser pathway to `preview.html` alongside the legacy cut-line-first path. 8 numbered tasks, verification across 069/068/071/099. Single-piece scope.
- `work/pieces.csv` — earlier in the session: 013-017 status flipped to `captured` with clone notes; 090 + 110 also flipped.
- `source/pieces/013.png`, `014.png`, `015.png` (overwriting), `016.png`, `017.png` — replicas of 012.png.

### Per-piece authoring activity (Alan-side, summarized)

- 067: panels-first complete (single `main` panel; 4 cross-piece landings to 069 + shared pivot)
- 068: panels-first complete (19 panels, 17 folds, 3 attaches to 069 + j letter-target). The most complex piece in the batch; surfaced the `back-` prefix and `attach-<letter><piece>` form
- 069: stable from the previous evening (11 panels, 10 folds; the test piece for panels-first)
- 070: panels-first complete (13 panels, 2 folds; cut marks `cut-a72` + `cut-a721` for accommodation)
- 071: panels-first complete (4 letter panels a/b/c/d, 3 folds, cross-piece landings to 070)
- 072: panels-first complete (single `main`, bare `hole` for hardware pin)
- 099: panels-first complete (2 panels: `main` + `tabb`; 3 folds incl. 2 curved circle-folds; 12-instance `id="a"` markers for triangle landings)
- 100: silhouette + marks only (no panels yet — flat disc; cuts `cut-lower`/`cut-upper`; alignment markers paired with 099)
- 065: panels-first complete (single `main` panel; axle marker `anchor-pivot` in axles; 7 attach-points to 066)
- 066: panels-first complete (22-23 panels incl. dual-presence b65/c65/.../h65; 21 folds bound; the co-linear-fold acid test cleanly resolved)

The connection graph entries from the final state:

- 065 ⇄ 066: 14 reciprocal edges (065 attaches to 066's letter regions; 066 has those as both panels and landing-marks)
- 066 → 068: 1 edge (landing-j68 ↔ 068's bare `j` in attach-points)
- 067 ⇄ 069: 4 edges + shared `pivot-anchor`
- 068 → 069: 3 attach edges (g/h/i resolved via composite panel matching)
- 071 → 070: 2 landing edges (b/c)

That's the full anchor cluster (065/066/067/068/069) + pendulum chain (070/071/072) connected and consistent.

## Branch / commit

Cowork session — no branch, commit message generated below for Alan to paste into GitHub Desktop.

## Open questions

**Decisions queued behind this session's locks:**

- **Bob pieces + escape wheel batch.** Next authoring batch (`094/095/096/097/098/093` for the bob; `087` likely the escape wheel). No prep work owed (Alan asked to skip cheat sheets unless explicitly requested). Pull when bench time.
- **Panels-aware parser ship.** `CODE_PROMPT_preview-html-panels-aware.md` is ready-for-code at repo root. Single-piece scope. Multi-piece scene assembly comes in a follow-up prompt once this lands.
- **Architecture call (DECISIONS #4: preview.html ↔ work/viewer/).** Still deferred. The panels-aware parser pathway will surface more about what `preview.html` is becoming; the architecture answer gets clearer as the panels-aware code lands.
- **`landing-h` and `landing-i` on 068 (untyped).** Could be typed cross-piece landings to 069 (`landing-h69`/`landing-i69`) but Alan kept them untyped. Worth a glance later — might or might not pair with 069's `bh`/`ai` panels.

**No blocking questions.** Conventions stable; tooling resolves; the path forward is clear.

## Next-session handoff

**Two paths Alan can pull from:**

1. **Code session** against `CODE_PROMPT_preview-html-panels-aware.md` — ships the panels-aware parser pathway in `preview.html`. After this lands, any panels-first piece can be rendered + folded + inspected. Big visual milestone.
2. **More authoring** — bob pieces + escape wheel. Conventions are stable; new pieces drop into the established pattern. Run the connection-graph script after each batch to see what validates.

Both are pull-based; pick what feels right.

When the Code session lands the panels-aware parser, the *next* cowork conversation is multi-piece scene assembly — using the cross-piece connection graph to position connected pieces relative to each other in 3D. That's the path to the first piece end-to-end milestone (CHARTER §6 commitment #2).

## Cowork commit message

```
panels-first batch authoring + connection graph script + LAYER-CONVENTIONS rewrite
```

```
End-to-end panels-first authoring of the anchor-pendulum batch (065/066/067/
068/069/070/071/072 + 099 + 100). 21 specific convention elements ratified
across the batch — from bare-alias panel ids and fold-<a>-<b> direct binding
through composite letter panels, the back- side annotation prefix, multi-
instance markers, dual-presence pattern, derived pivots, and fuzzy substring
matching with shortest-match tiebreaker.

LAYER-CONVENTIONS.md rewritten as the single canonical panels-first
reference. LAYERS.md (the v0 cheat sheet from earlier the same day) deleted
as redundant.

claude-work/scripts/build_assembly_graph.py shipped — reads panels-first
SVGs in work/pieces/, builds the cross-piece connection graph, validates
24/24 edges across the batch, outputs claude-work/state/connection-graph.
{md,json}. The data structure the M4 assembly engine will consume.

claude-work/DECISIONS.md row #7 captures the convention lock-in formally.
QUEUE.md and STATUS.md updated for the post-batch state — SVG layer
authoring next-move is bob pieces + escape wheel; preview.html iteration
next-move is the Code session against the new prompt.

CODE_PROMPT_preview-html-panels-aware.md drafted at repo root, ready-for-
code. Hand-off prompt for the Code session that adds the panels-aware
parser pathway to preview.html alongside the legacy cut-line-first path.
8 numbered tasks; verification across 069/068/071/099. Single-piece scope;
multi-piece scene assembly is a follow-up prompt.

Earlier in the session: source-side capture closed at 123/123 (013-017
resolved as clones of 012; 090 + 110 captured + initialized in work/pieces/);
Affinity lock-file cleanup verified clean; pieces.csv updated.

Session note: sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md.
```
