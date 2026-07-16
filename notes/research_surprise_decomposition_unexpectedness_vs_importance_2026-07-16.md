# Research: is SURPRISE one axis or two? (unexpectedness vs. importance/salience/value)

Director deep drill, 2026-07-16. Companion to the parallel omnibus drill
`research_consolidation_gate_quantitative_signals_2026-07-16.md` (which quantified the 3-signal ingest
gate — surprise/schema-fit/recurrence — and its combination rule). That drill is NOT redone here. This
drill goes one level deeper into ONLY the surprise axis, because the omnibus's "surprise" input
(`raw_PE = 1 - reciprocal_rank`) was taken as a single scalar — this drill asks whether that scalar is
secretly conflating two different biological/computational quantities, and if so, what the substrate is
missing. Four parallel Sonnet lit-scans (dissociation evidence generally; neural circuits that gate
consolidation specifically; formal value-of-information/free-energy treatments; the threat/stakes
"rock falling on your head" case) + director synthesis. Research-only: no code, no cell dispatched.
Generic biology/psychology/math terms only in all external queries.

## HEADLINE

**Surprise is two things, and the literature's support for this is unusually strong and convergent
across four independent angles — but the two things are NOT "prediction-error" and "importance" in a
clean symmetric sense. They are better described as (1) a REALIZED, backward-looking, single-observation
belief-shift (Bayesian surprise, `KL(P(M|D)||P(M))`, Itti & Baldi) and (2) a computed-independently
STAKES/RELEVANCE signal that in biology is supplied by dedicated reward/threat/goal machinery with NO
statistical-improbability content of its own** (unsigned dopaminergic salience neurons that fire equally
for good and bad outcomes of the same magnitude; amygdala-noradrenergic arousal tagging; looming/collision
geometry detectors; evolutionarily prepared fear categories) — none of which compute anything like `-log p`
or KL-divergence. The cleanest single piece of evidence is a genuine double dissociation at the level of
single neurons: Matsumoto & Hikosaka (2009, *Nature*) and Bromberg-Martin et al. (2010, *Neuron*) show two
anatomically distinct dopamine populations — "motivational value" neurons (signed, magnitude-scaled,
excited by good/inhibited by bad) and "motivational salience" neurons (unsigned, excited by BOTH good and
bad outcomes of comparable size) — meaning the brain literally has separate wiring for "was this better
or worse than expected" and "how much does this matter regardless of sign." **This directly answers the
prompt's rock-on-head intuition: threat computation (looming/collision-timing neurons, LGMD, superior
colliculus) is a GEOMETRIC/CONSEQUENCE computation, structurally incapable of being expressed as a
probability term at all — it is not "a bigger prediction error," it is a different variable entirely.**
The honest complication: HOW the two signals combine (additively vs. multiplicatively vs. as separate
inputs) is NOT settled in the literature — one direct test found additive/independent combination
(arousal x reward-anticipation, no interaction); another circuit (locus coeruleus) shows the same
physically-identical stimulus producing a bigger response when it is also aversive-associated, which
looks interactive/multiplicative. **This is the identical shape of gap the omnibus drill found for
schema-fit x surprise** (form is derivable in pieces, no single paper states the combination law) — now
confirmed a second time, one level up the stack, for salience x surprise. Deflated per calibration
discipline throughout.

## THE DECOMPOSITION (deliverable 1)

**(a) Unexpectedness — the cleanest formal statement.**
Shannon self-information `h(y) = -log p(y)` is a *data-space* quantity: it depends only on how improbable
the observed datum is, integrated over the space of possible data. This is what white noise maximizes —
every outcome of a maximum-entropy source is equally "surprising" in this sense, forever, with no decay.
**Bayesian surprise** (Itti & Baldi 2005/2006/2009, *Vision Research* 49:1295-1306; PMC2782645) is instead
a *model-space* quantity: `S(D,M) = KL(P(M|D) || P(M))` — the divergence between your posterior and prior
over a space of hypotheses/models, after observing D. The paper's own worked example is exactly the
prompt's pathology case: television static ("snow") carries far MORE Shannon information per second than
normal broadcast content, yet produces roughly 17x LESS Bayesian surprise, because if a datum is equally
improbable under every hypothesis (`P(D|M_i) = epsilon` for all i), Bayes' rule gives `P(M_i|D) = P(M_i)`
— the posterior equals the prior, so `KL = 0` regardless of how tiny epsilon is. Bayesian surprise is
therefore self-correcting against the "white noise problem" the prompt names — but only against noise
that is *globally uninformative about every live hypothesis*; it is not a full solution to what should
be memorable (see below).

