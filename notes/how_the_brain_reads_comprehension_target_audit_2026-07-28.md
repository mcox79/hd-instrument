# How The Brain Reads — Comprehension-Target Audit
date: 2026-07-28
type: director-level deep-research drill (one-off audit, NOT a routed research-delivery cycle)
scope: biology-first audit of an engineering "reading/comprehension" target against the brain's actual reading stack
calibration: novel cross-study synthesis about our own system deflated 0.15–0.25 vs. what the literature alone would license; novel-synthesis certainty capped at P≤0.50; contested neuroscience flagged inline and in section (e).

---

## (a) HEADLINE

An order-sensitive sentence representation from which a subject–relation–object (S-R-O) triple can be read out is a **real but shallow sub-skill** of human reading — it corresponds, in the field's own vocabulary (Kintsch), to a fragment of the **textbase** (the propositional layer that yields *shallow* comprehension), NOT to the **situation model** (the dynamic, knowledge-integrated mental simulation that the field equates with *deep* comprehension). A forward predictive-coding training objective is genuinely brain-faithful at the *incremental-prediction* layer (it is close to surprisal/N400-style prediction-error learning), but a pure next-token objective plus a triple-extraction ruler is **necessary-but-insufficient**: it under-specifies the situation-model machinery (protagonist/space/time/causality/goal tracking, knowledge-based inference, and — contested — perceptual/motor simulation) that defines comprehension in the brain. **Verdict: PARTIAL / valid first rung, wrong finish line.**

---

## (b) THE BRAIN READING STACK — element by element (biology-first)

### 1. Lexical access (orthography → phonology → meaning)
- **ESTABLISHED.** Visual word recognition runs through the **Visual Word Form Area (VWFA)** in the left ventral occipitotemporal cortex (Cohen & Dehaene, ~2000–2011), feeding lexical-semantic networks distributed over temporal and inferior-parietal cortex. Retrieval is graded/spreading, not a clean symbol lookup: semantically/phonologically related words pre-activate. Access is **cascaded/incremental** (partial information propagates before a word is fully identified), not strictly discrete — the **Cohort model (Marslen-Wilson 1987, *Cognition*)** is the reference account: each incoming segment activates a candidate set that is pruned as more input+context arrives, often resolving before the word's offset.
- **Audit relevance:** meaning is a distributed activation pattern, not a fetched atomic symbol — consistent with a learned distributed encoder, inconsistent with a lookup-table view of "word meaning."

### 2. Incremental predictive parsing (the layer the target most resembles)
- **ESTABLISHED (strong):** comprehension is **incremental and largely left-to-right / word-by-word**. Eye-tracking, self-paced reading, and ERP all show processing effort tracking a word's predictability in context.
- **Surprisal theory (Hale 2001, NAACL; Levy 2008 *Cognition*):** processing difficulty ∝ −log P(word | context). Reading time and N400 amplitude both scale with surprisal (validated across eye-tracking corpora). This is the closest thing in the brain literature to a **forward predictive-coding objective**, and it is well supported.
- **Direct evidence for genuine forward prediction — Altmann & Kamide (1999, *Cognition*):** in the visual-world paradigm, listeners fixate the only edible object (e.g. a cake) **at the verb "eat," before the noun is spoken** — verb-argument expectations are computed *ahead* of the predicted word. This is among the strongest demonstrations that comprehension pre-computes upcoming semantic/thematic content, and it directly supports a forward-prediction training pressure.
- **N400 as semantic prediction error:** the N400 (centro-parietal negativity ~400 ms; Kutas & Hillyard 1980+) is larger for semantically unexpected/ill-fitting words. Modern computational accounts (**Rabovsky, Hansen & McClelland 2018, *Nature Human Behaviour***; **Rabovsky & McRae**; **Lopopolo & Rabovsky 2024, *Neurobiology of Language***) model the N400 as the **update to a distributed representation of sentence meaning** ("Sentence Gestalt" model trained by predicting semantic features) — i.e., **implicit semantic prediction error / Bayesian surprise at the level of integrated meaning**, not merely lexical surprisal. **This is a load-bearing point for our audit: the brain's best-supported "prediction-error" signal is a prediction error over an integrated *meaning* representation, and the endpoint it drives is an *update to a situation-level meaning state*, not the emission of a symbol.**
- **P600:** a later positivity indexing **syntactic reanalysis/repair** and integration difficulty (garden-paths, agreement violations, and some semantic-reversal anomalies). Establishes that structural assignment is a separable, revisable process.
- **CONTESTED — how strong/obligatory is prediction?** The **DeLong, Urbach & Kutas (2005)** article-(a/an)-based pre-activation finding **failed to replicate** in the large multi-lab study **Nieuwland et al. (2018, *eLife*)** (~334 participants): "our results do not support the view that readers routinely pre-activate the phonological form of predictable words." Prediction is real and graded but likely **not deterministic form-level pre-activation**; integration vs. prediction accounts of the N400 remain debated. → *Flag: predictive processing is a good computational approximation, not a settled proof that the brain pre-computes specific upcoming tokens.*

