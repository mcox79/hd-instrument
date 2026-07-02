# M1.11 Confidence Header v3 — reconstruction_err-only, 5-seed, 2-regime experiment design

**Filed:** 2026-07-02 evening (main-thread substantive work during testbed substrate-KB fix)
**Author:** Director (main thread)
**Status:** DESIGN — pending cell-author dispatch after Stage 1 substrate-KB closure completes
**Motivation:** Skunkworks a8f265a VET on v2 extension returned MM_TENTATIVE (not CG). Orthogonality-dividend claim FALSE; the +0.183 AUC lift v1→v2 came from ADDING reconstruction_err as a feature, NOT from the 5-way logistic combiner. Path forward per Skunkworks: "reconstruction_err-only arm at 5+ seeds with cv<0.15 AND across 2+ contamination regimes with fixed (not observed-noisy) p."

---

## Intuitive problem statement (no jargon)

The substrate has been trained on facts. Some facts are true, some are contamination (deliberately-inserted noise clusters). When you ask the substrate a question, we want a **confidence signal** — a number that says "the substrate is probably right about this answer" vs "the substrate is guessing / hallucinating."

Analogy: a doctor confident in a diagnosis vs one who says "I'm not sure, we should run more tests." The confidence is a separate SIGNAL layered on top of the answer itself.

**What v2 tried.** Combine 5 different confidence signals — hoping their mistakes wouldn't correlate, so the combination beats any single one. Skunkworks proved: no, they DO correlate, and only ONE signal (`reconstruction_err` — "does the substrate's answer stay stable if we clean it up twice?") is doing all the work.

**What v3 tests.** Prove `reconstruction_err` alone is a real, reliable confidence signal by:
1. Dropping the combiner (isolate the one that works)
2. Testing at more seeds (5+ instead of 3) to squeeze noise in the metric
3. Testing at TWO different contamination levels (20% and 50%), not just one — so we know the signal isn't accidentally tuned to one regime
4. Using DETERMINISTIC contamination (fixed p, not stochastic p that drifts) — Skunkworks caught the v2 contamination_rate varying 0.45/0.22/0.24 across seeds even though p_target=0.40 was set. That's a nuisance-variance the confidence signal shouldn't have to deal with.

If v3 passes, M1.11 Confidence Header becomes an extractable formal primitive.

---

## Prior state summary

**v1 (aa8030) — MB CG at 3-seed FULL.** First mechanism above chance for confidence discrimination. AUC=0.571. Two signals (delta_E + sigma_J). Established Option C activity/energy path.

**v2 (0a456c030) — MM_TENTATIVE.** 7-arm extension adding temp_entropy + multi_sample_vote + reconstruction_err. Logistic combiner over all 5. COMBINED_5 AUC=0.754 at 3-seed FULL (up from smoke 0.663). BUT per-seed combiner-vs-reconstruction-alone delta was +0.014/-0.003/-0.006 (mean +0.002). cv=0.159 > 0.15 CG threshold. Skunkworks: "COMBINED_5 does NOT lift over reconstruction_err alone."

**v3 (this design) — target CG.** Isolate reconstruction_err. Fix p. Add seeds. Add regime.

---

## v3 cell design

### Anchor + files

- Anchor: `substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime`
- Cell: `experiments/exp_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime.py`
- Prereg: `preregs/2026-07-02_substrate_activity_energy_confidence_signal_v3_...md`

### Regime — held constant vs v2

- N_DIM = 8192 (v2-identical)
- N_ITEMS_KB = 3600 (v2-identical)
- INTRA_COS = 0.35 (v2-identical)
- TOPK = 10 (v2-identical)
- N_test = 200 per seed (v2-identical)

### Regime — CHANGED vs v2

**(A) Deterministic contamination — p is *fixed*, not *observed-noisy*.**

v2 code: `n_false = max(1, int(round(p_target * n_items_kb / (topk * (1.0 - p_target)))))` — an estimator of how many clusters to inject to *approximately* hit p_target. Actual observed p can drift.

