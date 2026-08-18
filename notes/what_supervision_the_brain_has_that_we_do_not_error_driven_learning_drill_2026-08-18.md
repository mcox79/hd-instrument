# WHAT DOES THE BRAIN GET TO LEARN FROM THAT WE DO NOT -- AND CAN WE GET IT WITHOUT AN LLM?

**Research drill, 2026-08-18. LEADS WITH BIOLOGY. Authored no cell, ran no experiment, dispatched
nobody.** Deliverable = the per-signal biological account, a PINNED-vs-OUR-INVENTION table, a
can-fail build specification ready for an exp_dev agent, and a brain-framed shelve criterion.

---

## 1. THE ANSWER IN PLAIN LANGUAGE (read this paragraph if you read nothing else)

A child is never handed a list of which words mean the same thing. What a child's brain *does* get,
and what our system does not, is **an error signal: a running comparison between what it expected to
hear next and what it actually heard.** That comparison is doing something our counting is not.
Counting records *which sentences a word turned up in*. Predicting records *what a word leads you to
expect*. Two words that can replace each other lead you to expect the same things even if they never
once appear in the same sentence -- so a system that learns by being wrong about what comes next has
a reason to move them together, while a system that only tallies co-occurrence has no such reason and
in fact has the opposite one: it pulls together the words that shared a sentence, which is exactly
the failure our instrument measures. There is a second, quieter difference that matters just as much:
an error signal carries information about **what did NOT happen** (the thing you expected that did
not arrive), and a tally has no way of recording a non-event at all. **And yes, we can have this
without an LLM.** The mechanism is a two-line arithmetic update -- *add what happened, subtract what
you already predicted* -- run offline over our own corpus, producing a plain table of numbers we can
open and read. No sequence model, no generation, nothing running at read time except a table lookup.
**The honest caveat, and it is a big one:** the published literature says that a properly-tuned
*counting* method matches a *predicting* method on similarity tasks like ours, and the counting
method we ran was the untuned version. So before we conclude "the missing thing is supervision," the
same experiment must run the tuned count method too. If the tuned counter clears the bar, our
diagnosis was wrong and the missing thing was never a learning signal at all.

---

## 2. WHAT LICENSES THIS DRILL, AND ONE CORRECTION TO THE NUMBER THAT LICENSED IT

Off disk, `data/exp_corpus_capacity_ppmi_svd_ceiling_v1/metrics.json` (`run_mode=full`,
`INSTRUMENT_LICENSED=true`, all 8 regression checks at `delta 0.0`, coverage 242/242):

| arm | AUC | band |
|---|---|---|
| `B1_PPMI` | 0.0249 [0.0108, 0.0418] | BELOW |
| `B3_SECOND_ORDER_COSINE` | 0.0510 [0.0335, 0.0708] | BELOW |
| `B2_PPMI_SVD` k=50 / 100 / 300 / 500 | 0.0519 / 0.0285 / 0.0230 / 0.0278 | all BELOW |
| `A0_INCUMBENT` | 0.0710 | BELOW |
| `C1_FITTED_ORACLE` fitted / pair-level CV | 0.9670 / 0.9606 | ABOVE |

**CORRECTION, and it is load-bearing.** The Director reports a group-disjoint recompute of the oracle
at **0.8629**, because 37.6% of pair-member words appear in more than one pair, so the pair-level
5-fold split leaked word identity. **0.8629 is the honest ceiling figure; 0.9606 must not be
re-quoted.** Disclosure: the landed `metrics.json` I read still carries only 0.9670/0.9606 -- the
group-disjoint number is not in that artifact, and the artifact should be amended or a superseding
note filed so the next reader does not pick up the leaked figure.

**Two consequences the rest of this note obeys.** (a) Neither figure is a capability: the oracle is
fitted on the evaluation construct. It says the counts CONTAIN the signal, nothing about what an
unsupervised learner can reach. (b) The 37.6% word-overlap fact means **any arm whose settings are
chosen by looking at these 242 pairs becomes a second oracle.** Every hyperparameter in the build
below is therefore fixed a priori from published defaults, never tuned on the population.

---

## 3. THE FOUR ERROR SIGNALS AVAILABLE TO CORTEX DURING LANGUAGE EXPERIENCE

For each: **what is compared against what**, **what is updated**, **PINNED BY EVIDENCE vs
THEORY-ONLY**, and the published objections. A mechanism here means a neural system, not a
cognitive-theory label.

### 3.1 PREDICTION ERROR against upcoming linguistic input

**Compared:** the neural state elicited *before* a word arrives (a pre-activation of the expected
item) against the state elicited *by* the word that actually arrives. **Updated:** the synaptic
weights carrying the context-to-item mapping, in proportion to the mismatch.

**PINNED BY EVIDENCE:**
- **Cortical cells whose firing scales with mismatch magnitude and that are absent before learning.**
  In mouse V1 layer 2/3, neurons compute a difference between top-down motor-related input and
  bottom-up visual flow; responses scale linearly with the degree of error, the two input streams
  have opposing signs on membrane potential (consistent with a *subtractive* comparison), distinct
  populations behave like positive- and negative-error units, and the responses **emerge only after
  sensorimotor learning**. A dedicated control paper rules out the obvious confound (locomotion-
  induced gain cannot explain them). This is the strongest single piece of "an error is physically
  computed in cortex" evidence, and it is sensorimotor, not linguistic.
- **In human language cortex specifically:** intracranial (ECoG) recordings show neural activity
  *before word onset* carrying context-dependent predictive information about the forthcoming word
  by hundreds of milliseconds, and post-onset activity tracking surprise, across the language
  network with an additional incorrect-word effect in inferior frontal gyrus (Goldstein et al. 2022,
  *Nature Neuroscience*).
- **The N400 graded by cloze probability** is one of the most replicated effects in the field.

**THEORY-ONLY:** that cortex implements *hierarchical predictive coding* in the Rao-Ballard/Friston
sense -- separate error units and representation units assigned to specific laminae, errors as
residuals on a generative model, precision-weighting by neuromodulators. The canonical-microcircuit
assignment is inferred from anatomy plus modelling, not recorded.

