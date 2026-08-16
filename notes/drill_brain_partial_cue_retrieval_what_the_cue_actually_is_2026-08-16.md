# DRILL -- how the brain retrieves from a degraded cue, and what the cue actually IS

Date: 2026-08-16. Type: BIOLOGY DRILL FIRST, then map-to-us, then a deciding-experiment spec.
No experiment cell was authored or run. No subagents spawned. No LLM in any path.

Standing frame that governs every line below (LONG_TERM_PLAN sec 8, owner directive): the owner
described their own memory doing this, so the capability is DEMONSTRATED. Nothing here concludes
that partial-cue retrieval is intrinsically limited. Every conclusion is about WHICH MECHANISM the
brain uses and how faithfully we could rebuild it.

Calibration: the standing lit-scan penalty is applied throughout (P deflated 0.15-0.25;
novel-synthesis P capped at 0.50).

---

## 0. DEDUP AGAINST PRIOR WORK (run first)

`.venv/Scripts/python.exe tools/director_kb_query.py --k 8 --tau 0.15 --chunk-content "entorhinal
cortex input to hippocampus pattern completion partial cue CA3 recall"` -> confidence 0.4297.

Top hits: `ca3_completion_partial_cue_v1` metrics (0.4297, verdict PAIRING_HYPOTHESIS_REFUTED);
`notes/research_drill_cross_domain_new_mechanism_5x_2026-06-10.md` "B7. Hippocampal pattern
completion" (0.3711); the bare NeuroLex `ENTORHINAL_CORTEX` node with a single edge
`PROJECTS_TO->DENTATE_GYRUS` (0.3486); and
`notes/research_drill_biological_distributed_coordination_2x_2026-06-07.md` chunk028 (0.3438),
which says "DG separates, CA3 completes, replay consolidates".

Because a KB miss is weak evidence, I ALSO enumerated the notes directory directly:
`grep -ril entorhinal notes/` returns **21 files**, and I read the two most likely to overlap.

**PRIOR WORK THAT EXISTS AND IS CREDITED, NOT RE-DERIVED:**

- `notes/research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md` lines 32-33
  already carries the DG ~10x expansion, the sparse "detonator" mossy-fibre synapses, CA3 as a
  genuine autoassociative attractor, and the proximal-vs-distal CA3 separation/completion gradient.
  **That is the substrate's existing baseline and this drill builds on it.**
- `notes/wave14d_icl_via_pool_research.md:437` cites Treves & Rolls 1992 by name -- but as a bare
  reference link supporting a CAPACITY figure (CA3 ~10^4-10^5 patterns), not for what that paper
  actually argues. `notes/ORGAN_MAP.md:499,1732` likewise cites Treves & Rolls for capacity, and
  1732 explicitly records the CA3 OPERATION as **UNPINNED**.

### A NOVELTY CLAIM I MADE AND THEN REFUTED WITH MY OWN GREP -- DISCLOSED, NOT QUIETLY FIXED

An earlier draft of this section asserted that "the string `perforant` appears in ZERO files under
`notes/`" and claimed five findings as new. **THAT WAS FALSE.** `grep -ril perforant notes/` returns
**10 files**. My first grep bundled `perforant` with eight other alternatives under a 30-line head
limit and the perforant hits fell off the end -- the exact "an absence claim requires an
ENUMERATION, not a search" fault, committed inside a drill that quotes the rule. Correcting it
turned out to matter more than the claim did.

**THE SUBSTRATE ALREADY KNEW MOST OF SECTIONS 1 AND 2, AND HAS SINCE 2026-07-04.**
`notes/research_regime_switch_dense_retrieval_sparse_storage_brain_grounding_2026-07-04.md` states,
verbatim:

> "**Entorhinal cortex (EC) II/III -> perforant path** carries the RETRIEVAL CUE: a DENSER,
> distributed grid/place cortical pattern. **The query that drives recall is denser than the sparse
> hippocampal trace it addresses.**" (line 23)

> "mossy-fiber DG->CA3 ('detonator', sparse) dominates ENCODING; perforant-path + CA3 recurrent
> collaterals dominate RETRIEVAL -- gated by acetylcholine ... The brain LITERALLY switches
> representational/dynamical regime between store and recall." (line 39, citing Hasselmo SPEAR and
> Treves-Rolls)

It also already carries hippocampal indexing theory, complementary learning systems, and the
key-value framing in which **keys and values are deliberately DIFFERENT representations** (keys
optimised for discrimination, values for fidelity).

