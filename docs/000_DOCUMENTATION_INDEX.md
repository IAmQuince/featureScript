# Documentation Index

## Reviewer-facing files

- `README_START_HERE.md` — first-read instructions and review order.
- `PORTFOLIO_REVIEW_GUIDE.md` — one-page reviewer map.
- `README.md` — project overview, launcher, GUI, Onshape relationship, and tests.
- `RUN_INSTRUCTIONS.md` — how to launch the GUI and CLI.
- `TEST_INSTRUCTIONS.md` — local validation commands.

## Core technical docs

- `docs/010_PRODUCT_REQUIREMENTS.md` — product goals and acceptance expectations.
- `docs/020_FEATURE_INVENTORY.md` — current package features.
- `docs/030_GEOMETRY_SPEC.md` — recovered tributary geometry rules.
- `docs/040_MODULE_BOUNDARY_SPEC.md` — FeatureScript/Python/tooling boundaries.
- `docs/080_ACCEPTANCE_TEST_PLAN.md` — validation approach.
- `docs/090_RISK_REGISTER.md` — known risks.
- `docs/100_TECHNICAL_DEBT_REGISTER.md` — known debt.
- `docs/110_REFACTOR_SEQUENCE_PLAN.md` — likely future cleanup sequence.
- `docs/120_DECISION_LOG.md` — key package decisions.
- `docs/130_REVIEWER_ONBOARDING.md` — how a reviewer should approach the repository.
- `docs/140_LOCAL_VERIFICATION_REPORT.md` — latest local verification summary.
- `docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md` — candid FeatureScript syntax/debugging history.
- `docs/160_GUI_LAUNCHER_AND_PREVIEW.md` — GUI and launcher design notes.

## Main source locations

- `launch_tributary_generator.bat` — single Windows entry point.
- `src/tributary_geometry/gui_app.py` — live preview GUI.
- `src/tributary_geometry/layout.py` — Python geometry generator.
- `src/tributary_geometry/bezier.py` — Bezier math.
- `feature_scripts/tributary_generator.fs` — Onshape FeatureScript candidate.

- `170_CFD_SCREENING_METRICS.md` — first-pass CFD/symmetry metrics used by the GUI and CLI.
- `180_RECOVERED_V1_UPDATE_REPORT.md` — summary of the recovered v1 update and verification work.
