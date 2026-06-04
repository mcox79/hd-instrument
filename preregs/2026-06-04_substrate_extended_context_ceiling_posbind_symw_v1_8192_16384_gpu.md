# Prereg: substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu
## Anchor
substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu
## Routing
notes/routing_bundle_g_extended_context_ceiling_test_2026-06-04.md (dependency-free subset; V=4000 subword
cell dropped; wikitext char serves as real task). GPU, $0.
## Scientific question
TRUE extended-context ceiling K* with position-binding (roll) + symmetric Hebbian at substrate-class N.
7 cells: K {8,12,16,24} @ V70/N8192; K16 @ N16384; K16 @ V512-synthetic/N8192; K8 @ V70/N16384. 3 seeds.
gap = uniform_nats - val_nats.
## Pre-registered bands
per-cell HP gap>0.8 (3/3); MID gap>0.3; HF gap<=0.3. AGGREGATE: K* = max K (V70/N8192) with HP;
HARD-PASS K*>=12; MIDDLE K*=8; HARD-FAIL no K>=8 HP.
## Formula self-tests (PROT-022)
roll-binding order-sensitive / K-context recall>0.5 / uniform=ln(V) / codebook unit-norm. [PASS]
## Smoke gate
Smoke PASSED on remote GPU (N=256, 2 seeds): cells run; gaps 0.73-1.39. NOTE: wikitext loader hits an
HfUriError post-datasets-install and falls back to local cache (real data; gaps reasonable); synthetic V512
cell unaffected. Full N=8192/16384 is the registered ceiling test.
## PROT-018/021
NO _nN suffix (N+K swept). per-seed partials. timeout 14400s.
## Queue
overnight_queue (GPU; N up to 16384 NxN Hebbian = genuine GPU load).