**PUBLISHED OBJECTIONS, stated at full strength:**
- **The adaptation account.** A short-term synaptic depression model reproduces both repetition
  adaptation and the mismatch negativity, including cases where adaptation had been claimed ruled
  out; comparably multifaceted predictive-coding simulations are missing from the literature. A
  parallel result argues amodal completion, not prediction, explains V1 suppression during illusory
  shape perception, and a 2026 *Annual Review of Neuroscience* piece ("Rethinking Predictive
  Processing") revisits the framework's evidential base.
- **The most on-point failure for LANGUAGE.** A 9-laboratory, N=334 pre-registered replication
  (Nieuwland et al. 2018) **failed to replicate the article-elicited N400 cloze modulation** of
  DeLong, Urbach & Kutas (2005) -- the flagship evidence for *probabilistic pre-activation* -- while
  successfully replicating the noun-elicited effect. So: prediction-like signals at the word are
  solid; graded pre-activation of the specific upcoming form is contested. The original authors
  published a rebuttal; the question is live.

**Honest reading:** the *existence* of an error-like comparison in cortex during language is PINNED.
The *specific algebra* we would copy is not.

### 3.2 CROSS-MODAL CORRESPONDENCE (the same referent through vision, touch, action)

**Compared:** features arriving in one modality against features predicted for that modality from a
shared multimodal state driven by the others. **Updated:** the hub-to-spoke weights, so that inputs
naming the same referent converge on one state.

**PINNED:** the anterior temporal lobe as a *transmodal* hub. Bilateral ATL degeneration in semantic
dementia produces selective, **cross-modal**, category-general semantic impairment; inhibitory rTMS
over ATL in healthy participants causally reproduces a semantic-specific deficit (Pobric et al. 2007,
*PNAS*); tractography shows convergence of multiple white-matter pathways into ATL; and ATL damage
impairs the *acquisition* of new conceptual knowledge via impaired feature integration.

**THEORY-ONLY:** that the hub is *trained by cross-modal prediction error* -- that is the
Rogers/McClelland parallel-distributed-processing account, a model, not a recording.

**Why this is the strongest signal in principle and unavailable to us in practice.** It is the only
signal that can equate two words that share no linguistic context at all, because it grounds both in
the same non-linguistic state. It is also exactly the signal our system measurably does not have: the
project's own accounting puts the live path at 35 of 141 modules reading ~28 MB of ~26 GB, with
grounding coverage scoped to one loop. **Do not build the substitutability fix on this signal now;
name it as the ceiling case and move on.**

### 3.3 CONSEQUENCES OF USE (was the utterance understood; did the action succeed)

**Compared:** an expected outcome against the delivered outcome. **Updated:** the cue-to-outcome
weights, scaled by the signed error.

**PINNED, and it is the best-pinned error signal in all of neuroscience:** midbrain dopamine
neurons carry a reward prediction error. Causal, not correlational: optogenetic dopamine activation
at reward delivery causes *unblocking* -- a normally-blocked cue acquires value (Steinberg et al.
2013); brief optogenetic *inhibition* mimics an endogenous negative prediction error (Chang et al.
2016); and a temporal-difference formulation is supported over a value formulation by blocking
designs (Maes et al. 2020). **The blocking phenomenon itself is the key one for us and I return to it
in section 4.**

**THEORY-ONLY for language:** that this signal carries word-*meaning* structure at any useful
resolution.

**PUBLISHED OBJECTION, decisive on bandwidth:** the no-negative-evidence problem. Marcus (1993)
computed that under noisy corrective feedback a child would have to repeat a given sentence verbatim
**~85 times** to conclude with reasonable certainty that it is ungrammatical, and no form of such
feedback is provided to all children at all ages for all error types. The recast literature is
genuinely split (some studies find 2-3x higher post-recast imitation of the correct morpheme; a
longitudinal study finds recasts are *negative* leading indicators of grammaticality).

**Reading:** real, pinned, and far too low-bandwidth to shape a 21,576-dimensional context geometry
over 5,491 words. **Not our lever.**

### 3.4 REPLAY / OFFLINE CONSOLIDATION

**Compared:** by itself, nothing. **This is the signal that is not a signal.** Replay does not compute
an error; it **re-supplies training samples offline** so a cortical learner can take more error-driven
steps, interleaved, without new input. **Updated:** whatever the cortical learning rule updates -- it
multiplies an existing error signal, it does not create one.

**PINNED:** hippocampal sharp-wave-ripple replay of experience-related ensembles; SWR count
correlates with post-sleep memory; **suppressing SWRs impairs consolidation**; closed-loop
optogenetic ripple boosting *enhances* hippocampal-prefrontal reactivation; SWRs lock to cortical
slow oscillations and spindles; and in humans, targeted memory reactivation during sleep improves
learning, including foreign-vocabulary learning.

**THEORY:** the complementary-learning-systems claim that this is *why* cortex must be slow and
interleaved.

**What it buys us concretely, and this is not decorative:** it licenses **multiple passes over a
fixed corpus, in interleaved order, as a brain-faithful operation rather than an engineering hack.**
That is precisely the knob our own ORGAN F result already found positive (+0.0263 from accumulating
~72 sentences per anchor instead of 1). Copy the operation; **sweep the number of passes, never adopt
a biological value for it.**

### 3.5 One more, because it is the cleanest supervised signal in the brain and it is honest about its limits

**Cerebellar climbing-fibre sensory prediction error.** Compared: the forward model's predicted
sensory consequence against the actual one; updated: parallel-fibre-to-Purkinje-cell synapses.
PINNED for sensorimotor learning (Marr-Ito-Albus, fifty years of it). **But the reviews state plainly
that how error signals for higher functions -- tool use, language acquisition -- would originate is
unresolved, and that genetically specified climbing-fibre teachers for such functions are
implausible.** Cite it as the existence proof that brains run genuine supervised learning; do not
claim it as a pinned language mechanism.

---

## 4. WHICH SIGNAL CAN PRODUCE SUBSTITUTABILITY -- THE CRUX

**Answer: prediction error against upcoming linguistic input. Cross-modal correspondence would do it
better but we do not have the data; consequences of use cannot carry the bandwidth; replay amplifies
whichever signal exists but supplies none.** Here is the mechanism, stated precisely enough to be
wrong.

### 4.1 The mechanism, in four steps

**(1) It changes what a word IS.** Counting defines a word by *the set of sentences it occurred in*.
Prediction defines a word by *the distribution over what follows it*. Only the second is invariant to
which particular sentences happened to be sampled. Two substitutable words predict the same
continuations; a system trained to predict is therefore given a reason to converge them **without
ever being told they are synonyms** -- which is exactly the "supervision without labels" the drill was
asked to find.

**(2) It supplies negative information, which a tally structurally cannot.** The update is
`observed - predicted`. When an expected context word does *not* arrive, the weight to it is pushed
*down*. A count vector has no cell for a non-event. On our instrument this is not an abstract point:
SET P pairs are WordNet synonyms with **zero corpus co-occurrence**, so in a 1.82M-token corpus each
member's positive support is small and the two supports may be nearly disjoint -- two sparse
positive-only vectors that are near-orthogonal by sampling accident. The negative mass is where the
shared structure lives.

**(3) It discounts what is already predicted -- and this is the pinned biological operation.**
Rescorla-Wagner: the change in a cue's association is proportional to the error *remaining after all
present cues have made their predictions*. So a cue that adds nothing beyond what is already
predicted gains nothing. This is **blocking**, one of the most replicated findings in associative
learning, and it has a **causally demonstrated dopaminergic substrate** (unblocking by optogenetic
DA activation, section 3.3). Its consequence for us is direct: **high-frequency collocates stop
dominating**, because after the first few exposures they are already predicted. Our measured failure
mode -- winners are collocates, `absence -> presence` is the signature error, AUC 0.05 -- is precisely
what an unblocked, competition-free tally produces. **In contrast with Hebbian/contiguity approaches,
cue-outcome co-occurrence is under this rule neither sufficient nor necessary for learning; what
matters is the cue's predictive value.** That sentence is the whole difference between our write rule
and the brain's.

**(4) A capacity bottleneck forces sharing.** With fewer parameters than word-context pairs, words
posing the same prediction problem must share parameters. SVD supplies the bottleneck but *not* the
error-driven part: it reconstructs the PPMI matrix in uniform least squares, fitting a sparse
matrix's accidental zeros as though they were data. An error-driven rule weights each cell by how
often it was actually at stake.

### 4.2 The single most testable design consequence: WHICH GEOMETRY WE READ

A predictive learner has **two** parameter sets: one for the word as a *cue* and one for the word as
a *predicted outcome* (word2vec's input and output matrices; in cortex, loosely, a predicting
population and a predicted population -- the laminar assignment is THEORY, section 3.1).

- **cue-vector vs outcome-vector** similarity measures *"does A predict B"* -- that is **syntagmatic,
  i.e. co-occurrence.**
- **cue-vector vs cue-vector** similarity measures *"do A and B predict the same things"* -- that is
  **paradigmatic, i.e. substitutability.**

**Our store has one vector per word -- a context profile -- and comparing two profiles is much closer
to the first geometry than the second.** It is entirely possible that a large part of our 0.0710 is
not a missing learning signal at all but **reading the wrong one of the two geometries.** That is
cheap to test and it is in the build as arm T3's secondary diagnostic. If input-input clears while
input-output does not, the fix is on the read side and costs almost nothing.

### 4.3 STEELMAN THE COUNTER-CASE (this is the part that should slow us down)

**(a) The literature says a properly-tuned COUNTING method matches a PREDICTING method on tasks like
ours.** Levy & Goldberg (2014) proved skip-gram with negative sampling is implicitly factorising a
word-context matrix of **PMI shifted by log k**. Levy, Goldberg & Dagan (2015, TACL) then showed that
much of the neural models' advantage came from **system design choices and hyperparameters, not the
algorithm**, that those choices transfer to count models, and that with them **exact SVD factorisation
is at least as good as SGNS on word-similarity tasks** (SGNS retains an edge on analogy). *Our
instrument is a similarity-type task.* So the literature's own prediction is that adding a predictive
objective buys **little** over a properly-tuned counter -- and if we run only the predictive arm and
it wins, we will not know whether we bought it with supervision or with hyperparameters.

**(b) OUR PPMI+SVD ARM WAS THE UNTUNED VERSION, AND THE PLAN CURRENTLY GENERALISES ITS FAILURE.**
Read off the cell source: it computes plain `max(0, log(count*total/(row*col)))`, no context-
distribution smoothing, no `-log k` shift, no subsampling of frequent words, no window weighting. It
does use the standard `U*sqrt(S)` eigenvalue weighting (p=0.5), which is one of LGD2015's
recommendations. **Context distribution smoothing (alpha=0.75) is singled out in that work as
bringing count models to state-of-the-art on word similarity, and subsampling frequent words attacks
exactly our failure mode** (frequent collocates dominating). Plan section 6.18 says "the classical
method for extracting substitutability FAILS on our corpus at every rank." **The accurate statement is
that the VANILLA classical method failed.** This is the project's own standing rule -- *a fair test of
a weak implementation proves that setup failed, not that the capability is impossible* -- applied to
our own headline. **The tuned-count arm is therefore not optional garnish; it is the arm that decides
whether "supervision" is even the variable.**

**(c) Where prediction gives co-occurrence structure instead.** Three named ways: reading the
cue-outcome geometry rather than cue-cue (4.2); a very short context window on a small corpus, where
the strongest predictive relation available *is* the immediate collocate; and the documented
degenerate solution of pure prediction -- regression-to-the-mean / "blurry future" collapse -- which
is why CPC pairs a predictive term with a contrastive one. **Our own 2026-07-09 drill already found
and recorded this**, and it is the reason its S2 design kept the predictive channel in a *separate*
matrix rather than making prediction the sole representation-shaping signal.

**(d) The corpus may simply be too small.** The closest published demonstration of our exact claim --
Huebner & Willits (2018), *Frontiers in Psychology* -- trained SRN, LSTM and skip-gram on
**next-word prediction over 5,244,672 tokens of child-directed speech** and found taxonomic/semantic
structure emerging automatically (semantic classification 70.0% SRN, 73.4% LSTM, 73.7% skip-gram;
perplexity ~4100 -> ~43). **We have 1,824,296 tokens -- about a third.** Two further honest points
from that paper: it ran **no count-based baseline at all**, so it does not establish the
predicting-vs-counting contrast we care about; and **window-based skip-gram matched the sequential
models**, which argues the *sequence* is not the active ingredient -- the error-driven contrast is.
Separately, the corpus-size literature puts "several million words" as the working range for a
child-scale distributional model, and finds input *quality* can outweigh size by orders of magnitude.

**(e) OUR OWN DISK ALREADY CONTAINS THE CAUTIONARY RESULT, AND IT IS THE STRONGEST ONE.**
`data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json` (`run_mode=full`): a
from-scratch trained encoder separated synonyms from siblings at **AUC 0.7064**, beating a matched
grounding arm at 0.3186 with scramble collapsing to 0.5042 -- **but the untrained, RANDOM-INIT,
same-architecture encoder using the same corpus-mention-pooling interface read 0.7452, i.e. equal or
better.** The verdict recorded is `MIDDLE_BAND_INTERFACE_SEPARATES_BUT_NOT_LEARNING`. **The
separation was a property of the pooling interface, not of anything learned.** Any build we ship here
must carry a random-init / untrained control on the *identical* readout, or it will reproduce that
exact error. It is in the spec as N1 and it is non-negotiable.

**Net calibrated position, after the 0.15-0.25 lit-scan deflation and the 0.50 novel-synthesis cap:**

| claim | P (deflated) |
|---|---|
| An error-driven (delta-rule) write over the SAME counts reads CI-separated ABOVE 0.5 | **0.30** |
| A *tuned* count method (no new learning signal) reads CI-separated ABOVE 0.5 | **0.32** |
| Whichever clears, the margin over the *other* is CI-separated (i.e. supervision is genuinely the variable) | **0.22** |
| The read-geometry diagnostic (cue-cue clears while cue-outcome does not) fires | **0.35** |
| Nothing unsupervised clears 0.5 at this corpus size, and the blocker is supply | **0.40** |

*(These do not sum to 1; they are not exclusive. The highest single probability is on the honest
negative, which is where the evidence currently points.)*

---

## 5. WHERE THE NO-LLM LINE FALLS, DESIGN BY DESIGN

The owner's Q3 ruling: **the foundation may be built however is efficient, including as a static
offline-built asset; NO LLM AT INFERENCE is the surviving invariant, and glass-box always.**

| design | offline train? | what runs at read time | verdict |
|---|---|---|---|
| **T1 tuned counts (SPPMI + SVD)** | no learning at all | table lookup + cosine | **SAFE.** Deterministic linear algebra over our own counts. |
| **T2 delta-rule / Rescorla-Wagner update over our own counts** | yes, offline, NumPy, no gradient library | row lookup + cosine | **SAFE, and the safest of the learned arms.** The learned object is a real-valued matrix of cue-to-outcome weights; every cell is inspectable and attributable to a corpus event. No nonlinearity, no generation. |
| **T3 skip-gram trained from scratch on OUR sentences only** | yes, offline, gensim | frozen vector table lookup + cosine | **ADMISSIBLE under Q3.** It is not an LLM: no sequence model, no forward pass, no generation at read time. But its dimensions are opaque, so treat it as a **CEILING REFERENCE for the error-driven family, not as the thing we wire.** |
| **T4 prediction-error-gated write reusing `hdlab/predictive_coding.py`** | the gate runs during ingest | existing store read, unchanged | **SAFE.** Reuses an owned, registered module. |
| **importing word2vec-GoogleNews / GloVe / fastText / any pretrained table** | -- | -- | **DISQUALIFYING**, and we have our own measured reason as well as the invariant: `data/exp_substrate_clean_encoder_substrate_as_LM_v1/metrics.json` (full, HARD_PASS) reads *"word2vec pretrained knowledge was load-bearing"* with a **0.4376 BPC gap** between the Google-News rail and the same model trained on our own data. An imported table smuggles another corpus's answers in. |
| **any transformer/LM call in the read path -- scoring, reranking, embedding, generating** | -- | -- | **DISQUALIFYING. Full stop.** |

**TWO PROPOSALS I AM FLAGGING AS DRIFTING TOWARD THE LINE, so nobody builds them by accident:**

1. **A trained CONTEXTUAL encoder run at inference.** Training a multi-layer encoder ourselves and
   then *running it on a context window at read time* is a neural forward pass in the operational
   path. Offline training is fine under Q3; the *forward pass at read time* is the part that needs an
   explicit owner ruling before anyone builds it. The project's own `scale_win_tinytransformer_encoder`
   sits exactly on this line. **My build spec deliberately stays on the safe side: train offline,
   freeze a static per-word table, read by lookup.**
2. **Using "replay" to GENERATE novel sentences.** Recombining or re-ordering our *own* corpus is
   fine and is what section 3.4 licenses. Generating new text with a learned sequence model is a
   generation step; I would not do it without a ruling, and never with a pretrained generator.

---

## 6. WHAT IS ALREADY ON DISK -- AND HOW I ENUMERATED IT

**An absence claim requires an enumeration, not a search.** Here is the enumeration, method first.

**How I enumerated (six passes, all from disk):**
1. `ls hdlab/` -- full directory listing, **148 `.py` files**, plus `ls -la hdlab/learner/` and
   `hdlab/learner/plugins/`. Not a keyword search.
2. Parsed **all 200 rows** of `data/capability_registry.jsonl` in Python and matched ten
   learning-related substrings against the **whole serialized row**, not just the name field: **90 of
   200 rows matched**; I then dumped 14 rows in full.
3. `ls data/` filtered for result directories named for predictive / contrastive / word2vec / SGNS /
   scale-learning work, then read `verdict` and `verdict_msg` out of each `metrics.json` directly.
4. **Recoverability check before any absence claim.** The four `spoke1` cells named in the registry
   and in the July drill have **no `metrics.json` under those exact directory names**. Rather than
   report them missing, I ran `ls -d data/*spoke1*` and found **six differently-named directories
   that do carry metrics.** This is the trap the project has hit twice; I checked before concluding.
5. Verified the instrument's population key exists by parsing checkpoint keys:
   **`POPULATION|v1.7|full` is line 10** of `data/exp_dissociation_score_instrument_v1/units.jsonl`
   (alongside `SCORES|v1.7|full`). The build must load it and never rebuild the matching.
6. Verified the venv has what the build needs: `.venv/Scripts/python.exe` reports **gensim 4.4.0,
   scikit-learn 1.9.0, scipy 1.17.1, numpy 2.4.5, torch 2.12.0+cpu**.

**NOT DONE, disclosed:** I did not re-run a runtime import trace (`tools/integration_health.py`).
The registry's `used_by` lists are import-graph-derived per their own provenance strings; CLAUDE.md
prefers runtime evidence over static graphs for "is X reached" questions. Treat the consumer counts
below as static-graph evidence.

### 6.1 The learning machinery that exists, and what each piece can and cannot do

| module | what it is | can | CANNOT |
|---|---|---|---|
| **`hdlab/learner/`** (`core.py`, `registry.py`, 4 plugins) | ONE MDL model-selection engine: fits every registered hypothesis-class plugin to a task and picks the one that best compresses past a null two-part code; enforces a glass-box invariant (the hypothesis must survive `json.dumps`). Plugins: `estimation` (frequency/evidence accumulation), `ruleind` (MDL-gated conjunction rule induction), `gam`, `proginduction`. Registered **WIRE / WIRED**, 14-23 consumers each. | learn a **symbolic or tabular hypothesis from labelled episodes**, with an explicit induce-vs-keep-episodic gate | **learn a real-valued representation.** Its contract is `learn(episodes, features, spec) -> glass-box hypothesis dict`. There is no plugin that consumes an error residual and updates an embedding; no delta rule; no negative sampling; no notion of "predict the next/context item". Its `estimation` plugin **accumulates evidence -- i.e. counts -- which is precisely the family that just failed.** |
| **`hdlab/predictive_coding.py`** (325 lines) | Rao-Ballard/Friston-framed: `predict(W,key)=sign(W@key)`, `residual`, `residual_magnitude` (mismatch fraction via cosine), `threshold_gate`, `proportional_gate`, `relative_threshold_gate` + `running_avg_update` (EST-style self-referential boundary test), `gated_write`, `vanilla_hebbian_write`, plus a self-test. Registry: **`ALREADY_WIRED` / `WIRED`, 15 consumers.** | gate a Hebbian write by how *surprising* the observation is; supply a precision-weighted write strength | it is **flat** (single `W`, single level), assumes **bipolar +-1** vectors with sign cleanup, and its residual currently gates **whether/how hard to write an existing outer-product update**. It has **no delta-rule update over a sparse count matrix** and no separate cue/outcome parameter sets. |
| `hdlab/perceptron.py` | Collins (2002) averaged structured perceptron, mistake-driven, Viterbi | genuinely error-driven **supervised sequence labelling** | needs labels; discrete features; not a representation learner |
| `hdlab/learning.py` | reward-modulated sparse Hebbian associations | contiguity-based association | **pure Hebbian -- no cue competition, which is the whole point of section 4.3** |
| `hdlab/ppmi_sparse_encoder.py` | PPMI -> SVD -> top-k threshold -> bipolar | our owned classical pipeline | vanilla PPMI (no smoothing/shift/subsampling); fit is over (sentence, concept-label) pairs |
| `hdlab/consequence_learning_loop.py`, `word_acquisition_loop.py`, `grounding_acquisition_loop.py` | the consequence/outcome learning family, WIRED, 13 consumers | learn from outcome feedback | the section-3.3 bandwidth objection applies |

### 6.2 The prior art that most constrains this build (all read off disk this session)

- **`notes/research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md`** (41 KB) --
  a full drill on this exact topic. Its conclusions that still stand and that I am **not**
  re-deriving: prediction error is a genuinely LOCAL rule (Whittington & Bogacz); its defining
  property is ONE error variable serving inference and learning on two timescales; a purely
  predictive channel has its **own** collapse mode (regression-to-the-mean / posterior collapse) and
  CPC exists precisely because of it; therefore keep the predictive channel in a **separate matrix**
  rather than making it the sole representation-shaping signal. Its deflated P for "prediction error
  is a worthwhile ADDITIONAL axis" was **0.46**; for the specific dedicated-`W_pred` improvement,
  **0.30**. My 0.30 in section 4.3 is consistent with that and arrived at independently.
- **The spoke1 cell family, and the numbers DO NOT TRANSFER.** Recovered from disk:
  `..._v2_smoke/metrics.json` is **`run_mode=smoke`**, HARD_PASS, metric = a hand-picked
  concept-triplet cosine `gap` (HYBRID 0.517, PRED 0.566);
  `..._v3_D_competitive_hebbian_only_2026_07_02/metrics.json` is **full, HARD_PASS -- but it is the
  COMPETITIVE-HEBBIAN arm, not the predictive one** (`ck=0.492`); and the apples-to-apples stress
  test at full is **MIDDLE_BAND** (`v3d_ck=0.492` vs `soft_ck=0.461`, failing
  `HP2_v3d_beats_softmax_by_min`). **So the only FULL, softmax-controlled run in that family measured
  the non-predictive arm, and the predictive HARD_PASS is smoke-only on a hand-picked probe.** That is
  a stronger caution than "different population": **predictive coding has never been scored on the
  licensed dissociation instrument, and its existing pass is not a full run.** Treat as UNVERIFIED.
- **`data/exp_pc1_predictive_coding_residual_gate_v1/metrics.json`** (full): MIDDLE_BAND -- both gate
  flavours **skipped 0.00** of writes, i.e. the gate never actually fired on that workload. A gate
  that never fires cannot have been tested. Note it in the new cell's design.
- **`exp_diag_learned_encoder_synonym_sibling_deep_wall_v1`** -- the random-init control result in
  section 4.3(e). **This dictates arm N1.**
- **A from-scratch SGNS on our own data already exists as an arm**:
  `exp_substrate_clean_encoder_substrate_as_LM_v1` trained gensim Word2Vec on the text8 training
  split only (`B_W2V_TEXT8_ONLY`). **The machinery and the discipline for a no-import, from-scratch
  predictive arm are already demonstrated in this repo** -- what has never been done is training it on
  *the profile corpus* and scoring it on *the dissociation instrument*.

### 6.3 The standing rule, and the honest answer to it

**MISSING-LEARNING -> REUSE/EXPAND `hdlab/learner`, never build a parallel one.** Applied literally
here it gives the wrong answer, and the reason should be stated rather than quietly ignored:
**`hdlab/learner`'s contract is `episodes -> glass-box symbolic hypothesis`, and the thing we need to
learn is a 5,491 x k real-valued matrix.** Forcing a matrix learner into the MDL-plugin interface
would be a parallel build wearing the module's name. **The module that genuinely fits is
`hdlab/predictive_coding.py`** -- it is the project's owned home for predict / residual / gated
write, it is registered WIRED with 15 consumers, and the missing piece is one additive function.
**So: EXPAND `hdlab/predictive_coding.py` with a delta-rule update; do not fork, do not build a new
learner, and do not bend the MDL plugin contract.** If exp_dev finds the module's bipolar/sign-cleanup
assumptions load-bearing enough that the addition does not fit cleanly, it must **say so explicitly**
rather than silently creating a sibling file.

---

## 7. PINNED BY EVIDENCE vs OUR INVENTION UNDER TEST -- every design choice

Presenting an invention as pinned is barred. Unpinned does not mean stop; it means test the best
brain-motivated candidate and say which it is.

| design choice | status | note |
|---|---|---|
| An error-like comparison between expected and actual upcoming input exists in cortex during language | **PINNED** | ECoG pre-onset predictive information + post-onset surprise; N400 graded by cloze. Objections in 3.1 stated in the same breath. |
| Cue competition: a cue already predicted gains no further association | **PINNED** (associative learning + causal dopaminergic RPE) | blocking/unblocking; this is the operation that discounts collocates |
| That cortex implements Rao-Ballard/Friston hierarchical predictive coding with distinct laminar error units | **THEORY-ONLY** | do not describe the build as replicating this |
| That error-driven learning is what organises the *lexicon* by substitutability | **THEORY** (computationally modelled, not recorded) | Baayen/Ramscar discriminative-learning line; the developmental phenomenon it explains is section 8's known-answer |
| Delta rule over a two-layer cue->outcome map | **OUR INVENTION UNDER TEST** | a deliberately minimal instance of the pinned operation |
| Word identity as the CUE, context words as OUTCOMES | **OUR INVENTION UNDER TEST** | the brain's cue set is certainly not one-hot lexical |
| Two separate parameter sets (cue-side, outcome-side) | **OUR INVENTION**, loosely motivated | separate predicting/predicted populations is THEORY at the laminar level; the *engineering* consequence (4.2) is testable regardless |
| Reading similarity as cue-vector cosine | **OUR INVENTION** | the alternative geometry is the diagnostic |
| Multiple interleaved passes over the corpus ("replay") | **the OPERATION is PINNED; the NUMBER is a PARAMETER to sweep** | our worst result copied a number, our best copied an operation |
| The 5,491-anchor / 34,169-sentence / 1,824,296-token corpus | **OUR SUPPLY CONSTRAINT** | not a brain fact; explicitly one of the stop-if outcomes |
| Vector dimensionality k | **PARAMETER, swept** | per the owner's per-organ regime ruling, set it per organ, do not ask "what is OUR dimensionality" |
| Frequency subsampling / context-distribution smoothing | **OUR INVENTION borrowed from published practice, credited** | Levy, Goldberg & Dagan 2015; fixed a priori at their defaults, never tuned on our 242 pairs |

---

## 8. THE BUILD SPECIFICATION -- can-fail, ready for an exp_dev agent

**Proposed anchor:** `exp_error_driven_write_rule_dissociation_v1`. **Local CPU.** The reference cell
it clones for structure is `experiments/exp_corpus_capacity_ppmi_svd_ceiling_v1.py`, which ran in
**48.6 s** on the same matrix.

### 8.0 Non-negotiable preconditions

1. **PRIMARY MEASURE = the licensed dissociation AUC.** Above 0.5 = substitutability; below = 
   co-occurrence. Bands are the instrument's, not new ones.
2. **POPULATION IS LOADED, NEVER REBUILT.** `data/exp_dissociation_score_instrument_v1/units.jsonl`,
   checkpoint key **`POPULATION|v1.7|full`** (verified present, line 10, alongside
   `SCORES|v1.7|full`), via `tools/exp_checkpoint.py`. 242 pairs per cell, byte-identical. Rebuilding
   the matching is a gate failure, not a variation.
3. **LICENCE GATE FIRST.** Reproduce all eight regression checks to 4 dp from the cached
   `SCORES|v1.7|full`: `F_ORTHOGRAPHIC 0.5000`, `F_FREQUENCY 0.4901`, `F_SCRAMBLE 0.4664`,
   `F_CONSTANT_PROTOTYPE 0.5431`, `KNOWN_ANSWER 0.9599`, `RANDOM_VECTOR_STORE 0.4862`,
   `INCUMBENT 0.0710`, `RAW_COUNT_FULL_ACCUM 0.0510`. Any delta > 0.0001 -> write only a GATE_FAIL
   metrics.json, `INSTRUMENT_NOT_LICENSED`, publish nothing else.
4. **ONE CORPUS, ONE SCORER, ONE POPULATION, ONE CUE REGIME across every arm.** The corpus is the
   same profile-sentence set the store was built from (5,491 anchors, `MIN_LEMMA_COUNT=8`,
   `K_SENT_TOTAL=90`, `PROFILE_FRAC=0.8`, 34,169 sentences, 1,824,296 tokens), reached through the
   same `Pstore|<word>` checkpoints and the same `build_vocab` / `to_sparse` helpers the capacity
   cell reused. Where an arm needs ordered tokens rather than counts, it must take them from the
   **same profile sentences** (`build_corpus("full")` -> `load_corpus_v5`) with the **same masking**
   (`raw_counts_for_window` removes every token whose lemma equals the target).
5. **NO HYPERPARAMETER MAY BE CHOSEN BY LOOKING AT THE 242 PAIRS.** All settings are fixed a priori
   at published defaults (listed per arm). 37.6% of pair members recur across pairs; tuning on them
   manufactures a second oracle.
6. **REPORT, BESIDE EVERY MARGIN:** the CI half-width, the null p95 at n=242 from the permutation
   arm, and both tie conventions. A width is not an effect.

### 8.1 Reference arms (loaded from cache, not recomputed)

`A0_INCUMBENT` 0.0710 | `B0_VANILLA_PPMI_SVD_k50` 0.0519 | `C1_ORACLE_GROUP_DISJOINT` -- carry the
**0.8629** group-disjoint figure, labelled `CEILING_NOT_A_CAPABILITY`, and if the cell recomputes it,
recompute it **group-disjoint by word**, never pair-level.

### 8.2 Treatment arms

**`T1_TUNED_COUNT` -- the arm that decides whether supervision is even the variable. RUN IT FIRST.**
Same counts, no learning. Shifted-PPMI with the published defaults, all fixed a priori:
context-distribution smoothing **alpha = 0.75**, shift **-log k with k = 5**, frequent-context
subsampling **t = 1e-5**, SVD with eigenvalue weighting **p in {0.0, 0.5}** (0.5 is what B0 already
used), rank **k in {50, 300}**. Cosine over the resulting rows.
*Credit: Levy & Goldberg 2014; Levy, Goldberg & Dagan 2015 -- we are learning from and building on
their published tuning, not inventing it.*

**`T2_DELTA_RULE` -- the brain-motivated arm. The one-variable test of error-driven vs counting.**
Cues = the content words of a profile sentence, masked of the target's own lemma (identical masking
to the count arms). Outcome = the anchor that sentence belongs to. Update, per sentence:

