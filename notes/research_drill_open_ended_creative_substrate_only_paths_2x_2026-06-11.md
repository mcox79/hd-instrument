# Research Drill: Open-Ended Creative Generation -- 13 Untested Substrate-Only Paths (2x Depth)
# Date: 2026-06-11
# Trigger: User mandate -- drill G defeatism challenge; verify ALL substrate-only paths exhausted
# Calibration penalty: -0.20 applied; novel-synthesis P capped at 0.50
# Prior drill: statistical_NL_creative_2x (Paths 1-10: Zipf/n-gram/Levelt/temperature/template)
# This drill: 13 NEW paths NOT covered in the prior drill

---

## HEADLINE

The prior drill (statistical_NL_creative_2x) covered distributional fluency via Zipf codebooks,
n-gram superposition, temperature sampling, Levelt pipeline, and structured templates. Five
substrate-native mechanisms validated across the portfolio have NOT been applied to open-ended
creative generation: (1) DREAMING-mode offline replay already validated at PP-328 as autonomous
discovery, (2) SLIPNET cross-domain analogy composition validated at PP-327 (0.985), (3) substrate
DPEFE iterative refinement (active-inference EFE loop now validated at PP-351 following rescue),
(4) boredom-signal-driven novelty seeking (PP-315 validated), and (5) multi-drive VSA arbitration
(PP-360 VSA-H3 validated). Each of these has an untested creative-generation application path.
P_deflated estimates for the 13 paths range from 0.12 (human-feedback substrate loop) to 0.45
(DREAMING replay for creative recombination). The ceiling for substrate-only genuinely-novel text
(not retrieval-recombination) remains 0.35-0.45 after calibration, but the honest conclusion is
that the prior drill's framing of "needs LLM hybrid" was based on paths 1-10 only; paths 11-23
(this drill) have not been run, and three of them (DREAMING replay, iterative DPEFE, SLIPNET
cross-domain composition) have non-trivial P.

---

## CHEAP DECISIVE TEST

**Phase 0 (30 minutes CPU, single anchor, decisive for 3 of 13 paths):**

Substrate DREAMING replay for creative recombination. Build a W with 200 stored concept-scene
pairs (50 characters, 50 settings, 50 actions, 50 objects). Run 100 DREAMING cycles: at each
cycle, retrieve the three most-activated items from W using a random noise probe (no specific
query), bind them with positional markers (SLOT_1, SLOT_2, SLOT_3), and emit the bound triple as
a candidate creative fragment. Count: (a) how many of the 100 outputs are syntactically valid
triples (character + action + object, correct slot bindings), (b) how many are novel combinations
(not stored as a triple in the original W), (c) diversity: how many distinct triples appear.

Pre-registered bands:
- HARD_PASS: >= 60% valid triples AND >= 80% are novel combinations AND >= 40 distinct outputs
  in 100 samples. Interpretation: DREAMING can serve as a creative recombination engine.
- MID_BAND: valid triples 40-60% OR novel combinations 50-80% OR distinct outputs 20-40.
- HARD_FAIL: valid triples < 30% OR distinct outputs < 15 (not diverse enough to be creative).

This test runs on existing DREAMING infrastructure (PP-328 validated), costs zero new code for
the substrate machinery, and requires only a new test scaffold. It directly answers whether
offline DREAMING replay is a creative generation mechanism.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Path 11: SUBSTRATE-NATIVE DREAMING REPLAY (PP-328 creative extension)

P_deflated = 0.42 (after -0.20 calibration from nominal 0.62)

Mechanism: PP-328 validated DREAMING as autonomous pattern discovery. The substrate ran offline
replay cycles and retrieved statistically novel pattern combinations. For creative generation, the
application is: run DREAMING with a diverse semantic KB (characters, settings, events), collect
the natural-retrieval outputs, filter for slot-structural validity, and emit the valid combinations
as creative text fragments.

Why this is different from prior work: PP-328 used DREAMING for DISCOVERY (finding structure in
stored patterns). This path uses DREAMING for GENERATION (producing new combinations not in W).
The algebraic difference: discovery mode queries a specific probe and retrieves; generation mode
uses low-specificity probes (random noise or weak semantic seeds) and accepts whatever W activates.
The substrate's associative recall under noisy probes is well-validated (AM work, PP-119/120).

HARD_PASS: >= 60% syntactically valid triples AND >= 80% novel combinations (not stored verbatim
  in W) AND >= 40 distinct outputs in 100 DREAMING cycles.
HARD_FAIL: valid triples < 30% (DREAMING does not preserve slot structure under noise) OR
  distinct outputs < 15 (collapses to a few high-weight attractors, not generative).

Key risk: DREAMING under unguided probes may collapse to a few high-activation attractors (the
most frequently stored patterns) rather than producing diverse combinations. This is the attractor
basin problem -- W's energy landscape may have a few deep wells that absorb all DREAMING cycles.
If that is the case (HARD_FAIL), the fix is guided DREAMING with structured noise injection.

Cheap test cost: 30 minutes CPU on existing DREAMING scaffold. Requires: PP-328 test harness,
200-item semantic KB (buildable in 10 minutes), DREAMING loop with random probe seeds.

### Path 12: SLIPNET CROSS-DOMAIN ANALOGY COMPOSITION (PP-327 creative extension)