**THIS IS THE SINGLE MOST IMPORTANT LINE IN THIS DRILL.** Six weeks ago this substrate wrote down
that the retrieval cue is SUPPOSED to be denser than the store it addresses. On 2026-08-16 the
`sparsify-right-object` cell measured the partial cue at PR 202.04/256 against the store's
88.74/256 and reported it as a DEFECT ("2.3x higher-rank than the thing it is querying ... why a
CA3-style attractor has almost nothing to grip"), and the `two-channel-cue` cell then spent a whole
cell successfully engineering the cue to be LOWER-rank -- **moving away from the brain, on purpose,
against a conclusion already banked in this repo** -- and measured no gain, which is what the
2026-07-04 drill predicts.

Other prior work now correctly credited rather than re-derived:
- `notes/research_working_memory_integration_upper_limit_2026-07-16.md:88` -- "Entorhinal cortex as
  a bidirectional TRANSLATION interface, not just a relay" (van Strien, Cappaert & Witter 2009).
  That is section 2's translation argument, already banked.
- Same file line 92 -- and this **CONTRADICTS my H1 below, so it is reported, not buried**: it reads
  the anatomy as a "fixed, largely non-learned perforant-path projection" and recommends treating
  the projection as FIXED, with "learned projections ... a v2 lever, not a v1 requirement."
- `notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md:48` -- the perforant path
  CONTINUOUSLY drives CA3 during completion; the cue must keep clamping the settle. **That is
  exactly the `alpha` cue-re-injection term in `hdlab/iterative_attractor`**, so that organ already
  implements this element and it is not a gap.
- `notes/research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md:32-33` -- DG
  expansion, mossy-fibre detonator synapses, CA3 attractor, proximal/distal gradient.
- `notes/ORGAN_MAP.md:1732` -- records the CA3 UPDATE RULE as explicitly **UNPINNED**, which is
  correct and which this drill does not change.

**WHAT REMAINS GENUINELY NEW after that correction, and it is less than I first claimed:**
1. The **semantic control network** (left IFG + pMTG, causally dissociable from the ATL store) as
   the neural analogue of narrowing the candidate set (sec 3) -- and the observation that it is
   driven by the GOAL, not by the cue, which is exactly what the size-matched-random-gate control
   measured.
2. **Encoding specificity** (Tulving & Thomson) and **retrieved-context theory** as the reason the
   owner's episodic step succeeded, and the observation that our held-out-sentence cue violates
   encoding specificity BY CONSTRUCTION (sec 4).
3. The **four-cue-type taxonomy** and the finding that our task poses types (c)/(d) while we
   implemented type (a) (sec 5).
4. The **two-stage lexicon / TOT transmission-deficit** mapping of the owner's own Q4 answer (sec 5).
5. The **runtime enumeration** showing no learned cue->store map exists in any of 147 `hdlab`
   modules, and that `context_retention.coarse_shortlist` is an owned, working, never-used-on-this-
   task narrowing organ (sec 6).

Caveat that stands regardless: the KB's own retrieval channel is `char_trigram_v1`, a SPELLING
channel. It did not surface the 2026-07-04 drill. A filesystem grep did. **Enumerate from disk.**

---

## 1. WHAT IS THE ACTUAL INPUT TO HIPPOCAMPAL COMPLETION?

### 1a. CA3 has TWO input systems and they have DIFFERENT JOBS [PINNED]

Treves & Rolls (1992, *Computational constraints suggest the need for two distinct input systems to
the hippocampal CA3 network*), developed in Rolls & Treves (1998) and restated in Rolls (2018, *The
storage and recall of memories in the hippocampo-cortical system*, Cell Tissue Res):

- **Mossy fibre route** (EC layer II -> dentate gyrus -> CA3). Few synapses per CA3 cell, each very
  powerful. Its sparsity forces a separated, near-orthogonal pattern to be written into CA3. **This
  is the STORAGE input.** It dominates the recurrent collaterals during encoding so that a NEW
  pattern can be laid down rather than an old one recalled.
- **Direct perforant path** (EC layer II -> CA3 directly, bypassing DG). Numerically LARGE, each
  synapse individually WEAK, and **associatively modified during storage**. **This is the RETRIEVAL
  CUE input.** Rolls' quantitative argument: to initiate retrieval you want a numerically large
  input through associatively-modified synapses, so that even a PARTIAL cue suffices; to store you
  want a small number of strong signals that can dominate the recurrence.

Corroborating lesion dissociation [PINNED]: mossy-fibre disruption impairs ENCODING of new
associations while sparing retrieval of already-stored ones; CA3-NMDA manipulations impair
completion from a degraded cue specifically (Kesner 2007 behavioural process analysis of CA3;
Nakazawa et al. line).

### 1b. What the entorhinal cortex delivers is a COMPRESSED, TYPED code, not a fragment [PINNED]

- **Lateral EC (LEC)** carries CONTENT: object/item features, the currently-present stimulus, and
  object-context associations. LEC lesions impair associative (object-in-context) recognition while
  sparing non-associative recognition.
- **Medial EC (MEC)** carries CONTEXT: spatial/contextual coding, grid modules. The grid code is
  explicitly a MODULAR code embedding a low-dimensional variable in a high-dimensional population,
  with residue-number-like properties and very large capacity (Fiete and colleagues; discretised
  grid modules, Nature 2012).
- The two are parallel input streams conveying two complementary sets of cortical inputs, integrated
  in the hippocampus into a context-specific, item-specific episodic representation.

### 1c. THE ANSWER, AND IT KILLS OUR FRAMING

**The brain's retrieval cue is NOT a subset of the stored pattern.** It is a differently-typed,
already-compressed cortical code, delivered on a DIFFERENT WIRE from the one that wrote the memory,
through a synaptic matrix that was itself learned during storage. Its function is to inject a weak
bias that the recurrent network then amplifies -- not to be compared for similarity against the
store.

**Therefore the "make our cue a fragment of the target" framing is WRONG and should be dropped.**
The two-channel-cue cell already produced the empirical half of this: it successfully built cues
that ARE fragment-shaped (participation ratio 63-108 against the store's 171, i.e. genuinely
lower-rank) and argmax recovery did not move. Its own conclusion -- "a clean fragment of the WRONG
THING is still the wrong thing" -- is right, and the biology says the target was never fragments in
the first place.

MARKED **[OURS, and it is the live suspect]**: that a raw cosine between cue and store can stand in
for the perforant-path projection. There is no neural stage that computes a similarity between the
retrieval cue and the stored items in a shared space. `sparsify-right-object.json` had already
flagged the exhaustive cosine argmax as the component with "structure: NONE".

---

## 2. DO CUE AND STORE SHARE A REPRESENTATIONAL SPACE?

**[PINNED] NO -- deliberately not, and there is a named translator.** Four independent lines:

1. **Dimensionality is deliberately mismatched at every stage.** EC layer II -> DG is a large
   EXPANSION (rat: order 2x10^5 EC layer II cells -> order 10^6 granule cells); DG -> CA3 is a
   contraction onto a sparse code. Cue space, separation space and store space are three different
   spaces with three different sparsities. Commensurability is not a design goal anywhere.
2. **The translation is LEARNED.** The direct PP->CA3 synapses are associatively modified during
   storage. So the map from EC space into CA3 space is a **learned heteroassociative matrix**, not
   an identity and not a fixed random projection.
3. **CA1 is the heteroassociative stage.** The standing computational division is CA3 =
   autoassociative, CA1 = heteroassociative: CA1 recodes CA3 output and sets up
   associatively-learned BACKPROJECTIONS to neocortex, which is how a completed hippocampal pattern
   gets turned back into a cortical one. The RETURN path is heteroassociative too.
4. **Hippocampal indexing theory** (Teyler & DiScenna 1986; Teyler & Rudy 2007; Goode et al. 2020,
   *The hippocampal engram as a memory index*): the hippocampus does not hold the CONTENT at all. It
   holds a sparse INDEX -- a set of pointers to cortically distributed feature patterns. A partial
   cue reactivates the index, and the index RESYNCHRONISES the cortical modules. Under this account
   the store and the cue are not merely in different spaces; the store is not even made of the same
   KIND of thing as the content being retrieved.

### THE CONSEQUENCE FOR US

**"Our cue has participation ratio 202/256 against the store's 88.74/256, 2.3x higher-rank" is NOT
a defect to be engineered away. It is the normal state of affairs, and what is missing is the
TRANSLATOR.** We have been trying to make the cue commensurable with the store because we have no
stage that could relate two incommensurable things. The brain never needs them commensurable.

**This conclusion is a RE-DERIVATION, and the credit belongs to
`research_regime_switch_dense_retrieval_sparse_storage_brain_grounding_2026-07-04.md`** (sec 0),
which stated it six weeks ago and went further: it named the correct fix as **LINK-NOT-RECONSTRUCT**
-- store a sparse KEY for addressing and a LINKED DENSE VALUE for read-out, address in the key
space, then RETURN the linked value; never try to reconstruct dense content out of the sparse index.
Its design implication is unimplemented. Our current read-out asks ONE flat store to be both key and
value and scores by cosine in one space, which is the configuration that drill says is fighting the
biology.

**Route-by-flavor (standing rule): this is a MISSING COMPONENT (flavor 2) with a MISSING-LEARNING
(flavor 4) candidate on top of it** -- not used-ability-wrong, and emphatically not an intrinsic
ceiling. The component is the translation/link stage. Whether that stage must be LEARNED is
genuinely open and the repo's own two drills disagree: 2026-07-16 reads the perforant projection as
fixed and largely non-learned; Rolls/Treves describe the PP->CA3 synapses as associatively modified.
**That disagreement is precisely what arm A2 exists to settle.**

---

## 3. WHAT NARROWS THE CANDIDATE SET BEFORE COMPLETION?

The measured finding this question comes from: the onset gate takes self-recovery 0.0711 -> 0.5734,
but a SIZE-MATCHED RANDOM gate does marginally BETTER (-0.0158 CI-separated). The value was POOL
SIZE, not the onset. So: is there a neural analogue of gating the search space, and what drives it?

**[PINNED] There are TWO, at different levels, and they are different objects.**

### 3a. Inside the memory circuit: inhibitory normalisation holds the live set near-constant

DG/CA3 sparseness is maintained by feedback inhibitory interneurons, and the theta-gamma nested code
processes a small, roughly FIXED number of items per theta cycle. The human hippocampus
**NORMALISES the information content of an episode against the density of sensory information** --
the same number of gamma episodes per theta cycle regardless of how rich the input is -- and this
normalisation is explained by combined fast (feedforward, ING) and slow (feedback, PING) inhibition.

**This is a NORMALISATION, and it is exactly the shape our onset gate accidentally implemented.** It
also explains why a size-matched RANDOM gate did marginally better: the brain's mechanism controls
the SIZE of the live set and does not care which items are in it. Our measurement is what this
literature predicts, not an anomaly.

### 3b. Outside the memory circuit: a dedicated SEMANTIC CONTROL NETWORK

Left inferior frontal gyrus (BA45/47) + posterior middle temporal gyrus + dorsomedial PFC. TMS to
IFG and to pMTG selectively disrupts executively-demanding semantic judgements and leaves decisions
based on strong automatic associations UNAFFECTED (Whitney et al. 2011, Cereb Cortex; the controlled
semantic cognition framework, Lambon Ralph, Jefferies, Patterson & Rogers 2017). The network is
anatomically and causally dissociable from the semantic STORE in the anterior temporal lobe.

**So the answer to "what drives the narrowing" is: THE GOAL AND THE CONTEXT, via a control network
that is separate from the store -- not the cue's content.** Our gate was built out of the cue's
content, and the control measured that the content bought nothing. That is the predicted result.

### 3c. WE ALREADY OWN A NARROWING ORGAN AND HAVE NEVER PUT IT ON THIS TASK

`hdlab/context_retention.py` -- RUNTIME-VERIFIED this session, not trusted by name
(`scratch/partial_cue_transfer/runtime_verify.json`):

- `build_coarse_projection(n_dim, d_coarse, generator) -> Tensor` -- ran, returns (1024, 64).
- `coarse_shortlist(query, k_tape, proj, k_shortlist) -> Tensor` -- ran, returns k indices.
- `coarse_to_fine_hopfield_read(query, k_tape, v_tape, beta, proj, k_shortlist)` -- present.
- `coarse_to_fine_read_cost_ratio(2000, 1024, 64, 32) = 0.0785`.

Registry reconciliation (disk FIRST, then registry, never the reverse): 2 rows, one
`WIRED_AND_PIPELINE_USED` and one `WIRED_BUT_NOT_PIPELINE_REACHABLE` -- mutually contradictory, the
known registry leak. The organ exists and runs; its registry status is not a usable single fact.

**The two-channel-cue cell built a gate from scratch instead of reusing this.** That is the
islanding failure the standing WIRE-DONT-ISLAND rule names.

---

## 4. WHY DID THE OWNER'S EPISODIC CUE SUCCEED WHERE OUR LEXICAL ONE FAILS?

Owner's Q5, verbatim: *"Since the tove ran - it must be an animal (or at least something that has
legs). Since it ran accross the road, I think of rabbits and deer which I've seen cross roads, and
so I assume it's a smallish animal."*

