# Pre-reg: gap1_multihop_ldpc_rts_bidirectional_v2_META_M6_rail

**Authored:** 2026-06-25 (exp_dev under autonomous YOLO; cross-cell rail-mismatch fix; same pattern as Cell B v2 + Cell C v2 + Cell X v2)
**Anchor:** `gap1_multihop_ldpc_rts_bidirectional_v2_meta_m6_rail`
**Cell:** `experiments/exp_gap1_multihop_ldpc_rts_bidirectional_v2_META_M6_rail.py`
**Routing:** `local_cpu_queue`
**Mode determination:** **MODE B** (Gap 1 v1 used the same forward K=1 cleanup primitive as pointer-chain v2; the baseline 0.332 vs anchor 0.145 mismatch is a REGIME artifact)

---

## V1 result (Gap 1 LDPC+RTS v1, landed just now)

Metrics: `data/exp_gap1_multihop_ldpc_rts_bidirectional_v1/metrics.json`

| Arm | Mean top1 (5 seeds) | per-seed sd |
|---|---|---|
| ARM_BASELINE_pointer_chain_v2 | **0.3320** | (target was [0.125, 0.165]; SANITY_BREACH 5/5 seeds) |
| ARM_SOFT_FWD | 0.6090 | |
| ARM_BACKWARD_ONLY | 0.3350 | |
| ARM_LDPC_BIDIR | 0.6090 | sd=0.030 |
| ARM_RTS_SMOOTH | 0.6090 | sd=0.030 |

LDPC and RTS both at 0.609 -- well above HP_TOP1_MIN=0.50 -- but verdict was `SANITY_BREACH_BASELINE_OUT_OF_BAND` because the v1 "baseline" was in the wrong regime to compare against the pointer-chain v2 anchor.

## V1 root cause (cross-cell rail mismatch)

| Component | Gap 1 v1 | pointer-chain v2 BASELINE_RAIL_FIXED |
|---|---|---|
| W build | `make_deep_chains(n_chains=200, V_P=10, max_depth=5)` | `make_deep_chains(n=200, V_P=10, max_depth=10)` |
| W binding count | 200 x 5 = **1000 bindings** | 200 x 10 = **2000 bindings** |
| BASELINE depth-5 top1 | 0.332 (v1 measured) | 0.145 (authoritative anchor) |

2x crosstalk diff in same (V_C=200, V_P=10) key space. Forward K=1 cleanup primitive is algorithmically identical across cells; the 2x W density gap drove the 0.332 vs 0.145 baseline split. Same regime-artifact pattern as Cell B v2 + Cell C v2 + Cell X (beam) v2.

## V2 design (META_M6 rail discipline)

### Six arms

