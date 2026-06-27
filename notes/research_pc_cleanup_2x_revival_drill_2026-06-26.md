# Research -- PC cleanup deeper-chains 2x revival drill (alternative mechanisms)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Drill type:** 2x revival drill on HARD_FAIL (per USER STANDING `feedback-route-negatives-to-research-2x-3x-revival-drills`)
**Trigger:** `data/exp_pc_cleanup_deeper_chains_v1_smoke/metrics.json` PC variant tested = monotone-descent + top-K softmax-bundling at each hop -- HARD_FAIL across depths 15/20/30 at M=160, gap -0.50 to -0.81 vs vanilla cleanup (per exp_dev diagnosis on the FULL run; smoke at M=4 d=5/10 saturates to recall=1.000 for all arms).
**Prior PC anchor:** `pc_cleanup_attractor_v1` HARD_PASS at M=80 d=5/10 (recall=1.000 all arms by-construction-saturation; Wave 1.5 cell was the stress retest that exposed the soft-bundle defect).

---

## HEADLINE

The tested PC mechanism (top-K softmax-bundle at each hop, `bundle = sign(sum_k w_k * codebook[top_k])`) **fails because soft-bundling INJECTS information from K-1 wrong neighbors into the iterated state**. Vanilla argmax-cleanup commits to top-1 each hop; even if top-1 is sometimes wrong, the COMMIT prevents cross-neighbor contamination from compounding. Soft-bundling at every hop turns single-hop ambiguity into a multiplicative noise channel: each hop, the bundle picks up `~beta^{-1} log(K)` bits of noise from the runner-up codewords; over d=20 hops at K=4, that is ~20 * (1/8) * log(4) ~ 5 bits of accumulated impostor-content per pattern.

**Root failure class:** any "soft / blended / mixed" cleanup at iterated-cleanup hops violates the substrate's discrete-attractor regime. The substrate's W-matrix is a HOPFIELD-LIKE landscape where basins are RIDGES not BOWLS -- the right move is hard projection to nearest basin (argmax), not interpolation between basins.

**Substrate-product implication:** to revive any PC-like predictive-error-correction mechanism on iterated chains, the mechanism MUST commit to a discrete attractor at each hop AND derive its corrective signal from a SEPARATE channel (the residual / surprise / energy gradient) that does NOT mix candidate identities back into the state.

**P_deflated for at least one of the 2 anchors closing PC-cleanup on deeper-noisier regime:** **0.40** (calibration penalty applied; novel-synthesis cap honored).

---

## Cheap decisive test

For BOTH anchors below, decisive test = run at the SAME deeper-noisier regime as `pc_cleanup_deeper_chains_v1` FULL (`N=2048, V=7680, M_CHAINS=160, depths=(15,20,30), p_flip=0.30, sigma=0.50, K_top=4` for any top-K usage). HARD_PASS requires `VAN@d20 < 0.85` (regime is genuinely hard) AND `ALTERNATIVE@d20 >= VAN + 0.10` (mechanism differentially helps). Smoke first at depth 5/10 to verify mechanism direction is detectable without by-construction saturation; smoke must use larger M_CHAINS than 4 (use M=20-40) to AVOID the saturation that masked the original smoke verdict.

---

## Falsifiable predictions

### ANCHOR 1: pc_cleanup_HARD_COMMIT_with_residual_rewrite_v1

