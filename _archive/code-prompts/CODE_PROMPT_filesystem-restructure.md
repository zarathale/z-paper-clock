---
status: shipped
started: 2026-05-03
shipped: 2026-05-03
owner: Zarathale (Alan)
target: filesystem-restructure
---

_Shipped 2026-05-03; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

## What You Are Doing and Why

The repo has accumulated drift in where authoring files (`.af`), SVG exports, and chunk-scan staging live. `.af` files split between `source/pieces/` (14) and `inbox/` (1). SVG exports split between `inbox/` (8) and `work/pieces/NNN/` (1). The `inbox/` folder is doing double duty — chunk-scan staging AND export-staging — and the second use is the painful one. There's also a duplicate (`069.af` in both `inbox/` and `source/pieces/`) and an iteration variant (`067-full.af` next to `067.af`) that need explicit canonicalization.

This Code session executes the 2026-05-03 evening filesystem restructure pass settled in `sessions/2026-05-03-2345_cowork_filesystem-restructure.md`. End state: each piece gets a single working folder at `work/pieces/NNN/` containing `NNN.af` (Affinity authoring), `NNN.svg` (latest export), `NNN.json` (sidecar, when authored), and optionally `crop.png` (pipeline output). `source/pieces/` locks to PNG scans only — no `.af`, no `.svg`. `inbox/` is retired entirely.

## Prerequisites — confirm before starting

- 14 `.af` files exist in `source/pieces/`: 001, 002, 058, 059, 065, 066, 067, 067-full, 068, 069, 070, 071, 072, 097.
- 1 `.af` file exists in `inbox/`: 069.af.
- 8 `.svg` files exist in `inbox/`: 001, 065, 066, 067, 069, 070, 071, 072.
- 1 `.svg` file already exists at `work/pieces/069/069.svg` (Alan dropped it manually before this session).
- `work/pieces/` exists; only currently-populated subdirectory is `069/`.
- `work/scripts/audit_state.py` is the current audit (schema_version 1).
- `CODE_PROMPT_preview-html-v1b.md` exists at repo root and references `inbox/069.svg` and `inbox/066.svg` in its verification section.
- Python 3.12 + `.venv` at repo root.
- `gh` CLI installed and authenticated.

## Read These Files First

1. `sessions/2026-05-03-2345_cowork_filesystem-restructure.md` — design rationale.
2. `CLAUDE.md` "Architectural Decisions (Closed)" → row "Per-piece authoring + export colocation; `inbox/` retired".
3. `CLAUDE.md` "File Naming Conventions" → "Per-piece working folder" bullet.
4. `work/scripts/audit_state.py` — the audit code you're modifying (full read; the changes touch 4 places).
5. `CODE_PROMPT_preview-html-v1b.md` — verification-paths bump.

## Target File Structure Changes

```
source/pieces/                              ← lock to PNG scans only
├── 001.af  002.af  058.af  059.af          ← REMOVE (move to work/pieces/NNN/NNN.af)
├── 065.af  066.af  067.af  067-full.af     ← REMOVE (067 variant: see canonical-pick rule)
├── 068.af  069.af                          ← REMOVE (069: see duplicate-pick rule)
├── 070.af  071.af  072.af  097.af          ← REMOVE
├── ... (PNGs unchanged)

inbox/                                      ← REMOVE entirely
├── 069.af                                  ← REMOVE (see duplicate-pick rule)
├── 001.svg  065.svg  066.svg  067.svg      ← REMOVE (move to work/pieces/NNN/NNN.svg)
├── 069.svg                                 ← REMOVE (see SVG-pick rule; work/pieces/069/069.svg already exists)
├── 070.svg  071.svg  072.svg               ← REMOVE

work/pieces/                                ← populated
├── 001/001.af  001/001.svg                 ← NEW
├── 002/002.af                              ← NEW
├── 058/058.af  059/059.af                  ← NEW
├── 065/065.af  065/065.svg                 ← NEW
├── 066/066.af  066/066.svg                 ← NEW
├── 067/067.af  067/067.svg                 ← NEW (canonical .af picked per rule)
├── 068/068.af                              ← NEW
├── 069/069.af                              ← NEW (canonical picked from inbox/source duplicate)
├── 069/069.svg                             ← already exists; resolve per SVG-pick rule
├── 070/070.af  070/070.svg                 ← NEW
├── 071/071.af  071/071.svg                 ← NEW
├── 072/072.af  072/072.svg                 ← NEW
├── 097/097.af                              ← NEW
├── NNN/_attic/                             ← only if the canonical-pick rules archive a loser

work/scripts/audit_state.py                 ← UPDATE (sidecar short form; drop inbox walk; catch .af in work/pieces; new "af in source" anomaly)
CODE_PROMPT_preview-html-v1b.md             ← UPDATE (verification paths)
```

