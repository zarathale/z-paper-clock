---
status: shipped
started: 2026-04-30
shipped: 2026-04-30
owner: Zarathale (Alan)
target: M1-pipeline-plate-d
---

_Shipped 2026-04-30; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

# CODE_PROMPT — M1: Pipeline end-to-end on plate D

## What You Are Doing and Why

Build the per-piece authoring pipeline (`01-crop.py` through `04-validate-sidecars.py`, plus a `Makefile`) and run it end-to-end on plate D's 11 pieces. Plate D is the simplest plate; getting the pipeline working there proves the spec is buildable and produces the first 11 piece directories under `work/pieces/`. M2 then runs the same pipeline across the rest of the plates.

You are the first Code session in the build. The design is settled (see `work/SPEC-3D-VIEWER.md`), the roadmap task list is in `ROADMAP.md`, the auto-trace approach is verified (see `work/auto-trace-test-v2/02_trace.py`), and the bbox index for plate D is already populated in `work/pieces.csv` by the prior Cowork session (`sessions/2026-04-30-1330_cowork_M1-prep.md`). Your job is the executable layer: scripts that read the csv, crop, trace, layer-split, and validate, all under `work/pipeline/`.

## Prerequisites — confirm before starting

- `source/scans-prepped/p00x-plate-D-pieces-4-10-18-19-26-29-32-91-92.jpg` exists (2400×3120 portrait).
- `work/pieces.csv` exists with header `id,plate,bucket,bbox_x,bbox_y,bbox_w,bbox_h` and 11 plate-D rows.
- Python 3.10+ with `Pillow`, `scipy`, `scikit-image`, `numpy`, `lxml` available.
- `potrace` native binary on PATH (`which potrace`) **or** Python `potracer` package as fallback. SPEC §"Tech stack" notes native potrace is 50–100× faster; install it if not present (`brew install potrace` on mac).
- `work/auto-trace-test-v2/02_trace.py` is the working reference for the trace step — read it before writing `02-trace.py`.
- Branch off `main` to `claude/M1-pipeline-plate-d` before any edits.

## Read These Files First

1. `work/SPEC-3D-VIEWER.md` — especially §"Per-piece data model", §"Authoring pipeline", §"File and folder layout".
2. `ROADMAP.md` — §"M1 — Pipeline end-to-end on plate D" task table; this prompt expands every Code-owned row.
3. `CLAUDE.md` — §"Git Workflow" (branch / PR rules), §"Ending a Session" (session note + commit + PR steps), §"File Naming Conventions".
4. `work/auto-trace-test-v2/01_crop.py` and `02_trace.py` — the working reference for tasks 1.2 and 1.3.
5. `source/transcriptions/embedded-labels.md` §"Panel D" — context for what each piece looks like and what labels it carries.
6. `work/pieces.csv` — the input you'll be reading.

## Target File Structure Changes

```
work/
├── pieces.csv                    ← exists (plate-D rows from Cowork prep session)
├── pipeline/                     ← NEW
│   ├── 01-crop.py                ← NEW: reads pieces.csv, crops from prepped scan
│   ├── 02-trace.py               ← NEW: native potrace (potracer fallback)
│   ├── 03-layer-split.py         ← NEW: classify paths into canonical SVG layers
│   ├── 04-validate-sidecars.py   ← NEW: linter for piece-NNN.json sidecars
│   └── Makefile                  ← NEW: crop / trace / layer-split / validate / all targets
└── pieces/                       ← NEW; populated by pipeline runs
    ├── 004/
    │   ├── crop.png              ← from 01-crop
    │   ├── raw.svg               ← from 02-trace (single-layer)
    │   └── piece-004.svg         ← from 03-layer-split (layered)
    ├── 010/
    ├── 018/
    ├── 019/
    ├── 026/
    ├── 029/
    ├── 030/
    ├── 031/
    ├── 032/
    ├── 091/
    └── 092/
```

`piece-NNN.json` sidecars are not produced by the pipeline; they're authored by hand in the next Cowork session (M1 task 1.6) and live alongside the SVG. The validate-sidecars script will lint them once they exist.

## Numbered Tasks

### Task 1.2 — Code `work/pipeline/01-crop.py`

**Reads:** `work/pieces.csv` and the prepped plate scans under `source/scans-prepped/`.
**Writes:** `work/pieces/NNN/crop.png` for every row in `pieces.csv`.