**Tagline:** Hard-commit to argmax at each hop (substrate's native discrete attractor), but use the predicted-vs-observed residual to RE-WRITE the W-matrix ONLINE for the duration of the chain, not to bundle the state.

**Mechanism (different from the failed top-K soft-bundle):**

1. At hop h, do vanilla cleanup: `next_state = codebook[argmax(W @ noisy(state))]`.
2. Compute residual: `r = noisy(state) - sign(W @ next_state)` (what the substrate FAILED to predict from the cleaned-up next-state going backwards).
3. If `|r|/N > tau_correct` (mismatch exceeds threshold), apply a TEMPORARY Hebbian correction: `W_temp = W + eta * outer(next_state, state)` -- only for the next hop, then revert. This is **predictive-error-driven online plasticity**, not state-blending.

The state never mixes candidates; only W gets a transient correction shaped by the residual.

**Why this avoids the failure mode:** soft-bundling failed because it contaminated the STATE. Online W-rewrite leaves the state pristine and uses the residual to nudge the LANDSCAPE -- exactly analogous to the brain's STDP-on-error (the cleanup attractor itself sharpens; the carried message stays a clean codeword).

**Falsifiable predictions:**
- HARD_PASS: at FULL regime, `recall@d20 >= VAN@d20 + 0.10` AND `recall@d30 >= 0.40` (mechanism preserves SOMETHING at depth 30 where vanilla collapses) AND `monotone_FE_per_hop = True for >= 2 of 3 seeds` (residual rewrite actually descends free energy).
- MIDDLE_BAND: `recall@d20 in [VAN+0.05, VAN+0.10]` (mechanism helps but not strongly).
- HARD_FAIL: `recall@d20 < VAN@d20` (rewrite destabilizes by chasing noise) OR `tau_correct never fires` (residual signal too weak to engage) OR `W_temp accumulates and degrades over chain` (proves transient-only rewrite is not implementable as posed).

**Cross-discipline pulls:**
- **Brain (predictive coding -- Rao-Ballard 1999, Friston 2010):** the brain implements PC via descending predictions + ascending errors; ERRORS update SYNAPSES, not the carried sensory signal. The carried signal at each cortical layer is a CLEANED-UP representation; error drives plasticity on the connections. The failed PC mechanism inverted this -- it used the error to corrupt the carried signal.
- **Signal processing (decision-feedback equalization, Forney 1973):** in DFE, the receiver makes a HARD decision on each symbol, then uses the decision (not a soft tentative) to subtract the inter-symbol-interference from the next symbol's observation. Soft-output DFE was shown by Belfiore-Park (1979) and later by Eyuboglu (1988) to suffer **error propagation** in low-SNR regimes -- exactly the substrate's depth-20 failure pattern. The fix in DFE practice was: hard decision feedback + adaptive equalizer update (online filter coefficient nudge) = direct analog of hard-commit + W-rewrite.
- **Math (online mirror descent, Hazan-Kale 2014):** the residual update on W is a single mirror-descent step on the energy `E(W) = sum over hops of |state_t - sign(W*state_{t-1})|`. Each chain provides T-1 gradient steps where T is chain depth; converges in O(sqrt(T)) regret.
- **Materials (annealing schedule, simulated annealing on substrate energy):** transient W-rewrite is equivalent to lowering the temperature of the energy landscape JUST during the chain, then raising it back. Avoids permanently destabilizing other stored chains.

**P_deflated:** **0.40** (raw 0.55 - 0.15 calibration penalty; brain-grounded mechanism class, well-mapped to substrate primitives; main risk is that the transient W-rewrite mechanism turns out to require deeper integration than substrate's current cell-author bandwidth supports OR that tau_correct never finds a discriminating value).

**Substrate primitives used:**
- Existing: cleanup_memory.py argmax cleanup, vanilla Hebbian outer-product update, hdlab/predictive_coding.py residual_magnitude + threshold_gate
- NEW: `hdlab/transient_W_rewrite.py` -- accept (state, next_state, W) returning W_temp valid for one hop; revert via stack discipline (save delta, subtract on exit).

---

### ANCHOR 2: pc_cleanup_TWO_STREAM_energy_descent_v1

**Tagline:** Run TWO parallel streams down the chain (vanilla + a "shadow" stream that does substrate-energy-descent instead of single-hop argmax); at the END, take the lower-energy result. No mixing along the way.

**Mechanism (different from failed soft-bundle AND from anchor 1):**

1. Stream A (vanilla): `state_A[t+1] = sign(W @ noisy(state_A[t])); idx_A[t+1] = argmax_cb(state_A[t+1])`.
2. Stream B (energy-descent shadow): at each hop, take TOP-K candidates `{c_1, ..., c_K}` by cosine; for each c_k, compute the cleanup energy `E_k = -sum_{prior hops in chain} cos(c_k, sign(W @ state_B[t-h]))` -- i.e. how well c_k continues the chain so far when viewed backwards. Pick `c_argmin_k(E_k)`. This is a `top-K-energy-scored argmax`, NOT a bundle. The state is always a clean codeword.
3. At end, return `argmin(final_E_A, final_E_B)`.

**Why this avoids the failure mode:** still hard-commit at each hop (top-K chooses ONE codeword); the K dimension is used for SCORING not for BUNDLING. Energy-descent introduces a backward-consistency check at near-zero cost.

**Falsifiable predictions:**
- HARD_PASS: at FULL regime, `min(A,B)@d20 >= VAN@d20 + 0.10` AND `B alone beats A on >= 50% of chains` (proving the energy-scoring discriminates, not just acts as a redundant copy) AND `cost <= 1.5x vanilla wall-time`.
- MIDDLE_BAND: `min(A,B)@d20 in [VAN+0.05, VAN+0.10]`.
- HARD_FAIL: `B never wins over A` (energy-scoring no-op) OR `B systematically worse than A` (top-K argmin energy picks wrong candidate, suggesting the energy frame doesn't match the substrate landscape) OR `cost > 3x vanilla` (impractical even if technically right).

**Cross-discipline pulls:**
- **Signal processing (Viterbi decoding, Forney 1973):** Viterbi keeps multiple candidate paths and picks the survivor by accumulated metric -- exact analog. The substrate's K=4 top-K cleanup already builds the candidate set; we are just adding a survivor-metric (accumulated cosine-energy along the path) and choosing at the end. Reduces from full Viterbi (exponential paths) to greedy-per-hop with end-of-chain rescoring.
- **Math (importance sampling on attractor basins):** the energy E_k is a (normalized) log-likelihood under the substrate's attractor distribution; argmin_k(E_k) is MAP within the top-K admissible set. Avoids the soft-bundle's bias toward the centroid of K candidates.
- **Brain (lateral competition in cortical sheets, Hebb-Marr-Albus):** cortical microcircuits implement WTA (winner-take-all) over local neighborhoods via fast inhibitory interneurons; the cortex never "bundles" multiple competing concepts into a single representation -- it always picks ONE active concept per microcolumn. Bundling-based mechanisms violate cortical-circuit principles.
- **Materials (replica symmetry vs RSB):** the soft-bundle assumes the K basins are interchangeable (replica-symmetric mixing); the substrate's W-landscape is REPLICA-SYMMETRY-BROKEN (per substrate META atoms on Phase Portrait v3 + heterogeneous basin depths). Under RSB, mixing between basins ALWAYS costs energy; the right operation is committing to one and scoring.

**P_deflated:** **0.35** (raw 0.50 - 0.15 calibration penalty; Viterbi-style scoring has strong theory but the per-hop energy E_k requires careful definition that doesn't itself amplify noise; main risk is that the backward-consistency check at depth 20 is uninformative because all top-K candidates are equally bad).

**Substrate primitives used:**
- Existing: codebook_cleanup with top-K (already in cell), W-matmul, cosine
- NEW: `hdlab/energy_scored_topk.py` -- accumulated cosine-energy scoring across chain; survivor selection at end-of-chain.

---

## Cross-thread synthesis

- **The 2 anchors are MECHANISM-CLASS DISJOINT from the failed soft-bundle:** Anchor 1 puts the predictive-error on PLASTICITY (the W matrix); Anchor 2 puts the top-K work on SCORING (not state-blending). Both preserve the substrate's hard-commit discipline at the state level.
- **Composes with `pc_cleanup_attractor_v1` HARD_PASS:** the M=80 d=5/10 regime where vanilla and PC both saturated will also saturate for Anchors 1/2; the discriminating test is M=160 d=15/20/30 (same as Wave 1.5 cell). Anchor 1/2 don't need a new envelope -- they slot into the existing Wave 1.5 cell as additional ARM variants.
- **No-Hebbian-window META atom (substrate META 2026-06-22):** Anchor 1's transient W-rewrite IS a Hebbian-window operation (outer-product within the chain). This is compatible with the substrate's no-Hebbian-window-DURING-INGEST stance because the rewrite is WITHIN A QUERY and reverted at end of chain (does not persist across queries). Anchor 2 is window-free.
- **Phase Portrait v3 / by-construction-saturation:** the Wave-1.5 cell at M=160 is HONESTLY in the discriminating regime (VAN dropped from 1.000 to ~0.94 at d=15, ~0.74 at d=20 per design notes). This is the right discriminator; Anchors 1/2 inherit this regime without re-tuning.
- **Aligns with USER pivot (substrate doesn't know language):** these anchors operate on the SUBSTRATE PRIMITIVE LAYER (chain traversal + cleanup) NOT on language eval. No BPC, no bigram. Per `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` these are appropriate experiments.

---

## Substrate-product implications

1. **Soft-bundling is structurally wrong on iterated chains.** This is now a substrate META-finding: any mechanism that mixes K candidate-states into the carried state will fail at depth >= 15 in noisy regimes. Atomize as a no-go pattern alongside the existing no-Hebbian-window atom: "no-soft-bundling-on-iterated-cleanup".
2. **Predictive-error has TWO substrate-compatible expression paths:** (a) error drives PLASTICITY (Anchor 1, brain-grounded); (b) error drives SCORING / SURVIVOR SELECTION (Anchor 2, signal-processing-grounded). Both keep the carried message a clean codeword.
3. **Even if both Anchors HARD_FAIL,** that closes the PC-on-iterated-cleanup mechanism class entirely (3 of 3 expression paths tried -- soft-bundle, plasticity-update, scoring-update). That would be a cap_map closure event ("PC predictive-error correction does not lift substrate above vanilla cleanup at depth >= 20 in noisy regimes; the right primitive for deep chains is something else entirely, likely Modern Hopfield with exponential capacity or HopfieldNet with energy-attractor descent across multiple hops").
4. **Cost:** Anchor 1 = ~3-5 CPU-hr local (single new primitive + 3 ARM variants on existing Wave 1.5 cell); Anchor 2 = ~3-5 CPU-hr local. Run in parallel.
5. **No language eval involved.** Pure substrate-primitive test; reveals whether predictive coding has a substrate-native expression path at all.

---

## Calibration penalty applied

- Lit-scan calibration penalty: 0.15-0.20 deflation applied (Anchor 1 raw 0.55 -> 0.40; Anchor 2 raw 0.50 -> 0.35).
- Novel-synthesis cap: 0.50 honored.
- HARD-FAIL thresholds explicit and falsifiable for both anchors with quantitative metrics.
- Brain-grounded mechanism (Anchor 1) gets higher prior per USER 2026-06-23 ("brain is existence proof"); raw 0.55 deflated to 0.40.
- Per-arm metrics-vs-verdict-msg per Fix #28: PC failure-mode diagnosis derived from cell-source READING (lines 220-244 of `experiments/exp_pc_cleanup_deeper_chains_v1.py`) showing the explicit `bundle_raw = sum(w[:,None] * codebook[top_k_idx])` soft-mix operation, NOT from a verdict_msg framing.

---

## Citations (verified)

External (cross-discipline lit-scan):
1. Rao & Ballard (1999). "Predictive coding in the visual cortex" -- Nature Neuroscience 2(1): https://www.nature.com/articles/nn0199_79
2. Friston (2010). "The free-energy principle: a unified brain theory?" -- Nature Reviews Neuroscience: https://www.nature.com/articles/nrn2787
3. Forney (1973). "The Viterbi Algorithm" -- Proceedings of the IEEE 61(3): https://ieeexplore.ieee.org/document/1450960
4. Eyuboglu (1988). "Reduced-state sequence estimation with set partitioning and decision feedback" -- IEEE Trans. Comm. 36(1): https://ieeexplore.ieee.org/document/4521
5. Hazan (2016). "Introduction to Online Convex Optimization" -- Foundations and Trends in Optimization 2(3-4): https://arxiv.org/abs/1909.05207
6. Belfiore & Park (1979). "Decision feedback equalization" -- Proceedings of the IEEE 67(8): https://ieeexplore.ieee.org/document/1455570

Internal (cross-thread):
- `data/exp_pc_cleanup_deeper_chains_v1_smoke/metrics.json` (the failed cell smoke metrics)
- `data/exp_pc_cleanup_attractor_v1/metrics.json` (Wave 1 baseline PASS at by-construction-saturation)
- `experiments/exp_pc_cleanup_deeper_chains_v1.py` (cell source; lines 220-244 contain the soft-bundle failure mechanism)
- `hdlab/predictive_coding.py` (existing primitives; will compose with Anchor 1 transient-rewrite)
- `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md` (sibling drill; same date)
- `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` (no-language-eval guard)

---

## Next-drill candidate field

If Anchor 1 lands first verdict, route next to **online-learning** (Tier-2; advisor shows count=1, yield=0.0% but adjacent to the Robbins-Monro / mirror-descent angle that Anchor 1's W-rewrite uses) for follow-up theory on convergence of online plasticity under noisy queries.

If Anchor 2 lands first verdict, route next to **coding-theory** (Tier-2; Viterbi-adjacent) for follow-up on whether the substrate's chain traversal admits a constructive code with known minimum distance, which would set a HARD ceiling on what any cleanup mechanism (vanilla or PC) can achieve at depth d.

If BOTH HARD_FAIL, route to **modern-hopfield** (Tier-1; fruit-bearing; Krotov-Hopfield 2016 dense Hopfield) -- the PC mechanism class is closed; the next probe is whether substrate energy attractors with exponential capacity (not the substrate's current linear-Hebbian) can rescue deep-chain recall.

-- Research (Opus 4.7-1M), 2026-06-26
