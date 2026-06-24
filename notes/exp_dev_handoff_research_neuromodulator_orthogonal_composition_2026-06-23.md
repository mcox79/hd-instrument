# exp_dev hand-off — research: neuromodulator orthogonal composition (brain mechanism 2x drill)

Filed-by: research sub-agent (Opus synthesis over 8 parallel Sonnet lit-scans)
Date: 2026-06-23
Trigger: notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md
Urgency: HIGH — sparse-bipolar envelope cap (+0.44 bits BPC) just landed HARD_FAIL; this is the cleanest brain-grounded rescue candidate before substrate-as-LM is pivoted to refuse-aware-knowledge-store

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: substrate_dual_trace_sequential_neuromod_LM_v1 (PRIMARY)

Anchor pointer: Research note "Cheap decisive test" section + "Falsifiable predictions" Predictions 1+2
Substrate-product reading: Tests whether the brain's dual-trace + sequential-modulator-gating mechanism (Brzosko 2017 + Huertas 2016 + Fremaux-Gerstner 2016) can break the sparse-bipolar +0.44-bits envelope cap that single-modulator + naive-multiplicative composition cannot. Two-arm contrast (NAIVE_MULT vs DUAL_TRACE) isolates whether the envelope is rank-1-Hebbian-intrinsic (HARD_FAIL both arms = substrate-as-LM pivot acknowledged) vs single-trace-degeneracy (DUAL_TRACE HARD_PASS = envelope broken, scaling cell next).
Tier hint: GPU remote (matches current sweep cell), ~35-45min wall time. Cheap-decisive. 3 arms x 3 seeds x text8 N_TRAIN=100k.
Why-now: Brain-existence-proof asymmetry says we cannot pivot away from substrate-as-LM until the brain-grounded composition is HONESTLY tested. Naive-multiplicative Gap A spec was refuted by Marder STG GPCR convergence; dual-trace is the brain-correct alternative. Either HARD_PASS rescues substrate-as-LM, or HARD_FAIL is the cleanest evidence for the pivot.

Pre-reg bands:
  HARD-PASS: ARM_DUAL_TRACE BPC lift >= +0.20 vs current best sparse-bipolar AND >= +0.10 vs ARM_NAIVE_MULT (orthogonality not degeneracy)
  MIDDLE-BAND: ARM_DUAL_TRACE beats baseline by +0.05 to +0.20 AND beats NAIVE_MULT by >= +0.05
  HARD-FAIL: ARM_DUAL_TRACE within +/-0.05 of baseline OR fails to beat NAIVE_MULT
  CV < 0.05 across seeds mandatory; per-arm metrics via tools/peek_arm_metrics.py per Fix #28

### Anchor 2: substrate_dual_trace_scaling_v1 (CONTINGENT on Anchor 1 HARD_PASS)

Anchor pointer: Research note "Substrate-product implications" / "If HARD_PASS" + Prediction 2 mechanism
Substrate-product reading: If dual-trace breaks the envelope at N_DIM=8192 N_TRAIN=100k, must scale to N_DIM=16384 N_TRAIN=1M to test whether the envelope STAYS BROKEN at production-relevant scale (where the BPC gap to text8 word-bigram ~1.13 bits matters). The just-failed sparse-bipolar sweep showed lift halving from N=512 to N=2048 with single modulator; if dual-trace shows same scaling-degradation pattern, broken envelope at small N is illusory.
Tier hint: GPU remote, ~2-4 hours wall time. N_DIM={8192, 16384} x N_TRAIN={100k, 1M} x 3 seeds x dual-trace arm only.
Why-now: Production-relevance gate. Lift > +0.5 bits at scale = real LM substrate; lift halving = same envelope-cap story at bigger numbers.

Pre-reg bands:
  HARD-PASS: ARM_DUAL_TRACE@N16384_T1M lift >= +0.40 bits BPC vs ARM_DUAL_TRACE@N8192_T100k (lift GROWS with scale)
  MIDDLE-BAND: lift stays approximately flat (+/-0.10 bits across scaling)
  HARD-FAIL: lift halves like single-modulator sweep (envelope reappears at scale; substrate-as-LM still capped)

### Anchor 3: substrate_dual_trace_ablation_v1 (CONTINGENT on Anchor 1 MIDDLE_BAND)

Anchor pointer: Research note "If MIDDLE_BAND" path
Substrate-product reading: If dual-trace gives partial lift but not full HARD_PASS, ablation cell identifies which trace (E_pos novelty-gated, E_neg attention-gated) is load-bearing. ARM_E_POS_ONLY isolates novelty-driven LTP-trace contribution; ARM_E_NEG_ONLY isolates attention-driven LTD-trace; ARM_BOTH replicates dual-trace lift. If E_POS alone explains > 80% of total dual-trace lift, then orthogonality story is weakened (single-trace + smart timescale wins instead).
Tier hint: GPU remote, ~30-40min wall time. 3 ablation arms x 3 seeds.
Why-now: Tells the program whether to keep both traces (orthogonality real) or simplify to single-trace + smart timescale (parsimony).

