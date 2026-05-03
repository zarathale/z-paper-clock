---
status: shipped
started: 2026-05-03
shipped: 2026-05-03
owner: Zarathale (Alan)
target: tag-pieces-v2-schema
---

_Shipped 2026-05-03; paths and concepts in this document reflect the state at ship time. Refer to CLAUDE.md / ROADMAP.md for current state._

# Update tag-pieces.html for the v2 character + subtype schema

## What You Are Doing and Why

`tag-pieces.html` was shipped on 2026-05-03 with a 10-archetype taxonomy (`flat-laminate`, `flat-decorative`, `folded-tube`, `folded-box`, `frame-channel`, `gear-disc`, `pinion-stack-disc`, `gear-teeth-strip`, `anchor-pendulum-mixed`, `reference`). After tagging all 122 captured pieces, Zarathale and Cowork pivoted to a v2 schema: 7 layer-signature-driven `character` values (the 2×2 of axle? × cutout? for flat, plus folded / folded-axle / reference) plus a free-form `subtype` field, plus an optional `controls` block for UI-bound parameters. The v2 schema is settled and lives in `work/piece_characters_v2.yaml` (the canonical state).

This Code session updates `tag-pieces.html` to use the v2 schema natively: 7 buttons mapped to keys 1–7 instead of 10 mapped to 1–0, a subtype text input with autocomplete from the known v2 vocabulary, an import path for `piece_characters_v2.yaml` so Alan keeps the work already done, and an export format that matches v2 exactly. The result: Alan can re-open the tool, see his v2 state, audit/refine character + subtype assignments, and re-export without leaving the tagging surface.

## Prerequisites — confirm before starting

- `/Users/mainstage/Documents/GitHub/z-paper-clock/tag-pieces.html` exists.
- `/Users/mainstage/Documents/GitHub/z-paper-clock/work/piece_characters_v2.yaml` exists and is current.
- `/Users/mainstage/Documents/GitHub/z-paper-clock/work/pieces.csv` exists with 123 rows (1–121 contiguous + 092a + 112a).
- Git working tree clean, on `main`.
- Branch name will be `claude/tag-pieces-v2-schema` (descriptive slug, NOT an auto-generated `claude/<adjective>-<name>-<hash>` — see CLAUDE.md "Code branch / commit / PR rules").

## Read These Files First

