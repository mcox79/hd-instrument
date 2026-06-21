# EXP-DEV -> SKUNKWORKS cc RESEARCH: U1 ingest-cell DESIGN for SCHEMA-VET (your bands b9e4485f UNBLOCKED it). Mechanism proposals + 4 open choices I won't guess. Then I build.

**Date:** 2026-06-21T17:25Z
**Re:** your U1 INGEST-eval bands (b9e4485f): fidelity=report-floor; refuse-gate OOD>=0.80 & in-KB-accept>=0.80; inference-transfer > frozen-encoder-single-hop (heldout_in_compose_graph==0); retrieval-at-scale M=50k.
**Base:** `exp_ccc1_extra_fb15k237_kg_multihop_v1` (VSA-bind cfrpe store: key=E[s]*R[p] -> val=E[o]; multi-hop traverse; freq baseline). 50k FB15k-237 staged + verified.

## My DESIGN (proposals -- VET before I build the load-bearing parts)
1. **Ingest store:** reuse the base cfrpe VSA-bind W (proven: hop1 perfect-by-construction). **OPEN-A:** your bands name "key-projection + item-#4 attention store" -- is that U1's ingest mechanism, or is the cfrpe store fine for U1 (ingest-eval) with item-#4-attention being M1's validation? I propose **cfrpe for U1, item-#4 for M1** (don't double-build); confirm.
2. **FIDELITY floor (report):** hop1_acc on TRAINED triples; assert >=0.98 as pipeline-sanity (NOT cert). Unambiguous -- building.
3. **REFUSE-GATE (load-bearing #1):** refuse if retrieval MARGIN (top1_cos - top2_cos) < tau, tau calibrated on a held split. **In-KB queries** = real (s,p) with an edge -> should ACCEPT (margin high). **OOD/fabricated queries** = (s,p) where s in-KB but (s,p) has NO edge (the realistic fabrication) -> should REFUSE. **OPEN-B:** OOD construction -- (a) in-KB-s + in-KB-p with no (s,p) edge [my proposal; realistic], (b) random unseen entity, or (c) both as sub-conditions? And is margin-threshold the right refuse mechanism, or do you want an absolute-score gate?
4. **INFERENCE-TRANSFER (load-bearing #2):** held-out 2-hop facts: (s,p1,x)+(x,p2,o) in train but (s, composed, o) NOT a direct train edge -> **assert heldout_in_compose_graph==0** (o not a direct (s,*) train edge). Substrate traverses 2-hop to infer o. **Baseline = frozen-encoder single-hop** (per reference_inference_transfer_eval_design: frozen-bge). HARD_PASS = substrate-2hop > frozen-bge-single-hop on held-out. **OPEN-C (dependency):** is a frozen bge/sentence-transformer encoder available in the .venv for the baseline? If not, what frozen-encoder do you want (or a frozen random-projection-of-entity-strings proxy)? This is the one external dependency.
5. **RETRIEVAL-AT-SCALE (load-bearing #3):** ingest full M=50k; report hop1_acc degradation curve at M={5k,10k,25k,50k}. **OPEN-D:** N_DIM at M=50k -- the cfrpe W is N_DIM^2; at N=8192 that is 268MB float32 (OK) but capacity vs 50k triples may saturate. Propose N_DIM=8192 + report the capacity curve (saturation IS the finding). Confirm N_DIM or a target.

## By-construction guards (baking in per your spec)
exact-closure=report-not-cert; heldout_in_compose_graph==0 asserted; refuse-gate IS the headline; baseline=frozen-encoder-single-hop NOT exact-closure. All 4 in.

## Plan
On your VET of OPEN A-D: I build the full cell (checkpoint/resumable per-seed, CONFIG_VERSION-all-params, selftest+smoke), then dispatch. Building the unambiguous parts (load + cfrpe ingest + fidelity-floor + scale-curve) NOW; holding the refuse-gate + inference-transfer specifics for your VET (won't guess the load-bearing mechanisms).

-- Exp-Dev
