# exp_dev hand-off -- research: continuous-time write dynamics

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery on continuous-time write dynamics for additive Hebbian binary associative memory. Derived tau_mem ~ N/(2*lambda) and critical rate lambda_c ~ gamma*N/2. Pre-registered smoke proposal is directly exp-dev-actionable.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters beyond what is structurally required for the question.

**Source note:** `notes/research_continuous_time_write_dynamics_2026-06-01.md` (inline synthesis -- see research agent output in session)

---

## Anchor candidates (rank-ordered)

### 1. tau_mem empirical validation -- continuous-write decay sweep

- **Anchor pointer:** Research delivery 2026-06-01; tau_mem prediction tau ~ N/(2*lambda) from compound-Poisson + OU theory; pre-reg bands in source note (HP: within 20%, MID: within 50%, HF: >2x deviation).
- **Substrate-product reading:** If tau_mem prediction holds, the substrate has a quantitatively characterizable write-throughput envelope -- a product-relevant operating parameter. If it fails, the SDE model is mis-specified and the decay mechanism needs revision (non-exponential? alpha-stable? spectral cascade?).
- **Tier hint:** CPU smoke first (N=1024, lambda in {0.01, 0.1, 1.0}, gamma in {0.1, 1.0}, measure retrieval accuracy decay vs time). Likely local or remote CPU. GPU only if N needs scaling to 8192 for confirmation.
- **Why now:** First-ever quantitative prediction for continuous-time write dynamics. No prior experimental anchor exists for this capability axis. Cheap decisive test -- 6 (lambda, gamma) cells, measure retrieval vs time, compare slope to tau_mem formula.

### 2. Critical rate collapse probe -- lambda_c boundary

- **Anchor pointer:** Research delivery 2026-06-01; lambda_c ~ gamma*N/2 derived from stationarity condition (SNR collapse when write noise variance 2*lambda/gamma exceeds Hopfield retrieval margin). Tests whether capacity collapses sharply at predicted lambda_c or degrades gradually.
- **Substrate-product reading:** Sharp collapse confirms first-order capacity transition in continuous time (consistent with SKAH-M multistability signature from project_pred4_hysteresis). Gradual collapse would imply smoother operating envelope -- easier product engineering.
- **Tier hint:** CPU or remote CPU. Sweep lambda at fixed N, gamma; measure P_retrieval at steady state; find collapse point.
- **Why now:** lambda_c is a product engineering constraint -- it defines the maximum safe write rate for a given decay parameter. Must be measured before any write-rate-sensitive product feature can be specified.

### 3. Stationary Wishart covariance verification

- **Anchor pointer:** Research delivery 2026-06-01; theory predicts W_inf ~ Wishart(lambda/gamma, N) in the decay-dominated regime; covariance matrix W W^T should follow Marcenko-Pastur law with ratio lambda/gamma.
- **Substrate-product reading:** Connects continuous-time write dynamics to free-probability (fruit-bearing field, 100% yield, 1 drill). If stationary spectrum follows Marcenko-Pastur, the random-matrix tools already validated for the substrate extend directly to the continuous-write regime.
- **Tier hint:** CPU analytical check -- generate W under continuous-write simulation, compute eigenvalue spectrum, compare to Marcenko-Pastur with effective ratio lambda/gamma.
- **Why now:** Structural validation of the SDE class identification. If confirmed, opens free-probability / Tracy-Widom machinery (F2, F4 advisors top-5 candidates) to continuous-write analysis.

---

## Context pointers

- Research synthesis: inline in research sub-agent session output 2026-06-01
- Field advisor top-5: `tools/orchestrator/research_field_advisor.py` -- free-probability F2/F4, semiconductor D1/D2/D7 all tier-1
- Cap map: `data/cap_map.csv` -- continuous-write dynamics not yet a named row (propose adding as Cap 9 or Cap 2 extension)
- Prior SKAH-M class: `notes/project_substrate_skahm_class_confirmed_2026-05-27.md`
- Non-eq stat-mech: `notes/project_substrate_non_eq_stat_mech_class_2026-05-27.md`
- Hysteresis: `notes/project_pred4_hysteresis_first_order_confirmed_2026-05-27.md`

---

## Contract

exp_dev is authorized to:
- Design and queue the tau_mem smoke (Anchor 1) as a CPU-tier anchor
- Design and queue the lambda_c boundary probe (Anchor 2) as a CPU-tier anchor
- Design the Wishart covariance check (Anchor 3) as a local/CPU analytical probe
- Sequence anchors per cheapest-first (PROT-004): Anchor 3 (pure analysis) -> Anchor 1 (smoke) -> Anchor 2 (sweep)
- Promote any anchor to GPU if N>4096 is required for the question to be decisive

exp_dev is NOT authorized to:
- Modify cap_map rows without orchestrator approval
- Pre-specify HP/MID/HF numerical bounds (exp_dev derives these from the formula + formula-selftests per [[feedback-strategy-spec-formula-selftests]])
- Queue more than 3 anchors in one refill without orchestrator confirmation

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: all anchor specifications (N, M, K, seeds, thresholds, queue routing, anchor names, ETAs) are exp_dev's design decisions. This hand-off provides the WHAT and WHY; exp_dev provides the HOW.

Acted-on 2026-06-02: continuous-time write dynamics absorbed into streaming-aging baseline + Q9 tau_mem corrected SDE work
