# Skunkworks tier ruling — Cell 5 (substrate_role_tagged_compositional_generalization_on_concept_KG_v1)

**Date:** 2026-06-25
**Reviewer:** Skunkworks (cert-owner / by-construction-saturation auditor)
**Verdict-from-cell:** HARD_PASS_CHAIN_GRADE (HYBRID heldout=1.000 cv=0.000)
**Skunkworks ruling:** **MEASURED_MECHANISM (mechanism_characterization_by_construction_saturation_label_driven_encoder_carries_lift)** + CHAIN_GRADE-eligible discriminator-direction note on cluster-vs-ortho

## TL;DR (intuitive)

The cell claims substrate compositionally generalized role-binding to heldout subjects via category structure transfer. But the only arm that achieved heldout=1.000 (HYBRID) is also the only arm whose encoder pre-fuses same-category instances into a shared category basis at *construction time*. The role-binding machinery is doing clean retrieval, but the heldout lift comes from the encoder, not from role-tagged compositional transfer. Five arms varied two factors (encoder × ingest); the cell did not run the diagnostic control (label-driven encoder + no-role / orthogonal-role) needed to attribute the lift to role-binding. Per META_M4 (K_THRESH=1 by-construction-saturation, just-atomized) and the SEMANTIC_v3 prior (A3 at metric ceiling → MM), Cell 5 is the same family of cert-violation.

