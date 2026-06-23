# Pre-reg -- alloc_routing_excitability_trace_smoke_v1

**Anchor name:** `alloc_routing_excitability_trace_smoke_v1`
**Script:** `experiments/exp_alloc_routing_excitability_trace_smoke_v1.py`
**Author:** exp_dev (per USER 2026-06-23 dispatch prompt; honoring research drill)
**Date:** 2026-06-23
**Queue:** `local_cpu_queue` (USER-directed; ~10-15 min smoke wall)
**Source-of-truth:**
- `notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md`
- `notes/exp_dev_handoff_research_drill_sparse_allocation_routing_learning_2026-06-23.md`

## Mechanism intuitive

Brain engram allocation works because neurons "remember" recent activity. CREB-mediated
intrinsic-excitability boost lasts hours-days post-activation; most-recently-active neurons
are MORE LIKELY to be recruited for the next memory ensemble (rich-get-richer / Tonegawa
2007/2014/2016). Substrate analog: maintain a per-position scalar excitability trace `E[i]`
for each of N positions; when writing a new atom, sample sparse positions weighted by
`softmax(beta * E[i])`; update traces after write. Forward-only: no backprop required.

## Configuration

- N_DIM = 4096
- M = 2000 (FULL) / 200 (smoke); production-ish scale per USER prompt
- K_SPARSE = 100 nonzero per atom (2.5% sparsity)
- 3 arms:
  - `ARM_RANDOM_SPARSE` (baseline; Drosophila-MB analog) -- uniform random K positions
  - `ARM_EXCITABILITY_TRACE` (mechanism; Tonegawa-CREB analog) -- softmax(beta*E) sampling +
    trace update `E[positions] += alpha`, decay `E *= 0.99` per write
  - `ARM_KWTA_HEBBIAN` (compare; Marr-Albus cerebellar analog) -- top-K by abs(W @ x) +
    Hebbian update on selected rows
- Hyperparameters: beta=2.0, alpha=0.1, decay=0.99, kwta_eta=0.01
- Corpus: 2000 synthetic clean bipolar atoms drawn from N_FAMILIES=20 random
  prototype centroids (within-family bit-flip noise p=0.20). No substrate-graph
  contamination per discipline.
- Seeds: FULL {7, 17, 23}; smoke {0}.
- Per-seed checkpointing via `_seed_checkpoint`.

## Pre-reg HARD bands (per USER 2026-06-23 explicit dispatch prompt)

**Discriminator:** ARM_EXCITABILITY_TRACE vs ARM_RANDOM_SPARSE.

### HARD_PASS (excitability-trace works; chain-grade-eligible)
ARM_EXCITABILITY_TRACE achieves **ALL THREE**:
- A. recall@1 at sigma=1.0 >= 0.50 (in operating envelope)
- B. capacity at sigma=1.0 >= 1.5x ARM_RANDOM_SPARSE
- C. clustering purity >= ARM_RANDOM_SPARSE + 0.05

### HARD_FAIL (mechanism dead; forward-only learned routing closed; backprop fallback)
ARM_EXCITABILITY_TRACE **ALL THREE**:
- recall@1 at sigma=1.0 <= ARM_RANDOM_SPARSE + 0.02
- AND capacity-ratio <= 1.05x ARM_RANDOM_SPARSE
- AND clustering purity not improved (within +0.01)

### MIDDLE_BAND
Partial benefit -- some but not all HP thresholds met, and HF thresholds not all tripped.

## Sanity (CONFOUND_FAIL detector)

At M=10 (light load), ALL arms must recall@1 = 1.000 at sigma=0. At identical input
(deterministic) excitability traces must evolve deterministically (T3b in --self-test).

## Metrics emitted per arm

- A. `cleanup_recall` at sigma in {0.0, 0.5, 1.0, 1.5}
- B. `capacity` -- largest M where recall@1 at sigma=1.0 >= 0.80 (M-grid sweep)
- C. `clustering_purity` -- K-means(N_FAMILIES) over normalized codebook + majority-vote
  purity vs known family labels
- D. `position_reuse` -- distribution of `E[i]` (mechanism arm) or selection-count (other
  arms): mean / std / cv / p10 / p50 / p90 / p99 / fraction_used

