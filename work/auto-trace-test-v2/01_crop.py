"""
Crop the five test pieces from their plate scans.

Bounding boxes are expressed as proportions (0..1) of the source image so they
work regardless of exact pixel dimensions. Adjust if a crop is too tight/loose.
"""

from pathlib import Path
from PIL import Image

REPO = Path("/sessions/happy-quirky-goldberg/mnt/z-paper-clock")
SCANS = REPO / "source" / "scans-prepped"
OUT = REPO / "work" / "auto-trace-test-v2" / "crops"
OUT.mkdir(parents=True, exist_ok=True)

# (piece_id, source_filename, (x0_frac, y0_frac, x1_frac, y1_frac), notes)
PIECES = [
    ("piece-001",
     "p00x-plate-A-pieces-1-2-6-7-110.jpg",
     (0.07, 0.015, 0.24, 0.985),
     "long thin frame strip, leftmost on plate A; full-height channel"),
    ("piece-033",
     "p00x-plate-G-spread-flat-pieces-33-36-50-57.jpg",
     (0.07, 0.06, 0.40, 0.62),
     "triangular motor wheel rim with toothed arcs on three sides; plate G"),
    ("piece-092",
     "p00x-plate-D-pieces-4-10-18-19-26-29-32-91-92.jpg",
     (0.18, 0.52, 0.42, 0.73),
     "disc piece 92; plate D, lower-left"),
    ("piece-099",
     "p00x-plate-H-spread-flat-pieces-67-100.jpg",
     (0.45, 0.22, 0.86, 0.74),
     "arc with sawtooth perimeter, with hole 92a inside; plate H right half"),
    ("piece-122-face",
     "p00x-plate-M-clock-face.jpg",
     (0.02, 0.02, 0.98, 0.98),
     "whole plate M = piece 122 clock face (rectangle with brown border)"),
]

print(f"Cropping {len(PIECES)} test pieces...\n")

for piece_id, src_name, frac, notes in PIECES:
    src = SCANS / src_name
    img = Image.open(src)
    w, h = img.size
    x0 = int(frac[0] * w)
    y0 = int(frac[1] * h)
    x1 = int(frac[2] * w)
    y1 = int(frac[3] * h)
    crop = img.crop((x0, y0, x1, y1))
    out = OUT / f"{piece_id}.png"
    crop.save(out)
    print(f"  {piece_id:18s}  src {w}x{h}  ->  crop {crop.size[0]}x{crop.size[1]}  ({notes})")
    print(f"                      {out}")

print("\nDone.")
