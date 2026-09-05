---
owner_verdict: DONE
---

SUBMISSION — problem: seed_the_entity_world_model_resolver_with_a_world_knowledge_role_kinship_prior_phase1
status: SOLVED (WIP until owner_verdict: DONE)

BAR (verbatim): a glass-box static role/kinship/scenario KB (foundation asset; NO LLM) seeding the entity
world-model resolver such that, on DEPLOYMENT, common-noun coref rises CI-sep over surface-head + unseeded
floors, AND a shared downstream (affect experiencer OR relational reference) rises CI-sep, with a shuffled-KB
info-free twin LOSING and no-regress on named coref. A rigorous located NEGATIVE (the prior needs per-text
instance binding no static KB supplies) is a FULL PASS.

RESULT — ALL FOUR CLAUSES MET (100 held-out LitBank docs, deployment self-built records, doc-level bootstrap,
floors recomputed per population). The KB seed ALONE is a LOCATED NEGATIVE (~2% coverage — the brief's exact
prediction); the wall is CROSSED by the brain-foundational CHAIN it belongs to:
  KB + situation-model instance binding + pronoun-into-entity resolution + the reader's REAL per-text head-coref.
  1) common-noun coref: aggregate char-cluster CoNLL 0.6046->0.6855 = +0.0809 CI[+0.0696,+0.0909] CI-sep;
     hard-link target pop 0.2537->0.4342 = +0.1793 CI[+0.1467,+0.2117], held-out A +0.1786 / B +0.1776 (both
     CI-sep) = 63% of the baseline->gold-ceiling(0.540) gap.
  2) downstream relational reference ('her father', 493 pairs) 0.3570->0.5010 = +0.1440 CI[+0.0768,+0.2132] CI-sep.
  3) shuffled-KB twin LOSES on the KB's populations (hard-link 0.4342>0.4187; downstream +0.0243 CI-sep);
     NOT-sep on aggregate (aggregate driver is the broader chain, not the KB — honestly reported).
  4) named coref NO-regress: -0.0034 (not sep).

HOW WE WON (the key findings for strategy):
  - THE EXACT SIGNAL LOSS: decomposed every hard failure -> 66% candidate-set misses, and 79% of those are
    because the true antecedent's most recent mention was a PRONOUN ("i"/"you"/"my"/"himself"...) that the
    resolver SKIPPED. Exact brain diff: the brain keeps one entity per character and binds pronouns INTO it
    (Sanford-Garrod); we threw them away. Fix (pronoun-into-entity) dropped gold_entity_absent 505->170,
    raised the candidate-set ceiling 0.34->0.40.
  - COMPONENT ATTRIBUTION: KB alone ~2%; composite salience ALONE +0.000 (must GATE accessibility, not
    re-score); pronoun-into-entity = the diagnosis-driven fix (aggregate +0.006->+0.067); the READER'S REAL
    COREF = the biggest single lever (hard-link 0.36->0.43, aggregate ->+0.081, downstream ->0.50).
  - THE READER-INTEGRATION LESSON (load-bearing for future wiring): the reader's AGENT via head-match
    REGRESSED named coref (-0.0064 CI-sep, lossy); the reader's COREF via its real sm.entities clustering was
    clean and the biggest win. Same upstream, two couplings, opposite signs -> "not truly brain-foundational
    SOMEWHERE" made concrete.

WHAT TO LAND (proposed hdlab, Q111): promote resolve() with the full chain
(salience=composite, kb, repair, sitmodel, attrs, pron_coref, reader_coref=<per-doc reader entity head-sets>)
+ ship the curated KB to data/frontend_assets/role_kinship_scenario_kb.json + wire the reader's sm.entities
head-coref (already computed in the live read) into commonnoun_binder. Default-ON justified (aggregate CI-sep,
downstream CI-sep, named no-regress). DO NOT wire the reader AGENT head-match (it regresses names).

KEY GOING FORWARD: push past 0.434 toward the 0.540 ceiling — the reader's own coref is only 0.58-accurate,
so a better substrate pronoun/coref resolver is the next lever (bidirectional: the resolver also improves the
reader). Remaining residual is rank_miss/abstain (a smaller scoring refinement).

CONTROLS: shuffled-KB twin (loses on KB populations); held-out even/odd (both CI-sep, zero fitted params);
named no-regress; signal-loss decomposition (candset-miss/abstain/rank-miss + reasons + oracle ceiling);
per-component ablation.
FILES: experiments/exp_entitykb_resolver_v2.py, experiments/exp_reader_sitmodel_cache_v1.py (+ cache),
verification/test_entitykb_resolver_v2.py (6/6), RESEARCH_brain_mechanism_upstream_chain.md, SOLVED.md.
NO hdlab/ writes. NO external LLM.
REVERIFY: .venv/Scripts/python.exe verification/test_entitykb_resolver_v2.py   (6/6 PASS)
