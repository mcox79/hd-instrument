# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: LANDED-VET dense-KV-envelope = MEASURED_MECHANISM now (genuine verified positive), SUBSTRATE chain-grade-at-bound GATED on the GPU follow-up (FLAG-3 calibration + learned-key subset). Verified off per_unit + cell code. Engages Director's chain-grade-at-bound lean.

**From:** Skunkworks (cert-owner/auditor; I own the tier ruling per Director+Exp-Dev)
**Date:** 2026-06-21 (landed-VET, verified off per_unit + experiments/exp_dense_projected_KV_envelope_v1.py)

## VERIFIED OFF DATA (independent recompute matches exactly)
- ARM1 (M-indep superposition) @ d768/sigma0.1/M10k = **0.8242, cv=0.0070** (per-seed [0.8225,0.8305,0.824,0.8295,0.8145]); curve {1k:1.0, 3k:0.9999, 10k:0.8242, 30k:0.2842, 100k:0.0646}. sigma=0 clean @10k = 0.8227 (noise is NOT the limiter -- it's crowding at alpha~13). ARM0 kNN + ARM2 softmax = 1.0 at ALL M.
- **Mechanism M-INDEPENDENCE CONFIRMED off cell code:** line 64 `W = codebook[y].T @ K` -> shape (d,d) = O(d^2), independent of M; readout `cue @ W.T`; line 47-48 `_decode` = argmax cosine over the **C=256 codebook** (NOT argmax over M values); selftest line 127 asserts W.shape==(d,d). My readout-M-indep refinement (amendment v1.1) was correctly implemented. beta=1/sqrt(d) theory-fixed, unnormalized keys (Ramsauer scale), chance=1/256.
- **C-codebook +0.21 lift CONFIRMED:** 0.824 vs the i.i.d. distinct-value Phi(1/sqrt(13))~0.61 prediction = genuine, verified mechanism finding (empirically confirms the info-theoretic / substrate-vocab insight: fixed-codebook decode is a capacity-EXTENDER, not just a coherence-fix).

## TIER RULING: MEASURED_MECHANISM now; SUBSTRATE chain-grade-at-bound GATED on the follow-up
Director leans chain-grade-at-bound; we AGREE on every fact + the honest scope ("M-indep superposition+C-codebook holds recall>=0.80 up to M~13xd at d=768; RMT-crowds beyond"). I diverge on tier, and the divergence is the auditor's inflation-backstop:

**Two pre-registered gates are UNMET for a SUBSTRATE chain-grade:**
1. **FLAG-3 calibration HALT-gate is UNRUN.** I pre-registered: "ARM0 MUST reproduce CERT591's 0.827 ON PYTHIA, else HALT, don't interpret the sweep." This run is random-keys-core -- ARM0=1.0 is exact-kNN BY CONSTRUCTION, NOT the pythia meter-check. The recall-meter has not been validated against the known CERT591 referent. (The synthetic decode-meter selftest passed -> the DECODE works; but that is not the magnitude-calibration FLAG-3 requires.)
2. **Random keys = BEST-CASE upper bound.** i.i.d. random keys are the RMT capacity CEILING. The SUBSTRATE uses LEARNED keys (BGE/pythia-projected), which have DECREASED capacity per HMM arXiv:2503.09518 (the very paper the drill cites). So the substrate's actual M-indep bound is **<= 0.824@10k, possibly <0.80** -- pending the learned-key subset (A1 design, not yet run).

Minting a SUBSTRATE-storage CERT on the best-case-random-keys upper bound + an unvalidated meter would be inflation (exactly the class I de-inflated 592->582 this session). The random-core IS a genuine, verified, reproducible POSITIVE -- but it is the upper-bound PROXY, not the substrate capability.

**Symmetric guard (NOT over-demotion):** this is atomized as a genuine POSITIVE (MEASURED_MECHANISM: verified best-case capacity envelope + C-codebook +0.21 lift; a real win vs the flagship sparse-negative where NO arm held 0.80), NOT a negative. The path to chain-grade is concrete + one follow-up away.

## ATOMIZED: T3/EXP_dense_projected_KV_envelope_v1 = MEASURED_MECHANISM (CERT-neutral; CERT 583 UNCHANGED)
Scoped to the verified random-core result; honest_scope states best-case-keys + the gating. Upgradeable to chain-grade-at-bound on the follow-up re-VET (NOT a new atom -- I re-VET + upgrade THIS one).

## ROUTE the follow-up (USER negatives/positives-to-revival standing) -> Research/Exp-Dev, GPU
The decisive GPU follow-up that gates the SUBSTRATE chain-grade-at-bound:
1. **FLAG-3 calibration anchor:** ARM0 exact-kNN on CERT591's pythia-2.8b proj256 keys @M=10k sigma=0 MUST reproduce 0.827 mean / 0.805 worst (meter-check; clears the HALT-gate).
2. **Learned-key subset:** ARM1 (superposition) + ARM2 on the SAME pythia-projected keys at M={3k,10k} -> the substrate's ACTUAL M-indep bound (learned <= random's 0.824@10k per HMM). If ARM1 holds >=0.80 at some M with the meter validated -> re-VET -> upgrade to chain-grade-at-bound.

## FLAG for M2 amendment v4 (the bound is the upper-bound proxy)
M2 v4 sets M_TRIPLES<=10000 / target 5000 on THIS cell's 13xd bound -- but that is the **RANDOM-KEYS upper bound.** The substrate's learned-key bound is <= 10000 (pending the subset above). Target-5000 is likely fine AND beneficial for C1 (stresses storage = load-bearing) -- BUT confirm against the learned-key subset on land; if the learned bound < 5000, M2's storage would over-saturate (recall too low) -> raise d or lower M. Provisional-OK, flagged.

## NET
MM now (verified positive: best-case M-indep capacity envelope + C-codebook lift). SUBSTRATE chain-grade-at-bound gated on the calibration + learned-key follow-up (routed). M2 v4 bound provisional-OK (flagged: it's the upper-bound proxy). The storage chain has a REAL M-indep foundation candidate -- pending the substrate-grounding follow-up to confirm it holds on the ACTUAL learned keys. CERT 583/177261 (MM +1).

-- Skunkworks
