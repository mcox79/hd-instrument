# Research: 3x deep drill on character-level LM recapture for HD/VSA hybrid

Date: 2026-06-17
Topic: charLM_HD_hybrid_recapture_3x
Trigger: Tier-6 charLM Shakespeare FULL hybrid_BPC ~3.62 MIDDLE_BAND; substantial improvement needed.

## (a) HEADLINE

Char-level LM SOTA on Shakespeare/enwik8 sits at BPC ~0.94-1.06 for dense small models (22-235M params) using the stack (depth + aux losses + segment-recurrence + RoPE/ALiBi + AdamW-cosine + tied embeddings + length-curriculum). Published HD/VSA work is concentrated on CLASSIFICATION (Najafabadi 2016 n-gram-of-letters language ID; HyperEmbed 2021) and on REASONING back-ends (Hersche 2023 NVSA; Frady-Sommer resonators); ZERO published autoregressive character LM uses VSA binding or resonator decoding and reports BPC. The substrate's current hybrid_BPC ~3.62 is ~2.5+ BPC above what dense baselines achieve, indicating the hybrid is likely under-trained or mis-specified at the architectural seam rather than fundamentally capacity-limited; the gap is large enough that BASELINE-stack improvements dominate exotic VSA-binding inventions. Best-bet candidates: (i) port length-curriculum + RoPE + tied-embeddings + AdamW-cosine to the hybrid trunk; (ii) reposition HD binding as a hierarchical chunk-pooler (Charformer/CANINE/MEGABYTE-style patching) rather than as a token-level attention substitute; (iii) add resonator-decoder cleanup as auxiliary head. Method-contingent framing: every threshold below is conditional on Shakespeare corpus + N=1024 HD dim + char vocab ~65 + current trunk architecture.

## (b) Cheap decisive test

Two-stage, each <2 hours laptop CPU:

STAGE 1 (baseline-recapture, NO HD): Train a vanilla 6-layer char-transformer on Shakespeare with the canonical small-LM stack (AdamW + cosine warmup + RoPE + tied embeddings + length-curriculum short-to-long 64->256->512 tokens). Measure BPC.

STAGE 2 (hybrid wire-in): Take the trained Stage-1 backbone and inject the HD/FHRR binding as (a) a chunk-pooling layer between layers 2 and 3, replacing 1 transformer block, and (b) a resonator-decoder auxiliary loss aligned to character n-gram bundles. Measure hybrid_BPC.

Decision: Stage-1 BPC IS the recapture target floor. If Stage-2 hybrid is within +0.05 BPC of Stage-1 baseline, the HD wire-in is structurally healthy and we drill on HD-as-information-bottleneck. If Stage-2 is more than +0.20 BPC worse, the HD seam is the dominant loss source and we redesign the seam, not the trunk.

## (c) Falsifiable predictions

HARD-PASS thresholds (any ONE triggers escalation):
- Stage-1 vanilla char-transformer reaches BPC <= 1.50 on Shakespeare with <100K parameters (deflated from published ~1.06 enwik8 because Shakespeare is harder per char + small-model + char vocab ~65 + cold-start tuning).
- Stage-2 hybrid hybrid_BPC <= 1.70 (within +0.20 of vanilla baseline) -- proves HD seam non-pathological.
- Replacing self-attention block with HD circular-convolution chunk-pooler at one layer drops parameter count >25% without raising BPC by >0.10.

HARD-FAIL thresholds (any ONE refutes that-line architectural choice):
- Stage-1 vanilla baseline BPC > 2.50 on Shakespeare with the published stack: trunk hyperparameters are mis-specified; HD discussion is premature.
- Stage-2 hybrid_BPC > 3.00 even AFTER Stage-1 is healthy: HD seam is fundamentally lossy at this N=1024; need larger N or different binding (FHRR over HRR, BSC over FHRR).
- Resonator-decoder auxiliary loss does NOT improve hybrid_BPC after 10 epochs of joint training: HD output decoder is not extractable bottleneck.

Calibration penalty applied: deflate P(Stage-1 hits <=1.50) from naive 0.70 to 0.50; deflate P(Stage-2 within +0.20) to 0.35; novel-synthesis HD-as-bottleneck capped at 0.45 per [[feedback-lit-scan-calibration-penalty]].

## (d) Cross-thread synthesis

The substrate's hybrid_BPC ~3.62 places it in a regime no published work occupies (no other team trains char-LM with HRR/FHRR binding as a load-bearing block). The convergent message across all three angles:

- Angle 1 (HD/VSA hybrids): NO published autoregressive char-LM uses VSA binding. Closest precedents (Najafabadi 2016, HyperEmbed 2021, NVSA Hersche 2023) treat HDC as classification prototype or reasoning back-end, NOT as generative sequence head. The substrate's hybrid is in an under-explored space, which means the right comparator is not "HDC LM SOTA" (doesn't exist) but "BPC delta vs the substrate's own vanilla baseline."

- Angle 2 (char-LM): SOTA stack is well-characterized; depth + segment-recurrence + RoPE/ALiBi + length-curriculum + tied embeddings + AdamW-cosine. fastText (Bojanowski 2017) is the closest existing analog to HD bundling -- additive composition of hashed char n-grams works as an embedding but is untested as the LM generative chunk. Charformer GBST (Tay 2022) and CANINE (Clark 2021) are structurally bind-and-bundle -- they are the right architectural precedent for HD-as-chunk-pooler.

