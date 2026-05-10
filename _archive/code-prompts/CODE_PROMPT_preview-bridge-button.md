---
status: shipped
started: 2026-05-10
shipped: 2026-05-10
owner: Zarathale (Alan)
target: preview-bridge-button
---

_Shipped 2026-05-10; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md / claude-work/STATUS.md for current state._

# CODE_PROMPT — preview.html "→ Claude" bridge button

## What You Are Doing and Why

Adds a one-press "→ Claude" button to `preview.html` that sends the current piece's parsed
state to a local bridge server (`claude-work/scripts/preview_bridge.py`), which writes it
to `claude-work/state/preview-dump.json`. Claude reads that file instead of having Alan
copy-paste console output.

The bridge server already exists. This Code session wires the browser side: a `sendToClaude()`
function + button. No new dependencies; pure vanilla JS + DOM addition to the existing file.

## Prerequisites — confirm before starting

- `claude-work/scripts/preview_bridge.py` exists (written in Cowork 2026-05-10).
- `preview.html` exists at repo root with the PR A foundational changes (cutouts, TC,
  camera lock, Bench/Cluster scaffold) merged in.
- No npm/node/build step — preview.html is a single static file.

## Read These Files First

1. `claude-work/scripts/preview_bridge.py` — understand the endpoint shape:
   `POST http://localhost:7777/dump` with JSON body → writes `preview-dump.json`.
   `GET http://localhost:7777/ping` → health check, returns `"bridge ok"`.
2. `preview.html` — grep for `sendSceneToFile\|saveAssembledPose\|#piece-id\|sidebar` to
   orient to the sidebar structure and the existing save/export button pattern.

## Target File Structure Changes

```
preview.html              ← update: add sendToClaude() + bridge button
claude-work/scripts/
  preview_bridge.py       ← already exists (no changes)
claude-work/state/
  preview-dump.json       ← NEW at runtime (written by bridge, read by Claude)
```

## Numbered Tasks

### Task 1 — Add `sendToClaude(payload, name)` function

Add this function near the other utility/export helpers (e.g. close to `saveAssembledPose`
or the download-blob helper):

```js
async function sendToClaude(payload, name = 'preview') {
  const btn = document.getElementById('bridge-btn');
  const label = btn ? btn.querySelector('.bridge-label') : null;
  const setLabel = (txt, cls) => {
    if (!btn) return;
    btn.disabled = true;
    if (label) label.textContent = txt;
    btn.className = btn.className.replace(/\bbtn-\S+/g, '').trim();
    if (cls) btn.classList.add(cls);
    setTimeout(() => {
      btn.disabled = false;
      if (label) label.textContent = '→ Claude';
      btn.classList.remove(cls);
    }, 2000);
  };
  try {
    const res = await fetch(`http://localhost:7777/dump/${name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      setLabel('Sent ✓', 'btn-ok');
    } else {
      setLabel('Error ' + res.status, 'btn-err');
    }
  } catch {
    setLabel('Bridge offline', 'btn-err');
  }
}
```

### Task 2 — Add `buildBridgePayload()` function

This collects the current piece state into a clean object for Claude to read:

```js
function buildBridgePayload() {
  const payload = {
    piece: currentPieceId || null,
    panelsFirst: null,
    cutouts: null,
    foldState: {},
    sidecar: null,
  };

  // parsed state
  if (typeof parsed !== 'undefined' && parsed) {
    if (parsed.panelsFirst) {
      const pf = parsed.panelsFirst;
      payload.panelsFirst = {
        panels: pf.panels ? [...pf.panels.entries()].map(([id, p]) => ({
          id,
          polygon: p.polygon,
          area: p.area,
        })) : [],
        folds: pf.folds || [],
        hingeTree: pf.hingeTree ? {
          // Maps don't serialise; convert
          nodes: pf.hingeTree.nodes
            ? Object.fromEntries([...pf.hingeTree.nodes.entries()].map(([k, v]) => [k, {
                panel: v.panel, parent: v.parent, foldIndex: v.foldIndex,
              }]))
            : {},
          root: pf.hingeTree.root,
          subtrees: pf.hingeTree.subtrees || [],
        } : null,
        attachPoints: pf.attachPoints || [],
        closureAttaches: pf.closureAttaches || [],
        marks: pf.marks ? [...pf.marks.entries()].map(([id, m]) => ({ id, ...m })) : [],
      };
    }
    if (parsed.cutouts) payload.cutouts = parsed.cutouts;
  }

  // current fold slider values
  document.querySelectorAll('#fold-controls .fold-row input[type=range]').forEach(sl => {
    if (sl.dataset.pathId) payload.foldState[sl.dataset.pathId] = Number(sl.value);
  });

  // sidecar if loaded (expose via module-level variable if not already)
  if (typeof currentSidecar !== 'undefined' && currentSidecar) {
    payload.sidecar = currentSidecar;
  }

  return payload;
}
```

**Note on `currentSidecar`:** check whether `preview.html` already has a module-level
variable holding the loaded sidecar (search for `maybeLoadSidecar` — it likely assigns to
a local or module-level var). If not module-level, promote it to module scope so
`buildBridgePayload` can read it. Name it `currentSidecar`.

### Task 3 — Add the button to the sidebar

Find the piece-id input row (the `<div>` containing `#piece-id` and the Load button). Add
the bridge button immediately after that row, before the fold-controls section:

