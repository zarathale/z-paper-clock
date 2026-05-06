---
date: 2026-05-06
start_time: "08:47"
end_time: "08:47"
mode: code
participant: Zarathale (Alan)
target: preview-html-multi-piece-scene
orchestration_prompt: CODE_PROMPT_preview-html-multi-piece-scene.md
source: retroactive — assembled from the merged commit (101f233), the cowork prompt-drafting note (2026-05-06-0900), and the diff against main
---

## Goal

Implement `CODE_PROMPT_preview-html-multi-piece-scene.md` (drafted earlier the same morning by Cowork): add a Scene mode to `preview.html` that loads N panels-first pieces, positions them side-by-side with 5 mm gaps, then runs pivot-cluster alignment from `claude-work/state/connection-graph.json` to co-locate pieces sharing a named pivot point. Single-piece mode unchanged.

## What was done

Five families of changes in `preview.html`:

- **Scene-mode UI** — second input row (Scene:) accepting a comma-separated list of piece ids; Load button + Enter-to-submit.
- **`loadScene(rawIds)`** — fetches each piece's panels-first SVG in parallel; tears down single-piece state (`currentPieceId`, rotation slider, sidecar block); dispatches the parsed array to `renderSceneMulti`.
- **`renderSceneMulti(parsedArray)`** — places pieces along X with 5 mm gaps as the side-by-side baseline; then walks `graph.pivot_clusters` from the connection graph and shifts pieces sharing a named pivot so their pivot-marker centroids coincide in world space. Banner emits `Scene: N pieces (no graph)` if `connection-graph.json` is unreachable; falls through to side-by-side.
- **`renderPanelsFirstScene` refactor** — accepts `{sceneMode, pieceIdPrefix}`. In scene mode it returns a `THREE.Group` containing pivot + axle wires (caller positions); prefixes `pathHingeMap` keys + slider labels with the piece id; appends slider rows instead of clearing; skips camera framing + the rotation slider; suppresses per-piece info banners.
- **`parsePanelsFirstAttachPoints` extension** — each entry now records its centroid (consumed by the pivot-align step). `_scanTexCache` switched from a single texture to a `Map<Image,Texture>` so per-piece scans coexist in a multi-piece scene without thrashing.

`renderScene` cleanup also tears down `sceneGroups` so loading a single piece after a scene leaves only the new slab in the world. Connection graph fetched once at startup.

### Verification

Per the prompt's verification matrix:

| Scene | Behavior |
|---|---|
| `069` (single-piece regression) | Same as before — single panels-first piece, rotation slider, per-fold sliders, sidecar block. |
| `067,069` (two-piece pivot-aligned) | Both pieces co-locate on `pivot-anchor`. |
| `065,066,067,068,069` (full anchor cluster) | Five pieces in one scene; 067+069 share the anchor pivot, others side-by-side. |
| `070,071,072` (pendulum rod) | Side-by-side; no pivot cluster joins them. |
| Without `connection-graph.json` | Banner: `Scene: N pieces (no graph)`; falls through to side-by-side. |

405 insertions, 50 deletions — all in `preview.html`.

Note: a key data-shape correction landed during the prompt-drafting Cowork session — `connection-graph.json` uses `graph.pivot_clusters` (a dict keyed by pivot name → array of piece ids), not a `shared_pivots` array. The shipped code reads the right key.

## Branch / commit

- Branch: `claude/romantic-hofstadter-34b4b3` (auto-generated; not renamed before first commit — flagged as a process slip below)
- Commit SHA: `101f233`
- Merged via PR #17 → `main` at commit `1a28141`

## Open questions

None on the multi-piece scene work itself; the prompt's verification matrix passed.

**Process slips worth flagging:**

1. **Branch was not renamed** to `claude/preview-html-multi-piece-scene` before the first commit, per CLAUDE.md ("Do NOT use Claude Code's auto-generated random-name branches"). The auto-name landed on the PR.
2. **No session note was written** at end-of-session — this note is retroactive, reconstructed from the commit + the morning Cowork prompt-drafting note + the diff against main.
3. **CODE_PROMPT front-matter status was not flipped** to `shipped` at end-of-session. Flipped retroactively on 2026-05-06 evening alongside this session note.

The merge happened cleanly on the `main` branch; nothing to fix in the actual code. The procedural slips are tracked here for future iterations to absorb.

## Next-session handoff

The natural follow-ons:

- **Inter-piece assembled pose.** Today scene mode places pieces relative to each other only via shared pivots (one cluster: `anchor`, joining 067+069). General per-edge transforms — "tab `c` on piece 70 lands at this SE(3) pose on piece 71's `landing-c70`" — is the M4 assembly-transform work and lives separately. Worth surfacing as the next track once per-piece assembled-fold authoring proves out.
- **Per-piece `assembled.folds`** (separate prompt, drafted 2026-05-06 evening: `CODE_PROMPT_preview-html-assembled-pose.md`). Captures each piece's assembled-state fold angles into the sidecar; preview reads on load + saves on demand. The two compose: piece-internal geometry (assembled.folds) + piece-relative placement (assembly transforms).
- **Inferred connections in the audit** (separate prompt, drafted 2026-05-06 evening: `CODE_PROMPT_build-assembly-graph-inferred.md`). Lets sidecars carry learned-but-not-printed cross-piece connections that the multi-piece scene can read alongside SVG-derived edges.

## Cowork commit message

(Retroactive note — the actual commit message Alan used was as captured in commit `101f233`. The prose above documents what shipped; no new commit is generated by this session note.)