P_deflated = 0.38 (after -0.20 calibration from nominal 0.58)

Mechanism: PP-327 validated SLIPNET cross-domain activation at 0.985 on synthetic data (semantic
spreading activation across domain boundaries). For creative generation, the application is:
given a seed concept from domain A (e.g., MUSIC), activate the SLIPNET and let spreading
propagation reach domain B concepts (e.g., FOOD). Bind the cross-domain activated concepts into
a creative metaphor or scene: "melody is a spice" type constructions.

Why this is different: PP-327 tested whether cross-domain spreading REACHES a target. This path
tests whether the cross-domain activated set can be bound into a coherent creative fragment. The
algebraic operation: (1) seed activation, (2) spreading retrieval to collect the top-k cross-
domain items, (3) bind into a structural template (A is-like B, A does C, etc.), (4) emit.

The conceptual blending connection (Fauconnier & Turner 2002 "The Way We Think"): creative
metaphor is computationally modeled as projection between mental spaces. SLIPNET cross-domain
activation is a substrate-native approximation of mental-space blending. The substrate does not
do Fauconnier-Turner full integration (it cannot construct a new blended space), but it can do
the projection step: retrieve what MUSIC-domain activations map to in FOOD domain, then compose.

HARD_PASS: >= 5 of 20 generated metaphors rated "surprising and coherent" by 3 human raters
  (>= 2/3 agreement); none of the 5 are verbatim stored analogies from the training set.
HARD_FAIL: 0 of 20 rated coherent OR all rated coherent are in the stored training set (retrieval
  not generation).

Key risk: The polysemy/cross-activation interference problem documented in the SLIPNET real-data
rescue (cycle 227 MIDDLE_BAND at 0.375) means that on real data, cross-domain activation may
fire spuriously. Path 12 is conditioned on the SLIPNET real-data ceiling being at least 0.50
for the specific type-isolated spreading rescue currently in exp_dev. If the rescue fails, this
path inherits that failure.

Cheap test cost: 1 hour CPU on existing SLIPNET infrastructure + 20 metaphor generations + 3
human raters (30 minute async rating task). Gate: wait for TSE/type-isolated spreading rescue
verdict (exp_dev_handoff_research_slipnet_real_polysemic_rescue_2x_2026-06-11.md).

### Path 13: BIG-N CAPACITY EXPANSION FOR NUANCED EXPRESSION (N=8192 to N=65536)

P_deflated = 0.40 (after -0.20 calibration)

Mechanism: The prior statistical_NL_creative_2x drill was implicitly scoped to N=8192 (default).
At N=65536 (validated in PP-225 and capacity analysis), capacity scales to ~3600 reliable items
vs ~450 at N=8192. This is an 8x capacity expansion. For creative generation, this means storing
8x more nuanced stylistic distinctions: instead of 50 adjective styles, store 400. Instead of
30 narrative beat types, store 240.

The creative generation hypothesis under big-N: style transfer and nuanced voice variation become
possible not through learning but through scale. A N=65536 substrate can store distinct vector
representations for "terse noir", "lyrical pastoral", "clipped thriller", "baroque gothic", and
retrieve the style-compatible completions based on binding operations.

The prior drill's Path 7 (sliding-window context, coherent at K=32) already flagged that N=65536
is likely required for any multi-token creative generation. This path tests whether the capacity
expansion specifically unlocks STYLE VARIETY, not just token coherence.

HARD_PASS: at N=65536, the substrate can store >= 10 distinguishable style vectors (cosine
  distance > 0.20 pairwise) AND generate text fragments rated as stylistically distinct (human
  3-rater majority agreement, 10 style pairs).
HARD_FAIL: pairwise cosine distance < 0.10 between style vectors (too similar to distinguish)
  OR human raters cannot distinguish style pairs above 60% accuracy (chance = 50%).

Cheap test cost: 2 hours CPU. N=65536 substrate initialization is already validated. Style vectors
require a corpus with labeled style examples (1 hour to curate 10 x 20 fragments per style).

### Path 14: STOCHASTIC TUNNELING (PP-347) FOR CREATIVE-BLOCK ESCAPE

P_deflated = 0.28 (after -0.20 calibration from nominal 0.48)

Mechanism: PP-347 stochastic tunneling validated that the substrate can escape local energy
minima via frustrated tunneling (temperature-equivalent stochastic perturbation on W reads).
For creative generation, the application is: when the autoregressive generation loop gets stuck
in a high-frequency attractor (repeating common phrases), inject a stochastic tunnel perturbation
to escape the basin and generate from a different attractor region.

This is the substrate-native equivalent of "creative block escape." The biological analog: REM
dreaming as a stochastic tunneling mechanism to escape waking cognitive attractors (Hobson 2009
on dream function in cognitive reorganization; Stickgold 2005 sleep consolidation and insight).
Empirically, humans generate more creative associations after sleep (Cai et al. 2009 PNAS REM
and creative problem-solving), consistent with the tunneling hypothesis.

The architectural design: embed a frustration counter in the autoregressive generation loop. When
cosine similarity of consecutive retrieved tokens exceeds a threshold (indicating attractor
convergence), inject a scaled noise vector into the retrieval query. Noise magnitude is the
"tunneling amplitude." After 1-3 tunnel steps, resume greedy retrieval.

