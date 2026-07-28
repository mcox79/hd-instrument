# Research: brain-architecture COMPLETENESS lit-scan for knowledge-based science MC-QA (2026-07-24)

## HEADLINE

The brain's pipeline for answering a grade-school science MC question from memory has **~30 named sub-systems across 11 stages**, but they resolve into only **4 recurring ORGANIZING PRINCIPLES** (parallel constraint satisfaction / settle, spreading activation, attention-gated competition, reward/precision-weighted control) that get re-instantiated at every stage, plus a handful of true discrete PIPELINE STAGES. Cross-referencing this inventory against our current ARC build (per `notes/ingestion_learn_sleep_loop_2026-07-24.md`) shows we have GENUINE analogs for the *encoding/comprehension* and *semantic-memory/settle* systems, but we are **structurally missing exactly the systems the biology uses to escape a dominant-but-wrong surface association** — Badre & Wagner's controlled/strategic retrieval (anterior VLPFC) and post-retrieval competitor suppression (RIF). This is not a new hypothesis: it is the same mechanism class our own diagnostics (29538, the WorldTree surface-trap measurement) already converged on independently. The lit-scan's value is turning "retrieval is the wall" into a **named, buildable primitive** with a concrete discriminator (below).

## Exhaustive component inventory (11 stages, all load-bearing calls made against OUR task: grade 3-9 science MC-QA, glass-box, no LLM at inference)

Legend: **LB** = load-bearing for this task, **PER** = peripheral, **PS** = pipeline stage (discrete), **OP** = organizing principle (continuous/recurring).

### 1. Perception / encoding
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Visual Word Form Area | orthographic letterbox | LB (gate, non-differentiating) | PS | Dehaene 2002; McCandliss/Cohen/Dehaene 2003 |
| Grapheme-phoneme conversion (dual-route) | sublexical decoding | PER (skilled silent reading) | PS (parallel-cascaded internally) | Coltheart 2001 DRC; McClelland & Rumelhart 1981 IA; Plaut et al 1996 |
| Lexical access / mental lexicon | word-form -> stored entry | LB (contact point w/ content words) | PS (locally competitive) | Dell 1986; Marslen-Wilson 1987 Cohort |

### 2. Comprehension -> situation model
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Parsing (syntactic structure) | recover hierarchical structure | LB (non-canonical stems) | PS (fast pass + slow repair) | Friederici 2002/2011; Grodzinsky 2000 |
| Thematic-role assignment | who-did-what-to-whom | LB (cause/effect direction is the whole game) | OP (converges w/ parsing, not sequential-after) | Grodzinsky & Friederici 2012 |
| Lexical-semantic access / WSD | word meaning + sense selection | LB (literal contact w/ stored knowledge) | PS (locally competitive) | Binder et al 2009 (ATL semantic hub meta-analysis) |
| Coreference resolution | link pronoun/reference to antecedent | PER for single-sentence stems, LB for multi-sentence | OP (recruits general ToM/TPJ updating) | Ledoux 2008 |
| **Discourse integration / Construction-Integration (Kintsch)** | construction = generate loose propositional net; integration = parallel constraint-satisfaction settle | **LB -- the crux of the whole task** | **OP, explicitly NOT a pipeline stage (Kintsch was emphatic)** | Kintsch & van Dijk 1978; van Dijk & Kintsch 1983 (textbase vs situation model); Kintsch 1988/1998 |

### 3. Question / goal representation
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| PFC retrieval-goal maintenance | hold "what is being asked" active | LB (without it, retrieval = passive association) | PS | Petrides; Fletcher & Henson 2001 |
| Encoding specificity (Tulving) | cue must reinstate encoded features | LB as a constraint, weaker for semanticized facts | OP | Tulving & Thomson 1973 |

