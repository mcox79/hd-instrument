# Research: is "grounded disambiguate-then-bind to build a sense-discriminative W" brain-foundational?
**Date:** 2026-09-04 | **Drilled by:** research (Opus synthesis + 3 parallel Sonnet lit-scans)

## HEADLINE
Two of the mechanism's three components are PINNED and were ALREADY BUILT AND TESTED on disk (order:
disambiguate-then-bind; consolidation: CLS Hebbian recurrence-filter) — neither was the bottleneck. The
third component (GROUNDING as the encoding-time sense-resolver) is the one genuinely new piece, and its
closest already-built analog — the richer Binder-65 grounded ATL hub-and-spoke, `build_the_atl_hub_and_
spoke_meaning_channel_online_predictive_reader/SOLVED.md` — already landed a CI-separated LOCATED
NEGATIVE below the topical-W floor (concat-hub 0.283 < launch-pad 0.313) when used analogously. Fresh
lit-scan confirms grounding-first bootstrapping is real ONLY for concrete-referent disambiguation
(Yu & Smith 2007; Trueswell 2013) and is untested-to-structurally-blocked for the abstract/regular
polysemy that dominates SemCor subordinate senses (Copestake-Briscoe 1995: taxonomic inheritance
under-differentiates regular-polysemy pairs BY CONSTRUCTION, because they share the same taxonomic/
qualia structure). **Verdict: will very likely land as another located negative on the FULL population
(est. a_s 0.22-0.27), not cross 0.35 — unless restricted to a concrete-homonym stratum, where a real but
narrow win is plausible.**

---

