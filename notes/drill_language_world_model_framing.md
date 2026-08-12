# DRILL — Language: build-meaning-FROM-TEXT vs update-a-grounded-WORLD-MODEL

date: 2026-07-29
type: director-level deep strategic framing drill (biology/cog-sci first; hypothesis to TEST not confirm)
scope: does brain-faithful comprehension build meaning from text, or use text to UPDATE/QUERY a pre-existing grounded world model? Implications for a glass-box ~6L/512d, 158M-token, KB+norms, no-embodiment substrate.
calibration: novel synthesis about our own system deflated 0.15-0.25 vs. what the literature licenses; novel-synthesis certainty capped P<=0.50; contested neuroscience flagged inline.

---

## (0) PRIOR-WORK CHECK (done first, per KB-check discipline)

KB concept-query `substrate_query.sh "grounded world model language comprehension situation model"` -> top hits are our OWN situation-model drills (cosine 0.49 `research_brain_qa_architecture_completeness`; 0.42 `research_drill_relation_comprehension_reader_thematic_roles`; 0.34 `research_drill_CI_comprehension_loop_situation_model`). So this drill sits directly on top of an existing, well-developed line. Load-bearing prior docs read in full:
- `notes/how_the_brain_reads_comprehension_target_audit_2026-07-28.md` — Kintsch surface/textbase/**situation-model**; Zwaan event-indexing 5 dims; Rabovsky N400=meaning-update; Frankland-Greene role-general slots; embodiment replication caveats. Verdict there: our S-R-O target = **textbase (shallow), not situation model (deep)**.
- `notes/comprehension_situation_model_frontier_scoping.md` — situation model = build-not-decode; role-general (not positional) binding; supply-STRUCTURE-not-MECHANISM line.
- `notes/brain_foundational_component_analysis.md` (2026-07-29) — per-component brain-fidelity pass. Conclusion: encoder is **feed-forward + bidirectional + stateless** where brain is **recurrent + forward-predictive + stateful**; the recurring error = bolting isolated pieces onto a FROZEN encoder; WM/active-maintenance is **ABSENT and likely THE structural block**.
- `notes/stateful_core_situation_model_build_design.md` (2026-07-29) — the already-scoped hard build: slot-attention-made-faithful, PE-gated learned write, role-general binding, trained END-TO-END.

**Foundation state (from KB + notes):** we have a 1.24M-edge relational foundation (CSKG/ConceptNet-class typed graph), Lancaster sensorimotor norms, Binder feature work, WordNet/VerbNet caches. This is a **symbolic/amodal semantic store**, used to date as SEED/teacher — NOT as an active world-model state that language updates. That distinction is the crux of this drill.

This drill's NEW contribution over the 07-28 audit: the **developmental sequence** (Spelke core knowledge), **hub-and-spoke semantic memory** (Lambon Ralph), and the **generative-world-model** reading of predictive processing — the three literatures that bear directly on "world model precedes / underlies language."

---

## (1) DEVELOPMENTAL SEQUENCE — does a grounded world model precede language? YES (strong).

**ESTABLISHED.** Human cognition is founded on a small set of **core-knowledge systems present in infancy, pre-linguistically, and shared with non-human primates** (Spelke & Kinzler 2007, *Developmental Science*, "Core knowledge"; Spelke 2000, *American Psychologist*, "Core knowledge"): systems for **objects** (cohesion, continuity, contact — objects persist and move on connected paths), **agents** (goal-directed, intentional action, not bound by contact/cohesion), **number** (approximate magnitude), **space/geometry**, and a likely fifth **social-partner** system. A ~6-month-old represents objects, number, space and agents "much as a mature rhesus monkey does" — i.e. **before productive language exists.** Intuitive physics and intuitive psychology (theory of mind) are scaffolded on these systems in the first two years.

**Implication (strong, direct):** in humans the **world model is built first and language is layered onto it.** Word learning is famously a *mapping* problem — the child maps a novel word onto a pre-existing conceptual/perceptual distinction (Revencu 2023 review of Spelke's *What Babies Know*, *Mind & Language*, treats "the missing link between core knowledge and language" as the open question precisely because the world model is the prior and language attaches to it). Language does not *create* the ontology of objects/agents/causes/goals; it *references, combines, and updates* it. This is the developmental case for framing **(b)**: comprehension = using language to update/query a pre-existing grounded model.

**Honest counter-weight (matters for us):** the core-knowledge systems are *perceptual-motor and about the concrete physical/social world.* They are the grounding for **concrete** meaning. They do **not** directly deliver the **abstract/relational** meaning (justice, because, ownership) that is our actual target — and much abstract meaning is acquired *through language itself* (verbal bootstrapping; Vygotskian internalization). So "world model precedes language" is strongest for the concrete substrate and weakest exactly where we operate. (This foreshadows the reframe: the world model our text should update is a **relational/semantic** one, not the sensorimotor core.)

---

## (2) EMBODIED / GROUNDED COMPREHENSION — is "language = instructions to build a simulation" the mainstream brain-faithful view? MAINSTREAM, but its STRONG form is now contested.

- **Barsalou (1999, *BBS*, Perceptual Symbol Systems):** concepts are re-enactments (simulations) of perceptual/motor states — meaning is grounded, not amodal-symbolic.
- **Bergen (2012, *Louder Than Words*) / Zwaan Immersed-Experiencer (2004) / Zwaan, Stanfield & Yaxley (2002):** comprehension = **mental simulation**; readers simulate perceptual detail not stated (implied shape/orientation). Language = a set of **cues/instructions** to construct and run a simulation of the described situation.
- **Pulvermüller / Hauk, Johnsrude & Pulvermüller (2004, *Neuron*):** reading action words somatotopically activates motor/premotor cortex — meaning retrieval recruits modality-specific machinery. Robust fMRI.

So the "language as instructions to construct/update a simulation" view **is** a mainstream brain-faithful position, and it is the natural mechanistic partner of the developmental case in (1).

**HONEST CALIBRATION — strong embodiment is weaker than it looked (carried from the 07-28 audit, still load-bearing):**
- The flagship behavioral effect, the **Action-Sentence Compatibility Effect (Glenberg & Kaschak 2002), FAILED a pre-registered ~18-lab replication (Morey et al. 2022)** — near-zero effect everywhere.
- **Mahon & Caramazza (2008, *J. Physiology-Paris*):** simulation may be **downstream/epiphenomenal** on top of an **amodal conceptual core**, not constitutive; and pure sensorimotor grounding **fails on abstract concepts** (the abstract-concept problem).
- Our own experiment agrees: **sensorimotor grounding applied to relational/abstract meaning HARD_FAILED (no transfer, ~chance 0.56)** — sensorimotor carries perceptual, not relational, structure.

**Net:** the *simulation/world-model* framing is mainstream and brain-faithful **at the level of "comprehension updates a model of the situation."** But the **strong, sensorimotor** version of grounding is (i) contested in the brain and (ii) empirically dead for us, and (iii) irrelevant to our abstract/relational target. This is the key disambiguation the Director's hypothesis must respect: **"grounded world model" should not be read as "sensorimotor-grounded."**

---

## (3) PREDICTIVE PROCESSING — the brain as a generative world model; comprehension = updating a latent state. STRONG.

- **Friston / Clark (predictive processing):** the brain is a **hierarchical generative model** that predicts sensory input and updates latent causes on prediction error. Comprehension, on this view, is **inference over the generative model's latent state** — new words are evidence that updates the posterior over "what situation is being described."
- **Schrimpf et al. (2021, *PNAS*), "The neural architecture of language: integrative modeling converges on predictive processing":** the models that best predict human language-network activity are next-word predictors; the language system is "optimized for predictive processing in the service of meaning extraction," combining lexical + syntactic + **world knowledge** + theory-of-mind.
- **Rabovsky Sentence-Gestalt (2018, *Nat. Hum. Behav.*; Lopopolo & Rabovsky 2024):** the N400 = **prediction error over an integrated *meaning* representation**, and it drives an **update to a situation-level meaning state** — not the emission of a symbol.

**Mapping to Kintsch/Zwaan:** the situation model (Kintsch: text integrated with prior knowledge via inference; Zwaan: multi-dimensional entity/time/causality/goal state, measurably **updated** at discontinuities) IS the linguistic-level instantiation of the predictive-processing latent state. Comprehension = **maintain a latent situation state; each incoming span is evidence; prediction error gates the update.** This is exactly the mechanism `stateful_core_situation_model_build_design.md` already scopes (PE-gated write). Predictive processing therefore **unifies** the objective (forward prediction), the update signal (prediction error / N400), and the maintained state (situation model) into ONE principle — and it is framing **(b)**: language updates a maintained generative/world-model state.

---

## (4) SEMANTIC MEMORY <-> LANGUAGE — is world knowledge the substrate language operates ON? YES (hub-and-spoke).

**Lambon Ralph, Jefferies, Patterson & Rogers (2017, *Nature Reviews Neuroscience*, "The neural and computational bases of semantic cognition") — hub-and-spoke:** conceptual knowledge = an **amodal integrative HUB in the anterior temporal lobe** that binds together **modality-specific SPOKES** (vision, action, sound, valence, language). The hub develops **modality-invariant conceptual representations** that capture deep similarity across all sensorimotor + verbal modalities; semantic dementia (ATL atrophy) degrades concepts amodally, evidence for the hub. Semantic cognition = a **representation** system (hub-and-spoke) **plus a control** system (semantic control, IFG/pMTG) that shapes retrieval to task/context.

**Implication (direct, load-bearing for us):** language does **not** carry meaning by itself — it is a **control/addressing signal into a pre-existing semantic store.** Words point into the hub; comprehension recruits and combines hub concepts, modulated by control, to build the situation model. So **world knowledge (semantic memory) is the substrate language operates on** — again framing **(b)**.

**The good news for a no-embodiment substrate:** the hub is **amodal**. The abstract/relational meaning we target lives at the hub, abstracted *across* modalities. A system with **no spokes** (no vision/motor) but a rich **relational/verbal** source is a partial, hub-biased semantic memory — impoverished for concrete/perceptual concepts, but structurally the *right kind of thing* for abstract/relational comprehension. **Our 1.24M-edge relational foundation is closest to a language-derived slice of the amodal hub — NOT a full grounded world model, but the hub is precisely the part abstract comprehension uses.**

---

## (5) THE CRUX — disentangle the THREE candidate blocks, weigh the evidence

Restate the three (not mutually exclusive):
- **(i) FRAMING:** we build meaning FROM TEXT into a blank text-situation-model; we lack a pre-existing grounded WORLD MODEL that language UPDATES.
- **(ii) SCALE/EXPERIENCE:** comprehension is emergent from massive scale + rich experience; a tiny text-only substrate can't reach it regardless of mechanism.
- **(iii) MECHANISM:** we lack the recurrent/stateful maintain-and-update machinery.

### Evidence weighing

**(ii) SCALE — REAL but DELIBERATELY ROUTED AROUND, not the block to attack.**
- True that the LLM route builds an *implicit* world model from trillions of tokens, and our 158M tokens / 6L-512d cannot reach that emergent regime (07-28 audit: emergent situation-model tracking shows up in far larger, often code-augmented models; small/data-limited models track poorly). If our plan were "scale until a world model emerges," scale would be the fatal block.
- **But that is explicitly NOT our plan.** The whole point of the foundation KB + norms is to **SUPPLY** the world model rather than wait for it to emerge. Supplying the model is the sanctioned way to sidestep the scale requirement (supply knowledge/data = allowed; the encoder still earns the *mapping*). So scale is a **constraint we engineer around**, not the lever. **P(scale is THE block) ~ low, GIVEN the supply strategy.** (If we abandoned supply and bet on emergence, it would flip to high.)

**(iii) MECHANISM — the PRIMARY implicated block (high confidence, already independently diagnosed).**
- `brain_foundational_component_analysis` already localized this rigorously: the encoder is **stateless feed-forward** and **cannot maintain OR update any state** — world model or blank situation model alike. Active working-memory maintenance is **ABSENT** ("likely THE structural block"). Every comprehension prior failed for the SAME reason: bolting a piece onto a frozen, stateless core.
- The developmental/predictive/hub-and-spoke evidence in (1)-(4) does not *compete* with this — it **sharpens** it. A world model is only useful if it can be **held and updated**; the machinery that holds-and-updates IS the mechanism block. **Framing and mechanism are the same finding seen from two ends:** "we lack a world model language updates" (framing) and "we lack the machinery to maintain/update a state" (mechanism) describe one missing organ.

**(i) FRAMING — REAL and CORRECTABLE, but a REFINEMENT of (iii), not a replacement for it.**
- The literature is strongly consistent with framing (b): world model precedes language (Spelke), comprehension = simulate/update a model (Barsalou/Zwaan/Bergen), = update a generative latent state (Friston/Rabovsky), operating ON semantic memory (Lambon Ralph). So framing (a) "build meaning purely from text into a blank slate" **is** the less brain-faithful of the two, and we HAVE been doing (a): encoder learns concepts from prose; comprehension probes use blank per-passage text-situation-models; the foundation KB sits UNUSED as an active comprehension state.
- **BUT** the framing correction is inert without the mechanism. Supplying a world model to a stateless encoder = design-A redux (structure bolted on frozen reps -> HARD_FAIL_STRUCTURE_ALONE). And "grounded" must be de-rated to "**relational/amodal-hub**," not "sensorimotor" (sensorimotor grounding is dead for us and contested in the brain, section 2). So the honest form of (i) is: **the stateful core we already plan to build should maintain the active state of a FOUNDATION-GROUNDED world model, rather than a blank text-situation-model.** That is a design-target refinement of (iii), and it is TESTABLE.

### Verdict on the three blocks
**Evidence most implicates (iii) MECHANISM, with (i) FRAMING as a genuine, adoptable refinement of the mechanism's TARGET STATE; (ii) SCALE is a constraint we deliberately supply-around, not the lever.** In one line: **BOTH world-model-framing and mechanism are the load-bearing finding — they are one missing organ (a maintainable, updatable, foundation-grounded situation state) — and the framing tells us what the mechanism should maintain.**

### FRAMING VERDICT (the headline question)
**WORLD-MODEL, with a hard caveat = "grounded" means RELATIONAL/AMODAL-HUB, not sensorimotor.** Brain-faithful comprehension is (b): language updates/queries a pre-existing model held in semantic memory + working memory — NOT (a) building meaning purely from text into a blank slate. Our current framing (a) is the less faithful one and is a real, correctable gap. HOWEVER, adopting (b) does **not** displace the mechanism diagnosis; it specifies it. **Verdict: (b) world-model, but the block is the MECHANISM that maintains the world-model state, and the reframe is a design-target upgrade to the already-scoped stateful core, not a new program.**

---

## (6) IMPLICATION + RECOMMENDATION

### Do NOT rubber-stamp the pure-framing hypothesis
The Director's hypothesis in its strong form — "block is (i): supply a world model and comprehension follows" — is **pressure-tested and rejected as insufficient.** Two independent reasons: (a) a supplied world model bolted onto a stateless encoder repeats the exact recurring error (design-A HARD_FAIL_STRUCTURE_ALONE); (b) "grounded" over-claims — our KB is an amodal hub slice, not embodied grounding, and sensorimotor grounding is empirically dead for our abstract target. **So the framing is not the whole block, and it is not a shortcut around the mechanism build.**

### What IS right about the framing (adopt it)
Reframe the **target state** of the already-scoped stateful core. Instead of the WM slots maintaining a **blank, per-passage text-situation-model** (bootstrapped only from the current text), they should maintain the **active state of a foundation-grounded world model**: slots are **seeded/keyed by the foundation-KB concepts** the passage's entities resolve to; updates are written **against prior world-knowledge**; consistency/prediction-error is judged **relative to the KB-grounded prior**, not just the local text. This is brain-faithful (comprehension = updating a pre-existing model, Kintsch's "integrate text with prior knowledge via inference"), on the **allowed side of the line** (SUPPLY the world-model content = KB, LEARN the text->update mapping = the gate, do NOT bolt on a parser/reader), and it turns the unused foundation from a static teacher into an **active comprehension substrate** (the WIRE-don't-island discipline applied to the KB itself).

### CONCRETE, BRAIN-FAITHFUL, GLASS-BOX, CAN-FAIL DESIGN DIRECTION
This is ONE added variable on top of the stateful-core build already scoped in `stateful_core_situation_model_build_design.md` — it does not change the decision to build the stateful core; it changes what the core is initialized/scored against, and it makes the FRAMING itself falsifiable.

**Design: "KB-grounded vs blank situation state" — a within-stateful-core ablation.**
- **Shared spine (from the existing scope):** K entity-slots (full d-dim, no scalar compression), recurrent clause-by-clause maintenance, LEARNED PE-gated write, role-general (content-key) binding, trained END-TO-END with the encoder. Measurement = the HARDER multi-entity/multi-boundary calibration-first construction with the MANDATORY random-init-core control.
- **The one variable (the framing test):**
  - **Arm A (current framing / blank):** slots initialized empty (or from local text only); consistency judged only against text seen so far.
  - **Arm B (world-model framing):** each detected mention is resolved to a foundation-KB concept vector (a supplied *content* prior, glass-box: you can read which concept keys each slot); slots are **seeded** with that KB prior; the PE/consistency signal includes a term for **agreement with the KB-grounded prior** (does the text's asserted entity-state cohere with world knowledge). Supplying the KB vector = allowed (knowledge/data); the update gate is still LEARNED.
- **Pre-registered can-fail bands:**
  - **HARD_PASS for the framing:** Arm B beats Arm A by >= +0.05 on cross-boundary consistency (and on a knowledge-dependent-inference / bridging arm where the answer requires prior knowledge not in the text), **both seeds**, with the **random-init-core control at chance** for BOTH arms (rules out structure-alone), and Arm B's advantage **concentrated on the knowledge-dependent items** (the discriminating signature — if B only helps where text-alone suffices, the KB prior isn't doing world-model work).
  - **HARD_FAIL for the framing:** Arm B ties/loses to Arm A both seeds, OR its gain vanishes once the random-init-core control is applied (structure/KB-lookup alone), OR the gain is uniform across knowledge-dependent and text-sufficient items (KB is acting as a generic feature, not a world model). -> the framing is NOT the lever; the pure stateful core (Arm A) is the story, and the block was mechanism-only.
  - **MIDDLE (+0.02-0.05 / single-seed):** weak; do not bank; add the knowledge-dependent arm weight and re-probe.
- **Calibration gate (measurement-first, non-negotiable):** the harder construction must first be passed by a known diagnostic reader (MiniLM/BGE, diagnostic-only) AND a knowledge-augmented reader must beat a text-only reader on the knowledge-dependent items — otherwise the construction can't even *express* a world-model advantage and the measurement is the block, not the framing.

**Why this is the right can-fail step:** it makes the Director's world-model hypothesis **falsifiable in one ablation**, piggybacks on a build we are doing anyway (no separate program), respects every standing discipline (supply structure not mechanism; no borrowed-embedding-as-encoder — the KB vector is a supplied *prior/content*, not the encoder; random-init + both-seed controls; calibration-first), and — critically — its **discriminating signature is knowledge-dependent inference**, the one thing a world-model framing predicts and a blank-slate framing does not. If Arm B wins ONLY there, the framing is real; if it wins everywhere or nowhere, it isn't.

### Sequencing (stay-course with a target upgrade)
1. **v5 forward-PC verdict** (in flight) — tests objective fidelity; do NOT expect comprehension (still stateless).
2. **Build the harder KB-dependent calibration construction FIRST** (measurement-first; must pass known-reader + knowledge-augmented > text-only gate).
3. **Build the stateful core with BOTH arms** (A blank, B KB-grounded) — one build, one added variable.
4. **VET on the brain-metric with random-init-core + both-seed controls;** the A-vs-B delta on knowledge-dependent items is the framing verdict.

**Bottom line:** the world-model framing is CORRECT and worth adopting as the stateful core's design target, but it is a **refinement of the mechanism build, not a substitute for it, and not a shortcut** — and "grounded" must be read as relational/amodal-hub (our KB), not sensorimotor (dead for us). Stay the course on the stateful core; upgrade its target from a blank situation model to a foundation-grounded one; and make the framing itself the falsifiable A/B variable so we TEST it rather than assume it.

---

## (7) CITATIONS (live-verified this session unless flagged)
- Spelke & Kinzler (2007), *Developmental Science* 10:89-96, "Core knowledge"; Spelke (2000), *American Psychologist*, "Core knowledge of objects" — pre-linguistic core systems (objects/agents/number/space/+social), shared with primates. ✔ (WebSearch, multiple live sources incl. harvardlds PDF, Wiley)
- Revencu (2023), *Mind & Language*, review of Spelke *What Babies Know* v.1 — "the missing link between core knowledge and language" (language layered onto pre-linguistic model). ✔ (Wiley listing)
- Barsalou (1999), *BBS* 22 — perceptual symbol systems. ✔ (carried, prior audit)
- Bergen (2012) *Louder Than Words*; Zwaan (2004) Immersed Experiencer; Zwaan, Stanfield & Yaxley (2002), *Psych Science* — comprehension = simulation. ✔ (concept; Zwaan 2002 verified prior audit)
- Hauk, Johnsrude & Pulvermüller (2004), *Neuron* 41 — somatotopic motor activation for action words. ✔ (prior audit)
- Glenberg & Kaschak (2002) ACE; **Morey et al. (2022) ~18-lab ACE non-replication**; Mahon & Caramazza (2008), *J. Physiology-Paris* 102 — embodiment critique / abstract-concept problem. ✔ (prior audit)
- Friston / Clark — predictive processing / hierarchical generative model. ✔ (concept, widely established)
- Schrimpf et al. (2021), *PNAS* 118, "The neural architecture of language: integrative modeling converges on predictive processing." ✔ (WebSearch, pnas.org)
- Rabovsky, Hansen & McClelland (2018), *Nat. Hum. Behav.*; Lopopolo & Rabovsky (2024), *Neurobiology of Language* — N400 = meaning-update / prediction error over integrated meaning. ✔ (prior audit)
- Kintsch (1988), *Psych Review*; van Dijk & Kintsch (1983) — surface/textbase/situation-model. ✔ (prior audit)
- Zwaan, Langston & Graesser (1995); Zwaan & Radvansky (1998); Rinck & Weber (2003) — event-indexing 5 dimensions, updating cost at discontinuities, spatial weakest. ✔ (prior audit)
- Frankland & Greene (2015), *PNAS* — role-general AGENT/PATIENT slots in lmSTC. ✔ (prior audit)
- **Lambon Ralph, Jefferies, Patterson & Rogers (2017), *Nature Reviews Neuroscience* 18:42-55, "The neural and computational bases of semantic cognition"** — hub-and-spoke; amodal ATL hub + modality spokes; representation + control. ✔ (WebSearch, nature.com + wiredbrains PDF)
- LLM emergent situation-model / entity-state tracking (scale/code-dependent, brittle) — entity-tracking probing literature 2023-2026. ✔ (prior audit; ML evidence not neuroscience)

**Recalled-unverified:** Vygotsky verbal internalization; Just & Carpenter capacity; specific Bergen 2012 page-level claims.
