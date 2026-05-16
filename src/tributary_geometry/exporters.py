from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from .layout import TributaryLayout
from .vector2 import Point2


def write_json(layout: TributaryLayout, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(layout.to_json(), indent=2), encoding="utf-8")
    return out


def write_branch_csv(layout: TributaryLayout, path: str | Path, samples_per_curve: int = 32) -> Path:
    if samples_per_curve < 2:
        raise ValueError("samples_per_curve must be >= 2.")
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["branch_id", "branch_type", "source_circle_id", "target_circle_id", "curve", "sample_index", "t", "x", "y"],
        )
        writer.writeheader()
        for branch in layout.branches:
            for curve_name in ("top", "bottom", "centerline"):
                curve = getattr(branch, curve_name)
                for i in range(samples_per_curve):
                    t = i / (samples_per_curve - 1)
                    p = curve.point(t)
                    writer.writerow(
                        {
                            "branch_id": branch.id,
                            "branch_type": branch.branch_type,
                            "source_circle_id": branch.source_circle_id,
                            "target_circle_id": branch.target_circle_id,
                            "curve": curve_name,
                            "sample_index": i,
                            "t": f"{t:.8f}",
                            "x": f"{p.x:.8f}",
                            "y": f"{p.y:.8f}",
                        }
                    )
    return out


