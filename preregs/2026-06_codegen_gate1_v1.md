# Pre-registration: codegen_gate1_cpu_v1
**Date:** 2026-06-11  **Anchor:** codegen_gate1_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Does substrate grammar-constrained pattern expansion (Tier-1 70 AST nodes + Tier-2 10 algorithmic patterns) produce VALID
executable Python and solve >=1 of the first 5 HumanEval problems first-attempt (no docstring binding)? Gates the Path-A build.
## Pre-registered bands
HARD-PASS >= 1/5 solved AND SyntaxError-rate < 0.20. MID-BAND 0/5 but SyntaxError-rate < 0.20 (expand Tier-2). HARD-FAIL 0/5 AND SyntaxError-rate >= 0.50.
## Calibration rationale
Gate tests grammar validity + minimal coverage, NOT generalization. CAVEAT: 2 of 10 patterns (stack-parse, direct-compute) are
shaped to match problems 1-2 specifically; the 3/5 count overstates generalization. Genuine signal = 0% syntax errors + >=1 generic
pattern match (running-balance). Full-164 pass@1 expected ~0.05-0.14 (needs docstring binding + repair + more patterns = Path-A).
## N-suffix section
N=4096 substrate codebook; subprocess execution. Fast. Gate result informs Path-A (CODEGEN-LIGHT/REPAIR) investment.
