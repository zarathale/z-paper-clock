---
date: 2026-04-30
start_time: "22:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

# Goal

Execute the 10-step consolidation pass teed up by `sessions/2026-04-30-2100_cowork_repo-audit.md`, with one in-flight pivot folded in: rename the printed clock face from piece 122 → 121 to close the only gap in the book's non-contiguous numbering. Close audit findings A3–A7, B1–B4, C2–C5, and D in a single Cowork commit. A1/A2 (live pipeline scripts crashing under the new `pieces.csv` schema) remain queued for a follow-on Code session as defensive guards before the M0.5.6 reshape.

# What was done

**Decisions settled in chat at start of session.**

- **Piece 121 / clock face renumber.** Cross-referenced the book against the in-repo transcriptions: `instructions.md` never references the face by piece number (only "the face"); `embedded-labels.md` Fig. 15 row had a "labeled `122`" claim that was a misread (the printed face is not numbered in print). Decision: drop the misread and reassign the build-authoring ID from 122 → 121, closing the gap in the book's non-contiguous numbering. The renumber threads through `pieces.csv`, `build_master_list.py`, `embedded-labels.md`, `inventory.md`, `ROADMAP.md`, and CLAUDE.md.
- **`source/scans-intake/`:** delete (per audit recommendation). `inbox/` plays the intake role under chunk-and-crop.
- **ROADMAP M2 reconciliation:** replace per-plate piece tables with a per-plate count summary plus pointer to `work/pieces.csv` as the canonical list. Eliminates the duplication that drove the audit's B2/B3 findings.
- **Session-note HHMM rename:** `2026-04-30-1500_code_M1-fix-pipeline-trace.md` → `2026-04-30-1700_…`; front-matter `start_time` `"15:00"` → `"17:00"`; grep + update each downstream reference.

**Step-by-step execution.** Tracked via the in-app TodoList (13 tasks; 10 from the audit + the renumber + a verification pass + this session note / commit / cleanup hand-off).