Algorithm:
1. Parse `work/pieces.csv` with `csv.DictReader`.
2. For each row: resolve plate letter → prepped scan path. The scans live under `source/scans-prepped/` with names like `p00x-plate-D-pieces-4-10-18-19-26-29-32-91-92.jpg`. Use `glob.glob(f"source/scans-prepped/p00x-plate-{plate}-*.jpg")` and assert exactly one match per plate.
3. Open the scan with PIL; read `bbox_x, bbox_y, bbox_w, bbox_h` as floats in `[0,1]` (these are fractions of image dimensions, not pixels — matching the convention from `auto-trace-test-v2/01_crop.py`). Compute pixel coords: `x0 = round(bbox_x * W); y0 = round(bbox_y * H); x1 = round((bbox_x+bbox_w) * W); y1 = round((bbox_y+bbox_h) * H)`.
4. Crop and save as PNG (lossless): `work/pieces/{id:03d}/crop.png`. Three-digit zero-padded id per `CLAUDE.md` §"File Naming Conventions" (e.g., `004`, `010`, `091`).
5. Print one summary line per piece: `piece NNN  plate D  bbox (x0,y0)-(x1,y1)  -> crop.png  WxH`.

Make `work/pieces/{id:03d}/` directories on the fly (`mkdir(parents=True, exist_ok=True)`).

A note on units: the `bbox_*` columns are **fractions in [0,1]**, not pixels. This is robust to rescans and matches the v2 reference. Document this at the top of the script in a docstring; the schema header in `pieces.csv` does not encode units explicitly.

### Task 1.3 — Code `work/pipeline/02-trace.py`

**Reads:** every `work/pieces/NNN/crop.png`.
**Writes:** `work/pieces/NNN/raw.svg` — single-layer SVG with all auto-traced paths as thin black strokes, no fill.

Use the v2 reference (`work/auto-trace-test-v2/02_trace.py`) as the starting point. Carry over: grayscale → optional downsample → Otsu threshold (with `-10` bias) → light morphological close → trace.

Two changes from v2:
1. **Prefer native potrace.** Try `subprocess.run(["potrace", "--version"])` once at startup. If it succeeds, use the native binary (write the closed bitmap to a temp `.pgm` or `.bmp`, run `potrace -s -o output.svg input.bmp`). If it fails, fall back to `import potrace as potracer` (the pure-Python `potracer` package; v2 used it). Print which path is in use at startup.
2. **No downsample for production.** v2 used `MAX_DIM = 700` because pure-Python potracer is slow. With native potrace, drop the downsample (or raise it to `MAX_DIM = 2400`). The full-resolution prepped scans give better trace quality.

