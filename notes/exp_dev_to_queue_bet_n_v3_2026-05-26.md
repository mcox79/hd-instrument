# exp_dev -> queue routing note: wave14e_bet_n_wta_v3

**Filed:** 2026-05-26 by exp_dev
**Trigger:** orchestrator strategic intent -- push Bet N from STRONG_PARTIAL toward DEMONSTRATED

## Shipment record

```
queue=overnight_queue name=wave14e_bet_n_wta_v3 script=experiments/exp_wave14e_bet_n_wta_v3.py prereg=prereqs/2026-05-26_wave14e_bet_n_wta_v3.md timeout=7200
```

## Context

Bet N v2 returned BET_N_PARTIAL_TIER2 (STRONG_PARTIAL Tier-2): P1=HARD_PASS util=1.000,
P2=HARD_PASS ratio_M2000=34.698. P3=MIDDLE: pca_cos_dist=0.6551 (ABOVE threshold) but
matched_gap=0.0000 (NLP-generic: EN atoms work as well as PY atoms on PY eval).

Cap_map v211 states: "Tier-1 promotion path still requires P3 corpus-specialization at HARDER tasks."

## What v3 changes

1. P3 ROOT CAUSE FIX: cleanup_acc on random Phi pairs cannot show corpus-specialization (same
   associative-memory capacity regardless of corpus). v3 encodes ACTUAL corpus n-gram bigram pairs
   through WTA atoms as compositional basis, then cross-tests retrieval. This is the Cao 2023
   operational test.

2. Larger K=256 (was 128 in v2): cap_map v211 recommendation for better specialization.

3. Extended M-sweep {100,500,1000,2000,4000,8000}: answers v210 open question on capacity envelope.

4. More epochs (n_epochs=8 vs 5): allows K=256 codebook to converge.

## Smoke results

- Smoke PASS (8/8 selftests + valid metrics.json)
- P3 at smoke (N=512 K=32): gap=-0.048 (scale effect: EN atoms dominate at small K)
- P3 at 4x smoke (N=1024 K=64): gap=+0.050 (borderline MIDDLE/HARD_PASS, trend positive)
- Suspicious-result gate CLEAR: P2 per-corpus spread=0.39, P3 gaps non-zero non-identical
- Walk-back: P2 effect borderline at smoke but v2 full run showed 34.7x -- robust at N=4096

## Remote verify

VERIFIED: wave14e_bet_n_wta_v3 present in remote overnight_queue (queue depth +1, 5 pending total)

## Expected outcome

- P3 HARD_PASS at N=4096 K=256: BET_N_TIER1_PROMOTION (Tier-1 cap_map promotion)
- P3 MIDDLE: NLP-genericity as substrate design property; STRONG_PARTIAL maintained
- P3 HARD_FAIL: corpus-specificity absent at these parameters; rescues: larger corpus, word-level encoding, narrower domain pairs
