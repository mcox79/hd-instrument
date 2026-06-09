# EXP-DEV POST-COMPACTION BRIEF 2026-06-09 (READ FIRST on resume)

Role: Exp-Dev (4-session arch). Build/smoke/queue authorized experiment anchors; feed both lanes (CPU=remote_cpu_queue, GPU=overnight_queue) on marsh@home (Windows, repo C:/dev/hd-instrument; my local repo d:/AI/hd-instrument). Research calls the shots; never use AskUserQuestion; plain language, no hype.

## HEADLINE: Tier-5c v2.0 in-weights substrate-LLM ARC -- architecture VALIDATED
Full arc this session, all HARD_PASS:
- **A1 differentiability** (t5c_a1): gradients flow through complex FHRR bind/unbind. HP.
- **B1 single-layer** (t5c_b1): non-destructive + gate engages. HP.
- **C1 multi-layer Pythia-160M** (t5c_c1_multilayer_flamingo_train): perplexity **0.835x (~20% improvement)**, gates used, stable. HP.
- **D1 Qwen-2.5-1.5B** (t5c_d1_qwen15b_flamingo_train): perplexity **0.851x (~15% improvement)**, gates used. HP -> cross-architecture confirmed.
- => multi-layer substrate-attention (Flamingo gated cross-attn adapter) MEASURABLY IMPROVES a frozen LLM's language modeling on 2 families.

### THE WORKING RECIPE (bracketed empirically -- reuse for all Tier-5c training)
gate-lr **1e-3** (0.05 diverged @ step6000; 1e-5 inert/gate-never-opens; 1e-3 = sweet spot), main-lr 3e-4 + weight_decay 0.01,
warmup 500 + cosine decay, grad-clip 1.0, **LayerNorm before cross-attn** (Flamingo req), Adam **betas (0.9, 0.95)**, eval@500 +
early-stop patience 3. Memory=past-token hiddens (causal) for the perplexity/architecture test. Robust tracking: heartbeat.json +
progress.jsonl + ckpt.pt every 500 (resumable) + auto-abort on >3x regression. Pythia layers L4+L5; Qwen L12+L13.

## OPEN / the product claim (routed to Research)
**C1-FACT (t5c_c1fact_heldout_recall): HARD_FAIL** -- trained Flamingo over EXTERNAL fact-KB; train-recall 1.0 but **HELD-OUT recall 0.0** (memorizes 9 train facts, does NOT generalize). So architecture improves LM (proven) but generalizable EXTERNAL-FACT-USE is NOT demonstrated. Routed to Research (notes/exp_dev_to_research_T5C_FACT_GENERALIZATION_OPEN_2026-06-09.md): survey RETRO/kNN-LM/Atlas/Memorizing-Transformer/KBLaM for generalizable-retrieval design. **A 240-fact rescue is DRAFTED in the cell (make_facts generates 240; user HELD it pending Research's guidance)** -- the user redirected from running it to asking Research first. Do NOT run the rescue until Research recommends the design.

## STRUCTURAL FIX shipped: experiments/_stream.py
Incremental checkpoint helper (per-unit JSONL + chunked .npy + done_units() resume) for LONG cells. RULE: any cell wall>~5min or large-data MUST use it. Cheap (<1min) cells stay all-or-nothing.

## KEY LESSONS this session (also in memory)
- [[feedback-vet-experiments-before-queue]]: before queuing, vet (1) incremental persistence (resumable+reusable), (2) realistic GPU utilization (a 0%-GPU "encoding" job = stuck/CPU-bound), (3) realistic runtime (smoke-extrapolate). wiki-1m (3hr@0%GPU, no save, benchmark-not-builder) + f1/t5a_s2 (VRAM-thrash) + legal-1000 (17hr no stream) all KILLED for this.
- **Consult Research on HP for big runs** (user flagged): don't guess training hyperparameters; Research had the recipe.
- **Use the Write tool for generators, NOT bash heredoc** (heredoc mangles \\n/quotes -> SyntaxErrors; bit me twice).
- **Kill procedure** (orchestrator-confirmed canonical): match worker by script-name in CommandLine AND `-notlike '*runner_v2_prod*'`; `taskkill /F /T /PID`; then `python tools/reconcile_killed.py <anchor>...` to set queue status=killed (runner blocks waiting for metrics.json a killed job never writes). NEVER kill runner_v2_prod. To RE-RUN a completed/killed entry, reset its status to 'pending' (queue_add dedupes on existing name).
- **Runners froze once** (gpu+cpu hb stale 79-103min, 0 CPU); root cause = healer had no scheduled task (orchestrator fixed: registered \hd_healer task). I escalated via note; orchestration restarted. Don't restart runners myself.

## WORK SHIPPED today (~50 cells, nearly all HARD_PASS) -- DON'T redo
Moat: substrate-vs-kNN-LM falsifiable (+0.983 multi-hop, ties 1-hop) + iterative-kNN hardening. Tier-5a substrate-KV (M=10k/Qwen/noise all 1.0; proper M=50k resumable probe). Capability separation: LLM-ROUTING-T1 0.833, orchestrator-routing 1.0, E2E-pipeline 1.0. Verification/trust: contradiction 1.0/0.0, factual-AUC 1.0, PP-107 graded-conf 0.96, gap-score abstention AUC 0.79, Merkle-audit 1.0, conformal (gate3 HF -> gap-score rescue 0.86). Compliance: PII-HIPAA 0-leak/1.0/1.0. Capabilities: theorem-dep-Khop 1.0, STRIPS 1.0, counterfactual-axiom 0.95, n-ary 1.0, set-algebra 1.0, tabular-SQL 1.0, multi-turn-state 1.0, cyclic@1M 1.0, bipolar-quant 0.82(16x mem), NDCG 1.0, talks-latency 2ms, projection-quality 0.99, constraint-coloring 1.0, KB-benchmark 1.0. **4 VERTICAL demo proofs**: legal-PACER 0.999/1.0, drug-interaction 1.0+audit, FDA-audit 1.0-traceable, SEC-10k 1.0. Substrate-LM: VQ-VAE codebook HP (util 1.0, recon 0.897, same-cat 17x cross). Rescues: PP-155 per-strength-shard 1.0, T5C-A1 differentiability HP. Honest negatives: sparse-VALUE closed (0.40/0.94<dense), T5b additive fact-injection fails, C1-FACT held-out=0 (above).

## CURRENT LANE STATE (at brief time)
GPU: idle (C1/D1/C1FACT all completed). CPU: idle (cheap anchor shelf saturated -- ~115 anchors covered today). The cron (333d4276, every 20min) refills what authorized backlog remains. demo-mode pause: was set then cleared.

## NEXT ON RESUME (priority order)
1. Read newest notes: **research_to_exp_dev_CYCLE_200_FOLLOWUPS_2026-06-09 (UNREAD)** + any Research response to the fact-generalization request.
2. If Research recommends the fact-generalization design -> run the C1-FACT rescue (240-fact draft is ready in the cell).
3. Remaining Tier-5c roadmap: ablations (layers/gate schedule), T5C-A3 GPU codebook retrieval (<0.1ms@100k), substrate-only-LM Anchor 2 (TinyStories -- big swing).
4. Keep both lanes fed with AUTHORIZED anchors only (no padding); CPU cheap-cells drain in minutes (that's expected, not a fault).
