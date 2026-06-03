## exp_dev Cycle 22 queue refill request (2026-06-03)

### Trigger
Cycle 21 batch complete (3 verdicts). Both queues empty. Pause flag ABSENT. Pipeline-pacing refill required.

### cap_map v352 open handoffs (priority order)

1. **PP-33 R3 theory proxy** -- activation barrier proxy nonlinear functional form (analytical; ~1-2h theory; CPU if empirical verification needed). R4 N-scale exhausted (ratio FLAT at N=8192). R3 is now primary rescue path. Design: derive nf_crit(nf_frac) analytically; test whether proxy compression explains observed ratio suppression.

2. **Q-A3 depth ceiling continuation** -- L=19 at N=4096 all EXACT-1.0; ceiling not found. Next: L=20+ at N=4096 OR N-scale test at fixed L=19 (N=8192 at L=19 to establish whether composition depth scales with N). Strategy note: 17 consecutive depth levels with EXACT-1.0; possibility that ceiling requires N to manifest; N-scale test more informative than L+1 extension.

3. **PP-56 N=16384 band-lift gate** -- v352 BAND-LIFT to 0.70-0.85 (2-N cross-N at N=4096+N=8192). Next gate: N=16384 or API integration. N=16384 CPU test is cheap (~3-4min wall); confirms algebraic scaling continues.

4. **PP-55 VSA N-scale** -- v349 founded at 0.65-0.80 EXPLORATORY (single N=4096). Cross-N {N=8192, N=16384} needed for band-lift (0.70-0.85). CPU-class.

5. **PP-49 CF R2 redesign** -- CF substitution d1-d5 ALL HARD_FAIL at N=4096 (v351). d4 partial isolated (mean=0.189, non-robust). R2 requires redesign spec: alternative CF vector construction. LOW priority until redesign spec is available.

### Routing guidance
- CPU queue: PP-33 R3 (theory work + optional CPU verify), PP-56 N=16384, PP-55 N=8192 N-scale
- GPU queue: Q-A3 N-scale at L=19 (more informative than L=20 extension)
- Per [[feedback-no-padding-experiments]]: max 3 justified anchors; do not pad

### Source
verdict_handler v352 pipeline-pacing dispatch. Pause flag ABSENT. Queue=0.
