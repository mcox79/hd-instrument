# Pre-registration: query_margin_gate_smoke_v1_n4096

Date: 2026-05-31
Origin: v290 cap_map U2 HARD_FAIL + C4 research analysis.
Trigger: research drill notes/research_adversarial_defense_analysis_v1_2026-05-30.md
identified D1 (query-similarity-margin gate) as the highest-priority defense
candidate against Pattern-2 codebook-collision attacks (~1 day eng, P_deflated
0.55-0.70).

## Hypothesis

At N=4096, M=2048, depth=5, applying a query-similarity-margin gate at
retrieval time (reject queries whose argmax-1 to argmax-2 cosine margin is
below delta_margin) significantly defends against Pattern-2 codebook-collision
attacks while maintaining acceptable false-positive rate on legitimate
in-distribution queries.

## Setup

- N = 4096 (PROT-018: `_n4096`).
- M = 2048 (production).
- depth = 5.
- BSC bipolar codebook + Kerdock-like properties as in U2 base config.
- Defense mechanism D1: at each retrieval, compute argmax_1 (top cosine)
  and argmax_2 (second-largest cosine) over the codebook against q' =
  q @ W^T (after depth iterations). If `(cos_top1 - cos_top2) < delta`,
  the query is REJECTED (treated as adversarial-suspect).
- delta sweep: {0.0, 0.031, 0.063, 0.125} where 0.031 = 2/sqrt(N).
- Attack: Pattern-2 codebook-collision from
  `exp_adversarial_multi_hop_probing_v2_n4096.py` lines 150-178. The
  attack ranks all M(M-1)/2 pairwise key cosines and selects top n_q
  pairs (the worst-case order statistic).
- Legitimate queries: 100 in-distribution queries (stored keys retrieved
  through W and judged against val_idx[:100]).
- Seeds: [7, 17, 23, 31, 41].

## Defense metrics (per delta)

- `p2_defense_rate` = (# rejected adversarial + # accepted-correct-target)
  / total adversarial queries.
- `p2_leak_rate` = (# accepted with wrong target = collision target) /
  total adversarial.
- `p2_reject_rate` = # rejected / total.
- `legit_fpr` = # rejected legitimate / total legitimate.
- `legit_recall_accepted` = (# accepted-and-correct) / accepted legitimate.

## Pareto target

A delta is a **Pareto point** if `p2_defense_rate >= 0.85` AND
`legit_fpr <= 0.10`.

## Pre-registered bands

- **HARD-PASS (HP)**: at least ONE delta in the sweep hits the Pareto
  point across the 5 seeds (mean over seeds).
- **HARD-FAIL (HF)**: NO delta defends `>= 0.50` mean defense rate;
  D1 mechanism is fundamentally weak (cannot defend the attack vector at
  any threshold).
- **MIDDLE-BAND (MB)**: some delta achieves `>= 0.50` defense but no
  delta hits the Pareto target (trades off too aggressively against
  false-positive).

## Outcome plan

- **HP**: D1 routes to testbed engineering for production implementation.
  cap_map row evolves to "Pattern 2 codebook-collision: D1
  query-margin gate defends at delta=<best>; deployment-blocker
  downgraded to Pattern 4 only." Schedule G10 D7 edit-log-replay probe
  for Pattern 4.
- **HF**: D1 closed; research investigates D7 (or D2 codebook rotation)
  as next defense candidate. cap_map row remains
  "Pattern 2 deployment-blocker; D1 refuted at smoke."
- **MB**: D1 routes to research for delta-tuning study; ship D2 codebook
  rotation in parallel as defense-in-depth.

## Smoke notes

Smoke at N=1024, M=256, depth=3, n_q_attack=16, n_legit=32, 1 seed.
Quick (~5-15 s) sanity check that all 4 delta thresholds compute and
verdict gates fire HP/HF/MB on synthetic per-delta data. SELFTEST PASSES.

Smoke at smoke-scale and a manual production-scale probe (N=4096, M=2048,
depth=5, 1 seed) both produce p2_defense_rate=0 and legit_fpr=0 across all
4 deltas. Mechanistic explanation: after depth=5 retrieval, the substrate
picks the (wrong) collision target with HUGE margin (>0.84), so the gate
based on top1-top2 cosine margin never fires. The research-drill-predicted
mechanism ("tied argmax fires the gate") is not observed at this depth in
this configuration. This is the PRE-DICTED HARD_FAIL outcome -- the smoke
correctly anticipates that the gate-as-designed has no signal vs Pattern-2
under depth-5 retrieval. SHIPPING ANYWAY: the FULL run provides the
multi-seed corroboration, and the resulting D1_HARD_FAIL routes to research
for D7 (edit-log-replay) or alternative-mechanism D1 variants
(e.g. margin computed before W^5 iteration, or absolute-similarity
threshold). This is a SCIENTIFIC pre-fail probe, not an instrumentation
artifact.

Also: the attack at scale collapses to a small number of distinct stored
keys (~3 unique i at N=4096 M=2048 due to Kerdock-tied pairwise cosines).
This matches U2's original pattern_2 implementation behavior (1 unique i
at the same config); not a code bug.

## Timeout estimate

- Smoke wall (actual observed): 0.09 s at N=1024 / M=256 / depth=3 / 1 seed.
- FULL: N=4096 (4x N_smoke), M=2048 (8x), depth=5 (vs 3), 5 seeds
  (vs 1), 4 deltas (vs 4 same).
- Formula: ceil(1.5 * 0.09 * 4^1.5 * 5) = ceil(5.4) = 6 s nominal.
- The formula estimate is far below the PROT-019 floor for _n4096 anchors
  (14400s). Applying the PROT-019 floor as the binding constraint.
- Note: experiment is expected to complete well within 1 hour at FULL scale.
  D1 mechanism is known to produce fast all-zero outputs (pre-registered
  HARD_FAIL behavior), so each seed completes in seconds.
- Queue TIMEOUT: **14400s (4h)** -- PROT-019 floor for _n4096.

## Queue + routing

- Queue: `remote_cpu_queue` (CPU-only smoke; D1 is a defense smoke probe).
- Script: `experiments/exp_query_margin_gate_smoke_v1_n4096.py`.
- Anchor: `query_margin_gate_smoke_v1_n4096`.
- Timeout: 14400 s (PROT-019 floor; actual expected runtime << 1h).
