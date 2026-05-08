---
date: 2026-05-07
start_time: "20:30"
end_time: "20:45"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Foreground the charter's Claude-leads-Alan-enables stance inside `CLAUDE.md` itself, so a fresh Cowork session loads the operating posture without having to crack open the charter.

## What was done

Added a new section **"Operating Stance — Claude Leads, Alan Enables"** to `CLAUDE.md`, placed as the first content section (between the intro blockquote and "What This Repo Is"). Three short paragraphs:

1. Names the lead/enable split directly. Claude drives planning, sequencing, scope, architecture, queue, conventions in motion. Alan runs the scanner, hand-authors SVGs in Affinity, runs git, merges PRs — owns cuts and labels (muscle memory from physically building the clock in the 90s).
2. Tells a fresh session how to behave: **don't default to "which direction would you like to go."** Propose a next move; pull from `claude-work/STATUS.md` + `claude-work/QUEUE.md`; surface trade-offs out loud; treat Alan's silence as not-a-stop.
3. Points at `claude-work/CHARTER.md` as a read-when-warranted reference (scope/ownership/stance questions), explicitly NOT as a routine startup step.

Session Startup checklist deliberately not touched — the user said the charter shouldn't be a forced read every session, and adding it there would have been exactly that.

Drafting beats: started with a Read of the existing CLAUDE.md top section to confirm structure, then surfaced two design questions before drafting (metaphor vs. direct; lift verbatim or fresh draft). User answered "stay direct, no fake metaphor layer needed; this is a hobby working paper clock model project." Read `claude-work/CHARTER.md` end-to-end to align language with what the charter actually says (esp. §3 role descriptions and §9 "loud one"). Wrote the section in one Edit pass.

## Open questions

Two stale references in `CLAUDE.md` flagged in chat but **not fixed** in this pass — both noted to user, neither acted on:

- **Line 17 metaphor is stale.** *"…the build is a stage production with Zarathale as director and Claude as the production team."* Director = creative authority, production team = executes; that's the pre-charter framing and now actively contradicts the new stance section. Suggested fix in chat: delete the sentence or invert it ("Claude leads the build; Alan brings the scanner, the X-Acto, and four decades of having actually held this thing in his hands"). User did not respond to that flag before asking for the commit message.
- **Session Startup step 2 points at `WORKPLAN.md`.** Per charter `DECISIONS.md` #7, WORKPLAN was frozen at charter sign-off and replaced by `claude-work/STATUS.md`. The status table further down the same `CLAUDE.md` already says this; the startup checklist hasn't caught up. A fresh session loading the checklist still gets pointed at a frozen doc as its live work surface.

Both are queued for a later pass; neither blocks anything authored in this session.

## Next-session handoff

If picking up tonight's thread: decide whether to fix line 17 + Session Startup step 2 in a follow-up doc pass, or fold them into the next time `CLAUDE.md` is opened for a different reason. Both are small enough to live in any pass that touches `CLAUDE.md`.

Otherwise the live work surface is `claude-work/STATUS.md` + `claude-work/QUEUE.md` — pull from there and pick the next move per the new operating-stance directive.
