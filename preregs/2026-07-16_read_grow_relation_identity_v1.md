# Pre-reg: exp_read_grow_relation_identity_v1 (TIER-1 RELATION IDENTITY)

Cell: `experiments/exp_read_grow_relation_identity_v1.py`
Trigger: `notes/exp_dev_handoff_research_new_relation_grounding_2026-07-16.md` anchor #1 (Primary), drilled in
`notes/research_new_relation_grounding_argument_structure_analogy_2026-07-16.md` section (b)/(c).

Question: `exp_read_grow_openvocab_fastmap_v1` grows a new relation ("grims") type-guarded only by
`_relation_args_coherent`, which reads arg-type membership alone. Its own docstring pre-registers the honest
gap: "any two new verbs with the same arg-types are indistinguishable by grounding." Is that gap fixable
glass-box by widening the coherence check to a DORA-style richer structural signature (order/symmetry-
consistency + co-occurrence with known relations for the same argument pair), reusing the existing
accepted-facts store (no new subsystem)? Tier-1 IDENTITY only (is the new relation a real, stable, distinct
category) -- Tier-2 class-mapping and Tier-3 meaning-verification are explicitly OUT OF SCOPE per the hand-off.

## Prior-work check (substrate-KB concept-query, per USER-locked discipline)
`bash tools/substrate_query.sh --k 8 "relation identity individuation new verb argument type structural
signature symmetry order consistency"` -- top hits at cosine 0.31-0.33: `research_drill_cross_domain_
revival_3x_2026-06-10.md` (P9 architecture's missing structural-alignment step, a Gentner-SME gap in
cross-domain KGE) and `research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md` (relation-TYPE
cross-activation interference in a 10-relation-type real KG). Both are conceptually adjacent (same
Gentner/SME lineage: structural alignment over relational content) but neither is this cell's test --
those concern cross-domain KGE alignment and relation-TYPE routing interference in an established schema,
not NEW-relation IDENTITY individuation via order/symmetry+co-occurrence widening in the read-grow
open-vocab pipeline. Verdict: genuinely novel, not a rediscovery.

## Pieces composed (reuse of mechanism, with provenance)
- Open-vocab parser: `exp_read_grow_openvocab_fastmap_v1.py::ie_extract_openvocab` -- IMPORTED verbatim.
- Ablation mechanism (required negative control): `exp_read_grow_openvocab_fastmap_v1.py::_relation_args_coherent`
  -- IMPORTED verbatim, reused UNMODIFIED as the "current mechanism" arm.
- Ingest gate + sharded store: `exp_read_grow_foundation_endtoend_v1.py::FoundationStore` -- IMPORTED.
- NEW (this cell): `_order_consistency`, `_co_occurrence_with_known`, `_relation_identity_signature` -- the
  widened structural-signature functions, reading only `store.accepted` / the imported ablation function
  (no new subsystem, no hidden ground-truth type labels).

## Design (the required negative control + the fix)
Two new relations, both animal-animal arg-type (same signature under the current mechanism):
- `grims` (relation A): fixed-order/asymmetric -- two DISJOINT argument pairs (cat->dog, bird->frog), never
  repeated. Vacuously order-consistent (no counter-evidence of role-swapping ever observed).
- `florps` (relation B): reciprocal/order-swapping -- the SAME argument pair (cow, dog) observed with roles
  REVERSED across its two exposures (cow->dog, then dog->cow).
Ablation signature = `(_relation_args_coherent(...),)` -- a single boolean. Both grims and florps reduce to
`(True,)` -- IDENTICAL -- a genuine signature COLLISION (the required negative control: arg-type-only cannot
tell them apart). Full signature = `(argtype_coherent, order_consistent, co_occurrence_frozenset)`. grims ->
`(True, True, {chases})` (its argument pairs co-occur with the known `chases` relation); florps -> `(True,
False, {})` (no known-relation co-occurrence for its pair) -- DIFFERENT tuples -> SEPARATED.

## Honest scope note (declared before running)
At CONFIRM_K=2, a 2-exposure buffer cannot present an internally-contradictory order pattern (needs >=3
exposures). So growth accept/reject is ARM-INVARIANT here -- both mechanisms legitimately grow both
relations. The widening's measurable effect is entirely on the post-hoc identity-SIGNATURE separability,
which is exactly the Tier-1 question (is grims a real, distinct category from florps), not a claim about
growth-gating power. This is the correct, narrower scope for "identity," not a gap discovered post-hoc.

