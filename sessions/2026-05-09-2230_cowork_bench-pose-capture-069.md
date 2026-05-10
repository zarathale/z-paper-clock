---
date: 2026-05-09
start_time: "22:30"
end_time: "23:50"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Confirm PR B archive, then use Bench mode to capture assembled poses for the anchor cluster
(065–069) — or at minimum enough to make PR C's verification checklist runnable.

## What was done

**Archive confirmation.** `CODE_PROMPT_preview-html-bench-transform.md` was already in
`_archive/code-prompts/` with `status: shipped` — the PR B Code session had moved it on
close. Nothing to do.

**Bench mode diagnosis — translation.** Alan reported click-drag not working. Root cause:
TransformControls only responds when you grab the colored axis handles (arrows), not the
piece mesh itself. Panel sliders work as an alternative for both translate and rotate.
Confirmed working once handles identified.

**R key dual-listener bug fixed.** Two `keydown` listeners both responded to R:
- `window` listener (line 546): `setTransformMode('rotate')` + `e.preventDefault()`
- `document` listener (line 1597): `reloadCurrentPiece()`

`e.preventDefault()` doesn't stop the second listener. Net effect: pressing R both switched
TC to rotate mode AND reloaded the piece, wiping any in-progress transform. Fix: added
`if (e.defaultPrevented) return;` guard to the reload listener. One line, `preview.html`.

**Dump Face Graph clarification.** Button is explicitly disabled in `renderPanelsFirstScene`
(line 3988) — it's cut-line-first instrumentation only. `window.__lastFaceGraph` is also
only written in the cut-line-first path. For panels-first pieces like 069, the console
command is: `copy(JSON.stringify({ panels: [...parsed.panelsFirst.panels.keys()], folds:
parsed.panelsFirst.folds, hingeTree: parsed.panelsFirst.hingeTree, ... }, null, 2))`.
Note: `hingeTree.nodes` appears `{}` in JSON output because it's a `Map` — the tree IS
built correctly internally.

**Save assembled pose workflow clarified.** The console dump Alan obtained earlier was raw
SVG parse data (panel geometry, fold-line coordinates), not the UI state. The correct path
is the "Save assembled pose" button in the sidebar, which reads live slider values.

**069 sidecar created — first in the repo.**
`work/pieces/069/069.json` written with:
- `assembled.folds`: all 10 folds at −90° (all-flat "Fold all" at 100%)
- `assembled.transform`: translation [0, 7.1, 0], rotation_deg [99.5, 0, 0], XYZ order,
  frame: cluster, origin: pivot-anchor

Piece reloads fully folded in assembled pose on next load. First sidecar in the repo.

**068 authoring issue identified — not fixed this session.**
Loaded 068 after 069. Banner: "Disconnected fold components: 2 sub-trees." The fold
adjacency graph has two components:
- Main pane chain: pane1–pane8, flap1, flap2, taba, tabb, tabff, b, g (connected)
- Slot cluster: c1, c2, sidel, sider (connected among themselves via fold-c1-c2,
  fold-sidel-c2, fold-c2-sider; but NO fold connects this cluster to any pane)

Missing: a fold line on the boundary between the slot panels and the adjacent main panel.
Alan needs to add this in `068.af` and re-export. Diagnostic console command given to
check which folds touch c1/sidel; deferred to next session.

## Open questions

- 068 two-component fold graph: which pane borders c1/sidel? Author the missing fold in
  Affinity, re-export, verify sub-trees warning clears.
- Anchor cluster sidecars 065, 066, 067, 068 still pending — only 069 captured. PR C
  verification checklist needs all 5 before "Load cluster → anchor" can be fully tested.
- `pivot_clusters.anchor` only lists [067, 069] in `connection-graph.json`. PR C's cluster
  load resolves pieces from that list — 065/066/068 won't auto-load. PR C Code session
  needs to expand cluster lookup transitively (follow edges) or rebuild the list to include
  all 5.

## Next-session handoff

1. Fix 068 fold authoring (missing pane→c1 fold line). Console: `parsed.panelsFirst.folds
   .filter(f => f.a === 'c1' || f.b === 'c1' || f.a === 'sidel' || f.b === 'sidel')` to
   confirm before reopening Affinity.
2. Continue anchor cluster pose capture: 067 next (pivot-anchor piece, cluster reference).
3. After all 5 sidecars land, update `connection-graph.json` anchor cluster piece list to
   include all 5, then hand PR C to Code.
