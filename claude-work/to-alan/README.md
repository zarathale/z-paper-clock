# to-alan/ — the rework dropbox

When Claude needs a piece revised — silhouette tightened, tab marks added, fold ids bound to markers, anything Alan-side — a small folder lands here per request. Per CHARTER §3 + §5.

## Shape of a request

```
to-alan/
└── <piece-or-topic>/
    ├── README.md            ← what to do, why, how Claude will know it landed
    ├── (artifacts)          ← annotated SVG, screenshot, reference link, etc.
```

The README inside each request explains:

- **What** — concrete change Alan should make in Affinity (or the scanner / cropper / wherever).
- **Why** — what unblocks downstream once it lands.
- **Where** — the path the revised piece should land at (typically `work/pieces/NNN/NNN.svg` per the inherited filename convention).
- **Verifies via** — how Claude will know the rework landed (audit re-run, preview.html load, visual check).

## Lifecycle

1. Claude drops a request folder in `to-alan/`.
2. Alan picks it up when he has bench time. Pull-based (CHARTER §9).
3. Alan reworks in Affinity (or wherever), commits the revised piece via GitHub Desktop.
4. Claude clears the request folder once the rework is verified.

## Right now

Empty. No requests open at charter sign-off.

---

*Created 2026-05-04 at charter sign-off as part of the day-one skeleton.*
