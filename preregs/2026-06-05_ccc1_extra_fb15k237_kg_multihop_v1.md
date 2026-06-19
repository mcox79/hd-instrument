# Prereg: ccc1_extra_fb15k237_kg_multihop_v1
## Anchor
ccc1_extra_fb15k237_kg_multihop_v1
## Routing
CCC-1-EXTRA: substrate KG multi-hop on REAL FB15k-237 (VSA bind s*p->o cf-RPE; K-hop traversal via cleanup). CPU $0.
## Bands
HARD-PASS 1hop>=0.85 AND >=3x relbase AND 2hop>=0.5. MIDDLE 1hop>=0.6 OR 2hop>=0.3. HARD-FAIL else.
Smoke (M=600): 1hop=0.987 2hop=0.895 3hop=1.000 (relbase=0.36 inflated at small M -> 3x artifact -> MIDDLE; full M=5000 lower relbase -> likely HP).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
