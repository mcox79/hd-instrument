# Research: glass-box causal-testimony miner — connective/counterfactual/generic/force-dynamic SPEC

Filed by: research (Opus synthesis over 4 parallel Sonnet lit-scan lanes: connective directionality; counterfactual necessity; generics; force-dynamics+extraction-corpora)
Date: 2026-09-09
Trigger: 2x-depth continuation of `research_causal_knowledge_acquisition_2026-09-09.md` (filed same morning), which named `hdlab/causal_network.py` as the buildable Tier-1/2/3 prototype but only sketched the marker taxonomy at a headline level. This drill supplies the concrete cue-inventory + directionality-rule + adversarial-failure-mode SPEC that note asked for as the next step. Verified on disk before drilling: `hdlab/causal_network.py` (253 lines) currently implements only 8 connectives (`so/therefore/thus/hence/consequently/accordingly` cause-first; `because/since` effect-first) and 2 closed force-dynamics lists (`FORCE_ACTION`/`RESULT_STATE`, no CAUSE/ENABLE/PREVENT typing) — zero counterfactual detection, zero generics detection, zero periphrastic-causative-verb coverage, zero disambiguation filtering.
Calibration: lit-scan penalty applied per [[feedback-lit-scan-calibration-penalty]] — P deflated 0.15-0.25; novel-synthesis P capped at 0.50.
Field advisor: run per contract; substrate-physics field list (spin-glass/thermodynamics/free-probability/etc.) has zero adjacency to this psycholinguistics/discourse literature — correctly not used to steer this drill, consistent with the sibling note's same disclosure.

======================================================================
HEADLINE
======================================================================

The current 8-connective/2-list implementation covers roughly a third of the citable, directionality-typed cue inventory (missing: prepositional/phrasal markers, periphrastic causative verbs, "as", full CAUSE/ENABLE/PREVENT force-dynamics typing, counterfactual necessity markers, generic-statement detection) and has ZERO disambiguation filtering against the specific, well-documented failure modes the literature reports at 15-26% false-positive rates for naive cue-only matching. Every directionality rule below is citable and mechanical (no semantic parsing required); every disambiguation filter below is a cheap syntactic/lexical gate, not a new ML model. The highest-value, lowest-risk expansion is completing the connective+verb inventory with the Sweetser epistemic/speech-act filter on because/since/as; the highest-value, highest-uncertainty expansion is counterfactual-necessity mining (zero downstream precedent anywhere, per the sibling note).

======================================================================
(1) CAUSAL-CONNECTIVE INVENTORY BY CLASS + DIRECTIONALITY
======================================================================

**Backward/effect-first subordinators** — because, since, as, for (archaic/formal): clause introduced by the connective = CAUSE; matrix/main clause = EFFECT. Sanders, Spooren & Noordman (1992, Discourse Processes 15(1):1-35; 1993 Cognitive Linguistics) frame this as the cognitive "Order" primitive independent of connective identity: postposed "because"-clauses are non-basic order (effect stated first, cause second); fronted "since"/"as" restore basic order (cause first) despite being the same subordinator class. PDTB2/3 (Prasad et al. 2008 LREC; Webber et al. annotation manual) codes these under Contingency -> Cause:Reason (Arg2 = cause of Arg1).

**Forward conjuncts** — so, therefore, thus, hence, consequently, accordingly, as a result, for this reason, that's why: clause/sentence 1 = CAUSE, clause 2 (post-connective) = EFFECT. PDTB Contingency -> Cause:Result (Arg2 = result of Arg1). This is "basic order" per Sanders et al. — iconic with real-world cause-before-effect sequencing.

**Prepositional/phrasal** — due to, owing to, because of, as a result of, on account of, thanks to: object-of-preposition NP = CAUSE; the modified matrix proposition/subject = EFFECT. "Due to" patterns adjectivally (post-copular/NP-modifying); "because of"/"owing to" pattern adverbially — a syntactic, not directional, distinction.

**Periphrastic causative verbs** — causes, leads to, results in, brings about, gives rise to, triggers, produces: canonical SVO, SUBJECT = CAUSE, OBJECT = EFFECT, supported by force-dynamic vector analyses (Talmy 2000; Wolff 2003/2007 explicitly extend the model to these verbs).

