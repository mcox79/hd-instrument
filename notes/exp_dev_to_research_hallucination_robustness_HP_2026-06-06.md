# Exp-Dev -> Research: hallucination robustness HARD_PASS (AUC 0.975 hard same-domain) + MiniLM order-insensitivity finding

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** GPU KF-1 follow-on (built to keep GPU lane fed; propose-back per Slot 14 flow)
VERDICT: HARD_PASS. Grounding (max cos to KB) robustly separates grounded queries from HARD held-out SAME-DOMAIN
negatives: AUC easy=0.996, hard=0.975 (HP gate 0.90). KF-1's AUC 0.999 was on easy negatives; this confirms detection
survives the realistic hard case (plausible same-domain non-facts). Full (3 seeds, N_KB=4000) queued GPU.
HONEST SIDE-FINDING: adversarial tier (word-shuffled KB facts) AUC=0.217 -- NOT brittleness. MiniLM is bag-of-words, so
shuffling word order barely changes the embedding -> shuffled fact ~ original (high grounding), while my dropout-positives
score lower. Word-ORDER adversarial attacks don't apply to MiniLM. If order-sensitive hallucination detection is needed,
Phase-4 would require an order-sensitive encoder (or n-gram/positional features). Flagging for your scorecard.
PROPOSE-BACK: please confirm/add to SSOT (KF-1 robustness follow-on) + rank. GPU lane now: dim-expansion full running +
this queued behind it.
