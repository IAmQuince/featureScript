from pathlib import Path
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def run_step(name, func):
    try:
        result = func()
        return True, f"PASS {name}: {result}"
    except Exception as exc:
        return False, f"FAIL {name}: {exc!r}\n{traceback.format_exc()}"


def main() -> int:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    lines = [
        "Tributary Generator Diagnostic Harness",
        "======================================",
        f"Python: {sys.version}",
        f"Platform: {platform.platform()}",
        f"Root: {ROOT}",
        "",
    ]

    def import_check():
        import tributary_geometry  # noqa: F401
        return "tributary_geometry imported"

    def geometry_check():
        from tributary_geometry import TributaryConfig, build_tributary_layout
        layout = build_tributary_layout(TributaryConfig(channel_num_snakes=6))
        return f"{len(layout.circles)} circles, {len(layout.branches)} branches"

    def smoke_check():
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "smoke_test.py")],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout)
        return "smoke_test.py passed"

    def unittest_check():
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout)
        return "unit test suite passed, including GUI static contract"

    def gui_import_check():
        from tributary_geometry import gui_app  # noqa: F401
        return "gui_app imported without opening a window"

    def featurescript_presence_check():
        fs_path = ROOT / "feature_scripts" / "tributary_generator.fs"
        text = fs_path.read_text(encoding="utf-8")
        required_snippets = [
            "Feature Type Name\" : \"Tributary Generator",
            "export const tributaryGenerator",
            "function _tgDrawTributaryPair",
            "function _tgDrawBezierBoundary",
            "newSketchOnPlane(context, id",
        ]
        missing = [snippet for snippet in required_snippets if snippet not in text]
        if missing:
            raise RuntimeError("Missing FeatureScript snippet(s): " + ", ".join(missing))
        return "tributary_generator.fs contains expected entry points"

    results = [
        run_step("import_check", import_check),
        run_step("geometry_check", geometry_check),
        run_step("gui_import_check", gui_import_check),
        run_step("smoke_check", smoke_check),
        run_step("unittest_check", unittest_check),
        run_step("featurescript_presence_check", featurescript_presence_check),
    ]
    for ok, message in results:
        lines.append(message)
        lines.append("")

    all_ok = all(ok for ok, _ in results)
    lines.append("Overall: " + ("PASS" if all_ok else "FAIL"))
    lines.append("Onshape FeatureScript compile status: NOT RUN LOCALLY; validate in Onshape.")

    report = reports / "diagnostic_harness_report.txt"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