**(b) Salience/importance/value — the cleanest formal statement, and why it is NOT reducible to (a).**
The strongest formal analog is **Friston's Expected Free Energy epistemic/pragmatic split** (Friston et
al. 2015; Da Costa et al. 2020): EFE decomposes additively into an **epistemic value** term (expected
information gain — this is where Bayesian surprise/"salience" lives, at the level of hidden STATES) and a
**pragmatic value** term (expected log-preference/reward-achievement — goal-conduciveness, NOT
information-theoretic at all). A further split inside epistemic value distinguishes state-level
information gain ("salience," ≈ Bayesian surprise) from parameter-level information gain ("novelty," ≈
learning-about-world-structure, formally close to Schmidhuber's learning-progress, below). The pragmatic
term is the closest formal analog of "importance/value/stakes," and it is explicitly NOT a KL divergence
or any information-theoretic quantity — it is expected achievement of a **preference/goal**, a separately
specified quantity with its own generative model. This is the formal reason the two are not reducible:
one is a statement about BELIEF CHANGE, the other is a statement about GOAL ACHIEVEMENT, and nothing
forces them to covary (you can have huge belief-change with zero goal-relevance — abstract trivia — and
zero belief-change with huge goal-relevance — a fully expected but life-threatening event recurring for
the hundredth time).

**(c) Are these neurally separable? Yes — this is the best-evidenced part of the whole drill.**
Three independent, convergent lines of neural dissociation:
- **Dopamine sub-populations** (Matsumoto & Hikosaka 2009, *Nature* 459:837; Bromberg-Martin, Matsumoto &
  Hikosaka 2010, *Neuron* 68:815, PMC3032992): "motivational value" neurons (signed, value/magnitude-
  scaled, standard Schultz-style RPE) vs. "motivational salience" neurons (unsigned, fire for both good and
  bad outcomes of comparable magnitude — a pure "how much does this matter" signal, blind to sign, and
  computed by anatomically distinct cells). Even within a single dopamine neuron's response, Schultz's
  two-component model shows an early, brief, UNSELECTIVE burst (salience-like) followed by a later,
  value-scaled component (Nature Reviews Neuroscience 2016 review) — i.e., the two computations are
  temporally as well as anatomically separable.
- **Unsigned vs. signed prediction-error and MEMORY, directly** (Rouhani, Norman & Niv 2018, *JEP:LMC*
  44:1430, PMC6117220; Rouhani & Niv 2021, *eLife* 10:e61077): unsigned PE (surprise magnitude) enhances
  memory for OUTCOME events via a proposed LC-noradrenergic route, is constant across learning, and
  targets a different memory type than signed PE (value/direction), which enhances memory for PREDICTIVE
  CUES via a proposed dopaminergic route and grows as learning progresses. These are primary, quantitative,
  directly-on-point dissociations — the single strongest citations in this drill.
- **ERP components**: novelty-P3a (frontal, automatic orienting to any deviant, habituates rapidly with
  repetition regardless of task relevance) is dissociable from target/relevance-P3b (parietal, requires
  goal/task relevance, correlates with subsequent memory) — Polich 2007, *Clin Neurophysiol* 118:2128,
  PMC2715154, a heavily-replicated integrative review.

**(d) Appraisal-theory consensus (the psychological-level convergence).** Scherer's Component Process
Model explicitly sequences "novelty" and "goal/need relevance" (later, "goal conduciveness/consequence")
as SEPARATE, independently-evaluated appraisal checks within ~600-800ms (Scherer, *Annu Rev Psychol* 2019).
Lazarus's older model similarly separates primary appraisal ("what's at stake," a pure relevance/stakes
computation requiring no novelty at all) from secondary appraisal (coping, closer to expectancy). This is
the dominant framing in that literature, not a fringe view.

**Verdict on deliverable 1: YES, cleanly separable, both formally (KL-divergence over beliefs vs.
expected-preference-achievement over goals) and neurally (distinct dopamine populations, distinct ERP
generators, distinct proposed neuromodulators). Deflated confidence: P=0.68** (undeflated ~0.85 given how
convergent the evidence is across independent circuits/paradigms; deflated for the fact that no single
study performs the fully orthogonalized test within one paradigm — see gap below).

## NEURAL IMPLEMENTATION — which surprises get consolidated (deliverable 2)

**The hippocampal-VTA loop is NOT a pure-novelty gate — the model itself says so.** Lisman & Grace (2005,
*Neuron* 46:703) propose CA1 mismatch-detection (a genuine unexpectedness computation, CA3-predicted vs.
entorhinal-actual) feeds forward to VTA via subiculum -> accumbens -> ventral pallidum, but the paper's own
text states the VTA's downward arm "combines novelty signals with information about salience and goals"
before dopamine is released — i.e., the anatomically-final gate to hippocampal LTP is already, in the
original model, a CONFLUENCE node, not a raw-surprise readout. Duszkiewicz, McNamara, Takeuchi & Genzel
(2019, *Trends Neurosci* 42:102, PMC6352318) refine this into two dissociable systems: **VTA responds to
"common novelty"** (new configuration of familiar/schema-related elements) and promotes SEMANTIC,
schema-integrated consolidation; **locus coeruleus responds to "distinct novelty"** (little relation to
prior experience, closer to a general arousal/salience signal) and drives strong initial encoding of
vivid but less schema-integrated episodic traces. Bunzeck & Düzel (2006, *Neuron* 51:369) independently
show SN/VTA novelty coding is "absolute" (non-value-adaptive), explicitly contrasted with reward coding —
a genuine within-dopamine-system dissociation between a novelty channel and a value channel.

