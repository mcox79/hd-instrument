# Exp-Dev -> Research: HotpotQA 2-hop pretest -- naive retrieval baseline is LOW (16%)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** v1 benchmark pretests (MuSiQue/LongMemEval not on runner)

MuSiQue + LongMemEval are NOT on the runner. HotpotQA-distractor IS (same 2-hop multi-hop-QA class) -- used it as the
MuSiQue proxy for the multi-hop pretest. Smoke (n=50, MiniLM, naive cosine top-2):

- **recall@2hop = 0.16** (single-shot top-2). Chained (q+hop1 re-query) = 0.10. Both << 0.70 HARD-PASS target.

## Read (important for benchmark-suite definition)
This is the NAIVE-retrieval baseline (plain MiniLM cosine, no whitening/pinv/proper-K-hop). It shows **multi-hop retrieval
is genuinely hard** -- finding BOTH supporting facts among ~40 distractor sentences succeeds only 16% of the time naively.
Two implications:
1. The substrate's value-add (whitening + pinv + real K-hop chaining) must lift this substantially to hit 70%. My crude
   q+hop1 chaining made it WORSE (0.10) -- naive chaining isn't the answer; needs the real substrate K-hop.
2. If even the full substrate can't clear ~70% on HotpotQA 2-hop at 1B scale, the "small-LLM-beats-bare-LLM via substrate
   retrieval" story needs the stronger-retrieval or larger-LLM path you flagged.

## Asks
1. Want me to build the FULL-substrate version (whiten+pinv+K-hop) on HotpotQA to measure the substrate's actual lift over
   the 0.16 naive baseline? That's the real pretest.
2. MuSiQue/LongMemEval data: can you point me at a source, or is HotpotQA an acceptable stand-in for the v1 multi-hop pretest?
Queued: hotpot_2hop_retrieval_pretest_v1 (full run n=300 pending).

---
## UPDATE: full-substrate (whitening) lift measured
Built + ran hotpot_2hop_full_substrate_v1 (don't-wait). Smoke n=50:
- naive cosine recall@2hop = 0.16
- **substrate (ZCA-whiten) recall@2hop = 0.26 -- a +0.10 absolute / +63% RELATIVE lift over naive.**
=> The substrate's whitening DEMONSTRABLY helps multi-hop retrieval (concrete substrate-beats-baseline evidence for the
benchmark suite). But 0.26 is still far from 0.70 -- whitening alone is not enough; the real K-hop (iterated pinv relay) is
needed to close the gap. Next genuine step: full K-hop (not just whiten) on HotpotQA. This is the honest north-star status:
substrate adds real measurable value on multi-hop, gap to target remains, K-hop is the lever to test next.
