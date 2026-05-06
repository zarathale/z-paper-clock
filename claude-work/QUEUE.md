# QUEUE.md — what Alan should author next

_Pull-based per CHARTER §3 + §9. Alan checks this when there's bench time. Claude maintains the ordering; Alan can reorder or push back. Kept modest in size on purpose — fewer asks, more thinking per ask. When a queue entry ships, it gets struck through here and migrates to the relevant STATUS track's recent log._

---

## Now

### 1. Multi-piece scene assembly — Code session

- **What:** open a Code session against `CODE_PROMPT_preview-html-multi-piece-scene.md` (repo root, ready-for-code). Walks `claude-work/state/connection-graph.json` and places panels-first pieces relative to each other in 3D using cross-piece attach/landing/pivot edges. `parsed.panelsFirst.attachPoints` is already populated in `preview.html` — just inert. This prompt wires it up.
- **Why first:** this is the first moment the clock looks like a clock. Closes CHARTER §6 commitment #2 (first piece end-to-end, now extended to the anchor cluster). The data is ready; the Code session is the only remaining step.
- **Verification target:** anchor cluster (065/066/067/068/069) assembled in one scene, with the pendulum rod (070/071/072) nearby.
- **How to pull:** open a Code session, hand it `CODE_PROMPT_preview-html-multi-piece-scene.md`.

### 2. Bob batch continuation (bench)

- **Pieces with open work:** 093a/093b (add fold paths in `folds-valley`/`folds-mountain`; rename `cutaway1` → `cutaway-1`; retire combined `work/pieces/093/093.svg` to `_attic/`), 070 (rename stale fold ids: `fold-panelsideb-tabb` → `fold-sideb-tabb`, `fold-panelsidec-tabc` → `fold-sidec-tabc`), 087 escape wheel (first gear-disc piece — should surface any gear-specific convention needs).
- **Decision to make before scaling:** 097 Affinity collision-suffix — 5 visually-distinct `attach-a99` copies auto-suffixed by Affinity to `attach-a991`/`992`/`993`/`994`. Options: (a) convention #16 parser tolerance (strip digit suffix when base id already resolves); (b) author per-instance ids. Either is fine; pick what feels right when you're at the bench.
- **How to pull:** bench session. Run `python claude-work/scripts/build_assembly_graph.py` after each export.

### 3. Tag 123 pieces in tag-pieces.html

- **Workflow:** open `tag-pieces.html` locally (`file://`), tag each piece by archetype. ~1 hour, splittable (localStorage persists).
- **Why:** unblocks audit-v2 + dashboard CODE_PROMPTs. See STATUS asset-state track.
- **Pre-req:** `CODE_PROMPT_tag-pieces-v2-schema.md` (ready-for-code at repo root) ships to a Code session first if you want the v2 schema active. Otherwise the v1 tagger works; re-tag pass after v2 ships.

---

## Soon (Claude-side work or decision pending)

### 4. `attach-x<piece-id>` convention formalization (Cowork)

- Surfaced in the 093 session: glue-only inter-piece attach (no printed tab letter), `attach-x<piece-id>` in `attach-points`. Not yet in LAYER-CONVENTIONS.md. Small conventions pass + DECISIONS entry before more pieces follow the pattern. Cowork-only; no Code needed.

### 5. Architecture call: preview.html ↔ work/viewer/ (DECISIONS #4, Cowork)

- Still deferred (open since charter sign-off). Multi-piece scene assembly landing will clarify what preview.html is becoming. After Now #1 ships, this conversation has enough data to close.

---

## Recently shipped

- ~~**Panels-aware parser + fold-step/closure-attach in preview.html**~~ → PRs #15 + #16, 2026-05-05. Panels-first dispatch, hinge forest, `attachPoints`/`closureAttaches` populated (inert — Now #1 wires them). See `sessions/2026-05-05-2345_code_preview-html-panels-aware.md` + `sessions/2026-05-05-1820_code_preview-html-fold-step-and-closure-attach.md`.
- ~~**Anchor-pendulum + bob batch authoring (15 pieces)**~~ → 2026-05-05 afternoon-evening. 065/066/067/068/069/070/071/072/099 + 094/095/096/097/098/100 panels-first. LAYER-CONVENTIONS.md rewritten; DECISIONS #7 (21 convention elements); connection-graph `build_assembly_graph.py` → 24/24 edges valid. See `sessions/2026-05-05-2330_cowork_panels-first-batch-and-graph.md`.
- ~~**Source capture closed at 123/123**~~ → 2026-05-05.
- ~~**Orientation/awareness reset (DECISIONS #6)**~~ → 2026-05-05 ~01:15. Panels-first locked in.
- ~~**Face-graph diagnostics (PR #13) + cut-trim (PR #14)**~~ → 2026-05-04. Legacy-path; still present.

---

## Conventions for this file

- **Format:** numbered entries with a 1-paragraph "what / why next / how to pull."
- **Order:** most-actionable first. Items that need Claude conversation before they can be pulled go in "Soon," not "Now."
- **Modesty:** keep "Now" to 3–5 entries. Pulling everything onto the queue at once defeats the iteration discipline (CHARTER §9).
- **Throughput floor:** none. Pull-based — when bench time happens, it happens.
- **Strikethrough on ship:** when something ships, strike the entry through and add a one-liner pointing at the session note. Periodically clean ship'd entries when they go stale enough to clutter.
- **Recently shipped:** keep a short tail of recent ships at the bottom for context. Trim aggressively once they're more than ~3 sessions old.

---

*Last updated: 2026-05-06 (morning) — doc-cleanup pass. Now #1 and #2 (069 authoring experiment + anchor-pendulum batch) struck through to Recently shipped; Soon #6 (panels-aware parser) struck through to Recently shipped. New Now #1 is multi-piece scene assembly Code session (CODE_PROMPT ready-for-code); new Now #2 is bob batch continuation; Soon 4-5 added. Footer trimmed.*

*Earlier 2026-05-05 (~00:30) — reconciliation pass. The original QUEUE #2 (face-graph diagnostics) shipped at 11:45 the same day the kickoff drafted the queue, so it was stale on arrival; cut-trim shipped at 21:00. Both struck through and moved to "Recently shipped." New #1 is the orientation/awareness reset conversation — the live thread post-22:00 research note. Old #1 (capture 6 pending pieces) and old #3 (tag 123 pieces) carried forward. Added #4 for the Affinity lock-file cleanup verification.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Three "Now" entries seeded from the inherited WORKPLAN tracks; one "Soon" entry earmarked for the next cowork conversation.*
