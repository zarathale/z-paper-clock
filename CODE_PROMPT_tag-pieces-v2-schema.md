---
status: ready-for-code
started: 2026-05-03
owner: Zarathale (Alan)
target: tag-pieces-v2-schema
---

# Update tag-pieces.html for the v2 character + subtype schema

## What You Are Doing and Why

`tag-pieces.html` was shipped on 2026-05-03 with a 10-archetype taxonomy (`flat-laminate`, `flat-decorative`, `folded-tube`, `folded-box`, `frame-channel`, `gear-disc`, `pinion-stack-disc`, `gear-teeth-strip`, `anchor-pendulum-mixed`, `reference`). After tagging all 122 captured pieces, Zarathale and Cowork pivoted to a v2 schema: 8 layer-signature-driven `character` values plus a free-form `subtype` field, plus an optional `controls` block for UI-bound parameters. The v2 schema is settled and lives in `work/piece_characters_v2.yaml` (the canonical state).

This Code session updates `tag-pieces.html` to use the v2 schema natively: 8 buttons mapped to keys 1–8 instead of 10 mapped to 1–0, a subtype text input with autocomplete from the known v2 vocabulary, an import path for `piece_characters_v2.yaml` so Alan keeps the work already done, and an export format that matches v2 exactly. The result: Alan can re-open the tool, see his v2 state, audit/refine character + subtype assignments, and re-export without leaving the tagging surface.

## Prerequisites — confirm before starting

- `/Users/mainstage/Documents/GitHub/z-paper-clock/tag-pieces.html` exists.
- `/Users/mainstage/Documents/GitHub/z-paper-clock/work/piece_characters_v2.yaml` exists and is current.
- `/Users/mainstage/Documents/GitHub/z-paper-clock/work/pieces.csv` exists with 123 rows (1–121 contiguous + 092a + 112a).
- Git working tree clean, on `main`.
- Branch name will be `claude/tag-pieces-v2-schema` (descriptive slug, NOT an auto-generated `claude/<adjective>-<name>-<hash>` — see CLAUDE.md "Code branch / commit / PR rules").

## Read These Files First

1. `CLAUDE.md` — the "File Naming Conventions" and "Architectural Decisions" sections, plus "Code branch / commit / PR rules".
2. `work/piece_characters_v2.yaml` — entire file. The schema header (CHARACTER, SUBTYPE, CONTROLS, STATUS, CLARIFICATIONS sections) is the canonical reference for what the tool must support. The character + subtype assignments for all 122 pieces are the migration source for `INITIAL_STATE` (see Task 4).
3. `tag-pieces.html` — entire file. Tasks below reference specific lines as they appear in the current file (HEAD as of 2026-05-03).
4. The most recent session note in `sessions/` — for the walkthrough context that finalized the v2 schema.

## Target File Structure Changes

```
z-paper-clock/
├── tag-pieces.html                     ← update: full v2 schema rewrite
└── sessions/
    └── 2026-05-03-HHMM_code_tag-pieces-v2-schema.md   ← NEW
```

No other files change. The v2 YAML in `work/piece_characters_v2.yaml` is the read-only migration source; the tool does not modify it.

## Numbered Tasks

### Task 1 — Replace ARCHETYPES with CHARACTERS + SUBTYPE_VOCABULARY

**File:** `tag-pieces.html`, lines 254–268.

Remove the `ARCHETYPES` constant. Replace with:

```javascript
// ─── Character taxonomy (v2) ────────────────────────────────────────────────
// 8 characters mapped to keys 1-8. Each character corresponds to a unique
// layer signature; see work/piece_characters_v2.yaml header for definitions.
const CHARACTERS = [
  { slug: "flat",             key: "1", desc: "flat: silhouette + (glue) + labels + marks" },
  { slug: "flat-cutout",      key: "2", desc: "flat with interior hole(s); no folds, no axles" },
  { slug: "flat-axle",        key: "3", desc: "flat with axle (pin/wire pass-through); no cutouts" },
  { slug: "flat-axle-cutout", key: "4", desc: "flat with axle AND interior cutout (pinion stacks, hands wheels)" },
  { slug: "folded",           key: "5", desc: "folded form (rails, brackets, tubes, boxes, teeth strips); no axles" },
  { slug: "folded-axle",      key: "6", desc: "folded form bearing an axle (frame columns, anchor-bearing box)" },
  { slug: "reference",        key: "7", desc: "non-build reference (dimension legends, etc.)" },
  // Key 8 reserved for an 8th character if one surfaces; document NULL
  // assignment here. For now, key 8 has no character; mark unused in legend.
];
const KEY_TO_CHARACTER = Object.fromEntries(CHARACTERS.map(c => [c.key, c.slug]));

// Subtype vocabulary — autocomplete suggestions, not strict validation.
// Sourced from work/piece_characters_v2.yaml header. Free-form override
// allowed via the subtype text input.
const SUBTYPE_VOCABULARY = [
  // Frame
  "frame-rail", "frame-rail-axle", "frame-rail-face",
  // Brackets
  "bracket-tab", "bracket-l", "bracket-wall",
  // Boxes
  "box-cross", "box-small", "box-wall-bracket", "box-anchor-bearing", "box-case-top",
  "triangle-spacer-motor",
  // Tubes
  "tube-pulley", "tube-pulley-drum", "tube-pulley-string-wind",
  "tube-pendulum-blade", "tube-bob-casing", "tube-weight-cylinder",
  "tube-weight-label-wrap", "tube-minute-hand-holder", "tube-strap",
  "tube-wheel-cover", "tube-rolled-pinion",
  // Teeth strips
  "teeth-strip-motor", "teeth-strip-reduction", "teeth-strip-hook",
  "teeth-strip-accordion-pulley", "teeth-strip-sawtooth-weight",
  // Discs
  "gear-face", "gear-back", "motor-wheel-face", "motor-wheel-back",
  "escape-wheel", "escape-wheel-back", "middle-wheel", "middle-wheel-back",
  "reduction-gear", "pulley-disc", "pulley-plate", "pulley-plate-back",
  "plate-cap", "lid-weight", "hands-wheel-hour", "hands-wheel-hour-back",
  "hands-wheel-star", "spacer-disc", "indicator-bob",
  // Pinion mounts
  "pinion-mount-middle", "pinion-mount-escape", "pinion-mount-motor",
  "pinion-mount-hands",
  // Anchor / pendulum
  "anchor-arm", "anchor-fork", "plate-anchor-rear", "blade-pendulum",
  "ring-square-pendulum", "pendulum-rod", "hook-pendulum",
  // Bob
  "bob-face", "bob-retainer", "bob-brace", "reinforcement-cardboard",
  "crescent-decorative",
  // Frame braces / spacers
  "face-brace-cross", "face-brace-cross-axle", "face-brace-cross-hole",
  "spacer-pendulum-support", "wedge-wall-bracket", "spacer-cardboard",
  // Hands
  "hand-minute", "hand-hour",
  // Case
  "case-side", "face-clock",
  // Misc
  "ring-tab-pulley", "tongue-oval", "oval-elongated", "tongue-narrow-hands",
  "push-tab-wheel", "axle-mount-square",
];
```

### Task 2 — Bump STORAGE_KEY and update entry shape

**File:** `tag-pieces.html`, lines 399–417.

Bump the storage key from `v1` to `v2` so old localStorage doesn't poison v2:

```javascript
const STORAGE_KEY = "z-paper-clock-tag-pieces-v2";
```

Update the entry shape comment + `entry()` default. New shape:

```javascript
// tag entry shape:
// { character: string|null, subtype: string|null,
//   status: "tagged"|"uncertain"|"skipped"|"pristine"|"pair-tag"|"pending",
//   note: string,
//   v1_was: string|null }   // audit trail; only set if this row was migrated
function entry(id) {
  return state[id] || {
    character: null, subtype: null, status: "pristine",
    note: "", v1_was: null,
  };
}
```

### Task 3 — Embed INITIAL_STATE from piece_characters_v2.yaml

**File:** `tag-pieces.html`, immediately after the `CHARACTERS` / `SUBTYPE_VOCABULARY` constants (Task 1).

Add a constant `INITIAL_STATE` containing one entry per piece tagged in `work/piece_characters_v2.yaml`. Read the YAML file at the absolute path above and translate every piece block to a JS object literal. Format:

