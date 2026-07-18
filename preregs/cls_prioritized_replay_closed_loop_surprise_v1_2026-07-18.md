# Pre-registration: cls_prioritized_replay_closed_loop_surprise_v1

Date: 2026-07-18. Cell: `experiments/exp_cls_prioritized_replay_closed_loop_surprise_v1.py`.
Buildable-queue item 1 (`notes/research_brain_learning_synthesis_and_overnight_buildable_program_2026-07-18.md`).
Local-runnable, glass-box, numpy, no external LLM. CLAIM-VET-pending; NOT self-declared chain-grade.

## Question
Does CLOSED-LOOP SURPRISE-prioritized replay (sample replay items by the substrate's OWN current surprise,
`additive_map.score_all = 1 - reciprocal_rank`, recomputed each block = closed-loop, Schaul-PER style) beat
UNIFORM random replay for consolidation, at MATCHED replay BUDGET -- or can rank-1 Hebbian storage NOT
exploit ANY priority signal? Prior R7 FALSIFIED a STATIC Hebbian-MIR tag; the closed-loop-surprise variant
was UNTESTED.

## Single variable
The replay SAMPLING DISTRIBUTION over a fixed replay-eligible pool, at matched budget B distinct items/block.
Everything else identical across arms: net init (same seed), budget, epochs, interference blocks, eval sets.

## Design
- Old bank: OLD_CLASSES=12 x OLD_EXEMPLARS=12 = 144 items. cue=[shared class code (SHARED_FRAC) | independent
  item probe]; target = UNIQUE per-item bipolar vector (independent within-class content; class tells you
  NOTHING about the target -> generalization/proximity confounds structurally defeated).
- Split (deterministic): ELIG_PER_CLASS=8 -> E=96 replay-ELIGIBLE pool; held-out Q=48 (4/class) NEVER
  replayed by any arm.
- Interference: K=8 sequential new blocks (NEW_CPB=3, NEW_EXEMPLARS=12), E_NEW=200 epochs each (drives real
  catastrophic forgetting via shared W1/W2). E_OLD=400. LR=0.04 (MEASURED@ parent: >=0.06 diverges).
- Net: RegNet cue(256)->tanh hidden(160)->linear target(64). Shared, rank-limited representation.
- Matched budget B_REPLAY=12 distinct eligible items/block (12.5% of E). Scarce budget = most-decisive
  operating point (reshuffle-vs-add-capacity shows most when budget is tight) + centers uniform in the
  measurable band (verified at smoke: uniform_E=0.55 at SF=0.75; META_RULE_AG).
- Surprise (glass-box) = 1 - reciprocal_rank of the item's TRUE target among the full old codebook by cosine
  of the net's CURRENT output = `additive_map.score_all` analog. Sampling P(i) ~ (surprise_i + 1e-3)^ALPHA,
  ALPHA=1.0, without replacement.

## Arms
- no_replay (floor), uniform_replay (REAL baseline), surprise_closed_loop (MECHANISM; recompute each block),
  surprise_static_snapshot (control; surprise frozen after old block), fresh_net_uniform / fresh_net_surprise
  (confounds; fresh net trained only on each arm's replayed union -- must FAIL on independent held-out Q).

## Metrics
- PRIMARY / LOAD-BEARING = E-pool retrieval accuracy (chance=1/144). delta_E = closed_loop_E - uniform_E.
  Captures whether priority ADDS net protected capacity over the directly-allocated pool or merely RESHUFFLES.
- SECONDARY = never-replayed held-out Q retrieval (distributed consolidation via shared basis).
- closed_vs_static = closed_loop_E - static_snapshot_E (is closed-loop recomputation the lever?).

## Pre-registered bands (envelope-fail-bands; retrieval-accuracy metric in [0,1]; structured end SF=0.75)
- HARD_PASS: delta_E >= 0.08 on 2/3 seeds AND delta_Q >= -0.03 (do-no-harm on held-out) -> priority replay
  is a REAL consolidation lever.
- HARD_FAIL: delta_E <= 0.02 on 2/3 seeds -> rank-1 Hebbian cannot exploit priority; fix = three-factor /
  eligibility-trace plasticity (the credit-assignment drill's differential-weighting rule). VALID informative
  outcome (plasticity-rule localization); NOT tortured to avoid.
- MIDDLE_BAND: 0.02 < delta_E < 0.08 -> weak/partial lever, not decisive.

## Difficulty-ON gates (aggregate, structured end; all must pass or MIDDLE_BAND_REGIME_INCONCLUSIVE)
net learned E initially (>=0.70); no_replay E collapses (<=0.35); uniform beats floor (>=0.10) and is in band
(0.30<uniform_E<0.90); BOTH fresh-net confounds FAIL held-out Q (<=0.10 -> content independent).

## Compute architecture
sequential-CPU justified: RegNet backprop chained across K interference blocks (step N depends on N-1); wall
time ~28s for full 3-seed grid (< the 10s-per-point batching trigger is moot at total 28s). No GPU needed.
final_metrics_atomicity: tmp_replace. cell_chunked: false (fast single-process). crlb_n/a: retrieval accuracy
over codebook, chance=1/144; feasibility verified by uniform in-band at smoke. arms_differ_verified: true.

## Result (MEASURED@ data/exp_cls_prioritized_replay_closed_loop_surprise_v1/metrics.json)
MIDDLE_BAND_WEAK_LEVER (see completion report for full numbers + interpretation). CLAIM-VET-pending.
