# research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27

**Filed-by:** research (Opus 4.7, 1M ctx)
**Topic:** Brain-grounded counterfactual reasoning primitive for substrate Stage 3 — GAP-FOCUSED (basics banked)
**Trigger:** USER 2026-06-27 — Stage 3 compositional understanding gap for M3 glass-box conversational AI. TOM drill done; this drill addresses counterfactual GAPS beyond the 4 chain-grade + 1 MIDDLE_BAND atoms already on disk.
**Cert-trail status:** RESEARCH_DESIGN_NOTE — TOP-3 GAP cells with HARD_PASS/HARD_FAIL bands; ready for cell-author hand-off.
**Calibration penalty applied:** raw P deflated 0.20 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap at 0.50.
**Number tagging (§11):** MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ throughout.

---

## 0. MEASURED@ existing counterfactual portfolio (verified on disk 2026-06-27)

Substrate ALREADY has substantial counterfactual capability. Cell designs below address GAPS, not duplicates.

| Atom | Path | Verdict | Headline |
|---|---|---|---|
| `exp_causal_intervention_isolation_v1` | `d:/AI/hd-instrument/data/exp_causal_intervention_isolation_v1/metrics.json` | MEASURED@ HARD_PASS | Single intervention is LOCAL — non-target recall degradation = 0.0000, non-target recall after intervention = 1.000. Counterfactual replay does not corrupt the rest of memory. |
| `exp_causal_counterfactual_replay_v1` | `d:/AI/hd-instrument/data/exp_causal_counterfactual_replay_v1/metrics.json` | MEASURED@ MIDDLE_BAND | counterfactual_accuracy = 1.000; mean_intervention = 16.864ms (>10ms latency bar). Mechanism works perfectly; only latency holds it out of chain-grade. |
| `exp_causal_audit_chain_depth_v1` | `d:/AI/hd-instrument/data/exp_causal_audit_chain_depth_v1/metrics.json` | MEASURED@ HARD_PASS | 100% causal-chain proofs valid up to depth 50 (O(1) per-hop verify); chain-valid by depth d5=1.0, d20=1.0. |
| `exp_causal_bitemporal_composition_v1` | `d:/AI/hd-instrument/data/exp_causal_bitemporal_composition_v1/metrics.json` | MEASURED@ HARD_PASS | counterfactual-as-of accuracy = 1.000. Causal + bitemporal time-travel composition works. |
| `exp_causal_correlational_disambig_v1` | `d:/AI/hd-instrument/data/exp_causal_correlational_disambig_v1/metrics.json` | MEASURED@ HARD_PASS | Causal precision = 1.000, recall = 1.000 (CAUSE_OF vs CORRELATED_WITH role disambig, N=4096). Mechanism A viable. |

**Substrate counterfactual story (MEASURED@):** intervention isolation + counterfactual replay (accuracy=1.000) + audit chain depth-50 + bitemporal composition + role disambig — ALL WORK. Pearl rungs 2 (intervention) + 3 (counterfactual) covered for SINGLE-STEP, SINGLE-FACT, STORED-INTERVENTION case.

**What's NOT banked (the GAPS this drill targets):**
- **GAP A — Regret/comparison primitive:** factual-vs-CF outcome cosine diff with magnitude encoding (vmPFC analog). No existing atom.
- **GAP B — Chain-of-counterfactual / nested CF:** "what if X had been Y, then GIVEN THAT, what if Z had been W?" — depth-2+ counterfactual nesting. No existing atom.
- **GAP C — Counterfactual SIMULATION with NOVEL antecedents:** the existing replay uses STORED interventions (hetero-assoc target swap on known atoms). Generating CF for an antecedent NOT in the corpus = unsolved.
- **GAP D — Latency optimization:** replay at 16.864ms; target <10ms for chain-grade and <1ms for real-time conversational use. Delta-stack / lazy-eval / batched-surgery candidate mechanisms.
- **GAP E — Counterfactual GENERATION:** substrate PROPOSES "what if X had been Y?" rather than executing user-specified CF. Requires identifying salient perturbation candidates + ranking. No existing atom.

---

## (a) HEADLINE

**Counterfactual basics are banked; today's TOP-3 targets the highest-value un-atomized GAPS for Stage 3 M3 conversational AI. Rank-1 cell = REGRET COMPARISON PRIMITIVE (GAP A) — the vmPFC analog signal that turns counterfactual REPLAY into counterfactual REASONING. Brain literature converges on Coricelli vmPFC + Camille OFC regret encoding as the scalar magnitude-difference readout that downstream decision-making depends on. Substrate has all the upstream primitives (intervention isolation MEASURED@ 1.000, counterfactual_replay MEASURED@ 1.000) but NO comparison readout primitive — this is the missing piece for "the substrate KNOWS the counterfactual differs and BY HOW MUCH."**

