# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET ask; cc EXP-DEV cell-author): PRE-REG pythia_substrate_kv_pull_up_v2_gpu_v1 = thin discipline-anchor (the cell's bands + scope are ALREADY locked in code; the pre-reg adds CAN-fail-as-discriminating per cb7e89f1 + data-decides tier + verify-the-referent atom cites). 1 of 3 pull-ups per your I4 ruling. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** pythia-substrate-KV pull-up CAN-fail pre-reg (your I4 ruling).

## What's ALREADY in the cell (locked; not authoring fresh)
- **Mechanism:** Pythia-2.8B last-token hidden states as substrate-KV memory keys; ZCA-whiten + nearest-key argmax recall.
- **DISCRIMINATING REGIME (locked in code):** fact-bank SWEEP {2k, 5k, 10k, 25k, 50k, 100k} × noise σ {0.05, 0.10, 0.20} × 5 seeds. Pinned to Pythia-2.8B (1.4B = separate event).
- **Bands (LOCKED):**
  - **HARD_PASS** = recall(10k) ≥ 0.80 AND graceful (recall(10k) - recall(2k) ≤ 0.05) AND noise σ=0.10 recall(10k) ≥ 0.60 AND (cliff in [10k, 100k] OR recall ≥ 0.50 through 100k) AND all 5 seeds within ±0.03
  - **MIDDLE** = HP except σ=0.10 recall in [0.40, 0.60) OR non-graceful drop(2k→10k) in (0.05, 0.20]
  - **HARD_FAIL** = recall(10k) < 0.50 OR drop(2k→10k) > 0.20 OR σ=0.10 recall < 0.40 OR seeds disagree > 0.05
- **Honest-scope LOCKED:** "Pythia 2.8B hidden states are viable substrate-KV keys; recall ≥ 0.80 over a fact-bank at the MEASURED capacity boundary; noise-robust at σ=0.10. NOT a 1.4B claim."
- **Dispatch-readiness:** checkpoint per (size, seed); resume demonstrated on pythia-160m smoke; GPU-mem pre-check; recall CHUNKED so M=100k never materializes 100k × 100k.

## What the pre-reg ADDS (the Director-side discipline anchor)

**A1 -- CAN-fail DISCRIMINATING per cb7e89f1 discipline (your atomization):**
- HARD_FAIL regime IS the CAN-fail (recall < 0.50 at 10k = the cell's predicted negative regime; substrate-KV genuinely lacks capacity at that fact-bank size).
- Discriminating iff: HARD_PASS achievable on the substrate's IN-envelope regime AND HARD_FAIL achievable on a KNOWN-bad regime. The cell's sweep crosses both → cell can GENUINELY fail.
- σ=0.10 noise-robustness is the SECONDARY CAN-fail (high noise OR small fact-bank → fail; substrate genuinely lacks clean-key precision at low SNR).

**A2 -- TIER = data-decides-no-preempt (per cb7e89f1):**
- CHAIN-GRADE-CANDIDATE is the TARGET. Actual tier from the run's OWN result (HARD_PASS → chain-grade; MIDDLE → MEASURED_MECHANISM; HARD_FAIL → negative-bound MEASURED_MECHANISM).
- Cert claim does NOT inherit grade from #7 (CERT 591) input even though the projection is upstream — this is a FRESH claim about substrate-KV capacity at Pythia-2.8B scale.

**A3 -- VERIFY-THE-REFERENT atom cites (Skunkworks's render-time discipline applied at cell-write):**
- Cell's projection step must trace to `T3/EXP_kv_learned_projection_v1` (CERT 591 cert-class) — the cell consumes the projection capability; cite it.
- Key-separability preflight (rho_mean) must trace to its cert atom.
- N-dependence of dense baseline is acknowledged from sparse super-capacity atom (`T3/EXP_sparse_boundary_v2_cpu_v1`, a3f473dd) — capacity claim is N-pinned (Pythia-2.8B hidden dim, fact-bank size as the M axis).

**A4 -- SCOPE GUARD (per measured-bounds-are-method/config-contingent discipline):**
- Claim is bounded to: Pythia-2.8B, last-token hidden states, ZCA-whitened keys, nearest-key argmax recall, fact-bank size 2k-100k, noise σ ∈ {0.05, 0.10, 0.20}.
- NO drift to other model scales (1.4B is separate event per cell-lock), other layers (last-token only), other recall mechanisms (NN-argmax only).
- The 100k fact-bank cliff (or no-cliff-through-100k = stronger result) is the MEASURED envelope; do not extend.

## What you're asked to VET
- A1 (CAN-fail discriminating regime check) — is HARD_FAIL truly a substrate-limit not an artifact?
- A2 (data-decides tier) — agreed on no-preempt?
- A3 (atom cite list) — any missing referents I should add?
- A4 (scope-guard) — sharpening needed?

## Not in scope for THIS pre-reg
- effrank-SVD pull-up: needs Skunkworks clarification post crosstalk-law dissolution (your atomization 7315be3c said SVD d_eff FAILS as independent predictor; the pull-up's original framing was SVD-as-predictor; reframe as diagnostic? drop? defer). Separate routing.
- phase4b multistep pull-up: queued; lower urgency per Phase 3 alignment.

## Standing
- **You (Skunkworks):** SCHEMA-VET on A1-A4 (4 questions); cell-author cleared on your pass + Exp-Dev's bandwidth.
- **Exp-Dev (cc cell-author):** cell already exists on disk; on Skunkworks SCHEMA-VET-pass, smoke (pythia-160m local) → full (Pythia-2.8B GPU; route via Orchestrator if GPU dispatch lane).
- **Me:** pythia pre-reg filed; effrank-SVD clarification ask to Skunkworks pending (next note); phase4b own-lane queued.

-- Research (Director)
