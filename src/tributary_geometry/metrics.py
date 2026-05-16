from __future__ import annotations

"""Geometry and first-pass CFD screening metrics for Tributary Generator.

These metrics are deliberately lightweight. They are not a CFD solver and they do
not replace meshing in Onshape/OpenFOAM/Fluent/etc. Their job is to give a user a
quick quantitative read on whether a candidate tributary layout is worth sending
forward to CAD regeneration, meshing, and flow simulation.
"""

from dataclasses import dataclass, asdict
from math import hypot, sqrt
from statistics import mean, pstdev
from typing import Iterable

from .layout import TributaryBranch, TributaryLayout
from .vector2 import Point2


def _distance(a: Point2, b: Point2) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def _polyline_length(points: list[Point2]) -> float:
    return sum(_distance(a, b) for a, b in zip(points, points[1:]))


def _safe_cv(values: list[float]) -> float:
    clean = [v for v in values if v > 0.0]
    if not clean:
        return 0.0
    avg = mean(clean)
    return 0.0 if avg == 0.0 else pstdev(clean) / avg


def _curvature_proxy(points: list[Point2]) -> tuple[float, float]:
    """Return approximate max/mean absolute curvature from sampled points.

    This is a polyline curvature proxy based on turn angle over local arc length.
    It is intended for screening abrupt tributary bends before CFD, not for final
    manufacturing acceptance.
    """

    values: list[float] = []
    for p0, p1, p2 in zip(points, points[1:], points[2:]):
        v1 = Point2(p1.x - p0.x, p1.y - p0.y)
        v2 = Point2(p2.x - p1.x, p2.y - p1.y)
        l1 = v1.length
        l2 = v2.length
        if l1 <= 1e-12 or l2 <= 1e-12:
            continue
        dot = max(-1.0, min(1.0, (v1.x * v2.x + v1.y * v2.y) / (l1 * l2)))
        # atan2 equivalent through cross/dot keeps the sign but we store abs.
        cross = v1.x * v2.y - v1.y * v2.x
        import math

        angle = abs(math.atan2(cross, dot))
        local_len = max(1e-12, 0.5 * (l1 + l2))
        values.append(angle / local_len)
    if not values:
        return 0.0, 0.0
    return max(values), mean(values)


def _min_point_gap(point_sets: list[list[Point2]]) -> float:
    """Approximate minimum distance between different branch centerlines."""

    min_gap = float("inf")
    for i in range(len(point_sets)):
        for j in range(i + 1, len(point_sets)):
            for a in point_sets[i]:
                for b in point_sets[j]:
                    d = _distance(a, b)
                    if d < min_gap:
                        min_gap = d
    return 0.0 if min_gap == float("inf") else min_gap


