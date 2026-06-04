# Prereg: substrate_hierarchical_5corpus_meta_v1_n2048_gpu
## Anchor
substrate_hierarchical_5corpus_meta_v1_n2048_gpu
## Routing
notes/routing_substrate_hierarchical_5_corpus_meta_test_2026-06-04.md (user "train many small models, aggregate
via meta substrate"). 5 synthetic Zipf domains (clean, no data dependency). Owned GPU, $0.
## Scientific question
Can a substrate aggregate 5 domain-specialist sub-LMs (via domain-binding ctx*dkey_d into one shared W_agg)
to predict across ALL domains better than cross-domain, preserving specialist skill + per-domain deletion?
4 cells x 3 seeds, N=2048, V=512, cf-RPE. H1 own / H2 cross / H3 aggregate / H4 deletion-retention.
## Pre-registered bands (BPC nats)
HARD-PASS: H3<H2 AND H3<=H1*1.25 (>=80% specialist) AND H4 retention>=0.95 AND 3/3 seeds.
MIDDLE: H3<H2 but H3>H1*1.25, OR retention [0.70,0.95). HARD-FAIL: H3>=H2 OR retention<0.50.
## Formula self-tests (PROT-022)
domain keys orthogonal / bipolar bind invertible / cf-RPE shrinks / distinct domains / uniform=ln(V). [PASS]
## Smoke gate
Smoke PASSED on remote GPU (N=256,V=128,2 seeds): HARD_PASS -- H1=2.09 H3=2.35 (lossless-ish) H2=4.83 (cross
fails) retention=1.03. Strong positive. Full N=2048 is the registered test.
## PROT-018 / 021
_n2048 -> N=2048. per-seed partials. timeout 14400s.
## Queue
overnight_queue (GPU).
