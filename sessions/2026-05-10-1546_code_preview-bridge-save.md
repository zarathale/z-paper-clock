---
date: 2026-05-10
start_time: "15:46"
end_time: "TBD"
mode: code
participant: Zarathale (Alan)
target: preview-bridge-save
orchestration_prompt: CODE_PROMPT_preview-bridge-save.md
---

# Goal

Eliminate the copy/paste sidecar-merge step from the assembled-pose save workflow by
adding a `/save` endpoint to `preview_bridge.py` and wiring `preview.html` to POST
directly. Persistence-on-reload becomes free; auto-save on Bench-mode piece switch
prevents losing in-progress fold work when scrolling through the queue.

# What was done

**`claude-work/scripts/preview_bridge.py`**
- Added `POST /save` endpoint via a new `_handle_save()` helper.
- Reads existing sidecar at `work/pieces/<numeric>/<piece-id>.json` (handles letter
  variants by routing `092a` → `work/pieces/092/092a.json`); replaces only the
  `assembled` block; preserves every other top-level field; stamps `_savedAt` for
  diff legibility.
- Returns `400 bad json`, `400 missing piece or assembled`, or `400 piece id has no
  digits` for the three input-validation cases. CORS headers identical to `/dump`.
- Module docstring extended with the new endpoint.

**`preview.html`** (single inline script block, all changes within it)
- New helpers near the existing save block: `saveViaBridge(assembled, pieceId)` (POST
  → `/save`, returns boolean for caller fallback decision); `flashBtn(btn, label,
  cls)` (plain-text confirmation flash, distinct from the bridge button's
  label-in-span flash); `buildBenchAssembled()` (extracted from the inline save
  handler, returns the inner `assembled` block for both manual save and auto-save);
  `assembledIsIdentity(assembled)` (skip-guard for auto-save when nothing meaningful
  has been touched); `maybeSaveCurrent()` (Bench-mode-only auto-save hook).
- Bench `savePoseBtn` handler refactored to `async`: build assembled → try bridge →
  flash "Saved ✓" on success, fall back to existing `showAssembledPoseModal` on
  bridge offline. The modal path still works for users who don't run the bridge.
- Cluster `saveSelectedBtn` handler refactored to `async`: same pattern. Build the
  full `payload` (with `folds`, `transform`, `snapped_connections`) as before, then
  POST `payload.assembled` to the bridge with modal fallback.
- `loadPieceById` gains a one-line auto-save hook: when `id !== currentPieceId`,
  `await maybeSaveCurrent()` before fetching the new SVG. Reload (same id) skips
  the auto-save by design.

**Verification (code-side, per CLAUDE.md two-tier protocol)**
- Python AST + import check on the modified bridge: passes.
- In-process unit test of `_handle_save` against a temp REPO_ROOT: confirms
  top-level field preservation, `assembled` replacement, `_savedAt` stamping, letter
  variant routing (`092a`), and all three 400-error paths.
- `node --check` on extracted JS modules from `preview.html` (single inline
  `<script>` block): passes.
- Ripgrep audit confirms all five new symbols defined and referenced consistently;
  no stale references to the old inline save logic.

Browser-side checks (run live preview.html, click both save buttons with bridge on
and off, reload to confirm persistence, switch Bench pieces with unsaved folds)
deferred to Manual tests in the PR body for Alan to run post-merge — Code does not
start an HTTP server during verification per project convention.

# Branch / commit

Branch: `claude/preview-bridge-save` (renamed from auto-generated
`claude/frosty-mcclintock-44bd09` before first commit per CLAUDE.md branch-naming
rule).

Commit SHA: see PR.

# Open questions

None. The bridge endpoint is content-addressable (POSTs the full `assembled` block,
bridge merges atomically) so concurrent saves from two open tabs would race only on
the `_savedAt` stamp — last write wins, which matches the existing manual workflow.
If multi-tab editing becomes a real workflow, we can add a sidecar-version field
later; not in scope here.

# Next-session handoff

After Alan merges and runs the browser checks, the workflow shift to "save
everything" can drive the next pass: with auto-save free, Cluster-mode interactions
(snap, drag) could persist on every change instead of only on explicit save. Out of
scope for this PR — flag it for a future Cowork session if Alan wants to pull it
forward.
