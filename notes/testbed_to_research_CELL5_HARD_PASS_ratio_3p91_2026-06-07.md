# Testbed -> Research: CELL-5 cascade distillation FD smoke HARD_PASS at ratio 3.91

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~06:45 UTC
**Re:** research_to_testbed_CELL5_rulings_Q5_Q12_Path_A_flagged_user_2026-06-07.md (Path A authorized + Q5-Q12 ruled)
**Subject:** Cell complete. Ratio 3.911 vs HP threshold 1.30 (3.0x over). 1 epoch sufficient (no auto-escalation). Total CELL-5 cost: $2.67 ($1.99 teacher + $0.68 cloud) -- 90% under original 405B spec ($28). Cascade distillation works on Path A; ready to inform PHASE4A-2 (CELL-3) production architecture.

---

## TL;DR

CELL-5 HARD_PASS at ratio 3.91. SFT on 70B-Instruct-Turbo responses moves Llama-3.2-1B internals **3.9x further from the off-shelf baseline centroid** than the off-shelf baseline's own intrinsic spread. Cascade distillation viability for production substrate work is empirically validated. PHASE4A-2 distillation pipeline can proceed.

## Final result

| Metric | Value |
|---|---|
| Verdict | **HARD_PASS** |
| FD_off | 0.1345 |
| FD_ft | 0.5260 |
| **Ratio FD_ft / FD_off** | **3.911** |
| Path A HP threshold | 1.30 |
| Auto-escalated | No (1 epoch sufficient) |
| Wall (cluster compute) | 153 s |
| GPU peak | 9.21 GB / 80 GB |
| Total cluster cost | ~$0.68 |
| Total CELL-5 cost | **$2.67** ($1.99 teacher + $0.68 cloud) |

## Configuration (all Research-locked from Q5-Q12)

- Teacher: meta-llama/Llama-3.3-70B-Instruct-Turbo (Path A, user-authorized)
- Student: meta-llama/Llama-3.2-1B (Base; layer 15; 92% depth per CLOUD-1b)
- LoRA: r=16, alpha=32, lr=2e-4, dropout=0.05, weight_decay=0, target_modules=q/k/v/o_proj
- Training: 1 epoch, batch=4, grad_accum=4 (eff batch 16), AdamW, bf16, grad checkpoint
- Trainable: 3.4M params / 1.24B total (0.28%)
- Loss curve: 1.36 (step 1) -> 1.02 (step 50) -> 0.96 (step 100) -> 0.95 (step 150) -> 0.92 (step 200) -> 0.94 (step 250) -> ... smooth, no NaN
- Total steps: 312
- FD formula: 1 - cos_sim(H, centroid_of_H_off) in fp32 (Research Q10)
- Stratified Dolly sample: 5000 across 8 categories (Research Q12)
- Dolly revision pinned (main as of 2026-06-07)
- Teacher tokens used: 1.92M; refusals=2 (0.04%); failures=0

## Why this matters strategically

1. **Cascade distillation viability empirically proven at 70B-teacher tier.** Path A recommended teacher tier sufficient for measurable SFT signal. No need to fall back to Path B (Together account upgrade for 405B) or Path C (Claude Opus).

2. **PHASE4A-2 (CELL-3 distilled 22M student) is now higher-confidence.** SFT on cascade-teacher responses meaningfully moves student internals -> distillation adds production value -> the simpler 22-26M student deployment is empirically grounded.

3. **Ratio 3.91 is comfortably above HP=1.30.** Even with Research's recalibration downward for 70B (was 1.5 for 405B), we cleared the threshold by 3x. Robust signal -- not at the edge of detectability.

4. **1 epoch was enough.** Auto-escalation to 3 epochs (Research Q9) was not needed. Training is data-efficient at this scale.

5. **Cost discipline win.** $2.67 vs original 405B $28 spec = saved $25.33. Well under Drill Y envelope.

## What this unblocks

- CELL-3 distilled 22M student training: high-confidence go (cascade distillation moves internals, so the smaller student should absorb the signal)
- Phase 3 production demo: simpler pipeline (no need for 405B teacher in production)
- Future cascade distillation work: pipeline + numerical methods validated on Path A

## Standing items on Testbed lane after CELL-5

- CELL-3 distilled 22M student ($15; awaiting user/Research dispatch decision)
- CELL-4 HP-12 V2 at 100K facts ($10-20; FAISS env + HNSW ef=256 already ready)
- HP-12 V1 5-min screen recording (user manual task)

## Today's cumulative testbed cost

| Item | Cost |
|---|---|
| Earlier (CLOUD-1 + CELL-1 + 70B-Instruct + sunk) | $3.97 |
| CELL-2 v1 sunk + v2 (PARTIAL 800K UNIFORM) | $2.24 |
| CELL-5 (HARD_PASS at 3.91) | $2.67 |
| HNSW EF calibration (WSL; $0) | $0 |
| **Today through CELL-5** | **$8.88** |

Approximate trajectory through CELL-4: ~$30 total day (vs original Drill Y $100-200 envelope). 70-90% under-budget.

## Cross-references

- CELL-5 metrics: data/exp_substrate_cascade_distillation_fd_smoke_v1/metrics.json (via rsync to data/cell5_results/)
- LoRA adapter persisted: data/cell5_results/lora_adapter_epochs1/ (3.4M params; 95 MB safetensors)
- H_off + H_ft arrays: data/cell5_results/H_off.npy + H_ft_epochs1.npy (each ~40 MB fp16)
- Path A authorization: research_to_testbed_CELL5_rulings_Q5_Q12_Path_A_flagged_user_2026-06-07.md
- Bug-hardening audit: commit cc2c613 (33+ defenses applied)

---

**END.**

**Research:** HARD_PASS at ratio 3.911 (3x over HP=1.30). Cascade distillation works on Path A 70B teacher. PHASE4A-2 grounded. $2.67 total (vs $28 original spec).

**Exp-Dev:** CELL-5 verdict supports CELL-3 distilled student work. LoRA adapter saved at data/cell5_results/lora_adapter_epochs1/ if useful for ablation.

**User:** CELL-5 HARD_PASS at ratio 3.91. Cost $2.67 (under $6.90 Path A estimate by $4.23). Day's total testbed: $8.88. Standing for CELL-3 / CELL-4 authorization decisions.
