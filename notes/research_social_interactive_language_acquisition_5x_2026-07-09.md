# Research (brain-first, cross-domain, 5x drill): the SOCIAL/INTERACTIVE engine of language
# acquisition -- does referential grounding require a communicative partner, or can it emerge from
# ingested data alone?

**Date:** 2026-07-09. **Trigger:** direct USER "5-drill FOUNDATIONAL program mapping how humans learn
language" -- this drill's domain is THE SOCIAL/INTERACTIVE ENGINE (usage-based acquisition, child-directed
speech, theory-of-mind/language co-development, language-games/emergent-communication). Prior scour:
`notes/research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md` (today, same
session) already ranked "inter-subjective/social correction" as a Tier-1 (strongly-independent) channel but
only briefly -- this drill supplies the full developmental-mechanism depth behind that one line. Also builds
on `notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md` and
`notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md` (same day: relational/structural
closure cannot manufacture grounded reference; needs an exogenous channel; a buildable externally-fed
numeric-attribute seed recipe was already proposed there). Substrate KB scour
(`director_kb_query.py "interactive language game emergent communication feedback loop"`) returned only
generic WordNet "communicative"/"intercommunication" atoms (cosine 0.30-0.37, char-trigram encoder,
MEDIOCRE per the standing dogfood-tally finding) -- confirms this domain is genuinely un-drilled on the
substrate side, not duplicated. 4 parallel Sonnet lit-scan sub-agents dispatched, one per framework angle
(usage-based/Tomasello; child-directed-speech + negative-evidence; theory-of-mind co-development;
language-games + emergent communication), generic terms only, no substrate framing exposed off-platform.

---

## (S1) Map of the social/interactive mechanisms and which are load-bearing for grounding

Four independent literatures were scanned. Ranked by how directly they bear on **reference grounding**
specifically (not just acquisition speed):

**LOAD-BEARING (the interaction/partner does something a passive corpus provably cannot, per direct
ablation or head-to-head comparison):**

1. **Joint attention + intention-reading (Tomasello's usage-based account).** Carpenter/Nagell/Tomasello
   1998 and Tomasello & Farrar 1986 show *manner* of achieving joint attention (following into the infant's
   focus vs. redirecting it) predicts vocabulary growth, not mere co-occurrence. The single sharpest ablation
   in the entire scan is **Kuhl, Tsao & Liu 2003 (PNAS)**: 9-month-olds get identical Mandarin phonetic input
   via live tutor vs. video vs. audio-only recording of the *same* speakers/material. Only the live,
   interactively-responsive condition produced learning -- video and audio-only, despite identical
   statistical content, produced **zero** measurable phonetic learning. This is a clean content-held-constant,
   interaction-varied ablation, not a correlational study.
2. **Contingency of caregiver response (not content simplification).** Newport/Gleitman/Gleitman 1977
   ("Mother, I'd rather do it myself") found child-directed speech's syntactic *simplicity* is a weak/
   inconsistent predictor of syntactic growth -- the classic "motherese hypothesis" oversold content
   simplification. What *does* show a clean causal effect: **Goldstein & Schwade 2008** manipulated only
   the *timing* of maternal vocal response to infant babbling (contingent vs. yoked non-contingent, content
   matched) and found only the contingent group rapidly restructured babbling -- timing, not content, is the
   active ingredient. The still-face paradigm (Tronick 1978, meta-analyzed 2009) shows withdrawing
   contingency alone (no content change) causes rapid communicative breakdown.
3. **Communicative-loop necessity for compositional/grounded codes (Wittgenstein -> Steels -> emergent
   communication ML).** This is the cleanest, most repeatedly-replicated cross-paradigm result. Wittgenstein's
   private-language argument (no community to check correctness -> no fact of the matter about correct use)
   is mechanistically instantiated by Steels' Talking Heads naming games (grounded reference converges only
   through repeated speaker/hearer/success-feedback rounds, never from one agent inventing words alone) and by
   modern ML: **Kottur et al. 2017** shows unconstrained multi-agent dialog collapses to non-interpretable,
   non-compositional shortcut codes without added constraints; most decisively, **the SimSiam Naming Game
   (2024)** ran the head-to-head control that matters most -- identical training objective, communicating
   two-agent setup (SSNG) vs. self-supervised-only no-communication baseline (NoCom): **NoCom reaches ~11-12%
   task accuracy with near-zero cross-agent alignment (cosine 0.04) vs. ~59% accuracy / 0.83 alignment for the
   communicating pair.** This is the single strongest, most direct piece of evidence in this entire drill:
   self-supervised representation-learning alone, absent any partner, essentially fails at producing an
   aligned referential code.

