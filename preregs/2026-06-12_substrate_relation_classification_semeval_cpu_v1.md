# Pre-reg: substrate-classical relation classification (SemEval-2010 Task 8) -- NEW capability class
Date 2026-06-12 Cycle 50. Cell exp_substrate_relation_classification_semeval_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
Multiclass averaged perceptron over entity-context features (e1/e2 heads, between-words bag+bigrams, order) on SemEval-2010 Task 8
(8000/2717, 19 relation classes). Macro-F1. NEW capability CLASS: relation extraction (entity-pair-aware). HARD-PASS macro-F1>=0.65;
MIDDLE 0.50-0.65; HARD-FAIL <0.50. Smoke (600 train) = 0.39 (underfit). Same discriminative-weighting lever; no LLM.
