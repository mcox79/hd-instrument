# Grounding-arc synthesis (CORRECTED, filesystem-verified) — 2026-07-26

**Why this exists:** the KB/notes-based look-back (a723f0cb) MISSED the on-disk grounding arc. USER pushed twice to actually look. This is the corrected picture, read directly off `experiments/exp_grounding_*` + `data/exp_grounding_*/metrics.json` (39 full-run cells) + `data/grounding_testbed/`.

## The brain-grounded-norms testbed (July 10, real, ran)
`data/grounding_testbed/`: Lancaster Sensorimotor Norms (39,707 words × 11 experiential dims), Brysbaert Concreteness (40k), Warriner VAD (13,915), Kuperman AoA (51k), CSKG (6M edges). Human brain-grounded RATINGS (Barsalou), NOT distributional embeddings. Provenance files present. These are the legitimate GloVe-free grounding sources.

## What the 39-cell grounding arc actually CONCLUDED (3 findings)

**1. Brain-grounded meaning is REAL + validated — and NOT the missing piece.**
- `exp_grounding_measured_attribute_concreteness_v1` = **HARD_PASS_GROUNDING_REAL** (F_A 0.509 -> A+B 0.568 gap +0.059; scramble collapses -0.539; fairness passes).
- `exp_grounding_multiattribute_fusion_v1` = MIDDLE (Lancaster sensorimotor+concreteness+AoA compound, fused_gap +0.079, scramble collapses).
- `exp_grounding_improves_relation_inference_mammal_v1` = **MIDDLE_BAND_GROUNDING_REDUNDANT_FOR_REASONING** (fused gain over relational only +0.011 n.s.; relational structure already carries it). => "we lack brain-grounded meaning" is the WRONG diagnosis.

**2. The recurring WALL = CHAINING / TRANSFER / GENERALIZATION (same wall the tie-work hits).**
- `exp_grounding_rung2_loop_closer_v1` = **HARD_FAIL_GROUNDING_DOESNT_TRANSFER** (grounded reach 0.057 < ungrounded 0.085; lift NEGATIVE).
- `exp_grounding_learned_sr_heldout_reasoning_v1` = **HARD_FAIL_CG_MEMORIZED_SEARCH** (learned @2=0.115 vs known-target 0.462; ratio 0.248 = memorizes, collapses held-out).
- `density_payoff` HARD_FAIL_DENSITY_ALONE; `percolation` HARD_FAIL_GROUNDING_NOT_STRUCTURAL; `selfplay` HARD_FAIL_REAL_BOUND; spanning-core SPAN_FAIL_MECHANISM (decoder bottleneck). Abstract/operation meaning = language-convention-carried (metaphor-bridge HARD_FAIL, Pecher-Zeelenberg).

**3. TWO brain-aligned mechanisms PARTIALLY crack chaining (prior HARD_PASS) — NEVER wired to ARC.**
- `exp_grounding_gated_fusion_relation_inference_mammal_v1` = **HARD_PASS**: learned per-channel gating (lambda*) of grounded channels recovers grounding on HELD-OUT relations 0.365 -> 0.662 (+0.297).
- `exp_grounding_multihop_sr_reachability_routing_v1` = **HARD_PASS_CG_SR_REACHABILITY**: Successor-Representation routing (hippocampal SR, Stachenfeld/Dayan) enables multi-hop chaining where greedy fails: SR_SEEDED @2=0.434/@3=0.416 vs AUTONOMOUS_GREEDY @2=0.181 (delta +0.253).
- CAVEAT (learned from this same arc): both tested only on CLEAN TOY domain (mammal allometry); the recurring pattern is toy-wins FAIL TO TRANSFER to real data.

## THE REFRAME (corrected direction)
Grounding-representation is solved-enough (validated brain-grounded norms exist; grounding often redundant). **The wall is the CHAINING/generalization mechanism.** The brain-aligned candidates already half-cracked = Successor-Representation routing + gated fusion, GloVe-free, NEVER applied to ARC. Informed next step = wire SR-routing / gated-fusion to the ARC tie/reasoning problem over the relational graph. Honest odds modest (toy-transfer has repeatedly failed). AWAITING USER steer before dispatch (Director ran ahead of prior work twice; not a third).

## Discipline lesson
KB/substrate_query look-backs MISS filesystem work (cells self-acquire data, reference files not concepts, so cosine-KB search returns nothing). For "what have we tried" questions: enumerate `experiments/*.py` + `data/*/metrics.json` verdicts DIRECTLY, not just the KB.
