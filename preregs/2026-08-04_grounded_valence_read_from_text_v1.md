# Pre-registration: exp_grounded_valence_read_from_text_v1

Date: 2026-08-04. Branch: dataprep/mcguffey-graded-corpus. Local-only (no queue/remote/push).

## Gap (localized by the prior disk-verified negative)
`exp_grounded_coherence_selector_v1` verdict = GROUNDED_PARTIAL_LEXICAL_PROXY. The grounded
coherence SELECTOR is grounded-faithful in-sim, but `valence_only` text transfer = 0.5143 (chance):
the frozen blind lexicon `resolve_valence_blind` (HARM_WORDS/HELP_WORDS from
exp_situated_goal_structure_valence_v1) CANNOT read appraisal off literary prose. Disk-verified per-item
(data/exp_grounded_coherence_selector_v1/metrics.json): it labels the true-cause spans NEUTRAL
(001 "drove the knife to the hilt in the breast", 003, 007, 008 "poured ink upon the page"), mislabels the
spiteful-withholding 004 "let her take care of herself" as HELP, and sign-flips 005 (true "bowl dropped
and broke" = NEUTRAL, distractor "scolding" = HARM). The gap is UPSTREAM of the selector: earning a
grounded VALENCE read from raw literary text.

## Question
Can we EARN a grounded valence read -- via the substrate's OWN organs (NOT the frozen lexicon, NOT a
bolt-on parser, NOT a borrowed embedding/LLM) -- that assigns harm/help/neutral to the candidate ACTIONS
such that `valence_only` selection of the true cause clears chance (>0.5) AND beats the frozen-lexicon
baseline 0.5143, on the 7 Director-verified items (grapp_mcca_001/003/004/005/007/008/009; 006 EXCLUDED)?

## Mechanism (earned grounded valence read) -- brain-foundational, glass-box
Reuse the grounded appraisal organs that DID transfer given structure:
- `hdlab.coreference_resolver.normalize_tokens` -- situation-model relational tokenizer (agent/patient
  content lemmas). Reused verbatim.
- `hdlab.situation_model_accumulate.AccumulateRegister` -- the VET-confirmed FHRR situation-model
  accumulate organ (atom 29609). Used as the APPRAISAL ACCUMULATOR: each grounded harm/help evidence unit
  is a role-bound event; the register bundles them; decode -> dominant valence. Brain: hippocampal
  situation-model role-binding accumulation. Reused verbatim.
- `exp_grounded_appraisal_sim_earned_v1.rand_fhrr` -- FHRR atom builder (project-native). Reused.
- Loader + contamination guard `load_items`, `mech_inputs`, `TRUE_SLOT` from
  `exp_coherence_selector_text_transfer_v1`. Reused verbatim.

The valence of a candidate ACTION = the sign of its accumulated effect on a valued patient/goal, read via
GROUNDED HARM/HELP EVENT PRIMITIVES (the ~6yo grounded foundation). These primitives are SUPPLIED KNOWLEDGE
(supplying knowledge/data is allowed; supplying the reading mechanism is not) -- a GENERAL store of
harm/help action classes (injure-animate, damage-object, deprive/withhold, deceive/misplace; warn/rescue/
protect/comfort), grounded through patient/object affordance and a hypothetical-modality guard, declared
HERE BEFORE running and NOT keyed to the 7 specific spans (no proper nouns, no item phrases).

Read (per candidate span, uses ONLY the candidate span text -- NEVER the goal/query/outcome text, so it is
structurally immune to outcome-vocabulary overlap gaming): tokenize; count harm-verb and help-verb hits;
gate harm evidence on a valued patient/object being present (grounded: harm needs something harmed) and on
not being purely hypothetical/conditional (grounded: a threatened future hanging "if they catch him" is not
an enacted harm); accumulate the evidence units in the FHRR register; decode HARM/HELP/NEUTRAL.

