---
date: 2026-05-05
start_time: "16:30"
end_time: "17:50"
mode: cowork
participant: Zarathale (Alan)
---

## Goal

Orient post-PR-#15 (panels-aware preview.html, merged earlier today). Verify what shipped. Build out the environment so future sessions don't keep hitting "I can't headlessly verify preview.html" — landed cross-device install doc, headless-browser daemon bridge, charter amendment for proactive tool asks. Then absorb two new authoring conventions Alan surfaced through the bob-batch authoring run (095, 096, 098).

## What was done

### Track 1 — PR #15 verification + bob-batch inspection

- Confirmed PR #15 panels-aware pathway is functional. Audit script + code-path review aligned with the Code session note's verification matrix (069/068/071/099 ✓; 058/113 fall to cut-line-first). Couldn't independently verify in-browser (gap that triggered Track 3).
- Inspected 094 + 097 in-flight authoring (Affinity lock files visible; bench was active). Surfaced three items:
  - 097 Affinity collision-suffix tangle: 5 visually-distinct landings on 099 came out as duplicate `attach-a99` ids + auto-renamed `attach-a991`/`a992`/`a993`/`a994`. Audit reads the suffixed forms as cross-piece partner-pieces 991-994 (which don't exist). Fix path open: script-side convention #16 tolerance vs. author-side per-instance ids. Alan deferred decision.
  - 094 had `main-alan-to-delete` orphan + disconnected fold-component warning. Alan removed the orphan layer; re-render confirmed clean (single sub-tree rooted at pane2).
  - 070 fold-id rename + 110 panel- prefix uplift queued in punch list.
- Punch list delivered: bob batch continuation (095/096/098/093 + escape-wheel 087); 097 collision question; 070 cleanup.

### Track 2 — CHARTER amendment A1 (tool acquisition)

- Alan flagged that the missing-tool ask should be in the charter as standing directive, not me-asking-each-time. CHARTER §9 "Marketplace" bullet rewritten as "Tool acquisition" — proactive ask, explicit cost/benefit (setup time, per-use compute, disk, ongoing cost, expected use frequency), browse marketplace + MCP registry first. Captured as CHARTER amendment A1 in §"Amendment log" + DECISIONS row #8.
- Marketplace probe done (`mcp__plugins__search_plugins` + `mcp__mcp-registry__search_mcp_registry`). No off-the-shelf for headless browser automation. Direct workspace install is right shape.

### Track 3 — Environment doc + headless-browser daemon

- Discovered: **Cowork sandbox can't install Playwright** — network allowlist blocks pypi.org, playwright CDN, github, npmjs. Documented as a standing fact in ENVIRONMENT.md §3.3.
- Pivoted plan: bench-side install + trigger-file daemon bridge.
- Shipped:
  - `claude-work/standards/ENVIRONMENT.md` — canonical build-environment doc (Mac + Windows install paths, Cowork sandbox capabilities/constraints, cross-device sync rules via GitHub Desktop). Becomes single source of truth; CLAUDE.md "Dev environment (mac)" section gains a forward-pointer.
  - `claude-work/scripts/preview_render.py` — local-HTTP-server + Playwright headless Chromium + screenshot/log/JSON output.
  - `claude-work/scripts/watch_and_render.py` — polling daemon that consumes trigger files at `claude-work/state/render-triggers/` and produces output at `claude-work/state/preview-renders/`.
  - `claude-work/scripts/PREVIEW_RENDER_README.md` — full protocol + Mac+Windows install + smoke-test + troubleshooting.
  - `.gitignore` extended for `.venv-headless/`, `claude-work/state/preview-renders/`, `claude-work/state/render-triggers/`.
  - CHARTER §5 updated to name `claude-work/standards/` first resident.
- Smoke test: Alan installed Playwright on his Windows bench, launched the daemon, ran `Out-File` of `069`. Daemon picked it up, rendered, dropped output. Cowork-side trigger of 094 from sandbox bash succeeded too — round-trip ~10 seconds. Bridge fully closed.
- 094 first render surfaced the `main-alan-to-delete` orphan + disconnect warning that the audit didn't catch. Daemon paid for itself within minutes of going live.

### Track 4 — Two new convention extensions from bob-batch authoring

- 095 authoring introduced the **fold-step ordinal prefix**: `<step>-fold-<a>-<b>` encodes the order in which a fold fires during a phased fold sequence. Same step number = simultaneous. 095's pattern: step 1 (central valley pane3-pane4) → step 2 (pane2-pane3 mountain + pane4-pane5 valley, paired) → step 3 (pane1-pane2 mountain + pane5-pane6 valley, closing flaps). Standard accordion-wrap-around-3D-form. Affinity Designer prefixes digit-leading ids with `_` for SVG-spec compliance; author's literal preserved in `serif:id`.
- 095 authoring also introduced **same-piece closure attach via panel-id**: `back-attach-<panel-id>` (or `attach-<panel-id>` on the front) where the suffix matches a panel of the SAME piece. Distinguished from cross-piece `attach-<letter><piece>` by panel-set lookup. Closes a convention gap: same-piece STRUCTURAL attach (vs. registration-only landing in marks).
- Both extensions ratified:
  - DECISIONS row #9 with full reasoning, downstream effects, and rendered example.
  - LAYER-CONVENTIONS.md extended (folds-section gets `<step>-fold-` form; attach-points gets `attach-<panel-id>` form; Parser rules gets fold-step rule + Affinity-underscore rule parallel to convention #16).
  - `claude-work/scripts/build_assembly_graph.py` patched: `parse_fold_bindings` strips leading `_` and extracts `step`; `parse_connection_id` resolves same-piece via panel-set lookup; new `closure_attaches` section in connection-graph output. Re-ran audit → 095's 5 folds resolved with steps 1, 2, 2, 3, 3; 3 closure attaches captured.
  - `CODE_PROMPT_preview-html-fold-step-and-closure-attach.md` drafted ready-for-code at repo root. Mirrors the Python audit-script logic into JS for `parsePanelsFirstFolds` + the attach-points parser. Verification matrix covers 095 (both extensions), 094/069 (regressions), 058 (cut-line-first untouched).
- Bob-batch state at session close: 094 ✓ clean, 095 ✓ clean (both extensions exercised), 096 ✓ clean (1-panel commemoration; "the most complex piece in the book" 😉), 097 has Affinity collision question pending, 098 ✓ clean (3 panels / 2 folds / fold ids parse), 093 in flight on bench, escape-wheel (087) queued.

## Branch / commit

Cowork session — no branch. Commit message at the bottom for Alan to paste into GitHub Desktop.

## Open questions

- **097 Affinity collision-suffix:** script-side convention #16 tolerance for partner-piece extraction vs. author-side per-instance ids. Defer until Alan picks. Either is small.
- **Phased-fold-all slider** as future preview.html UI: with the fold-step convention now ratified, "fold all" could ramp step 1 → step 2 → step 3 in sequence rather than lockstep. Not in the current CODE_PROMPT (stays minimal); worth a follow-up after the parser change lands.
- **Multi-piece scene assembly** still queued from the earlier panels-aware ship — consumes the cross-piece connection graph + closure-attaches.

## Next-session handoff

Two paths Alan can pull simultaneously:

1. **Code session** against `CODE_PROMPT_preview-html-fold-step-and-closure-attach.md` — single-file change, mirrors patched audit logic. After ship, daemon-rendered 095 will show fold-step-aware slider labels and closure-attach console summary.
2. **More authoring** — 093 in flight on bench, escape-wheel (087) queued. Convention is stable.

When the Code session lands, the next Cowork conversation is either (a) multi-piece scene assembly (if 097 collision is resolved + bob batch closes), or (b) the 097 collision-pattern decision.

## Cowork commit message

```
env build-up + headless-browser daemon + fold-step convention
```

```
Three landings in this session, plus PR #15 verification work:

(1) CHARTER amendment A1 lands: §9 "Marketplace" bullet replaced with
"Tool acquisition" — standing directive that I proactively raise tool/
integration/MCP/plugin gaps with explicit cost/benefit (setup time,
per-use compute, disk, ongoing cost, expected use frequency). DECISIONS
row #8 captures the amendment.

(2) Environment doc + headless-browser daemon ships. claude-work/
standards/ENVIRONMENT.md is the new canonical build-environment ref
(Mac + Windows + Cowork sandbox capabilities/constraints incl. the
sandbox-network-allowlist constraint). claude-work/scripts/
preview_render.py + watch_and_render.py + PREVIEW_RENDER_README.md form
the trigger-file daemon bridge that lets me verify preview.html
headlessly from Cowork via Alan's bench Playwright install. Smoke-
tested end-to-end: 069 + 094 render cleanly, ~10s round-trip per
trigger. .gitignore extended for the new state folders. CLAUDE.md
"Dev environment (mac)" gains a forward-pointer to ENVIRONMENT.md.
CHARTER §5 names standards/ENVIRONMENT.md as first resident.

(3) Two convention extensions from 095 authoring ratify as DECISIONS
row #9. Extension A: fold-step ordinal prefix on fold ids
(<step>-fold-<a>-<b>) encodes phased fold sequence; same step =
simultaneous. Extension B: attach-<panel-id> in attach-points layer
encodes same-piece closure attach (distinguished from cross-piece
attach-<letter><piece> by panel-set lookup). build_assembly_graph.py
patched to recognize both forms + Affinity's leading "_" SVG-spec
prefix; new closure_attaches section in connection-graph output.
LAYER-CONVENTIONS.md extended (folds + attach-points + Parser rules
sections). CODE_PROMPT_preview-html-fold-step-and-closure-attach.md
drafted ready-for-code at repo root.

Bob-batch authoring progress: 094 cleaned (main-alan-to-delete orphan
removed); 095 ✓ clean with both new conventions exercised; 096 ✓
("the most complex piece in the book" — single panel, zero folds, the
panels-first convention's robustness check); 098 ✓ clean.

Session note: sessions/2026-05-05-1630_cowork_env-buildup-and-fold-
step-convention.md.
```
