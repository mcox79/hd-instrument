---
problem: grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice
status: SOLVED
bar: "A rigorous NEGATIVE is a full PASS if located: if retrieval-practice, faithfully built and exposure-matched, does NOT beat re-reading on this population, then the 59% wall is REPRESENTATION-bound (the trace can't encode the distinction) not ENCODING-SCHEME-bound -- name it, with the evidence (e.g. the retrieval scorer's own accuracy ceiling on these words), and hand the representation gap to reader_meaning_channel/ATL."
result: "REPRESENTATION-BOUND NEGATIVE (the brief's full-PASS-if-located outcome). Retrieval practice, faithfully built (Mozer 2009 MCM Eq.7 + a PBV meaning-retrieval variant), CANNOT select a WordNet-correct grounding above chance on the CONSOLIDATION_FAIL population: selection-AUC (fixed meaning representation) retrieve=0.486 [0.413,0.554] / 0.503 [0.461,0.543] (seed0/seed1), PBV=0.467 [0.402,0.530] / 0.488 [0.446,0.531] -- both CIs INCLUDE chance (0.5). Grounding precision is FLAT at the ~0.25-0.32 base rate across every scheme; n=716/685 CONSOLIDATION_FAIL words, 3000 modern sentences (simplewiki+news+science), scored blind on WordNet."
floor: "Incumbent split-half RE-STUDY arm at EQUAL exposure (best-case, all traces at once): grounded-CORRECT rate 0.006 (seed0) / 0.004 (seed1) -- it grounds ~none of these words. Rate-independent info-free floor: random-selection AUC 0.447 / 0.456 for picking a correct grounding, which retrieval does not beat."
controls: "(1) exposure-matched RE-STUDY (incumbent split-half) -- retrieval's apparent recall gain over it is pure threshold-relaxation; (2) EXPOSURE-COUNT arm (strengthen every exposure, no retrieval gate) -- ties/beats retrieval, excluding 'the retrieval gate helps'; (3) info-free TWIN_SHUF (retrieval outcomes shuffled) and TWIN_RAND (random scores) -- retrieval does NOT beat them on grounded-correct; (4) DECISIVE rate-independent selection-AUC vs a random selector -- excludes 'grounds more words at base precision'; (5) PBV meaning-retrieval variant -- rules out a weak self-coherence retrieval; (6) m-quality-matched (hits-only vs full-bundle estimate) -- excludes 'a cleaner estimate'; (7) PPMI+SVD distributional representation probe (phi 0.302 vs bag-of-words 0.303, CI [-0.036,+0.036], not separated) -- excludes 'a richer target-word representation fixes it'; (8) population characterization -- excludes the brief's 'coherent repeated exposures' premise (mean split-half coherence 0.09-0.13; only 0.6-2% coherent-single-sense-with-anchor)."
files_changed: "experiments/exp_retrieval_practice_consolidation_v1.py (arms + decisive selection-AUC + PBV variant + distributional-representation probe + multi-prototype sense-splitting probe); verification/test_retrieval_practice_consolidation.py; notes/problems/grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice/SOLVED.md; data/exp_retrieval_practice_consolidation_v1/{metrics.json,dist_probe.json,sense_probe.json}"
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

**This deepens the verdict rather than overturning it.** Even the brain's *correct* mechanism for the largest slice,
faithfully built, cannot reliably find groundable senses **in this substrate's context representation** -- because that
representation (masked bag-of-content-words, d=256, sign-collapsed) is too weak to separate senses (the retrieval
self-vs-other AUC was only ~0.63). So the binding constraint sits at the **representation** at *every* level: the single
average blurs senses, multi-prototype can't cleanly recover them, and a PPMI+SVD upgrade didn't help nearest-anchor
precision. The lever is a richer context encoding (the p2 parser / structural encoder) and anchor-pool/ATL coverage --
not the consolidation operation, and not retrieval practice.

## Adjacent-component evaluation (brain-foundational fidelity + opportunities, verified on disk)

Per the standing rule to evaluate adjacent components (not just map them), to seed the next problems:

