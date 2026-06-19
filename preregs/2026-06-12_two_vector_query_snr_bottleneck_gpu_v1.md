# Pre-reg: two-vector index real bottleneck = query SNR (GPU)
Date 2026-06-12. Cell exp_two_vector_query_snr_bottleneck_gpu_v1.py. Lane overnight_queue (GPU). NO LLM.
Scaling-law cell showed atom count non-limiting (>=18x current, no degradation). Fix n=8000, N=1024, alpha=0.5; sweep
identity-query noise q (cos(cue,name)~1/sqrt(1+q^2)); find where identity_prec@1 breaks -- the REAL operating constraint.
HARD-PASS holds down to cos<=0.45 (generous). MIDDLE cos 0.45-0.70 (invest in query encoding not N). HARD-FAIL cos>=0.70 (brittle).
