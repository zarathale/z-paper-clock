# DECISIONS.md — Claude-led decision record

_Parallel to the inherited `CLAUDE.md` Architectural Decisions (Closed) table. Decisions made before charter sign-off (2026-05-04) live in their original homes (CLAUDE.md, the relevant CODE_PROMPTs, the relevant session notes). New decisions land here. Co-authored decisions on `LAYER-CONVENTIONS.md` are noted here too, but the file itself stays at repo root._

---

## How this file works

A row per decision. Each row captures:

- **#** — sequential, never reused.
- **Date** — when the decision was made.
- **Decision** — what was chosen.
- **Why** — the one-paragraph reasoning. Future-Claude reads this when tempted to reopen.
- **Type** — `Claude-led` (CHARTER §3 says I pick), `Co-authored` (LAYER-CONVENTIONS or charter amendment territory), `Inherited` (carried forward from pre-charter; cited here for visibility).
- **Reopen?** — `closed` or `open` (still in motion). Once closed, don't reopen without an explicit conversation.

---

## Decisions

### #1 — Charter signed and effective

- **Date:** 2026-05-04
- **Decision:** `claude-work/CHARTER.md` v1.0 signed. Claude takes the lead; Alan steps into a human-assistant role. All decisions captured in CHARTER §10 (rows 1-8) carry forward as decisions of record.
- **Type:** Co-authored (kick-off exception per CHARTER §11).
- **Reopen?** closed.

### #2 — STATUS.md replaces WORKPLAN.md as the live working surface

- **Date:** 2026-05-04
- **Decision:** `claude-work/STATUS.md` is the live work-state surface. `WORKPLAN.md` is frozen as pre-charter record. CHARTER §10 row 7 explicitly resolved this.
- **Type:** Claude-led (within charter mandate).
- **Reopen?** closed.

### #3 — LAYER-CONVENTIONS.md co-maintenance routine

- **Date:** 2026-05-04
- **Decision:** Settled-and-shipped conventions: unilateral edits with a footer date note. New / in-motion conventions: chat first, then DECISIONS row + LAYER-CONVENTIONS update in same pass. Audit script reads LAYER-CONVENTIONS wherever it lives.
- **Type:** Co-authored convention.
- **Reopen?** open-but-stable.

### #4 — preview.html ↔ work/viewer/ architecture (PENDING)

- **Date:** TBD.
- **Decision:** Deferred. Inherited SPEC's question 0.6.13 (graduate / parallel / replace `work/viewer/`) parked. Update 2026-05-05: diagnostic + cut-trim shipped; orientation reset (#6) landed; still deferred.
- **Type:** Claude-led when it lands.
- **Reopen?** open — next architecture decision in queue.

### #5 — Cut-trim uses `fold.start`/`fold.end`, not `authoredStart`/`authoredEnd`

- **Date:** 2026-05-04 (Code session 21:03)
- **Decision:** PR #14's `buildFaceGraph` cut-trim cuts each region using `fold.start`/`fold.end` (extend-to-nearest-silhouette outputs) rather than literal authored endpoints. Avoids the bigBox infinite extension while bridging Alan's standard authoring imprecision (~few units inside silhouette).
- **Why:** literal-spec produced 1 fold-edge for all of piece 066 (0 cuts triggered). Chosen behavior strictly better for normal pieces; partially better for 066 (27 regions, 17/17 markers, 13 residual orphans). Snap-only extension follow-up parked behind orientation reset.
- **Type:** Claude-led, executed via Code. Documented inline in 2026-05-04-2103 session note.
- **Reopen?** closed in current form. Becomes historical record once panels-first dominates.

### #6 — Orientation/awareness model: panels-first (B) + authored-vs-derived (D)

- **Date:** 2026-05-05
- **Decision:** Pivot to panels-first authoring (B). Authoring is authoritative; parser doesn't outsmart it (D). Concrete shape:
  1. New `panels` layer; closed polygon per panel with bare-alias id.
  2. Folds are explicit shared-edge declarations between named panels.
  3. `axles` splits into rotation-only + new `attach-points` layer.
  4. `marks` narrows to construction/registration only.
  5. Closure constraint = edge attribute in panel graph.
  6. 113-116 stay as byte-identical clones.
  7. Cut-line-first stays as legacy parser for pre-pivot pieces.
  8. Snap-only-extension on cut-trim killed.
- **First test:** 069 panels-first authoring brief at `claude-work/to-alan/069-panels-first/`.
- **Why this:** cut-trim ship is the best cut-line-first will be (066: 19→13 orphans, 17/17 markers). Residual is third epicycle on an algorithm reverse-engineering what the SVG already implicitly knows. Panels-first inverts: author draws closed polygons; folds become explicit shared-edge declarations; cut step disappears.
- **Type:** Claude-led, with Alan's pushback channel reserved for "is the authoring shape workable in Affinity."
- **Reopen?** closed — only reopens if 069 authoring proves panels-first impractical at the Affinity surface.

