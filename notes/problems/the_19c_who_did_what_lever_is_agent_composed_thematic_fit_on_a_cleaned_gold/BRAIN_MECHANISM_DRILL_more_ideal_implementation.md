# Brain-mechanism drill: the "more ideal" glass-box patient predictor -- faithful computation for the three residual gaps

**Scope.** Read-only literature drill. For each of the three gaps between the current patient
predictor (verb-prior CENTROID over a 200-d PPMI-SVD hub, sharpened by precision-weighted
agent-composition `P(patient|agent,verb)`, reaching 2.38x the organ's held-out MRR) and the brain,
this document gives (a) the mechanism, (b) the computational-level operation with the actual
formula/algorithm, (c) whether the current draft is faithful or a half-effort, (d) the specific
upgrade to implement in FHRR/numpy with no LLM. No experiments were run.

---

## THE ONE FINDING THAT UNIFIES ALL THREE GAPS (read this first)

**Every one of the three "half-effort" drafts is the *same* error, and every earlier negative
(naive concat hurt; WordNet hypernym-averaging hurt) was the *same* wrong operation.**

- The drafts all combine cues by a **GLOBAL, ADDITIVE, UNNORMALIZED** rule: `alpha*z_hub + (1-alpha)*z_spoke`,
  `+ beta*cos(cand, context)`, a fixed cross-stream switch.
- The brain does **PER-ITEM, RELIABILITY-WEIGHTED, MULTIPLICATIVE (log-probability / intersective)**
  cue integration. A plausible patient must be typical for the verb **AND** given the agent **AND**
  given the event context -- a conjunction (product of probabilities = sum of log-probabilities),
  not a disjunctive blend (sum of raw cosines lets a candidate win on one cue alone).
- Both earlier negatives used the **disjunctive / blurring** operation (mean of hypernym vectors;
  concatenation without per-space normalization so the high-norm space dominates). That is the wrong
  combination OP, not evidence the cue is dead.

**The single unifying upgrade, applied at three sites:**
1. Normalize each cue to a proper distribution over the candidate pool (z-score, or softmax -> log-prob).
2. Combine in **log-prob space** (sum of logs = product = conjunction / intersection).
3. Weight each cue **per item** by its reliability/precision `r_i = 1/sigma_i^2` (Ernst & Banks 2002),
   **not** by a global constant.

This is one mechanism -- **precision-weighted Bayesian cue integration** -- instantiated at (GAP 1)
spoke fusion, (GAP 2) event-context, (GAP 3) taxonomic back-off. It is also exactly the mechanism
that already earned its place in this project's composition step (precision-weighted composition beat
the raw estimator +0.014 CI-sep by removing over-commitment on sparse-evidence items). The gaps are
three more sites where the same precision principle is currently missing.

---

## GAP 1 -- MULTIMODAL REPRESENTATION (the ATL hub integrating spokes)

### Mechanism
The anterior temporal lobe (ATL) is a **transmodal hub** that learns a deep, nonlinear
**convergence** of modality-specific "spokes" (sensorimotor, visual, verbal, valence). Patterson,
Nestor & Rogers (2007) "Where do you know what you know?"; Lambon Ralph, Jefferies, Patterson &
Rogers (2017) "The neural and computational bases of semantic cognition" (Controlled Semantic
Cognition). The hub is a **learned shared latent space** that all spokes project into -- **not** a
late linear sum of independently-built spoke similarities. A linear late-fusion only *approximates*
it.

There are two distinct levels, and they need different implementations:
- **(a) Representation-level convergence** -- what the hub *is*: a jointly-learned shared space.
- **(b) Decision/score-level integration** -- when the system holds two *estimates* of a candidate's
  fit, the brain combines them by **reliability-weighting** (Ernst & Banks 2002, optimal cue
  integration), per item, not by a fixed weight.

### The computational-level operation with formula

