from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "README_START_HERE.md",
    "PORTFOLIO_REVIEW_GUIDE.md",
    "RUN_INSTRUCTIONS.md",
    "TEST_INSTRUCTIONS.md",
    "CHANGELOG.md",
    "KNOWN_LIMITATIONS.md",
    "launch_tributary_generator.bat",
    "pyproject.toml",
    ".gitignore",
    ".gitattributes",
    "src/tributary_geometry/__init__.py",
    "src/tributary_geometry/README.md",
    "src/tributary_geometry/layout.py",
    "src/tributary_geometry/gui_app.py",
    "src/tributary_geometry/metrics.py",
    "feature_scripts/README.md",
    "feature_scripts/tributary_generator.fs",
    "examples/tributary_example_config.json",
    "examples/gui_demo_scenario.json",
    "examples/generated_reference/tributary_layout.svg",
    "examples/generated_reference/tributary_layout.png",
    "examples/generated_reference/cfd_metrics_summary.txt",
    "docs/010_PRODUCT_REQUIREMENTS.md",
    "docs/020_FEATURE_INVENTORY.md",
    "docs/030_GEOMETRY_SPEC.md",
    "docs/040_MODULE_BOUNDARY_SPEC.md",
    "docs/080_ACCEPTANCE_TEST_PLAN.md",
    "docs/090_RISK_REGISTER.md",
    "docs/100_TECHNICAL_DEBT_REGISTER.md",
    "docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md",
    "docs/160_GUI_LAUNCHER_AND_PREVIEW.md",
    "docs/170_CFD_SCREENING_METRICS.md",
    "docs/180_RECOVERED_V1_UPDATE_REPORT.md",
    "references/README.md",
    "references/recovered_tributary_v1_notes.md",
    "tools/diagnostic_harness.py",
    "tools/structure_audit.py",
    "tests/test_geometry.py",
    "tests/smoke_test.py",
    "tests/test_gui_static.py",
]

FORBIDDEN_NAMES = {".DS_Store"}
FORBIDDEN_FILES = {
    "feature_scripts/myTributary_CircleLine_STABLE.fs",
    "feature_scripts/myTributary_Smooth_legacy_name.fs",
}
CACHE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def main() -> int:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    lines = ["Tributary Generator Structure Audit", "===================================", ""]
    failures = []

    for rel in REQUIRED_PATHS:
        if not (ROOT / rel).exists():
            failures.append(f"Missing required path: {rel}")

    for rel in FORBIDDEN_FILES:
        if (ROOT / rel).exists():
            failures.append(f"Legacy/stale source file should not be in clean package: {rel}")

    warnings = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in FORBIDDEN_NAMES for part in path.parts):
            failures.append(f"Forbidden OS/editor noise path present: {rel}")
        if any(part in CACHE_NAMES for part in path.parts):
            warnings.append(f"Runtime cache path present; remove before zipping/release: {rel}")

    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in warnings[:20])
        if len(warnings) > 20:
            lines.append(f"- ... {len(warnings) - 20} additional cache warnings omitted")
        lines.append("")

    if failures:
        lines.append("Result: FAIL")
        lines.extend(f"- {failure}" for failure in failures)
        code = 1
    else:
        lines.append("Result: PASS")
        lines.append(f"Required paths checked: {len(REQUIRED_PATHS)}")
        code = 0

    report_path = reports / "structure_audit_report.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
