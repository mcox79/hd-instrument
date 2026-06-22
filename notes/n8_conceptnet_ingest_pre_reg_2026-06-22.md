# N8 ConceptNet ingest-eval pre-registration

**Cell:** `experiments/exp_n8_conceptnet_ingest_eval_v1.py`
**Anchor:** `n8_conceptnet_ingest_eval_v1`
**Author:** exp_dev (Prover)  **Date (UTC):** 2026-06-22
**Lineage:** reuses U1 (`exp_u1_fb15k237_ingest_eval_v1`) chain-grade pattern (CERT 583 -> 584); OPEN-C UNLOCKED here

## Plain-English claim

ConceptNet is a multilingual lexical knowledge graph; the English subset (~3M edges, here 100k) has
READABLE-English entities like `cat is_a mammal`. Unlike FB15k-237 (MIDs `/m/027rn` -> entity-text
not available -> semantic-encoder baseline N/A), ConceptNet lets us add a frozen-encoder semantic
baseline (sentence-transformers MiniLM-L6) as the OPEN-C check U1 deferred. The substrate-2hop
traversal must beat both a 1-hop-lookup AND the frozen-encoder NN-by-entity-name (otherwise
"composition" might just be "semantic similarity"). This is a Track-B knowledge_graph pull-up.

## Mechanism (reused from U1, NOT a re-design)

1. Multi-value Hebbian-accumulate: `W += outer(E[o], key)/N`, key = `E[s] * R[p] * sqrt(N)`.
2. Set-readout top-K: for each (s,p) with K objects, take top-K argmax (multigraph-faithful).
3. Refuse-gate: tau calibrated on first half of (in-KB, OOD) confidences, evaluated on second half.
4. Inference-transfer: held-out 2-hop chains, `(s,o) NOT in direct` assert (closure guard); compare
   substrate-2hop traverse vs 1-hop-lookup baseline vs frozen-encoder semantic NN-by-name.

## Pre-registered bands (locked here; will not be revised post-VET)

- **HARD_PASS** if ALL of:
  - set-recall_all @ M=100k >= 0.95
  - refuse: OOD_refuse >= 0.80 AND in-KB-accept >= 0.80
  - substrate_2hop > baseline_1hop + 0.02
  - substrate_2hop >= 2.0 x baseline_frozen_encoder  (OPEN-C UNLOCK; the load-bearing new bar)
- **MIDDLE_BAND** if set-recall passes the 0.85 fail-floor but ANY load-bearing dim falls short.
- **HARD_FAIL** if set-recall_all @ M=100k < 0.85, OR refuse-gate fails on either side, OR no
  composition (substrate_2hop <= 1-hop + 0.02).

## Pre-registered directional predictions

- Set-recall scale-curve should remain >= 0.95 through M=100k (U1 hit 0.99 at M=50k; ConceptNet
  has 24.8% 1-to-many vs U1's 25.8%, comparable; max K=1239 vs U1's 160, so harder tail).
- Refuse-gate should hold; ConceptNet has only 8 relation types (FB15k-237 has ~237), so the
  fabrication search-space per subject is smaller -> OOD-refuse might be slightly EASIER. Pre-reg
  the same 0.80 floor (no upward revision).
- substrate_2hop should beat frozen-encoder by a large ratio (substrate composes; encoder doesn't).
  The smoke result was 75x at M=5k; pre-reg the 2x bar as the minimum.

## Honest scope (pre-reg, will not retract)

1. ConceptNet en-100k has 8 relation types (AtLocation, CapableOf, Antonym, Causes, DerivedFrom,
   CausesDesire, DefinedAs, CreatedBy). The OOD class for refuse-gate is (s,p) in-KB with no edge
   (same as U1; realistic-fabrication style), NOT held-out-relations (insufficient relation count).
2. Frozen-encoder = sentence-transformers MiniLM-L6 (~22M params). Encoder runs ONCE at ingest
   time to embed entity names; scoring (cosine sim) is numpy matmul; NO model forward calls during
   eval. Substrate-native gate: encoder is INPUT-stage only, evaluated as a numpy matmul, comparable
   to the substrate's own scoring pattern.
3. License: ConceptNet 5.7 CC-BY-SA 4.0 + ODC-BY 4.0 (allows commercial + redistribution).
4. Dataset = 100k English edges streamed from `s3://conceptnet/conceptnet-assertions-5.7.0.csv.gz`,
   filtered to `/c/en/...` head and tail, prefix stripped, cached at
   `data/datasets/conceptnet5_en_100k.jsonl` (~7.8 MB).

## Pre-reg directional fail-bands (no negativity-bias; symmetric)

- If substrate_2hop / frozen_encoder ratio comes back BELOW 2x BUT substrate beats 1-hop by margin,
  that's MIDDLE_BAND not HARD_PASS (the frozen-encoder bar is load-bearing for the OPEN-C unlock).
- If set-recall is 1.000 ACROSS all M including M=100k, treat with suspicion (would be saturation-
  by-construction worry; the U1 LANDED-VET showed multi-value setrecall is NOT by-construction;
  re-verify random-floor analysis off the per_seed if so).
- If wall < 30 min for the full 3-seed run, treat with suspicion (probably stale checkpoint or smoke
  drift); verify run_mode == 'full' in metrics.json before treating as cert.

## Smoke evidence

- Local smoke at M=5k, N=2048, 1 seed (encoder cached): elapsed 50.9s, HARD_PASS verdict;
  set-recall_all=1.000 / OOD=1.000 / accept=0.973 / substrate_2hop=0.750 / 1-hop=0.000 /
  frozen-enc=0.010 (ratio=75x). All REQUIRED_FIELDS present in metrics.json.
- Smoke wall scales: ingest at N^2=16x (N=2048 -> N=8192), curve breadth 5 points vs 1 (~10x sum),
  3 seeds vs 1, encoder one-shot ~510s for n_ent ~80k. Projected full wall ~2300s; 50% buffer
  -> 3600s (1h) timeout.

## Dispatch plan

- Queue: `remote_cpu_queue` (NumPy-only substrate ops; encoder is one-shot CPU; not GPU-bound).
- Timeout: 3600s (1h). Falls within PROT-019 anchor-name range (no `_n<N>` suffix in anchor -> no
  PROT-019 floor); well below PROT-021 4h checkpoint-required threshold.
- Resume: per-seed CONFIG_VERSION-gated checkpoint (same pattern as U1; bare _seed_checkpoint not
  used since timeout < 4h, but CONFIG_VERSION gate is in-cell).

## Path-scoped commit

- `experiments/exp_n8_conceptnet_ingest_eval_v1.py`
- `notes/n8_conceptnet_ingest_pre_reg_2026-06-22.md` (this file)
- `data/datasets/conceptnet5_en_100k.jsonl` (cached dataset; required at dispatch time)

-- exp_dev (Prover)
