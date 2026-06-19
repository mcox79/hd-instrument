# Pre-reg: two-vector trilogy REAL-substrate validation (CPU/local)
Date 2026-06-12. Cell exp_two_vector_real_substrate_identity_validation_cpu_v1.py. NO LLM. numpy-only (no torch/bge), local-safe.
Validate synthetic trilogy on real PartitionedStore atoms (data/substrate_index). Atom-keyed composite identity: clean-cue
id_prec@1; self/distractor cos margin; degraded-cue break cos vs synthetic ~0.45.
HARD-PASS clean id_prec>=0.95 AND break cos<=0.55. MIDDLE clean>=0.90 OR break<=0.65. HARD-FAIL clean<0.90.
