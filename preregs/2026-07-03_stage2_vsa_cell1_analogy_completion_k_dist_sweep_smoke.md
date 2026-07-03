# Stage 2 VSA Cell 1 — K_DIST sweep addendum (SMOKE Pre-Registration)

Date: 2026-07-03
Type: Cell pre-reg (SMOKE) — Skunkworks-approved sweep addendum to Cell 1.
Anchor: `stage2_vsa_cell1_analogy_completion_k_dist_sweep_smoke`
Author: hdi_exp_dev.
Parent Cell 1 prereg: `preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_smoke.md` (commit ad43cd195).
Cell file: `experiments/exp_substrate_vsa_cell1_analogy_completion_k_dist_sweep_smoke_2026-07-03.py`.

## Concept-query-before-dispatch (USER-locked 2026-07-02)

`bash tools/substrate_query.sh "K distractors sweep analogy completion cleanup memory ablation"` returned top-5 at cosine 0.32-0.37: `distraction`, `completion`, `Pre-registration cleanup`, `ablation`, `to completion`. All wordnet lexical hits + one unrelated notes file. **No prior K-distractor-sweep analogy cell** in substrate. Genuinely novel operational drill on Cell 1 HP3 caveat; NOT a rediscovery.

## 1. Purpose (sweep addendum, not new anchor)

Cell 1 smoke (commit ad43cd195) landed **MIDDLE_BAND** verdict:
- CLEANUP = 0.861 +/- 0.009  MEASURED@data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json:gates.cleanup
- NO_CLEANUP = 0.855 +/- 0.012  MEASURED@same:gates.no_cleanup
- COSINE_BASE = 0.007  MEASURED@same:gates.cosine_base
- HP1 PASS (0.861 >= 0.80); HP2 PASS (gap=+0.854 vs cosine); HP3 FAIL (gap=+0.007 < 0.05)

Cell-author note (MEASURED_BOUND, not defect): "at K_DISTRACTORS=3, bundle noise on r_hat is small enough that atomic-A argmax already denoises. Would presumably fire at larger K."

**Skunkworks strategic direction:** sweep K_DIST in {3, 5, 10, 20, 50} to characterize where cleanup earns its keep.
- If sweep fires HP3 at K >= 10 (gap >= 0.05): elevates atom (a) MEASURED_BOUND -> chain-grade upgrade candidate; supports 3rd witness -> CG_META META promotion path.
- If sweep fails HP3 at every K: refines atom (a) as "cleanup does not earn its keep on this canonical FHRR regime; may need different codebook or task structure" — strong refutation.

## 2. Sweep design (Option A: fork; scope-clarity)

- K_DIST_VALUES = [3, 5, 10, 20, 50] (5 sweep points, K=3 = Cell 1 regression sanity)
- ARM_MODES = [ARM_HRR_BIND_UNBIND_CLEANUP, ARM_HRR_BIND_UNBIND_NO_CLEANUP] (2 arms, LOAD_BEARING + ablation)
- Weak baselines (cosine, random) SKIPPED — Cell 1 already characterized them at chance (~0.007-0.012) and they're expected constant across K
- SEEDS = [11, 17, 23] (same as Cell 1 for bit-identical K=3 reproduction)
- **EXPECTED_N_UNITS = 3 seeds x 5 K x 2 arms = 30**

Same primitives (FHRR bind + unbind + cleanup-family cleanup), same codebook construction, same query generator — ONLY K_DISTRACTORS varies.

## 3. Config (held constant from Cell 1)

- `n_dim = 2048` (FHRR complex phasors; unit-magnitude)
- `N_CONCEPTS = 100`
- `N_RELATIONS = 10`
- `N_QUERIES = 500` per (seed, K) tuple
- `SEEDS = [11, 17, 23]`
- Compute: numpy CPU (per-query FFT-free FHRR is fast; smoke wall estimated < 3 min total)

## 4. HP_SCOPE (LOAD_BEARING gates)

| Gate | Applies to | Condition |
|---|---|---|
| Per-K HP3 | (CLEANUP_K, NO_CLEANUP_K) at each K | gap >= 0.05 |
| K_HP3_FIRES | sweep-wide | smallest K where per-K HP3 is True |
| Regression sanity | K=3 mean CLEANUP + NO_CLEANUP | bit-identical (delta <= 1e-9) to Cell 1 MEASURED@data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json |

**Per-arm HP scope (§5b canonical):**
- Per-K HP3 applies to per-K arm pair only.
- No HP1/HP2 in sweep addendum (these were established at K=3 in Cell 1).

## 5. HARD_FAIL bands

- **HF_regression:** K=3 CLEANUP or NO_CLEANUP mean recall@1 differs from Cell 1 by more than 1e-9. Indicates code drift; sweep unreliable. Ships as HARD_FAIL_REGRESSION_MISMATCH before verdict-tier decision.
- **HF_arm_error:** any arm returns non-OK arm_status. Ships as HARD_FAIL_ARM_ERROR.
- **HF_cardinality:** len(all_results) != 3 OR any seed with != 10 arms. Ships as HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.

