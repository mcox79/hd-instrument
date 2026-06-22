# H HotpotQA 1k-dev ingest pre-registration

**Cell:** `experiments/exp_h_hotpotqa_ingest_v1.py`
**Anchor:** `h_hotpotqa_ingest_v1`
**Author:** exp_dev (Prover)  **Date (UTC):** 2026-06-22
**Lineage:** reuses n8 ConceptNet pattern (CERT 585) + U1 FB15k-237 (CERT 584) chain-grade mechanism on a 3rd domain corpus (multi-hop QA on Wikipedia titles).

## Plain-English claim

HotpotQA is a multi-hop question-answering dataset where each question has 2 supporting Wikipedia paragraphs (with titles). The substrate ingests each item as a 2-hop chain:
`(title1, "linked_via", title2)` plus `(title2, "supplies_answer", answer)`.
At retrieval, the substrate must traverse from `title1` through the bridge entity `title2` to recover the `answer`, beating both a 1-hop direct baseline (substrate genuinely never saw `(title1, supplies_answer, ?)`) and a frozen-encoder semantic nearest-neighbor baseline. This is the same chain-grade mechanism that landed n8 (ConceptNet) and U1 (FB15k-237), now applied to multi-hop QA on free Wikipedia content.

## Mechanism (reused; not re-designed)

