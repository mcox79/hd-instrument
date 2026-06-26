# Pre-reg: gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7

**Authored:** 2026-06-26 (exp_dev under autonomous YOLO; Research-routed handoff)
**Anchor:** `gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7`
**Cell:** `experiments/exp_gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7.py`
**Routing:** `remote_cpu_queue` (USER directive 2026-06-26: local CPU saturated; remote queues idle)
**Timeout:** 14400s (4h; PROT-021 checkpoint-required)

## What this cell tests

Cell B v2 PART_ORACLE_5HOP=0.9550 cleared chain-grade band BUT carried a BIAS-P scope flag:
the partition router used `target_part = target_o // part_sz` -- i.e. ORACLE-routed (knows the
ground-truth target partition). USER asked: "why can't we use bidirectional to tell us where
it is for the 1st method?" Research drilled 5 mechanism classes across information theory,
hippocampal CA3, pulvinar, mushroom body / fly-LSH, and learned closed-form routers. USER's
steelman ranked #1; fly-LSH ranked #2 (cheap decisive alternative).

This cell BUNDLES anchors 1+2 (sharing `_forward_state` / `_backward_state` / `fly_lsh_expand`
infrastructure already proven in Cell B v2 + Cell C v2).

**Architecture decision (post-smoke design refinement 2026-06-26):**

All THREE candidate routers operate as CHAIN-MONOLITHIC endpoint routers (not per-hop).
Reason: per-hop bidir-collide via E[s] . backward_walk_one_step(Z, p) is mathematically
equivalent to forward argmax modulo Hebbian symmetry -- it gives same per-partition sum
as naive centroid (sum vs mean argmax-equivalent up to normalization). Smoke confirmed:
per-hop bidir = per-hop naive = 0.7400 (identical metrics). To genuinely test USER's
intuition, all 3 router arms operate at the CHAIN ENDPOINT level using full forward and
multi-predicate backward walks. This is apples-to-apples with Cell C v2 BIDIR_MEET_MID
(which scored full V_C with no partition routing). All 3 arms can now diverge based on
mechanism rather than degenerate to same math.

**Anchor 1 (USER steelman):** ARM_PART_BIDIR_COLLIDE_5HOP (chain-monolithic meet-in-middle)
- state_fwd_mid = _forward_state(S, preds[:mid])  # mid=depth/2
- state_fwd_full = _forward_state(S, all preds)
- For each candidate chain-endpoint Z:
    state_bwd_Z = _backward_state(E[Z], preds[mid:])   # backward (depth-mid) hops
    cos_Z = state_fwd_mid . state_bwd_Z
- For each partition p: score_p = sum_{Z in part_p} cos_Z
- predicted_endpoint_part = argmax_p score_p
- Within-partition cleanup: argmax(E_parts[predicted] @ state_fwd_full)
- Substrate-native: uses _forward_state + _backward_state from Cell C v2; multi-predicate
  backward walk gives nonlinear discriminative signal distinct from naive centroid.

**Anchor 2 (cheap-decisive):** ARM_PART_FLY_LSH_5HOP (chain-monolithic LSH router)
- state_fwd_full = _forward_state(S, all preds)
- state_lsh = fly_lsh_expand(state_fwd_full, projs)
- c_lsh_p = sum_{Z in part_p} fly_lsh_expand(E[Z]) (normalized)
- predicted_endpoint_part = argmax_p (state_lsh . c_lsh_p)
- Within-partition cleanup: argmax(E_parts[predicted] @ state_fwd_full)
- Substrate-native: uses fly_lsh_expand from Cell B v2; mushroom-body sparse projection.

**Falsification anchor:** ARM_PART_NAIVE_CENTROID_5HOP (chain-monolithic naive centroid)
- state_fwd_full = _forward_state(S, all preds)
- centroid_p = mean(E[Z] : Z in part_p), normalized
- predicted_endpoint_part = argmax_p (state_fwd_full . centroid_p)
- Within-partition cleanup: argmax(E_parts[predicted] @ state_fwd_full)
- Cell C v2 PROBE measured mean_midpoint_cosine=0.0000 -> expect FAIL.

## Arms (7)

