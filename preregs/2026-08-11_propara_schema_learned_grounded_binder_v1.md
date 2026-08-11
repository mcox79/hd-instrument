# Pre-registration: exp_propara_schema_learned_grounded_binder_v1

**Filed by:** exp_dev, 2026-08-11. **Task source:** director spawn (follow-up to the HARD_FAIL of
`exp_propara_schema_pattern_completion_v1`, commit e97a1437b). That cell proved schema pattern-
completion WORKS in isolation (self-test recovers the unmentioned participant "oxygen") but on
ProPara-as-scored the residual is per-participant GROUNDED BINDING: map a NAMED participant to its
schema slot/fate. Every prior binder (literal, graded concept_similarity, convergence-gate, native
thematic_role_labeler, and the v1 name-vector scoring) was UNSUPERVISED SURFACE MATCHING and all hit
the promiscuity wall (pair-precision 0.079). The one untried lever: a LEARNED glass-box grounded
binder, composed with the validated completion + selection.

## Prior-work check (SUBSTRATE-KB)
`bash tools/substrate_query.sh "learned grounded slot binding gam additive log-odds wordnet
supersense participant fate"` inherits the v1 cell's check (top hits `pattern_completion` registry,
"Partial Slot Filling" design note, both < 0.35, neither a learned-binder-over-completion cell). The
learner organ itself (`hdlab.learner.plugins.gam_plugin`) is WIRED (banked 29487) and PROVEN this
session on MAVEN-ERE for exactly this shape (additive log-odds + MDL-gated interactions ~doubled
precision by learning which cue-combinations predict the label). Novel composition: gam-over-schema-
completion for ProPara fate binding. Not a rediscovery.

## THE ONE VARIABLE
Keep the validated schema-completion + convergence-gated selection UNCHANGED. Swap ONLY the
per-(participant, schema-slot) FILL decision: promiscuous name-vector->slot scoring (v1's arm, pair-
precision 0.079 = the baseline/ablation) -> a LEARNED glass-box `gam` binary classifier
(FILL/SKIP) over grounded + interpretable features. Train on ProPara TRAIN gold, evaluate on DEV.

## Instances + supervision (no DEV/TEST leak)
One instance per (paragraph, convergence-gated-matched schema P, slot r in {consumes,produces,moves}
where P[r] is non-empty). TRAIN label = FILL iff effect(r) is in the participant's gold effect-set
from `_oracle_event_multiset` over TRAIN steps_df (the same participant-level oracle grant every arm
in this arc already uses); else SKIP. DEV/TEST gold is NEVER read for feature-building or prediction
-- only TRAIN gold sets labels. Inference: apply the fitted gam per DEV instance; FILL -> add
effect(r) + its trigger-verb-classes to `bridge[participant]` (bit-identical downstream contract to
v1 / the promiscuous arm).

## Features (grounded + interpretable string tokens for gam)
- `slot:{r}` -- the slot identity (label depends on it).
- `schema:{P}` and `schemaslot:{P}_{r}` -- active-schema identity (from selection/completion).
- `gm:{r}:{0/1}` -- does the participant graded-match P[r]'s word-list (v1's promiscuous signal, now
  a FEATURE the learner may reweight rather than threshold). CONTENT-derived -> scramble-sensitive.
- `cs:{r}:{bucket}` -- COMPLETION score bucket: cos(participant-name-vec, unbind(completed_schema,
  role_vec[r])) bucketed. Keeps the validated completion load-bearing in the binder; scramble- and
  completion-sensitive.
- `lex:{lexname}` -- WordNet lexicographer supersense of the participant head (owned WordNet access,
  same nltk.wordnet source as `hdlab.animacy_lexicon`; e.g. noun.substance/noun.artifact/noun.food).
  GROUNDED + generalizes across surface forms (log/timber/wood all -> noun.substance) = the lever for
  held-out-surface generalization.
- `cat:{category}` -- `hdlab.animacy_lexicon.lookup_animacy` category (person/animal/object/abstract),
  the owned WordNet-sourced glass-box category lexicon. GROUNDED.
- `surf:{headtoken}` -- participant surface head token. The MEMORIZATION channel: present for seen
  surfaces, absent (below gam min_coverage) for unseen -> the held-out control naturally tests
  whether the binder NEEDS surface memory or falls back to grounding.
- (native thematic-role feature = an available lever, toggled OFF for this decisive smoke: the frame-
  activation cell already showed native-roles-alone HARD_FAIL + it carries a McGuffey-trained caveat;
  the decisive question here is whether WORDNET GROUNDING generalizes. Documented, not exercised.)
