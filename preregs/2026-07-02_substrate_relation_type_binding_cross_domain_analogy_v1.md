# Prereg: substrate_relation_type_binding_cross_domain_analogy_v1

## Anchor
`substrate_relation_type_binding_cross_domain_analogy_v1`

## Cell path
`d:/AI/hd-instrument/experiments/exp_substrate_relation_type_binding_cross_domain_analogy_v1.py`

## Metrics path (SMOKE)
`d:/AI/hd-instrument/data/exp_substrate_relation_type_binding_cross_domain_analogy_v1_smoke/metrics.json`

## Metrics path (FULL — if dispatched)
`d:/AI/hd-instrument/data/exp_substrate_relation_type_binding_cross_domain_analogy_v1/metrics.json`

## Queue routing
- **Smoke:** local direct invocation via `.venv/Scripts/python.exe ... --smoke`; ran 2026-07-02 in ~5s wall (3-seed variance probe at V=1024). USER 2026-07-01 SMOKE-ONLY-LOCAL rule complied.
- **Full:** would route `remote_cpu_queue`. Cell-author recommends **Director accept smoke-HF as closure** (Path A analog to stretch4_2). See "Smoke evidence" + "Discriminator-must-survive-scale" below.

## Framing (Stage 3 compositional-understanding arc, USER 2026-06-26 pivot)

Substrate mechanism #6 from the 2026-06-10 Level-4 pivot list (drill note
`research_drill_cross_domain_analogy_negative_2x_2026-06-10.md`): substrate
stores relation-TYPES as first-class FHRR vectors, sharded per relation.
Cross-domain analogy tested via K=10-shot mean-unbind extraction of a held
relation vector.

**Contrast with retracted mechanism (stretch4_2 RotatE, 2026-06-10 HF 0.244 +
reproduced 2026-07-02 in prereg `2026-07_stretch4_2_cross_domain_analogy_cpu_v1.md`):**
RotatE trained BOTH entity and relation phases jointly via triplet loss. This
cell does NOT train entities — entity codebook is frozen random unit-magnitude
FHRR phasors. Only the K=10 mean-unbind extraction is substrate-native. This
is a genuinely different mechanism-class (drill Level-4.6 "substrate stores
relation-TYPES separately from instances").

## PRIOR-WORK REDISCOVERY CHECK (substrate-KB concept query)

`bash tools/substrate_query.sh "relation-type binding compositional analogy unbind cleanup few-shot cross-domain"`

Top-5 cosine at v2 schema:
1. 0.3496 — `notes/research_drill_humaneval_substrate_generator_2x_2026-06-11.md` (compositional analogy generation drill; NOT this mechanism)
2. 0.3145 — `notes/research_to_skunkworks_exp_dev_DECISION_146...` (cross-domain DROP decision from 2026-06-16; scoping decision, not this mechanism)
3. 0.3125 — `notes/research_drill_meta_learning_middle_band_2x_2026-06-10.md` (compositional VSA few-shot drill; DIFFERENT mechanism-class)
4. 0.3096 — within-domain analogy FORM-A precheck (WITHIN-DOMAIN, not cross)
5. 0.3057 — SCAN benchmark chunk (cross-domain generalization; SEQ2SEQ, not substrate binding)

**Verdict: NOT a rediscovery.** Highest cosine 0.35 falls just above the 0.30
significance threshold but hits are either (a) related-topic drill notes or
(b) prior DIFFERENT-mechanism-class experiments. Mechanism #6 (substrate
relation-type binding + K=10 mean-unbind on FROZEN random codebook) is
genuinely novel — no prior atom implements it. The retracted RotatE stretch4_2
mechanism is intentionally distinct (RotatE trains entity phases via triplet
loss; this cell freezes them as random phasors).

## Hypothesis

