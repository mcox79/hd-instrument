# WHAT DOES CORTEX COMPUTE WHEN IT EXTRACTS A REGULARITY ACROSS MANY EPISODES?

**A research drill for ORGAN A (THE WRITE RULE). Biology first, equation last. 2026-08-18.**
**Gates drill 1 of the three named in `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.7
(commit `c2d8ac84c`). No cell authored, nothing dispatched, nothing run.**

---

## 0. THE PLAIN-LANGUAGE VERSION (read this if you read nothing else)

Our store learns a word by **adding up** every sentence it ever appeared in. One running total per
word. That is the whole write rule.

The measurement that started this drill says the running total is the problem. Keep **one** sentence
picked at random and the system scores **0.0367**. Add all ~20-31 of them together and it scores
**0.0100** -- *worse than one*. Let a cheating oracle pick the single best sentence and it reaches
**0.3033**, against a bar of **0.1390** we have never once cleared. So the answer is sitting inside
the individual sentences and our addition step is grinding it out.

**The literature answer, in one sentence: no part of the brain adds evidence up without dividing it
by something.** Every biological account of "combine many experiences into one thing" that has ever
been written down as an equation has a **denominator** -- a division by the total activity of the
neighbouring population, by a running average of the cell's own recent output, or by the correlation
structure of the input itself. Plain summation with no denominator is not a simplified version of
what the brain does. It is the one form the brain is specifically known **not** to use, because a
network that does it blows up within minutes.

**And there is a second, deeper thing, which I think is the real finding of this drill.** Getting from
"these two words *appear next to each other*" to "these two words *can replace each other*" is not
a matter of adding more carefully. It requires a step that does not exist anywhere in our write rule
at all. Adding up sentences tells you who a word's neighbours are. To learn that *cat* and *dog* are
interchangeable, you have to notice that **their neighbour-lists resemble each other** -- and no
amount of summing one word's own neighbours ever computes a comparison between two different words'
neighbour-lists. That comparison is a separate operation. In the brain it is done by learning a
**shared low-dimensional code** in which words that predict the same things get pulled onto the same
axes. In our system the corresponding step is a **random projection**, which is mathematically
guaranteed to preserve the geometry it is handed and therefore mathematically incapable of creating
that structure. *We chose an operation whose defining property is that it changes nothing, to occupy
the slot where the brain does the one thing that matters.*

**Third thing, and it is a correction to our own plan, not to the literature.** The plan's line
*"summing is what converts our store from could-replace into appears-near"* is **not supported by the
cell it cites** -- see section 7. The co-occurrence share rises across ACCUMULATE for the *right*
answer too, and the bias ratio slightly *falls*. Accumulation is not where adjacency gets in.
Adjacency was there from the first sentence, because a bag of neighbours **is** an adjacency record.

**Does the brain average episodes into one representation, or keep them apart?** **Both, in two
anatomically separate pathways, at the same time, permanently.** That is section 6, and it means our
write rule is not a category error -- it is a *half*-error: we built the averaging half and threw the
episode away, and the evidence says the brain never throws the episode away.

---

## 1. THE ORGAN, AS IT ACTUALLY RUNS (enumerated from live code, not from memory)

**HOW I ENUMERATED.** I read `experiments/exp_writerule_step_ladder_v1.py` lines 10-57, which record
a runtime-verified enumeration with file-and-line citations, then opened each cited site and
confirmed it at HEAD:

| step | live code | what it does, as arithmetic |
|---|---|---|
| FILTER | `hdlab/grounding_acquisition_loop.py:106-114` `content_words` | keep `[a-z']+` tokens, drop ~70 stopwords, drop `len <= 2` |
| CODE | `hdlab/reading_grounding_loop.py:297-309` `symbol_vector` | `sha256(w)`-seeded bipolar draw at `d=256`; ONE fixed basis `H` shared by the whole vocabulary; a sentence's code is the sum of its surviving words' rows of `H` |
| ACCUMULATE | `hdlab/reading_grounding_loop.py:478-482` `ConceptSpace.observe` | `self._sums[lemma] += ctx_vec`. No weight, no decay, no cap, no denominator |
| NORMALISE | `hdlab/reading_grounding_loop.py:490-509` `anchor_matrix` | `np.sign(mat)` **only if** `GRADED_COMPARATOR` is off. Env `HD_GRADED_COMPARATOR` defaults to `"1"`, so **on the live path nothing normalises the store at all** |

Written as one equation, the entire organ is:

```
    m_a  =  SUM_{s in occurrences(a)}  SUM_{w in content_words(s), w != a}  H_w          (LIVE)
```

with `H_w` a fixed random +-1 row. Equivalently, letting `p_a` be the raw count vector of context
words for anchor `a` over the vocabulary:

```
    m_a  =  H^T p_a                (asserted bit-exact in exp_cue_information_audit_v1)
```

**So our store is the matrix `P` of raw word-context counts, right-multiplied by a fixed random
projection. Nothing else. No reweighting, no denominator, no learned basis.** Every candidate below
is a proposal for what to put where the `SUM` and the random `H` currently sit.

The measured per-step ladder (`data/exp_writerule_step_ladder_v1/metrics.json`, `run_mode=full`,
`RANKED_DROP_TABLE`, read off disk 2026-08-18):

| step | acc before -> after | signed effect | CI95 | band |
|---|---|---|---|---|
| FILTER | 0.0349 -> 0.0340 | LOSS 0.0009 | [-0.0016, +0.0033] | NOT_SEPARATED |
| ACCUMULATE | 0.0340 -> 0.0603 | **GAIN 0.0263** | [-0.0343, -0.0186] | BELOW (i.e. a gain) |
| CODE_PROJECT | 0.0603 -> 0.0481 | **LOSS 0.0123** | [+0.0060, +0.0188] | ABOVE |
| NORMALISE | 0.0481 -> 0.0464 | LOSS 0.0016 | [-0.0051, +0.0085] | NOT_SEPARATED |

**Read that table against the drill's own premise and something jumps out.** The only CI-separated
LOSS in the whole write rule is **CODE_PROJECT -- the random projection** -- and it is exactly the
step that section 0 argues is occupying the slot where the brain does its one indispensable
operation. The bare sum is not the biggest measured destroyer at this cue regime; the convenience
tool we dropped into the learned-basis slot is.

*(Caveat carried in the same breath: all five rungs are measured at the ORACLE EXACT-KEY cue, which
is not the operating point. Per the standing rule an exact-key number does not transfer to the
partial-cue regime -- and section 6.6 of the plan records the Director breaking that exact rule two
days ago. Read the table as a within-regime ranking of steps, not as operating-point magnitudes.)*

---

## 2. THE LEARNING RULE AT THE SYNAPSE AND ITS NORMALISATION

*(The drill calls this the single most important question. It is, and the answer is not the one I
expected: the normalisation the field can PIN is not the one that would help us.)*

### 2.1 Plain Hebb -- what we have, and why nothing biological is shaped like it

```
    dW_ij/dt  =  eta * x_j * y_i                                    [PLAIN HEBB]
```

`x_j` presynaptic activity, `y_i` postsynaptic activity, `eta` a rate. Our `_sums[lemma] += ctx_vec`
is this with `eta = 1`, `y_i` clamped to 1 for the anchor, and no other term.

**Status: PINNED that correlational strengthening exists** (LTP, thousands of preparations).
**PINNED that this form alone is unstable and is not observed in isolation**: the sign of the weight
change depends on the postsynaptic state in every measured induction protocol, and unbounded growth
is not observed. Every rule below is a proposal for the missing stabilising term. The field's
disagreement is about *which* term, never about *whether*.

### 2.2 Oja's rule -- normalise by the postsynaptic output; get the principal subspace

```
    dw_i/dt  =  eta * y * ( x_i  -  y * w_i )                        [OJA 1982]
    with y = w . x
```

The subtracted term `y * w_i` is a **self-normalisation**: it is the first-order correction that
keeps `||w|| -> 1`. Its consequence is the interesting part, and it is a theorem, not a fit:
**`w` converges to the top eigenvector of the input covariance `E[x x^T]`.** The generalised
(Sanger / subspace) version extracts the top-`k` principal subspace:

```
    dW/dt  =  eta * ( y x^T  -  LT[ y y^T ] W )                      [SANGER / GHA]
```

**This is the equation that matters most for us.** It says a purely local, purely Hebbian rule with
one subtracted term performs **online PCA** -- precisely the "learn a shared low-dimensional code in
which words that predict the same things land on the same axes" operation that section 0 identified
as our missing step, and precisely what a fixed random `H` provably cannot do.

**Status: THEORETICAL PROPOSAL, and I want to be blunt because it is our best candidate and the
least pinned of the five.** The literature position is that there is **no direct experimental
demonstration of Oja's rule operating at a biological synapse**. What is supported is (a) LTP and LTD
both exist, (b) some normalising influence on input weights and on output rates exists, and (c) a
biophysical derivation of a *generalisation* of the rule is constructible if you allow retrograde
signalling from the postsynaptic cell. That is "compatible with biology", not "measured in tissue".
Calling it brain-derived would repeat exactly the mislabelling this project already caught itself
making about VSA binding.

### 2.3 BCM -- normalise by a sliding threshold on the cell's own recent activity

```
    dw_i/dt  =  eta * x_i * phi( y, theta_M ),   phi(y,theta) = y * (y - theta)
    theta_M  =  E[ y^2 ]  over a long trailing window      [BIENENSTOCK-COOPER-MUNRO 1982]
```

Below `theta_M` the synapse depresses; above it, potentiates; and `theta_M` itself rises with the
square of the cell's recent output. That is the normalisation, and its superlinear dependence on `y`
is what makes the fixed point stable and **selective** -- the cell ends up responding to one input
pattern rather than to the average of all of them. *Selectivity rather than averaging is exactly the
property our accumulator lacks.*

**Status: PINNED AS A PHENOMENON, PROPOSED AS AN EQUATION.** The sliding threshold was first
demonstrated in V1 -- reducing activity by dark-rearing from birth promotes LTP and reduces LTD, a
genuine tissue measurement -- has since been confirmed in several regions, and heterosynaptic
modification of the LTP threshold has been shown both in vitro and in vivo. The **existence and
direction** of the slide is a fact about tissue. The **specific functional form** `y(y - E[y^2])` is
a modelling choice that fits; calcium-based implementations propose different forms fitting the same
data. Timescales are pinned and are a usable constraint: LTP/LTD induction in **seconds**, threshold
slide over **hours**.

**PRIOR WORK ON DISK, WHICH MUST BE STATED BEFORE ANYONE PROPOSES BCM AGAIN.** We have attempted BCM
twice and have **never obtained a valid measurement**:
- `data/exp_gap3_cls_two_tier_BCM_slow_replay_v1/metrics.json` -- `HARD_FAIL`, *"methodology_drift:
  ARM_BASELINE_SINGLE_W=1.0000 >= HF_BASELINE_MAX=0.5; cross-cell rail violated"*. The baseline was
  broken; the BCM arm is uninterpretable.
- `data/exp_gap3_cls_two_tier_BCM_v2_init_fix/metrics.json` -- `HARD_FAIL_UNIT_EXCEPTION`,
  *"RuntimeError 'value cannot be converted to type float without overflow' (completed 1/12 units
  before crash)"*. That is BCM's classic runaway, in our own code.

