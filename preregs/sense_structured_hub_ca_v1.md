# Pre-reg: C-A sense-structured lexical-semantic hub (sense_structured_hub_ca_v1)

Status: PRE-REGISTERED 2026-08-05 before running. Cell: `experiments/exp_sense_structured_hub_ca_v1.py`.
Plan ref: `notes/PLAN_grounded_semantic_organ_build.md` Section C-A + Section 0/2.
VET ref: `notes/design_vet_semantic_organ_plan.md` Axis 1 (rigged-floor fix) + Axis 3 (error-budget) +
the C-A rewrite items (floor = existing single-prototype encoder, not hash-random; disjoint-cue held-out).
Floor cell (MEASURED, reused): `experiments/exp_sense_collapse_floor_v1.py`,
`data/exp_sense_collapse_floor_v1/metrics.json` -- honest_floor_accuracy=0.5625 (concept_encoder).

## Prior-work check (substrate-KB, USER-locked gate)
`bash tools/substrate_query.sh "induced word sense multi-prototype context clustering polysemy
error-driven predictive coding"` -- top hit cosine=0.3525 (`predictive_coding` capability_registry row,
i.e. the module we are EXTENDING, not a prior sense-induction cell). No prior-arc cell at cosine>0.30
attempts induced multi-prototype sense structure. Genuinely novel build on top of two WIRED substrate
modules (`hdlab/ppmi_sparse_encoder.py`, `hdlab/predictive_coding.py`) + one HARD_PASS module
(`hdlab/concept_encoder.py`, reused only as the single-prototype control arm).

## Functional requirement decomposition (SCHEMA-VET item E)
- Requirement: a polysemous form's representation must become CONTEXT-APPROPRIATE (sense-resolved),
  not collapsed to one vector. Existing primitive addressing part of this: `hdlab/ppmi_sparse_encoder`
  (live per-sentence context encode -- the least-collapsed spoke per the floor measurement,
  forced_choice_accuracy=0.625 MEASURED@data/exp_sense_collapse_floor_v1/metrics.json:per_encoder.
  ppmi_sparse_encoder.forced_choice_accuracy). No existing primitive does INDUCED multi-prototype
  clustering per form -- that is the genuinely new mechanism this cell builds, sitting ON TOP of the
  PPMI context representation.
