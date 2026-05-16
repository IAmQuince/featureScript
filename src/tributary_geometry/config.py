from __future__ import annotations

from dataclasses import dataclass, asdict

PAIRING_MODES = (
    "y_aligned_physical",
    "recovered_docx_v1",
)


@dataclass(frozen=True)
class TributaryConfig:
    """Dimensional inputs for the recovered tributary flow-field layout.

    Units are arbitrary but must be consistent. The defaults are millimeter-like
    values chosen for local preview and portfolio review, not final stack dimensions.

    pairing_mode controls how the asymmetric circle counts recovered from the old
    FeatureScript document are connected:

    - y_aligned_physical: default portfolio mode. It preserves the recovered
      circle counts, uses the midline symmetry implied by the old FeatureScript,
      and pairs source circles by matching y level: feed -> interior snake,
      dump -> ladder. This best matches the fabricated/photo-like tributary row.
    - recovered_docx_v1: literal written note from the old document, where feed
      circles pair to ladder circles and dump circles pair to snake circles. It is
      retained because the syntax/debugging history should not be hidden.

    channel_depth gives the GUI and metrics module a simple third dimension for
    first-pass CFD screening. The geometry remains 2D sketch geometry; depth is a
    user-controlled analysis assumption used for hydraulic diameter, wetted area,
    and resistance-proxy calculations.
    """

    channel_num_snakes: int = 8
    manifold_length: float = 120.0
    manifold_reduction: float = 0.0
    ladder_width: float = 2.0
    feed_dump_offset: float = 18.0
    tributary_offset: float = 28.0
    feed_diameter: float = 8.0
    dump_diameter: float = 8.0
    snake_width: float = 2.0
    d_snake_m1: float = 10.0
    d_snake_m2: float = 10.0
    d_ladder_m1: float = 10.0
    d_ladder_m2: float = 10.0
    channel_depth: float = 1.0
    top_bottom_feed_left_shift: bool = True
    pairing_mode: str = "y_aligned_physical"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.channel_num_snakes < 2:
            errors.append("channel_num_snakes must be >= 2 so at least one tributary can be created.")
        for field_name in (
            "manifold_length",
            "ladder_width",
            "feed_dump_offset",
            "tributary_offset",
            "feed_diameter",
            "dump_diameter",
            "snake_width",
            "d_snake_m1",
            "d_snake_m2",
            "d_ladder_m1",
            "d_ladder_m2",
            "channel_depth",
        ):
            value = getattr(self, field_name)
            if value <= 0:
                errors.append(f"{field_name} must be > 0; got {value!r}.")
        if self.manifold_reduction < 0:
            errors.append("manifold_reduction must be >= 0.")
        # The recovered central line length is manifold_length + 2*reduction - 2*ladder_width.
        # Keep it positive so the central snake/ladder line remains valid.
        if self.manifold_length + 2.0 * self.manifold_reduction - 2.0 * self.ladder_width <= 0:
            errors.append("central snake/ladder line length must be positive; reduce ladder_width or increase manifold_length/reduction.")
        if self.pairing_mode not in PAIRING_MODES:
            errors.append(f"pairing_mode must be one of {PAIRING_MODES}; got {self.pairing_mode!r}.")
        return errors

    def to_json(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict[str, object]) -> "TributaryConfig":
        allowed = set(cls.__dataclass_fields__.keys())
        clean = {k: v for k, v in data.items() if k in allowed}
        # Scenario files and GUI variables may preserve numbers as strings.
        int_fields = {"channel_num_snakes"}
        float_fields = {
            "manifold_length",
            "manifold_reduction",
            "ladder_width",
            "feed_dump_offset",
            "tributary_offset",
            "feed_diameter",
            "dump_diameter",
            "snake_width",
            "d_snake_m1",
            "d_snake_m2",
            "d_ladder_m1",
            "d_ladder_m2",
            "channel_depth",
        }
        bool_fields = {"top_bottom_feed_left_shift"}
        for key in list(clean):
            if key in int_fields:
                clean[key] = int(round(float(clean[key])))
            elif key in float_fields:
                clean[key] = float(clean[key])
            elif key in bool_fields:
                if isinstance(clean[key], str):
                    clean[key] = clean[key].strip().lower() in {"1", "true", "yes", "on"}
                else:
                    clean[key] = bool(clean[key])
            elif key == "pairing_mode":
                clean[key] = str(clean[key])
        return cls(**clean)