**Ernst & Banks (2002) optimal (maximum-likelihood) cue integration.** Under Gaussian noise and a
flat prior, the optimal combined estimate is the inverse-variance-weighted average of the single-cue
estimates:

```
s_hat        = w_hub * s_hat_hub + w_spoke * s_hat_spoke
w_i          = r_i / sum_j r_j              # weights proportional to reliability
r_i          = 1 / sigma_i^2                # reliability = precision = inverse variance
1/sigma^2    = sum_j 1/sigma_j^2            # the combined estimate is MORE reliable than either cue
```

The weights are **per-item** (they depend on `sigma_i^2` for *this* query), which is the whole point:
a fixed alpha cannot express "trust the hub here, the spoke there."

**Andrews, Vigliocco & Vinson (2009) "Integrating experiential and distributional data to learn
semantic representations" (Psychological Review 116(3):463-498; and Andrews, Vigliocco & Vinson 2009
Acta Psychologica "Combining feature norms and text data with topic models").** They did **NOT**
concatenate two pre-built vectors. They built a **joint generative (Bayesian topic) model**: each
latent topic `z` generates BOTH a distribution over words AND a distribution over experiential
features; words-in-documents and feature-norms are both *observed data* explained by a **shared set
of latent topics**. Words and features are tied through the same latent variable. **The joint model
(both data types) predicted human semantic similarity/priming BETTER than either distributional-only
or experiential-only.** The faithful lesson: the winning combination is a **shared latent space
learned jointly**, not a post-hoc mix of separate spaces.

**Bruni, Tran & Baroni (2014) "Multimodal Distributional Semantics" (JAIR 49:1-47); Kiela & Bottou
(2014).** Build text and image vectors **independently**, then FUSE. The method that generally won
was **SVD applied to the (per-space-normalized) CONCATENATION** of the two spaces -- i.e.
dimensionality reduction over the concatenated matrix builds a **joint reduced latent space**
("middle/early fusion"), typically with a tunable mixing weight between the spaces. Raw concatenation
**without per-space L2 normalization is dominated by whichever space has larger norms** (here: the
200-d hub swamps the 12-d spoke) -- this is exactly the "naive concat hurt" failure. Score-level
(late) fusion also works but is the weaker approximation.

### Verdict on the draft: HALF-FAITHFUL (right normalization, wrong weighting)
Draft: z-score hub-fit and 12-d spoke-fit over the candidate pool, then `alpha*z_hub + (1-alpha)*z_spoke`, global alpha.
- **Correct instinct, keep it:** the per-pool z-scoring **is** the per-space normalization that stops
  one channel dominating. This is why the draft is not as broken as naive concat -- it already does
  what Bruni's per-space normalization does.
- **The half-effort:** the **global alpha**. The brain weights cues by **per-item reliability**
  (Ernst-Banks). When the hub has dense evidence for this `(agent, verb)` it should dominate; when the
  hub is sparse/OOV, the spoke should. A fixed alpha cannot do that. This is the *same* precision term
  the project already proved earns its place in the composition step -- it is simply missing at the
  fusion step.
- **The ceiling of score-level fusion:** a linear combo only approximates the hub's nonlinear
  convergence. The stronger-faithful move is a *joint latent space* (Andrews joint model / Bruni
  SVD-fusion), but that is a bigger build. The cheap, high-fidelity win is the per-item precision weight.

### The upgrade to implement (numpy/FHRR, no LLM)
Replace the global alpha with Ernst-Banks per-item inverse-variance weighting on the z-scored scores:

```
# per candidate c you have z_hub(c), z_spoke(c) (already z-scored over the pool)
z_combined(c) = w_hub * z_hub(c) + w_spoke * z_spoke(c)

# weights are per-QUERY (per (agent, verb)), NOT per candidate:
w_hub   = r_hub   / (r_hub + r_spoke)
w_spoke = r_spoke / (r_hub + r_spoke)
```
Estimate each channel's reliability `r_i` for *this* query from:
- **evidence count** `n_i` = number of exemplars supporting the estimate for this agent/verb
  (reliability rises with n); and