**Synaptic tagging and capture is architecturally a two-component system, and this is the load-bearing
mechanistic evidence for "surprise sets a local tag; something else (importance) captures it."** Frey &
Morris (1997, *Nature* 385:533): weak stimulation sets a transient (1-3h), protein-synthesis-independent
"tag" at a synapse; whether that tag converts to lasting late-LTP depends on plasticity-related proteins
(PRPs) synthesized ELSEWHERE, in response to a SEPARATE strong/salient event. Behavioral tagging (Moncada
& Viola 2007, *J Neurosci* 27:7476; Ballarini et al. 2009, *PNAS* 106:14599) extends this to the systems
level: a weak, otherwise-forgotten memory is rescued into long-term storage by an unrelated novel
experience occurring in a bounded time window, and this rescue is dopamine-D1/D5-receptor-dependent. This
is a clean instance of the local-tag/global-capture split the prompt is asking about, and it has THREE
documented floors that matter for "what gets discarded despite being unexpected":
1. **Zero-engagement floor**: novelty cannot rescue training so weak it fails to set any local tag at
   all — there is nothing for the systemic dopamine signal to capture onto.
2. **Cross-region floor**: novelty in one circuit cannot rescue a weak tag in an unrelated circuit — the
   capture signal must reach the SAME synapses/region where the tag was set, not a generic broadcast.
3. **Temporal-window floor**: the novelty event must fall in a bounded window relative to the weak
   training (tag decay ~1-3h, matching Frey & Morris), not "any time, any distance."

