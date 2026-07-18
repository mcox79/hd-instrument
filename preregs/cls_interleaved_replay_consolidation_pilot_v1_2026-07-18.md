# Pre-reg: exp_cls_interleaved_replay_consolidation_pilot_v1

Filed 2026-07-18 (exp_dev). Cell: `experiments/exp_cls_interleaved_replay_consolidation_pilot_v1.py`.
Metrics: `data/exp_cls_interleaved_replay_consolidation_pilot_v1/metrics.json`. CPU, self-contained numpy, glass-box.

## Question
Does the PROPER Complementary-Learning-Systems (CLS) loop -- architectural separation + interleaved-replay
consolidation + fast/slow schema-fit routing -- prevent catastrophic interference and beat BOTH (a) a
single shared store (McCloskey-Cohen failure mode) AND (b) the naive dual-W attempt that already
HARD_FAILED (`exp_two_substrate_fastslow_cls_cpu_v1`, old-consolidated recall 0.378)?

## Why the naive attempt failed (brain-check that motivated the redesign)
The naive cell's stores are pure additive Hebbian BUNDLES (single superposed complex vectors). On a
commutative additive bundle, (1) interleaved replay is a MATHEMATICAL NO-OP (order-independent sum) and
(2) superposition crosstalk from cramming thousands of items into one vector is the killer. That is the
McCloskey-Cohen single-shared-store failure mode at the storage level -- NOT a refutation of the CLS
principle. A faithful pilot therefore requires an ERROR-CORRECTING store with a SHARED distributed
representation (the exact thing neocortex is, and the exact thing interleaved replay exists to protect).
CITED@ McClelland-McNaughton-O'Reilly 1995; Kumaran-Hassabis-McClelland 2016; McCloskey-Cohen 1989.

## Design (ONE new variable = interleaved replay)
Class-incremental continual learning. K_BLOCKS=10 blocks, CPB=4 new classes/block (V=40), IPC=10
items/class, T=400 items, keys = N=128 bipolar hypervectors. Slow store = shared-hidden-layer net
(N->H=64->V, tanh, softmax) trained by batch backprop, E_EPOCHS=120, LR=0.3. Fast tier = exact
pattern-separated episodic buffer of the most-recent block (hippocampal one-shot). Recall routes
fast(exact, cos>=0.999)-then-slow. old = block 0; recent = last block.

2x2 ablation that LOCALIZES which half is load-bearing (Falsifiable-Prediction #2):

|              | no replay                        | interleaved replay          |
|--------------|----------------------------------|-----------------------------|
| no fast tier | single_seq (McCloskey base a)    | replay_only (ablation)      |
| fast tier    | naive_dual_w (HARD_FAILED base b)| full_cls (mechanism)        |

naive_dual_w and full_cls are IDENTICAL except full_cls interleaves a random replay sample of
already-seen items at each consolidation step -> clean one-variable isolation of the replay half.

## Design-gate (verified at smoke BEFORE full)
- REAL baselines: single_seq and naive_dual_w both genuinely forget old (not strawman/abstain).
- CAN-FAIL: HARD_FAIL_REPLAY_HALF_INEFFECTIVE fires if full_cls old-recall <= naive + 0.05.
- DIFFICULTY-ON: single_seq old-recall <= 0.40 (catastrophic forgetting real) AND recent >= 0.60
  (it CAN learn -> the low old-recall is forgetting, not inability). Forgetting deepens with block
  count, so smoke/self-test run the FULL K_BLOCKS regime (not reduced) per DISCRIMINATOR-MUST-SURVIVE-SCALE.
- ONE variable: naive_dual_w vs full_cls differ only by replay.
- No held-out generalization claim: target is RETENTION of trained associations, so replaying
  already-seen training items is the legitimate CLS mechanism, NOT a label leak.

## Bands (envelope-fail-bands)
- HARD-PASS (>=2/3 seeds): full_cls old-recall >= 0.70 AND recent >= 0.70 AND old-recall beats BOTH
  single_seq and naive_dual_w by >= 0.20.
- CAN-FAIL / HARD-FAIL (first-class, informative): full_cls old-recall <= naive + 0.05 -> replay half
  not load-bearing; missing ingredient localizes to REPLAY vs separation. Brain-check pre-specified:
  if replay does not help, the store is not sharing units / not actually interfering -> re-check difficulty.
- MIDDLE_BAND: full_cls beats both but below the 0.20 margin / 0.70 floor on the seed bar (tuning).
- Feasibility: interleaved(joint) ceiling (replay_only) is the reachable ceiling; measured ~0.82-0.85 >
  0.70 floor. crlb_n/a (retention accuracy, no argmax-noise floor).

## Result (MEASURED@ data/exp_cls_interleaved_replay_consolidation_pilot_v1/metrics.json)
VERDICT = HARD_PASS, 3/3 seeds. full_cls old=0.808 recent=1.000; naive_dual_w old=0.217;
single_seq old=0.217; replay_only old=0.817. margin vs both baselines = 0.591 (>> 0.20).
Per-seed full_cls old = {0.825, 0.825, 0.775}; naive/single = {0.125, 0.25, 0.275}. arms_differ=True.

## Localization (pre-specified brain-check)
Interleaved REPLAY is the load-bearing half: replay_only (0.817) ~ full_cls (0.808); the
separation-only arm (naive_dual_w, 0.217) = single_seq (0.217). The fast/separation tier contributes
recent-item EXACTNESS (recall=1.000 by construction) but not old-item retention. This matches CLS
biology: the hippocampal fast tier gives immediate access to recent episodes, while interleaved SWR
replay is specifically what protects distributed neocortical memories from being overwritten.

## Status
CLAIM-VET-pending (landed-VET by skunkworks required before chain-grade). NOT self-declared chain-grade.
Pause was ACTIVE: ran INLINE (local foreground, ~2s), no queue dispatch.