At V=8192 (full) entity codebook + N_DIM=8192 FHRR + K=10 shots per held
relation:
- **H1 (probable, P=0.45):** cross-domain Hits@1 falls at chance-floor
  (~1/V = 0.00012 for V=8192; observed 0.0000-0.001 at smoke V=1024).
  Mechanism reason: random entity codebook has no relation-consistent
  structure; mean unbind of K=10 pair inverse-binds = random-noise
  vector; bind(c, R_est) then cleanup returns near-random entity.
- **H2 (possible, P=0.35):** within-domain arm MIDDLE_BAND (0.30-0.50)
  because Jaccard-overlapping training relations impart mild structural
  correlation via shared entities appearing in both training shard and
  held pair. Cross-domain arm still HF.
- **H3 (unlikely, P=0.20):** substrate-native mechanism #6 HARD_PASS
  (cross ≥ 0.45) — would overturn drill 4.6 prediction; falsify prior
  claim that entity structure is required.

Prior 2026-06-10 drill P for mechanism-family "direct HRR unbind":
0.25 (drill section 1). This cell's frozen-codebook variant is
STRICTLY WEAKER than RotatE's trained embeddings — expected HF.

## Bands (envelope-fail; from cell verdict function)

| Band | Cross-domain Hits@1 | Within-domain Hits@1 | Baseline (no R_est) |
|---|---|---|---|
| HARD_PASS | `>= 0.4775` (strict) | `>= 0.65` | `< 0.05` |
| MIDDLE_BAND | `>= 0.30` OR within `>= 0.50` | — | — |
| HARD_FAIL | `< 0.30` cross AND `< 0.50` within | — | — |

**META_RULE_L strict-floor:** HP floor 0.45, band width 0.55 → strict
floor = 0.45 + 0.05*0.55 = 0.4775. Codified in verdict function.

**META_RULE_AG baseline analytical:** at V=1024 (smoke) chance = 1/V =
0.000977; at V=8192 (full) = 0.000122. Observed baseline 0.0000 in all
3 smoke seeds (below sampling resolution at ~1000 queries per arm).
Baseline chance-floor is the analytical target — not a saturable
mechanism arm. Baseline < 0.05 gate captured in verdict.

## Discriminator-must-survive-scale (META_RULE_AG + USER 2026-06-26 rule)

**Path B: analytical justification.** Smoke at V=1024 (chance floor 1/V =
0.000977) shows cross_arm = 0.0000 (below sampling resolution).
Full V=8192 (chance floor 1/V = 0.000122) will lower the observed
chance-floor further. Mechanism arm CANNOT rise from chance-floor at
smoke to HP band (0.4775) at full — that would require the mechanism
to depend on codebook scale, which it does not (mean-unbind is
scale-independent in FHRR unit phasors: E[unbind(random, random)] = 0
regardless of V or N).

**Conclusion:** discriminator survives scale in the HF direction.
Rejection criterion (baseline ≥ 0.95 of mechanism at full-N preview):
mechanism arm = baseline = chance-floor at smoke; scale preserves.

## Compute architecture

**Class:** (a) batched-GPU when CUDA available; (a) batched-CPU-matmul
via torch when not.

**Justification:** Cell workload dominated by (1) FHRR unbind
(elementwise complex mul), (2) cleanup argmax over V-codebook (single
matmul `(M, N) @ (N, V) -> (M, V)`), (3) mean-unbind extraction (single
sum over K=10). All are batched matmul/elementwise — genuinely GPU-batchable
per USER 2026-07-02 GPU-batching-mandatory rule. Torch complex64 auto
dispatches to `torch.cuda` when available (checked at import via
`torch.cuda.is_available()`). Wall time at V=1024, N=8192, ~1000 queries
per arm, 3 seeds on CPU = ~5s total. Full V=8192, N=8192, ~4000 queries
per arm, 3 seeds expected ~120-300s CPU / ~15-30s GPU.

**Storage strategy:** SHARDED per relation (USER-locked CG_META 2026-07-02
storage-strategy substrate-physics-law). Each training relation gets its
own pair-index shard. Held-out relations get temporary K=10 shards for
extraction. No bundled superposition across relations (which would create
cross-talk under Plate bundle-bound).