| Arm | W | Routing mechanism | Target band |
|---|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep (400 bindings) | n/a (2-hop) | [0.62, 0.68] sanity |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | W_pointer_v2 (2000 bindings; max_depth=10) | n/a (forward-only) | **[0.08, 0.25] META_M7 rail** |
| ARM_SINGLE_TOP1_5HOP | W_v1_regime (1000) | n/a (forward-only) | informational (v1 ~0.275) |
| ARM_PART_ORACLE_5HOP | W_v1_regime (1000) | `target_o // part_sz` (oracle) | **cross-cell sanity: Cell B v2 PART=0.9550 +/- 0.02** |
| ARM_PART_BIDIR_COLLIDE_5HOP | W_v1_regime (1000) | argmax_p sum_Z_in_p state_fwd . state_bwd(Z) | **PRIMARY: >= 0.80 for HARD_PASS** |
| ARM_PART_FLY_LSH_5HOP | W_v1_regime (1000) | argmax_p state_fwd_lsh . centroid_lsh_p | **PRIMARY: >= 0.80 for HARD_PASS** |
| ARM_PART_NAIVE_CENTROID_5HOP | W_v1_regime (1000) | argmax_p state_fwd . centroid_p | <= 0.40 expected (falsification) |

## SACRED SANITY rails (verdict pre-emption on majority-seed breach)

- `RAIL_BASELINE`: BASELINE NOT in [0.62, 0.68] on majority of seeds -> `SANITY_BREACH`
- `RAIL_META_M7`: REPRODUCE NOT in [0.08, 0.25] on majority -> META_M7 breach flag
  (surfaces in `HARD_PASS_..._WITH_META_M7_NOTE`; does not pre-empt)
- `RAIL_CROSS_CELL_PART_ORACLE`: ARM_PART_ORACLE diverges from Cell B v2 0.9550 by > 0.02
  on majority of seeds -> `CROSS_CELL_DRIFT` flag in verdict_msg (informational; not blocking)

## Verdict ladder (LOCKED via module-init asserts)

Composite verdict from BOTH router arms:

- `HARD_PASS_CHAIN_GRADE_BOTH_ROUTERS`:
  - PART_BIDIR_COLLIDE >= 0.80 AND PART_FLY_LSH >= 0.80 AND
  - cv <= 0.07 for both AND META_M7 OK
  - Headline: BOTH bidirectional-collide AND fly-LSH route per-hop without oracle;
    Gap 1 BIAS-P removed via TWO independent substrate-native paths.

- `HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER`:
  - PART_BIDIR_COLLIDE >= 0.80 AND cv <= 0.07 AND META_M7 OK AND PART_FLY_LSH < 0.80
  - Headline: USER intuition validated; bidirectional middle-state IS the substrate-native
    routing signal; fly-LSH does not match.

- `HARD_PASS_CHAIN_GRADE_LSH_ROUTER`:
  - PART_FLY_LSH >= 0.80 AND cv <= 0.07 AND META_M7 OK AND PART_BIDIR_COLLIDE < 0.80
  - Headline: substrate routes via sparse-binary fingerprint of forward state; brain-grounded
    mushroom-body analog.

- `HARD_PASS_WITH_META_M7_NOTE`: either router >= 0.80 but META_M7 not in band; regime gap surfaced.

- `HARD_FAIL_ROUTING_NOT_VIABLE`:
  - PART_BIDIR_COLLIDE <= 0.50 AND PART_FLY_LSH <= 0.50
  - Headline: substrate cannot route to partition without oracle via either path;
    Gap 1 BIAS-P stands; pivot to Anchor 5 (closed-form pseudoinverse) or accept
    oracle as substrate capability framing ("named-partition retrieval").

- `MIDDLE_BAND_ROUTING_PARTIAL`: at least one router arm in [0.50, 0.80); route 2x drill for
  refinement variants (max-instead-of-sum, deeper back-walks).

## Discriminator emphasis (per handoff requirement)

verdict_msg MUST explicitly state which arm (if any) removes the BIAS-P scope flag from
Cell B v2's 0.9550. Format string includes one of:
- `BIAS_P_REMOVED_VIA_BIDIR_COLLIDE`
- `BIAS_P_REMOVED_VIA_FLY_LSH`
- `BIAS_P_REMOVED_VIA_BOTH_INDEPENDENT_PATHS`
- `BIAS_P_STANDS_NEITHER_ROUTER_VIABLE`

## Config

**FULL mode:**
- N=8192, V_C=200, V_P=10, K_SET=20
- Seeds [7, 17, 23] (apples-to-apples with Cell B v2 + Cell C v2)
- W_pointer_v2: n=200 chains, max_depth=10 -> 2000 bindings
- W_v1_regime: n=200 chains, max_depth=5 -> 1000 bindings
- M=1000 (test pool); n_chains=200 (test chains)
- N_PARTITIONS=20, PART_SIZE=10
- N_LSH_EXPANSIONS=5, LSH_TOPK=20
- Test depth=5

