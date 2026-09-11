# PROBLEM — who-was-affected needs the FORWARD SALIENCE PRIOR: join the undergoer to the right discourse entity

**slug:** `who_was_affected_needs_the_forward_salience_prior_join_undergoer_to_discourse_entity`
**opened:** 2026-09-10 (solver full-auto), situation-model milestone 1 of the who-was-affected program.
**status:** OPEN. Solver writes `experiments/`, `verification/`, this folder only. NO `hdlab/` (Q111 — propose diffs).
Glass-box; **NO external LLM at inference**. Grade on MODERN gold (GUM; 19c-banned). THE DISK OUTRANKS THE BRIEF.

## The measured bottleneck (why)
"Who was affected" does not fail at the intra-sentence undergoer SLOT (`who_did_what_patient = 0.83`, near-solved).
It fails at ENTITY RESOLUTION: the undergoer is a pronoun/definite that must resolve to the right DISCOURSE ENTITY
(the coref board dim is the stuck residual; the oracle probe put the whole headroom in entity separation + recency).
Selectional-knowledge densification (typed Resnik) fixed coverage but NOT recovery — the residual is genuine
AMBIGUITY that needs a generative situation model. This is the project's 09-10 coref reframe: reference = FORWARD
situational-address PRIOR × BACKWARD retrieval LIKELIHOOD; only the backward half was built. The FORWARD prior —
the salient/topical/given entity is the likely undergoer (Centering Cb/Cf; Givenness Hierarchy; Kehler-Rohde
Bayesian pronoun resolution) — is an existing BF organ (`salience_binder`, `__bf_status__=BF`) that is applied to
generic pronoun anaphora but NEVER to the undergoer/affected decision. And the JOIN (undergoer TOKEN → coref
MENTION → resolved CHAIN) does not exist anywhere: patient work is token-level, coref work is pronoun-level.

## The bar
PASS = build the affected-ENTITY metric on a modern coref×role corpus (undergoer token → coref mention → gold
chain), and show the FORWARD SALIENCE PRIOR (the BF salience-coref organ applied to the undergoer decision) recovers
the correct discourse entity CI-separated over the recency floor, concentrated on the PRONOMINAL stratum, with the
control stack (scramble discourse order → collapse; info-free twin → lose; lexical stratum → near-floor; no-leak)
— OR a rigorous LOCATED NEGATIVE. The stratum split (pronominal vs lexical) IS the intra-sentence-vs-discourse
scoping test. Report CI half-width; floors on the item's OWN population.

## First steps (discipline)
- REUSE the BF organs (do not rebuild): `salience_binder` (BF, ACT-R base-level + Centering ROLE_PROMINENCE),
  `unified_referent` / `online_entity_cluster` (BF_SPIRIT coref), `convergent_cue_reader` (reliability weighting),
  the GUM reader (`gum_coref.load_docs`, `gum_to_live`). GUM carries gold deprels AND gold coref in one file.

> **BRAIN-FOUNDATIONAL CHECKLIST:** 1) which structure resolves the ambiguous undergoer? the forward
> situational-address PRIOR = salience/Centering over discourse referents (Grosz/Joshi/Weinstein; Lewis-Vasishth
> ACT-R; Kehler-Rohde). 2) COPY the computation (ACT-R base-level B = ln Σ w(role)·dt^-decay), SWEEP decay. 3) is
> each organ BF? salience_binder=BF; coref stack=BF_SPIRIT; GUM+WordNet admissible. 4) measure vs the recency floor
> on the item's OWN pronominal population, CI-separated; scramble must collapse; twin must lose. 5) route the
> residual (the still-hard cases) to the next build (entity-STATE ΔSG coherence). PHASE-DIAGRAM: decay/role weights
> free to sweep.


<!-- GUARD SECTIONS (appended by strategy 2026-09-11 for brief-cert conformance; the fleet brief above is the primary statement, SOLVED.md is authoritative). -->
## THE PROBLEM IN PLAIN LANGUAGE
"Who was affected" does not fail at the intra-sentence slot (who-did-what is near-solved at 0.83) but at resolving the undergoer PRONOUN to the right DISCOURSE ENTITY. The brain resolves it with the FORWARD situational-address prior (the salient/topical entity is the likely undergoer). See the fleet statement above and SOLVED.md.

## WHY THIS ONE
It is the FORWARD half of the 09-10 coref reframe (reference = forward prior x backward likelihood); only the backward half was built. The salience organ was applied to generic pronouns but never to the affected decision.

## MEASURED vs INFERRED
MEASURED: who_did_what_patient 0.83, coref residual stuck. INFERRED (now PROVEN): the forward salience prior recovers the entity +0.2727 CI-sep, and the corrected grammatical lever (Principle B + parallelism) +0.093 CI-sep (survives the predicted parse +0.049/+0.060). See SOLVED.md.

## ALREADY TRIED
Type-coherence and implicit-causality as the same-type discriminator = both LOCATED NEGATIVES (SOLVED builds 2/3). Do not re-run either.

## VERIFY BEFORE YOU START
Reuse salience_binder (BF) / unified_referent / online_entity_cluster / the GUM reader; read SOLVED.md IN FULL. Modern gold only (GUM; 19c banned). Cap cores (OMP_NUM_THREADS=4 ...).

## THE BAR
See "## The bar" above: recover the discourse entity CI-separated over the recency floor on the pronominal stratum with the full control stack (scramble collapses, twin loses, lexical near-floor, no-leak), or a rigorous located negative.

## FILES AND ENTRY POINTS
experiments/exp_affected_entity_{salience_prior,reliability_fusion,ic_prior,binding_parallelism}_gum_v1.py + the 4 verification/ witnesses; hdlab/affected_entity_resolver.py (landed); hdlab/situation_reader.py (undergoer decision).

## DO NOT QUOTE
Retired figures (notes/reference_retired_claims_never_requote.md); no spaCy / external LLM at inference; no 19c corpora (McGuffey/LitBank).
