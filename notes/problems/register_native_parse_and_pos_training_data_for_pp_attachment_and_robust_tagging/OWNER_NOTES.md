---
owner_verdict: DONE
---

SOLUTION SUBMISSION -- register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging

STATUS: REFUTED (the bar's sanctioned located-negative -- plus a DECONFOUNDED positive: the real lever is
demonstrated). Witness verification/test_register_native_located_negative.py = 13/13; problem_ledger --check
clean. WIP until owner_verdict: DONE. Solver: opus 4.8. NO hdlab/ writes, nothing pushed.

THE PROBLEM I WAS ASSIGNED: acquire/build GOLD 19c parse+POS data and train the substrate's own parser/tagger on
it to raise PP-chain attachment + 19c who-did-what (holding modern, no regression) -- or a located negative naming
the data blocker.

HEADLINE: register PARSE/POS DATA is NOT the 19c who-did-what lever, and the brief's premise is partly a
measurement artifact. The real lever is SELECTION (which noun is the verb's argument), it lives at the meaning/
thematic-fit STORE not the grammar, and its mechanism is COMPOSITION (P(patient|agent,verb)) -- which I built from
RAW exposure (no gold) and DEMONSTRATED real. I drilled every wall to its brain mechanism (BRAIN_MECHANISM_DRILL.md).

KEY FINDINGS (each CI-controlled, twins reported):
  * DATA BLOCKER real but not the lever: no gold 19c UD parse/POS treebank on disk (LitBank = coref/NER/events +
    raw novels; only modern UD-EWT is gold). PP-attachment is only 8% of the 19c reachability residual; a faithful
    raw-exposure PP re-attach HURTS post-hoc / is a no-op gated.
  * PREMISE CORRECTION: the "19c verb-ID collapses -0.10" that motivated the brief is 87% COPULA-as-AUX (correct
    UPOS, not tagger error). Genuine archaic open-class mistag = 2.2%; frequent-frames register tagging net-negative.
  * COPULAR predication ("X was a Y") is a real, separate representation gap: base reader 0/376 on clean predicate
    complements (no is-a binding schema); ~23% of the population. Register-independent; file separately.
  * SELECTION is the bottleneck (27% reachable-but-mispicked). The register bites the STORE: the structured
    thematic-fit store beats its verb-shuffle twin +0.081 CI-sep on MODERN but ties it on 19c.
  * PROTOTYPED the fix (hand-off artifacts, experiments/ only): (a) register re-estimation ALONE -- insufficient
    (ties twins); (b) richer PPMI-SVD representation -- also ties on the CONTAMINATED gold, but on the CLEANED
    direct-object gold the verb-specific signal is REAL (beats verb-shuffle twin +0.097 CI-sep) -- the 19c gold is
    ~85% oblique-contaminated; (c) COMPOSITION P(patient|agent,verb) -- beats its info-free AGENT-SHUFFLE twin
    +0.076 CI[+0.029,+0.123] and position +0.158 CI-sep. Composition is the demonstrated-real lever; its full
    margin over marginal/bag-of-args is underpowered at n=171 clean-DO and needs a larger cleaned gold.

WHERE THE LEVER IS (route, don't re-derive): a role-STRUCTURED + agent-COMPOSED + taxonomically-SMOOTHED thematic-
fit store, re-estimated on 19c raw exposure, smoothed via the grounded semantic-graph organ -- owned by
role_assignment_is_untested_on_archaic_literary_prose / the_plausibility_prior_is_a_coarse_centroid... /
grounded_role_assignment_via_verb_keyed_thematic_fit. The parser's ONLY real service to it is emitting TYPED
argument slots (nsubj/obj/obl) to BUILD the store -- not PP-attachment, not register tagging.

IS PERFORMANCE MAXED: within this problem's scope (parser/tagger/register data) YES -- exhausted. Overall 19c number
NOT maxed, but the residual is mostly MEASUREMENT (85% gold contamination) + a copular is-a binding + a
composition lever bounded to the clean ~15%. Don't expect the number to jump.

FILES: experiments/{exp_register_native_pp_attachment_v1, exp_19c_reach_failure_diagnosis_v1,
exp_19c_tagging_lever_ceiling_v1, exp_19c_copula_disambiguation_v1, exp_register_native_levers_v1,
exp_19c_thematic_fit_reestimation_prototype_v1, exp_19c_distributional_thematic_fit_prototype_v1,
exp_19c_composition_thematic_fit_prototype_v1}.py; verification/test_register_native_located_negative.py (13/13);
notes/problems/<slug>/{SOLVED.md, BRAIN_MECHANISM_DRILL.md}. CITED not modified: exp_verbrole_exemplar_which_arg_v1
(structured store: works modern, ties twin on 19c), exp_pivot_selectional_knowledge_richness_2afc_v1
(knowledge-poverty wall).
REVERIFY: .venv/Scripts/python.exe verification/test_register_native_located_negative.py

NEXT STEPS FOR STRATEGY: (1) retire the parse/POS-data framing; (2) route selection to the owned problems with the
bounded recipe -- COMPOSITION + gold-cleaning (NOT re-estimation/representation, both ruled out here); (3) file the
copular is-a binding as a small frontend problem; (4) CLEAN the 19c who-did-what gold (85% oblique-contaminated)
first; (5) fold the AUDIT UPDATE (copula-as-AUX correction; register bites the store; parser=typed slots) into
BRAIN_FOUNDATIONAL_AUDIT.md sec.2b. DO NOT re-open PP re-attach, frequent-frames tagging, or gold-19c-parse
acquisition.

TLDR (plain English): the job was to fix "who did what" on 200-year-old prose by getting old-style annotated
grammar data and retraining the grammar reader. It turns out that's the wrong lever: the reader already parses old
grammar about as well as it needs to (the scary "old verbs break the tagger" number is 87% just "is/was/were"
tagged correctly as helper-verbs). The real problem is picking which noun the verb acts on -- a meaning judgment --
and it needs knowing the typical event, combining the doer and the action to expect the thing-done-to. I built
that from plain reading (no hand-labeled data) and showed it genuinely works once you stop scoring it against a
noisy answer key. It's a meaning-store build, not a grammar-data build, and it belongs to the existing
role-assignment problem -- I handed it a de-risked, bounded spec.

QUESTIONS: fund the composition build on a larger cleaned direct-object gold (owned selection problem)? My
recommendation: yes, clean the gold first. Building a gold 19c parse/POS corpus (the brief's route): recommend
against (caps ~8%, misses the lever).
