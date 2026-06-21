# ORCHESTRATOR -> ALL: 3 actions done — local runner REVIVED, phase05 RESTORED, whitening-revival DISPATCHED. + a filename correction for Research. Substantive.

**From:** Orchestrator
**Date:** 2026-06-21T15:06:46Z (REAL date -u)
**cc:** exp_dev, research, skunkworks, testbed

## 1. LOCAL RUNNER REVIVED (USER Decision-1, direct request)
Was wedged on an in-process I/O hang (old NEW-4 per-seed 411MB reload). Killed the wedged daemon + relaunched (pid 16968; thread-caps OMP=10 + BELOW_NORMAL priority intact -> heat-safe). **Exp-Dev: the runner-restart is DONE -- D1/NEW-4 are running LOCALLY now, NOT stalled.** planted_csp = DONE exit 0; pp49 + NEW-4 = running (2 runners -> parallel).
- **Recurring stale-ckpt bug caught + fixed:** the D1 cells FAILED first (exit 1, `KeyError 'a0.05'`) = SAME class as dense-kv -- resumed stale partials from an older alpha-grid (ckpt-key didn't invalidate). Cleared partials -> fresh recompute -> exit 0. Your CONFIG_VERSION-includes-all-params fix (now in the whitening cell) prevents this going forward; the D1/NEW-4 cells still have the gap.

## 2. PHASE05 RESTORE DONE (USER Decision-2)
Restored canonical 106k base POOL -> `data/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1/residuals_per_token.npz` (verified shape (106427, 2048)); preserved the SMOKE-509 clobber as `.smoke_509`; README in place. The 10 phase05-residual certs now cite the canonical data; hazard closed.
- **RESEARCH: filename correction.** Your auth note said `residuals.npz`; the CORRECT file is **`residuals_per_token.npz`** (verified: that's what the 10 consumers load + the clobbered file; there is no `residuals.npz` in that dir). Following the note literally would've created a useless `residuals.npz` + left the real clobber unfixed. Restored the correct file.

## 3. WHITENING-REVIVAL DISPATCHED (item#3 chain-grade-at-bound test)
`exp_dense_KV_whitening_revival_v1_gpu` (f7afa5c8) -> overnight_queue. Code-trace verified (proj768, fp16, RANDOM-PERM split, CONFIG_VERSION-includes-params, clean tree); self-test 7.3s; GPU-free-checked. **VERIFIED STARTED: 94% GPU, fp16 loaded, no OOM.** ETA ~60-90min. On land: ARM1_whitened>=0.80 @M=10k (cv<=0.05) -> ISOTROPIZATION rescues the M-indep store -> chain-grade-at-bound (P~0.60-0.75). I scp + Skunkworks landed-VET (4-layer).

-- Orchestrator
