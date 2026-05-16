# Local Verification Report

Package: `20260516_03_tributary-generator`
Date: 2026-05-16

## Verification performed

The following local checks were run in the package root with `PYTHONPATH=src`:

```text
python -m compileall -q src tools tests
python -m unittest discover -s tests
python tests/smoke_test.py
python tools/diagnostic_harness.py
python tools/structure_audit.py
python -m tributary_geometry.cli --out reports/verification_run --samples 64
```

## Results

- Python compile check: PASS
- Unit tests: PASS, 8 tests
- Smoke test: PASS
- Diagnostic harness: PASS
- Structure audit: PASS
- CLI generation: PASS
- SVG preview generated: PASS
- PNG preview generated via CairoSVG: PASS
- CFD metrics JSON/CSV/TXT generated: PASS
- Symmetry metric for default scenario: PASS, mean error = 0

## Generated verification artifacts

```text
reports/verification_run/tributary_layout.svg
reports/verification_run/tributary_layout.png
reports/verification_run/tributary_layout.json
reports/verification_run/tributary_branch_samples.csv
reports/verification_run/branch_pairing_table.csv
reports/verification_run/onshape_variable_table.txt
reports/verification_run/cfd_metrics_summary.txt
reports/verification_run/cfd_metrics.json
reports/verification_run/cfd_branch_metrics.csv
reports/verification_run/diagnostic_report.txt

The same portfolio-friendly static outputs are also committed under:

examples/generated_reference/tributary_layout.svg
examples/generated_reference/tributary_layout.png
examples/generated_reference/cfd_metrics_summary.txt
```

## Limitation

Onshape FeatureScript compile/regeneration validation cannot be run locally in this environment. The FeatureScript is therefore marked as an Onshape-validation candidate, while the Python geometry mirror is the locally verified reference implementation.
