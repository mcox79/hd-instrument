# Prereg: nl_slot_filling_atis_bootstrap_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Direction 1 (firmed Tier-B->Tier-A promotion).
Slot-filler is count-deterministic (no train-seed variance); BOOTSTRAP-resample test sentences (B=1000) for a sampling-error CI on
micro slot-F1 + intent acc. Same substrate mechanism (emission + slot-bigram transition + Viterbi; intent count-NB). Point slot-F1 0.871.
ATIS cached offline. HARD-PASS slot-F1 2.5th-pct >= 0.85 AND intent >= 0.80 (Tier-A sampling-robust). MIDDLE point 0.65-0.85 or lower-CI<0.85. HARD-FAIL <0.50.
