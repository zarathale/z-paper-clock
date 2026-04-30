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


def _trace_native(ink: np.ndarray, w: int, h: int, cfg: dict) -> tuple[list[str], str]:
    """Run native potrace; return (list of SVG <path d=...> strings, transform string).

    potrace outputs paths in a flipped/scaled coordinate space and wraps them in
    a <g transform="translate(0,H) scale(0.1,-0.1)"> group. We capture that
    transform and propagate it so the paths render correctly in our pixel-space viewBox.
    """
    import re as _re
    import xml.etree.ElementTree as ET
    from PIL import Image as _Image

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

    # Parse potrace's SVG to extract paths and the group transform.
    # Strip XML declaration and DOCTYPE — ElementTree cannot handle DOCTYPE.
    clean = _re.sub(r'<\?xml[^>]*\?>', '', svg_text)
    clean = _re.sub(r'<!DOCTYPE[^>]*>', '', clean)
    root = ET.fromstring(clean.strip())

    # potrace wraps all paths in a single transformed <g>
    g_el = None
    for child in root:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "g" and child.get("transform"):
            g_el = child
            break
    if g_el is None:
        for el in root.iter():
            tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
            if tag == "g" and el.get("transform"):
                g_el = el
                break

    transform = g_el.get("transform", "") if g_el is not None else ""

    import re
    paths = re.findall(r'<path[^/]*/>', svg_text, re.DOTALL)
    if not paths:
        paths = re.findall(r'<path[^>]*>(?:</path>)?', svg_text, re.DOTALL)

    stroke_paths = []
    for el in paths:
        d_match = re.search(r'\bd="([^"]+)"', el)
        if d_match:
            stroke_paths.append(f'    <path d="{d_match.group(1)}"/>')

    return stroke_paths, transform


def _trace_potracer(ink: np.ndarray, w: int, h: int, cfg: dict) -> tuple[list[str], str]:
    """Trace using pure-Python potracer; return (path strings, empty transform).

    potracer outputs coordinates directly in pixel space, so no transform is needed.
    """
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
    return [f"    {p}" for p in parts], ""


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
