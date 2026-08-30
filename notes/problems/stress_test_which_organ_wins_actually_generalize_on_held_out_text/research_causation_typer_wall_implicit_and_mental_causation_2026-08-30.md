---
topic: causation_typer_wall_implicit_and_mental_causation
date: 2026-08-30
filed_by: research (solver-scoped, single-file write)
trigger: exp_generalize_causation_typer_maven_ere_v1.py DOES-NOT-HOLD result (T2a/T2b, GENERALIZATION_LEDGER.md rows 59-60, SOLVED.md "SECOND RERUN")
lit_scan_calibration: APPLIED per [[feedback-lit-scan-calibration-penalty]] -- all P estimates below deflated 0.15-0.25 off naive lit-scan confidence; novel-synthesis P capped at 0.50; hard-fail thresholds pre-registered in the decisive test
---

# HEADLINE

The 16.1% fire-rate is a **real scope boundary, not a bug**: force dynamics (Talmy/Wolff) is a lexical-semantic
theory of how a single explicit causative VERB encodes a force interaction inside one physical (or
physical-analog) event -- it was never a theory of, and has no mechanism for, inferring a causal EDGE between
two independently-described events with no causal predicate at all. The brain computes THAT (implicit,
connective-less, event-to-event narrative causation) with a **different, well-documented cognitive/neural
system**: causal-network construction over the situation model (Trabasso/van den Broek/Kintsch/Graesser,
Singer & Trabasso), neurally supported by a dissociable generation+integration inference process (Mason & Just
2004) and a right-hemisphere-dependent global-coherence process (Beeman lesion studies) -- separate from local/
explicit causal-sentence processing. For MENTAL/SOCIAL causation, the picture is a partial, additive
dissociation, not a clean either/or: physical and social causal judgments share a domain-general fronto-parietal/
insula "detect-a-causal-structure" network, but social/intentional causation additionally and specifically
recruits the mentalizing network (TPJ, mPFC/dmPFC), which selectively breaks down in ToM-impaired populations
(schizophrenia). **Verdict: narrowly-valid-but-mis-scoped, not a wrong primitive** -- reclassify the typer as a
sub-module for explicit physical-causal predications, and open a new problem for the implicit/event-graph causal-
inference organ that covers the ~84% the typer structurally cannot reach.

---

## WALL 1 -- IMPLICIT (connective-less) causal inference between two ordinary events

**Question:** How does the brain infer causality between "[the attack] ... [the city fell]" with no causal verb?

### PINNED / MODELING inventory

