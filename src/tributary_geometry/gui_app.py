from __future__ import annotations

"""Interactive Tributary Generator preview GUI.

This module is intentionally dependency-light. It uses Tkinter, which ships with
standard CPython, so a portfolio reviewer can run the live preview through the
root-level BAT launcher without first installing Qt or CAD tooling.

The GUI does not replace Onshape. It gives the reviewer a fast, visual way to
inspect the same parameter-driven tributary geometry that the FeatureScript is
intended to generate inside an Onshape sketch.
"""

import csv
import json
import math
import random
import time
import traceback
import webbrowser
from dataclasses import fields
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable

from .config import PAIRING_MODES, TributaryConfig
from .exporters import write_branch_csv, write_json, write_metrics_csv, write_metrics_json, write_metrics_summary_txt, write_svg
from .featurescript_export import write_variable_table
from .layout import TributaryLayout, build_tributary_layout
from .metrics import compute_layout_metrics
from .vector2 import Point2

APP_TITLE = "Tributary Generator - Live Geometry Preview"
SETTINGS_PATH = Path("reports/gui_settings.json")
AUTOSAVE_PATH = Path("reports/gui_autosave.json")
DEFAULT_EXPORT_DIR = Path("reports/gui_exports")


PARAM_SPECS: dict[str, dict[str, Any]] = {
    "channel_num_snakes": {
        "label": "Channel count / snakes",
        "type": "int",
        "min": 2,
        "max": 80,
        "step": 1,
        "help": "Number of main snake-circle stations. Branch count is N - 1.",
    },
    "manifold_length": {
        "label": "Manifold length",
        "type": "float",
        "min": 10.0,
        "max": 1000.0,
        "step": 1.0,
        "help": "Total vertical layout length before optional reduction.",
    },
    "manifold_reduction": {
        "label": "Manifold reduction",
        "type": "float",
        "min": 0.0,
        "max": 900.0,
        "step": 1.0,
        "help": "Length removed from the usable manifold span.",
    },
    "ladder_width": {
        "label": "Ladder channel width",
        "type": "float",
        "min": 0.1,
        "max": 80.0,
        "step": 0.1,
        "help": "Diameter-equivalent width for ladder construction circles.",
    },
    "feed_dump_offset": {
        "label": "Feed-to-dump offset",
        "type": "float",
        "min": 1.0,
        "max": 300.0,
        "step": 0.5,
        "help": "Horizontal spacing between feed and dump circle lines.",
    },
    "tributary_offset": {
        "label": "Dump-to-center offset",
        "type": "float",
        "min": 1.0,
        "max": 300.0,
        "step": 0.5,
        "help": "Horizontal spacing between dump and central snake/ladder line.",
    },
    "feed_diameter": {
        "label": "Feed diameter",
        "type": "float",
        "min": 0.1,
        "max": 120.0,
        "step": 0.1,
        "help": "Diameter of feed construction circles.",
    },
    "dump_diameter": {
        "label": "Dump diameter",
        "type": "float",
        "min": 0.1,
        "max": 120.0,
        "step": 0.1,
        "help": "Diameter of dump construction circles.",
    },
    "snake_width": {
        "label": "Snake channel width",
        "type": "float",
        "min": 0.1,
        "max": 80.0,
        "step": 0.1,
        "help": "Diameter-equivalent width for snake construction circles.",
    },
    "d_snake_m1": {
        "label": "Snake Bezier M1",
        "type": "float",
        "min": 0.0,
        "max": 250.0,
        "step": 0.25,
        "help": "First control distance for dump-to-snake branches.",
    },
    "d_snake_m2": {
        "label": "Snake Bezier M2",
        "type": "float",
        "min": 0.0,
        "max": 250.0,
        "step": 0.25,
        "help": "Second control distance for dump-to-snake branches.",
    },
    "d_ladder_m1": {
        "label": "Ladder Bezier M1",
        "type": "float",
        "min": 0.0,
        "max": 250.0,
        "step": 0.25,
        "help": "First control distance for feed-to-ladder branches.",
    },
    "d_ladder_m2": {
        "label": "Ladder Bezier M2",
        "type": "float",
        "min": 0.0,
        "max": 250.0,
        "step": 0.25,
        "help": "Second control distance for feed-to-ladder branches.",
    },
    "channel_depth": {
        "label": "Channel depth for CFD metrics",
        "type": "float",
        "min": 0.01,
        "max": 100.0,
        "step": 0.05,
        "help": "Analysis-only depth used for hydraulic diameter, wetted area, and resistance-proxy metrics.",
    },
    "pairing_mode": {
        "label": "Pairing mode",
        "type": "choice",
        "choices": PAIRING_MODES,
        "help": "Default y_aligned_physical uses midline symmetry and matches the photo-like tributary row. recovered_docx_v1 preserves the literal old note.",
    },
    "top_bottom_feed_left_shift": {
        "label": "Shift top/bottom feed circles left",
        "type": "bool",
        "help": "Recovered diagram rule: first and last feed circles shift left by one feed radius.",
    },
}

NUMERIC_PARAMS = [name for name, spec in PARAM_SPECS.items() if spec["type"] in {"int", "float"}]
WAVEFORMS = ["sin", "square", "saw", "triangle", "random_hold", "noise"]


