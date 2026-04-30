---
date: 2026-04-30
start_time: "17:30"
end_time: "17:40"
mode: code
participant: Zarathale (Alan)
target: M1-fix-pipeline-trace
orchestration_prompt: CODE_PROMPT_M1-fix-pipeline-trace.md
source: retroactive — assembled from commit 1047271 + the parent session note's deferred-item callout, during the 2026-04-30-2100 repo audit
---

## Goal

Resolve the 4 validator ERRs that the parent fix-pipeline-trace Code session (`sessions/2026-04-30-1500_code_M1-fix-pipeline-trace.md`) deferred. Those ERRs came from `piece-004.json`'s 4 positioning-guide connections to pieces 91/92 — the connections are one-directional (the printed labels live only on piece 4's surface), but `04-validate-sidecars.py` required reciprocity for any connection where the target sidecar exists. Fix shipped on the same branch (`claude/M1-fix-pipeline-trace`) as a follow-on commit before PR #2 merged.

## Context

This is a retroactive note. The work shipped as commit `1047271` on 2026-04-30 between the parent session's commit (`409eddd`) and the merge of PR #2 (`b4e1c85`). The parent session note flagged the issue explicitly under "Open questions" as "Deferred — not in scope for this session"; the deferred work was then taken up on the same branch without a session note. The 2026-04-30-2100 repo audit surfaced the gap; this note backfills it. Per CLAUDE.md, retroactive notes are valid as long as they reconstruct what shipped.

## What was done

Two file edits in one commit:

- **`work/pieces/004/piece-004.json`** — added `"reciprocal": false` to the 4 positioning-guide connections (`91a`, `91b`, `92a`, `92b`). These alignment references are expressed only on piece 4's surface (piece 4 carries the dotted curved/square outlines that locate where the spacers glue down); pieces 91 and 92 carry no outward reference back. Marking these one-directional matches the design intent surfaced in the parent session.

- **`work/pipeline/04-validate-sidecars.py`** — skip the reciprocation check when a connection has `"reciprocal": false`. The validator now exits 0 with 3 WARN (piece 25 cross-plate, sidecar not yet authored) and 0 ERR.

## Branch / commit

Branch: `claude/M1-fix-pipeline-trace`
Commit SHA: `1047271`
PR: #2 (merged 2026-04-30 as `b4e1c85`)

## Open questions

None blocking. The 3 remaining validator WARNs are cross-plate references to piece 25 (plate C, sidecar not yet authored) and resolve naturally during M2's plate-C tracing pass.

## Next-session handoff

PR #2 merged shortly after this commit. The next active work was the 2026-04-30-1800 cowork rescan-restructure session (which archived M1 outputs after Zarathale observed gutter warp on piece 31 in Inkscape). The `reciprocal: false` flag and the validator's support for it carried forward into the archive — they remain documented behavior under the chunk-and-crop pipeline.