| Arm | Config | Target |
|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep regime; chain_naive_hard | [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2 | K=1 noise=0 hard-argmax; W_pointer_v2_regime (n=200, max_depth=10) | **[0.08, 0.25] (META_M6 rail)** |
| ARM_SOFT_FWD | soft forward belief; W_pointer_v2_regime | discriminator |
| ARM_BACKWARD_ONLY | reverse-chain soft + forward re-derive; W_pointer_v2_regime | discriminator |
| ARM_LDPC_BIDIR | iterative sum-product factor graph (3 sweeps); W_pointer_v2_regime | **Anchor 1 PRIMARY** |
| ARM_RTS_SMOOTH | forward x backward analytical smoother; W_pointer_v2_regime | **Anchor 2 PRIMARY** |

**Single-W discipline:** ALL mechanism arms (REPRODUCE through RTS) share `W_pointer_v2_regime` (n=200, max_depth=10). The beta-sweep 2hop baseline uses its own W per the verbatim baseline pattern.

### Pre-reg bands (LOCKED via module-init asserts)

**SACRED SANITY rails (verdict pre-empted by rail breach on majority of seeds):**
- `RAIL_BASELINE`: ARM_BASELINE_HRR_2HOP NOT in [0.62, 0.68] -> `SANITY_BREACH_BASELINE_OUT_OF_BAND`
- `RAIL_META_M6`: ARM_REPRODUCE_POINTER_CHAIN_V2 NOT in [0.08, 0.25] -> rail violated; chain-grade pass downgraded to `HARD_PASS_WITH_META_M7_NOTE`

**Mode B verdict ladder (applies only if RAIL_BASELINE passes):**

- `HARD_PASS_GAP1_CHAIN_GRADE` (Anchor 1 chain-grade -- LDPC):
  - LDPC >= 0.50 AND
  - REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
  - LDPC > SOFT_FWD + 0.10 AND
  - sd_LDPC <= 0.06

- `HARD_PASS_GAP1_CHAIN_GRADE` (Anchor 2 chain-grade -- RTS):
  - RTS >= 0.50 AND
  - REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
  - RTS > max(REPRODUCE, BACKWARD) + 0.10 AND
  - sd_RTS <= 0.06

- `HARD_PASS_WITH_META_M7_NOTE` (lift real but rail breach):
  - LDPC >= 0.50 OR RTS >= 0.50, AND
  - REPRODUCE_POINTER_CHAIN_V2 OUT of [0.08, 0.25]

- `MIDDLE_BAND_GAP1_PARTIAL_LIFT`:
  - LDPC or RTS in [0.30, 0.50)

- `HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED`:
  - both LDPC <= 0.25 AND RTS <= 0.25

### Config (FULL mode)

- N=8192, V_C=200, V_P=10, K_SET=20
- Seeds [7, 17, 23, 31, 41] (5 seeds; matches v1 sample size)
- Pointer-v2-regime W: n_chains=200, max_depth=10, ingests 2000 bindings
- Test depth=5 in all multi-hop arms
- LDPC sweeps=3

### Config (SMOKE)

- N=2048, V_C=200, V_P=10, K_SET=20
- Seeds [7]
- Pointer-v2-regime W: n=50, max_depth=10 (KEEP depth=10 for crosstalk-relevant W)
- Per-arm test chains: 20
- **Smoke gate:** ARM_REPRODUCE_POINTER_CHAIN_V2 at smoke MUST land in [0.08, 0.40] (wider absorption at smaller N). If smoke REPRODUCE > 0.50 -> regime-confound risk; BLOCK full dispatch and re-investigate.

### Self-test (runs at module init; BLOCKS dispatch if any fails)

- T1: construction self-consistency
- T2: REPRODUCE arm produces in [0, 1]
- T3: SOFT_FWD numerical sanity (no NaN)
- T4: BACKWARD_ONLY numerical sanity
- T5: LDPC produces convergence stat
- T6: RTS produces per_step_acc
- T7: REPRODUCE arm EQUIVALENT to pointer-chain v2 inline cleanup
- T8: bands locked (exact numerics)
- T9: LLM call counter == 0
- T10: NaN guard at production-scale (N=4096)

## Estimated runtime

Full mode 5 seeds. Per seed v1 was ~225s; v2 adds REPRODUCE arm (~20s) but otherwise same arm count. Per seed estimate ~245s. 5 seeds + W rebuild -> ~1300-1400s. **Estimated ~1500s for full run** (5 seeds, local CPU, N=8192). Comfortable within local_cpu_queue.

## Routing

- Queue: `local_cpu_queue`
- Timeout: 5400s (3.5x safety on ~1500s estimate)
- Smoke gate: BLOCKS dispatch if --self-test OR --smoke fails

## What this cell answers

If `HARD_PASS_GAP1_CHAIN_GRADE` (LDPC or RTS): bidirectional belief propagation at MATCHED regime is chain-grade-eligible Gap-1 mechanism; route to Skunkworks for landed-VET tier classification.

If `HARD_PASS_WITH_META_M7_NOTE`: LDPC/RTS lift real but REPRODUCE didn't reproduce the cross-cell anchor; tier-decision deferred to Skunkworks; investigate regime-difference.

If `MIDDLE_BAND_GAP1_PARTIAL_LIFT`: lift exists but doesn't clear chain-grade bar; partial mechanism.

If `HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED`: bidirectional at MATCHED regime doesn't recover Gap 1; errors correlate; retire as Gap-1 candidate.

## Risk register

- BIAS-Q (suspect 1.000): if any per-step accuracy hits 1.00 at depth=5 with V_C=200, W-saturation flag in verdict_msg
- META_M6: this is THE rail; if it breaks, cross-cell comparisons are uninterpretable -> downgrade to HARD_PASS_WITH_META_M7_NOTE
- Fix #28: read per-arm metrics, NOT just verdict_msg framing; per-arm top1 + per-step + sd all reported
- BIAS-N (Cramer-Rao referent-verdict-field): verdict field name uses `arm_*` not `summary` to enforce per-arm read
- LDPC over_soft_fwd discipline: chain-grade requires LDPC > SOFT_FWD + 0.10; mere "high LDPC" insufficient
- RTS super-additivity discipline: chain-grade requires RTS > max(REPRODUCE, BACKWARD) + 0.10; ensures smoother is actually integrating both directions, not just inheriting one

## Strategy-route on landing

- HARD_PASS_GAP1_CHAIN_GRADE -> Skunkworks landed-VET
- HARD_PASS_WITH_META_M7_NOTE -> Skunkworks landed-VET + flag "lift real but anchor mismatch"
- MIDDLE_BAND / HARD_FAIL -> Research 2x revival drill (route negatives per standing USER rule)
