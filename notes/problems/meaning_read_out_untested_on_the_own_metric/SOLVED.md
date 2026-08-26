---
problem: meaning_read_out_untested_on_the_own_metric
status: PARTIAL
bar: "On the substrate's OWN meaning-assignment / grounding-precision instrument (same population and scorer as the 0.016-0.065 numbers above): a read-out (fusion of reading+grounded, and/or the taught direction), applied through the read-out path, must beat first-order co-occurrence COUNTING CI-separated over that floor's UPPER bound, with an information-free twin (shuffled grounding / random direction) LOSING."
result: "On the reproduced own-metric instrument (grounding precision vs data/conceptnet_gold_v1; 3 seeds; n=441/398/441 scorable grounded terms), TOP_COOC and SUBSTRATE reproduce the landed cell TO THE DIGIT (TOP_COOC 0.0476/0.0653/0.0590; SUBSTRATE 0.0159/0.0302/0.0272). THE BRIEF'S READ-OUTS LOSE TO COUNTING, CI-SEPARATED BELOW IT, ON EVERY SEED: FUSION 0.0068/0.0226/0.0091, taught-direction CHANNEL 0.0204/0.0101/0.0136, second-order READING 0.0091/0.0201/0.0227 -- all with paired (read-out - counting) CI excluding zero on the low side. The borrowed-scorer wins do NOT transfer. The strongest brain-foundational mechanism I could build -- frequency selects the top-K salient co-occurrents, the grounded hub picks the most sensorimotor-similar one (TOPK_GROUNDED) -- beats counting NUMERICALLY at every K in {5,10,15,20,30} (best pooled TOPK30_GROUNDED 0.0703 vs counting 0.0570, d=+0.0133) and beats its INFO-FREE (shuffled-grounding) twin CI-separated (pooled d=+0.027, CI [+0.014,+0.041]) -- but does NOT beat counting CI-separated even pooled at n=1280 (best d=+0.0133, CI [-0.0008,+0.0273], touches zero). No route tested clears the bar."
floor: "TOP_COOC = raw first-order co-occurrence COUNTING (argmax over the term's co-occurrents) = the landed TOP_COOCCURRENT, reproduced exactly: 0.0476/0.0653/0.0590, ci_hi 0.0680/0.0905/0.0816. It is the STRONGER counting floor: PMI-normalised counting (TOP_PPMI) collapses to 0.0045/0.0126/0.0045 (pooled 0.0070, ~8x worse), so the metric rewards raw FREQUENCY and any normalisation destroys the signal."
controls: "INFO-FREE TWINS ALL LOSE: shuffled-grounding fusion (FUSION_SHUFFLE_B ~= FUSION, so fusion's grounding adds nothing here); random-teacher taught direction (CHANNEL_RANDHUB_B ~0.00); random candidate / random vocab (~chance); shuffled-grounding TOPK (TOPK*_GROUNDED_SHUF 0.034-0.050, CI-separated BELOW the real TOPK*_GROUNDED at every K>=10). ORACLE CEILINGS (a gold neighbour is reachable among co-occurrents 0.46-0.50, in the vocab 0.80-0.83) prove the misses are RANKING failures, not coverage. The vectorized scorers reproduce the live organ APIs meaning_fusion.similarity_batch / distributional_meaning_channel.substitutability_batch to <3e-15 (asserted every run). Instrument reproduced to the digit vs the landed exp_grounding_precision_gold_v1."
files_changed: "experiments/exp_meaning_readout_own_metric_v1.py, experiments/exp_meaning_readout_own_metric_v1_ksweep.py, experiments/exp_meaning_readout_own_metric_v2_brainfaithful.py, experiments/exp_meaning_readout_own_metric_v3_discrimination.py, experiments/exp_meaning_readout_own_metric_v4_concreteness_control.py, experiments/exp_meaning_readout_own_metric_v5_concreteness_matched.py, verification/test_meaning_readout_own_metric.py, notes/problems/meaning_read_out_untested_on_the_own_metric/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_meaning_readout_own_metric.py"
INTEGRATED_BY_STRATEGY: "2026-08-25 (owner-DONE re-integration) -- EXCELLENT; top-1 re-verified PASS (read-outs lose -> no top-1 wiring); the owner-directed DISCRIMINATION reframe flips it (hard-negative COUNT 0.210 BELOW chance, GROUNDED 0.728 CI-separated, twin at chance) -> meaning organs carry real signal, 'they lose' is the frequency-dominated top-1 scorer; concreteness residual 0.648; discrimination not yet scaffold-witnessed (reverify covers top-1 only) -> lands via metric-fairness problem (priority 2)"
---

