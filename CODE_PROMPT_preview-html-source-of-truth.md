---
status: ready-for-code
started: 2026-05-03
owner: Zarathale (Alan)
target: M0.6.14-preview-source-of-truth
---

## What You Are Doing and Why

`preview.html` currently loads SVGs only via drag-drop. With the 2026-05-03 filesystem restructure (`CODE_PROMPT_filesystem-restructure.md`), every piece has a canonical home at `work/pieces/NNN/NNN.svg`. The preview tool should know that — instead of always asking "drop a file on me," it should let you say "show me piece 69" and load the canonical export directly.

This unblocks the iterate-fast workflow: edit the `.af` in Affinity, hit Export, click Reload in preview.html — no file picker, no path guessing. Drag-drop stays as a fallback for inspecting SVGs outside the canonical tree (e.g. one-off experiments).

This is roadmap row M0.6.14.

## Prerequisites — confirm before starting

- `CODE_PROMPT_filesystem-restructure.md` has shipped — `work/pieces/NNN/NNN.svg` is the canonical export location for at least pieces 001, 065, 066, 067, 069, 070, 071, 072.
- `preview.html` exists at repo root and ships v1a + cut-layer + texture-flip + back-face-mirror + perf + thickness fix + axle rotation as of 2026-05-02.
- `work/pieces.csv` is the master list (123 rows, schema `id,plate,section,bucket,status,notes`).
- `preview.html` opens via `file://` (no dev server). `fetch()` of relative paths from a `file://` page works in Chrome only with `--allow-file-access-from-files`. Simpler workflow: `python3 -m http.server 8000` from repo root, open `http://localhost:8000/preview.html`. Document this in the side panel.

## Read These Files First

1. `work/SPEC-3D-VIEWER.md` "Authoring/QA preview tool" section — the "What it consumes" and "What's not yet there" → "Source-of-truth piece-id loader" bullet.
2. `preview.html` — the file you're modifying. Especially the existing drag-drop handler (`dragover` / `drop` listeners) and the parsed-SVG plumbing (the `parsed.{folds, axles, north, rootCentroid}` shape).
3. `ROADMAP.md` M0.6 task 0.6.14.
4. `work/pieces.csv` — for the piece-id list (used to populate the autocomplete / dropdown).

## Target File Structure Changes

```
preview.html                                ← UPDATE: piece-id input + Load + Reload + URL param + sidecar surfacing
```

Single-file change.

## Numbered Tasks

### 1. Add piece-id UI

In the existing side panel (above or alongside the drag-drop hint), add:

- A text `<input>` labeled "Piece" with a `placeholder="069 or 092a"` and `pattern="^\d{1,3}[a-z]?$"`.
- Optional: `<datalist>` of valid piece ids fetched from `work/pieces.csv` for autocomplete. Skip the datalist on first ship if it's awkward — the placeholder is enough hint.
- A "Load" button.
- A "Reload" button (disabled until a piece is loaded).

Keyboard:
- Enter inside the input → triggers Load.
- `R` keypress at the document level (when input is not focused) → triggers Reload (if a piece is loaded).

### 2. Implement `loadPieceById(rawId)`

```js
async function loadPieceById(rawId) {
  const m = String(rawId).trim().toLowerCase().match(/^(\d{1,3})([a-z]?)$/);
  if (!m) { showBanner('warn', `Bad piece id: ${rawId!r}`); return; }
  const id = String(parseInt(m[1])).padStart(3, '0') + m[2];
  const path = `work/pieces/${id}/${id}.svg`;
  let resp;
  try { resp = await fetch(path + '?t=' + Date.now()); }
  catch (e) { showBanner('warn', `fetch failed: ${e.message}. If on file://, launch Chrome with --allow-file-access-from-files or run python3 -m http.server.`); return; }
  if (!resp.ok) {
    showBanner('warn', `No SVG at ${path} — has it been authored yet? (HTTP ${resp.status})`);
    return;
  }
  const svgText = await resp.text();
  loadSvgFromString(svgText, { source: 'piece-id', pieceId: id });
  currentPieceId = id;
  document.querySelector('#reload-btn').disabled = false;
  history.replaceState(null, '', `?piece=${id}`);
  await maybeLoadSidecar(id);
}
```

Where:
- `loadSvgFromString` is a refactor of the existing drag-drop SVG-text-handling path. Extract the parser-feeding logic from the `drop` handler into this function so both paths use the same flow. Don't fork the parser.
- `showBanner('warn', message)` reuses the existing banner mechanism (yellow / red panels in the side panel).
- `currentPieceId` is a new module-level let.
- `maybeLoadSidecar` is task 4.

### 3. Implement `reloadCurrentPiece()`

```js
function reloadCurrentPiece() {
  if (!currentPieceId) return;
  loadPieceById(currentPieceId);  // re-fetch hits the cache-buster path
}
```

Wire to the Reload button click and the `R` keyboard shortcut.

### 4. Optional sidecar surfacing

```js
async function maybeLoadSidecar(id) {
  const path = `work/pieces/${id}/${id}.json`;
  try {
    const r = await fetch(path + '?t=' + Date.now());
    if (!r.ok) return;
    const json = await r.json();
    if (json.function) renderFunctionBlock(json.function);
  } catch { /* silent — sidecar is optional */ }
}
```

`renderFunctionBlock(fn)` shows a small read-only block in the side panel:

```
function:
  type: gear
  toothCount: 60
  pinionToothCount: null
  drives: 39
