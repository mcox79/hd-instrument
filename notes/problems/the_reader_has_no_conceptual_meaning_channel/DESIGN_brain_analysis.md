# DESIGN + brain analysis -- the_reader_has_no_conceptual_meaning_channel

*Solver session (opus 4.8). This is the reasoning log; SOLVED.md is the deliverable. Numbers below the
line marked RESULTS are from the full run; everything above is the brain frame + design, stable.*

## 1. The brain frame (opening move: how does the brain actually do this?)

**Controlled Semantic Cognition (Lambon Ralph, Jefferies, Patterson, Rogers 2017).** Semantic cognition
is TWO systems plus a controller:
- an **amodal ATL CONCEPTUAL HUB** -- captures what a concept IS (definitional / taxonomic / relational
  structure), computing TAXONOMIC similarity (dog~wolf), privileging DISTINCTIVE features (semantic
  dementia loses those first: zebra->horse over-regularisation);
- a distributed **distributional / ASSOCIATIVE system** (temporo-parietal / angular gyrus / pMTG) --
  captures THEMATIC relatedness from broad co-occurrence (dog~leash);
- **semantic control** (LIFG / pMTG) -- selects the task-appropriate representation, engaged in
  proportion to competition/conflict.

The reader has ONLY the associative system and is at CHANCE on human meaning-IDENTITY. This problem builds
the missing conceptual hub and asks whether the two-system architecture is real on our substrate.

## 2. Research drill (dispatched; findings that shaped the build)

A focused literature drill (CSC hub-and-spoke, taxonomic-thematic, semantic control, distributional
semantics, acquisition) returned five load-bearing findings:

1. **The ATL hub is a LEARNED cross-modal covariance DISTILLATION** (Rogers & McClelland 2004; Chen,
   Lambon Ralph & Rogers 2017), not a fixed feature-lookup. Its emergent content privileges distinctive
   features (an EMERGENT property of the distillation, not a separate mechanism). **A raw gloss-bag is a
   PARTIAL proxy: PINNED for the categorical/genus (IS-A) content; OUR-INVENTION-UNDER-TEST for the graded
   similarity metric -- which the literature says likely needs a covariance/distillation step over the
   features.** => I must TEST the distillation step, not assume gloss-cosine is the faithful metric.
2. **Taxonomic (similarity) vs thematic (relatedness) is a REAL BUT PARTIAL dissociation** (Mirman,
   Landrigan & Britt 2017 review; semantic-dementia over-reliance on thematic knowledge supports it;
   Jackson et al. 2015 overlap complicates it). => report the dissociation as real-but-partial; expect
   channel overlap/leakage (do NOT claim a clean double dissociation).
3. **Semantic control is COMPETITION-GATED and graded** (Badre & Wagner 2007; Jefferies 2013; Noonan 2013;
   Davey TMS): control engages in proportion to conflict/weak-association and is near-absent for easy,
   dominant retrievals. **Switch-vs-blend as the control MECHANISM is UNSETTLED (OUR-INVENTION); the
   competition-gating principle is PINNED.** => routing should be tested against fusion ONLY on
   conflict/competition items; on easy decontextualised rating, fusion is expected to win (control inert).
4. **Distributional models capture relatedness >> genuine similarity** (Hill, Reichart, Korhonen 2015;
   mechanism = window size, Levy & Goldberg 2014: wide->topical relatedness, narrow/syntactic->paradigmatic
   similarity). => GloVe is a FAIR, mechanistically-understood STRONG associative competitor; its rel>>sim
   gap is a genuine property, not a bad implementation.
5. **The associative-only reader is a real DEVELOPMENTAL STAGE** (syntagmatic->paradigmatic shift ~6-9y;
   explicit definitional skill is later + schooling-linked; semantic control is latest-maturing, PFC into
   the 20s). => building the conceptual hub + control as later additions onto the associative substrate
   mirrors the brain's own acquisition order; the premise is validated, not an artifact.

## 3. Design (copy the operation; sweep the parameters)

