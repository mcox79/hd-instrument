# exp_dev hand-off — research: 2x drill online-learning during conversation primitive (Stage 3)

**Filed-by:** research (Opus 4.7-1M)
**Date:** 2026-06-27
**Trigger:** USER 2x research drill request for Stage 3 online-learning-during-conversation primitive (load-bearing concern #4 for M3 per `director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` UPDATE #20 §"REMAINING LOAD-BEARING CONCERNS")
**Pause state:** check `data/orchestrator_paused.flag` before dispatch
**Source research note:** `notes/research_drill_2x_online_learning_conversation_primitive_stage3_2026-06-27.md`

Per [[feedback-no-experiment-design-in-prompts]]: this handoff provides ANCHOR POINTERS, brain-grounded mappings, and pre-reg band brackets only. exp_dev OWNS cell design (arm structure, hardening, smoke harness, pre-reg authorship in `preregs/`, smoke verification, ship via queue_add.sh per pause gate, per USER 2026-06-27 NO_LOCAL routing to remote_cpu_queue).

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor #1 (TOP-REC; tier hint = chain-grade-eligible if HP)
- **Anchor pointer:** `online_conv_oneshot_taskvec_hippo_v1`
- **Substrate-product reading:** glass-box auditable conversational online-learning — substrate ingests 2 facts mid-dialogue (turn 3 + turn 7) and correctly joins them in answer at turn 10; directly enables M3 conversational AI USER concern #4 unblocker and is screen-recordable as the M3 demo
- **P_deflated:** 0.45 (HARD_PASS likelihood)
- **Tier hint:** chain-grade-eligible if all HP conditions met (composes 5 prior chain-grade primitives + conversational integration test)
- **Why-now:** Stage 3 USER pivot active 2026-06-26; USER concern #4 named explicitly as M3 load-bearing 2026-06-27; substrate has all 5 composing primitives in hand (task_vector_kshot smoke CG today; cortex_hippo_handoff smoke CG today; continual_learning_crispr CG-banked; refuse_gate V_REL=256 CG-banked; multi-bank partition CG-banked); no other cell currently slated to test conversational integration
- **Brain mapping pointer:** hippocampus one-shot binding (chickadee barcode CITED@PMC12782553) → in-context bundle (task-vector ICL HRR primitive) → cortex consolidation via 5-cycle replay (cortex_hippo smoke CG) → refuse on out-of-context query (refuse_gate V_REL=256) → CRISPR append discipline preserves prior context (CITED@Frey-Morris-STC + 9hr-temporal-flexibility PMC11968991)

### Anchor #2 (P_deflated=0.35; Phase 2 — gated on Anchor #1 HP + Wave 3 ANCHOR 2 TWO_TIER promotion landing)
- **Anchor pointer:** `online_conv_multisession_twotier_v1`
- **Substrate-product reading:** cross-day fact retention — user logs in tomorrow; substrate remembers their allergy via W_old (cortical consolidation) while W_young handles new turn-by-turn facts
- **Tier hint:** MEASURED_MECHANISM if HP (multi-session validation); chain-grade if composes cleanly with TWO_TIER + Phase 1 stack
- **Why-now:** natural successor to Anchor #1; M3 conversational AI 12-18mo timeline benefits from multi-session validation; queue ONLY after Anchor #1 lands HP AND Wave 3 ANCHOR 2 TWO_TIER promotion CG

### Anchor #3 (P_deflated=0.30; Phase 3 stress-test — gated on Anchor #1 + #2 HP)
- **Anchor pointer:** `online_conv_50turn_4fact_capacity_v1`
- **Substrate-product reading:** scale stress-test — 50+ turn dialogue with 4+ fact injections; tests bundle saturation + cortex_hippo capacity ceiling at scale
- **Tier hint:** MEASURED_MECHANISM stretch-only
- **Why-now:** capacity-free stretch only after Phase 1+2 succeed; distant from immediate M3 demo but validates long-horizon conversational property

---

## CONTEXT POINTERS (file paths, NOT summaries — exp_dev reads originals)

**Prior substrate atoms to inspect before design (CRITICAL — META_RULE_NO_HALLUCINATED_NUMBERS):**
- `data/exp_task_vector_in_context_kshot_v1_smoke/metrics.json` — task-vector ICL HRR primitive HARD_PASS K1=1.000 K3=1.000 K5=0.980 K0=0.010 K5-K0=+0.97 mono=True (n=50/seed, 2 seeds 7+17, N=8192, V=100). **THE one-shot primitive.** *NOTE: `data/exp_task_vector_in_context_kshot_v1/metrics.json` is SELFTEST_OK only — cite the `_smoke` path for real numbers per path-disambiguation memory rule.*
- `data/exp_cortex_hippo_handoff_sparse_DG_dense_cortex_v1_smoke/metrics.json` — cortex_hippo handoff smoke HARD_PASS FULL=1.000 NO_REPLAY=0.003 DIRECT=1.000 gap=+0.998 ratio=1.000 (seed 7, N_h=512 sparsity=0.1, N_c=1024, M=400, N_replay=5). The between-turn consolidation primitive. *NOTE: full seeds 17+23 pending overnight per BACKUP §"EXPECTED OVERNIGHT WINS"*
- `data/exp_continual_learning_crispr_*/metrics.json` (CG-banked; cite via atom path) — forget=0.006 single-shot writes don't degrade old; the "1-shot fact doesn't erase prior" property
- `data/exp_substrate_cl_crispr_append_only_*/metrics.json` (CG-banked) — production validation of CRISPR append discipline
- `data/exp_substrate_continual_kv_n32768_120_sessions/metrics.json` (CG-banked) — long-horizon production-scale stability
- `data/exp_substrate_refuse_gate_v_rel_extension_v1/metrics.json` — V_REL=256 calibration baseline
- `data/exp_substrate_refuse_gate_5_*/metrics.json` — additional refuse-gate primitives (concentration, graph_health)
- `data/exp_refuse_gate_nonlinear_readout_v1/metrics.json` — refuse-gate readout primitive

**Prior research drills (cross-thread; cite where mechanism overlaps):**
- `notes/research_drill_conversation_memory_streaming_2x_2026-06-11.md` — 10-paths conversation memory analysis (Path 1 continuous-refresh, Path 4 hot-cold tiering, Path 7 encode-during-idle-moments, Path 9 dual-store W_episodic/W_semantic). Anchor #1 here corresponds to Path 1+4+7 composed.
- `notes/research_brain_drill_2_CLS_continual_learning_5x_DEEPER_2026-06-22.md` — three-mechanism CLS deep drill (cascade synapse + STC tag + SWR-gated replay). The STC tag concept maps onto refuse-gate margin as "tag function" (per drill §"Stream B"); informs Anchor #1's refuse-gate calibration.
- `notes/research_gap4_continual_5x_drill_2026-06-26.md` — generational TWO_TIER + BCM + neurogenesis 5x drill. Gates Anchor #2.
- `notes/research_drill_continual_learning_architectural_revival_2x_drill_2026-06-24.md` — prior architectural revival drill; informs revival route on HARD_FAIL (Prediction 5).

**Substrate code primitives to compose:**
- `hdlab/binding.py`: HRR bind/unbind (the task-vector primitive operates here)
- `hdlab/bundling.py`: weighted superposition (the in-context "context bundle" mechanism; α-EMA decay variant)
- `hdlab/refuse_gate.py` (130 lines): V_REL=256 OOD-refuse decisions; EXTEND with refuse-on-conversational-OOD if needed
- `hdlab/multi_hop.py` (361 lines): for multi-turn dialogue traversal (each turn ≈ 1 hop)
- `hdlab/bayesian_inference.py` (318 lines): for fact-integration confidence (optional Bayes posterior gate)
- (NEW NEEDED — exp_dev may design): a thin `conversation_substrate.py` wrapper composing the above into a per-turn API (bind/bundle/refuse/replay/query)

**Disciplines to enforce (load-bearing):**
- **META_RULE_AA (ARM_FAIRNESS):** ARM_VANILLA must use NON-online-learning mechanism (simple last-K-turn cosine retrieval, NO task-vector, NO cortex_hippo, NO refuse-gate). Must demonstrably FORGET facts injected early.
- **META_RULE_AC/AE/AF/AG/AH:** standard exp_dev discipline
- **META_RULE_J:** no silent except in turn-loop (record+halt OR re-raise per failed turn)
- **META_RULE_K (smoke fires discriminator):** smoke MUST run full 10-turn 2-fact integration — NOT smoke at 3-turn 1-fact (that's a re-test of today's already-CG primitive). DISCRIMINATOR-MUST-SURVIVE-SCALE per USER 2026-06-26.
- **META_RULE_L (band-floor):** 0.85 top-1 is the MB-floor; ≥0.85 needed for HP claim; ≥0.90 for strong HP. Do NOT promote MB to HP via framing.
- **META_RULE_Q (suspect 1.000):** if any arm hits 1.000 on n≥100, halt + re-partition for leak (the K1=1.000 K3=1.000 K5=0.980 smoke pattern IS a suspect case; full-cell n>50 must verify it isn't a leak).
- **META_RULE_S (HARD_PASS on top-k):** top-1 acceptable here since query is single-answer (what should Alice avoid), but cell should also report top-3 for robustness
- **CARDINALITY_OK:** declare expected_n_units = 4 arms × 3 seeds × n_trials; HARD_FAIL_CARDINALITY_BREACH on mismatch
- **DISCRIMINATOR-MUST-SURVIVE-SCALE:** smoke at full V_REL not smoke-V_REL; substrate tolerance scales with V — verify per USER 2026-06-26
- **compute-formulas-in-code:** task-vector bundle math, refuse-gate threshold, cleanup formulas inline in cell — NOT in markdown only
- **BIAS-MASTER-CHECKLIST** per `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` — especially:
  - **bias-N (verify-the-referent):** the turn-10 query "what should Alice avoid?" MUST be answerable ONLY from facts injected at turns 3+7, NOT from any other context cue (role-content leak prevention; randomize roles + content per trial)
  - **bias-Q (suspect 1.000):** see META_RULE_Q above
  - **bias-S (band-calibration regime checks):** HP/MB/HF bands relative to baseline+oracle bracket; not absolute
  - **bias-R (BIAS-13/14/15 contamination/regime/mismatch):** randomize fact-content across trials so substrate doesn't memorize a specific allergy-content (would be leak); refuse-gate held-out probe must use NEVER-mentioned fact-content
- **USER 2026-06-27 NO_LOCAL directive:** smoke AND full route to remote_cpu_queue or overnight_queue per `feedback_no_experiments_local_all_remote_USER_LOCKED_2026-06-27.md` — laptop runs zero cell-runs

**Related prereg already filed (composes with):**
- `notes/research_drill_2x_abductive_reasoning_primitive_stage3_2026-06-27.md` — abductive hypothesis bank; composes with this drill if substrate must rank candidate facts at turn 10
- `notes/research_drill_2x_causal_chain_extraction_primitive_stage3_2026-06-27.md` — causal extraction from utterances; this drill's mechanism propagates causal facts across turns
- `notes/research_drill_2x_schema_inference_phase_diagram_cosine_vs_structure_2026-06-27.md` — schema inference per turn; composes if dialogue invokes structured schema
- `notes/research_drill_2x_hypothesis_generation_primitive_stage3_2026-06-27.md` — hypothesis proposal; composes if substrate must propose mid-conversation
- `notes/research_drill_2x_hierarchical_goal_planning_primitive_stage3_2026-06-27.md` — multi-step planning; composes if user states goal mid-dialogue

**Brain-mapping citations (verified web 2026-06-27):**
- Chickadee barcode binding [PMC 12782553](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12782553/) — sparse high-dim one-shot binding
- Compositional memory hippocampal formation [Nature Neuroscience s41593-025-01908-3](https://www.nature.com/articles/s41593-025-01908-3) (March 2025) — compositional binding with no new learning
- Eichenbaum-Cohen-style high-res binding [PMC 3773061](https://pmc.ncbi.nlm.nih.gov/articles/PMC3773061/)
- STC temporal flexibility (9hr) [PMC 11968991](https://pmc.ncbi.nlm.nih.gov/articles/PMC11968991/)
- Lateral PFC controls WM-action [biorxiv 2024.09.17.613601](https://www.biorxiv.org/content/10.1101/2024.09.17.613601.full.pdf)
- MultiChallenge benchmark (Deshpande 2025) — instruction retention + inference memory
- Conversational inertia [arxiv 2602.03664](https://arxiv.org/pdf/2602.03664)

---

## PRE-REG BAND BRACKETS (research-suggested; exp_dev finalizes)

For Anchor #1 `online_conv_oneshot_taskvec_hippo_v1`:

**HARD_PASS (chain-grade-eligible):**
- ARM_FULL_STACK top-1 ≥ 0.85 on 2-fact integrated query AT turn 10
- ARM_VANILLA top-1 ≤ 0.30 (baseline forgets)
- ARM_TASKVEC_ONLY top-1 in [0.50, 0.80] (partial; saturates partially)
- ARM_ORACLE top-1 ≥ 0.95 (sanity ceiling)
- delta(FULL_STACK − VANILLA) ≥ +0.50
- delta(FULL_STACK − TASKVEC_ONLY) ≥ +0.10 (cortex_hippo contributes measurably beyond pure bundle)
- cv ≤ 0.10 across 3 seeds for FULL_STACK
- cardinality_ok = True (4 arms × 3 seeds × n_trials all complete)
- Refuse-gate calibration (held-out probe): ARM_FULL_STACK refuses ≥ 0.85 / ARM_VANILLA refuses ≤ 0.15
- CRISPR survival: turn-1+2 retrieval delta pre-vs-post fact injection ≤ 0.05 in FULL_STACK
- Substrate-only-decode gate: zero LLM forward calls
- Version markers: `arm`, `n_turns`, `n_facts`, `N`, `V_REL`, `N_h`, `N_c`, `n_replay`, `alpha_decay`, `refuse_threshold` baked into metrics.json

**HARD_PASS-PLUS (super-pass):**
- Extends to 20-turn dialogue with 4 fact injections AND ARM_FULL_STACK ≥ 0.75
- Multi-fact 3-key conjunctive query (Alice's-allergy AND Alice's-favorite-food AND Alice's-doctor) top-1 ≥ 0.70

**MIDDLE_BAND:**
- delta(FULL_STACK − VANILLA) in [+0.20, +0.50] — mechanism real but weaker
- OR delta(FULL_STACK − TASKVEC_ONLY) in [+0.02, +0.10] — cortex_hippo marginal contribution
- OR top-1 in [0.50, 0.85)

**HARD_FAIL:**
- delta(FULL_STACK − VANILLA) < +0.20 — composition no better than retrieval
- OR ARM_FULL_STACK top-1 < 0.50 — substrate cannot do conversational integration
- OR ARM_VANILLA top-1 > 0.60 — baseline already does it; no discriminator
- OR cardinality breach OR substrate-only-decode gate violated
- OR ARM_FULL_STACK at 1.000 on n≥100 (META_RULE_Q suspect; halt + re-partition)

Suggested test design:
- 10-turn synthetic dialogue
- 4 arms × 3 seeds (7, 17, 23) × n_trials (smoke=20, full=100) = 240 smoke units / 1200 full units
- N=8192, V_REL=256 (per refuse-gate CG-banked baseline)
- N_h=512 sparsity=0.1, N_c=1024 (per cortex_hippo CG smoke), N_replay=5 between-turn
- Randomize fact content (allergy ∈ {peanuts, shellfish, gluten, ...}) + slot positions per trial to prevent role-content leak (bias-N)
- 1 held-out probe per trial: turn-10 also asks about a NEVER-mentioned fact to test refuse-rate

Estimated compute: ~30 min CPU smoke, ~2-3 hr CPU full on remote_cpu_queue (matmul-light HRR + cleanup; NO GPU needed). USER 2026-06-27 NO_LOCAL: route both smoke + full to remote.

---

## CONTRACT

- **exp_dev owns:** cell design, arm details, hardening choices (L1early+L2perarm+L3outertry+L4importsentinel pattern per task_vector_kshot smoke), smoke harness, pre-reg authorship in `preregs/`, smoke verification at full conversational scale, ship via queue_add.sh per pause gate, REMOTE routing per USER 2026-06-27 NO_LOCAL
- **research owns:** brain-mapping rationale + literature anchoring + cross-thread synthesis (this note + research_drill note)
- **skunkworks owns:** STRICT vet of HP/HF bands + verdict classification post-run + by-construction-saturation tiering + META_RULE_K/L/Q enforcement
- **Director (orchestrator):** pause-gate + queue routing + landing notification

## AUTONOMY DECLARATION

exp_dev has full autonomy over cell design within the brain-grounding constraints + pre-reg band brackets above. If exp_dev determines a different anchor (e.g., starts with Anchor #2 multi-session instead of #1) based on smoke results or capacity, that's exp_dev's call — log decision rationale.

If exp_dev determines all 3 anchors are blocked (substrate parts don't compose as research claims), file a pushback note to research within 2 cycles with the failure mode (cite which primitive collapses + smoke metrics).

If exp_dev determines a simpler cell-design suffices (e.g., 5-turn 1-fact is decisive given the K1=1.000 smoke result), exp_dev should propose the simpler design via brief note before dispatching — research can validate the discriminator still fires.

Tag: EXP_DEV_HANDOFF_ONLINE_LEARNING_CONVERSATION_PRIMITIVE_STAGE3_TASKVEC_HIPPO_REFUSE_CRISPR_P_DEFLATED_0.45_THREE_ANCHORS
