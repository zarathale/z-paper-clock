---
status: shipped
started: 2026-04-30
shipped: 2026-04-30
owner: Zarathale (Alan)
target: M1-fix-pipeline-trace
---

_Shipped 2026-04-30; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

## What You Are Doing and Why

Two bugs were discovered during the M1 Inkscape review pass. All eleven plate-D piece SVGs are broken: the paths have coordinates far outside the declared viewBox, so every piece renders as a tiny speck in Inkscape. A second bug causes piece 32's crop to cut off the bottom of the piece. Both must be fixed and the pipeline re-run for plate D before the Inkscape hand-edit pass (task 1.5) can proceed.

This prompt was produced in a Cowork session on 2026-04-30 after visual inspection of piece-026.svg, piece-032.svg, and their crop.png files.

---

## Prerequisites — confirm before starting

- `work/pieces/` exists and contains directories `004/` through `092/` for plate D
- `work/pipeline/02-trace.py` and `03-layer-split.py` exist
- `work/pieces.csv` exists
- Native `potrace` is on PATH (`potrace --version` returns 0)
- `.venv/bin/python` exists at repo root

---

## Read These Files First

1. `work/pipeline/01-crop.py` — understand bbox/crop logic
2. `work/pipeline/02-trace.py` — this is where the transform bug lives
3. `work/pipeline/03-layer-split.py` — needs a matching fix to preserve the transform
4. `work/pieces.csv` — piece 32's bbox needs correction
5. `work/SPEC-3D-VIEWER.md` §"Per-piece data model" — confirms SVG layer naming

---

## Target File Structure Changes

```
work/
├── pipeline/
│   ├── 02-trace.py          ← update: capture and preserve potrace transform
│   └── 03-layer-split.py    ← update: wrap layer groups in outer transform group
├── pieces.csv               ← update: fix piece 32 bbox_h
└── pieces/
    └── {004..092}/
        ├── crop.png          ← regenerate for piece 032 only
        ├── bitmap.png        ← regenerate for all plate-D pieces
        ├── raw.svg           ← regenerate for all plate-D pieces
        └── piece-NNN.svg     ← regenerate for all plate-D pieces
```

---

## Numbered Tasks

### Task 1 — Diagnose the exact potrace transform

Before writing any fix, run a diagnostic to confirm the transform format.

```bash
cd ~/Documents/GitHub/z-paper-clock
# Run the trace on just one piece and capture potrace's raw SVG
.venv/bin/python - <<'EOF'
import subprocess, tempfile
from pathlib import Path
from PIL import Image
import numpy as np
from skimage.filters import threshold_otsu

crop = Image.open("work/pieces/026/crop.png").convert("L")
gray = np.array(crop)
h, w = gray.shape
thr = threshold_otsu(gray) - 10
ink = gray < thr
ink_uint8 = (ink.astype(np.uint8) * 255)
from PIL import Image as _I
bmp = _I.fromarray(255 - ink_uint8, mode="L")

import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    bmp.save(str(tmp / "input.bmp"))
    subprocess.run(
        ["potrace", "--svg", "-o", str(tmp / "out.svg"), str(tmp / "input.bmp")],
        check=True, capture_output=True
    )
    print((tmp / "out.svg").read_text()[:2000])
EOF
```

Record the `<svg ...>` root attributes (especially `viewBox`, `width`, `height`) and the `transform` attribute on the first `<g>` element. This is what needs to be captured and preserved in the fix.

Expected output will look something like:
```
<svg ... width="576pt" height="1622pt" viewBox="0 0 576 1622">
<g transform="translate(0.00,1622.00) scale(0.10,-0.10)" fill="#000000" stroke="none">
```

---

### Task 2 — Fix `02-trace.py`: capture and preserve potrace's transform

