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

### 2. Capture the 6 pending pieces

- **Pieces:** 013, 014, 016, 017 (plate B brackets), 090 (plate F reduction-gear pulley/disc), 110 (plate A face-frame end rail).
- **Workflow:** flat-bed scanner → chunk(s) into `source/scans-chunks/` → editor crop → per-piece PNG into `source/pieces/NNN.png`. Per `source/SCAN-INTAKE-CHECKLIST.md`.
- **Why next:** clears the source-side onboarding entirely (123/123 captured). Independent of the orientation-reset thread — Alan's hands, no Claude conversation needed.
- **Splittable:** yes — plate B's four brackets are a single chunk; 090 + 110 are separate plates. Two sittings is fine; one is fine too.

### 3. Tag 123 pieces in tag-pieces.html

- **Workflow:** open `tag-pieces.html` locally (file://), tag each piece by archetype (10 keys + uncertain + skip). Estimate ~1 hour total, splittable across sittings (localStorage persists).
- **Why next:** unblocks the post-tagging cowork pass (merge `character` + `subtype` columns into `pieces.csv`, author `expected_layers.yaml` v1 keyed by archetype, then the dashboard + audit-v2 CODE_PROMPT). See STATUS asset-state track.
- **Pre-req:** the v2-schema CODE_PROMPT (`CODE_PROMPT_tag-pieces-v2-schema.md`) ships to a Code session first if you want the v2 schema active before tagging. Otherwise the v1 tagger works and a re-tag pass against the v2 schema can happen post-ship; pick what feels right.

### 4. Verify Affinity lock-file cleanup (Alan-side, ~30s)

- **What:** the 22:00 orientation-reset session flagged 5 tracked Windows Affinity lock files at `work/pieces/{001,002,058,066,113}/NNN.af~lock~` and prepared a `git rm --cached` block. The 2026-05-05 reconciliation pass didn't find them in `git ls-files` — they may have been swept already, or the listing may have been from a worktree state.
- **How to pull:** `git ls-files | grep -F "af~lock~"` from repo root. If empty, this entry is satisfied; strike it. If non-empty, run the `git rm --cached` block from the 22:00 session-note Addendum.
- **Why low-cost:** new lock files are now caught by the `.gitignore` pattern that landed with the 22:00 note. This is just sweeping the index if anything's stuck.

---

## Soon (Claude-side conversation pending)

### 5. Pick the first piece end-to-end

- **What:** pick one piece, drive it through SVG authoring → sidecar → preview.html render → placement in a (proto-)multi-piece scene. Charter §6 commitment #2.
- **Candidate, updated post-DECISIONS #6:** if panels-first authoring on 069 (Now #1) goes well, 069 itself is a strong "first end-to-end" candidate — the inventory already named it as the panels-as-polygons test piece, and folding it through to preview.html would double as the panels-aware parser proof. Pendulum bob (piece 094, plate H) per the inherited Pendulum POC track stays as the alternate.
- **Not in the queue yet** because the candidacy isn't locked. Earmarked here so it doesn't fall off.

### 6. Ship panels-aware parser pathway in preview.html

- **What:** new code path in `preview.html` that parses the `panels` layer, reads `fold-<a>-<b>` ids to build the panel adjacency graph, and resolves landings + pivots from the `attach-points` layer. Cut-line-first (`buildFaceGraph` + `extendFoldsToSilhouette` + cut-trim) stays alongside as the legacy parser for pre-pivot pieces.
- **Why not in "Now":** depends on Now #1 landing first. The fold-binding shape (`fold-<a>-<b>` id form vs. JSON sidecar edge list vs. hybrid) might tweak based on what 069 authoring teaches.
- **How to pull:** Code session via a CODE_PROMPT once the 069 authoring lands. No prompt drafted yet.

---

## Recently shipped

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

*Last updated: 2026-05-05 (~01:15) — orientation/awareness reset conversation landed. Old #1 (the reset conversation itself) struck through to Recently shipped; new #1 is "author piece 069 panels-first" with full brief at `claude-work/to-alan/069-panels-first/README.md`. Soon section gained #6 (panels-aware parser pathway in preview.html, blocked on Now #1).*

*Earlier 2026-05-05 (~00:30) — reconciliation pass. The original QUEUE #2 (face-graph diagnostics) shipped at 11:45 the same day the kickoff drafted the queue, so it was stale on arrival; cut-trim shipped at 21:00. Both struck through and moved to "Recently shipped." New #1 is the orientation/awareness reset conversation — the live thread post-22:00 research note. Old #1 (capture 6 pending pieces) and old #3 (tag 123 pieces) carried forward. Added #4 for the Affinity lock-file cleanup verification.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Three "Now" entries seeded from the inherited WORKPLAN tracks; one "Soon" entry earmarked for the next cowork conversation.*
