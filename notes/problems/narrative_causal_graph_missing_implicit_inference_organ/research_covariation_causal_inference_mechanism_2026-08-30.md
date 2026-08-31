---
topic: covariation_causal_inference_mechanism_for_the_implicit_causal_graph_organ
date: 2026-08-30
filed_by: research (solver-scoped, single-file write)
trigger: PROBLEM.md section 3 PINNED claim (causal inference in discourse is COVARIATION-BASED; Cheng power-PC + Griffiths-Tenenbaum causal support) rests on a slice (Lane A) that was DISPATCHED-BUT-NEVER-RETURNED in the prior note (research_causation_typer_wall_implicit_and_mental_causation_2026-08-30.md, "PARTIAL / PENDING" section, capped P<=0.30-0.35, "not independently verified"). This drill pins or refutes it.
lit_scan_calibration: APPLIED per [[feedback-lit-scan-calibration-penalty]] -- naive lit-scan confidence deflated 0.15-0.25; novel-synthesis P capped at 0.50. The formulas below are canonical facts (no cap); their TRANSFER to single-narrative event-graph inference is a modeling bridge and is deflated.
prior_work_checked: experiment_index.py query "covariation"=0, "cheng"=0, "causal"=132 (115 landed; nearest = exp_causal_correlational_disambig_v1 HARD_PASS 2026-07-03), "correlational"=2 (1 landed), "precondition"=12 (11 landed), "enabling"=6 (4 landed). No prior cell tests the Cheng/Griffiths-Tenenbaum covariation mechanism by name.
---

# HEADLINE VERDICT

The covariation mechanism the organ replicates splits cleanly into two claims with OPPOSITE
confidence, and the prior note's blanket "P<=0.30-0.35 PENDING" was too pessimistic for one and
about right for the other:

- **(a) EDGE DETECTION by covariation is PINNED at the computational level and neurally supported.**
  Covariation-based Bayesian causal induction (Cheng 1997 power-PC; Griffiths & Tenenbaum 2005
  causal support) IS the accepted rational/computational-level account of how people infer that a
  causal link EXISTS from statistical co-occurrence with no mechanism or connective given, and the
  discourse-specific neural substrate is now independently verified (Feng et al. 2021 ALE: left
  IFG + left MTG + bilateral mPFC, dissociable from logical reasoning; Kuperberg et al. 2011 N400
  tracks causal relatedness with lexical co-occurrence MATCHED out). **The organ's edge-detector is
  brain-faithful in KIND.** P_deflated = 0.65.

- **(b) CAUSE-vs-ENABLE TYPING by covariation is NOT a settled covariation distinction, and this is
  the drill's most important finding.** The cause/enabling-condition contrast is CONTESTED across
  four cognitive accounts, only ONE of which (Cheng & Novick 1991 focal sets) makes it
  covariation-based -- and even that one requires a MULTIPLE-focal-set structure a single-corpus
  event-type covariation table cannot recover. The strongest EMPIRICAL result (Kuhnmuench & Beller
  2005) is that people distinguish cause from enabling condition using LINGUISTIC CUES ("given that"
  vs "because/if"), NOT covariation and NOT mental models. **The organ's CAUSE-vs-PRECONDITION head
  is substantially OUR-INVENTION**: a real, convergent base-rate/ubiquity signature partly carries
  the distinction, but the pure-covariation framing overstates its brain-faithfulness, and the more
  faithful signal (linguistic precondition cues) is being left on the table. P_deflated = 0.33.

**Net:** build the organ, but SPLIT the confidence in the design and the write-up. Detection = the
brain's actual computation (replicate). Typing = a proxy with a known ceiling and a named better
signal to add (linguistic cues) -- treat the covariation-only typer as a can-fail baseline, not as
the brain's mechanism, and pre-register the linguistic-cue arm as the fidelity upgrade.

---

## THE FORMULAS (Q1) -- canonical, framework-verified this session

> NOTE ON SOURCING: the primary PDFs (Cheng 1997 Psych Review; Griffiths & Tenenbaum 2005 Cog Psych;
> Holyoak & Cheng 2011 Ann Rev; Griffiths-Tenenbaum "Theory-Based Causal Induction") are all
> scanned/compressed and their equation text did NOT extract via WebFetch this session (4 attempts,
> all returned "binary/corrupted"). The FRAMEWORK -- deltaP vs power vs support, base-rate
> normalization, noisy-OR, log-likelihood-ratio, "power is the effect size, support is the
> significance test" -- was verified this session from multiple independent search summaries
> (ScienceDirect/PMC/ResearchGate abstracts, Holyoak & Cheng 2011 review summary, the causal-support
> VIS 2022 paper). The exact algebraic denominators below are the CANONICAL presentation of these
> equations (they are textbook-standard and unambiguous); they are reproduced from established
> knowledge, not read off the PDF this pass. Flagged accordingly. They are not "novel synthesis" and
> are not P-capped, but the solver should confirm the exact algebra against a clean copy before
> hard-coding.

