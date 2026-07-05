# Mechanism + envelope-push: inductive relational transfer just moved off zero

**Filed:** 2026-07-05 by research (Opus synthesis + 3 parallel Sonnet lit-scans: KG-embedding
bilinear-vs-translation, TEM/cognitive-map neuroscience, few-shot-prototype/info-theoretic
ceilings).
**Trigger:** `exp_schema_relation_TEM_structural_content_binding_v1` (commit `d814a43bc`), smoke
`data/exp_schema_relation_TEM_structural_content_binding_v1_smoke/metrics.json`, verdict
MIDDLE_BAND, FULL queued. Verified off-disk (metrics.json read directly; `.py` mechanism code
read directly; ConceptNet corpus counted directly — see below).
**Basis:** prereg `preregs/2026-07-05_schema_relation_TEM_structural_content_binding_v1.md`;
prior frontier drill `notes/research_frontier_drill_inductive_relational_transfer_unseen_entities_2026-07-05.md`.

## HEADLINE

The mechanism difference is exactly the one the KG-embedding literature already named 15 years
ago: **GLOBAL is a TransE-style single additive relation vector** (`M_R = mean_i[O_i * conj(A_i)]`,
one transform, same for every subject) which the literature proves *must* degenerate to the
population-marginal object on one-to-many relations (TransE forces all valid tails into one
point in embedding space — TransH/RESCAL papers, Wang et al. 2014; Nickel et al. 2011).
**TEM and SCORER both instead condition on subject content before/while scoring** — TEM via hard
K-means-style clustering into type-conditional sub-marginals (a discretized, low-rank
approximation of a full relation matrix), SCORER via a genuine bilinear form (the RESCAL/DistMult/
ComplEx move, O(d^2) capacity vs TransE's O(d), with formal full-expressiveness proofs —
Trouillon 2016, Kazemi & Poole 2018). Shuffling breaks the *pairing* but not the *marginal*, so
GLOBAL(real)≈GLOBAL(shuffled); type-conditioning creates K distinct sub-marginals that shuffling
pulls back toward the single global marginal — that gap is exactly the ~0.05–0.13 signal observed.
This is a genuine emergence, not noise: it is the population-average → subpopulation-average
step, one level of resolution finer, well-precedented in the field (TransH vs TransE gives
+15–20 Hits@10 points on 1-to-N/N-to-1 FB15k subsets — same qualitative jump, comparable order of
magnitude once Hits@1-vs-Hits@10 strictness is accounted for).

**Why modest, verified off-disk (not lit-scan speculation):** I counted the actual ConceptNet
corpus (`data/datasets/conceptnet5_en_100k.jsonl`) restricted to each relation's top-V=100
codebook objects — the load-bearing number the cell's own `V_CODEBOOK` fixes for both smoke AND
full (V, M_OP=200, K∈{5,10,20} do NOT scale up between smoke and full; only seeds/test-size/
scorer-steps do). Result: **AtLocation** 27,797 triples / 7,769 distinct objects, top-100 covers
9,366 (34%); **CausesDesire** 4,688 triples / 598 distinct objects, top-100 covers 1,423 (30%);
**CapableOf** 22,677 triples / **18,541 distinct objects** (near one-to-one!), top-100 covers only
**949 (4.2%)**. CapableOf is structurally data-starved at this V — its usable in-codebook pool is
tiny regardless of mechanism, capping M_OP scale-up near ~700-800 max. AtLocation/CausesDesire
have real headroom (only 200 of 9,366 / 1,423 available in-codebook triples are currently used as
train pairs). So "why modest" splits genuinely: partly under-parameterization with real
recoverable headroom (AtLocation, CausesDesire — M_OP=200 is a tiny fraction of available data),
partly a hard data-availability ceiling specific to CapableOf, and partly a true one-to-many
entropy ceiling that the field never fully escapes even at scale (FB15k 1-to-N Hits@10 caps at
39.8% (TransH) to ~57-84% (bilinear family) — never near saturation for any model tried; direct,
solid precedent, Wang et al. 2014 / Trouillon et al. 2016).

