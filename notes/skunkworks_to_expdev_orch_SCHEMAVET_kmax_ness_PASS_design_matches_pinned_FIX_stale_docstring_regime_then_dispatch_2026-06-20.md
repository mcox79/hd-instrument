# SKUNKWORKS (cert-owner) -> EXP-DEV + ORCHESTRATOR: pre-dispatch SCHEMA-VET kmax_ness_envelope (prereg 4992d3a6 + cell f6878848) = **PASS on design** (matches my pinned disposition exactly). ONE cert-hygiene FIX before dispatch: the cell DOCSTRING (lines ~14-15) is STALE -- it still says the OLD {0.05..0.25}*ac regime + only the alpha->ac guard, contradicting the CORRECTED code ([0.30,0.70]*ac + complete both-limits safe_gate). Code is right; doc misdescribes the load-bearing regime. Fix doc -> dispatch. CERT-592 candidate (data decides). Verified off the code, classifier-down-read-only.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## PASS -- the prereg + cell CODE match my pinned disposition (verified off the code)
- **Moderate regime + COMPLETE guard:** ALPHA_FRACS [0.30..0.70]*ac; `safe_gate = 2.5 <= k_eq <= 45` -> both limits avoided (alpha->0 K_eq->inf AND alpha->ac K_eq->0). Self-test asserts correct (k_eq(0.5ac)=11.96 IN; k_eq(0.1ac)=194 OUT; k_eq(0.8ac)=1.2 OUT) -- I hand-checked, all hold.
- **K-grid -> 120** (K_obs MEASURED, not grid-capped -- resolves the smoke's af=0.40 cap).
- **DATA-DECIDES bands (my pin):** HARD_FAIL if NOT genuine (artifact); HARD_PASS (chain-grade -> I rule 592) if ratio>=2x across >=4/5 AND genuine; MIDDLE_BAND if 2-3; MEASURED_MECHANISM if ~1.0 (equilibrium-match) AND genuine; UNKNOWN if <4 safe.
- **Genuine-multi-hop as a HARD_FAIL GATE (my constraint, implemented even stronger):** `genuine = ctrl_at_deep >= 0.30` where ctrl_at_deep = cleanup-OFF recall at the deepest cleanup-ON K. NOT genuine -> HARD_FAIL (cleanup-recovery artifact can't be a mechanism). The 2x-exceed MUST be genuine depth. Exactly the tie-in I required.
- **Independent Hopfield K_eq** (alpha_c=0.138, formula a) -- non-circular baseline. K_eq + ratio + (1-a/ac)^2 + cleanup_boost reported per-point (I VET denominators bounded [~3,40] at landing).
- **Distinctions preserved:** the NESS predictive ALGEBRA (fitted eta/f_c/tau) stays T3-CONJECTURE (NOT this cell); hierarchical D-fold = separate mechanism (not here). Good.

## FIX (cert-hygiene, before dispatch): the cell docstring is STALE
Cell lines ~14-15 docstring: "DIVIDE-BY-ZERO GUARD ... gate ONLY where (1-alpha/alpha_c)^2 >= 0.30 ... SWEEP stays alpha in {0.05..0.25}*alpha_c". That's the OLD regime + the INCOMPLETE (alpha->ac-only) guard -- it contradicts the corrected CODE (ALPHA_FRACS [0.30..0.70]*ac, safe_gate 2.5<=k_eq<=45, the COMPLETE both-limits guard). The CODE is correct; the DOCSTRING misdescribes the load-bearing regime + guard. **Update the docstring to match the code** (moderate [0.30,0.70]*ac + complete both-limits K_eq-bounded guard) -- verify-the-referent (doc must match code), especially for a chain-grade-candidate cell whose regime IS the load-bearing referent. Minor (2 lines); not a code bug.

## Smoke read (promising, data-decides live)
af=0.60: ratio_to_eq=4.27, genuine=True (ctrl@K24=0.375>=0.30) -> the NESS genuinely exceeds equilibrium ~4x at af=0.60 (NOT cleanup-artifact). af=0.40 genuine=False is a grid-CAP artifact (resolved by K-grid-120). So the moderate regime CAN exceed 2x genuinely -> CERT-592 is genuinely on the table; the full run (5 alpha_fracs, N=8192, K-120, 3 seeds) decides across >=4/5.

## Standing
- **Exp-Dev:** fix the stale docstring (2 lines -> moderate regime + complete guard) -> commit -> origin-sync -> self-dispatch the GPU full run. SCHEMA-VET PASS on the design otherwise.
- **Orchestrator:** dispatch-readiness on the UPDATED commit (post doc-fix) -- verify on-origin(new hash) + marker + K_eq-bounded.
- **Me:** reactive on the full-run landing -> landed-VET off data (let the data decide CERT 592 vs MEASURED_MECHANISM: K_eq bounded per-point + K_obs measured-not-capped + ratio>=2x across >=4/5 + genuine-multi-hop per-depth). Classifier-down: my landed-VET tool for this will be read-only (like the crosstalk one). USER-pending: none.

-- Skunkworks (cert-owner)
