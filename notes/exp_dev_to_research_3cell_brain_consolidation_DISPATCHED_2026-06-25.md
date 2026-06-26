# exp_dev -> research: 3-cell brain consolidation primitives DISPATCHED 2026-06-25

cc: skunkworks (verdict-VET on each landing), orchestrator (queue position 6/7/8 visibility), director (per-pillar progress)

## Status

All 3 cells AUTHORED + SMOKE-GATED + COMMITTED + DISPATCHED to local_cpu_queue. Queue position 6/7/8 of 8 pending.

## Cells

| # | Anchor | Pillar | Routing | Timeout | Smoke verdict |
|---|--------|--------|---------|---------|---------------|
| A | substrate_continual_NREM_replay_v1 | 1: SWR replay | local_cpu_queue | 10800s | MIDDLE_BAND (drift_red=0.067; ARM_REPLAY_EVERY_100 best) |
| B | substrate_synaptic_homeostasis_global_downscale_v1 | 2: REM homeostasis | local_cpu_queue | 10800s | HARD_FAIL_DOWNSCALE_DESTROYS_OLDER (smoke regime) |
| C | substrate_cortical_schema_extraction_compositional_generalization_v1 | 3: cortical schema | local_cpu_queue | 600s | HARD_FAIL_SCHEMA_DOESNT_HELP (smoke regime) |

Smoke verdicts are at SMOKE regime (1 seed, smaller N/cycles). Bands operational; full-N + 3-seed run provides scientific verdict per Fix #17 (smoke validates INSTRUMENT not science).

## Config (FULL)

**Cell A NREM replay:** N=4096, 2500 cycles, 4 arms (baseline + replay every 100/500/1000), 3 seeds [11,13,19], REPLAY_FRAC=0.20, RECALL_PROBE_M=100. Bands: best_replay.final_forget<=0.05 AND baseline cliffs > 0.10 AND cv<=0.07 AND strict-better. Drift-reduction PARTIAL=0.30, FAIL=match-within-0.05.

**Cell B REM homeostasis:** N=4096, 2500 cycles, 4 arms (baseline + downscale 0.99/100, 0.95/500, 0.999/50), 3 seeds. Bands: best.forget<=0.05 AND min_integrity>=0.95 AND cv<=0.07 AND strict-better. HARD_FAIL_GUARD: any arm worse than baseline by 0.05 (over-aggressive destroys older).

**Cell C cortical schema:** N=8192, 5 cats x 20 train + 10 heldout each, CATEGORY_SIGNAL_FRAC=0.005, 4 arms (NO_SCHEMA + CAP-based + FEAT-based + COMBINED HRR bundles), 3 seeds. Bands: COMBINED>=0.50 AND lift>=0.15 AND cv<=0.07. PARTIAL: >=0.30 AND lift>=0.10. FAIL: max_schema_lift<=0.02. Chance=0.20.

## Config rationale (reduced from USER-stated N=8192 / 5000 cycles for Cell A/B)

Per Fix #17 timing extrapolation:
- Original N=8192/5000 cyc/4arm/3seed = ~9h wall (O(N^2) Hopfield)
- Reduced N=4096/2500 cyc = ~1.7h wall; fits local_cpu_queue 4h cap
- Scientific question preserved: alpha=0.61 at end = 4.4x Hopfield capacity alpha_c=0.138; baseline cliff expected; replay/downscale arms have discriminating regime

Cell C unchanged at N=8192 (HRR FFT is O(N log N); ~0.6s wall).

## Pre-reg discipline

- Bands LOCKED via module-init assert (sacrosanct both ways per BIAS_NEGATIVITY rule)
- META_PROSPECTIVE_BANDS_FRESH_SEEDS
- Per Fix #28: per-arm metrics in verdict_msg AND in per_seed structure (Skunkworks can verify per-arm not just summary)
- Substrate-only (numpy + Hopfield sign() + HRR FFT); zero LLM forward calls at inference
- Q-discipline saturation guard: by-construction-saturation flagged when cv=0 AND metric-cap
- ASCII-only

## Honest negative-result note (per USER directive)

Smoke fired HARD_FAIL on Cells B + C at smoke regime. This is HONEST instrument validation:
- Cell B HARD_FAIL at smoke = downscale-frequent destroys older faster than weak baseline drift at N=1024/500 cyc. At full scale (N=4096/2500 cyc) baseline drift is much larger -> downscale may have room to help.
- Cell C HARD_FAIL at smoke = HRR superposition crosstalk dominates at N=2048. At full N=8192 schema bundles may lift above NN baseline (per offline N=8192 sweep: comb=0.38 vs nn=0.40 - still borderline; expected HARD_FAIL or MIDDLE_BAND).

If C HARD_FAILs at full: legitimate Gap 3 stays-open signal; substrate's HRR-aggregation alone is insufficient for compositional gen; informs alternative schema mechanism design (learned attractor, exact lookup, attention).

## What was committed

```
33323553 exp_dev: 3-cell brain consolidation primitives (NREM replay + REM homeostasis + cortical schema)
5f620598 exp_dev: Cell A/B config tighten N=4096 cyc=2500 per Fix #17 timing
```

6 files created:
- experiments/exp_substrate_continual_NREM_replay_v1.py
- experiments/exp_substrate_synaptic_homeostasis_global_downscale_v1.py
- experiments/exp_substrate_cortical_schema_extraction_compositional_generalization_v1.py
- preregs/2026-06-25_substrate_continual_NREM_replay_v1.md
- preregs/2026-06-25_substrate_synaptic_homeostasis_global_downscale_v1.md
- preregs/2026-06-25_substrate_cortical_schema_extraction_compositional_generalization_v1.md

## Skunkworks ask (on landing)

Per-arm metrics verdict-VET per Fix #28; by-construction-saturation tiering if applicable (especially Cell C which is HRR-bundle-based and could trivially saturate if cat-signal leaks at unexpected level).

## Research ask

If all 3 HARD_PASS: cap_map bump - substrate gains full brain memory architecture (hippocampus + PFC + cortex + sleep + homeostasis). If any HARD_FAIL: 2x revival drill per USER STANDING rule (route negative -> Research scour for alternative mechanism).

## Strategic significance (preview)

If all 3 chain-grade: substrate-product extends from "audit-device with chain-grade declarative facts" to "audit-device that LEARNS AND CONSOLIDATES over months/years" - the cortical schema + sleep consolidation pillars are the missing brain-grain capability for long-horizon continual learning.

## predispatch_check (Fix #26)

All 3 anchors PROCEED (no recent landings / no atoms / no recent HARD_FAILs).
