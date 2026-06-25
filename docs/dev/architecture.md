# cf-plot Contour Subsystem — Architecture & Refactoring Analysis

*Generated 2026-05-16. Covers the refactored contour path only (`contour.py` and its
direct dependencies). The legacy monolith `cfplot.py` is explicitly out of scope.*

---

## 1. Package Layout

```
cfplot/
├── __init__.py          # Public API surface
├── cfplot.py            # Legacy monolith (out of scope)
├── contour.py           # Refactored contour rendering
├── colorbar.py          # Colorbar rendering helper
├── blockfill.py         # Block-fill rendering helper
├── layout_runtime.py    # Figure/viewport lifecycle (no map knowledge)
├── map_runtime.py       # Map setup, axes, and graticule
├── state.py             # Global plotvars singleton + colour scale state
└── utility.py           # Pure stateless utilities
```

---

## 2. Module Responsibilities

### `state.py`
Owns the single shared `plotvars` instance and the two colour-scale operations
that mutate it (`apply_colour_scale`, `get_colour_scale_map`). Everything else that
reads or writes plotting state goes through this object.

**Imports:** `utility` (for `load_colour_scale_rgb`, `interpolate_colour_channels`).
This is the only outward dependency; `state` does not import any rendering module.

### `utility.py`
Pure functions with no global state. Acts as the maths and data-extraction layer:
`gvals`, `mapaxis`, `ndecs`, `calculate_levels`, `cf_data_assign`, `timeaxis`,
`find_z`, `load_colour_scale_rgb`, `interpolate_colour_channels`, etc.

**Imports:** nothing from the package.

### `layout_runtime.py`
Figure lifecycle and Cartesian viewport management. Contains:

| Symbol | Role |
|--------|------|
| `gopen` / `gclose` | Session open/close, figure save/show |
| `ensure_xy_viewport` | Lazy figure + subplot creation for Cartesian plots |
| `set_plot_limits` | Forward axis limits to the active `plotvars.plot` |
| `apply_axes` | Dispatcher: routes to `_apply_xy_axes` or (local import) `map_runtime._apply_map_axes` |
| `_open_figure` | Private: creates the Matplotlib figure, applies subplots_adjust |
| `_select_position` | Private: creates one subplot or user-positioned axes |
| `_apply_xy_axes` | Private: labels and ticks for Cartesian axes |

**Imports:** `matplotlib`, `state`. No Cartopy, no NumPy.

### `map_runtime.py`
Everything required to create and decorate a Cartopy map axes. Contains:

| Symbol | Role |
|--------|------|
| `MapSet` class | Stateful map configuration + axes creation |
| `MapSet.configure` | Write map extent/projection parameters into `plotvars` |
| `MapSet.ensure_map_axes` | Create the Cartopy `GeoAxes` subplot |
| `MapSet.draw_grid` | Draw a graticule on the active map |
| `MapSet.draw_polar_axes` | Graticule + longitude labels for polar stereographic |
| `_apply_map_title` | Places a title on map axes using Cartopy transforms |
| `_apply_dim_titles` | Places dimension-string annotation beside plot |
| `ensure_map_viewport` | Module-level: lazy figure creation before map axes |
| `_apply_map_axes` | Module-level: lon/lat ticks for cyl and lcc projections |

**Imports:** `cartopy.crs`, `numpy`, `utility`, `state`. Uses a *local* import of
`_open_figure`/`_select_position` from `layout_runtime` inside `ensure_map_viewport`
to avoid a circular module-level dependency.

### `colorbar.py`
Single public function `cbar()` that draws a `ColorbarBase` onto a newly-added axes
inset below or beside the active plot. Reads `plotvars` directly for defaults.

**Imports:** `matplotlib`, `numpy`, `state`.

### `blockfill.py`
Single public function `_bfill()` that fills contour bands with solid-coloured
rectangles or polygons. Handles both Cartesian and map (lon/lat) modes.

**Imports:** `cartopy.crs`, `cartopy.util`, `cf`, `matplotlib`, `numpy`, `state`.

### `contour.py`
The main rendering module. Provides `con()` as its sole public entry point.

**Key objects:**

| Object | Role |
|--------|------|
| `ContourData` | Frozen dataclass: extracted, validated field + coordinate arrays |
| `ContourLayout` | Allocates viewport and applies titles/labels |
| `ColourScale` | Fits a colormap to contour levels |
| `ContourRenderer` | Abstract base: `render_filled`, `render_lines`, `render_blockfill`, `render_colorbar` |
| `MapContourRenderer` | Concrete: Cartopy-aware contour drawing (ptype 1) |
| `XYContourRenderer` | Concrete: Cartesian contour drawing (ptypes 0, 2–5) |

