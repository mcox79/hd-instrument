# Brain mechanism of ROBUST FEW-SHOT SCHEMA INDUCTION from individually-NOISY episodes

Research drill for `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference`.
Date 2026-08-31. Author: solver (finer brain-fidelity drill on the WEAK canonical-order result).
ONLINE-literature synthesis; calibration penalty applied — every "should"/"would" is a DESIGN
HYPOTHESIS pending our own measurement, NOT an inherited number.

**Scope.** I reused the substrate's brain-faithful ordering organ (`hdlab/transitive_ordering`) to LEARN a
canonical script order: read ~12 training narratives per scenario through the reader, extract each one's
event sequence from the reader's OWN timeline, aggregate the modal pairwise precedence into premises,
integrate on the ordering line, answer before/after on a NEW story by transitive read-out. Measured result:
a WEAK, NOT-CI-separated signal (end-to-end 0.535 vs random-order twin 0.492; on the subset the single
passage leaves undetermined 0.64 vs 0.48, n=25; canonical-used accuracy 0.532 [0.436, 0.630], CI includes
chance). The order LOOKS plausible in samples ("give→sign→leave"; "ask-for-ID before serve") but does not
reach significance. Retrieval fires on only 36% of items. This drill asks the mechanism question that
decides the next build: **is the weakness NOISY EXTRACTION (garbage-in), a TOO-CRUDE ABSTRACTION (modal
tally), or TOO FEW episodes — and should we route the noisy episodic sequences through a
consolidation/replay DENOISER before loading the ordering line?**

**Builds on** the two sibling drills and does NOT rehash them:
- `research_script_vs_episodic_temporal_order_wall_2026-08-31.md` established the DISSOCIATION (episodic
  hippocampal timeline vs canonical mPFC/posterior-medial schema; Baldassano 2018; the wall is a KNOWLEDGE
  gap = the missing canonical-order store) and recommended BUILDING the learned canonical-order prior — the
  build this note now diagnoses.
- `research_inference_over_situation_model_brain_mechanism_2026-08-31.md` established the
  online/offline + RECALL/STEP/KNOWLEDGE attribution frame.
This note goes FINER on ONE thing those two did not touch: the QUALITY of the INDUCTION step — how the brain
turns a handful of noisy episodes into a clean schema, and where in that pipeline our weakness sits.

**Prior-arc work on robust schema induction / replay-denoising / community-detection order learning:** NONE
(`experiment_index.py query "schema induction event order"` = 0 cells; freshly-opened problem; the two
sibling drills are the only adjacent notes and neither covers the induction ALGORITHM or a denoiser).

---

## Q1 — How the brain extracts a CLEAN schema from FEW, INDIVIDUALLY-NOISY episodes (the denoising step)

**The load-bearing division of labour (PINNED — CLS).** McClelland, McNaughton & O'Reilly (1995): the
hippocampus rapidly stores episode-specific bindings; the neocortex SLOWLY extracts cross-episode
regularities via **interleaved learning**. Kumaran, Hassabis & McClelland (2016) update this: the
regularity-extraction is driven by **hippocampal replay / sharp-wave ripples (SWRs)** that reactivate stored
episodes offline and feed them, interleaved, to the neocortex. So the abstraction is NOT a one-shot tally
over the raw episodes — it is a slow statistical distillation over MANY reactivations.

**The single most decisive mechanistic paper for our question: Spens & Burgess (2024), *Nature Human
Behaviour* 8:526–543 — "A generative model of memory construction and consolidation."** This is a published,
computational brain model of exactly the extraction-from-noise step:
- Consolidation is **teacher–student generative replay**: the hippocampal autoassociative store (a Modern
  Hopfield Network) is the TEACHER; it REPLAYS stored episodes to train a neocortical **generative model**
  (a variational autoencoder in EC / mPFC / anterolateral temporal cortex) as the STUDENT. The student
  learns the LATENT STATISTICAL STRUCTURE shared across episodes = the schema.
