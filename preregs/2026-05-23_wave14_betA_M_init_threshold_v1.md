# Pre-reg: Bet A M_init threshold sweep (Strategy 10:16 v152 add-2)

Sweep M_init in {1024, 2048, 4096, 8192, 16384, 32768} at N=65536, 5 seeds, n_edits=100. Find KILL -> PASS threshold.

## Verdicts
- `BETA_M_INIT_BOUND_FOUND` — threshold exists where kept_acc transitions <0.5 -> >=0.85.
- `BETA_M_INIT_UNIFORM_PASS` — all M_init pass.
- `BETA_M_INIT_UNIFORM_KILL` — all M_init kill.
- `BETA_M_INIT_MIXED` — intermediate.