Three sequential operations: verb-argument constraint, then EPISODIC recall of remembered scenes,
then a distribution over categories. The middle step is retrieval from a degraded cue THAT WORKED.
Three PINNED reasons it worked:

1. **Encoding specificity (Tulving & Thomson 1973).** A retrieval cue is effective to the extent it
   RECREATES the encoding conditions. A semantically strong cue that was NOT present at encoding
   fails; a weaker cue that WAS present succeeds. The owner's cue -- an animal crossing a road --
   was literally part of the encoded episode.
   **Our held-out-sentence cue fails this condition BY CONSTRUCTION.** We store an accumulated
   co-occurrence bag over a whole corpus and probe with one held-out sentence. That sentence was
   deliberately excluded from the trace. We built a cue guaranteed not to match the encoding.
2. **Retrieved-context theory (Howard & Kahana 2002, TCM).** In episodic recall the cue IS the
   drifting CONTEXT state; items were bound to context at encoding, and event-to-context
   associations let context serve as the cue. The owner reinstated a roadside context and the items
   came back. This is CONTEXT -> ITEM, a heteroassociation -- not item-fragment -> item.
3. **Scene construction (Hassabis & Maguire; anterior hippocampus with vmPFC driving it).** The
   owner did not retrieve a word. They CONSTRUCTED A SCENE and read a category distribution off it.

