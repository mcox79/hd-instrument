# Pre-reg: Competency #3 (cross-sentence coreference), ablation-verified bottleneck metric

Filed by: exp_dev, 2026-07-31. Supersedes the additive-blend measurement approach (retired per
`notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md` Drill D: additive
blending dilutes compositional value; dissociation fairness gate marginally failed). This cell measures
competency #3 with an ABLATION-VERIFIED BOTTLENECK metric instead.

KB-check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring): `bash tools/substrate_query.sh
"cross-sentence coreference competency ablation bottleneck AND-gate role-competitive"` -> top hit
cosine=0.4189 on generic WordNet entity 'competence' (not a matching prior cell); no atom above 0.30
matches this specific cell design. **Prior-work check: NONE at cosine>0.30 -- genuinely new cell, not a
rediscovery.**

Prior cell built on: `experiments/exp_multi_competency_growing_library_v1.py` (competency #1 entity +
#2 roles, fully-modular, self-test + fairness harness). This cell REUSES it as a library
(`import ... as base_lib`) for: `run_base_multi` (frozen references + floors), `_eval_heldahead`,
`_cue_pooled_grad`, `_attn_pooled_grad`, `_role_loss_step` (all already generic over `cue_key`), `ROLE_SLOTS`,
`DEPTH`, `install_graded_renders`/`restore_renders`, `HARDNESS_LITE`/`HARDNESS_SMOKE`. NOT modifying
`exp_multi_competency_growing_library_v1.py` (a certified prior cell; changes there risk its own
self-test/cert). Also reuses `hdlab/coref.py`'s CENTERING/role-prominence framing conceptually (Lever 1:
role-prominence disambiguates competing antecedents) to justify the Tier design, though the concrete
mechanism here is the FHRR mark-addressing DSL (`render_tag` / `render_coref_event` / `render_coref_query`
in `exp_situation_model_assembly_encoder_backed_v1.py`, aliased `eb` via `base_lib`), not `hdlab/coref.py`'s
symbolic LitBank pipeline directly (that module operates on real narrative text with pronoun-gender
agreement; this cell's synthetic Tier items use the SAME mark-based coreference DEVICE already wired into
the FHRR harness's `b_competitive_coref` query type). Discrepancy flagged honestly, not hidden.

## The construction being measured

`b_competitive_coref` (an EXISTING query type in the harness) already asks: "what was the entity TAGGED
<mark> <role> to?" -- i.e. it requires (a) resolving `mark` back to the entity it was tagged onto
(coreference: the mark is the pronoun-like reference device introduced by `render_tag`) AND (b) reading
out the value at the QUERIED role slot (S or P) for that entity. This is competency #3's natural target:
it is PARASITIC on entity re-id (#1, mark->entity) and thematic-role decode (#2, role->value) exactly as
construction-grammar parasitism predicts (Drill D section 1.3).

## Tiering (construction-time tag, not post-hoc curve-fitting)

For each held-out eval passage's `b_competitive_coref` query (`ent=b_ent`, `role`, `mark`, `answer`),
reconstruct the entity's CURRENT (S, P) values from `p["events"]` (identical reconstruction logic to
`base_lib._role_critical_fraction`, applied to `b_ent` instead of the a_name_maintenance entity):

- **Tier 0 (entity-only)**: `S(b_ent) == P(b_ent)`. The queried role is irrelevant to the answer -- mark
  resolution (coreference) alone suffices. Solvable by competency #1 alone.
- **Tier 1 (role-competitive coref)**: `S(b_ent) != P(b_ent)` AND `distance <= median(distance | role_critical)`
  where `distance = n_events - 1 - last_write_idx(b_ent)`. Requires #1 (resolve mark->entity) AND #2
  (decode the correct role slot) JOINTLY -- the compositional bottleneck bucket.
- **Tier 2 (harder / long-distance role-competitive)**: `S(b_ent) != P(b_ent)` AND `distance >
  median(distance | role_critical)`. Approximates "hardest bucket" via increased memory distance since
  the DSL has no passive/voice-reversal construction yet (per
  `notes/research_mcguffey_construction_density_grade_progression_2026-07-31.md`, voice-invariance is a
  separate, not-yet-built wall) -- **this is an honest APPROXIMATION of the task's "role-reversal-under-coref"
  Tier 2, substituting distance-hardness for syntactic voice-reversal**, flagged HYPOTHESIZED not
  THEORETICAL. Tier 2 is reported informatively, NOT gated.

## Fairness gate (checked BEFORE any capability read; closed-form + measured)

1. `role_critical_fraction` (fraction of eval items with S!=P for b_ent) >= 0.55 -- Tier 1+2 population
   must be substantial (THEORETICAL: with WRITES_MIN..MAX=1..3 the natural S!=P rate is high; measured in
   BASE unit).
2. **Shortcut-baseline check (construction-validity, model-free, closed-form)**: `shortcut_tier1_acc` =
   accuracy of "always answer with the S value regardless of which role was queried" on Tier-1 items.
   Since role is drawn uniformly S/P, this heuristic is expected ~0.50 (chance-level on the role axis) BY
   CONSTRUCTION if items are genuinely role-critical. If `shortcut_tier1_acc` clears 0.65, Tier-1 items are
   NOT genuinely role-dependent (a construction bug, not a capability finding) -> INVALID, fix items.
3. Tier-0 vs Tier-1 population balance: both tiers must have >= 8 eval items (LITE) / >= 4 (SMOKE) or the
   tier is too small to trust; reported, non-blocking at SMOKE scale (self-test only proves wiring).

## Mechanism (fully modular per Drill A: fresh subspace + gated update)

Two coref-track extractors (`lt.RetrainableExtractor`, own `nn.Parameter` tensors -- a fresh subspace per
Drill A's SupSup/PackNet-style recipe), trained on the SAME 3-term contrastive objective
(`base_lib._role_loss_step`, align+push+VICReg) over MARK-addressed synthetic text
(`eb.render_tag(ent,mark)` + `eb.render_coref_event(mark,s,p)`), alternating cue_key in {"S","P"}
(role decode, reusing `base_lib.ROLE_SLOTS`) exactly like the existing role-competency track, but keyed on
MARK-addressed events (coreference) instead of ENT-addressed events (name):

- **`coref_with_roles`**: initialized by COPYING the FINAL trained weights of an ext_r trained on the
  EXISTING roles objective (`base_lib._gather_role_texts` + `base_lib._role_loss_step`, ENT-addressed,
  identical to competency #2's mechanism) into a fresh `ext_c`'s parameter tensors (`.detach().clone()` +
  `.copy_()`, NOT a shared reference -- zero gradient interference with the source ext_r, which is
  discarded after the copy), THEN further fine-tuned on the coref/MARK objective. This is "roles present":
  the coref track's initialization carries the role competency's learned structure.
- **`coref_roles_ablated`**: a FRESH `ext_c` (frozen base init, role competency NEVER applied), fine-tuned
  IDENTICALLY (same steps, same data-generation seeds) on the coref/MARK objective only. This is "roles
  ablated": same amount of coref-specific training, without the role-competency prefix.

Same steps/LR/batch/data-generation seed between the two variants (only the INIT state_dict differs) --
the one variable is `variant in {with_roles, roles_ablated}`.

## Decisive measurement (ablation-verified bottleneck, NOT additive margin)

Primary value = Tier-1 accuracy of `coref_with_roles` MINUS Tier-1 accuracy of `coref_roles_ablated`, on
the SAME held-out Tier-1 eval items, evaluated via `base_lib._eval_heldahead(ext, tier1_structs, tables,
target)["per_type"]["b_competitive_coref"]` (the harness's existing decode pipeline, unmodified).

**HARD-PASS** (compositional AND-gate demonstrated):
- Tier-1 acc(`coref_with_roles`) >= 0.70, AND
- Tier-1 acc(`coref_roles_ablated`) <= 0.55, AND
- Tier-0 acc(`coref_with_roles`) shows no regression vs the frozen (untrained) baseline (modularity: adding
  the coref competency does not break the entity-only bucket) -- `tier0_acc >= frozen_tier0_acc - TIE_BAND(0.02)`.

**HARD-FAIL**:
- Tier-1 acc(`coref_with_roles`) <= 0.55 (integration/wiring gap: coref cannot cash in role info even when
  it is present), OR
- `|Tier-1 acc(with_roles) - Tier-1 acc(roles_ablated)| <= 0.05` (construction-invalid: coref is solving
  Tier-1 via a shortcut, e.g. recency, not actually using role information -- corroborated against the
  fairness gate's shortcut check).

**MIDDLE-BAND**: Tier-1 lift (with_roles - roles_ablated) in [0.10, 0.20] -- partial compositional use;
report + do not force a capability claim either way.

Per Drill E's recalibrated tiered bar (>=0.02 floor / 0.03-0.06 strong / 0.08+ stretch), the Tier-1 LIFT
here (0.70-0.55=0.15 at HARD-PASS boundary) is intentionally set well above the additive-metric floor
because this is a bottleneck/AND-gate lift on the SPECIFIC subset that requires the competency, not a
diluted whole-population additive lift -- consistent with Drill D's prediction that bottleneck lifts on the
right subset should be an order of magnitude larger than blended lifts.

## SCHEMA-VET fields

```yaml
one_variable: "variant in {coref_with_roles, coref_roles_ablated}; steps/LR/batch/data-gen seed identical"
cell_chunked: false          # single-seed-per-run acceptable at this scope (SEEDS_LITE=(7,)); 2-seed
                              # escalation is the documented next step if MIDDLE
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: "passed_all_4_patterns"
arms_differ_verified: true   # self-test hash-checks coref_with_roles vs coref_roles_ablated curves differ
final_metrics_atomicity: "tmp_replace"
crlb_n/a: "reader = zero-learned-param FHRR decode (verbatim base_lib/eb/lt/ih/clean); learned params =
  TWO independent RetrainableExtractor instances per variant (own nn.Parameter tensors, copy-init not
  shared-reference) -> zero shared gradient by construction (assert disjoint id() sets, per base_lib
  precedent)"
baseline_in_band: "frozen (untrained) Tier-1 accuracy must be < 0.70 (headroom exists for the with_roles
  arm to demonstrate a real HARD-PASS climb, not a by-construction-saturated floor)"
cardinality_ok: "EXPECTED_N_UNITS = n_seeds * (1 base + 2 variants); verdict HARD_FAILs on breach"
calibration_check: "default_ok_for_this_regime -- reuses base_lib's ALREADY-VALIDATED LR/steps/batch/VICReg
  weights verbatim (base_lib._role_loss_step unmodified); only NEW knob is coref-track step count, sized by
  analogy to base_lib's role-track step count"
composition_edges:
  - from: base_lib.run_base_multi (entity+roles harness, frozen references)
    to: this_cell.tier_split (post-hoc query-level tagging)
    A_natural_output_shape: "list[passage-dict] with events + queries[b_competitive_coref]"
    B_natural_input_shape: "same list[passage-dict], filtered by role-criticality + distance"
    verdict: SHAPE_MATCH
  - from: base_lib._role_loss_step (generic cue_key contrastive objective)
    to: this_cell._gather_coref_texts (MARK-addressed instead of ENT-addressed text)
    A_natural_output_shape: "(ids_batch, label_batch, cue_key) -> loss"
    B_natural_input_shape: "same signature, MARK-addressed render_tag+render_coref_event text"
    verdict: SHAPE_MATCH   # base_lib._role_loss_step already generalized over cue_key; verified in self-test
positive_control_arms:
  - arm: BASE_REPRODUCE_ROLE_FAIRNESS
    primitive: base_lib.run_base_multi (competency #1+#2 frozen references, floors, a_name_maintenance
      role-fairness diagnostics)
    cited_prior_atom: "exp_multi_competency_growing_library_v1 self-test PASS (this session, prior cell)"
    tolerance: "exact reuse, same function call, no reimplementation -- reproduction is by construction"
    if_outside_tolerance: N/A (verbatim call, cannot diverge except via the shared codepath itself)
    regime_extension_audit: SHAPE_MATCH
functional_requirements:
  - requirement: "resolve a mark back to the entity it was tagged onto (coreference)"
    primitive: "MARK cue pooling (eb.EncoderExtractor.CUES['MARK'], base_lib._cue_pooled_grad/_attn_pooled_grad)"
  - requirement: "decode the specific queried role's value once the entity is resolved (thematic role)"
    primitive: "S/P cue pooling (base_lib.ROLE_SLOTS, base_lib._role_loss_step, identical to competency #2)"
  - requirement: "demonstrate the AND-gate causally, not just correlationally"
    primitive: "ablation via init-state copy: coref_with_roles carries ext_r's trained weights as its
      init; coref_roles_ablated does not; both trained identically thereafter"
real_code_path_exercised: [base_lib.run_base_multi, lt.RetrainableExtractor, eb.render_tag,
  eb.render_coref_event, eb.render_coref_query, base_lib._eval_heldahead, base_lib._role_loss_step]
substrate_signature_checked: [lt.RetrainableExtractor.unfreeze_top, base_lib._role_loss_step,
  base_lib._eval_heldahead]
guard_baseline_validated: N/A   # no control-beats-baseline break-guard in this cell (bottleneck metric,
  not a POP-vs-RANDOM guard); fairness gate plays the analogous role (shortcut-baseline-must-not-solve-it)
deterministic_seeding: true    # numpy default_rng + torch.manual_seed only; no hash(), no list(set())
progress_logging: "print_flush_true"   # timeout_s for LITE budget-sec default 480s (< 1800s so the
                                        # MANDATORY-at-30min gate does not strictly apply, but flushing is
                                        # applied anyway per standing discipline)
```

## Compute architecture

Sequential-CPU, small-N (V_FILL=20, DIM=1024, single-hardness snapshot -- no graded curriculum needed since
this is an ablation snapshot test, not a climb test). Storage strategy: no_storage (online fine-tune +
closed-form FHRR eval; no atom-store writes). Wall-time estimate: BASE unit ~10-20s (reuses
base_lib.run_base_multi's own graded-profile forward passes at HARDNESS_LITE); each variant unit ~ role-
pretrain (40 steps) + coref-train (50 steps) + 6 tier-forward-evals (2 variants would be 2 units, each with
its own role-pretrain when `with_roles`) -- expected well under 10 min total at LITE scale on CPU;
GPU-batching not warranted (small batch, short sequences, `< 10s` per gradient step regime matches
base_lib's own precedent).

## Run

```
.venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --self-test
.venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --smoke
.venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --lite
```

(`--lite` is resumable per-(kind,seed,variant) unit via `tools/exp_checkpoint.py`, CPU-first, push-free,
INLINE-LOCAL foreground, `--budget-sec` default 480 < 600s Bash timeout ceiling.)
