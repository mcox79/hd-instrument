# Exp-Dev -> Research: OVERNIGHT batch 1 verdicts

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-04 ~23:35

## FLAGSHIP
- **Tier-6 Phase D FULL (GPU): MIDDLE_BAND** -- substrate-hybrid 4-layer LLM training: BPC within band, but
  GPU speedup did NOT clear 2.0x (GPU parallelizes the baseline's backprop cheaply, so the no-backprop advantage
  is modest on GPU). NOTE: the speedup claim is stronger on CPU (smoke showed 1.98x); the Tier-6-CPU full run is
  still pending -- that is the better speedup test. Substrate-hybrid LLM training is BPC-viable; the training-SPEED
  advantage is hardware-dependent (favors CPU / backprop-expensive regimes). Tier-4 (substrate-attention IN
  Pythia-160M) HARD_PASS already established the substrate-attention-in-real-LLM leg.

## HARD_PASS
- substrate_sq2_x_cfrpe_composition (P1): cf-RPE PRESERVES 12-hop reasoning.
- substrate_sq2_x_hierarchical_reasoning (P2): ensemble MULTIPLIES reasoning depth (24-hop where single collapses).
- substrate_stage_a_bio_b36_ratio_sweep: B3b+B6 SUPERADDITIVE across all mix ratios (0.3/0.5/0.7).
- substrate_sq5_matrixfree_biological_scale: sparse capacity >=10x dense at N=100k (matrix-free; biological scale).

## MIDDLE_BAND
- substrate_sq2_multihop_load_sweep: reasoning depth 12 holds to ~1.5x alpha_c, collapses at 2x.
- substrate_efficiency_composition_b3axb3b: B3a x B3b ~16x write reduction (sub-multiplicative; gates overlap).
- substrate_sq3_structured_image_retrieval: correlated-image retrieval reduced-but-usable.

## HARD_FAIL (confirmed negatives; pressure-tested)
- substrate_stage_a_bio_b5_bounded_weights: replay-consolidation FUNDAMENTAL negative (palimpsest + bounded + cf-RPE-replay all HF).
- substrate_sq6_graph_adjacency_v2_cleanup: cleanup does NOT improve edge-membership (bundle SNR-limited; structural).

## STILL RUNNING (next batch): Tier-6-CPU, capacity-4096/8192, CCC-AGGRESSIVE full, compositional-generalization, P5-stdp-b2, P3, P4.
## Pythia npz not yet present (CCC-1-v2 + EX-CONCEPT-real + audit-core gated on it).
**END.**
