#!/usr/bin/env python3
"""
build_assembly_graph.py — read panels-first SVGs in work/pieces/ and build the
cross-piece connection graph + report. Pre-work for the panels-aware preview.html
parser pathway (queued Code session).

Reads each <piece>/<piece>.svg under work/pieces/. Extracts:

  - Panel ids from <g id="panels">
  - Fold bindings from <g id="folds-valley"> + <g id="folds-mountain">
    (parsed as fold-<a>-<b> ids resolving to panel pairs)
  - Cross-piece connections from <g id="attach-points">
    (landing-<tab><piece>, attach-<letter><piece>, hole-<letter><piece>,
     pivot-<name>, with `back-` side annotation prefix support)
  - Same-piece markers from <g id="marks">
    (untyped landings, multi-instance markers, alignments, cuts)

Cross-references the cross-piece connections piece-by-piece:
  - For each landing-<tab><piece> on piece A, looks for tab<tab> on piece <piece>
  - For each attach-<letter><piece> on piece A, looks for <letter> on piece <piece>
  - For each pivot-<name> shared across multiple pieces, lists those pieces
  - Flags half-typed connections (one side has the annotation, partner doesn't)

Outputs:
  - claude-work/state/connection-graph.json — structured data
  - claude-work/state/connection-graph.md — human-readable report

Treats the SVG as text (regex). The XML is Affinity-exported and not always
strictly well-formed, so we don't use ElementTree. Layers are parsed by finding
<g id="..."> markers and walking forward with depth-balanced tag counts.

Run from repo root:
    python3 claude-work/scripts/build_assembly_graph.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# -- repo locations --------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PIECES_DIR = REPO_ROOT / "work" / "pieces"
OUT_JSON = REPO_ROOT / "claude-work" / "state" / "connection-graph.json"
OUT_MD = REPO_ROOT / "claude-work" / "state" / "connection-graph.md"

# -- canonical layer names per LAYERS.md (post-2026-05-05 panels-first) ----

LAYERS = ["silhouette", "cutouts", "panels", "folds-valley", "folds-mountain",
          "axles", "attach-points", "labels", "marks"]


# -- SVG parsing helpers (regex-based; Affinity exports are messy) ---------

def read_svg(svg_path: Path) -> str:
    return svg_path.read_text(encoding="utf-8", errors="replace")


def extract_layer_block(svg_text: str, layer_id: str) -> str | None:
    """Return the contents of <g id="LAYER">...</g>, or None if absent.

    Walks <g>...</g> with depth balance to handle nested groups.
    """
    m = re.search(r'<g[^>]*\bid="' + re.escape(layer_id) + r'"', svg_text)
    if not m:
        return None
    i = m.end()
    depth = 1
    while i < len(svg_text) and depth > 0:
        nxt_open = svg_text.find("<g", i)
        nxt_close = svg_text.find("</g>", i)
        if nxt_close == -1:
            break
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + 2
        else:
            depth -= 1
            i = nxt_close + 4
    return svg_text[m.start():i]


def all_ids_in_block(block: str) -> list[tuple[str, str]]:
    """Return [(tagname, id), ...] for id-bearing drawable elements inside block."""
    out = []
    for m in re.finditer(r'<(\w+)[^>]*?\bid="([^"]+)"', block):
        tag, eid = m.group(1), m.group(2)
        if tag in ("path", "rect", "ellipse", "circle", "line", "polyline", "polygon", "g"):
            out.append((tag, eid))
    return out


# -- sidecar parsing (per-piece JSON; learned overlay) ---------------------

def parse_sidecar(svg_path: Path) -> dict | None:
    """Read the JSON sidecar that lives next to this SVG, if it exists.

    Sidecars are colocated with their SVG: `093/093a.svg` → `093/093a.json`,
    `069/069.svg` → `069/069.json`. Failures (file missing, malformed JSON)
    return None silently — sidecars are optional and the script must run
    cleanly with none present.
    """
    sidecar_path = svg_path.with_suffix(".json")
    if not sidecar_path.exists():
        return None
    try:
        return json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[build_assembly_graph] WARNING: sidecar {sidecar_path} unreadable: {e}",
              file=sys.stderr)
        return None


def extract_inferred_connections(piece_id: str, sidecar: dict | None) -> list[dict]:
    """Extract connections.inferred[] entries from a sidecar.

    Returns a list of normalized inferred-edge records ready to merge with
    SVG-derived edges. Entries without a `kind` or `source` field are
    dropped with a warning. Partner ids are passed through as-authored
    (zero-padded or bare); the merger normalizes when matching.
    """
    if not sidecar:
        return []
    block = sidecar.get("connections", {}).get("inferred", [])
    if not isinstance(block, list):
        print(f"[build_assembly_graph] WARNING: piece {piece_id} sidecar "
              f"connections.inferred is not a list", file=sys.stderr)
        return []
    out = []
    for i, entry in enumerate(block):
        if not isinstance(entry, dict):
            print(f"[build_assembly_graph] WARNING: piece {piece_id} "
                  f"inferred[{i}] not a dict; skipped", file=sys.stderr)
            continue
        kind = entry.get("kind")
        source = entry.get("source")
        if not kind:
            print(f"[build_assembly_graph] WARNING: piece {piece_id} "
                  f"inferred[{i}] missing kind; skipped", file=sys.stderr)
            continue
        if not source:
            print(f"[build_assembly_graph] WARNING: piece {piece_id} "
                  f"inferred[{i}] missing source; skipped", file=sys.stderr)
            continue
        normalized = {
            "from": piece_id,
            "to": entry.get("partner"),
            "kind": kind,
            "side": entry.get("side", "front"),
            "tab": entry.get("tab"),
            "letter": entry.get("letter"),
            "name": entry.get("name"),
            "panel": entry.get("panel"),
            "source": source,
            "note": entry.get("note"),
            "provenance": "inferred",
        }
        out.append(normalized)
    return out


# -- connection-graph extraction -------------------------------------------

def parse_panel_ids(svg_text: str) -> set[str]:
    """Panel ids from <g id="panels">, excluding the layer's own id."""
    block = extract_layer_block(svg_text, "panels")
    if not block:
        return set()
    return {eid for tag, eid in all_ids_in_block(block) if eid != "panels"}


