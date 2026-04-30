#!/usr/bin/env python3
"""
Build the master pieces.csv from data extracted from
source/transcriptions/embedded-labels.md and instructions.md.

Output schema:
    id, plate, section, bucket, status, notes

- id: zero-padded NNN, plus NNNa for letter variants (092a, 112a)
- plate: A-M (the plate where the piece is primarily printed)
- section: framework | motor-wheel | middle-wheel | escapement
           | anchor-pendulum | hands | reduction-gear | weight
           | face-case | reference
- bucket: auto-trace-clean | auto-trace-edit | hand-trace | (blank)
  Populated only for pieces with a bucket assignment from M1
  (plate D); blank for all others (TBD when each plate is traced).
- status: pending | captured | traced
  All pieces start "pending" — flipped to "captured" by the future
  ingest skill once source/pieces/NNN.png exists.
- notes: free text. Cross-references to glue-mate pieces, multiple
  copies, partner pieces, etc.
"""

# (id, plate, section, bucket, notes)
# Bucket assignments preserved verbatim from the M1 plate-D pieces.csv.
# All other buckets blank — to be assigned per plate as tracing proceeds.

PIECES = [
    # ---- Plate A: 5 pieces ----
    ("001", "A", "framework", "", "U-channel frame strip (long horizontal frame run, paired with 2/6/7 across panels A and B)"),
    ("002", "A", "framework", "", "U-channel frame strip"),
    ("006", "A", "framework", "", "U-channel frame strip"),
    ("007", "A", "framework", "", "U-channel frame strip"),
    ("110", "A", "face-case", "", "Face-frame end rail; X/Y end-match markers to 111/112"),

    # ---- Plate B: 14 unique pieces ----
    ("003", "B", "framework", "", "Vertical frame strip (paired with 1)"),
    ("005", "B", "framework", "", "Vertical frame strip (paired with 2)"),
    ("008", "B", "framework", "", "Vertical frame strip (paired with 6)"),
    ("012", "B", "framework", "", "Bracket piece (12/13/14 top row)"),
    ("013", "B", "framework", "", "Bracket piece"),
    ("014", "B", "framework", "", "Bracket piece"),
    ("015", "B", "framework", "", "Bracket piece (15/16/17 bottom row)"),
    ("016", "B", "framework", "", "Bracket piece"),
    ("017", "B", "framework", "", "Bracket piece"),
    ("093", "B", "anchor-pendulum", "", "Pendulum-bob inner brace; printed as 6 copies, glued in pairs to make 3 braces"),
    ("113", "B", "face-case", "", "Cross-shaped brace piece for face frame (1 of 4: 113-116)"),
    ("114", "B", "face-case", "", "Cross-shaped brace piece for face frame"),
    ("115", "B", "face-case", "", "Cross-shaped brace piece for face frame"),
    ("116", "B", "face-case", "", "Cross-shaped brace piece for face frame"),

    # ---- Plate C: 10 pieces ----
    ("009", "C", "framework", "", "Long vertical frame strip (paired with anchor beam)"),
    ("011", "C", "framework", "", "Long vertical frame strip"),
    ("020", "C", "framework", "", "Long vertical frame strip"),
    ("021", "C", "framework", "", "Folded bracket for wall-bracket assembly"),
    ("022", "C", "framework", "", "Folded bracket; + center mark"),
    ("023", "C", "framework", "", "Wall-bracket box development; tabs to 25"),
    ("024", "C", "framework", "", "Wall-bracket box development; tabs to 25"),
    ("025", "C", "framework", "", "Tall wall-bracket main panel"),
    ("027", "C", "framework", "", "Pendulum-support spacer (small piece carrying '28' label); also appears on plate G"),
    ("028", "C", "framework", "", "Pendulum-support spacer"),

    # ---- Plate D: 11 pieces (bucket assignments preserved from M1) ----
    ("004", "D", "framework", "hand-trace", "Long main frame column (front center); axle holes; positioning guides for 91/92"),
    ("010", "D", "framework", "hand-trace", "Long main frame column (back center)"),
    ("018", "D", "framework", "auto-trace-edit", "Back-of-frame L-bracket; pinches pendulum blade"),
    ("019", "D", "framework", "auto-trace-edit", "Back-of-frame L-bracket; pinches pendulum blade"),
    ("026", "D", "framework", "auto-trace-clean", "Wall-bracket wedge; glue to strong cardboard"),
    ("029", "D", "framework", "auto-trace-edit", "Cross-box flat development (connects 4/10)"),
    ("030", "D", "framework", "auto-trace-edit", "Small box development"),
    ("031", "D", "framework", "auto-trace-clean", "Flat oval/leaf tongue; glue back to back to 32"),
    ("032", "D", "framework", "auto-trace-clean", "Flat elongated oval (pairs with 31); also appears on plate G"),
    ("091", "D", "hands", "auto-trace-clean", "Small square spacer; glue to 1mm cardboard; aligns to piece 4"),
    ("092", "D", "hands", "auto-trace-clean", "Disc spacer; glue to 1mm cardboard; aligns to piece 4"),

    # ---- Plate E: 15 pieces ----
    ("039", "E", "motor-wheel", "", "Accordion-pleated pulley column (glues to 38)"),
    ("060", "E", "escapement", "", "Pinion for escapement wheel (rolled cylinder)"),
    ("074", "E", "anchor-pendulum", "", "Thin strip (hook form) at bottom of plate E; small fragment also visible on H"),
    ("078", "E", "hands", "", "Hour-hand wheel; glue back to back to 79 before cutting teeth"),
    ("079", "E", "hands", "", "Hour-hand wheel partner to 78"),
    ("082", "E", "reduction-gear", "", "Reduction-gear accordion strip"),
    ("083", "E", "reduction-gear", "", "Reduction-gear accordion strip"),
    ("103", "E", "reduction-gear", "", "Small reduction gear with central spiral pattern"),
    ("104", "E", "weight", "", "Weight-cylinder lid disc; glue back to back to 106"),
    ("105", "E", "weight", "", "Sawtooth gear-teeth strip"),
    ("106", "E", "weight", "", "Weight-cylinder lid disc; partner to 104"),
    ("107", "E", "reference", "", "Axle-dimension reference lines + legend (not a build piece)"),
    ("111", "E", "face-case", "", "Face-frame horizontal rail"),
    ("112", "E", "face-case", "", "Face-frame horizontal rail (mirror partner of 112a)"),
    ("112a", "E", "face-case", "", "Face-frame horizontal rail (mirror partner of 112). LETTER VARIANT."),

    # ---- Plate F: 28 pieces ----
    ("038", "F", "motor-wheel", "", "Large motor-wheel front face; central star cut out"),
    ("046", "F", "motor-wheel", "", "Pulley plate (paired with 47, glue back to back)"),
    ("047", "F", "motor-wheel", "", "Pulley plate; partner to 46"),
    ("048", "F", "motor-wheel", "", "Plain disc; glue to double cardboard"),
    ("049", "F", "motor-wheel", "", "Small disc (plate cap); also appears on plate G"),
    ("058", "F", "escapement", "", "Escapement-wheel disc; glue back to back to 59 before cutting"),
    ("059", "F", "escapement", "", "Escapement-wheel disc partner to 58"),
    ("061", "F", "escapement", "", "Star-cutout disc (pinion-stack)"),
    ("062", "F", "escapement", "", "Star-cutout disc"),
    ("063", "F", "escapement", "", "Star-cutout disc"),
    ("064", "F", "escapement", "", "Star-cutout disc"),
    ("065", "F", "anchor-pendulum", "", "Zig-zag anchor arm; 'axe R' label = rear axle"),
    ("066", "F", "anchor-pendulum", "", "Pendulum-blade tube/casing development"),
    ("067", "F", "anchor-pendulum", "", "Rear plate of the anchor; flap labels a-f"),
    ("073", "F", "hands", "", "Star-shaped hands-assembly wheel; cut out center"),
    ("075", "F", "hands", "", "Star-shaped hands-assembly wheel"),
    ("076", "F", "hands", "", "Small rectangular piece for minute-hand assembly"),
    ("077", "F", "hands", "", "Minute-hand holder tube development"),
    ("080", "F", "hands", "", "Small rectangle ('Push into wheel 78'); 'rear' label on one face"),
    ("081", "F", "reduction-gear", "", "Reduction-gear stage piece"),
    ("084", "F", "reduction-gear", "", "Reduction-gear stage piece"),
    ("085", "F", "reduction-gear", "", "Rectangular strip; +++ along length"),
    ("086", "F", "reduction-gear", "", "Reduction-gear stage piece"),
    ("087", "F", "reduction-gear", "", "Reduction-gear disc; cut out center"),
    ("088", "F", "reduction-gear", "", "Pulley/gear stack disc"),
    ("089", "F", "reduction-gear", "", "Pulley disc for hands mechanism; also appears on plate H"),
    ("090", "F", "reduction-gear", "", "Pulley/gear stack disc"),
    ("120", "F", "reference", "", "Axle-mount cardboard square (model for all mounting squares)"),

    # ---- Plate G: 18 pieces (centerfold spread, two-page flat) ----
    ("033", "G", "motor-wheel", "", "Large disc with internal triangle (motor-wheel back face); a35 corner labels"),
    ("034", "G", "motor-wheel", "", "Long zig-zag teeth strip (motor-wheel teeth); engages between 33 and 36"),
    ("035", "G", "motor-wheel", "", "Long zig-zag teeth strip; folds into cone braced by 33's triangle"),
    ("036", "G", "motor-wheel", "", "Large motor-wheel disc with crown-band of vertical hatching (teeth band)"),
    ("037", "G", "motor-wheel", "", "Long thin strip with vertical-hatch (motor-wheel tooth strip)"),
    ("040", "G", "motor-wheel", "", "Pulley cylinder; glue ends together, slip over 39 with arrow toward motor wheel"),
    ("041", "G", "motor-wheel", "", "Pulley shaft; marked end glues to 40 (a/b alignment)"),
    ("042", "G", "motor-wheel", "", "Pulley drum; covers wrapped end of 41; arrow toward motor wheel"),
    ("043", "G", "motor-wheel", "", "Pulley throat (with 44, per Fig. 13)"),
    ("044", "G", "motor-wheel", "", "Pulley bearing disc; pairs with 43 for pulley throat"),
    ("045", "G", "motor-wheel", "", "Short straight strip; wraps around cylinder between 43 and 44"),
    ("050", "G", "middle-wheel", "", "Large disc (back face of middle wheel); glue back to back with 51"),
    ("051", "G", "middle-wheel", "", "Middle-wheel disc; partner to 50"),
    ("052", "G", "middle-wheel", "", "Middle-wheel disc; glues to 51"),
    ("054", "G", "middle-wheel", "", "Star-cut pinion piece"),
    ("055", "G", "middle-wheel", "", "Pinion (with 54-57 stack); pushes through star-shaped hole"),
    ("056", "G", "middle-wheel", "", "Star-cut pinion piece; slips over pinion 55"),
    ("057", "G", "middle-wheel", "", "Star-cut pinion piece; presses against pinion top"),

    # ---- Plate H: 14 pieces (second flat spread) ----
    ("053", "H", "middle-wheel", "", "Small disc with starred center (pinion-mount, middle wheel); also referenced on plate G"),
    ("068", "H", "anchor-pendulum", "", "Anchor fork; passes over beam piece 9"),
    ("069", "H", "anchor-pendulum", "", "Anchor-bearing box; + center mark"),
    ("070", "H", "anchor-pendulum", "", "Pendulum rod (long vertical strip); receives 71 at bottom"),
    ("071", "H", "anchor-pendulum", "", "Square ring; cut out center; glue between b/c of piece 70"),
    ("072", "H", "anchor-pendulum", "", "Pendulum blade with mounting-pin hole; squeeze into 70's slot"),
    ("092a", "H", "hands", "", "Narrow tongue piece; glues on top of 92 and 91 with axle holes coinciding. LETTER VARIANT."),
    ("094", "H", "anchor-pendulum", "", "Pendulum-bob outer casing (long tapered tube)"),
    ("095", "H", "anchor-pendulum", "", "Pendulum hook outer shape; receives 96 in bottom"),
    ("096", "H", "anchor-pendulum", "", "Narrow cardboard reinforcement; glue to 1mm cardboard"),
    ("097", "H", "anchor-pendulum", "", "Pendulum-bob front face (large round disc); 'apply no glue here' inner rectangle"),
    ("098", "H", "anchor-pendulum", "", "Bowed retainer; glues to 97 (bowed when glued, holds bob in place)"),
    ("099", "H", "anchor-pendulum", "", "Saw-toothed crescent (decorative trim)"),
    ("100", "H", "anchor-pendulum", "", "Bob-position disc with F (fast/up) and S (slow/down) arrows"),

    # ---- Plate I: 2 pieces ----
    ("118", "I", "face-case", "", "Case-side panel; * pin-hole markers; glues to b119/c119 underside of 117"),
    ("119", "I", "face-case", "", "Case-side panel; * pin-hole markers; glues to b118/c118 underside of 117"),

    # ---- Plate J: 5 pieces ----
    ("101", "J", "weight", "", "Weight cylinder development (rectangular sheet, multiple horizontal folds)"),
    ("102", "J", "weight", "", "Wide labeled strip wrapped around 101"),
    ("108", "J", "face-case", "", "Minute hand (solid black silhouette); glue on heavy cardboard"),
    ("109", "J", "face-case", "", "Hour hand (solid black silhouette); glue on heavy cardboard"),
    ("117", "J", "face-case", "", "Case top with chamfered corners; central 'front' tab"),

    # ---- Plate M: 1 piece ----
    ("122", "M", "face-case", "", "Clock face: tan/brown border, off-white field, numbers 1-12, minute marks"),
]

