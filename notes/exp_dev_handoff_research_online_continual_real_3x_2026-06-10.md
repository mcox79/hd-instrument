# exp_dev hand-off -- research: online continual learning on real correlated data (3x)

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research drill identified 5 substrate-implementable mechanisms for the
correlated-data failure (frequency-decay 0.886->0.570; neurogenesis 54 shards/18 domains).
All 5 mechanisms are exp_dev-actionable at CPU rung, zero cloud required.
Research note: `notes/research_drill_online_continual_real_3x_2026-06-10.md`

**Pause state:** check `data/orchestrator_paused.flag` before dispatching any queue items.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS and
POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice
(Tier A/B/C), anchor name, ETA, smoke profile, full profile. Orchestrator does NOT specify
numerical parameters.

---

## What the research drill found

Correlated-data failure (0.886->0.570 recall; 54 shards/18 domains) has four identified
root causes, each with a corresponding substrate-native fix:

1. WRITE-INTO-CORRELATED-SUBSPACE: consecutive correlated items write to the same W axes,
   collapsing effective capacity. Fix: ZCA pre-whitening before outer-product write.

2. UNIFORM DECAY ON CORRELATED CLUSTERS: standard gamma applies equally to isolated atoms
   and clustered atoms. KWW physics says clustered atoms should decay slower (they protect
   each other). Fix: correlation-aware decay, gamma_i proportional to (1 - local rho_i).

3. NO MATURATION REFRACTORY PERIOD: new shards spawned from correlated items are wide-basin,
   never narrow, and immediately compete with neighbors. Fix: contextual neurogenesis with
   maturation timer; no new shard while an immature shard occupies the neighborhood.

4. DOMINANT-CORRELATION REPLAY BIAS: uniform replay over-samples the dominant correlation
   direction, starving rare orthogonal items. Fix: maximal-coverage greedy replay selection.

Biology proves all four are solvable (dentate gyrus, CLS, adult neurogenesis, SWR-gated
replay). P_deflated(ZCA alone) = 0.55. P_deflated(corr-aware decay alone) = 0.50.

---

## Anchor candidates (rank-ordered; exp_dev picks appropriate subset + queue routing)

### 1. ZCA-PREWHITEN-CORRELATED-STREAM
- Anchor pointer: research note Section E1 + Cheap decisive test.
- Substrate-product reading: ZCA pre-whitening before outer-product write on a 500-item
  correlated stream (5 domains, rho=0.7 intra-domain). Measures whether decorrelating
  input before storage recovers recall@1 from ~0.57 baseline to >0.80.
- Tier hint: local CPU (pure numpy, O(d^2) per write update, ~30 min).
- Why now: cheapest decisive test; if HARD-PASS, establishes the core fix without any
  architectural change; if HARD-FAIL, confirms dual-rate W_slow is required immediately.
- HARD-PASS: recall@1 > 0.80 on correlated stream.
- HARD-FAIL: recall@1 < 0.65 (< 0.08 improvement over baseline 0.57).

### 2. CORR-AWARE-DECAY-SWEEP
- Anchor pointer: research note Section E2 + Test 3 design.
- Substrate-product reading: per-atom decay rate gamma_i = gamma_base * (1 - alpha * rho_i).
  Sweep alpha in {0.3, 0.5, 0.7}. Measure retention R(200) on 200-item correlated stream.
  Tests whether KWW physics (clustered items decay slower) improves retention.
- Tier hint: remote CPU (multi-alpha sweep, 2 hr).
- Why now: directly addresses 0.570 failure; pure parameter change on existing decay infra.
- HARD-PASS: R(200) > 0.75 for at least one alpha.
- HARD-FAIL: R(200) < 0.60 for all alpha values.

### 3. CONTEXTUAL-NEUROGENESIS-MATURATION
- Anchor pointer: research note Section E3 + Test 2 design.
- Substrate-product reading: refractory period K_mature consolidation passes after shard
  spawn. No new shard while immature shard exists within cosine-sim neighborhood theta_young.
  Sweep K_mature in {5, 10, 20}. Target: shard count 54->< 15 without recall loss.
- Tier hint: remote CPU (multi-K sweep, 1 hr).
- Why now: directly addresses 54-shard fragmentation; bounded shard count required before
  any product demo on multi-domain data.
- HARD-PASS: shard count < 15 AND recall > 0.80.
- HARD-FAIL: shard count < 15 BUT recall < 0.65 (maturation too restrictive).

### 4. DECORRELATED-REPLAY-MAXCOVERAGE
- Anchor pointer: research note Section E5 + Test 4 design.
- Substrate-product reading: compare uniform random replay vs maximal-coverage greedy replay
  selection. Measure retention of minority-domain items (rare orthogonal items that are
  crowded out by dominant-correlation replay). Target: minority-item retention > 0.70.
- Tier hint: remote CPU (replay comparison, 3 hr).
- Why now: replay bias is the hidden cause of long-term degradation under continued writes;
  fixes slow drift that ZCA alone does not address.
- HARD-PASS: minority-item retention > 0.70 under decorrelated replay.
- HARD-FAIL: minority-item retention < 0.55 under decorrelated replay.

### 5. COMBINED-PIPELINE-RECALL-RESCUE (integration test)
- Anchor pointer: research note Section F + Test 5 design.
- Substrate-product reading: run ZCA + contextual neurogenesis maturation + corr-aware decay
  together on the specific dataset that produced the observed 0.570 failure. Tests whether
  the three mechanisms together recover > 0.80.
- Tier hint: remote CPU (half day; wait for anchors 1-3 to return verdicts first).
- Why now: gate on anchors 1-3 HARD-PASS. If any of {1, 2, 3} hard-fail, revise pipeline
  before running anchor 5.
- HARD-PASS: recall@1 > 0.80 on the observed 0.570 failure dataset.
- HARD-FAIL: recall@1 < 0.70 (combined fix insufficient -- dual-rate W_slow required).

---

## Context pointers (file paths only, no summaries)

- `notes/research_drill_online_continual_real_3x_2026-06-10.md` -- this drill's full note.
- `notes/research_drill_continual_full_cls_5x_2026-06-10.md` -- prior CLS 5-stream note.
- `notes/research_drill_continual_learning_revival_3x_2026-06-10.md` -- prior CLS revival note.
- `notes/substrate_capability_map.md` -- current cap_map; check continual-learning rows.

---

## Contract

exp_dev owns: anchor naming, queue assignment (Tier A/B/C), N/M/K/seed params, smoke
profile, full profile, pre-reg bands, dispatch order, and verdict interpretation.

Research owns: mechanism hypotheses, P_deflated estimates, HARD-PASS/HARD-FAIL thresholds
at the measurement level, and context pointers.

Orchestrator owns: queue depth policy, pause state, routing between agents.

## Autonomy declaration

exp_dev is fully autonomous on anchor design for all 5 candidates above. No additional
sign-off required from Research or Orchestrator before dispatch (pause flag permitting).
Run anchors 1-3 in parallel (independent mechanisms). Gate anchor 5 on verdicts from 1-3.
