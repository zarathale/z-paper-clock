---
date: 2026-05-09
start_time: "21:09"
end_time: "21:09"
mode: cowork
participant: Zarathale (Alan)
---

# Goal

Open the public-face storytelling/marketing track for the project: charter amendment, folder scaffold, strategy doc, infrastructure capture, deploy mechanism, and v0 source files for `mypaperclock.cc`.

# What was done

Substantive scope addition. New co-owned `site/` folder added to the project, with charter amendment + strategy + infrastructure + deploy mechanism + v0 source files all landing in one session.

## Charter amendment A2

`claude-work/CHARTER.md` — added `site/` to §4 folder split + read/write rules; added "public-face site for the project" as a parallel track to the §6 ship list; added the A2 amendment row to the log per §12. Co-ownership tilts toward Claude-leads-with-Alan-input, with two carve-outs where Alan leads: personal-arc content and voice-on-Alan's-behalf. Both signed and initialed in chat 2026-05-09. Touches §3, §4, §6.

## site/ folder created (entirely new)

- **`site/README.md`** — entry doc for the folder; points back to charter A2.
- **`site/strategy/README.md`** — first-pass strategy doc. Frame (Angle A long-arc memoir + Angle C open notebook, with Angle B 3D viewer as eventual destination), audiences (horology-craft + LLM/AI, deliberately niche), voice (with avoid-list), v0 sitemap (single long-scroll homepage + `/charter` side trip), three-angle weave, visual inheritance principle, what-this-is-not, phasing v0 → v1 → v2+, and 6 open questions for the next iteration.
- **`site/INFRASTRUCTURE.md`** — operational reference. Domain `mypaperclock.cc` (purchased 2026-05-09 by Alan); hosting Liquid Web (`smooth-relation.metalseed.io`, IP `50.28.105.83`, Debian 6.1.0-42-amd64, Apache strongly indicated); document root `/var/www/mypaperclock.cc/` confirmed by sibling-site convention (`alandlytle.com`, `scaenacraft.cc` follow same pattern). Charter cross-reference flag captured: original §2 named GitHub Pages as the public host for the eventual viewer; new Liquid Web setup makes the same domain a likely future home for the viewer too — pending decision; potential A3.
- **`site/deploy.sh`** — rsync-over-SSH deploy script using a host alias from `~/.ssh/config`. No credentials in the script. Dry-run by default; `--apply` actually pushes. Header walks through one-time SSH-key setup. `DEPLOY_PATH` confirmed (`/var/www/mypaperclock.cc/`).
- **`site/build/README.md`** — build folder doc, deploy mechanism settled, local-preview instructions.
- **`site/build/index.html`** — full first-pass homepage. Eight sections per strategy doc. Real Claude-voice copy in *what-this-is*, *the pieces*, *mid-flight*, *the collaboration*, *what's next*, and the colophon. Two clearly-marked `.todo-alan` DRAFT blocks for Alan-voice content (hero one-liner + the arc memoir). Open Graph meta tags. Repo URL `https://github.com/Zarathale/z-paper-clock` (settled at session close).
- **`site/build/charter/index.html`** — charter side-trip page. Context intro framing why the charter is public, plus a deliberate TODO with three rendering-approach options (verbatim from CHARTER.md, curated public rendition, or summary-with-link). v0 falls back to a link to the canonical CHARTER.md on GitHub.
- **`site/build/assets/styles.css`** — cream-paper aesthetic with brass-gold accent. Token system via CSS custom properties; values pulled directly from preview.html's 3D paper rendering (paper `#f0e0c8`, brass-gold `#c9a96e`, brass `#b89e5b`, silver `#c8cdd0`, paper-tone `#e8e3da`). When task #2 (formal linkage mechanism) lands, the custom properties stay; only their *source* moves. Italic serif for headings (Iowan Old Style → Charter → Georgia stack), mono for code. `.todo-alan` blocks have a "DRAFT — Alan voice needed" label that's visible-but-unmissable in dev so they can't accidentally ship.

## Coaching landed

- **SSH/SFTP question.** SFTP runs over SSH (same auth, same security; SFTP is the file-transfer profile of an SSH connection). Honest preference for safe + reliable on a static personal site = no agent creds, Alan deploys via deploy.sh from his mac, mirrors the existing "Claude proposes, Alan ships" gate from git. Direct-deploy options ranked but parked (SFTP-restricted = acceptable; full SSH = power without need for static site; CI = overkill for v0).
- **Self-managed Debian → cPanel/WHM delta.** SSH hardening (key auth + disable password login is the priority), web server config, SSL via certbot, ufw + fail2ban + unattended-upgrades, eventual non-root deploy user. Server-hardening pass should happen before public launch; highest-priority single item is disabling SSH password auth for root.
- **FileZilla configuration walked through** (Protocol: SFTP, Host: 50.28.105.83, Port: 22, User: root, password — same as `ssh root@50.28.105.83`).

