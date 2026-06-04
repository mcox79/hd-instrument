# Exp-Dev -> Research + Orchestrator: bio-primitive smoke findings (laptop CPU; batches 1+2 + iter2)

Ran the REVISED bio-primitive smoke sweep (change_request_stage_a_bio_smoke_REVISED_drill_B_specs) on the
LAPTOP CPU per user direction ("do it all on laptop, explore + iterate right here"). 5 of 8 cells run + 1
iteration. All $0 CPU. write_metrics used. WHY-DRILLs applied + acted on.

## RESULTS

### B6 D-ECR energy-driven pruning -- HARD_PASS (validated; iterated)
Batch 1 (M=1.3*alpha_c): D-ECR=LRU=1.0 (both saturated below capacity) -> looked like HF.
WHY-DRILL -> iter2 swept M={1.0,1.5,2.0,2.5}*alpha_c at N=512, 3 seeds:
  m1.0: decr=1.00 lru=1.00 none=0.00   m1.5: decr=1.00 lru=0.97 none=0.00
  m2.0: decr=0.79 lru=0.39 none=0.00   m2.5: decr=0.05 lru=0.01 none=0.00
=> D-ECR (evict lowest energy-contribution = lowest self-overlap) holds ~2x LRU recall at 2x capacity;
   operating window m1.5-2.0. Audit-preserving eviction primitive CONFIRMED. (none=0 everywhere -> eviction is
   essential past capacity.) STRONG product result (indefinite auditable operation past single-substrate limit).

### B3 cf-RPE active gating -- NEAR-HP / MIDDLE
Write at top-10% prediction error: 8.3x fewer writes (15936->1928) retaining 94% of the gap (2.35->2.20).
Works; just under the 10x HP bar. Recommend: accept as MIDDLE OR push to top-5% / exp-smoothed surprise.

### B1 one-shot Hebbian classification -- HF (task too easy, not a primitive failure)
acc=1.00 always, but Adam matches in adam_epochs_to_match=1 -> no speed advantage on linearly-separable
classification. wall-speedup timing-noise-dominated (0x..9205x). The training-speed advantage is task-difficulty
dependent -> already addressed on char-LM by the queued crossover-N sweep + training-speed Stage A. one-shot
ACCURACY is fine; the SPEED claim needs a task where Adam needs many epochs.

### B2 DG-class sparse expansion -- IMPL NEEDS FIX (not a verdict)
My sparse-expansion recall (random projection + k-WTA + sparse covariance Hopfield) returned M_crit=0 (sparse
recall broken). Needs a corrected sparse associative-memory recall (Tsodyks/Willshaw threshold dynamics) before
a real capacity comparison. Will rebuild.

### B8 predictive-coding residual encoding -- REPRESENTATION QUESTION for Research
r = ||x_res||/||x_full|| = 0.86 (bigram base) vs 0.99 (uniform base). Bigram reduces residual but r=0.86 >> the
predicted 0.5-0.7. ROOT CAUSE: with a RANDOM bipolar codebook, the bigram-expected embedding is a weighted avg
of near-orthogonal vectors -> low norm (cancellation) -> projection barely reduces the residual. The residual-
encoding capacity gain assumes STRUCTURED/correlated embeddings, not random HD codes. QUESTION for Research:
does the residual-encoding primitive require learned/correlated embeddings, or a different residual definition
(e.g. residual in logit space, not codebook space)? Loop-back requested.

## NOT YET BUILT (careful per-cell builds pending)
- B4 column ensemble (reduce single-substrate N from 20480 -> RAM-safe ~10240 per the same RAM logic that revised B2).
- B5 STDP-replay consolidation (needs a palimpsest/bounded-weight decay model so forgetting exists for replay to correct).
- B7 theta-gamma phase binding (scalar cos modulation is degenerate; needs a per-position rotation/permutation phase model).

## Next iterations (laptop, continuing)
1. B2 sparse-recall fix. 2. B5 with decay model. 3. B7 proper phase binding. 4. B4 RAM-safe ensemble.
WHY-DRILL fixes: B8 -> Research loop-back (representation). B3 -> push gating. B1 -> harder task (covered by crossover sweep).

**END.** Realistic outcome matched the P_all_8=0.17 honesty: of 5 run, 1 clean HP (B6), 1 near-HP (B3), 1 task-artifact HF (B1), 2 need rework (B2 impl, B8 representation).
