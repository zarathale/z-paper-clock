---
status: ready-for-code
started: 2026-05-03
owner: Zarathale (Alan)
target: asset-state-audit-v0
---

## What You Are Doing and Why

Author `work/scripts/audit_state.py` — the v0 read-only audit script that walks the repo and emits a single `work/state.json` describing where every piece is in its lifecycle. Output is the basis of "what's the state of piece N" answers in chat today and (later) a static-HTML dashboard.

This advances the **Asset-state / audit tooling** track in `WORKPLAN.md`. The core design decisions are settled:

- Per-piece state is computed from filesystem reality every run. Nothing is hand-maintained. `pieces.csv`'s `status` column stays as a manual editorial signal; the audit is the machine-truth.
- Authoring conventions are encoded as **independent checks** (linter-rule pattern), not as a single SVG version stamp. New convention = add a new check; existing pieces get re-flagged automatically. This is the mechanic for the "uplift to new authoring standard" pain point Alan called out — pieces don't migrate, conventions are checked retroactively every audit run.
- Output for v0 is a single fat `work/state.json` (fast to ship, easy to skim). Future migration to per-piece sidecars is open.

This is a Cowork→Code handoff. The script lives at `work/scripts/audit_state.py` alongside `build_master_list.py`, runs via `.venv/bin/python work/scripts/audit_state.py`, takes ~seconds, exits 0 on read-only success, and is safe to run any time.

---

## Prerequisites — confirm before starting

- `.venv/bin/python` exists at repo root with Pillow + lxml installed (`/.venv/bin/python -c "import PIL, lxml; print('ok')"` succeeds).
- `work/pieces.csv` exists with 123 data rows + header + comment block.
- `source/pieces/` exists with at least some PNGs (currently 117 of 123).
- `work/scripts/build_master_list.py` exists (style reference for repo conventions).
- This prompt and `WORKPLAN.md`'s Asset-state track are aligned (read both before starting).

---

## Read These Files First