- The denoising is **reconstruction toward the learned distribution**, NOT an explicit average: the
  generative model reconstructs the PREDICTABLE (schema-consistent) components and lets the hippocampus keep
  the UNpredictable per-episode details. Quantitatively (their sims): recalled items from the same class
  become MORE similar (intra-class variance drops, *t*(7839)=60.5, *d*=−0.684); atypical exemplars are
  distorted toward the prototype (boundary extension; DRM-style false memories scale with list length).
- **KEY NUMBER for us:** their VAE trains on ~**10,000 replayed samples**. The brain's replay manufactures
  FAR MORE training instances than the raw episode count. Schema abstraction is GRADUAL and
  sample-hungry (their semantic-decoding curve improves continuously across epochs; no sharp threshold).
- Their own framing: consolidation is *"a continuous rebalancing from hippocampal detail-storage toward
  neocortical schema-reliance, necessarily introducing gist-based distortions as a byproduct of efficient
  compression."*

**So YES — there is an explicit denoising/abstraction step between the noisy episodic traces and the clean
schema, and our raw modal-tally is a degenerate one-pass caricature of it.** The brain's version has three
properties our tally lacks: (i) it operates over MANY reactivations (generative replay multiplies the
sample count), (ii) it regularizes toward a learned generative distribution (not a per-pair majority vote),
(iii) it is precision/reliability-sensitive (Q3). PINNED: a denoising/abstraction step exists and is
replay-driven. OUR-INVENTION-UNDER-TEST: that our specific modal-tally is an adequate stand-in for it (this
note argues it is not, but only partially — see the verdict).

**The critical statistical caveat I must flag (my synthesis, labelled as such).** Averaging/regularizing
over many instances cancels **zero-mean, episode-INDEPENDENT** noise — "integration of previously and
currently observed information … ameliorat[es] unreliability of individual perceptual events" (the
multi-instance-averaging literature; e.g. schema+episodic optimal-combination work below). It does NOT
cancel **SYSTEMATIC bias**. This is elementary statistics (PINNED), but its application to our case is a
HYPOTHESIS: if our parser misses the same construction types in EVERY narrative (systematic recall bias),
then NO amount of replay/tally removes it — more episodes entrench it. If instead our per-episode errors are
roughly independent garbles (some narratives parse cleanly, some don't), a denoiser + more episodes CAN
recover the signal. **Which regime we are in is the whole ballgame, and it is directly testable (Q5 build).**

---

## Q2 — EXTRACTION vs ABSTRACTION: where is the bottleneck in the brain, and can abstraction rescue noisy episodes?

**In humans the per-episode extraction is HIGH-FIDELITY, and schema induction is BUILT ON TOP of that.** Two
independent lines say clean episodic encoding is (largely) the PRECONDITION, not something abstraction
manufactures:

1. **Prediction-error-GATED encoding (SLIMM; van Kesteren et al. 2012, *TICS* 16:211–218).** Schema-congruent
   input is encoded EASILY (mPFC schema pre-activates and scaffolds MTL encoding); schema-INcongruent input
   throws a prediction error that recruits the hippocampus to encode the specifics. Either way the SYSTEM
   spends effort ensuring each episode is ENCODED WELL before it can contribute to (or update) the schema.
   The schema does not paper over a failure to perceive the event; it decides HOW the well-perceived event
   is stored.

2. **Schema abstraction is a REGULARIZER, not an error-corrector of the input signal.** Spens & Burgess
   (2024) and the fuzzy-trace / reconstruction literature (Brainerd & Reyna gist-vs-verbatim; the
   optimal-combination result — Hemmer & Steyvers 2009, *Psychon. Bull. Rev.*) are unanimous on the
   DIRECTION of the correction: the schema pulls recall toward the PROTOTYPE. That HELPS when the schema is
   right and the episode is genuinely noisy (it fills predictable gaps), but it INTRODUCES distortion
   (schema-consistent false memory; boundary extension; DRM lures) — it is NOT a mechanism for recovering
   the TRUE-but-mis-extracted content of a specific episode. In other words, **the brain's abstraction does
   heavy error-correction toward the SCHEMA MEAN, but it cannot invent signal the episodes never carried.**

**Consequence for us (PINNED direction, our-application HYPOTHESIS):** the literature is consistent with
"clean episodic extraction is the precondition; abstraction regularizes and fills, it does not resurrect
mis-parsed content." If our per-episode timelines are SYSTEMATICALLY wrong (miss the same events, invert the
same orders), a better abstraction algorithm will faithfully abstract the SYSTEMATIC ERROR. That is the
argument for EXTRACTION being the deepest wall — and it is exactly the project's recurring parser-recall
ceiling.

