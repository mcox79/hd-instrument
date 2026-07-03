# Stage 2 VSA Cell 2 — Compositional Generalization (SMOKE Pre-Registration)

Date: 2026-07-03
Type: Cell pre-reg (SMOKE).
Anchor: `stage2_vsa_cell2_compositional_generalization_smoke`
Author: hdi_exp_dev.
Parent prereg: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (commit 891fde49a, §5 Cell 2).
Cell file: `experiments/exp_substrate_vsa_cell2_compositional_generalization_smoke_2026-07-03.py`.

## Concept-query-before-dispatch (USER-locked 2026-07-02)

`bash tools/substrate_query.sh "compositional generalization novel role filler VSA HRR held out"` returned top-5 at cosine 0.42-0.49 (all borderline; highest was "Compositional generalization" cosine=0.4902):
1. `notes/wave14e_hierarchical_composition_research.md` (hierarchical composition research; not a VSA cell)
2. `notes/research_BetX_skill_composition_2026-05-21.md` (BetX skill composition; different task)
3. `notes/research_drill_iterated_retrieval_depth_scaling_hierarchical_2x_2026-06-04.md` (iterated retrieval depth; adjacent)
4. `notes/research_drill_cross_domain_new_mechanism_5x_2026-06-10.md` (SCAN mentioned; cross-domain)
5. `notes/research_BetX_skill_composition_2026-05-21.md` (context)

Also referenced: `notes/research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md` (parent prereg §5 cites; VSA composition benchmark methodology drill).

**Novelty assessment:** genuine new authoring under Stage 2 benchmark-reframe roadmap. No prior VSA cell has tested compositional generalization via held-out role-filler combinations at n_dim=2048 with K_DIST=10 discriminator. Cell 1 (analogy completion) landed MB with HP3 failed at K_DIST=3; Cell 2 forces the cleanup discriminator by increasing K_DIST to 10 per Skunkworks strategic guidance.

## 1. Task class + mechanism (§2B of parent prereg)

**Compositional generalization:** substrate must handle novel (role, filler) combinations never seen at training. Frame:slot binding composition (Smolensky TPR / Plate HRR).

- 5 roles × 100 fillers = 500 possible (role, filler) combinations.
- Training split: 300 SEEN pairs (60% coverage; used for baseline stored-bundle arm ONLY).
- Held-out split: 200 NOVEL pairs (never bundled during training; used for all test queries).
- Test: for each held-out (role_q, filler_true), mechanism must retrieve filler_true from role_q query.
- **VSA-native operation:** at test time, bind(role_q, filler_true) is composed with K_DIST=10 distractor pairs into a test bundle; unbind by role_q recovers noisy filler_hat; cleanup over filler codebook recovers filler_true.

## 2. Substrate mechanisms tested (arms; 5 arms × 3 seeds = 15 units)

| Arm | Mechanism | Test-time composition? | Load-bearing? |
|---|---|---|---|
| `ARM_HRR_BIND_UNBIND_CLEANUP` | HRR bundle+unbind test-time; cleanup argmax over F codebook | YES | LOAD-BEARING |
| `ARM_HRR_BIND_UNBIND_NO_CLEANUP` | HRR bundle at test but SKIP unbind: cleanup on raw B_q against F | YES (bundle only) | Ablation |
| `ARM_HRR_STORED_BUNDLE_LOOKUP` | Bundle all 300 SEEN pairs into M_stored once; unbind(M_stored, role_q) at test | NO (memory lookup only) | Fair baseline |
| `ARM_COSINE_ARGMAX_BASELINE` | argmax_i cos(role_q, F[i]) — direct role-vs-filler | n/a | Weak baseline |
| `ARM_RANDOM_BASELINE` | random filler index | n/a | Chance floor |

