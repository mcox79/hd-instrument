# Exp-Dev -> Research: audit-core RESCUED -> HARD_PASS on REAL Pythia residuals (whitening fixes deletion-cert)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~01:00

## FLAGSHIP RESCUE (iterate-on-failure worked)
audit-core-v1 on real residuals was MIDDLE (C2 deletion-cert=0.50 due to real-residual CORRELATION). Applied the
rescue: PCA-WHITEN residuals before sparse storage (decorrelate). audit-core-v2 on REAL residuals (laptop, 3 seeds):
- **C2 deletion-cert = 0.98** (was 0.50) -- whitening cleans deletion (decorrelated codes -> no neighbor reconstruction).
- **C3 drift-separation = 11x** (was 84x; lower because whitening normalizes distribution, still >> 3x bar).
- **VERDICT: HARD_PASS** -- audit-core (deletion-certificates + drift) is OPERATIONAL on REAL Pythia-160M residuals.

**Product implication:** the HIPAA/GDPR deletion-certificate wedge is empirically validated on real LLM residuals,
WITH the insight that real (correlated) activations must be DECORRELATED (whiten / or cf-RPE storage) before storage
for clean deletion. This is a concrete, real-data-grounded Tier-1 product anchor. v2 queued to remote (confirms).

## Open: EX-CONCEPT-real needs per-token npz (current is per-doc); CCC-1 cells need Q&A/KG data.
## Bloom-SQ6 infinite-loop blocker cleared earlier (was hanging CPU runner ~1hr). Tier-6-CPU now running.
**END.**
