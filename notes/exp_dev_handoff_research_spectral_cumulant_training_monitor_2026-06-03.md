# exp_dev hand-off -- research: free-cumulant spectral fingerprint as live LLM training monitor

**Filed:** 2026-06-03 by research sub-agent.

**Trigger:** Research drill on free-cumulant spectral fingerprint (Tier-1 F4, advisor score 5.5) delivered actionable probe experiment design with pre-registered HP/MID/HF bands. Finding: substrate spectral observer architecture is experimentally testable at small-transformer scale with ~6h GPU budget.

**Research note path:** `notes/research_drill_spectral_fingerprint_live_training_monitor_2026-06-03.md`

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching exp_dev.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. Spectral-cumulant training-phase predictor -- small transformer smoke probe (HIGHEST PRIORITY)

- **Anchor pointer:** Research note Section 4 (Probe Experiment Design). Cheap decisive test in Section "Cheap decisive test."
- **Substrate-product reading:** Attaches a spectral observer (fixed random projection of residual stream at layer ~0.7L) to a small transformer training run. Computes free-cumulant trajectory (kappa_2, kappa_3, kappa_4) every N steps. Pre-registers whether cumulant trajectory leads validation-loss phase transitions by >= 100 steps. Tests Gain A (auto-stop) directly: Correlation Trap onset (kappa_4 outlier excess) vs. validation perplexity rise timing.
- **Tier hint:** Local CPU or remote CPU smoke (small transformer, <25M params, WikiText-103 or similar; induced overfitting via repeated subset). Wall time estimate: 30-60 min for smoke. Full run: 4-6h A100.
- **Why now:** Tier-1 F4 advisor score 5.5 (highest current next-drill candidate). Convergent evidence from 3 independent papers (HTSR arXiv:1810.01075, Correlation Traps arXiv:2605.12394, Spectral Alignment arXiv:2510.04202). First substrate probe that tests a training-monitor capability (new cap_map row candidate). No existing anchor covers this axis.

### 2. Spectral-cumulant LR modulation experiment (Gain B validation)

- **Anchor pointer:** Research note Section 5, Gain B. Closed-loop architecture in Section 3(c).
- **Substrate-product reading:** After smoke validates spectral-phase prediction, this anchor tests whether substrate-signaled eta_multiplier (high during rapid-learning phase, decayed at plateau-onset from kappa_2 saturation) improves convergence speed vs. fixed cosine schedule. Compares steps-to-convergence under substrate-gated lr vs. Adam baseline.
- **Tier hint:** GPU (multi-seed comparison; full training run needed for convergence comparison). Only queue after Anchor 1 smoke PASSES.
- **Why now:** Gain B (lr modulation) is the ACh-analog capability -- most novel relative to current LLM training practice. Builds on Anchor 1 infrastructure.

### 3. Spectral fingerprint of continual-learning forgetting onset (Bet B tie-in)

- **Anchor pointer:** Research note Section "Cross-thread synthesis" (Bet B 4-stage CL tie-in). 4-stage compositional CL anchor from project note 2026-05-27.
- **Substrate-product reading:** During 4-stage continual learning, attach spectral observer. Does kappa_3 reversal (asymmetry sign flip) precede catastrophic forgetting as measured by retention_A drop? If yes: substrate provides a forgetting-onset warning signal for CL systems -- a direct product primitive for the Bet B direction.
- **Tier hint:** GPU (requires full 4-stage CL run + spectral monitoring). Only queue after Anchor 1 smoke PASSES.
- **Why now:** Ties Tier-1 free-probability finding to Bet B direction. Doubles the product surface of a single engineering investment.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_spectral_fingerprint_live_training_monitor_2026-06-03.md`
- Field advisor output: F4 Tier-1 score 5.5 (free-probability anchor, yield 100%, 1 prior drill)
- Related handoff (free-probability RRAM noise): `d:/AI/hd-instrument/notes/exp_dev_handoff_research_free_probability_rram_noise_2026-06-02.md`
- HTSR implicit self-regularization: arXiv:1810.01075
- Correlation Traps overfitting detection: arXiv:2605.12394
- Spectral Alignment loss-explosion predictor: arXiv:2510.04202
- Dyson Brownian motion weight dynamics: arXiv:2411.13512
- Yu-Dayan ACh expected uncertainty: Neuron 46, 681-692 (2005)

---

## Contract

exp_dev takes these anchor pointers, reads the research note, and designs the experiments with full autonomy over: N, projection dimension, transformer size, training corpus, seed count, monitoring interval, threshold values, HP/MID/HF bands, queue choice, and anchor naming. Orchestrator does not pre-specify any of these.

## Autonomy declaration

exp_dev decides: smoke vs FULL profile per Tier A/B/C policy; whether Anchor 2 and 3 queue contingent on Anchor 1 smoke result; whether to batch Anchors 2+3 into same GPU instance as Anchor 1 FULL; whether to split across local/remote CPU/GPU based on current queue depths.
