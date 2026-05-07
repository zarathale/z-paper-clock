---
date: 2026-05-06
start_time: "18:00"
end_time: "18:00"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Close out the Code session that shipped PR #18 (inferred-connections audit-side merge) and update repo state docs to reflect the new ship.

## What was done

- Verified ship state of `CODE_PROMPT_build-assembly-graph-inferred.md` — already flipped to `status: shipped, shipped: 2026-05-06` by the Code session (`sessions/2026-05-06-1700_code_build-assembly-graph-inferred.md`). Ship-time italic header in place.
- Verified `claude-work/state/connection-graph.md` regenerated with new `prov` column and the "Inferred connections" / "Inferred conflicts" sections (currently empty — no sidecars authored yet, so all 33 edges are `authored`). Legacy `pivot_clusters` flat-list shape preserved per spec.
- Updated `claude-work/STATUS.md`: Charter rollout track recent log gained the PR #18 ship entry; preview.html iteration track next-action narrowed from two queued CODE_PROMPTs to one (assembled-pose); recent log gained the PR #18 cross-reference entry. Footer dated.
- Updated `claude-work/QUEUE.md`: old Now #2 (inferred-connections Code session) struck through and migrated to Recently shipped with PR-#18 reference; bob batch + tag-pieces renumbered #2/#3; Soon entries renumbered #4/#5. Footer dated.
- Doc-swept downstream surfaces: `LAYER-CONVENTIONS.md`'s "Per-piece JSON sidecar" section (added 2026-05-06 evening) is already in the right shape — the schema description is what PR #18 now implements, no edits needed. `ROADMAP.md` and `CLAUDE.md` don't reference the audit script directly. No stale claims to repair.

## Branch / commit

Cowork session — no git operations. Commit message handed to Alan in two code blocks at end of conversation per CLAUDE.md display convention.

## Open questions

None blocking. Sidecars are now a real read surface for the audit; whenever Alan authors the first `connections.inferred[]` entry (probably during gear-train assembly when the instructions text and physical-build knowledge starts compounding), it'll surface in the next graph regen with `provenance: "inferred"` and a warning if it duplicates anything authored.

`pivot_clusters_provenance` is the new richer key on the graph; `pivot_clusters` legacy flat-list stays so `preview.html`'s scene-mode reader doesn't break. If a future preview-side change wants to surface `(authored)` / `(inferred)` annotations on pivot members in the scene, the data is already there.

## Next-session handoff

- **Now #1 in QUEUE.md** is `CODE_PROMPT_preview-html-assembled-pose.md` — preview-side pull. Pairs naturally with PR #18 (the audit now reads sidecars; the preview will write the assembled-fold half of the same sidecar). Either pull when bench time happens.
- **Now #2/#3** are bench (bob batch, 097 collision question) and tag-pieces (123-piece archetype tagging). Pull-when-ready.
- **DECISIONS #4** (preview.html ↔ work/viewer/ architecture call) still deferred. The assembled-pose ship will likely tip it.

## Cowork commit message

(See below in two code blocks per CLAUDE.md display convention.)