**Key private functions:**

| Function | Role |
|----------|------|
| `con()` | Public entry point; guards unsupported cases, delegates to `_render_with_new_xy` |
| `_render_with_new_xy` | Orchestrates: data extraction → levels → colour → layout → render → colorbar → title |
| `_add_cyclic` | Adds a cyclic longitude column using `cartopy_util` |
| `_clear_animation_artists` | Removes artists from the previous animation frame |
| `_can_use_new_xy_path` | Guards entry to the new renderer path |

**Imports:** `cf`, `cartopy.crs`, `cartopy.feature`, `matplotlib`, `numpy`,
`utility`, `blockfill._bfill`, `colorbar.cbar`, `layout_runtime`, `map_runtime`,
`state`.

---

## 3. Dependency Diagram

```plantuml
@startuml cf-plot-contour-dependencies
skinparam packageStyle rectangle
skinparam ArrowColor #444444
skinparam componentStyle uml2

package "External" {
  [cf]
  [cartopy]
  [matplotlib]
  [numpy]
}

package "cfplot" {
  [utility]
  [state]
  [layout_runtime]
  [map_runtime]
  [colorbar]
  [blockfill]
  [contour]
}

' Pure utilities layer
[state]         --> [utility]

' Layout layer (no Cartopy)
[layout_runtime] --> [state]
[layout_runtime] ..> [map_runtime] : local import\n(apply_axes branch)

' Map layer
[map_runtime]   --> [state]
[map_runtime]   --> [utility]
[map_runtime]   ..> [layout_runtime] : local import\n(ensure_map_viewport)
[map_runtime]   --> [cartopy]
[map_runtime]   --> [numpy]

' Rendering helpers
[colorbar]      --> [state]
[colorbar]      --> [matplotlib]
[colorbar]      --> [numpy]

[blockfill]     --> [state]
[blockfill]     --> [cartopy]
[blockfill]     --> [numpy]
[blockfill]     --> [cf]

' Main module
[contour]       --> [state]
[contour]       --> [utility]
[contour]       --> [layout_runtime]
[contour]       --> [map_runtime]
[contour]       --> [colorbar]
[contour]       --> [blockfill]
[contour]       --> [cartopy]
[contour]       --> [matplotlib]
[contour]       --> [numpy]
[contour]       --> [cf]
@enduml
```

---

## 4. Call Flow: a typical `con(f)` invocation

```plantuml
@startuml cf-plot-con-callflow
skinparam sequenceArrowThickness 1.2
skinparam actorBackgroundColor #eee

actor Caller

Caller        -> contour : con(f, **kwargs)
contour       -> contour : _can_use_new_xy_path()
contour       -> contour : _render_with_new_xy()

group Data extraction
  contour     -> utility : cf_data_assign(f)
  utility    --> contour : field, x, y, ptype, labels
  contour     -> contour : ContourData.from_cf_field()
end

group Levels & colour scale
  contour     -> utility : calculate_levels(field)
  utility    --> contour : clevs, mult, fmult
  contour     -> state   : ColourScale.fit_to_levels()
  state       -> utility : apply_colour_scale → load_colour_scale_rgb
end

group Viewport allocation  (ptype == 1 shown)
  contour     -> map_runtime : MapSet.configure()
  map_runtime -> state       : write lonmin/lonmax/proj/…
  contour     -> map_runtime : MapSet.ensure_map_axes()
  map_runtime -> layout_runtime : ensure_map_viewport() [local import]
  layout_runtime -> state    : _open_figure / _select_position
  map_runtime -> state       : write plotvars.mymap
  contour     -> contour     : ContourLayout.allocate_map_viewport()
end

group Rendering
  contour     -> contour : MapContourRenderer.render_filled()
  note right: reads plotvars.mymap, plotvars.norm
  contour     -> contour : MapContourRenderer.render_lines()
  contour     -> map_runtime : apply_axes (via layout_runtime dispatcher)
  map_runtime -> utility : mapaxis()
  contour     -> map_runtime : MapSet.draw_grid() / draw_polar_axes()
  contour     -> cartopy  : add_feature (coastlines etc.)
end

group Colorbar + title
  contour     -> colorbar : cbar(labels, levs, …)
  colorbar    -> state    : get_colour_scale_map()
  contour     -> map_runtime : _apply_map_title()
end

group Optional file save
  contour     -> matplotlib : figure.savefig()
end

contour      --> Caller : None (success)
@enduml
```

---

## 5. Semantic Leakage Analysis

The following issues are places where a module does work that belongs to a
different layer of the architecture. They are ordered roughly by severity and
ease of fixing.

---

### L1 — `_apply_map_title` and `_apply_dim_titles` moved to `map_runtime.py` (completed)

