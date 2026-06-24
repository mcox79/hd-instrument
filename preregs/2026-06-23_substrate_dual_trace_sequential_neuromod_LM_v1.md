# Prereg: substrate_dual_trace_sequential_neuromod_LM_v1

**Filed:** 2026-06-23
**By:** exp_dev (Sonnet sub-agent)
**Trigger:** notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md (Anchor 1)
**Status:** PRE-REGISTERED (filed before smoke; immutable after)

---

## Hypothesis

The sparse-bipolar LM envelope cap (+0.44 bits BPC) is a signature of SINGLE-TRACE SINGLE-MODULATOR degeneracy,
not a fundamental rank-1 Hebbian floor. The brain-correct rescue (Brzosko 2017 + Huertas 2016) is TWO SEPARATE
ELIGIBILITY TRACES with DIFFERENT timescales gated by DIFFERENT modulators:
  - E_pos (LTP-trace, tau_pos=5 steps) gated by dopamine (novelty/prediction-error)
  - E_neg (LTD-trace, tau_neg=50 steps) gated by ACh (attention/familiarity)
  - W += dopa * E_pos - ACh * E_neg

The naive-multiplicative approach (3-axis product on ONE trace) is degenerate per Marder STG GPCR
convergence: dopa * ACh * serotonin = single effective scalar eta_eff = same as one modulator.

This cell provides a DECISIVE TEST: ARM_DUAL_TRACE vs ARM_BASELINE vs ARM_NAIVE_MULT.
Either dual-trace breaks the envelope (HARD_PASS, substrate-as-LM viable) or it confirms the
rank-1 Hebbian cap is structural (HARD_FAIL, pivot to refuse-aware-knowledge-store acknowledged).

---

## Experimental design

**Anchor:** substrate_dual_trace_sequential_neuromod_LM_v1
**Script:** experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py
**Queue:** overnight_queue (GPU; N_DIM=8192 matmul-bound, Fix #22 trigger)
**Seeds:** [7, 17, 23] x 3 arms
**N_DIM:** 8192 (production N; matching fair_harness baseline config)
**N_TRAIN:** 100,000 text8 word tokens
**f_sparse:** 0.02 (best from param_sweep; matching envelope cap reference)
**Encoder:** word2vec-google-news-300 (hoisted; char-trigram fallback)
**Harness:** joint (T, lambda) sweep on dev; eval on test (same as fair_harness chain-grade)
**Metrics:** BPC, top1_acc, MRR@10 (per-arm, per-seed)

**Arms:**
1. ARM_BASELINE: cf-RPE single-trace dopamine only; W += dopa * outer(Delta, src)
   Reproduces ARM_DOPAMINE_ONLY from 3axis cell; direct envelope-cap reference.
2. ARM_NAIVE_MULT: 3-axis multiplicative on ONE trace; W += (dopa * ACh * 5HT) * outer(Delta, src)
   Replicates Gap A spec; tests Marder degeneracy prediction directly.
3. ARM_DUAL_TRACE: E_pos LTP (tau=5) + E_neg LTD (tau=50); W += dopa * E_pos - ACh * E_neg
   Brzosko 2017 + Huertas 2016 sequential mechanism; orthogonality via temporal separation.

---

## Pre-registered HARD bands (IMMUTABLE)

**HARD_PASS:** ARM_DUAL_TRACE BPC lift >= +0.20 bits vs ARM_BASELINE
              AND ARM_DUAL_TRACE BPC lift >= +0.10 bits vs ARM_NAIVE_MULT
              (orthogonality real; envelope broken)

**MIDDLE_BAND:** ARM_DUAL_TRACE beats ARM_BASELINE by +0.05 to +0.20 bits
                AND ARM_DUAL_TRACE beats ARM_NAIVE_MULT by >= +0.05 bits
                (orthogonality partial; ablation cell next per Anchor 3)

**HARD_FAIL:** ARM_DUAL_TRACE within +/-0.05 bits of ARM_BASELINE
              OR ARM_DUAL_TRACE fails to beat ARM_NAIVE_MULT
              (rank-1 Hebbian cap structural; pivot to refuse-aware-knowledge-store)

**CV mandatory:** dual_bpc_cv < 0.05 across 3 seeds (stability requirement)

**Reference baseline:**
  - fair_harness chain-grade: 7.3065 BPC (the HARD_PASS bar from prior chain-grade)
  - envelope cap: 7.295 BPC (sparse_bipolar_param_sweep best; max_lift=+0.44 bits)
  - unigram: 7.738 BPC

**P_deflated:** 0.42 (brain-existence-proof P~0.60 deflated 0.18 for novel substrate-synthesis)

---

## Contingency tree (per handoff)

- HARD_PASS -> Anchor 2: substrate_dual_trace_scaling_v1 (N=16384 N_TRAIN=1M; scale test)
- MIDDLE_BAND -> Anchor 3: substrate_dual_trace_ablation_v1 (E_pos_only vs E_neg_only vs both)
- HARD_FAIL -> Anchor 4: substrate_encoder_replacement_diagnostic_v1 (encoder bottleneck test)

---

## Timeout estimate

**Smoke reference (ARM_BASELINE):** estimated ~45s at N=512 N_TRAIN=2000 on laptop CPU
**Scale ratio:** N=512->8192 (16x), N_TRAIN=2000->100000 (50x), seeds=1->3
**Scaling exp:** 1.5 (vector ops; outer product accumulation with chunk-wise trace)
**Formula:**
  timeout_s = ceil(1.5 * smoke_wall_s * (8192/512)^1.5 * (100000/2000) * (3/1))
  = ceil(1.5 * 45 * 16^1.5 * 50 * 3)  [using smoke=45s estimate]
  = ceil(1.5 * 45 * 64 * 50 * 3)
  = ceil(648000) -> exceeds 14400s (4 hours)

**Override decision:** dual-trace trace-matrix operations (dim x dim E_pos, E_neg each)
  are SUBSTANTIALLY cheaper than naive calculation suggests because:
  a) GPU parallelism: outer products are batched matmul on GPU (not per-step CPU loops)
  b) INGEST_CHUNK=4096: only ~25 chunks per 100k tokens (not 100k individual steps)
  c) Prior 3-axis cell ran ~35-45min on GPU at N=8192 N_TRAIN=100k 3 seeds
  d) Dual-trace adds TWO extra dim*dim matrices in GPU memory vs one-trace; GPU can hold
     both: 2 * 8192^2 * 4 bytes = 537MB << 8GB GPU memory