## Corpus note
florps deliberately uses (cow, dog), not (fish, dog/cow): `The fish lives in the pond.` is REJECTED by the
pre-existing FoundationStore schema gate (fish's only established slot is eats-OBJECT, so it does not FIT
the lives_in-SUBJECT slot -- an honest, pre-existing gate decision shared with `exp_read_grow_foundation_
endtoend_v1`'s own documented `fish` recall gap, not introduced by this cell). Using fish would make the
ablation REJECT florps outright rather than COLLIDE with grims -- a different, less clean failure mode than
the one under test.

## Bands (pre-committed; matches research note section (b)/(c))
- **HARD-PASS (Tier-1 identity):** `separated_frac_full >= 0.90` AND `separated_frac_ablation <= 0.10`
  (required negative control genuinely fires -- `identity_control_fired`) AND `a_grown_all` AND `b_grown_all`
  AND `violation_rejected_all` AND `distractor_not_grown_all`.
- **HARD-FAIL:** `separated_frac_full < 0.50` (widened mechanism carries no separating signal at this corpus
  scale -- a scale/data-richness finding per the research note, not a refutation) OR `separated_frac_full <=
  separated_frac_ablation + 0.05` (VACUOUS -- the required ablation-fails-then-widened-succeeds pairing did
  NOT occur) OR growth broke for either relation.
- **MIDDLE_BAND:** separation clears its bar but a regression control (type-violation / single-exposure)
  leaked.
- Tier-2 (class-mapping) and Tier-3 (meaning-verification): OUT OF SCOPE, not attempted, not scored.

## Schema-vet fields
- compute_architecture: sequential-CPU (foundation grows fact-by-fact; gate state depends on prior admits).
  wall < 1s (MEASURED 0.05s smoke, 0.10s full -- discrete logic, tiny corpus).
- storage_strategy: sharded (one VSA vector per accepted fact, via imported FoundationStore).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true. deterministic_seeding: true
  (fixed int seeds; sorted() vocab; no hash()/list(set())). start_marker + crash_diagnostic present.
- real_code_path (F.1): self_test constructs the REAL imported objects (`ie_extract_openvocab`,
  `run_identity_loop` -> `FoundationStore`, `_relation_args_coherent`) at full-tiny scale and asserts.
- crlb_n/a: no quantitative noise floor -- discriminator is discrete structural-signature comparison
  (set/boolean logic over accepted facts), not phasor decode noise. FHRR cleanup among ~20 concepts at
  N=1024 is not the bottleneck (query_acc MEASURED 1.00).
- discriminator-fires (required negative control, META_RULE_K analog): verified at self-test AND smoke --
  ablation `sig_a == sig_b == [True]` (collision, separated_ablation=False); full mechanism separates
  (separated_full=True). A run where the ablation ALSO separates is explicitly demoted to HARD_FAIL via the
  `vacuous` check in `compute_verdict` (separated_frac_full <= separated_frac_ablation + 0.05).
- arms_differ (META_RULE_AF): FULL_STRUCTURAL vs ARGTYPE_ONLY_ABLATION signature hashes differ (verified at
  self-test). `accepted_hash` is DECLARED EXEMPT for this arm pair -- growth is arm-invariant at CONFIRM_K=2
  by design (see Honest scope note); the widening's effect is the separability signature, not the store.

## Dispatch
Wall time sub-second (deterministic discrete-logic discriminator, tiny hand-authored corpus) --
COMPUTE-PROPORTIONALITY (cheapest decisive method): self-test, smoke, and FULL all run INLINE/FOREGROUND
locally, not through queue_add.sh / remote. No GPU, no remote SCP, no atomize. Local-only per USER-locked
"prefer local/inline for this cell" instruction (remote CPU runner reserved for the parallel decorr
wider-M cell). Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before this run.

## Result (MEASURED @ data/exp_read_grow_relation_identity_v1/metrics.json, 5 seeds [11,23,37,41,53], run_mode=full)
HARD_PASS (claim, VET-pending). separated_frac_full=1.000 (5/5 seeds); separated_frac_ablation=0.000 (0/5
seeds -- ablation collided on every seed: `sig_a_ablation == sig_b_ablation == [True]`, deterministic);
identity_control_fired=True; a_grown_all=True; b_grown_all=True; relation_query_acc_mean=1.00;
violation_rejected_all=True; distractor_not_grown_all=True; relation_false_fact_rate_mean=0.000. Full
signatures: grims=`[True, True, ["chases"]]` (order-consistent, co-occurs with known `chases`); florps=
`[True, False, []]` (order-INconsistent -- the reciprocal pattern correctly detected, no known-relation
co-occurrence). Result is fully deterministic across all 5 seeds (the discriminator is discrete
set/boolean logic over accepted facts, not a phasor-noise-dependent score) -- multi-seed run served as a
robustness/pipeline-determinism check per contract, not a variance probe.