**BUT there is a real, bounded thing abstraction CAN fix, and our data says it is live.** The
optimal-combination principle (Hemmer & Steyvers 2009; the "reconstruction of familiar objects is biased to
the specific prior, unfamiliar objects to the category centre" result) shows the brain **precision-weights**:
noisy episodes are DOWN-weighted, reliable ones UP-weighted; the posterior is a reliability-weighted blend,
NOT a per-item majority vote. Our modal tally treats every episode as an EQUAL vote. If our per-episode
extraction quality is HETEROGENEOUS (some narratives parse cleanly, some are garbled — which is almost
certainly true), then equal-weight voting is throwing away recoverable signal that precision-weighting would
keep. That is an ABSTRACTION fix that does NOT require touching the parser, and our own result — signal is
REAL on the decided subset (0.64) but UNDERPOWERED (36% fire, n=25) — is consistent with "the signal is in
the clean episodes and the crude aggregator is diluting it."

**Verdict on Q2:** the brain says clean extraction is the PRECONDITION (abstraction regularizes, does not
resurrect), which makes EXTRACTION the deepest wall — BUT the SPECIFIC crudeness of our aggregator
(equal-weight, single-step) is independently costing us power, and that part is fixable without the parser.

---

## Q3 — What ABSTRACTION algorithm does the brain use beyond a modal tally?

Three brain-faithful upgrades over "count pairwise precedence + majority-vote," in increasing order of how
much they beat a tally:

**(a) PRECISION / RELIABILITY WEIGHTING (PINNED at the computational level).** Reconstruction is a
Bayesian, reliability-weighted combination of noisy traces and the schema prior (Hemmer & Steyvers 2009;
the optimal-combination literature). van Kesteren's SLIMM adds the neural gate: prediction error sets
whether an episode updates the schema at all. **Upgrade for us:** weight each episode's pairwise votes by an
extraction-confidence, and let high-prediction-error (surprising, likely-misparsed) episodes contribute
less — NOT one-episode-one-vote. We already have a live per-event confidence signal to drive this: the
just-landed `predict_surprisal` node exposes per-event surprisal + `pred_precision` on `EventRecord`.

**(b) TEMPORAL COMMUNITY STRUCTURE / SUCCESSOR-REPRESENTATION aggregation (PINNED — this is the decisive
"tally is too crude" result).** Schapiro, Rogers, Cordova, Turk-Browne & Botvinick (2013, *Nature
Neuroscience*; hippocampal fMRI follow-up Schapiro et al. 2015, *Hippocampus*, n=20): the hippocampus learns
higher-order sequence structure — which items share PREDECESSOR/SUCCESSOR SETS — even when every pairwise
transition probability is EQUAL (0.25), i.e. when there is NO pairwise-frequency cue AT ALL. **A pairwise
majority tally is provably blind to this**; the brain represents items by "the similar predictions they make
about the future," which is the **successor representation** (Stachenfeld, Botvinick & Gershman 2017, *Nature
Neuroscience*; Momennejad et al. 2017). The SR accumulates MULTI-STEP, temporally-discounted precedence
rather than adjacent-pair counts. **Why this matters for order specifically:** an SR-style aggregator pools
transitive, multi-step co-precedence, so it (i) extracts a stable ordering from FEWER direct observations
(more noise-robust — each pair's estimate borrows strength from indirect paths) and (ii) DECIDES more pairs
(raises the 36% coverage) because A-before-C is inferable from A-before-B and B-before-C even if A and C were
never adjacent. This is more brain-faithful AND directly attacks our under-power.

**(c) GENERATIVE-REPLAY AUGMENTATION (PINNED — Spens & Burgess 2024).** Multiply the effective sample count:
once a partial schema exists, SAMPLE synthetic orderings from it and interleave them with the real episodes,
so the estimate is stabilized over many reactivations rather than 12 raw traces. This is the brain's answer
to "too few episodes."

**Note on the existing substrate.** `hdlab/schema_exemplar_bayes` already implements an LSE-Bayes posterior
ROUTING over schema clusters (a precision-weighted posterior mechanism) — but it is a FACT-RETRIEVAL
compressor, not a sequence-order aggregator. The missing piece is a confidence-weighted, multi-step
(SR-flavoured) SEQUENCE aggregator feeding `transitive_ordering`. That is a NEW composition, not an existing
organ.

---

## Q4 — SHOULD schema induction route the noisy episodic sequences THROUGH a consolidation/replay denoiser before the ordering line?

**Brain-faithful answer: YES in principle — that IS the pipeline (hippocampal episodic traces → replay-driven
neocortical distillation → schematic store) — with two hard caveats that determine whether it helps US.**

The brain-faithful pipeline, mapped to our organs:

```
  reader.read(narrative_i)                         [hippocampal EPISODIC encoding — noisy, per-story]
        │   per-episode: event sequence from sm.timeline_order
        │               + per-episode CONFIDENCE  (parse completeness; mean pred_precision;
        │                                           1 − mean surprisal from the live predict_surprisal node)
        ▼
  CONSOLIDATION / REPLAY DENOISER                  [the missing organ — compose, don't invent from scratch]
        │  (1) PRECISION-WEIGHT pairwise precedence by per-episode confidence   (Hemmer&Steyvers; SLIMM)
        │  (2) accumulate MULTI-STEP, discounted co-precedence (SR-style)       (Stachenfeld'17; Schapiro'13)
        │      — not adjacent-pair counts; borrows strength across indirect paths
        │  (3) optional GENERATIVE REPLAY: sample synthetic orders from the
        │      partial schema + interleave to stabilize the estimate           (Spens&Burgess'24)
        ▼
  CLEAN CANONICAL-ORDER SCHEMA                     [neocortical / mPFC-analog store]
        │   denoised, precision-weighted pairwise order + confidences
        ▼
  transitive_ordering.TransitiveOrderingLine.integrate(premises)   [the READOUT organ — already faithful]
        │   transitive-closure magnitude line
        ▼
  answer before/after, with EPISODIC OVERRIDE where THIS passage marks a deviation (flashback/pluperfect)
```

**Caveat 1 (sample count).** The denoiser only earns its keep with ENOUGH reactivations. Spens & Burgess use
~10,000 samples; we feed 12. Generative-replay augmentation (step 3) is precisely the compensation, but it
can only amplify signal the episodes ALREADY carry — it cannot fabricate a correct order from systematically
wrong episodes.

**Caveat 2 (zero-mean vs systematic — the gate on the whole idea).** A denoiser that averages/regularizes
REMOVES zero-mean independent extraction noise and KEEPS systematic bias. So routing through consolidation
HELPS iff our extraction noise is roughly zero-mean/heterogeneous, and is FUTILE (or worse — it will
confidently entrench the wrong order) iff the noise is systematic. **This is the same fork as Q1/Q2, and the
build below is designed to RESOLVE it as a side-effect.**

Conclusion: compose `consolidation-denoiser + transitive_ordering` rather than raw-tally — but build it so
its result DIAGNOSES the noise regime, because that determines whether the ceiling is the denoiser or the
parser underneath it.

---

## Q5 — VERDICT: (a) noisy extraction / (b) too-crude abstraction / (c) too few episodes — and the single highest-leverage build

**Most likely diagnosis: a COMPOUND, with (a) NOISY EXTRACTION as the deepest / rate-limiting wall, (b)
CRUDE ABSTRACTION as a real and CHEAPLY-fixable secondary loss, and (c) TOO-FEW-EPISODES as a compounding
factor that only bites through (a).** Reasoning, tied to our own numbers and the biology:

- **Why (a) is deepest.** The biology says clean episodic extraction is the PRECONDITION for schema
  induction; abstraction regularizes toward the schema mean, it does not resurrect mis-parsed content (Q2).
  Our 36%-retrieval-fires and the fact that accuracy stayed FLAT when event RETRIEVAL was improved
  (coverage 0.55→0.69, per the sibling drill) both point at the input side. This is the project's unifying
  parser-recall ceiling, now seen through the schema-induction lens.
- **Why (b) is real but secondary — and the honest reason it is the highest-LEVERAGE build.** Our aggregate
  is NOT catastrophically biased: it looks plausible, gets textbook cases right, and reads 0.64 vs 0.48 on
  the DECIDED subset — the signal IS in the inputs, it is just UNDERPOWERED (equal-weight votes dilute clean
  episodes with garbled ones; single-step counts decide too few pairs). A precision-weighted, multi-step
  (SR-style) aggregator directly attacks both — WITHOUT a parser rewrite — and it is the brain's actual
  algorithm. It is cheaper than (a) by an order of magnitude.
- **Why (c) compounds but is not the primary.** 12 episodes is far below the brain's sample-hungry regime
  (Spens & Burgess ~10⁴), but scaling episode count only helps if per-episode signal is clean-ish; with a
  systematically-biased extractor, more episodes entrench the bias. So (c) is downstream of (a).

**THE SINGLE HIGHEST-LEVERAGE BUILD — a consolidation/replay DENOISER between extraction and the ordering
line, built as a DISCRIMINATOR.** Replace the equal-weight single-step modal tally with a brain-faithful
aggregator that (1) **precision-weights** each episode's precedence votes by extraction confidence (drive it
off the already-live `predict_surprisal` per-event `pred_precision` + parse completeness), (2) accumulates
**multi-step, temporally-discounted co-precedence (SR-style)** so it decides more pairs and borrows strength
across indirect paths, and (3) optionally **generative-replay-augments** to lift the effective sample count —
then loads the denoised premises onto `transitive_ordering` with episodic override. Run it as a **scaling +
ablation discriminator**: sweep episodes 12 → 30 → 60 → 120, and compare {equal-weight tally} vs
{precision-weighted} vs {precision-weighted + SR-multistep} vs {+ replay-aug}, tracking DECIDED-subset
accuracy and COVERAGE with the random-order twin LOSING.

