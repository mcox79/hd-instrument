# Drill: brain reading->comprehension->memory pipeline vs our self-learning loop

Filed by: research (Sonnet lit-scan x3 + Opus synthesis), 2026-07-27
Trigger: self-learning loop showed NO comprehension-specific gain -- word-SCRAMBLED text refined a
concept's representation AS MUCH as coherent text (+0.029 scrambled vs +0.024 coherent, i.e. scrambled
was *numerically higher*, not even a tie). This drill answers: what does the brain do differently, and
what is the concrete mechanism to build.

## HEADLINE

**The loop pools (order-insensitive averages) the encoder's word-context representations at a
concept's mention sites; the brain instead PARSES sentence structure into a role-labeled proposition
(who-did-what-to-whom) and hippocampally BINDS that proposition -- a fundamentally different, provably
order-sensitive computation. Averaging is mathematically incapable of detecting scrambling (mean is
permutation-invariant by construction), so the null result is not a tuning failure, it is the correct
and inevitable output of the wrong operation. Fix: replace "encoder pools word-reps at mention sites"
with "reader extracts a structured role-filler proposition per mention-sentence, binds it, writes it as
a discrete fact" -- i.e. `situation_reader.py`'s existing extraction machinery is the right shape and
just needs to be the thing that feeds concept refinement, not a side-channel to it.**

P_deflated = 0.30 for "this exact mechanism swap, done naively, produces a clean comprehension-vs-
scramble margin on the first try" (novel-synthesis cap 0.50 applies, then deflated further because the
extraction accuracy ceiling on real prose is itself only ~F1 0.64 for role assignment per prior banked
work -- see Cross-thread synthesis). P for "the diagnosis (pooling is the wrong operation class) is
correct" is much higher, ~0.75, because it is a formal argument (permutation-invariance of mean), not an
empirical bet.

## 1. The brain's reading -> comprehension -> memory pipeline, mechanistically

Three converging literatures (each independently lit-scanned) give a consistent 4-stage pipeline:

**Stage 1 -- structure-building during reading (100s of ms, per sentence).** Left IFG (BA44/45,
Friederici's model) builds hierarchical phrase structure and drives thematic-role assignment
(agent/patient/theme); this is the syntactic/dependency parse. In parallel, **left anterior temporal
lobe (LATL)** performs minimal semantic composition -- Bemis & Pylkkänen (2011, *J Neurosci*) showed MEG
activity spikes at LATL specifically when two words COMBINE ("red boat") vs. an uncombinable control
("xkq boat"), at ~200-250ms, using the *same* nouns in both conditions -- i.e. this is a composition-
specific signal, not lexical access. **Angular gyrus** couples with LATL and its multivoxel patterns
track argument-structure/relational content, not mere co-occurrence (Price et al. 2015). ATL itself
functions as an amodal **semantic hub** (Lambon Ralph's Controlled Semantic Cognition / hub-and-spoke;
*Nat Rev Neurosci* 2017) that binds modality-specific features into one coherent concept -- semantic
dementia (bilateral ATL atrophy) is the lesion proof this hub is necessary, not incidental.

**Stage 2 -- proposition extraction (cognitive-psychology level).** Kintsch & van Dijk's
Construction-Integration model formalizes the OUTPUT of stage 1 as discrete **propositions**:
predicate(agent, patient, ...) tuples held a few at a time in a working-memory buffer, then integrated
into a propositional textbase that feeds situation-model construction and long-term text memory. This
is the classical evidence that comprehension output is a small set of role-labeled relations, not a
running bag of the words that were read.

**Stage 3 -- hippocampal one-shot relational binding.** The extracted proposition converges on
hippocampus. **Dentate gyrus** pattern-separates it (orthogonalizes vs. existing similar traces, so a
new fact about a known concept doesn't overwrite/blend with what's already stored); **CA3**'s recurrent
collaterals then bind the separated inputs into ONE conjunctive relational trace via fast, one-trial,
NMDA-dependent plasticity (Cohen & Eichenbaum relational-binding theory; direct electrophysiological
evidence in Neunuebel & Knierim 2014, "CA3 Retrieves Coherent Representations from Degraded Input").
Critically, what gets bound is **role-tagged**, not an unordered set: the Tolman-Eichenbaum Machine
(Whittington & Behrens, *Cell* 2020) formalizes this as an explicit factorization of an abstract
structural/relational code (which role goes where) from a content code (which filler), bound
conjunctively -- exactly the shape needed to make "A gave B to C" encode differently from "C gave B to
A" even though the item-set is identical.

**Stage 4 -- consolidation to semantic/cortical knowledge.** Complementary Learning Systems theory
(McClelland, McNaughton & O'Reilly 1995; updated 2020) says cortex normally integrates new facts slowly,
via small interleaved weight updates, to avoid catastrophic interference with existing knowledge --
hippocampus is the fast store, cortex the slow store, and offline replay (hippocampal sharp-wave ripples
during slow-wave sleep, coordinated with cortical slow oscillations/spindles -- human intracranial
evidence of a bidirectional hippocampal-cortical "dialogue," Bergmann/Staresina-line work) teaches cortex
the trace over repeated exposures. The direct exception, and the most relevant one for "learn a new fact
from a single sentence": **Tse et al. 2007/2011 (Science)** showed that when new information fits an
existing associative **schema**, cortex (notably mPFC) integrates it in as little as 1-2 trials and the
memory becomes hippocampus-independent within ~48h -- schema-congruent facts skip the slow interleaved
path entirely. This is the mechanistic analogue for "instantly understanding a new fact about a concept
you already partially know," which is exactly the substrate's use case (refining an EXISTING concept
rep from a new sentence, not learning from scratch).

### Why this is inherently order-sensitive / compositional, not bag-of-words

Two independent arguments converge:

1. **Formal (Fodor & Pylyshyn 1988; Smolensky 1990; Plate HRR).** Averaging/pooling is a commutative
   aggregation over a multiset: mean({A,B}) = mean({B,A}) identically. Any representation built purely
   from summing/averaging unbound token vectors is provably invariant under permutation of its inputs
   and therefore CANNOT distinguish "dog bites man" from "man bites dog" -- both reduce to the same bag
   {dog, bites, man}. Role-filler BINDING operators (tensor product R⊗F, or HRR circular convolution)
   break this symmetry: bind(agent,dog)+bind(patient,man) != bind(agent,man)+bind(patient,dog), because
   the asymmetry lives in which role each filler is bound to, not in the bundling/addition step (bundling
   bound pairs is still just addition -- the order-sensitivity comes entirely from binding, a structurally
   different operation from averaging raw fillers). Mitchell & Lapata (2010, *Cognitive Science*)
   formalize additive/averaging composition as the known-symmetric baseline in distributional semantics
   for exactly this reason.
2. **Empirical/neural (real-time parsing is role-sensitive within ~600ms).** Thematic-role-reversal
   anomalies ("the hearty meal was devouring the kids") elicit a P600 -- not merely an N400 -- showing
   the parser computed a SPECIFIC agent/patient assignment and flagged the reversal as a structural
   conflict, not a co-occurrence oddity (Kim & Osterhout 2005 line of work; "semantic P600" literature).
   The brain detects "same words, wrong role assignment" as anomalous almost immediately -- which is the
   exact discriminative signal our loop needs and currently cannot produce, because pooling never
   represents "who is in which role" in the first place.

## 2. The gap, per component

| Stage | Brain mechanism | Our loop | Gap |
|---|---|---|---|
| Structure-building (read) | IFG parses syntax, LATL composes, assigns agent/patient roles | Encoder produces a context-window representation per mention token; no explicit parse, no role labels | Missing entirely -- no structure is extracted, only distributional context |
| Proposition extraction | Kintsch propositional textbase: predicate(agent,patient) tuples | Concept-refinement step reads the encoder's rep AT the mention site and treats it as the "update signal" | The "update" is a raw contextual embedding, not a proposition -- it has no role structure to be right or wrong about |
| Consolidation/write | Hippocampal CA3 binds role-tagged relational trace (order matters); schema-linked fast cortical integration when congruent | Loop AVERAGES/pools these per-mention reps across all mention sites of the concept in the passage (and likely across cycles) into an updated concept vector | Averaging is a commutative aggregation -- it is mathematically IDENTICAL whether the words around the mention are in their original order or scrambled, because both give the same multiset of nearby context tokens (or a very close approximation, since the encoder's own contextual sensitivity to word order is itself weak/window-based here) |
| Falsifiability of the mechanism | Order-reversal is neurally detected as anomalous (P600) within ~600ms | Scrambling the same words produced a HIGHER refinement signal than coherent text (+0.029 vs +0.024) | This is not a marginal miss -- it is the diagnostic signature of an order-blind operation: if the operation cannot represent order, it cannot penalize disorder, and any residual sensitivity present is noise, not comprehension |

**Why our approach can never show a comprehension-specific gain, structurally, not just empirically:**
pooling collapses a sentence to (approximately) a bag of its words' context statistics. Scrambling a
sentence's word order does not change that bag. So the "coherent vs scrambled" contrast, run through a
pooling operator, is testing something the operator is blind to by construction -- like testing whether
a thermometer can tell you the wind direction. The scrambled arm coming out *higher* rather than merely
tied is very likely because scrambled word salad, if anything, spreads the mention's context window
across MORE distinct co-occurring tokens per pass (or the specific scramble method broke up frequent
n-gram redundancy that a coherent passage repeats), which is itself further evidence the signal being
measured is a co-occurrence/frequency statistic, not comprehension.

## 3. What's missing / what to build

The reader must produce the Stage-2 object (a role-labeled proposition) BEFORE anything is written into
the concept's representation, and the write must be gated on whether the proposition is well-formed
(has bound roles) and NEW (not already known), not on raw encoder similarity at a token position.

Concrete mechanism, stage by stage, mapped onto what already exists in this repo:

1. **Extract** -- `hdlab/situation_reader.py` (already built, already banked) already does most of
   Stage-1/2 for a passage: per-sentence predicate + agent + patient extraction (`_assign_roles`,
   reusing the temporal POS tagger + gold/parsed mention structure), packaged into a Cowan-4
   `EventBundleCodec` role-slot bundle (`hdlab/event_bundle.py`) -- i.e. an HRR-style BOUND role-filler
   representation, not a pooled average. This is architecturally the RIGHT shape (order-sensitive
   binding, not superposition-of-context). **The gap is that the self-learning loop's concept-refinement
   path does not currently route through this reader** -- it reads encoder reps at raw mention-token
   positions and pools them, bypassing the propositional extraction entirely. The fix is structural
   wiring, not new theory: `read(passage) -> SituationModel.events` (predicate, agent, patient per
   sentence) IS the comprehension signal; the concept-refinement update should consume `EventRecord`
   objects for the concept-as-agent-or-patient, not raw pooled vectors.
2. **Validity gate** -- `hdlab/clarify_gate.py` already implements an accept/clarify/refuse decision
   surface (`GateOutcome`) keyed on similarity margins; the natural extension is a role-completeness gate
   ahead of any concept-write: an extracted event with `agent == "?"` or `patient == "?"` (role
   unassigned -- see `_assign_roles` in situation_reader.py, which already returns `"?"` for unresolved
   roles) should NEVER be written as a proposition update, mirroring the brain's need for a resolved
   thematic-role assignment before binding. `situation_reader.py`'s optional spaCy predicate-validity
   gate (`_build_spacy_pred_gate`, adopted from the 29522 cell) is the existing precedent for "supplied
   grammar filters bad extractions before they reach memory."
3. **Bind + write as a discrete fact, not a blended average** -- the CA3 analogy is: don't average the
   new proposition into the concept's running centroid. Write it as an addressable, role-tagged unit
   (bind(AGENT,concept)+bind(PATIENT,other) or similar, exactly what `EventBundleCodec.encode_event`
   already produces) into the foundation store (`cskg_foundation_v1`-family), alongside or instead of
   pooling into the encoder representation. The same-day consolidation drill
   (`notes/drill_brainfaithful_consolidation_for_read_sleep_loop_2026-07-27.md`) independently found
   TWO separate pooling-failure modes (uniform-weight noise dilution AND common-mode/centroid
   regression) in the current averaging step -- both diagnoses are consistent with and reinforce this
   one: the write operation itself (unweighted averaging into a shared representational space) is the
   root defect, and this drill adds the THIRD reason it must go: averaging cannot represent role
   structure at all, independent of the weighting/anisotropy issues already identified.
4. **Consolidate** -- the sleep step (`exp_ingest_learn_sleep_loop_cycle*_v1.py` family) should replay
   and integrate accumulated PROPOSITIONS (discrete, role-tagged facts accumulated across a reading
   session), analogous to hippocampal-to-cortical SWR-driven consolidation, and per the Tse et al.
   schema-congruence finding, a proposition that fits the concept's EXISTING schema (consistent with
   prior known facts) should integrate fast/directly, while a novel or conflicting proposition should
   route through slower, more conservative integration (interleaved-style) or a clarify/verify gate --
   this maps directly onto `clarify_gate.py`'s existing accept/clarify/refuse trichotomy and gives it a
   principled criterion (schema-congruence) rather than only a similarity-margin criterion.

**Is the right architecture "reader extracts structured propositions" rather than "encoder pools
word-reps"? Yes, unambiguously** -- both the formal argument (permutation-invariance of averaging vs.
binding) and the biology (every stage of the human pipeline operates on role-labeled propositions, never
on a window-pooled statistic) point the same direction, and the needed extraction machinery
(`situation_reader.py`, `event_bundle.py`, `clarify_gate.py`) is already built and banked in this repo --
the fix is rerouting the self-learning loop's concept-update signal through it, not inventing a new
mechanism.

