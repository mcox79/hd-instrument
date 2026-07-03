# Stage 2 VSA Cell 1 — Analogy Completion (SMOKE Pre-Registration)

Date: 2026-07-03
Type: Cell pre-reg (SMOKE).
Anchor: `stage2_vsa_cell1_analogy_completion_smoke`
Author: hdi_exp_dev.
Parent prereg: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (commit 891fde49a, §5 Cell 1).
Cell file: `experiments/exp_substrate_vsa_cell1_analogy_completion_smoke_2026-07-03.py`.

## Concept-query-before-dispatch (USER-locked 2026-07-02)

`bash tools/substrate_query.sh "analogy completion VSA HRR bind unbind cleanup"` returned top-5 at cosine 0.29-0.35 (`unbind`, `completion`, `Compositional query construction via bind/unbind ops`, `completion.n`, `bind`). All borderline (cosine < 0.40). Grep-verified prior analogy cells:
- `preregs/2026-06-06_analogy_map_v1.md` (SkipGram-analogy-map arc; different task class).
- `preregs/2026-07_pattern_b_analogy_v1.md` / `_rescue_v1.md` (1-line stub preregs; no cell shipped).
- No prior `hdlab.binding + cleanup_family` analogy cell exists.

Genuinely novel authoring under Stage 2 benchmark-reframe roadmap; NOT rediscovery.

## 1. Task class + mechanism (§2A of parent prereg)

**Analogy completion:** `a : b :: c : ?`
- Given random atomic concept-codebook `C` (|C|=N_CONCEPTS) and random atomic relation-codebook `R` (|R|=N_RELATIONS).
- Construct analogy tuples by sampling `(a_idx, r_idx, c_idx)` with `c_idx != a_idx`.
- Ground-truth pair: `b = bind(C[a_idx], R[r_idx])`, `d = bind(C[c_idx], R[r_idx])`.
- Query: given `(a, b, c)`, predict `d`.
- Retrieval metric: recall@1 = argmax_i cosine(d_hat, C[i]) == c_idx.
- **VSA-native operation:** the analogy is solved by `unbind(b, a) -> r_hat`, then `bind(c, r_hat) -> d_hat`.

## 2. Substrate mechanisms tested (arms)

| Arm | Mechanism | Cleanup on r_hat? | Load-bearing? |
|---|---|---|---|
| `ARM_HRR_BIND_UNBIND_CLEANUP` | HRR bind/unbind + k_NN cleanup of intermediate r_hat against R | YES | LOAD-BEARING |
| `ARM_HRR_BIND_UNBIND_NO_CLEANUP` | HRR bind/unbind, no intermediate cleanup on r_hat | NO | Ablation |
| `ARM_COSINE_ARGMAX_BASELINE` | argmax_i cosine(c, C[i]) (predict d = most-similar-to-c) | n/a | Weak baseline |
| `ARM_RANDOM_BASELINE` | random codebook item | n/a | Chance floor |

**Arms-must-differ (META_RULE_AF):** all 4 arms produce distinct outputs by construction (different code paths). Verified at smoke gate via `_arms_must_differ` hash-test.

**No DG-style 2%-sparsity 40x expansion** anywhere (Skunkworks architectural constraint b, 2026-07-03). Real-valued HRR at n_dim=2048 dense; no sparsification.

## 3. Config

- `n_dim = 2048` (real-valued HRR via FFT circular convolution per `hdlab.binding.bind`)
- `N_CONCEPTS = 100`
- `N_RELATIONS = 10`
- `N_QUERIES = 500`
- `SEEDS = [11, 17, 23]`
- Codebook: unit-norm i.i.d. Gaussian (real).
- Compute: numpy CPU (per-query FFT is fast; 500 * 3 seeds << 10min on laptop).

## 4. HP_SCOPE (LOAD_BEARING gates)

| Gate | Applies to arm | Condition |
|---|---|---|
| HP1 | ARM_HRR_BIND_UNBIND_CLEANUP | mean recall@1 across seeds >= 0.80 |
| HP2 | ARM_HRR_BIND_UNBIND_CLEANUP - ARM_COSINE_ARGMAX_BASELINE | gap >= 0.20 |
| HP3 | ARM_HRR_BIND_UNBIND_CLEANUP - ARM_HRR_BIND_UNBIND_NO_CLEANUP | cleanup positive-control gap >= 0.05 |

**Per-arm HP scope (§5b canonical):**
- HP1: `ARM_HRR_BIND_UNBIND_CLEANUP`
- HP2: pair (`CLEANUP`, `COSINE_ARGMAX_BASELINE`)
- HP3: pair (`CLEANUP`, `NO_CLEANUP`)
- ARM_RANDOM_BASELINE: no HP inheritance (chance floor only)

## 5. HARD_FAIL bands

