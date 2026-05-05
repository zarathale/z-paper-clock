---
date: 2026-05-04
start_time: "15:00"
end_time: "15:45"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Day one of Claude-as-lead. Charter signed (`claude-work/CHARTER.md` v1.0, effective 2026-05-04). Pick up at "let's kick it off here" and execute charter §10 row 8 first move (a) — build out the `claude-work/` skeleton. Tee up the next moves.

## What was done

### Read-in

Charter (full, in-context). WORKPLAN.md (full — the legacy-as-of-today live working surface). LAYER-CONVENTIONS.md (full — the doc I now share co-authoring on per CHARTER §10 row 2). The two most recent session notes: `2026-05-04-0815_cowork_marker-bound-fold-ids.md` (referenced from WORKPLAN; not re-read since it's already summarized in the SVG-layer-authoring track) and `2026-05-04-1100_cowork_face-graph-diagnostics.md` (full — the freshest active thread). Quick repo scan via Glob to confirm what's where; `claude-work/` was empty save for CHARTER.md, `alan-work/` doesn't exist yet, `work/` populated and frozen.

### Day-one skeleton landed

Per CHARTER §10 row 6 + the agreed first-move (a):

- **`claude-work/STATUS.md`** — the live working surface, replacing WORKPLAN.md. Eight tracks carried forward from WORKPLAN (Charter rollout NEW; Operations layer CLOSED; the other six reshaped to the new voice with shorter recent-logs that point back at WORKPLAN for pre-charter history). Repo-hygiene downgraded from `active` to `paused` since the 2026-05-03 filesystem restructure shipped cleanly and there's nothing to drive proactively right now.
- **`claude-work/QUEUE.md`** — modest size on purpose per CHARTER §9. Three "Now" entries: capture the 6 pending pieces, ship the face-graph-diagnostics CODE_PROMPT, tag 123 pieces in tag-pieces.html. One "Soon" entry: pick the first piece end-to-end (pendulum candidate not yet locked).
- **`claude-work/DECISIONS.md`** — parallel to CLAUDE.md's Architectural Decisions table. Four rows: charter signed (#1), STATUS/WORKPLAN succession (#2), LAYER-CONVENTIONS co-maintenance routine (#3 — light, one paragraph, "for shipped conventions edits are unilateral with a footer note; for in-motion conventions both sides talk first"), preview.html ↔ work/viewer/ architecture deferred (#4, marked open).
- **`claude-work/to-alan/README.md`** — explainer for the rework dropbox per CHARTER §3 + §5. Empty otherwise.

### Calls deferred deliberately

- **`preview.html` ↔ `work/viewer/` architecture (SPEC open question 0.6.13).** This was the third of the four CHARTER §10 row 8 first moves, and the inherited SPEC's biggest structural call. Deferred to the next cowork conversation. Reasoning captured in DECISIONS.md #4: the face-graph diagnostic ship + the post-diagnosis algorithm pick will teach more about what `preview.html` is becoming. Picking the architecture now would be premature.
- **First piece end-to-end (CHARTER §6 #2).** Pendulum bob (piece 094) is the inherited candidate per the WORKPLAN POC track; not locked. Earmarked in QUEUE.md "Soon" for the next cowork conversation against `source/transcriptions/embedded-labels.md` §II.C.
- **WORKPLAN.md banner.** WORKPLAN.md is read-only for Claude per CHARTER §4. Surfacing in the closing message that Alan might want to add a one-line top-of-file banner pointing readers at STATUS.md, since the charter's "becomes legacy" doesn't show up to a reader who lands on WORKPLAN.md cold.

## Files Created / Modified

| File | Action | Notes |
|---|---|---|
| `claude-work/STATUS.md` | created | Live working surface, replacing WORKPLAN.md. |
| `claude-work/QUEUE.md` | created | 3 "Now" + 1 "Soon" entries. Modest. |
| `claude-work/DECISIONS.md` | created | Four decisions; #4 is the next architecture call, marked open. |
| `claude-work/to-alan/README.md` | created | Dropbox explainer. |
| `sessions/2026-05-04-1500_cowork_charter-signed-day-one.md` | created | this note. |

No edits to inherited root-level docs (read-only for Claude per CHARTER §4). LAYER-CONVENTIONS.md untouched today. WORKPLAN.md untouched today (banner question raised in the closing message, not actioned).

## Open questions

1. **The architecture call (DECISIONS #4)** — when does it land? My instinct is: after the face-graph diagnostic ship + after the post-diagnosis algorithm refactor lands and we see whether preview.html's parser holds up under shared-edge or needs a deeper rewrite. That's likely 2-3 cowork sessions away, not this week.
2. **First piece pick** — the pendulum candidate is the obvious read but not locked. Worth a cowork pass through `embedded-labels.md` §II.C before committing.
3. **Code-mode lane back?** Charter §7 parks the question. Cowork can't run the dev server for a future Vite viewer; preview.html is fine as-is from here. The question becomes acute the moment the architecture decision (DECISIONS #4) picks "build a fresh viewer." Until then, parked.
4. **WORKPLAN.md self-flagging.** Alan-side: a one-line banner pointing at STATUS.md would be considerate to anyone landing on the file cold. Not in my edit lane.

## Next-session handoff

**Most likely next move:** Code session (Alan's hands) shipping `CODE_PROMPT_preview-html-face-graph-diagnostics.md` per QUEUE entry #2 — this is the highest-leverage existing thread. After that ships, the next cowork session is reading 066's diagnostic output and picking between shared-edge / cut-trim / multi-tag for the algorithm refactor.

**Parallel-pullable** by Alan (no Claude needed): scan the 6 pending pieces (QUEUE #1); tag 123 pieces in `tag-pieces.html` (QUEUE #3). Either or both can land independent of any cowork session.

**Cowork-needed-before-actionable:** first piece end-to-end pick (QUEUE "Soon"); preview.html ↔ work/viewer/ architecture decision (DECISIONS #4 still open).

## Cowork Commit Message

Subject:

```
sign claude-work charter v1.0; build day-one skeleton (STATUS/QUEUE/DECISIONS/to-alan)
```

Body:

```
Charter signed and effective 2026-05-04. Claude takes the lead on building the
clock; Alan steps into a human-assistant role. claude-work/ holds Claude's lead
zone; alan-work/ holds Alan's authoring zone (created lazily as we copy out of
the now-frozen work/). The rest of the repo is read-only background. Full role
split, folder rules, scope, and amendment policy in claude-work/CHARTER.md.

Built the day-one skeleton per CHARTER §10 row 6:
- STATUS.md: live working surface, replacing WORKPLAN.md. Eight tracks carried
  forward (Operations layer closed; Charter rollout opened; Repo hygiene
  downgraded paused).
- QUEUE.md: pull-based, modest size per §9. Three "Now" entries (capture 6
  pending pieces; ship face-graph-diagnostics prompt; tag 123 pieces); one
  "Soon" entry (first end-to-end piece pick).
- DECISIONS.md: parallel to CLAUDE.md's Architectural Decisions. Four rows;
  #4 (preview.html ↔ work/viewer/ architecture) deliberately marked open.
- to-alan/README.md: rework-dropbox explainer.

Two of the four agreed §10 row 8 first moves are deferred deliberately:
preview.html ↔ work/viewer/ architecture waits until the face-graph diagnostic
ship + algorithm pick teach more; first end-to-end piece needs a cowork pass
against embedded-labels §II.C to confirm pendulum candidate.

WORKPLAN.md not edited (read-only for Claude per §4). A one-line top-of-file
banner pointing at STATUS.md would be welcome if Alan wants to drop one in.

See sessions/2026-05-04-1500_cowork_charter-signed-day-one.md for the full
kick-off note.
```
