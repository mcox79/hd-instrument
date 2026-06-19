# Strategy -> Exp Dev request — 2026-05-24 post-v183 ship queue

**From**: Strategy (cycle 205, inline via main thread per orchestrator post-compaction brief Section 2)
**To**: Exp Dev (next cycle)
**Cap_map**: v183 (commit cf69a58 pushed)
**Priority ranking source**: notes/strategy_priority_ranking_2026-05-24_post_ewc_null.md

## Ship status at hand-off

| Item | Status | Queue | Notes |
|---|---|---|---|
| MoE GPU full re-run (post-device-fix) | **SHIPPED** | overnight_queue | Entry `wave14e_moe_xtalk_v1_post_device_fix_rerun_2026-05-24`; script fix committed at 2a85bf1 (gate() proj.to(keys.device) + degenerate-projection round-robin fallback + memory hygiene del+empty_cache); smoke re-confirmed PASS ratio=1.442 at N=512 M=2000 K=4. Full = N=4096 x M={500,2000,8000,32000} x K={4,8} x 5 seeds. |
| Tropical R2 substrate-scale (N=4096 empirical margin) | **SHIPPED** | overnight_queue | Entry `wave14_tropical_R2_substrate_scale_n4096`; script `exp_wave14_tropical_kerdock_N4096_emp_margin_v1.py` already smoke-passes; production scale (N=4096 4-coset MM = 16384 codewords). |
| Mingo-Speicher 1st order re-queue with iid_gauss + kerdock cells | **SHIPPED** | remote_cpu_queue | Entry `wave14_mingo_speicher_1st_order_full_v2_rerun_2026-05-24`; full mode runs all 3 codebooks (`iid_gauss`, `srht`, `kerdock`) at N=512 ratio=8 n_seeds=20 — addresses the prior INCONCLUSIVE which used only iid_gauss. |

## DESIGN HAND-OFFS — Exp Dev pickup (autonomy on design parameters)

You decide: N, M, ratio, seeds, thresholds, fail bands, output schema, queue, ETA. Strategy gives the falsifier statements and the scope; Exp Dev designs the experiment.

### Ablation A — Per-task sub-substrate (NEW, HIGH priority)

**Scope**: structural-separation-axis falsifier for Bet B retention. Train 3 separate W matrices on Bet B's three corpora (A, B, C from `exp_wave14d_betB_kovacs_v1.py`), concatenate at retrieval (gating-by-task or simple sum then read).

**Falsifier statements (pre-reg these in your script)**:
- HARD-PASS: retention_A >= 95% with 3-corpus per-task sub-substrate concatenation -> structural separation IS the load-bearing axis for Bet B retention; this would be the substrate-level analog of the MoE result.
- HARD-FAIL: retention_A < 80% with 3-corpus per-task sub-substrate concatenation -> structural separation NOT load-bearing; the 73% replay-driven ceiling is bounded by something other than parameter-importance OR structural-separation.
- MIDDLE: 80% <= retention_A < 95%; report bands and propose follow-up.

**Comparison anchor**: baseline = same Kovacs A->B->C training pipeline with single shared W and random replay = 73% retention_A.

**Per [[feedback-rehabilitation-after-rejection]]**: this is the structural-separation-axis rescue path for EWC-null; if Ablation A passes, MoE PASS predicted (same axis); if Ablation A fails AND MoE fails, structural-separation is also empty -> only retention-via-replay-frequency or wholly novel axis remains.

### Ablation B — Replay-only sweep across fractions (NEW, HIGH priority)

**Scope**: bound the replay-only ceiling for Bet B retention.

**Falsifier statements**:
- HARD-PASS monotone: retention_A monotone-increasing in replay_frac across {0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0} with peak >= 90% -> replay-alone can close the gap; cost-vs-retention frontier is the design knob.
- HARD-FAIL plateau: retention_A plateaus < 80% across all replay_frac >= 0.25 -> ceiling at ~73-80% bounded by structural property of the substrate; only structural-separation routes (MoE, sub-substrate) can break this ceiling.
- MIDDLE: any other pattern; report bands.

**Anchor**: the 73% retention_A at replay_frac=0.10 from earlier Bet B Kovacs runs is the established midpoint of the sweep.

### SSM/S4 re-queue with corrected task

**Scope**: rebuild the task wrapper around the substrate so that the W matrix exercises the HiPPO-stable spectrum. Smoke previously failed at task-design level not substrate-level.

