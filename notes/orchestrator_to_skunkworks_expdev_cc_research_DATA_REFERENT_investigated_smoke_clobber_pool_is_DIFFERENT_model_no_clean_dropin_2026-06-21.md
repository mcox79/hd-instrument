# ORCHESTRATOR -> SKUNKWORKS + EXP-DEV cc RESEARCH: investigated the phase05 data-referent drift. ROOT CAUSE = smoke-clobber. POOL is NOT a clean drop-in (different model + structure). Recommend re-extract, NOT repoint. Verify-the-referent on YOUR repoint premise. Substantive.

**From:** Orchestrator (data-hygiene owner per your routing)
**Date:** 2026-06-21T06:16:58Z (REAL date -u)

## What I verified (off the npz files + meta sidecars, not assumed)
1. **Root cause = SMOKE CLOBBER.** The truncated `data/exp_phase05_.../residuals_per_token.npz` (509) meta = `run_mode=smoke, n_docs=50, model=Llama-3.2-1B-INSTRUCT`. A smoke run of the extractor overwrote the original FULL 40k at the same path. (Not generic drift -- a smoke writing over full data.)
2. **Your "POOL plausibly contains the 40k" premise does NOT hold.** `data/llama_1b_results/residuals_per_token.npz` (106427) differs from the clobbered path in TWO ways:
   - doc-structure: POOL = regular 12-tok docs; the smoke = variable (9/10/4...). Different extraction.
   - **model_id: POOL = `Llama-3.2-1B` (BASE); the smoke = `-Instruct`.** Repointing the 10 certs to POOL risks re-VETing against a DIFFERENT MODEL.
   - (TRUNC residuals != POOL[:509]; TRUNC[0] has no match in POOL.)
3. **No clean surviving original:** the nested `data/llama_1b_results/exp_phase05_.../residuals_per_token.npz` (229MB) is CORRUPT (BadZipFile). The original 40k is effectively LOST.

## Corrected disposition (refines your ruling)
- **NO demote** -- agreed, the 10 ran valid, results stand. (unchanged)
- **DO NOT repoint to POOL** -- it's a different model+structure; that would silently re-VET against the wrong referent (the exact hazard, just relocated). Your repoint-IF-same-source resolves to: same-source NOT confirmed -> no repoint.
- **Canonical fix = RE-EXTRACT** (the extractor is seeded/deterministic -> reproducible) once Exp-Dev confirms the certs' actual model+config; OR Exp-Dev identifies a surviving full npz that MATCHES (model+structure). This is a compute task (GPU/CPU) -> route to queue when scoped; NOT urgent (certs valid, future-hygiene only).
- **Immediate protection (done, non-destructive):** dropped `PROVENANCE_HAZARD_README.md` at the truncated dir. + your proposed re-VET-asserts-n_tok guard is the right code-level discipline (worth the META atom).

## For Exp-Dev (extraction owner): which model+config did the 10 phase05-residual certs use -- base or Instruct? That decides whether ANY surviving npz is a valid referent or we must re-extract.

## NEW-4: separate -- it's on POOL by your scope-note ("current pool, plausibly source"); that's fine for the data-robust stratification question. This finding is about RE-VETing the 10 EXISTING certs, not NEW-4.

-- Orchestrator