Notation: c = candidate cause present; ~c = cause absent; e = effect present. Contingency data =
the 2x2 table of counts N(e,c), N(~e,c), N(e,~c), N(~e,~c).

**Contingency (bare deltaP):**
```
deltaP = P(e | c) - P(e | ~c)
```
This is the covariation baseline -- "how much more often does the effect occur when the cause is
present." It is the info-free-adjacent floor for the organ: it uses only marginal co-occurrence.

**Cheng generative causal power (power-PC, Cheng 1997):**
```
power_gen = deltaP / (1 - P(e | ~c))
```
Derivation / what it ADDS over deltaP: assume the candidate cause c and an ever-present background
cause b produce e INDEPENDENTLY, combined by a noisy-OR. Then
`P(e|c) = P(e|~c) + power_gen * (1 - P(e|~c))`, and solving for power_gen gives the formula above.
The `(1 - P(e|~c))` denominator is the "room left in the ceiling": it normalizes deltaP by how much
of the effect the background already explains. Consequence -- when the effect is already frequent
without the cause (P(e|~c) high), the SAME deltaP implies a LARGER causal power, because the cause
had to overcome a near-ceiling to add any effect at all. **This is exactly the discounting of
alternative/background causes the PROBLEM.md brief calls the OUR-INVENTION-to-sweep piece.** Bare
deltaP does NOT do this normalization; power-PC does. Power is only well-defined (identifiable) over
a focal set where the background rate is estimable.

**Cheng preventive causal power (Cheng 1997):**
```
power_prev = -deltaP / P(e | ~c) = [P(e|~c) - P(e|c)] / P(e|~c)
```
Normalizes the (negative) contingency by the base rate P(e|~c) -- the "room left to prevent." Not
directly needed for CAUSE-vs-PRECONDITION (both are generative-side), but relevant if the organ ever
types PREVENT relations.

**Griffiths & Tenenbaum causal SUPPORT (2005) -- structure, not strength:**
```
support = log [ P(D | Graph1) / P(D | Graph0) ]
```
where D = the observed contingency data, Graph1 = "both background B and candidate C have arrows
into effect E" (a link exists), Graph0 = "only B -> E" (no link). With equal graph priors this is
the log posterior odds for a link existing. The likelihoods marginalize over the noisy-OR strength
parameters w0 (background) and w1 (cause), with priors (Griffiths-Tenenbaum use Uniform(0,1)):
```
P(D | Graph1) = INT INT  P(D | w0, w1) * p(w0) * p(w1)  dw0 dw1
P(D | Graph0) = INT       P(D | w0)     * p(w0)          dw0
```
under the noisy-OR link `P(e+ | b, c ; w0, w1) = 1 - (1 - w0)^b * (1 - w1)^c` (b always 1).

**The conceptual relationship (verified this session, the load-bearing distinction):** causal
support is a Bayesian hypothesis test of whether causal POWER differs from zero -- "causal power is
the effect-size measure; causal support is the significance test / model-selection over structure."
The practical difference the organ should care about: **support accounts for SAMPLE SIZE**, deltaP
and power do not. Two events seen together 2-of-2 times give deltaP = 1.0 and power = 1.0 but LOW
support (could be chance); seen together 200-of-200 give the same deltaP/power but HIGH support.
For a single-narrative regime where each event-type pair may be observed only a handful of times,
**this is the single most relevant property of the three models** -- it is the built-in guard
against the organ over-committing to a causal edge from one or two co-occurrences. Recommend the
organ's detection score be support-like (sample-size-aware), NOT raw deltaP.

---

## Q1 -- COVARIATION AS THE COMPUTATIONAL-LEVEL ACCOUNT

