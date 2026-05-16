from __future__ import annotations

from dataclasses import dataclass

try:
    from .bezier import CubicBezier, connect_bezier_rect
    from .config import TributaryConfig
    from .vector2 import Point2
except ImportError:  # Allows direct exploratory runs like `python src/tributary_geometry/layout.py`.
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tributary_geometry.bezier import CubicBezier, connect_bezier_rect
    from tributary_geometry.config import TributaryConfig
    from tributary_geometry.vector2 import Point2


@dataclass(frozen=True)
class Circle:
    """One construction circle in the tributary layout."""

    id: str
    role: str
    center: Point2
    radius: float
    index: int

    def right_top(self) -> Point2:
        """Upper boundary point on the circle's right-side channel envelope."""

        return Point2(self.center.x + self.radius, self.center.y + self.radius)

    def right_bottom(self) -> Point2:
        """Lower boundary point on the circle's right-side channel envelope."""

        return Point2(self.center.x + self.radius, self.center.y - self.radius)

    def left_top(self) -> Point2:
        """Upper boundary point on the circle's left-side channel envelope."""

        return Point2(self.center.x - self.radius, self.center.y + self.radius)

    def left_bottom(self) -> Point2:
        """Lower boundary point on the circle's left-side channel envelope."""

        return Point2(self.center.x - self.radius, self.center.y - self.radius)

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "role": self.role,
            "center": self.center.to_json(),
            "radius": self.radius,
            "index": self.index,
        }


@dataclass(frozen=True)
class ConstructionRectangle:
    """Rectangle implied by one source/target circle pair.

    The recovered document explicitly asked for rectangles between the top-most
    and bottom-most source/target points, then Bezier boundaries inside those
    rectangles. This object stores that construction so the GUI/SVG exports can
    show it instead of hiding the method.
    """

    p_source_top: Point2
    p_source_bottom: Point2
    p_target_top: Point2
    p_target_bottom: Point2

    def corners(self) -> list[Point2]:
        return [self.p_source_top, self.p_target_top, self.p_target_bottom, self.p_source_bottom]

    def to_json(self) -> dict[str, dict[str, float]]:
        return {
            "source_top": self.p_source_top.to_json(),
            "source_bottom": self.p_source_bottom.to_json(),
            "target_top": self.p_target_top.to_json(),
            "target_bottom": self.p_target_bottom.to_json(),
        }


@dataclass(frozen=True)
class FieldStub:
    """Small upstream guide line used only for photo-like preview context."""

    id: str
    branch_id: str
    p0: Point2
    p1: Point2

    def to_json(self) -> dict[str, object]:
        return {"id": self.id, "branch_id": self.branch_id, "p0": self.p0.to_json(), "p1": self.p1.to_json()}


@dataclass(frozen=True)
class TributaryBranch:
    """One generated tributary connection between two circles.

    A branch stores two manufacturing-relevant boundary curves and one dashed
    diagnostic centerline. The top/bottom curves are the important CAD output.
    """

    id: str
    branch_type: str
    source_circle_id: str
    target_circle_id: str
    top: CubicBezier
    bottom: CubicBezier
    centerline: CubicBezier
    rectangle: ConstructionRectangle

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "branch_type": self.branch_type,
            "source_circle_id": self.source_circle_id,
            "target_circle_id": self.target_circle_id,
            "top": self.top.to_json(),
            "bottom": self.bottom.to_json(),
            "centerline": self.centerline.to_json(),
            "construction_rectangle": self.rectangle.to_json(),
        }


@dataclass(frozen=True)
class TributaryLayout:
    """Complete Python-side preview of the tributary generator output."""

    config: TributaryConfig
    circles: list[Circle]
    branches: list[TributaryBranch]
    field_stubs: list[FieldStub]

    def circles_by_role(self, role: str) -> list[Circle]:
        return [c for c in self.circles if c.role == role]

    def to_json(self) -> dict[str, object]:
        return {
            "config": self.config.to_json(),
            "circles": [circle.to_json() for circle in self.circles],
            "branches": [branch.to_json() for branch in self.branches],
            "field_stubs": [stub.to_json() for stub in self.field_stubs],
        }


