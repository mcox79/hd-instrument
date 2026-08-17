# DRILL: the COMPUTATIONAL THEORY layer -- what the field believes each organ actually COMPUTES

**2026-08-16, Director (research role). LITERATURE DRILL + DESIGN ONLY.
No experiment cell authored. No experiment run. No `hdlab/`, `experiments/`, `tools/` or `preregs/`
file modified. No `metrics.json` touched. No subagent spawned. No LLM in any path.
Live runs 18496 / 30812 / 22984 never signalled, never polled, no output directory written.**

Machine-readable companion: `.claude/scan-out/computational-theory-drill.json`.

---

## 0. WHY THIS DRILL EXISTS -- the owner's diagnosis, and it is correct

> *"are you also drilling how people THINK the brain components work, and/or the theory of how the
> computation happens? That should be our first blueprint obviously."*

**We have been drilling ANATOMY.** Which structure, what it connects to, what a lesion does, what
the sparsity level is. Read `notes/ORGAN_MAP.md` and the three 2026-08-16 drills back to back and
the pattern is unmistakable: every one names structures well, cites lesion dissociations well, and
then arrives at "the equation is UNPINNED" and stops. `ORGAN_MAP` section 1 records **14 of 38
organs with the core operation UNPINNED** and treats that as the end of the enquiry.

**It is not the end of the enquiry. It is the point at which you switch literatures.** Between
"which brain part" and "what code to write" sits a layer the owner has named: what the field
believes the structure COMPUTES, by what algorithm, under what objective, and where the field
disagrees. Neuroscience does not pin the equation. **Computational neuroscience proposes several,
argues about them, and those proposals have different, checkable implementation consequences.**
Skipping that layer is why several of our components are anatomically motivated and
computationally arbitrary.

The owner's four examples of the cost, all confirmed against disk this pass:
- we chose a **conjunction OPERATOR with no computational justification** and it lost
  (`ORGAN_MAP` B-series marks the operator OURS/UNPINNED; the cell was CI-separated below flat);
- we built **pattern separation with no completion** (`dg_pattern_separation` is an orphan with zero
  `hdlab/` importers; the completer arrived later and is refuted at smoke);
