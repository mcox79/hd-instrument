# Pre-registration: INTERACTION_ASYMMETRIC_DIRECTED_OPERATORS (v1)

**Cell:** `experiments/exp_interaction_asymmetric_directed_operators_v1.py`
**Anchor:** `interaction_asymmetric_directed_operators_v1`
**Design source:** `notes/research_brain_asymmetric_directed_relation_operators_2026-07-15.md`
**Arena reused verbatim:** `exp_interaction_bilinear_wall_break_v1.py` (29b53e63b) + `exp_interaction_nonadditive_discovery_v1.py` (59056b6d4).
**Filed:** 2026-07-15. Bands FIXED before the FULL run.

## Question
The landed bilinear cell HARD_FAILed dominance (BILINEAR_dom=0.485 vs role-keyed 1.000; ties elementwise) because
its final composition step is a **commutative Hadamard product over K factors** -- order-blind by construction.
Do any of THREE brain-theorized directed/asymmetric operators read DOMINANCE (asymmetric non-additive) on NOVEL
combos at/above the role-keyed specialist, where the bilinear failed -- by changing the FOLD, not the factors?

## Compute architecture
- Class **(b) sequential-CPU with justification**: ~75 independent small SGD trainings (5 seeds x 5 families x 3
  regimes), each ~15s; per-arm training is individually sub-2s. No GPU batching: (i) the arena is tiny (N_ENT=220,
  EMB_D=48, 48x48 transition matrices), (ii) the cell MIRRORS the already-landed CPU bilinear cell exactly for
  direct numeric comparability (same seeds/hyperparams), (iii) total wall ~19min < the batching-mandate threshold
  for a from-scratch redesign. Storage strategy: **no_storage / no_composition** (in-memory numpy/torch arrays; no
  substrate PartitionedStore). `progress_logging: print_flush_true` + `line_buffered_stdout`; heartbeat + per
  (seed,family) log line (cadence ~15-40s).

## Arms
| Arm | Class | Mechanism |
|---|---|---|
| INT_MATCH, MONO | construction-proof | reused verbatim; arena sanity (INT_MATCH exercises REAL FHRR bind) |
| LEARN_SYM | learned | shared code + product (symmetric / parity specialist / elementwise reference) |
| LEARN_INT, LEARN_ADD | learned | role-keyed product / sum; ROLE_KEYED = max(these) = incumbent asymmetric specialist |
| BILINEAR_REF | learned | LEARN_BILINEAR_RANK1 re-run in SAME seeds (the failed reference, controlled) |
| **TRANSITION_OP** | learned, NEW | shared code + non-commutative matrix chain `s_i=(M_i @ s_{i-1}) (*) e[x_i]` (mechanism 1) |
| **TRANSITION_OP_SHUFFLED_ORDER** | diagnostic, NEW | same trained M_i, TEST-time permuted slot order (reported) |
| **HETEROASSOC_OP** | one-shot Hebbian CONSTRUCT, NEW | `W = onehot(y)^T @ rolefiller(X)`, zero SGD (mechanism 2) |
| **PHASE_ORDER_OP** | learned, NEW | learned shared phasor code + fixed per-role phase offsets + FHRR product bind (3) |
| **PHASE_NO_OFFSET** | diagnostic, NEW | same but theta_i=0 (attribution control, reported) |
| FREQ_NULL, MEMORIZE, POP, ORACLE | baselines | reused verbatim |

Same EMB_D=48, EPOCHS=500, LR=0.05 for every learned arm (fairness). Same 5 seeds (7,13,17,23,29).

## FAITHFUL-BUILD CORRECTIONS (cell-author functional-requirement checks; documented, not silent)
1. **TRANSITION_OP grouping.** The design writes `s_i = M_i @ (s_{i-1} (*) e[x_i])`. Read literally, step 1 is
   `M_1 @ (e[x0] (*) e[x1])`, which is **symmetric in slots 0,1** (Hadamard commutes) -> the op cannot represent
   antisymmetric DOMINANCE (y=x0>x1) by construction (a guaranteed non-informative HARD_FAIL). The cell uses the
   grouping that realizes the STATED TEM mechanism (`g_{t+1}=f(W_a,g_t)`: transform the running STATE, then bind
   the new content): `s_i = (M_i @ s_{i-1}) (*) e[x_i]`. This IS asymmetric in (x0,x1) and at init M_i=I reduces
   EXACTLY to the elementwise product == LEARN_SYM. Both facts asserted in `--self-test`
   (`transition_asymmetric_in_slots01`, `transition_init_reduces_to_elementwise`).