**BCM here is UNTESTED, not refuted.** Anyone citing those two runs as evidence against BCM is
quoting a broken rail and a crash.

### 2.4 Synaptic scaling -- multiply every weight by one shared factor

```
    w_i  <-  alpha * w_i ,   alpha driven by ( target_rate - actual_rate )
```

**Status: MEASURED IN TISSUE, WITH A REPLICATION CAVEAT.** Turrigiano 1998: chronic (48 h) activity
blockade in dissociated neocortical cultures multiplies mEPSC amplitudes by a uniform factor;
multiplicativity is the measured claim; timescale hours-to-days; neocortical neurons in vitro and in
vivo regulate around a firing-rate set point. **But** in vivo replication is contested -- with 2 days
of tetrodotoxin blockade over hippocampus, multiplicative scaling of mEPSC and mIPSC amplitudes was
**absent**, diverging from the in vitro finding, and the stated general problem is that homeostatic
plasticity in an intact circuit has to operate without destroying the information carried across a
dendritic tree.

**And it does not solve our problem even if it is entirely real.** A single shared multiplier is a
**rank-0 normalisation**: it changes `||m_a||` and changes **no ratio inside `m_a`**. Cosine is
scale-invariant. **Synaptic scaling applied to our store is a mathematical no-op on every number we
measure.** It is the most-measured of the five and the least useful to us -- a clean illustration
that PINNED and LOAD-BEARING-FOR-US are different axes.

### 2.5 Heterosynaptic plasticity -- the competitive term, and the one I would actually reach for

```
    dw_i  =  eta * x_i * y   -   gamma * w_i * SUM_j ( x_j * y )         [schematic]
```

Potentiating one input **depresses the others on the same cell**, in proportion to their current
weight. **Status: MEASURED IN TISSUE** -- heterosynaptic depression at unstimulated synapses on a
potentiated cell is a robust experimental finding, and the modelling literature shows it prevents
runaway dynamics on the fast timescale that synaptic scaling (hours-days) is far too slow to police.

**This is the biologically strongest normalisation available, and unlike synaptic scaling it is NOT
scale-invariant** -- it redistributes weight *between* inputs, exactly the operation that could
suppress a high-frequency collocate in favour of a distinctive one. Note the structural kinship:
**Oja's rule IS a heterosynaptic rule** -- the `-y w_i` term depresses every synapse in proportion to
its own weight whenever the cell fires. *The most-measured normalisation and the most-useful-to-us
normalisation turn out to be the same operation seen from two directions.* That is the most
encouraging single fact in this drill, and it is why candidate C1 below is ranked first.

### 2.6 Weight decay

```
    dw_i/dt  =  ... - lambda * w_i
```

**Status: PINNED that synapses turn over and unrehearsed traces weaken; PROPOSED that the functional
form is a linear leak with one rate constant.** For us it is a **recency weighting** over a word's
occurrences. Cheap, and worth carrying as an arm, but it reweights *episodes*, not *dimensions*, so
it cannot by itself fix a collocate-dominance problem.

### 2.7 What this section changes about what gets stored

| rule | divides by | changes ratios inside `m_a`? | what it changes about what is stored |
|---|---|---|---|
| plain sum (ours) | nothing | -- | raw neighbour counts |
| synaptic scaling | one shared scalar | **NO** | **nothing measurable here** |
| weight decay | age | yes, mildly | recent episodes weighted up |
| BCM | trailing `E[y^2]` of the cell | yes | drives the accumulator to be **selective** for one pattern instead of the average |
| heterosynaptic / Oja | the other inputs on the same cell | yes, strongly | drives the store toward the **principal subspace** of the input covariance |

**The answer to the drill's most important question: the brain's substitute for our bare sum is a
COMPETITIVE term -- something that makes a word's context dimensions compete against each other on
the same accumulator. It is not a magnitude fix. It is a redistribution.**

---

## 3. DIVISIVE NORMALISATION AS A CANONICAL CORTICAL COMPUTATION

### 3.1 The actual form

```
    r_i  =  x_i^n  /  ( sigma^n  +  SUM_{j in POOL(i)} x_j^n )        [HEEGER 1992; CARANDINI & HEEGER 1994, 2012]
```

`x_i` the driving input to unit `i`; `POOL(i)` the **normalisation pool**, the set of concurrently
active units whose summed activity forms the shared denominator; `sigma` the **semi-saturation
constant**, an additive term that prevents division by zero and sets the input level at which the
response is half-maximal; `n` an exponent (commonly 2).

**Two properties are the whole point.** (1) The denominator is **shared across the pool**, so every
*ratio between two units inside the pool is preserved* -- this is a gain control, not a re-ranking.
(2) The `sigma` term makes it **non-scale-invariant at low input**: weak inputs are suppressed
super-proportionally.

