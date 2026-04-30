"""
Build a side-by-side comparison PNG for each test piece:
  [original crop] | [bitmap fed to Potrace] | [rendered SVG output]

Each row labels the piece. Output goes to work/auto-trace-test-v2/compare/.
"""

from pathlib import Path
import io
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/sessions/happy-quirky-goldberg/mnt/z-paper-clock/work/auto-trace-test-v2")
CROPS = ROOT / "crops"
BITMAP = ROOT / "bitmap"
SVG = ROOT / "svg"
OUT = ROOT / "compare"
OUT.mkdir(exist_ok=True)

PANEL_H = 700  # height of each panel; widths scale to keep aspect
GAP = 16
LABEL_H = 30
TOTAL_W_TARGET = None  # not used; widths are determined per-panel

def label_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, 18)
    return ImageFont.load_default()


def fit(img, target_h):
    w, h = img.size
    scale = target_h / h
    return img.resize((int(w * scale), target_h), Image.LANCZOS)


def svg_to_png(svg_path, target_h):
    # render SVG to PNG bytes at high enough resolution, then resize
    png_bytes = cairosvg.svg2png(url=str(svg_path), output_height=target_h)
    return Image.open(io.BytesIO(png_bytes)).convert("RGB")


def make_compare(name):
    crop = Image.open(CROPS / f"{name}.png").convert("RGB")
    bmp = Image.open(BITMAP / f"{name}.png").convert("RGB")
    svg_img = svg_to_png(SVG / f"{name}.svg", PANEL_H)

    crop = fit(crop, PANEL_H)
    bmp = fit(bmp, PANEL_H)
    svg_img = fit(svg_img, PANEL_H)

    panels = [
        ("1. Original crop", crop),
        ("2. Binarized (Potrace input)", bmp),
        ("3. Auto-traced SVG", svg_img),
    ]

    total_w = sum(p[1].size[0] for p in panels) + GAP * (len(panels) + 1)
    total_h = PANEL_H + LABEL_H + GAP * 2
    canvas = Image.new("RGB", (total_w, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = label_font()

    x = GAP
    y = LABEL_H + GAP
    for label, img in panels:
        # Label above the panel
        draw.text((x, GAP // 2), label, fill="black", font=font)
        canvas.paste(img, (x, y))
        x += img.size[0] + GAP

    # Top-right: piece name
    title = f"{name}"
    draw.text((total_w - 200, GAP // 2), title, fill="#666", font=font)

    out = OUT / f"{name}.png"
    canvas.save(out, optimize=True)
    print(f"  {name}: {canvas.size[0]}x{canvas.size[1]}  -> {out}")


print(f"Building comparison images...\n")
for crop in sorted(CROPS.glob("*.png")):
    make_compare(crop.stem)
print("\nDone.")