**Which surprises get discarded despite being unexpected — supported indirectly, not by one clean
study (an honest gap).** Best indirect evidence: (i) novelty-P3a habituates rapidly with repetition
regardless of task/goal relevance — the pure-surprise signal is transient and decaying, unlike consolidated
memory strength; (ii) Reichardt et al. (2022, PMID 35390179) failed to replicate that merely EXPECTING an
otherwise-irrelevant novel stimulus boosts its later recognition memory, complicating any simple
"surprise alone suffices" story; (iii) the behavioral-tagging floors above show a systemic
importance/novelty signal cannot manufacture a durable trace from a training event with zero local
engagement. **Genuine complication that must be flagged honestly**: the Von Restorff / distinctiveness
effect (a well-established list-learning finding) shows purely PERCEPTUAL oddity — no emotional or
motivational content whatsoever — reliably boosts memory, which pushes back against a strong version of
"meaningless surprise is never kept." The honest resolution is probably that distinctiveness effects
operate over SHORT time-scales / immediate recall (attention capture, matching Talmi's 2013 "immediate
effects are attention/distinctiveness-mediated") while true systems-level CONSOLIDATION into durable
long-term/cortical memory is where the importance-gated mechanisms (BLA-noradrenergic, dopamine-dependent
late-LTP/PRP-capture) do their differentiating work — i.e. distinctiveness gets you noticed and briefly
remembered; only additionally-salient/important material gets systems-consolidated. No single study
directly confirms this resolution — flag as director synthesis, not a cited finding.

## STRUCTURAL VERDICT (deliverable 3)

**Best-supported answer: importance/salience is an architecturally SEPARATE signal (not a mathematical
transform of surprise), but the field has NOT settled on one universal combination rule with surprise —
the empirical record shows BOTH additive and interactive patterns depending on which circuit is examined.**

Evidence for "separate, not reducible":
- The unsigned-salience dopamine population (finding above) fires identically for equally-sized good and
  bad outcomes — if importance were just "bigger PE," a value/magnitude-scaled account alone would
  suffice; the existence of a sign-blind population is direct evidence importance has its own computation.
- Looming/collision-timing neurons (superior colliculus rho/eta cells, cat; human SC-pulvinar-VTA
  pathway; insect LGMD/DCMD) compute a GEOMETRIC variable (time-to-collision, retinal expansion rate) that
  has no probability content at all — you cannot express "the object will hit you in 200ms" as a KL
  divergence over anything. This is the cleanest possible answer to the rock-on-head intuition: the
  "surprising in a different sense" IS a different variable, not a bigger number of the same variable.
- Öhman & Mineka's prepared-fear literature: evolutionarily-relevant threat categories (snakes, spiders)
  produce stronger, more extinction-resistant fear learning than novelty-matched fear-irrelevant stimuli
  (flowers, outlets) — stakes tracks a fixed evolutionary category membership, not the observer's own
  exposure statistics.

Evidence on HOW they combine (genuinely mixed, an honest open question):
- One directly-designed fMRI test (arousal vs. reward-anticipation, PMID 36205480) found **no
  interaction** — the two routes acted additively/independently on episodic memory formation.
- Bouret & Sara's locus coeruleus work shows the identical physical stimulus produces a LARGER phasic LC
  response when it is aversive-associated than when neutral — i.e., the same "surprise" input is
  amplified by importance, which looks multiplicative/interactive, not additive.
- Lisman & Grace's own VTA model describes novelty and salience/goal information as being "combined,"
  without specifying the arithmetic form.

**This is structurally the identical open question the omnibus drill found for schema-fit x surprise (no
paper states the combination law; form is derivable in pieces from adjacent formalisms) — now independently
confirmed one level up, for salience x surprise.** Two confirmed gaps of the same shape, from two
independent drills using different literatures, is itself informative: it suggests this is a genuine,
structural absence in the consolidation literature (not a search-query artifact), and that ANY concrete
combination rule the substrate adopts for either pairing is going to be novel synthesis requiring its own
empirical validation on this substrate, not an importable constant.

**Deflated confidence: P(surprise and salience/importance are genuinely separate, not reducible) = 0.65**
(undeflated ~0.80 — the dopamine double-dissociation and looming-geometry evidence are about as clean as
neuroscience dissociation evidence gets, but deflated because no single orthogonalized paradigm tests all
of surprise-magnitude x salience-magnitude x memory-outcome at once). **P(the combination is
multiplicative specifically, as opposed to additive-independent or gated/thresholded) = 0.30** (genuinely
contested; the one direct clean test found additive, one circuit-level finding suggests interactive — this
is capped low deliberately, novel-synthesis territory).

## THE VALUE-OF-INFORMATION ANGLE (deliverable 4)

**Yes — there is a formal chain connecting local surprise to a genuinely distinct "does this matter
elsewhere" quantity, and it directly targets the prompt's pathology concern.** Lindley's (1956) Expected
Information Gain is the EXPECTATION of a Bayesian-surprise-like KL divergence, taken over the distribution
of not-yet-observed future outcomes — i.e. "how much would I expect to learn," a forward-looking quantity,
versus Bayesian surprise's backward-looking "how much did I just learn." Howard's (1966) Value of
Information goes further and folds in DOWNSTREAM DECISION PAYOFF explicitly — value is defined relative to
how much observing the datum changes the EXPECTED UTILITY of subsequent decisions, not just beliefs.
Friston's Expected Free Energy formalizes essentially the same idea inside active inference: epistemic
value (parameter-level, "novelty") is expected information gain about the STRUCTURE of the world (as
opposed to state-level "salience," which is closer to plain Bayesian surprise), and this parameter-level
term is formally close to **Schmidhuber's learning progress / compression progress** (1991-2010): "interest"
is defined as the derivative of subjective compressibility, `I(D,O,t) = B(D,O(t)) - B(D,O(t-1))`. This is
the single most directly relevant formal answer to the prompt's pathology: learning progress is ZERO for
already-fully-predictable data (no further compression possible) AND ZERO for pure incompressible noise
(it never becomes more compressible, however long you watch it) and POSITIVE ONLY for learnable-but-not-
yet-learned structure. This is explicitly named in the literature as the fix for the "noisy-TV problem" —
raw prediction-error curiosity gets trapped forever attending to unlearnable randomness; learning-progress
does not, because progress requires actual improvement in compression, which noise structurally cannot
provide. This is a MORE COMPLETE answer to the prompt's pathology than Bayesian surprise alone: Bayesian
surprise already solves the "equally-improbable-under-every-hypothesis" case (posterior=prior, KL=0), but
it does NOT by itself solve the case of a genuinely-informative-but-never-useful-again idiosyncratic
one-off (a real belief update that nonetheless has zero recurring value) — learning-progress additionally
requires that the belief update be part of a LEARNABLE, recurring regularity, which is a stronger and more
useful filter.

**Confirmed gap, found independently a second time (once by the omnibus drill for schema-fit, now by this
drill for value-of-information/EFE/learning-progress): no paper explicitly proposes that memory
consolidation should be gated by expected-downstream-model-change / value-of-information rather than by
local surprise.** The active-inference and curiosity/exploration literatures are mature on attention and
exploration; the memory-consolidation literature independently converges on prediction-error/salience/
reward language; the two have not been formally unified in what was found. The closest adjacent material
is Gershman's resource-rational memory framework (memory as reward/utility-driven strategic allocation,
not passive salience response) and the state-vs-parameter split inside EFE — both are the right raw
material for this unification but neither states it directly. This is a genuine, repeatedly-confirmed
absence, not a search-term artifact (two independent lit-scan angles across two drills both came back
empty on the same specific claim).

