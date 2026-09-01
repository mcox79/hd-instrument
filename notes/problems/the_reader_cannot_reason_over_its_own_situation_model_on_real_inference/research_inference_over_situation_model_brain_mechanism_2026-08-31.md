# Brain mechanism of DRAWING INFERENCES over a situation model (the reasoning STEP)

Research drill for `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference`.
Date 2026-08-31. Author: solver (research drill). ONLINE-literature synthesis; calibration penalty
applied (this is a lit synthesis, not a measured result — every "the system should" below is a
DESIGN HYPOTHESIS pending our own measurement, not an inherited number).

Scope: the reasoning STEP itself (how the brain draws an inference over an already-built situation
model), NOT the model-building step. Inherits the prior drill's PINNED frame (Kintsch CI 1988; van
Dijk & Kintsch 1983; textbase-vs-situation-model; PPA/space, hippocampal time-cells/order,
pSTS/who-did-what, mPFC/cause, TPJ/belief; QUD-based paraphrase-invariant answer typing) and does
NOT rehash it.

Prior-arc work on inference-over-situation-model reasoning: **NONE** (`experiment_index.py query`
and `substrate_query.sh` both return 0 on this concept, 2026-08-31 — consistent with a
freshly-opened problem).

---

## Q1 — THE INFERENCE-GENERATION PROCESS: what is drawn ONLINE vs computed at QUESTION time

The two classic theories DISAGREE on how much is drawn online, but they CONVERGE on exactly the
distinction this decomposition needs.

**Minimalist (McKoon & Ratcliff 1992, *Psych Review* 99:440).** Only two inference classes are
encoded automatically during reading: (a) those needed for LOCAL coherence, and (b) those resting on
information that is readily/easily available (quickly and reliably activated from the text or from
general knowledge). Everything else — inferences linking local to DISTANT information, and
elaborations — is drawn only under STRATEGIC processing, i.e. when a goal or a question demands it.

**Constructionist / "search-after-meaning" (Graesser, Singer & Trabasso 1994, *Psych Review*
101:371).** Readers routinely construct a meaning representation coherent at BOTH local and global
levels. EXPLANATION-based (backward-looking, causal-antecedent, "why did that happen") inferences are
generated consistently and quickly online. ELABORATIVE and PREDICTIVE (forward-looking) inferences
are "much more variable and time-consuming" and are NOT routinely generated online.

**The convergence — this is the load-bearing finding for the decomposition:**
- **BRIDGING / COHERENCE inferences (backward, causal-antecedent, referential) ARE drawn ONLINE** and
  bound into the situation model as it is built. Both theories agree.
- **ELABORATIVE / PREDICTIVE / commonsense-default inferences are NOT routinely encoded online** —
  they are generated STRATEGICALLY at retrieval, when a question demands them, and only reliably when
  context strongly constrains them (consequence inferences appear only under strong constraint;
  elaborations "are not made during reading; they are not required for comprehension" — Potts et al.;
  McKoon & Ratcliff 1986; Cook/Guéraud on-line predictive-inference work).

**Direct implication for whether a static assembled model can CONTAIN the answer:**
- If the answer is a bridging/coherence fact (who, what-to-whom, backward "why"), it was drawn online
  and IS (or should be) in the assembled model → answerable by RETRIEVAL from the model.
- If the answer is an elaborative/predictive/script-default fact, it was NEVER encoded during reading
  → it is NOT in the model and MUST be computed at question time by a retrieval-plus-inference step
  against world knowledge. **A static situation model structurally cannot contain it.** This is a
  PINNED architectural constraint, not a tuning choice: the reasoner must run inference at query time
  for this class; there is nothing to look up.

---

## Q2 — MULTI-HOP / KNOWLEDGE-BASED BRIDGING: the retrieval mechanism and its degradation

**Chaining text → world knowledge → filled inference.** When the text leaves a gap, the described
event automatically activates GENERALIZED EVENT KNOWLEDGE (GEK) — schema/script structure for that
event type (Schank & Abelson 1977 scripts; McRae & Matsuki 2009; Metusalem et al. 2012, *JML* 66:545).
Metusalem showed a contextually anomalous word elicits a REDUCED N400 if it is merely event-related,
even after controlling for word-to-word association, and the effect DISAPPEARS without the discourse
context (Exp 2). So GEK is retrieved IMMEDIATELY, AUTOMATICALLY, and at the EVENT (message) level, and
it supplies the default fillers that bridge the unsaid.

