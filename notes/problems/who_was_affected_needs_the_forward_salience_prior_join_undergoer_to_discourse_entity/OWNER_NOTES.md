---
owner_verdict: DONE
---

SUBMISSION — problem: who_was_affected_needs_the_forward_salience_prior_join_undergoer_to_discourse_entity
(status: SOLVED, WIP until owner_verdict: DONE)

ONE-LINE RESULT. Built the affected-entity JOIN (undergoer token → coref mention → gold discourse
chain; a join that did not exist) on GUM, and found the correct lever for resolving object/undergoer
PRONOUNS: it is GRAMMAR (Binding Principle B + role/thematic parallelism = the LIKELIHOOD half),
not semantics. Two CI-separated, fully-controlled, mathematically-BF wins.

WINS (GUM modern, hard ambiguous pronoun-undergoer subset):
  • Milestone 1 — forward SALIENCE prior (ACT-R/Centering) applied to the undergoer decision:
    0.4545 vs recency floor 0.1818, +0.2727 CI[0.18,0.36]. Scramble collapses; twin loses; lexical
    stratum near-floor (discourse-specific). Witness test_affected_entity_salience_prior 4/4.
  • Build 4 — the corrected lever (LIKELIHOOD): Principle-B co-argument filter + role/thematic
    parallelism over salience. KILLER DIAGNOSTIC: the subject-biased model was ranking the ILLEGAL
    co-argument #1 ~19% of the time. Gold roles: A2 Principle-B (parameter-free) +0.048 CI-sep,
    A5 full +0.093 CI-sep, robust across γ. DEPLOYMENT (predicted supervised parse, n=952): +0.049
    (Principle B, robust) to +0.060 (full) CI-sep — the win SURVIVES the real parse.
    Witness test_affected_entity_binding_parallelism 4/4.

LOCATED NEGATIVES (earned the win): type-coherence (redundant given phi-agreement) and
implicit-causality (misapplies — it's a next-mention prior for a FOLLOWING pronoun, not the verb's
own argument; IC-alone below chance). Both witnessed; both forced the research that found the lever.

BF STATUS (owner-verified mathematically BF; full table in SOLVED.md):
  • BF / PINNED: salience_binder (BF); Principle B (PINNED universal, built fresh from the parse);
    parallelism (PINNED Bayesian likelihood exp(γ·1[role-match]), γ swept); Ernst-Banks inverse-
    variance fusion (PINNED — replaced the BF_SPIRIT margin weighting); Ferstl IC norms (empirical
    human asset). Every BF_SPIRIT organ in a winning path was upgraded/reimplemented before use.
  • NOT_BF: the pos_tagger/arc_parser/arc_labeler parse spine — a DECLARED offline scaffold; the
    headline was measured on gold roles AND re-measured on the predicted parse (it survives).

BRAIN COMPARISON (honest): ~0.46 on the hard ambiguous slice vs ~0.85–0.90 competent human and
~0.67 trained-neural (GAP). Grammar levers ~harvested (~0.55 reachable). Remaining ~40% is genuinely
world-model-bound → the generative entity-state/situation model (north star), not yet built.

PRIORITY NEXT STEPS:
  1. LAND the corrected resolver (Principle-B filter + role-conditioned salience) into the live
     situation_reader undergoer pick (Q111); add board_affected_entity_dimension so it's scored.
  2. BUILD 5: the generative entity-STATE/world-model reranker (state_register; Dowty change-of-state
     × Rabovsky-McClelland N400) for the ~40% situation-bound residual — the deepest, hardest lever.
  3. Recover the deployed parallelism term (degrades ~1/3 under predicted role labels — role-labeler /
     graded-role improvement).

FILES: experiments/exp_affected_entity_{salience_prior,reliability_fusion,ic_prior,binding_parallelism}
_gum_v1.py, exp_typed_selectional_preference_v1.py, exp_parse_cache_v1.py + 5 verification/ witnesses.
No hdlab/ writes (Q111 — proposed diffs in SOLVED.md). Reverify: run the 5 witnesses. Ledger malformed 0.
