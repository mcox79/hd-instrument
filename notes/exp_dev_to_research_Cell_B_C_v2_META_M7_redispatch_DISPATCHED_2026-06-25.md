# Cell B v2 + Cell C v2 META_M7 rail DISPATCHED (multi-hop revival batch)

**From:** exp_dev
**Recipients:** research (primary), skunkworks (cc landed-VET), orchestrator (cc queue), USER
**Anchors:**
- `substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail` (Cell B v2)
- `substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail` (Cell C v2)
**Queue:** local_cpu_queue (BOTH; PENDING; 6 ahead in queue)
**Commit:** see git log -- 4 files (2 cells + 2 preregs)
**Timeouts:** Cell B 7200s; Cell C 14400s (BIDIR_MEET_MID at V_C=200 dominates)

## TL;DR

V1 cells timed out at 3600s with seed 7 partials showing real Barrier 1 revival
signals:
- Cell B v1 ARM_COMPOSE_PARTITION_5HOP = 0.95
- Cell B v1 ARM_COMPOSE_MULTI_BANK_5HOP = 0.865
- Cell C v1 ARM_BIDIRECTIONAL_MEET_MID = 0.67

BUT META_M7 risk: SINGLE_CHAIN rail in both v1 cells landed at 0.275, NOT
pointer-chain v2's known 0.122 forward-only depth-5 rail. Same primitive
(`E @ (W @ key) -> argmax`); different W-binding count (1000 v1 vs 2000 pv2).
We cannot claim "revives Barrier 1 from 0.122 to 0.95" without verifying the
regime.

V2 fixes:
1. **ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP** in BOTH cells: separate W from
   `make_deep_chains(n=200, V_P=10, max_depth=10)` -> 2000 bindings (matches
   pointer-chain v2 exactly). Tests depth=5 with verbatim `_retrieve_1hop`.
   Target band [0.08, 0.25].
2. **Cell C: nan fix** in ARM_BIDIRECTIONAL_MEET_HOP2: top1=None (JSON null)
   instead of NaN (invalid JSON). v1 partial had bare `NaN` which most parsers
   reject; the probe arm's signal lives in mean/median cosine.
3. **Longer timeouts** let all 3 seeds complete.

## V1 -> V2 META_M7 regime diff (the load-bearing finding)

Both Cell B v1 and Cell C v1 use the IDENTICAL cleanup primitive
(`_retrieve_1hop` / `_retrieve_1hop_naive`) as pointer-chain v2's reference
arm. Verified by inspection: same key formula, same W projection, same argmax.

| | Cell B/C v1 | pointer-chain v2 |
|---|---|---|
| `make_deep_chains` n_chains | 200 | 200 |
| `make_deep_chains` max_depth | **5** | **10** |
| W bindings | **1000** | **2000** |
| V_C x V_P key space | 200 x 10 (same) | 200 x 10 (same) |
| Test depth | 5 | 5 |

V1 cells inadvertently used max_depth=5 in `make_deep_chains` -> half the
bindings of pointer-v2 -> ~half the crosstalk in the same per-(s,p) key space
-> per-hop cleanup is more accurate -> chain compounds at higher accuracy
(0.275 vs 0.122).

