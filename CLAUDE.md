# CLAUDE.md — Working Conventions for the z-paper-clock Repo

> Read this at the start of every session. It tells you where things are, what's active, and how to work with Zarathale (Alan) on this project. The "Z" in z-paper-clock is Zarathale — Alan's name in this collaboration. **Z**, **Zara**, and **Zarathale** are all good — Zarathale is a mouthful, so the casual forms are usually what comes out in chat. Alan also works.

This file is the cross-session coaching for z-paper-clock. It loads at the start of every Cowork session and is the standing context for every Code session. Per-task orchestration prompts (`CODE_PROMPT_*.md`) live alongside this file at repo root and are the Cowork→Code handoff docs for specific units of work — this file is the background everything else assumes.

---

## What This Repo Is

z-paper-clock is a personal study and derivative-work project around *Make Your Own Working Paper Clock* by James Smith Rudolph (Harper & Row 1983; Perennial 2003 reprint). Two halves:

**The study** — already complete and stable. `source/` holds dewarped scans, transcribed prose, and a comprehensive label/notation pass on all 13 plates. This is reference material; it isn't published from this repo and isn't redistributed. If asked about source provenance, point at the README's note on scope: the book is in print, buy a copy.

**The build** — actively being designed. `work/` is where derivative work grows: pre-processing pipeline, auto-trace experiments, and the 3D viewer that turns the cut-out plates into an interactive model of the assembled clock. The build's spec is `work/SPEC-3D-VIEWER.md` — that document is the next-action source of truth for any session that touches the viewer or the per-piece authoring pipeline.

This is a hobby project. The collaboration with Claude is part of the point. Keep the tone working-and-curious, not corporate. Lean into the metaphor when it helps — the build is a stage production with Zarathale as director and Claude as the production team.

**Repo path:** `/Users/mainstage/Documents/GitHub/z-paper-clock` (mac, in the GitHub folder convention; no OneDrive — see "Git locks" below for the implications).

---

## How This Project Divides Between Cowork and Code

Most design, transcription, and document work happens in **Cowork** (Claude desktop, this app). Most code-and-ship work happens in **Code** (Claude Code in a terminal). The handoff is **always sequential** — Cowork settles the design and produces a ready-for-code orchestration prompt; Code executes it. Never pass an orchestration prompt to Code while open questions remain — fix them in Cowork first.

**Cowork handles:**

- Reading and writing the spec (`work/SPEC-3D-VIEWER.md`) and any successor design docs
- Authoring `CODE_PROMPT_*.md` for the next Code session
- Transcription work and audits (the `source/transcriptions/` files)
- Pre-processing experiments and source-quality decisions (`work/scripts/`)
- Drafting per-piece JSON sidecars by hand from `embedded-labels.md`
- Repo hygiene (CHANGELOG, doc alignment, stale-branch triage), open-question tracking
- Session notes for any pass that touches repo files

**Code handles:**

- Writing Python pipeline scripts (`work/pipeline/*.py`)
- Writing TypeScript / three.js viewer code (`work/viewer/`)
- Running the pipeline end-to-end on real assets to produce SVGs, JSONs, and the viewer manifest
- Version bumps once the viewer ships, CHANGELOG entries
- Branch creation, commits, push, opening the PR
- Running tests and linters

**Builds and runs the sandbox cannot do:** the Cowork sandbox can run Python (and does, for things like `preprocess_scans.py` and the auto-trace test), but cannot run the dev server for the eventual Three.js viewer in a way Zarathale can see. **Don't try to host the viewer from inside the Cowork sandbox.** Spin it up in Code on Zarathale's machine, or open it in a regular browser against `work/viewer/dist/`.

---

## Session Startup

1. Read this file (and `PROJECT-STATE.md` for the slow-moving framing if loading fresh context)
2. Read `WORKPLAN.md` to see what tracks are open right now and what the next action is on each
3. Read `work/SPEC-3D-VIEWER.md` if the work touches the build at all
4. Read the most recent entry in `sessions/` to pick up the thread
5. **If working on a Code task:** read the relevant `CODE_PROMPT_*.md` in full before writing code
6. **If touching transcriptions:** read `source/transcriptions/embedded-labels.md` (or `instructions.md`) before editing the relevant section
7. **If touching the pre-processing pipeline:** re-skim `work/scripts/preprocess_scans.py`. The gen-1 per-plate quality assessment lives at `work/_archive/m1-plate-d-phone/RESCAN_FINDINGS.md` for reference; a fresh gen-2 version will live at `work/scripts/RESCAN_FINDINGS.md` once M0.5 surfaces re-tuning notes.
8. **If receiving / processing scans:** read `source/SCAN-INTAKE-CHECKLIST.md` (capture standard, per-file QC, intake → raw promotion).

---

## Where We Are

_For slow-moving framing on what this project is and what actually exists today, see `PROJECT-STATE.md`. For the current stance — open tracks + next actions + recent activity — see `WORKPLAN.md`. The status table below is the executive-summary mirror of `ROADMAP.md` and gets reconciled at each planning beat. The status table will likely simplify or get generated once `WORKPLAN.md` proves out for a few sessions._

The study side is complete. The build side hit a pause on 2026-04-30 over gutter warp surviving the gen-1 phone-scan pipeline (visible on piece 31 in Inkscape). Initial response: archive gen-1, capture gen-2 on a flat-bed home scanner. Same day, second-pass refinement: the home scanner can't fit a whole plate, so the workflow pivots to **chunk-and-crop** — capture multi-piece chunks that fit the bed, hand-crop to per-piece PNGs in your editor, archive the chunks as recovery references. M1 deliverables remain at `work/_archive/m1-plate-d-phone/`. Quick status:

