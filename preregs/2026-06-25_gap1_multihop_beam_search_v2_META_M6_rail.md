# Pre-reg: gap1_multihop_beam_search_v2_META_M6_rail

**Authored:** 2026-06-25 (exp_dev under autonomous YOLO; cross-cell rail-mismatch fix; same pattern as Cell B v2 + Cell C v2)
**Anchor:** `gap1_multihop_beam_search_v2_meta_m6_rail`
**Cell:** `experiments/exp_gap1_multihop_beam_search_v2_META_M6_rail.py`
**Routing:** `local_cpu_queue`
**Mode determination:** **MODE B** (Cell X v1 used the SAME forward K=1 cleanup primitive as pointer-chain v2; the 0.33-vs-0.122 SINGLE_TOP1_5HOP gap is a REGIME artifact, not a mechanism gain)

---

## V1 result (Cell X v1, landed; Skunkworks tier-ruled MEASURED_MECHANISM in batch 1)

Metrics: `data/exp_substrate_multihop_beam_search_with_WM_candidates_v1/metrics.json`

| Arm | Mean top1 | per-step |
|---|---|---|
| ARM_BASELINE_HRR_2HOP | 0.6500 | (sanity_breach 1/3 seeds) |
| ARM_SINGLE_TOP1_5HOP | **0.3300** | per-step ~ [0.83, 0.66, 0.50, 0.41, 0.33] |
| ARM_BEAM_W2_TOPK3 | 0.5950 | |
| ARM_BEAM_W5_TOPK3 | 0.6250 | |
| ARM_BEAM_W10_TOPK5 | 0.6667 | (monotonic, cv=0.043) |

Within-cell architectural lift honest: BEAM_W10 - SINGLE_TOP1 = +0.337. But cross-cell to pointer-chain v2 (mean SINGLE 5HOP = 0.122) is META_M7 unverifiable: v1 ran W with max_depth=5 (1000 bindings) while pointer-chain v2 used max_depth=10 (2000 bindings).

## V1 root cause (cross-cell rail mismatch)

| Component | Cell X v1 (beam) | pointer-chain v2 |
|---|---|---|
| `bipolar` / `ingest_hebbian` / `make_deep_chains` / `_retrieve_1hop` chained | verbatim | verbatim |
| Substrate dims (FULL) | N=8192 V_C=200 V_P=10 K_SET=20 | identical |
| W binding count | n=200 max_depth=5 -> **1000 bindings** | n=200 max_depth=10 -> **2000 bindings** |
| SINGLE_TOP1_5HOP | 0.33 mean | 0.122 mean |

2x crosstalk diff in same (V_C=200, V_P=10) key space. Same regime-artifact pattern that Cell B v2 + Cell C v2 fixed.

## Cell X v2 design (META_M6 rail discipline)

### Six arms

