---
date: 2026-04-30
start_time: "21:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
---

# Goal

Full read-and-verify audit of the repo to surface drift, contradictions, and baked-in errors after the high-velocity day of M1 ship + two M0.5 pivots (rescan-restructure → chunk-and-crop). Define a "consolidation pass" punch list for the next Cowork session that closes the gaps surfaced by the audit. No repo files changed in this session; this is a discovery + tee-up note.

# What was done

**Defined audit scope.** Five questions per file/folder: truth (does content match what docs claim?), currency (live state vs. archive vs. stale debris?), discoverability (~10 s for a fresh session to know what to do?), consistency (do conventions hold across siblings?), pointer integrity (do cross-references resolve and agree?). Ten-step check list executed against the live tree.

**Read every doc that drives navigation.** CLAUDE.md, README.md, ROADMAP.md, work/SPEC-3D-VIEWER.md, both CODE_PROMPT_\*.md, source/inventory.md, source/SCAN-INTAKE-CHECKLIST.md, every README in source/ + source/_archive/, source/transcriptions/embedded-labels.md, all 10 prior session notes in chronological order, the full 124-line work/pieces.csv (123 data rows), work/scripts/build_master_list.py, all four work/pipeline/ scripts + Makefile, work/_archive/m1-plate-d-phone/README.md, .gitignore, and the git log + branch + worktree state. Spot-checked the M1 archive contents (11/11 piece directories with crop/raw/bitmap/svg/json each).

**Findings — categorized A through D.**

## Category A — foot-guns and false claims

- **A1.** `work/pipeline/01-crop.py` reads `bbox_x`/`bbox_y`/`bbox_w`/`bbox_h` columns that no longer exist in `pieces.csv` (schema dropped them in the chunk-and-crop pivot). `make pieces` will crash with `KeyError`. CLAUDE.md says "don't run it" but the script itself has no inline indication.
- **A2.** `02-trace.py` and `03-layer-split.py` walk `work/pieces/NNN/` for input. Under chunk-and-crop the canonical input is `source/pieces/NNN.png`. Both scripts run silently and produce nothing.
- **A3.** `.claude/settings.json` (committed pre-approved tool patterns) **does not exist** in the repo. CLAUDE.md "Dev environment (mac)" section claims it does. Drafted in the 16:00 sidecars session, never moved from `outputs/` into `.claude/`.
- **A4.** `source/scans-intake/` exists with a README describing the rescan-restructure intake workflow that was retired same-day by the chunk-and-crop pivot. The new intake folder is `inbox/`. Folder + README contradict the live workflow.
- **A5.** Repo-root `README.md` describes the gen-1 plate-based world. No mention of the archive, the pivots, or the chunk-and-crop loop.
- **A6.** `work/SPEC-3D-VIEWER.md` has the most drift of any active doc. Live-source claims at line 5 still point at `source/scans-prepped/`. The "Authoring pipeline" section still describes a bbox-driven `pieces.csv` with `01-crop.py` as a live stage. The file-layout tree omits `source/pieces/` and `source/scans-chunks/`. M1 phasing reads in present-future tense. The 2026-04-30 note at line 15 only mentions the rescan pivot, not the same-day chunk-and-crop pivot.
- **A7.** `source/inventory.md` describes the rescan-restructure intake (`scans-intake/`/`scans-raw/`/`scans-clean/`/`scans-prepped/` as live). Was never updated for chunk-and-crop.

## Category B — drift between docs that should agree