def parse_fold_bindings(svg_text: str, panels: set[str]) -> list[dict]:
    """Each fold path's id is parsed as fold-<a>-<b> against the panel set.

    Recognized id forms (any of):
      - fold-<a>-<b>                     two-panel binding, no fold-step
      - fold-<a>-<b>-<deg>               two-panel binding + default angle
      - <step>-fold-<a>-<b>              two-panel binding + fold-step ordinal
      - <step>-fold-<a>-<b>-<deg>        + both
      - fold-<descriptive>               single-token descriptive fold
      - <step>-fold-<descriptive>        descriptive + fold-step

    The leading <step>-<digits>- is optional. Same step number across multiple
    folds means "fire simultaneously" during a phased fold sequence (introduced
    with piece 095 — accordion strip wrapping a 3D form).

    Returns:
      [
        {"id": "fold-pane1-pane2", "polarity": "valley", "a": "pane1", "b": "pane2", "step": null},
        {"id": "1-fold-pane3-pane4", "polarity": "valley", "a": "pane3", "b": "pane4", "step": 1},
        {"id": "fold-insidetabs", "polarity": "valley", "a": None, "b": None,
         "descriptive": "insidetabs", "step": null},
        ...
      ]
    """
    out = []
    for layer, polarity in [("folds-valley", "valley"), ("folds-mountain", "mountain")]:
        block = extract_layer_block(svg_text, layer)
        if not block:
            continue
        for tag, eid in all_ids_in_block(block):
            if eid == layer:
                continue
            # Affinity Designer prefixes ids that start with a digit with `_`
            # (SVG-spec compliance: ids must begin with a letter or underscore).
            # The author's literal is preserved in `serif:id` on the same element,
            # but for parsing purposes stripping the leading `_` recovers the
            # authored form. Also handles Affinity's collision-rename `_` prefix.
            normalized = eid[1:] if eid.startswith("_") else eid
            # Strip optional leading <step>-fold- prefix.
            step: int | None = None
            m_step = re.match(r'^(\d+)-fold-(.*)$', normalized)
            if m_step:
                step = int(m_step.group(1))
                rest = m_step.group(2)
            elif normalized.startswith("fold-"):
                rest = normalized[5:]
            else:
                continue
            # Strip Affinity collision-prefix '_' that occasionally lands on duplicates.
            # (The duplicate keeps the original id; this branch handles the renamed sibling.)
            # Note: rest never starts with '_' here because the prefix sits before <step>.
            # Try every possible split point in `rest` and look for a:b in panels.
            matched = None
            for i in range(1, len(rest)):
                if rest[i] == "-":
                    a, b = rest[:i], rest[i + 1:]
                    if a in panels and b in panels:
                        matched = (a, b)
                        break
            entry: dict = {
                "id": eid, "polarity": polarity, "step": step,
            }
            if matched:
                entry["a"] = matched[0]
                entry["b"] = matched[1]
            else:
                entry["a"] = None
                entry["b"] = None
                entry["descriptive"] = rest
            out.append(entry)
    return out


def parse_attach_points(svg_text: str, panels: set[str] | None = None) -> list[dict]:
    """Each id-bearing element in <g id="attach-points">.

    Cross-piece connection forms:
      - landing-<tab><piece>      : "I receive tab <tab> from piece <piece>"
      - attach-<letter><piece>    : "I attach to letter <letter> on piece <piece>"
      - hole-<letter><piece>      : "I receive pin <letter> from piece <piece>"
      - pivot-<name>              : "I share rotation pivot <name> with peers"
      - back-<form>               : back-side annotation; rest follows above forms

    Same-piece (closure) connection forms (introduced 2026-05-05 with 095):
      - attach-<panel-id>         : "I (this attach point) mate to <panel-id> of
                                     the same piece" — closure attach
      - back-attach-<panel-id>    : same, but the attach surface is on the back
      The `<panel-id>` must be a known panel of THIS piece; otherwise the form
      is interpreted as the cross-piece `<letter><piece>` shape.

    Forms without a numeric piece suffix (e.g., bare `landing-h`) are still
    in attach-points only by drift — the strict rule (per 068 cleanup) is
    that untyped forms live in marks. We log such cases as anomalies.
    """
    out = []
    block = extract_layer_block(svg_text, "attach-points")
    if not block:
        return out
    panels = panels or set()
    for tag, eid in all_ids_in_block(block):
        if eid == "attach-points":
            continue
        entry = parse_connection_id(eid, panels)
        entry["raw_id"] = eid
        entry["element"] = tag
        out.append(entry)
    return out


