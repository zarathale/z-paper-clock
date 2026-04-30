"""
Trace each work/pieces/NNN/crop.png into a single-layer SVG (raw.svg).

Pipeline per piece:
  1. Grayscale
  2. Otsu threshold with -10 bias (stricter — catches ink without over-capturing noise)
  3. Light morphological close (bridges tiny scanner gaps in lines)
  4. Trace with native potrace if available, pure-Python potracer as fallback
  5. Emit raw.svg: all paths as thin black strokes, no fill

Also saves bitmap.png (the binarized image fed to the tracer) for diagnostics.

potrace vs. potracer: native potrace is 50-100x faster and produces slightly
cleaner curves. The fallback (potracer package) is used only if the native
binary is not on PATH.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.filters import threshold_otsu

REPO = Path(__file__).resolve().parents[2]
PIECES_DIR = REPO / "work" / "pieces"

DEFAULTS = dict(
    threshold="otsu",
    threshold_bias=-10,
    close_iters=1,
    turdsize=10,
    alphamax=1.0,
    opttolerance=0.2,
)
# Per-piece threshold overrides. Add an entry if a piece needs non-default settings.
PER_PIECE: dict[str, dict] = {}


def _check_native_potrace() -> bool:
    try:
        result = subprocess.run(
            ["potrace", "--version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


USE_NATIVE = _check_native_potrace()
if USE_NATIVE:
    print("using native potrace\n")
else:
    try:
        import potrace as potracer_module
        print("native potrace not found — falling back to pure-Python potracer\n")
    except ImportError:
        print(
            "ERROR: neither native potrace nor the potracer Python package is available.\n"
            "Install one:\n"
            "  brew install potrace      # native (fast)\n"
            "  pip install potracer      # pure-Python fallback\n",
            file=sys.stderr,
        )
        sys.exit(1)


def _trace_native(ink: np.ndarray, w: int, h: int, cfg: dict) -> list[str]:
    """Run native potrace on a bool array; return list of SVG <path d=...> strings."""
    from PIL import Image as _Image

    # potrace reads PBM (1-bit); write a temp file
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        bmp_path = tmp / "input.bmp"
        svg_path = tmp / "output.svg"

        # Convert bool array to a 1-bit BMP (black ink on white paper)
        # potrace treats black pixels as ink
        ink_uint8 = (ink.astype(np.uint8) * 255)
        # invert: ink=True should be black (0) in the BMP for potrace
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

    # Extract <path> elements from potrace's SVG output
    import re
    paths = re.findall(r'<path[^/]*/>', svg_text, re.DOTALL)
    if not paths:
        # potrace sometimes uses <path ...></path>
        paths = re.findall(r'<path[^>]*>(?:</path>)?', svg_text, re.DOTALL)
    return paths


def _trace_potracer(ink: np.ndarray, w: int, h: int, cfg: dict) -> list[str]:
    """Trace using pure-Python potracer; return list of SVG path d-attribute strings."""
    import potrace as pt

    bmp = pt.Bitmap(ink.astype(bool))
    path = bmp.trace(
        turdsize=cfg["turdsize"],
        alphamax=cfg["alphamax"],
        opticurve=True,
        opttolerance=cfg["opttolerance"],
    )
    parts = []
    for curve in path:
        d = []
        sp = curve.start_point
        d.append(f"M {sp.x:.2f} {sp.y:.2f}")
        for seg in curve:
            ep = seg.end_point
            if seg.is_corner:
                c = seg.c
                d.append(f"L {c.x:.2f} {c.y:.2f}")
                d.append(f"L {ep.x:.2f} {ep.y:.2f}")
            else:
                c1, c2 = seg.c1, seg.c2
                d.append(
                    f"C {c1.x:.2f} {c1.y:.2f} "
                    f"{c2.x:.2f} {c2.y:.2f} {ep.x:.2f} {ep.y:.2f}"
                )
        d.append("Z")
        parts.append(f'<path d="{" ".join(d)}"/>')
    return parts


def trace_piece(piece_dir: Path) -> None:
    name = piece_dir.name  # e.g. "004"
    cfg = {**DEFAULTS, **PER_PIECE.get(name, {})}

    src = piece_dir / "crop.png"
    if not src.exists():
        print(f"  {name}  SKIP (no crop.png)")
        return

    img = Image.open(src).convert("L")
    gray = np.array(img)
    h, w = gray.shape

    if cfg["threshold"] == "otsu":
        thr = threshold_otsu(gray) + cfg.get("threshold_bias", 0)
    else:
        thr = cfg["threshold"]

    ink = gray < thr

    if cfg["close_iters"] > 0:
        ink = ndimage.binary_closing(ink, iterations=cfg["close_iters"])

    # Save diagnostic bitmap (white=ink, black=paper — matching v2 convention)
    Image.fromarray((ink.astype(np.uint8) * 255)).save(piece_dir / "bitmap.png")

    # Trace
    if USE_NATIVE:
        path_elements = _trace_native(ink, w, h, cfg)
        # Rebuild as stroke-only, no fill — potrace native outputs filled black paths
        import re
        stroke_paths = []
        for el in path_elements:
            d_match = re.search(r'\bd="([^"]+)"', el)
            if d_match:
                stroke_paths.append(f'    <path d="{d_match.group(1)}"/>')
        path_strs = stroke_paths
    else:
        path_strs = [f"    {p}" for p in _trace_potracer(ink, w, h, cfg)]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">',
        '  <rect x="0" y="0" width="100%" height="100%" fill="#fffaf0"/>',
        '  <g fill="none" stroke="#2a2a2a" stroke-width="1.4" '
        'stroke-linejoin="round" stroke-linecap="round">',
    ]
    lines.extend(path_strs)
    lines.append("  </g>")
    lines.append("</svg>")

    (piece_dir / "raw.svg").write_text("\n".join(lines))

    print(
        f"  piece {name}  {w}x{h}  thr={thr:.0f}  "
        f"ink {ink.mean()*100:.1f}%  paths {len(path_strs)}"
    )


def main():
    dirs = sorted(p for p in PIECES_DIR.iterdir() if p.is_dir())
    if not dirs:
        print("No piece directories found under work/pieces/. Run 01-crop.py first.")
        sys.exit(1)

    print(f"Tracing {len(dirs)} pieces...\n")
    for d in dirs:
        trace_piece(d)
    print(f"\nDone. raw.svg and bitmap.png written for each piece.")


if __name__ == "__main__":
    main()
