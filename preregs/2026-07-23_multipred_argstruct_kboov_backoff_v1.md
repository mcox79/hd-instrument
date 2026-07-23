# Prereg: multipred_argstruct_kboov_backoff_v1

## Question
Does an OOV back-off / class-smoothing fix (Clark & Weir 2002) let the scaled selectional-knowledge
table's isolated 2AFC win (29479, +0.199) transfer to the parser-integrated multi-predicate reader,
given the precisely-diagnosed COVERAGE bound in 29483/29484 (kept_hash(V3_INTEGRATED) ==
kept_hash(V3_KNOWLEDGE_SCRAMBLE); scrambling the table changed ZERO picks because OOV=-1.0 always lets
the covered candidate win regardless of its own rating)?

## Mechanism (ONE variable)
Replace 29483's OOV=-1.0 sel_fn with a three-tier graded back-off:
TIER0 item-specific (exact verb|noun rating) -> TIER1 verb+WordNet-noun-supersense class average ->
TIER2 verb average -> TIER3 global mean. Never returns None; every competition becomes a graded
comparison. Assignment mechanism, learned gate, role-assignment clf, parser training: ALL byte-identical
reuse of 29483's own code (imported via `experiments.exp_multipred_argstruct_agentfix_kbgate_v3`).

## Compute architecture
Class (b) sequential-CPU with justification. Reuses 29483's arc-eager parser training + per-clause
greedy decode + AveragedPerceptron classification + O(candidates) dict lookups (assignment walk +
back-off table lookup, O(1) after one-time O(|table|) precomputation of class/verb aggregates). No
matmul/storage/GPU-batchable primitive. Storage: no_storage. LOCAL-ONLY, foreground-to-completion,
NO push / NO remote-persist / NO queue_add (inline-local routing task; not banked, skunkworks VETs
separately).

## Functional requirements
- OOV competitor gets a graded plausibility estimate instead of a hard -1.0 sentinel -> existing
  primitive addressed: none (this cell IS the new mechanism under test; no prior chain-grade primitive
  maps to "class-conditional selectional back-off" in this substrate yet).
- Knowledge-scramble control must become able to fire (flip >=1 pick) if the fix is genuine.

## Fairness
Same reader/gold/split/parser-training-budget/clf/gate as 29478/29483. Gold =
`data/gold_mcguffey_lccp_argstruct_v1.json` (independent, single-annotator, never read while authoring
this fix). FULL_SLICE = L04/L05/L07/L08/L09/L10/L12; SMOKE_SLICE = L04/L05.

## Pre-registered bands (set BEFORE running; grounded on 29483's own landed MEASURED numbers)
Cited anchors: F1(V3_INTEGRATED, no-backoff)=0.5738; F1(V3_PARSEFIX_ONLY)=0.4651;
F1(V3_KNOWLEDGE_SCRAMBLE)=0.5738 (identical to INTEGRATED -- the bound), all
MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json.

**HARD_PASS_BACKOFF_TRANSFERS_KNOWLEDGE** (ALL must hold):
1. `n_flipped_new_scheme >= 1` -- knowledge-scramble control now flips at least one pick.
2. `flip_fraction_new >= 0.05` -- not a lone coincidental flip.
3. `F1(V4_KNOWLEDGE_SCRAMBLE_BACKOFF) <= F1(V4_INTEGRATED_BACKOFF) - 0.02` -- scramble hurts F1.
4. `F1(V4_INTEGRATED_BACKOFF) > 0.5738 + 0.01` -- lifts past the pre-backoff structural number.
5. `F1(V4_INTEGRATED_BACKOFF) > 0.4651` -- still beats the no-knowledge parsefix-only number.
6. `F1(V4_ARCSCRAMBLE_BACKOFF) <= F1(V4_INTEGRATED_BACKOFF) - 0.05` -- structural control still fires.

**HARD_FAIL_COVERAGE_ARTIFACT_CONFIRMED_EVEN_WITH_BACKOFF** (ANY triggers):
1. `n_flipped_new_scheme == 0` -- scramble STILL cannot flip a single pick even with graded back-off.
2. `F1(V4_KNOWLEDGE_SCRAMBLE_BACKOFF) >= F1(V4_INTEGRATED_BACKOFF) - 0.01` -- control fails to fail.
3. `F1(V4_INTEGRATED_BACKOFF) <= 0.5738` -- back-off adds nothing beyond the pre-backoff number.

**MIDDLE_BAND**: otherwise. Report failing condition(s) + `tier_usage` / `n_tied_competitions_backoff`
diagnostic (per atom 29471's supersense-coarseness caveat) + whether item-level table density (not class
smoothing) is the deeper remaining lever.

## Calibration probe band-width
N/A -- this is NOT a calibration probe with no prior empirical anchor. Bands are grounded directly on
29483's own landed MEASURED F1 numbers (tight decisive band, per policy for anchor-having cells).