**The retrieval mechanism itself is cue-based, content-addressable (Lewis & Vasishth 2005, *Cog Sci*
29:375, in ACT-R).** On a retrieval:
1. Retrieval CUES (here: the current text proposition + the QUD-derived question cue) are assembled.
2. Each cue spreads activation to ALL memory items that match it (situation-model elements AND GEK).
3. Activated items enter a NOISY RACE to a retrieval threshold; the most-activated item wins.
4. SIMILARITY-BASED INTERFERENCE (fan effect): the more items match a cue, the lower each one's
   activation and the slower/less reliable the retrieval. This is the built-in degradation term.

**Degradation with inference distance (the "multi-hop discriminator" the bar wants).** Human evidence
is consistent and graded, not a cliff:
- Bridging inferences across LARGER chunks of text are harder than adjacent-sentence ones.
- Answer time is SLOWER with greater INFERENTIAL DISTANCE and with surface reversal of cause/effect.
- CAUSAL-CHAIN DENSITY largely determines text difficulty; comprehension FAILS when a reader cannot
  infer a missing causal connection (Trabasso & colleagues; Britton; Singer).
- Working-memory capacity gates multi-hop success (individual-differences work).

**Realistic depth.** Automatic online bridging is typically ONE hop — backward to the most recent
needed antecedent. Deeper chaining (2+ hops) is effortful, strategic, and degrades with distance and
with interference (fan). So a brain-faithful reasoner should show a GRADED accuracy-vs-hops curve:
1-hop reliable, deep chains degrading — and a CLIFF-to-chance at hop 1 would indicate the reasoning
STEP (the retrieval/chaining machinery) is broken, not that distance is the problem.

---

## Q3 — THE CRITICAL DISCRIMINATOR: answerable-from-model vs needs-world-knowledge

**There IS a principled cognitive taxonomy that maps onto exactly this split — Graesser's 13 inference
classes (Graesser, Singer & Trabasso 1994), of which 6 are generated ONLINE and 7 are not.**

**Generated ONLINE (drawn during reading, bound into the situation model → ANSWERABLE FROM THE MODEL
if the parser extracted them):**
1. Referential (anaphora: who/what a pronoun points to)
2. Case-structure role assignment (who did what to whom — the pSTS/agent-patient dimension)
3. Causal antecedent (backward "why did that happen" — the bridging inference proper)
4. Superordinate goal (why a character did an action)
5. Thematic (the point/gist)
6. Character emotional reaction

These are precisely the who / what-to-whom / when / where / backward-why bindings the reader's
assembled model already carries (roles, timeline, space, causation, belief). **If a "text" question
asks for one of these and the reader fails, the fact is either present-and-unbound (RECALL gap) or
present-and-bound-but-uncombined (reasoning-STEP gap).**

**NOT generated online (require query-time retrieval + inference against world knowledge → NOT in the
model):**
7. Causal consequence (forward/predictive: what happens next)
8. Instantiation of a noun category (which specific thing)
9. Instrument (what tool was used — a classic script default)
10. Subordinate goal/action (how a goal was carried out — script steps)
11. State (ongoing background conditions)
12. Reader's emotion
13. Author's intent

These are script/GEK fillers. **A "commonsense" question that targets one of these can NEVER be
answered from the model alone, no matter how good the model is — it needs a world-knowledge/GEK store
plus a query-time inference (KNOWLEDGE gap).**

**MCScript2 (Ostermann et al. 2019, *SEM 2019; arXiv:1905.09531) splits along EXACTLY this line.**
~20,000 questions over ~3,500 everyday-activity texts; by construction **~half the questions cannot be
answered from the text and require commonsense/script knowledge**, the other half are text-answerable.
The dataset's own "text vs commonsense" label IS the online-vs-offline / model-vs-world-knowledge
taxonomy. Note (per the corpus-age standing confound): MCScript2 is MODERN text — no 200-year-old
McGuffey confound here.

**Three-way failure attribution (the decomposition the solver needs — attribute every miss to one):**

| gap | definition | on-disk diagnostic |
|---|---|---|
| **RECALL** (parser wall) | fact is text-derivable AND a model dimension, but the parser didn't extract/bind it | the needed proposition is in the passage but ABSENT from the reader's assembled model |
| **reasoning STEP** (missing chaining) | facts ARE bound in the model but the system can't COMBINE/CHAIN them | both facts present+bound in the model; answer needs their composition; still fails |
| **KNOWLEDGE** (no GEK store) | the fact was NEVER in the text; needs world knowledge/script | the needed proposition is nowhere in the passage; it is a script default |

These three call for THREE DIFFERENT builds (better parser / a chaining mechanism / a GEK store), so
collapsing them into one "reasoning fails" verdict would misdirect the whole program. The MCScript2
text/commonsense split cleanly separates KNOWLEDGE gaps (commonsense questions) from RECALL+STEP gaps
(text questions); the multi-hop discriminator then separates RECALL from STEP within the text
questions.

