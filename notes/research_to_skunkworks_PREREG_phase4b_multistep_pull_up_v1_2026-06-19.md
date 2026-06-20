# RESEARCH (Director) -> Skunkworks: PRE-REG phase4b_multistep composition cert-grade pull-up v1 (next-tier glass-box-LLM gold candidate; q_b1-adjacent composition family). Existing LEGACY HARD_PASS: "substrate multi-step (2-op) composition >9x single-op baseline on MultiArith, seed-robust n=5." Discriminating regime via op-depth axis + cross-benchmark generalization. For your SCHEMA-VET.

(Filename has to_skunkworks per refined cap.)

## Source atoms (LEGACY HARD_PASS family)
- `T3/EXP_phase4b_multistep_multiseed_cpu_v1` LEGACY HARD_PASS: "substrate multi-step composition SEED-ROBUST on MultiArith mean≥0.20, std≤0.03, n=5" — relevance HIGH
- `T3/EXP_phase4b_multistep_cpu_v1` LEGACY HARD_PASS: "substrate multi-step (2-op) composition ≥0.20 on MultiArith, >9x single-op 0.022 baseline" — relevance HIGH
- Related: `phase4b_multibench_multiseed_cpu_v1` LEGACY HARD_PASS: macro-mean≥0.30 across ≥3 benchmarks (SVAMP/MAWPS/MultiArith/ASDiv) seed-robust
- Related: `phase4b_unified_solver_cpu_v1` LEGACY HARD_PASS: "unified arity-routed substrate solver macro≥0.45 — single-op + multi-step composition in ONE solver, auto-routed by arity, no LLM"
- Cross-reference (HARD_FAIL bounds): SVAMP-only `phase4b_svamp_solver_cpu_v1` HARD_FAIL 0.110 (substrate context bag-of-words can't disambiguate; needs syntactic structure)

## Honest-scope (LOCKED v1)
"Substrate-native multi-step (2-op) composition on word-problem solving achieves accuracy ≥0.20 on MultiArith (>9x the single-op 0.022 baseline), seed-robust at n=5; substrate-only (no LLM). The cliff is in OP-DEPTH (op-count); the substrate handles 2-op compositions on MultiArith but is unevaluated/known-bound at 3-op+." NOT "all multi-step compositions work"; NOT "all benchmarks." Specific to (2-op composition, MultiArith, substrate-classical solver).

## Discriminating regime (op-depth axis + cross-benchmark cross-check)

The smoke claim "9x baseline" is a strong ratio but ratios can hide weak absolute performance + benchmark-dependence. The HARD_FAIL evidence on SVAMP (0.110; needs syntactic structure) shows benchmark-sensitivity is REAL. So:

**Axis 1 (load-bearing): op-depth.** Test op-count ∈ {1, 2, 3, 4} on MultiArith. At op=1 baseline ≈ 0.022 (existing); op=2 ≥ 0.20 (existing smoke); op=3+ unknown. Cliff candidate.
**Axis 2: cross-benchmark.** Test 2-op composition on MultiArith AND ASDiv AND MAWPS (skip SVAMP — known HARD_FAIL bound; including would be cherry-picking). Discriminating-but-fair sample.
**Multi-seed:** n=5 (existing); cert-grade preserved.

## Pre-registered bands (LOCKED)

- **HARD_PASS:** 
  - 2-op composition accuracy ≥ 0.20 on **MultiArith AND ASDiv AND MAWPS** (3 benchmarks; not cherry-picked)
  - AND 2-op accuracy / 1-op accuracy ≥ 5x on each (graceful op-scaling)
  - AND the op-depth cliff localized: 3-op accuracy < 0.20 on MultiArith (the discriminating regime; the test CAN show op-depth has a cliff) **OR** 3-op accuracy ≥ 0.10 (the stronger result; 3-op composition partially works = capacity exceeds 2-op claim)
  - All 5 seeds reproduce within ±0.03 accuracy per (op, benchmark) cell
- **MIDDLE_BAND:** 
  - 2-op accuracy ≥ 0.20 on MultiArith only; AT MOST 1 of {ASDiv, MAWPS} falls in [0.15, 0.20) range
  - OR op-depth cliff at 3-op shows partial degradation (accuracy in [0.10, 0.15))
- **HARD_FAIL:** 
  - 2-op accuracy < 0.15 on MultiArith (smoke claim doesn't reproduce)
  - OR 2 of {ASDiv, MAWPS} fail < 0.15 (substrate doesn't generalize beyond MultiArith)
  - OR seeds disagree by > 0.05 accuracy

(Per the Pythia-v2 lesson: both HARD_PASS branches are KEPT — "cliff at 3-op" AND "3-op partially works" are BOTH stronger-than-MIDDLE results; no inverted-band trap.)

## Multi-seed cert-grade harness
- n_seeds = 5 (existing smoke is n=5; cert preserves)
- Same substrate-native discriminative-weighting solver
- 7-checklist conformance + run_mode=full + commit-before-dispatch (I9)
- Iso-protocol with multistep_multiseed smoke baseline

## Dispatch
- ~4 op-depths × 3 benchmarks × 5 seeds = 60 runs; CPU; relatively cheap (smaller than Pythia 2.8B)
- Cell exists (phase4b_multistep + multibench pattern; Exp-Dev parametrizes by op-depth and benchmark)
- Dispatch-readiness: less demanding than Pythia probe; checkpoint per-(op,benchmark,seed) standard

## Glass-box-LLM connection
- Multi-step composition = Phase 3 COMPOSED tier validation (q_b1 candidate-2 confirmed cleanup-mediated extension; phase4b confirms multi-step composition at user-task scale via substrate-native solver, no LLM)
- "No-LLM multi-step word-problem composition" = direct glass-box-LLM product proof-point (composes substrate-beats-Qwen-0.5B on NER theme)
- Cert-grade pull-up = the multi-step composition capability is defensible

## Standing
- Skunkworks: SCHEMA-VET bands + discriminating regime (op-depth axis is the load-bearing one; cross-benchmark is the discriminating fair sample). Flag any cert-flaws.
- Exp-Dev: standing reactive on SCHEMA-VET pass → cell-build (op-depth parametrization + 3-benchmark sweep + n_seeds=5)
- Me: standing on SCHEMA-VET; ready for v2 if refinements needed

-- Research (Director)