- **peakedness/separation** of the channel's score distribution over the candidate pool -- a channel
  that separates candidates strongly is more reliable this item. Concretely any of:
  `r_i propto n_i/(1+spread_i)`, or `r_i = (top1 - top2 margin of channel i)`, or
  `r_i = -entropy(softmax(z_i over pool))`.

**Optional stronger-faithful representation upgrade (only if score-level plateaus):** build the joint
space by **SVD of the per-space-normalized concatenated `[hub || spoke]` matrix** (Bruni) and score in
that joint space. This subsumes the linear combo and is the closer analogue of the ATL convergence.

### Why the earlier negative (naive concat hurt) happened
Naive concatenation without per-space normalization let the higher-norm/higher-dim hub dominate the
12-d spoke, so the spoke contributed nothing or added noise. **Wrong combination op, not a useless
cue.** The fix is per-space normalization (the draft's z-scoring already does this) **then**
reliability-weighted combination (the missing piece) or SVD-fusion.

---

## GAP 2 -- EVENT/DISCOURSE CONTEXT prediction (cue breadth)

### Mechanism
**Generalized Event Knowledge (GEK).** Comprehenders immediately activate *structured* knowledge of
typical events (who does what to whom, where, with what) and use it to **pre-activate** upcoming
arguments. McRae & Matsuki (2009) "People use their knowledge of common events to understand language,
and do so as quickly as possible"; Elman (2009) "On the meaning of words and dinosaur bones" (the
lexicon as a set of *cues* to event knowledge, not static word vectors); Metusalem, Kutas, Urbach,
Hare, McRae & Elman (2012) "Generalized event knowledge activation during online sentence
comprehension." Metusalem is the decisive one: an event-related but contextually anomalous word still
gets a **reduced N400**, even after controlling for word-to-word association -- so pre-activation is
driven by the **EVENT SCHEMA (role-bound), not just lexical association**. A bag-of-context-words mean
captures the association component (which is real) but **discards the role binding that is the whole
point**.

### The computational-level operation -- two faithful, implementable architectures

**(A) Sentence Gestalt / Situation-State Vector (St. John & McClelland 1990; Brouwer, Crocker,
Venhuizen & Hoeks 2017 "A Neurocomputational Model of the N400 and the P600"; Venhuizen, Crocker &
Brouwer 2019).**
- Maintain an **incrementally-updated situation vector** `SG_t`. Update on each incoming constituent:
  `SG_t = f(SG_{t-1}, input_t)`. In the original this is a recurrent (sigmoid) *update network*; the
  copyable computational-level operation is a **recurrent update that binds the new constituent into a
  running situation vector**.
- **Readout (the operation to copy):** to get the expected filler of a role, **probe the gestalt with
  the role** and read out a distribution over fillers. In the SG model this is a trained *query
  network*; the **FHRR-faithful analogue is exactly VSA unbinding**: represent the situation as a
  superposition of role-filler bindings and unbind by the target role:
  ```
  SG        = sum_i  role_i  (x)  filler_i          # (x) = FHRR binding (you already have it)
  pred_pat  = SG  (x)  patientrole^{-1}             # unbind -> approx. expected patient vector
  ```
  Score a candidate `c` by `cos(pred_pat, vec(c))`. **No LLM, no training -- pure FHRR algebra you
  already possess.** This is the Sentence-Gestalt readout done in your substrate.
- **N400 / surprise** is modeled as the **change** the incoming word induces (Brouwer: N400 =
  retrieval of word meaning; P600 = integration/update of the situation vector). So "surprise of
  candidate c" is proportional to the distance between the gestalt's predicted next filler and `c` --
  the graded prediction signal, which is the instrument this project already showed composition wins
  on (held-out MRR).

