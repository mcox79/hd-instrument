# RESEARCH DRILL: settle-dynamics mechanics for brain-faithful bind+settle over ~2-3 central facts (aggregation retriever)

**Date:** 2026-07-24. **Trigger:** direct grounding request for the AGGREGATION RETRIEVER cell staged in
`notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md` (gated behind the CLIMB FULL
diagnostic). That note already commits to Construction-Integration (CI) bind+settle over a Cowan-4 working-memory
vessel as the USER-locked design constraint; THIS drill pins the mechanism details underneath that commitment so
the cell's settle dynamics are literally brain-derived, not an ad-hoc scoring aggregator wearing CI's name.
**Method:** 3 parallel Sonnet lit-scans (axis 1: Kintsch CI exact matrix/cycle/readout mechanics via direct primary-source
read; axis 2: theta-gamma oscillatory multiplexing for multi-item WM without blur; axis 3: biased-competition/
normalization/episodic-gating literature for how the brain avoids being swamped by candidates) + director synthesis,
course-corrected mid-task to fold in Eliasmith's Semantic Pointer Architecture (SPA)/Spaun as the closest existing
FHRR-family precedent for "combine bound facts -> settle -> answer" (already in KB, not re-derived). Lit-scan
calibration penalty applied (deflate 0.15-0.25 from raw agreement; novel-synthesis capped <=0.50).

**Explicitly NOT this drill's territory:** sequential multi-hop CHAINING (hippocampal transitive inference, the
khop module) -- covered by `notes/research_multihop_reasoning_layer_biology_and_design_sketch_2026-07-24.md`. This
drill is the DIFFERENT operation: parallel combination of a small simultaneously-held support set.

---

## HEADLINE

Kintsch's Construction-Integration model, read directly from the 1988 *Psychological Review* primary source (not
secondary paraphrase), turns out to specify a **real, signed, numeric algorithm** that is far more concrete than
the "propositions activate and coherent ones reinforce" gloss usually repeated: a connection matrix with entries in
[-1, 1] (positive = shared-argument/supporting, negative = explicitly mutually-exclusive/contradictory, zero =
irrelevant), settled by repeated matrix multiplication + renormalization (negatives clipped to zero, positives
divided by their sum) until mean activation change < .001 (Kintsch's own stated epsilon), typically 7-43 iterations
on his own small (4-28 node) worked examples. Two of Kintsch's own worked examples are unexpectedly load-bearing
for our design: (1) his short-term buffer carryover rule keeps **exactly the four most strongly activated
propositions** between processing cycles -- an independent, primary-source empirical anchor for "4," not just
Cowan's number by analogy; (2) his arithmetic-word-problem example resolves competing HYPOTHESES (not just
propositions) via a **separate, mutually-inhibitory sub-network** compared only against each other, structurally
identical to what our cell needs for "which answer choice does the settled evidence support." This gives our cell
a much more literal template than "CI-flavored" -- it gives an actual bipartite-graph recipe.

The other two legs are genuine literature GAPS, not just weakly-supported: (a) the theta-gamma oscillatory
literature (Lisman & Idiart 1995; Lisman & Jensen 2013) explains, in real mechanistic and increasingly
human-intracranial-verified detail, how the brain keeps 2-4 items from BLURRING via temporal multiplexing carved
by fast GABAergic inhibition (PING/ING) -- but it is **silent on how those items get COMBINED into one joint
answer**; that combination step is CI's job, a different (cortical, symbolic-level) mechanism operating on top of,
not instead of, the anti-blur multiplexing. (b) The selection/gating literature (Desimone & Duncan biased
competition; Reynolds & Heeger normalization; O'Reilly & Frank PBWM Go/NoGo; Anderson's retrieval-induced
forgetting) explains HOW competition + top-down bias funnels many candidates down to a few, but **none of these
theories independently derives "why ~4"** -- winner-set size is treated as graded/task-dependent everywhere it's
formalized. Cowan's number remains the only concrete anchor for cardinality; the gating literature explains the
MECHANISM that funnels toward it, not the number itself.

Eliasmith's Semantic Pointer Architecture (SPA)/Spaun (2013, already in KB) is the closest existing precedent that
actually DOES combine-bound-vectors-into-an-answer in the substrate's own binding algebra family (HRR/FHRR circular
convolution), demonstrated on question-answering and analogy in a biologically-realized (spiking, NEF) system --
but its mechanism is simpler than CI: bundle (superpose) several bound role-fillers, unbind the query role, and run
ONE attractor-network clean-up pass against a stored-item memory. It is an existence-proof that bind+bundle+
clean-up is neurally realizable in this exact algebra, not a precedent for CI's genuine multi-round, signed,
inter-item constraint satisfaction. The cell should use BOTH: SPA-style clean-up as the per-item "stay on the
semantic-pointer manifold" operation, CI-style signed-graph relaxation as the actual multi-fact/multi-choice
coherence dynamic layered on top.

