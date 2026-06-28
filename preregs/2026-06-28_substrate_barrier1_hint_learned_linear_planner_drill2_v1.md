# Pre-registration -- substrate_barrier1_hint_learned_linear_planner_drill2_v1

**Date filed:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M; spawn from research task)
**Parent prereg:** `d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_substrate_derived_hint_v1.md`
**Sibling drills (HARD_FAIL precedents; same Barrier 1 / different mechanism class):**
- Drill 1: `substrate_partition_oracle_substrate_derived_hint_v1` (cosine centroid; route_acc=0.217 = chance)
- Drill 1.5: `substrate_partition_oracle_brain_composition_hint_v1` (3-primitive brain comp; HARD_FAIL)
- Drill A: `substrate_partition_oracle_pfc_wm_state_tracker_v1` (4-primitive PFC-WM; HARD_FAIL)
- Drill B: `substrate_partition_oracle_trajectory_schema_per_hop_v1` (per-hop schema-Bayes; HARD_FAIL)

**Task:** Drill 2 of 2x-drill-before-closure for Barrier 1 hint-derivation. Tests
**Option B (learned linear partition planner)** as a genuinely DIFFERENT mechanism class
(supervised learned linear projector) from prior cosine/schema/state-track attempts.

## Anchor names (3 chunked sibling cells; one seed each)

- `substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_7`
- `substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_13`
- `substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_19`

## Cell files

- `d:/AI/hd-instrument/experiments/exp_substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_7.py`
- `d:/AI/hd-instrument/experiments/exp_substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_13.py`
- `d:/AI/hd-instrument/experiments/exp_substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_19.py`

## Motivation (functional-requirement-first per USER 2026-06-28)

Drill 1 (cosine centroid `argmax(C @ state)`) FAILED with route_acc=0.217 (chance
for 5 partitions = 0.20). The mechanism was UNTRAINED: the centroid `C[p] =
normalize(mean(E_part[p] @ W))` assumes the W-output state at hop i naturally
clusters near the target partition's centroid. **Smoke confirmed this assumption
is false** -- multihop W @ key state at any hop i carries near-zero partition
information when read via cosine to per-partition mean.

**This drill tests a strictly stronger mechanism class:**

A supervised learned linear classifier `W_planner: (N=8192) -> (N_PART=5)`
trained on `(state_hop_i, true_partition_at_hop_i)` pairs from a TRAINING CHAIN
SPLIT. At test time, `pred_part = argmax(W_planner @ state)`. This is the SAME
signal-shape oracle B receives (state = W @ key) but the readout is now a learned
linear function trained to maximize partition_acc via cross-entropy (sklearn
logistic regression or gradient descent on softmax cross-entropy).

**Why this is mechanism-class DIFFERENT from prior drills:**
- Drill 1 used a *fixed* readout (per-partition mean centroid -- cosine; no
  training signal).
- Drill 1.5/A/B used *handcrafted* composition (3-4 brain primitives; no
  training signal).
- Drill 2 uses *supervised learning* over the training-chain partition labels.
  If any low-SNR partition cue exists in the W @ key state, learned W_planner
  CAN extract it; cosine baselines CANNOT (cosine assumes uniform partition
  prior + zero learned weight).

**M3 interpretation if HARD_PASS:** learned planner is a viable candidate
mechanism for M3 Phase 1.5 (substrate-native learned planner, not requiring
LLM-in-loop). The mechanism is bounded by Bacon-Roy option-critic (heavier RL
hierarchy) on the complexity axis; if linear is enough, no need for the option
hierarchy.

**M3 interpretation if HARD_FAIL:** strong joint evidence with Drills 1/1.5/A/B
that the multihop_query signal at depth-d carries NO recoverable partition-
routing information beyond the entity-identity cue. Atomize Barrier 1 hint-
derivation as CLOSED with mechanism-class-2 negative (cosine + composition +
supervised linear ALL fail). Pivot recommendation: external LLM cortex layer
(M3 Phase 1) is the LOAD-BEARING path; no substrate-internal shortcut exists.

## Source citations (ABSOLUTE PATHS; META_RULE_AE)

