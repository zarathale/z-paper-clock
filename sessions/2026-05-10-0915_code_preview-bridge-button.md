---
date: 2026-05-10
start_time: "09:00"
end_time: "09:25"
mode: code
participant: Zarathale (Alan)
target: preview-bridge-button
orchestration_prompt: CODE_PROMPT_preview-bridge-button.md
---

## Goal

Wire the browser side of the local-loopback bridge: a one-press "→ Claude" button in `preview.html` that POSTs the current piece's parsed state to `claude-work/scripts/preview_bridge.py`, which writes the body to `claude-work/state/preview-dump.json` for Claude to read directly. Replaces the copy-paste console-dump workflow.

## What was done

**HTML.** New `<div id="bridge-row">` placed inside `#piece-section` between `#sidecar-block` and the closing `</div>`, so the button sits directly under the per-piece info block (above the dropzone). Single `<button id="bridge-btn">` with `<span class="bridge-label">→ Claude</span>` inside; inline styles match the existing dark sidebar palette (green-on-dark to read as a different action class than save/export).

**CSS.** Two feedback-state rules added to the `<style>` block near `#hint`:

```css
#bridge-btn.btn-ok  { background:#0a2a0a; color:#7fc97f; border-color:#4a8a4a; }
#bridge-btn.btn-err { background:#2a0a0a; color:#cf7f7f; border-color:#8a3a3a; }
```

**JS.** Three additions inside the bridge section:

1. `buildBridgePayload()` — collects current piece state into a clean serialisable object. Walks `parsed.panelsFirst` and converts the Maps (`panels`, `hingeTree.nodes`) to plain objects, strips DOM `element` references, and reduces `hingeTree` nodes to `{parent, foldId, children:[{childId, foldId}]}` so the inline fold object isn't duplicated against `folds[]`. Per-fold slider values come from `#per-fold-sliders .slider-row` (matching `savePoseBtn`'s traversal — `dataset.pathId` lives on the row, not the input). Includes the full `currentSidecar` JSON when loaded.

2. `sendToClaude(payload, name='preview')` — `fetch('http://localhost:7777/dump/${name}', POST, JSON)`. The `flash(text, cls)` helper toggles disabled state, swaps the label, and adds `btn-ok` / `btn-err` for ~2s before restoring the default. Catch handler flashes `'Bridge offline'` with `btn-err`.

3. Page-load ping at `/ping`. On rejection, dims the button (`opacity: 0.45`), updates the title to the run command, and rewrites the label to `'→ Claude (offline)'`. Per the prompt, this fires once at load — reload to recheck.

**Module-state plumbing.** Added `let currentSidecar = null;` near `currentAssembledFolds`, populated inside `maybeLoadSidecar`'s success path, and reset at the same three sites the existing assembled-pose state is reset (`maybeLoadSidecar` reset block, `loadSvgFromString`'s drag-drop / file-picker / cached-reload branch, and `loadScene`'s tear-down).

**.gitignore.** Added `claude-work/state/*-dump.json` so the runtime dump file (overwritten on every POST) doesn't get committed. The bridge server's `/dump/<name>` endpoint also writes named variants like `069-dump.json` if Alan ever wants to label them — covered by the same glob.

## Verification

Bridge server started in background; preview.html served via `python3.12 -m http.server 8770` and loaded headless against piece 069 then 071. All 9 verification checklist items from the orchestration prompt passed:

| # | Check | Result |
|---|---|---|
| 1 | piece 069 loads, no console errors, button visible | ✅ |
| 2 | bridge NOT running → label `→ Claude (offline)`, opacity 0.45 | ✅ |
| 3 | bridge starts, page reloads | ✅ |
| 4 | label `→ Claude`, full opacity | ✅ |
| 5 | click → `Sent ✓` flash for ~2s then return | ✅ (sampled at 50ms intervals; flash held through ≥600ms) |
| 6 | dump JSON has piece, panelsFirst, foldState, _bridgeTimestamp | ✅ |
| 7 | 069: panels=11, foldState=10 keys, hingeTree.nodes is plain object (11 entries) | ✅ |
| 8 | 071: cutouts array length 2 | ✅ |
| 9 | click while offline → `Bridge offline` flash for 2s | ✅ |

Sample piece-069 dump snapshot (truncated):

```
top-level keys: ['_bridgeTimestamp', 'cutouts', 'foldState', 'panelsFirst', 'piece', 'sidecar']
piece: 069
panels count: 11
folds count: 10
foldState keys: 10  (e.g. 'fold-taba-abc': -90)
hingeTree.nodes count: 11
hingeTree.root: abc
sidecar present: True
```

Headless verification only — no real-browser eyes-on. Preview tools confirm DOM + computed styles + click handlers, which is sufficient for this change (no rAF / TC dependencies).

## Branch / commit

Branch: `claude/preview-bridge-button` (renamed from auto-generated `claude/hungry-leakey-57577b` before first commit).

## Open questions

- The 2s flash callback unconditionally restores `'→ Claude'`, dropping the `(offline)` suffix even when the bridge was offline at page load. Matches the prompt's literal snippet, but means a failed click visually "promotes" the button back to looking online. Out of scope for this change; revisit if it becomes confusing in practice. Per-prompt design intent is "reload-to-recheck simplicity," so leaving as-is.
- Same-page bridge-up detection: the page-load ping is one-shot. If Alan starts the bridge after opening preview.html, the button stays in the offline state until reload. Could be polled later, but adds rAF/timer noise for a workflow that's already a quick `cmd-R`.

## Next-session handoff

The button is the unblock — Claude can now read `claude-work/state/preview-dump.json` whenever Alan presses it. Natural next pulls (per QUEUE.md):

1. PR-merge sweep: this PR + `claude/preview-html-bench-cluster-foundation` (PR A) + `claude/parser-marks-lookup` are all queued. After merge, do the manual visual check on PR A in a real browser (gizmo paint, TC handles, worktable).
2. Fix 068 fold authoring (missing `pane→c1` connection — the bridge button is now the easiest way to capture 068's panel/fold state and inspect it side-by-side with the SVG).
3. Pose capture for 067 (pivot-anchor reference), then 066, 065, 068.
