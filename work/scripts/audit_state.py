#!/usr/bin/env python3
"""
audit_state.py — Read-only asset-state audit for z-paper-clock.

Walks the repo, computes per-piece state from filesystem reality, emits work/state.json.
Never writes anywhere except work/state.json. Never modifies pieces.csv or anything under source/.

Usage:
    python work/scripts/audit_state.py            # write state.json + print summary
    python work/scripts/audit_state.py --quiet    # write state.json; suppress summary
    python work/scripts/audit_state.py --piece 069  # detailed report for one piece (no file write)
    python work/scripts/audit_state.py --check    # exit non-zero if any required check fails
"""

from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Resolve repo root from this file's location: work/scripts/audit_state.py → repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ── canonical constants ────────────────────────────────────────────────────────

CANONICAL_LAYERS = {
    "silhouette", "cutouts", "folds-valley", "folds-mountain",
    "axles", "glue-zones", "labels", "marks",
}

# IDs that are valid inside <g id="silhouette"> but not canonical layer names
SILHOUETTE_CHILD_IDS = re.compile(r"^(cutaway(?:-\d+)?|mask(?:-\d+)?)$")

# Landing marker id format — two valid forms:
#   1. Cross-piece:  landing-<letter><piece-number>[<variant-letter>]
#                    e.g. landing-c70, landing-h65, landing-a92a
#   2. Same-piece closure (LAYER-CONVENTIONS.md line 157): landing-<panel-id>
#                    where the suffix is bare letters naming a panel on this piece
#                    (a tab wraps around to land here on the same piece)
#                    e.g. landing-d, landing-taba, landing-tabaa, landing-aa
LANDING_ID_RE = re.compile(r"^landing-[a-z]+(?:[0-9]+[a-z]?)?$")

# ── filename patterns ──────────────────────────────────────────────────────────

PIECE_PNG    = re.compile(r"^(\d{3})([a-z])?\.png$")
PIECE_AF     = re.compile(r"^(\d{3})([a-z])?(?:-([a-z]+(?:-[a-z]+)*))?\.af$")
SVG_FILE     = re.compile(r"^(\d{3})([a-z])?(?:-([a-z]+(?:-[a-z]+)*))?\.svg$")
CHUNK_LIST   = re.compile(r"^(\d+(?:_\d+)+)\.(jpe?g|png)$")
CHUNK_SINGLE = re.compile(r"^(\d+)\.(jpe?g|png)$")
CHUNK_SINGLE_LV = re.compile(r"^(\d+[a-z])\.(jpe?g|png)$")
CHUNK_STITCH = re.compile(r"^(\d+(?:_\d+)*)_stitched\.png$")
CHUNK_LR     = re.compile(r"^(\d+(?:_\d+)*)_(l|r)\.jpeg$")


def _local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def normalize_piece_id(raw: str) -> str:
    """Zero-pad numeric part of a raw piece id token to 3 digits."""
    m = re.match(r"^(\d+)([a-z]?)$", raw)
    if m:
        num, letter = m.group(1), m.group(2)
        return f"{int(num):03d}{letter}"
    return raw


def chunk_piece_ids(filename: str) -> list[str]:
    """Extract zero-padded piece ids from a chunk filename."""
    name = Path(filename).name

    m = CHUNK_STITCH.match(name)
    if m:
        return [normalize_piece_id(p) for p in m.group(1).split("_")]

    m = CHUNK_LR.match(name)
    if m:
        return [normalize_piece_id(p) for p in m.group(1).split("_")]

    m = CHUNK_LIST.match(name)
    if m:
        return [normalize_piece_id(p) for p in m.group(1).split("_")]

    m = CHUNK_SINGLE_LV.match(name)
    if m:
        return [normalize_piece_id(m.group(1))]

    m = CHUNK_SINGLE.match(name)
    if m:
        return [normalize_piece_id(m.group(1))]

    return []


# ── data structures ────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    id: str
    description: str
    severity: str
    result: str          # pass | fail | skip | error
    evidence: Optional[str] = None
    message: Optional[str] = None