## Q1 — Disambiguate-at-encoding, then bind
**PINNED (behavioral):** Tulving & Thomson 1973 encoding specificity ("specific encoding operations...
determine what is stored, and what is stored determines what retrieval cues are effective") + the
homograph demonstration Light & Carter-Sobell 1970 (*JVLVB* 9:1-11) — recognition of a homograph studied
under one meaning collapses when the test context biases the other meaning of the SAME word-form. The
encoded MEANING, not the surface form, is what's stored and matched.
**PINNED (neural, access side):** Controlled semantic cognition (Lambon-Ralph/Jefferies/Rogers/Patterson
2017, *NRN*; Jefferies 2013) — LIFG/pMTG causally resolve context-appropriate sense (TMS: Whitney et al.
2011, *Cereb Cortex*).
**GAP:** no primary source directly bridges "LIFG/pMTG resolves sense" to "hippocampal binding operates
on the resolved rep" — a well-supported SYNTHESIS of two independently-strong pillars, not a single
directly-tested finding.
**Already built + measured:** `exp_consolidation_gate_readbind_v1` implements this exact order. Result:
necessary but not sufficient — imperfect in-context attribution (0.242) ≈ perfect gold attribution
(0.232), both near gloss (0.251). **Quantitative expectation: order alone buys ~0 marginal a_s once
resolver accuracy is held fixed; RESOLVER ACCURACY, not encoding order, is what matters.**

## Q2 — Does grounding break the bootstrap circularity?
**PINNED but narrower than the brief assumes:** Yu & Smith 2007 and Trueswell 2013 resolve REFERENT
ambiguity for concrete object words via cross-situational word↔scene statistics — a different
STATISTICAL channel (word-to-referent vs word-to-word), not obviously "non-distributional" grounding.
Neither paper tests polysemy or abstract senses.
**PINNED (cuts against the premise):** Riordan & Jones 2011 — distributional co-occurrence is largely
REDUNDANT with perceptual features for concept clustering, especially on child-directed speech.
**NOT SUPPORTED / genuine gap:** no source found tests grounding on regular polysemy (institution/
building, container/contents). Sense/polysemy acquisition literature (Srinivasan 2021; Li-Armstrong-Xu
2026 *PNAS*) instead explains sense extension via SEMANTIC CHAINING/relational extension, not perceptual
grounding.
**Disk-confirmed structural failure mode:** regular polysemy is DEFINED by two senses sharing taxonomic/
qualia structure (Copestake-Briscoe 1995; Apresjan 1974; Pustejovsky 1995) — inheritance-based coverage
mechanisms under-differentiate exactly those pairs BY CONSTRUCTION (already PINNED in P9's SOLVED.md).
**Verdict: OUR-INVENTION EXTRAPOLATION when applied to abstract/regular polysemy.** Real for concrete
referent disambiguation; unproven-to-structurally-blocked for the majority-abstract SemCor population.

## Q3 — Hebbian binding to resolved sense + cross-situational consolidation
**PINNED:** McClelland-McNaughton-O'Reilly 1995 (*Psych Rev* 102:419-457) — hippocampus fast/sparse
one-shot; neocortex slow, INTERLEAVED extraction. "Keep what recurs, discard singletons" is an accurate
INFERENCE from interleaved dynamics, not a verbatim claim.
**IMPORTANT CORRECTION from this session's lit-scan:** neocortical consolidation is NOT strictly
single-pass. It requires REPEATED offline REPLAY of each episode (chiefly sleep), each replay producing
a small weight change — functionally closer to multi-pass training over a replay buffer (the literal
inspiration for DQN experience replay, Kumaran-Hassabis-McClelland 2016, *TICS*) than one-shot online
Hebbian update. "Online/one-pass, no batch training" is accurate ONLY for the hippocampal fast-encode
stage — the W-accumulation-over-a-corpus this mechanism proposes is closer to "one fast episodic log +
many interleaved replayed consolidation passes" than "read the corpus once."
**Already built + measured:** readbind + recurrence gate + MFS-quarantine (schema-consistent keep, Tse
2007) faithfully implement this. Result: cleans the raw regression (-0.033 → recovers to ~gloss,
0.238-0.246) but the residual leak is association DISCRIMINATIVENESS (topical, not sense-substitutive),
not the consolidation machinery. `hdlab/cls_growth` (keep-both + rollback + EMA slow-anchor, eta=0.1) —
which already resembles the "many small repeated increments" picture the lit-scan just confirmed — is
proven safe (+0.110/6 rounds). **The consolidation machinery is PINNED, BUILT, and NOT the bottleneck.**

## Q4 — THE KILLER QUESTION
The closest built analog to "grounded-resolved W" is P9's richer grounded ATL hub (Binder-65 + Warriner
VAD, ATL-whitened, WordNet-inheritance-propagated to 54.4% coverage) fed as enriched sense
representations to the wired readout: **grounded-keys-alone a_s = 0.184; concat-hub = 0.283 — BOTH
CI-separated BELOW the topical-W floor (0.313), and grounded-alone is even below the topical-FAILURE
number the prompt cites (0.25).** The grounded signal is real (separates gold-vs-dominant at cos 0.222
vs w2v's 0.799; rescues 80% of distribution-merged pairs) but the loss is QUERY-side (100% per the
parent's oracle decomposition) plus coverage (47.7%), not key separability.
Using grounding as an ENCODING-TIME RESOLVER (rather than as enriched keys) inherits the same two
blockers plus a third: an abstract/regular-polysemy item will either (a) have no grounded coverage and
fall back to the same dominant-sense attractor as distribution-resolved encoding, or (b) get
mis-resolved because taxonomic inheritance blurs exactly the sibling senses that share qualia structure.
**Honest quantitative estimate (calibration-deflated):**
- **FULL population: a_s ≈ 0.22-0.27 — closer to the TOPICAL-FAILURE end (0.25), not the
  gold-discriminative band (0.31+).** Point estimate ~0.24.
- **Concrete-homonym-only stratum (a minority of SemCor subordinate items): plausible CI-separated win**
  over topical-W, because grounded separability is proven strong there and this is exactly the segment
  Riordan & Jones's redundancy caveat does not cover (fine within-form sense discrimination, not
  concept-to-concept clustering).
- **Where it helps:** perceptually/sensorimotor-distinct sense pairs (river-bank/money-bank, animal/
  equipment). **Where it fails:** abstract regular polysemy (institution-for-building,
  process-for-result, container-for-contents) — the majority of the target population, structurally
  blocked by inheritance under-differentiation, not just data-sparsity.

## Q5 — Coverage
SemCor-scale coverage measured at 52% (disk). Literature: Nagy-Herman-Anderson ~6-20 exposures for
reliable word-from-context learning (PINNED, general estimate only); subordinate senses are Zipfian-rare
(Kilgarriff 2004) so need proportionally more total exposures, with subordinate-sense availability
graded/cumulative not all-or-none (Rodd et al.). Taxonomic/category-based inheritance (Collins & Quillian
1969; Osherson 1990) is PINNED as a real generalization mechanism, but NOT the sole one — it operates
alongside similarity-based generalization (Sloman 1993), and (per Q2/Q4) it structurally
under-differentiates exactly the regular-polysemy edges this project needs, because it propagates COARSE
category features, not fine sense-discriminating distinctions. **The mechanism that actually scales,
per the parent's own proof, is more correctly-resolved reading exposure, consolidated (the learned-W
+0.059-on-covered-senses result) — not a taxonomic-inheritance shortcut for the discriminating edge
itself**, though inheritance can still help propagate coarser features affordably.

---

