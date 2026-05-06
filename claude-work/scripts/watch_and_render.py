#!/usr/bin/env python3
"""Daemon: watch claude-work/state/render-triggers/ for new request files and run
preview_render.py against the piece id named in each.

Usage:
    python watch_and_render.py [--poll 2.0]

The trigger-file protocol:
  - Cowork-Claude (or you) drop a file into claude-work/state/render-triggers/.
  - The filename or file content names a piece id (3 digits, optional letter
    variant — e.g. "069", "092a"). The first match found by the regex wins.
  - This daemon picks the file up, runs preview_render.render(piece_id) inline,
    and moves the trigger to .../render-triggers/done/ on success or
    .../render-triggers/failed/ on error.
  - Output (screenshot + console log + JSON summary) lands in
    claude-work/state/preview-renders/<NNN>.{png,log,json}.

Leave this running in a Terminal window during your work session. Stop with Ctrl-C.

Trigger files of any name are picked up; conventions worth using:
    req-2026-05-05-001.txt   — content: "069"
    069.txt                  — empty; piece id from filename
    render-094.txt           — content irrelevant; filename matches first

Both files and content are scanned; filename takes priority.

Requires: Playwright + Chromium installed in .venv-headless/, plus this script
launched from the same .venv-headless/. See ENVIRONMENT.md for the install path.
"""
import argparse
import re
import shutil
import sys
import time
from pathlib import Path

# Make sibling preview_render importable.
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = SCRIPTS_DIR.parent.parent
TRIGGERS_DIR = REPO_ROOT / "claude-work" / "state" / "render-triggers"
DONE_DIR = TRIGGERS_DIR / "done"
FAILED_DIR = TRIGGERS_DIR / "failed"
RENDERS_DIR = REPO_ROOT / "claude-work" / "state" / "preview-renders"

# Piece id: 3 digits with optional lowercase letter (e.g. 069, 092a, 112a).
PIECE_RE = re.compile(r"\b(\d{3}[a-z]?)\b")


def extract_piece(trigger_file: Path) -> str | None:
    """Pull a piece id out of the filename first, then the file content."""
    m = PIECE_RE.search(trigger_file.name)
    if m:
        return m.group(1)
    try:
        content = trigger_file.read_text().strip()
        m = PIECE_RE.search(content)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def run_one(trigger_file: Path) -> bool:
    """Process one trigger file. Returns True on clean render."""
    from preview_render import render  # imported once; cached after first call

    piece = extract_piece(trigger_file)
    if not piece:
        print(f"  ✗ {trigger_file.name}: could not extract piece id; → failed/")
        FAILED_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(trigger_file), FAILED_DIR / trigger_file.name)
        return False

    print(f"  → rendering {piece} (trigger: {trigger_file.name})...")
    try:
        summary = render(piece, RENDERS_DIR)
        ok = summary["error_count"] == 0
        marker = "✓" if ok else "⚠"
        print(f"  {marker} {piece}: banner={summary['banner']!r}, "
              f"errors={summary['error_count']}, "
              f"console={summary['console_msgs']}, "
              f"{summary['render_time_ms']}ms")
        DONE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(trigger_file), DONE_DIR / trigger_file.name)
        return ok
    except Exception as e:
        print(f"  ✗ {piece}: render failed: {e}")
        FAILED_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(trigger_file), FAILED_DIR / trigger_file.name)
        return False


def main():
    ap = argparse.ArgumentParser(description="Watch render-triggers/ and run preview_render.")
    ap.add_argument("--poll", type=float, default=2.0,
                    help="Polling interval in seconds (default: 2.0)")
    args = ap.parse_args()

    TRIGGERS_DIR.mkdir(parents=True, exist_ok=True)
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)

    print("[watch_and_render] z-paper-clock preview-render daemon")
    print(f"[watch_and_render] watching:  {TRIGGERS_DIR.relative_to(REPO_ROOT)}/")
    print(f"[watch_and_render] outputs:   {RENDERS_DIR.relative_to(REPO_ROOT)}/")
    print(f"[watch_and_render] poll:      every {args.poll}s")
    print("[watch_and_render] Ctrl-C to stop.")
    print()

    while True:
        try:
            triggers = sorted(
                p for p in TRIGGERS_DIR.iterdir()
                if p.is_file() and not p.name.startswith(".")
            )
            if triggers:
                print(f"[{time.strftime('%H:%M:%S')}] {len(triggers)} trigger(s)")
                for t in triggers:
                    run_one(t)
                print()
            time.sleep(args.poll)
        except KeyboardInterrupt:
            print("\n[watch_and_render] stopping.")
            break
        except Exception as e:
            # Don't die on a transient filesystem hiccup; log and keep going.
            print(f"[watch_and_render] loop error: {e}; continuing")
            time.sleep(args.poll)


if __name__ == "__main__":
    main()