### #7 — Panels-first conventions ratified across the anchor-pendulum batch

- **Date:** 2026-05-05 (evening)
- **Decision:** Conventions locked across 9 panels-first pieces (065/066/067/068/069/070/071/072/099 + 100). 24/24 cross-piece edges valid in `claude-work/scripts/build_assembly_graph.py` audit. Twenty-one specific convention elements (full ref in `LAYER-CONVENTIONS.md`):
  1. Bare-alias panel ids (no `panel-` prefix).
  2. `fold-<a>-<b>` two-panel binding; symmetric; optional `-<deg>` suffix.
  3. `fold-<descriptive>` for single-panel/curved.
  4. Curved fold elements (`<circle>`/`<ellipse>` inside fold layers).
  5. Composite letter panels (`bh`, `ai`); fuzzy substring + shortest-match tiebreaker.
  6. `attach-points` = structural cross-piece refs.
  7. `marks` = same-piece-or-decorative.
  8. `attach-<letter><piece>` = direct face/edge attach.
  9. `landing-<panel-id>` (no piece suffix) = same-piece closure landing.
  10. `align-<letter><partner-piece>` paired symmetric registration.
  11. `cut-<descriptive>` prefix for accommodation/passage cuts.
  12. Bare `hole` = same-piece pin-hole; `hole-<letter><piece>` cross-piece.
  13. `back-<form>` = back-side annotation.
  14. `landing-back-X` vs `back-landing-X` disambiguated by leading token.
  15. Multi-instance markers in `marks` define oriented frame for N≥2.
  16. Affinity collision-suffix tolerance (`<id><digits>` = same logical id).
  17. Parser tolerance for `cutaway`/`cutout-` slipping into `panels`.
  18. Panels mandatory on every piece (even flat single-region).
  19. Derived pivots: rigidly attached pieces inherit rotation through edges.
  20. Dual-presence pattern: typed landing region as both panel and mark.
  21. Fuzzy substring matching with prefix-stripping + shortest-match tiebreaker.
- **Why:** stress-tested through 9 pieces of end-to-end authoring; 100% edge resolution.
- **Type:** Co-authored.
- **Reopen?** closed in current form. New conventions land as new rows.

### #8 — Tool acquisition is a standing proactive ask (CHARTER amendment A1)

- **Date:** 2026-05-05
- **Decision:** Charter §9 "Marketplace" → "Tool acquisition" — standing directive that Claude proactively raises tool/integration/MCP/plugin/skill/sandbox-capability gaps with explicit cost/benefit (setup time, per-use compute, disk, ongoing cost, expected use frequency); browses marketplace + MCP registry before defaulting to direct workspace install. Captured as CHARTER amendment A1.
- **Why:** the gap surfaced concretely on PR #15 review. Right response was to ask for the tool, not work around it. Earlier-rather-than-later beats accumulating workarounds.
- **Type:** Co-authored (substantive charter amendment per §12).
- **Reopen?** closed. Procedural directive — specific tool installs still get their own DECISIONS rows.

### #9 — Fold-step prefix and same-piece closure attach (panels-first convention extensions)

- **Date:** 2026-05-05 (bob-batch evening)
- **Decision:** Two convention extensions surfaced through 095 authoring on the bob casing strip.

  **A — Fold-step ordinal prefix.** Optional leading `<step>-` (positive integer + hyphen) before `fold-`. Full form: `[<step>-]fold-<a>-<b>[-<deg>]`. Same step number across multiple folds = "fire simultaneously" during a phased fold sequence. Captures fold ORDER — information the parser cannot derive from geometry alone. Step is independent of polarity (M/V).

  Example from 095: step 1 (central valley pane3-pane4) → step 2 (pane2-pane3 mountain + pane4-pane5 valley, paired) → step 3 (pane1-pane2 mountain + pane5-pane6 valley, closing flaps).

  Affinity Designer prefixes ids that start with a digit with `_` for SVG-spec compliance (`_3-fold-pane1-pane2`); author's literal preserved in `serif:id`. Parser strips leading `_` to recover authored form.

  **B — Same-piece closure attach via panel-id.** New form `attach-<panel-id>` (and `back-attach-<panel-id>`) where suffix matches a panel id of THIS piece. Distinguished from cross-piece `attach-<letter><piece>` by panel-set lookup: if suffix is a known panel of this piece, it's same-piece. Closes the convention gap between cross-piece structural attaches and same-piece registration marks.

  Example from 095: `back-attach-pane1`, `back-attach-pane2`, `back-attach-pane3` — bob-casing strip's closing flaps glue back onto pane1/2/3 from the back side. Parallels `landing-<panel-id>` (convention #9).