## SINGLE HIGHEST-CONFIDENCE VERDICT
**Will land as another located negative on the full population, not cross 0.35.** Two of three
components (encoding order; CLS consolidation) are PINNED, built, and already shown NOT to be the
bottleneck. The third (grounded resolution) is the one live bet, and its nearest built analog already
failed CI-separated below the topical floor when the exact same asset (Binder-65 grounded ATL) was used
in a closely analogous role. Fresh lit-scan finds no primary support for grounding resolving abstract/
regular polysemy, and a structural reason (Copestake-Briscoe) it should specifically fail there.
**The ONE component still not brain-foundational that blocks it (same one two independent problems on
disk converged on):** the QUERY side — the context representation the resolver matches against — is
still a frozen, non-recomputed, sense-blind bag of static word2vec. 100% of the measured loss sits there
(parent's oracle decomposition), and grounding enriches the KEYS while leaving this untouched. The one
component that IS a proven, brain-faithful, CI-separated fix for this specific piece is precision-
weighted (Friston) selective gain on the query (+0.023 CI-sep, already landed as a wire candidate in
P9) — real but insufficient alone. The true crosser remains a broad-coverage sense-discriminative W
(oracle 0.995, learned +0.059 on covered senses), which grounding at any tested or proposed richness
does not supply for the abstract-dominated majority of the target population.

**P_deflated(crosses a_s≥0.35 CI-sep on full population) = 0.10.** P(located negative, similar shape to
P9, full-population a_s in 0.20-0.28) = 0.65. P(PARTIAL: full-population negative + genuine narrow win
on concrete-homonym stratum, mirroring the shape of the last two related problems) = 0.55-0.65 (not
mutually exclusive with the first).

---

## Cheap decisive test (before building the full pipeline)
Do NOT build the full corpus-scale grounded-resolution + W-accumulation pipeline first — it is expensive
and the closest analog already failed. Instead, RE-SLICE data already on disk:
1. Take `exp_atl_hubspoke_grounded_separability_v1`'s per-item separability decomposition (grounded
   cos(gold,dominant) vs w2v cos(gold,dominant), already computed for all n=2676 items).
2. Split items into CONCRETE-HOMONYM-LIKE (high Binder Vision/Praxis/Sound variance between candidate
   senses, grounded cos < 0.5) vs ABSTRACT/REGULAR-POLYSEME-LIKE (low grounded variance or below the
   47.7% coverage threshold).
3. On the concrete-homonym-like stratum ONLY, score a grounded-nearest-sense ENCODING-TIME resolver
   (does grounding pick the CORRECT sense per-occurrence, not just separate the two key centroids) — a
   resolution-ACCURACY number, not a key-separability number, which P9 never directly measured.
4. This costs a re-aggregation pass over already-computed vectors (no new corpus read, no new GPU/CPU
   run) and directly falsifies/confirms the core claim before committing further compute.

## Falsifiable predictions
- **HARD-PASS:** grounded-resolved W (built full-pipeline) crosses a_s ≥ 0.32 CI-separated over the
  topical-W floor (0.313) on the FULL strict document-disjoint SemCor subordinate population (n≈2676),
  shuffled-grounding-resolution twin loses CI-separated, no MFS regression.
- **HARD-FAIL / located-negative-as-PASS-by-bar (predicted, ~65% mass):** full-population a_s ≤ 0.31
  (CI-separated at or below the topical floor), WITH a genuine CI-separated win confined to the
  concrete-homonym stratum from the cheap decisive test above — a positive, actionable finding inside
  an overall negative, the same shape as the last two related problems (both PARTIAL).
- **MIDDLE-BAND:** full-population a_s in (0.28, 0.32), not CI-separated from the topical floor either
  direction — treat as a null result, not a crossing.

## Cross-thread synthesis with prior entries
This drill sits directly downstream of two owner-integrated SOLVED problems that already built and
tested two of the mechanism's three components:
- `notes/problems/break_the_contextual_input_encoding_ceiling_for_specific_sense_selection/SOLVED.md` —
  proved the ceiling is W quality×coverage (oracle-W → 0.995), not encoder/readout/mechanism-shape; the
  parent's oracle decomposition (100% of loss is the QUERY side) is load-bearing for this note's Q4/verdict.
- `notes/problems/build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner/SOLVED.md` —
  built disambiguate-then-bind + CLS consolidation faithfully (readbind, recurrence, MFS-quarantine);
  ruled out 12/15-dim grounding at every richness (=gloss); redirected to richer Binder-class spokes.
- `notes/problems/build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader/SOLVED.md` (P9) —
  built EXACTLY the richer-grounding follow-on this note verifies; concat-hub 0.283 < launch pad 0.313
  (located negative); precision-weighting +0.023 CI-sep is the only positive found; named the query-side
  + coverage + regular-polysemy-inheritance blockers this note's lit-scan now independently corroborates.
