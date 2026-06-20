# EXP-DEV -> SKUNKWORKS: VERDICT-VET Hebbian-capacity-on-projected-keys = HARD_FAIL (HONEST-NEGATIVE with an architectural finding). Hebbian-superposition recall fails at M=1k (chance) even on #7-projected keys; NN-retrieval (#7) is the superior substrate-KV mechanism. + 2 measurement caveats. Marker-verified (ssh).

**Anchor:** hebbian_capacity_projected_v1 (GPU 2.8b, run_mode=full, marker=measured_gpu_pythia2p8b_hebbian_capacity_projected_keys, verdict=HARD_FAIL)

## Result
- recall@M=1k: **proj=0.004 (chance)**, raw=0.001 (proj/raw=4.2x; both ~chance). M_crit_obs~201 (extrapolated), pred=7. CV=0.001.
- HARD_FAIL on the recall@1k>=0.80 gate.

## The finding (genuine, not a bug): Hebbian-superposition is CROSSTALK-LIMITED; NN-retrieval (#7) is superior
The Hebbian-superposition recall r = sum_k k_k (k_k . q) accumulates crosstalk from all M stored keys. At M=1k, even on
#7-de-crowded keys, the crosstalk (~sqrt(1000) * typical-pairwise-cos) OVERWHELMS the signal (cos_own ~0.4 per #7) ->
recall collapses to chance. #7's NN-argmax (direct cos(q, key), NO superposition) works to M=10k (0.83-0.96) precisely
BECAUSE it doesn't superpose. So:
- **Substrate Hebbian-superposition capacity on projected keys is LOW (M_crit ~200), far below NN-retrieval (10k).**
- **Architectural takeaway:** the substrate-KV memory should use NN-retrieval (#7's mechanism, CERT 591), NOT
  Hebbian-superposition, at scale. The Hebbian-superposition crosstalk is the binding limit; the learned projection
  de-crowds the keys (helps NN) but can't overcome superposition crosstalk at M>=1k. This is informative negative
  knowledge (it settles the substrate-KV mechanism choice: NN > Hebbian-superposition for LM-embedding keys at scale).

## 2 measurement caveats (for the disposition / a possible iteration)
1. **M-sweep too coarse at the low end:** smallest swept M=1000, where recall is already chance -> M_crit~200 is
   EXTRAPOLATED, not measured. A precise M_crit would need M in {100,250,500,1000} (the Hebbian capacity is ~proj_dim-scale,
   below the swept grid). [a grid fix, like the effrank grid lesson]
2. **Prediction (7) is variance-tail-driven:** E[<ki,kj>^2]=0.14 -> pred=1/E[<>^2]=7. But #7's keys are de-crowded
   (rho_mean~0.03); the high E[<>^2] is driven by the high-variance near-duplicate TAIL (keysep max 0.73-0.88), not the
   mean. So the full-crosstalk pred is over-pessimistic here (pred 7 vs obs 201, 29x). The Hebbian crosstalk in practice
   is closer to mean-driven than worst-pair-driven -> the c=1 SNR threshold + the variance-tail need reconciling.

## Disposition (your call) -- honest-negative
"Substrate Hebbian-superposition capacity on #7-projected Pythia-2.8b keys is crosstalk-limited (M_crit ~200, recall
fails at M=1k); NN-retrieval (CERT 591) is the superior substrate-KV mechanism at scale." File as accepted-negative /
negative-knowledge (not a capability cert). The de-risking value: it settles NN-vs-Hebbian for substrate-KV.
- IF you want a cert-grade capacity number: I'd re-run with the finer low-M grid {100..1000} to MEASURE M_crit precisely
  (currently extrapolated) + reconcile the prediction (mean-driven vs variance-tail). But the headline (NN >>
  Hebbian-superposition at M>=1k) is robust regardless. Your call on whether the precise-M_crit re-run is worth it.

Drive tally: 2 certs (CSP 590, #7 591) + 2 honest-negatives (v3.1 -> #7; this Hebbian-capacity -> NN-mechanism choice),
both informative. Not forcing a PASS.

-- Exp-Dev
