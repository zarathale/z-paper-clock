---
name: piece-scan-ingest
description: Audit the per-piece source archive (`source/pieces/`) and chunk archive (`source/scans-chunks/`) against the master piece list (`work/pieces.csv`) for the z-paper-clock build. Read-only — never modifies `pieces.csv` or anything under `source/`. Use this skill whenever Alan asks about chunk-and-crop ingest status, audits the piece archive, asks what pieces are still pending or missing, asks which chunks contain a given piece, asks to validate piece-scan filenames, asks for a captured-vs-pending count, or wants a status check after a scanning or cropping session. Trigger on phrasings like "ingest pieces," "audit pieces," "what's still missing," "where am I in chunk-and-crop," "check the piece archive," "is everything captured," "what's left to scan," or "did the rename land." Also offer this skill proactively at the end of any Cowork session that touched `inbox/`, `source/pieces/`, or `source/scans-chunks/`.
---

# Piece-Scan Ingest

Audits the chunk-and-crop source archive for the z-paper-clock build. Reports captured-vs-pending status, image-health warnings, and surfaces which chunk files could feed each still-pending piece. Read-only by design — the audit is an observer, not an authority.

## Why this skill exists

Under the chunk-and-crop onboarding model (settled 2026-04-30; see `CLAUDE.md` Architectural Decisions table), `source/pieces/NNN.png` is the canonical pipeline input. Alan captures multi-piece chunks on a flat-bed scanner, hand-crops them in his image editor, and the per-piece PNGs feed `02-trace.py` directly. This skill is the audit that closes the loop: it tells Alan which pieces are done, which are still pending, and which chunks could be the source for the pending ones.

It exists separately from `04-validate-sidecars.py` (which lints SVG sidecars in `work/pieces/`) — that's about derivative artifacts; this skill is about source archive completeness.

## What this skill does

1. Reads the master list from `work/pieces.csv`. Expected: 123 piece IDs (1–121 contiguous, plus 092a and 112a).
2. Walks `source/pieces/` for files matching `^\d{3}[a-z]?\.png$` (e.g., `004.png`, `092a.png`).
3. Walks `source/scans-chunks/` for files matching the four chunk filename patterns from `source/SCAN-INTAKE-CHECKLIST.md`:
   - `NN_NN_NN.{jpeg,png}` — multi-piece chunks listing complete pieces inside, ascending
   - `NN.{jpeg,png}` — single-piece chunks
   - `NN_NN_l.jpeg` / `NN_NN_r.jpeg` — left/right partials pre-stitching
   - `NN_NN_stitched.png` — stitched composites (always PNG)
4. Runs tiered checks per file (see "Health checks" below).
5. Cross-references chunk filenames against pending pieces — for each pending piece, lists which chunks contain it.
6. Prints a structured markdown report to stdout. Exits 0 if no BLOCK errors; non-zero otherwise.

## Health checks (tiered)

The audit is strict about the things that break downstream and lenient about the things that are merely cosmetic. The whole point of the tiered model is to keep the audit useful — a single warning on every piece would be noise.

**BLOCK errors** (audit fails; non-zero exit):

- File unreadable (corrupt PNG, zero-byte file, permission error)
- Filename does not match the canonical pattern for its folder
- Piece ID parsed from a filename is not present in `work/pieces.csv` (typo, misread, or a piece the master list missed — pause and verify before adding to the archive)

**WARN issues** (audit passes; warnings listed):

- DPI metadata missing or below 600 (the `SCAN-INTAKE-CHECKLIST.md` standard)
- Image dimensions less than 400 px on either axis (probably a mis-crop; gen-2 piece crops are typically 600–4000 px wide depending on piece)
- Color mode not RGB or RGBA (grayscale or palette mode is unexpected; bleed-through detection in any future pre-processing pass uses chroma)
- File size suspiciously small (< 50 KB for `source/pieces/`; might indicate an empty or near-empty image)

The thresholds are deliberately loose — gen-2 capture is new and we don't want the audit fighting Alan over edge cases. Tighten or relax based on real-world findings; the skill is allowed to evolve.

## How to run

The audit is implemented as a Python helper bundled with this skill. Run from the repo root:

```bash
cd ~/Documents/GitHub/z-paper-clock
.venv/bin/python .claude/skills/piece-scan-ingest/scripts/audit.py
```

The helper:

- Auto-detects the repo root via `git rev-parse --show-toplevel` (so it works from any subdirectory)
- Uses Pillow for image-header inspection (already in `.venv`; no full-image pixel decode needed for DPI/dims/mode)
- Has no network access, no file writes, no destructive operations
- Accepts an optional `--json` flag to emit JSON instead of markdown (for programmatic consumption; not needed for the chat-render flow)

If `scripts/audit.py` is not present, the helper hasn't been authored yet. Tell Alan:

> The piece-scan ingest helper hasn't been authored yet — see `CODE_PROMPT_M0.5.2-piece-scan-ingest.md` at the repo root for the open Code session.

