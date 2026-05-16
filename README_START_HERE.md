# Start Here

Package: `20260516_03_tributary-generator`

Purpose: clean, GitHub-ready, portfolio-facing package for the Onshape FeatureScript **Tributary Generator**, its auxiliary Python geometry engine, live preview GUI, recovered v1 design basis, and CFD-screening metrics.

## First action

Run:

```bat
launch_tributary_generator.bat
```

This is the single intended Windows launcher. It starts the local live preview GUI and avoids direct-module import errors.

## Review order

1. `launch_tributary_generator.bat` — single reviewer entry point.
2. `PORTFOLIO_REVIEW_GUIDE.md` — fast reviewer map.
3. `src/tributary_geometry/gui_app.py` — live preview GUI with docked panels, LFO animation, and CFD metrics.
4. `src/tributary_geometry/layout.py` — main Python geometry generator and recovered symmetry/pairing logic.
5. `src/tributary_geometry/metrics.py` — CFD-screening and symmetry metrics.
6. `feature_scripts/tributary_generator.fs` — main Onshape FeatureScript candidate.
7. `references/recovered_tributary_v1_notes.md` — recovered v1 design basis.
8. `examples/generated_reference/tributary_layout.png` — locally generated verification preview.
9. `examples/generated_reference/cfd_metrics_summary.txt` — locally generated metrics report.
10. `docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md` — candid FeatureScript debugging history.
11. `tests/` and `tools/` — local validation.

The Python GUI and generator are the executable local references. The FeatureScript is the Onshape implementation candidate and must still be validated inside Onshape.
