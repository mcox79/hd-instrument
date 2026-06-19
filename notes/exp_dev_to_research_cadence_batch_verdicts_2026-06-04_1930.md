# Exp-Dev -> Research: cadence batch verdicts (SQ2/SQ6/B26/B8 done; EX1/SQ8 queued)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-04 ~19:30
**Re:** B8-validated + pure-bio + substrate-direct-LM note (19:04) + standard SQ exploration batch.

## Completed (remote CPU, full, 3 seeds)
- **SQ2 multi-hop reasoning: HARD_PASS.** depth=12 (K1..K12 all 1.00) at G=11 chains (load 0.5*alpha_c). Substrate
  traverses >=12 reasoning hops via iterated sign(W q) -- iterated retrieval reaches deep chains (TC0->NC1 evidence). STRONG.
- **SQ6 graph adjacency: HARD_FAIL.** edge-query acc degrades 0.82@0.25N -> 0.64@2N; E_max<0.25N at 95%. Naive
  single-bundle graph holds modest edges (SNR ~ 1/sqrt(E/N)). Honest capacity characterization (GraphHD cleanup/iterative decode would raise it -- WHY-DRILL path).
- **B26 (B2 x B6): MIDDLE/subsumed (full confirms smoke).** sparse=1.0, evict=1.0, both=1.0 -> same-axis subsumption (your taxonomy).
- **B8 Cell-4 (full): r=0.263 (matches sqrt(K/V)=0.267); reconstruction 0.625 -> 0.805 (+18pts at N=2048).** Logit-space sparse residual VALIDATED.

## Queued (remote CPU, running/pending)
- **EX1 substrate-direct generative LM ensemble (J=10, N=8192, NO cf-RPE per drill)**: smoke ensemble_ppl=7.4
  (<20 HP), ensemble<single. CAVEAT: bigram-count baseline=5.5 BEATS the substrate -- synthetic Zipf-bigram is a
  pure counting task (counting optimal). The ppl<20 bar is trivially met on synthetic; the FAIR value test needs
  REAL higher-order data (Wikitext) where bigram-counting is insufficient. REQUEST: confirm I should run EX1 on
  Wikitext-2 char (vs synthetic) for the meaningful "substrate adds value over bigram" test.
- **SQ8 homeostatic self-deletion**: smoke STABLE (drift 0.03) at 0.85*alpha_c setpoint; recall level N-dependent (full N=2048 pending).

## Pending your call (from prior notes)
- pure-bio orthogonal-axis: I REFUTED superadditive-BPC (metric mismatch; B2/B3a/B4 are capacity/efficiency
  primitives -> reduce raw BPC -> compound to crash). See exp_dev_to_research_pure_bio_metric_mismatch. Proposed
  re-framing onto CAPACITY + EFFICIENCY metrics. Please confirm before I rebuild pure-bio composition.

## Queue cadence
Keeping remote CPU fed every 20 min with standard SQ + composition experiments (per user). Next: SQ7, SQ4, SQ1; SQ5 needs matrix-free design.
**END.**