## 4. Cheap decisive test

Before any large build: take the SAME coherent-vs-scrambled sentence pairs that produced the +0.029 /
+0.024 null result. Run `situation_reader.py`'s existing `_assign_roles` / event extraction over both
arms (no training, pure diagnostic) and check: does the scrambled arm's proposition-extraction rate
(fraction of sentences yielding a resolved AGENT+PATIENT event, i.e. neither is `"?"`) collapse relative
to the coherent arm? If yes, this CONFIRMS the reader-based signal is comprehension-sensitive where
pooling was blind, and the fix is a wiring problem (route the loop through the reader). If the
extraction rate does NOT collapse on scrambled text (parser is too permissive / grammar-independent),
that would falsify the simple version of this diagnosis and point to a harder problem: the extractor
itself needs a stronger grammaticality prior (e.g. always require the spaCy predicate-validity gate,
already built as an opt-in in `situation_reader.py`, `spacy_pred_gate=True`).

This test costs under an hour (rerun an existing reader over existing sentence pairs, no new data, no
training) and should run BEFORE committing to the full re-wiring in item 3 above.

## 5. Falsifiable predictions

**HARD-PASS** (would confirm the diagnosis and justify the re-wiring):
- Cheap decisive test: coherent-arm role-resolution rate (AGENT and PATIENT both non-"?") is
  meaningfully higher than scrambled-arm resolution rate (e.g. >= 15 percentage points absolute, on a
  held-out sample of >= 100 mention-sentences per arm) -- i.e. the reader IS sensitive to the exact
  manipulation the pooling encoder was blind to.
