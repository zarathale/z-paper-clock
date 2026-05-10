---
status: ready-for-code
started: 2026-05-10
owner: Zarathale (Alan)
target: preview-html-snap
revised: 2026-05-10 (Cowork session guided-assembly-design — field-name bugs fixed,
         verification checklist corrected, bidirectional lookup added, progress panel added,
         snapped_connections sidecar field added, large-residual banner added)
---

# CODE_PROMPT — Snap-to-connection-point in Cluster mode

## What You Are Doing and Why

Manual slider dragging is not a viable way to assemble pieces that have authored
connection constraints. The connection graph already encodes exactly which point on piece A
meets which point on piece B — tab-b on 065 meets landing-b65 on 066, seven times over.
The viewer should use that knowledge to place pieces, not make the user estimate mm offsets.

This PR adds **smart snap** to Cluster mode:

1. User enters Snap mode. Clicks any connection sphere on any piece.
2. The system looks up that point's known partners in the connection graph and highlights
   those partner spheres on other pieces in gold.
3. A persistent sidebar panel shows all connections for the loaded cluster (snapped /
   unsnapped / locked). The clicked point's partners appear as actionable rows.
4. A [Snap] button per partner row. Clicking it translates the tab piece so its connection
   point meets the landing point exactly.
5. For pieces with multiple connections (e.g., 065↔066 has 7 pairs), "Snap all" computes
   the median translation across all pairs — more robust than a single-pair snap.
6. After snapping, a green line between the two points confirms the connection.
7. If the max residual after "Snap all" exceeds 1.5mm, a yellow warning banner fires —
   this usually means the piece needs rotation adjustment before its connections will seat.

The system is active, not passive: it offers the pairings, the user confirms or skips.
The user never has to identify matching pairs manually — the graph already knows.

## Prerequisites — confirm before starting

- PR A, PR B, PR C all merged to `main`.
- `claude-work/state/connection-graph.json` exists with valid `edges` array.

  **Read the actual edge schema before writing any matching code.** The real fields are:

  ```json
  {
    "from":        "065",
    "to":          "066",
    "kind":        "attach",
    "side":        "front",
    "tab":         null,
    "letter":      "b",
    "raw_id":      "attach-b66",
    "source_layer":"attach-points",
    "provenance":  "authored",
    "valid":       true,
    "matched_panel":"tabb",
    "matched_via": "panel-tab"
  }
  ```

  Critical asymmetry: **for `kind: "attach"` edges, the letter is in `letter` and `tab`
  is null. For `kind: "landing"` edges, the letter is in `tab` and `letter` is null.**
  The wrong field is null for the wrong kind — this is intentional in the build script.
  Any matching code that reads `edge.tab` without checking `edge.kind` will silently
  miss all attach-kind edges.

  The field previously described in this prompt as `partner_match` is actually
  `matched_panel`. The field previously described as `prov` is actually `provenance`.

  The `to` field is mostly zero-padded (`"066"`) but may be bare (`"66"`) on some older
  invalid edges. Always normalize: `String(id).padStart(3, '0')` when matching against
  `pieceGroups` keys.

- Connection point spheres are rendered in Cluster mode (PR C Task 5). They must carry
  metadata identifying `{ pieceId, pointId, pointType }` on their `userData` so raycasting
  can identify what was clicked. Verify this exists; if not, add it as a prerequisite step
  (see Task 1).
- `preview.html` has an active `connectionGraphData` (or equivalent) module-level variable
  holding the parsed `connection-graph.json`. Grep for where the graph is fetched and
  cached; use that variable. Do not fetch it again.

## Read These Files First

1. `preview.html` — Cluster mode section: how `pieceGroups` are structured, how the
   existing raycasting works for piece selection (Task 2 in PR C), and how connection
   point spheres are built and added to `pieceGroup` (PR C Task 5).
2. `claude-work/state/connection-graph.json` — read the actual `edges` array. Note the
   `kind`/`tab`/`letter` asymmetry described above. Note `pivot_clusters` shape.
3. `claude-work/DECISIONS.md` #13 — cluster-local frame semantics; snap operates in
   world space while all pieces share the same scene.

## Target File Structure Changes

```
preview.html    ← all changes; Cluster mode snap additions only
```

No new files. Sidecar save is handled by `CODE_PROMPT_preview-bridge-save.md` — this PR
adds `snapped_connections` to the save payload (Task 8) but does not change the save
mechanism itself.

## Numbered Tasks

