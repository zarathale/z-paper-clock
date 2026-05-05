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


# -- connection-graph extraction -------------------------------------------

def parse_panel_ids(svg_text: str) -> set[str]:
    """Panel ids from <g id="panels">, excluding the layer's own id."""
    block = extract_layer_block(svg_text, "panels")
    if not block:
        return set()
    return {eid for tag, eid in all_ids_in_block(block) if eid != "panels"}


def parse_fold_bindings(svg_text: str, panels: set[str]) -> list[dict]:
    """Each fold path's id is parsed as fold-<a>-<b> against the panel set.

    Returns:
      [
        {"id": "fold-pane1-pane2", "polarity": "valley", "a": "pane1", "b": "pane2"},
        {"id": "fold-insidetabs", "polarity": "valley", "a": None, "b": None,
         "descriptive": "insidetabs"},
        ...
      ]
    Unresolved fold ids (no matching panel pair) get a:b=None and a "descriptive"
    field set.
    """
    out = []
    for layer, polarity in [("folds-valley", "valley"), ("folds-mountain", "mountain")]:
        block = extract_layer_block(svg_text, layer)
        if not block:
            continue
        for tag, eid in all_ids_in_block(block):
            if eid == layer or not eid.startswith("fold-"):
                continue
            rest = eid[5:]
            # Try every possible split point in `rest` and look for a:b in panels.
            matched = None
            for i in range(1, len(rest)):
                if rest[i] == "-":
                    a, b = rest[:i], rest[i + 1:]
                    if a in panels and b in panels:
                        matched = (a, b)
                        break
            if matched:
                out.append({
                    "id": eid, "polarity": polarity,
                    "a": matched[0], "b": matched[1],
                })
            else:
                out.append({
                    "id": eid, "polarity": polarity,
                    "a": None, "b": None, "descriptive": rest,
                })
    return out


def parse_attach_points(svg_text: str) -> list[dict]:
    """Each id-bearing element in <g id="attach-points">.

    Cross-piece connection forms:
      - landing-<tab><piece>      : "I receive tab <tab> from piece <piece>"
      - attach-<letter><piece>    : "I attach to letter <letter> on piece <piece>"
      - hole-<letter><piece>      : "I receive pin <letter> from piece <piece>"
      - pivot-<name>              : "I share rotation pivot <name> with peers"
      - back-<form>               : back-side annotation; rest follows above forms

    Forms without a numeric piece suffix (e.g., bare `landing-h`) are still
    in attach-points only by drift — the strict rule (per 068 cleanup) is
    that untyped forms live in marks. We log such cases as anomalies.
    """
    out = []
    block = extract_layer_block(svg_text, "attach-points")
    if not block:
        return out
    for tag, eid in all_ids_in_block(block):
        if eid == "attach-points":
            continue
        entry = parse_connection_id(eid)
        entry["raw_id"] = eid
        entry["element"] = tag
        out.append(entry)
    return out


def parse_connection_id(eid: str) -> dict:
    """Decompose a connection-graph id into its semantic parts.

    Returns dict with at least: kind, side. Optional: tab, letter, name, partner.

    Side annotation: if id starts with `back-` followed by a recognized
    prefix (landing-, tab-, attach-, hole-, pivot-), strip and mark side="back".
    Otherwise side="front" (default).

    Kind detection on the (possibly side-stripped) id:
      - "landing-" : tab landing
      - "attach-"  : direct attachment
      - "hole-"    : pin hole
      - "pivot-"   : rotation pivot
      - other      : unknown / anomaly
    """
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
        # Try to split into <tab><piece> where <piece> is a numeric suffix.
        # Pattern: letters+ followed by digits+ (with optional letter variant `a`).
        m = re.match(r'^([a-zA-Z][a-zA-Z\-]*?)(\d+[a-z]?)$', rest)
        if m:
            return {"kind": "landing", "side": side,
                    "tab": m.group(1), "partner": m.group(2)}
        # No piece suffix — untyped landing
        return {"kind": "landing", "side": side, "tab": rest, "partner": None}
    if s.startswith("attach-"):
        rest = s[7:]
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
    """Read one piece's SVG and return its full extracted record."""
    piece_id = svg_path.parent.name  # e.g. "069"
    text = read_svg(svg_path)

    layers_present = []
    for layer in LAYERS:
        if extract_layer_block(text, layer):
            layers_present.append(layer)

    panels = sorted(parse_panel_ids(text))
    folds = parse_fold_bindings(text, set(panels))
    attach = parse_attach_points(text)
    marks = parse_marks(text)

    # cutouts
    cutouts = []
    block = extract_layer_block(text, "cutouts")
    if block:
        cutouts = [eid for tag, eid in all_ids_in_block(block) if eid != "cutouts"]

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
    }


def is_panels_first(record: dict) -> bool:
    """A piece is panels-first if it has a non-empty panels layer."""
    return record["panel_count"] > 0


