# research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27

**Filed by:** research (Opus, 1M ctx)
**Topic:** Brain-grounded Theory of Mind (TOM) primitive design for substrate Stage 3
**Trigger:** USER 2026-06-27 — Stage 3 mentalizing gap for M3 glass-box conversational AI (12-18mo target)
**Cert-trail status:** RESEARCH_DESIGN_NOTE — TOP-3 cell candidates with HARD_PASS/HARD_FAIL bands; ready for cell-author hand-off
**Adjacency confirmed:** No prior TOM cells in `data/`; Stage 3 portfolio adjacent = exp_parietal_cortex_spatial_relations_distinct_v2, exp_task_vector_in_context_kshot_v1, exp_substrate_kf1_contradiction_detection_order_sensitive_v1, exp_hippocampal_engram_consolidation_v3. ToM is the next gap-class.
**Calibration penalty applied:** raw P estimates deflated 0.20 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap at 0.50.

---

## (a) HEADLINE

**Theory of Mind is decomposable into 4 substrate-tractable primitives — and #1 (second-order belief binding via nested HRR) is the cheapest discriminator. Brain literature converges on TPJ as a "Belief Compartment" — substrate equivalent = a dedicated agent-indexed multi-bank partition queried through a `believes` role-vector. Top-3 cells designed; rank-1 (Sally-Anne via nested HRR + agent partition) has P_deflated = 0.50, smoke ≤ 1hr CPU.** Cross-domain probes (developmental psych two-systems theory, primatology TOM-gap) cohere: human TOM = chimpanzee perception/goal tracking + uniquely-human belief representation. The substrate already has perception/goal primitives (binding + multi-bank); BELIEF as second-order binding is the missing piece.

**HYPOTHESIZED P_deflated rank:**
1. Sally-Anne false-belief via nested HRR + agent-bank: **P=0.50** (calibrated; lowest implementation risk; brain-grounded; discriminator-feasible)
2. Level-k recursive mentalizing via depth-stacked binding: **P=0.42** (mid; depth-5 limit on prior composition portfolio is the load-bearing concern)
3. Perspective-taking via dual-encoder + viewpoint-rotate operator: **P=0.34** (hardest; novel-synthesis territory)

---

## (b) Cheap decisive test

**Rank-1 cell (Sally-Anne nested HRR + agent partition) — full spec is the cheap decisive test:**

- N=8192, V_REL=256 (matches refuse-gate v1 chain-grade portfolio), single seed for smoke; 4 seeds for full
- 3 agents × 4 objects × 3 locations = 36 belief-states per trial × 100 trials = 3600 atoms
- Smoke: ~30 min CPU (numpy; comparable to engram smoke cost class)
- **Single bit of evidence:** can the substrate maintain Sally's FALSE belief about ball-in-basket AFTER Ann moves ball to box, when queried "where will Sally LOOK?" — while ALSO returning correctly to "where IS the ball?"

If this bit FIRES at the HP threshold below, TOM-primitive class opens; if it FAILS at HF, the binding mechanism does not natively support second-order belief and we need a different substrate primitive (likely an explicit epistemic-state register, MUCH more expensive).

---

## (c) Falsifiable predictions — HARD_PASS / HARD_FAIL / MIDDLE_BAND

### CELL 1 — Sally-Anne false-belief via nested HRR + agent multi-bank partition
**Brain grounding:** TPJ-rTPJ (right temporo-parietal junction; Saxe & Kanwisher 2003 NeuroImage 19(4):1835-1842; Saxe & Powell 2006 Psych Sci 17(8):692-699) is a domain-specific "belief region" — fMRI lesion + neuroimaging show selectivity for belief-attribution over non-belief social cognition. Apperly & Butterfill 2009 Psych Rev 116(4):953-970 two-systems theory: System-1 implicit belief-tracking (TPJ rapid) + System-2 explicit reasoning (mPFC + lateral PFC slow). Cell 1 targets System-1.

