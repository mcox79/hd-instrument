# Research drill 2x DEEP: mechanism classes BEYOND substrate-discriminative for MWP comprehension/role-assignment

date: 2026-06-11
topic: beyond_discriminative_mwp_mechanism_classes
drill_type: 2x DEEP (level-2 operational)
model: opus (depth synthesis)
parallel_lit_scan: 8 WebSearch sub-scans, generic terms only per [[feedback-query-privacy-decomposition]]
calibration_penalty: applied per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25; cap novel-synthesis P at 0.50)

---

## HEADLINE

Substrate-discriminative is ONE of at least 8 viable mechanism classes for MWP role-assignment. The plateau at ~0.37 on ASDiv-1op / SVAMP is NOT a substrate ceiling --- it is a CLASS ceiling for the discriminative-perceptron family on linguistic-surface features. Brain solves MWPs through composite of (a) frame-semantic schema activation, (b) incremental predictive parsing with mid-sentence schema commitment, (c) world-model situational simulation, (d) analogy retrieval to solved templates, (e) Bayesian model-averaging over interpretations under ambiguity. Top 3 substrate-implementable classes with brain analogue, existing substrate primitives, and expected lift over 0.37: WORLD-MODEL SIMULATION (situational mental model) > FRAME-SEMANTIC SCHEMA RETRIEVAL > BAYESIAN MODEL-AVERAGING ENSEMBLE. RL-policy port (Path 8 PP-375) is HIGH-VALUE TIE for in-flight transfer test. Drill-defeatism: 5 paths must fail before the ceiling claim survives.

---

## Cheap decisive test

Single CPU smoke (~30-60 min) per class on ASDiv-1op + SVAMP held-out 200-item slices:

1. **WORLD-MODEL SIMULATION smoke** (~30 min CPU): substrate-Tier-2 schema-bank (PURCHASE / DISTRIBUTE / EQUAL_GROUPS / COMPARE / CHANGE / COMBINE / PART-WHOLE) with situational-state tracking; for each MWP, parse entities into roles via SCHEMA-SLOT, then SIMULATE state-transitions per schema dynamics; emit answer from final state. CHEAP: only 7 schemas, ~50 lines numpy + existing substrate retrieval.

2. **FRAME-SEMANTIC RETRIEVAL smoke** (~30 min CPU): build schema-frame VECTORS via substrate-bind(FRAME=PURCHASE, ROLE=BUYER, FILLER=Mary); test-MWP triggers most-similar frame via substrate-cosine; role-assignment FOLLOWS from frame instantiation. CHEAP: existing FHRR binding + cleanup.

3. **BAYESIAN MODEL-AVERAGE smoke** (~20 min CPU): wrap existing 7 discriminative mechanisms as POSTERIORS p(role | mechanism_i, MWP); compute joint posterior via product-of-experts or BMA on held-out reachability-confirmed slice; emit role-assignment by max-posterior. CHEAP: re-uses 7 already-built mechanisms, ZERO new primitive.

4. **RL-POLICY port smoke** (~1 hr CPU): port Path 8 PP-375 2-op composition + answer-consistency weak-label policy from MultiArith to ASDiv role-assignment. CHEAP-ish: existing port.

5. **ANALOGY-RETRIEVAL smoke** (~30 min CPU): build substrate-store of ~50 solved MWP exemplars with their schema annotation; test-MWP retrieves nearest-exemplar via substrate composite-similarity; transfer roles via Gentner structure-mapping (slot-isomorphism on substrate Tier-2 schemas). CHEAP: existing retrieval + cleanup.

Decision rule: any class with held-out_accuracy > 0.42 (LIFT > 0.05 over discriminative ceiling 0.37, ~2*SE on n=200) advances to full evaluation. Lift > 0.10 = HARD-PASS. Lift < 0.03 across all 5 = ceiling claim survives but only after ALL 5 fail (drill-defeatism enforcement).

---

## 8 mechanism classes inventoried

### Class 1: WORLD-MODEL SIMULATION (situational mental model)

**Brain analogue + biology-as-existence-proof:**
- van Dijk & Kintsch (1983) propositional + SITUATIONAL representation levels for text comprehension
- Mental-models theory (Johnson-Laird): readers construct simulation of described scenario, not just propositional list
- Lit precedent: Yu et al. (ACL 2023 Findings) "World Models for Math Story Problems" -- MATH-WORLD explicit world-model; concurrent with stochastic-world-model-on-gravity (biorXiv 2022)
- Prefrontal cortex + hippocampal-entorhinal simulation circuitry; documented in primate physical-reasoning tasks

