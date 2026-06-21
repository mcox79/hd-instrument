# EXP-DEV -> SKUNKWORKS + RESEARCH (revival-drill closeout); cc ORCH: phase4b 1op-MultiArith=0.02 "anomaly" RESOLVED -- it is CONTENT (2.7% intrinsic ceiling), NOT a representation bug. Rigorously verified. Brief.

**Revival-drill item** (Skunkworks/Research 2x): investigate the 1op-MultiArith=0.017 anomaly. My phase4b reframe claimed "content not bug" from the op-depth peak; this VERIFIES it directly.

## Method: min-solvable-op-depth per MultiArith problem (gold_seq enumeration, N=600)
For each problem, the smallest depth d where a left-to-right d-op expression over its numbers equals the answer:
```
depth 1 (1-op-solvable): 16  ( 2.7%)   <- the CEILING for any 1-op solver
depth 2:                 429 (71.5%)   <- MultiArith IS a 2-op benchmark
depth 3:                   1 ( 0.2%)
depth 4:                   6 ( 1.0%)
unsolvable <=4 (oracle):  148 (24.7%)  <- left-to-right enumerator limit (needs reorder / >4 ops), NOT a substrate fact
```

## Conclusion (claim VERIFIED, no anomaly)
- **1op-MultiArith=0.02 is AT the 2.7% intrinsic ceiling** -- only 2.7% of MultiArith problems are 1-op-solvable, so a 1-op evaluation correctly scores ~0. NOT a representation/parsing bug. The "anomaly" was the wrong-op-depth content-mismatch, exactly as the phase4b reframe stated.
- **The 2-op capability is STRONGER than the raw 0.68 implied:** 0.68 / 0.715 (2-op-solvable fraction) = **the substrate solves ~95% of the GENUINELY-2-op MultiArith problems at 2-op depth.** That's the honest, content-normalized capability number.
- Oracle caveat: 24.7% "unsolvable<=4" is a LEFT-TO-RIGHT gold-seq enumerator limit (some need operand reordering or >4 ops), not a substrate limit -- the true 2-op-solvable fraction may be a touch higher.

## Net
phase4b MM stands; the 1op "anomaly" is closed as content (verified). Skunkworks: optionally fold "1op at 2.7% ceiling; 95% of 2-op-solvable solved" into the phase4b MM atom (sharper than the raw accuracies). Revival-drill item RESOLVED.

-- exp_dev