1. `CLAUDE.md` — the "File Naming Conventions" and "Architectural Decisions" sections, plus "Code branch / commit / PR rules".
2. `work/piece_characters_v2.yaml` — entire file. The schema header (CHARACTER, SUBTYPE, CONTROLS, STATUS, CLARIFICATIONS sections) is the canonical reference for what the tool must support. The character + subtype assignments for all 122 pieces are the migration source for `INITIAL_STATE` (see Task 3).
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
// 7 characters mapped to keys 1-7. Each character corresponds to a unique
// layer signature; see work/piece_characters_v2.yaml header for definitions.
const CHARACTERS = [
  { slug: "flat",             key: "1", desc: "flat: silhouette + (glue) + labels + marks" },
  { slug: "flat-cutout",      key: "2", desc: "flat with interior hole(s); no folds, no axles" },
  { slug: "flat-axle",        key: "3", desc: "flat with axle (pin/wire pass-through); no cutouts" },
  { slug: "flat-axle-cutout", key: "4", desc: "flat with axle AND interior cutout (pinion stacks, hands wheels)" },
  { slug: "folded",           key: "5", desc: "folded form (rails, brackets, tubes, boxes, teeth strips); no axles" },
  { slug: "folded-axle",      key: "6", desc: "folded form bearing an axle (frame columns, anchor-bearing box)" },
  { slug: "reference",        key: "7", desc: "non-build reference (dimension legends, etc.)" },
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

**Implementation notes for the migration:**

- **Multi-line note collapse for INITIAL_STATE.** The source YAML uses block-scalar (`|`) for multi-line notes — these come in as several lines, each indented by 6 spaces. Flatten each multi-line note to a single-line JS string by: (a) replacing each newline with a single space, (b) collapsing runs of whitespace to one space, (c) trimming leading/trailing whitespace. The intent is a clean one-line string suitable for the localStorage round-trip. (The on-export round-trip restores multi-line block-scalar form — see Task 8.)
- **`v1_was` field.** Preserve verbatim. If the YAML has `v1_was: null`, the embedded JS value is the literal `null` (not the string `"null"`). If the YAML has no `v1_was` field, embed `null`.
- **`status` field.** Preserve when present (`pair-tag`, `pending`, `uncertain`). When the YAML has no explicit status field, embed `status: "tagged"` — the v2 YAML treats absence as the tagged default.
- **`controls` block.** The YAML's `controls:` is a list of objects. Embed as a JS array of objects, one object per list item, with keys verbatim from the YAML. Today only piece `100` has a controls block, with one item:

  ```javascript
  "100": {
    character: "flat-axle",
    subtype: "indicator-bob",
    status: "tagged",
    note: "Pair-tag resolved 2026-05-03. ...",   // collapsed per the rule above
    v1_was: "anchor-pendulum-mixed",
    controls: [
      {
        parameter: "bob-position",
        type: "scalar",
        semantics: "Sliding adjustment along pendulum rod (70). +1 = bob raised (faster period); -1 = bob lowered (slower period). Final viewer (M3+) exposes a master control linked to this disc; nudge fast/slow increments the parameter.",
        ui_hint: "Slider with F (up/fast) / S (down/slow) labels matching the printed arrows on 100.",
      },
    ],
  },
  ```

  See Task 7 for how the tool surfaces the controls block.

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

Change the legend grid from 10 columns to 7:

```css
.legend {
  display: grid; grid-template-columns: repeat(7, 1fr);
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

Update `tagCurrent()` (lines 547–559) to spread `prev` so every v2 field (subtype, v1_was, controls) rides along automatically:

```javascript
function tagCurrent(character, status) {
  const p = currentPiece();
  if (!p) return;
  const prev = entry(p.id);
  state[p.id] = { ...prev, character, status };
  saveState();
  advanceAfterMutation(p.id);
  toast(`${p.id} → ${character} (${status})`);
}
```

**While you're here, fix the same silent-data-loss footgun in the other four mutators.** v1's `markUncertain` (line 574), `skipCurrent` (line 589), `clearCurrent` (line 599), and the debounced `perPieceNote` save (line 648) all rebuild entries with explicit fields (`{ character, status, note }`) and would silently strip `subtype`, `v1_was`, and `controls` after v2. Switch each to spread:

```javascript
function markUncertain() {
  const p = currentPiece();
  if (!p) return;
  const prev = entry(p.id);
  if (!prev.character) {
    // No character yet; mark uncertain anyway so it shows up as "needs second pass".
    state[p.id] = { ...prev, status: "uncertain" };
  } else {
    state[p.id] = { ...prev, status: prev.status === "uncertain" ? "tagged" : "uncertain" };
  }
  saveState();
  render();
  toast(`${p.id} marked ${state[p.id].status}`);
}

function skipCurrent() {
  const p = currentPiece();
  if (!p) return;
  const prev = entry(p.id);
  state[p.id] = { ...prev, character: null, status: "skipped" };
  saveState();
  advanceAfterMutation(p.id);
  toast(`${p.id} skipped`);
}

function clearCurrent() {
  const p = currentPiece();
  if (!p) return;
  const prev = entry(p.id);
  state[p.id] = { ...prev, character: null, status: "pristine" };
  saveState();
  render();
  toast(`${p.id} cleared`);
}
```

And the `perPieceNote` debounce (line 648):

```javascript
let noteSaveTimer = null;
document.getElementById("perPieceNote").addEventListener("input", e => {
  const p = currentPiece();
  if (!p) return;
  clearTimeout(noteSaveTimer);
  const value = e.target.value;
  noteSaveTimer = setTimeout(() => {
    const prev = entry(p.id);
    state[p.id] = { ...prev, note: value };
    saveState();
  }, 250);
});
```

(v1's `status: prev.status === "pristine" && value ? "pristine" : prev.status` clause is dropped — typing into the note never changes status in v2; tagging is the only way to leave pristine. The clause was a no-op anyway, but it's clearer to remove it.)

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

**Field ordering (canonical, must match v2 YAML for clean diff).** For each entry, emit fields in this order:

1. `character`
2. `subtype` (only if non-null)
3. `v1_was` (always emit; render `null` when empty)
4. `status` (only if non-`tagged`)
5. `controls` (only if present)
6. `note` (only if non-empty)

This matches the canonical order in `work/piece_characters_v2.yaml` (see e.g. piece 100 = character / subtype / v1_was / controls / note; piece 110 = character / subtype / v1_was / status / note).

**Block-scalar emission for multi-line notes.** When `e.note` contains a newline, render as a YAML block scalar with 6-space indented body lines (matches the v2 YAML's indentation for fields nested under `  "ID":`, which itself sits at 2 spaces, with sub-fields at 4 and block-scalar bodies at 6). Sketch:

```javascript
function emitNote(noteString) {
  if (!noteString) return [];
  if (noteString.includes("\n")) {
    return ["    note: |", ...noteString.split("\n").map(ln => `      ${ln}`)];
  }
  return [`    note: ${JSON.stringify(noteString)}`];
}
```

Single-line notes use `JSON.stringify` (which produces a valid YAML double-quoted string for any plain string).

**Controls emission.** When `e.controls` is a non-empty array, render as a YAML list, one item per object, with each key indented 8 spaces under the `      - ` of the first key. Sketch:

```javascript
function emitControls(controls) {
  if (!controls || controls.length === 0) return [];
  const out = ["    controls:"];
  for (const item of controls) {
    const keys = Object.keys(item);
    keys.forEach((k, i) => {
      const prefix = i === 0 ? "      - " : "        ";
      const value = typeof item[k] === "string" && (item[k].includes(":") || item[k].includes("\""))
        ? JSON.stringify(item[k])
        : item[k];
      out.push(`${prefix}${k}: ${value}`);
    });
  }
  return out;
}
```

This preserves the v2 YAML's `      - parameter: bob-position` / `        type: scalar` shape for piece 100. Strings that contain colons or double-quotes get JSON-stringified for safety.

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

Targeted YAML parser — does NOT need a general YAML library. The format is well-constrained. **Note on ordering**: the controls-block check sits BEFORE the inline-field check, with an explicit fall-through when a line is recognised as not-a-controls-list-item (e.g. the `note: |` that follows a controls block on piece 100). Without that fall-through the post-controls field is consumed but never recorded — Bug found during QA.

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
    if (currentControlItem) controlsItems.push(currentControlItem);
    if (currentId && controlsItems.length > 0) {
      result[currentId].controls = controlsItems;
    }
    inControlsBlock = false;
    controlsItems = [];
    currentControlItem = null;
  };

  for (const raw of lines) {
    const trimmed = raw.replace(/\s+$/, "");

    // 1. ID line: "001": at column 2 — always wins.
    const idMatch = trimmed.match(/^  "([^"]+)":\s*$/);
    if (idMatch) {
      flushBlockScalar();
      flushControls();
      currentId = idMatch[1];
      result[currentId] = { character: null, subtype: null, status: "tagged", note: "", v1_was: null };
      continue;
    }

    // 2. Block-scalar continuation (only active between `note: |` and the next non-indented line).
    if (currentField && currentBlockLines !== null) {
      if (trimmed.startsWith("      ") || trimmed === "") {
        currentBlockLines.push(trimmed.replace(/^      /, ""));
        continue;
      }
      flushBlockScalar();
      // fall through — current line still needs to be matched against controls / fieldMatch
    }

    // 3. Controls block — consume list items, fall out (without `continue`) on a non-matching line.
    if (inControlsBlock) {
      const itemStart = trimmed.match(/^      - (\w+):\s*(.*)$/);
      const itemContinue = trimmed.match(/^        (\w+):\s*(.*)$/);
      if (itemStart) {
        if (currentControlItem) controlsItems.push(currentControlItem);
        currentControlItem = {};
        let value = itemStart[2];
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        currentControlItem[itemStart[1]] = value;
        continue;
      }
      if (itemContinue && currentControlItem) {
        let value = itemContinue[2];
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        currentControlItem[itemContinue[1]] = value;
        continue;
      }
      // Falling out — flush, then fall through (NO continue) so the current line is
      // re-evaluated by the fieldMatch logic below. This is the Bug-B fix: without
      // the fall-through, a `note: |` immediately after a controls block is lost.
      flushControls();
    }

    // 4. Inline field: "    character: folded" or "    note: |" or "    controls:"
    const fieldMatch = trimmed.match(/^    (\w+):\s*(.*)$/);
    if (fieldMatch) {
      const [, key, rawValue] = fieldMatch;
      if (rawValue === "|") {
        currentField = key;
        currentBlockLines = [];
      } else if (rawValue === "") {
        if (key === "controls") {
          inControlsBlock = true;
          controlsItems = [];
          currentControlItem = null;
        }
      } else {
        let value = rawValue;
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        if (value === "null") value = null;
        result[currentId][key] = value;
      }
      continue;
    }
  }
  flushBlockScalar();
  flushControls();

  return result;
}
```

**Test the parser against the canonical YAML before declaring done.** Specifically: import `work/piece_characters_v2.yaml`, then export, then diff the export against the source. Modulo header comments and field-ordering details, every piece's character / subtype / v1_was / status / controls / note should round-trip cleanly. Piece 100 (the only one with a controls block today) is the highest-value smoke test because it stresses the controls-block fall-out path; piece 067 is a good multi-line-note round-trip test.

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

Add filters for pair-tag and pending. Without the pending filter, pieces with `status: "pending"` (013, 014, 016, 017, 090, 110 today) fall through every filter except "all" — they're not pristine, not tagged, not skipped:

```html
<label><input type="radio" name="filter" value="pair-tag"> Pair-tag only <span class="count" id="cntPairTag">—</span></label>
<label><input type="radio" name="filter" value="pending"> Pending capture <span class="count" id="cntPending">—</span></label>
```

Update `applyFilter()` (lines 425–439) to handle the new values:

```javascript
case "pair-tag": return e.status === "pair-tag";
case "pending":  return e.status === "pending";
```

Update the count displays in `renderProgress()`:

```javascript
document.getElementById("cntPairTag").textContent = counts["pair-tag"];
document.getElementById("cntPending").textContent = counts.pending;
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
Upgrade tag-pieces.html from v1 (10 archetypes) to v2 (7 characters + subtype + optional controls), import the canonical state from `work/piece_characters_v2.yaml`, and ship a re-export path that matches v2 format exactly.

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
2. **7 buttons render in the legend, keys 1–7 work.** Mouse-click and keyboard each map to the correct character. Keys 8, 9, and 0 have no effect.
3. **Subtype input persists.** Type a subtype, navigate to next piece, navigate back; the subtype is preserved.
4. **Subtype autocomplete works.** Click in the subtype input; the datalist suggestions appear as you type (browser behavior).
5. **Pair-tag flag toggles.** Press `p` on any piece; status changes to `pair-tag`. Press `p` again; reverts to `tagged`. Filter by Pair-tag only — exactly the tagged-as-pair-tag pieces appear.
6. **Controls block displays for piece 100.** Navigate to piece 100; the "Controls: bob-position (scalar)" badge appears. Navigate to any other piece; badge disappears.
7. **Non-tag mutators preserve v2 fields.** On piece 100 (which has subtype, v1_was, AND controls): press `u` (uncertain), then `u` again (back to tagged), then type a single character into the note box, then delete it. After all that, piece 100's subtype is still `indicator-bob`, v1_was is still `anchor-pendulum-mixed`, and the controls badge is still showing. Repeat with piece 001 (subtype + v1_was, no controls): same fields preserved through `u`/`s`/`x` cycles. This is the Bug-A regression test — without the spread fix, any of those keys silently strips the v2 fields.
8. **Export YAML matches v2 schema in field order.** Export and diff against `work/piece_characters_v2.yaml`. Comments will differ (the tool's auto-generated header is briefer); piece entries should match in field order (character → subtype → v1_was → [status] → [controls] → [note]). `v1_was`, `subtype`, `controls` fields should round-trip.
9. **Round-trip via Import → Export.** Paste `work/piece_characters_v2.yaml` into the import box, click Load, confirm the prompt. Then click Export YAML. Diff the export against the original — should be functionally identical (same fields per piece, same ordering, same values; only header comment differs). This is the Bug-B regression test — piece 100's `note: |` comes after its `controls:` block in the source, and the v1 parser dropped it on import.
10. **Pending filter chip works.** With "Pending capture" selected, only the 6 pending-capture pieces (013, 014, 016, 017, 090, 110) appear; count badge reads 6.
11. **No console errors** during init or any of the above flows.
12. **Existing flows still work.** Skip (`s`), uncertain (`u`), clear (`x`), jump (`j`), prev/next arrows, section filter, untagged filter — all behave as before.
13. **`gh pr create`** runs cleanly. The PR title is `update tag-pieces.html for v2 character + subtype schema`.

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
| Open `tag-pieces.html` in your browser (file://) | Initial state shows 122 tagged from v2 YAML. (`<datalist>` autocomplete UI varies between browsers; the data is the same.) |
| Click character button "flat-axle-cutout" on piece 058 (currently `flat-axle`) | Character changes; subtype preserved (`escape-wheel`); `v1 was` annotation shows `gear-disc`. |
| Press `p` on piece 027 | Status flips to `pair-tag`. |
| Edit subtype on piece 042 to `tube-pulley-drum-with-north-cue` | Subtype persists across navigation. |
| Navigate to piece 100; press `u` then `u` again; then type and delete a character in the note box | Subtype (`indicator-bob`), v1_was (`anchor-pendulum-mixed`), AND the controls badge still showing — none of those keystrokes silently stripped v2 fields. |
| Click Export YAML | Output diffs cleanly against `work/piece_characters_v2.yaml` (modulo header comments). Field order matches: character → subtype → v1_was → [status] → [controls] → [note]. |
| Click Import YAML, paste fresh `piece_characters_v2.yaml`, Load | State resets to canonical v2; all per-session edits cleared. Piece 100's note (which follows its controls block in the source) round-trips intact. |
| Press `s` on piece 041 | Status flips to skipped. |
| Reload page | All state preserved (localStorage). |