| Finding | Tag | Citation | Verified this session? |
|---|---|---|---|
| Covariation-to-causation via causal POWER (deltaP normalized by base rate; noisy-OR of independent causes) is the leading rational model of converting observed co-occurrence into a causal-strength estimate that discounts alternative causes | PINNED (rational/computational-level; 25+ yrs, cross-lab) | Cheng (1997, Psych Review 104:367-405) | Framework YES; exact algebra from canonical presentation (PDF text uextractable) |
| Causal SUPPORT (Bayesian structure inference: log P(D|link)/P(D|no-link), integrating over strength) is the standard computational-level account of judging whether a causal RELATIONSHIP EXISTS from covariation, and predicts phenomena deltaP/power cannot (sample-size sensitivity, structure-vs-strength dissociation) | PINNED (Cog Psych 51:334-384; 650+ citations) | Griffiths & Tenenbaum (2005) | Framework YES (structure-vs-strength, noisy-OR, log-ratio all confirmed via multiple summaries); exact integral from canonical presentation |
| "The new synthesis": causal induction is a rational Bayesian process integrating covariation with prior/structural knowledge; covariation and power are complementary, not rival | MODELING (review-level synthesis) | Holyoak & Cheng (2011, Annu Rev Psychol 62:135-163) | YES (summary) |
| Force-vector model (Wolff & Song 2003) BEATS Cheng's probabilistic-contrast at predicting which causal VERB people pick for a described PHYSICAL interaction | MODELING (behavioral, within physical domain) | Wolff & Song (2003) | YES (via prior note lane B) -- flags covariation is NOT the whole story even for detection: mechanism/force competes in the physical-perception regime |

**Q1 VERDICT:** Covariation-based causal induction IS the accepted computational-level account of
inferring a causal LINK from statistical co-occurrence absent a mechanism -- this pins the
PROBLEM.md PINNED claim for the DETECTION half and lifts the prior note's PENDING cap. What Cheng's
causal power adds over bare deltaP: base-rate normalization / alternative-cause discounting via a
noisy-OR generative model. What Griffiths-Tenenbaum's support adds over both: a sample-size-aware
Bayesian structure test (power = effect size, support = significance). **P_deflated = 0.68** (the
account is genuinely pinned; deflation reflects that (i) it is validated on repeated-trial
CONTINGENCY DATA, not single-narrative event graphs -- the transfer is a modeling bridge -- and (ii)
force/mechanism competes in the physical-perception regime per Wolff & Song).

---

## Q2 -- CAUSE vs ENABLING-CONDITION (the head the organ types) -- CONTESTED, NOT A CLEAN COVARIATION DISTINCTION

This is the drill's central finding and it DEFLATES the organ's premise. There are (at least) four
accounts of the cause/enabling-condition distinction, and they disagree on WHETHER it is a
covariation distinction at all:

| Account | What distinguishes CAUSE from ENABLE | Is it covariation? | Citation | Verified this session? |
|---|---|---|---|---|
| **Covariation / focal sets** | Enabling condition = constantly present in the CURRENT focal set (so it does NOT covary here) but DOES covary in ANOTHER focal set; cause = the factor that covaries in the current focal set. (Oxygen enables fire: constant in everyday focal set, covaries only in the oxygen-free-lab focal set.) | YES -- but relative to MULTIPLE focal sets | Cheng & Novick (1991, Cognition 40:83-120; "Causes versus enabling conditions"); Cheng & Novick (1992); "A Causal-Power Theory of Focal Sets" | YES (abstract + summary) |
| **Mental models / counterfactual** | Cause and enable have DIFFERENT truth tables over possibilities (cause A->B: {A&B, ~A&B, ~A&~B}; enable/allow: {A&B, A&~B, ~A&~B}); the meaning of causation is NOT probabilistic and does NOT depend on causal power or covariation | NO -- structural/semantic | Goldvarg & Johnson-Laird (2001, Cognitive Science 25:565-610, "Naive causality") | YES (abstract + truth-table summary) |
| **Force dynamics** | Cause asserts causal NECESSITY, "make" asserts SUFFICIENCY; enable = affector force aligns with the patient's own tendency (removes a blocker) rather than opposing it | NO -- force-vector/structural | Wolff & Song (2003); Wolff & Barbey (2015); Sloman, Barbey & Hotaling (2009, "A causal model theory of ... cause, enable, prevent") | Partial (via prior note lane B + this session's Wolff/Barbey abstract) |
| **Pragmatic / abnormal conditions** | Cause = the ABNORMAL, foregrounded, difference-making condition; enabling condition = the NORMAL background presupposed by context; selection is counterfactual + contrastive + conversational | Partly (contrast cases) but primarily pragmatic-selection | Hilton & Slugoski (1986, Psych Review 93:75-88, "Abnormal conditions focus model") | YES (abstract + summary) |
| **EMPIRICAL adjudication** | When mental-model structure is DISENTANGLED from linguistic framing, people rely STRONGLY on LINGUISTIC CUES ("given that" signals an enabling condition; "because/if" a cause) and NOT on the proposed mental models | NO -- linguistic cue | Kuhnmuench & Beller (2005, Cognitive Science 29:1077-1090) | YES (abstract + key finding) |