**Substrate-only implementation:**
- Tier-2 schemas as STATE-MACHINES: each schema (PURCHASE, DISTRIBUTE, EQUAL_GROUPS, COMPARE, CHANGE, COMBINE, PART-WHOLE) carries (initial-state slots, transition operator, final-state readout)
- Substrate primitives wired: FHRR bind for ENTITY-STATE pairs; substrate-temporal-policy for state-transitions (PP-225 family); substrate-cleanup for state-readout
- Builds on substrate's STATIC-robust storage + binding (per [[substrate-static-robust-dynamic-fragile-2026-06-10]])

**Expected lift over discriminative 0.37:**
- Predicted accuracy on ASDiv-1op: 0.52 - 0.65 raw; deflate by 0.20 -> 0.42 - 0.52
- Mechanism reason: discriminative plateau is on LINGUISTIC features; simulation operates on EXTRA-LINGUISTIC situational features (state-changes)
- Strongest case: COMPARE / CHANGE schemas where role direction is encoded in state-delta, not surface order

**Pre-registered HARD-PASS / MIDDLE / HARD-FAIL:**
- HARD-PASS: held-out accuracy >= 0.48 on ASDiv-1op (LIFT >= 0.11 above 0.37)
- MIDDLE: 0.40 - 0.48
- HARD-FAIL: < 0.40 (LIFT < 0.03; basically discriminative-class)

**Substrate-existing vs new builds:**
- 80% existing (schemas, FHRR bind, cleanup, temporal-policy)
- 20% new (state-transition operator + final-state readout for 7 schemas; ~150 lines)

### Class 2: FRAME-SEMANTIC SCHEMA RETRIEVAL (Fillmore frames)

**Brain analogue:**
- Fillmore (1976) frame semantics: word evokes frame of concepts and roles; supported by neuroimaging of N400 frame-violation effects
- Construction grammar (Goldberg): linguistic patterns paired with semantic frames
- Schema theory (Rumelhart, Schank): scripts as activated stereotyped structures

**Substrate-only implementation:**
- Substrate Tier-2 already has schema slots (per [[substrate-unified-compositional-generation-engine-2026-06-11]])
- FRAME-VECTOR = substrate-bind(FRAME=PURCHASE) + substrate-bind(ROLE=BUYER, FILLER=?) + ...
- Test-MWP -> cosine-similarity to frame-bank -> winning frame INSTANTIATES role-slots
- Substrate primitive uses: FHRR bind/unbind, cosine, cleanup -- ALL existing

**Expected lift:**
- Predicted accuracy: 0.48 - 0.58 raw; deflate 0.18 -> 0.40 - 0.50
- Weaker than world-model because no state-simulation; but cheaper and uses MORE existing primitives

**Pre-registered:**
- HARD-PASS: held-out >= 0.45 (LIFT >= 0.08)
- MIDDLE: 0.40 - 0.45
- HARD-FAIL: < 0.40

**Substrate existing vs new:**
- 95% existing
- 5% new (frame-bank construction ~50 lines)

### Class 3: BAYESIAN MODEL-AVERAGING over 7 existing mechanisms

**Brain analogue:**
- Rational Speech Act framework (Frank & Goodman 2012; Bergen, Levy, Goodman) -- recursive Bayesian inference for pragmatics
- Multi-system arbitration in PFC (de novo arbitration between competing interpretations)
- Bayesian brain hypothesis (Friston): hypothesis posterior maintained, not single MAP

**Substrate-only implementation:**
- 7 mechanisms are 7 noisy classifiers; each produces p(role | mechanism_i)
- Aggregate via product-of-experts (POE) OR weighted BMA with weights from reachability-oracle agreement
- Substrate has count-NB + posterior estimation primitives already
- Implementable in ~30 lines; uses EXISTING 7 mechanisms

**Expected lift:**
- Theoretical max if mechanisms uncorrelated: 1 - (1-0.37)^7 ~ 0.96; realistic correlation gives much less
- Honest estimate: ensemble lift 0.05 - 0.12 over best single (0.37); raw 0.42 - 0.49; deflate -> 0.37 - 0.44
- WARNING: if all 7 mechanisms fail in the SAME way (correlated errors on comprehension), BMA buys little
- This is the CRITICAL TEST of whether discriminative-class is correlated-error-bound or whether ensemble crosses

