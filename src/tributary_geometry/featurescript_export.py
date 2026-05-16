from __future__ import annotations

from pathlib import Path

from .config import TributaryConfig


def emit_variable_table(config: TributaryConfig) -> str:
    """Emit a copy/paste helper table for Onshape variable studios.

    This does not use the Onshape API. It simply keeps the recovered Python-side config
    synchronized with the FeatureScript variable names expected by the recovered feature.
    """

    rows = [
        ("Channel_Num_Snakes", config.channel_num_snakes),
        ("Manifold_Length", config.manifold_length),
        ("Manifold_Reduction", config.manifold_reduction),
        ("Ladder_Width", config.ladder_width),
        ("FeedDump_Offset", config.feed_dump_offset),
        ("Tributary_Offset", config.tributary_offset),
        ("Feed_Diameter", config.feed_diameter),
        ("Dump_Diameter", config.dump_diameter),
        ("Snake_Width", config.snake_width),
        ("d_snake_M1", config.d_snake_m1),
        ("d_snake_M2", config.d_snake_m2),
        ("d_ladder_M1", config.d_ladder_m1),
        ("d_ladder_M2", config.d_ladder_m2),
    ]
    lines = ["# Onshape variable table", "# Units: use your Part Studio's intended length unit for dimensional values."]
    for name, value in rows:
        lines.append(f"{name} = {value}")
    return "\n".join(lines) + "\n"


def write_variable_table(config: TributaryConfig, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(emit_variable_table(config), encoding="utf-8")
    return out
