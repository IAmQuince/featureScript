from __future__ import annotations

from dataclasses import dataclass

from .vector2 import Point2, Vector2


def _lerp(a: Point2, b: Point2, t: float) -> Point2:
    """Linear interpolation helper used by De Casteljau evaluation."""

    return a * (1.0 - t) + b * t


@dataclass(frozen=True)
class CubicBezier:
    """Four-control-point cubic Bezier curve.

    This class is the Python preview equivalent of the `skBezier` calls in the
    FeatureScript. The goal is not to replace Onshape; it is to make the geometry
    inspectable before the FeatureScript is pasted into a Part Studio.
    """

    p0: Point2
    p1: Point2
    p2: Point2
    p3: Point2

    def point(self, t: float) -> Point2:
        """Return the point on the curve at normalized parameter t in [0, 1]."""

        return bezier_point(t, self.p0, self.p1, self.p2, self.p3)

    def derivative(self, t: float) -> Vector2:
        """Return the tangent vector at normalized parameter t in [0, 1]."""

        return bezier_derivative(t, self.p0, self.p1, self.p2, self.p3)

    def sample(self, samples: int = 32) -> list[Point2]:
        """Return evenly spaced parameter samples along the curve."""

        if samples < 2:
            raise ValueError("samples must be >= 2.")
        return [self.point(i / (samples - 1)) for i in range(samples)]

    def to_json(self) -> dict[str, dict[str, float]]:
        """Serialize control points for review, diffing, or downstream tooling."""

        return {
            "p0": self.p0.to_json(),
            "p1": self.p1.to_json(),
            "p2": self.p2.to_json(),
            "p3": self.p3.to_json(),
        }


def bezier_point(t: float, p0: Point2, p1: Point2, p2: Point2, p3: Point2) -> Point2:
    """Evaluate a cubic Bezier curve using De Casteljau's algorithm."""

    if not 0.0 <= t <= 1.0:
        raise ValueError(f"t must be within [0, 1]; got {t!r}.")
    a = _lerp(p0, p1, t)
    b = _lerp(p1, p2, t)
    c = _lerp(p2, p3, t)
    d = _lerp(a, b, t)
    e = _lerp(b, c, t)
    return _lerp(d, e, t)


def bezier_derivative(t: float, p0: Point2, p1: Point2, p2: Point2, p3: Point2) -> Vector2:
    """Evaluate the first derivative of a cubic Bezier curve."""

    if not 0.0 <= t <= 1.0:
        raise ValueError(f"t must be within [0, 1]; got {t!r}.")
    return (
        (p1 - p0) * (3.0 * (1.0 - t) * (1.0 - t))
        + (p2 - p1) * (6.0 * (1.0 - t) * t)
        + (p3 - p2) * (3.0 * t * t)
    )


def connect_bezier_rect(p_begin: Point2, p_end: Point2, d_m1: float, d_m2: float, sign_flip: float | None = None) -> CubicBezier:
    """Build one recovered rectangular-control tributary boundary.

    The old document's diagram showed d_M1 and d_M2 as horizontal construction
    distances inside a rectangle between the source and target circle edge
    points. Earlier reconstructed code used a perpendicular-to-chord offset; that
    produced smooth curves, but it did not match the fabrication/photo reference.

    This corrected helper intentionally keeps the first handle on the source
    point's horizontal construction line and the second handle on the target
    point's horizontal construction line:

        P0 = source circle boundary point
        P1 = P0 shifted toward the target by d_M1
        P2 = P3 shifted back toward the source by d_M2
        P3 = target circle boundary point

    sign_flip is accepted only for backward compatibility with older tests and
    FeatureScript naming. It is ignored because top/bottom separation now comes
    from the selected top/bottom circle-boundary points themselves, not from
    artificially bowing a centerline to either side.
    """

    if d_m1 < 0 or d_m2 < 0:
        raise ValueError("Bezier control distances must be non-negative.")
    chord = p_end - p_begin
    if chord.length == 0:
        raise ValueError("Cannot build a Bezier connection between identical points.")
    x_sign = 1.0 if p_end.x >= p_begin.x else -1.0
    p1 = Point2(p_begin.x + x_sign * d_m1, p_begin.y)
    p2 = Point2(p_end.x - x_sign * d_m2, p_end.y)
    return CubicBezier(p_begin, p1, p2, p_end)


def connect_bezier_perpendicular(p_begin: Point2, p_end: Point2, d_m1: float, d_m2: float, sign_flip: float) -> CubicBezier:
    """Legacy comparison helper retained for diagnostics only.

    This was the first reconstruction strategy. Keeping it separate makes the
    syntax/debugging history explicit instead of silently erasing it.
    """

    if d_m1 < 0 or d_m2 < 0:
        raise ValueError("Bezier control distances must be non-negative.")
    chord = p_end - p_begin
    if chord.length == 0:
        raise ValueError("Cannot build a Bezier connection between identical points.")
    perp = chord.normalized().perpendicular_left()
    p1 = p_begin + perp * (sign_flip * d_m1)
    p2 = p_end + perp * (sign_flip * d_m2)
    return CubicBezier(p_begin, p1, p2, p_end)
