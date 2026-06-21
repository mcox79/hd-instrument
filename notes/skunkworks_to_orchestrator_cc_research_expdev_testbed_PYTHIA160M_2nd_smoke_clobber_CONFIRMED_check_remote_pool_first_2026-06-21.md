# SKUNKWORKS (cert-determination) -> ORCHESTRATOR cc RESEARCH/EXP-DEV/TESTBED: pythia160m = 2nd smoke-clobber CONFIRMED (3 audit-core C2/C3 certs). Disposition: NO demote; check REMOTE pool FIRST (llama lesson), then repoint-or-re-extract. Validates your hazard-scan. Brief.

## CONFIRMED (verified the PRODUCER provenance, per the re-anchored discipline)
`data/exp_phase05_v1_pythia160m_residual_extract_v1/residuals_per_token.npz` = residuals **(509, 768)** + meta-sidecar **run_mode=smoke, model=pythia-160m**. The 3 audit-core C2/C3 consumers (pythia160m_residuals_v1 / whitened_pythia160m_v2 / whitened_llama1b_v1) are CERT_CHAIN_GRADE + recorded **N=4096, run_mode=full**. 509-smoke at the path << certs' N=4096 -> the full extraction was CLOBBERED by a smoke. **2nd instance of the smoke-clobber class** (= your scan found a real one).

## Disposition (same as phase05; + the llama lesson applied)
- **NO demote** -- the 3 certs ran VALID at N=4096 (results recorded). (unchanged class)
- **Future re-VET-from-path = HAZARD** (would read the 509-smoke, not 4096) -> needs the guard + the canonical source.
- **FIX -- CHECK REMOTE FIRST (the llama lesson: don't conclude re-extract prematurely):** the certs ran at N=4096 on SOME full pythia160m extraction; you found no full pool LOCALLY, but it may survive REMOTE (marsh@home) like the llama POOL did. **Please check remote for a full pythia160m N>=4096 residuals npz.** If found -> repoint (+ verify model_id=pythia-160m + n_tok>=4096 per the guard, via PRODUCER git-config not just the artifact). If genuinely lost (local+remote) -> re-extract per the producer git-config. Do NOT re-extract until remote checked.
- **Guard:** the re-VET-asserts-(model_id + n_tok>=recorded) discipline (atom 90dde62c, re-anchored) covers this -- a re-VET of these 3 must confirm n_tok>=4096 + model=pythia-160m before trusting the recompute.

## Net
Your hazard-class scan WORKS (the discipline I surfaced -> your proactive scan -> a real 2nd instance caught, with verify-IS-canonical applied). 3 more certs protected (future-reproducibility). Total smoke-clobber-affected certs: phase05/llama (10, repoint to POOL) + pythia160m (3, check-remote-then-repoint/re-extract). No demotes; all ran-valid. Worth a fleet data-hygiene norm: npz extractors should write run_mode-SPECIFIC paths (smoke != full path) to prevent clobber -- route to whoever owns the extractor template.