## Discriminator (load-bearing)

Three load-bearing comparisons, ALL must be passed for HARD_PASS:
1. recall_lift := exc.recall@sigma=1.0 - random.recall@sigma=1.0 ; HP requires >= 0.50 absolute
   (random baseline below this; exc must clear envelope)
2. capacity_ratio := exc.capacity / random.capacity ; HP requires >= 1.5x
3. purity_lift := exc.purity - random.purity ; HP requires >= 0.05 absolute

Inverted (ALL three) for HARD_FAIL.

## Falsifiable predictions (cross-arm)

- **P1**: If excitability-trace produces structured (non-uniform) use of position space,
  `position_reuse.cv` for ARM_EXCITABILITY_TRACE should exceed RANDOM by >= 0.3 (RANDOM
  use_count CV near sqrt(M*K/N)/mean ~ low; trace concentrates use).
- **P2**: ARM_KWTA_HEBBIAN expected weaker than ARM_EXCITABILITY_TRACE because weight-based
  forward-only learning at N=4096 with bounded data is the regime that HARD_FAILed for
  SoftHebb at the encoder layer (different layer here so result may differ). If KWTA
  outperforms EXC by recall_lift >= 0.05 we have surprise evidence that weight-based
  competitive allocation > position-trace allocation.

## Substrate-product implications

- **HARD_PASS**: lift to `hdlab/allocation_trace.py` as substrate primitive in next cycle;
  compose with `kg_traversal` for substrate_self_map_v2f rescue and Phase-2 autoatom path.
  Substrate gains forward-only learned-routing primitive without published HD/VSA precedent.
- **HARD_FAIL**: forward-only routing path closes at production scope. Backprop-minimum
  fallback (Anchor 2 of research drill -- single linear projection + InfoNCE) becomes
  next-line lever, pending USER confirmation that routing-layer-backprop is acceptable
  (distinct from representation-layer MiniLM/BGE forbid).
- **MIDDLE_BAND**: characterize via alpha/beta/decay ablation sweep; tunable primitive.

## Compute / wall budget

- Smoke (M=200, 1 seed, 4 arms over capacity grid + cleanup-sigmas + clustering):
  estimated ~3-5 min CPU. Cap via `--timeout 900` (15 min) on the queue.
- FULL (M=2000, 3 seeds, all metrics): estimated ~45-60 min CPU per research drill;
  this is the SMOKE variant (anchor name ends `_smoke_v1`) -- FULL variant would be a
  follow-on cell `alloc_routing_excitability_trace_v1` queued only after smoke HARD_PASS
  or signal-positive MIDDLE on smoke metrics.

## Self-test coverage (T1-T12, all in script `_selftest`)

T1 family-prototype atom builder (bipolar shape/labels), T2 random-alloc K-sparsity,
T3 excitability-trace shape + cv>0, T3b excitability determinism across runs, T4 kwta
K-sparsity, T5 sigma=0 cleanup=1.0, T6 perfect-cluster purity~1.0, T7 reuse stats keys,
T8 measure_capacity sigma=0, T9 CONFOUND_FAIL on bad sanity, T10 HARD_PASS detection,
T11 HARD_FAIL detection, T12 MIDDLE_BAND detection.

## Cites

- Research drill source: `notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md`
- Exp-dev handoff: `notes/exp_dev_handoff_research_drill_sparse_allocation_routing_learning_2026-06-23.md`
- Tonegawa engram allocation (CREB) -- Han 2007 / Yiu 2014 / Cai 2016 / PMC11112642 2024
- Marr 1969 / Albus 1971 -- cerebellar k-WTA Hebbian
- Lin eLife 2014 -- Drosophila APL sparse coding (random+inhibition baseline)
- Moraitis 2021 SoftHebb -- prior HARD_FAIL at encoder layer (distinct from allocation layer)

## Substrate-product moat positioning

If HARD_PASS: substrate gets forward-only learned-sparse-routing primitive that has no
direct published precedent in HD/VSA literature. Combined with chain-grade KG portfolio
(FB15k-237 / ConceptNet / HotpotQA), substrate becomes first VSA framework with
substrate-native learned sparse routing.
