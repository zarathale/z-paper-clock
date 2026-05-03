---
date: 2026-05-03
start_time: "23:59"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: filesystem-restructure
orchestration_prompt: CODE_PROMPT_filesystem-restructure.md
---

**Goal.** Execute the 2026-05-03 evening filesystem restructure: per-piece authoring (`.af`), latest export (`.svg`), and sidecar (`.json`) all colocate at `work/pieces/NNN/`; `source/pieces/` locks to PNG scans only; `inbox/` retires entirely. Repoint `audit_state.py` to the new layout and bump verification paths in `CODE_PROMPT_preview-html-v1b.md`.

**What was done.**

- **Inbox PNG triage (option 2 — drop entirely).** Six tracked PNGs in `inbox/` (065, 066, 067, 069, 070, 071) were not in the orchestration prompt's prerequisites. Diffed all six against the same-id files in `source/pieces/`: all byte-different (070 by 2 bytes only — likely metadata). These looked like Affinity PNG-export companions to the SVG drops, not paper scans, with no slot in the new model (`source/pieces/` = PNG scans only; `work/pieces/NNN/` = `.af` + `.svg` + `.json`). Alan picked drop. `git rm` on all six.
- **Duplicate / variant resolution.** Filesystem mtimes in this worktree all reflected checkout time within ~2 s of each other and were not authoritative — fell back to `git log -1 --format='%ci %H'` to find the actual newer-by-commit version.
  - **069.af.** `source/pieces/069.af` (commit 2026-05-03 16:17, d0f23a07) wins → `work/pieces/069/069.af`. `inbox/069.af` (2026-05-02 09:55, fb5e14e6) → `work/pieces/069/_attic/069-OLD-20260502.af`.
  - **069.svg.** `work/pieces/069/069.svg` (2026-05-03 16:17, d0f23a07) wins; already in place. `inbox/069.svg` (2026-05-02 09:26, e2a4bf1e) → `work/pieces/069/_attic/069-OLD-20260502.svg`.
  - **067 variant.** `source/pieces/067.af` (2026-05-02 10:39, 2b817ccf) wins → `work/pieces/067/067.af`. `source/pieces/067-full.af` (2026-05-01 18:13, 8a48b1c8) → `work/pieces/067/_attic/067-full-OLD-20260501.af`. Iteration variant, not a duplicate; content not merged — attic copy stays available.
- **Bulk moves.** 11 unambiguous `.af` files moved from `source/pieces/` → `work/pieces/NNN/NNN.af` (001, 002, 058, 059, 065, 066, 068, 070, 071, 072, 097). 7 unambiguous `.svg` files moved from `inbox/` → `work/pieces/NNN/NNN.svg` (001, 065, 066, 067, 070, 071, 072). All via `git mv` so history is preserved.
- **`inbox/` deleted.** After all moves, `inbox/` was empty; `rmdir inbox/`.
- **`work/scripts/audit_state.py` updated** (6 edits per task list):
  1. Sidecar path: `piece-{id}.json` → `{id}.json` (line 480 → 479).
  2. Removed the entire `# ── inbox/ ──` walk block (was lines 571–608).
  3. Removed `"inbox_pngs": []` from `PieceState.files` default; removed the `if ps.files["inbox_pngs"]:` anomaly check from `detect_anomalies`.
  4. Extended the `work/pieces/` walk to also slot `.af` files matched by `PIECE_AF` into `pieces[pid].files["affinity"]`. `_attic/` subdirs are ignored (loop filters to direct children only).
  5. Added new anomalies in the `source/pieces/` walk: `repo_anomalies.append(".af file in source/pieces/: …")` + per-piece `"af in source/pieces/ (should be in work/pieces/{pid}/)"` — mirrors the existing SVG-in-source/pieces check.
  6. Bumped `schema_version` 1 → 2 (the `inbox_pngs` field was removed).
- **`CODE_PROMPT_preview-html-v1b.md`** — replaced 7 path references in total (4 of `inbox/069.svg`, 3 of `inbox/066.svg`) with `work/pieces/069/069.svg` / `work/pieces/066/066.svg`. (Replaced everywhere those paths appear, not just Verification Checklist + Manual tests sections, since the intro/prereqs in the same prompt point at the same files.) Status stays `shipped` — that flip already happened before this session.
- **This prompt's status** flipped to `shipped`; added `shipped: 2026-05-03` and the standard `_Shipped …; refer to CLAUDE.md / ROADMAP.md for current state._` italic header.

**Verification (Windows worktree).** Items 1–5, 9–11 of the orchestration prompt's checklist all pass:
- 0 `.af` and 0 `.svg` left in `source/pieces/`.
- `inbox/` does not exist.
- All 13 expected `.af` files present at `work/pieces/NNN/NNN.af`.
- All 8 expected `.svg` files present at `work/pieces/NNN/NNN.svg`.
- 0 stale `inbox/06[69]` refs in v1b prompt; 7 new `work/pieces/06[69]/...` refs.
- `git status` shows clean rename + delete + modify diffs (no stray untracked).

**Audit-run blocked, queued as manual test.** Verification items 6, 7, 8, 12 require running `audit_state.py`, which needs a real Python interpreter. This Code session ran on Alan's Windows machine in a worktree, where only the Windows Store stub `python.exe` is on `PATH` (no real Python installed). Alan's mac has `.venv/bin/python` (per CLAUDE.md dev-env section) — running the audit there post-pull is the next manual step.

**Audit-script edits verified by inspection** (since we couldn't compile-check). Re-read of `audit_state.py` shows: `PieceState.files` default no longer has `inbox_pngs`; the inbox walk block is gone; `work/pieces/` walk now matches both `SVG_FILE` and `PIECE_AF` (with a `continue` after the SVG match so files don't double-count); the new `.af`-in-source/pieces anomaly fires symmetrically with the existing SVG-in-source/pieces one; `schema_version: 2` in the return dict.

**Branch / commit.** `claude/filesystem-restructure` (renamed from the auto-generated `claude/peaceful-jang-a8211e` worktree branch before any commit, per CLAUDE.md branch-name rule). Commit + PR pending at the time of writing this note — adding to message thread once `gh pr create` returns.

**Open questions.**

- **Dead code in `detect_anomalies`.** The `# duplicate .af across source/pieces/ and inbox/` block (now ~lines 626–638) is dead — `inbox_af` will always be `[]` after this restructure. Left as-is because the orchestration prompt's task list didn't request its removal and the verification check `grep -i 'duplicate-affinity' = 0` will still pass (no anomalies fire). Easy follow-up if Alan wants it cleaned up.
- **No other unexpected state surfaced.** All 14 `.af` files, 8 `.svg` files, and 1 `.svg` already in `work/pieces/069/` matched the prerequisites exactly (modulo the inbox PNGs handled above).

**Next-session handoff.** Hand `CODE_PROMPT_preview-html-source-of-truth.md` to Code next — the preview.html piece-id loader (M0.6.14) reads from the canonical `work/pieces/NNN/NNN.svg` paths this session put in place. Before that lands, Alan can manually verify by running `python work/scripts/audit_state.py` on his mac post-merge to confirm verification items 6–8, 12.
