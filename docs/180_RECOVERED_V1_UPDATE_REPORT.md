# Recovered v1 Update Report

Date: 2026-05-16
Package: `20260516_03_tributary-generator`

## Why this update was needed

The previous GUI worked, but it did not resemble the intended physical tributary geometry closely enough. An older `Tributaryv1.docx` reference showed the missing construction logic: circle pairs, construction rectangles, and two Bezier boundaries per tributary.

## Geometry changes

Updated implementation now uses:

- recovered `2 * Channel_Num_Snakes + 1` central snake/ladder station count;
- feed count = `Channel_Num_Snakes - 1`;
- dump count = `Channel_Num_Snakes`;
- paired upper/lower channel boundaries rather than loose centerline-only curves;
- rectangular `d_M1`/`d_M2` Bezier control handles;
- visible construction rectangles and Bezier handles in SVG/GUI exports;
- explicit middle symmetry axis at `y = 0`;
- default `y_aligned_physical` pairing mode for the photo-like physical interpretation;
- retained `recovered_docx_v1` mode for transparency about the old written note.

## CFD-analysis additions

Added lightweight geometry metrics for CFD screening:

- centerline lengths
- channel width statistics
- hydraulic diameter
- wetted perimeter and wetted area proxy
- resistance proxy
- branch balance coefficients of variation
- curvature proxy
- branch spacing proxy
- symmetry error

## Verification performed locally

Local Python verification was run for:

- compile check
- unit tests
- smoke test
- diagnostic harness
- CLI generation of JSON/SVG/PNG/CSV/metrics outputs

The Onshape FeatureScript still requires Onshape-side compile/regeneration validation.