1. `WORKPLAN.md` §"Track: Asset-state / audit tooling" — the hypothesis and design decisions
2. `CLAUDE.md` §"File Naming Conventions" — what the audit recognizes as canonical filenames
3. `CLAUDE.md` §"Architectural Decisions (Closed)" — rows for cut-layer authoring convention, axle + north convention, faithful-trace direction (the audit's initial check set comes from these)
4. `source/pieces/README.md` — confirms `source/pieces/` holds canonical PNGs only (no SVGs); .af files there are drift, not deliberate
5. `work/pieces.csv` — schema (in comment block) + 123 data rows the audit validates against
6. `work/scripts/build_master_list.py` — style reference (Python 3.12, no externals beyond stdlib + a couple of pip libs)
7. `work/SPEC-3D-VIEWER.md` §"Authoring/QA preview tool (`preview.html`)" — for canonical SVG layer names + per-element id rules (the convention checks reference these)

---

## Target File Structure Changes

```
work/
├── scripts/
│   ├── build_master_list.py         ← exists; do not modify
│   └── audit_state.py               ← NEW: this is what we author
├── state.json                       ← NEW: generated output (committed; small, queryable, history-useful)
└── pieces.csv                       ← exists; never modified by audit
```

No other files change. No new dependencies — Pillow + lxml already in `.venv`.

`.gitignore` is intentionally **not** updated to exclude `state.json`. Committing the file gives Git history of asset-state evolution, which is useful for "when did piece 069 get its first SVG?" investigations and for the eventual dashboard. The file is small (~20-50 KB for 123 pieces).

---

## Numbered Tasks

### Task 1 — File header and CLI

```python
#!/usr/bin/env python3
"""
audit_state.py — Read-only asset-state audit for z-paper-clock.

Walks the repo, computes per-piece state from filesystem reality, emits work/state.json.
Never writes anywhere except work/state.json. Never modifies pieces.csv or anything under source/.

Usage:
    python work/scripts/audit_state.py            # write state.json + print summary
    python work/scripts/audit_state.py --quiet    # write state.json; suppress summary
    python work/scripts/audit_state.py --piece 069  # detailed report for one piece (no file write)
    python work/scripts/audit_state.py --check    # exit non-zero if any required check fails
"""

from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# Resolve repo root from this file's location: work/scripts/audit_state.py → repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
```

`--check` is the CI-style invocation: returns non-zero if any required-severity check fails on any piece. Skip this for v0 if it complicates the implementation; advisory only.

### Task 2 — Master-list reader

Reuse the `build_master_list.py` parsing pattern. Comment lines start with `#`; CSV header follows; data rows have `id, plate, section, bucket, status, notes`.

```python
def load_master(repo_root: Path) -> dict[str, dict]:
    """Return {piece_id: {plate, section, bucket, status, notes}} from work/pieces.csv."""
    pieces_csv = repo_root / "work" / "pieces.csv"
    with pieces_csv.open(newline="") as f:
        rows = (line for line in f if not line.startswith("#"))
        reader = csv.DictReader(rows)
        return {
            row["id"].strip(): {k: row.get(k, "").strip() for k in ("plate", "section", "bucket", "status", "notes")}
            for row in reader
            if row.get("id")
        }
```

After loading, assert `len(master) == 123` — fail loudly otherwise (the master list is the source of truth).

### Task 3 — Filename regexes (mirror M0.5.2 ingest skill)

```python
PIECE_PNG     = re.compile(r"^(\d{3})([a-z])?\.png$")
PIECE_AF      = re.compile(r"^(\d{3})([a-z])?(?:-([a-z]+))?\.af$")  # captures suffixes like -full
SVG_FILE      = re.compile(r"^(\d{3})([a-z])?(?:-([a-z]+))?\.svg$")
CHUNK_LIST    = re.compile(r"^(\d+(?:_\d+)+)\.(jpe?g|png)$")
CHUNK_SINGLE  = re.compile(r"^(\d+)\.(jpe?g|png)$")
CHUNK_STITCH  = re.compile(r"^(\d+(?:_\d+)*)_stitched\.png$")
CHUNK_LR      = re.compile(r"^(\d+(?:_\d+)*)_(l|r)\.jpeg$")
```

The `PIECE_AF` and `SVG_FILE` patterns capture an optional suffix slug (e.g. `067-full.af`, future `069-draft.svg`) so variants are catalogued, not hidden.

### Task 4 — Per-piece state record

```python
@dataclass
class PieceState:
    id: str
    csv_meta: dict
    files: dict = field(default_factory=lambda: {
        "source_png": None,
        "affinity": [],          # list of {path, suffix or None}
        "svgs": [],              # list of {path, suffix or None, mtime}
        "inbox_pngs": [],        # PNGs in inbox/ matching this id (cleanup nudges)
        "derivative_dir_files": [],  # files in work/pieces/NNN/ if directory exists
        "chunk_membership": [],  # chunk filenames in source/scans-chunks/ that include this id
    })
    svg_analysis: Optional[dict] = None  # populated only if at least one svg found
    convention_checks: list[dict] = field(default_factory=list)
    stage: str = "pending_capture"
    anomalies: list[str] = field(default_factory=list)
```

`stage` is derived (Task 8) from booleans elsewhere in the record. `anomalies` are human-facing warnings (e.g. duplicate .af file, off-spec layer name, csv status disagrees with filesystem).

### Task 5 — Filesystem walk

Walk these directories and slot files into the right piece:

| Directory | Pattern | Slot |
|---|---|---|
| `source/pieces/` | `PIECE_PNG` | `files.source_png` |
| `source/pieces/` | `PIECE_AF` | `files.affinity` (each entry: `{path, suffix}`) |
| `source/pieces/` | `SVG_FILE` | `files.svgs` + anomaly `"svg in source/pieces (should be in work/pieces/NNN/)"` |
| `source/pieces/` | other | anomaly `"unrecognized file in source/pieces"` (skip README.md) |
| `inbox/` | `SVG_FILE` | `files.svgs` |
| `inbox/` | `PIECE_AF` | `files.affinity` |
| `inbox/` | `PIECE_PNG` | `files.inbox_pngs` (cleanup: this should normally promote to `source/pieces/` or chunks) |
| `inbox/` | `CHUNK_*` | NOT a per-piece file; record under repo-level summary |
| `work/pieces/NNN/` | any file | `files.derivative_dir_files` (just list filenames) |
| `source/scans-chunks/` | `CHUNK_*` | for each piece-id token in the filename, append to that piece's `files.chunk_membership` |

If the same piece has `.af` files in both `source/pieces/` and `inbox/`, append both AND add an anomaly `"duplicate-affinity-file"`. Do not pick a winner.

If the SVG appears in multiple folders (inbox/ + work/pieces/NNN/), include all and anomaly `"svg-in-multiple-locations"`.

### Task 6 — SVG analysis

For each piece with at least one SVG, pick a `primary_svg` (newest mtime), parse it with `lxml.etree`, and populate `svg_analysis`:

```python
{
    "primary_svg": "inbox/069.svg",
    "primary_svg_mtime": "2026-05-02T16:05:00Z",
    "all_svgs": ["inbox/069.svg"],
    "xml_well_formed": True,
    "view_box": "0 0 1234 5678" or None,
    "layers_present": ["silhouette", "axles", "folds-valley"],
    "layer_id_inventory": {
        "silhouette": ["cutaway"],
        "axles": ["north"],
    },
    "off_spec_layers": []  # any <g id="..."> at top level whose id isn't in CANONICAL_LAYERS
}
```

Use `inkscape:label` as a fallback when `id` is missing on a top-level `<g>`. Recognize the Affinity-wraps-silhouette-children-in-unnamed-`<g>` case (see CLAUDE.md cut-layer convention row): walk descendants of `<g id="silhouette">` looking for ids in `{cutaway, cutaway-N, mask, mask-N}`.

```python
CANONICAL_LAYERS = {
    "silhouette", "cutouts", "folds-valley", "folds-mountain",
    "axles", "glue-zones", "labels", "marks-other",
}
```

### Task 7 — Convention checks (the linter)

Each check is a function `(svg_root: lxml.etree._Element, layer_inventory: dict) -> CheckResult`. Run each against the primary SVG. A `CheckResult` is:

```python
{
    "id": "silhouette-layer-present",
    "description": "<g id=\"silhouette\"> exists at top level",
    "severity": "required",     # required | advisory | conditional
    "result": "pass",            # pass | fail | skip | error
    "evidence": "Found 1 silhouette layer with cutaway child" or None,
    "message": None              # populated on fail/skip/error
}
```

Initial check set:

| ID | Description | Severity |
|---|---|---|
| `xml-well-formed` | SVG parses without error | required |
| `silhouette-layer-present` | `<g id="silhouette">` exists at top level | required |
| `silhouette-cutaway-id` | Has `cutaway` or `cutaway-N` element among silhouette descendants | required |
| `cutouts-layer-format` | If `<g id="cutouts">` exists, all numbered children use `cutout-N` ids (not `cutout-letter`) | advisory |
| `axles-layer-clean` | If `<g id="axles">` exists, contains only ellipse/circle/path elements + optional `id="north"` | advisory |
| `axles-north-marker-shape` | If `id="north"` exists, it is a parseable shape (ellipse/circle/rect/path) | advisory |
| `mask-elements-ignorable` | `mask` / `mask-N` ids appear only inside `<g id="silhouette">` (not at top level) | advisory |
| `canonical-layer-names-only` | All top-level `<g>` ids are in CANONICAL_LAYERS or are `mask` / `mask-N` (visual frame) | advisory |
| `no-stray-paths-at-root` | No `<path>` elements directly under `<svg>` (everything in a layered group) | advisory |

Each check is one small function. Adding a new convention later = adding one function and one row to the registry list. **This is the uplift mechanic.**

Implementation pattern:

```python
@dataclass
class CheckResult:
    id: str
    description: str
    severity: str
    result: str
    evidence: Optional[str] = None
    message: Optional[str] = None

CHECKS = []  # populated by @register decorator

def register(check_id: str, description: str, severity: str):
    def deco(fn):
        CHECKS.append((check_id, description, severity, fn))
        return fn
    return deco

@register("silhouette-layer-present", "<g id='silhouette'> exists at top level", "required")
def check_silhouette_layer(svg_root, inventory):
    if "silhouette" in inventory:
        return CheckResult(..., result="pass", evidence=f"Found 1 silhouette layer")
    return CheckResult(..., result="fail", message="Top-level <g id='silhouette'> not found")
```

`severity = "conditional"` checks include a `_applies(piece_state)` predicate (e.g. `axles-layer-present` only applies to §II.B / §II.C / face pieces). For v0, leave `conditional` as a documented severity but skip implementation — make every check unconditional.

### Task 8 — Lifecycle stage (derived)

Compute `stage` from the booleans, in priority order:

```
in_viewer            ← if work/manifest.json (when it exists later) lists this id
sidecared            ← if work/pieces/NNN/piece-NNN.json exists
svg_validated        ← if all required-severity checks pass
svg_layered          ← if SVG exists AND silhouette + at least one of {folds-valley, folds-mountain, axles} present
svg_drafted          ← if SVG exists (any state)
affinity_started     ← if .af exists, no SVG
captured_only        ← if PNG exists, nothing further
pending_capture      ← if no PNG
```

Surface in the per-piece record. Do NOT write back to `pieces.csv`.

### Task 9 — Anomaly detection (cross-cutting)

Add anomaly strings to the per-piece record when:

- duplicate .af file across `source/pieces/` + `inbox/`
- SVG present in multiple folders
- SVG present but no PNG (orphan derivative)
- PNG in `inbox/` matching this id (should have been promoted)
- pieces.csv `status` says `traced` but no SVG found, or says `pending` but PNG exists
- variant suffix on .af (`067-full.af`) — informational, not error

Repo-level anomalies (in the summary, not per-piece):

- chunk files in `inbox/` (chunks should live in `source/scans-chunks/`)
- unrecognized files at the root of `source/pieces/` (other than README.md)
- piece IDs in filenames that aren't in pieces.csv

### Task 10 — Output: state.json

```python
{
  "schema_version": 1,
  "generated_at": "2026-05-03T14:30:00Z",
  "repo_root": "/Users/.../z-paper-clock",
  "audit_revision": "2026-05-03",   # bump when checks change
  "summary": {
    "total_pieces": 123,
    "by_stage": {"pending_capture": 6, "captured_only": 100, ...},
    "convention_pass_rates": {
      "silhouette-layer-present": {"pass": 7, "fail": 1, "skip": 115},
      ...
    },
    "repo_anomalies": [...]
  },
  "checks_registry": [
    {"id": "silhouette-layer-present", "severity": "required", "description": "..."},
    ...
  ],
  "pieces": {
    "001": { ...PieceState as dict... },
    ...
  }
}
```

`schema_version` increments on incompatible changes; `audit_revision` is a date stamp the dashboard/users can read to know "have I seen this audit's check set?".

Write JSON with `indent=2, sort_keys=False` so the file diffs cleanly across runs.

### Task 11 — Stdout summary (human-readable)

When run without `--quiet`, after writing `state.json`, print:

```
Asset state audit — z-paper-clock
Generated 2026-05-03 14:30 UTC

Pieces by stage:
  pending_capture     6
  captured_only     100
  affinity_started   11
  svg_drafted         8
  svg_layered         3   (silhouette + ≥1 fold/axle layer)
  svg_validated       0
  sidecared           0
  in_viewer           0

Convention pass rates (pieces with SVGs):
  silhouette-layer-present     7/8 pass  (1 fail: 001)
  silhouette-cutaway-id        6/8 pass
  ...

Anomalies:
  - inbox/069.af duplicates source/pieces/069.af
  - inbox/065.png  → should be in source/pieces/ or source/scans-chunks/
  - 1 SVG in source/pieces/ (should be in work/pieces/NNN/)
  - 14 .af files in source/pieces/ (drift; per source/pieces/README.md these belong elsewhere)

Run with `--piece 069` for per-piece detail.
Wrote work/state.json
```

Keep the summary terse. Detail is in `state.json` and surfaceable per-piece via `--piece`.

### Task 12 — `--piece NNN` mode

Print the full PieceState for one piece in YAML-ish prose (or pretty-printed JSON; either works). Don't write `state.json` in this mode (it's a query mode). Useful in chat for "tell me about piece 069".