**Does the brain approximate this?** Partially, and only crudely. Bunzeck & Düzel's finding that SN/VTA
novelty coding is "absolute" (non-value-adaptive, i.e. does NOT rescale with how often the novel category
has recurred) is actually evidence AGAINST a clean learning-progress implementation at that specific
node — a true learning-progress signal should habituate as a regularity becomes learnable/learned, and
"absolute" coding is closer to raw Bayesian surprise than to compression-progress. The clearest
brain-side analog of learning-progress-like gating is instead the SCHEMA-formation timeline itself (Tse et
al., cited extensively in the omnibus drill): rapid one-trial learning for schema-CONSISTENT material
(the schema has already "compressed" that regularity, so a new instance costs almost nothing) versus
~13-session/1-month schema-BUILDING (the regularity is not yet compressed, so integrating it costs a lot)
— this IS structurally a learning-progress/compression story, just not framed that way in the schema
literature. **P(the brain implements something functionally equivalent to learning-progress/EFE-epistemic-
value for consolidation gating, even if not via that exact math) = 0.45** (novel synthesis across two
independently-confirmed-absent literatures; capped per calibration discipline).

## SUBSTRATE MAPPING — the crux (deliverable 5)

An organism's "importance" ultimately bottoms out in survival/reproduction stakes, instantiated
concretely via reward/threat circuitry with NO probability content (unsigned salience dopamine, BLA-
noradrenergic arousal tagging, looming-geometry detectors, evolutionarily-fixed threat categories). A
knowledge substrate has none of this — there is no organism, no body, no death, no reward loop tied to
survival. The literature above, taken as a whole, points to **two distinct legitimate substitutes**,
mapping onto the two things biology keeps architecturally separate:

1. **Analog of the EXTERNAL/stakes-supplied signal (BLA arousal tagging, value-directed-remembering's
   cued point-values, P3b task-relevance, Lisman-Grace's "goal information" input):** something outside
   the substrate's own belief-update math has to supply this — a designer-set value function, an explicit
   query/task-relevance weighting, or a downstream consumer's stated priority. This is legitimate (biology
   itself gets its stakes from an external-to-the-belief-system source — the reward/threat machinery is a
   SEPARATE system from the cortical/hippocampal belief-updating machinery) but it is inescapably
   EXOGENOUS: no computation over the substrate's own graph alone can manufacture genuine stakes, exactly
   as no amount of cortical prediction-error computation manufactures a threat signal without amygdala/
   dopamine circuitry attached.

2. **Analog of the INTRINSIC, no-stakes-required signal (EFE's parameter-level epistemic value / novelty,
   Schmidhuber's learning progress, Lindley's expected information gain):** this one is fully computable
   from the substrate's OWN model/graph, with no external reward analog needed, because it is defined
   purely in terms of expected belief-change ELSEWHERE in the model, not in terms of goal-achievement.
   Concretely: how much would correctly integrating this candidate fact change OTHER predictions across
   the rest of the knowledge graph (its downstream inferential reach), versus how much it merely updates
   belief about itself in isolation. This is the more substrate-native, no-stakes-required answer, and it
   is the one this drill flags as the missing piece: **hub-centrality / downstream-reach of the candidate
   fact's entities in the current graph is a legitimate, computable, zero-external-input proxy for
   "importance," distinct in kind from schema-fit (which asks "does this fit a known structural pattern")
   and distinct from raw surprise (which asks "did this update my belief about itself").**

**What fails if raw unexpectedness (surprise alone) is used without either substitute**: exactly the
prompt's pathology, now sharpened by this drill's formal chain. Bayesian surprise alone handles the
purest case (data equally likely under every live hypothesis -> KL=0, a global-noise event correctly
produces zero surprise) but does NOT by itself filter a genuinely-informative, real-belief-shifting,
NEVER-RECURRING idiosyncratic one-off with zero downstream reach — that candidate can score high raw_PE,
pass a reasonable schema_fit check (it might even structurally resemble known patterns), and still be
worthless to consolidate because nothing else in the graph depends on it and it will never recur. Neither
surprise nor schema-fit (as currently specified in the omnibus drill) computes this; recurrence (the third
omnibus signal) partially guards against it (a true one-off has recurrence_count=1, held at low local
precision) but recurrence-as-precision is a NOISE-CONTROL heuristic, not a value/stakes computation — a
fact that recurs often but changes nothing downstream would still pass recurrence-gating despite being
low-value, and a fact that recurs only once but sits at a genuine structural hub (high downstream reach)
would be wrongly held back by recurrence alone.

**Structural implication for the substrate's ingest gate (explicitly flagged as an addendum, not a
redesign of the omnibus's already-derived 3-signal architecture):** this drill's findings suggest a
genuine 4TH candidate input — downstream-reach/hub-centrality as a value-of-information proxy — sits at a
different conceptual layer than any of the omnibus's three signals (surprise=belief-change-at-self,
schema_fit=structural-congruence, recurrence=precision-from-repetition). It is NOT a redundant relabeling
of schema_fit: schema_fit asks "does this fit a KNOWN PATTERN," downstream-reach asks "does this MATTER TO
OTHER THINGS regardless of whether it fits a known pattern" — a fact can be perfectly schema-consistent
and low-value (a redundant slot-fill nobody will ever query) or schema-inconsistent and high-value (a
genuinely novel structural link that, if wrong, would corrupt many downstream inferences). This is flagged
for a follow-up cheap test below, not built or dispatched here.