Per-piece overrides (like v2's `PER_PIECE = {"piece-122-face": dict(threshold=200)}`): keep the override mechanism but plate D shouldn't need any. If you find a piece needs a non-default threshold during your run, document it in the script's `PER_PIECE` dict with a comment explaining why.

Output SVG format: keep v2's stroke-only-no-fill convention (`fill="none" stroke="#2a2a2a"`). Every potrace curve becomes one `<path>`. The viewBox matches the crop's pixel dimensions.

Also save the binarized bitmap as `work/pieces/NNN/bitmap.png` for diagnostic purposes (per v2).

### Task 1.4 — Code `work/pipeline/03-layer-split.py`

**Reads:** every `work/pieces/NNN/raw.svg`.
**Writes:** `work/pieces/NNN/piece-NNN.svg` — layered SVG with named groups per SPEC §"Per-piece data model".

The eight canonical layers are: `silhouette`, `cutouts`, `folds-valley`, `folds-mountain`, `axles`, `glue-zones`, `labels`, `marks-other`. The auto-trace produces undifferentiated paths; this script classifies them. Heuristics, in order:

1. **Closed-path detection.** A path is closed if its `d` attribute ends with `Z` AND its bounding box has non-trivial area (drop turdsize-equivalent micro-paths if any survive).
2. **Silhouette.** The single largest closed path by bounding-box area is the silhouette. Mark with `inkscape:label="silhouette"`.
3. **Cutouts.** Closed paths whose bounding box lies fully inside the silhouette's bounding box AND whose area is >5% of the silhouette → cutouts. Mark with `inkscape:label="cutouts"`. (5% threshold filters out small text-glyph closed loops like `o`, `e`, `8`.)
4. **Labels.** Remaining closed paths whose area is <5% of the silhouette → labels. Mark with `inkscape:label="labels"`.
5. **Open paths.** Anything that doesn't end with `Z` → goes to `marks-other` for now. (Distinguishing valley folds vs mountain folds vs glue-zone hatching vs construction lines from auto-trace output is genuinely hard — the SPEC budgets the human Inkscape pass for that, M1 task 1.5.)
6. **Axles.** Skip in this pass — axles are short pairs of crossing line segments (`+` glyphs). They'll get pulled out of `marks-other` by the human Inkscape pass.
7. **Glue-zones.** Skip in this pass — same reason. Hatched fill rectangles are visually obvious to a human; classifying them programmatically from auto-trace output is brittle.

Output SVG structure:
```xml
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     viewBox="..." width="..." height="...">
  <g inkscape:groupmode="layer" inkscape:label="silhouette"> ... </g>
  <g inkscape:groupmode="layer" inkscape:label="cutouts"> ... </g>
  <g inkscape:groupmode="layer" inkscape:label="folds-valley"></g>
  <g inkscape:groupmode="layer" inkscape:label="folds-mountain"></g>
  <g inkscape:groupmode="layer" inkscape:label="axles"></g>
  <g inkscape:groupmode="layer" inkscape:label="glue-zones"></g>
  <g inkscape:groupmode="layer" inkscape:label="labels"> ... </g>
  <g inkscape:groupmode="layer" inkscape:label="marks-other"> ... </g>
</svg>
```

All eight layer groups must be present even if empty — keeps Inkscape's layer panel predictable. Strokes should keep the v2 styling (thin black, no fill); the viewer's decal-baking step handles final visual styling.

Use `lxml` for XML manipulation (or stdlib `xml.etree.ElementTree` if you prefer — but lxml's pretty-print is nicer). Preserve path coordinates exactly; this is a regrouping pass, not a transform pass.

### Task 1.7 — Code `work/pipeline/04-validate-sidecars.py`

**Reads:** every `work/pieces/NNN/piece-NNN.json` (these don't exist yet — they'll be authored by hand in the M1 follow-up Cowork session, task 1.6).
**Writes:** stdout report; exit code 0 if all pass, non-zero otherwise.

Lint rules per SPEC §"Authoring pipeline" step 6:

1. **JSON parses.** Each `piece-NNN.json` is valid JSON.
2. **Required fields present.** Every sidecar has: `id` (int), `plate` (str), `name` (str), `role` (str), `material` (one of `paper`, `cardboard-1mm`, `wire`, `knitting-needle-2mm`), `extrudeMm` (number), `connections` (array), `folds` (object with `valley` and `mountain` arrays), `axles` (array), `introducedInStep` (str), `figureRefs` (array), `notes` (str).
3. **`id` matches filename.** `piece-091.json` has `"id": 91`, etc.
4. **Connections are reciprocal.** For every `{"tab": "x", "to": N, "atTab": "y"}` in piece A's `connections`, piece N's `connections` must contain a matching entry. (Skip this check if the referenced piece's sidecar doesn't exist yet — this is M1, only 11 pieces exist; cross-references to pieces in other plates won't be reciprocable until M2.)
5. **Axles are reciprocal.** Every `axle.id` referenced in a sidecar must appear in at least one other sidecar (same caveat as connections: skip if referenced piece doesn't exist yet).
6. **`plate` matches `pieces.csv`.** Cross-check the JSON's `plate` field against the `plate` column for the same `id` in `pieces.csv`.

Report format:
```
piece-004.json  OK
piece-010.json  OK
piece-018.json  ERROR: missing required field "introducedInStep"
piece-091.json  WARN: connection to piece 88 not reciprocable (piece 088 sidecar not found)
...
Summary: 9 pass, 1 fail, 1 warn.
```

Exit non-zero if any ERROR; warnings don't fail the lint.

The SPEC also calls for a check that "silhouette is one closed path; folds are open paths" against the layered SVG — that's a separate concern. **Skip the SVG-shape lint for M1.** If time permits, add it in M2 when sidecars across plates exist and the SVG-vs-sidecar consistency story matters more.

### Task 1.8 — Run `04-validate-sidecars.py`; iterate until clean

The 11 sidecars don't exist when this Code session runs (they're a Cowork follow-up). For task 1.8, **run the linter against an empty `work/pieces/*/` set and confirm it exits gracefully with a "no sidecars found" report.** That validates the script's empty-input handling.

Optionally: if the M1 follow-up Cowork session has run before this Code session (check `git log --oneline -- work/pieces/`), run the linter against the actual sidecars and iterate. But don't block the Code session waiting for sidecars — that's an explicit handoff to a separate Cowork session.

### Task 1.9 — Author `work/pipeline/Makefile`

Targets:
- `make crop` → runs `python 01-crop.py`
- `make trace` → runs `python 02-trace.py` (depends on `crop`)
- `make layers` → runs `python 03-layer-split.py` (depends on `trace`)
- `make validate` → runs `python 04-validate-sidecars.py`
- `make pieces` → runs all four in order: `crop`, `trace`, `layers`, `validate`
- `make clean` → removes `work/pieces/*/crop.png`, `*/raw.svg`, `*/bitmap.png`, `*/piece-*.svg`. Does NOT remove sidecars (`piece-*.json`) — those are hand-authored.

Use simple recipe lines; no fancy GNU Make patterns. Each target is a phony target. Working directory inside the recipes is `work/pipeline/`.

Add a `.PHONY: crop trace layers validate pieces clean` line at the top.

## Verification Checklist

After implementation, run these to confirm M1 ships:

1. `cd work/pipeline && make pieces` runs end-to-end with no Python tracebacks.
2. `ls work/pieces/` shows exactly 11 directories: `004 010 018 019 026 029 030 031 032 091 092`.
3. Each directory contains `crop.png`, `bitmap.png`, `raw.svg`, and `piece-NNN.svg`.
4. Spot-check piece 092 (a known-clean auto-trace from the v2 test): open `work/pieces/092/piece-092.svg` in Inkscape. The silhouette layer should contain one closed path (the disc); the labels layer should contain the small `a`, `b`, and `92` text shapes; the marks-other layer should contain the `+` axle marker fragments.
5. Spot-check piece 091 (an accordion piece per the roadmap, but actually a small square per the embedded labels): open `work/pieces/091/piece-091.svg`. The silhouette should be one rectangle; the marks-other layer should contain the `+` center marker fragments and the surrounding glue-instruction text fragments (the latter are arguably labels, but the heuristic puts them in marks-other since they're open paths).
6. `make validate` exits 0 and reports "no sidecars found" cleanly (sidecars don't exist yet — that's expected for this session).
7. `make clean` removes the pipeline outputs but leaves any sidecars untouched (verify by creating a stub `work/pieces/004/piece-004.json`, running `make clean`, confirming the JSON survives).
8. `git status` shows the four new scripts, the Makefile, and 11 piece directories with their files. No edits to anything outside `work/pipeline/` and `work/pieces/`.

## What NOT to Change

- **Don't touch the viewer.** `work/viewer/` is M3 territory; it doesn't even exist as a directory yet. Don't create it.
- **Don't author sidecars (`piece-NNN.json`).** That's M1 task 1.6, a Cowork follow-up. The validate script just needs to handle their eventual presence.
- **Don't extend `pieces.csv` beyond plate D.** M2 task 2.1 is the bucket-triage and bbox pass for plates A–C and E–M. Adding rows here muddies M2's audit.
- **Don't refactor the v2 test scripts.** `work/auto-trace-test-v2/01_crop.py` and `02_trace.py` are kept as audit trail per CLAUDE.md §"Repo Structure" (the `auto-trace-test/` and `auto-trace-test-v2/` entries are existing). Read them, lift logic into the production scripts, but leave the originals in place.
- **Don't write the gear-ratio validator.** That's M2 task 2.6.
- **Don't bump a version number.** M1 is pipeline-only; the viewer doesn't exist yet so there's no `package.json` to bump. CLAUDE.md §"Versioning Policy" says "For pipeline-only work that doesn't touch the viewer (M1, M2 milestones), no version bump."
- **Don't create a CHANGELOG.** That's a follow-up when M3 first ships the viewer.

## Manual tests (after merge, on Zarathale's mac)

| Pre-condition | Action | Expected post-condition |
|---|---|---|
| Fresh `main` checkout | `cd work/pipeline && make clean && make pieces` | 11 piece directories under `work/pieces/`, each with `crop.png`, `bitmap.png`, `raw.svg`, `piece-NNN.svg`. No errors on stdout. |
| Pipeline ran cleanly | Open `work/pieces/092/piece-092.svg` in Inkscape | Layer panel shows all eight canonical layers; silhouette layer is the disc; labels layer has the `a`/`b`/`92` text glyphs |
| Native potrace installed | Re-run `make trace` | Startup line says "using native potrace" (not "falling back to potracer") |
| Stub sidecar present at `work/pieces/004/piece-004.json` with `{"id": 4, "plate": "X", ...}` (deliberate plate mismatch) | `make validate` | Exits non-zero; reports `piece-004.json  ERROR: plate "X" does not match pieces.csv plate "D"` |

## End of session

Per `CLAUDE.md` §"Ending a Session, Code sessions":

1. No version bump — M1 is pipeline-only, no viewer yet.
2. No CHANGELOG entry — viewer's CHANGELOG doesn't exist; create when M3 first ships.
3. Add a session note: `sessions/YYYY-MM-DD-HHMM_code_M1-pipeline-plate-d.md` with branch name and commit SHA(s).
4. Commit to `claude/M1-pipeline-plate-d` and push.
5. Open the PR via `gh pr create --base main --head claude/M1-pipeline-plate-d --title "M1: pipeline end-to-end on plate D" --body-file <prepared-body.md>`. Return the PR URL in your final chat message.
6. Flip this prompt's front matter to `status: shipped` and add `shipped: YYYY-MM-DD`.
7. Mirror the M1 row in `CLAUDE.md`'s "Where We Are" status table (likely from "⏳ Pending Code session" to "✅ Shipped — see PR #N"). Update the matching rows in `ROADMAP.md` task table 1.2–1.4 and 1.7–1.9 to `done` with `see sessions/YYYY-MM-DD-HHMM_…`. Tasks 1.1, 1.5, and 1.6 stay where they are — Cowork-owned, not your concern this session.