**So the successful step was a different OPERATION from the one we implemented, on a store built a
different way.** Not a better version of ours.

---

## 5. 'PARTIAL CUE' IS NOT ONE THING -- IT IS FOUR RETRIEVAL PROBLEMS

| kind | example | circuit [PINNED] | correct operation |
|---|---|---|---|
| (a) degraded copy of the stored item | a smudged photo of a face | EC -> direct perforant path -> CA3 recurrent | AUTOASSOCIATIVE completion (attractor) |
| (b) different-modality pointer | the smell that names the dish | modality spokes -> ATL transmodal hub; CA1 convergence | CROSS-MODAL heteroassociation |
| (c) semantic description | "the furry one that barks" | semantic control network (IFG/pMTG) gating the ATL store | CONSTRAINT SATISFACTION over features, under goal control |
| (d) context in which it occurred | "the word from that lecture" | LEC/MEC context code -> hippocampal index -> cortical reinstatement | CONTEXT -> ITEM heteroassociation + index reinstatement |

### WHICH ONE DOES OUR TASK POSE? (c) AND (d). WE IMPLEMENTED (a).

Our "partial cue" is a held-out SENTENCE the word occurred in. That is a CONTEXT (d) carrying some
semantic-description content (c). It is measurably not a degraded copy of the stored profile:
participation ratio 202.04/256 against the store's 88.74/256, and cosine 0.1592 to the target's own
row. We then ran an AUTOASSOCIATIVE attractor over it (`hdlab/iterative_attractor`,
`hdlab/cleanup_family.iterative_attractor`, `hdlab/ca3_completer.complete_flat`), which is the
correct operator for (a) ONLY.