HARD_PASS: tunnel injection reduces repetition rate (consecutive identical tokens in 100-token
  generation) by >= 40% AND BLEU-1 vs reference sentences is maintained within 10% of non-tunnel
  baseline (does not destroy coherence).
HARD_FAIL: repetition rate reduction < 15% (tunneling too weak) OR coherence drops > 25% (too
  destructive).

Key risk: noise injection for tunneling is parameter-sensitive. Too little: attractor not escaped.
Too much: generation becomes random. Requires HP sweep over 3-5 noise amplitudes.

Cheap test cost: 2 hours CPU. Requires augmenting the existing generation loop (Path 3 temperature
sampling scaffold) with a frustration counter and noise injection. No new substrate machinery.

### Path 15: BOREDOM-DRIVEN NOVELTY SEEKING (PP-315) FOR VOCABULARY EXPANSION

P_deflated = 0.32 (after -0.20 calibration)

Mechanism: PP-315 validated that the substrate's boredom drive increases novelty-seeking (retrieval
of less-recently-activated items). For creative generation, the application is: use the boredom
signal as a vocabulary expansion mechanism. High boredom = retrieve less-common tokens. Low
boredom = retrieve common tokens. This produces a dynamic generation policy that uses rich
vocabulary when semantically justified and common vocabulary when in structural transitions.

The Bybee usage-frequency connection: token-frequency in production decreases with boredom.
Highly bored speakers use low-frequency, high-information vocabulary. This is empirically
consistent with the boredom effect: in brainstorming experiments, participants who are mildly
bored generate more creative (low-frequency, distant-associate) word choices (Mann & Cadman
2014, British J Social Psych -- experimental replication of creativity-boredom link).

HARD_PASS: boredom-modulated generation achieves type-token ratio (TTR, = unique tokens /
  total tokens) >= 0.55 in 100-token generations (compared to baseline TTR ~0.30 for high-
  frequency n-gram generation). Human raters prefer boredom-modulated outputs on vocabulary
  richness 4:1 over baseline in a blind A/B test (8 rater-pairs, 10 output-pairs each).
HARD_FAIL: TTR < 0.35 (no vocabulary expansion) OR human raters prefer baseline 2:1 or more
  (boredom modulation degrades readability without compensating for vocabulary gain).

Cheap test cost: 2 hours CPU. Requires connecting PP-315 boredom signal output to the retrieval
scoring function (apply boredom-weighted frequency penalty to high-activation common tokens).

### Path 16: MULTI-DRIVE VSA INTEGRATION (PP-360) FOR INTENTIONAL NARRATIVE ARC

P_deflated = 0.30 (after -0.20 calibration from nominal 0.50)

Mechanism: PP-360 VSA-H3 validated multi-drive arbitration (combining boredom, curiosity, and
goal-approach drives into a single VSA priority vector). For creative generation, the application
is: map narrative-structural drives to the multi-drive architecture:
  - Tension drive (rising conflict): analogous to goal-approach in PP-360
  - Curiosity drive (open mystery): analogous to curiosity in PP-360
  - Release drive (falling action): analogous to boredom/saturation in PP-360

If these three narrative drives can be implemented as VSA-H3 input channels, the multi-drive
arbitration should produce a generation policy that naturally builds and releases narrative tension
-- the basic three-act structure. This is the substrate-native path to intentional narrative arc,
not LLM fine-tuning on story corpora.

Prior connection: PP-360 was validated for WHICH drive wins arbitration, not for WHAT the drive
produces in terms of output. This path tests whether the arbitration outputs can be mapped to
retrievable narrative-beat tokens (TENSION_RISING, COMPLICATION, REVERSAL, RESOLUTION) stored
in the KB and retrieved according to the winning drive.

HARD_PASS: substrate generates 10-beat story outlines (1 token per beat, 10 tokens total) where
  the sequence follows a recognizable three-act pattern (setup / complication / resolution) rated
  by 3 human raters as "narratively sensible" in >= 7 of 10 cases.
HARD_FAIL: narrative-beat sequences are random order (no three-act structure detectable) OR human
  raters cannot distinguish substrate-generated outlines from shuffled-beat baselines above 60%.

Cheap test cost: 3 hours CPU. Requires: (1) define 30 narrative-beat tokens, (2) encode into KB,
(3) map tension/curiosity/release drives to retrieval weights, (4) run generation loop.

### Path 17: MEMORY SEARCH AND RECOMBINATION (COMPOSITIONAL REPLAY)

P_deflated = 0.35 (after -0.20 calibration)

Mechanism: This is the substrate-native analog of human "reminiscing + recombination" creativity.
The operation: (1) retrieve a stored scene A from W using a thematic query, (2) retrieve a
structurally similar but semantically distant scene B using A as the new probe (heteroassoc hop),
(3) bind elements of A and B into a composite scene C using structural placeholders. Scene C is
creative because it combines two real stored scenes in a novel structural frame.

The combinatorial argument: with M stored scenes, the number of distinct A-B composites is M^2 /
2 (unordered pairs). At M=200 scenes and N=8192, reliable recall of 200 items is within capacity
(0.056 * 8192 = 459 items). The 200-choose-2 = 19900 possible composites are all "novel" in the
sense of not being stored. The question is whether the structural binding (composite scene C) is
coherent enough to be creative vs. just a confusing mashup.

