---
date: 2026-05-10
start_time: "21:00"
end_time: "22:06"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Continue ring-lock work on piece 066, then compute and write the assembled.transform needed to position 066's heptagonal pivot box around pieces 065 and 067 in the cluster scene.

## What was done

### Ring-lock event delegation (final fix, from prior context)

The per-slider constraint listeners weren't firing (possibly closure-variable capture). Rewrote using event delegation: one `body.addEventListener('input', ...)` with `paneSliderRefs.indexOf(event.target)` identifying the dragged fold. When ring-lock is active and a pane fold is dragged, the other N-1 pane folds redistribute equally to keep Σ_pane constant. The closure fold (fold-tabaa-pane7) is deliberately NOT touched by the constraint. This fix was applied just before the context window filled.

### 066 assembly geometry computation

User pivoted from ring-lock testing to: "assemble 066 around 065 and 067." This required computing the correct `assembled.transform.translation` for 066 so its folded heptagonal tube is centered on the anchor-pivot at world (0,0,0).

**Correction from user:** "tube casing" is the wrong description. 066 forms a **pivot bearing box** — it wraps specifically around the pendulum anchor pivot point, forming a completely enclosed solid-walled 3D housing. The axle goes straight through it. 065 (anchor arm) and 067 (anchor rear plate) are the two face panels; they extend well beyond the box. Only the pivot area is enclosed.

**Key geometry facts derived:**

- `MM_PER_UNIT = 0.01016` mm/unit (from embedded PNG thumbnail diagonal at 600 DPI assumed)
- 7 pane heights: 4478, 2246, 1202, 3085, 1191, 2621, 3434 SVG units → 45.5, 22.8, 12.2, 31.3, 12.1, 26.6, 34.9 mm
- Cyclic polygon circumradius R = 31.2 mm → tube diameter ≈ 62 mm
- Strip wall depth (fold-to-fold): 20.3 mm
- Closure gap with saved fold angles (68°, 33°, 42°, 41°, 36°, 59°, 81°): 0.53 mm — essentially perfect
- All pane fold lines in 066's SVG run consistently (left-to-right folds have signFwd=-1; right-to-left folds have signFwd=+1; both give +deg around +X axis → all consistent fold direction)
- Tube center in 3D (before pieceGroup Y rotation): (0, 70.79, −23.89) mm relative to silBbox center
- After Y rotation of −89.9°: tube center is at world (23.89, 70.79, −0.04) mm when translation=[0,0,0]
- Required translation to center tube on world origin: **[−23.9, −70.8, 0]**

The Y offset (70.8 mm) is intrinsic: the heptagonal polygon's centroid does not coincide with the strip's geometric center after folding, because the seven panels have unequal heights and the tube "curves away" asymmetrically.

**Written to `work/pieces/066/066.json`:**
- `assembled.folds` unchanged (the ring-cyclic angles from prior session are correct)
- `assembled.transform.translation` updated from `[0,0,0]` to `[-23.9, -70.8, 0]`
- Added `note` field explaining the offset derivation

**Z position note:** 066's walls span Z ≈ −10mm to +10mm in world space (strip width = 20mm). Both 065 and 067 are saved at Z=0 (the middle of the box depth). This means the face plates appear to pass through the mid-wall rather than sitting flush at the open ends. Acceptable for visualization — the spatial relationship is clear. To fix properly: 065 needs Z ≈ +10mm, 067 needs Z ≈ −10mm (or 066 shifted in Z with appropriate face adjustments).

## Open questions

- Does the computed translation actually look right when loading "065,066,067" as a scene in preview.html? (Browser verification needed — cannot confirm from Cowork sandbox)
- If the Y is still off, adjust with TransformControls and save a new assembled pose
- Ring-lock event delegation fix: not yet confirmed working by user (they pivoted before testing it)

## Next-session handoff

1. In preview.html bench mode, load piece 066 and verify ring-lock event delegation works (drag a pane fold while locked; other 5 pane folds should redistribute equally)
2. Switch to cluster mode, type `065,066,067` in the Scene input, hit Load — confirm 066's tube appears roughly centered on the anchor-pivot area
3. If translation is off: select 066 in cluster mode, use TransformControls to correct, save assembled pose
4. Architecture decision still pending: graduate preview.html into `work/viewer/`, keep as a parallel authoring tool, or replace? See `claude-work/STATUS.md` `preview.html iteration` track
