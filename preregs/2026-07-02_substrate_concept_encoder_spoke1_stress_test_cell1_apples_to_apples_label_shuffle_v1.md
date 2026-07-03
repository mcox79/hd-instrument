# Pre-reg: Stage 2 Spoke 1 stress-test Cell 1 — apples-to-apples supervised baseline (Test 2) + label-semantics shuffle ablation (Test 4) COMBINED

- **Filed:** 2026-07-02
- **Anchor:** `substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1`
- **Cell:** `experiments/exp_substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1.py`
- **Depends on:** `hdlab.concept_encoder.ConceptEncoder` (extracted 2026-07-02 from Spoke 1 v3-D FULL, commit e8f15a036) + `hdlab.char_trigram_encoder.CharTrigramEncoder` + `hdlab.char_positional_encoder.CharPositionalEncoder` + sklearn 1.9.0 (CountVectorizer, LogisticRegression, KMeans, adjusted_mutual_info_score)
- **Design ref:** `notes/research_spoke1_stress_test_suite_design_2026-07-02.md`

## Strategic context (USER-CRITICAL, LOAD-BEARING)

USER 2026-07-02 late evening challenge: *"stress test spoke 1. how does substrate know what a cat or airplane are? are we sure we tested apples to apples?"*

Skunkworks self-demoted META `drill_convergence_method` CG_META → MM_TENTATIVE per USER's honest scope challenge. Spoke 1 v3-D CG scope tightened to "supervised synthetic concept-label regime with designer-imposed clusters" (see `hdlab/concept_encoder.py` module docstring VALIDATION SCOPE + STAGE 4 CAVEATS).

**This cell is the load-bearing apples-to-apples validity test.**
- **HP2 pass** = Spoke 1 has a real substrate story beyond a trivial supervised classifier.
- **HF2 fire** = arc pauses honestly and mechanism reframes.

**Framing discipline (LOAD-BEARING per `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`):** cell tests SUPERVISED regime; result informs mechanism scope claim, NOT deep concept-understanding claim. No overclaims of "brain-analog concept understanding".

## Prior-work check (substrate-KB concept-query — inherited from design note, section 1)

Design note ran three substrate-KB v2 queries (`unsupervised concept discovery clustering AMI`, `supervised classifier baseline apples to apples`, `concept invariance transfer template ablation`). Verdict: apples-to-apples-vs-supervised-classifier for a concept-encoder is NOVEL to the substrate. First application of the `Apples-to-apples` discipline (established 2026-06-24 hub-spoke E1 Lane 1) against a supervised-classifier baseline. See design note section 1 for the full query dump.

## Functional requirements

Per USER framing challenge (mechanism-analog-vs-task-analog rule):

1. **Reproduce Spoke 1 v3-D at same regime** — Gate D positive control. Uses `hdlab.concept_encoder.ConceptEncoder` (the extracted primitive) with same N / SPC / seeds / mask_target_word=True. Must reproduce v3-D FULL cat_kitten_cos_mean = 0.492 within tolerance.
2. **Head-to-head against trivial supervised classifier** — bag-of-char-trigram + sklearn LogisticRegression softmax baseline. If softmax matches / beats v3-D on cat_kitten_cos, mechanism has not earned complexity.
3. **Label-semantics ablation** — same v3-D mechanism with shuffled labels. If shuffled arm produces similar cat_kitten_cos to unshuffled, mechanism is structural (arbitrary label routing), not semantic.
4. **Chance control** — random bipolar HDs; verifies scoring rig at chance.
5. **Unsupervised bonus** — CharPositionalEncoder + KMeans k=50; AMI vs true concept labels; REPORT-ONLY (informs Spoke 3 unsupervised design if AMI > 0.30).

All 5 functional requirements are addressed by 5 corresponding arms (below).

## Arms (5 arms × 3 seeds = 15 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_SPOKE1_V3D_REPRO | `hdlab.concept_encoder.ConceptEncoder` fit on true labels, mask_target_word=True | Positive-control Gate D reproducer |
| ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE | sklearn LogisticRegression on CountVectorizer char-trigram counts + per-concept centroid HD via `hdlab.char_trigram_encoder.CharTrigramEncoder` | **LOAD-BEARING Test 2** |
| ARM_SPOKE1_LABEL_SHUFFLED | Same v3-D mechanism, labels shuffled uniformly at random before fit, mask_target_word=False (avoid cross-arm masking-vs-label confound) | **LOAD-BEARING Test 4** |
| ARM_RANDOM_BASELINE | Random bipolar HD per concept; no learning | Chance control |
| ARM_UNSUPERVISED_KMEANS | CharPositionalEncoder → KMeans k=50 → AMI vs true labels | REPORT-ONLY bonus |