### Task 1 — Ensure connection sphere userData is populated

In the Cluster mode sphere-creation code (PR C Task 5), confirm each sphere mesh has:

```js
sphere.userData = {
  type:      'connection-point',
  pieceId:   pieceId,    // e.g. "065"
  pointId:   point.id,   // e.g. "attach-b66" or "landing-b65" — the raw_id from the edge
  pointKind: point.kind, // "attach" or "landing"
};
```

Use `raw_id` as `pointId` — it's the stable, unique identifier already in the graph.
Do not use synthesized names like "tab-b" — they introduce another translation layer.
Everything else depends on this.

### Task 2 — Snap mode toggle in Cluster toolbar

Add a "Snap" toggle button to the Cluster mode toolbar (next to the existing "Measure"
toggle from PR C). Only one of Snap / Measure / Select can be active at a time.

```
[ Select ]  [ Measure ]  [ Snap ]
```

`currentClusterTool = 'select' | 'measure' | 'snap'`

When Snap mode activates:
- Cursor changes to crosshair on the canvas.
- The snap sidebar panel appears (see Task 4).
- Connection spheres brighten / increase radius slightly to indicate they're clickable.

When Snap mode deactivates: clear all snap highlights and pending state.

### Task 3 — First click: select a connection point + auto-detect partners

In the canvas mousedown handler, when `currentClusterTool === 'snap'`:

1. Raycast against all connection sphere meshes across all `pieceGroups`.
2. On hit: record `snapFrom = { pieceId, pointId, pointKind, worldPos }`.
3. **Look up partners in the connection graph.** Walk `edges` in both directions:

   ```js
   // Helper: get the letter from an edge regardless of kind
   function edgeLetter(edge) {
     return edge.kind === 'attach' ? edge.letter : edge.tab;
   }

   // Helper: normalize piece ID to 3-digit zero-padded
   function normId(id) {
     return String(id).padStart(3, '0');
   }

   function findPartners(pieceId, rawPointId, edges) {
     // rawPointId is the sphere's userData.pointId = edge.raw_id, e.g. "attach-b66"
     // Extract the letter from the raw_id: strip "attach-" or "landing-" prefix,
     // then strip the trailing piece number digits.
     // e.g. "attach-b66" → letter "b"; "landing-b65" → letter "b"
     const letterMatch = rawPointId.match(/^(?:attach|landing)-([a-z]+)/);
     if (!letterMatch) return [];
     const clickedLetter = letterMatch[1].replace(/\d+$/, ''); // strip trailing digits

     const partners = [];
     const seen = new Set(); // dedup key: `${normId(partnerPiece)}:${letter}`

     for (const edge of edges) {
       if (!edge.valid) continue;
       const letter = edgeLetter(edge);
       if (!letter) continue;

       let partnerPieceId = null;
       let tabPieceId = null;
       let landingPieceId = null;

       // Case A: clicked piece is the "from" side
       if (normId(edge.from) === normId(pieceId) && letter === clickedLetter) {
         partnerPieceId = normId(edge.to);
         tabPieceId     = edge.kind === 'attach' ? normId(edge.from) : normId(edge.to);
         landingPieceId = edge.kind === 'attach' ? normId(edge.to)   : normId(edge.from);
       }
       // Case B: clicked piece is the "to" side
       else if (normId(edge.to) === normId(pieceId) && letter === clickedLetter) {
         partnerPieceId = normId(edge.from);
         tabPieceId     = edge.kind === 'attach' ? normId(edge.from) : normId(edge.to);
         landingPieceId = edge.kind === 'attach' ? normId(edge.to)   : normId(edge.from);
       }

       if (!partnerPieceId) continue;

       const dedupKey = `${partnerPieceId}:${letter}`;
       if (seen.has(dedupKey)) continue; // graph stores both directions; dedup here
       seen.add(dedupKey);

       // Find the partner sphere's raw_id: it's the edge on the partner side
       // For attach: partner's landing sphere has raw_id like "landing-b65"
       // For landing: partner's attach sphere has raw_id like "attach-b66"
       const partnerRawId = edge.kind === 'attach'
         ? `landing-${letter}${normId(pieceId)}`   // landing marker on partner piece
         : edge.raw_id;                             // attach point on partner piece

       partners.push({
         partnerPieceId,
         partnerRawId,
         tabPieceId,
         landingPieceId,
         letter,
         matchedVia: edge.matched_via,  // e.g. "panel-tab" — show in sidebar
         edge,
       });
     }
     return partners;
   }
   ```

   **Note on `partnerRawId`:** the partner sphere's `userData.pointId` was set to the
   edge's `raw_id` in Task 1. For the partner, look up the sphere by iterating
   `pieceGroups[partnerPieceId].children` and matching `userData.pointId`. If no exact
   match, fall back to any sphere on that piece with the same letter in its pointId.

