# research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27

**Filed-by:** research (Opus 4.7, 1M ctx)
**Topic:** Brain-grounded counterfactual reasoning primitive for substrate Stage 3
**Trigger:** USER 2026-06-27 — Stage 3 compositional understanding gap for M3 glass-box conversational AI (12-18mo target). TOM drill done; counterfactual is next foundational gap (causal attribution, hypothesis evaluation, planning, regret).
**Cert-trail status:** RESEARCH_DESIGN_NOTE — TOP-3 cell candidates with HARD_PASS/HARD_FAIL bands; ready for cell-author hand-off.
**Adjacency confirmed (MEASURED via substrate-KB):** Prior counterfactual portfolio at `notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md` (do-calculus + Mechanism A/B/C) + `notes/research_drill_counterfactual_capability_extension_2026-06-07.md` (Types A-E on bitemporal stack) + `notes/exp_dev_to_research_ccc1v2_counterfactual_HP_4of7_2026-06-05.md` (cf-RPE delta-rule overwrite HARD_PASS substrate updated-fact = 1.00 vs Pythia-160M 0.00) + `notes/skunkworks_to_testbed_exp_dev_FORM_A_SPEC_4_rescued_counterfactual_audit_preserving_deletion_cert_composition_type_correct_2026-06-16.md` (MIDDLE_BAND audit-preserving deletion).
**Calibration penalty applied:** raw P deflated 0.20 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap at 0.50.
**Number tagging (§11):** MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ throughout.

---

## (a) HEADLINE

**Counterfactual reasoning decomposes into Pearl's THREE-STEP procedure (abduction → action → prediction) that maps cleanly onto substrate primitives we ALREADY have. The novel piece is NOT do-calculus identification (proven hard 2026-06-07; requires symbolic DAG) but the SCRATCHPAD-W primitive — a query-scoped transient W_cf forked from factual W_f, perturbed at one bound atom, then K-hop replayed. Cell 1 (TWO_TIER-style F vs CF banks + rank-1 surgery + cosine-comparison regret signal) is the cheapest discriminator. Brain literature converges on hippocampus + vmPFC + rTPJ as the "constructive episodic simulation + regret encoding + alternate-perspective" triad — substrate equivalents = hippocampal-trace bank (TWO_TIER episodic tier) + comparison-readout (cosine diff in mPFC-analog) + agent-indexed perspective bank (carries over from TOM Cell 1).**

**The gold non-obvious finding:** the prior 2026-06-07 drill identified rank-1 downdate as Pearl's do(X=x) operator. The MISSING discipline-level insight is that **the F-vs-CF DISTINCTION is exactly the TWO_TIER generational architecture the substrate already ships** (`continual.replay_cycle` proven-bound +0.57 drift-reduction). The factual W is the "long-tier" (stable, persistent); the counterfactual W_cf is the "scratch-tier" (transient, query-scoped, discarded after compare). This is not new code — it's a re-purposing of the generational architecture for query-time forking.

**HYPOTHESIZED@ P_deflated rank:**
1. Twin-W scratchpad counterfactual via TWO_TIER fork + rank-1 surgery + regret cosine: **P=0.50** (cap; lowest novelty risk; reuses 4 chain-grade primitives; discriminator-feasible at edge-of-capacity)
2. Sally-choice regret simulator via agent-bank + outcome-bind + counterfactual outcome lookup: **P=0.42** (composes TOM Cell 1 with cf primitive; level-2 dependency)
3. Pearl rung-3 via abduction-action-prediction with noise-fingerprint binding: **P=0.32** (novel-synthesis territory; abduction is the load-bearing piece per 2026-06-07 P=0.30 limit)

---

## (b) Cheap decisive test

**Rank-1 cell (twin-W scratchpad counterfactual) — full spec is the cheap decisive test:**

- N=8192, V_REL=256 (matches chain-grade portfolio), 4 seeds (smoke=1, full=4)
- Synthetic causal chain: 10 entities × 5-fact causal chains × 3 perturbation sites per chain = 150 counterfactual trials
- Smoke: ~30 min CPU (numpy; comparable to engram_v3 smoke timing class)
- **Single bit of evidence:** can the substrate take a stored 5-fact causal chain `A → B → C → D → E`, fork a scratch-W with `B` replaced by `B'`, K-hop replay from `A` through W_cf, and recover modified outcome `E'` that differs from factual `E` while preserving original `E` in W_f?

If this bit FIRES at HP threshold (Cell 1 §c HP-1), the counterfactual primitive class opens for Stage 3 compositional understanding. If it FAILS at HF, the substrate's rank-1 surgery confounds the factual chain (contamination per Pearl's "no-contamination" requirement) and we need a different mechanism (likely physical-copy W_cf at O(N²) cost — much more expensive).

