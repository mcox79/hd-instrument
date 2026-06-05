# exp_dev hand-off -- research: cf-RPE + sparse shared axis / superadditive composition roadmap

Filed-by: research sub-agent (2026-06-04)
Trigger: notes/research_drill_cfrpe_sparse_shared_axis_negative_2x_2026-06-04.md
Pause state: OBEY orchestrator_paused.flag; do not queue if flag present

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev decides anchor names, sweep grids,
threshold formulas, and queue routing. This file provides TASK + WHY + CONTRACT + AUTONOMY only.

---

## CONTEXT

Bundle A result: cf-RPE + Drosophila sparse at bigram N=512 yielded MIDDLE_BAND (additive, not
superadditive). Research drill confirms: both primitives address the SAME effective gain axis
(task-supervised retrieval fidelity). Superadditive composition requires pairing primitives from
ORTHOGONAL gain axes: task-supervision x temporal-storage.

Gain-axis taxonomy (from research note):
  Task-supervised: cf-RPE, sparse coding, BCM normalization
  Temporal: STDP-asymmetric, position-binding, multi-bank addressing
  Capacity: modern Hopfield p=4, anti-Hebbian, hierarchical aggregation
  Compositional: L-deep composition, stacked W

---

## ANCHOR CANDIDATES (rank-ordered)

1. cf-RPE + STDP-asymmetric at bigram N=512
   Why now: highest-priority heterogeneous pairing (task x temporal); cheapest decisive test
   for shared-axis vs orthogonal-axis hypothesis. Algebraic prediction: gap > 0.70 nats (HP).
   Pre-reg bands from research note: HP if gap > 0.70, MIDDLE if 0.40-0.70, HF if <= 0.40.
   Tier hint: rung-2 (CPU or GPU, short wall).

2. cf-RPE + STDP-asymmetric at trigram N=512
   Why now: secondary test confirming superadditivity extends to higher-order task; anchors
   architectural composition ceiling estimate. Follow-on to anchor 1 if HP1 passes.
   Tier hint: rung-2 to rung-3.

3. Drosophila sparse + STDP-asymmetric at bigram N=512
   Why now: weaker version of heterogeneous pairing; tests whether SNR-boost (sparse) + temporal
   (STDP) also compose superadditively, at lower magnitude than cf-RPE + STDP.
   Tier hint: rung-2 (CPU, short wall).

4. cf-RPE + position-binding at trigram N=512
   Why now: tests task x temporal composition at position-encoding axis (not transition-encoding).
   Bundle E already shows position-binding has independent temporal sub-axis vs STDP.
   Tier hint: rung-2 to rung-3.

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_cfrpe_sparse_shared_axis_negative_2x_2026-06-04.md
Bundle E results: check data/exp_*/metrics.json for position-binding + STDP trigram anchors
Bundle A baseline: substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu (cycle 67)

---

## CONTRACT

exp_dev ships the cheapest decisive test first (anchor 1 above). Anchor 2-4 are follow-ons
contingent on anchor 1 result. exp_dev pre-registers HP/MIDDLE/HF bands per research note
thresholds before queueing. No smoke pre-framing.

## AUTONOMY DECLARATION

exp_dev has full autonomy over: anchor naming, sweep grid, seed count, queue choice, timeout
formula, pre-reg band values, and implementation path. The research note provides algebraic
predictions as context; exp_dev is not bound to match them exactly.
