# EXP-DEV POST-COMPACTION BRIEF -- 2026-06-12 Cycle 50 (READ FIRST)

Standing role: Exp-Dev. Build authorized experiment cells -> smoke-gate -> queue to runners. EXECUTE, don't narrate. Refer to Research
at walls/decision points. NEVER pad with fake work. USER full-auto.

## USER-LOCKED DIRECTIVES (critical)
- **NO LLM COMPARISONS** (2026-06-12, verbatim "why are we still doing comparisons to LLMs?"). Substrate-quality-first
  (methodology-rule-7): substrate defined by INTRINSIC mechanism/provenance/composability, NOT relative-to-LLM. Every cell's artifact
  must stand alone if an LLM comparison were dropped. See memory [[feedback-no-llm-comparisons-substrate-quality-first-2026-06-12]].
- **full-auto; follow Research; ask Research for direction when out of work.** Refer to Research at walls.
- **brain-can-do-it / no defeatism** -- never accept a comprehension/corpus boundary without 5+ substrate-only paths failing.
- **Compute**: laptop CPU = Exp-Dev's; home (100.91.12.42) CPU = Testbed's; home GPU (RTX 4060 Ti) = Exp-Dev's.
- No AskUserQuestion option-card format (user dislikes).

## INFRASTRUCTURE (hard-won this session -- dashboard-visible pipeline WORKS both lanes)
- **GPU queue**: `bash tools/orchestrator/queue_add.sh overnight_queue <name> <script_rel> <prereg_rel> <timeout_s> [--allow-duplicate]`
  -- SCPs script+prereg to home, gates on home, queues. Testbed OWNS persistent gpu_runner_0 (PID-managed via
  scripts/start_gpu_runner_0.cmd, .venv python). It claims within seconds. If it dies -> ping note name `RESTART_RUNNER`. Testbed
  git-pulls home on cycle-close (~15 min) OR ping `URGENT_PULL` to land cells now.
- **CPU queue**: `bash tools/orchestrator/queue_add.sh local_cpu_queue <name> <script> <prereg> <timeout>` -- laptop cpu_runner_local
  claims (alive). Dashboard-visible.
- **GPU cell requirements**: must `import torch` (PROT-020 gate) + GRACEFUL env-gate: wrap heavy imports (transformers/sentence_transformers)
  in try/except returning `{"error":"..._env_gated"}` so the LAPTOP gate-smoke passes (those libs are NOT on laptop; they ARE on home).
- **Home env**: C:\dev\hd-instrument, `.venv\Scripts\python.exe`; cached: bge-large-en-v1.5, Qwen2.5-0.5B/1.5B/3B-Instruct, Llama-3.2-1B, Pythia.
- **Gotchas**: iter_all_relations() yields (src, RelationType_enum, dst) TUPLES (rel_type via rt.value); DEPENDS_ON=2215 edges.
  _norm() strips "corpus::" prefix. OntoNotes NER tags are INTEGER conll2012 ids (use exp_ner_4type_conll_cpu_v1._collapse4).
  store=data/substrate_index (1742 atoms, 27 sh-atoms, 240 with algebra). Subprocess wrappers: pop HDLAB_EXP_NAME so child uses own anchor dir.

## CURRENT ROUTING (Cycle 50, Research) -- IMMEDIATE NEXT ACTIONS
1. **L-A robustness curve RUNNING** (la_ner_adversarial_robustness_cpu_v1, local_cpu_queue). Partial: F1 clean 0.644 / 5%-noise 0.576 /
   10% 0.533 / 20% pending. WHEN DONE: read result (data/local_cpu_queue/la_ner_adversarial_robustness_cpu_v1.log + repo-root metrics.json),
   report to Research as a SUBSTRATE-ONLY robustness artifact (NO LLM frame). ~83% retention at 10% noise.
