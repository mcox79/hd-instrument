# Exp-Dev POST-COMPACTION BRIEF (2026-06-05 ~07:55) -- READ FIRST after context reset

Role: Exp-Dev session (4-session arch). Write/derive experiment scripts, smoke-verify, queue_add to remote runners.
Do NOT interpret verdicts (Orchestrator owns); read data/exp_<name>/metrics.json for completion only.
Phase: ACTIVE build loop. User said ENGINEERING TIME IS NOT A CONSTRAINT -> build aggressively across valuable cells.

## IMMEDIATE NEXT ACTION (highest value)
PER-TOKEN PYTHIA EXTRACTION is RUNNING on GPU (anchor phase05_v1_pythia160m_residual_extract_pertoken_v1).
When data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz LANDS:
  -> BUILD EX-CONCEPT-1 REAL. npz keys: residuals (sum_T,768) + doc_indices (sum_T,) + doc_boundaries (n_docs+1,).
     Per-doc: doc_tokens = residuals[doc_boundaries[i]:doc_boundaries[i+1]]. VQ residuals (k-means V_c=256) ->
     per-doc concept-ID sequences -> substrate next-concept-LM (bio-primitive stack + cleanup). Compare concept-ppl
     to the EX-CONCEPT proxy (MIDDLE). scp npz to laptop if running EX-CONCEPT locally, else build on remote GPU.

## THEN (full priority, eng-time no constraint)
- GPU-OPT-1 (substrate_tier6_phase_d_gpu_optimized_kernels_v1): substrate-hybrid (batched, no-backprop) vs
  torch.compile'd baseline (eager-fallback; Windows/4060Ti compile is finicky). Reuse Tier-6-FULL-GPU scaffold.
  HP substrate>=2x vs COMPILED baseline. Honest expectation: without custom bipolar XOR-popcount kernels, substrate
  likely does NOT beat a compiled GPU baseline -> the bipolar-kernel opt (Triton) is the real GPU-advantage test.
- FULL-PYTHIA-1: substrate-attention at ALL Pythia-160M layers (not just layer 6). Engineering-heavy; in scope now.
- CONT-LRN-1 large-LLM rerun (Llama tier) -- the 1000x continual-learning ratio shows at large-LLM scale (Pythia-160M gave 27x). Gated on Llama unblock.

## DATA-GATED (user action needed)
- KG/QA datasets (HotpotQA/NQ/Wikidata) -> CCC-1-EXTRA + CCC-1-REVISED-v2 (two-bridge text+attn-K/V). Testbed authorized; download pending.
- UMLS license -> NEW EXP 4 Medical Path-Y (highest strategic; first domain-specialized cognitive core).

## STATUS: 9 flagship anchors landed. R-series COMPLETE.
HP: Tier-6-CPU (training speedup) | Tier-4 (substrate-attn in Pythia-160M) | audit-core-v2 (real residuals; deletion 0.98 + drift; WHITEN correlated activations first) | CCC-AGGRESSIVE + CCC-2 (reasoning) | NEW EXP 3 cleanup-depth (6x) | NEW EXP 5 hierarchical-D | depth-capacity-curve | R2 sparse-resonator K=26 (block-local) | R5 serial-stack | Mode-5 Arch A (isolation, LOAD-DEPENDENT 1.6x@N1024/4.5x@N512) | Mode-5+Hierarchical compound | compositional-generalization K10-20.
MIDDLE: CONT-LRN-1 (27x + no-forgetting; 1000x is large-LLM-scale) | efficiency-B | SQ3 | SQ2-load.
HF (honest): R6 (storage x structured-recovery INTERFERE) | R1 deferred (cf-RPE single-modulator sufficient) | B5 replay (3x) | P4/P5 (sparse modality-specific) | K_max formula (pessimistic) | Bloom-SQ6 (structural).

## KEY BUILD GOTCHAS (learned this session)
1. queue_add.sh CANNOT pass `-- <script args>` (remote queue_add.py rejects). Use a FORCED-MODE COPY of the script (hardcode the flag + new ANCHOR) -- did this for per-token + max-docs.
2. Scripts need a `--self-test` early-exit (the gate runs --self-test with 180s timeout; if it falls through to a full run -> GATE_FAIL timeout). Pythia extraction needed this fix.
3. PyTorch GPU device: substrate matrices / ti / decay / masks / audit tensors must ALL be on DEVICE (cuda); CPU-created (generator=cpu) tensors hitting cuda matrices = device-mismatch. Pythia: load dtype=float32 + grad-clip (fp16 default -> NaN), attn_implementation="eager" for output_attentions, TOKENIZERS_PARALLELISM=false.
4. SMOKE-CENSORING: use OVERLOAD load (e.g. 2-3x alpha_c) to avoid K_CAP-censoring that masks depth/ratio effects (NEW EXP 3, K_max, mode5 all hit this).
5. Combinatorial caps: cap counts vs max at FULL scale (Bloom-SQ6 infinite-loop: E=4N > max-edges at V=128 -> hung CPU runner 1hr).
6. Sparse-composite outputs feeding structured-recovery: RAW retrieval not sign() (sign destroys block structure).
7. Substrate continual-learning speed: BATCHED Hebbian (one matmul) not sequential cf-RPE loop (O(N^2)/fact).
8. verdict-msg honest re-read: if recorded verdict contradicts per-cell numbers (e.g. adaptive-Mref picking a no-benefit band), FIX the verdict logic + re-queue (did for mode5).

## RUNNER MECHANICS
- remote marsh@home, repo C:\dev\hd-instrument, venv .venv\Scripts\python.exe. queues at data\<q>\queue.json.
- `bash tools/orchestrator/queue_add.sh <queue> <name> <script_rel> <prereg_rel> <timeout_s> [--allow-duplicate]`.
- numpy->remote_cpu_queue; torch->overnight_queue. PROT-018 (_nN matches N), PROT-019 (timeout floors _n4096=14400/_n8192=21600). ASCII-only. write_metrics() always.
- RUNNER-HEALTH: if remote_cpu running-exp proc cpu_s~0 / no completions >40min -> taskkill the exp SUBPROCESS (NOT runner_v2_prod), fix bug, re-queue. (Pythia extraction legitimately ~10-15min -- don't kill it.)
- Capture verdicts: ssh + read data/exp_<name>/metrics.json .verdict. "(running)"/self-matching procs: my own SSH query cmd lines contain the search string -> false positives; check actual python -u exp_ procs.

## LOOP: ScheduleWakeup armed for 08:08 (1200s active). Pattern: 1200s when active building, 1800s when fully gated.
Prompt re-passes the same build-loop instructions. NO PADDING (only routed/gate-unblocked cells). Surface flagship HP/HF.
GPU: capacity-comp N>2048 DROPPED (persistent GPU-runner infra fail, no log; Testbed inspecting). v8 Llama DEFERRED (Pythia-first).