```

Skip the block entirely if the JSON has no `function` field. Keep this ≤ 30 lines of code.

### 5. URL-param auto-load

On page load, parse `window.location.search` for `?piece=NNN`. If present, call `loadPieceById(NNN)` automatically (after the page is interactive).

### 6. Banner: drag-drop outside canonical tree

When a file is dropped via the existing handler:

- If the dropped file's name matches `^(\d{3})([a-z]?)\.svg$` AND `currentPieceId` is unset OR doesn't match the dropped id, show a soft yellow banner: `Loaded ${name} via drag-drop. Canonical home is work/pieces/${id}/${id}.svg — consider exporting there for the iterate-fast workflow.`
- If the dropped file doesn't match the per-piece pattern (arbitrary SVG), no banner — the user explicitly wants ad-hoc inspection.

This is a soft nudge, not a block. Drag-drop continues to work the same way for any file.

Pass `{ source: 'drag-drop', pieceId: <inferred-or-null> }` into `loadSvgFromString` from this path.

### 7. Diagnostics

Add to the existing console-diagnostics block: `console.log('[preview] loaded via:', source, 'piece:', pieceId || '<none>');`

### 8. On-page documentation

Update the existing on-page README/help blurb (or the side panel's intro text) to mention:
- "Type a piece id (e.g. `069`) and press Enter, or drag-drop any SVG."
- "If loading by id fails on `file://`, run `python3 -m http.server 8000` from repo root and open `http://localhost:8000/preview.html`."
- "Reload re-reads from disk after a fresh export from Affinity."

Keep this terse — three lines max.

### 9. Session note + commit + PR

Write `sessions/YYYY-MM-DD-HHMM_code_preview-html-source-of-truth.md`. Front matter: `target: M0.6.14-preview-source-of-truth`, `orchestration_prompt: CODE_PROMPT_preview-html-source-of-truth.md`.

Branch: `claude/M0.6.14-preview-source-of-truth`. Commit subject: `preview.html: piece-id loader, reload, sidecar surfacing`. PR per CLAUDE.md.

Flip THIS prompt's `status` to `shipped`, add `shipped: YYYY-MM-DD`, add the italic header.

Update ROADMAP.md M0.6.14 row from `ready-for-code` → `done` and add the closing-session-note pointer in Notes.

## Verification Checklist

1. Open `preview.html` (or via `python3 -m http.server` if `file://` fetch is blocked); type `69` in the piece input + Enter — `work/pieces/069/069.svg` loads, page URL updates to `?piece=069`.
2. Click Reload — preview re-fetches with cache-buster (verify in the network panel).
3. Type `999` (a non-existent piece) — yellow banner says `No SVG at work/pieces/999/999.svg`.
4. Open `preview.html?piece=066` directly — auto-loads 066.
5. Drag-drop a non-canonical SVG (e.g. an old export) — still works; soft banner appears suggesting canonical location IF the filename matches `NNN.svg`.
6. If `work/pieces/069/069.json` exists with a `function` block, side panel surfaces it.
7. Console log shows `loaded via: piece-id` (or `url-param` / `drag-drop`).
8. No regressions on existing render paths — silhouette, thickness, axle rotation, north sphere, scan texture all behave as before.
9. `R` keyboard shortcut triggers Reload (when input not focused, when a piece is loaded).

## What NOT to Change

- Don't touch the parser (silhouette source chain, fold extraction, axle parsing, scan-image transform reading).
- Don't touch the render pipeline (slab build, scan texture, axle wires, north sphere).
- Don't add a build step. Stays single-file HTML.
- Don't pre-fetch every piece on load. Only fetch what the user asked for.
- Don't write back to the SVG. Read-only.
- Don't try to make `localStorage` remember the last-viewed piece — `?piece=NNN` URL is the bookmark surface.

## Manual tests

| Test | Expected |
|---|---|
| Type `69` + Enter | 069 loads, URL becomes `?piece=069` |
| Re-export 069 from Affinity, click Reload | preview updates with new geometry |
| Visit `?piece=066` | 066 auto-loads |
| Press `R` | Reload triggers (if a piece is loaded) |
| Drag-drop arbitrary SVG | works as before, no per-piece banner |
| Drag-drop a `070.svg` from outside the canonical tree | works, soft "consider canonicalizing" banner |