- This prereg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_barrier1_hint_learned_linear_planner_drill2_v1.md`
- Drill 1 prereg (parent): `d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_substrate_derived_hint_v1.md`
- Drill 1 smoke metrics (HARD_FAIL evidence; route_acc=0.217):
  `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7_smoke/metrics.json`
- Chain-grade oracle reference (ground-truth upper bound):
  `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1/metrics.json`
- Functional-requirement-first directive: `feedback_functional_requirement_first_test_design_USER_2026-06-28.md`
- M3 architecture decision (USER 2026-06-28): `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.md`
- DISCRIMINATOR-MUST-SURVIVE-SCALE: `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md`
- META_RULE_AP_v3 signal-shape audit: `feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27.md` (related discipline)

## Number tagging (META_RULE_AC)

- MEASURED@DRILL1_ROUTE_ACC_SMOKE: 0.2173 (5-partition chance = 0.20; cosine
  centroid IS chance at d=15)
- MEASURED@DRILL1_ARM_B_TOP1: 0.0000 (collapse after wrong-partition cleanup)
- MEASURED@DRILL1_ORACLE_C_SMOKE: 0.8400 (ground-truth oracle upper bound)
- MEASURED@DRILL1_BASELINE_A_SMOKE: 0.4000 (no-hint baseline; full V_C cleanup)
- HYPOTHESIZED@HP_PLANNER_ROUTE_ACC: >= 0.50 (linear classifier extracts ANY
  signal above chance; if no signal, fails strictly)
- HYPOTHESIZED@HP_ARM_B_TOP1: in [0.50, 0.95] (oracle is 0.84; planner with
  route_acc=0.50 should reach 0.50+; with route_acc=0.80+ should reach 0.70+)
- HYPOTHESIZED@HP_LIFT_OVER_BASELINE: >= 0.30 (real signal vs no-hint baseline)
- HYPOTHESIZED@HP_LIFT_OVER_RANDOM: >= 0.30 (vs random partition floor)
- HYPOTHESIZED@HP_GAP_ORACLE: <= 0.30 (planner retains most of oracle's lift)
- HYPOTHESIZED@HP_NOISY_SANITY: |D - A| <= 0.10 (negative control matches base)
- HYPOTHESIZED@POSITIVE_CONTROL_DELTA: at smoke (d=5, N_part=10), planner
  route_acc >= 0.50 (well above chance=0.10); IF FAILS, mechanism BROKEN OR
  query carries zero signal -- triggers immediate STOP before full dispatch
- THEORETICAL@CHANCE_ROUTING_5_PART: 0.20
- THEORETICAL@CHANCE_ROUTING_10_PART: 0.10

## Arms (5; mirror Drill 1 for clean delta interpretation)

| Arm | Mechanism | Role |
|---|---|---|
| A: BASELINE | argmax over V_C=4000 (no hint) | Baseline rail; expected ~0.40-0.45 |
| B: LEARNED_PLANNER | argmax(W_planner @ state) trained on (state, part) pairs | **Drill 2 M3-usable mechanism** |
| C: ORACLE | ground-truth partition (gen-time peek) | Upper-bound positive control |
| D: NOISY_HINT | randomly permuted partition labels at query time | Negative control (~baseline) |
| E: RANDOM | random partition pick per hop | Floor (~0) |

**Planner training (the new content vs Drill 1):**
- For each TRAINING chain c in chains_train (N=200), at each hop i in 0..DEPTH-1:
  - Compute `state = W @ (E[s_i] * R[p_i] * sq)` where (s_i, p_i, o_i) = c[i]
  - Record `(state, true_part = o_i // PART_SIZE)`
- Total training pairs: ~200 chains x 15 hops = 3000 (state, label) pairs
- Train linear softmax classifier `W_planner: R^N -> R^N_PART` via sklearn
  LogisticRegression (multinomial; lbfgs; max_iter=200; C=1.0 default L2)
- At TEST time, identical to Drill 1 arm B but `pred_part = argmax(W_planner @ state)`

## Train/test disjointness verification (mandatory)

- chains_train uses `disallow_s=set()` (default)
- chains_test uses `disallow_s = set(c[0][0] for c in chains_train)` -- ensures
  test-chain starting entities are disjoint from train-chain starting entities
- Assert in code: `anchor_set_intersection = set(c[0][0] for c in chains_train) & set(c[0][0] for c in chains_test); assert len(anchor_set_intersection) == 0`
- Additionally: training (state, label) pairs come ONLY from chains_train; planner
  is FROZEN before any chains_test forward pass; verified by frozen-W_planner
  weight checksum logged

## Signal-shape audit (META_RULE_AP_v3)

- Oracle B (test): `state = W @ (E[s_i_test] * R[p_i_test] * sq)`
- Drill 2 planner (training): `state = W @ (E[s_i_train] * R[p_i_train] * sq)`
- Drill 2 planner (test): `state = W @ (E[s_i_test] * R[p_i_test] * sq)`
- IDENTICAL signal-shape across train/test/oracle: same W, same E/R encoders, same
  binding formula. The planner sees the SAME state-vector geometry it will
  receive at test time. No cleaner-than-test signal leak.
- Assertion logged: `state_test.shape == state_train.shape == (N_DIM,)`

## Pre-reg bands (META_RULE_AL; LOCKED at module init)

### Baseline rail (BIAS-S sanity)
- ARM_A.top1@d15 in [0.30, 0.70] (matches Drill 1 BASELINE=0.40)

### HARD_PASS (chain-grade-eligible; learned planner real)
- ARM_B.top1@d15 in [0.50, 0.95]  (un-saturated; META_RULE_AG)
- AND ARM_B.top1@d15 - ARM_A.top1@d15 >= 0.30
- AND ARM_B.top1@d15 - ARM_E.top1@d15 >= 0.30
- AND ARM_C.top1@d15 - ARM_B.top1@d15 <= 0.30
- AND |ARM_D.top1@d15 - ARM_A.top1@d15| <= 0.10
- AND saturation == False (HP_SATURATION_CEIL = 0.95)
- AND arms_distinct == True via SHA-256 (META_RULE_AF)
- AND positive_control_pass == True (smoke at d=5 N_part=10 planner_route_acc >= 0.50)
- AND train_test_disjoint == True (assertion checksum)
- AND cv(ARM_B across seeds) < 0.15 (enforced post-hoc across 3 sibling cells)

### HARD_FAIL
- ARM_B.top1@d15 <= 0.30
- OR planner_route_acc@d15 < 0.30 (planner cannot improve on chance + margin)
- OR (ARM_B.top1@d15 - ARM_A.top1@d15) < 0.10
- OR positive_control_pass == False at SMOKE (mechanism broken OR no signal)

### MIDDLE_BAND
- ARM_B in [0.30, 0.50) with lift_b_a >= 0.15
- OR HP-band hit BUT lift_b_a in [0.15, 0.30) (partial signal)
- OR planner_route_acc in [0.30, 0.50) (above chance but below HP)

## Cardinality (META_RULE_H)

- per cell: 5 arms x 1 seed = 5 units
- Cross-cell (post-hoc): 5 arms x 3 seeds = 15 units (cv computed)
- EXPECTED_N_UNITS = 5 per cell
- HARD_FAIL_CARDINALITY_BREACH if observed != expected

## Configuration

- N=8192, V_C=4000, V_P=10, DEPTH=15 (LOCKED -- matches Drill 1 regime)
- N_PART=5, PART_SIZE=800 (matches Drill 1)
- N_CHAINS_TRAIN=200 (provides 200*15=3000 planner training pairs)
- N_CHAINS_TEST=200 (full); 100 (smoke)
- POSITIVE_CONTROL config: at module init, run a separate d=5 / N_part=10 / 500
  training chains / 100 test chains planner training + eval; assert
  planner_route_acc >= 0.50; if fails, abort before full ingest.
- Encoder: SUBSTRATE_NATIVE_BIPOLAR (matches parent chain)
- Planner: sklearn LogisticRegression(multi_class='multinomial', solver='lbfgs',
  max_iter=200, C=1.0, random_state=seed)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: ORACLE_C must be > 0.50 to confirm
  upper bound exists; if ORACLE_C < 0.50 the regime is broken and cell HARD_FAIL

## Smoke gate (DISCRIMINATOR-MUST-SURVIVE-SCALE)

Smoke runs seed=7 at FULL N=8192 + FULL depth=15 (matches Drill 1 smoke).
n_chains_test=100 for ~5-8 min wall (includes planner training).

**Smoke MUST FIRE discriminator, not just verify cell runs:**
1. POSITIVE CONTROL gate FIRST (small d=5 / N_part=10):
   - planner_route_acc_pc >= 0.50 (well above chance=0.10)
   - IF FAILS: abort + report MECHANISM_BROKEN_OR_NO_SIGNAL_AT_EASIER_REGIME
2. Full-N (d=15 / N_part=5) discriminator:
   - planner_route_acc >= 0.30 (above chance=0.20 + margin)
   - ARM_B - ARM_A >= 0.30 (real signal)
   - OR fail with EVIDENCE-CLASS-2-NEGATIVE_AT_FULL_SCALE

**Smoke pass requires BOTH gates pass.** If positive control passes but
full-N discriminator fails: that's the load-bearing finding (signal too low-SNR
to extract at full depth with linear planner) -- HARD_FAIL still appropriate.