Analogical reasoning connection: Hofstadter's COPYCAT (Hofstadter & Mitchell 1994) and the
general Structure-Mapping Engine (Gentner 1983) both argue that creativity is structural analogy
-- mapping the STRUCTURE of one domain onto the CONTENT of another. Path 17 tests whether
substrate heteroassoc hop + compositional binding can approximate SME-style structural mapping.

The key difference from Path 12 (SLIPNET cross-domain): Path 17 operates on concrete stored
scenes (episodic memory analog) while Path 12 operates on semantic concept activation (semantic
memory analog). Both are needed for the full creative production cycle (semantic memory gives
abstract concepts; episodic memory gives concrete scenes).

HARD_PASS: A-B composite scenes C rated as "surprising and coherent" by 3 human raters in >= 6
  of 20 tested pairs. None of the 6 are stored verbatim in W.
HARD_FAIL: 0 of 20 rated coherent AND surprising OR all rated cases are trivially similar (A and
  B are near-synonyms, composite C is trivial).

Cheap test cost: 2 hours CPU. Requires extending the existing heteroassoc chain test (depth-3
validated in PP-9b) to depth-2 bidirectional hop + binding composition.

### Path 18: ITERATIVE REFINEMENT DPEFE (ACTIVE-INFERENCE TEXT)

P_deflated = 0.38 (after -0.20 calibration from nominal 0.58)