def _linspace(start: float, end: float, count: int) -> list[float]:
    """Return count evenly spaced values, including start and end."""

    if count <= 0:
        return []
    if count == 1:
        return [(start + end) / 2.0]
    step = (end - start) / float(count - 1)
    return [start + i * step for i in range(count)]


def _build_branch(branch_id: str, branch_type: str, source: Circle, target: Circle, d_m1: float, d_m2: float) -> TributaryBranch:
    """Build the recovered top/bottom Bezier boundaries for one circle pair."""

    source_top = source.right_top()
    source_bottom = source.right_bottom()
    target_top = target.left_top()
    target_bottom = target.left_bottom()
    rectangle = ConstructionRectangle(source_top, source_bottom, target_top, target_bottom)
    top = connect_bezier_rect(source_top, target_top, d_m1, d_m2)
    bottom = connect_bezier_rect(source_bottom, target_bottom, d_m1, d_m2)
    centerline = connect_bezier_rect(source.center, target.center, d_m1, d_m2)
    return TributaryBranch(
        id=branch_id,
        branch_type=branch_type,
        source_circle_id=source.id,
        target_circle_id=target.id,
        top=top,
        bottom=bottom,
        centerline=centerline,
        rectangle=rectangle,
    )


def _make_field_stubs(branch: TributaryBranch, length: float) -> list[FieldStub]:
    """Create optional left-side channel guides for visual comparison to machined plates."""

    x0_top = branch.rectangle.p_source_top.x - length
    x0_bottom = branch.rectangle.p_source_bottom.x - length
    return [
        FieldStub(f"{branch.id}_stub_top", branch.id, Point2(x0_top, branch.rectangle.p_source_top.y), branch.rectangle.p_source_top),
        FieldStub(f"{branch.id}_stub_bottom", branch.id, Point2(x0_bottom, branch.rectangle.p_source_bottom.y), branch.rectangle.p_source_bottom),
    ]


