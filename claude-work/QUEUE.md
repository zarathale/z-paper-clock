# QUEUE.md — what Alan should author next

_Pull-based per CHARTER §3 + §9. Alan checks this when there's bench time. Claude maintains the ordering; Alan can reorder or push back. Kept modest in size on purpose — fewer asks, more thinking per ask. When a queue entry ships, it gets struck through here and migrates to the relevant STATUS track's recent log._

---

## Now

### 1. Tag 123 pieces in tag-pieces.html

- **Workflow:** open `tag-pieces.html` locally (`file://`), tag each piece by archetype. ~1 hour, splittable (localStorage persists).
- **Why:** unblocks audit-v2 + dashboard CODE_PROMPTs (Soon #3). See STATUS asset-state track.
- **State:** v2 schema shipped 2026-05-03 (`_archive/code-prompts/CODE_PROMPT_tag-pieces-v2-schema.md`); embedded data snapshot refreshed 2026-05-06 to flip 013/014/016/017/090/110 from pending → captured/tagged (capture closed at 123/123). No Code-session pre-req.
- **Caveat:** if you opened `tag-pieces.html` before 2026-05-06, your localStorage has the stale snapshot pinned. Clear site data for the page (DevTools → Application → Storage → Clear site data) and reload to pick up the refreshed defaults — or just override per-piece via the UI as you go.

---

## Soon (Claude-side work or decision pending)

### 2. Architecture call: preview.html ↔ work/viewer/ (DECISIONS #4, Cowork)

- The strategically biggest open item, and STATUS Charter-rollout track explicitly calls it the next Cowork beat. Three substantive ships now sit on top of `preview.html` (PR #17 multi-piece scene, PR #18 inferred-connections audit-side, PR #19 assembled-pose) — enough data on the table to close. Three options on record: graduate `preview.html` into `work/viewer/`, run them in parallel as separate tools, or replace `work/viewer/` outright. Pull as a Cowork conversation; if we surface a need for more information mid-discussion, we'll log it and defer rather than pretend.

### 3. Audit-v2 + dashboard CODE_PROMPT (Cowork drafts; Code ships)

- Post-tag follow-on: once Now #1 lands, merge `character` + `subtype` from `INITIAL_STATE` (or the v2 YAML re-export) into `pieces.csv`; author `expected_layers.yaml` v1 keyed by character; draft `CODE_PROMPT_dashboard-and-audit-v2.md`. STATUS asset-state track has this queued; surfacing it explicitly so it doesn't fall through the cracks once tagging is done. Per CHARTER §5, audit script + dashboard land under `claude-work/` rather than evolving `work/scripts/audit_state.py` in place.

### 4. `attach-x<piece-id>` convention formalization (Cowork)

- Surfaced in the 093 session: glue-only inter-piece attach (no printed tab letter), `attach-x<piece-id>` in `attach-points`. Not yet in LAYER-CONVENTIONS.md. Small conversation + DECISIONS entry before more pieces follow the pattern. Alan flagged as open-to-reauthoring (not committed to defining a whole new standard) — the discussion may close it as "use existing convention X instead" rather than ratify a new form.

### 5. 093a / 093b fold paths (bench authoring; no Code prereq)

- Both halves landed under `work/pieces/093/` with `silhouette` + `panels` + `marks` + clean `cutaway` ids and cross-half `attach-x093a` on 093b, but neither has fold paths yet — the bob brace can't fold in `preview.html` until valley/mountain folds are authored. Pure bench work; surfaces during the next anchor/pendulum/bob touch-up pass. Not blocking the gear-train batch (087 is the next-action there per STATUS SVG-layer-authoring track).

### 6. Build-graph script: support split pieces (`work/pieces/093/093a.svg` etc.) (Cowork or Code)

- `claude-work/scripts/build_assembly_graph.py` main loop only globs `work/pieces/<dir>/<dir>.svg`, so 093a + 093b are silently absent from the connection graph today. Tiny extension: glob every `*.svg` in each piece dir, derive piece id from the filename stem rather than the dir name. Surfaced during the 2026-05-06 post-PR-19 review. Informational; not blocking — 093a/093b are the only split pieces today, and the SVGs themselves audit-clean (cutaway hyphenation fixed; combined 093.svg retired to `_attic/`).

---

## Recently shipped

- ~~**Per-fold assembled-pose load + save in `preview.html`**~~ → PR #19, 2026-05-06. `preview.html` reads `assembled.folds` from the per-piece sidecar at load time (precedence `assembled.folds[id]` > fold-id `-<deg>` suffix > 0) and applies the rotations immediately so the piece appears in its assembled pose. New "Save assembled pose" button emits the current per-fold slider state as a JSON snippet (copy-to-clipboard + download). Scene mode opted out for v1. All 9 verification checks green. See `sessions/2026-05-06-1900_code_preview-html-assembled-pose.md`.
- ~~**Bob batch continuation (070 / 093a / 093b refresh)**~~ → 2026-05-06 (late evening, bench). 070 renamed `panelsideb`/`panelsidec` panel ids → `sideb`/`sidec` (folds now resolve cleanly); 093a + 093b shipped under `work/pieces/093/` with `silhouette` + `panels` + `folds-valley` + `marks` + clean `cutaway` ids; combined `093.svg`/`.af` retired to `work/pieces/093/_attic/`; 093b carries cross-half `attach-x093a`. 087 .af authoring underway on the bench (no SVG export yet — pieces.csv stays at `captured`). 097 Affinity collision-suffix left as authoring choice (Alan: author uniquely if it ever truly matters; otherwise leave the `attach-a991`/`992`/`993`/`994` Affinity-disambiguated state in place); not promoted to a convention. Fresh `build_assembly_graph.py` run: 17 panels-first pieces, 24 valid authored cross-piece edges, 070 folds clean.
- ~~**Inferred cross-piece connections in the audit**~~ → PR #18, 2026-05-06. `claude-work/scripts/build_assembly_graph.py` reads `connections.inferred[]` from per-piece sidecars and merges with SVG-derived edges. Every edge tagged `provenance: "authored" | "inferred"`. Soft `inferred_warnings` on duplicates; legacy `pivot_clusters` shape preserved (preview.html scene-mode unaffected). New `prov` column + "Inferred connections" + "Inferred conflicts" sections in the markdown report. See `sessions/2026-05-06-1700_code_build-assembly-graph-inferred.md`.
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

*Last updated: 2026-05-06 (later evening, PM cleanup) — refreshed `tag-pieces.html` embedded data snapshot in-session (Cowork hand-edit; Alan opted out of a Code-session formal route on hobby-project grounds): the 6 stale `pending` rows for 013/014/016/017/090/110 are now `captured` in PIECES; INITIAL_STATE flips them to `tagged` (bracket clones inherit 012's `folded / bracket-tab`; 090 keeps the speculative-tag note; 110 keeps the pair-tag note). LocalStorage caveat called out in Now #1 — if Alan already opened tag-pieces.html under the v2 schema, he'll need to clear site data once to pick up the new defaults. Soon section reordered: architecture call (DECISIONS #4) promoted to #2 (was #3) on the basis that three substantive `preview.html` ships now push the question; new #3 audit-v2 + dashboard surfaced as the explicit post-tag follow-on (was buried in STATUS asset-state); attach-x demoted to #4 (was #2); new #5 093a/093b fold paths (was buried in STATUS SVG-layer-authoring open-questions); old #4 build-graph split-pieces extension demoted to #6.*

*Earlier 2026-05-06 (post-PR-19 review) — assembled-pose shipped via PR #19; bob batch continuation (070 rename, 093a/093b refresh, combined 093.svg retired, 087 .af underway, 097 collision left as authoring choice) verified at the bench. Both struck through to Recently shipped. Old Now #1 + #2 retired; tag-pieces.html promoted to Now #1. Soon section renumbered (attach-x convention #2, architecture call #3); a new #4 logs the build-graph script's `<dirname>.svg` lookup that silently skips split pieces (093a/093b) — small extension queued, not blocking.*

*Earlier 2026-05-06 (late evening) — inferred-connections audit shipped via PR #18. Old Now #2 struck through to Recently shipped; bob batch + tag-pieces renumbered to #2/#3; Soon section renumbered #4/#5. Now #1 (assembled-pose Code session) carried forward as the highest-ROI next pull.*

*Earlier 2026-05-06 (evening) — multi-piece scene shipped (PR #17) + assembled-pose / inferred-connections design conversation closed. Multi-piece scene struck through to Recently shipped; new Now #1 is assembled-pose Code session (`CODE_PROMPT_preview-html-assembled-pose.md`); new Now #2 is inferred-connections audit Code session (`CODE_PROMPT_build-assembly-graph-inferred.md`). Bob batch + tag-pieces renumbered to #3/#4. Soon section renumbered #5/#6.*

*Earlier 2026-05-06 (morning) — doc-cleanup pass. Old Now #1 and #2 (069 authoring experiment + anchor-pendulum batch) struck through; Soon #6 (panels-aware parser) struck through. New Now #1 was multi-piece scene assembly Code session, shipped same morning.*

*Earlier 2026-05-05 (~00:30) — reconciliation pass. The original QUEUE #2 (face-graph diagnostics) shipped at 11:45 the same day the kickoff drafted the queue, so it was stale on arrival; cut-trim shipped at 21:00. Both struck through and moved to "Recently shipped." New #1 is the orientation/awareness reset conversation — the live thread post-22:00 research note. Old #1 (capture 6 pending pieces) and old #3 (tag 123 pieces) carried forward. Added #4 for the Affinity lock-file cleanup verification.*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. Three "Now" entries seeded from the inherited WORKPLAN tracks; one "Soon" entry earmarked for the next cowork conversation.*