| Finding | Tag | Citation | Verified this session? |
|---|---|---|---|
| Causation in a reader's situation model is represented as **edges in an event-to-event graph**, validated by a counterfactual-necessity test ("if A had not occurred, B would not have occurred in the circumstances of the story"), not as a property computed inside a verb | MODELING (robust behavioral convergence: recall, importance-rating, summarization, reading-time) | Trabasso & van den Broek (1985, *J. Mem. & Lang.* 24:612-630); Trabasso & Sperry (1985, same journal) | Yes (lane C) |
| Causal-inference generation during reading is **online and sequential**: each incoming event is tested against the running causal network; unsupported/contradicting events raise reading time | MODELING | van den Broek (1990, in Graesser & Bower, *Psych. of Learning & Motivation*) | Yes (lane C) |
| Reading = "search after meaning": comprehension prioritizes causal-antecedent ("why did X happen") and superordinate-goal inference-generation over a propositional situation model | MODELING | Graesser, Singer & Trabasso (1994, *Psychological Review* 101:371-395) | Yes (lane C) |
| Causal-relatedness distance between two events shows an **inverted-U** effect on recall (too-close and too-distant pairs both recalled worse than moderate-distance) -- only explicable if causation is a chain/graph-DISTANCE property, not a property of an isolated verb | MODELING | Myers, Shinjo & Duffy (1987, *J. Mem. & Lang.* 26:453-465) | Yes (lane C) |
| Causation is one of **five indices** (time, space, entity, causation, motivation/goal) that link whole event-nodes in the situation model; causal, temporal, goal, and protagonist discontinuities (not spatial) reliably slow reading | MODELING | Zwaan & Radvansky (1998, event-indexing model); Zwaan, Radvansky, Hilliard & Curiel | Yes (lane C) |
| Causal-COHERENCE bridging is computed via a mediating causal proposition (e.g. RELIEVE[ASPIRIN,PAIN]) constructed on the fly and validated against world knowledge, even absent instruction | MODELING | Singer & Halldorson (1992, *J. Mem. & Lang.*); Singer et al. (2015, *J. Psycholinguistic Research*) | Yes (lane C) |
| Comprehension = construction (over-generate a loosely-connected propositional net from text + background knowledge, with noise) then integration (connectionist-like spreading-activation settling) -- causal coherence EMERGES from network settling, not verb-force computation | MODELING | Kintsch (1988, *Psychological Review* 95:163-182) | Yes (lane C) |
| **Causal-inference-during-reading recruits two dissociable large-scale cortical networks** -- a generation component and an integration component | **PINNED** (fMRI, coarse component-process dissociation) | Mason & Just (2004, *Psychological Science*) | Yes (lane C) |
| **Right-hemisphere-damaged (RHD) patients selectively fail to generate/integrate global coherence-relevant (bridging, predictive) causal inferences**, while locally-explicit causal comprehension is comparatively preserved | **PINNED** (lesion dissociation) | Beeman (1993, 2000) | Cited via secondary source this session -- flag as **background-confirmed, not primary-source-verified this pass** |
| Glass-box / non-LLM computational models infer implicit event-event causality from **discourse-connective pattern mining** (CausalBank: "because"/"so that" etc., 314M pairs, ~95% precision, explicit-only by construction -- same coverage ceiling as a force typer), **higher-order selectional-preference/co-occurrence over parsed eventuality pairs** (ASER, Zhang et al.), or **crowd-sourced schematic if-then triples** (ATOMIC / Event2Mind, Sap et al. 2019) -- never from verb-internal force decomposition | MODELING (engineering, symbolic/interpretable, not neural-LLM) | Schank & Abelson (1977, scripts); ASER (Zhang et al. 2020/2022, arXiv:2104.02137); COPA (Roemmele, Bejan & Gordon 2011); CausalBank (Li et al., JHU); ATOMIC (Sap et al. 2019, arXiv:1811.00146) | Yes (lane C) |
| Trabasso's four narrative causal-relation TYPES (physical > motivational > psychological > enabling, strong-to-weak) were directly operationalized to MINE causal pairs from raw text (film scene descriptions), beating co-occurrence baselines against human judgment | MODELING, but a working non-LLM extraction system | Hu & Walker (2017, SIGDIAL, arXiv:1708.09496) | Yes (lane C) |

### PARTIAL / PENDING -- the Bayesian-structure-learning slice (Lane A did not return; do not treat as refuted, treat as unconfirmed this pass)

Lane A (dispatched specifically for Griffiths & Tenenbaum causal-structure-and-strength Bayes nets, Waldmann
causal-model theory, Cheng 1997 causal-power PC theory, Sloman's *Causal Models*, Fugelsang & Dunbar 2005
*prior-belief x covariation* fMRI work, and the Feng et al. 2021 ALE meta-analysis of discourse causal
inference) returned only a dispatch stub, not synthesized findings, before this note was due. **This slice is
PENDING, not negative.** From background knowledge only (uncalibrated, NOT independently verified this session
-- treat as P<=0.30 until re-run):
- Griffiths & Tenenbaum's Bayesian causal-support model (causal structure as a hypothesis over a small space of
  graphs, scored by a likelihood over observed covariation) is the standard COMPUTATIONAL-level account of how
  people infer a causal link from statistical co-occurrence when no mechanism/verb is given -- this is the
  natural candidate mechanism for exactly the "[attack]...[city fell]" case, since attack and fall co-occur
  with high narrative regularity (a prior) even with zero force-verb marking.
- Cheng's causal-power (power PC) theory is the leading MODEL of how covariation gets converted to a causal-
  strength estimate discounting alternative causes -- again a covariation-based, not mechanism/force-based,
  route.
- A "dual-route" architecture (covariation-based statistical route vs mechanism/force-knowledge route) is a
  plausible reconciliation frame, but the specific neural dissociation evidence (which regions carry which
  route) was NOT independently confirmed this session and must not be quoted until Lane A (or a follow-up)
  actually returns primary-source-verified citations.
**Action for the Director:** either re-dispatch a narrow follow-up lit-scan specifically for Griffiths &
Tenenbaum / Cheng / Waldmann / Feng et al. 2021 ALE meta, or treat the WALL 1 verdict below as resting on the
(already well-verified) narrative-causal-network + Mason&Just/Beeman evidence alone, which is sufficient to
answer the VERDICT question without the Bayesian slice.