| Arm | Config | Target |
|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep regime; chain_naive_hard | [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2 | K=1 noise=0; W = make_deep_chains(n=200, V_P=10, max_depth=10); test depth=5 | **[0.08, 0.25] (META_M6 rail)** |
| ARM_SINGLE_TOP1_5HOP_V1_REGIME | K=1 noise=0; W = make_deep_chains(n=200, V_P=10, max_depth=5); test depth=5 | [0.20, 0.50] (advisory; replicates v1's 0.33) |
| ARM_BEAM_W2_TOPK3_5HOP | beam_width=2 top_k=3; W_pointer_v2_regime | discriminator at matched-regime |
| ARM_BEAM_W5_TOPK3_5HOP | beam_width=5 top_k=3; W_pointer_v2_regime | discriminator at matched-regime |
| ARM_BEAM_W10_TOPK5_5HOP | beam_width=10 top_k=5; W_pointer_v2_regime | **PRIMARY discriminator** |

**Two-W discipline:** ARM_REPRODUCE + ARM_BEAM_* all share `W_pointer_v2_regime` (n=200, max_depth=10). ARM_SINGLE_V1 has its own `W_v1_regime` (n=200, max_depth=5; informational; advisory rail does NOT pre-empt verdict).

### Pre-reg bands (LOCKED via module-init asserts)

**SACRED SANITY rails (verdict pre-empted by rail breach on majority of seeds):**
- `RAIL_BASELINE`: ARM_BASELINE_HRR_2HOP NOT in [0.62, 0.68] -> `SANITY_BREACH`
- `RAIL_META_M6`: ARM_REPRODUCE_POINTER_CHAIN_V2 NOT in [0.08, 0.25] -> rail violated; if BEAM_W10>=0.50 -> `HARD_PASS_WITH_META_M7_NOTE`; otherwise downgrade

**Mode B verdict ladder (applies only if RAIL_BASELINE passes):**

- `HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM`:
  - BEAM_W10 >= 0.50 AND
  - REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
  - monotonic W2 <= W5 <= W10 (within MONOTONIC_TOL=0.02) AND
  - cv_W10 <= 0.07

- `HARD_PASS_WITH_META_M7_NOTE`:
  - BEAM_W10 >= 0.50 AND
  - REPRODUCE_POINTER_CHAIN_V2 OUT of [0.08, 0.25]
  - (lift is real but cross-cell rail anchor isn't reproducing; tier-decision deferred to Skunkworks)

- `HARD_PASS_PARTIAL_BEAM_LIFT`:
  - BEAM_W10 >= 0.30 AND not chain-grade

- `MIDDLE_BAND_BEAM_MARGINAL`:
  - BEAM_W10 in [0.20, 0.30)

- `HARD_FAIL_BEAM_DOESNT_HELP`:
  - BEAM_W10 < 0.20

### Config (FULL mode)

- N=8192, V_C=200, V_P=10, K_SET=20
- Seeds [7, 17, 23] (apples-to-apples with pointer-chain v2 + Cell B v2)
- Pointer-v2-regime W: n_chains=200, max_depth=10, ingests 2000 bindings
- V1-regime W: n_chains=200, max_depth=5, ingests 1000 bindings
- Test depth=5 in all multi-hop arms
- Beam configs: (W=2,K=3), (W=5,K=3), (W=10,K=5)

### Config (SMOKE)

- N=2048, V_C=200, V_P=10, K_SET=20
- Seeds [7]
- Pointer-v2-regime W: n=50, max_depth=10 (KEEP depth=10 for crosstalk-relevant W)
- V1-regime W: n=40, max_depth=5
- Per-arm test chains: 20 each
- **Smoke gate:** ARM_REPRODUCE_POINTER_CHAIN_V2 at smoke MUST land in [0.08, 0.40] (wider absorption at smaller N). If smoke REPRODUCE > 0.50 -> regime-confound risk; BLOCK full dispatch and re-investigate.

### Self-test (runs at module init; BLOCKS dispatch if any fails)

- T1: construction self-consistency (bipolar / ingest_hebbian / make_deep_chains)
- T2: arm_single_chain_naive beats chance at small scale
- T3: beam(W=1, K=1) per-hop top-of-beam EQUALS arm_single per_step_acc (invariant)
- T4: beam top_of_beam <= correct_in_beam invariant
- T5: arm_single _retrieve_1hop EQUIVALENT to pointer-chain v2 inline cleanup
- T6: NaN guard at production-scale (N=4096)
- T7: bands locked (exact numeric values)
- T8: LLM call counter == 0

## Estimated runtime

Full mode 3 seeds. Per seed: baseline ~7s, REPRODUCE ~18s, SINGLE_V1 ~18s, BEAM_W2 ~35s, BEAM_W5 ~70s, BEAM_W10 ~135s. Plus 2x W construction (~15s). Total per seed ~315s. 3 seeds -> ~950s. **Estimated 950-1100s for full run** (3 seeds, local CPU, N=8192). Comfortable within local_cpu_queue.

## Routing

- Queue: `local_cpu_queue`
- Timeout: 3600s (3x+ safety on ~1100s estimate)
- Smoke gate: BLOCKS dispatch if --self-test OR --smoke fails

## What this cell answers

If `HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM`: beam search at MATCHED regime is chain-grade-eligible Barrier-1 mechanism; route to Skunkworks for landed-VET tier classification.

If `HARD_PASS_WITH_META_M7_NOTE`: beam search lifts but REPRODUCE didn't reproduce the cross-cell anchor; investigate regime-difference before tier-claim.

If `HARD_PASS_PARTIAL_BEAM_LIFT`: beam lifts over single-top1 but doesn't clear chain-grade bar; partial mechanism.

If `MIDDLE_BAND_BEAM_MARGINAL` / `HARD_FAIL_BEAM_DOESNT_HELP`: beam search at MATCHED regime doesn't recover Barrier 1; errors correlate through W; retire as Barrier-1 candidate.

## Risk register

- BIAS-Q (suspect 1.000): if any per-step accuracy hits 1.00 at depth=5 with V_C=200, W-saturation flag in verdict_msg
- META_M6: this is THE rail; if it breaks, cross-cell comparisons are uninterpretable -> downgrade to HARD_PASS_WITH_META_M7_NOTE
- Fix #28: read per-arm metrics, NOT just verdict_msg framing; per-arm top1 + per-step + cv all reported
- BIAS-Q non-monotonic beam: if W5 > W10 or W2 > W5, that's a tell that beam width isn't the mechanism

## Strategy-route on landing

- HARD_PASS_CHAIN_GRADE -> Skunkworks landed-VET
- HARD_PASS_WITH_META_M7_NOTE -> Skunkworks landed-VET + flag as "lift real but anchor mismatch; investigate"
- MIDDLE_BAND / HARD_FAIL -> Research 2x revival drill (route negatives per standing USER rule)