@dataclass
class PieceState:
    id: str
    csv_meta: dict
    files: dict = field(default_factory=lambda: {
        "source_png": None,
        "affinity": [],
        "svgs": [],
        "derivative_dir_files": [],
        "chunk_membership": [],
    })
    svg_analysis: Optional[dict] = None
    convention_checks: list = field(default_factory=list)
    stage: str = "pending_capture"
    anomalies: list = field(default_factory=list)


# ── master list ────────────────────────────────────────────────────────────────

def load_master(repo_root: Path) -> dict[str, dict]:
    pieces_csv = repo_root / "work" / "pieces.csv"
    with pieces_csv.open(newline="") as f:
        rows = (line for line in f if not line.startswith("#"))
        reader = csv.DictReader(rows)
        return {
            row["id"].strip(): {k: row.get(k, "").strip() for k in ("plate", "section", "bucket", "status", "notes")}
            for row in reader
            if row.get("id")
        }


# ── SVG analysis ──────────────────────────────────────────────────────────────

def find_layers(svg_root) -> dict[str, object]:
    """Return {layer_id: element} for all layers in the SVG.

    Handles the Affinity pattern where some layers are children of an unnamed
    top-level <g> wrapper while others are direct children of <svg>.
    """
    layers = {}

    def _collect(parent):
        for child in parent:
            if _local(child.tag) != "g":
                continue
            eid = child.get("id", "") or child.get(
                "{http://www.inkscape.org/namespaces/inkscape}label", ""
            )
            if eid in CANONICAL_LAYERS:
                layers[eid] = child
            elif not eid:
                # unnamed wrapper — look one level deeper
                _collect(child)

    _collect(svg_root)
    return layers


def collect_named_descendant_ids(elem) -> list[str]:
    """Return ids of all named descendants of elem (skipping elem itself)."""
    ids = []
    for child in elem.iter():
        if child is elem:
            continue
        cid = child.get("id", "")
        if cid:
            ids.append(cid)
    return ids


def top_level_named_groups(svg_root) -> dict[str, object]:
    """Return {id: element} for named <g> elements at SVG top level (including unnamed-wrapper children)."""
    groups = {}
    for child in svg_root:
        if _local(child.tag) != "g":
            continue
        eid = child.get("id", "")
        if eid:
            groups[eid] = child
        else:
            for grandchild in child:
                if _local(grandchild.tag) == "g":
                    gcid = grandchild.get("id", "")
                    if gcid:
                        groups[gcid] = grandchild
    return groups


def analyse_svg(path: str, repo_root: Path) -> dict:
    from lxml import etree

    abs_path = repo_root / path
    result: dict = {
        "primary_svg": path,
        "primary_svg_mtime": None,
        "all_svgs": [path],
        "xml_well_formed": False,
        "view_box": None,
        "layers_present": [],
        "layer_id_inventory": {},
        "off_spec_layers": [],
        "_root": None,
    }

    try:
        mtime = abs_path.stat().st_mtime
        result["primary_svg_mtime"] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        tree = etree.parse(str(abs_path))
        root = tree.getroot()
        result["xml_well_formed"] = True
        result["_root"] = root
    except Exception as e:
        result["_parse_error"] = str(e)
        return result

    result["view_box"] = root.get("viewBox")

    layers = find_layers(root)
    result["layers_present"] = sorted(layers.keys())

    inventory = {}
    for lid, layer_elem in layers.items():
        named_ids = collect_named_descendant_ids(layer_elem)
        if named_ids:
            inventory[lid] = named_ids
    result["layer_id_inventory"] = inventory

    # top-level named groups not in CANONICAL_LAYERS (and not mask/mask-N visual frames)
    all_top_groups = top_level_named_groups(root)
    off_spec = [
        gid for gid in all_top_groups
        if gid not in CANONICAL_LAYERS and not re.match(r"^mask(?:-\d+)?$", gid)
    ]
    result["off_spec_layers"] = off_spec

    return result


# ── convention checks ──────────────────────────────────────────────────────────

CHECKS: list[tuple] = []


def register(check_id: str, description: str, severity: str):
    def deco(fn):
        CHECKS.append((check_id, description, severity, fn))
        return fn
    return deco


def _make(check_id, description, severity, result, evidence=None, message=None) -> CheckResult:
    return CheckResult(
        id=check_id, description=description, severity=severity,
        result=result, evidence=evidence, message=message,
    )


