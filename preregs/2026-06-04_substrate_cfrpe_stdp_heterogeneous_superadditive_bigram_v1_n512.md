# Prereg: substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512
## Anchor
substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512
## Routing
notes/routing_cfrpe_stdp_superadditive_test_2026-06-04.md. Tests heterogeneous-axis (task cf-RPE + temporal
STDP) superadditivity, where cf-RPE+sparse only added (shared axis). GPU, $0. 4 arms x 5 seeds, bigram V=512 N=512.
## Pre-registered bands (BPC nats; gap=uniform-val)
HARD-PASS (superadditive): C1 combined gap>0.70 nats AND 4/5 seeds. MIDDLE: C1 in [max(cf,stdp),0.70].
HARD-FAIL: C1<=max(cf,stdp) (still shared-axis/additive).
## Formula self-tests (PROT-022)
STDP antisym W+W^T=0 / cf-RPE shrinks / zipf cond-ent<log(V) / uniform=ln(V). [PASS]
## Smoke gate
Smoke PASSED (N=256,V=128): combined(2.87)>cfrpe(2.78)>stdp(2.53) -- leaning superadditive; full V=512 decides.
## PROT-018/021
_n512 -> N=512. 5 seeds. timeout 14400s.
## Queue
overnight_queue (GPU).