```javascript
// Embedded snapshot of work/piece_characters_v2.yaml as of 2026-05-03.
// On first load (empty localStorage), state seeds from this. Subsequent
// edits are persisted to localStorage and override INITIAL_STATE on reload.
// Re-embed when piece_characters_v2.yaml changes.
const INITIAL_STATE = {
  "001": { character: "folded", subtype: "frame-rail", status: "tagged", note: "", v1_was: "frame-channel" },
  "002": { character: "folded", subtype: "frame-rail", status: "tagged", note: "", v1_was: "frame-channel" },
  // ... 120 more entries
  "041": { character: "flat", subtype: "tongue-oval", status: "pair-tag", note: "DEFERRED 2026-05-03 — Alan re-reading instructions to determine flat strip vs rolled cylinder. v1 export retagged folded-tube → flat-decorative; held as flat pending the re-read.", v1_was: "flat-decorative" },
  // ...
};
```

Implementation note: the source YAML uses block-scalar (`|`) for multi-line notes. Collapse those to single-line strings when embedding. Preserve the `v1_was` field; preserve `status` field where present (`pair-tag`, `pending`, `uncertain`); set `status: "tagged"` when no explicit status is given. For pieces with a `controls` block in YAML (only `100` currently), copy the block verbatim into the entry as a JS object — see Task 7 for how the tool surfaces it.

Update `loadState()` to seed from `INITIAL_STATE` on first run:

```javascript
function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return JSON.parse(JSON.stringify(INITIAL_STATE));  // deep copy
    const parsed = JSON.parse(raw);
    return (parsed && typeof parsed === "object") ? parsed : JSON.parse(JSON.stringify(INITIAL_STATE));
  } catch (e) { return JSON.parse(JSON.stringify(INITIAL_STATE)); }
}
```

### Task 4 — Add subtype input to the piece card

**File:** `tag-pieces.html`, around line 192 (between `currentTagLine` and the `perPieceNote` textarea).

Add a subtype input wired to a `<datalist>` for autocomplete:

```html
<div class="piece-subtype" id="subtypeRow">
  <label for="subtypeInput" style="font-size: 13px; color: var(--muted);">Subtype:</label>
  <input type="text" id="subtypeInput" list="subtypeList"
         placeholder="e.g. frame-rail, bracket-tab, tube-pulley"
         style="width: 60%; padding: 5px 8px; font: inherit;
                border: 1px solid var(--line); border-radius: 4px; margin-left: 6px;">
  <datalist id="subtypeList"></datalist>
</div>
```

Populate the `<datalist>` from `SUBTYPE_VOCABULARY` on init:

```javascript
function populateSubtypeList() {
  const list = document.getElementById("subtypeList");
  SUBTYPE_VOCABULARY.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s;
    list.appendChild(opt);
  });
}
```

Wire up save-on-input (debounced, like `perPieceNote`):

```javascript
let subtypeSaveTimer = null;
document.getElementById("subtypeInput").addEventListener("input", e => {
  const p = currentPiece();
  if (!p) return;
  clearTimeout(subtypeSaveTimer);
  const value = e.target.value.trim();
  subtypeSaveTimer = setTimeout(() => {
    const prev = entry(p.id);
    state[p.id] = { ...prev, subtype: value || null };
    saveState();
  }, 250);
});
```

In `renderCard()` (around line 511), after the `perPieceNote` set, also set:

```javascript
document.getElementById("subtypeInput").value = e.subtype || "";
```

Style minor — the row should sit between `currentTagLine` and `perPieceNote` and not break the layout.

### Task 5 — Add a "pair-tag" toggle

**File:** `tag-pieces.html`, lines 194–201 (`nav-row` div).

Add a button next to "Uncertain" called "Pair-tag", keyboard `p`. Toggles the status between the current tag's status and `pair-tag`. Distinct from `uncertain`: pair-tag means "the call was made but Cowork should review"; uncertain means "I couldn't decide".

```html
<button class="nav-btn" id="pairTagBtn">Pair-tag <span class="key">p</span></button>
```

Action handler:

```javascript
function markPairTag() {
  const p = currentPiece();
  if (!p) return;
  const prev = entry(p.id);
  const newStatus = prev.status === "pair-tag" ? "tagged" : "pair-tag";
  state[p.id] = { ...prev, status: newStatus };
  saveState();
  render();
  toast(`${p.id} marked ${newStatus}`);
}
```

Wire it up alongside the other action buttons (lines 665–670) and to the `p` keyboard handler (lines 698–706).

Add a CSS rule for `.piece-status.pair-tag` matching the existing color pattern (e.g. background `#dde6f1`, color `#365683`).

### Task 6 — Update the legend rendering and keyboard shortcut count

**File:** `tag-pieces.html`, lines 36–40 (`.legend` grid CSS) and lines 446–458 (`renderLegend()`).