@register("xml-well-formed", "SVG parses without XML error", "required")
def check_xml_well_formed(analysis):
    if analysis.get("xml_well_formed"):
        return _make("xml-well-formed", "SVG parses without XML error", "required",
                     "pass", "Parsed successfully")
    err = analysis.get("_parse_error", "unknown parse error")
    return _make("xml-well-formed", "SVG parses without XML error", "required",
                 "fail", message=err)


@register("silhouette-layer-present", "<g id='silhouette'> exists", "required")
def check_silhouette_layer(analysis):
    if "silhouette" in analysis.get("layers_present", []):
        return _make("silhouette-layer-present", "<g id='silhouette'> exists", "required",
                     "pass", "Found silhouette layer")
    return _make("silhouette-layer-present", "<g id='silhouette'> exists", "required",
                 "fail", message="Top-level <g id='silhouette'> not found")


@register("silhouette-cutaway-id", "silhouette has cutaway or cutaway-N element", "required")
def check_silhouette_cutaway(analysis):
    inv = analysis.get("layer_id_inventory", {})
    sil_ids = inv.get("silhouette", [])
    cutaway_ids = [i for i in sil_ids if re.match(r"^cutaway(?:-\d+)?$", i)]
    if cutaway_ids:
        return _make("silhouette-cutaway-id", "silhouette has cutaway or cutaway-N element", "required",
                     "pass", f"Found: {', '.join(cutaway_ids)}")
    if "silhouette" not in analysis.get("layers_present", []):
        return _make("silhouette-cutaway-id", "silhouette has cutaway or cutaway-N element", "required",
                     "skip", message="silhouette layer not present")
    return _make("silhouette-cutaway-id", "silhouette has cutaway or cutaway-N element", "required",
                 "fail", message="No cutaway or cutaway-N id found among silhouette descendants")


@register("cutouts-layer-format", "cutouts children use cutout-N ids (not cutout-letter)", "advisory")
def check_cutouts_format(analysis):
    layers = analysis.get("layers_present", [])
    if "cutouts" not in layers:
        return _make("cutouts-layer-format", "cutouts children use cutout-N ids (not cutout-letter)", "advisory",
                     "skip", message="No cutouts layer present")
    inv = analysis.get("layer_id_inventory", {})
    cutout_ids = [i for i in inv.get("cutouts", []) if i.startswith("cutout")]
    bad = [i for i in cutout_ids if not re.match(r"^cutout-\d+$", i)]
    if bad:
        return _make("cutouts-layer-format", "cutouts children use cutout-N ids (not cutout-letter)", "advisory",
                     "fail", message=f"Non-numeric cutout ids: {', '.join(bad)}")
    good = [i for i in cutout_ids if re.match(r"^cutout-\d+$", i)]
    return _make("cutouts-layer-format", "cutouts children use cutout-N ids (not cutout-letter)", "advisory",
                 "pass", f"{len(good)} cutout-N id(s) found" if good else "No cutout ids (layer may be empty)")


@register("axles-layer-clean", "axles layer contains only ellipse/circle/path + optional north", "advisory")
def check_axles_clean(analysis):
    layers = analysis.get("layers_present", [])
    if "axles" not in layers:
        return _make("axles-layer-clean", "axles layer contains only ellipse/circle/path + optional north", "advisory",
                     "skip", message="No axles layer present")
    root = analysis.get("_root")
    if root is None:
        return _make("axles-layer-clean", "axles layer contains only ellipse/circle/path + optional north", "advisory",
                     "skip", message="SVG root unavailable")
    from lxml import etree
    axles_layer = find_layers(root).get("axles")
    if axles_layer is None:
        return _make("axles-layer-clean", "axles layer contains only ellipse/circle/path + optional north", "advisory",
                     "skip", message="axles layer not found in tree")
    ALLOWED = {"ellipse", "circle", "path", "g"}
    bad_tags = []
    for elem in axles_layer.iter():
        if elem is axles_layer:
            continue
        tag = _local(elem.tag)
        if tag not in ALLOWED:
            bad_tags.append(tag)
    if bad_tags:
        return _make("axles-layer-clean", "axles layer contains only ellipse/circle/path + optional north", "advisory",
                     "fail", message=f"Unexpected element types: {', '.join(set(bad_tags))}")
    return _make("axles-layer-clean", "axles layer contains only ellipse/circle/path + optional north", "advisory",
                 "pass", "All elements are ellipse/circle/path")


