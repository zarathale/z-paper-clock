"""
Pre-process cleaned plate scans for downstream auto-tracing.

Three passes per image, applied to LUMINANCE ONLY so chroma (e.g. plate M's
brown border) is preserved:

  1. Local-max background estimate + flat-field correction
     For each pixel, estimate the local "paper white" as the local maximum
     in a wide neighborhood (paper is the brightest thing in any window
     once content is sparse). Smooth the max-map with a Gaussian. Divide
     the luminance by this background and rescale. Removes:
       - book-gutter shadow
       - vignette / uneven lighting from phone-photo capture

  2. Gentle luminance levels stretch
     Push the 99.5th percentile to pure white (paper background). Leave the
     low end alone so brown borders stay brown.

  3. Bleed-through suppression
     Pixels with high L and near-neutral chroma above `bleed_cutoff` snap
     to pure white. Coloured content is exempt by chroma test.

Inputs:  source/scans-clean/*.jpg
Outputs: source/scans-prepped/*.jpg  (same filenames, JPEG q=92)
"""

from pathlib import Path
import argparse
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, maximum_filter


def _bg_estimate_max(channel, max_size, smooth_sigma, ds=4):
    """Estimate paper-white background as a smoothed local maximum.

    1. Downsample by `ds` for speed.
    2. Local-max with a window of `max_size / ds` -- pulls each pixel up to
       the brightest pixel in its neighborhood (i.e. nearby paper).
    3. Gaussian-smooth so the result is a slowly-varying illumination map.
    4. Upsample back to original size.

    This is robust to dark content (ink, brown borders) -- their darkness
    doesn't pull the background estimate down because we take the max,
    not the average.
    """
    h, w = channel.shape
    sw, sh = max(1, w // ds), max(1, h // ds)
    small = np.array(Image.fromarray(channel).resize((sw, sh), Image.BILINEAR))
    win = max(3, int(max_size / ds))
    bg_max = maximum_filter(small, size=win)
    bg_smooth = gaussian_filter(bg_max.astype(np.float32),
                                sigma=smooth_sigma / ds)
    bg_full = np.array(Image.fromarray(bg_smooth.clip(0, 255).astype(np.uint8))
                       .resize((w, h), Image.BILINEAR), dtype=np.float32)
    return bg_full


def rgb_to_lab_arrays(rgb):
    """Convert HxWx3 uint8 RGB to (L, a, b) float arrays via Pillow."""
    pil = Image.fromarray(rgb).convert("LAB")
    lab = np.array(pil, dtype=np.float32)
    return lab[..., 0], lab[..., 1], lab[..., 2]


def lab_arrays_to_rgb(L, a, b):
    """Convert L, a, b float arrays back to HxWx3 uint8 RGB via Pillow."""
    lab = np.stack([np.clip(L, 0, 255),
                    np.clip(a, 0, 255),
                    np.clip(b, 0, 255)], axis=-1).astype(np.uint8)
    return np.array(Image.fromarray(lab, mode="LAB").convert("RGB"))


def preprocess(src_path, dst_path, max_size=200, smooth_sigma=120,
               high_pct=99.5, bleed_cutoff=235, chroma_threshold=8):
    """Run the full pre-processing pipeline.

    - max_size:        local-max window for background estimate (pixels)
    - smooth_sigma:    Gaussian smoothing of the bg map (pixels)
    - high_pct:        percentile of L that gets pushed to 255 (paper white)
    - bleed_cutoff:    luminance above which near-neutral pixels snap to pure white
    - chroma_threshold: how far from neutral (in LAB a/b) a pixel can be and
                       still count as bleed-through; coloured content (e.g.
                       brown border) is exempt.
    """
    rgb = np.array(Image.open(src_path).convert("RGB"))

    # 1. Decompose to LAB and operate on luminance only.
    L, a, b = rgb_to_lab_arrays(rgb)

    # 2. Flat-field L using local-max background.
    bg = _bg_estimate_max(L.astype(np.uint8),
                          max_size=max_size, smooth_sigma=smooth_sigma)
    target_white = 250.0  # gives a hair of headroom under 255
    L_flat = np.clip(L * (target_white / np.maximum(bg, 1.0)), 0, 255)

    # 3. Gentle high-end stretch: push the high percentile to pure 255.
    hi = np.percentile(L_flat, high_pct)
    L_stretched = np.clip(L_flat * (255.0 / max(hi, 1.0)), 0, 255)

    # 4. Bleed-through suppression: only on near-neutral, high-L pixels.
    chroma = np.maximum(np.abs(a - 128.0), np.abs(b - 128.0))
    bleed_mask = (L_stretched > bleed_cutoff) & (chroma < chroma_threshold)
    L_stretched[bleed_mask] = 255

    # 5. Reassemble. Chroma untouched -> brown border, etc., preserved.
    out = lab_arrays_to_rgb(L_stretched, a, b)
    Image.fromarray(out).save(dst_path, quality=92, subsampling=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="source/scans-clean")
    ap.add_argument("--dst", default="source/scans-prepped")
    ap.add_argument("--pattern", default="*.jpg")
    ap.add_argument("--max-size", type=int, default=200,
                    help="Local-max window for background estimate (pixels)")
    ap.add_argument("--smooth-sigma", type=float, default=120,
                    help="Smoothing of background map (pixels)")
    ap.add_argument("--high", type=float, default=99.5,
                    help="High percentile of L pushed to 255")
    ap.add_argument("--bleed", type=int, default=235,
                    help="L above this snaps to white if chroma is near-neutral")
    ap.add_argument("--chroma", type=int, default=8,
                    help="Max chroma distance from neutral to count as bleed")
    ap.add_argument("--limit", default=None,
                    help="Comma-sep list of filename stems to process (skip the rest)")
    args = ap.parse_args()

    repo = Path("/sessions/happy-quirky-goldberg/mnt/z-paper-clock")
    src_dir = repo / args.src
    dst_dir = repo / args.dst
    dst_dir.mkdir(parents=True, exist_ok=True)
    limit = set(args.limit.split(",")) if args.limit else None

    files = sorted(src_dir.glob(args.pattern))
    processed = 0
    for src in files:
        if limit and src.stem not in limit:
            continue
        dst = dst_dir / src.name
        preprocess(src, dst,
                   max_size=args.max_size, smooth_sigma=args.smooth_sigma,
                   high_pct=args.high, bleed_cutoff=args.bleed,
                   chroma_threshold=args.chroma)
        in_size = src.stat().st_size / 1024
        out_size = dst.stat().st_size / 1024
        print(f"  {src.name}  {in_size:.0f}K -> {out_size:.0f}K")
        processed += 1
    print(f"\nProcessed {processed} files into {dst_dir}")


if __name__ == "__main__":
    main()