## 6. MIDDLE_BAND

- Sweep runs cleanly but no K in {3, 5, 10, 20, 50} fires HP3 (max gap < 0.05). Cleanup does not earn keep at any tested distractor count on this canonical FHRR regime. Refines atom (a) MB with 5-point envelope; potentially motivates alternative regime probes (different codebook, longer chains, different cleanup mechanism).

## 7. HARD_PASS

- Some K in sweep fires HP3 (gap >= 0.05) AND K=3 regression clean. Characterizes cleanup-earns-keep envelope. Enables upgrade path for atom (a) MEASURED_BOUND -> CG when composed with Cell 1 K=3 boundary observation.

## 8. Discriminator-must-survive-scale + AG (baseline in band)

**Predicted per-K CLEANUP mean:** monotone decrease from Cell 1's 0.861 at K=3 toward chance as K grows. THEORETICAL@Plate1995: FHRR bundle SNR ~= 1/sqrt(K+1) per role slot; at K=50 the r_hat unbind is far noisier than at K=3. Cleanup should retain higher recall than NO_CLEANUP as K rises because argmax over R denoises before the second unbind.

**Predicted per-K NO_CLEANUP mean:** monotone decrease steeper than CLEANUP as K grows. At K=3 both nearly saturate (Cell 1 result: 0.861 vs 0.855, gap +0.007). At K=10, gap predicted 0.05-0.15 (HP3 fires). At K=50, gap could either grow (cleanup denoises effectively) or shrink again if r_hat is TOO noisy for even the cleaner argmax to recover.

**Baseline in band (META_RULE_AG):** NO_CLEANUP is the ablation control and must be in (0.05, 0.95) at each K to be a discriminating band. At K=3: NO_CLEANUP=0.855 (in-band but saturated-adjacent). At K>=10: NO_CLEANUP predicted to drop below 0.80, well in-band.

- `baseline_in_band` predicted True for K in {5, 10, 20, 50}; at K=3 it's saturated-adjacent (Cell 1 already showed HP3 fail at K=3 as MB — that's the load-bearing observation motivating the sweep).

**Discriminator survives scale:** smoke IS the intended regime (analytical justification per Cell 1 parent + Plate 1995 capacity). No FULL variant contemplated at this stage — the sweep IS the characterization.

## 9. CRLB / capacity feasibility

- Binomial CRLB per (seed, K, arm): sigma_p = sqrt(p*(1-p)/500). At p=0.5, sigma = 0.0224. HP3 threshold 0.05 is ~2.2 sigma per seed, ~1.3 sigma over 3-seed mean; well-resolved at expected discriminating K values.
- FHRR capacity (Plate 1995): at n=2048, N_C=100, M_roles=10, bundle capacity per role slot ~= sqrt(n/(K+1)). At K=50: SNR ~= sqrt(2048/51) = 6.3 (still comfortable). At K=3: SNR ~= sqrt(512) = 22.6 (well above ceiling; explains K=3 saturation both arms).
- `crlb_floor_computed: 0.0224` (binomial CRLB per seed at p=0.5)
- `crlb_formula_reference: "sigma_p = sqrt(p*(1-p)/N_QUERIES); Plate 1995 HRR capacity per-role SNR"`
- `discriminator_reachability: True` (HP3=0.05 gap threshold >> 2 * per-seed CRLB)

## 10. Selftests (6 total; >= 5 required)

1. **Bind-unbind round-trip** at n_dim=2048: cosine > 0.999.
2. **Analogy generator valid at K in {3, 10, 50}** — no leakage, correct shape, distractor concepts != target on each side.
3. **Cleanup memory correct top-K** — cleaned vector matches injected codebook entry at cosine > 0.999.
4. **Scale sentinel at n_dim=8192** — bind/unbind round-trip finite + cosine > 0.999.
5. **Arms-must-differ at K=10** (META_RULE_AF) — CLEANUP vs NO_CLEANUP predictions differ (hash-check).
6. **Regression sanity at K=3** — 3 seeds x 500 queries reproduce Cell 1 CLEANUP=0.8613... and NO_CLEANUP=0.8546... within 1e-9. THIS IS THE LOAD-BEARING SELFTEST for sweep validity.

## 11. Cell-template mandates checklist

- `arms_differ_verified: True` (hash-test at K=10)
- `final_metrics_atomicity: "tmp_replace"` (single-shot; .tmp + os.replace)
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- `crlb_floor_computed: 0.0224` (binomial per seed)
- `discriminator_reachability: True`
- `baseline_in_band: True` for K >= 5; K=3 saturated-adjacent (that IS the load-bearing observation from Cell 1)
- `cell_chunked: False` (3 seeds run within one process; wall < 5min)
- `start_marker_written: True`
- `crash_diagnostic_present: True` (Exception -> CELL_CRASHED metrics)
- `heartbeat_present: True` (per-(seed, K, arm) progress lines with flush=True)
- `progress_logging: "print_flush_true"`
- `cardinality_ok: True` (len(per_seed)==3 AND each seed has 10 arms)
- `defensive_error_checking: "passed_all_4_patterns"`
- `calibration_check: "default_ok_for_this_regime"` (evidence: Cell 1 K=3 landed clean; sweep uses same primitives)

