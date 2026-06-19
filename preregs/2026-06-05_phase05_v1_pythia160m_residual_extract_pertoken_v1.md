# Prereg: phase05_v1_pythia160m_residual_extract_pertoken_v1
## Anchor
phase05_v1_pythia160m_residual_extract_pertoken_v1
## Routing
Per-token Pythia-160M residual extraction (Testbed ready-to-queue; forced PER_TOKEN_MODE variant). Output
residuals_per_token.npz (residuals + doc_indices + doc_boundaries). Unblocks EX-CONCEPT-1 REAL (token concept-ID seqs).
## Bands
HARD-PASS n_residuals>=5000 tokens AND npz exists AND finite. MIDDLE 2500-5000. HARD-FAIL <2500.
## Queue
overnight_queue timeout 3600s.
