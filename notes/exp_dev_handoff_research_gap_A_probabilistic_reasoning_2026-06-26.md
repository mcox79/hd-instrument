# exp_dev hand-off — research: Gap A probabilistic / soft-confidence reasoning

Filed-by: research (Opus 4.7 1M)
Filed-at: 2026-06-26
Trigger: USER deep drill on Gap A + USER addendum to compose with cortex layer landing today

Pause state: check `data/orchestrator_paused.flag` per standard exp_dev contract.

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off ranks anchor candidates
and points at the research note for the math + mechanism. It does NOT design cells inline;
exp_dev authors cells per autonomy declaration.

## Source research note

`notes/research_gap_A_probabilistic_reasoning_2026-06-26.md`

Read it FIRST for: the 3 mechanism classes (CAND-0/1/2), 2 cross-domain (CROSS-1/2),
discriminator design, brain-fidelity, substrate-better-than-brain angles, pre-registered
HARD-PASS / HARD-FAIL bands, citations.

## Anchor candidates — rank-ordered

### ANCHOR_1 (TOP — cheapest decisive test, highest P): soft_topK_cleanup_distribution_preserving_v1

- **Substrate-product reading:** ships a CALIBRATED retrieval primitive. Every cleanup
  returns top-K with calibrated relative confidences instead of throwing away K-1
  candidates per step. IMMEDIATELY product-useful for any uncertainty-sensitive
  application (medical, legal, financial). LLMs lack this; substrate ships it as a
  primitive output of cleanup, no learning required.
- **Tier hint:** **MEASURED_MECHANISM** by-construction (cleanup readout change); promotes
  to **CHAIN_GRADE** if 3-arm discriminator with R11 temperature scaling shows top-1@hop-5
  lift >= 0.03 AND entropy ratio H(hop-5)/H(hop-1) in [0.4, 0.9] AND ECE@hop-5 <= 0.15.
- **Why now:** the cheapest possible L2 lever currently identified. ~10 LOC change to
  cleanup primitive. 1-2 CPU-hours. Composes naturally with the n5/n6/n7 sequence-
  prediction harness already on disk; affects BPC measurement directly (current substrate
  is forced-argmax = entropy bound at 0; soft top-K carries entropy across hops). Predicted
  to close 0.2-0.5 bit of the 1.13-bit gap-to-text8-word-bigram WITHOUT new architecture.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL** = 0.55 / 0.25 / 0.20.

### ANCHOR_2 (USER-addendum top per cortex composition): cortex_prior_x_soft_topK_bayesian_inference_v1

- **Substrate-product reading:** ships a CORTEX-PRIOR BAYESIAN RETRIEVAL — substrate forms
  a prior over hypotheses from its slow-learned cortical schema (W_schema from gap4
  TWO_TIER + gap3 BCM), then updates the prior with hippocampal-fast evidence (W
  associative). This is the **glass-box Bayesian brain** product story; every step
  observable, every prior auditable, every evidence weight logged.
- **Tier hint:** **MEASURED_MECHANISM** target; promotes to **CHAIN_GRADE** if 4-arm
  discriminator shows ARM_C (cortex prior x soft top-K) top-1@hop-5 lift >= 0.04 over
  ARM_B (soft top-K alone) AND ECE@hop-5 <= 0.15.
- **Why now:** composes the cortex layer landing TODAY (gap4_two_tier_generational_W_v1
  HARD_PASS_PARTIAL) with the cheap soft top-K primitive from ANCHOR_1. The L2 categorical-
  lift product narrative requires cortex + bayesian inference + multi-hop posterior carry.
- **Why-now caveat (sequencing):** RUN ANCHOR_1 FIRST. If ANCHOR_1 HARD-FAIL, ANCHOR_2 is
  un-discriminable from underlying soft top-K problem. Also recommend deferring until
  TWO_TIER is full HARD_PASS (current HARD_PASS_PARTIAL leaves room for ANCHOR_2 MIDDLE
  caused by cortex-prior still being too weak, not the bayesian composition mechanism
  itself). If user wants ANCHOR_2 anyway, ARM_C vs ARM_B contrast still discriminates
  cortex-as-prior lift.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL** = 0.35 / 0.40 / 0.25 (deflated; novel-synthesis
  cap at 0.50 honored).

### ANCHOR_3 (substrate-better-than-brain marquee): multi_bank_parallel_hypothesis_tracking_v1

- **Substrate-product reading:** ships PARALLEL-HYPOTHESIS TRACKING at 50-1000 concurrent
  hypotheses. The categorical lift over the brain: brain caps at ~7 simultaneous
  hypotheses (Cowan 2001), substrate at multi-bank K=4096 holds 50-1000. **70x-150x
  parallel-search advantage at the inference bottleneck.**
- **Tier hint:** **MEASURED_MECHANISM**; promotes to **CHAIN_GRADE** if discriminator
  shows rank-1 vote >= 0.90 across >= 50 distinguishable hypothesis tracks on SYNTHETIC
  AMBIGUOUS chains (correct answer only emerges after hop-3 disambiguation; early commit
  by argmax provably fails).
