# Pre-reg: slot-filling few-shot curve (low-data fit generalization)
Date 2026-06-12 Cycle 50. Cell exp_substrate_atis_slot_filling_fewshot_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
Slot-F1 at train fractions {1,5,10,50,100}pct. Tests whether NER's low-data architectural fit (L-B: 63pct of full at 5pct data)
generalizes to large-tag-set slot-filling. HARD-PASS rel@5pct>=0.60; MIDDLE 0.45-0.60; HARD-FAIL <0.45 (large tag set limits low-data fit).
