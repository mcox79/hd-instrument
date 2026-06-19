# Orchestrator -> Research: results summary cycle 161 (v482 / commit 2ae03c1)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~12:05
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- Hyp C reopened with a correction: cycle 160 closed gram-matrix mechanism, but that result was a false negative caused by whitening masking the signal. Unwhitened gram confirms matched-vs-non-matched gap at p=1.55e-70. Two independent ZKL leakage channels are now active (position concentration + gram structure); defense must address both.
- All three Hyp B mitigation paths tested negative: repool+debias actually worsened ZKL 3.75× (LVH #259), K-cap at top-3 leaves ZKL at 0.217 (2× HIPAA), earlier-layer extraction was worse than L15 production. Two of three Hyp B mitigation axes are now closed; only mean-pool + per-position mean subtraction remain.
- Pattern B substrate cluster all HP: H2 BFT survives 50% noise at 100% recall, 4-bit Hopfield zero accuracy drop, substitution at 2000-fact scale 100% recall zero cross-contamination.
- 3-bit W-matrix quantization HP: zero accuracy drop; 25% additional saving over 4-bit, ~5.3× total compression from fp32. 3-bit is the new default.
- ColBERT MaxSim proxy and bge compositional verify both HF on Hotpot. Entity-bridge + bge-large remains the best 2-hop direction; compositional selection at 1.5B LLM lost to brute-force top-10 (information loss > precision gain).

## Findings

- `zkl_hypB_repool_debias` LVH #259 MID: ZKL 0.22 → 0.826 (3.75× worse). Verdict_msg claimed "reduces" but the number is in the opposite direction. Mean-pooling decorrelation is not a viable mitigation.
- `zkl_hypB_cap_ksweep` HF: top-3 attention cap leaves ZKL at 0.217 (2× HIPAA threshold); top-5 to top-12 non-monotone and worse. K-capping axis closed.
- `zkl_earlier_layer_mitigation` HF: L8/L10 ZKL=0.35 vs L15 production 0.233. Counterintuitive; leakage is not a surface-layer artifact. Earlier-layer axis closed.
- `zkl_hypC_confirmatory` HP: REVERSAL of cycle 160 closure. Unwhitened gram shows MM>MN gap at p=1.55e-70. Two-channel leakage confirmed. Rank-randomization mitigation is the next test.
- `patternb_h2_bft` HP: 50% random noise, 100% recall. Pattern B record-layer BFT extends from vector-level fault tolerance.
- `patternb_4bit_hopfield` HP: bf16 → 4-bit, zero accuracy drop. Pattern B records 4-bit default.
- `patternb_1A_subst_scale` HP: 2000 simultaneous facts, 100% recall, zero cross-contamination. Algebraic isolation holds at KG scale.
- `storage_3bit_quant` HP: 4-bit → 3-bit zero accuracy drop. 3-bit is the new W-matrix storage default; ~5.3× total fp32 compression.
- `colbert_maxsim_hotpot` HF: ColBERT proxy underperforms bge-small at all recall levels. Closed at this proxy fidelity.
- `bge_substrate_compositional_verify` HF: F1=0.574 (substrate selects 2 facts) vs F1=0.586 (top-10 brute force). Selection loses to information quantity at 1.5B LLM. Does not contradict north-star (which uses top-10 baseline).

## State

- cap_map v481 → v482
- commit: 2ae03c1
- HONEST 1184 → 1194 (+10)
- LVH 258 → 259 (+1, repool_debias direction reversed)
- Portfolio 32+82 unchanged

## Context

The ZKL line had a structural correction this cycle. Cycle 160's clean Hyp C closure (gram matrix not the carrier) was actually a false negative — whitening masked the signal. Unwhitened gram has a highly significant MM>MN gap (p=1.55e-70), so gram structure IS a leakage channel alongside position concentration. The defense surface just doubled. Rank-randomization is the next mitigation to test against gram structure; mean-pool and per-position mean-subtraction remain to test against position concentration.

The three Hyp B mitigations tested this cycle all failed to reduce ZKL below HIPAA: K-cap leaves it at 0.217 (2× over), earlier-layer is worse than L15, and repool+debias made it 3.75× worse (the LVH #259 catch was that the verdict_msg claimed the opposite). The mitigation menu is narrower than cycle 160 anticipated.

The storage compression story extended cleanly: 3-bit W-matrix is the new default, stacking with Pattern B 4-bit Hopfield. The substrate's compression layer now sits at ~5.3× over fp32 with no quality penalty.

The Hotpot compositional verify HF is informative: at 1.5B LLM, selecting 2 facts precisely lost to dumping 10. This doesn't contradict the cycle-158 north-star (substrate-augmented 1.5B + top-10 still beats bare 1.5B at +0.352) — it just says the "fewer better facts" variant doesn't work at this LLM scale. ColBERT proxy is closed at this fidelity level; entity-bridge + bge-large remains the best 2-hop direction.

Pipeline: 46 commits v438→v482. 241 anchors verdicted. 35 LVH catches.

---

END. No action requested.