### 3. Syntax + thematic-role binding (who-did-what-to-whom)
- **ESTABLISHED.** The brain builds structured **argument bindings**, not just a bag of activated words. **Frankland & Greene (2015, *PNAS*), "An architecture for encoding sentence meaning in left mid-superior temporal cortex":** MVPA shows **left mid-superior temporal cortex (lmSTC)** carries **role-general, decodable slots for AGENT ("who did it") and PATIENT ("to whom")** — the pattern flips when roles swap but is invariant to surface phrasing (active/passive). Combinatorial/compositional semantics is hubbed in the **anterior temporal lobe** (semantic combination) with **left inferior frontal gyrus / Broca's** supporting structure-building and working-memory-linked integration.
- **Audit relevance:** the brain literally instantiates something like **filler→role binding into typed slots (agent/patient)** — this is the element the S-R-O triple *does* approximate well. The triple's (subject, relation, object) ≈ (agent, predicate, patient/theme). So the target is brain-faithful *at this layer*.

### 4. SITUATION MODEL construction (the crux)
- **ESTABLISHED as the field's definition of deep comprehension.** **Kintsch's Construction–Integration model (van Dijk & Kintsch 1983; Kintsch 1988, *Psych Review*)** distinguishes three separable levels: **surface form → textbase (propositions) → situation model.** Crucially, **a reader who only encodes the textbase has *shallow* comprehension** ("sufficient to reproduce the text but not for deeper understanding"); **deep comprehension = the situation model**, built by **integrating the text with prior knowledge via inference.** *A single S-R-O triple sits at (a fragment of) the textbase layer — Kintsch's own definition places it below deep comprehension.*
- **Event-Indexing Model (Zwaan, Langston & Graesser 1995, *Psych Science*; Zwaan & Radvansky 1998, *Psych Bulletin*):** during narrative reading comprehenders track **five situational dimensions in parallel** — **protagonist/entity, space, time, causation, intentionality/goals** — and **updating cost is measurable**: reading times increase at **discontinuities** (temporal shift "an hour later…", causal break, protagonist change, goal change). **Independently replicated (Rinck & Weber 2003, *Memory & Cognition*, "Who, when, where"):** protagonist and temporal shifts reliably raise reading time; **spatial shifts are the weakest/most task-dependent effect** (space tends to surface in offline memory-accessibility probes — Rinck & Bower 2000 — more than in online reading time). This is direct behavioral evidence that comprehension maintains and *updates* a multi-dimensional model, not a static proposition. **Causality and time dominate the online processing signatures.**
- **Mental Models (Johnson-Laird 1983):** reasoning/comprehension operate over an analog model of the described state of affairs, supporting inference by "reading off" the model.
- **Embodied / grounded simulation (CONTESTED strength):**
  - **Hauk, Johnsrude & Pulvermüller (2004, *Neuron*):** reading action words (lick/pick/kick) somatotopically activates face/arm/leg motor & premotor cortex overlapping actual movement — meaning retrieval recruits modality-specific machinery.
  - **Zwaan, Stanfield & Yaxley (2002, *Psych Science*)** implied-shape/orientation simulation ("the eagle in the sky") — comprehenders simulate perceptual detail not stated in the sentence (shape effect replicated in Zwaan & Pecher 2012; color effect did *not* replicate).
  - **Barsalou (1999, *BBS*), Perceptual Symbol Systems:** concepts are grounded in re-enacted perceptual/motor states.
  - **⚠️ MAJOR REPLICATION CAVEAT — the flagship behavioral effect is now disputed.** The **Action-Sentence Compatibility Effect (Glenberg & Kaschak 2002)** — the single most-cited embodiment finding — **failed a large pre-registered multi-lab replication (Morey et al. 2022, ~18 labs): essentially zero effect in every lab**, despite a small-but-significant pooled effect in the older meta-analysis. Treat "action simulation IS comprehension" as a *live theoretical position*, not consensus fact.
  - **STRONG vs WEAK embodiment debate is genuinely unsettled.** **Mahon & Caramazza (2008, *J. Physiology-Paris*)** argue simulation may be **epiphenomenal / a downstream spreading-activation consequence** on top of an amodal conceptual core rather than constitutive of meaning (their "grounding by interaction" middle path), and note the **abstract-concept problem** (justice, inflation) that pure sensorimotor grounding struggles with. So: sensorimotor activation is *reliably recruited* for concrete language (Hauk 2004 is robust fMRI); whether it is *causally necessary/constitutive* is contested, and recent replication failures have shifted weight toward the skeptical/weak-embodiment side.