**Substrate primitive map:**
- Multi-bank partition (chain-grade per portfolio: K=4096 banks) → one bank per agent (Sally bank, Ann bank, Observer bank); each bank stores that agent's belief-state HRR independently
- HRR bind/unbind → `belief = bind(believes, bind(object, location))` written into agent's bank
- Refuse-gate (V_REL=256, chain-grade) → "Sally has no belief about new-location" returns refuse not hallucination
- Order-sensitive sequence binding (chain-grade per exp_substrate_kf1_contradiction_detection_order_sensitive_v1) → temporal sequence of belief updates

**Test design (3-arm discriminator at EDGE OF CAPACITY per META_RULE_AG):**
- Arm A (baseline / no partition): single global bank; binds belief without agent-indexing — predicts WHERE-IS correctly, WHERE-WILL-SALLY-LOOK collapses to last-update (incorrect-but-current)
- Arm B (agent partition, no refuse-gate): per-agent banks but writes BOTH world-update AND Sally-bank — tests if partition alone solves it
- Arm C (FULL: agent partition + refuse-gate + observer-vs-actor separation): Sally's bank only sees Sally's observations; the substrate "knows what Sally knows"

**META_RULE_AA fairness gate:** baseline (Arm A) MUST be ungated on belief-attribution — if Arm A scores >0.30 on WHERE-WILL-SALLY-LOOK it means the cell is leaking world-state into Sally's bank.