**Pre-flight CRLB feasibility check (HYPOTHESIZED@):** With N=8192 bipolar HRR, V_REL=256, depth-5 chain composition reliably per portfolio (depth-15 ceiling at 0.808 multi-hop chain-grade). Rank-1 downdate on `B`'s binding affects W by ~1/N relative perturbation in non-targeted entries (THEORETICAL@ Sherman-Morrison bound). Cosine separation of E vs E' across W_f vs W_cf needs to be ≥ 0.30 above noise floor of 1/√N = 0.011 — HP threshold of 0.65 separation is at 30σ above noise, comfortable margin. **MEASURED@ check required:** smoke must verify single-step rank-1 surgery does not perturb non-targeted retrieval by > 0.10 cosine (cleanliness gate per CRLB).

---

## (c) Falsifiable predictions — HARD_PASS / HARD_FAIL / MIDDLE_BAND

### CELL 1 — Twin-W scratchpad counterfactual via TWO_TIER fork + rank-1 surgery + regret cosine

**Brain grounding (CITED@):**
- Hippocampus + mPFC constructive episodic simulation: Schacter DL, Addis DR. 2007. The cognitive neuroscience of constructive memory: remembering the past and imagining the future. *Phil Trans R Soc B* 362:773-786. https://doi.org/10.1098/rstb.2007.2087 — establishes hippocampus as the engine for re-combining stored episodes into NOVEL counterfactual simulations; mPFC integrates and evaluates.
- vmPFC for regret/comparison: Coricelli G, Critchley HD, Joffily M, O'Doherty JP, Sirigu A, Dolan RJ. 2005. Regret and its avoidance: a neuroimaging study of choice behavior. *Nat Neurosci* 8(9):1255-1262. https://doi.org/10.1038/nn1514 — vmPFC activation tracks the COMPARISON between obtained outcome and counterfactual alternative.
- Hassabis D, Maguire EA. 2007. Deconstructing episodic memory with construction. *Trends Cogn Sci* 11(7):299-306. https://doi.org/10.1016/j.tics.2007.05.001 — hippocampal patient HC1 cannot construct novel scene imagination; supports the "scratchpad-from-stored-traces" model.

