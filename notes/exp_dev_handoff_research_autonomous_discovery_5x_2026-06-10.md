# exp_dev hand-off -- research: autonomous discovery 5-stream

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research delivery notes/research_drill_autonomous_discovery_5x_2026-06-10.md -- 5-stream convergence on substrate-native autonomous discovery mechanisms. Multiple mechanisms ready for empirical test; cheapest test is a read-only analysis of existing retrieval logs.

**Pause state:** Check data/orchestrator_paused.flag before queuing. If paused, hold this handoff pending resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** This handoff names ANCHORS and POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, full profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. COMPRESSION-PROGRESS-SIGNAL (Tier C / local CPU, ~30 min)

- **Anchor pointer:** research note F2.2 / Test 1 section. The cheap decisive test for whether the Schmidhuber compression-progress fitness function is discriminating on existing substrate retrieval logs.
- **Substrate-product reading:** If the LZ77 compression delta is discriminating (Spearman rho > 0.3 between delta and query-context diversity), then F2.2 is immediately operational as a data quality scorer and novelty fitness function. Product implication: real-time telemetry on "how much new capability this document adds."
- **Tier hint:** Local CPU. Pure analysis of existing retrieval logs; no new training. No GPU needed. Queue: local_cpu_queue.
- **Why now:** Cheapest decisive gate. All downstream mechanisms (dreaming, quasispecies, MAP-Elites) benefit from knowing whether compression-progress signal exists. Run this first.
- **Hard-pass threshold:** Spearman rho > 0.3 AND top-quartile atoms cover 2x more query contexts than bottom-quartile.
- **Hard-fail threshold:** rho < 0.05 OR compression delta variance < 1% of mean delta.

### 2. DREAMING-SUBSTRATE-SMOKE (Tier B / remote CPU, ~1 day)

- **Anchor pointer:** research note F2.3 / Test 2 section. Three-phase loop: Wake (standard retrieval) -> NREM (low-threshold replay, candidate generation) -> REM (evaluation of candidates on held-out query batch).
- **Substrate-product reading:** A substrate that generates novel atoms offline is the clearest product differentiator vs. static retrieval. If the dreaming mechanism works, it is the foundation of the "substrate improves between queries" product claim.
- **Tier hint:** Remote CPU. Smoke is 500-query wake pass + 1 NREM pass + 1 REM evaluation. No GPU required. Queue: overnight_queue (remote_cpu_queue).
- **Why now:** Highest P_deflated of all discovery mechanisms (0.45). Biology precedent is the strongest (hippocampal generative replay, adversarial dreaming paper PMC9071267). Smoke is cheap and decisive.
- **Hard-pass threshold:** >10 new atoms per 500-query wake session that score above threshold on held-out queries AND are not within cosine distance 0.05 of existing atoms.
- **Hard-fail threshold:** Zero new atoms pass REM evaluation over 5 consecutive wake sessions OR all new atoms are within cosine distance 0.05 of existing atoms (redundant).

### 3. QUASISPECIES-SMOKE (Tier B / remote CPU, ~1 day)

- **Anchor pointer:** research note F2.1 / Test 3 section. Population of k=5 codebooks with mutation-selection dynamics. Evaluate coverage gain on held-out query batch.
- **Substrate-product reading:** Quasispecies population provides a natural ensemble for retrieval confidence estimation (standard deviation across k codebooks = calibrated uncertainty). Directly usable as a reliability signal in the product API.
- **Tier hint:** Remote CPU. k=5 codebooks, 50 generations, held-out evaluation. No GPU needed for smoke. Queue: overnight_queue.
- **Why now:** P_deflated = 0.42. Wright-Fisher population-genetics drill (2026-06-04) established the drift correction formula; this smoke tests the Eigen quasispecies substrate analog directly.
- **Hard-pass threshold:** >5% coverage gain on held-out batch at k=5 vs. single codebook.
- **Hard-fail threshold:** Quasispecies DEGRADES coverage vs. single codebook at mu=0.01 (error threshold crossed at this rate).

