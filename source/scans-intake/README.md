# scans-intake/ — Drop folder for in-flight scans

Raw output from the home scanner lands here first, then gets promoted into `source/scans-raw/` after passing the QC checks in `source/SCAN-INTAKE-CHECKLIST.md`.

## Why a separate intake folder

Keeps `source/scans-raw/` clean. When the scanner produces a too-dark, off-center, or upside-down output, it sits here until corrected — never enters the canonical tree. Once a file passes intake, it gets renamed (per `inventory.md`) and moved to `scans-raw/`.

## Workflow

```
home scanner →  source/scans-intake/Scan_001.jpg
                source/scans-intake/Scan_002.jpg
                                    ↓
                   QC checks (see SCAN-INTAKE-CHECKLIST.md)
                                    ↓
                rename + move to source/scans-raw/p00x-plate-A-...jpg
                                    ↓
                run preprocess_scans.py to populate scans-clean/ and scans-prepped/
```

## Don't commit raw scanner output

Files in `scans-intake/` are temporary by design. Once promoted to `scans-raw/`, delete the intake copy. The repo tracks the canonical post-intake versions only.
