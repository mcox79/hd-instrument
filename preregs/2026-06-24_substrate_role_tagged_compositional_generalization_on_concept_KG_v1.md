# Pre-reg: substrate_role_tagged_compositional_generalization_on_concept_KG_v1
Date: 2026-06-24
Author: exp_dev (Wave E retry; USER course-correction)
Routing: remote_cpu_queue via orchestrator handoff
Lane: 1 (substrate-native concept-KG; NOT text8)

## USER course-correction (this cell SUPERSEDES the original Cell B)
text8 is RAW character stream with no labels, no grammatical structure, no
concept categories. Testing role-tagged context on text8 = labeling primitive
on an unlabeled corpus -> strategic confusion.

Redirect: extend SEMANTIC battery v2's chain-grade-eligible HARD_PASS to a
STRICTER compositional-generalization test. Substrate sees:
  (king, R_subj_of, ruling_action)
  (queen, R_subj_of, ruling_action)
and only:
  (prince, is_a, royal)
Can substrate predict (prince, R_subj_of, ?) -> ruling_action via category-
structure transfer, even though prince was never bound under R_subj_of?

This is the strictest extension of A3 generalization (heldout-instance) into
heldout-(instance, role) pairs.

## Verify-the-referent (Skunkworks N1 discipline)
- substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL/metrics.json:
  verdict=HARD_PASS (6/6 arms PASS). A3 heldout_top1 = 1.000 across 3 seeds
  (cv=0.000). A4 compose_top1 = 0.708 mean (cv=0.083). USER citation EXACT;
  this cell extends the A3/A4 task class with role-tagged binding.

## Mechanism
- 4 categories x 8 instances = 32 concepts; V_categories=4, V_instances_per_cat=8.
- V_roles = 6: R_subj_of, R_obj_of, R_property_of, R_pos1, R_pos2, R_pos3.
- V_predicates = 8 relation/action types.
- pure-numpy HRR; dense bipolar codebooks per seed; N=8192.
- Training:
  - Concept-KG: each (subject, R_role, predicate_action) atom Hebbian-ingested.
  - Each heldout subject sees ONLY (heldout, is_a, category) atoms in train --
    NEVER under R_subj_of with any action.
  - For trained subjects: full (s, R_subj_of, action) bindings stored.
- Eval:
  - Generalization query: (heldout_subject, R_subj_of, ?). Substrate must
    structurally complete to a category-appropriate action via category
    inference.
  - 4-way control: arms differ in role codebook construction (see Arms).

## Arms (5)
1. ARM_NO_ROLES                      -- control: store (s, p_action, o) directly with no R-binding.
2. ARM_ROLES_ORTHOGONAL_RANDOM       -- Plate canonical: role atoms = Gram-Schmidt orthogonal sparse-bipolar.
3. ARM_ROLES_SEMANTICALLY_CLUSTERED  -- R_subj_of ~ R_agent (close in HD); R_pos1/2/3 close to each other.
4. ARM_GRAMMATICAL_ROLE_BINDING      -- full triple binding: bind(subj, R_subj) + bind(action, R_verb) + bind(obj, R_obj).
5. ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS -- ARM_4 + label-driven anisotropic encoder for concept atoms (per Cell D).

## Config
- N=8192, V_categories=4, V_instances_per_cat=8 (total 32 concepts),
  V_roles=6, V_predicates=8.
- N_HELDOUT_INSTANCES = 8 (2 per category).
- 3 seeds [7, 17, 23].
- pure numpy CPU.

## HARD bands (compositional generalization to unseen subject in known role)
- HARD_PASS_CHAIN_GRADE: best arm top1 on heldout-subject role-tagged query >= 0.85 AND beats ARM_NO_ROLES by >= 0.20 AND CV across seeds <= 0.05.
- HARD_PASS: best arm top1 >= 0.70 AND beats ARM_NO_ROLES by >= 0.15.
- HARD_FAIL: ALL role-tagged arms within +/- 0.05 of ARM_NO_ROLES (roles don't help).
- MIDDLE_BAND: otherwise.

## Sanity rails
- ARM_NO_ROLES on TRAINED (s, action, ?) recovery >= 0.70 (proves storage primitive intact at this V/M scale).
- chance_top1 = 1 / V_predicates = 0.125 (predicate-space sized); explicitly reported.
- READOUT_DEGENERATE: if all arms within +/- 0.02 of chance -> degenerate flag.
- Refusal floor: substrate on (heldout, R_NEW, ?) where R_NEW never trained should return low-confidence; reported as audit.

## Discriminator
- ARM_ROLES_ORTHOGONAL_RANDOM vs ARM_ROLES_SEMANTICALLY_CLUSTERED isolates
  whether ROLE-SIMILARITY-STRUCTURE adds beyond pure Plate orthogonality.
  If clustered ~= orthogonal -> orthogonal is sufficient.
  If clustered > orthogonal -> roles benefit from semantic structure (brain-aligned).

## Timeout budget
- 3600s per USER spec; pure-numpy at N=8192, 32 concepts, 5 arms x 3 seeds, light.

## Routing
- remote_cpu_queue via orchestrator handoff.
- Anchor: substrate_role_tagged_compositional_generalization_on_concept_KG_v1.
