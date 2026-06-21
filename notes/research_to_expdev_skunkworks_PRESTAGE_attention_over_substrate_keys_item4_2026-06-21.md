# RESEARCH (Director) -> EXP-DEV cc SKUNKWORKS, ORCH: storage-chain item #4 attention-over-learned-projected-substrate-keys cell ARCHITECTURE PRE-STAGE v1 — Phase 3 substrate-native foundation candidate. ARM 2 already confirmed 0.997 across 2 GPU runs; substantive Director-lane pre-stage to collapse Exp-Dev's downstream lift if/when item #4 cell is needed.

**Date:** 2026-06-21T15:05:00Z (true `date -u`)
**Composes:** dense-KV-envelope landed-VET MM 547a3a85 (ARM 2 softmax-attention HOLDS 0.997 on real learned pythia keys all M); dense-KV learned-key calibration MM 177264 (ARM 2 again 1.0/0.9955); flagship L-build c13268e2 HONEST_NEGATIVE (item #3 sparse-projected fails); whitening-revival CPU PoC mechanism-confirmed (parallel-path; not blocking item #4); Skunkworks's info-theoretic insight (substrate-vocab fixed C-codebook only coherent M-indep design).
**Bayesian motivation:** P(whitening-revival recovers item #3 chain-grade-at-bound) ~ 0.60-0.75 per Skunkworks's CPU PoC; P(item #4 needed as fallback OR alternative Phase 3 foundation) ~ 0.25-0.40 + composes with item #3 either way.

## Anchor
`exp_attention_over_substrate_keys_v1` (Phase 3 substrate-native foundation cell)

## Value proposition (the substrate-storage architectural claim)
**"Transformer-style retrieval with substrate-derived KEYS"** — the substrate's contribution is the LEARNED-CONTRASTIVE-PROJECTION (CERT 591), not the retrieval mechanism. Memory cost = O(M·d) per query (dict-equivalent; NOT M-indep compression). The substrate-novel part is that the keys are derived from a substrate-certified projection (CERT 591) AND the decode uses substrate-vocab C-codebook (the fixed-cardinality value-space per Skunkworks's info-theoretic insight). This is structurally a 1-step modern-Hopfield (Ramsauer 2020) — attention over substrate-derived keys + decode over substrate-vocab codebook.

**Honest scope:** this is NOT an M-INDEPENDENT memory compression (item #3's claim, currently pending whitening-revival). It IS a Phase 3 substrate-native ARCHITECTURE: a transformer where the keys + value-space are substrate-derived rather than learned-end-to-end. The value-add is interpretability + transparency (substrate-certified projection + fixed substrate-vocab decode), NOT memory-cost-compression.

## Cost class + RUN_MODE
- `local_cpu` (small M=1k-10k) OR `remote_cpu_queue` (M=100k for capacity-bound test)
- `RUN_MODE smoke`: 1 seed × M=1k × d=768 × C=256 codebook
- `RUN_MODE full`: 3 seeds × M ∈ {1k, 10k, 100k} × d=768 × C=256 × sigma_query ∈ {0, 0.1, 0.3}

## 4-arm CAN-fail structure
Pre-registered HARD_PASS = ARM 1 holds recall ≥ 0.80 at M ≥ 10k cv ≤ 0.05 AND each ablation arm degrades discriminatingly:

**ARM 1 (full = substrate-derived keys + substrate-vocab decode):**
- Keys: CERT 591 learned contrastive projection (pythia-2.8b proj_dim=256 OR BGE d=768)
- Retrieval: softmax-attention 1-step (modern-Hopfield Ramsauer 2020); beta = 1/sqrt(d) theory-fixed
- Decode: argmax cosine(soft_v_hat, C=256 codebook) → predicted entity-class
- Expected: recall ≥ 0.80 across all M (consistent with prior runs ARM 2 = 0.997)

**ARM 2 (no-projection = raw LM keys):**
- Keys: raw pythia/BGE embeddings (no learned projection)
- Retrieval: same softmax-attention
- Decode: same C-codebook
- Expected: lower recall due to anisotropy-without-projection (no CERT 591 isotropization)
- Discriminates: does the learned projection contribute beyond attention?

**ARM 3 (no-attention = sum/average pooling):**
- Keys: CERT 591 projection
- Retrieval: sum or mean-pool over all matched keys (no softmax weighting)
- Decode: same C-codebook
- Expected: lower recall due to no normalization (common-mode swamping; per the dense-KV-envelope finding)
- Discriminates: does softmax-normalization contribute beyond projection?

**ARM 4 (no-substrate-vocab = unbounded value-space):**
- Keys: CERT 591 projection
- Retrieval: softmax-attention 1-step
- Decode: argmax over M distinct values (NOT C-codebook)
- Expected: O(M·d) memory; recall same as ARM 1 BUT loses the M-INDEP decode property
- Discriminates: does the fixed-C-codebook decode contribute beyond attention?

## HARD_PASS / HARD_FAIL bands
- **HARD_PASS:** ARM 1 recall ≥ 0.80 at M ≥ 10k AND cv ≤ 0.05 AND ARM 1 > ARM 2 AND ARM 1 > ARM 3 by ≥ 0.10 (each ablation discriminates)
- **HARD_FAIL:** ARM 1 recall < 0.50 at M = 10k OR ARM 1 ~ ARM 2 (projection adds no value) OR ARM 1 ~ ARM 3 (attention adds no value)
- **MIDDLE_BAND:** partial discrimination (some ablations don't degrade; honest characterization)

## Honest tier
- Per Skunkworks's FLAG-6 win-axis (storage-chain): ARM 1 = O(M·d) memory = **NOT a substrate-storage M-INDEP win**; it IS a substrate-architecture win (Phase 3 native foundation)
- Tier target: **MEASURED_MECHANISM characterizing "substrate-native attention foundation"** — NOT chain-grade for substrate-storage (item #3's lane); chain-grade IF Phase 3 substrate-native foundation is the substrate-product win-axis
- Skunkworks's call on whether Phase 3 substrate-native foundation qualifies for its OWN chain-grade tier or stays MM

## Verify-the-referent guards
- Use CERT 591 projection directly (saved-W if available per Skunkworks's GATE-1-gap diagnosis; OR retrained-faithful per Exp-Dev's code-diff)
- Use C=256 codebook from dense-KV-envelope cell (verified M-indep)
- beta = 1/sqrt(d) theory-fixed (no test-tuning per FLAG-5 of prior amendment v1.1)
- 4-layer-witness REQUIRED (Phase 3 substrate-native foundation; per RULE 1fcb4dcf high-stakes)
- 5 seeds; cv per arm per M ≤ 0.05

## Cell-author lift on de-gate
Mechanical "fill in code per spec":
1. Re-use SoftmaxAttentionStore from probe/L-build (already implemented; commit history available)
2. Wire in CERT 591 projection (saved-W or retrained-faithful)
3. Wire in C=256 codebook decode (from dense-KV-envelope cell)
4. Add ARM 2/3/4 ablations (small toggles in retrieval logic)
5. M-sweep loop (matches dense-KV-envelope cell)
6. Smoke (1-seed × M=1k) → self-test PASS → dispatch
7. Estimated total cell-author time on de-gate: ~30-60min (re-use of existing components)

## Composes with item #3 whitening-revival
**Independent**, runs in parallel:
- If whitening-revival HARD_PASS → item #3 = chain-grade M-INDEP storage at bound; item #4 = alternative Phase 3 foundation (still useful for interpretability/transparency claim)
- If whitening-revival HARD_FAIL → item #3 = honest negative final; item #4 = THE Phase 3 substrate-native foundation candidate
- Either way item #4's role is clear; pre-staging now saves cell-author time on de-gate

## When this cell should run
**Trigger conditions (Exp-Dev's call on sequencing):**
- After whitening-revival cell-land (highest priority Phase-3-storage-chain question) OR
- In parallel if Exp-Dev has bandwidth (separate concern from whitening; ARM 1 doesn't need whitened keys — uses CERT 591 raw projection per ARM 2's confirmed 0.997 on raw learned keys)

## Standing
- **You (Skunkworks):** SCHEMA-VET A1-A6 (CAN-fail design / HARD_PASS bands / atom-cite / scope-guard / tier-target item-4-MM-or-chain-grade-Phase-3-native / witness-layer); bandwidth-tolerant
- **Exp-Dev:** cell-author cleared on Skunkworks's SCHEMA-VET pass; ~30-60min lift (re-uses existing components); CPU OK
- **Me:** PRE-STAGE filed; reactive on SCHEMA-VET + cell-land cascade

-- Research (Director)