def parse_connection_id(eid: str, panels: set[str] | None = None) -> dict:
    """Decompose a connection-graph id into its semantic parts.

    Returns dict with at least: kind, side. Optional: tab, letter, name, partner,
    panel (for same-piece closure forms).

    Side annotation: if id starts with `back-` followed by a recognized
    prefix (landing-, tab-, attach-, hole-, pivot-), strip and mark side="back".
    Otherwise side="front" (default).

    Kind detection on the (possibly side-stripped) id:
      - "landing-"  : tab landing (cross-piece) OR same-piece if matches panels
      - "attach-"   : direct attachment (cross-piece) OR same-piece if matches panels
      - "hole-"     : pin hole
      - "pivot-"    : rotation pivot
      - other       : unknown / anomaly

    Same-piece resolution: when `panels` is provided and the suffix after the
    structural prefix matches a panel id of this piece, the form is interpreted
    as same-piece (closure attach / closure landing). Otherwise we fall through
    to the cross-piece <letter><piece> shape.
    """
    panels = panels or set()
    side = "front"
    s = eid
    # Side-annotation: back- followed by a recognized prefix.
    if s.startswith("back-"):
        rest = s[5:]
        for prefix in ("landing-", "tab-", "attach-", "hole-", "pivot-"):
            if rest.startswith(prefix):
                side = "back"
                s = rest
                break

    if s.startswith("landing-"):
        rest = s[8:]
        # Same-piece closure landing: matches a panel id of this piece.
        if rest in panels:
            return {"kind": "landing-same-piece", "side": side,
                    "panel": rest, "tab": None, "partner": None}
        # Cross-piece: <tab><piece> where <piece> is a numeric suffix.
        m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', rest)
        if m:
            return {"kind": "landing", "side": side,
                    "tab": m.group(1), "partner": m.group(2)}
        # No piece suffix — untyped landing
        return {"kind": "landing", "side": side, "tab": rest, "partner": None}
    if s.startswith("attach-"):
        rest = s[7:]
        # Same-piece closure attach: matches a panel id of this piece.
        if rest in panels:
            return {"kind": "attach-same-piece", "side": side,
                    "panel": rest, "letter": None, "partner": None}
        # Cross-piece: <letter><piece> where <piece> is a numeric suffix.
        m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', rest)
        if m:
            return {"kind": "attach", "side": side,
                    "letter": m.group(1), "partner": m.group(2)}
        return {"kind": "attach", "side": side, "letter": rest, "partner": None}
    if s.startswith("hole-"):
        rest = s[5:]
        m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', rest)
        if m:
            return {"kind": "hole", "side": side,
                    "letter": m.group(1), "partner": m.group(2)}
        return {"kind": "hole", "side": side, "letter": rest, "partner": None}
    if s.startswith("pivot-"):
        return {"kind": "pivot", "side": side, "name": s[6:], "partner": None}
    if s == "hole":
        # bare hole = same-piece generic pin-hole, no partner
        return {"kind": "hole", "side": side, "letter": None, "partner": None}
    # Bare <letter><piece> in attach-points = shorthand for attach-<letter><piece>.
    # Authored on 065 as e66/h66/b66/... pointing at piece 66's letter regions.
    m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', s)
    if m:
        return {"kind": "attach", "side": side,
                "letter": m.group(1), "partner": m.group(2)}
    # Bare letter (no piece suffix) in attach-points = partner-side reference target
    # (e.g. 'j' on 068 confirms "letter j is a structurally referenced point here").
    if re.match(r'^[a-zA-Z][a-zA-Z\-]*$', s) and len(s) <= 8:
        return {"kind": "letter-target", "side": side,
                "letter": s, "partner": None}
    return {"kind": "unknown", "side": side, "raw": s}


def parse_marks(svg_text: str) -> list[dict]:
    """Same-piece markers in <g id="marks">.

    Recognizes: untyped landings (landing-X with no piece suffix),
    multi-instance markers (id repeated N times), printed-letter dots
    (bare letters), alignments (align-<letter><piece>), cuts (cut-<descriptive>),
    side-annotated variants of the above.
    """
    out = []
    block = extract_layer_block(svg_text, "marks")
    if not block:
        return out
    counts: dict[str, int] = defaultdict(int)
    elems: dict[str, str] = {}  # first-seen tag per id
    for tag, eid in all_ids_in_block(block):
        if eid == "marks":
            continue
        counts[eid] += 1
        if eid not in elems:
            elems[eid] = tag

    for eid, count in counts.items():
        side = "front"
        s = eid
        # Side-annotation: back- followed by a recognized prefix.
        if s.startswith("back-"):
            rest = s[5:]
            for prefix in ("landing-", "align-", "cut-", "tab-"):
                if rest.startswith(prefix):
                    side = "back"
                    s = rest
                    break
            else:
                # back-<single-letter-or-id> = back-side decorative marker
                if re.match(r'^[a-zA-Z][a-zA-Z0-9\-]*$', rest):
                    side = "back"
                    s = rest

        kind = "decorative"  # default for bare singletons / printed letters
        partner = None
        tab = None
        if s.startswith("landing-"):
            sub = s[8:]
            # Try to pull a numeric piece suffix (e.g. landing-c69 → tab=c, partner=69)
            m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', sub)
            if m:
                kind = "landing-typed"
                tab = m.group(1)
                partner = m.group(2)
            else:
                kind = "landing-untyped"
                tab = sub
        elif s.startswith("align-"):
            sub = s[6:]
            m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', sub)
            if m:
                kind = "alignment"
                partner = m.group(2)
            else:
                kind = "alignment"
        elif s.startswith("cut-"):
            kind = "cut"
        elif s.startswith("tab-"):
            kind = "tab-marker"
        elif count > 1:
            kind = "multi-instance"
        out.append({
            "id": eid, "side": side, "kind": kind,
            "count": count, "element": elems[eid],
            "tab": tab, "partner": partner,
        })
    return out


# -- per-piece extraction --------------------------------------------------

def parse_piece(svg_path: Path) -> dict:
    """Read one piece's SVG and return its full extracted record.

    The piece id comes from the SVG filename stem, not the parent folder —
    letter-variant pieces (093a, 093b, 092a, 112a) share a parent dir with
    their numeric base.
    """
    piece_id = svg_path.stem  # e.g. "069", "093a", "112a"
    text = read_svg(svg_path)

    layers_present = []
    for layer in LAYERS:
        if extract_layer_block(text, layer):
            layers_present.append(layer)

    panels = sorted(parse_panel_ids(text))
    panels_set = set(panels)
    folds = parse_fold_bindings(text, panels_set)
    attach = parse_attach_points(text, panels_set)
    marks = parse_marks(text)

    # cutouts
    cutouts = []
    block = extract_layer_block(text, "cutouts")
    if block:
        cutouts = [eid for tag, eid in all_ids_in_block(block) if eid != "cutouts"]

    sidecar = parse_sidecar(svg_path)
    inferred = extract_inferred_connections(piece_id, sidecar)

    return {
        "id": piece_id,
        "layers": layers_present,
        "panels": panels,
        "panel_count": len(panels),
        "folds": folds,
        "fold_count": len(folds),
        "fold_unresolved": [f["id"] for f in folds if f["a"] is None],
        "attach_points": attach,
        "marks": marks,
        "cutouts": cutouts,
        "inferred_connections": inferred,
    }


def is_panels_first(record: dict) -> bool:
    """A piece is panels-first if it has a non-empty panels layer."""
    return record["panel_count"] > 0


# -- cross-piece graph + cross-checks --------------------------------------