**Status: MEASURED IN TISSUE AND GENERALISED BEYOND IT.** The functional form is fitted across
contrast gain control, surround suppression, cross-orientation suppression and self-normalisation in
V1, and comparable forms fit responses in olfactory, auditory, multisensory and value-coding areas --
which is why the "canonical computation" label was applied. It can additionally be derived from
redundancy-reduction first principles and has been shown derivable from Wilson-Cowan dynamics.
Honest calibration: the **form** is exceptionally well fitted; **`sigma`, `n` and the membership of
`POOL` are free parameters fitted per area and per preparation**, not constants to import. This is a
textbook instance of the project's own rule -- copy the operation, sweep the parameter.

### 3.2 What it would do to a co-occurrence-dominated accumulation

The drill asks specifically whether it would suppress the high-frequency context words that carry
adjacency rather than identity. **Written out, the answer is: only if the pool is chosen over
CONTEXT WORDS, and then yes, and the resulting equation is one we already have implemented.**

Set the pool to be *all anchors sharing context dimension `j`* and apply the normalisation to the
count matrix `P` at write time:

```
    P~_aj  =  P_aj  /  ( sigma  +  SUM_a' P_a'j )
```

The denominator of column `j` is the corpus frequency of context word `j`. A word like *because*
appears in nearly every anchor's profile, so its column sum is huge and it is crushed; a word like
*photosynthesis* has a small column sum and survives. **That is exactly the "suppress adjacency, keep
identity" behaviour asked for, and it is one line.** Take logs and it *is* PMI:

```
    PMI(a,j) = log ( P(a,j) / ( P(a) P(j) ) ) ,   PPMI = max(0, PMI)
```

**Divisive normalisation over a frequency pool and PPMI are the same operation in different
notation.** We already own an implementation: `hdlab/ppmi_sparse_encoder.py` (`PPMI(t,c) = max(0,
log(P(t,c)/(P(t) P(c))))`, then SVD, then threshold). It is not on the live write path.

### 3.3 PRIOR WORK ON DISK -- DIVISIVE NORMALISATION HAS BEEN TESTED HERE TWICE AND LOST TWICE

**Both tests were on the READ side. Neither touched the write rule. State this whenever the result is
quoted, because the scope is what makes it non-fatal.**

- `data/exp_graded_divisive_comparator_v1/metrics.json`, `run_mode=full`, `HARD_PASS`:
  `d = 0.0602 CI [0.0440, 0.0762]`. **But the win is from REMOVING the two `sign()` quantisers, not
  from adding division** -- its successor records that the removal is worth `+0.0585` of the
  `+0.0602`, and **global-field divisive normalisation on top is NULL: `+0.0018 CI
  [-0.0030,+0.0065]`**, despite removing a shared component worth 58% of every anchor's norm.
- `data/exp_task_local_normalisation_pool_v1/metrics.json`, `run_mode=full`,
  **`HARD_FAIL_GAIN_HURTS`**: with the pool narrowed to the concurrently-active candidate pair (the
  Carandini-Heeger-faithful choice), `d(P_CONTROL - R_BASE) = -0.0220 CI [-0.0340,-0.0097]` -- the
  CI **excludes zero and is negative**. And the decisive control fired the wrong way:
  `WRONGPOOL d = +0.0243 CI [+0.0075,+0.0410]`, i.e. computing the gain from a *different item's*
  pool reproduced the effect, so what little the operation did was **a generic variance filter, not a
  task-local normalisation**.

**The honest reading.** Divisive normalisation over a pool of *anchors at decision time* is
measured-negative here, twice, with a control that says the mechanism was never the one claimed. That
is a real negative and it should lower anyone's prior. **It says nothing about a divisive
normalisation over a pool of CONTEXT DIMENSIONS at write time**, which is a different pool, a
different stage, and reduces to PPMI. Different pool, different operation, different measurement --
per the standing rule that a number may not cross populations, these results cannot be imported to
score candidate C2 below. But they are the reason C2 is ranked second rather than first: our one
in-house data point on "add a denominator" is a loss.

---

## 4. SPARSE CODING AND PREDICTIVE CODING, AS OBJECTIVES

### 4.1 Sparse coding (Olshausen & Field 1996)

```
    E(a, Phi)  =  || x  -  Phi a ||^2   +   lambda * SUM_i S( a_i / sigma )
```

`x` the input; `Phi` the dictionary (learned basis); `a` the coefficients; `S` a sparsity penalty
(`|a|`, or `log(1 + a^2)`); `lambda` the trade-off. **Two nested updates:**

```
    inference:  da_i/dt  =  b_i  -  SUM_j C_ij a_j  -  (lambda/sigma) S'(a_i/sigma)
                            with b = Phi^T x,  C = Phi^T Phi        [a competitive settling]
    learning:   dPhi     =  eta * < ( x - Phi a ) a^T >             [Hebbian on the RESIDUAL]
```

**What the resulting code represents:** a set of basis elements such that any input is explained by a
*few* of them. Learned on natural images it yields localised, oriented, bandpass filters resembling
V1 simple-cell receptive fields.

**Status: THE OBJECTIVE IS A PROPOSAL; SOME OF ITS PREDICTIONS ARE MEASURED.** Sparse firing is
observed in visual cortical neurons, V1 neurons show high lifetime sparseness under natural stimuli,
and sparse coding predicts V1 receptive-field changes induced by abnormal visual input -- a genuine
predictive success, not just a post-hoc fit. What is *not* measured is that cortex minimises this
particular loss; that is inference from the fit. Recent work also argues V1 is not well described by
the `l1` version specifically. **Verdict: a model that fits data and has made at least one risky
prediction -- stronger than "popular", weaker than "measured in tissue".**

**The load-bearing detail for us:** note the `C = Phi^T Phi` term in the inference update. That is
**explaining-away** -- basis elements that overlap compete, so the code does not double-count a
feature already accounted for. Our accumulator has no such term, which is precisely why a context
word appearing in 40 of an anchor's sentences contributes 40 times over.

### 4.2 Predictive coding (Rao & Ballard 1999; Friston)

```
    residual:   e  =  x  -  Phi a                      (prediction error, carried forward)
    inference:  da/dt  =  eta_a * Phi^T e  -  lambda * dS/da
    learning:   dPhi   =  eta_W * e a^T
```

Same algebra as 4.1 with the residual given an explicit representational role. **Status: the LOOP is
a proposal; PREDICTION-ERROR-LIKE SIGNALS ARE MEASURED, WITH A LIVE CHALLENGE.** Mismatch responses
are reported in mouse V1 L2/3 when visual flow coupled to running is unexpectedly stopped, and in
auditory cortex; locus coeruleus broadcasts sensorimotor prediction errors cortex-wide, which is a
plausible plasticity-gating signal. **The challenge is real and must be carried:** perturbation-
responsive neurons prefer slow visual speeds and respond most at their preferred orientation, and a
convergence of ordinary motor and sensory signals **reproduces the mismatch signal without any
predictive-coding machinery** -- i.e. feature selectivity can explain the observation. **So: error
signals exist in cortex; that they are the residual of a generative model is a model that fits, and
one with a published alternative explanation.**

### 4.3 OUR OWN RESIDUAL ATTEMPT, AND WHAT A NON-DEGENERATE VERSION NEEDS

Recorded in `notes/STATUS.md` lines 98-101: surprise-weighting produced a **clean null with a named
cause -- the signal was DEGENERATE (median 0.875, where 1.0 is orthogonality), selection beat a
token-matched random subset in 4 of 18 comparisons, and the residual rule was a near-no-op (cos
0.9771 to uniform)**. The cell had **pre-registered** this as the bootstrapping problem, so this is a
correctly-predicted failure, not a surprise.

The mechanism of the failure, stated as algebra: we computed `e = x - predict(x)` with `predict`
being *the store we were criticising*. If the store is a near-uniform bag, `predict(x)` is nearly
constant across items, so `e ~ x - const`, so `cos(e, uniform) ~ 1` and the weights are all equal.
**A residual is only informative if the predictor is BETTER than the accumulator being trained.**

**A non-degenerate version needs at least one of these three, and none is exotic:**
1. **A predictor that is not the store.** A held-out-fold store, an older checkpoint of the same
   store (a temporally-lagged target -- and lagged/slow targets are how every stable predictive
   learner in ML avoids exactly this collapse), or a genuinely different organ.
