from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import TributaryConfig
from .exporters import write_branch_csv, write_json, write_metrics_csv, write_metrics_json, write_metrics_summary_txt, write_pairing_csv, write_png_from_svg, write_svg
from .featurescript_export import write_variable_table
from .layout import build_tributary_layout


def _load_config(path: str | None) -> TributaryConfig:
    """Load a JSON config file or return the built-in diagnostic defaults."""

    if not path:
        return TributaryConfig()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TributaryConfig.from_json(data)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for the Python preview generator."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate tributary geometry previews before validating the companion "
            "FeatureScript inside Onshape."
        )
    )
    parser.add_argument("--config", help="Optional JSON config path. Uses built-in diagnostic defaults when omitted.")
    parser.add_argument("--out", default="reports/tributary_generator", help="Output folder for JSON/SVG/CSV diagnostics.")
    parser.add_argument("--samples", type=int, default=48, help="Samples per Bezier curve for SVG/CSV exports.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the local tributary preview workflow.

    The output files are deliberately simple:
    - tributary_layout.svg: visual preview for portfolio/review use
    - tributary_layout.json: exact generated geometry data
    - tributary_branch_samples.csv: sampled branch coordinates for inspection
    - onshape_variable_table.txt: copy/paste helper for Onshape variables
    - cfd_metrics.json/csv/txt: first-pass CFD screening and symmetry metrics
    - diagnostic_report.txt: short run summary
    """

    args = build_parser().parse_args(argv)
    config = _load_config(args.config)
    errors = config.validate()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_lines = ["Tributary Generator Python Preview", "==================================", ""]
    if errors:
        report_lines.append("Configuration failed validation:")
        report_lines.extend(f"- {error}" for error in errors)
        (out_dir / "diagnostic_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
        return 2

    layout = build_tributary_layout(config)
    json_path = write_json(layout, out_dir / "tributary_layout.json")
    svg_path = write_svg(layout, out_dir / "tributary_layout.svg", samples_per_curve=args.samples)
    csv_path = write_branch_csv(layout, out_dir / "tributary_branch_samples.csv", samples_per_curve=args.samples)
    pairing_path = write_pairing_csv(layout, out_dir / "branch_pairing_table.csv")
    variable_path = write_variable_table(config, out_dir / "onshape_variable_table.txt")
    metrics_json_path = write_metrics_json(layout, out_dir / "cfd_metrics.json")
    metrics_csv_path = write_metrics_csv(layout, out_dir / "cfd_branch_metrics.csv")
    metrics_summary_path = write_metrics_summary_txt(layout, out_dir / "cfd_metrics_summary.txt")
    png_path = None
    try:
        png_path = write_png_from_svg(svg_path, out_dir / "tributary_layout.png")
    except Exception as exc:
        png_path = f"PNG not rendered: {exc}"

    report_lines.extend(
        [
            f"Circles: {len(layout.circles)}",
            f"Branches: {len(layout.branches)}",
            f"JSON: {json_path}",
            f"SVG: {svg_path}",
            f"CSV: {csv_path}",
            f"Pairing table: {pairing_path}",
            f"PNG: {png_path}",
            f"Onshape variable table: {variable_path}",
            f"CFD metrics JSON: {metrics_json_path}",
            f"CFD branch metrics CSV: {metrics_csv_path}",
            f"CFD metrics summary: {metrics_summary_path}",
            "",
            "Status: PASS - Python geometry preview completed.",
            "Note: feature_scripts/tributary_generator.fs still requires Onshape-side validation.",
        ]
    )
    (out_dir / "diagnostic_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print("\n".join(report_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
