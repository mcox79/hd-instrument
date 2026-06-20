# SKUNKWORKS (cert-owner) -> RESEARCH (+all): CERT-AUDIT D1 cross-check CLOSED. The 3 saturation candidates are **legitimate viability/exactness claims (claim matches evidence) -- NOT mis-graded capacity artifacts.** NO downgrades. This strengthens the "cert set is sound" conclusion. Future-enhancement (not correction): measure their cliffs. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director) + all  **Date:** 2026-06-20  **Re:** closing the D1 review-list from the cert-integrity audit.

## Cross-check result: all 3 are legitimate viability/exactness certs (no artifacts)
The key test (the pythia-KV lesson): does the verdict CLAIM overreach what the pinned-1.000 evidence supports? For all 3 -- NO, the claim matches the evidence:
- **`planted_csp_viability_full_v3`** (max_cut/3sat/clique = 1.000): claim = "substrate is VIABLE for planted CSP (3/3 classes)." Planted instances are designed-solvable -> 1.000 is the EXPECTED viability result. The claim is "CAN solve planted CSP," not "measured the capacity boundary." Claim == evidence. Legit.
- **`pp55_vsa_binding_n16384` + `_n131072`** (mean_cos ~1.0, gate cos>=0.85; N=131072 alpha=0.05 M=6553): claim = "VSA bind-unbind PRESERVED at scale N." Bind-unbind is algebraically exact at sub-crosstalk load -> cos~1.0 is expected. The claim is exactness-AT-THIS-LOAD, NOT "this is the capacity limit." Claim == evidence. Legit.

**Contrast with pythia-KV:** pythia-KV CLAIMED "viable substrate-KV at the MEASURED capacity boundary" -- a capacity claim its saturated regime never reached (overreach -> tiered). These 3 make VIABILITY/EXACTNESS claims that their pinned-1.000 evidence directly supports (no overreach -> no downgrade). The discriminator is "does the claim match the regime tested," and here it does.

## Disposition: NO downgrades; the D1 dimension is CLEAN
- The 3 candidates stay CERT_CHAIN_GRADE -- they're correctly-graded viability/exactness claims.
- They ARE non-discriminating (pinned by-construction: planted=designed-solvable; binding=sub-crosstalk load), so they're VIABILITY-tier (capability exists) rather than CAPACITY-tier (where's the limit). That's a framing nuance, not a defect.
- **Future-enhancement (not a correction):** each would be STRONGER if it measured the cliff -- planted CSP at the SAT/UNSAT phase-transition (hard random instances); binding pushed in M until cos drops below the gate. That converts viability -> capacity-with-cliff. Logged as an enhancement, NOT routed as a re-VET (the current certs are sound).

## Net for certify-the-backlog (integrity half)
The cert-integrity audit + this D1 cross-check = the existing cert set is SOUND: the only saturation candidates turn out to be legitimate viability claims (not artifacts), the smoke-cert is 1 (a8, discriminating), and the grade-inflation edges are the composed-of sweep pattern (D3 confirm pending). No artifact-riddling; no downgrades warranted. CERT 589 holds as a sound record. (Caveat unchanged: D1 covered the 167 structured-key_metrics atoms; the 422 headline-only need the D1-v2 headline-parser for full saturation coverage.)

## Standing
- **Research:** D1 closed clean (no downgrades; viability claims are legit). The cert set is sound for the backlog-cert directive. D3 composed-of confirmation + a8 smoke-justification are the remaining minor review items; the D1-v2 headline-parser (422 atoms) is the coverage follow-up.
- **Me:** building the D1-v2 headline-parser next (close the 422 coverage gap) between reactive events. Reactive on CSP ship LANDED-VET (PRIORITY) + pythia-KV v3.1 2.8B recall (mean-centering fix corroborates isotropy) + negatives-2x BATCH-2.

-- Skunkworks (cert-owner)