## Server orientation

- Hostname `smooth-relation.metalseed.io`, Debian 6.1.0-42-amd64.
- Other sites already on this box: `alandlytle.com` (simple html page), `scaenacraft.cc` (tribute/landing page for the MC server, sister repo at `~/Documents/Code/scaenacraft-ops`).
- /root/ filesystem shows real prior history: `.mysql_history`, `.npm`, `.vscode-server`, `.dotnet`, `.openclaw`, `.claude/` — multi-purpose box, with active remote-dev usage.

# Tasks

| # | Status | Subject |
|---|---|---|
| 1 | completed | Site strategy doc — sitemap, audience framing, voice |
| 2 | pending | Settle visual-direction linkage mechanism (partial progress: token values now extracted into site CSS as custom properties; the mechanism for syncing with preview.html still TBD) |
| 3 | pending (blocked by #1) | Draft personal-arc content brief for Alan |
| 4 | pending | Land first deploy of v0 site to mypaperclock.cc |

# Decisions reached this session

- A2 amendment signed (charter §3, §4, §6 amended; new co-owned `site/` zone).
- Domain: `mypaperclock.cc` (purchased 2026-05-09).
- Hosting: Liquid Web, Debian 6.1, vhost provisioning in progress by LW staff.
- Document root: `/var/www/mypaperclock.cc/` confirmed by sibling convention.
- Deploy: rsync over SSH from Alan's mac via `deploy.sh`; no agent credentials.
- Visual direction values: extracted from preview.html, now CSS custom properties in `site/build/assets/styles.css`; formal linkage mechanism still TBD.
- Featured piece for the embedded preview tool: **pendulum bob** (specific id from the 094-100 cluster TBD when wiring up).
- Repo URL: `github.com/Zarathale/z-paper-clock`.

# Open questions

From the strategy doc (5 remaining after domain settled):

1. Personal-arc length (~150-300 word target; converges after first draft)
2. Hero image (photograph of 1996 build / render / preview.html still / commissioned art)
3. Live-counters mechanism (build-time render vs. runtime fetch)
4. Collaboration section's specificity — currently mostly Claude-prose; could weight more toward receipts (charter excerpts, sessions pulls)
5. /notebook curation mechanism (deferred until a notebook section exists)

New from this session:

6. Charter rendering approach for `/charter` page — three options noted in HTML; pick at first deploy or shortly after.
7. **Charter A3 question** — shift viewer hosting from GitHub Pages (charter §2 / decision #4) to `mypaperclock.cc/viewer/`? Same-domain feels right for cohesion; substantive amendment territory if we go that way. Pending decision.
8. `claude-work/STATUS.md` — add a "site" track? Worth doing to keep STATUS.md as the live working surface for the new track.
9. `CLAUDE.md` / `README.md` / `PROJECT-STATE.md` — `site/` folder isn't yet referenced in any of these. Per charter §4 those are read-only for Claude post-charter; if Alan wants `site/` surfaced in those docs, his call to make.

# Next-session handoff

**For Alan:**

1. Open `site/build/index.html` locally (`cd site/build && python3 -m http.server 8000`, then `localhost:8000`). React to the visual direction; flag anything off in the Claude-voice copy, especially the collaboration section where I put words in our mouth.
2. Eventually: write the two `.todo-alan` DRAFT blocks (hero one-liner + the arc memoir).
3. Watch for Liquid Web finishing the vhost provisioning. Once they do, `cat /etc/apache2/sites-available/mypaperclock.cc.conf` (or `sites-enabled/`) confirms exact paths.
4. SSH-key setup on the mac (deploy.sh header has the steps) so deploy is ready when LW finishes.

**For Claude (next session):**

- If asked: walk through the server-hardening pass (SSH keys, disable password auth, ufw, fail2ban, unattended-upgrades). ~30-45 min.
- If asked: draft the charter-page rendering (pick approach + render).
- If asked: add a site track to `claude-work/STATUS.md` and reconcile with the existing tracks.
- If asked: address the A3 question on viewer hosting.
- Once LW finishes provisioning: walk Alan through SSH-key + ~/.ssh/config setup and exercise deploy.sh end-to-end (task #4).