### 4. Memory systems
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Semantic memory (ATL hub-and-spoke) | store of decontextualized facts | **LB -- the core system for this task by definition** | PS + OP (hub always active) | Lambon Ralph; Patterson, Nestor & Rogers 2007 |
| Episodic memory (hippocampus) | context-bound event memory | PER (fact-lookup doesn't need "where I learned it") | PS | Tulving 1972; Squire & Zola |
| Episodic/semantic distinction | routes fact-QA to semantic not episodic system | LB as architecture | OP | Tulving 1972; Squire 1992 |
| CA3 pattern completion | content-addressable recall from partial cue | PER for consolidated facts (per CLS, transferred to cortex); LB only for freshly-learned/degraded cues | OP | Marr 1971; McClelland/McNaughton/O'Reilly 1995 |
| Spreading activation (Collins & Loftus) | cue -> candidate propagation, incl. distractors | **LB -- the actual cue-to-candidate mechanism, and why MC lures work** | OP | Collins & Quillian 1969; Collins & Loftus 1975 |

### 5. Retrieval control -- **the identified gap (see synthesis)**
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Controlled/strategic retrieval (anterior VLPFC) vs automatic/associative | top-down effortful search past the dominant-but-wrong cue-association | **LB precisely when surface association favors a distractor (our surface-trap finding)** | PS (engaged conditionally) | Badre & Wagner 2007; Badre et al 2005 |
| Post-retrieval selection (mid-VLPFC) | adjudicate among simultaneously-active candidates vs the goal | **LB -- direct neural analog of "answering a multiple-choice question"** | PS | Badre & Wagner 2007; Thompson-Schill et al 1997 |
| Relevance-gating | suppress retrieved-but-irrelevant content pre-selection | LB | OP overlapping w/ PS | Badre & Wagner 2007; Jonides & Nee 2006 |
| Competitor suppression / retrieval-induced forgetting | inhibits competing associates so target wins | LB at the moment of competition-resolution (the RIF after-effect is the measurable signature of the same inhibitory act) | OP w/ discrete after-effects | Anderson, Bjork & Bjork 1994; Wimber et al 2015 |

### 6. Reasoning
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Construction-Integration as settle (generalized) | turns activated candidates into one coherent answer | LB | OP | Kintsch 1988/1998; Thagard 1989 ECHO |
| Hippocampal-entorhinal relational memory / transitive inference | combine two facts never linked at encoding | **LB -- WorldTree gold shows ARC needs ~2.5 central facts combined, exactly this signature** | PS | Dusek & Eichenbaum 1997; Preston & Eichenbaum 2013; Behrens et al 2018 |
| Mental simulation / model-based reasoning | imagine scenario/consequence | PER for pure recall, LB for "what happens if" items | PS (optional escalation) | Hassabis & Maguire 2007; Daw et al 2011 |
| Analogy / schema-based reasoning | relational structure-mapping vs surface-feature lure | **LB -- this is literally what separates the correct structural analogy from a designed surface distractor** | PS via OP (settle) | Gentner 1983; Bartlett 1932; Rumelhart 1980 |

### 7. Working memory + attention
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Cowan's ~4-item focus of attention | bounded active set for stem+choices+facts | **LB -- matches our own measured ~2.5-central-fact aggregation load, inside Cowan-4** | OP | Cowan 1988/1999/2001/2005 |
| PFC-basal ganglia gating (PBWM) | selective Go/NoGo load/protect of WM slots | LB -- decides which retrieved fact enters the bounded set | PS implementing OP | O'Reilly & Frank 2006 |
| Biased competition + top-down attention | goal-biased competitive suppression among representations | LB (general mechanism for "the question biases which memories dominate") | OP | Desimone & Duncan 1995 |

### 8. Executive control / method selection
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Basal ganglia Go/NoGo (action selection) | reward-trained commit to a response/strategy | LB (general substrate for method commitment) | PS implementing OP | Frank 2005/2006; Frank, Seeberger & O'Reilly 2004 |
| **ACC conflict monitoring + ERN** | detect co-active incompatible candidates, trigger control | **LB -- this is the escalation trigger; we already have a partial analog (trustworthy-reader gate / feeling-of-knowing AUC 0.885)** | OP | Botvinick, Cohen & Carter 2001/2004 |
| Dual-process (System 1/2) | fast associative default, slow deliberate override | LB (describes recognize-fast vs verify-slow tradeoff) | OP (framing, not a stage) | Kahneman 2011; Evans & Stanovich 2013 |
| Expected Value of Control (EVC) | cost-benefit gate on how much deliberation to allocate | **LB -- the decision of whether to escalate to controlled retrieval** | OP | Shenhav, Botvinick & Cohen 2013 |
| Siegler adaptive strategy-choice | learned, experience-weighted mixture over strategies | LB as the developmental/learning analog of the above | PS operationalizing OP | Siegler 1988; Shrager & Siegler 1998 |

### 9. Decision + metacognition
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Feeling-of-knowing / accessibility (Koriat) | infer confidence from partial-cue accessibility, not direct introspection | **LB -- this is what should gate "trust this retrieval" vs "escalate"** | PS | Hart 1965; Koriat 1993 |
| Metacognitive monitor+control (Nelson & Narens) | object-level/meta-level loop converting certainty into action | LB -- converts confidence into answer/keep-searching/abstain | PS (recurring loop) | Nelson & Narens 1990 |
| Neural confidence readout (rostral/anterior PFC) | dissociable second-order calibration system | LB for trustworthy answering, more peripheral for raw accuracy | PS riding on precision-weighting (OP) | Fleming, Weil, Nagy, Dolan & Rees 2010 |

### 10. Learning / plasticity foundation
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Complementary Learning Systems | hippocampus (fast, pattern-separated) + cortex (slow, interleaved) acquisition of semantic facts | **LB -- the acquisition mechanism for the very knowledge the MCQ probes** | OP (lifetime), gates 10.3 | McClelland, McNaughton & O'Reilly 1995 |
| Dopaminergic reward-prediction-error | trains value/strategy representations from feedback | PER within one answering act; LB for how knowledge/strategy got shaped over schooling | OP | Schultz, Dayan & Montague 1997 |
| Sleep-dependent consolidation / hippocampal replay | offline transfer + abstraction of episodic to semantic | LB for durability/generalization of the knowledge base | **distinct OFFLINE STAGE** | Wilson & McNaughton 1994; Stickgold & Walker 2007 |
| Predictive processing / precision-weighting | brain-wide prediction-error minimization, ACh/NE gain control | LB as architecture (source of the confidence signal in Stage 9), more implicit for narrow MCQ scoring | OP | Rao & Ballard 1999; Friston 2010; Yu & Dayan 2005 |

### 11. Grounding
| System | Role | Call | Type | Key cites |
|---|---|---|---|---|
| Perceptual symbol systems / embodied simulation | concepts as reactivatable sensorimotor traces | **PERIPHERAL, honestly, for narrow MC scoring** (text-pattern-matching can "get away" without it); LB for genuine understanding/transfer | alternative representational substrate, not a stage | Barsalou 1999/2008 |
| Sensorimotor activation during concept processing | motor/visual cortex reactivation for concrete words | PERIPHERAL for abstract science vocabulary (energy, force, cell) specifically | property of representation, not a stage | Pulvermuller 2005 |

## Which are ORGANIZING PRINCIPLES vs PIPELINE STAGES (cross-cutting summary)

Four principles recur across nearly every stage and are NOT localizable to one step:
1. **Parallel constraint satisfaction / settle** (Kintsch CI, ECHO, biased competition, CI-generalized-to-reasoning) -- the single most repeated mechanism in the whole inventory.
2. **Spreading activation over associative/semantic networks** (Collins & Loftus; also the retrieval-propagation substrate for MC distractors).
3. **Attention/reward-gated competition** (biased competition, PBWM Go/NoGo, basal ganglia action-selection, all one family per Frank/O'Reilly).
4. **Precision-weighted prediction/control** (Friston/Yu&Dayan precision-weighting underlies both learning-rate modulation and the confidence signal Stage 9 reads out; EVC is the executive-level instance of the same "how much should this update/escalate cost" computation).

Everything else (VWFA, GPC, parsing, thematic-role assignment as a discrete step, encoding-specificity, anterior/mid-VLPFC retrieval, RIF, transitive inference, mental simulation, Siegler strategy-choice, FOK, CLS acquisition, sleep replay) is a genuine discrete PIPELINE STAGE, engaged conditionally or sequentially.

## What AI/computational systems commonly OMIT (consolidated across all 4 sub-scans)

Ranked by how directly it explains an ALREADY-MEASURED gap in our own system:

1. **No controlled/strategic retrieval distinct from automatic similarity ranking** (Badre & Wagner anterior VLPFC) -- our system's "retrieval" IS spreading-activation/cosine-similarity (automatic), and has no top-down goal-reformulated second pass when the automatic winner is a surface lure. **This is our own diagnosed wall (29537/29538: retrieval dominates, surface-trap lure_rate 0.23 on Challenge).**
2. **No post-retrieval selection distinct from top-1 ranking** (mid-VLPFC) -- top-1-by-cosine collapses "access" and "selection" into one score; the brain keeps these as two functionally distinct steps.
3. **No competitor suppression / RIF analog** -- nothing in our system actively down-weights the dominant (often lure) candidate to let a weaker-but-correct signal win on a second pass.
4. **No ACC-conflict-triggered escalation loop with an action side** -- we HAVE the monitor half (trustworthy-reader gate, feeling-of-knowing AUC 0.885, per 07-24 notes) but no wired escalation to controlled-retrieval-on-conflict.
5. **No signed support-vs-contradict representation in the settle** (already independently found: 29537/29538, CI's key ingredient never fires because our meaning-encoder only represents similarity, never opposition) -- this converges with gap #3: both need a way to actively DOWN-WEIGHT/oppose a currently-dominant node, not just accumulate positive similarity.
6. Lower-priority gaps (present but less load-bearing for THIS task): no separate episodic/semantic memory split (fine, task is semantic); no metacognition distinct from a bare score (partially addressed by ClarifyGate/trustworthy-reader gate); no dopamine-style online RL loop tied to real feedback (addressed structurally by learner-MDL module, different mechanism); grounding absent (USER-deferred, correctly out of scope for MC-QA per the lit-scan's own honest read that grounding is peripheral for narrow multiple-choice scoring).

## Cross-thread synthesis (against our own build, `notes/ingestion_learn_sleep_loop_2026-07-24.md`)

- We HAVE genuine analogs for: Stage 1-2 encoding/comprehension (SituationReader, spaCy-POS predicates, semantic HD encoder = WSD/lexical-semantic access), Stage 4 semantic memory (HD fact store + trust-vetting = a hub-like store), Stage 6 CI-as-settle (SPA bundle accumulation), Stage 7 working memory (role_slot_summarizer Cowan-4 bundle -- explicitly validated against WorldTree's measured ~2.5-central-fact aggregation load, a genuine brain-fit), Stage 9 partial metacognition (ClarifyGate / trustworthy-reader gate), Stage 10 acquisition+sleep (condenser + MDL sleep-generalize loop, VET'd though weak on high-entropy real verbs).
- We are MISSING, specifically, Stage 5 (controlled retrieval + post-retrieval selection + competitor suppression) and the ACTION side of Stage 8's ACC-conflict-escalation loop. Our own 29537/29538 findings ("retrieval is the wall," "CI's contradiction ingredient never fires," "surface-trap lure_rate 0.23") are, in hindsight, ALL explained by this one missing stage-5 primitive: an automatic-only retrieval system has no mechanism to escape a dominant surface-similar-but-wrong candidate. The lit-scan does not open a new direction; it **names and sharpens the direction our own diagnostics already pointed at**, and supplies the two-part mechanism (controlled re-retrieval + inhibitory suppression of the dominant node) as a concrete, biologically-specific pair of primitives to build and test, rather than a vaguer "improve retrieval."

## Cheap decisive test

Reuse the ALREADY-MEASURED WorldTree/ARC-Challenge surface-trap diagnostic (naive stem-word-overlap accuracy: Challenge 0.197, below chance; lure_rate 0.23 where a distractor out-overlaps the correct answer, mean max-distractor-overlap 0.74 vs correct 0.46). Split Challenge into LURE subset (n~0.23*1119=~257) and NON-LURE subset. Build the smallest possible two-part probe:
- (a) **Competitor suppression pass**: after automatic retrieval, identify the top-1 candidate; if a signed contradiction/oppose signal (even a crude WordNet-antonym/negation flag, already built in 29538) or simply "this candidate = the surface-overlap winner" fires, DOWN-WEIGHT it and re-rank.
- (b) **Controlled re-retrieval pass**: on down-weighting, reformulate the query (e.g. expand via relation-typed WordNet/ConceptNet neighbors of the STEM's central concept, not the raw stem tokens) and re-retrieve.

Cost: reuses existing harness (ARC/WorldTree cell), existing semantic encoder, existing trust-vetted fact store; no new infra. Est. 1 day build + smoke.

## Falsifiable predictions

**HARD-PASS thresholds:**
- Suppression+re-retrieval lifts accuracy on the LURE subset by >= +0.08 absolute vs the automatic-only baseline (0.696 oracle-gold / ~0.30 real-retrieval per 29537), with the NON-LURE subset unchanged within noise (+/- 0.03) -- i.e. the mechanism targets exactly the failure mode it's meant to fix, not a general improvement (which would suggest leakage/confound).
- Scramble/shuffle control on the suppression signal collapses the LURE-subset gain to within noise of baseline (confirms genuineness, not an artifact of the re-ranking step alone).

**HARD-FAIL thresholds (per lit-scan calibration discipline):**
- If LURE-subset gain < +0.03 absolute, OR if the NON-LURE subset also moves by >= +0.05 (mechanism is not selective to the diagnosed failure mode), treat as REFUTED for this specific two-part design -- the "retrieval is the wall" diagnosis stands, but the controlled-retrieval-anterior-VLPFC-analog is not the fix (would redirect toward relevance-gating precision or a different retrieval-expansion strategy).
- If suppression fires on the CORRECT choice more than the WRONG choice (repeating 29538's crude-polarity anti-precision failure mode), the crude oppose-signal is disqualified and only a precision-tested contradiction detector should be tried next (not simply re-tuned thresholds).

**P estimates (calibration-penalty applied, deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]], novel-synthesis capped at 0.50):**
- P(mechanism produces a genuine, selective LURE-subset lift meeting HARD-PASS) = **0.35** (deflated from an un-calibrated read of ~0.55-0.60, because this is uncharted-regime novel synthesis of two biological primitives into our substrate, and our own prior attempt at a crude contradiction signal, 29538, already failed once on precision grounds — the base rate for "second attempt at a related mechanism succeeds" should stay capped, not optimistic).
- P(HARD-FAIL, mechanism non-selective or repeats the anti-precision failure) = 0.40.
- P(inconclusive / needs a third iteration, e.g. precision-tuned detector) = 0.25.

## Substrate-product implications

This is not a publication-framed finding; it is a build-prioritization finding. The product-relevant takeaway: our glass-box, no-LLM-inference substrate's current bottleneck on knowledge-based multi-choice reasoning is not "more knowledge" or "bigger retrieval index" — the lit-scan converges with our own measurements that it is a missing CONTROL mechanism (escape-the-dominant-association + suppress-the-competitor), which is exactly the kind of small, auditable, glass-box addition that plays to the substrate's differentiator (inspectable evidence, no black-box LLM needed to add this). If the cheap decisive test HARD-PASSES, the productizable claim becomes: "the substrate resists designed adversarial surface-lure distractors via an auditable suppression+re-retrieval step" -- a concrete, demonstrable robustness property that generic embedding-similarity retrieval products lack and cannot cheaply retrofit (they'd need the same architectural addition we're describing).

## Citations (verified count)

4 parallel Sonnet lit-scan sub-agents returned approximately **85 distinct researcher/paper citations** (with some overlap across scans, e.g. Kintsch 1988/1998 and Tulving 1972 cited by multiple sub-agents independently, which is a mild corroboration signal rather than a citation-count inflation). These are SUB-AGENT WEB-SOURCED citations (via WebSearch/WebFetch against public neuroscience/cognitive-science literature) — I (the synthesizing agent) did not independently re-verify each citation's exact page/claim; treat citation-level details (exact journal, exact year) as sub-agent-reported, not disk/DOI-verified. The overall FRAMEWORK claims (existence and rough role of each named system) are standard, well-established cognitive neuroscience and are HIGH confidence; the SPECIFIC citation-year pairings carry the lit-scan calibration penalty (deflate before treating any single citation as load-bearing for a build decision).

## Next-drill candidate

Per the field-advisor read at cycle start (110 drills, 22 fields — this topic is orthogonal to the substrate-physics field taxonomy the advisor tracks, since it's a cognitive-architecture/biology inventory feeding the ARC/ingestion program, not a spin-glass/thermodynamics/free-probability substrate-physics thread). The natural next-drill candidate is a FOCUSED 2x-depth drill on Badre & Wagner's anterior-VLPFC-vs-mid-VLPFC dissociation and the RIF/competitor-suppression literature specifically (the two systems the cheap decisive test above depends on), once the test's build result lands -- to sharpen the mechanism design if HARD-FAIL or INCONCLUSIVE.