**Actual timeout:** 5400s (90min) -- matching the 3-axis cell wall time with 50% buffer.
  This is the authoritative estimate; the formula over-estimates because it uses laptop
  CPU scaling, not GPU scaling. Post-smoke, if actual smoke_wall_s differs significantly,
  the timeout may be adjusted via --rerun-as before re-dispatch.

---

## No _n suffix note (PROT-018)

Anchor name lacks _n suffix. Production N = 8192 (PRODUCTION_N constant in script).
Rationale: matching fair_harness baseline config for fair comparison. N is fixed, not swept.

---

## Dependency verification (pre-dispatch checklist)

- [x] text8 corpus at data/text8_cache/text8.txt: checked on remote via SSH
- [x] gensim word2vec cache at data/gensim_cache_v2/: available on remote (used by 3-axis cell)
- [x] experiments/_seed_checkpoint.py: exists, API verified
- [x] tools/gensim_load_helper.py: exists (used by 3-axis cell; same import chain)
- [x] No other external dependencies beyond numpy + torch + standard library

---

## Cites

- Brzosko, Zannone, Schultz, Clopath, Paulsen (2017). "Sequential neuromodulation of Hebbian
  plasticity offers mechanism for effective reward-based navigation." eLife 27756.
- Huertas, Schwettmann, Shouval (2016). "The Role of Multiple Neuromodulators in Reinforcement
  Learning That Is Based on Competition between Eligibility Traces." PMC5156839.
- Fremaux, Gerstner (2016). "Neuromodulated STDP, and Theory of Three-Factor Learning Rules."
  Front Neural Circuits.
- Marder, Bucher (2007). "Understanding circuit dynamics using the stomatogastric nervous system."
  Annu Rev Physiol. [GPCR convergence caveat]
- notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md
- notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md
- data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json (envelope cap reference)
