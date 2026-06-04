# Prereg: substrate_friston_fep_trigram_cell_v1_n4096

## Anchor
substrate_friston_fep_trigram_cell_v1_n4096

## Routing
notes/change_request_bundle_b_add_friston_fep_trigram_cell_2026-06-04.md. Shipped as SEPARATE addendum
(Bundle B already queued when change-request landed -> change-request-protocol "in flight" case). Owned GPU, $0.

## Scientific question
Does Friston FEP (precision-weighted cf-RPE: eps=Nxt-W*ctx, Pi=1/running-var(eps), dW=(Pi*eps)^T ctx) beat
K=1 Hebbian at K=3 trigram, even though it HARD_FAILed at K=2 bigram in Bundle A? trigram V=70 wikitext char,
N=4096, roll-binding 2-char context, 3 seeds. 2 cells: baseline_k1 (symmetric Hebbian) vs friston_fep.

## Pre-registered bands (BPC nats)
HARD-PASS: FEP < baseline - 0.50 nats AND 3/3 seeds (FEP activates at K=3).
MIDDLE: improvement 0.20-0.50 nats. HARD-FAIL: FEP >= baseline (implicit-subsumption confirmed; FEP redundant).

## Formula self-tests (PROT-022)
1. roll-binding order-sensitive. 2. cf-RPE shrinks error. 3. Pi positive+finite. 4. uniform=ln(V). [PASS]

## Smoke gate
Smoke PASSED on remote GPU (N=256, 2 seeds): both cells run; FEP worse than baseline (preview HARD_FAIL ->
implicit-subsumption, consistent with Bundle A bigram HF). Full N=4096 is the registered test.

## PROT-018 / 019 / 021
_n4096 -> N=4096. timeout floor 14400s. 3 seeds.

## Queue
overnight_queue (GPU).