**(B) Structured Distributional Model / Distributional Event Graph (Chersoni, Santus, Blache & Lenci
2019 "A Structured Distributional Model of Sentence Meaning and Processing," Natural Language
Engineering; Lenci 2011 "Composing and Updating Verb Argument Expectations," ACL CMCL workshop).**
- Maintain an **Active Context (AC)**: a set of **role-linked expectation vectors**, one per thematic
  role, built from event knowledge -- a **Distributional Event Graph** of `(verb, role, filler)` tuples
  mined from parsed/proximity-extracted corpus. **You already have this**: proximity-extracted
  `(agent, verb, patient)` triples.
- As each word arrives it **updates the AC**: the filler of one role activates the typical fillers of
  the *other* roles via the event graph. The expectation on the patient given agent+verb is the
  composed role-linked expectation.
- **Composition/update operation -- Lenci (2011) tested ADDITIVE vs MULTIPLICATIVE composition** of
  the cues (the verb's patient-expectation and the agent's patient-expectation). **The MULTIPLICATIVE
  (product / intersective) model better captured the dynamic update:** a product acts as a conjunction
  (a good patient must be typical for the verb AND typical given the agent), which sharpens the
  expectation more than an additive blend. **This directly answers the "how to combine" question.**

### Referential givenness (should salient/given entities be up-weighted?) -- YES
Altmann & Kamide (1999) "Incremental interpretation at verbs: restricting the domain of subsequent
reference" (anticipatory eye movements: "the boy will eat ..." pre-activates *edible*, scene-present
objects). Recently-mentioned and scene-present entities are **up-weighted as candidates**. Implement a
**givenness prior** over the candidate pool:
```
salience(e) = sum over mentions m of e  decay(distance_to_m)   # recency-weighted, decaying with distance
                                                               # + mention count
P(c | givenness) propto exp(gamma * salience(c))
```
Fold this into the product with the thematic-fit cue (below), never as a separate additive term.

### Verdict on the draft: HALF-EFFORT (unstructured context + wrong combination op)
Draft: context = MEAN hub-vector of the sentence's other content words; add `beta*cos(cand, context)`, global beta.
- **Unstructured:** the mean is a *bag of content words* -- it throws away role binding, which is the
  entire GEK finding (Metusalem: event structure beats word-association even after controlling for it).
- **Wrong combination:** additive `beta*cos` with a **global beta** is the wrong operator. Lenci (2011)
  shows **multiplicative/product beats additive** for updating argument expectations; and the
  agent-verb prediction and the event-context prediction are approximately **independent cues**, which
  combine by **adding log-probs = multiplying probabilities**, not by adding raw cosines. Adding raw
  cosines also mixes unnormalized similarities on different scales and is *disjunctive* (a candidate
  can win on one cue alone), whereas the brain's cue integration is *intersective*.

### The upgrade to implement (numpy/FHRR, no LLM)
1. **Structure the context as role-linked expectations, not a bag mean.** Keep separate
   role-conditioned expectation vectors from your event triples; the context contribution to the
   patient prediction is the patient-expectation activated by *each filled role* (agent, verb, and any
   other mentioned entity), not a mean over undifferentiated content words.
2. **If you keep a single context vector, make it the FHRR superposition of role-filler bindings** and
   read out the patient by unbinding the patient role (architecture A above). This is strictly more
   faithful than a bag mean and costs only the bind/unbind you already have.
3. **Combine cues in log-prob (product) space, not additive cosine:**
   ```
   score(c) = log P(c | agent, verb)                      # your precision-weighted composition
            + lambda_ctx * log P(c | event-context)       # role-structured, architecture A or B
            + lambda_giv * log P(c | givenness)           # recency/mention salience prior
   ```
   Each `P(.)` is a **softmax over the candidate pool** (a proper normalized distribution from that
   cue). The `lambda` are **per-item reliabilities** (same Ernst-Banks precision principle as GAP 1),
   **not** a single global beta. Sum-of-log-probs = product = the Lenci-multiplicative / conjunctive
   result.

