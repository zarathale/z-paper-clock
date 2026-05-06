#!/usr/bin/env python3
"""Render a piece in preview.html via headless Chromium and dump screenshot + console log.

Usage:
    python preview_render.py NNN [--out claude-work/state/preview-renders] [--port 8765]

What it does:
  - Spins up a tiny local HTTP server rooted at the repo root (so preview.html's
    fetch() of work/pieces/NNN/NNN.svg works the same way it does in your browser).
  - Launches headless Chromium via Playwright.
  - Navigates to preview.html?piece=NNN.
  - Waits for the dispatch banner ('panels-first ✓' or 'cut-line-first (legacy)').
  - Captures a screenshot, the console log, and a small JSON summary.

Outputs (under <out>/):
    <NNN>.png   — viewport screenshot once the dispatch banner appears
    <NNN>.log   — newline-delimited console messages + any pageerrors
    <NNN>.json  — banner text, error count, console-message count, render time

Designed to be invoked by watch_and_render.py (the daemon) but also fine to run
directly when debugging.

Requires: Playwright + Chromium installed in .venv-headless/ (see ENVIRONMENT.md).
Run from the repo root or any subdirectory — paths are resolved relative to this
script's location.
"""
import argparse
import http.server
import json
import socketserver
import sys
import threading
import time
from pathlib import Path

# Repo root is two parents up from this file (claude-work/scripts/X.py).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def serve_repo(port: int) -> socketserver.TCPServer:
    """Start a SimpleHTTPRequestHandler rooted at REPO_ROOT on a background thread."""
    def handler(*args, **kw):
        return http.server.SimpleHTTPRequestHandler(*args, directory=str(REPO_ROOT), **kw)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    httpd.allow_reuse_address = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def render(piece: str, out_dir: Path, port: int = 8765, timeout_ms: int = 15000) -> dict:
    """Render preview.html?piece=<piece> headlessly, write outputs, return summary dict."""
    # Lazy import — pay the Playwright import cost only when render() is called.
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    httpd = serve_repo(port)
    banner_text = None
    messages: list[dict] = []
    errors: list[str] = []
    t_render_ms = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            page.on("console", lambda msg: messages.append({"type": msg.type, "text": msg.text}))
            page.on("pageerror", lambda err: errors.append(str(err)))

            url = f"http://127.0.0.1:{port}/preview.html?piece={piece}"
            t0 = time.time()
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            # Wait for whichever dispatch banner shows up first.
            try:
                page.wait_for_selector(
                    "text=/panels-first ✓|cut-line-first \\(legacy\\)/",
                    timeout=timeout_ms,
                )
            except Exception as e:
                errors.append(f"banner-wait-timeout: {e}")
            t_render_ms = int((time.time() - t0) * 1000)

            # Capture screenshot.
            png_path = out_dir / f"{piece}.png"
            page.screenshot(path=str(png_path), full_page=False)

            # Pull dispatch-banner text if visible.
            try:
                handle = page.query_selector("text=/panels-first ✓|cut-line-first \\(legacy\\)/")
                banner_text = handle.inner_text() if handle else None
            except Exception:
                banner_text = None

            browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()

    # Write console log.
    log_path = out_dir / f"{piece}.log"
    log_lines = [f"[{m['type']}] {m['text']}" for m in messages]
    if errors:
        log_lines.append("")
        log_lines.append("ERRORS:")
        log_lines.extend(errors)
    log_path.write_text("\n".join(log_lines))

    summary = {
        "piece": piece,
        "banner": banner_text,
        "console_msgs": len(messages),
        "error_count": len(errors),
        "errors": errors,
        "render_time_ms": t_render_ms,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "outputs": {
            "screenshot": str(out_dir / f"{piece}.png"),
            "log": str(out_dir / f"{piece}.log"),
            "json": str(out_dir / f"{piece}.json"),
        },
    }
    json_path = out_dir / f"{piece}.json"
    json_path.write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser(description="Render a piece in preview.html via headless Chromium.")
    ap.add_argument("piece", help="Piece id (e.g. 069 or 092a)")
    ap.add_argument("--out", default="claude-work/state/preview-renders",
                    help="Output dir, relative to repo root (default: claude-work/state/preview-renders)")
    ap.add_argument("--port", type=int, default=8765, help="Local HTTP server port (default: 8765)")
    args = ap.parse_args()

    out_dir = REPO_ROOT / args.out
    summary = render(args.piece, out_dir, port=args.port)
    print(json.dumps(summary, indent=2))
    # Non-zero exit if there were render errors, so the daemon can surface them.
    sys.exit(1 if summary["error_count"] > 0 else 0)


if __name__ == "__main__":
    main()