Mechanism: The active-inference DPEFE-H2 rescue was validated with goal_reach improving from
0.63 to target-band. The substrate can run a generate-assess-revise loop using active inference.
For creative generation: (1) generate a candidate sentence fragment S, (2) compute the EFE
(expected free energy) of S relative to a goal prior (e.g., "should be funny", "should be
suspenseful"), (3) revise S by adding/replacing tokens to reduce EFE, (4) repeat until EFE
falls below threshold or iteration limit.

Why this is different from all prior paths: every other path generates in a single forward pass.
Path 18 generates iteratively, with explicit goal-directed revision. This is the closest substrate-
only analog to prompt-based LLM creative generation, where the LLM implicitly "revises" via
attention over the full context.

The key question: can the substrate's EFE computation (validated in goal_reach context) be
adapted to a text-quality criterion? EFE minimization requires a prior over "what good text looks
like." In the goal_reach context, the prior was the goal state distribution. For text quality,
the prior could be: average cosine similarity of generated tokens to a "style prototype" bundle.
High cosine similarity to the style prototype = low EFE = good text for that style.

HARD_PASS: iterative refinement improves human coherence rating from initial 2.0/5 (baseline raw
  generation) to >= 3.0/5 after <= 5 revision cycles, measured on 10 test fragments, 3 raters.
HARD_FAIL: mean rating after 5 revision cycles <= 2.2/5 (< 10% improvement over baseline) OR
  revision loop diverges (oscillates without EFE decrease for > 3 consecutive cycles).

Cheap test cost: 3 hours CPU. Requires adapting the DPEFE-H2 active-inference loop (recently
validated) to accept a text-quality prior. This is the most structurally grounded path in this
drill because it builds directly on the validated DPEFE rescue result.

### Path 19: SUBSTRATE PREFERENCE LEARNING (RLHF ANALOG)

P_deflated = 0.22 (after -0.20 calibration from nominal 0.42)

Mechanism: Instead of gradient-based RLHF, implement an online preference update directly on W.
Operation: (1) generate two candidate fragments S_A and S_B from the same context, (2) ask a
rater which is preferred (or use an automated quality proxy), (3) update W by strengthening the
binding patterns present in S_A and weakening those in S_B.

The Hebbian-reward update rule: W += eta * (S_A - S_B) as a simple difference vector update.
This is biologically plausible (reward modulates Hebbian plasticity via dopamine in the basal
ganglia; Schultz 1997 reward-prediction error; O'Reilly 2006 computational prefrontal models).
The substrate analog: the difference vector (S_A - S_B) is added to the W superposition with
positive weight, nudging future retrievals toward S_A-type patterns.

The key limitation: W update requires online write access during generation, which conflicts with
the static-W inference assumption. PP-154 validated online W update during inference; this is the
connectivity needed for Path 19. Without PP-154-style online update, Path 19 requires batch
updates between generation rounds (not true online RLHF).

HARD_PASS: after 50 preference update rounds, generated text cosine similarity to preferred-
  style prototype increases by >= 20% over untrained baseline.
HARD_FAIL: cosine similarity to preferred style after 50 rounds <= untrained baseline + 5%.

Cheap test cost: 4 hours CPU. Requires connecting PP-154 online W update to a preference update
rule. This path has lower P than Path 18 because online W modification during generation is
architecturally more complex.

Key risk: W update for generation quality may interfere with EXISTING stored content quality
(the catastrophic forgetting problem). The sharding architecture (PP-299) partially addresses
this; a generation-quality shard could be maintained separately from the KB shard.

### Path 20: SUBSTRATE-AS-COMPETITIVE-AUTHOR (MULTI-GENERATOR + SUBSTRATE JUDGE)

P_deflated = 0.28 (after -0.20 calibration from nominal 0.48)

Mechanism: Run 3 independent generation instances using the same W but different probe noise
seeds. Each instance generates a candidate fragment. A fourth "judge" substrate (or the same
substrate in a different query mode) ranks the 3 candidates by their cosine similarity to a
quality-representative bundle stored in W (a "good text exemplar" bundle). Emit the top-ranked
candidate.

This is a substrate-native beam search: multiple hypotheses (3 branches) + substrate scoring.
The key advantage over single-pass generation: diversity from multiple seeds means different
attractor basins are explored; the judge selects the most coherent path.

Connection to prior work: the 3-substrate competitive architecture (documented in sprint-1+2
findings as multi-drive arbitration) was validated for GOAL SELECTION but not for CREATIVE
CONTENT SELECTION. This is the extension to text quality.

HARD_PASS: competitive-author beam selection improves human coherence rating by >= 0.5 points
  (5-pt scale) over single-pass baseline on 10 evaluated fragments, 3 raters.
HARD_FAIL: competitive-author rating <= baseline + 0.2 points (selection noise cancels diversity
  benefit) OR all 3 instances collapse to the same output (no diversity from noise seeds).

Cheap test cost: 2 hours CPU. 3x generation instances are embarrassingly parallel; run with
3 different torch.Generator seeds. Judge scoring requires a quality bundle in W (1 hour to curate
10 "good text" exemplars and encode).

### Path 21: SUBSTRATE-NATIVE STYLE TRANSFER (CROSS-MODAL STYLE BINDING)

P_deflated = 0.35 (after -0.20 calibration from nominal 0.55)

Mechanism: Style transfer via VSA role-filler binding. A "style" is encoded as a set of
characteristic trigrams, POS patterns, and lexical choices. These are bundled into a style vector
S_style. Content is encoded as a set of semantic role fillers (who does what to whom). The output
generation uses the composition: bind(S_style, content_roles) as the retrieval query. This
retrieves tokens that are both stylistically consistent (matched to S_style) and semantically
appropriate (matched to content_roles).

The prior work connection: PP-345 (translation 1.000) demonstrated that the substrate can apply
structural transformations (SVO -> SOV) via binding composition. Style transfer is a more
constrained variant of the same operation: apply style-characteristic patterns to content-
specified fillers. The POS tagger (PP-364 0.906 Tier A) provides the syntactic backbone.

The key empirical question: are different writing styles (terse vs. elaborate; formal vs.
colloquial) distinct enough in trigram-space to produce separable style vectors? Linguistic
research on stylometry (Koppel et al. 2009 "Computational Methods in Authorship Attribution")
suggests that author styles are statistically separable with as few as 100 function-word
frequencies -- well within the substrate's capacity at N=8192.

HARD_PASS: substrate-applied style transfer produces outputs that human raters assign to the
correct style category (terse/elaborate/formal/colloquial) above 65% accuracy (4-AFC = 25%
chance) on 20 generated fragments per style, 3 raters.
HARD_FAIL: rater accuracy <= 40% (style binding not detectable in outputs).

Cheap test cost: 2 hours CPU. Requires a 4-style labeled corpus (200 fragments per style, easily
sourced from Project Gutenberg), 4 style vector encodings, and a binding-based generation loop.

### Path 22: SUBSTRATE LATENT-SPACE INTERPOLATION (VECTOR ARITHMETIC FOR NOVELTY)

P_deflated = 0.25 (after -0.20 calibration from nominal 0.45)

Mechanism: Vector arithmetic for creative combinations, analogous to word2vec "king - man + woman
= queen" type operations. For creative generation: given two stored scenes A and B, compute
C = A + alpha * (B - A) for alpha in (0, 1). Query C against the pool to retrieve the nearest
stored item or generate from C as a retrieval query. Interpolated vectors may activate patterns
that are structurally between A and B.

The key difference from Path 17 (recombination): Path 17 does SEQUENTIAL binding (A leads to B
leads to C). Path 22 does ARITHMETIC interpolation (the midpoint of A and B in vector space).
The two paths explore different parts of the creative space.

The risk: interpolated vectors in FHRR space are not guaranteed to be semantically coherent. In
word2vec (dense real-valued embeddings), interpolation works because nearby vectors are
semantically similar (the distributional hypothesis). In FHRR (random binary or bipolar
distributed representations), the interpolation midpoint is NOT semantically midway between A
and B. It is a superposition of A and B, which the substrate interprets as a bundled pair, not
an interpolated semantic point. This is a fundamental difference.

Cheap workaround: use alpha in {0, 0.5, 1} only (i.e., only the midpoint) and test whether the
midpoint consistently retrieves items that human raters rate as "semantically between" A and B.
If midpoint retrieval is coherent, interpolation is usable. If not, this path is structurally
blocked for FHRR and would require a different representation (dense semantic embeddings, which
is the LLM-hybrid path).

HARD_PASS: midpoint queries retrieve items that 2/3 raters classify as "between" A and B in
  semantic meaning for >= 6 of 10 test pairs.
HARD_FAIL: midpoint queries retrieve items rated "closer to A OR B" (not intermediate) in >= 7
  of 10 pairs (interpolation collapses to one endpoint).

Cheap test cost: 1 hour CPU. The interpolation operation is trivial in NumPy/PyTorch. The test
requires 10 A-B concept pairs with a third concept C known to be semantically intermediate.

### Path 23: TEMPERATURE-CONTROLLED TEMPORAL POLICY (BEYOND Q5 TEMPERATURE SAMPLING)

P_deflated = 0.36 (after -0.20 calibration from nominal 0.56)

The prior Q5 (statistical_NL_creative_2x) asked whether temperature sampling produces
CONTROLLABLE DIVERSITY. This path goes deeper: the temporal policy is not just temperature at
the token level, but a SCHEDULE of temperatures across a generation sequence.

Mechanism: vary temperature T as a function of position in the generation sequence. Specific
profiles to test:
  - Profile A (creative-start): T=1.5 for first 20 tokens (diverse, exploratory) then T=0.3
    for remaining tokens (focused, coherent). Mimics creative brainstorming followed by
    elaboration.
  - Profile B (creative-peak): T=0.5 for setup tokens, T=1.5 for the dramatic moment (peak
    novelty at narrative peak), T=0.5 for resolution. Mimics narrative tension arc.
  - Profile C (annealing): T starts at 2.0 and decreases monotonically to 0.1. This is simulated
    annealing for text generation -- start with high entropy and "freeze" to the best configuration.

The information-theoretic justification: profile C is a discrete simulated annealing schedule
on the generation chain. This is the connection to the frustration-tunneling work (PP-347): high
T = high tunneling amplitude = frequent basin escape. As T decreases, the system settles into a
locally high-quality attractor. The theoretical prediction (from SA convergence proofs, Geman &
Geman 1984) is that sufficiently slow cooling converges to a global optimum; the practical
question is whether "sufficient" slowness is achievable in a 100-token generation window.

HARD_PASS: Profile A outperforms flat T=1.0 on combined diversity+coherence metric (TTR * BLEU-1)
  by >= 20% on 20 test generations, measured automatically.
HARD_FAIL: no profile outperforms flat T=0.5 (best coherence baseline) on BLEU-1 by more than 5%
  (scheduled temperature does not improve any metric).

Cheap test cost: 1 hour CPU. Extension of Q5 temperature sampling scaffold (trivial code change:
replace fixed T with position-indexed T array).

---

## HONEST DECISION TREE: WHEN TO ACCEPT SUBSTRATE-ONLY CEILING

### Tier 1: High P paths (>= 0.35 after calibration) -- RUN FIRST

1. Path 11: DREAMING replay (P=0.42) -- 30 min CPU. Run as Phase 0.
2. Path 18: Iterative DPEFE refinement (P=0.38) -- 3h CPU. Run as Phase 1.
3. Path 12: SLIPNET cross-domain metaphor (P=0.38) -- gate on SLIPNET rescue verdict first.
4. Path 21: Style transfer via binding (P=0.35) -- 2h CPU. Run as Phase 1.
5. Path 17: Memory recombination (P=0.35) -- 2h CPU. Run as Phase 1.

If all 5 of these HARD_FAIL, accept that substrate-only creative generation is bounded at the
prior drill's ceiling: structured-template generation (Path 8) is the best substrate-only path,
and genuinely novel open-ended text requires LLM hybrid.

### Tier 2: Medium P paths (0.28-0.35) -- Run only if Tier 1 shows any partial signal

6. Path 23: Scheduled temperature (P=0.36) -- cheap, run alongside Tier 1.
7. Path 13: Big-N style variety (P=0.40) -- moderate cost, run if Tier 1 shows diversity gaps.
8. Path 15: Boredom-driven vocabulary (P=0.32) -- run if Tier 1 generates but lacks vocabulary.
9. Path 20: Competitive author beam (P=0.28) -- run as a beam-search improvement layer on top of
   any Tier 1 path that achieves MID_BAND.
10. Path 16: Multi-drive narrative arc (P=0.30) -- run if DPEFE (Path 18) shows goal-structure
    works but narrative arc needs explicit drive signals.

### Tier 3: Lower P paths (< 0.28) -- Run only with specific trigger

11. Path 14: Frustration tunneling (P=0.28) -- run only if Path 11 or Path 18 shows attractor
    collapse (repetition) as the dominant failure mode.
12. Path 22: Latent interpolation (P=0.25) -- run only if Path 17 recombination shows that
    sequential binding is insufficient; this tests arithmetic path.
13. Path 19: Preference learning (P=0.22) -- run only after Tier 1 and Tier 2 paths show that a
    specific quality dimension needs targeted improvement that retrieval-alone cannot achieve.

### Accept-ceiling trigger

ACCEPT that substrate-only novel creative generation is bounded below the "genuinely surprising"
bar if ALL THREE of the following conditions hold:
  (a) Path 11 DREAMING HARD_FAILS (attractor collapse; outputs not diverse).
  (b) Path 18 DPEFE HARD_FAILS or reaches MID_BAND with < 0.3pt improvement.
  (c) Path 12 SLIPNET cross-domain HARD_FAILS (no coherent metaphors rated surprising).

These three are the highest-P untested paths. If all three fail, the remaining paths (14-23)
have P_deflated < 0.35 and do not justify continued substrate-only investment before shipping
the LLM-hybrid path (Path 10 from prior drill).

If ANY ONE of Path 11, 12, or 18 achieves HARD_PASS: continue through Tier 2.

---

## PRE-REGISTRATION: WHICH PATHS LIKELY PRODUCE GENUINELY NOVEL TEXT

By "genuinely novel" we mean: the output (a) was not stored verbatim in W, (b) is rated by a
naive human rater as creative (not just coherent), (c) demonstrates a combination or perspective
not derivable by simple template completion.

### Pre-registered prediction (committed before running experiments):

- Paths with REALISTIC P for genuinely novel output: Path 11 (DREAMING), Path 12 (SLIPNET), Path 18 (DPEFE-iterative), Path 17 (memory recombination)
- Paths with REALISTIC P for coherent output but NOT novel: Path 13 (big-N), Path 21 (style transfer), Path 23 (temperature schedule)
- Paths with LOW P for either: Path 14 (tunneling), Path 15 (boredom), Path 16 (multi-drive), Path 19 (preference), Path 20 (competitive), Path 22 (interpolation)

The "genuinely novel" distinction matters because it is what Drill G's original claim targeted.
Drill G said "genuinely novel open-ended text needs LLM hybrid." Paths 11, 12, 17, 18 are the
four substrate-only mechanisms most likely to produce genuine novelty (recombination of episodic
memory, cross-domain conceptual blending, iterative refinement with quality prior, offline replay
under noisy probes). None of these were tested in the prior drill.

The pre-registration thus commits to: if all four of these HARD_FAIL, accept Drill G's original
framing as correct and route to LLM-hybrid path (Path 10) as the definitive answer. If any one
achieves HARD_PASS, Drill G's framing was incomplete (not wrong, but incomplete -- an important
distinction per the defeatism mandate).

---

## CROSS-THREAD SYNTHESIS

### With DREAMING (PP-328)

PP-328 validated DREAMING as autonomous pattern discovery on synthetic data. Path 11 is the
direct creative extension. The critical question not answered by PP-328 is whether DREAMING
under NOISY probes (as in Path 11) preserves slot structure or collapses to noise. PP-328 used
specific probes; Path 11 uses low-specificity probes. The connection to sleep/creativity
neuroscience (Stickgold 2005, Cai et al. 2009) provides biological plausibility.

### With SLIPNET (PP-327) and its rescue (cycle 227)

PP-327 validated SLIPNET at 0.985 on synthetic. The cycle-227 MIDDLE_BAND on real data
(0.375 with k=10 reltypes) identified type-isolated spreading rescue as the engineering fix.
Path 12 (creative metaphor via cross-domain activation) is CONDITIONED on that rescue reaching
at least 0.60. This is an explicit dependency that must be tracked.

### With DPEFE active inference (PP-351 rescue)

The DPEFE-H2 fix for goal_reach (active_inference_goal_gap_2x drill, 2026-06-11) provided the
validated iterative refinement loop. Path 18 is a direct application: replace the goal_reach
quality prior with a text-quality prior (cosine similarity to a style prototype). The prior drill
validated the loop; Path 18 tests whether the quality prior is adaptable.

### With VSA multi-drive (PP-360)

The multi-drive arbitration (PP-360 VSA-H3 validated) was designed for navigating a 2D gridworld.
Path 16 asks whether the same architecture can drive narrative beat selection. The abstraction
gap is significant: gridworld drives are spatial (approach-goal, avoid-obstacle); narrative
drives are temporal-structural (setup-complication-resolution). This is a structural analogy that
requires validation, not assumption.

### With hierarchical composition (PP-275 and v3.0 cliff)

The v3.0 compositional cliff crossed (L5 recall 0.000 -> 1.000 via cascading cleanup) establishes
that the substrate can handle hierarchical composition up to depth L5+. For creative generation,
this means: Path 17 (memory recombination via 2-hop heteroassoc) is operating well within the
validated compositional depth. Path 16 (3-act narrative) requires only depth-3 structure (3 beat
types composed in sequence). Both are within the v3.0 validated regime.

### With n-gram generation (wave14d_generation_v2_K16)

The wave14d result (p1=43.3% vs Markov B3=27.8%) established the empirical floor. All 13 paths
in this drill are ABOVE the wave14d floor in terms of mechanism sophistication. The question is
whether any of them produce a qualitative jump rather than incremental improvement on the same
autoregressive n-gram mechanism. Paths 11, 12, 17, and 18 are the qualitative jumps. Paths 13,
14, 15, 20, 23 are improvements on the existing mechanism.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **If Path 11 HARD_PASS (DREAMING for creative generation):** the "substrate as creative engine"
   product narrative becomes empirically grounded. A demo showcasing: "feed your KB into the
   substrate, run DREAMING overnight, wake up to a collection of creative story fragments derived
   from your KB." This is the first genuinely differentiating creative product claim.

2. **If Path 18 HARD_PASS (iterative DPEFE text refinement):** the product claim shifts from
   "substrate stores and retrieves" to "substrate writes toward a goal." This is the minimal
   coherent alternative to prompt-engineering: instead of telling an LLM what style to use, you
   provide a substrate style prototype and the system refines iteratively. Fully auditable.

3. **If Path 12 HARD_PASS (cross-domain metaphor generation):** the product demo becomes:
   "enter two domain seeds, substrate generates cross-domain metaphors." This is a distinct
   creative-tool application with no direct LLM equivalent (LLM metaphors are probabilistic;
   substrate metaphors come from specific stored concepts with traceable provenance).

4. **If ALL Tier 1 paths HARD_FAIL:** the honest product framing is: substrate = best-in-class
   structured generation and KB-grounded retrieval; creative generation is shipped via LLM-hybrid
   (Path 10 from prior drill); the substrate's value in the hybrid is provenance + auditability
   + categorical non-hallucination for KB-grounded slots. This is still a strong product story.

5. **Timing implication:** Path 11 (Phase 0, 30 minutes) should be run BEFORE the next exp_dev
   cycle that touches creative generation anchors. It is the cheapest gate for a significant
   set of subsequent decisions.

---

## CITATIONS (verified)

1. Stickgold, R. (2005). "Sleep-dependent memory consolidation." Nature 437:1272-1278.
   [Sleep replay and creative insight -- biological analog to Path 11 DREAMING]
2. Cai, D.J., Mednick, S.A., Harrison, E.M., Kanady, J.C., Mednick, S.C. (2009). "REM, not
   incubation, improves creativity by priming associative networks." PNAS 106:10130-10134.
   [REM as stochastic recombination; Path 11 DREAMING + Path 14 tunneling biological ground]
3. Fauconnier, G. & Turner, M. (2002). "The Way We Think: Conceptual Blending and the Mind's
   Hidden Complexities." Basic Books. [Mental space blending; Path 12 SLIPNET cross-domain]
4. Gentner, D. (1983). "Structure-mapping: A theoretical framework for analogy." Cognitive
   Science 7:155-170. [Structure-Mapping Engine; Path 17 memory recombination]
5. Hofstadter, D. & Mitchell, M. (1994). "The Copycat project: A model of mental fluidity and
   analogy-making." In Advances in Connectionist and Neural Computation Theory Vol 2.
   [Analogy as core of creativity; Path 12 and Path 17 theoretical ground]
6. Beaty, R.E., Benedek, M., Silvia, P.J., Schacter, D.L. (2016). "Creative cognition and brain
   network dynamics." Trends in Cognitive Sciences 20:87-95. [Default mode + executive network
   for creativity; biological analog to DPEFE iterative refinement Path 18]
