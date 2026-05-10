---
date: 2026-05-10
start_time: "16:31"
end_time: "16:45"
mode: code
participant: Zarathale (Alan)
target: preview-html-guided-stepper
orchestration_prompt: CODE_PROMPT_preview-html-guided-stepper.md
---

## Goal

Ship the guided assembly stepper for `preview.html` Cluster mode per
`CODE_PROMPT_preview-html-guided-stepper.md`.

## What was done

`preview.html` only — no other repo files modified. Twelve tasks from the prompt landed
in a single editing pass.

- **Topbar**: added `#guidedToggleBtn` ("Guide") after the existing Snap button inside
  `#cluster-controls`. CSS `.active` rule mirrors the snap-button green palette
  (`#3a5a3a` / `#c8e8c8` / `#5a8a5a`).
- **Cluster panel**: inserted `#guided-panel-section` (hidden by default) between the
  save/deselect button row and the Measurements header. Contains the section header
  + `#guided-counter`, the `#guided-step-card` content surface, and Prev / Done ✓ /
  Skip buttons.
- **Step-card CSS**: `.step-type-badge` + per-type color-map classes
  (`badge-add-piece` / `-fold` / `-glue-self` / `-glue-cross` / `-glue-no` /
  `-lock-shape` / `-snap-connection` / `-check` and a fallback bucket for
  `-install-bearing` / `-insert-axle` / `-orient` / `-pin`).
  `.step-desc` / `.step-human` / `.step-quote` / `.step-action-btn` shaped per the
  prompt.
- **State**: `let guidedMode`, `let guidedSequence`, `let guidedStepIndex` added
  near the snap-state block.
- **JS surface** (inserted after `setSnapMode`):
  - `loadGuidedSequence(clusterName)` — fetches `claude-work/state/guided_sequence_<name>.json`
    with cache-buster; banner-warns on failure.
  - `setGuidedMode(on)` — gates on `currentClusterName` being a named cluster (not
    `<ad-hoc>`), loads the sequence, toggles button + panel, renders + applies
    behavior.
  - `currentGuidedStep` / `guidedTotalSteps` / `advanceGuidedStep` /
    `retreatGuidedStep` / `markGuidedStepDone`.
  - `renderGuidedPanel` — draws badge, pieces label
    (`from → to` for snap-connection, `+`-joined otherwise), description, human-note
    when `requires_human`, source quote, and the add-piece action button. Disables
    Done ✓ for add-piece steps whose piece is not yet in the scene.
  - `escHtml` — minimal module-scope HTML escaper (distinct from the local
    `escapeHtml` inside `showAssembledPoseModal`).
  - `applyGuidedStepBehavior` — highlights `ui.highlight_pieces`, auto-activates
    snap tool for `snap-connection` steps, selects the piece for `fold` steps,
    falls back to `select` tool for all other types.
  - `highlightGuidedPieces` / `clearGuidedHighlights` — warm-amber emissive on
    highlighted pieces, neutral on the rest.
  - `showGuidedConfirmModal` — Promise-based DOM-rendered confirm modal for
    `lock-shape` Done ✓ presses.
- **Auto-advance hooks**:
  - `snapAllPairs` tail: after the existing `requestRender();`, checks if the
    current guided step is a `snap-connection` whose `from_piece`/`to_piece`
    match the snapped pair (via `snapNormId`), and advances if so.
  - `loadClusterPieces` tail: re-renders the panel + re-applies behavior if
    guided mode is on (so add-piece steps update from "Add piece" to "✓ in scene"
    automatically).
  - `teardownClusterScene`: calls `setGuidedMode(false)` if guided is active.
    Covers the Bench-mode-switch path automatically via `setMode`'s existing
    teardown call.
- **Button wiring**: Guide toggle, Prev, Done ✓ (with lock-shape modal flow), Skip
  added alongside the existing cluster-controls listeners (the IIFE at the
  bottom of the file).

## Verification (code-side)

- `node --check` on the extracted inline `<script>` block (lines 492–7566) —
  no syntax errors.
- Brace balance: 1418 open / 1418 close.
- All 14 named guided symbols present (62 ripgrep matches).
- `guidedCompleted` does NOT appear (dead state confirmed absent).
- All 7 DOM ids present (24 references).
- `^function escHtml` appears exactly once at module scope.
- `setGuidedMode(false)` present in `teardownClusterScene`.
- "Guided stepper" auto-advance markers: 6 matches (covers `snapAllPairs` +
  `loadClusterPieces` + class headers).
- Non-snap step snap-mode exit present:
  `if (clusterInteractionMode === 'snap') setClusterTool('select');`

Browser-side checks (Guide button visibility, modal flow, snap auto-advance,
amber highlighting, Bench switch teardown) intentionally not run from Code —
the worktree-vs-repo-root server path mismatch makes that unreliable. Listed
under the prompt's Manual tests section for Alan post-merge.

## Branch / commit

Branch: `claude/preview-html-guided-stepper` (renamed off auto-generated
`claude/gallant-colden-5dcfbe` before the first commit, per CLAUDE.md branch-naming
rule).

Commit SHA: TBD (filled by commit step).

## Open questions

None — the guided stepper covers the full schema in `guided_sequence_anchor.json`
(13 step types, popup_title/body/confirm/cancel on lock-shape, source_quote,
requires_human+human_note). Browser-side verification is the only thing
deferred to post-merge, and it's the standard cluster-of-tests pattern from
the prompt's Manual tests section.

## Next-session handoff

Alan to merge the PR, pull `main`, and run the 10 browser-side manual tests
from the prompt's Manual tests block. Likely follow-ups based on what surfaces:

- A second cluster's guided sequence (mechanism §II.B is the obvious next one).
- "Lock-shape" actually freezing the piece (vs. just confirming the popup) is
  out-of-scope here but a natural next track.
- Per-step `depends_on` enforcement (skip button currently never blocks).
