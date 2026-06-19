# Prereg: transfer_p5_factrecall_mwp_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research APPROVED E5 / Drill 2 Transfer-P5 framework discriminator.
Test PP-225 FHRR fact-recall mechanism [value=cleanup(unbind(memory, bind(subject,relation)))] transfer to KB-fact-from-MWP-text
extraction WITHOUT a parser. Genuine FHRR (unit phasors dim=1024, bind/unbind/bundle/cleanup). Two attempts: adjacent-pair memory +
cartesian best-shot (category knowledge, no association). Headline = best of the two vs regex heuristic baseline.
Drill 2 predicts HARD-FAIL (P_transfer=0.012; C1 homology 0.20 structural mismatch).
HARD-PASS F1>=0.50 (REFUTES framework -> discovery). MIDDLE 0.30-0.50. HARD-FAIL <0.30 (framework validated).