**Problem:** `_trace_native` extracts `<path>` elements via regex and discards the `<g transform="...">` wrapper that potrace applies. Without the transform, path coordinates (which are in potrace's internal scaled/flipped space) are written to raw.svg with a pixel-space viewBox, making them appear far outside the canvas.

**Fix:** Parse potrace's SVG output with `ElementTree`, extract the `transform` attribute from the containing `<g>`, and return it alongside the path strings. Then include the transform on the path group in raw.svg.

Replace the `_trace_native` function signature and return value, and update `trace_piece` accordingly.

**`_trace_native` — new return type: `tuple[list[str], str]`**

```python
def _trace_native(ink: np.ndarray, w: int, h: int, cfg: dict) -> tuple[list[str], str]:
    """Run native potrace; return (list of SVG <path d=...> strings, transform string)."""
    from PIL import Image as _Image
    import xml.etree.ElementTree as ET

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bmp_path = tmp / "input.bmp"
        svg_path = tmp / "output.svg"

        ink_uint8 = (ink.astype(np.uint8) * 255)
        bmp_img = _Image.fromarray(255 - ink_uint8, mode="L")
        bmp_img.save(str(bmp_path))

        subprocess.run(
            [
                "potrace",
                "--svg",
                f"--turdsize={cfg['turdsize']}",
                f"--alphamax={cfg['alphamax']}",
                f"--opttolerance={cfg['opttolerance']}",
                "-o", str(svg_path),
                str(bmp_path),
            ],
            check=True,
            capture_output=True,
        )

        svg_text = svg_path.read_text()

    # Parse potrace's SVG to extract paths and the group transform
    # Strip XML declaration and DOCTYPE if present (ElementTree can't handle DOCTYPE)
    import re as _re
    clean = _re.sub(r'<\?xml[^>]*\?>', '', svg_text)
    clean = _re.sub(r'<!DOCTYPE[^>]*>', '', clean)
    root = ET.fromstring(clean.strip())

    # Find the <g> with a transform — potrace wraps all paths in one transformed group
    ns_svg = "http://www.w3.org/2000/svg"
    g_el = None
    for child in root:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "g" and child.get("transform"):
            g_el = child
            break
    if g_el is None:
        # Fallback: search deeper
        for el in root.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag == "g" and el.get("transform"):
                g_el = el
                break

    transform = g_el.get("transform", "") if g_el is not None else ""

    # Extract path d-attributes
    import re
    paths = re.findall(r'<path[^>]*/>', svg_text, re.DOTALL)
    if not paths:
        paths = re.findall(r'<path[^>]*>(?:</path>)?', svg_text, re.DOTALL)

    stroke_paths = []
    for el in paths:
        d_match = re.search(r'\bd="([^"]+)"', el)
        if d_match:
            stroke_paths.append(f'    <path d="{d_match.group(1)}"/>')

    return stroke_paths, transform
```

**`_trace_potracer` — also update to return `tuple[list[str], str]`:**

The pure-Python potracer outputs coordinates in pixel space directly (no transform needed), so return an empty transform string:

```python
def _trace_potracer(ink: np.ndarray, w: int, h: int, cfg: dict) -> tuple[list[str], str]:
    # ... existing logic unchanged ...
    return [f"    {p}" for p in parts], ""  # no transform needed
```

**`trace_piece` — use the returned transform in raw.svg:**

```python
    # Trace
    if USE_NATIVE:
        path_strs, transform = _trace_native(ink, w, h, cfg)
    else:
        path_strs, transform = _trace_potracer(ink, w, h, cfg)

    g_attrs = 'fill="none" stroke="#2a2a2a" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"'
    if transform:
        g_open = f'  <g id="potrace-paths" transform="{transform}" {g_attrs}>'
    else:
        g_open = f'  <g id="potrace-paths" {g_attrs}>'

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">',
        '  <rect x="0" y="0" width="100%" height="100%" fill="#fffaf0"/>',
        g_open,
    ]
    lines.extend(path_strs)
    lines.append("  </g>")
    lines.append("</svg>")
```

---

### Task 3 — Fix `03-layer-split.py`: preserve the transform in piece-NNN.svg

**Problem:** `03-layer-split.py` creates one `<g inkscape:label="...">` per layer and writes them directly under the SVG root. The transform from raw.svg's path group is not preserved, so the layer SVGs have the same coordinate-space mismatch.

**Fix:** Read the `transform` attribute from raw.svg's `<g id="potrace-paths">` element and wrap all layer groups in an outer `<g transform="...">` in piece-NNN.svg.

In `split_piece`, after parsing `raw_svg`:

```python
    # Read the transform from raw.svg's path group (written by 02-trace.py)
    potrace_transform = ""
    for el in root.iter():
        if el.get("id") == "potrace-paths" and el.get("transform"):
            potrace_transform = el.get("transform", "")
            break
        # Also check for any g with transform (backwards compat)
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag == "g" and el.get("transform"):
            potrace_transform = el.get("transform", "")
            break
```

Then in the output SVG construction, wrap all layer groups:

```python
    out_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     xmlns:inkscape="{INKSCAPE_NS}"',
        f'     viewBox="{vb}" width="{w_attr}" height="{h_attr}">',
        '  <rect x="0" y="0" width="100%" height="100%" fill="#fffaf0"/>',
    ]

    # Open outer transform group if needed
    if potrace_transform:
        out_lines.append(f'  <g transform="{potrace_transform}">')
        indent = "  "
    else:
        indent = ""

    for layer_name in CANONICAL_LAYERS:
        out_lines.append(
            f'  {indent}<g inkscape:groupmode="layer" inkscape:label="{layer_name}"'
            f' fill="none" stroke="#2a2a2a" stroke-width="1.4"'
            f' stroke-linejoin="round" stroke-linecap="round">'
        )
        for el in layers[layer_name]:
            d = el.get("d", "")
            out_lines.append(f'    {indent}<path d="{d}"/>')
        out_lines.append(f'  {indent}</g>')

    if potrace_transform:
        out_lines.append('  </g>')

    out_lines.append("</svg>")
```

---

### Task 4 — Fix piece 32's crop bbox in `pieces.csv`

Piece 32 (elongated oval tongue, pairs with piece 31) has its bottom cut off by the current bbox. The current bbox is:

```
32,D,auto-trace-clean,0.04,0.490,0.16,0.260
```

Determine the correct `bbox_h` by:
1. Opening the plate-D prepped scan
2. Visually identifying where piece 32's bottom edge falls
3. Updating `pieces.csv` with the corrected `bbox_h` (increase until the full piece fits with a small margin)

Do this by writing a short diagnostic script:
```python
# Check current crop boundaries in pixels
from pathlib import Path
from PIL import Image
img = Image.open("source/scans-prepped/p00x-plate-D-*.jpg")  # adjust glob
W, H = img.size
# Current: x=0.04, y=0.490, w=0.16, h=0.260
print(f"Current crop: ({int(0.04*W)},{int(0.490*H)}) to ({int(0.20*W)},{int(0.750*H)})")
print(f"Plate size: {W}x{H}")
```

Compare to the scan visually. Try increasing `bbox_h` to `0.320` (adding ~23% more height at the bottom) and re-crop to verify the full piece fits. Adjust further if needed. Update `pieces.csv` with the correct value.

---

### Task 5 — Re-run the pipeline for all plate-D pieces

After both fixes are in place, re-run the full pipeline for plate D:

```bash
cd ~/Documents/GitHub/z-paper-clock

# Re-crop (only needed because piece 32 bbox changed;
# re-crops all plate-D pieces — fast, safe to run all)
.venv/bin/python work/pipeline/01-crop.py

# Re-trace (regenerates raw.svg and bitmap.png for all pieces)
.venv/bin/python work/pipeline/02-trace.py

# Re-layer-split (regenerates piece-NNN.svg for all pieces)
.venv/bin/python work/pipeline/03-layer-split.py
```

---

### Task 6 — Validate

```bash
.venv/bin/python work/pipeline/04-validate-sidecars.py
```

Expected: same 4 cross-plate WARNs as before (pieces 4/10 → piece 25, piece 4 → pieces 91/92). No new ERRs.

---

## Verification Checklist

1. `work/pieces/026/raw.svg` — open in a browser or Inkscape; piece 26 (wedge shape) should be clearly visible and correctly sized in the canvas
2. `work/pieces/032/crop.png` — piece 32 (elongated oval tongue) should be fully visible with margin at bottom
3. `work/pieces/032/piece-032.svg` — should render correctly in Inkscape, not as a tiny speck
4. `work/pieces/091/piece-091.svg` and `092/piece-092.svg` — should render as the small square and disc spacers
5. `work/pieces/004/piece-004.svg` — should render as a long column (even if silhouette path is rough — it's hand-trace bucket)
6. Linter passes with only the 4 expected WARNs
7. Open at least pieces 026, 031, 032, 091, 092 in Inkscape to confirm they display at correct size and position

---

## What NOT to Change

- Do not modify `01-crop.py` except to verify piece 32's bbox if the script needs no code changes
- Do not change any sidecar JSON files (`piece-NNN.json`)
- Do not change `pieces.csv` except for piece 32's `bbox_h` (and only after visual verification)
- Do not change `work/SPEC-3D-VIEWER.md` or `CLAUDE.md`
- Do not alter the eight canonical layer names — the viewer keys off them exactly
- Do not modify any files in `source/`

---

## Manual tests (Zarathale runs post-merge)

| Step | Expected |
|---|---|
| Open `work/pieces/026/piece-026.svg` in Inkscape | Wedge shape (piece 26) visible, fills canvas at correct proportions |
| Open `work/pieces/032/piece-032.svg` in Inkscape | Full elongated oval visible, not cut off |
| Open `work/pieces/092/piece-092.svg` in Inkscape | Disc shape visible |
| Open `work/pieces/004/piece-004.svg` in Inkscape | Long column shape visible (auto-trace quality may be rough — that's expected for hand-trace bucket) |
