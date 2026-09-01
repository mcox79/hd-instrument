---
problem: grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice
status: SOLVED
bar: "A rigorous NEGATIVE is a full PASS if located: if retrieval-practice, faithfully built and exposure-matched, does NOT beat re-reading on this population, then the 59% wall is REPRESENTATION-bound (the trace can't encode the distinction) not ENCODING-SCHEME-bound -- name it, with the evidence (e.g. the retrieval scorer's own accuracy ceiling on these words), and hand the representation gap to reader_meaning_channel/ATL."
result: "REPRESENTATION-BOUND NEGATIVE (the brief's full-PASS-if-located outcome). Retrieval practice, faithfully built (Mozer 2009 MCM Eq.7 + a PBV meaning-retrieval variant), CANNOT select a WordNet-correct grounding above chance on the CONSOLIDATION_FAIL population: selection-AUC (fixed meaning representation) retrieve=0.486 [0.413,0.554] / 0.503 [0.461,0.543] (seed0/seed1), PBV=0.467 [0.402,0.530] / 0.488 [0.446,0.531] -- both CIs INCLUDE chance (0.5). Grounding precision is FLAT at the ~0.25-0.32 base rate across every scheme; n=716/685 CONSOLIDATION_FAIL words, 3000 modern sentences (simplewiki+news+science), scored blind on WordNet. FURTHER, owner-drilled to the bottom: the wall is representation-bound at the SELECTION level. For the ~78% of words where a correct anchor EXISTS (oracle), the correct anchor is RETRIEVABLE -- median rank ~3, top-10 recall ~85% -- under EVERY encoder incl. the full SYNTACTIC/dependency-parse encoder (so the encoder is NOT the wall), but it is NOT SELECTABLE by ANY read-out: nearest 0.21, background-subtraction 0.23, the landed distilled-substitutability axis (0.865 on its own instrument) 0.24, and a SUPERVISED logistic on top-K features (CV over held-out words) 0.22 (lift +0.008, all coefs ~0) -- vs the top-10 ceiling ~0.87. The signal separating the correct SENSE from the topical ASSOCIATE is genuinely absent from distributional co-occurrence; the lever is GROUNDED/sensorimotor input (reader_meaning_channel/ATL = Phase 1), NOT a better encoder or read-out. **DEMONSTRATED (not just inferred): re-ranking the retrieved top-K by GROUNDED-HUB similarity (the ATL hub-and-spoke feature vector -- 11 Lancaster sensorimotor + 3 Warriner affect dims) SELECTS the correct sense where NO distributional read-out could: rank-1 correct 0.32/0.35 vs distributional 0.24/0.27 (seed0/seed1, lift +0.08/+0.07), beating every distributional read-out (all 0.21-0.24), at ~78% grounded coverage of these words. So the fix is concrete and brain-faithful -- ground the sense-selection in sensorimotor+affective features -- and it is a partial lift (to ~0.33, not the ~0.87 ceiling), so richer grounding (Binder 65-dim / a learned grounded selector) + coverage for the ~22% uncovered abstract words is the remaining work."
full_lift: "THE FULL LIFT (2026-09-01, brain-foundational, two research drills): a pure GROUNDED sense-selection re-rank over the distributional shortlist (two-stage LASS, grounded-DOMINANT) roughly DOUBLES correct sense selection. 2-seed SMOKE, CI-separated BOTH seeds: distributional read-out ~0.20-0.28 -> grounded cascade ~0.35-0.48 (predicted-Binder-65 experiential spoke = the exp_selpref_unseen_lowdata_v1 extension of Binder-2016 to 24978 words rho 0.69; morphology-extended; distributional-fallback where uncovered). CONTROLS hold both seeds: info-free grounded-shuffle ~= distributional (CI includes 0 -> real grounding); RE-FUSING the distributional cue HURTS (fusion < grounded-alone) because the distributional cue is confidently-WRONG for sense (peaky about TOPIC not SENSE) -> the cascade is grounded-dominant NOT equal fusion; MEASURED-Binder-535 ~ PREDICTED-Binder on the human-rated slice (0.8-0.9 vs 0.1-0.2) -> not an imputation artifact. The UNSUPERVISED cascade (~0.47) MATCHES the SUPERVISED-over-grounded-features CEILING (0.41, shuffle-controlled) -> no supervision headroom; the brain-faithful mechanism extracts the full grounded signal. Brain basis PINNED: ATL hub-and-spoke (Lambon Ralph/Patterson/Rogers); reliability-weighted cue combination == product-of-experts (Ernst-Banks/noisy-channel); argmax = attractor basin (Rodd 2004); fast distributional shortlist -> slow grounded re-rank = LASS (Barsalou 2008). ACCUMULATION (the problem's literal name) is SECOND-ORDER for this population (precondition = coherent within-sense repetition, absent: coherence 0.09-0.13); selection-only is the near-complete brain-faithful answer. Honest bound: LARGE lift (~2x, CI-separated) but not to the within-set ceiling (1.0), ~0.45. Magnitudes are 2-seed SMOKE (read population is str-hash-randomized so only CI-separated DIRECTIONS are citeable at smoke); the full 3000-sentence 2-seed run is REMOTE (dropped). WIRE = additive default-off canonicalize_grounded (thresh stays on distributional cosine = no bar-relaxation); landing gate = end-to-end grounding-precision rises CI-separated above ~0.30."
floor: "Incumbent split-half RE-STUDY arm at EQUAL exposure (best-case, all traces at once): grounded-CORRECT rate 0.006 (seed0) / 0.004 (seed1) -- it grounds ~none of these words. Rate-independent info-free floor: random-selection AUC 0.447 / 0.456 for picking a correct grounding, which retrieval does not beat."
controls: "(1) exposure-matched RE-STUDY (incumbent split-half) -- retrieval's apparent recall gain over it is pure threshold-relaxation; (2) EXPOSURE-COUNT arm (strengthen every exposure, no retrieval gate) -- ties/beats retrieval, excluding 'the retrieval gate helps'; (3) info-free TWIN_SHUF (retrieval outcomes shuffled) and TWIN_RAND (random scores) -- retrieval does NOT beat them on grounded-correct; (4) DECISIVE rate-independent selection-AUC vs a random selector -- excludes 'grounds more words at base precision'; (5) PBV meaning-retrieval variant -- rules out a weak self-coherence retrieval; (6) m-quality-matched (hits-only vs full-bundle estimate) -- excludes 'a cleaner estimate'; (7) PPMI+SVD distributional representation probe (phi 0.302 vs bag-of-words 0.303, CI [-0.036,+0.036], not separated) -- excludes 'a richer target-word representation fixes it'; (8) population characterization -- excludes the brief's 'coherent repeated exposures' premise (mean split-half coherence 0.09-0.13; only 0.6-2% coherent-single-sense-with-anchor)."
files_changed: "experiments/exp_retrieval_practice_consolidation_v1.py (retrieval arms + decisive selection-AUC + PBV + distributional-representation probe + sense-splitting probe + ORACLE anchor-ceiling decomposition + ENCODER diagnostic with read-out re-rankers [nearest/bg-subtract/abstain/distilled] + SUPERVISED re-ranker probe + GROUNDED-hub re-ranker probe [the demonstrated fix]); verification/test_retrieval_practice_consolidation.py; notes/problems/grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice/SOLVED.md; data/exp_retrieval_practice_consolidation_v1/{metrics.json,dist_probe.json,sense_probe.json,oracle_probe.json,encoder_probe.json,supervised_probe.json}"
reverify: ".venv/Scripts/python.exe verification/test_retrieval_practice_consolidation.py"
---

# Retrieval practice is the WRONG fix: the 59% CONSOLIDATION_FAIL wall is REPRESENTATION/STRUCTURE-bound, not consolidation-encoding-bound

**Bottom line up front.** I built the brief's proposed mechanism -- retrieval practice / the testing effect -- as
faithfully as the literature pins it, exposure-matched it against re-reading, and it does **not** ground the
repeated-exposure words the incumbent leaves un-grounded. It fails for a specific, measured reason: the words in the
`CONSOLIDATION_FAIL` population are not "coherent exposures that fail to accumulate durability." They are dominated by
polysemous words (need sense-splitting), words with no available meaning-anchor (need a bigger/ATL vocabulary), words
whose contexts genuinely do not cohere, and proper nouns (no target). None of those is a durability problem, and no
consolidation-encoding scheme -- retrieval-gated, exposure-count, or a richer distributional representation -- moves
grounding precision off the ~0.30 base rate. **This is the brief's explicitly-defined full-PASS negative: the wall is
representation-bound; the representation gap belongs to `reader_meaning_channel`/ATL and to two new sub-problems named
below.**