---

## Q4 — PINNED vs OUR-INVENTION-UNDER-TEST

**PINNED (brain-constrained; replicate the operation):**
- Inference operates over the SITUATION MODEL, not surface form (Kintsch CI; van Dijk & Kintsch).
- Bridging/coherence inferences (backward causal-antecedent, referential, role assignment) are drawn
  ONLINE and are IN the model. Elaborative/predictive/commonsense inferences are NOT — they are
  computed at QUESTION time (McKoon & Ratcliff 1992; Graesser et al. 1994). **This dictates a
  two-regime architecture: model-lookup for online classes, query-time inference for offline classes.**
- Answering = CUE-BASED CONTENT-ADDRESSABLE retrieval (Lewis & Vasishth 2005): cue from question+QUD →
  spreading activation → race to threshold → similarity-based (fan) interference. NOT a similarity
  lookup over one static vector; a CUED retrieval followed by an inference step. (The substrate's
  convergent/cue-based retrieval operation is the right primitive; PINNED.)
- World-knowledge retrieval = Generalized Event Knowledge / script instantiation (Schank & Abelson
  1977; McRae & Matsuki 2009; Metusalem et al. 2012), automatic and event-level.
- GRACEFUL degradation of multi-hop accuracy with inferential distance (a graded signature), driven by
  fan interference + WM limits. PINNED as a signature.
- Neural dimension subsystems (inherited PINNED): angular gyrus = situation-model INTEGRATION/UPDATING
  convergence hub; dmPFC = coherence/inference processing; ATL = semantic hub for concept combination;
  pSTS/who-did-what; TPJ/belief; hippocampus/order. (Ferstl reviews; Metusalem; ATL-vs-AG spatiotemporal
  semantic-network work, Cerebral Cortex 2022.)

**OUR-INVENTION-UNDER-TEST (sweep; do NOT adopt as truth; must stay glass-box, NO external LLM):**
- **Question → model MATCHING function** (how a question builds the retrieval cue and cues the relevant
  slots). PINNED that it is cue-based content-addressable; UNPINNED the exact cue features, which
  dimensions to cue, and cue weighting.
- **Chaining DEPTH / policy** (max hops, stopping rule, backward vs forward). PINNED that it degrades
  with distance; UNPINNED the exact depth cap and the stop criterion.
- **Answer READ-OUT** (scoring a retrieved+inferred proposition against MC options). PINNED it is not
  raw surface similarity; UNPINNED the exact match/scoring rule.
- **The world-knowledge / GEK STORE for offline (commonsense) questions.** The brain uses GEK; our
  substrate must SUPPLY a glass-box script/GEK store for the offline class. WHETHER the substrate's own
  knowledge base can serve as that store, and how it is queried, is an OUR-INVENTION design choice —
  but it is a SEPARATE build from the reasoning-over-the-model step, and absent it the offline class is
  unanswerable by construction.

---

## Predictions for the MCScript2 experiment (design from these)

A brain-faithful inference-over-model reasoner, driven from `SituationReader.read()`:

**SHOULD be able to answer (contingent on parser RECALL being adequate):**
- "Text" questions whose answer is an ONLINE-class fact bound into the assembled model: referential
  (who), role assignment (who-did-what-to-whom), backward causal-antecedent (why-it-happened), when,
  where. These are model RETRIEVAL, possibly + 1 bridging hop.
- On these, accuracy should degrade GRACEFULLY with the number of bridging hops between the question
  cue and the answer proposition (1-hop reliable; deep chains lower) — a graded curve, the reasoning
  signature. A CLIFF to chance at hop 1 = the reasoning STEP (chaining/retrieval) is broken, not
  distance.

**SHOULD NOT be able to answer FROM THE MODEL ALONE (and this is a PASS-as-honest-negative, correctly
attributed):**
- "Commonsense/script" questions whose answer is an OFFLINE-class fact never in the text: instrument,
  subordinate goal/action, predictive consequence, script default, instantiation. Without a supplied
  GEK/script store, the reader should sit AT CHANCE on these REGARDLESS of situation-model quality.
  **Attribute this to the KNOWLEDGE gap (no world-knowledge store), NOT the reasoning-STEP gap** — it
  points at a DIFFERENT build (a glass-box GEK store + query-time inference), not at chaining.

**Dissociations that validate the read-out and localize the gap:**
- INFO-FREE TWIN (shuffled bindings, same slots): should DESTROY the "text"-question advantage but
  leave "commonsense"-question performance UNCHANGED (it never depended on the model). A clean double
  dissociation — it proves the model is what carries the text-question signal and simultaneously shows
  the model is irrelevant to the knowledge-gap class.