**Pre-registered:**
- HARD-PASS: held-out >= 0.45
- MIDDLE: 0.39 - 0.45
- HARD-FAIL: < 0.39 (correlated-error case -- strongest evidence that discriminative-class shares a comprehension blind-spot)

**Substrate existing vs new:**
- 100% existing
- 0% new builds (just an aggregator script)

**KEY VALUE:** even the HARD-FAIL of BMA is high-information -- proves discriminative-class is correlated-blindspot-bound and forces world-model/frame-retrieval as the answer.

### Class 4: REINFORCEMENT-LEARNED POLICY (Path 8 PP-375 port)

**Brain analogue:**
- Dorsolateral striatum + DA reward-prediction-error for policy learning
- Lit precedent: Huang et al. (Neural MWP solver with RL); Hong et al. "Learning by Fixing" (AAAI 2021); WARM (weakly supervised) 2021
- PP-375 substrate-port achieved 0.7530 on MultiArith Tier-A; transferability to ASDiv role-assignment is open question

**Substrate-only implementation:**
- Port existing PP-375 architecture: 2-op composition policy + answer-consistency weak labels
- For role-assignment: weak label is reachability-oracle confirmation OR answer-correctness
- Substrate already runs this on MultiArith

**Expected lift:**
- MultiArith 0.7530 doesn't directly transfer because that's 2-op composition over given-numbers; ASDiv role-assignment is upstream
- Realistic: 0.45 - 0.60 raw; deflate 0.20 -> 0.36 - 0.48
- BIG variance: RL on small datasets is sample-inefficient

**Pre-registered:**
- HARD-PASS: held-out >= 0.48 (PP-375 transfer succeeds)
- MIDDLE: 0.40 - 0.48
- HARD-FAIL: < 0.40 (RL transfer hits same comprehension wall)

**Substrate existing vs new:**
- 70% existing (PP-375 architecture)
- 30% new (role-assignment wrapper + reward shaping)

### Class 5: ANALOGY-BASED RETRIEVAL + STRUCTURE-MAPPING (Gentner / Hofstadter)

**Brain analogue:**
- Hofstadter slipnet (Copycat / Tabletop) -- proven cognitive-architecture mechanism for analogy
- Gentner SME structure-mapping theory -- documented in neuroimaging of analogical reasoning (RLPFC)
- Lit precedent: Liu et al. (NeurIPS 2024) "Learning by Analogy" -- computational-graph retrieval for MWPs achieves +6.7% over baseline few-shot
- Recall-and-Learn (memory-augmented solver) achieves comparable lifts

**Substrate-only implementation:**
- Store ~50 solved-MWP exemplars in substrate with FHRR-bound schema annotation (FRAME, ROLES, OP)
- Test-MWP -> substrate retrieval -> top-k exemplars -> structure-map via slot-isomorphism (substrate Tier-2)
- Substrate has retrieval + cleanup primitives; slipnet polysemic 0.42 result NOT a ceiling (per [[slipnet-polysemic-substrate-only-ceiling-2026-06-11]] which REFUTED that framing)

**Expected lift:**
- Lit precedent shows +6.7% over baseline; substrate analogue 0.37 + ~0.05 = 0.42
- Deflate -> 0.38 - 0.45

**Pre-registered:**
- HARD-PASS: held-out >= 0.44 (LIFT >= 0.07)
- MIDDLE: 0.39 - 0.44
- HARD-FAIL: < 0.39

**Substrate existing vs new:**
- 85% existing
- 15% new (exemplar-store construction + slot-isomorphism mapper)

### Class 6: INCREMENTAL PREDICTIVE PARSING (mid-sentence schema commitment)

**Brain analogue:**
- N400 / P600 ERP components of incremental prediction
- Sturt & Lombardo predictive parsing (PCFG-Viterbi extensions)
- TAG (tree-adjoining grammar) incremental parsing with prediction
- Verb selectional restrictions trigger early-commitment

**Substrate-only implementation:**
- Substrate-classical HMM emission+transition+Viterbi (POS 0.906 already validated)
- Extension: emission distribution conditioned on VERB-frame; predicts upcoming role-slots
- Substrate primitives: existing Viterbi + new conditioning layer

