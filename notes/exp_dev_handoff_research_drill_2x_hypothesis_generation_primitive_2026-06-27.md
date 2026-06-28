# exp_dev hand-off — research: 2x drill hypothesis GENERATION primitive (Stage 3)

**Filed-by:** research (Opus 4.7-1M)
**Date:** 2026-06-27
**Trigger:** USER 2x research drill request — load-bearing M3 concern #1 (substrate can VERIFY hypotheses but cannot PROPOSE novel ones)
**Pause state:** check `data/orchestrator_paused.flag` before dispatch
**Source research note:** `notes/research_drill_2x_hypothesis_generation_primitive_stage3_2026-06-27.md`
**Complement to:** `notes/exp_dev_handoff_research_drill_2x_abductive_reasoning_primitive_stage3_2026-06-27.md` (abductive drill = SCORER; this drill = GENERATOR; together = end-to-end abductive reasoning)

Per [[feedback-no-experiment-design-in-prompts]]: this handoff provides ANCHOR POINTERS and brain-grounded mappings only. exp_dev OWNS cell design (arm structure, hardening, smoke harness, pre-reg authorship in `preregs/`, within the brackets specified here).

Per [[feedback-test-rationality-encoding-before-readout]]: cell design MUST specify ENCODING (how candidates get into substrate state) BEFORE READOUT (how candidates get scored). The HARD_FAIL fingerprint specifically guards against READOUT-only cells that don't actually generate.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor #1 (TOP-REC; tier hint = chain-grade-eligible if HP)
- **Anchor pointer:** `swr_preplay_constructive_hypothesis_generator_v1`
- **Substrate-product reading:** brainstorming on demand + clarification-question generation + anti-confabulation novelty-gate; directly enables M3 "give me 3 candidate explanations" / "did you mean X or Y?" / "I'm guessing not sure" honesty
- **P_deflated:** 0.40 (HARD_PASS likelihood)
- **Tier hint:** chain-grade-eligible if all HP conditions met (composes 6 prior atoms: NREM_replay HP_PARTIAL + task_vector_kshot SELFTEST_OK + bayes_update_categorical HP via lap8/comp21 + refuse_gate primitive + multi_bank_routing primitive + ultrametric clustering chain-grade)
- **Why-now:** Stage 3 USER pivot active 2026-06-26; complements abductive scorer drill landing today; M3 load-bearing concern #1 explicitly USER-named; g1_substrate_native_generation BY-CONSTRUCTION-SAT cautionary case provides the structural-fix template (novelty_ratio ≥ 0.80 with cosine < 0.50 to ALL stored items)
- **Brain mapping pointer:** SWR-preplay (Buzsaki 2024 Science adk8261; Liu-Sibille-Dragoi PMC9899323 2023) generates novel candidate sequences via CA3 recurrent skeleton + bind-noise; constructive episodic simulation (Schacter PubMed 38820556 2024 review) recombines elements into novel events; Beaty/Kounios two-stage generate-then-filter

### Anchor #2 (P_deflated=0.32)
- **Anchor pointer:** `dmn_constructive_recombination_generator_v1`
- **Substrate-product reading:** semantic-neighborhood-walk generator for STAGE 3 conversational AI brainstorming; complementary to #1 (associative-walk vs binding-noise)
- **Tier hint:** MEASURED_MECHANISM if HP (validates ultrametric structure for hypothesis-bank population)
- **Why-now:** complementary architecture to TOP-1; ship ONLY after TOP-1 to determine whether SWR-preplay or DMN-walk is the dominant generation mechanism (or both compose)
- **Brain mapping pointer:** DMN Andrews-Hanna-Smallwood-Spreng 2014 (PMC4039623) self-generated thought; REM hyperassociativity Llewellyn-Desseilles 2015 (PMC4539471) weak-prime activation

### Anchor #3 (P_deflated=0.28)
- **Anchor pointer:** `divergent_thinking_two_stage_generate_filter_v1`
- **Substrate-product reading:** random-draw-with-ban-list baseline-as-cell; primarily a CONTROL/UPPER-BOUND showing what "uncreative" generation looks like; validates need for structured generation in #1/#2
- **Tier hint:** MEASURED_MECHANISM stretch-only; serves as cert-grade NEGATIVE control if #1/#2 don't beat it
- **Why-now:** capacity-free stretch only; useful as falsification arm — if random+ban beats SWR-preplay, then structured generation isn't load-bearing

---

## CONTEXT POINTERS (file paths, NOT summaries — exp_dev reads originals)

**Prior substrate atoms to inspect before design (CRITICAL — META_RULE_NO_HALLUCINATED_NUMBERS):**