## Compute estimate

- Cell wall: ingest (~5s for 6000 triples) + planner train (3000x8192 logreg
  ~30-90s) + 5 arms x 200 chains x 15 hops x cleanup (~3 min) + positive control
  (~30s) = ~5-8 min smoke; ~10-12 min full.
- Per-cell timeout: 4500s (1.25h; same as Drill 1 cells; safety margin)

## Routing

- Smoke: local CPU (seed=7; ~8 min)
- Full per seed: remote_cpu_queue (timeout 4500s each)
- Queue currently empty (verified `queue_status.py`: remote_cpu pending=0)

## Discipline tags

- META_RULE_AC/AE/AF/AG/AH/AL/AN/H all enforced (inherited from parent)
- META_RULE_AP_v3: signal-shape audit documented + asserted
- BIAS-Q saturation guard @ 0.95
- BIAS-N: per-arm metrics in summary
- BIAS-S: baseline rail [0.30, 0.70]
- DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at FULL N + FULL depth + positive control
- PROT-018: anchor binds regime in CONFIG_VERSION
- Fix #28: per-arm reads from metrics.json
- substrate-as-canonical query first: verified Drill 1's chance-routing finding
  (route_acc=0.217) before designing trained-planner alternative
- 2x-drill-before-closure (USER standing): Drill 2 is mechanism-class-DIFFERENT
  (supervised learned linear) vs Drills 1/1.5/A/B (cosine + handcrafted comp);
  if both Drill 2 + future Bacon-Roy option-critic fail, closure justified
