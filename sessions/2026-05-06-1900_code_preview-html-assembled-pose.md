---
date: 2026-05-06
start_time: "19:00"
end_time: "19:00"
mode: code
participant: Zarathale (Alan)
target: preview-html-assembled-pose
orchestration_prompt: CODE_PROMPT_preview-html-assembled-pose.md
---

## Goal

Implement `CODE_PROMPT_preview-html-assembled-pose.md` (drafted by Cowork the same day, see `sessions/2026-05-06-1520_cowork_assembled-pose-and-inferred-connections.md`): make the preview load + save per-fold assembled pose data via the JSON sidecar's `assembled.folds` block. On load: each per-fold slider initialises to the sidecar value (precedence `assembled.folds[id]` > fold-id `-<deg>` suffix > 0) and the geometry rotates to the assembled pose immediately. On save: a "Save assembled pose" button captures the current slider state into a JSON snippet for Alan to copy/download and merge by hand.

This is the preview-side companion to DECISIONS #11.

## What was done

Six families of changes in `preview.html`:

- **State plumbing.** New module-level `currentAssembledFolds` (line 254-260) — the loaded sidecar's `assembled.folds` map for the current single-piece load, or null. Reset to null on `loadScene` teardown alongside `currentPieceId`. Drag-drop / file-picker / cached-reload paths in `loadSvgFromString` also clear it (those paths bypass the piece-id loader, so without this the prior piece's saved pose would leak into the new SVG's slider defaults).
- **`maybeLoadSidecar` extended.** Reads `json.assembled.folds` and stashes it into `currentAssembledFolds` if present and is an object. The existing `function`-block handling is unchanged. Resets `currentAssembledFolds = null` first thing so a missing-block sidecar (just `function`, no `assembled`) clears any stale value.
- **`loadPieceById` reorder (Option A).** `await maybeLoadSidecar(id)` now runs BEFORE `loadSvgFromString(...)`, so `currentAssembledFolds` is populated by the time `renderPanelsFirstScene` builds per-fold sliders. One-line move; comment added explaining why.
- **`renderPanelsFirstScene` slider build.** New precedence chain for slider initial value: `assembled.folds[fold.id]` (literal id, sidecar) > `fold.defaultAngle` (fold-id `-<deg>` suffix) > 0. Malformed sidecar values (NaN, non-numeric) emit a `console.warn` naming the fold-id and the offending value, then fall through to default-angle precedence. The slider's `value` attribute and the displayed `°` text both reflect the initial. When initial != 0, the existing fold-rotation code runs once at build time so the piece appears in its assembled pose at load. The per-slider `input` listener is unchanged. A `fromSidecar[]` accumulator emits one console line per piece summarising which fold ids loaded from the sidecar (`[panels-first] assembled.folds applied: 2 folds: fold-main-ai=-45°, fold-main-bh=90°`). Scene mode is intentionally opted out — `assembledMap` is gated on `!sceneMode`; comment explains.
- **Save assembled pose UI.** New `#save-pose-row` row inside `#fold-controls`, just below `#per-fold-sliders`, containing one `#savePoseBtn`. Visibility logic: `style.display = ''` when (single-piece mode AND `pathHingeMap.size > 0`); `none` otherwise. Set inside `renderPanelsFirstScene` (after the slider loop), and explicitly hidden in `renderSceneMulti` (scene teardown) and the legacy cut-line-first body of `renderScene`. Button click handler builds a payload of the form `{ assembled: { folds: {...}, captured: <iso>, note: "" } }` from every panels-first slider's current `value` (rounded to 2 decimals, finite-only), and opens a modal via `showAssembledPoseModal`. Modal contents: a readonly textarea with the JSON, plus "Copy to clipboard", "Download `<piece>.assembled.json`", and "Close" buttons. Copy uses `navigator.clipboard.writeText`; Download builds a Blob + temporary anchor + `URL.revokeObjectURL`. Defensive: bails with a banner if `currentPieceId` isn't set or there are no slider rows.
- **Scene-mode regression hold.** `renderSceneMulti`'s teardown block hides `#save-pose-row` upfront (so a single-piece load → scene load doesn't leave the button visible). The per-piece `renderPanelsFirstScene` call inside scene mode also sees `sceneMode=true` and skips the assembled.folds map.

### Verification

Per the prompt's Verification Checklist, all run from the worktree against piece 069 (the panels-first reference piece, 10 valley folds):

