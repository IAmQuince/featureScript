# tributary_geometry Python Package

This package is the local executable reference for the Tributary Generator.

## Main modules

- `gui_app.py` — live preview GUI launched by `launch_tributary_generator.bat`.
- `layout.py` — main geometry generator, including recovered circle counts, pairing modes, and middle symmetry.
- `bezier.py` — cubic Bezier math and rectangular `d_M1`/`d_M2` control-point construction.
- `metrics.py` — CFD-screening and symmetry metrics.
- `config.py` — parameter dataclass and validation.
- `exporters.py` — SVG/PNG/JSON/CSV/metrics exports.
- `featurescript_export.py` — Onshape variable-table export.
- `cli.py` — command-line artifact generator.

## Why this package exists

FeatureScript was difficult to debug locally because syntax, unitful values, and Onshape sketch APIs cannot be fully exercised outside Onshape. This Python package provides a testable geometry mirror so the tributary pattern can be previewed, exported, animated, measured, and diagnosed before CAD-side validation.

## Geometry model

The default mode is `y_aligned_physical`:

- feed circles connect to interior snake circles;
- dump circles connect to ladder circles;
- branches are built from top and bottom Bezier boundaries;
- rectangular construction handles follow the recovered `d_M1` / `d_M2` diagram;
- symmetry is checked about `y = 0`.

The alternate `recovered_docx_v1` pairing is retained for traceability to the older document, but it is not the default portfolio view.

## GUI launch

Use the root-level launcher:

```bat
launch_tributary_generator.bat
```

The GUI exposes every `TributaryConfig` parameter, redraws in real time, supports LFO animation, reports CFD-screening metrics, and exports reviewer/CAD setup artifacts.

## CLI launch

```bat
set PYTHONPATH=%CD%\src
python -m tributary_geometry.cli --config examples\tributary_example_config.json --out reports\example_run
```

The CLI writes SVG/PNG/JSON/CSV previews, a pairing table, an Onshape variable table, and CFD-screening metrics.