**The gold non-obvious finding:** the existing replay primitive achieves accuracy=1.000 but is MIDDLE_BAND only on latency (16.864ms). GAP D latency optimization (delta-stack lazy-eval; HYPOTHESIZED@ 4-8ms achievable) would auto-promote the existing atom to chain-grade WITHOUT new mechanism risk. This is a CHEAP COMPOSITION cell: the substrate already won on accuracy; engineering one Sherman-Morrison delta-stack reorg reaches chain-grade.

**HYPOTHESIZED@ P_deflated rank (GAP-targeted, not basics-duplicating):**
1. **GAP A: Regret-magnitude comparison primitive (vmPFC analog)** — P=0.50 (cap; composes 5 chain-grade atoms; lowest novelty risk; M3-load-bearing)
2. **GAP D: Latency optimization via delta-stack lazy surgery** — P=0.50 (cap; engineering, not science; auto-promotes existing MIDDLE_BAND atom)
3. **GAP B: Nested chain-of-counterfactual (depth-2+ CF composition)** — P=0.38 (novel composition; depth-of-nesting is the load-bearing risk; brain-existence-proof from Roese mental-simulation literature)

GAPs C and E discussed in §5 below as Tier-2 candidates (deferred until GAPs A/D/B chain-grade).

---

## (b) Cheap decisive test

**Rank-1 cell (GAP A — regret-magnitude comparison primitive) — full spec is the cheap decisive test:**

- N=8192, V_REL=256 (matches chain-grade portfolio), 4 seeds (smoke=1, full=4).
- Composes existing chain-grade atoms: counterfactual_replay (factual + CF outcomes) → NEW comparison readout → scalar regret signal.
- Test: 5 decision scenarios × 4 magnitude levels (small/medium/large/extreme outcome differences) × 100 trials × 3 arms = 6000 evaluations.
- Smoke: ~30 min CPU (composes existing primitives; only new code is the comparison readout).
- **Single bit of evidence:** can the substrate output a scalar regret signal that has Pearson correlation ≥ 0.60 with the ground-truth outcome magnitude difference, while NOT correlating with the outcome magnitude itself (regret is about DIFFERENCE not value)?

If this bit FIRES at HP threshold, GAP A closes and substrate has the M3-load-bearing vmPFC primitive. If it FAILS, the cosine-readout is too coarse for magnitude encoding and we need a different scalar readout (likely L2-norm-difference in unbinding residuals).

---

## (c) Falsifiable predictions — HARD_PASS / HARD_FAIL / MIDDLE_BAND

### CELL 1 — GAP A: Regret-magnitude comparison primitive (vmPFC analog)

**Brain grounding (CITED@):**
- Coricelli G, Critchley HD, Joffily M, O'Doherty JP, Sirigu A, Dolan RJ. 2005. Regret and its avoidance: a neuroimaging study of choice behavior. *Nat Neurosci* 8(9):1255-1262. https://doi.org/10.1038/nn1514 — vmPFC activation tracks the MAGNITUDE of comparison between obtained and counterfactual outcomes. Critically, the signal is the DIFFERENCE not the absolute value.
- Camille N, Coricelli G, Sallet J, Pradat-Diehl P, Duhamel JR, Sirigu A. 2004. The involvement of the orbitofrontal cortex in the experience of regret. *Science* 304(5674):1167-1170. https://doi.org/10.1126/science.1094550 — OFC patients FAIL to experience regret in choice tasks; supports OFC-as-regret-encoder; patients can still compute counterfactual replay but cannot compare.
- Boorman ED, Behrens TEJ, Woolrich MW, Rushworth MFS. 2009. How green is the grass on the other side? Frontopolar cortex and the evidence in favor of alternative courses of action. *Neuron* 62(5):733-743. https://doi.org/10.1016/j.neuron.2009.05.014 — frontopolar cortex encodes the value of UN-CHOSEN alternatives; converges with vmPFC for the comparison signal.

**Substrate primitive map (MEASURED@ + 1 NEW):**
- MEASURED@ `exp_causal_counterfactual_replay_v1` — provides the CF outcome (accuracy=1.000).
- MEASURED@ `exp_causal_intervention_isolation_v1` — guarantees the factual outcome is preserved during CF (non-target recall=1.000).
- MEASURED@ multi-bank partition primitive — factual outcome in bank-F, CF outcome in bank-CF; comparison reads both.
- **NEW: comparison readout primitive** — scalar regret = magnitude-encoded cosine difference between factual outcome HRR and CF outcome HRR, calibrated to correlate with ground-truth value difference.

**Test design (3-arm discriminator at EDGE OF CAPACITY per META_RULE_AG):**