### WALL 1 VERDICT

Implicit event-event causal inference IS a different brain system from force-dynamic verb semantics, and it is
**PINNED at the coarse/component level, not at circuit/mechanism level**: Mason & Just (2004) show causal-
inference-during-reading recruits dissociable generation and integration cortical networks (fMRI), and Beeman's
right-hemisphere lesion work shows global/bridging coherence inference selectively fails under RHD while local
explicit causal comprehension is spared -- i.e., there is a real neural fractionation between "read an explicit
causal predicate" and "infer an implicit causal edge across the discourse," but no one has localized a
"graph-edge-builder" circuit at finer grain. At the cognitive/representational level (robust, cross-lab,
40+ years of convergent behavioral evidence: Trabasso, van den Broek, Kintsch, Graesser/Singer/Trabasso, Zwaan/
Radvansky), the mechanism is well-characterized: causation is a **graph-edge property linking whole propositions/
events**, built online via construction-integration and validated against world knowledge/schemas, NOT a
property computed by classifying a single verb's force structure. The typer's 16.1% fire-rate is therefore a
**genuine, expected scope boundary**: force dynamics operates at word/predicate-internal grain; narrative
causal inference operates at the graph/discourse grain; they were never going to be the same system, and no
result here suggests the typer is broken so much as aimed at the wrong 84% of the population.
**P_deflated = 0.62** (narrative-causal-network account) / **0.35 PENDING** (specific Bayesian-mechanism
sub-claim, capped low until Lane A confirmed).

---

## WALL 2 -- Physical vs mental/social force-dynamics

**Question:** Is Talmy's physical-to-psychological/social extension of force dynamics PINNED (same circuitry) or
a linguistic-theory stretch (mental causation = ToM/intentional-stance, a different system)?

### PINNED / MODELING inventory

| Finding | Tag | Citation | Verified this session? |
|---|---|---|---|
| Talmy's own framing of the physical-to-mental/social extension is explicitly **"metaphorical transfer,"** i.e. a claim about conceptual-semantic structure, not shared neural circuitry | MODELING | Talmy (1988, *Cognitive Science*) | Yes (lane B) |
| Wolff (2007) extends the CAUSE/ENABLE/PREVENT force-vector model to social-causal verbs (persuade, convince, compel, constrain, deter, ...) and shows the model captures verb-CHOICE behavior -- **all evidence is verb-categorization/sentence-judgment behavior, zero neuroimaging** | MODELING | Wolff (2007, *JEP:General* 136:82-111) | Yes (lane B, partial -- full-text of Exp 5-6 blocked) |
| Wolff & Barbey's strongest amodality claim ("the processes used for composing forces in the physical world CAN BE RECRUITED for composing forces in other domains") is a computational-level hypothesis tested only against linguistically-presented compositions, published in a neuroscience-titled venue but containing **no brain data** | MODELING | Wolff & Barbey (2015, *Frontiers in Human Neuroscience* 9:1) | Yes (lane B) |
| Wolff & Song ran 5 experiments showing the force-vector model beats Cheng's probabilistic-contrast model at predicting which causal VERB (cause/help/allow/prevent) people choose for a described PHYSICAL interaction -- the model's strongest empirical grounding is entirely within the physical domain | MODELING (behavioral, strong within-domain support) | Wolff & Song (2003, *Cognitive Psychology*) | Yes (lane B) |
| Physical/mechanical causal PERCEPTION has a real, partially lesion-verified substrate: causal (launching) vs non-causal events -> right middle frontal gyrus + right inferior parietal lobule; **split-brain patients show direct perceptual causality is right-hemisphere-dependent while inferred/reasoned causality relies more on the left hemisphere** | **PINNED** (lesion/split-brain dissociation -- the strongest tier of evidence in this drill) | Fugelsang, Roser, Corballis, Gazzaniga & Dunbar (2005, *Cognitive Brain Research* 24:41-47); Roser, Fugelsang, Dunbar, Corballis & Gazzaniga (2005, *Neuropsychology* 19:591-602) | Yes (lane B) |
| Mechanical/inanimate contingency detection (-> middle temporal gyrus + right IPS) and intentional/animate contingency detection (-> superior parietal networks) are **already separable at the level of simple animacy cues**, well below full "social causation" verb complexity | **PINNED** (factorial fMRI double dissociation) | Blakemore, Boyer, Pachot-Clouard, Meltzoff, Segebarth & Decety (2003, *Cerebral Cortex* 13:837-844) | Yes (lane B) |
| The mentalizing network (right TPJ, mPFC/dmPFC, precuneus/PCC, bilateral pSTS) is selectively engaged whenever a task requires representing another's mental states, dissociated from physical/appearance-based control tasks | **PINNED** (foundational fMRI dissociation + converging meta-evidence) | Saxe & Kanwisher (2003, *NeuroImage* 19:1835-1842); Frith & Frith (2006 review) | Yes (lane B) |
| **Closest direct contrast found:** within-subject 2x2 fMRI of physical-causal vs social-causal judgment finds a domain-general fronto-parietal/insula "causality-general" network shared by BOTH, but social causal judgment ADDITIONALLY and specifically recruits TPJ + animacy/intentionality-linked regions not needed for physical judgment | **PINNED** | Straube, Wende, Nagels, Blos, Stratmann, Chatterjee & Kircher (2013/2014, *Neuropsychologia*); Blos, Chatterjee, Kircher & Straube (2012, *NeuroImage*, reversed activation + reversed psychophysics by domain) | Yes (lane B, full-text blocked 403 -- region list from search-summary) |
| **Patient-group double dissociation:** schizophrenia patients show selectively altered SOCIAL (not physical) causality judgments, tracking their known ToM/TPJ deficits | **PINNED** (clinical dissociation) | Wende, Nagels, Stratmann, Chatterjee, Kircher & Straube (2015) | Yes (lane B) |
| A 2026 behavioral study explicitly critiques force/counterfactual causal-language models as physical-event-centric, and finds people choose systematically DIFFERENT causal verbs depending on whether the "force" being described is physical, epistemic (belief-based), or preference-based -- direct evidence mental/social causal language tracks a **belief-desire-structured** representation, not a force-vector one | MODELING (behavioral, but diagnostic for text) | Teo, Bergey & Gerstenberg (2026, Stanford CICL preprint) | Yes (lane B, abstract-level) |