…and stop. **Do not attempt to inline the audit in chat** — the cross-referencing and image-header inspection is fiddly enough that hand-rolling it leads to subtle errors, and the helper is the source of truth for the algorithm. A missing helper is a known M0.5.2 state, not a problem to work around.

## Report structure

Render the helper's stdout to chat verbatim — it's already markdown-formatted. The expected sections in order:

1. **Summary** — captured / pending / total counts; BLOCK and WARN counts
2. **BLOCK errors** (if any) — file path, error type, brief explanation
3. **WARN issues** (if any) — file path, warning type, the actual value vs. expected
4. **Pending pieces** — grouped by plate, with chunk-source suggestions where the piece appears in a chunk filename
5. **Chunk inventory** — each chunk listed with the pieces it claims to contain
6. **Footnote** — if `inbox/` has files (informational only; not a warning)

After rendering the report, add a one-line takeaway line addressed to Alan. Examples:

- "All 123 pieces captured; 0 BLOCK / 0 WARN. M0.5.4 done — ready to flip the status column and move to M0.5.6."
- "47 of 123 pieces captured. 2 BLOCK errors and 4 WARNs. Address the BLOCK errors before resuming cropping."
- "12 pending pieces have a chunk source identified — the rest need new captures. Plate F is the gap."
- "Archive empty as expected — first audit run. 8 chunks queued; 19 pieces have a chunk source identified."

The takeaway is the user-facing read; the body is reference detail.

## What this skill never does

- **Never edits `work/pieces.csv`.** Status flips (`pending` → `captured` → `traced`) are deliberate decisions, not derived from filesystem presence. They land in a separate, intentional commit when Alan decides a milestone closes.
- **Never deletes or moves files** in `source/pieces/`, `source/scans-chunks/`, or `inbox/`. The audit is read-only by contract.
- **Never re-captures or re-crops.** Those are manual steps Alan owns at the scanner and in his image editor.
- **Never trusts content over filenames.** Every ID it cites must come from a parsed filename or `pieces.csv`. No OCR over image content; the filenames are the declared truth.
- **Never blocks on cosmetic issues.** A missing DPI tag or a small dimension is a WARN, not a fail. The build can still proceed.

## Edge cases to handle gracefully

- **Empty `source/pieces/`** — valid early state. Report 0 captured, 123 pending, no errors. Mention it's the expected first-run state.
- **Letter variants** — `092a.png` and `112a.png` are real and expected per `pieces.csv`. Never flag them as anomalies.
- **Unknown IDs in chunk filenames** — BLOCK error. The book's piece set is finite and known; an unknown ID is a typo or misread that needs manual review.
- **Multiple chunks containing the same piece** — fine and useful. Report all chunks per pending piece (the spare ones are alternate sources).
- **`inbox/` has files** — informational footnote only. Lingering inbox files are an in-flight signal (M0.5.3 active), not a problem; the audit notes them so Alan knows the loop isn't fully drained.
- **`.DS_Store` and other macOS cruft** — ignore quietly; not worth a line in the report.
- **Symlinks, hidden files, dotfiles** — ignore quietly; the audit only looks at canonically-named files.

## Trigger examples

These are realistic phrasings that should trigger this skill:

- "Run the ingest skill"
- "Audit my piece archive"
- "What's still pending in chunk-and-crop?"
- "Did piece 31 land?"
- "Which chunks contain piece 92?"
- "How far am I in M0.5.4?"
- "Is the source archive complete?"
- "Check the filenames in `source/pieces/`"

These are near-misses that should NOT trigger this skill (they touch the same domain but want different work):

- "Trace the pieces" → that's `02-trace.py`, M2 work, not this skill
- "Validate the sidecars" → that's `04-validate-sidecars.py`, derivative artifacts
- "Re-scan plate D" → manual hands-on work; this skill audits but doesn't direct capture
- "What does the master list look like?" → that's just reading `pieces.csv`; the skill is overkill

## Notes for the helper (`scripts/audit.py`)

The Python helper is authored in a separate Code session — see `CODE_PROMPT_M0.5.2-piece-scan-ingest.md` at the repo root. Its contract:

- **Inputs:** none (auto-detects repo root via `git rev-parse --show-toplevel`)
- **Reads:** `work/pieces.csv`, `source/pieces/*`, `source/scans-chunks/*`, `inbox/*` (for the footnote)
- **Writes:** nothing to disk
- **Stdout:** markdown report, sections per "Report structure" above
- **Exit code:** 0 if no BLOCK errors; non-zero (1) otherwise — for CI compatibility down the road
- **Dependencies:** Pillow (already in `.venv`); standard library otherwise
- **Performance target:** completes in under 1 second on a fully-populated archive (123 pieces + ~30 chunks). Image-header inspection only; no full pixel decode.
- **No network access.** No external API calls.

The helper can grow over time — accepting `--json` for machine-readable output, a `--quiet` flag for CI use, or a `--piece NNN` filter for asking about one specific piece. Start with the bare contract above; add flags as concrete needs emerge.