**Status (2026-05-16):** Completed. Both helpers now live in `map_runtime.py` and
`contour.py` calls them from there.

**What:** Two functions that place annotated text on map axes using Cartopy
coordinate transforms (`ccrs.PlateCarree`, `ccrs.Robinson`, etc.) are defined
as module-level privates in `contour.py`.

**Why it matters:** These are map annotation concerns. They have nothing to do
with the contour rendering strategy (levels, colourmaps, fill/lines). Their
natural home is `map_runtime.py`, alongside `draw_grid` and `draw_polar_axes`.

**Symptom in `ContourLayout`:** `ContourLayout.apply_title` branches on
`plot_type == 1` and calls `_apply_map_title`. This forces the *layout* class
to have knowledge of map projections — exactly the concern `map_runtime` is
supposed to own.

**Result:** Done. Ownership is now aligned: map annotations are in `map_runtime.py`.

---

### `rotated_runtime.py`
Rotated-pole (ptype 6) rendering and grid axes helpers. Encapsulates rotated-latitude-longitude
coordinate system rendering, including continent drawing via shapefile, rotated transforms,
and index-space grid lines/axis labels.

**Key functions:**

| Function | Role |
|----------|------|
| `_rotated_vloc` | Maps geographic lon/lat points into rotated-grid index space |
| `_render_rotated_grid_axes` | Draws rotated-pole graticule + continent lines in index space |
| `_render_ptype6_rotated_pole` | Handles rotated-pole plots (ptype 6) orchestration |

**Imports:** `cartopy.crs`, `cartopy.feature`, `numpy`, `utility`, `blockfill._bfill`,
`colorbar.cbar`, `layout_runtime`, `map_runtime`, `state`.

---

### L2 — `_render_rotated_grid_axes` and `_render_ptype6_rotated_pole` moved to `rotated_runtime.py` (completed)

**Status (2026-05-17):** Extraction complete. Both functions moved to `rotated_runtime.py`.
Post-move simplification:  extracted duplicated map feature decoration code into a
centralized `_apply_map_features()` helper in `map_runtime.py`, eliminating ~35 lines
of duplicate code in both `contour.py` and `rotated_runtime.py`.

**Result:** Done. Ptype-6 rendering has its own module with reduced duplication. Map
decoration logic is now centralized.

---

### L3 — `ColourScale.colourbar_labels` now the single source of truth (completed)

**Status (completed):** The ~50-line inline colourbar label logic in
`_render_with_new_xy` has been removed and replaced with a call to
`cs.colourbar_labels()`. The method itself was fixed: the dead-code second
`if label_skip is None:` guard was removed so the horizontal skip heuristic
now runs correctly.

**What was done:**
- Renamed `colorbar_labels()` to `colourbar_labels()` on `ColourScale`
- Fixed dead-code bug in method: removed early `label_skip = 1` that
  prevented the horizontal skip heuristic from ever executing
- Replaced ~50 lines of inline label-skip/level-selection logic in
  `_render_with_new_xy` with a single call to `cs.colourbar_labels()`
- All 112 tests passing

**Result:** ~50 lines of duplicate logic removed. `ColourScale.colourbar_labels`
is now the canonical implementation.

---

### L4 — `_add_cyclic` consolidated into `utility.py`

**Status (completed):** Duplicate implementations from `contour.py` and `blockfill.py`
merged into single canonical function `utility.add_cyclic()` with unified error
handling for cyclic longitude grids. Both modules now import and call `utility.add_cyclic()`.

**What was done:** 
- Added `cartopy.util as cartopy_util` import to `utility.py`
- Created canonical `add_cyclic()` function combining error handling from both sources
- Updated `contour.py` line 1164: changed from local `_add_cyclic()` to `utility.add_cyclic()`
- Updated `blockfill.py` line 202: changed from local `_add_cyclic()` to `utility.add_cyclic()`
- Removed duplicate `_add_cyclic()` and `_max_ndecs_data()` definitions
- Removed now-unused `cartopy.util` imports from both modules
- All 112 tests passing

**Result:** ~25 lines of duplicate code removed. Cyclic longitude handling centralized in utility layer.

---

### L5 — Renderer classes (`MapContourRenderer`, `XYContourRenderer`) bypass their injected dependencies and read `plotvars` directly

**What:** Both subclasses receive `layout`, `data`, and `colour_scale` in their
constructor, yet render methods reach back to `plotvars.mymap`, `plotvars.image`,
`plotvars.norm`, `plotvars.levels_extend`, etc.

**Why it matters:** The object design suggests the renderers are self-contained, but
at runtime they depend on global state being in the right shape. This makes testing
them in isolation hard and means the class boundaries are more cosmetic than real.