**PARTIALLY LOAD-BEARING (helps, but existence-proof computational models show it is not strictly required
for this specific narrower phenomenon):**

4. **Theory-of-mind / intent-inference for reference resolution.** Bloom's intentionality model (word
   learning requires inferring speaker referential intent to resolve Quine's gavagai indeterminacy) and RSA
   (Frank & Goodman 2012, formalizing a k=1 recursive "pragmatic listener" as the minimal ToM computation
   needed for anything beyond literal reference) both argue intent-inference is necessary in **naturalistic,
   sparse, ambiguous** input. But Yu & Smith's cross-situational statistical word learning shows 12-14-month
   infants (and adults) CAN bootstrap correct word-object mappings from co-occurrence statistics alone, with
   zero ostensive/intentional cues -- in dense, low-ambiguity **lab** conditions. The floor (pure stats) is
   real; it just may not survive contact with naturalistic sparsity/noise.
5. **Negative evidence / explicit correction for grammar.** Brown & Hanlon 1970's classic finding (parents
   don't correct grammar, only truth-value) still stands; recasts (Farrar 1992, Chouinard & Clark 2003,
   Saxton's Direct Contrast Hypothesis) provide a real, accelerating implicit-correction channel where
   present, but **Taatgen & Anderson 2002** built an explicit computational existence proof (ACT-R model)
   reproducing the full overregularization-then-recovery U-shaped trajectory using ONLY ambient corpus/
   frequency statistics -- no feedback, no interaction at all. Pre-emption/entrenchment (Ambridge; PLOS ONE
   meta-analysis) are purely distributional mechanisms. **This is the one mechanism in the whole map that the
   literature shows is NOT load-bearing for its target phenomenon** -- corrective interaction accelerates
   grammar-error recovery but a large-enough passive corpus can do it alone.

**Load-bearing chain, summarized:** referential *grounding* (does the symbol pick out a real thing, checkable
against a real-world/task-shared success criterion) needs a partner-like channel; grammatical
*productivity/error-recovery*, given a large enough corpus, does not. This is the exact same fault line the
substrate's own same-day drills already found from a totally different angle (relational/structural
knowledge vs. grounded meaning; self-referential closure cannot manufacture the property it lacks).

---

## (S2) MAPS-TO-SUBSTRATE: does the self-contained substrate need a communicative-partner /
## speaker-listener self-play loop, or can it ground from ingested data alone?

**Verdict: partial-partner-necessary, but the partner does NOT have to be external.** The convergent
literature answers a narrower question than the one usually asked ("passive data vs. a live human") -- it
answers "closed-loop self-referential estimation vs. an informationally-independent check," which is exactly
the amendment today's `research_brain_independent_channels...` note derived from the compounding-error
thread. Applying that amendment here:

- **Relational/distributional structure** (syntax productivity, error-recovery, word co-occurrence patterns,
  cross-situational statistics in dense conditions) is empirically NOT partner-dependent (Taatgen & Anderson;
  pre-emption/entrenchment; Yu & Smith CSWL). The substrate's existing large-scale ingest-and-compose pipeline
  is the right tool for this slice, no self-play needed.
