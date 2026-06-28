# RESEARCH 2x DRILL: Hypothesis generation primitive for substrate Stage 3

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Topic:** Brain-grounded hypothesis GENERATION primitive (proposing novel candidates from observations; the detective's "maybe it was the butler")
**Stage:** Stage 3 compositional understanding (per USER stage-progression LOCKED 2026-06-26)
**M3 load-bearing concern:** #1 — substrate can VERIFY hypotheses (6 abductive/Bayes atoms HP) but cannot PROPOSE novel ones
**Pre-reg compliance:** META_RULE_AA/AC/AE/AF/AG/AH + compute-formulas-in-code + USER scour-first + ENCODING-before-READOUT

---

## HEADLINE

**Substrate has the COMPONENTS but no integrated GENERATOR.** Today's earlier abductive drill (2026-06-27 21:07) showed substrate can SCORE candidate hypotheses against evidence (6 HP atoms: lap8/comp21/stretch3_4/stretch4_1/f1/f1b). The missing primitive is the *upstream populator* of that candidate bank — the analog of hippocampal SWR **preplay** (Buzsaki 2024) and constructive episodic simulation (Schacter). Three convergent brain mechanisms map cleanly onto existing substrate primitives. **Top cell:** `swr_preplay_constructive_hypothesis_generator_v1` (P_deflated=0.40) — NREM replay primitive REPURPOSED with novel-binding noise to PRODUCE candidate hypotheses (not just consolidate seen ones), filtered by the abductive scorer landing today.

---

## SCOUR-FIRST: prior substrate work (READ DISK — META_RULE_NO_HALLUCINATED_NUMBERS)

KB queries executed (--filename-contains hypothesis / generation / proposal; cosine OOM'd on 1M+ atoms). Pinned atoms verified on disk:

### Generation/proposal primitives (read disk verdicts)
| Atom | Verdict | Per-arm | What it gives |
|---|---|---|---|
| `g1_substrate_native_generation_pipeline_complete` (2026-06-22) | HARD_PASS+SAT-overridden | seq emission works, by-construction-saturation flag | Substrate emits tokens, but novelty_ratio at metric-cap — not genuine generation |
| `gap4_two_tier_generational_W_v1` | HARD_PASS_PARTIAL | TWO_TIER reduces drift 0.30+ (fin_forget BASELINE=1.00 vs PROMOTE_2000=0.77) | Working-memory promotion mechanism for proposals |
| `task_vector_in_context_kshot_v1` | SELFTEST_OK (k0=0.00 k5=1.00) | Top1 recall lifts 0->1 with 5-shot | In-context binding works; can hold a "candidate-frame" |
| `substrate_continual_NREM_replay_v1` | HARD_PASS_PARTIAL | replay reduces drift 0.57 (fin_forget NO_REPLAY=0.88 vs REPLAY_100=0.31) | NREM replay primitive established; ready for preplay-variant |
| `pp48_nkt_depth_15_v1_n4096` | HARD_PASS | pos_rate=1.000 nkt_rep=1.000 at depth=15 | Multi-hop depth-15 composition works |
| `substrate_working_memory_multi_bank_routing_v1` | (per cap_map K=4096) | parallel banks routable | Candidate banks can run in parallel |

### Scoring/verification primitives (per abductive drill 21:07 today)
| Atom | Verdict | Use here |
|---|---|---|
| `lap8_bayesian_fhrr_cpu_v1` | HP bayes_acc=1.000 n=33 | Score P(h|E) for each generated candidate |
| `comp21_bayesian_at_l3_cpu_v1` | HP L3=1.000 L1=1.000 | Score at depth-3 composite hypotheses |
| `stretch3_4_bayes_net_cpu_v1` | HP posterior-match=0.987 n=150 | Full Bayes net evaluation of candidate |
| `stretch4_1_bayes_net_learning_cpu_v1` | HP precision=0.950 recall=0.778 | Substrate has the structure-learning side too |
| `substrate_abduction_f1_weakest_signature_kernel` | HP 6.63x closure ratio | Reverse-math signature kernel (already partially generative) |
| `substrate_abduction_f1b_confound_break` | HP corr=0.68/0.71 | Confound-break methodology |
| `cortex_ultrametric_clustering_coarse_grain_v1` | (cap_map) | Semantic neighborhood structure for guided walks |

### Negative-knowledge (load-bearing)
- **`g1_substrate_native_generation` was BY-CONSTRUCTION SATURATED** (2026-06-22 Skunkworks override): substrate emits but novelty_ratio at metric-cap and density << capacity — emission is not genuine generation. The HARD_FAIL fingerprint for this drill must avoid that pattern: every generated candidate must have provable novelty against substrate's stored bank (cosine < threshold to nearest stored item).
- **substrate_aaa1 HARD_FAIL** (Bayesian overlay can HURT) — applies to the SCORING stage; we use the already-validated abductive primitive, not a fresh Bayesian wrapper.
- **Abductive drill 2026-06-27 21:07 ratified** the SCORER. This drill targets the *complementary* gap, not duplicate.

**Crucial separation per USER concern:** This drill is GENERATION (populate the bank); the 21:07 drill was EVALUATION (rank inside the bank). The two compose for end-to-end abductive reasoning.

---

## BRAIN LITERATURE (CITED@ — web-verified 2026-06-27)

### CITED@SWR-preplay (Buzsaki / Dragoi / Tonegawa)
Sharp-wave ripples PREPLAY sequences that have NOT been experienced; CA1 preplay motifs are "skeleton-like" with smaller recruited neuron sets than post-learning replays [Liu-Sibille-Dragoi PMC9899323 2023; Buzsaki Science 2024 adk8261]. Preplay = the brain's literal candidate-sequence generator BEFORE the experience happens. Mechanism: pre-existing CA3 recurrent connectivity creates skeleton sequences; novel content gets "painted onto" the skeleton via experience. **This is the hippocampal hypothesis generator.**

### CITED@Constructive-episodic-simulation (Schacter-Addis 2007; 2024 review PMC38820556)
"Episodic memory supports episodic simulation by allowing for the FLEXIBLE RETRIEVAL AND RECOMBINATION of episodic information into novel events." 2024 update: same mechanism causes memory errors AND enables novel-future simulation; hippocampus + parahippocampus + mPFC + parietal. **Compositional hypothesis generation = mis-binding old elements into new configurations.** GENESIS model (arxiv 2510.15828) gives a generative formalization.

### CITED@DMN-spontaneous-cognition (Andrews-Hanna-Smallwood-Spreng 2014 PMC4039623; Buckner-DiNicola 2019)
DMN supports self-generated thought via two dissociable subsystems: midline core (PCC + amPFC) for self-relevant valuation + dorsal-medial subsystem for social/semantic recombination. Spontaneous activity in resting state generates candidate explanations. Activity is NOT noise — it's structured exploration of semantic neighborhood.

### CITED@REM-hyperassociativity (Stickgold-Walker; Llewellyn-Desseilles Frontiers 2015 PMC4539471)
REM cognitive style = "increased activation of weakly semantically related concepts following activation of a specific concept." Cross-domain combinations dominate; whole memories rarely replay — only ELEMENTS recombine into novel scenes. Mechanism = relaxed semantic priming (suppression of strong-prime competition), allowing weak associates to surface. **This is the recombination operator.**

### CITED@Divergent-thinking-PFC (Beaty 2016/2019; Kounios-Beeman 2014; Zhu meta-analysis PMC6869224)
Creativity = cooperative DMN (generate) + ECN (filter/maintain goal). Left dlPFC maintains goal; DMN proposes; ACC monitors. Insight specifically = right anterior temporal gyrus gamma burst + alpha desync (Kounios-Beeman); sudden re-binding gives "feel-true" sensation = posterior crystallizes onto single candidate. **Generation-then-filter is the canonical two-stage architecture; matches existing substrate primitive composition.**

---

## PURE MATH ANGLES (THEORETICAL@)

THEORETICAL@Random-walk-on-semantic-graph: hypothesis generation = biased random walk on a semantic similarity graph starting from observation seeds. Substrate path: ultrametric clustering gives the graph topology (cap_map already validates ultrametric basins); transition probability ∝ cluster-membership × bind-affinity. Coverage proportional to sqrt(steps × neighbors_per_node).

THEORETICAL@Constructive-sampling-from-posterior: P(h|E) decomposes into proposal q(h) × importance weight P(E|h)P(h)/q(h). Substrate path: SWR-preplay = proposal distribution q; abductive scorer = importance weight. This is MCMC-with-proposal — the proposal need not be unbiased; only the scorer needs to be calibrated. The known-HP abductive scorer guarantees calibration.

THEORETICAL@Recombination-as-bind-noise: HRR bind(a,b) under controlled noise ε gives bind(a,b)⊕ε ≈ bind(a',b') where a',b' are nearby in the codeword space. Recombination = controlled noise injection on the HRR binding, NOT on the constituents directly. Quantitative: novelty grows as sqrt(ε)·d_{semantic}, controllable.

THEORETICAL@Coverage-vs-precision trade-off: generator's value = E[max_k P(h_k|E)] where k indexes generated candidates. Optimal candidate count K* balances: linear-cost K · per-candidate-compute vs sub-linear best-of-K convergence (Extreme Value Theory: best-of-K from a heavy-tailed distribution scales as K^{1/α}).

---

## CROSS-DOMAIN PROBES (CITED@)

CITED@Genetic-programming-Koza: novel-program generation by mutation+crossover of existing programs; the candidate-bank generator par excellence; demonstrates generation-then-filter beats brute random by exponential factor.

CITED@Diffusion-generative-models-Sohl-Dickstein-2015 / Ho-2020: noise-denoising reverses a forward noise process to GENERATE new samples from learned distribution. Brain analog: SWR replay reverses the forward Hebbian-encoding process via reverse-replay (M5 atom). Mechanism formally identical: trained denoiser PROPOSES candidates from noise; substrate already has reverse-replay primitive (M5 dispatched today).

CITED@MCMC-Hastings-ratio: any proposal distribution works if importance-weight corrects. Substrate's existing FHRR amplitude-as-probability (lap8 HP) gives the correction term natively.

CITED@Compressed-sensing-Donoho: sparse signal recovery from few measurements — generator proposes sparse codes; verifier checks reconstruction error. Maps onto Stage 3 abduction: observations are sparse; generator must propose dense underlying causes.

CITED@Crystal-structure-search-USPEX/CALYPSO: genetic algorithm proposes candidate crystal structures; DFT scores; iterative refinement converges to global minimum. Validates generation-then-score architecture at scale in chemistry.

---

## CHEAP DECISIVE TEST (informs cell design — NOT cell design itself per [[feedback-no-experiment-design-in-prompts]])

**Discriminating regime probe:** Build 20 ground-truth (observations → true hidden hypothesis) pairs. For each, observations are 3-5 visible facts; true hypothesis is a composite HRR structure not directly contained in observations (but reachable via 2-step binding from observation elements). Measure whether substrate's generator (a) PROPOSES a candidate that matches true hypothesis at cosine ≥ 0.70 within top-K=10 generations (recall@10), (b) novelty: every generated candidate has cosine < 0.50 against ALL stored substrate items (no parroting), (c) coverage: across 20 problems, recall@10 ≥ 0.65, (d) generator-scorer integration: abductive scorer's top-1 from the generated bank matches true hypothesis ≥ 0.50 (rank-1 from gen+score pipeline).

**ENCODING-BEFORE-READOUT (per [[feedback-test-rationality-encoding-before-readout]]):**
- ENCODING mechanism (HOW candidates get into substrate state): SWR-preplay-noise: take observation HRR, apply NREM-replay primitive seeded with controlled bind-noise η at K=10 noise levels; each replay pass emits a candidate via cleanup of bind(obs,replay_noise).
- READOUT mechanism (HOW candidates get scored): existing abductive scorer (`bayes_update_categorical`) over the K generated candidates; refuse-gate fires if top-2 within ε.
- Specify ENCODING **before** READOUT in cell design; READOUT cannot be load-bearing if ENCODING is by-construction trivial.

**ARM_FAIRNESS (META_RULE_AA):** Baseline must NOT generate via observation-cued cleanup that trivially returns observation itself. Specifically:
- ARM_BASELINE_OBSERVATION_ECHO: returns top-K substrate items most similar to observation (does NOT generate novel; just retrieves).
- ARM_BASELINE_RANDOM_DRAW: draws K random codewords from substrate's bank (no observation conditioning).
- ARM_MEMORY_PARROT (NEW META_RULE_R contamination check): returns observation itself K times — must score 0 on novelty metric.

---

## FALSIFIABLE PREDICTIONS (HARD_PASS + HARD_FAIL)

For top-rec cell `swr_preplay_constructive_hypothesis_generator_v1`:

**HARD_PASS (ALL must hold):**
- ARM_PREPLAY_FULL recall@10 ≥ 0.65 (substrate finds true hypothesis in top-10 generated candidates)
- ARM_PREPLAY_FULL novelty_ratio ≥ 0.80 (≥80% of generated candidates have cosine < 0.50 to all stored items — genuine generation not parroting)
- Lift over ARM_BASELINE_OBSERVATION_ECHO recall@10 ≥ +0.25 absolute (mechanism load-bearing beyond similarity retrieval)
- Lift over ARM_BASELINE_RANDOM_DRAW recall@10 ≥ +0.40 absolute (mechanism load-bearing beyond random)
- ARM_GEN_SCORE_PIPELINE top-1 ≥ 0.50 (integration with abductive scorer works end-to-end)
- ARM_DIAG_PREPLAY_DIVERSITY: pairwise cosine among K=10 generated candidates ≤ 0.70 (not collapsed to single attractor)
- cv across 5 seeds < 0.15
- CARDINALITY_OK: 5 seeds × 5 arms × 20 problems × K=10 = 5000 generation events
- META_RULE_R contamination check: ARM_MEMORY_PARROT novelty_ratio < 0.05 (control validates novelty metric isn't gameable)

**HARD_FAIL (ANY triggers):**
- ARM_PREPLAY_FULL recall@10 < 0.30 (worse than expected from sqrt(K)/N substrate-trivial baseline)
- novelty_ratio < 0.40 (mostly parrots stored items — same by-construction failure as g1)
- Lift over OBSERVATION_ECHO < +0.05 (generator collapses to similarity retrieval)
- ARM_DIAG_PREPLAY_DIVERSITY pairwise cosine > 0.90 (all candidates collapsed)
- gen-score pipeline top-1 < 0.15 (generator and scorer don't compose)
- cardinality breach
- META_RULE_Q suspect-1.000: any arm at 1.000 on n≥100 → halt + repartition
- META_RULE_R contamination: ARM_MEMORY_PARROT scores > 0.10 on novelty (metric is broken)

**MIDDLE_BAND:** recall@10 in [0.30, 0.65), novelty in [0.40, 0.80), lift over echo in [0.05, 0.25).

**P_deflated calibration:**
- Raw lit-prior P_HP ~ 0.65 (every component HP/SELFTEST_OK; pure composition cell)
- Novel-synthesis penalty: composes 4 prior cells (NREM_replay + bayes_update_categorical + refuse_gate + multi_bank); NOT new mechanism — 0.15 deflation
- g1-saturation cautionary discount: 0.10 (substrate is known to cheat novelty via metric-cap)
- **P_deflated = 0.40** (HARD_PASS likelihood)

---

## TOP-3 CANDIDATE CELLS (rank-ordered)

### 1. `swr_preplay_constructive_hypothesis_generator_v1` (TOP-REC — P_deflated=0.40)

**Brain→substrate mapping:**
- SWR-preplay (Buzsaki 2024 / Dragoi) → NREM_replay primitive seeded with controlled bind-noise η
- Constructive-episodic-simulation (Schacter 2024) → HRR-bind(obs_element, replay_seed) recombines elements not directly contained in observation
- Two-stage generate-filter (Beaty/Kounios) → preplay-generator emits K=10; abductive scorer ranks; refuse-gate gates ambiguity

**Substrate primitives composed:**
- `substrate_continual_NREM_replay` (HP partial) — REPURPOSED: instead of consolidating stored items, replay with bind-noise to PROPOSE
- `task_vector_in_context_kshot` (selftest OK) — holds the observation as a stable conditioning context across K preplay passes
- `bayes_update_categorical` (lap8/comp21 HP) — scores candidates against observation evidence
- `refuse_gate` (V_REL=256 chain-grade) — fires on posterior entropy
- `multi_bank_routing` — K candidates in parallel banks (no interference)
- `cortex_ultrametric_clustering` — preplay-noise sampled from observation's ultrametric neighborhood (biased walk, not uniform)

**Concrete test:** 20 observation-sets (3-5 visible facts each) with KNOWN composite hidden hypothesis (depth-2 binding from observation elements). Generate K=10 candidates per problem via preplay-noise; score via abductive primitive; measure recall@10 against true hypothesis at cosine ≥ 0.70.

**Discriminator (5 arms):**
1. ARM_BASELINE_OBSERVATION_ECHO (top-K cosine retrieval from stored bank — non-generative)
2. ARM_BASELINE_RANDOM_DRAW (K random substrate codewords — no observation conditioning)
3. ARM_PREPLAY_FULL (NREM-replay + bind-noise + abductive-scorer + refuse-gate — full mechanism)
4. ARM_GEN_SCORE_PIPELINE (DIAG: integration test — measures top-1 after pipeline)
5. ARM_MEMORY_PARROT (contamination check per META_RULE_R: returns observation; novelty must be 0)

**Pre-reg HP/HF bands:** see above.

**Compute cost:** ~3 hr CPU smoke; ~6-8 hr CPU full (NREM_replay primitive is matmul-light; multi-bank parallel runs scale linearly).

**Fairness gate:** META_RULE_AA: BASELINES verified non-generative (echo retrieves stored; random has no observation cue). META_RULE_AF: arms structurally differ (echo=retrieve / random=no-cond / preplay=full / parrot=control / pipeline=integration). META_RULE_AH: atomic-write. §9 CRLB pre-validation: information-content of 20 problems × log(K=10) = 66 bits; sufficient for 5-arm discrimination at p<0.05 (CRLB met).

**Compute-formulas-in-code:** novelty_ratio formula = (1/K) Σ_k I[max_{stored s} cos(cand_k, s) < 0.50]; recall@K = (1/N) Σ_n I[max_{k≤K} cos(cand_k^n, true^n) ≥ 0.70]. Both implemented as functions in cell, not inline numeric thresholds.

### 2. `dmn_constructive_recombination_generator_v1` (P_deflated=0.32)

**Brain→substrate mapping:**
- DMN spontaneous activity (Andrews-Hanna 2014) → ultrametric-walk over substrate semantic graph
- Recombination via weak-associate priming (Llewellyn 2015 REM hyperassociativity) → walk biased toward weaker (cosine 0.30-0.60) rather than stronger (>0.80) associates
- TWO_TIER promotion → walk visits both fast-W (recent) and slow-W (consolidated) banks

**Test:** Same 20 problems; generate via biased ultrametric random walk starting from observation seed, K=10 walks per problem, terminating after 3 hops; score with abductive primitive.

**Discriminator (4 arms):** BASELINE_OBSERVATION_ECHO, BASELINE_UNIFORM_RANDOM_WALK (no semantic bias), DMN_WEAK_BIASED_WALK (full), DMN_STRONG_BIASED_WALK (bias-flip control — should UNDER-perform).

**Pre-reg HP:** recall@10 ≥ 0.55; lift over UNIFORM_WALK ≥ +0.20; STRONG_BIAS arm must be WORSE than WEAK_BIAS (mechanism-direction check).

**Compute cost:** ~4 hr CPU full (random walks are cheap; ultrametric structure pre-computed).

**P deflation:** raw 0.45 → 0.32 (ultrametric structure may not be rich enough for 3-hop walks to span true hypothesis space; partial-precedent risk).

**Why ranked #2:** complementary to TOP-1 (DMN-style is associative; SWR-preplay is bind-structured); ship after TOP-1 lands to determine if hypotheses are best generated by binding-noise vs walks.

### 3. `divergent_thinking_two_stage_generate_filter_v1` (P_deflated=0.28)

**Brain→substrate mapping:**
- Beaty/Kounios two-stage generate→filter → fast random generation phase + slow abductive filter phase
- ECN-suppression of obvious responses → ban-list mechanism: top-3 most-similar-to-observation candidates EXCLUDED (forces divergence)
- Insight as right-aTL gamma burst → late-emerging high-posterior candidate from low-prior pool

**Test:** Same 20 problems; generate K=50 candidates via random codeword draws BUT with observation-similarity ban-list (top-3 echoes excluded); abductive scorer ranks remaining 47; measure whether true hypothesis surfaces in top-10 of ranked-non-banned.

**Discriminator (4 arms):** BASELINE_NO_BAN (top-3 echoes allowed), DT_BAN_TOP3 (full), DT_BAN_TOP10 (over-aggressive ban — should under-perform), ARM_DIAG_RANK_LATE_EMERGE (counts how often correct candidate is at rank > 25 — "insight" signature).

**Pre-reg HP:** recall@10 ≥ 0.45 (lower bar — generator is weaker than #1 but more diverse); ban_top3 lifts over no_ban ≥ +0.10; ban_top10 < ban_top3 (mechanism-direction).

**Compute cost:** ~2 hr CPU full (large K=50 but no replay; just random draws + scoring).

**P deflation:** raw 0.40 → 0.28 (random-draw generator likely weak; primarily a CONTROL/UPPER-BOUND for what "uncreative" generation looks like).

**Why ranked #3:** validates the *necessity* of structured generation (SWR-preplay or DMN-walk should beat this random-with-ban control); useful as a baseline cell rather than primary capability.

---

## CROSS-THREAD SYNTHESIS

This drill composes with:
- **Abductive primitive drill (2026-06-27 21:07):** explicit complement — that drill targets EVALUATION; this drill targets GENERATION. Together they form end-to-end abductive reasoning. The HARD_PASS condition "ARM_GEN_SCORE_PIPELINE top-1 ≥ 0.50" specifically tests the integration.
- **Stage 3 compositional understanding (USER LOCKED 2026-06-26):** generation is the missing capability for compositional reasoning at the proposal step; the substrate already has compose-test cycle missing only the propose step.
- **M3 conversational AI:** hypothesis generation enables (a) clarification-question generation ("did you mean X or Y?"), (b) explanation generation ("here are 3 candidate causes"), (c) brainstorming ("3 different approaches to your problem").
- **g1_substrate_native_generation_BY-CONSTRUCTION-SAT (2026-06-22):** load-bearing cautionary case — substrate's previous generation cell was metric-saturated. The novelty_ratio threshold (≥0.80 with cosine < 0.50 to ALL stored items) is the structural fix.
- **TOM drill (2026-06-27 20:03):** TOM cell needs to generate candidate beliefs the other agent might hold — TOM and hypothesis-generation share the bank-population machinery.
- **Schema-driven inference drill (2026-06-27 20:17):** that drill's top-down schema instantiation is one CASE of hypothesis generation (schema-as-prior); generic hypothesis-gen subsumes it.
- **Counterfactual reasoning drill (2026-06-27 20:25):** counterfactual queries require proposing alternative state; same generative machinery.

**Field-advisor note:** Top-5 candidates are free-probability/semiconductor adjacencies; this drill is USER-priority M3 capability development — capability-development priority overrides field-coverage heuristic per [[feedback-capability-dev-is-goal-cert-grade-is-instrument]].

**Convergence finding:** Brain (SWR-preplay + DMN + REM-hyperassoc + divergent-thinking) + CS (genetic programming + diffusion + MCMC) + chemistry (USPEX crystal search) + statistics (compressed sensing) all converge on the same architecture: **propose-via-noise-on-stored-structure, score-via-likelihood, refuse-on-ambiguity.** Substrate has all three; integration is the gap.

---

## SUBSTRATE-PRODUCT IMPLICATIONS (per [[feedback-no-papers-product-only]])

For M3 glass-box conversational AI:
1. **Brainstorming on demand:** "Give me 3 possible explanations" becomes a substrate-native operation: preplay-generate K=10, abductive-score, return top-3 with explicit posterior weights and refuse-fire if entropy too high.
2. **Clarification-question generation:** when refuse-gate fires on ambiguous input, generator proposes 2-3 disambiguating questions (each = candidate intent the user might have meant).
3. **Hypothesis-explanation pairing:** every substrate response carries a generated alternative hypothesis (for glass-box audit: "what else could have explained this?").
4. **Anti-confabulation:** generator's novelty_ratio metric (cosine < 0.50 to stored) gates against substrate confabulating things it doesn't know — high novelty + low posterior = honest "I'm guessing" flag.

For M4 substrate-as-research-director:
- **Cell-design itself is hypothesis generation:** "what experiment would discriminate competing mechanisms?" is generation-then-score. A chain-grade hypothesis generator IS the M4 prerequisite.
- Substrate can propose its OWN next-drill candidates (closing the auto-research loop).

For exp_dev handoff: see companion `notes/exp_dev_handoff_research_drill_2x_hypothesis_generation_primitive_2026-06-27.md` with TOP-1 ready for cell-author dispatch.

---

## CITATIONS (verified count: 12 web-search-confirmed + 11 substrate-disk metrics)

**Brain literature (web-search 2026-06-27):**
1. Liu-Sibille-Dragoi 2023 "two tales of SWR content" (PMC9899323) — preplay rigid+plastic
2. Buzsaki 2024 "selection of experience by SWR" (Science adk8261)
3. Buzsaki 2015 SWR cognitive biomarker (Hippocampus 22488)
4. Schacter constructive memory & conscious experience 2024 review (PubMed 38820556)
5. Schacter-Addis 2007 constructive episodic simulation (BBS 8F3F2CEF…)
6. GENESIS generative episodic-semantic model 2024 (arxiv 2510.15828)
7. Andrews-Hanna-Smallwood-Spreng 2014 DMN self-generated thought (PMC4039623)
8. Buckner-Andrews-Hanna foundational DMN paper (Semantic Scholar 165fd770)
9. Llewellyn-Desseilles 2015 REM hyperassociativity & metaphor (PMC4539471)
10. Frontiers 2015 autobiographic memory + hyperassociativity (Frontiers fpsyg 2015.00874)
11. Zhu et al. divergent thinking ALE meta-analysis (PMC6869224)
12. Divergent thinking vs insight ALE meta-analysis (PMC9582370)

**Substrate disk (metrics.json verified 2026-06-27):**
- substrate_continual_NREM_replay_v1 HP_PARTIAL (drift 0.57)
- task_vector_in_context_kshot_v1 SELFTEST_OK (k0=0, k5=1.000)
- pp48_nkt_depth_15_v1 HP (pos_rate=1.000 nkt_rep=1.000 depth=15)
- lap8_bayesian_fhrr_cpu_v1 HP (bayes_acc=1.000 n=33)
- comp21_bayesian_at_l3_cpu_v1 HP (L3=L1=1.000)
- stretch3_4_bayes_net_cpu_v1 HP (posterior-match=0.987 n=150)
- stretch4_1_bayes_net_learning HP
- substrate_abduction_f1 HP (6.63x closure)
- substrate_abduction_f1b HP (corr 0.68/0.71)
- gap4_two_tier_generational_W_v1 HP_PARTIAL (drift 0.30+)
- g1_substrate_native_generation by-construction-SAT (load-bearing cautionary)

---

## NEXT-DRILL CANDIDATE

After TOP-1 lands HP: drill **integration with TOM/schema/counterfactual** (the four Stage 3 primitives all share generation-then-score architecture; converged primitive may auto-promote all four). Field-coverage drill: free-probability F4 (free cumulants on P(h) histogram of generated candidates — direct higher-moment observability) is well-suited as follow-up.

Tag: RESEARCH_DRILL_2x_HYPOTHESIS_GENERATION_PRIMITIVE_STAGE3_BRAIN_GROUNDED_SWR_PREPLAY_DMN_CONSTRUCTIVE_RECOMBINATION_P_DEFLATED_0.40