### Why the additive-cosine draft underperforms
Adding raw cosines is a **disjunctive, unnormalized** mix; the brain's cue conjunction is
**intersective** (verb AND agent AND context). Using raw cosine instead of a normalized log-prob is
the *same wrong-combination class* as naive concat in GAP 1. Switching to a normalized log-prob
product (with per-item reliability weights) is the fix.

---

## GAP 3 -- TAXONOMIC COVERAGE back-off for rare/OOV fillers

### Mechanism
Resnik (1996) "Selectional constraints: an information-theoretic model and its computational
realization" (Cognition 61) / Resnik (1993 thesis). The faithful taxonomic generalization is a
**CLASS-CONDITIONAL EXPECTATION over an ontology (WordNet)**, **not** vector-averaging of hypernym
lemmas. A verb has a selectional-preference distribution over semantic **classes**; an OOV filler is
scored by how well its **class** fits, using the verb's class-conditional association.

### The exact Resnik computation (the algorithm to implement)
```
P(c)      = base rate of class c as the argument (e.g. object), across all verbs
P(c|v)    = distribution over classes for the argument of verb v

# Selectional Preference Strength -- how choosy the verb is (KL divergence):
S(v)      = D_KL( P(c|v) || P(c) )  =  sum_c  P(c|v) * log[ P(c|v) / P(c) ]

# Selectional Association -- fit of class c to verb v (the class's normalized share of S(v)):
A(v,c)    = (1/S(v)) * P(c|v) * log[ P(c|v) / P(c) ]

# Score a noun n (specific lemma may be rare/OOV but n is in WordNet): take the BEST-fitting class:
A(v,n)    = max over c in classes(n)  of  A(v,c)     # max implicitly disambiguates the noun's sense
```
**Estimation with distributed counting up the hypernym hierarchy (the key trick that makes it robust):**
```
freq(v,c) ~= sum over n in words(c)  count(v,n) / |classes(n)|      # spread each obs across its classes
P(c|v)     = freq(v,c) / sum_c' freq(v,c')                          # then propagate counts UP the tree
```

### Would this back off OOV fillers correctly where vector-averaging FAILED? -- YES
- **Why naive hypernym-lemma vector-AVERAGING hurt (the three causes):** (i) **polysemy** -- averaging
  in vectors of the *wrong senses* of the hypernyms; (ii) **over-general classes** (`entity`, `object`,
  `thing`) contribute high-frequency generic vectors that **wash out** the signal; (iii) it mixes the
  **wrong level** of the hierarchy. It is an **averaging (disjunctive, blurring)** operation on the
  representation.
- **Why Resnik fixes exactly those:** it computes a **per-class fit SCORE** and takes the **MAX-fitting
  class** (not a mean), grounded in the verb's actual class-preference distribution. **Over-general
  classes self-attenuate**: they do not discriminate the verb, so `P(c|v) ~= P(c)`, so
  `log[P(c|v)/P(c)] ~= 0`, so `A(v,c) ~= 0`. The **max over classes** does sense disambiguation
  implicitly. It never averages vectors, so polysemy and level-mixing cannot blur it.

### Is dense nearest-neighbor (exemplar/CLS) better than explicit classes? -- the real fork
Complementary Learning Systems (McClelland, McNaughton & O'Reilly 1995; Kumaran, Hassabis & McClelland
2016): the brain has **both** a hippocampal **exemplar** memory (nearest-neighbor in a high-fidelity
space) and neocortical **semantic categories**. For rare/OOV fillers:
- **When the dense space is RELIABLE, exemplar nearest-neighbor beats brittle explicit class
  assignment.** Given this project's finding that the 200-d PPMI hub is the reliable space and the
  composition margin grows monotonically with hub capacity, **nearest-neighbor-in-hub is a strong,
  faithful back-off for OOV agents**: borrow the agent-conditioned patient expectations of the OOV
  agent's k nearest *reliable* hub neighbors (a CLS/exemplar generalization) rather than averaging its
  WordNet hypernyms.