HEADER = (
    "# work/pieces.csv — master piece index for the build\n"
    "#\n"
    "# Schema: id, plate, section, bucket, status, notes\n"
    "#\n"
    "# id      Three-digit zero-padded piece number; letter variants append a-z\n"
    "#         (e.g., 004, 092a, 112a, 122). Matches source/pieces/<id>.png.\n"
    "# plate   Letter A-M of the printed plate where the piece primarily appears.\n"
    "#         Some pieces appear on multiple plates as duplicate copies; this\n"
    "#         column records the primary detailed-description plate from\n"
    "#         source/transcriptions/embedded-labels.md. Notes column flags duplicates.\n"
    "# section Functional group: framework | motor-wheel | middle-wheel | escapement\n"
    "#         | anchor-pendulum | hands | reduction-gear | weight | face-case | reference\n"
    "#         (book sections II.A-F, refined). Used by the viewer's hierarchical\n"
    "#         Object3D groups per work/SPEC-3D-VIEWER.md.\n"
    "# bucket  Tracing strategy: auto-trace-clean | auto-trace-edit | hand-trace.\n"
    "#         Populated only for plate D from M1 (gen-1 era); blank for all other\n"
    "#         pieces until each plate's tracing pass assigns one.\n"
    "# status  pending | captured | traced. 'pending' = not yet in source/pieces/;\n"
    "#         flipped to 'captured' by the ingest skill once source/pieces/<id>.png\n"
    "#         lands; 'traced' once work/pieces/<id>/piece-<id>.svg ships.\n"
    "# notes   Free text. Cross-references, glue-mate pieces, partner pieces,\n"
    "#         duplicate copies on other plates, special instructions.\n"
    "#\n"
    "# Generated 2026-04-30 from source/transcriptions/embedded-labels.md +\n"
    "# instructions.md, replacing the gen-1 11-row plate-D bbox table. Bbox columns\n"
    "# are gone: under the chunk-and-crop onboarding model, source/pieces/ already\n"
    "# holds per-piece crops, so the pipeline reads them directly without slicing.\n"
)

