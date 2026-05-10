#!/usr/bin/env python3
"""
preview_bridge.py — local HTTP bridge between preview.html and Claude's filesystem.

Run once per session (from any directory):
    python3.12 claude-work/scripts/preview_bridge.py

Then press the "→ Claude" button in preview.html to send the current piece state.
Claude reads the output file at: claude-work/state/preview-dump.json

Endpoints:
    GET  /ping             → health check (preview.html uses this to detect bridge)
    POST /dump             → write payload to claude-work/state/preview-dump.json
    POST /dump/<name>      → write to claude-work/state/<name>-dump.json

Handles CORS for file:// origin so preview.html can fetch without a dev server.
"""

import http.server
import json
import pathlib
import datetime
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent   # claude-work/scripts/
REPO_ROOT  = SCRIPT_DIR.parent.parent                  # z-paper-clock/
STATE_DIR  = REPO_ROOT / "claude-work" / "state"
PORT = 7777


class BridgeHandler(http.server.BaseHTTPRequestHandler):

    def _send_cors(self):
        # file:// pages send Origin: null; * covers it
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        """Preflight for CORS."""
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"bridge ok")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parts = self.path.strip("/").split("/")
        if parts[0] != "dump":
            self.send_response(404)
            self.end_headers()
            return

        name = parts[1] if len(parts) > 1 and parts[1] else "preview"
        # sanitise: only allow alphanum + hyphen
        name = "".join(c for c in name if c.isalnum() or c == "-") or "preview"

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except Exception as e:
            self.send_response(400)
            self._send_cors()
            self.end_headers()
            self.wfile.write(f"bad json: {e}".encode())
            return

        data["_bridgeTimestamp"] = datetime.datetime.now().isoformat()

        STATE_DIR.mkdir(parents=True, exist_ok=True)
        out_path = STATE_DIR / f"{name}-dump.json"
        out_path.write_text(json.dumps(data, indent=2))

        size_kb = out_path.stat().st_size / 1024
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[bridge] {ts}  {out_path.name}  ({size_kb:.1f} KB)")

        self.send_response(200)
        self._send_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "file": str(out_path)}).encode())

    def log_message(self, format, *args):
        pass  # suppress default per-request log lines; we print our own above


if __name__ == "__main__":
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    server = http.server.HTTPServer(("localhost", PORT), BridgeHandler)
    print(f"[bridge] listening on http://localhost:{PORT}")
    print(f"[bridge] dumps  →  {STATE_DIR}/")
    print(f"[bridge] Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[bridge] stopped")