**The completer is not failing. It is the right organ pointed at the wrong cue type.** Every
completer result to date -- `PAIRING_HYPOTHESIS_REFUTED`, the 0.35%-of-argmaxes-move temperature
probe, the monotone accuracy loss on softening -- is consistent with running an autoassociative
operator on a cue that is not autoassociatively related to the store. Those results should NOT be
read as evidence about completion.

**And the metric conflates all four kinds into one number.** That is a real defect in the
instrument, independent of any mechanism.

### THIS ALSO REFRAMES THE TWO-CHANNEL RESULT

The owner's channel 1 (word onset) is a type-(a) FORM fragment addressed at the FORM lexicon.
Channel 2 (same-meaning words) is a type-(c) semantic description addressed at the MEANING store.
**They should never have been summed into one cue vector, because in the brain they enter DIFFERENT
STORES.** [PINNED]

- The two-stage model of lexical access separates LEMMA retrieval (semantic + grammatical, no
  phonology) from WORD-FORM retrieval, and anomia dissociates the two stages cleanly (Badecker,
  Miozzo & Zanuttini 1995: preserved grammatical gender with no phonological access).
- The tip-of-the-tongue **transmission deficit model** (Burke & MacKay 1991) states the failure
  precisely: in TOT the SEMANTIC/lemma node is fully activated and the deficit is in the
  SEMANTIC -> PHONOLOGICAL TRANSMISSION, caused by weakened connections (infrequent use, non-recent
  use, ageing). Phonological priming of related words reduces TOTs -- it strengthens the LINK.

**The owner's Q4 report is a textbook TOT: they hold the meaning, they hold partial form, and the
LINK between the two stores is what has failed.** Our architecture has one store and one space; it
cannot even represent that failure mode, which is why summing the two channels measured BELOW the
incumbent (-0.0612 CI-separated at k=3) instead of complementing it.

---

## 6. MAP TO US -- WHAT WE OWN, ENUMERATED FROM DISK THEN RECONCILED

Method per standing rule: `ls hdlab/` FIRST (**147 modules**), then SHAPE search inside them, then
reconcile to `data/capability_registry.jsonl` (200 rows). Never registry-first. Every module below
was IMPORTED at runtime and its public callables read from `inspect`, not from docstrings --
artifact `scratch/partial_cue_transfer/runtime_verify.json`, 31/31 imported OK.

| brain mechanism | do we own an organ? | evidence |
|---|---|---|
| CA3 autoassociative completion | **YES** -- `hdlab/iterative_attractor`, `hdlab/cleanup_family`, `hdlab/ca3_completer` (`complete_flat`, `complete_addressed`, plus 5 self-tests) | imported; `ca3_completer` has **0 registry rows** |
| DG pattern separation | **YES** -- `hdlab/dg_pattern_separation`, `hdlab/hippocampal_encoder.DGProjection` | imported; `dg_pattern_separation` carries 5 mutually contradictory rows |
| perirhinal conjunctive coding | **YES** -- `hdlab/perirhinal_conjunctive` (`kwta`, `pair_conjunction`, `conjunctive_context_vector_masked`) | imported; 2 rows, both `WIRED_BUT_NOT_PIPELINE_REACHABLE` |
| hub-and-spoke separately-addressed slots | **PARTIAL** -- `hdlab/hub_spoke_word` (`spoke_key`, `HubSpokeWord(role_keys=...)`) | keys are FIXED RANDOM, nothing learned |
| **narrowing / shortlist before the fine read** | **YES, and never used on this task** -- `hdlab/context_retention.coarse_shortlist` + `build_coarse_projection` + `coarse_to_fine_hopfield_read` | RAN this session; cost ratio 0.0785; 2 contradictory rows |
| drifting episodic context vector (TCM) | **PARTIAL** -- `hdlab/temporal_trace.TemporalTrace(alpha, n_dim)` is a single leaky trace, no item-to-context binding; `hdlab/situation_model_accumulate` has role registers | imported; `temporal_trace` 2 rows, both not-pipeline-reachable |
| goal-driven semantic control gate | **NO ORGAN OF THE RIGHT SHAPE.** `clarify_gate`, `refuse_gate`, `low_information_filter`, `entity_slot_gate` all gate OUTPUT or SLOTS, none constrains which region of the store may be active | imported and signatures read |
| **LEARNED CUE -> STORE TRANSLATION (the perforant-path analogue)** | **NO. IT DOES NOT EXIST.** | see enumeration below |

### THE ABSENCE CLAIM, STATED AS AN ENUMERATION (standing rule: an absence claim requires an enumeration, not a search)

I enumerated all 147 `hdlab/*.py` modules and shape-searched every one for map-fitting primitives
(`lstsq`, `pinv`, `orthogonal_procrustes`, `np.linalg.solve`, `Ridge(`) and for gradient machinery
(`nn.Linear`, `torch.optim`, `.backward()`, `Parameter(`):

- **Exactly ONE least-squares fit exists in the whole of `hdlab/`:**
  `hdlab/reachability_audit.py:200`, `coef, _res, _rank, _sv = np.linalg.lstsq(A, r, rcond=None)`.
  That is an AUDIT tool, not a retrieval organ.
- **Exactly THREE modules contain gradient machinery:** `hdlab/slot_attention_wm.py`,
  `hdlab/entity_slot_gate.py` (`fit_entity_slot_gate(...)`, a coref slot gate), and
  `hdlab/additive_map.py` (`LearnedSGDCoordinateSource`, which lazily calls
  `experiments/_kge_anchor1_fit.fit_kge_anchor1` -- a knowledge-graph embedding fitter over triples).