4. **Highlight partner spheres.** For each partner found, change that sphere's material
   to a bright pulsing gold colour. All non-partner connection spheres dim (not hidden).
5. If no partners found: banner "No known partners for this point — click another point
   to snap manually."

### Task 4 — Snap sidebar panel (persistent + interactive)

The sidebar has two zones:

**Zone A — Connections progress (always visible in Snap mode):**

```
Connections — anchor cluster
  065 ↔ 066   7 pairs   ○ unsnapped
  066 ↔ 068   1 pair    ○ unsnapped
  067 ↔ 069   4 pairs   ○ unsnapped
  068 ↔ 069   3 pairs   ○ unsnapped
```

Build this list on Snap mode activation by reading `connectionGraphData.graph.edges`,
filtering `valid === true`, grouping by unique piece-pair `{min(from,to), max(from,to)}`,
and deduplicating (the graph stores both directions). As pairs get snapped, dots
change: `○` unsnapped → `●` snapped → `🔒` locked. Clicking a row highlights those two
pieces in the scene.

**Zone B — Active snap interaction (appears when a point is clicked):**

```
Snap: 065 / attach-b66
────────────────────────────
Known connections:
  → 066 / landing-b65  (panel-tab)  [Snap]
────────────────────────────
[Snap all 7 pairs → 066]
[Clear]
```

- One row per partner. Letter in parentheses shows `matched_via` — gives Code confidence
  in match quality (`panel-tab` = strong; `panel-substring` = weaker).
- "Snap all N pairs → [piece]" button when multiple pairs exist between the same two pieces.
- [Clear] resets Zone B, dims all spheres, Zone A remains visible.

If the user clicks a second sphere that is not a known partner, show at bottom of Zone B:

```
Custom snap: 066 / attach-j68 → 068 / landing-j066  [Snap]
```

Custom snap moves the tab piece to align the two clicked points, regardless of graph
knowledge.

### Task 5 — Snap execution (single pair)

```js
function snapPair(partner) {
  // partner: { tabPieceId, landingPieceId, partnerRawId, edge }
  // Convention: the TAB piece moves to the LANDING piece (landing is the anchor).
  // tabPieceId and landingPieceId are already resolved in findPartners.

  const tabSphere     = findSphereByRawId(partner.tabPieceId,     /* attach raw_id */);
  const landingSphere = findSphereByRawId(partner.landingPieceId, partner.partnerRawId);

  if (!tabSphere || !landingSphere) {
    showBanner('warn', 'Could not locate connection spheres — check sphere userData.');
    return;
  }

  const tabWorld     = tabSphere.getWorldPosition(new THREE.Vector3());
  const landingWorld = landingSphere.getWorldPosition(new THREE.Vector3());
  const delta        = landingWorld.clone().sub(tabWorld);

  pieceGroups[partner.tabPieceId].position.add(delta);

  // Visual feedback
  setSphereColor(tabSphere,     0x00cc66); // green — snapped
  setSphereColor(landingSphere, 0x00cc66);
  drawLine(tabWorld, landingWorld, 0x00cc66); // thin green line, persists until reload

  const distMm = delta.length(); // already in mm if scene units are mm
  appendToSnapLog(`✓ Snapped: ${partner.tabPieceId}:${partner.edge.raw_id} → `
    + `${partner.landingPieceId}:${partner.partnerRawId} (Δ = ${distMm.toFixed(1)} mm)`);

  snappedPairs.push({
    tabPieceId:     partner.tabPieceId,
    tabRawId:       partner.edge.raw_id,
    landingPieceId: partner.landingPieceId,
    landingRawId:   partner.partnerRawId,
    letter:         partner.letter,
  });

  updateProgressPanel(); // refresh Zone A dot for this piece-pair
}

function findSphereByRawId(pieceId, rawId) {
  const group = pieceGroups[pieceId];
  if (!group) return null;
  // Walk all descendants; spheres may be nested
  let found = null;
  group.traverse(obj => {
    if (obj.userData?.type === 'connection-point' && obj.userData.pointId === rawId) {
      found = obj;
    }
  });
  return found;
}
```