**Discriminator logic:**
- HP1 (does compositional generalization work at all): CLEANUP mean r@1 ≥ 0.60 on HELD-OUT novel pairs.
- HP2 (does unbind earn its keep at K_DIST=10): CLEANUP − NO_CLEANUP ≥ 0.10. K_DIST=10 chosen precisely to force this separation; at K_DIST=3 (Cell 1's HP3 regime), gap was +0.007.
- HP3 (is generalization non-trivial): CLEANUP − STORED_BUNDLE ≥ 0.05. Verifies that test-time bind+unbind composition beats stored memory. filler_true is NEVER paired with role_q in M_stored (held-out by construction), so STORED_BUNDLE ≈ 0.0 expected. HP3 clearing is not trivially guaranteed — if CLEANUP fails, HP3 could clear vacuously with both arms near 0.
- HP4 (mechanism vs cosine): CLEANUP − COSINE ≥ 0.30. Cosine is expected at chance (~0.01); this is a sanity gate.

**Arms-must-differ (META_RULE_AF):** all 5 arms produce distinct outputs by construction (different code paths). Verified at smoke gate via `_arms_must_differ` hash-test.

**No DG-style 2%-sparsity 40x expansion** anywhere (Skunkworks architectural constraint b, 2026-07-03). FHRR unit-magnitude complex phasors at n_dim=2048 dense; no sparsification.

## 3. Config

- `n_dim = 2048` (FHRR unit-magnitude complex phasors per Plate 2003; matches Cell 1)
- `N_ROLES = 5`
- `N_FILLERS = 100`
- `N_SEEN = 300` (of 500 total combinations; 60% seen)
- `N_HELDOUT = 200` (never bundled during training)
- `K_DISTRACTORS = 10` (Skunkworks-flagged threshold; forces cleanup discriminator)
- `SEEDS = [11, 17, 23]`
- Codebook: unit-magnitude complex phasors (uniform random phase).
- Compute: numpy CPU (smoke wall estimated < 3min; below 10s per-phase-point threshold).

## 4. HP_SCOPE (LOAD_BEARING gates)

| Gate | Applies to | Condition |
|---|---|---|
| HP1 | ARM_HRR_BIND_UNBIND_CLEANUP | mean r@1 across seeds ≥ 0.60 |
| HP2 | pair (CLEANUP, NO_CLEANUP) | CLEANUP − NO_CLEANUP ≥ 0.10 |
| HP3 | pair (CLEANUP, STORED_BUNDLE_LOOKUP) | CLEANUP − STORED_BUNDLE ≥ 0.05 |
| HP4 | pair (CLEANUP, COSINE_ARGMAX_BASELINE) | CLEANUP − COSINE ≥ 0.30 |

**Per-arm HP scope (§5b canonical):**
- HP1: `ARM_HRR_BIND_UNBIND_CLEANUP`
- HP2: pair (CLEANUP, NO_CLEANUP)
- HP3: pair (CLEANUP, STORED_BUNDLE_LOOKUP)
- HP4: pair (CLEANUP, COSINE_ARGMAX_BASELINE)
- ARM_RANDOM_BASELINE: no HP inheritance (chance floor only)

## 5. HARD_FAIL bands

- HF: CLEANUP r@1 < 0.30 (mechanism doesn't generalize compositionally on VSA-native task class) — strong refutation of task-class-fit hypothesis.
- HF_stored_beats_mechanism: STORED_BUNDLE > CLEANUP + 0.05 (stored memory beats compositional; would refute compositional-generalization claim).
- HF_cardinality: `len(per_seed) != 3` OR `len(arms_per_seed) != 5`.

## 6. MIDDLE_BAND

- 0.30 ≤ CLEANUP < 0.60: partial generalization; may indicate K_DIST=10 exceeds SNR margin at n_dim=2048 (would want scale sweep).
- HP1 clears but HP2 fails: cleanup ablation-safe at K_DIST=10 (would be surprising given Cell 1's HP3 fail at K=3; would indicate cell design issue).
- HP1 clears but HP3 fails: compositional gain small (STORED_BUNDLE unexpectedly retrieves via seen-role-paired distractors + noise leakage).

## 7. Discriminator-must-survive-scale + AG (baseline in band)

**Predicted per arm at n_dim=2048, K_DIST=10 (HYPOTHESIZED@this-prereg; no prior CG-level measurement at this exact regime):**
- CLEANUP: 0.60-0.85. FHRR SNR at K_DIST=10 superposition ≈ sqrt(n_dim/(K_DIST+1)) = sqrt(2048/11) ≈ 13.6; well above 1.0 cleanup threshold for M=100 codebook.
- NO_CLEANUP (raw B_q vs F codebook, no unbind): near chance ~0.01. Bundle of 11 bind(r,f) products has expected cos with any single f_j ≈ O(1/sqrt(n_dim)); argmax over 100 near-uniform sims.
- STORED_BUNDLE: near 0.00. filler_true is NOT paired with role_q in M_stored by held-out construction; unbind(M_stored, role_q) recovers superposition of ~60 seen-with-role_q fillers, none of which is filler_true. Argmax picks one of the ~60 seen; miss by construction.
- COSINE: ~0.01 (chance). random role vs random filler.
- RANDOM: ~0.01 (chance).

**Baseline in band (META_RULE_AG):**
- ARM_HRR_BIND_UNBIND_NO_CLEANUP expected ~0.01 (chance-floor by construction, exempted).
- ARM_HRR_STORED_BUNDLE_LOOKUP expected ~0.00 (held-out-construction-floor, exempted).
- ARM_COSINE_ARGMAX_BASELINE expected ~0.01 (chance, exempted).
- ARM_RANDOM_BASELINE expected ~0.01 (chance floor, exempted).
- The IN-BAND baseline is the LOAD-BEARING CLEANUP arm itself (expected 0.60-0.85; well within [0.05, 0.95]).
- `baseline_exempted_arms: [ARM_HRR_BIND_UNBIND_NO_CLEANUP, ARM_HRR_STORED_BUNDLE_LOOKUP, ARM_COSINE_ARGMAX_BASELINE, ARM_RANDOM_BASELINE]` (all chance-floor / construction-floor).

**Discriminator survives scale:** smoke IS the intended regime (n_dim=2048, K_DIST=10, 200 held-out queries, 3 seeds). Scale sentinel at n_dim=8192 in selftest verifies FFT path scales cleanly. If HP passes at smoke, FULL variant would sweep n_dim ∈ {1024, 2048, 4096, 8192} and K_DIST ∈ {5, 10, 20, 50} — separate pre-reg.

## 8. CRLB / capacity feasibility

**Recall@1 CRLB:** binomial proportion over N_HELDOUT=200 per seed; sigma_min = sqrt(p*(1-p)/200). At p=0.7: sigma_min = 0.0324. HP2 gap ≥ 0.10 requires margin ~3*sigma per seed; well-resolved. HP3 gap ≥ 0.05 requires margin ~1.5*sigma; adequate given expected STORED_BUNDLE ≈ 0.00.

**FHRR capacity (Plate 1995 / Frady-Sommer 2020):** for n_dim=2048, superposition of K_DIST+1=11 bind products, single-slot cleanup over M=100 codebook; theoretical clean-up recall @ SNR=13.6 ≈ 0.90+. HP1 = 0.60 is below theoretical ceiling; strict enough to fail if regime is off.

- `crlb_floor_computed: 0.0324` (binomial CRLB at p=0.7, N=200 per seed)
- `crlb_formula_reference: "sigma_p = sqrt(p*(1-p)/N_HELDOUT); FHRR SNR = sqrt(n_dim/(K+1)) per Plate 1995"`
- `discriminator_reachability: True` (HP1=0.60 << 0.90 theoretical ceiling; HP2=0.10 >> 3*sigma; HP3=0.05 >> 1.5*sigma)

## 9. Selftests (≥ 5 required)

1. **Bind-unbind round-trip** at n_dim=2048 FHRR: `unbind(bind(a, b), b) ~= a` at cosine > 0.999 (exact for FHRR up to float).
2. **Data-split validity** — 300 seen + 200 held-out; no overlap; all pairs valid; each held-out pair verified not in seen set.
3. **Cleanup argmax correctness** — clean codebook entry F[i] retrieves index i via cosine argmax.
4. **Scale sentinel at n_dim=8192** — bind/unbind round-trip finite + cosine > 0.999 at increased scale (verifies FFT path scales cleanly).
5. **Deterministic seed invariance** — repeat with same seed reproduces recall@1 to 1e-6 tolerance.
6. **Arms-must-differ (META_RULE_AF)** — all 5 arms produce bit-different predictions on a shared batch.

## 10. Cell-template mandates checklist

- `arms_differ_verified: True` (SHA256 hash-test on per-arm outputs)
- `final_metrics_atomicity: "tmp_replace"` (single-shot; write via .tmp + os.replace)
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- `crlb_floor_computed: 0.0324` (binomial per seed at p=0.7, N=200)
- `discriminator_reachability: True`
- `baseline_in_band: True` for CLEANUP load-bearing arm (0.05 < 0.60-0.85 < 0.95); chance-floor arms exempted
- `cell_chunked: False` (single-file cell; 3 seeds run within one process; smoke wall << 5min)
- `start_marker_written: True`
- `crash_diagnostic_present: True` (Exception handler writes CELL_CRASHED metrics)
- `heartbeat_present: True` (per-seed progress lines flush=True)
- `progress_logging: "print_flush_true"` (all progress lines flush=True)
- `cardinality_ok: True` (len(per_seed)==3 AND each seed has 5 arms; EXPECTED_N_UNITS=15)
- `defensive_error_checking: "passed_all_4_patterns"`
- `calibration_check: "default_ok_for_this_regime"` (evidence: FHRR SNR ≈ 13.6 at K_DIST=10, n_dim=2048; well within Plate 1995 capacity theorem)

## 11. Compute architecture

- **Class:** (b) sequential-CPU with justification.
- **Justification:** smoke wall estimated 60-180s across 3 seeds × 5 arms × 200 queries × per-query FHRR (elementwise complex mul + argmax over 100). Per-seed wall < 60s; below GPU-batching mandate threshold.
- **Storage strategy:** `mixed`. Test-time CLEANUP + NO_CLEANUP arms are `no_composition` (each query bundles fresh at test; no persistent storage). STORED_BUNDLE arm is `bundled` (intentional; positive-control comparison to test that stored bundle CANNOT retrieve held-out combinations — sharded-vs-bundled META rule allows bundled here as (b) discriminator arm per §CG 2026-07-02).

## 12. Test-design gates §15 (canonical)

- **A) effective_vs_nominal parameter audit:** No swept parameter; single regime. `sweep_alignment_verdict: ALIGNED`.
- **B) `discriminating_fraction`:** All 3 seeds at same regime; expected CLEANUP r@1 in 0.60-0.85 band (in discriminating band [0.30, 0.70] boundary). `points_in_discriminating_band: 3 / 3 = 1.0` at seed-level; if r@1 lands above 0.85, MB pattern (too-easy regime).
- **C) signal_shape_compatibility_audit:** All primitives share (n_dim,) complex128 shape. `bind` output matches `unbind` + `bundle` + cleanup input shape. SHAPE_MATCH throughout.
- **D) positive_control_arms:** ARM_HRR_STORED_BUNDLE_LOOKUP serves as positive-control **negative**: it must FAIL (STORED_BUNDLE ≈ 0.00 by construction because held-out pairs are not in M_stored). If STORED_BUNDLE unexpectedly succeeds, it indicates leakage in the data split.
  - `cited_prior_metric: "Cell 1 CLEANUP=0.861 at K_DIST=3, n_dim=2048, N_C=100, N_R=10"` MEASURED@`data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json:gates.cleanup`
  - `test_regime: {n_dim: 2048, N_R: 5, N_F: 100, K_DIST: 10, N_HELDOUT: 200}`
  - `tolerance: N/A` (Cell 2 is different task class; not direct reproduction; K_DIST is intentionally 10 not 3)
  - `regime_extension_audit: SHAPE_DRIFT_with_documented_risk` (K_DIST=3→10; task changed from analogy to compositional generalization; both operations share the FHRR bind/unbind primitives which Cell 1 verified)