- HARD_FAIL_CARDINALITY_BREACH enforced (META_RULE_H)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: ORACLE_C > 0.50 floor + ARM_B < 0.95 ceiling
- _start_marker.json + _crash_diagnostic.json + per-seed checkpoint + heartbeat
  (§13 patterns via _seed_checkpoint + _cell_heartbeat)
- No silent except: blocks (verify in selftest; SystemExit re-raised before
  BaseException)

## Strategic reading

- **IF HARD_PASS across all 3 sibling seeds**: learned linear planner is the
  Barrier 1 chain-grade break (M3-usable; no LLM-in-loop required for Phase 1.5
  routing). Atomize as chain-grade promotion. Pivot M3 architecture: Phase 1
  LLM cortex remains as outer-loop intent translator, but per-hop planning can
  be substrate-native learned linear.
- **IF MIDDLE_BAND**: planner provides partial signal; gap to ground-truth
  oracle wider than 0.30; iterate (Bacon-Roy option-critic for non-linear
  planning OR augment state with multi-hop history vector).
- **IF HARD_FAIL with positive control PASS**: linear planner works at easy
  regime (d=5 / N_part=10) but signal vanishes at d=15 / N_part=5. STRONG joint
  evidence Barrier 1 hint-derivation impossible from substrate state alone at
  full regime. Triggers Drill 3 (Bacon-Roy option-critic; non-linear) OR
  capability closure with M3 LLM-cortex as load-bearing.
- **IF HARD_FAIL with positive control FAIL**: mechanism BROKEN -- cell-author
  error; do not interpret as substrate-impossibility.