### WALL 2 VERDICT

The physical-to-mental/social extension is **NOT neurally pinned as "same circuitry."** Every piece of evidence
for the extension (Wolff 2007 Exp 5-6, Wolff & Barbey 2015, Teo et al. 2026) is behavioral/linguistic; no
imaging or lesion study shows the physical-force circuitry (right MTG/IPL/MFG per Fugelsang et al. 2005, right-
hemisphere-lateralized per Roser et al. 2005 split-brain) is reused for intentional/social judgment. What the
neural literature actually shows is a **partial, additive dissociation**: a domain-general fronto-parietal/
insula network handles causal-structure DETECTION for both physical and social cases (giving Wolff's amodal-
core intuition some real support), but social/intentional causation additionally and specifically recruits the
mentalizing network (TPJ, mPFC), which selectively fails in ToM-impaired patients (schizophrenia). **Practical
diagnostic for real text:** force-dynamic causatives take direct-object/PP complements describing energetic
transfer and are defeated only by physical facts ("the ball broke the window"); intentional/social causatives
(persuade, allow-by-an-agent, prevent-by-an-agent) take propositional-attitude/infinitival complements
referencing the target's subsequent BELIEF-MEDIATED action and are defeated by evidence about the target's
prior beliefs/desires ("she persuaded him to leave, but he'd already decided to go") -- this is exactly the
physical/epistemic/preference distinction Teo et al. (2026) show speakers track in verb choice, and it is a
detectable surface signature (complement type + defeasibility class), not a hidden one.
**P_deflated = 0.55** (additive-dissociation reading) -- this is a novel-synthesis integration of several
independently-pinned pieces, so capped near the 0.50-0.55 band per calibration policy despite each individual
component being well-evidenced.

---

## WALL 3 -- The right brain-faithful causal representation for narrative, and SCOPE vs WRONG-PRIMITIVE

### Trabasso-vs-Wolff grain mismatch (the mechanistic reason the typer structurally cannot cover most real causation)

