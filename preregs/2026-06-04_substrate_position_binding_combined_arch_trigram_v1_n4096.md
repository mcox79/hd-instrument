# Prereg: substrate_position_binding_combined_arch_trigram_v1_n4096
## Anchor
substrate_position_binding_combined_arch_trigram_v1_n4096
## Routing
notes/routing_position_binding_combined_architecture_bundle_e_2026-06-04.md (Bundle E). UNGATED: Bundle B
(task_complexity_sweep) landed HARD_PASS -> the Bundle-B-conditional gate is satisfied. Owned GPU, $0.
## Scientific question
Does combining position-binding (roll-binding VSA) + asymmetric-W (STDP) and/or sparse coding enable
substrate-as-training at TRIGRAM (K=3), exceeding the K*~2.1 symmetric-Hebbian ceiling? 4 cells x 3 seeds,
N=4096, trigram V=70 wikitext: E1 posbind+Hebbian, E2 posbind+STDP, E3 posbind+sparse, E4 posbind+sparse+STDP.
## Pre-registered bands (per-cell; BPC nats)
HARD-PASS: gap>1.0 nat AND 3/3 seeds AND stable. MIDDLE: gap [0.3,1.0] or 2/3. HARD-FAIL: gap<0.3 or <1/3.
AGGREGATE: HP if any cell HP (combination enables trigram); HF if all 4 HF (substrate K=2 bound).
## Formula self-tests (PROT-022)
posbind order-sensitivity / single-trigram recall / STDP antisym / sparse support / uniform=ln(V). [PASS]
## Smoke gate
Smoke PASSED on remote GPU (N=256, 2 seeds): all 4 cells run; posbind order-sensitive; trigram recall OK.
## PROT-018 / 019 / 021
_n4096 -> N=4096. timeout floor 14400s. 3 seeds.
## Queue
overnight_queue (GPU).