# What the brief asked, and the answer

Two meaning read-outs won on BORROWED scorers -- `meaning_fusion` (~0.45 WordSim relatedness) and
`distributional_meaning_channel` (~0.84 substitutability). The substrate's OWN metric (grounding
precision: for each grounded term, pick ONE anchor; hit = the anchor is a gold ConceptNet neighbour)
is where the stage is declared broken and where plain co-occurrence COUNTING beats the live rule 2-3x.
Nobody had scored the new read-outs there. **The answer is NO: the read-outs do not beat counting on
the own metric -- they lose to it, CI-separated, on every seed.** This answers the two decisions the
brief gates: (a) stage 2 is NOT fixed by these read-outs; (b) the wiring decision is NO -- do not wire
either read-out into the live reader for meaning assignment, because it loses to word-counting there.

This is the outcome the brief pre-registered as the valuable one ("it ties or loses counting on the
own metric -- then the borrowed-scorer wins do not fix the broken stage"). It is a clean **REFUTED of
the brief's INFERRED premise.** The status is PARTIAL, not REFUTED-alone, because I then went after
the underlying problem and found a real -- but sub-threshold -- brain-foundational signal (below).

# What I built and measured

I reproduced the own-metric instrument by re-reading with the SAME seeds and the SAME read loop as
`exp_grounding_precision_gold_v1` (grounded population reproduced EXACTLY: 572/490/571 grounded,
441/398/441 scorable; TOP_COOC and SUBSTRATE match the landed numbers to the digit). Each read-out is
applied "through the read-out path" two ways, the second being the more brain-faithful:
  * REGIME A -- re-rank the term's co-occurrent candidates (the exact pool counting argmaxes over).
  * REGIME B -- open-vocabulary nearest-concept retrieval over ALL stored concepts (a paradigmatic
    neighbour can win even if it never co-occurred). Both regimes lose to counting.

The vectorized scorers reproduce the live organ APIs to <3e-15 (asserted every run), so "through the
read-out path" is faithful, not an approximation.

**REFUTED of the brief:** FUSION 0.007-0.023, CHANNEL 0.010-0.020, second-order READING 0.009-0.023,
all CI-separated BELOW counting's 0.048-0.065. PMI-NORMALISED counting collapses to 0.004-0.013
(pooled 8x below raw count) -- direct evidence the metric is carried by RAW FREQUENCY, which every
"meaning" transform (SVD second-order, grounded fusion, substitutability) correctly de-emphasises and
thereby loses.

**The underlying problem, attempted (halfway-point mandate).** The diagnostic said: keep frequency,
add a meaning discriminator. The brain-foundational form -- frequency (salience) selects the top-K
co-occurrents, the grounded hub (cross-modal agreement) picks within them (TOPK_GROUNDED) -- is the
ONLY route that beats counting numerically, at EVERY K in {5,10,15,20,30}, and it beats its info-free
twin CI-separated (the grounded signal is REAL). But it never beats counting CI-separated, even pooled
at n=1280 (best d=+0.013, CI lower bound -0.0008, touching zero). Twenty variants swept
(K x {grounded, fusion, reading}); NONE clears. So the underlying problem is not solved to the bar,
but it is not a flat null either: there is a real, control-validated grounded re-rank that misses
significance by ~1 point.

# The wiring finding the brief did not anticipate

The live ROUTE B co-occurrence store (`ConceptSpace.observe_context_counts`) fires ONLY for
seed-vocabulary lemmas -- it covers **0 of the 441 grounded terms** the own metric scores. So the
read-outs as wired have NO representation for the very terms this task is about; I had to build them
from the full first-order co-occurrence store (the same store the counting floor uses) to score them
at all. Any future attempt to apply these organs to grounding precision must first extend the store to
grounded terms.

# What I did NOT establish / would withdraw first

- **Withdraw first if wrong:** that TOPK_GROUNDED beats counting NUMERICALLY. It is a +0.9-to-+1.3
  point pooled effect whose CI touches zero; a different seed set could flip its sign. What is robust
  and would survive: the read-outs LOSE to counting (CI-separated), and TOPK_GROUNDED beats its
  info-free twin (CI-separated).
- I did NOT test a directional operator for asymmetric relations (distributional inclusion / Hearst)
  or a syntactic-frame-conditioned read-out. The scorer unions both gold edge directions into the
  neighbour set, so direction does not affect scoring, which lowered the prior on these; they remain
  untested routes.
- I did NOT establish that MORE POWER would let TOPK_GROUNDED clear. To move its paired CI off zero
  needs ~2.3x the data, and even then it would clear only the PAIRED test, never the brief's STRICT
  upper-bound gate (which needs a ~+3-point margin an effect this small cannot reach).

# KEY REALIZATIONS

1. **THE OWN METRIC IS FREQUENCY-DOMINATED, AND THAT IS WHY EVERY MEANING TRANSFORM LOSES.** Raw
   counting 0.057 vs PMI-normalised counting 0.007 (pooled): removing the frequency confound -- the
   textbook first step toward "meaning" -- makes the score 8x WORSE. The metric rewards syntagmatic
   frequency; the read-outs compute paradigmatic similarity, which is near-orthogonal to it. The
   borrowed-scorer wins are on PAIRWISE tasks (rank-correlation / AUC over given pairs); the own metric
   is TOP-1 RETRIEVAL over hundreds of candidates -- a different, harder task where frequency is a
   strong baseline. The measurement that made this credible was adding TOP_PPMI as a second floor.
2. **A RELIABLE COUNT (THE ORACLE CEILING) SEPARATED "COVERAGE" FROM "RANKING".** The gold neighbour is
   reachable among the co-occurrents ~48% of the time (in vocab ~80%), while counting lands it ~6% and
   the read-outs ~2%. So this is a RANKING failure with large headroom, not a coverage failure -- which
   is what licensed the mechanism-building attempt instead of giving up.
3. **THE INFO-FREE TWIN IS WHAT MAKES THE SMALL SIGNAL INTERPRETABLE.** TOPK_GROUNDED beats counting by
   a whisker (not CI-separated) but beats its shuffled-grounding twin CI-separated. Without the twin,
   the +1-point effect would be dismissible noise; with it, we know the grounded hub carries REAL
   signal for picking the anchor -- just not enough to overtake raw frequency.
4. **THE LIVE READ-OUT WIRING HAD ZERO COVERAGE OF THE SCORED TERMS.** Checking WHAT the store contains
   (seed vocab) vs WHAT the task scores (grounded terms) -- coverage 0/441 -- caught that the read-outs
   could not even address the task as wired, before any ranking question. Read what the resource
   covers, not just what it scores.

# TLDR (plain language)

We tested whether the two new "meaning" tools actually beat plain word-counting at the substrate's own
broken job: guessing the right related word for a term it just read. They do NOT -- they lose to
word-counting, clearly and repeatably, and our reproduction of the counting score matches the old
measurement exactly, so the test is trustworthy. The reason is that this particular scoring rewards
"which word showed up nearby most often," and the meaning tools deliberately look past raw frequency,
which is the very thing that wins here (when we strip frequency out with the standard normalisation,
the score gets 8x worse). So the borrowed-test wins do not fix the broken step, and we should NOT wire
these tools into the reader for this job. Chasing the problem further, the most brain-like recipe we
could build -- let frequency pick the handful of most-salient nearby words, then let the "hands-on
feel" sense pick the best of those -- does edge past counting and clearly beats a scrambled-sense
control, but the edge is too small to call a real win. Net: the tools don't fix it; there's a faint
real signal in the right direction; and, separately, we found the tools' live memory doesn't even
store the words this task asks about.

# QUESTIONS

None.

# NEXT STEPS (for the strategy session; you own hdlab + integration, board Q111)

1. **Re-verify:** `.venv/Scripts/python.exe verification/test_meaning_readout_own_metric.py` (recomputes
   the headline from saved data and re-confirms the instrument reproduces the landed cell).
2. **Do NOT wire the read-outs into the reader for meaning assignment** -- they lose to counting here.
   The WordSim/substitutability wins stand on their own instruments; they do not transfer to grounding
   precision.
3. **Reconsider the own metric as an "understanding" instrument.** A task where raw frequency beats
   every meaning-aware method and normalisation makes it 8x worse is measuring association-frequency,
   not conceptual integration. This is a strategic question about the instrument, above the solver's
   remit -- but it is the single most important thing this result surfaces.
4. **If the grounded re-rank direction is judged worth it:** the mechanism is TOPK_GROUNDED (frequency
   selects top-K salient co-occurrents; grounded hub picks within them). It beats its info-free twin
   CI-separated but misses counting by ~1 point; it would need ~2.3x reading to test paired
   significance and still would not clear the strict upper-bound bar. Proposed hdlab change IF pursued:
   (a) extend `ConceptSpace.observe_context_counts` to accumulate for GROUNDED terms, not just seed
   vocab (today it covers 0/441 of the scored terms); (b) add a meaning-assignment read that restricts
   to the top-K frequent co-occurrents and ranks by grounded-hub similarity. Neither should land until
   the effect clears a bar.

# ADDENDUM (post-integration, 2026-08-25): a BRAIN-FOUNDATIONAL alternative that DIFFERS from the brief -- score DISCRIMINATION, not top-1

Owner asked to test brain-foundational routes that DIFFER from the brief's frame and report what they
mean / how they perform / what they require. The brief scores TOP-1 RETRIEVAL (precision@1: is the
single argmax anchor a gold neighbour?). But the ATL semantic hub -- and these read-outs -- do NOT
emit a single argmax; they emit a GRADED similarity, and their proven wins (WordSim, substitutability)
are DISCRIMINATION tasks. So I scored the SAME ConceptNet gold as a relatedness AUC (rank gold
neighbours above non-neighbours). **This is a DIFFERENT SCORER; its AUC does NOT cross to the top-1
precision above.** Cell: `experiments/exp_meaning_readout_own_metric_v3_discrimination.py`.

**HOW IT PERFORMS (pooled 3 seeds; matched to grounded-covered pairs so no number crosses populations):**
- RANDOM negatives (random non-neighbours): COUNT 0.641, READING 0.719, GROUNDED 0.760, FUSION 0.804.
  Every read-out beats counting CI-separated; info-free grounded twin at chance (0.488).
- HARD negatives (co-occurring NON-neighbours, matched on co-occurrence -- "tell the gold neighbour
  from a mere co-occurrent"; counting is stripped of its frequency advantage): **COUNT 0.210
  (BELOW chance -- it ACTIVELY PREFERS co-occurrents over gold neighbours), READING 0.352 (below
  chance -- the distributional spoke partly tracks co-occurrence), GROUNDED 0.728 (well above chance),
  FUSION 0.589.** GROUNDED and FUSION beat COUNT CI-separated; the info-free grounded twin is at chance
  (0.489), so the 0.728 is REAL grounded meaning, not a bias.

**WHAT IT MEANS.** The read-outs DO capture the meaning step's core competence -- distinguishing a true
conceptual neighbour from a mere co-occurrent -- which is exactly what co-occurrence CANNOT do (counting
is anti-correlated, 0.21, on the hard task). The brief's TOP-1 metric could not see this because its
argmax is dominated by frequency. So the "read-outs lose" headline is a property of the SCORER, not of
the read-outs: on the brain-faithful discrimination scorer they win decisively. Two further findings:
(1) the GROUNDED (sensorimotor) spoke carries the meaning signal (0.73); the READING (distributional)
spoke does NOT on hard negatives (0.35, below chance) -- it is a co-occurrence proxy. (2) EQUAL-WEIGHT
FUSION IS SUBOPTIMAL: averaging good grounded (0.73) with bad reading (0.35) yields diluted fusion
(0.59). For meaning-vs-association discrimination, grounded-WEIGHTED (or grounded-alone) beats fusion.

**WHAT IT REQUIRES TO FUNCTION PROPERLY.** (a) Score meaning assignment as RANKING/DISCRIMINATION (does
it rank real neighbours above co-occurrents?), not top-1 argmax over a frequency-rich pool. (b) Weight
the GROUNDED spoke heavily (or use it alone) for the real-neighbour-vs-co-occurrent decision -- equal
weight dilutes it; this is a licensed re-weighting of `meaning_fusion`, swept not adopted. (c) The
grounded discrimination only applies where sensorimotor norms cover BOTH words (~55-75% of pairs);
outside that, there is currently no meaning signal that beats counting. (d) If the distributional spoke
is used at all, extend the store to grounded terms (the 0/441 wiring gap).

**CONCRETENESS CONTROL (run 2026-08-25; cells v4 + v5) -- the caveat is now CLOSED, and it MATTERS.**
The grounded 0.73 is LARGELY a concreteness effect: concreteness-alone (the 1 Brysbaert dim) scores
AUC 0.706 on the hard task, ~= the full 0.726 (v4). But it is not ONLY concreteness. On
concreteness-MATCHED hard negatives (each positive paired with a co-occurring non-neighbour of nearly
identical concreteness; mean gap 0.018 z-units), a RESIDUAL sensorimotor-meaning signal SURVIVES:
  GROUNDED (11 sensorimotor dims, concreteness removed) AUC=0.648 [0.639,0.658] -- above chance;
  READING (distributional spoke) AUC=0.360 -- does NOT survive (carries nothing beyond concreteness);
  COUNT 0.207 (still anti-correlated); CONC_ONLY 0.502 (match confirmed); info-free twin 0.486 (chance).
So the honest, fully-controlled statement: the GROUNDED SENSORIMOTOR spoke carries a GENUINE but MODEST
conceptual-meaning signal (~0.65) that co-occurrence and the distributional spoke cannot; roughly half
of the raw 0.73 was a concreteness/imageability confound (itself a real semantic dimension, but coarse).

**WHAT I WOULD WITHDRAW FIRST / did NOT establish.** The discrimination AUC is NOT the brief's scorer,
so it does not overturn the top-1 result -- it reframes what the top-1 result means. And the residual
sensorimotor signal, while robust (0.648, twin at chance), is modest -- do not claim the grounded spoke
"solves" meaning; claim it carries real conceptual signal that frequency and distribution do not.

**BRAIN-FIDELITY AUDIT (drill 2026-08-25) -- the findings above are what pinned mechanisms PREDICT.**
An independent mechanism-fidelity drill (ATL hub; Lambon Ralph/Rogers/Chen; Jefferies semantic control;
Kutas/Federmeier N400; Connell/Lynott sensorimotor norms; Rogers/Plaut attractor cleanup) audited the
four load-bearing choices:
1. HUB INTEGRATION. PINNED: ATL integration is NON-LINEAR and CONTROL-GATED, with a LEARNED, graded,
   task-dependent spoke weight (semantic-control network, L-IFG/pMTG, up-weights the task-relevant
   spoke). OUR-INVENTION: our fixed equal-weight ADDITIVE z-fusion -- the largest fidelity divergence.
   The measured dilution (fused 0.59 sits BETWEEN grounded 0.73 and reading 0.35) is the signature of an
   additive average with a bad summand; "weight grounded more for concrete concepts" is the pinned
   prediction (concrete concepts are sensorimotor-carried, low semantic diversity), NOT a task artifact.
2. READ-OUT FORM. PINNED: the meaning read-out is GRADED goodness-of-fit (the N400 scales continuously
   with semantic fit); winner-take-all is a LATER downstream decision. So GRADED DISCRIMINATION (AUC) is
   the brain-faithful scorer and TOP-1 ARGMAX is the artifact -- it scores a downstream stage where raw
   frequency dominates. This is independent theory support for the whole reframe.
3. GROUNDED SPOKE. PINNED: sensorimotor strength predicts word processing BETTER than concreteness
   (Connell & Lynott 2012); concreteness is a half-confound (imageability/context-availability). The
   drill PREDICTED concreteness-only should underperform the full sensorimotor spoke -- which the v5
   control confirms. Use the 11 sensorimotor dims as content; treat concreteness as a GATING signal, not
   a representational dimension.
4. SELECTION. PINNED: meaning assignment is ATTRACTOR CLEANUP onto a STORED-CONCEPT inventory (Rogers
   2004; Plaut & Shallice; Chen 2017), NOT argmax over raw co-occurrents -- which structurally removes
   the frequency-wins problem (co-occurrents are not attractors; cleanup is similarity- not
   frequency-driven). OUR-INVENTION: our argmax over raw co-occurrents. NOTE: a WEAKER form of this
   (restrict candidates to grounded concepts, pick by grounded sim; cells v2) was already tested and did
   NOT beat counting on top-1 -- so the full attractor-cleanup build is a real NEXT experiment with a
   modest prior, not a settled win.
The forward mechanisms (control-gated graded gain on the two spokes; graded scorer with a swept
decision-temperature; stored-inventory attractor cleanup) are hdlab BUILDS and belong to the strategy
session; they are refinements of an established finding, not blockers on this result.
