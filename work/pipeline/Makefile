.PHONY: crop trace layers validate pieces clean

PYTHON := ../../.venv/bin/python

crop:
	$(PYTHON) 01-crop.py

trace: crop
	$(PYTHON) 02-trace.py

layers: trace
	$(PYTHON) 03-layer-split.py

validate:
	$(PYTHON) 04-validate-sidecars.py

pieces: crop trace layers validate

clean:
	find ../../work/pieces -name "crop.png" -delete
	find ../../work/pieces -name "raw.svg" -delete
	find ../../work/pieces -name "bitmap.png" -delete
	find ../../work/pieces -name "piece-*.svg" -delete
