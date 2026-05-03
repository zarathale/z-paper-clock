# source/pieces/ — per-piece source archive

Canonical archive of human-validated, individually cropped piece scans. One file per piece, lossless PNG.

## Naming

```
NNN.png       — bare numbered piece (e.g., 004.png, 010.png, 122.png)
NNNa.png      — letter variant (e.g., 092a.png, 112a.png)
```

Three-digit zero-padded piece number. Lowercase letter suffix only when the piece has a real letter variant in the master list (`work/pieces.csv`). The file extension is `.png`, lossless.

## Workflow

1. Capture multi-piece chunks on the flat-bed scanner (see `source/SCAN-INTAKE-CHECKLIST.md`).
2. Save the chunk directly to `source/scans-chunks/` (canonical chunk filename: `NN_NN_NN.{jpeg,png}` listing the COMPLETE pieces inside, ascending).
3. Crop each named piece from the chunk in your editor (Affinity / Photoshop / Preview / GIMP).
4. Save the crop as `NNN.png` directly into this folder.
5. Run the asset-state audit (`python work/scripts/audit_state.py`) to validate filenames against `work/pieces.csv`, run image-health checks, and report inventory status (which pieces are still missing).

## Notes

- This folder is the source-of-truth granularity for the build. The pipeline (`02-trace.py` onward) reads from here.
- This folder holds **only `NNN.png` (and `NNNa.png`)** scans. Authoring files (`.af`) and derivative SVGs/JSONs live one folder over at `work/pieces/NNN/`. The audit flags strays.
- The master piece list is `work/pieces.csv`. If a piece # in this folder isn't in the master list, it's a flag worth investigating before tracing.
- Don't commit speculative pieces to this folder before they're scanned and validated.