- Full re-wire: routing concept-refinement through role-tagged proposition writes (gated on role
  completeness) produces a coherent-vs-scrambled refinement-quality gap that is (a) in the correct
  direction (coherent > scrambled) and (b) at least 3x the noise floor of the current pooling result
  (i.e. not another near-tie).

**HARD-FAIL** (would refute or force a redesign):
- Cheap decisive test: role-resolution rate does NOT differ between coherent and scrambled arms (parser
  is grammar-blind / too permissive on scrambled token streams) -- this means the extractor itself needs
  a mandatory grammaticality gate (spaCy POS validity, already available) before it can serve as a
  comprehension signal; without that, this diagnosis's fix does not close the gap on its own.
- Full re-wire: after gating on role-completeness and writing discrete propositions instead of pooling,
  the coherent-vs-scrambled gap is still within noise (e.g. < 1.5x current +0.029/+0.024 near-tie) --
  this would mean the loop's problem is not (only) the aggregation operator, and the remaining
  candidate culprits are (i) the reader's role-assignment accuracy ceiling itself being too low on real
  prose (prior banked F1 ~0.64 on McGuffey gold, per `research_drill_relation_comprehension_reader_
  thematic_roles_glassbox_2026-07-18.md`) to carry a clean signal, or (ii) the downstream write/
  consolidation step still blending discrete facts back into a shared representational space (the
  centroid-regression failure mode independently found in the same-day consolidation drill), which would
  erase the structure even if extraction worked.
