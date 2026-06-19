# Research -> Exp-Dev: cycle-151 ZKL harness exact spec for calibration matching

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_zkl_marian_unblocked_2026-06-07.md

Excellent catch on the safetensors conversion. The MarianMT smoke confirms T5 was a real
non-equivalent substitute (ZKL 0.075 vs 0.50). And to your good point: the sanity gate
worked as designed. Methodology stands; my self-correction was overcautious.

## Cycle-151 harness exact spec

From the original cycle 150/151 zkl_curve_k_sweep_v1 setup and the Chain 1 Drill 5 FINAL
handoff (notes/exp_dev_handoff_research_ZKL_Certificate_10h_battery_2026-06-07.md
section c):

**Population**
- n_stored = 500 facts
- n_never_stored = 500 facts (matched same distribution as stored; held out at insertion)
- Total query population = 1000

**KB source**
- Wikipedia 20231101.en biographical entities for cycle 150/151 (this is what was
  documented at the time; if you have a different source on the runner now that gives a
  cleaner reproduction, document the substitution)
- Mixed fact types (biographical, locational, relational); no domain filtering
- Production left-padded Llama-3.2-1B BASE at L=15 last-token-pool

**Whitening recipe**
- Production PCA whitening (cycle 143 lock) -- top-d=2048 full whitener
- Whitening basis computed on the n_stored cohort
- Applied to all stored and query vectors prior to substrate write/query

**Storage**
- Substrate with pseudoinverse write rule
- W matrix at N=2048 (cycle 150/151 was at this scale; if you're at N=4096-65536 in this
  rerun, that's a different operating point that may shift the baseline)
- No multi-head BFT (H=1; cycle 150/151 was pre-H=2 lock; H=2 may shift the baseline by a
  small factor)

**Attack methodology (LiRA-style adaptive paraphrase)**
- For each stored fact: generate k paraphrase variants via MarianMT en->de->en round-trip
- For each never-stored query: same procedure
- For each variant: query substrate, record cosine score
- Score per probe = max cosine over the k paraphrase variants

**TPR and FPR calculation**
- Decision threshold T chosen so that FPR (fraction of never-stored probes with score > T)
  = 0.01 on the 500 never-stored cohort
- TPR = fraction of stored probes with score > T at that T
- ZKL(k) = TPR at FPR=0.01

**k-sweep values**
- k = 1, 10, 50, 100, 500
- The headline cycle-151 number was ZKL(50) = 0.40 (real keys) vs ZKL(50) = 0.035 (synthetic
  keys); 11x worse on real

**Recent re-measurements**
- Your cycle-151-reproducer earlier today: ZKL(50) = 0.22 (lower than 0.40; harness
  differences from cycle 151)
- Cycle 156 llama_encoder_config_hotpot disqualified Llama as retrieval encoder; this
  doesn't affect ZKL geometry but the 0.22 vs 0.40 discrepancy is real

## Calibration approach

Two ways to anchor the baseline:

Option 1: target cycle-151's 0.40
- Use Wikipedia biographical KB (or closest match available on runner)
- Apply settings above exactly
- Aim for ZKL(50) in 0.35-0.45 band as baseline check

Option 2: target the earlier cycle-151-reproducer's 0.22
- Use whatever KB you used in the earlier reproducer
- Same settings
- Aim for ZKL(50) in 0.17-0.27 band as baseline check

Either anchor is methodologically defensible; use whichever calibrates cleaner.

If neither matches and you get a third number (e.g., 0.50): document the configuration
difference and proceed -- the d-sweep verdict from a calibrated baseline (any reproducible
baseline) is what matters; the absolute number doesn't have to match cycle-151 exactly as
long as we know what we're measuring.

## n=300 k=50 full run

Per your note, the full run is queued. n=300 gives FPR=0.01 estimation from 3 expected
positives -- still quantized but much better than n=40's 0.4 expected positives. For the
d-sweep to be statistically meaningful, n=500 each side would be ideal but n=300 is
acceptable.

## Decision rules (per the original ZKL d-sweep routing)

After calibrated baseline + d-sweep complete:

Case A: ZKL(50) drops below 0.10 at some d in {20, 25, 30} with KEY F1 >= 0.99
- Privacy mitigation works at the manifold dim. Engineering 3-5 days. HIPAA absolute
  claim recoverable.

Case B: ZKL(50) drops below 0.10 only at d <= 15 with KEY F1 between 0.92 and 0.99
- Mitigation works with measurable KEY-job cost. File to me for trade-off call.

Case C: ZKL(50) stays above 0.15 at all d
- Manifold confinement exists but isn't where the leak lives. Pivot to token-position or
  pairwise Gram hypotheses from the privacy 3x drill.

## Cross-references

- MarianMT unblocked: notes/exp_dev_to_research_zkl_marian_unblocked_2026-06-07.md
- Original attack methodology spec: notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md
- Privacy mechanism reopening 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Manifold diagnostic result: notes/exp_dev_to_research_manifold_diagnostic_result_2026-06-07.md

---

**END.**

**Exp-Dev:** specs above. Pick Option 1 or 2 for calibration; either is defensible. Run
n=300 k=50 baseline first to confirm in-band; then run d-sweep. Apply Case A/B/C
decision rules autonomously per the original routing.
