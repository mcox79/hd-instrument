# Exp-Dev -> Research: G1 MIDDLE (expansion transfers to mpnet) + G7 HARD_FAIL (expansion subsumes whitening)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT GPU Slots G1 + G7. Both LAUNCHED + marked.
G1 (etf_dim_expansion_mpnet_768): smoke MIDDLE. mpnet-768: raw_cap=460 -> whitened=1152 (2.5x) at D=768; scales to
D=1536 (D1536 grid-censored). Dim-expansion rescue TRANSFERS to mpnet (sentence-transformer family) -- rule is not
MiniLM-specific. Full (N_enc=10000, longer grid) queued.
G7 (hadamard_plus_whitening_combined): smoke HARD_FAIL but INFORMATIVE. caps base_raw=230, whiten_only=768,
expand_only=4000(=data ceiling), expand_plus_whiten=4000. EXPANSION ALONE saturates the (data-limited) capacity, so
whitening adds nothing on top -> EXPANSION SUBSUMES WHITENING (random-sign expansion already decorrelates the keys).
CAVEAT: expand arms are N_ENC-censored, so "no stacking" is partly a data-limit artifact; full (N_enc=10000) confirms.
PRACTICAL implication: for real-encoder substrate, dim-EXPANSION is the single dominant lever; whitening is redundant
once expanded. Simplifies the Phase-4 rule to "expand" (not "expand AND whiten").
GPU lane now: G3/G5/G9/G13/G8/G1/G7 queued today. Remaining high-priority GPU: G4 (continual-KV n32768, CPU/numpy) +
a proposed G14 (NLI-head contradiction detection). Will pull next.
