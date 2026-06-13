# Pre-reg: F4 free-cumulant saturation horizon kappa_3..kappa_8 (CPU, remote)
Date 2026-06-13. Cell exp_f4_kappa_n_saturation_cpu_v1.py. Lane remote_cpu_queue (desktop, no laptop heat). NO LLM. numpy only.
Free cumulants via M(z)=1+sum kappa_j z^j M(z)^j; round-trip self-test (free-Poisson kappa_n=alpha). Bootstrap SNR per order; n_sat.
Pre-reg bands (research): HP SNR_3>=5, SNR_4>=3, SNR_5 in[1.5,3], SNR_6<1.5, n_sat stable. HF SNR_6>=3 or SNR_4<2 or n_sat range>=2.
CAVEAT (exp_dev): SNR measures MEASURABILITY not INDEPENDENCE (free-Poisson kappa_n all = alpha); result is alpha-sensitive. Report flags this.
