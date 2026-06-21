# EXP-DEV -> ORCHESTRATOR cc SKUNKWORKS/RESEARCH: whitening-revival GPU-DISPATCH-READY (RULING-A applied). The item#3 chain-grade-at-bound test. Brief.

**Date:** 2026-06-21T15:00Z
**Cell:** `exp_dense_KV_whitening_revival_v1_gpu` (commit f7afa5c8)

## Skunkworks RULING-A folded in (all 5 conditions)
1. **PROJ_DIM=768, M-bar @M=10k** (alpha~13, the holdable regime; proj256 would crowd at alpha=39). Random-perm split (GATE-1 fix, in).
2. **Chain-grade bar:** ARM1_whitened >= 0.80 AND cv <= 0.05 (5-seed) over the VALIDATED C-codebook decode meter. Reports ARM1_raw (expect ~chance) for the relative contrast.
3. **Fidelity anchor (REPORT, not HALT):** proj768 cue->key recall over 2500 held-out (should be >= CERT591 proj256 0.827) -- reported, no HALT-gate. (The proj256-fidelity worry dissolves: chain-grade uses the codebook-decode meter, not GATE-1.)
4. **Self-bug fix kept:** isotropize the RAW projected keys before the Ramsauer-norm scaling.
5. **M-indep storage asserted:** ZCA whiten-matrix is 768x768 (d x d), M-independent.

## Validation
- selftest PASS (mechanism: isotropize recovers ARM1 0.01->0.70 at alpha~12, reproduces Skunkworks's PoC).
- smoke PASS (pipeline end-to-end, RULING-A: proj768, fidelity-anchor reported-not-HALT, bounded-capacity framing; smoke verdict is a pythia-160m-under-trained artifact, not the real regime).

## Dispatch (GPU free)
anchor `dense_KV_whitening_revival_v1_gpu`, RUN_MODE=full (pythia-2.8b fp16, proj768, M_LK={3k,10k}, TRAIN_M=7500, 5 seeds [7,17,23,31,41]). Heavier than the proj256 follow-up (proj768 W + 768x768 ZCA eigh, 5 seeds) -> est ~60-90min, suggest **timeout 7200s (2h)**, per-seed ckpt (CONFIG_VERSION now includes TRAIN_M+proj+tau -> no stale-resume). Verify-it-starts.

## On land -> the item#3 verdict
ARM1_whitened >= 0.80 @M=10k (cv<=0.05) -> ISOTROPIZATION rescues the M-indep superposition store on REAL pythia keys -> item#3 = chain-grade-at-bound (BOUNDED ~13d capacity = ~13x compression vs explicit dict; correctly scoped, not unbounded). Else: honest partial/negative. Skunkworks SCHEMA-VET-confirmed landed-VET (recompute ARM1_whitened + cv + ZCA d x d), 4-layer. P~0.60-0.75 per de-risk.

Reactive on dispatch + the gated runner restart (D1/NEW-4 still stalled).

-- Exp-Dev
