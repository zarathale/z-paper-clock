---
date: 2026-05-01
start_time: "02:00"
end_time: "TBD"
mode: cowork
participant: Zarathale (Alan)
source: retroactive — reconstructed from restart-prompt.rtf + repo state (two interrupted sessions, no prior notes filed)
---

## Goal

Set Affinity SVG export settings for piece 069, verify layer/id structure survives the round-trip, and begin a three.js 3D render of the piece folded correctly — to learn workflow lessons from one real piece before generalizing.

---

## What Was Done

### Session A — SVG export settings + layer model revision

**Context at start:** piece 069 (`inbox/069.af`, `inbox/069.png`) chosen as first test piece. 069 = "Anchor-bearing box; + center mark" (plate H, §II.C anchor-pendulum group). Good choice: it actually folds into geometry (a hinged box net), unlike a flat tab.

**Layer model redefined.** The canonical 8-layer model from SPEC-3D-VIEWER.md was revised mid-session:

| Old layer | Decision |
|---|---|
| `silhouette` | **Drop** — already done; alpha channel handles this |
| `cutouts` | **Drop** — same; alpha |
| `labels` | **Drop** — ambiguous, superseded |
| `marks-other` | **Drop** — superseded |
| `folds-valley` | **Keep** |
| `folds-mountain` | **Keep** (not yet authored on 069) |
| `axles` | **Keep** — mechanism geometry, separate role from marks |
| _(new)_ `marks` | **Add** — single layer containing `tab-X` and `landing-X` ellipses |

**Naming convention locked:** `<role>-<label>` (lowercase). So `tab-a`, `landing-a`, `axle-anchor-pivot` (axles stay in their own layer using full descriptive IDs). The `marks` layer holds both tab markers and landing markers in one group; globally-unique IDs solve the duplicate-id problem that would have appeared in the two-layer version.

**Affinity export settings confirmed:**
- Preset: **"SVG (digital - high quality)"** (not "SVG (for export)" — that strips group structure)
- Don't export hidden layers: **OFF** (want all authored layers)
- Use document resolution: **ON**
- Rasterize: **"Nothing"**
- Decimal places: **3**
- Flatten transforms: **OFF** (implicit in the preset; preserves `id=` nesting)

**Export verified.** SVG exported to `inbox/069.svg`. All IDs survived cleanly. Structure confirmed in file:

```
viewBox: 0 0 3417 3342

Layers (flat siblings of SVG root):
  <g id="Background">  — embedded scan underlay (base64 PNG, 820×802)
  <g id="folds-valley">  — 8 paths (fold hinge lines)
  <g id="marks">  — 11 ellipses:
      tab-a  cx=920.8   cy=929.2
      tab-b  cx=2587.5  cy=908.3
      tab-c  cx=1787.5  cy=470.8
      tab-d  cx=395.8   cy=1756.2
      tab-e  cx=3120.8  cy=1770.1
      tab-f  cx=1812.5  cy=2979.2
      tab-g  cx=1808.3  cy=2575.0
      landing-a  cx=2712.5  cy=1275.0
      landing-b  cx=829.2   cy=1270.8
      landing-h  cx=2716.7  cy=2675.0
      landing-i  cx=841.7   cy=2670.8
  <g id="axles">  — 1 ellipse:
      anchor-pivot  cx=1771.7  cy=1729.2  (rx=30.9, ry=33.3)
  <image id="_Image1">  — the actual scan raster (referenced by Background)
```

**Anchor pivot is dead center:** cx=1771.7, cy=1729.2 within a viewBox of 3417×3342 → ~51.8% across, ~51.7% down. Matches the printed `+` mark.

**Fold topology mapped from the 8 paths:**

| Feature | x range | y range |
|---|---|---|
| BASE rectangle | ~1061–2452 | ~1162–2333 |
| Left outer fold | ~575 | ~1125–2358 |
| Right outer fold | ~2929 | ~1170–2400 |
| Top outer fold | ~1062–2450 | ~670 |
| Bottom outer fold | ~1070–2458 | ~2812 |

BASE width ≈ 1391 px, height ≈ 1171 px. Anchor pivot sits dead center on base. ✓

**Tab/landing topology for 069:**
- Tabs a–g are authored; landings a, b, h, i are authored.
- Tabs c–g glue to other pieces; tabs a/b glue to this piece's own landings a/b (self-closure corners). Landings h/i receive tabs from other pieces.

---

### Session B — Scan-as-texture pivot + 3D start (cut short)

**Major pivot: scan as surface texture.** During review of the exported SVG, Zarathale clarified the embedded scan background is **intentional and wanted** — not to be stripped. The scan PNG should wrap around the 3D surface as the face texture, giving the render "human feel" (Smith Rudolph's 1983 pen weight, paper texture, registration offsets survive into 3D). This supersedes the SPEC's "illustrative-first / photographic-in-M5" resolved decision and is a significant upgrade.

Rationale:
- Consistent with faithful-trace: SVG geometry is artifact-faithful; scan-as-texture makes the full rendering artifact-faithful.
- Same three.js code path: `ImageTexture` vs `CanvasTexture` is a trivial swap; UV coordinates write themselves because the scan and authored SVG paths are already in registered coordinates.
- When the silhouette is partitioned into hinged sub-meshes along fold lines, each face keeps its scan region — texture "follows" the fold as the paper does.

Tradeoffs flagged (not blockers):
1. **Bundle size** — downsample to ~256–512 px on long side for viewer (~10 MB total for 120 pieces at ~80 KB each). Need a new "downsample-for-viewer" pipeline stage not in current SPEC.
2. **Back face** — back of paper is cream only; don't mirror scan onto inside of folded box.
3. **Scan quality now affects final deliverable** — every speck is in the render. Gen-2 flat-bed captures are clean enough; worth a re-look at the 117 existing `source/pieces/` captures once they're the visible surface.
4. **Edge pixel quality at sharp folds** — untested; want to see 069 folded with scan applied before committing.

**Spec revisions held** (two items queued; to be written together):
- Layer model (marks / tab-X / landing-X)
- Scan-as-texture material model + "downsample-for-viewer" pipeline stage

**3D build started, not completed.** Three.js HTML model (base + 4 walls, scan as face texture) was being assembled when the session hit a usage limit. The model was not written to disk. Alan pushed the updated 069.svg from a different device.

---

## Open Questions

- Does the scan texture read cleanly at sharp fold angles in three.js? (Answer pending 3D test.)
- Tabs c–g: which specific pieces do they connect to? (Needed for assembly graph in M4; not needed now.)
- `folds-mountain` layer: not yet authored on 069. Does any wall on this piece have a mountain fold? Check the book.

---

## Next-Session Handoff

Pick up where the 3D build got cut off:

1. Read this session note.
2. The SVG is at `inbox/069.svg` — structure confirmed correct.
3. Goal: build a three.js HTML rendering of 069 folded into its box shape, with the scan PNG as the face texture. Simplified model: base + 4 walls only (ignore corner triangular flaps and lid/tab extensions beyond outer folds). Enough to demonstrate the scan-as-texture workflow.
4. Once the render looks right: note what spec sections need updating (layer model, material model, pipeline stage), but hold the spec edits for a dedicated pass.
