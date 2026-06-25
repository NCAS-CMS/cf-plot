# Staged Merge Playbook: main -> refactor26

This playbook is a command-level draft for merging as much as possible from `main` while preferring the refactor architecture on `refactor26`.

The intent is to:
- preserve ancestry/history from `main`
- keep the `refactor26` state/runtime architecture as the source of truth
- integrate selected modules from `main` in controlled stages

No command below is executed by default. Work through sections one-by-one.

## 0) Pre-flight and safety checkpoints

Run from repo root.

```bash
git status --short -b
```

If not clean, either commit or stash first.

Create explicit safety refs:

```bash
git checkout refactor26
git pull --ff-only

# Safety tag on current refactor tip
git tag -a safety/refactor26-pre-main-merge-$(date +%Y%m%d-%H%M) -m "Safety tag before staged main merge"

# Optional backup branch
git branch backup/refactor26-pre-main-merge
```

## 1) Create dedicated integration branch

This keeps `refactor26` clean while integrating.

```bash
git checkout -b integration/main-into-refactor26
```

## 2) Bring in main history (single merge commit)

Start a non-committing merge so conflicts can be resolved deliberately.

```bash
git fetch origin
git merge --no-commit --no-ff main
```

### Conflict resolution policy

Use these rules consistently:
- default conflict preference: keep refactor architecture
- accept `main` where change is orthogonal and low-risk
- never re-introduce old structure if equivalent refactor code already exists

Useful helpers:

```bash
# List unresolved files
git diff --name-only --diff-filter=U

# Inspect each conflict
git checkout --ours <path>   # keep integration branch version (refactor26 side)
git checkout --theirs <path> # take main version
git add <path>
```

When all conflicts are resolved:

```bash
git commit -m "merge: main into integration branch (prefer refactor26 architecture)"
```

## 3) Immediate post-merge sanity pass

```bash
git status --short -b
pytest -q tests/unit
```

If tests fail broadly, stop and create a fix commit before module stages.

Suggested commit message:

```text
fix: restore baseline after main merge
```

## 4) Stage plan for target modules

Main appears to use `vector.py` (not `vect.py`).

Stages:
1. `stipple`
2. `trajectory`
3. `line`
4. `vector`

For each stage, do the same workflow below.

---

## 5) Per-module workflow template

Use `<module>` as one of: `stipple`, `trajectory`, `line`, `vector`.

### A) Inspect source on main and current branch

```bash
git show main:cfplot/<module>.py | sed -n '1,220p'
rg -n "<module>|plotvars|gclose|gopen|gpos|state|utility" cfplot
```

### B) Port with adaptation, not blind copy

Guidance:
- translate imports from old module layout to refactor layout
- route global state reads/writes through `cfplot/state.py` (`plotvars`)
- route graphics lifecycle calls through refactor runtime entrypoints
- avoid duplicating logic that already exists in runtime modules

### C) Validate stage

```bash
pytest -q tests/unit
pytest -q tests/integration
```

If image regression workflow is available locally, run focused checks for module behavior.

### D) Commit stage

```bash
git add -A
git commit -m "merge-stage: integrate <module> from main into refactor runtime"
```

### E) Stage exit criteria

- module imports cleanly
- no broad regressions in unit/integration tests
- no duplicate competing implementation paths introduced

---

## 6) Suggested conflict defaults by area

These are starting defaults, not strict rules:

- Keep refactor side by default:
  - `cfplot/state.py`
  - `cfplot/layout_runtime.py`
  - `cfplot/map_runtime.py`
  - `cfplot/rotated_runtime.py`
  - `cfplot/utility.py` (unless cherry-picked utility fixes are clearly better)

- Evaluate carefully / case-by-case:
  - `cfplot/cfplot.py` (compatibility surface, likely heavy conflict zone)
  - `cfplot/contour.py` (high behavior impact)

- Bring from main with adaptation:
  - `cfplot/stipple.py`
  - `cfplot/trajectory.py`
  - `cfplot/line.py`
  - `cfplot/vector.py`

## 7) Optional: isolate each module on micro-branches

If you want very fine rollback points:

```bash
git checkout integration/main-into-refactor26
git checkout -b integration/stage-stipple
# integrate stipple, commit
git checkout integration/main-into-refactor26
git merge --no-ff integration/stage-stipple
```

Repeat for each module.

## 8) Final hardening before merging back

```bash
pytest -q
```

If you have example/image reference checks, run full suite here.

Then compare against `refactor26`:

```bash
git log --oneline --decorate --graph refactor26..integration/main-into-refactor26
git diff --stat refactor26...integration/main-into-refactor26
```

If satisfied:

```bash
git checkout refactor26
git merge --ff-only integration/main-into-refactor26
```

If fast-forward is not possible and you want to preserve branch topology:

```bash
git checkout refactor26
git merge --no-ff integration/main-into-refactor26
```

## 9) Rollback recipes

Abort in-progress merge:

```bash
git merge --abort
```

Reset integration branch to pre-merge safety ref:

```bash
git reset --hard safety/refactor26-pre-main-merge-<timestamp>
```

Restore refactor baseline quickly:

```bash
git checkout refactor26
git reset --hard backup/refactor26-pre-main-merge
```

Only use hard reset when you intentionally want to discard uncommitted work.

## 10) Suggested commit message scheme

- `merge: main into integration branch (prefer refactor26 architecture)`
- `fix: restore baseline after main merge`
- `merge-stage: integrate stipple from main into refactor runtime`
- `merge-stage: integrate trajectory from main into refactor runtime`
- `merge-stage: integrate line from main into refactor runtime`
- `merge-stage: integrate vector from main into refactor runtime`
- `test: update expectations for merged behavior`
