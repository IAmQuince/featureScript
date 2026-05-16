# Module Boundary Specification

## Root launcher

`launch_tributary_generator.bat` is the reviewer-facing entry point. It owns:

- changing to the repository root;
- setting `PYTHONPATH` to `./src`;
- launching `tributary_geometry.gui_app`;
- reporting launch failures clearly.

It does not contain geometry logic.

## GUI layer

`src/tributary_geometry/gui_app.py` owns:

- the Tkinter application shell;
- top menus;
- central preview canvas;
- dockable/detachable panels;
- parameter controls;
- LFO animation;
- parameter-space mapping;
- scenario persistence;
- export commands;
- reviewer-visible logs.

The GUI must call the geometry engine rather than duplicating layout rules.

## Geometry layer

`src/tributary_geometry/layout.py` owns:

- converting `TributaryConfig` into circles and tributary branches;
- recovered layout rules;
- branch count and circle alignment;
- source/target selection for feed-to-ladder and dump-to-snake branches.

`src/tributary_geometry/bezier.py` owns Bezier control-point construction and curve sampling.

`src/tributary_geometry/config.py` owns input definitions and validation.

## Export layer

`src/tributary_geometry/exporters.py` owns SVG, JSON, and CSV exports.

`src/tributary_geometry/featurescript_export.py` owns Onshape variable-table export.

## FeatureScript layer

`feature_scripts/tributary_generator.fs` owns the Onshape-side implementation candidate.

It must stay traceable to the Python geometry rules but cannot be fully verified by local Python tests.

## Tooling layer

`tests/` and `tools/` own local validation, diagnostics, and package structure checks.

They do not validate FeatureScript syntax inside Onshape.
