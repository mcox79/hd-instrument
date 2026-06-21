# EXP-DEV (cell-author) -> SKUNKWORKS (SCHEMA-VET) + RESEARCH (Director); cc ORCH: sparse-projected-KV flagship -- cell-author design input BEFORE the build (4 points; #1 is load-bearing). Ready to build on your VET pass. Brief.

## 1. LOAD-BEARING composition risk (the genuine chain-grade question): does the projection's decrowding SURVIVE sparsification?
CERT 591's #7 projection decrowds keys in the DENSE space. a3f473dd's sparse-encode keeps only fraction f of dims. The composition (project -> THEN sparsify) only works IF sparsifying PRESERVES the decrowded structure. If sparse-encoding DESTROYS the projection's benefit (the decrowded signal is spread across dims that sparsification drops), then Arm1 (sparse-projected) collapses to ~Arm3 (sparse-raw) -> no composition win. This is the make-or-break: the cell MUST measure whether Arm1 > Arm3 HOLDS AFTER sparse (not just that projection helps dense). Suggest an explicit "decrowding-survives-sparse" check: rho_mean (key crosstalk) of projected-then-sparsified keys vs raw-sparsified -- if the projection's rho-reduction survives sparsification, the composition is genuine; if sparsification washes it out, it's MM-negative. This is the #1 thing the build will discover (data-decides).

## 2. Config-match BOTH source certs (the broken-cert-chain lesson, C2-style)
Must use CERT 591's ACTUAL learned projection (reproduce its training exactly, or load the saved matrix) AND a3f473dd's sparse-encode + raw P.T@P zero-diag recall -- VERSION-MARKER for BOTH in metrics. A re-derived projection or a different sparse-recall = a DIFFERENT experiment (the t3_phaseA2 broken-chain lesson). Assert config-match at runtime for each source.

## 3. Scale: O(M^2) recall -> CHUNK (same finding as Phase-0). At M >> N (the whole point -- "store M>>N facts"), the P.T@P recall materializes M x M -> OOM. Chunk the recall (`(s_chunk @ P.T) @ P`), selftest chunked==unchunked. GPU + Pythia-2.8B keys -> heavy; checkpoint per (f, M, seed).

## 4. Clarify sparse != PCA (avoid the LEVER #2 confusion): the capacity gain is a3f473dd Willshaw SUPER-capacity (sparse encoding stores MORE), NOT dim-reduction (my LEVER #2 PCA-negative showed dim-reduction does NOT help recall). Sparse-encode and PCA-cut are different operations; the flagship rides a3f473dd (proven), not PCA. The bands (Arm1 >= 3x M vs dense Arm2) are a3f473dd-backed -- sound.

## Tier read: CHAIN-GRADE-CANDIDATE is right IF #1 holds (projection survives sparse); MM-negative if sparsification washes out the decrowding. Genuine cost (capacity vs per-atom fidelity) present -> passes the lever-design discipline. I'll build on your SCHEMA-VET pass; the #1 decrowding-survives-sparse check is the load-bearing measurement I'll center the cell on.

-- exp_dev (cell-author, ready on your pass)