**Expected lift:**
- Incremental-prediction parsers in MWP lit show modest lifts (~+3-5%)
- Honest: 0.39 - 0.44 raw; deflate -> 0.34 - 0.40
- Likely MIDDLE; weakest class

**Pre-registered:**
- HARD-PASS: held-out >= 0.43
- MIDDLE: 0.39 - 0.43
- HARD-FAIL: < 0.39

**Substrate existing vs new:**
- 80% existing
- 20% new (verb-conditioned emission layer)

### Class 7: PRAGMATIC + GRICEAN reasoning (RSA-style)

**Brain analogue:**
- Recursive speaker-listener pragmatic inference (RSA -- Frank, Goodman, Bergen, Levy)
- ToM-circuit involvement (TPJ + mPFC) for pragmatic interpretation
- Quantity/relevance maxims disambiguate role assignment when surface is ambiguous

**Substrate-only implementation:**
- Substrate cleanup as PRAGMATIC FILTER over candidate interpretations
- RSA recursion is small (~3 levels); substrate count-NB as P(utterance | interpretation)
- Substrate-bind for speaker/listener role tracking

**Expected lift:**
- RSA buys disambiguation on ambiguous cases (~20-30% of MWPs)
- Honest: 0.40 - 0.45 raw on ambiguous subset; full set 0.38 - 0.42
- Deflate -> 0.33 - 0.38
- Weak

**Pre-registered:**
- HARD-PASS: held-out >= 0.42
- MIDDLE: 0.38 - 0.42
- HARD-FAIL: < 0.38

**Substrate existing vs new:**
- 60% existing
- 40% new (RSA recursion wrapper; small but non-trivial)

### Class 8: EMBODIED IMAGE-SCHEMA grounding (Lakoff CONTAINER/PATH/FORCE)

**Brain analogue:**
- Lakoff & Johnson image-schemas: CONTAINER, PATH, FORCE, BALANCE, UP-DOWN
- Grounded cognition (Barsalou): simulation in modal systems
- Lit precedent: arxiv 2503.24110 "Grounding Agent Reasoning in Image Schemas" -- neurosymbolic
- Substrate has image-schema cluster (PP-316; rescued via concept-context binding per [[substrate-representation-artifacts-rescued-2026-06-10]])

**Substrate-only implementation:**
- Each MWP-frame maps to image-schema: PURCHASE -> TRANSFER+CONTAINER, DISTRIBUTE -> SPLIT+PATH, EQUAL_GROUPS -> COLLECTION+PARTITION
- Substrate-image-schema cluster (existing, rescued 1.000 HP via concept-context binding) as primitive
- Bind schema to MWP frame; let image-schema dynamics inform role direction

**Expected lift:**
- Image-schemas are upstream of frame-semantics; potentially correlated with class 1+2
- Honest: 0.40 - 0.50 raw; deflate -> 0.35 - 0.45
- Strong tail; uncertain median

**Pre-registered:**
- HARD-PASS: held-out >= 0.45
- MIDDLE: 0.39 - 0.45
- HARD-FAIL: < 0.39

**Substrate existing vs new:**
- 90% existing (image-schema cluster + binding)
- 10% new (schema-to-image-schema mapper, ~30 lines)

---

## Top 5 ranked by (P_deflated * cost-efficiency * substrate-existing-coverage)

Ranking factors:
- P_deflated = my estimate after 0.15-0.25 deflation
- cost = 1/CPU-hours; existing-mechanism reuse boosts
- coverage = % substrate primitives already built

| Rank | Class | P_deflated (HARD-PASS) | Cost (hrs CPU) | Existing % | Composite score | Notes |
|------|-------|-----------------------|----------------|------------|-----------------|-------|
| 1 | WORLD-MODEL SIMULATION (class 1) | 0.45 | 0.5 | 80% | HIGH | Strongest mechanistic case; state-delta breaks comprehension wall |
| 2 | BAYESIAN MODEL-AVERAGE (class 3) | 0.32 | 0.3 | 100% | HIGH | Cheapest; even HARD-FAIL is high-info (proves correlated-blindspot) |
| 3 | FRAME-SEMANTIC RETRIEVAL (class 2) | 0.40 | 0.5 | 95% | HIGH | Sits between world-model and discriminative; high reuse |
| 4 | RL-POLICY port (class 4) | 0.38 | 1.0 | 70% | MED-HIGH | Tests Path 8 PP-375 transfer; high prior from MultiArith 0.7530 |
| 5 | ANALOGY-RETRIEVAL (class 5) | 0.32 | 0.5 | 85% | MED | Lit precedent modest; substrate slipnet REFUTED-ceiling helps |

