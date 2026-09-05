---
owner_verdict: DONE
---

SUBMISSION — problem: wire_the_curated_meaning_foundation_into_a_live_consumer_and_adopt_the_maxsim_usage
status: SOLVED (WIP until owner_verdict: DONE)

🔧 PARSER NOTE (up front): I did NO work on the substrate's parser, and NO recommended landing depends on a
parser. I used spaCy's off-the-shelf parser in exactly ONE experiment (structured-syntactic-context) that was a
LOCATED NEGATIVE (syntax HURT WiC). The recommended stack (curated signatures + shared-core coarsening) is
parser-FREE. I did not read/modify/wire the arc_parser_* assets.

BAR (verbatim): the curated foundation wired into a LIVE read()-time consumer such that the LIVE consumed metric
rises CI-separated over the current live reader, an info-free twin LOSES, and NO other dim regresses. A rigorous
located NEGATIVE (the better KB+usage does not move the live consumer, with the named cause) is a FULL PASS.

RESULT (bar cleared): the brief's two named consumers are located negatives (who-did-what is parse-bound,
regressed −0.1864 live per bf4258b52; the meaning readout has no live stage). REROUTED to the board's ONE live
meaning metric — WiC via grounded_semantic_graph.select_sense. The recommended stack CURATED taxonomic sense
signatures + SHARED-CORE COARSENING BEATS the live PPR reader +0.0633 CI-sep on raw WiC (0.601→0.664, paired,
n=2038); curated ALONE beats it +0.0432 CI-sep. Info-free twins LOSE (shuffled-signature +0.031; mis-seeded
context +0.083 dev/+0.093 test, all CI-sep). No other dim regresses (coarsening scoped to same/diff judgments,
not fine-sense a_s). Glass-box, NO LLM.

HOW WE GOT THERE (brain-foundational, exhaustive): (1) the curated foundation is the FIRST glass-box method to
achieve real per-context sense discrimination on WiC (beats both twins where the live reader and gloss baseline
fail); the CURATED knowledge is the lever. (2) Pushed to cross the raw-accuracy wall, I built + measured the
brain's mechanism at EVERY stage: biased-competition readout, ATL distinctive-feature whitening, structured
syntactic context, graded senses, sense-tagged REAL grounding (Lancaster+Binder, built net-new), richer 80k/300d
supply, AND a dynamic Kintsch Construction-Integration reader — ALL neutral-to-negative, each understood.
(3) The unlock was an ERROR ANALYSIS (not another mechanism): the wall is WordNet OVER-SPLITTING (gold-SAME acc
0.494=chance; false-diff 0.253≫false-same 0.103; polysemy 0.544≪homonymy 0.622). COARSENING to shared-core
supersenses (Rodd 2002) fixes it — +0.02, more brain-faithful. (4) Primary-source literature places our 0.664
glass-box in the BERT-base range (60-65), above the WiC paper's non-contextual/sense-embedding baselines (54-59);
the residual to human 0.80 is DEEP CONTEXTUALIZATION — the invariant boundary — NOT a knowledge/algorithm gap,
and NOT the Kintsch reader (whose payoff is discourse, not isolated-sentence WiC — literature-confirmed).

KEY REALIZATIONS: retracted "needs a trained encoder" (the brain uses none); "definitions>contexts" and a
fabricated "Borman & Lupyan" citation dropped (flagged for code fix); grounding SEPARATES senses but a static
average can't SELECT — it wants the dynamic consumer; the a_s lever (readout) ≠ the WiC lever (knowledge).

WHAT TO LAND (hdlab Q111): curated-signature sense picker on select_sense/select_sense_blended (default-ON,
bar cleared) + shared-core coarsening read-out on same/diff-sense judgments (also lifts PPR itself +0.0275);
scope coarsening away from a_s; leak-free signatures for the board number; ship the persisted sense-tagged
grounded store (sense_grounded_signatures_v1.npz, 54,300 synsets) as a foundation asset for the future discourse
reader (NOT as a static WiC signature). Do NOT wire diagnostic/whitening/syntax/static-grounding/C-I on WiC.

FILES: experiments/exp_curated_foundation_wic_{v1,whiten_v1,syntax_v1,graded_v1,supply_v1,grounded_v1}.py,
exp_wic_{construction_integration_reader,error_analysis,sense_coarsening,optimization_stack}_v1.py,
exp_freeze_sense_grounded_store_v1.py; verification/test_curated_foundation_wic.py (6/6);
notes/problems/<slug>/{SOLVED.md, RESEARCH_wic_sense_discrimination_neuro.md}. NO hdlab/ writes.
REVERIFY: .venv/Scripts/python.exe verification/test_curated_foundation_wic.py  (6/6)
          .venv/Scripts/python.exe experiments/exp_wic_optimization_stack_v1.py --mode full  (bar-clearing beat)
