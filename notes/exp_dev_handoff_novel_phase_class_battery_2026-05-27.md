# exp_dev handoff — 6-cell positive-identifier battery for substrate phase-class identification

**Date.** 2026-05-27
**Owner.** Research → exp_dev hand-off.
**Trigger.** `notes/research_novel_phase_class_methodology_2026-05-27.md` Finding 7 — substrate most likely DOCUMENTED-BUT-UNTESTED (P=0.48 "gated multistable AM / lR-phase" class); secondary NOVEL (P=0.22) requiring SKAH-M declaration; tertiary FINITE-N artifact (P=0.30). Decisive test = 6-cell battery distinguishing the three.

## TASK

Ship a 6-cell battery (`anchor_novel_phase_battery_v1`) on existing Bet B fixtures + one N-sweep extension. Each cell is an independent observable; joint result determines class call.

## WHY

Five-rejection sequence (1-RSB / AGS-RS-multi-ferromagnet / cluster-glass / reaction-diffusion / unified-SVD-cascade) has cleared the standard phase-class space. The 6-cell battery is the structural-positive-identifier follow-up — it tests for the 2024-2026 documented class of "gated multistable AM" BEFORE escalating to novel-class declaration. Outcome shapes product whitepaper framing (academic-legitimate vs novel-declared vs honest-but-N-capped).

## CONTRACT

- Use existing Bet B 4-stage continual-learning fixtures (`data/exp_wave14_betB_4stage_continual_v1/`) for cells C3, C4, C5, C6 at default N=1024.
- New N-sweep fixture at N ∈ {512, 1024, 2048, 4096} for cells C1, C2 (q_EA and plateau heights vs N).
- 5 seeds per cell minimum; report `mean ± std` not raw values.
- Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND bands per cell (see methodology note section b for full table).
- Self-test the q_EA formula and free-energy reconstruction with synthetic Z_3-Potts toy model BEFORE running on substrate (formula-selftests gate).

## AUTONOMY

- Choose queue (GPU recommended for N=4096 cell; CPU acceptable for C3-C6 at default N).
- Estimate ETA; surface if exceeds 12h compute.
- Smoke gate: run C1 at N=512 only first; if q_EA computation crashes / returns NaN / takes >10min for one seed, halt and rebuild before scaling N.
- Decision rules (joint outcome interpretation) per methodology note section b:
  - ≥5/6 documented-column → DOCUMENTED-BUT-UNTESTED call
  - ≥4/6 novel-column AND ≥1 anomaly in C1/C2/C3 → NOVEL call
  - ≥4/6 finite-N-column → FINITE-N-ARTIFACT call
  - else MIDDLE-BAND (extend seed count + N range)

## DEPENDENCY VERIFICATION (per [[feedback-ship-before-dependency-verified]])

Verify BEFORE queue_add:
1. Bet B fixture `data/exp_wave14_betB_4stage_continual_v1/` exists and has post-Phase-C metrics
2. q_EA computation primitives exist in `hdlab/` (replica overlap, EA order parameter); if not, build them in `verification/theory.py` FIRST
3. Free-energy reconstruction via histogram-of-overlaps method exists; if not, build before C6 cell
4. N=4096 GPU memory budget is feasible on existing GPU runner (~16GB headroom needed for Hebbian W at N=4096 with 5 seeds parallel)

## VERDICT WIRING

- `verdict_msg`: report per-cell HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL
- `outcome_class`: one of {DOCUMENTED, NOVEL, FINITE-N, MIDDLE-BAND}
- `per_cell_metrics`: dict with cell_id → {observable_value, error_bar, band_call}

## ETA estimate

GPU: ~3-4h (C1+C2 N-sweep is bottleneck at N=4096; C3-C6 are quick)
Remote CPU: ~8-10h (same composition; slower N=4096)

Recommend GPU queue. Ship as single composite anchor `anchor_novel_phase_battery_v1`.