**P(downstream-reach/hub-centrality is a genuinely non-redundant 4th signal, distinct from schema_fit and
recurrence, on this substrate) = 0.40** (novel synthesis, capped per calibration discipline; well-motivated
by the EFE parameter-level/state-level split and value-directed-remembering's demonstration that importance
predicts prioritization independent of surprise, but untested on this substrate's coordinate geometry).

## Cheap decisive test

Reuse existing substrate machinery, zero new acquisition (mirrors the omnibus drill's test design):
against the already-fitted `additive_map` graph, compute for each candidate fact in the omnibus drill's
existing GENUINE-NOVEL-RELIABLE batch (batch 2) a candidate 4th signal — **downstream-reach** — as a cheap
graph-centrality proxy (e.g. degree or a lightweight PageRank/personalized-PageRank score of the
candidate's two entities in the CURRENT graph, reusing the SRColumnSolver machinery already identified as
reusable in the same-day `research_schema_fit_derivability_signal_upgrade_2026-07-16.md` note — zero new
build). Then test: does downstream-reach predict DOWNSTREAM MRR-improvement (i.e., MRR change on OTHER,
unrelated facts elsewhere in the graph after folding this candidate in) beyond what raw_PE and schema_fit
already predict?

- **HARD-PASS:** downstream-reach explains incremental variance in downstream-MRR-improvement (i.e., a
  partial correlation / incremental R² controlling for raw_PE and schema_fit) that is NOT explained by
  either of the other two signals — concretely, top-tertile downstream-reach candidates show >=15
  percentage points more downstream-MRR-improvement than bottom-tertile candidates AT MATCHED raw_PE and
  schema_fit levels. This would mirror value-directed-remembering's clean demonstration that importance
  predicts prioritization independent of surprise.
- **HARD-FAIL:** downstream-reach is near-perfectly correlated with the existing schema_fit reachability
  metric (Pearson r >= 0.85) and/or shows no incremental predictive power on downstream-MRR-improvement
  once schema_fit and raw_PE are controlled for — i.e., the omnibus's existing 3-signal architecture
  already structurally captures this, and no 4th signal is needed (a genuine, useful negative — closes
  this drill's proposed addendum cleanly rather than leaving it open).
- **MIDDLE band (plausible modal outcome):** moderate correlation with schema_fit (r=0.4-0.7, since both
  are graph-connectivity-flavored metrics) but nonzero incremental predictive power — suggesting
  downstream-reach and schema_fit are related but not identical constructs, consistent with this drill's
  conceptual distinction (structural-fit vs. downstream-consequence) rather than full redundancy or full
  independence.

## Falsifiable predictions (restated compactly, HARD-PASS + HARD-FAIL)

- P(surprise and salience/importance are neurally/formally separable, not one axis) HARD-PASSES if
  cited-above dissociation evidence (unsigned-salience dopamine population, looming-geometry detectors,
  Rouhani unsigned-vs-signed-PE memory dissociation) replicates on independent re-check; HARD-FAILS only
  if a later, more careful re-read of Matsumoto & Hikosaka / Bromberg-Martin shows the "unsigned salience"
  population's responses are actually explainable as a magnitude-only rescaling of signed value (i.e., the
  double dissociation collapses under scrutiny) — flagged as the single highest-leverage re-verification
  target if this drill's conclusions get load-bearing use.
- P(the downstream-reach 4th-signal cheap decisive test, as specified above, HARD-PASSes) — the single
  most decision-relevant open question from this drill; see P_deflated below.
- HARD-FAIL localization: if the cheap test instead shows downstream-reach is fully redundant with
  schema_fit, the correct action is NOT to abandon the value-of-information concept — it is to recognize
  that the omnibus's reachability-based schema_fit ALREADY functions as a value-of-information proxy on
  this substrate (structural congruence and downstream reach may simply covary strongly in a graph this
  size/density), and no separate signal needs to be engineered.

## Cross-thread synthesis

- Directly extends (does not redo) `research_consolidation_gate_quantitative_signals_2026-07-16.md`: that
  drill quantified surprise/schema-fit/recurrence and their combination; this drill interrogates whether
  "surprise" itself is well-specified, and surfaces a candidate 4th signal (downstream-reach/value-of-
  information) that sits outside that drill's 3-signal space rather than refining any of its three terms.
- Independently confirms (a second time, different literature entirely) the omnibus drill's single biggest
  structural finding: **no published study states a combination law for [schema-fit x surprise]** (omnibus)
  and **no published study states a combination law for [salience x surprise]** (this drill) — two
  independent confirmations of the same shape of gap is itself evidence this is a structural absence in
  the consolidation literature, not a search-term artifact. Both gaps get the same honest treatment: form
  borrowed from adjacent formalisms (Friston precision-weighting for the first; EFE epistemic/pragmatic
  split for the second), constants/combination-arithmetic ours to derive and test.
- Consistent with `research_schema_fit_derivability_signal_upgrade_2026-07-16.md`'s finding that the
  existing schema_fit proxy (`reach_pct[h]+reach_pct[t]`, a per-node aggregate percentile) is currently
  NOT pair-specific and closer to a generic-connectivity/hub metric than a genuine congruency measure —
  which raises a real risk that schema_fit (as currently implemented) and this drill's proposed
  downstream-reach signal may turn out to be MORE redundant than the conceptual distinction suggests,
  purely because of how schema_fit happens to be implemented today (node-level reachability percentile)
  rather than because the underlying constructs (structural fit vs. downstream consequence) are actually
  the same thing. This is exactly why the cheap decisive test above is framed as a redundancy check
  first — the schema_fit upgrade note's Tier-B pairwise fix (personalized-PageRank resolvent score) may
  independently move schema_fit toward or away from downstream-reach; recommend re-running this drill's
  cheap test AFTER, not before, that pairwise upgrade lands, so the redundancy check is against the
  corrected signal, not the flagged-as-coarse current one.

## Substrate-product implications

1. This drill's central actionable claim is narrow and additive to the existing architecture: a candidate
   downstream-reach/value-of-information 4th signal, computed from graph structure alone (zero external
   reward/stakes input required), which the biology literature independently motivates as a DIFFERENT
   construct from both raw surprise and schema-fit. It costs one new lightweight computation
   (degree/personalized-PageRank on the candidate's entities), reusing already-built graph machinery.
2. The two "importance substitutes" identified (exogenous designer/query-relevance weighting vs. intrinsic
   downstream-reach) are NOT mutually exclusive — biology itself uses both (external reward circuitry AND,
   separately, something learning-progress-like in schema formation timelines). The substrate can and
   probably should eventually use both: an intrinsic, always-available downstream-reach signal for
   default/unsupervised ingest gating, plus an optional external task/query-relevance weighting layer for
   when a specific downstream use-case is known (directly analogous to value-directed-remembering's cued
   point-values, which require an external value function to exist at all).
3. Genuine risk flagged, not smoothed over: TWO independent lit-scans (this drill's, and the omnibus's)
   confirm no paper states a combination law for either [schema-fit x surprise] or [salience x surprise].
   Any concrete arithmetic this program adopts for combining downstream-reach with the other three signals
   is, by definition, untested novel synthesis (P<=0.50 per discipline) — the cheap decisive test above is
   designed to generate the substrate's OWN empirical answer rather than import an unverified assumption.
4. If the cheap test's HARD-FAIL fires (downstream-reach fully redundant with schema_fit as currently
   implemented), the correct next move is NOT to search for yet another value-of-information proxy — it
   is to recognize the existing reachability-based schema_fit signal is already doing double duty as a
   crude structural-connectivity AND downstream-value proxy, and to let the Tier-B pairwise schema_fit
   upgrade (already queued per the same-day schema_fit_derivability note) subsume this question rather
   than adding a redundant parallel signal.

## Citations (verified count: 27 distinct sources across 4 lit-scans + this note's synthesis)

**Surprise/salience dissociation, general:** Polich 2007, *Clin Neurophysiol* 118:2128 (PMC2715154,
verified primary/integrative review); Rouhani, Norman & Niv 2018, *JEP:LMC* 44:1430 (PMC6117220, verified
primary); Rouhani & Niv 2021, *eLife* 10:e61077 (verified primary); Bunzeck & Düzel 2006, *Neuron* 51:369
(verified primary via Cell Press); Reichardt et al. 2022, PMID 35390179 (verified via PubMed abstract,
non-replication finding); Talmi 2013, *Curr Dir Psychol Sci* (verified secondary-review level); Castel et
al. value-directed-remembering review, *Annu Rev Psychol* 2022 (PMC10023194, verified); Howard, Kahnt et
al. 2017 dopamine sensory-PE, *Neuron* (secondary-sourced, PMID unverified directly); Science Advances 2026
striatal multi-domain PE (verified existence via search).

**Neural gating of consolidation:** Lisman & Grace 2005, *Neuron* 46:703 (PMID 15924857, primary text
quoted consistently across independent secondary citations); Duszkiewicz, McNamara, Takeuchi & Genzel 2019,
*Trends Neurosci* 42:102 (PMC6352318, verified review); Frey & Morris 1997, *Nature* 385:533 (verified
primary abstract, widely replicated); Moncada & Viola 2007, *J Neurosci* 27:7476 (verified primary
abstract); Ballarini et al. 2009, *PNAS* 106:14599 (verified primary); Ballarini et al. 2012 footshock
rescue, *PNAS* (verified primary); McGaugh 2004, *Annu Rev Neurosci* (verified, canonical); McGaugh &
Roozendaal 2006, *PNAS* 103:6741 (verified primary); "Independent effects of emotional arousal and reward
anticipation," PMID 36205480 (verified primary fMRI, no-interaction finding); Menon & Uddin 2010, *Brain
Struct Funct* 214:655 (PMID 20512370, verified primary abstract).

**Formal value-of-information / free energy / learning progress:** Itti & Baldi 2005/2006/2009, *Vision
Research* 49:1295 (PMC2782645, verified primary, exact equations and "wow"/snow-clip example quoted);
Baldi & Itti 2010, *Neural Networks* 23:649 (PMC2860069, verified primary); Lindley 1956 expected
information gain (verified via multiple convergent secondary/BOED-literature sources); Howard 1966,
"Information Value Theory," *IEEE Trans Syst Sci Cybern* (verified via secondary summaries, primary not
directly fetched); Friston et al. 2015 / Da Costa et al. 2020 expected free energy epistemic/pragmatic
split (verified via Frontiers Robotics & AI 2022 review + convergent secondary sources); Schmidhuber 2010,
"Formal Theory of Creativity, Fun, and Intrinsic Motivation," *IEEE Trans Auton Ment Dev* (verified
primary, direct quotes on compression-progress and the noisy-TV problem); Gershman, "rational analysis of
memory" (verified existence, primary text not fully extractable).

**Threat/stakes computation:** LeDoux low-road/high-road model (verified via multiple secondary sources);
Pessoa & Adolphs 2010, *Nat Rev Neurosci* (verified primary, explicit rebuttal of the subcortical-pathway
claim — flagged as a live debate, not settled); cat superior-colliculus looming neurons (PubMed
21546772, verified primary); human SC-pulvinar-VTA collision detection (PMC10795999, verified primary);
locust LGMD/DCMD looming detector (*J Neurosci* 19:1122, PMC2662764, verified primary, cross-species);
Öhman & Mineka 2001, "Fears, Phobias, and Preparedness" (verified, canonical); Matsumoto & Hikosaka 2009,
*Nature* 459:837 (verified primary); Bromberg-Martin, Matsumoto & Hikosaka 2010, *Neuron* 68:815
(PMC3032992, verified primary); Scherer 2019, *Annu Rev Psychol*, Component Process Model (verified
primary PDF).

## Deflated confidence summary (lit-scan calibration: deflate 0.15-0.25 off undeflated read; novel synthesis capped at 0.50)

- **P(surprise/unexpectedness and salience/importance are genuinely separable — two things, not one) =
  0.65** (undeflated ~0.80-0.85; this is the best-evidenced claim in the drill, deflated for lack of one
  fully-orthogonalized single-paradigm test).
- **P(the specific combination rule is multiplicative, as opposed to additive/independent or
  threshold-gated) = 0.30** (genuinely contested — one clean direct test found additive, one circuit
  suggests interactive; capped low deliberately).
- **P(downstream-reach/hub-centrality is a genuine, non-redundant 4th ingest-gate signal on this
  substrate, distinct from the omnibus's schema_fit and recurrence) = 0.40** (novel synthesis, capped per
  discipline; well-motivated by EFE's state/parameter split and value-directed-remembering, untested here).
- **P(the brain implements something functionally learning-progress-like for consolidation gating, even
  if not via Schmidhuber's exact math) = 0.45** (novel synthesis across two independently-confirmed-absent
  literatures — the schema-formation timeline is the best available indirect analog).
- **P(cheap decisive test above, as specified, HARD-PASSes) = 0.30** (undeflated ~0.40-0.45; genuinely
  uncertain until measured, and plausibly confounded by schema_fit's own known coarseness per the same-day
  schema_fit_derivability note — recommend sequencing after that upgrade lands, per Cross-thread synthesis).

## Next-drill candidate

If the cheap test is piloted (after the schema_fit pairwise upgrade lands) and downstream-reach proves
non-redundant: the natural follow-up is a `network-science-graph-theory` drill (Tier-1 in the field
advisor) specifically comparing personalized-PageRank-style downstream-reach against simpler degree-based
centrality, to establish which graph-centrality flavor best matches the biological "parameter-level
epistemic value" construct rather than defaulting to the cheapest available metric. If instead the test
shows full redundancy with schema_fit: no new research drill is needed — treat schema_fit (post pairwise
upgrade) as already subsuming the value-of-information question, and redirect attention to the
still-unresolved combination-law question (additive vs. multiplicative vs. gated) shared by both this
drill and the omnibus drill, which would benefit from an `AMP/VAMP` or `inference` field angle on
multi-signal Bayesian fusion under uncertain weighting — but only dispatch that if the redundancy check
fires HARD-FAIL first, per the "don't drill deeper into a closed question hoping for reversal" discipline.
