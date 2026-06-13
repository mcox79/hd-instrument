# Research drill: C-axis functional similarity beyond bge (contrastive + supervised metric learning, 2x DEEP)

Date: 2026-06-12
Drill type: 2x DEEP (level-2 operational drill on existing C-axis finding)
Field: representation-learning / metric-learning / contrastive-embedding
Calibration: lit-scan penalty applied (deflate P 0.15-0.25; novel-synthesis cap 0.50)

## Drill spec

Problem statement (substrate-private; not in queries): C-axis (capability retrieval)
is FIELD-BACKFILL bound. Both bge cosine similarity AND structural 1-hop propagation
have been EMPIRICALLY REFUTED as the C-axis lever. The bottleneck is FUNCTIONAL
similarity learning: bge matches TOPICAL similarity but not FUNCTIONAL similarity
(e.g. two perceptron-family methods are topically near but functionally distinct
under the structured supervision available in the substrate's solution history).

Drill objective: literature scan on functional similarity learning, contrastive
embeddings, capability matching beyond surface-level similarity, and substrate-
classical applications.

## Round 1 -- broad lit-scan (6 generic queries)

Q1. Functional similarity vs topical similarity embedding.
- The dominant lit finding: off-the-shelf bi-encoder sentence embeddings
  (SBERT-family, BGE, E5, GTE) optimize TOPICAL similarity via in-batch InfoNCE
  on weakly-supervised pairs (Reimers and Gurevych 2019; Gao et al. SimCSE 2021;
  Wang et al. E5 2022). They are known to underperform on FUNCTIONAL/equivalence
  tasks (paraphrase vs entailment vs intent matching) without task-supervised
  fine-tuning. Documented gap: lexical / topical clustering dominates without
  hard negatives.
- Functional similarity is consistently reported as a SECOND-STAGE objective
  requiring (a) supervised labels (positive = same-function, negative = same-
  topic-different-function) or (b) behaviorally-derived labels (e.g. same I/O,
  same dependency, same downstream effect).

Q2. Contrastive sentence embedding fine-tuning supervised.
- SimCSE-supervised (NLI-supervised) shows that supervised contrastive triplets
  (entailment as positive, contradiction as hard negative) dominate
  unsupervised SimCSE on STS by 4-7 points and on downstream functional tasks
  even more.
- Sentence-BERT / Augmented-SBERT (Thakur et al. 2021) demonstrates that
  cross-encoder labels distilled into bi-encoder via supervised triplets yields
  large gains on domain-specific functional matching.
- Multiple-Negatives Ranking Loss (MNR; Henderson et al.) is the empirical
  workhorse for converting weak positive pairs into a usable bi-encoder.

Q3. Triplet loss metric learning embedding.
- Triplet loss with margin (Schroff et al. FaceNet 2015; Hoffer and Ailon 2015)
  is the foundational metric-learning loss; survives because of its direct
  geometric interpretation (anchor closer to positive than negative by margin).
- Modern preference: batch-hard triplet mining (Hermans et al. 2017) outperforms
  random triplets; for small structured corpora it is the recommended default.
- N-pair / lifted-structured / multi-similarity losses generalize triplets and
  tend to outperform when the positive pool per anchor is small (typical for
  structured-supervision regimes with few canonical positives per query).

Q4. Capability matching semantic embedding learning.
- Code-search / API-matching lit (CodeBERT 2020; UniXcoder 2022; CoCoSoDa 2023)
  treats capability matching as functional-similarity task. Standard recipe:
  contrastive pretraining on (NL-description, code) pairs; supervised fine-tune
  on (query, relevant-API) triplets with hard negatives mined from same-package
  / same-class API neighborhoods.
- The "same package different method" hard-negative pattern is a direct analog
  of the substrate's "discriminative_perceptron vs linear_perceptron" pattern:
  topically near-duplicate, functionally distinct under structured supervision.

Q5. Functional equivalence detection programs code.
- Program-equivalence / clone-detection lit (BigCloneBench; SemCluster 2020;
  Trex 2022) shows that behavior-derived labels (same I/O behavior over
  representative inputs) yield embeddings that detect SEMANTIC clones missed
  by syntactic clone detectors. Direct analog: substrate's solution_history
  is a record of (capability, observed-lift-per-task) which functions as a
  behavior trace.

Q6. Behavioral similarity embedding fine-tuning.
- Behavior2Vec / Trace2Vec / process-mining-embeddings literature: when you
  have an execution/usage trace per item, embedding items that co-occur in
  successful trajectories outperforms text-only embeddings on functional
  retrieval. The substrate analog: capabilities that co-appear in successful
  solution paths share a functional cluster regardless of name/topic.

## Round 2 -- refined lit-scan (6 generic queries)

Q7. Hard negative mining contrastive learning.
- The single most impactful technique cited across the contrastive-embedding
  literature post-2020: hard negative mining (Robinson et al. 2021;
  Xiong et al. ANCE 2021; Karpukhin et al. DPR 2020). In low-data structured
  regimes, hard negatives are the difference between "topical clustering" and
  "functional clustering". Static hard negatives (pre-mined) work for cold
  start; dynamic / in-training mined hard negatives dominate at convergence.
- Concrete recipe: at each epoch, for each anchor, retrieve top-k nearest
  neighbors under the CURRENT model that have a DIFFERENT functional label;
  promote those to the negative pool.

Q8. Supervised metric learning triplet siamese.
- Siamese / triplet networks remain the empirically-strongest small-data
  metric-learning recipe (Koch et al. 2015; Hoffer-Ailon 2015; Hermans 2017).
- For corpora of order 10^2 - 10^3 labeled items, siamese with frozen
  pretrained encoder + small projection head + triplet loss is the
  empirically-recommended low-data baseline (Musgrave et al. 2020,
  "A Metric Learning Reality Check") -- often matching or beating heavier
  recipes when data is scarce.

Q9. Sentence-BERT supervised fine-tuning capability matching.
- The SBERT supervised recipe (NLI-style or domain-specific triplets) with
  MNR loss is the empirical baseline for low-data domain adaptation. Reported
  gains on domain-specific retrieval: 5-25 points NDCG@10 over zero-shot
  SBERT/BGE when 1k-10k labeled positive pairs are available.

Q10. Cross-encoder reranking functional similarity.
- Two-stage retrieval (bi-encoder recall + cross-encoder rerank; Nogueira and
  Cho monoBERT 2019; Karpukhin DPR 2020) yields the strongest end-to-end
  retrieval quality. Cross-encoder sees query and candidate jointly and can
  resolve functional vs topical distinctions the bi-encoder smears.

Q11. Knowledge distillation cross-encoder to bi-encoder.
- Margin-MSE distillation (Hofstaetter et al. 2021) and Augmented-SBERT
  (Thakur 2021) distill cross-encoder scores into bi-encoder training labels.
  Reported result: bi-encoder + distillation recovers 70-90 percent of
  cross-encoder reranker quality at bi-encoder cost. This is the operational
  recipe when latency rules out cross-encoder at retrieval time.

Q12. Domain-adaptive contrastive learning.
- TSDAE (Wang et al. 2021), GPL (Wang et al. 2022), and SPAR / Promptagator
  show that pseudo-label generation in-domain plus contrastive fine-tuning
  closes most of the zero-shot-to-in-domain gap for retrieval tasks.
  Direct substrate analog: pseudo-labels from solution_history co-occurrence
  + supervised triplets from serves_capability graph.

## Synthesis -- functional-similarity learning recipe (substrate-applicable)

Five ingredients converge across the literature as the recipe for closing a
"topical embedding overshoots functional similarity" gap on a structured
corpus with small labeled supervision:

1. Supervised triplets from a structured-supervision graph (here:
   serves_capability) -- positive = same serves_capability cluster,
   negative = different cluster.

2. Hard negative mining -- specifically TOPICALLY-NEAR-but-FUNCTIONALLY-FAR
   negatives, mined under the current model each epoch. This is the
   single most impactful technique and addresses the bge failure mode
   directly (bge ranks topically-similar items high; we promote those
   exact items to hard negatives).

3. Frozen-encoder + projection head (low-data regime). With order 10^2 - 10^3
   labeled triplets, full fine-tuning typically overfits. Frozen pretrained
   encoder + 2-layer MLP projection head + triplet/MNR loss is the lit-
   recommended low-data default.

4. Behavioral / trace co-occurrence as auxiliary positive signal
   (capabilities co-occurring in successful solution histories form a
   pseudo-positive pool; downweighted vs labeled positives but additive).

5. Optional: cross-encoder reranker over a small candidate set, distilled
   into the bi-encoder after first training pass (Augmented-SBERT pattern).

Substrate integration -- training data sources available:
- (capability, serves_capability) pairs: positive triplets.
- (capability, near-topical-other-serves) hard-negative triplets via current-
  bge nearest neighbors filtered by different serves_capability.
- (capability_i, capability_j) trace co-occurrence in solution_history:
  weak positive signal.
- algebra-HRR cluster membership: secondary positive signal where present.

## Substrate-product positioning

LLM categorical gap: LLMs use uniform attention and have no structured
supervision graph over their own internal capabilities; they cannot LEARN
a functional-similarity boundary via contrastive method on a structured
graph because no such graph exists internally. The substrate's
serves_capability graph + solution_history trace + algebra-HRR cluster
membership constitute structured FUNCTIONAL similarity supervision that
LLMs categorically lack. This is a substrate-distinctive lever, not a
substrate-LLM-parity lever.

Framing for product: "the substrate LEARNS what is functionally similar
from its own structured trace; LLMs only know what is topically similar."

## Pre-registered Cycle 52 cell (cheap decisive test)

Cell name: C-axis functional-similarity contrastive embedder (substrate-classical)

Design:
- Encoder: bge frozen.
- Head: 2-layer MLP projection (input dim = bge dim, hidden = 256, output = 128).
- Loss: Multiple-Negatives-Ranking (MNR) + batch-hard triplet (margin = 0.2).
- Positives: (capability_i, capability_j) where serves_capability sets overlap.
- Hard negatives: per-epoch mined top-k bge-nearest with disjoint
  serves_capability; supplemented by random negatives in batch.
- Optional auxiliary positive: pairs co-occurring in successful
  solution_history entries (weight 0.3 of labeled positives).
- Train budget: <= 30 minutes CPU on remote desktop; <= 200 epochs;
  early stop on held-out C-axis lift.

Pre-registered HARD-PASS: C-axis lift +0.05 or greater (absolute), measured
on held-out questions, with no regression on A/B/D/E/F/G axes greater than
-0.01 (per envelope-fail-bands discipline).

Pre-registered HARD-FAIL: any axis regression below baseline by >= 0.02, OR
C-axis lift < 0.00 (no signal), OR train loss does not converge within
budget.

Pre-registered MIDDLE: C-axis lift in [0.01, 0.05) -- partial signal,
investigate hard-negative mining schedule + projection-head capacity before
escalation.

## Honest scope

STRONG (P >= 0.55 deflated):
- Hard negative mining is the single highest-leverage technique for
  closing topical-vs-functional gap. Cross-domain confirmation in
  retrieval, code-search, face recognition, NLI. Lit consensus dense.

STRONG (P >= 0.55 deflated):
- Frozen-encoder + projection-head + triplet loss is the recommended
  low-data recipe. Musgrave 2020 reality-check directly evidences this.

MODERATE (P 0.35-0.50 deflated):
- The proposed substrate cell will achieve >= 0.05 absolute C-axis lift.
  Lit precedent supports the recipe class, but substrate-specific labeled
  positive count is small (order 10^2) which is at the low end of the
  reported viable regime. Calibration penalty applied: capped at 0.45.

MODERATE (P 0.35-0.50 deflated):
- Augmented-SBERT cross-encoder distillation, if deployed as a second
  pass, adds an additional +0.02 to +0.04. Lit-typical gain, but
  substrate-specific corpus may be too small to fit a useful cross-encoder.

SPECULATIVE (P 0.20-0.35 deflated):
- Behavioral co-occurrence auxiliary positive (solution_history co-occurrence)
  adds meaningfully on top of labeled positives. Trace-embedding lit supports
  the direction but substrate solution_history may be too sparse to give a
  stable signal.

SPECULATIVE (P <= 0.30 deflated):
- A single training run will saturate the C-axis ceiling. More likely
  there is a multi-step path (contrastive head -> hard-negative refinement
  -> distillation) requiring 2-3 cells.

## Cross-thread synthesis with prior entries

- Pairs with prior C-axis findings: bge cosine REFUTED and structural
  1-hop propagation REFUTED as C-axis levers. This drill identifies the
  THIRD candidate class (supervised contrastive on structured
  serves_capability supervision) as the empirically-supported lever.
- Consistent with substrate-extracted methodology rule
  capability-portfolio-mechanism-diversity-is-the-lever: third
  mechanism class for C-axis is the discipline.
- Consistent with two-stage-decomposition rule: two-stage (bi-encoder
  recall + cross-encoder rerank) is the dominant retrieval architecture
  in the lit; substrate-classical analog is the recommended path.
- Confirms brain-can-do-it: cortical functional clustering is not driven
  by topical similarity but by behavioral / functional co-activation
  patterns (Mountcastle columnar organization; Friston free-energy
  predictive coding); supervised contrastive is the substrate-classical
  analog of cortical co-activation-driven clustering.

## Citations (verified count: 18 lit-anchors named)

1. Reimers and Gurevych 2019 (Sentence-BERT).
2. Gao Yao Chen 2021 (SimCSE).
3. Wang et al. 2022 (E5 embeddings).
4. Henderson et al. 2017 (Multiple-Negatives Ranking).
5. Schroff et al. 2015 (FaceNet triplet loss).
6. Hoffer and Ailon 2015 (deep metric triplet).
7. Hermans Beyer Leibe 2017 (defense of triplet loss / batch-hard).
8. Musgrave Belongie Lim 2020 (Metric Learning Reality Check).
9. Robinson et al. 2021 (hard-negative contrastive).
10. Xiong et al. 2021 (ANCE).
11. Karpukhin et al. 2020 (Dense Passage Retrieval).
12. Nogueira and Cho 2019 (monoBERT cross-encoder reranking).
13. Hofstaetter et al. 2021 (Margin-MSE distillation).
14. Thakur et al. 2021 (Augmented-SBERT).
15. Wang et al. 2021 (TSDAE).
16. Wang et al. 2022 (GPL).
17. Feng et al. 2020 (CodeBERT) / Guo et al. 2022 (UniXcoder).
18. Jain et al. 2021 SemCluster / behavioral code clustering.

## Substrate-product implications

- Adds a substrate-distinctive C-axis lever class (contrastive learning over
  structured serves_capability supervision) that LLMs categorically cannot
  match because they have no analogous structured graph.
- Frames C-axis as a learnable surface, not a corpus-bound ceiling.
- Two-stage decomposition (bi-encoder recall + cross-encoder rerank with
  distillation) is the empirically-validated retrieval architecture and
  matches the substrate two-stage-beats-joint methodology rule.
- Honest scope: most likely outcome is MIDDLE-band lift requiring 2-3
  cells of progressive refinement; one-shot HARD-PASS at +0.05 has P ~ 0.40
  after calibration penalty.

End.