- **The two are complementary, not rivals:** use Resnik class-conditional association when the filler
  is in WordNet with reliable class counts; use dense NN when the hub is reliable but the taxonomy is
  noisy/absent. Your `hdlab/grounded_semantic_graph` PPR (personalized PageRank / spreading activation
  over WordNet++ with thematic edges) is a **third, graph-based** generalization -- a **sense-aware,
  smoothed** version that already avoids naive averaging.

### Verdict on the draft
Draft: if the agent is OOV in the hub, fall back to the sensorimotor spoke (cross-stream); earlier naive WordNet hypernym vector-averaging HURT.
- **Cross-stream fallback (hub OOV -> spoke): keep, but make it graded.** It is the GAP-1 Ernst-Banks
  logic (when hub reliability -> 0, weight -> spoke). Do it as a **precision-weighted** blend, not a
  hard switch.
- **The abandoned WordNet hypernym vector-averaging was a HALF-EFFORT with the WRONG OPERATION.**
  Taxonomy is not useless; you used the **disjunctive/blurring** op (mean of hypernym vectors) instead
  of Resnik's **discriminative class-association** with max-over-classes and distributed counting.

### The upgrade to implement (raise coverage without noise)
1. **Replace hypernym-lemma vector-averaging with Resnik selectional association.** Precompute `P(c)`
   and `P(c|v)` via distributed counting up the WordNet hypernym tree from your `(verb, patient)`
   triples; score an OOV/rare candidate `n` as `A(v,n) = max_{c in classes(n)} (1/S(v)) P(c|v) log[P(c|v)/P(c)]`.
   Over-general classes self-attenuate to `A ~= 0`.
