# Tributary Generator for Onshape FeatureScript

This repository is a clean, portfolio-ready package for an automated CAD tributary generator developed for Onshape FeatureScript.

The project generates a repeatable tributary/channel sketch pattern from variable-driven circle rows and Bezier branches. It is intended for CAD flow-field/channel-layout exploration where the geometry should be regenerated from parameters instead of manually redrawn.

## Fastest way to review it

On Windows, extract the package and run this from the repository root:

```bat
launch_tributary_generator.bat
```

That launches the live Python preview GUI. The GUI is the easiest way to see what the generator does before reading the FeatureScript.

## Where to look first

For a portfolio or interview review, start with these files:

```text
launch_tributary_generator.bat
README_START_HERE.md
PORTFOLIO_REVIEW_GUIDE.md
src/tributary_geometry/gui_app.py
src/tributary_geometry/layout.py
feature_scripts/tributary_generator.fs
examples/generated_reference/tributary_layout.svg
examples/generated_reference/tributary_layout.png
examples/generated_reference/cfd_metrics_summary.txt
docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md
docs/160_GUI_LAUNCHER_AND_PREVIEW.md
```

The main Onshape code is:

```text
feature_scripts/tributary_generator.fs
```

The main local geometry generator is:

```text
src/tributary_geometry/layout.py
```

The interactive preview application is:

```text
src/tributary_geometry/gui_app.py
```

## What it does

The generator builds:

- a feed circle line;
- a dump circle line;
- a central alternating snake/ladder circle line;
- top and bottom Bezier boundaries connecting feed circles to interior snake circles in the default physical/symmetric mode;
- top and bottom Bezier boundaries connecting dump circles to ladder circles in the default physical/symmetric mode;
- optional diagnostic centerlines and Bezier control information.

The Python package mirrors the same geometry so the tributary pattern can be previewed before testing in Onshape.

## Live GUI preview

The GUI provides:

- a central live geometry preview canvas;
- top File, View, Settings, Run, and Help menus;
- dockable or detachable panels;
- controls for every recovered geometry parameter;
- LFO automation for selected numeric parameters using sine, square, saw, triangle, random-hold, and noise waveforms;
- real-time redraw while parameters or LFOs change;
- parameter-space CSV mapping within bounded ranges, including CFD-screening metrics;
- a CFD Metrics panel with centerline length, width, hydraulic diameter, relative resistance proxy, curvature proxy, and symmetry error;
- scenario save/load plus autosave/restore;
- demo scenario file at `examples/gui_demo_scenario.json`;
- SVG, JSON, CSV, Onshape-variable-table, CFD-metrics, and branch-metrics exports.

The GUI intentionally uses standard-library Tkinter so a reviewer does not need to install Qt just to open the preview.

## How it works with Onshape

The Onshape FeatureScript expects a selected planar face and a set of Onshape variables, such as:

```text
Channel_Num_Snakes
Manifold_Length
Manifold_Reduction
Ladder_Width
FeedDump_Offset
Tributary_Offset
Feed_Diameter
Dump_Diameter
Snake_Width
d_snake_M1
d_snake_M2
d_ladder_M1
d_ladder_M2
```

The FeatureScript creates a sketch on the selected plane and draws the construction circles plus Bezier tributary boundaries.

## Command-line preview workflow

The BAT launcher is the recommended reviewer path. The CLI is still available for repeatable diagnostics:

```bat
set PYTHONPATH=%CD%\src
python -m tributary_geometry.cli --config examples\tributary_example_config.json --out reports\example_run
```

Open this file to preview the generated tributaries:

```text
reports/example_run/tributary_layout.svg
```

The command also writes JSON, CSV, an Onshape variable table, PNG preview when CairoSVG is available, CFD-screening metrics, and a diagnostic report.

## Testing and diagnostics

From the repository root:

```bat
set PYTHONPATH=%CD%\src
python tests\smoke_test.py
python -m unittest discover -s tests
python tools\diagnostic_harness.py
python tools\structure_audit.py
```

## Current status

The Python geometry generator, live GUI module import checks, smoke test, unit tests, diagnostic harness, CLI generation, PNG/SVG preview generation, CFD metric exports, and structure audit pass locally.

The FeatureScript is still a reconstructed clean baseline and must be validated inside Onshape. That limitation is documented directly instead of hidden. FeatureScript syntax, Id handling, unit handling, and sketch creation were recurring problems during development. See:

```text
docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md
```

## Repository hygiene

This package intentionally excludes old drafts, failed experiments, caches, local CAD exports, and bad files. Historical feature names are documented for traceability, but the old draft files are not included.
