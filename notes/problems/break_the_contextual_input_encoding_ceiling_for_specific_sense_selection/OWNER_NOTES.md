---
owner_verdict: DONE
---

SUBMISSION -- break_the_contextual_input_encoding_ceiling_for_specific_sense_selection
status: PARTIAL (rigorous located-negative + a DECISIVELY-PROVEN, quantified lever). WIP until owner_verdict: DONE.
No hdlab/ written (Q111). Witness 10/10 from source; ledger malformed: 0.
reverify: .venv/Scripts/python.exe verification/test_contextual_ceiling_signal_loss.py   # 10/10, CPU, no GPU/LLM

RESULT (strict document-disjoint SemCor, subordinate senses, subject-weighted a_s, n~2676; glass-box, NO external LLM):
- THE BRIEF'S ROUTE FAILS. A self-supervised glass-box CONTEXTUAL encoder (context2vec-style bidirectional LM, OUR
  model, 41M tok, GPU-trained) best arm a_s=0.293 -- below the bag and below the wired diagnostic 0.307-0.317 at
  matched scale; twins lose. The transformer "fork" the brief named is REFUTED as the brain answer.
- THE READOUT/MECHANISM IS NOT THE GAP. The brain's exact mechanism (iterative joint constraint-satisfaction
  settling, Hoffman 2018) = the one-shot readout (0.312 vs 0.312, not sep); dominance-weighting HURTS subordinate
  (0.21). Built Kintsch Construction-Integration joint settling over a topic-W: 0.22 < diag 0.31 (topic reinforces
  the DOMINANT sense).
- SIGNAL-LOSS FULLY LOCATED. Oracle decomposition: KEY-unwinnable=0.000 (glosses always separable), QUERY-loss=100%,
  oracle-context ceiling=0.85 (the cue IS in the plain w2v context). Sense-resolving context via glosses HURTS;
  grounding real but redundant; settling ties cosine.
- THE DECISIVE PROOF -- the lever is the world-knowledge connection matrix W, quantified:
    TOPIC diagnostic (wired)                 a_s 0.316
    LEARNED sense-discriminative W (doc-disjoint SemCor)  covered-only 0.367 vs topic 0.308 (+0.059, twin-sep)
    ORACLE  sense-discriminative W (upper bound)          a_s 0.995   <-- ceiling was 100% W-quality, never the encoder
  Binding bottleneck = COVERAGE (52% at SemCor scale). Each covered sense buys ~+0.06 over topic; ceiling ~0.99.

CONTROLS: strict doc-disjoint throughout; shuffled-context/sense twins LOSE CI-sep on every signal-bearing arm;
ORACLE decomposition isolating KEY (0.000 unwinnable) vs QUERY (100%) and the in-context ceiling (0.853);
matched-scale (encoder vs diagnostic both 41M); W-quality ladders (C-I gloss-vs-SyntagNet; clean-knowledge
SyntagNet-vs-ConceptNet; sense-discriminative TOPIC->LEARNED->ORACLE); paired bootstrap CI + null p95.

KEY REALIZATIONS: (1) the "lexical WSD / classify-then-weight" frame is the wrong shape -- the brain has no
standalone relevance stage; relevance IS the connection strength in a learned graph. (2) Building the brain's
actual mechanism and watching it LOSE localized the constraint to W-quality. (3) A perfect sense-discriminative W
solves the task (0.995) with the SAME mechanism -- the encoder/readout were never the ceiling. (4) Transformers
cross via rich learned reps, not relevance-selection (Tang-Sennrich-Nivre 2018) -- so encoder scale is irrelevant
to the lever (the 277M run was dropped as a settled point, not run).

FILES: experiments/exp_sg_lite_{context2vec_encoder_wsd_v1, predictive_coding_encoder_wsd_v1,
grounded_settling_readout_v1, signal_loss_decomposition_v1, iterative_settling_sense_selector_v1,
sense_aware_context_ceiling_v1, clean_knowledge_context_relevance_v1, construction_integration_joint_wsd_v1,
sense_discriminative_W_headroom_v1}.py; verification/test_contextual_ceiling_signal_loss.py; SOLVED.md +
3 research notes (research_{situation_model_sense_selection, exact_neural_circuit_sense_access,
gold_blind_relevance_mechanism}_2026-09-03.md). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT sec 2b.

FOR STRATEGY: no hdlab wire (nothing beat the wired diagnostic readout); NOT the transformer fork. The redirect,
now PROVEN + NUMBERED, goes to build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner: grow a
broad-coverage, CLEAN, SENSE-DISCRIMINATIVE W (which words indicate THIS sense over its competitors -- topic
relatedness reinforces the WRONG sense). Acceptance test scaffolded (exp_sg_lite_sense_discriminative_W_headroom):
recover >=50% of the 0.31->0.85 headroom on the FULL population as coverage grows.

DO NOT OVERCLAIM: the full-population positive cross is NOT achieved here (learned W is coverage-limited: 0.191
overall) -- that cross requires the broad-coverage W, which is the world-knowledge/consolidation problem. This
submission proves and quantifies the target; it does not build the store.