This single build is decisive either way:
- If precision-weighting + SR-multistep + more episodes **climb** (coverage up, decided-subset accuracy
  CI-separates from the twin) → the noise was zero-mean/heterogeneous and power-limited → the abstraction WAS
  the fixable wall, the parser is adequate for this task, and we have a real canonical-order organ.
- If they **plateau** at the current weak signal → the noise is SYSTEMATIC → this is a rigorous NEGATIVE that
  routes the problem back to the unifying upstream wall (parser-recall / extraction), now PROVEN (not
  assumed) to be the binding constraint for schema induction too. Either outcome is a publishable result and
  a correct next-step signal.

**One thing NOT to do:** do not "fix the parser" as the first move. It is the deepest wall but the most
expensive, project-wide effort; the biology does not tell us the parser is the ONLY problem here (the
equal-weight/single-step aggregator is independently lossy), and the cheap discriminator above tells us
whether the parser investment is even necessary for THIS capability before we pay for it.

---

## PINNED vs OUR-INVENTION ledger

| Claim | Status |
|---|---|
| CLS: hippocampus stores specifics, neocortex slowly extracts cross-episode regularity via interleaved learning | PINNED (McClelland 1995; Kumaran/Hassabis/McClelland 2016) |
| Consolidation = replay-driven generative distillation; denoises toward a learned distribution; introduces gist distortion; sample-hungry (~10⁴ replays) | PINNED at computational level (Spens & Burgess 2024); the specific VAE/MHN implementation is that paper's MODEL, not a direct recording |
| Averaging cancels zero-mean noise but NOT systematic bias | PINNED (elementary statistics) — its APPLICATION ("our parser noise is systematic") is a HYPOTHESIS the build tests |
| Clean episodic extraction is the precondition; abstraction regularizes toward schema mean, does not resurrect mis-parsed content | PINNED direction (SLIMM; fuzzy-trace; Spens&Burgess); our-case application is a hypothesis |
| Reconstruction is reliability/precision-weighted (down-weight noisy episodes), not equal votes | PINNED at computational level (Hemmer & Steyvers 2009; optimal-combination lit) |
| The brain learns higher-order sequence structure with NO pairwise-frequency cue; a pairwise tally is blind to it; SR captures it | PINNED (Schapiro et al. 2013/2015; Stachenfeld et al. 2017) |
| Route noisy episodic sequences THROUGH a replay/consolidation denoiser before the ordering line | PINNED as the brain's pipeline shape; that it will RESCUE our result is OUR-INVENTION-UNDER-TEST (gated on the zero-mean-vs-systematic fork) |
| Precision-weighted + SR-multistep + replay-aug aggregator feeding `transitive_ordering` | OUR-INVENTION (a faithful COMPOSITION of PINNED mechanisms; must be built + can-fail tested) |