@register("axles-north-marker-shape", "id='north' is a parseable shape if present", "advisory")
def check_north_shape(analysis):
    inv = analysis.get("layer_id_inventory", {})
    axles_ids = inv.get("axles", [])
    if "north" not in axles_ids:
        return _make("axles-north-marker-shape", "id='north' is a parseable shape if present", "advisory",
                     "skip", message="No north marker in axles layer")
    root = analysis.get("_root")
    if root is None:
        return _make("axles-north-marker-shape", "id='north' is a parseable shape if present", "advisory",
                     "skip", message="SVG root unavailable")
    north_elem = root.find(".//*[@id='north']")
    if north_elem is None:
        return _make("axles-north-marker-shape", "id='north' is a parseable shape if present", "advisory",
                     "error", message="north element listed in inventory but not found in tree")
    tag = _local(north_elem.tag)
    PARSEABLE = {"ellipse", "circle", "rect", "path"}
    if tag in PARSEABLE:
        return _make("axles-north-marker-shape", "id='north' is a parseable shape if present", "advisory",
                     "pass", f"north is <{tag}>")
    return _make("axles-north-marker-shape", "id='north' is a parseable shape if present", "advisory",
                 "fail", message=f"north element is <{tag}>, expected ellipse/circle/rect/path")


@register("mask-elements-ignorable", "mask/mask-N ids appear only inside silhouette", "advisory")
def check_mask_location(analysis):
    inv = analysis.get("layer_id_inventory", {})
    # mask ids in non-silhouette layers
    stray_masks = []
    for layer_id, ids in inv.items():
        if layer_id == "silhouette":
            continue
        for eid in ids:
            if re.match(r"^mask(?:-\d+)?$", eid):
                stray_masks.append(f"{layer_id}/{eid}")
    if stray_masks:
        return _make("mask-elements-ignorable", "mask/mask-N ids appear only inside silhouette", "advisory",
                     "fail", message=f"mask ids outside silhouette: {', '.join(stray_masks)}")
    sil_masks = [i for i in inv.get("silhouette", []) if re.match(r"^mask(?:-\d+)?$", i)]
    return _make("mask-elements-ignorable", "mask/mask-N ids appear only inside silhouette", "advisory",
                 "pass",
                 f"mask ids in silhouette only: {', '.join(sil_masks)}" if sil_masks else "No mask ids found")


@register("canonical-layer-names-only", "All top-level <g> ids are canonical or mask/mask-N", "advisory")
def check_canonical_names(analysis):
    off = analysis.get("off_spec_layers", [])
    if off:
        return _make("canonical-layer-names-only", "All top-level <g> ids are canonical or mask/mask-N", "advisory",
                     "fail", message=f"Non-canonical top-level groups: {', '.join(off)}")
    return _make("canonical-layer-names-only", "All top-level <g> ids are canonical or mask/mask-N", "advisory",
                 "pass", "All top-level named groups are canonical")


@register("no-stray-paths-at-root", "No <path> elements directly under <svg>", "advisory")
def check_no_stray_paths(analysis):
    root = analysis.get("_root")
    if root is None:
        return _make("no-stray-paths-at-root", "No <path> elements directly under <svg>", "advisory",
                     "skip", message="SVG root unavailable")
    stray = [e for e in root if _local(e.tag) == "path"]
    if stray:
        return _make("no-stray-paths-at-root", "No <path> elements directly under <svg>", "advisory",
                     "fail", message=f"{len(stray)} stray <path> element(s) directly under <svg>")
    return _make("no-stray-paths-at-root", "No <path> elements directly under <svg>", "advisory",
                 "pass", "No stray paths at root")


@register("landing-marker-id-format",
          "landing-* ids match landing-<letter><piece-number>[variant] OR landing-<panel-id> format", "advisory")