def main():
    out_path = "pieces.csv"
    seen_ids = set()
    duplicates = []
    rows = []
    for piece_id, plate, section, bucket, notes in PIECES:
        if piece_id in seen_ids:
            duplicates.append(piece_id)
        seen_ids.add(piece_id)
        # Escape commas/quotes in notes
        if "," in notes or '"' in notes:
            notes_escaped = '"' + notes.replace('"', '""') + '"'
        else:
            notes_escaped = notes
        rows.append(f"{piece_id},{plate},{section},{bucket},pending,{notes_escaped}")

    with open(out_path, "w") as f:
        f.write(HEADER)
        f.write("id,plate,section,bucket,status,notes\n")
        for row in rows:
            f.write(row + "\n")

    print(f"Wrote {len(rows)} rows to {out_path}")
    if duplicates:
        print(f"WARNING: duplicate IDs: {duplicates}")
    print(f"Unique IDs: {len(seen_ids)}")
    # Distribution by plate
    from collections import Counter
    by_plate = Counter(p[1] for p in PIECES)
    print("By plate:")
    for plate in sorted(by_plate.keys()):
        print(f"  {plate}: {by_plate[plate]}")
    by_section = Counter(p[2] for p in PIECES)
    print("By section:")
    for section in sorted(by_section.keys()):
        print(f"  {section}: {by_section[section]}")

if __name__ == "__main__":
    main()