| # | Check | Result |
|---|---|---|
| 1 | Baseline: no sidecar, `?piece=069` | ✓ All 10 sliders at 0°, no rotations applied (`rotatedHingeCount: 0`), save-pose-row visible. |
| 2 | Sidecar with `{"folds": {"fold-main-bh": 90, "fold-main-ai": -45}}` | ✓ Sliders initialise to 90° and -45° respectively (text + value + dataset); other 8 stay at 0°. Hinge quaternions confirm geometry rotated (`fold-main-bh` quaternion → 90° axis-angle, `fold-main-ai` → 45°). Console line `[panels-first] assembled.folds applied: 2 folds: fold-main-ai=-45°, fold-main-bh=90°` fires. |
| 3 | Save round-trip | ✓ Scrub `fold-main-g` to 60°, click "Save assembled pose"; modal opens with payload containing all 10 fold entries (the test sidecar's 90/-45 + fold-main-g: 60 + zeros for the rest), `captured: <iso8601>`, `note: ""`. Copy and Download buttons present. Close works. |
| 4 | Affinity `_`-prefix fold ids on piece 095 | ✓ Sidecar `{"_1-fold-pane3-pane4": 180, "_2-fold-pane2-pane3": 90}` → both sliders pick up the values; literal id (with underscore) is the key. |
| 5 | Malformed sidecar value | ✓ `{"fold-main-bh": "not a number"}` → slider falls through to 0° (no `defaultAngle` on this fold), `console.warn` fires with `[panels-first] assembled.folds["fold-main-bh"] is not a finite number: not a number — falling through to default-angle precedence.` No crash. |
| 6 | Both `function` AND `assembled` blocks | ✓ Sidecar `{"function": {"teeth": 60, "drives": "070"}, "assembled": {"folds": {"fold-main-bh": 75}}}` → `function:` block surfaces in side panel as `function:\n  teeth: 60\n  drives: "070"`; `fold-main-bh` slider initialises to 75°. |
| 7 | Scene mode unaffected | ✓ `loadScene('065,066,067,068,069')` → 48 sliders all initialised at 0° regardless of any sidecar's assembled.folds (scene mode opted out); save-pose-row hidden (`display: none`, `offsetParent: null`). `currentPieceId` nulled. |
| 8 | R-key reload | Inherited via `reloadCurrentPiece()` which calls `loadPieceById(id, 'piece-id-reload')` — same code path validated by Verification #2 (`reloadCurrentPiece`-driven reload). Cache-busted via existing `?t=Date.now()`. |
| 9 | Sidecar deletion + reload | ✓ Delete the test sidecar, `reloadCurrentPiece()` → `currentAssembledFolds: null`, all 10 sliders back to 0°, no errors. |

All temporary test sidecars (`work/pieces/069/069.json`, `work/pieces/095/095.json`) deleted after their respective verification runs; `git status --short` after verification shows only `M preview.html`.

## Branch / commit

- Branch: `claude/preview-html-assembled-pose` (renamed from auto-name `claude/gallant-hermann-99bad7` before first commit per CLAUDE.md).
- Commit: TBD (see end-of-session output).

## Open questions

None blocking. Two intentional v1 limitations carried forward to follow-ups:

1. **Scene-mode assembled poses.** v1 single-piece only. Per-piece assembled poses applied independently across a scene is a follow-up — when it lands, `currentAssembledFolds` will need to grow into a per-piece map keyed by `_sceneId`.
2. **Inter-piece assembled transforms.** Where each piece sits in 3D space relative to its neighbours when folded — M4 work. v1's `assembled.folds` only covers one piece's internal fold geometry. The two compose later: per-fold settles internal geometry; per-edge transform settles placement.

## Next-session handoff

- This branch is ready for review and merge. After merge, no follow-up Code task is queued from this prompt. Alan can start authoring `assembled.folds` blocks immediately by loading a piece, scrubbing sliders to the assembled pose, clicking Save, copying the JSON, and pasting it into `work/pieces/NNN/NNN.json`. Pieces with both `function` and `assembled` blocks coexist cleanly.
- The companion `CODE_PROMPT_build-assembly-graph-inferred.md` (DECISIONS #10) shipped earlier the same day in PR #18. The two sidecar extensions (`connections.inferred[]` and `assembled.folds`) are now both wired through their respective consumers.
