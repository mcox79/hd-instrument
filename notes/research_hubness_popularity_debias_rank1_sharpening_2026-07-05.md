# Research: sharpening rank-1 on the Hits@k/MRR reframe's MIDDLE_BAND — hubness + popularity-debiasing as a cheap post-hoc rescore

**Filed:** 2026-07-05 by research (Opus synthesis; off-disk recompute of the landed reframe cell's
FROZEN score matrix — 3 seeds x 2 relations, functions imported verbatim, no new machinery — plus
2 parallel Sonnet lit-scan sub-agents, generic-math-terms only per query-privacy discipline).

**Trigger:** `data/exp_schema_relation_hitsatk_mrr_reframe_v1_smoke/metrics.json` +
`_multiseed_v300_full_hyperparam_preview.log`, verdict `MIDDLE_BAND`: filtered Hits@10 rms clears
the informal >=0.20 mark on average (AtLocation 3-seed mean +0.213, CausesDesire +0.449) but MRR
never reliably clears the 0.15 HARD-PASS floor (AtLocation +0.108, CausesDesire +0.166 mean but
sd=0.071 with seed=7 at only +0.098) and `win_rels=[]`/`win_encs=[]` — the object lands in the
top-10 more than a shuffled control, but does not reliably win rank-1. Mechanism lineage:
`experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py` (read in full, all scorer/rank
machinery reused verbatim below) <- `exp_schema_relation_TEM_scorer_scaleup_envelope_v2.py` <-
`exp_schema_relation_richer_content_vscan_v1.py`. Cross-referenced against
`notes/research_reframe_rank_set_prediction_one_to_many_ceiling_2026-07-05.md` (which flagged
sparse-coding/compressed-sensing as ONE adjacency candidate, not a foreclosed answer) and
`notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` (CA3
regenerative-cleanup verified strong in reasoning — cited below as the reason attractor cleanup is
evaluated on merit, not dismissed).

---

## HEADLINE

**The crowding that keeps the true object out of rank-1 is neither a diffuse cloud of
idiosyncratic per-query near-neighbors, nor a tight 2-3-object semantic cluster. Two direct,
quantified diagnostics converge on a two-part answer: (1) genuine geometric HUBNESS — the
object-side top-1-winner-count distribution has Gini=0.87-0.95 across both relations (a handful of
objects hoover up the argmax slot across dozens of unrelated queries) — the textbook signature
Radovanović, Nanopoulos & Ivanović call "Hubs in Space" (*JMLR* 2010); and (2) LABEL-PRIOR bias —
that hub distribution correlates with training-label frequency at r=0.42 (AtLocation) to r=0.80
(CausesDesire). Residualizing the hub distribution against training frequency shows the two
relations sit at DIFFERENT points on this spectrum: CausesDesire's hubness is almost entirely
explained by label frequency (residual Gini collapses 0.95->0.08), AtLocation's is a genuine mix
(residual Gini only drops 0.87->0.18 — real geometric hubness survives frequency-removal). Because
the scorer already trains with EXACT full softmax over the small (V<=300) candidate set — not
sampled/in-batch softmax — the classic logQ negative-sampling correction (Yi et al. 2019) targets a
mechanism that is NOT present here and is explicitly NOT the lead fix. The matched fix, ranked by
cost: FIRST, a training-free post-hoc rescore combining CSLS/local-scaling (fixes the hubness
component, Radovanović 2010 / Schnitzer et al. 2012 / Feldbauer & Flexer 2019) with post-hoc logit
adjustment (fixes the label-prior component, Menon et al. 2021, ICLR) — both are pure rescalings of
the score matrix the reframe cell already computes, zero retraining. SECOND (staged, only if the
cheap rescore under-delivers), the trained complements: train-time logit-adjustment loss and
hard-negative mining on the identified hub objects (Karpukhin et al. 2020 / Xiong et al. 2021),
which need a continued-training loop. NOT chosen: CA3-style attractor cleanup — the data below
argues cleanup would likely worsen, not fix, this specific failure mode.

---

## 1. MECHANISM — quantifying the crowding (off-disk recompute, 3 seeds x 2 relations)

