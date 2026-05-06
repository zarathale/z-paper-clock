# QUEUE.md — what Alan should author next

_Pull-based per CHARTER §3 + §9. Alan checks this when there's bench time. Claude maintains the ordering; Alan can reorder or push back. Kept modest in size on purpose — fewer asks, more thinking per ask. When a queue entry ships, it gets struck through here and migrates to the relevant STATUS track's recent log._

---

## Now

### 1. Per-fold assembled-pose load + save — Code session

- **What:** open a Code session against `CODE_PROMPT_preview-html-assembled-pose.md` (repo root, ready-for-code). Adds two things to `preview.html`: (a) read `assembled.folds` from the per-piece sidecar at piece-load time and use those values as the per-fold slider's initial value, applying the rotations immediately so the piece appears in its assembled pose; (b) a "Save assembled pose" button that emits the current slider state as a JSON snippet (copy + download) for Alan to merge into the sidecar by hand. Schema settled in DECISIONS #11.
- **Why first:** the missing durable-record-of-fold-state piece. Today every preview reload starts at zero; assembled-pose makes the validation work stick. Pairs naturally with the multi-piece scene mode just shipped — once individual piece poses are recorded, the scene starts looking like the actual assembled clock instead of a row of flat slabs.
- **Verification target:** load `?piece=069` with no sidecar (regression: all sliders at 0); load with a test sidecar carrying two assembled folds (those sliders pre-populate, geometry pre-folds); Save button emits JSON containing all 10 folds at their current values.
- **How to pull:** open a Code session, hand it `CODE_PROMPT_preview-html-assembled-pose.md`.

### 2. Inferred cross-piece connections in the audit — Code session

- **What:** open a Code session against `CODE_PROMPT_build-assembly-graph-inferred.md` (repo root, ready-for-code). Extends `claude-work/scripts/build_assembly_graph.py` to read `connections.inferred[]` from per-piece sidecars and merge with SVG-derived edges. Every edge gains a `provenance` field (`"authored"` / `"inferred"`); inferred edges carry their `source` + optional `note`. Conflict detection runs as soft warnings. Schema settled in DECISIONS #10.
- **Why now:** with assembled-fold pose authoring landing alongside, the sidecar is becoming a real surface for learned knowledge. Better to settle the inferred-connection merge while the audit script is the single thing reading these files. Doesn't conflict with #1 (different file, different repo area).
- **Verification target:** baseline regression (no sidecars → byte-identical output plus `provenance` field); sidecar with one inferred attach (surfaces in JSON + markdown); sidecar duplicating an authored edge (surfaces in `inferred_warnings`).
- **How to pull:** open a Code session, hand it `CODE_PROMPT_build-assembly-graph-inferred.md`.

### 3. Bob batch continuation (bench)

- **Pieces with open work:** 093a/093b (add fold paths in `folds-valley`/`folds-mountain`; rename `cutaway1` → `cutaway-1`; retire combined `work/pieces/093/093.svg` to `_attic/`), 070 (rename stale fold ids: `fold-panelsideb-tabb` → `fold-sideb-tabb`, `fold-panelsidec-tabc` → `fold-sidec-tabc`), 087 escape wheel (first gear-disc piece — should surface any gear-specific convention needs).
- **Decision to make before scaling:** 097 Affinity collision-suffix — 5 visually-distinct `attach-a99` copies auto-suffixed by Affinity to `attach-a991`/`992`/`993`/`994`. Options: (a) convention #16 parser tolerance (strip digit suffix when base id already resolves); (b) author per-instance ids. Either is fine; pick what feels right when you're at the bench.
- **How to pull:** bench session. Run `python claude-work/scripts/build_assembly_graph.py` after each export.

### 4. Tag 123 pieces in tag-pieces.html

- **Workflow:** open `tag-pieces.html` locally (`file://`), tag each piece by archetype. ~1 hour, splittable (localStorage persists).
- **Why:** unblocks audit-v2 + dashboard CODE_PROMPTs. See STATUS asset-state track.
- **Pre-req:** `CODE_PROMPT_tag-pieces-v2-schema.md` (ready-for-code at repo root) ships to a Code session first if you want the v2 schema active. Otherwise the v1 tagger works; re-tag pass after v2 ships.

---

## Soon (Claude-side work or decision pending)

### 5. `attach-x<piece-id>` convention formalization (Cowork)

- Surfaced in the 093 session: glue-only inter-piece attach (no printed tab letter), `attach-x<piece-id>` in `attach-points`. Not yet in LAYER-CONVENTIONS.md. Small conventions pass + DECISIONS entry before more pieces follow the pattern. Cowork-only; no Code needed.

### 6. Architecture call: preview.html ↔ work/viewer/ (DECISIONS #4, Cowork)

- Still deferred (open since charter sign-off). Multi-piece scene assembly shipped (PR #17); assembled-pose ship will likely tip the conversation. After Now #1 ships, this has enough data to close.

---

## Recently shipped

- ~~**Multi-piece scene assembly in preview.html**~~ → PR #17, 2026-05-06. `loadScene` + `renderSceneMulti` + pivot-cluster co-location. Anchor cluster (065/066/067/068/069) renders in one scene with 067+069 pivot-aligned on `pivot-anchor`. See `sessions/2026-05-06-0847_code_preview-html-multi-piece-scene.md`.
- ~~**Panels-aware parser + fold-step/closure-attach in preview.html**~~ → PRs #15 + #16, 2026-05-05. Panels-first dispatch, hinge forest, `attachPoints`/`closureAttaches` populated. See `sessions/2026-05-05-2345_code_preview-html-panels-aware.md` + `sessions/2026-05-05-1820_code_preview-html-fold-step-and-closure-attach.md`.
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

*Last updated: 2026-05-06 (evening) — multi-piece scene shipped (PR #17) + assembled-pose / inferred-connections design conversation closed. Multi-piece scene struck through to Recently shipped; new Now #1 is assembled-pose Code session (`CODE_PROMPT_preview-html-assembled-pose.md`); new Now #2 is inferred-connections audit Code session (`CODE_PROMPT_build-assembly-graph-inferred.md`). Bob batch + tag-pieces renumbered to #3/#4. Soon section renumbered #5/#6.*

*Earlier 2026-05-06 (morning) — doc-cleanup pass. Old Now #1 and #2 (069 authoring experiment + anchor-pendulum batch) struck through; Soon #6 (panels-aware parser) struck through. New Now #1 was multi-piece scene assembly Code session, shipped same morning.*

*Earlier 2026-05-05 (~00:30) — reconciliation pass. The original QUEUE #2 (face-graph diagnostics) shipped at 11:45 the same day the kickoff drafted the queue, so it was stale on arrival; cut-trim shipped at 21:00. Both struck through and moved to "Recently shipped." New #1 is the orientation/awareness reset conversation — the live thread post-22:00 research note. Old #1 (capture 6 pending pieces) and old #3 (tag 123 pieces) carried forward. Added #4 for the Affinity lock-file cleanup verification.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Three "Now" entries seeded from the inherited WORKPLAN tracks; one "Soon" entry earmarked for the next cowork conversation.*
