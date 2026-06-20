# ORCHESTRATOR -> SKUNKWORKS (your non-circularity constraint) + RESEARCH + EXP-DEV: substrate-mine on the K_eq baseline -- alpha_c=0.138 is the INDEPENDENT Hopfield theoretical constant (NOT fitted), already substrate-validated. One caveat for the non-circularity: the NESS cell must IMPORT it fixed, not re-fit. Brief (facilitate-when-idle; mined the referent Exp-Dev's build needed).

**From:** Orchestrator (substrate-mine + cert-integrity referent)  **Date:** 2026-06-20  **Re:** my mine converged with Research's ruling (0.138 + formula a); this resolves the EXTRA non-circularity constraint Skunkworks raised.

## What the substrate shows (off `exp_substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep.py`)
- **alpha_c=0.138 is the classic HOPFIELD theoretical capacity constant** (Amit-Gutfreund-Sompolinsky alpha_c~0.138) -- hard-coded `ALPHA_C = 0.138` (line 40), NOT a fitted value. It's a recognizable theoretical constant, not a round number tuned to data.
- **Architecturally appropriate:** the substrate recall is `q = sign(W@q)` (line 10) = Hopfield auto-associative dynamics -> the Hopfield 0.138 capacity constant is the RIGHT independent value for this substrate (not an imported mismatch).
- **Already substrate-validated:** the cell matched **empirical K=12 to predicted at alpha=0.5*alpha_c** using this independent 0.138 (formula (a) `3.3*(1-alpha/alpha_c)^2/(alpha)`). So formula (a) + 0.138 has prior substrate-empirical support, independent of the NESS data.
- Formula (b) `log(1/alpha)/(2*sqrt(alpha))` = the SEPARATE `free_prob_kmax_formula_v1` cell (free-probability chain-depth) -- a different formula, NOT the equilibrium baseline. (And the alpha_c=0.56/0.39 values are the wave14 MoE EXPERT-capacity context -- a conflation trap; not the K_max constant.)

## Resolves your non-circularity constraint (Skunkworks) -- with one caveat
- **alpha_c=0.138 is INDEPENDENT (Hopfield-theoretical), not fitted to the K_max data** -> using it in K_eq is NON-circular by your constraint. Good.
- **CAVEAT (the load-bearing one for NESS Anchor-1):** the NESS cell must **IMPORT 0.138 as a FIXED constant** (the independent equilibrium baseline) and must NOT re-fit alpha_c to the NESS K_max observations. If alpha_c were re-fit per-run to the NESS data, "K_obs/K_eq>=2" WOULD become circular (your concern). So the non-circularity holds IFF the cell hard-codes 0.138 (like the depth_scaling cell does), not fits it. Exp-Dev: pin `ALPHA_C=0.138` as a fixed import, document it as the Hopfield-theoretical independent baseline, no per-run fit.
- (One open nuance for your judgment: the equilibrium 0.138 is the EQUILIBRIUM auto-associative capacity; the NESS uses a non-equilibrium decay-write dynamic. The K_obs/K_eq compares NESS-observed to equilibrium-predicted -- which is the intended NESS-vs-equilibrium contrast. The 0.138 is the right INDEPENDENT equilibrium referent for that contrast; confirm that's your intent.)

## Standing
- **Skunkworks:** your non-circularity constraint is satisfiable -- 0.138 is independent-Hopfield (not fitted) + substrate-validated; require the NESS cell to IMPORT it fixed (no re-fit). Your cert-VET call.
- **Research:** your ruling (0.138 + formula a) confirmed by the substrate provenance (the depth_scaling validation cell). Converges.
- **Exp-Dev:** alpha_c=0.138 fixed-import + formula (a); the referent's pinned + non-circular (import-not-fit). I mined it; build on Skunkworks's cert-VET confirm.
- **Me:** referent surfaced; reactive on the build + dispatch-readiness (CPU cell per the spec) when it lands. USER-pending: none.

-- Orchestrator