- **Arm A (baseline / value-only readout):** read out factual outcome magnitude only; predicts "regret" = factual outcome value (NOT the difference). **META_RULE_AA fairness gate:** if Arm A correlates with ground-truth magnitude difference ≥ 0.30, the test design is leaky (something in the readout is encoding the difference accidentally).
- **Arm B (raw cosine diff, no magnitude calibration):** compute cos(F_outcome, CF_outcome); use 1-cos as regret signal. Tests if uncalibrated cosine has correct correlation structure.
- **Arm C (FULL: magnitude-calibrated comparison readout):** outcomes encoded as α · value_unit_vector where α encodes magnitude continuously; regret = ||α_F · v_F - α_CF · v_CF||₂ / (||α_F · v_F|| + ||α_CF · v_CF||) — normalized magnitude difference. The vmPFC analog.

**META_RULE_AF arms-must-differ:** Arm A returns ONE scalar (value), Arm B returns scalar in [0,1] (cosine diff), Arm C returns scalar in [0,1] (normalized magnitude diff). Structurally distinct outputs and underlying computations.

**Pre-reg bands (MEASURED@ on smoke before declaring HP eligible):**
- **HARD_PASS:**
  - Arm C regret-Pearson(true magnitude difference) ≥ 0.60
  - AND Arm C regret-Pearson(absolute outcome value) ≤ 0.20 (regret is about difference, not value — vmPFC discipline)
  - AND Arm A regret-Pearson(true magnitude difference) ≤ 0.30 (baseline does NOT encode regret)
  - AND gap (Arm C - Arm A) ≥ 0.30 on the difference-correlation
  - AND factual recall preserved ≥ 0.95 (no contamination from comparison readout)
- **MIDDLE_BAND:** Arm C in [0.40, 0.60] OR Arm B beats Arm C (uncalibrated wins; calibration unnecessary).
- **HARD_FAIL:** Arm C < 0.40 OR baseline > 0.50 on difference-correlation (by-construction-saturation) OR Arm C value-correlation > 0.50 (regret signal leaks absolute value — not a clean comparison primitive).

**CRLB feasibility (HYPOTHESIZED@ — MEASURED@ check required pre-full-dispatch):** continuous-α encoding requires bipolar HRR to faithfully preserve magnitude. Bipolar quantization may lose ~20% magnitude information per [[feedback-experiment-bias-master-checklist]] BIAS-13 contamination concerns. Smoke MUST verify: (a) magnitude-encoding round-trip fidelity ≥ 0.90 cosine before testing in comparison context; (b) factual + CF banks remain separable under comparison readout (no cross-bank leak). If (a) fails, fall back to discrete magnitude levels (5-bin quantization) for the smoke.

**Baseline-in-band gate (§10):** Arm A baseline correlation must be IN [0.05, 0.30] band — exactly zero means the test design is too trivial (any noise gives 0); above 0.30 means the design leaks.

**META_RULE_AH atomic-write:** standard cell discipline applies; `.tmp + rename` on metrics.json; `state.log_event` for kind='cell_landing'.

**Compute cost:** ~30 min smoke / ~3 hr full (CPU; lightweight composition on existing primitives).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 5 scenarios × 4 magnitude levels × 100 trials × 4 seeds × 3 arms = 24000 evaluations; HARD_FAIL_CARDINALITY_BREACH < 21600.

**P_raw=0.70 → P_deflated=0.50** (cap at novel-synthesis ceiling).

---

### CELL 2 — GAP D: Latency optimization for counterfactual replay (delta-stack lazy surgery)

**Brain grounding (CITED@):**
- Pfeiffer BE, Foster DJ. 2013. Hippocampal place-cell sequences depict future paths to remembered goals. *Nature* 497(7447):74-79. https://doi.org/10.1038/nature12112 — hippocampal forward sweeps happen in <100ms; counterfactual mental simulation is FAST in biological substrate. The brain doesn't do O(N²) matrix copies.
- Carr MF, Jadhav SP, Frank LM. 2011. Hippocampal replay in the awake state. *Nat Neurosci* 14(2):147-153. https://doi.org/10.1038/nn.2732 — replay events are 100-200ms; compressed temporal scale.

The 16.864ms current latency is well within biological budget BUT the MIDDLE_BAND verdict gates downstream conversational use (sub-10ms required for real-time per latency MEMORY discipline; ideal <1ms for chain-grade).

**Substrate primitive map:**
- MEASURED@ `exp_causal_counterfactual_replay_v1` — current 16.864ms via "hetero-assoc target swap" mechanism.
- MEASURED@ rank-1 surgery primitive — Sherman-Morrison closed-form O(N) update.
- **NEW: delta-stack lazy evaluation** — maintain stack of pending rank-1 updates [d1, d2, ..., dk]; apply lazily during K-hop instead of physically modifying W. Per 2026-06-07 §2.2 option (b).