P_deflated: **0.38** (see Calibration section).

---

## (1) Kintsch Construction-Integration -- the concrete algorithm (primary-source verified)

**Construction matrix** (Kintsch 1988, p.165-168): connection strength `s(i,j)` in [-1, 1]. Text-derived
propositions connect positively, strength proportional to textual proximity. Propositions inherited from the
general knowledge net keep that net's signed strength; values are additive up to a ceiling of 1. **Negative
weights are reserved specifically for propositions the knowledge net marks as mutually exclusive/contradictory**
(rival word senses, rival pronoun referents, contradictory logical results, mutually exclusive problem-solving
hypotheses) -- concrete quoted values from the paper: MONEY-BANK2 = -0.5, BANK1-BANK2 = -1.0 (homonym competition);
KNOW[SOLUTION]-EASY = -1.0 (garden-path contradiction); competing arithmetic hypotheses PPW/PWP/WPP get -1 to each
other, described by Kintsch as "mutually exclusive and inhibit each other." **Genuinely irrelevant propositions get
zero**, not negative -- they are simply never reinforced and lose share under renormalization. So there is a real
three-way semantics (positive=coherent-support, zero=irrelevant, negative=actively-contradictory), and the
"lateral inhibition" framing later commentators use for CI is literally Kintsch's own signed-matrix mechanism, not
an added gloss.

**Integration/settling procedure** (quoted): "an activation vector...is postmultiplied repeatedly with the
connectivity matrix. After each multiplication the activation values are renormalized: negative values are set to
zero, and each of the positive activation values is divided by the sum of all activation values, so that the total
activation on each cycle remains at a value of one" (citing Rumelhart & McClelland 1986 for the renormalization
procedure itself). **Stopping criterion, exact:** mean |change in activation| < .001. Kintsch flags this epsilon as
somewhat arbitrary but robust (order-of-magnitude changes to it barely move the final activations). **Iteration
counts from his own worked examples** (not estimates -- read directly): 4-node garden-path example converged in 10
iterations; 7-node pronoun-resolution example in 19; 18-node word-identification matrix in 11 (then 9 more after
adding 2 inference nodes); a 3-cycle arithmetic word problem took 10 / 7 / 43 iterations per cycle (18/28/unspecified
node counts). Kintsch states explicitly there is no fixed cycle count -- it depends on network size -- and flags in
his own discussion that "there is at present no really satisfactory way to tell how good an equilibrium a process
achieves," gesturing at (but not adopting) Smolensky's "harmony" statistic as an alternative stopping criterion.

**Readout -- no single discrete rule, TWO task-specific patterns that matter for us:** the primary "answer" in
Kintsch's own account is the continuous settled activation vector itself ("the highly activated nodes constitute
the discourse representation"). But two of his worked applications give us a directly reusable structural
template:
1. **Buffer-carryover rule (the "4" anchor):** in the Manolita arithmetic example, "the four most strongly
   activated propositions...are retained in the short-term buffer and enter the second processing cycle" -- a
   hard top-4 cutoff, independently converging with Cowan's number from an entirely different (1988,
   text-comprehension) primary source, not derived from Cowan at all.
2. **Competing-hypothesis sub-network (the answer-choice template):** the arithmetic-hypothesis selection
   (WHOLE vs. PART decomposition; PPW/PWP/WPP schema choice) is resolved by comparing the mutually-inhibiting
   hypothesis nodes **only against each other**, explicitly held separate from the (much more highly activated)
   supporting text-proposition nodes: "the activation values of the latter must be considered separately, relative
   to each other, rather than in relation to the text propositions." This is a genuine **bipartite two-node-type
   network**: evidence propositions feed positive activation into whichever hypothesis they support; hypotheses
   inhibit each other; the winning hypothesis is read off by relative activation within that sub-network, not by
   comparing hypothesis activation to evidence activation directly.

