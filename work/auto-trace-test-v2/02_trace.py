"""
Auto-trace each cropped piece into an SVG.

Approach: trace the line-drawings directly, no silhouette extraction.
This is what a vector-editor workflow would expect -- you get one SVG with
every line as a Bezier path; you then pick / merge / delete in Inkscape or
Affinity Designer to get the final piece silhouette.

Pipeline per piece:
  1. Grayscale, optional downsample
  2. Threshold (dark ink -> 1)
  3. Light morphological close (bridge tiny scanner gaps in lines)
  4. potracer trace -> Bezier paths
  5. Emit SVG with all paths

Also saves the binarized bitmap that was actually fed to Potrace, so the
visual diagnostic shows the input quality.
"""

from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.filters import threshold_otsu
import potrace

ROOT = Path("/sessions/happy-quirky-goldberg/mnt/z-paper-clock/work/auto-trace-test-v2")
CROPS = ROOT / "crops"
BITMAP = ROOT / "bitmap"
SVG = ROOT / "svg"
BITMAP.mkdir(exist_ok=True)
SVG.mkdir(exist_ok=True)

MAX_DIM = 700  # downsample crops longer than this; potracer is pure-Python and slow

# threshold     : "otsu" for auto, or an integer 0-255 to override
# threshold_bias: shift Otsu threshold by this amount (negative = stricter)
# close_iters   : morph-close iterations -- small, just to bridge tiny scanner gaps
# turdsize      : Potrace param: drop paths smaller than this many pixels
# alphamax      : Potrace corner smoothness (1.0 default)
# opttolerance  : Potrace curve-fit tolerance
DEFAULTS = dict(threshold="otsu", threshold_bias=-10, close_iters=1,
                turdsize=10, alphamax=1.0, opttolerance=0.2)
PER_PIECE = {
    # piece-122 has a darker brown border; force a higher threshold to catch it
    "piece-122-face": dict(threshold=200),
}


def trace_piece(name):
    cfg = {**DEFAULTS, **PER_PIECE.get(name, {})}
    src = CROPS / f"{name}.png"
    img = Image.open(src).convert("L")
    if max(img.size) > MAX_DIM:
        scale = MAX_DIM / max(img.size)
        new = (int(img.size[0] * scale), int(img.size[1] * scale))
        img = img.resize(new, Image.LANCZOS)
    gray = np.array(img)
    h, w = gray.shape

    # Threshold: ink -> 1
    if cfg["threshold"] == "otsu":
        thr = threshold_otsu(gray) + cfg.get("threshold_bias", 0)
    else:
        thr = cfg["threshold"]
    ink = gray < thr
    if cfg["close_iters"] > 0:
        ink = ndimage.binary_closing(ink, iterations=cfg["close_iters"])

    # Save the bitmap that Potrace will see (white = ink, black = paper)
    Image.fromarray((ink.astype(np.uint8) * 255)).save(BITMAP / f"{name}.png")

    # Trace -- pass a bool array; potracer's uint8 path thresholds at 127 and
    # would treat 0/1 as all-False
    bmp = potrace.Bitmap(ink.astype(bool))
    path = bmp.trace(turdsize=cfg["turdsize"],
                     alphamax=cfg["alphamax"],
                     opticurve=True,
                     opttolerance=cfg["opttolerance"])

    # Build SVG: every Potrace curve becomes one <path>, rendered as a thin
    # stroke (no fill). potracer inverts the input internally so its first
    # curve is the canvas perimeter; with even-odd fill that washes everything
    # out. Stroke-only rendering avoids that and is more diagnostic anyway.
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">',
        '  <rect x="0" y="0" width="100%" height="100%" fill="#fffaf0"/>',
        '  <g fill="none" stroke="#2a2a2a" stroke-width="1.4" '
        'stroke-linejoin="round" stroke-linecap="round">',
    ]
    n_curves = 0
    n_segs = 0
    for curve in path:
        n_curves += 1
        d = []
        sp = curve.start_point
        d.append(f"M {sp.x:.2f} {sp.y:.2f}")
        for seg in curve:
            n_segs += 1
            ep = seg.end_point
            if seg.is_corner:
                c = seg.c
                d.append(f"L {c.x:.2f} {c.y:.2f}")
                d.append(f"L {ep.x:.2f} {ep.y:.2f}")
            else:
                c1, c2 = seg.c1, seg.c2
                d.append(f"C {c1.x:.2f} {c1.y:.2f} "
                         f"{c2.x:.2f} {c2.y:.2f} {ep.x:.2f} {ep.y:.2f}")
        d.append("Z")
        parts.append(f'    <path d="{" ".join(d)}"/>')
    parts.append('  </g>')
    parts.append('</svg>')
    (SVG / f"{name}.svg").write_text("\n".join(parts))

    print(f"  {name:18s}  src {w}x{h}  thr={thr:>3}  "
          f"ink-pixels {int(ink.sum()):,} ({ink.mean()*100:.1f}%)  "
          f"curves {n_curves}  segments {n_segs}")
    return n_curves, n_segs


print(f"Tracing {len(list(CROPS.glob('*.png')))} pieces...\n")
for crop in sorted(CROPS.glob("*.png")):
    trace_piece(crop.stem)
print("\nDone.")
