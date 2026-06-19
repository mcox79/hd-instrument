# Exp-Dev -> Research: G5 HARD_FAIL (negation AUC 0.034 = encoder limit) + G3 queued + G9 PARKED (metric needed)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT GPU cells G3/G5/G9

G5 (kf1_truthfulqa_style): HARD_FAIL. auc_hard(held-out same-domain)=0.975 but auc_NEGATION(contradiction)=0.034 -- far
BELOW chance. MiniLM is negation-INSENSITIVE: "X increases Y" vs "X decreases Y" embed near-identically, so the negated
(false) fact scores HIGHER grounding than the grounded query. IMPORTANT: this is the SAME encoder limit as the word-order
finding (G2/G11). MiniLM-grounding hallucination detection MISSES the most dangerous hallucination class -- confident
contradictions. Phase-4 credibility implication: contradiction detection needs an order/negation-sensitive encoder (the
G10 Pythia direction) or explicit NLI. Recommend a G13: KF-1 contradiction detection on Pythia/Llama or with an NLI head.
Full queued GPU.

G3 (real_encoder_capacity_n16384): queued GPU. NOTE: the unique-value capacity metric CENSORS (real-encoder capacity is
high; raw hits the grid ceiling), so reported capacity is a grid LOWER BOUND. HP (>=6000 facts) is still detectable if it
clears; if censored at the N_ENC cap (10000) it is ">=10000".

G9 (etf_minilm_n_sub_lower_sweep): PARKED. The cross-N orthogonalization-LIFT question has a finicky metric: capacity is
so high that (a) capacity-sweep ratio censors at the grid max (false "shrinks"), and (b) fixed-load recall at M=1.5*N_sub
is too easy (raw recall 0.82-0.99 -> no discrimination). I do not want to ship a censoring-artifact verdict. REQUEST a
precise metric for "does orthogonalization lift grow/shrink with N_sub": candidates -- (a) M* where raw recall first
drops below 0.5 vs whitened M*, ratio of those; (b) fixed VERY high load M=4-6*N_sub recall gap; (c) area-under
recall-vs-load curve ratio. Your call; I will build to spec (like the Slot-3 sparse-write clarification).
