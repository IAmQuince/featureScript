# Technical Debt Register

## TD-001: Onshape validation pending

The FeatureScript needs direct Onshape compile/regeneration validation.

## TD-002: GUI is useful but not CAD-grade

The Tkinter GUI provides live preview, docking positions, LFOs, exports, and scenario persistence. A future Qt version could provide drag-and-drop docking, more advanced plotting, richer styling, and model/view separation.

## TD-003: Parameter-space mapper is metric-only

The current mapper exports bounded CSV metrics. It does not optimize, rank designs, or produce thumbnails for every point.

## TD-004: FeatureScript/Python parity needs formal snapshots

The Python engine and FeatureScript should eventually be tied together with documented parity cases: input variables, expected counts, expected source/target pairs, and visual screenshots from Onshape.

## TD-005: LFO animation is exploratory

The LFO system is useful for visually probing geometry sensitivity, but it is not currently connected to a formal design-study database.
