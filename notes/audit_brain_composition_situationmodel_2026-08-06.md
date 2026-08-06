# Deep brain-foundational audit: semantic composition + relational binding + situation-model integration (2026-08-06)

USER-requested audit of the component cluster underneath the whole comprehension organ: how the brain
COMPOSES word meanings, BINDS relations (who-did-what-to-whom, whose-goal, outcome-to-goal), and maintains
+ INFERS over the running situation model. Trigger case: "you are a good boy" (said by the mother) =
the help-mother goal was met -- never stated, must be composed from utterance + social relation + goal.
Method: 3 parallel Sonnet lit-scan sub-agents (minimal composition/LATL-Hagoort; binding-problem/synchrony
+ thematic-role-to-filler; bridging-inference/schema-prediction/pragmatics), reconciled here against 4
already-landed in-repo brain drills (`drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md`,
`drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md`,
`drill_brain_goal_owner_flow.md`, `drill_brain_outcome_valence_goal_congruence_2026-08-06.md`) and the
disk-verified implementation state (`notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md`,
`notes/brain_audit_SYNTHESIS_missing_semantic_organ.md`). Calibration penalty per
[[feedback-lit-scan-calibration-penalty]] applied throughout; deflated 0.15-0.25, novel-synthesis capped 0.50.

---

## HEADLINE

The substrate's algebraic composition/binding machinery (FHRR `bind`=elementwise complex multiply,
`bundle`=superposition, and the role-keyed registers built from them) is, on the freshest literature found
this session, in the **same functional class as the best-currently-supported empirical account of neural
thematic-role binding** (Lalisse & Smolensky 2021's direct reanalysis of Frankland & Greene's fMRI data
finds a superposition/tensor-product-style code fits real neural role-binding data BETTER than an
orthogonal-register code) -- this is a genuinely strong, not aspirational, brain-fidelity result for one
of our most-used primitives. **The barrier is not composition/binding. It is the INFERENTIAL layer the
brain runs OVER bound representations** -- Kintsch-style construct-then-integrate constraint satisfaction,
schema-based forward prediction (Event Segmentation Theory / posterior-medial-mPFC script system), and
Graesser-class bridging inference across NON-lexical (pragmatic/social/evaluative) links -- none of which
exist in the substrate. The "good boy" case is the textbook instance of exactly this missing stack: it
requires retrieving an antecedent goal, interpreting an evaluative speech act's illocutionary force
(praise, not just its literal semantics), applying social-relation/authority knowledge (mother = caregiver
whose approval tracks task success), and composing all three into an outcome judgment -- with **no shared
lexical item or thematic role linking the outcome clause to the goal clause** for our current
theme-match/verb-class machinery to walk.

---

## 1. MINIMAL COMPOSITION -- SHAPE / POSITION / METRIC

| Dimension | Finding | Confidence |
|---|---|---|
| **POSITION** | Left anterior temporal lobe (LATL), ~200-250ms post-noun-onset, for two-word minimal phrases ("red boat" vs. list-control "cup, boat") -- Bemis & Pylkkanen (2011, *J. Neurosci.* 31:2801-2814; 2013, *Cerebral Cortex* 23:1859-1873, replicated amodally auditory+visual). Later vmPFC effect ~400ms, left angular gyrus effect also reported. ECoG at finer grain (Murphy, Woolnough, Rollo, Roccaforte, Segaert, Hagoort & Tandon 2022, *J. Neurosci.* 42:3216-3227, n=19) finds the generator is actually a fine-grained **posterior STS "mosaic"** of neighboring lexicality-sensitive vs. phrase-structure-sensitive sites (~210-300ms), not a monolithic ATL pole signal -- a partial divergence from the pure-MEG localization. | HIGH on phenomenon existing; MEDIUM on exact anatomical grain |
| **SHAPE (what a composed representation IS)** | The field's OWN interpretation shifted (2011->2020): originally framed as loosely "syntactic," now characterized as **conceptual/intersective feature combination sensitive to modifier specificity** (Zhang & Pylkkanen 2015, *NeuroImage*, PMID 25703829: LATL response to the head noun scales with modifier feature-richness). Pylkkanen's own later synthesis (2020, *Phil. Trans. R. Soc. B* 375:20190299 -- not directly fetched, secondary-sourced) proposes **two separate composition systems**: (i) a conjunctive/intersective LATL system ("red boat" = an individual that is both red AND a boat), (ii) a separate, not-yet-anatomically-dissociated "more logical" predicate-argument (function-application) system for non-modification composition. **Direct, recent (2025) RSA evidence** (Ciapparelli, Marelli, Graves & Reverberi, *Cerebral Cortex* 35:bhaf246, directly fetched) tests additive-vs-multiplicative compositional models against real RSA in LIFG/LATL/angular gyri/mid-STS: **the multiplicative (elementwise-product, "symmetric intersection of features") model consistently outperforms the additive/vector-sum model**, strongest in LIFG, weaker (but positive) in LATL. This is the single most load-bearing, directly-fetched, most-recent finding for "what operation is composition": **NOT additive summation, but multiplicative/elementwise conjunction of feature vectors** -- naturally read alongside our own `bind` primitive. | HIGH for "not naive additive sum"; MEDIUM for the two-systems (conjunction vs. predicate-argument) split, which is theoretically proposed but not anatomically confirmed |
| **Full-sentence composition needs a DIFFERENT, asymmetric operation** | Frankland & Greene (2015, *PNAS* 112:11732-11737, secondary-sourced via PNAS listing, cross-corroborated) and follow-up (2020, *Cerebral Cortex* 30:3838-3855, "Two Ways to Build a Thought") show full transitive-sentence composition is NOT well-modeled by a symmetric multiplicative/additive operation at all -- multiplicative/additive combination is, by construction, insensitive to WHICH word plays WHICH role (order-symmetric), whereas real sentence meaning ("dog chased cat" != "cat chased dog") requires an asymmetric, role-labeled code (see Section 2). Different regions (amPFC, lmSTC, hippocampus) are reported to build composed representations via genuinely DIFFERENT compositional schemes -- "no single neural format for composed meaning," per the 2020 paper's own explicit framing. | MEDIUM-HIGH |
| **Hagoort's Memory-Unification-Control (MUC) model, LIFG** | Directly fetched (PMC3709422). Three-way split: Memory (stored lexical/syntactic/semantic frames, temporal cortex + angular gyrus) / Unification (binding retrieved frames into larger structures, **LIFG/Broca's area**) / Control (task management, dlPFC+ACC). Mechanism proposed for unification: (a) **sustained/reverberatory neuronal activity** -- LIFG maintains an incrementally-built interpretive context via feedback loops to the temporo-parietal regions items were retrieved from, NMDA-mediated persistence (directly fetched); (b) a separate, not-fully-reconciled strand: **oscillatory gamma-band synchrony** indexes semantic unification, **beta-band** indexes syntactic unification (Bastiaansen, Magyari & Hagoort 2010, *J. Cogn. Neurosci.* 22:1333-1347, secondary-sourced). The MUC paper itself does NOT discuss LATL at all -- the two research programs (Hagoort/LIFG, Bemis-Pylkkanen/LATL) developed independently and are not cleanly reconciled in any single source found. **Complication**: Ciapparelli et al. 2025 (above) found LIFG shows the STRONGEST (not weakest) match to the multiplicative compositional model -- muddying any simple "LATL composes, LIFG just selects/disambiguates" story; LIFG may be central to the composed FORMAT itself, not merely downstream control. | HIGH on the MUC model's existence/structure; LOW-MEDIUM on the precise LATL-LIFG division of labor (genuinely unresolved) |
| **Controversy (explicitly flagged, not settled science)** | (i) Task-dependency: Fló et al. (2020, EEG) found the composition effect disappears without an explicit compose/don't-compose task block -- challenges automaticity. (ii) Failed cross-linguistic replication: Kochari et al. (2021, *Neuropsychologia*) failed to replicate the early LATL effect in Dutch. (iii) Association confound: Li & Pylkkanen (2021, *J. Neurosci.* 41:6526-6538, directly fetched) found LATL responds selectively to HIGH-association phrases, with a separate left-MTL region for low-association phrases -- concedes earlier "pure composition" effects were confounded with lexical co-occurrence strength. (iv) Methodological critique (Calinescu, Ramchand & Baggio 2023, *Frontiers in Language Sciences*, directly fetched): minimal two-word paradigms have low ecological validity and confounded controls. | Explicitly MEDIUM/contested -- do not treat "LATL=composition" as closed science |