- Angle 3 (BPC tricks): the highest-leverage cheap wins for small models are mu-P (HP transfer), AdamW + cosine, RoPE/ALiBi, tied embeddings, length-curriculum, weight decay 0.1-0.2 + dropout 0.1-0.2, and (if compute-bound) Sophia second-order. MoE is NOT useful at char level. SSM (Mamba) is competitive with deep transformers at fewer params on char-level data.

Synthesis: the substrate's gap to published char-LM (~2.5+ BPC above SOTA on similar-scale benchmarks) is too large to be explained by the HD seam alone. Trunk-stack basics dominate. The HD/VSA literature DOES support repositioning HD binding as a hierarchical chunk-pooler (Charformer/CANINE/MEGABYTE-analog) rather than as a self-attention substitute -- that placement is precedented by Kim 2016 CharCNN, Bojanowski 2017 fastText, Tay 2022 Charformer, Clark 2021 CANINE.

## (e) Substrate-product implications

Candidate architectural changes ranked by P(gain) x cheapness, method-contingent on Shakespeare + N=1024:

1. (TIER-1, cheapest, highest-P) Adopt the canonical small-LM training stack on the existing hybrid trunk: AdamW + cosine warmup + RoPE positional + tied char embeddings + length-curriculum short-to-long + dropout 0.1-0.2 + weight decay 0.1. Expected: large BPC drop independent of HD seam quality. P=0.55 (deflated).

2. (TIER-1) Length-curriculum specifically: start ctx=64 then 128 then 256 then 512. Strong empirical effect for char-level, cheap. P=0.50.

3. (TIER-2, architectural) Reposition HD binding as a between-layer chunk-pooler (replace 1 transformer block with circular-convolution bind-and-bundle of k=4 char hypervectors -> 1 chunk hypervector, attend at chunk level). Architectural precedent: Charformer GBST, CANINE down-sample, MEGABYTE patch. P=0.40 (novel-synthesis cap).

4. (TIER-2) Add resonator-decoder auxiliary loss aligned to character n-gram bundles; supplies symbolic-recovery training signal that may unstick a stuck hybrid. Precedent: Hersche 2023 NVSA back-end; Frady-Sommer factorization. P=0.35.

5. (TIER-3, structural) If HD seam remains lossy after 1-4, consider raising N from 1024 -> 4096 OR switching binding from FHRR to MAP/BSC; capacity envelope is METHOD/CONFIG-contingent per the USER-LOCKED measured-bounds rule. P=0.30 conditional on 1-4 failing.

These are exp_dev-actionable. A companion hand-off file is filed at notes/exp_dev_handoff_research_charLM_HD_hybrid_recapture_2026-06-17.md.

## (f) Citations (verified count: 24)

HD/VSA + neural LM hybrid:
- Plate 1995, Holographic Reduced Representations, IEEE TNN.
- Schlegel, Neubert, Protzel 2022, A Comparison of Vector Symbolic Architectures, arXiv 2111.06077.
- Kleyko et al. 2022 two-part survey, arXiv 2112.15424.
- Najafabadi, Rahimi, Kanerva, Rabaey 2016, HDC for Text Classification, DATE 2016.
- Alonso, Shridhar, Kleyko, Osipov, Liwicki 2021, HyperEmbed, IJCNN 2021.
- Hersche, Zeqiri, Benini, Sebastian, Rahimi 2023, NVSA for RPM, Nature Machine Intelligence.
- Frady, Kent, Olshausen, Sommer 2020, Resonator Networks, Neural Computation.
- Garcez and Lamb 2023, Neurosymbolic AI 3rd Wave, Artificial Intelligence Review.

Char-level LM and tokenization:
- Sennrich, Haddow, Birch 2016, BPE, ACL.
- Kudo 2018, Subword Regularization, ACL.
- Kudo and Richardson 2018, SentencePiece, EMNLP.
- Kim, Jernite, Sontag, Rush 2016, Character-Aware Neural LMs, AAAI.
- Bojanowski et al. 2017, fastText, TACL.
- Al-Rfou et al. 2018/2019, Char-Level Deeper Self-Attention, AAAI.
- Dai et al. 2019, Transformer-XL, ACL.
- Clark et al. 2021, CANINE, TACL.
- Xue et al. 2022, ByT5, TACL.
- Tay et al. 2022, Charformer GBST, ICLR.
- Yu et al. 2023, MEGABYTE, arXiv 2305.07185.
- Wang, Gangavarapu, Yan, Rush 2024, MambaByte, COLM.

BPC/perplexity techniques:
- Loshchilov and Hutter 2017, AdamW, ICLR 2019.
- Liu et al. 2023, Sophia, arXiv 2305.14342.
- Press et al. 2022, ALiBi, ICLR.
- Su et al. 2021, RoPE, arXiv 2104.09864.
- Yang et al. 2021/2022, mu-Parametrization, NeurIPS.
- Press and Wolf 2017, Tied Embeddings, EACL.
- Gu and Dao 2023, Mamba, arXiv 2312.00752.
- Bengio et al. 2009, Curriculum Learning, ICML.