Recompute method: imported `build_split_scaled`, `encode_feature_matrix`, `_proj_pair`,
`fit_scorer_paired`, `score_scorer`, `_filter_mask`, `filtered_ranks` **verbatim** from
`exp_schema_relation_hitsatk_mrr_reframe_v1.py` (no reimplementation), ran the FULL-mode config
(V=300, M_op=800, matching `_multiseed_v300_full_hyperparam_preview.log`) for seeds {7,13,19} on
both HP-eligible relations, encoding=bge_semantic. For every inductive test row where the true
object was NOT rank-1 (a "miss"), recorded which object DID win rank-1 (post-filter argmax).

| Relation | seed | n_miss / n_test | distinct rank-1 winners among misses | top-10-winner share of misses | uniform-diffuse baseline (10/distinct) | corr(winner-count, train-frequency) |
|---|---|---|---|---|---|---|
| AtLocation | 7 | 102/150 | 66 | 0.314 | 0.152 | 0.607 |
| AtLocation | 13 | 86/150 | 61 | 0.349 | 0.164 | 0.653 |
| AtLocation | 19 | 102/150 | 59 | 0.363 | 0.169 | 0.568 |
| AtLocation | **mean** | | | **0.342** | ~0.16 | **0.609** |
| CausesDesire | 7 | 59/150 | 40 | 0.492 | 0.250 | 0.732 |
| CausesDesire | 13 | 53/150 | 34 | 0.528 | 0.294 | 0.629 |
| CausesDesire | 19 | 60/150 | 40 | 0.500 | 0.250 | 0.604 |
| CausesDesire | **mean** | | | **0.507** | ~0.26 | **0.655** |

**Reading:** the top-10 dominant "wrong winners" claim ~2x the share of misses a uniform-diffuse
distribution over the observed number of distinct winners would predict, in every one of 6
seed-x-relation cells — concentrated, but NOT collapsed to 2-3 objects (66/102 and 40/59 misses
still spread across genuinely distinct competitors, i.e. a fat head + long tail, not a monolith).
The correlation with training frequency is large, positive, and stable across all 3 seeds for both
relations — this is not sampling noise. Named winners for AtLocation seed=7: `country`(5),
`cabinet`(4), `park`(4), `sporting_goods_store`(4), `closet`(3), `city`(3) — generic,
frequently-labeled location nouns, not subject-specific semantic near-misses. For CausesDesire:
`have_party`(7), `go_somewhere`(4), `pass_course`(3), `go_on_internet`(3) — same pattern.

### 1a. The decisive diagnostic split: is this HUBNESS (geometric) or LABEL-PRIOR (frequency), or both?

These are distinguishable claims and the cell design depends on getting the split right, so this
note computed both directly (seed=7, bge_semantic) rather than inferring one from the other:

- **Object-side k-occurrence (Nk) skew** — the hubness-proper statistic: for EVERY inductive test
  row (hit or miss), which object wins the post-filter argmax? Gini coefficient of the resulting
  per-object win-count vector: **AtLocation Gini=0.869, skew=14.0; CausesDesire Gini=0.953,
  skew=16.9** (V_eff=300, n_test=150 both). Both are extremely concentrated relative to a uniform
  null (a handful of objects hoover up most of the argmax slots across unrelated queries) — this
  IS the textbook hubness signature, independent of any frequency argument.
- **Residualized against training frequency** — to separate "hub because it's geometrically
  central" from "hub because it was trained on often," this note regressed Nk on train_freq
  (simple OLS) and recomputed Gini/skew on the RESIDUAL: **AtLocation residual Gini=0.175 (down
  from 0.869), skew=13.5 (barely changed); CausesDesire residual Gini=0.077 (down from 0.953),
  skew=3.7 (down from 16.9)**.

**Reading — the two relations split cleanly, and the split matters for the fix:**
CausesDesire's hub-dominance is **overwhelmingly LABEL-PRIOR/frequency-driven** (corr(Nk,
train_freq)=0.799; residual Gini collapses to near-baseline once frequency is removed) — the
matched fix here is **logit adjustment** (Menon et al. 2021). AtLocation's hub-dominance is
**a genuine MIX** (corr(Nk, train_freq)=0.420, weaker; a substantial residual Gini of 0.175
survives frequency-removal, i.e. real geometric hubness beyond what training frequency explains)
— the matched fix here needs **both** logit adjustment AND a geometric hubness rescore (CSLS /
local scaling). This is exactly why the proposed cell below applies BOTH corrections together
rather than picking one: the data shows the two relations sit at different points on the same
hubness<->label-prior spectrum, and a single-term fix would under-correct whichever relation
doesn't match its assumed mechanism.

