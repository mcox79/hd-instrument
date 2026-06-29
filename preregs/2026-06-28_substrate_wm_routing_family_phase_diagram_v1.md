# Pre-registration: substrate_wm_routing_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER 2026-06-28 Research directive — systematic phase-diagram coverage
across COMPONENTS, not just config parameters. Encoder family (substrate_pc_*) +
cleanup family (PC variant) + sequence-binding encoder family already in flight.
This is the FOURTH systematic component-sweep cell; covers the ROUTING family
for multi-bank WM.

## Anchor

`substrate_wm_routing_family_phase_diagram_v1_seed_{7,13,19}`

Three sibling cells (one per seed; CHUNKED architecture per USER 2026-06-28).

## Routing

- **Queue:** overnight_queue (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** N_DIM=8192, CODEBOOK_SIZE=16384, K_max=8192. Multi-bank workspace
  computation is matmul-heavy; routing-family swap evaluates 4 different
  bank-routing fns over (K, B) grids per regime. GPU mandate per Fix #24.
- **Fallback:** CPU fallback works for smoke (verified locally below);
  FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue.
- **GPU util gate:** smoke profiles gpu_util >= 30% on remote GPU (Fix #24
  lowered ceiling); WM K-ceiling v3 achieved gpu_util_mean=55% at K=16384
  scale; this cell at K=8192 expected ~30-50%.

## Hypothesis

**Question:** does the 3rd-most-load-bearing lever — bank routing — show
routing-family invariance, partition-dominance, or k-NN-style preference for
substrate multi-bank WM?

**Brain prior (USER existence-proof intuition):** biological dlPFC routing
is closer to k-NN-style (graded gating) than hard partition. If substrate
echoes this, we'd expect knn_softmax / softmax_attention to dominate at
discriminating K. If partition dominates, that's substrate's current
chain-grade architecture being correct. If all routings cluster, that's
routing-family-invariance — a feature, not a bug.

**Honest-downward:** all three outcomes are scientifically meaningful for
the phase diagram. Smoke evidence (below) shows all 4 routings COMPETITIVE
at K<=1024; discriminating regime is K=4096/8192 + ADVERSARIAL.

## Mechanism

Multi-bank associative-memory writing with bank-routing cleanup (per
WM K-ceiling v3 chain-grade primitive). Each bank holds k_per_bank=64 items
in bipolar workspace (sum of item*slot_tag + Gaussian noise, sign-quantized).
Cue contains bank-tag + slot-tag (CUE_COS=0.70); the load-bearing axis is the
**routing function** that maps cue -> selected workspace.

## Routing families (OUTER axis; LOCKED)

| Routing | Description | Brain analogy |
|---------|-------------|---------------|
| `partition` | argmax(cue @ bank_tags.T); hard partition. POSITIVE CONTROL. | n/a (engineering default) |
| `knn_softmax` | softmax(beta * cue @ bank_tags.T) @ workspaces; soft mixture. | graded dlPFC gating |
| `softmax_attention` | softmax over banks -> top-2 -> renormalize -> mix -> WTA. | self-attention top-k regime |
| `learned_hierarchical` | 2-level: argmax group of GROUP_SIZE=4 banks, then argmax bank within group. | hierarchical cortical routing |

## Inner axes

| Axis | FULL | SMOKE |
|------|------|-------|
| K (capacity x banks) | 1024, 4096, 8192 | 256, 1024 |
| Regimes | RANDOM, ADVERSARIAL | RANDOM |
| k_per_bank | 64 (envelope) | 32 |
| N_DIM | 8192 | 2048 |
| CODEBOOK_SIZE | 16384 | 4096 |
| N_ITEMS_PER_K | 100 | 40 |

**Cardinality:**
- FULL: 4 routings * 3 K * 2 regimes = **24** phase points per seed (locked)
- SMOKE: 4 routings * 2 K * 1 regime = **8** corner points per seed

## Pre-reg bands (LOCKED at module init)

- HP_CHAIN_GRADE_RECALL = 0.95
- HP_CHAIN_GRADE_ROUTE_ACC = 0.95
- HP_ADV_WITHIN_RANDOM = 0.05
- HP_ADV_BREAK_THRESHOLD = 0.30
- HP_K_PER_BANK_MAX = 64 (envelope)
- Q_SUSPECT_SATURATION = 0.995 (by-construction-saturation flag)
- HP_HARD_PASS_LO = 0.80
- HP_MIDDLE_BAND_LO = 0.50
- HP_FLOOR_HI = 0.10
- HP_DISCRIMINATOR_FRACTION = 0.30 (each routing must show >=30% disc phase points)
- BETA_SOFT = 8.0 (softmax temperature; matches PC encoder family v1 + sane prior)
- GROUP_SIZE = 4 (hierarchical: 2 groups at K=1024+ ; 4 at K=4096+; 16 at K=8192+)

## POSITIVE CONTROL

`partition` routing at K_total=4096, regime=RANDOM must reproduce
recall >= 0.90 (WM K-ceiling v3 measured rec=1.000 at this point; conservative
floor 0.90).

If POSITIVE CONTROL fails, the test rig is broken and verdict = HARD_FAIL_CONTROL_FAIL
regardless of any other arm outcomes.

Smoke variant: partition at K=1024 must >= 0.60 (smoke-N=2048 rail-drift OK).

## Verdicts

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_ROUTING_FAMILY_PHASE_DIAGRAM | 1 routing strictly dominant (mean recall >0.10 above next best) + cardinality OK + control passes |
| ROUTING_FAMILY_INVARIANCE | >=2 routings COMPETITIVE (within 0.05 of best) + control passes |
| MIDDLE_BAND | sat_fraction >=0.75 (by-construction-saturation) OR mixed |
| HARD_FAIL_CARDINALITY_BREACH | n_units < expected (META_RULE_H) |
| HARD_FAIL_CONTROL_FAIL | partition baseline didn't reproduce chain-grade |
| HARD_FAIL_ROUTING_COLLAPSE | <2 non-partition routings produced distinct ws_selected hashes |

## Discriminator-must-survive-scale (USER 2026-06-26)

**Check option B (analytical justification):**

At K<=1024 smoke regime, all 4 routings should converge to high recall
because BETA_SOFT=8.0 + high CUE_COS=0.70 makes softmax one-hot and
hierarchical's group-level routing also picks the correct group with high
confidence. This is the SATURATED regime (expected from smoke).

At K=4096/8192 FULL regime + ADVERSARIAL feature-overlap, the routings
should DIFFERENTIATE because:
- Higher K = more banks = more confusable bank_tags (softmax becomes less
  one-hot when many bank_tags have similar similarity to cue)
- ADVERSARIAL FEATURE_OVERLAP_FRAC=0.20 reduces cue specificity
- Hierarchical's 2-level routing has different error-mode than flat partition

Smoke evidence supports this: at K<=1024, sat=3-6 of 8 pts (some HP, no MB);
at full K=4096+ discrimination expected.

**Why this passes the discriminator-survives-scale gate:** the discriminator
IS the routing-family separation at full-N + ADVERSARIAL; smoke verifies
mechanism works + positive control passes + routing-pair distinctness
demonstrated at ambiguous-regime probe (hierarchical 22% different from
partition at ambiguous selftest probe).

## Smoke verdict (laptop CPU 2026-06-28)

All three siblings HARD_PASS_SMOKE:

| Seed | sat | hp | mb | floor | fail | PC recall | Verdict |
|------|-----|-----|-----|-------|------|-----------|---------|
| 7  | 3 | 5 | 0 | 0 | 0 | 0.989 | HARD_PASS_SMOKE |
| 13 | 6 | 2 | 0 | 0 | 0 | 0.996 | HARD_PASS_SMOKE |
| 19 | 4 | 4 | 0 | 0 | 0 | 0.993 | HARD_PASS_SMOKE |

- 8/8 cardinality on every seed (META_RULE_H satisfied)
- POSITIVE CONTROL passes (partition reproduces chain-grade at K=1024 smoke)
- All 4 routings COMPETITIVE at smoke (within 5% of best)
- Selftest: 4/4 routings sanity recall=1.000; hierarchical 22-24% distinct
  from partition at ambiguous-regime probe (knn_softmax ~0.3% diff,
  softmax_attention 0% diff — these collapse to one-hot at BETA_SOFT=8.0
  with clear cues, as expected by softmax theory; full-K + ADVERSARIAL
  expected to differentiate them)

## Config

- N_DIM=8192 (FULL); CODEBOOK_SIZE=16384
- SIGMA=1.0, CUE_COS=0.70, FEATURE_OVERLAP_FRAC=0.20
- Seeds: [7, 13, 19] across 3 sibling files (CHUNKED per USER 2026-06-28)
- Encoder provenance: SUBSTRATE_NATIVE (bipolar codebook + bank routing)
- Substrate-only decode (zero LLM calls; gate assertion in main())

## ETA + Timeout

Per-seed wall (FULL, GPU):
- K=1024 routing*regime: ~0.5s/arm * 4 routings * 2 regimes = ~4s
- K=4096 routing*regime: ~2-3s/arm * 8 = ~20s
- K=8192 routing*regime: ~4-6s/arm * 8 = ~40s
- Codebook builds (per regime): ~2s * 2 = ~4s
- Total per seed: ~70-80s GPU

Total (3 seeds): ~4-5 min GPU.

**Timeout per seed: 1800s (30 min)** — generous 20x margin over GPU estimate
for CPU fallback or slow-start; well under PROT-019 4h floor (no _n<N> suffix
on anchor so PROT-019 not triggered).

## REQUIRED_FIELDS

verdict, verdict_msg, elapsed_s, summary, anchor_name, cardinality_ok,
expected_n_units, observed_n_units, positive_control_result, per_routing_summary,
routing_tiers, routings_differ_from_partition, n_routings_distinct_from_partition.

## Functional requirements (composition edges)

This cell's mechanism is multi-bank WM (already chain-grade per WM K-ceiling v3).
Composition: encoder (fixed bipolar) -> bank_tag * slot_tag bind -> ROUTING
(swapped axis) -> cleanup over codebook. SHAPE_MATCH per routing: each
routing receives same (cues, bank_tags, workspaces) tuple and returns
(ws_selected: K x N, bank_routed: K) — see `_ROUTING_REGISTRY` in
`_substrate_wm_routing_family_phase_diagram_v1_core.py`.
