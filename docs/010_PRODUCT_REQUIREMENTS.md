# Product Requirements

## Purpose

The Tributary Generator package shall demonstrate a parameter-driven CAD workflow for generating tributary flow-field geometry intended for Onshape FeatureScript.

The package shall also provide a local Python preview environment so geometry can be inspected and tuned before Onshape-side validation.

## Portfolio goals

The package shall make it obvious to a reviewer:

1. what the project does;
2. where the main code lives;
3. how to launch the interactive preview;
4. how the Python geometry mirrors the FeatureScript intent;
5. what has been locally tested;
6. what remains unvalidated inside Onshape;
7. what syntax/debugging problems occurred during development.

## Functional requirements

### Launcher

- The repository shall include one clear Windows launcher at the root: `launch_tributary_generator.bat`.
- The launcher shall set local import paths correctly.
- The launcher shall start the GUI without requiring the reviewer to run a package module by file path.

### Python geometry engine

- The package shall generate feed, dump, snake, and ladder construction circle rows.
- The package shall generate feed-to-ladder and dump-to-snake tributary branches.
- Each tributary branch shall include top and bottom Bezier boundaries.
- Each tributary branch shall include a diagnostic centerline.
- The geometry engine shall validate invalid or nonphysical parameter combinations.

### GUI preview

- The GUI shall provide a main central preview screen.
- The GUI shall provide top-level menus.
- The GUI shall provide dockable or detachable control panels.
- The GUI shall expose every recovered geometry parameter available in `TributaryConfig`.
- The GUI shall redraw the geometry in near real time when parameters change.
- The GUI shall allow bounded parameter-space mapping to CSV.
- The GUI shall support LFO animation of selected numeric parameters.
- The GUI shall support sine, square, saw, triangle, random-hold, and noise waveforms.
- The GUI shall export SVG, JSON, CSV samples, and Onshape variable tables.
- The GUI shall support scenario save/load and autosave/restore.

### Onshape FeatureScript

- The FeatureScript candidate shall remain in `feature_scripts/tributary_generator.fs`.
- The FeatureScript shall be documented as requiring Onshape-side compile/regeneration validation.
- Known FeatureScript syntax hazards shall be documented openly.

## Nonfunctional requirements

- The package shall be GitHub-ready and exclude stale drafts, caches, and bad files.
- The package shall be understandable without chat history.
- The GUI shall use no external runtime dependency beyond standard Python/Tkinter.
- Diagnostics shall produce text artifacts suitable for copy/paste review.
- Documentation shall not hide known limitations.
