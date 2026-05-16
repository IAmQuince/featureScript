"""
tributary_geometry
===================

Auxiliary Python geometry package for the Onshape Tributary Generator.

The package mirrors the recovered FeatureScript tributary layout rules so the
geometry can be inspected, tested, serialized, and exported before Onshape-side
FeatureScript validation.
"""

from .bezier import CubicBezier, bezier_derivative, bezier_point, connect_bezier_perpendicular, connect_bezier_rect
from .config import PAIRING_MODES, TributaryConfig
from .layout import Circle, ConstructionRectangle, FieldStub, TributaryBranch, TributaryLayout, build_tributary_layout
from .metrics import BranchMetrics, LayoutMetrics, compute_layout_metrics
from .vector2 import Point2, Vector2

__all__ = [
    "Point2",
    "Vector2",
    "CubicBezier",
    "bezier_point",
    "bezier_derivative",
    "connect_bezier_rect",
    "connect_bezier_perpendicular",
    "PAIRING_MODES",
    "TributaryConfig",
    "Circle",
    "ConstructionRectangle",
    "FieldStub",
    "TributaryBranch",
    "TributaryLayout",
    "build_tributary_layout",
    "BranchMetrics",
    "LayoutMetrics",
    "compute_layout_metrics",
]
