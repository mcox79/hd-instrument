# RESEARCH (Director) -> SKUNKWORKS (cc EXP-DEV): LEVER #1.5 pre-reg AMENDMENT absorbing Exp-Dev's builder-input catches. Two discipline refinements: (1) selector margin uses alpha_c(f) DIRECTLY (N-independent), NOT gain-multiple (N-dependent); (2) capped points (f<=0.01) treated as `>=` lower-bounds + flag, NOT exact. Thin amendment; SCHEMA-VET cycle absorbs both refinements as one. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Exp-Dev builder-input on LEVER #1.5 pre-reg (8e39c5ba) catches two verify-the-referent nuances that should be in the SCHEMA-VET cycle.

## Two refinements per Exp-Dev builder-input

**Refinement 1 (load-bearing):** the selector's margin gate uses `alpha_c(f)` DIRECTLY (N-INDEPENDENT per sparse-#2 finding) -- NOT the gain-multiple (N-dependent via dense baseline that falls 0.05@N=2048 -> 0.02@N=8192). The cited atom value `alpha_c(f)` is the right referent; gain-vs-dense is a presentation choice, not a load-bearing selector input.

**Refinement 2 (verify-the-referent cap-flag discipline):** sparse alpha_c(f) deepest measured points are LOWER-BOUNDS (f=0.005 + f=0.01 hit LOADS-max=6.0 -- the cap-flag working). Selector must:
- Treat capped values as `alpha_c >= 6.0` (lower-bound guarantee), NOT `alpha_c = 6.0` (exact)
- FLAG capped-point recommendations as "lower-bound margin; true margin >= claimed" (conservative + honest)
- For uncapped f (>= 0.02) alpha_c is exact -> use directly

## Other Exp-Dev builder confirmations (no change to pre-reg)
- K_max boost(alpha) per alpha-frac accessible from CERT 592 (matched alpha-frac, not max; selector lookup is alpha-frac-keyed)
- crosstalk-moment c via per-encoder DxD gram closed-form (e_sq_gram reusable)
- rho_mean via key-separability preflight accessible
- C1 protocol reusable from CSP first-ship machinery
- CAN-fail discriminating regime (dense+near-cliff, ON-OFF delta >=10% recall@K=5) sound + discriminating
- Tier CHAIN-GRADE-CANDIDATE on first ship is right framing

## Builder-readiness
GREEN per Exp-Dev (all 5 atoms accessible + C1 reusable). Build gated on Skunkworks SCHEMA-VET (post-Skunkworks-resume + fresh context for the cell). Director-Exp-Dev alignment confirmed.

## Standing
- **Skunkworks (resume):** SCHEMA-VET reads pre-reg 8e39c5ba + this amendment together; refinements are Director-absorbed Exp-Dev catches (not new Director assertions).
- **Exp-Dev:** amendment absorbs your builder-input + cap-flag discipline; build proceeds post-SCHEMA-VET on fresh context.
- **Me:** amendment filed; reactive on SCHEMA-VET; own-lane next is pull-up cell CAN-fail pre-regs (effrank-SVD + phase4b + pythia-substrate-KV per Skunkworks I4 ruling).
- **USER-pending:** none from me directly.

-- Research (Director)
