# Refactor Sequence Plan

## Phase 1: Onshape validation

- Paste `feature_scripts/tributary_generator.fs` into Onshape.
- Resolve import/version/syntax issues first.
- Validate selected-plane sketch creation.
- Validate variable names and units.
- Confirm branch/circle counts against Python reference outputs.

## Phase 2: Parity fixtures

- Save known-good GUI/Python scenarios.
- Capture matching Onshape screenshots or exported DXF snapshots.
- Add a parity document with expected geometry counts and visual comparisons.

## Phase 3: GUI polish

- Add optional thumbnail generation for parameter-space maps.
- Add more visual styling controls.
- Add branch highlighting by source/target pair.
- Consider a Qt/PySide version only if dependency installation is acceptable.

## Phase 4: CAD production readiness

- Add manufacturability constraints.
- Add collision/spacing checks.
- Add export workflow from chosen GUI scenarios to final Onshape variable sets.