- **Referential grounding proper** (does the symbol correctly pick out a real, checkable referent, and does
  the code stay aligned/interpretable rather than collapsing into an idiosyncratic private shortcut) is where
  every direct ablation found in this scan (Kuhl 2003; Goldstein & Schwade; SimSiam NoCom-vs-SSNG; Kottur's
  uninterpretable-without-constraints result) shows passive/single-estimator approaches failing or degrading
  sharply. This is the substrate's actual gap, and it maps cleanly onto the SAME finding as the grounded-
  meaning drill (relational closure != grounded meaning) and the independent-channels drill (self-referential
  correction shares failure modes with the thing it's checking).

**The minimal loop, concretely -- a self-contained (no external LLM) speaker/listener self-play design:**

1. **World/referent set:** reuse the already-proposed externally-fed numeric-attribute seed set from
   `research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md` (a small set of
   ground-truth attributes fed once, not an external model) as the shared "physical world" Steels' naming
   games require -- something checkable independent of either role's internal estimate.
2. **Two roles, genuinely asymmetric, not two copies of the same estimator:** a Speaker role that sees the
   full relational-graph neighborhood of a referent and must emit a bandwidth-constrained message (a
   fixed-length HD bundle, not the full representation -- an explicit information bottleneck, per Chaabouni's
   finding that a communication bottleneck, not population size, is what correlates with compositional,
   generalizing codes); a Listener role that sees ONLY the message plus a set of distractor referents and must
   select/reconstruct the correct one. The asymmetry (full-neighborhood view vs. message-only view) is what
   prevents the pair from collapsing into a shared-shortcut code that looks aligned but encodes nothing
   checkable -- this is the substrate-internal analog of Kottur's finding that unconstrained agents converge
   to uninterpretable codes without an added structural constraint.
3. **Success/failure signal, not distillation:** the training pressure is task success (did the Listener pick
   the right referent), never gradient/embedding matching to an external LM -- keeps the design inside the
   "no external AI model" mandate while still providing the informationally-independent check the brain
   literature says is required. This is honestly a self-play loop, not a partner in the human sense; per
   Wittgenstein's argument the open question (below) is whether self-play with two views of ONE substrate is
   a strong enough "community" to make the private-language worry moot, or only a weaker approximation of it.
4. **Contingency over content, per the CDS finding:** the design lever the literature actually supports is
   FAST, tight temporal/architectural contingency between the Listener's guess and the Speaker's next update
   (immediate success/failure feedback each round) -- not "simplify the referent set" or "reduce vocabulary
   size for the model's benefit," which the Newport/Gleitman non-effect result argues against as the wrong
   lever entirely.
5. **A cheap substitute worth flagging:** Kirby's iterated-learning bottleneck result shows compositionality
   can also emerge from a transmission-bottleneck WITHOUT any reward/success signal -- a "student" copy that
   must reconstruct meaning from a compressed teacher output, cheaper to build than a full reward-trained
   dyadic game and closer to the substrate's existing teacher-free-encoder direction. Worth testing as a
   lower-cost first rung before the full success-signal loop.

**Ingested data alone (no self-play, no partner-analog at all) is very unlikely to be sufficient** for the
grounding-proper slice specifically -- every direct comparison found in this scan shows a large, not marginal,
gap (SimSiam's 11% vs 59%; Kuhl's zero-vs-nonzero). It is entirely sufficient for the relational/distributional
slice, which is most of what large-scale ingest already buys the substrate.

---

## (S3) Sharpest open question + deflated P estimates (capped 0.50 for novel synthesis)

**Sharpest open question:** does a self-play loop built from two ASYMMETRIC VIEWS of the same substrate
(shared parameters/failure-modes at some level, differing only in what each role is allowed to see) constitute
a genuine "community" in Wittgenstein's sense -- or is it structurally the same self-referential closure that
today's independent-channels drill and the compounding-error drill already flagged as the recurring substrate
failure mode (a channel that LOOKS independent on a naive screen but shares a hidden common cause)? The
emergent-communication literature's own partial counter-evidence (Kirby's transmission-bottleneck-without-
reward result) suggests the "partner" doesn't have to be a full independent agent -- a sufficiently strict
information bottleneck plus a genuinely separate checkable referent (the externally-fed seed set) might be the
load-bearing ingredient, not agent-count per se. No paper found in this scan tests the exact substrate-relevant
case (two views of ONE underlying estimator, differing only in information access, not in parameters or
learning rule) against the two extremes (fully independent agents vs. fully shared self-supervised
autoencoding) -- this is the natural next drill: search for any result on PARTIAL agent-independence
(shared-weight, asymmetric-view multi-agent setups) in the emergent-communication literature specifically,
since that is closer to what a self-contained substrate can actually build than the fully-separate-agent
setups this scan found.

