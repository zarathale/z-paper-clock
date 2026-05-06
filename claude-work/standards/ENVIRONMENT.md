# ENVIRONMENT.md — z-paper-clock build environment

_Single source of truth for the tools, runtimes, and configuration this project depends on. Maintained by Claude per CHARTER §3 ("Owns most of the standards corpus") and §5 (`claude-work/standards/`). Used by Alan when setting up a new device, when Claude needs Alan to install something, or when either of us needs to know where a capability lives._

This doc supersedes the "Dev environment (mac)" section in CLAUDE.md going forward. CLAUDE.md's section stays as inherited background; this doc is what gets updated as the environment evolves.

---

## How to read this doc

The build runs across three surfaces and they have different capabilities:

- **Alan's Mac bench** (`~/Documents/GitHub/z-paper-clock`) — the primary authoring surface. Affinity Designer, Inkscape, Python venv, GitHub Desktop, native browser.
- **Alan's Windows bench** (`C:\Users\Alan Lytle\Documents\Code\z-paper-clock`) — the secondary authoring surface, kept in sync via GitHub Desktop. Same toolchain, different package manager.
- **Cowork sandbox** (Linux, mounted at `/sessions/<id>/mnt/z-paper-clock/`) — Claude's working surface during Cowork sessions. Has Python + Node + ImageMagick + ffmpeg + opencv pre-installed; **no public package-registry access** (allowlist blocks pypi, npmjs, github, etc.); spins up fresh Linux processes each session, but the workspace folder persists because it's the user-side filesystem mounted in.

For each tool below, the doc says which surface needs it, why, and the install command per platform.

---

## What's settled / what's open

**Settled** (in use today):

- Python 3.12 venv at `.venv/` with project dependencies (Pillow, scipy, scikit-image, numpy, lxml, potracer)
- Native `potrace` for tracing (used by `02-trace.py`)
- Inkscape for hand-edits on auto-traced SVGs
- Affinity Designer for per-piece SVG authoring (Alan-side, primary tool)
- `gh` (GitHub CLI) for Code-session PRs
- GitHub Desktop for Alan's commit/merge surface
- Cowork sandbox's pre-installed Python + Node + ImageMagick + opencv stack (no install required; documented for future-reference)

**Settled 2026-05-05:** Headless browser verification via the **trigger-file daemon** at `claude-work/scripts/watch_and_render.py` + `preview_render.py`. Alan installs Playwright in `.venv-headless/` per device, launches the daemon once per session, and Cowork-Claude triggers renders by writing files to `claude-work/state/render-triggers/`. Outputs land in `claude-work/state/preview-renders/`. Both folders gitignored. Full protocol + troubleshooting in `claude-work/scripts/PREVIEW_RENDER_README.md`. Claude-in-Chrome MCP remains the right path for ad-hoc verification within a single conversation.

**Open** (decisions pending — see `claude-work/DECISIONS.md` and chat):

- **Node.js / pnpm** for the eventual viewer (M3 timing). Not needed yet; install when M3 starts.

---

## Surface 1: Alan's Mac bench

**OS:** macOS, Apple Silicon, case-insensitive filesystem (lowercase filenames everywhere).
**Package manager:** Homebrew (`brew`). Install once if missing: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.

### 1.1 First-time setup on a new Mac

Run from a fresh terminal in the repo root after cloning via GitHub Desktop:

```bash
# Repo: clone via GitHub Desktop (https://github.com/Zarathale/z-paper-clock)
# Then cd into the repo:
cd ~/Documents/GitHub/z-paper-clock

# 1. Install native tools via Homebrew
brew install python@3.12 potrace gh

# 2. Install Inkscape (cask)
brew install --cask inkscape

# 3. Install Affinity Designer manually (paid; from Mac App Store or Affinity site)
# https://affinity.serif.com/en-us/designer/

# 4. Project Python venv
python3.12 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install Pillow scipy scikit-image numpy lxml potracer

# 5. Headless browser venv (for preview.html verification scripts)
python3.12 -m venv .venv-headless
.venv-headless/bin/pip install --upgrade pip
.venv-headless/bin/pip install playwright
.venv-headless/bin/python -m playwright install chromium

# 6. Authenticate gh
gh auth login

# 7. (Optional) Make sure Affinity lock-files are gitignored — already in .gitignore as of 2026-05-04
```