## 12. Compute architecture

- **Class:** (b) sequential-CPU with justification.
- **Justification:** total smoke ~= 5 K-values x 3 seeds x 2 arms x 500 queries ~= 30 (arm,seed) tuples at ~0.1-0.3s each = ~30-90s wall total. Well below 10s per-phase-point threshold. Sub-minute wall; CPU-appropriate. If we scale to full Google-analogy corpus (n=15k concepts) or n_dim=8192, re-classify to (a) batched-GPU.
- **Storage strategy:** `bundled` per Cell 1 (single-hop analogy; no downstream chaining; bundle IS the analogy-side representation as canonical Plate 1995 mechanism). Sharded-vs-bundled META rule does not fire — bundle here is the mechanism-under-test, not a compositional-chain storage layer.

## 13. Test-design gates §15 (canonical)

- **A) effective_vs_nominal parameter audit:** K_DISTRACTORS is the swept parameter; each primitive (bind, unbind, bundle, cleanup) experiences K distractors directly (no partition-routing intermediate). `sweep_alignment_verdict: ALIGNED`.
- **B) discriminating_fraction:** 5 sweep points {3, 5, 10, 20, 50}. Predicted CLEANUP-NO_CLEANUP gaps: K=3: ~0.01 (saturated, MB), K=5: ~0.02-0.05 (borderline), K=10: ~0.05-0.10 (HP3 fires), K=20: ~0.10-0.20 (HP3 fires), K=50: ~0.05-0.25 (HP3 likely fires). 3/5 predicted in band [0.05, 0.30]. `discriminating_fraction >= 0.60` (well above 0.30 threshold).
- **C) signal_shape_compatibility_audit:** bind output (n_dim,) complex -> bundle (n_dim,) complex -> unbind (n_dim,) complex -> cleanup (n_dim,) complex -> argmax int. All SHAPE_MATCH. No adapter required.
- **D) positive_control_arms:** ARM_HRR_BIND_UNBIND_CLEANUP at K=3 IS the positive control at test regime (must reproduce Cell 1 MEASURED atom bit-identical). `cited_prior_metric: 0.8613333` MEASURED@Cell1; `tolerance: 1e-9`; `regime: {N: 2048, N_C: 100, N_R: 10, K_DIST: 3}`. Regime-extension audit: identical regime, only K varies -> SHAPE_MATCH.
- **E) functional_requirements_present:** Same as Cell 1 (bind role+concept, recover role via unbind, cleanup r_hat, retrieve target via second unbind + argmax). All primitives in hdlab.

## 14. Framing discipline (USER-locked; Director has 5 Fix#28 hits today)

- **SUBSTRATE KNOWS ALMOST NOTHING** — this is a REGIME CHARACTERIZATION sweep on SUPERVISED SYNTHETIC analogy; no general-knowledge claim, no language claim.
- **Skunkworks caveat on Cell 1 K=3:** "72-sigma separation is REAL but ENTIRELY EXPECTED per Plate 1995 (theoretical ~0.95 at these params; observed 0.86 sits below ceiling)" — Plate 1995 canonical mechanism, NOT novel finding.
- Cell 1 K=3 was mechanism reproduction on regime WELL WITHIN capacity; NOT a discriminating capacity-edge probe.
- **If sweep fires HP3 at K>=10 (gap >= 0.05):** atom (a) MB -> CG upgrade + supports 3rd witness -> CG_META META promotion path. **This is what Skunkworks predicted.**
- **If sweep fails HP3 at any K:** refines atom (a) as "cleanup doesn't earn keep on THIS canonical FHRR regime; may need different codebook or task structure." Strong refutation with envelope.
- **No "first" / "physics law" language.** VSA analogy is canonical Plate-1995-era mechanism.
- **No overclaiming.** The sweep characterizes where cleanup earns keep; it does NOT establish substrate-general capability.
- **Self-correction pattern MM_STANDARD 3-witness CG_META discipline:** if verdict overclaims, self-correct in report.

## 15. Dispatch plan

- **Smoke gate:** local_cpu (SMOKE-only-local USER-LOCKED 2026-07-01). Estimated wall < 3min including selftest regression check.
- **After smoke lands:** REPORT + HARD HOLD before any FULL variant. Director decides next.
- **If HP3 fires at some K:** atom (a) upgrade path opens; may motivate n_dim sweep or N_C sweep FULL variant separately.
- **If HP3 never fires:** memorialize refinement of atom (a); investigate alternative mechanism variants (codebook structure, different cleanup family).

## References

- Cell 1 (parent): `preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_smoke.md`; commit ad43cd195.
- Cell 1 MEASURED atom: `MATH_VSA_CELL1_ANALOGY_COMPLETION_CG_MEASURED_BOUND` (cert_ledger 2026-07-03).
- Roadmap parent: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md`.
- Plate 1995 HRR capacity theory.
- USER-LOCKED framing: `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`.
