# Known Limitations

- FeatureScript cannot be compiled in this local package; Onshape validation is required.
- The original historical FeatureScript source file was not available in the accessible file set, so `feature_scripts/tributary_generator.fs` is a reconstructed clean baseline.
- The auxiliary Python package is a repaired/rebuilt mirror of the recovered geometry rules, not a recovered original file.
- FeatureScript syntax issues were a recurring project problem and are documented openly in `docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md`.
- The Python package does not call the Onshape API.
- The SVG exporter is diagnostic and portfolio/review oriented; it is not a manufacturing drawing.
- Default dimensions are visualization defaults, not final electrolyzer hardware dimensions.
- The current FeatureScript focuses on sketch-generation geometry and intentionally omits downstream extrusion/removal operations.