- **None of the four fits a mapping from a retrieval cue's space into the store's space.**

`hdlab/learner/` is a real and useful module but it is a symbolic MDL/Bayesian **model-selection**
engine over hypothesis classes (plugins: `estimation`, `ruleind`, `gam`, `proginduction`). It does
not learn vector-space mappings. Registry: 16 rows, 10 `WIRED_AND_PIPELINE_USED`.

**So the substrate owns the completer, the separator, the conjunctive encoder and a narrowing
organ, and owns NO translator between cue space and store space.** Given section 2, that is the
organ the biology says does the work.

---

## 7. THE DECIDING EXPERIMENT -- `exp_cue_to_store_translation_v1`

Two leading hypotheses survive the drill. They make OPPOSITE predictions and one cell separates
them.

- **H1 TRANSLATION MISSING.** The partial cue carries usable information about the target, but it
  lives in a different space and we own no learned map. Prediction: a learned heteroassociative map
  from cue-space to store-space moves the partial-cue read-out above all four floors WITHOUT
  touching the store.
- **H2 THE ASSOCIATION WAS NEVER ENCODED (encoding specificity).** The cue was never bound to the
  item at encoding, so no map can recover it. Prediction: the map buys nothing, and BINDING context
  to item AT ENCODING TIME is what moves it.
- **H3 KEY AND VALUE ARE THE SAME OBJECT AND SHOULD NOT BE (LINK-NOT-RECONSTRUCT).** This is the
  2026-07-04 drill's design, never implemented. Our one flat store is asked to be both the
  discriminative ADDRESS and the high-fidelity CONTENT, and cosine in one space is asked to do both
  jobs. Prediction: separating them -- address in a sparse key space, then RETURN A LINKED DENSE
  VALUE rather than reconstructing content from the address -- moves the partial cue without either
  a learned map or a re-encoded store. **H3 is cheap, is already designed, and was never run.**

### ARMS (identical instrument, n, pool, gold, scorer as the landed partial-cue read-out; `hit_exp` primary, both tie conventions published beside every arm)

| arm | what it is | which hypothesis |
|---|---|---|
| `A0_RAW_INCUMBENT` | the landed partial-cue arm. **Regression gate: must reproduce 0.0223 to 4 dp** | neither |
| `A1_LEARNED_LINEAR_MAP` | fit `W` minimising `\|\|cue_i W - store_i\|\|^2` (ridge) on a TRAIN item split; score TEST items by `cos(cue W, store)`. Glass-box: `W` is an inspectable matrix on disk, fitted OFFLINE, one matmul at inference | **H1** |
| `A2_FIXED_RANDOM_MAP` | identical shape, `W` random. **The control that decides whether LEARNING or merely the change of basis is doing the work.** Without it A1 is uninterpretable | H1 control |
| `A3_WHITEN_ONLY` | `hdlab/whitening` on both sides, no map. Removes "the cue is higher-rank" as an explanation by equalising rank while learning nothing | H1 control |
| `A4_CONTEXT_BOUND_STORE` | rebuild the store as item-BOUND-to-context per occurrence (`hdlab/hub_spoke_word` role-key binding + `hdlab/temporal_trace` drift), then cue with the held-out context | **H2** |
| `A5_NARROW_THEN_READ` | `hdlab/context_retention.coarse_shortlist` over A0 at a swept shortlist size. **The owned narrowing organ on the read-out for the first time** | sec 3 |
| `A6_MAP_INSIDE_NARROW` | A1 within A5's shortlist -- tests the super-additive interaction the gate cell measured | interaction |
| `A7_SPLIT_LEXICON` | score the FORM channel and the MEANING channel against SEPARATE stores and combine at the DECISION, never in the cue vector. Direct test of two-stage lexical access against the additive union that measured BELOW | sec 5 |
| `A8_LINK_NOT_RECONSTRUCT` | build a sparse KEY per item (`hdlab/dg_pattern_separation` or `hippocampal_encoder.DGProjection`, unmodified), address the cue in KEY space with the cue CLAMPED through the settle (`iterative_attractor` `alpha`, the perforant-drive analogue already owned), then **return the LINKED dense value** and score in the dense space. Never reconstruct content from the key | **H3** |
| `A8b_KEY_COLLISION_AUDIT` | how many items share a key at the chosen sparsity. The prior work names key-COLLISION, not value density, as the bottleneck, and a 1,476-codes-for-4,096-words collision has already been self-flagged once in this repo. **Must be read BEFORE A8's score** | H3 validity |

### FLOORS -- all four, recomputed on the SAME stratum, permutation-calibrated, via `tools/floor_battery.py`

`F1_ORTHOGRAPHIC` (run BOTH `char_trigram_encoder` and `char_positional_encoder`; the positional one
orders the owner's own `unhelpful/unhealthy/helpful` example correctly where the trigram one inverts
it, so the standing 8.70% floor may be encoder-specific and that must be measured, not assumed);
`F2` = `frequency_floor`; `F3` = `scramble_null`; **`F4` = `constant_prototype_floor`, MANDATORY** --
this is the floor that beat spelling by +0.0523 and had never been run.
Bar = CI-separated margin over `max(F1..F4)` computed with `paired_bootstrap_ci` + `margin` from the
same module. Never a bare number.

