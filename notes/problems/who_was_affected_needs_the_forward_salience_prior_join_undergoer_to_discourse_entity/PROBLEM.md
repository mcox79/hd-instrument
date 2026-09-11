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
