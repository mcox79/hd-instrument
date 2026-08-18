# IS A COARSE, CORRUPTION-TOLERANT ROLE PROFILE WHAT CORTEX COMPUTES?

**Research drill, 2026-08-18, on the landed `5170c7751`
(`exp_typed_role_context_write_rule_dissociation_v1`, plan 6.39). LEADS WITH BIOLOGY. Authored no
cell, ran no experiment cell, dispatched nobody, edited no `experiments/**`, no `preregs/**` and no
`arm_key*` file.**

**It DID run a read-only post-hoc diagnostic** over the cell's own persisted `units.jsonl`
(`tools/diagnose_role_profile_is_category_detector.py`, promoted out of `scratch/` because this note
cites its numbers). Every number below is either read off the landed `metrics.json` or produced by
that script, whose first act is to **reproduce the landed AUCs exactly from the persisted arc
events** as a fidelity check. It did.

---

## 0. THE HEADLINE, BEFORE ANY BIOLOGY

**BOTH READINGS ARE PARTLY RIGHT, AND THE EVIDENCE SEPARATES THEM CLEANLY.**

1. **The coarse role signal is REAL.** It is not a coverage artifact and it is not a collocate
   detector. It survives every control I could invent, including two the cell did not run.
2. **But two of the three things we are saying about it are wrong.** The *corruption tolerance* is a
   property of how the corruption was drawn, not of the representation. The *`U1 == U3` tie* is what
   a starved lexical channel looks like, not evidence that word identity is unnecessary.
3. **And the biology does not say what we are about to say it says.** Cortex demonstrably computes
   something in this family -- but it uses it to CONSTRAIN a meaning hypothesis during acquisition,
   and assigns the substitutability code itself to a **different organ**. We have replicated the
   acquisition-stage category signal and are on the verge of calling it the similarity code.

---

## 1. ANSWER TO QUESTION 2 (THE DECISIVE ONE) -- WITH THE CONTROLS THAT DECIDE IT

### 1.1 What landed, read off disk

`data/exp_typed_role_context_write_rule_dissociation_v1/metrics.json`, `run_mode: full`, bar
(max of four floors) **0.5431**, corpus 34,169 sentences, 80,056 arc events, parser UAS 0.7868
(cited, not recomputed):

| arm | context identifier | vocab | AUC | CI95 |
|---|---|---|---|---|
| `U1_TYPED_CONTEXT` | (neighbour, relation, direction) | 21,093 | **0.6669** | [0.6184, 0.7136] |
| `U3_ROLE_ONLY` | (relation, direction) -- **word discarded** | **64** | **0.6466** | [0.5977, 0.6936] |
| `T2_UNTYPED_SAME_COVERAGE` | neighbour only | 7,150 | 0.6128 | [0.5614, 0.6622] |
| `N1_LABEL_PERMUTED` | -- | 38,064 | 0.5564 | [0.5052, 0.6071] |
| `N2_RANDOM_TYPING` | -- | 50,084 | 0.5602 | [0.5098, 0.6116] |
| `A0_INCUMBENT` (bag of words) | -- | 17,377 | 0.0510 | -- |
| `S1_SLOT_COMPETITION` | supervised | 17,377 | 0.0695 | [0.0475, 0.0940] |
| `N3_MAGNITUDE_PERMUTED` | its control | 17,377 | 0.0591 | [0.0396, 0.0808] |

Paired: `U1 vs U3` **+0.0203 [-0.0185, +0.0591] NOT SEPARATED**; `U1 vs T2` +0.0541 [0.0339, 0.0753]
separated; `U1 vs N1` +0.1105 [0.0800, 0.1420] separated.

### 1.2 The three controls the cell did not have, and what they say

All from `tools/diagnose_role_profile_is_category_detector.py`, seed 20260818, 2,000-resample paired
bootstrap. **Fidelity gate first: reconstructing the profiles from the persisted `arc_events`
reproduces `U1 = 0.6669` and `U3 = 0.6466` to four decimals**, and reconstructing the bag channel
reproduces `A0 = 0.055` against a landed 0.0510. The reconstruction is faithful, so the controls
below are about the same object the cell measured.

**CONTROL A -- is it just a collocate detector?** I built `SET_R`: 242 random pairs from the same 617
eval words, zero co-occurrence, neither WordNet-synonym (P) nor high-co-occurrence (S). My hypothesis
going in was that the arm merely detects "these two are not complementary parts of one construction"
-- P and S nouns occupy systematically different head/dependent positions.

