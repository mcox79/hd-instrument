# exp_dev hand-off -- research: hippocampal-phenomena-mapping

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery notes/research_hippocampal_phenomena_mapping_2026-06-01.md; 3 concrete cheap decisive tests with pre-reg HP/HF bands ready for empirical validation.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching. If present, hold.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Context

Research drill mapped 7 hippocampal phenomena to substrate algebra (algebraic + lit-scan only). Three phenomena produced concrete, cheap-to-test predictions with pre-registered HP/HF thresholds. The research note contains the full derivations and literature benchmarks.

Research note path: `notes/research_hippocampal_phenomena_mapping_2026-06-01.md`

---

## Anchor candidates (rank-ordered)

### 1. Basin-radius scaling vs. load -- pattern completion empirical validation

- **Anchor pointer**: Section 1 of research note. Formula: r_basin ~ sqrt(1 - alpha/alpha_c). Biological benchmark: Treves-Rolls (1991) CA3 formula pmax = C_RC * a * ln(1/a) * k.
- **Substrate-product reading**: Cheapest decisive test. Store M patterns at varying loads alpha = M/N. Measure retrieval accuracy vs. initial corruption fraction rho. Plot empirical r_basin(alpha) vs. analytical formula. If R^2 > 0.90, substrate quantitatively matches Treves-Rolls and the neuroscience-modeling product narrative is substantiated.
- **Tier hint**: Local or CPU smoke (N=1024, ~140 patterns max, 10 seeds, 10 corruption levels). Estimated wall clock < 30 min.
- **Why now**: This is the cheapest of the 3 tests and the most direct parameter-mapping check against a published biological model. Settles whether substrate belongs in the same quantitative class as Treves-Rolls or merely the same qualitative class.

### 2. Engram ablation curve -- deletion certificate threshold

- **Anchor pointer**: Section 5 of research note. Formula: m_residual = m0 * (1 - f / f_crit), f_crit = a^2 * N. For N=8192, a=0.02: ~27M targeted weight entries = 0.04% of total W.
- **Substrate-product reading**: Directly validates the deletion certificate product story with a quantitative biological framing. The ablation formula is fully derivable (zero free parameters). If the linear m_residual curve is confirmed, the deletion-cert capability gains a biological precedent (CA3 engram ablation) AND a computable engineering bound (exactly how many weights to zero for guaranteed retrieval disruption).
- **Tier hint**: Local or CPU (single-pattern ablation sweep, varies f from 0 to 1). Very fast.
- **Why now**: Deletion-cert (PP-9) is a SHARED PRIMITIVE driving 5+ product stories. Confirming the biological engram framing strengthens the narrative for all 5 downstream product uses simultaneously.

### 3. Non-reciprocal W replay directionality -- trajectory asymmetry

- **Anchor pointer**: Section 3 of research note. Prediction: asymmetric component A = (W - W^T)/2 != 0 produces statistically significant forward-biased replay in random-init dynamics. This is a NOVEL prediction absent from Treves-Rolls, Marr, and Krotov DAM.
- **Substrate-product reading**: If confirmed, substrate's non-reciprocal FRSB class has a direct functional consequence (replay directionality) that is algebraically controlled -- no STDP tuning required. This opens the neuromodulation product framing: non-reciprocal W as a programmable replay-direction control knob.
- **Tier hint**: CPU or GPU depending on seeds required for statistical power (research note suggests p < 0.05, N=1024, 50 seeds). Likely CPU (non-trivial but not GPU-scale).
- **Why now**: This is the most novel prediction. If it HARD-PASSes, it distinguishes substrate from ALL existing hippocampal AM models on a falsifiable empirical axis. If it HARD-FAILs, the non-reciprocal mechanism claim loses behavioral relevance and needs rescue.

---

## Context pointers

- Research note: `notes/research_hippocampal_phenomena_mapping_2026-06-01.md`
- Cap_map deletion-cert row: `notes/substrate_capability_map.md` PP-9 and SHARED PRIMITIVE note
- Non-reciprocal FRSB confirmation: project memory `project_substrate_non_eq_stat_mech_class_2026-05-27.md`
- SKAH-M class confirmation: project memory `project_substrate_skahm_class_confirmed_2026-05-27.md`
- SEB regime: substantiated in cap_map CAN section; SEB floor = slow-forgetting biological analog

---

## Contract

exp_dev owns: anchor naming, sweep grid, threshold bands, queue assignment, smoke profile, FULL profile, pre-reg write, ship verification. Research sub-agent has provided: biological benchmarks, analytical formulas, parameter mappings, HP/HF bounds (as research-grade estimates, not engineering specs -- exp_dev re-derives independently).

## Autonomy declaration

exp_dev may reorder these anchors, split any anchor into smoke+FULL stages, or combine anchors 1 and 2 into a single experiment if they share infrastructure. exp_dev may decline any anchor that does not meet queue-justification criteria per [[feedback-no-padding-experiments]]. exp_dev may route to any tier per the Tier A/B/C policy.

<!-- routing-completed: Acted-on 2026-06-01: handoff to Round 10 dispatch -->