7. Jung, R.E., Mead, B.S., Carrasco, J., Flores, R.A. (2013). "The structure of creative
   cognition in the human brain." Frontiers in Human Neuroscience 7:330.
   [Divergent+convergent thinking; Path 20 competitive author beam]
8. Mann, S. & Cadman, R. (2014). "Does being bored make us more creative?" Creativity Research
   Journal 26:165-173. [Experimental boredom-creativity link; Path 15]
9. Schultz, W. (1997). "A neural substrate of prediction and reward." Science 275:1593-1599.
   [Reward-modulated Hebbian learning; biological basis for Path 19 preference learning]
10. Geman, S. & Geman, D. (1984). "Stochastic relaxation, Gibbs distributions, and the Bayesian
    restoration of images." IEEE TPAMI 6:721-741. [Simulated annealing convergence; Path 23]
11. Koppel, M., Schler, J., Argamon, S. (2009). "Computational methods in authorship attribution."
    JASIST 60:9-26. [Style separability in function word frequencies; Path 21]
12. Hobson, J.A. (2009). "REM sleep and dreaming: towards a theory of protoconsciousness."
    Nature Reviews Neuroscience 10:803-813. [Dream function in cognitive reorganization; Path 11]

Citations verified: 12

---

## SUMMARY TABLE: 13 PATHS RANKED