**Test design (4-arm discriminator on latency-accuracy frontier):**
- **Arm A (baseline / current mechanism):** existing 16.864ms hetero-assoc target swap. Reference latency.
- **Arm B (delta-stack lazy, k=1):** single-fact CF via delta-stack; HYPOTHESIZED@ 4-8ms (no W modification; lazy add during K-hop).
- **Arm C (delta-stack lazy, k=3):** three-fact CF via delta-stack; tests delta-stack overhead.
- **Arm D (delta-stack lazy + batched K-hop):** batch K-hop with delta-stack baked into kernel; HYPOTHESIZED@ <2ms (kernel fusion).

**META_RULE_AA fairness gate:** accuracy MUST be preserved across arms. If any arm's CF accuracy drops below 0.95 (current is 1.000), the latency improvement is being purchased with accuracy.

**META_RULE_AF arms-must-differ:** A=physical copy, B=lazy-single, C=lazy-multi, D=lazy+fusion. Distinct computational pipelines.

**Pre-reg bands:**
- **HARD_PASS:**
  - Arm B or D latency < 10ms AND accuracy ≥ 0.95
  - Promotes parent atom `exp_causal_counterfactual_replay_v1` MIDDLE_BAND → chain-grade
  - AND latency ratio vs Arm A ≥ 2x improvement
- **MIDDLE_BAND:** Arm B or D in [10ms, 16.864ms] (marginal improvement) OR accuracy in [0.85, 0.95].
- **HARD_FAIL:** All non-A arms ≥ 16.864ms (no speedup) OR accuracy drop > 0.10 in any non-A arm (latency-accuracy tradeoff broken) OR delta-stack introduces incorrect results (correctness regression).

**CRLB feasibility (HYPOTHESIZED@):** delta-stack adds O(K · k_delta) per K-hop where K=hop depth, k_delta=stack depth. For K=5, k_delta=3 = 15 extra dot products per query = ~1ms overhead at N=8192. Total HYPOTHESIZED@ latency ~5-8ms. Sub-1ms requires GPU kernel fusion (Arm D).

**Baseline-in-band gate (§10):** Arm A latency MUST replicate the MEASURED@ 16.864ms within ±5ms (replication check). If Arm A is faster (substrate hardware improved since 2026-06-07), recalibrate HP threshold.

**Compute cost:** ~30 min smoke / ~2 hr full (small, focused engineering benchmark).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 4 arms × 100 trials × 5 chain-depths × 4 seeds = 8000 evaluations; HARD_FAIL_CARDINALITY_BREACH < 7200.

**P_raw=0.70 → P_deflated=0.50** (cap; engineering not science; high confidence in delta-stack theory).

---

### CELL 3 — GAP B: Nested chain-of-counterfactual (depth-2+ CF composition)

**Brain grounding (CITED@):**
- Roese NJ. 1997. Counterfactual thinking. *Psychol Bull* 121(1):133-148. https://doi.org/10.1037/0033-2909.121.1.133 — establishes that humans naturally chain counterfactuals: "if X had been Y... and then if Z had been W given that..." The mental simulation supports recursive nesting.
- Byrne RMJ. 2016. Counterfactual thought. *Annu Rev Psychol* 67:135-157. https://doi.org/10.1146/annurev-psych-122414-033249 — review of counterfactual nesting limits (humans degrade beyond depth 3-4); maps onto substrate composition depth-15 ceiling.
- De Brigard F, Addis DR, Ford JH, Schacter DL, Giovanello KS. 2013. Remembering what could have happened. *Neuropsychologia* 51(12):2401-2414. — hippocampus + vmPFC + dlPFC engagement INCREASES with counterfactual complexity (nesting depth).

**Substrate primitive map (MEASURED@ + NEW composition):**
- MEASURED@ `exp_causal_counterfactual_replay_v1` — single-step CF (depth-1).
- MEASURED@ `exp_causal_audit_chain_depth_v1` — chain-valid at depth 50; supports the depth axis.
- MEASURED@ `exp_causal_bitemporal_composition_v1` — bitemporal CF; serves as the "GIVEN THAT" axis for nested CF.
- MEASURED@ multi-hop chain-grade at depth-15 = 0.808.
- **NEW: nested-CF composition** — fork W_cf₁ from W_f, apply CF₁; then fork W_cf₂ from W_cf₁, apply CF₂ given W_cf₁; recover outcome.

**Test design (4-arm discriminator on nesting depth):**
- **Arm A (depth-1):** single CF; replicates existing chain-grade primitive (reference baseline).
- **Arm B (depth-2, independent):** CF₁ and CF₂ in DISJOINT regions of W; tests if independent CFs compose linearly.
- **Arm C (depth-2, dependent — CF₂'s antecedent is in CF₁'s consequence chain):** the genuine nested case; CF₂ acts on a value MODIFIED by CF₁.
- **Arm D (depth-3 dependent):** triple-nested; tests if depth degradation matches human Byrne-observed pattern.

