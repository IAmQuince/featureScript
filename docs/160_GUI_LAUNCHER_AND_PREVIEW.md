# GUI Launcher and Live Preview

## Reviewer-facing entry point

Run the package from the repository root with:

```bat
launch_tributary_generator.bat
```

That BAT file is the intended single entry point for a reviewer. It sets `PYTHONPATH` to the local `src` folder and launches:

```text
tributary_geometry.gui_app
```

The launcher avoids the earlier confusion where a package module was run as a loose script and relative imports failed.

## What the GUI does

The GUI is a local preview and exploration tool for the tributary generator. It does not require Onshape. It lets a reviewer change the same recovered parameters used by the FeatureScript and immediately see the resulting feed, dump, snake, ladder, and Bezier tributary geometry.

The GUI includes:

- a central live geometry preview canvas;
- top-level File, View, Settings, Run, and Help menus;
- dockable or detachable control panels;
- parameter controls for every recovered `TributaryConfig` field;
- live LFO animation slots for numeric variables;
- waveforms: sine, square, saw, triangle, random-hold, and noise;
- bounded parameter-space CSV mapping;
- exports for SVG, JSON, CSV samples, and Onshape variable tables;
- scenario save/load plus autosave/restore;
- a log panel for reviewer-visible diagnostics.

## Why Tkinter instead of Qt

The GUI uses Python's standard-library Tkinter stack intentionally. A richer Qt implementation would be possible, but it would add an installation dependency for a portfolio reviewer. The goal here is for the extracted package to run through one BAT file on a normal Python installation.

The panel system supports practical docking positions: left, right, bottom, and detached. It is not a full CAD-grade drag-and-drop docking framework.

## Relationship to Onshape

The GUI previews the Python geometry engine. The FeatureScript remains the Onshape implementation candidate. The GUI is useful before Onshape because it lets the user tune geometry visually, export an Onshape variable table, and detect obviously bad parameter combinations before opening the CAD environment.

## Honest limitation

The GUI validates and previews the Python geometry. It does not prove that the companion FeatureScript compiles inside Onshape. That Onshape-side validation remains an explicit package limitation.
