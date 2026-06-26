# Cell X v2 META_M6_rail DISPATCHED + Stage-1 sanity-check findings (2026-06-25)

**From:** exp_dev
**Recipients:** research (primary), skunkworks (cc landed-VET), orchestrator (cc queue), USER
**Anchor:** `substrate_multihop_parallel_replicate_majority_vote_v2_meta_m6_rail`
**Queue:** local_cpu_queue (RUNNING; 1 pending dispatched + now in flight)
**Cell:** `experiments/exp_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail.py`
**Pre-reg:** `preregs/2026-06-25_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail.md`
**Commit:** `0a50f8e4`
**Timeout:** 1800s (1.5x safety on ~600s estimate from pointer-chain v2 baseline)

## TL;DR (under-claim discipline)

Stage-1 sanity check found Cell X v1's striking 0.78 single-chain 5HOP was a **REGIME ARTIFACT**, NOT a
better cleanup primitive or a parallel-vote win. Cell X v1 ran in SMOKE MODE (N=2048, n_chains=50,
max_depth=5 -> 250 W bindings); pointer-chain v2 ran FULL (N=8192, n_chains=200, max_depth=10 -> 2000
bindings). **8x crosstalk difference in the same V_C=200, V_P=10 key space** — exactly the documented
pointer-chain v1 -> v2 bug pattern.

**Mode B selected:** Cell X v1 and pointer-chain v2 use the SAME cleanup primitive (verified by selftest
T9: identical argmax index at K=1 noise=0). Cell X v2 introduces two-W discipline to isolate regime from
mechanism. Whether parallel-vote actually revives Barrier 1 at MATCHED regime is now the open question;
the full run answers it.

## Stage 1 — line-level diff

### Identical (verbatim)
- `bipolar(M, n, g)` — atom construction
- `ingest_hebbian` — Hebbian outer-product W construction
- `make_two_hop_chains_betasweep` — baseline chain construction
- `chain_naive_hard` — baseline mechanism
- `make_deep_chains` — deep-chain construction
- Substrate dims at FULL: N=8192, V_C=200, n_predicates=10, K_SET=20, seeds=[7, 17, 23]

### Cleanup primitive math (the load-bearing pair)

Cell X v1 `_one_chain_step` at K=1 noise=0:
```
key = (cur_state * R[p] * sq).astype(np.float32)
readout = W @ key
next_idx = int((E @ readout).argmax())
new_state = E[next_idx].copy()  # next-hop cur_state = cleaned codebook atom
```

Pointer-chain v2 `_retrieve_1hop` chained:
```
key = (E[s] * R[p] * sq).astype(np.float32)
scores = E @ (W @ key)
s_pred = int(scores.argmax())  # next-hop seed = cleaned codebook index
```

**Algorithmically identical.** Both form key from `E[s] * R[p] * sq`, both apply W, both argmax over E,
both use cleaned-atom for next hop's seed. **Confirmed by selftest T9 at runtime** (idx=51 from both
primitives on the same query).

### So why did Cell X v1 K=1 5HOP = 0.78 vs pointer-chain v2 K=1 5HOP = 0.122?

Cell X v1 ran SMOKE: `"run_mode": "smoke"` per metrics.json L5, N=2048, n_chains=50, max_depth=5,
1 seed.

W-bindings:
- Cell X v1 W = 50 chains x 5 hops = **250 bindings**
- pointer-chain v2 W = 200 chains x 10 hops = **2000 bindings**

8x more bindings in pointer-chain v2 in the same V_C=200, V_P=10 key space -> drastically more per-(s,p)
crosstalk -> lower 1-hop accuracy -> chain compounds at depth 5.

This is **the documented pointer-chain v1 -> v2 bug pattern repeating**, this time as a smoke-vs-full
sign-flip in Cell X v1. The K=5/K=15 voting arms in v1 (0.80, 0.86, 0.82) showed only marginal lift over
0.78 and were NON-monotonic (K5 > K15) which itself is a tell that voting wasn't the load-bearing
mechanism.

## Cell X v2 design

### Five arms with two-W discipline

