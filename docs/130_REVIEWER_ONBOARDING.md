# Reviewer Onboarding

## What to do first

Run:

```bat
launch_tributary_generator.bat
```

The GUI gives the fastest understanding of the project. The central canvas shows the tributary geometry; the side panel exposes parameters, LFO animation, parameter-space mapping, exports, and logs.

## What to read after launching

1. `PORTFOLIO_REVIEW_GUIDE.md`
2. `src/tributary_geometry/layout.py`
3. `src/tributary_geometry/gui_app.py`
4. `feature_scripts/tributary_generator.fs`
5. `docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md`

## What this package demonstrates

- Parametric CAD thinking.
- Python-side geometry modeling.
- CAD automation through FeatureScript.
- GUI-based geometry exploration.
- Honest diagnostic packaging.
- GitHub-ready cleanup and documentation discipline.

## What not to assume

Do not assume the FeatureScript has already compiled inside Onshape. It is a reconstructed clean candidate and must still be validated directly in the Onshape environment.