v3 code: for each test query, decide independently whether this query lands on a contaminated cluster via a Bernoulli(p) draw seeded from a query-id hash (deterministic per (seed, query_idx)). Compute cluster assignment such that observed p == target p EXACTLY. `contamination_rate` becomes a preregistered constant, not a per-seed observation.

**(B) Two contamination regimes.**

- REGIME_LOW: p = 0.20
- REGIME_HIGH: p = 0.50

Bracketed around v2's p_target=0.40. If the confidence signal only works at one regime, that's a regime-narrowness finding (candidate META rule) that must be surfaced.

**(C) Five seeds — {11, 17, 23, 29, 37}.** Two additional over v2's {11, 17, 23}.

### Arms

Cardinality target: `EXPECTED_N_UNITS = 4 arms × 5 seeds × 2 regimes = 40 units`.

- **ARM_RECONSTRUCTION_ERR** (LOAD-BEARING): AUC over test half using ||cleanup(cleanup(q)) - cleanup(q)||^2 as risk score. Higher risk → contaminated.
- **ARM_DELTA_E** (report-only): kept as v1 baseline for continuity.
- **ARM_SIGMA_J** (report-only): kept as v1 baseline for continuity.
- **ARM_ABLATED_RANDOM** (positive control): uniform-random risk vector; AUC → 0.50 by construction (verifies scoring rig).

**Explicitly REMOVED vs v2:** `ARM_TEMP_ENTROPY`, `ARM_MULTI_SAMPLE_VOTE`, `ARM_COMBINED_5`. Combiner is falsified; keeping them wastes compute and pretends the mechanism might still work.

### Pass bands

**HARD_PASS (target CG):** across ALL 5 seeds × BOTH regimes:
- ARM_RECONSTRUCTION_ERR AUC ≥ 0.65
- Cross-seed cv (AUC) < 0.15 in each regime
- Positive control ARM_ABLATED_RANDOM AUC ∈ [0.45, 0.55] each seed × regime
- Arm-per-seed digests unique (`arms_differ_verified`)
- `contamination_rate` observed EXACTLY equals `p_target` (deterministic verification)

**HARD_FAIL:** ARM_RECONSTRUCTION_ERR AUC < 0.60 mean across seeds in EITHER regime, OR cv ≥ 0.25 in either regime.

**MIDDLE_BAND (partial):** AUC ∈ [0.60, 0.65) OR cv ∈ [0.15, 0.25). Would land Tentative_MM_v3; not CG; requires v4 with either different mechanism or scale.

### Ablation controls (proving mechanism vs artifact)

- **Positive control:** ARM_ABLATED_RANDOM — pins scoring rig at chance
- **Regime consistency:** cv across seeds in each regime — catches per-seed contamination-nuisance if deterministic-p patch fails
- **Regime dispersion:** ratio of mean_AUC(REGIME_HIGH) / mean_AUC(REGIME_LOW) — flag if extreme (>1.5x or <0.67x) as regime-narrow

### Compute architecture

- (a) batched-GPU / batched-CPU-torch (v2-identical)
- Per-seed × regime wall: ~5-15s GPU, ~2-5min CPU-torch
- FULL total: ~5min GPU, ~50min CPU-torch (2 regimes × 5 seeds)
- Route: `remote_cpu_queue` (single dispatch, no chunking); FULL wall estimate well within 1800s timeout

### CELL-TEMPLATE MANDATORY compliance

- `arms_differ_verified: True` (4 arms × 5 seeds × 2 regimes → 40 distinct digests)
- `final_metrics_atomicity: tmp_replace` (via `_seed_checkpoint.write_metrics`)
- `except SystemExit: raise` before `except Exception`
- `crlb_n/a`: "AUC discriminator on binary contamination; no closed-form CRLB"
- `baseline_in_band`: ARM_ABLATED_RANDOM = 0.50 by construction
- `discriminator_survives_scale`: N_DIM=8192 (CG regime; matches v2)
- HARD_PASS strictly above floor: 0.65 vs floor 0.55
- `HP_SCOPE`: ARM_RECONSTRUCTION_ERR load-bearing; others report-only
- `cardinality_ok`: 40 units expected
- `calibration_check`: default_ok (no combiner → no calibration parameters)
- `progress_logging: print_flush_true`
- `start_marker + heartbeat + crash_diagnostic`: standard wiring

