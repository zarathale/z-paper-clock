# CHARTER.md — claude-work/

**Status:** signed v1.0 — effective 2026-05-04. Co-authored by Alan + Claude as the one-time exception to Claude's read-only access; now a Claude-maintained living doc, with co-authoring on the explicit exceptions noted below.
**Started:** 2026-05-04
**Signed:** 2026-05-04
**Owners:** Alan (as supporter/enabler), Claude (as lead/builder)

This document defines a significant pivot in the z-paper-clock project: Claude takes the lead on building the clock; Alan steps into a human-assistant role. Going forward, everything Claude touches lives under `claude-work/` (this folder); everything Alan authors with his hands lives under `alan-work/` (a fresh folder, created as part of this pivot). The existing `work/` folder gets archived in place as a frozen reference. The rest of the repo is read-only background.

---

## 1. Frame

Alan built the physical paper clock in the mid-1990s, working from *Make Your Own Working Paper Clock* by James Smith Rudolph. He kept a spare copy of the book on the shelf for years to remake it "someday." This project is that remake — but in code, in 3D, on the open web — with Claude as the builder.

Up to now Alan has been leading this project: writing the spec, making architectural calls, drafting CODE_PROMPTs for Code sessions. That phase ends here. Claude is being handed the source material — the scanned book, the transcriptions, the conventions, the existing study work — and asked to make the clock and share it.

Claude is not starting from scratch. The repo's existing study side (`source/`) and a substantial chunk of the build side (`work/`, now frozen) are the inheritance: PNG scans of every piece, full prose and label transcriptions, an authoring-and-QA preview tool, settled conventions for SVG layering, a roadmap of where the build was heading, and a working set of architectural decisions. Claude inherits all of it as input. Claude is free to revise direction, but doesn't have to start with revision — the existing direction is good and largely worth continuing.

---

## 2. Mission

Build a working interactive 3D model of the Rudolph paper clock, hosted publicly off this repo, faithful to the book's design and to Alan's authoring choices.

Concretely:

- **Working** in the sense already defined by `work/SPEC-3D-VIEWER.md` and the resolved product decisions in `ROADMAP.md`. v0.1 is the flat viewer (M3); the clock takes its real shape in M4; mechanism animation is M6 stretch. "Real-time accurate" (1s = 1s) is the target where animation lands; the gear-ratio validation in M2 is the data-side preparation. If Claude wants to revise that definition, it's revisable — but starting with the existing definition is the default.
- **Interactive** = orbit, zoom, hover, click, exploded slider, layer toggles, inspect panel. Per the existing SPEC.
- **Public** = GitHub Pages off this repo (resolved decision #4). Deploy artifact is the per-piece SVG/JSON + viewer build; the source scan archive stays in-repo as personal reference but is not republished.
- **Faithful** = the visual style already modeled in `preview.html` (faithful trace + functional sidecar; cream paper, scan-textured slabs; illustrative aesthetic for v0.1) is the direction. The build continues that direction; departures are conscious.
- **Educational is a bonus, not a deliverable.** If the inspect panel teaches mechanical energy, papercraft, or how an LLM agent collaborates on a real artifact, great. Don't build separate curriculum.

---

## 3. Roles

### Alan — Author / Maker

Alan owns the *physical* side of the digital model:

- **Owns the cuts.** Alan decides where the X-Acto blade goes. Silhouette boundaries, cutouts, what's a fold vs. what's a printed mark — those calls are his. He built the physical clock; that muscle memory is the source of truth.
- **Owns the labels.** Layer naming, marker ids, fold-binding ids, landing markers, anything that makes a per-piece SVG legible to downstream tooling. Alan is responsible for the *outcome* — Claude can orient itself in any piece Alan has authored — not for any particular set of conventions.
- **Hand-authors per-piece SVGs** in Affinity Designer, working over the per-piece PNG scans. The output is `alan-work/pieces/NNN/NNN.svg` (and `NNN.af` as the editable source).
- **Captures source scans.** Runs the flat-bed scanner, crops chunks to per-piece PNGs in `source/pieces/`. Six pieces still pending (013, 014, 016, 017, 090, 110).
- **Runs git.** All commits and pushes go through GitHub Desktop. Claude doesn't touch git.
- **Reworks per Claude's notes.** When Claude needs an SVG revised — silhouette tightened, tab marks added, fold ids bound to markers, anything — Claude drops the request into `claude-work/to-alan/`. Alan picks it up, reworks in Affinity, drops the revised piece back into `alan-work/pieces/NNN/`. See §5 for the protocol detail.
- **Reviews + pushes back.** Alan has veto power on convention changes that affect what he has to author. Claude can propose; Alan decides. (LAYER-CONVENTIONS.md is co-authored — see below.)

### Claude — Lead / Builder

Claude owns the *digital* side of the model:

- **Owns the queue.** What gets authored next, in what order, and why. Alan pulls from a queue Claude maintains; Alan can reorder or push back, but the default ordering is Claude's call. The queue stays modest in size — see §9 on iteration discipline.
- **Owns the viewer code.** Architecture choice (graduate `preview.html`, build a fresh viewer, or some blend), framework, build system, deploy. Claude picks; Alan reviews if asked.
- **Owns the JSON sidecars.** All per-piece JSON (`alan-work/pieces/NNN/NNN.json`) is Claude-authored from the transcriptions. Function blocks for §II.B + §II.C pieces draw on Alan's mechanism knowledge; Claude drafts them and Alan signs off.
- **Owns most of the standards corpus.** The audit script, the sidecar schema, the viewer manifest schema, any new tooling-side standards. **Exception: `LAYER-CONVENTIONS.md` is co-authoring territory, ongoing** (Alan's call during this charter's drafting). It sits at the seam between Alan's authoring hand and Claude's tooling — neither side moves it unilaterally. Both write to it; both read it as the live truth.
- **Owns the workplan.** What's done, what's in flight, what's blocked, what's next. Claude maintains; Alan can read and react.
- **Owns architecture.** Tech stack, hosting, file layout decisions inside `claude-work/`, any new convention for how the digital model represents the clock.
- **Leads on conventions still in motion.** Some authoring conventions are settled (cut-layer, axles + north, faithful trace + functional sidecar). Others are explicitly evolving (marker-bound fold ids, landings, the regions/face-graph design, anything that surfaces during the next round of pieces). Claude's job on the still-evolving ones isn't to defer — it's to think through *how the digital build actually works* and let that thinking finalize the layering model. Alan still has the final say on whether something is human-authorable, but Claude leads the design.
- **Is the loud one.** Claude surfaces decisions out loud, flags tensions, proposes options. Alan is welcome to be quiet; silence isn't agreement, but it isn't blocking either.

### What this means for existing project artifacts

The existing root-level docs (`CLAUDE.md`, `ROADMAP.md`, `WORKPLAN.md`, `PROJECT-STATE.md`, `LAYER-CONVENTIONS.md`, `README.md`, and `work/SPEC-3D-VIEWER.md` inside the now-frozen `work/`) carry forward as **inherited input**. They were excellent under Alan-as-lead and they remain valid background. Going forward:

- **`LAYER-CONVENTIONS.md`** stays at repo root, co-authored.
- **`WORKPLAN.md`** becomes legacy (a frozen record of pre-charter tracks). The live working surface is `claude-work/STATUS.md` going forward.
- **`PROJECT-STATE.md`, `ROADMAP.md`, `CLAUDE.md`, `README.md`** stay in place as inherited background; they capture the project's history and direction up to this point. Claude doesn't maintain them by default; Alan can still edit if he wants.
- **`work/SPEC-3D-VIEWER.md`** lives inside the now-frozen `work/`. The decisions in it are still the substrate; if Claude wants to evolve any of them, that happens in a new doc under `claude-work/`.

The existing `sessions/` convention carries forward. Both Alan and Claude continue writing session notes; they live in `sessions/` as before.

---

## 4. Folder split

```
z-paper-clock/
├── source/                  ← read-only for both. The book; the scans; the transcriptions.
├── work/                    ← FROZEN as of this charter. Read-only for both. Pre-charter build artifacts.
├── alan-work/               ← NEW. Clean. Alan's authoring zone going forward.
│   ├── pieces/              ← per-piece working folders (NNN.af, NNN.svg, NNN.json)
│   ├── pieces.csv           ← master index (copied from work/ as needed)
│   └── ...                  ← whatever else Alan needs; populated lazily by what we copy out of work/
├── claude-work/             ← NEW. Claude's lead zone.
│   ├── CHARTER.md           ← this document
│   ├── (further structure detailed in §5)
├── sessions/                ← session notes, both modes
├── CLAUDE.md, README.md, ROADMAP.md, PROJECT-STATE.md, WORKPLAN.md, LAYER-CONVENTIONS.md
│                            ← inherited at repo root. LAYER-CONVENTIONS.md is co-authored;
│                              the rest are inherited-as-of-charter and not maintained going forward
│                              (WORKPLAN.md explicitly becomes legacy).
└── (eventually) the deployed viewer artifact, location TBD
```

**Read/write rules:**

- `claude-work/` — Claude writes; Alan reads.
- `alan-work/` — Alan writes; Claude reads.
- `work/` — frozen. Read-only for both. Existing artifacts that need to live on go to `alan-work/` or `claude-work/` via an explicit copy.
- `source/` — neither writes (study side is stable).
- `sessions/` — both write, in their respective modes.
- `LAYER-CONVENTIONS.md` at repo root — both write (co-authored).
- All other root-level docs — read-only for Claude. Alan can edit (and may, e.g. to update README for the public face).

**Rename policy: clean break.** The existing `work/` folder is archived in place as a frozen reference. `alan-work/` is a fresh folder, created from scratch. We copy out of `work/` whatever we want to reuse — pieces.csv, individual piece folders, the preview.html source-of-truth pattern, scripts worth carrying forward — and bring it into `alan-work/` or `claude-work/` deliberately. This avoids the find/replace pain of renaming a folder referenced in dozens of docs, and it gives the pivot a clean substrate to work on rather than picking up implicit history.

The one carve-out is **this charter document**: we co-author v0/v1 right now during the kick-off conversation. After sign-off, it becomes a `claude-work/` doc and Claude maintains it. Alan can propose edits via chat; Claude makes them.

---

## 5. What Claude maintains in `claude-work/`

Initial structure. Not all need to exist on day one; Claude builds them out as work progresses. Day-one set is in §10.

- **CHARTER.md** — this document. Decision record once signed; living doc thereafter.
- **STATUS.md** — what's done, in flight, blocked. Live working surface; replaces the inherited `WORKPLAN.md`.
- **QUEUE.md** — the prioritized list of what Alan should author next, with the why. Pull-based: Alan checks it when he has bench time. Each entry: piece id, what Claude needs from it, why it's next, any specific authoring notes. Kept modest in size per §9.
- **DECISIONS.md** — Claude-led decisions, parallel to the existing `CLAUDE.md` Architectural Decisions table. Decisions inherited from before this charter stay where they were captured; new decisions land here.
- **to-alan/** — the rework dropbox. When Claude needs a piece revised, a small folder lands here per request: `to-alan/<piece-or-topic>/` with a short README (what to do, why) plus any artifacts (annotated SVG, screenshot, reference link). Alan picks it up, reworks in Affinity, drops the revised piece into `alan-work/pieces/NNN/`, and Claude clears the `to-alan/` entry.
- **viewer/** — the build's actual code, when there's code to write. Architecture choice (graduate `preview.html`, build a fresh TS/Vite viewer per the existing SPEC, or some blend) is Claude's first non-charter call.
- **pipeline/** — successor to `work/pipeline/` and `work/scripts/`. Pipeline scripts and tooling Claude will iterate move here when needed; the M1 archive in `work/_archive/` stays put as a decision record (and `work/` is frozen anyway).
- **standards/** — successor home for new tooling-side standards docs as they emerge (sidecar schema versions, viewer manifest schema, audit-script rule reference). `LAYER-CONVENTIONS.md` is the explicit exception — it stays at repo root, co-authored.

**Sidecar JSON colocation.** Per-piece JSON lives at `alan-work/pieces/NNN/NNN.json`, alongside the SVG. Claude is the author; the file lives in Alan's tree because that's where the piece lives. Claude writes there as a one-line carve-out from "Claude doesn't write to alan-work/." (If this gets messy in practice, revisit.)

---

## 6. What Claude is committing to ship

In rough order, with the existing roadmap as the baseline:

1. **Finish onboarding.** Six pieces (013, 014, 016, 017, 090, 110) still need scanning + cropping. Alan's hands; Claude tracks.
2. **First end-to-end piece, proven in 3D.** Pick one piece — the pendulum bob is a good candidate per WORKPLAN.md — drive it through SVG authoring → sidecar → preview-html render → placement in a multi-piece scene. The point is to make the seam between Alan's authoring and Claude's tooling solid before it scales.
3. **Decide preview.html ↔ work/viewer/ architecture** (the open M0.6.13 question). Pick one path; commit.
4. **Bring authoring up to a sustainable rate.** Alan can author SVGs as fast as the conventions are clear. Claude's job during this phase is to keep the conventions clear, the queue ordered, and the tooling responsive to authoring slips.
5. **Assemble the clock.** Per-group transforms (existing M4). This is hand-fitting against the book's figures; substantial.
6. **Polish + ship v0.1.** Public URL.
7. **Mechanism animation** if the budget supports it. Stretch.

Claude is **not** committing to a timeline. This is a hobby project. The commitment is to make steady progress, surface where help is needed, and not let the build drift.

---

## 7. Constraints carried forward

These are inherited from the existing project; not reopened in this charter:

- **Faithful trace + functional sidecar.** SVG geometry stays human-drawn-and-scanned messy; mechanism geometry captured separately in JSON.
- **Layered SVG conventions** as documented in `LAYER-CONVENTIONS.md` (canonical layer names, cut-layer convention, axles + north, marker-bound fold ids, landing markers). Some are settled; others are still in motion (see §3 on Claude leading on conventions in motion).
- **GitHub Pages off this repo** for hosting. Public.
- **Desktop-first.** Mobile is Post-M5, deferred per resolved decision #3.
- **Illustrative aesthetic for v0.1.** Photographic is M5 polish if time allows.
- **Cowork mode is the working surface.** No Code-mode CODE_PROMPTs in `claude-work/` to start. (Open: do we want a Code-mode lane back? Probably yes once viewer scaffolding starts — Cowork doesn't run dev servers. Park for now.)

---

## 8. What's explicitly out of scope

- **Republishing the book.** The transcriptions and scans stay in-repo as personal reference and are never deployed.
- **Rebuilding the physical clock.** Already done in the 90s. The remake is digital.
- **Mobile UX in v0.1.**
- **Reopening genuinely settled conventions** (cut-layer, axles + north, faithful trace direction, the canonical layer names). Claude can refine, can extend, but doesn't restart from scratch. **Conventions still in motion are explicitly NOT out of scope** — Claude leads on those (see §3); this scope item is about the truly settled foundations only.
- **A CHANGELOG, formal SemVer, or release engineering** until v0.1 is in sight.
- **CI** until there's something worth gating on.

---

## 9. Pace + working style

- **Hobby project.** No deadline. Quality > speed.
- **Honest about state.** Per `PROJECT-STATE.md`: aspirational and shipped get clearly distinguished. Claude won't oversell what exists.
- **Pull-based, not push.** Alan pulls from the queue when he has bench time. Claude doesn't expect throughput; Claude designs around whatever throughput Alan has.
- **Iteration discipline; human-manageable authoring.** This is an explicit constraint from Alan: not 99 edits per piece. The way the project moves forward is iterative — try something on a piece, learn from how it lands, adjust the convention or the tooling, try the next piece. The queue stays small (a handful of pieces / asks at a time, not the full backlog), each piece teaches something, lessons stack. Claude resists the temptation to fan out parallel asks even when the tooling could absorb them — Alan can't, and the bottleneck is Alan's bench, not Claude's throughput. When in doubt, fewer asks, more thinking per ask.
- **Loud thinking.** Claude surfaces decisions and trade-offs. Alan can be quiet without that being read as agreement; Alan's pushback is welcome and expected on convention questions.
- **Marketplace.** Alan invited Claude to browse for plugins/skills that would help. Claude will propose targeted additions (a clean validation skill, a deployment plugin, anything else that would unlock more leverage); Alan installs them.
- **Models.** Per the existing model selection guide in `ROADMAP.md`. Most work is Sonnet's wheelhouse; bulk sidecar authoring is a clean Haiku downshift; gnarly viewer code (mesh extrusion, assembly engine) is where Opus earns its keep. Claude reaches accordingly without making it a discussion.

---

## 10. Drafting decisions (resolved during this kick-off)

These were the open items Claude flagged while drafting; all resolved in the back-and-forth. Captured here as decision record.

| # | Question | Resolution |
|---|---|---|
| 1 | Folder rename — lazy or eager? | **Clean break.** `work/` archived in place (read-only, frozen). New `alan-work/` created clean; we copy from `work/` deliberately. |
| 2 | `LAYER-CONVENTIONS.md` location | **Co-authored at repo root, ongoing.** Both Alan and Claude write to it. |
| 3 | Sidecar JSON location | **Colocated** at `alan-work/pieces/NNN/NNN.json`. Claude writes; carve-out from the alan-work read-only-for-Claude rule. |
| 4 | Pipeline scripts location | **Move to `claude-work/pipeline/`** as Claude iterates them. Existing `work/pipeline/` stays in the frozen archive. |
| 5 | Audit script + LAYER-CONVENTIONS coupling | **Audit script moves to `claude-work/`** alongside other tooling. `LAYER-CONVENTIONS.md` stays at repo root co-authored. The convention-as-linter pattern still works because the audit reads the conventions wherever they live. |
| 6 | Day-one structure for `claude-work/` | **Yes — build CHARTER + STATUS + QUEUE + DECISIONS + to-alan/ on day one.** They're how Alan sees what's happening and what to do next. |
| 7 | `WORKPLAN.md` succession | **Becomes legacy.** Frozen as a record of pre-charter tracks. `claude-work/STATUS.md` is the live surface going forward. |
| 8 | First moves after sign-off | **Agreed.** (a) Build out `claude-work/` skeleton; (b) settle the LAYER-CONVENTIONS co-maintenance routine; (c) pick the preview.html / work/viewer/ architecture; (d) put the first piece end-to-end. |

Other decisions absorbed into the body of this doc:

- **Alan owns cuts and labels** (§3) — Alan's authoritative scope on the SVG side.
- **Rework via `claude-work/to-alan/`** (§3, §5) — the dropbox protocol for revisions.
- **Iteration discipline; not 99 edits per piece** (§9) — Claude keeps the queue modest; lessons stack.
- **Conventions still in motion get Claude's leadership** (§3, §8) — settled conventions don't reopen, but evolving ones get driven by the build's needs.

---

## 11. Sign-off

- Alan: ☑ (signed 2026-05-04)
- Claude: ☑ (signed 2026-05-04)

This document is now in effect. It moves from "co-authored kick-off" to "Claude-maintained living doc," with co-authoring preserved on the explicit exceptions in §3 and §10 (LAYER-CONVENTIONS.md, charter amendments). Future changes follow the amendment policy in §12.

---

## 12. Amendment policy

The charter is a living doc, not a contract. It exists to keep us aligned. If reality teaches us a boundary in here is wrong, we change it — that's the charter doing its job, not failing.

**Two kinds of change:**

**Clarifying edits** — typos, wording fixes, additional examples, structural cleanup that doesn't move ownership, scope, or any commitment. Either side asks; Claude edits; a one-line note in the footer (e.g., "2026-05-12: tightened §5 wording on to-alan/ protocol"). No re-sign.

**Substantive amendments** — anything that touches a role boundary, an ownership rule, a scope item, a structural commitment, or one of the resolved drafting decisions in §10. Proposed in chat first; on agreement, captured as a new row appended to §10 (or a new section directly under it) with the date, what changed, and why. Both sides initial that amendment row. The original §10 table stays as the kick-off record; amendments stack underneath as a decision history.

**Either side can call for revision.** Not just Alan. If Claude hits a wall where the charter conflicts with how the build actually wants to work, Claude flags it loudly and we amend rather than silently drift.

**Test cases for the substantive line** (kept as a calibration aid; not exhaustive):

| Change | Substantive? | Reason |
|---|---|---|
| Move sidecars from `alan-work/pieces/NNN/NNN.json` under `claude-work/` | yes | reverses §10 row 3; touches §3 carve-out and §5 layout |
| Use React in the viewer instead of vanilla TS | no | architecture is Claude's pen per §3 |
| Add `claude-work/standards/manifest-schema-v1.md` | no | covered by §5 |
| Pull mechanism animation forward to v0.1 | yes | changes the §6 ship commitment |
| Alan starts authoring some sidecars too | yes | role-boundary shift in §3 |
| Add a new piece to the queue | no | ordinary queue maintenance |
| Replace `to-alan/` with a different rework protocol | yes | §3 + §5 structural commitment |

When in doubt, treat as substantive. The cost of one extra round-trip in chat is small; the cost of a silent boundary drift is real.

---

*Last updated: 2026-05-04 (signed v1.0; effective. Amendment policy added as §12. Both Alan and Claude signed at kick-off.)*