def check_landing_format(analysis):
    inv = analysis.get("layer_id_inventory", {})
    marks_ids = inv.get("marks", [])
    landing_ids = [i for i in marks_ids if i.startswith("landing-")]
    if not landing_ids:
        return _make("landing-marker-id-format",
                     "landing-* ids match landing-<letter><piece-number>[variant] OR landing-<panel-id> format", "advisory",
                     "skip", message="No landing-* ids in marks layer")
    bad = [i for i in landing_ids if not LANDING_ID_RE.match(i)]
    if bad:
        return _make("landing-marker-id-format",
                     "landing-* ids match landing-<letter><piece-number>[variant] OR landing-<panel-id> format", "advisory",
                     "fail", message=f"Malformed landing ids: {', '.join(bad)}")
    return _make("landing-marker-id-format",
                 "landing-* ids match landing-<letter><piece-number>[variant] OR landing-<panel-id> format", "advisory",
                 "pass", f"All {len(landing_ids)} landing id(s) valid: {', '.join(landing_ids)}")


@register("landing-markers-in-marks-only", "landing-* ids appear only inside marks layer", "advisory")
def check_landing_location(analysis):
    inv = analysis.get("layer_id_inventory", {})
    stray = []
    for layer_id, ids in inv.items():
        if layer_id == "marks":
            continue
        for eid in ids:
            if eid.startswith("landing-"):
                stray.append(f"{layer_id}/{eid}")
    if stray:
        return _make("landing-markers-in-marks-only", "landing-* ids appear only inside marks layer", "advisory",
                     "fail", message=f"landing-* ids outside marks: {', '.join(stray)}")
    marks_landings = [i for i in inv.get("marks", []) if i.startswith("landing-")]
    return _make("landing-markers-in-marks-only", "landing-* ids appear only inside marks layer", "advisory",
                 "pass",
                 f"{len(marks_landings)} landing id(s) in marks" if marks_landings else "No landing ids found")


def run_checks(analysis: dict) -> list[dict]:
    results = []
    for check_id, description, severity, fn in CHECKS:
        try:
            result = fn(analysis)
        except Exception as e:
            result = CheckResult(
                id=check_id, description=description, severity=severity,
                result="error", message=f"check raised exception: {e}",
            )
        results.append(asdict(result))
    return results


# ── stage derivation ──────────────────────────────────────────────────────────

def derive_stage(ps: PieceState) -> str:
    # Check for viewer manifest (future)
    manifest = REPO_ROOT / "work" / "manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text())
            if ps.id in data.get("pieces", {}):
                return "in_viewer"
        except Exception:
            pass

    # Sidecar JSON
    sidecar = REPO_ROOT / "work" / "pieces" / ps.id / f"{ps.id}.json"
    if sidecar.exists():
        return "sidecared"

    # SVG validation
    if ps.convention_checks:
        required_fails = [
            c for c in ps.convention_checks
            if c.get("severity") == "required" and c.get("result") == "fail"
        ]
        if not required_fails and ps.svg_analysis and ps.svg_analysis.get("xml_well_formed"):
            return "svg_validated"

    # SVG with meaningful layers
    if ps.svg_analysis:
        present = set(ps.svg_analysis.get("layers_present", []))
        if "silhouette" in present and present & {"folds-valley", "folds-mountain", "axles"}:
            return "svg_layered"
        return "svg_drafted"

    # Affinity file exists (no SVG exported yet)
    if ps.files["affinity"] and not ps.files["svgs"]:
        return "affinity_started"

    # PNG in source/pieces/
    if ps.files["source_png"]:
        return "captured_only"

    return "pending_capture"


# ── filesystem walk ───────────────────────────────────────────────────────────