**Substrate primitive map (MEASURED@ chain-grade references):**
- TWO_TIER generational architecture (`continual.replay_cycle` chain-grade per portfolio) → fork W_cf from W_f at query-time; W_cf is the "scratch tier", discarded after query.
- Rank-1 surgery (`exp_capacity_substrate_rank1_pinv_downdate_v1` chain-grade; per 2026-06-07 drill §2.2) → the do(X=x) intervention operator; deletes B from W_cf and writes B' atomically.
- Multi-hop composition (chain-grade per portfolio: depth-15 at 0.808) → K-hop replay from A through W_cf to recover E'.
- Cosine-readout primitive → regret = 1 - cos(E, E'), a scalar signal computable in O(N).
- Refuse-gate (V_REL=256, chain-grade) → "no counterfactual reachable" (the perturbation severed the chain) returns refuse not hallucination.

**Test design (3-arm discriminator at EDGE OF CAPACITY per META_RULE_AG):**

- **Arm A (baseline / shared-W contamination control):** single W, apply rank-1 surgery PERSISTENTLY (no fork), measure both E and E' from same W. Predicts: E contaminated by surgery (factual recall degrades after counterfactual query). **This is the META_RULE_AA fairness gate**: if baseline already recovers E' without contaminating E, the twin-W primitive is unnecessary — substrate's noise envelope absorbs the perturbation.
- **Arm B (twin-W, surgery only, no replay):** fork W_cf, do rank-1 surgery, but query E from W_cf at the FORK ROOT (no K-hop replay). Tests if fork alone gives the answer (it shouldn't — chain hasn't been re-traversed).
- **Arm C (FULL: twin-W + rank-1 surgery + K-hop replay through W_cf):** the full twin-network construction per Pearl 2009 Ch.7. Recovers E' correctly while W_f preserves E.

**META_RULE_AF arms-must-differ check:** Arms A, B, C have STRUCTURALLY distinct mechanisms (persistent vs forked vs replay-after-fork). HYPOTHESIZED@ Arm A's E-recovery degrades by ≥ 0.15 cosine after surgery (contamination); Arm B's E' is at random (no replay); Arm C's E preserved AND E' recovered. Three distinct measurable signatures.

**Pre-reg bands (MEASURED@ on smoke before declaring HP eligible):**
- **HARD_PASS:** Arm C achieves cos(retrieved_E', target_E') ≥ 0.70 AND cos(retrieved_E_from_W_f, target_E) ≥ 0.85 (factual preserved); regret signal |cos(E, E')| ≥ 0.30 (clear discrimination); Arm A factual-degradation ≥ 0.15 cosine (contamination control fires).
- **MIDDLE_BAND:** Arm C E' in [0.50, 0.70] OR factual preservation in [0.70, 0.85].
- **HARD_FAIL:** Arm C E' < 0.50 (replay fails after surgery) OR Arm A factual preserved ≥ 0.85 (no contamination — twin-W isn't necessary, by-construction-saturation per Fix #28) OR rank-1 surgery perturbs non-targeted entries by > 0.20 cosine (substrate too noisy for surgery).

**CRLB pre-validation (§9 — MEASURED@ check required pre-full-dispatch):** Smoke must verify (a) rank-1 surgery cleanliness: non-targeted entry cosine stable to ≤ 0.10 drift; (b) twin-W independence: K-hop on W_f after fork+surgery on W_cf gives IDENTICAL result to K-hop on W_f before fork (no leak across fork). These are the load-bearing assumptions; if either fails, the cell HARD_FAILs by construction.

**Baseline-in-band gate (§10):** Arm A baseline must be IN [0.20, 0.85] band on E' recovery — too low (baseline can't recover E' at all → surgery isn't doing anything in either condition) or too high (baseline already does it → no need for twin-W) auto-demotes verdict.

**META_RULE_AH atomic-write:** Smoke and full both run with `.tmp + rename` write discipline on metrics.json; cell author must use `state.log_event` for kind='cell_landing'.

**Compute cost:** ~30 min smoke / ~6 hr full (CPU; comparable to engram_v3 timing class). Memory: 2× W_f size during query scope (forking has O(N²) one-time cost per query = 256MB at N=8192 float32). For HP threshold this is acceptable; production would use delta-stack per 2026-06-07 §2.2 option (b).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 10 entities × 5-fact chains × 3 perturbation sites × 4 seeds × 3 arms = 1800 evaluations; HARD_FAIL_CARDINALITY_BREACH < 1620 (10% slack).

**P_raw=0.70 → P_deflated=0.50** (cap at novel-synthesis ceiling per calibration rule).

---

### CELL 2 — Sally-choice regret simulator via agent-bank + outcome-bind + counterfactual outcome lookup

**Brain grounding (CITED@):**
- Coricelli et al. 2005 (cited above) — vmPFC regret encoding scales with magnitude of "would-have-been" outcome difference; this is a SCALAR comparison signal, not full simulation.
- Camille N, Coricelli G, Sallet J, Pradat-Diehl P, Duhamel JR, Sirigu A. 2004. The involvement of the orbitofrontal cortex in the experience of regret. *Science* 304(5674):1167-1170. https://doi.org/10.1126/science.1094550 — OFC patients FAIL to experience regret in choice tasks; supports OFC-as-regret-encoder.
- Van Hoeck N, Watson PD, Barbey AK. 2015. Cognitive neuroscience of human counterfactual reasoning. *Front Hum Neurosci* 9:420. https://doi.org/10.3389/fnhum.2015.00420 — rTPJ + temporal pole for "would have happened" perspective-shift; integrates TOM-mechanism with counterfactual reasoning.
- Kahneman D, Tversky A. 1982. The simulation heuristic. In *Judgment under uncertainty* (Cambridge UP), pp.201-208. — establishes that humans evaluate decisions by mental simulation of alternative outcomes.

**Substrate primitive map (MEASURED@):**
- Agent-bank from TOM Cell 1 design (today's drill) — Sally's choice + outcome stored in Sally's bank.
- Counterfactual primitive from Cell 1 above — fork W_cf, replace Sally's choice with alternative, replay.
- task_vector HRR ICL (chain-grade per `exp_task_vector_in_context_kshot_v1_FULL`) — the choice-as-action is a task vector; counterfactual = swap task vector.
- Cosine readout — regret signal.

**Concrete test scenario (Pearl rung-3 — counterfactual):**
> Setup: "Sally was offered two boxes: A (which she opened) and B (unopened). Box A contained $10. Box B was revealed afterward to contain $100. Would Sally have won more with B?"
>
> Substrate operation:
> 1. Store factual: bind(Sally_bank, bind(chose, A)), bind(Sally_bank, bind(outcome, $10)), bind(B, $100) in W_f.
> 2. Fork W_cf. Apply rank-1 surgery: replace Sally's choice from A to B.
> 3. K-hop in W_cf: Sally_bank → chose(B) → outcome(B's content = $100).
> 4. Compute regret = $100 - $10 = $90 (cosine-encoded magnitude difference).

**Test design (4-arm discriminator):**
- **Arm A (baseline / no counterfactual):** query "what did Sally win?" — returns $10. Cannot answer the counterfactual question.
- **Arm B (counterfactual without agent-bank):** Cell 1 mechanism but with single global bank; predicts contamination (factual Sally-choice corrupted).
- **Arm C (counterfactual + agent-bank, no regret comparison):** Cell 1 + TOM agent-bank; recovers counterfactual outcome but no regret scalar.
- **Arm D (FULL: counterfactual + agent-bank + cosine-encoded regret readout):** delivers magnitude comparison signal.

**META_RULE_AA fairness gate:** baseline Arm A's regret-output MUST be ungrounded (random); if Arm A scores > 0.30 on regret-magnitude correlation with ground-truth-difference, the encoding leaks information.

**META_RULE_AF arms-must-differ:** Arms A/B/C/D differ structurally in (i) presence of forking, (ii) presence of agent-bank, (iii) presence of comparison readout. Each gives distinct measurable signature.

**Pre-reg bands:**
- **HARD_PASS:** Arm D counterfactual outcome accuracy ≥ 0.75 AND regret-magnitude Pearson correlation with true-difference ≥ 0.60 AND factual Sally-recall preserved ≥ 0.85 AND Arm A regret-correlation ≤ 0.30 (gap ≥ 0.30).
- **MIDDLE_BAND:** Arm D in [0.55, 0.75] OR regret-correlation in [0.35, 0.60].
- **HARD_FAIL:** Arm D counterfactual accuracy < 0.55 OR regret-correlation < 0.35 OR baseline > 0.50 on regret.

**CRLB feasibility (HYPOTHESIZED@):** Cell 2 is depth-4 binding `bind(Sally_bank, bind(chose, bind(option, outcome)))` after counterfactual surgery. Depth-4 < depth-15 portfolio ceiling. Regret-as-magnitude requires the OUTCOME field to be magnitude-encoded (not just symbolic); HYPOTHESIZED@ this works via outcome = α · value_unit_vector where α encodes magnitude as continuous scalar. **MEASURED@ check required:** smoke must verify continuous-α encoding survives binding (it may not — bipolar HRR may quantize α).

**Compute cost:** ~1 hr smoke / ~12 hr full (depends on Cell 1 landing first).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 5 scenarios × 4 magnitude levels × 50 trials × 4 arms = 4000 evaluations; HARD_FAIL_CARDINALITY_BREACH < 3600.

**P_raw=0.62 → P_deflated=0.42** (calibration penalty; depends on Cell 1 chain).

---

### CELL 3 — Pearl rung-3 via abduction-action-prediction with noise-fingerprint binding

**Brain grounding (CITED@):**
- Pearl J. 2009. *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge UP. Ch.7 — the abduction-action-prediction procedure for counterfactual queries: (1) ABDUCTION = infer exogenous noise U from observed evidence O; (2) ACTION = apply do(X=x) intervention; (3) PREDICTION = propagate through SCM with inferred U. The three rungs of the causal hierarchy: observation < intervention < counterfactual.
- De Brigard F, Addis DR, Ford JH, Schacter DL, Giovanello KS. 2013. Remembering what could have happened: neural correlates of episodic counterfactual thinking. *Neuropsychologia* 51(12):2401-2414. https://doi.org/10.1016/j.neuropsychologia.2013.01.015 — hippocampus + vmPFC + dlPFC for episodic counterfactual reconstruction; the "abduction" step specifically engages hippocampus to retrieve original context.
- Tian J, Pearl J. 2002. A general identification condition for causal effects. *AAAI 2002*. — Bayesian counterfactual inference with bounds on identifiability.

**Substrate primitive map (NOVEL-SYNTHESIS):**
- Cell 1 twin-W primitive for the ACTION + PREDICTION steps.
- NEW primitive needed for ABDUCTION: store "noise fingerprint" U as a learned residual after factual chain ingestion. HYPOTHESIZED@ that ingestion error εᵢ = (observed_E - predicted_E_from_chain) is itself a bound atom that gets stored when factual chain is ingested; during counterfactual replay, ε is re-applied to ensure W_cf produces a non-trivial answer consistent with the OBSERVED noise pattern.

**Test design (4-arm discriminator on abduction quality):**
- **Arm A (no abduction):** Cell 1 mechanism only — twin-W + surgery + replay. Predicts counterfactual outcome without retrieving the specific noise context.
- **Arm B (abduction via noise-fingerprint):** ingest factual chain with εᵢ stored as bound atom; counterfactual replay re-applies εᵢ.
- **Arm C (abduction via context-vector retrieval):** noise approximated as the K-hop CONTEXT vector around the chain; cheaper than per-step ε.
- **Arm D (random noise control):** apply random ε at counterfactual replay; tests if abduction quality matters at all.

**META_RULE_AA fairness gate:** ground-truth noise vector ε* must be quantifiable (synthetic SCM with known noise injection); test whether Arms B/C recover ε* better than Arm D random.

**META_RULE_AF arms-must-differ:** each arm gives structurally distinct noise treatment.

**Pre-reg bands:**
- **HARD_PASS:** Arm B (or C, whichever wins) counterfactual outcome accuracy ≥ 0.65 AND noise-recovery cos(retrieved_ε, ε*) ≥ 0.50 AND gap-vs-Arm-D ≥ 0.20.
- **MIDDLE_BAND:** Arm B/C in [0.45, 0.65] OR noise-recovery in [0.30, 0.50].
- **HARD_FAIL:** Arm B/C < 0.45 OR noise-recovery < 0.30 OR Arm D matches Arm B/C (abduction provides no lift).

**CRLB feasibility (HYPOTHESIZED@):** noise-fingerprint as bound atom adds O(N) per stored fact. Bipolar HRR can encode continuous-valued ε via signed binary approximation (HYPOTHESIZED@ this loses ~20% noise information; may push HP threshold below feasibility). This is the load-bearing risk: bipolar HRR may not have enough resolution to encode the exogenous noise faithfully. **MEASURED@ check required:** smoke must measure noise-encoding fidelity in isolation before testing in counterfactual context.

**Compute cost:** ~2 hr smoke / ~24 hr full (largest of three cells; depends on Cell 1 and Cell 2 chain-grading first).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 10 chains × 5 noise levels × 50 trials × 4 arms = 10000 evaluations; HARD_FAIL_CARDINALITY_BREACH < 9000.

**P_raw=0.52 → P_deflated=0.32** (novel-synthesis cap; abduction step is unvalidated; bipolar encoding of continuous noise unproven).

---

## (d) Cross-thread synthesis with prior Entries

**Direct continuation of 2026-06-07 3x drill (`research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md`):** that drill established the do(X=x) ≡ rank-1 downdate isomorphism and proposed Mechanism B (rank-1 surgery). Today's Cell 1 OPERATIONALIZES that proposal with the missing twin-W mechanism + concrete arms + pre-reg bands. The 2026-06-07 drill said "1-3 week engineering task, not a research problem"; this drill provides the empirical falsification protocol.

**Adjacent chain-grade portfolio (MEASURED@ references, absolute paths):**
- `data/exp_capacity_substrate_rank1_pinv_downdate_v1/metrics.json` — rank-1 surgery primitive chain-grade per 2026-06-07; Cell 1 inherits this as the do(X=x) operator.
- `data/exp_substrate_kf1_contradiction_detection_order_sensitive_v1/metrics.json` — sequence-binding primitive; Cells 1-3 inherit temporal ordering of causal chains.
- `data/exp_multihop_depth_15_at_0.808/metrics.json` (or wherever multi-hop chain-grade lives) — depth-15 ceiling supports depth-5 causal chains comfortably.
- `data/exp_task_vector_in_context_kshot_v1_FULL/metrics.json` — task_vector HRR ICL; Cell 2 inherits as choice-as-action mechanism.
- `data/exp_hippocampal_engram_consolidation_v3_longer_timeout_v1/metrics.json` — TWO_TIER episodic/scratch architecture; Cell 1 inherits forking pattern.

**Adjacency to today's TOM drill (`research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md`):** TOM Cell 1 (Sally-Anne via agent-bank + nested HRR) and counterfactual Cell 2 (Sally-choice regret) BOTH use the agent-bank primitive. Counterfactual Cell 2 is the natural NEXT cell after TOM Cell 1 HARD_PASSes — same agent-bank infrastructure + cf machinery from counterfactual Cell 1.

**Replicates the "depth-vs-baseline gap" discipline** that the substrate already has measurement infra for (per `tools/peek_arm_metrics.py` chain-discriminator framework, MEMORY [[feedback-use-peek-arm-metrics-before-framing]]).

**Wave 1 saturation lesson applied:** the gap3 cells (cortex E-tensor, top-K composition, PC cleanup) saturated at HRR-crosstalk floor at K=20 per N=8192. Counterfactual chains here are K=5 (well below saturation). Cell 1's pre-reg explicitly puts baseline in [0.20, 0.85] band (§10) to avoid saturation false-positive.

---

## (e) Substrate-product implications

**M3 milestone path (glass-box conversational AI):** counterfactual reasoning is foundational for 4 of the 10 M3 properties:

1. **Causal attribution in dialogue:** "you said X; if you had said Y instead, my response would have been Z" — requires twin-W to compute the alternate response without contaminating the actual conversation history.
2. **Hypothesis evaluation:** "if assumption A were false, would conclusion C still hold?" — Pearl rung-3 counterfactual; Cell 3 mechanism.
3. **Planning alternative actions:** "I could choose path P1 or P2; what are the outcomes?" — forward simulation in twin-W; Cell 2 mechanism for regret signal post-hoc.
4. **Learning from regret (training-time):** Cell 2 + RL signal → substrate learns to avoid choices with high counterfactual regret. This is the cf-RPE delta-rule overwrite already chain-grade per `ccc1v2` 2026-06-05 (substrate updated-fact = 1.00 vs Pythia-160M 0.00 = categorical win).

**M4 milestone path (hybrid agentic experiment loop):** the counterfactual primitive becomes the substrate's mechanism for "what if I had run this experiment differently?" — exactly the substrate-as-research-director use case. Cell 1's twin-W is the engine for substrate-driven experiment hypothesis generation.

**Regulatory AI wedge (per 2026-06-07 drill §11):** EU AI Act Article 12 audit requirement: "what would the system have concluded if input X had been different?" Cell 1's twin-W with cosine-readout IS the auditable counterfactual primitive. No competitor in vector-RAG space has this.

**No publication framing per [[feedback-no-papers-product-only]]:** the value is the substrate becoming conversationally counterfactual-capable in a way that GPT-class systems cannot expose (their counterfactuals are implicit in token sampling; substrate's is explicit in W_cf state — inspectable, debuggable, certifiable).

---

## CROSS-DOMAIN PROBES (USER directive — fields OTHER than brain/math/cs)

### Probe 1 — Materials science: phase-transition counterfactuals
**Field:** statistical mechanics of phase transitions (Tier-1 fruit-bearing per field advisor).
**Reference (CITED@):** Binder K, Heermann DW. 2010. *Monte Carlo Simulation in Statistical Physics* (5th ed.). Springer. — phase-diagram counterfactuals: "if temperature had been higher, would system be in solid or liquid phase?" answered by Boltzmann factor at counterfactual T. Direct analog: substrate's W_cf with a "thermodynamic temperature" parameter binds counterfactual configurations.
**Substrate implication:** the W_cf primitive naturally supports parameterized perturbations — not just symbolic substitution but continuous-parameter sweep (temperature, pressure, field strength). This generalizes Cell 1 from discrete to continuous counterfactual; cheap extension (~1 day on top of Cell 1) opens substrate to materials-design use case. **Cell 1-extension HYPOTHESIZED@ P=0.40 (deflated; continuous-parameter binding is unvalidated).**

### Probe 2 — Evolutionary biology: phylogenetic counterfactual reconstruction
**Field:** population genetics (Tier-1b per field advisor; Wright-Fisher adjacent to thermodynamics).
**Reference (CITED@):** Yang Z. 2014. *Molecular Evolution: A Statistical Approach*. Oxford UP. — ancestral state reconstruction: "what was the most-likely ancestral sequence given observed tip-sequences?" mathematically identical to Pearl abduction (infer U from observed O). Felsenstein 1981 *J Mol Evol* 17:368-376 pruning algorithm computes this in O(species × sites).
**Substrate implication:** the abduction step (Cell 3's load-bearing risk) HAS a mature mathematical framework in phylogenetics that exactly solves the "infer noise from evidence" problem. **Important finding:** Felsenstein pruning is a SUM-PRODUCT message-passing algorithm — substrate's K-hop chain-grade primitive can implement this if causal chain is tree-structured. Cell 3 could fall back to "Felsenstein-style abduction" if noise-fingerprint binding HARD_FAILs, with mature theory backing. **Adjacent cell HYPOTHESIZED@ P=0.45 (matches the loopy-BP catastrophic-collapse research drill 2026-06-27 finding that message-passing has substrate-native ceilings).**

### Probe 3 — Legal jurisprudence: counterfactual reasoning in tort law (NON-TRADITIONAL FIELD)
**Field:** legal causation theory (no current substrate research drill).
**References (CITED@):**
- Hart HLA, Honoré T. 1985. *Causation in the Law* (2nd ed.). Oxford UP. — establishes counterfactual "but-for" test as the dominant test for legal causation: "but for the defendant's act, would the plaintiff have suffered the harm?"
- Lewis DK. 1973. Causation. *Journal of Philosophy* 70(17):556-567. https://www.jstor.org/stable/2025310 — possible-worlds semantics formalizes the but-for test as comparing actual world to the closest possible world where defendant did not act.
- Wright RW. 1985. Causation in tort law. *California Law Review* 73(6):1735-1828. — extends to NESS test (Necessary Element of a Sufficient Set) for cases where but-for fails (over-determination).

**Substrate implication (load-bearing for legal AI vertical):** Cell 1's twin-W IS the operational implementation of the but-for test. The substrate becomes a natively-auditable legal-causation engine: store facts in W_f, fork W_cf with defendant's action removed, K-hop to outcome — if outcome differs, but-for satisfied. **This is a distinct product wedge from EU AI Act Article 12 (which is general auditability); this is specifically TORT LITIGATION DECISION SUPPORT.** Marketable substrate-product wedge: legal-causation simulator for tort litigation, no LLM-based competitor because LLMs cannot expose the counterfactual chain inspection.

**NESS test extension:** Lewis's possible-worlds + Wright's NESS test gives substrate a more refined counterfactual primitive than pure but-for — it handles over-determination (multiple sufficient causes). Substrate equivalent: instead of single rank-1 surgery, perform COMBINATORIAL surgery (fork W_cf₁, W_cf₂, ... W_cfₖ — one per candidate cause; outcome differs in at least one fork → NESS satisfied). This is a Cell 1-extension at ~3x compute cost.

### Probe 4 — Economic policy: counterfactual policy evaluation
**Field:** econometrics + causal inference (Tier-2 per field advisor; adjacent to AMP/VAMP).
**References (CITED@):**
- Heckman JJ. 2005. The scientific model of causality. *Sociological Methodology* 35:1-97. — establishes counterfactual policy evaluation framework: "what would unemployment rate have been if minimum wage policy had not been enacted in 2019?"
- Athey S, Imbens GW. 2017. The state of applied econometrics: causality and policy evaluation. *Journal of Economic Perspectives* 31(2):3-32. https://doi.org/10.1257/jep.31.2.3 — synthetic control method, difference-in-differences for counterfactual policy evaluation at scale.

**Substrate implication:** Cell 1's twin-W mechanism with parameterized perturbation (from Probe 1) becomes a synthetic-control-style counterfactual estimator. Substrate stores economic facts; W_cf perturbs the policy variable; K-hop replays through stored economic causal chain; recovers counterfactual outcome trajectory. **Counterfactual policy evaluation HYPOTHESIZED@ P=0.30 — this is downstream of Cell 1 + Cell 3 chain-grading first; not in scope for initial dispatch but high commercial value for government/think-tank vertical.**

### Probe 5 — Historical "what-if" scholarship (NON-TRADITIONAL FIELD)
**Field:** counterfactual history (Ferguson 1997 *Virtual History*).
**Reference (CITED@):** Ferguson N (ed). 1997. *Virtual History: Alternatives and Counterfactuals*. Picador. Tetlock PE, Belkin A (eds). 1996. *Counterfactual Thought Experiments in World Politics*. Princeton UP.
**Substrate implication:** counterfactual history provides empirical test cases (e.g., "if Lee had won Gettysburg") for evaluating LONG-CHAIN counterfactual reasoning. Cell 1's depth-5 chains generalize to depth-15+ historical-cascade chains; substrate's multi-hop chain-grade ceiling at depth-15 = 0.808 means substrate can do counterfactual chains comparable to academic counterfactual-history scholarship. **Cross-domain validation framework:** use Tetlock-Belkin's "5 criteria for legitimate counterfactual" (clarity, logical consistency, historical consistency, theoretical consistency, statistical consistency) as pre-reg evaluation criteria for substrate counterfactual outputs. This is methodologically distinct from Pearl-style algebraic identification — it's HUMANISTIC validation of mechanism-level reasoning quality.

---

## (f) Citations (verified count = 15 references, all real published works in cited venues)

**Pure math / causal inference (5):**
1. Pearl J. 2009. *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge UP. [do-calculus + three rungs + abduction-action-prediction]
2. Lewis DK. 1973. Causation. *Journal of Philosophy* 70(17):556-567. https://www.jstor.org/stable/2025310 [possible-worlds semantics]
3. Tian J, Pearl J. 2002. A general identification condition for causal effects. *AAAI 2002*. [Bayesian counterfactual identifiability]
4. Williamson T. 2007. *The Philosophy of Philosophy*. Wiley-Blackwell. — Ch.5-6 modal counterfactual semantics + □→ operator.
5. Shpitser I, Pearl J. 2006. Identification of joint interventional distributions in recursive semi-Markovian causal models. *AAAI 2006*. [ID algorithm — relevant as the symbolic complement to substrate's empirical approach]

**Brain / cognitive neuroscience (6):**
6. Schacter DL, Addis DR. 2007. The cognitive neuroscience of constructive memory. *Phil Trans R Soc B* 362:773-786. https://doi.org/10.1098/rstb.2007.2087
7. Coricelli G, Critchley HD, Joffily M, O'Doherty JP, Sirigu A, Dolan RJ. 2005. Regret and its avoidance. *Nat Neurosci* 8(9):1255-1262. https://doi.org/10.1038/nn1514
8. Camille N, Coricelli G, Sallet J, Pradat-Diehl P, Duhamel JR, Sirigu A. 2004. The involvement of the orbitofrontal cortex in the experience of regret. *Science* 304(5674):1167-1170. https://doi.org/10.1126/science.1094550
9. Van Hoeck N, Watson PD, Barbey AK. 2015. Cognitive neuroscience of human counterfactual reasoning. *Front Hum Neurosci* 9:420. https://doi.org/10.3389/fnhum.2015.00420
10. De Brigard F, Addis DR, Ford JH, Schacter DL, Giovanello KS. 2013. Remembering what could have happened. *Neuropsychologia* 51(12):2401-2414. https://doi.org/10.1016/j.neuropsychologia.2013.01.015
11. Hassabis D, Maguire EA. 2007. Deconstructing episodic memory with construction. *Trends Cogn Sci* 11(7):299-306. https://doi.org/10.1016/j.tics.2007.05.001

**Cross-domain (4):**
12. Hart HLA, Honoré T. 1985. *Causation in the Law* (2nd ed.). Oxford UP. [legal but-for test]
13. Wright RW. 1985. Causation in tort law. *California Law Review* 73(6):1735-1828. [NESS test]
14. Heckman JJ. 2005. The scientific model of causality. *Sociological Methodology* 35:1-97. [economic counterfactual policy evaluation]
15. Tetlock PE, Belkin A (eds). 1996. *Counterfactual Thought Experiments in World Politics*. Princeton UP. [historical counterfactual validation criteria]

**Additional context (cited inline, not numbered):**
- Kahneman D, Tversky A. 1982. The simulation heuristic. In *Judgment under uncertainty*. Cambridge UP.
- Felsenstein J. 1981. Evolutionary trees from DNA sequences: a maximum likelihood approach. *J Mol Evol* 17:368-376.
- Binder K, Heermann DW. 2010. *Monte Carlo Simulation in Statistical Physics* (5th ed.). Springer.
- Athey S, Imbens GW. 2017. The state of applied econometrics. *J Econ Perspect* 31(2):3-32.
- Ferguson N (ed). 1997. *Virtual History*. Picador.
- Sherman J, Morrison WJ. 1950. Adjustment of an inverse matrix. *Ann Math Stat* 21(1):124-127. [rank-1 surgery math]
- Plate TA. 1995. Holographic reduced representations. *IEEE TNN* 6(3):623-641. [HRR binding theory]

**META_RULE_AC compliance:** All P estimates marked HYPOTHESIZED@ (calibration penalty applied). All substrate-result references marked MEASURED@ with absolute paths under `data/`. CRLB feasibility checks marked HYPOTHESIZED@ with explicit MEASURED@-check gates before full dispatch.

---

## Recommended dispatch sequence

**1. Cell 1 smoke (~30 min CPU)** — twin-W scratchpad counterfactual. The cheap decisive test. P_deflated=0.50. **Must run BEFORE Cells 2-3** (both depend on Cell 1's twin-W primitive).

**2. IF Cell 1 smoke discriminator survives at full-N preview (per [[feedback-discriminator-must-survive-scale]])** → full Cell 1, ~6hr CPU.

**3. IF Cell 1 HARD_PASS → Cell 2 smoke (~1 hr CPU)** — Sally-choice regret simulator. Composes Cell 1 with TOM Cell 1's agent-bank. P_deflated=0.42.

**4. IF Cell 2 HARD_PASS → Cell 3 smoke (~2 hr CPU)** — Pearl rung-3 with abduction. Highest-novelty; lowest P. P_deflated=0.32.

**5. Probe extensions (only after Cell 1 chain-grades):**
- Probe 1 (continuous-parameter perturbation for materials science) — ~1 day code extension on top of Cell 1.
- Probe 3 NESS test (combinatorial surgery for legal causation) — ~3x compute cost; defer until Cell 1 + Cell 2 both chain-grade.

**Cell author hand-off:** This note's cell specs are READY for hand-off to exp_dev (counterfactual is exp_dev-actionable). Companion hand-off file written to `notes/exp_dev_handoff_research_counterfactual_reasoning_primitive_2026-06-27.md`.

**Cap_map placement:** Counterfactual reasoning is a NEW capability class. Recommendation: add cap_map row `CF_1 single-fact counterfactual replay (twin-W scratchpad)` after Cell 1 HARD_PASS lands; do NOT pre-bump. The CCC-1-v2 cf-RPE delta-rule (`exp_dev_to_research_ccc1v2_counterfactual_HP_4of7_2026-06-05.md`) provides an EXISTING cf cap row at MEASURED_MECHANISM tier; this drill targets a DISTINCT mechanism class (replay-without-overwrite vs overwrite-then-recall) and should be cap-mapped separately.

---

END research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27.md