**Bottom line, Section 1:** the most current, most-directly-fetched evidence (Ciapparelli et al. 2025) points to composition-as-**multiplicative/conjunctive feature combination**, not additive summation, for word-level modification composition -- and a role-asymmetric code for full-sentence argument composition (Section 2). This is directly relevant to our own architecture: our `bind` primitive IS a multiplicative (elementwise complex product / circular convolution) operation, not an additive one -- see Section 4 for the honest read-across.

---

## 2. RELATIONAL / STRUCTURED BINDING -- precisely, and an honest FHRR-faithfulness verdict

### 2a. The classical binding problem and its contested resolution

Treisman & Gelade's Feature Integration Theory (1980, *Cognitive Psychology* 12:97-136) is the origin
statement: early sensory maps register features separately; nothing there specifies which feature belongs
to which object ("illusory conjunctions" without attention). The classic proposed neural solution --
**binding-by-synchrony** (von der Malsburg 1981 correlation theory; Singer & Gray 1995, *Annu. Rev.
Neurosci.* 18:555-586, gamma-band ~40Hz stimulus-dependent synchronization) -- is **genuinely, currently
contested, not settled**: Shadlen & Movshon (1999, *Neuron* 24:67-77) is the classic critique (insufficient
temporal precision; failed replications of predicted stimulus-locked oscillations; pushes the binding
problem back a level rather than solving it -- who reads out the synchrony tag?). The most recent
authoritative review, Roelfsema (2023, *Neuron* 111:1003-1019), concludes the weight of evidence now favors
**firing-rate enhancement via object-based attention** over oscillatory synchrony as the actual binding
mechanism -- BUT a 2024 human intracranial study (Garrett et al., *Nature Human Behaviour* 8:1988-2002)
finds positive evidence for high-frequency (~90Hz) "co-ripple" synchrony specifically in
language/semantic-comprehension cortex, timed exactly where predicted for binding during reading. **Net:
domain-dependent and unresolved** -- vision-dominant evidence trends against synchrony-as-the-mechanism;
language-domain evidence (most relevant to our case) is newer and points the other way. Flag as contested,
not use as a load-bearing premise either way.

### 2b. Hippocampal conjunctive/relational binding -- the alternative, better-evidenced answer for cross-talk avoidance

A structurally different (non-timing) answer to "how do you bind A-B without corrupting the also-stored
A-C": dentate gyrus / CA3 achieve **sparse, high-dimensional, near-orthogonalizing conjunctive coding**
(pattern separation) so overlapping inputs are driven to decorrelated codes before CA3's autoassociative
attractor dynamics bind and later complete them (Leutgeb et al. 2007, *Science* 315:961-966; Yassa & Stark
2011, *Trends Neurosci.* 34:515-525, integrative review). O'Reilly & Rudy (2001, *Psychological Review*
108:311-345) formalize this computationally: hippocampus is intrinsically biased toward fast, sparse,
CONFIGURAL coding (each novel co-occurring conjunction gets a near-orthogonal code), vs. neocortex's slow,
overlapping, generalization-favoring codes. Eichenbaum (2004, *Neuron* 44:109-120) generalizes this into
"relational memory theory" -- hippocampus binds elements into events, events into episodes, episodes into
inferable relational networks. This is corroborated by prior in-repo drills (`drill_brain_nonadditive_
interaction...`: A1/A3, same DG/CA3 conjunctive machinery) -- not a new finding this session, but
independently re-confirmed by a fresh lit-scan.

