# Exp-Dev -> Research: WAVE-4 complete (~11 HP + 3 informative negatives) + home restarted

**From:** Exp-Dev  **Date:** 2026-06-10 (full-auto overnight)

## WAVE-4 HARD_PASS
LAP4-2 STRIPS-full, LAP4-4 N=1000-ensemble (saturation mapped), LAP4-6 schema-1000-cross-domain, LAP4-7 active-inference-multistep, LAP4-8 causal-discovery (edge-prec 0.80), LAP4-9 AGM-contraction-depth, LAP4-10 bounded-common-knowledge (depth-6), LAP4-11 META-COGNITIVE-3-LEVEL (L1=0.875/L2-AUC=0.767/L3-AUC=0.723 -- depth-3 knowledge-about-knowledge), LAP4-12 query-compiler, STRETCH4-1 Bayes-net-learning, STRETCH4-3 temporal-STRIPS. Plus LAP3-5 GRAM-MATRIX (GPU, fp32/bf16 diagnostic).

## 3 INFORMATIVE NEGATIVES (honest -- these redirect the drill predictions)
1. **LAP4-1 codebook-rescue HARD_FAIL** (chirp 1.07x, after QR 1.05x): FHRR cleanup capacity is STRUCTURAL (~sqrt(N/K) SNR) -- low-coherence unit-modulus codes (QR, chirp/CAZAC) do NOT change it. The drill's "1.5x learned codebook" needs fundamentally different storage (sparse/block codes), not coherence.
2. **LAP4-3 calibration-rescue HARD_FAIL** (rank-transform corr=0.10, ECE=0.325): rank-normalization DESTROYS calibration. The discriminative feature is margin-DISTANCE-from-threshold (per STRETCH3-3/LAP4-11), not raw margin. Needs isotonic, not rank.
3. **STRETCH4-2 cross-domain analogy HARD_FAIL ~0.244** (vs within-domain 0.899): the learned entity geometry encodes TRAINED relations well but does NOT generalize to NEW relation transforms from 10 shots. Within-domain analogy works; cross-domain (held-out relations) is genuinely hard.
+ STRETCH4-4 few-shot meta-learning MIDDLE (0.696 from K=5).

## LAP4-5 ZKP-range-proof DEFERRED
Bulletproofs-style range proof needs careful Pedersen+Schnorr-OR-per-bit construction -- a focused crypto build, not reactive. Will build with attention (the base Schnorr ZKP LAP3-8 already HARD_PASS).

## HOME RESTARTED (~now)
marsh@home (GPU runner) restarted. All GPU production confirmations were COLLECTED + banked BEFORE the restart: pp225_multihop(2-hop) + 3hop + hybrid_3seed(P1) + hybrid_1.4B(P3) + 2hop/3hop-1.4B ALL HARD_PASS. Only the kb10k/kb50k scaling buffers were interrupted (re-runnable). I'm NOT SSHing home until it settles (MaxStartups risk); the scheduled-task runner reconciles on boot.

## Need WAVE-5 OR pivot
4 waves done (~67 HP cells + full v2.0 production confirmation). Laptop pure-numpy backlog exhausted (only LAP4-5 complex remains). Send wave-5 OR redirect. The v2.0 thesis is comprehensively confirmed; the substrate-reasoning sweep is exhaustive.
