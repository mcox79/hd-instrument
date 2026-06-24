# exp_dev hand-off — research: dual-trace mechanism elucidation (2x DEPTH on HARD_PASS lever-isolation)

Filed-by: research sub-agent (Opus synthesis over 4 parallel Sonnet WebSearches)
Date: 2026-06-23
Trigger: notes/research_dual_trace_mechanism_elucidation_2026-06-23.md
Urgency: HIGH — the just-landed `substrate_dual_trace_sequential_neuromod_LM_v1` HARD_PASS (bpc 7.221 vs 7.738 unigram; +0.52 over baseline) confounds FOUR mechanisms simultaneously; substrate-product strategy depends on which is the lever (anti-Hebbian subtraction generalizes broadly; joint conspiracy locks in a single composite primitive).

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

### Anchor 1: substrate_dual_trace_axis_ablation_LM_v1 (PRIMARY — cheap-decisive lever-isolation)

Anchor pointer: research note "Cheap decisive test" section + "Falsifiable predictions" A-E
Substrate-product reading: 4-arm ablation cell that cleanly factors the 5-way confound between DUAL_TRACE and NAIVE_MULT into 3 testable axes (sign-heterogeneity, target-heterogeneity, timescale-heterogeneity). Modulator-orthogonality is structurally redundant once these are tested. Outcome cleanly discriminates ALL FIVE hypotheses (anti-Hebbian / multi-timescale / cardinality / modulator-axes / joint-conspiracy) with ONE cell.
Tier hint: GPU remote, ~25-30min wall time (matches reference cell 507s x 4/3 arms x some overhead). 4 arms x 3 seeds x text8 N_TRAIN=100k N_DIM=8192.
Why-now: Until the load-bearing axis is identified, every downstream cell will either (a) over-specify the dual-trace package as the irreducible unit, missing the broader pattern; or (b) under-specify by dropping the load-bearing axis. Single cheap-decisive ablation prevents both errors.