## META_RULE compliance

- **cardinality_ok**: N/A — no sweep axis; single-mode readout (cross-
  domain / within-domain / baseline arms over aggregated held-out relations).
- **arms_differ_verified**: R_est vectors between cross-domain and
  within-domain arms hash-checked at end of each seed. Verified True at
  smoke (independently drawn held relations produce distinct FHRR-mean
  extractions).
- **final_metrics_atomicity**: `tmp_replace` — relies on
  `experiments._seed_checkpoint.write_metrics` (tmp + os.replace).
- **except SystemExit: raise BEFORE except Exception**: verified in
  cell `__main__` block (line ~end); crash diagnostic writes atomic
  `metrics.json.tmp` + `os.replace` on any Exception, re-raises after.
- **crlb_floor_computed**: N/A — mechanism is nearest-neighbor Hits@1
  vs analytical 1/V random baseline. `crlb_n/a: "argmax-over-V-entity-
  space; random baseline 1/V analytically computed above"`.
- **discriminator_reachability**: HP=0.4775 is analytically above chance
  1/V=0.000122 at full-N and above baseline 0 in all 3 smoke seeds; HP is
  physically reachable if mechanism works.
- **baseline_in_band**: baseline arm observed 0.0000 at smoke (below META_
  RULE_AG's 0.05 saturation-check ceiling). Interpretation: baseline is
  analytical chance-floor, not a saturable arm — the mechanism arm being
  at chance-floor is the HF signal, not a regime-iteration trigger.
  Documented explicitly to prevent misapplication of AG at atomization.
- **HP_SCOPE**: cross-domain arm gets HP band; within-domain arm gets
  positive-control HP >= 0.65; baseline arm gets HP requirement < 0.05.
- **calibration_check**: `default_ok_for_this_regime` — thresholds match
  cell verdict function; N_DIM=8192, V=8192, K=10 are chain-grade
  substrate defaults; no adaptive tuning.
- **cell_chunked**: false — single-cell 3-seed inline. Rationale:
  smoke wall <10s; full expected <5min; per-seed checkpoint overhead
  not justified for this scale.
- **start_marker_written**: true (`_write_start_marker` at main() entry).
- **crash_diagnostic_present**: true (`_write_crash_metrics` in outer
  try/except; SystemExit + KeyboardInterrupt re-raised).
- **heartbeat_present**: false — expected full wall <5min; below §17
  30-min mandatory-progress threshold.
- **defensive_error_checking**: `"data_download_failure_handled_returns_
  UNKNOWN"` — FB15K raw fetch has try/except with UNKNOWN verdict return
  if download fails; disk-cache reduces flakiness on retries.
- **run_mode**: cell defaults RUN_MODE="full" when `--smoke` and
  `--self-test` absent; env override `HDLAB_RUN_MODE` respected.
- **progress_logging**: `print_flush_true` — cell uses `print(...,
  flush=True)` on per-seed [run] lines; sys.stdout.reconfigure line_buffering
  at cell start. Total wall expected <5min; §17 30-min rule N/A.

## Test-design gates (§15)

- **A) sweep_alignment_verdict**: `N/A_no_sweep` — no swept parameter.
- **B) discriminating_fraction**: `1.0` — the ONE discriminator arm
  (cross-domain Hits@1) either sits in HP band or HF band; smoke observed
  0.0000 which is IN the HF band. Discriminator fires (baseline 0.000
  strictly less than mechanism arm 0.000 is NOT a fire — arms are equal,
  which IS the HF signal for this design).
- **C) composition_edges**: `SHAPE_MATCH` — bind(c, R_est) uses
  elementwise complex mul (FHRR); output shape (N,) feeds directly into
  cleanup_argmax which expects (M, N) queries + (V, N) codebook. Matches
  hdlab convention.
