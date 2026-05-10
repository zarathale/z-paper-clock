# Infrastructure — mypaperclock.cc

_Operational reference for the deployed site. Captures domain, hosting, deploy flow, and known constraints. Co-owned per CHARTER A2 (2026-05-09)._

## Domain

- **Hostname:** `mypaperclock.cc`
- **Registrar:** TBD — fill in
- **Purchased:** 2026-05-09 (Alan)
- **Renewal:** TBD — set calendar reminder ~30 days before expiry once known
- **WHOIS privacy:** TBD

Note on the name: the *my* prefix echoes the book's title (*Make Your Own Working Paper Clock* — *your own*). Slight resonance worth keeping in mind when voice gets drafted.

Note on the TLD: `.cc` is the ccTLD for Cocos (Keeling) Islands but is widely used internationally as a generic alternative. No practical issues.

## Hosting

- **Provider:** Liquid Web
- **Server IP:** `50.28.105.83`
- **Server hostname:** `smooth-relation.metalseed.io`
- **OS:** Debian GNU/Linux (kernel 6.1.0-42-amd64) — confirmed 2026-05-09
- **Plan / tier:** TBD (self-managed; no WHM or cPanel; Liquid Web staff handle initial vhost provisioning)
- **Web server:** Apache (apache2) — strongly indicated (`/var/www/html/` is present, the apache2 package's default doc root)
- **PHP version:** TBD (irrelevant for v0; site is fully static)
- **Other sites on this box:** `alandlytle.com`, `scaenacraft.cc` (both follow `/var/www/<sitename>/` convention)
- **Document root path:** `/var/www/mypaperclock.cc/` — confirmed by convention from sibling sites (2026-05-09). Liquid Web staff are provisioning the vhost; document root will exist once they finish.

## DNS

- **A record:** `mypaperclock.cc` → `50.28.105.83` _(verify it resolves correctly once propagated)_
- **CNAME:** `www.mypaperclock.cc` → `mypaperclock.cc` _(recommended; redirect www → apex)_
- **MX:** N/A unless we want email at the domain
- **TXT (SPF/DKIM/DMARC):** N/A unless email
- **Nameservers:** TBD (usually Liquid Web's by default; Cloudflare in front is an option if we want a CDN/WAF layer)

## SSL/TLS

- **Cert source:** TBD — Liquid Web typically offers free Let's Encrypt via AutoSSL (on cPanel) or paid certs
- **HTTPS redirect:** Plan to enforce — the site should be HTTPS-only
- **HSTS:** Defer until cert is verified working in production

## Deploy

See `site/build/README.md` for the deploy section once the build folder is real. Short version: **Alan ships, Claude authors.** Same pattern as git — Claude doesn't push to live directly. Three deploy-mechanism options on the table; v0 default is manual SFTP from Alan's mac until shipping cadence justifies automation.

## Credentials

**Not in this repo.** Ever. SFTP credentials, registrar login, control-panel access — all live in Alan's password manager. This file names what services exist; it does not store how to log in.

If a credential is ever needed for an automated step (e.g. a future deploy script):

1. Alan stores the credential in his shell environment or a local `.env` file (gitignored).
2. The script reads from environment, never from a committed file.
3. CI-based deploys (option 3 in `site/build/README.md`) use GitHub Actions secrets, which never live in the repo.

## Charter cross-reference

**Direction-update from CHARTER §2 / resolved decision #4.** That decision named "GitHub Pages off this repo" as the public host for the eventual viewer. The new `mypaperclock.cc` / Liquid Web setup makes Liquid Web the public host for *the site*. Two open follow-ups:

1. **Is the eventual viewer still GitHub Pages, or does it live at `mypaperclock.cc/viewer/` (or similar)?** Same domain feels right for cohesion, which would shift viewer hosting to Liquid Web too. That's a charter-relevant change worth an explicit decision.
2. **A3?** If the answer to #1 is "shift viewer to Liquid Web," this is a substantive amendment per CHARTER §12 (touches resolved decision #4 in §6). Park as a pending question until we settle.

---

*Last updated: 2026-05-09 — initial scaffold from Alan's domain purchase. Many fields TBD; fill in as we learn the Liquid Web setup.*