2. **For OOV AGENTS (the composition case), do NOT average hypernyms -- use exemplar nearest-neighbor in
   the reliable HUB space.** Find the k nearest reliable agents to the OOV agent in the 200-d hub;
   borrow their agent-conditioned patient expectations (CLS-style), weighted by neighbor similarity.
   Dense generalization in the reliable space is where fine individuation lives (this project's finding).
3. **Combine the class-based (Resnik) and dense-NN back-offs by reliability (Ernst-Banks again).**
   Resnik is reliable when class counts are dense and `S(v)` is high; dense-NN is reliable when the OOV
   has close reliable hub neighbors. Weight each by its evidence. Use `grounded_semantic_graph` PPR as
   the sense-disambiguated smoother.
4. **Sense-disambiguate before building any vector.** The max-over-classes in Resnik does this
   implicitly. If you must build a filler vector at all, build it from the **disambiguated sense's
   hyponym exemplars (frequency-weighted)**, never a raw mean of all hypernym lemmas.

### Why the earlier negative (WordNet smoothing hurt) happened
Same class of error as GAP 1's naive concat: the **wrong combination/aggregation operation**
(disjunctive averaging that amplifies polysemy and over-general classes), not evidence the taxonomy is
useless. Resnik's discriminative, max-over-classes, self-attenuating association is the operation that
raises coverage without adding noise.

---

## PER-GAP BOTTOM LINE

| gap | draft verdict | the one faithful operation to implement |
|---|---|---|
| **1 Multimodal fusion** | **half-faithful** -- z-scoring (normalization) is right; **global alpha is the half-effort** | Ernst-Banks per-item inverse-variance weighting `w_i = r_i/sum r_j`, `r_i = 1/sigma_i^2` from evidence-count and score-separation; optional SVD-fusion of the per-space-normalized `[hub||spoke]` for the joint space |
| **2 Event/discourse** | **half-effort** -- bag-of-words mean is unstructured; **additive global beta is wrong op** | FHRR role-filler superposition + unbind for readout (Sentence Gestalt), OR role-linked Active Context (SDM); combine cues as a **sum of pool-softmax log-probs** (Lenci multiplicative/conjunctive) with per-item reliability weights; add a recency/mention **givenness prior** |
| **3 Taxonomic back-off** | **half-effort** -- cross-stream switch OK if graded; **hypernym vector-averaging was the wrong op** | Resnik `A(v,n)=max_c (1/S(v))P(c\|v)log[P(c\|v)/P(c)]` with distributed hypernym counting (over-general classes self-attenuate), OR dense k-NN in the reliable hub for OOV agents; blend by reliability |

**Both earlier negatives (naive concat hurt; WordNet averaging hurt) were the wrong COMBINATION
OPERATION, not a dead cue.** The disjunctive/blurring op (unnormalized concat; mean of hypernym
vectors) was replaced-by-nothing when it should have been replaced by the normalized, per-item
precision-weighted, multiplicative/log-prob (or max-over-classes) operation the brain uses. One
mechanism -- precision-weighted Bayesian cue integration -- closes all three, and it is the same
mechanism the project already validated at the composition step.

---

## SOURCES (specific papers with the method)

- **Ernst, M.O. & Banks, M.S. (2002).** Humans integrate visual and haptic information in a statistically
  optimal fashion. *Nature* 415:429-433. -- inverse-variance (reliability) weighting; `w_i = (1/sigma_i^2)/sum_j(1/sigma_j^2)`.
- **Andrews, M., Vigliocco, G. & Vinson, D. (2009).** Integrating experiential and distributional data
  to learn semantic representations. *Psychological Review* 116(3):463-498. (and Acta Psychologica 2009,
  "Combining feature norms and text data with topic models"). -- JOINT Bayesian topic model; shared
  latent topics generate BOTH words and features; joint model beats either alone.
- **Bruni, E., Tran, N.K. & Baroni, M. (2014).** Multimodal Distributional Semantics. *JAIR* 49:1-47.
  -- fuse text+image by SVD of the (normalized) concatenation into a joint reduced space; per-space
  normalization required; late (score) fusion is the weaker alternative. (Kiela & Bottou 2014, CNN
  visual features + skip-gram text.)
- **Patterson, K., Nestor, P.J. & Rogers, T.T. (2007).** Where do you know what you know? *Nat. Rev.
  Neurosci.* 8:976-987. **Lambon Ralph, Jefferies, Patterson & Rogers (2017).** The neural and
  computational bases of semantic cognition. *Nat. Rev. Neurosci.* 18:42-55. -- hub-and-spoke; ATL as
  learned nonlinear transmodal convergence, not linear late fusion.
- **McRae, K. & Matsuki, K. (2009).** People use their knowledge of common events to understand
  language, and do so as quickly as possible. *Lang. Ling. Compass* 3:1417-1429. -- generalized event
  knowledge pre-activates arguments.
- **Metusalem, R., Kutas, M., Urbach, T., Hare, M., McRae, K. & Elman, J. (2012).** Generalized event
  knowledge activation during online sentence comprehension. *J. Memory & Language* 66:545-567. --
  event-related anomalies reduce N400 beyond word-association; structure, not bag-of-words.
- **Elman, J.L. (2009).** On the meaning of words and dinosaur bones. *Cognitive Science* 33:547-582.
  -- lexicon as cues to event knowledge.
- **St. John, M.F. & McClelland, J.L. (1990).** Learning and applying contextual constraints in
  sentence comprehension. *Artificial Intelligence* 46:217-257. -- Sentence Gestalt: incrementally
  updated situation vector; probe with role to read out filler.
- **Brouwer, H., Crocker, M.W., Venhuizen, N.J. & Hoeks, J.C.J. (2017).** A Neurocomputational Model of
  the N400 and the P600 in Language Processing. *Cognitive Science* 41(S6):1318-1352. (Venhuizen,
  Crocker & Brouwer 2019, situation-state vectors). -- N400 = retrieval, P600 = update of the situation
  vector; readout by role probe.
- **Altmann, G.T.M. & Kamide, Y. (1999).** Incremental interpretation at verbs: restricting the domain
  of subsequent reference. *Cognition* 73:247-264. -- anticipatory pre-activation; scene/givenness
  constraint on candidate arguments.
- **Lenci, A. (2011).** Composing and updating verb argument expectations: a distributional semantic
  model. *ACL Workshop on Cognitive Modeling and Computational Linguistics (CMCL).* -- tests ADDITIVE
  vs MULTIPLICATIVE composition of argument expectations; multiplicative/product better for the dynamic
  update.
- **Chersoni, E., Santus, E., Blache, P. & Lenci, A. (2019).** A Structured Distributional Model of
  Sentence Meaning and Processing. *Natural Language Engineering* 25(4):483-502. -- Active Context +
  Distributional Event Graph; role-linked incremental expectation update. (Santus, Chersoni, Lenci &
  Blache 2017, "Measuring Thematic Fit with Distributional Feature Overlap," EMNLP -- prototype/feature
  scoring.)
- **Resnik, P. (1996).** Selectional constraints: an information-theoretic model and its computational
  realization. *Cognition* 61:127-159. (Resnik 1993 thesis.) -- `S(v)=D_KL(P(c|v)||P(c))`,
  `A(v,c)=(1/S(v))P(c|v)log[P(c|v)/P(c)]`, distributed hypernym counting.
- **McClelland, J.L., McNaughton, B.L. & O'Reilly, R.C. (1995);** **Kumaran, Hassabis & McClelland
  (2016).** Complementary Learning Systems -- hippocampal exemplar (dense NN) + neocortical categories;
  basis for exemplar-vs-class back-off.

## TLDR (plain English)
The predictor already works well; three upgrades would make it more like the brain, and all three are
the *same* fix. (1) When it blends the "dictionary-meaning" signal with the "physical-sense" signal, it
currently uses one fixed mixing knob; the brain instead trusts whichever signal is more reliable *for
that particular word*, so make the mix depend on how much evidence each side has (Ernst-Banks
reliability weighting). (2) When it uses the rest of the sentence as context, it currently averages the
other words into one blob; the brain keeps track of *who is doing what* (structured event knowledge),
and combines clues by multiplying probabilities (a good answer must fit the verb AND the doer AND the
situation), not by adding scores. Keeping roles separate and multiplying is the fix -- and your own
tools (the bind/unbind algebra) already do it. (3) For rare or unseen words it once tried averaging
WordNet parent-word vectors and it hurt; the right method (Resnik) never averages -- it scores how well
each *category* fits the verb and takes the best category, which automatically ignores useless
catch-all categories like "thing." For unseen *doers*, just borrow from the nearest well-known doers in
the reliable space. The headline: both past failures ("averaging hurt") were the wrong blending
operation, not proof the idea was bad.

## QUESTIONS
None blocking. One judgment call for whoever implements: GAP 2 has two faithful options -- the FHRR
role-filler superposition readout (cheaper, reuses your bind/unbind) vs the SDM role-linked Active
Context (closer to the parsed-event-graph literature but needs typed roles). Recommendation: start with
the FHRR readout because it reuses existing algebra and needs no parser; escalate to SDM only if the
structured-context cue underperforms the bag mean by less than expected.

## NEXT STEPS
1. Implement the single unifying primitive first: a `precision_weighted_logprob_combine(cues, reliabilities)`
   that softmax-normalizes each cue over the candidate pool, takes logs, and sums with per-item
   inverse-variance weights. All three gaps call it.
2. GAP 1: swap the global alpha for that primitive with `r_hub`, `r_spoke` from evidence-count + score-separation.
3. GAP 2: build the FHRR role-filler situation readout; feed its log-prob as one cue; add the givenness prior.
4. GAP 3: implement Resnik `A(v,n)` with distributed hypernym counting + dense-hub k-NN for OOV agents;
   feed as the back-off cue, reliability-gated.
5. Each is a can-fail ablation against the current 2.38x-MRR predictor on the held-out forward-prediction
   instrument (the one the brain's agent x verb effect actually shows on), with info-free twins.