**Note:** This is a known cost of incremental refactoring. Fully fixing it requires
threading `mymap`, `norm`, etc. through the renderer interface, which is a larger
change. It should be tracked as a future goal rather than fixed immediately.

---

### L6 — Tick generation for ptypes 2–5 extracted from `_render_with_new_xy` (completed)

**Status (completed):** The inline ptype tick-generation block was moved out of
`contour._render_with_new_xy` and consolidated in `utility.compute_xy_ticks()`.

**What was done:**
- Added `utility.compute_xy_ticks()` as the canonical non-map tick/label helper
  for ptypes 2-5, including default axis-label resolution.
- Added `utility._pressure_axis_ticks()` to keep pressure/log-pressure Y tick
  logic shared and centralized.
- Replaced the inline ptype-dispatch tick block in
  `contour._render_with_new_xy` with one call to `utility.compute_xy_ticks()`.
- Kept behaviour parity for Hovmuller time-axis handling by passing precomputed
  `time_ticks`, `time_labels`, and `time_label` through the new helper.
- Verified with focused unit and integration tests.

**Result:** Tick-generation concerns are now owned by the utility layer,
reducing orchestration complexity in `contour.py` and making axis logic easier
to reuse and test.

---

### L7 — `maybe_autosave` extracted to `layout_runtime` (completed)

**Status (completed):** `_finalize_non_session_plot()` (previously a private
function in `contour.py`) has been moved to `layout_runtime` as the public
`maybe_autosave()` function. Both `_render_with_new_xy` (direct call) and
`_render_ptype6_rotated_pole` (via `finalize_callback` argument) now use it.

**What was done:**
- Added `maybe_autosave()` to `layout_runtime.py`
- Removed `_finalize_non_session_plot()` from `contour.py`
- Updated `contour.py` import to include `maybe_autosave`
- Updated direct call site in `_render_with_new_xy`
- Updated `finalize_callback=maybe_autosave` passed to `_render_ptype6_rotated_pole`
- All 112 tests passing

**Result:** File-save/close responsibility correctly owned by `layout_runtime`.

---

### L8 — `colorbar.py` reads `plotvars` extensively for defaults

**What:** `cbar()` currently reads at least fifteen `plotvars` attributes to fill in
unset parameters (`rows`, `plot_type`, `proj`, `levels_extend`, `cs`, `norm`,
`image`, `master_plot`, etc.).

**Why it matters:** This makes `colorbar.py` tightly coupled to the state object
and hard to unit-test. It is the deepest legacy coupling left in the refactored
modules.

**Note:** Fixing this requires threading all the required values as explicit
arguments. It is the right long-term direction but is a substantial interface
change. For now the coupling is contained within `colorbar.py` and nowhere
else imports `colorbar` except through `contour.py`.

---

### L9 — `lonlat` removed from the refactored `blockfill._bfill` API (completed)

**Status (completed):** The refactored `_bfill` implementation no longer accepts
the misleading `lonlat` keyword. Runtime behaviour is unchanged: `_bfill` still
derives lon/lat handling from `plotvars.plot_type == 1`, but the fake override
hook is no longer exposed in the function signature.

**What was done:**
- Removed `lonlat` from the refactored `blockfill._bfill` signature
- Updated refactored call sites in `contour.py` and `rotated_runtime.py`
- Kept existing behaviour by computing `lonlat` internally from `plotvars.plot_type`
- Added a unit test to prevent `lonlat` from reappearing in the refactored API

**Result:** The refactored internal API is now honest about what it controls,
without changing rendering behaviour.

---

## 6. Suggested Refactoring Order

| Priority | Item | Module(s) affected |
|----------|------|--------------------|
| 1 (done) | Fix L4: merge `_add_cyclic` into `utility` | `contour`, `blockfill`, `utility` |
| 2 (done) | Fix L7: extract `maybe_autosave` to `layout_runtime` | `layout_runtime`, `contour` |
| 3 (done) | Fix L3: replace inline label logic with `colourbar_labels()` | `contour` |
| 4 (done) | Fix L1: move `_apply_map_title` / `_apply_dim_titles` to `map_runtime` | `contour`, `map_runtime` |
| 5 (done) | Fix L2: extract rotated-pole path to `rotated_runtime` | `contour`, `rotated_runtime` |
| 6 (done) | Fix L6: extract tick logic to utility helper(s) | `contour`, `utility` |
| 7 (done) | Fix L9: remove misleading `lonlat` parameter from `_bfill` | `blockfill` |
| 8 (future) | Fix L8: thread colorbar params explicitly | `colorbar`, `contour` |
| 9 (future) | Fix L5: decouple renderers from global `plotvars` | `contour` |
