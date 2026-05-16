# Decision Log

## D-001: Keep only the clean FeatureScript candidate

Old draft FeatureScript names are documented but not included as source files. The clean candidate is `feature_scripts/tributary_generator.fs`.

## D-002: Use Python as the local executable geometry reference

FeatureScript cannot be validated locally in this package, so the geometry rules are mirrored in Python for inspection, tests, and exports.

## D-003: Add a single Windows BAT launcher

A single root-level `launch_tributary_generator.bat` is included so reviewers do not need to understand package-relative imports or command syntax.

## D-004: Use Tkinter for the GUI

The live preview GUI uses Python's standard-library Tkinter stack. This avoids requiring Qt/PySide installation for a portfolio reviewer. The tradeoff is that docking is practical left/right/bottom/detached behavior, not a full CAD-grade drag-and-drop dock framework.

## D-005: Document syntax problems explicitly

FeatureScript syntax issues were a constant development obstacle. The package documents this directly in `docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md` rather than hiding it.

## D-006: Add LFO animation as an exploration tool

The GUI includes LFO automation for numeric parameters to make geometric sensitivity visible in real time. This is exploratory and does not replace formal design optimization.