## Proposed AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b` (surfaced for strategy — NOT applied here)
> **Schema induction from noisy episodes is a REPLAY-DRIVEN, PRECISION-WEIGHTED, MULTI-STEP distillation —
> our modal pairwise tally is a degenerate one-pass caricature of it.** The brain's abstraction (a) runs over
> MANY replayed reactivations (generative replay multiplies the sample count; Spens & Burgess 2024), (b)
> reliability-weights episodes (Hemmer & Steyvers 2009; SLIMM), and (c) aggregates higher-order/multi-step
> sequence structure that pairwise counts are provably blind to (Schapiro 2013; SR, Stachenfeld 2017). It
> denoises ZERO-MEAN error but faithfully abstracts SYSTEMATIC bias — so clean episodic extraction is the
> precondition. Follow-on organ: a consolidation-denoiser (precision-weighted + SR-multistep + replay-aug)
> composed with `transitive_ordering`, built as a scaling/ablation discriminator that resolves whether our
> extraction noise is zero-mean (denoiser rescues) or systematic (routes back to the parser-recall wall).

## Key citations
- McClelland J.L., McNaughton B.L. & O'Reilly R.C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. *Psychological Review* 102:419–457.
- Kumaran D., Hassabis D. & McClelland J.L. (2016). What learning systems do intelligent agents need? Complementary Learning Systems theory updated. *Trends in Cognitive Sciences* 20:512–534.
- Spens E. & Burgess N. (2024). A generative model of memory construction and consolidation. *Nature Human Behaviour* 8:526–543. (Replay = teacher–student generative denoiser; schema = learned latent distribution; gist distortion; ~10⁴ replayed samples; gradual.)
- van Kesteren M.T.R., Ruiter D.J., Fernández G. & Henson R.N. (2012). How schema and novelty augment memory formation. *Trends in Cognitive Sciences* 16:211–218. (SLIMM: prediction-error-gated, mPFC↔MTL.)
- Hemmer P. & Steyvers M. (2009). A Bayesian account of reconstructive memory. *Psychonomic Bulletin & Review* 16:80–87. (Reliability/precision-weighted combination of episodic trace + schema prior.)
- Schapiro A.C., Rogers T.T., Cordova N.I., Turk-Browne N.B. & Botvinick M.M. (2013). Neural representations of events arise from temporal community structure. *Nature Neuroscience* 16:486–492.
- Schapiro A.C., Turk-Browne N.B., Norman K.A. & Botvinick M.M. (2015/2016). Statistical learning of temporal community structure in the hippocampus. *Hippocampus* 26:3–8. (n=20; within-community pattern similarity with equal transition prob.)
- Stachenfeld K.L., Botvinick M.M. & Gershman S.J. (2017). The hippocampus as a predictive map. *Nature Neuroscience* 20:1643–1653. (Successor representation.)
- Momennejad I. et al. (2017). The successor representation in human reinforcement learning. *Nature Human Behaviour* 1:680–692.
- Whittington J.C.R. et al. (2020). The Tolman–Eichenbaum Machine: unifying space and relational memory through generalization in the hippocampal formation. *Cell* 183:1249–1263. (Factorized structural vs sensory codes → generalize a learned structure across environments from few examples.)
- Reynolds J.R., Zacks J.M. & Braver T.S. (2007). A computational model of event segmentation from perceptual prediction. *Cognitive Science* 31:613–643. (Prediction-error event boundaries; working event model.)
- Brainerd C.J. & Reyna V.F. (2002). Fuzzy-trace theory and false memory. *Current Directions in Psychological Science* 11:164–169. (Gist vs verbatim; gist drives schema-consistent false memory.)
- Ghosh V.E. & Gilboa A. (2014); Baldassano C., Hasson U. & Norman K.A. (2018) — see the sibling drill (mPFC/PMC canonical-schema store; where the DENOISED schema lives).

