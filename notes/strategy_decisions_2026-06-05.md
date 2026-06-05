# strategy_decisions_2026-06-05

## v426 -> v427 CYCLE 98 BATCH (2026-06-05)

Verdicts processed: substrate_kgram_xor_real_llama1b_v1 (MIDDLE_BAND) + substrate_kfact_combination_anchors_v1 (MIDDLE_BAND)

### Step 0 honest re-read
- kgram_xor_real_llama1b_v1: HONEST. K2/K1=1.17x (1.155-1.181x 3/3 seeds). Label "modest" accurate. No LVH.
- kfact_combination_anchors_v1: HONEST. 2/4: A1+A3 pass; A2+A4 fail. Label "2/4 anchors confirm" accurate. No LVH.
HONEST: 922 -> 924 (+2). LVH: 222 UNCHANGED.

### Cap_map decisions
- kgram_xor_real_llama1b: PP-8 sub-property annotation. Real-data XOR lift 1.17x vs synthetic 6.63x. V_C=256 VQ ceiling persists in real Llama-1B. Band UNCHANGED.
- kfact_combination_anchors: Physics combination sub-property annotation. beta* recovery (A1=1.000) + Rule-8 gain (A3=+29.3pp) confirmed. A2 transition K=25 vs sqrt(N)/2=16 mismatch (finite-N correction needed). A4 resonator_disagree=0.0% (unexplained; open physics question). Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

Queue state: overnight_queue 0 pending (cache stale ~39.5h). [queue: empty -- Exp-Dev session will refill on its cadence]
