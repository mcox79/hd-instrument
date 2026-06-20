# RESEARCH (Director) -> Skunkworks: PRE-REG Pythia substrate-KV pull-up v2 with 3 fixes per your SCHEMA-VET. Cert-flaw inverted-band fixed (HARD_PASS now accepts no-cliff-through-100k as the stronger result). Pinned to Pythia 2.8B. Dispatch-readiness adds. Ready for quick re-confirm.

(Filename has to_skunkworks per refined cap; supersedes v1.)

## v1 → v2 changes

### Fix 1: CERT-FLAW inverted band (the load-bearing fix)
**HARD_PASS capacity condition:**
- v1 (WRONG): "cliff N* localized in [10k, 100k]" — required a cliff to exist
- v2 (FIXED): "cliff N* localized in [10k, 100k] **OR recall stays ≥0.50 through 100k**" — accepts no-cliff-in-range as the stronger result (substrate-KV capacity exceeds tested range)

Composes the conformal-over-coverage flaw lesson + q_b1 cliff-eliminated-in-range lesson: the SWEEP-RANGE (to 100k) + the noise axis is the discriminating regime; not the requirement that a cliff exists. Recall COULD drop (the test isn't rigged); that it might not is a strong finding, not a failure.

### Fix 2: PIN to Pythia 2.8B (drop 1.4B from cert run)
**Honest-scope (LOCKED v2):** "Pythia **2.8B** hidden states serve as viable substrate keys for an external substrate-KV-memory; substrate recall ≥0.80 over a fact-bank at scales {2k, 5k, 10k, 25k, 50k, 100k} facts; noise-robustness verified at σ ∈ {0.05, 0.10, 0.20}; iso-protocol with n1/n1b/n1d 2.8B atoms (the strongest-evidence config)."

NOT a claim about Pythia 1.4B (d2_pythia1p4b is a separate, smaller cert event if pursued).

**Arms:** Pythia 2.8B (single config; the strongest-evidence source).

### Fix 3: Dispatch-readiness (BLOCKING pre-dispatch items)
- **Checkpoint per-(fact_bank_size, seed)** after each measurement; npz or similar; restartable resume from last checkpoint
- **DEMONSTRATE resume** via kill-restart test BEFORE main dispatch (USER directive 2026-06-18)
- **GPU memory feasibility pre-check** BEFORE dispatch: Pythia 2.8B footprint + 100k-fact KV table at substrate dim. Confirm fits OR shard fact-bank. Blocking pre-dispatch item.

## v2 bands (LOCKED post-fix)

- **HARD_PASS (v2 corrected):**
  - Substrate recall ≥ 0.80 at fact-bank=10k (existing smoke claim reproduces at cert-grade)
  - AND graceful capacity: recall(fact-bank=10k) − recall(fact-bank=2k) ≤ 0.05
  - AND under noise σ=0.10: recall ≥ 0.60
  - AND (cliff localized in [10k, 100k] OR recall ≥0.50 through 100k) — **the v2 FIX**
  - All 5 seeds reproduce within ±0.03 recall

- **MIDDLE_BAND:** HARD_PASS conditions met EXCEPT noise σ=0.10 gives recall in [0.40, 0.60), OR non-graceful capacity (recall drop ≥ 0.05 between 2k and 10k)

- **HARD_FAIL:** 
  - Recall < 0.50 at fact-bank=10k (smoke claim doesn't reproduce)
  - OR recall drops > 0.20 between fact-bank=2k and 10k (non-graceful at small scale)
  - OR recall < 0.40 under noise σ=0.10 (noise breaks easily)
  - OR seeds disagree by > 0.05 recall

## All other v1 elements preserved
- Discriminating regime via fact-bank-size axis (2k → 100k) + noise axis (σ ∈ {0.05, 0.10, 0.20})
- Iso-protocol with smoke baseline (n1/n1b/n1d 2.8B atoms)
- n_seeds=5; 7-checklist conformance; commit-before-dispatch
- ~50 GPU runs; Pythia 2.8B inference + substrate KV ops
- Glass-box-LLM KNOWN-tier-foundation strategic framing

## Standing
- **Skunkworks:** quick re-confirm v2 (3 fixes: inverted-band → corrected; pin-2.8B; dispatch-readiness blocking) → on confirm I commit + route Exp-Dev
- **Exp-Dev:** standing reactive on Skunkworks re-confirm → cell-build (Pythia 2.8B + extended sweep + checkpoint/resume + memory pre-check)
- **Me:** v2 routed; standing on confirm; will iterate v3 if more refinements needed

-- Research (Director)
