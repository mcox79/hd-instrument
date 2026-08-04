# Pre-registration: coherence_selector_novel_types_v3 (2026-08-04)

## Problem (why v2's HARD_PASS is not yet the real competence)
`coherence_selector_insim_v2` (data/exp_coherence_selector_insim_v2/metrics.json) landed
HARD_PASS: the reverse-replay coherence selector generalized to NOVEL ENTITIES
(entity_overlap=0) via shared structural TYPE features; a shuffled-structure control
collapsed 1.0 -> 0.27 (structural_lift 0.73). BUT `train_eval_type_overlap_frac == 1.0`:
v2's EVAL reused the SAME 10 types as TRAIN, only the ENTITY instances were novel
(entity = type_vector + 5% noise). So v2 demonstrated robustness to novel INSTANCES of
KNOWN types under a KNOWN single-hop grammar -- it did NOT test whether the mechanism
learned an ABSTRACT coherence rule that transfers to types/relations UNSEEN in TRAIN.

Moreover, v2's grammar was `RULE: type_id -> type_id`, an arbitrary random BIJECTION over
discrete type INDICES (a 10x10 lookup table). Under that construction a novel type index
has NO entry in the table and RULE[novel_type] is undefined -- so testing v2's mechanism on
novel types would be UNFAIR (unsolvable by ANY mechanism, rigged to fail).

## The discriminating question
Did v2 learn an ABSTRACT transferable coherence RULE (generalizes to novel types/relations)
or just MEMORIZE this grammar's per-type transition TABLE (works only for seen types)?

## Fairness fix -- a CONSISTENT structural transform (novel types solvable IN PRINCIPLE)
To make the novel-types test FAIR, the grammar is a CONSISTENT STRUCTURAL TRANSFORMATION,
NOT an arbitrary per-type-ID bijection:
- `T` = a fixed random PERMUTATION of the N_DIM=2048 coordinate axes, generated ONCE per
  seed and applied IDENTICALLY to every type's content vector (orthogonal, invertible,
  bipolar-preserving). This is the SAME `T` for seen and novel types.
- Each type `t` (seen, novel, or scale) gets an independent i.i.d. random bipolar base
  vector `b_t`, drawn from the SAME generative distribution for all type ranges (the
  fairness-critical property: nothing about a novel type's distribution differs from a seen
  type's -- only its index range and whether TRAIN ever samples it).
- A causal chain for type `t` is the iterated orbit of `T`: `u_0=b_t, u_1=T(u_0),
  u_2=T(u_1)`. A cause->effect edge is `hop_k -> hop_{k+1}` within one chain.
- Because "effect content = T(cause content)" holds via the SAME `T` regardless of type,
  a mechanism that learns `T^-1` in the shared 2048-dim vector space can invert it for ANY
  content vector, novel or seen -> novel types are solvable IN PRINCIPLE. This is
  content-addressable / hippocampal-relational-match style, NOT a discrete type-ID table.

## Hypothesis
A backward SR-transport map `M_backward` (TD(0) delta-rule, `train_sr_transport`) trained
ONLY on TRAIN-partition (seen types 0..9) reversed chain transitions will, IF it has learned
`T^-1` as a content transform rather than a per-type association, discriminate the true
antecedent from a narratively-more-recent distractor on EVAL episodes built from BRAND-NEW
never-seen types (disjoint type-index range, fresh i.i.d. base vectors), purely from vector
content -- an ABSTRACT competence.

## Mechanism (reuse, brain-structure-tagged; NO new organ)
- SR-transport backward map: `exp_pfc_gate_cfrpe_trained_v2.train_sr_transport` (TD(0);
  TD-error == RPE). Brain: hippocampal-striatal successor representation (Dayan 1993 /
  Stachenfeld 2017), reverse replay (Foster & Wilson 2006), need x gain (Mattar & Daw 2018).
- Scoring: `reach_value(outcome_E, candidate_E, M_backward)`, reused verbatim.
- NO_REPLAY_LOCAL floor / anti-tautology: `reach_control_targetcos` (M:=identity).
- Situation-model buffer: `AccumulateRegister` (glass-box sanity, not scorer).
- Abstain-band: `decide_keep_or_revert` / `ABSTAIN_BAND_DEFAULT` over the reach margin.
- Recency floor: literal narrative-position comparison.

## Arms (all scored against the SAME single M_backward per seed, trained once on seen types)
- **ARM_NOVEL_1HOP (primary discriminator)**: EVAL from N_TYPES_NOVEL=10 brand-new types
  (indices 10..19, disjoint from TRAIN), 1-hop episodes.
- **ARM_NOVEL_2HOP (multi-hop stress)**: same novel-type partition, outcome=hop2,
  true_cause=hop0 (grandparent via 2 chain edges). Tests coherence over longer chains.
- **ARM_NOVEL_SCALE (vocab-scale stress)**: a 4x-larger disjoint type range
  (N_TYPES_SCALE=40, indices 20..59), 1-hop, SAME M_backward (no retrain). Tests whether the
  learned map is type-COUNT agnostic.

## Floors (each arm's EVAL, MUST fail): RECENCY, RANDOM, NO_REPLAY_LOCAL.
## Anti-memorization controls
- **SHUFFLED-STRUCTURE** (on ARM_NOVEL_1HOP episodes): novel-partition embeddings replaced by
  i.i.d. random bipolar UNRELATED to the T-orbit; M_backward held fixed. MUST collapse toward
  chance (coherence <= 0.65, structural_lift >= 0.15) for the win to attribute to structure.
- **Type/entity disjointness asserted on disk**: `train_eval_entity_overlap==0`,
  `train_eval_type_overlap_novel==0.0`, `train_eval_type_overlap_scale==0.0`.
## Positive control: ORACLE == 1.0/1.0 (train + every eval arm) -- chain-construction sanity.

## HARD-PASS bands (ARM_NOVEL_1HOP primary; per-arm gates via record_gate)
- coherence_eval_acc >= 0.75; min_lift over all 3 floors >= 0.15; glassbox margin > 0 every
  seed; shuffled coherence <= 0.65 AND structural_lift >= 0.15.
- HARD_PASS requires ARM_NOVEL_1HOP pass AND both stress arms (2hop, scale) pass their
  own floor/margin/positive-control bar; ARM_NOVEL_1HOP pass but a stress arm short ->
  MIDDLE_BAND (partial/scope-limited competence).

## Honest-result contract
- GENERALIZES on ARM_NOVEL_1HOP (novel types) => ABSTRACT transferable rule = real
  competence (report the number vs floors + shuffled control).
- FAILS novel types => MEMORIZED TABLE despite the fair content-addressable construction:
  informative NEGATIVE. Debug impl FIRST (confirm T is learnable + SR TD converged
  err_last<err_first) before concluding mechanism-level failure; then route the DIRECT
  effect<->outcome content-MATCH reformulation (reach_control_targetcos-style raw geometric
  match within the episode, no learned type-table) as the next redesign. Do NOT force a pass.

## Determinism / resumability
5 seeds [7,17,23,31,41]; torch.Generator + numpy default_rng seeded per component;
per-seed atomic checkpoint via `_seed_checkpoint`; store atomic tmp+replace. Local-only:
no queue, no remote dispatch, no push.

Author: exp_dev-role direct run (agent-spawn), 2026-08-04.
Cell: experiments/exp_coherence_selector_novel_types_v3.py
Out: data/exp_coherence_selector_novel_types_v3/metrics.json