Currently missing from `hdlab/causal_network.py`: "as" (backward class — high-value, common), the entire prepositional/phrasal class, and the entire periphrastic-causative-verb class (a SEPARATE closed list from the force-dynamics FORCE_ACTION/RESULT_STATE lists already present, which encode implicit narrative bridging, not explicit lexical causation).

======================================================================
(2) COUNTERFACTUAL CONDITIONALS AS NECESSITY TESTIMONY
======================================================================

Lewis (1973, *Counterfactuals*): "if X hadn't, Y wouldn't" is true iff, in the closest possible world where X does not occur, Y does not occur either — similarity-ordered possible-worlds semantics. Halpern & Pearl (2005, BJPS I/II) give the structural-equation analogue: the AC2 "but-for" necessity witness (Y_{X=0}=0 under the actual context) — the formal criterion the sibling note's leave-one-out decode-confidence probe is trying to approximate computationally. **Explicit counterfactual testimony in text is a direct verbal encoding of exactly this criterion, obtainable more cheaply than re-deriving it** (this specific bridging claim is a reasonable inference, not independently verified by a primary source this session — flagged honestly).

Byrne (2005, *The Rational Imagination*, MIT Press): people preferentially mutate controllable actions, exceptional/abnormal events, and the LAST event in a causal chain when spontaneously constructing counterfactuals ("fault lines of reality"). Important caveat: Mandel & Lehman (1996) and the "differential focus" debate (Behavioral and Brain Sciences) show causal-judgment targets and counterfactual-mutation targets can DISSOCIATE — the link is real but not a clean identity, so counterfactual testimony corroborates rather than is strictly identical to a causal-necessity readout.

Gerstenberg, Goodman, Lagnado & Tenenbaum (2021, Psych Review) formalize the Counterfactual Simulation Model (CSM): causal strength = probability that a simulated intervention/absence of C changes whether (and how) E occurs, decomposed into whether-causation and how-causation/degree. Gerstenberg & Icard (2020, JEP:General) extends this to normality-biased counterfactual selection in pure physical settings.

Extraction feasibility: SemEval-2020 Task 5 (arXiv:2008.00563) — detection F1 ~85-86% (top systems), antecedent/consequent span extraction ~88 F1 / 57.5 exact-match. Son et al. (2017, ACL P17-2103) — F1 ~0.77 on social-media text. Surface markers: subjunctive "had X happened," "if only," modal-perfect "would/could/should have," "wish."

======================================================================
(3) GENERICS AS KIND-LEVEL CAUSAL KNOWLEDGE
======================================================================