- **E) functional_requirements_present:**
  1. **Encode novel role-filler binding** at test time: `bind(role_q, filler_true)` → FHRR bind primitive.
  2. **Superpose target with K_DIST=10 distractor bindings**: `bundle([bind(r, f) for pairs])` → FHRR bundle primitive.
  3. **Recover filler from superposition given role key**: `unbind(B_q, role_q)` → FHRR unbind primitive.
  4. **Cleanup noisy filler estimate against codebook**: `argmax cos(filler_hat, F[i])` → cosine cleanup argmax.
  All primitives implemented directly in cell (FHRR complex phasor primitives; no external mechanism dependencies).

## 13. Framing discipline (USER-locked; non-negotiable per spawn prompt)

- **SUBSTRATE KNOWS ALMOST NOTHING** — this cell is a MECHANISM COMPOSITION PROBE on SUPERVISED SYNTHETIC role-filler regime; no general-knowledge claims.
- **HP verdict semantic:** if HP1+HP2+HP3+HP4 clear at K_DIST=10, substrate mechanism DEMONSTRATES compositional generalization on VSA-native task class with cleanup discriminator forcibly separated (Cell 1 HP3 failed at K=3; Cell 2 HP2 clearing at K=10 validates that cleanup IS load-bearing when noise level is sufficient). Combined with Cell 1's HP1+HP2 result, this makes MM_STANDARD_3_WITNESS_CANDIDATE task-class-fit META a 4-witness observation → CG_META promotion path CLEAN.
- **HF verdict semantic:** if HP1 fails (CLEANUP < 0.30), substrate cannot compositionally generalize on VSA-native task; strongly refutes task-class-fit hypothesis; requires drill (regime tuning at n_dim scale or K_DIST scale).
- **Skunkworks calibration:** Cell 1's 72.5σ result was Plate 1995 canonical reproduction (theoretical ceiling 0.95; observed 0.86) — NOT novel substrate win. Frame Cell 2 similarly: FHRR compositional generalization at K_DIST=10 is canonical VSA (Plate 1995; Frady-Sommer 2020); Cell 2 result is mechanism reproduction on held-out compositional test, NOT novel substrate discovery.
- **No σ claims without formula verification.** Cell 1 spawn iteration went through 12σ (cell-author) → 95σ (Director over-derive) → 72.5σ (Skunkworks correction). Cell 2 will compute σ from binomial CRLB directly + verify in-code before reporting.
- **Cell-author self-correction pattern is DOCUMENTED CG_META discipline** — if verdict_msg over-claims honest read of metrics, self-correct in interpretation section.
- **No "first" / "physics law" without precedent grep.** VSA compositional generalization on held-out combinations is Plate-1995-era canonical; nothing novel about the operation itself.
- **Skunkworks architectural constraint STANDS:** no 40x expansion at 2% sparsity. Cell uses dense FHRR at n_dim=2048; no sparsification.

