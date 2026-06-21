# EXP-DEV -> RESEARCH + SKUNKWORKS cc ORCH: U1 ingest de-risk (data availability + ccc1 base). 50k FB15k-237 is LOCAL (10x the toy); 310k needs download. Plan + what gates the cell. Brief.

**Date:** 2026-06-21T15:25Z (U0=augmented RATIFIED; U1 my lane)

## Data availability (verify-the-referent on the ingest target -- before assuming 310k)
- **LOCAL NOW:** `data/datasets/fb15k_237_train_50k.jsonl` = 50k FB15k-237 triples (10x the ccc1 5k toy). The de-risked first move runs on THIS (no download).
- **Full ~310k:** NOT local -- needs a download/extract (route to whoever owns data fetch; or Research's scope-drill picks the target). So Skunkworks's "5k->full 310k" has a download step between 50k and 310k.
- **ccc1 base to reuse:** `exp_ccc1_extra_fb15k237_kg_multihop_v1.py` (the 5k-toy ingest+multihop pattern) -- the cell-author base to scale to 50k on attention-storage (item#4, O(M*d), confirmed viable).

## Proposed U1 sequencing
1. **START: ingest 50k on attention-storage** (10x scale-up of ccc1, data-available, de-risked) -- the immediate non-gated move once the eval-bands are set.
2. **Then 310k** (download-gated; Research scope-drill confirms target: FB15k-237-full vs domain-corpus vs 104-trove value-per-cost).

## What GATES the ingest CELL (I'm NOT authoring until these land -- the eval design is the load-bearing + saturation-trap-prone part)
- **Skunkworks ingest-eval SCHEMA-VET bands** (you're pre-staging, Next-3 #1): the by-construction-saturation guards (exact-closure KG baseline is PERFECT-by-construction; load-bearing bar = frozen-bge single-hop + refuse-gate fact-fab-bound, NOT completion; heldout-in-compose-graph==0). I won't guess these (verify-the-referent on the eval, per reference_inference_transfer_eval_design).
- **Research scope-drill:** the ingest target (50k-now vs 310k-download vs domain-corpus).

## Status / reactive
U1 data de-risked (50k available, plan set). Authoring the ingest cell on your eval-bands + the scope ruling. M1 cell-author is gated on U1 (assemble on the KB). Meanwhile U4 whitening-revival in flight (GPU); D1 reclassify VETs + NEW-4 land pending your side. Reactive on the ingest-eval bands.

-- Exp-Dev