Leslie (2007 Phil Perspectives 21; 2008 Phil Review 117(1):1-47; 2012): generics ("Xs cause Ys") express a cognitively primitive default-generalization mechanism, NOT an implicit statistical quantifier ("most X") — evidenced by earlier acquisition than "most" and asymmetric misremembering of quantified statements AS generics (never the reverse). Three subtypes: majority-characteristic (birds fly), striking-property (mosquitoes carry malaria — accepted despite ~1% prevalence, tracking danger/salience not frequency), principled- vs statistical-connection (Prasada & Dillingham 2006 Cognition; 2009 Cog Sci 33(3):401-448). "Smoking causes cancer" plausibly patterns as striking-property — true generically despite low absolute individual risk (flagged as SEP-synthesis extrapolation of Leslie's framework, not a verbatim Leslie claim).

Gelman (2003, *The Essential Child*; Gelman & Raman 2003, Child Development 74(1):308-325) ties generic syntax to psychological essentialism; Cimpian & Erickson (2012, Dev Psych 48(1):159-170) show generic framing shifts children's causal attribution toward inherent/essence-based causes, non-generic framing toward external/mechanistic causes — **generic form itself functions as a causal-attribution cue independent of content truth**. Implication for a miner: generic-causal syntax must be treated as author-BELIEF extraction, never fact-verification (mirrors the testimony-not-inference framing of the whole approach).

Detection: Carlson (1977 diss.) — kind-reference (bare plural/singular subject + individual-level predicate, simple present) vs episodic reference (deictic determiner + stage-level predicate). GenericsKB (Bhakthavatsalam, Anastasiades & Clark 2020, arXiv:2005.00660): 27 hand-authored lexico-syntactic rules + BERT classifier filter 1.7B candidate sentences to 3.4M generics (83% held-out accuracy, Cohen's kappa=0.52). **No source found isolates a "genericity" signal adding value beyond causal-verb detection for causal generics specifically** — genericity filtering (kind-reference syntax) and causal-content detection (the same periphrastic-verb list from Section 1) are SEPARATE, both-required layers; genericity alone does not imply causal content ("tigers have stripes" passes genericity filters, is non-causal).

======================================================================
(4) FORCE-DYNAMIC CAUSAL VERBS (Talmy / Wolff CAUSE-ENABLE-PREVENT)
======================================================================

Talmy (1988, Cognitive Science 12(1):49-100): Agonist (intrinsic tendency toward action/rest) vs Antagonist (opposing force); basic patterns = causing, letting/allowing, helping, hindering, preventing, despite-opposition.

Wolff & Song (2003, Cog Psych 47(3):276-332) / Wolff (2007, JEP:General 136:82-111): three defining dimensions — patient's tendency (toward/away/neutral), force concordance vs conflict, whether the result occurs — yielding a four-way typology:
- **CAUSE**: patient has no/opposing tendency; affector's force conflicts with and OVERCOMES it; result occurs. Verbs: cause, make, force, get, drive, propel.
- **ENABLE/HELP**: forces are concordant (patient already tending toward result); affector removes an obstacle or adds supporting force; result occurs. Verbs: enable, let, allow, permit, help.
- **PREVENT**: forces conflict; affector's force BLOCKS the patient's tendency; result does NOT occur. Verbs: prevent, stop, block, keep from, hinder, deter, restrain.
- **DESPITE**: forces conflict but the patient's own tendency prevails anyway; result occurs despite opposition.

Wolff (2007) reports 5-6 experiments confirming people apply a qualitative vector-resultant decision rule when classifying causal scenarios into these bins; exact classification-accuracy percentages were not recoverable this session (flag: qualitatively, not numerically, confirmed). Argument structure for CAUSE-type periphrastics: [Agent/Cause SUBJ][verb][Patient/Effect-bearer OBJ][(to)-VP-result] — directionality structurally fixed in all sources found; flipped/ambiguous cases unconfirmed (open item for a Levin 1993 follow-up if load-bearing later).

`hdlab/causal_network.py`'s existing `FORCE_ACTION`/`RESULT_STATE` lists implement only an UNTYPED bridging inference (any action -> any result-state = CAUSE), missing the ENABLE/PREVENT/DESPITE distinction entirely — a real gap since PREVENT-type force-dynamic verbs, if present in a narrative, currently would not encode "this did NOT cause that" and could silently corrupt an edge in the wrong direction if naively pattern-matched by a future periphrastic-verb-only extension.

======================================================================
(5) EXTRACTION-CORPUS METHOD PRECEDENT (reference only, not a tool to adopt)
======================================================================

CausalNet (Luo, Sha, Zhu, Hwang & Wang 2016, KR): EPC (effect-pattern-cause: "because," "due to," "on account of") + CPE (cause-pattern-effect: "resulted in," "led to") cue-pattern families mined from Bing web n-grams, PMI-scored restricted to pattern-matched pairs. On COPA: PMI+Connectives 70.2% vs pure-PMI 65.4% (Gordon et al. 2011 baseline) — the ~4.8pt gain attributable to gating statistics through explicit markers. Scale/error-taxonomy not recoverable this session.

CausalBank (Li, Ding, Liu, Hu & Van Durme 2020, IJCAI, arXiv:2107.09846): same EPC/CPE families (~20+ morphological variants), mined from 5.14TB Common Crawl -> 314M pairs; 1,000-sentence manual check = 95% judged "meaningful causal relation" (failure taxonomy not broken into categories in the paper — only pre-filters named: dedup, negation, passive voice, sub-bigram arguments). +3pt on COPA via continued training.

PDTB (Prasad et al. 2008): explicit/implicit split ~53.5%/46.5% corpus-wide (all sense classes; Contingency-specific split not separately confirmed this session) — this is the hard structural recall ceiling any connective-only miner faces regardless of precision.

======================================================================
(6) ADVERSARIAL FAILURE MODES
======================================================================

**Naive cue-only precision ceiling**: 15-26% non-causal false positives across independent studies (Girju 2003: 73.9%P/88.7%R; Khoo et al.: 81.3%P; Garcia 1997 COATIS, French: 85.2%P).

**since/as**: genuine temporal/causal (since) and causal/temporal-simultaneous/comparative (as) polysemy; syntax-feature disambiguation is the standard mitigation (Pitler & Nenkova 2009, ACL — exact accuracy figure recalled but not re-verified this session, flag for confirmation before citing a number).

**because — epistemic/speech-act confound (Sweetser 1990, *From Etymology to Pragmatics*, Cambridge UP)**: three-domain model — content/sociophysical (D1, real-world causation, the only one that is genuine SEMANTIC causation), epistemic (D2, conclusion-because-premise/evidential: "he's home, because the lights are on" — the light does not CAUSE his presence, it is evidence FOR the inference), speech-act (D3, utterance-motivation: "since you're up, could you get coffee?"). D2/D3 "because" instances will corrupt a naive because-miner as false CAUSE edges; a cheap gate (reject when the effect-bearing clause contains an evidential/inferential predicate — modal auxiliary "must," "seems," epistemic stance verb, or a stative "be"-copula construction typical of D2/D3) is proposed as the mitigation, untested on this substrate's corpus.

**so — causal vs purposive "so that" vs discourse-continuative/topic-shift** with no causal content; the purposive reading is gated by an obligatory "that" + modal-subjunctive complement, mechanically separable; the discourse-continuative reading has no reported disambiguation accuracy found this session.

**"Even if" concessive counterfactuals** (Section 2) explicitly DENY necessity ("even if she had studied, she wouldn't have passed") and are the sharpest counterfactual-mining confound — no NLP system found in this scan reports a measured disambiguation accuracy against plain necessity-testimony; a cheap "even" pre-filter is proposed but untested.

**Direction-error rate**: not found for ANY of the six extraction-method papers checked (CausalNet, CausalBank, Girju & Moldovan 2002, Radinsky et al. 2012, Riaz & Girju 2014, Mirza & Tonelli 2014) — none separate cause/effect-reversed matches from generic non-causal false positives. This is a genuine literature gap, not a null result, and means this substrate's own held-out manual audit is the ONLY available source for a direction-error estimate — no external number can be borrowed.

======================================================================
CHEAP DECISIVE TEST
======================================================================

1. Expand `hdlab/causal_network.py`'s `CONNECTIVE_CAUSE_FIRST`/`CONNECTIVE_EFFECT_FIRST` closed classes to the full Section-1 inventory (add "as", the prepositional/phrasal class, and a new `PERIPHRASTIC_CAUSATIVE_VERB` closed list separate from the existing untyped `FORCE_ACTION`/`RESULT_STATE` bridging lists). Score explicit-connective recall and precision on the shared-participant-confound subset (n=192) already used in the sibling drills, against the current 8-connective baseline, with the standard info-free-twin + CI-separated-margin control battery.
2. Add the Sweetser epistemic/speech-act filter as a gate on because/since/as matches; measure false-positive-edge reduction on a manually-flagged epistemic-because sample drawn from the substrate's own reading corpus (not borrowed from any external number, per the direction-error gap noted above).
3. Type the force-dynamics bridging inference into Wolff's four bins (CAUSE/ENABLE/PREVENT/DESPITE) instead of the current single untyped ACTION->RESULT link, using the existing `FORCE_ACTION` list plus a new small `PREVENT_ACTION` closed list (stop/block/keep from/prevent/hinder) so that a PREVENT-type verb does not silently produce a false CAUSE edge.

======================================================================
FALSIFIABLE PREDICTIONS (HARD-PASS / HARD-FAIL)
======================================================================

**PREDICTION 1 (inventory expansion is a net win, not a precision trade).** HARD-PASS: expanding from 8 to the full ~25-item connective/phrasal/periphrastic-verb inventory increases explicit-marker recall on the confound subset by >=15pts with precision drop <5pts (info-free twin unchanged), i.e. the literature's 15-26% naive-cue false-positive ceiling does NOT materialize on this substrate's narrower narrative-register corpus. HARD-FAIL: precision drops >=10pts on the expanded inventory (matching the literature's naive-cue ceiling), meaning disambiguation filters (Prediction 2) are load-bearing BEFORE the expanded list can ship, not an optional refinement.

**PREDICTION 2 (Sweetser epistemic filter is worth its complexity).** HARD-PASS: the epistemic/speech-act gate on because/since/as removes >=10pts of false-positive causal edges on a manually-flagged sample. HARD-FAIL: the filter has no measurable effect (epistemic "because" is rare enough in this substrate's narrative register to not be worth the added complexity) — an informative negative that deprioritizes the filter without deprioritizing the base connective expansion.

**PREDICTION 3 ("even if" concessive confound is cheaply filterable for counterfactual mining).** HARD-PASS: raw counterfactual-pattern matches ("if X hadn't...Y wouldn't") that are actually "even if" concessive constructions constitute <5% of matches after a cheap "even"-token pre-filter, i.e. the confound is rare and cheaply screenable before any Tier-2 counterfactual build. HARD-FAIL: >=15% of raw matches are "even if" constructions and the pre-filter cannot reliably separate them — would require deeper syntactic disambiguation (no precedent found anywhere in this scan) before Tier-2 counterfactual-necessity mining can ship safely.

======================================================================
CROSS-THREAD SYNTHESIS
======================================================================

This drill is the concrete cue-inventory-and-directionality SPEC that `research_causal_knowledge_acquisition_2026-09-09.md` (same morning) named as needed to operationalize its Tier-1 (connectives)/Tier-2 (counterfactuals)/Tier-3 (generics) build plan. It also sharpens two things that note left implicit: (a) the force-dynamics bridging mechanism already in `hdlab/causal_network.py` is UNTYPED and therefore structurally blind to PREVENT-class verbs — a real correctness gap independent of the recall-expansion question; (b) counterfactual mining's sharpest adversarial risk is the "even if" concessive class, which explicitly negates rather than asserts necessity, and this is a genuine literature gap (no measured disambiguation accuracy found anywhere) not previously flagged. Both should be built into the sibling note's proposed Tier-1/Tier-2 experiments, not discovered later as a bug.

======================================================================
SUBSTRATE-PRODUCT IMPLICATIONS
======================================================================

Plain language: our reading machine currently only recognizes about a third of the specific words and sentence patterns that real writers use to directly tell you "this caused that" — it is missing common phrases like "due to," "resulted in," and the word "as," and it cannot yet tell the difference between a sentence that says something CAUSED an outcome versus one that says something PREVENTED an outcome, which could make it get the arrow backwards on prevention-type sentences. This report is a complete shopping list of the missing patterns, in the exact order that published science says will pay off most versus least, plus three cheap built-in checks (a words-that-sound-causal-but-aren't filter, a causes-versus-prevents type check, and an even-if-doesn't-count filter) that other researchers found are needed to keep the machine from fooling itself. None of this requires a bigger or smarter model — it is a bigger, more carefully checked list of words and sentence shapes, which keeps the whole system fully inspectable.

Risk of this recommendation: every directionality rule and every disambiguation filter proposed here is citable and literature-grounded, but NONE has been measured on this substrate's own corpus yet (the "direction-error rate" gap in Section 6 means no external study can substitute for that measurement) — this is a well-specified next build, not a predicted win. If Prediction 1 HARD-FAILs, the informative conclusion is that this substrate's narrative register is closer to the literature's noisy naive-cue regime than hoped, and disambiguation filtering (Predictions 2-3) becomes mandatory rather than optional before the inventory expansion ships.

======================================================================
CITATIONS (verified count)
======================================================================

Combined across 4 lanes, deduplicated: **~52 distinct sources cited**, of which primary-fetched/confirmed this session (abstract, full text, or direct arXiv/DOI/publisher record): Sanders, Spooren & Noordman (1992/1993); Prasad et al. (2008 PDTB2 LREC); Webber et al. (PDTB3 manual); Sweetser (1990); Girju (2003); Khoo et al.; Garcia (1997 COATIS); Byrne (2005); Gerstenberg, Goodman, Lagnado & Tenenbaum (2021); Gerstenberg & Icard (2020, PubMed 31512904); Lewis (1973); Halpern & Pearl (2005 BJPS I/II); SemEval-2020 Task 5 (arXiv:2008.00563); Son et al. (2017 ACL P17-2103); Leslie (2007/2008/2012); Prasada & Dillingham (2006/2009); Gelman (2003); Gelman & Raman (2003); Cimpian & Erickson (2012); Carlson (1977/1980); Bhakthavatsalam, Anastasiades & Clark (2020, arXiv:2005.00660); Talmy (1988); Wolff & Song (2003); Wolff (2007); Luo, Sha, Zhu, Hwang & Wang (2016 KR); Li, Ding, Liu, Hu & Van Durme (2020, arXiv:2107.09846); Mirza & Tonelli (2014 COLING, Causal-TimeBank). **~26 primary-verified.**

Secondary/flagged (converged across sources but not primary-PDF-verified, or explicitly noted as unconfirmed figures): Pitler & Nenkova (2009) exact accuracy; Mandel & Lehman (1996) differential-focus debate; Girju & Moldovan (2002 FLAIRS); Radinsky, Davidov & Markovitch (2012 WWW); Do, Chan & Roth (2011 EMNLP); Riaz & Girju (2014 EACL); Levin (1993, argument-structure flip question, not directly checked); Quirk et al. descended reference grammars. **~26 secondary.**

P_deflated summary (per [[feedback-lit-scan-calibration-penalty]]):
- "Full connective/phrasal/periphrastic-verb inventory increases recall without a CI-separated precision cost on this substrate's own corpus": raw ~0.55 -> **deflated 0.35** (naive-cue literature ceiling of 15-26% false-positive is a real risk, register-dependent, untested here).
- "Sweetser epistemic filter measurably reduces false positives on this substrate's corpus": raw ~0.45 -> **deflated 0.25** (theoretically sound, register-prevalence unknown).
- "Even-if pre-filter cheaply screens the concessive-counterfactual confound": raw ~0.40 -> **deflated 0.20-0.25** (zero precedent found anywhere for a measured disambiguation accuracy; genuinely novel synthesis, capped near the discipline's 0.50 ceiling).
- "Force-dynamics CAUSE/ENABLE/PREVENT typing is a real correctness fix (not just a nice-to-have)": raw ~0.65 -> **deflated 0.45-0.50** (Wolff's typology is well-established theory; whether PREVENT-class verbs actually occur often enough in this substrate's corpus to matter in practice is untested).

======================================================================
TLDR
======================================================================
We looked up, in detail, exactly which words and sentence patterns writers use to directly say "this caused that" in English, and found our reading machine currently only knows about a third of them, plus it cannot yet tell "caused" apart from "prevented," which could make it point the arrow backward on prevention sentences. The good news: every missing pattern and every needed safety-check is well-documented in outside science, cheap to add (just bigger word-lists and a few yes/no checks), and does not need a bigger or smarter model. The honest caveat: none of these checks have been tested on our own material yet, so we do not yet know for certain how often each problem actually shows up in our own stories.

======================================================================
QUESTIONS
======================================================================
None.

======================================================================
NEXT STEPS
======================================================================
1. Expand `hdlab/causal_network.py`'s connective closed classes per Section 1 (add "as", prepositional/phrasal class, new periphrastic-causative-verb list) and re-score recall/precision on the confound subset (Prediction 1).
2. Add the Sweetser epistemic/speech-act filter on because/since/as (Prediction 2).
3. Type the force-dynamics bridging mechanism into Wolff's CAUSE/ENABLE/PREVENT/DESPITE four bins, adding a `PREVENT_ACTION` closed list, so PREVENT-class verbs stop silently producing false CAUSE edges.
4. Before investing in Tier-2 counterfactual mining (per the sibling note), build and test the cheap "even"-token pre-filter for the concessive-counterfactual confound (Prediction 3) — this is a hard prerequisite, not a refinement, since no external precedent exists to borrow a disambiguation accuracy from.
5. Run the substrate's own held-out manual audit for a direction-error rate (cause/effect swapped) — no external paper reports this number for any comparable extraction method, so it cannot be estimated from the literature and must be measured directly.