```
V = sum over cues c present of W[c, :]              # what the present cues already predict
W[c, :] += eta * ( lambda * e_anchor  -  V )        # for every cue c present
```

`lambda = 1.0`, `eta in {0.001, 0.01}`, passes over the corpus **in {1, 2, 4, 8}** in interleaved
(shuffled-sentence) order -- **the passes are the replay knob of section 3.4, swept as a parameter,
never adopted from a biological value.** A word's representation is its **column** `W[:, anchor]`
("which contexts predict me"), which has the same shape as the store's profile so the comparison is
one-variable. **The only difference from `RAW_COUNT_FULL_ACCUM` is the subtraction of `V` -- that is
cue competition, and it is the entire hypothesis.**
Memory note: `W` is 21,576 x 5,491 float32 ~ 474 MB. If that is too heavy, restrict cues to the top
`V_c` context words by document frequency and **disclose the truncation as a config field**.

**`T2b_ANALYTIC_EQUILIBRIUM` -- the same rule solved instead of iterated. Cheapest decisive arm.**
The delta rule's equilibrium is known in closed form (Danks 2003): for each outcome, the converged
weights satisfy `C w = p`, where `C[c,c'] = P(c' present | c present)` and `p[c] = P(outcome | c)`.
So `w = C^{-1} p` -- **error-driven learning at convergence is exactly decorrelating the context
matrix**, and `hdlab/whitening.py` is the owned module for that step. Use a ridge term
(`C + gamma I`, `gamma = 1e-3`) and a truncated cue vocabulary `V_c in {2000, 5000}` by document
frequency, disclosed. **This arm is seconds of linear algebra and it makes the mechanism inspectable:
if `T2b` and `T2` disagree, the iterative arm has not converged and its number means nothing.**

