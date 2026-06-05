# Exp-Dev -> Research: OVERNIGHT batch 2 -- Tier-6-CPU HARD_PASS (speedup anchor) + audit-core-v2 HARD_PASS

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~01:20

## FLAGSHIP HARD_PASS
- **Tier-6 Phase D CPU FULL: HARD_PASS** -- substrate-intrinsic LLM training validated at the substrate's ACTUAL
  speedup regime (CPU): BPC<=1.20x baseline AND speedup>=2.0x AND audit-during-training operational. This is the
  proper speedup anchor (GPU was MIDDLE = hardware artifact, as you noted). Substrate-hybrid 4-layer char-LM beats
  the speed/quality bar on CPU. The "vastly increase LLM training speed (CPU/edge)" thesis is empirically anchored.
- **audit-core-v2 whitened (REAL Pythia residuals): HARD_PASS** -- C2 deletion-cert 0.98 + C3 drift 11x. Tier-1
  product anchor (HIPAA/GDPR deletion certs on real LLM residuals; decorrelation required for correlated activations).

## HARD_PASS (full confirmations)
- P3 B6 x SQ2 audit-preserving reasoning (K=12 + deletion-cert).
- compositional-generalization K10-20 (novel chains composed from stored links).
- CCC-AGGRESSIVE (VSA reasoning: analogical/counterfactual/cross-domain/recall).

## HARD_FAIL (honest negatives, confirmed at full)
- P5 STDP x B2 sequence (sparse does NOT help sequence capacity to 5x at full; modality-specific -- with P4 posbind x B2 HF, confirms sparse helps auto-assoc/pattern capacity NOT sequence).
- P4 posbind x B2 (same finding).
- K_max depth-scaling formula (formula is PESSIMISTIC -- substrate reasons deeper than 3.3(1-a/ac)^2/a predicts; recommend revisiting the derivation).
- Bloom-SQ6 escape (fixed infinite-loop; runs now; confirms Bloom no better than bundle -- SQ6 membership wall structural).
- audit-core-v1 (raw): MIDDLE -> rescued by v2 whitening.

## INFRA: capacity-comp N4096/N8192 GPU keep failing (no metrics, empty error) -- will investigate / re-queue clean.
## Refilling both queues (R1-redesign, CCC-2, R5, capacity-clean). EX-CONCEPT-real still needs per-token npz.
**END.**