### 5. World-knowledge / schema integration & inference generation
- **ESTABLISHED that inference is central; the *scope* is contested.** Schemas/scripts fill gaps, resolve ambiguity, and license **bridging inferences** (connecting a new entity to an antecedent, e.g. "picnic … the beer was warm" → the beer belongs to the picnic). 
- **CONTESTED scope:** **McKoon & Ratcliff (1992) "minimalist hypothesis"** (only inferences needed for local coherence + those from readily available info are automatic) vs. **constructionist "search-after-meaning" (Graesser, Singer & Trabasso 1994)** (readers routinely generate goal/causal/global-coherence inferences). Either way, comprehension is not literal proposition-extraction — it **adds knowledge-derived content not in the text.**

### 6. Working memory
- **ESTABLISHED.** Incremental integration is **capacity-constrained** (**Just & Carpenter 1992, capacity theory**). Long-distance dependencies incur **locality/integration cost** (**Gibson 2000, Dependency Locality Theory**) and parsing is well modeled as **cue-based retrieval** from a content-addressable memory (**Lewis & Vasishth 2005**). Partial structure is held and updated across the sentence/discourse — the situation model *lives in* working/episodic memory and is continuously revised.

### 7. What it means, functionally, to "understand a sentence" (the endpoint)
- **Field consensus (functional):** the comprehension endpoint is **not** a single stored symbol; it is a **dynamic, updatable situation model held in working/episodic memory**, operationally defined by what it *enables*: answering questions, drawing inferences (including ones not literally stated), detecting inconsistency, and predicting what comes next. The Rabovsky Sentence-Gestalt line makes this concrete computationally: understanding = the current state of a **distributed meaning representation** that gets **updated** by each incoming word. → *"Understood" ≈ "the internal state now supports correct inference / question-answering / anomaly-detection about the described situation," not "a triple has been emitted."*

---

## (c) THE AUDIT — target vs. each brain element

Target restated: (i) an **order-sensitive** sentence representation (coherent ≠ scrambled), (ii) from which an **S-R-O proposition** is extractable, (iii) trained by a **forward predictive-coding objective + structure-sensitive readout head**, (iv) evaluated by **order-sensitivity + relation/object recovery accuracy.**

