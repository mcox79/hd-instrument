# Research: the ingestion valve -- what the brain consolidates vs lets fade (3x drill)

Filed by: research (Opus synthesis over 3 parallel Sonnet lit-scan sub-agents).
Trigger: self-drive thread following the 07-20 accounting/synthesis arc. The ACCOUNTING doc
(item 21, "Attention / selective gating") flags a TOTAL GAP -- substrate processes all ingested
input uniformly, no selection layer -- and separately flags "Consolidation / schema-extraction
replay" as PARTIAL (anti-forgetting random-replay exists; schema-EXTRACTION is a total gap).
This drill grounds a buildable ingestion-selection component on top of the substrate's EXISTING
self-monitoring signals (surprise=IDF family, schema-fit, reliability, coherence, recurrence) +
the learned codebook (concept store, chain-graded).

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates are DEFLATED 0.15-0.25 from the raw
sub-agent reads, and novel-synthesis P is capped at 0.50. Per [[feedback-dont-dismiss-adjacent-methods]]:
machine-learning continual-learning literature (PER/MIR/GEM, active-learning evaluation, curiosity/
noisy-TV) is treated as a load-bearing computational ANALOGY, never as neuroscience evidence, and
flagged as such throughout -- consistent with [[feedback-mechanism-analog-is-not-task-analog]].

---

## HEADLINE

The brain's "what to consolidate" decision is not one signal but a **branching, gain-modulated
combination of at least five distinguishable drivers** (prediction-error/novelty, schema-fit,
importance/reward-relevance, emotional/arousal salience, and retrieval-effort/spacing), and the
literature's single most load-bearing, convergent, and actionable lesson for a buildable gate is:
**raw novelty/surprise must be gated by reducibility (is this passage's unfamiliarity something
more data would resolve, or is it just noise?), and static/frequency-style tags reliably LOSE to
model-state-relative signals whenever the two are directly compared** -- both in the neuroscience
(hippocampal novelty = CA1 mismatch against a *current* prediction, not corpus rarity) and, more
sharply, in machine-learning continual-learning literature that has RUN the direct comparison
(Aljundi et al. 2019 MIR beats Schaul et al. 2015 PER's stored-tag approach; the entire
curiosity/"noisy-TV" literature exists because raw-surprise-without-reducibility fixates on
noise). **This is not a new finding for this project** -- the substrate's OWN prior experiment
(wave14b/c, R7, 2026-05-19) already demonstrated exactly this pattern in-house: static
concept-tagged replay LOST to loss/interference-based dynamic selection by 0.53 bpc on BWT. The
present substrate's "surprise" signal is IMPLEMENTED AS IDF -- a static, corpus-level frequency
statistic, structurally the same *kind* of signal (a fixed tag) that both the R7 negative and the
PER-vs-MIR ML literature show is the weaker approach whenever a truly dynamic alternative is
available. **This is the single highest risk to flag before building anything**, not a reason to
abandon the surprise signal (it is still a legitimate, cheap, partially-correct proxy -- rarity does
correlate with informativeness on average -- just a known-weaker one that must not be trusted alone
or trusted to resist a frequency-confound must-fail control).

A combined-signal ingestion-valve gate, built ENTIRELY from already-existing substrate signals
(no new architecture) plus the codebook, is **brain-faithful in mechanism** (deflated P ~0.55 that
the mechanism-class mapping is sound) and the design below is **tractable as a real, non-injected,
can-fail test** using corpora already partially sourced by a same-day companion drill
(research_brain_source_independence_monitoring). Deflated P that a first, honestly-designed cell
HARD-PASSES: **~0.30** (capped per novel-synthesis rule, pulled down further because the weakest
of the five signals -- surprise=IDF -- is precisely the one most exposed to the frequency-confound
trap this drill surfaces, and because the arc's track record this cycle is dominated by clean
nulls on adjacent self-supervised composition claims).

---

## (1) THE SELECTION SIGNALS -- what determines consolidation, and how do they combine

### The five (at least) distinguishable drivers

1. **Prediction-error / novelty**, via the hippocampal-VTA dopaminergic loop (Lisman & Grace 2005,
   *Neuron*, canonical) -- CA1 detects mismatch between CA3-predicted and actual input; the
   mismatch signal is relayed through subiculum/accumbens/VTA and dopamine returns to facilitate
   hippocampal LTP. This is genuinely a **prediction-error** signal (relative to the system's OWN
   current model), not raw statistical rarity. Barron, Auksztulewicz & Friston (2020, *Prog.
   Neurobiol.*) give the standard predictive-coding synthesis: encoding/consolidation is precision-
   weighted prediction-error minimization. A 2019 direct empirical dissociation (PMC9542624)
   found *expected* novelty (anticipated-but-irrelevant novel stimuli) has no consistent memory
   benefit -- novelty's boost is conditional on genuine, unanticipated model mismatch, not mere
   unfamiliarity. Duszkiewicz, McNamara, Takeuchi & Genzel (2019, *Trends Neurosci.*, canonical-
   recent synthesis) further bifurcate this into "common novelty" (schema-related, VTA/dopamine
   route, assimilates) vs "distinct novelty" (schema-unrelated, locus-coeruleus/noradrenergic
   route, produces vivid-but-encapsulated traces) -- directly relevant to signal 2 below.

