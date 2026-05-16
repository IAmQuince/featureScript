# Portfolio Review Guide

This package is meant to be understandable without chat history.

## One-minute summary

**Tributary Generator** is an automated CAD geometry generator for Onshape FeatureScript. It creates a structured tributary/channel pattern from variable-driven circle rows and Bezier branches. The package also includes a Python geometry engine and live GUI so the tributaries can be inspected and tuned as SVG-like preview geometry before Onshape validation.

## Run it first

From the repository root on Windows:

```bat
launch_tributary_generator.bat
```

The GUI opens a central preview canvas and a control panel. Change parameters, run LFO animation, dock or detach panels, and export SVG/JSON/CSV/Onshape variable-table artifacts.

## Main code entry points

### Live Python preview GUI

```text
src/tributary_geometry/gui_app.py
```

This is the best first code file for a reviewer because it shows the interactive front end: central canvas, dockable/detachable panels, menus, parameter controls, LFO automation, parameter-space mapping, CFD metrics, exports, logs, scenario persistence, and autosave.

### Python geometry generator

```text
src/tributary_geometry/layout.py
```

This is the local geometry engine that mirrors the intended FeatureScript. It is easier to test, inspect, and debug than FeatureScript directly.

### Bezier construction helper

```text
src/tributary_geometry/bezier.py
```

This shows the rectangular d_M1/d_M2 curve-control logic used to generate the tributary boundaries.

### CFD/symmetry metrics

```text
src/tributary_geometry/metrics.py
```

This computes first-pass CFD screening metrics: centerline length, channel width, hydraulic diameter, wetted area proxy, resistance proxy, curvature proxy, branch-balance CV, and symmetry error about the recovered midline.

### Onshape FeatureScript

```text
feature_scripts/tributary_generator.fs
```

This is the main CAD automation code. It defines the Onshape feature display name **Tributary Generator** and exports `tributaryGenerator`.

## Generated preview

Open:

```text
examples/generated_reference/tributary_layout.svg
examples/generated_reference/tributary_layout.png
examples/generated_reference/cfd_metrics_summary.txt
```

That SVG is the quickest static artifact for seeing what the generator produces.

## Honest status

The Python package is locally runnable and tested. The GUI uses standard-library Tkinter so it can be launched without a Qt install.

The FeatureScript code is a reconstructed clean baseline and still needs Onshape-side compile/regeneration validation.

FeatureScript syntax issues were a constant development obstacle, especially around import/version syntax, Id-versus-string handling, unitful values, and sketch creation. This is documented in:

```text
docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md
```

## Why this package exists

The package demonstrates a practical engineering workflow:

1. define the CAD pattern parametrically;
2. mirror the geometry in Python for fast preview and diagnostics;
3. provide a live GUI for parameter exploration before CAD regeneration;
4. export SVG/PNG/JSON/CSV/metrics artifacts for review;
5. keep the Onshape FeatureScript implementation traceable;
6. document known limitations instead of burying them.

## Recovered v1 update

The 2026-05-16 update incorporated an older `Tributaryv1.docx` reference. That document made clear that the original implementation had reached the tributary-building section but still needed the branch-pairing and Bezier-boundary logic added. This package now implements that logic in Python and in the FeatureScript candidate, including middle symmetry and CFD-screening metrics.