### 2c. Thematic-role-to-filler binding at the neural level -- and a genuine, load-bearing controversy just surfaced

**Frankland & Greene (2015, *PNAS* 112:11732-11737)** -- the single most decisive study for our purposes.
fMRI/MVPA on simple transitive sentences ("the truck hit the ball" vs. "the ball hit the truck"). Found
**distinct, neighboring left mid-superior-temporal-cortex (lmSTC) patches separately and
cross-generalizably encode "who is agent" vs. "who is patient"** -- decoders trained on one verb generalize
to held-out verbs, proving the code represents the ABSTRACT ROLE VARIABLE, not a verb-specific template. The
original authors' own interpretation: role-filler binding works like **"data registers" of a classical
computer** -- spatially SEGREGATED slots, each holding a distributed filler-identity code (an
orthogonal/localist account, explicitly downplaying synchrony as unnecessary for this data).

**Direct empirical challenge to that interpretation, same dataset (Lalisse & Smolensky 2021, arXiv:2110.12342,
directly fetched full text, originally a MACSIM 8 2019 poster -- flag: preprint/poster venue, not confirmed
peer-reviewed-journal-published)**: re-analyzing Frankland & Greene's own Experiment 2 fMRI data (25
subjects, 360 trials), they build an explicit **Tensor-Product-Representation-style encoding model**
(role-vector outer-product filler-vector, then SUPERPOSED/summed across role-fillers) and pit it against the
original "single-pattern" (orthogonal/segregated-register) account. **Result: the superposition/TPR-style
mixed-pattern model decodes BETTER than the orthogonal-register model** in both the agent-selective ROI
(26.1% vs 25.6%, p=.010) and patient-selective ROI (27.3% vs 26.5%, p=.030; chance=25%) -- i.e. thematic-role
bindings in lmSTC look **non-orthogonal and spatially OVERLAPPING/superposed**, directly contradicting
Frankland & Greene's own "segregated data register" reading of their own data. Effect sizes are small
(~1 percentage point above chance) and this is a single, not-yet-independently-replicated study -- treat as
suggestive, MEDIUM confidence, not consensus.

### 2d. HONEST assessment: is our FHRR bind a faithful analog of the brain's relational binding?

Our production primitive (`hdlab/binding.py`): FHRR `bind(a,b) = a * b` (elementwise complex multiply);
`unbind(c,b) = c * conj(b)`; `bundle(vectors)` = per-component-magnitude-renormalized superposition (sum).
This is mathematically HRR/circular-convolution's complex-domain sibling -- exactly the family the VSA
literature (Smolensky 1990 tensor-product binding; Plate 1995/2003 Holographic Reduced Representations,
explicitly the compressed/lossy projection of the tensor product; Eliasmith's Semantic Pointer Architecture,
which implements HRR-style bind+bundle in a biologically-plausible spiking population as a
proof-of-implementability) already proposes as the connectionist-modeling answer to symbolic role-filler
binding.

**The verdict, stated honestly, not overclaimed:**

- **Same algebraic/functional CLASS as the currently best-supported empirical account.** The
  Lalisse & Smolensky finding is directly on point: the neural data for real thematic-role binding (the
  exact "who-did-what-to-whom" problem this audit is about) fits a **superposition of role-filler bindings**
  BETTER than an orthogonal-segregated-register account -- i.e. the functional shape of `role1(x)filler1 +
  role2(x)filler2` (our `bind`+`bundle` composition, and exactly the pattern our `GoalOutcomeRegister` and
  `CausalLinkRegister` already use, per their own docstrings: "same bind/unbind/bundle/cleanup_argmax organ")
  is, on the freshest and most direct evidence located, closer to the real neural code than the
  naive-localist alternative. This is a genuinely strong result for one of our most heavily-used primitives
  -- not aspirational, empirically grounded, though single-study/thin-effect-size and not independently
  replicated (MEDIUM confidence, deflated).