- If the reader ALSO fails "text" questions: distinguish RECALL from STEP by checking whether the
  needed facts are present-but-unbound in the assembled model (RECALL → parser wall, the SPACE finding
  the brief already names) vs present-and-bound-but-uncombined (STEP → build a chaining mechanism).

**One caution against a false positive:** MCScript2 is 4-option-ish MC; a lexical-overlap / similarity
floor can score well above chance on the "text" split by surface matching. The PASS bar (CI-separated
over the similarity-only floor AND the no-model floor, twin LOSING) is exactly what discriminates
genuine model-based retrieval from surface matching — hold that line, and report per-SPLIT (text vs
commonsense) separately, because a single pooled accuracy will average a real text-split effect
against a structurally-unanswerable commonsense-split floor and hide both.

---

## Key citations
- McKoon G. & Ratcliff R. (1992). Inference during reading. *Psychological Review* 99(3):440-466. (Minimalist.)
- Graesser A.C., Singer M. & Trabasso T. (1994). Constructing inferences during narrative text comprehension. *Psychological Review* 101(3):371-395. (Constructionist / search-after-meaning; the 13 inference classes, 6 online.)
- Kintsch W. (1988). The role of knowledge in discourse comprehension: a construction-integration model. *Psychological Review* 95:163-182. (PINNED, inherited.)
- van Dijk T.A. & Kintsch W. (1983). *Strategies of Discourse Comprehension.* (Situation model; inherited.)
- Schank R.C. & Abelson R.P. (1977). *Scripts, Plans, Goals and Understanding.* (Scripts.)
- McRae K. & Matsuki K. (2009). People use their knowledge of common events to understand language, and do so as quickly as possible. *Language and Linguistics Compass* 3:1417-1429. (GEK.)
- Metusalem R., Kutas M., Urbach T.P., Hare M., McRae K. & Elman J.L. (2012). Generalized event knowledge activation during online sentence comprehension. *Journal of Memory and Language* 66:545-567. (Automatic event-level world-knowledge activation; N400.)
- Lewis R.L. & Vasishth S. (2005). An activation-based model of sentence processing as skilled memory retrieval. *Cognitive Science* 29:375-419. (Cue-based content-addressable retrieval; fan interference.)
- Ostermann S., Roth M. & Pinkal M. (2019). MCScript2.0: a machine comprehension corpus focused on script events and participants. *SEM 2019* / arXiv:1905.09531. (Benchmark; ~half the questions need commonsense.)
- Ferstl E.C. Neuroimaging of text comprehension (review). (Angular gyrus = situation-model updating; dmPFC = inference/coherence.) + Cerebral Cortex 32(20):4549 (2022) on ATL vs AG spatiotemporal semantic network.

---

## TLDR (plain English)
When a person reads a story, they work out the easy, "joins-the-dots" conclusions as they go and store
them with the story — who did what, and why-it-just-happened. But the fill-in-the-blank conclusions
that need everyday world knowledge (what tool they probably used, what they'd do next) are NOT worked
out while reading; the person only figures those out at the moment you ask, by pulling in general
knowledge. So our reader can hope to answer story questions by looking things up in the model it built,
but for the "common sense" questions there is nothing to look up — it must reason on the spot against a
store of world knowledge it does not yet have. The benchmark we picked splits its questions exactly
along that line (about half are "from the text", half need common sense), so we can tell three failure
types apart: the reader never captured the fact (reading problem), captured the facts but can't combine
them (reasoning problem), or the fact was never in the text at all (missing-knowledge problem) — and
those need three different fixes.

## QUESTIONS
None — the design is well-specified by this synthesis. (The one open DESIGN choice, not a question for
the owner: whether to supply a glass-box world-knowledge store for the commonsense split now, or first
prove the text-split result and attribute the commonsense split as an honest KNOWLEDGE-gap negative.
Recommendation: do the latter first — it is the cleaner can-fail step and correctly localizes the wall.)

## NEXT STEPS
1. Score MCScript2 PER SPLIT (text vs commonsense) separately — never pool them.
2. On the text split: cue-based retrieval from the assembled model + a bounded bridging-chain; PASS bar
   = CI-separated over similarity-only AND no-model floors, shuffled-model twin LOSING, with a graceful
   accuracy-vs-hops curve as the reasoning signature.
3. Attribute every miss to RECALL / STEP / KNOWLEDGE using the table in Q3 (present-unbound vs
   present-bound-uncombined vs never-in-text).
4. Expect (and correctly label) chance-level on the commonsense split absent a GEK store — a PASS-grade
   honest negative that names the next build, not a reasoning-step failure.