Trabasso's narrative causal categories (physical > motivational > psychological > enabling, strong-to-weak, per
Trabasso & Sperry 1985 / Trabasso & van den Broek 1985 / van den Broek 1990) are **coarse relations between two
whole story EVENTS** ("did event A have to happen for event B to be possible?"). Wolff's CAUSE/ENABLE/PREVENT
is a **fine-grained relation between two force-VECTORS inside a single depicted physical interaction** (does
the affector's force align with or oppose the patient's own tendency?). The overlap is real but narrow:
Trabasso's "physical" category is the only stratum where force dynamics could, in principle, further subdivide
CAUSE-vs-ENABLE-vs-PREVENT; Trabasso's motivational and psychological categories (goal -> action; event ->
character emotion) have **no force-dynamic analog at all**, because there is no agonist/antagonist force pair
between a belief and an emotion. [MODELING -- behavioral typology, verified lane C; no neural localization of
the four Trabasso categories specifically was found.]

### Coverage math (ties the MAVEN-ERE finding to the literature)

PDTB-style corpora show a large share of ALL discourse relations carry no explicit connective (the ~39-40%
implicit-relation figure is a discourse-relations-in-general statistic, NOT independently re-verified as
causal-relations-specific this session -- **flag as background-deflated, do not quote the exact percentage as
causal-specific**). The MAVEN-ERE result itself (16.1% fire-rate, i.e. 83.9% implicit by the typer's own
measurement) is a DIRECT, already-verified-on-our-own-data instance of exactly this pattern, and is consistent
in DIRECTION (implicit dominates) with the PDTB base rate even though the exact number should not be imported
across corpora.

### Glass-box precedent for the missing organ

Non-LLM, interpretable systems already exist for the implicit-causal-inference gap and give a concrete
architecture menu: **Schank & Abelson scripts** (stereotyped causal-temporal action sequences, symbolic slot-
filling), **ASER** (eventuality knowledge graph, causal edges from higher-order selectional-preference /
co-occurrence statistics over parsed discourse), **ATOMIC/Event2Mind** (crowd-sourced if-then commonsense
causal triples), **CausalBank** (314M pairs mined from explicit connectives at ~95% precision -- useful as a
TRAINING signal for a symbolic scorer, not itself a solution to the implicit case since it is connective-based
by construction), and **Hu & Walker (2017)** who directly operationalized Trabasso's four-way typology to mine
causal pairs from raw narrative text (film descriptions) and beat co-occurrence baselines against human
judgment -- the closest existing non-LLM bridge from the psychological typology to a working extractor. All
verified lane C, all symbolic/interpretable (ASER/CausalBank are statistical-graph, not neural-LLM; COMET-style
neural completions are an optional add-on, not the base mechanism).

### WALL 3 VERDICT

