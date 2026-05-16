# Acceptance Test Plan

## Local acceptance scope

Local acceptance can validate:

- Python package imports;
- geometry generation;
- configuration validation;
- Bezier curve construction;
- SVG/JSON/CSV/Onshape-variable-table exports;
- GUI static contract coverage;
- package structure and required files;
- diagnostic harness execution.

Local acceptance cannot validate Onshape FeatureScript compile or regeneration behavior.

## Commands

Run from repository root:

```bat
set PYTHONPATH=%CD%\src
python tests\smoke_test.py
python -m unittest discover -s tests
python tools\diagnostic_harness.py
python tools\structure_audit.py
```

## GUI reviewer acceptance

Manual GUI check:

1. Run `launch_tributary_generator.bat`.
2. Confirm the central preview appears.
3. Change `Channel count / snakes` and confirm the branch/circle count changes.
4. Change offsets and Bezier M values and confirm the preview redraws.
5. Enable an LFO slot and run animation.
6. Dock the panel left/right/bottom and detach it.
7. Export SVG, JSON, CSV, and Onshape variable table.
8. Save and reload a scenario JSON.
9. Generate a parameter-space map CSV.

## Pass criteria

- Unit tests pass.
- Smoke test writes preview artifacts.
- Diagnostic harness writes a diagnostic report.
- Structure audit passes.
- GUI static test confirms parameter exposure.
- Manual GUI launch opens and redraws geometry.
- FeatureScript limitation remains documented.
