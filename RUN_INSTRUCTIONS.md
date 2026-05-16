# Run Instructions

## Recommended Windows launch

From the extracted repository root, double-click or run:

```bat
launch_tributary_generator.bat
```

The BAT file sets `PYTHONPATH` to `./src` and launches the live GUI:

```text
tributary_geometry.gui_app
```

This is the intended reviewer-facing entry point.

## Manual GUI launch

```bat
cd /d C:\path\to\20260516_02_tributary-generator-gui
set PYTHONPATH=%CD%\src
python -m tributary_geometry.gui_app
```

## Command-line diagnostic generation

```bat
cd /d C:\path\to\20260516_02_tributary-generator-gui
set PYTHONPATH=%CD%\src
python -m tributary_geometry.cli --config examples\tributary_example_config.json --out reports\example_run
```

Generated files include:

```text
reports/example_run/tributary_layout.svg
reports/example_run/tributary_layout.json
reports/example_run/tributary_branch_samples.csv
reports/example_run/onshape_variable_table.txt
reports/example_run/diagnostic_report.txt
```

## Direct-file note

Running a package module by full file path can break relative imports in Python packages. This package now includes a direct-run fallback in `layout.py`, but the intended workflow is still the BAT launcher or `python -m ...` commands from the repo root.