| Brain element | Target's fidelity | Verdict |
|---|---|---|
| 1. Lexical access (distributed, cascaded meaning) | Learned distributed encoder is compatible; fine as substrate | ✅ apples-to-apples (at substrate level) |
| 2. Incremental predictive parsing (surprisal / N400) | Forward next-token/state prediction ≈ surprisal-minimization; **strong match** to the best-supported learning signal | ✅ apples-to-apples (best-aligned element) |
| 3. Thematic-role binding (agent/patient slots, Frankland & Greene) | S-R-O ≈ (agent, predicate, patient) typed slots; readout head targeting roles is faithful | ✅ apples-to-apples (this is the element the triple genuinely captures) |
| 4. Situation model: protagonist/space/time/causality/goals + simulation | **A single static triple discards 4 of the 5 event-indexing dimensions** (keeps entity/role; drops space, time, causality, intentionality) and discards perceptual/motor simulation | ❌ **SHALLOW PROXY — the core divergence** |
| 5. Knowledge-based & bridging inference | Triple extraction recovers *stated* content only; no gap-filling / inference generation | ❌ shallow proxy |
| 6. Working memory / cross-sentence update | Single-sentence triple has no updatable cross-discourse state; no revision on new info | ❌ missing (discourse-level) |
| 7. Endpoint = dynamic, inference-supporting model | Endpoint = emitted symbol, not an updatable state judged by downstream inference | ❌ measures the wrong endpoint |

**Is the ruler (order-sensitivity + relation/object recovery) measuring reading competence?**
It measures a **necessary-but-insufficient sub-skill.** Order-sensitivity is a genuine and non-trivial gate: it rules out pure bag-of-words and confirms the encoder is at least an order-sensitive transformer encoding (which each mention-representation *is*) — good. Relation/object recovery confirms role-binding (element 3), which is real brain machinery. **But passing this ruler is fully consistent with encoding only a textbase fragment and building no situation model.** It cannot distinguish "understood the situation" from "extracted the stated proposition," because it never tests **updating, inference, or cross-sentence consistency** — exactly the operations the brain literature uses to *define* comprehension. A system can ace order + triple recovery and still fail to notice that "an hour later" moved the timeline or that a re-mentioned entity changed location.

**Is a forward-prediction objective alone sufficient to induce situation-model comprehension? (SYNTHESIS — calibration-penalized, P≤0.50)**
- **Point in favor (real):** next-token prediction at scale **does** induce *some* emergent situation-model structure. Probing studies show transformer LMs trained only on next-token prediction develop **entity-state / discourse-entity tracking** and brittle situation models (entity-tracking probing literature; "(How) Do Language Models Track State?" 2025; entity-tracking work 2023–2026). So forward prediction is not *inert* w.r.t. situation models — the pressure to predict the next word *rewards* latent state-tracking.
- **Point against (real):** that emergent structure is **brittle, uneven, and scale/data-dependent** (e.g., strong entity-tracking emerged notably in models pretrained on **code**; small/limited-data models track poorly). Pure next-token training does **not reliably** yield robust multi-dimensional (space/time/causality/goal) tracking or perceptual/motor grounding, and gives **no direct pressure** for the grounding the brain uses. The brain does *not* learn comprehension from text prediction alone — it has **perceptual/motor grounding, explicit event segmentation, and goal/intention tracking** as additional machinery.
- **My synthesis (flagged as inference, deflated, P≈0.40):** a forward-prediction objective is **the right learning *pressure* but an insufficient *specification*** for our regime. At our data/scale (well below LLM scale, and data-limited per prior findings), a pure next-token objective is **unlikely on its own** to spontaneously produce robust situation-model tracking; the emergent-situation-model results come from models far larger and often code-augmented. Expect forward-prediction to buy element 2 (and reinforce 3) cheaply, but **not** to hand us elements 4–6 for free. Getting 4–6 likely needs **explicit auxiliary structure**: event/entity-state tracking objectives, an updatable discourse memory, and whatever grounding/knowledge signal is available (CSKG, norms — supplying *knowledge/data* is sanctioned; supplying a *reading mechanism* is the anti-pattern to avoid).