gam additionally fits MDL-gated pairwise interactions (e.g. schema x lex, slot x gm) -- the exact
non-additive disambiguation ("in combustion, a noun.substance that graded-matches consumes ->
DESTROY") a pure sum-of-mains or a promiscuous threshold cannot represent.

## THE decisive control -- HELD-OUT SURFACE FORMS (the whole game)
SEEN = the set of participant head tokens appearing in any TRAIN participant. A DEV participant is
UNSEEN if none of its head tokens (len>2) is in SEEN. Report the learned binder's pair-precision/
recall (`_fact_coverage`) restricted to the UNSEEN-surface participants, vs the promiscuous baseline
on the same subset. If the binder only works on SEEN surfaces (unseen collapses to ~0 or ~promiscuous)
it MEMORIZED -> report plainly (not real grounding). If it beats promiscuous on UNSEEN, scramble-
clean, it LEARNED the grounding.

## Controls (all load-bearing)
- `prior_lesion`, `without_knowledge` (floor), `with_oracle` (ceiling) -- reused unchanged.
- `with_promiscuous_completion` -- v1's real schema-completion arm (pair-precision 0.079) = the
  BASELINE and the ABLATION (learned-binder swap disabled -> back to threshold scoring).
- `with_learned_binder` -- the mechanism.
- `with_learned_binder_scramble_kb` -- SCRAMBLE-SCHEMA (decoupled double-permutation via the owned
  `_scramble_kb_processes`) applied at DEV inference; the gam is trained on the REAL KB and applied to
  scrambled features -> gm/cs/schemaslot features decorrelate from the label -> must collapse.
- NO-LEAK: feature-builders take only paragraphs + KB; gold used solely to set TRAIN labels.

## Pre-registered bands (modest ceiling is fine; the point is the MECHANISM + generalization proof)
- `LIFT_BEATS_PROMISCUOUS`: learned unmentioned-F1 lift >= promiscuous lift AND learned pair-precision
  > promiscuous pair-precision (0.079 DEV-measured, recomputed live).
- `SCRAMBLE_MAX_RETAINED_FRACTION = 0.50` (reused): scramble retains <= 50% of learned lift.
- `GENERALIZES`: learned UNSEEN-surface pair-precision > promiscuous UNSEEN pair-precision AND
  memorization_ratio = unseen_pair_f1 / max(seen_pair_f1, eps) >= 0.34 (unseen does >= 1/3 as well as
  seen -> not memorized) AND learned unseen_pair_f1 > 0.
- `LEAK_CEILING = 0.95`, `LEAK_ORACLE_MARGIN = 0.02`, `WITHOUT_COLLAPSE_CEILING = 0.60` (reused).
- HARD_PASS = all of: infra + floor-collapse + no-leak + LIFT_BEATS_PROMISCUOUS + scramble-collapse +
  GENERALIZES. HARD_FAIL (with precise reason) = does-not-beat-promiscuous OR memorized (unseen
  collapses) OR scramble-does-not-collapse OR no-lift. MIDDLE_BAND = partial.

## Cell-template mandates (declared)
arms_differ_verified (6 arms hash-differ); final_metrics_atomicity: tmp_replace; except SystemExit
before except Exception (no bare/BaseException); crlb_n/a (F1 over fixed corpus + a counting/log-odds
learner -- no noise-floor threshold; the gam's own MDL compression_ratio is reported instead);
HP_SCOPE {with_learned_binder: [lift_beats_promiscuous, scramble_collapses, generalizes_heldout,
no_leak, arms_differ, decode_ok]}; cardinality_ok (single split, fixed 6 arms); per-unit failure-class
(no bare except); calibration_check: adaptive_with_discriminator_gate (gam min_coverage/interactions
pre-set; discriminator-fires = binder must beat promiscuous on the held-out subset, verified in
smoke); all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@; self-test constructs the REAL
gam over real features at tiny scale + a synthetic separable task proving the learner fires;
progress_logging: print_flush_true; deterministic_seeding: true (hashlib-seeded vectors; gam is a
deterministic counting fit; scramble reuses the F.5-compliant `_scramble_kb_processes`).

## Scope discipline (director instruction)
self-test PASS -> SMOKE (DEV; decisive; one-variable) -> STOP + report. No --full dispatch. No edits to
`exp_propara_bridging_frame_activation_v1.py` (owned by another agent) or the MAVEN cells -- import
only. Targeted commit; branch dataprep/mcguffey-graded-corpus; no origin push.
