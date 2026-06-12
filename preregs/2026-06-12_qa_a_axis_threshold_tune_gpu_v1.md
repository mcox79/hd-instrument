# Pre-reg: A-axis adaptive bge-cosine-threshold route (keyword UNION {bge atoms > tau})
Date 2026-06-12 Cycle 50. Cell exp_qa_a_axis_threshold_tune_gpu_v1.py. Lane remote_cpu_queue (DESKTOP; bge). NO LLM frame.
The one unverified A lever: ADAPTIVE threshold (set size adapts) vs the FIXED top-k that failed (5 methods). Sweep tau; report
best A-F1 vs keyword 0.378. HARD-PASS best>=0.42 (+0.04). MIDDLE 0.38-0.42. HARD-FAIL <0.378 (A bge-ceiling-bound; only tuned RRF UNION lifts).
