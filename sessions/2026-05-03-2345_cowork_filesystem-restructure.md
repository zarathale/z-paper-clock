---
date: 2026-05-03
start_time: "23:45"
end_time: "23:45"
mode: cowork
participant: Zarathale (Alan)
---

**Goal.** Settle a single-source-of-truth file layout for per-piece authoring (`.af`) + export (`.svg`) + sidecar (`.json`); retire the `inbox/` folder; produce orchestration prompts for the moves and the paired preview.html update.

**What was done — the design.** Triaged the actual filesystem state: 14 `.af` files in `source/pieces/` (001, 002, 058, 059, 065, 066, 067, 067-full, 068, 069, 070, 071, 072, 097), 1 stray `.af` in `inbox/` (069.af, duplicate of `source/pieces/069.af`), 8 SVG exports in `inbox/` (001, 065, 066, 067, 069, 070, 071, 072), 1 already-correct SVG at `work/pieces/069/069.svg` (Alan dropped it manually as the conversation starter). Settled the new layout: each piece gets a single working folder at `work/pieces/NNN/` containing `NNN.af` + `NNN.svg` + `NNN.json` (+ optional `crop.png`). `source/pieces/` locked to PNG scans only — no `.af`, no `.svg` (audit catches strays). The `inbox/` folder is retired entirely: chunks land directly in `source/scans-chunks/` from the scanner; SVG exports land directly in `work/pieces/NNN/` from Affinity. Filename convention drops the `piece-` prefix going forward (the folder name `NNN/` provides the context); the M1 archive's `piece-NNN.svg` files stay as-is as decision records. Affinity lock files (`.~lock.NNN.af#`) and editor backups (`NNN.af~`) gitignored — don't try to use lock-file presence as repo signal because cross-machine sync would produce false-positive "in-progress" warnings; explicit "currently authoring" state belongs in the JSON sidecar's `status` field.

**Decisions on duplicates / variants** (rules baked into the filesystem-restructure CODE_PROMPT, executed by Code, not in this Cowork session):

- `069.af` duplicate (inbox vs. source/pieces): canonical = newer by mtime; if identical, prefer the inbox copy (newer in workflow). Loser gets archived to `work/pieces/069/_attic/`.
- `069.svg` duplicate (inbox vs. work/pieces/069/): canonical = newer by mtime; if identical, the existing `work/pieces/069/069.svg` wins. Loser archived to `_attic/` if any.
- `067-full.af` vs. `067.af` (iteration variants, NOT duplicates): newer by mtime becomes `067.af`. Older archived to `_attic/`. Don't try to merge content — Alan can re-open the attic copy if needed.

**Doc updates landed in this Cowork session.**

- `CLAUDE.md` — new Architectural-Decisions row "Per-piece authoring + export colocation; `inbox/` retired"; Repo Structure tree (drop `inbox/`; update `work/pieces/` description); Per-piece working folder line in File Naming Conventions (rewrite); Chunk scans line (drop "promoted from inbox/"); Session Startup step 8 (intake → save-direct-to-chunks); Known Issues "Letter-variant convention split" struck through (resolved); Last-updated note added.
- `source/SCAN-INTAKE-CHECKLIST.md` — chunk-and-crop loop step 1 (no inbox); step 6 (Audit instead of "archive the chunk"); Per-file QC header rewrite; Promotion section renamed "Naming + saving the chunk"; Quick-reference inbox→scans-chunks; Notes section drops `_pending-rescan/` and inbox semantics.
- `source/pieces/README.md` — workflow steps 2 + 4 (chunks land in source/scans-chunks/ directly); Notes section says SVGs / `.af` belong in `work/pieces/NNN/`.
- `LAYER-CONVENTIONS.md` — line 110: SVG-in-source/pieces note no longer mentions inbox.
- `work/SPEC-3D-VIEWER.md` — file/folder layout (drop `inbox/`; update `work/pieces/`); preview.html "What it consumes" (load by piece id from `work/pieces/NNN/NNN.svg`, drag-drop fallback); preview.html "What's not yet there" → new "Source-of-truth piece-id loader (M0.6.14)" bullet.
- `ROADMAP.md` — new M0.6.14 row for the preview piece-id loader (`ready-for-code`); Last-updated note.
- `WORKPLAN.md` — Repo hygiene track next_action + recent log entry + open question on `inbox/` flipped to resolved; preview.html iteration track recent log gains the source-of-truth prompt; Last-updated note.
- `.gitignore` — Affinity lock + backup patterns (`.~lock.*.af#`, `*.af~`); old `inbox/_pending-rescan/` rule removed (folder is going away).

**Two CODE_PROMPTs handed off (`status: ready-for-code`).**

1. `CODE_PROMPT_filesystem-restructure.md` — the actual file moves: 14 `.af` + 9 SVG (incl. `inbox/069.svg` + `work/pieces/069/069.svg` duplicate resolution + `067-full` vs. `067` variant pick), `inbox/` deletion, audit-script repoint (sidecar to short-form `NNN.json`, drop inbox-walking block, drop `inbox_pngs` field, extend `work/pieces/` walk to catch `.af`, add new "af in source/pieces/" anomaly, bump `schema_version` 1 → 2), `CODE_PROMPT_preview-html-v1b.md` verification path bump (`inbox/069.svg` → `work/pieces/069/069.svg`, `inbox/066.svg` → `work/pieces/066/066.svg`).
2. `CODE_PROMPT_preview-html-source-of-truth.md` — preview.html grows a piece-id input + Load + Reload buttons. URL `?piece=NNN` for bookmarking. Optional `function`-block surfacing from `work/pieces/NNN/NNN.json`. Drag-drop retained as fallback. M0.6.14.

The two prompts are independent — Code can ship them in either order, but the cleaner order is filesystem-restructure first so the canonical paths exist by the time preview.html starts reading from them.

**Open questions.** None outstanding. The three duplicate / variant ambiguities all have explicit resolution rules in the filesystem-restructure prompt — Code picks canonical via mtime + diff and archives losers to per-piece `_attic/`.

**Branch / commit.** Cowork session — no git ran from this seat. Commit message displayed at end of the chat for Zarathale to paste into GitHub Desktop.

**Next-session handoff.** Hand `CODE_PROMPT_filesystem-restructure.md` to Code first. Verify the audit summary's stage histogram afterward (~13 pieces in `affinity_started` or `svg_drafted`). Then hand `CODE_PROMPT_preview-html-source-of-truth.md` to Code. After both ship, Alan tests the iterate-fast workflow: open `work/pieces/069/069.af`, edit, export, click Reload in preview.html — the loop should be one click instead of a file-picker dance.