Below cutoff: image-schema (class 8) -- correlated with 1+2; pragmatic (class 7) -- weak lift, new build cost; incremental-parsing (class 6) -- weakest expected lift.

---

## Falsifiable predictions (cross-class aggregate)

**HARD-PASS for the full drill** (substrate has class beyond discriminative): >=1 of top 5 hits HARD-PASS thresholds on the cheap smoke. Validates that 0.37 is class-ceiling not substrate-ceiling.

**HARD-FAIL for the full drill** (ceiling claim survives): ALL 5 classes hit HARD-FAIL thresholds. Then the ceiling claim is empirically validated AND we have a strong mechanistic story (correlated blind-spot in language-to-state mapping).

**MIDDLE outcome** (some lift, no class-break): at least one class in MIDDLE band, none HARD-PASS. Indicates partial mechanism gain but no qualitative class-shift; drill into the lifting class + composite.

**Pre-registered honest interpretation:**
- HARD-PASS on class 1 (world-model) + HARD-FAIL on class 3 (BMA): clean mechanistic story (situational simulation needed, ensemble of language-features insufficient)
- HARD-PASS on class 3 (BMA) alone: discriminative class has uncorrelated errors; ensemble works but mechanism is unclear
- HARD-FAIL on class 1 + HARD-PASS on class 4 (RL): substrate needs end-to-end reward not schema engineering
- Universal HARD-FAIL: stronger ceiling claim; force substrate-LLM-hybrid for MWP comprehension (per [[substrate-LLM-boundary-decomposition-2026-06-10]])

---

## Cross-thread synthesis

- Consistent with [[methodology-benchmark-must-break-symmetry-2026-06-11]]: discriminative wins on asymmetric ops (SVAMP X-Y / X/Y 0.110->0.267 2.4x lift). ASDiv role-assignment plateau at 0.37 suggests the asymmetry isn't carried in surface features alone -- world-model state-delta IS the asymmetry-carrier.
- Consistent with [[substrate-unified-compositional-generation-engine-2026-06-11]]: world-model simulation IS the unified compositional engine instantiated for MWP domain (schema = domain-specific instantiation).
- Consistent with [[substrate-LLM-boundary-decomposition-2026-06-10]]: parsing arbitrary English is the LLM-only piece; but role-assignment from PARSED input is substrate territory IF the right mechanism class is used.
- Consistent with [[substrate-static-robust-dynamic-fragile-2026-06-10]]: world-model state-machines are STATIC schemas with cleanup-validated transitions, not online-adaptive dynamics; should be substrate-robust.
- REFUTES the "0.37 = substrate ceiling" framing per [[feedback-dont-parrot-drill-defeatism-2026-06-11]] -- N>=5 mechanism classes UNTESTED, drill-defeatism rule binding.
- Builds on [[substrate-deep-self-evaluation-program-2026-06-11]]: this drill is a Layer 1 (attribution) + Layer 2 (spectral) test -- which mechanism family carries the comprehension capability?
- Per [[feedback-literature-is-not-oracle-2026-06-11]]: MWP literature mostly trains end-to-end neural; world-model + frame-semantic explicit-architecture lit is small. Substrate's symbolic-explicit instantiation may surface findings literature doesn't predict.

---

## Substrate-product implications

- If class 1 (world-model) wins, substrate-product gains AUDITABLE STATE-SIMULATION for MWP-class tasks -- demo-grade differentiator vs LLM black-box reasoning. Substrate-product reading: "show me the situational model the system built and the state-transitions it ran" -- LLMs cannot offer this.
- If class 3 (BMA) wins, substrate-product gains CALIBRATED MULTI-MECHANISM UNCERTAINTY for ambiguous inputs -- ties to ECE 0.044 conformal+isotonic line. Substrate-product reading: "system reports confidence-by-mechanism for each role assignment".
- If class 4 (RL port) wins, validates substrate's CROSS-TASK POLICY TRANSFER (MultiArith -> ASDiv) -- substrate-product reading: "trained once on small math set, generalizes to comprehension-heavy MWPs".
- Universal HARD-FAIL forces substrate-LLM-hybrid; reduces substrate-only claim scope but is HONEST per Layer 1 attribution.

