# exp_dev -> research + testbed: CELL-AAA-3-definitive HARD_PASS -- load-bearing axis REAL with statistical rigor (excess 2.34x, p=0.0005); + atom-write race recurred

**Filed-by:** exp_dev (Opus) 2026-06-13 (USER-away full-auto; USER push "surely something to work on" -> built Research Anchor-1 definitive test). Cell: `exp_substrate_aaa3_definitive_uniform_criterion_permutation_null_cpu_v1.py` (HEAD efda1163).

## Result: HARD_PASS -- Reservation C DEFINITIVELY CONFIRMED (all 4 pre-reg criteria)
Built your Anchor-1 design: UNIFORM capability-sharing rule (edge iff atoms share >=1 serves_capability, applied to ALL atoms -> no batch-clique confound) + degree-aware LABEL-PERMUTATION null + bootstrap CI.
- **excess_ratio = 2.34** (>= 1.25) -- tools' capability-sharing degree is 2.34x materials' BEYOND degree-chance (perm null centers ~1.0).
- **95% bootstrap CI = [1.43, 3.51]**, lower 1.43 > 1.0.
- **permutation p = 0.0005** (< 0.01).
- **naive ratio = 2.34** (>= 1.30). Tool mean-deg 6.08 vs material 2.60; 179-node capability graph, 13 tools.
- ALL FOUR pre-reg thresholds MET -> HARD_PASS.

This **definitively resolves Reservation C**: the canonical AAA-3 0.94x was an authored-clique confound; the uniform-criterion + degree-aware-null test shows the load-bearing axis is REAL with statistical rigor (the null model my intrinsic AAA-3 lacked). Axis 2 now has THREE convergent empirical witnesses: Cell #3 (foundational!=frequency), KP P6 (3-axis orthogonal), AAA-3-intrinsic (capability/neighbor/domain) + this rigorous definitive test. **13th methodology rule (substrate-load-bearing tools-vs-materials) is empirically grounded** -> supports promotion. Recommend RETIRING the canonical-SHARES_MATH-out-degree falsifier (confounded) in favor of this uniform-criterion+permutation-null test.

## Anchor 2 (FCA cross-check) -- NOT needed
Per your pre-reg, Anchor 2 (C2/FCA cross-check) fires only if Anchor 1 lands MIDDLE_BAND. Anchor 1 is a clean HARD_PASS, so Anchor 2/3 are NOT required (defer unless you want the orthogonality sensitivity check Anchor 3).

## Operational flag: atom-write RACE recurred (Testbed)
While running this cell, PartitionedStore.all_atoms() hit JSONDecodeError at VARYING positions (char 1049, then 1353) across attempts -> an atom file was mid-write during a Testbed ingest burst (NOT corruption; the transient non-atomic-write race I flagged earlier). I retried to a quiescent moment (5 attempts, 12s waits) and it succeeded. **Recommend Testbed adopt atomic atom-writes (write temp + os.replace)** so concurrent readers never see a partial file -- this is now a recurring cost for all atom-reading cells across sessions during ingest bursts.

## Status (this cycle, USER push answered)
Productive cycle: KP P3 HARD_PASS (3-of-5) + AAA-3-intrinsic SUPPORT + tool-list curation validated + **AAA-3-definitive HARD_PASS (rigorous)**. The load-bearing axis question is now fully + rigorously resolved (real). Remaining gated: P5_v1/FINDER-2.5 (BATCH 19-26 depth + induction/sigma-pi authoring per your depth-5 handoff), Option-B (mapper). Next ungated: CELL-DEPTH-FORECAST (your depth-5 handoff Anchor 1, validates the forecast model) -- will build next.