## What the brief said, and what the disk says (the disk wins)

The brief's premise (verbatim): "**59% `CONSOLIDATION_FAIL`** (>=4 coherent traces, the single-averaging consolidation
never grounds them)" and "why do repeated **coherent** exposures of the SAME word not accumulate into durable
grounding." I verified this on disk and it is **false for ~92% of the population**.

I re-derived the `CONSOLIDATION_FAIL` population from a live read (3000 modern sentences, the incumbent CI_050 forager +
the incumbent consolidation) and characterized every word in it (n=716 seed0 / 685 seed1):

| category | seed0 | seed1 | what it needs (NOT durability) |
|---|---|---|---|
| POLYSEMOUS (>=5 WordNet senses) | 293 (41%) | 301 (44%) | sense-SPLITTING (multiple hypotheses) |
| SINGLE-SENSE but NO eligible anchor | 205 (29%) | 169 (25%) | anchor-pool / ATL coverage |
| HAS anchor but INCOHERENT traces (split-half < 0.25) | 127 (18%) | 167 (24%) | the contexts genuinely don't cohere |
| proper-noun / no WordNet target | 77 (11%) | 44 (6%) | entity grounding (no common-word meaning) |
| **COHERENT single-sense WITH anchor** | **14 (2%)** | **4 (0.6%)** | the ONLY slice durability could help |

Mean split-half context coherence of the population is **0.125 (seed0) / 0.088 (seed1)** -- only **7.7% / 4.7%** clear
the incumbent's 0.25 gate. The traces are *not coherent*; that is *why* the split-half gate rejects them. The brief's
"coherent exposures" framing does not match the data.

## The mechanism I built (faithful copy of the operation; parameters swept)

Opening move -- how the brain does this (PINNED, from a literature drill): retrieval practice / the testing effect
(Karpicke & Roediger 2008 Science 319:966 -- once an item is retrievable, repeated **retrieval** drives ~80% one-week
retention while equal repeated **study** is indistinguishable from zero). The computational form I copied is
**Mozer, Pashler, Cepeda, Lindsey & Vul 2009 (NIPS, Multiscale Context Model), Eq. 7**: `Delta s = eps * (1 - s)`, with
`eps` LARGE on a successful retrieval and SMALL on failure/first-exposure. The `(1 - s)` term is Bjork & Bjork's New
Theory of Disuse (biggest boost when weakest; diminishing returns -> no runaway). It is **retrieval-gated, not
exposure-count-gated** -- exactly the shape needed to make grounding rise with coherent re-exposure instead of falling.
Layered on top: the 3-way outcome rule (Kornell/Hays/Bjork 2009 + Marsh 2007) -- HIT strengthens and folds the context
in; MISS-then-CORRECTED elaborates with a small increment; MISS-uncorrected does not fold noise into the estimate.