### Substrate primitives called

- `k_NN_lookup` (cleanup step, called twice per query for reconstruction_err)
- `hd_bind` / no unbind (reconstruction is just cleanup composition)
- storage strategy: `SHARDED` (per USER-locked storage-strategy law for compositional cells)

---

## What happens next based on v3 verdict

### If HARD_PASS at CG (both regimes, all 5 seeds, cv<0.15, AUC≥0.65)

- v3 CG'd at MM_TENTATIVE → CG promotion
- **M1.11 Confidence Header extraction FIRES:** author `hdlab/confidence_header.py` following M1.9 SemanticParser extraction pattern (INPUT REGIME discipline, 10 selftests, ASCII-only, no cortex.py wiring in initial extract)
- Cortex primitive stack: M1.3 + M1.4 + M1.5 + M1.6 + M1.7 + M1.8 + M1.9 + M1.11 (M1.10 dispatch parallel arc)
- M1.11 becomes callable confidence readout for future glass-box M3 conversational cortex

### If MIDDLE_BAND (AUC 0.60-0.65 or cv 0.15-0.25)

- v3 filed as MM
- Options for v4:
  - Try posterior-entropy mechanism instead of reconstruction_err
  - Try attention-dispersion at cleanup step
  - Try residual-stream norm
  - Scale up N_test to 500 (v2 used 200; possibly noise-limited)
- M1.11 extraction DEFERRED further

### If HARD_FAIL (AUC<0.60 in either regime)

- Option C mechanism family is genuinely below CG threshold at multi-seed multi-regime
- Confidence signal work becomes a research question again, not a primitive-extraction path
- File CG_HONEST_NEGATIVE atom closing Option C activity/energy branch of confidence work
- Pivot to alternative confidence mechanism families (posterior-based, attention-based, residual-based per Skunkworks)

---

## Blockers before dispatch

1. Testbed af135622 must complete substrate-KB fix (Stage 1 closure). Not a hard blocker on this cell technically, but Stage 1 closure precedes any Stage 3 cortex-primitive extraction commits.
2. Cell must pass smoke gate on local_cpu_queue (USER-locked SMOKE_ONLY_LOCAL_CPU 2026-07-01).
3. Pre-reg SCHEMA-VET by Skunkworks before FULL dispatch.

## Estimated timeline (once dispatch fires)

- Cell authoring (hdi_exp_dev): ~30-45 min
- Smoke on local_cpu: ~15 min run + smoke iteration if needed
- Pre-reg SCHEMA-VET (Skunkworks): ~5 min
- FULL dispatch on remote_cpu (10 seeds × 2 regimes with single-dispatch pattern): ~50 min wall
- Skunkworks landed-VET: ~5 min
- If CG: hdlab/confidence_header.py extraction: ~30 min (similar to M1.9 pattern)

Total end-to-end: ~2-3 hours from dispatch to potential M1.11 primitive availability.

---

## Position in program

Confidence signal is one of the four gaps flagged today for M3 cortex conversational agent. The other three:
- M1.9 SemanticParser: ✅ CG'd + extracted to hdlab today
- M1.10 Response Planner: ✅ designed (P_CG=0.60); dispatch pending
- Semantic-parser + Response-planner ROUNDTRIP: to be tested by M1.10 v1 arm
- **M1.11 Confidence Header (this design):** the remaining substantive gap

If v3 lands CG, all four M1.x primitives sitting under cortex have a completion path. Then Stage 3 cortex mechanism-primitive stack is meaningfully closed pending USER-directed extensions (M1.12+ analogy, planning, etc.).

Stage 4 language ingest is a separate, deferred lane (USER 2026-06-26); M1.11 does not depend on or advance it.
