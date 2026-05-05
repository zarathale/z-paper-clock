# QUEUE.md — what Alan should author next

_Pull-based per CHARTER §3 + §9. Alan checks this when there's bench time. Claude maintains the ordering; Alan can reorder or push back. Kept modest in size on purpose — fewer asks, more thinking per ask. When a queue entry ships, it gets struck through here and migrates to the relevant STATUS track's recent log._

---

## Now

### 1. Author piece 069 panels-first — the convention test

- **What:** in Affinity, duplicate `069.af` → `069-panels.af`. Add a `panels` layer (closed polygon per region, ~14 panels, each id'd `panel-<descriptive>`). Bind each fold path to the two panels it joins via `id="fold-<panel-a>-<panel-b>"`. Move `landing-a` / `landing-b` out of `marks` into a new `attach-points` layer; while there, drop `anchor-pivot` into `attach-points` with `id="pivot-anchor"`. Export to `069-panels.svg` alongside the existing canonical files.
- **Why next:** this is the test piece for DECISIONS #6 (orientation/awareness model: panels-first + authored-vs-derived). Locked in this evening's cowork session; this is the first move that turns the decision into reality. Before scaling the convention to other pieces, I need to know whether panels-first authoring is workable at the Affinity surface. If it's painful, we build an authoring helper before pivoting more pieces; if it's small extra effort per panel, we roll forward.
- **Brief:** full detail in `claude-work/to-alan/069-panels-first/README.md`. Includes the feedback I want to hear (time, friction, naming, what you'd redesign) — that's the most valuable part of this experiment, not the SVG itself.
- **Effort estimate:** unknown. That's the experiment. My guess is "an evening's authoring time including the duplicate-and-relabel," but I want your real number.
- **How to pull:** Affinity session. When `069-panels.svg` is up, drop a one-liner in chat and I'll review + decide whether to ship the panels-aware preview.html pathway next.

### 2. Anchor + pendulum + circles authoring batch (panels-first, in-place uplift)

- **Pieces, ordered easier-to-harder:** 067 (anchor rear plate) → 068 (anchor fork) → 072 (pendulum blade) → 070 (pendulum rod) → 066 (pendulum-blade tube/casing — the acid test for panels-first vs. the co-linear-fold failure mode) → 099 (saw-toothed crescent) → 100 (bob-position disc with F/S arrows). 069 already done. 065 and the rest of the bob pieces (094/097/098/etc.) ride in the next batch.
- **Why this stack:** it's the structural heart of the ticking mechanism (anchor + pendulum rod), all anchor/rod pieces already have `work/pieces/NNN/` folders authored cut-line-first so you can uplift in place. 066 specifically tests whether panels-first cleanly resolves the failure mode (14 co-linear vertical folds) that broke cut-line-first. **099 + 100 added 2026-05-05** to surface the "circle authoring" question (saw-tooth boundary, disc with sector markings) before we tackle the gear discs in the next batch — gears inherit whatever convention answers these.
- **Workflow:** edit canonical `work/pieces/NNN/NNN.{af,svg}` directly. No `-panels` variant — convention shift from the 069 experiment landing.
- **Reference:** `LAYERS.md` at repo root for the cheat sheet (held at v0 pending the curve-case lock-in); `claude-work/to-alan/069-panels-first/README.md` for the worked example.
- **Format observations from the first review (2026-05-05 afternoon):** panel ids are bare aliases (no `panel-` prefix); folds reference them directly via `fold-<a>-<b>`; cut marks for accommodation cuts use `cut-<tab><piece>` in `marks`; closure landings use `landing-<tab>` (no piece suffix); shared `pivot-<name>` pairs pieces at that mechanical pivot. Patches needed on first-batch pieces: 070's two fold ids reference stale `panelsideb`/`panelsidec` (rename to `sideb`/`sidec`) and the rest of its strip folds need authoring; 071's `cutaway` element drifted into panels layer (relocate to silhouette). Parser will tolerate cutaway-in-panels going forward but Alan's goal is to delete on sight.
- **In progress as of 2026-05-05 afternoon:** 067/069/071/072 panels-first complete and exportable; 070 partial; 066 not yet uplifted; 099 + 100 authoring in flight; 068 deferred until format locks in (most complex of original five).

### 3. Tag 123 pieces in tag-pieces.html

- **Workflow:** open `tag-pieces.html` locally (file://), tag each piece by archetype (10 keys + uncertain + skip). Estimate ~1 hour total, splittable across sittings (localStorage persists).
- **Why next:** unblocks the post-tagging cowork pass (merge `character` + `subtype` columns into `pieces.csv`, author `expected_layers.yaml` v1 keyed by archetype, then the dashboard + audit-v2 CODE_PROMPT). See STATUS asset-state track.
- **Pre-req:** the v2-schema CODE_PROMPT (`CODE_PROMPT_tag-pieces-v2-schema.md`) ships to a Code session first if you want the v2 schema active before tagging. Otherwise the v1 tagger works and a re-tag pass against the v2 schema can happen post-ship; pick what feels right.

### ~~4. Verify Affinity lock-file cleanup (Alan-side, ~30s)~~

~~The 22:00 orientation-reset session flagged 5 tracked Windows Affinity lock files at `work/pieces/{001,002,058,066,113}/NNN.af~lock~`.~~ → **resolved 2026-05-05:** Alan ran `git ls-files | grep -F "af~lock~"` and it returned empty. Index is clean; the `.gitignore` pattern landed in the 22:00 note prevents recurrence. Migrating to Recently shipped on next sweep of this file.

---

## Soon (Claude-side conversation pending)

### 5. Pick the first piece end-to-end

- **What:** pick one piece, drive it through SVG authoring → sidecar → preview.html render → placement in a (proto-)multi-piece scene. Charter §6 commitment #2.
- **Candidate, updated post-DECISIONS #6:** if panels-first authoring on 069 (Now #1) goes well, 069 itself is a strong "first end-to-end" candidate — the inventory already named it as the panels-as-polygons test piece, and folding it through to preview.html would double as the panels-aware parser proof. Pendulum bob (piece 094, plate H) per the inherited Pendulum POC track stays as the alternate.
- **Not in the queue yet** because the candidacy isn't locked. Earmarked here so it doesn't fall off.

### 6. Ship panels-aware parser pathway in preview.html — `CODE_PROMPT_preview-html-panels-aware.md` ready

- **What:** new code path in `preview.html` that parses the `panels` layer, reads `fold-<a>-<b>` ids to build the panel adjacency graph, and resolves landings + pivots from the `attach-points` layer. Cut-line-first (`buildFaceGraph` + `extendFoldsToSilhouette` + cut-trim) stays alongside as the legacy parser for pre-pivot pieces. Single-piece scope; multi-piece scene assembly is a follow-up prompt.
- **Status:** **CODE_PROMPT drafted and ready-for-code** at `CODE_PROMPT_preview-html-panels-aware.md` (repo root). 8 numbered tasks; verification across 069/068/071/099. Conventions are stable (DECISIONS #7) and the connection-graph audit (`claude-work/scripts/build_assembly_graph.py`) provides a reference parser implementation in Python.
- **How to pull:** open a Code session, hand it `CODE_PROMPT_preview-html-panels-aware.md` and the LAYER-CONVENTIONS.md, follow the numbered tasks and verification checklist.

---

## Recently shipped

- ~~**Anchor-pendulum batch panels-first authoring (9 pieces)**~~ → landed 2026-05-05 (afternoon-evening). Alan authored 065/066/067/068/069/070/071/072 + 099 with the panels-first conventions across one extended bench session. End-to-end review surfaced 21 specific convention elements; LAYER-CONVENTIONS.md rewritten as the single canonical reference (LAYERS.md deleted). Connection-graph audit at `claude-work/scripts/build_assembly_graph.py` resolves 24/24 cross-piece edges across the batch. DECISIONS #7 ratifies the conventions.
- ~~**Cross-piece assembly connection graph**~~ → shipped 2026-05-05 (evening). `claude-work/scripts/build_assembly_graph.py` reads panels-first SVGs and emits `claude-work/state/connection-graph.{md,json}`. 10 panels-first pieces processed; 24/24 cross-piece edges valid; 1 pivot cluster (anchor); 10 untyped landings (closures + back-side + WIP, intentional). The structural backbone for the M4 assembly engine.
- ~~**Source-side capture closed at 123/123**~~ → 2026-05-05 afternoon. Pieces 090 and 110 both captured + initialized in `work/pieces/`; combined with the morning's 013-017 clone resolution, every piece in the master index now has a PNG in `source/pieces/`. Piece-capture track in STATUS flipped to `complete`.
- ~~**Plate B brackets 013/014/016/017 capture**~~ → resolved 2026-05-05 by clarification + replication: Alan flagged that 013-017 are all identical drawings to 012 (six bracket pieces, same artwork, different print positions). I replicated `source/pieces/012.png` → `013.png`/`014.png`/`015.png`/`016.png`/`017.png` (overwriting the redundant separate 015 scan). MD5-verified all six identical. `work/pieces.csv` rows updated to `captured` with clone notes.
- ~~**Cowork conversation: orientation/awareness reset**~~ → landed 2026-05-05 via cowork session `sessions/2026-05-05-0115_cowork_orientation-awareness-model.md`. Decision: panels-first (B) + authored-vs-derived (D). DECISIONS row #6 closed. See that row for the full shape.
- ~~**Ship the face-graph diagnostics CODE_PROMPT**~~ → shipped 2026-05-04 via PR #13 (`6ecdb45`). Diagnostic harness is permanent in preview.html. See `sessions/2026-05-04-1145_code_preview-html-face-graph-diagnostics.md`.
- ~~**Cut-trim algorithm refactor**~~ → shipped 2026-05-04 via PR #14 (`e0cb5cb`). 066 improved (19 → 13 orphans, all 17 markers resolve, no broken-graph banners). Snap-only-extension follow-up on standby — **killed 2026-05-05 by DECISIONS #6** (not investing more in cut-line-first). See `sessions/2026-05-04-2103_code_preview-html-cut-trim.md`.

---

## Conventions for this file

- **Format:** numbered entries with a 1-paragraph "what / why next / how to pull."
- **Order:** most-actionable first. Items that need Claude conversation before they can be pulled go in "Soon," not "Now."
- **Modesty:** keep "Now" to 3–5 entries. Pulling everything onto the queue at once defeats the iteration discipline (CHARTER §9).
- **Throughput floor:** none. Pull-based — when bench time happens, it happens.
- **Strikethrough on ship:** when something ships, strike the entry through and add a one-liner pointing at the session note. Periodically clean ship'd entries when they go stale enough to clutter.
- **Recently shipped:** keep a short tail of recent ships at the bottom for context. Trim aggressively once they're more than ~3 sessions old.

---

*Last updated: 2026-05-05 (late evening) — anchor-pendulum batch panels-first authoring landed (9 pieces); connection-graph audit script shipped (24/24 edges valid); LAYER-CONVENTIONS.md rewritten as canonical (LAYERS.md deleted); CODE_PROMPT_preview-html-panels-aware.md drafted ready-for-code. Soon #6 (panels-aware parser pathway) updated with the prompt status. Source-side capture closed at 123/123. DECISIONS #7 ratifies the convention lock-in.*

*Earlier 2026-05-05 (morning) — Alan flagged that plate B brackets 013-017 are all identical to 012; replicated 012.png x5 to fill those slots; pieces.csv + STATUS piece-capture track updated. #2 narrowed to piece 090 only (with parked question about 110 status). #4 lock-file verification closed (returned empty). Two new entries in Recently shipped.*

*Earlier 2026-05-05 (~01:15) — orientation/awareness reset conversation landed. Old #1 (the reset conversation itself) struck through to Recently shipped; new #1 is "author piece 069 panels-first" with full brief at `claude-work/to-alan/069-panels-first/README.md`. Soon section gained #6 (panels-aware parser pathway in preview.html, blocked on Now #1).*

*Earlier 2026-05-05 (~00:30) — reconciliation pass. The original QUEUE #2 (face-graph diagnostics) shipped at 11:45 the same day the kickoff drafted the queue, so it was stale on arrival; cut-trim shipped at 21:00. Both struck through and moved to "Recently shipped." New #1 is the orientation/awareness reset conversation — the live thread post-22:00 research note. Old #1 (capture 6 pending pieces) and old #3 (tag 123 pieces) carried forward. Added #4 for the Affinity lock-file cleanup verification.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Three "Now" entries seeded from the inherited WORKPLAN tracks; one "Soon" entry earmarked for the next cowork conversation.*