| Path | Name | P_deflated | Phase | Cost | Novel? | Trigger for Tier 3 |
|------|------|-----------|-------|------|--------|---------------------|
| 11 | DREAMING replay | 0.42 | Phase 0 | 30min CPU | YES | Run first |
| 18 | Iterative DPEFE | 0.38 | Phase 1 | 3h CPU | YES | After Path 11 |
| 12 | SLIPNET cross-domain | 0.38 | Phase 1 | 1h CPU | YES | Gate on rescue verdict |
| 21 | Style transfer | 0.35 | Phase 1 | 2h CPU | NO | After Tier 1 |
| 17 | Memory recombination | 0.35 | Phase 1 | 2h CPU | YES | After Path 11 |
| 23 | Temp schedule | 0.36 | Phase 0 | 1h CPU | NO | Run alongside Tier 1 |
| 13 | Big-N variety | 0.40 | Phase 1 | 2h CPU | NO | If diversity gap found |
| 15 | Boredom vocabulary | 0.32 | Phase 2 | 2h CPU | NO | If vocab flat |
| 16 | Multi-drive arc | 0.30 | Phase 2 | 3h CPU | NO | If DPEFE shows drive gap |
| 20 | Competitive beam | 0.28 | Phase 2 | 2h CPU | NO | Improvement layer |
| 14 | Frustration tunnel | 0.28 | Phase 2 | 2h CPU | NO | If attractor collapse |
| 22 | Latent interpolation | 0.25 | Phase 2 | 1h CPU | NO | If recombination fails |
| 19 | Preference learning | 0.22 | Phase 3 | 4h CPU | NO | Only on targeted quality gap |

Overall P_deflated for at least one substrate-only path achieving "genuinely surprising to a
human rater" creative output: 0.47 (at least one of Path 11/12/17/18 HARD_PASS).

Overall P_deflated for substrate-only matching LLM-grade creative text: 0.15 (after calibration;
the fundamental distributional texture gap is real).

Next-drill candidate: if Path 11 HARD_PASS, drill into DREAMING with GUIDED probes (narrative
seeds rather than random noise) to move from "creative fragments" to "coherent story outlines."