### VALIDITY ARMS THAT FAIL INDEPENDENTLY

- `KA_EXACT_KEY` (known-answer): cue = the item's own stored row. Must read 1.0000. Sensitive to the
  scorer, the pool and the eligibility mask; INSENSITIVE to the cue->item pairing.
- `NULL_PERMUTED_CUE` (null): identical pipeline with cue-to-item assignment permuted. Must read
  chance. Sensitive to the pairing; INSENSITIVE to whether the scorer is correct.
- **Why they fail independently:** a bug in `W` cannot make both pass. If `W` leaked item identity,
  NULL rises above chance while KA stays 1.0. If the scorer were broken, KA falls while NULL stays
  at chance. This is the same independence pattern that caught the v1 two-channel design.

### LEAKAGE CONTROLS, each naming the leak it closes

1. **Fit/score split on ITEMS, not occurrences.** `W` is fitted only on items disjoint from the
   scored items. Closes: A1 memorising the answer.
2. **Morphology-blocked replicate of A1** -- delete every cue feature sharing a stem or prefix with
   the target and re-fit. Closes the SPELLING leak. Mandatory, because a pure spelling channel
   already beats the whole system 8.70% to 4.80%.
3. **Gold-blind fitting.** `W`'s objective never sees the WordNet gold sets; its only target is the
   item's own stored row. Closes the circularity the two-channel cell correctly labelled
   `INADMISSIBLE_CIRCULAR` when a WordNet-synonym cue met a WordNet gold.
4. **Popularity/genericity control**: F4 plus an explicit `oracle_constant_scores` arm. Closes: a win
   that is really prototypicality.
5. **Size-matched RANDOM gate beside A5** at every shortlist size. Closes: attributing to the
   narrowing CRITERION what belongs to the pool SIZE -- already measured once and it will recur.
6. **NO LLM anywhere.** `W` is a fitted matrix built offline; inference is one matrix multiply. This
   is the Q3-admissible static-foundation shape, not an inference-time model.
7. **Populations never merged.** Items with and without a usable held-out context are reported
   separately, as the two-channel cell did for the 37.1% with no WordNet synonym.

### DECISION RULE, WRITTEN BEFORE THE RUN

- A1 CI-separated ABOVE A2 **and** above `max(F1..F4)` -> **H1 confirmed.** The missing organ is the
  learned translation. Build target: a cue->store projection module in `hdlab/`, registered at land.
