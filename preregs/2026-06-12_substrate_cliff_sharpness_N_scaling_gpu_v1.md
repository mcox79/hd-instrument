# Pre-registration: free-prob cliff-sharpness N-scaling test (design-corrected)

**Date:** 2026-06-12 Cycle 50. Cell: exp_substrate_cliff_sharpness_N_scaling_gpu_v1.py. Lane: overnight_queue (GPU). NO LLM frame.

## Design correction (verify-before-asserting)
Probe found: at alpha=0.5 the cliff LOCATION scales ~N (N=512 cliff F~22; N=4096 no cliff at F=60). So spec'd fixed F<=30
cannot capture cliffs for N>=2048, and absolute d(cleanup)/dF scales ~1/N (transition widens in raw F), not N^{2/3}. The
N^{2/3} TW-edge prediction is in SCALED units. Cell uses N-adaptive F grids bracketing each cliff; reports sharpness both
absolute (d cleanup/dF) and SCALED (d cleanup/d(F/F_cliff), via transition-band linear fit); fits log-log slope vs N.

## Bands (on SCALED sharpness = TW-edge quantity)
- HARD-PASS: log-log slope in [0.55,0.80] (covers N^{2/3}=0.667).
- MIDDLE: [0.40,0.85] outside HP, or monotone-uncertain.
- HARD-FAIL: outside [0.40,0.85] or non-monotone (N^{2/3} sharpness prediction unsupported).
Absolute-sharpness + F_cliff(N) slopes reported alongside (F_cliff slope ~1 confirms cliff location scales with N).
N in {512,1024,2048,4096}, alpha=0.5, 3 seeds, 241-atom algebra-HRR codebook re-encoded per N. Definitional choice flagged to Research.