## Discriminator
Discriminator = the knowledge-scramble must-fail control (`V4_KNOWLEDGE_SCRAMBLE_BACKOFF`). MUST be able
to fire post-fix (29484's landed finding was that it did NOT fire pre-fix: 0 picks changed). Smoke-gate
verifies via the scaffold-free witness (`eat`+branches-vs-nut) that back-off mechanically CAN flip a
pick; the FULL run's aggregate `n_flipped_new_scheme` + F1 gap are the load-bearing must-fail checks.

## CRLB / capacity-feasibility
`crlb_n/a`: discrete count/precision measurement (F1 over kept argument tuples), no HD noise floor or
matmul-derived variance; CRLB formula does not apply.

## Cardinality
No swept axis besides the fixed 9-arm comparison. `EXPECTED_N_ARMS = 9`; self-test asserts
`len(scored) == 9`. Competition-log cardinality cross-check: `len(comps_old_real) ==
len(comps_old_scr) == len(comps_new_real) == len(comps_new_scr)` (the competition SET is sel_fn-
independent; a divergent length is an instrumentation bug, asserted at runtime).

## Arms-differ / atomicity / exception ordering
- `arms_differ_verified`: hash test over all 9 arms' kept-tuple sets. `V4_INTEGRATED_BACKOFF` vs
  `V4_KNOWLEDGE_SCRAMBLE_BACKOFF` EXEMPTED at SMOKE scale only (same small-sample rationale 29483 used
  for its own analogous pair); FULL run's `n_flipped_new_scheme` + F1 gap are load-bearing.
- `final_metrics_atomicity: tmp_replace` (os.replace).
- `except SystemExit / KeyboardInterrupt: raise` BEFORE `except Exception` (no bare/BaseException).

## Baseline-in-band
`baseline_in_band`: `0.05 < precision(BASELINE) < 0.95` asserted at smoke.

## Calibration-check field
`calibration_check: "default_ok_for_this_regime"` -- reuses 29483's exact regime (same slice/parser
budget/clf/gate); the only new element is the back-off table lookup, itself deterministic and bounded
in [0,1] by construction (weighted averages of ratings already in [0,1]).

## Determinism
Fixed int `SEED = 20260725`; `sorted(dict.keys())` for scramble permutations; `numpy.random.default_rng`
(seeded); no `hash()`-seeded RNG anywhere in this cell or its reused 29483 code.

## Numbers tagging (META_RULE_AC)
- F1(V3_INTEGRATED)=0.5738: `CITED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1`
- F1(V3_PARSEFIX_ONLY)=0.4651: `CITED@` same file `:arms.V3_PARSEFIX_ONLY.f1`
- F1(V3_KNOWLEDGE_SCRAMBLE)=0.5738: `CITED@` same file `:arms.V3_KNOWLEDGE_SCRAMBLE.f1`
- isolated_2afc_lift=0.199: `CITED@data/exp_pivot_scaled_seed_knowledge_table_v1/metrics.json`
- `eat|branches=0.15`, `noun.plant` class avg for `eat`=0.6067 (acorn=0.9, acorns=0.9, firs=0.02):
  `MEASURED@` ad-hoc verification script against `data/exp_pivot_scaled_seed_knowledge_table_v1/scaled_seed_table_v1.json` + nltk WordNet `lexname()`, reproduced inside this cell's own `self_test()` witness.
- All arm F1/precision/recall/kept_hash/flip-count numbers: `MEASURED@data/exp_multipred_argstruct_kboov_backoff_v1/metrics.json` (this cell's own FULL landing).

## Timeout estimate
29483's own FULL run (byte-identical parser training + ~7 clause-decode passes) landed at
`elapsed_s=225.2` (`MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json`). This cell
adds 5 more clause-decode passes (comps_old_real, comps_old_scr, comps_new_real, arcscramble_backoff,
comps_new_scr) on the SAME slice/parser -- no re-training, no matmul, O(candidates) work per pass.
Estimate: `ceil(225.2 * (7+5)/7) ~= 386s`. Foreground-to-completion via Bash tool with a long blocking
timeout (up to 600s); no queue_add (inline-local contract, pause-state ACTIVE).

## Progress logging
`print(..., flush=False)` acceptable -- wall time well under the 30-min heartbeat mandate threshold;
runner invokes via `python -u` regardless (defense-in-depth already present via stdout reconfigure).

## Contract
INLINE-LOCAL, FOREGROUND-TO-COMPLETION. No remote/GPU. Glass-box (from-scratch parser + curated dict +
corpus-observed table + WordNet lexname lookups, local only; NO LLM/network/autograd at inference).
Commit cell + prereg + metrics.json by EXPLICIT PATH (never `git add -A`). Do NOT bank this
cell -- skunkworks VETs it separately.
