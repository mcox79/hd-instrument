# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: SCHEMA-VET on exp_dense_projected_KV_envelope_v1 = BUILD-WITH-CONDITIONS. One LOAD-BEARING referent-mismatch (ARM 1 != CERT 591) + 5 strengthening conditions. Verified off CERT 591's cell code + metrics.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21 (SCHEMA-VET, verified off DATA: experiments/exp_kv_learned_projection_v1.py + data/exp_kv_learned_projection_v1/metrics.json)
**Verdict:** BUILD-WITH-CONDITIONS. The drill is valuable + theory-grounded; ONE load-bearing fix needed before build, + 5 conditions that make it decisive.

## CREDIT (symmetric) -- what's sound
3 converging theoretical lenses = excellent pre-reg grounding; sigma_query stress sweep = good de-sat; random-key control = good meter-calibration; N-matched arm separates encoder-from-alpha-law; contingent modern-Hopfield pivot pre-staged; deflated probabilities (P_HARD_PASS=0.15) = honest calibration. Good drill.

## FLAG-1 (LOAD-BEARING -- must resolve BEFORE build): ARM 1 is mislabeled "= CERT 591"; the prediction contradicts CERT 591's own data.
- The pre-reg: ARM 1 = "DenseProjectedKVStore CERT 591 (learned projection + cosine-argmax over **outer-product superposition**)", predicted to die at M=10k (~0.40) via RMT crosstalk Phi(1/sqrt(alpha)).
- **VERIFIED OFF THE CELL (line 71):** CERT 591's recall = `np.argmax(Qn @ Kn.T, axis=1) == correct_idx` = **EXACT cosine-kNN over the M x 256 key MATRIX. There is NO superposition store (no W = sum v k^T).**
- Exact-kNN-over-matrix does NOT obey superposition crosstalk. CERT 591 **already measured M=10k at recall 0.827 mean / 0.805 worst_per_unit** (5-seed, GPU, full) -- HOLDS the 0.80 bar, at alpha = 10000/256 ~= 39 (RMT superposition would predict ~0). The drill's ARM 1 prediction (~0.40 @ 10k, fails) is **contradicted by the very cell it cites** -- because it applies superposition-crosstalk theory to an exact-kNN mechanism.
- ALSO: CERT 591 = pythia-2.8b, proj_dim=256, M_sweep already {2k,10k}. The drill's N in {768 BGE, 1024} is a DIFFERENT encoder -> a NEW projection-training (CERT 591 honest_scope: "each LM may need its own projection, by design"). So a BGE arm cannot inherit CERT 591's pass; it must re-establish the projection generalizes on BGE first.
- **RESOLVE (pick one):** (a) ARM 1 IS exact-kNN-over-matrix -> then correct the prediction (CERT 591 HOLDS 10k; the genuine can-fail is the 30k/100k EXTENSION, not 10k) and use CERT 591's exact config (pythia-2.8b/proj256) for the anchor; OR (b) ARM 1 is a SUPERPOSITION store (the RMT law's actual regime) -> then DON'T call it CERT 591; add CERT 591 exact-kNN as a separate baseline arm.

## FLAG-2 (design): make it 3-arm to separate MEMORY-COST from recall (this is the real value-axis)
- **ARM 0 = CERT 591 exact-kNN over key matrix** -- known-pass baseline; **O(M*d) memory** (stores all M keys).
- **ARM 1 = superposition store W = sum v k^T** -- **O(d^2), M-INDEPENDENT memory**; the crosstalk-limited candidate the RMT law actually models.
- **ARM 2 = softmax-attention / modern-Hopfield 1-step** -- the lever; BUT note it ALSO stores all M keys = **O(M*d)**.

## FLAG-3 (calibration anchor / verify-the-referent -- pre-register as a HALT-gate)
At M=10k, sigma=0, ARM 0 (exact-kNN, CERT 591 config) MUST reproduce 0.827 mean / 0.805 worst_per_unit. If it doesn't, the recall meter is mis-calibrated and the whole envelope is suspect -> HALT, don't interpret the sweep.

## FLAG-4 (seed-stability gate -- the flagship lesson)
The flagship L-build died on cv=0.707. Pre-register a cv threshold (e.g. cv<0.05 clean; cv>thr -> MIDDLE_BAND, not chain-grade). A seed-unstable arm is NOT chain-grade.

## FLAG-5 (ARM 2 hidden-DOF)
softmax-attention has beta (inverse temp). Pre-register beta as FIXED-by-theory (Ramsauer beta or 1/sqrt(d)) OR tuned on a DISJOINT split -- NEVER tuned on test. A test-tuned beta inflates ARM 2.

## FLAG-6 (THE win-axis -- pre-commit it, or a "pass" could be a substrate-NEGATIVE)
The storage-chain's value proposition is **M-INDEPENDENT memory** (superposition's O(d^2)). But exact-kNN (ARM 0) AND attention (ARM 2) BOTH store all M keys = O(M*d) = **no better than a plain key-value dict / kNN index.** So per lever-design (99392cca), a "recall win" via ARM 2 at O(M*d) is NOT a substrate-storage win -- it's just "use attention," which a dict already does.
- **Pre-commit the claim:** is it (a) recall-at-M-INDEPENDENT-memory [ONLY the superposition ARM 1 qualifies for chain-grade]; or (b) "the learned projection enables high-M retrieval regardless of readout" [then ARM 0/ARM 2 fine -- but that's a PROJECTION result, which CERT 591 ALREADY established, not a new storage result]?
- Verdict logic must score recall **AT memory-cost**, not recall alone. Otherwise ARM 2 "holds at 10k" reads as a storage win when it's memory-equivalent to a dict.

## NET
Fix FLAG-1 (the load-bearing referent-mismatch) + adopt FLAG-2/3/6 (3-arm + calibration anchor + memory-cost win-axis) + FLAG-4/5 gates -> the cell becomes a genuinely decisive test of THE substrate-storage question (can we get exact-kNN recall WITHOUT exact-kNN's O(M*d) memory). As currently framed it risks "passing" on a memory-equivalent-to-dict mechanism + a prediction its own referent contradicts. Pre-stage approved on these conditions; landed-VET on cell-land. ~1hr CPU est stands if scoped to the corrected grid.

-- Skunkworks
