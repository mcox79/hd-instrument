# Pre-reg: exp_read_grow_relation_identity_v2 (POPULATION + GENUINE FAILURE-RATE)

Cell: `experiments/exp_read_grow_relation_identity_v2.py`
Trigger: Skunkworks landed-VET on v1 (commit 980eb1576), explicit expansion criterion verbatim: ">=4-6
authored relations with varied same-argtype collisions (not just fixed-order-vs-reciprocal), INCLUDING at
least one case designed to DEFEAT order-consistency+co-occurrence (to test the discriminator's genuine
failure rate, not just its success case), and ideally a CONFIRM_K>=3 corpus that stress-tests the
GROWTH-gate (not just post-hoc signature)."

## Prior-work check
Direct expansion of `exp_read_grow_relation_identity_v1` (VET-passed, commit 980eb1576), which already
carries its own substrate-KB concept-query (cosine 0.31-0.33, genuinely novel, not a rediscovery -- see
`preregs/2026-07-16_read_grow_relation_identity_v1.md`). This cell is a population/failure-rate/growth-gate
SCALE-UP of the same mechanism, not a new concept, per Director-routed VET follow-up; a fresh substrate-KB
query was not re-run (same mechanism class, same prior-work verdict applies).

## Design (population, verified empirically via a design-check script against the REAL FoundationStore
before authoring -- pair choices are not hand-guessed; see module docstring for the argtype/order/
co-occurrence derivation traced through the actual bootstrap-derived `type_profile`)

6 new same-arg-type ("animal-animal") relations, CONFIRM_K=3 (bumped from v1's K=2):
- `grims` (cat-dog / bird-frog, fixed-order) -- both pairs independently co-occur with known `chases` ->
  full sig `(True, True, {chases})`.
- `florps` (cow-dog, reciprocal -- roles reversed on exposure 2) -- order-INconsistent, no co-occurrence ->
  `(True, False, {})`. SEPARATES from grims on the order axis (same axis v1 tested).
- `krendles` (cat-bird, fixed-order, single pair x3) -- co-occurs with known `chases` -> `(True, True, {chases})`.
- `shleps` (cow-bird, fixed-order, single pair x3) -- no co-occurrence -> `(True, True, {})`. SEPARATES from
  krendles on the CO-OCCURRENCE axis (both order-consistent=True) -- a DIFFERENT separating axis than
  grims-vs-florps, satisfying "varied collision structures."
- `vorbs` (cat-frog / dog-bird, fixed-order) -- no co-occurrence -> `(True, True, {})`.
- `dringles` (cow-cat / dog-frog, fixed-order) -- no co-occurrence -> `(True, True, {})`.

**vorbs vs dringles = the REQUIRED DEFEAT CASE.** Both fixed-order (vacuously order-consistent) with EMPTY
co-occurrence (their argument pairs happen to touch no known/other-new relation). Full signatures are
LITERALLY IDENTICAL: `(True, True, frozenset())`. Two genuinely different relations (different words,
different argument pairs) collapse to the same widened signature. This was constructed by picking argument
pairs that are arg-type coherent (share a common accepted (rel,role) slot per animal, traced against the
real bootstrap) but touch no other relation's pairs -- the natural, non-contrived failure mode of a
signature whose third component is a co-occurrence SET that is empty whenever a relation doesn't happen to
overlap another relation's argument pairs (common in a small schema, not rare).

`shleps` empirically ALSO lands in this exact `(True,True,{})` bucket -- discovered during design-check, not
designed. The "no-cooccurrence fixed-order" equivalence class contains 3 of 6 relations, not 2. Reported
honestly (not hidden) as the population-wide all-pairs measurement below.

**Growth-gate stress (7th relation, `zant`, K=3-only, NOT in the 6-relation identity population):** cow-frog
pair observed in BOTH orders across 3 exposures (internally order-CONTRADICTORY) while remaining arg-type
coherent. Two growth-gate mechanisms compared: `ARGTYPE_GATE` (current production mechanism, identical
discipline to v1/openvocab_fastmap -- grows iff arg-type coherent) vs `FULL_STRUCTURAL_GATE` (hypothetical:
also requires order-consistency across the buffered exposures). EXPLORATORY, no pre-registered "correct"
direction.

**Seed variance (VET note: v1's signature is deterministic over a fixed corpus -- multi-seed was
pipeline-determinism, not a real probe):** the new-relation sentences (each relation's own internal exposure
order preserved) are round-robin-merge-shuffled across relations per seed. Verified genuinely different
interleave order per seed (design-check + self-test both assert `interleave_orders_genuinely_differ`), with
the MEASURED result being ROBUSTNESS-DESPITE-GENUINE-VARIATION (grown-sets + signatures identical across all
seeds tested) -- a stronger claim than "determinism because nothing varies."

## Bands (pre-committed BEFORE running; the defeat pair CAN fail the discriminator by design -- this is not
a vacuous pre-reg)

