---
owner_verdict: DONE
---

SUBMISSION — upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior
status: SOLVED (WIP until owner_verdict: DONE). No hdlab/ written (Q111 — strategy lands the wire). Ledger malformed: 0.
reverify: .venv/Scripts/python.exe verification/test_joint_decode_register_robust.py   # 5/5 (located negative + dependency)
          .venv/Scripts/python.exe verification/test_whodidwhat_clean_frame.py          # 3/3 (the "wall" is a gold artifact)
          .venv/Scripts/python.exe verification/test_freetext_event_recall_deployed.py  # 3/3 (deployed win, free-text 19c)
(all core-capped; spaCy is offline-diagnostic only, never at inference)

RESULT — SOLVED via the CALIBRATED POSTERIOR (axis-1); the JOINT DECODE (axis-3, the brief's named mechanism) is a
rigorous LOCATED NEGATIVE (the bar's explicitly-sanctioned full pass). Glass-box, NO external LLM at inference.

1. JOINT DECODE (axis-3) DOES NOT beat the calibrated posterior on 19c — LOCATED NEGATIVE. CRF calibrated posterior
   alone separates 19c dropped verbs at AUROC 0.9409; adding force-VERB parse-coherence adds +0.0017 with a
   register-robust DELEXICALIZED parser (no-op at the operating point) and +0.0012 with the modern LEXICAL parser
   (which HURTS: 0.800). The delex coherence IS the better structural cue (AUROC 0.618 > 0.590 — the parser's
   register-brittleness is real) but IMMATERIAL: the calibrated emission posterior already captures the signal.
   Delexicalization is NOT the lever (19c is ~90% in-vocab → word-ORDER gap, not vocabulary; delex costs 8 UAS
   in-domain). Cause + number named; the joint-decode "deeper build" the parent proposed is retired.

2. THE DEPLOYABLE WIN (axis-1), MEASURED END-TO-END. The likelihood-trained CRF calibrated posterior is made GLASS-BOX
   and DEPENDENCY-FREE (pure-numpy linear-chain forward-backward reproducing sklearn_crfsuite.predict_marginals to
   max|dP(VERB)|=7.3e-7 → ships as a static json asset, NO crfsuite at runtime). DEPLOYMENT LOOP CLOSED on FREE-TEXT
   19c (raw LitBank, spaCy-oracle event gold, n_sents=5000, n_dropped=538), deployed detector at a PRECISION-GUARDED
   modern-fixed FP<=0.25 threshold applied unchanged to 19c:
     - recovery 0.898 @ 0.243 FP/sent, CI-SEPARATED over the info-free random-verbhood twin (Δ +0.715 CI[+0.670,+0.760],
       twin 0.182);
     - END-TO-END event recall 0.9382 → 0.9792 (+0.041; recovered 483/538).
   Parser-downstream consumer: precision-guarded verb recovery lifts 19c who-did-what REACHABILITY +0.309 CI[+0.18,+0.45]
   over base and +0.364 over the twin on the genuine-drop subpopulation (naive full-pop flooding collapses it — a
   detector-precision artifact, not a limit).

3. DEEP RESEARCH REFRAME (4 lanes + disk verification). The 19c who-did-what "0.44/0.60 ceiling" is largely a
   GOLD-CONTAMINATION artifact: the eval gold is ~84% non-core-argument (16% direct-object, 53% PP-oblique, 23% copular,
   8% pre-verbal, independently counted, reproduced n=3015). On the CLEAN direct-object gold: position 0.913,
   NP-head 0.980 — and NP-head BEATS the competent-reader proxy (spaCy 0.916), +0.064 CI[+0.035,+0.093]. So the earlier
   "spaCy beats us at the parse stage" was purely the contaminated ruler; on a correct ruler our reader is AT/ABOVE the
   competent reader. Composition/thematic-fit as a SELECTOR is refuted at power; the genuine residual is ~3% individuation
   (→ meaning hub P1). Audit-PINNED: category+structure+fit settle ONLINE during attachment (Lewis-Vasishth; MacDonald),
   so a post-hoc precision-weighted selector is a fenced dead-end (built, confirmed null).

FLOORS: perceptron max-margin 0.582 (19c drops); CRF-alone calibrated posterior 0.8727 (the joint decode ties/loses to
it); deployed free-text twin 0.182; who-did-what base reachability 0.4909 (drop subpop). CONTROLS (9): info-free twins on
every arm (all lose CI-sep); AUROC decomposition; lexical-vs-delex parser; spaCy offline oracle (fidelity gap, not
meaning ceiling); modern UAS retention; full-pop-flooding vs subpop-precision-guarded; glass-box CRF byte-faithfulness;
deployment-loop twin. Full CI half-widths + null p95 in SOLVED.md.

KEY REALIZATIONS: (a) when a calibrated posterior already separates a class at AUROC 0.94, a structural/joint cue is
redundant — decompose by AUROC BEFORE building the joint decoder. (b) The who-did-what "meaning wall" was a broken ruler;
counting the gold's true role composition dissolved it. (c) Thematic fit must compete ONLINE, not post-hoc — a post-hoc
gate structurally cannot separate override-when-conflicting from leave-alone. (d) A pickled dependency becomes a glass-box
static asset by writing out the weights and reimplementing the 20-line forward-backward math (7e-7 match). (e) Measure the
DEPLOYED path on the instrument where the value lives (free-text event recall), not the one that hides it (who-did-what
gold supplies the main verb).

FILES: experiments/exp_joint_decode_register_robust_tagger_parser_v1.py, exp_joint_decode_residual_decomposition_v1.py,
exp_joint_decode_downstream_bestshot_v1.py, exp_brain_comparison_signal_loss_ladder_v1.py,
exp_ideal_precision_weighted_whodidwhat_v1.py, exp_whodidwhat_clean_frame_ladder_v1.py,
exp_freetext_event_recall_deployed_v1.py, exp_crf_glassbox_marginals_v1.py; verification/{test_joint_decode_register_robust,
test_whodidwhat_clean_frame, test_freetext_event_recall_deployed}.py; data/exp_crf_glassbox_marginals_v1/
crf_tagger_glassbox.json (the deployable dependency-free asset). AUDIT UPDATE folded for BRAIN_FOUNDATIONAL_AUDIT §2b.

FOR STRATEGY (Q111 wire, default-off, witnessed): ship crf_tagger_glassbox.json → a frontend asset; add hdlab/crf_tagger.py
(GlassBoxCRF, pure-numpy vpost); swap predicate_detector's category cue from the perceptron max-margin to
logit(GlassBoxCRF P(VERB)) — tied on modern, the calibrated axis-1 cue on 19c, dependency-free. DO NOT land the joint
decode or the delex parser (measured null/immaterial). For the who-did-what side: flip the already-owner-DONE
np_head_reduce ON (clean-19c 0.918→0.980); the copular is-a schema + the online incremental parser are the filed
successors (the online parser is where this calibrated tagger is the keystone — do not compete, Q113).

DO NOT OVERCLAIM: the hdlab wire is PROPOSED, not landed (strategy's step). "past 0.806" is population-sensitive — the
load-bearing claim is RELATIVE (joint decode does not beat the calibrated posterior; the deployed calibrated cue beats
the perceptron floor + twin CI-sep). spaCy is an offline gold/reference only.