## Configuration

- **Smoke:** N_DIM=2048, seeds=[11, 17, 23], SENTENCES_PER_CONCEPT=40 → 2000 sentences/seed × 15 units. Timeout 1200s (20 min).
- **Full:** N_DIM=4096, seeds=[11, 17, 23], SENTENCES_PER_CONCEPT=40 → 2000 sentences/seed × 15 units. Timeout 1800s (30 min).
- **Selftest:** import + tiny corpus at N=256 (2 sent/concept) + scale-sentinel probe at N=8192 on ARM_SPOKE1_V3D_REPRO for NaN detection at production-scale matmul.
- **Corpus:** 25-cluster × 2-concept synthetic templated corpus (verbatim from v3-D for direct comparability).

## HP bands

| ID | Applies to | Metric | Threshold | Rationale |
|---|---|---|---|---|
| HP1 | ARM_SPOKE1_V3D_REPRO | cat_kitten_cos_mean vs v3-D FULL 0.492 | \|Δ\| ≤ 0.05 at FULL, ≤ 0.10 at smoke | Gate D positive-control reproducer at same regime as v3-D FULL (MEASURED@data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02/metrics.json:arm_summary.ARM_COMPETITIVE_HEBBIAN.cat_kitten_cos_mean) |
| HP2 | ARM_SPOKE1_V3D_REPRO − ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE | cat_kitten_cos_mean | delta ≥ +0.05 | **LOAD-BEARING**: v3-D beats trivial supervised classifier by ≥ 0.05 cosine (apples-to-apples earned complexity) |
| HP3 | ARM_SPOKE1_V3D_REPRO − ARM_SPOKE1_LABEL_SHUFFLED | cat_kitten_cos_mean | delta ≥ +0.30 | **LOAD-BEARING**: shuffled labels collapse discrimination → mechanism uses labels meaningfully |
| HP4 | ARM_RANDOM_BASELINE | \|cat_kitten_cos_mean\| | ≤ 0.05 | Chance control (scoring rig sanity) |
| HP5 | ARM_UNSUPERVISED_KMEANS | ami_score_mean | ≥ 0.30 | **REPORT-ONLY** (not gating) — informs Spoke 3 unsupervised design |

## HF bands

| ID | Applies to | Metric | Threshold | Consequence |
|---|---|---|---|---|
| HF1 | ARM_SPOKE1_V3D_REPRO | \|cat_kitten_cos_mean − 0.492\| | > 0.10 | **INVOCATION_MISMATCH halt** — Gate D fails; downstream arms suspect until reproduction resolved |
| HF2 | ARM_SPOKE1_V3D_REPRO − ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE | cat_kitten_cos_mean delta | < −0.05 | v3-D LOSES to trivial classifier; mechanism has no advantage; **major arc-reframe required** |
| HF3 | ARM_SPOKE1_LABEL_SHUFFLED | cat_kitten_cos_mean AND HP3 not met | > 0.30 AND HP3 delta < 0.30 | Mechanism clusters arbitrary labels; deep concept structure NOT being learned |

## MIDDLE_BAND (partial signals)

- HP2 delta ∈ (0.00, 0.05) — v3-D marginally beats softmax; scope-tighten arc.
- HP3 delta ∈ (0.10, 0.30) — labels partially matter; scope-tighten arc.

## HP_SCOPE

**LOAD_BEARING on HP2 (softmax) + HP3 (label-shuffled).** These two are the critical apples-to-apples + label-semantics tests USER's challenge directly probes. HP1 is Gate D reproducibility sanity; HP4 is chance sanity; HP5 is REPORT-ONLY diagnostic.

Per-arm HP_SCOPE mapping (in cell `cell_template_compliance.hp_scope`):
- ARM_SPOKE1_V3D_REPRO: [HP1]
- ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE: [HP2]
- ARM_SPOKE1_LABEL_SHUFFLED: [HP3]
- ARM_RANDOM_BASELINE: [HP4]
- ARM_UNSUPERVISED_KMEANS: [HP5 report-only]

## Cardinality

`cardinality_ok`: EXPECTED_N_UNITS = 5 arms × 3 seeds = 15.

## SCHEMA-VET gates (per exp_dev.md §15)