The cluster-vs-ortho discriminator (USER's "roles should cluster semantically" insight) is DIRECTION-CORRECT (clustered 0.333 vs ortho 0.167, +0.167 mean lift across 3 seeds) but not statistically significant at n=3 seeds × 8 heldout per seed.

## Per-seed metrics (verified by reading metrics.json off data, not verdict_msg)

| Arm | Seed 7 | Seed 17 | Seed 23 | Mean | std |
|---|---|---|---|---|---|
| ARM_NO_ROLES (heldout_top1) | 0.250 | 0.125 | 0.125 | 0.167 | 0.059 |
| ARM_ROLES_ORTHOGONAL_RANDOM | 0.250 | 0.250 | 0.000 | 0.167 | 0.118 |
| ARM_ROLES_SEMANTICALLY_CLUSTERED | 0.375 | 0.500 | 0.125 | 0.333 | 0.156 |
| ARM_GRAMMATICAL_ROLE_BINDING | 0.125 | 0.125 | 0.000 | 0.083 | 0.059 |
| **ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS** | **1.000** | **1.000** | **1.000** | **1.000** | **0.000** |

Trained-top1 (NO_ROLES baseline): 0.833, 0.792, 0.708 → mean 0.778; min 0.708 borderline-passes 0.70 rail.

Role-codebook inner products (verifying construction):
- ORTHO arm: within-A ~0, within-B ~0, cross ~0. (Orthogonal by construction.)
- CLUSTERED arm: within-A 0.691, within-B 0.691, cross ~0. (Clustering achieved.)
- HYBRID arm: within-A ~0, within-B ~0, cross ~0. (HYBRID uses orthogonal codebook, NOT clustered. The "hybrid" name is misleading — HYBRID = label-driven encoder + orthogonal role codebook + grammatical ingest. NO role-clustering in HYBRID.)

## The by-construction-saturation mechanism (load-bearing)

Tracing the cell source code:

**1. HYBRID encoder (`concept_encoder_label_driven`, lines 213-238):**
```
For each category c in [0..3]: GS-orthogonal basis vector B[c].
For each instance i: E[i] = L2_normalize(B[category_of(i)] + 0.5 * orthogonal_noise_i)
```
Same-category instances share their dominant basis component. Pairwise cosine within category ≈ 1 / sqrt(1.25) ≈ 0.894. Cross-category cosine ≈ 0 (orthogonal bases).

**2. HYBRID ingest (`ingest_grammatical`):** stores per training triple (s, R_subj, a):
```
W += outer( E_action[a], bind(E_inst[s], R_role[R_subj]) ) / N
```
plus a verb-role structural binding (additive but inner-product orthogonal to the retrieval key on heldout).

**3. HYBRID query at heldout h (category c, action a_c canonical):**
```
key = bind(E_inst[h], R_role[R_subj])
pred = W @ key
score[a_c] = sum over trained_i of cosine(E_action[a_c], E_action[a_train_i])
              × cosine(bind(E_inst[h], R_subj), bind(E_inst[train_i], R_subj))
```
For trained_i sharing category c with h: bind() is associative-like under HRR-bind with normalized roles, so cosine(bind(E_h, R_subj), bind(E_train_i, R_subj)) ≈ cosine(E_h, E_train_i) ≈ **0.894** (same-cat encoder cosine).

For trained_i in a different category: cosine ≈ 0.

So `score[a_c] ≈ 0.894 × n_trained_same_cat ≈ 0.894 × 6` (each cat has 8 instances, 2 heldout → 6 trained per cat), which dominates `score[a_c'] ≈ 0` for c' ≠ c. **Argmax always picks a_c. Heldout=1.000 by construction.**

**4. The is_a atoms are NEVER USED at retrieval.** Query keys use R_role[R_subj] (idx 0), not R_isa. The is_a write `outer(E_category[c], bind(E_h, R_isa))` is decorative — its key direction R_isa is orthogonal to R_subj, so it doesn't contribute to the retrieval inner product. The cell's stated "compositional transfer via is_a binding" pathway is not the mechanism that gives heldout=1.000.

**5. By contrast, ARM_ROLES_ORTHOGONAL (heldout=0.167):** uses `concept_encoder_random` (i.i.d. bipolar). Same-category cosine ≈ 0 (random). Score collapses to noise. Substrate has no path to discover category from is_a alone (since query is R_subj-keyed). Result: chance-band.

**Conclusion:** the 6x lift HYBRID-vs-ORTHO is attributable 100% to the label-driven encoder (which writes category equivalence classes into E_inst at construction time), 0% to role-binding composition. The role-binding does its job (clean trained-top1=1.000 across all role arms) but contributes nothing additional to heldout. This is mathematically equivalent to category-label lookup in a category-collapsed embedding space, which is by-construction-saturation per META_M4.

## Verify-the-referent against prior chain-grade

Prior chain-grade cited as precedent in the cell's DESIGN_NOTE: "SEMANTIC_concept_learner_battery_v2 A3 heldout top1=1.000 (cv=0.000)."

But yesterday Skunkworks ruled (2026-06-25 ledger entry): `SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING_MM — A3 primary at metric ceiling already in v2`. The referent is itself MEASURED_MECHANISM, not chain-grade. Inheriting "compositional generalization" framing from A3 inherits by-construction-saturation of A3.

This is the same N1 verify-referent-verdict-field discipline I (Skunkworks) flagged on the concept_kg referent yesterday. **Cell 5's lineage is MM, not chain-grade.** Compositional-generalization claims layered on top of MM ancestry default to MM.

## Statistical sanity (n_heldout=8 concern)

The USER asked: at top1=1.000 with n=8 heldout per seed, what's the binomial CI?

Per seed: 8 of 8 → 95% Wilson CI [0.68, 1.00]. Across 3 seeds (24 trials total, all hits): [0.86, 1.00]. cv=0.000 across seeds because *every* query passes — variance is unmeasurable, not measured. n=8 IS too small for chain-grade by statistical-sufficiency alone, but the by-construction-saturation argument makes the statistical question moot: even at n=1000 heldout, the encoder-baked category lookup would still hit 1.000. The cell is testing whether B[c]-cosine ≈ 0.894 beats noise; that's not the substrate-architecture claim it purports to test.

## Cluster-vs-ortho discriminator (USER's "roles should cluster semantically" insight)

Per-seed CLUSTERED − ORTHO:
- Seed 7: 0.375 − 0.250 = +0.125
- Seed 17: 0.500 − 0.250 = +0.250
- Seed 23: 0.125 − 0.000 = +0.125
- Mean: +0.167; std 0.072; t = 0.167 / (0.072/sqrt(3)) ≈ 4.01 paired; or unpaired ≈ 1.46

Direction-correct: clustered > ortho across all 3 seeds. Paired-t suggests significance (p ≈ 0.03), unpaired weaker (p ≈ 0.10). Magnitude is small (2x chance vs 1.3x chance), and absolute clustered top1 0.333 is well below any chain-grade band. **DIRECTION-CORRECT for USER's intuition that clustered roles help, but not chain-grade evidence. Worth a follow-up at higher V_PREDICATES / more seeds / no-encoder-confound design.**

Important nuance: the clustered-role mechanism is INDEPENDENT of the label-driven encoder confound. CLUSTERED arm uses `concept_encoder_random` (i.i.d. bipolar). So the +0.167 gap is plausibly attributable to role-codebook geometry, not to encoder-baked category lookup. This is the **honest signal** in the cell — a small, direction-correct hint that clustered roles help — but it's separate from the headline HYBRID claim.

## Tier ruling

**MEASURED_MECHANISM (mechanism_characterization_by_construction_saturation_label_driven_encoder_carries_lift)**

- cert_status: measured_mechanism
- cert_class: mechanism_characterization_by_construction_saturation
- cert_increment_delta: 0 (does NOT advance CERT N from 588)
- supersedes: none (first ruling on this anchor)
- direction: lift is real, mechanism is encoder not role-binding
- subsidiary finding: CLUSTERED-vs-ORTHO direction-correct for USER's role-clustering hypothesis (+0.167 mean across 3 seeds); needs follow-up at no-encoder-confound design

## What chain-grade evidence would actually look like

To certify substrate role-tagged compositional generalization chain-grade, design a follow-up cell with:

1. **Diagnostic control arm: ARM_HYBRID_NO_ROLES_LABEL_DRIVEN** — label-driven encoder + no role binding. Hypothesis: this arm ALSO achieves heldout≈1.000 by the same encoder-baked mechanism. If yes, role-binding contributes nothing; if no, role-binding is load-bearing.
2. **Encoder-blind variant: ARM_HYBRID_ROLE_PLUS_ORTHOGONAL_LABELS** — random orthogonal between-instance encoder (no within-category structure), full grammatical role-binding. Hypothesis: heldout collapses to chance, isolating the encoder's contribution.
3. **Heldout-design fix:** make heldout instances whose category is NOT trained at all (rather than 2-per-cat with 6-per-cat trained). Forces genuine cross-category compositional transfer rather than within-category lookup.
4. **Scale n_heldout to ≥ 32 per seed** for binomial CI tightness.
5. **Use ARM_ROLES_SEMANTICALLY_CLUSTERED + label-driven encoder hybrid** as the new candidate (not the current HYBRID which uses orthogonal codebook). This tests the USER cluster intuition × encoder-anisotropy joint effect.

## Atomize-on-ledger plan

Three atoms to write (per Fix #28 + results-to-application same-cycle):

1. `math::T3/EXP_substrate_role_tagged_compositional_generalization_on_concept_KG_v1_MM` — the main MM ruling
2. `meta::T3/META_M6_label_driven_encoder_writes_category_equivalence_class_pre_fuses_heldout_with_trained` — generalization of the by-construction-saturation pattern to encoders (sibling to META_M4 K_THRESH=1)
3. `meta::T3/META_M7_role_binding_lift_attribution_requires_encoder_factor_controlled` — methodology rule: any 2-factor cell varying encoder × ingest must include the 4-cell crossproduct (4 arms) not just the 2 "matched" arms, else attribution is confounded

(Atomization happens in a separate Skunkworks turn per A5-gate discipline.)

## Cross-check on USER's hypothesis

USER hypothesis: "Cell 5 chain-grade = first chain-grade Stage 2 architectural win on right corpus." Substantial.

Skunkworks finding: it's NOT chain-grade for the *role-tagged-binding architectural win* it claims. It IS evidence that the **label-driven encoder geometry transfers to KG-style heldout queries**, which is an interesting and substrate-relevant capability — but that capability was already established in SEMANTIC_battery_v2 A3 and ruled MM yesterday. Cell 5 reproduces the v2 A3 mechanism in a slightly more complex (role-binding wrapped) regime; it does not isolate a new substrate primitive.

What Stage 2 architectural chain-grade WOULD look like: role-binding that demonstrably lifts heldout above an encoder-matched baseline. The current data does not provide this evidence; it provides evidence consistent with role-binding being neutral and the encoder doing all the work.

## Output integrity check

- Per-arm metrics read directly from `data/exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1/metrics.json` (NOT from verdict_msg) per Fix #28.
- Mechanism trace from `experiments/exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1.py` lines 213-238 (encoder), 332-362 (ingest), 416-435 (arm routing).
- Cluster gap re-computed off raw per-seed values, not summary.
- Prior-art referent (SEMANTIC_v3 A3) cross-checked against ledger entry 2026-06-25.
- META_M4 / META_M5 family-similarity ruling cited from same-day ledger.

End ruling.
