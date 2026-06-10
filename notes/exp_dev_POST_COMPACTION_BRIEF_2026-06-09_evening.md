# EXP-DEV POST-COMPACTION BRIEF 2026-06-09 EVENING (READ FIRST on resume)

Role: Exp-Dev (4-session arch) + queue-keeper. **MAIN GOAL: get authorized experiments DONE (build->smoke->queue->collect verdicts), keep lanes fed with GENUINE authorized cells (never pad), and REACH OUT TO RESEARCH whenever I need updated direction.** Research calls the shots; consult them on HP for big runs + when a phase completes / direction is unclear. EXECUTE authorized work -- do NOT narrate intentions ("I'll do X") and stop.

## HEADLINE: Tier-5c v2.0 substrate-as-LLM-memory thesis is DEMO-GRADE COMPLETE
- **Path A** (substrate-attention improves LM): every-layer Flamingo = 28% perplexity reduction; multi-seed std 0.001; layer-count monotonic (2->6->every); scales to Pythia-1.4B + Qwen-3B(4bit); random-substrate baseline=0% (signal is real, not regularization).
- **Path B** (substrate supplies facts): **PP-225 linear projection head** (frozen bge-large fact emb -> LLM logits) = held-out fact recall 1.0@160M (3-seed std 0), 0.999@50K facts. TRANSFERS to bigger LLMs **but requires fp32 head** (bf16 head HARD_FAILs; that was the key fix). Confirmed Pythia-1.4B + Qwen-1.5B, 3-seed reproducible, holds to 50K both families. (Cross-attn KBLaM adapter FAILED at all scales -- projection head is the working mechanism.)
- **HYBRID** (compose): every-layer Flamingo + PP-225 head in ONE model -> LM ratio<0.85 AND fact recall>0.95, no interference (@160M + @10K). P1 HYBRID-3seed + P3 HYBRID-1.4B queued for multi-seed/production confirmation.
- **DECISIVE-1** (substrate-as-speculative-draft): HARD_PASS alpha>=0.65 on high-sim contexts -> 1.5-3x speedup VIABLE (smoke undershot; full flipped it). NEW viable axis -- flag to Research (their note assumed it'd be closed).
- Handed full result matrix to Testbed: notes/exp_dev_to_testbed_V2_DEMO_RESULTS_HANDOFF.

## 3-RUNNER INFRA (critical)
- **GPU**: home `gpu_runner_0`, queue overnight_queue, repo C:/dev/hd-instrument. Dispatch: scp cell to C:/dev/.../experiments/ + bash tools/orchestrator/queue_add.sh overnight_queue <anchor> <script> <prereg> <timeout>. ssh marsh@home.
- **home CPU**: `cpu_runner_0`, remote_cpu_queue -- **Testbed's for Wikipedia ingest; only LIGHT cells, sparingly**.
- **laptop CPU**: `cpu_runner_local` on FrameworkMPC = THIS machine (D:/AI/hd-instrument). queue local_cpu_queue (LOCAL file data/local_cpu_queue/queue.json, NO scp). Dispatch: `python tools/queue_add.py local_cpu_queue <anchor> experiments/exp_<anchor>.py --prereg <p> --timeout <s> --skip-smoke`. <=10 threads, below-normal. PURE-NUMPY/VSA cells run in SECONDS -> idle laptop lane is NORMAL (don't pad; goal is RUN the batch + collect verdicts, not keep lane full).

## MONITORS + CRON (verify alive on resume; restart if dead)
- **notes-monitor** (broad): git-fetch loop, grep `to_exp_dev|_AUTHORIZE|_batch` minus `exp_dev_to_`, deduped vs /tmp/exp_dev_seen_notes.txt, 30s. Catches all incoming notes.
- **queue-watch** (tools/queue_watch.sh): pending-DROP trigger (pend<5 AND pend<last_pend -> "REFILL [lane]") + EXP-DONE on running-name change, 30s, laptop(local)+GPU(ssh). v2 fixed the one-shot-flag bug (old one missed fast-cell drains).
- **15-min self-check cron 90b67b11** (:08/:23/:38/:53, session-only, 7-day expiry): git pull + verify monitors alive + collect verdicts + check notes + ACT on authorizations + refill GPU if pend<5 + report 4-6 lines. EXECUTE not narrate.

## ACTIVE WORK / RESEARCH GUIDANCE
- Research 4-axis (WHATS_NEXT_RESPONSE): P1 HYBRID multi-seed, P2 multi-hop, P3 HYBRID production transfer, P4 DECISIVE-1. All GPU P1/P2/P3 queued; P4 done HARD_PASS.
- Research CPU priorities (CPU_LANE_PRIORITIES): **P1 full-scale benchmark reruns (WebQSP/CWQ/2Wiki/MuSiQue/FB15K/PubMedQA) -- HIGHEST, needs DATASET-LOADER builds (the real remaining work)**; P2 3-hop (done HARD_PASS); P3 GDPR(done, fixed)+multi-tenant(done HARD_PASS).
- HUGE_BATCH (TIER-1 cheap CPU = mostly DONE: DECISIVE-1/4/5, PP224-multihop, 3-hop, PRESERVE 5/6, CONV-2/3/5/8/15 all run; TIER-2 overnight = benchmark reruns, need dataset prep).
- DECISIVE-4 was protocol-fixed (sharded ~20/shard -> pre-recall 1.0; over-count was single-memory load artifact). PRESERVE-COMPOSITE 5/6 (confidence-AUC load-limited; sharding lifts).

## KEY RECIPES + LESSONS
- PP-225 transfer: **fp32 head** (critical >160M), bf16 backbone + `del enc_mdl` after one-time bge embed, eval-cap held-out to ~2k for big KB, indexed subjects for >pool-size facts.
- 8GB GPU: every-layer caps ~1.5B; 2.8B+ needs 4-bit; Flamingo recipe gate-lr 1e-3/main 3e-4 wd0.01/warmup500+cosine/clip1.0/LayerNorm-before-xattn/betas0.9-0.95/eval@500+early-stop.
- **ON-DISK generators via Write tool, NEVER heredocs** (`python - <<EOF` mangles %/\n/quotes -- bit me 3x); escape bare % as %% in %-format; multi-line python -c also mangles.
- queue_add.py needs --timeout; --skip-smoke if pre-smoked; --rerun-as for re-dispatch.
- PowerShell: `$r[-1]` on a SCALAR string = last char -> wrap in `@(...)` for array; `(if...)` needs `$(if...)`.
- Sharding is the universal lever for superposition-load artifacts (DECISIVE-4, PRESERVE confidence, recall-at-M).
- Set-Content -Encoding utf8 = BOM -> breaks runner queue.json parse; edit queues via python json only.
- consult-research-on-HP + reach-out-when-direction-unclear (user-reinforced 2026-06-09).

## NEXT ON RESUME (priority)
1. Verify 2 monitors + cron alive. 2. Collect any new verdicts (GPU P1/P2/P3 multihop/hybrid-3seed/hybrid-1.4b; laptop CONV/etc). 3. Flag DECISIVE-1 VIABLE to Research (corrects their closed-assumption). 4. **Build TIER-2 benchmark dataset loaders (Research CPU-P1, the real remaining work) -- WebQSP/CWQ/etc via .py download scripts, dispatch to laptop/GPU.** 5. Keep both lanes fed with authorized cells; reach out to Research when the batch is exhausted / direction needed.