---

## Verification Checklist

1. `python work/scripts/audit_state.py` runs in <5 seconds on a clean repo and writes `work/state.json`.
2. `work/state.json` is well-formed JSON (`python -c "import json; json.load(open('work/state.json'))"` succeeds).
3. `state.json["summary"]["total_pieces"] == 123`.
4. `state.json["summary"]["by_stage"]["pending_capture"] == 6` (matches WORKPLAN's count of remaining captures).
5. `state.json["pieces"]["069"]` exists and has both `inbox/069.af` and `source/pieces/069.af` listed under `files.affinity` AND a `duplicate-affinity-file` anomaly.
6. `state.json["pieces"]["069"]["svg_analysis"]["primary_svg"]` is the inbox path; `convention_checks` runs.
7. `state.json["pieces"]["067"]["files"]["affinity"]` lists both `067.af` and `067-full.af` (with suffix `full` captured); no anomaly (variant suffix is informational only).
8. `python work/scripts/audit_state.py --piece 069` prints detail for piece 069 and does NOT touch `state.json`.
9. `python work/scripts/audit_state.py --quiet` succeeds with no stdout summary.
10. Running the script never modifies any file outside `work/state.json`. (Spot-check: `git status` after a run shows only `work/state.json` modified.)
11. The script never imports anything outside stdlib + Pillow + lxml.

---

## What NOT to Change

- `pieces.csv` — never written by this script. Read-only.
- `source/pieces/` — never written. Read-only.
- `inbox/` — never written. Read-only.
- `work/pieces/` — never written. Read-only.
- The `piece-scan-ingest` skill at `.claude/skills/piece-scan-ingest/` — different tool, different scope. The audit and the skill might collapse later, but for v0 they stay separate.
- No new CLI dependencies beyond stdlib + Pillow + lxml. No `click`, no `rich`, no progress bars.
- No HTML output. The dashboard is downstream of this and gets its own prompt.

---

## Manual Tests

Run after merge from the repo root:

| Command | Expect |
|---|---|
| `.venv/bin/python work/scripts/audit_state.py` | Summary printed; `work/state.json` written; exit 0 |
| `cat work/state.json \| jq '.summary.by_stage'` | `pending_capture: 6, captured_only: ~100, ...` |
| `cat work/state.json \| jq '.pieces["069"].anomalies'` | Includes `"duplicate-affinity-file"` |
| `cat work/state.json \| jq '.pieces["069"].svg_analysis.layers_present'` | Lists silhouette + whatever else 069 has |
| `.venv/bin/python work/scripts/audit_state.py --piece 067` | Shows piece 067 detail with both 067.af and 067-full.af |
| `.venv/bin/python work/scripts/audit_state.py --piece 110` | Shows piece 110 in `pending_capture` stage |
| `git status` after a run | Only `work/state.json` modified |

If any of these fail, the script shouldn't be merged.