**SMOKE mode:**
- N=2048, V_C=200, seeds [7]
- W_pointer_v2: n=100 max_depth=10 -> 1000 bindings
- W_v1_regime: n=50 max_depth=5 -> 250 bindings
- 50 test chains

## Self-test (T1-T9; module-init blocks dispatch if any fails)

- T1: BASELINE 2-hop arm returns 0.0 <= top1 <= 1.0
- T2: REPRODUCE arm uses 2000-binding W; returns 0.0 <= top1 <= 1.0
- T3: SINGLE_TOP1 arm uses 1000-binding W; returns 0.0 <= top1 <= 1.0
- T4: PART_ORACLE arm reproduces Cell B v2 mechanism; per-hop math byte-identical
- T5: PART_BIDIR_COLLIDE arm runs without error; top1 in [0, 1]
- T6: PART_FLY_LSH arm runs without error; top1 in [0, 1]
- T7: PART_NAIVE_CENTROID arm runs; top1 in [0, 1]
- T8: bands locked (HP_THRESHOLD=0.80, HF_THRESHOLD=0.50; META_M7=[0.08, 0.25])
- T9: LLM call counter == 0 (substrate-only)

## Estimated runtime

- BASELINE: ~7s/seed (2-hop, small W)
- REPRODUCE + SINGLE: ~20s + ~20s/seed (forward-only)
- PART_ORACLE: ~19s/seed (Cell B v2 numbers)
- PART_BIDIR_COLLIDE: dominant cost = n_chains * depth * V_C * O(N^2) for backward walks
  = 200 * 5 * 200 * 8192^2 / 200 = ~6.7e10 ops/seed... Actually per-hop scoring is
  V_PARTS=20 * PART_SIZE=10 = 200 backward walks per hop, each (depth-mid) hops of N^2 matmul.
  Estimate ~1200s/seed (same envelope as Cell C v2 BIDIR_MEET_MID which scored full V_C).
- PART_FLY_LSH: ~30s/seed (Research estimate; fly-LSH expansion + dot products)
- PART_NAIVE_CENTROID: ~5s/seed (centroid + dot product per hop)

Total per seed: ~1300s; 3 seeds = ~3900s + safety = **14400s timeout** (PROT-021 checkpoint required).

## What this cell answers

- `HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER`: USER intuition is correct; substrate routes without
  oracle via bidirectional collision. Substrate-product story: "Substrate retrieves multi-hop
  facts by bidirectional routing -- forward walk meets backward-reflected per-candidate states;
  no learned router; no oracle; chain-grade." Route to Skunkworks for landed-VET TIER A.
- `HARD_PASS_CHAIN_GRADE_LSH_ROUTER`: fly-LSH routes per-hop; substrate-product story:
  "Substrate routes via sparse-binary fingerprint -- substrate-native mushroom-body analog."
- `HARD_PASS_CHAIN_GRADE_BOTH_ROUTERS`: two INDEPENDENT substrate-native routing paths;
  follow-up cell `gap1_partition_routing_two_stage_bidir_lsh_v1` (Research Anchor 3) becomes valuable.
- `HARD_FAIL_ROUTING_NOT_VIABLE`: substrate genuinely needs learned router; route to
  Research for Anchor 5 (closed-form pseudoinverse) or pivot to named-partition retrieval framing.

## Risk register (Fix #26 verify-the-referent + USER bias checklist)

- BIAS-Q (suspect 1.000): per-step_acc reported per-arm; if any depth=5 per-step hits 1.00
  at V_C=200, flag W-saturation in verdict_msg
- BIAS-P (anisotropy / oracle routing): PART_ORACLE arm intentionally USES oracle (Cell B v2
  cross-cell sanity rail). All NEW router arms are oracle-free; that's the THING being tested.
- BIAS-N (verify referent): cross-cell PART_ORACLE drift flag fires if mean diverges from
  Cell B v2 0.9550 by > 0.02
- Fix #28: per-arm metrics fully reported (top1 + per_step_acc + per-hop routing diagnostics)
- META_M7: REPRODUCE_PV2 in [0.08, 0.25] is the rail; if breaks, router HPs carry META_M7 note
- BIAS-O (basis vs use-case): partition routing is a use-case readout on top of W's substrate basis
- Substrate-native discipline: zero new primitives; zero LLM forward calls; zero gradient updates