1. **Authored `.claude/settings.json`** from CLAUDE.md's "Dev environment (mac)" pre-approval list: `git`, `make`, `python`/`python3`/`python3.12`, `.venv/bin/` binaries, `pip`/`pip3`, `brew`, `potrace`, `gh`, `node`/`npm`/`pnpm`/`npx`, plus read-only inspection (`ls`, `cat`, `rg`, `find`, `grep`, `head`, `tail`, `wc`, `diff`, `awk`, `sed`, `jq`, `tree`). Destructive ops (`rm`, `mv`, `cp`) and WebFetch intentionally NOT pre-approved. Closes A3.
2. **Renumbered the clock face 122 → 121** in `work/pieces.csv` (data row + line-6 comment example), `work/scripts/build_master_list.py` (the `PIECES` tuple + the header docstring example), and `source/transcriptions/embedded-labels.md` (Fig. 15 row, Panel M section header, Panel M section body — drops the misread "labeled 122" claim and rephrases as "not numbered in print; tracked as piece 121 for build authoring"). Verified: regenerating `pieces.csv` from `build_master_list.py` produces output byte-identical to the hand-edited file.
3. **Rewrote `README.md`** for the chunk-and-crop reality: `source/pieces/` and `source/scans-chunks/` introduced; gen-1 phone-scan archive note; pointers to CLAUDE.md (working conventions) and ROADMAP.md (build sequence). Closes A5.
4. **Doc-swept `work/SPEC-3D-VIEWER.md`** — six surgical edits: line-5 source-materials pointer (now `source/pieces/` + `source/scans-chunks/`); the "decisions feeding into this spec" #2 (gen-1 v2 trace test framed as historical); the 2026-04-30 note (now mentions BOTH pivots: rescan-restructure → chunk-and-crop); the "Authoring pipeline" section (steps 1–4 rewritten for chunk-and-crop; pipeline starts at trace reading `source/pieces/`; `01-crop.py` annotated as archived); assembly table (face-and-case row 122 → 121); file-layout tree (added `inbox/`, `source/pieces/`, `source/scans-chunks/`; removed `scans-intake/`; marked `01-crop.py` as ARCHIVED; added `build_master_list.py`; reframed `pieces.csv` schema and `preprocess_scans.py` notes); M1 phasing in past tense ("Shipped 2026-04-30; archived"); M2 piece reference (122 → 121); closing "Sequence" paragraph (M1 archived; M0.5 active; then M2). Closes A6.
5. **Updated `source/inventory.md`** for chunk-and-crop and the renumber: Scan-generations section notes the same-day pivot from plate-rescan to chunk-and-crop; folder layout adds `inbox/`, `pieces/`, `scans-chunks/` (and notes the deletion of `scans-intake/`); file-naming convention split per-piece archive / chunks / legacy plate scans; Page-inventory section reframed as "gen-1 era, archived" with descriptions retained as reference; plate M row updated from "Identified as **piece 122** in Fig. 15" to "Tracked as **piece 121** in `work/pieces.csv` (face is not numbered in print)"; Status section updated to chunk-and-crop in progress with pointers to both pivot session notes. Closes A7.
6. **Deleted `source/scans-intake/`** (folder + README.md + .gitkeep). Required `mcp__cowork__allow_cowork_file_delete` permission since `.claude/`-protected paths block from the Write tool by default. Propagated to inventory.md, SPEC file-layout tree, and CLAUDE.md (file-layout tree + the "legacy folders" sentence). Closes A4.
7. **Reconciled `ROADMAP.md` M2** by replacing the 11 per-plate piece tables (lines 178–356 in the pre-edit doc) with a single per-plate count summary table plus pointer to `work/pieces.csv` as the canonical list. Counts pulled from CSV directly (123 unique pieces: 121 numbered contiguous from 1–121, plus 092a on plate H and 112a on plate E). Replaced "all ~119 pieces" / "all ~119 sidecars" / "all ~119 pieces flat" phrasing with "all 123 pieces"/etc. Cleaned up the now-orphan "per-piece status columns" paragraph. Fixed M1 task 1.1 status `not-started` → `done` (the plate-D bbox work shipped in M1 and is preserved in the archive); annotated that the bbox columns were dropped in the chunk-and-crop pivot. Closes B2, B3, B4.
8. **Tightened CLAUDE.md piece-count phrasing** in three locations (status-table row, file-layout tree, Architectural Decisions table row) to "**121 numbered pieces (1–121, contiguous) + 092a + 112a**" with explicit note that the clock face was renumbered 122 → 121 in this consolidation pass and rationale. Also normalized the letter-variant phrasing from "92a" to "092a" to match the file-naming convention. Closes B1.
9. **Added three CLAUDE.md workflow improvements** to prevent the patterns that drove the audit:
    - **§"Ending a Session, Cowork sessions" gained a doc-sweep step** (now step 3 of 5): grep the repo for the names of anything renamed/retired and confirm README/SPEC/inventory/transcriptions/ROADMAP/CLAUDE.md/archive READMEs are coherent. With a one-line note that the audit existed *because* this step had been skipped over a high-velocity day.
    - **§"Orchestration Prompt Format" gained a shipped-header rule:** after ship, add an italic header below the front matter — `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._` Stops a fresh session from misreading a stale orchestration prompt as a current task list.
    - **§"File Naming Conventions" gained an HHMM collision rule:** if the date+HHMM is already taken in `sessions/`, bump the second to a non-colliding HHMM. Front matter `start_time` should match the filename's HHMM (it's a unique-key, not a precise time log).
   Closes C4, C5.
10. **Applied the new shipped-header convention** to both shipped orchestration prompts at repo root: `CODE_PROMPT_M1-pipeline-plate-d.md` and `CODE_PROMPT_M1-fix-pipeline-trace.md`. One italic line each, below the front matter, above the body. The shipped prompts' bodies are unchanged — they're decision records.
11. **Renamed `sessions/2026-04-30-1500_code_M1-fix-pipeline-trace.md` → `sessions/2026-04-30-1700_code_M1-fix-pipeline-trace.md`**; updated front-matter `start_time` `"15:00"` → `"17:00"`. Grep'd for the old filename across the repo: only one downstream reference (in `2026-04-30-1730_code_M1-fix-validator-reciprocal.md`'s Goal section, identifying its parent session) — updated. The audit's two references to the old filename are intentional historical record (describing the wrongness at audit time) and were not touched.
12. **Verification pass.** Grep'd for stale references to: `piece 122` / `piece-122`, `scans-intake` (in live docs), `scans-prepped` used as live source, the old `1-122 + 92a` phrasing, and the old `1500_code_M1-fix-pipeline-trace` filename. Confirmed: orphan worktree at `.claude/worktrees/tender-hofstadter-2fb755/` retains stale references to all of the above (it's a 225 MB orphan slated for `git worktree prune`); the two shipped CODE_PROMPTs retain "scans-prepped" / "piece-122-face" references in code comments inside the prompt body (intentionally — covered by the new shipped-header convention); historical session notes retain timestamped references to the pre-pivot world (intentionally). All live docs in main, including the just-edited ones, are clean. Independently verified that `python3 work/scripts/build_master_list.py` produces output byte-identical to the hand-edited `work/pieces.csv`.
13. This session note + the standard two-block commit message + the post-merge cleanup bash block.