2. **Schema-fit / connection to prior knowledge.** Tse et al. (2007, 2011, *Science*, canonical
   within its rodent paradigm) showed schema-CONGRUENT new learning consolidates in ~24-48h
   instead of the normal weeks-long systems-consolidation timeline, via a fast mPFC-mediated route.
   But schema-INCONGRUENT (violating) material also gets a boost -- via a DIFFERENT (MTL/
   hippocampal, richly-detailed) route. van Kesteren, Ruiter, Fernandez & Henson's SLIMM model
   (2012, *Trends Neurosci.*, canonical integrative account) resolves this as a **U-shaped, non-
   monotonic function**: highly congruent -> fast cortical integration; highly incongruent ->
   rich MTL "snapshot" encoding; moderately-novel/ambiguous material is the WORST remembered of the
   three regimes (empirically confirmed, Quent, Greve & Henson 2022, *Psych. Science*). Gilboa &
   Marlatte (2017, *Trends Cogn. Sci.*, canonical review) add that a genuine schema is, by
   definition, "adaptable" -- able to rapidly and non-disruptively absorb congruent new instances --
   which is the schema-fit signal's core function: LOW interference risk when congruent.

3. **Importance / goal-relevance / reward-salience**, a signal DISSOCIABLE from both of the above.
   Adcock, Thangavel, Whitfield-Gabrieli, Knutson & Gabrieli (2006, *Neuron*, canonical landmark)
   showed reward-cue anticipation (BEFORE the to-be-remembered item even appears) drives VTA-
   hippocampal coupling that predicts 24h memory -- i.e. goal-relevance acts PROSPECTIVELY, sharing
   the same dopaminergic gate as novelty (signal 1), not an independent additive channel.
   Wittmann et al.'s "enriched encoding" work shows reward and novelty explicitly INTERACT (reward
   context amplifies novelty detection), not sum. Value-directed remembering (Castel and
   colleagues; Middlebrooks, Kerr & Castel 2022, *Annu. Rev. Psychol.*, canonical review) shows a
   separate, more STRATEGIC/metacognitively-guided allocation of encoding effort toward explicitly
   high-value items, selectively impaired in Alzheimer's -- dissociating "I know this matters" from
   automatic novelty/reward gating.

4. **Emotional/arousal salience** -- McGaugh's modulation-of-consolidation theory (canonical,
   decades of causal pharmacological evidence: propranolol blocks emotional-memory enhancement
   without blocking the memory itself; amygdala lesions abolish it). This is one of the most
   solid, causally-validated mechanisms in the whole field. But Kensinger's program (canonical,
   well-replicated) shows arousal does NOT uniformly enhance memory -- it NARROWS resources to
   central/emotionally-relevant detail at the cost of peripheral detail, and biases negative
   emotion toward perceptual specifics vs positive emotion toward gist. Mather & Sutherland's
   arousal-biased-competition model (2011, *Perspect. Psychol. Sci.*, well-regarded integrative
   account) formalizes this as **multiplicative gain on whatever ALREADY has priority** -- arousal
   amplifies existing winners, doesn't add a flat bonus.

5. **Desirable difficulty / testing-retrieval effect / spacing** -- Bjork's desirable-difficulty
   framework (1994, canonical umbrella theory); Roediger & Karpicke's testing effect (2006,
   extremely well-replicated: retrieval practice beats restudying for LONG-term retention despite
   feeling worse at the time -- a genuine dissociation between subjective fluency and durable
   storage strength); Cepeda et al.'s spacing meta-analysis (2006, *Psych. Bull.*, canonical,
   839 assessments, near-undisputed at the behavioral level, with optimal spacing scaling with
   desired retention interval). These operate on a **temporal-distribution axis largely orthogonal**
   to signals 1-4 -- they modulate HOW STRONGLY a given exposure counts, not WHICH content is
   worth consolidating in the first place. The mechanistic link from testing/spacing to the
   dopaminergic/tagging substrates of signals 1-4 is genuinely under-specified in the literature --
   flagged as a real gap, not filled in by inference.

### How they combine -- the honest answer is: no single validated formal equation, but a strong,
convergent constraint on the SHAPE

There is no paper that gives one unified combination equation across all five signals -- this is
a genuine, explicitly-flagged open synthesis problem in the literature, not something to pretend
is solved. But several strong, convergent constraints rule out the naive options:

- **Pure OR-gating (any one signal suffices) is wrong.** Synaptic tagging and capture (Frey &
  Morris 1997/1998, *Nature*; Redondo & Morris 2011, *Nat. Rev. Neurosci.*, canonical) and
  behavioral tagging (Moncada & Viola 2007) both show a weak/inconsequential trace becomes durable
  ONLY if a temporally-proximal salient/novel event supplies a "tag" -- novelty/salience ALONE,
  without something worth tagging, produces nothing durable. And "expectation of irrelevant novel
  stimuli has no consistent effect on recognition memory" (PMC9542624) directly shows novelty
  without relevance is inconsistent/weak.
- **Pure AND-gating (all signals required) is also wrong.** Reward can RETROACTIVELY rescue
  temporally-adjacent mundane material that was independently neither novel nor important at
  encoding time (Science Advances, "Salient experiences enhance mundane memories through graded
  prioritization") -- a graded, WINDOW-OPENING structure, not a strict conjunction.
- **The best-supported shape is GATED/MULTIPLICATIVE, with novelty and reward sharing one
  dopaminergic gate that a second signal (arousal, schema-fit direction) MODULATES the gain of.**
  Mather & Sutherland's arousal-biased-competition model is the clearest formally-worked-out
  instance: arousal multiplies whatever priority already exists, rather than adding independently.
  Duszkiewicz et al.'s two-pathway split (common-novelty/dopamine vs distinct-novelty/
  noradrenergic) is a BRANCHING structure gated by schema-relatedness, not a sum.
- **Adjacent computational literature (analogy, not neuroscience) sharpens this further: the
  correct combination is "surprise GATED by reducibility/learnability," not "surprise AND
  relevance" as independent additive terms.** The curiosity-driven-RL "noisy TV" problem (Burda
  et al. 2018/2019 ICLR) is the clean demonstration: prediction-error-driven attention fixates on
  irreducible (aleatoric) stochasticity forever, because raw surprise never distinguishes "will
  get better with more data" (epistemic, worth attending) from "will never get better" (pure
  noise). The fix (Mavor-Parker et al. 2022, ICML; Oudeyer & Kaplan's original learning-progress
  framework, 2007) is to explicitly require a DECREASING-with-exposure trajectory, not a raw
  magnitude. Feldman & Friston's precision-weighting (2010, *Front. Hum. Neurosci.*) is the
  matching neuroscience-side formalism: signals combine via precision (reliability) acting as a
  multiplicative GAIN on a prediction-error term, exactly the sensor-fusion form (unreliable-but-
  surprising should be discounted, not summed in at face value).

### The conflict cases, explicitly

- **Surprising-but-irrelevant**: the tagging/capture conditionality literature plus the
  "expectation-of-irrelevant-novelty has no consistent effect" null converge on: this fails to
  consolidate durably UNLESS paired with something else that supplies relevance/tag -- it is a
  triangulated, multiply-converging pattern, not one single clean confirmatory study (the sub-agent
  flagged this honestly -- no paper is titled exactly "surprising-irrelevant items are forgotten").
- **Expected-but-important (dull-but-important) is the brain's best-documented FAILURE MODE.**
  Flashbulb-memory literature (Neisser & Harsch 1992; Talarico & Rubin 2003, *Psych. Science*,
  canonical) shows CONFIDENCE/vividness dissociates from OBJECTIVE ACCURACY -- emotionally vivid
  material is remembered with high confidence but decays in accuracy at the SAME rate as ordinary
  material. Talmi & Daw's retrieved-context model formalizes emotional arousal's immediate
  (attentional) and delayed (consolidation) effects as only weakly correlated, i.e. "feels
  important" and "durably consolidated" are NOT the same axis mechanistically. This is the direct
  analog of the design risk flagged in the HEADLINE: a text-ingestion valve that over-weights
  surface-salient (rare-token, distinctively-worded) material over dull-but-corroborated,
  frequently-repeated factual content would be reproducing this exact, well-documented human
  failure mode -- not a hypothetical risk, a REPLICATED one.

### Load-bearing vs auxiliary (deflated ranking from the lit-scan)

**Tier 1 (load-bearing, strong convergent evidence):** novelty/prediction-error via
hippocampal-dopaminergic gating; reward/goal-relevance sharing that same gate; emotional/arousal
modulation via amygdala-noradrenergic action (decades of causal pharmacological evidence); testing
effect + spacing (extremely robust behaviorally, acting as amplifiers largely orthogonal to the
content-selection signals). **Tier 2 (load-bearing but nonmonotonic/qualified):** schema-fit
(U-shaped per SLIMM, not simply "more congruence = more consolidation"); arousal-biased
gain-amplification as the best current FORMAL combination account. **Tier 3 (auxiliary/
modulatory):** distinctiveness/von Restorff (likely subsumed under novelty/schema-violation);
synaptic tagging (explains HOW, not WHAT, to select); gist/central-peripheral narrowing under
emotion (a corrective constraint, not a trigger signal).