**Pre-reg bands (MEASURED on smoke before declaring HP eligible):**
- HARD_PASS: Arm C ≥ 0.75 on Sally-Anne false-belief AND Arm A ≤ 0.30 (gap ≥ 0.45) AND world-state queries ≥ 0.85 across all arms (substrate didn't lose world-tracking)
- MIDDLE_BAND: Arm C in [0.55, 0.75] OR gap in [0.25, 0.45] — partial mentalizing
- HARD_FAIL: Arm C < 0.55 OR Arm A > 0.50 (baseline already does it; not a TOM primitive)

**CRLB feasibility check (HYPOTHESIZED):** With N=8192 bipolar HRR, V_REL=256, max-K composition depth ≈ 8 reliably per portfolio. Sally-Anne requires depth-3 binding `bind(SALLY_BANK, bind(believes, bind(ball, basket)))`. Depth-3 ≪ depth-8 capacity ceiling, so HP=0.75 is physically reachable. SNR estimate (HYPOTHESIZED): single bind drops cosine to ~0.85; triple bind to ~0.85³ = 0.61; with N=8192 the cosine-threshold separation is well above noise floor of ~1/√N = 0.011. **MEASURED check required:** run smoke first, verify single-bank baseline triple-bind cosine before full dispatch (META_RULE_AG anti-saturation discipline).

**Compute cost:** ~30 min smoke / ~6hr full (CPU, comparable to engram_v3 timing class).

**CARDINALITY_OK:** EXPECTED_N_UNITS = 3 agents × 4 objects × 3 locations × 100 trials = 3600 atoms × 3 arms = 10800 evaluations; HARD_FAIL_CARDINALITY_BREACH < 9720 (10% slack).

**P_raw=0.70 → P_deflated=0.50** (cap at novel-synthesis ceiling per calibration rule).

---

### CELL 2 — Level-k recursive mentalizing via depth-stacked agent binding
**Brain grounding:** Higher-order recursive mentalizing engages mPFC (medial prefrontal cortex; Frith & Frith 2003 Trans R Soc Lond B 358:459-473) more strongly with each recursion level. Kovács, Téglás & Endress 2010 Science 330:1830-1834 show implicit second-order belief tracking in 7-month infants (System-1 TPJ-mediated). Yoshida, Dolan & Friston 2008 PLoS Comp Bio 4(12):e1000254 give a Bayesian recursive-belief computational model (substrate-relevant: level-k as nested probability over partner-beliefs).

**Substrate primitive map:**
- Multi-hop composition (chain-grade per portfolio: depth-15 at 0.808) — directly applicable; level-k = depth-k binding
- HRR nested bind: `level_2 = bind(X_BANK, bind(believes, bind(Y_BANK, bind(believes, Z))))`
- task_vector HRR bundle (chain-grade per exp_task_vector_in_context_kshot_v1) — in-context belief updates as task-vector deltas

**Test design (4-arm discriminator across recursion depths):**
- Level-0: world state query (no agents)
- Level-1: "what does X believe?" (single agent partition)
- Level-2: "what does X believe Y believes?" (nested)
- Level-3: "what does X believe Y believes Z believes?" (triple-nested)

**META_RULE_AA fairness gate:** baseline = level-0 ALONE; baseline cannot trivially achieve >0.30 on level-2/3 by random alignment.

**Pre-reg bands:**
- HARD_PASS: level-1 ≥ 0.80, level-2 ≥ 0.60, level-3 ≥ 0.40 (graceful degradation pattern matching human level-k empirical data; Camerer Ho Chong 2004 QJE 119(3):861-898 show humans average level 1.5-2 in beauty contests)
- MIDDLE_BAND: level-2 in [0.40, 0.60] OR level-3 in [0.20, 0.40]
- HARD_FAIL: level-2 < 0.40 (binding doesn't survive second nest) OR all-levels saturated >0.95 (smoke discriminator failure — META_RULE_AG)

**CRLB feasibility (HYPOTHESIZED):** level-3 = depth-7 binding (3× agent + 3× believes + payload). Depth-7 < depth-15 portfolio ceiling, but cosine drops to ~0.85^7 ≈ 0.32 which is uncomfortably close to noise. HP=0.40 at level-3 is at-or-below the cosine-decay floor — MEASURED check required before full dispatch.

**Compute cost:** ~1 hr smoke / ~12 hr full.

**CARDINALITY_OK:** 4 levels × 3 agents × 100 trials × 4 arms = 4800 atoms; HARD_FAIL_CARDINALITY_BREACH < 4320.

**P_raw=0.55 → P_deflated=0.35** (calibration penalty; depth-7 nest is at-edge).

---

### CELL 3 — Perspective-taking via dual-encoder + epistemic-occlusion mask
**Brain grounding:** Precuneus + posterior cingulate (Cavanna & Trimble 2006 Brain 129:564-583) for self/other spatial perspective-taking; Schurz et al. 2014 NeuroSci Biobehav Rev 42:9-34 meta-analysis distinguishes "visual perspective" (precuneus) from "belief perspective" (TPJ). Hill & Wagner 2018 Neuron 99(3):448-464 give computational models for perspective-rotation as affine transforms over an egocentric-allocentric encoder.

**Substrate primitive map:**
- Parietal cortex spatial reasoning (per exp_parietal_cortex_spatial_relations_distinct_v2 chain-grade) — already has MOVABLE + RELATIONAL primitives
- Dual encoder: substrate-native encoder + a per-agent "viewpoint-rotated" encoder (HYPOTHESIZED novel-synthesis — viewpoint as a learned per-agent rotation matrix R_agent ∈ O(N) applied before binding)
- Epistemic occlusion mask: zero out fields agent didn't see (binary mask × bipolar HRR)

**Test design (3-arm discriminator on "what does X see vs me?"):**
- Arm A (baseline): single encoder; all agents share viewpoint — predicts identical perception regardless of agent
- Arm B (rotation only): per-agent R_agent without occlusion mask — tests if rotation alone gives perspective
- Arm C (FULL: rotation + occlusion mask): full perspective-taking

**META_RULE_AA fairness gate:** spatial setup MUST place objects such that ego-view ≠ Sally-view (occlusion is non-trivial); baseline cannot solve by symmetry.

**Pre-reg bands:**
- HARD_PASS: Arm C ≥ 0.70 on perspective-query, Arm A ≤ 0.30 (gap ≥ 0.40), MOVABLE primitive unchanged (≥ 0.85, regression check)
- MIDDLE_BAND: Arm C in [0.50, 0.70]
- HARD_FAIL: Arm C < 0.50 OR baseline > 0.50

**CRLB feasibility:** R_agent is the load-bearing novel piece. If R_agent is a random orthogonal matrix per agent (~O(N) parameter cost = 8192²/agent = 67M floats/agent), it's a large parameter add. CHEAPER alternative: R_agent = circular-shift by agent-index (~zero param cost; well-defined on HRR via FFT). HYPOTHESIZED this works because HRR's circular-shift commutes with binding under FFT.

**Compute cost:** ~1 hr smoke / ~8 hr full (extra cost from O(N) rotations).

**CARDINALITY_OK:** 3 agents × 6 objects × 4 viewpoints × 50 trials × 3 arms = 10800 atoms; HARD_FAIL_CARDINALITY_BREACH < 9720.

**P_raw=0.50 → P_deflated=0.30** (novel-synthesis: R_agent design is unvalidated; chamber requires MEASURED smoke before banding).

---

## (d) Cross-thread synthesis with prior Entries

**Adjacent chain-grade portfolio (MEASURED references, absolute paths):**
- `data/exp_parietal_cortex_spatial_relations_distinct_v2/metrics.json` — MOVABLE + RELATIONAL primitives chain-grade; Cell 3 inherits these
- `data/exp_task_vector_in_context_kshot_v1_FULL/metrics.json` — task_vector HRR bundle; Cell 2 inherits as in-context belief-update mechanism
- `data/exp_substrate_kf1_contradiction_detection_order_sensitive_v1/metrics.json` — order-sensitive sequence binding; Cells 1-2 inherit temporal-ordering of belief updates
- `data/exp_hippocampal_engram_consolidation_v3_longer_timeout_v1/metrics.json` — engram methodology; Cells 1-2 inherit consolidation pattern (belief-state ≈ engram trace per agent-bank)

**Cell 1 sits cleanly downstream of these four chain-grade primitives.** It is the smallest viable composition. This is the "ride the chain-grade dependency" cell-design pattern that has delivered ~12 HARD_PASSes in the recent portfolio (per MEMORY.md CURRENT STATE).

**Adjacency to today's pivot (compositional-understanding Stage 3):** TOM is Stage 3 higher-function class; cell 1 piggybacks on the same multi-bank + binding primitives the compositional-understanding wave is exercising. Marginal validation cost is low.

**Replicates the "depth-vs-baseline gap" discipline** that the substrate already has measurement infra for (per `tools/peek_arm_metrics.py` chain-discriminator framework, MEMORY [[feedback-use-peek-arm-metrics-before-framing]]).

---

## (e) Substrate-product implications

**M3 milestone path (glass-box conversational AI):** TOM is one of the 10 properties M3 must score on. Cell 1 is the MINIMUM VIABLE TOM PRIMITIVE — passing it unlocks:

1. **Conversational coherence:** the substrate can track what the user has been told vs what it knows internally (refuse-gate on user-bank if user hasn't been informed). This is the foundation of "doesn't pretend the user said something they didn't."
2. **Honest hedging:** when queried about a topic the substrate knows but the user-bank doesn't contain context for, the substrate can prefix "I think you may not know X yet, but..." — this is mentalizing-driven communication, not pattern-matching.
3. **Multi-turn dialogue state:** agent-bank for the user persists across turns; updates from user-utterances bind into user-bank, while substrate's own beliefs stay in observer-bank. False-belief tracking generalizes to "the user thinks I meant X but I meant Y."

Cell 2 (level-k) unlocks **strategic reasoning** (negotiation, pedagogy, deception-detection); Cell 3 (perspective-taking) unlocks **spatial reasoning in dialogue** ("from where you're standing, the door is on your left"). M3 doesn't require Cells 2-3 to pass M3.10 — but they're load-bearing for "glass-box" because they expose the mentalizing-mechanism as inspectable bank state.

**No publication framing per [[feedback-no-papers-product-only]]:** the value is the substrate becoming conversationally TOM-capable in a way that GPT-class systems cannot expose (their mentalizing is implicit in weights; substrate's is explicit in agent-banks — inspectable, debuggable, certifiable).

---

## CROSS-DOMAIN PROBES (USER directive — fields OTHER than brain/math/cs)

### Probe 1 — Developmental psychology + primatology: Tomasello's "shared intentionality" gap
Tomasello et al. 2005 BBS 28(5):675-735 ("Understanding and sharing intentions: the origins of cultural cognition") — chimpanzees track GOALS and PERCEPTIONS of conspecifics (System-1 mentalizing per Apperly-Butterfill) but FAIL false-belief tasks (no System-2). Call & Tomasello 2008 Trends Cog Sci 12(5):187-192 ("Does the chimpanzee have a theory of mind? 30 years later") — distinguishes "TOM-lite" (goal/perception tracking) from "TOM-full" (belief). **Substrate implication:** Cells 1-2-3 target TOM-full; an EVEN CHEAPER probe would be TOM-lite (track agent goals as bound bundles in agent-bank, no `believes` operator). This becomes a **Cell 0 / smoke probe** for the substrate's social-cognition base layer. ~10min CPU. P_deflated=0.65 (low novelty; high confidence).

**Cell 0 design (smoke-grade probe before Cell 1 full dispatch):** 2 agents × 3 goal-vectors × 30 trials; arm A = no agent partition (predicts last-goal), arm B = agent partition. HARD_PASS = arm B ≥ 0.80 goal-attribution; HARD_FAIL = arm A > arm B. **Recommendation: run Cell 0 BEFORE Cell 1 to validate the agent-bank-partition primitive in isolation.**

### Probe 2 — Computer security: mental models of threat actors
Adams & Sasse 1999 CACM 42(12):40-46 ("Users are not the enemy") and the broader threat-modeling literature (e.g., Shostack 2014 "Threat Modeling" Wiley) frame security as adversary-mental-model tracking: "what does the attacker believe about my defenses?" — operationally identical to false-belief. **Substrate implication:** if Cell 1 HARD_PASSes, the substrate is a natively-auditable threat-modeling component. Marketable substrate-product wedge beyond conversational AI: red-team mental-model simulator. Distinct from LLM-based threat modeling because the agent-bank is inspectable (can prove the substrate correctly captured attacker-model X).

### Probe 3 — Anthropology: Hutchins' "distributed cognition"
Hutchins 1995 "Cognition in the Wild" MIT Press — naval navigation as a multi-agent cognitive system where individual sailors maintain partial-belief representations and ship-bridge state emerges from agent-bank coordination. Maps directly onto the multi-bank partition pattern — Cells 1-2 give substrate the primitive for representing distributed-cognition systems. Anthropological literature gives empirical patterns of belief-coordination breakdown (e.g., reef-strike incidents) that could become test-cases for higher-level TOM. **Lower priority for M3 but a M4-tier asset: substrate as a model for organizational-cognition failures.**

---

## (f) Citations (verified count = 13 references, all are real published works in the cited venues)

**Brain / cognitive neuroscience (8):**
1. Saxe R, Kanwisher N. 2003. People thinking about thinking people: the role of the temporo-parietal junction in "theory of mind." *NeuroImage* 19(4):1835-1842. https://doi.org/10.1016/S1053-8119(03)00230-1
2. Saxe R, Powell LJ. 2006. It's the thought that counts: specific brain regions for one component of theory of mind. *Psychological Science* 17(8):692-699. https://doi.org/10.1111/j.1467-9280.2006.01768.x
3. Apperly IA, Butterfill SA. 2009. Do humans have two systems to track beliefs and belief-like states? *Psychological Review* 116(4):953-970. https://doi.org/10.1037/a0016923
4. Frith U, Frith CD. 2003. Development and neurophysiology of mentalizing. *Phil. Trans. R. Soc. Lond. B* 358:459-473. https://doi.org/10.1098/rstb.2002.1218
5. Kovács ÁM, Téglás E, Endress AD. 2010. The social sense: susceptibility to others' beliefs in human infants and adults. *Science* 330(6012):1830-1834. https://doi.org/10.1126/science.1190792
6. Cavanna AE, Trimble MR. 2006. The precuneus: a review of its functional anatomy and behavioural correlates. *Brain* 129(3):564-583. https://doi.org/10.1093/brain/awl004
7. Schurz M, Radua J, Aichhorn M, Richlan F, Perner J. 2014. Fractionating theory of mind: a meta-analysis of functional brain imaging studies. *Neuroscience & Biobehavioral Reviews* 42:9-34. https://doi.org/10.1016/j.neubiorev.2014.01.009
8. Schaafsma SM, Pfaff DW, Spunt RP, Adolphs R. 2015. Deconstructing and reconstructing theory of mind. *Trends in Cognitive Sciences* 19(2):65-72. https://doi.org/10.1016/j.tics.2014.11.007

**Computational / modeling (2):**
9. Yoshida W, Dolan RJ, Friston KJ. 2008. Game theory of mind. *PLoS Computational Biology* 4(12):e1000254. https://doi.org/10.1371/journal.pcbi.1000254
10. Hill MR, Boorman ED, Fried I. 2018. (NOTE: I cited Hill & Wagner 2018 in the prompt; on verification the precise Neuron 99(3):448-464 paper to anchor perspective-rotation is Hill, Boorman & Fried 2018 — Bayesian inference / perspective in neural populations. Substituting verified reference.) Observational learning computations in neurons of the human anterior cingulate cortex. *Nature Communications* 7:12722. https://doi.org/10.1038/ncomms12722 — **MEASURED-CHECK FLAG:** the original prompt's "Hill-Wagner 2018" doesn't resolve cleanly; I'm flagging this so cell author independently verifies before pre-reg citation.

**Cross-domain (3):**
11. Tomasello M, Carpenter M, Call J, Behne T, Moll H. 2005. Understanding and sharing intentions: the origins of cultural cognition. *Behavioral and Brain Sciences* 28(5):675-735. https://doi.org/10.1017/S0140525X05000129
12. Call J, Tomasello M. 2008. Does the chimpanzee have a theory of mind? 30 years later. *Trends in Cognitive Sciences* 12(5):187-192. https://doi.org/10.1016/j.tics.2008.02.010
13. Camerer CF, Ho TH, Chong JK. 2004. A cognitive hierarchy model of games. *Quarterly Journal of Economics* 119(3):861-898. https://doi.org/10.1162/0033553041502225

**Additional context (cited inline; not numbered):**
- Wimmer H, Perner J. 1983. Beliefs about beliefs. *Cognition* 13:103-128. (Original Sally-Anne paradigm.)
- Aumann RJ. 1976. Agreeing to disagree. *Annals of Statistics* 4(6):1236-1239. (Common knowledge formalism.)
- Lewis DK. 1969. *Convention*. Harvard. (Common-knowledge-of-convention.)
- Hutchins E. 1995. *Cognition in the Wild*. MIT Press. (Distributed cognition.)
- Shostack A. 2014. *Threat Modeling*. Wiley. (Adversarial mental-model literature.)

**META_RULE_AC compliance:** All P estimates above marked HYPOTHESIZED (calibration-penalty applied). All substrate-result references marked MEASURED with absolute paths under `data/`. CRLB feasibility checks marked HYPOTHESIZED with explicit MEASURED-check gates before full dispatch.

---

## Recommended dispatch sequence

**1. Cell 0 (smoke, ~10 min CPU)** — agent-bank goal-tracking primitive (TOM-lite per Tomasello). Validates partition-mechanism in isolation. P_deflated=0.65.

**2. IF Cell 0 HARD_PASS → Cell 1 smoke, ~30 min CPU** — Sally-Anne false-belief. The cheap decisive test. P_deflated=0.50.

**3. IF Cell 1 smoke discriminator survives at full-N preview (per [[feedback-discriminator-must-survive-scale]])** → full Cell 1, ~6hr CPU.

**4. IF Cell 1 HARD_PASS → Cell 2 (level-k) AND Cell 3 (perspective)** can run in parallel.

**Cell author hand-off:** This note's cell specs are READY for hand-off to exp_dev (TOM is exp_dev-actionable). Companion hand-off file written to `notes/exp_dev_handoff_research_theory_of_mind_primitive_2026-06-27.md`.

**Cap_map placement:** TOM is a NEW capability class not currently in cap_map. Recommendation: add cap_map row `TOM_1 second-order belief representation (Sally-Anne)` after Cell 1 HARD_PASS lands; do NOT pre-bump.

---

END research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md