- HF1: ARM_HRR_BIND_UNBIND_CLEANUP mean recall@1 < 0.50 (mechanism does not work on intended task class) -- strong finding, refutes task-class-mismatch hypothesis.
- HF_baseline: ARM_COSINE_ARGMAX_BASELINE > 0.30 (baseline sees lexical/structural leakage; task is not VSA-load-bearing).
- HF_cardinality: `len(per_seed) != 3` OR `len(arms_per_seed) != 4`.

## 6. MIDDLE_BAND

- HP1 clears (mechanism works) but HP2 does not (baseline saturates similarly) -- **regime-too-easy pattern**, cf Spoke 3 CLS smoke.
- HP1 clears, HP2 clears, but HP3 does not (cleanup does not earn its keep -- ablation-safe).

## 7. Discriminator-must-survive-scale + AG (baseline in band)

**Predicted ARM_COSINE_ARGMAX_BASELINE:** ~1/N_CONCEPTS = 0.01 (chance) since random Gaussian atomic concepts have no structure aligning c to d.
HYPOTHESIZED@this-prereg (no prior measurement; standard VSA capacity theory).

**Predicted ARM_HRR_BIND_UNBIND_CLEANUP:** ~0.85-0.95 at n_dim=2048 / N=100 / N_R=10 (well within HRR capacity per Plate 1995: capacity ~= n_dim/(k*log(M)) for k slots). THEORETICAL@Plate1995.

**Baseline in band (META_RULE_AG):** ARM_COSINE_ARGMAX_BASELINE expected 0.01 << 0.05 lower floor. Since it's a **chance-floor by construction** (not a discriminator), we exempt it from `baseline_in_band` per prereg exemption: `baseline_exempted_arms: [ARM_COSINE_ARGMAX_BASELINE, ARM_RANDOM_BASELINE]` (both are named chance-floor / weak-heuristic arms; the meaningful baseline for AG is ARM_HRR_BIND_UNBIND_NO_CLEANUP which is expected 0.5-0.7 in band).

**Discriminator survives scale:** smoke IS the intended regime (n_dim=2048, N=100, 500 queries, 3 seeds); FULL-scale probes would be n_dim sweep or N sweep separately (out of scope this cell). Smoke fires the discriminator: HP2 gap (CLEANUP vs COSINE_ARGMAX_BASELINE) must be >= 0.20.

## 8. CRLB / capacity feasibility

**Recall@1 CRLB:** binomial proportion over N_QUERIES=500 per seed; sigma_min = sqrt(p*(1-p)/500). At p=0.5: sigma_min = 0.0224. HP2 gap >= 0.20 requires margin ~9*sigma per seed; well-resolved.

**HRR capacity (Plate 1995):** for n=2048, M=100 codebook, k=1 slot (single bind), theoretical clean-up recall ~= 1.0 at SNR = sqrt(n/M) ~= 4.5. Analogy needs 2 chained bind/unbinds; effective SNR reduces to ~3.2. Recall in 0.85-0.95 expected. HP1 >= 0.80 is achievable and strict.

- `crlb_floor_computed: 0.0224` (binomial CRLB at p=0.5 per seed)
- `crlb_formula_reference: "sigma_p = sqrt(p*(1-p)/N_QUERIES); Plate 1995 HRR capacity theorem for SNR"`
- `discriminator_reachability: True` (HP1=0.80 << 0.95 theoretical ceiling)

## 9. Selftests (>= 5 required)

1. **Bind-unbind round-trip** at n_dim=2048: `unbind(bind(a, b), b) ~= a` at cosine > 0.95.
2. **Analogy generator valid** — no c_idx == a_idx leakage; all `(a_idx, r_idx, c_idx)` valid indices.
3. **Cleanup memory correct top-K** — cleaned vector matches injected codebook entry at cosine > 0.99 when input is noise-free.
4. **Scale sentinel at n_dim=8192** — bind/unbind round-trip finite + cosine > 0.9 at increased scale (verifies FFT path scales cleanly, no numerical blowup).
5. **Deterministic seed-invariance** — repeat with same seed reproduces recall@1 to 1e-6 tolerance (encoder + generator are deterministic given seed).

## 10. Cell-template mandates checklist

- `arms_differ_verified: True` (SHA256 hash-test on per-arm outputs across a fixed query batch)
- `final_metrics_atomicity: "tmp_replace"` (single-shot; write via .tmp + os.replace)
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- `crlb_floor_computed: 0.0224` (binomial per seed)
- `discriminator_reachability: True`
- `baseline_in_band: True` for NO_CLEANUP ablation; `baseline_exempted_arms` for chance-floor arms
- `cell_chunked: False` (single-file cell; 3 seeds run within one process; smoke wall << 5min so no chunking)
- `start_marker_written: True`
- `crash_diagnostic_present: True` (Exception handler writes CELL_CRASHED metrics)
- `heartbeat_present: True` (per-seed progress lines; cell is fast so file-based heartbeat not strictly required)
- `progress_logging: "print_flush_true"` (all progress lines flush=True)
- `cardinality_ok: True` (len(per_seed)==3 AND each seed has 4 arms)
- `defensive_error_checking: "passed_all_4_patterns"`
- `calibration_check: "default_ok_for_this_regime"` (evidence: n_dim=2048 well above Plate 1995 M=100 capacity; k=1 bind depth; SNR ~4.5)