- **Why now:** multi-bank WM is chain-grade at K=4096 (MULTI_64x) and K=8192 (MULTI_128x)
  TODAY; the hypothesis-per-bank routing is the novel composition. Requires ANCHOR_1 first
  (each bank initialized from soft top-K seed). 3-5 CPU-hours.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL** = 0.30 / 0.45 / 0.25 (deflated; bank-
  independence is the main risk).

### ANCHOR_4 (cross-domain; defer): particle_filter_SMC_substrate_v1

- **Substrate-product reading:** parallel particle cloud as substrate-native Bayesian
  filter. Treat each multi-bank WM slot as a particle carrying a hypothesis + weight.
  Importance-sample, resample, propagate.
- **Tier hint:** **CONCEPTUAL_PROBE** until basic substrate variant ships and passes a
  particle-cloud-entropy-tracks-true-posterior discriminator.
- **Why now:** defer until ANCHOR_3 lands. The multi-bank parallel routing in ANCHOR_3 is
  prerequisite infrastructure for the particle filter.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL** = 0.30 / 0.40 / 0.30.

### ANCHOR_5 (cross-domain; defer): free_energy_variational_message_passing_v1

- **Substrate-product reading:** predictive-coding glass-box column. Substrate cleanup
  error = prediction error; iterating cleanup + soft top-K + re-bind = variational message
  passing.
- **Tier hint:** **CONCEPTUAL_PROBE** until convergence is demonstrated in <= 10 iterations.
- **Why now:** lower P; less directly composable; defer until top 3 anchors are measured.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL** = 0.25 / 0.40 / 0.35.

## Context pointers

- Source note (math + mechanism + discriminator design):
  `notes/research_gap_A_probabilistic_reasoning_2026-06-26.md`
- Prior 5x drill (mechanism inventory + LLM failure taxonomy):
  `notes/research_drill_substrate_probabilistic_reasoning_5x_2026-06-08.md`
- R11 calibration protocol (R11 temperature scaling for ARM_C):
  `notes/research_R11_calibration_uncertainty_2026-05-21.md`
- Cortex layer LIVE today (cortex W_schema source for ANCHOR_2):
  gap4_two_tier_generational_W_v1 HARD_PASS_PARTIAL (status_log 21:28 UTC 2026-06-26;
  details in `data/orchestrator_status_log.jsonl`)
- BCM cell in flight (sharper cortex prior, re-run candidate for ANCHOR_2):
  `notes/exp_dev_handoff_research_gap3_brain_slow_schema_mechanism_2026-06-26.md`
- Modern Hopfield feature-regime in queue (CAND-1 composer):
  `notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md`
- Sequence-prediction harness for discriminator (n5/n6/n7 BPC measurement):
  `notes/research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md`
- Capability map row (PP-155 continuous-strength as substrate amplitude=confidence):
  `notes/substrate_capability_map.md` (search PP-155)
- HEADLINE + CHEAP DECISIVE TEST + HARD-PASS / HARD-FAIL bands:
  source note section "Cheap decisive test" + "Falsifiable predictions (pre-registered)"

## Contract section

- Pre-reg discipline per envelope-fail-bands: bands above are pre-registered HERE; exp_dev
  must lift them into the cell's prereg note verbatim before dispatch.
- Smoke gate mandatory per [[fix24-gpu-dispatch-must-actually-use-gpu]] — but these are
  CPU cells (1-5 hr); use cell-author smoke + remote_cpu_queue.
- Post-ship REMOTE VERIFY per Fix #11 pipeline template.
- Per-arm metrics-read per Fix #28 — DO NOT trust verdict_msg framing; read metrics.json
  per-arm before any cross-cell convergence claim.

## Autonomy declaration

exp_dev decides:
- Cell author (manual vs spawn cell-author sub-agent)
- Smoke seed + smoke timeout
- N_DIM choice (recommend N=8192 to match TWO_TIER cortex layer dimensionality, but
  N=4096 viable if smoke ok)
- Multi-hop depth for discriminator (recommend 5 hops; minimum 3)
- Queue routing (recommend remote_cpu_queue for CPU cells; local_cpu_queue if priority
  conflict)
- Discriminator extension (e.g. add ARM for perturbation-stability if cheap)
- Whether to bundle ANCHOR_1 + ANCHOR_2 into a single 5-arm cell (efficient if cell-author
  can handle; otherwise sequential)

Research's authority ends at the anchor list + bands + brain-mechanism math. exp_dev is
the cell-design authority.

Recommended FIRST dispatch: ANCHOR_1 single-cell, 3-arm discriminator (ARM_A hard-argmax,
ARM_B soft top-K untempered, ARM_C soft top-K + R11 temperature), n5/n6/n7-style sequence
harness, depth=5, 3 seeds, N=8192, smoke + remote_cpu_queue, 2 CPU-hr timeout.
