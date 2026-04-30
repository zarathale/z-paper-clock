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

1. Read this file
2. Read `work/SPEC-3D-VIEWER.md` if the work touches the build at all
3. Read the most recent entry in `sessions/` to pick up the thread
4. **If working on a Code task:** read the relevant `CODE_PROMPT_*.md` in full before writing code
5. **If touching transcriptions:** read `source/transcriptions/embedded-labels.md` (or `instructions.md`) before editing the relevant section
6. **If touching the pre-processing pipeline:** re-skim `work/scripts/preprocess_scans.py` and `work/scripts/RESCAN_FINDINGS.md`

---

## Where We Are

The study side is complete. The build side has the spec drafted and is ready to start M1 (pipeline end-to-end on plate D). Quick status:

| Track | State |
|---|---|
| Source scans (raw + clean + prepped) | ✅ Complete; 13 plates pre-processed |
| Transcriptions (5 markdown files) | ✅ Complete; full audit pass done 2026-04-29 |
| Auto-trace test v1 + v2 | ✅ Complete; v2 confirms pre-processing eliminates bleed-through |
| 3D viewer spec (`work/SPEC-3D-VIEWER.md`) | ✅ Drafted; 5 open product decisions flagged inline |
| M1 — pipeline end-to-end on plate D | ⏳ Pending Code session |
| M2 — all pieces traced + sidecared | ⏳ Pending |
| M3 — flat viewer with hover/click/inspect | ⏳ Pending |
| M4 — assembly transforms | ⏳ Pending |
| M5 — polish + figure cross-references | ⏳ Pending |
| M6 — mechanism animation (stretch) | 📋 Aspirational |

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

**After ship:** don't delete the prompt. Flip its front-matter `status` to `shipped`, add `shipped:` and (if applicable) `shipped_version:`, and leave the file in repo root as the decision record. The session note should reference the prompt by filename.

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
├── source/                                 ← reference archive (personal-use only)
│   ├── inventory.md
│   ├── scans-raw/                          original phone photos
│   ├── scans-clean/                        dewarped + perspective-corrected
│   ├── scans-prepped/                      flat-fielded + bleed-suppressed (auto-trace input)
│   └── transcriptions/                     5 markdown files: prose, labels, instructions
├── work/                                   ← derivative work
│   ├── SPEC-3D-VIEWER.md                   build spec; the source of truth for the viewer
│   ├── pieces/                             per-piece SVG + JSON + crop (NEW, populated in M1+)
│   ├── assemblies/                         per-group transforms (NEW, populated in M4)
│   ├── pipeline/                           Python pipeline scripts (NEW, populated in M1)
│   ├── viewer/                             TS + three.js viewer (NEW, populated in M3)
│   ├── pieces.csv                          master index: piece → plate → bucket → bbox (NEW)
│   ├── scripts/
│   │   ├── preprocess_scans.py             flat-field + chroma-aware bleed suppression
│   │   └── RESCAN_FINDINGS.md              per-plate quality assessment
│   ├── auto-trace-test/                    v1 test (kept as audit trail)
│   └── auto-trace-test-v2/                 v2 test on pre-processed scans
├── sessions/                               session notes (NEW, this convention)
└── CODE_PROMPT_*.md                        per-task orchestration prompts (NEW, root-level)
```

The (NEW) entries don't exist yet but are reserved by name in the SPEC. Don't create them speculatively — let M1+ populate them.

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

- Branch name: `claude/M<n>-<short>` for milestone work; `claude/v<x.y.z>` for version ships; otherwise `claude/<descriptive-slug>`.
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
3. **Hand the commit to Zarathale.** Cowork does not run `git commit` / `git push` from the sandbox. Generate a copy-paste-ready commit message at end-of-session and display it. Zarathale commits and pushes via GitHub Desktop.
4. Cowork does **not** open PRs. PRs are a Code-mode step (or Zarathale opens via GitHub web).

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
| Rescans | Not required to start. Plate L thumb and plate A higher-resolution are optional cosmetic rescans, deferred. |

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

---

## File Naming Conventions

- **Session notes:** `YYYY-MM-DD-HHMM_mode_short-topic.md` in `sessions/`. Datetime, not date-only.
- **Orchestration prompts:** `CODE_PROMPT_<target>.md` at repo root. `<target>` is either `M<n>-<short>` for milestone work or `v<x.y.z>` for version ships.
- **Per-piece files:** `piece-NNN.svg` + `piece-NNN.json` + `crop.png` inside `work/pieces/NNN/`. Three-digit zero-padded piece number. Letter variants are appended: `piece-092a.svg`.
- **Scans:** `pNNN-short-description.jpg` (set in `source/inventory.md`). Don't rename existing scans.
- **Layered SVG groups:** Inkscape `inkscape:label` matches the canonical layer names (`silhouette`, `cutouts`, `folds-valley`, `folds-mountain`, `axles`, `glue-zones`, `labels`, `marks-other`) — the viewer keys off these names.

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

*Last updated: 2026-04-29 — initial authoring; cross-pollinated from ScaenaShows and arc-qb-sync working conventions.*
