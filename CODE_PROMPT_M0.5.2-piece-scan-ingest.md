---
status: ready-for-code
started: 2026-04-30
owner: Zarathale (Alan)
target: M0.5.2-piece-scan-ingest
---

## What You Are Doing and Why

Author the Python helper that powers the `piece-scan-ingest` skill. The skill's `SKILL.md` is already in place at `.claude/skills/piece-scan-ingest/SKILL.md` (drafted in `sessions/2026-04-30-2300_cowork_M0.5.2-ingest-skill-draft.md`). It tells Claude to run `.claude/skills/piece-scan-ingest/scripts/audit.py` and render its stdout to chat. That helper is what this Code session writes.

The audit closes the chunk-and-crop loop: it reads `work/pieces.csv` (the 123-row master list), walks `source/pieces/` and `source/scans-chunks/`, and reports captured-vs-pending status with cross-referenced chunk-source suggestions for each pending piece. Read-only by contract — never writes to disk, never modifies `pieces.csv`.

This is **M0.5.2** in `ROADMAP.md`. Estimated 1.5 hours including verification. Once shipped, the chunk-and-crop loop is fully audited end-to-end — Alan can ask "what's pending?" at any time and get a clean answer.

---

## Prerequisites — confirm before starting

- `.claude/skills/piece-scan-ingest/SKILL.md` exists and reads as expected (the skill description and helper contract are both there)
- `.claude/skills/piece-scan-ingest/scripts/` directory exists (empty; this Code session populates it)
- `work/pieces.csv` exists with 123 data rows + header + comment block
- `source/pieces/` exists (likely empty of PNGs at audit-helper-author time; the helper must handle that gracefully)
- `source/scans-chunks/` exists with at least the 8 chunks captured 2026-04-30
- `.venv/bin/python` exists at repo root with Pillow installed (`/.venv/bin/python -c "import PIL; print(PIL.__version__)"` succeeds)
- Native `potrace` not required for this milestone

---

## Read These Files First

