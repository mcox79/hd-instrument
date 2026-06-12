# Exp-Dev -> Testbed/Research: MEASURED -- the A-axis is NOT cue-bound. bge puts the gold atom at median rank 0.5/1743 (recall@3=0.92, recall@10=1.0). The residual is downstream RANKING / UNION-precision on SMALL gold sets, NOT query encoding. Refutes the trilogy's free-text-path extrapolation; explains the prior "tuned-UNION-bound" finding.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-physics of the A-route. bge = embedding model (NO generative LLM).
**Cell:** exp_qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1.py (GPU, bge on CUDA, real substrate + gap7 benchmark).

## What was measured
The two-vector trilogy PREDICTED (by analogy to the atom-keyed query-SNR result) that the free-text A-axis would be limited by
bge CUE quality. This cell tests it directly on the 12 A-axis answerable-with-gold questions: bge-encode the query topic, cosine
to the gold atom's bge semantic vector, gold RANK in the full semantic ordering, in-top-k (k=3 production).

## Result -- the trilogy's prediction is REFUTED (cleanly)
- **median best-gold bge cosine = 0.771** (mean 0.756) -- high alignment.
- **recall@3 = 0.917, recall@10 = 1.000** -- every A-gold atom is reachable within the top 10.
- **median gold rank = 0.5 of 1743 atoms** -- bge typically ranks the gold atom FIRST or SECOND.
- per-q ranks: mostly 0-2; one outlier Q32-A at rank 4 (the single recall@3 miss).

VERDICT: CUE-ALIGNED. The bge cue is excellent; A-gold is NOT hard to reach. So the A-axis F1 residual is NOT a query-encoding
problem -- it is DOWNSTREAM of the cue.

## Mechanism (reconciles with the prior "Testbed-tuned-UNION-bound" finding)
- A-gold sets are SMALL (typically 2-3 atoms per question; e.g. Q01 gold = 3 atoms). The production A-route returns keyword
  UNION bge-top-3. bge-top-3 captures the BEST-ranked gold atom (recall@3=0.92) but a 3-slot top-k cannot capture a 3-atom gold
  set AND stay precise -- raising k to recall the 2nd/3rd gold atoms admits non-gold atoms, crashing precision on a tiny gold set.
- So the A-axis ceiling is a PRECISION-RECALL-ON-SMALL-GOLD-SETS problem at the fusion stage, exactly the "tuned UNION" sweet
  spot found earlier (all simple bge route changes HURT). This cell explains WHY at the mechanism level: the cue is not the
  limit (gold rank ~0), the small-gold precision-recall tradeoff is.

## Honest note
- This REFUTES the trilogy's extrapolation of "every path is query-SNR-bound" to the free-text A-route. The PRINCIPLE held for
  the atom-keyed identity channel (cue~0.45 margin), but for A-route the bge cue is so strong that the binding constraint moved
  DOWNSTREAM to fusion. Measurement corrected the prediction.

## Routing
- **Testbed:** the A-route's tuned keyword-UNION-bge-top-k is justified -- the bge cue already ranks gold at ~0; the residual is
  small-gold precision-recall, not the cue. A per-question ADAPTIVE k (size of expected gold set) or a cosine-threshold cutoff
  (gold cos ~0.77 vs distractors) is the only plausible lever, and it trades precision; likely near the tuned ceiling already.
- **Research:** A-axis is corpus/gold-set-granularity-bound, not encoder-bound -- consistent with the axis-bottleneck-class
  taxonomy (A = semantic/corpus axis). The bge encoder is NOT the A-axis bottleneck (measured).
- **Exp-Dev:** A-axis cue question decisively CLOSED (cue excellent, rank ~0). Honest self-correction logged. Holding.
