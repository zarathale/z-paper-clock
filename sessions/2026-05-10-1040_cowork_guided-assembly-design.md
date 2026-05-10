---
date: 2026-05-10
start_time: "10:40"
end_time: "11:13"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Design the guided assembly interface for `preview.html` — the step-by-step mode that walks
Alan through assembling the anchor/pendulum cluster (and eventually all clusters) using the
connection graph as the assembly specification.

## What was done

### Design decisions settled

- **Step types are open-ended** — not just "add piece." Types include: `add-piece`, `fold`,
  `glue-self`, `glue-cross`, `glue-no`, `lock-shape`, `snap-connection`, `insert-axle`,
  `install-bearing`, `orient`, `pin`, `check`. Taxonomy is extensible as assembly surfaces
  new action types.

- **"Let it dry" → `lock-shape`** — the permanence-state-shift when glue sets is modelled
  as a `lock-shape` step with a confirmation popup:
  > "Lock [piece]'s shape? Like letting the glue dry — folds and self-connections are set
  > from here. [Lock it] [Keep editing]"
  Two distinct lock moments: after `glue-self` (piece's own shape set) and after
  `glue-cross` (joint between pieces set).

- **Guided mode = Cluster mode + a step sequence layer** — not a fourth mode. The stepper
  drives what's highlighted and what the sidebar says; all snap/fold mechanics are the same
  substrate. Guided on = stepper active. Guided off = freeform Cluster.

- **Author from the book, not from graph traversal** — Claude reads `instructions.md`,
  interprets the prose into typed steps, and marks `requires_human: true` for anything
  requiring visual/tactile judgment. The connection graph fills in the specific tab/landing
  pairings the prose leaves to the letter labels.

- **Step granularity** — piece-by-piece (one piece fully prepared and attached per step
  group), with individual connection-level steps available as drill-down. "Snap all N pairs"
  is the default; individual pair snaps are available if residual is large.

- **glue-no is explicit** — where the book says NOT to glue (e.g., tongue 031 into slot,
  blade 072 held by pin), the step type is `glue-no` so the guided mode can actively warn
  against gluing.

### Artifacts produced this session

1. **`claude-work/INSTRUCTIONS-ANNOTATED.md`** — complete annotated read of all assembly
   instructions (§I through §III). Every section tagged with `[RULE]`, `[STEP type]`,
   `[GRAPH]`, `[GAP]`, `[HUMAN]`, `[WARN]`, `[MECH]`, `[ORDER]`. Permanent reference —
   eliminates re-reading source instructions in future sessions.

2. **`claude-work/state/guided_sequence_anchor.json`** — complete §II.C guided step
   sequence: 68 steps, 24 requiring human judgment, covering all pieces 065–072, 093–095,
   097–098. Schema includes: step type, piece(s), description, source quote, requires_human,
   human_note, graph_edges (for snap steps), depends_on (DAG ordering), ui block (what to
   show in the stepper sidebar and what popup/panel to open).

### Key learnings from the book

- **§I.D is the assembly spine:** fold → glue-self → lock-shape → attach → glue-cross →
  lock-shape → next piece. Every piece follows this template without exception.
- **067's axle hole is intentionally loose** — no bearing on 067. Bearings only on 065 and
  069. This is a functional requirement, not an oversight.
- **098 must be bowed before gluing** — spring tension holds the bob on the rod.
  The book doesn't specify bow angle; calibrated by feel.
- **072 (blade) is held by pin, not glue** — removable by design.
- **5-inch brace spacing** inside 094 is the only physical measurement given in the book.
- **Escapement engagement** = 1.0–1.5mm from tooth tip. Anchor axle height is the tuning
  parameter. Requires iterations.
- **Gap G4**: 067's direct connections to 065/066 are not in current valid graph edges.
  Either 067 connects via 069 as intermediary, or edges need authoring. Flagged in both
  artifacts (INSTRUCTIONS-ANNOTATED.md §II.C and guided_sequence_anchor.json step c-265).

## Open questions

- **Gap G4**: Does 067 connect directly to 065/066, or only via 069? Needs authoring check
  when 067's SVG is complete.
- **093a/093b**: The book's "six pieces designated 93" = six copies; our repo split 093 into
  two distinct shapes (093a, 093b). Which variant(s) make up the braces? Verify against
  plate G scan.
- **Snap CODE_PROMPT bugs**: field names wrong (prov → provenance, partner_match →
  matched_panel, tab/letter asymmetry), verification checklist uses non-existent
  pivot-anchor sphere type, `edgeKind` undefined in snapPair. Fix before handing to Code.
- **Progress panel**: Persistent sidebar showing all cluster connections + status dots
  (proposed in snap prompt review). Likely belongs in snap CODE_PROMPT as an enhancement.

## Next-session handoff

1. Fix the snap CODE_PROMPT (field name bugs + verification checklist + bidirectional
   partner lookup + lock-shape/progress-panel additions from this session's design work).
2. Once 067's SVG is authored: re-run `build_assembly_graph.py`, check for 067↔065/066
   edges, insert snap-connection step between c-260 and c-270 if found.
3. The annotated instructions cover §II.A and §II.B at a high level — those sections will
   need their own `guided_sequence_*.json` files when those clusters are ready.
4. Consider whether `guided_sequence_anchor.json` schema needs a top-level
   `progress_connections` block listing all cluster edges for the persistent sidebar panel.