## 14. Dispatch plan

- **Smoke gate:** local_cpu (SMOKE-only-local USER-LOCKED 2026-07-01). Estimated wall < 5min.
- **After smoke lands:** HOLD before any FULL cell authoring. Report + Director decides next.
- **If HP:** author FULL variant with n_dim sweep {1024, 2048, 4096, 8192} × K_DIST sweep {5, 10, 20, 50} × 3 seeds — separate pre-reg per Skunkworks SCHEMA-VET.
- **If HF:** memorialize as counter-evidence to compositional-generalization hypothesis; return to Director for re-scope decision (task class B may not be substrate-fit; consider Cell 4 episodic first).

## References

- Parent prereg: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (commit 891fde49a).
- Cell 1 prereg: `preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_smoke.md` (K_DIST=3, MB verdict, HP3 failed).
- Cell 1 metrics: `data/exp_stage2_vsa_cell1_analogy_completion_smoke/metrics.json` (CLEANUP=0.861 MEASURED@; K_DIST=3 too small for cleanup discriminator).
- Plate 1995 HRR capacity theory (`Holographic Reduced Representations`, IEEE TNN).
- Frady-Sommer 2020 Resonator Networks (Neural Comp): FHRR SNR scaling.
- Skunkworks architectural constraint b (2026-07-03): no 40x expansion at 2% sparsity.
- USER-LOCKED framing: `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`.
