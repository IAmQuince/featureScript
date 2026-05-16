# Test Instructions

From the repository root:

```bat
set PYTHONPATH=%CD%\src
python tests\smoke_test.py
python -m unittest discover -s tests
python tools\diagnostic_harness.py
python tools\structure_audit.py
```

The GUI is not automatically opened during tests because that would require an interactive display. The static GUI test verifies that the GUI exposes every `TributaryConfig` field and that the LFO parameter list is constrained to numeric variables.

Expected local status for this package:

```text
unit tests: pass
smoke test: pass
diagnostic harness: pass
structure audit: pass
GUI static import/contract test: pass
```