def find_partner_feature(letter: str, partner: dict, self_id: str | None = None) -> dict | None:
    """Search a partner piece for any feature matching `letter`.

    Lookup chain (LAYER-CONVENTIONS.md "Cross-piece feature lookup"; DECISIONS #12):

      1. Exact panel id == letter                              → "panel-exact"
      2. Panel id == "tab" + letter                            → "panel-tab"
      3. Partner attach-points: parsed letter field == letter  → "attach-{kind}-letter"
      4. Partner marks: id == letter (exact bare-letter match) → "marks-exact"
                                                                 ("marks-exact-multi" when N≥2)
      5. Partner marks: id == "mark-" + letter
                  OR id matches "landing-<letter><self>"       → "marks-mark-prefix"
                                                                 / "marks-landing-self"
      6. Fuzzy substring on panel id                           → "panel-substring"
      7. Fuzzy substring on attach-points semantic part        → "attach-substring"
      8. Fuzzy substring on marks semantic part                → "marks-substring"

    Substring tiebreaker: shortest matching id wins (composite letter clusters
    like 'ai' beat word-shaped names like 'main'); alphabetical break.

    Multi-instance partner marks (one id repeated N≥2 times) return one record
    with `count` field populated so the connection-graph report can render
    "id (×N)" and the via reads "marks-exact-multi".

    Returns {"id": <matched id>, "via": <which step>, "count"?: <N>} or None.
    Backwards-compat alias `_find_letter_match` preserved below.
    """
    if not letter:
        return None
    panels = set(partner.get("panels", []))
    marks = partner.get("marks", [])

    # Normalize self_id for the landing-<letter><self> match in step 5: marks
    # parse partner ids without zero-padding (per the print convention), so
    # "094" needs to compare as "94", "092a" as "92a".
    self_bare = None
    if self_id:
        m_self = re.match(r'^0*(\d+[a-z]?)$', self_id)
        self_bare = m_self.group(1) if m_self else self_id

    # 1. Exact panel
    if letter in panels:
        return {"id": letter, "via": "panel-exact"}

    # 2. tab<letter>
    tab_form = "tab" + letter
    if tab_form in panels:
        return {"id": tab_form, "via": "panel-tab"}

    # 3. Partner attach-points: parsed letter field == letter
    for ap in partner.get("attach_points", []):
        ap_letter = ap.get("letter")
        ap_kind = ap.get("kind")
        if ap_letter == letter and ap_kind in ("attach", "landing", "letter-target", "hole"):
            return {"id": ap.get("raw_id", letter), "via": f"attach-{ap_kind}-letter"}

    # 4. Partner marks: bare-letter exact match (covers multi-instance markers).
    # Convention #16 collision-collapse: when the partner has a base `<letter>`
    # mark AND additional `<letter>\d+` marks (Affinity's auto-rename of
    # duplicate ids on export — e.g. 099's `a, a1, a2, …, a11` for 12 instances),
    # treat the whole group as one logical multi-instance marker. parse_marks
    # keeps the raw ids; the collapse happens here so the resolver returns a
    # single record with a combined `count`. The base id alone (no numbered
    # siblings) returns the singleton with count=1.
    has_base = any(m.get("id") == letter for m in marks)
    if has_base:
        sibling_re = re.compile(rf'^{re.escape(letter)}\d+$')
        total = 0
        for m in marks:
            rid = m.get("id", "")
            if rid == letter or sibling_re.match(rid):
                total += m.get("count", 1)
        via = "marks-exact-multi" if total > 1 else "marks-exact"
        result = {"id": letter, "via": via}
        if total > 1:
            result["count"] = total
        return result

    # 5a. Partner marks: id == "mark-<letter>"
    mark_prefix_id = f"mark-{letter}"
    for mark in marks:
        if mark.get("id") == mark_prefix_id:
            return {"id": mark["id"], "via": "marks-mark-prefix"}

    # 5b. Partner marks: typed-landing whose tab == letter and partner == self
    # (i.e. id matches "landing-<letter><self>"). parse_marks already
    # decomposed these into kind="landing-typed" with tab/partner fields.
    if self_bare:
        for mark in marks:
            if (mark.get("kind") == "landing-typed"
                    and mark.get("tab") == letter
                    and mark.get("partner") == self_bare):
                return {"id": mark["id"], "via": "marks-landing-self"}

    # 6. Fuzzy substring on panel id; shortest-match tiebreaker.
    panel_candidates = [pid for pid in panels if letter in pid]
    if panel_candidates:
        panel_candidates.sort(key=lambda x: (len(x), x))
        return {"id": panel_candidates[0], "via": "panel-substring"}

    # 7. Fuzzy substring on attach-points semantic part. Stripping the
    # structural prefix prevents 'h' from matching the 'h' inside 'hole-'.
    structural_prefixes = ("attach-", "landing-", "tab-", "pivot-", "hole-", "back-")
    for ap in partner.get("attach_points", []):
        rid = ap.get("raw_id", "")
        semantic = rid
        for pfx in structural_prefixes:
            if semantic.startswith(pfx):
                semantic = semantic[len(pfx):]
        if letter in semantic:
            return {"id": rid, "via": "attach-substring"}

    # 8. Fuzzy substring on marks semantic part. Strip mark-/landing-/back-
    # so the prefix word doesn't leak into the substring match.
    def _strip_marks_prefix(rid: str) -> str:
        s = rid
        for pfx in ("back-", "mark-", "landing-"):
            if s.startswith(pfx):
                s = s[len(pfx):]
        return s

    mark_candidates = []
    for mark in marks:
        rid = mark.get("id", "")
        semantic = _strip_marks_prefix(rid)
        if semantic and letter in semantic:
            mark_candidates.append((rid, mark.get("count", 1)))
    if mark_candidates:
        mark_candidates.sort(key=lambda x: (len(x[0]), x[0]))
        rid, count = mark_candidates[0]
        result = {"id": rid, "via": "marks-substring"}
        if count > 1:
            result["count"] = count
        return result

    return None


# Backwards-compat alias for any in-tree caller still using the old name.
_find_letter_match = find_partner_feature


