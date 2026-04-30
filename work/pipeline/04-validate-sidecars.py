"""
Lint every work/pieces/NNN/piece-NNN.json sidecar.

Checks:
  1. JSON parses
  2. Required fields are present
  3. id matches filename
  4. plate matches pieces.csv
  5. connections are reciprocal (skipped if referenced piece has no sidecar yet)
  6. axle ids are referenced by at least one other sidecar (skipped if not yet present)

Exit code 0 if no ERRORs; non-zero if any ERROR exists (WARNs do not fail).
"""

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PIECES_DIR = REPO / "work" / "pieces"
PIECES_CSV = REPO / "work" / "pieces.csv"

REQUIRED_FIELDS = [
    "id",
    "plate",
    "name",
    "role",
    "material",
    "extrudeMm",
    "connections",
    "folds",
    "axles",
    "introducedInStep",
    "figureRefs",
    "notes",
]

VALID_MATERIALS = {"paper", "cardboard-1mm", "wire", "knitting-needle-2mm"}


def load_csv_plates() -> dict[int, str]:
    plates: dict[int, str] = {}
    if not PIECES_CSV.exists():
        return plates
    with PIECES_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            plates[int(row["id"])] = row["plate"]
    return plates


def find_sidecars() -> list[Path]:
    sidecars = []
    for d in sorted(PIECES_DIR.iterdir()):
        if not d.is_dir():
            continue
        expected = d / f"piece-{d.name}.json"
        if expected.exists():
            sidecars.append(expected)
    return sidecars


def main():
    sidecars = find_sidecars()
    if not sidecars:
        print("No sidecars found. Nothing to validate.")
        print("(Run the Cowork sidecar-authoring session to create piece-NNN.json files.)")
        sys.exit(0)

    csv_plates = load_csv_plates()

    # Load all parseable sidecars for cross-reference checks
    all_data: dict[int, dict] = {}
    for path in sidecars:
        try:
            data = json.loads(path.read_text())
            if isinstance(data.get("id"), int):
                all_data[data["id"]] = data
        except Exception:
            pass

    errors: list[str] = []
    warnings: list[str] = []
    results: list[str] = []
    pass_count = 0
    fail_count = 0
    warn_count = 0

    for path in sidecars:
        fname = path.name
        piece_errors: list[str] = []
        piece_warns: list[str] = []

        # 1. JSON parses
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            results.append(f"{fname}  ERROR: invalid JSON — {e}")
            fail_count += 1
            continue

        # 2. Required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                piece_errors.append(f'missing required field "{field}"')

        # 3. id matches filename (piece-NNN.json -> id = NNN as int)
        expected_id = int(path.parent.name)
        if "id" in data:
            if data["id"] != expected_id:
                piece_errors.append(
                    f'id {data["id"]} does not match filename (expected {expected_id})'
                )

        # 4. material is valid
        if "material" in data and data["material"] not in VALID_MATERIALS:
            piece_errors.append(
                f'material "{data["material"]}" not one of {sorted(VALID_MATERIALS)}'
            )

        # 5. folds has valley and mountain arrays
        if "folds" in data:
            folds = data["folds"]
            if not isinstance(folds, dict):
                piece_errors.append('"folds" must be an object')
            else:
                for key in ("valley", "mountain"):
                    if key not in folds:
                        piece_errors.append(f'"folds" missing "{key}" array')

        # 6. plate matches pieces.csv
        if "id" in data and "plate" in data:
            piece_id = data["id"]
            if piece_id in csv_plates:
                if data["plate"] != csv_plates[piece_id]:
                    piece_errors.append(
                        f'plate "{data["plate"]}" does not match pieces.csv plate '
                        f'"{csv_plates[piece_id]}"'
                    )

        # 7. Connections reciprocal (warn if referenced piece sidecar is absent)
        if "connections" in data and isinstance(data["connections"], list):
            for conn in data["connections"]:
                if not isinstance(conn, dict):
                    continue
                to_id = conn.get("to")
                at_tab = conn.get("atTab")
                tab = conn.get("tab")
                if to_id is None:
                    continue
                if conn.get("reciprocal") is False:
                    pass  # intentionally one-directional; no reciprocation expected
                elif to_id not in all_data:
                    piece_warns.append(
                        f"connection to piece {to_id} not reciprocable "
                        f"(piece {to_id:03d} sidecar not found)"
                    )
                else:
                    other = all_data[to_id]
                    other_conns = other.get("connections", [])
                    matches = [
                        c for c in other_conns
                        if isinstance(c, dict)
                        and c.get("to") == expected_id
                        and (at_tab is None or c.get("tab") == at_tab)
                    ]
                    if not matches:
                        piece_errors.append(
                            f"connection to piece {to_id} (tab={tab!r}, atTab={at_tab!r}) "
                            f"is not reciprocated in piece-{to_id:03d}.json"
                        )

        # 8. Axle ids referenced by at least one other sidecar
        if "axles" in data and isinstance(data["axles"], list):
            for axle in data["axles"]:
                if not isinstance(axle, dict):
                    continue
                axle_id = axle.get("id")
                if axle_id is None:
                    continue
                referenced_elsewhere = any(
                    other_id != expected_id
                    and any(
                        a.get("id") == axle_id
                        for a in other.get("axles", [])
                        if isinstance(a, dict)
                    )
                    for other_id, other in all_data.items()
                )
                if not referenced_elsewhere:
                    if axle_id not in all_data:
                        piece_warns.append(
                            f"axle id {axle_id!r} not referenced by any other sidecar "
                            f"(other piece sidecar may not exist yet)"
                        )
                    else:
                        piece_errors.append(
                            f"axle id {axle_id!r} is not referenced by any other sidecar"
                        )

        if piece_errors:
            for msg in piece_errors:
                results.append(f"{fname}  ERROR: {msg}")
            fail_count += 1
        elif piece_warns:
            for msg in piece_warns:
                results.append(f"{fname}  WARN: {msg}")
            warn_count += 1
            pass_count += 1
        else:
            results.append(f"{fname}  OK")
            pass_count += 1

    for line in results:
        print(line)

    total = pass_count + fail_count
    print(
        f"\nSummary: {pass_count} pass, {fail_count} fail, {warn_count} warn."
    )

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