# Files Changed

| File | Change |
|---|---|
| `.claude/settings.json` (NEW) | Pre-approved Bash patterns for Code sessions, per CLAUDE.md "Dev environment (mac)" |
| `README.md` (rewrite) | Chunk-and-crop reality; pointers to CLAUDE.md / ROADMAP.md; gen-1 archive note |
| `CLAUDE.md` (edits) | Piece-count phrasing tightened (121-not-122; 092a-not-92a); three workflow improvements (doc-sweep step, shipped-header rule, HHMM collision rule); file-layout tree drops `scans-intake/`; "legacy folders" sentence updated |
| `ROADMAP.md` (edits) | M2 per-plate tables → summary + CSV pointer; ~119 → 123 piece counts; M1 task 1.1 status `not-started` → `done` (with bbox-column-drop note) |
| `CODE_PROMPT_M1-pipeline-plate-d.md` (one-line add) | Shipped-header below front matter |
| `CODE_PROMPT_M1-fix-pipeline-trace.md` (one-line add) | Shipped-header below front matter |
| `work/SPEC-3D-VIEWER.md` (doc-sweep) | Six surgical edits: source-materials line, gen-1-trace-test framing, 2026-04-30 note, Authoring pipeline section, assembly table piece-122 → 121, file-layout tree, M1 past-tense, closing paragraph |
| `work/pieces.csv` (edit) | Row 122 → 121; line-6 comment example update; longer notes column on the renumbered piece |
| `work/scripts/build_master_list.py` (edit) | `PIECES` tuple plate-M entry 122 → 121 with explanatory comment; header docstring example update |
| `source/inventory.md` (rewrite of layout/conventions/status sections) | Chunk-and-crop folder layout; per-piece + chunk + legacy file-naming split; gen-1 page inventory reframed as archive; plate M renumbered 122 → 121 |
| `source/transcriptions/embedded-labels.md` (edits) | Drop "labeled 122" claim from Fig. 15 row; rewrite Panel M section to reflect "not numbered in print; tracked as piece 121 for build authoring" |
| `source/scans-intake/` (deleted) | Folder + README + .gitkeep removed; intake now lives at repo-root `inbox/` |
| `sessions/2026-04-30-1500_code_M1-fix-pipeline-trace.md` → `2026-04-30-1700_code_M1-fix-pipeline-trace.md` | Renamed; front-matter `start_time` 15:00 → 17:00 |
| `sessions/2026-04-30-1730_code_M1-fix-validator-reciprocal.md` (one-line edit) | Updated reference to the renamed parent session note |
| `sessions/2026-04-30-2200_cowork_consolidation-pass.md` (NEW) | This file |

# Open questions / Flags

- **A1, A2 (pipeline scripts crashing under the new schema) are not closed by this pass** — they're queued as a follow-on Code session for defensive guards (fail-fast checks at the top of `01-crop.py`, `02-trace.py`, `03-layer-split.py` so they exit with a clear "this script is archived under chunk-and-crop; see ROADMAP M0.5.6" error rather than `KeyError` or silent no-op). Estimated 30 min Code session. The permanent fix is M0.5.6 (archive `01-crop.py`, repoint `02-trace.py` at `source/pieces/`, update Makefile target chain) — already on the ROADMAP.
- **`work/scripts/preprocess_scans.py` still writes to `source/scans-prepped/` by default.** Gen-1 era; not actively run under chunk-and-crop. Per the existing Known Issue in CLAUDE.md, this script is slated for per-piece re-tuning if/when needed. Leave as-is until M0.5 surfaces a re-tuning need.

# Next-session handoff

Two parallel tracks open up:

1. **Code session: pipeline defensive guards** (A1/A2 stop-gap before M0.5.6). Tight `CODE_PROMPT_*.md` adding fail-fast `KeyError`-class guards at the top of the three live pipeline scripts. ~30 min.
2. **Continue M0.5 chunk-and-crop onboarding** — Zarathale at the scanner producing more chunks, hand-cropping into `source/pieces/`. Per `ROADMAP.md` task table M0.5.3 / M0.5.4. Once enough pieces land, queue the piece-scan ingest skill authoring (M0.5.2) as the next CODE_PROMPT.

The ROADMAP M0.5 task table is the source of truth for the active work.

# Commit message (copy/paste)

Subject:

```
consolidate repo state; renumber clock face 122→121; close audit punch list
```

Body:

