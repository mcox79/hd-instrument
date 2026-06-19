# Pre-reg: Endpoint coset census (Strategy 10:16 v152 add-1)

Extends RM1M_FAIL_LOW. RM(1,16) via FWHT + 3 nonlinear anchor codewords (proxy for nonlinear Kerdock cosets at our BSC substrate). Assign 1000 endpoints to nearest coset. N=65536, 3 seeds.

## Verdicts
- `COSET_UNIFORM_NONLINEAR` — nonlinear cosets ~uniform, RM(1,16) < 5%.
- `COSET_BIASED_NONLINEAR` — one nonlinear coset > 50%.
- `COSET_RM_AVOIDED` — RM(1,16) < 5%, nonlinear mixed.
- `COSET_RM_PRESENT` — RM(1,16) >= 5% (substrate doesn't avoid linear).
