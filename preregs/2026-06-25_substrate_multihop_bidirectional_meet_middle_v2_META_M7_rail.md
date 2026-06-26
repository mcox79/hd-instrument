# Pre-reg: substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail

**Authored:** 2026-06-25 (exp_dev under autonomous YOLO; Director-routed redispatch)
**Anchor:** `substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail`
**Cell:** `experiments/exp_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail.py`
**Routing:** `local_cpu_queue`
**Timeout:** 14400s (4x v1's 3600s -- v1 timed out at 3600s with seed 7 partial; the
V_C=200 candidate-ranking arm in BIDIR_MEET_MID is the dominant cost: 2687s alone;
3 seeds estimated ~8500-9000s total; 14400s is the queue_add.sh cap and provides
safety margin to land all 3 seeds without re-dispatch)

---

## V1 ISSUES

### Issue 1: same META_M7 problem as Cell B v1

Cell C v1 SINGLE_CHAIN_5HOP_FORWARD rail (seed 7 partial) = **0.275**.
Pointer-chain v2 forward-only depth-5 rail = **0.122**.
Both use ALGORITHMICALLY IDENTICAL `_retrieve_1hop` cleanup primitive.

| | Cell C v1 | pointer-chain v2 |
|---|---|---|
| n_chains | 200 | 200 |
| max_depth | **5** | **10** |
| W bindings | **1000** | **2000** |
| Crosstalk per (s,p) pair | ~lower | ~2x higher |

Same regime diff as Cell B v1. Cell C v1's BIDIRECTIONAL_MEET_MID = 0.67 lift
over 0.275 SINGLE_FWD is honest within-cell, but cannot honestly claim
"bidirectional revives Barrier 1 from 0.122 to 0.67" without META_M7 verification.

### Issue 2: ARM_BIDIRECTIONAL_MEET_HOP2 produced NaN