- **Why:** Both extensions emerged organically from authoring 095. Extension A captures fold order, real structural property. Extension B fills convention gap. Grammar parallels are clean: `<step>-fold-<...>` mirrors `fold-<...>-<deg>` (prefix vs. suffix); `attach-<panel-id>` parallels `landing-<panel-id>`.
- **Type:** Co-authored.
- **Downstream:** `build_assembly_graph.py` patched (recognizes both forms; new `closure_attaches` section in connection-graph); `preview.html` parser changes queued via `CODE_PROMPT_preview-html-fold-step-and-closure-attach.md`; LAYER-CONVENTIONS.md extended (folds-section + attach-points-section + Parser-rules-section).
- **Reopen?** closed. Stress-tested on 095; audit picks up 5 folds + 3 closure attaches cleanly.

### #10 — Sidecar `connections.inferred[]` for learned-but-not-printed cross-piece connections

- **Date:** 2026-05-06
- **Decision:** Per-piece JSON sidecars (`work/pieces/NNN/NNN.json` — same file the existing `function` block lives in) gain an optional `connections.inferred[]` array. Each entry captures a cross-piece (or same-piece) relationship that the printed piece doesn't explicitly mark — knowledge from the book's instructions text, from physical assembly, or from any source other than the SVG itself. Entry shape mirrors the existing connection-graph edge shape with one new mandatory field:

  ```json
  {
    "connections": {
      "inferred": [
        {
          "kind": "attach",                                      // attach | landing | hole | pivot | attach-same-piece | landing-same-piece
          "side": "front",                                       // optional; "front" | "back"; default "front"
          "letter": "x",                                         // for attach/hole; null otherwise
          "tab": null,                                           // for landing; null otherwise
          "name": null,                                          // for pivot; null otherwise
          "panel": null,                                         // for *-same-piece; null otherwise
          "partner": "099",                                      // partner piece id; null for pivot/same-piece
          "source": "instructions §II.B p. 14",                  // MANDATORY — where the knowledge came from
          "note": "Pin from 097 actually slots through 099's main panel near landing-c."  // optional free-form
        }
      ]
    }
  }
  ```

  `build_assembly_graph.py` reads the sidecar's inferred list during piece extraction and merges it into the cross-piece graph alongside SVG-derived edges. Every edge in the output graph gains a `provenance` field — `"authored"` (from SVG) or `"inferred"` (from sidecar). Inferred edges carry `source` + (optional) `note` through to the rendered report. The Markdown report grows a "Inferred connections" section listing each piece's inferred edges with their source.

  Conflict policy: if an inferred entry duplicates an authored edge (same `{from, to, kind, letter|tab|name|panel}`), the authored entry wins and the report flags the duplicate with a warning. The script does not block on conflicts — duplicates can mean Alan authored the connection on the SVG after the inferred entry was captured, in which case the inferred entry should be removed manually.

  Schema is documented in `LAYER-CONVENTIONS.md` "Per-piece JSON sidecar" section.

- **Why:** The connection graph only sees what's authored as SVG markup. Knowledge from the instructions text and from physically assembling pieces has no structured home — it lands in chat, cheat sheets (`claude-work/to-alan/cheats/066-068.md`), or Alan's head. With 16 panels-first pieces in the graph and the gear-train assembly ahead, that gap will widen. Inferred connections in the sidecar gives the connection graph one substrate for both printed and learned truth, preserves the faithful-trace direction (SVG = artifact-truth), and lets the audit flag "needs human re-confirmation if the SVG ever changes" via provenance.
- **Type:** Co-authored (sidecar shape sits at the seam Alan and Claude both touch — Alan reads, Claude writes).
- **Downstream:** `CODE_PROMPT_build-assembly-graph-inferred.md` (audit script extension); `LAYER-CONVENTIONS.md` updated with new "Per-piece JSON sidecar" section.
- **Reopen?** closed in v1. Reopens if a real piece surfaces a connection shape the schema doesn't cover.

### #11 — Sidecar `assembled.folds` for per-fold assembled-state angles