- **HARD-PASS:** `ablation_population_separated_frac == 0.0` (REQUIRED population-wide negative control) AND
  ORDER_PAIR(grims,florps) separates under FULL AND COOCCUR_PAIR(krendles,shleps) separates under FULL AND
  DEFEAT_PAIR(vorbs,dringles) does NOT separate under FULL (the required, honest failure) AND all 6+1
  relations legitimately grow under the production ARGTYPE_GATE AND violation rejected AND the K=3-threshold
  control (`trelps`, exactly 2 exposures) is NOT confirmed AND interleave-order robustness holds across seeds.
- **HARD-FAIL:** ablation separates ANY population pair (VACUOUS) OR either designed success pair fails to
  separate OR the DEFEAT pair unexpectedly separates (bug in the defeat construction, flagged as its own
  condition per the dispatching contract -- not silently reinterpreted as a discriminator win) OR growth
  breaks OR a regression control leaks.
- **MIDDLE_BAND:** all HARD-PASS gates hold except interleave-order robustness (a genuinely interesting
  order-dependence finding, not fatal).
- `population_separated_frac` (full and ablation) is reported DESCRIPTIVELY, not gated to an exact
  pre-committed number -- gating a population fraction discovered during corpus-design iteration to itself
  would be circular. The pairwise separate/collide gates above are the real pre-registered claims.
- `growth_gate_arm_invariant_at_k3` is EXPLORATORY/descriptive only.

## Schema-vet fields
- compute_architecture: sequential-CPU (foundation grows fact-by-fact; gate state depends on prior admits).
  wall < 1s (MEASURED 0.85s smoke, 0.48s full -- discrete logic, tiny corpus, 2 gate-mode arms x 5 seeds).
- storage_strategy: sharded (one VSA vector per accepted fact, via imported FoundationStore).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true. deterministic_seeding: true
  (fixed int seeds; sorted() vocab; per-seed interleave-shuffle RNG offset by +9000; no hash()/list(set())).
- real_code_path (F.1): self_test constructs the REAL imported objects (`ie_extract_openvocab`,
  `run_identity_loop` -> `FoundationStore`, `_relation_args_coherent`, `_order_consistency`,
  `_co_occurrence_with_known`) at full-tiny scale and asserts.
- crlb_n/a: no quantitative noise floor -- discriminator is discrete structural-signature comparison, not
  phasor decode noise. relation_query_acc MEASURED 1.00 under the production gate.
- discriminator-fires gate: verified at self-test AND smoke AND full -- ablation collides population-wide
  (0/15), FULL separates 11/15 (0.733) including both designed success pairs, and genuinely collides on the
  required defeat pair. A run where the ablation separates anything, or the defeat pair unexpectedly
  separates, is explicitly demoted to HARD_FAIL.
- arms_differ (META_RULE_AF): FULL vs ABLATION population-signature hashes differ (verified at self-test).
  `accepted_hash` is NOT compared across the two GROWTH-GATE arms (ARGTYPE_GATE vs FULL_STRUCTURAL_GATE) --
  those are EXPECTED to differ; that divergence IS the growth-gate-arm-invariance measurement, not a bug.

## Dispatch
Wall time sub-second (MEASURED 0.48s full, 5 seeds x 2 gate-mode arms) -- COMPUTE-PROPORTIONALITY: self-test,
smoke, and FULL all run INLINE/FOREGROUND locally, not through queue_add.sh / remote (matches v1's dispatch
precedent for this cell family; no GPU, no remote SCP, no atomize, no origin push, no remote-persist). Pause
flag `data/orchestrator_paused.flag` re-checked absent immediately before both smoke and full runs.

## Result (MEASURED @ data/exp_read_grow_relation_identity_v2/metrics.json, 5 seeds [11,23,37,41,53],
run_mode=full)
HARD_PASS (claim, VET-pending). population_separated_frac_full=0.733 (11/15 pairs); population_separated_
frac_ablation=0.000 (0/15 -- required control fired population-wide); ORDER_PAIR(grims,florps) separated_full
=True; COOCCUR_PAIR(krendles,shleps) separated_full=True; DEFEAT_PAIR(vorbs,dringles) separated_full=False
(genuine collision, the required honest failure -- both signatures literally `(True,True,[])`); all_grown_
all=True (6 identity relations + zant, under production ARGTYPE_GATE); relation_query_acc_mean=1.00;
violation_rejected_all=True; trelps_k3_not_confirmed_all=True; interleave_robust_across_seeds=True with
interleave_orders_genuinely_differ=True (genuine variance axis, robust result, not fake determinism).
EXPLORATORY: growth_gate_arm_invariant_at_k3=False -- FULL_STRUCTURAL_GATE (order-consistency-required
growth) diverges from production ARGTYPE_GATE by exactly {florps, zant}: it correctly blocks the
deliberately-contradictory zant but ALSO incorrectly blocks the legitimate reciprocal florps, showing
order-consistency cannot serve as a hard growth-gate requirement (it cannot distinguish "genuinely
reciprocal category" from "contradictory noise" from inside a single relation's own exposure history).
Bonus (not hidden): shleps also collides with vorbs/dringles in the `(True,True,{})` bucket, and
grims collides with krendles in the `(True,True,{chases})` bucket -- the population-wide all-pairs measure
(11/15) captures this honestly; the 2 designated success pairs and 1 designated defeat pair were each
independently checked and behaved exactly as designed.