---

## TLDR (plain English)
Our reader tried to learn "the usual order of steps in a familiar activity" by reading about a dozen example
stories, pulling each story's order of events out of its own reading, and taking a majority vote on which
step comes before which. The result carried a faint but real signal that never became statistically solid.
Reading the brain science on how people learn this kind of "usual order" from a few messy examples, three
things stand out. First, the brain does NOT take a plain majority vote: it replays each memory many times in
the background to manufacture far more practice examples than the handful it actually saw, it trusts clean
memories more than muddled ones instead of counting every example equally, and it tracks not just "what came
right after what" but "what tends to come somewhere after what," which lets it fill in orders it never saw
directly. Our majority-vote is a crude stand-in for all three. Second, and importantly, this background
"averaging" only cleans up RANDOM mistakes — if our reader makes the SAME mistake on every story (which is
likely, since one parser reads them all), no amount of averaging fixes it; only fixing the reading does.
Third, a dozen examples is far fewer than the brain uses. Our best read: the deepest problem is the messy
reading underneath (the same wall that caps everything else here), but our voting method is ALSO needlessly
crude and that part is cheap to fix. The recommended move is to build the brain's smarter averaging step —
weight clean stories more, track multi-step order, and manufacture extra practice examples — and run it while
increasing the number of example stories. If accuracy climbs, the voting was the fixable problem and the
reader is good enough. If it flatlines, that PROVES the reading itself is the wall — which is a real,
useful answer either way, at a fraction of the cost of rebuilding the reader first.