| Track | State |
|---|---|
| Source scans — gen-1 (phone) | 📦 Archived 2026-04-30 to `source/_archive/phone-scans-2025/` |
| Source scans — gen-2 chunks (`source/scans-chunks/`) | 🔄 In progress; flat-bed multi-piece chunks. 8 chunks landed 2026-04-30 (most of plate D + parts of E/F/G/H). 2026-05-01 added L/R partials + programmatically-stitched composites for pieces 34/35 (plate G long teeth strip) and 94 (plate H pendulum-bob casing) — both stitched at score 0.9+ via cv2.matchTemplate. |
| Source pieces — gen-2 per-piece archive (`source/pieces/`) | 🔄 **117 of 123 captured** (115 numeric + 092a + 112a). 6 still pending: 013, 014, 016, 017 (plate B brackets), 090 (plate F reduction-gear pulley/disc), 110 (plate A face-frame end rail). First batch (97) ingested 2026-04-30 — see `sessions/2026-04-30-2359_cowork_inbox-ingest.md`. Second batch (4 + L/R-stitching for 34/35/94) ingested 2026-05-01 — see `sessions/2026-05-01-0030_cowork_inbox-ingest-batch2.md`. Third batch (16 more: 003/005/008/012/015/034/035/065/067/073/075/076/080/094/120/121) ingested 2026-05-01 — see `sessions/2026-05-01-0130_cowork_inbox-ingest-batch3.md`. Effective DPI verified at ~613 from a ruler measurement on piece 002 (above the 600-DPI spec). |
| Master piece list (`work/pieces.csv`) | ✅ Expanded 2026-04-30 to a 123-row master index: **121 numbered pieces (1–121, contiguous) + 092a + 112a**. The clock face was renumbered from 122 → 121 in the consolidation pass (face is not numbered in print; the book's piece numbering is non-contiguous and 121 is the only available slot — closes the gap). Schema: id, plate, section, bucket, status, notes. Bbox columns dropped — pipeline reads `source/pieces/` directly. |
| Transcriptions (5 markdown files) | ✅ Complete; audited 2026-04-29; scan-independent |
| Auto-trace test v1 + v2 | 📦 Archived (gen-1 era) |
| 3D viewer spec (`work/SPEC-3D-VIEWER.md`) | ✅ Drafted; 5 product decisions resolved 2026-04-30 |
| Build roadmap (`ROADMAP.md`) | ✅ Drafted 2026-04-30; M0.5 reshaped 2026-04-30 for chunk-and-crop onboarding |
| M0.5 — Chunk-and-crop onboarding + pipeline reshape | 🔄 In progress; superseded the original "rescan + re-bring-up" plate-based plan |
| M0.6 — Authoring/QA preview tool (`preview.html`) | 🔄 In progress; foundation + cut-layer + texture-flip + back-face-mirror + perf + thickness fix + axle rotation shipped 2026-05-02. v1b (polygon cut + hinge animation) + cutouts subtraction + multi-cutaway + `work/viewer/` graduation decision pending. See `work/SPEC-3D-VIEWER.md` §"Authoring/QA preview tool" and `ROADMAP.md` M0.6. |
| M1 — pipeline end-to-end on plate D (gen-1) | 📦 Shipped against gen-1 (archived); to be re-run against gen-2 per-piece archive in M0.5 |
| Piece-scan ingest skill | 🔄 SKILL.md drafted at `.claude/skills/piece-scan-ingest/SKILL.md`; helper queued via `CODE_PROMPT_M0.5.2-piece-scan-ingest.md` |
| M2 — all pieces traced + gear-ratio validation | ⏳ Pending; blocked on M0.5 |
| M3 — flat viewer (illustrative aesthetic) | ⏳ Pending; ships v0.1.0 |
| M4 — assembly transforms | ⏳ Pending |
| M5 — polish + figure cross-references | ⏳ Pending |
| M6 — mechanism animation (stretch) | 📋 Aspirational |
| Post-M5 — mobile interactivity | 📋 Deferred per resolved decision #3 |

Update the relevant row whenever a milestone closes or a new state is reached.

---

## Orchestration Prompt Format (`CODE_PROMPT_*.md`)

This is the Cowork→Code handoff format. It's what turns a fuzzy intent into a clean Code session.

Naming: `CODE_PROMPT_M1-pipeline-plate-d.md` for milestone work; `CODE_PROMPT_v0.1.0.md` once the viewer is shipping versioned releases. Both live at repo root and are kept after ship as decision records.

**Front matter:**

```yaml
---
status: draft | in-development | ready-for-code | shipped
started: YYYY-MM-DD
owner: Zarathale (Alan)
target: M1-pipeline-plate-d            # or target_version: 0.1.0
# After ship:
shipped: YYYY-MM-DD
shipped_version: 0.1.0                 # if version-numbered
---
```

**Required body sections, in order:**

1. **What You Are Doing and Why** — two paragraphs max. Name the change and the motivation. If a previous session surfaced the work, name the session note.
2. **Prerequisites — confirm before starting** — bulleted list Code can verify in 30 seconds (e.g., "`source/scans-prepped/p00x-plate-D-...jpg` exists"; "Python 3.10+ with Pillow + scikit-image installed"; "previous milestone session note exists").
3. **Read These Files First** — numbered list of files Code must load before writing. Always include the relevant SPEC section.
4. **Target File Structure Changes** — fenced tree showing only files that will be touched, annotated with `← update: ...` / `← NEW: ...` / `← remove: ...`.
5. **Numbered Tasks** — one section per logical change. Each task names the file, gives the exact code to add/replace/remove (or the exact algorithm/structure for new code), and explains any non-obvious decision inline.
6. **Verification Checklist** — numbered post-implementation checks Code runs against the finished work (file exists, lints pass, output is what we expected, version constants match if version-numbered).
7. **What NOT to Change** — named exclusions. Stops Code from drifting into out-of-scope refactors.
8. **Manual tests** (optional) — small table or list of pre-/post-conditions Zarathale runs after merge against the local checkout. Include when the change is observable end-to-end.

**After ship:** don't delete the prompt. Flip its front-matter `status` to `shipped`, add `shipped:` and (if applicable) `shipped_version:`, and leave the file in repo root as the decision record. The session note should reference the prompt by filename. **Add a one-line italic header below the front matter:** `_Shipped YYYY-MM-DD; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._` This stops a fresh session from misreading a stale orchestration prompt as a current task list — the prompt body stays as it shipped (decision record), but the header makes the time-of-write framing explicit.

---

## Sessions Convention

Every Cowork session that touches repo files, and every Code session that ships work, drops a note into `sessions/`.

**Filename pattern:** `YYYY-MM-DD-HHMM_mode_short-topic.md`

Examples: `2026-04-29-1400_cowork_3d-viewer-spec.md`, `2026-05-15-0900_code_M1-pipeline-plate-d.md`.

**Required front matter:**

```yaml
---
date: YYYY-MM-DD
start_time: "HH:MM"
end_time: "HH:MM"  # or "TBD" if written mid-session
mode: cowork | code
participant: Zarathale (Alan)
# Code sessions:
target: M1-pipeline-plate-d            # or version_shipped: 0.1.0
orchestration_prompt: CODE_PROMPT_M1-pipeline-plate-d.md
# Retroactive notes:
source: retroactive — assembled from [sources]
---
```

**Required body:**

- **Goal** — one line.
- **What was done** — files touched, decisions made, output produced.
- **Branch / commit** (Code sessions only) — branch name and the commit SHA(s) pushed.
- **Open questions** — anything unresolved. If a follow-up Code session is needed, name it.
- **Next-session handoff** — what the next person at the keyboard should do first.

Session notes are working records, not polished deliverables. Write one even if the session ended abnormally — that's when they matter most. **Retroactive notes are valid:** if a session shipped without a note, reconstruct it from the prompt + commits + chat residue, mark `source: retroactive`, and file under the date the work actually happened. The transcription audit (originally captured in `work/audit-session-log.md`) was onboarded this way — see `sessions/2026-04-29-0900_cowork_transcription-audit.md`.

---

## Versioning Policy

The repo doesn't version the study side — `source/` and `source/transcriptions/` are stable and don't have a version number. The viewer app, once it's running in M3+, gets SemVer.

**Viewer SemVer:**

| Bump | When |
|---|---|
| **Patch** (0.1.**x**) | Bug fix or small correction in a shipped feature. |
| **Minor** (0.**x**.0) | New feature — new piece, new layer toggle, new inspect-panel field, new pipeline stage. |
| **Major** (**x**.0.0) | Breaking change — manifest schema change, sidecar format change, asset path change. |

Pre-1.0 (i.e., everything before the viewer is "done"), minor bumps absorb breaking changes too — that's the SemVer convention for 0.x.

When ready: version lives in `work/viewer/package.json` and `work/manifest.json`'s `viewerVersion` field. CHANGELOG entry required for every bump.

For pipeline-only work that doesn't touch the viewer (M1, M2 milestones), no version bump — the milestone label in the orchestration prompt's front matter is the identifier.

---

## Repo Structure

```
z-paper-clock/                              ← repo root
├── CLAUDE.md                               ← this file
├── README.md                               ← public-facing project description
├── inbox/                                  ← working zone for in-flight chunk scans (transient)
│   └── _pending-rescan/                    gitignored; scans set aside for re-do
├── source/                                 ← reference archive (personal-use only)
│   ├── inventory.md
│   ├── SCAN-INTAKE-CHECKLIST.md            chunk-and-crop capture + QC standard (gen-2)
│   ├── pieces/                             per-piece source archive: NNN[a].png, lossless (NEW, populating M0.5)
│   ├── scans-chunks/                       multi-piece chunk captures kept as recovery references (NEW, populating M0.5)
│   ├── scans-raw/                          legacy plate-oriented raw (kept; mostly unused)
│   ├── scans-clean/                        legacy plate-oriented clean (kept; mostly unused)
│   ├── scans-prepped/                      legacy plate-oriented prepped (kept; mostly unused)
│   ├── transcriptions/                     5 markdown files: prose, labels, instructions
│   └── _archive/
│       └── phone-scans-2025/               gen-1 (handheld phone) raw + clean + prepped, archived 2026-04-30
├── work/                                   ← derivative work
│   ├── SPEC-3D-VIEWER.md                   build spec; the source of truth for the viewer
│   ├── pieces/                             per-piece SVG + JSON + crop (NEW, repopulated in M0.5+)
│   ├── assemblies/                         per-group transforms (NEW, populated in M4)
│   ├── pipeline/                           Python pipeline scripts; 01-crop.py being archived in M0.5 (chunk-and-crop replaces plate slicing)
│   ├── viewer/                             TS + three.js viewer (NEW, populated in M3)
│   ├── pieces.csv                          master index of all 123 pieces (1–121 contiguous + 092a + 112a). Schema: id, plate, section, bucket, status, notes
│   ├── scripts/
│   │   ├── build_master_list.py            generator for pieces.csv from embedded-labels.md (run to regenerate)
│   │   └── preprocess_scans.py             flat-field + chroma-aware bleed suppression (gen-1 era; per-piece re-tuning if needed)
│   └── _archive/
│       └── m1-plate-d-phone/               M1 gen-1 outputs: pieces/0NN/, auto-trace-test/, auto-trace-test-v2/, RESCAN_FINDINGS.md
├── sessions/                               session notes (NEW, this convention)
└── CODE_PROMPT_*.md                        per-task orchestration prompts (NEW, root-level)
```

The (NEW) entries don't exist yet but are reserved by name in the SPEC. Don't create them speculatively — let the active milestone populate them. The legacy `scans-raw/`, `scans-clean/`, `scans-prepped/` folders carry forward as empty-but-reserved; they're not part of the active chunk-and-crop loop, but the structure stays in case a non-plate page ever benefits from a whole-page capture path. (The original `scans-intake/` folder was deleted in the chunk-and-crop consolidation pass; intake now lives at the repo-root `inbox/`.)

---

## Git Workflow

Three agents touch this repo. Keep them in their lanes.

**Cowork (Claude desktop, this app)** — edits files directly in the mounted folder. Does not run `git`. Generates a copy-paste-ready commit message at end of session; Zarathale stages and commits via GitHub Desktop after reviewing.

**Code (Claude Code, terminal)** — writes Python and TypeScript. Always works on a feature branch (`claude/<short-description>` or `claude/M<n>-<topic>`). When done: commits to that branch, pushes, opens the PR via `gh pr create`. Stops there. Zarathale reviews the diff and merges via GitHub Desktop or GitHub web. **Code never commits directly to `main`.**

**GitHub Desktop** — Zarathale's merge/push surface. The source of truth for what's actually on `main`. Cowork and Code both stop short of merge.

**Cowork commit-message format** (what Cowork produces at end of session, for Zarathale to paste into GitHub Desktop):

- **Subject:** imperative, lowercase, scoped, ~70 chars or less. Examples: `add SPEC-3D-VIEWER.md and bootstrap CLAUDE.md`, `audit transcriptions; fix paragraph breaks in preface`.
- **Body:** 2–5 short paragraphs (or bullets if the changes are inherently a list). What changed and why; reference filenames; mention the session-note filename. No marketing language.

**Display convention.** Always close a Cowork session by displaying the commit message at the end of the closing comment, with **subject and body in two separate copy-pasteable code blocks** — GitHub Desktop has separate fields for each, and one combined block forces Zarathale to split it by hand. Don't put any prose between the two blocks.

**Code branch / commit / PR rules:**

- **Branch name (strict).** `claude/M<n>-<short>` for milestone work (e.g. `claude/M1-pipeline-plate-d`); `claude/v<x.y.z>` for version ships (e.g. `claude/v0.1.0`); otherwise `claude/<descriptive-slug>` (e.g. `claude/fix-trace-threshold`). **Do NOT use Claude Code's auto-generated random-name branches** like `claude/vigorous-rhodes-06b447` — those make the branch list illegible and obscure what the work was for. If Claude Code starts on an auto-generated branch, rename it before the first commit: `git branch -m claude/<correct-name>`.
- Commit message subject: imperative, lowercase, ≤70 chars. For version ships, prefix with the version: `v0.1.0: bring up flat viewer with hover and inspect panel`.
- Bump version (if applicable) **before** the commit, not after.
- Push the branch; do not merge.
- Open the PR with `gh pr create` directly. Do not probe for `gh` first — it's installed and authenticated on Zarathale's mac. Surface the real error if anything goes wrong, don't silently hand the PR step back.

Canonical PR command (Code runs this directly):

```bash
gh pr create \
  --base main \
  --head "$(git branch --show-current)" \
  --title "<imperative, lowercase, ≤70 chars, scoped>" \
  --body-file "<path-to-prepared-body.md>"
```

**PR title and description:**

- **Title:** imperative, lowercase, ≤70 chars, scoped.
- **Description:**
  - One-line summary.
  - "What changed" — bullets of `file → what`.
  - Any post-merge manual steps.
  - Branch name + commit SHA(s).
  - Link to the orchestration prompt file.

---

## Ending a Session

### Cowork sessions

At the end of any Cowork session that made design decisions or touched repo files:

1. Add a session note to `sessions/` using the filename pattern above.
2. If a `CODE_PROMPT_*.md` was produced or updated, confirm its front-matter `status` is current (`ready-for-code` if it's ready to ship, `in-development` if not).
3. **Doc-sweep before drafting the commit message.** If the session renamed, retired, or replaced anything (a folder, a piece ID, a workflow stage, a script, a status), grep the repo for the old names and confirm the downstream docs still hang together: `README.md`, `work/SPEC-3D-VIEWER.md`, `source/inventory.md`, `source/transcriptions/`, `ROADMAP.md`, CLAUDE.md itself, and any READMEs in `source/_archive/` / `work/_archive/`. Update each downstream reference, or annotate the stale claim as legacy/historical with a date. The 2026-04-30 repo audit (`sessions/2026-04-30-2100_cowork_repo-audit.md`) exists because this step had been skipped over a high-velocity day.
4. **Hand the commit to Zarathale.** Cowork does not run `git commit` / `git push` from the sandbox. Generate a copy-paste-ready commit message at end-of-session and display it. Zarathale commits and pushes via GitHub Desktop.
5. Cowork does **not** open PRs. PRs are a Code-mode step (or Zarathale opens via GitHub web).

No version bump for design-only Cowork sessions.

### Code sessions

At the end of any Code session that changed files, in this order:

1. Bump the version in `work/viewer/package.json` (if the viewer was touched and is at v0.x+).
2. Add a dated entry to the relevant CHANGELOG (the viewer has its own; the repo doesn't yet).
3. Add a session note to `sessions/` — not optional. Include branch name and commit SHA.
4. Commit to the `claude/*` branch and push to `origin`.
5. Open the PR via `gh pr create`. Return the PR URL to Zarathale in the final chat message.
6. Flip the orchestration prompt's front matter to `shipped` + add `shipped:` and (if applicable) `shipped_version:`. Leave the file in place as the decision record.
7. Zarathale reviews + merges in-browser, deletes the remote branch there, pulls `main` via GitHub Desktop, then runs the post-merge cleanup block (below) on his mac.

**If a Code session must end before all of these steps are complete:** at minimum, write the session note with whatever was done, commit to `claude/*`, and push. A session that wrote code but left no commit trail is a bug, not a feature. If only the PR step didn't complete, say so explicitly and paste the exact `gh pr create` command Zarathale can run.

---

## Mac + git locks (less aggressive than Windows + OneDrive)

This repo lives on a mac in `~/Documents/GitHub/z-paper-clock`. There's no OneDrive sync layer here, so the stale-lock failure mode that bites the arc-qb-sync repo doesn't apply by default. Most of the time, normal `git` works.

If `git` does misbehave:

```bash
cd ~/Documents/GitHub/z-paper-clock

# Clear stale lock files (safe; no-op if absent)
rm -f .git/index.lock
rm -f .git/packed-refs.lock

# Normal cleanup
git fetch --prune
git worktree prune
```

If you see `fatal: bad config line N in file .git/config`, the file got partially overwritten. Canonical safe content:

```
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	ignorecase = true
	precomposeunicode = true
[remote "origin"]
	url = https://github.com/<owner>/z-paper-clock.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main
```

(Replace `<owner>` with the actual GitHub owner; verify against `git remote -v` before rewriting if at all possible.)

If GitHub Desktop is showing weird state — half-applied commits, unexpected modified files, lock errors — close GitHub Desktop, run the cleanup above in Terminal, then reopen GitHub Desktop. The desktop app holds file handles on `.git/` that can confuse other tooling.

---

## Post-merge cleanup

After Zarathale merges a Code PR and pulls `main`, run this in the repo root to clean up the local feature branches:

```bash
cd ~/Documents/GitHub/z-paper-clock
git fetch --prune
git worktree prune
git branch --merged main | grep -E '^\s+claude/' | xargs -r git branch -d
```

If a branch refuses to delete cleanly because it was force-rebased on the remote, swap `-d` for `-D`. The `--merged main` filter keeps that safe — only branches already merged to `main` are eligible.

If stale `claude/*` branches are spotted at the start of a Cowork session (i.e., cleanup was missed after a previous merge), flag them and run the cleanup before building on top of the repo.

---

## Dev environment (mac)

This is what Code can assume is installed and configured on Zarathale's mac without re-probing at session start. If any of these break, fix them once and update this section; do not turn each session into a probe-and-install scavenger hunt.

**Toolchain.**

- macOS with Apple Silicon, case-insensitive filesystem (so lowercase filenames everywhere — see "File Naming Conventions" above).
- `python3.12` on PATH (Homebrew install: `brew install python@3.12`). The repo's virtualenv lives at `.venv/` at repo root, created via `python3.12 -m venv .venv`. The `Makefile` invokes `../../.venv/bin/python` directly; Code can use that path without activating the venv first.
- Native `potrace` on PATH (`brew install potrace`). The pipeline's `02-trace.py` prefers it (50–100× faster); pure-Python `potracer` is the fallback for sandbox-only use.
- `gh` (GitHub CLI) installed and authenticated under Zarathale's GitHub account. Use `gh pr create` directly without probing for auth state — if it fails, surface the real error.
- Inkscape installed at `/Applications/Inkscape.app` for the hand-edit pass on auto-traced SVGs.

**Python packages already in `.venv`** (reinstall via `pip install <name>` only if a script imports something missing):

Pillow, scipy, scikit-image, numpy, lxml, potracer.

**What's NOT installed by default.**

- Node.js / pnpm — needed once the viewer (`work/viewer/`) lands in M3. Install with `brew install pnpm` at that point.
- A Vite dev server has nowhere to run inside the Cowork sandbox. Run viewer dev servers locally on the mac via Code (`cd work/viewer && pnpm dev`).

**Pre-approved tool patterns.** `.claude/settings.json` (committed) pre-approves the common Bash patterns Code reaches for in this repo: `git`, `make`, `python` and `python3`/`python3.12`, the venv binaries under `.venv/bin/`, `pip`/`pip3`, `brew`, `potrace`, `gh`, `node`/`npm`/`pnpm`/`npx`, plus read-only inspection (`ls`, `cat`, `rg`, `find`, `grep`, `head`, `tail`, `wc`, `diff`, `awk`, `sed`, `jq`, `tree`). Destructive ops (`rm`, `mv`, `cp`) and WebFetch are intentionally NOT pre-approved — they continue to prompt. Per-machine overrides go in `.claude/settings.local.json` (gitignored).

---

## Architectural Decisions (Closed)

Do not reopen these without Zarathale.

| Decision | Choice |
|---|---|
| Auto-trace pipeline | Auto-trace + light hand-edit + hand-trace for gutter strips and rectangles. Native `potrace` once available; pure-Python `potracer` as sandbox fallback. |
| Pre-processing | LAB-luminance flat-field + levels stretch + chroma-aware bleed-through suppression. Per-plate, run once per scan version. |
| Per-piece data model | Layered SVG (silhouette, cutouts, folds-valley, folds-mountain, axles, glue-zones, labels, marks-other) + JSON sidecar. Silhouette is the only layer that extrudes. |
| 3D extrusion | three.js `SVGLoader` + `ExtrudeGeometry` at view time. Decals baked from non-silhouette layers into a `CanvasTexture` on the front face. |
| Assembly model | Hierarchical `Object3D` groups, one per book section (§II.A framework, §II.B mechanism subgroups, §II.C anchor/pendulum, §II.D hands, §II.E weight, §II.F face/case). Per-group JSON of transforms. |
| Viewer tech stack | TypeScript + Vite + three.js. Vanilla TS, no React. Tailwind for inspect-panel layout. Static-site deploy. |
| Source scope | `source/` is personal-reference. The deployed viewer ships per-piece crops (derivative work) and SVGs/JSONs, not the source plate JPGs themselves. |
| Rescans (gen-1 → gen-2) | **Reversed 2026-04-30.** Originally "not required to start; cosmetic only, deferred." Now: full re-scan on a flat-bed home scanner is required. Gutter warp from gen-1 phone scans survived pre-processing and showed up as bowed silhouettes in M1 outputs. Gen-1 archived; gen-2 capture standard in `source/SCAN-INTAKE-CHECKLIST.md`. Filenames preserved where applicable; chunk-and-crop introduces new filename conventions (see below). |
| Chunk-and-crop onboarding | **Settled 2026-04-30 (later same day).** The home scanner can't fit a whole plate. Workflow: capture multi-piece chunks (filename = NN_NN_NN.{jpeg,png} listing the COMPLETE pieces inside) → archive chunks to `source/scans-chunks/` as recovery references → hand-crop each piece in editor → save as `source/pieces/NNN.png` (lossless, three-digit zero-padded; letter variants `NNNa.png`). Pipeline reads `source/pieces/` directly. Replaces the plate-based `01-crop.py` slicing model. |
| pieces.csv schema | **Reshaped 2026-04-30.** Was `id, plate, bucket, bbox_x, bbox_y, bbox_w, bbox_h` (11 plate-D rows from M1). Now `id, plate, section, bucket, status, notes` (123 rows: 1–121 contiguous + 092a + 112a). Bbox columns dropped because `source/pieces/` is the pipeline input and there's no plate to slice from. The clock face was renumbered from 122 → 121 in the consolidation pass (the face is not numbered in print; piece 121 is assigned for build authoring, closing the gap in the book's non-contiguous numbering). `bucket` retained for tracing-strategy hints; populated for plate D (M1), blank elsewhere until each plate's tracing pass assigns. `status` flips from `pending` → `captured` → `traced` as pieces flow through the pipeline. Status flips are deliberate manual edits, not derived from filesystem presence — the ingest skill (M0.5.2) audits and reports but never writes to `pieces.csv`. |
| Per-piece archive format | **Settled 2026-04-30.** Lossless PNG (`NNN.png`). Chunks stay JPG (q=92+) since they're intermediate; stitched composites are PNG to preserve seam fidelity; per-piece archive is PNG to keep auto-trace input clean. |
| Piece-scan ingest skill | Workflow design settled 2026-04-30: skill audits `source/pieces/` against `work/pieces.csv` master list; runs filename + image-health checks (DPI, dimensions, color mode); reports captured-vs-pending status; flags anomalies. **Read-only by contract — never modifies `pieces.csv` or anything under `source/`.** Tiered checks (BLOCK on bad-filename / unknown-id / unreadable; WARN on low-DPI / small-dims / non-RGB). SKILL.md drafted at `.claude/skills/piece-scan-ingest/SKILL.md`; Python helper at `scripts/audit.py` queued via `CODE_PROMPT_M0.5.2-piece-scan-ingest.md`. |
| Faithful trace + functional sidecar | **Settled 2026-04-30 (later in the day).** Default direction for the build: trace each piece **faithfully** — the SVG geometry preserves the human-drawn, human-scanned messiness as the artifact, and no "clean up the gear teeth" pass ever runs against the SVG. Mechanism geometry (gear tooth counts, axle positions, drive relationships) is captured separately as an optional `function` block in the JSON sidecar so the (M6 stretch) mechanism animation can read intended values without modifying the trace. **Scope:** `function` block populated only for §II.B (gear train) + §II.C (anchor / pendulum / escapement) pieces — the ~25–30 pieces that have to satisfy the ticking constraint. All other pieces (framework, hands, weight, face, case) stay purely artifact-faithful with no `function` block. Hand rotation rates inherit from the gear chain at animation time; nothing about a hand's *shape* is functional. **Anchor unit:** *escape-wheel advance per tick.* One tick = the escape wheel rotates `2π/N` rad, where `N` is its tooth count. Every other rotation in the mechanism is derived from this. The book's stated period (from `instructions.md`) becomes a sanity-check, not a primary input. The validation script queued under M2 (resolved decision #5) operates on `function` blocks. |
| Cut-layer authoring convention | **Settled 2026-05-02** after triaging v1a render bugs. The cut is authored as `<g id="silhouette">` containing `<path id="cutaway">` (single piece) or `<path id="cutaway-1">`, `<path id="cutaway-2">`, ... (multiple disconnected outer pieces). Visual authoring frames use `id="mask"` or `id="mask-N"` and are ignored by the parser. Interior holes go in a sibling `<g id="cutouts">` layer with `id="cutout-1"`, `id="cutout-2"`, ... — semantically distinct (subtracted from the slab, not extruded). Affinity wraps silhouette children in an unnamed `<g>`; parser walks descendants so wrappers are transparent. `extractSilhouette` priority chain: silhouette layer → PNG alpha → largest-colored-path heuristic, with banners on each fallback. `extractSilhouettePath`'s `skipIds` set extended to include `silhouette` and `cutouts` so the heuristic never matches authored cut paths. Settled in `sessions/2026-05-02-1500_cowork_preview-html-cut-layer-spec.md`; implemented via `CODE_PROMPT_preview-html-cut-layer.md`. |
| Axle rotation + orientation cue | **Settled 2026-05-02** during axle-rotation build in `preview.html`. Each piece with an authored axle gets a Rotation slider (−180° to +180°, **CW positive** clock convention) that pivots the slab around the axle line (Z-axis through the active axle, perpendicular to the slab). Single-axle assumption: `axles[0]` is the active rotation axle; multi-axle support deferred until a piece surfaces with multiple axles. The axle itself renders as a 1 mm-diameter shiny silver cylinder (metalness 0.9, roughness 0.25, color 0xc8cdd0), world-anchored OUTSIDE the rotation pivot — matching the physical clock where the axle wire is fixed to the framework and the piece (with a future glued-on knitting-needle bushing) rotates around it. The bearing's hollow tube will be added INSIDE the pivot when authoring data for it lands. Optional orientation cue: an element with `id="north"` inside `<g id="axles">` defines the +0° direction via the (active-axle → north) vector; rendered as a brass-gold sphere (color 0xb89e5b) INSIDE the pivot so it visualises the current angle relative to the as-authored 0°. Default/fallback thickness on no-thickness-layer SVGs is 0.4 mm (cardstock-typical). Settled in `sessions/2026-05-02-2330_cowork_preview-html-axle-rotation.md`. |

---

## Open Questions

| # | Priority | Question | Source |
|---|---|---|---|
| 1 | Medium | Layer-toggle: hide vs. translucent (case off → invisible or 20% opacity)? | SPEC §"Open product decisions" |
| 2 | Medium | Aesthetic: photographic vs. illustrative as default? | SPEC §"Open product decisions" |
| 3 | Low | Mobile interactivity depth — full orbit/explode, or read-only inspect? | SPEC §"Open product decisions" |
| 4 | Medium | Hosting: GitHub Pages off this repo (with public/private split for source), separate viewer repo, or self-host? | SPEC §"Open product decisions" |
| 5 | Low | Pull mechanism animation forward from M6 stretch to validate gear ratios early? | SPEC §"Open product decisions" |

---

## Known Issues / Tech Debt

- `instructions.md` §II.B Motor Wheel piece-40 assembly text is flagged as scan-unclear. Resolved in audit but tagged for re-verification if it surfaces in M2 sidecaring.
- Pure-Python `potracer` is ~50–100× slower than native `potrace`. Acceptable for the auto-trace test; will need to swap to native for production tracing across all pieces. Track in M1 prereqs.
- The mac filesystem is case-insensitive; if pipeline scripts ever produce both `piece-001.svg` and `Piece-001.svg`, they will collide. Convention: lowercase filenames everywhere.
- `work/scripts/preprocess_scans.py` flat-field strength and bleed-suppression chroma threshold were tuned for handheld phone scans (strong vignette, visible bleed-through). Flat-bed gen-2 scans are cleaner; the same parameters likely over-correct on per-piece input. Under chunk-and-crop, pre-processing becomes a per-piece operation if/when needed — re-tune as specific captures surface issues, capturing findings in a fresh `work/scripts/RESCAN_FINDINGS.md`.
- **Pipeline reshape pending.** `work/pipeline/01-crop.py` was the plate-slicing stage that consumed `pieces.csv` bbox fractions. Under chunk-and-crop those fractions are gone, and `source/pieces/` is the direct pipeline input. `01-crop.py` is now stale and slated for archival to `work/_archive/`; `02-trace.py` needs a small repoint to read from `source/pieces/NNN.png` instead of `work/pieces/NNN/crop.png` (or a rename of the input path inside each piece directory). The Makefile target chain needs a parallel update. Tracked in M0.5; do **not** run `make pieces` in the meantime — it'll fail.
- **`pieces.csv` bucket coverage.** Buckets (auto-trace-clean / auto-trace-edit / hand-trace) are populated only for plate D's 11 pieces (carried forward from M1). All other pieces have `bucket=` blank pending visual triage in M2 task 2.1.
- **Letter-variant convention split.** Source archive uses `092a.png` (short form, since the folder name `source/pieces/` provides context). Derivative artifacts in `work/pieces/` use `piece-092a.svg` (long form, kept for filename self-documentation in flat tooling output). Both refer to the same piece. The viewer manifest key is the bare ID `092a`.

---

## File Naming Conventions

> For a scannable cheat sheet of the SVG authoring conventions (layer names, per-element ids, common slips), see `LAYER-CONVENTIONS.md` at repo root. The list below is the authoritative source; the cheat sheet is the distilled version designed to stay open while editing in Affinity.

- **Session notes:** `YYYY-MM-DD-HHMM_mode_short-topic.md` in `sessions/`. Datetime, not date-only. **HHMM collision rule:** if a previous session note already exists for the same `YYYY-MM-DD-HHMM`, bump the new note to a non-colliding HHMM (15:00 + 15:30, not 15:00 + 15:00). Front-matter `start_time` should match the filename's HHMM, even if it's a small fudge from the actual clock — filename and front matter agree, and the HHMM is just a unique-key, not a time log.
- **Orchestration prompts:** `CODE_PROMPT_<target>.md` at repo root. `<target>` is either `M<n>-<short>` for milestone work or `v<x.y.z>` for version ships.
- **Per-piece source archive:** `source/pieces/NNN.png` (lossless PNG). Three-digit zero-padded. Letter variants suffix lowercase: `092a.png`, `112a.png`.
- **Per-piece derivative files:** `piece-NNN.svg` + `piece-NNN.json` + `crop.png` inside `work/pieces/NNN/`. Three-digit zero-padded piece number. Letter variants are appended: `piece-092a.svg`. (The `piece-` prefix here is intentional self-documentation in flat tooling output; the source archive in `source/pieces/` skips it because the folder name already provides context.)
- **Chunk scans:** `NN_NN_NN.{jpeg,png}` listing the COMPLETE pieces inside, ascending. Single-piece chunks: `NN.{jpeg,png}`. L/R partials: `NN_l.jpeg` + `NN_r.jpeg` for a single piece, `NN_NN_l.jpeg` + `NN_NN_r.jpeg` for a multi-piece chunk. Stitched composites: `NN_stitched.png` (single piece) or `NN_NN_stitched.png` (multi-piece), always PNG. Letter-variant pieces (`92a`) sort alphanumerically with their numeric base in ascending lists (e.g. `92a_98_99.jpeg`). Live in `source/scans-chunks/` once promoted from `inbox/`.
- **Legacy plate scans (gen-1 + reserved):** `pNNN-short-description.jpg` (set in `source/inventory.md`). Don't rename existing scans. Under chunk-and-crop, this naming applies only to whole-page captures of non-plate pages (front matter, instructions, back cover) if those are ever scanned.
- **Layered SVG groups:** Authored as `<g id="...">` (Affinity Designer) or via Inkscape `inkscape:label` — semantically equivalent. Canonical layer names: `silhouette`, `cutouts`, `folds-valley`, `folds-mountain`, `axles`, `glue-zones`, `labels`, `marks-other`. The viewer keys off these names.
- **Per-element ids inside cut layers** (settled 2026-05-02). Inside `<g id="silhouette">`: `id="cutaway"` for a single piece, or `id="cutaway-1"`, `id="cutaway-2"`, ... for multiple disconnected outer pieces on one SVG; `id="mask"` or `id="mask-N"` is a visual authoring frame the parser ignores. Inside `<g id="cutouts">`: `id="cutout-1"`, `id="cutout-2"`, ... for interior holes (e.g. piece 71's center cell). Numeric suffix (not alphabetic) so it scales past 26. `cutaway-N` means "another disconnected outer piece" (becomes its own slab); `cutout-N` means "another interior hole in the same piece" (subtracted from the slab). They are NOT interchangeable — they live in different top-level layers because the renderer treats them differently. Affinity may wrap silhouette children in an unnamed `<g>`; the parser walks descendants, so wrappers are transparent.
- **Per-element ids inside `<g id="axles">`** (settled 2026-05-02). Axle markers themselves are unidentified ellipse / circle elements (existing convention, unchanged). Optional one-per-piece orientation cue: an element with `id="north"` defines the +0° rotation direction via the vector from the active axle (`axles[0]`) to the marker's centroid. Element type for `north` is any shape `elementCentroid()` parses — ellipse, circle, rect, or path. North without an axle is banner-warned and ignored. Slider sign for the rotation it grounds: +deg = CW (clock convention) when viewed from the front. Currently consumed only by `preview.html`; downstream uses (assembly orientation offsets, M6 mechanism animation) will read the same convention.

---

## Notes for Every Session

- Read the relevant `CODE_PROMPT_*.md` in full before starting a Code session.
- Piece numbers, plate letters, and label notation come from `source/transcriptions/embedded-labels.md` — never invent.
- Don't try to host the viewer dev server from the Cowork sandbox. Code does that on Zarathale's mac.
- The sandbox can run Python scripts against `source/` and `work/` directly via the bash tool. Use it for trace experiments, validation passes, and any other Python work that doesn't need to leave the box.
- Do not republish or commit anything that re-creates the book's content (text, imagery) verbatim. The transcriptions are personal-reference. Derivative artifacts (per-piece traces, the 3D viewer) are fine.
- At the end of each session, write a session note. Even small ones. Especially small ones.
- "Z" in z-paper-clock = Zarathale = Alan. Z, Zara, and Zarathale are all embraced; the casual forms are usually what comes out in chat (Zarathale is a mouthful). Alan in commit attribution and any context calling for the legal name.

---

*Last updated: 2026-05-03 (afternoon) — **shipped LAYER-CONVENTIONS.md cheat sheet at repo root** and **handed CODE_PROMPT_asset-state-audit.md to Code** for v0 of the per-piece state audit. The cheat sheet is the scannable companion to the File Naming Conventions section above (designed to stay open while authoring in Affinity). The audit script is the linter-rule pattern that addresses the "how do I track which pieces still need to be uplifted to convention X" pain point — each authoring convention becomes its own check, new conventions auto-flag old SVGs at next audit run, no migration step. Cross-reference added at the top of the File Naming Conventions section. Asset-state track in `WORKPLAN.md` flipped queued → active. See `sessions/2026-05-03-1400_cowork_asset-state-schema-and-audit.md`.*

*Earlier 2026-05-03 (morning) — **introduced PROJECT-STATE.md + WORKPLAN.md operating-layer documents** at repo root. PROJECT-STATE.md is the slow-moving framing doc (what this project actually is, what exists today, how to read other docs); WORKPLAN.md is the active stance (per-track hypothesis + status + next action + recent log, eight tracks seeded). Session Startup gained a step for WORKPLAN.md and a fresh-context mention of PROJECT-STATE.md. The "Where We Are" header gained a one-paragraph framing pointer; the status table itself is unchanged for now and will be reconciled in a later pass once WORKPLAN proves out for a few sessions. Asset-state design (per-piece JSON, audit-script-generated from filesystem reality) settled in the design conversation but implementation queued as its own track. GitHub Projects parked as a future open question on the operations-layer track. See `sessions/2026-05-03-0000_cowork_project-state-and-workplan.md`.*

*Earlier 2026-05-02 (very late evening) — **doc pass surfacing the `preview.html` work into the SPEC and ROADMAP.** Added a new section "Authoring/QA preview tool (`preview.html`)" to `work/SPEC-3D-VIEWER.md` (consumes / silhouette source chain / current feature set / what's not yet there / path forward — including the open question of whether preview.html graduates into `work/viewer/`, stays a separate authoring tool, or replaces `work/viewer/` outright). Added an **M0.6** row to `ROADMAP.md` (index + full milestone section between M0.5 and M1) covering all preview.html work shipped to date, v1b queued, cutouts + multi-cutaway + TODO(070)/TODO(uv-offsets) deferred, and the architecture-decision row 0.6.13. Status table above gained a matching row. The "Sequence" section at the bottom of the SPEC now references M0.6 as a parallel track to M0.5. No code changes; just the docs catching up to what's in the file. See `sessions/2026-05-02-2359_cowork_preview-html-spec-and-roadmap.md`.*

*Earlier 2026-05-02 (late evening / midnight pass) — fixed a long-latent **thickness extrusion bug** in `preview.html` (variable `UNITS_PER_MM` was misnamed as the inverse of its actual value, leading to T being multiplied by ~0.01; renamed to `MM_PER_UNIT` and removed the multiplier so `T = thicknessMm` directly). Default/fallback thickness dropped 1.0 → 0.4 mm to match Alan's cardstock plan. Then added **axle rotation** to `preview.html`: pieces with axles get a Rotation slider (−180° to +180°, CW positive clock convention) that pivots the slab around the axle via a wrapping `THREE.Group`. Axles render as 1 mm shiny silver cylinders, world-anchored outside the pivot (mirroring the physical clock's framework-mounted wire). Future bearing slots in cleanly inside the pivot. Optional `id="north"` element inside `<g id="axles">` becomes the +0° orientation cue, rendered as a brass-gold sphere. Architectural Decisions table gained one row; File Naming Conventions section extended with the axles-layer per-element ids. Three cowork sessions today: `2026-05-02-2300_cowork_preview-html-thickness-fix.md` (extrusion fix + thickness default tweak as addendum), `2026-05-02-2330_cowork_preview-html-axle-rotation.md` (rotation slider, silver wires, north cue), and the earlier mid-day pair on the cut-layer spec (`-1500`) + ship (`-1400`).*

*Earlier 2026-05-02 (afternoon pass) — settled the **cut-layer authoring convention** after triaging v1a render bugs across 066/067/069/070. Inside `<g id="silhouette">`: `id="cutaway"` (single) or `id="cutaway-N"` (multi-piece), `id="mask"` for visual frames the parser ignores. Inside `<g id="cutouts">`: `id="cutout-N"` for interior holes — semantically distinct (subtracted from slab, not extruded). Affinity wraps silhouette children in an unnamed `<g>`; parser walks descendants. Architectural Decisions table gained one row; File Naming Conventions section extended. Implementation queued via `CODE_PROMPT_preview-html-cut-layer.md`. Two cowork sessions notes today: `2026-05-02-1500_cowork_preview-html-cut-layer-spec.md` (spec) and `2026-05-02-1400_code_preview-html-v1a.md` (the v1a ship that triggered the triage).*

*Earlier 2026-05-01 (early-morning pass) — third ingest pass on `inbox/`. 16 new per-piece PNGs landed in `source/pieces/`: 003, 005, 008, 012, 015, 034, 035, 065, 067, 073, 075, 076, 080, 094, 120, 121 (status flipped to `captured`). 080 came in as both `080.jpeg` and `080.png` (same content, mean pixel diff 0.17); the PNG is the canonical archive, the JPEG was parked at `source/scans-chunks/080.jpeg` as a redundant intermediate. Pieces 34/35 cropped out of `34_35_stitched.png` from the prior session (tight crops, 0–22 px paper margin). Piece 94 cropped from `94_stitched.png` directly (printed area covers 99%+ of the stitched composite, no further crop needed). Both `34_35_stitched.png` and `94_stitched.png` are no longer present in `source/scans-chunks/` after Zarathale's editor pass — the L/R partials remain, so re-stitching is possible if needed. Cumulative state: **117 of 123 captured**; 6 still pending (013, 014, 016, 017, 090, 110). Master-list status row + ROADMAP M0.5.4 updated.*

*Earlier 2026-05-01 (just-past-midnight pass) — second ingest pass on `inbox/`. Four new per-piece PNGs landed in `source/pieces/`: 010, 092, 097, 100 (status flipped to `captured`). L/R partials for pieces 34/35 and piece 94 stitched programmatically using `cv2.matchTemplate` with TM_CCOEFF_NORMED; alignment scores 0.899 and 0.919 (above the 0.7 "solid" threshold). Stitched composites and partials archived to `source/scans-chunks/` (`34_35_l.jpeg`, `34_35_r.jpeg`, `34_35_stitched.png`, `94_l.jpeg`, `94_r.jpeg`, `94_stitched.png`). Pieces 34, 35, 94 stay `pending` — they need editor-side cropping out of the stitched composites before per-piece PNGs can land. Cumulative state: 101 of 123 captured; 22 still pending. Master-list status row + ROADMAP M0.5.4 updated.*

*Earlier 2026-04-30 (late evening / midnight pass) — first ingest from `inbox/` into `source/pieces/`. 97 per-piece PNGs landed (95 numeric + 092a + 112a); 26 still pending. `pieces.csv` status flipped from `pending` → `captured` for the 97 ingested rows. `107-weight.png` (a non-build axle/weight-wire dimension reference, originally captured separately from `107.png` because the book labels both as "107") parked in `source/scans-chunks/107-weight-reference.png` rather than in the per-piece archive — both are reference material, not pieces, and the per-piece archive only has one slot for ID 107. Effective DPI verified at ~613 from a ruler measurement on piece 002 (slightly above the 600-DPI spec). PNG headers don't carry DPI metadata; cosmetic only, nothing downstream reads it. Status table row for `source/pieces/` bumped accordingly. Duplicate clusters 021/022 and 113–116 ingested as byte-identical files in their own slots (deliberate — the four cross-shaped face braces and the two folded brackets are physically the same artwork in print; convention stays "every piece ID has its own `source/pieces/NNN.png`").*

*Earlier 2026-04-30 (later same day, evening pass) — settled the **faithful trace + functional sidecar** direction for the build. SVG stays artifact-faithful; mechanism geometry captured in an optional `function` block on §II.B + §II.C sidecars only. Anchor unit = escape-wheel advance per tick (one tick = 2π/N rad). Architectural Decisions table gained one new row; SPEC sidecar schema updated to document the `function` block.*

*Earlier 2026-04-30 (later same day) — pivoted from plate-based gen-2 rescan to **chunk-and-crop onboarding** after confirming the home scanner can't fit a whole plate. New `source/pieces/` and `source/scans-chunks/` folders; `pieces.csv` expanded from 11 plate-D rows to 123-row master index; bbox columns dropped; `01-crop.py` slated for archival. Architectural Decisions table gained three new rows (chunk-and-crop, pieces.csv schema, per-piece archive format). Known Issues updated. File Naming Conventions split source/derivative/chunk/legacy paths.*

*Earlier 2026-04-30 — added gen-1/gen-2 scan archive note; flipped M1 status; revised Rescans decision; expanded Known Issues for pre-processing tuning + bbox re-validation.*

*Earlier: 2026-04-29 — initial authoring; cross-pollinated from ScaenaShows and arc-qb-sync working conventions.*
