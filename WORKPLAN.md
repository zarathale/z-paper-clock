# WORKPLAN.md — z-paper-clock

_The active stance. What tracks are open right now, what's the next action on each, what's blocked, what was learned recently. Updated regularly. See `PROJECT-STATE.md` for slow-moving framing; see `ROADMAP.md` for the long milestone arc; see `CLAUDE.md` for working conventions._

---

## How this document works

**What it is.** This is the working plan, not the milestone arc. Each section below is a **track** — a chunky unit of work, finer than a milestone and coarser than a task. Tracks have a hypothesis (what we're trying to learn or build), a current next action, blockers, and a short log of recent activity.

**What it isn't.** It's not a task list (those live in `CODE_PROMPT_*.md` for code-shaped work, and in track logs for everything else). It's not a milestone roadmap (that's `ROADMAP.md`). It's not a session journal (that's `sessions/`).

**Status values.** `active` (being touched right now or this week), `queued` (next-up but not started), `blocked` (can't start until something resolves), `paused` (deliberately on ice), `killed` (closed without shipping; kept as decision record).

**Front-matter format.** Each track opens with a small YAML block giving status, last-updated date, and a short next-action summary. The free-form sections below it (hypothesis, blockers, recent log) are markdown prose.

**Cadence.** Append a one-line entry to the relevant track's recent log at the end of each session that touched it. When ~3+ session notes have accumulated since the last review, run a dedicated **planning beat** Cowork session whose only deliverable is updates to this document — re-read the recent sessions, prune tracks, advance, re-prioritize, re-read ROADMAP.md to make sure the working plan still serves the long arc.

**Track lifecycle.** When a track is genuinely finished, flip status to `killed`, add a `closed:` line to the front-matter with date + reason, and leave the section in place as a decision record. Don't delete tracks; they're history.

---

## Track: Operations layer

```yaml
status: active
last_updated: 2026-05-03
next_action: Settle on per-piece JSON shape for asset-state; write a v0 audit script.
```

**Hypothesis.** The repo has a missing operations layer. Multiple planning surfaces (CLAUDE.md status table, ROADMAP.md milestones, sessions/ chronology, CODE_PROMPT front-matter) overlap and none answer "what tracks are open right now and what's the next action on each." Introducing PROJECT-STATE.md (framing) + WORKPLAN.md (stance) + an asset-state JSON + audit script (per-piece state, machine-generated from filesystem) closes that gap. ROADMAP.md stays as the long arc; CLAUDE.md status table eventually rationalizes once the new docs prove out.

**Open questions.**

- Whether GitHub Projects becomes the eventual home for issue-shaped tasks (parking lot — revisit after WORKPLAN.md has been used for a few sessions). Reasoning seeded in the design conversation: GitHub Projects fits issue-shaped work; WORKPLAN.md fits track-shaped work; they can co-exist if cleanly partitioned.
- Future browser-rendered dashboard: combine `workplan.json` (scraped from this doc's front-matter) + `state.json` (audit-script output) into a static HTML view, hostable on GitHub Pages. Deferred until the source-of-truth docs are settled.
- Whether the long-term ops layer stays repo-resident markdown forever or graduates to a cross-project tool that spans z-paper-clock plus other work. Today's answer: single-project, markdown-first.

**Recent log.**

- 2026-05-03 (afternoon): asset-state schema settled and `CODE_PROMPT_asset-state-audit.md` handed off (see Asset-state track). `LAYER-CONVENTIONS.md` shipped at repo root in parallel — distilled scannable reference for SVG authoring conventions, paired with the audit (audit checks each rule mechanically; the cheat sheet keeps the rules human-reachable while editing). One file landing: the convention-as-linter pattern that addresses the "uplift to new authoring standard" pain point. See `sessions/2026-05-03-1400_cowork_asset-state-schema-and-audit.md`.
- 2026-05-03 (morning): shipped PROJECT-STATE.md + WORKPLAN.md as v1; light cross-reference update to CLAUDE.md.
- 2026-05-03 (morning): settled the two-doc split (work-state vs. asset-state) and per-piece JSON shape for asset-state. GitHub Projects parked.
- 2026-05-02: design conversation began (multi-turn Cowork session). Identified the methodology question buried inside the user's PROJECT STATE draft.

---

## Track: Piece capture (chunk-and-crop)

```yaml
status: active
last_updated: 2026-05-03
next_action: Capture remaining 6 pieces (013, 014, 016, 017, 090, 110) on the home flat-bed scanner; crop to source/pieces/.
```

**Hypothesis.** The chunk-and-crop workflow (multi-piece flat-bed chunks → editor crop → per-piece PNG archive) is reliable and scales. Quality is better than gen-1 phone scans (no gutter warp). Effective DPI ~613 verified, above the 600 spec.

**Status detail.** 117 of 123 pieces captured. Six pending: 013, 014, 016, 017 (plate B brackets), 090 (plate F reduction-gear pulley/disc), 110 (plate A face-frame end rail). Captures land in `inbox/`, get promoted to `source/scans-chunks/`, and the per-piece PNGs land in `source/pieces/NNN.png`.

**Blockers.** None. Bench time and access to the scanner.

**Recent log.**

- 2026-05-01: third batch ingested (16 pieces, including editor crops of 34/35 and 94 from stitched composites). Cumulative 117/123. See `sessions/2026-05-01-0130_*`.
- 2026-05-01: second batch ingested (4 pieces + L/R-stitched composites for 34/35/94). See `sessions/2026-05-01-0030_*`.
- 2026-04-30: first batch ingested (97 pieces). See `sessions/2026-04-30-2359_*`.

---

## Track: SVG layer authoring

```yaml
status: active
last_updated: 2026-05-04
next_action: Finish authoring marker-bound fold ids on piece 066 (apply tab-X / landing-X<piece> to the remaining vertical fold paths so all 14 side-panel folds carry binding ids). Then queue CODE_PROMPT_marker-bound-fold-ids.md for the preview.html parser change.
```

**Hypothesis.** The actual current bottleneck of the project. PNG capture is mostly done; turning each PNG into a layered SVG with the project's authoring conventions (silhouette + cutouts + folds-valley + folds-mountain + axles + glue-zones + labels + marks) is what's standing between the source archive and any of the downstream work (preview.html, eventual viewer, regions, folding, grouping, mechanism animation).

**Status detail.** Only a small handful of pieces have started down this pipeline. The conventions themselves are still iterating as new piece-types reveal new authoring requirements (the cut-layer convention and axles-with-north convention both shipped this past week as examples). Each new piece can both apply the convention and stress-test it.

**Open questions.**

- Whether the convention work converges fast enough to enable bulk authoring, or whether each piece is going to keep surfacing new requirements for a while.
- Whether some pieces are simple enough to delegate to a Haiku-class model with a tight prompt, and which need Sonnet-or-better hand-attention. (See the Model Selection Guide in ROADMAP.md.)

**Blockers.** None outright, but the regions/face-graph design (separate track) is the upstream concept work that will make the folding-related layers (folds-valley, folds-mountain) interpretable, not just authored.

**Recent log.**

- 2026-05-04 (morning): **marker-bound fold ids convention settled — and revised within the same session.** Triggered by piece 066's fold-tagging failure — its 14 vertical tab/landing folds all sit at the same x-coordinates (x ≈ 2501 right / x ≈ 479 left), so the half-plane cut algorithm collapses them and only the first cut at each x produces region splits; downstream folds at the same x become no-ops, no fold edges, no driven hinges. Resolution is authoring-side, not parser-geometry: a fold path's id has the form `fold-<marker-id>` where `<marker-id>` matches the id of any marker in `<g id="marks">` (today: `tab-X` and `landing-X<piece>`). When it does, the parser strips the `fold-` prefix, looks up the rest in the marks centroid map, and binds the fold to the region containing that marker's centroid. Optional default-angle suffix: `id="fold-tab-c-40"`, `id="fold-landing-h65-90"`. **The `fold-` prefix was added mid-session** — initially the convention had fold path ids share their marker's id directly (`tab-c` in both layers), but Affinity Designer's export pipeline silently suffixed the marker side with `1` on cross-layer id collisions (`tab-c` in marks → `tab-c1` after export), breaking the binding for 15 of 17 marker pairs in piece 066. Prefixing the fold side guarantees every fold-path id is unique within the SVG, so Affinity has nothing to rename. Convention locked across CLAUDE.md (new Architectural-Decisions row + new "Per-element ids inside fold layers" entry in File Naming Conventions), LAYER-CONVENTIONS.md (extended folds section), and `work/SPEC-3D-VIEWER.md` (parser-consumption table row). Implementation also landed in this session: `preview.html`'s parser now builds `marksCentroidsById`, parses marker-bound ids, and uses point-in-polygon to override the adjacency-step passive check for marker-bound folds. Closure constraint (the whole-strip wrap-around so tab-aa lands on landing-aa) is a related but distinct convention still in design — three options on the table (author-most/derive-one, author-shape, closure-as-slider). See `sessions/2026-05-04-XXXX_cowork_marker-bound-fold-ids.md` (forthcoming at session-close).
- 2026-05-03 (afternoon): two convention corrections surfaced while reviewing piece 071's re-export. (1) The "everything else from the print" canonical layer is `marks`, not `marks-other` — the wrong name had been carried across the docs and is now fixed in `CLAUDE.md`, `LAYER-CONVENTIONS.md`, `work/SPEC-3D-VIEWER.md`, `work/pipeline/03-layer-split.py`, and the asset-state CODE_PROMPT. preview.html already used the correct name. (2) **Landing markers** are now formally part of the schema: inside `<g id="marks">`, an element with id `landing-<tab-letter><piece-number>` (e.g. `landing-c70`) marks a panel that receives a tab from another piece — the inverse of a glue tab. Cross-piece pairing (`tab-c` on 70 ⟷ `landing-c70` on 71) is the connection-graph primitive M4's assembly engine will read. New Architectural-Decisions row in `CLAUDE.md`; new section in `LAYER-CONVENTIONS.md`; two new checks queued in the asset-state CODE_PROMPT. Same session note.
- 2026-05-03 (afternoon): `LAYER-CONVENTIONS.md` shipped at repo root — distilled scannable cheat sheet for canonical layer names, the cut-layer / axles+north conventions, the faithful-trace direction, and the common authoring slips the audit catches. Designed to stay open on a second window while authoring in Affinity. See `sessions/2026-05-03-1400_cowork_asset-state-schema-and-audit.md`.
- 2026-05-02: cut-layer authoring convention settled and shipped through preview.html. See `sessions/2026-05-02-1500_cowork_preview-html-cut-layer-spec.md`.
- 2026-05-02: axles-with-`id="north"` orientation cue convention settled and shipped through preview.html. See `sessions/2026-05-02-2330_cowork_preview-html-axle-rotation.md`.
- 2026-05-02: faithful-trace + functional-sidecar direction settled (artifact stays human-drawn; mechanism geometry captured in optional `function` block).

---

## Track: preview.html iteration

```yaml
status: active
last_updated: 2026-05-04
next_action: Queue CODE_PROMPT_marker-bound-fold-ids.md once piece 066's authoring pass completes — parser change to honor `tab-X` / `landing-X<piece>` ids on fold paths (binds the fold to the region containing the matching marker's centroid). Then resume the closure-constraint design (three options open: author-most/derive-one, author-shape, closure-as-slider).
```

**Hypothesis.** A single-file HTML preview tool at repo root is the right substrate for testing SVG authoring conventions piece-by-piece, while the eventual `work/viewer/` Vite + TS + three.js application is still upstream. Each new convention or fix gets its own `CODE_PROMPT_preview-html-<topic>.md` and ships independently. The architecture decision (graduate into `work/viewer/`, stay separate, or replace `work/viewer/` outright) is intentionally deferred until v1b ships.

**Status detail.** Shipped: SVG parse + flat slab + thickness extrusion + axle rendering + cut-layer convention + texture-flip fix + back-face mirror + render-on-demand performance pass + thickness extrusion fix + axle rotation slider with silver wires and brass-gold north sphere. Queued: v1b (polygon cut + adjacency BFS + hinge hierarchy + per-fold sliders), cutouts subtraction (`<g id="cutouts">`), multi-cutaway slabs, `TODO(070)` rotated-`<use>` transforms, `TODO(uv-offsets)`. See ROADMAP.md M0.6 for the per-task table.

**Open questions.**

- Whether v1b's polygon-cut + hinge-hierarchy approach validates (it's a substantial chunk of code). If it does, the path forward into `work/viewer/` clarifies a lot.
- Whether the architecture decision (0.6.13) waits until after v1b, or whether stress-testing on a few real pieces resolves it sooner.

**Recent log.**

- 2026-05-04 (morning): debugged piece 066's fold-tagging failure end-to-end. Symptoms: 19 orphan regions, 188 unknown-tag edges, only 7 of 22 folds producing driven hinges (valley-15..19 + mountain-20..21 — the column-internal horizontals; valley-0..14 — the 14 vertical tab/landing folds — produce zero hinges). Root cause: co-linear authored folds at shared x-coordinates collapse under the half-plane cut. Settled the **marker-bound fold ids** authoring convention as the resolution (see SVG-layer-authoring track). Parser change deferred to its own CODE_PROMPT. Folded the path-fallback silhouette banner during the same pass — Alan added `<g id="silhouette">` around the existing `cutaway` and the marks-layer `tab-*` / `landing-*` ids, so the cleaner Tier 1 silhouette source is now in play (vertex/area unchanged from the path-fallback heuristic; banner gone).
- 2026-05-03 (session-start sweep): v1b end-to-end verification (069 + 066 in-browser) still pending — flagged in ROADMAP.md 0.6.9 task row.
- 2026-05-04 (just past midnight): **M0.6.14 shipped.** `CODE_PROMPT_preview-html-source-of-truth.md` flipped to `shipped`. `preview.html` now opens any piece by id (Enter, Load button, or `?piece=NNN` URL param) from `work/pieces/NNN/NNN.svg`, with `R` / Reload re-fetching from disk (cache-busted), an optional `NNN.json` `function` sidecar block, drag-drop fallback retained with a soft canonical-home nudge banner when a per-piece-shaped filename is dropped from outside the canonical tree, and a datalist auto-populated from `work/pieces.csv`. No parser or render-pipeline changes. Verified live against pieces 001/066/067/069/070/999 + URL-param + `R` keybind. See `sessions/2026-05-04-0030_code_preview-html-source-of-truth.md`.
- 2026-05-03 (evening): **`CODE_PROMPT_preview-html-source-of-truth.md` queued (status: ready-for-code).** Pairs with the same-day filesystem restructure. Adds a piece-id loader to `preview.html` so it always knows the canonical location for any piece's latest export — `work/pieces/NNN/NNN.svg`. Drag-drop retained as fallback for ad-hoc inspection. Optional reload + sidecar-surfacing nice-to-have. M0.6.14 in the roadmap. NOTE for the v1b prompt: its verification paths (`inbox/069.svg`, `inbox/066.svg`) get bumped to `work/pieces/069/069.svg` and `work/pieces/066/066.svg` as part of the filesystem restructure CODE_PROMPT.
- 2026-05-03: clean-start `CODE_PROMPT_preview-html-v1b.md` authored at repo root (status: ready-for-code). Grounded in current `preview.html` (real signatures: `currentSlabPivot`, `buildSlab(polygon, thicknessMm)`, `extractSilhouette` Tier-1/2/3, `parsed.{folds,axles,north,rootCentroid}`, render-on-demand `requestRender()`, etc.) and `work/SPEC-REGIONS.md` (terminology + two-step algorithm: extend folds to silhouette boundary, then iteratively split via `polygon-clipping` half-plane intersection). Eight tasks; verification + manual tests scoped to 069 + 066. Rotation pivot wraps the whole fold tree; polarity in UI is implicit (default angle only). See `sessions/2026-05-03-0300_cowork_v1b-clean-start.md`.
- 2026-05-03: original `CODE_PROMPT_preview-html-v1b.md` archived to `_archive/code-prompts/` (status flipped to `archived`, body preserved as design record). Re-tightening pass against v1a's session note alone was insufficient — the file's drift since v1a is too substantial; clean-start authored against the current `preview.html` is the next move. See `sessions/2026-05-03-0200_cowork_v1b-archive.md`.
- 2026-05-02 (late evening): thickness extrusion fix + axle rotation shipped. See `sessions/2026-05-02-2300_*` and `sessions/2026-05-02-2330_*`.
- 2026-05-02 (earlier): cut-layer convention + texture flip + back-face mirror + perf pass shipped.
- 2026-05-02: SPEC + ROADMAP doc-pass surfaced preview.html as M0.6. See `sessions/2026-05-02-2359_cowork_preview-html-spec-and-roadmap.md`.

---

## Track: Repo hygiene

```yaml
status: active
last_updated: 2026-05-03
next_action: Hand CODE_PROMPT_filesystem-restructure.md to a Code session — it executes the 2026-05-03 filesystem restructure: moves 14 .af files from source/pieces/ to work/pieces/NNN/NNN.af, moves 8 SVGs from inbox/ to work/pieces/NNN/NNN.svg, retires the 067-full.af variant, deletes inbox/, and repoints audit_state.py + the v1b verification paths.
```

**Hypothesis.** The repo is high-velocity right now and accumulates organizational debt — files moving from folder to folder, structures evolving, archives left behind, transient working zones (`inbox/`) feeling unsettled. CLAUDE.md's doc-sweep discipline is reactive (catch it at session-end). The asset-state audit script (separate track) makes some of this proactive: visible repo state at a glance, "this piece has been in inbox/ for 5 days" surfacing automatically. Doc-sweep stays for the cases the audit can't see.

**Open questions.**

- ~~Whether `inbox/` stays or gets renamed/folded into a clearer pre-`source/` staging area once asset-state surfaces what's actually in it at any moment.~~ **Resolved 2026-05-03 (evening): `inbox/` retired entirely.** Chunks land directly in `source/scans-chunks/`; SVG exports land directly in `work/pieces/NNN/NNN.svg`. See the 2026-05-03 evening recent-log entry below.
- Whether the periodic repo-audit (last one: `sessions/2026-04-30-2100_cowork_repo-audit.md`) becomes a regular cadence — perhaps at each planning beat — or stays event-triggered.

**Recent log.**

- 2026-05-03 (evening): **filesystem restructure pass.** Settled the `.af` + `.svg` colocation question that had been festering as drift for weeks. Each piece now has a single working folder at `work/pieces/NNN/` containing `NNN.af` (authoring), `NNN.svg` (latest export), `NNN.json` (sidecar). `source/pieces/` locked to PNG scans only. The `inbox/` folder retired in the same pass — chunks go straight to `source/scans-chunks/` from the scanner, exports go straight to `work/pieces/NNN/` from Affinity. Filename convention drops the `piece-` prefix going forward (the folder name provides the context). Affinity lock files + editor backups added to `.gitignore`. Doc updates: CLAUDE.md (new Architectural-Decisions row + Repo Structure tree + File Naming Conventions + Known Issues + Last-updated note), `source/SCAN-INTAKE-CHECKLIST.md`, `source/pieces/README.md`, `LAYER-CONVENTIONS.md`, `work/SPEC-3D-VIEWER.md` (file/folder layout + preview.html source-of-truth note), `ROADMAP.md` (M0.6.14 row), this file. Two CODE_PROMPTs handed off: `CODE_PROMPT_filesystem-restructure.md` (the actual moves) and `CODE_PROMPT_preview-html-source-of-truth.md` (preview.html piece-id loader, paired). See `sessions/2026-05-03-2345_cowork_filesystem-restructure.md`.
- 2026-05-03 (afternoon): `share/` folder no longer present at the repo root (cleaned up between sessions; the prior cowork turn observed it had 4 SVGs overlapping `inbox/`). `inbox/` still contains `069.af` (duplicate of `source/pieces/069.af`) plus 8 SVGs (001, 065, 066, 067, 069, 070, 071, 072) that the asset-state audit will flag once it ships. Audit-as-it-ships will surface what to do with each.
- 2026-05-03 (morning): track opened. Inbox/-feels-awkward observation captured during the operations-layer design conversation.
- 2026-04-30: repo audit caught downstream-doc drift after a high-velocity day of folder pivots.

---

## Track: Asset-state / audit tooling

```yaml
status: active
last_updated: 2026-05-03
next_action: tag-pieces.html v2 schema shipped. Alan refines subtypes + flips piece 041 in the tagger. Then Cowork: merge `character` + `subtype` into pieces.csv, author expected_layers.yaml v1 keyed by character, draft CODE_PROMPT_dashboard-and-audit-v2.md.
```

**Hypothesis.** Per-piece state ("where is each piece in its lifecycle") needs its own surface, separate from work-state (this document). A small Python audit script reads the filesystem (`source/pieces/`, `work/pieces/`, `inbox/`, `source/scans-chunks/`, etc.) and emits a per-piece JSON file (or a single fat `state.json`) reflecting which stages each piece has reached. Generated, never hand-maintained — eliminates the "I forgot to update the CSV" failure mode. Output becomes the basis for an eventual browser-rendered dashboard.

**Design decisions so far** (settled in the operations-layer design conversation, 2026-05-03):

- **Per-piece JSON**, not a single fat CSV. Mirrors the eventual sidecar structure; co-locates state with asset; scales better than wide-CSV.
- **Audit script reads filesystem, doesn't trust hand-maintained columns.** `pieces.csv`'s `status` column stays as a manual editorial signal; the audit script is the machine-truth.
- **Per-piece stage fields** (initial sketch — confirm during schema work): `in_inbox`, `source_png`, `source_chunk_present`, `svg_authored`, `svg_layer_coverage`, `sidecar_json`, `function_block`, `in_viewer_manifest`, `notes`.

**Open questions.**

- Single fat `state.json` for v0 (fast to ship, easy to skim) vs. per-piece file from the start (mirrors final shape)? Probably v0 single fat JSON, transition to per-piece later.
- Where the audit script lives: `work/scripts/audit_state.py` is the natural home (alongside `build_master_list.py`). Use the same `.venv`.
- Eventual integration with the piece-scan ingest skill at `.claude/skills/piece-scan-ingest/` (see ROADMAP.md M0.5.2). The two are obvious cousins; might collapse into one tool, or stay separate (skill = ingest-time check; audit = repo-state-anytime check).

**Blockers.** None. Just hasn't been started.

**Recent log.**

- 2026-05-03 (late evening): v1→v2 schema sharpen + pair-tag walkthrough + CODE_PROMPT draft + QA pass on the prompt. Closed 10 of 11 pair-tags (041 deferred); three character changes from the v2 draft (077, 080, 100, 120); three schema additions to the YAML header (controls: field, glue-agnostic clarification, sliding-axles clarification). Drafted `CODE_PROMPT_tag-pieces-v2-schema.md` at repo root (status: `ready-for-code`); QA pass surfaced two real bugs (silent data loss across non-tag mutators; YAML parser dead-end after a controls block) and one 8-vs-7 character-count inconsistency, all folded back into the prompt before final. See `sessions/2026-05-03-2300_cowork_v2-schema-and-tag-pieces-prompt.md`.
- 2026-05-03 (evening, later): organizing-principle pivot for `expected_layers.yaml`. Drafted the section-based v0 with ~50 per-piece overrides; surfaced ~3 calls that split 50/50 (motor-wheel folds, hands-without-folds, anchor-pendulum-with-axles). Alan flagged: when defaults split 50/50, they're noise — section axis is wrong. Pivoted to a **physical-character / construction-archetype axis**. Sketched 10 archetypes (flat-laminate, flat-decorative, folded-tube, folded-box, frame-channel, gear-disc, pinion-stack-disc, gear-teeth-strip, anchor-pendulum-mixed, reference). Decided data home: new `character` column on `work/pieces.csv`. Built `tag-pieces.html` at repo root (file://-friendly, embedded pieces.csv, keyboard-driven, localStorage-backed, YAML export) so Alan can tag 123 pieces cold. Section-based v0 of `expected_layers.yaml` stays in place pending post-tagging restructure. CODE_PROMPT teeing-up parked. See `sessions/2026-05-03-2000_cowork_archetype-pivot.md`.
- 2026-05-03 (evening): dashboard design conversation. Settled: filter-and-list layout (not kanban), `dashboard.html` parallel to `preview.html`, bucket menu **derived from state.json** (lifecycle stages + per-failing-check chips + anomalies — auto-grows when new conventions land), live inline SVG thumbnails, expected-layers hints in `work/expected_layers.yaml` with section defaults + per-piece add/remove overrides, diff computed in `audit_state.py` (new fields `expected_layers` + `missing_layers`, plus a new convention check `expected-layers-present`), YAML format. Deferred: section default values (next session), element-id-level expectations (v1), bucket placement (build time). Flagged for CODE_PROMPT: `repo_root` worktree-path normalization, schema_version bump to 2, `pyyaml` dep. See `sessions/2026-05-03-1800_cowork_dashboard-design.md`.
- 2026-05-03 (afternoon, late): `CODE_PROMPT_asset-state-audit.md` shipped via Code session. `work/state.json` now exists with rich per-piece data (file paths, layer inventories, convention check results, derived stage, anomalies). Audit prompt status flipped to `shipped`. See `sessions/2026-05-03-1600_code_asset-state-audit-v0.md`.
- 2026-05-03 (afternoon): schema settled and `CODE_PROMPT_asset-state-audit.md` authored at repo root (status: ready-for-code). Key design point Alan flagged — "as preview.html matures, conventions evolve and pieces need to be uplifted" — handled by per-convention linter-style checks (new convention = new check; existing pieces auto-flag at next audit run; no migration step). `LAYER-CONVENTIONS.md` cheat sheet shipped in parallel at repo root. Track flipped queued → active. See `sessions/2026-05-03-1400_cowork_asset-state-schema-and-audit.md`.
- 2026-05-03 (morning): track opened. Per-piece JSON shape settled in design conversation.

---

## Track: Regions / face-graph design (SPEC-REGIONS.md)

```yaml
status: active
last_updated: 2026-05-03
next_action: Review SPEC-REGIONS.md against pendulum arm piece ID (§II.C); confirm fold-line authoring convention is sufficient to produce the face graph. SPEC-REGIONS.md is referenced from the new v1b prompt (`CODE_PROMPT_preview-html-v1b.md`, status: ready-for-code) as the upstream concept doc — the v1b ship will be the empirical test of whether the SPEC's two-step algorithm holds up against real authored fold lines.
```

**Hypothesis.** Folding and grouping (separate track) are both operations on subdivisions of a piece. Neither can advance with confidence until "what counts as a region of piece N" is a deterministic, computed thing. Regions are not authored — they're derived from the layered SVG (silhouette + cutouts + fold lines forming a planar face graph: vertices at fold-line endpoints, edges along fold lines and boundary segments, faces as the closed polygons between them). Origami CAD calls this a "face graph" or similar. Building this concept once unblocks F1, F2, F3 (visual / semantic / experiential folding) and G1–G4 (grouping at increasing depth).

**Scope of the SPEC.**

- Definition of a region (what counts as one, what doesn't).
- Computation: how the face graph is derived from the layered SVG (algorithm sketch, not full code).
- Data shape: how regions are represented in the per-piece JSON sidecar.
- What regions enable downstream: per-region fold metadata, per-region glue-tab labels, mesh-split for hinge animation.
- What regions explicitly do NOT solve in v1: 3D collisions, paper thickness during fold, multi-fold sequencing.

**Open questions.**

- Whether a simple scanline-or-Shapely-based polygon decomposition is enough, or whether some manual hint authoring (e.g. labeling which side of a fold is the "moving" half) needs to be part of the per-piece SVG convention.
- Whether the SPEC stays standalone or eventually merges into SPEC-3D-VIEWER.md.

**Blockers.** None for the SPEC itself. (Implementation depends on having SVG-authored pieces with fold lines populated; the pendulum POC track surfaces those.)

**Recent log.**

- 2026-05-03: `work/SPEC-REGIONS.md` drafted and written. Decisions: live computation (not stored in sidecar), root-marker BFS for moving-side, polygon-clipping + Shapely named as libraries, pendulum self-fold flagged as open stress case. See `sessions/2026-05-03-0100_cowork_spec-regions.md`.
- 2026-05-03: track opened. Regions-as-upstream-of-folding-and-grouping insight emerged during design conversation about exploration tracks.

---

## Track: Pendulum folding & grouping POC

```yaml
status: queued
last_updated: 2026-05-03
next_action: Identify exact piece IDs for the pendulum bob + pendulum arm from embedded-labels.md §II.C; queue authoring + folding/grouping tests.
```

**Hypothesis.** A small, mechanically-real two-piece subsystem (pendulum bob + pendulum arm) is the right first proof for the folding and grouping primitives. The arm folds onto itself (tests F1 visual fold; tests the regions concept directly — when both ends are part of the same piece, which side is "the moving side"?). The arm glues to the bob (tests G1 trivial transform parenting baseline + G2 semantic grouping via embedded-labels glue references). Both pieces sit in §II.C, which is one of the function-block sections — so once the function block is populated they become the candidate test bed for eventual mechanism animation, too.

**Open questions.**

- Exact piece IDs to use. Piece 94 (pendulum-bob casing, plate H) is one candidate; the pendulum arm and other §II.C pieces should be confirmed against `source/transcriptions/embedded-labels.md` when starting the work.
- Whether the POC produces just renderable visual output (F1 + G1) or extends through F2 + G2 (semantic encoding of folds and glue).
- Whether the POC informs the SPEC-REGIONS.md draft, or whether SPEC-REGIONS.md gets drafted first and the POC validates it. Probably the latter: write the SPEC speculatively, test against the pendulum, refine the SPEC.

**Blockers.**

- SPEC-REGIONS.md (separate track) — concept work needs a stake in the ground first.
- SVG layer authoring on the pendulum pieces — they need to exist as authored SVGs before any folding/grouping can happen on them.

**Recent log.**

- 2026-05-03: track opened. Pendulum chosen as POC subject during design conversation. F1 + G1 + G2 + regions identified as the test surface.

---

*Last updated: 2026-05-04 (morning) — marker-bound fold ids convention settled (then revised mid-session for the `fold-` prefix to dodge Affinity's cross-layer id collision auto-rename). Parser implementation landed in `preview.html`; significant improvement on piece 066 (orphans 19 → 5, 15+ marker-bound folds resolving). Session closed at a design pivot: next iteration should replace the geometric adjacency search with shared-edge polygon topology — no new authoring required, existing `fold-tab-X` / `fold-landing-Y` ids stay. Closure constraint still parked. See `sessions/2026-05-04-0815_cowork_marker-bound-fold-ids.md`.*

*Earlier 2026-05-03 (evening) — filesystem restructure pass. `.af` + `.svg` per-piece colocation at `work/pieces/NNN/`; `source/pieces/` locked to PNG; `inbox/` retired entirely. Two CODE_PROMPTs handed off (filesystem-restructure + preview-html-source-of-truth). Repo-hygiene track's open question on `inbox/` flipped to resolved. preview.html iteration track gained a pointer to the new source-of-truth prompt. See `sessions/2026-05-03-2345_cowork_filesystem-restructure.md`.*

*Earlier 2026-05-03 (afternoon, addendum) — piece 071 review surfaced two convention corrections: `marks-other` was the wrong name in docs (canonical layer is `marks`) and the landing-marker convention (`landing-<tab><piece>` inside `<g id="marks">`) was settled. Both propagated to all live docs + the asset-state CODE_PROMPT's check registry. The linter-rule pattern absorbed the changes without any per-piece migration. See `sessions/2026-05-03-1400_cowork_asset-state-schema-and-audit.md` (Addendum section).*

*Earlier 2026-05-03 (afternoon) — asset-state schema settled and `CODE_PROMPT_asset-state-audit.md` handed off; `LAYER-CONVENTIONS.md` cheat sheet shipped at repo root in parallel. Asset-state track flipped queued → active.*

*Earlier 2026-05-03 (morning) — initial authoring. Eight tracks seeded from the multi-turn Cowork design conversation that introduced PROJECT-STATE.md + WORKPLAN.md. See `sessions/2026-05-03-0000_cowork_project-state-and-workplan.md`.*
