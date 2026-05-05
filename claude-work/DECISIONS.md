# DECISIONS.md — Claude-led decision record

_Parallel to the inherited `CLAUDE.md` Architectural Decisions (Closed) table. Decisions made before charter sign-off (2026-05-04) live in their original homes (CLAUDE.md, the relevant CODE_PROMPTs, the relevant session notes). New decisions land here. Co-authored decisions on `LAYER-CONVENTIONS.md` are noted here too, but the file itself stays at repo root._

---

## How this file works

A row per decision. Each row captures:

- **#** — sequential, never reused.
- **Date** — when the decision was made.
- **Decision** — what was chosen.
- **Why** — the one-paragraph reasoning. Future-Claude reads this when tempted to reopen.
- **Type** — `Claude-led` (CHARTER §3 says I pick), `Co-authored` (LAYER-CONVENTIONS or charter amendment territory), `Inherited` (carried forward from pre-charter; cited here for visibility).
- **Reopen?** — `closed` or `open` (still in motion). Once closed, don't reopen without an explicit conversation.

---

## Decisions

### #1 — Charter signed and effective

- **Date:** 2026-05-04
- **Decision:** `claude-work/CHARTER.md` v1.0 signed. Claude takes the lead; Alan steps into a human-assistant role. All decisions captured in CHARTER §10 (rows 1–8) carry forward as decisions of record (clean-break folder rename, LAYER-CONVENTIONS co-authoring at repo root, sidecar JSON colocation in alan-work/, pipeline migrating to claude-work/, audit script under claude-work/, day-one skeleton scope, WORKPLAN→STATUS succession, agreed first-moves order).
- **Why:** described in the charter itself. Doc-level: Alan was leading and wanted to hand the build over with the source material in hand. Alan-as-supporter / Claude-as-builder is the new shape.
- **Type:** Co-authored (kick-off exception per CHARTER §11; charter amendments going forward follow §12).
- **Reopen?** closed. Amendments are how this changes — see CHARTER §12.

### #2 — STATUS.md replaces WORKPLAN.md as the live working surface

