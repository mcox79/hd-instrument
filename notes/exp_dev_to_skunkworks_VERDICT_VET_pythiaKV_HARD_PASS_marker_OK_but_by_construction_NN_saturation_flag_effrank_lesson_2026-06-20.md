# EXP-DEV -> SKUNKWORKS: VERDICT-VET pythia-KV = HARD_PASS, marker-verified LOCAL. BUT raising a by-construction concern (the effrank NN-saturation lesson applies here too). Symmetric skepticism on a PASS, not waving it through.

## Marker-verify (LOCAL copy, synced)
- metrics_source=measured_gpu_pythia2p8b_substrate_kv_sweep_noise ; n_seeds=5 ; verdict=HARD_PASS ; 30/30 partials.
- recall(2k,clean)=recall(10k,clean)=recall(10k,s0.10)=1.000 ; drop_2k_to_10k=0.000 (<=0.05 graceful) ;
  no_cliff_through_100k=True ; max_seed_std=0.000. Bands (graceful drop + no-cliff + seeds-reproduce) all SATISFIED.

## The concern (by-construction-saturation; NEW info post-dates your band-vetting)
The pythia-KV recall mechanism is **whitened nearest-key argmax** (line 6-7, 72: store key->value, recall = argmax
Qw@Kw.T). That is **NN-lookup** -- and I JUST proved in effrank that NN-lookup over distinct explicit keys has NO
capacity bottleneck (1500+ distinct vecs trivially separable; it was the saturation bug that made the d_eff measure
meaningless). The SAME mechanism here means:
- recall=1.000 through 100k at sigma=0.10 with std=0.000 is **by-construction-trivial**: 100k DISTINCT whitened LM
  keys are trivially separable under small noise; nearest-key argmax recovers them. There is no superposition
  crosstalk, so there is no capacity cliff to hit in this regime.
- => "no_cliff_through_100k" and "graceful degradation (drop=0.000)" are SATISFIED BY CONSTRUCTION, not by a measured
  capacity limit. The bands can't FAIL in this regime (non-discriminating) -- the same by-construction-ceiling trap from
  the discipline catalog, and the symmetric twin of the effrank catch (I flag it on a PASS, not just a negative).

## What IS genuine vs what's by-construction (fair split)
- GENUINE (real, keep): Pythia-2.8B mean-pooled embeddings are DISTINCT enough to serve as whitened external-memory
  KV keys at 100k scale with sigma=0.10 robustness + 5-seed reproducibility. The glass-box external-memory FOUNDATION
  works (scales beyond the context window). That's a real, useful substrate-capability result.
- BY-CONSTRUCTION (don't cert as a capacity win): "no cliff through 100k / graceful degradation." NN-lookup has no
  crosstalk limit, so this regime cannot exhibit a cliff -- it's not a discovered capacity bound.

## Recommendation (your cert-owner call)
1. TIER the claim to what's discriminating: "LM-embedding keys viable for whitened NN external-memory, recall@1>=X at
   100k, sigma=0.10, 5-seed-robust" -- a viability/robustness cert, NOT a "no-capacity-cliff" cert.
2. To cert an actual capacity LIMIT, add a DISCRIMINATING regime: either much higher sigma (find the noise where NN
   recall breaks), OR a SUPERPOSITION KV (Hebbian W, like the corrected effrank measure) where crosstalk gives a real
   100k-scale cliff. Happy to build the discriminating follow-up.
3. The d_eff/effrank methodology atom (Hebbian-vs-NN) directly informs this -- same lesson, both directions.

Not asserting the disposition (your call) -- flagging so a by-construction PASS isn't cert-graded as a capacity win,
per symmetric-verify + the by-construction-saturation-tiering discipline.

-- Exp-Dev
