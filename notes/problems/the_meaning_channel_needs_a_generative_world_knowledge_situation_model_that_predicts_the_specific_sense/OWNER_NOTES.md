---
owner_verdict: DONE
---

SUBMISSION -- the_meaning_channel_needs_a_generative_world_knowledge_situation_model_that_predicts_the_specific_sense
status: PARTIAL (advancing the parent). SUBMITTING NOW. WIP until owner_verdict: DONE. NO hdlab/ written (Q111). Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_generative_situation_sense_selector.py   # 8/8 FROM SOURCE

>> SUBMITTING NOW WITH ONE PUSH-RUN STILL IN FLIGHT (owner decision). The submission stands COMPLETE on the confirmed,
   witnessed results (A)+(B) below. A self-supervised SG-lite SCALE run (exp_sg_lite_scale_v1, ~277M tokens, GPU) is STILL
   RUNNING (word2vec phase, ~1-2h) as a max-push toward the glass-box band; its a_s (~0.33-0.39 expected, recipe drill) is a
   FOLLOW-UP that will update items A/#1 -> data/exp_sg_lite_scale_v1/metrics.json. NOT a blocker; if it fails to land the
   submission is complete without it. The scale gain is a diminishing-returns refinement, not a load-bearing claim.

TWO RESULTS, brain-foundational, CI-separated, held-out (SemCor 30 files, n=17,317; even/odd doc-disjoint; MFS floor 0.6831):

A) BAR 2 (parent's NET-GAIN see-saw) -- BROKEN, robustly, by the brain's DECISION RULE (not the generative source).
   Precision-weighted ADDITIVE rule (reordered access: dominant NEVER suppressed, context only ADDS; non-margin reliability;
   NO hard flip) nets +0.0116 over MFS [0.006,0.017] CI-sep, dominant preserved 0.949 (no see-saw), shuffled-situation twin
   LOSES CI-sep. Parent's best was NET -0.0013 CI-sep BELOW. The wall was the DECISION RULE, not a_s.

B) BAR 1 (the a_s "which specific rare sense" lever) -- the "0.4 ceiling / needs-an-LLM" claim is DEMOLISHED (I retract it).
   That ~0.4 is a nearest-centroid READOUT artifact (MFS-biased), NOT the brain's mechanism. Built the ideal prototype -- a
   self-supervised INCREMENTAL GENERATIVE sense-gestalt (Sentence-Gestalt/predictive-coding), GPU-trained -- with the brain's
   glass-box readout: RECONSTRUCTION-MATCH (score each sense by how well it reconstructs the gestalt's top-down predicted
   meaning mu vs a grounded per-sense signature) + predictive-coding SETTLING. STRICT doc-disjoint: a_s 0.280 BEATS the
   nearest-centroid readout 0.220 AND the overfit supervised NB 0.198, and GENERALIZES; net vs MFS +0.0128..+0.0154 CI-sep,
   twin loses. Corroboration: BEM lifts rare senses 37->52.6 at FIXED model size via reconstruction-match; UKB+SyntagNet
   (pure glass-box graph, no NN) rivals supervised WSD. Honest: 0.280 < glass-box band top (~0.4-0.53); readout MAXED on the
   41M gestalt (IDF pooling + settling NEUTRAL -> cap is gestalt/embedding quality) -> the SCALE run (in flight) pushes this.

GENERATIVE SOURCE (bar 1 nuance): the STATIC world-knowledge signal is a real-but-modest net contributor (twin loses CI-sep).
A SemCor-supervised LEARNED distributional predictor OVERFITS -- leave-one-DOC-out a_s 0.43/net +0.052 but a STRICT
disjoint-document foundation collapses it to 0.198/-0.038 (scramble confirms) -- the decisive rigor catch (base rate: 30
vetted HARD_PASS, 1 upheld). The GENERALIZING a_s lever is the incremental-generative gestalt + reconstruction-match (B).

KEY REALIZATIONS: (1) the wall was the DECISION RULE, not a_s (hard-flip argmax see-saws c_d~1.0; the brain's additive,
facilitatory-only, non-margin-precision rule converts the existing signal into net gain). (2) A small net over near-oracle
MFS IS the brain's regime (human all-words ~0.72 vs MFS ~0.66). (3) "needs an LLM" was WRONG -- the brain does inference-time
generative reconstruction glass-box (predictive-coding settling; Nour-Eddine-Kuperberg's N400 model is a ~13k-unit network,
not an LLM).

CONTROLS (witness 8/8 FROM SOURCE): shuffled-situation twin loses CI-sep; STRICT disjoint-doc foundation (-0.038, leak catch);
scramble-label collapse (+0.0008); decision-rule contrast (additive +0.0100 vs parent gated hard-flip -0.0013); additive-rule
sanity; reconstruction-match strict doc-disjoint (0.280 > centroid 0.220 > NB 0.198), twin loses.

FOR STRATEGY -- HOW TO OPTIMIZE (ordered; full map in SOLVED.md):
 0. [BLOCKED ON YOU] dispatch/monitor the SG-lite SCALE run (running now; if it crashes, re-dispatch: --allow-duplicate +
    finish ARC 1.48GB ship + install gensim on the GPU box if missing, as nltk-semcor was). Fold its a_s into item A/#1.
 1. LAND the proven net-gain read path (A) into hdlab/semantic_control (default-off, witnessed, Q111): additive
    reordered-access + non-margin precision. OFF byte-identical; ON nets over MFS CI-sep, twin loses.
 2. after scale: ROLE-FILLER prediction TARGET (true Sentence-Gestalt) -- biggest fidelity lever (needs SRL/FrameNet signal).
 3. richer glass-box gloss embedding for e_s (reconstruction-match's cap; IDF pooling was neutral).
 4. grounded input spoke + LIFG biased-competition + divisive prediction-error units; Raganato-ALL external validity.

FILES: experiments/exp_generative_situation_sense_selector_v1.py,_v2.py, exp_incremental_generative_sense_predictor_v1.py,
exp_sg_lite_sense_gestalt_v1.py, exp_sg_lite_generative_readout_v1.py, exp_sg_lite_scale_v1.py;
verification/test_generative_situation_sense_selector.py (8/8); notes/problems/<slug>/{SOLVED.md, DESIGN_brain_foundational.md,
REMOTE_RUN_REQUEST_*.md}. AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT sec 2b + 3 hygiene corrections.

DO NOT OVERCLAIM: net gain is small (+0.0116) -- the brain's regime over near-oracle MFS, not a big WSD win; the
learned-predictor LOO-doc numbers are corpus-overfit (use the strict -0.038); a_s 0.280 beats the readout ceiling + NB +
generalizes but is not human-level (~0.8) -- residual is representation/scale, glass-box-closable, NOT an LLM.