- **Gate A (effective-vs-nominal parameter):** No sweep axis; N/A. `sweep_alignment_verdict: N/A_no_sweep_axis`.
- **Gate B (bracket includes discriminating band):** No sweep axis; the discriminator is a delta between arms at a single regime. `discriminating_fraction: N/A_no_sweep_axis`.
- **Gate C (signal-shape compatibility):** All arms produce N_CONCEPTS × N_DIM float32 arrays; cat_kitten_cos computed identically per arm. `composition_edges: SHAPE_MATCH` (uniform per-arm concept-HD shape).
- **Gate D (reproduce prior chain-grade result at test regime):** ARM_SPOKE1_V3D_REPRO uses `hdlab.concept_encoder.ConceptEncoder` (extracted from Spoke 1 v3-D FULL commit e8f15a036) at same regime (N_DIM_FULL=4096, seeds 11/17/23, SPC=40, mask_target_word=True). Cited prior atom: v3-D FULL cat_kitten_cos_mean=0.492 MEASURED@data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02/metrics.json:arm_summary.ARM_COMPETITIVE_HEBBIAN.cat_kitten_cos_mean. Tolerance: 0.05 at FULL, 0.10 at smoke. If outside tolerance → HF1 INVOCATION_MISMATCH halt. `regime_extension_audit: SHAPE_MATCH` (same corpus + same mechanism; only mode differences are smoke N=2048 vs full N=4096).
- **Gate E (functional-requirement decomposition):** 5 functional requirements listed above; each mapped to a corresponding arm. `functional_requirements: [reproduce_v3d, apples_to_apples_supervised, label_shuffle_ablation, chance_control, unsupervised_diagnostic]`.

## CELL-TEMPLATE compliance