2. **HETEROASSOC feature keys all K slots** (design text illustrates x0,x1). Full-combo role-filler key matches the
   novelty granularity of `split_novel` and hands no arm which-slots-matter (fairness).
3. **SEEN stratum = in-sample (train-row) recall.** `make_X` samples all-UNIQUE combos, so every query combo is
   novel and the query "seen" stratum is always empty. The heteroassoc lookup diagnostic therefore uses SEEN =
   heteroassoc IN-SAMPLE recall of the memory built from train (the literature's recall-stored-vs-generalize
   framing). NOVEL = out-of-sample query.
4. **HETERO_D=2048** so memory capacity >> ~121 train combos, isolating NOVEL generalization failure as the clean
   lookup signal (a capacity-starved failure would be uninformative). SEEN recall is still crosstalk-bounded well
   below 1.0 (role-filler keys inherit combo-similarity; similar combos with conflicting labels crosstalk) -- this
   is a distributed-memory property, not a construction failure (mechanism correctness asserted separately on
   near-orthogonal keys: `heteroassoc_mechanism_correct >= 0.95`).

## Must-fails
Same ARBITRARY + SHUFFLE regimes, `MUSTFAIL_TOL=0.10`, applied to each gated candidate (TRANSITION_OP,
HETEROASSOC_OP, PHASE_ORDER_OP) over CLAIM_FAMILIES={PARITY,AND2,MULT,DOMINANCE} (ADD excluded). Each candidate's
NOVEL gap over FREQ_NULL on ARBITRARY/SHUFFLE must be `<= 0.10`, else that candidate fits noise -> its result void.

## Pre-registered bands (NOVEL CLEAN; TOL_SPEC=0.10; SAME constants as the landed bilinear cell)
For each candidate `OP in {TRANSITION_OP, HETEROASSOC_OP, PHASE_ORDER_OP}`:
```
dominance_ok(OP) = OP_dom >= ROLE_KEYED_dom - 0.10  AND  OP_dom - FREQ_dom >= 0.10  AND  OP_dom - SYM_dom >= 0.15
parity_ok(OP)    = OP_par >= SYM_par - 0.10  AND  OP_par >= chance_p + 0.20  AND  OP_par - LADD_par >= 0.15
                   AND OP_par - FREQ_par >= 0.15
mustfail_ok(OP)  = arb_gap(OP) <= 0.10 AND shuf_gap(OP) <= 0.10, all CLAIM_FAMILIES
```
Reference (MEASURED@data/exp_interaction_bilinear_wall_break_v1/metrics.json): role-keyed dom=1.000, FREQ_dom=0.778,
SYM_dom=0.477 -> the binding dominance_ok constraint is **OP_dom >= 0.90** (a genuine high bar).

### Attribution diagnostics (reported; gate MIDDLE vs HARD_PASS for a raw passer)
```
transition_order_confirmed    = TRANSITION_OP_dom - TRANSITION_OP_SHUFFLED_ORDER_dom >= 0.20
phase_attribution_to_role_tag = (PHASE_ORDER_OP_dom - PHASE_NO_OFFSET_dom) >= 0.20 AND |PHASE_ORDER_OP_dom - ROLE_KEYED_dom| <= 0.15
heteroassoc_lookup_confirmed  = HETEROASSOC_seen_dom - HETEROASSOC_novel_dom >= 0.30
```

## Verdict logic
- **REFUTE_IMPL** if INT_MATCH parity or dominance < 0.90 (arena/impl sanity).
- **HARD_PASS** = at least one candidate clears `dominance_ok AND mustfail_ok AND its attribution diagnostic`
  (for TRANSITION_OP: transition_order_confirmed; for PHASE_ORDER_OP: phase_attribution_to_role_tag; HETEROASSOC_OP
  has no positive-attribution gate -- an unexpected pass is accepted). Reports which candidate(s) cleared it.