**Contrast with plain spreading activation / ACT-R (Collins & Loftus 1975; Anderson's ACT-R):** neither has an
explicit inhibitory/negative-weight term between competing nodes. Collins & Loftus: pure positive-link spreading
activation with distance/time decay, no subtractive competition (verified by direct read, flagged as
scan-tool-mediated rather than line-by-line, but consistent with established secondary literature). ACT-R: total
activation `A_i = B_i (base-level, power-law recency/frequency decay) + sum(S_ji) (spreading from context) + noise`;
retrieval requires `A_i > threshold`; among candidates, choice is a **Boltzmann/softmax** over activations (no
inhibitory link, only relative-magnitude competition via a stochastic choice rule); the fan effect (Anderson &
Reder 1999) implements interference by **dividing** the spreading-activation contribution among however many things
a cue is linked to, not by adding negative edges between the competitors themselves. **CI is the outlier and the
right precedent for us**: it is the only member of this family with literal signed negative edges wired directly
into the same matrix that carries the positive ones, actively zeroed each cycle by the renormalization step. A
score-sum-then-argmax aggregator is structurally closer to Collins & Loftus/ACT-R (relative-magnitude ranking, no
true inhibition) than to CI -- this is the concrete, citable line between "CI-flavored" and "actually CI."

## (2) Theta-gamma oscillatory multiplexing -- solves anti-blur, is silent on combination

**Mechanism** (Lisman & Idiart 1995, *Science*; Jensen & Lisman 1998; Lisman & Jensen 2013, *Neuron* "The
Theta-Gamma Neural Code"): each held item is a distinct cell-assembly firing in its own **gamma sub-cycle (~40 Hz)**
nested inside one slower **theta cycle (~5-12 Hz)**. Item populations need NOT be spatially/orthogonally separated
at all -- they can even share neurons -- because **temporal** separation (each gets its own time-slot within the
theta period) substitutes for population-level separation. The number of gamma cycles fitting in one theta cycle
(~3-8 depending on where in the theta band) is the proposed origin of the classic 7+-2 and, at the faster end of the
theta range, the ~4 number. **Inhibition is not peripheral -- it is the carving mechanism**: PING/ING (fast PV+
GABAergic interneuron-mediated inhibition, Whittington/Traub/Buzsáki & Wang 2012) enforces winner-take-all within
each gamma sub-cycle, suppressing competing assemblies until their own slot comes around -- this is literally what
converts a population code that would otherwise superpose-and-blur into a temporally discretized, one-item-at-a-time
code.

**Empirical status, separated by confidence:** well-established/replicated -- theta/gamma bands themselves, PING/ING
gamma generation, theta-gamma phase-amplitude-coupling (PAC) scaling with WM load in human intracranial recordings
(Axmacher et al. 2010, *PNAS*), serial phase-organized item representation in human ECoG (Bahramisharif et al.
2018, *PLoS Biology*, Lisman co-author). Weaker/contested -- the precise "count the gamma cycles, get the capacity
number" quantitative claim: only one small (N=17) human EEG study (Kaminski, Brzezicka & Wrobel 2011) directly
correlates digit-span with theta/gamma cycle-length ratio; a 2023/2024 human single-neuron intracranial study
(Daume/Rutishauser et al., *Nature*) actually found PAC WEAKER at load 3 than load 1 (opposite the naive
prediction), attributed to longer gamma bursts smearing phase-coupling at higher load, and reframes the PAC-coding
neurons as likely inhibitory interneurons carrying top-down prefrontal control signals rather than passive
slot-counters.

**The genuine, explicit gap (load-bearing for our design):** the sub-agent found no published account -- in this
line or elsewhere in the WM-oscillation literature -- of a mechanism for how 2-4 temporally-multiplexed items get
COMBINED into one joint output, as opposed to maintained separately and read out one-at-a-time (Lundqvist et al.
2018, *Nature Communications*, shows gamma/beta "readout bursts" selecting ONE held item for output at a time --
serial selection, not multi-item integration). **This maps cleanly onto our two-mechanism design**: theta-gamma
multiplexing is the brain's analog of our role-slot binding (keeps facts distinct without vector-level blur);
CI-style signed-graph relaxation is the SEPARATE mechanism that does the actual combining. Neither the brain nor
our design should expect one mechanism to do both jobs.

## (3) Avoiding being swamped -- biased competition, normalization, episodic gating

**Desimone & Duncan 1995 biased competition:** multiple candidates sharing a processing pool suppress each other
(response to two simultaneous stimuli approximates a WEIGHTED AVERAGE, not a sum, of the individual responses);
top-down bias (PFC/WM-sourced target template) tips the competition toward task-relevant candidates by boosting
their gain/baseline activity. **No fixed winner-set cardinality is asserted** -- winner-set size is continuous/
graded, modulated by bias strength, bottom-up salience, and perceptual grouping.

**Reynolds & Heeger 2009 normalization model:** formalizes the same phenomenon via **divisive normalization** --
each candidate's (drive x attentional gain) is divided by a pooled activity term shared across competitors, so
effective activation depends on how much competing drive is present, not just raw input. Treated in the literature
as a mechanistic refinement of biased competition (a general-purpose divisive gain-control computation), not a
rival account. Again, **no independent derivation of a specific winner-set size** from the equations themselves.

**Episodic/associative-memory-specific gating:** (a) retrieval-induced forgetting (Anderson, Bjork & Bjork 1994;
inhibition account reviewed in Storm & Levy 2012) -- practicing retrieval of a target actively suppresses
cue-activated competitors (not just passive non-practice), via right-DLPFC-mediated control recruiting GABAergic
suppression of competing hippocampal traces (Kuhl et al. 2007; Anderson & Hulbert 2021). This is a genuine,
citable case of ACTIVE gating-down of non-selected but cue-activated associations, though its documented context is
consequences for later LTM, not explicitly framed by its own authors as real-time WM-entry gating (an inference we
are making, flagged as such). (b) O'Reilly & Frank 2006 PBWM: PFC organized into independently-gateable "stripes,"
each with its own basal-ganglia Go/NoGo gate (striatal Go/NoGo -> GPi/SNr -> thalamic relay); gating across stripes
is PARALLEL and independent (several items can be gated in at once, each to a different stripe); within a stripe,
k-winners-take-all competition resolves which candidate wins that gate; which candidate wins is LEARNED via
dopaminergic reinforcement (not an innate salience rule).

**The honest finding, stated plainly:** none of biased competition, normalization, or PBWM independently derives
"why ~4" -- all three treat winner-set size as an emergent, task/bias-dependent quantity. **Cowan's number remains
the only load-bearing cardinality anchor**; this literature explains the funneling MECHANISM (mutual suppression +
top-down relevance bias + learned/dynamic gating), not the number itself. This matters for the cell: do not expect
top-down relevance-gating alone to "discover" 4 as the right candidate-set size -- it must be architecturally
fixed (per Cowan/the existing 4-slot WM vessel), with the gating mechanism only used to decide WHICH ~4 (or
top-N-before-4) enter, not HOW MANY.

## (4) Eliasmith SPA / Spaun -- the existing FHRR-family precedent for combine-bound-facts-into-an-answer

Eliasmith (2013, *How to Build a Brain*) and the Spaun model implement the Semantic Pointer Architecture: bound
role-filler structures via HRR/FHRR-style circular convolution, superposed (bundled) into a single vector,
realized in spiking populations via the Neural Engineering Framework (NEF). Question-answering and analogy tasks
are demonstrated by (1) binding several role-filler pairs, (2) bundling (superposing) them into one composite
vector, (3) unbinding the query role to get a noisy candidate, (4) running that candidate through an **associative
clean-up memory** -- an attractor network that settles the noisy vector to its nearest stored prototype. This is
the closest published precedent to "combine several bound facts, then settle to an answer" in the substrate's own
binding algebra family, and it is a genuine existence-proof that this class of operation is neurally realizable
(spiking, not just abstract linear algebra) at Spaun's scale.

**Where it matches our cell and where it doesn't:** SPA/Spaun's clean-up step is a Hopfield-like single (or
few-iteration) attractor settle against a FIXED item memory -- structurally simpler than CI's genuine multi-round,
signed, inter-item constraint satisfaction over several DISTINCT propositions/hypotheses. SPA/Spaun answers "what
was bound to this role" (single-query retrieval); our task is "which of these 2-5 answer CHOICES is best supported
by combining these 2-4 CENTRAL facts plus the semantic glue" -- structurally closer to Kintsch's competing-hypothesis
resolution (section 1) than to SPA's single clean-up lookup. **The right synthesis, not a forced choice:** use
SPA-style attractor clean-up as the LOCAL operation that keeps each individual fact/hypothesis vector a valid,
on-manifold semantic pointer after any binding/composition step (this is what makes the CI-style graph's NODES
well-formed vectors, not drifting noise); use CI-style signed-graph relaxation as the GLOBAL operation that
combines several such nodes into a joint, contradiction-aware decision. This gives the cell two validated
mechanisms operating at two different levels rather than one overloaded mechanism doing both jobs.

---

## IMPLICATIONS FOR THE CELL -- concrete settle-dynamics choices

1. **Build a real bipartite, two-node-type signed graph**, directly modeled on Kintsch's arithmetic-hypothesis
   example: node type A = the ~5-10 retrieved candidate FACTS (initial activation = their semantic-relevance cosine
   to the question+choice cue, per Desimone-Duncan top-down bias -- NOT uniform starting activation); node type B =
   the answer CHOICES (2-5, initial activation = uniform or small prior). Edges: fact-to-choice edges are POSITIVE,
   weight proportional to how strongly that fact supports that choice (the direct analog of Kintsch's
   text-proposition-to-hypothesis edges). Choice-to-choice edges are NEGATIVE (mutually exclusive, matching
   Kintsch's PPW/PWP/WPP treatment -- exactly one choice should ultimately win). Fact-to-fact edges are signed by
   mutual compatibility: positive if facts share arguments/support the same choice (Kintsch's shared-argument
   proximity rule), negative if two facts support mutually exclusive choices (a genuine cross-fact contradiction
   signal, the single biggest thing a plain score-sum aggregator has zero of).
2. **Load the ~5-10 candidate facts into the existing 4-slot working-memory vessel by RUNNING THE GRAPH DOWN TO 4**,
   not by pre-truncating to 4 before settling. Per Kintsch's own buffer-carryover rule (his top-4-after-settling
   retention, an independent primary-source anchor matching Cowan's number), the settle process itself should
   determine which facts survive into the 4-slot focus -- gate on POST-settle activation, not pre-settle relevance
   rank alone. This is the concrete way to honor both "top-down bias determines the initial competition" (Desimone-
   Duncan/Reynolds-Heeger) and "the number that survives is Cowan's/Kintsch's 4" (neither theory derives the
   number, so fix it architecturally per the existing WM vessel, exactly as flagged in section 3).
3. **Iterate**: activation vector times signed connection matrix, renormalize each cycle (clip negative activations
   to zero, divide positives by their sum -- literally Kintsch's rule). **Stopping criterion**: mean |delta
   activation| below a pre-registered epsilon (Kintsch used .001 on activation values summing to 1; scale
   appropriately to this graph's size and pre-register before looking at results). **Iteration budget**: Kintsch's
   own small networks (4-28 nodes, close to our ~7-15-node graph) converged in 7-43 iterations -- pre-register a
   comparable range (e.g. cap at 40-50) as a safety bound, not a target to hit exactly.
4. **Report convergence quality, not iteration count alone** (reuse G8 from `research_brain_settle_to_coherence_
   parse_selection_2026-07-20.md`): correct/spurious/non-convergent breakdown per item, because faster convergence
   is not the same as correct convergence in this literature family (documented in the resonator-network follow-up
   cited in that prior note).
5. **Readout**: the winning answer CHOICE is the node (in the choice sub-network) with highest settled activation,
   read off in RELATIVE comparison to the OTHER CHOICE nodes only -- exactly Kintsch's rule for his competing-
   hypothesis sub-network ("considered separately, relative to each other, rather than in relation to the text
   propositions"). Do not compare choice-node activation directly to fact-node activation; they are different node
   types with different activation scales by construction.
6. **Keep anti-blur and combination as SEPARATE mechanisms, matching the brain's own division of labor** (section
   2): the existing role-slot/positional binding (our theta-gamma analog) is what keeps the ~4 facts distinct
   *inside the vector representation*; the signed-graph relaxation above is a SEPARATE, small, discrete
   computation over those already-distinct facts (indices/handles into the slot-bound vectors, not vector
   superposition arithmetic itself). Do not expect the vector-binding layer to also do the coherence/contradiction
   reasoning, and do not expect the graph relaxation to also solve the blur problem -- neither the brain nor this
   design gets away with one mechanism doing both.
7. **Use SPA-style attractor clean-up as the node-well-formedness operation**, not the coherence operation: after
   any bind/compose step that produces a candidate fact or hypothesis vector, run it through the existing
   codebook/cleanup step (already in the pipeline per the resonator/cleanup machinery used elsewhere in this
   program) so graph NODES are valid semantic pointers before the CI-style relaxation runs on top. This is the
   concrete Eliasmith/SPA connection: clean-up memory handles "is this vector a real, recognizable thing," CI-style
   relaxation handles "given several real things, which combination is coherent."
8. **Restrict the pre-settle candidate SET size to a pre-registered bound (e.g. top-8-to-10 by initial semantic
   relevance) before building the graph**, matching Kintsch's own network scale and avoiding the O(n^2)
   pairwise-constraint cost already flagged as a perf risk in the aggregation-retriever note. This cutoff is an
   engineering choice, not itself claimed brain-derived (per section 3's honest finding that no gating theory
   independently derives a specific pre-settle number) -- state this plainly in the pre-reg, do not smuggle it in
   as "brain says so."
9. **Must-fail / construction-determinism guards (reuse G1-G9 family from the 07-20 settling-parse-selector note,
   same mechanism lineage):**
   - Zero-iteration control (single-pass score-sum using only the fact-to-choice edge weights, no relaxation, no
     fact-to-fact or choice-to-choice terms) = the explicit "disguised score-sum" arm the cell must beat. If
     multi-cycle settling does not outperform this, the CI framing is adding nothing.
   - Shuffled/randomized signed-matrix control (same edge COUNT and magnitude distribution, random assignment) --
     selection accuracy must collapse toward chance.
   - Inverted-readout control (select the LOWEST-activation choice after settling) -- must perform significantly
     WORSE than chance, not merely differently.
   - Ablation isolating the NEGATIVE edges specifically: run the identical graph with all negative weights zeroed
     (positive-only, i.e. plain spreading activation / ACT-R-style, no true inhibition) -- this is the single
     cleanest test of whether Kintsch's signed-inhibition mechanism (vs. Collins-Loftus/ACT-R-style positive-only
     spreading) is actually load-bearing for THIS task, not assumed.
10. **What would make this a disguised score-sum vs. genuinely CI-faithful, stated as a checklist**: (a) are there
    real NEGATIVE edges between contradictory facts/choices, not just top-k-then-argmax? (b) does the readout come
    from RELAXATION (>=2 real iterations changing the activation distribution), not a single pass? (c) is the
    winning choice read off in comparison to OTHER CHOICES specifically (Kintsch's separate-hypothesis-subnetwork
    rule), not compared against fact-node activations directly? (d) does the positive-only ablation (guard 9)
    measurably underperform the full signed version? If any of (a)-(d) is "no," the cell is CI-flavored, not CI.

---

## Cheap decisive test

On the aggregation-retriever cell's existing harness (ARC Easy + Challenge, WorldTree gold support, held-out
test-question-support-exclusion per the test-targeting guardrail already specified in the 07-24 cell note): run
five arms on the SAME retrieved candidate-fact set per question -- (i) full signed bipartite CI relaxation per
items 1-8 above, (ii) zero-iteration score-sum control, (iii) shuffled-matrix control, (iv) inverted-readout
control, (v) positive-only (no negative edges) ablation. Report accuracy on Easy and Challenge separately, plus the
correct/spurious/non-convergent breakdown (item 4) and the checklist verdict (item 10) for every item.

## Falsifiable predictions

**HARD-PASS (all must hold, pre-registered before results):**
1. Full signed CI relaxation beats the zero-iteration score-sum control by a pre-registered margin (>=5 points
   accuracy) on BOTH ARC Easy and Challenge, replicated across >=2 seeds.
2. Both must-fail controls (shuffled-matrix, inverted-readout) collapse to at-or-below chance.
3. The positive-only (no-negative-edges) ablation underperforms the full signed version by a non-trivial margin
   (confirming Kintsch's signed-inhibition mechanism, not just Collins-Loftus/ACT-R-style positive spreading, is
   load-bearing for this task).
4. Settling converges (mean |delta| < pre-registered epsilon) within the pre-registered iteration budget on the
   large majority of items, with the correct/spurious/non-convergent breakdown showing convergence tracks
   correctness (not anti-correlated, per the fastest-converging-is-least-accurate trap flagged in the 07-20 note).

**HARD-FAIL (any one sufficient to refute the CI-faithful framing, though the cell may still be useful as a
plain-aggregator result):**
1. Full signed relaxation does not beat the zero-iteration score-sum control -- the settling framing adds nothing;
   report honestly as a score-sum result, not CI.
2. Either must-fail control does not degrade toward chance -- the readout is a construction artifact.
3. The positive-only ablation matches or beats the full signed version -- the negative/inhibitory edges are not
   load-bearing for this task, and the design should be reported as spreading-activation-style, not CI-style
   (an honest, useful negative result, not a failure of the cell itself).
4. Non-convergence rate is high AND uncorrelated with accuracy -- signals the graph construction (edge weights) is
   not capturing real fact/choice relationships, a construction problem to fix before re-testing the mechanism.

## Cross-thread synthesis

- Directly sharpens `notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md`'s already-
  correct high-level commitment (CI bind+settle over Cowan-4, reject score-sum) with the actual signed-matrix/
  epsilon/readout mechanics from Kintsch's primary text, plus a concrete bipartite fact-vs-choice graph template
  lifted directly from Kintsch's own competing-hypothesis worked example -- this was not previously specified at
  this level of concreteness in that note.
- Extends `notes/research_brain_settle_to_coherence_parse_selection_2026-07-20.md`'s guard discipline (G1-G9,
  zero-iteration control, shuffled-codebook must-fail, convergence-quality reporting) to a DIFFERENT settling
  mechanism (discrete signed-graph relaxation over facts+choices, not vector-codebook cleanup for parse selection)
  -- same construction-determinism traps apply, reused rather than re-derived.
  That note's flag that "no paper proves CI is formally isomorphic to a Hopfield energy function" still stands;
  this drill adds that Kintsch's actual algorithm (signed matrix, clip-negative-and-renormalize) is NOT literally
  gradient descent on an energy function either -- it is its own, primary-source-documented, distinct dynamical
  rule. Do not conflate the two when implementing.
- Extends `notes/research_working_memory_integration_upper_limit_2026-07-16.md`'s F=3-4 resonator-sweet-spot /
  Cowan-4 mapping: this drill adds a THIRD, independent primary-source anchor for "4" (Kintsch's own buffer-
  carryover rule in the Manolita example), strengthening rather than merely repeating that note's numeric
  convergence claim -- three independently-derived sources (Cowan psychology, substrate resonator-factorization
  empirics, Kintsch's own 1988 text-comprehension simulation) now point at the same cardinality.
- New finding not in either prior note: the theta-gamma multiplexing literature and the CI-settling literature
  solve DIFFERENT problems (anti-blur maintenance vs. actual combination) and neither substitutes for the other --
  this directly justifies keeping the existing role-slot binding (anti-blur) and the new signed-graph relaxation
  (combination) as two separate mechanisms in the cell, rather than trying to get one mechanism to do both, which
  would be an easy design mistake absent this drill.
- New finding: biased-competition/normalization/PBWM gating literature, while real and directly relevant to HOW
  facts get their initial activation bias, does NOT independently justify a pre-settle candidate-set size --
  the cell's top-8-to-10 pre-settle cutoff (item 8) must be reported as an engineering choice, not a brain-derived
  number, distinct from the settle-derived top-4 (item 2), which DOES have a primary-source anchor (Kintsch's own
  buffer rule).
- Eliasmith SPA/Spaun (course-corrected addition, credited per KB) gives the cell's node-cleanup sub-step (item 7)
  a validated neural-realizability precedent in the exact same binding algebra family the substrate already uses --
  this is the strongest single piece of evidence that bind+settle-style combination is achievable in a
  brain-faithful, non-symbolic substrate at all, even though Spaun's own clean-up mechanism is simpler than the
  full CI relaxation this cell needs for the harder multi-choice-discrimination task.

## Substrate-product implications

A cell built per items 1-10 gives the product a **genuinely inspectable, two-level glass-box aggregation trace**:
per-question, the user-facing explanation can show (a) which facts were retrieved and their initial relevance
bias, (b) the signed fact-to-fact and fact-to-choice graph actually built, (c) the settling trajectory (iteration-
by-iteration activation), and (d) the winning choice's margin over its competitors in the separate choice
sub-network -- a direct, literal "why did it pick this answer" audit trail, not a black-box top-k-then-argmax
score. If the checklist (item 10) and HARD-PASS predictions both clear, the product claim is precise and
defensible: "combines several relevant facts the same mutually-constraining way a reading mind does, including
recognizing when two retrieved facts actually contradict each other" -- a materially stronger and more literally
brain-grounded claim than "retrieves and ranks facts by similarity." If the positive-only ablation (guard 9) wins
or ties, the honest fallback claim is still useful (a validated multi-fact aggregator) but must NOT be marketed as
CI-faithful -- report it as spreading-activation-style, per the honest distinction this drill draws in section 1.

## Citations (verified count: 31 distinct external primary/secondary sources across 3 lit-scans + 1 KB-credited
addition, cross-checked for canonical-vs-speculative/flagged status; 4 internal cross-thread notes)

**Construction-Integration / spreading-activation family:** Kintsch (1988, *Psychological Review* 95(2), primary
text directly read); Kintsch (2005, *Discourse Processes* 39(2&3)); Kintsch & Rawson (2005, in *The Science of
Reading*); Rumelhart & McClelland (1986, PDP, cited within Kintsch 1988 for the renormalization procedure);
Collins & Loftus (1975, *Psychological Review* 82, direct read flagged as scan-tool-mediated); Anderson (ACT-R
activation equations, via Taatgen, Lebiere & Anderson course chapter, direct read); Anderson & Reder (1999, fan
effect); McClelland & Rumelhart (1981, Interactive Activation model -- flagged as background context, NOT
independently re-verified this session).

**Theta-gamma oscillatory multiplexing:** Lisman & Idiart (1995, *Science* 267); Jensen & Lisman (1998, *J
Neurosci* 18(24)); Lisman & Jensen (2013, *Neuron* 77(6), "The Theta-Gamma Neural Code"); Axmacher, Henseler,
Jensen, Weinreich, Elger & Fell (2010, *PNAS* 107); Bahramisharif, Jensen, Jacobs & Lisman (2018, *PLoS Biology*
16); Kaminski, Brzezicka & Wrobel (2011, *Neurobiology of Learning and Memory* 95, N=17, flagged single-study);
Kaminski, Sullivan, Chung, Ross, Mamelak & Rutishauser (2017, *Nature Neuroscience*); Kaminski & Rutishauser
(2020, *Ann NY Acad Sci* review); Daume, Kaminski et al. (2023/2024, *Nature*, human single-neuron intracranial);
Lundqvist et al. (2018, *Nature Communications*, gamma/beta readout bursts); Buzsáki & Wang (2012, *Annu Rev
Neurosci*, PING/ING gamma-generation review); Whittington, Traub et al. (1996/2000, PING/ING mechanism papers, via
the Buzsáki & Wang review).

**Biased competition / normalization / episodic gating:** Desimone & Duncan (1995, *Annual Review of Neuroscience*
18); Beck & Kastner (2009, *Vision Research* review, PMC2740806); Reynolds & Heeger (2009, *Neuron* 61, accessed
via secondary sources -- primary paywalled); Doostani et al. (2022, *eLife* 11:e75726); Anderson, Bjork & Bjork
(1994, *JEP:LMC*, retrieval-induced forgetting); Storm & Levy (2012, *Memory & Cognition*, inhibition-account
review); Kuhl, Dudukovic, Kahn & Wagner (2007, *Nature Neuroscience*); Anderson & Hulbert (2021, *Annual Review of
Psychology*); O'Reilly & Frank (2006, *Neural Computation* 18, PBWM -- primary PDF not text-extractable, read via
secondary/textbook summary, flagged; stripe-count/capacity claim explicitly flagged as an unresolved search gap,
not a confirmed absence). One 2026 preprint (arXiv:2606.11242, "Game-Theoretic Foundations of Competition for
Conscious Access") noted but explicitly downweighted as speculative/unreviewed/partially-extractable.

**KB-credited, not re-derived (per mid-task course correction):** Eliasmith (2013, *How to Build a Brain*, MIT
Press) -- Semantic Pointer Architecture / Spaun.

**Internal cross-thread:** `notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md`;
`notes/research_brain_settle_to_coherence_parse_selection_2026-07-20.md`;
`notes/research_working_memory_integration_upper_limit_2026-07-16.md`;
`notes/research_multihop_reasoning_layer_biology_and_design_sketch_2026-07-24.md` (build-on/do-not-repeat
boundary).

## Calibration reasoning (P_deflated = 0.38)

Raw confidence in the CORE BIOLOGY (CI's exact signed-matrix mechanics, now primary-source verified rather than
inferred; theta-gamma multiplexing as a real, partially human-confirmed phenomenon; biased competition/
normalization as textbook-consensus computational accounts) is high, ~0.85, given direct primary-text verification
on the single most load-bearing leg (CI mechanics) and convergent, cross-checked findings across three independent
lit-scans with flagged rather than silently-dropped uncertainty. Standard lit-scan deflation (-0.15 to -0.25)
brings the biology alone to ~0.60-0.70. The SUBSTRATE-APPLICATION step -- building a bipartite fact-vs-choice
signed graph, gating pre-settle candidates by semantic relevance, and using SPA-style clean-up as the node-
well-formedness sub-operation -- is genuine novel synthesis (capped at 0.50 per discipline), further discounted to
0.38 because: (i) the literature explicitly does NOT address multi-item COMBINATION (theta-gamma silent on it,
biased-competition/normalization silent on cardinality) -- this drill's design for the combination step itself
extends beyond any single cited mechanism, it is a synthesis across three literatures Kintsch's own paper does not
unify with WM-oscillation or attention-gating theory; (ii) Kintsch's competing-hypothesis template (the strongest
concrete precedent) is drawn from a single small worked example (an arithmetic word problem), not a validated
general-purpose multi-choice discriminator; (iii) none of this has been smoked -- the cell described in items 1-10
is a design, not yet a measurement, and per the mandatory hard-fail thresholds above it may well show the
positive-only ablation winning (a real, useful, but non-CI-faithful outcome) rather than the hoped-for signed-
inhibition win.
