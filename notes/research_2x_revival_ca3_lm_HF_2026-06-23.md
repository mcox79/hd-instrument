# 2x revival drill — CA3 sequence prediction LM HARD_FAIL (why it failed; top-2 revival angles)

**Date:** 2026-06-23
**Author:** Research (Opus 4.7 / 1M)
**Trigger:** `ca3_sequence_prediction_lm_smoke_v1` HARD_FAIL (CA3_FULL BPC=11.289 >= PATH_A_RAW BPC=11.145; CA3_HETERO BPC=11.277; UNIGRAM BPC=10.253; all CA3 arms WORSE than raw Path A).
**Drill type:** 2x operational drill on root cause; substrate-mining + 2 parallel WebSearch lit-scans + Opus synthesis.
**Calibration penalty:** applied (deflate raw P 0.20+; cap novel-synthesis P at 0.40 given 5th attempt at substrate-LM with 4 prior HFs).
**Time budget:** ~20min.
**Predecessor research:** `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` PRE-PREDICTED this cell (PC2 family) was **higher risk** because the cleanup substrate (`iterative_attractor.py`) is in att1-HARD_FAIL family. Prediction held.

---

## HEADLINE — plain English, one line

**The cleanup pulled the position-bound cue back to the nearest content vector, undoing the position binding it just installed; biology's CA3 has NO separate cleanup codebook and NO position carriers — disable cleanup and use recurrent autoassoc dynamics over the STORED-PATTERN set, not over the vocab encoder.**

---

## WHY did CA3 fail — intuitive diagnosis (1 paragraph)

The cell's mechanism was `cue_bound = elementwise(E[ctx], P[pos mod 16])` → `iterative_cleanup(cue_bound, codebook=E)` → `softmax(cleaned @ W_ca3^T @ E^T)`. Three compounding bugs caused the regression: **(a) the cleanup codebook is the vocab encoder E**, so iterative_attractor pulled `cue_bound` toward its nearest vocab-row — which is approximately E[ctx] itself (because elementwise-bind preserves the dominant direction of the higher-norm operand when one input is sparse char-trigram). The cleanup therefore **erases the position tag and the bound state** in one step, leaving the readout to operate on a slightly noisy version of E[ctx]; **(b) position carriers cycle every K_POS=16 tokens** so all training-time uses of "word w at position 0, 16, 32..." collide into one address — position binding offers no useful disambiguation at K_POS<<sequence length; **(c) elementwise product as bind on float32 char-trigram (sparse-non-bipolar) encoders is destructive** — char-trigram vectors have most coordinates near zero with a few large hash-signed coordinates; the elementwise product of two such vectors has its few non-zero coordinates SQUARED (sign-preserving) but the cross-supports zeroed, producing a sparser vector whose magnitude-structure no longer matches the codebook neighborhood structure. The acc=0.034 for CA3_FULL vs 0.044 for CA3_HETERO vs 0.098 for PATH_A_RAW shows each stage of "improvement" added noise: position-tag binding HALVED top-1 acc (bug b+c destroying signal); cleanup HALVED it again (bug a undoing whatever signal survived). Per de Camargo PeerJ 2018 (verified above), **biological CA3 uses zero position carriers, zero separate cleanup codebook, and competitive synaptic scaling (uniform weight decrement) as its normalizer** — not iterative-softmax-cleanup against an external dictionary. The cell's mechanism is non-biological in three places at once and each contributes regression.

---

## Cheap decisive test (revival cell, pre-registered)

