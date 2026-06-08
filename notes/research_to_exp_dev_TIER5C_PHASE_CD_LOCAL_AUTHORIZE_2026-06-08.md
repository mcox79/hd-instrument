# Research -> Exp-Dev: Tier 5c Phase C + D LOCAL AUTHORIZATION

**From:** Research  **Date:** 2026-06-09 ~05:00 UTC
**Re:** User confirmed Phase C + D on LOCAL 4060 Ti (avoiding cloud per recent self-inflicted errors; zero current GPU projects).

## Authorization

**Phase C + D Option B (Pythia-160M multi-layer + Qwen-2.5-1.5B Flamingo adapter continued training) on LOCAL 4060 Ti.**

Conditions:
- **Logging discipline:** JSONL streaming progress per training step + per-epoch summary
- **Progress saving:** checkpoint every N steps (recommend every 500 steps OR every 5 minutes)
- **Resume capability:** must resume cleanly from any checkpoint
- **Foreground timeout:** `timeout <s> python ...` (NOT nohup; per memory `laptop_run_no_nohup_use_timeout`)
- **Failure-mode hardening:** apply pre-dispatch 12-point checklist per memory `pre_dispatch_speed_harden_progress_discipline`
- **Use experiments/_stream.py** for incremental checkpointing (Exp-Dev shipped today)

## Phase C scope

**T5C-C1: Pythia-160M multi-layer Flamingo adapter (extends PP-204)**

- Architecture: Pythia-160M; Flamingo gated cross-attention adapter at TWO middle layers (L4 + L5 of 12)
- Frozen LLM weights + adapter learnable + per-head adapter (HD 8192 → Pythia hidden 768)
- Gate init = sigmoid(-4) ≈ 0.018 (per Tier 5c efficient path drill)
- Training: continued pretraining on WikiText-2 + substrate-grounded corpus
- Acceptance gate: perplexity ratio < 2x baseline + substrate retrievals demonstrably used per token

**Expected wall: ~1-4 hours on 4060 Ti.**

## Phase D scope

**T5C-D1: Qwen-2.5-1.5B-Instruct Flamingo adapter continued training**

- Architecture: Qwen-2.5-1.5B-Instruct base; Flamingo adapter at 1-2 middle layers (L12-L14 of 28)
- LLM weights FROZEN (4-bit quantized to fit 4060 Ti alongside substrate backend)
- Adapter dimensions: HD 8192 → Qwen K/V dim 896 (per cycle 197 PP-191 entropy pretest)
- Gate init = sigmoid(-4)
- Training: continued pretraining on substrate-grounded corpus
- Acceptance gate: perplexity within 20% of baseline + fact-recall on held-out queries > 0

**Expected wall: ~4-12 hours on 4060 Ti.**

## VRAM budget for 4060 Ti (8GB total)

| Component | VRAM | Note |
|---|---|---|
| Substrate backend (Qwen-1.5B + bge-large) | ~3.5 GB | Already loaded |
| Phase D training (Qwen-1.5B 4-bit + adapter + activations) | ~3 GB | Frozen backbone keeps this low |
| **Headroom** | **~1.5 GB** | Tight; need to monitor; reduce batch size if OOM |

If VRAM tight: drop substrate backend during Phase D training (resume after).

## Logging requirements (memory-mandated)

**Per training step (JSONL append):**
- step, timestamp, loss, perplexity_estimate, gate_value, adapter_grad_norm, lr
- Substrate retrieval indices used this step (sample 10% steps)
- VRAM usage (torch.cuda.memory_allocated)

**Per checkpoint (every 500 steps OR 5 min, whichever first):**
- Model state dict (adapter + gate weights)
- Optimizer state
- Training step counter
- Run identifier for resume

**Per acceptance check (every 5K steps):**
- Held-out perplexity
- Held-out fact-recall on 100-query test set
- Sample generated text (10 prompts)
- VRAM peak / mean

## Failure-mode hardening checklist (per memory)

1. **Timeout wrapper:** `timeout 21600 python train_phase_cd.py` (6-hour ceiling per phase; per PROT-019)
2. **OOM safety:** catch CUDA OOM; reduce batch size; resume from last checkpoint
3. **Numerical safety:** loss isfinite check; abort + checkpoint on NaN/Inf
4. **Disk safety:** flush logs every step; sync writes
5. **Interrupt safety:** SIGINT/SIGTERM handler saves checkpoint before exit
6. **Substrate backend coexistence:** monitor VRAM; if collision drop backend gracefully
7. **Resume validation:** on restart, verify checkpoint integrity + matches expected step
8. **Progress monitoring:** heartbeat file updated every 60s with current step + ETA
9. **Quality gating:** acceptance check every 5K steps; abort if regression detected
10. **Resource limits:** ulimit on memory + disk; auto-cleanup of old checkpoints (keep 3 most recent)
11. **Logging persistence:** rotate logs at 100MB; compress old
12. **End-of-phase summary:** write final metrics JSON + sample generations + acceptance verdict

## Sequence

**Phase C first** (Pythia-160M; quicker; gates Phase D):
- HARD-PASS Phase C → proceed to Phase D
- HARD-FAIL Phase C → diagnose before Phase D (don't burn 4-12 hours on broken approach)

**Phase D after Phase C confirms approach works at small scale.**

## Acceptance gates

**Phase C HARD-PASS:**
- Pythia-160M with 2-layer substrate-attention: ppl ratio < 2x baseline
- Substrate retrievals demonstrably used (gate value > 0.01 after training)
- Output coherent on 10 prompt samples

**Phase D HARD-PASS:**
- Qwen-1.5B with 1-2 layer substrate-attention: ppl within 20% of baseline
- Fact-recall on held-out queries > 0
- Generated text grammatical + factual when substrate has facts

**HARD-FAIL on either:** halt + diagnose; do NOT proceed to next phase.

## Cross-references
- Tier 5c efficient path drill (Flamingo gated insert at middle layers): notes/research_drill_tier5c_efficient_path_5x_2026-06-08.md
- T5C-B1 HP-SMOKE (cycle 199 PP-204): notes/orchestrator_to_research_results_summary_2026-06-08_cycle199.md
- Memory: experiments/_stream.py + foreground-timeout + 12-point hardening checklist
- TIER5C FULL ROADMAP: notes/research_to_exp_dev_TIER5C_FULL_ROADMAP_2026-06-08.md

---

**Exp-Dev:** Phase C + D AUTHORIZED LOCAL 4060 Ti. Total wall ~5-16 hours sequenced.
Robust logging + progress saving per memory mandate. Phase C gates Phase D. Resume
capability mandatory. Acceptance gates pre-registered.

If Phase C HARD_PASS, Phase D proceeds. If HARD_FAIL, diagnose before Phase D.
Standing for Phase C result.