def _edge_signature(edge: dict) -> tuple:
    """Conflict-detection signature for cross-piece edges."""
    return (
        edge.get("from"),
        edge.get("to"),
        edge.get("kind"),
        edge.get("letter") or edge.get("tab") or edge.get("name") or edge.get("panel"),
    )


def _closure_signature(entry: dict) -> tuple:
    """Conflict-detection signature for same-piece closure attaches."""
    return (entry.get("piece"), entry.get("kind"), entry.get("panel"))


def _pivot_signature(piece_id: str, name: str) -> tuple:
    """Conflict-detection signature for pivot membership."""
    return (piece_id, "pivot", name)


def build_connection_graph(pieces: dict[str, dict]) -> dict:
    """Walk every piece's attach_points, build typed cross-piece edges, then
    merge in each piece's sidecar `connections.inferred[]`.

    Edges:
      - landing edges: piece A receives tab <tab> from piece B
        → expects tab<tab> (or panel <tab>) on piece B
      - attach edges: piece A glues onto letter <letter> on piece B
        → expects panel <letter> on piece B
      - hole edges: piece A receives pin from piece B
      - pivot edges (shared name across multiple pieces): pivot ring

    Every edge / closure / pivot member carries a `provenance` field of
    `"authored"` (SVG-derived) or `"inferred"` (sidecar-derived). Conflict
    warnings are computed after the merge: an inferred entry that duplicates
    an authored entry on its conflict signature lands in `inferred_warnings`.
    The script never fails on conflicts.
    """
    edges: list[dict] = []
    # pivot_groups: legacy flat-list shape, preserved for backward-compat
    # consumers (preview.html scene loader). pivot_groups_provenance carries
    # the richer per-member provenance / source / note shape.
    pivot_groups: dict[str, list[str]] = defaultdict(list)
    pivot_groups_provenance: dict[str, list[dict]] = defaultdict(list)
    closure_attaches: list[dict] = []  # same-piece structural attaches (closures)

    # -- pass 1: authored edges from SVG -----------------------------------
    for piece_id, rec in pieces.items():
        # Structural mechanical bindings from attach-points
        for ap in rec["attach_points"]:
            kind = ap.get("kind")
            partner = ap.get("partner")
            if kind == "pivot":
                pivot_groups[ap["name"]].append(piece_id)
                pivot_groups_provenance[ap["name"]].append({
                    "piece": piece_id, "provenance": "authored",
                })
            elif kind in ("attach-same-piece", "landing-same-piece"):
                closure_attaches.append({
                    "piece": piece_id, "kind": kind,
                    "side": ap.get("side"), "panel": ap.get("panel"),
                    "raw_id": ap.get("raw_id"),
                    "provenance": "authored",
                })
            elif kind in ("landing", "attach", "hole") and partner:
                edges.append({
                    "from": piece_id, "to": partner,
                    "kind": kind, "side": ap.get("side"),
                    "tab": ap.get("tab"), "letter": ap.get("letter"),
                    "raw_id": ap.get("raw_id"),
                    "source_layer": "attach-points",
                    "provenance": "authored",
                })
        # Typed landings from marks layer (the reference-marker side of the graph)
        for mark in rec["marks"]:
            if mark["kind"] == "landing-typed" and mark.get("partner"):
                edges.append({
                    "from": piece_id, "to": mark["partner"],
                    "kind": "landing", "side": mark.get("side"),
                    "tab": mark.get("tab"), "letter": None,
                    "raw_id": mark["id"],
                    "source_layer": "marks",
                    "provenance": "authored",
                })

    # -- pass 2: inferred entries from sidecar -----------------------------
    for piece_id, rec in pieces.items():
        for entry in rec.get("inferred_connections", []):
            kind = entry["kind"]
            if kind in ("landing", "attach", "hole"):
                partner = entry.get("to")
                if not partner:
                    print(f"[build_assembly_graph] WARNING: piece {piece_id} "
                          f"inferred {kind} missing partner; skipped",
                          file=sys.stderr)
                    continue
                edges.append({
                    "from": piece_id, "to": partner,
                    "kind": kind, "side": entry.get("side") or "front",
                    "tab": entry.get("tab"), "letter": entry.get("letter"),
                    "raw_id": None,
                    "source_layer": "sidecar.connections.inferred",
                    "provenance": "inferred",
                    "source": entry.get("source"),
                    "note": entry.get("note"),
                })
            elif kind in ("attach-same-piece", "landing-same-piece"):
                closure_attaches.append({
                    "piece": piece_id, "kind": kind,
                    "side": entry.get("side") or "front",
                    "panel": entry.get("panel"),
                    "raw_id": None,
                    "provenance": "inferred",
                    "source": entry.get("source"),
                    "note": entry.get("note"),
                })
            elif kind == "pivot":
                name = entry.get("name")
                if not name:
                    print(f"[build_assembly_graph] WARNING: piece {piece_id} "
                          f"inferred pivot missing name; skipped",
                          file=sys.stderr)
                    continue
                pivot_groups[name].append(piece_id)
                pivot_groups_provenance[name].append({
                    "piece": piece_id, "provenance": "inferred",
                    "source": entry.get("source"),
                    "note": entry.get("note"),
                })
            else:
                print(f"[build_assembly_graph] WARNING: piece {piece_id} "
                      f"inferred unknown kind {kind!r}; skipped",
                      file=sys.stderr)

    # -- pass 3: validation against partner geometry -----------------------
    # Note: partner ids in attach/marks are typically bare numeric ("69") while
    # pieces are keyed zero-padded ("069"). Try both. Inferred and authored
    # edges go through the same validation.
    edge_validation = []
    for edge in edges:
        partner_id = edge["to"]
        partner = pieces.get(partner_id)
        if partner is None and partner_id and partner_id.isdigit():
            padded = partner_id.zfill(3)
            partner = pieces.get(padded)
            if partner is not None:
                edge["to"] = padded
        if partner is None:
            edge_validation.append({**edge, "valid": False,
                                    "reason": f"partner piece {partner_id} not authored yet"})
            continue
        if edge["kind"] == "landing":
            target = edge["tab"]
            match = find_partner_feature(target, partner, edge.get("from"))
            if match:
                rec = {**edge, "valid": True,
                       "matched_panel": match["id"],
                       "matched_via": match["via"]}
                if match.get("count", 1) > 1:
                    rec["matched_panel_count"] = match["count"]
                edge_validation.append(rec)
            else:
                edge_validation.append({**edge, "valid": False,
                                        "reason": f"partner has no feature matching letter {target!r}"})
        elif edge["kind"] == "attach":
            target = edge["letter"]
            match = find_partner_feature(target, partner, edge.get("from"))
            if match:
                rec = {**edge, "valid": True,
                       "matched_panel": match["id"],
                       "matched_via": match["via"]}
                if match.get("count", 1) > 1:
                    rec["matched_panel_count"] = match["count"]
                edge_validation.append(rec)
            else:
                edge_validation.append({**edge, "valid": False,
                                        "reason": f"partner has no feature matching letter {target!r}"})
        elif edge["kind"] == "hole":
            edge_validation.append({**edge, "valid": True,
                                    "note": "hole partner geometry not validated (hardware pin or panel)"})

    pivot_clusters = {name: pieces_list for name, pieces_list in pivot_groups.items()
                      if len(pieces_list) >= 1}
    pivot_clusters_provenance = {
        name: members for name, members in pivot_groups_provenance.items()
        if len(members) >= 1
    }

    # Untyped landings: in marks but no partner piece resolved yet
    untyped = []
    for piece_id, rec in pieces.items():
        for mark in rec["marks"]:
            if mark["kind"] == "landing-untyped":
                untyped.append({
                    "piece": piece_id, "id": mark["id"],
                    "side": mark["side"],
                })

    # -- pass 4: conflict detection ---------------------------------------
    inferred_warnings: list[dict] = []

    # Cross-piece edge conflicts
    authored_edge_sigs = {
        _edge_signature(e) for e in edge_validation
        if e.get("provenance") == "authored"
    }
    for e in edge_validation:
        if e.get("provenance") == "inferred" and _edge_signature(e) in authored_edge_sigs:
            inferred_warnings.append({
                "kind_of_conflict": "edge",
                "from": e.get("from"),
                "to": e.get("to"),
                "kind": e.get("kind"),
                "letter": e.get("letter"),
                "tab": e.get("tab"),
                "panel": e.get("panel"),
                "name": e.get("name"),
                "inferred_source": e.get("source"),
                "message": "inferred entry duplicates an authored edge; "
                           "remove the inferred entry to clean up.",
            })

    # Closure conflicts
    authored_closure_sigs = {
        _closure_signature(c) for c in closure_attaches
        if c.get("provenance") == "authored"
    }
    for c in closure_attaches:
        if c.get("provenance") == "inferred" and _closure_signature(c) in authored_closure_sigs:
            inferred_warnings.append({
                "kind_of_conflict": "closure",
                "piece": c.get("piece"),
                "kind": c.get("kind"),
                "panel": c.get("panel"),
                "inferred_source": c.get("source"),
                "message": "inferred closure entry duplicates an authored "
                           "same-piece attach; remove the inferred entry.",
            })

    # Pivot membership conflicts
    authored_pivot_sigs = set()
    for name, members in pivot_groups_provenance.items():
        for m in members:
            if m.get("provenance") == "authored":
                authored_pivot_sigs.add(_pivot_signature(m["piece"], name))
    for name, members in pivot_groups_provenance.items():
        for m in members:
            if m.get("provenance") == "inferred":
                if _pivot_signature(m["piece"], name) in authored_pivot_sigs:
                    inferred_warnings.append({
                        "kind_of_conflict": "pivot",
                        "piece": m["piece"],
                        "kind": "pivot",
                        "name": name,
                        "inferred_source": m.get("source"),
                        "message": "inferred pivot membership duplicates an "
                                   "authored pivot; remove the inferred entry.",
                    })

    if inferred_warnings:
        print(f"[build_assembly_graph] WARNING: {len(inferred_warnings)} "
              f"inferred-vs-authored conflict(s) detected (see report)",
              file=sys.stderr)

    return {
        "edges": edge_validation,
        "pivot_clusters": pivot_clusters,
        "pivot_clusters_provenance": pivot_clusters_provenance,
        "untyped_landings": untyped,
        "closure_attaches": closure_attaches,
        "inferred_warnings": inferred_warnings,
    }


