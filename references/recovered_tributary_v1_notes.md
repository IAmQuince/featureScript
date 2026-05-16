# Recovered Tributary v1 Notes

## What was recovered

The old design document established the core construction:

- `FeatureScript 2559`
- feature name history: `myTributary_Smooth`
- three vertical construction/circle lines:
  - feed circles
  - dump circles
  - central alternating snake/ladder circles
- source variables:
  - `Channel_Num_Snakes`
  - `Manifold_Length`
  - `Manifold_Reduction`
  - `Ladder_Width`
  - `FeedDump_Offset`
  - `Tributary_Offset`
  - `Feed_Diameter`
  - `Dump_Diameter`
  - `Snake_Width`
  - `d_snake_M1`, `d_snake_M2`
  - `d_ladder_M1`, `d_ladder_M2`
- central target-line count rule:
  - `2 * Channel_Num_Snakes + 1`
- source circle count rules:
  - feed circles: `Channel_Num_Snakes - 1`
  - dump circles: `Channel_Num_Snakes`
- central target circle rules:
  - even central indices become snake circles
  - odd central indices become ladder circles
- a middle symmetry axis is implied by the central target line being centered about the sketch midpoint.

## What was missing in the old document

The old document stopped at the section where tributaries needed to be generated. It explicitly called out that the correct logic still needed to be added.

The important recovered instruction was:

1. pair the feed/dump circles to the snake/ladder circle row;
2. create construction rectangles between the relevant upper and lower boundary points;
3. create top and bottom cubic Bezier boundaries;
4. use separate `d_M1` and `d_M2` control distances for snake and ladder tributaries.

## What this package changed

The repaired package implements the missing logic in both places:

- Python preview engine: `src/tributary_geometry/layout.py`
- Onshape candidate FeatureScript: `feature_scripts/tributary_generator.fs`

The default Python/FeatureScript interpretation is `y_aligned_physical`:

- feed circles connect to interior snake circles;
- dump circles connect to ladder circles;
- the layout remains symmetric about the middle y-axis;
- the preview better resembles the physical tributary row than the earlier generic reconstruction.

The literal old-note interpretation is also retained in the Python GUI as `recovered_docx_v1`, because the development history should be visible rather than hidden.