| Arm | W | Config | Target band |
|---|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep W (400 bindings) | n=200 2-hop chains | [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2 | W_pointer_v2 (2000 bindings; HARD) | K=1 noise=0; depth=5 test | [0.08, 0.25] (META_M6 rail) |
| ARM_CELLX_V1_AS_DOC | W_v1 (250 bindings; EASIER) | K=1 noise=0; depth=5 test | [0.60, 0.90] (V1_DOC rail) |
| ARM_PARALLEL_K5_PERHOP_5HOP | W_pointer_v2 (HARD) | K=5 noise=0.05; per-hop vote | discriminator |
| ARM_PARALLEL_K15_PERHOP_5HOP | W_pointer_v2 (HARD) | K=15 noise=0.05; per-hop vote | PRIMARY |

**Parallel arms use the HARD regime** so any lift is real mechanism contribution, NOT W-crosstalk
shortcut.

### Pre-reg bands (LOCKED via module-init asserts)

**SACRED rails (verdict pre-empt on majority-seed breach):**
- `RAIL_BASELINE_BREACH`: baseline NOT in [0.62, 0.68]
- `META_M6_RAIL_VIOLATION`: REPRODUCE_POINTER_CHAIN_V2 NOT in [0.08, 0.25] — THE rail
- `RAIL_V1_DOC_BREACH`: CELLX_V1_AS_DOC NOT in [0.60, 0.90]

**Mode B ladder (all 3 rails pass):**
- `HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE`: K15 >= 0.70 AND K5 >= 0.50 AND monotonic K1<K5<K15 AND cv_K15 <= 0.07
- `HARD_PASS_PARTIAL_BARRIER_1_LIFT`: K15 >= 0.50 AND monotonic K1<K5<K15
- `MIDDLE_BAND_VOTING_MARGINAL`: K15 in [0.30, 0.50)
- `HARD_FAIL_PARALLEL_DOESNT_HELP`: K15 < 0.30

Locked assert at module init: `META_M6_RAIL_HI (0.25) < V1_DOC_RAIL_LO (0.60)` — encodes Stage-1
prediction that the two regimes produce different bands.

## Smoke results (pre-flight gate)

```
baseline   = 0.6450   (sanity_ok=True; rail [0.62, 0.68])
reproduce  = 0.4500   (META_M6_ok=False; rail [0.08, 0.25]; smoke at intermediate-W: N=2048 n=50 d=10 -> 500 bindings)
v1_doc     = 0.8500   (V1_DOC_ok=True; rail [0.60, 0.90]; smoke v1 regime: N=2048 n=20 d=5 -> 100 bindings)
K5_perhop  = 0.4000   (smoke matched-pv2-regime; 500 bindings)
K15_perhop = 0.5000   (smoke matched-pv2-regime; 500 bindings; +0.05 lift over K=1 single-chain)
```

Smoke REPRODUCE landed at 0.45 (above [0.08, 0.25] full rail). This is **expected smoke behavior** at
intermediate W-bindings (500 smoke vs 2000 full); the prereg smoke-regression-guard threshold (> 0.50)
was NOT breached. Full run at N=8192 with 2000 bindings is where the verdict happens; expected to land
near pointer-chain v2's known 0.122.

**Note:** Smoke shows K15 (0.50) > K1 (0.45) > K5 (0.40) — NOT monotonic. At smoke scale this is
unreliable (1 seed, 20 test queries). Full run is the verdict.

## Self-test results (all 9 PASS)

- T1: bipolar/ingest_hebbian/make_deep_chains construction self-consistent
- T2: K=1 noise=0 at small-W regime beats chance (0.950 > 0.083)
- T3: large-W < small-W at selftest scale (0.425 < 0.950) — crosstalk-is-load-bearing
- T4: K=5 per_hop diversity > 0 (vote mechanism active)
- T5: vote_at_end != vote_per_hop math (protocols distinct)
- T6: NaN guard at N=4096 production-scale
- T7: bands locked (asserts exact numeric values)
- T8: LLM call counter == 0 (substrate-only)
- **T9: Cell X v1 _one_chain_step (K=1 noise=0) EQUIVALENT to pointer-chain v2 _retrieve_1hop**
  (verified identical argmax index)

## What this cell answers

- If `HARD_FAIL_PARALLEL_DOESNT_HELP` at matched regime: parallel voting cannot revive Barrier 1 even
  when the mechanism is the same as pointer-chain v2; errors through W are correlated. Retire parallel
  voting as Barrier 1 candidate.
- If `HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE`: USER-proposed mechanism is chain-grade-eligible
  at matched regime; route to Skunkworks for landed-VET tier classification.
- If `META_M6_RAIL_VIOLATION`: Stage-1 analysis is wrong; ARM_REPRODUCE doesn't reproduce pointer-chain
  v2 at IDENTICAL regime. Cell X v2 itself needs re-design.

## Cell X v1 disposition

Cell X v1's 0.78 single-chain 5HOP is **NOT a legitimate Barrier-1 revival**. It is a regime artifact.
Recommend Research treat Cell X v1 metrics as **uninterpretable for Barrier 1 revival claim** until Cell
X v2 lands. Do NOT atomize Cell X v1 as Barrier 1 revival even if Skunkworks tier-routes it MIDDLE_BAND.

## Notifications

- Research: this note + reactive on full verdict
- Skunkworks: landed-VET candidate on full landing (HARD_PASS path); cert-routing on any verdict
- Orchestrator: queue running on local_cpu (visible via queue_status.py)

## Bias-check checklist applied

- BIAS-Q (suspect 1.000): per-step accuracy reported per-arm; will flag in verdict_msg if any depth-5
  step hits 1.00 at V_C=200 (W-saturation tell)
- BIAS-Q non-monotonic K (K5 > K15): explicit monotonic check in verdict; v1 already showed this pattern
- Fix #28: per-arm metrics fully reported (top1 + per_step_acc + diversity + cv per arm)
- Fix #26 (verify-the-referent): Stage-1 line-level diff replaces "trust the verdict_msg" with
  "read the cleanup primitive code"
- META_M6: this is THE rail; if it breaks, the entire stack of comparisons is uninterpretable
- BIAS-O (basis vs use-case): regime (W-binding count) is the basis property; K=1/5/15 + per_hop/at_end
  vote protocols are the use-case readout