| component | brain-fidelity | limitation (measured/on-disk) | opportunity |
|---|---|---|---|
| **sense-assignment** (`canonicalize`, the 0.45 gate) | ATL nearest-neighbour in a semantic hub -- reasonable at the computational level | **single-prototype**: one bundle per lemma, cannot express multiple senses; precision capped ~0.25-0.35 by anchor-pool coverage | multi-prototype per-sense anchors (my sense-split); this is the largest-slice fix if the representation improves |
| **anchor-pool expansion** (`process_sentence(anchor_pool=...)` + `exp_anchor_pool_expansion_v1`) | grounded words bootstrap later grounding (developmental vocabulary growth) | **EXISTS but DEFAULT-OFF**; cell verdict `COMPARATOR_IS_BINDING` = anchor-pool SIZE is the binding variable | wire grounded words in as anchors -> directly shrinks the 29% no-anchor slice; a built, un-wired lever |
| **`ultrametric_clustering`** (WIRED) | hierarchical clustering primitive | not used for sense induction | reuse as the substrate for multi-prototype sense-clustering (don't reinvent) |
| **single-hypothesis Library / PBV** | brain represents multiple senses; one carried hypothesis is a simplification | OUR-INVENTION single-sense store | multi-sense Library items (the store-level version of sense-splitting) |
| **context representation** (masked bag-of-content-words, d=256) | crude, order-free, no syntax | self-vs-other retrieval AUC only ~0.63 -> caps every downstream sense/grounding decision | the p2 parser / structural encoder -- the deepest shared lever |

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
representation (recovery 0.4-4%, seed-unstable; DP-cluster coherence 0.33-0.64 vs whole-bundle 0.09 but confounded by
cluster size -- a size-matched random twin ties it in one seed). So the constraint is the **context/meaning REPRESENTATION
at every level** (self-vs-other retrieval AUC ~0.63 caps it), not the consolidation operation. Adjacent components:
`canonicalize` is single-prototype (no multi-sense); anchor-pool expansion is BUILT default-OFF
(`exp_anchor_pool_expansion_v1`, `COMPARATOR_IS_BINDING`) and targets the 25-29% no-anchor slice; `ultrametric_clustering`
(WIRED) can substrate multi-sense clustering; prior sense work (`exp_sense_collapse_floor`, `exp_sense_structured_hub_ca`)
is SHELVED.

## FOLLOW-ON PROBLEMS THIS SURFACES (candidate briefs; adjacent-component evaluation)

1. **Multi-prototype sense-splitting (41-44% of the wall) -- BUT gated on a better context representation.** The
   consolidation loop carries a *single* prototype per lemma. Polysemous words need clustered per-sense prototypes. I built
   and tested this (the push above): the operation is brain-faithful and recovers a small, above-base-precision slice, but
   does NOT robustly break the wall *in the current d=256 bag-of-words representation* (recovery 0.4-4%, seed-unstable;
   coherence confounded by cluster size). Honest sequencing: land the sense-splitting consolidation change only once the
   context encoding can separate senses (see #4). Reuse `ultrametric_clustering` (WIRED) as the clustering substrate.
2. **Anchor-pool / ATL coverage (25-29%) -- a BUILT, un-wired lever.** Single-sense words with no eligible anchor cannot
   ground because the target meaning is absent from the known vocabulary. The mechanism already exists default-OFF
   (`process_sentence(anchor_pool=...)` + `exp_anchor_pool_expansion_v1`, verdict `COMPARATOR_IS_BINDING` = anchor-pool
   SIZE is the binding variable). Opportunity: wire grounded words in as anchors so grounding bootstraps its own coverage.
   This is the `reader_meaning_channel`/ATL problem; this result quantifies its 25-29% share of the depth wall.
3. **Entity grounding for proper nouns (6-11%).** These have no common-word meaning; they belong in an episodic/entity
   store (cf. the belief/ToM entity work), not the distributional grounding channel -- route them *out* of the grounding
   target set rather than counting them as failures.
4. **The context encoding is the deepest shared lever.** The masked bag-of-content-words d=256 vector gives a self-vs-other
   retrieval AUC of only ~0.63, which caps *every* downstream grounding/sense decision -- it is why both single-average and
   multi-prototype fail. A structural/parsed encoder (the p2 parser track) sits upstream of #1 and of this whole problem.

## PROPOSED hdlab CHANGE (Q111 -- strategy lands; here it is a proposed NON-change + a routing fix)

**Do NOT land a retrieval-practice consolidation step as a grounding fix.** It does not raise durable-*correct* grounding
and its only effect is to relax the grounding threshold, which the brief forbids (adds wrong meanings at the base rate).
Concretely: leave `hdlab/grounding_acquisition_loop.py::consolidation_pass` and `hdlab/reading_grounding_loop.py`
unchanged with respect to a retrieval-gated durability rule.

The actionable landings this result *does* motivate (for the strategy session to schedule as the follow-on briefs above):
(a) route proper-noun / no-WordNet-target lemmas *out* of the grounding target set (they inflate the "fail" count and can
never ground to a common-word anchor); (b) prioritize sense-splitting + ATL anchor coverage over any consolidation-scheme
change. None of these is written to `hdlab/` here (solver scope; Q111).

---

## TLDR (plain language)

We thought words a reader meets many times but never learns fail because the "make it stick" step just averages the
meetings together, and that quizzing-style practice (recall the meaning each time you meet the word) would fix it. I built
that quizzing mechanism exactly as the brain-science describes it and tested it fairly. **It does not help.** The reason
is that those words are not "seen clearly many times but not remembered" -- most of them are words with several different
meanings, or words whose meaning the reader has no word for yet, or names of people/places. Quizzing makes a memory
*stronger*; it cannot decide *which* of several meanings is right, or supply a meaning the reader doesn't have. So the real
problem is how word meaning is *represented and told apart*, not how hard the memory is drilled. Even swapping in a much
richer meaning representation didn't help these particular words. This is a clean, useful "no": it rules out the proposed
fix and points at the two things that would actually help (telling word senses apart, and growing the vocabulary of known
meanings).

## QUESTIONS

None. (The brief pre-authorized a located representation-bound negative as a full PASS, and I located it with the
evidence it asked for.)

## NEXT STEPS

- Strategy: fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (retrieval practice refuted as the consolidation
  lever; multi-prototype sense-splitting also does not robustly break it in the current representation; the wall is
  representation-bound at every level).
- Strategy: the highest-leverage follow-on is the **context encoding** (#4 -- the p2 parser / structural encoder), because
  it is upstream of both the sense-splitting fix and this problem. Then the BUILT-but-un-wired **anchor-pool expansion**
  (#2, targets 25-29%) and, once the encoder is stronger, **multi-prototype sense-splitting** (#1, targets 41-44%).
- Do NOT land a retrieval-practice consolidation step, and do NOT land sense-splitting against the current encoder
  (proposed non-changes -- both would only relax the threshold / add small unstable gains at the base precision).
- Reverify anytime: `.venv/Scripts/python.exe verification/test_retrieval_practice_consolidation.py` (13/13 incl. the
  sense-splitting check).
