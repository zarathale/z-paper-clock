# site/

The outward-facing zone of z-paper-clock — strategy, voice, content, and (eventually) the built public site for the project.

Co-owned by Alan and Claude, established by charter amendment **A2 (2026-05-09)**. See `claude-work/CHARTER.md` §4 (folder split + read/write rules), §6 (parallel track to the build), and the A2 amendment row in the log for the formal scope and co-ownership rules.

## What lives here

This folder is mostly empty for now — populating as we go. Anticipated structure:

- **strategy/** — design direction, target audience, voice notes, sitemap, content plan. Where we work out *how* to talk about the project before we write the site itself.
- **content/** — drafts of the actual long-form material (the 30-year arc, the build-notebook entries, captions for pieces, copy on the collaboration).
- **build/** — site code and static assets, when we get to the build phase.

Subfolders land when there's something to put in them. Don't pre-build empty rooms.

## Direction (short form)

A site about a personal hobby project, deliberately niche.

- **Angle A** (the long-arc memoir — *built this in the mid-90s, rebuilding it in three.js now, with an AI collaborator*) is the frame.
- **Angle C** (open notebook of the mid-flight build) provides the substance.
- **Angle B** (the 3D viewer as the headline) is the destination, once M3+ lands.
- The Claude-collaboration angle is **foregrounded**, not buried.

Audience: horology-craft community + LLM / working-with-AI crowd.

Visual direction inherits from the project itself — when `preview.html` and the eventual viewer evolve their aesthetic, the site evolves with them. One source of truth, exact linking mechanism TBD at design time.

## Co-ownership in practice

Read/write for both. Default tilt is Claude-leads-with-Alan-input (matching the rest of the charter), with two carve-outs where Alan leads:

- Personal-arc content (the 30-year story; the physical-clock memory; anything that's Alan's lived experience).
- Voice-on-Alan's-behalf — any copy putting words in Alan's voice needs Alan's sign-off before it goes live.

The `claude-work/to-alan/` rework dropbox applies here like everywhere else: when Claude needs Alan to author or revise something site-side, the ask lands in `to-alan/site-<topic>/` with a short brief.