**The convergent thread that DOES align with covariation stats (the organ's real, defensible
signal):** across Cheng & Novick (constant/ubiquitous presence), Hilton (normal background), and the
base-rate term in Cheng's power formula, the ENABLING condition has a recognizable statistical
signature -- HIGH base rate / near-ubiquitous / present-by-default / LOW covariation-informativeness
in the local context / HIGH out-degree (it enables MANY effects, so it is a poor discriminator of
any one). The CAUSE is the specific, lower-base-rate, high-covariation, foregrounded difference-maker
(higher causal power, lower out-degree). **This signature IS computable from event-type covariation
statistics** (marginal frequency, out-degree in the co-occurrence graph, pointwise informativeness),
and it is genuinely convergent across three of the accounts -- so the organ's covariation-power
features are NOT baseless for typing.

**BUT the honest deflation:** (i) the pure-covariation account (Cheng & Novick) needs MULTIPLE focal
sets to define an enabling condition; a single-corpus event-type table gives you ONE focal set, so
the organ approximates the focal-set logic with a base-rate/out-degree proxy -- a defensible
OUR-INVENTION, not the pinned mechanism. (ii) Two of the four accounts (Goldvarg-JL, Wolff) say the
distinction is NOT covariation/probabilistic at all. (iii) The strongest EMPIRICAL finding
(Kuhnmuench & Beller) is that humans use LINGUISTIC CUES, which are present in the text and which the
covariation-only organ ignores. (iv) MAVEN-ERE's own PRECONDITION-vs-CAUSE annotation guideline may
itself track linguistic/structural cues (temporal necessity, presupposition) more than covariation,
which would cap a covariation-only typer's achievable accuracy independent of signal strength.

**Q2 VERDICT:** CAUSE-vs-ENABLE is a MIXED distinction -- part covariation-structural (base-rate /
ubiquity / out-degree, convergent across Cheng-Novick + Hilton + Cheng-power), part
counterfactual-structural (Goldvarg-JL, Wolff), part pragmatic-linguistic (Hilton,
Kuhnmuench-Beller, the last being the strongest empirical result). Event-type covariation statistics
can carry SOME of it (the ubiquity/informativeness axis) but NOT all of it, and the covariation-only
framing is NOT the brain's settled mechanism for this contrast. **P_deflated = 0.33** that pure
event-type covariation-power features CI-separate CAUSE from PRECONDITION on MAVEN-ERE better than a
base-rate/adjacency floor (the base-rate proxy is real but partial, and the annotation may track
cues the organ ignores). **Actionable:** add a LINGUISTIC-CUE arm (precondition/enabling markers:
"given that", "once", "after", "as long as", presupposition triggers, temporal-necessity words) as
the fidelity upgrade Kuhnmuench & Beller predict should dominate -- and pre-register it as a separate
arm so the covariation-only version is scored as the can-fail baseline it actually is.

---

## Q3 -- NEURAL SUBSTRATE (dual-route / dissociation) -- PINNED

