# Pre-reg: substrate_resonator_multihop_integration_v1

**Anchor**: `substrate_resonator_multihop_integration_v1`
**Authored**: 2026-06-24 by exp_dev (Director-routed; pre-authored DISPATCH 1 spec)
**Routing**: local_cpu_queue
**Lane**: Lane 1 (substrate-native; ALL arms identical primitives, ONE knob varies)
**Timeout**: 1800s

## Strategic context

Today's `substrate_concept_kg_storage_retrieval_v1` cell observed 2-hop chained
recovery = 0.638 (ARM_2 `top1_chained` at V_C=200, V_P=10, N=8192). The base
mechanism is `naive_chain` (Hebbian-write -> argmax cleanup per hop). The
substrate Store already contains a chain-grade `iter_cleanup_chain`
(Modern-Hopfield beta-scaled softmax bundle; CERT 585 at K=2 from n8
ConceptNet; r1 MM at K=3, K=4 per LANDED-VET ee4081e6 2026-06-22). This cell
integrates the existing chain-grade Resonator primitive (PLUMBING, not novel
research) into the concept_kg apples-to-apples harness.

If HARD_PASS, validates the gap-map approach: existing Store solutions close
identified gaps without new research. First chain-grade integration demo.

## Mechanism

Synthetic concept graph (NO encoder leakage):
- V_concepts = 200, V_predicates = 10
- Random bipolar {-1,+1} unit-norm HRR codebooks (same as base cell)
- Multi-value Hebbian-accumulate ingest: `W += outer(E[o], E[s]*R[p]*sqrt(N))/N`
- Train chains: 2-hop = (s, p1, x) + (x, p2, o); 3-hop = (s, p1, x) + (x, p2, y) + (y, p3, o)

Arms (ALL share same E, R, W per seed; only composition mechanism varies):

1. **ARM_NAIVE_HEBBIAN_2HOP** (control; reproduces ~0.638)
   - Per hop: `state = W @ (state * R[p] * sq)`, then `argmax(E @ state)`
   - Pure substrate primitive; no cleanup; no top-K bundling.
   - Matches `hdlab.multi_hop.naive_chain` semantics; mirrors base cell ARM_2.

2. **ARM_RESONATOR_2HOP** (PRIMARY; integrates Resonator + confidence-tier gating)
   - Per hop: `transit = W @ (state * R[p] * sq)`; `scores = E @ transit`;
     pick top-K_set (default K_SET=20); Modern-Hopfield bundle:
     `state = sum(softmax(beta * top_scores) * E[top_idx])`, then L2-normalize.
   - beta = N_DIM (Ramsauer 2021 substrate-appropriate scale).
   - Confidence-tier gating: if top1 conf below tau_terminate, refuse (return None).
     For this PRIMARY measurement we set tau_terminate = None (no early refuse;
     measure pure cleanup gain). A separate downstream cell can sweep tau.
   - Final: argmax over E.
   - Mirrors `hdlab.multi_hop.iter_cleanup_chain` (single inner iter; standard
     one-step Hopfield per hop).

3. **ARM_RESONATOR_3HOP** (extends to 3-hop chained retrieval)
   - Same mechanism as ARM_RESONATOR_2HOP but 3 hops (s, p1, p2, p3) -> o.
   - Discriminates whether the cleanup-iteration stabilizes deeper chains
     where naive_chain catastrophically degrades.

