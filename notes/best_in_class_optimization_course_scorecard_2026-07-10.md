# Best-in-Class Optimization Course + Per-Part Scorecard — 2026-07-10 (Director)

USER directive: "plot a course towards optimizing these parts so we're best in class ... it has to work and work well." Two phases per part: PHASE 1 WORK-FAIR -> PHASE 2 OPTIMIZE-TO-FRONTIER (brain reference + external SOTA as diagnostic). This is the living scorecard; update as parts move. [[feedback_best_in_class_not_shitty_optimize_every_part_to_frontier]]

## Scorecard (honest measured state -- no dressing up)

| Part | Phase | Measured state | Best-in-class reference | The gap / weak link | Frontier technique (Phase-2) |
|---|---|---|---|---|---|
| **Bind/unbind compose** | ~2 (near-BIC) | CHAIN_GRADE: perfect systematicity, lossless typed-binding under superposition | optimal VSA algebra | ~none for the op itself | keep; capacity via sharding when needed |
| **Memory/store capacity** | ~2 (proven law) | PP-127 sharding scaling law: per-shard 1.000 S1-S32, monolithic collapses S>=8, interference 0 | best assoc-memory capacity | apply degree-adaptive sharding where load>knee | PP-129 online-split; ACF (row 51, 50x) |
| **Glass-box / self-audit** | ~2 (BIC differentiator) | cert ledger, tiered, self-certifying, telemetry-sensitive discriminators | UNIQUE vs opaque models | maintain rigor at scale | keep; extend fairness+weak-point gates |
| **Readout / decode** | near-optimal (not the weak link) | single-shot matched-filter is the OPTIMAL linear detector; resonator+rerank did NOT beat it (VET) | SOTA factorizer/resonator capacity | decode is fine; below-floor signal is unrecoverable by ANY linear rank | do NOT over-invest; only relevant if a real SNR-floor appears |
| **Reasoning engine** | 1 (front) | on FAIR low/mid stratum: REACHES candidates (0.345) but RANKS poorly (0.097 into top10). Loses aggregate only because unfair hubs dominate | NBFNet/RNNLogic + brain few-shot relational inference | **RANKING of reached candidates** = the weak link (not compose, not decode, not capacity) | learned head-conditional path scoring, rank calibration, hop-norm conf, negative-evidence |
| **Ingest / corpus** | 1 (building) | current = thin symbol graph, ZERO grounded data; FB15k-237 = frequency-guessable hubs (unfair). CSKG dense-core headroom test in flight | dense + compositionally-derivable + grounded + spanning | need a corpus where held-out relations are DERIVABLE not guessable | CSKG cross-cutting core + grounded channels + derivability-selection |
| **Grounding / verifier** | 1 | concreteness = weak MM (works); magnitude(math)+social scalar channels FAILED -> abstract needs STRUCTURAL grounding | self-contained grounded-from-primitives (edge over LLMs that borrow) | abstract-domain grounding + making grounding load-bearing for INFERENCE | metaphor-structural bridge (Anchor 3); grounded-verifier (convergence exp) |
| **Native encoder** | 1 (not current front) | fidelity 0.28->0.53, sparsity/exact solid (prior) | SOTA embedding + brain grounded perception | co-evolving fidelity at graph scale | deferred until reasoning+corpus land |

## The strategic focus this scorecard forces

**The reasoning engine's weak link is RANKING, full stop.** Compose is CG, decode is near-optimal, capacity is a proven law -- none of those is the bottleneck. So "best-in-class reasoning" = a best-in-class RANKER of reached candidates on a fair (low/mid-degree) regime. That is a narrow, concrete optimization target, and it is exactly what the symbolic proof (afd0d1cd) is testing right now. Phase-2 reference for ranking = NBFNet-style learned path scoring + brain few-shot inference.

**Parts already at/near best-in-class:** compose (CG), sharded capacity (PP-127), glass-box self-audit. These are the foundation -- do not re-litigate; build on them.

**The durable escape from the whole frequency-wall problem = the corpus** (derivable relations, not guessable), building now, fairness-gated.

## Course sequence
1. PHASE-1 finish: reasoning engine beats frequency on the FAIR stratum (symbolic proof) + corpus passes the headroom acceptance test. (in flight)
2. On each pass -> PHASE-2 per part: name frontier reference, localize weak link, drill the frontier technique, implement (real compute), re-measure to BIC or a proven wall.
3. System-level: compose the BIC parts into an end-to-end system that works well (integration correctness, robustness, no seed-fragility, real perf). Parts-passing != system-working.
