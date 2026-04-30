---
date: 2026-04-30
start_time: "19:00"
end_time: "20:30"
mode: cowork
participant: Zarathale (Alan)
source: retroactive — assembled from sessions/interruptedsession001.rtf, the working tree at session-end, and a follow-on resumption pass that closed out the documentation gaps
---

## Goal

Pivot the gen-2 source-archive workflow from "whole-plate scans on a flat-bed home scanner" to "multi-piece chunks → hand-crop in editor → per-piece PNG archive," and reshape `pieces.csv`, `SCAN-INTAKE-CHECKLIST.md`, `ROADMAP.md` M0.5, and `CLAUDE.md` to match. The plate-based approach settled in `2026-04-30-1800_cowork_rescan-restructure.md` was retired same-day after Zarathale confirmed the home scanner bed can't fit a whole plate.

## What was done

**Trigger.** Continuation of the 18:00 rescan-restructure session. Zarathale began capturing on the home scanner and discovered (a) a whole plate doesn't fit, and (b) chunk captures naturally arrive named by which complete pieces are inside (e.g., `43_44_45_51.jpeg`). The plate-based intake assumed in the 18:00 session — `source/scans-raw/p00x-plate-X-...jpg` consumed by `01-crop.py` + `pieces.csv` bbox fractions — became obsolete on contact with the scanner.

**Two rounds of design questions** (via AskUserQuestion). First round established the macro shape: chunks named by complete pieces inside; per-piece archive is `source/pieces/NNN.png` (lossless PNG, three-digit zero-padded); letter variants `092a` / `112a`; chunks archived to `source/scans-chunks/` as recovery references. Second round settled operational details: `pieces.csv` reshapes to a 123-row master index without bbox columns; the ingest skill is a future Cowork+Code authoring pass; `SCAN-INTAKE-CHECKLIST.md` gets fully rewritten rather than forked.

**Reversed a same-session mis-call.** Earlier in the session, Claude proposed setting aside `plateD.jpeg` and `plateD-2.jpeg` as edge-clipped. Zarathale corrected the framing read: `plateD.jpeg` is a complete chunk of pieces 4, 18, 19, 26, 29, 30, 31, 32, 91, 92 (everything except 10), and `plateD-2.jpeg` is a complete single-piece chunk for piece 10. They're a complementary pair covering plate D fully. They were renamed to canonical chunk form and promoted alongside the rest.

**Files moved (during session, before cutoff).**

```
inbox/plateD.jpeg                   → source/scans-chunks/4_18_19_26_29_30_31_32_91_92.jpeg
inbox/plateD-2.jpeg                 → source/scans-chunks/10.jpeg
inbox/platecenter1.jpeg             → source/scans-chunks/33_37_40_41_50.jpeg
inbox/platecenter2.jpeg             → source/scans-chunks/42_52_53_54_55_56_57.jpeg
inbox/platecenter3.jpeg             → source/scans-chunks/43_44_45_51.jpeg
inbox/platecenter4l.jpeg            → source/scans-chunks/34_35_l.jpeg
inbox/platecenter5l.jpeg            → source/scans-chunks/34_35_r.jpeg
(stitched composite already authored in editor) → source/scans-chunks/34_35_stitched.png
```

Filename rule on file: list every piece whose silhouette is fully visible and not edge-clipped, ascending. Partial neighbors are deliberately omitted from the filename.

**Files created (during session, before cutoff).**

- `source/pieces/` (with `README.md` and `.gitkeep`) — canonical per-piece source archive.
- `source/scans-chunks/` (with `README.md`) — chunk recovery archive.
- `work/scripts/build_master_list.py` — generator that emits `pieces.csv` from `source/transcriptions/embedded-labels.md` + `instructions.md`. Run it to regenerate the master list when the schema changes or new pieces are discovered.
- `work/pieces.csv` (replaced) — master index, 123 rows (1–122 + 92a + 112a). Schema: `id, plate, section, bucket, status, notes`. Bbox columns dropped. Plate-D bucket assignments preserved verbatim from the M1 partial-csv; all other buckets blank pending per-plate triage in M2.

**Files updated (during session, before cutoff).**