---

## (d) CONCRETE RECOMMENDATION + cheapest decisive test

**Recommendation: (a-with-a-guardrail).** Proceed with the forward-prediction objective + structure-sensitive readout as a **valid first rung** — it is the single most brain-faithful element and it is cheap. **But do not let the triple-recovery ruler define "comprehension."** Before investing further architecture in the current encoder, **run one cheap situation-model-consistency probe** to find out whether the encoder *already implicitly* tracks a situational dimension. This keeps the effort honest: it directly tests the biggest divergence (element 4) at near-zero cost, and its result routes the ladder.

Rationale for not jumping straight to (b): re-engineering toward full situation models before knowing whether forward-prediction already induces *latent* dimension-tracking would risk building machinery the encoder may partly already have. Measure first.

### Cheapest decisive test — "Situation-Model Consistency Probe" (bolt-on to an existing sentence encoder, no architecture change)
Design (generic, implementable from a from-scratch text encoder + available KB signal):
1. Build minimal 2-sentence discourse pairs that establish then **update one event-indexing dimension** — start with the two dimensions with the strongest, most replicable reading-time signatures (**entity-state/location** and **time**), avoiding the weak spatial-shift effect.
   - *Consistent* item: S1 sets a state; S2 is compatible ("The cup is on the table. Later, she drank from **the cup on the table**.").
   - *Inconsistent* item: S2 violates the updated state ("The cup **fell and shattered**. Later, she **drank from the cup**.").
2. From the encoder's sentence/discourse representation, train a **light linear probe** (or use a similarity/anomaly readout) to classify consistent vs. inconsistent, on **held-out entities/verbs** (so it can't memorize lexical pairs).
3. Add the mandatory **scrambled + wrong-dimension controls** (per our standing "vet positives hardest / active-control gain" discipline): a coherent-but-consistency-neutral control and a word-scrambled version. The signal of interest is **consistent-vs-inconsistent separation ABOVE the scrambled/neutral control's separation**, on held-out items.

**Falsifiable pass/fail thresholds (pre-registered):**
- **PASS (encoder already latently tracks the dimension):** held-out consistent-vs-inconsistent classification **≥ 0.70 AUC** (or ≥ +0.15 accuracy over the scrambled control), **replicated across both seeds**, with the scrambled/neutral control at chance (≤ ~0.55 AUC). → Situation-model structure is *implicitly present*; proceed on rung 1, and the ruler should be *upgraded* to include a consistency term but no architecture change is urgent.
- **FAIL (no latent tracking):** separation ≤ 0.55 AUC / within noise of the scrambled control on held-out items. → Forward-prediction alone is **not** inducing situation-model structure at our scale; **escalate to (b)**: add explicit event/entity-state tracking + updatable discourse memory as first-class training targets *before* further scaling the current triple objective.
- **AMBIGUOUS (0.55–0.70):** weak latent signal; cheapest follow-up = add an explicit entity-state auxiliary loss and re-probe.

Cost: one small probe dataset (hundreds–low-thousands of templated items) + a linear probe over the existing encoder. No new architecture, no retrain required for the first read.

---

