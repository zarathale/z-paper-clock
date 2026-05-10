---
status: ready-for-code
started: 2026-05-10
owner: Zarathale (Alan)
target: preview-html-snap
---

# CODE_PROMPT — Snap-to-connection-point in Cluster mode

## What You Are Doing and Why

Manual slider dragging is not a viable way to assemble pieces that have authored
connection constraints. The connection graph already encodes exactly which point on piece A
meets which point on piece B — tab-b on 065 meets landing-b65 on 066, seven times over.
The viewer should use that knowledge to place pieces, not make the user estimate mm offsets.

This PR adds **smart snap** to Cluster mode:

1. User enters Snap mode. Clicks any connection sphere on any piece.
2. The system looks up that point's known partners in the connection graph and immediately
   highlights those partner spheres on other pieces.
3. A sidebar panel lists the known pairs with a [Snap] button per pair.
4. Clicking [Snap] translates the tab piece so its connection point meets the landing point
   exactly. One click per constraint pair.
5. For pieces with multiple connections (e.g., 065↔066 has 7 pairs), "Snap all" computes
   the median translation across all pairs — more robust than a single-pair snap.
6. After snapping, a green line between the two points confirms the connection.

The system is active, not passive: it offers the pairings, the user confirms or skips.
The user never has to identify matching pairs manually — the graph already knows.

## Prerequisites — confirm before starting

- PR A, PR B, PR C all merged to `main`.
- `claude-work/state/connection-graph.json` exists with valid `edges` array. Each edge has:
  `{ from, to, kind ("attach"|"landing"), tab, partner_match, valid, prov }`.
- Connection point spheres are rendered in Cluster mode (PR C Task 5). They must carry
  metadata identifying `{ pieceId, pointId, pointType ("attach"|"landing"|"pivot") }` on
  their userData so raycasting can identify what was clicked. Verify this exists; if not,
  add userData assignment to the sphere-creation code as a prerequisite step.
- `preview.html` has an active `connectionGraphData` (or equivalent) module-level variable
  holding the parsed `connection-graph.json`. Grep for where the graph is fetched and
  cached; use that variable.

## Read These Files First

1. `preview.html` — Cluster mode section: how `pieceGroups` are structured, how the
   existing raycasting works for piece selection (Task 2 in PR C), and how connection
   point spheres are built and added to `pieceGroup` (PR C Task 5).
2. `claude-work/state/connection-graph.json` — `edges` array shape and `pivot_clusters`.
3. `claude-work/DECISIONS.md` #13 — cluster-local frame semantics; snap operates in
   cluster-local space (world space while all pieces share the same scene).

## Target File Structure Changes

```
preview.html    ← all changes; Cluster mode snap additions only
```

No new files. No sidecar changes (save is handled by `CODE_PROMPT_preview-bridge-save.md`).

## Numbered Tasks

### Task 1 — Ensure connection sphere userData is populated

In the Cluster mode sphere-creation code (PR C Task 5), confirm each sphere mesh has:

```js
sphere.userData = {
  type:      'connection-point',
  pieceId:   pieceId,          // e.g. "065"
  pointId:   point.id,         // e.g. "tab-b" or "landing-b65" or "pivot-anchor"
  pointType: point.kind,       // "attach", "landing", or "pivot"
};
```

If this isn't present, add it now. Everything else depends on it.

### Task 2 — Snap mode toggle in Cluster toolbar

Add a "Snap" toggle button to the Cluster mode toolbar (next to the existing "Measure"
toggle from PR C). Only one of Snap / Measure / Select can be active at a time.

```
[ Select ]  [ Measure ]  [ Snap ]
```

`currentClusterTool = 'select' | 'measure' | 'snap'`

When Snap mode activates:
- Cursor changes to crosshair on the canvas.
- A "Snap" sidebar panel appears (see Task 4).
- Connection spheres brighten / increase radius slightly to indicate they're clickable.

When Snap mode deactivates: clear all snap highlights and pending state.

### Task 3 — First click: select a connection point + auto-detect partners

In the canvas mousedown handler, when `currentClusterTool === 'snap'`:

1. Raycast against all connection sphere meshes across all `pieceGroups`.
2. On hit: record `snapFrom = { pieceId, pointId, pointType, worldPos: sphere.getWorldPosition(new THREE.Vector3()) }`.
3. **Look up partners in the connection graph.** An edge `{ from: A, to: B }` means piece
   A's attach point connects to piece B's landing. Build the partner list:
   ```js
   function findPartners(pieceId, pointId, edges) {
     // pointId on piece A may appear as:
     //   - edge.from === pieceId AND edge.tab === letter extracted from pointId
     //   - edge.to   === pieceId AND edge.partner_match matches pointId
     // Return array of { partnerPieceId, partnerPointId, edgeKind }
   }
   ```
   Match heuristic: strip "tab-" / "landing-" / "mark-" prefixes and compare the
   bare letter(s). E.g., "tab-b" on 065 matches edge `{ from: "065", tab: "b" }`;
   the partner is `{ to: "066", partner_match: "tabb" }` → resolve to point "tab-b"
   on 066 (or the landing mark whose id contains "b65"/"tabb"). Use the sphere userData
   pointId list for each piece to find the closest match.
4. **Highlight partner spheres.** For each partner found, change that sphere's material
   to a bright pulsing gold colour. All non-partner spheres dim.
5. If no partners found: banner "No known partners for this point — click another point
   to snap manually."

### Task 4 — Snap sidebar panel

Show a panel below the toolbar when a snap-from point is selected:

```
Snap: 065 / tab-b
────────────────────────────────
Known connections:
  → 066 / landing-b65   [Snap]
────────────────────────────────
[Snap all 7 pairs → 066]
[Clear]
```

- One row per known partner. [Snap] button per row.
- "Snap all N pairs" button when multiple known pairs exist between the same two pieces
  (e.g., all 7 between 065 and 066).
- [Clear] resets snap state, dims all spheres.

If user clicks a second sphere (not a known partner) without using a sidebar button:
show "Custom snap: [piece] / [pointId] → [piece] / [pointId]  [Snap]" at the bottom.
Custom snap applies regardless of graph knowledge.

### Task 5 — Snap execution (single pair)

When the user clicks [Snap] for a specific pair:

```js
function snapPair(fromPieceId, fromPointId, toPieceId, toPointId) {
  // Convention: the TAB piece moves to the LANDING piece (landing is the anchor).
  // Determine which is which from the edge kind.
  const tabPieceId    = (edgeKind === 'attach') ? fromPieceId : toPieceId;
  const landingPieceId = (edgeKind === 'attach') ? toPieceId  : fromPieceId;

  const tabSphere     = findSphere(tabPieceId, fromPointId or toPointId);
  const landingSphere = findSphere(landingPieceId, ...);

  const tabWorld     = tabSphere.getWorldPosition(new THREE.Vector3());
  const landingWorld = landingSphere.getWorldPosition(new THREE.Vector3());

  const delta = landingWorld.clone().sub(tabWorld);  // move tab to landing
  pieceGroups[tabPieceId].position.add(delta);
}
```

After snap:
- Replace the gold highlight on the two spheres with green (snapped).
- Draw a thin green line between the two world positions (persists until cluster reloads).
- Log to sidebar: "✓ Snapped: 065:tab-b → 066:landing-b65 (Δ = N.N mm)"
- Record `snappedPairs.push({ tabPieceId, tabPointId, landingPieceId, landingPointId })`.

### Task 6 — Snap all pairs (median translation)

"Snap all N pairs → 066" button:

```js
function snapAllPairs(tabPieceId, landingPieceId, pairs) {
  // pairs: [{ tabPointId, landingPointId }, ...]
  const deltas = pairs.map(({ tabPointId, landingPointId }) => {
    const tabWorld     = findSphere(tabPieceId, tabPointId).getWorldPosition(...);
    const landingWorld = findSphere(landingPieceId, landingPointId).getWorldPosition(...);
    return landingWorld.clone().sub(tabWorld);
  });

  // Median per component — robust against one outlier pair
  const medX = median(deltas.map(d => d.x));
  const medY = median(deltas.map(d => d.y));
  const medZ = median(deltas.map(d => d.z));

  pieceGroups[tabPieceId].position.add(new THREE.Vector3(medX, medY, medZ));

  // After applying, report residuals: how far off is each pair?
  // Show in sidebar: "Max residual: 0.3 mm (tab-e / landing-e65)"
}
```