Change the legend grid from 10 columns to 8:

```css
.legend {
  display: grid; grid-template-columns: repeat(8, 1fr);
  gap: 6px; padding: 10px 20px; background: #fff;
  border-bottom: 1px solid var(--line);
}
```

Update `renderLegend()` to iterate `CHARACTERS` instead of `ARCHETYPES`:

```javascript
function renderLegend() {
  const legend = document.getElementById("legend");
  legend.innerHTML = "";
  CHARACTERS.forEach(c => {
    const btn = document.createElement("button");
    btn.className = "arch-btn";
    btn.dataset.slug = c.slug;
    btn.title = c.desc;
    btn.innerHTML = `<span class="key">${c.key}</span><span class="name">${c.slug}</span>`;
    btn.addEventListener("click", () => tagCurrent(c.slug, "tagged"));
    legend.appendChild(btn);
  });
}
```

Update `tagCurrent()` (lines 547–559) to preserve the existing subtype on tag changes:

```javascript
function tagCurrent(character, status) {
  const p = currentPiece();
  if (!p) return;
  const prev = entry(p.id);
  state[p.id] = {
    character: character,
    subtype: prev.subtype || null,
    status: status,
    note: prev.note || "",
    v1_was: prev.v1_was || null,
  };
  saveState();
  advanceAfterMutation(p.id);
  toast(`${p.id} → ${character} (${status})`);
}
```

Update the keyboard handler (lines 686–707) to use `KEY_TO_CHARACTER`:

```javascript
if (KEY_TO_CHARACTER[e.key]) {
  e.preventDefault();
  tagCurrent(KEY_TO_CHARACTER[e.key], "tagged");
  return;
}
```

Add the `p` key:

```javascript
case "p": case "P": e.preventDefault(); markPairTag(); break;
```

Update the keys help panel (lines 224–234):

```html
<div class="help">
  <kbd>1</kbd>–<kbd>7</kbd> tag with character<br>
  <kbd>u</kbd> mark uncertain<br>
  <kbd>p</kbd> mark pair-tag<br>
  <kbd>s</kbd> skip<br>
  <kbd>x</kbd> clear current tag<br>
  <kbd>n</kbd> focus note box<br>
  <kbd>j</kbd> jump to ID<br>
  <kbd>←</kbd> <kbd>→</kbd> prev / next<br>
  <em>Auto-saves to localStorage on every action.</em>
</div>
```

### Task 7 — Surface controls block (read-only, forward-looking)

**File:** `tag-pieces.html`, in `renderCard()` around line 510.

Only one piece (100) currently has a controls block. The tool should DISPLAY it as a read-only badge if present, but not expose authoring UI for it (controls authoring is M6 work). Add markup near the subtype row:

```html
<div class="piece-controls" id="controlsBadge" style="display: none; font-size: 12px; color: var(--accent); margin-top: 4px;">
  <strong>Controls:</strong> <span id="controlsList"></span>
</div>
```

In `renderCard()`:

```javascript
const controlsBadge = document.getElementById("controlsBadge");
if (e.controls && e.controls.length > 0) {
  controlsBadge.style.display = "block";
  document.getElementById("controlsList").textContent =
    e.controls.map(c => `${c.parameter} (${c.type})`).join(", ");
} else {
  controlsBadge.style.display = "none";
}
```

The controls block is preserved through tag/subtype/status edits — `tagCurrent()` and friends should spread `prev` (which already does), so this works automatically.

### Task 8 — Update Export YAML

**File:** `tag-pieces.html`, lines 710–747 (`buildExportYaml()`).

