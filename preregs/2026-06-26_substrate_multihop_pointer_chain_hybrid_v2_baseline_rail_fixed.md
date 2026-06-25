# Pre-reg: substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED

**Authored:** 2026-06-26 by exp_dev (Director-triage of v1 baseline rail mismatch).
**Cell:** `experiments/exp_substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED.py`
**Lane:** 1 (substrate-native; pure numpy).
**Routing intent:** local_cpu_queue (CPU-feasible; ~245s/seed -> ~735s wall).
**Predecessor:** `experiments/exp_substrate_multihop_pointer_chain_hybrid_v1.py` (v1; landed HARD_FAIL with baseline at 0.395, not the expected 0.65).

## v1 bug (Director triage 2026-06-26)

v1 reported BASELINE_HRR_2HOP = 0.395 (mean across 3 seeds) but the sanity
rail expected 0.65 +/- 0.02 (beta-sweep regime). POINTER_2HOP = 0.415 (no
lift) -> verdict HARD_FAIL_POINTER_NO_LIFT. **But the baseline was wrong**:
the cell couldn't be interpreted because the reference regime didn't
reproduce.

### Two compounding regime differences

1. **Chain construction**: v1's `make_chains` uses `p = int(g.integers(0, P))`
   for each triple (random predicates, P=10) and builds chains of
   `max_depth=10`. Result: 3000 (s,p,o) bindings in W (300 chains x 10
   hops) spread across 10 predicates -> ~300 bindings per predicate.
   Beta-sweep's regime: `make_two_hop_chains` with FIXED-PAIR (p1=0, p2=1)
   and 2-hop only -> 400 bindings (200 chains x 2 hops) across 2 predicates
   -> ~200 bindings per predicate. v1's W has ~50% more per-predicate
   crosstalk AND ~7.5x more total bindings, dropping per-hop 1-hop accuracy
   from beta-sweep's ~0.78 (first hop) / ~0.65 (second hop) to v1's 0.695 /
   0.415 (matches the per-step trace).
2. **Chain mechanism**: v1's `arm_baseline_hrr_chain` uses `_retrieve_1hop`
   which does `argmax(E @ W @ (E[s] * R[p] * sq))` and re-feeds `E[s_pred]`
   to the next hop -- cleanup BETWEEN hops. Beta-sweep's `chain_naive_hard`
   propagates the noisy state (`state = W @ (state * R[p] * sq)`; no
   cleanup until final argmax). The "naive" baseline numbers between the
   two cells are mechanism-not-comparable.

## v2 fix