- we **compress where the brain expands** (12 -> 12; the brain's EC -> DG is an expansion);
- we implemented **degraded-copy retrieval** where our task poses description/context retrieval
  (the partial-cue drill's four-cue-type taxonomy: we built type (a), the task poses (c)/(d)).

**This drill supplies the missing layer.** Calibration: the standing lit-scan penalty is applied
throughout -- every probability deflated 0.15-0.25, no novel-synthesis confidence above 0.50.
Where the literature is contested I report the contest and do not pick a winner. Several of our
worst calls came from treating a contested account as settled, and section 7 argues the largest one
is still live.

---

## 0.1 DEDUP -- run first, and the KB failed again in an instructive way

`.venv/Scripts/python.exe tools/director_kb_query.py --k 8 --tau 0.15`:

- `"hippocampal indexing theory what the hippocampus computes index versus relational map"`
  -> confidence 0.415. **Top eight hits are bare nodes**: `HIPPOCAMPUS` (0.415),
  `hippocampal_index.py` (0.415), `Hippocampus` (0.415), `hippocampus` (0.415), `hippocampal`
  (0.3975), `HIPPOCAMPUS_CA3` (0.3916), `HIPPOCAMPUS_CA1` (0.3867), `HIPPOCAMPUS_CA2` (0.3799).
  **Nothing conceptual. That is a spelling match on the word "hippocampal".**
- `"vector symbolic architecture hyperdimensional computing brain theory binding criticism"`
  -> confidence 0.4199. Top hit the node `hyperdimensional computing`; hits 2-7 are **CITATION-LIST
  chunks** of three June drills (`research_drill_ner_3datapoint_plateau...`,
  `research_drill_field_VSA_algebraic_foundation_5x_2026-06-07`,
  `research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23`).

The index reports `encoder=char_trigram_v1`. **The substrate KB's retrieval channel is a SPELLING
channel** -- the same channel that beats our read-out 8.70% to 4.80% -- and it matched the word
"hyperdimensional" inside bibliographies. This reproduces the finding of all three sibling 08-16
drills: **for a concept query the filesystem enumeration is the stronger instrument.**

**So the absence claim below is made by ENUMERATION, not by search** (standing rule). Ripgrep over
`notes/`:

| probe | files |
|---|---|
| `Smolensky\|tensor product variable binding\|Gayler\|Plate 1995\|Holographic Reduced Represent` | 60+ (limit hit) |
| `predictive coding\|free energy\|Friston` | 60+ (limit hit) |
| `indexing theory\|Teyler\|relational memory theory\|Eichenbaum\|cognitive map` | 28 |
| `Olshausen\|sparse coding\|efficient coding\|Barlow\|metabolic cost` | 40+ (limit hit) |

**WHAT PRIOR WORK EXISTS AND IS CREDITED, NOT RE-DERIVED.** The MECHANICS of VSA have been drilled
repeatedly and well: `research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md` (Plate,
Kanerva, Gayler, Frady resonators), `research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md`
(Kleyko surveys, Smolensky TPR), `prior_art_vsa_hdc_for_language_2026-08-06.md`,
`research_vsa_learned_reader_prior_art_scour_2026-07-18.md`, and
`research_R9_source_item_dissociation_2026-05-21.md` section 1.7 ("The substrate's algebraic
alternative -- Smolensky tensor binding"). Hippocampal indexing, CLS and the key/value framing are
already banked in `research_regime_switch_dense_retrieval_sparse_storage_brain_grounding_2026-07-04.md`.
Predictive coding as an ACTIVE-INFERENCE control theory is banked in
`research_drill_substrate_as_active_inference_control_theory_lyapunov_stability_unifying_normative_theory_2x_2026-06-12.md`.

**WHAT IS GENUINELY NEW, stated narrowly:**
1. **The CRITIQUE OF VSA AS A BRAIN THEORY.** No enumerated note names O'Reilly/Busby coarse-coded
   conjunctive binding, Hummel's role-filler-independence objection, Shadlen & Movshon's
   "Synchrony unbound", or the cleanup-memory objection **as rivals to our own foundational
   choice**. Every prior VSA note treats VSA as the frame and drills inside it. Section 7.
2. **Sparsity's FOUR different objectives with four different optima**, and the resulting
   explanation of the MTL-band-worst sweep result. Section 3.
3. **The successor-representation reading of our own thematic-consolidation win.** Section 1.
4. **The convergence of predictive coding and the fast-mapping exposure census onto ONE missing
   update rule.** Section 5.
5. **The "no theoretical justification at all" enumeration.** Part C.
6. **The two-sided empirical literature on fidelity-predicts-performance** and the power argument.
   Part D.

---

# PART A -- THE COMPUTATIONAL THEORY, ORGAN BY ORGAN

Format per item: WHAT IS IT COMPUTING (field's own terms) / ALGORITHM OR OBJECTIVE / EVIDENCE /
WHERE THEORIES DISAGREE. Every claim marked **PINNED-BY-EVIDENCE**, **CONTESTED** (competing
accounts named), or **UNPINNED**.

---

## 1. HIPPOCAMPAL INDEXING THEORY AND ITS RIVALS

**There are FOUR live accounts of what the hippocampus computes, they are not notational variants
of each other, and they make different implementation demands. We have been building as if the
answer were obvious. It is not.**

### 1a. INDEXING -- the hippocampus computes an ADDRESS, and holds no content

- **COMPUTING:** a sparse POINTER SET into distributed neocortical activity. Teyler & DiScenna 1986;
  Teyler & Rudy 2007 *Hippocampus* 17:1158; Goode, Tanaka, Sahay & McHugh 2020 *Neuron* 107:805
  ("the hippocampal engram as a memory index").
- **ALGORITHM:** on an episode, allocate a sparse hippocampal ensemble and form bidirectional links
  to the cortical modules active at that moment. At retrieval, partial reactivation of the index
  RESYNCHRONISES those cortical modules. **The content never enters the hippocampus.**
- **OBJECTIVE:** none is stated. This is a mechanism claim, not an optimisation. That is itself a
  finding -- indexing theory does not tell you what to minimise.
- **EVIDENCE:** engram-tagging and optogenetic reactivation -- driving the index without a natural
  cue produces recall. **PINNED-BY-EVIDENCE as an architecture.**
- **UNPINNED:** the ALLOCATION RULE. Nothing says which cells get recruited to an index.

### 1b. CONJUNCTIVE AUTOASSOCIATIVE STORE -- the hippocampus computes a content-addressable memory

- **COMPUTING:** a store of CONJUNCTIONS of cortical features, retrievable from a part.
  Marr 1971; Treves & Rolls 1992/1994; McClelland, McNaughton & O'Reilly 1995;
  O'Reilly & McClelland 1994.
- **ALGORITHM:** one-shot Hebbian outer product on a sparse code; retrieval by recurrent settling.
- **OBJECTIVE, and this one IS quantitative:** maximise retrievable patterns subject to
  interference. Capacity `p ~ k*C / (a * ln(1/a))`, `C` = recurrent connections per cell,
  `a` = sparseness. **This is the only organ in the whole drill with a closed-form design equation
  that we are not using.**
- **EVIDENCE:** CA3 recurrent anatomy; ~36,000 patterns at rodent CA3 connectivity;
  CA3-NMDA knockouts impair completion from a degraded cue specifically.
  **PINNED-BY-EVIDENCE as a capacity theory; the UPDATE RULE remains UNPINNED** (`ORGAN_MAP` D2 is
  correct that Hopfield sign-update and modern-Hopfield softmax are OUR imports).

**1a VERSUS 1b IS A REAL DISAGREEMENT AND IT IS THE ONE THAT BEARS ON US MOST.** Under indexing,
what you store is a POINTER and the retrieval product is a re-instated CORTICAL pattern -- the
hippocampal code need never be decodable as content. Under the conjunctive store, the hippocampal
pattern IS a compressed version of the content and you read content back out of it.
**Our flat store is 1b, done without the sparsity that 1b's own capacity equation requires. The
"LINK-NOT-RECONSTRUCT" design banked on 2026-07-04 and never implemented is 1a.**
**CONTESTED.** Goode 2020 frames them as compatible at different levels (index for allocation,
autoassociation for completing the index), but that reconciliation is a proposal, not a measurement.

### 1c. RELATIONAL MEMORY / COGNITIVE MAP -- the hippocampus computes a STRUCTURE over items

- **COMPUTING:** relations among items, supporting inference about pairs never experienced together
  -- transitive inference, associative inference, acquired equivalence.
  O'Keefe & Nadel 1978; Cohen & Eichenbaum 1993; Eichenbaum 2017.
- **ALGORITHM:** **UNPINNED as an equation.**
- **OBJECTIVE:** flexible generalisation, explicitly NOT storage fidelity.
- **EVIDENCE:** hippocampal lesions spare item memory and impair relational inference.
  **PINNED-BY-EVIDENCE as a dissociation.**
- **THE BUILD CONSEQUENCE WE HAVE NEVER DRAWN:** under 1c the primary stored object is an EDGE, not
  an item, and **a store that cannot answer about a pair it never saw has missed the point of the
  organ.** Our store's primary object is a per-word accumulated vector. We have no edge in the
  store at all -- our relations live in a separate `.pkl`.

### 1d. PREDICTIVE MAP / SUCCESSOR REPRESENTATION -- the hippocampus computes a DISCOUNTED FUTURE

- **COMPUTING:** `M(s,s') = E[sum_k gamma^k * 1{s_k = s'}]`, i.e. `M = (I - gamma*P)^-1`. Place
  fields are rows of `M`; grid cells are its eigenvectors. Stachenfeld, Botvinick & Gershman 2017
  *Nat Neurosci*.
- **OBJECTIVE:** predict future state occupancy at discount `gamma`. This is a REPRESENTATION that
  makes value computation linear.
- **EVIDENCE:** place-field skewing in directed environments; hippocampal pattern similarity
  mirroring the COMMUNITY STRUCTURE of a graph (states with similar successors represented
  similarly); successor-like representation found in human hippocampus **and V1**
  (Ekman et al., *eLife* 2023). **PINNED-BY-EVIDENCE as a representational signature.**
- **CONTESTED, and the contest is about the LEARNING RULE:** TD learning is not known to be
  implemented in hippocampal networks. George et al. 2023 show STDP + theta phase precession
  approximates `M` without TD. Also `M` is POLICY-DEPENDENT -- it is a map of what you DO, not of
  what IS, which is a real objection to it as a general memory theory.

### 1e. THE SYNTHESIS, AND ONE STRATEGIC READ WORTH THE OWNER'S ATTENTION

Stated as four build instructions that CONFLICT, which is the point:

| account | says the store's primary object is | says retrieval is | our store |
|---|---|---|---|
| 1a index | a sparse ADDRESS with a LINKED cortical value | reinstatement of the linked value | no key at all |
| 1b conjunctive | a compressed CONTENT vector | settling to the nearest attractor | this, without the sparsity |
| 1c relational | an EDGE | inference over a graph | edges live outside the store |
| 1d predictive | a DISCOUNTED-FUTURE co-occurrence | a linear read of `M` | first-order co-occurrence |

**MY STRATEGIC READ, LABELLED AS A HYPOTHESIS PENDING VET, NOT A MEASURED VERDICT.** The strongest
positive result this programme has produced recently is thematic-graph consolidation: replay-partner
synonym purity 4.4x, channel 0.2417 -> 0.2795, open-vocabulary read-out **0.0462 -> 0.1069**,
clearing four matched controls -- **and confirming a PRE-WRITTEN prediction that the pull would be
SECOND-ORDER.** A second-order relational pull, learned from co-participation, that beats
first-order, is the empirical signature of a successor-like representation. `ORGAN_MAP` D7 lists
the successor representation as **MISSING** and gives its equation. And `ORGAN_MAP` D4 records that
the replay SELECTION function's leading normative candidate (Mattar & Daw 2018,
`priority = GAIN x NEED`) computes NEED from exactly that missing `M`.

**So we may have measured the signature of an organ we have not built, twice, in two different
components, without connecting them.** P that a direct successor-representation arm (compute `M` on
our own thematic graph and use its rows as the code) beats the first-order arm CI-separated:
**~0.35** after the calibration penalty. Low because our graph is sparse and the same 1-hop-only
ceiling that killed `grounding_snowball` applies -- `M`'s value is in the multi-hop tail, and our
multi-hop tail is noise by d3. **But it is cheap, it is glass-box (a matrix inverse of a graph we
own), it uses no external asset, and it has never been run.**

---

## 2. PATTERN SEPARATION AND COMPLETION AS A COMPUTATIONAL PAIR

### 2a. WHAT THE PAIR COMPUTES

- **Separation (DG):** expand into a much larger, sparser layer so that two similar inputs become
  nearly orthogonal. Formally: the OUTPUT overlap falls faster than the INPUT overlap.
  **PINNED-BY-EVIDENCE and it was MEASURED as an inequality**, not asserted -- Neunuebel & Knierim
  2014 *Neuron* 81:416 show the DG representational change EXCEEDS its entorhinal input's change,
  and the CA3 change is LESS than both its entorhinal and DG inputs. Those two inequalities are the
  operational definitions of separation and completion.
- **Completion (CA3):** recurrent settling toward the nearest stored attractor.
- **THE ORDER MATTERS AND IS PINNED:** separation happens at ENCODING, completion at RETRIEVAL.

### 2b. THE TRADEOFF, AND ITS RESOLUTION -- the part we never used

The tradeoff is formal and named: **O'Reilly & McClelland 1994, "Hippocampal conjunctive encoding,
storage, and recall: avoiding a trade-off"** (*Hippocampus* 4:661). Separation wants sparse,
decorrelated codes, which starve completion of the overlap it needs; completion wants overlapping
codes, which destroy separation.

**THE FIELD'S RESOLUTION IS A REGIME SWITCH, NOT A PARAMETER SETTING, AND THIS IS THE MOST
ACTIONABLE SENTENCE IN THIS SECTION.** The same network does both by using DIFFERENT PATHWAYS at
different times:
- **encoding mode:** mossy-fibre path dominant (few, powerful synapses), recurrent collaterals
  suppressed, so a NEW pattern is written rather than an old one recalled;
- **retrieval mode:** direct perforant path + recurrent collaterals dominant.
- **The switch is neuromodulatory** -- acetylcholine, Hasselmo's SPEAR framework. High ACh =
  encode, low ACh = retrieve. **PINNED-BY-EVIDENCE as a modulatory switch; the exact gain values
  are UNPINNED.**

**WE HAVE NO REGIME SWITCH AT ALL.** One store, one path, one operating point for both write and
read. The 2026-07-04 drill already said "the brain LITERALLY switches representational/dynamical
regime between store and recall" and it remains unimplemented.

**CONTESTED, and report it rather than adjudicate:** whether CA3 is a DISCRETE attractor network at
all. Leutgeb et al. 2007 (*Learn Mem* 14:745, "Pattern separation, pattern completion, and new
neuronal codes within a continuous CA3 map") report graded, continuous CA3 responses rather than
discrete attractor jumps; continuous-attractor accounts (Samsonovich & McNaughton) treat CA3 as a
manifold. **If CA3 is continuous, "settle to the nearest stored pattern" is the wrong operation and
our three floored attractor nulls are less informative than they look.**

### 2c. WHAT THE THEORY SAYS THE CUE MUST BE -- and it says our "defect" is correct

We measured our partial cue at participation ratio **202.04/256** against the store's **88.74/256**
and called it a defect: "2.3x higher-rank than the thing it is querying".

**THE THEORY SAYS THAT IS THE NORMAL STATE OF AFFAIRS AND THE CUE SHOULD BE DENSER STILL.**
Treves & Rolls 1992's quantitative argument for two input systems: to STORE you want a small number
of strong signals that can dominate the recurrence (mossy fibre); to RETRIEVE you want a
numerically LARGE input through individually WEAK, associatively-modified synapses, so that even a
partial cue suffices (direct perforant path). The retrieval cue is therefore a DENSE cortical
pattern addressing a SPARSE store through a LEARNED heteroassociative matrix.

Quantitatively the brain's mismatch is far larger than ours: rat EC layer II is order `2e5` cells
projecting to order `1e6` granule cells -- a **5x expansion** into a code that is then roughly
**100x sparser**. Our 2.3x rank ratio is, on the theory's terms, an under-mismatch on both sides:
**our cue is not dense enough relative to a store that is not sparse enough.**

**BUILD CONSEQUENCE, and it contradicts a cell we already ran.** The `two-channel-cue` cell spent a
whole cell engineering the cue to be LOWER-rank -- moving away from the theory on purpose -- and
measured no gain. That is what the theory predicts. **The missing component is the LEARNED
TRANSLATOR, and the partial-cue drill's enumeration confirms we own exactly zero cue-to-store
map-fitting primitives in 147 `hdlab` modules.**

---

## 3. SPARSE DISTRIBUTED CODING THEORY -- what is sparsity FOR?

**THIS IS THE ITEM WHERE THE THEORY MOST CLEANLY EXPLAINS ONE OF OUR OWN MEASUREMENTS, AND THE
EXPLANATION CHANGES WHAT WE SHOULD BUILD.**

### 3a. FOUR OBJECTIVES, FOUR OPTIMA. There is no single "optimal sparsity".

| # | objective | proposed by | what it optimises | direction of the optimum |
|---|---|---|---|---|
| (i) | **METABOLIC** | Levy & Baxter 1996; Attwell & Laughlin 2001; Lennie 2003 | bits per joule | very LOW active fraction; Attwell/Laughlin's budget bounds mean rates below ~1 Hz |
| (ii) | **CAPACITY / INTERFERENCE** | Marr 1971; Willshaw; Tsodyks & Feigel'man; Treves & Rolls 1990/1992 | number of stored patterns | monotonically LOWER is better -- `p ~ C/(a ln(1/a))` |
| (iii) | **EFFICIENT CODING OF STATISTICS** | Barlow 1961; Olshausen & Field 1996/1997 | reconstruction error + a sparsity prior on natural input | an INTERMEDIATE optimum; recovers V1 Gabors |
| (iv) | **DECODABILITY / LINEAR SEPARABILITY** | Babadi & Sompolinsky 2014; Dasgupta, Stevens & Navlakha 2017 (fly) | ease of a downstream LINEAR readout | expansion + sparsification, an intermediate `k` |

**These are FOUR DIFFERENT QUESTIONS and the literature routinely conflates them. So do we.**

**A category error to stop making, and it may be live in our own docs.** The frequently-quoted
cortical "sparseness index ~0.2-0.3" (Rolls & Tovee) is a **Treves-Rolls sparseness statistic over
a tuning distribution**, not an active fraction. It does NOT mean 20-30% of neurons are on. The MTL
~0.2% figure (Waydo et al. 2006) IS an active fraction. **Quoting the two side by side as if they
were the same quantity is exactly the "a number may not be carried between populations" fault, in
the biology rather than in our metrics.** `ORGAN_MAP` B4 gets this right and warns it is a trap;
several downstream summaries do not.

### 3b. DOES THEORY EXPLAIN OUR MTL-BAND-WORST SWEEP? YES. IT PREDICTS IT.

Our measurement (`sparsify-right-object.json`, POP_FULL, exact key, d=1024, hit@1):

```
f=0.002  0.0396      <- the PINNED MTL band
f=0.005  0.0496
f=0.010  0.0606
f=0.020  0.0706
f=0.050  0.0696
f=0.100  0.0774      <- best
f=0.200  0.0749
f=0.300  0.0769
f=0.500  0.0759
DENSE (no cap) 0.0744
```

Monotone rise OUT of the MTL band up to ~10%, then flat, ending at parity with doing nothing.
The cell's own honest note: *"the PINNED MTL band (0.2-1%) was the WORST meaning zone in the
sweep."*

**TWO INDEPENDENT THEORY REASONS THIS IS THE PREDICTED RESULT.**

1. **We applied objective (ii)'s optimum and measured objective (iii)/(iv)'s quantity.** MTL 0.2%
   is optimal for STORING MANY PATTERNS WITHOUT INTERFERENCE. We scored SIMILARITY STRUCTURE for a
   meaning judgement. **Separation is the deliberate destruction of similarity** -- that is not a
   side effect, it is the function. A code optimised to make two similar things orthogonal is
   optimised to make a similarity judgement impossible. Applying it to a meaning metric should
   hurt, and it did, monotonically.
2. **The field says this out loud, and the paper is a critique of sparse coding itself.**
   Spanne & Jorntell 2015, *Trends in Neurosciences* 38:417, "Questioning the role of sparse coding
   in the brain": the advantages of sparse coding "come at the cost of several trade-offs, with the
   **lower capacity for generalization** being especially problematic", and dense coding has a
   representational capacity that grows exponentially in the number of neurons where a sparse
   scheme grows only linearly. They further argue the beneficial properties ascribed to sparse
   coding are achievable by other means (silent synapses, inhibitory interneurons) and that the
   experimental support for cortical sparse coding is itself questionable.
   **CONTESTED, therefore -- sparse coding is not the settled account we have been treating it as.**

**THE BUILD CONSEQUENCE, AND IT RECONCILES ITEM 3 WITH ITEM 1.** Do NOT sparsify the meaning code.
**Sparsify the ADDRESS and keep the VALUE dense and graded.** That is objective (ii) applied to the
key and objective (iii) applied to the value -- and it is precisely the LINK-NOT-RECONSTRUCT design
banked on 2026-07-04, arrived at from a completely different literature. **Two independent routes
now point at the same unimplemented design. That raises my confidence in it more than either route
alone.**

Corollary that saves future cells: our own sweep already tells us the value's operating point.
The best sparse point is `f=0.10` and it is NOT CI-separated from dense (+0.0030 [-0.0030,+0.0088]).
**There is nothing to win by sparsifying the value. Stop sweeping it.**

---

## 4. COMPLEMENTARY LEARNING SYSTEMS AS A COMPUTATIONAL ARGUMENT

**The CLS argument is NOT anatomical. It is a mathematical dilemma, and stating it as anatomy
throws away the part that tells you what to build.**

### 4a. THE ARGUMENT, in its own terms

McClelland, McNaughton & O'Reilly 1995 *Psychol Rev* 102:419:
1. To extract structure that GENERALISES, you must average over many examples with a SMALL learning
   rate and INTERLEAVED presentation. Small rate + interleaving is intrinsically SLOW.
2. To learn one event in ONE SHOT you must take a LARGE weight step. In a network with OVERLAPPING
   distributed representations, a large step moves the weights far from the multi-task optimum and
   destroys prior learning -- **catastrophic interference** (McCloskey & Cohen 1989; Ratcliff 1990).
3. **These two demands cannot be met by one set of weights.** Therefore two systems.
4. **The quantity that governs interference is REPRESENTATIONAL OVERLAP.** A sparse,
   pattern-separated system can take large steps safely. **That is the same `a` from item 3's
   capacity equation -- CLS and sparse coding are ONE argument, not two.**

The framing that matters: this paper "transformed what had been widely regarded as the fundamental
failing of neural network models into a point of leverage in understanding the functional
organization of the brain."

### 4b. WHAT CONSOLIDATION ACTUALLY COMPUTES

**Interleaved replay approximates the gradient of the JOINT objective over old-plus-new data, using
samples generated by the fast store.** It is stochastic gradient descent on a dataset you no longer
have. That is the precise computational content, and it is routinely lost when consolidation is
described as "strengthening" or "transferring". **Strengthening is not what it computes. Sampling
an unavailable dataset is.**

### 4c. WHERE IT IS CONTESTED

- **Schema versus interference.** Tse et al. 2007 *Science* 316:76 -- schema-congruent paired
  associates become hippocampus-independent within ~48 h after a SINGLE trial. Pure interference
  avoidance does not predict that. Kumaran, Hassabis & McClelland 2016 (*TiCS*, "What learning
  systems do intelligent agents need? CLS theory updated") adds schema-dependent fast cortical
  learning to the theory. **So CLS 1.0's "cortex is always slow" is superseded by its own authors.**
- **Real versus generative replay.** Van de Ven, Siegelmann & Tolias 2020 (*Nat Commun*) show
  generative replay achieves the same interference protection without storing episodes.
  **UNPINNED which the brain does.**
- **Interleaving RATIO is UNPINNED.** The principle is pinned; no number is.

### 4d. WHAT CLS WOULD HAVE TOLD US TO BUILD, AND WHERE WE DIVERGE

Our divergence is already correctly named in `LONG_TERM_PLAN` Phase 5 ("one store doing both
jobs"). **The sharper consequence we have NOT drawn is about the SLOW system's OBJECTIVE.**

CLS says the slow system's job is to **extract the latent structure shared across episodes**. Our
slow store accumulates `self._sums[lemma] += ctx_vec` -- a raw first-order co-occurrence sum. That
IS a statistic across episodes, but **it is not the statistic CLS names**, and we have measured the
consequence precisely: **only 0.46% of a word's top-20 neighbours in our store are its synonyms.**

**And here is the divergence that has never been written down.** Every implemented cortical model in
the CLS lineage -- Rogers/McClelland's semantic network, Jackson/Rogers/Lambon Ralph 2021's hub
model -- extracts that latent structure with an **ERROR-DRIVEN** objective, not a Hebbian sum.
`ORGAN_MAP` B1 already flags this and flags the honest caveat with it: *"Do not over-read this into
'training is the right tool' -- but equally, do not claim the brain's model is Hebbian."*
**CONTESTED, and it must be reported as contested.** But the fact that we implemented the CLS
ARCHITECTURE with an objective no CLS model uses is a real, named, unexamined divergence, and it
sits directly upstream of the 0.46% number.

---

## 5. PREDICTIVE CODING / FREE ENERGY AS AN ACCOUNT OF CORTICAL COMPUTATION

### 5a. WHAT IT SAYS CORTEX COMPUTES

Rao & Ballard 1999 *Nat Neurosci* 2:79; Friston 2005/2010. Each cortical level maintains a
GENERATIVE MODEL of the level below. The FEEDFORWARD signal is not the sensory signal, it is the
**RESIDUAL** `x - x_hat`, weighted by PRECISION (inverse expected variance). Learning minimises
prediction error. `ORGAN_MAP` G2 already carries this as a pinned equation form.

### 5b. WHAT IT PREDICTS FOR WORD LEARNING FROM CONTEXT -- and there is a direct, implemented model

**The N400 IS lexico-semantic prediction error.** Nour Eddine, Brothers, Wang & Kuperberg 2024
*Cognition* ("A predictive coding model of the N400", PMID 38428168) implement predictive coding
explicitly and show the magnitude of lexico-semantic prediction error tracks the N400's temporal
dynamics AND its sensitivity to bottom-up lexical variables, priming, context, and their
higher-order interactions. Corroborated from the modelling side by Michaelov et al.
(*Neurobiology of Language* 5:136) tracking lexical and semantic prediction error in ANN sentence
models. **PINNED-ENOUGH TO BUILD ON:** the brain's signal for learning a word from its context is a
PREDICTION ERROR, it is measurable, and it has a working computational model.

**THE PREDICTION FOR US, STATED AS AN EQUATION:** a word's meaning should be updated by
`delta ~ precision * (observed_context - predicted_context)`. **An unsurprising occurrence should
teach approximately nothing.**

**Our loop does `self._sums[lemma] += ctx_vec`. Every occurrence is weighted 1.**

### 5c. THE CONVERGENCE, and it is the strongest single build recommendation in this drill

**Two completely independent literatures arrive at the same instruction.**
- Predictive coding: weight the update by the RESIDUAL.
- Fast-mapping / word learning: Medina et al. 2011 *PNAS*'s exposure census -- **~90% of natural
  exposures are UNINFORMATIVE, ~7% are highly informative** (already banked in the 08-16 bridging
  drill, section A2). An informative-encounter SELECTOR is a REQUIRED upstream component, not a
  workaround.

One says weight by surprise; the other says most exposures carry nothing. **They are the same
instruction from two directions, and we implement neither.** A surprise-weighted accumulator is a
two-line change to the observe path, is glass-box, uses no external asset, needs no LLM, and has a
pre-registered prediction from both literatures. I regard this as the highest
theory-support-per-unit-cost item this drill found.

Honest deflation: the reason it may not fire is that our "prediction" would have to come from the
store we are criticising, so early in training the residual is just the observation and the change
is a no-op. **That is a real design risk and it must be pre-registered as a possible null cause,
not discovered afterwards.** P(a surprise-weighted accumulator beats the uniform one CI-separated
on the rho instrument) ~ **0.35** after the penalty.

### 5d. WHERE IT IS CONTESTED -- loudly

- **The free energy principle is widely criticised as UNFALSIFIABLE.** The recurring charge is that
  it is "a mathematical tautology: true by definition rather than by empirical test", with
  categorical confusion between thermodynamic and information-theoretic free energy. The most
  useful formulation of the defence is itself a concession worth adopting: **the FEP is not
  falsifiable, but a PROCESS THEORY of how a particular system minimises free energy is.**
  **CONTESTED. Never quote free energy as pinned. Quote a process theory or quote nothing.**
- **Explicit error UNITS have weak direct evidence.** Alternatives exist (dendritic error coding;
  "predictive processing without error units").
- **Whether prediction error drives LEARNING or only ATTENTION/GAIN is contested.**

### 5e. RIVAL OR COMPATIBLE WITH WHAT WE ARE BUILDING?

**COMPATIBLE with VSA, RIVAL to Hebbian accumulation.** Nothing in vector-symbolic algebra forbids a
residual update -- `acc += (ctx - predicted)` is still a bundle, still glass-box, still one matmul.
The rivalry is with our LEARNING RULE, not with our representation. That is a useful narrowing:
**adopting predictive coding costs us nothing architecturally and does not touch the invariant.**

---

## 6. SEMANTIC HUB-AND-SPOKE -- what does the ATL hub COMPUTE?

### 6a. THE FIELD'S OWN ANSWER, and it is not "a similarity space"

Lambon Ralph, Jefferies, Patterson & Rogers 2017 *Nat Rev Neurosci* 18:42; Rogers et al. 2004:

> the ATL computes **the nonlinear mappings required to transform modality-specific information into
> pan-modal, multifaceted concepts**, and expresses **DEEP conceptual similarity that is not
> strongly influenced by superficial similarity in any one modality** -- pear and light bulb have
> similar shapes; the ATL instead captures the greater conceptual overlap between pear and
> pineapple.

**THE ALGORITHM IN THE IMPLEMENTED MODELS, and this is the load-bearing distinction:** the hub is a
recurrent network trained by ERROR-DRIVEN learning to reproduce ANY spoke's pattern from ANY other
spoke's pattern. **Its objective is CROSS-MODAL RECONSTRUCTION -- an autoencoder over modalities.**
The similarity space is what EMERGES from that objective; it is not the objective.

**WE BUILT THE SIMILARITY SPACE DIRECTLY AND SKIPPED THE OBJECTIVE THAT PRODUCES IT.** That is the
cleanest statement of our B1 divergence and it is stronger than `ORGAN_MAP`'s current
"WRONG-OP: unweighted shared-feature overlap". The problem is not only that the overlap is
unweighted; it is that a hand-authored overlap dictionary is the OUTPUT SHAPE of a process we never
ran.

### 6b. FOUR CANDIDATE ANSWERS, and they are not the same claim

| candidate | what it implies for the code | status |
|---|---|---|
| a SIMILARITY SPACE | build a metric | **our implicit assumption; NOT the field's statement** |
| a CROSS-MODAL TRANSLATOR | build a reconstructor over spokes | the implemented models' actual objective |
| a CONJUNCTIVE BINDER / feature integrator | build binding, test on NEW concept acquisition | supported: semantic dementia shows impaired FEATURE INTEGRATION when acquiring new concepts |
| a DEEP-TO-SHALLOW COMPRESSOR WITH COMPLETION BACK ONTO SPOKES | build a LOOP, not a map | Jackson, Rogers & Lambon Ralph 2021 *Nat Hum Behav* 5:774 -- the core operation is **pattern completion via a compact abstract label feeding BACK onto shallower unimodal features** |

**The field's current best statement is the LAST one, and it is a LOOP.** Backward connections are
consistently STRONGER than forward (Tiesinga 2023 *Sci Rep*), which is the anatomy of a generative
model, not of a feedforward encoder. **Our hub is a feedforward sum with no back-projection to the
spokes at all.** That is a named, un-built organ: the hub-to-spoke return path.

### 6c. THE DUAL-HUB THEMATIC ACCOUNT WE ADOPTED LAST NIGHT -- and the contest we did not report

What the thematic system computes: **co-occurrence in EVENTS** -- a fundamentally different
similarity relation from the taxonomic one. Taxonomic = SUBSTITUTABILITY (dog/wolf can fill the
same slot). Thematic = COMPLEMENTARITY (dog/leash co-occur in an event and cannot substitute).
**Those are different metrics over the same vocabulary, and no single vector space can express both
as "high cosine" without collapsing them.** That is a formal statement and it bears directly on why
pouring a thematic channel into a sensorimotor rating space may not land -- as the target-space
drill found independently from the norms' own authors.

**THE CONTEST, WHICH LAST NIGHT'S ADOPTION DID NOT REPORT.** Schwartz et al. 2011 *PNAS* (VLSM
double dissociation) and Mirman, Landrigan & Britt 2017 support two anatomically separate hubs.
**Lambon Ralph's group argue the temporo-parietal effects reflect SEMANTIC CONTROL demands rather
than a second STORE** -- the controlled-semantic-cognition framework treats ATL as the single
representational hub and IFG/pMTG as a control network that reshapes access to it. Under that
reading, thematic relations are not stored elsewhere; they are RETRIEVED under different control
settings from the same store.

**This matters to our build, concretely.** If the dual-hub account is right, we need a second
STORE. If the control account is right, we need a second CONTROL SETTING over one store -- which is
`ORGAN_MAP` C3's multiplicative gain, already built once and HARD_FAIL. **We adopted the dual-hub
reading as though it were settled. It is CONTESTED, and the two readings imply different builds.**
Recording that here is the point of this drill.

---

## 7. VECTOR-SYMBOLIC / HYPERDIMENSIONAL COMPUTING AS A BRAIN THEORY

**THE BRIEF CALLS THIS THE MOST IMPORTANT ITEM AND IT IS RIGHT. WE HAVE NEVER DRILLED THE CRITIQUE
OF OUR OWN FOUNDATIONAL CHOICE.** Six prior VSA drills exist and all six drill INSIDE the frame.

### 7a. WHO ARGUES THE BRAIN DOES VSA-LIKE BINDING, and it is a serious case

- **Smolensky 1990** (*Artif Intell* 46), tensor product variable binding -- the formal origin,
  explicitly a theory of how a connectionist system can be systematic.
- **Plate 1995** (*IEEE TNN* 6:623) HRR; **Kanerva 1988** SDM / **2009** hyperdimensional computing;
  **Gayler 2003**, "Vector Symbolic Architectures answer Jackendoff's challenges for cognitive
  neuroscience" (cs/0412059) -- **the strongest explicit "VSA is a brain theory" paper**, arguing
  VSA meets the four challenges (binding, the problem of two, variables, working/long-term memory)
  that Jackendoff posed to neuroscience.
- **Eliasmith's Neural Engineering Framework / Semantic Pointer Architecture, and Spaun**
  (Eliasmith et al. 2012 *Science* 338:1202): circular convolution IMPLEMENTED in spiking LIF
  neurons driving a working brain model. **This is the single strongest existence proof that a VSA
  operation is neurally realisable, and it should not be dismissed.**
- **Biological anchor points that are real measurements in real brains, not models:**
  - the fly's **random expansion** antennal lobe -> Kenyon cells with k-winner inhibition
    (Dasgupta, Stevens & Navlakha 2017 *Science*) is a genuine random-projection HD operation;
  - **grid modules as a modular, residue-number-like code** embedding a low-dimensional variable in
    a high-dimensional population (Fiete and colleagues) is a genuine algebraic high-dimensional
    code;
  - **gain fields** (Andersen; Salinas & Abbott 1996) are a genuine MULTIPLICATIVE combination of
    two variables in cortex -- the closest measured thing to a binding operation.

### 7b. WHAT THE CRITICS SAY -- and I am going to be blunt because we have never written this down

**(a) NO ONE HAS MEASURED AN ALGEBRAIC BINDING OPERATOR IN CORTEX.** My own literature scan on
"evidence brain implements vector symbolic binding neural circuits" returned, as its own summary
sentence, that the results *"focus primarily on computational models inspired by neuroscience rather
than direct neurobiological evidence of vector symbolic binding in the brain."* No recording has
shown a population computing a circular convolution or an elementwise product of two full
representations. **Gain fields are the nearest measured multiplicative interaction, and they are the
product of a SCALAR GAIN with a tuning curve -- not the product of two full-rank vector codes.**

> **THE CORE OPERATION OF OUR SUBSTRATE IS UNPINNED IN THE BRAIN.**
> That is the single most important sentence in this drill. It belongs in the plan.

**(b) THE LEADING RIVAL IS CONJUNCTIVE CODING, AND IT IS A LOOKUP, NOT AN OPERATOR.**
O'Reilly & Busby 2001/2002 ("Generalizable relational binding from coarse-coded distributed
representations", NIPS) and O'Reilly, Ranganath & Russin 2022 ("The structure of systematicity in
the brain", *Curr Dir Psychol Sci* 31:124): posterior cortex binds using **coarse-coded, low-order
CONJUNCTIONS** -- units with broad tuning through a high-dimensional conjunction space, slowly
acquired over experience. The classic objections to conjunctive coding are combinatorial
inefficiency and failure to generalise; O'Reilly's response is that COARSE coding buys considerable
generalisation to novel inputs.
**We own this account's organ: `hdlab/perirhinal_conjunctive.py`. It lost, CI-separated below flat.
But it lost with an operator we chose with no computational justification -- which is the owner's
exact charge, arriving from the rival theory's side.**

**(c) THE THIRD RIVAL IS BINDING BY SYNCHRONY, AND ITS ARGUMENT AGAINST US IS PRECISE.**
von der Malsburg; Singer; Hummel & Holyoak's LISA. **Hummel's objection is not vague: synchrony lets
you represent a ROLE INDEPENDENTLY OF ITS FILLER; conjunctive coding does not** -- and role-filler
independence is exactly what systematic relational generalisation requires. (This objection lands on
conjunctive coding, not on VSA, which DOES have role-filler independence -- a point in VSA's favour
that should be recorded.) The counter-critique of synchrony is equally strong: Shadlen & Movshon
1999 *Neuron* "Synchrony unbound"; Ray & Maunsell 2010 *PLoS Biol* showing gamma frequency varies
with stimulus contrast and therefore cannot serve as a stable binding tag.

> **ALL THREE candidate brain binding mechanisms -- algebraic, conjunctive, synchronous -- have
> live published objections. THE BINDING PROBLEM IS OPEN. We have been building as if VSA won.**

**(d) THE CLEANUP-MEMORY OBJECTION, AND IT IS THE ONE THAT SHOULD WORRY US MOST.**
In HRR/VSA, unbinding returns a **NOISY** vector that is useless until cleaned up against an item
memory. Plate says so himself: *"the noisy reconstructions extracted from convolution memories can
be cleaned up by using a separate associative memory that has good reconstructive properties."*
**Therefore a VSA system's actual capability is set by its CLEANUP MEMORY -- an auto-associative
network -- and not by the algebra. The algebra is a compression scheme; the intelligence is in the
cleanup.**

**AND WE HAVE MEASURED OUR CLEANUP TO BE INERT, FIVE TIMES, WITHOUT DRAWING THIS CONCLUSION:**

```
exp_hub_spoke_word_g3_cleanup_rescore_v1   reading through cleanup changed the vector by 1.192e-07
exp_att1_iterative_attractor_cleanup_v1    lift +0.005, basin 1.00x
exp_cleanup_graded_attractor_vs_argmax_v1  +0.003
exp_att1_..._krotov_v1                     HARD_FAIL -0.020
ca3_completion partial cue                 cosine to target +39% relative, argmax recovery 0.0711 -> 0.0709
```

**On the critics' reading, that is a VSA with the load-bearing half missing.** This is a re-reading
of five banked nulls, and it is worth more than the criticism that produced it. It also reframes
them: those cells were scored as "does completion help the task", and the theory says the right
question is "does the cleanup memory recover the un-bound item", which is the completer's own
known-answer axis. **The one cell that measured that axis found the completer moves the state toward
the target in cosine WITHOUT changing which pattern is nearest. In VSA terms, that is a cleanup
memory that cannot clean up.** That is a component-level diagnosis we did not have.

**(e) THE CAPACITY OBJECTION, and the theory PREDICTED our largest measured lever.**
Superposition capacity in VSA is roughly `O(d / log d)` items at fixed retrieval fidelity
(Frady, Kleyko & Sommer 2018; Thomas, Dasgupta & Rosing 2021 "Theoretical foundations of
hyperdimensional computing"; the capacity analysis line arXiv 2301.10352). **Our live path holds
2,377 concepts at d=256.** That is outside the regime where the algebra is supposed to work at all.
`ORGAN_MAP` B4 measured that 16x the dimensionality buys **+0.0843, more than any mechanism change
this programme has produced**, and crosstalk falling exactly as `1/sqrt(d)`. **The theory told us
that in advance and we found it by sweeping.**

**(f) "IT IS A DESCRIPTION, NOT AN EXPLANATION."** Any distributed code can be written post hoc as a
bundle of bound pairs; that a representation CAN be described as a VSA does not mean the system
COMPUTES with binding. This is structurally the same objection as the free-energy tautology charge.
**No experiment has falsified VSA as a brain theory -- because none has been designed. UNFALSIFIED
IS NOT CONFIRMED, and we should stop treating the absence of a refutation as support.**

**(g) THE `sign()` PROBLEM IS OURS, NOT VSA'S.** Binary spatter codes (Kanerva 1996) are a
legitimate VSA family, but the capacity and fidelity theory for binary codes is well known and worse
than real- or complex-valued HRR at equal `d`. Our 34 `sign()` call sites across 12 modules are a
design choice INSIDE VSA whose cost the theory would have quoted us. Separately, the empirical
comparison literature has a relevant result we have never used: **random PERMUTATION outperformed
circular CONVOLUTION on the number of paired associates reliably stored in a single trace**
(Kelly, Mewhort & West 2015, *Comput Intell Neurosci*) -- and `hdlab/random_indexing.py:219` already
implements the order-sensitive permutation variant and the live path does not use it.

### 7c. THE HONEST BALANCE -- because overcorrecting here would be its own failure

VSA has real biological anchors (fly random projection; grid modular codes; gain fields), one strong
neural-implementation existence proof (Spaun), the only clean answer to Jackendoff's challenges that
does not require synchrony, and a genuine advantage over the leading rival (role-filler
independence, which conjunctive coding lacks).

**THE VERDICT IS NOT "VSA IS WRONG". IT IS:**
1. VSA is an **UNPINNED-IN-THE-BRAIN** choice that we have treated as pinned. Under R13 and the
   fidelity gate, presenting invention as pinned emits no score at all -- **and by that standard our
   whole representational substrate has been mislabelled.**
2. Its capability rests on a **CLEANUP MEMORY we have measured to be inert**, and we scored those
   cells on the wrong axis.
3. Its **CAPACITY THEORY says our `d` is too small**, and our largest measured lever confirms it.
4. There are **TWO named rivals with published support**, one of whose organs we own and shelved.

All four are actionable. None of them is "abandon the substrate".

---

## 8. WORD LEARNING AND LEXICAL ACCESS AS COMPUTATION -- and BOARD Q8

### 8a. THE STANDARD MODEL

Two-stage lexical access: CONCEPT -> LEMMA (semantic + syntactic, no phonology) -> WORD FORM
(Levelt, Roelofs & Meyer 1999 WEAVER++; Dell 1986 interactive activation). Selection at the lemma
level is a competitive normalisation -- a Luce ratio / softmax over activations, not an argmax over
a fixed list. **Dissociated by anomia** (Badecker, Miozzo & Zanuttini 1995: preserved grammatical
gender with no phonological access). **PINNED-BY-EVIDENCE as a two-stage architecture.**

**SERIAL SEARCH versus PARALLEL ACTIVATION, and it is settled enough to state.** Forster 1976's
autonomous serial search versus the parallel family (Morton's logogen, McClelland & Rumelhart's
interactive activation, Marslen-Wilson's cohort, Norris's Shortlist B). **The field has settled on
PARALLEL ACTIVATION WITH COMPETITIVE SELECTION**, on the evidence of near-simultaneous
electrophysiological indexes of lexical, semantic and contextual processing at 100-250 ms.
**Serial scanning of a lexicon is refuted.**

**CONTESTED within the parallel family:** DISCRETE-serial (activation reaches phonology only for
the SELECTED lemma) versus CASCADED (activation flows to phonology for non-selected lemmas too).
This is a live dispute and it matters to us -- see 8c.

### 8b. HOW THAT RECONCILES WITH THE OWNER'S Q8, and the reconciliation IS the design

The owner's Q8 answer: *"wrong candidates definitely come up and get rejected. It's often
iterative... I often have a sense of what the first letter is."*

**There is no contradiction, and the resolution is precise:**
1. **Parallel activation is what happens in the first ~250 ms and it is NOT INTROSPECTABLE.** When
   it succeeds, nothing is experienced but the word arriving.
2. **The iterative propose-and-reject the owner describes is what happens WHEN THE FAST PARALLEL
   PROCESS FAILS** -- i.e. in the tip-of-the-tongue state. And there IS a literature on exactly
   that regime.
3. **The TRANSMISSION DEFICIT model** (Burke & MacKay 1991): in TOT the semantic/lemma node is
   FULLY activated and the deficit is in the SEMANTIC -> PHONOLOGICAL transmission, from weakened
   connections (infrequent use, non-recent use, ageing). Phonological priming reduces TOTs by
   strengthening the LINK. **PINNED-BY-EVIDENCE.**
4. **The BLOCKING / interloper account** (Jones & Langford 1987; the "persistent alternates"
   tradition): wrong candidates DO surface, and they are PHONOLOGICALLY related to the target far
   above chance. **CONTESTED against transmission-deficit -- whether interlopers CAUSE the block or
   are a symptom of it is unresolved, and the field currently leans toward symptom.**
5. **"I often have a sense of what the first letter is" is the founding measurement of the whole
   field.** Brown & McNeill 1966 (*JVLVB* 5:325, "The 'tip of the tongue' phenomenon") measured
   exactly that: in TOT, first letter and syllable count are recalled above chance while the whole
   form is unavailable. **The owner independently reproduced a 1966 result. PINNED.**

### 8c. THE ALGORITHM Q8 IMPLIES, WRITTEN AS A SPEC

```
GENERATE   candidates by parallel activation from the semantic/lemma level (NOT a serial scan)
RANK       by activation
TEST       each against a criterion that is NOT the generator
REJECT     and re-propose
STOP       on a VALUE criterion, not on exhaustion
```

**That is GENERATE-AND-TEST WITH A SEPARATE VERIFIER**, and it is the same structure the word-
LEARNING literature independently supports: **PROPOSE-BUT-VERIFY** (Medina et al. 2011 *PNAS*;
Trueswell et al. 2013 *Cogn Psychol*) -- a learner commits to ONE hypothesis and at the next
informative encounter confirms or abandons it, with no partial credit to alternatives.
**Two literatures, one about retrieving a known word and one about learning a new one, specify the
same control structure.** That is the strongest convergence in this drill after item 5.

**THE CRITICAL PROPERTY: THE VERIFIER MUST NOT BE THE GENERATOR.** If the test is the same function
as the proposal, the loop cannot fail informatively -- the top-ranked candidate always passes.
**`canonicalize_fast` is `argmax` over cosine: a generator with no verifier and no reject step.**
That is a precisely named missing organ, and `LONG_TERM_PLAN` currently files "selection" as the
failing component without naming WHAT is missing from it. **This is what is missing from it.**

### 8d. WHAT THE OWNER SAID THE VERIFIER CHECKS, and why it converges with a separate drill

Q10, verbatim: *"I either know what it means and it doesn't match, or it doesn't feel right...
I think I'm trying to match it to the feeling of the word... 'think' versus 'contemplate' have very
different feelings - one is informal one is more thoughtful and purposeful."*

**The owner is describing register and affective connotation as the REJECTION CRITERION.**
And the target-space drill measured, independently and on a different question, that adding the
AFFECT channel (Warriner valence/arousal/dominance, on disk, unused) lifts the hand-rated ceiling
**+0.1013 [+0.0615,+0.1419] CI-separated** overall and **+0.1228 on verbs**, while an equal-size
widening with rater-SD columns buys nothing.

**Two independent lines now point at the same missing channel: a ceiling diagnostic, and the
owner's own account of how rejection works.** Neither knew about the other. I regard that as the
strongest triangulation available in the current evidence and it should raise the priority of the
affect channel above where the target-space drill left it -- **not as a wider target space, but as
the VERIFIER'S FEATURE.** That is a different build with a different test.

### 8e. Q12 -- the STOPPING RULE, and we own the organ

Q12: *"I'll give up basically because it's not worth it - I'll use a word that means the same thing
instead... if I stop thinking about it, often it will come to me later."*

- "not worth it" is a **VALUE-BASED stopping rule**, formally the marginal-value theorem
  (Charnov 1976): leave the patch when the instantaneous return rate falls to the environment's
  average. **We own `hdlab/information_foraging.py` -- 807 lines, Charnov/Constantino-Daw/Hayden/
  Wittmann cited in-module, `ForagingController` + `RhoTracker` + `DepletionEstimator` +
  `oracle_mvt_optimum` -- and it is NOT PIPELINE REACHABLE.** The organ for Q12's stopping rule
  exists, is unwired, and nobody has connected it to retrieval.
- "it comes to me later" is INCUBATION / delayed TOT resolution, consistent with continued
  sub-threshold spreading activation after the explicit search stops. **UNPINNED as a mechanism**;
  the phenomenon is well attested.

---

# PART B -- WHAT EACH THEORY WOULD HAVE TOLD US TO BUILD, VERSUS WHAT WE BUILT

**This table is the build backlog.** Ordered by how load-bearing the divergence is, not by cost.

| # | theory | what it would have told us to build | what we actually built | divergence, named precisely |
|---|---|---|---|---|
| B1 | **VSA's own theory (7d)** | a CLEANUP MEMORY that recovers the un-bound item, because the algebra's output is noise without it | a cleanup that changes the vector by 1.192e-07 and never changes an argmax | **the load-bearing half of our own framework is present in name and inert in fact**, and five cells scored it on the downstream task instead of on its own recovery axis |
| B2 | **VSA capacity `O(d/log d)` (7e)** | `d` sized to the item count | d=256 for 2,377 concepts | **outside the regime where the algebra works**; confirmed by 16x d buying +0.0843 |
| B3 | **Predictive coding + Medina census (5c)** | `delta ~ precision * (observed - predicted)`; an informative-encounter selector | `self._sums[lemma] += ctx_vec`, every occurrence weighted 1 | **no surprise weighting anywhere**; two independent literatures, one instruction, zero implementation |
| B4 | **Hippocampal indexing + sparse-coding objectives (1a, 3b)** | a SPARSE KEY addressing a DENSE GRADED VALUE, returned by link, never reconstructed | one flat store asked to be both key and value, scored by cosine in one space | **LINK-NOT-RECONSTRUCT, designed 2026-07-04, never implemented**; and we sparsified the VALUE, which theory says is the wrong object |
| B5 | **Separation/completion regime switch (2b)** | different pathways and gains at WRITE and at READ, neuromodulated | one path, one operating point for both | **no regime switch at all** |
| B6 | **Treves & Rolls two-input argument (2c)** | a LEARNED heteroassociative map from a DENSE cue space into a SPARSE store space | raw cosine between cue and store in one space | **no cue-to-store translator exists in 147 `hdlab` modules** (enumerated); and we spent a cell moving the cue AWAY from the theory's prescription |
| B7 | **Hub-and-spoke objective (6a)** | a CROSS-MODAL RECONSTRUCTOR; the similarity space emerges | a hand-authored similarity dictionary over ~230 concepts | **we built the output shape of a process we never ran** |
| B8 | **Hub completion loop (6b)** | a BACK-PROJECTION from hub to spokes; backward connections are the stronger ones | feedforward sum, no return path | **the hub's core operation per Jackson 2021 is completion back onto spokes, and we have no return path** |
| B9 | **Lexical access / propose-but-verify (8c)** | GENERATE -> TEST with a VERIFIER THAT IS NOT THE GENERATOR -> REJECT -> re-propose -> STOP on value | `argmax` over cosine | **no verifier, no reject step, no stopping rule** -- and the stopping-rule organ exists unwired (`information_foraging`) |
| B10 | **CLS slow-system objective (4d)** | extract the LATENT STRUCTURE shared across episodes (error-driven in every implemented model) | a first-order co-occurrence sum | **0.46% synonym purity in the top-20 neighbours** is the measured consequence. CONTESTED whether error-driven is required |
| B11 | **Relational memory (1c)** | store EDGES; be answerable about pairs never co-observed | per-word vectors; edges in a separate `.pkl` | **the store cannot represent the object the theory says is primary** |
| B12 | **Successor representation (1d)** | a discounted-future occupancy matrix `M = (I - gamma P)^-1` | first-order co-occurrence | **MISSING organ (`ORGAN_MAP` D7); we measured its signature twice without building it** |
| B13 | **Dual-hub metric incompatibility (6c)** | taxonomic and thematic are DIFFERENT relations; one cosine cannot express both | one space, one cosine | **the thematic channel is being poured into a space its own authors document as not representing thematic structure** |

**Sequencing note.** B1, B4 and B9 are the three that change what the system IS rather than how well
a component scores, and B4 is the one two independent literatures converge on. B2 is arithmetic and
should simply be fixed. B3 is the cheapest with real theory support behind it.

---

# PART C -- COMPONENTS WITH NO THEORETICAL JUSTIFICATION AT ALL

**The brief calls this the more damning finding and it is right.** Part B lists places where theory
and implementation DIVERGE. This lists places where **no computational theory in any of the eight
items above proposes what we did**, so there is nothing to diverge FROM.

| component | where | what theory says about it |
|---|---|---|
| **the exhaustive cosine argmax read-out** | `reading_grounding_loop.canonicalize_fast:770`; `concept_encoder:564` | **NOTHING. There is no neural analogue of an exhaustive cosine argmax over 5,491 stored items, and none of the eight theories proposes one.** The partial-cue drill already flagged it as `structure: NONE`. **It is the decision variable of the entire substrate.** |
| **`sign()` as the terminal operation, 34 sites in 12 modules** | enumerated in `ORGAN_MAP` section 1 | no theory proposes it. VSA's binary-spatter family PERMITS it and its own capacity theory PENALISES it. It is mathematically a prototype extractor, which is the signature of a DEGRADING hub |
| **`d = 256`** | `grounding_acquisition_loop.py:79` | chosen by nothing. VSA capacity theory says `O(d/log d)`; 2,377 concepts at 256 is out of regime |
| **`GROUNDED_CAP = 0.45`** | `grounded_similarity.py` | a hard cap that structurally prevents the grounded channel from ever crossing the 0.50 link threshold. No theory. Its measured effect is that 76.2% of SimLex pairs collapse onto two values |
| **`SENSE_MATCH_THRESH = 0.45`** | banked-fact acceptance | no derivation. 55.5% of banked facts beat "nothing matched" by less than 0.05 |
| **`VOTE_MARGIN = 0.15`** | `wordnet_polarity_propagation.py` | no derivation, and the module ABSTAINS on its own docstring's motivating example at margin 0.0141 |
| **unweighted shared-feature overlap** | `lexical_similarity.py` | worse than unjustified -- it is the **precise inverse** of the distinctiveness weighting the Conceptual Structure Account predicts (Tyler & Moss) |
| **equal weighting of every occurrence** | `ConceptSpace.observe` | two literatures say weight by surprise (item 5c). Nothing says weight by 1 |
| **the conjunction operator** | `perirhinal_conjunctive.py` | the owner's own example. `ORGAN_MAP` already marks the algebraic form OURS/UNPINNED; the literature does not fix one, and the rival account (7b) says it is a learned lookup, not an operator at all |
| **`alpha = 0.5` labelled "brain-canonical"** | `iterative_attractor.py` | **an invention wearing a pinned label, and it shipped.** Already caught by the fidelity honesty gate; recorded here because it is the archetype of this whole list |

**THE PATTERN.** Every entry is a place where a NUMBER or an OPERATOR was chosen once, by
convenience, and then became load-bearing without anyone asking what computes it. The read-out is
the worst case because it is universal: **every arm this programme has ever scored was scored
through an operation with no theoretical justification of any kind.** That does not invalidate the
comparisons between arms -- they share the operation -- but it means the LEVEL of every number we
have is set by a component nobody chose deliberately.

---

# PART D -- THE OWNER'S DEEPER QUESTION: DOES BRAIN FIDELITY PREDICT PERFORMANCE?

**The owner's position:** fidelity might predict performance up to a point, because the brain is the
only existence proof of this efficiency. **Our score is UNVALIDATED as a predictor -- 6 points, 1
positive, p ~ 0.17 -- but that is a narrow, LOW fidelity range, exactly where a real relationship
would be hardest to detect.**

**This deserves a real answer, and there is a directly relevant empirical literature that neither
the plan nor any drill has cited. It says: YES AT LOW FIDELITY, NO AT HIGH FIDELITY.**

### D1. THE EVIDENCE FOR

**Yamins & DiCarlo (2014 *PNAS* 111:8619; 2016 *Nat Neurosci* 19:356) and the Brain-Score
programme (Schrimpf et al.)** measured, across many models, the relationship between task
performance and NEURAL PREDICTIVITY -- how well a model's internal representations predict
recorded responses in IT cortex. **Over a wide range the two were POSITIVELY correlated:** models
that did object recognition better also predicted the brain better. Schrimpf et al. 2021 *PNAS*
found the same shape for LANGUAGE models predicting human neural and behavioural language data.

**That is the strongest published support for the owner's intuition, it is quantitative, and it
replicates across two modalities.** Note the causal direction in those papers runs the other way
(performance -> predictivity), but it is the same correlation, and a correlation constrains both
readings.

### D2. THE EVIDENCE AGAINST, and it is recent

- **Linsley, Feng, Serre et al. 2023, "Performance-optimized deep neural networks are evolving into
  worse models of inferotemporal visual cortex"** (arXiv 2306.03779): DNN neural predictivity is
  **progressively WORSENING** as models improve on ImageNet. The correlation held, then broke, then
  inverted.
- **Nonaka, Majima, Aoki & Kamitani 2021 *iScience*, brain hierarchy score:** across 29 pretrained
  DNNs, brain-likeness was **NEGATIVELY correlated** with image-recognition performance.

**So "fidelity predicts performance" is an empirically SCOPED claim, not a law. It has a measured
breaking point.**

### D3. THE ASYMMETRY, AND IT IS WHAT MAKES THE OWNER RIGHT IN OUR CASE

**Both of those literatures measure fidelity ABOVE A HIGH PERFORMANCE BASELINE.** Every model in
Brain-Score already does the task well. **The break happens at the TOP of the fidelity range, among
models that all work.** In the same datasets, at the BOTTOM of the range, the relationship is steep
and positive -- a model with no hierarchy at all predicts nothing and does nothing.

**We are at the bottom.** Our scored components read 0%, 25%, 50%, 62% blind. Our 0% component is
the sha256 hash encoder and it is **the structure-axis null by construction** -- 0% fidelity and
0 capability is not a coincidence, it is the relationship's left endpoint.

**So the published evidence is consistent with a shape the owner has essentially described:
strongly positive at low fidelity, saturating, then inverting.** The owner's "up to a point" is the
literature's finding, arrived at independently.

### D4. WHY THE THEORY PREDICTS EXACTLY THAT SHAPE

The brain's solution is ONE point in a large space of solutions to the same problem.
- **Below a threshold you are not solving the problem at all.** Our null encoder is the proof.
- **Above it there are many solutions, and the brain's is optimised under constraints we do not
  share:** a metabolic budget, a wiring volume, a development time, and evolutionary path
  dependence. **Copying a parameter whose justification is a constraint we do not have should be
  expected to hurt.**

**And this drill produced the cleanest possible example of that.** Item 3: the brain's 0.2% MTL
active fraction is optimal under a METABOLIC objective and a CAPACITY objective. We have no
metabolic budget, and we were measuring SIMILARITY. **The pinned brain parameter was the worst
setting in our sweep, monotonically.** That is not a failure of brain fidelity. It is fidelity
applied to a parameter instead of to a computation.

### D5. IS THERE A LEVEL BELOW WHICH THE RELATIONSHIP IS UNDETECTABLE? YES, AND IT IS A POWER
STATEMENT, NOT AN EVIDENCE STATEMENT

**Six points with exactly ONE positive-class member cannot produce a p-value below `1/6 = 0.167`
under a random-ranking null, no matter how good the score is.** Any monotone score that ranks the
single positive first achieves exactly that. **`p ~ 0.17` is therefore the CEILING of the design,
not a measurement of the score.**

**"UNVALIDATED" is a statement about our experimental design, and it is the same fault the
target-space drill flagged for the verb sub-stratum: an underpowered primary is how a real effect
gets banked as a null.** The plan already says this correctly and it is worth repeating: *"Six
points with exactly one positive-class member cannot support a separation claim."*

**THE RIGHT TEST IS ALREADY NAMED IN `PLAN.md` AND HAS NOT BEEN RUN.** `ORGAN_MAP` carries an
INDEPENDENT fidelity classification for **38 organs** (SAME / RIGHT-OP-WRONG-METRIC /
RIGHT-OP-WRONG-PLACE / WRONG-OP / MISSING), produced by a different pass on different evidence
before the scoring scheme existed. Concordance against those 38 labels is a real test with real `n`.
**The blocker is that most of the 38 carry no floored result -- which is itself the finding, and it
means the fidelity-predictor question is BLOCKED ON THE SAME EVIDENCE GAP as everything else.**

The pre-registered forward test on the books is the right shape and should be protected: **any
future component scoring 0 on D3 (regime) or D5 (pairing) fails its floor.** Note that item 3 of
this drill supplies a mechanism for why D3 in particular would predict failure -- a regime mismatch
means you are optimising a different objective from the one being scored.

### D6. MY ANSWER TO THE OWNER, DEFLATED, AND ONE REFINEMENT I THINK IS THE REAL POINT

**The claim is SUPPORTED by the strongest directly-relevant literature (Brain-Score correlations
across vision and language), BOUNDED by that same literature (the correlation inverts at the top),
and UNTESTED in our system for reasons of statistical POWER rather than reasons of evidence.**

Calibrated, standing penalty applied:
- P(a properly-powered ~38-organ concordance test finds a positive fidelity-outcome relationship)
  **~ 0.55**
- P(the relationship is monotone all the way up) **~ 0.20**
- P(the D3/D5-zero forward test survives its next five components) **~ 0.45**

**THE REFINEMENT, and I think it is worth more than the yes/no.** The literature and this drill
together suggest the predictor is not fidelity-in-general but **fidelity OF THE COMPUTATION, not
fidelity OF THE PARAMETERS.**

- Brain **PARAMETERS** -- 0.2% sparsity, 7 gamma cycles per theta, a 5-hour tagging window, a
  particular expansion ratio -- are derived from constraints we do not share. **Treat every one as a
  HYPOTHESIS TO SWEEP, never a value to adopt.**
- Brain **COMPUTATIONS** -- separation before completion, a dense cue addressing a sparse store
  through a learned map, an error-driven residual as the learning signal, generate-and-test with a
  separate verifier, two systems because one set of weights cannot serve both timescales -- are
  derived from **the problem, which we DO share.** Those are the ones to copy exactly.

**The evidence in our own table is consistent with this and nobody has read it this way.** Our one
100%-fidelity component (hub-and-spoke role addressing) copied a STRUCTURE and held under partial
cue but did not beat the flat bag. Our most explicit parameter copy (MTL 0.2%) was the worst point
in its sweep. **The components that have most clearly hurt us are the ones where we copied a number;
the components that have most clearly helped are the ones where we copied an operation.**

**STATUS: this is MY STRATEGIC READ, a hypothesis pending VET, not a measured verdict.** It is
testable: score the 38 organs' divergences as PARAMETER-divergence versus COMPUTATION-divergence and
check which class predicts the floored outcome. That is a re-analysis of evidence we already own and
it needs no new run.

---

# PART E -- WHAT I COULD NOT VERIFY

- **The citations in Part A were retrieved this pass and are POINTERS TO CHECK, not a replication
  audit.** Per the `ORGAN_MAP` provenance rule, treat each as needing verification before it becomes
  load-bearing. Specifically un-re-verified this pass: the exact Levy & Baxter optimal-sparsity
  range; the Brown & McNeill first-letter accuracy figures; the Kelly/Mewhort permutation-versus-
  convolution result (I have the abstract's claim, not the numbers); the Nonaka brain-hierarchy
  correlation coefficient.
- **Whether O'Reilly's coarse-coded conjunctive account and our `perirhinal_conjunctive.py`
  implement the same thing.** I did not read the module this pass. The claim "we own this account's
  organ" is a NAME-level claim and needs a runtime check before it is acted on.
- **Whether the substrate's replay/consolidation path is error-driven anywhere.** I did not
  enumerate `hdlab/` for error-driven objectives this pass; the partial-cue drill's enumeration
  found exactly three modules with gradient machinery, none of them in the consolidation path, and
  I am relying on that rather than re-running it.
- **The successor-representation reading of the thematic-consolidation win (1e).** This is a
  strategic read over a measured number I did not recompute. It is a hypothesis, and the number
  0.0462 -> 0.1069 is quoted from `STATUS.md` / `LONG_TERM_PLAN`, not re-derived.
- **A full `experiments/` and `preregs/` keyword sweep.** Bash `grep` over `notes/` timed out at 2
  minutes and was replaced with scoped ripgrep on `notes/` only. **My dedup coverage is `notes/`
  plus the substrate KB. It is NOT a full sweep of `experiments/` or `preregs/`.** Stated because an
  absence claim requires an enumeration and mine is partial, and because two of the four ripgrep
  probes hit the 60-file display limit, so those counts are lower bounds.
- **Whether a surprise-weighted accumulator is implementable without a bootstrapping problem.**
  Flagged in 5c as a real design risk. Not resolved.
- **The exact tie between the cortical "sparseness index 0.2-0.3" and an active fraction.** I assert
  they are different quantities and `ORGAN_MAP` B4 agrees, but I did not re-derive the Treves-Rolls
  sparseness definition from source this pass.

---

# PART F -- PINNED / CONTESTED / UNPINNED, the full ledger for this drill

**PINNED-BY-EVIDENCE**
- Hippocampal indexing as an architecture; the hippocampus stores pointers, not content.
- CA3 capacity theory `p ~ C/(a ln(1/a))`; sparser stores more.
- The separation/completion inequalities as MEASURED quantities (Neunuebel & Knierim 2014).
- Encoding versus retrieval as distinct DYNAMICAL REGIMES with a neuromodulatory switch.
- The two-input argument: the retrieval cue is dense, numerically large, weak per synapse, and
  associatively modified.
- Sparse coding's metabolic constraint (Attwell & Laughlin; Lennie) as a CONSTRAINT.
- The CLS dilemma: one weight set cannot serve one-shot and slow-statistical learning; interference
  scales with representational overlap.
- The N400 as lexico-semantic prediction error, with an implemented model.
- The ATL hub computes nonlinear cross-modal mappings expressing DEEP similarity; backward
  connections stronger than forward.
- Two-stage lexical access, dissociated by anomia; parallel activation with competitive selection;
  serial lexicon scanning refuted.
- TOT as a transmission deficit with above-chance partial phonological access (first letter,
  syllable count).
- Propose-but-verify as the supported word-learning mechanism; ~90% of exposures uninformative.
- The successor representation as a representational SIGNATURE in hippocampus and V1.

**CONTESTED -- competing accounts named, no winner picked**
- What the hippocampus computes: index vs conjunctive store vs relational map vs predictive map.
- Whether CA3 is a discrete attractor or a continuous manifold (Leutgeb 2007 vs Treves & Rolls).
- Whether sparse coding is the right account of cortical coding at all (Spanne & Jorntell 2015).
- Whether the cortical slow system's objective must be error-driven or can be Hebbian.
- Whether consolidation replays real or generative samples.
- Whether the thematic system is a second STORE or a different CONTROL SETTING over one store.
- **How the brain binds: algebraic (VSA) vs coarse-coded conjunctive (O'Reilly) vs synchrony
  (Hummel). ALL THREE HAVE LIVE OBJECTIONS. THIS IS THE ONE WE HAVE BEEN TREATING AS SETTLED.**
- Discrete-serial vs cascaded activation to phonology.
- Whether TOT interlopers cause or merely accompany the block.
- The free energy principle's status as science versus as a formal identity.

**UNPINNED -- ours to choose and test, and labelling them as pinned is barred**
- The hippocampal index ALLOCATION rule.
- The CA3 update rule.
- The learning rule for the successor representation in hippocampus.
- The optimal active fraction for a SIMILARITY objective (all four published optima are for other
  objectives).
- The interleaving ratio in consolidation.
- The hub-spoke combination rule.
- The gain function in semantic control.
- **The binding operator. This is the substrate's core operation and the literature does not fix
  it.**

**SHELVE / REVIVE, brain-framed**
- **DO NOT SHELVE the cleanup memory.** It has never been tested on its own recovery axis with a
  code the theory says it can clean. Its five standing nulls were scored downstream.
- **DO NOT SHELVE `perirhinal_conjunctive`.** It is the rival theory's organ and it lost with an
  operator chosen by convenience. Revive when a computationally justified conjunction operator
  exists -- not when the score improves.
- **SHELVE "sparsify the meaning value".** Brain-framed reason: separation is the destruction of
  similarity, and we measured a monotone curve confirming it. Revive only if the value is being used
  as an ADDRESS rather than as a similarity carrier.
- **SHELVE "make the cue lower-rank."** Brain-framed reason: the theory says the cue should be
  DENSER than the store. Already shelved by the partial-cue drill on the same grounds; this drill
  supplies the quantitative argument (Treves & Rolls 1992).

---

## G. DISCLOSURE

**No tool call in this session was denied at any point.** Two Bash calls exceeded the 2-minute
timeout and were moved to background by the harness (a `director_kb_query.py` run, which completed
and whose output is quoted in section 0.1; and a repo-wide `grep -ril` over `notes/`, whose output I
did not use -- it was replaced by scoped ripgrep, and the consequence for my dedup coverage is
stated in Part E). Neither was a denial and neither was retried as a variant to hide it.

No deletion token was issued, alone or bundled with work. No `git add -A`. No origin push. No
commit. No subagent spawned. No LLM in any path. No experiment authored, smoked or dispatched.

**Protected paths: READ ONLY, none written.** `data/foundation/**` never opened. `CLAUDE.md`,
`preregs/**`, `notes/PLAN.md`, `notes/LONG_TERM_PLAN.md`, `notes/BOARD.md`,
`data/capability_registry.jsonl`, `tools/**`, `experiments/**`, `hdlab/**` were read and not
modified.

**Live runs 18496 / 30812 / 22984 were never signalled, never polled, and none of their output
directories was written to.**

**Files written by this drill:** `.claude/scan-out/computational-theory-drill.json` and this note.
Nothing else.