# -- cross-piece graph + cross-checks --------------------------------------

def _find_letter_match(letter: str, partner: dict) -> dict | None:
    """Search a partner piece for any feature matching `letter`.

    Strips structural prefixes (attach-, landing-, tab-, pivot-, hole-, back-)
    from partner ids before comparing, so substring matches don't leak into
    those prefix words. Compares against parsed letter fields where available.

    Search priority:
      1. Exact panel id == letter
      2. Exact panel id == "tab" + letter   (landing-c69 → tabc on 069)
      3. Partner attach-points: parsed letter field == letter
      4. Partner attach-points: id (semantic part) starts with letter / equals letter
      5. Fuzzy substring on panel id (composite ids like 'bh', 'ai', 'e65')
      6. Fuzzy substring on attach-points semantic part

    Returns {"id": <matched id>, "via": <which search step>} or None.
    """
    if not letter:
        return None
    panels = set(partner.get("panels", []))

    # 1. Exact panel
    if letter in panels:
        return {"id": letter, "via": "panel-exact"}
    # 2. tab<letter>
    tab_form = "tab" + letter
    if tab_form in panels:
        return {"id": tab_form, "via": "panel-tab"}
    # 3-4. Attach-points: compare against parsed letter field
    for ap in partner.get("attach_points", []):
        ap_letter = ap.get("letter")
        ap_kind = ap.get("kind")
        if ap_letter == letter and ap_kind in ("attach", "landing", "letter-target", "hole"):
            return {"id": ap.get("raw_id", letter), "via": f"attach-{ap_kind}-letter"}
    # 5. Fuzzy substring on panel id (only meaningful chars; skip if letter is too short
    # and would create silly matches — but composite ids like 'bh' are exactly the case
    # we want, so keep it permissive on panels). Tie-break by preferring the SHORTEST
    # match (composite letter clusters like 'ai' beat word-shaped names like 'main').
    candidates = [pid for pid in panels if letter in pid]
    if candidates:
        candidates.sort(key=lambda x: (len(x), x))
        return {"id": candidates[0], "via": "panel-substring"}
    # 6. Fuzzy substring on attach-points but only on the SEMANTIC portion of the id
    # (after stripping known prefixes), so 'h' in 'attach-d66' doesn't match.
    structural_prefixes = ("attach-", "landing-", "tab-", "pivot-", "hole-", "back-")
    for ap in partner.get("attach_points", []):
        rid = ap.get("raw_id", "")
        semantic = rid
        for pfx in structural_prefixes:
            if semantic.startswith(pfx):
                semantic = semantic[len(pfx):]
        if letter in semantic:
            return {"id": rid, "via": "attach-substring"}
    return None