**P_deflated:**
- P(literature consensus: a communicative-partner-like loop is necessary for referential grounding
  specifically, as distinct from relational/distributional structure, which does not need it) -- raw
  cross-domain convergence is strong (4 independent literatures, one very clean ablation each: Kuhl 2003,
  Goldstein & Schwade, Taatgen & Anderson as the clean NEGATIVE control, SimSiam NoCom-vs-SSNG) -> raw ~0.75,
  **P_deflated ~0.55-0.60** after calibration penalty (kept below "near-certain" because "communicative
  partner" as a single unified category papers over real heterogeneity -- live human, robotic dyad, and
  neural-net referential game are not obviously the same mechanism, and the literature doesn't test that
  they are interchangeable).
- P(novel-synthesis substrate claim: an internal asymmetric-view self-play loop, built from the substrate's
  own architecture with no external model, is SUFFICIENT to satisfy the grounding requirement that the
  literature shows external/live partners satisfy) -- this is the drill's own synthesis, untested in any
  literature found (the shared-weight/asymmetric-view case is exactly the gap named as the open question)
  -> **P_deflated ~0.35-0.40**, held under the mandatory 0.50 novel-synthesis cap.
- P(negative evidence / explicit grammatical correction is NOT load-bearing, i.e. safely skippable given
  large-enough ingested corpus) -- this is the one sub-claim resting on a clean computational existence proof
  (Taatgen & Anderson) plus convergent distributional theory (pre-emption/entrenchment meta-analysis) -> raw
  ~0.55, **P_deflated ~0.35-0.40** (still capped conservatively since Taatgen & Anderson is one model family,
  not a general proof).

**HARD-FAIL thresholds for all three claims are embedded in the cheap decisive test below** (per calibration
discipline: every falsifiable claim carries an explicit failure condition, not just a pass condition).

---

## Cheap decisive test

**Near-zero new build, reuses existing substrate assets.** Directly parallels the SimSiam Naming Game
SSNG-vs-NoCom ablation, which is the single cleanest, most decisive piece of evidence found in this whole scan:

1. **Referent set:** the existing small externally-fed numeric-attribute seed set proposed in
   `research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md` (already scoped, not yet
   built at time of this note -- check before dispatch whether it has landed).
2. **Arm A (NoCom baseline):** a single-view self-supervised/autoencoding readout over the existing relational
   encoder -- reconstruct or retrieve the referent from its own encoding, no message-passing, no second role.
3. **Arm B (asymmetric self-play):** the two-role Speaker/Listener split described in S2 above -- Speaker
   (full-neighborhood view) emits a bandwidth-capped HD message; Listener (message-only + distractors) must
   select the correct referent.