- arms_differ_verified: True (META_RULE_AF; ARMS-MUST-DIFFER hash check at smoke gate + selftest)
- final_metrics_atomicity: `tmp_replace` (META_RULE_AH; write to `metrics.json.tmp` then `os.replace`)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- cardinality_ok: True (EXPECTED_N_UNITS = 15 gated in verdict logic)
- baseline_in_band: RANDOM ~0 (chance); ARM_SPOKE1_V3D_REPRO target 0.4-0.6 (comfortably in band 0.05 < x < 0.95)
- calibration_check: `default_ok_for_this_regime` (synthetic corpus; no tuning; k_sparsity 0.02 inherited from v3-D CG regime)
- crlb_n/a: supervised concept-encoder cell; discriminator is cosine delta between arms, not a noise-floor CRLB regime
- discriminator survives scale: ARM_SPOKE1_V3D_REPRO uses same mechanism as v3-D FULL CG at N=4096; smoke at N=2048 is representative (v3-D smoke at N=2048 also CG'd)
- scale_sentinel_probe: selftest runs ARM_SPOKE1_V3D_REPRO at N=8192 asserting n_nan==0
- progress_logging: `line_buffered_stdout` (sys.stdout.reconfigure at main() entry) + explicit `flush=True` on progress prints; cell wall < 15 min so `timeout_s < 1800` — progress_logging field not mandatory per §17 but adopted for observability parity with v3-D
- crash_diagnostic_present: True (`_write_crash_metrics` writes CELL_CRASHED metrics + traceback via tmp+replace)
- start_marker_written: True (`_start_marker.json` at main() entry)
- cell_chunked: False (single-seed-per-cell not required; total wall < 15 min, low runner-zombie risk)
- heartbeat_present: False (cell wall < 15 min; per-seed progress prints suffice)
- defensive_error_checking: "passed_all_4_patterns" (start marker + crash diagnostic + arms-must-differ + scale-sentinel; heartbeat exempted for short cell)

## Environment variable contract

- `HDLAB_RUN_MODE`: production runner injects `full`; argparser reads via `os.environ.get("HDLAB_RUN_MODE", "smoke")` default. Verified by `_run_selftest` env_contract inline check.
- `HDLAB_EXP_NAME`, `HDLAB_QUEUE`: informational; not consumed.

## Compute architecture (MANDATORY per USER-locked GPU-batching rule 2026-07-02)

- **Class (b) sequential-CPU + sklearn CPU with justification.** Per-arm wall estimates:
  - ARM_SPOKE1_V3D_REPRO: ~30-60s per seed at N=2048 (v3-D smoke MEASURED)
  - ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE: ~10-20s per seed (sklearn LogisticRegression on ~2000 sentences × ~5000 trigram features)
  - ARM_SPOKE1_LABEL_SHUFFLED: ~30-60s per seed (same mechanism as v3-D repro)
  - ARM_RANDOM_BASELINE: <1s per seed (trivial)
  - ARM_UNSUPERVISED_KMEANS: ~30-60s per seed (KMeans k=50 on 2000×2048 HDs, n_init=10)
  - **Total smoke wall estimate: ~5-10 min for 15 units at N=2048.**
- **Justification for sequential-CPU (per §15 GPU-batching rule):**
  - `ConceptEncoder.fit` is a per-sentence sequential Hebbian outer-product accumulator (bit-identical CPU reference; the substrate primitive under test is CPU-numpy at the extraction commit).
  - sklearn LogisticRegression + KMeans are CPU-native primitives; GPU-porting is out of scope for a stress-test cell.
  - Per-seed wall < 10 min; total wall < 15 min. Well under the batching-mandate threshold.
- **Storage strategy:** SHARDED (per-concept HD; not bundled) per storage-strategy law `T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1`.

## Dispatch plan

1. **Selftest** — `.venv` python, `--self-test` mode (import + tiny + scale-sentinel N=8192).
2. **Local smoke** — `local_cpu_queue` per SMOKE-only-on-local-cpu USER lock 2026-07-01. Timeout 1200s.
3. **HOLD before FULL** — Director + USER review smoke verdict per arm before authorizing FULL. Full is dispatched only on USER approval per honest arc-pause protocol.
4. **FULL (post-approval)** — `remote_cpu_queue` (needs git push by Orchestrator; no cell-author push authority). Timeout 1800s.

## Expected outcomes (HYPOTHESIZED@this pre-reg)

Per design note section 5 + spawn prompt honest-expectations:
- ARM_SPOKE1_V3D_REPRO cat_kitten_cos ≈ 0.49 (should reproduce Gate D at N=4096; may be lower at N=2048 smoke since v2 measured 0.47 at that regime)
- ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE cat_kitten_cos: UNKNOWN — this is the load-bearing test. Templated corpus with heavy char-trigram surface signal likely gives softmax high accuracy; whether centroid HD matches v3-D on this specific metric is the empirical question.
- ARM_SPOKE1_LABEL_SHUFFLED cat_kitten_cos: probably collapses toward ~0.1-0.2 (all shuffled W[c'] average random sentences → similar centroids → moderate uniform similarity)
- ARM_RANDOM_BASELINE cat_kitten_cos ≈ 0 (chance)
- ARM_UNSUPERVISED_KMEANS AMI: probably weak (0.05-0.20 range) — mechanism relies on supervision

## References

- Design note: `notes/research_spoke1_stress_test_suite_design_2026-07-02.md`
- v3-D pre-reg: `preregs/2026-07-02_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only.md`
- v3-D cell: `experiments/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026-07-02.py` (commit e8f15a036)
- v3-D metrics: `data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02/metrics.json` (arm_summary.ARM_COMPETITIVE_HEBBIAN.cat_kitten_cos_mean = 0.492)
- Framing rule: `~/.claude/projects/d--AI/memory/feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`
- ConceptEncoder module: `hdlab/concept_encoder.py` (extracted 2026-07-02)
- Prior apples-to-apples discipline: `preregs/2026-06-24_substrate_hub_spoke_E1_v2_diverse_algorithm.md` (Lane 1 rho guard)

## Honesty caveats

- If HF2 fires (softmax matches v3-D on cat_kitten_cos), the Spoke 1 arc pauses regardless of HP3 outcome. USER + Director determine reframe direction (sparsity+composition vs raw discrimination framing).
- ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE's concept HD is a per-concept centroid over CharTrigramEncoder outputs — a supervised bag-of-trigrams baseline. It is NOT the softmax classifier's logit vector projected back into N_DIM space; the two are commensurable proxies for the "trivial supervised classifier" alternative but the centroid approach is the head-to-head-comparable one for cat_kitten_cos. Classifier test accuracy is reported separately as sanity.
- ARM_UNSUPERVISED_KMEANS is REPORT-ONLY. AMI < 0.30 is expected and does NOT block cell HARD_PASS. Purpose is diagnostic input for Spoke 3 unsupervised design (per design note section 3, Test 1).
- Label-shuffle arm uses `mask_target_word=False` (v3-D repro uses True). Rationale: masking with a random-permuted label word would introduce cross-arm asymmetric bias in the surface HDs. To isolate the label-semantics variable EXCLUSIVELY, we hold masking constant (off) in the shuffle arm. Note this means the shuffle arm's surface HDs include the concept-name character sequence, but that only strengthens the ablation: if even with the concept-name character signal present the shuffled labels cannot recover cat_kitten discrimination, the label-semantics dependence is confirmed.