Report the max residual after snapping all pairs — that number tells Alan how well the
SVG geometry is self-consistent. Sub-1mm is excellent; larger residuals flag authoring
discrepancies worth investigating.

### Task 7 — Rigid group lock (post-snap)

After one or more snaps between pieces A and B, a "Lock together" button appears:

```
✓ 065 ↔ 066 snapped (7 pairs, max residual 0.2mm)
[Lock together]
```

Clicking "Lock together":
- Makes the tab piece's `pieceGroup` a child of the landing piece's `pieceGroup` in the
  THREE.js scene graph: `pieceGroups[landingPieceId].add(pieceGroups[tabPieceId])`.
  Adjust `tabPieceGroup.position` to be relative to parent (subtract parent world pos).
- From this point, moving the landing piece moves the tab piece with it.
- In the sidebar, show the locked group: "Locked group: [066, 065]"
- Locked pieces can be individually unlocked (they revert to world children).

**Simplification note:** if the scene graph re-parenting proves complex to implement
cleanly alongside the existing transform/TC infrastructure, an acceptable v1 fallback is
a "move together" list: maintain `rigidGroups: [[pieceA, pieceB], ...]` and in the TC
`change` event handler, for each group containing the moved piece, apply the same delta
to all other group members. Either approach is fine; prefer whichever is cleaner in the
existing codebase.

## Verification Checklist

1. Load cluster `anchor`. Switch to Snap mode. Connection spheres visible and brighter.
2. Click `pivot-anchor` sphere on 067. Gold spheres appear on 069 (the partners). Sidebar
   shows "Snap: 067 / pivot-anchor → 069 / pivot-anchor  [Snap]".
3. Click [Snap]. 069 translates so its pivot-anchor meets 067's. Green line appears.
   Sidebar shows "✓ Snapped … Δ = N.N mm".
4. Click `tab-b` sphere on 065. Sidebar shows "Known connections: → 066 / landing-b65
   [Snap]" + "Snap all 7 pairs → 066".
5. Click "Snap all 7 pairs". 065 translates. Sidebar shows max residual. All 7 pairs
   show green lines.
6. Click "Lock together" for 065+066. Move 066 via TC translate. 065 moves with it.
7. Custom snap: click `tab-j` on 066, then `landing-j068` on 068 (or nearest sphere).
   "Custom snap" row appears in sidebar. Click [Snap]. 068 moves.
8. After snapping all pieces: click Save selected piece for each → bridge writes sidecars.
   Reload cluster → pieces load at snapped positions (from sidecars).
9. Snap mode off → Select mode normal. TC and selection unaffected.
10. No regressions in Bench mode.

## What NOT to Change

- Bench mode (PR A + PR B) — snap is Cluster mode only.
- Sidecar shape — snap doesn't touch sidecars; save is a separate PR.
- Rotation — snap is translation-only in v1. If pieces need rotation alignment, the
  user uses the rotation sliders after snapping. Rotation-matching snap (aligning tab
  face normals) is deferred.
- Auto-snap without user confirmation — always require a [Snap] button click. Never
  move a piece without explicit user action.
- The connection graph on disk — snap reads it, never writes it.

## Manual Tests (Alan runs after merge)

| Step | Expected |
|---|---|
| Load cluster `anchor`, enter Snap mode | All 5 pieces load; spheres visible at connection points |
| Click pivot-anchor on 067 | Partner on 069 highlights gold |
| [Snap] | 069 jumps to share pivot-anchor with 067. Green line. |
| Click tab-b on 065 | 066's landing-b65 highlights; "Snap all 7" offered |
| [Snap all 7] | 065 translates into 066. Max residual < 1mm (expect ~0mm if geometry is clean) |
| [Lock together] 065+066 | Moving 066 via gizmo carries 065 |
| Save each piece, reload cluster | All pieces at snapped positions |