### Task 6 — Snap all pairs (median translation)

```js
function snapAllPairs(tabPieceId, landingPieceId, partners) {
  // partners: array from findPartners filtered to this piece-pair
  const deltas = [];

  for (const p of partners) {
    const tabSphere     = findSphereByRawId(tabPieceId, p.edge.raw_id);
    const landingSphere = findSphereByRawId(landingPieceId, p.partnerRawId);
    if (!tabSphere || !landingSphere) continue;
    const tw = tabSphere.getWorldPosition(new THREE.Vector3());
    const lw = landingSphere.getWorldPosition(new THREE.Vector3());
    deltas.push(lw.clone().sub(tw));
  }

  if (!deltas.length) return;

  // Median per component — robust against one outlier pair
  const med = v => [...v].sort((a, b) => a - b)[Math.floor(v.length / 2)];
  const medX = med(deltas.map(d => d.x));
  const medY = med(deltas.map(d => d.y));
  const medZ = med(deltas.map(d => d.z));

  pieceGroups[tabPieceId].position.add(new THREE.Vector3(medX, medY, medZ));

  // Compute residuals after applying the median translation
  const residuals = partners.map(p => {
    const tabSphere     = findSphereByRawId(tabPieceId, p.edge.raw_id);
    const landingSphere = findSphereByRawId(landingPieceId, p.partnerRawId);
    if (!tabSphere || !landingSphere) return { letter: p.letter, mm: null };
    const tw = tabSphere.getWorldPosition(new THREE.Vector3());
    const lw = landingSphere.getWorldPosition(new THREE.Vector3());
    return { letter: p.letter, mm: tw.distanceTo(lw) };
  }).filter(r => r.mm !== null);

  const maxResidual = Math.max(...residuals.map(r => r.mm));
  const worstPair   = residuals.find(r => r.mm === maxResidual);

  appendToSnapLog(
    `Snapped all ${partners.length} pairs: ${tabPieceId} → ${landingPieceId}. `
    + `Max residual: ${maxResidual.toFixed(1)} mm (${worstPair.letter})`
  );

  // Large-residual warning — usually means rotation adjustment needed before locking
  if (maxResidual > 1.5) {
    showBanner('warn',
      `Large residual after snap: ${maxResidual.toFixed(1)} mm on letter-${worstPair.letter}. `
      + `This often means the piece needs rotation adjustment before its connections will seat cleanly. `
      + `Use the rotation sliders, then re-snap.`
    );
  }

  // Mark each pair as snapped individually
  for (const p of partners) {
    snappedPairs.push({
      tabPieceId,
      tabRawId:       p.edge.raw_id,
      landingPieceId,
      landingRawId:   p.partnerRawId,
      letter:         p.letter,
      residual_mm:    residuals.find(r => r.letter === p.letter)?.mm ?? null,
    });
  }

  updateProgressPanel();
}
```

### Task 7 — Rigid group lock (post-snap)

After one or more snaps between pieces A and B, a "Lock together" button appears in Zone B:

```
✓ 065 ↔ 066 snapped (7 pairs, max residual 0.2mm)
[Lock together]
```

**Implementation: use a `rigidGroups` move-together list** (preferred over THREE.js
scene-graph re-parenting, which conflicts with TransformControls):

```js
// rigidGroups: Array of Set<pieceId>
const rigidGroups = [];

function lockTogether(pieceIdA, pieceIdB) {
  // Find existing groups containing either piece
  const groupA = rigidGroups.find(g => g.has(pieceIdA));
  const groupB = rigidGroups.find(g => g.has(pieceIdB));

  if (groupA && groupB && groupA !== groupB) {
    // Merge two groups
    for (const id of groupB) groupA.add(id);
    rigidGroups.splice(rigidGroups.indexOf(groupB), 1);
  } else if (groupA) {
    groupA.add(pieceIdB);
  } else if (groupB) {
    groupB.add(pieceIdA);
  } else {
    rigidGroups.push(new Set([pieceIdA, pieceIdB]));
  }
}

// In the TC `change` event handler, after applying the TC delta to the selected piece:
function applyRigidGroupDelta(movedPieceId, delta) {
  const group = rigidGroups.find(g => g.has(movedPieceId));
  if (!group) return;
  for (const id of group) {
    if (id === movedPieceId) continue;
    pieceGroups[id].position.add(delta);
  }
}
```

