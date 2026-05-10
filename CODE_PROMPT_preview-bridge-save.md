---
status: ready-for-code
started: 2026-05-10
owner: Zarathale (Alan)
target: preview-bridge-save
---

# CODE_PROMPT — Direct sidecar save via bridge

## What You Are Doing and Why

The current "Save assembled pose" workflow produces a JSON snippet the user has to
hand-merge into the sidecar file. Every page reload loses in-progress work because the
merge step is skipped. This PR eliminates that step entirely.

The bridge server (`claude-work/scripts/preview_bridge.py`) already exists as a read path.
Add a `/save` endpoint that reads the current sidecar, merges the new `assembled` block,
and writes it back. Change the Save button in `preview.html` to POST to `/save` directly.
If the bridge is offline, fall back to the existing copy/download modal so nothing breaks.

## Prerequisites — confirm before starting

- `claude-work/scripts/preview_bridge.py` exists (written 2026-05-10).
- `preview.html` at repo root has PR A + PR B + PR C merged (Bench mode, Cluster mode,
  bridge button already wired).
- `python3.12` available; no third-party packages needed (stdlib only).

## Read These Files First

1. `claude-work/scripts/preview_bridge.py` — existing endpoints (`/ping`, `/dump`).
   Add `/save` following the same CORS + error-handling pattern.
2. `preview.html` — grep for `saveAssembledPose\|Save assembled pose\|copy.*JSON\|download`
   to find all save-button handlers. There are two: one in Bench mode, one in Cluster mode.
   Both need the same treatment.

## Target File Structure Changes

```
claude-work/scripts/preview_bridge.py    ← update: add /save endpoint
preview.html                             ← update: save buttons POST to /save; fallback to modal
```

## Numbered Tasks

### Task 1 — Add `/save` endpoint to `preview_bridge.py`

Insert after the `/dump` handler in `do_POST`:

```python
if parts[0] == 'save':
    length = int(self.headers.get('Content-Length', 0))
    body   = self.rfile.read(length)
    try:
        payload = json.loads(body)
    except Exception as e:
        self.send_response(400); self._send_cors(); self.end_headers()
        self.wfile.write(f'bad json: {e}'.encode()); return

    piece_id = payload.get('piece', '')
    assembled = payload.get('assembled')
    if not piece_id or assembled is None:
        self.send_response(400); self._send_cors(); self.end_headers()
        self.wfile.write(b'missing piece or assembled'); return

    # Resolve sidecar path — handle letter variants (093a, 093b)
    numeric = ''.join(c for c in piece_id if c.isdigit())
    sidecar_path = REPO_ROOT / 'work' / 'pieces' / numeric / f'{piece_id}.json'
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing sidecar or start fresh
    if sidecar_path.exists():
        try:
            existing = json.loads(sidecar_path.read_text())
        except Exception:
            existing = {}
    else:
        existing = {}

    # Merge: replace assembled block, preserve everything else
    existing['assembled'] = assembled
    existing['_savedAt']  = datetime.datetime.now().isoformat()

    sidecar_path.write_text(json.dumps(existing, indent=2))
    size_kb = sidecar_path.stat().st_size / 1024
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'[bridge] {ts}  saved {sidecar_path.relative_to(REPO_ROOT)}  ({size_kb:.1f} KB)')

    self.send_response(200); self._send_cors()
    self.send_header('Content-Type', 'application/json'); self.end_headers()
    self.wfile.write(json.dumps({'ok': True, 'file': str(sidecar_path)}).encode())
    return
```

Place this block so it executes before the existing `/dump` handler check (or refactor
`do_POST` into a dispatch dict — either is fine as long as both endpoints work).

### Task 2 — `saveViaBridge(assembled, pieceId)` in `preview.html`

Add a helper near `sendToClaude`:

```js
async function saveViaBridge(assembled, pieceId) {
  try {
    const res = await fetch('http://localhost:7777/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ piece: pieceId, assembled }),
    });
    return res.ok;
  } catch {
    return false;   // bridge offline
  }
}
```

### Task 3 — Update Bench mode save button

Find the existing Bench-mode "Save assembled pose" handler. It currently builds the
`assembled` object and shows a copy/download modal. Replace with:

```js
// Try bridge first; fall back to copy modal
const saved = await saveViaBridge(assembled, currentPieceId);
if (saved) {
  // Flash "Saved ✓" on the button for 2 s — same pattern as bridge-btn
  flashBtn(savePoseBtn, 'Saved ✓', 'btn-ok');
} else {
  // Bridge offline — show the existing copy modal as before
  showSaveModal(assembled);
}
```

`flashBtn(btn, label, cls)` is a small helper (add it once, reuse for both buttons):

```js
function flashBtn(btn, label, cls) {
  const orig = btn.textContent;
  btn.disabled = true;
  btn.textContent = label;
  btn.classList.add(cls);
  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = orig;
    btn.classList.remove(cls);
  }, 2000);
}
```

### Task 4 — Update Cluster mode "Save selected piece" button

Same treatment as Task 3, but `pieceId` is `selectedPiece.id` rather than
`currentPieceId`. The `assembled` object includes both `folds` (from the piece's fold
sliders if in assembled pose) and `transform` (from the piece's current cluster-local
transform). Build it the same way PR C's save handler does; just change the delivery
from "show modal" to "POST to bridge, fall back to modal."

### Task 5 — Auto-save on piece switch (Bench mode only)

When the user loads a different piece in Bench mode (clicks Load with a new piece id),
check if the current piece has unsaved changes (fold sliders or transform differ from
what was loaded from the sidecar). If so, auto-save via bridge before switching:

```js
async function maybeSaveCurrent() {
  if (!currentPieceId) return;
  const assembled = buildCurrentAssembled();  // same logic as save button
  if (!assembledIsIdentity(assembled)) {
    await saveViaBridge(assembled, currentPieceId);
    // No flash — this is silent. Bridge-offline case: silently skip.
  }
}
```

Call `await maybeSaveCurrent()` at the top of the Load button handler before switching
pieces. `assembledIsIdentity` returns true if all folds are 0 and transform is identity
within ε=0.01 — don't auto-save a default pose (that would overwrite real data with zeros).

## Verification Checklist

1. Bridge server starts: `python3.12 claude-work/scripts/preview_bridge.py` — no errors.
2. Load piece 069 in Bench mode. Move a fold slider to −90. Click Save assembled pose.
   Terminal prints `[bridge] HH:MM:SS  saved work/pieces/069/069.json  (N KB)`.
   Button flashes "Saved ✓" for 2 s.
3. `work/pieces/069/069.json` exists; `assembled.folds` has the slider values; other
   existing sidecar fields (`character`, etc.) are preserved.
4. Reload page. Load 069. Fold sliders pre-set to −90 from sidecar. ✓ Persistence works.
5. Stop bridge. Click Save assembled pose. Copy modal appears (fallback). ✓ Graceful.
6. Load 069, move slider, then type 070 and Load. Bridge prints save for 069 before
   loading 070 (auto-save on switch). ✓
7. Cluster mode: select piece 069, move transform slider, click Save selected piece.
   Terminal prints save for 069. ✓

## What NOT to Change

- The copy/download modal — keep it intact as the offline fallback.
- Sidecar schema — `assembled` block shape is per DECISIONS #11/#13; don't restructure.
- The `/dump` and `/ping` endpoints — no changes to those.
- Any parsing, rendering, or fold logic.