def write_pairing_csv(layout: TributaryLayout, path: str | Path) -> Path:
    """Write one row per branch so reviewers can audit the pairing policy."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "branch_id",
                "branch_type",
                "source_circle_id",
                "target_circle_id",
                "source_top_x",
                "source_top_y",
                "target_top_x",
                "target_top_y",
                "source_bottom_x",
                "source_bottom_y",
                "target_bottom_x",
                "target_bottom_y",
            ],
        )
        writer.writeheader()
        for branch in layout.branches:
            r = branch.rectangle
            writer.writerow(
                {
                    "branch_id": branch.id,
                    "branch_type": branch.branch_type,
                    "source_circle_id": branch.source_circle_id,
                    "target_circle_id": branch.target_circle_id,
                    "source_top_x": f"{r.p_source_top.x:.8f}",
                    "source_top_y": f"{r.p_source_top.y:.8f}",
                    "target_top_x": f"{r.p_target_top.x:.8f}",
                    "target_top_y": f"{r.p_target_top.y:.8f}",
                    "source_bottom_x": f"{r.p_source_bottom.x:.8f}",
                    "source_bottom_y": f"{r.p_source_bottom.y:.8f}",
                    "target_bottom_x": f"{r.p_target_bottom.x:.8f}",
                    "target_bottom_y": f"{r.p_target_bottom.y:.8f}",
                }
            )
    return out


def _svg_point(p: Point2, min_x: float, max_y: float, scale: float, pad: float) -> tuple[float, float]:
    return ((p.x - min_x) * scale + pad, (max_y - p.y) * scale + pad)


def _path_for_curve(points: list[Point2], min_x: float, max_y: float, scale: float, pad: float) -> str:
    coords = [_svg_point(p, min_x, max_y, scale, pad) for p in points]
    first = coords[0]
    rest = " ".join(f"L {x:.3f} {y:.3f}" for x, y in coords[1:])
    return f"M {first[0]:.3f} {first[1]:.3f} {rest}"


def _line_svg(p0: Point2, p1: Point2, min_x: float, max_y: float, scale: float, pad: float, style: str) -> str:
    x0, y0 = _svg_point(p0, min_x, max_y, scale, pad)
    x1, y1 = _svg_point(p1, min_x, max_y, scale, pad)
    return f"<line x1='{x0:.3f}' y1='{y0:.3f}' x2='{x1:.3f}' y2='{y1:.3f}' {style}/>"


def write_svg(
    layout: TributaryLayout,
    path: str | Path,
    samples_per_curve: int = 64,
    show_rectangles: bool = True,
    show_control_handles: bool = True,
    show_centerlines: bool = True,
    show_field_stubs: bool = True,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    all_points: list[Point2] = []
    for circle in layout.circles:
        all_points.extend(
            [
                Point2(circle.center.x - circle.radius, circle.center.y - circle.radius),
                Point2(circle.center.x + circle.radius, circle.center.y + circle.radius),
            ]
        )
    for branch in layout.branches:
        for curve_name in ("top", "bottom", "centerline"):
            all_points.extend(getattr(branch, curve_name).sample(samples_per_curve))
        all_points.extend(branch.rectangle.corners())
    for stub in layout.field_stubs:
        all_points.extend([stub.p0, stub.p1])

    min_x = min(p.x for p in all_points)
    max_x = max(p.x for p in all_points)
    min_y = min(p.y for p in all_points)
    max_y = max(p.y for p in all_points)
    pad = 36.0
    drawing_w = max_x - min_x
    drawing_h = max_y - min_y
    scale = 7.0 if max(drawing_w, drawing_h) <= 150 else 900.0 / max(drawing_w, drawing_h)
    width = drawing_w * scale + 2 * pad
    height = drawing_h * scale + 2 * pad

    role_style = {
        "feed": "stroke-width='1.8' stroke='rgb(160,40,40)' fill='none'",
        "dump": "stroke-width='1.8' stroke='rgb(40,100,180)' fill='none'",
        "snake": "stroke-width='1.2' stroke='rgb(20,20,20)' fill='none'",
        "ladder": "stroke-width='1.2' stroke='rgb(50,120,60)' fill='none'",
    }
    branch_style = {
        "feed_to_ladder": "stroke='rgb(150,45,45)'",
        "feed_to_snake": "stroke='rgb(150,45,45)'",
        "dump_to_snake": "stroke='rgb(30,85,150)'",
        "dump_to_ladder": "stroke='rgb(30,85,150)'",
    }

    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width:.1f}' height='{height:.1f}' viewBox='0 0 {width:.1f} {height:.1f}'>",
        "<rect x='0' y='0' width='100%' height='100%' fill='white'/>",
        "<text x='12' y='20' font-size='14' font-family='monospace'>Tributary Generator reference preview</text>",
        f"<text x='12' y='38' font-size='11' font-family='monospace'>pairing_mode={escape(str(layout.config.pairing_mode))}; rectangular d_M1/d_M2 control handles</text>",
    ]

    if show_field_stubs:
        for stub in layout.field_stubs:
            parts.append(_line_svg(stub.p0, stub.p1, min_x, max_y, scale, pad, "stroke='rgb(170,170,170)' stroke-width='1.1'"))

    if show_rectangles:
        for branch in layout.branches:
            corners = branch.rectangle.corners()
            for p0, p1 in zip(corners, corners[1:] + corners[:1]):
                parts.append(_line_svg(p0, p1, min_x, max_y, scale, pad, "stroke='rgb(190,190,190)' stroke-width='0.8' stroke-dasharray='3 3'"))

    for branch in layout.branches:
        style = branch_style.get(branch.branch_type, "stroke='black'")
        for curve_name in ("top", "bottom"):
            curve = getattr(branch, curve_name)
            d = _path_for_curve(curve.sample(samples_per_curve), min_x, max_y, scale, pad)
            parts.append(f"<path d='{escape(d)}' fill='none' {style} stroke-width='1.8'/>")
            if show_control_handles:
                parts.append(_line_svg(curve.p0, curve.p1, min_x, max_y, scale, pad, "stroke='rgb(120,120,120)' stroke-width='0.8' stroke-dasharray='2 4'"))
                parts.append(_line_svg(curve.p2, curve.p3, min_x, max_y, scale, pad, "stroke='rgb(120,120,120)' stroke-width='0.8' stroke-dasharray='2 4'"))
        if show_centerlines:
            d = _path_for_curve(branch.centerline.sample(samples_per_curve), min_x, max_y, scale, pad)
            parts.append(f"<path d='{escape(d)}' fill='none' stroke='rgb(80,80,80)' stroke-width='0.9' opacity='0.38' stroke-dasharray='4 5'/>")

    for circle in layout.circles:
        x, y = _svg_point(circle.center, min_x, max_y, scale, pad)
        r = circle.radius * scale
        style = role_style.get(circle.role, "stroke='black' fill='none'")
        parts.append(f"<circle cx='{x:.3f}' cy='{y:.3f}' r='{r:.3f}' {style}/>")
        parts.append(f"<circle cx='{x:.3f}' cy='{y:.3f}' r='1.7' fill='rgb(80,80,80)'/>")
        parts.append(f"<text x='{x + r + 3:.3f}' y='{y + 3:.3f}' font-size='8' font-family='monospace'>{escape(circle.id)}</text>")

    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def write_png_from_svg(svg_path: str | Path, png_path: str | Path) -> Path:
    """Render an SVG preview to PNG when CairoSVG is available."""

    svg_path = Path(svg_path)
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import cairosvg
    except Exception as exc:  # pragma: no cover - depends on optional environment
        raise RuntimeError("PNG export requires cairosvg. SVG export is still available.") from exc
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))
    return png_path


def write_metrics_json(layout: TributaryLayout, path: str | Path) -> Path:
    """Write CFD-screening and symmetry metrics as JSON."""

    from .metrics import compute_layout_metrics

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    metrics = compute_layout_metrics(layout)
    out.write_text(json.dumps(metrics.to_json(), indent=2), encoding="utf-8")
    return out


def write_metrics_csv(layout: TributaryLayout, path: str | Path) -> Path:
    """Write per-branch CFD-screening metrics as CSV."""

    from .metrics import compute_layout_metrics

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    metrics = compute_layout_metrics(layout)
    rows = [branch.to_json() for branch in metrics.branch_metrics]
    fieldnames = list(rows[0].keys()) if rows else ["branch_id"]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out


def write_metrics_summary_txt(layout: TributaryLayout, path: str | Path) -> Path:
    """Write human-readable CFD-screening summary metrics."""

    from .metrics import compute_layout_metrics

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    metrics = compute_layout_metrics(layout)
    lines = [
        "Tributary Generator CFD-Screening Metrics",
        "=========================================",
        "",
        "These are first-pass geometric proxies only; they are not a CFD solution.",
        "Use them to compare layouts before exporting geometry to CAD/meshing tools.",
        "",
    ]
    for key, value in metrics.summary_rows():
        if isinstance(value, float):
            lines.append(f"{key}: {value:.8g}")
        else:
            lines.append(f"{key}: {value}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