**Margin check (rules out "razor-thin near-miss"):** for miss rows, the z-scored margin between
the wrongly-ranked top-1 and the true object's score (normalized by that row's score std) has
mean 2.2-2.7 / median 2.2-2.4 — a *substantial* separation, not a hair's-breadth tie. The scorer
is confidently, not marginally, preferring the popular decoy. This further argues against "many
tightly-clustered semantic near-neighbors barely edging out the truth" (which would show small
margins) and for a systematic score-inflation bias toward a specific, identifiable set of objects.

**Why this rules out (a) sparse-coding/compressed-sensing:** compressed-sensing set-recovery
theory addresses exact support recovery under a sparsity/incoherence assumption on the *signal*;
it has no natural term for "a specific known subset of codewords gets scored anomalously high
regardless of query," which is what's observed. Not dismissed by fiat — evaluated against the
actual crowding shape and it is simply the wrong shape of problem (no adjacency to compressed
sensing's phase-transition machinery was found relevant to a training-frequency-correlated
score bias).

**Why this argues AGAINST (c) attractor/CA3-style cleanup as the fix (not a dismissal — a
data-grounded caution):** the substrate's own strongest evidence for regenerative-cleanup
(`research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md`: regen_d5 ~0.70 vs
analog ~0.10, gap widens with load) is a case where cleanup corrects *representation noise around
a single correct stored attractor*. Here the failure mode is different in kind: multiple valid
codewords compete, and classical attractor-network theory (Amit-Gutfreund-Sompolinsky-era Hopfield
capacity analysis) establishes that attractor basin depth/width scales with how often a pattern is
reinforced/stored. Iterative cleanup dynamics run on this score landscape would be expected to
snap PREFERENTIALLY toward the already-popular hub objects — i.e., cleanup risks amplifying
exactly the bias measured above, not correcting it, unless debiasing happens first. This is a
falsifiable claim (see HARD-FAIL below), not an assumption.

**Why (d) resolution-increasing representation is deprioritized (not rejected):** the parent
research note already showed a nonparametric k-NN oracle using the SAME frozen features lands in
the SAME real-minus-shuf band as the trained bilinear/MLP scorers, and a separately-trained richer
content encoder (`exp_schema_relation_richer_content_vscan_v1`) HARD_FAILed to beat the frozen
baseline. Both facts say the ceiling is not primarily "not enough resolving power in the content" —
it is what happens to the SCORES after that content is used. A decorrelation/resolution lever
(per the hubness lit: hubness IS partly a concentration-of-measure/dimensionality effect) is a
real adjacent lever, but it requires retraining an encoder that was already tried and failed;
the diagnosis above says a training-FREE rescoring of the EXISTING scores plausibly captures most
of the fixable part of this specific failure mode at near-zero cost, so it is the cheaper first
move, with (d) staged as a fallback only if the cheap rescore lands in HARD-FAIL.

---

## 2. Lit-scan synthesis (2 parallel Sonnet sub-agents, generic math/stats terms only)

**Hubness core mechanism (verified via direct fetch):** in high dimensions, distances concentrate
(expected norm grows as roughly sqrt(d) while variance stays near-constant); points closer to the
data centroid have distances to *every other point* that grow more slowly with dimension than a
peripheral point's distances do — so central points get pulled into disproportionately many
nearest-neighbor lists ("hubs"), peripheral points become "antihubs." Radovanović et al. (JMLR
2010) is the canonical source; Feldbauer & Flexer (*Knowl. Inf. Syst.* 2019, verified via direct
fetch) benchmark correction methods head-to-head.