> `AUC(R > S)` = **0.4838 [0.4322, 0.5373]** (U1) and **0.5133 [0.4605, 0.5641]** (U3).

**My hypothesis is refuted.** Random pairs do NOT beat collocates. Something specific to synonymy is
being read. *(The positional story is real but partial: mean |head-share(a) - head-share(b)| is
**P 0.1142 < R 0.1970 < S 0.2313** -- S pairs really are the most positionally complementary, but R
sits between and still loses.)*

**CONTROL B -- the floor the cell imported was the wrong floor.** The cell's bar carries
`F_FREQUENCY = 0.4901`, recomputed on the pair population but under the OLD representation. I
reproduce that on bag occurrences (**0.4893**). But under the arc representation actually being
scored, an attestation floor -- *how well attested is the WEAKER partner*, `log(min(arc_mass))`, no
word identity, no context, no meaning --

> reads **`AUC(P > S) = 0.6317 [0.5820, 0.6781]`**, statistically indistinguishable from the
> `U3_ROLE_ONLY` headline of 0.6466.

The cell's own `N5` coverage control did not catch this: `U1_COVERAGE_MATCHED` reads 0.6669 on
**242/242 pairs** -- `COVERAGE_MIN = 3` dropped nobody. A presence threshold is not a mass match.
**This is a general lesson, not a local one: a floor is a property of the SCORER AND THE
REPRESENTATION, not of the pair population. Importing it because "the population is identical" is
exactly wrong when the representation is the variable under test.**

**CONTROL C -- and the effect survives it anyway.** Mass-matched subsample, greedy 1-1 on both
partners' log arc mass, n = 189 pairs per side, residual attestation floor **0.507 [0.4477,
0.5665]**:

> `U3_ROLE_ONLY` **0.6369 [0.5822, 0.6911]**; `U1_TYPED_CONTEXT` **0.6284 [0.5717, 0.6843]**.

**The headline loses about one point to the artifact and keeps the rest.** And on a
frequency-matched synonym-vs-random contrast that removes the S set entirely:

> `AUC(P > R2_freq_matched)`: `U3` **0.5958 [0.5458, 0.6458]**, `U1` **0.6209 [0.5706, 0.6707]**,
> against recomputed floors `F_ATTEST_SIM` 0.5141 and `F_ATTEST_MIN` 0.5053 (both CI-overlapping
> 0.50).

**A 64-bin grammatical-role histogram, with word identity thrown away, separates WordNet synonym
pairs from frequency-matched random noun pairs, CI-separated above the strongest floor recomputed on
that same comparison.** That is a genuine, if modest, substitutability signal in a code that contains
no words.

### 1.3 The two claims that do NOT survive

**(i) "Corruption-tolerant" is an artifact of the corruption model.** The cell reports
0.6669 -> 0.6649 -> 0.6603 -> **0.6507** at 0%/10%/25%/50% arc corruption. I re-ran three corruption
models on the reconstructed profile:

| model (50% of ALL arcs) | U1 | U3 |
|---|---|---|
| replace the relation label from the global marginal | 0.6386 | 0.6575 |
| replace the neighbour lemma from the global marginal | 0.6534 | 0.6466 |
| **replace BOTH** | **0.6479** | **0.6648** |

