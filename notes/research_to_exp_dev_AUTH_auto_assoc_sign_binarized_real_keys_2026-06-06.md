# Research -> Exp-Dev: CONFIRMED -- auto-assoc Hopfield exact-recovery on sign-binarized real keys (re-point one pass)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~16:40
**Re:** exp_dev_to_research_ROOT_CAUSE_unique_value_metric_unusable_2026-06-06.md
**Subject:** CONFIRMED metric = auto-assoc Hopfield exact-recovery on sign(whiten(expand(emb))) for the whole real-encoder capacity family. Re-point in one pass. Dequeue DAMB1 (will read flat). This is THE day's biggest methodology save.

---

## Catch acknowledged -- biggest methodology save of the day

You correctly identified that:
- M_50 censors (catch 1)
- Fixed-load M=2*N also reads 1.0=1.0 (catch 2)
- Root cause is structural: argmax_v over random near-orthogonal values is too easy
- The unique-value hetero recall metric measures VALUE-distinguishability, NOT key-collision capacity
- The ENTIRE real-encoder capacity family using this metric is measuring the wrong quantity

Today's affected verdicts (Slot 9 / Slot 14 / G1 / G8 / G3 / G9 / DAMB1 / DIMSPARSE) are LARGELY METRIC ARTIFACTS, not real findings.

## Spec confirmed: auto-assoc Hopfield exact-recovery on sign-binarized real keys

Architecture:
- Take real-encoder keys: emb in R^N_enc
- Optionally: expand via random-feature lift (phi(x) = sign(Rx); D_eff)
- Optionally: whiten (or not -- whitening is now testable as a clean intervention)
- Sign-binarize: phi_bin = sign(emb_processed) in {-1, +1}^D
- Auto-associative substrate W = sum_i phi_bin_i (phi_bin_i)^T - I * M (zero-diag)
- Retrieval: phi_recovered = sign(W . phi_corrupted) where phi_corrupted = flip(phi_bin_i, FLIP=0.05)
- Capacity metric: M_max = M at which exact-recovery (all bits match) first drops below 0.95

This is the SAME metric Slot 2 / Slot 3 / Slot 10 used (which gave clean, discriminating results). Real-encoder substrate now becomes DIRECTLY COMPARABLE to synthetic.

## Why this is the right move

1. Slot 2 (ETF 8x), Slot 3 (sparse 5-12x), Slot 10 (flat 8x N-sweep) used this metric and gave clean discrimination
2. True capacity ~0.14N (Hopfield 1982) -- well-defined limit
3. Fails SHARPLY past capacity (not gradually) -- clean threshold
4. Sign-binarization preserves the bipolar substrate working assumption
5. Cross-arm comparisons (real vs synthetic; Hadamard vs random; expanded vs base) are apples-to-apples

## Re-point plan

Use hopfield_recall_t (GPU, exact-recovery) from _gpu_cap.py.

Re-point in one pass:
- Slot 9 (real MiniLM whitened) - test capacity at sign-binarized real keys
- Slot 14 (dim-expansion D in {384, 1024, 4096}) - capacity at each D with sign-binarized expanded keys
- G1 (mpnet-768) - capacity at sign-binarized mpnet keys
- G8 (Pythia cross-encoder) - capacity at sign-binarized Pythia keys + expansion
- G3 (N=16384 production) - capacity at production scale
- G9 (N_sub sweep) - capacity ratio across N_sub
- DIMSPARSE (4-arm at sign-binarized real keys) - new compound test
- DAMB1 -- DEQUEUE (would read flat; no value in running on broken metric)

Pre-reg per cell (apples-to-apples with synthetic cells):
- HP: arm M_max >= 1.5x baseline M_max (if at matched dim) OR >= 0.14*D ceiling if at matched-capacity-budget
- MID: 1.10-1.50x
- HF: < 1.10x

## DAMB1 dequeue confirmed

Dequeue DAMB1 -- it would read flat on the broken metric. Once re-pointed, the disambiguation question (H1 vs H2) becomes well-defined again: M_max(real) vs M_max(synthetic) curves at different N_sub.

## What this means for today's strategic conclusions

The HONEST RE-STATEMENT:

Today's reasoning + hallucination + audit + SYNTHETIC capacity stories are SOLID:
- K-hop K=10 N=16384 (29th flagship)
- KF-1 AUC 0.999/0.975 (BAND-LIFT)
- HP-12 V1 cert <1ms
- Slot 2 ETF synthetic 8x
- Slot 3 sparse synthetic 5-7x
- Slot 10 flat 8x across synthetic N

Today's REAL-ENCODER capacity story is UNKNOWN until re-metric'd:
- G8 6.68x (Pythia cross-encoder dim-expansion) - METRIC ARTIFACT
- Slot 9 2.75x (ETF on MiniLM) - METRIC ARTIFACT
- Slot 14 plateau (dim-expansion) - METRIC ARTIFACT
- The "causal LM dominates sentence-transformer" story (built on G8) - WEAKER
- Production LM choice (Llama-3.1-8B vs others) - revisit pending real-encoder verification

3 confirmed axes claim revised: 2 confirmed (synthetic) + 1 unreliable (real-encoder dim-expansion).

## Standing rule for me going forward

When specifying a capacity metric, verify it CAN discriminate by predicting where it should fail. M_50 unique-value cannot fail at reasonable loads on the substrate's capacity range. I should have predicted this before specifying.

Adding to BRIEF + memory: **always pressure-test capacity metrics by asking "where does this metric fail empirically, and is that within the substrate's operating range?" If not, the metric is too lenient.**

---

**END.**

**Exp-Dev:** GREEN LIGHT on auto-assoc Hopfield exact-recovery on sign(whiten(expand(real_keys))). Re-point capacity family in one pass. DAMB1 DEQUEUE. Use hopfield_recall_t. ~3-4h to re-run the family. This is the day's biggest methodology save -- thank you for not letting it ship.

**User:** Exp-Dev caught that even the fixed-load recall metric I specified earlier doesn't discriminate -- value-argmax is too easy. Real-encoder capacity family verdicts today (Slot 9 / 14 / G1 / G8 / G3 / G9 / DIMSPARSE) are LARGELY METRIC ARTIFACTS. The "causal-LM substrate dominates" story from G8 may be wrong; needs re-verification. SOLID stories that hold: K-hop K=10 reasoning, KF-1 hallucination AUC, HP-12 audit, synthetic Hadamard/sparse capacity (different metric). Re-pointing to auto-assoc Hopfield exact-recovery on sign-binarized real keys -- same metric as the trustworthy synthetic cells. ~3-4h to re-run. Today's compound-math story is now UNKNOWN pending re-run; algebraic ceiling per Drill W still 20-40x compound (most defensible estimate). This is Exp-Dev's 6th methodology save today; without it, we'd have multiple wrong strategic conclusions on the books.
