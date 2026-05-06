---
date: 2026-05-06
start_time: "17:00"
end_time: "17:00"
mode: code
participant: Zarathale (Alan)
target: build-assembly-graph-inferred
orchestration_prompt: CODE_PROMPT_build-assembly-graph-inferred.md
---

## Goal

Implement `CODE_PROMPT_build-assembly-graph-inferred.md` (drafted by Cowork the same day, see `sessions/2026-05-06-1520_cowork_assembled-pose-and-inferred-connections.md`): extend `claude-work/scripts/build_assembly_graph.py` to read `connections.inferred[]` from each piece's JSON sidecar (`work/pieces/NNN/NNN.json`) and merge it with SVG-derived edges. Every edge in the output graph gains a `provenance` field of `"authored"` or `"inferred"`. Conflict detection between authored and inferred entries runs as a soft warning — the script never fails on conflicts.

This is the audit-side companion to DECISIONS #10 (the schema is locked there; this session implements the merge).

## What was done

Five families of changes in `claude-work/scripts/build_assembly_graph.py`:

- **`parse_sidecar` + `extract_inferred_connections`** — two new stdlib-only helpers near the SVG-parsing layer. `parse_sidecar` reads `NNN.json` next to the SVG and returns parsed dict or `None` on missing/malformed (warning to stderr; never raises). `extract_inferred_connections` walks `connections.inferred[]`, drops entries without `kind` or `source` (warning), and emits normalized records with `from`/`to`/`kind`/`side`/`tab`/`letter`/`name`/`panel`/`source`/`note`/`provenance: "inferred"`.
- **`parse_piece` extended** — reads sidecar via `parse_sidecar(svg_path.parent)` and attaches `inferred_connections` to each piece record alongside the existing `attach_points`/`marks`/`folds`/etc. fields. Sidecar-less pieces simply get an empty list.
- **`build_connection_graph` reshaped into 4 passes** —
  1. Authored walk (existing logic), now tagging every edge / closure / pivot member with `provenance: "authored"`.
  2. Inferred merge: per-piece, dispatch each `inferred_connections` entry by `kind` — `landing`/`attach`/`hole` append to `edges` with `source_layer: "sidecar.connections.inferred"` and `provenance: "inferred"`; `attach-same-piece`/`landing-same-piece` append to `closure_attaches`; `pivot` appends to both the legacy flat-list `pivot_groups` and a new richer `pivot_groups_provenance`.
  3. Validation: same `_find_letter_match` heuristic and partner-id `zfill(3)` normalization runs over the unified edge list, so inferred edges get the same `valid` / `matched_panel` / `matched_via` annotations as authored ones (and the same `valid: false, reason: "partner piece N not authored yet"` shape if the partner doesn't exist).
  4. Conflict detection: signature `(from, to, kind, letter|tab|name|panel)` for cross-piece edges; `(piece, kind, panel)` for closures; `(piece, "pivot", name)` for pivot membership. Inferred entries that match any authored signature land in a new `inferred_warnings: [...]` list. Stderr warning fires on count > 0; script exits 0 either way.
- **`pivot_clusters` shape preservation** — the legacy `dict[str, list[piece_id]]` flat-list shape is unchanged (preview.html scene loader keeps working). New parallel `pivot_clusters_provenance: dict[str, list[{piece, provenance, source?, note?}]]` carries the richer view. Inferred pivot members appear in BOTH (per Verification #5 spec).
- **Markdown report** — added `prov` column to the existing "Cross-piece connections" table; new "Inferred connections (from sidecar)" section with source/note column; new "Inferred conflicts" section enumerating warnings (empty state `_(no conflicts detected)_`); "Closure attaches" gained `prov` and `source` columns; "Shared pivots" now annotates each member as `067 (authored), 069 (authored), 068 (inferred)`. Per-piece detail's attach-points list now interleaves inferred entries with `_(inferred)_` label, `[inferred]` tag, and source/note as italic sub-bullets.

`main()` summary print extended with the authored-vs-inferred edge breakdown and inferred-conflict count.

### Verification

Per the prompt's verification checklist (all run from the worktree at `.claude/worktrees/reverent-blackburn-2b31b1/`):

| # | Check | Result |
|---|---|---|
| 1 | Baseline regression with no sidecars | ✓ 33 authored edges (was 33), 1 pivot cluster, 3 closure attaches, 10 untyped landings — byte-identical to prior except for added `provenance: "authored"` on every edge / closure, new top-level `pivot_clusters_provenance`, `inferred_warnings: []`, and per-piece `inferred_connections: []`. The legacy `pivot_clusters` dict shape unchanged. |
| 2 | Sidecar happy-path: `068 → 069` attach `z` | ✓ Inferred edge surfaces in `connection-graph.json` with `provenance: "inferred"`, `source: "test"`, `valid: false`, `reason: "partner has no feature matching letter 'z'"` (same shape as authored validation). Markdown shows row in "Inferred connections" table and `_(inferred)_ (attach → piece 069 (letter/tab z)) [inferred]` on 068's per-piece detail. |
| 3 | Conflict detection: `065` inferred dup of authored `attach-e66` | ✓ `inferred_warnings` contains one entry with `kind_of_conflict: "edge"`, the inferred source, and the dedup-suggestion message. Markdown's "Inferred conflicts" section lists it. |
| 4 | Same-piece closure inferred: `068` `attach-same-piece` panel `main` | ✓ Lands in `closure_attaches` with `provenance: "inferred"`, `source: "v4-test"`, `raw_id: None`. |
| 5 | Inferred pivot: `068` joins `pivot-anchor` via sidecar | ✓ Legacy `pivot_clusters["anchor"]` is `["067", "069", "068"]`; `pivot_clusters_provenance["anchor"]` lists 068 as `provenance: "inferred"` alongside authored 067/069. |
| 6 | Malformed sidecar resilience: `attach` entry missing `source` | ✓ Stderr warning `inferred[2] missing source; skipped`; entry dropped; script exits 0. |
| 7 | preview.html scene-mode regression | Structural: legacy `pivot_clusters` flat-list shape preserved verbatim from the prior schema; preview.html consumer's read path is unchanged. Live browser test from this Windows worktree out of sandbox scope (per CLAUDE.md "Don't try to host the viewer dev server from the Cowork sandbox"); flagged for Alan to run from the local checkout if desired. |

All temporary test sidecars (`work/pieces/065/065.json`, `work/pieces/068/068.json`) deleted after their respective verification runs; final `connection-graph.{json,md}` is the no-sidecar baseline + structural extensions. Stash-and-rerun confirmed the prior committed graph also produced 33 edges (the prompt's "16 pieces / 24 edges" count was pre-pendulum-batch and pre-095/099 — current panels-first-piece count is 18).

## Branch / commit

- Branch: `claude/build-assembly-graph-inferred` (renamed from auto-name `claude/reverent-blackburn-2b31b1` before first commit per CLAUDE.md).
- Commit: TBD (see end-of-session output).

## Open questions

None blocking. Real `connections.inferred[]` content lands when Cowork (or Alan) starts authoring sidecars off the instructions text or bench notes — the merger is now ready to receive them. The `pivot_clusters_provenance` parallel-key shape is a deliberate backward-compat hedge; if a downstream consumer wants to read provenance on pivot members, point it at the new key.

## Next-session handoff

- This branch is ready for review and merge. After merge, no follow-up Code task is queued from this prompt. The companion `CODE_PROMPT_preview-html-assembled-pose.md` (DECISIONS #11) is the next preview-side track.
- If Alan wants to validate Verification #7 live: from the local mac checkout, `cd work/viewer/...` (or open `preview.html` per the existing scene-mode workflow) and load `065,066,067,068,069`. The scene loader reads `claude-work/state/connection-graph.json`'s legacy `pivot_clusters` field — the new file format on `main` after this PR merges is fully compatible with that read path.