**Why SCORER matches/beats TEM:** not a "brain-alignment fails" result. The as-built TEM arm is a
hard, non-differentiable K-means discretization — no recurrence, no path integration, no
attractor dynamics, none of the machinery that makes the actual Tolman-Eichenbaum Machine
(Whittington et al. 2020, *Cell*) work. The lit-scan found **zero ablation evidence anywhere in
the TEM literature** isolating recurrence's contribution (STAR Methods assumes noise-free
deterministic transitions; TEM-t, ICLR 2022, reformulates the recurrence as attention but never
removes it) — so there is no published precedent either confirming or refuting that "proper" TEM
would beat a bilinear scorer. What we tested is "hard discrete clustering vs. continuous
gradient-optimized bilinear factorization" — capacity theory (RESCAL/ComplEx full-expressiveness
proofs) predicts the continuous form wins, unsurprising. Per
`feedback_mechanism_analog_is_not_task_analog`, this is our under-realized approximation losing
to a better-optimized analog of the *same principle* — not evidence against the brain-grounded
hypothesis itself, which was never actually implemented (the K-means step is closer to
Prototypical Networks, Snell et al. 2017, than to real TEM).

## Cheap decisive test (single next cell, CPU-only, no GPU needed)

`schema_relation_TEM_scorer_scaleup_v1`: same paired REAL/SHUFFLED/discriminator design, sweep
**M_OP ∈ {200, 500, 800}** for AtLocation/CausesDesire only (CapableOf capped near 500 given the
949-triple in-codebook ceiling — flag it separately, don't lump into the same sweep axis),
**SCORER_STEPS ∈ {150, 300, 600}** and **SCORER_DF ∈ {96, 192}** (cheap, numpy CPU, current wall
~29s/seed leaves huge headroom), plus a **SOFT-TEM variant**: replace hard-argmax prototype
classification with a posterior-weighted (softmax-similarity) mixture over the nearest 2-3
prototypes at both train and test — the cheapest available brain-aligned upgrade that
specifically targets the "under-realized, no continuity" critique without building a full
recurrent/attractor system (which the lit-scan flags as high-cost/uncertain-payoff — zero
ablation precedent either way).

**HARD-PASS:** scaled config yields `real_minus_shuf(inductive) >= 0.2075` on >=1 semantic
relation for either family, discriminator firing -> useful-magnitude transfer reachable by scale
alone; predicts further scale-up is worthwhile.
**HARD-FAIL:** scaled config (M_OP 4x, steps 4x) improves `real_minus_shuf` by `< 0.03` absolute
on ALL semantic relations x both families, discriminators still firing -> genuine entropy/data
ceiling; scale will not rescue it; the fix (if any) is richer content (structured attributes,
multi-sentence descriptions — the DKRL->KEPLER->BLP->SimKGC trend, BLP: 0.180->0.285 MRR,
+58% relative, from richer jointly-trained content, not more of the same short-text signal), not
more compute on the same content.
**MIDDLE_BAND:** partial gain (0.03-0.10 absolute improvement, still under 0.2075) -> mechanism
directionally right, iterate content richness next, not mechanism pivot.

## Falsifiable predictions (calibration-penalized, novel-synthesis capped at 0.50)

- P(scaled M_OP/steps config clears HARD-PASS on >=1 relation) = 0.18 (naive ~0.38, deflated
  -0.20; real headroom exists per corpus counts, but field precedent shows one-to-many relations
  rarely reach this magnitude even at far larger scale).
- P(HARD-FAIL / genuine ceiling on all relations) = 0.30 (naive ~0.45, deflated -0.15; Fano's-
  inequality-style entropy argument for one-to-many targets is solid generic theory; CapableOf's
  4.2% codebook coverage is independently damning regardless of mechanism).
- P(MIDDLE_BAND, most likely honest outcome) = 0.52.
- P(SOFT-TEM upgrade closes >=half the TEM-SCORER smoke gap) = 0.30 (genuinely unknown; zero
  direct precedent either way per lit-scan, held near naive estimate rather than deflated further
  since there is no misleading naive prior to correct).

**P_deflated (headline mechanism diagnosis: content-conditioning-vs-averaging is the correct
explanation, magnitude is a mix of recoverable under-parameterization + a real one-to-many/data
ceiling, SCORER's edge over TEM reflects a discretization gap not a brain-alignment failure) =
0.42** (capped below 0.50; deflated from KG-embedding lit precedent being strong/direct while TEM
recurrence-ablation precedent is genuinely absent, not merely uncited).

## Cross-thread synthesis

- Confirms and sharpens the prior frontier-drill's operator-class diagnosis
  (`notes/research_frontier_drill_inductive_relational_transfer_unseen_entities_2026-07-05.md`):
  that note predicted the averaged-transform family is shuffle-invariant by construction; this
  finding is the first cell to show the FIX (type/content conditioning) actually produces
  nonzero, non-vacuous signal, closing the open question with a real (not synthetic-control-only)
  positive result.
- BLP (Daza et al. 2021) remains the single cleanest converging citation across both this note and
  the prior drill: richer, jointly-trained entity-content representations reliably beat frozen/
  thin content, independent of relation-operator sophistication — directly predicts that content
  enrichment, not just mechanism or scale, is the other lever worth pulling.
- New quantitative literature surfaced this round not in the prior drill: TransH/RESCAL/ComplEx/
  SimplE capacity and full-expressiveness results (Nickel 2011, Trouillon 2016, Kazemi & Poole
  2018) — a concrete mathematical grounding for "bilinear beats translation on one-to-many," and
  an entropy-ceiling paper for multi-modal target distributions (arXiv 2603.27952, unverified/
  low-citation preprint — flagged, not load-bearing alone, but consistent with the older Fano's-
  inequality textbook result which IS load-bearing).
- Adjacency-cascade candidate (per Trigger C): **knowledge-graph-relational-embedding capacity
  theory** (RESCAL/ComplEx/SimplE expressiveness bounds) is a genuinely new, quantitatively rich
  field this drill surfaced, adjacent to the existing free-probability/random-matrix tier-1
  fields (rank/expressiveness bounds are a shared mathematical language) and to
  network-science-graph-theory (node-degree skew explains the CapableOf coverage collapse).
  Recommend as next-drill candidate.

## Substrate-product implications

This is the first non-vacuous evidence that the substrate CAN turn stored facts into transferable
relational knowledge about entities it has never seen — a real, if modest, capability, not a
rediscovery of the exhausted-zero result. Honest product framing: usable today for relations with
either (a) real training-pair headroom AND coarse-type-predictable objects (AtLocation-like), not
yet for (b) near-one-to-one/long-tail relations (CapableOf-like) at small V, and not yet at
magnitude sufficient to replace curated relation lookups. The decisive next spend (cheap, CPU,
days not weeks) tells us whether this is an engineering ramp (more data + richer content closes
most of the gap, per the BLP/SimKGC field trend) or a load-bearing ceiling specific to thin
generic-sentence content on noisy crowd-sourced relations (CapableOf's 4.2% coverage already
suggests part of the answer is the latter, regardless of mechanism choice).

## Citations (verified count: 9, distinct, new this round; see prior drill note for the other 15)

KG-embedding capacity/expressiveness (5): Wang, Zhang, Feng & Chen, AAAI 2014 (TransH, per-category
Hits@10 table); Nickel, Tresp & Kriegel, ICML 2011 (RESCAL); Trouillon, Welbl, Riedel, Gaussier &
Bouchard, ICML/JMLR 2016 (ComplEx, full-expressiveness at d=n_e·n_r); Kazemi & Poole, NeurIPS 2018
(SimplE, tighter expressiveness bound); Teru, Denis & Hamilton, ICML 2020 (GraIL, inductive
subgraph-based, loose analog only) / Shah et al. 2019 (OWE, content-based induction, closer
analog, mixed results).

TEM/cognitive-map (2): Whittington, Muller, Mark, Chen, Barry, Burgess & Behrens, *Cell* 2020
(TEM, STAR Methods confirms deterministic noise-free transitions, no recurrence ablation);
Whittington, Warren & Behrens, ICLR 2022 (TEM-t, recurrence reframed as attention, not removed).
Snell, Swersky & Zemel, NeurIPS 2017 (Prototypical Networks — the actual closest precedent for
the as-built TEM arm's hard-clustering mechanism).

Information-theoretic ceiling (2): Cover & Thomas (Fano's inequality, textbook, load-bearing);
arXiv:2603.27952 (entropy-bound on sequential-recommender top-1 accuracy — recent/low-citation,
flagged as suggestive not canonical, consistent with but not independently verified beyond Fano).

George et al., *Nat Commun* 2021 (Clone-Structured Cognitive Graphs — explicit contrast case for
one-to-many/aliased transition handling that TEM does not natively address) counted as
context, not separately in the 9.