# -- report rendering ------------------------------------------------------

def render_markdown(pieces: dict[str, dict], graph: dict) -> str:
    lines: list[str] = []
    lines.append("# Assembly connection graph")
    lines.append("")
    lines.append("_Generated by `claude-work/scripts/build_assembly_graph.py`. "
                 "Pre-work for the panels-aware preview.html parser. "
                 "Reads panels-first SVGs in `work/pieces/`._")
    lines.append("")

    # Per-piece summary table
    lines.append("## Per-piece authoring status")
    lines.append("")
    lines.append("| piece | panels-first? | layers | panels | folds (resolved/total) | cross-piece edges out | same-piece marks |")
    lines.append("|---|---|---|---|---|---|---|")
    for piece_id in sorted(pieces.keys()):
        rec = pieces[piece_id]
        pf = "✓" if is_panels_first(rec) else "—"
        n_folds = rec["fold_count"]
        n_unres = len(rec["fold_unresolved"])
        n_resolved = n_folds - n_unres
        n_attach = sum(1 for ap in rec["attach_points"]
                       if ap.get("partner")
                       or ap.get("kind") in ("pivot", "attach-same-piece", "landing-same-piece"))
        n_marks = len(rec["marks"])
        layers = ", ".join(rec["layers"])
        lines.append(f"| {piece_id} | {pf} | {layers} | {rec['panel_count']} | {n_resolved}/{n_folds} | {n_attach} | {n_marks} |")
    lines.append("")

    # Cross-piece edges
    lines.append("## Cross-piece connections (typed edges)")
    lines.append("")
    if not graph["edges"]:
        lines.append("_(none yet)_")
    else:
        lines.append("| from | → | to | kind | side | tab/letter | partner match | matched via | valid? | prov | note |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for edge in graph["edges"]:
            tab_or_letter = edge.get("tab") or edge.get("letter") or "—"
            partner_panel = edge.get("matched_panel", "—")
            count = edge.get("matched_panel_count")
            if count and count > 1:
                partner_panel = f"{partner_panel} (×{count})"
            via = edge.get("matched_via", "")
            valid = "✓" if edge.get("valid") else "✗"
            prov = edge.get("provenance", "authored")
            note = edge.get("reason") or edge.get("note") or ""
            lines.append(f"| {edge['from']} | → | {edge['to']} | {edge['kind']} | {edge.get('side','front')} | {tab_or_letter} | {partner_panel} | {via} | {valid} | {prov} | {note} |")
    lines.append("")

    # Inferred connections (sidecar-derived; learned overlay)
    lines.append("## Inferred connections (from sidecar)")
    lines.append("")
    lines.append("_Cross-piece edges merged from per-piece JSON sidecars' `connections.inferred[]` "
                 "blocks. These are connections learned from the book's instructions text or from "
                 "physically assembling pieces — not printed on the SVG. Each entry carries a "
                 "mandatory `source` field. See DECISIONS #10._")
    lines.append("")
    inferred_edges = [e for e in graph["edges"] if e.get("provenance") == "inferred"]
    if not inferred_edges:
        lines.append("_(none authored)_")
    else:
        lines.append("| from | → | to | kind | side | tab/letter | partner match | valid? | source | note |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for edge in inferred_edges:
            tab_or_letter = edge.get("tab") or edge.get("letter") or "—"
            partner_panel = edge.get("matched_panel", "—")
            count = edge.get("matched_panel_count")
            if count and count > 1:
                partner_panel = f"{partner_panel} (×{count})"
            valid = "✓" if edge.get("valid") else "✗"
            note = edge.get("note") or edge.get("reason") or ""
            source = edge.get("source") or ""
            lines.append(f"| {edge['from']} | → | {edge['to']} | {edge['kind']} | {edge.get('side','front')} | {tab_or_letter} | {partner_panel} | {valid} | {source} | {note} |")
    lines.append("")

    # Inferred conflicts (warnings only; the script does not fail on these)
    lines.append("## Inferred conflicts")
    lines.append("")
    lines.append("_Inferred entries that duplicate an authored edge / closure / pivot membership "
                 "on their conflict signature (`{from, to, kind, letter|tab|name|panel}`). The "
                 "authored entry wins; the inferred entry should typically be removed manually._")
    lines.append("")
    warnings = graph.get("inferred_warnings", [])
    if not warnings:
        lines.append("_(no conflicts detected)_")
    else:
        for w in warnings:
            kc = w.get("kind_of_conflict", "edge")
            if kc == "edge":
                ident = w.get("letter") or w.get("tab") or w.get("panel") or w.get("name") or "—"
                lines.append(f"- **edge** {w.get('from')} → {w.get('to')} "
                             f"({w.get('kind')}, {ident}) — _source: {w.get('inferred_source')}_ — "
                             f"{w.get('message')}")
            elif kc == "closure":
                lines.append(f"- **closure** {w.get('piece')} "
                             f"({w.get('kind')}, panel `{w.get('panel')}`) — "
                             f"_source: {w.get('inferred_source')}_ — {w.get('message')}")
            elif kc == "pivot":
                lines.append(f"- **pivot** {w.get('piece')} ↔ "
                             f"`pivot-{w.get('name')}` — _source: {w.get('inferred_source')}_ — "
                             f"{w.get('message')}")
    lines.append("")

    # Closure attaches (same-piece structural attaches via panel-id; introduced 2026-05-05 with 095)
    lines.append("## Closure attaches (same-piece structural)")
    lines.append("")
    lines.append("_Same-piece attach points authored as `attach-<panel-id>` or `back-attach-<panel-id>` "
                 "where the suffix matches a panel of the piece itself. These are closure attachments — "
                 "tabs that wrap around and glue back onto the same piece (e.g. accordion strip closing on itself). "
                 "Inferred entries (sidecar `kind: \"attach-same-piece\" | \"landing-same-piece\"`) appear "
                 "alongside authored ones with their `source`._")
    lines.append("")
    closure = graph.get("closure_attaches", [])
    if not closure:
        lines.append("_(none authored)_")
    else:
        lines.append("| piece | id | side | mates to panel | prov | source |")
        lines.append("|---|---|---|---|---|---|")
        def _closure_sort_key(x):
            return (x.get("piece") or "", x.get("raw_id") or "", x.get("panel") or "")
        for c in sorted(closure, key=_closure_sort_key):
            raw = c.get("raw_id") or "_(inferred)_"
            id_cell = f"`{raw}`" if c.get("raw_id") else raw
            prov = c.get("provenance", "authored")
            source = c.get("source") or ""
            lines.append(f"| {c['piece']} | {id_cell} | {c.get('side','front')} | `{c.get('panel')}` | {prov} | {source} |")
    lines.append("")

    # Pivot clusters
    lines.append("## Shared pivots")
    lines.append("")
    pivot_prov = graph.get("pivot_clusters_provenance", {})
    if not pivot_prov and not graph.get("pivot_clusters"):
        lines.append("_(none authored)_")
    elif pivot_prov:
        for name, members in sorted(pivot_prov.items()):
            # Stable de-duped per piece (one entry per piece per cluster, prefer authored on tie).
            seen: dict[str, str] = {}
            for m in members:
                p = m.get("piece")
                prov = m.get("provenance", "authored")
                if p not in seen or (seen[p] == "inferred" and prov == "authored"):
                    seen[p] = prov
            ordered = sorted(seen.items())
            members_str = ", ".join(f"{p} ({prov})" for p, prov in ordered)
            lines.append(f"- **`pivot-{name}`** — pieces: {members_str}")
    else:
        # legacy fallback (no provenance map for some reason)
        for name, members in sorted(graph["pivot_clusters"].items()):
            lines.append(f"- **`pivot-{name}`** — pieces: {', '.join(sorted(set(members)))}")
    lines.append("")

    # Untyped landings (in marks but partner piece not yet specified)
    lines.append("## Untyped landings (in `marks`, no partner piece)")
    lines.append("_Landing markers without a partner-piece suffix. These are placeholders the parser can't yet resolve to cross-piece edges. Closure landings (where same-piece tab wraps around) and informative untyped markers both land here. Untyped doesn't mean wrong — many of these are intentional._")
    lines.append("")
    if not graph["untyped_landings"]:
        lines.append("_(none)_")
    else:
        for ut in sorted(graph["untyped_landings"], key=lambda x: (x["piece"], x["id"])):
            side = f" ({ut['side']})" if ut["side"] != "front" else ""
            lines.append(f"- **{ut['piece']}** has `{ut['id']}`{side}")
    lines.append("")

    # Per-piece detail
    lines.append("## Per-piece detail")
    lines.append("")
    for piece_id in sorted(pieces.keys()):
        rec = pieces[piece_id]
        lines.append(f"### Piece {piece_id}")
        lines.append("")
        lines.append(f"- **Layers present:** {', '.join(rec['layers'])}")
        lines.append(f"- **Panels ({rec['panel_count']}):** {', '.join(rec['panels']) if rec['panels'] else '—'}")
        if rec["cutouts"]:
            lines.append(f"- **Cutouts:** {', '.join(rec['cutouts'])}")
        if rec["fold_count"]:
            valley = [f for f in rec["folds"] if f["polarity"] == "valley"]
            mountain = [f for f in rec["folds"] if f["polarity"] == "mountain"]
            steps = sorted({f["step"] for f in rec["folds"] if f.get("step") is not None})
            step_str = f"; fold-steps: {steps}" if steps else ""
            lines.append(f"- **Folds:** {len(valley)} valley + {len(mountain)} mountain "
                         f"({rec['fold_count'] - len(rec['fold_unresolved'])} resolved, "
                         f"{len(rec['fold_unresolved'])} unresolved){step_str}")
            if rec["fold_unresolved"]:
                lines.append(f"  - Unresolved: {', '.join(rec['fold_unresolved'])}")
        ap = rec["attach_points"]
        ic = rec.get("inferred_connections", [])
        if ap or ic:
            total = len(ap) + len(ic)
            lines.append(f"- **Attach-points ({total}):**")
            for entry in ap:
                desc = entry.get("kind", "?")
                side = entry.get("side", "front")
                side_str = f" [back-side]" if side == "back" else ""
                partner = entry.get("partner")
                panel = entry.get("panel")
                if panel:
                    target_str = f" → same-piece panel `{panel}`"
                elif partner:
                    target_str = f" → piece {partner}"
                else:
                    target_str = " (no partner)"
                lines.append(f"  - `{entry['raw_id']}` ({desc}{side_str}{target_str})")
            for entry in ic:
                kind = entry.get("kind", "?")
                side = entry.get("side", "front")
                side_str = f" [back-side]" if side == "back" else ""
                if kind in ("attach-same-piece", "landing-same-piece"):
                    target_str = f" → same-piece panel `{entry.get('panel')}`"
                elif kind == "pivot":
                    target_str = f" (pivot `{entry.get('name')}`)"
                else:
                    ident = entry.get("letter") or entry.get("tab") or "?"
                    target_str = f" → piece {entry.get('to')} (letter/tab `{ident}`)"
                lines.append(f"  - _(inferred)_ ({kind}{side_str}{target_str}) [inferred]")
                if entry.get("source"):
                    lines.append(f"    - _source: {entry['source']}_")
                if entry.get("note"):
                    lines.append(f"    - _note: {entry['note']}_")
        marks = rec["marks"]
        if marks:
            lines.append(f"- **Marks ({len(marks)}):**")
            kind_grouped: dict[str, list[dict]] = defaultdict(list)
            for mark in marks:
                kind_grouped[mark["kind"]].append(mark)
            for kind, items in sorted(kind_grouped.items()):
                ids_str = ", ".join(f"`{m['id']}`" + (f"×{m['count']}" if m['count'] > 1 else "")
                                    for m in items)
                lines.append(f"  - {kind}: {ids_str}")
        lines.append("")

    return "\n".join(lines)


# -- main ------------------------------------------------------------------

def main() -> int:
    pieces: dict[str, dict] = {}
    # Match SVGs whose stem is the dir name OR the dir name + a single lowercase
    # letter (the variant suffix per File Naming Conventions: `093/093a.svg`,
    # `093/093b.svg`). This skips Affinity untitled exports like `Document.svg`.
    variant_re = re.compile(r'^[a-z]?$')
    for piece_dir in sorted(PIECES_DIR.iterdir()):
        if not piece_dir.is_dir():
            continue
        for svg_path in sorted(piece_dir.glob("*.svg")):
            stem = svg_path.stem
            if not stem.startswith(piece_dir.name):
                continue
            suffix = stem[len(piece_dir.name):]
            if not variant_re.match(suffix):
                continue
            rec = parse_piece(svg_path)
            if not is_panels_first(rec):
                continue
            pieces[stem] = rec

    graph = build_connection_graph(pieces)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump({"pieces": pieces, "graph": graph}, f, indent=2)

    md = render_markdown(pieces, graph)
    OUT_MD.write_text(md, encoding="utf-8")

    print(f"[build_assembly_graph] panels-first pieces processed: {len(pieces)}")
    print(f"[build_assembly_graph]   pieces: {', '.join(sorted(pieces.keys()))}")
    print(f"[build_assembly_graph] cross-piece edges: {len(graph['edges'])}")
    authored_edges = sum(1 for e in graph["edges"] if e.get("provenance") == "authored")
    inferred_edges = sum(1 for e in graph["edges"] if e.get("provenance") == "inferred")
    print(f"[build_assembly_graph]   authored edges: {authored_edges}, inferred edges: {inferred_edges}")
    print(f"[build_assembly_graph] pivot clusters: {len(graph['pivot_clusters'])}")
    print(f"[build_assembly_graph] untyped landings: {len(graph['untyped_landings'])}")
    print(f"[build_assembly_graph] closure attaches: {len(graph.get('closure_attaches', []))}")
    print(f"[build_assembly_graph] inferred conflicts: {len(graph.get('inferred_warnings', []))}")
    print(f"[build_assembly_graph] wrote: {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"[build_assembly_graph] wrote: {OUT_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