Discriminator control (smoke-only sanity; not load-bearing for PASS):
- `RANDOM_CLEANUP` shuffles top-K indices before bundling. If RESONATOR matches
  RANDOM_CLEANUP, the cleanup mechanism is null in this regime (Fix #16 nuance);
  reported as a secondary metric.

## Pre-reg HARD bands (PRIMARY arm = ARM_RESONATOR_2HOP, single primary metric = top1)

- **Sanity** (provenance for the gap claim):
  `ARM_NAIVE_HEBBIAN_2HOP.top1` in [0.59, 0.69] (reproduces 0.638 +- 0.05)

- **HARD_PASS**: `ARM_RESONATOR_2HOP.top1 >= 0.85` AND cv across seeds <= 0.05
  (closes 2-hop interference gap; integration of existing chain-grade Resonator
  primitive validates gap-map approach)

- **MIDDLE_BAND**: `ARM_RESONATOR_2HOP.top1` in [0.70, 0.85)
  (Resonator helps but doesn't close the gap; tune K_SET / beta)

- **HARD_FAIL**: `ARM_RESONATOR_2HOP.top1 < 0.70`
  (Resonator integration does NOT close gap; gap-map approach needs revisit)

- **Bonus**: `ARM_RESONATOR_3HOP.top1 >= 0.70` = chain-grade for 3-hop
  (consistent with r1 MIDDLE_BAND at K=3 in ConceptNet; this would be tighter)

## Bias-controls / Lane 1 discipline

- Lane 1 declared: substrate-native; ALL arms share same E, R, W; ONE knob
  varies (composition mechanism only).
- Single primary metric: top1.
- Per-seed entries; cv across seeds computed; reported per arm.
- Chance baseline (1/V_concepts = 0.005) reported per arm for INTRA_LANE_DELTA.
- By-construction-saturation guard: chance-rate explicitly logged + verified
  << observed; sanity arm reproduces ~0.638 (not by-construction-perfect).
- Synthetic data; no encoder leakage; no transformer / bigram / text8 baselines.
- CONFOUND_AUDIT: codebook orthogonality (V_P=10 known collision risk);
  resonator iterations (k_inner=1 standard); confidence threshold (None for
  primary measurement; tau-sweep deferred to downstream cell).
- INTRA_LANE_DELTA: ARM 2 vs ARM 1 varies ONE knob (cleanup on/off).

## Implementation pointers

- Base cell: `experiments/exp_substrate_concept_kg_storage_retrieval_v1.py`
  (reuses bipolar, ingest_hebbian, _build_keys, _scores_batch).
- Primitive reference: `hdlab/multi_hop.py:iter_cleanup_chain` (Modern-Hopfield
  beta-scaled softmax bundle).
- Resonator network reference: `hdlab/kg_traversal.py:KGStore`,
  `experiments/exp_resonator_factorization_v1.py` (Frady/Kent 2020 resonance).
- 72b confidence-tier reference: `exp_substrate_72b_R0R1R2_claim12_tier_proof_walk_cpu_v1`
  (tau-terminate gating; we set tau=None for the primary measurement).

## Runtime estimate

- Smoke: 1 seed, N=1024, n_chains=80; ~30s expected.
- Full: 3 seeds, N=8192, n_chains=300; estimated ~10-20min wall.
- Timeout 1800s gives 3x headroom; well under PROT-021 4h checkpoint floor.

## Disciplines

- ASCII-only.
- Pure numpy (no torch) -> local_cpu_queue eligible (PROT-020 N/A).
- Per-seed CONFIG_VERSION-gated checkpoint per `experiments/_seed_checkpoint.py`.
- `_seed_checkpoint` imported (satisfies PROT-021 even though we are well below
  4h; defensive).
- Verify-run_mode-before-cert: metrics.json includes `run_mode`, `n_seeds`,
  `config_version`.
- Per-arm primary metric; cv across seeds; reported per arm.
- Per-arm metrics in `per_seed[i]` (NOT collapsed) per Fix #28.

## Fix #26 predispatch verify-the-referent (PROCEED)

- recent_landings.jsonl: 0 matches for anchor (clean dispatch).
- atoms.jsonl: 0 chain-grade matches (this is a NEW integration cell).
- Prior precedent: wave14_multihop_resonator + multi_hop primitive (CERT 585 at
  K=2); 72b R0R1R2 (confidence-tier; CERT chain-grade per memory index).
- Cell integrates these EXISTING chain-grade mechanisms into apples-to-apples
  3-arm harness.
