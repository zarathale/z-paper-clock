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
    POST /save             → merge {piece, assembled} into work/pieces/NNN/NNN.json

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

        if parts[0] == "save":
            self._handle_save()
            return

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

    def _handle_save(self):
        """POST /save — merge {piece, assembled} into work/pieces/NNN/NNN.json.

        Reads the existing sidecar (if any), replaces the `assembled` block
        verbatim, preserves every other top-level field, and writes back. Also
        stamps `_savedAt` for diff legibility. Letter variants like 092a or
        093b live under the numeric folder (work/pieces/092/092a.json).
        """
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            payload = json.loads(body)
        except Exception as e:
            self.send_response(400)
            self._send_cors()
            self.end_headers()
            self.wfile.write(f"bad json: {e}".encode())
            return

        piece_id = payload.get("piece", "")
        assembled = payload.get("assembled")
        if not piece_id or assembled is None:
            self.send_response(400)
            self._send_cors()
            self.end_headers()
            self.wfile.write(b"missing piece or assembled")
            return

        # Letter-variant pieces (092a, 093b) live under the numeric folder.
        numeric = "".join(c for c in piece_id if c.isdigit())
        if not numeric:
            self.send_response(400)
            self._send_cors()
            self.end_headers()
            self.wfile.write(b"piece id has no digits")
            return
        sidecar_path = REPO_ROOT / "work" / "pieces" / numeric / f"{piece_id}.json"
        sidecar_path.parent.mkdir(parents=True, exist_ok=True)

        if sidecar_path.exists():
            try:
                existing = json.loads(sidecar_path.read_text())
            except Exception:
                existing = {}
        else:
            existing = {}

        existing["assembled"] = assembled
        existing["_savedAt"] = datetime.datetime.now().isoformat()

        sidecar_path.write_text(json.dumps(existing, indent=2))
        size_kb = sidecar_path.stat().st_size / 1024
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        rel = sidecar_path.relative_to(REPO_ROOT)
        print(f"[bridge] {ts}  saved {rel}  ({size_kb:.1f} KB)")

        self.send_response(200)
        self._send_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "file": str(sidecar_path)}).encode())

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