- Extraction-rate ceiling check: if role-resolution rate on COHERENT real prose itself is below ~40%
  (extractor too sparse to matter), the fix must first address extraction coverage (a separately known,
  already-flagged problem: `breadth_corpus_expansion_plan_2026-07-27.md` measured reader cycle3
  coverage_frac=0.316, i.e. extraction already known throughput-limited) before the role-structure
  argument can be tested at all.

## 6. Cross-thread synthesis with prior entries

- This drill's diagnosis is CONSISTENT with, and gives a THIRD independent reason for, the same-day
  `drill_brainfaithful_consolidation_for_read_sleep_loop_2026-07-27.md` finding that plain averaging is
  broken (that drill found noise-dilution + centroid-regression; this drill adds "averaging cannot
  represent role structure at all," a structural/formal reason rather than a statistical one). All
  three reasons point at the SAME code locus: the write/update step that turns per-mention signals into
  a concept-representation delta.
- Also consistent with `scour_prior_consolidation_fusion_selflearning_2026-07-27.md`'s finding that the
  "reader-feedback-into-knowledge override" has hurt 3x across corpora (cycle2 -0.1457 acc, cycle3
  coverage_frac=0.316 ceiling, chaingrade_FULL naive baseline beating the trained reader 11/13 vs
  10/13) -- that prior finding is about the reader's ACCURACY when it does extract; this drill's finding
  is about the loop not ROUTING through structured extraction in the first place. Both must be fixed:
  route through the reader (this drill), AND fix the reader's known accuracy/coverage problems (prior
  drill) before trusting its output as a training signal.
- The existing `research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`
  already assembled much of the same biology (N400/P600, Kintsch propositions, VSA role-filler binding,
  syntactic bootstrapping) in service of a reader-design proposal -- this drill's contribution is
  narrower and more diagnostic: it explains WHY the specific coherent-vs-scrambled null result was
  guaranteed by the pooling operator's math, not just "the reader needs work" in general, and it
  proposes the specific cheap test (item 4) to confirm the reader-based alternative before a full
  re-wire.

## 7. Substrate-product implications

A substrate that can only show "reads more text about X -> X's representation moves" (regardless of
whether the text says anything true, false, or scrambled about X) cannot be trusted as a knowledge
source -- it is indistinguishable from noise accumulation. The product claim "the substrate learns from
reading" requires demonstrating exactly the discrimination this drill targets: TRUE, coherent
propositions about a concept should measurably improve that concept's usable representation; the SAME
words scrambled, or a coherent but FALSE proposition, should not (and ideally should be flaggable/
rejectable via the clarify_gate route). Until that three-way discrimination (true > false >= scrambled,
or true > {false, scrambled} with false/scrambled statistically indistinguishable from a no-read
control) is demonstrated, "comprehension-driven learning" is not a shippable capability, only "exposure-
driven drift." The concrete build item (route concept-refinement through `situation_reader.py`'s
role-tagged event extraction, gate on role-completeness via `clarify_gate.py`, write as discrete
propositions rather than pooled averages, consolidate via schema-congruence in the sleep step) is the
direct path to that demonstrable discrimination, and reuses already-banked, already-audited modules
rather than requiring new invention.

