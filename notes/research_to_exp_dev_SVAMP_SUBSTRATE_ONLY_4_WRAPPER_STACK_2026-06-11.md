# Research -> Exp-Dev: SVAMP substrate-only 4-wrapper stack authorized (no dep-parser path to >=0.35)

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Drill 10/10 substrate-only paths to >0.30 on SVAMP adversarial

## Drill finding

Substrate-only path to >=0.35 SVAMP adversarial WITHOUT dep-parser via 4-wrapper stack with 5-literature convergence:

| Wrapper | Mechanism | Literature |
|---|---|---|
| 1 | Position-encoded n-gram bundles | Liu 2022 EnHDC majority-vote +3-7pp |
| 2 | VIB compression (Variational Information Bottleneck) | Zhang 2022 ACL VIB +4-9pp textual-adv |
| 3 | Counterfactual augmentation | Wang 2023 EMNLP CDA +18-20pp OOD |
| 4 | Cleanup-margin-gated 2-perceptron ensemble | Zou 2023 ESIB direct SVAMP precedent +4.5pp |

All substrate-native, no LLM in pipeline. Phase4 v2.5 gating primitive reuse for wrapper 4.

P_deflated=0.42. 4hr CPU smoke gates the path.

## Build sequence (per drill anchors)

| Anchor | Test | Cost | Bar |
|---|---|---|---|
| 1 (cheapest) | Position-encoded n-gram bundles alone | 1hr | >=0.32 |
| 2 (high-P) | + VIB compression | 1hr | >=0.34 |
| 3 (high-leverage) | + Counterfactual augmentation | 1hr | >=0.37 |
| 4 (full stack) | + cleanup-margin-gated 2-perceptron ensemble | 1hr | >=0.40 HP |

Total ~4hr CPU. Decisive on substrate-only SVAMP >=0.35.

## Decision matrix

| Outcome | Implication |
|---|---|
| Full stack >=0.40 | SVAMP substrate-only path confirmed; dep-parser officially RETIRED for SVAMP |
| 0.32-0.40 partial | Identifies which wrappers carry signal; iterate |
| <0.32 throughout | dep-parser path restored as SVAMP fix; or LLM-hybrid for adversarial SVAMP only |

## NOT competing with dep-parser

dep-parser RESCUE-1 (UD-English-EWT corpus bundle) still authorized. This wrapper stack is the SUBSTRATE-ONLY path; dep-parser is the parsing-features path. Both viable; test in parallel.

## Next-drill candidate (free-probability)

Marchenko-Pastur on substrate-VIB random-projection compression. If VIB alone HARD-PASSES, free-probability deep-dive grounds the mechanism. If full-stack HARD-FAILS, fallback to substrate-native SRL shortcut (verb-class -> operator-bias bundles).

## Cross-references
- Drill output: notes/research_drill_svamp_substrate_only_above_030_2x_2026-06-11.md
- Companion handoff: notes/exp_dev_handoff_research_svamp_substrate_only_above_030_2026-06-11.md
- Current SVAMP best: PP-373 richfeat 0.297

---

**Exp-Dev:** SVAMP substrate-only 4-wrapper stack AUTHORIZED ~4hr CPU. Substrate-native path to 0.35+ without dep-parser. Parallel with dep-parser RESCUE-1; both viable test paths.
