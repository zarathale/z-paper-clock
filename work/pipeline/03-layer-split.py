"""
Classify paths in each work/pieces/NNN/raw.svg into canonical layers,
writing work/pieces/NNN/piece-NNN.svg.

Layer classification heuristics (in order of precedence):
  1. Closed paths (d ends with Z, non-trivial area):
     - Largest by bounding-box area         -> silhouette
     - Inside silhouette bbox, area >5% of silhouette -> cutouts
     - All other small closed paths         -> labels
  2. Open paths (d does not end with Z)     -> marks-other

Valley folds, mountain folds, glue-zones, and axles require human judgment
from the Inkscape pass (M1 task 1.5) — those layers are emitted empty here
and filled in during the hand-edit step.

All eight canonical layer groups are always present in the output SVG so
Inkscape's layer panel stays predictable.
"""

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
PIECES_DIR = REPO / "work" / "pieces"

INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SVG_NS = "http://www.w3.org/2000/svg"

ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)

CANONICAL_LAYERS = [
    "silhouette",
    "cutouts",
    "folds-valley",
    "folds-mountain",
    "axles",
    "glue-zones",
    "labels",
    "marks-other",
]


def _path_is_closed(d: str) -> bool:
    return bool(re.search(r"[Zz]\s*$", d.strip()))


def _path_bbox(d: str) -> tuple[float, float, float, float]:
    """Return (x_min, y_min, x_max, y_max) from M/L/C coordinates in a path d-string.
    Approximation: samples all numeric coordinate pairs. Good enough for area comparison.
    """
    nums = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", d)]
    if len(nums) < 2:
        return (0.0, 0.0, 0.0, 0.0)
    xs = nums[0::2]
    ys = nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def _bbox_area(bbox: tuple[float, float, float, float]) -> float:
    x0, y0, x1, y1 = bbox
    w = x1 - x0
    h = y1 - y0
    return w * h if w > 0 and h > 0 else 0.0


def _bbox_contains(outer: tuple, inner: tuple) -> bool:
    return (
        inner[0] >= outer[0] - 1
        and inner[1] >= outer[1] - 1
        and inner[2] <= outer[2] + 1
        and inner[3] <= outer[3] + 1
    )


def split_piece(piece_dir: Path) -> None:
    name = piece_dir.name  # e.g. "004"
    raw_svg = piece_dir / "raw.svg"
    if not raw_svg.exists():
        print(f"  {name}  SKIP (no raw.svg)")
        return

    tree = ET.parse(raw_svg)
    root = tree.getroot()

    # Collect all <path> elements from any group
    all_paths: list[ET.Element] = root.findall(f".//{{{SVG_NS}}}path")
    if not all_paths:
        # Try without namespace (some SVGs may omit it)
        all_paths = root.findall(".//path")

    # Native potrace SVG may wrap paths differently; collect from the whole tree
    if not all_paths:
        all_paths = [el for el in root.iter() if el.tag.endswith("path")]

    # Classify paths
    closed: list[tuple[ET.Element, str, tuple, float]] = []  # (el, d, bbox, area)
    open_paths: list[ET.Element] = []

    for el in all_paths:
        d = el.get("d", "")
        if not d:
            continue
        if _path_is_closed(d):
            bbox = _path_bbox(d)
            area = _bbox_area(bbox)
            if area > 4:  # drop micro-paths (turdsize equivalent)
                closed.append((el, d, bbox, area))
        else:
            open_paths.append(el)

    # Sort closed paths by area descending
    closed.sort(key=lambda t: t[3], reverse=True)

    layers: dict[str, list[ET.Element]] = {layer: [] for layer in CANONICAL_LAYERS}

    if closed:
        silhouette_el, silhouette_d, silhouette_bbox, silhouette_area = closed[0]
        s = ET.Element("path")
        s.attrib.update({k: v for k, v in silhouette_el.attrib.items()})
        layers["silhouette"].append(s)

        for el, d, bbox, area in closed[1:]:
            p = ET.Element("path")
            p.attrib.update({k: v for k, v in el.attrib.items()})
            if (
                _bbox_contains(silhouette_bbox, bbox)
                and silhouette_area > 0
                and (area / silhouette_area) > 0.05
            ):
                layers["cutouts"].append(p)
            else:
                layers["labels"].append(p)

    for el in open_paths:
        p = ET.Element("path")
        p.attrib.update({k: v for k, v in el.attrib.items()})
        layers["marks-other"].append(p)

    # Build output SVG
    vb = root.get("viewBox", "")
    w_attr = root.get("width", "")
    h_attr = root.get("height", "")

    out_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     xmlns:inkscape="{INKSCAPE_NS}"',
        f'     viewBox="{vb}" width="{w_attr}" height="{h_attr}">',
        '  <rect x="0" y="0" width="100%" height="100%" fill="#fffaf0"/>',
    ]

    for layer_name in CANONICAL_LAYERS:
        out_lines.append(
            f'  <g inkscape:groupmode="layer" inkscape:label="{layer_name}"'
            f' fill="none" stroke="#2a2a2a" stroke-width="1.4"'
            f' stroke-linejoin="round" stroke-linecap="round">'
        )
        for el in layers[layer_name]:
            d = el.get("d", "")
            out_lines.append(f'    <path d="{d}"/>')
        out_lines.append("  </g>")

    out_lines.append("</svg>")

    out_path = piece_dir / f"piece-{name}.svg"
    out_path.write_text("\n".join(out_lines))

    counts = {k: len(v) for k, v in layers.items() if v}
    counts_str = "  ".join(f"{k}:{n}" for k, n in counts.items())
    print(f"  piece {name}  {len(all_paths)} paths -> {counts_str}")


def main():
    dirs = sorted(p for p in PIECES_DIR.iterdir() if p.is_dir())
    if not dirs:
        print("No piece directories found under work/pieces/. Run 01-crop.py first.")
        sys.exit(1)

    print(f"Layer-splitting {len(dirs)} pieces...\n")
    for d in dirs:
        split_piece(d)
    print(f"\nDone. piece-NNN.svg written for each piece.")


if __name__ == "__main__":
    main()