4. **Metric:** novel-referent generalization accuracy (held-out referents never seen during training/self-play)
   plus cross-role/cross-view representational alignment (cosine similarity between what Speaker encodes and
   what Listener decodes, analogous to SimSiam's 0.04-vs-0.83 alignment gap).

**Falsifiable predictions:**

- **HARD-PASS (self-play loop is the substrate's working grounding mechanism, matches the biological/ML
  literature's signature):** Arm B novel-referent accuracy exceeds Arm A by a large, paired-significant margin
  (mirroring the ~5x gap in SimSiam, i.e. Arm B >= 2x Arm A, `sign_p < 0.05`) **AND** cross-role alignment in
  Arm B is substantially above Arm A's baseline alignment. => confirms the load-bearing literature finding
  transfers to the substrate's own architecture; proceed to build the full contingency-timing + bottleneck
  design as a first-class capability.
- **HARD-FAIL (asymmetric self-play collapses to the shared-closure failure mode, the private-language worry
  is realized):** Arm B does not significantly outperform Arm A on novel-referent generalization, **OR**
  cross-role alignment in Arm B is statistically indistinguishable from Arm A's -- i.e. the two "roles" are
  just the same estimator wearing two hats, sharing the exact failure mode the independent-channels drill
  flagged as the disqualifying condition. => the negative would be actionable and precise: it means true agent
  independence (separate parameters/learning rule, not just separate information access) is required, and the
  substrate needs a genuinely externally-fed grounding channel (the small numeric-attribute seed set used
  directly, not mediated through self-play) rather than an internally-generated partner.
- **MIDDLE_BAND:** Arm B beats Arm A but by a small margin (<1.5x) or alignment is only weakly elevated --
  partial signal; run the bandwidth-cap and asymmetry-strength as sweep parameters before concluding either way.

---

## Cross-thread synthesis

- **Directly extends and grounds Tier-1 item #4** ("inter-subjective/social correction") from
  `research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`, which named it in one
  line without developmental mechanism detail -- this drill supplies the full Tomasello/CDS/ToM/language-games
  literature behind that entry, and sharpens its own "independence must be independence of FAILURE MODE, not
  merely of architecture" amendment: the SimSiam NoCom-vs-SSNG ablation and Kuhl's live-vs-recorded ablation
  are BOTH, read this way, empirical confirmations of the exact same principle from entirely different
  literatures (developmental psycholinguistics; multi-agent ML) than the neuroscience literature that note
  scanned -- three-way convergence (neuroscience, developmental psycholinguistics, ML) on one structural
  principle, same day, from three independent starting points.
- **Directly extends `research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`**
  (relational structure != grounded meaning, needs an exogenous channel) by giving the SPECIFIC MECHANISM
  family (communicative/self-play loops) that the developmental literature shows fills that exogenous-channel
  role in humans, and by proposing a concrete architecture (asymmetric-view Speaker/Listener self-play) that
  is compatible with that note's "no external LLM" constraint.
- **Extends `research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md`**'s child-vocabulary-cascade
  angle: that note found fast-mapping/cross-situational learning are one-shot, not compounding, while
  trained-shape-bias is a genuine cascade -- this drill's Yu & Smith CSWL citation is the same mechanism from a
  different angle (pure statistics CAN bootstrap SOME word-object mapping, in dense lab conditions), and this
  drill adds the caveat that naturalistic (sparse, ambiguous, ecologically realistic) conditions are where the
  literature shows the statistics-alone floor breaks down and intent/partner cues become necessary.
- Does not reopen unrelated closures (algebraic-topo, quantum-info, dynamics) per
  `[[feedback-prior-work-informs-not-constrains]]`.

---

## Substrate-product implications

The self-contained substrate (no external LLM) is compatible with "needs a partner-like channel" the same way
the independent-channels drill already established: **"self-contained" means no external AI model; it does
not mean no external or internally-differentiated channel.** Concretely:

1. **(No new build, reframe only)** The already-proposed externally-fed numeric-attribute seed set (from the
   grounded-meaning drill) is the substrate's literal analog of Steels' "shared physical world" -- the
   checkable ground truth neither role's internal estimate can fake. Confirms that proposal is the right
   foundation piece, strengthens the case to build it first.
2. **Asymmetric-view Speaker/Listener self-play cell** (the cheap decisive test above, generalized): a
   standing capability, not a one-off test -- bandwidth-capped message passing between two views of the
   relational encoder, trained on success/failure (task reward), never on distillation-style matching.
   Directly buildable on the existing relational encoder + KB-grounded infrastructure.
3. **Contingency-over-content design lever:** wherever the substrate has any existing feedback/replay loop
   (self-manager, KB-grounded gate, recasts-style correction if any exists), prioritize tightening the
   TEMPORAL/architectural immediacy of the feedback signal over simplifying its content -- the CDS literature's
   clearest lesson is that content-simplification was the wrong lever historically, timing was the right one.
4. **Anti-collapse constraint baked in from day one:** per Kottur's finding, do not build the Speaker/Listener
   split without an explicit bandwidth cap and novel-referent generalization test from the start -- an
   unconstrained version will converge to a private, uninterpretable shortcut code that scores well on
   trained referents while failing the actual grounding test, which is the substrate-internal version of the
   private-language trap.
5. **Cheap fallback rung:** if the full success-signal-trained self-play loop proves expensive to stabilize,
   Kirby's iterated-learning/transmission-bottleneck design (a compressed teacher-to-student reconstruction
   requirement, no reward signal) is a strictly cheaper substitute worth testing first -- closer to the
   substrate's existing teacher-free-encoder direction and requires no reward-learning machinery.

---

## Citations (verified count: 30, all live-URL-confirmed via WebSearch/WebFetch by 4 parallel Sonnet
sub-agents this session, generic developmental-psycholinguistics/philosophy/ML terms only, no substrate-novel
mechanism names, cell names, configs, or numerical parameters exposed off-platform per
`[[feedback-query-privacy-decomposition]]`)

