from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class Vector2:
    """Small dependency-free 2D vector class used by the tributary geometry engine."""

    x: float
    y: float

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scale: float) -> "Vector2":
        return Vector2(self.x * scale, self.y * scale)

    def __rmul__(self, scale: float) -> "Vector2":
        return self.__mul__(scale)

    def __truediv__(self, scale: float) -> "Vector2":
        if scale == 0:
            raise ZeroDivisionError("Cannot divide Vector2 by zero.")
        return Vector2(self.x / scale, self.y / scale)

    @property
    def length(self) -> float:
        return hypot(self.x, self.y)

    def normalized(self) -> "Vector2":
        length = self.length
        if length == 0:
            return Vector2(0.0, 0.0)
        return self / length

    def perpendicular_left(self) -> "Vector2":
        return Vector2(-self.y, self.x)

    def perpendicular_right(self) -> "Vector2":
        return Vector2(self.y, -self.x)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def to_json(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}


Point2 = Vector2
