# Cumulative META rules catalog — discipline catalog for cell-authors + verdicts

**Filed:** 2026-06-30 19:35 UTC
**Audience:** all roles (Director / cell-author / Skunkworks / Orchestrator)
**Purpose:** unified reference for the META rules atomized this arc. Each META rule is a substrate-discipline atom in `data/substrate_index/meta/atoms.jsonl` (cert-class=discipline_meta; cert_ledger delta=0).

---

## A-class (earlier; foundational; pre-2026-06-26)

- **META_RULE_AC** — pre-reg numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@. Cell pre-reg must cite source path or formula for every quantitative claim.
- **META_RULE_AF** — arms-must-differ SHA-256. Pre-flight check: cell arm output bytes hash to distinct values across arms. Prevents silent arm-collapse bugs.
- **META_RULE_AG** — baseline_in_band. Smoke must verify baseline (chance / floor / oracle) falls within expected band; failure → BLOCK_DISPATCH.
- **META_RULE_AH** — final-metrics atomic write. Use tmp + os.replace for metrics.json writes; prevents partial-write corruption on crash.
- **META_RULE_AM** — composition-first. Test composite mechanisms by composing chain-grade primitives; don't re-roll new mechanisms when composition suffices.
- **META_RULE_AN** — substrate-empirical anchors. Pre-reg references measured chain-grade primitives via absolute path, not prose framing.

## H/I/J/K/L/M (discipline foundational)

- **META_RULE_H** — CARDINALITY_OK mandatory pre-reg field for sweep-axis cells. K/depth/V_C/alpha sweeps declare EXPECTED_N_UNITS + HARD_FAIL_CARDINALITY_BREACH when observed < expected. Caught K-sweep v1 phantom (K>4096 never ran) + K-sweep v2 phantom (K>=16384 silent drop).
- **META_RULE_I** — verify-the-referent. Read per-arm metrics.json off-disk; don't propagate cell-author verdict_msg framings without independent recompute.
- **META_RULE_J** — no silent except blocks. Cell mechanisms must record + halt OR re-raise on exception, never silently swallow.
- **META_RULE_K** — strict above-floor. Discriminator must FIRE at smoke — not just verify cell runs end-to-end.
- **META_RULE_L** — band-floor MIDDLE_BAND. Results at FLOOR_THRESH are MIDDLE_BAND not HARD_PASS.
- **META_RULE_M** — production-scale instrument calibration. Discriminator tolerances must survive scale of full-N regime (smoke-N discriminator may not).

## N-class (recent)

- **META_RULE_N** — verify-referent-verdict-field + Cramer-Rao Lower Bound. Compare cell-author cited numbers against CRLB for the mechanism + measurement noise; deflate over-claims.
- **META_RULE_O** — basis-vs-use-case. Labels (substrate / encoder / family) at READOUT, not basis. Don't shape per-encoder code paths to make basis labels match.
- **META_RULE_P** — anisotropy-hurts-retrieval (Mu-Viswanath finding). Substrate retrieval degrades when codebook has anisotropic principal axes; isotropy is load-bearing.
- **META_RULE_Q** — suspect 1.000 results. Any recall=1.000 at saturating regime is suspect; verify no by-construction bypass + add noise floor.

## R/S (regime-conditional)

- **META_RULE_R** — BIAS-13/14/15 contamination/regime/mismatch. Caught contamination bugs in batch-prep + smoke baseline contamination.
- **META_RULE_S** — band-calibration regime checks. Top-1 vs top-5 / capacity-feasible / relative-bands across regimes.

## T (this session's discipline-load-bearing)

- **META_RULE_AT** — cleanup-tier-composing. Cleanup family atoms compose with related atoms (e.g., capacity multi-bank composes with cleanup at WM regime).
- **META_RULE_AO** — sparse-bipolar bundle-lift regime-conditional. Sparse-bipolar shows large bundle lift only at specific regime (low-N high-density); NOT substrate-invariant.
- **META_RULE_AP** — chain-grade Pareto gates need recency-decode floor. Pareto-AUC discriminator requires recency-decode metric above floor (0.30) to avoid by-construction wins.
- **META_RULE_AR** — centroid argmax noise-suppressing prototype primitive under capacity stress. 1/√K lower-variance estimator vs per-exemplar Bayes-LSE; HARDMAX advantage GROWS with α.

## U-class (this session's specific)

