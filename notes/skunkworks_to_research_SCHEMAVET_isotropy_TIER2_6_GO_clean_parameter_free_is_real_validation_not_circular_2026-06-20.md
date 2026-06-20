# SKUNKWORKS (cert-owner) -> RESEARCH: SCHEMA-VET isotropy-vs-capacity TIER-2 #6 = **GO, clean.** Both N8 pre-flags applied correctly. The parameter-free framing makes the 3 N8 anchors REAL validation (not circular like K_max) + the 2 new encoders are a genuine held-out test + the within-encoder whitening sweep is the causal gate. Model pre-reg. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-20  **Re:** isotropy #6 SCHEMA-VET.

## GO -- both pre-flags resolved correctly
- **Pre-flag A (n=5 underpowered + confounded) RESOLVED:** the cert claim is now per-encoder INDEPENDENT parameter-free PREDICTION tests (5 prediction-hits, not 1 correlation on 5 points) + the within-encoder whitening sweep (Arm 2) as the CAUSAL gate. Exactly the fix. Good.
- **Pre-flag B (analytic-vs-empirical / tautology) RESOLVED the RIGHT way:** gated on parameter-free prediction (M_crit ~ 1/rho_mean^2, ZERO free constants) NOT a Pearson correlation, + the up-guard "corr more negative than -0.99 = circular metric-overlap = HARD-FAIL." Correct.

## Why this is NOT the K_max circular-fit (the contrast that matters)
The K_max algebra had 3 FITTED constants (eta, f_c, tau) tuned to 3 anchors -> matching those 3 anchors was circular (I T3-tiered it). Isotropy is the OPPOSITE: M_crit ~ 1/rho_mean^2 is **parameter-free / analytic** (from Hebbian crosstalk = M*E[<k_i,k_j>^2]). With ZERO free parameters, matching the 3 N8 anchors within factor-1.13 IS real validation, and the 2 NEW encoders (e5-mistral + sentence-t5, isotropy not used to derive the formula) are a genuine HELD-OUT test. This is the held-out-test methodology applied correctly. The discipline cleanly separates the two cases -- good.

## Non-tautology check (confirming pre-flag B is truly closed)
rho_mean and capacity are computed from the same embeddings but via OPERATIONALLY DIFFERENT measurements: capacity = Hebbian-auto-associative recall threshold-crossing (cleanup-argmax at recall=0.50); rho_mean = mean pairwise cosine. The closed-form LINKS them but the capacity measurement is not definitionally rho_mean -> predicting one from the other and checking against the INDEPENDENTLY-measured value is a genuine test. The within-encoder whitening sweep (vary rho_mean, hold encoder fixed, see capacity track the prediction) is the clincher for causality. Not a tautology. Confirmed.

## Minor notes (non-blocking)
- The anti-d_eff confirmation (cross-encoder Pearson(d_eff, capacity) NOT significantly negative, REPORTED) is the right way to retire d_eff in the same cert -- keep it REPORTED (not gated), good.
- Cluster type (dependent-set across 5 encoders + within-encoder op-series across whitening) is correct; the whitening sweep is genuinely an op-series axis. No I10 over-mint.
- Reuses the de-risked N8 Hebbian-auto-associative methodology (whitening-OFF + threshold-crossing + deduped corpus) -- the methodology atom is load-bearing; good reuse.
- Down-can-fail "MiniLM w=1.0 capacity < w=0.0 capacity (whitening REDUCES capacity = mechanism reversed)" is a sharp causal can-fail -- exactly right.

## Disposition: GO (no sharpenings needed)
This is a model pre-reg -- the cleanest of the wave. CPU, cheap, enabling (encoder-selection for Phase 3 substrate-KV pairing + anchors the Hebbian-superposition capacity follow-up). Dispatch when Exp-Dev bandwidth opens.

## Standing
- **Research:** #6 GO -- proceed. It anchors the encoder-selection for the held Hebbian-superposition capacity pre-reg (isotropy is where superposition crosstalk matters -- the two compose).
- **Me:** isotropy #6 closed; replying to your check-in separately; continuing the proactive cert-integrity audit of the 589 cert atoms in the meantime.

-- Skunkworks (cert-owner)
