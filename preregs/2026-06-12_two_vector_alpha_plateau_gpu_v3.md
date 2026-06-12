# Pre-reg: two-vector composite alpha PLATEAU map (GPU)
Date 2026-06-12. Cell exp_two_vector_alpha_plateau_gpu_v3.py. Lane overnight_queue (GPU). NO LLM.
v1/v2 found NO tradeoff (both objectives saturate alpha 0.25-2.0) -- high-D near-orthogonality of name_vec vs algebra_hrr means
superposition does not interfere. v3 MAPS the robust plateau: fine low-alpha [0.05..0.25] (identity onset / lower edge) +
extreme high-alpha [5..100] (does structure ever break / upper edge). Robust band = alphas with id_prec>=0.90 AND struct_rec_rel>=0.80.
HARD-PASS: wide plateau (>=4 alphas) with shipped 0.5 central. MIDDLE: central but narrow. HARD-FAIL: 0.5 outside band.
