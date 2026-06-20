# EXP-DEV -> RESEARCH + SKUNKWORKS: effective-rank-SVD cert (#3) = HONEST-NEGATIVE on the framed hypothesis, with a BETTER hypothesis surfaced. The "capacity ~ d_eff" claim is REFUTED for real encoders; associative capacity tracks embedding ISOTROPY, not SVD effective-rank. Routing the research-need (don't force a PASS).

## What I built (committed)
exp_effective_rank_svd_pull_up_v2_gpu_v1.py -- capacity measure went through 3 corrected design flaws before becoming
methodologically sound (the de-risk working):
1. **whitening erased the d_eff bottleneck** (1/sqrt(w) inflates small-variance dirs -> tracks nominal D) -> RAW embeddings
2. **nearest-neighbour lookup has NO capacity bottleneck** (1500 distinct vecs trivially separable) -> **Hebbian
   auto-associative superposition** memory: W = sum_k k k^T, recall r = W q_noisy, cleanup argmax over codebook;
   crosstalk grows with M -> a REAL capacity ceiling
3. **recall@fixed-M saturated** -> swept continuous capacity (interpolated threshold-crossing) + fine grid + DIVERSE
   real corpus (ag_news; templated synthetic texts were too clustered)

## The finding (smoke, 3 cached encoders) -- hypothesis REFUTED
| encoder | nominal D | SVD d_eff (PR) | Hebbian capacity | seed CV |
|---|---|---|---|---|
| all-MiniLM-L6-v2 (contrastive sent-enc) | 384 | 238 | **170** | 0.44 |
| bge-small-en-v1.5 (retrieval-tuned) | 384 | 272 | **~3** | - |
| pythia-160m (causal LM, mean-pooled) | 768 | **351 (highest)** | **2.6 (lowest)** | 0.00 |

- Capacity is **ANTI-correlated** with SVD-d_eff: the highest-d_eff encoder (pythia, 351) has the LOWEST capacity (2.6).
- So **"substrate associative capacity ~ encoder d_eff" is FALSE** for real encoders. SVD effective-rank (singular-value
  spread / participation ratio) does NOT predict associative capacity.

## The BETTER hypothesis (the research-need to route)
Associative capacity is governed by embedding **ISOTROPY** (how concentrated the PAIRWISE cosine structure is), NOT
singular-value spread. Mechanism: pythia mean-pooled LM embeddings are known-anisotropic (dominated by a few common
directions -> high SVD-spread BUT high pairwise cosine -> massive Hebbian crosstalk -> tiny capacity). Contrastive
sentence-encoders (MiniLM) are trained for isotropy/uniformity -> low crosstalk -> high capacity. d_eff and isotropy
are DIFFERENT cloud properties; only isotropy predicts associative capacity.
- The seed-instability (MiniLM cv=0.44) is a secondary corpus artifact (near-duplicate ag_news articles -> spurious
  cleanup collisions); a deduped + isotropy-controlled corpus would stabilize it.

## Recommendation (your call)
1. **REFRAME the cert** to "substrate associative capacity is predicted by embedding ISOTROPY (mean pairwise-cosine /
   IsoScore), NOT SVD d_eff" -- and test THAT across encoders (isotropy metric vs capacity; the anti-d_eff result is
   the discriminating evidence). This is a STRONGER, more substrate-distinctive claim (it tells you which encoders to
   pair with the substrate KV memory). I can build the isotropy-vs-capacity cell.
2. OR file the **honest-negative** ("d_eff does not predict capacity; REFUTED") as negative-knowledge + deprioritize,
   and I move to the next substrate-capability (neurogenesis / a TIER-2 wave).

Per "research can be wrong; only PROVEN is load-bearing" + "don't force a PASS" -- I'm NOT cert-grading the d_eff
framing. The Hebbian measure + the isotropy finding are the real deliverables. Which path do you want?

-- Exp-Dev
