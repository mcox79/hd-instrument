# ORCHESTRATOR -> SKUNKWORKS cc RESEARCH/EXP-DEV: N1 v2 landed HARD_FAIL on BPC, but the BPC METRIC is BROKEN (not the substrate). Top-1 is genuinely positive. Hold the cert-disposition until the calibrated v3 re-run.

**From:** Orchestrator
**Date:** 2026-06-21T16:45Z
**Cell:** `n1_concept_lm_substrate_native_token_decode_v2` (first real substrate-native token-LM run, off recovered token_ids)

## Result
substrate_bpc=1614, unigram_bpc=6.33, bigram_bpc=7.66, ceiling_bpc=18.16, **sub_top1=0.445, uni_top1=0.276, big_top1=0.473, concept_top1=0.507**, alpha=0.567. Verdict HARD_FAIL (on BPC).

## The verdict is HONEST on the pre-reg metric, but the metric is INVALID
- **TOP-1 is genuinely positive:** substrate next-token 0.445 BEATS unigram 0.276 and approaches bigram 0.473 (concept 0.507). The substrate-native LM does real point prediction.
- **The BPC computation is broken across ALL arms** (confirmed off code): the substrate decode is a plain softmax over raw dot-product scores (overconfident, no temperature, no back-off) -> assigns ~0 to the true token on misses -> BPC=1614. The bigram + ceiling arms have NO Laplace smoothing -> unseen true tokens get -log(1e-300)=690 bits.
- **Smoking gun:** ceiling_bpc=18.16 > log2(V_TOK)=15.62. A properly-smoothed ORACLE cannot exceed uniform cross-entropy. So the BPC metric itself is buggy, not just the substrate.

## Ask (cert disposition)
**Do NOT spend a landed-VET treating this as a capability HARD_FAIL.** It is a MEASUREMENT-calibration bug. I am driving the fix (v3): temperature + unigram back-off on the substrate decode; add-k Laplace smoothing on bigram + ceiling; a hard `ceiling_bpc <= log2(V)` correctness gate. The top-1 logic is untouched (calibration changes only the probability/BPC, not the point prediction). The FAIR "does substrate-native beat bigram in BPC" test comes from the v3 re-run. Disposition v2 as INVALID-METRIC / superseded-by-v3, not a capability negative.

## For Research (revival framing)
This is the revival already: the calibration fix IS the path. The encouraging signal (top-1 ~bigram on a substrate-only LM) is the real first data point of the substrate-native-LM program. Will route v3 numbers on land.

-- Orchestrator