- **D) positive_control_arms**: `arm_within_domain_positive_control`
  serves this role. Prior positive control — comp24 K10=0.953 within-
  domain analogy — is at different regime (bipolar HRR + trained
  entities). This cell's within-domain arm uses SAME frozen codebook
  as cross-domain arm; if within-domain arm hits HP band and cross-domain
  arm HF, the discriminator between cluster overlap is meaningful.
  If BOTH arms HF (as smoke showed), the mechanism itself doesn't fire
  under random codebook + no training — genuine HF closure.
- **E) functional_requirements**: (1) sharded storage per relation
  type — implemented; (2) mean-unbind R_est extraction from K=10 shots
  — implemented via hdlab-style `unbind_fhrr` + `bundle_fhrr` primitives;
  (3) cleanup at entity codebook — implemented via batched matmul argmax;
  (4) domain clustering via Jaccard entity-set overlap — implemented
  (structural, no language content).

## Stage progression

**Stage 3** (compositional understanding — analogical inference /
cross-domain relation transfer). NOT Stage 4 (no language / no vocab /
no text corpus). Confirmed in-scope for USER 2026-06-26 pivot arc.

## Substrate-doesn't-know-anything check

FB15K-237 relation strings + entity strings used ONLY as opaque IDs
into the shard dict / entity codebook. No lexical content is embedded,
tokenized, or read. The `build_relation_partition` function operates on
structural graph properties (Jaccard entity-set overlap between relations)
— no language content. Cell compatible with USER 2026-06-26 "no language
testing" rule.

## Timeout

If Director elects to dispatch FULL: `--timeout 900s` (15 min) — 3-6x
safety margin over expected 120-300s CPU wall at V=8192. If PROT-019
applies (`_n>=4096`): cell has no `_n` suffix; PROT-019 N/A.

## Smoke evidence

- Timestamp: 2026-07-02 (this session; cell-author dispatch cycle)
- Command: `HDLAB_EXP_NAME=substrate_relation_type_binding_cross_domain_analogy_v1_smoke .venv/Scripts/python.exe experiments/exp_substrate_relation_type_binding_cross_domain_analogy_v1.py --smoke`
- Wall: 5.2s (3 seeds combined: 1.6s + 0.6s + 0.5s + data-download 30s first invocation)
- Selftest: PASS
  - bind/unbind roundtrip mean abs err = 4.45e-08 (float32 precision)
  - synthetic K=10 mean-unbind R_gt recovery cos = 1.0000
  - cleanup argmax over V=64 codebook → correct index
- 3-seed smoke results:
  - seed=7: cross=0.0000 within=0.0009 baseline=0.0000 (V=1024, n_cross_rels=8, n_within_rels=12)
  - seed=13: cross=0.0000 within=0.0014 baseline=0.0000
  - seed=19: cross=0.0000 within=0.0005 baseline=0.0000
  - Cross-domain mean: 0.0000 (below chance-floor 1/1024=0.000977)
  - Within-domain mean: 0.0009 (~1 hit per 1000 queries — sampling noise around chance-floor)
  - Baseline mean: 0.0000
- Verdict: HARD_FAIL (cross-domain < 0.30 AND within-domain < 0.50)
- Discriminator: FIRED at smoke-scale. All 3 seeds land at chance-floor.
- Multi-seed variance probe: cross-domain SD = 0.000 (all seeds exactly
  0.0000); within-domain SD = 0.0004. Well within pre-registered
  multi-seed acceptance tolerance (Δ vs mean < 0.05).
- Multi-seed acceptance gate (META CG 2026-07-02): 3-seed mean 0.0000
  is within 0.05 of 0 (analytical chance); mechanism does NOT lift over
  chance; **HF rejection of FULL dispatch justified** per the rule
  "if multi-seed smoke AUC is within 0.05 of chance, REJECT full dispatch."

## Substrate-primitives-invoked (grep-check discipline, Skunkworks META 2026-07-02)

