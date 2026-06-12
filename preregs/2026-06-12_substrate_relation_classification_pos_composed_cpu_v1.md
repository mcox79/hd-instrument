# Pre-reg: capability composition (substrate POS tagger -> relation classification)
Date 2026-06-12 Cycle 50. Cell exp_substrate_relation_classification_pos_composed_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
The substrate composes its OWN primitives: POS tagger (structured perceptron, PTB-trained) tags SemEval -> POS features for the
RE classifier. Tests whether composition lifts RE past the lexical ceiling (0.672). HARD-PASS POS-composed>=0.69 AND lift>=+0.02;
MIDDLE 0.65-0.69 (neutral); HARD-FAIL <0.65. Substrate-product: explicit capability composition (LLMs do it implicitly).