2. **A prediction target that is not the input.** Predict the NEXT sentence's context bag from the
   current accumulator, not the current one. Then `e` cannot be trivially small, because the target
   was never written in.
3. **A measured non-degeneracy gate before any scoring.** Pre-register a check that the residual's
   spread across items exceeds the null spread -- e.g. that the median cosine of `e` to the uniform
   direction is below some pre-set bound, and that the item-wise variance of `||e||` is above the
   variance a shuffled-assignment control produces. The 0.875 / 0.9771 pair would have tripped such a
   gate before a single arm was scored, and it should be a mandatory precondition on any future
   residual arm in this project.

**Neither of the first two is a refutation of predictive coding; both are repairs of a bootstrap.
Predictive coding here is UNTESTED, exactly as BCM is.**

---

## 5. COMPLEMENTARY LEARNING SYSTEMS, AS MECHANISM RATHER THAN SLOGAN

### 5.1 The claim, restated as an update schedule

CLS is not a statement about anatomy; it is a statement about **two learning rates and a sampling
distribution**:

```
    hippocampus:  W_H  <-  W_H  +  eta_fast * Delta(episode)          eta_fast large, one-shot
    neocortex:    W_C  <-  W_C  +  eta_slow * Delta(sample)           eta_slow small
                  where `sample` is drawn from  ( new episodes  UNION  replayed old material )
```

**Two separate ingredients, and they do different jobs:**
- **`eta_slow` small** bounds how far any single item can move the cortical weights. Alone, this only
  *slows* interference; it does not prevent it.
- **INTERLEAVING** -- the sample containing old material alongside new -- is what actually prevents
  catastrophic interference. Replay of recent experience is interleaved with spontaneous retrieval of
  existing categories, so cortical weights are adjusted gradually toward a solution that satisfies
  old and new material simultaneously.

The mechanism claim in the current literature is explicit that the third ingredient is
**error-sensitivity**: interleaved training *coupled with a learning mechanism sensitive to
prediction error* is what forces cortex to build representations reconciling rare and common events;
recent work adds that the interleaving need not be uniform -- **similarity-weighted** interleaving
(replay the old items most similar to the new one) achieves the same protection at far lower cost.

**Status: PINNED that fast hippocampal and slow cortical learning are separable systems; PINNED that
replay occurs and that hippocampal-cortical dialogue happens in slow-wave sleep. PROPOSED: that
cortical learning is gradient descent on prediction error; PROPOSED: the specific interleaving
distribution. And -- important, stated because I went looking for it -- THE FIELD DOES NOT PUBLISH A
MEASURED VALUE FOR `eta_slow`.** There is no tissue measurement of a cortical learning rate. The
small rates in CLS simulations are model hyperparameters. **Anyone who writes a specific slow rate
into a cell as "the brain's value" is inventing it. `eta_slow` is a SWEEP, never a constant.**

Also pinned and directly contradicting the simplest slogan: cortex is **not** always slow. Learning
into a pre-existing schema consolidates in cortex within about 48 hours (the Tse et al. paired-
associate result is the canonical demonstration), so "cortex is slow" is a statement about
*schema-inconsistent* material specifically.

### 5.2 THE CRUX: WHAT OPERATION CONVERTS ADJACENCY INTO SUBSTITUTABILITY?

This is the drill's central question and it has a clean mathematical answer, which is **not** in the
learning-rate half of CLS at all. It is in the **error-driven** half.

Take a linear predictive learner: input `x` = an item, output `y` = the things that item predicts.
Gradient descent on squared prediction error, in the continuous-time limit, gives

```
    tau dW1/dt  =  W2^T ( Sigma_yx  -  W2 W1 Sigma_xx )
    tau dW2/dt  =        ( Sigma_yx  -  W2 W1 Sigma_xx ) W1^T          [SAXE, McCLELLAND & GANGULI 2019]
    tau = 1 / (P * lambda)
```

with `Sigma_yx = E[y x^T]` the **input-output correlation matrix** and `Sigma_xx = E[x x^T]` the
input correlation matrix. Decompose

```
    Sigma_yx  =  U S V^T  =  SUM_alpha  s_alpha  u^alpha  v^alpha T
```

and, under whitened inputs (`Sigma_xx ~ I`), each mode has the **exact solution**

```
    a_alpha(t)  =  s_alpha * e^(2 s_alpha t / tau)
                   ----------------------------------------------
                   e^(2 s_alpha t / tau)  -  1  +  s_alpha / a_alpha(0)
```

**Read what that says, in words.** The learner does not store `Sigma_yx`. It **factorises** it, and
it acquires the modes **in order of singular value**, each in a sigmoidal jump. The internal
representation of an item is its projection onto the `v^alpha` -- the **object analysers**. Two items
that predict the same features have similar loadings on the same `v^alpha`, so **they end up nearby
in the internal code even if they never once co-occurred.** The categories that emerge are uniquely
determined by the statistics of the environment.

**That is the conversion operation, and it is a factorisation, not an accumulation.** The equation
tells us three concrete, checkable things:

1. **`Sigma_yx` alone is our store.** `H^T P` is a random rotation of the raw input-output
   correlation matrix. **We have built `Sigma_yx` and stopped.** Everything that makes representations
   organise by substitutability happens in the *factorisation*, and we never do it.
2. **The `Sigma_xx` term is the one that handles frequency, and we dropped it.** The Hebbian
   one-shot solution is `W_hebb = Sigma_yx`; the least-squares solution the error-driven dynamics
   converge to is `W_opt = Sigma_yx Sigma_xx^{-1}`. **Our bare sum is the optimal rule with the
   inverse input-correlation term deleted.** For word-context counts `Sigma_xx` is grotesquely
   anisotropic (Zipf), so deleting `Sigma_xx^{-1}` is *precisely* the deletion that lets frequent
   collocates dominate. The paper's own whitening assumption `Sigma_xx ~ I` is the assumption that
   our data most violently violates.
3. **A random projection cannot substitute for the factorisation, and this is a theorem, not an
   opinion.** Johnson-Lindenstrauss says a random projection is a near-isometry: it *preserves* inner
   products up to distortion. A truncated SVD is deliberately *not* an isometry -- it discards the
   low-variance subspace, and that discarding is what makes "shares neighbours" collapse into "is
   nearby". This is the same fact the NLP literature states directly: **PPMI alone does not capture
   second-order information; the SVD factorisation is what does.** Our `CODE` step uses the isometry.
   **This is the step the ladder measures as the only CI-separated loss in the write rule
   (`+0.0123 CI [+0.0060,+0.0188]`), and the theory says it should be the step that contributes the
   most and currently contributes nothing.**

**One more brain-pinned route to the same place, worth recording because it is MTL-grounded rather
than backprop-grounded.** The Temporal Context Model maintains a gradually-drifting context vector
`t_i = rho_i t_{i-1} + beta c_i^IN`, and its predictive extension builds a word's semantic
representation by **aggregating the PREDICTION VECTORS available when that word occurs** rather than
the words themselves. Two words that occur in similar contexts get similar semantic vectors without
ever co-occurring. That is a second, independent, biologically-motivated formulation of the same
conversion -- and structurally it is our accumulator with *one substitution*: accumulate what the
context **predicts**, not what the context **contains**. That substitution is candidate C4 below and
it is the cheapest thing on the list.

---

## 6. DOES THE BRAIN EVER AVERAGE EPISODES INTO ONE REPRESENTATION?

**Answer: yes -- and it never stops keeping them apart either. Both, permanently, in parallel
pathways. Our error is not that we average; it is that averaging is ALL we keep.**

The evidence, separated by strength:

- **MEASURED (lesion + imaging, decades):** semantic knowledge survives hippocampal damage while
  episodic detail does not. Something context-free is stored outside hippocampus. **Averaging-like
  abstraction is real.**
- **MEASURED (fMRI, category learning):** prototype and exemplar codes are **simultaneously present
  in different regions** -- prototype predictors tracked in ventromedial prefrontal cortex and
  anterior hippocampus, exemplar predictors in inferior frontal gyrus and lateral parietal cortex.
  Not a competition the brain resolves; a division of labour it maintains.
