# Changelog

## 20260516_03 - Recovered v1 tributary logic, symmetry, and CFD metrics

- Incorporated the older `Tributaryv1.docx` design basis into the cleaned package.
- Repaired the tributary geometry so branches are built from paired upper/lower channel boundaries instead of generic centerline-style curves.
- Restored the recovered central grid rule: `2 * Channel_Num_Snakes + 1` central snake/ladder stations.
- Added default `y_aligned_physical` pairing mode for the photo-like physical interpretation and retained `recovered_docx_v1` for traceability.
- Added explicit middle symmetry handling and visual symmetry midline in the GUI/SVG output.
- Updated the Onshape FeatureScript candidate with rectangular `d_M1`/`d_M2` Bezier control logic and a completed tributary-building section.
- Added `src/tributary_geometry/metrics.py` for CFD-screening metrics.
- Added GUI CFD Metrics tab and metrics exports.
- Added CLI metrics outputs: `cfd_metrics_summary.txt`, `cfd_metrics.json`, and `cfd_branch_metrics.csv`.
- Added reference notes and recovered-v1 update documentation.
- Regenerated static reference SVG/PNG/JSON/CSV outputs.
- Updated tests, smoke test, diagnostic harness, structure audit, README, and portfolio guide.


## 20260516_02 - Live GUI launcher package

- Added `launch_tributary_generator.bat` as the single Windows reviewer entry point.
- Added `src/tributary_geometry/gui_app.py`, a standard-library Tkinter live preview GUI.
- Added central live preview canvas with zoom, pan, fit-to-view, grid, labels, centerlines, and optional Bezier control polygons.
- Added dockable/detachable control panel with Parameters, LFO Animation, Space Map, Exports, and Logs tabs.
- Added controls for every recovered geometry parameter in `TributaryConfig`.
- Added four LFO automation slots with sine, square, saw, triangle, random-hold, and noise waveforms.
- Added bounded two-variable parameter-space CSV mapping.
- Added GUI scenario save/load and autosave/restore.
- Added GUI exports for SVG, JSON, CSV samples, and Onshape variable table.
- Added `docs/160_GUI_LAUNCHER_AND_PREVIEW.md`.
- Added `tests/test_gui_static.py`.
- Updated README, start guide, portfolio guide, run instructions, test instructions, feature inventory, and structure audit.
- Added direct-run fallback for `src/tributary_geometry/layout.py` to reduce import confusion.

## 20260516_01 - Portfolio cleanup

- Renamed the FeatureScript to `tributary_generator.fs`.
- Added portfolio-facing review documentation.
- Rebuilt auxiliary Python geometry package.
- Documented FeatureScript syntax and debugging problems candidly.
- Removed stale legacy FeatureScript draft files from the clean package.

## 20260516_00 - Initial recovered tributary baseline

- Reconstructed a clean baseline from recovered tributary rules.
- Added Python preview geometry engine, SVG/JSON/CSV export, tests, and diagnostics.