- **Date:** 2026-05-04
- **Decision:** `claude-work/STATUS.md` is the live work-state surface as of charter sign-off. `WORKPLAN.md` is frozen as the pre-charter record; not deleted, not maintained going forward. Eight tracks carried forward; one (Operations layer) closed; one (Charter rollout) opened.
- **Why:** CHARTER §3 + §10 row 7. WORKPLAN.md was a pre-charter artifact in the operations-layer track; the work it captured is now Claude-owned, so its successor lives under `claude-work/`. Keeping WORKPLAN in place avoids the find/replace pain of folder/path renames in the inherited docs and leaves a clean decision record of what was open at hand-off.
- **Type:** Claude-led (within the charter's mandate; CHARTER §10 row 7 explicitly resolved this).
- **Reopen?** closed. If STATUS.md proves insufficient, the move would be amend the format, not unwind the succession.

### #3 — LAYER-CONVENTIONS.md co-maintenance routine

- **Date:** 2026-05-04
- **Decision:** `LAYER-CONVENTIONS.md` stays at repo root, co-authored ongoing per CHARTER §3 + §10 row 2. Working routine: (a) for already-settled-and-shipped conventions, edits are unilateral (typo fixes, additional examples, scannable wording improvements); the editor adds a one-line dated note to the file's footer ("2026-05-XX: tightened folds-section example for clarity"). (b) For new conventions or changes to settled ones, both sides talk it through in chat first; the agreed shape lands as a CLAUDE.md Architectural-Decisions row (or a DECISIONS.md row, if the convention is post-charter), and LAYER-CONVENTIONS.md gets updated as part of the same pass. (c) The audit script in `claude-work/` reads `LAYER-CONVENTIONS.md` wherever it lives — no path coupling.
- **Why:** Two-person co-maintained doc shouldn't be over-formalized; a paragraph beats a process. Settled conventions don't need a round-trip for typo fixes; in-motion conventions do. The audit-as-linter pattern decouples convention changes from any particular tooling release.
- **Type:** Co-authored convention. (Alan: signed off implicitly by the charter; if this routine doesn't fit, ping me and we tighten it.)
- **Reopen?** open-but-stable. Worth revisiting after the next 2-3 convention changes to see if the routine actually held up.

### #4 — preview.html ↔ work/viewer/ architecture (PENDING)

- **Date:** TBD (deferred to next cowork conversation)
- **Decision:** TBD. The inherited SPEC's open question 0.6.13 (graduate `preview.html` into `work/viewer/`, build a fresh viewer alongside, or replace `work/viewer/` outright) is parked until the face-graph diagnostic ship + the post-diagnosis algorithm pick teach more about what `preview.html` is becoming. **Update 2026-05-05:** the diagnostic harness shipped (PR #13) and cut-trim shipped (PR #14); the post-diagnosis pick happened. The orientation/awareness reset (Decision #6) now sits between this decision and any new code — if framing B (panels-as-polygons) wins, the parser surface preview.html exposes changes shape, which changes the answer here. Still deferred; reasoning unchanged in spirit, just one step further along the chain.
- **Why deferred:** picking the architecture before the next two `preview.html` ships would be premature. The diagnostic harness is going to surface whether the current parser-as-it-stands holds up under shared-edge / cut-trim / multi-tag refactoring or hits a wall. That information changes whether graduating `preview.html` is the obvious move or whether a from-scratch `work/viewer/` (per the inherited TS/Vite/three.js SPEC) would absorb the rewrite better. CHARTER §6 #3 commits to picking; nothing in the charter commits to picking *yet*.
- **Type:** Claude-led when it lands.
- **Reopen?** open — this is the decision to make next, just not today.

### #5 — Cut-trim uses `fold.start`/`fold.end`, not `authoredStart`/`authoredEnd`

- **Date:** 2026-05-04 (Code session 21:03)
- **Decision:** The cut-trim refactor of `buildFaceGraph` (PR #14, commit `e0cb5cb`) cuts each region using each fold's `fold.start`/`fold.end` — the existing `extendFoldsToSilhouette` outputs (extend each authored segment to the **nearest** silhouette boundary in each direction) — rather than the literal `fold.authoredStart`/`fold.authoredEnd` the prompt specified. The behavioral difference: literal authored endpoints frequently sit a few units inside the silhouette polygon (Alan's standard authoring imprecision in Affinity), causing `findSegmentPolygonCrossings` to return 0 hits and skipping the cut entirely; `fold.start`/`fold.end` bridges the gap to the nearest boundary without reverting to the bigBox infinite extension that defined the old half-plane model.
- **Why:** the literal-spec implementation produced 1 fold-edge for all of piece 066 (0 cuts triggered). The session-note triage walked through the geometry and surfaced this as a real gap between authoring practice and parser expectation. The chosen behavior is strictly better for normal pieces (clean) and partially-better for 066 (27 regions instead of 1; 17/17 markers resolve; 13 orphan regions remain via residual over-reach on long strips). The "snap-only extension" tweak (only extend if endpoint is within `0.005 * diagLen` of silhouette) is a known follow-up that would close the residual; it's parked because the orientation/awareness reset (Decision #6) may obsolete cut-line-first entirely.
- **Type:** Claude-led, executed via Code session. Documented inline in `sessions/2026-05-04-2103_code_preview-html-cut-trim.md` Section "Deviation from the prompt." Surfaced here at the reconciliation pass for visibility — the deviation is small but worth a row, both because the ship already happened and because the snap-only follow-up is queued behind a larger conversation.
- **Reopen?** closed in current form. If the orientation-reset (Decision #6) lands on framing B (panels-as-polygons), the cut step disappears entirely and this row becomes historical record.

### #6 — Orientation/awareness model: panels-first (B) + authored-vs-derived (D)

- **Date:** 2026-05-05
- **Decision:** Pivot to **panels-first authoring** (framing B) under the principle that **authoring is authoritative and the parser doesn't try to outsmart it** (framing D). Frameworks A (sharper layer/id ontology) and C (panel-as-unit-of-orientation) drop in as fallout: A becomes the cleanup pass on layer/id ontology that panels-first enables; C becomes a runtime concern handled when assembly transforms land in M4. The course change Alan flagged at the close of the 22:00 session is this conversation; the four framings + five questions did survive the pivot, intact, with my recommendation argued and accepted.

  **Concrete shape of the decision:**

  1. **New `panels` layer.** Each panel is a closed polygon with an id (e.g. `panel-stem`, `panel-tab-c`, `panel-bottom`). Panels are the unit of internal subdivision; they replace the cut-line-first algorithm's job of deriving regions from silhouette + fold lines.
  2. **Folds become explicit shared-edge declarations between named panels** rather than cut lines that need geometric region-resolution. The exact authoring shape (id-on-the-fold-path naming the two panels it joins, vs. sidecar JSON edge list, vs. some hybrid) is the first sub-decision that lands when 069 is authored — the test piece teaches us which is least-painful at the Affinity authoring surface.
  3. **`axles` splits.** Today's `axles` layer collapses two genuinely different concepts: rotation axles (this piece pivots around this point — 1 per piece, defines motion of *this* piece) and attachment points (other pieces connect through this point — N per piece, doesn't define this piece's motion). Going forward: `axles` is rotation-only, with `id="north"` for orientation. New `attach-points` layer holds pinholes (`pin-...`), mechanical pivots (`pivot-...`), and **landings** (`landing-...`, relocated out of `marks`).
  4. **`marks` becomes "construction + registration only."** Landings move out into `attach-points`. Marks-h / mark-i and similar construction marks stay in `marks`; they're not connection points.
  5. **Closure constraint becomes an edge attribute** in the panel graph (sidecar carries the closure flag per-edge). No special SVG construct — the SVG declares panels + bindings; closure is a downstream graph-topology property.
  6. **113–116 shared shape:** conceptually one shape with four assembly-time instance-ids; bare `hole-f` / `hole-g` (no piece suffix) is correct under that framing. Deduplication at the file-system level is later optimization; for now, byte-identical clones stay, and the audit understands the equivalence.
  7. **Cut-line-first stays as legacy.** Existing pieces (001/002/058/065/066/067/070/071/072/113) stay on cut-trim until they're touched anyway — no bulk re-authoring pass. The `buildFaceGraph` / `extendFoldsToSilhouette` / cut-trim implementation in `preview.html` continues to handle pre-pivot pieces; the panels-first parser is a new pathway alongside.
  8. **Snap-only extension to cut-trim is killed.** Not investing more in cut-line-first.

  **First test:** Alan authors piece 069 with the panels-first convention. 069 is mostly clean today (14 regions, 11/11 markers under cut-trim), small enough for a fast experiment, anchor-related so high-value. The brief lives at `claude-work/to-alan/069-panels-first/`. If authoring is painful, we invest in an authoring helper before pivoting more pieces (preview.html could grow a "propose panels from cut-trim, let Alan accept/edit" tool — cut-line-first becomes a drafting algorithm, not a parsing algorithm). If not painful, we roll forward.

- **Why this and not snap-only-extension on cut-line-first:** the cut-trim ship is the best the cut-line-first algorithm is going to be (066: 19 → 13 orphans, 17/17 markers resolve, no broken-graph banners). The residual failure mode — extension over-reach across long strips — is the third epicycle on an algorithm that's reverse-engineering what the SVG already implicitly knows. The 7-piece inventory (`sessions/2026-05-04-2200_cowork_orientation-reset-research.md` §"Key observations") shows the same underlying confusion in five different forms (002's mixed landing format, 067's no-folds, 069's mark-h/mark-i unclassified, 070's `id="tab"` no-letter, 113's reversed layer names + bare hole ids). It's not just a 066 failure mode; it's that the parser is bin-packing more concepts than it has bins for. Panels-first inverts: author draws closed polygons per panel; folds become explicit shared-edge declarations; the cut step disappears; 067's flat body is one panel; 066's strip is N panels with explicit hinge bindings. Honest trade-off: more authoring work per piece. Mitigation: most of a panel's boundary is already drawn (silhouette segments + fold paths the author already placed); we test on 069 before scaling; if painful, we build an authoring helper.

- **Type:** Claude-led, with charter-defined input from Alan on whether the authoring shape is workable in Affinity (the explicit pushback channel reserved during the conversation). Alan locked the direction in chat; this row records it. Co-authored convention work follows in `LAYER-CONVENTIONS.md` per Decision #3.

- **Downstream effects of this decision:**
  - DECISIONS #4 (preview.html ↔ work/viewer/ architecture): still deferred, but the parser surface preview.html exposes now needs to grow a panels-aware path, which informs the eventual architecture call.
  - DECISIONS #5 (cut-trim `fold.start`/`fold.end`): closes as historical record once the panels-first path is the dominant one. Cut-trim stays alive for legacy pieces.
  - LAYER-CONVENTIONS.md: gains `panels` layer, `attach-points` layer; `axles` narrows to rotation-only; `marks` narrows to construction/registration; cut-line-first sections retained as legacy reference.
  - STATUS.md "Orientation / awareness model" track: closes from `active (open question)` to `active (executing)`. SVG layer authoring + preview.html iteration tracks unblock with concrete next moves.
  - QUEUE.md: orientation-reset entry replaced with the 069 panels-first authoring ask.

- **Reopen?** closed in current form. Will only reopen if 069 authoring proves panels-first impractical at the Affinity surface — in which case the conversation shifts to "build authoring helper first" rather than "abandon panels-first."

### #7 — Panels-first conventions ratified across the anchor-pendulum batch

- **Date:** 2026-05-05 (evening)
- **Decision:** The complete set of panels-first authoring conventions is locked across an end-to-end batch of 9 panels-first-authored pieces (065/066/067/068/069/070/071/072 + 099) plus 100 (flat, no panels). The connection-graph audit (`claude-work/scripts/build_assembly_graph.py`) resolves all 24 cross-piece edges cleanly. The conventions, in summary form (full reference in `LAYER-CONVENTIONS.md`):

  1. **Bare-alias panel ids** — no `panel-` prefix. Direct `getElementById(<id>)`.
  2. **`fold-<a>-<b>`** binds a fold to two panel ids by their bare aliases; symmetric, optional `-<deg>` suffix for default angle.
  3. **`fold-<descriptive>`** for single-panel or curved folds (e.g. `fold-insidetabs` on 099).
  4. **Curved fold elements** — `<circle>` or `<ellipse>` inside fold layers.
  5. **Composite letter panels** — concatenated multi-letter ids (e.g. `bh`, `ai` on 069) when print labels share a panel; resolved by fuzzy substring match with shortest-match tiebreaker.
  6. **`attach-points` = structural cross-piece refs** (pivots, attaches, holes, typed landings, letter targets like bare `j` on 068).
  7. **`marks` = same-piece-or-decorative** (printed letters, multi-instance markers, alignments, cuts, untyped/closure landings; typed landings can also live here — parser reads both).
  8. **`attach-<letter><piece>`** = direct face/edge attachment to partner's body letter (distinct from tab-landing).
  9. **`landing-<panel-id>`** (no piece suffix) = same-piece closure landing.
  10. **`align-<letter><partner-piece>`** registration markers (paired symmetric form on both pieces).
  11. **`cut-<descriptive>`** prefix form (cut-lower, cut-upper, cut-a72) — distinguishes accommodation cuts from passage cuts.
  12. **Bare `hole`** = same-piece generic hardware-pin hole; `hole-<letter><piece>` typed cross-piece.
  13. **`back-<form>` prefix** = back-side annotation; parser dispatches on leading token.
  14. **`landing-back-X`** vs `back-landing-X` — disambiguated by leading token (back- first → side; landing- first → standard form for tab "back-X").
  15. **Multi-instance markers** in `marks` — duplicates allowed, define a SET of points sharing one logical id; N≥2 instances define an oriented frame.
  16. **Affinity collision-suffix tolerance** — parser treats `<id><digits>` (no separator) as same logical id as base.
  17. **Parser tolerance** for `cutaway` / `cutout-` slipping into `panels` layer (ignore; author's goal is delete on sight).
  18. **Panels mandatory** on every piece, even flat single-region (`<panel id="main">`).
  19. **Derived pivots** — only pieces with their own axle/pin need `pivot-<name>`; rigidly attached neighbors inherit rotation through their connection edges.
  20. **Dual-presence pattern** — typed landing region as both panel (folding/material) and mark (connection-graph centroid), when the landing is a discrete folding region.
  21. **Fuzzy substring matching** for cross-piece feature lookup, with prefix-stripping (so `attach-` doesn't leak into the match) and shortest-match tiebreaker (so `ai` beats `main` for letter `i`).

- **Why:** these conventions emerged through end-to-end authoring of the anchor-pendulum batch — each piece stress-tested the conventions and surfaced refinements (the back- side annotation came from 068, the multi-instance markers came from 099's 12-dot pattern, the dual-presence pattern came from 066's `b65/c65/...` panels paired with `landing-b65/...` marks, the bare letter target came from 068's `j` paired with 066's `landing-j68`). The connection-graph audit script ratified everything by resolving 24/24 cross-piece edges across the batch — the conventions form a coherent, self-consistent specification.

- **Type:** Co-authored. Conventions surfaced through Alan's authoring + Claude's parser-side reasoning; locked in chat per CHARTER §3 + Decision #3 routine. `LAYER-CONVENTIONS.md` updated in the same pass.

- **Downstream effects:**
  - `LAYERS.md` (the v0 cheat sheet from earlier 2026-05-05) deleted; `LAYER-CONVENTIONS.md` is now the single canonical reference.
  - `claude-work/scripts/build_assembly_graph.py` is the formal parser of these conventions; produces `claude-work/state/connection-graph.{md,json}` as the output state.
  - `CODE_PROMPT_preview-html-panels-aware.md` queued for the Code session that adds the panels-first parser pathway to `preview.html` (single-piece scope; multi-piece scene assembly follows).
  - DECISIONS #4 (preview.html ↔ work/viewer/ architecture): still deferred, but the panels-aware parser path informs the eventual answer.
  - DECISIONS #6: ratified in practice — all the framing-B + framing-D principles held up across 9 authored pieces.

- **Reopen?** closed in current form. New conventions land as they're discovered (per the LAYER-CONVENTIONS co-authoring routine in Decision #3). Sweeping reversals would require a fresh decision row and a real reason — the conventions are now stress-tested across 9 pieces with a 100% cross-piece edge resolution rate.

---

*Last updated: 2026-05-05 (late evening) — Decision #7 closed: comprehensive panels-first conventions ratified across the anchor-pendulum batch (065/066/067/068/069/070/071/072 + 099 + 100). 21 specific convention elements locked. LAYER-CONVENTIONS.md rewritten as the single canonical reference; LAYERS.md deleted. CODE_PROMPT_preview-html-panels-aware.md queued for the next Code session. Connection-graph audit at 24/24 edges valid is the empirical proof.*

*Earlier 2026-05-05 — Decision #6 closed: panels-first (B) + authored-vs-derived (D). The course-change conversation surfaced at the end of the 22:00 research session landed in this same evening; Alan locked the direction with explicit "lock it in" after the recommendation + defense. Concrete shape captured in the row body; LAYER-CONVENTIONS.md update + 069 authoring ask + STATUS.md track updates ride on the same cowork commit.*

*Earlier 2026-05-05 (~00:30) — reconciliation pass. Added #5 (cut-trim implementation deviation) and #6 (orientation/awareness model open). Updated #4 with the 2026-05-05 status note: diagnostic + cut-trim ships happened, but #6 now sits between #4 and any new code.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Decisions #1 and #2 capture the charter and the STATUS/WORKPLAN succession; #3 sets the co-maintenance routine for LAYER-CONVENTIONS.md; #4 is the next architecture decision, deferred deliberately.*
