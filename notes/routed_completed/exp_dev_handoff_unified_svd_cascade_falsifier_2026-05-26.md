# exp_dev hand-off: UNIFIED-framework falsifier (SVD-cascade equal-spacing)

Filed: 2026-05-26 by Research sub-agent (Opus synthesis).
Trigger: `notes/research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md` cross-prediction (2) — load-bearing falsifier.
Cap_map context: this test resolves UNIFIED (P=0.46) vs INDEPENDENT (P=0.32) for the three substrate theoretical-home findings (v206 saddle-cascade + v211 1-RSB hysteresis + v212 MoE SHIFT).

---

## TASK

Test whether the top-K detached singular values of trained-W (excess above Marchenko-Pastur bulk edge) are equally spaced across substrate experiments. This is the cheapest decisive test for the UNIFIED framework hypothesis per parent note section (b).

## WHY

The parent drill identifies Bachtis-Biroli-Decelle-Seoane 2024 NeurIPS "Cascade of phase transitions in EBM training" as the candidate master framework: training proceeds via SVD-cascade of phase transitions, each resolving a principal mode of W. The three substrate findings would then be projections of this single mechanism:
- v206 4-plateau saddle-cascade = sequence of 4 mode-resolution events.
- v211 1-RSB hysteresis = single-mode-detachment basin signature.
- v212 MoE SHIFT lift = per-expert mode-resolution preserved by full-N experts.

If detached singular values of trained W are equally spaced (matching the equal-plateau-spacing observation), UNIFIED gains strong empirical support (P rises to 0.55-0.60). If not, three findings are independent (P drops to 0.25-0.30 for UNIFIED; INDEPENDENT becomes leading).

## CONTRACT

1. **Add helper** `compute_svd_cascade_equal_spacing(W, M_stored, N)` returning dict with:
   - `sigmas` (full singular spectrum, descending)
   - `bulk_edge = (1 + sqrt(M_stored / N))**2` (Marchenko-Pastur top)
   - `K_detached` (count of sigmas above bulk_edge * 1.05)
   - `excess_sigmas` (top-K detached - bulk_edge)
   - `gaps` (negative diff of excess_sigmas; positive for descending)
   - `spacing_error` (std(gaps) / mean(gaps); CoV)
   - `hard_pass` (spacing_error < 0.05 AND K_detached >= 4)
   - `hard_fail` (spacing_error > 0.15 OR K_detached < 2)
   - `band` ('HARD_PASS' | 'HARD_FAIL' | 'MIDDLE' | 'INSTRUMENTATION_FAIL')

2. **Run** the helper on trained-W matrices from existing data dirs:
   - `data/exp_wave14_betB_saddle_cascade_reanalysis_v1/` (v206)
   - `data/exp_wave14_1rsb_hysteresis_v3/` or `_v4_multi_N/` (v211)
   - `data/exp_wave14_moe_shift_K_scaling_v2/` (v212; multiple K experts -> multiple W matrices)

3. **Check first** whether W matrices were saved on those runs. If NOT (likely — substrate scripts typically don't auto-save W), re-ship a minimal re-run at N=1024 (CPU, ~1 hour) with `--save_W` flag added per script. Use the SAME pre-reg bands as v206/v211/v212 originals (no change in experimental design — only add W persistence).

4. **Aggregate verdict** across the runs into a single dict and report per standard verdict envelope:
   - `unified_falsifier_band`: PASS / FAIL / MIDDLE / INSTRUMENTATION_FAIL based on >= 3 of 5 W instances meeting hard_pass / hard_fail.
   - Per-instance `K_detached`, `spacing_error`, `excess_sigmas` for traceability.

5. **No new experimental design**. This is a post-hoc analysis layer. The bands are pre-registered (parent note section b); the helper logic is closed-form.

## Pre-registered bands (HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL)

- **HARD-PASS (UNIFIED confirmed):** spacing_error < 0.05 on >= 3 of 5 trained-W instances. AND K_detached >= 4 on all of them. AND mean spacing_error across all instances < 0.07.
- **HARD-FAIL (UNIFIED rejected -> INDEPENDENT verdict):** spacing_error > 0.15 on >= 3 of 5 instances OR K_detached < 4 on >= 3 of 5 instances (would prove SVD-cascade framework does not produce visible 4-detached-mode structure in substrate W).
- **MIDDLE BAND (INCONCLUSIVE; needs higher-N reship):** spacing_error in [0.05, 0.15] across most instances OR K_detached oscillates between 3 and 4 across runs. Recommend N=4096 re-run for any instance in MIDDLE BAND.
- **INSTRUMENTATION-FAIL:** SVD doesn't converge (very unlikely for N <= 4096) OR W matrices weren't saved and re-run requires script modification (escalate to Strategy for re-ship approval).

## AUTONOMY

- Choose whether to attempt post-hoc on existing data dirs first (cheapest path, ~minutes) or escalate to re-run-with-W-save immediately.
- Choose smoke vs full mode for any re-ship (default: smoke first to verify W-save logic, then full).
- Choose queue (laptop_cpu for analysis-only; remote_cpu_queue for any re-ship per [[feedback-laptop-cpu-quick-probes]] threshold).
- Self-test the helper at module load before running on real data per [[feedback-strategy-spec-formula-selftests]]:
  - Self-test: feed a synthetic W = U @ diag([bulk_edge + 4*delta, bulk_edge + 3*delta, bulk_edge + 2*delta, bulk_edge + delta, bulk_eigvals_below_edge...]) @ V.T for arbitrary delta=0.1; verify K_detached=4, spacing_error~0 (within float epsilon), band='HARD_PASS'. If self-test fails, ABORT before touching real data.

## Cross-prediction context (do NOT test these in v1 of this handoff — defer)

- Cross-prediction (1): free-additive top-edge ratio chains to 1-RSB hysteresis gap magnitude. DEFER to follow-up handoff after (2) closes.
- Cross-prediction (3): MoE alpha_c-emerge = 1-RSB alpha_c-emerge. DEFER. Requires overlapping M-grids in v211 and v212 which may not exist.

## Status / verdict reporting

Per [[feedback-for-you-tab-primary-channel]]: write status_log entry on completion with `plain_language` field explaining whether substrate's three theoretical-home findings turned out to share one underlying mechanism (visible as equal-spaced singular values) or not. `importance=HIGH`.

Per [[feedback-verdict-msg-honest-reread]]: when reporting, compare the per-instance `spacing_error` and `K_detached` numbers against the pre-reg bands explicitly (don't just report a verdict label).

---

**End handoff.**

Strategic posture: this is a CHEAP DECISIVE test. Post-hoc on existing data if W was saved; minimal re-ship (~1 hour CPU) if not. Either way, settles UNIFIED vs INDEPENDENT for the three theoretical-home findings.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