V1 source line 312: `"top1": float("nan")` for the probe arm (intentional --
probe arm has no classification top1; it's a state-cosine sanity check).
BUT NaN is NOT valid JSON. The partial file serialized it as bare `NaN`
which most JSON parsers reject. The arm's actual signal lives in
`mean_cosine_at_midpoint` + `median_cosine_at_midpoint`.

**V2 FIX:** `top1: None` (JSON null) + `is_probe_arm: True` flag.

## V2 ADDS

1. **ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP** (META_M7 rail): builds a SEPARATE
   `W_pointer_v2` from `make_deep_chains(n=200, V_P=10, max_depth=10)` ->
   2000 bindings (pointer-v2 exact regime). Test at depth=5 using verbatim
   `_retrieve_1hop` (same primitive as SINGLE_CHAIN_5HOP_FORWARD arm; ONLY the
   W matrix differs). Target band [0.08, 0.25].

2. **NaN fix** in ARM_BIDIRECTIONAL_MEET_HOP2 (top1: None instead of NaN).

3. **Longer timeout** (7200s) lets the V_C=200 candidate-ranking arm complete
   for all 3 seeds.

## Arms (5)

| Arm | W | Config | Target |
|---|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep W (400 bindings) | n=200 2-hop, V_P=2 | [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | W_pointer_v2 (2000) | depth=10 ingest; depth=5 test | **[0.08, 0.25] META_M7 rail** |
| ARM_SINGLE_CHAIN_5HOP_FORWARD | W_v1_regime (1000) | depth=5 | (v1 rail 0.275; informational) |
| ARM_BIDIRECTIONAL_5HOP_MEET_HOP2 | W_v1_regime (1000) | probe arm; cosine only | top1=None; cosine in [-1, 1] |
| ARM_BIDIRECTIONAL_5HOP_MEET_MID | W_v1_regime (1000) | full V_C ranking; depth=5 | **PRIMARY: >= 0.50 for HARD_PASS** |

## SACRED SANITY rails

- `RAIL_BASELINE`: BASELINE NOT in [0.62, 0.68] majority -> SANITY_BREACH (pre-empts)
- `RAIL_META_M7`: REPRODUCE NOT in [0.08, 0.25] majority -> META_M7 BREACH
  flag (does NOT pre-empt verdict; routes through HARD_PASS_REVIVAL_WITH_META_M7_NOTE)

## Verdict ladder (LOCKED via module-init asserts)

- `HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL`:
  - BIDIRECTIONAL_MEET_MID >= 0.50 AND cv <= 0.07 AND
  - REPRODUCE in [0.08, 0.25] (META_M7 OK)
  - Headline: bidirectional meet-in-middle at pointer-v2-matched-rail revives
    Barrier 1 from chain-grade-impossible to chain-grade

- `HARD_PASS_REVIVAL_WITH_META_M7_NOTE`:
  - BIDIRECTIONAL_MEET_MID >= 0.50 AND cv <= 0.07 BUT
  - REPRODUCE NOT in [0.08, 0.25]
  - Within-cell lift honest; cross-cell narrative needs regime reconciliation

- `HARD_FAIL_BIDIRECTIONAL_DOESNT_HELP`:
  - BIDIRECTIONAL_MEET_MID < 0.30 -- the v1 0.67 didn't replicate

- `MIDDLE_BAND_BIDIRECTIONAL_PARTIAL`: bidir in [0.30, 0.50)

## Config

**FULL mode:**
- N=8192, V_C=200, V_P=10, K_SET=20
- Seeds [7, 17, 23]
- W_pointer_v2: n=200 chains, max_depth=10 -> 2000 bindings
- W_v1_regime: n=200 chains, max_depth=5 -> 1000 bindings
- DEPTH=5 (test); midpoint_hop=2

**SMOKE mode:**
- N=2048, V_C=200, seeds [7]
- W_pointer_v2: n=100 max_depth=10 -> 1000 bindings (preserves crosstalk regime)
- W_v1_regime: n=50 max_depth=5 -> 250 bindings

## Self-test (T1-T9; module-init blocks dispatch if any fails)

- T1: bipolar / ingest_hebbian / make_deep_chains primitives
- T2: SINGLE_CHAIN_NAIVE at small-V valid top1
- T3: META_M7 arm uses byte-equivalent primitive (just different W)
- T4: PROBE arm top1 must be None (NOT NaN -- v1 bug regression guard)
- T5: BIDIRECTIONAL_MEET_MID rank arm returns valid top1
- T6: forward/backward state-cosine math is correct on clean 1-hop W (cos > 0.2)
- T7: bands locked (asserts numeric values)
- T8: LLM call counter == 0
- T9: META_M7 cleanup-primitive byte-equivalence

## Estimated runtime

v1 seed 7 reported `elapsed_s=2738s` with BIDIR_MEET_MID at 2687s dominant
(V_C=200 inner loop: 200 candidates x backward-walk-3-hops + cosine per candidate
per query x 200 queries = 200 * 200 * 3 = 120K backward walks at N=8192).

**3 seeds estimated total: ~8500-9000s.** Routed at **14400s** (queue_add.sh cap)
for safety margin; v2 adds a fast REPRODUCE arm (~20s/seed). Seed-checkpointing
+ atexit synth ensures partial seed completion still lands interpretable
metrics if wall-clock exceeded.

Smoke confirmation (1 seed, V_C=200 n_chains=50 N=2048): BIDIR_MEET_MID = 55s.
Full = 200 chains x N=8192 ~50x larger inner loop -> ~2800s/seed empirically
matches v1's 2687s seed 7 cost.

## What this cell answers

- `HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL`: bidirectional meet-in-middle at
  matched regime is a chain-grade Barrier 1 revival mechanism. Route to Skunkworks.
- `HARD_PASS_REVIVAL_WITH_META_M7_NOTE`: within-cell lift honest; cross-cell narrative
  needs investigation. Substrate program needs to either reproduce pointer-v2 baseline
  at v1 regime or vice versa.
- `HARD_FAIL`: v1's 0.67 was noise or oracle-routing leakage; retire bidirectional
  meet-in-middle as Barrier 1 candidate.

## Risk register (Fix #26 + USER bias checklist)

- BIAS-Q (suspect 1.000): per-step accuracy not reported for ranking arm
  (no concept of per-step for a midpoint-cosine rank); per-query
  `_correct_per_query` enables post-hoc error analysis
- BIAS-J (oracle / closed-set leakage): the V_C candidate-set INCLUDES the
  true_Z; this is intentional (testing the substrate's ranking ability over the
  known concept set); honest scope flag for cross-cell comparison
- Fix #28: per-arm metrics fully reported (top1 + cosines + error correlation)
- META_M7: this IS the rail; same as Cell B v2 logic
- BIAS-O (basis vs use-case): W-binding count = basis; bidirectional mechanism
  = use-case readout
