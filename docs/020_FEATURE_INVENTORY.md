# Feature Inventory

## Reviewer entry point

- `launch_tributary_generator.bat` launches the GUI from the repository root.
- The launcher sets `PYTHONPATH` to `./src` so reviewers do not need to know Python package import details.

## Live Python GUI

Implemented in:

```text
src/tributary_geometry/gui_app.py
```

Current GUI features:

- central tributary preview canvas;
- zoom, pan, fit-to-view, and reset zoom;
- grid, labels, centerline, Bezier control-polygon, and symmetry-midline toggles;
- top File, View, Settings, Run, and Help menus;
- dockable/detachable control panel;
- Parameters tab exposing every recovered `TributaryConfig` field;
- LFO Animation tab with four automation slots;
- LFO waveforms: sine, square, saw, triangle, random-hold, and noise;
- bounded two-variable parameter-space CSV mapping with CFD-screening metrics;
- CFD Metrics tab with geometry, hydraulic-diameter, resistance-proxy, curvature, and symmetry summaries;
- SVG, JSON, CSV, Onshape-variable-table, and CFD-metrics exports;
- scenario save/load;
- autosave/restore;
- demo scenario file at `examples/gui_demo_scenario.json`;
- log panel.

## Python geometry engine

Implemented in:

```text
src/tributary_geometry/layout.py
src/tributary_geometry/bezier.py
src/tributary_geometry/config.py
src/tributary_geometry/exporters.py
src/tributary_geometry/metrics.py
```

Current geometry features:

- feed line generation;
- dump line generation;
- central alternating snake/ladder line generation;
- recovered top/bottom feed-circle left-shift option;
- default y-aligned physical pairing: feed-to-interior-snake and dump-to-ladder tributary branches;
- retained literal recovered-docx mode: feed-to-ladder and dump-to-snake tributary branches;
- top, bottom, and diagnostic centerline Bezier curves;
- rectangular d_M1/d_M2 Bezier control handles;
- explicit y=0 middle symmetry handling and symmetry-error metrics;
- first-pass CFD screening metrics;
- JSON serialization;
- SVG preview export;
- CSV sampled-curve export;
- Onshape variable-table export.
- CFD metrics JSON/CSV/TXT export.

## Onshape FeatureScript candidate

Implemented in:

```text
feature_scripts/tributary_generator.fs
```

Current FeatureScript intent:

- selected planar-face input;
- variable-driven tributary layout;
- sketch creation on selected plane;
- construction circles for feed/dump/snake/ladder geometry;
- Bezier tributary boundary construction;
- optional construction/control geometry.

## Diagnostics and tests

- `tests/test_geometry.py` validates the geometry engine, default recovered counts, Bezier handles, and symmetry metrics.
- `tests/test_gui_static.py` checks that the GUI exposes all config fields and constrains LFOs to numeric variables.
- `tests/smoke_test.py` generates local preview artifacts.
- `tools/diagnostic_harness.py` writes a diagnostic report and export bundle.
- `tools/structure_audit.py` checks package completeness and excludes stale files.

## Explicit non-features

- The GUI is not a replacement for Onshape.
- The GUI does not prove FeatureScript compile success.
- The panel system is practical dock/detach behavior, not a full drag-and-drop CAD docking framework.
- The parameter-space mapper exports metrics; it is not an optimizer.