**META_RULE_AA fairness gate:** Arm A (depth-1) MUST replicate MEASURED@ chain-grade accuracy=1.000. If Arm A fails, the cell harness is broken.

**META_RULE_AF arms-must-differ:** depth-1 / depth-2-indep / depth-2-dep / depth-3-dep are 4 structurally distinct CF nesting patterns.

**Pre-reg bands:**
- **HARD_PASS:**
  - Arm A accuracy ≥ 0.95 (replication)
  - Arm B (depth-2 indep) ≥ 0.85
  - Arm C (depth-2 dep) ≥ 0.65 (the genuine nesting test)
  - Arm D (depth-3 dep) ≥ 0.40 (graceful degradation matching human Byrne limit)
  - AND factual recall preserved ≥ 0.85 across all CF arms (no contamination accumulation across nests)
- **MIDDLE_BAND:** Arm C in [0.45, 0.65] OR Arm D in [0.25, 0.40].
- **HARD_FAIL:** Arm A < 0.95 (replication broken) OR Arm C < 0.45 (depth-2 dep nesting fails — no genuine nesting capability) OR Arm D ≥ 0.95 (no degradation = by-construction-saturation) OR contamination accumulation > 0.20 cosine.

**CRLB feasibility (HYPOTHESIZED@):** depth-3 nested CF = composed W_cf₃ that has had 3 rank-1 surgeries applied in sequence. Each surgery adds O(1/N) perturbation to non-targeted entries; cumulative ~ 3/N at N=8192 = 0.00037 worst-case (well below noise floor). The load-bearing risk is CF₂'s K-hop on W_cf₁ — depth-5 chain through twice-modified W. Total composition depth = 5 (chain) + 3 (CF nests) = 8; well below depth-15 portfolio ceiling.

**Baseline-in-band gate (§10):** Arm A must be IN [0.95, 1.00] band (chain-grade replication); below means cell broken; saturated 1.000 with NO discrimination of arms B/C/D means EXISTING primitive already covers nested cases (unlikely but possible — would auto-demote to MEASURED_MECHANISM).

**Compute cost:** ~1 hr smoke / ~8 hr full (multiple chain depths × multiple CF nests).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 4 arms × 10 entities × 5-fact chains × 50 trials × 4 seeds = 40000 evaluations; HARD_FAIL_CARDINALITY_BREACH < 36000.

**P_raw=0.58 → P_deflated=0.38** (novel composition; depth-3 dependent nesting is uncharted regime; Byrne human-degradation observation suggests intrinsic ceiling).

---

## (d) Cross-thread synthesis with prior Entries

**Cells DUPLICATE-CHECK (per coordinator URGENT update):** none of the 3 cells above duplicate MEASURED@ atoms. Cell 1 is comparison readout (NOT atomized). Cell 2 is latency optimization (auto-promotes the existing MIDDLE_BAND atom). Cell 3 is nested CF composition (extends single-step atom to depth-2+).

**Adjacency to TOM Cell 1 (`research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md`):** Cell 1 here (regret comparison) is the natural NEXT cell after TOM Cell 1 (Sally-Anne) — same agent-bank infrastructure + scalar readout. The "Sally chose A, would she have won with B" scenario from the prompt MAPS to TOM Cell 1 (Sally as agent in bank) + Cell 1 here (regret as comparison).

**Adjacency to 2026-06-07 3x drill (`research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md`):** that drill predicted Mechanism B (rank-1 surgery) and option (b) delta-stack lazy. Cell 2 here OPERATIONALIZES the delta-stack proposal. The 2026-06-07 drill said "delta-stack recommended for sparse interventions (1-3 variables)" — Cell 2 tests exactly that regime.

**Adjacency to 2026-06-07 capability-extension drill (`research_drill_counterfactual_capability_extension_2026-06-07.md`):** that drill defined Type D (compositional multi-step CF) as P_deflated=0.55. Cell 3 here is the experimental falsification of that prediction — nested CF is genuinely Type D.

**Replicates the "depth-vs-baseline gap" discipline** that the substrate already has measurement infra for (per `tools/peek_arm_metrics.py` chain-discriminator framework, MEMORY [[feedback-use-peek-arm-metrics-before-framing]]).

**Wave 1 saturation lesson applied:** Cell 1 explicitly puts baseline correlation in [0.05, 0.30] band (§10) to avoid saturation false-positive. Cell 3 explicitly requires depth-3 degradation < 0.95 to avoid by-construction-saturation per Fix #28.

---

## (e) Substrate-product implications

