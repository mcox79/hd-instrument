# Pre-reg: F4 deviation-SNR (Research re-spec Cell A) -- CPU remote
Date 2026-06-13. Cell exp_f4_kappa_n_deviation_snr_cpu_v1.py. Lane remote_cpu_queue. NO LLM.
DEVIATION-SNR_k=|kappa_k-alpha|/bootstrap_std (independent signal beyond alpha). n_sat=first k>=3 with dev<=1.5.
HARD-PASS n_sat in {3,4,5} per seed AND max dev-SNR k>=6 < 3 (8d pillar stands). HARD-FAIL dev-SNR>=3 sustained beyond 5. MIDDLE k6 in[1.5,3).