def walk_repo(master: dict[str, dict], repo_root: Path) -> tuple[dict[str, PieceState], list[str]]:
    pieces = {pid: PieceState(id=pid, csv_meta=meta) for pid, meta in master.items()}
    repo_anomalies: list[str] = []
    known_ids = set(master.keys())

    # helper: warn on unknown piece id in filename
    def check_known(piece_id: str, context: str):
        if piece_id not in known_ids:
            repo_anomalies.append(f"unknown piece id {piece_id!r} in {context}")

    # ── source/pieces/ ──────────────────────────────────────────────────────
    src_dir = repo_root / "source" / "pieces"
    AF_LOCK = re.compile(r"^(\d{3})([a-z])?(?:-([a-z]+))?\.af~lock~$")

    for p in sorted(src_dir.iterdir()):
        name = p.name
        if name in ("README.md", ".gitkeep") or name.startswith("."):
            continue
        if p.is_dir():
            continue

        m = AF_LOCK.match(name)
        if m:
            pid = m.group(1) + (m.group(2) or "")
            if pid in pieces:
                pieces[pid].anomalies.append(f"affinity-file-open-lock: {name}")
            continue

        m = PIECE_PNG.match(name)
        if m:
            pid = m.group(1) + (m.group(2) or "")
            check_known(pid, f"source/pieces/{name}")
            if pid in pieces:
                pieces[pid].files["source_png"] = f"source/pieces/{name}"
            continue

        m = PIECE_AF.match(name)
        if m:
            pid = m.group(1) + (m.group(2) or "")
            suffix = m.group(3)
            check_known(pid, f"source/pieces/{name}")
            if pid in pieces:
                pieces[pid].files["affinity"].append({"path": f"source/pieces/{name}", "suffix": suffix})
                pieces[pid].anomalies.append(f"af in source/pieces/ (should be in work/pieces/{pid}/)")
            repo_anomalies.append(f".af file in source/pieces/: {name}")
            continue

        m = SVG_FILE.match(name)
        if m:
            pid = m.group(1) + (m.group(2) or "")
            suffix = m.group(3)
            check_known(pid, f"source/pieces/{name}")
            if pid in pieces:
                pieces[pid].files["svgs"].append({"path": f"source/pieces/{name}", "suffix": suffix})
                pieces[pid].anomalies.append(f"svg in source/pieces/ (should be in work/pieces/{pid}/)")
            repo_anomalies.append(f"SVG in source/pieces/: {name}")
            continue

        repo_anomalies.append(f"unrecognized file in source/pieces/: {name}")

    # ── work/pieces/ ────────────────────────────────────────────────────────
    work_pieces_dir = repo_root / "work" / "pieces"
    if work_pieces_dir.exists():
        for d in sorted(work_pieces_dir.iterdir()):
            if not d.is_dir():
                continue
            pid = d.name
            if pid not in known_ids:
                repo_anomalies.append(f"work/pieces/{pid}/ directory has unknown piece id")
                continue
            file_list = [f.name for f in sorted(d.iterdir()) if f.is_file()]
            pieces[pid].files["derivative_dir_files"] = file_list
            # slot SVGs and .af files from direct children of work/pieces/NNN/
            # (subdirectories like _attic/ are not traversed — archive zone)
            for fname in file_list:
                m = SVG_FILE.match(fname)
                if m:
                    sid = m.group(1) + (m.group(2) or "")
                    suffix = m.group(3)
                    if sid == pid or sid.startswith(pid):
                        pieces[pid].files["svgs"].append(
                            {"path": f"work/pieces/{pid}/{fname}", "suffix": suffix}
                        )
                    continue
                m = PIECE_AF.match(fname)
                if m:
                    sid = m.group(1) + (m.group(2) or "")
                    suffix = m.group(3)
                    if sid == pid or sid.startswith(pid):
                        pieces[pid].files["affinity"].append(
                            {"path": f"work/pieces/{pid}/{fname}", "suffix": suffix}
                        )

    # ── source/scans-chunks/ ────────────────────────────────────────────────
    chunks_dir = repo_root / "source" / "scans-chunks"
    if chunks_dir.exists():
        for p in sorted(chunks_dir.iterdir()):
            name = p.name
            if p.is_dir() or name == "README.md":
                continue
            ids = chunk_piece_ids(name)
            if ids:
                for pid in ids:
                    if pid in pieces:
                        pieces[pid].files["chunk_membership"].append(f"source/scans-chunks/{name}")
                    else:
                        check_known(pid, f"source/scans-chunks/{name}")
            # (unrecognized chunk files are not repo anomalies — they may have special names)

    return pieces, repo_anomalies


# ── anomaly detection ─────────────────────────────────────────────────────────