**Per user analysis**: substrate W as state transition matrix, key as input, value as readout, standard copy-task or selective-copying benchmark.

**Falsifier statements**:
- HARD-PASS: standard copy-task accuracy >= 95% at seq_len=128 and selective-copying accuracy >= 90% at seq_len=64 -> substrate W is functional as HiPPO-class state-transition operator at standard benchmark scales.
- HARD-FAIL: accuracy <= 50% (random chance) at any of the two benchmark cells -> substrate W is not HiPPO-class at standard scale.
- MIDDLE: partial pass on one of the two; characterize.

**Existing script to start from**: `experiments/exp_wave14e_s4_depth_smoke_v1.py` (failed at smoke-level task design per the user analysis).

### F-6 Boolean re-queue with proper schema

**Scope**: the v182 F-6 Boolean noise-stability KILL was at the closed-form-margin theory level. User flagged that re-queue needs "proper schema" — Strategy reading: the prior schema may have applied Walsh-Hadamard analysis to the WRONG substrate state (post-Hopfield-cleanup mangles bent assumption; pre-cleanup applies bent assumption directly but downstream Cap 3 readout always applies cleanup).

**Suggested schema correction**:
- Add a third measurement schema: substrate-physics-layer (= the W matrix structure ITSELF, not the Boolean function over a single codeword), inspired by the v182 closure framing "future rehab REFRAME at production-N substrate-physics layer".
- OR: clarify pre-cleanup vs post-cleanup test cells to make them BOTH falsifiers (currently script gives a partial-pass status to "pre-cleanup PASS only" which the v182 closure ruled was not enough).

**Falsifier statements (substrate-physics framing)**:
- HARD-PASS: at production N=4096 4-coset MM Kerdock + the W matrix itself analyzed as a function: bent-equivalent stability holds at rho=0.9 within 2% -> substrate-physics-layer KKL framing works.
- HARD-FAIL: at production N=4096: KKL slack > 30% -> substrate is not bent-equivalent at production scale either.

**Existing script**: `experiments/exp_wave14_boolean_noise_stab_kerdock_kkl_v1.py`.

### Sellke re-queue at narrower eps OR alternate baseline construction

**Scope**: the v183 SELLKE_INCONCLUSIVE result came from baseline modes=8 at eps=0 (RS phase has modes=1 by definition). The baseline construction in the current script is producing a multimodal P(q) at eps=0, which the Sellke probe interprets as "not in RS phase, can't test for RS -> RSB transition".

**Suggested correction**:
- Option 1: tighten baseline. Use a smaller N or longer thermalization to ensure unimodal P(q) at eps=0 (the predicted RS state).
- Option 2: alternate baseline. Use a known-RS construction (e.g., explicit ferromagnetic-only J at temperature T < T_c with hot-restart annealing) and probe with the Sellke epsilon-drift only.
- Option 3: reframe. If the substrate's default state has 8 modes at eps=0, that itself is a finding — substrate is RSB-default not RS-default; Sellke probe becomes "does epsilon-ferromagnetic-drift CONSOLIDATE the modes" not "does epsilon-drift break RS".

**Existing script**: `experiments/exp_wave14_sellke_marginal_stability_v1.py`.

## Discipline pointers

- Per [[feedback-no-experiment-design-in-prompts]] this hand-off provides scope + falsifier-statement-class + pointers; YOU decide N/M/eps/seeds/thresholds/queue.
- Per [[feedback-no-papers-product-only]] all framings are substrate-product.
- Per [[feedback-no-smoke]] both HARD-PASS and HARD-FAIL bands MUST be falsifiable BEFORE running.
- Per [[feedback-rehabilitation-after-rejection]] Ablation A + Ablation B are the rehab sketches for the EWC-null closure; HS-v2 + Cap 2 Rescue 1 are CLOSED-FAILED so further rehab on those paths is OFF-LIMITS.
- Per [[feedback-pipeline-pacing]] when you ship, honor queue-depth >= 1 invariant; current state at hand-off: overnight_queue=3 (cap8_iterates running + MoE GPU full pending + TropR2 substrate-scale pending); remote_cpu_queue=1 (MS re-run pending); local_cpu_queue=0.

## Status log fired

`status_log` cap_map_commit + queue_refill entries written at v183 close. The 5 hand-offs above are the NEXT exp_dev cycle's work — not blocking; not in-flight; not status_log'd until exp_dev picks up.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