---

## (2) THE CONSOLIDATION MECHANISM -- fast capture, slow integration, gist vs specifics, and what
counts as "reshaping" vs "just another episode"

**Complementary Learning Systems (McClelland, McNaughton & O'Reilly 1995, *Psych. Review*,
canonical foundation).** Two systems are needed because ONE cannot satisfy both: rapid one-shot
acquisition of arbitrary new information (needs sparse, pattern-separated, minimal-interference
encoding) and extraction of shared statistical structure across many experiences (needs dense,
overlapping, slow-learning representations). A single dense network updated fast on individual
items produces catastrophic interference (McCloskey & Cohen 1989; Ratcliff 1990). Hippocampus =
fast/sparse/pattern-separated; neocortex = slow/dense/overlapping; transfer = replay, INTERLEAVED
with old material, which is the specific mechanism that avoids catastrophic interference in
simulation (a well-replicated computational result, O'Reilly et al. tradition). Kumaran, Hassabis
& McClelland's 2016 update (*Trends Cogn. Sci.*) explicitly imports reward/novelty-MODULATED
replay (not just uniform interleaving) and anticipates the schema-graded assimilation-without-
full-interleaving case (point below).

**Prioritized replay -- Mattar & Daw 2018 (*Nat. Neurosci.*, "need x gain") is EXPLICITLY
SCOPE-LIMITED to sequential decision-making/spatial-navigation/planning, not a general theory of
semantic/declarative consolidation** -- this scope limit is stated directly by reviewers (a 2022
*J. Neurophysiol.* review, an eLife 2024/25 unifying-replay paper), not inferred here. What IS
directly comparable to our design question -- static vs dynamic replay-selection -- is best
resolved in the machine-learning continual-learning literature, where the comparison has actually
been RUN: Prioritized Experience Replay (Schaul et al. 2015, a stored/lazily-updated per-item TD-
error tag) is beaten by Maximally Interfered Retrieval (Aljundi et al. 2019, NeurIPS -- selection
computed relative to the SPECIFIC incoming update's foreseeable damage) and by Gradient Episodic
Memory's gradient-conflict criterion (Lopez-Paz & Ranzato 2017). **This exact pattern -- dynamic,
current-model-state-relative selection beating static/stored tags -- is precisely what our OWN
in-house R7 experiment (wave14b/c) already found**: static concept-tagged replay lost to random/
loss-based dynamic replay by 0.53 bpc BWT. Sharp-wave-ripple biology (Foster & Wilson 2006;
Ambrose, Pfeiffer & Foster 2016, *Neuron*) shows replay content IS reward/novelty-biased at
encoding time (a real "tag" exists) but ALSO tracks *updated*, revalued information later (a 2019
*Nat. Neurosci.* reward-revaluation study) -- i.e. biology plausibly runs BOTH an encoding-time tag
and a retrieval-time dynamic reweighting, not purely one or the other. This is the one place the
ML literature is more decisive than the neuroscience literature on this specific question, and is
flagged explicitly as such.

**Gist vs specifics.** Fuzzy-Trace Theory (Brainerd & Reyna, canonical, decades of DRM/false-
memory replication) posits parallel verbatim (fast-decaying) and gist (slow-decaying) traces from
the SAME experience. Schapiro, Kustner & Turk-Browne (2012) and Schapiro, Turk-Browne, Botvinick &
Norman (2017, *Phil. Trans. R. Soc. B*, recent/still-maturing model, but widely cited) show
repeated exposure across MANY instances drives hippocampal (and MTL) representations to reorganize
toward abstracted community/structural regularities, at the expense of idiosyncratic single-
instance detail -- i.e. **repetition-across-many-exposures is what drives gist extraction**,
while a single, highly salient, distinctive episode favors specific retention. Three independent
literatures (behavioral/FTT, hippocampal statistical-learning, computational/CLS) converge on the
same qualitative principle.

**Assimilation vs accommodation vs mere episodic storage -- a genuine three-way branch, not a
binary.** Tse et al. (2007/2011, canonical within paradigm): schema-CONGRUENT new learning
consolidates fast via a prelimbic-mPFC route -- assimilation, low interference, the new instance
just "slots in." Ghosh & Gilboa's (2014, *Neuropsychologia*, influential conceptual review)
four defining schema properties include "adaptable" -- the capacity to absorb congruent new
information without disruption is part of the DEFINITION of a schema. But schema-INCONGRUENT
material triggers a genuine FORK (Bein/Davachi-adjacent synthesis, *Neurosci. Biobehav. Rev.* 2023;
Duncan/Schapiro "Mnemonic prediction errors bias hippocampal states," *Nat. Commun.* 2020;
"Prediction errors disrupt hippocampal representations and update episodic memories," *PNAS*
2021/22): moderate, registered-as-informative prediction error can drive genuine ACCOMMODATION
(the schema/structure itself updates) -- OR the same prediction error can instead produce
SEPARATION (an encapsulated, isolated new episode that leaves the existing schema untouched, if
the mismatch is treated as an exception rather than a generalizable correction). This is flagged
explicitly as a RECENT (last ~5 years), actively-developing research area, not decades-settled
canon like the core CLS claim.

**What actually discriminates "reshaped my knowledge" from "just an episode"?** No single clean
neuroscience marker exists (honestly, per the lit-scan). The best-supported answer is a
CONJUNCTION of three correlated markers, none individually sufficient: (a) schema-congruence at
encoding (high congruence -> low-risk assimilation), (b) prediction-error magnitude MEDIATED by a
hippocampal encode-vs-protect mode switch (moderate, informative PE -> accommodation; can also ->
separation depending on context), (c) subsequent replay/sleep "dosage" over time (CLS's
interleaving story -- genuine cortical reshaping requires sustained offline replay, not a single
encoding moment). Elastic Weight Consolidation (Kirkpatrick et al. 2017, *PNAS*) is flagged
explicitly as a machine-learning ENGINEERING analogy for "protecting important synapses," itself
contested even as pure ML (Huszar's 2018 PNAS commentary), and LESS faithful to the actual CLS
biology than replay-based methods (GEM/MIR) -- worth noting because EWC is the most commonly-cited
"neuro-inspired" ML method despite being the less faithful analogy.

---

## (3) DESIGN + A CAN-FAIL TEST for a first ingestion-valve cell

### Mapping the literature onto the substrate's existing five signals

| Substrate signal (as currently built) | Literature correspondence | Discrepancy / risk flagged |
|---|---|---|
| **surprise = IDF family** | Novelty/prediction-error (Lisman-Grace, Barron-Friston) | **IDF is a STATIC corpus-frequency statistic, not a model-state-relative prediction error.** This is exactly the "static tag" pattern the R7 negative and the PER-vs-MIR ML literature show LOSES to dynamic, current-model-relative alternatives. Highest-risk signal in the stack. |
| **schema-fit** | Tse/SLIMM schema-congruence | Real signal-class match, but literature says the relationship is U-SHAPED (van Kesteren et al. 2012), not monotonic -- a naive "higher schema-fit = more consolidation" scoring would misrepresent the brain's own function here. |
| **reliability** | Precision-weighting (Feldman-Friston), value-directed remembering, source-monitoring (companion drill: research_brain_source_independence_monitoring) | Matches the "precision as multiplicative gain" formalism cleanly -- the best-grounded signal in the stack. |
| **coherence** | Kintsch CI settling-residual (companion drill: research_brain_settle_to_coherence_parse_selection); noisy-TV epistemic-vs-aleatoric distinction (Mavor-Parker 2022) | Directly maps to the reducibility gate the curiosity literature says surprise MUST be conditioned on: incoherent (non-settling) high-surprise text = noise (aleatoric), coherent high-surprise text = genuine schema-violation worth encoding (epistemic). **Coherence is the mechanism that keeps surprise honest.** |
| **recurrence** | Spacing/repetition (Cepeda), statistical-learning gist-extraction (Schapiro) -- BUT ALSO the illusory-truth/source-independence failure mode (companion drill, same day) | **Raw recurrence-count is a known brain FAILURE MODE if not source-independence-gated**: humans have no default competence for discounting repetition-from-the-same-origin as independent corroboration (illusory truth). A naive recurrence signal would reproduce this exact bias. Must be paired with the existing common-mode detector (atom 29378) so recurrence only counts INDEPENDENTLY-SOURCED repetition. |

### The combined gate (branching, not additive, per the literature's convergent shape)

Mirroring the SLIMM/Duszkiewicz branching-pathway structure and the precision-weighted-gain
formalism, NOT a flat weighted sum:

1. **Reject / let fade** if: reliability is low, OR (surprise is high AND coherence is low --
   the noisy-TV/aleatoric case: unfamiliar-looking text that doesn't settle to a stable parse is
   noise, not signal), OR recurrence is high but common-mode-detector-flagged as non-independent
   (the illusory-truth case: many copies of the same one source, not real corroboration).
2. **Strong consolidation / gist-reinforcement (assimilation pathway)** if: schema-fit is high
   AND reliability is high AND recurrence is high AND common-mode-detector-confirmed independent
   (multiple genuinely different sources corroborate it) -- this is precisely the "expected-but-
   important" bucket the brain systematically UNDER-serves (per the flashbulb/Talarico-Rubin
   literature); a well-designed valve should PROTECT this bucket explicitly rather than let a loud
   surprise signal starve it of resources.
3. **Flag as accommodation / new-concept-atom candidate** if: schema-fit is low/moderate AND
   surprise is high AND coherence is high (settles cleanly despite being unexpected -- a real,
   parseable, structured departure from the existing codebook, not garbage) AND reliability is
   high.
4. **Default (weak/no consolidation)**: everything else -- most notably schema-fit high but
   reliability low (plausible-sounding but unreliable), which is the version of "surprising-but-
   irrelevant" this text-ingestion setting actually produces.

### Cheap decisive test

Reuse the EXACT held-out target already validated non-construction-determined for the codebook:
word-similarity/analogy generalization AUC (wordsim353/simlex999-style references never used to
build codes), on the STEP1 RI/PPMI+SVD codebook-build pipeline (existing 0.927 ungated baseline,
VET-confirmed genuine generalization). This choice is consistent with, and reuses infrastructure
from, the same-day confidence-weighted-learning-consolidation note's recommended target -- do NOT
invent a new metric.

**Corpus construction (real, not injected):**
- "Worth consolidating" candidate pool: a diverse real reference corpus (distinct topics/sources).
- "Noise/redundant" arm: reuse the wire-dedup / PAN-plagiarism-style near-duplicate corpus and the
  MRPC/Turku paraphrase corpus already sourced by the same-day companion drill
  (research_brain_source_independence_monitoring) as the non-independent-repetition stress case.
- "Unreliable" arm: a fact-checking corpus with known-false or low-quality claims (e.g. FEVER/LIAR-
  style), for the reliability-signal discriminator.
- "Incoherent" arm: sentence-order-scrambled and word-order-scrambled versions of the SAME real
  passages, preserving lexical/frequency statistics exactly -- this is the direct must-fail probe
  for the coherence signal and for the IDF-surprise-confound risk simultaneously (scrambling
  destroys structure/coherence but NOT token frequency, so it isolates whether the gate is doing
  anything beyond frequency-matching).

**Arms:** (a) ungated "consolidate everything" baseline (uniform weight, same architecture/corpus/
order -- only the per-item weight differs, per the design-gate discipline); (b) combined 5-signal
gate; (c) surprise-IDF-alone gate (isolates whether the weakest, static-tag signal is secretly
doing all the work); (d) reliability-alone gate; (e) shuffled-signal control (permute each
signal's score across items); (f) inverted-gate control (deliberately weight the noise/unreliable/
non-independent-recurrence arms MORE -- the explicit "must be able to hurt" probe); (g) scrambled-
text control (feed (b)'s gate the word/sentence-scrambled corpus, confirm coherence collapses and
the gate correctly down-weights it).

### Falsifiable predictions

**HARD-PASS** (all required, pre-registered, >=3 seeds):
- Combined 5-signal gate beats the ungated baseline on held-out AUC by a non-trivial, seed-
  consistent margin (baseline is near-ceiling at 0.927; use effect-size + seed consistency, not a
  fixed percent, per the confidence-weighted-learning note's precedent).
- Combined gate beats BOTH single-signal ablations (c) and (d) -- i.e. the combination earns its
  keep beyond any one signal alone, specifically ruling out "IDF was doing all the work."
- Shuffled-signal control (e) collapses to indistinguishable from ungated baseline.
- Inverted-gate control (f) significantly UNDERPERFORMS both ungated and the real gate.
- Scrambled-text control (g): the coherence sub-signal specifically must show near-zero settling/
  high incoherence on scrambled input, and the full gate must down-weight scrambled text relative
  to its unscrambled counterpart at matched token-frequency statistics.
- Common-mode-detector-gated recurrence outperforms raw-recurrence-count on the illusory-truth
  stress arm (multiplicity-injected non-independent repeats correctly discounted).

**HARD-FAIL** (any one kills the candidate):
- Combined gate performs within noise of ungated baseline (no real lift) -- plausible GIVEN that
  the confidence-weighted-learning note's structurally similar cell (S1-gating a different
  consolidation step, same held-out metric) already flagged this as the MOST LIKELY outcome for a
  gate composing existing bounded signals against a near-ceiling baseline.
- Combined gate loses to the surprise-IDF-alone ablation (proves the other four signals add
  nothing, or worse, actively dilute IDF's real-but-weak contribution).
- Combined gate wins ONLY on the unscrambled corpus and shows no real discrimination on the
  scrambled must-fail arm at matched frequency statistics (proves the apparent win is a frequency-
  confound artifact, not genuine coherence/structure detection -- this is the SPECIFIC operational
  form of the top-flagged risk and must be checked FIRST, before any other analysis, per the
  Ojala-Garriga permutation-test precedent).
- Raw-recurrence-count performs comparably to common-mode-gated recurrence on the illusory-truth
  stress arm (proves the recurrence signal has not actually been protected from the illusory-truth
  failure mode it was designed to guard against).
- Any of the five signals is degenerate/saturated on the real corpus (design-gate failure, kill
  before full run).

### Construction-determinism guards (mandatory, pre-registered before any full run)

1. Frequency/length confound check FIRST (scrambled-corpus arm, matched token statistics) --
   given this drill's own headline finding that the weakest signal in the stack (IDF) is exactly a
   frequency statistic, this is the single most important guard, not a generic afterthought.
2. Fair ungated baseline: identical architecture/corpus/order, only the per-item weight differs.
3. All four must-fail controls (shuffled-signal, inverted-gate, scrambled-text, raw-vs-gated-
   recurrence) required, not optional -- each targets a DIFFERENT, literature-specific failure
   mode (generic-regularization artifact; miscalibration-can't-hurt; noisy-TV/aleatoric fixation;
   illusory-truth).
4. No signal may be retuned/recalibrated against this task's own held-out labels -- every signal
   used exactly as already built/trained elsewhere (same discipline as the confidence-weighted-
   learning note's guard #1).
5. Distributional precondition check on all five signals before any full run.
6. Monotone dose-response is NOT expected to be simply "stricter = always better" here (unlike the
   simpler single-signal cases in prior notes) -- the schema-fit literature's own U-shape and the
   learning-progress literature's inverted-U both predict a real ceiling/degradation at excessive
   strictness (an empty or near-empty codebook trivially can't be "wrong" but also can't be
   useful). A strictness sweep that improves monotonically with NO ceiling is itself a
   construction-determinism red flag, not a clean win -- pre-register a companion COVERAGE metric
   (fraction of real corpus retained) alongside the quality metric.

---

## Cross-thread synthesis

This drill sits directly on three same-day companion drills and one older in-house negative,
and the connections are load-bearing, not decorative:

- **wave14b/c R7 (2026-05-19)**: static concept-tagged replay lost to dynamic loss-based selection
  by 0.53 bpc BWT. This drill's headline finding -- that surprise=IDF is structurally the same
  "static tag" pattern -- means R7's negative result is a DIRECT, already-paid-for warning about
  the weakest link in the proposed gate, not a new risk discovered today. The substrate has ALREADY
  tested this exact pattern-class once and it lost.
- **research_brain_confidence_weighted_learning_consolidation_2026-07-20**: the sibling design
  (gate a real consolidation step by a self-generated reliability signal, same held-out codebook
  AUC target, same four-arm must-fail-control template). That note's honest read -- "most likely
  outcome is within-noise-of-baseline against a near-ceiling target" -- applies here with equal or
  greater force, since this gate composes FIVE bounded signals rather than one, raising rather than
  lowering the risk of compounding weak signals into net noise.
- **research_brain_source_independence_monitoring_2026-07-20**: supplies both the illusory-truth
  failure-mode framing for the recurrence signal AND the concrete real-corpus sourcing (wire-dedup/
  PAN/MRPC) reused directly in this design's corpus construction -- avoiding a redundant, separate
  corpus-sourcing effort.
- **research_brain_settle_to_coherence_parse_selection_2026-07-20**: supplies the settling-residual
  operationalization of "coherence," which this drill identifies as the mechanism that keeps the
  surprise signal honest (the reducibility/epistemic-vs-aleatoric gate the curiosity-RL literature
  says is mandatory) -- a genuine cross-drill dependency, not a coincidence of timing.
- **ACCOUNTING_substrate_vs_brain_foundation_discrepancies_2026-07-20** (item 21, attention/
  selective-gating = TOTAL GAP; item labeled "Consolidation/schema-extraction replay" = PARTIAL):
  this drill is the first concrete design proposal that could close BOTH gaps simultaneously with
  a single cell, since the branching gate above IS an attention/selective-gating mechanism whose
  "strong consolidation" pathway also performs schema-extraction (routing corroborated, schema-fit
  material toward gist-reinforcement rather than raw episodic storage).

Credit: this design sketch is entirely an application of existing, credited literatures
(McClelland/McNaughton/O'Reilly CLS; Lisman & Grace; Tse et al.; van Kesteren et al. SLIMM;
Mather & Sutherland; Roediger & Karpicke; Bjork; Cepeda et al.; Feldman & Friston; Itti & Baldi;
Burda et al./Mavor-Parker noisy-TV; Ghorbani & Zou / Koh & Liang data-valuation methodology;
Lüth et al. active-learning fair-evaluation; Ojala & Garriga permutation testing) to an
already-built glass-box mechanism (existing surprise/schema-fit/reliability/coherence/recurrence
signals + the codebook). No claim of novel neuroscience or novel ML method; the only new content
is the specific wiring, mapping table, and guard design for this substrate -- engineering
recombination, not research, consistent with the 07-20 SYNTHESIS finding.

## Substrate-product implications

If a version of this passes (deflated as it is): the product gets a genuine, inspectable "the
system decides what's worth remembering the same way it decides what's worth trusting" capability
-- built entirely from signals already exposed in the glass-box audit trail, with an explicit,
demonstrable defense against the two best-documented human failure modes (over-weighting vivid/
surprising-but-unreliable content; falling for illusory-truth-style repetition-without-independent-
corroboration). That is a concrete, auditable product narrative distinct from "we ingested more
data." If it HARD-FAILs on the frequency-confound check specifically (the single most likely
failure mode per this drill's own headline), it still narrows the problem precisely: it would show
the substrate's CURRENT operationalization of "surprise" (static IDF) is the load-bearing weak
link, redirecting future effort toward replacing IDF with a genuine model-relative prediction-error
signal (matching what the brain literature says is actually used) rather than toward abandoning
the gate concept entirely. Either outcome is informative; this is designed to be able to fail
cleanly and specifically, not to be a foregone demonstration.

## Citations (verified count: 3 independent lit-scan sub-agents, ~45 unique sources cross-checked
via PubMed/Nature/Science/Neuron/PNAS/arXiv/NeurIPS/ICML/ICLR primary-source links; full per-axis
citation lists preserved in the sub-agent transcripts this note synthesizes)

Selection signals (axis 1): Lisman & Grace 2005 *Neuron*; Duszkiewicz et al. 2019 *Trends
Neurosci.*; Barron, Auksztulewicz & Friston 2020 *Prog. Neurobiol.*; Tse et al. 2007/2011
*Science*; van Kesteren et al. 2012 *Trends Neurosci.* (SLIMM); Quent, Greve & Henson 2022
*Psych. Science*; Gilboa & Marlatte 2017 *Trends Cogn. Sci.*; Adcock et al. 2006 *Neuron*;
Wittmann et al. *Cereb. Cortex*-lineage; Middlebrooks, Kerr & Castel 2022 *Annu. Rev. Psychol.*;
McGaugh & Cahill modulation-of-consolidation literature; Kensinger emotion/memory-tradeoff
literature; Mather & Sutherland 2011 *Perspect. Psychol. Sci.*; Bjork 1994; Roediger & Karpicke
2006; Karpicke & Roediger 2007 *JML*; Cepeda et al. 2006 *Psych. Bull.*, 2008 *Psych. Science*;
Frey & Morris 1997 *Nature*; Redondo & Morris 2011 *Nat. Rev. Neurosci.*; Moncada & Viola 2007
*J. Neurosci.*; Neisser & Harsch 1992; Talarico & Rubin 2003 *Psych. Science*; Talmi & Daw
retrieved-context model.

Consolidation mechanism (axis 2): McClelland, McNaughton & O'Reilly 1995 *Psych. Review*;
Kumaran, Hassabis & McClelland 2016 *Trends Cogn. Sci.*; O'Reilly et al. interleaved-learning
tradition; Mattar & Daw 2018 *Nat. Neurosci.*; Foster & Wilson 2006 *Nature*; Ambrose, Pfeiffer &
Foster 2016 *Neuron*; Schaul et al. 2015 (PER); Aljundi et al. 2019 NeurIPS (MIR); Lopez-Paz &
Ranzato 2017 NeurIPS (GEM); Brainerd & Reyna fuzzy-trace theory; Schapiro, Kustner & Turk-Browne
2012; Schapiro, Turk-Browne, Botvinick & Norman 2017 *Phil. Trans. R. Soc. B*; Ghosh & Gilboa 2014
*Neuropsychologia*; Bein/Davachi-adjacent synthesis, *Neurosci. Biobehav. Rev.* 2023; Duncan et
al. 2020 *Nat. Commun.*; PNAS 2021/22 prediction-error/hippocampal-update paper; Kirkpatrick et al.
2017 *PNAS* (EWC, ML analogy, contested even as ML).

Combination models + fair-test methodology (axis 3): Itti & Baldi 2005/2006/2009 (Bayesian
surprise); Itti & Koch 2001 *Nat. Rev. Neurosci.*; Desimone & Duncan 1995 *Annu. Rev. Neurosci.*
(biased competition); Feldman & Friston 2010 *Front. Hum. Neurosci.*; Schmidhuber formal theory of
creativity/curiosity; Oudeyer & Kaplan 2007 (intrinsic-motivation typology); Burda et al.
2018/2019 ICLR (RND, noisy-TV); Mavor-Parker et al. 2022 ICML (aleatoric/epistemic fix); Lüth et
al. 2023 NeurIPS (active-learning evaluation pitfalls); Ghorbani & Zou 2019 ICML (Data Shapley);
Koh & Liang 2017 ICML (influence functions); Cormack & Lynam TREC Spam Track literature; Ojala &
Garriga 2010 *JMLR* (permutation testing).