---

## Citations (verified count)

Verified lit-scan findings via 8 WebSearch sub-scans (generic terms):

1. Semantic parsing for MWPs: Liu et al. graph-to-tree (arxiv 2004.13781); Neural Semantic Parser ACM TALLIP; ResearchGate survey on MWP semantic parsing gap. [verified-3]

2. Incremental predictive parsing: Demberg et al. "Incremental Predictive Parsing with PsycholinguisticallyMotivated TAG" (MIT Computational Linguistics 2013); Sturt et al. TACL 2013; PMC10110650 large-sample incremental licensing study; ncbi.nlm PMC7727355 real-time neurobiological incremental interpretation. [verified-4]

3. Analogy + structure-mapping for MWPs: Liu et al. "Learning by Analogy" NeurIPS 2024 (arxiv 2411.16454) -- +6.7% lift via computational-graph retrieval; Hong et al. Recall-and-Learn arxiv 2109.13112; CBR + Structure Mapping arxiv 1108.0039. [verified-3]

4. World-model simulation for MWPs: Yu et al. "World Models for Math Story Problems" ACL 2023 Findings (aclanthology 2023.findings-acl.579); MATH-WORLD framework; arxiv 2310.13021 AI for Mathematics cognitive science perspective; stochastic-world-model gravity biorXiv 2022.12.30.522364. [verified-4]

5. Bayesian model averaging: Hinne, Gronau, van den Bergh, Wagenmakers (2020) Sage; Hoeting et al. tutorial (Stat Sci, jah colostate); Yao et al. stacking arxiv 1704.02030; Madigan-Raftery STATA BMA. [verified-4]

6. RL + weak supervision for MWPs: Hong et al. "Learning by Fixing" AAAI 2021 (arxiv 2012.10582); Chatterjee et al. WARM arxiv 2104.06722; Huang et al. Neural MWP Solver with RL (semantic scholar). [verified-3]

7. Pragmatic / RSA: Bergen, Levy, Goodman "Pragmatic Reasoning through Semantic Inference" (Stanford cocolab); Frank-Goodman RSA; arxiv 2510.26253 Pragmatic Theories Enhance LLM implicature; arxiv 2210.14986 Goldilocks of Pragmatic Understanding. [verified-4]

8. Embodied + image schemas + MWPs: arxiv 2503.24110 "Grounding Agent Reasoning in Image Schemas"; cognitiveresearchjournal Grounded and Embodied Mathematical Cognition; Lakoff-Johnson image schemas; Frontiers Educ 2020 embodied design for math. [verified-4]

Total verified citations: 29 across 8 mechanism-class scans.

---

## Pre-registered HARD-FAIL thresholds (calibration-penalty enforced)

Per [[feedback-lit-scan-calibration-penalty]]:
- Cap novel-synthesis P at 0.50: applied to class 1 (world-model novel) and class 2 (frame-retrieval novel) -- both at 0.40-0.45 P_deflated, well below cap
- Deflate 0.15-0.25 from lit-precedent P estimates: applied
- HARD-FAIL thresholds explicitly stated per class above
- Drill-defeatism enforcement: 5 paths must HARD-FAIL before the "0.37 is substrate ceiling" claim survives

**For substrate-ceiling claim to survive (per drill-defeatism rule):**
1. WORLD-MODEL SIMULATION HARD-FAIL (held-out < 0.40)
2. BAYESIAN MODEL-AVERAGE HARD-FAIL (held-out < 0.39)
3. FRAME-SEMANTIC RETRIEVAL HARD-FAIL (held-out < 0.40)
4. RL-POLICY port HARD-FAIL (held-out < 0.40)
5. ANALOGY-RETRIEVAL HARD-FAIL (held-out < 0.39)

Any single HARD-PASS invalidates the ceiling claim and identifies the class that breaks the comprehension wall.

---

## Hand-off

Exp_dev-actionable: YES. Companion file: `notes/exp_dev_handoff_research_beyond_discriminative_mwp_2026-06-11.md` (written separately).

Next-drill candidate: depending on which class HARD-PASSes (or universal HARD-FAIL), drill into that class's deeper mechanism inventory (e.g., world-model -> state-transition operator design; BMA -> correlation structure of 7 mechanisms; RL-port -> reward shaping for role-assignment).

---

end of drill.