I copied the OPERATION exactly and SWEPT the parameters (hit/near-miss thresholds, `eps` ratio -- Mozer fit ~9 for
verbal paired-associate spacing, a different regime, so I swept it -- and the ground threshold), tuning them on a
held-out DEV word split to give retrieval its **best** shot, then reporting on the TEST split. Two retrieval variants:
self-coherence retrieval (test the new context against the running estimate) and **PBV meaning-retrieval** (retrieve the
current best-guess anchor and test whether the new context still points at it -- the closest analog to "retrieve the
answer, test it"). The mechanism itself is correct: on synthetic data a coherent word strengthens to s=0.95 and grounds;
an incoherent word stays at s=0.05 and does not (self-test).

The sense-assignment gate (canonicalize, 0.45) is held **unchanged** for every arm, so no arm can manufacture grounding
by relaxing the meaning bar (the brief's explicit prohibition -- DO NOT QUOTE #5).

## What I measured (the decisive, rate-independent test)

The naive comparison is a trap: retrieval grounds more `CONSOLIDATION_FAIL` words than the incumbent re-read (recall
0.38-0.62 vs ~0.02), but that is pure threshold-relaxation -- an exposure-count arm and an info-free random twin ground
just as many, and every scheme lands at the **same ~0.25-0.32 precision** (the ~35% WordNet-correct ceiling the whole
grounding channel already has). So absolute grounded-correct count rewards volume, not signal.

The decisive test holds the meaning representation FIXED (full-bundle for every word, so "does it ground correctly?" is
arm-independent) and asks: **does the retrieval-derived confidence rank the words that ground correctly above chance?**

| selection score -> AUC for a WordNet-CORRECT grounding | seed0 | seed1 |
|---|---|---|
| retrieval strength `s` | 0.486 [0.413, 0.554] | 0.503 [0.461, 0.543] |
| PBV meaning-retrieval strength | 0.467 [0.402, 0.530] | 0.488 [0.446, 0.531] |
| exposure-count strength | 0.429 | 0.434 |
| random | 0.447 | 0.456 |
| self-signal margin | 0.559 | 0.542 |

Both retrieval mechanisms' CIs **include chance (0.5)** on both seeds -- retrieval confidence is no better than a coin at
picking which words ground correctly. Quarantining misses to build a "cleaner" estimate did not help either (m-quality:
hits-only precision 0.265/0.304 vs full-bundle 0.247/0.317 -- inconsistent, no gain). And a **richer representation does
not rescue it**: a PPMI+SVD distributional embedding (the CLS/ATL manifold that reads substitutability at AUC 0.865 on a
curated instrument) built from the same read gives nearest-anchor precision 0.302 vs 0.303 for bag-of-words (CI
[-0.036, +0.036], not separated).

**Witness: 12/12 CHECKS PASS** (`verification/test_retrieval_practice_consolidation.py`, scaffold-free, fresh smoke read).

## Why the brain grounds these and we don't (the deep answer)

The brain *does* use retrieval practice, but the literature drill surfaced its precondition (Kornell 2009): retrieval
practice confers **zero** benefit when the cue-target relationship cannot support partial/semantic activation. For this
population that precondition fails in three brain-faithful ways, none of which retrieval practice addresses:
1. **Polysemy (41-44%)** -- the context points at *different* referents across encounters. A single carried hypothesis
   (PBV / retrieval practice) is the wrong shape; the brain splits senses (multiple competing hypotheses), it does not
   average or single-track them.
2. **No anchor / no target (25-29% + 6-11%)** -- the meaning isn't in the learner's known vocabulary yet (or is a named
   entity with no common-word meaning). Retrieval can't retrieve a meaning that isn't representable. The brain forms a
   new semantic hub entry / an episodic entity, not a stronger association to a missing target.
3. **Genuinely incoherent contexts (18-24%)** -- there is no stable single meaning to strengthen toward.

Retrieval practice is a **durability** mechanism. The `CONSOLIDATION_FAIL` wall is a **representation/structure**
problem. That is the whole finding.

## Pushing THROUGH the wall: the brain's actual mechanism for the largest slice (sense-splitting) also does not robustly break it

A located negative is not the end -- if the brain grounds these words, we should be able to once we understand how.
The brain *does* learn the largest slice (41% polysemous words) from reading, by a specific mechanism: it does NOT
average a word's contexts into one meaning; it **clusters them into separate senses** (multi-prototype; Rodd, Gaskell &
Marslen-Wilson 2004 separable attractor basins; Klein & Murphy 2001; Neelakantan 2014 online non-parametric sense
induction; Kulis & Jordan 2012 DP-means). So I built that operation -- online DP-means sense-clustering (assign a context
to the nearest sense-centroid if cos >= tau, else spawn a new sense; min-count-per-sense gate; tau swept) -- and ground
each coherent sense-cluster separately, with the 0.45 anchor gate unchanged. The pinned prediction (Rodd/Klein-Murphy):
clustering recovers senses only for **unrelated** (homonym-like) meanings, not for related regular-polysemy; the honest
control is a **random-cluster** twin at the same cluster sizes (split-half coherence is inflated for small clusters, so
"clusters cohere" is only meaningful *above* size-matched random).

**Result (full, 2 seeds, polysemous slice n=293/301): a small, seed-UNSTABLE effect that does NOT robustly break the
wall.**
- **Correct-grounding recovery** (grounds a WordNet-correct sense the single-average misses): seed0 **0.041** at split-
  precision 0.358; seed1 **0.003** at split-precision 0.444. Above the ~0.30 base precision when it fires, but ~4% in one
  seed and <1% in the other -- not robust.
- **Coherence recovery is confounded by cluster size**: DP-means clusters cohere (0.33-0.64) far above the whole bundle
  (0.086-0.089), and above the size-matched random twin in seed0 (0.33 vs 0.21 at tau=0.10) -- but the random twin
  **ties/beats** DP in seed1 (0.52 vs 0.37 at tau=0.10). The split-half metric is too size-sensitive at these cluster
  sizes to be a clean readout of "real senses."
- Relatedness stratification was clean at smoke (recovery only in homonym-like words) but did **not** hold at full scale.

**This deepens the verdict rather than overturning it** -- and the encoder/read-out drill below (owner-pressed: "nail
all of them") then LOCATED the binding constraint precisely. Even the brain's *correct* mechanism for the largest slice
cannot reliably find groundable senses here; the binding constraint is representational. **The next section pins WHERE:
it is NOT the encoder (any encoder retrieves the correct anchor to the top-10) -- it is the SELECTION signal, which is
absent from distributional context.** (An earlier draft of this doc guessed "a richer context encoder / the p2 parser
is the lever"; the head-to-head encoder test below REFUTED that guess -- read on.)

## The encoder is NOT the wall; the SELECTION is -- and no read-out fixes it (the decisive drill)

Owner-pressed to nail every rung, I asked: for the ~78% of words where a WordNet-correct anchor EXISTS in the vocabulary
(the ORACLE decomposition: ~78% representation-recoverable, ~8% coverage-bound, both seeds), WHERE does the encoder rank
it, and can any read-out select it?

**(a) The meaning is RETRIEVABLE -- the encoder is not the wall.** Head-to-head over the recoverable slice, the correct
anchor sits at **median rank ~3, top-10 recall ~85%** under EVERY encoder: incumbent hashed bag (signed 0.26 / graded
0.22 nearest), separable-raw full-D (no hash collision) 0.24, PPMI 0.22, PPMI+SVD 0.21, AND the full **SYNTACTIC /
dependency-parse structural encoder** 0.27. Capacity, frequency-weighting, dimensionality-smoothing and SYNTAX all
converge -- none beats the incumbent, and all put the correct anchor in the top-10 ~85% of the time. So a better encoder
(including the p2 parser track) is REFUTED as the lever, head-to-head.

**(b) But it is NOT SELECTABLE by any read-out.** On the retrieved top-K, every read-out lands at ~0.21-0.24 rank-1
correct vs the top-10 ceiling ~0.87: NEAREST 0.21, BACKGROUND-SUBTRACTION (remove the topical/frequency backbone) 0.23,
the landed DISTILLED substitutability axis (0.865 on its curated instrument) 0.24, and a SUPERVISED logistic over cheap
per-candidate features (cosine, background-subtracted cosine, anchor frequency, specificity/depth, rank), 5-fold
CROSS-VALIDATED over held-out WORDS, **0.22 -- lift +0.008 over nearest, all learned coefficients ~0.** Even supervision
cannot extract a selector from the distributional features.

**(c) Mechanism.** The nearest distributional neighbour is a SYNTAGMATIC (topical, co-occurrence) associate --
whisky->wedding -- not the PARADIGMATIC (substitutable, same-meaning) anchor whisky->brandy, which waits at rank ~3.
Selecting the paradigmatic anchor over the topical one needs a signal that is **genuinely absent from distributional
co-occurrence** for these hard (polysemous, low-coherence) words -- confirmed by the learned axis AND the supervised
probe both failing. **So the wall is representation-bound at the SELECTION level; the lever is a GROUNDED/sensorimotor
meaning signal (the `reader_meaning_channel`/ATL problem = Phase 1 of the long-term plan, sensorimotor spokes -> ATL
hub), NOT a better encoder, NOT a read-out re-ranker, NOT the consolidation operation, NOT retrieval practice.**

## THE DEMONSTRATED FIX -- grounded sense-selection (elimination -> proof; "exactly how")

A located negative that only *infers* the lever by elimination is not enough; the brain-foundational standard is to
*show* the brain's mechanism works. The ATL hub-and-spoke model (Lambon Ralph, Patterson, Rogers) says sense meaning is
an amodal hub fed by SENSORIMOTOR spokes -- so "whisky" and "brandy" are close via shared grounded features (amber
spirits you drink) while "whisky" and "wedding" are close only distributionally. **I tested it directly and it holds.**

Re-ranking the SAME retrieved top-K by GROUNDED-HUB similarity -- the project's `build_grounded_hub` teacher, an
ATL-shaped 14-dim vector (11 Lancaster sensorimotor dims: auditory/gustatory/haptic/visual/hand-arm/mouth/... + 3
Warriner affective dims: valence/arousal/dominance) -- SELECTS the correct sense where NO distributional read-out could:

| selector over the retrieved top-K (same population) | rank-1 correct (seed0 / seed1) |
|---|---|
| distributional nearest (incumbent) | 0.24 / 0.27 |
| every distributional read-out (bg-subtract / distilled / supervised) | 0.21 - 0.24 |
| **GROUNDED hub (sensorimotor + affective)** | **0.32 / 0.35 -- lift +0.08 / +0.07** |

at **~78% grounded coverage** of these words (84% of anchors). Both seeds. This is the POSITIVE demonstration: grounded
features carry the sense-selection signal that distributional co-occurrence does not, exactly as the hub-and-spoke model
predicts.

**EXACTLY HOW TO SOLVE THIS (concrete, actionable, brain-faithful, uses existing assets):** the reader retrieves a
distributional top-K (already ~85% contains the right meaning) and then SELECTS with a GROUNDED read-out --
`hdlab.distributional_meaning_channel.build_grounded_hub` (Lancaster + Warriner norms, already on disk) -- ranking the
candidates by grounded-hub similarity, not distributional cosine. That is the wire: a grounded sense-selection read-out
on top of the existing retrieval, which is precisely Phase-1 (sensorimotor spokes -> ATL hub).

**Honest bound:** it is a PARTIAL lift (to ~0.33, not the ~0.87 top-10 ceiling), and it only helps the ~78% with grounded
norms. So the demonstrated lever is real but not a full solution; the residual is richer grounding (Binder 65-dim
experiential; a learned grounded selector) and coverage for the ~22% uncovered (abstract words whose senses may need
affective/linguistic rather than purely sensorimotor grounding -- Barsalou/Vigliocco). That is the shape of the follow-on.

## THE FULL LIFT -- grounded sense-selection cascade (owner: "a full solution including a full lift")

Two research drills (`RESEARCH_sense_selection_mechanism.md`, `RESEARCH_accumulation_and_cross_situational_learning.md`)
turned the partial fix into a FULL, brain-foundational lift. The mechanism is a **pure GROUNDED sense-selection re-rank
over the distributional shortlist** -- a two-stage LASS cascade (fast distributional top-K shortlist -> slow grounded
select), grounded-DOMINANT. It roughly DOUBLES correct sense selection.

**Result (2-seed SMOKE, CI-separated both seeds; magnitudes wobble because the read population is str-hash-randomized, so
only CI-separated DIRECTIONS are citeable at smoke -- the full 3000-sentence 2-seed run is REMOTE, dropped):**

| selector over the retrieved top-K (unsupervised; same scoreable population, within-set ceiling 1.0) | rank-1 correct |
|---|---|
| DIST (distributional cosine -- the incumbent read-out) | 0.20 - 0.32 |
| GRD14 (14-dim sensorimotor+affect re-rank -- the earlier demonstrated fix) | 0.31 - 0.35 |
| **GRD65 / CASCADE (predicted-Binder-65 experiential re-rank, dist-fallback)** | **0.35 - 0.48** |
| GRD65_MORPH / CASCADE_MORPH (+ morphology backoff for the derived tail) | 0.35 - 0.47 |
| FUSE_BOTH (reliability-weighted dist+grounded fusion) | 0.31 - 0.39 (< grounded-alone) |
| GRD65_SHUF (info-free grounded shuffle -- the null) | ~= DIST (CI includes 0) |

CI-separated headline: **CASCADE_MORPH - DIST = +0.15 to +0.18, CI above 0, both seeds** (~2x DIST).

**Why it is the brain's mechanism (PINNED):** ATL hub-and-spoke (Lambon Ralph/Patterson/Rogers) -- sense meaning is an
amodal hub fed by grounded spokes; "whisky~brandy" share grounded features, "whisky~wedding" share only distributional
co-occurrence. Cue combination is reliability-weighted (Ernst & Banks 2002 / noisy-channel) == product-of-experts; the
argmax is the settled attractor basin (Rodd 2004); the two-stage shortlist->re-rank is LASS (Barsalou 2008).

**Three decisive controls (all hold both seeds):**
1. **Info-free grounded shuffle ~= DIST** (CI includes 0) -- the lift is REAL grounding, not the machinery.
2. **Re-fusing the distributional cue HURTS** (FUSE_BOTH < grounded-alone). Mechanistically important: reliability-
   weighting by peakiness OVER-trusts the distributional cue, which is *confidently WRONG* for sense (peaky about TOPIC,
   not SENSE). So the brain-faithful selector is grounded-DOMINANT, distributional as shortlist ONLY -- not equal fusion.
   (This is an evidence-driven refinement of the cue-combination literature, backed by the ablation.)
3. **Measured-Binder-535 ~ Predicted-Binder** on the human-rated slice (0.8-0.9 vs DIST 0.1-0.2) -- the lift is real
   experiential grounding, NOT an imputation artifact of the predicted table.

**No supervision headroom:** a SUPERVISED logistic over the SAME grounded features (5-fold CV, shuffle-controlled --
shuffled collapses to ~nearest) tops out at a CEILING of ~0.41; the UNSUPERVISED cascade (~0.47) MATCHES OR EXCEEDS it.
The brain-faithful mechanism extracts the full grounded sense-signal with no gold labels -- exactly what a wireable
inference-time mechanism needs (the supervised probe is a CEILING YARDSTICK ONLY, never a wire: training on WordNet-
correctness to then score on WordNet is grade-by-what-you-ground-by; the brain has no such teacher).

**The accumulation half (the problem's LITERAL name) is second-order for THIS population.** Drill 2 pins why at
mechanism depth: an accumulator's precondition is coherent within-SENSE repetition, and this population fails it
(coherence 0.09-0.13; 92% polysemy/no-anchor/incoherent). A per-word running mean = the incumbent's refuted single-
average; the brain carries MULTIPLE competing sense-hypotheses for polysemy (cross-situational learning: the single-
hypothesis "propose-but-verify" result is a monosemous-lab finding, does not transfer). Consolidation's honest value
here is variance-reduction of the noisy grounded read -> a steadier selector, foldable into the reliability weight -- no
separate machinery. **Selection-only is the near-complete brain-faithful answer for this population.** MORPHOLOGY
surfaced as a word-internal spoke for the abstract/derived tail (brightness<-bright) but adds only +0.005/+0.02 here
because the predicted-Binder table already covers ~86% of that tail. Calibration: incidental word-learning is
~15%/exposure (Nagy & Anderson), so "grounding doesn't accumulate" on a thin low-coherence corpus is partly EXPECTED.

**Honest bound + the wire.** The lift is LARGE (~2x, CI-separated) but not to the within-set ceiling (1.0) -- ~0.45, not
perfect; the residual is harder senses where grounded features don't separate + grounded-read noise. The wire is an
ADDITIVE default-off `canonicalize_grounded` sibling (`WIRE_PROPOSAL_grounded_sense_selection.md`; strategy lands, Q111):
distributional cosine SHORTLIST -> grounded-hub SELECT, with the grounding `thresh` kept on the distributional cosine so
it does NOT relax the grounding bar (the brief's prohibition). Its landing gate is the END-TO-END measurement: does
CONSOLIDATION_FAIL grounding PRECISION rise CI-separated above the ~0.30 distributional ceiling, 2-seed, info-free twin
loses, recall not bought by bar-relaxation (REMOTE).

## TOWARD THE CEILING -- how close to 1.0, understood intrinsically (owner: "as close to 1 as possible... every wall intrinsically")

The full-lift cascade reaches ~0.45 (within-set); the owner asked how far toward 1.0 we can push and to
understand every wall INTRINSICALLY. Researched (`RESEARCH_toward_ceiling_sense_selection.md`) + prototyped
+ fair-tested. Decisive answer:

**1. The ceiling is ~0.85, NOT 1.0 (a hard cap).** The correct anchor is only IN the distributional
shortlist ~85% of the time (cannot select what is not there); fine-grained WordNet human inter-annotator
agreement is ~0.70-0.80; best supervised all-words WSD ~0.80-0.83. Our wup>=0.5 scoring is coarse-
equivalent (ceiling ~0.90) but the shortlist cap dominates -> realistic ceiling ~0.85. The last 0.85->1.0
is a SHORTLIST-RECALL problem (a different lever), not selection.

**2. The selection algorithm is SATURATED** (unsupervised cascade ~0.47 == supervised-over-grounded-features
ceiling ~0.41). The only lever with headroom is making the grounded features OCCURRENCE-SPECIFIC (context-
conditioned) rather than one static per-word sense-blend (research-pinned: Barsalou situated conceptualization;
predictive-coding context pre-activation).

**3. Context-gating (the pinned lever) was PROTOTYPED TWO WAYS and FAILS on this population -- fair-tested,
2-seed, intrinsically understood:**
- `context_gated_probe` (g: occurrence-context d256-hashed-bag -> Binder-65): CTXGATE ~0.24 << GRD65_static
  ~0.39 (CI-sep below 0). FAIR controls: a MONOSEMOUS-only-trained g (avoids the blend-target circularity)
  STILL loses (~0.23 << 0.38); and with a VALID cross-word shuffle, CTXGATE ~= a random OTHER word's context
  (lift -0.0015, CI incl 0). The stored d256 HASHED occurrence context carries ZERO sense-discriminative signal.
- `situation_grounding_probe` (ground each occurrence by the mean Binder of its ACTUAL context WORDS -- the
  rich, un-hashed version): SITU ~0.29 STILL << GRD65_static ~0.37-0.45 (CI-sep below 0, both seeds). Real
  context words carry a TINY real signal over cross-word-shuffle (+0.03/+0.045; seed1 CI-separated) -- more
  than the hashed d256's zero -- but an order of magnitude too small to beat static grounding.

**4. WHY (intrinsic):** for these hard words, averaging the experiential features of a word's NEIGHBORS is a
BLURRIER meaning cue than the word's OWN static grounding -- context here DILUTES rather than SHARPENS,
because this population's contexts are genuinely low-coherence (0.09-0.13). g(thin/noisy occurrence context)
is a noisy estimate of the word's grounding, strictly worse than the clean per-word average (which IS that
estimate averaged over all contexts). Context-gating is the correct brain mechanism but is bottlenecked by
(a) the occurrence-context REPRESENTATION and (b) the intrinsic incoherence of THESE words' contexts, plus
(c) the per-word any-sense metric under-rewards occurrence-sense-specificity.

**5. THE REAL WALL to ~0.85 is a SENSE-INDUCTION wall, not a selection/grounding wall.** To beat static you
need PER-SENSE grounded prototypes (split a word's occurrences into senses, ground each separately) + a per-
occurrence sense-correctness metric. Sense-splitting is the sub-problem already shown UNSTABLE here (recovery
0.4-4%, seed-dependent, W9). That is the identified, hard, currently-open gap -- NAMED, not hand-waved. Plus
shortlist-recall for the final stretch. So the practical best remains the static grounded cascade (~0.45
smoke, ~0.85 asymptote gated by robust sense induction).

**6. THE DEEPEST UNDERSTANDING (4th drill, `RESEARCH_breakthrough_sense_grounding_from_limited_exposure.md`):
the ~0.45 plateau is the ceiling of FEATURE-COSINE, and sense selection is TAXONOMIC/RELATIONAL.** Pinned,
doubly-dissociated brain fact: TAXONOMIC relations (whisky~brandy, same-kind) live in the ATL hub; THEMATIC
relations (whisky~wedding, co-occur) live in TPJ/pMTG (Mirman 2017; Schwartz 2011 PNAS). Our distributional
channel is a THEMATIC machine; the correct-SENSE signal is TAXONOMIC -- which is WHY grounded (Binder) features
doubled selection (they are the taxonomic substrate). BUT we reach the taxonomic system with a FLAT FEATURE-
VECTOR COSINE over a blend -- a lossy proxy for what the ATL taxonomic system IS: a RELATIONAL is-a graph.
EMPIRICAL PROOF the feature-cosine family is EXHAUSTED: FIVE controlled prototypes -- per-word blend (~0.45),
context-gated (loses), occurrence-clustered (+0.05 over random), per-sense GLOSS grounding (`gloss_grounding_probe`:
GLOSS_PERSENSE 0.27-0.29 <= blend 0.29-0.37 both seeds; GLOSS_ANYSENSE upper bound == random-gloss multi-try
= ZERO real per-sense structure) -- ALL plateau or fail. You cannot recover a RELATIONAL structure by averaging
feature vectors at ANY granularity. **THE BREAK-THROUGH is a change in KIND: RELATIONAL selection over a
taxonomic GRAPH** (WordNet IS one; personalized-PageRank/Lesk seeded by OBSERVED grounded anchors; per-sense
gloss vectors as seed nodes, NOT the selection cosine). **HONEST BLOCKER: our correctness metric IS WordNet-
relatedness, so a WordNet-graph selector is CIRCULAR against it (grade-by-what-you-ground-by).** Validly building
+ testing the relational lever requires a GOLD per-occurrence sense benchmark (modern sense-annotated corpus,
independent of the graph, MFS baseline) -- ALREADY a standing priority (migrate the reader eval off the proxy).
NEXT PROBLEM (well-scoped): (1) gold-sense WSD eval; (2) relational gloss-grounded selector measured on it with
beat-MFS + seed-shuffle->chance + hold-out-target-synset controls. New probes: `--gloss-probe` (+ earlier
`--context-gated-probe`, `--situation-probe`, `--sense-cluster-probe`).

**7. BOTH BREAK-THROUGH LEVERS PROTOTYPED + FAIL -- the reading context is EXHAUSTED (the converged, controls-
verified conclusion).** `relational_graph_probe` (Lever 2, the change-in-KIND): score each candidate anchor by
TAXONOMIC coherence (shared-hypernym-ancestry Jaccard over WordNet) to the KNOWN grounded anchors OBSERVED in the
word's contexts. THE VALID (metric-INDEPENDENT) CONTROL -- RELATIONAL(real seeds) vs RELATIONAL(shuffled seeds
from a random other word) -- is NULL both seeds: 0.223 vs 0.239 (seed0), 0.247 vs 0.302 (seed1), CI incl 0. The
observed context of these words carries NO more sense signal than a RANDOM word's context. RELATIONAL also LOSES
to GRD65_static (0.22-0.25 vs 0.34-0.42, CI-sep). So BOTH families are eliminated OVER THE READING CONTEXT: the
FEATURE-COSINE family (blend/context/cluster/gloss, 5 prototypes) AND the RELATIONAL-GRAPH family -- and both for
the SAME root reason, now controls-proven: these are CONSOLIDATION_FAIL words BECAUSE their contexts are low-
coherence (0.09-0.13), so any mechanism leaning on that context (feature-average OR graph-seed) is no better than
random. The static per-word grounding wins BECAUSE it ignores the incoherent context. DECISIVE, EMPIRICALLY-FORCED
CONCLUSION: no mechanism over these words' reading context can break the plateau -- the break-through must bring
RICHER KNOWLEDGE FROM THE SHELF (definitional/relational grounding per hard word; "a definition is worth many
contexts", Borman-Lupyan), validly proven on a GOLD per-occurrence sense benchmark (escape the WordNet
circularity). New probe: `--relational-probe`.

**8. THE WALL + BREAK-THROUGH DEMONSTRATED ON GOLD, WORDNET-INDEPENDENT LABELS (owner "test and show proof").**
New cell `experiments/exp_sense_wall_breakthrough_wic_v1.py` on WiC (Word-in-Context; human same/different-sense
judgements, balanced -> floor 0.50; escapes the WordNet-relatedness circularity). Reused `tools.load_wsd_
benchmarks.load_wic`; prior WiC work (`exp_frame_sense_wic_v1`, a CONSTRUCTION/frame disambiguator) HARD_FAILED,
and `exp_context_conditioned_sense_selection_v1/v2` HARD_FAILED -- both INDEPENDENTLY confirm the context wall.
RESULT (dev n=638 / test n=1400, CI, leak-free):
- **THE WALL**: thematic co-occurrence context (CTX_OVERLAP) = 0.52 (CI includes the 0.50 floor); simple gloss-
  word-overlap (Lesk) = 0.52-0.53; info-free twin = 0.52 -- ALL at chance. Co-occurrence context AND simple
  definitional overlap CANNOT discriminate sense.
- **THE BREAK-THROUGH**: the RICHER definitional representation -- GLOSS-EMBEDDING (mean predicted-Binder-65 of
  the DEFINITION words, matched to the context's grounded vector) -- = 0.600 (dev) / 0.586 (test), CI-SEPARATED
  above the 0.50 floor AND above every context arm (+0.05-0.08). Modest (WiC is hard; human ~0.80) but REAL,
  gold-labeled, leak-free, controlled (mis-seeded twin at chance). The break-through = embedding the DEFINITION
  into grounded EXPERIENTIAL space -- definitional knowledge (the sense inventory) + grounded features (the
  taxonomic substrate) TOGETHER clear the wall where neither context nor gloss-words alone can.
- **HONESTY CATCH (reusable, load-bearing):** the FIRST run scored 0.83 -- a LEAK: WiC was CONSTRUCTED FROM
  WordNet/Wiktionary sense EXAMPLE sentences, so including `synset.examples()` in the gloss bag let each eval
  sentence match its own source synset (dev 0.517 -> 0.831). Caught by the "verify a too-good number vs the
  human ceiling 0.80" discipline; examples EXCLUDED -> the honest 0.52-0.60. THE VERIFY-TOO-GOOD RULE PAID OFF.
So: the wall is real and gold-confirmed; the break-through (grounded definitional knowledge) is real, modest,
and leak-free -- the honest proof, and the concrete lever to scale (richer sense embeddings / graph PPR toward
the ~0.68 knowledge-based band, human ~0.80). Cell: `--self-test` PASS; `--mode full`.

**8b. THE FINAL OPTIMIZATION prototyped + measured (owner "show the prototype for the final optimization").**
Three leak-free, shelf-only (no LLM) optimizations added to the cell:
- **OPT_EXTGLOSS_EMBED (WINNER): extended-gloss embedding** -- expand each sense's definition with its
  hypernym/hyponym DEFINITIONS before grounding (extended Lesk x Binder). 0.591 -> **0.619 (dev) / 0.594
  (test)**, CI-separated above the wall and above plain gloss-embedding. Richer definitional context = better.
- **OPT_GRAPH_taxonomic: shared-hypernym-ancestry to the context's concepts = 0.508 dev / 0.499 test = CHANCE**
  -- GOLD-CONFIRMS the relational_graph_probe seed-shuffle null: taxonomic-graph-OVER-CONTEXT carries no sense
  signal (the context concepts are too noisy). Same wall, now on gold labels.
- **OPT_FUSION (embed + graph) HURTS** (0.582 dev / 0.538 test) -- the chance graph signal drags the embedding
  down; the best is grounded-definitional ALONE.
CONCLUSION: the winning final optimization is GROUNDED-DEFINITIONAL, made RICHER (extended gloss), capping
~0.62 with our shelf embeddings; the graph-over-context and fusion routes are dead (gold-confirmed). Reaching
the ~0.68 knowledge band needs richer SENSE embeddings than mean-Binder (LMMS-style; unavailable w/o an LLM) --
the honest ceiling of the shelf-only approach. Cell: `--self-test` PASS; `--mode full`.

**8c. HONEST CORRECTION (owner "deeply understand sense embeddings + prototype glass-box before submission" ->
the verification caught an OVER-CLAIM). New cell `experiments/exp_glassbox_sense_embeddings_wic_v1.py` builds
glass-box sense embeddings (LMMS analog, NO LLM) from SemCor usage: SENSE_DIST (Yarowsky/Naive-Bayes context-
word distribution), SENSE_GRND (mean-Binder of usage contexts), FUSION, gloss backoff. Added the CONTROL THE
FIRST WiC CELL LACKED: a per-method MIS-SEEDED TWIN (assign side-2 from a RANDOM other context) = the MFS-
AGREEMENT baseline (how well you do by knowing the word's sense inventory / dominant sense, IGNORING the
specific context). RESULT (full dev 638 / test 1400): the twin sits at ~0.56-0.61, NOT the naive 0.50 floor.
Against the twin, `real - twin` is TINY and inconsistent: dev NO method beats its twin (ext-gloss +0.020 ns,
grnd +0.044 ns, fusion +0.031 ns); test only ext-gloss barely (+0.034, CI[0.002,0.065]). SENSE_DIST/GRND/FUSION
(usage-based) do NOT beat ext-gloss, so the LMMS "usage>gloss" insight does NOT hold glass-box here.
**THEREFORE the §8/§8b "0.62 CI-separated break-through" was measured against the WRONG baseline (0.50 floor);
against the honest MFS-agreement baseline (~0.59) the real per-context definitional signal is only ~+0.02-0.03,
MARGINAL/inconsistent.** DEFLATED HONEST VERDICT: on gold WiC, glass-box sense embeddings (usage OR gloss) do
NOT clear the wall beyond the DOMINANT-SENSE baseline; the wall demonstration (context ~ chance) stands, but the
"definitional break-through" is mostly MFS-agreement with a marginal real edge. Real per-context WSD needs a
CONTEXTUAL representation (LLM) barred at inference. LESSON (reusable): compare to the MFS-AGREEMENT twin, NOT
the naive floor -- the naive floor over-credits any method that just picks the dominant sense. Cell: `--self-
test` PASS; `--mode full`.

**8d. BOTH BREAK-THROUGH PATHS PROTOTYPED + TESTED (owner "test both right now"). Cell
`experiments/exp_contextual_encoder_paths_wic_v1.py` on gold WiC vs the HONEST baseline (floor 0.50 AND
MFS-agreement ~0.59), UNSUP (cosine-threshold, tau tuned on train) + SUPERVISED (logistic on [|v1-v2|,
v1*v2] pair features):
- PATH A (glass-box, PREFERRED): contextual encoder from DEPENDENCY-TYPED context (structured_context_
  learner's lever; spaCy parse + GloVe filler embeddings, NO LLM) vs FULL-bag GloVe. DEP dev/test unsup
  0.536/0.529, sup 0.558/0.524; FULL unsup 0.560/0.552, sup 0.600/0.574. NEITHER clears MFS-agreement CI-
  separated. Dependency-typing HURT vs full-bag -- the syntactic lever helps SIMILARITY (SimLex) not SENSE
  (WiC). Glass-box context is too weak for per-context sense.
- PATH B (off-the-shelf contextual): all-MiniLM-L6-v2 cached contextual target-token embedding (LLM AT
  INFERENCE -> bars the invariant; tested to measure the ceiling). Unsup 0.571/0.586, sup 0.556/0.598. Also
  does NOT clear MFS-agreement CI-separated. (Low vs the field's ~0.68 because MiniLM is a small frozen
  sentence model + a simple classifier; ~0.68 needs a LARGE contextual LM FINE-TUNED end-to-end = the most
  invariant-violating option, still not a clean solve.)
*** RETRACTED CONCLUSION (see 8e): the "LLM-gated" verdict below was an OVERGENERALIZATION FROM A WEAK
PROTOTYPE (the exact "don't generalize a narrow failure to impossible" failure mode). Both prototypes used
FEATURE-VECTOR COSINE over averaged bags -- NOT the brain's mechanism. The brain does SPREADING ACTIVATION
over a relational graph; when that is actually built (8e) it CLEARS the wall glass-box. Keep 8d only as the
record of the weak-prototype results; the CONCLUSION is WRONG. ***
[SUPERSEDED] DECISIVE VERDICT: NEITHER path, unsupervised OR supervised, clears the dominant-sense (MFS-
agreement ~0.59) baseline AS PROTOTYPED (feature-cosine). Path A GloVe-cosine 0.53-0.60; Path B frozen-MiniLM-
cosine 0.56-0.60. [The "LLM-gated / no glass-box break-through" conclusion is RETRACTED -- see 8e.] Cell:
`--self-test` PASS; `--mode full`.

**8e. THE ACTUAL BREAK-THROUGH -- BRAIN-FAITHFUL, GLASS-BOX, LM-FREE: PERSONALIZED-PAGERANK SPREADING
ACTIVATION over the WordNet++ graph (owner "not LLM-gated... do deep research to identify the path").**
Drill `RESEARCH_real_path_to_per_context_wsd.md`: the brain does per-context sense selection by SPREADING
ACTIVATION over a relational semantic network (Collins & Loftus 1975) that SETTLES into a sense attractor
(Rodd 2004), context pre-activating candidates (Kuperberg). Personalized PageRank == random-walk-with-restart
== the DIFFUSION FORM of spreading activation (PINNED bridge) -- so PPR-over-WordNet is simultaneously brain-
faithful, glass-box, LM-FREE, and above MFS (UKB ~67 / SyntagRank ~72 vs MFS 65.2 all-words). Our earlier
methods used vector COSINE (the wrong op) on a problem that is relational/graph; we OWNED the graph (WordNet)
but used it as a flat lookup. Cell `experiments/exp_ppr_spreading_activation_wsd_wic_v1.py` (UKB ppr_w2w:
personalize the walk on the context words' synsets EXCLUDING the target's own, damping 0.85, 30 iters, read
out the target synset with max activation; WordNet++ = relations + GLOSS edges).
**FULL-N result (believe full over smoke -- the smoke n=150 gave 0.673 and OVERSTATED it):** WiC dev (n=638)
PPR_wordnet++ = **0.618** CI[0.580,0.657]; test (n=1400) = **0.593** CI[0.568,0.618]; floor 0.500. NO_GLOSS
ablation dev = 0.569 (gloss edges help +0.05 -> load-bearing, the pinned trap confirmed). PPR BEATS THE NAIVE
FLOOR (0.50) CI-SEPARATED and edges above the MFS-agreement level (~0.59), glass-box + LM-FREE + brain-faithful
-> **"LLM-gated" is REFUTED** (the right mechanism beats the naive floor and all the feature-cosine methods).
HOWEVER the context-shuffle TWIN = 0.571 (dev) / 0.570 (test); real-minus-twin = +0.047 / +0.023, NOT CI-
separated -> the per-THIS-context signal is MARGINAL: most of the above-floor gain is the graph's structural
bias, not disambiguating this occurrence. HONEST VERDICT: the mechanism is RIGHT (brain-faithful spreading
activation, above floor, gloss-edges load-bearing) but plain WordNet++ PPR AS BUILT (undisambiguated gloss
edges, a SIMPLIFIED UKB) does NOT decisively clear the twin at full scale. This MOTIVATES the augmentations
(NEXT_the_living_grounded_semantic_graph.md): a proper UKB uses a DISAMBIGUATED gloss corpus + SyntagNet
(SyntagRank ~72 vs UKB ~67 all-words); + grounded nodes (#1, GROUNDED_PPR arm) + the learned graph (#2/#3).
LESSON: I mistook a WEAK-IMPL (feature-cosine) failure for "LLM-gated" (WRONG -- graph diffusion beats it); AND
the smoke (0.673) overstated the full number (0.618) -- believe full over smoke. Cell: `--self-test` PASS.

**8f. THE CLOSER -- DISAMBIGUATED gloss edges CLEAR THE TWIN (mechanism-done-right; owner "do all").**
`--gloss-compare` (full dev, WordNet++ with gloss_cap=1 MFS-disambiguated vs gloss_cap=3 undisambiguated):
- undisambiguated (g3): 0.618, twin 0.571, real-twin +0.047, real>twin=FALSE (the marginal 8e result).
- **MFS-DISAMBIGUATED (g1): 0.652 CI[0.614,0.690], twin 0.574, real-twin +0.078, real>twin=TRUE.**
Disambiguating each gloss word to its MFS (1 clean edge, not top-3 noisy) both RAISES accuracy (+0.034) AND
CI-SEPARATES above the context-shuffle twin -- the twin stays flat (0.574) while accuracy rises, so the +0.078
is GENUINELY context-driven (uses THIS occurrence's context, not structural bias). **DECISIVE, HONEST VERDICT
for the whole thread: "LLM-gated" is REFUTED -- the brain's actual mechanism (spreading activation over a
relational graph), built PROPERLY (disambiguated glosses), reaches the field's knowledge-based-WSD level (~0.65
vs LMMS 0.677 which NEEDS a live LLM) glass-box + LM-free, and CLEARS the strict twin baseline.** The
augmentation ladder works: the FIRST rung (disambiguated glosses) already clears the bar; SyntagNet/ConceptNet/
grounded-nodes/the learned graph (the #2/#3 Problem) are further rungs toward the ~0.72+ ceiling. Make g1
(disambiguated) the default. Cell: `--self-test` PASS; `--gloss-compare --mode full` (~320s, graph cached).

## Adjacent-component evaluation (brain-foundational fidelity + opportunities, verified on disk)

Per the standing rule to evaluate adjacent components (not just map them), to seed the next problems:

| component | brain-fidelity | limitation (measured/on-disk) | opportunity |
|---|---|---|---|
| **sense-assignment** (`canonicalize`, the 0.45 gate) | ATL nearest-neighbour in a semantic hub -- reasonable at the computational level | **single-prototype**: one bundle per lemma, cannot express multiple senses; precision capped ~0.25-0.35 by anchor-pool coverage | multi-prototype per-sense anchors (my sense-split); this is the largest-slice fix if the representation improves |
| **anchor-pool expansion** (`process_sentence(anchor_pool=...)` + `exp_anchor_pool_expansion_v1`) | grounded words bootstrap later grounding (developmental vocabulary growth) | **EXISTS but DEFAULT-OFF**; cell verdict `COMPARATOR_IS_BINDING` = anchor-pool SIZE is the binding variable | wire grounded words in as anchors -> directly shrinks the 29% no-anchor slice; a built, un-wired lever |
| **`ultrametric_clustering`** (WIRED) | hierarchical clustering primitive | not used for sense induction | reuse as the substrate for multi-prototype sense-clustering (don't reinvent) |
| **single-hypothesis Library / PBV** | brain represents multiple senses; one carried hypothesis is a simplification | OUR-INVENTION single-sense store | multi-sense Library items (the store-level version of sense-splitting) |
| **context representation / encoder** (bag-of-words d=256; also tested PPMI, PPMI+SVD, syntactic parse) | distributional co-occurrence -- captures TOPIC (syntagmatic), not SENSE (paradigmatic) | REFUTED as the lever head-to-head: every encoder incl. the full parser retrieves the correct anchor to top-10 ~85%, none selects it (~0.21-0.24) | NOT the lever. The missing signal is grounded/sensorimotor (ATL), absent from distributional context |
| **the SELECTION read-out** (the actual wall) | picking the correct sense from topically-close candidates | no read-out selects above ~0.24 vs top-10 ceiling ~0.87 (nearest/bg-subtract/distilled/supervised all fail) | a GROUNDED meaning signal (`reader_meaning_channel`/ATL = Phase 1); distributional re-ranking is a dead end here |

Prior sense work exists but is SHELVED (`exp_sense_collapse_floor_v1`, `exp_sense_structured_hub_ca_v1/v2`, under the
superseded vwfa/ppmi encoder cluster), so multi-prototype grounding is genuinely un-built on the live path.

## What I did NOT establish / what I would withdraw first

- I did **not** test retrieval practice on a corpus rich enough to give the tiny (0.6-2%) coherent-single-sense-with-anchor
  slice statistical power. On that slice retrieval practice *might* add a small, real benefit -- but it is 1-2% of the
  wall, so it cannot be the fix for the 59%. **First thing I'd withdraw if wrong:** the strong-form claim that retrieval
  adds *nothing*; the defensible claim is that it does not move the *population* precision and is at chance for selection.
- The WordNet blind metric is a proxy for "correct meaning" (~35% ceiling even on incumbent groundings). A different
  correctness oracle could shift absolute precision, but the *relative* result (all schemes flat; retrieval at chance for
  selection; phi == bow) is oracle-independent and reproduces across seeds.
- The PPMI+SVD probe was built from the same 3000-sentence read (thin for SVD). At larger scale phi could improve in
  absolute terms, but it is *equal* to bag-of-words here, so it is not the lever *for these words* at this scale.

## KEY REALIZATIONS (the enabling moves)

- **RETRIEVABLE != SELECTABLE -- the oracle+encoder decomposition split the wall in two.** Asking "does a correct anchor
  even EXIST?" (oracle: yes for ~78%) and then "where does the encoder rank it?" (median ~3, top-10 ~85% under *every*
  encoder) proved the meaning is retrievable and the encoder is not the wall -- which REFUTED the tempting "build a better
  encoder / p2 parser" follow-on head-to-head, and relocated the wall to SELECTION among the retrieved candidates.
- **Syntagmatic vs paradigmatic is THE frame.** The nearest distributional neighbour is a topical co-occurrence associate
  (whisky->wedding), not the substitutable same-meaning anchor (whisky->brandy). Naming this predicted exactly which
  read-outs might fix it (paradigmatic re-rankers) and, when nearest/bg-subtract/distilled/**supervised** all failed
  (~0.21-0.24 vs 0.87 ceiling), proved the selecting signal is absent from distributional co-occurrence -> grounded input.
- **Escalate the read-out ladder to a SUPERVISED probe before concluding "absent."** Unsupervised failing is weak
  evidence; a cross-validated logistic on the features failing (lift +0.008, coefs ~0) is strong evidence the signal is
  genuinely not in the representation -- not merely unextracted by a hand-rule.
- **Match the ESTABLISHED correctness criterion exactly (caught twice).** Two probes dropped Wu-Palmer from the WordNet
  relatedness check "for speed" and produced collapsed, invalid numbers (top-10 0.13 vs the valid 0.85). Any comparison
  must use the SAME `_wn_related` criterion (shared-synset/subsumption OR wup>=0.5); scope the wup cost to the top-K
  candidates rather than dropping it.
- **The rate-independent selection-AUC is what defeats the unmatched-twin trap.** Absolute "grounded-correct count"
  rewards any scheme that grounds more words at the base precision, so a rate-*unmatched* random twin can "win." Holding
  the meaning representation fixed and asking whether the mechanism's confidence *ranks* correct groundings above chance
  (AUC vs a random selector) is the honest test, and it is the one that exposed the negative.
- **Characterize the failure population before believing the brief's label.** "CONSOLIDATION_FAIL" sounds like a
  durability problem; on disk it is 92% polysemy / no-anchor / incoherent / proper-noun. The brief's word "coherent" was
  the load-bearing error; one WordNet+split-half breakdown refuted the premise.
- **Separate the consolidation gate from the sense-assignment gate.** Grounding rides on TWO gates (split-half coherence,
  then canonicalize@0.45). Keeping the second fixed while varying the first proved the precision ceiling lives in the
  *representation/sense-assignment*, not the consolidation encoding.
- **Copy the published equation, don't invent one.** Mozer Eq.7 `Delta s = eps*(1-s)` gave a principled retrieval-gated
  accumulator (and the `(1-s)` = New Theory of Disuse for free); the negative is therefore about the substrate, not about
  a hand-rolled rule.
- **Push through the wall with the brain's mechanism, and let the multi-seed run overrule the smoke.** Rather than stop at
  "representation-bound," I built the brain's actual mechanism for the largest slice (multi-prototype sense-splitting). At
  smoke it looked like a clean positive; at full 2-seed scale it was small and seed-unstable, and the coherence readout was
  confounded by cluster size. Believing the 2-seed result over the smoke turned a tempting false win into a firmer verdict:
  the constraint is the *representation*, at every level, not the consolidation operation.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b)

The 2026-08-31 `information_foraging` + `definitional_extraction` component scans **converged on "consolidation" as the
bottleneck and proposed retrieval-practice-not-reread (Karpicke) as the next clean-foundation fix** (audit §2b, the entry
that spawned this brief). **CORRECTION, measured:** the bottleneck under the `CONSOLIDATION_FAIL` label is **not** the
consolidation *encoding scheme* and retrieval practice does **not** fix it. On the actual population (n=716/685, 3000
modern sentences) retrieval practice built to Mozer 2009 Eq.7 (+ a PBV meaning-retrieval variant) selects a correct
grounding at **chance** (AUC 0.486/0.503, CI includes 0.5), grounding precision is **flat at the ~0.30 base rate** across
retrieval-gated / exposure-count / info-free schemes, and a **PPMI+SVD representation does not beat bag-of-words**
(0.302 vs 0.303). The wall is **representation/structure-bound**: 41-44% polysemous (sense-splitting), 25-29% no eligible
anchor (ATL coverage), 18-24% genuinely incoherent contexts, 6-11% proper-noun/no-target; only 0.6-2% coherent-single-
sense-with-anchor. For the `reading_grounding_loop`/B3 entry: the grounding-precision ceiling (~0.25-0.35) is set by the
sense-assignment (canonicalize) representation and is invariant to the consolidation scheme -- consolidation is not the
lever for durable *correct* grounding on this population. "Make growth stick" via retrieval practice is refuted as the
clean-foundation lever; the lever is the meaning representation + sense disambiguation. **FURTHER (the constructive push):**
the brain's actual mechanism for the largest slice -- multi-prototype **sense-splitting** (Rodd 2004; Neelakantan 2014
online DP-means) -- was built and tested and it too does NOT robustly ground the polysemous words in the current
representation (recovery 0.4-4%, seed-unstable). **DECISIVE LOCALISATION (owner-drilled "nail all"): the constraint is
representation-bound at the SELECTION level, and it is NOT the encoder.** Oracle: a correct anchor EXISTS for ~78% of
words. Head-to-head, EVERY encoder -- hashed bag, separable-raw, PPMI, PPMI+SVD, AND the full syntactic/dependency-parse
encoder -- retrieves the correct anchor to median rank ~3 / top-10 ~85% (so a better encoder, incl. the p2 parser, is
REFUTED as the lever), but NO read-out selects it: nearest 0.21, background-subtraction 0.23, the landed distilled
substitutability axis 0.24, a supervised CV logistic 0.22 (lift +0.008, coefs ~0) -- vs top-10 ceiling ~0.87. The
signal separating the correct SENSE from the topical ASSOCIATE is absent from distributional co-occurrence; the lever is
a GROUNDED/sensorimotor meaning signal (`reader_meaning_channel`/ATL = Phase 1). For the `reading_grounding_loop`/B3
entry: the grounding-precision ceiling is set by the SELECTION representation and is invariant to the consolidation
scheme AND to the encoder. Adjacent: anchor-pool expansion is BUILT default-OFF (`exp_anchor_pool_expansion_v1`,
`COMPARATOR_IS_BINDING`); `ultrametric_clustering` (WIRED) can substrate multi-sense clustering; prior sense work
(`exp_sense_collapse_floor`, `exp_sense_structured_hub_ca`) SHELVED.

## FOLLOW-ON PROBLEMS THIS SURFACES (candidate briefs; adjacent-component evaluation)

1. **THE lever -- a GROUNDED sense-selection read-out (`reader_meaning_channel`/ATL = Phase 1), DEMONSTRATED.** The drill
   proved the correct meaning is retrievable (top-10 ~85%) but not selectable by ANY distributional read-out (all
   0.21-0.24), AND that a GROUNDED-hub re-rank (Lancaster sensorimotor + Warriner affect) DOES select it (+0.08/+0.07 lift
   over distributional, both seeds, ~78% coverage). Concrete wire (see "THE DEMONSTRATED FIX" above): select over the
   retrieved distributional top-K with `build_grounded_hub` similarity, not distributional cosine. Highest leverage; the
   project's named Phase-1 bottleneck. NOT a better encoder (refuted head-to-head), NOT a distributional re-ranker
   (refuted incl. supervised). Next: richer grounding (Binder 65-dim / learned grounded selector) + coverage for the ~22%
   uncovered abstract words to close the residual toward the ~0.87 ceiling.
2. **Anchor-pool / ATL coverage (~8% genuinely coverage-bound; ~25-29% no-anchor before dedup) -- a BUILT, un-wired lever.**
   Words whose meaning is absent from the known vocabulary. The mechanism exists default-OFF
   (`process_sentence(anchor_pool=...)` + `exp_anchor_pool_expansion_v1`, verdict `COMPARATOR_IS_BINDING` = anchor-pool
   SIZE is the binding variable). Opportunity: wire grounded words in as anchors so grounding bootstraps its own coverage.
3. **Multi-prototype sense-splitting (41-44% polysemous) -- a consolidation-side refinement that only pays off ONCE the
   grounded selection signal (#1) exists.** The operation is brain-faithful (built + tested) but recovers only 0.4-4%
   (seed-unstable) here, because splitting senses does not help if you still cannot SELECT the right sense's anchor.
   Sequence it AFTER #1. Reuse `ultrametric_clustering` (WIRED) as the clustering substrate.
4. **Entity grounding for proper nouns (6-11%).** No common-word meaning; route them to an episodic/entity store (cf. the
   belief/ToM entity work), not the distributional grounding channel -- out of the grounding target set, not a failure.

## PROPOSED hdlab CHANGE (Q111 -- strategy lands; here it is a proposed NON-change + a routing fix)

**Do NOT land a retrieval-practice consolidation step as a grounding fix.** It does not raise durable-*correct* grounding
and its only effect is to relax the grounding threshold, which the brief forbids (adds wrong meanings at the base rate).
Concretely: leave `hdlab/grounding_acquisition_loop.py::consolidation_pass` and `hdlab/reading_grounding_loop.py`
unchanged with respect to a retrieval-gated durability rule.

Also do NOT land a distributional read-out re-ranker (nearest/background-subtraction/distilled/supervised all refuted) or
a "better encoder" swap (every encoder incl. the parser retrieves to top-10 ~85% but none selects) as a grounding fix.
The actionable landings this result *does* motivate (for the strategy session to schedule as follow-on briefs above):
(a) the highest-leverage lever is a GROUNDED/sensorimotor SENSE-SELECTION signal -- the `reader_meaning_channel`/ATL /
Phase-1 problem (the drill proves distributional context cannot supply it); (b) wire the BUILT default-off anchor-pool
expansion to shrink the coverage-bound slice; (c) route proper-noun / no-WordNet-target lemmas *out* of the grounding
target set. None is written to `hdlab/` here (solver scope; Q111).

---

## TLDR (plain language)

We thought words a reader meets many times but never learns fail because the "make it stick" step just averages the
meetings together, and that quizzing-style practice (recall the meaning each time you meet the word) would fix it. I built
that quizzing mechanism exactly as the brain-science describes it and tested it fairly. **It does not help.** The reason
is that those words are not "seen clearly many times but not remembered" -- most of them are words with several different
meanings, or words whose meaning the reader has no word for yet, or names of people/places. Quizzing makes a memory
*stronger*; it cannot decide *which* of several meanings is right, or supply a meaning the reader doesn't have. So the real
problem is how word meaning is *told apart*, not how hard the memory is drilled. We then drilled to the very bottom: for
the words where the right meaning IS in the reader's vocabulary, the right answer is almost always *among the top handful*
of the reader's guesses (~85% of the time in the top 10) -- but the reader picks the wrong one, because from plain reading
it can only tell that two words *go together* (whisky and weddings) not that they *mean the same kind of thing* (whisky and
brandy). We tried everything to fix the picking: removing common-topic bias, a smarter grammar-aware reader, the best
meaning-similarity tool we have, and even a small model *trained* to pick -- none helped. The missing ingredient isn't in
reading text at all; it's *grounded* knowledge of what things are (what the project calls the sensorimotor->meaning-hub
pathway, Phase 1). So this is a clean, useful "no" that points precisely at the one lever left: give the reader grounded
meaning, not more reading tricks.

## QUESTIONS

None. (The brief pre-authorized a located representation-bound negative as a full PASS, and I located it with the
evidence it asked for.)

## NEXT STEPS

- Strategy: fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b -- retrieval practice refuted; sense-splitting not
  robust; and the DECISIVE localisation: the wall is representation-bound **at the SELECTION level** (correct meaning
  retrievable to top-10 ~85% under every encoder incl. the parser, but selectable by no read-out incl. supervised) -> the
  lever is grounded/sensorimotor sense-selection = Phase 1 / `reader_meaning_channel`/ATL. **Retire the earlier
  "context-encoder / p2-parser is the deepest lever" line -- refuted head-to-head.**
- Strategy: the highest-leverage follow-on is a **grounded sense-SELECTION signal** (Phase-1 ATL), NOT a better encoder and
  NOT a distributional read-out (both refuted). Then the BUILT-but-un-wired **anchor-pool expansion** (~8% coverage slice);
  sense-splitting is a later consolidation-side refinement that only pays off once selection works.
- Do NOT land: a retrieval-practice consolidation step; a distributional read-out re-ranker; or a "better encoder" swap --
  all refuted here (proposed non-changes).
- Reverify: `.venv/Scripts/python.exe verification/test_retrieval_practice_consolidation.py` (extended with the read-out /
  encoder-not-the-wall checks).
