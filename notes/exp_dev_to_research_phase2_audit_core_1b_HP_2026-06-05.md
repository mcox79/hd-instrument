# Exp-Dev -> Research: Phase 2 -- audit-core at Llama-1B HARD_PASS (HIPAA wedge scales) + EX-CONCEPT-1B

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~12:30

## Phase 2 launched (Llama-1B npz delivered: 106k tokens, 2048-dim, 10000 docs). Residual-only cells:
- substrate_audit_core_C2_C3 at Llama-1B: HARD_PASS (real data, 3 seeds). C2 deletion-cert=1.00, C3 drift-sep=15.5x
  on REAL Llama-1B residuals. The HIPAA/GDPR deletion-certificate + drift-detection product wedge SCALES to 1B
  (cleaner than Pythia's C2=0.98). Tier-1 product anchor confirmed at 1B. Build fix: whiten newb into store-space
  (orig dim 2048 > M=2000 reduced the whitened rank; Pythia 768<M never hit this).
- EX-CONCEPT-1-real at Llama-1B: MIDDLE (substrate 0.727 vs bigram 0.716 at V_c=256 -- same bigram-level finding as
  Pythia; the K2-XOR rescue should apply at 1B too, building next).

## Phase-2 remaining: Tier-4-Llama (CRITICAL attn-swap -- LOADS 1B model -> 8GB 4060Ti OOM risk; will attempt bf16
or flag for bigger GPU); EX-CONCEPT strong-baselines + K2-XOR at real 1B concepts; CCC-1-v2 at 1B (needs Llama-1B
baseline = model load). The residual-only cells (audit-core, EX-CONCEPT, K2-XOR) are safe; the model-load cells
(Tier-4, CCC-1-v2 generation) need the 1B model on 8GB -- may need bigger GPU.
**END.**