1. Multi-value Hebbian-accumulate: `W += outer(E[o], key)/N`, key = `E[s] * R[p] * sqrt(N)`.
2. Set-readout top-K: for each (s,p) with K objects, take top-K argmax.
3. Refuse-gate: tau calibrated on cal-half of (in-KB, OOD) confidences, evaluated on ev-half.
4. Inference-transfer: held-out bridge-type 2-hop chains; substrate-2hop vs 1-hop direct (no leak; substrate never saw `(t1, supplies_answer, ?)`) vs frozen-encoder semantic NN-by-name.
5. Discriminator-regime control (Fix #16): random-key control on (s,p) pairs not in keyobjs; substrate setrecall must exceed random-control by >= 2.0x.
6. Encoder-geometry guard: off-diagonal mean cosine over a 500-entity sample; HALT if > 0.95 (the MedQA mean-pool-collapse signature).

## Pre-registered HARD bands (locked here; will not be revised post-VET)

**HARD_PASS** if ALL of (3 seeds, all bands met):
- setrecall_all >= 0.95 (load-bearing #1; floor)
- refuse OOD >= 0.80 AND in-KB accept >= 0.80 (load-bearing #2)
- substrate_2hop > 1-hop direct + 0.02 AND substrate_2hop / 1-hop direct >= 2.0x (load-bearing #3a)
- substrate_2hop >= 2.0x frozen-encoder semantic (load-bearing #3b)
- zero_llm_calls_at_inference == True (substrate-only-decode gate)
- encoder off-diag cos <= 0.95 (mean-pool keysep intact)

**HARD_FAIL** if ANY:
- setrecall_all < 0.50 (the MedQA signature; substrate at chance)
- refuse OOD < 0.50
- substrate_2hop / 1-hop direct < 1.5x (composition fails)
- encoder off-diag cos > 0.95 (mean-pool collapse pre-empt)

**MIDDLE_BAND:** setrecall in [0.50, 0.95] OR 2-hop ratio in [1.5x, 2.0x] OR refuse partial.

## Design deviation from spawn directive (documented)

Spawn directive nominated **pythia-160m mean-pool** as the encoder. The MedQA HARD_FAIL HONEST_NEGATIVE earlier today (2026-06-22) showed pythia-160m mean-pool collapsed on long medical vignettes (off-diag cos 0.9865). HotpotQA encodes ENTITIES (Wikipedia titles, 3-5 tokens), not long passages, so pythia collapse risk is lower -- but **MiniLM-L6** is the encoder that landed n8 chain-grade (CERT 585) on short entity names. To maximize mechanism-mirror to n8 + minimize encoder-risk on the 3rd corpus, I chose MiniLM-L6.

The substrate-only-decode gate is identical: encoder runs ONCE at ingest, scoring is numpy matmul, no model forward calls at retrieval. `_LLM_CALL_COUNTER[0]` instrumented module-top.

The encoder-geometry HALT check is in the cell verdict path explicitly per directive: if off-diag cos > 0.95, the cell HARD_FAILs with the MedQA-collapse-signature reason printed.

## Smoke evidence (committed)

Local smoke at N=1024, M=200 items (400 triples), 1 seed: elapsed 13.9s, **HARD_PASS verdict**:
- setrecall = 1.000 (random-control 0.000; ratio essentially infinite)
- refuse OOD = 1.000, accept = 0.980 (tau = 0.0009114)
- substrate_2hop = 1.000, 1-hop direct = 0.000 (substrate genuinely never saw the direct key; pure composition)
- frozen-encoder = 0.083 (substrate ratio = 12x; well above 2.0x bar)
- bridge_recall = 1.000 (hop-1 perfect)
- encoder off-diag cos = 0.1440 (max 1.0 = diagonal self-match; well below 0.95 HALT)

## Near-full-scale single-seed timing probe (Fix #3 mandatory)

Single-seed at N=4096, M=1000 items (2000 triples, 2696 entities), measured locally:
- **wall = 13.8s** (encoder load: 12.7s; ingest matmul: 0.4s; eval: <0.1s)
- setrecall = 1.0000, 2-hop substrate = 0.9933, refuse OOD = 1.000
- encoder off-diag cos = 0.1463 (max 0.8580)
- Discriminator-regime control PASSES: random-key control = 0.0000; substrate ratio = infinite over random

Extrapolation to 3-seed full: encoder load is one-shot (cached across seeds in-process) ~13s + 3 x (matmul + eval) ~3s = **~16-30s wall on remote**.

Conservative timeout: **1800s** (30 min) -- 60x safety margin over measured. Falls below PROT-019 (no `_n<N>` suffix) and PROT-021 (< 14400s; no checkpoint required, but checkpoint helper is wired anyway).

## Pre-reg directional symmetry (negativity-bias prevention)

- If substrate_2hop = 1.000 EXACTLY across all 3 seeds, treat with suspicion: verify chains were ACTUALLY held out from the direct-keys (assert n8/U1 `heldout_in_compose_graph == 0` check; in this cell the 1-hop direct baseline serves the same role).
- If random-key control returns > 0.05, escalate as discriminator-regime ambiguous.
- If frozen-encoder is > 0.20, investigate: HotpotQA bridge entities may have high semantic similarity to t1 (e.g., same-actor questions), in which case the frozen-enc baseline is a stronger discriminator than expected, and substrate may "merely" be ~10x rather than 24x.

## Honest scope (pre-reg, will not retract)

1. Corpus = 1000 HotpotQA dev items (distractor split). Each item contributes 2 triples; bridge-type items also contribute one 2-hop chain. Comparison-type items (yes/no answers) are ingested for set-recall + refuse-gate but excluded from 2-hop eval (no genuine bridge).
2. Entity vocab = union of supporting-fact titles + answer strings; ~2700 entities at full scale.
3. Relation vocab = 2 types: "linked_via", "supplies_answer".
4. Encoder = sentence-transformers/all-MiniLM-L6-v2 (~22M params); ingest-time only; encoder discarded post-encode; scoring at retrieval is numpy matmul (no forward calls).
5. License: HotpotQA is CC BY-SA 4.0; redistributable.
6. Cell is NumPy-only; route to remote_cpu_queue (not overnight_queue / GPU).

## Dispatch plan

- Queue: **remote_cpu_queue**.
- Timeout: **1800s** (30 min; 60x safety margin over measured 14s single-seed).
- Resume: per-seed `_seed_checkpoint` with `run_config={N, M, run_mode}` mismatch guard.
- Push: harness-DENIED to exp_dev; route to Orchestrator with the local commit hash.

## Path-scoped commits

- `experiments/exp_h_hotpotqa_ingest_v1.py`
- `notes/h_hotpotqa_ingest_pre_reg_2026-06-22.md` (this file)
- `data/exp_h_hotpotqa_ingest_v1_smoke/metrics.json` (smoke evidence)
- `data/datasets/hotpot_qa_distractor_dev_1k.jsonl` ALREADY on disk locally and (verify) remote.

-- exp_dev (Prover)