@dataclass(frozen=True)
class BranchMetrics:
    branch_id: str
    branch_type: str
    source_circle_id: str
    target_circle_id: str
    centerline_length: float
    top_boundary_length: float
    bottom_boundary_length: float
    average_boundary_width: float
    min_boundary_width: float
    max_boundary_width: float
    planform_area_proxy: float
    cross_sectional_area: float
    wetted_perimeter: float
    hydraulic_diameter: float
    wetted_surface_area_proxy: float
    resistance_proxy: float
    entry_angle_degrees: float
    exit_angle_degrees: float
    max_curvature_proxy: float
    mean_curvature_proxy: float

    def to_json(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(frozen=True)
class LayoutMetrics:
    branch_count: int
    circle_count: int
    total_centerline_length: float
    total_planform_area_proxy: float
    total_wetted_surface_area_proxy: float
    average_boundary_width: float
    min_boundary_width: float
    max_boundary_width: float
    min_centerline_gap: float
    hydraulic_diameter_average: float
    resistance_proxy_total_parallel: float
    resistance_proxy_cv: float
    length_cv: float
    max_curvature_proxy: float
    symmetry_axis_y: float
    symmetry_mean_error: float
    symmetry_max_error: float
    symmetry_unpaired_count: int
    branch_metrics: list[BranchMetrics]

    def to_json(self) -> dict[str, object]:
        data = asdict(self)
        data["branch_metrics"] = [branch.to_json() for branch in self.branch_metrics]
        return data

    def summary_rows(self) -> list[tuple[str, float | int]]:
        return [
            ("branch_count", self.branch_count),
            ("circle_count", self.circle_count),
            ("total_centerline_length", self.total_centerline_length),
            ("total_planform_area_proxy", self.total_planform_area_proxy),
            ("total_wetted_surface_area_proxy", self.total_wetted_surface_area_proxy),
            ("average_boundary_width", self.average_boundary_width),
            ("min_boundary_width", self.min_boundary_width),
            ("max_boundary_width", self.max_boundary_width),
            ("min_centerline_gap", self.min_centerline_gap),
            ("hydraulic_diameter_average", self.hydraulic_diameter_average),
            ("resistance_proxy_total_parallel", self.resistance_proxy_total_parallel),
            ("resistance_proxy_cv", self.resistance_proxy_cv),
            ("length_cv", self.length_cv),
            ("max_curvature_proxy", self.max_curvature_proxy),
            ("symmetry_mean_error", self.symmetry_mean_error),
            ("symmetry_max_error", self.symmetry_max_error),
            ("symmetry_unpaired_count", self.symmetry_unpaired_count),
        ]


def _angle_degrees(vec: Point2) -> float:
    import math

    return math.degrees(math.atan2(vec.y, vec.x))


def _branch_metrics(branch: TributaryBranch, channel_depth: float, samples: int) -> BranchMetrics:
    top_points = branch.top.sample(samples)
    bottom_points = branch.bottom.sample(samples)
    center_points = branch.centerline.sample(samples)
    widths = [_distance(a, b) for a, b in zip(top_points, bottom_points)]
    avg_width = mean(widths) if widths else 0.0
    min_width = min(widths) if widths else 0.0
    max_width = max(widths) if widths else 0.0
    centerline_length = _polyline_length(center_points)
    top_length = _polyline_length(top_points)
    bottom_length = _polyline_length(bottom_points)
    planform_area = avg_width * centerline_length
    cross_section_area = avg_width * channel_depth
    wetted_perimeter = 2.0 * (avg_width + channel_depth)
    hydraulic_diameter = 0.0 if (avg_width + channel_depth) <= 0 else 2.0 * avg_width * channel_depth / (avg_width + channel_depth)
    wetted_surface_area = wetted_perimeter * centerline_length
    resistance_proxy = float("inf") if hydraulic_diameter <= 0 else centerline_length / (hydraulic_diameter**4)
    entry_angle = _angle_degrees(branch.centerline.derivative(0.0))
    exit_angle = _angle_degrees(branch.centerline.derivative(1.0))
    max_curv, mean_curv = _curvature_proxy(center_points)
    return BranchMetrics(
        branch_id=branch.id,
        branch_type=branch.branch_type,
        source_circle_id=branch.source_circle_id,
        target_circle_id=branch.target_circle_id,
        centerline_length=centerline_length,
        top_boundary_length=top_length,
        bottom_boundary_length=bottom_length,
        average_boundary_width=avg_width,
        min_boundary_width=min_width,
        max_boundary_width=max_width,
        planform_area_proxy=planform_area,
        cross_sectional_area=cross_section_area,
        wetted_perimeter=wetted_perimeter,
        hydraulic_diameter=hydraulic_diameter,
        wetted_surface_area_proxy=wetted_surface_area,
        resistance_proxy=resistance_proxy,
        entry_angle_degrees=entry_angle,
        exit_angle_degrees=exit_angle,
        max_curvature_proxy=max_curv,
        mean_curvature_proxy=mean_curv,
    )


def _branch_mid_y(branch: TributaryBranch) -> float:
    pts = branch.centerline.sample(9)
    return mean(p.y for p in pts)


def _mirror_error(a: TributaryBranch, b: TributaryBranch, samples: int, axis_y: float) -> float:
    pa = a.centerline.sample(samples)
    pb = b.centerline.sample(samples)
    # Use the same parametric direction because mirrored branches are generated
    # with the same left-to-right source-target convention.
    errors = []
    for p, q in zip(pa, pb):
        mirrored = Point2(p.x, 2.0 * axis_y - p.y)
        errors.append(_distance(mirrored, q))
    return mean(errors) if errors else 0.0


def _symmetry_errors(layout: TributaryLayout, samples: int, axis_y: float = 0.0) -> tuple[float, float, int]:
    """Estimate branch-pair mirror error about the midline y=axis_y."""

    errors: list[float] = []
    unpaired = 0
    unused = set(range(len(layout.branches)))
    for i, branch in enumerate(layout.branches):
        if i not in unused:
            continue
        my = _branch_mid_y(branch) - axis_y
        if abs(my) < 1e-9:
            # Centerline branch should be self-symmetric.
            pts = branch.centerline.sample(samples)
            self_errors = []
            for p, q in zip(pts, reversed(pts)):
                self_errors.append(abs((p.y + q.y) / 2.0 - axis_y))
            errors.append(mean(self_errors) if self_errors else 0.0)
            unused.remove(i)
            continue
        candidates = [
            j
            for j in unused
            if j != i
            and layout.branches[j].branch_type == branch.branch_type
            and (_branch_mid_y(layout.branches[j]) - axis_y) * my < 0.0
        ]
        if not candidates:
            unpaired += 1
            unused.remove(i)
            continue
        best = min(candidates, key=lambda j: abs((_branch_mid_y(layout.branches[j]) - axis_y) + my))
        errors.append(_mirror_error(branch, layout.branches[best], samples, axis_y))
        unused.remove(i)
        unused.remove(best)
    if not errors:
        return 0.0, 0.0, unpaired
    return mean(errors), max(errors), unpaired


def compute_layout_metrics(layout: TributaryLayout, samples: int = 64) -> LayoutMetrics:
    """Compute screening metrics from a generated tributary layout."""

    samples = max(8, int(samples))
    branch_rows = [_branch_metrics(branch, layout.config.channel_depth, samples) for branch in layout.branches]
    total_len = sum(row.centerline_length for row in branch_rows)
    total_area = sum(row.planform_area_proxy for row in branch_rows)
    total_wetted = sum(row.wetted_surface_area_proxy for row in branch_rows)
    widths = [row.average_boundary_width for row in branch_rows]
    min_widths = [row.min_boundary_width for row in branch_rows]
    max_widths = [row.max_boundary_width for row in branch_rows]
    hydraulic_ds = [row.hydraulic_diameter for row in branch_rows if row.hydraulic_diameter > 0]
    resistance = [row.resistance_proxy for row in branch_rows if row.resistance_proxy != float("inf")]
    lengths = [row.centerline_length for row in branch_rows]
    curvatures = [row.max_curvature_proxy for row in branch_rows]
    centerline_sets = [branch.centerline.sample(24) for branch in layout.branches]
    sym_mean, sym_max, sym_unpaired = _symmetry_errors(layout, samples=24, axis_y=0.0)
    # Equivalent parallel resistance proxy using conductance summation. Units are
    # arbitrary because viscosity and constants are intentionally omitted.
    conductance = sum((1.0 / r) for r in resistance if r > 0.0)
    parallel_proxy = 0.0 if conductance <= 0.0 else 1.0 / conductance
    return LayoutMetrics(
        branch_count=len(layout.branches),
        circle_count=len(layout.circles),
        total_centerline_length=total_len,
        total_planform_area_proxy=total_area,
        total_wetted_surface_area_proxy=total_wetted,
        average_boundary_width=mean(widths) if widths else 0.0,
        min_boundary_width=min(min_widths) if min_widths else 0.0,
        max_boundary_width=max(max_widths) if max_widths else 0.0,
        min_centerline_gap=_min_point_gap(centerline_sets),
        hydraulic_diameter_average=mean(hydraulic_ds) if hydraulic_ds else 0.0,
        resistance_proxy_total_parallel=parallel_proxy,
        resistance_proxy_cv=_safe_cv(resistance),
        length_cv=_safe_cv(lengths),
        max_curvature_proxy=max(curvatures) if curvatures else 0.0,
        symmetry_axis_y=0.0,
        symmetry_mean_error=sym_mean,
        symmetry_max_error=sym_max,
        symmetry_unpaired_count=sym_unpaired,
        branch_metrics=branch_rows,
    )