Rewrite to emit the v2 schema. The output should match `work/piece_characters_v2.yaml` row-for-row in shape (not necessarily comments — the tool's export is a snapshot, not a hand-curated reference). For each non-pristine entry:

```yaml
  "001":
    character: folded
    subtype: frame-rail
    v1_was: frame-channel
```

Status, note, and controls fields render only when present. Multi-line notes render as YAML block scalars (`note: |`) when they contain newlines; otherwise as JSON-string-quoted single-line.

Update the file header comment block:

```
# work/piece_characters.yaml
# Generated by tag-pieces.html on <ISO timestamp>.
# Schema v2 — characters + subtypes; see work/piece_characters_v2.yaml header.
# 'pair-tag' pieces flagged for joint Cowork review.
# 'uncertain' pieces flagged for second pass.
# 'skipped' deliberately not tagged.
```

Update the counts line:

```
# tagged: <n> · pair-tag: <n> · uncertain: <n> · skipped: <n> · pristine: <n>
# character distribution: flat=<n>, flat-cutout=<n>, flat-axle=<n>, ...
```

Default download filename: keep `piece_characters.yaml` (so it overwrites cleanly when Alan saves to `work/`).

### Task 9 — Add Import YAML modal

**File:** `tag-pieces.html`, near the existing export modal (lines 240–249).

Add an "Import YAML" button to the Output panel (lines 218–222) and a modal that lets Alan paste a YAML payload, parse it, and replace localStorage state.

```html
<button id="importBtn">Import YAML…</button>
```

Modal HTML:

```html
<section class="export-modal" id="importModal">
  <h2>Import · piece_characters.yaml</h2>
  <p style="color: var(--muted); font-size: 13px;">
    Paste the contents of <code>work/piece_characters_v2.yaml</code> (or any v2-format export) below.
    Loading replaces all current tags. Export first if you want a backup.
  </p>
  <textarea id="importText" placeholder="characters:&#10;  &quot;001&quot;:&#10;    character: folded&#10;    subtype: frame-rail&#10;..."></textarea>
  <div class="actions">
    <button class="nav-btn primary" id="loadImportBtn">Load</button>
    <button class="nav-btn" id="closeImportBtn">Close</button>
  </div>
</section>
```

Targeted YAML parser — does NOT need a general YAML library. The format is well-constrained:

```javascript
function parseV2Yaml(yamlText) {
  // Targeted parser for piece_characters_v2.yaml format.
  // Recognized fields: character, subtype, status, note, v1_was, controls.
  // Multi-line block scalars (note: |) supported. Inline strings supported.
  const result = {};
  const lines = yamlText.split("\n");
  let currentId = null;
  let currentField = null;
  let currentBlockLines = null;
  let inControlsBlock = false;
  let controlsItems = [];
  let currentControlItem = null;

  const flushBlockScalar = () => {
    if (currentId && currentField && currentBlockLines !== null) {
      result[currentId][currentField] = currentBlockLines.join("\n").trim();
    }
    currentField = null;
    currentBlockLines = null;
  };

  const flushControls = () => {
    if (currentId && controlsItems.length > 0) {
      result[currentId].controls = controlsItems;
    }
    inControlsBlock = false;
    controlsItems = [];
    currentControlItem = null;
  };

  for (const raw of lines) {
    const trimmed = raw.replace(/\s+$/, "");

    // ID line: "001": at column 2
    const idMatch = trimmed.match(/^  "([^"]+)":\s*$/);
    if (idMatch) {
      flushBlockScalar();
      flushControls();
      currentId = idMatch[1];
      result[currentId] = { character: null, subtype: null, status: "tagged", note: "", v1_was: null };
      continue;
    }

    // Continuing block scalar: indented further than the field key
    if (currentField && currentBlockLines !== null) {
      if (trimmed.startsWith("      ") || trimmed === "") {
        currentBlockLines.push(trimmed.replace(/^      /, ""));
        continue;
      }
      flushBlockScalar();
    }

    // Inline field: "    character: folded"
    const fieldMatch = trimmed.match(/^    (\w+):\s*(.*)$/);
    if (fieldMatch && !inControlsBlock) {
      const [, key, rawValue] = fieldMatch;
      if (rawValue === "|") {
        currentField = key;
        currentBlockLines = [];
      } else if (rawValue === "") {
        if (key === "controls") {
          inControlsBlock = true;
          controlsItems = [];
        }
      } else {
        let value = rawValue;
        // Strip quotes if present
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        if (value === "null") value = null;
        result[currentId][key] = value;
      }
      continue;
    }

    // Inside controls block — list item starts with "      - parameter: ..."
    if (inControlsBlock) {
      const itemStart = trimmed.match(/^      - (\w+):\s*(.*)$/);
      const itemContinue = trimmed.match(/^        (\w+):\s*(.*)$/);
      if (itemStart) {
        if (currentControlItem) controlsItems.push(currentControlItem);
        currentControlItem = {};
        let value = itemStart[2];
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        currentControlItem[itemStart[1]] = value;
      } else if (itemContinue && currentControlItem) {
        let value = itemContinue[2];
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        currentControlItem[itemContinue[1]] = value;
      } else if (trimmed.match(/^  "/) || trimmed.match(/^    \w+:/)) {
        // Falling out of controls block; reprocess the line on the next iteration
        if (currentControlItem) controlsItems.push(currentControlItem);
        flushControls();
      }
    }
  }
  flushBlockScalar();
  flushControls();

  return result;
}
```

Wire up the import flow:

```javascript
function openImport() {
  document.getElementById("importText").value = "";
  document.getElementById("importModal").classList.add("open");
  document.getElementById("modalBg").classList.add("open");
}
function closeImport() {
  document.getElementById("importModal").classList.remove("open");
  document.getElementById("modalBg").classList.remove("open");
}
document.getElementById("importBtn").addEventListener("click", openImport);
document.getElementById("closeImportBtn").addEventListener("click", closeImport);
document.getElementById("loadImportBtn").addEventListener("click", () => {
  const text = document.getElementById("importText").value;
  if (!text.trim()) { toast("nothing to import"); return; }
  try {
    const parsed = parseV2Yaml(text);
    const ids = Object.keys(parsed);
    if (ids.length === 0) { toast("no entries parsed"); return; }
    if (!confirm(`Import ${ids.length} entries? This replaces ALL current tags.`)) return;
    state = parsed;
    saveState();
    closeImport();
    render();
    toast(`imported ${ids.length} entries`);
  } catch (e) {
    toast("parse error: " + e.message);
  }
});
```

The existing modal-bg click (line 761) also closes the import modal — wire it up:

```javascript
document.getElementById("modalBg").addEventListener("click", () => {
  closeExport();
  closeImport();
});
```

### Task 10 — Update progress + filter UI

**File:** `tag-pieces.html`, lines 460–474 (`renderProgress()`) and 207–217 (filter list).

Add `pair-tag` and `pending` to the status counter:

```javascript
const counts = { tagged: 0, uncertain: 0, "pair-tag": 0, pending: 0, skipped: 0, pristine: 0 };
PIECES.forEach(p => {
  const s = entry(p.id).status;
  counts[s] = (counts[s] || 0) + 1;
});
document.getElementById("progress").innerHTML =
  `<strong>${counts.tagged}</strong>/${PIECES.length} tagged · ` +
  `<strong>${counts["pair-tag"]}</strong> pair-tag · ` +
  `<strong>${counts.uncertain}</strong> uncertain · ` +
  `<strong>${counts.pending}</strong> pending · ` +
  `<strong>${counts.skipped}</strong> skipped · ` +
  `<strong>${counts.pristine}</strong> pristine`;
```

Add a filter for pair-tag:

```html
<label><input type="radio" name="filter" value="pair-tag"> Pair-tag only <span class="count" id="cntPairTag">—</span></label>
```

Update `applyFilter()` (lines 425–439) to handle the new value:

```javascript
case "pair-tag": return e.status === "pair-tag";
```

Update the count display in `renderProgress()`:

```javascript
document.getElementById("cntPairTag").textContent = counts["pair-tag"];
```

### Task 11 — Show v1_was annotation on reclassified pieces

**File:** `tag-pieces.html`, in `renderCard()`.

Below the `currentTagLine` (line 192-ish), add a small read-only annotation when the piece has a `v1_was` field that differs from the current character:

```html
<div class="piece-v1-was" id="v1WasLine" style="display: none; font-size: 12px; color: var(--muted); font-style: italic;">
  v1 was: <span id="v1WasValue"></span> · reclassified to current
</div>
```

In `renderCard()`:

```javascript
const v1WasLine = document.getElementById("v1WasLine");
if (e.v1_was && e.v1_was !== e.character) {
  v1WasLine.style.display = "block";
  document.getElementById("v1WasValue").textContent = e.v1_was;
} else {
  v1WasLine.style.display = "none";
}
```

This gives Alan visual feedback on which pieces moved family during the v1→v2 migration.

### Task 12 — Init wiring + session note

**File:** `tag-pieces.html`, end of script block (after line 800-ish).

Make sure `populateSubtypeList()` is called on init alongside `fullRender()`:

```javascript
fullRender();
populateSubtypeList();
```

**File:** `sessions/2026-05-03-HHMM_code_tag-pieces-v2-schema.md` (NEW).

Standard session note per CLAUDE.md sessions convention:

```markdown
---
date: 2026-05-03
start_time: "HH:MM"
end_time: "HH:MM"
mode: code
participant: Zarathale (Alan)
target: tag-pieces-v2-schema
orchestration_prompt: CODE_PROMPT_tag-pieces-v2-schema.md
---

# tag-pieces.html v2 schema upgrade

## Goal
Upgrade tag-pieces.html from v1 (10 archetypes) to v2 (8 characters + subtype + optional controls), import the canonical state from `work/piece_characters_v2.yaml`, and ship a re-export path that matches v2 format exactly.

## What was done
- ... (Code fills in)

## Branch / commit
- branch: claude/tag-pieces-v2-schema
- commit(s): ... (Code fills in)

## Open questions
- ... (anything that surfaced)

## Next-session handoff
- Alan opens tag-pieces.html, confirms initial state matches v2 YAML, refines subtype assignments, exports back to work/piece_characters.yaml.
- After review, merge piece_characters_v2.yaml into pieces.csv as the `character` column (separate Cowork session).
```

## Verification Checklist

Run after Task 12 completes:

1. **Empty localStorage seeds from INITIAL_STATE.** Open the file with localStorage cleared. The first piece (001) should show `character: folded`, `subtype: frame-rail`, `v1 was: frame-channel`. The progress bar shows 122 tagged + non-pristine count matching v2 YAML.
2. **8 buttons render in the legend, keys 1–8 work.** Mouse-click and keyboard each map to the correct character. Key 9 and Key 0 have no effect.
3. **Subtype input persists.** Type a subtype, navigate to next piece, navigate back; the subtype is preserved.
4. **Subtype autocomplete works.** Click in the subtype input; the datalist suggestions appear as you type (browser behavior).
5. **Pair-tag flag toggles.** Press `p` on any piece; status changes to `pair-tag`. Press `p` again; reverts to `tagged`. Filter by Pair-tag only — exactly the tagged-as-pair-tag pieces appear.
6. **Controls block displays for piece 100.** Navigate to piece 100; the "Controls: bob-position (scalar)" badge appears. Navigate to any other piece; badge disappears.
7. **Export YAML matches v2 schema.** Export and diff against `work/piece_characters_v2.yaml`. Comments will differ (the tool's auto-generated header is briefer); piece entries should match exactly. `v1_was`, `subtype`, `controls` fields should round-trip.
8. **Import YAML works.** Paste `work/piece_characters_v2.yaml` into the import box, click Load, confirm the prompt. State reloads to match v2 YAML.
9. **No console errors** during init or any of the above flows.
10. **Existing flows still work.** Skip (`s`), uncertain (`u`), clear (`x`), jump (`j`), prev/next arrows, section filter, untagged filter — all behave as before.
11. **`gh pr create`** runs cleanly. The PR title is `update tag-pieces.html for v2 character + subtype schema`.

## What NOT to Change

- Do NOT modify `work/piece_characters_v2.yaml`. The tool reads from it (via the embedded INITIAL_STATE) but does not write back to it.
- Do NOT regenerate the `PIECES` array from `work/pieces.csv`. The current embedded list is canonical.
- Do NOT change the `source/pieces/${id}.png` image path or the placeholder behavior on `pending` status.
- Do NOT pull in a YAML library from CDN. The tool runs from `file://`; the targeted regex parser in Task 9 is the right shape.
- Do NOT introduce a build step (no bundler, no package.json). `tag-pieces.html` stays single-file, double-clickable.
- Do NOT auto-migrate v1 localStorage to v2 in code. The bumped STORAGE_KEY plus INITIAL_STATE seeding handles the migration cleanly.

## Manual tests (Alan, post-merge)

| What | Expected |
|---|---|
| Open `tag-pieces.html` in Safari (file://) | Initial state shows 122 tagged from v2 YAML. |
| Click character button "flat-axle-cutout" on piece 058 (currently `flat-axle`) | Character changes; subtype preserved (`escape-wheel`); `v1 was` annotation shows `gear-disc`. |
| Press `p` on piece 027 | Status flips to `pair-tag`. |
| Edit subtype on piece 042 to `tube-pulley-drum-with-north-cue` | Subtype persists across navigation. |
| Click Export YAML | Output diffs cleanly against `work/piece_characters_v2.yaml` (modulo header comments). |
| Click Import YAML, paste fresh `piece_characters_v2.yaml`, Load | State resets to canonical v2; all per-session edits cleared. |
| Press `s` on piece 041 | Status flips to skipped. |
| Reload page | All state preserved (localStorage). |