## (e) CONTESTED-NEUROSCIENCE FLAGS (where the science itself is unsettled)
1. **Strength/obligatoriness of prediction:** form-level pre-activation (DeLong 2005) **failed to replicate at scale** (Nieuwland 2018, eLife). Prediction is graded, not proven-deterministic. Predictive coding is a useful computational-level approximation of parsing, not an established mechanistic fact.
2. **Prediction vs. integration interpretation of the N400:** whether the N400 is prediction error, integration difficulty, or an implicit *learning* signal (Rabovsky vs. others; Hodapp & Rabovsky 2021 learning-signal account) is actively debated.
3. **Strong vs. weak embodiment:** perceptual/motor simulation is reliably *recruited* for concrete language (Hauk 2004, robust fMRI) but whether it is **causally constitutive** of meaning or **epiphenomenal** (Mahon & Caramazza 2008) is unresolved; the **abstract-concept grounding problem** is a standing objection; and the flagship **ACE behavioral effect failed a pre-registered multi-lab replication (Morey et al. 2022)** — the strong-embodiment evidence base is weaker than it looked five years ago.
4. **Scope of automatic inference:** minimalist (McKoon & Ratcliff 1992) vs. constructionist (Graesser et al. 1994) — how much situation-model inference is *default/automatic* vs. strategic is contested.
5. **How "situational" default comprehension is:** shallow-/"good-enough" processing (Ferreira et al.) shows readers often *don't* build a full situation model unless the task demands it — so "the brain builds a rich situation model" is a **capacity/ceiling claim, not an always-on default.** (This actually *softens* the critique: the triple may be closer to routine shallow comprehension than the deep-comprehension literature implies.)
6. **Spatial dimension weakness:** among the five event-indexing dimensions, spatial-shift reading-time costs are the weakest/most task-dependent — don't treat all five dimensions as equally load-bearing.

---

## (f) CITATIONS
**Verified this session via WebSearch/WebFetch (author/finding confirmed against live sources):**
- Zwaan, Langston & Graesser (1995), *Psychological Science* — Event-Indexing Model; five dimensions; discontinuity reading-time costs (temporal/causal/protagonist/goal strong, spatial weak). ✔
- Rabovsky, Hansen & McClelland (2018), *Nature Human Behaviour* / Rabovsky & McRae; **Lopopolo & Rabovsky (2024), *Neurobiology of Language*** — N400 as semantic prediction error / Sentence-Gestalt meaning-update. ✔ (2024 venue confirmed)
- Frankland & Greene (2015), *PNAS* "An architecture for encoding sentence meaning in left mid-superior temporal cortex" — agent/patient role-general slots in lmSTC, phrasing-invariant. ✔
- Hauk, Johnsrude & Pulvermüller (2004), *Neuron* 41:301–307 — somatotopic motor activation for action words. ✔
- Nieuwland et al. (2018), *eLife* — large multi-lab failure to replicate DeLong & Kutas (2005) article a/an prediction N400. ✔
- Kintsch — Construction–Integration; surface/textbase/situation-model levels; textbase=shallow, situation-model=deep-via-knowledge-inference. ✔ (concept confirmed across multiple live sources; primary = Kintsch 1988, *Psychological Review*; van Dijk & Kintsch 1983)
- LLM situation-model / entity-state tracking emergence from next-token training — entity-tracking & "(How) Do Language Models Track State?" (2023–2026 arXiv); code-pretraining boosts tracking; brittle situation models. ✔ (existence/direction confirmed; treat as ML evidence, not neuroscience)
- Bridging-inference & discourse-entity probing designs (probing for bridging inference in transformer LMs; discourse-entity recognition) — used only for test-design grounding. ✔