Estimated total time: ~10-15 min on a clean machine, mostly Homebrew + Chromium download. Disk: ~500 MB across all tools.

### 1.2 Mac toolchain reference

| Tool | Purpose | Install | Notes |
|---|---|---|---|
| Python 3.12 | Project scripts; `.venv` | `brew install python@3.12` | Path: `/opt/homebrew/bin/python3.12` |
| Native `potrace` | Auto-trace pipeline (`02-trace.py`); 50-100× faster than `potracer` Python fallback | `brew install potrace` | |
| Inkscape | Hand-edit pass on auto-traced SVGs | `brew install --cask inkscape` | App at `/Applications/Inkscape.app` |
| Affinity Designer | Per-piece SVG authoring (Alan's primary tool) | Mac App Store or affinity.serif.com | Paid. Lock files (`.~lock.*.af#`) already gitignored |
| `gh` (GitHub CLI) | PR creation in Code sessions | `brew install gh` | Authenticate once: `gh auth login` |
| GitHub Desktop | Merge/push surface (Alan's primary git UX) | desktop.github.com | Holds locks on `.git/`; close it if other tooling complains |
| Playwright + Chromium (`.venv-headless/`) | Headless verification of preview.html | See §1.1 step 5 | ~150 MB disk; gitignored; per-device |

### 1.3 Mac environment quirks worth knowing

- **Case-insensitive filesystem.** If a script ever produced both `piece-001.svg` and `Piece-001.svg` they'd collide. Convention: lowercase filenames everywhere.
- **No OneDrive layer.** Stale `.git/index.lock` issues are rare here. If git misbehaves, the cleanup block at CLAUDE.md "Mac + git locks" still applies.
- **Mac venv is not portable to Linux/Windows.** `.venv/` and `.venv-headless/` are gitignored for this reason — every device installs its own.

---

## Surface 2: Alan's Windows bench

**OS:** Windows 11, x64.
**Package manager:** `winget` (built-in on Win 11). Alternative: Scoop or Chocolatey if preferred.
**Default shell for command lines:** PowerShell or Git Bash.

### 2.1 First-time setup on a new Windows machine

Run from PowerShell in the repo root after cloning via GitHub Desktop:

```powershell
# Repo: clone via GitHub Desktop (https://github.com/Zarathale/z-paper-clock)
# Then cd into the repo:
cd "C:\Users\$env:USERNAME\Documents\Code\z-paper-clock"

# 1. Install native tools via winget
winget install --id Python.Python.3.12 -e --silent
winget install --id PeterLemenkov.potrace -e --silent  # verify exact ID — see notes below
winget install --id GitHub.cli -e --silent
winget install --id Inkscape.Inkscape -e --silent

# 2. Install Affinity Designer manually (paid; from Microsoft Store or Affinity site)
# https://affinity.serif.com/en-us/designer/

# 3. Project Python venv
python -m venv .venv
.\.venv\Scripts\pip install --upgrade pip
.\.venv\Scripts\pip install Pillow scipy scikit-image numpy lxml potracer

# 4. Headless browser venv (for preview.html verification scripts)
python -m venv .venv-headless
.\.venv-headless\Scripts\pip install --upgrade pip
.\.venv-headless\Scripts\pip install playwright
.\.venv-headless\Scripts\python -m playwright install chromium

# 5. Authenticate gh
gh auth login
```

Estimated total time: ~15-20 min on a clean machine.

**Notes on `winget` package IDs:** The IDs above are best guesses; verify with `winget search potrace` (etc.) if any fail. `potrace` may need to come from a portable distribution if winget doesn't carry it — fallback: download from https://potrace.sourceforge.net and add to PATH manually.

### 2.2 Windows toolchain reference

| Tool | Purpose | Install | Notes |
|---|---|---|---|
| Python 3.12 | Project scripts; `.venv` | `winget install Python.Python.3.12` | Adds `python` to PATH |
| Native `potrace` | Auto-trace pipeline | `winget install` (verify ID) or portable from potrace.sourceforge.net | If portable, add directory to PATH |
| Inkscape | Hand-edit pass | `winget install Inkscape.Inkscape` | |
| Affinity Designer | Per-piece SVG authoring | Microsoft Store or affinity.serif.com | Lock files (`*.af~lock~`) gitignored |
| `gh` (GitHub CLI) | PR creation in Code sessions | `winget install GitHub.cli` | |
| GitHub Desktop | Merge/push surface | desktop.github.com | |
| Playwright + Chromium (`.venv-headless/`) | Headless verification of preview.html | See §2.1 step 4 | Per-device; gitignored |

### 2.3 Windows environment quirks worth knowing

- **Case-insensitive filesystem.** Same convention as Mac: lowercase filenames.
- **OneDrive sync** is a real risk if the repo ever lands inside `OneDrive\Documents\`. Keep it under `Documents\Code\` directly. CLAUDE.md mentions this for a different repo and the same lesson applies — OneDrive can hold file locks that confuse git.
- **Affinity lock files** use the `*.af~lock~` form (different from Mac's `.~lock.*.af#`). Both patterns are already gitignored.
- **PowerShell vs. Git Bash.** Both work. If a command in this doc uses bash syntax (forward slashes, `$()` substitution), translate or use Git Bash.
- **Path separator** in scripts: prefer `os.path.join` / `pathlib.Path` in Python so the same code works on both platforms.

---

## Surface 3: Cowork sandbox (Linux, where Claude lives)

The sandbox is a fresh Linux process per Cowork session. It mounts the user's repo folder at `/sessions/<id>/mnt/z-paper-clock/`, so file changes Claude makes are visible to Alan and vice versa. The sandbox itself doesn't persist between sessions — only the workspace folder does.

### 3.1 What's pre-installed in the sandbox

| Capability | Available | Version | Notes |
|---|---|---|---|
| Python | ✓ | 3.10.12 | At `/usr/bin/python3` |
| Node.js | ✓ | 22.22 | + npm 10.9 |
| `requests` (Python) | ✓ | 2.33 | |
| `Pillow` | ✓ | 12.1 | |
| `numpy` | ✓ | 2.2 | |
| `opencv-python` (cv2) | ✓ | 4.13 | Used by `build_assembly_graph.py` and image-stitching |
| `lxml` | ✓ | 6.0 | XML/SVG parsing |
| `matplotlib` | ✓ | 3.10 | Plotting if needed |
| `imageio` + `imageio-ffmpeg` | ✓ | 2.37 / 0.6 | Image/video I/O |
| `pyyaml` | ✓ | 6.0 | For `expected_layers.yaml` etc. |
| `reportlab` | ✓ | 4.4 | PDF generation |
| ImageMagick (`convert`) | ✓ | system | Image conversion / manipulation |
| Ghostscript (`gs`) | ✓ | system | PDF/PostScript |
| ffmpeg | ✓ | system | Video |

### 3.2 What's NOT pre-installed

- Chromium / Firefox / WebKit
- Playwright (Python or Node)
- Selenium
- Native `potrace` (the Python fallback `potracer` is what works in the sandbox)
- Inkscape

### 3.3 The big constraint — sandbox network is heavily restricted

**The Cowork sandbox cannot reach public package registries.** Every test on 2026-05-05 returned 403 (proxy block) or timeout (000):

- pypi.org → 403
- files.pythonhosted.org → 403
- github.com → timeout
- raw.githubusercontent.com → timeout
- registry.npmjs.org → timeout
- nodejs.org → timeout
- playwright.azureedge.net → timeout

What IS reachable: `api.anthropic.com`, `docs.claude.com`. (Probably others — these are the ones I've confirmed.)

**Implication:** Don't try to `pip install` or `npm install` inside the sandbox. It will fail. The pre-installed stack is what's available, full stop. New Python tooling that requires install needs to either come pre-installed by Cowork or be vendored into the repo (gitignored if large).

### 3.4 What Claude uses the sandbox for

Static work that needs Python or shell:

- Running `claude-work/scripts/build_assembly_graph.py` against the panels-first SVGs
- Running the asset-state audit (when it relocates from `work/scripts/`)
- Parsing SVGs to inspect layer structure / validate convention compliance
- Image processing on existing images via opencv (cv2.matchTemplate for stitching, image diff for visual regression)
- Reading and writing files in the workspace
- Running git status / log (read-only — Claude doesn't run `git commit` per CHARTER §3)

What it cannot do:

- Render WebGL / Three.js scenes (no headless browser, no install path)
- Pull new packages from public registries
- Run a dev server visible to Alan (Vite, etc. — Claude lacks port-forward to Alan's browser)

---

## Cross-device sync via GitHub Desktop

Alan switches between Mac and Windows; both check out the repo via GitHub Desktop. The repo lives at:

- Mac: `~/Documents/GitHub/z-paper-clock`
- Windows: `C:\Users\Alan Lytle\Documents\Code\z-paper-clock`

### What syncs

Everything tracked by Git syncs. That includes:
- All source files, transcriptions, SVGs, JSONs
- All scripts, docs, conventions
- This doc

### What does NOT sync (per `.gitignore`)

| Path | Why ignored |
|---|---|
| `.venv/` | Project Python venv; binaries are platform-specific. Each device installs its own per §1.1 / §2.1 |
| `.venv-headless/` | Headless browser venv; binaries platform-specific + Chromium binary is large |
| `__pycache__/`, `*.pyc` | Python bytecode; per-device |
| `.DS_Store` | Mac Finder metadata |
| `.~lock.*.af#`, `*.af~lock~`, `*.af~` | Affinity lock files + editor backups |
| `.claude/worktrees/`, `.claude/settings.local.json` | Claude Code internals; per-machine state |
| `claude-work/state/preview-renders/` | Bench-side verification output (per-device, not synced) |

### When switching devices

1. Pull via GitHub Desktop (or `git pull`).
2. If `.venv/` is missing or stale, re-run §1.1 step 4 / §2.1 step 3.
3. If working with `preview.html` verification, re-run §1.1 step 5 / §2.1 step 4 to install Playwright on the new device.
4. Otherwise just open the repo and keep working — everything that matters is in Git.

---

## How Claude works against this environment

### Cowork sessions (Claude in Cowork mode)

Claude runs in the Linux sandbox. It can:

- Read/write files in the workspace folder.
- Run Python scripts using the pre-installed stack (§3.1).
- Read connection-graph state, audit outputs, screenshots dropped by bench scripts.
- Drive Alan's Chrome via the Claude-in-Chrome MCP (when available; takes a tab briefly).

It cannot:

- Install new packages.
- Render `preview.html` headlessly.
- Run a dev server visible to Alan.

### Code sessions (Claude Code on Alan's bench)

Claude Code runs natively on Alan's Mac/Windows with full filesystem and network access. It can install, run, test, deploy. CODE_PROMPT files at repo root drive each Code session.

### The bridge: trigger-file daemon (`watch_and_render.py`)

For verification work that needs to run on Alan's bench but be readable by Cowork-Claude:

1. **Once per device:** Alan installs Playwright + Chromium in `.venv-headless/` (see §1.1 step 5 / §2.1 step 4).
2. **Once per work session:** Alan launches the daemon in a background Terminal:
   ```bash
   .venv-headless/bin/python claude-work/scripts/watch_and_render.py
   ```
   It polls `claude-work/state/render-triggers/` every 2s.
3. **Anytime:** Cowork-Claude writes a trigger file (e.g. `echo "069" > claude-work/state/render-triggers/req-001.txt`).
4. The daemon picks it up, runs `preview_render.py 069`, writes outputs to `claude-work/state/preview-renders/069.{png,log,json}`, moves the trigger to `render-triggers/done/`.
5. Cowork-Claude reads the screenshot + log + summary.

Round-trip is ~10s per piece. Async-by-design — Alan triggers the daemon and forgets it; Claude triggers individual renders without waiting on Alan's attention.

The trigger-file dropbox + the renders folder are gitignored (per-device, not synced via Git). Full protocol + troubleshooting at `claude-work/scripts/PREVIEW_RENDER_README.md`.

---

## Maintenance log

_When the environment changes, append a one-line entry here. Substantive changes (new tool added, version pinned, allowlist constraint discovered) get a row; typos and clarifications don't._

- **2026-05-05** — Initial authoring. Captures Mac + Windows + sandbox toolchain at the post-PR-#15 state. Sandbox network constraint surfaced (no public-registry access) and documented as a standing fact. Playwright headless install moved to bench-side per the constraint. ENVIRONMENT.md created at `claude-work/standards/`.
- **2026-05-05 (later)** — Trigger-file daemon protocol settled. `claude-work/scripts/preview_render.py` + `watch_and_render.py` + `PREVIEW_RENDER_README.md` shipped. `.gitignore` extended for `claude-work/state/render-triggers/` (paired with the existing `preview-renders/` ignore). "Headless browser verification" flipped from Open → Settled in the §"What's settled / what's open" section.