**Usage-based acquisition / Tomasello (8):**
1. Carpenter, Nagell & Tomasello (1998), *Monographs of the SRCD* 63 -- joint attention 9-15 months.
2. Tomasello & Farrar (1986), *Child Development* 57(6) -- joint attention and early language.
3. Baldwin (1991), *Child Development* 62(5) -- infants' contribution to joint reference.
4. Akhtar & Gernsbacher (2007) -- "Joint Attention and Vocabulary Development: A Critical Look."
5. Kuhl, Tsao & Liu (2003), *PNAS* 100(15) -- live vs. recorded phonetic-learning ablation.
6. "Two are better than one" (2018), *PNAS* -- peer co-presence and video learning.
7. Tomasello (2000) -- item-based/verb-island syntactic development.
8. Yang, Tolerance Principle (lingbuzz/002833) -- productivity threshold, counter-evidence to pure gradualism.

**Child-directed speech / negative evidence (9):**
9. Snow (1972) -- motherese register, refutation of impoverished-input claim.
10. Newport, Gleitman & Gleitman (1977) -- CDS syntactic simplicity non-effect.
11. Goldstein & Schwade (2008), *Psychological Science* -- contingent vocal feedback shapes babbling.
12. Tronick (1978) still-face paradigm; Mesman et al. (2009) meta-analysis.
13. Brown & Hanlon (1970) -- no correction of grammatical errors.
14. Farrar (1992), *Developmental Psychology* -- recasts and morpheme imitation.
15. Saxton (1997), *J. Child Language* -- Direct Contrast Hypothesis.
16. Chouinard & Clark (2003), *J. Child Language* -- adult reformulations as negative evidence.
17. Taatgen & Anderson (2002), *Cognition* -- past-tense U-shape without feedback (ACT-R existence proof).
18. Ambridge (2013 WIREs review); Preemption vs. Entrenchment (PLOS ONE); meta-analysis (Collabra 2018).

**Theory of mind / language co-development (7):**
19. Milligan, Astington & Dack (2007), *Child Development* -- meta-analysis, language-FB directionality.
20. Onishi & Baillargeon (2005), *Science* -- implicit false-belief in 15-month-olds.
21. De Villiers & Pyers (2002), *Cognitive Development* -- complement syntax precedes false-belief passing.
22. Bloom -- intentionality model of word learning, Quine's gavagai problem.
23. Clark & Brennan (1991) -- Grounding in Communication.
24. Frank & Goodman (2012), *Science* -- Rational Speech Act framework, k=0/1/2 recursion.
25. Yu & Smith -- cross-situational statistical word learning in 12-14-month infants.

**Language games / emergent communication (9, some overlap consolidated):**
26. Wittgenstein, *Philosophical Investigations* -- language-games, private language argument.
27. Steels & Loetzsch -- Talking Heads / grounded naming games.
28. Lewis (1969) signaling game -- formal ancestor of referential games.
29. Lazaridou, Peysakhovich & Baroni (2017, ICLR); Havrylov & Titov (2017, NeurIPS) -- neural referential games.
30. Kottur et al. (2017, EMNLP) -- unconstrained agents collapse to non-compositional codes; Chaabouni et al.
    (ICLR 2022) -- bottleneck drives compositionality, population size does not; Kirby -- iterated learning;
    SimSiam Naming Game (2024, arXiv 2410.21803) -- SSNG (59%, alignment 0.83) vs. NoCom (11-12%, alignment
    0.04) head-to-head ablation, the single decisive result of this drill.

All 4 sub-agents used generic terms only ("Tomasello joint attention infant language development,"
"child-directed speech contingent feedback negative evidence recast," "theory of mind false belief language
acquisition rational speech act," "Wittgenstein language game Steels naming game emergent communication
referential game compositionality") -- no substrate-novel mechanism names, cell names, configs, or numerical
parameters were exposed off-platform, per `[[feedback-query-privacy-decomposition]]`.