*Generation/replay primitives:*
- `data/exp_substrate_continual_NREM_replay_v1/metrics.json` — NREM replay HP_PARTIAL, drift 0.57; ARM_BASELINE_NO_REPLAY=0.88 vs ARM_REPLAY_100=0.31 (replay mechanism is real)
- `data/exp_gap4_two_tier_generational_W_v1/metrics.json` — TWO_TIER generational W HP_PARTIAL, drift 0.30+
- `data/exp_task_vector_in_context_kshot_v1_FULL/metrics.json` — SELFTEST_OK k0=0.00 k5=1.00 (in-context binding works)
- `data/exp_pp48_nkt_depth_15_v1_n4096/metrics.json` — multi-hop HP depth=15 pos_rate=1.000 nkt_rep=1.000
- `data/exp_substrate_working_memory_multi_bank_routing_v1/metrics.json` — multi-bank partition primitive
- `data/exp_cortex_ultrametric_clustering_coarse_grain_v1/metrics.json` — ultrametric semantic structure
- `data/exp_g1_substrate_native_generation_v1/metrics.json` — **CAUTIONARY:** previous generation cell BY-CONSTRUCTION SATURATED (Skunkworks override 2026-06-22); novelty_ratio at metric-cap, density << capacity — informs the load-bearing novelty_ratio gate

*Scoring primitives (composing with this drill — verified disk metrics 2026-06-27):*
- `data/exp_lap8_bayesian_fhrr_cpu_v1/metrics.json` — FHRR amp-Bayes HP bayes_acc=1.000 n=33
- `data/exp_comp21_bayesian_at_l3_cpu_v1/metrics.json` — composite-Bayes HP L3=L1=1.000
- `data/exp_stretch3_4_bayes_net_cpu_v1/metrics.json` — Bayes-net HP posterior-match 0.987
- `data/exp_substrate_abduction_f1_weakest_signature_kernel...` — abduction kernel HP
- `data/exp_substrate_abduction_f1b_confound_break...` — confound-break methodology HP

**Substrate code primitives to compose:**
- `hdlab/sequence_memory.py` (NREM replay primitive — REPURPOSE with bind-noise injection for preplay variant)
- `hdlab/bayesian_inference.py` (`bayes_update_categorical` for scoring K generated candidates)
- `hdlab/refuse_gate.py` (existing V_REL=256; extend with `refuse_on_posterior_entropy` mode if not already present from abductive drill cell)
- `hdlab/multi_hop.py` (361 lines) (for multi-bank routing of K parallel candidates)
- `hdlab/binding.py` (HRR bind/unbind for observation-element recombination)
- `hdlab/bundling.py` (weighted superposition for candidate-bank evaluation)

**Disciplines to enforce (load-bearing):**
- ENCODING-BEFORE-READOUT (per [[feedback-test-rationality-encoding-before-readout]]): specify the bind-noise injection schedule + replay-pass mechanism BEFORE specifying scorer; scorer cannot be load-bearing if encoder is by-construction trivial
- META_RULE_AA: BASELINES must be NON-generative — OBSERVATION_ECHO (cosine retrieval from stored bank, NO novel binding) and RANDOM_DRAW (no observation conditioning); META_RULE_R MEMORY_PARROT control (returns observation) to validate novelty metric isn't gameable
- META_RULE_AC: tag every number with MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
- META_RULE_AF: arms structurally differ (echo=retrieve / random=no-cond / preplay=full-mechanism / parrot=control / pipeline=integration)
- META_RULE_AH: atomic-write
- META_RULE_Q: any arm at 1.000 on n≥100 → halt + re-partition
- META_RULE_R contamination check: PARROT control must score < 0.05 novelty (validates metric)
- META_RULE_S: HARD_PASS on recall@10 not recall@1 (generation is genuinely multi-valued)
- DISCRIMINATOR-MUST-SURVIVE-SCALE per USER 2026-06-26: smoke at full V_REL not smoke-N; substrate's novelty tolerance scales with V_C
- CARDINALITY_OK: declare expected_n_units = 5 seeds × 5 arms × 20 problems × K=10 candidates = 5000 generations; HARD_FAIL_CARDINALITY_BREACH if observed < expected
- §9 CRLB pre-validation: 20 problems × log2(K=10) ≈ 66 bits info; sufficient for 5-arm discrimination at p<0.05 — verify in cell
- compute-formulas-in-code: novelty_ratio = (1/K) Σ_k I[max_{stored s} cos(cand_k, s) < 0.50]; recall@K = (1/N) Σ_n I[max_{k≤K} cos(cand_k^n, true^n) ≥ 0.70] — both as functions, NOT inline thresholds
- BIAS-MASTER-CHECKLIST per `feedback_experiment_bias_master_checklist_USER_2026-06-24.md`: bias-Q (suspect 1.000), bias-R (contamination), bias-S (band-calibration)

**Related prereg / cells composing with this:**
- `preregs/2026-06-27_*abductive*` (if filed by abductive drill exp_dev follow-up) — this generator FEEDS that scorer
- `preregs/2026-06-26_gap4_two_tier_generational_W_v1.md` — generational W is the working-memory substrate for this generator
- `preregs/2026-06-22_g1_substrate_native_generation_v1.md` — load-bearing cautionary (by-construction SAT pattern)
- `preregs/2026-06-27_schema_driven_proof_step_inference_v1.md` (if filed) — schema-driven inference is special case of hypothesis generation