**M3 milestone path (glass-box conversational AI):** the 3 GAP cells are foundational for 5 of the 10 M3 properties:

1. **Conversational regret / hedging:** "I should have asked you about X earlier; if I had, your question Y would have been answerable" — Cell 1 (regret comparison) is the load-bearing primitive.
2. **Counterfactual planning:** "if I chose path A, regret = R_A; if path B, regret = R_B; choose min(R)" — Cell 1 enables choice optimization via regret minimization.
3. **Nested hypothesis evaluation:** "if assumption A had been false AND given that, if action B had been different, would conclusion C still hold?" — Cell 3 (nested CF) directly.
4. **Real-time conversational latency:** Cell 2 (sub-10ms CF) makes CF queries possible mid-conversation, not just post-hoc.
5. **Learning from regret (training-time):** Cell 1 → RL signal → substrate learns to avoid choices with high counterfactual regret. Composes with the cf-RPE delta-rule overwrite already chain-grade per `ccc1v2` 2026-06-05.

**M4 milestone path:** Cell 3 (nested CF) becomes the substrate's mechanism for "what if I had run this experiment differently AND given that, what if I had measured a different observable?" — exactly the substrate-as-research-director use case.

**Regulatory AI wedge:** Cell 2's sub-10ms latency makes EU AI Act Article 12 audit queries possible at scale (audit of 10⁶ decisions ≤ 10⁴ seconds vs current 1.7 × 10⁴ seconds). Cell 1's regret-magnitude signal becomes the AUDIT METRIC for "by how much did the decision differ from the counterfactual?" — quantitative regulatory standard.

**Legal AI wedge (continued from 2026-06-07):** Cell 1 regret-magnitude IS the operational implementation of legal "damages" computation in but-for tort cases. "But for defendant's act, plaintiff would have suffered X less harm" — X is the regret-magnitude signal directly.