- `source/SCAN-INTAKE-CHECKLIST.md` — full rewrite for the chunk-and-crop loop. Capture standard, naming conventions for chunks vs. per-piece archive, six per-file QC checks, per-piece crop guidance, promotion procedure.
- `CLAUDE.md` — "Where We Are" status table reworked to add chunk-scan and per-piece-archive rows; M0.5 row reshaped; pieces.csv row updated. "Architectural Decisions" gained three new closed rows (chunk-and-crop onboarding; pieces.csv schema; per-piece archive format). "Known Issues / Tech Debt" gained the pipeline-reshape pending and pieces.csv bucket-coverage entries. "File Naming Conventions" split into source / derivative / chunk / legacy paths. Footer last-updated note added.
- `ROADMAP.md` — milestone-index M0.5 row updated to point at chunk-and-crop. Milestone-index footer updated.

**Files updated (in this resumption pass, after cutoff).**

- `ROADMAP.md` — §M0.5 body section rewritten end-to-end. New header ("Chunk-and-crop onboarding + pipeline reshape"), new goal, new why-this-exists pointing at the right session note, new strategy section, new 9-task table reflecting the chunk-and-crop loop and pipeline reshape, new verification + what-not-to-do. Footer last-updated note refreshed. The session-note reference at line 32 of the milestone-index was a `19xx` placeholder; updated to `2026-04-30-1900_cowork_chunk-and-crop-pivot.md`.
- `.gitignore` — added `inbox/_pending-rescan/` so the set-aside zone is never committed.
- `inbox/ChatGPT Image Apr 30, 2026, 12_13_57 PM.png` → `inbox/_pending-rescan/` — set aside per Zarathale's call. The file remains on disk but is now gitignored.
- `sessions/2026-04-30-1900_cowork_chunk-and-crop-pivot.md` — this note.

**Files explicitly NOT touched.**

- `source/transcriptions/*` — text content is scan-independent.
- `source/_archive/phone-scans-2025/` — gen-1 archive untouched.
- `work/_archive/m1-plate-d-phone/` — M1 outputs and sidecars stay archived; the 11 plate-D sidecars will copy forward verbatim into the M0.5 retrace.
- `work/pipeline/*` — pipeline scripts. `01-crop.py` is slated for archival in M0.5.6, but that's a Code task; not done in this session.
- `work/scripts/preprocess_scans.py` — gen-1 era flat-field + bleed suppression. May be re-tuned per-piece during M0.5.4 if specific captures need it, but unchanged here.
- `CODE_PROMPT_M1-pipeline-plate-d.md` and `CODE_PROMPT_M1-fix-pipeline-trace.md` — preserved as shipped decision records.
- `work/SPEC-3D-VIEWER.md` — design source of truth, scan-independent.

**Verification (post-resumption).**

```
$ ls source/pieces/
README.md   (folder ready to populate)

$ ls source/scans-chunks/
10.jpeg                                 4_18_19_26_29_30_31_32_91_92.jpeg
33_37_40_41_50.jpeg                     42_52_53_54_55_56_57.jpeg
43_44_45_51.jpeg                        34_35_l.jpeg
34_35_r.jpeg                            34_35_stitched.png
README.md

$ wc -l work/pieces.csv
151 work/pieces.csv     # 124 data rows + comments/header

$ ls inbox/
.DS_Store  _pending-rescan/   # ChatGPT image set aside; gitignored
```

Master list row count: 124 (123 unique pieces + one accounting line that's the empty trailing newline; effectively 123 piece rows). Plate-D rows carry forward bucket assignments from M1 unchanged. SCAN-INTAKE-CHECKLIST.md, CLAUDE.md, and ROADMAP.md M0.5 are all coherent on chunk-and-crop terminology and the new pipeline shape.

## Open questions

None blocking. Two follow-ups queued, both already in M0.5:

- **Piece-scan ingest skill (M0.5.2).** Workflow design settled this session; SKILL.md draft is a Cowork task and the runtime helper is a Code task. Will need a `CODE_PROMPT_*.md` handoff once SKILL.md is drafted.
- **Pipeline reshape (M0.5.6).** `01-crop.py` archival + `02-trace.py` repointing + Makefile update. Code task. Needs a `CODE_PROMPT_*.md` handoff. Don't run `make pieces` until this lands — it'll fail under the new layout.

## Next-session handoff

Zarathale's next move at the keyboard: keep capturing chunks per `SCAN-INTAKE-CHECKLIST.md`, work through the per-piece crops, and surface anomalies as you go. The next Cowork session is a natural fit for drafting `SKILL.md` + the `CODE_PROMPT_*.md` for the ingest skill and the pipeline reshape. Either can be drafted in any order; the pipeline reshape is a smaller change and lower-risk to ship first.

The `interruptedsession001.rtf` scratch file in `sessions/` was the cutoff transcript that seeded this resumption. Once this note is committed, the RTF is redundant and can be deleted.
