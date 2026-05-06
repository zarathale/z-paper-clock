# Preview-render daemon — protocol + usage

_How Cowork-Claude verifies preview.html renders without taking your bench out of authoring rotation. Maintained by Claude per CHARTER §3._

## What this is

A two-script bridge that lets Claude (running in the Cowork sandbox) trigger headless-Chromium renders of `preview.html` on Alan's bench. Claude can't run Chromium itself — the sandbox doesn't have it and can't install it (see `claude-work/standards/ENVIRONMENT.md` §3.3 for the network constraint). This daemon closes that gap.

```
Cowork sandbox                     Alan's bench (Mac/Win)
─────────────────                  ───────────────────────
Claude writes:                     watch_and_render.py polls,
  claude-work/state/                 sees the trigger,
  render-triggers/req-NNN.txt   →  runs preview_render(NNN),
                                   drops outputs.

Claude reads:                      ←  claude-work/state/
  claude-work/state/                  preview-renders/NNN.png
  preview-renders/NNN.png             preview-renders/NNN.log
  preview-renders/NNN.json            preview-renders/NNN.json
```

The trigger and output folders are gitignored — ephemeral state, per-device.

## First-time setup

Once per device. Done in a Terminal at the repo root.

### Mac

```bash
cd ~/Documents/GitHub/z-paper-clock
python3.12 -m venv .venv-headless
.venv-headless/bin/pip install --upgrade pip
.venv-headless/bin/pip install playwright
.venv-headless/bin/python -m playwright install chromium
```

Total: ~2 min. Disk: ~150 MB (gitignored).

### Windows (PowerShell)

```powershell
cd "C:\Users\Alan Lytle\Documents\Code\z-paper-clock"
python -m venv .venv-headless
.\.venv-headless\Scripts\pip install --upgrade pip
.\.venv-headless\Scripts\pip install playwright
.\.venv-headless\Scripts\python -m playwright install chromium
```

## Per-session: launch the daemon

One Terminal window per work session. Leave it running in the background.

### Mac

```bash
cd ~/Documents/GitHub/z-paper-clock
.venv-headless/bin/python claude-work/scripts/watch_and_render.py
```

### Windows

```powershell
cd "C:\Users\Alan Lytle\Documents\Code\z-paper-clock"
.\.venv-headless\Scripts\python claude-work\scripts\watch_and_render.py
```

You'll see:

```
[watch_and_render] z-paper-clock preview-render daemon
[watch_and_render] watching:  claude-work/state/render-triggers/
[watch_and_render] outputs:   claude-work/state/preview-renders/
[watch_and_render] poll:      every 2.0s
[watch_and_render] Ctrl-C to stop.
```

Close the Terminal window or Ctrl-C to stop. Restarting is free — the state's in files.

## Manual one-shot (skipping the daemon)

When you want to render a piece yourself without the daemon:

```bash
.venv-headless/bin/python claude-work/scripts/preview_render.py 069
```

Output lands in `claude-work/state/preview-renders/069.{png,log,json}`. Nonzero exit code if any console errors fired.

## Trigger-file conventions

A trigger is any file inside `claude-work/state/render-triggers/`. The daemon scans the filename, then the content, for a 3-digit piece id (with optional lowercase letter for variants like `092a` / `112a`). First match wins.

Examples that all work:

```
render-triggers/069.txt              ← filename match (content empty)
render-triggers/req-2026-05-05.txt   ← content match: file contains "069"
render-triggers/render-094-bob.txt   ← filename match (94 is the bob casing)
```

After processing, triggers move to `render-triggers/done/` (success) or `render-triggers/failed/` (couldn't parse / render failed). Outputs land in `claude-work/state/preview-renders/`.

## Output shape

For piece `NNN`:

- **`NNN.png`** — viewport screenshot (1280×900) once the dispatch banner appeared
- **`NNN.log`** — console messages (info + warn + error) from the page
- **`NNN.json`** — small structured summary:
  ```json
  {
    "piece": "069",
    "banner": "panels-first ✓ — 11 panels, 10 folds, root: abc",
    "console_msgs": 8,
    "error_count": 0,
    "errors": [],
    "render_time_ms": 1240,
    "timestamp": "2026-05-05 23:40:11",
    "outputs": { ... }
  }
  ```

## Troubleshooting

- **Daemon prints `[watch_and_render] loop error: ...`** — transient filesystem issue, daemon keeps running. If it persists, restart it.
- **`render() failed: net::ERR_CONNECTION_REFUSED`** — the local HTTP server didn't start. Check that port 8765 isn't already in use; pass `--port 8766` to either script if so.
- **`banner-wait-timeout`** — preview.html loaded but neither dispatch banner appeared within 15s. Likely a JS error before banner code runs; check `<NNN>.log` for stack traces.
- **Screenshot is blank** — Three.js scene may not have rendered yet. The daemon waits for the banner but not for full WebGL composition; if this becomes an issue we can extend `preview_render.py` to wait for a specific scene state.
- **Multiple devices triggered the same render** — last writer wins; that's fine for single-Alan, single-bench use.