```
Single Cowork pass closing the audit findings teed up at
sessions/2026-04-30-2100_cowork_repo-audit.md, with one in-flight
pivot folded in: rename the printed clock face piece from 122 → 121
to close the only gap in the book's non-contiguous numbering. The
"labeled 122" claim in embedded-labels.md Fig. 15 was a transcription
misread — the printed face is not numbered in print at all. The
renumber threads through pieces.csv, build_master_list.py,
embedded-labels.md, inventory.md, ROADMAP.md, and CLAUDE.md;
build_master_list.py regenerates pieces.csv byte-identical after the
edit.

Authored .claude/settings.json from CLAUDE.md's pre-approved Bash
patterns (closes A3 — file was claimed-but-absent in the audit).
Rewrote README.md for the chunk-and-crop reality with pointers to
CLAUDE.md and ROADMAP.md (closes A5). Doc-swept SPEC-3D-VIEWER.md:
source-materials pointer, authoring pipeline (chunk-and-crop), file-
layout tree, M1 past tense, both 2026-04-30 pivots noted (closes A6).
Updated source/inventory.md for chunk-and-crop folder layout +
naming conventions; reframed the 27-photo inventory as gen-1 archive;
plate M renumbered (closes A7). Deleted source/scans-intake/ and
propagated to inventory + SPEC + CLAUDE.md (closes A4). Reconciled
ROADMAP M2 by replacing the per-plate tables with a count summary +
CSV pointer; fixed M1 task 1.1 status not-started → done (closes
B2/B3/B4). Tightened CLAUDE.md piece-count phrasing in three
locations to "121 numbered (1-121, contiguous) + 092a + 112a"
(closes B1).

Added three CLAUDE.md workflow improvements to prevent the patterns
that drove this audit: doc-sweep step in §"Ending a Session, Cowork
sessions"; CODE_PROMPT shipped-header convention in §"Orchestration
Prompt Format"; HHMM collision rule in §"File Naming Conventions"
(closes C4/C5). Applied the new shipped-header to both shipped
CODE_PROMPT_*.md files. Renamed the 1500-stamped session note to
1700 with front-matter fix and downstream-reference update (closes
C4 specifically).

Verification: pieces.csv byte-identical against build_master_list.py
output; .claude/settings.json valid JSON; SPEC line 5 + ROADMAP M1
1.1 status + both shipped headers all confirmed; renamed session
note exists, old filename removed; live-docs grep clean of stale
122/scans-intake/old-1-122 phrasing (orphan worktree at
.claude/worktrees/tender-hofstadter-2fb755/ retains stale refs and
is slated for git worktree prune in the post-merge cleanup; shipped
CODE_PROMPT bodies retain ship-time refs intentionally — covered by
the new shipped-header convention; historical session notes retain
timestamped pre-pivot refs intentionally).

Out of scope and queued separately: A1/A2 pipeline-script defensive
guards (Code session, ~30 min); proper M0.5.6 pipeline reshape
(already in ROADMAP); piece-scan ingest skill authoring (M0.5.2).

Files: .claude/settings.json (new); README.md, CLAUDE.md, ROADMAP.md
(rewritten/edited); CODE_PROMPT_M1-pipeline-plate-d.md, CODE_PROMPT_
M1-fix-pipeline-trace.md (shipped-header added); work/SPEC-3D-VIEWER
.md (doc-swept); work/pieces.csv, work/scripts/build_master_list.py
(renumber); source/inventory.md, source/transcriptions/embedded-
labels.md (renumber + chunk-and-crop reality); source/scans-intake/
(deleted); sessions/2026-04-30-1500_code_M1-fix-pipeline-trace.md
→ 2026-04-30-1700_code_…; sessions/2026-04-30-1730_code_M1-fix-
validator-reciprocal.md (parent ref updated); sessions/2026-04-30-
2200_cowork_consolidation-pass.md (new).
```

# Post-merge cleanup (run after the consolidation commit lands on `main`)

Closes audit C2, C3, and D in one block. Frees ~225 MB on disk (the orphan worktree). The `find … -delete` removes 7 `.DS_Store` files; safe — they're gitignored. Skip the `--delete origin` line if those branches were already deleted via the GitHub web UI when their PRs merged.

```bash
cd ~/Documents/GitHub/z-paper-clock
git worktree prune
git fetch --prune
git branch --merged main | grep -E '^\s+claude/' | xargs -r git branch -d
git push origin --delete claude/vigorous-rhodes-06b447 claude/M1-fix-pipeline-trace
find . -name .DS_Store -not -path './.git/*' -not -path './.claude/worktrees/*' -delete
```