This is the **documented pointer-chain v1 -> v2 bug pattern** (cell v2
DESIGN_NOTE quote: "v1 ingested ~7.5x more triples spread across the same
per-predicate key space -> drastically more per-(s,p) crosstalk -> lower 1-hop
accuracy -> chain compounds"). It now appears at a SHALLOWER differential
ratio (2x not 7.5x) but still produces a 2.25x SINGLE-rail divergence.

## V2 design

### Two-W discipline

Both v2 cells build TWO W matrices per seed:
- `W_pointer_v2` = `ingest_hebbian(make_deep_chains(n=200, V_P=10, max_depth=10))`
  = 2000 bindings. Used ONLY by ARM_REPRODUCE.
- `W_v1_regime` = `ingest_hebbian(make_deep_chains(n=200, V_P=10, max_depth=5))`
  = 1000 bindings. Used by all OTHER multi-hop arms (matches v1 exactly).

### Arms (Cell B v2: 7; Cell C v2: 5)

**Cell B v2:**
1. ARM_BASELINE_HRR_2HOP (beta-sweep sanity rail [0.62, 0.68])
2. ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP (META_M7 rail [0.08, 0.25])
3. ARM_SINGLE_CHAIN_5HOP (v1 rail; informational)
4. ARM_COMPOSE_FLY_LSH_5HOP (v1: 0.330)
5. ARM_COMPOSE_MULTI_BANK_5HOP (v1: 0.865)
6. ARM_COMPOSE_PARTITION_5HOP (v1: 0.95 -- **PRIMARY: >=0.70 for HARD_PASS**)
7. ARM_COMPOSE_ALL_3_5HOP (v1: 0.880)

**Cell C v2:**
1. ARM_BASELINE_HRR_2HOP ([0.62, 0.68])
2. ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP ([0.08, 0.25])
3. ARM_SINGLE_CHAIN_5HOP_FORWARD (v1 rail; informational)
4. ARM_BIDIRECTIONAL_5HOP_MEET_HOP2 (probe arm; top1=None; cosine probe)
5. ARM_BIDIRECTIONAL_5HOP_MEET_MID (v1: 0.67 -- **PRIMARY: >=0.50 for HARD_PASS**)

### Verdict ladder (BOTH cells)

- `HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL` / `..._BIDIRECTIONAL_REVIVAL`:
  PRIMARY arm clears HP_threshold AND REPRODUCE in [0.08, 0.25] (META_M7 OK)
- `HARD_PASS_REVIVAL_WITH_META_M7_NOTE`: PRIMARY clears HP_threshold BUT
  REPRODUCE NOT in band (within-cell lift honest; cross-cell needs reconciliation)
- `HARD_FAIL_...`: PRIMARY below floor (revival didn't replicate)
- `MIDDLE_BAND`: PRIMARY in [floor, HP_threshold)

## Smoke results (pre-flight gate; both PASS)

### Cell B v2 smoke (N=2048, 1 seed, 65s total)
```
BASELINE      = 0.6450  (sanity_ok)
REPRODUCE_PV2 = 0.2500  (META_M7_ok at upper edge; full will be lower with 2000 bindings)
SINGLE_v1     = 0.7600  (smaller W at smoke; v1 full was 0.275)
FLY_LSH       = 0.7200
MULTI_BANK    = 0.9600
PARTITION     = 0.9800  (PRIMARY; HARD_PASS bar 0.70)
ALL_3         = 0.9600
VERDICT       = HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL_PARTITION_PER_HOP
```

### Cell C v2 smoke (N=2048, 1 seed, 59s total)
```
BASELINE      = 0.6450  (sanity_ok)
REPRODUCE_PV2 = 0.2500  (META_M7_ok at upper edge)
SINGLE_FWD    = 0.7600
BIDIR_HOP2    = top1=None (probe; mean_cos=0.0; cleanly serialized)
BIDIR_MEET_MID= 0.9400  (PRIMARY; HARD_PASS bar 0.50)
VERDICT       = HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL
```

**Important smoke caveat:** REPRODUCE at smoke uses 1000 bindings (N=2048),
landing at 0.25 -- the UPPER edge of the [0.08, 0.25] band. At full
(N=8192, 2000 bindings), expected to land near pointer-v2's 0.122 well
inside band. If REPRODUCE at FULL also lands > 0.25, that's a meaningful
finding requiring substrate-level investigation (regime difference is more
than just W-binding count).

## Self-test results (T1-T9; both cells)

All PASS, including:
- T_META_M7: `_retrieve_1hop` byte-equivalent across SINGLE and REPRODUCE arms
  (only the W matrix differs; the primitive is byte-identical to pointer-chain
  v2's `_retrieve_1hop`)
- T_PROBE_TOP1 (Cell C): probe arm top1 == None (NOT NaN -- regression guard)
- T_BANDS_LOCKED: numeric values asserted at module init
- T_LLM_ZERO: substrate-only, no LLM forward calls

## What this answers

### HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL (best case)
- Both v2 cells PRIMARY arms hold across 3 seeds AND REPRODUCE in band
- **Barrier 1 is revived via partition-routing-per-hop (Cell B) AND/OR
  bidirectional-meet-in-middle (Cell C)** at pointer-v2-matched-rail regime
- 2-hop ceiling lifts; substrate extends to chain-grade multi-hop QA
- Route to Skunkworks for landed-VET tier classification

### HARD_PASS_REVIVAL_WITH_META_M7_NOTE
- PRIMARY arm holds but REPRODUCE diverges from [0.08, 0.25]
- v1's regime IS genuinely different from pointer-v2 in a way not just W-binding
  count; investigation needed (V_C? V_P? primitive variant we missed?)
- Within-cell architectural lifts STILL honest; cross-cell narrative pending

### HARD_FAIL
- v1's seed-7 partial was noise / oracle-routing leakage that didn't generalize
- Retire the partition-routing OR bidirectional-meet-in-middle angle

## Risk register

- BIAS-Q (suspect 1.000): per-step accuracy reported per-arm; flag in
  verdict_msg if any depth-5 step hits 1.00 at V_C=200
- BIAS-P (oracle routing): Cell B COMPOSE_MULTI_BANK + PARTITION use ORACLE
  routing (target_bank / target_part). Honest scope flag; follow-up cell would
  test with real router (would also test whether routing is the bottleneck)
- Fix #28: per-arm metrics fully reported (top1 + per_step_acc + W_n_bindings)
- META_M7: this IS the rail; if it breaks, the architectural lifts are honest
  within-cell but cross-cell narrative needs reconciliation

## Coordination

- **Research:** this note + reactive on full verdicts; if HARD_PASS_REVIVAL_WITH_
  META_M7_NOTE, route a same-cycle drill on the underlying regime-diff source
- **Skunkworks:** landed-VET candidate on HARD_PASS path for each cell; routing
  on any verdict
- **Orchestrator:** queue running on local_cpu (6 ahead per `pending` list);
  visible via queue_status.py

## Spawn-budget accounting (Fix #14)

- 2 of currently 2 exp_dev tasks complete (this batch + anisotropy v4 CPU path elsewhere)
- Non-conflicting cells (different anchors, no race on shared state)
- ASCII-only; substrate-only; substrate-native cleanup primitive verbatim across cells