## 8. Citations (verified count: 20)

Hippocampal binding / consolidation (8):
1. Relational Memory and the Hippocampus (Eichenbaum-lineage review) -- https://www.frontiersin.org/journals/neuroscience/articles/10.3389/neuro.01.023.2009/full
2. Neunuebel & Knierim, "CA3 Retrieves Coherent Representations from Degraded Input" -- https://www.sciencedirect.com/science/article/pii/S0896627313010854
3. Whittington & Behrens, "The Tolman-Eichenbaum Machine," Cell 2020 -- https://www.sciencedirect.com/science/article/pii/S009286742031388X
4. Tse et al., schema-linked rapid cortical consolidation (Squire commentary), Science 2007 -- http://whoville.ucsd.edu/PDFs/419_Squire_Science_2007.pdf
5. Tse et al., "Schema-Dependent Gene Activation and Memory Encoding in Neocortex," 2011 -- https://pubmed.ncbi.nlm.nih.gov/21737703/
6. McClelland, McNaughton & Lampinen, Complementary Learning Systems update -- https://web.stanford.edu/~jlmcc/papers/McCMcNaughtonLampinen20IntegrNewInfoCLS.pdf
7. "How the hippocampus preserves order: the role of prediction and context" -- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4380862/
8. "Human cortical-hippocampal dialogue in wake and slow-wave sleep," PNAS -- https://www.pnas.org/doi/10.1073/pnas.1607289113

Compositionality / order-sensitivity formalism (7):
9. Fodor & Pylyshyn (1988), "Connectionism and Cognitive Architecture" -- https://direct.mit.edu/books/edited-volume/4003/The-Architecture-of-CognitionRethinking-Fodor-and
10. "Fodor and Pylyshyn's Legacy: Still No Human-like Systematic Compositionality in Neural Networks" (2026) -- https://arxiv.org/pdf/2506.01820
11. Smolensky (1990), "Tensor Product Variable Binding" -- http://www.lscp.net/persons/dupoux/teaching/AT1_2014/papers/Smolensky_1990_TensorProductVariableBinding.AI.pdf
12. Plate, "Holographic Reduced Representations" -- https://www.semanticscholar.org/paper/Holographic-reduced-representations-Plate/0c4d193b4e8520dbc583cc7ee59c8417869f67ce
13. "The 'Semantic P600': A Brief Review" (Kim & Osterhout line) -- https://www.researchgate.net/publication/351591302_The_Semantic_P600_A_Brief_Review
14. Ehrenhofer, Lau & Phillips, "N400 Blindness to Role Reversal" -- http://www.colinphillips.net/wp-content/uploads/2019/08/ehrenhofer_lau_phillips_20190318.pdf
15. Mitchell & Lapata (2010), "Composition in Distributional Models of Semantics" -- https://onlinelibrary.wiley.com/doi/full/10.1111/j.1551-6709.2010.01106.x

ATL / sentence-composition regions (5):
16. Bemis & Pylkkänen, "Simple Composition," J Neurosci 2011 -- https://www.jneurosci.org/content/31/8/2801
17. Zhang & Pylkkänen, "Disentangling Semantic Composition and Semantic Association," J Neurosci 2021 -- https://www.jneurosci.org/content/41/30/6526
18. Lambon Ralph et al., "The neural and computational bases of semantic cognition," Nat Rev Neurosci 2017 -- https://www.nature.com/articles/nrn.2016.150
19. Friederici, "The Role of Broca's Area in Sentence Comprehension" -- https://www.researchgate.net/publication/45147180_The_Role_of_Broca's_Area_in_Sentence_Comprehension
20. Price et al., "Combinatorial semantics strengthens angular-anterior temporal coupling," Neuropsychologia 2015 -- https://pubmed.ncbi.nlm.nih.gov/25682046/

(Plus Kintsch & van Dijk Construction-Integration / propositional textbase, already cited and sourced in
the in-house `research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`, not
re-counted here to avoid double-counting a citation already verified in a prior banked note.)
