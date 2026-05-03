---
date: 2026-05-04
start_time: "00:30"
end_time: "00:30"
mode: code
participant: Zarathale (Alan)
target: M0.6.14-preview-source-of-truth
orchestration_prompt: CODE_PROMPT_preview-html-source-of-truth.md
---

## Goal

Ship the source-of-truth piece-id loader for `preview.html` so the iterate-fast workflow becomes type-id-and-press-Enter, with drag-drop retained as a fallback.

## What was done

Single-file change: `preview.html`. No parser or render-pipeline edits.

Added (above the existing dropzone in the side panel):

- A `Piece` text input with `placeholder="069 or 092a"` and `pattern="^\d{1,3}[a-z]?$"`.
- A `<datalist>` populated from `work/pieces.csv` on bootstrap (best-effort; silent on `file://` fetch failure).
- `Load` button → triggers `loadPieceById(pieceInput.value)`.
- `Reload` button (initially disabled) → re-fetches the current piece from disk with a cache-buster query string.
- Optional read-only sidecar block that surfaces a `function` field from `work/pieces/NNN/NNN.json` if present.

Added (script):

- `loadSvgFromString(text, opts)` — extracted from the old `onFileLoaded` so drag-drop / file-picker / piece-id / URL-param / cached-reload paths all share one parse-and-render call.
- `loadPieceById(rawId, source = 'piece-id')` — normalises any of `69`, `069`, `92a`, `092a`, `92A` → `NNN[a]`; `fetch('work/pieces/${id}/${id}.svg?t=' + Date.now())`; sets `currentPieceId`, enables the Reload button, updates the URL via `history.replaceState` to `?piece=${id}`. Banners on bad id, fetch failure (with the `file://` workaround instructions), or 404.
- `reloadCurrentPiece()` — re-calls `loadPieceById` with `source='piece-id-reload'`. Wired to the Reload button and to a document-level `keydown` handler for `r` / `R` (no-op when the piece input is focused or any modifier key is held).
- `maybeLoadSidecar(id)` + `renderFunctionBlock(fn)` + `hideSidecarBlock()` — best-effort; silent on missing JSON or missing `function` field.
- `populatePieceDatalist()` — pulls the id column out of `work/pieces.csv` into the `<datalist>`.

Bootstrap:

- `populatePieceDatalist()` runs once on page load.
- `?piece=NNN` is parsed from `location.search` and triggers `loadPieceById(rawId, 'url-param')`.

Drag-drop:

- Existing handler routes through the new `loadSvgFromString` with `source='drag-drop'`.
- If the dropped filename matches `^(\d{3})([a-z]?)\.svg$` AND the canonical loader isn't tracking that id, a soft yellow banner suggests the canonical home (`work/pieces/${id}/${id}.svg`). Arbitrary SVGs (no per-piece pattern) drop without the banner.

Diagnostics:

- Every load path emits `console.log('[preview] loaded via:', source, 'piece:', pieceId || '<none>')`. Sources: `piece-id`, `piece-id-reload`, `url-param`, `drag-drop`, `file-picker`, `cached-reload`.

On-page help:

- Added a three-line `<div id="help">` blurb at the bottom of the side panel covering id-load, the `python3 -m http.server` workaround, and Reload / `R`.

Operations-side:

- Created `.claude/launch.json` for `mcp__Claude_Preview__preview_start` to spin up `python3 -m http.server 8770` against the worktree root.

## Verification

Live-tested via Claude Preview against `python3 -m http.server` on port 8770. Pieces fetched out of `work/pieces/NNN/NNN.svg`. Console log assertions captured the diagnostic lines.

| Test | Result |
|---|---|
| `loadPieceById('69')` | `currentPieceId=069`, `pieceInput.value=069`, `?piece=069`, polygon parsed, no errors |
| `loadPieceById('66')` | `currentPieceId=066`, full face graph (32 regions, 19 fold edges) renders |
| `loadPieceById('999')` | yellow banner: `No SVG at work/pieces/999/999.svg — has it been authored yet? (HTTP 404)`; `currentPieceId` unchanged |
| `loadPieceById('xyz')` | yellow banner: `Bad piece id: "xyz" — expected NNN or NNNa (e.g. 069, 092a).` |
| `?piece=001` URL load | `currentPieceId=001`, input value populated, Reload enabled, render OK |
| `loadBtn.click()` with `pieceInput.value='67'` | `currentPieceId=067`, URL → `?piece=067` |
| `Enter` keydown in pieceInput with `'70'` | `currentPieceId=070`, URL → `?piece=070` |
| `R` keydown with input not focused, after a piece is loaded | console shows `[preview] loaded via: piece-id-reload piece: 070` |
| `R` keydown with input focused | no-op (`currentPieceId` unchanged) |
| Drag-drop simulation of `069.svg` while `currentPieceId=067` | soft canonical-home banner appears |
| Drag-drop simulation of `random-experiment.svg` | no piece-banner (correct) |
| Datalist | 123 options populated from `work/pieces.csv` |

No regressions on existing render paths: silhouette, thickness, axle rotation, north sphere, scan texture, fold-graph, slab build all behave as before.

## Branch / commit

Branch: `claude/M0.6.14-preview-source-of-truth` (renamed from auto-generated `claude/agitated-volhard-84f12d` before first commit, per CLAUDE.md).

Base: `8a8ab50` (merge of `claude/filesystem-restructure`).

Commit (this session): see PR.

## Open questions

None. M0.6.14 is closed; the loader is feature-complete for the iterate-fast workflow. Next M0.6 row in the roadmap is M0.6.9 (v1b face-graph + hinge animation), which is independent of this change.

## Next-session handoff

- Try `python3 -m http.server 8000` from repo root, open `http://localhost:8000/preview.html?piece=069`, hit Reload after re-exporting the `.af` from Affinity to confirm the iterate-fast loop end-to-end.
- If the loader feels usable, the next `preview.html` track is M0.6.9 (v1b polygon-cut + adjacency-BFS + hinge animation) — orchestration prompt already authored at `CODE_PROMPT_preview-html-v1b.md`.
- Filesystem-restructure pass already completed yesterday; nothing else needed before M0.6.9 is unblocked.