- **NOT a claim of literal mechanistic identity.** No evidence found (and the literature does not claim)
  that cortical neurons literally perform complex-phase elementwise multiplication. The brain's most
  DIRECTLY evidenced binding substrate (Section 2b) is sparse, high-dimensional, near-orthogonalizing
  CONJUNCTIVE-CELL coding (a nonlinear population-code expansion, closer to Rigotti/Fusi's "nonlinear mixed
  selectivity + linear readout" story, already covered in `drill_brain_nonadditive_interaction...`) --
  mathematically a different operation family (population-code sparse expansion) than dense
  phase-vector multiplicative binding. VSA/HRR's own self-understanding in the literature is as a
  *compressed, biologically-IMPLEMENTABLE* analog of tensor-product binding (Eliasmith's SPA proves it CAN
  be run on spiking populations), not as a claim that cortex literally computes it this way.
- **Plain elementwise `bind` alone is COMMUTATIVE and cannot by itself represent role-order/asymmetry** --
  already proven as an architectural wall in prior work (`drill_brain_nonadditive_interaction...`, GHRR
  matrix-vector bind as the validated non-commutative fix). Our production registers avoid this NOT via
  plain `a*b` but via **role-KEYED binding** (a distinct role vector per slot, e.g. GOAL-role bound to the
  goal-holder, OUTCOME-role bound to the affected entity, then bundled) -- this is precisely the
  Smolensky/TPR "sum of role-filler binds" pattern, and precisely what `drill_brain_unifies_symmetric_
  asymmetric_binding_factorization_2026-07-14.md`'s Rank-1 recommendation (shared vector, dual readout lens)
  already independently converged on as the brain-aligned design. So: **the specific way our registers are
  actually built (role-keyed bind + bundle, not naive symmetric bind) is the brain-faithful design**, and
  this session's fresh evidence (Lalisse & Smolensky) is an independent, later confirmation of that same
  prior conclusion from a different literature angle.
- **Where it is genuinely NOT tested / open:** Frankland & Greene's own account (segregated register) and
  Lalisse & Smolensky's account (superposed/distributed) are DIRECT COMPETING interpretations of the SAME
  dataset, not a settled consensus -- and our registers currently store a relatively small, curated set of
  roles (GOAL/OUTCOME/CAUSE/EFFECT), not the full continuous thematic-role space a real neural system
  handles. Whether cross-talk between many simultaneously-bound relations (not just one goal + one outcome)
  degrades gracefully the way superposition-based neural codes are argued to is untested on our substrate.

**P(FHRR bind+bundle+role-keyed-register is a faithful functional analog of thematic-role binding) = 0.55**
(raw ~0.72 on the strength of the direct, on-point Lalisse & Smolensky reanalysis + the independent
convergence with our own prior Rank-1 drill; deflated 0.17 for: single-study/thin-effect-size/unreplicated
status of the key citation, the genuine Frankland-vs-Lalisse&Smolensky interpretive controversy over the
identical dataset, and the acknowledged mechanistic-implementation gap between dense phase-multiplication and
sparse population coding).

---

## 3. SITUATION-MODEL INTEGRATION + INFERENCE -- where "good boy = goal met" actually gets computed

### 3a. The running situation model and its tracked dimensions

Zwaan & Radvansky (1998, *Psychological Bulletin* 123:162-185) event-indexing model: five tracked
dimensions -- time, space, entity/protagonist, causation, and **motivation/intentionality** (goal is a
first-class dimension, not derivative of causation; already independently verified in-repo in
`drill_brain_goal_owner_flow.md`). Trabasso & van den Broek's causal-network model explicitly codes
narrative clauses as Setting/Event/Internal-Response/**Goal**/Attempt/**Outcome** linked causal-network
nodes -- Goal and Outcome are distinct node types in the brain's own narrative representation, which
directly validates our system's goal-typing/outcome-typing separation (already confirmed in-repo).

### 3b. Kintsch's Construction-Integration model -- the mechanism that resolves implicit content

Kintsch (1988, *Psychological Review* 95:163-182; 1998 book) -- two phases: **Construction** (loosely,
promiscuously activate ALL text propositions PLUS associated background knowledge, forming an initially
locally-inconsistent network -- deliberate OVER-generation, not a single committed parse) then
**Integration** (spreading activation acts as constraint satisfaction: propositions coherent with context
mutually reinforce, incongruent/irrelevant ones are inhibited, settling into a stable situation-model
state). This is the textbook mechanism by which IMPLICIT information gets resolved: candidate inferences are
over-generated, then pruned by activation-based fit to the whole discourse, not derived by a single
deterministic logical/lexical rule. Still a live, actively-extended framework (not superseded, though
increasingly reframed in modern predictive-coding/predictive-processing terms as continuous
next-event-prediction with error-driven update -- a reframing of the same core mechanism, not a refutation).

### 3c. Bridging/elaborative inference taxonomy -- exactly which inference class "good boy = goal met" is

Graesser, Singer & Trabasso's constructionist theory (1994, *Psychological Review* 101:371-395; taxonomy
directly fetched via a companion chapter reproducing the primary table) names 13 inference classes. Two are
decisive here:
- **Class 4, Superordinate goal** ("a goal that motivates an agent's intentional action") -- predicted
  **ROUTINE/AUTOMATIC**.
- **Class 7, Causal antecedent** ("bridges the current explicit event/state to previous context via a
  causal chain") -- predicted **ROUTINE/AUTOMATIC**.
- (Class 8, Causal Consequence -- FORWARD prediction of what happens next -- is predicted NOT routinely
  generated; this is the wrong class for our case, which is BACKWARD retrieval of an antecedent goal from a
  later event, not forward guessing.)

The "good boy" case is structurally a **Class-7 backward causal-antecedent bridging inference**: the reader
encounters the praise as an explicit event/state and must retrieve, from earlier context, the antecedent
goal that explains why this praise is occurring -- structurally identical to the taxonomy's own worked
example ("the murderer confessed" -> infer superordinate goal "wanted to turn himself in"). Per
constructionist theory this class is predicted AUTOMATIC; the competing minimalist account (McKoon &
Ratcliff 1992, *Psychological Review* 99:440-466) predicts it is NOT automatic for global-coherence
goal-linking specifically. The debate is unresolved as a strict binary and is now generally treated as a
continuum (automatic -> routine -> strategic), with working-memory-span evidence (St. George, Mannes &
Hoffman 1997) suggesting goal-antecedent/bridging inferences are the MORE robust, less
individual-difference-sensitive class -- i.e. even under the more conservative reading, this specific
inference class is among the more reliably-generated ones, not a rare/optional edge case. **Directly
relevant, MEDIUM-HIGH confidence: this is squarely the SAME evidence class already used in-repo
(`drill_brain_goal_owner_flow.md`'s Trabasso/Graesser generative goal-inference finding) to argue our
lexically-gated goal-typing is too narrow -- this session's finding extends that: it is not just goal-FROM-
ACTION inference that's missing, it's goal-outcome-FROM-EVALUATIVE-SPEECH-ACT bridging specifically.**

### 3d. Schema-based forward prediction -- Event Segmentation Theory and the posterior-medial system

Event Segmentation Theory (Zacks, Speer, Swallow, Braver & Reynolds 2007, *Psychological Bulletin*
133:273-293): perception continuously generates PREDICTIONS about what happens next using both low-level
cues and learned SCHEMA/SCRIPT knowledge (including inferred actor goals/plans); a transient spike in
prediction error flags the current event model as inadequate, triggers updating (subjectively an "event
boundary"), and schema retrieval. Ranganath & Ritchey (2012, *Nat. Rev. Neurosci.* 13:713-726) PMAT
framework: the **posterior-medial (PM) system** (parahippocampal, retrosplenial, posterior cingulate,
angular gyrus, precuneus, **mPFC**) -- not the anterior-temporal/item system -- is the proposed carrier of
CONTEXTUAL/SCRIPT/RELATIONAL structure used for exactly this kind of prediction. Direct empirical support:
Baldassano et al. (2018, *J. Neurosci.* 38:9689-9699) find mPFC + posterior medial cortex patterns
GENERALIZE across different stories sharing the same script (e.g. restaurant, airport), decodable at high
accuracy from mPFC via HMM, and DEGRADE when event order is scrambled -- direct evidence mPFC carries
abstracted, temporally-structured script knowledge used predictively. **This is precisely the missing piece
for "praise from an authority figure typically follows successful task completion"** -- a social-script
prior that would need to live in exactly this system. No direct evidence located that this specific
social-evaluative script has been studied (see 3f) -- but the GENERAL mechanism (script-carrying PM/mPFC
system, prediction-error-driven updating) is well-evidenced.

### 3e. Pragmatic/social inference -- interpreting the speech act itself, not just its literal content

A mentalizing/Theory-of-Mind network (bilateral TPJ with rTPJ emphasis, dmPFC, precuneus/PCC) is reliably
recruited whenever comprehension must go BEYOND literal sentence meaning to infer speaker intent -- Spotorno,
Koun, Prado, Van der Henst & Noveck (2012, *NeuroImage* 63:25-39): irony comprehension (literal meaning must
be overridden by inferred attitude) selectively engages this network beyond literal-but-implausible control
statements. Jacoby & Fedorenko (2020, *Language, Cognition and Neuroscience* 35(6)): ToM regions (dmPFC/PCC)
activate for coherent MULTI-SENTENCE discourse even in non-narrative expository text -- i.e. this network is
recruited for building inter-sentential coherence generally, not just for mental-state content specifically.
The language network (IFG, MTG/STG -- literal semantic composition) and the ToM network (TPJ, mPFC --
pragmatic/intent inference) are functionally/anatomically DISSOCIABLE but coupled systems (Fedorenko lab,
2019, *J. Neurophysiology*). **Directly relevant new evidence for social-relation integration**:
Van Berkum et al. (2008, *J. Cognitive Neuroscience*) show a listener's model of WHO is speaking (social
category/role) is integrated INCREMENTALLY and EARLY (~200-300ms N400 effects), in parallel with literal
composition, not as a late separate step. Bornkessel-Schlesewsky, Krauspenhaar & Schlesewsky (2013, *PLOS
ONE* 8:e69173): a speaker's social AUTHORITY/potency to act on their words modulates early (150-450ms) N400
falsity-sensitivity -- WHO says something changes how its content is integrated, in the same early time
window as semantic composition, not after. This is direct evidence the brain treats "the mother said this"
as load-bearing input to meaning construction from the earliest measurable stage, not a late add-on.

### 3f. The genuine, explicitly-flagged gap -- no study integrates all three

**No study located tests the specific three-way integration our trigger case needs: (1) an established
antecedent goal-state, (2) a later evaluative speech act (praise/blame) from a specific social-role speaker,
(3) social-relation/authority knowledge -- combined into an inferred goal-outcome.** This is stated as an
explicit, honest literature gap by the dedicated lit-scan sub-agent, not papered over. What exists are three
well-studied ADJACENT pieces (goal-tracking/Class-7 bridging per 3c; schema/script prediction via PM/mPFC
per 3d; speaker-intent/authority integration via ToM+language-network coupling per 3e) with a plausible but
UNTESTED composite mechanism: these three systems are each independently well-evidenced and known to
interact, but no paradigm has shown them jointly computing THIS inference class. Flagged explicitly as
HYPOTHESIS-PENDING-VET, not an established finding.

---

## 4. THE PRECISE GAP vs OUR IMPLEMENTATION -- SHAPE/POSITION/METRIC, honest FAITHFUL-vs-MISSING split

Grounded in the disk-verified component map (`deep_vet_comprehension_organ_vs_brain_2026-08-05.md`,
`brain_audit_SYNTHESIS_missing_semantic_organ.md`) plus this session's fresh literature.

### FAITHFUL (real, not aspirational -- brain-analogous in SHAPE and/or METRIC)

| Our component | SHAPE/METRIC | Brain analog | Verdict |
|---|---|---|---|
| `hdlab/binding.py` `bind`+`bundle`, and role-keyed registers (`GoalOutcomeRegister`, `CausalLinkRegister`) built as `role1(x)filler1 + role2(x)filler2` | Multiplicative role-filler binding (elementwise complex product / circular convolution), superposed via bundle | Compressed/VSA analog of Smolensky tensor-product binding; DIRECTLY favored over an orthogonal-register alternative by Lalisse & Smolensky's 2021 reanalysis of real thematic-role fMRI data (Section 2c/2d) | FAITHFUL (functional class), P=0.55 deflated, single-study caveat |
| Goal-typing / outcome-typing as DISTINCT node types (not one flat "event" label) | Component-3/5 pipeline separates GOAL from OUTCOME | Trabasso/van den Broek causal-network model's own Goal vs. Outcome node distinction (Section 3a) | FAITHFUL |
| Outcome-valence = goal-congruence comparison (landed HARD_PASS, `hdlab/goal_typing.py` desired-state vs. actual-state on shared referent, per `drill_brain_outcome_valence_goal_congruence_2026-08-06.md`) | Compare `(theme, result_verb_class)` desired vs. actual | Scherer/Roseman goal-conduciveness appraisal, dissociable from intrinsic word valence | FAITHFUL |
| Coreference (event-role centrality default) | Bottom-up event-centrality candidate resolution | Plausible analog of hippocampal event-based antecedent retrieval; independently the strongest-measured organ (HARD_PASS on its own instrument) | FAITHFUL AS FAR AS IT GOES -- but see MISSING row below (it is bottom-up only) |

### MISSING (the true inferential situation-model gap -- this is the barrier)

| Gap | What the brain does (this audit) | What we have | Consequence |
|---|---|---|---|
| **No construct-then-integrate loop** | Kintsch CI: over-generate candidate propositions/inferences, then prune via spreading-activation constraint satisfaction against the WHOLE situation model (Section 3b) | Feedforward, one-shot-per-clause pipeline (deep_vet META-PATTERN 1): each organ computes once locally and hands off a flat result; nothing is over-generated then pruned by global coherence | Cannot resolve implicit content that requires weighing multiple candidate readings against distant context |
| **No schema/script-based forward prediction** | Event Segmentation Theory: schema generates a prediction, prediction-error against incoming input drives update (Section 3d); PM/mPFC carries the script library (Baldassano et al.) | `predictive_coding.py` exists, right SHAPE (predict->residual->gated_write) but ZERO hdlab consumers (islanded, per deep_vet #6); AND no script/schema KNOWLEDGE layer exists at all -- this is a compound gap (missing wiring + missing knowledge), not wiring alone | Cannot predict "praise from an authority typically follows task success" as a prior; every inference is post-hoc from local cues only |
| **No bridging-inference path across NON-lexical (pragmatic/social) links** | Graesser Class-7 causal-antecedent bridging is not restricted to shared lexical items -- readers link a later event back to an earlier goal via CONTENT/CAUSAL reasoning, whatever form it takes (Section 3c) | Our goal-owner + outcome-valence machinery is verified to require a lexical/thematic PATH: `clause_theme`/`entity_goal_themes` (shared referent), `RESULT_VERB_CLASS` (shared or opposed verb class). "You are a good boy" shares NO verb, NO theme, NO thematic role with any goal clause -- there is nothing for these mechanisms to match on | This is the SHARPEST, most concrete instance of the missing inferential layer: not a coverage gap in an existing mechanism, but the total ABSENCE of a mechanism class (evaluative-speech-act -> goal-outcome bridging) |
| **No mentalizing/pragmatic illocutionary-force layer** | rTPJ/dmPFC mentalizing network interprets a speech act's INTENT (this is praise, sincere, directed at outcome X) as distinct from its literal semantic content (Section 3e) | ToM sally-anne module exists and is HARD_PASS-proven (Q2=0.806) but ISLANDED (zero consumers, per deep_vet's own roadmap note); no speech-act/illocutionary-force classifier exists at all | Cannot distinguish praise from criticism from irony, cannot attach an evaluative utterance to "approval of a prior act" |
| **No early speaker-identity/authority integration** | Van Berkum / Bornkessel-Schlesewsky: WHO is speaking (social role/authority) is integrated with content from the earliest stage (~200-300ms), not late (Section 3e) | Social-relation knowledge (e.g. "mother" = caregiver/authority) is not represented or consulted anywhere in the pipeline | Even if praise were detected as praise, there is no mechanism to weight it by the speaker's social standing relative to the goal-holder |
| **Composition operates over hand-authored/frame-slot inputs, not an earned amodal hub** | LATL/LIFG composition (Section 1) operates over rich, graded, cross-modal concept features (the ATL-hub) | The ATL-hub gap is already independently identified (`drill_brain_atl_lexical_semantic_hub_2026-08-06.md`) -- Random Indexing exists, MIDDLE_BAND, unwired | The composition ALGEBRA (bind/bundle) is faithful, but its current INPUTS are impoverished relative to what LATL/LIFG actually compose over |

---

## Cheap decisive test

Build a small (N=10-15) hand-authored bank of "pragmatic-bridging outcome" items structurally like the
trigger case: a goal clause (character wants X), then an OUTCOME clause that is a purely evaluative speech
act from a socially-marked speaker (praise/criticism, e.g. "His mother said, 'You did a good job.'"), with
**zero shared lexical item, verb class, or thematic role** between the two clauses (so the existing
theme-match/`RESULT_VERB_CLASS` mechanism cannot fire on lexical grounds at all). Run:
(a) the current production outcome-valence mechanism (goal-congruence, `hdlab/goal_typing.py`) -- expect it
to ABSTAIN (theme-mismatch guard) on every item, since there is no shared referent/verb-class to match.
(b) a minimal proposed bridging mechanism: SUPPLY a small hand-authored `EVALUATIVE_SPEECH_ACT` register
(PRAISE-class predicates: "good job," "well done," "proud of you," etc. -> positive evaluation of a
PRIOR unspecified act by the addressee; CRITICISM-class -> negative) + a check that the addressee currently
holds an OPEN goal in the persistent register (reuse `GoalOutcomeRegister`) + bind PRAISE-directed-at-X to
MET / CRITICISM-directed-at-X to UNMET for X's most recent open goal, gated on the speaker being a distinct
entity from the goal-holder (a minimal social-relation stand-in; full authority-modeling is out of scope for
this cheap test).

**HARD-PASS**: bridging mechanism (b) correctly resolves >=70% of the bank to the gold MET/UNMET label,
strictly beating (a)'s abstain-everywhere baseline by >=0.50 absolute; a scramble control (shuffle which
open-goal register the praise/criticism event is checked against) collapses accuracy to within 0.15 of the
item-set base rate.

**HARD-FAIL**: bridging mechanism (b) does not beat (a) by >=0.25 absolute, OR scramble does not collapse
(mechanism secretly keying off surface praise/criticism words alone rather than the open-goal binding, the
exact failure mode this test exists to catch).

This is deliberately the SMALLEST possible increment that tests whether a bridging path exists AT ALL
(evaluative-speech-act -> goal-outcome, no lexical/thematic overlap required) -- it does NOT attempt the
full schema-prediction or speaker-authority layer (Sections 3d/3e), which are larger, separate builds.

## Falsifiable predictions

- **HARD-PASS (this audit's central claim -- FHRR bind+bundle+role-keyed-register is the brain-faithful
  relational-binding mechanism, composition/binding is NOT the barrier)**: the cheap decisive test above
  clears HARD-PASS using ONLY the already-owned bind/bundle/register primitives (no new binding operator
  needed) -- confirms the algebra is sufficient once given the right INPUT (an evaluative-speech-act signal),
  consistent with this audit's Section 2/4 verdict.
- **HARD-FAIL**: the bridging mechanism (b) cannot be built as a strict ADD-ON to the existing
  bind/bundle/register primitives and instead requires a structurally different binding operator -- would
  falsify the audit's core claim that binding/composition is already faithful and the gap is purely
  inferential/knowledge-layer.

## Cross-thread synthesis

- Directly extends `drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md` and
  `drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md`: this session's fresh
  Lalisse & Smolensky citation is an INDEPENDENT, later confirmation (different literature entry point --
  direct fMRI reanalysis rather than theoretical synthesis) of those drills' Rank-1 conclusion (role-keyed
  bind + bundle, joint code with selective readout, is the brain-aligned design) -- convergent evidence
  across two separate research passes, which raises rather than lowers confidence in that specific design
  choice.
- Directly extends `drill_brain_goal_owner_flow.md`: that drill established the brain's goal-attribution is
  GENERATIVE (infers goals from action sequences with no goal-word present) where ours is lexically gated.
  This audit's Section 3c/3f finding is the OUTCOME-side mirror of the same problem: the brain's
  outcome-to-goal BINDING is also generative/inferential (works across non-lexical evaluative/social links)
  where ours requires a lexical/thematic path. Same structural gap class, opposite end of the goal-owner
  pipeline.
- Directly extends `drill_brain_outcome_valence_goal_congruence_2026-08-06.md`'s "COVERAGE WALL" finding
  (referent binding fails on pronoun/synonym/multi-object cases, fixed via coref+concept-similarity wiring)
  -- this audit identifies a DEEPER coverage wall one level up: even PERFECT referent binding cannot help
  when there is no lexical/thematic referent-and-verb-class relationship to bind AT ALL (the "good boy" case
  has no verb corresponding to any RESULT_VERB_CLASS entry).
  Also converges with `deep_vet_comprehension_organ_vs_brain_2026-08-05.md`'s META-PATTERN 1
  (feedforward/local pipeline vs. the brain's recurrent/top-down-gated loop) and its islanded
  `predictive_coding.py` + islanded ToM (sally_anne) findings -- this audit supplies the missing
  BRAIN-MECHANISM detail for WHY those two islanded pieces matter together: ToM supplies illocutionary-force
  interpretation (Section 3e), predictive_coding's SHAPE (predict-then-observe) is the right pattern for
  schema-based forward prediction (Section 3d) IF it is fed script/schema content, which does not yet exist
  anywhere in the substrate.

## Substrate-product implications

- **Do not build a new binding/composition operator.** This audit's clearest actionable finding: the
  existing `bind`+`bundle`+role-keyed-register machinery is adequately brain-faithful for relational binding
  (Section 2d, P=0.55 deflated) and for word-level multiplicative composition (Section 1, consistent with
  Ciapparelli et al. 2025's multiplicative-beats-additive finding). Effort spent on a new composition
  algebra would not address the identified barrier.
- **The next buildable increment is small and concrete**: the cheap decisive test above (evaluative-speech-
  act -> goal-outcome bridging register) is a strict ADD-ON, reuses `GoalOutcomeRegister` unmodified, and is
  scoped exactly like the already-landed desiderative-partition and goal-congruence fixes (small hand-
  authored register + a composition step, not a new mechanism class) -- same "used-ability-wrong /
  missing-FACT SUPPLY" routing as those prior wins, NOT missing-LEARNING.
  The cheap decisive test above is itself the next dispatch candidate -- a small build for exp_dev pickup,
  not a further research question.
- **Larger, longer-horizon targets named but explicitly NOT the next move**: (a) wiring `predictive_coding`
  to a genuine script/schema library (needs the schema-content problem solved first -- likely a
  supply-a-small-hand-authored-script-set project analogous to the RESULT_VERB_CLASS register, scaled up);
  (b) wiring the already-HARD_PASS ToM sally-anne module as an illocutionary-force classifier upstream of
  outcome-valence; (c) a Kintsch-style construct-then-integrate loop, which is the largest and most
  architecturally invasive of the three (would require the pipeline to over-generate candidate readings
  before committing, a genuine departure from the current one-shot-per-clause design) -- correctly the
  lowest-priority of the three per do-the-hard-blocking-thing-but-sequence-by-what-actually-blocks
  discipline, since (a) and (b) are smaller, already-owned-capability reuse and should be tried first.
- **Honest scope**: this audit's cheap decisive test targets ONLY the narrowest instance of the inferential
  gap (evaluative-speech-act bridging with no social-authority weighting). Even a full HARD-PASS there would
  NOT close Section 3d (schema-based forward prediction) or the social-authority-weighting half of Section
  3e -- those remain open, larger builds.

## Citations (verified count)

**This note's own new citations (3 parallel lit-scan sub-agents, this session, generic-terms-only per
query-privacy discipline):**
- Directly fetched / high confidence (8): Hagoort MUC (PMC3709422); Calinescu, Ramchand & Baggio (2023,
  *Frontiers in Language Sciences*); Li & Pylkkanen (2021, *J. Neurosci.* 41:6526-6538); Ciapparelli, Marelli,
  Graves & Reverberi (2025, *Cerebral Cortex* 35:bhaf246); Frankland & Greene (2015, *PNAS* 112:11732-11737,
  full text via PMC); Lalisse & Smolensky (2021, arXiv:2110.12342, via ar5iv); Graesser, Singer & Trabasso
  (1994, *Psychological Review* 101:371-395, taxonomy table verified via companion chapter); Graesser,
  Louwerse, McNamara, Olney, Cai & Mitchell (2005 book chapter, full PDF).
- Verified via search / secondary-source, not full-text fetched (~28): Bemis & Pylkkanen (2011, 2013); Zhang
  & Pylkkanen (2015); Del Prato & Pylkkanen (2014); Westerlund & Pylkkanen; Murphy et al. (2022, *J.
  Neurosci.* 42:3216-3227); Fló et al. (2020); Kochari et al. (2021); Pylkkanen (2020, *Phil. Trans. R. Soc.
  B*); Bastiaansen, Magyari & Hagoort (2010); Frankland & Greene (2020, *Cerebral Cortex* + *Annu. Rev.
  Psychol.*); Treisman & Gelade (1980); von der Malsburg (1981); Singer & Gray (1995); Shadlen & Movshon
  (1999); Roelfsema (2023, *Neuron* 111:1003-1019); Garrett et al. (2024, *Nature Human Behaviour*);
  Leutgeb et al. (2007); Yassa & Stark (2011); O'Reilly & Rudy (2001); Eichenbaum (2004); Giglio, Hagoort &
  Ostarek (2024, *Cerebral Cortex*); Smolensky (1990); Plate (1995/2003); Eliasmith SPA; McKoon & Ratcliff
  (1992); Kintsch (1988, 1998); Schmalhofer, McDaniel & Keefe (2002); Zacks, Speer, Swallow, Braver &
  Reynolds (2007); Ranganath & Ritchey (2012); Baldassano et al. (2018); Spotorno, Koun, Prado, Van der
  Henst & Noveck (2012); Jacoby & Fedorenko (2020); Van Berkum et al. (2008); Bornkessel-Schlesewsky,
  Krauspenhaar & Schlesewsky (2013); Wu & Cai (2025/2026).
- Explicit gaps flagged (not evidence of absence): no direct study of a social-evaluative script
  ("praise follows success") in the PM/mPFC prediction literature; no study integrating goal-state +
  evaluative-speech-act + social-relation into one inference paradigm (Section 3f); LATL-LIFG division of
  labor not reconciled in any single source; synchrony-binding status genuinely domain-dependent/unresolved.

**Reused, already-verified in-repo citations** (not re-fetched this session, full lists in the source notes):
`drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md` (~34 citations),
`drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md` (~23 citations),
`drill_brain_goal_owner_flow.md` (~10 citations), `drill_brain_outcome_valence_goal_congruence_2026-08-06.md`
(~27 citations).

**Total this note: ~44 new external citations (8 directly fetched, ~28 search-verified secondary, several
explicit gaps) + 4 in-repo prior drills reconciled/extended (~94 additional citations by reference, not
re-verified).**

## P_deflated (overall, this audit's central claim)

**P(composition/binding is faithful, the barrier is specifically the inferential/situation-model layer) =
0.50** (raw ~0.68: the Section 2 FHRR-faithfulness finding is well-triangulated across two independent
literature passes plus a direct fMRI reanalysis; the Section 4 gap analysis is directly disk-verified against
this substrate's own code, not speculative. Deflated by the standard 0.18 for: (i) the load-bearing
Lalisse & Smolensky citation is a single, small-effect-size, not-independently-replicated study genuinely
contested by the original authors' own opposing interpretation of the same data; (ii) the Section 3f
three-way-integration gap is a novel synthesis composing three independently-evidenced but never-jointly-
tested literatures, capped at the standard novel-synthesis ceiling of 0.50 -- the cap is binding here, not
just the deflation.)

---

## Bottom line

**We are faithful where it matters most for an audit this deep to be reassuring: the FHRR bind/bundle
primitive and the role-keyed registers built from it (GoalOutcomeRegister, CausalLinkRegister) sit in the
same functional class as the most-directly-evidenced current account of neural thematic-role binding
(Lalisse & Smolensky's 2021 reanalysis of Frankland & Greene's data favors exactly this superposition-of-
role-filler-binds shape over a segregated-register alternative) -- no new binding operator is needed.**
**The real wall is inferential: the brain closes gaps like "praise from mother = goal met" via a
construct-then-integrate loop (Kintsch), schema-based forward prediction (Event Segmentation Theory, carried
by a posterior-medial/mPFC script system), and Class-7 causal-antecedent bridging inference that does NOT
require any shared lexical item or thematic role between the goal and the outcome clause -- and our
substrate currently has none of these three layers, with the missing bridging-across-non-lexical-links piece
being the single sharpest, most concrete, and cheapest-to-test next increment.**