**Additionally verified this session via parallel research sub-agents (title/venue/finding confirmed against live sources):**
- Hale (2001), NAACL — probabilistic Earley parser / surprisal. ✔
- Levy (2008), *Cognition* 106(3) — expectation-based syntactic comprehension. ✔
- Kutas & Hillyard (1980), *Science* 207 — original N400 ("senseless sentences"). ✔
- Altmann & Kamide (1999), *Cognition* 73 — anticipatory eye movements at the verb (forward prediction). ✔
- Marslen-Wilson (1987), *Cognition* — Cohort model of incremental lexical access. ✔
- Rinck & Weber (2003), *Memory & Cognition* — independent event-indexing replication (protagonist/time strong, space weak). ✔
- Frankland & Greene (2020), *Annual Review of Psychology* 71 — "Concepts and Compositionality" (language-of-thought / role-filler independence). ✔
- Just & Carpenter (1992), *Psych Review* 99 — capacity theory of comprehension (with MacDonald & Christiansen 2002 rebuttal). ✔
- Gibson (2000) — Dependency Locality Theory. ✔ ; Lewis & Vasishth (2005), *Cognitive Science* 29 — cue-based retrieval parsing. ✔
- McKoon & Ratcliff (1992), *Psych Review* 99 — minimalist inference hypothesis. ✔ ; Graesser, Singer & Trabasso (1994), *Psych Review* 101 — constructionist "search-after-meaning." ✔
- Barsalou (1999), *BBS* 22 — perceptual symbol systems. ✔ ; Glenberg & Kaschak (2002), *Psychon. Bull. Rev.* — ACE. ✔ ; **Morey et al. (2022) — multi-lab ACE non-replication.** ✔ ; Zwaan, Stanfield & Yaxley (2002), *Psych Science* + Zwaan & Pecher (2012), *PLOS ONE* replications. ✔
- Mahon & Caramazza (2008), *J. Physiology-Paris* 102 — embodiment critique / grounding-by-interaction. ✔
- Kuperberg & Jaeger (2016) / Noureddine & Kuperberg (2024), *Cognition* — predictive-coding N400. ✔ (via sub-agent)
- Johnson-Laird (1983) — Mental Models. ✔ (concept/venue)

**Recalled from training, NOT independently re-verified (treat as recalled-unverified):**
- Cohen & Dehaene VWFA specifics (~2000–2011). (recalled; VWFA existence/location sub-agent-verified)
- Zwaan (2004) Immersed Experiencer Framework. (recalled, secondary-source only)
- Ferreira et al. "good-enough"/shallow processing. (recalled)
- van Dijk & Kintsch (1983) book bibliographic details. (recalled; concept sub-agent-verified via Kintsch 1988)

**Count:** ~24 finding-clusters verified live this session (director's own searches + 3 sub-agents; 2 full-text fetches — Nieuwland 2018 eLife, N400 Wikipedia — plus ~22 abstract/snippet-level confirmations); ~4 recalled-unverified standard-textbook items. No citations fabricated; where author/year/venue could not be pinned, it is flagged inline.

---

## (g) EXECUTIVE SUMMARY (5–6 lines)
1. **Apples-to-apples? PARTIAL** — the target nails the *incremental-prediction* and *thematic-role-binding* layers (forward prediction ≈ surprisal/N400 prediction-error; S-R-O ≈ agent/patient slots, Frankland & Greene lmSTC), but stops at what Kintsch calls the *textbase* (shallow comprehension), not the situation model (deep comprehension).
2. **Biggest divergence:** a single static S-R-O triple discards 4 of the 5 event-indexing dimensions (space, time, causality, intentionality/goals) and all cross-sentence *updating* — the brain's comprehension endpoint is a dynamic, inference-supporting, updatable situation model, not an emitted symbol.
3. **Recommended adjustment:** proceed with forward-prediction as a valid first rung (don't rebuild the encoder yet), but stop treating triple-recovery as "comprehension" and add a situation-model *consistency* term to the ruler.
4. **Cheapest decisive next step:** bolt a linear "situation-model consistency" probe (entity-state/time update, held-out items, scrambled + neutral controls) onto the existing encoder — PASS ≥0.70 AUC over control on both seeds ⇒ latent tracking exists, keep rung 1; FAIL ≤0.55 ⇒ escalate to explicit event/entity-state tracking + updatable discourse memory before more scaling.
5. **Synthesis caveat (deflated, P≈0.40):** pure next-token training *can* induce brittle situation models at LLM scale (often code-boosted), but at our data-limited scale it is unlikely to yield robust space/time/causality/goal tracking or grounding on its own — expect to *supply* explicit event/entity structure and knowledge signal, not the reading mechanism.
6. **Honesty flag:** the "brain builds a rich situation model" claim is a *ceiling*, not an always-on default (good-enough/shallow processing is real), and key supports are contested (embodiment strong-vs-weak; prediction replication failures) — so the triple is a legitimate first rung, just not the finish line.
