I want to merge as much as possible from main onto this branch, recognsing that this branch diverged a long time back in the history of main.

Goals are to: preserve the history from main, but prefer the refactoring done here.

Main has has a minor refactor, and in particular broke the original cfplot into several modules. I think we can bring the 
 - stipple.py
 - trajectory.py
 - line.py
 - vect.py 

code in carefully, recognising that they may refer to plotvars and utilities such as gclos which we have refactored.

Please investigate the feasibility but don't do anything until we have discussed.

---

Feasibility looks good for a staged merge, but not as a single direct “take everything” merge.

What I found:
1. Divergence is large: main is far ahead while this branch also has many unique commits (about 268 vs 47 from the merge base).
2. The four modules you called out exist on main (except vect.py, which appears to be vector.py on main), and are absent on this branch.
3. Main’s versions of those modules depend on modular internals such as parameters, graphic, and utils; this branch has equivalent responsibilities reorganized around state/runtime files.
4. This branch centralizes shared plotting state in state.py, with runtime orchestration in layout_runtime.py, map_runtime.py, and contour.py.
5. gclose entry points already exist here in layout_runtime.py and legacy compatibility still exists in cfplot.py.

Risk hotspots to expect:
1. API mismatch: main modules expect old modular imports and old plotvars ownership; this branch uses the refactored state/runtime model.
2. Duplicate control flow risk if trajectory/line/vector logic is brought in without routing through current runtime/state paths.
3. Semantic conflicts will be higher than textual conflicts, even if git reports few raw conflict markers.

Recommended merge strategy to preserve main history while preferring this refactor:
1. Merge main into a dedicated integration branch from refactor26, but do not resolve by taking old structure wholesale.
2. Keep this branch’s state/runtime architecture as the source of truth.
3. Replay the four target modules from main one by one, adapting imports and state access to current abstractions.
4. For each module: port, run focused tests/examples, then proceed to the next.
5. Keep a thin compatibility layer in cfplot.py during transition to reduce breakage.

No code changes were made.

If you want, next I can prepare a concrete per-module integration checklist (expected import rewrites, likely function shims, and test targets) before we touch the branch.