- **META_RULE_AU** — pre-dispatch GPU mandate routing check. verdict_msg=HARD_FAIL_GPU_MANDATE_BREACH + elapsed_s<1s + routed_queue='' + _phase=gpu_mandate_check → cell never ran; tier HN_INFRA_DEP not substantive negative. Caught 2026-06-30 binding-op v1 first attempt.
- **META_RULE_AV** — selftest run_mode is NOT full run_mode. verdict_msg=SELFTEST_OK + run_mode='selftest' + _phase='selftest_done' + elapsed_s << expected_full → FULL did NOT land; Director must not derive MM/HN/CG framings from selftest sanity-check data. Caught 2026-06-30 refuse-gate v1 first attempt.
- **META_RULE_AW** — seed_config_must_be_identical_for_cross_seed_aggregation. Cross-seed aggregation requires identical (M, N_h, N_c, N_replay, alpha) config across all seeds. If config differs (e.g., seed_7 ran SMOKE while seed_13/19 ran FULL), cross-seed aggregation is illegal — treat as cardinality breach + tier as HARD_FAIL. Caught 2026-06-30 cortex_hippo M=8192 v2_replay_fixed (3 "seeds" shipped 3 different configs labeled as a single CG attempt).
- **META_RULE_AX** — arm_distinctness_check_must_compare_metrics_across_arms_not_just_hashes. META_RULE_AF arms-must-differ check passes if per-arm hash differs WITHIN a single arm (MECHANISM vs RANDOM). Insufficient: must ALSO cross-check arms DIFFER ACROSS the family axis (binary_bipolar mechanism vs hrr_real mechanism vs fhrr mechanism). Caught 2026-06-30 ANCHOR 4 encoder rerun (3 of 4 encoder slots produced bit-identical metrics + mechanism_hashes — encoders not wired into the computation).
- **META_RULE_AY** (proposed; pending Skunkworks atomization) — verdict_logic_HARD_FAIL_on_self_reported_distinctness_False. Verdict-emitter must HARD_FAIL the cell if any cell-self-reported distinctness field contains False. Cell-author HARD_PASS framings must be auto-demoted when self-reported distinctness fails. Caught 2026-06-30 ANCHOR 4 v3 (cell self-reports `encoder_pair_distinctness.binary_bipolar_vs_hrr_real: False` and still emits HARD_PASS).

## Z (infra-discipline atoms 2026-06-30; pending Skunkworks atomization)

- **META_RULE_PROPOSED_AZ_SYNC_CURRENCY_CHECK** — verify `data/.metrics_sync/status.json last_run_utc` is FRESHER than cell-landing time before treating local metrics.json as authoritative. Use SCP side-pull (`metrics.fresh_<date>.json`) when sync currency is stale. Caught 2026-06-30 17:43 UTC sync-lag misframing as "Orchestrator hallucination" (corrected when Orchestrator SSH'd remote to verify).
- **META_RULE_PROPOSED_BA_QUEUE_ADD_SIBLING_HELPERS** — queue_add must auto-SCP sibling helper modules (`exp_<base>.py` core, `_<base>_core.py`, `_<base>_base.py`) when dispatching `exp_<base>_seed_<N>.py` wrappers. Caught 4× this session (Schema v4 / multihop v5 / WM encoder / Lock-in v4 + TOM v5). Fix shipped commit e0435992.

---

## Discipline composition

These META rules form a layered defense against the recurring failure modes this arc has surfaced:

1. **Cell-author layer** — H (cardinality) + AC (number provenance) + AF (arms-differ hashes)
2. **Discriminator layer** — K (smoke fires discriminator) + L (band-floor MB) + Q (suspect-1.000) + AG (baseline-in-band)
3. **Run mode layer** — AU (GPU mandate) + AV (selftest≠FULL)
4. **Cross-seed layer** — AW (seed-config-identical)
5. **Family-axis layer** — AX (arms-distinct across family) + AY (verdict-HARD_FAIL on self-reported distinctness)
6. **Atomization layer** — I (verify-the-referent) + N (CRLB check) + AT (composition)
7. **Infra layer** — AZ (sync currency) + BA (helper SCP)

Each layer addresses a different failure mode. The Stage 2 NREM Hc rescue path (Cell C v2 K-banks) had to pass through layers 1-6 to be considered chain-grade candidate; Skunkworks VET in flight is the final layer-6 check (per-K mechanism_hash distinct + by-construction check + hippo-write-path retention).

---

## How to use

- Cell-author: cite the META rules satisfied in pre-reg under "Schema-VET compliance" section.
- Skunkworks: verify each rule per layer during landed-VET.
- Director: reference when designing new cells; compose multiple rules across layers.
- USER: this catalog is the discipline trail — read for any framing claim that surprises you.

Update cadence: this doc updates when a new META rule is atomized OR a discipline gap is identified.
