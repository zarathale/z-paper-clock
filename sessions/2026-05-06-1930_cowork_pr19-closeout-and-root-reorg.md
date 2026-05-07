---
date: 2026-05-06
start_time: "19:30"
end_time: "22:30"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Three things, started as one and grew:

1. Review what landed in PR #19 (assembled-pose load + save in `preview.html`) against the prompt's verification checklist; update docs.
2. Verify Bob batch continuation work Alan did at the bench: pieces 070, 093a, 093b, 087, 097 — and review a freshly-regenerated `build_assembly_graph.py` run.
3. Reorganize the root of the project folder per Alan's directive: move shipped CODE_PROMPTs to `_archive/code-prompts/`, then audit every remaining root file for stale facts and broken references.

The third item flipped a long-standing convention (CLAUDE.md previously said shipped prompts stay at root as decision records); the new rule keeps root clean while-in-flight and archives the decision record after ship. 21 stale shipped prompts had piled up at root.

## What was done

### PR #19 review

Read the Code-session note (`sessions/2026-05-06-1900_code_preview-html-assembled-pose.md`) and confirmed all 9 verification checks logged green. The `assembled.folds` schema (DECISIONS #11) is now wired through `preview.html`'s `maybeLoadSidecar` → `loadPieceById` (Option A reorder) → `renderPanelsFirstScene` slider build, with a "Save assembled pose" modal (copy + download). Scene mode opted out for v1; per-piece assembled poses across a scene parked as a follow-up.

### Bob batch verification

- **070** ✓ — `panelsideb`/`panelsidec` panel ids renamed to `sideb`/`sidec` in `070.af`/`070.svg`. Both folds resolve cleanly in the fresh graph (2/2 of 2).
- **093a / 093b** ✓ — under `work/pieces/093/` with `silhouette` + `panels` + `folds-valley` + `marks` + clean `cutaway` ids. 093b carries cross-half `attach-x093a` in `attach-points`. Combined `093.svg`/`.af` retired to `work/pieces/093/_attic/` (Alan moved during the session — original draft was at `work/pieces/_attic/`, which is now empty).
- **087** — `source/pieces/087.png` exists; no `work/pieces/087/` folder yet (.af authoring underway on the bench, no SVG export). Pieces.csv stays at `captured` until the SVG lands.
- **097** — confirmed authoring state: 5 elements at id `attach-a99` plus Affinity-suffixed `attach-a991`/`a992`/`a993`/`a994`. Per Alan: leaving as authored, treating the parser-tolerance recommendation (convention #16, strip digit suffix when base id resolves) as informational only — not promoting to a convention. If it ever truly matters, Alan will author each instance with a unique id.

### Fresh `build_assembly_graph.py` run

17 panels-first pieces, 24 valid authored cross-piece edges. 4 invalid edges from 097 (the Affinity-suffixed ids — expected behavior given Alan's stance). 070 folds clean. **Caveat surfaced:** the script's main loop only globs `work/pieces/<dir>/<dir>.svg`, so split pieces (093a + 093b in the 093 folder) are silently absent from the report. Logged as QUEUE Soon #4.

### Doc updates from the review

- `claude-work/QUEUE.md` — Now #1 (assembled-pose) + Now #2 (bob batch) struck through to Recently shipped with full provenance for each piece (070 / 093a / 093b / 087 / 097). Tag-pieces.html promoted to Now #1 with the v2-schema pre-req corrected (it shipped, not ready-for-code). Soon section renumbered: `attach-x` convention #2, architecture call #3, new #4 for the build-graph split-pieces extension. Footer log entry added.
- `claude-work/STATUS.md` — Charter rollout track logs PR #19 + bob-batch verification. SVG layer authoring track closes 070 stale-ids and 097 collision-suffix as resolved (Alan's authoring choice), keeps 093a/093b fold paths and `attach-x<piece-id>` convention as the live opens, adds the `<dirname>.svg` graph-script gap as a status detail. preview.html iteration track clears the queued CODE_PROMPT and notes the parked scene-mode follow-up.
- `claude-work/DECISIONS.md` — #11 downstream pointer flipped to "shipped 2026-05-06 via PR #19"; v1 follow-up parked (per-piece `assembled.folds` map keyed by `_sceneId` for scene mode).

### Root-folder reorganization

Convention flip: shipped CODE_PROMPTs now move to `_archive/code-prompts/` rather than staying at root.

- Moved 19 `status: shipped` + 1 `status: superseded` (`v1.md`) prompt from root → `_archive/code-prompts/`.
- Caught a filename collision: the pre-existing archived-without-shipping v1b draft (`status: archived`) and the shipped v1b shared the canonical filename. Restored the archived draft from git (`d0403b4`) and renamed it to `CODE_PROMPT_preview-html-v1b-archived-draft.md`. Updated the cross-references in the shipped v1b's `supersedes:` line + body, and in `work/SPEC-REGIONS.md` § "Relation to other docs."
- Updated `CLAUDE.md` four places to match the new rule: intro paragraph, Orchestration Prompt Format § (Naming + After-ship paragraphs), end-of-Code-session step #6, and the File Naming Conventions Orchestration-prompts row. Killed-without-shipping prompts get an explicit paragraph in the After-ship section noting they live alongside shipped prompts in the archive folder, distinguished by `status: archived` + `archived_reason:`.
- Rewrote the Repo Structure tree in CLAUDE.md (was last refreshed 2026-05-03 and missing `claude-work/`, `_archive/code-prompts/`, `LAYER-CONVENTIONS.md`, `PROJECT-STATE.md`, `WORKPLAN.md`, `ROADMAP.md`, `preview.html`, `tag-pieces.html`, `work/SPEC-REGIONS.md`, `work/state.json`, the v2 yamls, and `.claude/`).

### Stale-fact pass on remaining root files

- `CLAUDE.md` status table refreshed: capture row 117/123 → 123/123 (closed 2026-05-05); M0.5 reframed (capture done, pipeline reshape pending); M0.6 row enumerates the post-0.6.14 ships; new "Panels-first SVG authoring" row; framing paragraph points at `claude-work/STATUS.md` rather than WORKPLAN.md; piece-scan-ingest row updated to reflect archive (final state below).
- `README.md` Layout + Status sections rewrote: added `claude-work/`, `LAYER-CONVENTIONS.md`, `PROJECT-STATE.md`, `preview.html`, `tag-pieces.html`; corrected the active milestone from "M0.5 chunk-and-crop" to panels-first SVG authoring + M0.6 preview iteration with a STATUS.md pointer.
- `WORKPLAN.md` got a "⚠ FROZEN — pre-charter record" banner at the top (it had been quietly frozen since charter sign-off but didn't say so on the file itself).
- `PROJECT-STATE.md`: 117/123 → 123/123; preview.html capability paragraph rewritten (panels-first parser + multi-piece scene + assembled-pose, was the v1a snapshot); "In progress" + "How to read" + "Active exploration tracks" sections updated to reflect STATUS.md as the live surface; `inbox/` retired-section folded out; `claude-work/` directory section added; CODE_PROMPT lifecycle line added; new footer note dated 2026-05-06.
- `ROADMAP.md`: header banner pointing readers at STATUS.md for live state; row 0.5.4 flipped done with closure date; M0.6 footer block added explicitly noting post-0.6.14 ships are tracked in STATUS.md.
- `LAYER-CONVENTIONS.md`: read-through, no edits needed (recent and current).

### Lone in-flight prompt — archived per Alan's call

`CODE_PROMPT_M0.5.2-piece-scan-ingest.md` was the only remaining in-flight prompt at root. Source-side capture closed at 123/123 on 2026-05-05 without the helper getting written; `claude-work/scripts/build_assembly_graph.py` and `work/scripts/audit_state.py` cover most of the audit ground in practice. Archived at Alan's direction:

- Front matter flipped to `status: archived` + `archived: 2026-05-06` + `archived_reason:` documenting the shift in urgency. Italic header added below front matter ("Archived 2026-05-06 without shipping...").
- File moved to `_archive/code-prompts/`.
- `CLAUDE.md` status-table row "Piece-scan ingest skill" updated to 📦 archived with full context.
- `ROADMAP.md` row 0.5.2 flipped from `in-progress` → `archived` with the Notes column documenting the why and pointing at the archived prompt + the two scripts that cover the audit ground.

The skill's `SKILL.md` at `.claude/skills/piece-scan-ingest/SKILL.md` is preserved as design record; the helper script described in the prompt was never written.

### Final root state

```
CLAUDE.md
LAYER-CONVENTIONS.md
PROJECT-STATE.md
README.md
ROADMAP.md
WORKPLAN.md      (frozen banner)
preview.html
tag-pieces.html
```

`_archive/code-prompts/` now holds 22 files (20 newly moved this session + 2 pre-existing archived). Zero CODE_PROMPTs at root.

## Open questions

None blocking. Two on the queue that surfaced or sharpened today:

- **Architecture call (DECISIONS #4: preview.html ↔ work/viewer/).** Three substantive preview-side ships now sit on top of the current substrate (PR #17 multi-piece scene, PR #18 inferred-connections audit, PR #19 assembled-pose). Enough on the table to settle. Next Cowork beat.
- **`attach-x<piece-id>` convention formalization.** Alan flagged in QUEUE Soon #2 (with the comment "open to reauthoring this, wasn't trying to define a whole new standard. Let's discuss."). Small Cowork conversation when bench rhythm allows.

## Next-session handoff

- Bench-side: pull QUEUE Now #1 (tag 123 pieces in `tag-pieces.html`) when bench time happens. The v2 schema is shipped, so the tagger is ready to use directly.
- Cowork-side: pull QUEUE Soon #3 (architecture call). The `attach-x<piece-id>` conversation could ride along if it's adjacent.
- The 070/093a/093b/087/097 bob-batch state is fully captured in QUEUE Recently-shipped + STATUS recent-log; nothing follows up automatically.
