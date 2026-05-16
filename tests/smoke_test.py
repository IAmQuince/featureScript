from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tributary_geometry.config import TributaryConfig
from tributary_geometry.exporters import write_branch_csv, write_json, write_metrics_csv, write_metrics_json, write_metrics_summary_txt, write_svg
from tributary_geometry.featurescript_export import write_variable_table
from tributary_geometry.layout import build_tributary_layout


def main() -> int:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    lines = ["Tributary Generator Smoke Test", "===============================", ""]
    try:
        config = TributaryConfig()
        layout = build_tributary_layout(config)
        json_path = write_json(layout, reports / "smoke_tributary_layout.json")
        svg_path = write_svg(layout, reports / "smoke_tributary_layout.svg")
        csv_path = write_branch_csv(layout, reports / "smoke_tributary_branch_samples.csv")
        var_path = write_variable_table(config, reports / "smoke_onshape_variable_table.txt")
        metrics_json_path = write_metrics_json(layout, reports / "smoke_cfd_metrics.json")
        metrics_csv_path = write_metrics_csv(layout, reports / "smoke_cfd_branch_metrics.csv")
        metrics_txt_path = write_metrics_summary_txt(layout, reports / "smoke_cfd_metrics_summary.txt")
        lines.extend(
            [
                f"Circles: {len(layout.circles)}",
                f"Branches: {len(layout.branches)}",
                f"Wrote: {json_path.name}",
                f"Wrote: {svg_path.name}",
                f"Wrote: {csv_path.name}",
                f"Wrote: {var_path.name}",
                f"Wrote: {metrics_json_path.name}",
                f"Wrote: {metrics_csv_path.name}",
                f"Wrote: {metrics_txt_path.name}",
                "Result: PASS",
            ]
        )
        code = 0
    except Exception as exc:
        lines.append(f"Result: FAIL - {exc!r}")
        code = 1
    report_path = reports / "smoke_test_report.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
