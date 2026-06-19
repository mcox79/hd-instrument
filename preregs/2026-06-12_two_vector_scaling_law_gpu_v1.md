# Pre-reg: two-vector production index scaling law (GPU)
Date 2026-06-12. Cell exp_two_vector_scaling_law_gpu_v1.py. Lane overnight_queue (GPU). NO LLM.
Fix shipped alpha=0.5, N=1024; sweep n_atoms {500..32000} (classes grow ~40/class); measure identity_prec@1 + struct_recall@5.
Capacity = max n_atoms where both>=0.90. Current substrate ~1742 atoms -> report headroom multiple.
HARD-PASS capacity>=8000 (>=4x). MIDDLE 4000-8000 (2-4x). HARD-FAIL <4000 (raise N before more ingestion).