- **B1.** CLAUDE.md says the master index covers "1-122 + 92a + 112a" (implies 124 entries) and also "123-row" — internally contradictory. Actual: 123, because **piece 121 doesn't exist** (no reference in `embedded-labels.md`, `instructions.md`, or `build_master_list.py`). Accurate phrasing: "1-120 + 122 + 092a + 112a" or simply "123 unique pieces."
- **B2.** ROADMAP M2 per-plate tables list **118 numbered pieces**; `pieces.csv` has **121 numbered pieces** (plus 092a + 112a). The 4 pieces present in CSV but missing from ROADMAP are **40, 41, 42, 43** (which exist physically — they're inside chunk filename `33_37_40_41_50.jpeg`). ROADMAP plate G section is missing them.
- **B3.** ROADMAP plate counts vs CSV plate counts disagree on B (15 vs 14), E (14 vs 15), G (15 vs 18), H (12 vs 14) — different primary-plate calls for cross-plate pieces (e.g., 53, 92a, 112).
- **B4.** ROADMAP M1 milestone-index row says "shipped/archived," but task 1.1 ("Author bbox-by-hand for plate D's 11 pieces") inside the M1 task table is still `not-started`. Work was done (the 11 sidecars exist in the archive); status field is wrong.
- **B5.** `embedded-labels.md` line 5 still references `scans-clean/` as the lookup path for piece numbers. That folder is empty (gen-2) or archived (gen-1).
- **B6.** `work/_archive/m1-plate-d-phone/README.md` claims `pieces.csv` has bbox columns ("bbox fractions describing each piece's location"). True at archive time, false now.

## Category C — workflow gaps

- **C1.** Commit `1047271` ("add reciprocal:false flag for one-directional connections; fix validator," co-authored by Claude Sonnet 4.6) shipped as part of PR #2 but **has no session note**. Per CLAUDE.md this is a violation. The orphan worktree at `.claude/worktrees/tender-hofstadter-2fb755/` is on this commit — it's the unrecorded session's working state.
- **C2.** Two merged feature branches still exist locally and on origin: `claude/vigorous-rhodes-06b447`, `claude/M1-fix-pipeline-trace`. CLAUDE.md "Post-merge cleanup" not run.
- **C3.** Orphan worktree `.claude/worktrees/tender-hofstadter-2fb755/` is **225 MB** on disk, marked `prunable` by `git worktree list`. Gitignored so it doesn't pollute commits, but `git worktree prune` would clean it.
- **C4.** Two session-note HHMM collisions (15:00 and 16:00). `2026-04-30-1500_code_M1-fix-pipeline-trace.md` claims `start_time: "15:00"` in front matter and filename, but the work followed the 16:00 cowork pipeline-bug-audit (which produced its CODE_PROMPT). File mod time 17:59 confirms. Filename + front matter both wrong.
- **C5.** Both shipped CODE_PROMPT_\*.md have `status: shipped` correctly, but their bodies are still pure present-tense ("`source/scans-prepped/p00x-plate-D-...jpg` exists"). They become misleading to a fresh session that mistakes them for a current task list.

## Category D — small cleanups

7 `.DS_Store` files on disk under tracked folders (gitignored, harmless on the wire — but noise locally). Locations: repo root, `inbox/`, `sessions/`, `source/`, `work/`, `work/_archive/m1-plate-d-phone/pieces/`, `work/_archive/m1-plate-d-phone/auto-trace-test/`.

# Files Changed

Mostly read-only audit + tee-up; three small, isolated fixes folded in at end-of-session because the audit context was loaded and the items were independent of the broader consolidation pass.

- `sessions/2026-04-30-2100_cowork_repo-audit.md` (NEW) — this file.
- `sessions/2026-04-30-1730_code_M1-fix-validator-reciprocal.md` (NEW) — retroactive note for commit `1047271` (the `reciprocal: false` flag + validator fix that shipped without a session note as part of PR #2). Closes C1.
- `work/_archive/m1-plate-d-phone/README.md` (EDITED) — added a one-line callout at the top noting that `pieces.csv` has since dropped bbox columns and expanded to a 123-row master, so claims below about pieces.csv schema are accurate as of M1 archive time only. Closes B6.
- `source/transcriptions/embedded-labels.md` (EDITED) — fixed the line-5 lookup hint to point at `source/pieces/` (and `source/scans-chunks/` until the per-piece archive populates) instead of the now-empty `scans-clean/`. Closes B5.

# Open Questions / Flags

- **Piece 121.** Confirmed not referenced anywhere in source. Almost certainly genuinely absent from the book (which uses non-contiguous numbering — the cover advertises "160 pieces" but the highest numbered piece in the transcriptions is 122, with gaps). Worth a one-line confirmation from Zarathale before the consolidation pass tightens CLAUDE.md's phrasing.
- **`.claude/settings.json` resolution.** Two paths: (a) re-author and commit it for real this time, or (b) remove the CLAUDE.md claim. Recommend (a) — the pre-approval list is genuinely useful for Code sessions, and a single sandboxed Cowork pass can write the file. CLAUDE.md "Dev environment (mac)" already specifies its contents.
- **`source/scans-intake/` disposition.** Two paths: (a) rewrite README + folder purpose for chunk-and-crop, or (b) delete folder. Recommend (b); `inbox/` already plays this role and the folder is vestigial.
- **CODE_PROMPT_\*.md historical-marker convention.** Add a one-line "_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._" header below the front matter on both shipped prompts. Cheap, prevents stale reads. Adopting this would also be a CLAUDE.md addition.

# Next-Session Handoff

Run a single Cowork **consolidation pass** that closes A3–A7, B1–B4, the Cowork-owned bits of C (C4, C5), and D. (B5, B6, and C1 were folded into this audit session, see Files Changed.) A1/A2 are Code-owned and queue separately as defensive guards (see post-consolidation block below). One session, one commit. Estimated 45–75 min. Order:

1. **Move/draft `.claude/settings.json`** (closes A3). The original outputs draft is gone (Cowork sandbox cleared between sessions); re-author from CLAUDE.md's "Dev environment (mac)" pre-approval list. Verify by listing the file. Note: the committed file is `.claude/settings.json`; the gitignored sibling is `.claude/settings.local.json`.

2. **Rewrite `README.md`** (closes A5). Short, public-facing. Mention the gen-1 → gen-2 transition; point at CLAUDE.md for working conventions and ROADMAP for build sequence. Drop "27 cleaned scans cataloged" — that's gen-1 era and now an archive claim, not a live one.

3. **Doc-sweep pass on `work/SPEC-3D-VIEWER.md`** (closes A6). Update line 5 (live-source pointer); revise "Authoring pipeline" steps 1–4 to describe chunk-and-crop (no bbox, no plate slicing, pipeline starts at trace reading `source/pieces/`); update the file-layout tree to add `source/pieces/` + `source/scans-chunks/` and mark `01-crop.py` as archived; rewrite the M1 section in past tense ("M1 shipped against gen-1 phone scans 2026-04-30; archived"). Refresh the line-15 note to mention both pivots.

4. **Update `source/inventory.md`** (closes A7). Folder layout section: `inbox/` is intake, `source/scans-chunks/` is chunk archive, `source/pieces/` is per-piece archive. `scans-intake/`/`scans-raw/`/`scans-clean/`/`scans-prepped/` are legacy/empty (note them as such). Status section: drop "scans-raw/clean/prepped will repopulate" — that was the rescan-restructure plan that got retired.

5. **Decide and act on `source/scans-intake/`** (closes A4) per the Open Questions item. Recommend deleting the folder; if kept, rewrite the README to point at `inbox/` as the actual intake.

6. **Reconcile `ROADMAP.md` M2 per-plate tables with `pieces.csv`** (closes B2, B3, B4). Pick one of:
   - **(Recommended)** Replace per-plate tables with a per-plate count summary plus "see `work/pieces.csv` for canonical list." Reduces duplication and drift surface; CSV is the canonical source.
   - **(Alternative)** Regenerate per-plate tables from CSV by hand. Captures pieces 40/41/42/43 in plate G, fixes B/E/G/H plate-count disagreements. More work; preserves doc style.
   Either way: while in ROADMAP, fix M1 task 1.1 status `not-started` → `done` (that's B4 regardless of which approach).

7. **Tighten CLAUDE.md "1-122 + 92a + 112a" claim** (closes B1) to "123 unique pieces (1–120 + 122 + 092a + 112a; piece 121 doesn't exist in the book)." Pending Zarathale confirmation per Open Questions.

8. **Add CLAUDE.md improvements** to prevent the patterns that drove this audit:
    - **Doc-sweep step** in §"Ending a Session, Cowork sessions": "Before drafting the commit message, grep the repo for the names of anything renamed/retired in this session and confirm `README.md`, `work/SPEC-3D-VIEWER.md`, `source/inventory.md`, `source/transcriptions/`, CLAUDE.md itself, and any READMEs in `source/_archive/`/`work/_archive/` are coherent. Update each downstream reference or annotate it as legacy."
    - **CODE_PROMPT shipped-header rule** in §"Orchestration Prompt Format" (closes C5): "After ship, add a one-line italic header below the front matter: '_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._' Apply this to both existing shipped prompts at root."
    - **HHMM collision rule** in §"File Naming Conventions" (closes C4): two sessions in the same HHMM window should bump the second to a non-colliding HHMM (e.g., 16:00 + 16:30 instead of 16:00 + 16:00). Also fix `2026-04-30-1500_code_M1-fix-pipeline-trace.md` to reflect its actual start time — recommend renaming to `2026-04-30-1700_code_M1-fix-pipeline-trace.md` and editing front matter `start_time: "17:00"`. Be careful: this file is referenced from `CODE_PROMPT_M1-fix-pipeline-trace.md` and from CLAUDE.md/ROADMAP.md commit/Notes columns; grep for the old filename before renaming. The retroactive `2026-04-30-1730_code_M1-fix-validator-reciprocal.md` shipped in this session at a non-colliding HHMM and is fine as-is.

9. **At end-of-session, hand Zarathale the post-merge cleanup commands** (closes C2, C3, D):
    ```bash
    cd ~/Documents/GitHub/z-paper-clock
    git worktree prune
    git fetch --prune
    git branch --merged main | grep -E '^\s+claude/' | xargs -r git branch -d
    git push origin --delete claude/vigorous-rhodes-06b447 claude/M1-fix-pipeline-trace
    find . -name .DS_Store -not -path './.git/*' -not -path './.claude/worktrees/*' -delete
    ```
    These run after the consolidation commit lands on `main`. The worktree-prune line frees ~225 MB.

10. **Author session note** for the consolidation pass and produce the standard two-block commit message.

**Then queue (separately, post-consolidation):**

- **Code session: pipeline defensive guards.** Tight `CODE_PROMPT_*.md` for adding fail-fast checks at the top of `01-crop.py`, `02-trace.py`, `03-layer-split.py` so they exit with a clear "this script is archived under chunk-and-crop; see ROADMAP M0.5.6" error rather than `KeyError` or silent no-op. Closes A1, A2 as a stop-gap. ~30 min Code session.
- **The existing M0.5.6** — proper pipeline reshape (archive `01-crop.py`, repoint `02-trace.py` at `source/pieces/`, update Makefile). The permanent fix; supersedes the defensive guards. Already in ROADMAP.
- **Per the existing M0.5.2** — author the piece-scan ingest skill once the consolidation pass settles the surrounding docs.

# Commit message (copy/paste)

Subject:

```
audit repo; tee up consolidation pass; backfill + small fixes
```

Body:

```
sessions/2026-04-30-2100_cowork_repo-audit.md (new): full read-and-
verify pass over CLAUDE.md, README, ROADMAP, SPEC, both shipped
CODE_PROMPTs, all 10 prior session notes, source/ + work/ structure,
the 123-row pieces.csv, every pipeline script, archive READMEs,
.gitignore, and git state. Findings categorized A-D: foot-guns and
false claims (live pipeline scripts crash under the new pieces.csv
schema; .claude/settings.json claimed-but-absent; SPEC + README +
inventory still describe the pre-chunk-and-crop world); drift
between docs (pieces.csv vs ROADMAP M2 vs CLAUDE.md disagree on
piece counts and plate assignments; piece 121 doesn't exist in the
book); workflow gaps (commit 1047271 missing session note; merged
branches not cleaned up; 225 MB orphan worktree); small cleanups.

sessions/2026-04-30-1730_code_M1-fix-validator-reciprocal.md (new):
retroactive note for commit 1047271 (the reciprocal:false flag +
validator fix that shipped as part of PR #2 without a session note).
Backfilled while audit context was loaded.

work/_archive/m1-plate-d-phone/README.md (edited): one-line callout
at top noting that pieces.csv has since dropped bbox columns and
expanded to a 123-row master, so claims below about the schema are
accurate as of M1 archive time only.

source/transcriptions/embedded-labels.md (edited): line-5 lookup
hint repointed from the now-empty scans-clean/ to source/pieces/
(and source/scans-chunks/ until that archive populates).

Next-session handoff is a 10-step Cowork consolidation pass closing
A3-A7, B1-B4, C2-C5, and D: .claude/settings.json, README rewrite,
SPEC doc-sweep, inventory update, scans-intake disposition, ROADMAP
M2 reconciliation, CLAUDE.md piece-count phrasing, three CLAUDE.md
workflow improvements (doc-sweep step, CODE_PROMPT shipped-header
convention, HHMM collision rule), post-merge cleanup commands.
Followed by a Code session for pipeline defensive guards (A1, A2),
then the existing M0.5.6 reshape and M0.5.2 ingest skill.
```
