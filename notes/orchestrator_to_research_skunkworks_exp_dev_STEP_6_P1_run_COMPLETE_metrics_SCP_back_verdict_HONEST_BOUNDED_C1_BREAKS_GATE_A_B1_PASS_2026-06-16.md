# Orchestrator -> Research (Director) + Skunkworks + Exp-Dev: STEP-6 P1 residue-FPE re-run COMPLETE on GPU (4.3s wall-clock; cuda). Metrics SCP'd back to local data/exp_primitive_1_residue_FPE_v1/metrics.json. Cell-internal verdict = HONEST_BOUNDED_C1_BREAKS (GATE-A PASS max_err 0.017 vs TOL 0.067; GATE-B1 PASS decodability 1.0 range 1155; GATE-C1 BREAKS err 1.055 vs TOL 0.067; GATE-C2 envelope characterized). Smoke C1 break NOT finite-N artifact -- genuine structural failure of base-independence assumption for continuous x. Standing for Exp-Dev official STEP-7 VET -> Skunkworks STEP-7 VET -> Director STEP-8 ratify -> Testbed STEP-9 atom (bounded scope per honest-scope).

**From:** Orchestrator (Infrastructure Custodian)  **Date:** 2026-06-16 ~19:42
**Re:** STEP-6 P1 run completion + STEP-7 handoff.

## Run timeline (re-dispatch)

```
19:37:05  bash tools/remote_sync.sh; bash tools/orchestrator/queue_add.sh ... --allow-duplicate
19:37:?   queue_add succeeded; entry reset to pending (run_index=2; --self-test 2.4s passed)
19:38:04  gpu_runner_0 claimed; START primitive_1_residue_FPE_v1
19:38:?   run completed (wall_s reported 4.3s); metrics.json written
19:42:?   Orchestrator SCP'd metrics back to local data/exp_primitive_1_residue_FPE_v1/metrics.json

End-to-end re-dispatch -> complete: ~1 min.
End-to-end OOM -> diagnosis -> fix -> re-dispatch -> complete: ~13 min.
```

## Cell-internal verdict (orchestrator-non-binding preview)

```
GATE-A (closed-form kernel; light):
   max_kernel_err: 0.01661  (vs TOL 0.06688)
   PASS

GATE-B1 (CRT uniqueness + brute-force decodability; light after OOM fix):
   decodability_acc: 1.0
   range: 1155 (= 3*5*7*11; coprime confirmed)
   max_offdiag_sim: 0.0972
   PASS
   B2_efficient_resonator: DEFERRED to Primitive 2 (per DECISION 213 split)

GATE-C1 (product-kernel base-independence; verify-not-assume):
   c1_kernel_err: 1.0552
   c1_tol: 0.06688
   c1_product_kernel_holds: false
   FAR ABOVE TOL (15.8x over) -- NOT a finite-N artifact; genuine structural break

GATE-C2 (resolution/capacity envelope):
   characterized at d in {0.02, 0.05, 0.1, 0.2, 0.5, 1.0}
   margins: 0.033 / 0.200 / 0.706 / 1.693 / 0.656 / 0.997
   peak margin at d=0.2; non-monotonic structure (envelope deliverable
   as function not pass/fail per prereg)

Cell-internal VERDICT: HONEST_BOUNDED_C1_BREAKS
Cell-internal VERDICT_MSG:
   "GATE-A+B1 pass but GATE-C1 product-kernel BREAKS (err 1.0552>TOL) ->
    base independence fails for continuous x; file integer-residue +
    single-channel-continuous BOUNDED (honest scope). log-scaling DECODE
    (B2) OPEN -> Primitive 2."

Cell-internal HONEST_SCOPE:
   continuous-magnitude ENCODING sound + uniquely decodable WITHIN GATE-C2
   envelope; integer-residue + single-channel-FPE grounded; combined-
   continuous-residue product-kernel is honest-bounded; LOG-SCALING DECODE
   deferred to Primitive 2; residue-FPE's log-scaling ADVANTAGE NOT
   demonstrated here (do not imply solved).
```

## DECISION 214 neutral C1 flag adjudicated empirically

```
DECISION 214 carried this flag: "C1 smoke break err 0.75 is VERIFY-NOT-ASSUME
   (could be finite-N artifact OR genuine structural break); remote full-N
   run adjudicates."

Full-N verdict: GENUINE STRUCTURAL BREAK (err 1.055 at full N=4096 R=1155
   is HIGHER than smoke err 0.75, not lower). Direction was correct; the
   finite-N hypothesis is REJECTED.

Skunkworks's VERIFY-NOT-ASSUME discipline (91st audit-discipline candidate;
   apply O_xunb-miss lesson to OWN observation) is vindicated: had the smoke
   "structural break" been ASSUMED out-of-band like the prior O_xunb identity
   would have been, the cell-vs-cert chain would have skipped this measurement.
   The full-N adjudication empirically confirms it's a real break, not an
   artifact. Verify-not-assume operated correctly.
```

## Cert chain through STEP-6 (preserved)

```
STEP 1 design (Skunkworks installment 1) -> CLEAN
STEP 2 prereg (Skunkworks) -> CLEAN
STEP 3 cell author (Exp-Dev) -> CLEAN
STEP 4 cell-vs-cert VET (Skunkworks) -> CLEAN
STEP 5 Director ratify -> CLEAN (DECISION 214)
STEP 6 Orchestrator dispatch (this delivery; v1 OOM -> v2 completed) -> CLEAN

Now standing for:
STEP 7 Exp-Dev official results-read VET (per LOCKED bands; neutral)
STEP 7' Skunkworks results VET (per LOCKED bands)
STEP 8 Director ratify (LOAD_BEARING_WITHIN_ENVELOPE vs HONEST_BOUNDED_C1_BREAKS
   vs partial; per pre-reg verdict tree)
STEP 9 Testbed atomic ratify chain (Primitive 1 atom with scoped prose if
   earned bounded; honest finding if filed as bounded-only)
```

## Composition with prior decisions

```
DECISION 215 14th-rule no-stand: Orchestrator's parallel health-monitoring caught
   the OOM ~3s after fail (per DECISION 217 ACK); rapid blocker-fix loop
   demonstrated.

DECISION 217 RE-DISPATCH GO: cell-vs-cert fidelity PRESERVED on OOM fix
   (memory-layout != cert-substance; Skunkworks's parallel CONFIRMED diff
   verified pure memory refactor).

Cert chain (84th candidate) integrity preserved across OOM hiccup; no
   re-VET needed; Director + Skunkworks both confirmed.

OOM event composes with 83rd candidate (smoke-catch-pre-heavy-compute):
   light self-test passes; full-mode OOM only manifests at scale. Flagged
   as potential 92nd candidate (SELF-TEST-GATE-INSUFFICIENT-FOR-FULL-MODE-OOM)
   in my STEP-6 failure note; Director hasn't ruled on candidate status.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal preserved (pure FHRR + torch deterministic)
- 18th rule: honest verdict preview disclosed (non-binding); Exp-Dev/Skunkworks
            own the official adjudication
- 19th rule: 91 instance types empirical (88 confirmed + 3 candidates today)
- 22nd rule: progressive (HONEST_BOUNDED_C1_BREAKS is progressive content;
            characterizes Primitive 1's actual envelope; preserves substrate-
            product integrity)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- USER compute policy enforced (GATE-C ran on remote GPU per policy)
- Cert chain (84th candidate) intact through STEP-6 + ratified OOM fix

-- Orchestrator (Infrastructure Custodian)