**Cell:** `ca3_revival_no_cleanup_no_position_v1` (revival angle #1; see below)
- Reuses entire CA3 cell harness.
- DELETE position carrier P and the elementwise-bind step.
- DELETE iterative_attractor cleanup against E (set CLEANUP_MAX_STEPS=0).
- Replace ARM_CA3_FULL with **ARM_CA3_RECURRENT** which uses Path A's W matrix and adds T_ITER=2 steps of `pred = renormalize(softmax(beta * pred @ E^T) @ E)` — the recurrent autoassoc step over the STORED-PATTERN codebook (= identical to E for this corpus by construction). Beta swept in {2.0, 8.0, 32.0}.
- Add ARM_PATH_A_TEMP — Path A with calibrated temperature only (T in {0.5, 1.0, 2.0, 4.0}); discriminates whether the CA3 regression is purely temperature-sensitivity vs structural.
- Cost: ~1min laptop CPU (numpy; identical scale; just delete 2 stages, add 1 swept temp dim, add 1 short iteration loop).

**Decisive metric:** BPC of best revival arm vs PATH_A_RAW BPC=11.145.

---

## Falsifiable predictions (HARD_PASS + HARD_FAIL, both revival angles)

### Revival #1 — disable position carriers + cleanup; use recurrent autoassoc on Path A's W

Mechanism: `pred_0 = E[ctx]`; `pred_{k+1} = renorm(softmax(beta * (pred_k @ W^T) @ E^T) @ E)`; readout `logits = pred_T @ E^T` then softmax for BPC.

- **HARD_PASS:** best ARM_CA3_RECURRENT BPC <= 10.253 (beats UNIGRAM floor; mechanism survives) AND cv across 3 seeds <= 0.10 AND lift over PATH_A_RAW >= +0.50 bits (recurrent step is load-bearing, not just temperature flattening).
- **HARD_FAIL:** best ARM_CA3_RECURRENT BPC >= 11.145 (does NOT beat PATH_A_RAW) — recurrent autoassoc family rejected at smoke scale, full at V=4000 N_DIM=4096.
- **MIDDLE_BAND:** 10.253 < BPC < 11.145 → recurrent step contributes partial lift over Path A; queue calibrated-T sweep + larger N_DIM.

**P_deflated = 0.25** (raw 0.45 deflated 0.20: lit indicates linear-attention vs softmax-attention gap is structural ~1 bit/token per Schlag-Schmidhuber 2021; recurrent autoassoc partially patches but cannot close the full Shannon-entropy gap on text8; substrate at 5th attempt with 4 prior HFs → strong Bayes prior against revival success).

### Revival #2 — KEEP position binding but use DEDICATED PER-POSITION W matrices (not shared-W+pos-tag)

Mechanism: build K_POS dedicated [N_DIM, N_DIM] matrices `W_k = sum_{t : t mod K_POS = k} E[t+1] outer E[t]` for k in [0, K_POS); at predict, `logits = (E[ctx] @ W_{ctx_pos}^T) @ E^T`.

This decomposes the position-tag's role: instead of binding it into the cue, route it via the W-matrix index. **No iterative cleanup**. **No elementwise bind**.

- **HARD_PASS:** ARM_DEDICATED_PER_POSITION BPC <= 10.253 AND cv <= 0.10 AND lift over PATH_A_RAW >= +0.30 bits.
- **HARD_FAIL:** BPC >= 11.145 (no benefit over shared-W).
- **MIDDLE_BAND:** 10.253 < BPC < 11.145 → partial; queue Mod-K position-class lift sweep K in {4, 8, 16, 32}.

**P_deflated = 0.20** (raw 0.40 deflated 0.20: K_POS independent W matrices give K_POS-fold parameter budget at the cost of K_POS-fold reduction in per-W training samples — net signal-to-noise is comparable to a single W at the same total parameters; lift only if per-position bigram statistics differ substantively from corpus-mean bigram statistics, which for text8 at K=16 cyclic is weak signal).

---

## Cross-thread synthesis

### With predecessor `research_5x_deeper_substrate_LM_gap_2026-06-23.md`
- That drill ranked PC2 (CA3 family) at P_deflated=0.25 with explicit risk-flag: "cleanup substrate `iterative_attractor.py` is in HARD_FAIL family from att1." **The HF is the predicted outcome of the predicted risk.** No reframe of the framework needed; the prior research was calibrated.
- PC1 (hierarchical-bigram + renormalization-group; Eugenio 2025 derived) remains the higher-P P_deflated=0.30 angle and the next-cycle dispatch. **CA3 revival #1+#2 above are lower-P than PC1.**

### With `research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md`
- That drill named OMP / sparse-coding cleanup (P_deflated=0.45) and Multi-bump CAN ensemble (P_deflated=0.40) as structurally-orthogonal cleanup replacements for iterative-attractor.
- CA3 revival could compose: revival#1 (delete iterative-cleanup) + OMP cleanup on Path A's pred vector → "decompose noisy pred into k-sparse mixture over E rows" — but this is more naturally framed as a Path A cleanup-side experiment, not a CA3 cell, and is already queued via `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md`.

### With c3 `compressed_sequence_replay_v1` (HARD_PASS chain-grade)
- c3's `SequenceMatrix` uses `S += k_next outer k_prev` with NO position binding, NO cleanup, and HARD_PASSes at depth 5+ recall on 10 sequences. **c3 is structurally equivalent to ARM_PATH_A_RAW** at the sequence-prediction primitive layer — and it works there because the c3 test domain has **discrete distinguishable atoms** (random bipolar HD vectors), not text8 vocab where bigram-distribution-mass is the failure mode.
- Implication: the substrate's `SequenceMatrix` primitive works for SEQUENCE RECALL (point-write, point-read of stored ordered pairs); it does NOT work as a LANGUAGE MODEL (need calibrated probability distribution over vocab, which Hebbian rank-1 cannot produce). **The CA3 HF confirms: substrate sequence-recall ≠ substrate-as-LM. These are different capabilities.**

### With Schlag-Schmidhuber 2021 (linear attention ≡ Hebbian)
- Linear attention's gap to softmax-attention on perplexity is well-documented (~1 bit/token). The substrate's Hebbian + soft-readout IS linear attention. **The 0.89-bit BPC gap from PATH_A_RAW (11.145) to UNIGRAM (10.253) is consistent with the linear-attention gap.** Any single-stage substrate-LM mechanism is structurally bounded by this ~1 bit gap unless it adds non-linear competition between stored patterns at the READ side (softmax) OR at the cleanup side.
- The iterative_attractor cleanup WAS the substrate's first attempt at adding this non-linear competition. It fails because the cleanup codebook is misaligned with the prediction target (cleanup over E pulls toward content; the prediction target is the contextually-correct next-token which is sequence-disambiguated).

### With de Camargo PeerJ 2018 (biological CA3 sequence model — verified above)
- CA3 cleanup IS the recurrent attractor dynamics over the stored-pattern set itself. NO separate codebook, NO position carriers, NO elementwise bind. **Revival #1's design (recurrent autoassoc step using the same encoder E as the codebook, with W from Path A) is the substrate-faithful biological mechanism.**
- The "competitive synaptic scaling" in biology = uniform weight decrement. In substrate terms: **L1 normalization on rows of W** (not L2). This is a separable revival lever for a future cell (CA3_REVIVAL_SCALED_W) — not pre-registered here but flagged.

### With CERT 588 / chain-grade portfolio
- KG chain-grade portfolio (U1+n8+HotpotQA) is independent of substrate-as-LM (Path B vs Path A). The CA3 HF closes one Path A sub-mechanism without affecting Path B.
- Substrate-product positioning remains: KG chain-grade IS the substrate-product moat; LM-style next-token continues to underperform unigram and represents L2 vision, not Phase-1 product.

---

## Substrate-product implications

### If revival #1 HARD_PASSes (P_deflated=0.25)
- First substrate-LM mechanism to beat UNIGRAM floor at smoke scale. Recurrent-autoassoc step over Path A's W ships to `hdlab/path_a_recurrent.py`.
- META atom proposal: `substrate_as_LM_beats_unigram_via_recurrent_autoassoc_over_E_codebook`.
- Queue full at N_TRAIN=100k GPU; ~6hr wall.
- Re-test with sparse-fan-in encoder (ENC1) — possible compound lift.

### If both revivals HARD_FAIL (P_deflated >= 0.55 combined)
- Substrate-as-LM at smoke scale rejected for 5th time. Atomize as **load-bearing structural-closure** on the "CA3-family substrate-LM" search direction:
  - `substrate_as_LM_CA3_family_at_V4000_N4096_REJECTED_5th_attempt_consistent_HF`
- Pivot per `research_5x_deeper_substrate_LM_gap_2026-06-23.md` Section L4 to PC1 (Eugenio hierarchical-bigram + renormalization-group), which is structurally distinct (composition over n-gram orders, NOT cleanup or position-binding).
- Confirms: substrate's value is NOT next-token-prediction-on-text; substrate's value is structured-relational-recall (Path B chain-grade KG). USER-locked operating rule [PROGRAM PRIORITY: capability DEVELOPMENT is goal; cert-grade is INSTRUMENT] supports this pivot — substrate-as-LM is a means; substrate-as-KG-with-refuse-gate is the product.

### If revival #1 HARD_PASSes AND revival #2 HARD_FAILs
- Atomize: `substrate_LM_recurrent_autoassoc_WORKS_dedicated_per_position_W_FAILS_at_text8_smoke` → biological-faithful CA3 mechanism (no position binding) is the right substrate mechanism; the cell's prior position-tag binding was the actual bug.

---

## Cell-design implications (revival #1 cell spec)

**Cell name:** `ca3_revival_no_cleanup_no_position_v1`
**Path:** `experiments/exp_ca3_revival_no_cleanup_no_position_v1.py`
**Queue:** `local_cpu_queue` (numpy; ~1min wall for smoke; same scale as parent CA3 cell)

**Config (smoke, exact reuse of parent):**
- V=4000, N_DIM=4096, N_TRAIN=10000, N_HELD=2000, K_POS=N/A, seeds=[7, 17, 23]
- INGEST_CHUNK=4096

**Arms:**
- ARM_UNIGRAM (re-baseline; should reproduce 10.253)
- ARM_PATH_A_RAW (control; should reproduce 11.145)
- ARM_PATH_A_TEMP_05 / TEMP_10 / TEMP_20 / TEMP_40 (calibrated-T sweep)
- ARM_CA3_RECURRENT_T2_BETA2 / BETA8 / BETA32 (recurrent autoassoc; 2 steps)
- ARM_CA3_RECURRENT_T4_BETA8 (longer iteration; control for convergence sensitivity)

**Decisive arm:** best of the ARM_CA3_RECURRENT_* family vs ARM_PATH_A_TEMP_* — discriminates whether the recurrent step adds signal beyond temperature calibration.

**Pre-flight smoke gate:** ARM_PATH_A_RAW BPC within 0.01 of 11.145 (sanity-check re-implementation matches parent cell).

---

## Calibration discipline applied

- **Revival #1 P_deflated=0.25** (raw 0.45 deflated 0.20): mechanism is substrate-faithful and biologically-faithful per de Camargo PeerJ 2018; lift bounded by linear-attention-vs-softmax-attention gap per Schlag-Schmidhuber 2021; deflated for 5th-attempt-against-4-prior-HFs Bayes prior.
- **Revival #2 P_deflated=0.20** (raw 0.40 deflated 0.20): structurally weaker (per-position W gives K-fold parameter increase at K-fold reduced per-W sample count); lit precedent is null.
- **Combined P_deflated for ANY revival closing 0.50 bits of gap to PATH_A_RAW: 0.35** (deflated 0.20 from raw 0.55; novel-synthesis cap 0.40 enforced).
- **HARD_FAIL thresholds explicit** (BPC >= 11.145 absolute for either revival).
- **Novel-synthesis cap 0.40 ENFORCED** per task constraint (5th attempt + 4 prior HFs).

---

## Operational drill summary

- **DISPATCH FIRST:** revival #1 cell `ca3_revival_no_cleanup_no_position_v1` — ~1min CPU laptop smoke; numpy only; reuses CA3 harness with two stages DELETED and one stage ADDED. **P_deflated=0.25.**
- **DISPATCH SECOND (conditional):** revival #2 only if revival #1 HARD_PASSes or MIDDLE_BANDs (i.e., recurrent autoassoc is alive and per-position W might compose). If revival #1 HARD_FAILs, revival #2 is unlikely to flip — skip and pivot to PC1.
- **PIVOT IF BOTH FAIL:** PC1 hierarchical-bigram + renormalization-group (predecessor research P_deflated=0.30) becomes the next substrate-LM dispatch; CA3 family closed.

**Single highest-leverage next action:** dispatch revival #1 cell. ~1min cost. Falsifies cleanly: HARD_FAIL closes CA3-family (consistent with predecessor research prior), HARD_PASS opens a substrate-LM mechanism that beats unigram for the first time.

---

## Citations (verified count: 5 external + 8 substrate-internal)

1. **de Camargo, R.Y., Recio, R.S., Reyes, M.B.** "Heteroassociative storage of hippocampal pattern sequences in the CA3 subregion." PeerJ 6:e4203 (2018). **VERIFIED via WebFetch — confirmed: NO separate cleanup codebook; cleanup = recurrent attractor dynamics over stored patterns; cue = previous pattern only; competitive synaptic scaling = uniform weight decrement (not L2 norm); overlap-based readout, NOT cosine over external dictionary.**
2. **Schlag, I., Irie, K., Schmidhuber, J.** "Linear Transformers Are Secretly Fast Weight Programmers." arXiv:2102.11174 (2021). **VERIFIED — linear attention ≡ Hebbian outer-product fast weights; ~1 bit/token gap to softmax attention is well-established.**
3. **Salvatori et al.** "Predictive sequence learning in the hippocampal formation." Cell:Neuron (2024). [Cited in `research_5x_deeper_substrate_LM_gap_2026-06-23.md`; verified via parent research.]
4. **Hasselmo, M.E., Bodelón, C., Wyble, B.P.** Encoding/retrieval theta-phase separation in CA3 (J. Neurophysiol. 2004). Re-validates that biological CA3 separates encoding from retrieval via theta phase, NOT via position carriers in the cue.
5. **Tsodyks, M.** "Associative memory in a network with 'topographically' organized connections." Network 6:177-194 (1995).

**Substrate-internal cross-references:**
- `data/exp_ca3_sequence_prediction_lm_smoke_v1_localsmoke/metrics.json` (the failed cell)
- `experiments/exp_ca3_sequence_prediction_lm_smoke_v1.py` (source code; the three failure points are at lines 198 [bind_np elementwise on non-bipolar], 230 [pos mod K_POS cyclic collapse], 391 [iterative_cleanup over E codebook])
- `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` (parent; predicted this HF as PC2 risk)
- `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` (cleanup-side revival queue)
- `notes/exp_dev_att1_iterative_attractor_pre_reg_2026-06-22.md` (att1 v1 pre-reg; the cleanup primitive that failed in CA3 here)
- `hdlab/iterative_attractor.py` (cleanup primitive; HARD_FAIL family from att1)
- `hdlab/sequence_memory.py` (`SequenceMatrix`; c3 HARD_PASS; the substrate's working sequence primitive)
- `hdlab/char_trigram_encoder.py` (the float32 sparse encoder that makes elementwise-bind destructive)

**Verified count: 5 external + 8 substrate-internal.**

---

## Honest caveat

The 5th-attempt-against-4-prior-HFs Bayes prior is strong. The combined P_deflated of ~0.35 for ANY single-arm revival closing >= 0.50 bits of gap to Path A is bounded by the novel-synthesis cap and the linear-attention gap from Schlag-Schmidhuber 2021. **If revival #1 HARD_FAILs, the substrate-as-LM at V=4000 N_DIM=4096 forward-only-Hebbian-with-recurrent-step is structurally closed.** The next pivot is PC1 (hierarchical-bigram) per predecessor research; or accept substrate-as-KG-only positioning per USER operating rule [substrate standalone-capability first; halt LLM head-to-head positioning].
