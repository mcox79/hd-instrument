# Prereg: asdiv_pp375_port_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Path 8 (HIGHEST PRIORITY) -- port PP-375 multistep mechanism to ASDiv.
PP-375 (MultiArith Tier-A 0.753): op-SEQUENCE prediction (4/16 classes) over TEXT-ORDER numbers + answer-consistency weak labels;
sidesteps operand selection. Two variants: faithful text-order (first-2/3) vs +operand-search. Substrate-self-improvement
(existing mechanism -> new capability ASDiv).
HARD-PASS ASDiv-1op>=0.45. MIDDLE 0.40-0.45. HARD-FAIL<0.40.
Smoke (200): text-order 1op=0.4416, +search 1op=0.4286 -- transfers, beats multihop 0.376! text-order > search (canonical selection
better than search for 1-op). Full decisive.