**Cheapest post-hoc corrections, ranked (all training-free rescalings of an already-computed score
matrix):**
1. **Local Scaling (Zelnik-Manor & Perona 2004) / NICDM** — rescale each score by a per-point
   local-density normalizer (distance/similarity to that point's own k-th neighbor). O(n) extra
   work on top of a score matrix already in hand; empirically among the STRONGEST hub-reducers in
   Feldbauer & Flexer's benchmark, ran in 3-51s at n=10,000 vs 754-2510s for full Mutual Proximity.
2. **Mutual Proximity, Gaussian-approximated (MPGaussI)** — reinterprets distance as a
   co-occurrence probability using per-point mean/variance; O(n^2), ~8s at n=10k; raised average
   neighborhood symmetry 0.50->0.73 in the same benchmark.
3. **CSLS (Cross-domain Similarity Local Scaling; Conneau et al. ICLR 2018)** —
   `adj(q,c) = 2*score(q,c) - mean_topk(q) - mean_topk(c)`; essentially free at a few-hundred-
   candidate scale; the standard practical choice in cross-lingual/entity-alignment retrieval,
   which is the closest published task analog.
   - **Flagged as a trap:** Shared Nearest Neighbor / simhubIN reduced hub SKEW but *impaired*
     classification accuracy in the same benchmark — hub-symmetry is not automatically the same
     objective as ranking accuracy; the cell below must gate on the actual filtered Hits/MRR
     metric, never on a hub-symmetry proxy.
4. **KG-embedding precedent (direct, verified via fetch):** Obraczka & Rahm (KEOD 2021) show hub
   status in KG embeddings correlates with entity frequency/degree in the training graph — the
   SAME compounding this note found by direct recompute — and evaluate MP/LS/NICDM/CSLS for entity
   alignment, reporting hubness-reduced NN search "recoverable at practically no added cost."

**Popularity/prior-bias mechanism (verified + reasoned, important correction to the naive "just
apply logQ" instinct):** the classic logQ sampled-softmax correction (Yi et al. 2019) fixes bias
introduced by estimating the softmax denominator from SAMPLED negatives. The reframe cell's FROZEN
scorer already trains with EXACT full softmax over the whole (<=300-object) candidate set — logQ's
target mechanism is very likely absent. The correlated bias here is better explained by (i) plain
ERM/cross-entropy under a skewed TRAINING label prior baking that skew into P_train(y|x) even under
exact normalization, and (ii) the embedding-geometry hubness effect above, which the lit-scan
independently confirms COMPOUNDS with label-frequency (popular items acquire systematically larger
embedding norms / more central positions — Wu et al. *TOIS* 2023; arXiv:2504.04752 2025). The
correctly-matched training-free fix for (i) is **post-hoc logit adjustment** (Menon et al., "Long-
Tail Learning via Logit Adjustment," ICLR 2021): shift test-time logits by `-tau * log(pi_y)` where
`pi_y` is the training-label prior — same shape as a log-prior subtraction but targeting label-prior
mismatch under full softmax, not sampled-negative bias. Reported magnitude in the literature for
this family of corrections is real but moderate: roughly mid-single-digit to low-double-digit
accuracy-point recoveries (long-tail logit adjustment: ~7-10 top-1 points on ImageNet-LT-style
benchmarks; recommendation debiasing losses: ~1-17% relative NDCG/Recall gains depending on
method). **Heavier, training-time complement (Stage 2 if the cheap rescore under-delivers):**
hard-negative mining (Karpukhin et al., DPR, EMNLP 2020; Xiong et al., ANCE, ICLR 2021) —
deliberately re-mine the model's current highest-scoring WRONG candidates as explicit negatives and
continue training; at a few-hundred-candidate scale this needs no ANN index (exhaustive rescoring
every epoch is trivial), so it is a lightweight continued-fine-tune, not a retrain from scratch.
Reported magnitude is larger (DPR: 9-19 percentage points top-20 retrieval accuracy over sparse
baselines; ANCE: >20% relative NDCG gains) but requires an actual training loop, unlike the
rescoring options above.

---

## 3. ENVELOPE — falsifiable cell spec (SPEC ONLY, no dispatch)

**Proposed cell name:** `exp_schema_relation_hubness_debias_rescore_v1`

**Design (reuse, don't rebuild):** IDENTICAL harness to
`exp_schema_relation_hitsatk_mrr_reframe_v1.py` — same V-scan {100,300,1000}, same relations
(AtLocation, CausesDesire semantic; DerivedFrom watchdog), same 2 encodings, same 3 seeds, same
FROZEN/JOINT/KNN slots, same paired REAL/SHUFFLED arms, same inductive/transductive modes, same
`filtered_ranks`/`rank_metrics` functions verbatim. **The ONLY change:** before ranking, apply a
FIXED (pre-registered, not tuned-for-pass), two-term post-hoc rescoring to the already-computed
(T,V) score matrix:

```
s'(t, j) = s(t, j)  -  CSLS_term(t, j)  -  tau * log(train_freq(j) + eps)
```

where `CSLS_term(t,j) = mean_topk_row_sim(t) + mean_topk_col_sim(j)` (standard CSLS form, k
pre-registered at k=10 matching the parent's own KNN_K reference slot — no new hyperparameter
search), and `tau` fixed at 1.0 (the standard logit-adjustment default, Menon et al. 2021) — both
values fixed BEFORE running the FULL cell, exactly as the reframe cell fixed its own hyperparameters
verbatim from its parent. Compute overhead versus the already-landed reframe cell: two vectorized
matrix reductions (row-mean-of-topk, col-mean-of-topk) plus a per-column log-frequency subtraction
— negligible next to the existing FROZEN/JOINT training cost, and requires ZERO additional
training (this is even cheaper than the reframe cell itself, which changed the eval metric but
still needed the same training loop; this cell reuses that identical training loop and only adds a
rescoring step before the argsort). **Both terms are the training-free, test-time-only variant of
their respective corrections** (post-hoc CSLS rescoring; post-hoc logit adjustment per Menon et al.
2021's inference-time-shift formulation, NOT their alternative train-time loss modification) — this
is deliberately the CHEAPEST test in the family, run first. The heavier, training-based variants
(train-time logit-adjustment loss; DPR/ANCE-style hard-negative mining re-mined from the current
checkpoint, trivial at V<=1000 with no ANN index needed) are staged as the Stage-2 fallback below,
not run in this cell.

**New discriminator-fires controls (positive + null, mirroring the parent cell's discipline):**
- `synth_hub_signal`: construct a synthetic regime with skewed synthetic label frequency (one
  object over-represented ~10x in training, by construction) layered on top of the parent cell's
  existing `synth_rank_signal` linear-content generator. The rescore must recover Hits@1/MRR rms
  materially above the UNCORRECTED score on this synthetic positive control (proves the correction
  mechanism fires when hub bias is present by construction).
- `synth_hub_null`: same linear-content generator with UNIFORM synthetic label frequency (no hub
  bias by construction). The rescore's Hits@1/MRR rms must stay within +/-0.02 of the uncorrected
  score (proves the correction does not manufacture false signal / does not hurt when there is
  nothing to correct — directly guards against the "hub-symmetry improves but accuracy doesn't"
  trap the lit-scan flagged for SNN/simhubIN).

**HP_SCOPE:** identical exclusion as parent — bands apply to `best-of-{FROZEN,JOINT}
REAL/inductive/FILTERED, SEMANTIC rel x enc @ V>=300`; KNN/DerivedFrom/SHUFFLED/POP remain
references/watchdogs/controls, not HP-eligible.

### Falsifiable predictions

**HARD-PASS** (the rescore converts the MIDDLE_BAND into a genuine broad win): best-of-{FROZEN,JOINT}
filtered **MRR real_minus_shuf(inductive) >= 0.15** **AND** filtered **Hits@1 real_minus_shuf shows
a material lift of >=0.05 absolute over the matched UNCORRECTED (parent reframe cell) Hits@1 rms**
on the same seed/config — both holding on >=2 relations (AtLocation + CausesDesire) x >=2 encoders
(bge + gsbc) at V>=300, AND Hits@10 rms does not regress below 0.20 (non-regression guard on the
metric that already mostly passed). Both `synth_hub_signal`/`synth_hub_null` discriminators must
fire as specified above.

**HARD-FAIL** (hub/popularity debiasing is not the fix — the residual is genuinely elsewhere):
best-of-{FROZEN,JOINT} filtered MRR rms improvement over the UNCORRECTED reframe cell's own MRR rms
is **<=+0.02 absolute** on EVERY semantic rel x enc cell at V>=300 (i.e. rescoring measurably fails
to move MRR at all) — would falsify the hub/popularity diagnosis as the dominant lever and would
redirect to the heavier levers: (i) DPR/ANCE-style hard-negative-mining continued-training (the
training-time complement identified above), or (ii) the deprioritized resolution-increasing
representation lever, in that order.

**MIDDLE-BAND** (real but partial — the most likely outcome given the reframe cell's own history of
landing MIDDLE, and the lit-scan's own "mid-single-digit to low-double-digit" typical magnitude for
this class of correction): MRR rms improvement over the uncorrected cell in **(+0.02, +0.15)**, or
Hits@1 lifts materially but MRR still falls short of 0.15 on one of the two relations. This would
motivate staging the heavier, training-based complements as the next iteration on the SAME
diagnosed hub set — train-time logit-adjustment loss (Menon et al. 2021's loss-modification
variant, for relations like CausesDesire where the residual-decomposition above shows label-prior
dominates) and/or DPR/ANCE-style hard-negative-mining continued-fine-tune re-mined from the current
checkpoint (for relations like AtLocation where genuine geometric hubness survives frequency-
removal) — rather than declaring the question closed either way.

**Cardinality / compute:** same `EXPECTED_N_UNITS` structure as the parent reframe cell (rescoring
adds no new units, only a post-processing step per unit); same compute class; expect similar
wall-clock (~7-10 min FULL), since the training loop is unchanged and the rescore is O(candidates^2)
at V<=1000 — trivial.

---

## Cheap decisive test

This note's own 3-seed x 2-relation off-disk recompute of hubness concentration + train-frequency
correlation (Section 1) IS the cheap decisive test for WHETHER the hub/popularity diagnosis is real
(answer: yes, robustly, 6/6 seed-relation cells). The proposed cell above is the next cheap test —
whether CORRECTING that diagnosed bias actually recovers the MRR floor — and it is itself cheap
(no training-loop change, a vectorized rescoring step only), consistent with the "cheap first, heavy
second" discipline already established by the reframe cell that triggered this drill.

## Cross-thread synthesis

- Directly extends `notes/research_reframe_rank_set_prediction_one_to_many_ceiling_2026-07-05.md`
  (which diagnosed near-miss content-neighbor competition qualitatively and flagged
  sparse-coding-compressed-sensing as one open adjacency, not the answer) by giving that
  "near-miss competition" a precise, quantified, externally-precedented name (hubness +
  popularity/label-prior bias) and a correspondingly precise, cheap fix.
- Does NOT re-open the richer-content HARD_FAIL (`exp_schema_relation_richer_content_vscan_v1`) or
  re-litigate CLS-dual-store — this is a scoring-layer correction on the SAME content
  representation and SAME trained scorer, not a new representation claim.
- Evaluated attractor/CA3-style cleanup (candidate (c)) on its merits per
  [[feedback-dont-dismiss-adjacent-methods]] rather than dismissing it; the data-grounded reason it
  is not the chosen mechanism here (basin depth scaling with reinforcement frequency, per classical
  Hopfield capacity theory, would likely compound rather than correct the measured hub bias) is
  itself a testable claim and should be revisited if the proposed cell HARD-FAILs — a debiased
  cleanup (apply the rescore FIRST, then cleanup on the residual) remains an open, not foreclosed,
  combination for a future drill.
- Sparse-coding/compressed-sensing (candidate (a)) was evaluated, not caged-off, and the crowding
  shape (training-frequency-correlated score inflation, not a sparsity/support-recovery pattern)
  does not match it; no further drill queued on that adjacency for THIS specific failure mode.

## Substrate-product implications

If the proposed cell clears HARD-PASS, the honest product story sharpens further than the reframe
cell alone allowed: "the substrate's relational ranking was not just being graded by the wrong
yardstick (exact-match) — a second, well-understood, textbook artifact of high-dimensional
similarity scoring (hubness/popularity bias, the SAME effect documented in cross-lingual embedding
retrieval and KG entity alignment) was suppressing its rank-1 accuracy, and correcting it recovers
most of the gap at near-zero additional compute — no retraining, no richer content." If it lands at
HARD-FAIL, the product-honest sharpening is: the true bottleneck is not the scoring convention at
all (two independent conventions now tried and found insufficient) but a genuine content/training
resolution ceiling, which motivates the heavier hard-negative-mining or richer-content path
explicitly, rather than another cheap reframe attempt.

## Citations (verified count: 8 new this round via 2 independent Sonnet lit-scan sub-agents,
cross-referenced against the 4 already banked in the prior reframe note)

1. Radovanović M, Nanopoulos A, Ivanović M (2010) Hubs in Space: Popular Nearest Neighbors in
   High-Dimensional Data. *JMLR* 11:2487-2531. — VERIFIED (fetched). Canonical hubness mechanism.
2. Schnitzer D, Flexer A, Schedl M, Widmer G (2012) Local and Global Scaling Reduce Hubs in Space.
   *JMLR* 13. — title/venue confirmed via search; lightly verified.
3. Feldbauer R, Flexer A (2019) A comprehensive empirical comparison of hubness reduction in
   high-dimensional spaces. *Knowledge and Information Systems*. — VERIFIED (fetched, concrete
   benchmark numbers used above).
4. Zelnik-Manor L, Perona P (2004) Self-Tuning Spectral Clustering — origin of Local Scaling.
   Cited via Feldbauer & Flexer; not independently re-fetched.
5. Conneau A et al. (2018) Word Translation Without Parallel Data. *ICLR* — origin of CSLS.
   Recalled/lightly verified via search.
6. Obraczka D, Rahm E (2021) An Evaluation of Hubness Reduction Methods for Entity Alignment with
   Knowledge Graph Embeddings. *KEOD*. — VERIFIED (fetched). Direct KG-embedding precedent: hub
   status correlates with entity frequency/degree in the training graph.
7. Yi X et al. (2019) Sampling-Bias-Corrected Neural Modeling for Large Corpus Item
   Recommendations. *RecSys*. — VERIFIED (fetched abstract/mechanism). Origin of logQ correction;
   argued above to NOT be the matched mechanism here (full softmax, not sampled).
8. Menon AK et al. (2021) Long-Tail Learning via Logit Adjustment. *ICLR* (arXiv:2007.07314). —
   VERIFIED (abstract fetched). The correctly-matched post-hoc correction for label-prior mismatch
   under exact full softmax; used above as the `tau*log(pi_y)` term in the proposed rescore.
9. Karpukhin V et al. (2020) Dense Passage Retrieval for Open-Domain Question Answering. *EMNLP*.
   — VERIFIED (fetched). Hard-negative-mining precedent (Stage-2 heavier fallback).
10. Xiong L et al. (2021) Approximate Nearest Neighbor Negative Contrastive Learning (ANCE).
    *ICLR* (arXiv:2007.00808). — VERIFIED (fetched). Model-refreshed hard-negative mining.
11. Wu et al. (2023) On the Effectiveness of Sampled Softmax Loss for Item Recommendation. *TOIS*;
    and arXiv:2504.04752 (2025) Investigating Popularity Bias Amplification in Recommender
    Systems. — verified via fetch/search snippet; support the popularity-compounds-with-hubness
    claim (frequent items acquire larger/more-central embeddings).

Verified count: 8 new external citations this round (6 fetched directly, 2 lightly-verified via
search), all cross-checked by 2 independent Sonnet lit-scan sub-agents plus this note's own direct
recompute of the internal numbers (not asserted from the parent cell's metrics.json alone —
independently reproduced against `data/datasets/conceptnet5_en_100k.jsonl` and
`data/datasets/bge_small_schema_TEM_entities_v1.npz`, matching the parent cell's own seed/split
logic exactly, 3 seeds x 2 relations, all 6 cells confirming the same direction).

## P_deflated

**P_deflated(HARD-PASS as spec'd above) = 0.38** (raw ~0.55: well-precedented external mechanism
match with a direct KG-embedding-entity-alignment analog reporting "practically no added cost"
recovery, clean 6/6-seed-relation internal diagnostic support, genuinely cheap to test; -0.17
lit-scan calibration for this correction never having been tried on THIS substrate/task, and for
the reframe cell's own precedent of landing MIDDLE despite ALSO looking well-precedented on paper).

**P_deflated(at least MIDDLE-BAND, i.e. MRR rms lift > +0.02) = 0.50** (capped per novel-synthesis
discipline; raw estimate higher, ~0.70, given the mechanism-match strength, but capped).
