# Pre-reg: Online W Robbins-Monro + SNAP (Strategy 10:03 v151 P3 — Gap B online learning rescue)

Sequential 50-write test with Robbins-Monro lr schedule (1/(1+t/10)) + SNAP saturation guard. Track retention min_acc across 50 sequential pattern insertions. N=8192.

## Verdicts
- `ONLINE_W_RESISTS_CF` — min_acc >= 0.95 (substrate resists catastrophic forgetting).
- `ONLINE_W_GRADUAL_FORGETTING` — 0.3 <= min_acc < 0.95.
- `ONLINE_W_CATASTROPHIC` — min_acc < 0.3.