**Destroying both channels of half the arcs costs about two points.** The reason is structural:
replacements drawn from the *global marginal* add the SAME vector to every word's profile, and adding
a shared component to all items is close to rank-preserving for a rank-sum AUC. **`N6_PARSE_NOISE` as
built is very nearly incapable of failing, so its pass is not evidence.** The cell's `N1_LABEL_
PERMUTED` (0.5564) is the control that actually bites, and it bites only on U1's typed pairing --
nothing in the cell tests whether U3's role marginal itself is the carrier. My Control C is now that
test, and U3 passes it.

**(ii) The `U1 == U3` tie is a data-poverty signature, not a finding about word identity.** Median
arc count per word is **130**; median distinct occupied `(relation, direction)` bins per word is
**18**. A 21,093-dimensional typed context space cannot be populated by 130 observations. **The typed
profile IS a role profile plus sampling noise, by arithmetic.** The tie is predicted by sample size
alone and licenses nothing about whether the lexical channel matters.

### 1.4 And how coarse is coarse

Truncating the 64-bin profile to its top-k bins:

| k | 1 | 2 | 3 | 5 | 16 | 64 | binary presence (counts discarded) |
|---|---|---|---|---|---|---|---|
| `AUC(P>S)` | 0.5269 | 0.5851 | **0.6240** | 0.6260 | 0.6370 | 0.6466 | 0.6282 |

**Three relation bins carry 96% of it, and the counts are nearly discardable.** A single categorical
bin (top-1, i.e. a distributional part-of-speech tag) carries almost none of it (0.5269). So the
effective code is *"which two or three grammatical jobs does this word do at all"* -- coarser than a
POS tag set, and finer than a single category label.

### 1.5 The verdict on question 2, stated plainly

**The result is a genuine, very coarse, distributional-syntax signal -- and it is NOT the thing the
brain uses for substitutability.** Both readings in the brief are wrong in their strong forms:

- *"We accidentally replicated something real about how the brain codes distributional syntax"* --
  **partly true, and this is the half worth keeping.** Coarse distributional-frame information really
  does support grammatical-category induction, and that is pinned in acquisition (section 3).
- *"Our representation is too weak to carry anything finer"* -- **also true, demonstrably**: 130 arcs
  per word cannot populate 21,093 dimensions, so we have not tested whether anything finer exists in
  our data. **The lexical channel was starved, not falsified.**
- **The reading the evidence actually favours, and neither option in the brief states it:** cortex
  computes coarse role/frame information and uses it as a **CONSTRAINT ON A MEANING HYPOTHESIS**,
  while the substitutability code itself is computed by a **different, feature-based organ**. We have
  built the constraint and are scoring it as though it were the code.

---

## 2. QUESTION 1 -- HOW CORTEX REPRESENTS A WORD'S GRAMMATICAL ROLE

Marked PINNED-BY-EVIDENCE / OPEN / OUR-INVENTION throughout, per the standing rule.

**PINNED -- role information is decodable, and topographically biased.** Frankland & Greene (2015,
PNAS) used MVPA on two fMRI experiments and found **neighbouring subregions of left mid-superior
temporal cortex** whose activity patterns carry the identity of the current **agent** (upper bank of
the superior temporal sulcus) and the current **patient** (lateral bank of the superior temporal
gyrus), generalising across sentences. Wurm & Caramazza (2019, *Nat. Commun.*) found **left lateral
posterior temporal cortex** encoding action representations that generalise **across observed scenes
and written descriptions**, with the representational geometry predicted by agent-patient relational
models -- i.e. abstract of both modality and surface form.

**PINNED -- structure, not merely processing load, is visible.** Reddy & Wehbe (NeurIPS 2021) built
constituency-subgraph structural embeddings and showed they predict fMRI better than the standard
effort metric (node count), with syntax processing distributed across the language network. Pasquiou
et al. (2023) reach a compatible conclusion with information-restricted language models.

**PINNED -- grammatical class is available early and is not reducible to meaning.** MEG on
noun/verb homonyms shows distinguishable correlates not explained by word meaning; grammatical class
modulates left inferior frontal gyrus from **~80-100 ms** when the syntactic context is predictive.

**PINNED -- and this is the one that matters most for us: the ORGAN THAT COMPUTES SUBSTITUTABILITY IS
NOT THE ORGAN THAT COMPUTES ROLE.** The dual-hub dissociation is supported by lesion localisation
(taxonomic errors -> left anterior temporal lobe; thematic errors -> left temporoparietal junction),
by fMRI (taxonomic similarity modulates ATL, thematic relatedness modulates supramarginal gyrus), by
TMS, and by intracranial EEG with distinct oscillatory signatures for taxonomic overlap (ATL) versus
thematic relations (pMTG). **Our instrument's SET_P (WordNet synonyms and co-hyponyms, zero
co-occurrence) is the taxonomic axis and SET_S (high co-occurrence, shared domain) is the thematic
axis. Our instrument is the dual-hub dissociation, measured in a corpus.** The arm that won it is
built out of verb-argument role structure -- which is the pMTG/AG side, i.e. the **thematic** organ
being asked to do the **taxonomic** organ's job.

**OPEN -- is role represented SEPARATELY from the word filling it?** Genuinely unresolved, with two
strong competing accounts, both with published objections.

| account | evidence for | objection |
|---|---|---|
| **Dedicated role registers** (Frankland & Greene) -- role has an address, fillers are written into it | MVPA agent/patient subregions; cross-modal generalisation of agent-patient geometry in LPTC | A reanalysis of F&G's own ROIs ("Distributed neural encoding of binding to thematic roles", arXiv 2110.12342) finds the neural instantiations of filler-to-role bindings are **non-orthogonal and spatially overlapping** -- not what separate registers predict |
| **No separable syntactic code at all** (Fedorenko et al. 2020, *Cognition*) | Three fMRI experiments with individual-subject localisers; **no region responds more strongly to syntactic than lexico-semantic processing** anywhere in the language network (syntactic d = 0.33-0.72, lexico-semantic d = 0.59-1.37); 5 of 6 regions favour lexico-semantics | The authors themselves note abstract syntactic representations may exist and be undetected by their manipulations; and their contrast is region-level response magnitude, which is not the same instrument as pattern decoding |

**OUR-INVENTION-UNDER-TEST -- the code.** **No recording shows a role vector and a filler vector
combined by an algebraic binding operation.** This is the project's own 2026-08-16 finding and it
applies here verbatim. It also applies to our new result in a specific way: **nothing in the
literature shows cortex maintaining a per-word histogram over dependency-relation types.** The
`(relation, direction)` context identifier is ours. Say so in every downstream document.

---

## 3. QUESTION 3 -- DOES THE BRAIN DERIVE SUBSTITUTABILITY FROM ROLE PROFILES?

**Split the question, because the honest answer is different for each half.**

### 3.1 For SYNTACTIC CATEGORY: yes, and the learning signal is unsupervised distributional structure

**PINNED (behavioural/computational, in acquisition).** Mintz (2003) showed **frequent frames** --
two words bracketing one intervening word, `you __ it` -- yield very accurate grammatical categories
from child-directed speech; cross-linguistic follow-ups (Chemla, Mintz, Bernal & Christophe, 2009,
English and Spanish) report the categorised word types covering **~50% of corpus tokens from ~6% of
contexts**. Redington, Chater & Finch (1998) established the same for broader distributional context.
**No teacher, no labels: the supervision is the distributional structure itself.** A frame is a very
coarse cue, which is a direct, independent precedent for our coarse result.

**So the coarse-role-profile route has real precedent -- for CATEGORY.**

### 3.2 For MEANING substitutability: no, not primarily -- role profiles CONSTRAIN, they do not decide

**PINNED.** Syntactic bootstrapping (Gleitman 1990; Landau & Gleitman 1985; recent review in *Nature
Reviews Psychology* 2024): children as young as **12 months** treat a novel word framed as a noun as
naming an object kind, and at **18 months** expect a novel verb to name an event category; a verb
taking a clausal complement is inferred to be a mental-state verb. **The frame narrows the hypothesis
space. It does not supply the meaning.** The published limitation is stated in the same literature:
syntactic evidence about meaning is *noisy and highly abstract*, and needs supplementing with
referential and lexical-context information; pragmatic and syntactic cues combine.

**PINNED -- what supplies the rest.** The transmodal ATL hub, whose evidence base is causal (semantic
dementia's cross-modal category-general impairment; inhibitory rTMS over ATL; ATL damage impairing
the **acquisition** of new concepts). Its code is a convergence of experiential/feature information
across modalities -- **not a syntactic distribution**.

**Therefore, the answer to "does the brain derive substitutability from role profiles":**

> **NO for meaning; YES for the grammatical category that gates the search for meaning. The brain
> runs a two-stage architecture -- a cheap coarse distributional/frame stage that narrows the
> hypothesis, and a grounded cross-modal stage that fixes the code. We have built stage one, scored
> it on a stage-two instrument, and it did surprisingly well. That is a real finding about stage one.
> It is not evidence that stage two is unnecessary.**

### 3.3 A correction the landed cell's verdict needs

The cell's verdict string reads `STOPIF5_S1_NOT_ABOVE_N3__SECOND_INDEPENDENT_NEGATIVE_ON_PREDICTION_
ERROR`, and the pre-registration says that outcome "should be treated as decisive for the signal, not
just the site". **The persisted arm diagnostics do not support the strong version.**
`S1_SLOT_COMPETITION` and `N3_MAGNITUDE_PERMUTED` both record `n_occurrences: 33907, vocab_size:
17377` -- **identical to `T3_COMBINED`'s declared bag channel**, and different from the typed
channel's `n_arc_events: 80056, vocab_size: 21093`. On the persisted evidence, **the supervised write
rule was applied to the bag-of-words channel that reads 0.0510, not to the typed channel that reads
0.6669.** S1 reading 0.0695 is what that channel reads.

**So the error rule has still never been tested on top of the representation that works.** That is
not a rescue narrative -- it is a factual reading of the arm diagnostics, and it should be **verified
in the cell source by whoever owns that file** (I did not read it; the brief bars me from touching
it) before the "decisive for the signal" wording propagates any further.

---

## 4. QUESTION 4 -- THE BRAIN-FAITHFUL VERSION WE ARE NOT DOING

Four elements, each with SHAPE, POSITION and the METRIC **the brain's version is judged on** -- which
in three of four cases is *not* an AUC on 242 known pairs. Ordered by what blocks what.

### 4.1 ROLE AS A GATE ON A GROUNDED CODE, NOT AS THE CODE (the structural one)

- **SHAPE.** A small posterior over ~3-8 grammatical frames per word (my truncation sweep says 3 bins
  carry 96% of the available signal, so this is *not* a lossy simplification -- it is the measured
  effective dimensionality). It **selects which dimensions of a separate feature code get written**;
  it is never itself the vector compared at read time.
- **POSITION.** Between the parse and the write. The role profile is the *address selector*; the
  Lancaster-style experiential profile (owned, **90.3% coverage of the 617 eval words**, measured in
  the prior drill -- credit `admissible_supervision_sources_drill_2026-08-18.md`) is the *content*.
- **METRIC.** The ATL evidence is about **acquisition** and **cross-modal generality**, so the brain's
  version is judged on: after *k* exposures to a **held-out** word, does the role-gated write reach a
  correct code faster than the ungated one, and does it transfer to a modality/task not used in
  training. **Not** rank-sum AUC on pairs already in the store.
- **Status.** Two-stage architecture: **PINNED**. Role-profile-as-gate: **OUR INVENTION UNDER TEST.**

### 4.2 VERB-SPECIFIC SELECTIONAL CONTENT, NOT A RELATION-TYPE MARGINAL (the cheapest discriminator)

Our winning code says *"this word appears as a subject and as an object"*. The pMTG/AG code the
literature describes is **verb-argument specific** -- *what can be eaten*, not *what can be an
object*. These are different objects and the cell conflated them: `U3`'s 64 bins are relation TYPES.

- **SHAPE.** Word code = its distribution over `(verb_lemma, ROLE)` slots. The asset exists:
  `data/selectional_preferences_v1/selectional_slots_v1.pkl`, **41,529 slots, 944,990 observations,
  90.0% coverage of the eval words**, WordNet-free (credit: the prior drill measured this, and
  `experiments/selectional_preference_extractor_v1.py` built it).
- **POSITION.** Identical to `U3` -- same step, different context identifier. This is the missing
  `U4` arm, and it is the direct discriminator between **role TYPE** (what we measured) and **role
  CONTENT** (what the brain's thematic organ is described as holding).
- **METRIC.** The brain's version is judged by **anomaly detection** (the N400 to selectional
  violations), so score it that way too: for an **unseen** verb, does the code rank a plausible
  filler above an implausible one? Report the pair AUC as a secondary readout only.
- **The prior negative, disclosed up front.** `data/exp_selectional_constraint_bridge_v1/metrics.json`
  landed `SELECTIONAL_CONSTRAINT_BRIDGE_DOES_NOT_CLEAR_THE_FLOOR`, CI-separated **below**
  neighbour-copying. **That cell CONSTRUCTED codes for words never stored, on a different scorer
  (Spearman rho, CI half-width ~0.1122) and a different population.** This arm RE-REPRESENTS words
  already stored, on the AUC instrument. Per the standing rule that no number crosses scorers or
  populations, the negative does not transfer -- but it is real, it is on the same asset, and it
  should deflate the prior substantially.

### 4.3 COMMIT-THEN-REVISE (the element whose absence our own result exposes)

Our arm is coarse and (apparently) robust. **Cortex's role assignment is coarse and robustly WRONG**
-- and it has a repair stage we do not have. Good-enough processing (Ferreira, Bailey & Ferraro 2002;
Christianson 2016) is PINNED: comprehenders build shallow underspecified representations and
**misassign thematic roles in passives and garden-paths**, with the wrong reading persisting after
reanalysis. The repair is the P600 (Osterhout & Holcomb).

- **SHAPE.** A provisional role assignment from the cheap cue, a mismatch detector, and a **replace
  (not blend)** update.
- **POSITION.** Within-sentence, between parse and write -- the point at which a disambiguating cue
  arrives.
- **METRIC.** Role-assignment accuracy on **non-canonical constructions** (passive, object-relative)
  versus canonical, where the cheap heuristic is known to invert. A system with only the cheap stage
  scores at or below chance on passives; that is the diagnostic, and it is not a similarity metric at
  all.
- **Credit.** `notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`
  already specified this mechanism at the encoder level (Caramazza & Zurif 1976; Grodzinsky TDH;
  Friederici ELAN/LAN/P600; Bornkessel-Schlesewsky eADM). **Build on that note; do not re-derive it.**

### 4.4 THE MEASUREMENT ELEMENT: FLOORS BELONG TO THE REPRESENTATION

Not biology, but it blocks everything above, and section 1.2 is the evidence.

- **SHAPE.** Every floor recomputed **inside the representation under test**, including an
  attestation floor of the form `log(min(mass))`, plus a synonym-vs-frequency-matched-random contrast
  alongside the synonym-vs-collocate one.
- **POSITION.** Pre-registration, before the bar is stated.
- **METRIC.** A margin is reportable only when the strongest floor **actually run in that
  representation** is beaten with CI separation. Under the arc representation that floor is
  **0.6317**, not 0.4901.

---

## 5. PINNED vs OUR-INVENTION -- THE TABLE THIS NOTE IS ACCOUNTABLE TO

| claim | status |
|---|---|
| Agent/patient role information is decodable from left mid-STC / left LPTC and generalises across sentences and across vision and language | **PINNED** (Frankland & Greene 2015 PNAS; Wurm & Caramazza 2019 Nat. Commun.) |
| Syntactic *structure*, not just processing effort, is recoverable from fMRI | **PINNED** (Reddy & Wehbe NeurIPS 2021) |
| Taxonomic similarity (ATL) and thematic relatedness (pMTG/TPJ) doubly dissociate | **PINNED** (lesion localisation; fMRI; TMS; intracranial EEG oscillatory dissociation) |
| Grammatical class is available in LIFG within ~80-100 ms under predictive context; noun/verb MEG differences not explained by meaning | **PINNED** |
| Coarse distributional frames support grammatical-category induction without a teacher | **PINNED** (Mintz 2003; Redington/Chater/Finch 1998; Chemla et al. 2009) |
| Syntactic frames constrain but do not determine word meaning; children use them from 12-18 months | **PINNED**, with the authors' own limitation (syntactic evidence is noisy and abstract; needs referential support) |
| Role assignment in comprehension is shallow, underspecified and frequently wrong, with a later revision stage | **PINNED** (good-enough processing; P600 reanalysis) |
| **Whether role is represented SEPARATELY from the filler** | **OPEN.** Dedicated registers (F&G) vs non-orthogonal overlapping bindings (arXiv 2110.12342) vs no separable syntactic code at region level (Fedorenko et al. 2020, *Cognition*) |
| **That cortex maintains a per-word histogram over dependency-relation types** | **OUR INVENTION UNDER TEST.** No recording shows this. |
| **That the semantic write rule is indexed by grammatical role** | **OUR INVENTION UNDER TEST** (unchanged from the prior drill, which labelled it correctly) |
| **That a role vector and a filler vector are combined by an algebraic binding** | **UNPINNED** (project finding 2026-08-16, applies verbatim) |
| **That a coarse role profile is corruption-tolerant in cortex** | **NOT A CLAIM ANYONE SHOULD MAKE FROM OUR DATA.** Our tolerance is an artifact of marginal-drawn corruption (section 1.3) |

---

## 6. WHAT THIS NOTE DOES NOT LICENSE

- **It does not retract the win.** `U1 = 0.6669` and `U3 = 0.6466` are real, reproduce exactly from
  the persisted units, survive mass matching at 0.6284 / 0.6369, and beat frequency-matched random
  pairs at 0.6209 / 0.5958 above recomputed floors. **This is still the strongest arm this programme
  has produced.**
- **It does not license the phrase "robust to half its input being wrong."** Retire it. `N6` as built
  is near-incapable of failing.
- **It does not license "word identity does not matter."** The typed channel was starved by
  arithmetic (130 arcs, 21,093 dimensions). Re-test it on a corpus where it can be populated -- the
  SimpleWiki asset (737,488 parsed sentences) with a bag-of-words twin at the same corpus.
- **It does not license quoting 0.5431 as the bar for this representation.** Under the arc
  representation the attestation floor alone reads **0.6317**.
- **It does not license "prediction error is dead."** On the persisted arm diagnostics the supervised
  rule was applied to the bag channel. **Verify in source before propagating** (section 3.3).
- **It does not generalise past NOUNS.** All 242 matched pairs are nouns (prior drill, section 4.1).
- **It does not claim the two-stage architecture is our design.** The two-stage claim is pinned; the
  proposal to use a role profile as the gate is ours and untested.

---

## 7. HOW I ENUMERATED PRIOR WORK, AND WHAT I BUILT ON

**`tools/substrate_query.sh` was NOT used** -- the brief states it is non-functional (returns zero
bytes, exits 0), and I am **not** reporting its silence as evidence of absence.

**Method, so it can be faulted:** `ls notes/ | grep -iE "<topic>"` at NAME level for five topic
families (`admissible|supervision`; `role|syntax|syntactic|grammat|typed|slot|parse|pos_`;
`distribut|substitut|neighbour|neighbor|word_class|category|induction|bootstrap`), then READ the
hits. No `find` and no `os.walk` over `notes/` or `data/`, per the brief's warnings. Both landed
`metrics.json` files were read with the repo `.venv` interpreter, never bare `python`.

**Prior work built on and credited:**

- **`notes/admissible_supervision_sources_drill_2026-08-18.md`** (829 lines, read in full). It is the
  parent of the cell that landed: it specified `U1`/`U3`/`S1`/`N1`-`N6`, named the dual-organ
  literature (pMTG/AG verb-argument structure dissociable from the ATL taxonomic hub), measured every
  asset's coverage and WordNet-independence, and **correctly labelled role-indexing as our invention.**
  This note builds on it and corrects exactly two things: its floors were imported across a
  representation change (its own text predicted they would "regression-match at delta 0.0 because the
  population is identical" -- the population is, the representation is not), and its `N6` and `N5`
  designs cannot fail as built. Its central judgement -- *run the unsupervised falsifier before any
  supervised arm* -- was correct and is what produced this result.
- **`notes/what_supervision_the_brain_has_that_we_do_not_error_driven_learning_drill_2026-08-18.md`**
  -- the four-candidate supervision taxonomy; not re-derived.
- **`notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`** -- the
  staged commit-then-revise account (section 4.3 is its mechanism, not a new one).
- **`experiments/selectional_preference_extractor_v1.py`** and its header's brain-fidelity work
  (pMTG/angular gyrus; slot-filler organisation developmentally prior to taxonomic).

**Literature consulted this session (generic-term web scan; lit-scan deflation applied):** Frankland
& Greene 2015 PNAS; Wurm & Caramazza 2019 *Nature Communications*; "Distributed neural encoding of
binding to thematic roles" (arXiv 2110.12342); Fedorenko, Blank, Siegelman & Mineroff 2020
*Cognition*; Reddy & Wehbe NeurIPS 2021; Pasquiou et al. 2023 (information-restricted LMs); Mintz
2003; Redington, Chater & Finch 1998; Chemla, Mintz, Bernal & Christophe 2009; Gleitman 1990 and the
2024 *Nature Reviews Psychology* syntactic-bootstrapping review; Ferreira, Bailey & Ferraro 2002;
Christianson 2016; the dual-hub taxonomic/thematic dissociation literature (lesion, fMRI, TMS,
intracranial EEG).

**Provenance of every number I computed:**
`tools/diagnose_role_profile_is_category_detector.py` (promoted out of `scratch/` because this note
cites it). Read-only over
`data/exp_typed_role_context_write_rule_dissociation_v1/units.jsonl` and
`data/exp_dissociation_score_instrument_v1/units.jsonl` (`POPULATION|v1.7|full`). Seed 20260818,
`N_BOOT = 2000`. Re-run it to regenerate. **No experiment cell was authored or run; no file under
`experiments/`, `preregs/` or any `arm_key*` was opened for writing or reading.**