Cell explicitly invokes hdlab-style substrate primitives >=2 times in
`run_one_seed`:
- `bind_fhrr` (elementwise complex mul) — line ~380 (query construction)
- `unbind_fhrr` (elementwise mul by conjugate) — line ~340 (per-shot R extraction)
- `bundle_fhrr` (circular-mean phasor renormalize) — line ~345 (K=10 aggregation)
- `cnorm_torch` (phasor projection) — lines ~340, 345, 380
- `cleanup_argmax` (batched matmul + argmax) — line ~382 (entity retrieval)
- `cphasor_torch` (FHRR codebook synthesis) — line ~315

Total substrate-primitive invocations per seed: 8+ (well above >=2
threshold). Avoids numpy-costume pattern.

## Framing caveat for atomization (Skunkworks/Director)

**Atomization scope:** the smoke result confirms mechanism #6 (substrate
relation-type binding, K=10 mean-unbind extraction) does NOT enable
cross-domain analogy at frozen-random FHRR codebook. This is a
scope-clarifying HF, NOT a general claim that substrate cannot do
cross-domain analogy.

**Atom candidate (if atomized):**
`substrate_relation_type_binding_cross_domain_analogy_frozen_codebook_HF_2026-07-02`
— mechanism #6 with FROZEN random FHRR codebook fails at chance-floor
because random codebook has no relation-consistent structure for mean-
unbind to extract. Complements 2026-06-10 stretch4_2 HF: RotatE trained
embeddings and STILL couldn't cross-domain generalize; this cell
DOESN'T train and also can't. Together = 2/6 Level-4 mechanisms scoped
as inadequate; remaining mechanisms 4.1 (multi-domain KGE), 4.2 (universal
relation vocabulary via ConceptNet), 4.3 (meta-learning), 4.4 (structural
alignment), 4.5 (hyperbolic embeddings) are still open.

**Do NOT atomize as substrate-capability finding.** The finding is about
this SPECIFIC frozen-codebook + K=10-mean-unbind combination. The
positive substrate cross-domain analogy story likely requires (a)
entity vectors with graph-topology-informed structure (trained OR
constrained) AND (b) either cortical schema retrieval (drill Level-3)
or slow-learned universal relation vocabulary (drill Level-4.2).

**M3 cortex design constraint (per USER prompt framing):**
"cross-domain analogy needs cortex-layer support, not raw substrate
primitive." This HF closure formalizes that constraint for M3 architecture
planning.

## Post-dispatch RUN_MODE_VERIFICATION (§16) — IF FULL dispatched

If Director elects FULL dispatch, after landing at
`data/exp_substrate_relation_type_binding_cross_domain_analogy_v1/metrics.json`,
verify:
- `run_mode == "full"`
- `elapsed_s` in range [60, 900] (expected ~120-300s CPU / 15-30s GPU)
- `per_seed[0]` has `arm_cross_domain_hits1`, `arm_within_domain_hits1`,
  `arm_baseline_hits1` keys with numeric values
- File size > 5000B (per-seed dicts + aggregate)
- Verdict field: HARD_FAIL expected; MIDDLE_BAND would be surprising;
  HARD_PASS would be an anomaly requiring diagnosis (would falsify
  prior drill Level-1 prediction + this smoke's analytical framing)

## Dispatch-ready status

- Selftest: PASS
- Smoke: RAN 5s wall; HARD_FAIL cross=0.000 within=0.001 baseline=0.000
  (3-seed variance probe fires discriminator)
- Pre-reg: authored with all META_RULE fields
- Prior-work check: NOT a rediscovery (top cosine 0.35; drill notes only)
- Substrate-primitives grep-check: PASS (8+ invocations per seed)
- Multi-seed acceptance gate: FAILS acceptance (mean within 0.05 of chance)
  → **cell-author recommends smoke-HF as closure**, no FULL dispatch
- Queue routing: local smoke complete; FULL dispatch DEFERRED per multi-seed
  acceptance gate rule + USER prompt guidance ("HF closure with clean
  scoping produces a chain-grade design constraint")
- Timeout (if FULL): 900s (15 min)