### 4. STOCHASTIC-RESONANCE-NEAR-MISS (Tier C / local CPU, ~1 hour)

- **Anchor pointer:** research note F2.5 / Test 5 section. Near-miss queries (confidence in [0.6, 0.8]) with noise injection at multiple sigma levels.
- **Substrate-product reading:** Extends PP-276 stochastic-resonance to the discovery context. If optimal noise improves >20% of near-miss queries, this is a zero-cost mechanism (no new architecture) for expanding retrieval coverage.
- **Tier hint:** Local CPU. Pure retrieval test on existing data. Queue: local_cpu_queue.
- **Why now:** Cheapest non-analysis test after compression-progress signal. Extensions of existing PP-276 work have high prior probability of positive result.
- **Hard-pass threshold:** At optimal sigma, >20% of near-miss queries cross threshold (vs. 0% at sigma=0).
- **Hard-fail threshold:** No sigma level improves more than 5% of near-miss queries.

### 5. MAP-ELITES-COVERAGE-SMOKE (Tier B / remote CPU, ~2 days)

- **Anchor pointer:** research note F2.8 / Test 4 section. MAP-Elites over a 10x10 domain-difficulty behavioral descriptor grid. Track cell coverage over 500 queries.
- **Substrate-product reading:** The behavioral coverage map is a product-legible representation of "what the substrate is good at." Filling the grid over time gives a progress metric that is customer-visible. This is the clearest capability visualization.
- **Tier hint:** Remote CPU. MAP-Elites implementation + 500-query run. No GPU needed. Queue: overnight_queue.
- **Why now:** MAP-Elites is the most empirically validated quality-diversity algorithm (2024-2025 literature confirms robustness). P_deflated = 0.44. The behavioral descriptor space definition is the main design decision.
- **Hard-pass threshold:** >50% cells filled after 500 queries, coverage growing monotonically.
- **Hard-fail threshold:** Coverage plateaus below 20% before query 300.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_autonomous_discovery_5x_2026-06-10.md
- PP-276 stochastic resonance prior work: check notes/strategy_decisions*.md for PP-276 anchor state
- Population-genetics / Wright-Fisher prior drill: d:/AI/hd-instrument/notes/research_drill_wright_fisher_kimura_substrate_population_genetics_2x_2026-06-04.md
- Compositional cliff crossing brief: C:\Users\marsh\.claude\projects\d--AI\memory\substrate_v3_compositional_cliff_crossed.md
- Schmidhuber formal theory: IEEE TAMD 2010 (10.1109/TAMD.2010.2056368)
- Adversarial dreaming: PMC9071267

---

## Contract section

exp_dev accepts this handoff and owns all implementation and design decisions. The research note provides theoretical grounding and pre-registered pass/fail thresholds. exp_dev decides: exact N/M/K, mutation rates, threshold values, codebook population size, smoke vs. full profile, queue assignment, anchor naming, ETA.

The recommended sequence (if queues have capacity): (1) COMPRESSION-PROGRESS-SIGNAL first (local, ~30 min, read-only) -> (2) STOCHASTIC-RESONANCE-NEAR-MISS if signal exists (local, ~1 hour) -> (3) DREAMING-SUBSTRATE-SMOKE (remote CPU, 1 day) in parallel with (4) QUASISPECIES-SMOKE (remote CPU, 1 day) -> (5) MAP-ELITES-COVERAGE-SMOKE (remote CPU, 2 days) after smoke results are in.

If any Hard-fail fires: do not escalate mutation rate or theta modifications; return finding to Research for 2x drill.

---

## Autonomy declaration

exp_dev has full autonomy over all implementation parameters within the pass/fail bands specified above. Research has pre-registered the thresholds; exp_dev designs the experiments. No further research consultation needed before dispatch unless a mechanism requires novel substrate architecture not yet implemented.