This note's contribution: (1) confirms via primary literature that Q1/Q3 are well-established and were
correctly built, (2) corrects the "online/one-pass" framing for cortical CLS consolidation (repeated
replay, not single-pass), (3) finds NO literature support for grounding resolving abstract/regular
polysemy specifically — closing the one open question P9 could not answer from disk data alone (P9
tested grounding as enriched KEYS; this note's lit-scan explains WHY an encoding-time-RESOLVER framing
would fail the same way, and by the same structural mechanism, Copestake-Briscoe).

## Substrate-product implications
Building the full "grounded disambiguate-then-bind" pipeline as originally proposed would very likely
cost real corpus-scale engineering time for a result that lands at or below where the product already is
(topical-W floor). The cheap decisive test above (near-zero cost, reuses existing data) should run
FIRST. If it confirms the predicted concrete/abstract split, the actionable product move is narrower and
cheaper than the full brief: use grounding as a STRATIFIED bonus (apply it only to the minority of
occurrences where candidate senses are grounded-separable), not as a universal encoding-time resolver —
and prioritize the two already-proven levers instead: precision-weighted query readout (+0.023, ready to
land) and continued growth of the learned sense-discriminative W from correctly-resolved reading
exposure (the proven +0.059-on-covered-senses lever), since inheritance cannot substitute for it on
regular polysemy.

## Citations (verified count)
**20 citations independently checked against primary/secondary sources this session** (3 parallel
Sonnet lit-scans): Tulving & Thomson 1973; Thomson & Tulving 1970; Craik & Lockhart 1972; Light &
Carter-Sobell 1970; Anderson & Ortony 1975; Lambon-Ralph/Jefferies/Rogers/Patterson 2017; Jefferies 2013;
Whitney et al. 2011; Yu & Smith 2007; Trueswell et al. 2013; embodied-bootstrapping reviews (Barsalou-
line, PMC6015819, Frontiers 2021/2022); Riordan & Jones 2011; Srinivasan 2021; Li, Armstrong & Xu 2026
(*PNAS*); McClelland, McNaughton & O'Reilly 1995; Kumaran, Hassabis & McClelland 2016; Nagy, Herman &
Anderson 1985/1987; Kilgarriff 2004; Collins & Quillian 1969; Osherson et al. 1990; Sloman 1993. Plus
**10 disk-pinned citations reused from 2 prior owner-integrated SOLVED problems** (independently verified
in those sessions): Copestake & Briscoe 1995; Apresjan 1974; Pustejovsky 1995; Tse et al. 2007; Friston
2010/Bastos 2012; Deco & Rolls (biased competition); Vu & Kellas 2003; Arora et al. 2018; Kintsch 1988;
Waltz & Pollack 1985. **Total: 30 citations underpinning this note.**

## TLDR (plain language)
The plan was: use a "what does this word look/feel/relate to" description (not word-neighbor
statistics) to figure out a word's specific meaning as we read, glue the surrounding words to that
specific meaning, and keep only the glue that shows up again and again — building a big "which nearby
words mean which specific meaning" reference table. Two of the three steps in this plan are well-proven
science and we already built and tested them; neither was the weak link. The third step — using
look/feel/relate descriptions to pick the meaning — we already tried something very close to this at a
richer level than before, and it scored WORSE than what we already have, for a specific, understood
reason: those descriptions only exist, richly, for about half of the words, and even where they exist
clearly telling two meanings apart (like a river bank vs a money bank) is not what was actually slowing
us down — the slow-down is figuring out which nearby WORDS are the clue, which look/feel descriptions
don't help with. Fresh outside reading confirms this description-based trick has only ever been shown to
work for concrete, physical-feeling differences, not for the abstract shades-of-meaning that make up
most of the reference table we need. Bottom line: building the full version of this plan is likely to
score about the same or worse than what we already have, except possibly on the minority of clearly
physical/concrete words — so the smart move is a cheap five-minute check on data we already have before
spending real build time.

## QUESTIONS
None blocking. One judgment call: whether to run the cheap decisive test (near-zero cost, reuses
existing P9 data) before deciding whether any part of this mechanism is worth building at all, versus
treating this note's verdict as sufficient to close the direction outright. Recommend the cheap test —
it is nearly free and would convert an estimate into a measured number.

## NEXT STEPS
1. Run the cheap decisive test (re-slice `exp_atl_hubspoke_grounded_separability_v1` data by concrete/
   abstract stratum) before any new corpus-scale build.
2. If the concrete-stratum win is confirmed, scope a MUCH narrower build (grounded stratified bonus, not
   a universal resolver) as its own small anchor.
3. In parallel, land the already-proven precision-weighting readout refinement (P9, +0.023, ready) and
   continue the learned sense-discriminative-W growth path (parent, +0.059-on-covered) — both outrank
   this mechanism in expected value per the numbers above.