- **A1 NOT separated from A2 while BOTH are above the floors -> the TRANSLATION is what matters and
  the LEARNING is not.** This is the outcome the 2026-07-16 in-repo reading predicts ("fixed,
  largely non-learned perforant path"). It is a WIN for the component and a NULL for the learning,
  and it must be reported as both. A3 then separates "a change of basis" from "a change of rank".
- A1 not separated from A2 and neither above the floors, but A4 above -> **H2 confirmed.** The
  association was never encoded. Build target: bind context to item AT ENCODING.
- **A8 above the floors -> H3 confirmed**, and it is the cheapest of the three because the design
  already exists. If A8 wins while A1 does not, the defect was never the cue's format; it was asking
  one store to be both key and value.
- Several above the floors -> more than one organ is missing, and the ORDER is **A4, then A8, then
  A1**: you cannot learn a map to an association that was never stored, and you cannot address a
  store whose keys collide.
- None above the floors while `KA_EXACT_KEY` = 1.0 and `NULL_PERMUTED_CUE` = chance -> the cue
  genuinely carries nothing about the target, and the gap RELOCATES UPSTREAM to the encoding stage.
  **That is not a ceiling claim.** It names the next component.

### PRIOR PROBABILITIES, calibration penalty applied, REVISED AFTER THE DEDUP CORRECTION

Before finding the 2026-07-04 drill I had H1 (learned map) at ~0.55 and no H3. After it:
P(H3 -- key/value separation carries it) ~ 0.30; P(H2 -- encoding specificity) ~ 0.25;
P(H1 -- and specifically the LEARNING, not merely the projection) ~ 0.20;
P(the projection matters but learning does not, i.e. A1 ties A2 above the floors) ~ 0.15;
P(none; the gap is upstream of retrieval) ~ 0.10.
Novel-synthesis capped at 0.50 per the standing rule. H1 was deflated by 0.35 specifically because
an in-repo drill reads the same anatomy as non-learned, and I should weight a contradicting prior
reading more heavily than my own fresh one.

### SEQUENCING RECOMMENDATION

**Run A8 (LINK-NOT-RECONSTRUCT) first**, with A8b read before its score. It is the one hypothesis
whose design is already written and banked, it needs no fitting, no new store and no held-out split,
and a positive there would explain the entire exact-key-versus-partial-cue split without any of the
other machinery. A1/A2/A3 and A4 are the second wave and should be built only after A8b tells us
whether the key space can address the store at all.

---

## 8. PINNED vs OURS -- the full ledger for this drill

**PINNED BY EVIDENCE**
- CA3 has two input systems with different jobs; the direct perforant path is the retrieval-cue path
  and its synapses are associatively modified (Treves & Rolls 1992; Rolls 2018; Kesner 2007).
- LEC carries content, MEC carries context; they are parallel streams integrated in hippocampus.
- The MEC grid code is modular and compressed, not fragmentary.
- CA3 autoassociative / CA1 heteroassociative, with associatively-learned backprojections to cortex.
- Hippocampal indexing: the hippocampus stores pointers, not content; retrieval reinstates cortex.
- Sparse coding maintained by feedback inhibition; theta-gamma normalises item count per episode
  against sensory density.
- A semantic CONTROL network (left IFG + pMTG + dmPFC) is causally dissociable from the semantic
  STORE (ATL) and constrains retrieval to the goal.
- Encoding specificity: a cue is effective in proportion to its overlap with the encoded trace.
- Retrieved-context theory: in episodic recall the cue is the context state.
- Scene construction: anterior hippocampus with vmPFC drive.
- Two-stage lexical access (lemma then word form), dissociated by anomia.
- TOT is a transmission deficit between an intact semantic node and the phonological node.

**OURS, INVENTION UNDER TEST (authorised; presenting it as pinned would be barred)**
- That a fitted ridge-regression `W` is an adequate stand-in for the associatively-modified
  perforant-path matrix. The biology pins that the map is LEARNED; it does not pin linearity.
- That a coarse random projection shortlist (`context_retention`) is an adequate stand-in for
  inhibitory normalisation. The biology pins the SIZE control; it does not pin the mechanism.
- That a leaky `TemporalTrace` is an adequate stand-in for TCM's drifting context.
- That WordNet meaning-sets stand in for a semantic neighbourhood.
- That an exhaustive cosine argmax read-out is acceptable at all. **It has NO neural analogue** and
  is the component most likely to be silently setting the ceiling on every arm.

**SHELVE / REVIVAL CRITERIA, brain-framed and never performance-framed**
- **SHELVE "make the cue a fragment of the target".** Shelved because the brain's retrieval cue is
  not a subset of the stored pattern and arrives on a different wire. REVIVE only if evidence
  appears that a cortical stream delivers a literal subset of a hippocampal pattern.
- **DO NOT SHELVE the autoassociative completer.** It is the correct organ for cue type (a) and has
  never been tested on a cue type (a) in this substrate. Its standing refutations are all on cue
  types (c)/(d) and should be re-labelled accordingly rather than counted against it.
- **DO NOT SHELVE the two owner channels.** They are real; they were combined in the wrong place
  (one cue vector rather than two stores plus a link). `A7_SPLIT_LEXICON` is the fair re-test.

---

## 9. WHAT THIS DRILL DOES NOT CLAIM

- It does NOT claim any number. No experiment was run. Every figure quoted from
  `foundation-purity-build.json`, `two-channel-cue.json` and `sparsify-right-object.json` is that
  agent's measurement, cited, not recomputed here.
- It does NOT claim `W` will work. H1 is a hypothesis with P ~ 0.30 after the calibration penalty.
- It does NOT claim partial-cue retrieval is limited in any way. The owner's own memory does it.
- The reading in section 5 -- that our task poses cue types (c)/(d) while we implemented (a) -- is
  MY STRATEGIC READ of measured quantities (PR 202 vs 88.7; cosine 0.1592; the held-out-sentence
  construction). It is a hypothesis pending VET, not a measured verdict.
- Registry statuses quoted above are contradictory for 5 of the modules named. "The registry says X"
  is not a usable single fact for `dg_pattern_separation`, `cleanup_family`, `hd_fact_store`,
  `context_retention` or `hippocampal_encoder`.
- **It does NOT claim the novelty it originally claimed.** Sections 1 and 2 are substantially a
  RE-DERIVATION of `research_regime_switch_dense_retrieval_sparse_storage_brain_grounding_2026-07-04.md`.
  I asserted the opposite from a truncated grep and refuted it with a second grep twenty minutes
  later. The correction is in sec 0 and it is the more valuable half of this drill: the finding is
  not that we lacked the biology, it is that **we had the biology, banked, for six weeks, and built
  in the opposite direction from it anyway**. That is a process defect, not a knowledge gap, and it
  is the one worth acting on.
- It does NOT claim `verdict_bar_check.py` has a bar class for anything here. Nothing was run.

## 10. DISCLOSURE

No tool call in this session was denied at any point. No deletion token was issued, alone or bundled
with work. No `git add -A`. No origin push. No subagents spawned. No LLM in any path. No protected
path was written: `data/foundation/**` never opened; `CLAUDE.md`, `notes/PLAN.md`,
`notes/LONG_TERM_PLAN.md`, `notes/BOARD.md`, `data/capability_registry.jsonl`, `tools/status_*.py`,
`tools/c3_gate.py`, `tools/verdict_bar_check.py`, `tools/floor_battery.py` and `experiments/**` were
READ ONLY. `preregs/` untouched. Live runs (`scratch/selbridge_full.pid`, `scratch/them_v2_full.pid`,
foundation grid PID 22984) were never signalled, never polled, and none of their output directories
was written to. Files written by this drill: `scratch/pctd_runtime_verify.py`,
`scratch/partial_cue_transfer/runtime_verify.json`,
`.claude/scan-out/partial-cue-transfer-drill.json`, and this note. Thread pins set before numpy
import in the verification script.
