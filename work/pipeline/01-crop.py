"""
Crop each piece from its prepped plate scan, writing work/pieces/NNN/crop.png.

Bounding-box columns in pieces.csv (bbox_x, bbox_y, bbox_w, bbox_h) are
fractional coordinates in [0, 1] relative to the source image dimensions, not
pixels. This makes crops robust to rescans at different resolutions.
"""

import csv
import glob
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
PIECES_CSV = REPO / "work" / "pieces.csv"
SCANS = REPO / "source" / "scans-prepped"
PIECES_DIR = REPO / "work" / "pieces"


def scan_path_for_plate(plate: str) -> Path:
    matches = glob.glob(str(SCANS / f"p00x-plate-{plate}-*.jpg"))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one prepped scan for plate {plate}, "
            f"found {len(matches)}: {matches}"
        )
    return Path(matches[0])


def main():
    rows = []
    with PIECES_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"Cropping {len(rows)} pieces...\n")

    scan_cache: dict[str, tuple[Image.Image, int, int]] = {}

    for row in rows:
        piece_id = int(row["id"])
        plate = row["plate"]
        bbox_x = float(row["bbox_x"])
        bbox_y = float(row["bbox_y"])
        bbox_w = float(row["bbox_w"])
        bbox_h = float(row["bbox_h"])

        if plate not in scan_cache:
            p = scan_path_for_plate(plate)
            img = Image.open(p)
            W, H = img.size
            scan_cache[plate] = (img, W, H)
        img, W, H = scan_cache[plate]

        x0 = round(bbox_x * W)
        y0 = round(bbox_y * H)
        x1 = round((bbox_x + bbox_w) * W)
        y1 = round((bbox_y + bbox_h) * H)

        crop = img.crop((x0, y0, x1, y1))
        out_dir = PIECES_DIR / f"{piece_id:03d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "crop.png"
        crop.save(out_path)

        print(
            f"piece {piece_id:03d}  plate {plate}  "
            f"bbox ({x0},{y0})-({x1},{y1})  "
            f"-> crop.png  {crop.size[0]}x{crop.size[1]}"
        )

    print(f"\nDone. {len(rows)} crops written to {PIECES_DIR}.")


if __name__ == "__main__":
    main()
