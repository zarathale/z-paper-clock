# Site Strategy — z-paper-clock

_First-pass strategy for the public-face site established by charter amendment **A2 (2026-05-09)**. Living doc; revised as we draft actual content and discover what works. See `claude-work/CHARTER.md` §6 + amendment A2 for the formal scope._

---

## Frame

A small, niche, personal site about an unfinished hobby project. The frame is the long-arc memoir (Angle A): *In the mid-1990s I built this paper clock from a book. Three decades later, I'm rebuilding it in three.js, with an AI collaborator.* That sentence is the whole thing. Everything else on the site is in service of that frame, or on the way to it, or coming back from it.

The site doesn't sell anything. It doesn't teach as its main job. It doesn't aspire to general appeal. It's for two specific kinds of reader, and it can be honest with both because both are inclined to read carefully.

## Audiences

**The horology-craft reader** comes for the clock. They want to see the pieces, understand how the escapement works, look at hand-traced SVGs, maybe trace a path back to Rudolph's book if they don't already have a copy. They appreciate that the source isn't being republished — they know what that line is. They'll click through to per-piece detail when it lands. They'll forgive a half-built site if the artifact is real.

**The LLM / working-with-AI reader** comes for the collaboration. They want specifics, not testimony — the charter, the role split, the queue, the rework dropbox, the moments where the model bends. They've read enough breathless AI commentary to be wary of it. The site treats the collaboration as material, not as a marketing angle: here's what we wrote, here's how we work, here's what doesn't work yet.

The two audiences overlap less than you'd think and that's fine. Don't write to a synthetic third reader interested in both equally. Let each find their door.

## Voice

Working-and-curious. Full sentences. Honest about state. Not corporate, not breathless, not cute. Specifics over abstractions. When a thing is half-built, say it's half-built. When something works, say what it does and don't oversell it. CLAUDE.md's texture (*"hobby project. Keep the tone working-and-curious, not corporate."*) is the master sample.

Avoid-list:

- Don't perform humility. The project is what it is.
- Don't perform AI excitement. Same reason.
- Don't write *journey*, *passion project*, *crafted*, *artisan*. They show up because they've been written before, not because they fit.
- Don't pad the personal-arc sections with sentiment that wasn't in the original feeling. The arc is moving on its own; let it be.

## Structure — v0 (what ships first)

A single long-scroll homepage with a couple of side trips. Sitemap:

- `/` — the spine of the site. One long page, sectioned roughly:
  1. **Hero.** A still or short loop of the clock. The one-sentence frame.
  2. **The arc.** Alan's voice. 1996 → today. Tight, not sprawling.
  3. **What this is.** The project, the book, the scope note (study side personal; build side derivative + public).
  4. **The pieces.** Visual section. v0: the embedded `preview.html` for one or two emblematic pieces (pendulum bob is the obvious POC; an anchor or escape wheel for the mechanism feel). Later: gallery + viewer.
  5. **Mid-flight.** The open-notebook frame. Live counters (X of 123 pieces authored), recent decisions, what's on the bench. Pulled from the repo, not hand-curated.
  6. **The collaboration.** Claude as lead, Alan as enabler. Abridged charter; link to the full version as a side trip.
  7. **What's next.** Roadmap glimpse. Plain about what's unbuilt.
  8. **Colophon.** Book's status, attribution, repo link.

- `/charter` — the full charter, lightly contextualized. Stands alone so it can be linked directly without forcing a scroll through the front page.
- `/notebook` _(eventually)_ — curated longer-form entries from `sessions/`, not the full feed.

Three URLs at v0; one of them mostly a long page. That's enough.

## Structure — v1 (when M3+ ships)

Same shape, but **The pieces** becomes the headline. The 3D viewer embeds inline; per-piece pages (`/pieces/NNN`) start landing with the inspect panel and detail. Hero may shift from still to live viewer. Angle B begins carrying the site.

The arc, the mid-flight section, the collaboration — all stay. They were never temporary.