Pre-reg bands:
  HARD-PASS (orthogonality confirmed): each-arm-alone delivers < 60% of BOTH-arms lift (super-additive composition)
  MIDDLE-BAND: each-arm-alone delivers 60-80% of BOTH lift (additive composition, each contributes)
  HARD-FAIL (orthogonality refuted): one arm alone delivers > 80% of BOTH lift (other trace is decorative)

### Anchor 4: substrate_encoder_replacement_diagnostic_v1 (CONTINGENT on Anchor 1 HARD_FAIL)

Anchor pointer: Research note "If HARD_FAIL" + Prediction 3
Substrate-product reading: If BOTH dual-trace and naive-multiplicative within +/-0.05 of baseline, the bottleneck is NOT modulator composition AT ALL. Per Prediction 3, diagnose by routing to encoder-replacement: swap substrate's own-encoder for pretrained Pythia / word2vec / sentence-bge as diagnostic probe (NOT as substrate-product answer per Path C lockin). If pretrained encoder + same single-trace breaks the envelope, encoder was the bottleneck. If pretrained encoder ALSO caps, the rank-1 Hebbian floor is structural.
Tier hint: GPU remote, ~1-2 hours wall time. Multi-arm encoder swap.
Why-now: Provides clean diagnosis between "modulator composition is the lever" vs "encoder is the lever" vs "rank-1 Hebbian floor is structural" — three distinct substrate-product implications.

Pre-reg bands:
  HARD-PASS (encoder bottleneck): pretrained-encoder + single-trace BPC lift >= +0.30 vs current best sparse-bipolar
  MIDDLE-BAND: pretrained-encoder gives +0.10 to +0.30 lift (encoder is partial bottleneck)
  HARD-FAIL (structural rank-1 cap): pretrained-encoder gives < +0.10 lift => META atom: substrate_as_LM_genuinely_capped_at_rank1_hebbian_floor (commit pivot to refuse-aware-knowledge-store)

---

## Context pointers (file paths only, exp_dev reads them)

- d:/AI/hd-instrument/notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md  (this drill — load-bearing)
- d:/AI/hd-instrument/notes/next_iteration_composition_spec_2026-06-23.md  (Gap A original spec; lines 14-26 superseded by this drill)
- d:/AI/hd-instrument/notes/research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md  (prior breadth scan; mech #4 detailed here)
- d:/AI/hd-instrument/data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json  (just-failed envelope cap reference)
- d:/AI/hd-instrument/data/exp_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu/metrics.json  (single-modulator baseline; MIDDLE_BAND; lift-halving pattern)
- d:/AI/hd-instrument/experiments/exp_substrate_drosophila_mb_sparse_single_modulator_v1_n4096.py  (single-modulator cell architecture to extend with dual-trace)
- d:/AI/hd-instrument/tools/peek_arm_metrics.py  (Fix #28 mandatory pre-framing check)

---

## Contract

- Pre-reg per envelope-fail-bands (Fix #19; bands stated above for each anchor)
- Smoke gate via tools/predispatch_check.py before cell-author spawn (Fix #26)
- Per-arm metrics via tools/peek_arm_metrics.py before any tier/framing claim (Fix #28)
- Foreground Store + cert_ledger writes (Fix #20: no background pipe-tail monitoring)
- Verify-the-referent on cross-arm metrics (Fix #28 recurring)
- GPU dispatch must actually use GPU (Fix #24): torch.cuda + batched ops + concurrent-seed harness

## Autonomy declaration

exp_dev decides:
- Exact substrate scaffold to extend (existing drosophila_mb cell vs fresh cell vs fork sparse_bipolar_param_sweep)
- Whether to author all 4 anchors as one parametric cell or 4 separate cells
- Smoke-test design (clean synthetic data per [[feedback-smoke-clean-synthetic-data]])
- Whether to dispatch Anchor 1 alone first (cheapest decisive) and wait for verdict before authoring 2/3/4 — RECOMMENDED to avoid spawn-spam per Fix #27
- Time constants for E_pos/E_neg (research note suggests tau_fast~5, tau_slow~50 as starting point; exp_dev free to grid-search if cheap)
- Whether to compose dual-trace ON TOP OF best sparse-bipolar config (f=0.02 N=8192) per L5 cross-thread synthesis or test standalone first

Research note's "Cheap decisive test" section provides the load-bearing logic; exp_dev maps that logic to actual cell construction.

If exp_dev finds the dual-trace formulation requires architectural changes outside cell-author scope (e.g., new substrate primitive in hdlab/), route back to Director for atomization decision.
