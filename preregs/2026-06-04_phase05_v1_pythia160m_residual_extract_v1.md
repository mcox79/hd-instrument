# Prereg: phase05_v1_pythia160m_residual_extract_v1
## Anchor
phase05_v1_pythia160m_residual_extract_v1
## Routing
Research-requested (hourly_cadence note): queue Pythia-160M residual extraction per Testbed ready-to-queue handoff.
Unblocks CCC-1-v2 + CCC-1-EXTRA + EX-CONCEPT-1-real + audit-core C2/C3. GPU idle post-v7. TOKENIZERS_PARALLELISM=false
+ per-doc watchdog (v6/v7 fork-deadlock fix). 10k docs target, hidden 768.
## Bands
HARD-PASS n_residuals>=5000 AND npz exists AND finite AND shape (n,768). MIDDLE 2500-5000. HARD-FAIL <2500 or npz absent or NaN.
## Queue
overnight_queue timeout 3600s.