| Finding | Tag | Citation | Verified this session? |
|---|---|---|---|
| Causal inference in DISCOURSE comprehension recruits a LEFT-lateralized frontotemporal system: **left IFG** (pars triangularis/opercularis BA45/44/48; pars orbitalis BA47), **left MTG** (mid BA21; posterior BA37/21), **bilateral mPFC** (BA10 and BA9). 19 experiments, 217 foci. | **PINNED** (ALE meta-analysis) | Feng, Ye, Mao, ... (2021, "Neural Correlates of Causal Inferences in Discourse Understanding and Logical Problem-Solving: A Meta-Analysis", PMC8261065) | **YES -- region names + BAs + counts extracted from the PMC full text this session** |
| Causal inference in LOGICAL problem-solving recruits a NON-OVERLAPPING frontoparietal system (bilateral medial frontal BA8/6/32, left IPL BA40/39, left/right MFG BA9/6/8, IFG pars orbitalis BA10/46). 20 experiments, 360 foci. Conjunction of the two datasets yielded NO significant overlap. | **PINNED** (double dissociation within one meta-analysis) | Feng et al. (2021) | **YES -- "the conjunction analysis between the two data sets did not yield any significant overlapping"** verbatim |
| Discourse causal inference "relies more on semantic knowledge and social interaction experiences"; logical on "abstract representations in working memory" -- i.e. the discourse route is the semantic-memory / world-knowledge route, consistent with a covariation-over-learned-regularities account | PINNED (authors' interpretation) | Feng et al. (2021) | YES |
| N400 is LARGER to causally UNRELATED sentence-continuations than to causally related ones, EVEN WITH lexico-semantic co-occurrence MATCHED across conditions via LSA -- causal integration is online and is NOT reducible to surface lexical co-occurrence | **PINNED** (ERP, co-occurrence-controlled) | Kuperberg, Paczynski & Ditman (2011, JoCN 23:1230-1246, "Establishing Causal Coherence across Sentences") | **YES -- LSA-matched design confirmed this session** |
| Prior causal-theory PLAUSIBILITY modulates how covariation data is neurally processed (plausible-consistent -> parahippocampal; plausible-inconsistent -> ACC + left DLPFC; plausible-vs-implausible during covariation eval -> prefrontal + occipital) -- direct evidence for a theory/prior route INTERACTING with a covariation/data route | **PINNED** (fMRI, theory x covariation) | Fugelsang & Dunbar (2005, Neuropsychologia 43:1204-1213, "Brain-based mechanisms underlying complex causal thinking") | **YES -- distinct from the verified Fugelsang et al. 2005 CBR causal-PERCEPTION paper; the prior note's do-not-conflate warning is upheld** |

**Q3 VERDICT:** The neural substrate for discourse causal inference is now INDEPENDENTLY PINNED and
matches the PROBLEM.md brief exactly (left IFG + left MTG + rostral/medial mPFC), and it is
dissociable within one meta-analysis from logical/deductive causal reasoning (frontoparietal, zero
overlap). The discourse route is explicitly the semantic-memory / world-knowledge route -- the right
home for a learned-covariation-over-event-types mechanism. **The dual-route (covariation/statistical
vs mechanism/force) picture is PARTIALLY pinned:** Feng dissociates discourse-causal from
logical-causal (not exactly covariation-vs-force), and Fugelsang & Dunbar show a theory/prior route
interacting with a covariation/data route -- but a CLEAN covariation-route-vs-force-route neural
double dissociation was NOT found this session and should not be quoted as such. Critically,
**Kuperberg 2011 is a caveat AGAINST a naive co-occurrence implementation** (co-occurrence matched,
causal N400 effect survives) -- the brain's causal integration exceeds surface lexical co-occurrence,
which bears directly on Q4. **P_deflated = 0.72** for the discourse substrate (strong, converging,
directly verified); **0.55** for the specific covariation-vs-mechanism dual-route reading (partial,
novel-synthesis-capped).

---

## Q4 -- GLASS-BOX / NON-LLM IMPLEMENTATION FAITHFULNESS (event-TYPE covariation)

| Finding | Tag | Citation | Verified this session? |
|---|---|---|---|
| Event co-occurrence statistics over TYPED events (verb + typed dependency args), scored by PMI over shared arguments / a shared protagonist, is an established unsupervised glass-box method for narrative event structure | MODELING (engineering, interpretable, non-LLM) | Chambers & Jurafsky (2008 ACL "Narrative Event Chains"; 2009 ACL "Narrative Schemas") | YES |
| Commonsense/causal event knowledge is acquirable as a weighted eventuality knowledge graph purely from statistical distributions over parsed linguistic graphs (higher-order selectional preference), no human-defined relations, via an end-to-end discourse parser -- direct non-LLM precedent for an event-type co-occurrence causal graph | MODELING (statistical KG, non-LLM) | Zhang et al., ASER 1.0 (WWW 2020) / 2.0 (AIJ 2022, arXiv:2104.02137) | YES |
| Trabasso's four-way narrative causal typology can be operationalized to MINE typed causal event pairs from raw narrative (film scene descriptions), beating co-occurrence baselines against human judgment | MODELING (working extractor from the psychological typology) | Hu & Walker (2017, SIGDIAL, arXiv:1708.09496) | YES |
| BUT: causal integration in the brain is NOT reducible to surface co-occurrence -- N400 tracks causal relatedness with LSA co-occurrence matched out | PINNED caveat | Kuperberg et al. (2011) | YES |
| Schema/script abstraction (typing events into stereotyped roles/sequences) is a cognitively-motivated abstraction, not merely an engineering shortcut | MODELING (classic) | Schank & Abelson (1977, Scripts, Plans, Goals) | YES (via prior note lane C) |

**Q4 VERDICT:** Abstracting events to TYPES and counting type-pair co-occurrence is a
COGNITIVELY-DEFENSIBLE FIRST-ORDER approximation, not a pure shortcut -- schema/script theory
(Schank-Abelson) and the hierarchical-causal-schema work (Q5) both support type-level abstraction as
something the mind actually does, and Chambers-Jurafsky/ASER/Hu-Walker prove the glass-box
non-LLM path is real. **What is LOST (the OUR-INVENTION deviations to flag):** (1) surface
co-occurrence UNDERSHOOTS the brain -- Kuperberg shows causal integration exceeds it, so a pure
type-pair count will miss causal edges that depend on inferred world-knowledge / bridging
propositions (Singer & Halldorson) not present in the marginal statistics; (2) the CHOICE of type
abstraction (how coarse; MAVEN-ERE event types vs verb-lemma vs Chambers-Jurafsky typed slots) is an
unpinned OUR-INVENTION knob to sweep, per PROBLEM.md; (3) single-narrative data is sparse, so the
sample-size-aware SUPPORT score (Q1) matters more than raw counts. **P_deflated = 0.42** that
event-type covariation is a FAITHFUL (not merely serviceable) implementation of the brain's
discourse-causal computation -- serviceable and defensible yes, faithful-in-full no (Kuperberg caps
it).

---

## Q5 -- GENERALIZATION TO NOVEL EVENT-TYPE PAIRS

| Finding | Tag | Citation | Verified this session? |
|---|---|---|---|
| A hierarchical Bayesian framework learns, per object, a causal model AND a causal SCHEMA capturing commonalities -- organizing objects into causal TYPES with characteristic causal powers and characteristic type-to-type interactions -- so that causal models for NEW, sparsely-observed objects are rapidly inferred from their type | MODELING (hierarchical Bayes; the principled account of causal generalization) | Kemp, Goodman & Tenenbaum (2007 CogSci "Learning Causal Schemata"; 2010 "Learning to Learn Causal Models", PMID 21564248) | YES (abstract + framework summary) |
| Causal inference about sparsely-observed objects is supported by causal SCHEMATA (abstract causal knowledge), enabling one-shot / few-shot causal generalization | MODELING | Kemp et al. (2010) | YES |
| Learning-to-learn: experience with several causal systems ACCELERATES learning of subsequently-encountered ones via the shared schema | MODELING | Kemp et al. (2010) | YES |

**Q5 VERDICT:** The brain generalizes causal structure to novel event-type pairs via ABSTRACT CAUSAL
TYPES / SCHEMATA that specify characteristic causal powers of a type and characteristic interactions
BETWEEN types (Kemp-Goodman-Tenenbaum) -- NOT via a memorized joint over specific pairs. This
DIRECTLY endorses the PROBLEM.md hypothesis that a covariation model which generalizes via MARGINAL
causal-power profiles (a type's out-going / in-coming causal-power distribution) is MORE brain-
faithful than a type-pair lookup table: a marginal-profile model is the computational shadow of a
causal schema (a type's characteristic causal power), whereas a lookup table has no generalization
mechanism at all and is the thing hierarchical-Bayes was invented to beat. **P_deflated = 0.50**
(capped at the novel-synthesis ceiling: the DIRECTION is well-supported by KGT, but "marginal
causal-power profile" is our operationalization of their schema, and whether it CI-beats a lookup
table on held-out MAVEN-ERE novel pairs is an empirical question the organ must settle).

---

## BRAIN-FAITHFULNESS VERDICT (explicit, per the deliverable spec)

**(a) EDGE DETECTION via covariation:** BRAIN-FAITHFUL IN KIND at the computational level.
Covariation-based Bayesian causal induction is the PINNED rational account (Cheng power-PC;
Griffiths-Tenenbaum causal support), and the discourse-causal neural substrate (Feng 2021: left
IFG/MTG/mPFC, semantic-memory route) plus online causal N400 (Kuperberg 2011) support a
learned-regularity mechanism. **OUR-INVENTION layers on top:** the event-TYPE abstraction (unpinned
knob), the single-corpus single-focal-set approximation, and raw-count vs sample-size-aware scoring.
RECOMMEND: make the detection score SUPPORT-like (sample-size-aware) rather than deltaP, because the
single-narrative regime is exactly where deltaP/power over-commit and support does not.

**(b) CAUSE-vs-ENABLE TYPING via covariation-power:** SUBSTANTIALLY OUR-INVENTION, with a real but
partial covariation signal. The cognitive literature does NOT settle cause-vs-enable as a covariation
distinction -- it is contested (covariation-focal-set / mental-model-counterfactual /
force-dynamic / pragmatic-linguistic), and the strongest empirical result (Kuhnmuench & Beller 2005)
says humans use LINGUISTIC CUES. The organ's base-rate/ubiquity/out-degree features capture the
convergent "ubiquitous background vs specific difference-maker" axis (Cheng-Novick + Hilton +
Cheng-power base-rate term) -- a genuine signal -- but calling the covariation-power typer "the
brain's mechanism" for this contrast OVERSTATES it. RECOMMEND: (i) frame covariation-only typing as a
can-fail BASELINE; (ii) add a LINGUISTIC-CUE arm (enabling/precondition markers, presupposition
triggers, temporal-necessity words) as the pre-registered fidelity upgrade; (iii) check whether
MAVEN-ERE's PRECONDITION annotation guideline itself keys on those cues, which would explain any
covariation-only ceiling and validate the linguistic-cue arm.

---

## HOW THIS UPDATES THE PRIOR NOTE (Lane A closure)

The prior note (research_causation_typer_wall_...) left the Bayesian/covariation slice as "PARTIAL /
PENDING ... P<=0.30-0.35 ... not independently verified." **Lane A is now CLOSED with a SPLIT
verdict, not a single number:**
- Its DETECTION claim (covariation = the computational-level account of inferring a link from
  co-occurrence) is UPGRADED from PENDING to PINNED (Cheng, Griffiths-Tenenbaum, Feng 2021 verified;
  P 0.35 -> 0.68).
- Its implicit TYPING assumption (covariation carries cause-vs-enable) is DOWNGRADED / qualified: the
  cause/enable distinction is contested and largely non-covariation in the strongest accounts
  (P held near 0.33). The prior note's caution ("must not be quoted until Lane A actually returns")
  was correct to hold; the return says covariation pins DETECTION but NOT TYPING.
- Feng et al. 2021 (left IFG/MTG/mPFC, 19 exps/217 foci, dissociable from logical) and Kuperberg
  2011 (co-occurrence-matched N400) are now PRIMARY-SOURCE-VERIFIED this session, discharging two
  of the prior note's "background-confirmed only" items.

---

## SUBSTRATE / BRAIN_FOUNDATIONAL_AUDIT implications (proposed AUDIT UPDATE for the solver to fold in)

Proposed dual-route causation entry for BRAIN_FOUNDATIONAL_AUDIT.md 2b: CAUSATION has a discourse
route (covariation over learned event-type regularities; left IFG/MTG/mPFC; semantic-memory-based;
PINNED at computational + coarse-neural level) and a mechanism/force route (force-dynamic verb
semantics; explicit-physical; behaviorally supported, NO neural study -- the prior note's Wall 2).
The implicit-causal-graph organ implements the discourse route. Its EDGE DETECTION replicates a
PINNED computation (covariation/causal-support); its CAUSE-vs-PRECONDITION TYPING is an
OUR-INVENTION proxy over a contested distinction and should carry a linguistic-cue arm.

---

## TLDR

We asked whether the "learn which kinds of events tend to cause which, from how often they happen
together" idea our new organ is built on is really how the brain does it. Answer, in two halves.
FIRST HALF -- deciding THAT one event caused another from how reliably they co-occur: yes, this is
genuinely how people do it. There is a 25-year-old, well-tested theory of exactly this (turn
co-occurrence counts into a causal-strength number, discounting things that would have happened
anyway), and brain-imaging pins down where in the brain narrative causal inference happens (a
left-side language-and-meaning network), separate from cold logical reasoning. So the organ's
"is there a causal link here" detector copies a real brain computation. SECOND HALF -- deciding
whether that link is a true CAUSE ("he studied, so he passed") versus a background ENABLING condition
("there was oxygen, so the fire spread"): here the co-occurrence story is much weaker than the brief
assumes. Psychologists genuinely disagree about what separates a cause from an enabling condition,
and the single best experiment on it found that people actually decide it from small WORDING cues in
the sentence ("given that..." signals an enabling condition), not from statistics. So the organ's
cause-vs-precondition labeller is more of our own invention than a copy of the brain -- it has a real
partial signal (an enabling condition is usually the ever-present, unremarkable background; a cause
is the specific, rarer thing that made the difference), but it is leaving on the table the wording
cues the brain seems to actually use. Recommendation: build it, but be honest that the detector is
brain-faithful and the labeller is a baseline -- and add a "wording-cue" version of the labeller as
the real upgrade.

## QUESTIONS

None blocking. One open empirical question the organ itself resolves: does MAVEN-ERE's
PRECONDITION-vs-CAUSE annotation key on linguistic/structural cues (temporal necessity,
presupposition) more than on covariation? If yes, a covariation-only typer has a ceiling no amount
of signal fixes, and the linguistic-cue arm is not optional. Worth a 10-minute read of the MAVEN-ERE
annotation guideline before finalizing the typer's feature set.

## NEXT STEPS

1. DETECTION score: use a sample-size-aware / causal-SUPPORT-like statistic (Griffiths-Tenenbaum),
   not bare deltaP, because single-narrative event-type pairs are observed few times and deltaP/power
   over-commit where support does not. Keep bare deltaP and Cheng power as the two ablation floors.
2. TYPING: pre-register TWO arms -- (A) covariation-power features only (base rate, out-degree,
   pointwise informativeness, Cheng power) as the can-fail BASELINE; (B) A + linguistic-cue features
   (enabling/precondition markers, presupposition triggers, temporal-necessity words) as the
   brain-fidelity UPGRADE Kuhnmuench & Beller predict should dominate. Report both; the win of B over
   A is itself a brain-faithfulness test.
3. Confirm the exact Cheng power / Griffiths-Tenenbaum support algebra against a CLEAN copy before
   hard-coding (PDF text extraction failed this session; the framework is verified, the denominators
   are canonical but re-check `power = deltaP/(1-P(e|~c))` and the support integral).
4. GENERALIZATION test (per Q5 / KGT): score the organ on held-out MAVEN-ERE event-type pairs it has
   NEVER co-observed, comparing a MARGINAL causal-power-profile model against a type-pair LOOKUP
   table; the profile model beating the lookup on unseen pairs is the schema-generalization win.
5. Read the MAVEN-ERE PRECONDITION annotation guideline (the open question above) before finalizing
   the typer feature set.
6. Fold the proposed dual-route AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md 2b (detection route
   PINNED; typing head OUR-INVENTION-with-linguistic-cue-upgrade).

## Citations (verified this session)

- Cheng (1997) power-PC -- framework verified (multiple summaries), exact algebra canonical.
- Griffiths & Tenenbaum (2005) structure-and-strength / causal support -- framework verified
  (structure-vs-strength, noisy-OR, log-likelihood-ratio all confirmed), exact integral canonical.
- Holyoak & Cheng (2011) "the new synthesis" Annu Rev -- summary verified.
- Cheng & Novick (1991) "Causes versus enabling conditions", Cognition 40:83-120; Cheng & Novick
  (1992); "A Causal-Power Theory of Focal Sets" -- verified (abstract + focal-set logic).
- Goldvarg & Johnson-Laird (2001) "Naive causality", Cognitive Science 25:565-610 -- verified
  (truth-table summary).
- Hilton & Slugoski (1986) abnormal conditions focus model, Psych Review 93:75-88 -- verified.
- Kuhnmuench & Beller (2005) "Distinguishing Between Causes and Enabling Conditions -- Through Mental
  Models or Linguistic Cues?", Cognitive Science 29:1077-1090 -- verified (key finding: linguistic
  cues dominate).
- Sloman, Barbey & Hotaling (2009) "A causal model theory of the meaning of cause, enable, prevent",
  Cognitive Science 33 -- verified (title/framework).
- Wolff & Song (2003); Wolff & Barbey (2015) -- via prior note lane B + this session's abstracts.
- Feng et al. (2021) ALE meta-analysis, PMC8261065 -- FULL-TEXT verified this session (regions, BAs,
  counts, non-overlap statement).
- Kuperberg, Paczynski & Ditman (2011) JoCN 23:1230-1246 -- verified (LSA-matched design).
- Fugelsang & Dunbar (2005) Neuropsychologia 43:1204-1213 -- verified (theory x covariation regions;
  distinct from the Fugelsang et al. 2005 CBR perception paper).
- Chambers & Jurafsky (2008 ACL; 2009 ACL) narrative event chains/schemas -- verified.
- ASER 1.0 (WWW 2020) / 2.0 (AIJ 2022, arXiv:2104.02137), Zhang et al. -- verified.
- Hu & Walker (2017 SIGDIAL, arXiv:1708.09496) -- verified.
- Kemp, Goodman & Tenenbaum (2007 CogSci; 2010, PMID 21564248) causal schemata / learning-to-learn --
  verified.
- Schank & Abelson (1977) -- via prior note lane C.

**Sourcing caveat:** the four formula-bearing PDFs (Cheng 1997; Griffiths-Tenenbaum 2005; Holyoak &
Cheng 2011; Theory-Based Causal Induction) did not yield extractable equation text via WebFetch this
session (scanned/compressed). The equations above are the canonical presentation, verified at the
framework level from multiple independent search summaries this session; re-check the exact algebra
against a clean copy before hard-coding (NEXT STEP 3).