## Numbered Tasks

### 1. Resolve duplicate / variant ambiguities

**1.1 Duplicate `069.af` (inbox vs. source/pieces).**

```bash
cd ~/Documents/GitHub/z-paper-clock
diff source/pieces/069.af inbox/069.af && echo IDENTICAL || echo DIFFERENT
```

- If IDENTICAL: canonical is either; pick `inbox/069.af` (reflects newer-in-workflow), `mv` it to `work/pieces/069/069.af`, and `rm source/pieces/069.af`.
- If DIFFERENT: canonical is the **newer by mtime**. Use `stat -f "%m %N" source/pieces/069.af inbox/069.af` and pick the higher mtime. Move newer to `work/pieces/069/069.af`. Archive the older to `work/pieces/069/_attic/069-OLD-YYYYMMDD.af` (YYYYMMDD = older file's mtime date). `mkdir -p work/pieces/069/_attic/` first.

Log in the session note: which path won, which path was archived (or deleted), and the rule applied (IDENTICAL vs newer-by-mtime).

**1.2 Duplicate `069.svg` (inbox vs. work/pieces/069/).**

```bash
diff inbox/069.svg work/pieces/069/069.svg && echo IDENTICAL || echo DIFFERENT
```

- If IDENTICAL: canonical is `work/pieces/069/069.svg` (already in place); `rm inbox/069.svg`.
- If DIFFERENT: newer by mtime wins. If newer is `inbox/069.svg`, archive existing `work/pieces/069/069.svg` to `_attic/069-OLD-YYYYMMDD.svg` first, then `mv inbox/069.svg work/pieces/069/069.svg`. If newer is the existing one, `rm inbox/069.svg` (no archive needed since the canonical was already in place).

Log the decision.

**1.3 Variant `067-full.af` vs. `067.af`.**

These are NOT duplicates — they're iteration variants. Pick canonical by mtime: newer becomes `work/pieces/067/067.af`. Archive the older to `work/pieces/067/_attic/` with name `067-OLD-YYYYMMDD.af` or `067-full-OLD-YYYYMMDD.af` depending on which lost. Don't try to merge content. Log the decision and Alan can re-open the attic copy later if he wants.

### 2. Create per-piece directories under `work/pieces/`

For each of {001, 002, 058, 059, 065, 066, 067, 068, 069, 070, 071, 072, 097}: `mkdir -p work/pieces/NNN/`. Idempotent; existing `069/` stays.

### 3. Move `.af` files (the unambiguous ones)

```bash
mv source/pieces/001.af   work/pieces/001/001.af
mv source/pieces/002.af   work/pieces/002/002.af
mv source/pieces/058.af   work/pieces/058/058.af
mv source/pieces/059.af   work/pieces/059/059.af
mv source/pieces/065.af   work/pieces/065/065.af
mv source/pieces/066.af   work/pieces/066/066.af
mv source/pieces/068.af   work/pieces/068/068.af
mv source/pieces/070.af   work/pieces/070/070.af
mv source/pieces/071.af   work/pieces/071/071.af
mv source/pieces/072.af   work/pieces/072/072.af
mv source/pieces/097.af   work/pieces/097/097.af
```

Pieces 067, 069 are handled by the resolutions in task 1.

### 4. Move `.svg` files from `inbox/`

```bash
mv inbox/001.svg  work/pieces/001/001.svg
mv inbox/065.svg  work/pieces/065/065.svg
mv inbox/066.svg  work/pieces/066/066.svg
mv inbox/067.svg  work/pieces/067/067.svg
mv inbox/070.svg  work/pieces/070/070.svg
mv inbox/071.svg  work/pieces/071/071.svg
mv inbox/072.svg  work/pieces/072/072.svg
```

069 handled by task 1.2.

### 5. Delete the empty `inbox/` folder

```bash
ls -A inbox/   # should print nothing
rmdir inbox/
```

If anything remains in `inbox/`, **stop and report** in the session note — don't delete unfamiliar files.

### 6. Update `work/scripts/audit_state.py`

**6.1.** Sidecar check uses long-form filename. In `derive_stage` (around line 480), change:

```python
sidecar = REPO_ROOT / "work" / "pieces" / ps.id / f"piece-{ps.id}.json"
```

to:

```python
sidecar = REPO_ROOT / "work" / "pieces" / ps.id / f"{ps.id}.json"
```

**6.2.** Delete the inbox-walking block in `walk_repo`. The block starts at the `# ── inbox/ ──` comment (around line 571) and runs to just before `# ── work/pieces/ ──` (around line 610). Remove the block entirely. The `inbox/` folder no longer exists; the `if inbox_dir.exists():` guard would silently skip forever, but cleaning the dead code is the right move.

**6.3.** In `PieceState.files` (around line 110–116), remove the `"inbox_pngs": []` field. In `detect_anomalies` (around line 678), remove the `if ps.files["inbox_pngs"]:` block. Search the rest of the file for any other `inbox_pngs` references and remove (there should be none).

**6.4.** Extend the `# ── work/pieces/ ──` walk (around line 610) to also catch `.af` files. Today it only matches via `SVG_FILE`. Add a parallel `PIECE_AF.match(fname)` check inside the existing per-file loop and slot matches into `pieces[pid].files["affinity"]` exactly as the source/pieces walk does. Use the same regex (`PIECE_AF`) — it already accepts variant suffixes. Variant suffixes inside `work/pieces/NNN/_attic/` should NOT count as canonical — only direct children of `work/pieces/NNN/` matter; `_attic/` is the archive zone.

**6.5.** Add a new anomaly to the `source/pieces/` walk: when a `.af` file is matched, append `repo_anomalies.append(f".af file in source/pieces/: {name}")` and `pieces[pid].anomalies.append(f"af in source/pieces/ (should be in work/pieces/{pid}/)")`. This mirrors the existing SVG-in-source/pieces anomaly. After this restructure, the audit should NEVER find an `.af` in `source/pieces/` — the rule is locked.

**6.6.** Bump `schema_version` from 1 to 2 in `run_audit`'s return dict (around line 788) — the field set on `PieceState` changed (no more `inbox_pngs`).

**6.7.** Run `python work/scripts/audit_state.py` after the moves. Confirm:
- Exit 0.
- `summary.repo_anomalies` is empty (or only entries unrelated to this restructure).
- No `duplicate-affinity-file` anomalies remain on any piece.
- No `svg in source/pieces/` or `af in source/pieces/` anomalies.
- `summary.by_stage` shows ~12–13 pieces in `affinity_started` (those with `.af` but no `.svg` yet) plus 7–8 in `svg_drafted` (those with both `.af` and `.svg` and no sidecar).

### 7. Update `CODE_PROMPT_preview-html-v1b.md` verification paths

Replace path references in the Verification Checklist + Manual tests sections:

- `inbox/069.svg` → `work/pieces/069/069.svg`
- `inbox/066.svg` → `work/pieces/066/066.svg`

Don't change the prompt's `status` (stays `ready-for-code`).

### 8. Session note + commit + PR

Write `sessions/YYYY-MM-DD-HHMM_code_filesystem-restructure.md` with:
- Front matter: `target: filesystem-restructure`, `orchestration_prompt: CODE_PROMPT_filesystem-restructure.md`.
- Goal one-liner.
- What was done — the 14 `.af` moves, 8 `.svg` moves, the duplicate/variant resolutions (with mtime/diff evidence), `inbox/` deleted, audit script updated, v1b prompt path-bumped.
- Branch / commit SHA.
- Open questions: any pieces that surfaced unexpected state.
- Next-session handoff: hand `CODE_PROMPT_preview-html-source-of-truth.md` to Code next.

Branch: `claude/filesystem-restructure`. Commit subject: `move .af + .svg into work/pieces/NNN/; retire inbox/; repoint audit`. PR via `gh pr create` per CLAUDE.md.

Flip THIS prompt's front-matter `status` to `shipped`, add `shipped: YYYY-MM-DD`, add the italic header `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._`

## Verification Checklist

1. `ls source/pieces/*.af 2>/dev/null | wc -l` returns `0`.
2. `ls source/pieces/*.svg 2>/dev/null | wc -l` returns `0`.
3. `[ -d inbox ]; echo $?` returns `1`.
4. For each of {001, 002, 058, 059, 065, 066, 067, 068, 069, 070, 071, 072, 097}: `[ -f work/pieces/NNN/NNN.af ]` succeeds.
5. For each of {001, 065, 066, 067, 069, 070, 071, 072}: `[ -f work/pieces/NNN/NNN.svg ]` succeeds.
6. `python work/scripts/audit_state.py --quiet && echo OK` succeeds.
7. `python work/scripts/audit_state.py 2>&1 | grep -iE 'svg in source/pieces|af in source/pieces' | wc -l` returns `0`.
8. `python work/scripts/audit_state.py 2>&1 | grep -i 'duplicate-affinity' | wc -l` returns `0`.
9. `grep -c 'inbox/06[69]' CODE_PROMPT_preview-html-v1b.md` returns `0`.
10. `grep -cE 'work/pieces/069/069\.svg|work/pieces/066/066\.svg' CODE_PROMPT_preview-html-v1b.md` returns `≥ 2`.
11. `git status` shows the moves + audit-script change + v1b-prompt change as clean staged diffs (no stray untracked files).
12. Audit's stage histogram contains entries for `affinity_started` AND `svg_drafted` (counts will match the file inventory).

## What NOT to Change

- Don't touch any `source/pieces/NNN.png` files. Those stay put.
- Don't touch `source/scans-chunks/`. Chunk-and-crop intake is a separate workflow.
- Don't touch any file under `work/_archive/`. M1 archive uses `piece-NNN.svg` long-form intentionally — those are decision records.
- Don't touch `work/pieces.csv`. Status flips are deliberate manual edits per the existing convention.
- Don't run the auto-trace pipeline (`make pieces`); it's stale and would fail.
- Don't write SVG content. The 9 SVGs being moved are Alan's authored exports — they're inputs, not outputs of this session.
- Don't try to merge or modify `069.af` or `069-full.af` content — pick canonical, archive the rest, move on.
- Don't touch `preview.html` itself — that's a separate prompt (`CODE_PROMPT_preview-html-source-of-truth.md`).

## Manual tests (optional, post-merge)

| Test | Expected |
|---|---|
| Open `work/pieces/069/069.af` in Affinity | File opens, layered as before. |
| Open `work/pieces/069/069.svg` in `preview.html` (drag-drop) | Renders the same as it did pre-move. |
| `python work/scripts/audit_state.py` | Summary shows ~13 pieces in `affinity_started` or `svg_drafted`. No `inbox/` references. |