- **MIDDLE_BAND** = a candidate clears the raw dominance_ok+mustfail threshold but FAILS its attribution diagnostic
  (unattributed win); OR HETEROASSOC clears dominance on SEEN but not NOVEL without heteroassoc_lookup_confirmed
  (under-diagnosed partial). Reported per-candidate, not averaged.
- **HARD_FAIL** = none of the three clears dominance_ok AND mustfail_ok (role-keying remains the best asymmetric
  construct on this arena).
- **BONUS (reported, not gating):** does a dominance-passing candidate ALSO clear parity_ok (one code doing BOTH)?

## Predicted outcome (design's honest call; HYPOTHESIZED, not asserted)
- TRANSITION_OP most likely to pass (P_deflated 0.48); strongest brain + already-validated GHRR precedent.
- HETEROASSOC_OP most likely to HARD_FAIL dominance on NOVEL (P 0.12) but confirm the lookup gap (P ~0.55) --
  informative negative. (Live risk: crosstalk-bounded SEEN may blunt a clean gap; reported.)
- PHASE_ORDER_OP most likely to fail or produce an unattributable pass (P 0.15); the fixed offset is provably
  absorbed under commutative product bind + linear readout, so PHASE_ORDER ~= PHASE_NO_OFFSET expected.
- Overall (>=1 candidate HARD_PASS): P_deflated = 0.42.

## SCHEMA-VET fields
```yaml
cardinality_ok: true            # EXPECTED_N_UNITS_PER_SEED=15; verdict counts n_units == 15*n_seeds
arms_differ_verified: true      # AF hash-test on DOMINANCE-clean-novel over 7 distinct mechanism arms
arms_differ_exempted:           # legitimately-may-coincide pairs (declared)
  - [TRANSITION_OP, TRANSITION_OP_SHUFFLED_ORDER]   # same model; equal iff order-invariant (the diagnostic)
  - [PHASE_ORDER_OP, PHASE_NO_OFFSET]               # offset provably absorbed -> equal output is the attribution result
  - [LEARN_INT, LEARN_ADD]                          # both dominance specialists; may both saturate to oracle
final_metrics_atomicity: tmp_replace
except_systemexit_before_exception: true            # no BaseException; no bare except
crlb_n/a: "top-1 accuracy discriminator; band feasibility set by MEASURED reference numbers (role_dom=1.0, INT_MATCH=1.0), not a noise floor"
discriminator_reachability: true                    # OP_dom>=0.90 reachable: INT_MATCH=1.0, role-keyed=1.0, TRANSITION seed-7 preview=1.0
baseline_in_band: true                              # SYM_dom~0.48, FREQ_dom~0.78, BILINEAR~0.49 (not saturated); INT_MATCH=1.0 is the solvability ceiling
calibration_check: "default_ok_for_this_regime"     # all hyperparams inherited from the landed bilinear cell (same arena)
cell_chunked: false                                 # single-process seed loop (mirrors landed bilinear cell)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
progress_logging: "print_flush_true"
defensive_error_checking: "passed_all_4_patterns"
deterministic_seeding: true                         # all RNG from integer indices/fixed generators; no hash()/list(set())
real_code_path_exercised: [hd_bind, _transition_compose, arm_heteroassoc, _train_phase]  # self-test constructs/calls each
substrate_signature_checked: [bind]                 # hd_bind = long-stable base signature (local+remote parity)
# Gate D positive control: BILINEAR_REF re-run in same seeds reproduces the prior HARD_FAIL (dom ~0.48) as a
# controlled in-cell reference (not cross-cited); INT_MATCH reproduces arena solvability (=1.0) at the test regime.
```

## Substrate-product implication
If TRANSITION_OP HARD_PASSes: converts "role-keying is our only working asymmetric construct" into "a brain-grounded,
order-sensitive-by-construction sequential matrix-chain operator ALSO works," reusing the validated GHRR
non-commutative-bind machinery in a new composition pattern -- a second, mechanistically-explained path to asymmetric
relation encoding directly relevant to the active AdditiveKGMap improvement thread. If it fails: role-keying remains
best; the three transferred brain mechanisms do not beat it on this arena.
