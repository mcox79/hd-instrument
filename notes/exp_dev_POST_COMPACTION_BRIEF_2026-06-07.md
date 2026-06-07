# Exp-Dev POST-COMPACTION BRIEF -- 2026-06-07 (READ FIRST on resume)

**Role:** Exp-Dev session. Build/smoke-gate/queue experiments from authorized Research handoff anchors; report verdicts;
escalate intractable issues to Research. NEVER interpret verdicts into strategy. NEVER ask the user survey questions.

## IMMEDIATE on resume
1. **RE-ARM the 15-min loop** if the ScheduleWakeup was dropped by compaction. See memory `project_exp_dev_15min_loop.md`
   for the exact per-wake task list. delaySeconds=900, self-re-arming.
2. `git pull`; check both queue depths (overnight_queue=GPU, remote_cpu_queue=CPU); check NEW notes in LOCAL repo
   `d:/AI/hd-instrument/notes/` (NOT the stale remote runner notes dir -- that bug cost an hour).
3. Runner: marsh@home (Windows/PowerShell), repo C:\dev\hd-instrument, venv python C:\dev\hd-instrument\.venv\Scripts\python.exe.

## HARD RULES (user-stated this session)
- NEVER use AskUserQuestion (memory: feedback_never_ask_survey_questions). Decide + keep work flowing.
- NO padding / config-inflation to fill queue or runtime. Idle is OK when no genuine work; escalate, don't manufacture.
- Use the WRITE tool for cells, NOT heredoc (heredoc keeps breaking on nested quotes/parens/lambdas).
- Bias HARD toward action; escalate to Research via notes/exp_dev_to_research_*.md WHILE still queuing other work.
- North star (memory: north_star_functional_system_beats_LLMs): deployed system beating LLMs head-to-head at relative size.
  Prefer LLM-comparison/benchmark/product work over substrate-internal drift.

## KEY EMPIRICAL FINDINGS THIS SESSION (all committed; metrics in data/exp_<anchor>/metrics.json)
- **PRIVACY (central commercial thread):** SRHT helps MiniLM but HURTS production Llama-L15 (ZKL 0.22->0.58) -> I caught it,
  Research CANCELLED Authorization-3 SRHT engineering. DP-noise injection ALSO fails (no sigma reaches ZKL<=0.10). R3:
  encoder IS anisotropic (PR/D=0.16) -- anisotropy is the real-key ZKL root cause. Testing 3 cheap fixes (cone-centering /
  rank-randomization / entropy-rotation) + a stacked combined fix -- watch privacy_fixes_* + privacy_combined verdicts.
  Posture: QUALIFIED privacy claim (~2x relative), NOT absolute HIPAA, until a fix lands.
- **NORTH-STAR BENCHMARK (HotpotQA 2-hop, MuSiQue proxy):** naive cosine recall@2hop=0.16; whitening lifts to 0.26 (+63%
  rel); bridge-hop K-hop = same 0.26. Substrate adds REAL measurable multi-hop value but gap to 0.70 target remains.
  NEXT: stronger retrieval / real iterated-pinv K-hop / larger encoder on HotpotQA. (MuSiQue + LongMemEval NOT on runner;
  HotpotQA-distractor IS, HF columnar format: context.{title,sentences}, supporting_facts.{title,sent_id}.)
- **v1 DISTRIBUTED REASONING = GO:** soft-Krum HARD_PASS (recovery 1.0 @ f=4/10 Byzantine); bundle-relay graceful
  degradation (ship 50-LOC pure-relay coordinator, no 2PC); CRDT-quorum + G-Counter order-independent (eventual consistency
  no 2PC). Cell-A: real-KB distractors are COHERENT (c_d=0.48) -> v1 may need semantic sharding (but confidence-threshold
  rescue held K_max=22 -- noise-model calibration tension, flagged to Research).
- **CAPABILITIES proven:** pinv = production write rule (encoder-class-general: MiniLM/BGE/Llama all ~3x+; rescues real
  keys); pinv insert (rank-1 SMW)/delete (downdate)/churn all EXACT + incremental (GDPR erasure works); counterfactual
  replay 100% (EU AI Act do()); MMR fixes anchoring; bf16 no-overflow + capacity-parity at N=65536; causal Mechanism A
  viable (role disambig 1.0); bitemporal+GDPR erasure correct; CRDT/streaming aggregation native.
- **STORAGE:** sparse-W only 2x (NOT the hoped 8x); N-reduction free (alpha_c N-independent); 4-bit-W + modern-Hopfield
  queued; predicate-partition no gain (pinv already full capacity).

## OPEN THREADS / NEXT GENUINE WORK
- Full iterated-pinv K-hop on HotpotQA (close 0.26->0.70) -- THE decisive north-star follow-up.
- Privacy: privacy_combined (stacked cone+rotation) verdict; if it reaches ZKL<=0.14, HIPAA path reopens.
- K-hop noise-model fork (averaging vs distractor) -- Cell A said coherent (c_d=0.48); reconcile with confidence-rescue.
- Backlog anchors not yet built: online_adaptation LoRA-InfoNCE; storage multidim-criteria; TruthfulQA+FActScore pretests
  (next tier after MuSiQue/LongMemEval per benchmark handoff); biological-coordination remaining anchors.
- Research files new handoffs every few min -- the loop pulls them; check newest exp_dev_handoff_research_* each wake.

## DISCIPLINE per cell
--self-test + --smoke gate; ASCII-only; write_metrics(verdict/verdict_msg/elapsed_s/summary); dated prereg; scp; queue_add.sh;
atomic commit+push (git add only REPO paths). capacity=Hopfield-exact-recovery sign keys; real-encoder=ZCA-whiten+pinv;
causal-LM=last-token pool + left-pad; use_safetensors for .bin on torch<2.6; W-free GPU + expandable_segments + VRAM<12GB
cap N<=16384 + empty_cache; pinv W + argsort OOMs at N=16384 (cap 8192). Gate runs self-test on the runner GPU (different
RNG than local CPU) -- make self-test assertions robust to that.