**`T3_SGNS_FROM_SCRATCH` -- ceiling reference for the error-driven family, plus THE read-geometry
diagnostic.** gensim `Word2Vec(sg=1, negative=5, sample=1e-5, window=5, min_count=1, epochs=5)`,
**trained on the profile sentences only, nothing imported.** (`gensim 4.4.0` confirmed in the venv;
the repo already demonstrates a no-import from-scratch Word2Vec arm in
`exp_substrate_clean_encoder_substrate_as_LM_v1`.) Report **two** numbers on the same pairs:
`T3_IN_IN` (cue-vector cosine, paradigmatic) as primary, and `T3_IN_OUT` (cue-vs-outcome, syntagmatic)
as the diagnostic. **Assert `NO_PRETRAINED_EMBEDDING_TABLE_IMPORTED = true` in metrics.json**, as the
capacity cell does.

**`T4_PREDICTION_GATED_WRITE` -- does our OWN module fix the write rule?** Rebuild the store with
each occurrence's write strength set by `hdlab.predictive_coding.proportional_gate(observed=context
vector, predicted=predict(W, anchor))`, module reused unchanged (this is the EXPAND-don't-fork move
of 6.3). **MANDATORY PRECONDITION, learned from `exp_pc1_predictive_coding_residual_gate_v1` (full,
MIDDLE_BAND) where both gate flavours skipped exactly 0.00 of writes: assert the realised gate
statistic is strictly interior (0 < mean write strength < 1 and its variance > 0). If the gate does
not actually vary, this arm is `UNINTERPRETABLE_GATE_DID_NOT_FIRE`, NOT a negative result.**

### 8.3 Floors, known-answer, null and controls -- all on the same 242 pairs

- **Four floors**, reproduced from cache as part of the licence gate (8.0.3): orthographic,
  frequency-max, scramble, constant-prototype. All four sit at chance by construction; the gate is
  that they still do.
- **`K1_KNOWN_ANSWER`** (WordNet path similarity) must reproduce **0.9599**. This is the arm that
  proves the instrument can see substitutability when it is there.
- **`N0_RANDOM_VECTOR_STORE`** must reproduce **0.4862**.
- **`N1_UNTRAINED_CONTROL` -- MANDATORY, one per learned arm (T2, T2b, T3, T4).** Identical
  architecture, identical readout, weights never updated (T2/T4) or `epochs=0`/random-init vectors
  (T3). **This exists because `exp_diag_learned_encoder_synonym_sibling_deep_wall_v1` measured
  randinit 0.7452 >= trained 0.7064 on a structurally similar question. If a learned arm is not
  CI-separated from its own N1, the result is an INTERFACE ARTIFACT and must be reported as one.**
- **`N3_SHUFFLED_PAIRING`** -- the same tokens with context sets permuted across anchors, destroying
  the word-context pairing while preserving every marginal. A learned arm that does not beat N3
  CI-separated has learned frequency, not structure.
- **`NULL_PERMUTATION`** -- permute the P/S labels 10,000 times; report the null distribution's p95
  beside every margin. At n=242 this is what tells us whether a margin is an effect or a width.
- **`ARMS_MUST_DIFFER`** digest check per new arm, as the capacity cell does.
- **Monotonicity/leak check:** no arm that destroys information may score above an arm that keeps it.
  If one does, report the leak, not the ladder.

### 8.4 Pre-registered stop-ifs, evaluated IN THIS ORDER

**(i)** Licence gate fails -> `INSTRUMENT_NOT_LICENSED`; nothing is concluded from the run.

**(ii)** **`T1_TUNED_COUNT` is CI-separated ABOVE 0.5.** Then **the missing ingredient was never
supervision; it was frequency discounting**, and section 6.18 of the ladder plan must be corrected in
the owner-facing report in those words -- "the vanilla classical method failed; the tuned one did
not." The learning-signal programme pauses and Organ A's five gates are re-read against the tuned
baseline rather than against the untuned one.

**(iii)** **T2 / T2b / T3_IN_IN CI-separated ABOVE 0.5 *and* CI-separated above `T1`.** Error-driven
learning is the lever. **Report the margin over T1, never the margin over 0.5** -- the margin over 0.5
includes whatever the hyperparameters bought.

**(iv)** **A learned arm clears 0.5 but is NOT CI-separated from its own `N1` or from `N3`.** The win
is an interface / marginal artifact. Report it as an artifact in the headline, not as a capability.
This is the pre-registered guard against repeating the 2026-08-17 encoder result.

**(v)** **`T3_IN_IN` clears while `T3_IN_OUT` does not (or vice versa).** **Highest-value outcome.**
The defect is *which geometry we read*, not what we learn, and the fix is a cheap read-side change.
Report the two numbers side by side and route to a read-side build, not another write rule.

**(vi)** **Everything -- T1, T2, T2b, T3, T4 -- stays CI-separated BELOW 0.5 while the group-disjoint
oracle still clears.** Then the signal is in the counts and **no local error-driven rule reaches it at
this corpus size.** The blocker relocates to **SUPPLY** (1.82M tokens against the ~5.2M that the
closest published demonstration needed) or to the read geometry. That goes to the owner as a supply
question with a recommendation, **not as another write rule**, and write-rule engineering stops.

**(vii)** `T4`'s gate statistic is degenerate -> `UNINTERPRETABLE_GATE_DID_NOT_FIRE` for that arm
only; the other arms still report.

**WHAT WOULD INVALIDATE ALL OF THE ABOVE:** a licence-gate or `K1` failure. And one thing that is
explicitly NOT a permitted response to an unwelcome answer: **adjusting the instrument's bands.
Adjusting the bands is not a result.**

---

## 9. THE SHELVE CRITERION -- BRAIN-FRAMED, NEVER PERFORMANCE-FRAMED

**No AUC shelves this direction.** A miss means our implementation failed; the brain is the existence
proof that the capability is reachable. What would have to be true about the **biology** for us to
abandon it:

1. **If the pre-onset predictive signal in human language cortex turns out not to be predictive.**
   The ECoG result (activity before word onset carrying context-dependent information about the
   forthcoming word) is the load-bearing observation. If it goes the way the DeLong article effect
   went -- a large pre-registered multi-lab attempt finding the pre-onset signal is post-hoc
   integration or a decoding artifact -- **and** the cortical mismatch responses that anchor the
   error account are better explained by short-term synaptic depression (the adaptation model), then
   **there is no cortical error signal to copy** and we would be replicating a theory rather than a
   structure. Shelve.
2. **If the syntagmatic-to-paradigmatic reorganisation turns out to be driven by an organ we are not
   modelling.** Children's word associations shift from *co-occurrence* responses (dog -> bark) to
   *substitutability* responses (dog -> cat) between roughly ages 5 and 10 -- **this is our
   instrument's own axis, measured in humans, and it says our store is sitting at the pre-shift
   stage.** But the literature already flags that the shift tracks **reading acquisition** and
   schooling context, not accumulated speech alone. If the evidence consolidates that the shift is
   caused by explicit orthographic/categorisation instruction rather than by accumulated predictive
   experience, then **the operation we are copying is not the operation that produces the
   capability**, and error-driven learning over a text stream is the wrong organ. Shelve, and go look
   at what instruction supplies.
3. **If cross-modal correspondence turns out to be necessary rather than merely better.** If the
   evidence shows that the transmodal hub's substitutability structure cannot form from linguistic
   input alone in any species or any patient population, then the text-only route is closed on
   principle and the work relocates to supply.

**REVIVAL CRITERIA, so this is not a one-way door:** revive if a recording shows an error-like signal
at the word/lexical level in a transmodal semantic region; or if a replication consolidates graded
pre-activation of upcoming lexical items; or if the corpus grows past the ~5M-token range where the
closest published demonstration succeeded, since a scale-limited null is not a mechanism null.

---

## 10. WHAT THIS DRILL DOES NOT LICENSE

- It does not license quoting **0.8629** (or 0.9606) as a capability. The oracle is fitted on the
  evaluation construct.
- It does not license the claim that predictive coding "already passed." **It has never been scored
  on this instrument, its only full softmax-controlled run measured the non-predictive arm, and its
  predictive HARD_PASS is smoke-only on a hand-picked concept triplet.** (6.2, verified off disk.)
- It does not license "the classical method fails on our corpus." **The vanilla classical method
  failed.** (4.3b.)
- It does not license treating a predictive objective as grounding. Our own July drill put that at
  **P=0.15** and the ML literature is openly split (form-vs-meaning critiques; "epistemic
  parasitism"). This drill does not reopen that.
- **Strategic reads in this note are hypothesis-pending-VET.** The one I would most want VET'd is
  4.2 (the read-geometry claim), because it is the cheapest and it would be embarrassing to be right
  about it for the wrong reason.

---

## 11. SOURCES

Prediction error / predictive coding: [Rethinking Predictive Processing, Annual Review of
Neuroscience](https://www.annualreviews.org/content/journals/10.1146/annurev-neuro-102124-031410) *
[The Adaptation Model Offers a Challenge for the Predictive Coding Account of
MMN](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8640521/) * [Amodal completion instead of
predictive coding, V1](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8131992/) * [Predictive coding: a
theoretical and experimental review](https://arxiv.org/pdf/2107.12979) * [Locomotion-induced gain
cannot explain visuomotor mismatch responses in L2/3](https://pubmed.ncbi.nlm.nih.gov/36821437/) *
[Opposing influence of top-down and bottom-up input on L2/3 excitatory
neurons](https://www.biorxiv.org/content/10.1101/2020.03.25.008607v1.full)

Language prediction in cortex: [Shared computational principles for language processing in humans and
deep language models, Nature Neuroscience](https://www.nature.com/articles/s41593-022-01026-4) *
[Thinking ahead: spontaneous prediction in
context](https://www.biorxiv.org/content/10.1101/2020.12.02.403477v4.full) * [Large-scale replication
study reveals a limit on probabilistic prediction in language
comprehension](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5896878/) * [DeLong, Urbach & Kutas
comment on the 9-lab study](http://kutaslab.ucsd.edu/FinalDUK17Comment9LabStudy.pdf)

Error-driven learning of language: [Language learning as uncertainty reduction: the role of
prediction error](https://www.sciencedirect.com/science/article/abs/pii/S0749596X21000140) *
[Emergence of speech and language from prediction error (special
issue)](https://www.tandfonline.com/doi/full/10.1080/23273798.2023.2197650) * [An exploration of
error-driven learning in simple two-layer
networks](https://link.springer.com/article/10.3758/s13428-021-01711-5) * [Modelling lexical decision
with linear discriminative learning](https://quantling.org/~hbaayen/publications/HeitmeierChuangBaayen2023.pdf)

Reward prediction error, causal: [A causal link between prediction errors, dopamine neurons and
learning](https://pmc.ncbi.nlm.nih.gov/articles/PMC3705924/) * [Brief optogenetic inhibition mimics
endogenous negative RPE](https://www.nature.com/articles/nn.4191) * [Causal evidence that dopamine
transients function as temporal-difference prediction
errors](https://www.nature.com/articles/s41593-019-0574-1)

Cross-modal hub: [ATL mediates semantic representation: mimicking semantic dementia with
rTMS, PNAS](https://www.pnas.org/doi/10.1073/pnas.0707383104) * [ATLs are critically involved in
acquiring new conceptual knowledge](https://pmc.ncbi.nlm.nih.gov/articles/PMC3884130/)

Replay / consolidation: [The hippocampal sharp wave-ripple in memory retrieval and
consolidation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6794196/) * [Large sharp-wave ripples promote
hippocampo-cortical reactivation and consolidation,
Neuron](https://www.cell.com/neuron/abstract/S0896-6273(25)00756-1) * [Neurofeedback training
modulates task-relevant replay rate](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11221834/)

Cerebellum: [Prediction signals in the cerebellum: beyond supervised motor learning,
eLife](https://elifesciences.org/articles/54073) * [Predictive reward-prediction errors of climbing
fiber inputs](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11957396/) * [50 years since Marr, Ito and
Albus](https://arxiv.org/pdf/2003.05647)

Negative evidence: [Negative evidence in language
acquisition (Marcus)](https://pubmed.ncbi.nlm.nih.gov/8432090/) * [Negative evidence and negative
feedback: immediate effects](https://journals.sagepub.com/doi/10.1177/014272370002006001)

Syntagmatic-paradigmatic shift: [The syntagmatic-paradigmatic shift and reading
development](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/1AC9626782613EB5BED808D6961B514F/S0305000901004998a.pdf/the-syntagmatic-paradigmatic-shift-and-reading-development.pdf)
* [When words shift: age and language of elicitation influence syntagmatic-paradigmatic shifts in
bilingual children](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12729949/) * [Paradigmatic
associations and individual variability in early lexical-semantic
networks](https://pubmed.ncbi.nlm.nih.gov/31670556/)

Predicting vs counting, and corpus scale: [Improving Distributional Similarity with Lessons Learned
from Word Embeddings (Levy, Goldberg & Dagan 2015,
TACL)](https://aclanthology.org/Q15-1016/) * [Neural word embedding as implicit matrix factorization
(Levy & Goldberg 2014)](https://www.researchgate.net/publication/287514944_Neural_word_embedding_as_implicit_matrix_factorization)
* [Structured semantic knowledge can emerge automatically from predicting word sequences in
child-directed speech (Huebner & Willits
2018)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5827184/) * [The effects of data size and
frequency range on distributional semantic models](https://arxiv.org/pdf/1609.08293)

**Prior work is learned from, built on and credited here -- never framed as taken.** The tuning
recipe in `T1` is Levy, Goldberg & Dagan's; the equilibrium identity in `T2b` is Danks's; the
discriminative-learning formulation in `T2` is the Rescorla-Wagner / Baayen-Ramscar line; the
child-directed-speech demonstration is Huebner & Willits's.
