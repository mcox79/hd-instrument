# Pre-registration: code2_adversarial_cpu_v1
**Date:** 2026-06-11  **Anchor:** code2_adversarial_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does code2 template-conditional bug detection (F1=0.938 Tier C) hold under HARDER adversarial bug families: out-of-grammar,
cross-template (op valid for another template's slot), and double-swap (2 slots)?
## Pre-registered bands
HARD-PASS worst-case F1 >= 0.78 across all 3 bug families. MIDDLE worst-case 0.65-0.78. HARD-FAIL worst-case < 0.65.
## Calibration rationale
Cross-template bugs are closer to grammar (harder); double-swap stresses the min-slot detector. Worst-case >=0.78 confirms
the Tier-C result is robust, not brittle to the simple out-of-grammar bug it was tuned on.
## N-suffix section
N=8192; numpy; 3 adversarial modes x 90 trials. Fast.