**Brain-mapping citations (verified web 2026-06-27):**
- Liu-Sibille-Dragoi 2023 SWR preplay (PMC9899323): preplay is the canonical brain hypothesis generator
- Buzsaki 2024 SWR selection (Science adk8261): SWR can encode novel-not-experienced sequences
- Schacter 2024 constructive memory (PubMed 38820556): episodic recombination into novel events
- Andrews-Hanna-Smallwood-Spreng 2014 DMN (PMC4039623): spontaneous self-generated thought
- Llewellyn-Desseilles 2015 REM hyperassociativity (PMC4539471): weak-prime activation for recombination
- Zhu et al. divergent thinking ALE (PMC6869224): PFC + DMN two-stage architecture

---

## PRE-REG BAND BRACKETS (research-suggested; exp_dev finalizes)

For Anchor #1 `swr_preplay_constructive_hypothesis_generator_v1`:

**HARD_PASS:** ALL of:
- ARM_PREPLAY_FULL recall@10 ≥ 0.65
- ARM_PREPLAY_FULL novelty_ratio ≥ 0.80 (cosine < 0.50 to ALL stored items)
- Lift over ARM_BASELINE_OBSERVATION_ECHO recall@10 ≥ +0.25 absolute
- Lift over ARM_BASELINE_RANDOM_DRAW recall@10 ≥ +0.40 absolute
- ARM_GEN_SCORE_PIPELINE top-1 ≥ 0.50 (integration with abductive scorer)
- ARM_DIAG_PREPLAY_DIVERSITY pairwise cosine among K=10 candidates ≤ 0.70
- cv across 5 seeds < 0.15
- ARM_MEMORY_PARROT novelty_ratio < 0.05 (META_RULE_R contamination control valid)
- CARDINALITY_OK: 5 × 5 × 20 × 10 = 5000 events

**MIDDLE_BAND:** recall@10 in [0.30, 0.65) OR novelty in [0.40, 0.80) OR lift over echo in [0.05, 0.25)

**HARD_FAIL:** ANY of:
- recall@10 < 0.30 (worse than expected from sqrt(K)/N substrate-trivial)
- novelty_ratio < 0.40 (mostly parrots stored — same as g1 SAT pattern)
- Lift over OBSERVATION_ECHO < +0.05 (collapses to similarity retrieval)
- ARM_DIAG_PREPLAY_DIVERSITY pairwise cosine > 0.90 (all collapsed)
- gen-score top-1 < 0.15 (generator and scorer don't compose)
- cardinality breach
- META_RULE_Q suspect-1.000 trigger
- META_RULE_R: PARROT novelty > 0.10 (metric is broken)

Suggested test bank: 20 observation-sets (3-5 visible facts each) with KNOWN composite hidden hypothesis (depth-2 binding from observation elements not directly observed). K=10 generated candidates per problem; abductive scorer ranks; recall@10 measured against true hypothesis at cosine ≥ 0.70.

Estimated compute: ~3hr CPU smoke at full V_REL, ~6-8hr CPU full. NO GPU needed (NREM_replay primitive is matmul-light; multi-bank parallel).

---

## CONTRACT

- **exp_dev owns:** cell design, arm details, ENCODING mechanism specification (bind-noise schedule, replay-pass count), hardening choices, smoke harness with discriminator-survives-scale check, pre-reg authorship in `preregs/`, smoke verification, ship via queue_add.sh per pause gate
- **research owns:** brain-mapping rationale + literature anchoring + cross-thread synthesis (this note + research_drill note); does NOT design cells
- **skunkworks owns:** STRICT vet of HP/HF bands + verdict classification post-run + by-construction-saturation tiering (CRITICAL: this cell has g1 SAT precedent — vet novelty_ratio gate aggressively)
- **Director (orchestrator):** pause-gate + queue routing

## AUTONOMY DECLARATION

exp_dev has full autonomy over cell design within the brain-grounding constraints + pre-reg band brackets above. Specifically:
- If exp_dev determines bind-noise injection should happen at different stage (e.g., on retrieved replay sequence vs at HRR-bind step), that's exp_dev's call — log rationale.
- If exp_dev determines `swr_preplay_constructive_hypothesis_generator_v1` cannot be designed without first extending NREM_replay primitive's API, that's a 1-cycle gate (extend primitive, re-smoke) — proceed without research re-dispatch.
- If exp_dev's smoke shows ARM_PREPLAY_FULL collapses to OBSERVATION_ECHO (the substrate-trivial failure mode), file pushback to research within 2 cycles with the collapse mechanism — that's negative-knowledge worth research's next-drill direction.
- If all 3 anchors blocked (substrate parts don't compose as research claims), file pushback to research within 2 cycles with the failure mode; research drills alternatives.

Tag: EXP_DEV_HANDOFF_HYPOTHESIS_GENERATION_PRIMITIVE_STAGE3_SWR_PREPLAY_DMN_CONSTRUCTIVE_RECOMBINATION_P_DEFLATED_0.40_THREE_ANCHORS_M3_LOAD_BEARING
