# Pre-reg: RE few-shot curve (classification low-data fit contrast)
Date 2026-06-12. Cell exp_substrate_relation_classification_fewshot_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM.
SemEval RE macro-F1 at train fractions {1,5,10,50,100}pct. Contrast: sequence-labeling NER 63%/slot 87% of full at 5%.
HARD-PASS rel@5pct>=0.60; MIDDLE 0.40-0.60; HARD-FAIL <0.40 (classification needs more data per class than sequence labeling).