def detect_anomalies(ps: PieceState):
    af_paths = [a["path"] for a in ps.files["affinity"]]

    # duplicate .af across source/pieces/ and inbox/
    source_af = [p for p in af_paths if p.startswith("source/pieces/")]
    inbox_af  = [p for p in af_paths if p.startswith("inbox/")]
    for sa in source_af:
        base_a = Path(sa).name
        for ia in inbox_af:
            base_b = Path(ia).name
            if base_a == base_b:
                if "duplicate-affinity-file" not in ps.anomalies:
                    ps.anomalies.append("duplicate-affinity-file")

    # SVG in multiple folders
    svg_dirs = {str(Path(s["path"]).parent) for s in ps.files["svgs"]}
    if len(svg_dirs) > 1:
        ps.anomalies.append(f"svg-in-multiple-locations: {', '.join(sorted(svg_dirs))}")

    # SVG but no source PNG (orphan derivative)
    if ps.files["svgs"] and not ps.files["source_png"]:
        ps.anomalies.append("svg-present-but-no-source-png")

    # variant .af suffix — informational
    for af in ps.files["affinity"]:
        if af.get("suffix"):
            ps.anomalies.append(f"affinity-variant-suffix: {af['path']} (suffix={af['suffix']!r})")

    # pieces.csv status mismatch
    csv_status = ps.csv_meta.get("status", "")
    if csv_status == "traced" and not ps.files["svgs"]:
        ps.anomalies.append("csv-status-traced-but-no-svg")
    if csv_status == "pending" and ps.files["source_png"]:
        ps.anomalies.append("csv-status-pending-but-png-exists")


# ── SVG picking + full analysis for a piece ──────────────────────────────────

def resolve_primary_svg(svg_list: list[dict], repo_root: Path) -> Optional[str]:
    """Return path (relative to repo_root) of newest SVG in the list."""
    if not svg_list:
        return None
    best_path = None
    best_mtime = -1
    for entry in svg_list:
        p = repo_root / entry["path"]
        try:
            mt = p.stat().st_mtime
            if mt > best_mtime:
                best_mtime = mt
                best_path = entry["path"]
        except FileNotFoundError:
            pass
    return best_path


def build_svg_analysis(ps: PieceState, repo_root: Path) -> Optional[dict]:
    if not ps.files["svgs"]:
        return None
    primary = resolve_primary_svg(ps.files["svgs"], repo_root)
    if not primary:
        return None
    analysis = analyse_svg(primary, repo_root)
    analysis["all_svgs"] = [s["path"] for s in ps.files["svgs"]]
    # strip internal-only key before storing
    analysis.pop("_root", None)
    return analysis


# ── main audit loop ───────────────────────────────────────────────────────────

def run_audit(repo_root: Path) -> dict:
    master = load_master(repo_root)
    assert len(master) == 123, f"Expected 123 pieces in master list, got {len(master)}"

    pieces, repo_anomalies = walk_repo(master, repo_root)

    for pid, ps in pieces.items():
        detect_anomalies(ps)

    # SVG analysis + convention checks
    for pid, ps in pieces.items():
        if ps.files["svgs"]:
            primary = resolve_primary_svg(ps.files["svgs"], repo_root)
            if primary:
                analysis = analyse_svg(primary, repo_root)
                analysis["all_svgs"] = [s["path"] for s in ps.files["svgs"]]

                # run checks before stripping _root
                ps.convention_checks = run_checks(analysis)

                # strip internal keys before storing
                analysis.pop("_root", None)
                analysis.pop("_parse_error", None)
                ps.svg_analysis = analysis

    # derive stages after checks are populated
    for ps in pieces.values():
        ps.stage = derive_stage(ps)

    # ── summary ──────────────────────────────────────────────────────────────
    from collections import Counter
    stage_counts = Counter(ps.stage for ps in pieces.values())

    # convention pass rates (only for pieces with SVGs)
    check_ids = [t[0] for t in CHECKS]
    pass_rates: dict[str, dict] = {cid: {"pass": 0, "fail": 0, "skip": 0, "error": 0, "failing_pieces": []} for cid in check_ids}
    for pid, ps in pieces.items():
        for c in ps.convention_checks:
            cid = c["id"]
            result = c.get("result", "skip")
            if cid in pass_rates:
                bucket = result if result in pass_rates[cid] else "skip"
                pass_rates[cid][bucket] += 1
                if result == "fail":
                    pass_rates[cid]["failing_pieces"].append(pid)

    checks_registry = [
        {"id": t[0], "severity": t[2], "description": t[1]}
        for t in CHECKS
    ]

    summary = {
        "total_pieces": len(pieces),
        "by_stage": dict(stage_counts),
        "convention_pass_rates": pass_rates,
        "repo_anomalies": repo_anomalies,
    }

    return {
        "schema_version": 2,
        "generated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "audit_revision": "2026-05-03",
        "summary": summary,
        "checks_registry": checks_registry,
        "pieces": {pid: asdict(ps) for pid, ps in sorted(pieces.items())},
    }


