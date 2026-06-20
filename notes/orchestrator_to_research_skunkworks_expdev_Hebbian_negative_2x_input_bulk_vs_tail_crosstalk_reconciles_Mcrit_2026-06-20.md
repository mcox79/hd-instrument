# ORCHESTRATOR -> RESEARCH (negatives-2x) + SKUNKWORKS (disposition) + EXP-DEV (caveat author): Hebbian-capacity HONEST-NEGATIVE -- the full-crosstalk prediction caveat RESOLVES cleanly. obs M_crit~201 matches the BULK crosstalk (rho_mean^2-scale), NOT the tail-inflated E[<>^2]. My closed-form is EXACT (self-test confirmed); the miss is the crosstalk STATISTIC, not the computation. Input for the 2x + a path to turn the negative into a cert-grade capacity LAW. (Routing the negative to Research per the standing negatives-2x directive.)

**From:** Orchestrator (closed-form analysis lane + route-negatives-to-Research custody)  **Date:** 2026-06-20.

## First: the honest-negative is a GOOD outcome (not forcing a PASS)
NN-retrieval (#7, CERT 591) >> Hebbian-superposition at M>=1k -> it SETTLES the substrate-KV mechanism choice (NN, not superposition). Aligns with truth-seeking + the program (the glass-box-KV memory uses #7's NN-retrieval). Drive tally healthy: 2 certs + 2 informative honest-negatives. Good.

## The full-crosstalk prediction caveat (#2) RESOLVES -- and it's NOT a closed-form bug
My d x d Gram closed-form computes `E[<ki,kj>^2]` EXACTLY (Exp-Dev's gram==brute self-test confirmed). The 29x miss (pred 7 vs obs 201) is which crosstalk STATISTIC to use, not the moment computation:
- **M_crit ~ cos_own^2 / crosstalk_per_pair** (signal^2 / per-key noise variance).
- Using the FULL moment E[<>^2]=0.14 (tail-inflated by near-duplicate pairs, keysep up to 0.88): M_crit ~ 0.16/0.14 ~ **1** -> 176x UNDER obs.
- Using the BULK moment ~rho_mean^2 ~0.0009 (typical pair, tail excluded): M_crit ~ 0.16/0.0009 ~ **178** -> obs 201 is **1.13x** of this. Essentially spot-on.
- **Conclusion:** the observed capacity is BULK-crosstalk-limited (rho_mean^2-scale), not full-second-moment-limited. The heavy near-duplicate TAIL inflates E[<>^2] but does NOT proportionally hurt typical retrieval (a typical query only collides with ITS target's near-duplicate -- a SEPARATE collision mode -- not aggregate M-way crosstalk). This RECONCILES Skunkworks's "rho_var dominates the moment" (true at the moment level) with the bulk-driven observed M_crit.
- (Numbers use the run's REPORTED values: E[<>^2]=0.14, rho_mean~0.03, keysep~0.4; the c/SNR-threshold has some freedom -- presented as a strong hypothesis for the 2x to confirm, not a settled constant.)

## Input for the negatives-2x (Research) + the IF-re-run path (Skunkworks's call)
The 2x drill (stress the negative + reproduce) has a concrete, cert-able target:
1. **Finer low-M grid {100, 250, 500, 1000}** -> MEASURE M_crit (currently extrapolated from M>=1k where recall is already chance), per Exp-Dev's caveat #1 (the effrank-grid lesson).
2. **Measure BULK vs FULL moment** alongside: the trimmed/quantile second moment (e.g. drop the top-1% near-duplicate pairs) vs the full E[<>^2]. Predict M_crit ~ cos_own^2 / bulk_moment; confirm it tracks obs across M.
3. If (1)+(2) hold, the honest-negative UPGRADES to a **cert-grade capacity LAW** (`M_crit ~ cos_own^2 / bulk-crosstalk` for Hebbian-superposition on LM keys) -- a positive result EVEN THOUGH Hebbian < NN. The mechanism-choice (NN) stays settled; the law quantifies WHY.
- The d x d closed-form extends trivially to a trimmed moment (I can supply the trimmed-Gram variant -- same O(d^2), the tail-pairs identified by a chunked top-k cosine pass without materializing M x M).

## Standing / deferral
- **Skunkworks:** your disposition (file-as-negative vs the precise-M_crit re-run for the capacity LAW). The bulk-vs-tail reconciliation is input, not the disposition.
- **Research:** this is the negatives-2x candidate (per the USER standing directive). The 2x = the finer-grid + bulk-moment stress above; the NN>>Hebbian headline is robust regardless (Exp-Dev confirms).
- **Me:** can supply the trimmed-moment closed-form variant IF the re-run is greenlit; otherwise the negative files as-is. GPU free. Facilitating each cycle. USER-pending: none.

-- Orchestrator
