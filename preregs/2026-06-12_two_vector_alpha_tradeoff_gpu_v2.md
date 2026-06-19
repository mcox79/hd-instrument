# Pre-reg: two-vector composite alpha tradeoff curve (GPU)
Date 2026-06-12. Cell exp_two_vector_alpha_tradeoff_gpu_v2.py. Lane overnight_queue (GPU). NO LLM.
Production composite_hrr = normalize(algebra_hrr + 0.5*name_vec) (PP-410). Sweep alpha; measure identity_prec@1 (collision-resistance)
vs struct_recall@5 normalized to alpha=0 ceiling. STRESS regime (N=1024 production, tight near-colliding classes struct_spread=0.06, noisy id queries q=0.6) so structure+identity genuinely compete. v1 saturated 1.0/all-alpha.
HARD-PASS alpha=0.5: id_prec>=0.90 AND struct_rec_rel>=0.80. MIDDLE one strong + other 0.70+. HARD-FAIL dominated.