def build_tributary_layout(config: TributaryConfig) -> TributaryLayout:
    """Generate the full tributary geometry preview.

    This is the main Python geometry generator. Portfolio reviewers should start
    here after reading the README because it expresses the CAD intent in ordinary,
    locally testable Python.

    Corrected/recovered layout rules implemented here:
    - feed, dump, and central snake/ladder circle lines are built from the old
      FeatureScript document's formulas;
    - central line has 2*N + 1 stations, alternating snake/ladder circles;
    - feed circles use N - 1 interior stations;
    - dump circles use N half-step stations;
    - branches are paired according to the selected recovered pairing mode;
    - the default pairing mode keeps the generated layout mirrored about y=0;
    - every tributary has two real boundaries, not a single centerline curve;
    - each boundary starts and ends on facing circle-edge points;
    - d_M1 and d_M2 are rectangular horizontal control-handle distances.
    """

    errors = config.validate()
    if errors:
        raise ValueError("Invalid TributaryConfig: " + "; ".join(errors))

    n = int(config.channel_num_snakes)
    feed_count = n - 1
    dump_count = n
    central_count = 2 * n + 1

    # Recovered line lengths. The first two source lines use Manifold_Length.
    # The central snake/ladder line uses the L3 expression from Tributaryv1.docx.
    source_top = config.manifold_length / 2.0
    source_bottom = -config.manifold_length / 2.0
    central_length = config.manifold_length + 2.0 * config.manifold_reduction - 2.0 * config.ladder_width
    central_top = central_length / 2.0
    central_bottom = -central_length / 2.0

    feed_x = 0.0
    dump_x = config.feed_dump_offset
    central_x = config.feed_dump_offset + config.tributary_offset

    feed_radius = config.feed_diameter / 2.0
    dump_radius = config.dump_diameter / 2.0
    snake_radius = config.snake_width / 2.0
    ladder_radius = config.ladder_width / 2.0

    circles: list[Circle] = []
    feeds: list[Circle] = []
    dumps: list[Circle] = []
    snakes: list[Circle] = []
    ladders: list[Circle] = []

    # Source line 1: feed circles at interior manifold stations.
    feed_spacing = config.manifold_length / n
    for i in range(feed_count):
        feed_shift = -feed_radius if config.top_bottom_feed_left_shift and (i == 0 or i == feed_count - 1) else 0.0
        y = source_top - feed_spacing * (i + 1)
        circle = Circle(f"feed_{i}", "feed", Point2(feed_x + feed_shift, y), feed_radius, i)
        feeds.append(circle)
        circles.append(circle)

    # Source line 2: dump circles at half-step stations.
    for i in range(dump_count):
        y = source_top - (config.manifold_length / (2.0 * n) + feed_spacing * i)
        circle = Circle(f"dump_{i}", "dump", Point2(dump_x, y), dump_radius, i)
        dumps.append(circle)
        circles.append(circle)

    # Target line: alternating snake/ladder circles on the recovered 2*N+1 grid.
    central_y_values = _linspace(central_top, central_bottom, central_count)
    for central_index, y in enumerate(central_y_values):
        if central_index % 2 == 0:
            index = central_index // 2
            circle = Circle(f"snake_{index}", "snake", Point2(central_x, y), snake_radius, index)
            snakes.append(circle)
        else:
            index = central_index // 2
            circle = Circle(f"ladder_{index}", "ladder", Point2(central_x, y), ladder_radius, index)
            ladders.append(circle)
        circles.append(circle)

    branches: list[TributaryBranch] = []

    if config.pairing_mode == "recovered_docx_v1":
        # Written interpretation from the old document: feed/dump pair with
        # ladder/snake respectively. Counts are asymmetric, so feed uses the
        # first N-1 ladder targets and dump uses the first N snake targets.
        feed_targets = ladders[:feed_count]
        dump_targets = snakes[:dump_count]
    elif config.pairing_mode == "y_aligned_physical":
        # Spacing interpretation: feed stations align with interior snake circles;
        # dump stations align with ladder circles. This is helpful when comparing
        # to a machined plate/photo where branches should stay locally parallel.
        feed_targets = snakes[1:n]
        dump_targets = ladders[:dump_count]
    else:  # defensive; validate() should prevent this.
        raise ValueError(f"Unsupported pairing_mode: {config.pairing_mode}")

    for i, (source, target) in enumerate(zip(feeds, feed_targets)):
        branches.append(_build_branch(f"feed_to_{target.role}_{i}", f"feed_to_{target.role}", source, target, config.d_ladder_m1, config.d_ladder_m2))
    for i, (source, target) in enumerate(zip(dumps, dump_targets)):
        branches.append(_build_branch(f"dump_to_{target.role}_{i}", f"dump_to_{target.role}", source, target, config.d_snake_m1, config.d_snake_m2))

    # Small context stubs make the preview read more like the physical photo:
    # paired channel boundaries approach from a field region, then bend into the
    # port/circle row. They are explicitly preview-only and not exported as
    # FeatureScript manufacturing geometry.
    stub_length = max(config.feed_dump_offset * 0.7, config.feed_diameter * 1.5)
    field_stubs: list[FieldStub] = []
    for branch in branches:
        field_stubs.extend(_make_field_stubs(branch, stub_length))

    return TributaryLayout(config=config, circles=circles, branches=branches, field_stubs=field_stubs)


if __name__ == "__main__":
    layout = build_tributary_layout(TributaryConfig())
    print("Tributary layout preview built successfully.")
    print(f"Circles: {len(layout.circles)}")
    print(f"Branches: {len(layout.branches)}")
    print(f"Pairing mode: {layout.config.pairing_mode}")
    print("Run launch_tributary_generator.bat from the repository root for the live GUI.")
