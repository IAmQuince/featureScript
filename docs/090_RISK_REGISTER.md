# Risk Register

## R-001: FeatureScript syntax validation remains external

**Risk:** Local Python tests cannot prove that `feature_scripts/tributary_generator.fs` compiles inside Onshape.

**Mitigation:** Keep the Python geometry engine as an executable reference, document the limitation, and validate the FeatureScript directly in Onshape before claiming production readiness.

## R-002: FeatureScript syntax and unit handling were recurring failure points

**Risk:** Id handling, imports, unitful values, and sketch APIs can fail in ways that normal Python tests will not catch.

**Mitigation:** Maintain `docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md`; keep FeatureScript compact; mirror logic in Python; use small Onshape validation increments.

## R-003: GUI and FeatureScript could drift

**Risk:** The GUI/Python preview could evolve away from the FeatureScript implementation.

**Mitigation:** Keep `TributaryConfig` as the single local parameter contract and keep FeatureScript variable names documented/exported.

## R-004: Parameter-space exploration can generate nonphysical layouts

**Risk:** Wide sweeps can create geometry that is technically generated but not useful for CAD.

**Mitigation:** Bound GUI controls, run `TributaryConfig.validate()`, and export space-map status rows rather than silently accepting invalid cases.

## R-005: Tkinter panel docking is not a full CAD docking framework

**Risk:** A reviewer may expect drag-and-drop docking like Qt or a commercial CAD application.

**Mitigation:** Document that the GUI provides practical left/right/bottom/detached panel behavior with no external dependencies.