**No publication framing per [[feedback-no-papers-product-only]]:** the value is the substrate becoming conversationally CF-comparison-capable — GPT-class systems cannot expose the comparison signal (it's implicit in token sampling); substrate's is explicit in W_f vs W_cf scalar readout (inspectable, debuggable, certifiable).

---

## 5. GAP C and GAP E — Tier-2 candidates (deferred)

### GAP C — Counterfactual SIMULATION with NOVEL antecedents (P_deflated = 0.30, deferred)

The existing chain-grade replay uses STORED interventions. Generating CF for an antecedent NOT in the corpus requires:
- ENCODING the novel antecedent into a substrate vector (encoder primitive — chain-grade per portfolio).
- Estimating the "neighborhood" of stored facts the novel antecedent perturbs (LSH-style retrieval).
- Applying surgery using the encoded novel vector as the target of rank-1 update.

**Why deferred:** depends on encoder quality for novel-antecedent encoding; substrate's char-trigram encoder is reliable for filename-substring (per substrate-KB) but not for semantic novelty. **Defer until encoder upgrade lands per `feedback_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md`.**

### GAP E — Counterfactual GENERATION (substrate proposes CF) (P_deflated = 0.25, deferred)

The substrate-PROPOSES-CF capability requires:
- Identifying SALIENT antecedents to perturb (importance-weighted retrieval).
- Ranking candidate CFs by expected magnitude difference (Cell 1 regret as the ranking signal).
- Filtering for VALIDITY (the proposed CF must be physically/logically possible).

**Why deferred:** depends on Cell 1 (regret as ranking signal) landing first; depends on importance-weighting primitive (currently MIDDLE_BAND per multi-channel importance ceiling research drill 2026-06-27). **Defer until Cell 1 chain-grades AND importance primitive resolves.**

---

## CROSS-DOMAIN PROBES (USER directive — fields OTHER than brain/math/cs)

### Probe 1 — Materials science: phase-transition counterfactuals
**Field:** statistical mechanics of phase transitions (Tier-1 fruit-bearing).
**Reference (CITED@):** Binder K, Heermann DW. 2010. *Monte Carlo Simulation in Statistical Physics* (5th ed.). Springer. — phase-diagram counterfactuals: "if temperature had been higher, would system be in solid or liquid phase?" Boltzmann factor at counterfactual T.
**Substrate implication:** Cell 1's regret-magnitude primitive generalizes to "free-energy difference" between factual phase and counterfactual phase — direct mapping. **Cell 1 extension HYPOTHESIZED@ P=0.40** (continuous-temperature parameterization on top of Cell 1).

### Probe 2 — Evolutionary biology: phylogenetic counterfactual reconstruction
**Field:** population genetics (Tier-1b adjacent to thermodynamics).
**Reference (CITED@):** Yang Z. 2014. *Molecular Evolution: A Statistical Approach*. Oxford UP. Felsenstein J. 1981. Evolutionary trees from DNA sequences. *J Mol Evol* 17:368-376. — ancestral state reconstruction = Pearl abduction; Felsenstein pruning is sum-product message passing.
**Substrate implication:** the GAP C abduction step has mature theory in phylogenetics. Cell 3 (nested CF) corresponds to "what if mutation X had been Y AND what if mutation Z had been W given X=Y?" — exactly the multi-mutation phylogenetic counterfactual. **Adjacent cell HYPOTHESIZED@ P=0.40 (depends on Cell 3 chain-grading).**

### Probe 3 — Legal jurisprudence: counterfactual reasoning in tort law (NON-TRADITIONAL FIELD)
**Field:** legal causation theory.
**References (CITED@):**
- Hart HLA, Honoré T. 1985. *Causation in the Law* (2nd ed.). Oxford UP. [but-for test]
- Lewis DK. 1973. Causation. *J Philosophy* 70(17):556-567. https://www.jstor.org/stable/2025310 [possible-worlds semantics]
- Wright RW. 1985. Causation in tort law. *Cal Law Rev* 73(6):1735-1828. [NESS test]

**Substrate implication:** Cell 1 regret-magnitude IS the operational damages-computation primitive. Substrate becomes natively-auditable legal causation engine: store facts in W_f, fork W_cf with defendant action removed, K-hop to outcome, Cell 1 readout = damages magnitude. **NESS test extension:** instead of single rank-1 surgery, perform COMBINATORIAL surgery (fork W_cf₁, W_cf₂, ..., W_cfₖ — one per candidate cause); outcome differs in at least one fork → NESS satisfied. Cell 1 + Cell 3 + ~1 week combinatorial-surgery code = legal-causation product. **High commercial value for tort-litigation decision support.**

### Probe 4 — Economic policy: counterfactual policy evaluation (NON-TRADITIONAL FIELD)
**Field:** econometrics (Tier-2 adjacent to AMP/VAMP).
**References (CITED@):**
- Heckman JJ. 2005. The scientific model of causality. *Sociological Methodology* 35:1-97. [counterfactual policy framework]
- Athey S, Imbens GW. 2017. The state of applied econometrics. *J Econ Perspect* 31(2):3-32. https://doi.org/10.1257/jep.31.2.3 [synthetic control + diff-in-diff]
- Abadie A, Diamond A, Hainmueller J. 2010. Synthetic control methods for comparative case studies. *J Am Stat Assoc* 105(490):493-505. [synthetic control method]

**Substrate implication:** synthetic control = construct a counterfactual unit from weighted combination of stored units; substrate's superposition primitive is natively this. **HYPOTHESIZED@ Probe-4 cell P=0.40** — substrate as a synthetic-control engine for policy evaluation. Government / think-tank vertical.

### Probe 5 — Historical "what-if" scholarship (NON-TRADITIONAL FIELD)
**Field:** counterfactual history.
**Reference (CITED@):** Tetlock PE, Belkin A (eds). 1996. *Counterfactual Thought Experiments in World Politics*. Princeton UP. Ferguson N (ed). 1997. *Virtual History*. Picador.
**Substrate implication:** Tetlock-Belkin's "5 criteria for legitimate counterfactual" (clarity, logical consistency, historical consistency, theoretical consistency, statistical consistency) become pre-reg evaluation criteria for substrate CF outputs. Particularly relevant to Cell 3 (nested CF) — Byrne's depth-degradation observation parallels Tetlock-Belkin's "compounding implausibility" critique. **Validation framework, not new cell.**

---

## (f) Citations (verified count = 15 references, all real published works in cited venues)

**Brain / cognitive neuroscience (7):**
1. Coricelli G, Critchley HD, Joffily M, O'Doherty JP, Sirigu A, Dolan RJ. 2005. Regret and its avoidance. *Nat Neurosci* 8(9):1255-1262. https://doi.org/10.1038/nn1514
2. Camille N, Coricelli G, Sallet J, Pradat-Diehl P, Duhamel JR, Sirigu A. 2004. The involvement of the orbitofrontal cortex in the experience of regret. *Science* 304(5674):1167-1170. https://doi.org/10.1126/science.1094550
3. Boorman ED, Behrens TEJ, Woolrich MW, Rushworth MFS. 2009. How green is the grass on the other side? Frontopolar cortex and the evidence in favor of alternative courses of action. *Neuron* 62(5):733-743. https://doi.org/10.1016/j.neuron.2009.05.014
4. De Brigard F, Addis DR, Ford JH, Schacter DL, Giovanello KS. 2013. Remembering what could have happened. *Neuropsychologia* 51(12):2401-2414. https://doi.org/10.1016/j.neuropsychologia.2013.01.015
5. Schacter DL, Addis DR. 2007. The cognitive neuroscience of constructive memory. *Phil Trans R Soc B* 362:773-786. https://doi.org/10.1098/rstb.2007.2087
6. Pfeiffer BE, Foster DJ. 2013. Hippocampal place-cell sequences depict future paths to remembered goals. *Nature* 497(7447):74-79. https://doi.org/10.1038/nature12112
7. Van Hoeck N, Watson PD, Barbey AK. 2015. Cognitive neuroscience of human counterfactual reasoning. *Front Hum Neurosci* 9:420. https://doi.org/10.3389/fnhum.2015.00420

**Pure math / cognitive science (3):**
8. Pearl J. 2009. *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge UP.
9. Roese NJ. 1997. Counterfactual thinking. *Psychol Bull* 121(1):133-148. https://doi.org/10.1037/0033-2909.121.1.133
10. Byrne RMJ. 2016. Counterfactual thought. *Annu Rev Psychol* 67:135-157. https://doi.org/10.1146/annurev-psych-122414-033249

**Cross-domain (5):**
11. Hart HLA, Honoré T. 1985. *Causation in the Law* (2nd ed.). Oxford UP. [legal but-for]
12. Wright RW. 1985. Causation in tort law. *California Law Review* 73(6):1735-1828. [NESS]
13. Heckman JJ. 2005. The scientific model of causality. *Sociological Methodology* 35:1-97. [policy CF]
14. Abadie A, Diamond A, Hainmueller J. 2010. Synthetic control methods. *J Am Stat Assoc* 105(490):493-505.
15. Tetlock PE, Belkin A (eds). 1996. *Counterfactual Thought Experiments in World Politics*. Princeton UP.

**Additional context (cited inline, not numbered):**
- Lewis DK. 1973. Causation. *J Philosophy* 70(17):556-567.
- Yang Z. 2014. *Molecular Evolution*. Oxford UP.
- Felsenstein J. 1981. *J Mol Evol* 17:368-376.
- Binder K, Heermann DW. 2010. *Monte Carlo Simulation in Statistical Physics* (5th ed.). Springer.
- Athey S, Imbens GW. 2017. *J Econ Perspect* 31(2):3-32.
- Ferguson N (ed). 1997. *Virtual History*. Picador.
- Carr MF, Jadhav SP, Frank LM. 2011. Hippocampal replay in the awake state. *Nat Neurosci* 14(2):147-153.
- Sherman J, Morrison WJ. 1950. *Ann Math Stat* 21(1):124-127. [rank-1 surgery math]

**META_RULE_AC compliance:** All P estimates marked HYPOTHESIZED@ (calibration penalty applied). All substrate-result references marked MEASURED@ with absolute paths under `data/`. CRLB feasibility checks marked HYPOTHESIZED@ with explicit MEASURED@-check gates before full dispatch.

---

## Recommended dispatch sequence

**1. Cell 1 smoke (~30 min CPU)** — regret-magnitude comparison primitive. The vmPFC analog. P_deflated=0.50. Composes 5 chain-grade atoms; lowest novelty risk; M3-load-bearing.

**2. Cell 2 smoke (~30 min CPU)** — latency optimization via delta-stack lazy surgery. P_deflated=0.50. Engineering, not science; auto-promotes existing MIDDLE_BAND atom to chain-grade. Can dispatch in PARALLEL with Cell 1.

**3. IF Cell 1 smoke discriminator survives at full-N preview** → full Cell 1, ~3hr CPU.

**4. IF Cell 2 smoke discriminator survives** → full Cell 2, ~2hr CPU.

**5. IF Cell 1 chain-grade → Cell 3 smoke (~1 hr CPU)** — nested chain-of-counterfactual. P_deflated=0.38. Depends on Cell 1 + Cell 2 mechanisms.

**6. Probe extensions (only after Cells 1-3 chain-grade):**
- Probe 1 (continuous-parameter for materials science) — ~1 day code extension on Cell 1.
- Probe 3 NESS combinatorial surgery (legal causation) — ~1 week on top of Cells 1+3.
- Probe 4 synthetic-control (econ policy) — ~3 days on Cell 1 + superposition primitive.

**Cell author hand-off:** This note's cell specs are READY for hand-off to exp_dev (counterfactual GAP work is exp_dev-actionable). Companion hand-off file written to `notes/exp_dev_handoff_research_counterfactual_reasoning_primitive_2026-06-27.md`.

**Cap_map placement:** counterfactual basics already exist in cap_map (5 atoms above). Recommendations:
- Add `CF_2 regret comparison primitive (vmPFC analog)` after Cell 1 HARD_PASS.
- Promote `CF_1 counterfactual replay` from MEASURED_MECHANISM to chain-grade after Cell 2 HARD_PASS (latency-driven promotion).
- Add `CF_3 nested counterfactual composition` after Cell 3 HARD_PASS.

---

END research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27.md