- **MEASURED / STRONGLY SUPPORTED (anatomy + lesion dissociation):** the two hippocampal pathways do
  the two jobs. The **trisynaptic** path (DG -> CA3, pattern separation) is critical for
  exemplar-specific information; the **monosynaptic** path (EC -> CA1) is suited to learning structure
  *across* episodes. **Separation and integration are concurrent, not sequential.**
- **CONTESTED (the theory-level dispute, and it does not change our answer):** whether remote episodic
  memory ever becomes hippocampus-independent. Standard consolidation says yes; Multiple Trace Theory
  says the hippocampus is required for detailed retrieval of *all* episodic memories however remote,
  and that each retrieval lays down a **new** trace rather than updating the old one. Both sides agree
  the semantic/context-free representation lives in extra-hippocampal cortex. **Under MTT the brain
  does not merely fail to collapse -- it actively MULTIPLIES traces with every retrieval.**

**What this rules in and out for us.**

- **Not a category error.** A cortical, cross-episode, averaged representation is a real thing the
  brain builds. Keeping one summary vector per word is defensible.
- **But a one-sided implementation.** We keep the average and *discard the episodes*. The brain keeps
  both, and the pathway that keeps the episodes is the one whose loss produces amnesia. And our own
  decisive arm says the discarded half is where the answer is: **`BEST_SINGLE_ORACLE` 0.3033 against
  `SUM_ALL` 0.0100.** *(That oracle consults the answer when choosing the occurrence. It is a ceiling
  diagnostic and must never be quoted as a capability -- it establishes that the information survives
  in individual episodes, nothing more.)*
- **The strongest brain-framed statement I can make from this section:** the brain's cortical average
  is **not the thing retrieval reads by itself**. Retrieval reads a cortical summary *and* a
  separated episodic store, together. Any of our candidates that keeps only one vector per word is
  replicating one of the brain's two stores and substituting nothing for the other.

---

## 7. A CORRECTION TO OUR OWN PLAN, FOUND WHILE GROUNDING THIS DRILL