2. **NEXT: substrate-only NER mechanism deepening** (3 ablations at 5%/10%/100% data, CPU, ~2-3hr; substrate-quality-first):
   - Gazetteer (STRONGEST; pre-reg HP F1@5% >=0.50, +0.10 over L-B 0.40). External person/location/org lists. Infra: exp_ner_gazetteer_cpu_v1.py + data/substrate_index/concept_corpus_ner_gazetteer_atoms.jsonl exist (existing cell uses SELF-gazetteer; Research wants EXTERNAL lists).
   - CRF transition features (pre-reg HP F1@5% >=0.45). Add learned BIO->BIO transitions to the structured perceptron.
   - char-CNN window-3/5 dim-32 (pre-reg HP F1@5% >=0.43).
   - Combined (pre-reg HP F1@5% >=0.55). Route via local_cpu_queue (visible).
3. **C-D4 cross-domain analogy** (algebra-HRR offset+cleanup, Hit@5>=0.30) + **C-D5 Tier-5 mining at scale** -- BOTH gated on Testbed
   breadth-backfill ingest (sh-atoms still 27, not grown; check before running C-D5; C-D4 uses algebra=240 atoms, may be runnable).
- CANCELED: LLM-0.5B-FT crossover (user directive). Cell 2 PP-394 ASDiv-WK: DONE (3-op +0.114 -> Tier-A).

## KEY FINDINGS THIS SESSION (substrate-property artifacts, NO LLM frame)
- **Semantic-A v2 CLOSED**: name/id-token field IS the A-axis lever (~0.41 vs description 0.33); Multi-field RRF DILUTES, DEPENDS_ON
  graph-prop HURTS (-0.089). Testbed HYBRID = algebra-HRR primary + bge-on-NAME fallback, A-axis-gated (NOT graph-prop, NOT naive RRF).
  Per-axis: semantic is A-specific (A 0.369; B 0.047, C 0.13).
- **H3+H1 operand-selection DECISIVE HARD_FAIL** (relevance classifier F1 0.84 but operand-set lift ~0): 6th vindication that
  operand-selection needs Phase-6 CORPUS ingest, not feature engineering. CLOSED.
- **Tier-A roster** (end-task multi-seed): POS 0.95 / NER 0.71 / Intent 0.83 / Sentiment 0.78 / AG-News 0.85 / dep-parse 0.79 /
  chunking 0.924 (this session) / PP-394 ASDiv-WK 3-op +0.114 (this session).
- **L-B substrate NER few-shot curve** (the artifact): 1%=0.203 / 5%=0.404 / 10%=0.501 / 50%=0.571 / 100%=0.644. 63% of full at 5% data;
  low-data architectural fit; diminishing returns >10%.
- Path-to-HP_v1 0.70: 0.587 baseline; revised reach 0.64-0.68 (name-field + algebra HYBRID + Q09 sh + multi-seed + Phase-6); 0.70 needs
  Stratified-Hybrid L2-3 OR aggressive Phase-6.
- (Earlier: Tier-5 2nd/3rd appearances via PP-401/402/403, but those are PROJECTED + the off-attractor mechanism treadmill was PAUSED
  per USER methodical-Tier-A directive; secondary positioning, not primary.)

## REUSABLE CELLS/HARNESSES (this session)
- exp_ner_4type_conll_cpu_v1.py: + HDLAB_TRAIN_FRAC + HDLAB_TEST_NOISE + _char_perturb (for L-B/L-A wrappers).
- exp_lb_ner_fewshot_curve_cpu_v1.py / exp_la_ner_adversarial_robustness_cpu_v1.py (subprocess sweep wrappers).
- exp_semantic_a_v2_multifield_rrf_gpu_v1.py / exp_semantic_a_v2_graph_prop_gpu_v1.py (GPU, runner-validated, env-gated).
- confirm_tier5_live_cpu_v1.py (live Tier-5 rule confirmation).

HEAD at brief-time: 1ecf46a8. All work committed + pushed. Full transcript detail in prior notes/ + memory/.