class ScrollableFrame(ttk.Frame):
    """A reusable scrollable frame for dense dock-panel forms."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.inner.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_inner_width)
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel, add="+")

    def _sync_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_inner_width(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        if self.winfo_containing(event.x_root, event.y_root) is self.canvas or str(self.winfo_containing(event.x_root, event.y_root)).startswith(str(self.inner)):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class LfoSlot:
    """One low-frequency oscillator that can modulate a numeric parameter."""

    def __init__(self, index: int, on_change: Callable[[], None]) -> None:
        self.index = index
        self.on_change = on_change
        self.enabled = tk.BooleanVar(value=False)
        self.parameter = tk.StringVar(value=NUMERIC_PARAMS[0])
        self.waveform = tk.StringVar(value="sin")
        self.amplitude = tk.DoubleVar(value=1.0)
        self.frequency_hz = tk.DoubleVar(value=0.15)
        self.phase_degrees = tk.DoubleVar(value=0.0)
        self.center_offset = tk.DoubleVar(value=0.0)
        self.random_value = 0.0
        self.random_bucket = -1

    def value_at(self, elapsed_s: float) -> float:
        frequency = max(0.0, float(self.frequency_hz.get()))
        phase = math.radians(float(self.phase_degrees.get()))
        theta = 2.0 * math.pi * frequency * elapsed_s + phase
        wave = self.waveform.get()
        if wave == "sin":
            raw = math.sin(theta)
        elif wave == "square":
            raw = 1.0 if math.sin(theta) >= 0.0 else -1.0
        elif wave == "saw":
            cycle = (frequency * elapsed_s + phase / (2.0 * math.pi)) % 1.0 if frequency > 0 else 0.0
            raw = (2.0 * cycle) - 1.0
        elif wave == "triangle":
            cycle = (frequency * elapsed_s + phase / (2.0 * math.pi)) % 1.0 if frequency > 0 else 0.0
            raw = 4.0 * abs(cycle - 0.5) - 1.0
        elif wave == "random_hold":
            bucket = int(elapsed_s * max(frequency, 0.001))
            if bucket != self.random_bucket:
                self.random_bucket = bucket
                self.random_value = random.uniform(-1.0, 1.0)
            raw = self.random_value
        elif wave == "noise":
            raw = random.uniform(-1.0, 1.0)
        else:
            raw = 0.0
        return float(self.center_offset.get()) + float(self.amplitude.get()) * raw

    def as_json(self) -> dict[str, Any]:
        return {
            "enabled": bool(self.enabled.get()),
            "parameter": self.parameter.get(),
            "waveform": self.waveform.get(),
            "amplitude": float(self.amplitude.get()),
            "frequency_hz": float(self.frequency_hz.get()),
            "phase_degrees": float(self.phase_degrees.get()),
            "center_offset": float(self.center_offset.get()),
        }

    def from_json(self, data: dict[str, Any]) -> None:
        self.enabled.set(bool(data.get("enabled", False)))
        if data.get("parameter") in NUMERIC_PARAMS:
            self.parameter.set(str(data["parameter"]))
        if data.get("waveform") in WAVEFORMS:
            self.waveform.set(str(data["waveform"]))
        for key, var in (
            ("amplitude", self.amplitude),
            ("frequency_hz", self.frequency_hz),
            ("phase_degrees", self.phase_degrees),
            ("center_offset", self.center_offset),
        ):
            try:
                var.set(float(data.get(key, var.get())))
            except Exception:
                pass


class TributaryPreviewCanvas(ttk.Frame):
    """Central preview screen with zoom, pan, fit, grid, and live redraw."""

    def __init__(
        self,
        parent: tk.Misc,
        log: Callable[[str], None],
        show_labels: tk.BooleanVar,
        show_centerlines: tk.BooleanVar,
        show_grid: tk.BooleanVar,
        show_controls: tk.BooleanVar,
        show_symmetry_axis: tk.BooleanVar,
    ) -> None:
        super().__init__(parent)
        self.log = log
        self.canvas = tk.Canvas(self, background="#f7f7f7", highlightthickness=0)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.layout: TributaryLayout | None = None
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.base_scale = 7.0
        self.bounds = (-100.0, -100.0, 100.0, 100.0)
        self.drag_start: tuple[int, int, float, float] | None = None
        self.show_labels = show_labels
        self.show_centerlines = show_centerlines
        self.show_grid = show_grid
        self.show_controls = show_controls
        self.show_symmetry_axis = show_symmetry_axis

        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<ButtonPress-1>", self._start_pan)
        self.canvas.bind("<B1-Motion>", self._pan)
        self.canvas.bind("<MouseWheel>", self._wheel_zoom)
        self.canvas.bind("<Button-4>", self._wheel_zoom_linux)
        self.canvas.bind("<Button-5>", self._wheel_zoom_linux)

    def set_layout(self, layout: TributaryLayout) -> None:
        self.layout = layout
        self._update_bounds()
        self.redraw()

    def fit_to_view(self) -> None:
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._update_bounds()
        self.redraw()

    def reset_zoom(self) -> None:
        self.zoom = 1.0
        self.redraw()

    def _start_pan(self, event: tk.Event) -> None:
        self.drag_start = (event.x, event.y, self.pan_x, self.pan_y)

    def _pan(self, event: tk.Event) -> None:
        if not self.drag_start:
            return
        x0, y0, px, py = self.drag_start
        self.pan_x = px + (event.x - x0)
        self.pan_y = py + (event.y - y0)
        self.redraw()

    def _wheel_zoom(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 1.0 / 1.1
        self.zoom = min(30.0, max(0.05, self.zoom * factor))
        self.redraw()

    def _wheel_zoom_linux(self, event: tk.Event) -> None:
        factor = 1.1 if event.num == 4 else 1.0 / 1.1
        self.zoom = min(30.0, max(0.05, self.zoom * factor))
        self.redraw()

    def _all_points(self) -> list[Point2]:
        if not self.layout:
            return [Point2(-1, -1), Point2(1, 1)]
        points: list[Point2] = []
        for circle in self.layout.circles:
            points.extend(
                [
                    Point2(circle.center.x - circle.radius, circle.center.y - circle.radius),
                    Point2(circle.center.x + circle.radius, circle.center.y + circle.radius),
                ]
            )
        for branch in self.layout.branches:
            for curve_name in ("top", "bottom", "centerline"):
                points.extend(getattr(branch, curve_name).sample(20))
        return points or [Point2(-1, -1), Point2(1, 1)]

    def _update_bounds(self) -> None:
        points = self._all_points()
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        if math.isclose(min_x, max_x):
            max_x += 1.0
        if math.isclose(min_y, max_y):
            max_y += 1.0
        self.bounds = (min_x, min_y, max_x, max_y)
        cw = max(200, self.canvas.winfo_width())
        ch = max(200, self.canvas.winfo_height())
        drawing_w = max_x - min_x
        drawing_h = max_y - min_y
        self.base_scale = 0.86 * min(cw / drawing_w, ch / drawing_h)

    def _to_screen(self, p: Point2) -> tuple[float, float]:
        min_x, min_y, max_x, max_y = self.bounds
        scale = self.base_scale * self.zoom
        cw = max(200, self.canvas.winfo_width())
        ch = max(200, self.canvas.winfo_height())
        world_cx = (min_x + max_x) / 2.0
        world_cy = (min_y + max_y) / 2.0
        x = cw / 2.0 + (p.x - world_cx) * scale + self.pan_x
        y = ch / 2.0 - (p.y - world_cy) * scale + self.pan_y
        return (x, y)

    def _draw_grid(self) -> None:
        if not self.show_grid.get():
            return
        min_x, min_y, max_x, max_y = self.bounds
        span = max(max_x - min_x, max_y - min_y)
        raw_step = span / 10.0
        if raw_step <= 0:
            return
        pow10 = 10 ** math.floor(math.log10(raw_step))
        step = pow10
        if raw_step / pow10 > 5:
            step = 10 * pow10
        elif raw_step / pow10 > 2:
            step = 5 * pow10
        elif raw_step / pow10 > 1:
            step = 2 * pow10
        x = math.floor(min_x / step) * step
        while x <= max_x:
            p0 = self._to_screen(Point2(x, min_y))
            p1 = self._to_screen(Point2(x, max_y))
            self.canvas.create_line(p0[0], p0[1], p1[0], p1[1], fill="#e2e2e2")
            x += step
        y = math.floor(min_y / step) * step
        while y <= max_y:
            p0 = self._to_screen(Point2(min_x, y))
            p1 = self._to_screen(Point2(max_x, y))
            self.canvas.create_line(p0[0], p0[1], p1[0], p1[1], fill="#e2e2e2")
            y += step

    def _draw_curve(self, curve: Any, color: str, width: int, dash: tuple[int, int] | None = None) -> None:
        coords: list[float] = []
        for point in curve.sample(42):
            x, y = self._to_screen(point)
            coords.extend([x, y])
        self.canvas.create_line(*coords, fill=color, width=width, smooth=True, dash=dash)

    def redraw(self) -> None:
        self.canvas.delete("all")
        self._draw_grid()
        if not self.layout:
            self.canvas.create_text(30, 30, anchor="nw", text="No layout loaded.", fill="#444444")
            return

        if self.show_symmetry_axis.get():
            min_x, min_y, max_x, max_y = self.bounds
            p0 = self._to_screen(Point2(min_x, 0.0))
            p1 = self._to_screen(Point2(max_x, 0.0))
            self.canvas.create_line(p0[0], p0[1], p1[0], p1[1], fill="#777777", width=1, dash=(6, 5))
            self.canvas.create_text(p1[0] - 4, p1[1] - 6, anchor="e", text="symmetry midline", fill="#666666", font=("Segoe UI", 8))

        branch_colors = {
            "feed_to_ladder": "#943232",
            "feed_to_snake": "#943232",
            "dump_to_snake": "#2d5f9a",
            "dump_to_ladder": "#2d5f9a",
        }
        for branch in self.layout.branches:
            color = branch_colors.get(branch.branch_type, "#202020")
            self._draw_curve(branch.top, color, 2)
            self._draw_curve(branch.bottom, color, 2)
            if self.show_centerlines.get():
                self._draw_curve(branch.centerline, "#555555", 1, dash=(4, 4))
            if self.show_controls.get():
                for curve in (branch.top, branch.bottom):
                    pts = [curve.p0, curve.p1, curve.p2, curve.p3]
                    coords: list[float] = []
                    for p in pts:
                        coords.extend(self._to_screen(p))
                    self.canvas.create_line(*coords, fill="#aaaaaa", width=1, dash=(2, 3))

        circle_style = {
            "feed": ("#b33a3a", 2),
            "dump": ("#316cac", 2),
            "snake": ("#333333", 1),
            "ladder": ("#458545", 1),
        }
        scale = self.base_scale * self.zoom
        for circle in self.layout.circles:
            x, y = self._to_screen(circle.center)
            r = max(2.0, circle.radius * scale)
            color, width = circle_style.get(circle.role, ("#000000", 1))
            self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=width)
            if self.show_labels.get():
                self.canvas.create_text(x + r + 4, y, anchor="w", text=circle.id, font=("Segoe UI", 8), fill="#333333")

        min_x, min_y, max_x, max_y = self.bounds
        summary = f"{len(self.layout.circles)} circles | {len(self.layout.branches)} branches | bounds x:[{min_x:.1f},{max_x:.1f}] y:[{min_y:.1f},{max_y:.1f}] | zoom {self.zoom:.2f}x"
        self.canvas.create_rectangle(8, 8, 8 + 720, 34, fill="#ffffff", outline="#dddddd")
        self.canvas.create_text(16, 21, anchor="w", text=summary, font=("Segoe UI", 9), fill="#333333")


class TributaryGeneratorApp:
    """Main Tk application for live tributary exploration and export."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1320x850")
        self.root.minsize(980, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.style = ttk.Style(self.root)

        self.settings = self._load_json(SETTINGS_PATH, default={})
        self.theme = tk.StringVar(value=self.settings.get("theme", "light"))
        self.ui_scale = tk.DoubleVar(value=float(self.settings.get("ui_scale", 1.0)))
        self.autosave_enabled = tk.BooleanVar(value=bool(self.settings.get("autosave_enabled", True)))
        self.status_text = tk.StringVar(value="Ready")
        self.animation_running = tk.BooleanVar(value=False)
        self.show_labels = tk.BooleanVar(value=True)
        self.show_centerlines = tk.BooleanVar(value=True)
        self.show_grid = tk.BooleanVar(value=True)
        self.show_controls = tk.BooleanVar(value=False)
        self.show_symmetry_axis = tk.BooleanVar(value=True)
        self.animation_start_s = time.monotonic()
        self._pending_update: str | None = None
        self._last_config_json = ""

        self.param_vars: dict[str, tk.Variable] = {}
        default_config = TributaryConfig()
        for field in fields(TributaryConfig):
            value = getattr(default_config, field.name)
            spec = PARAM_SPECS[field.name]
            if spec["type"] == "bool":
                self.param_vars[field.name] = tk.BooleanVar(value=bool(value))
            elif spec["type"] == "int":
                self.param_vars[field.name] = tk.IntVar(value=int(value))
            elif spec["type"] == "float":
                self.param_vars[field.name] = tk.DoubleVar(value=float(value))
            elif spec["type"] == "choice":
                self.param_vars[field.name] = tk.StringVar(value=str(value))
            else:
                self.param_vars[field.name] = tk.StringVar(value=str(value))

        self.lfo_slots = [LfoSlot(i + 1, self.schedule_update) for i in range(4)]
        self.map_x_param = tk.StringVar(value="feed_dump_offset")
        self.map_y_param = tk.StringVar(value="tributary_offset")
        self.map_x_min = tk.DoubleVar(value=8.0)
        self.map_x_max = tk.DoubleVar(value=50.0)
        self.map_y_min = tk.DoubleVar(value=8.0)
        self.map_y_max = tk.DoubleVar(value=60.0)
        self.map_steps = tk.IntVar(value=8)
        self.metrics_text_var = tk.StringVar(value="Metrics will update after the first layout build.")

        self._configure_style()
        self._build_menu()
        self._build_shell()
        self._build_status_bar()
        self._restore_autosave_if_present()
        self.schedule_update("startup")
        self.root.after(33, self._animation_tick)

    def _configure_style(self) -> None:
        try:
            scale = max(0.75, min(2.0, float(self.ui_scale.get())))
            self.root.tk.call("tk", "scaling", scale)
        except Exception:
            pass
        if self.theme.get() == "dark":
            self.root.configure(bg="#202124")
            self.style.configure("TFrame", background="#202124")
            self.style.configure("TLabel", background="#202124", foreground="#eeeeee")
            self.style.configure("TCheckbutton", background="#202124", foreground="#eeeeee")
            self.style.configure("TLabelframe", background="#202124", foreground="#eeeeee")
            self.style.configure("TLabelframe.Label", background="#202124", foreground="#eeeeee")
        else:
            self.root.configure(bg="#f3f3f3")
            self.style.configure("TFrame", background="#f3f3f3")
            self.style.configure("TLabel", background="#f3f3f3", foreground="#222222")
            self.style.configure("TCheckbutton", background="#f3f3f3", foreground="#222222")
            self.style.configure("TLabelframe", background="#f3f3f3", foreground="#222222")
            self.style.configure("TLabelframe.Label", background="#f3f3f3", foreground="#222222")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open Scenario JSON...", command=self.open_scenario)
        file_menu.add_command(label="Save Scenario JSON...", command=self.save_scenario)
        file_menu.add_separator()
        file_menu.add_command(label="Export SVG...", command=lambda: self.export_one("svg"))
        file_menu.add_command(label="Export JSON...", command=lambda: self.export_one("json"))
        file_menu.add_command(label="Export CSV Samples...", command=lambda: self.export_one("csv"))
        file_menu.add_command(label="Export Onshape Variable Table...", command=lambda: self.export_one("vars"))
        file_menu.add_separator()
        file_menu.add_command(label="Export CFD Metrics Summary...", command=lambda: self.export_one("metrics_txt"))
        file_menu.add_command(label="Export CFD Metrics JSON...", command=lambda: self.export_one("metrics_json"))
        file_menu.add_command(label="Export Branch Metrics CSV...", command=lambda: self.export_one("metrics_csv"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label="Fit Geometry to View", command=lambda: self.preview.fit_to_view())
        view_menu.add_command(label="Reset Zoom", command=lambda: self.preview.reset_zoom())
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Labels", variable=self.show_labels, command=self._redraw_preview)
        view_menu.add_checkbutton(label="Show Centerlines", variable=self.show_centerlines, command=self._redraw_preview)
        view_menu.add_checkbutton(label="Show Grid", variable=self.show_grid, command=self._redraw_preview)
        view_menu.add_checkbutton(label="Show Bezier Control Polygons", variable=self.show_controls, command=self._redraw_preview)
        view_menu.add_checkbutton(label="Show Symmetry Midline", variable=self.show_symmetry_axis, command=self._redraw_preview)
        view_menu.add_separator()
        view_menu.add_command(label="Dock Panel Right", command=lambda: self.dock_panel("right"))
        view_menu.add_command(label="Dock Panel Left", command=lambda: self.dock_panel("left"))
        view_menu.add_command(label="Dock Panel Bottom", command=lambda: self.dock_panel("bottom"))
        view_menu.add_command(label="Detach Panel", command=self.detach_panel)
        menubar.add_cascade(label="View", menu=view_menu)

        settings_menu = tk.Menu(menubar, tearoff=False)
        settings_menu.add_radiobutton(label="Light Theme", variable=self.theme, value="light", command=self.apply_settings)
        settings_menu.add_radiobutton(label="Dark Theme", variable=self.theme, value="dark", command=self.apply_settings)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label="Autosave/Restore Scenario", variable=self.autosave_enabled, command=self.apply_settings)
        settings_menu.add_command(label="UI Scale 90%", command=lambda: self.set_ui_scale(0.9))
        settings_menu.add_command(label="UI Scale 100%", command=lambda: self.set_ui_scale(1.0))
        settings_menu.add_command(label="UI Scale 125%", command=lambda: self.set_ui_scale(1.25))
        settings_menu.add_command(label="UI Scale 150%", command=lambda: self.set_ui_scale(1.5))
        menubar.add_cascade(label="Settings", menu=settings_menu)

        run_menu = tk.Menu(menubar, tearoff=False)
        run_menu.add_checkbutton(label="Run LFO Animation", variable=self.animation_running, command=self.animation_state_changed)
        run_menu.add_command(label="Reset LFO Clock", command=self.reset_lfo_clock)
        run_menu.add_command(label="Generate Parameter-Space Map CSV", command=self.generate_space_map)
        menubar.add_cascade(label="Run", menu=run_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="Open Portfolio Guide", command=lambda: self._open_path(Path("PORTFOLIO_REVIEW_GUIDE.md")))
        help_menu.add_command(label="Open Syntax/Debugging History", command=lambda: self._open_path(Path("docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md")))
        help_menu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.configure(menu=menubar)

    def _build_shell(self) -> None:
        self.main = ttk.Frame(self.root)
        self.main.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.preview = TributaryPreviewCanvas(
            self.main,
            self.log,
            self.show_labels,
            self.show_centerlines,
            self.show_grid,
            self.show_controls,
            self.show_symmetry_axis,
        )
        self.panel_host = ttk.Frame(self.main)
        self.panel_window: tk.Toplevel | None = None
        self.panel_dock = self.settings.get("panel_dock", "right")
        self._build_panel_contents(self.panel_host)
        self.dock_panel(self.panel_dock)

    def _build_status_bar(self) -> None:
        status = ttk.Frame(self.root)
        status.grid(row=1, column=0, sticky="ew")
        ttk.Label(status, textvariable=self.status_text).pack(side="left", padx=6, pady=3)
        ttk.Button(status, text="Fit", command=self.preview.fit_to_view).pack(side="right", padx=4)
        ttk.Button(status, text="Export SVG", command=lambda: self.export_one("svg")).pack(side="right", padx=4)

    def _build_panel_contents(self, parent: tk.Misc) -> None:
        for child in parent.winfo_children():
            child.destroy()
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)
        self._build_parameter_tab(notebook)
        self._build_lfo_tab(notebook)
        self._build_space_map_tab(notebook)
        self._build_metrics_tab(notebook)
        self._build_export_tab(notebook)
        self._build_log_tab(notebook)

    def _build_parameter_tab(self, notebook: ttk.Notebook) -> None:
        tab = ScrollableFrame(notebook)
        notebook.add(tab, text="Parameters")
        row = 0
        intro = ttk.Label(
            tab.inner,
            text="Edit the same recovered geometry variables used by the FeatureScript. Changes redraw immediately.",
            wraplength=330,
        )
        intro.grid(row=row, column=0, columnspan=3, sticky="ew", padx=8, pady=(8, 10))
        row += 1
        for name, spec in PARAM_SPECS.items():
            var = self.param_vars[name]
            label = ttk.Label(tab.inner, text=spec["label"])
            label.grid(row=row, column=0, sticky="w", padx=8, pady=4)
            if spec["type"] == "bool":
                widget = ttk.Checkbutton(tab.inner, variable=var, command=self.schedule_update)
                widget.grid(row=row, column=1, sticky="w", padx=8, pady=4)
            elif spec["type"] == "choice":
                choices = list(spec.get("choices", []))
                widget = ttk.OptionMenu(tab.inner, var, var.get(), *choices, command=lambda _v, _name=name: self.schedule_update(f"choice:{_name}"))
                widget.grid(row=row, column=1, sticky="ew", padx=8, pady=4)
            else:
                widget = ttk.Spinbox(
                    tab.inner,
                    from_=spec["min"],
                    to=spec["max"],
                    increment=spec["step"],
                    textvariable=var,
                    width=12,
                    command=self.schedule_update,
                )
                widget.grid(row=row, column=1, sticky="ew", padx=8, pady=4)
                slider = ttk.Scale(
                    tab.inner,
                    from_=spec["min"],
                    to=spec["max"],
                    variable=var,
                    command=lambda _v, _name=name: self.schedule_update(f"slider:{_name}"),
                )
                slider.grid(row=row + 1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))
                row += 1
            help_text = spec.get("help", "")
            ttk.Label(tab.inner, text=help_text, wraplength=330, foreground="#666666").grid(
                row=row, column=0, columnspan=3, sticky="ew", padx=8, pady=(0, 8)
            )
            var.trace_add("write", lambda *_args: self.schedule_update("trace"))
            row += 1
        ttk.Button(tab.inner, text="Reset to Defaults", command=self.reset_parameters).grid(row=row, column=0, sticky="w", padx=8, pady=10)
        ttk.Button(tab.inner, text="Fit Preview", command=self.preview.fit_to_view).grid(row=row, column=1, sticky="e", padx=8, pady=10)
        tab.inner.grid_columnconfigure(1, weight=1)

    def _build_lfo_tab(self, notebook: ttk.Notebook) -> None:
        tab = ScrollableFrame(notebook)
        notebook.add(tab, text="LFO Animation")
        ttk.Label(
            tab.inner,
            text="Automate selected numeric variables with low-frequency oscillators. Enable one or more slots, press Run, and the preview updates live.",
            wraplength=360,
        ).grid(row=0, column=0, columnspan=6, sticky="ew", padx=8, pady=8)
        headers = ["On", "Parameter", "Wave", "Amp", "Hz", "Phase", "Offset"]
        for col, text in enumerate(headers):
            ttk.Label(tab.inner, text=text).grid(row=1, column=col, padx=4, pady=4)
        for idx, slot in enumerate(self.lfo_slots, start=2):
            ttk.Checkbutton(tab.inner, variable=slot.enabled, command=self.schedule_update).grid(row=idx, column=0, padx=4, pady=4)
            ttk.OptionMenu(tab.inner, slot.parameter, slot.parameter.get(), *NUMERIC_PARAMS, command=lambda _v: self.schedule_update()).grid(row=idx, column=1, sticky="ew", padx=4, pady=4)
            ttk.OptionMenu(tab.inner, slot.waveform, slot.waveform.get(), *WAVEFORMS, command=lambda _v: self.schedule_update()).grid(row=idx, column=2, sticky="ew", padx=4, pady=4)
            for col, var, width in (
                (3, slot.amplitude, 7),
                (4, slot.frequency_hz, 6),
                (5, slot.phase_degrees, 7),
                (6, slot.center_offset, 7),
            ):
                spin = ttk.Spinbox(tab.inner, textvariable=var, from_=-9999, to=9999, increment=0.1, width=width, command=self.schedule_update)
                spin.grid(row=idx, column=col, padx=4, pady=4)
                var.trace_add("write", lambda *_args: self.schedule_update("lfo"))
        control_row = 8
        ttk.Button(tab.inner, text="Run / Pause", command=self.toggle_animation).grid(row=control_row, column=0, columnspan=2, sticky="ew", padx=6, pady=10)
        ttk.Button(tab.inner, text="Reset LFO Clock", command=self.reset_lfo_clock).grid(row=control_row, column=2, columnspan=2, sticky="ew", padx=6, pady=10)
        ttk.Button(tab.inner, text="Disable All", command=self.disable_lfos).grid(row=control_row, column=4, columnspan=3, sticky="ew", padx=6, pady=10)
        for col in range(7):
            tab.inner.grid_columnconfigure(col, weight=1)

    def _build_space_map_tab(self, notebook: ttk.Notebook) -> None:
        tab = ScrollableFrame(notebook)
        notebook.add(tab, text="Space Map")
        ttk.Label(
            tab.inner,
            text="Sweep two variables across a bounded grid and export metrics for the generated geometry. This is a light parameter-space mapper, not an optimizer.",
            wraplength=360,
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=8, pady=8)
        controls = [
            ("X parameter", self.map_x_param, "option"),
            ("X min", self.map_x_min, "float"),
            ("X max", self.map_x_max, "float"),
            ("Y parameter", self.map_y_param, "option"),
            ("Y min", self.map_y_min, "float"),
            ("Y max", self.map_y_max, "float"),
            ("Steps per axis", self.map_steps, "int"),
        ]
        row = 1
        for label, var, kind in controls:
            ttk.Label(tab.inner, text=label).grid(row=row, column=0, sticky="w", padx=8, pady=5)
            if kind == "option":
                ttk.OptionMenu(tab.inner, var, var.get(), *NUMERIC_PARAMS).grid(row=row, column=1, sticky="ew", padx=8, pady=5)
            else:
                ttk.Spinbox(tab.inner, textvariable=var, from_=-9999, to=9999, increment=1, width=12).grid(row=row, column=1, sticky="ew", padx=8, pady=5)
            row += 1
        ttk.Button(tab.inner, text="Generate Space Map CSV", command=self.generate_space_map).grid(row=row, column=0, columnspan=2, sticky="ew", padx=8, pady=12)
        tab.inner.grid_columnconfigure(1, weight=1)


    def _build_metrics_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="CFD Metrics")
        ttk.Label(
            tab,
            text="First-pass geometry metrics for screening before CFD. These are not a CFD solver; they help compare candidate layouts before CAD/mesh export.",
            wraplength=390,
        ).pack(anchor="w", padx=10, pady=(10, 6))
        text = tk.Text(tab, height=20, wrap="none", font=("Consolas", 9))
        ybar = ttk.Scrollbar(tab, orient="vertical", command=text.yview)
        xbar = ttk.Scrollbar(tab, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=6)
        ybar.pack(side="right", fill="y", pady=6)
        xbar.pack(side="bottom", fill="x", padx=10)
        self.metrics_text = text
        ttk.Button(tab, text="Export Metrics Summary", command=lambda: self.export_one("metrics_txt")).pack(fill="x", padx=10, pady=(4, 2))
        ttk.Button(tab, text="Export Metrics JSON", command=lambda: self.export_one("metrics_json")).pack(fill="x", padx=10, pady=2)
        ttk.Button(tab, text="Export Branch Metrics CSV", command=lambda: self.export_one("metrics_csv")).pack(fill="x", padx=10, pady=(2, 8))

    def _update_metrics_text(self, layout: TributaryLayout) -> None:
        try:
            metrics = compute_layout_metrics(layout)
            lines = [
                "CFD-screening metrics (geometric proxies only)",
                "================================================",
                "",
                f"pairing_mode: {layout.config.pairing_mode}",
                f"channel_depth: {layout.config.channel_depth:.6g}",
                "",
            ]
            for key, value in metrics.summary_rows():
                if isinstance(value, float):
                    lines.append(f"{key:34s}: {value:.8g}")
                else:
                    lines.append(f"{key:34s}: {value}")
            lines.extend([
                "",
                "Interpretation notes:",
                "- total_centerline_length and total_planform_area_proxy are useful quick size/load checks.",
                "- resistance_proxy uses L / hydraulic_diameter^4 as a relative laminar-flow screening proxy.",
                "- length_cv and resistance_proxy_cv flag balance mismatch between parallel tributary branches.",
                "- symmetry_* values check mirror behavior about the recovered midline y=0.",
            ])
            if hasattr(self, "metrics_text"):
                self.metrics_text.delete("1.0", "end")
                self.metrics_text.insert("end", "\n".join(lines))
        except Exception:
            if hasattr(self, "metrics_text"):
                self.metrics_text.delete("1.0", "end")
                self.metrics_text.insert("end", traceback.format_exc())

    def _build_export_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Exports")
        ttk.Label(tab, text="Export the current live geometry preview for review, CAD setup, or diagnostics.").pack(anchor="w", padx=10, pady=(10, 4))
        for label, kind in (
            ("Export SVG Preview", "svg"),
            ("Export Geometry JSON", "json"),
            ("Export Branch Samples CSV", "csv"),
            ("Export Onshape Variable Table", "vars"),
            ("Export CFD Metrics Summary", "metrics_txt"),
            ("Export CFD Metrics JSON", "metrics_json"),
            ("Export Branch Metrics CSV", "metrics_csv"),
        ):
            ttk.Button(tab, text=label, command=lambda k=kind: self.export_one(k)).pack(fill="x", padx=10, pady=4)
        ttk.Button(tab, text="Export Full Bundle", command=self.export_bundle).pack(fill="x", padx=10, pady=(14, 4))
        ttk.Label(tab, text="Tip: the SVG preview is the fastest artifact for portfolio reviewers to understand visually.", wraplength=360).pack(anchor="w", padx=10, pady=8)

    def _build_log_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Logs")
        self.log_text = tk.Text(tab, height=12, wrap="word", font=("Consolas", 9))
        ybar = ttk.Scrollbar(tab, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=ybar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        ttk.Button(tab, text="Clear Log", command=lambda: self.log_text.delete("1.0", "end")).grid(row=1, column=0, sticky="ew", padx=6, pady=5)
        self.log("GUI initialized.")

    def dock_panel(self, position: str) -> None:
        self.panel_dock = position if position in {"left", "right", "bottom"} else "right"
        if self.panel_window is not None:
            self.panel_window.destroy()
            self.panel_window = None
            self.panel_host = ttk.Frame(self.main)
            self._build_panel_contents(self.panel_host)
        for child in self.main.winfo_children():
            child.grid_forget()
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=0)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=0)
        if self.panel_dock == "left":
            self.panel_host.grid(row=0, column=0, sticky="nsew")
            self.preview.grid(row=0, column=1, sticky="nsew")
            self.main.grid_columnconfigure(0, weight=0, minsize=410)
            self.main.grid_columnconfigure(1, weight=1)
        elif self.panel_dock == "bottom":
            self.preview.grid(row=0, column=0, sticky="nsew")
            self.panel_host.grid(row=1, column=0, sticky="nsew")
            self.main.grid_rowconfigure(0, weight=1)
            self.main.grid_rowconfigure(1, weight=0, minsize=260)
        else:
            self.preview.grid(row=0, column=0, sticky="nsew")
            self.panel_host.grid(row=0, column=1, sticky="nsew")
            self.main.grid_columnconfigure(0, weight=1)
            self.main.grid_columnconfigure(1, weight=0, minsize=430)
        self.schedule_update("dock")
        self.log(f"Panel docked {self.panel_dock}.")

    def detach_panel(self) -> None:
        if self.panel_window is not None:
            self.panel_window.lift()
            return
        self.panel_host.grid_forget()
        self.panel_window = tk.Toplevel(self.root)
        self.panel_window.title("Tributary Generator Controls")
        self.panel_window.geometry("520x720")
        self.panel_window.protocol("WM_DELETE_WINDOW", lambda: self.dock_panel(self.panel_dock))
        self.panel_host = ttk.Frame(self.panel_window)
        self.panel_host.pack(fill="both", expand=True)
        self._build_panel_contents(self.panel_host)
        self.preview.grid(row=0, column=0, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)
        self.log("Panel detached.")

    def _current_base_config(self) -> TributaryConfig:
        data: dict[str, Any] = {}
        for name, var in self.param_vars.items():
            spec = PARAM_SPECS[name]
            value = var.get()
            if spec["type"] == "int":
                value = int(round(float(value)))
            elif spec["type"] == "float":
                value = float(value)
            elif spec["type"] == "bool":
                value = bool(value)
            elif spec["type"] == "choice":
                value = str(value)
            data[name] = value
        return TributaryConfig.from_json(data)

    def _current_effective_config(self) -> TributaryConfig:
        data = self._current_base_config().to_json()
        if self.animation_running.get():
            elapsed = time.monotonic() - self.animation_start_s
            for slot in self.lfo_slots:
                if not slot.enabled.get():
                    continue
                name = slot.parameter.get()
                if name not in NUMERIC_PARAMS:
                    continue
                spec = PARAM_SPECS[name]
                base = float(data[name])
                value = base + slot.value_at(elapsed)
                value = min(float(spec["max"]), max(float(spec["min"]), value))
                if spec["type"] == "int":
                    value = int(round(value))
                data[name] = value
        return TributaryConfig.from_json(data)

    def schedule_update(self, reason: str | None = None) -> None:
        if self._pending_update is not None:
            return
        self._pending_update = reason or "update"
        self.root.after(30, self._rebuild_layout)

    def _rebuild_layout(self) -> None:
        self._pending_update = None
        try:
            config = self._current_effective_config()
            errors = config.validate()
            if errors:
                self.status_text.set("Invalid configuration: " + errors[0])
                return
            layout = build_tributary_layout(config)
            current_json = json.dumps(config.to_json(), sort_keys=True)
            self.preview.set_layout(layout)
            self._update_metrics_text(layout)
            metrics = compute_layout_metrics(layout)
            self.status_text.set(f"Live preview: {len(layout.circles)} circles, {len(layout.branches)} branches | symmetry mean error {metrics.symmetry_mean_error:.3g}")
            if current_json != self._last_config_json:
                self._last_config_json = current_json
                if self.autosave_enabled.get():
                    self._write_autosave()
        except Exception as exc:
            self.status_text.set(f"Error: {exc}")
            self.log(traceback.format_exc())

    def _animation_tick(self) -> None:
        if self.animation_running.get():
            self.schedule_update("animation")
        self.root.after(33, self._animation_tick)

    def toggle_animation(self) -> None:
        self.animation_running.set(not self.animation_running.get())
        self.animation_state_changed()

    def animation_state_changed(self) -> None:
        if self.animation_running.get():
            self.animation_start_s = time.monotonic()
            self.log("LFO animation started.")
        else:
            self.log("LFO animation paused.")
        self.schedule_update("toggle_animation")

    def reset_lfo_clock(self) -> None:
        self.animation_start_s = time.monotonic()
        for slot in self.lfo_slots:
            slot.random_bucket = -1
        self.log("LFO clock reset.")
        self.schedule_update("reset_lfo")

    def disable_lfos(self) -> None:
        for slot in self.lfo_slots:
            slot.enabled.set(False)
        self.animation_running.set(False)
        self.log("All LFO slots disabled.")
        self.schedule_update("disable_lfos")

    def reset_parameters(self) -> None:
        defaults = TributaryConfig()
        for field in fields(TributaryConfig):
            self.param_vars[field.name].set(getattr(defaults, field.name))
        self.log("Parameters reset to defaults.")
        self.schedule_update("reset")

    def apply_settings(self) -> None:
        self._configure_style()
        self._save_settings()
        self.log("Settings applied.")

    def set_ui_scale(self, value: float) -> None:
        self.ui_scale.set(value)
        self.apply_settings()
        messagebox.showinfo("UI scale", "UI scale was saved. Restart the launcher for the cleanest full-scale refresh.")

    def _scenario_json(self) -> dict[str, Any]:
        return {
            "config": self._current_base_config().to_json(),
            "lfo_slots": [slot.as_json() for slot in self.lfo_slots],
            "view": {
                "show_labels": bool(self.show_labels.get()),
                "show_centerlines": bool(self.show_centerlines.get()),
                "show_grid": bool(self.show_grid.get()),
                "show_controls": bool(self.show_controls.get()),
                "show_symmetry_axis": bool(self.show_symmetry_axis.get()),
                "panel_dock": self.panel_dock,
            },
        }

    def _load_scenario_json(self, data: dict[str, Any]) -> None:
        config = TributaryConfig.from_json(data.get("config", {}))
        for field in fields(TributaryConfig):
            self.param_vars[field.name].set(getattr(config, field.name))
        for slot, slot_data in zip(self.lfo_slots, data.get("lfo_slots", [])):
            if isinstance(slot_data, dict):
                slot.from_json(slot_data)
        view = data.get("view", {})
        if isinstance(view, dict):
            for key, var in (
                ("show_labels", self.show_labels),
                ("show_centerlines", self.show_centerlines),
                ("show_grid", self.show_grid),
                ("show_controls", self.show_controls),
                ("show_symmetry_axis", self.show_symmetry_axis),
            ):
                if key in view:
                    var.set(bool(view[key]))
            if view.get("panel_dock") in {"left", "right", "bottom"}:
                self.dock_panel(str(view["panel_dock"]))
        self.log("Scenario loaded.")
        self.schedule_update("scenario_loaded")

    def open_scenario(self) -> None:
        path = filedialog.askopenfilename(title="Open Tributary Scenario", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self._load_scenario_json(data)
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))
            self.log(traceback.format_exc())

    def save_scenario(self) -> None:
        path = filedialog.asksaveasfilename(title="Save Tributary Scenario", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(self._scenario_json(), indent=2), encoding="utf-8")
            self.log(f"Scenario saved: {path}")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))
            self.log(traceback.format_exc())

    def _write_autosave(self) -> None:
        try:
            AUTOSAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
            AUTOSAVE_PATH.write_text(json.dumps(self._scenario_json(), indent=2), encoding="utf-8")
        except Exception:
            pass

    def _restore_autosave_if_present(self) -> None:
        if not self.autosave_enabled.get() or not AUTOSAVE_PATH.exists():
            return
        try:
            self._load_scenario_json(json.loads(AUTOSAVE_PATH.read_text(encoding="utf-8")))
            self.log("Autosave restored.")
        except Exception as exc:
            self.log(f"Autosave restore skipped: {exc}")

    def export_one(self, kind: str) -> None:
        try:
            layout = build_tributary_layout(self._current_effective_config())
            default_name = {
                "svg": "tributary_layout.svg",
                "json": "tributary_layout.json",
                "csv": "tributary_branch_samples.csv",
                "vars": "onshape_variable_table.txt",
                "metrics_json": "cfd_metrics.json",
                "metrics_csv": "cfd_branch_metrics.csv",
                "metrics_txt": "cfd_metrics_summary.txt",
            }[kind]
            path = filedialog.asksaveasfilename(title=f"Export {kind.upper()}", initialfile=default_name)
            if not path:
                return
            out_path = Path(path)
            if kind == "svg":
                write_svg(layout, out_path)
            elif kind == "json":
                write_json(layout, out_path)
            elif kind == "csv":
                write_branch_csv(layout, out_path)
            elif kind == "vars":
                write_variable_table(layout.config, out_path)
            elif kind == "metrics_json":
                write_metrics_json(layout, out_path)
            elif kind == "metrics_csv":
                write_metrics_csv(layout, out_path)
            elif kind == "metrics_txt":
                write_metrics_summary_txt(layout, out_path)
            self.log(f"Exported {kind.upper()}: {out_path}")
            self.status_text.set(f"Exported {out_path.name}")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
            self.log(traceback.format_exc())

    def export_bundle(self) -> None:
        try:
            out_dir = filedialog.askdirectory(title="Choose Export Bundle Folder")
            if not out_dir:
                return
            out = Path(out_dir)
            out.mkdir(parents=True, exist_ok=True)
            layout = build_tributary_layout(self._current_effective_config())
            write_svg(layout, out / "tributary_layout.svg")
            write_json(layout, out / "tributary_layout.json")
            write_branch_csv(layout, out / "tributary_branch_samples.csv")
            write_variable_table(layout.config, out / "onshape_variable_table.txt")
            write_metrics_json(layout, out / "cfd_metrics.json")
            write_metrics_csv(layout, out / "cfd_branch_metrics.csv")
            write_metrics_summary_txt(layout, out / "cfd_metrics_summary.txt")
            (out / "tributary_scenario.json").write_text(json.dumps(self._scenario_json(), indent=2), encoding="utf-8")
            self.log(f"Exported full bundle: {out}")
            self.status_text.set(f"Exported bundle to {out}")
        except Exception as exc:
            messagebox.showerror("Export bundle failed", str(exc))
            self.log(traceback.format_exc())

    def generate_space_map(self) -> None:
        try:
            x_name = self.map_x_param.get()
            y_name = self.map_y_param.get()
            steps = max(2, min(80, int(self.map_steps.get())))
            x_min, x_max = float(self.map_x_min.get()), float(self.map_x_max.get())
            y_min, y_max = float(self.map_y_min.get()), float(self.map_y_max.get())
            path = filedialog.asksaveasfilename(title="Save Parameter Space Map", defaultextension=".csv", initialfile="tributary_parameter_space_map.csv", filetypes=[("CSV files", "*.csv")])
            if not path:
                return
            base = self._current_base_config().to_json()
            rows: list[dict[str, Any]] = []
            for ix in range(steps):
                x_val = x_min + (x_max - x_min) * ix / (steps - 1)
                for iy in range(steps):
                    y_val = y_min + (y_max - y_min) * iy / (steps - 1)
                    data = dict(base)
                    data[x_name] = int(round(x_val)) if PARAM_SPECS[x_name]["type"] == "int" else x_val
                    data[y_name] = int(round(y_val)) if PARAM_SPECS[y_name]["type"] == "int" else y_val
                    try:
                        config = TributaryConfig.from_json(data)
                        errors = config.validate()
                        if errors:
                            rows.append({"x_param": x_name, "x_value": x_val, "y_param": y_name, "y_value": y_val, "status": "invalid", "message": errors[0]})
                            continue
                        layout = build_tributary_layout(config)
                        points = self.preview._all_points() if False else []
                        all_points: list[Point2] = []
                        for circle in layout.circles:
                            all_points.append(circle.center)
                        for branch in layout.branches:
                            all_points.extend(branch.top.sample(8))
                            all_points.extend(branch.bottom.sample(8))
                        min_x = min(p.x for p in all_points)
                        max_x = max(p.x for p in all_points)
                        min_y = min(p.y for p in all_points)
                        max_y = max(p.y for p in all_points)
                        metrics = compute_layout_metrics(layout)
                        rows.append(
                            {
                                "x_param": x_name,
                                "x_value": x_val,
                                "y_param": y_name,
                                "y_value": y_val,
                                "status": "ok",
                                "circles": len(layout.circles),
                                "branches": len(layout.branches),
                                "bounds_width": max_x - min_x,
                                "bounds_height": max_y - min_y,
                                "total_centerline_length": metrics.total_centerline_length,
                                "average_boundary_width": metrics.average_boundary_width,
                                "min_boundary_width": metrics.min_boundary_width,
                                "hydraulic_diameter_average": metrics.hydraulic_diameter_average,
                                "resistance_proxy_cv": metrics.resistance_proxy_cv,
                                "length_cv": metrics.length_cv,
                                "symmetry_mean_error": metrics.symmetry_mean_error,
                                "message": "",
                            }
                        )
                    except Exception as exc:
                        rows.append({"x_param": x_name, "x_value": x_val, "y_param": y_name, "y_value": y_val, "status": "error", "message": str(exc)})
            fieldnames = ["x_param", "x_value", "y_param", "y_value", "status", "circles", "branches", "bounds_width", "bounds_height", "total_centerline_length", "average_boundary_width", "min_boundary_width", "hydraulic_diameter_average", "resistance_proxy_cv", "length_cv", "symmetry_mean_error", "message"]
            with Path(path).open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            self.log(f"Parameter-space map written: {path} ({len(rows)} samples)")
            self.status_text.set(f"Space map exported: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Space map failed", str(exc))
            self.log(traceback.format_exc())

    def _redraw_preview(self) -> None:
        self.preview.redraw()

    def _save_settings(self) -> None:
        try:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "theme": self.theme.get(),
                "ui_scale": float(self.ui_scale.get()),
                "autosave_enabled": bool(self.autosave_enabled.get()),
                "panel_dock": self.panel_dock,
            }
            SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    @staticmethod
    def _load_json(path: Path, default: Any) -> Any:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
        return default

    def _open_path(self, path: Path) -> None:
        try:
            webbrowser.open(path.resolve().as_uri())
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))

    def about(self) -> None:
        messagebox.showinfo(
            "About Tributary Generator",
            "Tributary Generator live preview\n\n"
            "A local Python geometry explorer for a reconstructed Onshape FeatureScript tributary generator.\n\n"
            "The GUI previews parameter-driven feed/dump/snake/ladder tributary geometry, supports live LFO animation, and exports SVG/JSON/CSV/Onshape variable tables.",
        )

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        text = f"[{timestamp}] {message}\n"
        if hasattr(self, "log_text"):
            self.log_text.insert("end", text)
            self.log_text.see("end")
        else:
            print(text, end="")

    def close(self) -> None:
        self._save_settings()
        if self.autosave_enabled.get():
            self._write_autosave()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    app = TributaryGeneratorApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