## Three angles, woven

| Angle | Role | Where it lives |
|---|---|---|
| **A — long arc** | the *frame* | Hero, arc section, colophon. Bookends. |
| **C — open notebook** | the *substance* | Pieces (real artifacts, honestly half-finished), mid-flight, linked charter, linked notebook. Carries the middle. |
| **B — 3D viewer** | the *destination* | Pieces section, growing. v0: preview.html on a couple pieces. v1: full viewer. |

The collaboration thread runs through all three: explicit in §6 of the page, implicit everywhere else. The site is itself a Claude-led artifact; the charter's existence is part of what the site is *about*, not metadata in the footer.

## Visual

Inherit from the project. The project's aesthetic is the master; the site is downstream.

The site doesn't pick its own colors, type, or texture — it pulls them. Mechanism is task #2 in the queue (three plausible options: shared CSS custom-properties file at repo root, build-time tokens, or the site loads `preview.html`'s stylesheet directly). Whichever wins, the principle stays: when the project's aesthetic evolves (cream warms a shade, texture shifts, type changes), the site evolves the same day, no hand-sync.

Short-form direction (matching the charter): cream paper background, scan-textured slabs where appropriate, illustrative not photographic (per resolved decision in CHARTER §2 — photographic is M5 polish, much later), a serif body type at home with the book's era, mono for code and repo references, restrained color, one accent at most.

## What this site is *not*

- Not a republication of *Make Your Own Working Paper Clock*. Page scans don't appear in deployed assets. The book is in print; if you want to build the clock, buy a copy. The colophon says this plainly.
- Not a tutorial. There are better places for that.
- Not a portfolio piece. No "Hire me" button, no list of services.
- Not aimed at the general public. Niche by design.
- Not a launch. There's no v1.0 button to push. The site exists from the day it's a paragraph and a hero image; it grows.

## Phasing

| Phase | When | What's on the page |
|---|---|---|
| **v0** | Soon | Hero, arc, what-this-is, two embedded pieces via preview.html, mid-flight, abridged collaboration, what's next, colophon. `/charter` side trip. |
| **v1** | After M3+ ships | Pieces section becomes the headline; viewer embeds inline; per-piece pages start landing. Everything else holds. |
| **v2+** | After M5+ | Polish pass. Photographic aesthetic if it ships. More notebook entries. Mechanism animation if M6 lands. |

We don't wait on v1 to launch v0. v0 is enough.

## Open questions

For the next strategy iteration, or for chat:

1. ~~**Domain.**~~ **Settled 2026-05-09: `mypaperclock.cc`** (Liquid Web hosting; see `site/INFRASTRUCTURE.md` for the operational details). The *my* prefix echoes the book's title (*Make Your Own Working Paper Clock* — *your own*); voice can lean on that resonance lightly without overworking it.
2. **Personal-arc length.** Can be 80 words or 800. My instinct: middle. Dense, not lean, not sprawling. Converges after Alan's first draft.
3. **Hero image.** A photograph of Alan's 1996 build (if any survived), a render from the eventual viewer, a still from preview.html, or commissioned art? Affects scheduling.
4. **Live-counters mechanism.** "X of 123 pieces authored" wants to pull from `work/state.json`. Build-time render or runtime fetch? Tied to whatever build system the site uses (also TBD — task #2 territory).
5. **The collaboration section's specificity.** Foregrounded ✓. But — earnest prose, specific-with-receipts (charter excerpts, session note pulls), or both? Instinct: both, weighted toward receipts because they're what make it credible to the LLM-reader audience.
6. **`/notebook` curation.** When that lands: who picks which session notes to surface? Probably Claude proposes, Alan signs off, given the personal-arc carve-out. Defer until there's actually a notebook section to fill.

---

*Last updated: 2026-05-09 — initial draft, paired with the A2 amendment landing the same session. Expected to iterate as we draft actual content; the open-questions list is the queue for the next pass.*
