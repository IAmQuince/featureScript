# FeatureScript Entry Point

The portfolio-facing Onshape code is:

```text
feature_scripts/tributary_generator.fs
```

Open that file first when reviewing the CAD automation work.

It defines the Onshape feature display name **Tributary Generator** and exports the FeatureScript symbol `tributaryGenerator`.

Historical project names such as `myTributary_Smooth` and `myTributary_CircleLine_STABLE` are documented for traceability, but the old draft files are intentionally not included because this package is meant to be a clean GitHub/portfolio baseline.

The Python preview generator that mirrors the same geometry is here:

```text
src/tributary_geometry/layout.py
```