```html
<div id="bridge-row" style="margin: 6px 0 2px;">
  <button id="bridge-btn" title="Send current piece state to Claude via local bridge (run preview_bridge.py first)"
    style="width:100%; padding:5px 8px; font-size:12px; cursor:pointer; background:#1a2a1a; color:#7fc97f; border:1px solid #3a5a3a; border-radius:3px;">
    <span class="bridge-label">→ Claude</span>
  </button>
</div>
```

Wire it after the DOM is ready (or at the same point where other sidebar buttons are wired):

```js
document.getElementById('bridge-btn').addEventListener('click', () => {
  sendToClaude(buildBridgePayload());
});
```

Add two tiny CSS rules for the feedback states (inline in the `<style>` block or near other
button styles):

```css
#bridge-btn.btn-ok  { background: #0a2a0a; color: #7fc97f; border-color: #4a8a4a; }
#bridge-btn.btn-err { background: #2a0a0a; color: #cf7f7f; border-color: #8a3a3a; }
```

### Task 4 — Ping check on page load (optional but nice)

After the button is wired, add a one-time ping to detect whether the bridge is running.
If offline, dim the button and update the title:

```js
fetch('http://localhost:7777/ping').then(r => {
  if (!r.ok) throw new Error();
  // bridge online — button stays as-is
}).catch(() => {
  const btn = document.getElementById('bridge-btn');
  if (btn) {
    btn.title = 'Bridge offline — run: python3.12 claude-work/scripts/preview_bridge.py';
    btn.style.opacity = '0.45';
    btn.querySelector('.bridge-label').textContent = '→ Claude (offline)';
  }
});
```

The ping fires once at load; the button stays in offline state for the page lifetime even
if the bridge starts later (keeps it simple — reload the page to recheck).

## Verification Checklist

1. `preview.html` loads piece 069 without console errors; bridge button visible in sidebar.
2. With bridge server NOT running: button label reads "→ Claude (offline)", opacity ~0.45.
3. Start bridge: `python3.12 claude-work/scripts/preview_bridge.py`. Reload page.
4. Button label "→ Claude", full opacity.
5. Click button → label flashes "Sent ✓" for ~2 s, then returns to "→ Claude".
6. `claude-work/state/preview-dump.json` written; contains keys `piece`, `panelsFirst`,
   `foldState`, `_bridgeTimestamp`.
7. For 069: `panelsFirst.panels` has 11 entries; `foldState` has 10 keys (one per fold
   slider); `hingeTree.nodes` is a plain object (not `{}`).
8. For piece 071 (has cutouts): `cutouts` array is non-empty in the dump.
9. Sending while bridge is running, then stopping bridge and sending again → "Bridge offline"
   flash (2 s), button returns to "→ Claude".

## What NOT to Change

- The bridge server (`claude-work/scripts/preview_bridge.py`) — already correct, no edits.
- Any existing save/export/download buttons or their event handlers.
- The panels-first parser, fold slider construction, or any rendering logic.
- The sidecar load/save shape — `currentSidecar` is read-only from the bridge payload's
  perspective; don't change how it's written.

## Manual Tests (Alan, post-merge)

| Step | Expected |
|---|---|
| Open preview.html, bridge NOT running | Button shows "→ Claude (offline)", dimmed |
| Run `python3.12 claude-work/scripts/preview_bridge.py`, reload page | Button shows "→ Claude", full brightness |
| Load piece 069, press "→ Claude" | Terminal prints `[bridge] HH:MM:SS  preview-dump.json  (N KB)` |
| Claude reads `claude-work/state/preview-dump.json` | Panel IDs, fold state, sidecar visible |
| Load piece 071 (cutouts), press "→ Claude" | Dump has non-empty `cutouts` array |
| Bridge running; move a fold slider, press "→ Claude" | `foldState` in dump reflects moved slider |