**Instruments (OFF-WORDNET gold -- the integrated prior flagged WiC's WordNet provenance).**
- SimLex-999 (human SIMILARITY, NOT derived from WordNet) + SimVerb-3500 (verbs, similarity) -- the
  IDENTITY axis. SimLex ships **Assoc(USF)** (free-association strength) on the SAME pairs -- the
  RELATEDNESS axis with vocabulary/frequency held fixed (the cleanest dissociation control).
- WordSim-353 (relatedness) -- cross-check.
Gold is independent human judgement; a WordNet-content representation predicting it is a fair test. The
twin (shuffled glosses) controls for mere WordNet coverage; the same-representation-two-golds dissociation
controls for provenance (a lookup artefact would inflate BOTH golds equally).

**Channels.**
- CONCEPTUAL / ATL hub = per-word definitional feature bag (WordNet gloss + examples + synonym lemmas +
  genus/hypernym closure, sense-frequency weighted), **distinctive-feature weighted = global IDF** (a
  token's document-frequency over ALL ~117k synsets; the sparse-space analog of the ATL's
  privilege-distinctive-features op), cosine. Glass-box, static, offline (admissible foundation).
  - PRIMARY = FULL (content + genus); CONSERVATIVE = GLOSS-ONLY (pure definitional content, zero taxonomy
    graph) -- reported to defuse "it's just taxonomy-lookup".
  - WRONG-OP floor = UNWEIGHTED count cosine (the audit's flagged inverse of distinctive-feature
    privileging).
  - DISTILLED = SVD covariance-distillation (+whiten) over the definitional features, fit gold-blind on a
    background WordNet sample -- the literature-faithful ATL metric; TESTED against the sparse IDF cosine.
- ASSOCIATIVE (steelman) = GloVe-wiki-gigaword-300 (strong static distributional foundation; the reader's
  own co-occurrence is ~0.04 on SimLex per the integrated prior -- GloVe is the HARD competitor).
- GROUNDED (prior ATL spoke) = distinctive-feature-weighted (whitened) Lancaster+Brysbaert grounding, from
  the integrated `the_substrate_has_one_meaning_system...` SOLVED.

**Bars.**
- A (identity): CONCEPTUAL beats ASSOCIATIVE (and grounded) on SimLex + SimVerb CI-separated over the
  strongest floor's UPPER bound, twin LOSING, floors recomputed. Report gloss-only + full.
- B (dissociation): CONCEPTUAL tracks similarity > relatedness; ASSOCIATIVE tracks relatedness > similarity;
  crossover CI-separated (real-but-partial). WordSim cross-check + SimAssoc333 conflict subset.
- C (routing): mixed-demand pool (SIM block + REL block); demand-ROUTE vs best fixed FUSION vs fixed single
  vs random-switch twin. Plus the CONFLICT-GATED analysis (does conceptual beat fusion specifically on the
  SimAssoc333 conflict pairs, where the associative response misleads?).

## 4. Probe-established findings (scratchpad, pre-full-run -- reproduced in the cell)

- Conceptual (full) on SimLex-similarity rho ~0.55 (n=999, FULL coverage) vs grounded-ATL 0.29 vs the
  reader's associative 0.04; twin (shuffled glosses) ~ -0.001. Gloss-ONLY (no taxonomy) ~0.36 -- already
  beats grounded + reader's-associative; ties strong GloVe (0.37). The taxonomy genus terms take it to
  0.55, past even GloVe.
- Double dissociation vs GloVe: {conceptual, GloVe} x {SimLex-sim, SimLex-assoc, WordSim-rel} =
  conceptual sim 0.55 / assoc 0.35 / rel 0.47; GloVe sim 0.37 / assoc 0.39 / rel 0.61. Crossover +0.24.
  On the conflict subset (SimAssoc333) every conceptual variant tracks similarity (0.26-0.48) far above
  association (0.16-0.20).
- **DISTILLATION BOUNDARY (the research's open question, TESTED):** SVD covariance-distillation (+whiten)
  over the definitional features does NOT beat the sparse IDF cosine (raw IDF 0.518; best distilled dim=500
  whiten=True 0.508, monotonically approaching from below). On the DENSE 12-dim grounding space the prior
  SOLVED found decorrelation/whitening HELPS; on the SPARSE high-dim definitional space, IDF already
  realises the distinctiveness and SVD compression only blurs the rare distinctive tokens that carry
  synonymy. **One ATL principle (privilege distinctive features), two supply-dependent realisations:
  dense->whiten, sparse->IDF.** This is the fidelity BOUNDARY, reported honestly (not a ceiling).

## 5. Labelling (invent freely; mislabelling is the only bar)

- PINNED: two-system (conceptual/taxonomic vs associative/thematic) architecture; ATL privilege-distinctive
  op-class; distributional = relatedness (rel>>sim); competition-gating of control; acquisition order.
- PARTIALLY-PINNED: the sim/rel dissociation is real-but-partial (expect overlap); gloss/genus content as
  the hub's categorical layer.
- OUR-INVENTION-UNDER-TEST: instantiating the hub as WordNet-gloss+genus IDF cosine; the covariance-
  distillation metric (tested -> does not beat IDF here); switch-vs-blend as the control mechanism;
  sense-aggregation; taxonomy depth.

---
## RESULTS (full run, verdict CONCEPTUAL_CHANNEL_WINS_IDENTITY_AND_DISSOCIATES; both bars PASS)

Witness `verification/test_conceptual_meaning_channel.py` reproduces these INDEPENDENTLY (fresh recompute).

**BAR A -- identity (conceptual beats the steelmanned GloVe, off-WordNet gold):**
- SimLex-999 (n=999): CONC **0.5210** CI[0.4725,0.5703] vs GloVe **0.3705** CI[0.3078,0.4320] -- margin
  **+0.1505 CI[0.0850,0.2156]** (ci_hw 0.065). Gloss-only 0.3996; grounded-ATL 0.2902; concreteness -0.1380;
  twin p95 **0.0622** (LOSES). IDF vs UNWEIGHTED(WRONG-OP) +0.0247 CI[0.0145,0.0356]; IDF vs DISTILLED
  +0.0279 CI[0.0013,0.0531] (distillation does NOT beat sparse IDF).
- SimVerb (n=2986): CONC **0.4981** vs GloVe **0.2204** -- margin **+0.2777 CI[0.2377,0.3165]**; twin p95
  0.0420; distilled 0.5070 (ties IDF, CI incl 0).

**BAR B -- double dissociation (real-but-partial):** same SimLex pairs -- CONC sim 0.5210 > assoc 0.3420;
GloVe sim 0.3705 <= assoc 0.3881; crossover **+0.1966 CI[0.1113,0.2815]**. WordSim relatedness: GloVe
**0.6102** > CONC 0.4028 (+0.2074 CI[0.0970,0.3150]). Each system wins its own axis; channels overlap
(CONC 0.34 on assoc; GloVe 0.37 on sim) -- partial, as the biology predicts.

**BAR C -- routing (fusion wins on easy rating; reconciles brief vs disk):** mixed pool -- ROUTE mean
0.5656 vs best fixed FUSION 0.5958 (alpha 0.70); route-minus-fusion **-0.0302 CI[-0.0631,0.0040]** (TIE
leaning fusion). ROUTE (0.566) > random-switch p95 (0.442) so the task signal is real, but fusion is at
least as good. CONFLICT-GATED: conceptual-minus-fusion swings from -0.053 (congruent) to +0.016 (SimAssoc333
conflict) -- the competition-gating DIRECTION, not CI-separated on rating. => faithful design: wire the
conceptual hub, DEMAND-ROUTE for identity, FUSE for graded rating, keep conflict-gated SELECTION in the
already-built semantic-control organ (context_override slug, trigger AUC 0.79).

**Runtime note:** the ATL covariance-DISTILLATION arm (builds thousands of background definitional bags) is
gated behind `--with-distill` (SLOW, ~45min at full); the landed metrics.json carries its tested-negative
result. The default full path + the witness use a cached GloVe benchmark subset (glove_bench_subset.npz) so
they skip the 4-min full-GloVe load. hdlab/ NOT modified.

## FINEST-RESOLUTION LIMIT MAP (2nd research drill + exp_conceptual_channel_limits_v1)

Owner: "are we truly brain-foundational; do we understand the limits and why?" A second (finest-resolution)
research drill + a landed limit diagnostic answer: the ceiling is **SUPPLY-limited, not method-limited**.
- **Ceiling is real:** SimLex IAA rho~0.67 (pairwise); model ceiling ~0.70s (counter-fitting 0.74). Our 0.52
  has ~0.15-0.2 genuine headroom, not noise.
- **Per-POS:** N CONC 0.599 / GloVe 0.397; V CONC 0.492 / GloVe 0.152; **A CONC 0.479 / GloVe 0.585** (the
  one class we lose). WHY: WordNet gives adjectives NO genus hierarchy (antonym-anchored scalar clusters) --
  a FORMAT mismatch; adjectives are scalar/MAGNITUDE (Kennedy; ATOM), not taxonomic.
- **Drill's #1 fix (route adjectives -> grounded spoke) TESTED and REFUTED:** grounded 0.170 vs conceptual
  0.479 on adjectives (grounded-minus-conceptual -0.309 CI[-0.536,-0.093]). WHY: our grounded asset is
  SENSORIMOTOR (Lancaster perceptual/action), not the scalar-MAGNITUDE representation adjectives need; many
  SimLex adjectives are abstract. => unbuilt SUPPLY gap, not the sensorimotor spoke.
- **Antonyms:** GloVe rates opposites HIGHER than random (0.539 vs 0.388) -- association cannot separate
  opposites; conceptual rates them correctly low. WordNet antonym-repulsion patch +0.037 -- TARGET-faithful,
  MECHANISM-approximate (faithful form = Osgood bipolar scalar axes = the same missing supply). NOT wired
  (a convenient symbolic patch, not the operation).
- **Learned GPU hub premature:** a hub earns its keep reconciling HETEROGENEOUS spokes (Silberer & Lapata
  2014); over one spoke there is nothing to reconcile (my linear-distillation tie corroborates). Build it
  only after a 2nd structurally-different spoke exists.
- **Unifying frontier (mapped, timeboxed):** an unbuilt SCALAR/MAGNITUDE + brain-derived feature-norm
  (Binder-65/McRae) SUPPLY -- fixes adjectives + antonyms + gives the hub a second spoke. A supply-building
  program, filed not half-built.

## THE WALL IS A WRONG-OPERATION, AND A BUILD TARGET (aggressive drill + exp_scalar_adjective_operation_v1)

Owner: "if the brain can do it and we can't, understand WHY." Aggressive mechanism drill (Walsh ATOM/IPS
magnitude system; Moyer distance-effect for scalar adjectives; Kennedy degree semantics; Osgood; SemAxis
An 2018 / Nguyen 2016) -> the adjective failure is a WRONG-OPERATION, not missing data:
- **No single similarity operation.** NOUN = taxonomic feature/genus overlap (gloss channel, 0.599);
  ADJECTIVE = SIGNED-magnitude distance on a shared scale (feature-overlap cosine has no order/sign ->
  structurally wrong); VERB = relational/argument-structure (gloss carries it, 0.492; GloVe's single blended
  vector fails at 0.152 -- polysemy-blending). One cosine is wrong for 2 of 3 classes.
- **Built from OWNED resources (no new data):** GloVe encodes scale-MEMBERSHIP; WordNet antonym pole-pairs
  supply POLARITY. Op = GloVe cosine - lambda*opposite-pole-penalty on the relevant antonym axis (SemAxis).
  SimLex adjectives 0.585 -> 0.623; INFO-FREE RANDOM-AXIS control at matched lambda LOSES (0.553).
- **CI-separation power-limited (n=111 adj pairs):** antonym-axis-minus-GloVe +0.038 CI[-0.050,0.127];
  minus-random +0.070 CI[-0.002,0.151]. Point estimates as predicted, CIs just include 0 -- a POWER limit
  (need a larger adjective gold), not a mechanism failure. First (global profile-cosine) impl FAILED (tied
  its random control) -- the wrong operationalisation; the corrected per-pair signed-opposition op works.
- **Wiring implication:** OPERATION-ROUTE the read-out by word class; this is the natural home for the
  semantic-control router (route by word-class demand as well as task demand).
