# Pre-reg: two-vector STRUCTURAL channel real-substrate validation (CPU/local)
Date 2026-06-12. Cell exp_two_vector_structural_channel_real_substrate_cpu_v1.py. NO LLM. numpy + PartitionedStore, local-safe.
Validate algebra_hrr (STRUCTURAL channel) on 242 real covered atoms: does algebra_hrr cosine track algebra-dict (key,value)
Jaccard overlap? Primary metric Spearman among jac>0 pairs (all-pairs deflated by ~83pct zero-overlap ties).
HARD-PASS rho(jac>0)>=0.60 AND identical-dict collide (cos>=0.95) AND within-cat>between-cat. MIDDLE 0.40-0.60. HARD-FAIL <0.40.