## Selection rule (fixed, pre-registered)
All 7 outcomes are NEG (blocked/harmed goal). The causally consistent valence is HARM. Pick the candidate
read HARM. If both HARM or neither HARM (tie) -> ABSTAIN (scored incorrect; no lexical-overlap fallback --
that was the prior proxy failure). `valence_only` selection accuracy = fraction of 7 items picked correctly.

## Arms
- FROZEN_LEXICON: `resolve_valence_blind` (target: reproduce ~0.514).
- EARNED_GROUNDED: the earned read above (with the hypothetical/patient guards).
- EARNED_GROUNDED_NO_GUARD: same, guards off (transparency ablation; not a tuned pick).
- EARNED_NO_KNOWLEDGE: the SAME read with the harm/help primitive store EMPTIED (the substrate with NO
  supplied grounded harm knowledge) -> all NEUTRAL -> demonstrates the routing to building/supplying
  grounded harm knowledge.
- RANDOM_VALENCE (floor, per-seed): uniform {HARM,HELP,NEUTRAL} per candidate. MUST fail.
- SHUFFLED_VALENCE (floor, per-seed): EARNED_GROUNDED labels permuted across the 14 candidate slots. MUST
  fail (breaks the span-label correspondence).

## Adversarial guard (mandatory) -- 003 and 007 are the recency-trap
The distractor shares more outcome/harm vocabulary than the true cause: 003 distractor names Jo as the
default suspect ("pranks", "hand in this"); 007 distractor "I set Diana _drunk_ ... disgraceful condition"
lexically describes the harm while the TRUE cause is Marilla's subtle misplacement ("put the cordial in the
cellar instead of the pantry"). The earned valence must NOT be gamed by surface overlap. Because the read
never consumes the outcome text, it cannot be gamed by outcome overlap by construction; but 003/007 may
still FAIL because the true harm act is out-of-span (003: forgery not in the span) or subtly causal/
counterfactual (007). Reported specifically per the directive.

## Floors / guards
- RANDOM and SHUFFLED must not beat chance materially (report; MUST_FAIL).
- Contamination: valence read consumes ONLY candidate span text; assert primitive tables contain no proper
  nouns and no item-specific phrases; loader's MECH_FORBIDDEN_FIELDS guard reused (no gold-answer leak; the
  item-007 goal_owner leak is avoided -- goal text is never read by the valence mechanism at all).
- Determinism: torch.Generator per seed; sorted(set()); OMP/OPENBLAS/MKL=1; no hash()-seed. FHRR accumulate
  decode asserted == direct-count valence (organ faithfully realizes the accumulation).
- Resumable per-seed via tools/exp_checkpoint.py. Multi-seed SEEDS=[0,1,2,3,4].
- n=7 TINY -- DIRECTIONAL, not powered. Stated in every claim.

## Verdict bands (set before running)
- EARNED_BEATS_LEXICON_AND_CHANCE: EARNED_GROUNDED > 0.5143 AND >= 0.5 AND RANDOM/SHUFFLED floors fail AND
  003/007 not both won by surface overlap -> real progress on the extraction bottleneck (VET hard, n=7).
- ROUTES_TO_GROUNDED_HARM_KNOWLEDGE: EARNED_GROUNDED does not cleanly beat the lexicon AND EARNED_NO_KNOWLEDGE
  ~ chance -> the failing spans need grounded harm knowledge the substrate lacks (per-span reported). The
  appraisal MECHANISM is faithful; the gap is the missing grounded world knowledge -> route to building it.
- MECHANISM_ARTIFACT: if EARNED_NO_KNOWLEDGE or floors DON'T fail -> construction/similarity artifact; deflate.

## Honest can-fail
Reading valence off "drove the knife to the hilt in the breast" requires grounded harm knowledge
(knife+body=harm) -- exactly the ~6yo foundation. Where the substrate lacks it, the earned read WILL fail;
that routes to building/supplying grounded harm knowledge (allowed), not a mechanism fix. Reported honestly,
per-span, not hidden.