- Requirement: sense differentiation must be ERROR-DRIVEN (predict differently -> pull apart), not
  hand-listed. Existing primitive: `hdlab/predictive_coding.py` (`residual_magnitude`, `threshold_gate`)
  -- WIRED, Rao-Ballard residual-gated Hebbian. REUSED directly as the split/merge decision function
  (Axis-1 fix #2 of the design-VET: name the real error-driven substrate, not hdlab/learner).

## Mechanism (glass-box, inspectable, induced not hand-listed)

1. **Context representation.** `hdlab.ppmi_sparse_encoder.PPMISparseEncoder` fit on the UNION of all
   FIT-set context sentences (target word masked out) across all 10 forms, with `concept_labels =
   arange(n_fit_sentences)` (each sentence its own PPMI "concept" -- classic PPMI/SVD distributional
   context-embedding usage, i.e. LSA-style, NOT word-form-supervised; word-form-supervision was
   rejected because it would train the encoder to separate FORMS not SENSES, defeating the point).
   `encode(context_str)` gives the context vector for any sentence (fit or held-out; held-out
   generalizes via shared trigrams, out-of-vocab trigrams skipped -- genuine generalization test).
2. **Induction (online, error-driven, per form, unsupervised -- clustering never sees sense labels).**
   For each form, FIT context vectors are visited in a fixed seeded-shuffle order. Maintain a list of
   running-mean prototype vectors (Hebbian bundling = running sum / count). For each new context vector
   `cv`: find the nearest existing prototype by cosine; call
   `predictive_coding.threshold_gate(observed=cv, predicted=nearest_prototype_mean, threshold=T)`.
   If `not skipped` (residual >= T, i.e. the prototype predicts this context POORLY / it is surprising):
   SPAWN a new prototype (differentiation) -- capped at `max_prototypes=4` per form (beyond the cap,
   merge into nearest). If `skipped` (residual < T, predicted well): MERGE (Hebbian running-mean update
   into the nearest prototype) -- this is the literal reuse of `predictive_coding`'s gate as the
   error-driven split/merge signal named in the plan.
3. **Threshold calibration (adaptive, not hand-picked, FIT-only -- `calibration_check` field below).**
   `T` = midpoint between (a) mean `residual_magnitude` over FIT same-sense pairs and (b) mean
   `residual_magnitude` over FIT different-sense pairs, computed ACROSS ALL 10 FORMS (never touches
   TEST). This is measured + logged in metrics (`threshold_calibration` block), not asserted.
4. **Cluster-to-sense labeling (post-hoc, scoring-only, never feeds back into induction).** Each induced
   prototype is labeled by MAJORITY true-sense among its FIT members (ties broken deterministically by
   prototype creation order). This is standard word-sense-induction (WSI) evaluation practice (purity /
   best-match alignment) -- induction itself is label-free; labels are used only to SCORE it.
5. **Assignment (new occurrence -> sense).** For a held-out TEST context vector: nearest-prototype by
   cosine (argmax), then `pred_sense = cluster_label_map[nearest_prototype_id]`.

Everything is inspectable: per-form prototype vectors, per-item assigned prototype id, and the
FIT-vs-TEST residual/threshold trace are written to metrics.json (`per_form.induction_trace`).

## Probe (10 forms; DISJOINT fit/test context vocabulary; adequate n)

10 polysemous forms, 2 senses each: hard, trick, pay, cross (the 4 audit collision tokens, MANDATORY
per task) + bright, sound, light, bear (extended from the Step-0 floor probe, NEW fit/test sentences,
not reused verbatim) + bank, bat (2 new forms). Per form: FIT = 3 sentences/sense (6/form, 60 total);
TEST(held-out) = 3 sentences/sense (6/form, 60 total). **Disjointness is machine-checked at cell
runtime**, not just hand-verified: `_content_words(sentence, target_word)` strips the target word +
a closed-class stopword list; the cell asserts
`test_content_words(form) & fit_content_words(form) == empty` for all 10 forms BEFORE any measurement
runs (`AssertionError` halts the cell if violated -- this is the leakage guard the design-VET's
"disjoint cue vocabulary" fix requires, made mechanical instead of eyeballed).

`EXPECTED_N_UNITS = 10` (forms). Cardinality gate: `len(per_form) == 10` or `HARD_FAIL_CARDINALITY_
BREACH_META_RULE_H`.

## Controls (all three run; MANDATORY per contract)

(a) **Single-prototype floor control.** `hdlab.concept_encoder.ConceptEncoder` (mask_target_word=True,
    labels = word-FORM index, i.e. EXACTLY the honest-floor mechanism from the Step-0 measurement,
    re-fit + re-evaluated on THIS cell's expanded held-out set for an apples-to-apples number). Because
    `encode()` returns one vector per FORM (context-blind lookup), 2AFC forced-choice against the two
    FIT-sense reference encodes degenerates to near-tie -> near-chance, exactly reproducing the
    mechanism (not just citing) that gave 0.5625 on the Step-0 probe. HARD-FAIL condition: this control
    must NOT also pass the C-A gate (>= 0.80) -- if it does, the induced hub's "signal" is a probe
    artifact, not sense-structure.
(b) **Same-sense false-split control.** For each form/sense, take the 3 held-out TEST items of that
    sense; for each of the 3 pairwise combinations, check whether both items were assigned (by the
    induced hub) to the SAME prototype id. `same_sense_agreement` = agree_pairs / total_pairs across
    all 10 forms x 2 senses x 3 pairs = 60 pairs. Guards against over-splitting (spurious extra
    prototypes that fragment a single sense, which would inflate held-out accuracy by luck on a 2-item
    probe but fail generalization).
(c) **Induced-not-hand-listed witness.** `per_form.induction_trace` in metrics.json records, per form:
    number of prototypes actually induced (NOT fixed at 2 -- can be 1 to 4), the FIT item -> prototype-id
    assignment sequence (in visitation order, showing exactly when a split fired and its residual value),
    and the final prototype vectors. This is the glass-box inspection artifact.

## Pre-registered bands (per META_RULE_L: HARD-PASS strictly above floor + 5% band width)

Floor for META_RULE_L purposes = the (re-measured, this cell's probe) single-prototype control accuracy,
expected ~0.50-0.58 per the Step-0 number; band width to ceiling 1.0 ~0.42-0.50; 5% of that ~0.02-0.025,
i.e. strictly-above-floor threshold ~0.52-0.60. HARD-PASS at 0.80 clears this by a wide, non-floor-hugging
margin (MIDDLE_BAND avoided by construction unless the measured floor is unexpectedly high).

- **HARD_PASS**: `held_out_sense_discrimination_accuracy >= 0.80` AND
  `single_prototype_control_accuracy <= 0.65` (stays near the Step-0 chance-ish floor, i.e. does NOT
  also solve the held-out probe -- rules out a probe-artifact leak) AND
  `same_sense_agreement >= 0.75` (no false-split) AND senses INDUCED (verified via `induction_trace`,
  `n_prototypes_induced` per form logged, never a fixed hand table).
- **HARD_FAIL**: `held_out_sense_discrimination_accuracy < 0.65`, OR
  `single_prototype_control_accuracy >= 0.80` (control also passes = leak, gate invalid), OR
  `same_sense_agreement < 0.50` (mechanism is fragmenting single senses, not finding real structure).
- **MIDDLE_BAND**: anything else (e.g. 0.65 <= held_out_acc < 0.80, or same_sense_agreement in
  [0.50, 0.75)) -- honest inconclusive tier, not forced to a verdict.

`HP_SCOPE`: `{induced_hub_arm: [held_out_acc_gate, same_sense_agreement_gate, induced_not_hand_listed],
single_prototype_control_arm: [must_stay_near_chance_gate]}` -- the "must stay near chance" gate applies
ONLY to the control arm, not the induced-hub arm (per SCHEMA-VET item 5b).

## Error-budget note (Axis 3 fix, informal -- no C-D/C-C cell exists yet to derive a hard number from)
No downstream C-B/C-C/C-D consumer cell exists yet to derive a precise minimum-accuracy contract from
(they are future components in the plan). 0.80 is set as a generously-above-floor, generalization-tested
(disjoint-vocab held-out) number consistent with "clearly usable by a downstream selector," not tuned to
pass. This is flagged HYPOTHESIZED (no downstream consumer measured yet) pending C-B's actual build.

## Compute architecture / storage / atomicity / defensive-checking (SCHEMA-VET declarations)
- Compute architecture: **(b) sequential-CPU with justification** -- corpus is 120 sentences total, PPMI
  SVD is O(V x n_fit_sentences) on a tiny matrix, online per-form induction is O(n_items x n_prototypes)
  with n_prototypes<=4; wall time expected << 10s. GPU batching would add complexity with zero benefit
  at this scale.
- Storage strategy: `no_storage` (representation-induction cell, not an associative-memory
  write/retrieve cell; no chained composition).
- `cell_chunked: false` (single-shot measurement, no seed axis, wall << 10s -- same exemption class as
  the Step-0 floor cell).
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: false`
  (`defensive_error_checking: "exempt_short_singleshot_cell_start_marker_and_crash_diagnostic_present"`,
  same precedent as `exp_sense_collapse_floor_v1.py`).
- `final_metrics_atomicity: "tmp_replace"`.
- `crlb_n/a`: "representational sense-induction measurement; no quantitative noise-floor formula
  applies" (same as Step-0 floor cell).
- `arms_differ_verified`: induced-hub predictions vs single-prototype-control predictions compared
  directly (not required to be bit-identical-hash-different since these are scalar predictions per
  item, not tensors -- logged as `n_items_where_arms_disagree` in metrics; some agreement on easy items
  is expected and fine, the induced hub must simply not be IDENTICAL to the control on every item).
- `calibration_check: "adaptive_with_discriminator_gate"` -- threshold `T` computed from FIT-only
  same-sense vs diff-sense residual distributions (formula above); logged in `threshold_calibration`;
  discriminator-still-fires is verified by construction (T sits between the two measured means, so a
  form whose FIT senses are genuinely separable in PPMI-context space WILL differentiate).
- `real_code_path_and_signature_preflight`: self-test (`--self-test`) constructs the REAL
  `PPMISparseEncoder`, `ConceptEncoder`, and calls the REAL `predictive_coding.residual_magnitude` /
  `threshold_gate` functions at tiny scale (2 forms), not a synthetic-only branch.
- Discriminator-fires gate: smoke/self-test asserts induction produces >= 2 prototypes for at least one
  form with FIT senses (not `n_prototypes==1` for all forms, which would mean the split never fires).

## Honest can-fail routing (contract item 5)
If `held_out_sense_discrimination_accuracy` does not clear 0.80: report is diagnostic, not forced --
inspect `threshold_calibration` (did T end up too high, so nothing ever splits -- `n_prototypes_induced`
would show mostly 1s?) vs too low (over-splits -- `same_sense_agreement` would show fragmentation) vs
the PPMI context representation itself being too weak on this vocabulary (compare per-form `mean_fit_
same_sense_cos` vs `mean_fit_diff_sense_cos` -- if these are nearly equal, the context REPRESENTATION,
not the clustering/error-signal, is the bottleneck -- route to "missing component: richer context
representation" not "clustering algorithm is wrong"). This traces to a concrete mechanism, not a vague
"ceiling."
