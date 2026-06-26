# Pre-reg: substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail

**Authored:** 2026-06-25 (exp_dev under autonomous YOLO; Director-routed redispatch)
**Anchor:** `substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail`
**Cell:** `experiments/exp_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail.py`
**Routing:** `local_cpu_queue`
**Timeout:** 7200s (2x v1's 3600s -- v1 timed out at 3600s with seed 7 partial complete)

---

## V1 ISSUE: same primitive, different W-bindings -> different "rail"

Cell B v1 SINGLE_CHAIN_5HOP rail (seed 7 partial) landed at **0.275**.
Pointer-chain v2 forward-only depth-5 rail = **0.122**.
Both cells use ALGORITHMICALLY IDENTICAL `_retrieve_1hop` cleanup primitive
(`E @ (W @ key) -> argmax`).

So the 0.275 vs 0.122 gap is NOT a mechanism diff. It's a **regime diff**:

| | Cell B v1 | pointer-chain v2 |
|---|---|---|
| n_chains | 200 | 200 |
| max_depth | **5** | **10** |
| W bindings | **1000** | **2000** |
| V_C x V_P key space | 200 x 10 | 200 x 10 |
| Crosstalk per (s,p) pair | ~lower | ~2x higher |

This is the **documented pointer-chain v1 -> v2 bug pattern** (cell v2 DESIGN_NOTE
quote: "v1 ingested ~7.5x more triples spread across the same per-predicate key
space -> drastically more per-(s,p) crosstalk -> lower 1-hop accuracy -> chain
compounds"). Cell B v1 inadvertently re-created the LOWER-CROSSTALK regime by
using max_depth=5 in `make_deep_chains` -> half the bindings of pointer-v2.

Without verifying this, we cannot claim Cell B v1's COMPOSE_PARTITION_5HOP=0.95
and COMPOSE_MULTI_BANK_5HOP=0.865 "revive Barrier 1 from 0.122 to 0.95" -- they
might just be more lift on top of an easier baseline. **WITHIN-cell lifts** (compose
arms vs single arm IN SAME REGIME) are honest either way.

## Mode (verdict logic)

**Two-W discipline:** Cell B v2 builds TWO W matrices per seed.

1. `W_pointer_v2` = `ingest_hebbian(make_deep_chains(n=200, V_P=10, max_depth=10))`
   = 2000 bindings -- matches pointer-chain v2 ingest EXACTLY.
   Used by ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP only.

2. `W_v1_regime` = `ingest_hebbian(make_deep_chains(n=200, V_P=10, max_depth=5))`
   = 1000 bindings -- matches Cell B v1 ingest EXACTLY.
   Used by all v1 arms (SINGLE / FLY / BANK / PART / ALL3).

## Arms (7)

| Arm | W | Config | Target band |
|---|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep W (400 bindings) | n=200 2-hop chains, V_P=2 fixed-pair | [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | W_pointer_v2 (2000 bindings) | depth=10 ingest; depth=5 test; verbatim `_retrieve_1hop` | **[0.08, 0.25] META_M7 rail** |
| ARM_SINGLE_CHAIN_5HOP | W_v1_regime (1000 bindings) | depth=5 ingest+test; same primitive | (v1 rail 0.275; informational) |
| ARM_COMPOSE_FLY_LSH_5HOP | W_v1_regime (1000) + fly_LSH expansion | fly-LSH per-hop | (v1: 0.330) |
| ARM_COMPOSE_MULTI_BANK_5HOP | W_v1_regime (1000), banked | 8 banks, oracle-routed | (v1: 0.865) |
| ARM_COMPOSE_PARTITION_5HOP | W_v1_regime (1000), partitioned | 20 partitions, oracle-routed | **PRIMARY: >= 0.70 for HARD_PASS** |
| ARM_COMPOSE_ALL_3_5HOP | W_v1_regime (1000), all composed | fly+bank+partition | (v1: 0.880) |

## SACRED SANITY rails (verdict pre-emption on majority-seed breach)

- `RAIL_BASELINE`: BASELINE NOT in [0.62, 0.68] on majority of seeds -> `SANITY_BREACH`
- `RAIL_META_M7`: REPRODUCE NOT in [0.08, 0.25] on majority of seeds -> META_M7 BREACH
  flag in verdict (does NOT pre-empt; surfaces in `HARD_PASS_REVIVAL_WITH_META_M7_NOTE`)

## Verdict ladder (LOCKED via module-init asserts)

- `HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL`:
  - ARM_COMPOSE_PARTITION_5HOP >= 0.70 AND cv <= 0.07 AND
  - ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP in [0.08, 0.25] (META_M7 OK)
  - Headline: partition-routing per-hop at MATCHED-PV2-REGIME-FOR-RAIL revives
    Barrier 1 from chain-grade-impossible (0.122) to chain-grade (>=0.70)

- `HARD_PASS_REVIVAL_WITH_META_M7_NOTE`:
  - ARM_COMPOSE_PARTITION_5HOP >= 0.70 AND cv <= 0.07 AND
  - ARM_REPRODUCE_POINTER_CHAIN_V2 NOT in [0.08, 0.25]
  - Within-cell lifts honest; cross-cell narrative to pointer-chain v2 needs
    regime-reconciliation; the regime gap is itself information

- `HARD_FAIL_REVIVAL_DIDNT_HOLD`:
  - ARM_COMPOSE_PARTITION_5HOP < 0.50 -- the 0.95 v1 lift didn't replicate

- `MIDDLE_BAND_REVIVAL_PARTIAL`: partition in [0.50, 0.70)

## Config

**FULL mode:**
- N=8192, V_C=200, V_P=10, K_SET=20
- Seeds [7, 17, 23] (apples-to-apples with pointer-chain v2 + Cell X v2)
- W_pointer_v2: n=200 chains, max_depth=10 -> 2000 bindings
- W_v1_regime: n=200 chains, max_depth=5 -> 1000 bindings
- 6 composition primitives: N_BANKS=8, N_PARTITIONS=20, N_LSH_EXPANSIONS=5, LSH_TOPK=20
- Test depth=5 across all multi-hop arms

**SMOKE mode:**
- N=2048, V_C=200, seeds [7]
- W_pointer_v2: n=100 max_depth=10 -> 1000 bindings (preserves crosstalk regime ratio)
- W_v1_regime: n=50 max_depth=5 -> 250 bindings

## Self-test (T1-T9; module-init blocks dispatch if any fails)

- T1-T7: original cell B v1 selftest (all primitive arms return valid top1)
- T8: bands locked (asserts numeric values)
- T9: LLM call counter == 0 (substrate-only)
- META_M7 invariant: `_retrieve_1hop_naive` byte-equivalent across arms (only the
  W matrix differs between SINGLE and REPRODUCE arms)

## Estimated runtime

v1 timed out at 3600s with seed 7 partial (~1890s reported, plus shutdown).
Per-seed compute dominated by COMPOSE_FLY_LSH (~692s) + COMPOSE_MULTI_BANK
(~490s) + COMPOSE_ALL_3 (~661s) + partition (~19s) + single (~19s) = ~1900s/seed.
v2 adds REPRODUCE arm = single_chain at 2000 bindings (similar cost to v1 SINGLE
~19s; negligible). **3 seeds * ~1900s = ~5700s + safety margin** => 7200s timeout.

## What this cell answers

- `HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL`: partition-routing per-hop reviving
  Barrier 1 at pointer-v2-matched regime; cross-cell honest claim. Route to
  Skunkworks for landed-VET tier classification.
- `HARD_PASS_REVIVAL_WITH_META_M7_NOTE`: revival arm holds but rail diverges
  from pointer-v2; rationale must surface; substrate program needs to either
  reproduce pointer-v2 baseline at v1 regime or vice versa.
- `HARD_FAIL_REVIVAL_DIDNT_HOLD`: v1 seed-7 partial was a noise / oracle-routing
  bug that didn't generalize across seeds; retire the partition revival angle.

## Risk register (Fix #26 verify-the-referent + USER bias checklist)

- BIAS-Q (suspect 1.000): per-step_acc reported per-arm; if any depth=5 per-step
  hits 1.00 at V_C=200, flag W-saturation in verdict_msg
- BIAS-P (anisotropy / oracle routing): COMPOSE_MULTI_BANK + COMPOSE_PARTITION
  use ORACLE routing (target_bank / target_part). Honest scope flag: assumes
  perfect routing; follow-up cell would test with real router
- Fix #28: per-arm metrics fully reported (top1 + per_step_acc + W_n_bindings)
- META_M7: this IS the rail; if it breaks, the COMPOSE arms are honest within-
  cell but not directly comparable to pointer-chain v2
- BIAS-O (basis vs use-case): W-binding count is the basis property; composition
  primitives are the use-case readout
