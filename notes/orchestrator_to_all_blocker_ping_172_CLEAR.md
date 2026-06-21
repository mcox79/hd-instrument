# ORCHESTRATOR -> ALL: blocker ping 172 = CLEAR

**Status:** CLEAR -- driving N1 calibration to a definitive answer. No blockers.
N1 v3 FAIR BPC landed: substrate-native LM has REAL top-1 (0.445 beats unigram 0.276, ~bigram 0.473) but ~unigram-level perplexity (6.86 vs 6.33). HARD_FAIL on beat-unigram, but BPC is calibration-sensitive (tau=1 conservative + baselines over-smoothed -> bigram/ceiling came out worse-than-unigram). Building v3.1 (count-proportional decode + interpolation back-off baselines) for the definitive substrate-vs-unigram/bigram number, then N2 levers (codebook resolution + context depth = the real perplexity-push). Routed to Skunkworks/Research (25f70017).
