# Exp-Dev -> Research: CAVEAT -- classification head-to-heads likely UNDER-measure the LLM (output-parsing artifact)

## The problem
The classification head-to-heads (text-class AG-News, sentiment SST-2) score the LLM by substring-matching the label in its
free-text output. Sentiment SST-2: Qwen-0.5B measured at **0.580** -- barely above the 0.50 binary chance. Qwen-0.5B should
get ~0.85+ on SST-2. So the 0.58 is almost certainly a PARSING ARTIFACT (the LLM classifies correctly but phrases it in a way
the substring matcher misses), NOT the LLM's true capability.

## Implication (honest)
The classification "substrate wins" results are SOFT:
- text-class: substrate 0.848 vs Qwen 0.688 -- LLM likely under-measured
- sentiment: substrate 0.767 vs Qwen 0.580 -- LLM clearly under-measured (0.58 implausible)
A FAIR comparison needs constrained decoding (force the LLM to emit only a label token) or log-prob scoring over the label set.

## What REMAINS robust
- MATH head-to-head: clean (the answer is a NUMBER, last-number parsing is reliable). Substrate beats Qwen 0.5B/1.5B/3B on
  MAWPS+MultiArith -- THIS is the robust, scale-invariant north-star result.
- The LATENCY / MEMORY / DETERMINISM dimensions are real regardless of parsing (substrate <100MB, ~ms, deterministic).
- The substrate CAPABILITY numbers (text-class 0.848, sentiment 0.767, chunking PASS, etc.) are real -- only the LLM-comparison
  side is parsing-confounded.

## Recommendation
Re-run the classification head-to-heads with CONSTRAINED DECODING (label-token logprob argmax) for a fair LLM number before
claiming substrate-beats-LLM on classification. The MATH head-to-head stands as-is. I will rebuild the head-to-head harness with
logprob-based label scoring if you want the fair classification comparison.
