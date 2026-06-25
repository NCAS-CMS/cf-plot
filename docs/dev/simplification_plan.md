# cf-plot Maintainability Simplification Plan (No Public API Change)

*Created 2026-05-23. Companion to architecture.md. This file tracks post-merge
simplifications that reduce duplication and improve readability while preserving
all public API behaviour.*

---

## 1. Scope And Constraints

### In scope
- Internal refactoring and deduplication in runtime and plotting modules.
- Bug fixes that restore expected behaviour without changing public signatures.
- Test additions/updates needed to lock in current API behaviour.

### Out of scope
- Renaming/removing public symbols from `cfplot.__init__`.
- Changing function call signatures users rely on.
- Visual style or plotting-output changes unless fixing a clear bug.

### Hard constraint
- Keep public API stable.

---

## 2. Issue Register

Legend:
- Priority: P0 (critical), P1 (high), P2 (medium), P3 (low)
- Effort: S (small), M (medium), L (large)
- Status: Not Started, In Progress, Done, Deferred

| ID | Priority | Effort | Status | Issue | Why it matters | Candidate files |
|----|----------|--------|--------|-------|----------------|-----------------|
| S1 | P0 | S | Done | Trajectory label regression (`user_xlabel`/`user_ylabel` overwritten) | User input can be ignored; blocks confidence in subsequent refactors | `cfplot/trajectory.py` |
| S2 | P1 | M | Done | Duplicate map helper trio (`_set_map`, `_plot_map_axes`, `_map_title`) across modules | Same logic in three places increases drift risk | `cfplot/stream.py`, `cfplot/trajectory.py`, `cfplot/vector.py`, `cfplot/map_runtime.py` |
| S3 | P1 | M | Done | Coastline/feature rendering duplicated despite shared helper | Styling and behaviour can diverge by plot type | `cfplot/map_runtime.py`, `cfplot/stream.py`, `cfplot/trajectory.py`, `cfplot/vector.py` |
| S4 | P1 | M | Done | Repeated graphics session lifecycle open/gpos/close patterns | Boilerplate hides intent and makes fixes repetitive | `cfplot/layout_runtime.py`, `cfplot/line.py`, `cfplot/stream.py`, `cfplot/trajectory.py`, `cfplot/vector.py`, `cfplot/rotated_runtime.py` |
| S5 | P2 | M | Done | Axis hiding uses sentinel numeric ticks (`100000000`) | Non-obvious and brittle behaviour | `cfplot/line.py`, `cfplot/vector.py` |
| S6 | P2 | M | Done | Shared-state reset logic duplicated | High chance of reset drift and latent state bugs | `cfplot/__init__.py`, `cfplot/layout_runtime.py`, `cfplot/state.py` |
| S7 | P3 | S | Done | Executable lookup duplicated (`_which` and `shutil.which`) | Minor maintenance overhead and inconsistency | `cfplot/__init__.py`, `cfplot/layout_runtime.py` |
| S8 | P3 | S | Done | `pvars.__str__` implementation is non-informative | Debugging shared state is harder than necessary | `cfplot/state.py` |

---

## 3. Phased Implementation Plan

### Phase 1 - Correctness Baseline (S1)
Goal: Fix known regression before broader refactors.

Steps:
- [x] Fix label clobbering in `traj()` so user-provided labels are preserved.
- [x] Add/adjust focused tests for trajectory label overrides.
- [x] Run trajectory-related tests.

Exit criteria:
- User labels are respected when supplied.
- No public API or signature change.

---

### Phase 2 - Map Helper Consolidation (S2, S3)
Goal: Remove repeated map orchestration logic.

Steps:
- [x] Introduce/expand shared private helpers in `map_runtime.py` for map setup, axes application, and title application.
- [x] Replace duplicated helper definitions in `stream.py`, `trajectory.py`, and `vector.py` with imports from `map_runtime.py`.
- [x] Route map feature/coastline code paths through `_apply_map_features` where applicable.
- [x] Validate map plot types (cylindrical, polar stereographic, lcc where relevant).

Exit criteria:
- No duplicated helper trio remains in stream/trajectory/vector.
- Map feature behaviour remains equivalent for existing tests/examples.

---

### Phase 3 - Session Lifecycle Consolidation (S4)
Goal: Centralize figure/session management boilerplate.

Steps:
- [x] Add internal helper(s) for common open/gpos/close flow in `layout_runtime.py`.
- [x] Migrate line/stream/trajectory/vector/rotated paths incrementally.
- [x] Keep module-level public functions unchanged.
- [x] Run regression tests for each migrated module.

Exit criteria:
- Repeated lifecycle pattern replaced by shared internal helper(s).
- Behaviour remains stable under multi-panel and user-managed sessions.

---

### Phase 4 - Axis And State Hygiene (S5, S6)
Goal: Improve clarity and reduce state drift risk.

Steps:
- [x] Replace sentinel tick suppression with explicit axis-hiding helper logic.
- [x] Introduce a single internal state-reset helper in `state.py` (or equivalent central location).
- [x] Make `cfplot.reset()` and runtime close/reset paths delegate to shared reset logic.

Exit criteria:
- No sentinel tick hacks in active code paths.
- Reset behaviour remains equivalent but centralized.

---

### Phase 5 - Low-Risk Cleanup (S7, S8)
Goal: Finish small consistency improvements.

Steps:
- [x] Unify executable lookup usage while preserving exported compatibility wrappers.
- [x] Fix `pvars.__str__` to return meaningful state output for debugging.

Exit criteria:
- Utility duplication removed or delegated.
- Shared state object is easier to inspect.

---

## 4. Execution Checklist

Use this as the day-to-day tracker.

- [ ] Phase 1 complete (S1)
- [x] Phase 1 complete (S1)
- [x] Phase 2 complete (S2, S3)
- [x] Phase 3 complete (S4)
- [x] Phase 4 complete (S5, S6)
- [x] Phase 5 complete (S7, S8)
- [ ] Full regression pass complete
- [ ] Plan reviewed and archived

---

## 5. Validation Strategy Per Phase

- Prefer targeted tests first, then broader integration tests.
- Keep at least one representative run for each major plotting path:
  - line
  - contour
  - vector
  - stream
  - trajectory
  - rotated-pole path
- Compare generated images only where behavioural parity is uncertain.
- Record any intentional behaviour adjustments explicitly in this file.

---

## 6. Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-05-23 | Copilot | Initial issue register and phased implementation plan created |
| 2026-05-23 | Copilot | Completed S1: fixed trajectory label clobbering and added focused unit coverage |
| 2026-05-23 | Copilot | Phase 2 partial: consolidated stream/vector/trajectory map helpers to map_runtime and routed shared map features; targeted vector/stream/trajectory tests passed |
| 2026-05-23 | Copilot | Completed Phase 2 validation: targeted projection tests (including LCC-related path) passed; no image-diff failures in executed set |
| 2026-05-23 | Copilot | Phase 3 in progress: introduced shared runtime session helpers and migrated line/stream/trajectory/vector; targeted runs show image-comparison differences in selected advanced examples pending user decision |
| 2026-05-23 | Copilot | Completed Phase 3: shared runtime session helpers validated with targeted regression tests across line, vector, stream, trajectory, and rotated paths |
| 2026-05-23 | Copilot | Completed Phase 4: replaced sentinel axis hiding with explicit helper logic and centralized runtime reset behavior; targeted runtime and lineplot validation passed |
| 2026-05-23 | Copilot | Completed Phase 5: removed private _which helper from __init__.py and fixed state object string output; targeted unit validation passed |
