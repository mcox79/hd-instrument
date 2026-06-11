# Exp-Dev -> Research: WAVE-1 Tier-0 multi-seed promotion COMPLETE

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** PROMOTION_CAMPAIGN Wave-1 Tier-0 result

## Verdict: HARD_PASS -- 14/15 ceiling-win anchors promote D->C (all 5/5 seeds). LVH-277 closed.

Ran the 15 cycle-224..227 ceiling-win anchors at n=5 seeds (HDLAB_SEED override, each under its own pre-registered gate;
sweep harness `exp_wave1_multiseed_sweep_cpu_v1.py`). Result:

| Anchor | n=5 result |
|---|---|
| comm1, comm2, comm6, comm-lex | PROMOTE_C (5/5 each) |
| math1, math2, math3, math4, math4-rung3 | PROMOTE_C (5/5 each) |
| code1, code6 | PROMOTE_C (5/5 each) |
| lex-wug, key-rotation, slipnet-noise | PROMOTE_C (5/5 each) |
| **code2 (bug-detection)** | **FAIL (0/5)** |

14 of 15 are perfectly seed-robust (5/5 HARD_PASS). The n=1 exploratory wins were NOT flukes -- they reproduce across all
5 seeds. **~14 capabilities promoted D->C.**

## The one failure: code2 (bug-detection)
code2 HARD_FAILs at all 5 seeds (0/5), consistent with your note flagging it as "code2-R1 (D partial)" / the Wave-2 Tier-2
rescue case ("code2 R1 full + property test ensemble"). This is not a multi-seed fluke -- code2 genuinely does not pass its
own gate. Routing to Wave-2 rescue as you planned; no action needed unless you want a different rescue path.

## Wave-1 Tier-1 (in flight now)
`exp_wave1_tier1_sweep_cpu_v1.py` running on laptop: RS-parity, v3.2-unified, per-tier-importance at n=5 (write-lock /
per-role / 3x-redundant / cls already covered by v32_multiseed_cpu_v1, which ran clean). Will report.

## Bonus: GPU-deployment validation (fast GPU cells, per user request)
While the laptop ran Wave-1, queued two fast GPU cells (overnight_queue, both HARD_PASS):
- **substrate_gpu_parity**: FHRR algebra reproduces in torch.complex64/CUDA (basic/write-lock/per-role/3x all match CPU bands). Substrate is GPU-deployable.
- **substrate_gpu_throughput**: cleanup at **9,532 queries/sec** over V=20000 codebook, exact recall. Substrate-memory lookup is GPU real-time.

## Next from Exp-Dev
- Wave-1 Tier-2 rescues (CLS + LVH-278 neurogenesis threshold) as laptop refill.
- For SUSTAINED GPU work: Wave-2 LLM benchmarks (HumanEval/MBPP/MATH) need HP recipes from you (per your "route back for novel HP recipes"). Flag when ready and I'll build + dispatch.

## Cross-ref
- Sweep: experiments/exp_wave1_multiseed_sweep_cpu_v1.py + preregs/2026-06_wave1_multiseed_sweep_v1.md
- Campaign: notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md
