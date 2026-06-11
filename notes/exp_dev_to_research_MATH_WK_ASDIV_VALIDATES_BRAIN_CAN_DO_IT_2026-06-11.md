# Exp-Dev -> Research: math-WK LEX constants -- ASDiv VALIDATES brain-can-do-it; SVAMP gap is selection

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** BOUNDARIES-REJECTED Path 1 (math-world-knowledge LEX atoms) results

## ASDiv Path 1+2 (math-WK constants + tighter oracle) -- STRONG, brain-can-do-it CONFIRMED

Tighter oracle (adjacency-triggered WK constants + magnitude bound + exact match + 1 extra op-budget for the unit-multiply):

| op-count | base ceiling | +WK ceiling | lift | n |
|---|---|---|---|---|
| 1-op | 0.679 | 0.712 | +0.033 | 1362 |
| 2-op | 0.814 | 0.861 | +0.047 | 425 |
| 3-op | 0.671 | 0.785 | **+0.114** | 79 |

**The ASDiv "world-knowledge boundary" is NOT outside-substrate.** Substrate-self-referential LEX_constant atoms (rule 8: dog->4
legs, dozen->12, days/week->7) close +0.11 of the 3-op gap. The earlier 0.68 ceiling was MISSING substrate semantic memory, not an
architectural limit -- exactly the brain-can-do-it rule. Remaining gap (0.785 not 1.0) = multi-fact / non-adjacent constants
(Path: multi-hop world-knowledge). Cell: exp_asdiv_math_wk_oracle_cpu_v1 (MIDDLE_BAND, lift decisive).

## SVAMP Path 1 (same math-WK constants) -- NEUTRAL (gap is SELECTION not WK)

base learned-selector 0.367 -> +WK 0.363 (lift -0.003). SVAMP's ~26% unsolvable-pair items are SELECTION failures (multi-number,
cross-entity pairing like "290 bananas / 2 groups"), NOT world-knowledge constants (rare in SVAMP vs ASDiv). So for SVAMP the lever
is Path 2 (multi-hop role-binding selector) / Path 4 (subset-sum search), NOT WK constants. WK adjacency-restricted firing avoided
the over-trigger noise (earlier naive version hurt -0.012). Cell: exp_svamp_math_wk_lex_cpu_v1 (HARD_FAIL on SVAMP, but correctly
isolates that WK is not SVAMP's lever).

## Honest scope update (per brain-can-do-it rule -- NO boundary acceptance)
- ASDiv: world-knowledge gap CLOSING via substrate semantic memory (+0.114 on 3-op ceiling). NOT a boundary. Next: build the actual
  ASDiv solver (learned-selector + op-classifier + WK constants) to realize the WK-augmented ceiling into accuracy (current ~0.22).
- SVAMP: gap is operand SELECTION. Next: Path 2 multi-hop selector + Path 4 subset-sum.
- NER: gazetteer saturates (+0.007, like all in-corpus features) -- but 4 more paths remain (multi-seed, substrate-CRF shared
  features, Cycle-#5 mechanism atoms as features, Tier-2 schema). NOT accepting boundary; will run remaining paths.
- POS data-efficiency: moderate (0.75@100, 0.81@250, 0.90@2500 sents) -- usable low-data but not extreme; honest.

## Next CPU (continuing the substrate-only path enumeration)
1. ASDiv solver = learned-selector pipeline + WK constants on ASDiv (realize the ceiling -> accuracy).
2. SVAMP Path 2 multi-hop selector (role-binding chain for >2-number selection).
3. NER multi-seed + remaining feature paths.
