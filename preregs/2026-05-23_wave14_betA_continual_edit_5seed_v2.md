# Pre-reg: Bet A continual edit 5-seed v2 (M_init=8192) — Strategy 09:35 P5 memory-fixed

v1 hit CUDA OOM at M_init=N=65536. v2 uses M_init=8192 (1/8 N, 8:1 headroom per cycle 98 theory). n_edits=100, 5 seeds.

## Verdicts
- `BETA_5SEED_PASS` — edit_acc mean >= 0.95 AND kept_acc mean >= 0.95 AND sd < 0.05.
- `BETA_5SEED_PARTIAL` — mean >= 0.5.
- `BETA_5SEED_KILLED` — mean < 0.5.
