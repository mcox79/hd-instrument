# Research -> Exp-Dev: 5 cheap empirical gap-closing experiments AUTHORIZED

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Drill-recommended pre-registered experiments not yet routed (gap inventory)

## Context

Today's 19 drills produced ~20 pre-registered empirical experiments. Most routed via specific cycle 232/233/234 routings. The 5 cheapest highest-leverage that remain unrouted are below.

## 5 cheap experiments AUTHORIZED

### 1. Substrate-CRF on WSJ POS (lift PP-364 Tier A 0.906 -> 0.92+)

**Per drill 4 substrate structured-prediction.**

Build: substrate-CRF (semiring DP + resonator-as-BP + Tier-2 emission/transition bundles + learned weights via structured-perceptron updates). Apply to WSJ POS tagging on the bundled UD-English-EWT or PTB sec 24.

Target: tag-accuracy >= 0.92 (substrate HMM PP-364 at 0.906).
Cost: ~1 day CPU.
Outcome: NEW Tier A candidate (substrate-CRF generalization of PP-364).

### 2. TP-HDC unified SVAMP rescue (lift unified 0.442 -> 0.50+)

**Per drill 6 unified solver SVAMP rescue.**

Build: per-benchmark context-binding (TP-HDC pattern, structurally identical to PP-346 polysemy rescue 0.342 -> 1.000 HP) + cleanup-margin soft-MoE router. Apply to unified arity-routed solver.

Target: unified macro >= 0.50 (currently 0.442 below 0.45 HP bar).
Cost: ~1 day CPU.
Outcome: pushes unified solver to Tier A bar; preserves single-solver unification.

### 3. Capacity-precision tradeoff (cheapest of drill 7 frontier-scale anchors)

**Per drill 7 frontier-scale interaction.**

Build: substrate KB scaled from kb10K -> kb100K -> kb1M with synthetic-padded facts; measure recall@1 + cleanup-margin distribution + memory footprint + retrieval latency. Compute free-probability ~30-line spectral observability at each scale (separately validates the framework).

Target: identify capacity regime shift threshold (sqrt(M) crosstalk -> log(M) separability per drill 7 prediction).
Cost: ~2 hr CPU.
Outcome: empirically characterizes substrate at scale; informs head-to-head + production claims.

### 4. CODE synthesis substrate-only empirical (confirm drill 1 ~0.05-0.15 ceiling)

**Per drill 1 CODE synthesis feasibility.**

Build: substrate-only HumanEval-EASY pass@1 attempt via template-retrieve + grammar-constrained slot-fill. No LLM. Substrate stores templates + CFG productions as Tier-2 bundles.

Target: confirm 0.05-0.15 ceiling OR refute (would indicate substrate-only synthesis viable).
Cost: ~2 hr CPU.
Outcome: closes honest substrate-only synthesis boundary OR opens substrate-only synthesis path.

### 5. Chung-Lu diagnostic on existing analogy benchmarks (FB15K + WN18RR + MIRB)

**Per drill 9 Chung-Lu + automorphism methodology.**

Build: ~30-line numpy diagnostic computing Chung-Lu rho (spectral density) + 1-WL orbit-novelty f_orb on FB15K + WN18RR + MIRB. Tells us which benchmarks are topology-confounded for substrate analogical retrieval.

Target: per-benchmark adequacy verdict; potentially refutes any single-benchmark "substrate ceiling" claim.
Cost: ~30 min CPU per benchmark (~1.5 hr total).
Outcome: methodology validation; closes the slipnet WN18RR diagnostic loop.

## Total cost: ~3-5 days CPU spread across 5 cells

These are independent + can run in parallel on cpu_runner_local.

## Sequencing recommendation

| Priority | Experiment | Cost | Justification |
|---|---|---|---|
| 1 | TP-HDC unified SVAMP (lift to Tier A bar) | 1 day | Closes a known Tier-A-bar miss; substrate-self-improvement validated |
| 2 | Substrate-CRF WSJ POS (new Tier A candidate) | 1 day | Extends validated NL capability; potential 11th Tier A |
| 3 | Capacity-precision tradeoff | 2 hr | Validates free-prob framework empirically; informs head-to-head |
| 4 | Chung-Lu diagnostic | 1.5 hr | Methodology validation; cheap |
| 5 | CODE synthesis empirical | 2 hr | Closes honest substrate-only boundary |

## Decision matrix for each

| Experiment | HARD_PASS | MIDDLE | HARD_FAIL |
|---|---|---|---|
| Substrate-CRF WSJ POS | >=0.92 (new Tier A) | 0.91-0.92 (annotation) | <0.91 (CRF infra needs refinement) |
| TP-HDC unified SVAMP | >=0.50 (Tier A unified) | 0.45-0.50 (PP-377 annotation) | <0.45 (mechanism doesn't recover) |
| Capacity-precision tradeoff | Regime shift detected at predicted threshold | Partial regime signal | No regime shift |
| CODE synthesis | >=0.15 (refutes ceiling) | 0.05-0.15 (confirms ceiling) | 0 (mechanism does not function) |
| Chung-Lu diagnostic | >=1 benchmark adequate (substrate testable cleanly) | All borderline | All inadequate (need synthetic calibrated benchmark) |

NO pre-registered defeat threshold per drill-defeatism rule. Empirical results decide.

## What this completes

Per gap inventory: 5 of ~8 drill-recommended experiments routed. Remaining gaps:
- Drill 8 conformal full 5 anchors (only metrics.py integration routed)
- Drill 3 slipnet top-5 substrate-only paths empirical + SCAN disjoint-vocab pilot
- 3x DEEP framework 5 pre-registered experiments

These can be routed after first 5 land OR if user prioritizes.

## Cross-references
- Drill outputs (10 backlog + 3x DEEP free-prob): notes/research_drill_*_2x_2026-06-11.md
- Pre-existing Exp-Dev queue: ASDiv cascade v2 + head-to-head GPU + GSM8K + Hendrycks revisit + SVAMP 4-wrapper + Phase 4B-FULL dep-parser
- Gap inventory in chat (this turn)

---

**Exp-Dev:** 5 cheap empirical gap-closing experiments AUTHORIZED (~3-5 days CPU total spread across 5 cells; independent parallel-runnable). Substrate-CRF + TP-HDC + capacity-precision + CODE synthesis + Chung-Lu diagnostic. Closes drill-to-build gap from today's 19 drills.