In the sidebar, show locked groups:

```
Locked: [065, 066]   [Unlock]
```

[Unlock] removes the pair from its rigidGroup (splits or dissolves as appropriate).

### Task 8 — Record snapped connections in the save payload

When the Cluster mode "Save selected piece" button fires (from PR C), extend the
`assembled` object with the snapped connections for that piece:

```js
// In the save handler, before calling saveViaBridge:
assembled.snapped_connections = snappedPairs
  .filter(p => p.tabPieceId === selectedPieceId || p.landingPieceId === selectedPieceId)
  .map(p => ({
    letter:         p.letter,
    tab_piece:      p.tabPieceId,
    tab_raw_id:     p.tabRawId,
    landing_piece:  p.landingPieceId,
    landing_raw_id: p.landingRawId,
    residual_mm:    p.residual_mm ?? null,
  }));
```

This is additive — the bridge-save PR merges `assembled` into the sidecar, so
`snapped_connections` just rides along without any bridge changes. On cluster reload,
a future session can read these to pre-populate the progress panel dots.

## Verification Checklist

1. Load cluster `anchor`. Switch to Snap mode. Connection spheres visible and brighter.
   Zone A progress panel shows 4 connection groups, all `○ unsnapped`.

2. Click the `landing-e69` sphere on piece **067**. Gold spheres appear on **069**
   (the `tabe` panel — 067 has 4 known partners on 069: letters c, d, e, f). Sidebar
   Zone B shows:
   ```
   Snap: 067 / landing-e69
   Known connections:
     → 069 / tabe  (panel-tab)  [Snap]
   [Snap all 4 pairs → 069]
   [Clear]
   ```

3. Click "Snap all 4 pairs". 069 translates. Sidebar shows max residual.
   Zone A: 067↔069 dot turns `●`. If residual > 1.5mm, yellow banner fires.

4. Click an `attach-b66` sphere on **065**. Sidebar shows:
   ```
   Known connections:
     → 066 / landing-b65  (panel-tab)  [Snap]
   [Snap all 7 pairs → 066]
   ```

5. Click "Snap all 7 pairs". 065 translates into 066. Zone A: 065↔066 turns `●`.
   Max residual shown. All 7 pairs show green lines.

6. Click "Lock together" for 065+066. Move 066 via TC translate. 065 moves with it.
   Sidebar shows "Locked: [065, 066]".

7. Custom snap: click any sphere on **066**, then any sphere on **068** that isn't a
   known partner. "Custom snap" row appears. Click [Snap]. Piece moves.

8. After snapping all pieces: click Save selected piece for each → bridge writes sidecars.
   Each sidecar should contain `assembled.snapped_connections` array.
   Reload cluster → pieces load at snapped positions.

9. Snap mode off → Select mode normal. TC and selection unaffected.

10. No regressions in Bench mode. No regressions in Measure mode.

## What NOT to Change

- Bench mode (PR A + PR B) — snap is Cluster mode only.
- Sidecar schema beyond adding `assembled.snapped_connections` — all other fields per
  DECISIONS #11/#13.
- Rotation — snap is translation-only in v1. If pieces need rotation alignment, the
  user uses the rotation sliders after snapping. Rotation-matching snap (aligning tab
  face normals) is deferred.
- Auto-snap without user confirmation — always require a [Snap] button click. Never
  move a piece without explicit user action.
- The connection graph on disk — snap reads it, never writes it.

## Manual Tests (Alan runs after merge)

| Step | Expected |
|---|---|
| Load cluster `anchor`, enter Snap mode | All 5 pieces load; spheres visible at connection points; Zone A shows 4 connection groups |
| Click `landing-e69` sphere on 067 | 4 partner spheres on 069 highlight gold; Zone B shows "Snap all 4 pairs" |
| [Snap all 4 pairs] | 069 translates toward 067; max residual shown; Zone A 067↔069 turns ● |
| Click `attach-b66` sphere on 065 | 066's landing-b65 and 6 other partners highlight; "Snap all 7" offered |
| [Snap all 7 pairs] | 065 translates into 066; residual < 1mm if geometry is clean; all 7 green lines |
| [Lock together] 065+066 | Moving 066 via gizmo carries 065 |
| Save each piece, reload cluster | All pieces at snapped positions; sidecars have snapped_connections |
| Residual > 1.5mm on any snap | Yellow banner fires with rotation advice |
| Click a non-partner sphere second | Custom snap row appears in Zone B |