Pre-reg bands (per research note's lever-attribution table; cell-author may refine per harness conventions):
  ARM_DT_BASELINE bpc must reproduce 7.221 ± 0.02 (sanity)
  ARM_DT_SAME_SIGN >= 7.55 AND ARM_DT_SAME_TARGET >= 7.50 AND ARM_DT_SAME_TAU <= 7.30 -> Anti-Hebbian-against-prediction is the lever (Prediction A confirmed)
  ARM_DT_SAME_TAU >= 7.55 AND ARM_DT_SAME_SIGN <= 7.30 -> Timescale separation is the lever (Prediction B confirmed)
  All three ablation arms in [7.40, 7.55] -> Joint conspiracy / irreducible composite (Prediction E)
  Any single arm fully recovers (bpc <= 7.25) -> that axis was load-free; simpler mechanism isolated
  cv across 3 seeds <= 0.05 mandatory; per-arm metrics via tools/peek_arm_metrics.py per Fix #28
  fair-harness bpc baseline 7.3065 + unigram 7.738 as control rails

### Anchor 2: substrate_anti_hebbian_subtract_generalization_v1 (CONTINGENT on Anchor 1 confirming Prediction A)

Anchor pointer: research note "Substrate-product implications" / "If anti-Hebbian-subtraction is confirmed"
Substrate-product reading: If Anchor 1 confirms the anti-Hebbian-of-prediction term is load-bearing, test whether this pattern generalizes BEYOND the dual-trace framing. Strip away dopa/ACh modulators (use constant scalars) and test minimal recipe: W += γ_pos * outer(Δ,src) − γ_neg * EMA_slow(outer(pred,src)). If lift survives, the pattern is a single-line drop-in for any plasticity cell (substrate-as-KG, continual-learning, multi-hop chain). If lift dies without the modulators, then the gating IS load-bearing (changes substrate-product story).
Tier hint: GPU remote, ~20-30min wall time. 2-3 arms x 3 seeds.
Why-now: Anti-Hebbian decorrelation is a powerful substrate-product primitive if it generalizes; tested at the same scale as Anchor 1.

Pre-reg bands:
  HARD-PASS (generalizes): minimal-recipe arm bpc <= 7.30 (within 0.08 of full dual-trace)
  MIDDLE-BAND: 7.30 < bpc < 7.50 (partial generalization; modulators contribute but not load-bearing)
  HARD-FAIL: bpc >= 7.55 (modulator gating IS load-bearing; pattern does not generalize)

### Anchor 3: substrate_dual_trace_compose_with_chain_grade_primitives_v1 (CONTINGENT on Anchor 1 HARD_PASS or MIDDLE_BAND)

Anchor pointer: research note "Composition with already-chain-grade primitives" section
Substrate-product reading: Once the load-bearing axis is identified, test whether composing dual-trace with already-chain-grade primitives (lock-in CERT 583 carriers as natural tau-pair; sparse-bipolar CERT 592 codebook for sparse outer products; HRR for target-bind) gives multiplicative lift OR is redundant (already-captured by dual-trace). Single-cell test of one composition (suggest: dual-trace + sparse-bipolar codebook routing for E_pos/E_neg outer products).
Tier hint: GPU remote, ~45-60min wall time. 2-3 arms.
Why-now: Substrate-product depends on whether dual-trace stacks with existing chain-grade primitives or is parallel to them.

Pre-reg bands:
  HARD-PASS (multiplicative composition): dual-trace + sparse-bipolar bpc <= 7.10 (additional +0.12 over dual-trace alone)
  MIDDLE-BAND: bpc in [7.15, 7.25] (small additive contribution)
  HARD-FAIL: bpc >= 7.25 (composition captures no additional structure; primitives are redundant)

### Anchor 4: substrate_dual_trace_scaling_v1 (CONTINGENT on any Anchor 1 outcome other than HARD_FAIL across all arms)

Anchor pointer: research note "Substrate-product implications" — production-relevance gate
Substrate-product reading: Scale dual-trace from N_DIM=8192 N_TRAIN=100k to N_DIM=16384 N_TRAIN=1M with the identified-load-bearing axis only (cheaper) or full package. Test whether lift grows, flattens, or halves at scale — the same test the original predictive note's Anchor 2 specified, now anchored to the lever-isolated mechanism.
Tier hint: GPU remote, ~2-4 hours wall time. 2-3 arms (current-best vs scaled).
Why-now: Production-relevance gate. If lift halves at scale (like single-modulator sweep did), substrate-as-LM is still capped despite the elucidation.

Pre-reg bands:
  HARD-PASS: scaled bpc lift >= +0.40 vs N8192/T100k dual-trace baseline (lift GROWS with scale)
  MIDDLE-BAND: lift stays approximately flat ± 0.10 bits across scaling
  HARD-FAIL: lift halves (envelope reappears at scale; production-relevant story dies)

---

## Context pointers (file paths only, exp_dev reads them)

- d:/AI/hd-instrument/notes/research_dual_trace_mechanism_elucidation_2026-06-23.md  (this elucidation drill; load-bearing)
- d:/AI/hd-instrument/notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md  (predictive note)
- d:/AI/hd-instrument/data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json  (HARD_PASS reference; ARM_DT_BASELINE must reproduce)
- d:/AI/hd-instrument/data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json  (READOUT_DEGENERATE reference; confirms NAIVE_MULT collapse)
- d:/AI/hd-instrument/experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py  (cell source; commit 7f450ce7; lines 454-541 = build_W_dual_trace; lines 395-450 = build_W_naive_mult; lines 355-393 = build_W_baseline)
- d:/AI/hd-instrument/notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md  (broader rank-1 escape framework)
- d:/AI/hd-instrument/experiments/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512.py  (substrate-mine atom: "heterogeneity is the lever" — N=512 chain-grade)
- d:/AI/hd-instrument/tools/peek_arm_metrics.py  (Fix #28 per-arm metric reader — MANDATORY before any tiering claim)

---

## Contract

- exp_dev authors smoke test on CPU first (5-10min), then dispatches Anchor 1 to GPU.
- After Anchor 1 lands, Skunkworks tiers per Fix #28 (read per-arm metrics, not verdict_msg).
- Director routes to Anchor 2, 3, or 4 based on Anchor 1 outcome per the predictions table in research note.
- All cells must commit on origin/main BEFORE remote dispatch per [[feedback-commit-prereg-notes-before-remote-dispatch]].
- Per-arm metric verification via tools/peek_arm_metrics.py per Fix #28 — DO NOT propagate cross-arm narratives from verdict_msg alone.

---

## Autonomy declaration

exp_dev decides: cell file name; smoke test variant; SEEDS list (default {7,17,23} per prior cells); precise harness conventions; encoder choice (default word2vec per chain-grade precedent in prior cell); torch device routing (GPU per Fix #24 cell-author smoke requirement); whether to add Anchor 2 minimal-recipe arm to Anchor 1 (5-arm cell would save a follow-up dispatch but increases per-cell wall time — exp_dev's call).

Skunkworks decides: classification post-landing.

Director decides: contingent next-anchor dispatch order.

Research is done with the elucidation drill until next requested.