# ── output formatters ─────────────────────────────────────────────────────────

STAGE_ORDER = [
    "pending_capture", "captured_only", "affinity_started",
    "svg_drafted", "svg_layered", "svg_validated", "sidecared", "in_viewer",
]

STAGE_LABELS = {
    "pending_capture":  "pending_capture     (no PNG yet)",
    "captured_only":    "captured_only       (PNG, nothing further)",
    "affinity_started": "affinity_started    (.af exists, no SVG yet)",
    "svg_drafted":      "svg_drafted         (SVG exists)",
    "svg_layered":      "svg_layered         (silhouette + ≥1 fold/axle layer)",
    "svg_validated":    "svg_validated       (all required checks pass)",
    "sidecared":        "sidecared           (piece-NNN.json exists)",
    "in_viewer":        "in_viewer           (in viewer manifest)",
}


def print_summary(state: dict):
    summary = state["summary"]
    print(f"\nAsset state audit — z-paper-clock")
    print(f"Generated {state['generated_at']}")
    print(f"\nPieces by stage ({summary['total_pieces']} total):")
    by_stage = summary["by_stage"]
    for s in STAGE_ORDER:
        n = by_stage.get(s, 0)
        if n:
            print(f"  {STAGE_LABELS[s]:<50}  {n:>4}")

    rates = summary["convention_pass_rates"]
    pieces_with_svgs = sum(
        1 for p in state["pieces"].values() if p.get("svg_analysis")
    )
    if pieces_with_svgs:
        print(f"\nConvention checks ({pieces_with_svgs} piece(s) with SVG):")
        for check_id, counts in rates.items():
            total_checked = counts["pass"] + counts["fail"] + counts["error"]
            if total_checked == 0:
                continue
            fails = counts["fail"]
            fail_info = ""
            if fails and counts["failing_pieces"]:
                fail_info = f"  (fail: {', '.join(counts['failing_pieces'][:5])})"
            print(f"  {check_id:<40}  {counts['pass']}/{total_checked} pass{fail_info}")

    anomalies = summary.get("repo_anomalies", [])
    all_piece_anomalies = [
        f"[{pid}] {a}"
        for pid, p in sorted(state["pieces"].items())
        for a in p.get("anomalies", [])
    ]
    if anomalies or all_piece_anomalies:
        print("\nAnomalies:")
        for a in anomalies:
            print(f"  - {a}")
        for a in all_piece_anomalies:
            print(f"  - {a}")

    out = REPO_ROOT / "work" / "state.json"
    print(f"\nWrote {out}")
    print(f"Run with --piece NNN for per-piece detail.")


def print_piece_detail(pid: str, state: dict):
    if pid not in state["pieces"]:
        # try zero-padded
        pid_pad = f"{int(re.sub('[a-z]', '', pid)):03d}" + re.sub(r'\d', '', pid)
        if pid_pad in state["pieces"]:
            pid = pid_pad
        else:
            print(f"Piece {pid!r} not found in master list.")
            sys.exit(1)
    piece = state["pieces"][pid]
    print(json.dumps(piece, indent=2))


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="z-paper-clock asset-state audit")
    parser.add_argument("--quiet", action="store_true", help="Suppress human-readable summary")
    parser.add_argument("--piece", metavar="ID", help="Print detail for one piece; no file write")
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if any required check fails on any piece")
    args = parser.parse_args()

    state = run_audit(REPO_ROOT)

    if args.piece:
        print_piece_detail(args.piece, state)
        return

    out_path = REPO_ROOT / "work" / "state.json"
    out_path.write_text(json.dumps(state, indent=2, sort_keys=False) + "\n")

    if not args.quiet:
        print_summary(state)

    if args.check:
        for pid, piece in state["pieces"].items():
            for c in piece.get("convention_checks", []):
                if c.get("severity") == "required" and c.get("result") == "fail":
                    print(f"REQUIRED check failed on piece {pid}: {c['id']}", file=sys.stderr)
                    sys.exit(1)


if __name__ == "__main__":
    main()
