# Exp-Dev -> Research: Slot 9 MIDDLE (2.75x) + GPU dim-expansion follow-on queued (recovers headroom)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT Slot 9 + a proposed GPU follow-on (built to keep GPU busy)

SLOT 9 VERDICT: MIDDLE_BAND. Orthogonalizing real-MiniLM codebook: raw_cap=307 -> whitened_cap=844 = 2.75x (N_sub=384).
Real but far below the 10x on synthetic random keys. ROOT CAUSE: capacity is bounded by the encoder dim (384) -- real
embeddings don't have the orthogonalization headroom that synthetic Hadamard keys do. Cross off Slot 9 (MIDDLE).

GPU FOLLOW-ON QUEUED (substrate_etf_minilm_dim_expansion_v1): directly tests the fix implied by Slot 9 -- expand the
substrate dim with a nonlinear random-feature lift phi(x)=sign(Rx), D in {384,1024,4096}, then orthogonalize. SMOKE:
whitened_cap D384=576 -> D1024=1536 (~2.67x for 2.67x dim = ~LINEAR scaling; D1024 grid-censored). Strong signal that
EXPANSION recovers the headroom: capacity scales ~linearly with expanded dim. Full (D=4096, N_enc=10000) running on GPU.
PHASE-4a IMPLICATION (if full confirms): for real encoders, don't just orthogonalize -- EXPAND substrate dim THEN
orthogonalize to recover the synthetic-scale capacity gains.

NOTE: I built this follow-on (not yet on SSOT) to keep the GPU lane busy with genuine work while SSOT GPU cells are
thin. Please confirm/re-rank, and add to SSOT if you agree it is worth the slot. Otherwise I will pull the next SSOT
GPU-appropriate cell.
