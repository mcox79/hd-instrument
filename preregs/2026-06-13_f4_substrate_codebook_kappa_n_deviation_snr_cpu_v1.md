# Pre-reg: F4 Cell B real-codebook deviation-SNR (Research re-spec, load-bearing) -- CPU remote
Date 2026-06-13. Cell exp_f4_substrate_codebook_kappa_n_deviation_snr_cpu_v1.py. Lane remote_cpu_queue. NO LLM.
G=A^T A/N, A=substrate composite_hrr codebook; deviation-SNR_k=|kappa_k-alpha_est|/std, alpha_est=M/N.
HARD-PASS n_sat in {3,4,5} AND max dev-SNR k>=6 <1.5 (free-Poisson, pillar complete). MIDDLE 1.5-3 (clustered structure). HARD-FAIL >=3 beyond 5.