**Reclassify as: valid-but-narrowly-scoped (explicit physical-causal predication only), NOT wrong primitive.**
Wolff & Song's five experiments give force dynamics genuine, replicated support as the correct lexical-semantic
account of how ENGLISH CAUSATIVE VERBS encode a force interaction WITHIN a single explicitly-described physical
interaction -- that support does not evaporate because the typer fails on MAVEN-ERE; MAVEN-ERE mostly is not
testing what force dynamics was built to explain (implicit event-to-event narrative causation and motivational/
psychological causation, both structurally outside the theory's scope per the Trabasso grain-mismatch above).
The correct design is therefore additive, not a replacement: (a) keep the force-dynamic typer scoped to
explicit physical-causal predications, where an unbiased test (the organ's own minimal-pair construction) may
still hold; PLUS (b) build a complementary implicit/graph-based causal-inference organ modeled on the
Trabasso-network / construction-integration tradition, informed by the ASER/ATOMIC/CausalBank precedent for a
non-LLM implementation path, to cover the ~84% the typer cannot reach by design.

---

## NAMED NEXT PROBLEM

**`narrative_causal_graph_missing_implicit_inference_organ`** -- build a complementary implicit-causal-inference
component that scores a causal EDGE between two events with no connective, using event-type co-occurrence /
schema plausibility (ASER-style selectional preference or an equivalent glass-box statistic derivable from an
existing corpus) plus discourse-adjacency and coreference-chain position as features, gated by whether it beats
a majority-class / adjacency-only floor CI-separated on held-out MAVEN-ERE causal relations.

- **Adjacent brain system:** the narrative-causal-network / construction-integration comprehension system
  (Trabasso & van den Broek 1985; Kintsch 1988; Graesser, Singer & Trabasso 1994; Singer & Halldorson 1992),
  neurally supported by the generation+integration dissociation (Mason & Just 2004) and right-hemisphere global-
  coherence dependency (Beeman lesion work, background-confirmed only). **PINNED status: coarse/component-level
  PINNED (fMRI + lesion dissociation that implicit/global causal inference is a separable process from local
  explicit-causal comprehension); NOT pinned at circuit/mechanism level (no "graph-edge-builder" has been
  localized).** This is a materially different confidence profile than the causation typer's force-dynamics
  claim, which is behaviorally well-supported but has ZERO neural evidence for its social extension (Wall 2) --
  here the SEPARABILITY of implicit inference from explicit local processing IS neurally shown, even though the
  edge-scoring mechanism itself is only behaviorally characterized.

- **Cheap decisive test (pre-registered, HARD-PASS/HARD-FAIL):** On the SAME MAVEN-ERE valid split already
  loaded by `exp_generalize_causation_typer_maven_ere_v1.py` (n=9,698 causal relations, 8,139 currently
  UNFIRED by the force typer), build the simplest possible glass-box implicit-inference scorer: causing-event-
  type x effect-event-type co-occurrence rate (an ASER-style selectional-preference statistic, computable
  directly from MAVEN-ERE's own event-type annotations or a background corpus) plus discourse/temporal
  adjacency, scored CAUSE-vs-PRECONDITION on the UNFIRED 83.9% subset against (i) the majority-class floor
  (0.863 per the existing rerun) and (ii) an info-free twin (shuffled event-type pairing, same marginal
  frequencies).
  - **HARD-PASS** (license building the full organ): CI-separated beat of the majority floor on the unfired
    subset, twin losing, with coverage-weighted lift >= +0.05 (half the magnitude that would be needed to flip
    the typer cluster's headline verdict, kept modest because this is a first probe of a genuinely different
    mechanism).
  - **HARD-FAIL** (do not build; implicit narrative causation is event-type-independent / requires deeper
    world-knowledge the co-occurrence statistic cannot approximate): scorer ties or loses to majority floor, OR
    is statistically indistinguishable from its shuffled twin (NOT_SEP by the same convention used throughout
    this ledger) -- in which case the next candidate mechanism to test is discourse-position/coreference-chain
    features alone (a purely structural, non-semantic implicit-causality proxy) before concluding no cheap
    glass-box signal exists.
  - Pre-registered P estimate for HARD-PASS: **0.40** (deflated from a naive ASER-literature-informed prior of
    ~0.55-0.60, per calibration policy, because ASER/CausalBank's precision numbers were measured on their own
    curated extraction pipelines, not on MAVEN-ERE's specific CAUSE-vs-PRECONDITION distinction, which the
    existing rerun already showed is a harder-than-expected discrimination even for the force typer where it
    fires).

---

## Cross-thread synthesis

This closes the same population (MAVEN-ERE causal relations) opened by `exp_generalize_causation_typer_maven_ere_v1.py`
(GENERALIZATION_LEDGER.md row T2a/T2b) and follows the identical rerun grammar used successfully for the
retrieval-interference wall one day earlier (`research_retrieval_interference_load_and_dg_boundary_2026-08-30.md`
in this same problem folder): a headline construction-only win (0.929/1.000 on n=42/40 minimal pairs) does not
transfer to real annotated text, but the honest diagnosis is a SCOPE mismatch (measuring the wrong 84% of the
population) rather than a mechanism failure -- directly parallel to that note's finding that the retrieval-
interference organ was tested on the wrong LOAD AXIS (event-count instead of similar-competitor overlap). Both
walls recommend the same shape of fix: keep the validated-narrow organ scoped to where it is actually valid,
and open a new problem for the complementary mechanism the population actually needs.

## Substrate-product implications

A causation-typing feature built ONLY on the force-dynamic typer would silently fail on 84% of real narrative
causal relations while reporting high confidence on constructed test cases -- exactly the failure mode a user-
facing reading-comprehension or summarization product would hit hardest on real prose (news, fiction) rather
than curated sentences. The fix costs one new organ (implicit causal-edge scorer, cheap glass-box statistic,
no LLM) rather than replacing existing work; the existing force typer keeps its validated niche (explicit
physical-causal predications) and does not need to be torn out.

## Citations (verified count)

- **Verified via live WebSearch/WebFetch this session:** Talmy 1988; Wolff 2007; Wolff & Song 2003; Wolff &
  Barbey 2015; Wolff, Barbey & Hausknecht 2010; Fugelsang, Roser, Corballis, Gazzaniga & Dunbar 2005; Roser,
  Fugelsang, Dunbar, Corballis & Gazzaniga 2005; Blakemore, Boyer, Pachot-Clouard, Meltzoff, Segebarth & Decety
  2003; Saxe & Kanwisher 2003; Frith & Frith 2006; Blos, Chatterjee, Kircher & Straube 2012; Straube, Wende,
  Nagels, Blos, Stratmann, Chatterjee & Kircher 2013/2014; Wende, Nagels, Stratmann, Chatterjee, Kircher &
  Straube 2015; Teo, Bergey & Gerstenberg 2026; Trabasso & van den Broek 1985; Trabasso & Sperry 1985; van den
  Broek 1990; Graesser, Singer & Trabasso 1994; Myers, Shinjo & Duffy 1987; Zwaan & Radvansky 1998; Singer &
  Halldorson 1992; Singer et al. 2015; Kintsch 1988; Haviland & Clark 1974; Schank & Abelson 1977; ASER (Zhang
  et al.); COPA (Roemmele, Bejan & Gordon 2011); CausalBank (Li et al.); ATOMIC/Event2Mind (Sap et al. 2019);
  MAVEN-ERE (Wang et al. 2022); Hu & Walker 2017; Mason & Just 2004; Michotte / Scholl & Tremoulet 2000;
  Kominsky, Strickland, Wertz, Elsner, Wynn & Keil 2017; Kominsky & Scholl 2020. **Count: 33 distinct
  citations independently verified this session across the two completed lanes.**
- **Cited from background knowledge only, NOT independently verified this session (treat as unconfirmed until
  re-scanned):** Beeman 1993/2000 (secondary-source-cited only); Griffiths & Tenenbaum causal-support Bayes
  nets; Waldmann causal-model theory; Cheng 1997 power PC theory; Sloman's *Causal Models*; Fugelsang & Dunbar
  2005 "Brain-based mechanisms underlying complex causal thinking" (distinct paper from the verified Fugelsang
  et al. 2005 *Cognitive Brain Research* causal-PERCEPTION paper -- do not conflate the two); Feng et al. 2021
  ALE meta-analysis; Ahn & Kalish; PDTB implicit-relation-rate exact percentage (background figure, discourse-
  relations-general, not causal-specific).
- **Lane status:** Lane A (Bayesian causal-structure-inference angle) was dispatched but returned only a
  dispatch acknowledgment, not synthesized findings, before this note was due. Per Director instruction this
  note was written without blocking on it. Agent ID `a816c8a8d3f0ea448` may still hold completed sub-lane
  output recoverable via SendMessage if the Director wants the Bayesian-structure slice filled in as a
  follow-up rather than re-dispatched fresh.

## TLDR

We asked why our causation-detector, which looked great on hand-built test sentences, almost completely missed
real causal relationships in a large independently-labeled dataset. Answer: it was built to read one specific
kind of sentence (an explicit action-verb describing one physical event pushing on another, like "the ball
broke the window"), but most real causation in stories and news is NOT written that way -- it is two separate
events placed near each other with the causal link left for the reader to infer (an attack happens, then a
city falls, with no word connecting them). The brain has a well-documented, different mechanism for that kind
of inference -- it builds a network of "what led to what" across a whole story, not by reading force out of a
single verb. Separately, when causation is about persuading or influencing someone (rather than pushing an
object), the brain leans on its people-reading system, not its physics system, though the two share some
common machinery. Our detector is not broken; it is just aimed at a narrow 16% slice of the problem. The right
fix is not to throw it out but to add a second, complementary tool for the other 84%.

## QUESTIONS

None.

## NEXT STEPS

1. Decide whether to re-run Lane A (Bayesian causal-structure angle: Griffiths & Tenenbaum, Cheng, Waldmann,
   Feng et al. 2021 ALE meta) as a narrow follow-up, or accept the WALL 1 verdict as resting on the already-
   verified narrative-causal-network + Mason & Just / Beeman evidence (sufficient on its own).
2. Dispatch the named next problem (`narrative_causal_graph_missing_implicit_inference_organ`) with the
   pre-registered cheap decisive test above, reusing the existing MAVEN-ERE loader from
   `exp_generalize_causation_typer_maven_ere_v1.py`.
3. Update `BRAIN_FOUNDATIONAL_AUDIT.md` / the GENERALIZATION_LEDGER per the AUDIT UPDATE language already
   proposed in SOLVED.md, adding the refinement that the typer is narrowly-valid (explicit physical predication)
   rather than a dead end.