1. `.claude/skills/piece-scan-ingest/SKILL.md` — the skill's contract and the helper's expected stdout structure
2. `source/SCAN-INTAKE-CHECKLIST.md` — the canonical chunk filename patterns and the 600 DPI capture standard (the helper's WARN thresholds derive from here)
3. `work/pieces.csv` — both the schema (in the comment block at the top) and the data rows (123 IDs the audit validates against)
4. `CLAUDE.md` §"File Naming Conventions" — confirms the `NNN.png` / `NNNa.png` / chunk filename forms
5. `work/pipeline/04-validate-sidecars.py` — for style reference (existing pipeline-validator pattern to mirror; not for logic)
6. `ROADMAP.md` M0.5 row — confirms this task's place in the sequence

---

## Target File Structure Changes

```
.claude/
└── skills/
    └── piece-scan-ingest/
        ├── SKILL.md                     ← exists; do not modify
        └── scripts/
            └── audit.py                 ← NEW: this is what we author
```

No other files change. No new dependencies. Pillow is already in `.venv`.

---

## Numbered Tasks

### Task 1 — Filename pattern regexes

Define and unit-test (mentally) these compiled regexes at the top of `audit.py`. They must match exactly the patterns documented in `SCAN-INTAKE-CHECKLIST.md`.

```python
import re

# Per-piece archive: source/pieces/NNN.png or source/pieces/NNNa.png
PIECE_PNG = re.compile(r"^(\d{3})([a-z])?\.png$")

# Chunks: NN_NN_NN.{jpeg,png}, NN.{jpeg,png}
# (One or more numeric IDs separated by underscores, then .jpeg/.jpg/.png)
CHUNK_LIST = re.compile(r"^(\d+(?:_\d+)+)\.(jpe?g|png)$")
CHUNK_SINGLE = re.compile(r"^(\d+)\.(jpe?g|png)$")

# Stitched composites: NN_stitched.png (single-piece) or NN_NN_stitched.png (multi-piece). Always PNG.
CHUNK_STITCHED = re.compile(r"^(\d+(?:_\d+)*)_stitched\.png$")

# L/R partials: NN_l.jpeg / NN_r.jpeg (single-piece) or NN_NN_l.jpeg / NN_NN_r.jpeg (multi-piece). Always JPEG.
CHUNK_LR = re.compile(r"^(\d+(?:_\d+)*)_(l|r)\.jpeg$")
```

Match order matters when files have ambiguous-looking names. Check `CHUNK_STITCHED` and `CHUNK_LR` **before** `CHUNK_LIST`, since `34_35_l.jpeg` would naively match a permissive list pattern. Use anchored, mutually-exclusive regexes as above; any file that matches none of them is an error.

### Task 2 — Master-list reader

Parse `work/pieces.csv` into a set of normalized IDs. The file has comment lines starting with `#` followed by a CSV header and data rows. Use `csv.DictReader` after filtering comment lines.

```python
import csv
from pathlib import Path

def load_master(repo_root: Path) -> set[str]:
    """Return set of piece IDs from work/pieces.csv (e.g., {'001', '092a', '121'})."""
    pieces_csv = repo_root / "work" / "pieces.csv"
    with pieces_csv.open(newline="") as f:
        # Skip comment lines; DictReader handles header + body
        rows = (line for line in f if not line.startswith("#"))
        reader = csv.DictReader(rows)
        return {row["id"].strip() for row in reader if row.get("id")}
```

After loading, assert `len(ids) == 123` — if not, fail loudly with a clear error. The master list is the source of truth; if it drifted, the audit's accuracy is compromised.

Also build a per-plate map for the report's "Pending pieces grouped by plate" section:

```python
def load_master_with_plates(repo_root: Path) -> dict[str, str]:
    """Return {piece_id: plate_letter}."""
    # Same parser but returns dict.
```

### Task 3 — Repo-root detection

Use `git rev-parse --show-toplevel` so the helper works from any cwd:

```python
import subprocess

def find_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())
```

Wrap with try/except `subprocess.CalledProcessError` and fail with a clear message if not in a git repo.

### Task 4 — Per-piece file audit

For each file in `source/pieces/`, run the tiered checks defined in SKILL.md. Use Pillow's `Image.open()` for image-header inspection only — call `.verify()` to check integrity, then re-open (verify closes the file) for `.size` / `.mode` / `.info.get('dpi')`.

```python
from PIL import Image

def audit_piece_file(path: Path, master_ids: set[str]) -> tuple[list, list]:
    """Return (errors, warnings). Each entry: dict with file, kind, detail."""
    errors, warnings = [], []
    name = path.name

    m = PIECE_PNG.match(name)
    if not m:
        errors.append({"file": str(path), "kind": "bad_filename",
                       "detail": "does not match NNN[a].png pattern"})
        return errors, warnings

    piece_id = m.group(1) + (m.group(2) or "")
    if piece_id not in master_ids:
        errors.append({"file": str(path), "kind": "unknown_id",
                       "detail": f"id {piece_id} not in pieces.csv"})
        return errors, warnings

    # Integrity check
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as exc:
        errors.append({"file": str(path), "kind": "unreadable",
                       "detail": f"{type(exc).__name__}: {exc}"})
        return errors, warnings

    # Header inspection (re-open since verify() invalidates)
    with Image.open(path) as img:
        dpi = img.info.get("dpi")
        size = img.size
        mode = img.mode

    if dpi is None:
        warnings.append({"file": str(path), "kind": "dpi_missing",
                         "detail": "no DPI metadata; expected 600"})
    elif min(dpi) < 600:
        warnings.append({"file": str(path), "kind": "dpi_low",
                         "detail": f"DPI {dpi}; expected >= 600"})

    if min(size) < 400:
        warnings.append({"file": str(path), "kind": "small_dims",
                         "detail": f"size {size}; expected >= 400 px on each axis"})

    if mode not in ("RGB", "RGBA"):
        warnings.append({"file": str(path), "kind": "color_mode",
                         "detail": f"mode {mode}; expected RGB/RGBA"})

    if path.stat().st_size < 50_000:
        warnings.append({"file": str(path), "kind": "small_file",
                         "detail": f"{path.stat().st_size} bytes; expected >= 50 KB"})

    return errors, warnings
```

### Task 5 — Per-chunk file audit

Walk `source/scans-chunks/` and parse every file. Each chunk yields a list of declared piece IDs (the numeric IDs in the filename, normalized to three-digit zero-padded). Anything that doesn't match one of the four patterns is a BLOCK error. Any declared ID not in the master list is a BLOCK error.

```python
def normalize_id(raw: str) -> str:
    """Pad a raw chunk id like '4' or '92' to '004' or '092'."""
    return raw.zfill(3)

def parse_chunk_ids(name: str) -> tuple[list[str], str] | None:
    """Return (list of piece ids, kind) or None if no pattern matches.

    kind ∈ {'list', 'single', 'stitched', 'left', 'right'}
    """
    if (m := CHUNK_STITCHED.match(name)):
        return [normalize_id(x) for x in m.group(1).split("_")], "stitched"
    if (m := CHUNK_LR.match(name)):
        side = "left" if m.group(2) == "l" else "right"
        return [normalize_id(x) for x in m.group(1).split("_")], side
    if (m := CHUNK_LIST.match(name)):
        return [normalize_id(x) for x in m.group(1).split("_")], "list"
    if (m := CHUNK_SINGLE.match(name)):
        return [normalize_id(m.group(1))], "single"
    return None
```

For each chunk file:

- If `parse_chunk_ids` returns `None` → BLOCK: `bad_chunk_filename`
- Try `Image.open(...).verify()` → BLOCK: `unreadable` if it fails (no further checks for chunks; chunks don't get cosmetic checks since they're intermediate)
- For each declared piece ID: if not in `master_ids` → BLOCK: `unknown_id`

### Task 6 — Cross-reference: pending pieces ↔ chunks

Build the `pending_with_sources` mapping:

```python
def build_pending_index(
    master_ids: set[str],
    captured_ids: set[str],
    chunk_inventory: dict[str, list[str]],  # chunk_filename -> list of piece ids
) -> dict[str, list[str]]:
    """Return {pending_piece_id: [chunk_filenames containing this piece]}."""
    pending = master_ids - captured_ids
    return {
        pid: sorted(chunk for chunk, ids in chunk_inventory.items() if pid in ids)
        for pid in sorted(pending)
    }
```

### Task 7 — Markdown report writer

Print the report to stdout in the exact section order from `SKILL.md` "Report structure":

```
# Piece-Scan Ingest Audit

## Summary

- Captured: {n} / {total}
- Pending:  {n}
- BLOCK errors: {n}
- WARN issues:  {n}

## BLOCK errors  (only if there are any)

(list)

## WARN issues  (only if there are any)

(list)

## Pending pieces

### Plate A (3 pending)
- 001 — chunks: 1_2_3.jpeg, 1_5.jpeg
- 003 — chunks: (none — needs capture)
- ...

### Plate B (12 pending)
...

## Chunk inventory

- 4_18_19_26_29_30_31_32_91_92.jpeg — pieces: 004, 018, 019, 026, 029, 030, 031, 032, 091, 092
- 10.jpeg — pieces: 010
- ...

## inbox/  (footnote, only if files present)

3 files in inbox/: Scan_001.jpg, Scan_002.jpg, Scan_003.jpg
(M0.5.3 in flight; loop not fully drained)
```

Skip empty sections (no "BLOCK errors" header if zero errors). Order pending pieces by plate letter (A through M, with letter variants under their plate) per the master list's `plate` column.

### Task 8 — Argparse + main + exit code

```python
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true",
                        help="emit JSON instead of markdown")
    args = parser.parse_args()

    repo_root = find_repo_root()
    master = load_master_with_plates(repo_root)

    # ... walk dirs, run audits, build report ...

    if args.json:
        print(json.dumps(report_dict, indent=2))
    else:
        print(render_markdown(report_dict))

    return 1 if any_block_errors else 0

if __name__ == "__main__":
    sys.exit(main())
```

### Task 9 — Module docstring and CLI help

Top of file:

```python
#!/usr/bin/env python3
"""Audit source/pieces/ and source/scans-chunks/ against work/pieces.csv.

Read-only. Reports captured-vs-pending status with image-health checks and
chunk-source suggestions for pending pieces. Exit 0 if no BLOCK errors;
1 otherwise.

Run from anywhere in the repo:
    .venv/bin/python .claude/skills/piece-scan-ingest/scripts/audit.py

Bundled with the piece-scan-ingest skill at .claude/skills/piece-scan-ingest/.
"""
```

---

## Verification Checklist

Run these from the repo root after the helper exists. Each must pass before merging.

1. **Helper executes cleanly with current archive state.**
   ```bash
   .venv/bin/python .claude/skills/piece-scan-ingest/scripts/audit.py
   echo "exit=$?"
   ```
   Expected: a markdown report listing 0 captured, 123 pending, all 8 chunks parsed; exit 0 (no BLOCK errors with current repo state).

2. **Master-list assertion fires correctly.**
   Temporarily comment out one row in `work/pieces.csv`, run the helper, confirm it fails loudly with a "master list has 122 rows; expected 123" error. Restore the row.

3. **Bad filename triggers BLOCK error.**
   Create a temp file `source/pieces/badname.png` (any valid PNG; copy the SKILL.md if needed and rename), run the helper, confirm it surfaces the bad-filename BLOCK error, exit code 1. Remove the temp file.

4. **Unknown ID triggers BLOCK error.**
   Create `source/pieces/999.png` (any valid PNG), run, confirm `unknown_id` BLOCK error. Remove.

5. **Cosmetic warnings fire on a low-DPI / small file.**
   Create a small synthetic PNG (200×200, 72 DPI, RGB) named `source/pieces/004.png` (or whichever ID isn't yet captured), run, confirm WARN entries for `dpi_low` (or `dpi_missing`) and `small_dims`. Remove.

6. **JSON mode produces valid JSON.**
   ```bash
   .venv/bin/python .claude/skills/piece-scan-ingest/scripts/audit.py --json | python -m json.tool > /dev/null
   echo "json valid: $?"
   ```
   Expected: exit 0.

7. **Performance target: under 1 second on the current archive.**
   ```bash
   time .venv/bin/python .claude/skills/piece-scan-ingest/scripts/audit.py > /dev/null
   ```
   Expected: real time well under 1 second. (Image-header inspection only; no full pixel decode.)

8. **No file writes.**
   ```bash
   git status -s
   ```
   Before and after running the helper, the working-tree status should be identical. The helper writes nothing.

9. **Chunk parsing covers all existing chunks.**
   Confirm the report's "Chunk inventory" section lists all 8 files currently in `source/scans-chunks/`:
   - `4_18_19_26_29_30_31_32_91_92.jpeg`
   - `10.jpeg`
   - `33_37_40_41_50.jpeg`
   - `34_35_l.jpeg`, `34_35_r.jpeg`, `34_35_stitched.png`
   - `42_52_53_54_55_56_57.jpeg`
   - `43_44_45.jpeg`
   And that pieces 4, 10, 18, 19, 26, 29, 30, 31, 32, 33, 34, 35, 37, 40, 41, 42, 43, 44, 45, 50, 52, 53, 54, 55, 56, 57, 91, 92 are listed as pending pieces with chunk sources identified. (Piece 51 is no longer in `source/scans-chunks/` — its chunk source `36_51.jpeg` is still in `inbox/_pending-rescan/` awaiting promotion.)

---

## What NOT to Change

- **Do not modify `work/pieces.csv`.** The audit is read-only. Status flips are out of scope for this milestone.
- **Do not modify `SKILL.md`.** It's the contract; the helper conforms to it.
- **Do not add CLI flags beyond `--json`.** `--quiet`, `--piece NNN`, etc. are deferred until concrete needs surface (per SKILL.md "Notes for the helper").
- **Do not introduce dependencies beyond Pillow + standard library.** No `click`, no `rich`, no `pydantic`. Argparse for CLI; csv module for parsing; Pillow for images.
- **Do not OCR image content.** Filenames are the declared truth. The audit must never try to derive a piece ID from pixels.
- **Do not touch the live pipeline scripts** (`01-crop.py`, `02-trace.py`, `03-layer-split.py`, `04-validate-sidecars.py`). The defensive-guards prompt is separate; this prompt is scoped to the audit helper only.
- **Do not write a Makefile target.** The skill invokes the helper directly via the path.
- **Do not commit a sample report fixture.** A minimal helper + the verification checks above are enough.

---

## Manual tests (after merge)

Run these from `~/Documents/GitHub/z-paper-clock` after the PR merges and `main` is current:

| # | Pre-condition | Action | Expected |
|---|---|---|---|
| 1 | Current archive (8 chunks, 0 pieces) | `.venv/bin/python .claude/skills/piece-scan-ingest/scripts/audit.py` | Markdown report; 0 captured / 123 pending; all 8 chunks listed; exit 0 |
| 2 | Same | Invoke from a subdirectory: `cd source && ../.venv/bin/python ../.claude/skills/piece-scan-ingest/scripts/audit.py` | Same report (repo-root detection works) |
| 3 | Drop a single PNG into `source/pieces/004.png` (any file from `source/scans-chunks/` works as a stand-in if you copy and rename) | Re-run | Report shows 1 captured, 122 pending; piece 004 not listed under pending |
| 4 | Add a typo: `source/pieces/abc.png` | Re-run | Exit code 1; BLOCK error `bad_filename` for `abc.png` |
| 5 | Add a chunk with an unknown id: `source/scans-chunks/999_888.jpeg` (copy any existing chunk and rename) | Re-run | Exit code 1; BLOCK error `unknown_id` for `999`, `888` |

After tests, clean up any temp files added.

---

## Branch and commit

- Branch: `claude/M0.5.2-piece-scan-ingest`
- Commit subject: `add piece-scan-ingest helper at .claude/skills/piece-scan-ingest/scripts/audit.py`
- After ship: flip this prompt's front matter `status: ready-for-code` → `shipped`, add `shipped: YYYY-MM-DD`, add the italic shipped-header line below the front matter per CLAUDE.md convention.
- No version bump (pipeline-only / skill-only work; viewer not yet versioned).
- Session note: `sessions/YYYY-MM-DD-HHMM_code_M0.5.2-piece-scan-ingest.md` per CLAUDE.md convention.
- ROADMAP update: flip M0.5.2 status `not-started` → `done` with closing-session-note pointer.
