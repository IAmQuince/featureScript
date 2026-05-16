# Geometry Specification

## Coordinate convention

The Python preview uses a 2D coordinate system with the recovered symmetry axis at:

```text
y = 0
```

Default x locations:

```text
feed line   x = 0
dump line   x = FeedDump_Offset
target line x = FeedDump_Offset + Tributary_Offset
```

The Onshape FeatureScript uses the same local sketch convention after creating a sketch on the selected planar face.

## Recovered circle count rules

Let:

```text
N = Channel_Num_Snakes
```

Then:

```text
feed circles:   N - 1
dump circles:   N
snake circles:  N + 1
ladder circles: N
```

The central target-line station count is:

```text
2 * N + 1
```

Even central station indices become snake circles. Odd central station indices become ladder circles. This produces a real middle snake circle on the y=0 symmetry line.

## Recovered vertical spans

Feed and dump source circles use the manifold span:

```text
Manifold_Length
```

The central snake/ladder target line uses the recovered v1 expression:

```text
Manifold_Length + 2 * Manifold_Reduction - 2 * Ladder_Width
```

## Source positions

Feed source circles are placed at interior manifold stations:

```text
y_feed[i] = Manifold_Length / 2 - Manifold_Length * (i + 1) / N
```

Dump source circles are placed at half-step stations:

```text
y_dump[i] = Manifold_Length / 2 - (Manifold_Length / (2 * N) + Manifold_Length * i / N)
```

The first and last feed circles may be shifted left by one feed radius; this is retained as `top_bottom_feed_left_shift`.

## Default pairing mode

The default package mode is:

```text
y_aligned_physical
```

It pairs:

```text
feed[i] -> snake[i + 1]
dump[i] -> ladder[i]
```

This mode preserves the middle symmetry and best matches the physical/photo-like reference row.

The alternative Python-only mode is:

```text
recovered_docx_v1
```

It preserves the literal old written note:

```text
feed -> ladder
dump -> snake
```

That mode is kept for traceability; it is not the default portfolio view.

## Tributary boundary construction

Each tributary branch is a pair of cubic Bezier curves:

```text
top boundary
bottom boundary
```

The branch also has a diagnostic centerline for preview and metrics.

Each top/bottom boundary is built from a source-side channel-envelope point to a target-side channel-envelope point:

```text
source upper envelope -> target upper envelope
source lower envelope -> target lower envelope
```

The d_M1/d_M2 control construction is rectangular:

```text
P0 = source boundary point
P1 = P0 shifted horizontally toward target by d_M1
P2 = P3 shifted horizontally back toward source by d_M2
P3 = target boundary point
```

Earlier perpendicular-offset logic is retained only as a diagnostic comparison helper because it was part of the development history but did not match the recovered v1 diagram as well.

## CFD-screening geometry

The Python metrics module samples the generated branches and computes:

- centerline length
- top/bottom boundary length
- boundary width statistics
- planform area proxy
- hydraulic diameter from user-supplied channel depth
- wetted perimeter
- wetted surface area proxy
- relative resistance proxy
- curvature proxy
- branch spacing proxy
- mirror symmetry error about y=0

These metrics are useful for selecting a candidate layout before CAD regeneration and meshing; they are not a CFD solution.