## QUESTIONS
None for the owner. One open DESIGN choice (solver's call, not a question): whether to build the full
denoiser (precision-weighting + SR-multistep + replay-augmentation) in one cell or ship precision-weighting
first as the cheapest single ablation. Recommendation: build all three as ARMS of one discriminator cell so
the scaling/ablation sweep answers "abstraction vs extraction" in a single run.

## NEXT STEPS
1. Build the consolidation-denoiser as a COMPOSITION cell: per-episode confidence (from the live
   `predict_surprisal` `pred_precision` + parse completeness) → precision-weighted, SR-style multi-step
   pairwise-precedence aggregator (optional generative-replay augmentation) → `transitive_ordering` premises
   → before/after read-out with episodic override.
2. Run it as a SCALING + ABLATION discriminator: episodes {12,30,60,120} × arms {equal-tally,
   precision-weighted, +SR-multistep, +replay-aug}; primary metric = DECIDED-subset accuracy and COVERAGE vs
   the random-order twin (twin must LOSE, CI-separated).
3. READ THE CURVE as the diagnosis: climbs → abstraction/power was the wall (real canonical-order organ,
   parser adequate); plateaus → SYSTEMATIC extraction bias PROVEN → rigorous negative that routes back to the
   parser-recall wall as the binding constraint for schema induction.
4. Land the proposed AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md §2b` (schema induction is a
   replay-driven, precision-weighted, multi-step distillation; our modal tally is a degenerate caricature).