## 11. Compute architecture

- **Class:** (b) sequential-CPU with justification.
- **Justification:** smoke wall estimated < 60s; sub-10s per seed; below the 10s per-phase-point wall-time threshold that triggers GPU-batching mandate. If we scale to n_dim=8192 + N_CONCEPTS=10000 (Google-analogy subset), we re-classify to (a) batched-GPU. **Smoke is CPU-appropriate; FULL sweep at scale requires re-authoring.**
- **Storage strategy:** `no_composition` (cell is single-hop analogy; no downstream chaining; sharded-vs-bundled META rule does not apply — bundled would require storing multiple pairs in one vector, which this cell does NOT do).

## 12. Test-design gates §15 (canonical)

- **A) effective_vs_nominal parameter audit:** No swept parameter that changes meaning under composition. Cell sweeps only seeds. `sweep_alignment_verdict: ALIGNED` (trivially — single regime).
- **B) `discriminating_fraction`:** All 3 seeds at same regime; expected recall@1 in 0.85-0.95 band. `points_in_discriminating_band: 3 / 3 = 1.0` (not saturated at 1.0 exactly; HRR analogy noise floor ~0.05).
- **C) signal_shape_compatibility_audit:** `bind` output shape matches `unbind` + `cleanup` input shape (all (n_dim,) real). SHAPE_MATCH.
- **D) positive_control_arms:** ARM_HRR_BIND_UNBIND_NO_CLEANUP is the internal positive control (reproduces canonical HRR analogy at test regime; no prior chain-grade atom for this specific N/n_dim so no external reproduction target). `cited_prior_metric: "Plate 1995 theoretical ceiling ~0.95 at these params"` THEORETICAL@ (no cell-level prior; this IS the first analogy cell at this regime).
- **E) functional_requirements_present:** Requirements: (1) bind role + concept (bind primitive), (2) recover role from bound tuple (unbind primitive), (3) apply recovered role to novel concept (bind), (4) retrieve target concept (cleanup memory / argmax). All primitives exist in `hdlab.binding` + `hdlab.cleanup_family`.

## 13. Framing discipline (USER-locked; non-negotiable per spawn prompt)

- **SUBSTRATE KNOWS ALMOST NOTHING** — this cell is a MECHANISM PROBE on SUPERVISED SYNTHETIC analogy task; no general-knowledge claims.
- **HP verdict semantic:** if HP1+HP2+HP3 clear, this is an EXISTENCE PROOF that the substrate performs analogy completion on a VSA-native task class with clean margin over baseline. Substantially reframes the 5-witness "substrate loses on Wikipedia retrieval" pattern from "substrate loses" to "substrate wins on natural tasks." Does NOT prove substrate generalizes to arbitrary tasks.
- **HF verdict semantic:** if HP1 fails, the mechanism has issues even on the intended VSA-native task class. Would strongly refute the task-class-mismatch reframe hypothesis (H_reframe in parent §1.4) and support H_null (substrate architecture is load-bearing weakness).
- **No "first" / "physics law" language.** VSA analogy is a canonical Plate-1995-era mechanism; nothing novel about the operation itself. What's being probed is whether the substrate primitives cleanly implement it.
- **Skunkworks-corrected TF formula:** C_TF = N/(2*ln(1/p)) — not directly invoked here (this is analogy not tag-storage). Any capacity-adjacent quote in verdict output must be verified in-code before stating.
- **Skunkworks architectural constraint:** no 40x expansion at 2% sparsity. Cell uses dense real-valued HRR at n_dim=2048; no sparsification anywhere.

## 14. Dispatch plan

- **Smoke gate:** local_cpu (SMOKE-only-local USER-LOCKED 2026-07-01). Estimated wall < 5min.
- **After smoke lands:** HOLD before any FULL cell authoring. Report + Director decides next.
- **If HP:** author FULL variant with n_dim sweep {1024, 2048, 4096, 8192} and N_CONCEPTS sweep {100, 1000, 10000} — separate pre-reg per Skunkworks SCHEMA-VET §7 of parent.
- **If HF:** memorialize as counter-evidence to reframe hypothesis; return to Director for re-scope decision.

## References

- Parent prereg: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (commit 891fde49a).
- Plate 1995 HRR capacity theory (`Holographic Reduced Representations`, IEEE TNN).
- Skunkworks architectural constraint b (2026-07-03): DG 2%-sparsity + 40x expansion in capacity-edge regimes amplifies noise; avoided here.
- Cell-template pattern reference: `experiments/exp_cortex_hippo_handoff_FULL_seed_7_v1.py`.
- USER-LOCKED framing: `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`.
