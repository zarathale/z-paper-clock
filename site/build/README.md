# site/build/

The actual deployable site. Static HTML/CSS for v0; build tooling (Vite, Astro, Eleventy) only when complexity warrants it. v0 is plain files.

## Structure

```
site/build/
├── index.html              homepage — 8 sections per site/strategy/README.md
├── charter/
│   └── index.html          /charter side trip
├── assets/
│   └── styles.css          shared stylesheet (visual-direction inheritance TBD)
└── README.md               this file
```

## Deploy target

`mypaperclock.cc` — Liquid Web, IP `50.28.105.83`. See `site/INFRASTRUCTURE.md` for full operational reference.

## Deploy pattern

**Alan ships; Claude authors.** Same gate as git. Claude does not write to the live server directly.

Three viable deploy mechanisms:

1. **Manual SFTP from Alan's mac.** Cyberduck / FileZilla / Transmit pointed at the Liquid Web box; drag-drop the changed files. Slow but visible — Alan sees exactly what's going up before it goes up.
2. **Scripted deploy from Alan's mac.** ✅ Selected for v0 (2026-05-09). Lives at [`../deploy.sh`](../deploy.sh) (= `site/deploy.sh`). Uses `rsync` over SSH with a host alias defined in `~/.ssh/config` — **no credentials in the script**. Default is dry-run; `--apply` actually pushes. See the script's header for one-time setup steps.
3. **CI-triggered.** GitHub Actions on push to `main`, deploying via SSH/SFTP to Liquid Web. Most automation; requires creds in GitHub Actions secrets. Reserved for if/when shipping cadence justifies it.

**Decision (2026-05-09):** option (2). The dry-run-by-default behavior is the no-PR-review substitute: Alan reads the planned diff before approving with `--apply`. If that gate proves enough, we stay here. Promote to (3) only if shipping cadence ever needs it.

## Local preview

Open `index.html` directly in a browser, or run a tiny local server (better — relative paths and routing behave correctly):

```bash
cd site/build
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Status

**Skeleton only.** v0 content has not been drafted yet. The HTML files contain commented section markers but no real copy. Drafting begins once:

- the strategy doc's open questions converge (currently 5 remaining; domain just landed),
- the visual-direction linkage mechanism is settled (task #2 in `site/strategy/README.md`),
- and the personal-arc brief lands (Alan's content carve-out per CHARTER A2).

Until then, this folder is a scaffold to build into.