- **Date:** 2026-05-06
- **Decision:** Per-piece JSON sidecars gain an optional `assembled.folds` block: a map of fold-id → angle in degrees, capturing the assembled-state pose for each fold. The preview reads this block on piece load and uses it as the per-fold slider's default. The preview gains a "Save assembled pose" affordance that emits the current fold-slider state as a JSON snippet (copy-to-clipboard + download) for Alan to merge into the sidecar by hand — browsers can't write to disk from `preview.html`.

  ```json
  {
    "assembled": {
      "folds": {
        "fold-pane1-pane2": 90,
        "fold-pane2-pane3": 90,
        "fold-tabaa-pane7": 180,
        "_3-fold-pane1-pane2": 180,
        "fold-insidetabs": 0
      },
      "captured": "2026-05-06T15:30:00",
      "note": "Final assembled state per book figure 14."
    }
  }
  ```

  Rules:

  1. **Keys are the literal SVG fold ids** — including any Affinity `_<digit>` underscore prefix (`_3-fold-pane1-pane2`). The SVG is the unambiguous reference; the parser's `_`-strip normalization is not applied here. Why: the literal id is what `parsePanelsFirstFolds` exposes on each fold object's `id` field, and what the slider's `dataset` attribute carries. Matching against literal ids avoids round-tripping through normalized form.
  2. **Values are signed integers or floats** in degrees. Sign convention matches the existing default-angle suffix on fold-ids: **positive = layer's natural direction** (valley = dashed-in-print direction; mountain = plus-sign-in-print direction). To flip polarity for a specific fold, move the path to the other layer in the SVG — the sidecar value stays positive.
  3. **Precedence** (preview slider default, highest first): `assembled.folds[id]` > fold-id `-<deg>` suffix > 0. The default-angle suffix on the fold id stays valid as a fallback; the sidecar overrides it.
  4. **Optional siblings.** `captured` (ISO 8601 timestamp; informational) and `note` (free-form prose).

  "Save assembled pose" UX: button in the side panel, visible only when at least one panels-first fold slider is present. Clicking shows a modal/textarea with the current `assembled.folds` block (only folds whose slider value has moved off the precedence-determined default since load are emitted; unchanged folds are omitted to keep the diff small). Two buttons: "Copy to clipboard" and "Download `<piece>.assembled.json`." Alan merges into `work/pieces/NNN/NNN.json` by hand — same workflow as merging anything Claude generates into the sidecar.

  Schema is documented in `LAYER-CONVENTIONS.md` "Per-piece JSON sidecar" section.

- **Why:** Per-fold validation today happens by scrubbing sliders in the preview, but the result evaporates on reload. Sidecar `assembled.folds` makes it durable and reproducible across machines, sessions, and commits. The preview becomes a tool Alan uses to *discover* the angle and *capture* it; the sidecar carries it forward.
- **Type:** Co-authored.
- **Downstream:** `CODE_PROMPT_preview-html-assembled-pose.md` (preview.html load + save affordance) — **shipped 2026-05-06 via PR #19**; `LAYER-CONVENTIONS.md` updated with new "Per-piece JSON sidecar" section.
- **Out of scope (deliberately):** Inter-piece assembled transforms — where each piece sits in 3D space relative to its partners once folded — are M4 assembly-transform work and live separately. Likely shape: SE(3) transforms attached to connection-graph edges, or a top-level `assembled.json`. Per-fold pose (one piece's internal fold geometry) is the v1 deliverable here. The two compose later: each piece's `assembled.folds` settles its internal geometry; a per-edge transform settles its placement in the world.
- **Follow-up parked from v1 ship:** scene mode opted out of the per-piece `assembled.folds` map for v1 — `currentAssembledFolds` is gated on single-piece mode. Per-piece assembled poses applied independently across a scene needs `currentAssembledFolds` to grow into a per-piece map keyed by `_sceneId`. Pull when the scene-mode use case actually wants it.
- **Reopen?** closed in v1.

---

*Last updated: 2026-05-06 (post-PR-19 review) — Decision #11 downstream pointer flipped to shipped (PR #19 wired `assembled.folds` load + save through `preview.html`); v1 follow-up parked for per-piece assembled poses across scene mode (only relevant when the scene-mode use case actually surfaces). #10 had already shipped via PR #18 the same evening.*

*Earlier 2026-05-06 — Decisions #10 and #11 closed: per-piece JSON sidecar gains `connections.inferred[]` (learned cross-piece connections with provenance) and `assembled.folds` (per-fold assembled-state angles, with preview load + save affordances). Two CODE_PROMPTs queued for execution. LAYER-CONVENTIONS extended.*

*Earlier 2026-05-05 (bob-batch evening) — Decision #9 closed: fold-step prefix + same-piece closure attach via panel-id. Both extensions surfaced through 095 authoring; build_assembly_graph patched + LAYER-CONVENTIONS extended; preview.html parser changes queued.*

*Earlier 2026-05-05 (bob-batch evening) — Decision #9 closed: fold-step prefix + same-piece closure attach via panel-id.*

*Earlier 2026-05-05 — Decision #8 closed (CHARTER amendment A1 tool-acquisition directive); #7 closed (21 panels-first convention elements ratified); #6 closed (panels-first + authored-vs-derived); #5 closed (cut-trim deviation captured).*

*Earlier 2026-05-04 (afternoon) — initial authoring at charter sign-off. #1-#4 captured.*
