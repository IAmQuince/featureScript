# Syntax and Debugging History

This document is intentionally candid. FeatureScript syntax and type behavior were a constant source of development friction in this project. The package does not try to hide that history because it is part of the engineering record and explains why the Python preview generator exists.

## Why syntax issues mattered

The desired geometry was conceptually straightforward: build circle rows, pair boundary points, and connect them with Bezier curves. The difficult part was repeatedly translating that intent into valid FeatureScript syntax and unit-safe operations.

## Recurring FeatureScript issues encountered

- **FeatureScript version/import syntax**: different drafts had problems around the exact `FeatureScript ####;` and `import(...)` syntax.
- **Id versus string handling**: Onshape expects `Id` values in some API calls, while sketch entities use string-like identifiers. Passing a plain concatenated string where an `Id` was expected caused failures.
- **Sketch plane creation**: the safer recovered pattern is to evaluate the selected face plane, explicitly construct a plane from origin and normal, and pass the feature `id` into `newSketchOnPlane`.
- **Unitful comparisons**: comparing a `ValueWithUnits` to a bare scalar caused errors; dimensioned tolerances such as `1e-12 * meter` are safer.
- **Vector magnitude mistakes**: early drafts confused string/list length behavior with vector magnitude and had to use explicit Euclidean norm calculations.
- **Undefined or renamed helper functions**: helpers such as point/vector constructors and Bezier evaluation functions changed across drafts.
- **Geometry versus syntax debugging**: a visible failure in Onshape could come from syntax, missing entities, invalid sketch geometry, or unit typing, so small isolated tests were needed.

## How this package responds

- The main FeatureScript is now named and documented as `feature_scripts/tributary_generator.fs`.
- The fragile areas are commented directly in the code.
- The Python package mirrors the geometry so a reviewer can inspect the intended tributaries before Onshape compilation.
- Tests, a smoke test, and a diagnostic harness validate the Python side.
- The FeatureScript status is stated plainly: it still requires Onshape-side validation.

## What this demonstrates

The project demonstrates not only CAD automation, but also an engineering workflow for an environment where the target language is hard to test locally:

1. recover and formalize the geometry rules;
2. create a local Python reference generator;
3. export inspectable artifacts;
4. keep FeatureScript small and annotated;
5. record known syntax hazards instead of burying them.

## Launcher/import issue added during GUI packaging

A normal Python package module such as `src/tributary_geometry/layout.py` is not meant to be launched by full file path. Running it that way can produce:

```text
ImportError: attempted relative import with no known parent package
```

That is not a geometry failure; it is a package import-context failure. This package now addresses that in two ways:

1. `launch_tributary_generator.bat` is the single reviewer-facing launch path.
2. `layout.py` includes a small direct-run fallback for exploratory use.

The preferred pattern remains launching modules from the repository root with `python -m ...` or using the BAT launcher.

## Recovered v1 syntax note

The old `Tributaryv1.docx` file was useful precisely because it showed both the intended FeatureScript structure and the point where implementation broke down: the tributary-building section was still a TODO. That old file also showed several syntax choices that needed to be handled carefully in the cleaned version, including `skBezier` point-key usage, sketch-plane creation, and construction geometry calls.

The current package does not claim that the first drafts were clean. The portfolio story is that the geometry was recovered, made testable in Python, instrumented with diagnostics/metrics, and then translated back into a cleaner FeatureScript candidate.