The brief and `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.1 both state:

> *"across the ACCUMULATE step the share of top-1 winners that have ever co-occurred with the query
> rises 66.0% -> 94.4% -- summing is what converts our store from 'could replace' into 'appears
> near'."*

**The two numbers are correct. The conclusion drawn from them is not supported by the cell's own
table.** Read off `data/exp_writerule_step_ladder_v1/metrics.json`
(`report.WINNER_COMPOSITION_PER_RUNG[*].syntagmatic`), `run_mode=full`, n_probe=700, 2026-08-18:

| rung | winner `frac_ever_co_occurring` | **best-gold** `frac_ever_co_occurring` | winner/gold ratio of means |
|---|---|---|---|
| R1 UNFILTERED_SINGLE_OCC | 0.6543 | 0.2200 | 4.361 |
| R2 FILTERED_SINGLE_OCC | 0.6600 | 0.2386 | 3.967 |
| **R3 FILTERED_FULL_ACCUM** | **0.9443** | **0.6029** | **3.822** |
| R4 PROJECTED_GRADED | 0.9057 | 0.5043 | 4.112 |
| R5 PROJECTED_SIGN | 0.7400 | 0.4300 | 3.877 |

**Across ACCUMULATE the RIGHT ANSWER's co-occurrence share rises too, and by more in relative terms
(0.2386 -> 0.6029, 2.53x, against the winner's 1.43x). The bias ratio FALLS, 3.967 -> 3.822.** The
rise in the winner's share is largely mechanical: `frac_ever_co_occurring` is monotone in how many
sentences are in the profile, and ACCUMULATE is the step that takes the profile from 1 sentence to
~72. **A quantity that must rise when you add sentences cannot be evidence that adding sentences
introduces a bias.**

And the same cell's *other* composition measure moves the other way: across ACCUMULATE the
**no-relation rate FALLS 0.8400 -> 0.7971, delta -0.0430 CI [-0.0800, -0.0086], band BELOW** -- a
CI-separated **improvement** in the kind of word that wins.

**So on both composition measures the cell reports, ACCUMULATE looks neutral-to-better, not worse.**

**Two caveats on my own correction, stated so it is not over-read in turn.** (i) The cell computes a
paired CI only for the no-relation delta; **no CI is computed for the co-occurrence deltas or for the
ratio**, so "the ratio falls" is a point estimate with unknown width and must not be quoted as a
separated effect. (ii) All of this is at the ORACLE EXACT-KEY cue.

**What survives, and it is still the strongest thing we have:** the decisive arm's
`SUM_ALL` 0.0100 vs `RANDOM_SINGLE` 0.0367 vs `BEST_SINGLE_ORACLE` 0.3033. Summing is measurably
worse than not summing. **What does NOT survive is the mechanism story attached to it.** Adjacency is
not something ACCUMULATE introduces -- **a bag of context words IS an adjacency record from the very
first sentence**, which the table confirms: the bias ratio is already 4.361 at a single unfiltered
occurrence, its highest value anywhere in the ladder. **The relation is not destroyed at ACCUMULATE.
It was never encoded, at any rung, by any step.** That reframes the organ: we are not looking for the
step that breaks substitutability, we are looking for the **missing step that would have created
it** -- which is section 5.2's factorisation, and which is why candidate C1 is ranked first.

---

## 8. OUR FOUR LIVE STEPS AGAINST THEIR CLOSEST BRAIN COUNTERPART

| step | our operation | closest brain counterpart | pinned? | **VERDICT** |
|---|---|---|---|---|
| **FILTER** | `content_words`: regex `[a-z']+`, drop ~70 hand-listed stopwords, drop `len<=2` | attentional / salience gating of what enters a trace; and, at the statistical level, frequency-dependent suppression | gating is PINNED as a phenomenon; the specific gate is not | **SUBSTITUTING.** A hand-written English stopword list is not a neural gate. It is also a *hard binary* gate where every biological analogue is *graded*. Measured effect 0.0009 NOT_SEPARATED; composition delta NOT_SEPARATED. **This step currently does nothing at all, in either direction.** |
| **CODE** | `sha256(w)`-seeded fixed bipolar basis `H`, `d=256`, shared by the whole vocabulary; sentence code = sum of rows | expansion into a high-dimensional code with a **learned, competitive** basis (V1 simple cells under sparse coding; Kenyon-cell expansion; DG) | **expansion and learned selectivity are PINNED**; the specific basis is not | **SUBSTITUTING, TWICE OVER.** (a) The basis is **fixed and random** where every biological code is **learned**; a random projection is a near-isometry and therefore provably cannot create the similarity structure this organ needs (sec 5.2 pt 3). (b) The direction is **inverted**: vocabulary -> 256 is a **compression**, where the pinned cortical motif is **expansion**. This is the only step the ladder scores as a CI-separated loss (`0.0123 [0.0060,0.0188]`). |
| **ACCUMULATE** | `self._sums[lemma] += ctx_vec`; no weight, no decay, no cap, no denominator | Hebbian potentiation **with** heterosynaptic depression / BCM sliding threshold | correlational strengthening PINNED; **that it is normalised is PINNED**; the form of the normaliser is PROPOSED | **PARTIALLY REPLICATING, SUBSTITUTING ON THE LOAD-BEARING HALF.** The correlational term is right. The competitive term -- the half that makes the accumulator *selective* rather than *average* -- is simply absent. Measured as a GAIN of 0.0263 in the ladder, and as -0.0266 against `RANDOM_SINGLE` in the decisive arm; both are true, they answer different questions (sec 6.3 of the plan). |
| **NORMALISE** | `np.sign(mat)`, **OFF by default** since 2026-08-14 | divisive normalisation `x_i^n/(sigma^n + SUM_pool x_j^n)`; homeostatic scaling | the divisive **form** is measured across many areas; `sigma`, `n`, POOL are fitted | **SUBSTITUTING, AND CURRENTLY ABSENT.** When it was on, `sign()` was a **per-component SELF denominator**, which sets every within-pool ratio to exactly 1 -- the *opposite* of divisive normalisation, whose defining property is that shared denominators **preserve** within-pool ratios. Our own comparator audit already established this and measured removing it as worth `+0.0585`. Off by default, so today the slot is **empty**: nothing normalises the store. |

**Summary verdict: zero of four steps are REPLICATING. One (ACCUMULATE) replicates half an operation.
The other three substitute a convenient tool -- a hand-written word list, a random projection, and
(when enabled) an operation that is the algebraic inverse of the cortical one.**

---

## 9. RANKED, IMPLEMENTABLE CANDIDATES TO REPLACE THE BARE SUM

**Ranking rule used:** expected value against the question that actually distinguishes fixing the
RELATION from improving the RANKING -- i.e. movement in **winner COMPOSITION** (no-relation rate, and
the winner/gold co-occurrence **RATIO**, never the raw share, per section 7). Probabilities are
novel-synthesis estimates, capped at 0.50 and deflated per standing calibration; they are for
`P(CI-separated movement in composition)`, not `P(clears the floor)`.

**A composition measurement rule that applies to every candidate below, and is new to this drill:**
**report the winner/gold co-occurrence RATIO with a paired CI, not `frac_ever_co_occurring` alone.**
The raw share is confounded with profile depth (sec 7) and will move for reasons that have nothing to
do with the write rule. Any candidate scored on the raw share alone should be rejected on
methodology.

---

### **C1 -- LEARN THE BASIS. Replace the fixed random projection with online principal-subspace extraction (Oja / Sanger).** `P(composition moves) ~ 0.35`

**Equation.** Stream context vectors `x` (or accumulated rows `m_a`) through
```
    y  =  W x
    dW =  eta * ( y x^T  -  LT[ y y^T ] W )                [Sanger / generalised Hebbian]
```
and let the store be `W m_a` instead of `H^T p_a`. Offline-equivalent closed form: truncated SVD of
the (reweighted) count matrix -- our `hdlab/ppmi_sparse_encoder.py` already implements PPMI-then-SVD,
and `hdlab/whitening.py` already implements ZCA, so **no new mathematics has to be written.**

**Why first.** It targets the **only CI-separated loss in the write rule** (`CODE_PROJECT`,
`+0.0123 [+0.0060,+0.0188]`); it is the operation section 5.2 identifies as the actual
adjacency-to-substitutability converter; and section 2.5 shows it is algebraically the same family as
the **best-measured-in-tissue** normalisation (heterosynaptic depression). It is the one candidate
where the biology, the theory and our own measured ladder all point at the same step.

**Sweep, never adopt:** `k` (subspace rank -- and sweep it ABOVE 256 as well as below, because the
pinned cortical motif is expansion); `eta`; whether inputs are whitened first; the reweighting fed in
(raw counts vs PPMI).

**Controls.**
- **MATCHED-RANK RANDOM BASIS** at the same `k`. If a random `k`-dim projection reproduces the gain,
  the win is dimensionality, not learning. *(This is the control the project's own "padding hurts"
  result shows is decisive -- width-matched noise arms landing BELOW the narrow incumbent is what
  made the verb result a CONTENT claim.)*
- **FREQUENCY-MATCHED SHUFFLE BASIS**: learn the basis on a corpus shuffled within-document so
  unigram frequencies are exactly preserved and co-occurrence structure is destroyed. If that basis
  reproduces the win, the effect is a frequency filter wearing a factorisation's clothes.

**Composition prediction (this is the discriminating claim).** If C1 is doing what the theory says,
**the winner/gold co-occurrence RATIO must fall toward 1.0** (from ~3.9) and the **no-relation rate
must fall** below 0.79. If accuracy rises while the ratio stays near 3.9, C1 improved the RANKING and
did not touch the RELATION -- report that as a null on the organ's question regardless of the score.

**SHELVE CRITERION (brain-framed).** Shelve C1 if, with `k` and `eta` swept and the basis
demonstrably learned (spectrum non-flat, reconstruction improving), **the KIND of word that wins does
not change** -- ratio within noise of 3.9. That would mean principal-subspace extraction, the
operation cortex is best-attested to perform on its inputs, does not perform the
adjacency-to-substitutability conversion **on this input distribution** -- which would falsify the
sec 5.2 account for our data and send the question to the CODE step's *input* (what a "context" is)
rather than its basis. **Not shelved for failing to clear a floor.**

---

### **C2 -- PUT A DENOMINATOR ON THE WRITE. Divisive normalisation over the CONTEXT-WORD pool (= PPMI).** `P ~ 0.30`

**Equation.**
```
    P~_aj  =  P_aj^n  /  ( sigma^n  +  SUM_{a'} P_{a'j}^n )        [Carandini-Heeger form, pool = column j]
    log form:  PPMI(a,j) = max( 0, log( P(a,j) / ( P(a) P(j) ) ) )
```
then `m_a = H^T P~_a` exactly as now. **One line, on a pool we have never normalised over.**

**Why second and not first.** Cheapest thing on the list, an owned implementation, and it directly
attacks frequent collocates. Ranked below C1 because **our one in-house data point on "add a
denominator" is a loss** (sec 3.3) and because reweighting alone provably cannot create second-order
structure -- PPMI without a factorisation does not capture second-order information. *C2 is best
understood as the correct PREPROCESSING for C1, not as a rival to it.*

**Sweep:** `sigma` (the semi-saturation constant -- **the parameter Carandini & Heeger fit per area;
we sweep it**), `n`, and the pool definition (column sums / row sums / both = full PMI).

**Controls.**
- **WRONGPOOL** -- denominator computed from a permuted column assignment. This is the exact control
  that killed the read-side version (`+0.0243 CI [+0.0075,+0.0410]`, i.e. the wrong pool reproduced
  the effect), and it must be run here.
- **PURE-IDF** arm -- divide by document frequency only. Separates "any frequency suppression" from
  "this normalisation".

**Composition prediction.** Ratio falls; no-relation rate falls modestly. **If PURE-IDF matches it,
declare a frequency effect and do not claim the cortical operation.**

**SHELVE CRITERION (brain-framed).** Shelve if WRONGPOOL reproduces the effect (then it is a generic
variance filter, not normalisation over a meaningful pool -- the same defect already measured on the
read side), **or** if the operation changes ranking without changing composition, since divisive
normalisation's defining cortical property is that it *preserves within-pool ratios while suppressing
pooled drive*, and an effect that only re-ranks is not exhibiting that property.

---

### **C3 -- KEEP THE EPISODES. Multi-trace store with a temperature-controlled read.** `P ~ 0.25`

**Equation.** Store the set `{c_1..c_k}` per anchor instead of their sum. Score
```
    s(a,q)  =  (1/beta) * log SUM_i exp( beta * cos(q, c_i) )
```
**`beta -> 0` is exactly our current mean-like rule; `beta -> infinity` is `BEST_SINGLE`.** Our store
is one endpoint of a one-parameter family whose other endpoint reads 0.3033 under an oracle. **Sweep
`beta`.** This is the cleanest "sweep the parameter, copy the operation" instrument on the list, and
section 6 says the brain's own answer is to run both endpoints concurrently.

**The honest deflation, and it is why this is third and not first.** `BEST_SINGLE_ORACLE` **consults
the answer** to pick the episode. A `beta`-weighted read must pick the episode **from the cue**, and
our cue is the weakest component in the whole system -- a cheating WordNet oracle reads 0.8787 at the
exact key and **0.0365 under the partial cue**. A max-over-episodes selector driven by a cue that
weak may realise none of the 0.3033. **The gap between 0.0100 and 0.3033 is an upper bound on what
C3 can pay, and the partial-cue result is a strong argument that the realisable fraction is small.**
*This is in flight already (`accumulate-no-collapse`, plan sec 6.3); this drill's contribution is the
`beta` family and this deflation.*

**Controls.** RANDOM-PARTITION (split one word's occurrences into `k` random groups -- a multi-vector
store must not win merely by having more vectors to match against); MATCHED-STORAGE and MATCHED-DEPTH
(it must not win by being bigger). Both are already specified in the in-flight cell.

**Composition prediction.** If `beta > 0` helps, the winning episode should be the one most similar to
the cue, and **generic sentences -- which match every cue about equally -- should stop winning
argmaxes**, so the no-relation rate should fall. If accuracy rises with the no-relation rate flat,
C3 improved retrieval precision without touching the relation.

**SHELVE CRITERION (brain-framed).** Shelve if **no intermediate `beta` beats both endpoints** after
the cue-strength confound is controlled. The brain's answer is explicitly *both stores at once*
(sec 6); a family that interpolates between them and is worse everywhere in the middle would mean our
episodes are not separable **in this code**, which relocates the problem to CODE (C1) rather than to
ACCUMULATE.

---

### **C4 -- ACCUMULATE THE PREDICTION, NOT THE CONTEXT (predictive Temporal Context Model).** `P ~ 0.25`

**Equation.** Maintain a drifting context and accumulate what it *predicts*:
```
    t_i  =  rho_i * t_{i-1}  +  beta * c_i^IN                        [TCM context drift]
    m_a  <-  m_a  +  pred( t_i )     at each occurrence of a         [pTCM semantic accumulation]
```
where `pred(t)` is the store's prediction from context, **not** the context itself.

**Why it belongs on the list.** It is the one candidate that produces substitutability *by
construction* -- two words in similar contexts acquire similar vectors without ever co-occurring --
and it is the most MTL-grounded formulation available, not a backprop result. Structurally it is
**our accumulator with exactly one substitution.**

**Sweep:** `rho` (drift rate), `beta`, and the number of passes (it needs at least two: pass 1 builds
a predictor, pass 2 accumulates predictions).

**Controls.** (i) The **non-degeneracy gate of sec 4.3, as a hard precondition** -- median
`cos(pred, uniform)` below a pre-set bound and item-wise variance of `||pred||` above a shuffle
control, checked BEFORE any arm is scored. (ii) A **lag-0 arm** where `pred` is replaced by the
current sentence's own bag, which must collapse to the incumbent -- a positive control on the
plumbing.

**Composition prediction.** This should move the ratio **the most** of any candidate, because a
prediction vector shared by two non-co-occurring words is the definition of the target relation. If
it does not, the pTCM account does not transfer to our corpus.

**SHELVE CRITERION (brain-framed).** Shelve if the predictor stays degenerate after both repairs
(held-out-fold predictor, next-sentence target). Degeneracy would mean this corpus does not support a
drifting-context predictor distinguishable from the mean context -- a statement about the input, and
the MTL mechanism cannot be instantiated on it.

---

### **C5 -- THE MISSING `Sigma_xx^{-1}`: least-squares / pseudoinverse write.** `P ~ 0.12`, **and there is a FREE pre-check that could kill it before any cell is written**

**Equation.** `W_hebb = Sigma_yx` (ours) vs `W_opt = Sigma_yx Sigma_xx^{-1}`; implemented
glass-box and SGD-free as
```
    W  =  Cross @ inv( Gram + ridge * I ),   Cross = SUM_i outer(E[o_i], k_i),  Gram = SUM_i outer(k_i, k_i)
```
(the exact form already coded in `experiments/exp_kg_store_write_rule_decorrelated_ceiling_v1.py`).

**PRIOR WORK, AND IT IS MOSTLY NEGATIVE.**
- `data/exp_hebb_vs_pseudoinverse_write_rule_v1/metrics.json`: `HARD_PASS`, *"pinv/hebb = 8.00x
  (theory ~7x)"*. **But `run_mode = smoke`, and the patterns are synthetic random bipolar vectors in
  a Hopfield capacity test.** It is a capacity result on made-up data, not a language result.
- `data/exp_kg_store_write_rule_decorrelated_ceiling_v1/metrics.json`, **`run_mode = full`**:
  **`HARD_FAIL_WRITE_RULE_NOT_THE_LEVER`** -- oracle MRR `hebb 0.0231 -> pinv 0.0240` (**1.0392x**),
  native `0.0140 -> 0.0156` (1.1138x), against a `HARD_PASS` bar of 2.0x. Positive control passed
  (the Hebbian arm reproduced its landed baseline), pinv was numerically stable and its must-fail
  controls fired. **This is a clean, well-controlled negative.**

**Why it is not yet dead, stated as a hypothesis and not as a finding.** `Sigma_xx^{-1}` can only pay
when `Sigma_xx` is far from identity. In the KG store the keys are **bound random codebook vectors**,
which at `d=1024` are near-orthogonal -- so `Gram ~ I` and the inverse is nearly a no-op **by
construction**. In the word store the inputs are **Zipf-distributed context counts**, whose
covariance is about as anisotropic as data gets. Same operation, opposite input regime.

**THE FREE PRE-CHECK, AND IT SHOULD BE RUN BEFORE ANYTHING ELSE ON THIS CANDIDATE.** Compute the
eigenvalue spectrum and condition number of `Gram` for (a) the KG store's keys and (b) the word store's
context vectors, on disk, with no experiment cell. **If the word store's `Gram` is not markedly worse
conditioned than the KG store's, the distinction above is refuted for free and C5 is closed.** If it
is dramatically worse, C5 is re-opened with a measured reason and moves up the ranking. *Either way
we learn it in minutes with no compute.* This is exactly the "state what was tested and what the
stronger version would be, then test THAT" discipline, applied to our own prior negative.

**SHELVE CRITERION (brain-framed).** Shelve if the pre-check shows `Gram` is already well-conditioned
-- decorrelation cannot be the missing operation when the inputs are already decorrelated. Note also
that the exact-inverse form is **not** biologically available; it is the closed-form limit of the
heterosynaptic/Oja family in C1, which is. **If C5 wins, the brain-faithful version to ship is C1.**

---

### **C6 -- BCM SELECTIVITY ON THE ACCUMULATOR.** `P ~ 0.15`

**Equation.** Per-anchor (or per-dimension) sliding threshold on the accumulator's own recent output:
```
    m_a  <-  m_a  +  eta * x * ( y - theta_a ),      y = <m_a, x>,      theta_a = EWMA( y^2 )
```

**Sweep:** the EWMA window (**hours in tissue -- sweep it in units of occurrences here, never import
a duration**), `theta` initialisation, warm-up length.

**Controls.** A working baseline rail (both prior attempts died on this), plus a **non-degeneracy
smoke discriminator** -- the v2 cell already specifies the right one (assert `max|y|` is non-trivial
in the first N updates) and it must additionally guard the **overflow** direction that actually
killed it.

**Composition prediction.** BCM's signature is **selectivity**: the accumulator should end up
responding to one context pattern rather than the average of all. So the no-relation rate should fall
and the winner distribution should get *less* generic. If it becomes more selective without becoming
more *relational*, BCM fixed the wrong kind of averaging.

**SHELVE CRITERION (brain-framed).** Shelve if, with a valid rail and non-degenerate initialisation,
the sliding threshold does not increase selectivity of the accumulator at any window -- the V1
phenomenon then has no analogue in a count-accumulator, which is a real structural statement.
**It cannot be shelved on the two existing runs: those are a broken rail and a crash.**

---

### **NOT RECOMMENDED: SYNAPTIC SCALING.** `P ~ 0.02`

It is the best-measured homeostatic rule in this drill and it is a **rank-0, scale-invariant
multiplier**. Cosine is scale-invariant. **It is a mathematical no-op on every metric we score.**
Recorded here explicitly so nobody proposes it on fidelity grounds without noticing that it cannot
move a single number we measure.

### **MARGINAL: WEIGHT DECAY / RECENCY.** `P ~ 0.08`
Cheap enough to carry as an extra arm inside C3 (`m_a = SUM_i lambda^(k-i) c_i`, sweep `lambda`;
`lambda=1` is the incumbent). Reweights *episodes*, not *dimensions*, so it cannot address
collocate dominance on its own.

---

## 10. WHERE THE FIELD DOES NOT HAVE AN EQUATION -- AND WE ARE THEREFORE INVENTING

The drill asks for this explicitly. Six honest gaps, each of which is a place where "brain-faithful"
cannot mean "copied":

1. **There is no measured cortical learning rate.** `eta_slow` in every CLS simulation is a model
   hyperparameter. No tissue measurement fixes it. **Sweep it; never quote one.**
2. **There is no equation for what gets replayed, or in what proportion.** Interleaving is the
   load-bearing ingredient and its *distribution* is a modelling choice; similarity-weighted
   interleaving is a recent proposal that works better, not a measurement.
3. **There is no principled rule for normalisation POOL membership.** Divisive normalisation's form
   is superbly fitted; `sigma`, `n` and *which units are in the pool* are fitted per area and per
   preparation. **Our own failure on this exact free parameter is already on disk** (sec 3.3): the
   read-side cell got the pool wrong twice and the WRONGPOOL control caught it.
4. **Oja's rule has never been demonstrated at a synapse.** It is our top candidate and it is the
   least pinned item in this drill. Saying so is the point.
5. **The measured plasticity closest to an error-driven cortical rule points the WRONG WAY for CLS.**
   Three-factor rules (`eligibility trace` set by pre/post coincidence, converted to a weight change
   by a later neuromodulatory factor) have direct experimental support, and BTSP in CA1 is a real,
   measured, **one-shot, seconds-scale, plateau-gated** rule. That is fast, hippocampal and episodic
   -- **the opposite of slow interleaved cortical learning**. The measured rules we have are for the
   system CLS says is *not* doing the abstraction. **There is no measured synaptic rule for the
   cortical half of CLS.**
6. **The adjacency-to-substitutability conversion has no tissue-level equation at all.** Section
   5.2's exact solution is a theorem about an artificial deep linear network; pTCM is a cognitive
   model fitted to recall data. Neither is a measured cortical circuit. **This is the single most
   important operation in ORGAN A and it is OUR-INVENTION-UNDER-TEST, informed by two converging
   models, not replicated from biology.** Any brief, prereg or organ row that calls it brain-derived
   is mislabelled -- the same correction this project already had to make about VSA binding.

**Where the biology IS strong enough to constrain us:** that the accumulator must be normalised
(pinned); that the normaliser must be **competitive between inputs on the same cell** rather than a
shared multiplier (pinned via heterosynaptic depression, and the shared-multiplier version is a no-op
for us anyway); that codes are **expanded and learned**, not compressed and random (pinned); and that
episodes are **never fully collapsed** (pinned, section 6).

---

## 11. HOW I ENUMERATED, AND CALIBRATION

**Repo facts.** `director_kb_query.py` / `substrate_query.sh` treated as STALE per the brief; I did
not use them. Instead:
- `ls hdlab/` (full listing, 141-ish modules) and `ls experiments/` filtered on the substantive terms
  `writerule|write_rule|organ_a|accumulate` and separately
  `predictive|surprise|residual|oja|bcm|normal|divisive|sparse_cod`, plus `ls notes/` filtered on
  `predictive|surprise|residual|coding`. These are enumerations of the directory, then filtered --
  not a keyword search of file contents.
- Every prior-work verdict quoted above was read from its own `data/<anchor>/metrics.json` on disk
  in this session, with `run_mode` reported alongside. Where `run_mode` is `smoke` (C5's first
  result) or `None` (the two `readout_writerule` cells) I said so.
- The four live steps were confirmed by opening `hdlab/reading_grounding_loop.py`,
  `hdlab/grounding_acquisition_loop.py` and `hdlab/ppmi_sparse_encoder.py` and
  `hdlab/whitening.py` at the cited lines.

**Absence claims I am making, and the enumeration behind each:**
- *"Divisive normalisation has never been applied at the WRITE step here"* -- based on enumerating
  `experiments/` for `divisive|normal|task_local` and reading the two hits' headers, both of which
  state in their own docstrings that they change **comparator arithmetic only** and that
  *"NOTHING UNDER hdlab/ IS MODIFIED"*. Bounded claim; a differently-named cell could exist.
- *"BCM has never produced a valid measurement here"* -- based on enumerating `experiments/` for
  `bcm` (2 hits) and reading both `metrics.json`.
- *"`ppmi_sparse_encoder` is not on the live write path"* -- weaker: based on reading the live write
  path's four steps, none of which import it. Per the standing rule that grep and eager import traces
  both get this wrong, **a runtime closure check would be needed to make this claim firmly.**

**Calibration applied.** All probabilities in section 9 are novel-synthesis estimates, **capped at
0.50** and deflated. They are for `P(CI-separated movement in winner composition)` -- deliberately
**not** `P(clears the 0.1390 floor)`, which is much lower for every candidate and which no
combination of these is likely to reach on its own.

**Standing rules I am explicitly NOT breaking, flagged because this drill's own source numbers
tempt it:** every ladder number quoted here is at the **oracle exact-key cue**, which is not the
operating point; `BEST_SINGLE_ORACLE` 0.3033 **consults the answer** and is a ceiling diagnostic,
never a capability; and no number here is compared across scorers or populations.

**A computational-theory label is not a neural system.** "Complementary learning systems",
"consolidation" and "semantic memory" appear in this note only as pointers to the equations they
stand for. Where I could not find an equation, section 10 says so.

---

## 12. SOURCES CONSULTED (learn-from and build-on, with credit)

Equations and evidence claims above are built on prior work by others; the synthesis and the
application to our write rule are ours, and the errors are ours.

- Saxe, McClelland & Ganguli, *A mathematical theory of semantic development in deep neural networks*
  -- the `tau dW/dt`, `Sigma_yx = U S V^T`, and `a_alpha(t)` solutions in sec 5.2 are taken from this
  paper. https://arxiv.org/abs/1810.10531 / https://www.pnas.org/doi/abs/10.1073/pnas.1820226116
- Carandini & Heeger, *Normalization as a canonical neural computation*, Nat Rev Neurosci 13:51-62 --
  the divisive form and the pool/semi-saturation framing.
  https://www.cns.nyu.edu/heegerlab/content/publications/Carandini-NRN2012.pdf
- Cooper & Bear, *The BCM theory of synapse modification at 30*, and the V1 dark-rearing evidence.
  https://brabeeba.github.io/neuralReadingGroup/cooper.pdf ; http://www.scholarpedia.org/article/BCM_theory
- Oja's rule and the honest statement that no direct synaptic demonstration exists.
  https://en.wikipedia.org/wiki/Oja's_rule ; https://arxiv.org/pdf/2408.08408
- Chistiakova/Volgushev et al., *Heterosynaptic plasticity prevents runaway synaptic dynamics*.
  https://www.jneurosci.org/content/33/40/15915
- Turrigiano-line synaptic scaling, and the in vivo non-replication.
  https://cshperspectives.cshlp.org/content/4/1/a005736.full.pdf ;
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1933594/ ;
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6901705/
- Olshausen & Field sparse coding objective and its V1 predictions.
  http://www.scholarpedia.org/article/Sparse_coding ;
  https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1003005 ;
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10516432/
- Predictive-coding mismatch signals in mouse cortex, **and the feature-selectivity alternative
  explanation** which I have carried as a live challenge rather than suppressed.
  https://www.sciencedirect.com/science/article/pii/S2211124721012262 ;
  https://elifesciences.org/articles/85111
- CLS interleaving and similarity-weighted interleaved learning.
  https://www.pnas.org/doi/10.1073/pnas.2115229119 ;
  https://www.biorxiv.org/content/10.1101/2025.06.25.661579v2.full
- Three-factor rules / eligibility traces, and BTSP in CA1.
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6079224/ ; https://elifesciences.org/articles/73046
- Prototype and exemplar codes tracked simultaneously in different regions; hippocampal separation
  vs integration pathways. https://elifesciences.org/articles/59360 ;
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10712951/
- Multiple Trace Theory vs standard consolidation.
  https://www.pnas.org/doi/10.1073/pnas.2123426119 ;
  https://link.springer.com/article/10.1007/s11559-007-9003-9
- Temporal Context Model and its predictive extension.
  https://memory.psych.upenn.edu/files/pubs/HowaKaha02.pdf ;
  https://people.bu.edu/marc777/docs/HowardEtal05-PsychReview.pdf
- Levy & Goldberg (SGNS implicitly factorises a shifted PMI matrix) and the point that PPMI alone
  does not capture second-order information while the SVD factorisation does.
  https://arxiv.org/pdf/1906.02479 ;
  https://en.wikipedia.org/wiki/Second-order_co-occurrence_pointwise_mutual_information