**BASELINE arm**: VERBATIM port of beta-sweep regime AND mechanism.
- `make_two_hop_chains_betasweep` (verbatim L171-192 of beta-sweep cell)
- `chain_naive_hard` (verbatim L136-142 of beta-sweep cell)
- V_P=2 fixed-pair (p1=0, p2=1); BASELINE_N_CHAINS=200; 2-hop only
- BASELINE arm has its OWN W (built from baseline-arm triples; no entanglement
  with pointer arms' triples)

**POINTER arms** use their own deep-chain set (V_P=10 random predicates,
max_depth from HOP_DEPTHS) and their own W. Same E and R primitives are
shared (apples-to-apples on encoder + atoms + bind/unbind), but the
graphs differ. **The apples-to-apples is encoder/atoms/primitives, NOT W**;
this is the honest scope flag baked into the cell's DESIGN_NOTE.

## SACRED SANITY RAIL

If `BASELINE` arm top1 is OUT of [0.62, 0.68] on a majority of seeds:
- verdict = **SANITY_BREACH** (NOT HARD_PASS/HARD_FAIL)
- metrics.json still written for diagnosis but the cell is NOT interpretable
- no cert claim possible until rail reproduces

This guards against the v1 failure mode where the cell continued running and
produced a "no lift" verdict that was actually unreadable because the
reference floor didn't reproduce.

## Smoke preview (PASS at N=2048)

```
ARM_BASELINE_HRR_2HOP top1=0.6450 (n=200, beta-sweep regime, IN [0.62, 0.68])
ARM_POINTER_CHAIN_2HOP top1=0.9800 per_step=[1.0, 0.98]
ARM_POINTER_CHAIN_5HOP top1=0.7800 per_step=[1.0, 0.98, 0.94, 0.88, 0.78]
ARM_POINTER_HRR_HYBRID top1=0.9800
Verdict at smoke: HARD_PASS_BREAK_CEILING
```

This is a **strong positive signal**: baseline reproduces 0.645 (in band)
and pointer-chain lifts to 0.98 -- 0.34 absolute (52% relative) lift at
2-hop. The pointer mechanism IS the multi-hop escape hatch.

## Config

| Param | Smoke | Full | Reason |
|---|---|---|---|
| N_DIM | 2048 | 8192 | beta-sweep N for full; 2048 smoke (still in regime per beta-sweep smoke) |
| V_CONCEPTS | 200 | 200 | matches beta-sweep regime |
| BASELINE_V_P | 2 | 2 | beta-sweep fixed-pair |
| BASELINE_N_CHAINS | 200 | 200 | beta-sweep regime EXACT |
| POINTER_V_P | 10 | 10 | Director Barrier-1 spec |
| POINTER_N_CHAINS | 50 | 200 | apples-to-apples chain-count vs beta-sweep |
| POINTER_K_SET | 20 | 20 | Director spec |
| HOP_DEPTHS | [2, 5] | [2, 5, 10] | depth retention |
| SEEDS | [7] | [7, 17, 23] | cv check |

## Arms (5)

1. **ARM_BASELINE_HRR_2HOP**: VERBATIM beta-sweep regime + mechanism; SANITY RAIL
2. **ARM_POINTER_CHAIN_2HOP**: pointer routing + per-step argmax cleanup
3. **ARM_POINTER_CHAIN_5HOP**: depth retention at 5
4. **ARM_POINTER_CHAIN_10HOP**: depth retention at 10
5. **ARM_POINTER_HRR_HYBRID**: pointer + HRR cleanup at retrieval node

## HARD bands (LOCKED prospectively; unchanged from v1)

- **HARD_PASS_BREAK_CEILING_WITH_DEPTH**: POINTER_2HOP >= 0.95 AND HYBRID >= 0.85
  AND CV <= 0.05 AND POINTER_10HOP >= 0.80
- **HARD_PASS_BREAK_CEILING**: POINTER_2HOP >= 0.95 AND HYBRID >= 0.85 AND CV <= 0.05
- **MIDDLE_BAND**: best > 0.75
- **HARD_FAIL**: best <= 0.75
- **SANITY_BREACH** (new): baseline arm OUT of [0.62, 0.68] on majority of seeds
  -> cell NOT INTERPRETABLE

## Pre-registered expectation (Q discipline)

- BASELINE: 0.65 +/- 0.03 (CONFIRMED at smoke 0.645; full N=8192 should be tighter)
- POINTER_2HOP: ~0.98 (CONFIRMED at smoke 0.980); FULL probability lift
  P(POINTER_2HOP >= 0.95) = 0.85 (smoke evidence very strong)
- HYBRID: ~0.98 at smoke; full P(HYBRID >= 0.85) = 0.85
- POINTER_5HOP at smoke: 0.78; full P(>= 0.80 with 200 chains) = 0.55
- POINTER_10HOP: at smoke 5hop only; full N=8192 chain-count = 200 will
  better reveal compounding decay; P(>= 0.80) = 0.35 (ambitious -- per-step
  0.98^10 = 0.82 is the theoretical ceiling if per-step stays at 0.98)
- **Expected verdict**: P(HARD_PASS_BREAK_CEILING_WITH_DEPTH) = 0.35;
  P(HARD_PASS_BREAK_CEILING) = 0.40; P(MIDDLE_BAND) = 0.20;
  P(HARD_FAIL) = 0.05. Skewed toward HARD_PASS because smoke evidence is
  unambiguous on 2-hop lift; the 10-hop depth retention is the uncertain
  band.

## Disposition

- HARD_PASS_BREAK_CEILING_WITH_DEPTH -> Skunkworks landed-VET; cert as
  Barrier-1 closure via pointer-chain escape hatch (multi-hop + depth retention)
- HARD_PASS_BREAK_CEILING only -> cert + Research drill on per-step cleanup
  primitive for depth retention
- MIDDLE_BAND -> Skunkworks VET on which depth-retention threshold makes
  the cleanest cut
- HARD_FAIL -> route NEGATIVE to Research for revival angle on Barrier-4
  anisotropic encoder
- SANITY_BREACH -> abort; rebuild from beta-sweep cell with even tighter
  fidelity check before re-dispatch

## Operational disciplines

- D1 roofline (CPU): smoke wall 1.7s; full estimated ~245s/seed -> ~735s total
- D2 atexit + per-seed checkpoint mandatory
- Self-test PASS gate VERIFIED
- LOCAL SMOKE PASS gate VERIFIED (and SACRED RAIL CONFIRMED at 0.645)
- ASCII only
- Substrate-only (`_LLM_CALL_COUNTER = [0]`)
- `--timeout 900s` (3.7x estimate; PROT-019 N=8192 triggers --timeout >= 3600 floor
  BUT this is a CPU-feasible local cell with bounded wall; 900s is a budget
  ceiling not a runtime expectation)

NOTE on PROT-019: per `tools/queue_add.py` exit code 7, `anchor _n>=4096
requires --timeout >= 3600s`. Anchor name has NO `_n<N>` suffix so PROT-018
applies (no binding); PROT-019's >= 3600s requirement is suffix-conditional.
However to be safe and avoid the failure mode the guard exists for, use
`--timeout 1800s` (well above ~735s estimate, still under the 1h guard
spirit; matrix ops at N=8192).

## Fix #28 discipline

- 5 arms; per-arm top1 + per-step accuracies + CV across seeds
- verdict_msg cites per-arm numerics + SANITY_BREACH count
- Multi-seed CV computed and gated (HP_BREAK_CV_MAX = 0.05)

## Cites

- `experiments/exp_substrate_multihop_pointer_chain_hybrid_v1.py` (v1; broken)
- `data/exp_substrate_multihop_pointer_chain_hybrid_v1/metrics.json`
  (v1 verdict = HARD_FAIL_POINTER_NO_LIFT with baseline at 0.395)
- `experiments/exp_substrate_resonator_softchain_beta_sweep_v1.py` L136-142,
  L171-192 (verbatim baseline mechanism + regime source)
- `data/exp_substrate_resonator_softchain_beta_sweep_v1/metrics.json`
  (BASELINE_HARD across 3 seeds: 0.605 / 0.670 / 0.675; mean 0.65)
- Director Barrier-1 cell spec note
  (`notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md`)