def build_connection_graph(pieces: dict[str, dict]) -> dict:
    """Walk every piece's attach_points, build typed cross-piece edges.

    Edges:
      - landing edges: piece A receives tab <tab> from piece B
        → expects tab<tab> (or panel <tab>) on piece B
      - attach edges: piece A glues onto letter <letter> on piece B
        → expects panel <letter> on piece B
      - hole edges: piece A receives pin from piece B
      - pivot edges (shared name across multiple pieces): pivot ring
    """
    edges: list[dict] = []
    pivot_groups: dict[str, list[str]] = defaultdict(list)

    for piece_id, rec in pieces.items():
        # Structural mechanical bindings from attach-points
        for ap in rec["attach_points"]:
            kind = ap.get("kind")
            partner = ap.get("partner")
            if kind == "pivot":
                pivot_groups[ap["name"]].append(piece_id)
            elif kind in ("landing", "attach", "hole") and partner:
                edges.append({
                    "from": piece_id, "to": partner,
                    "kind": kind, "side": ap.get("side"),
                    "tab": ap.get("tab"), "letter": ap.get("letter"),
                    "raw_id": ap.get("raw_id"),
                    "source_layer": "attach-points",
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
                })

    # Validate edges: does the partner piece have the expected counterpart?
    # Note: partner ids in attach/marks are typically bare numeric ("69") while
    # pieces are keyed zero-padded ("069"). Try both.
    edge_validation = []
    for edge in edges:
        partner_id = edge["to"]
        partner = pieces.get(partner_id)
        if partner is None and partner_id.isdigit():
            padded = partner_id.zfill(3)
            partner = pieces.get(padded)
            if partner is not None:
                edge["to"] = padded
        if partner is None:
            edge_validation.append({**edge, "valid": False,
                                    "reason": f"partner piece {partner_id} not authored yet"})
            continue
        if edge["kind"] == "landing":
            # Search partner for any feature matching the tab letter.
            # Order: exact panel `tab<X>`, exact panel `<X>`, fuzzy panel substring,
            # exact id in partner attach-points / marks (the letter-target form).
            target = edge["tab"]
            match = _find_letter_match(target, partner)
            if match:
                edge_validation.append({**edge, "valid": True,
                                        "matched_panel": match["id"],
                                        "matched_via": match["via"]})
            else:
                edge_validation.append({**edge, "valid": False,
                                        "reason": f"partner has no feature matching letter {target!r}"})
        elif edge["kind"] == "attach":
            target = edge["letter"]
            match = _find_letter_match(target, partner)
            if match:
                edge_validation.append({**edge, "valid": True,
                                        "matched_panel": match["id"],
                                        "matched_via": match["via"]})
            else:
                edge_validation.append({**edge, "valid": False,
                                        "reason": f"partner has no feature matching letter {target!r}"})
        elif edge["kind"] == "hole":
            edge_validation.append({**edge, "valid": True,
                                    "note": "hole partner geometry not validated (hardware pin or panel)"})

    pivot_clusters = {name: pieces_list for name, pieces_list in pivot_groups.items()
                      if len(pieces_list) >= 1}

    # Untyped landings: in marks but no partner piece resolved yet
    untyped = []
    for piece_id, rec in pieces.items():
        for mark in rec["marks"]:
            if mark["kind"] == "landing-untyped":
                untyped.append({
                    "piece": piece_id, "id": mark["id"],
                    "side": mark["side"],
                })

    return {
        "edges": edge_validation,
        "pivot_clusters": pivot_clusters,
        "untyped_landings": untyped,
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
                       if ap.get("partner") or ap.get("kind") == "pivot")
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
        lines.append("| from | → | to | kind | side | tab/letter | partner match | matched via | valid? | note |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for edge in graph["edges"]:
            tab_or_letter = edge.get("tab") or edge.get("letter") or "—"
            partner_panel = edge.get("matched_panel", "—")
            via = edge.get("matched_via", "")
            valid = "✓" if edge.get("valid") else "✗"
            note = edge.get("reason") or edge.get("note") or ""
            lines.append(f"| {edge['from']} | → | {edge['to']} | {edge['kind']} | {edge.get('side','front')} | {tab_or_letter} | {partner_panel} | {via} | {valid} | {note} |")
    lines.append("")

    # Pivot clusters
    lines.append("## Shared pivots")
    lines.append("")
    if not graph["pivot_clusters"]:
        lines.append("_(none authored)_")
    else:
        for name, members in sorted(graph["pivot_clusters"].items()):
            lines.append(f"- **`pivot-{name}`** — pieces: {', '.join(sorted(set(members)))}")
    lines.append("")

    # Untyped landings (in marks but partner piece not yet specified)
    lines.append("## Untyped landings (in `marks`, no partner piece)")
    lines.append("")
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
            lines.append(f"- **Folds:** {len(valley)} valley + {len(mountain)} mountain "
                         f"({rec['fold_count'] - len(rec['fold_unresolved'])} resolved, "
                         f"{len(rec['fold_unresolved'])} unresolved)")
            if rec["fold_unresolved"]:
                lines.append(f"  - Unresolved: {', '.join(rec['fold_unresolved'])}")
        ap = rec["attach_points"]
        if ap:
            lines.append(f"- **Attach-points ({len(ap)}):**")
            for entry in ap:
                tag = entry.get("element", "?")
                desc = entry.get("kind", "?")
                side = entry.get("side", "front")
                side_str = f" [back-side]" if side == "back" else ""
                partner = entry.get("partner")
                partner_str = f" → piece {partner}" if partner else " (no partner)"
                lines.append(f"  - `{entry['raw_id']}` ({desc}{side_str}{partner_str})")
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
    for piece_dir in sorted(PIECES_DIR.iterdir()):
        if not piece_dir.is_dir():
            continue
        svg_path = piece_dir / f"{piece_dir.name}.svg"
        if not svg_path.exists():
            continue
        rec = parse_piece(svg_path)
        if not is_panels_first(rec):
            continue
        pieces[piece_dir.name] = rec

    graph = build_connection_graph(pieces)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump({"pieces": pieces, "graph": graph}, f, indent=2)

    md = render_markdown(pieces, graph)
    OUT_MD.write_text(md, encoding="utf-8")

    print(f"[build_assembly_graph] panels-first pieces processed: {len(pieces)}")
    print(f"[build_assembly_graph]   pieces: {', '.join(sorted(pieces.keys()))}")
    print(f"[build_assembly_graph] cross-piece edges: {len(graph['edges'])}")
    valid = sum(1 for e in graph['edges'] if e.get('valid'))
    print(f"[build_assembly_graph]   valid: {valid} / {len(graph['edges'])}")
    print(f"[build_assembly_graph] pivot clusters: {len(graph['pivot_clusters'])}")
    print(f"[build_assembly_graph] untyped landings: {len(graph['untyped_landings'])}")
    print(f"[build_assembly_graph] wrote: {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"[build_assembly_graph] wrote: {OUT_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
