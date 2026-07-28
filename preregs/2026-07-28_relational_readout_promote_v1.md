# Pre-reg: relational_readout_promote_v1 (2026-07-28)

## Purpose

Promote `experiments/diag_readout_limit_probe_v1.py` -- a standalone, NOT-dispatched, single-shot
CPU diagnostic that measured (seed_7 only) a learned low-rank bilinear readout beating cosine-NN
by **+0.0666** on held-out-NEW relational AUC (95% paired-bootstrap CI **[0.0277, 0.1081]**,
excludes zero; corroborated on its own TRAIN-fit pairs) -- into a leak-proof, multi-seed,
arbitrary-ckpt **dispatched cell**: `experiments/exp_relational_readout_promote_v1.py`.

Two jobs:
1. **REPLICATE**: is the readout-limit lift a robust finding, or did the diagnostic's single
   arbitrary run (one ckpt, one DIAG_SEED) get lucky? (The standing seed-luck-over-read discipline
   caught exactly this class of over-read on the relObj/comprehension track earlier tonight --
   apply the same rigor here before trusting the finding.)
2. **FAIR-TEST HARNESS**: build the comparison so ANY future encoder ckpt (grounding / relObj /
   later objectives) can be re-measured under "learned-readout vs learned-readout" (not
   "learned-readout vs cosine"), answering: does a trained objective add DECODABLE relational
   structure BEYOND what a learned readout already extracts from the MLM-only baseline?

## Prior-work check (substrate-KB, USER-locked 2026-07-01)

`bash tools/substrate_query.sh "learned readout linear probe relational placement held-out concept
bilinear cosine decoder"` -- top hits: (1) `linear concept` cosine=0.3652 (generic WordNet-adjacent
node, not a prior cell); (2) `native_binding_compositional_generalization_v1` cert cosine=0.3281
(a DIFFERENT finding -- linear readout beats an entangled nonlinear-MLP readout on single-hop
concept-binding property-recovery; same *pattern class* "readout linearity matters" but different
mechanism/domain, corroborating rather than duplicating); (3) `bilinear` (WordNet dictionary entry,
irrelevant); (4) an ARCH-B nonlinear-readout-as-refuse-signal prereg (different application: refuse
gating, not relational placement). **Verdict: genuinely novel for THIS mechanism/domain
(relational-placement readout-limit); no rediscovery.** The two top hits corroborate a broader
"readout linearity is often the fix, not the representation" pattern recurring across this
substrate's cells -- worth noting as a cross-cell regularity, not a duplicate cell.

## Known gap (state honestly, do not paper over)

**No second MLM-v2 training-seed checkpoint exists on disk.** Confirmed via `find data
-iname "ckpt_seed_*.pt"`: `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` is the ONLY
MLM-baseline seed. (v3_relobj DOES have two training seeds: `ckpt_seed_7.pt` and `ckpt_seed_13.pt`
under `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/`.)

Consequence for "REPLICATE... across seeds": this cell substitutes the closest available multi-seed
check -- sweeping the diagnostic's own arbitrary **DIAG_SEED** (controls anchor sampling, negative
sampling, probe init, bootstrap resampling) across 3 independent values on the SAME ckpt_seed_7.
This tests replicability of the FITTING/EVAL PROCEDURE, not of encoder-training-seed variance. The
SECONDARY arm group (relobj_v3 seed_7 + seed_13) gives a genuine cross-**training**-seed check of
the MECHANISM (learned readout beats cosine), but on a different objective (relObj, not MLM) -- so
it corroborates portability, not the MLM-baseline finding's magnitude specifically.
**Recommendation for Director/GPU queue**: if strict same-objective cross-training-seed replication
is required later, train a second MLM-v2 seed (e.g. seed_13) -- currently not scheduled by this cell.

## Hypothesis

H1 (PRIMARY, gates verdict): on `ckpt_seed_7` (MLM-only v2 baseline), the learned-readout margin
over cosine-NN on held-out-NEW relational AUC replicates across a majority of 3 independent
DIAG_SEEDs, with validity controls (SHUFFLE_CONTROL, POPULARITY_CONTROL) landing near chance in
every unit.

H2 (SECONDARY, informational only, NOT gated): the SAME harness applied to `v3_relobj` seed_7 and
seed_13 measures whether that (already-known-negative-on-comprehension) objective shows MORE or
LESS learned-readout lift than the MLM baseline -- feeding the "does a trained objective add
decodable relational structure beyond a learned readout on MLM" question for Director's synthesis.

## Bands (envelope-fail-bands discipline)

**HARD_PASS_MARGIN = 0.03** (MEASURED@d:/AI/hd-instrument/data/diag_readout_limit_probe_v1/
results.json:margin_over_baseline = 0.0666 is the reference point; 0.03 is a conservative ~45% of
that, chosen so replication requires a REAL fraction of the original signal, not a rounding-error
crossing of zero). Band width [0.0, ~0.067] (measured ceiling) -> META_RULE_L 5%-width floor =
0.0033, comfortably below the 0.03 threshold (no floor-hugging risk).

- **HARD_PASS**: >=2/3 PRIMARY diag-seed units clear `margin_over_baseline >= 0.03` AND
  `bootstrap_ci.ci_excludes_zero == True` AND `train_corroborates == True` AND
  `validity_ok == True` for ALL 3 PRIMARY units (a validity breach on any PRIMARY unit
  auto-demotes to HARD_FAIL_VALIDITY_CONTROL_BREACH regardless of the other two units' margins --
  an invalid harness at any seed means we cannot trust that unit's reading, and cherry-picking the
  other two would be exactly the over-read this discipline exists to prevent).
- **MIDDLE_BAND**: exactly 1/3 PRIMARY units clears the bar (seed-luck cannot be ruled out; do NOT
  treat as replicated, per the standing 07-28 seed-luck lesson from the relObj/comprehension track).
- **HARD_FAIL**: 0/3 PRIMARY units clear the bar, OR any PRIMARY unit's validity controls
  (SHUFFLE_CONTROL / POPULARITY_CONTROL) fall outside [0.40, 0.60].
- **HARD_FAIL_CARDINALITY_BREACH_META_RULE_H**: fewer than 5 total units complete (3 PRIMARY + 2
  SECONDARY).

### HP_SCOPE (per-arm declaration, SCHEMA-VET item 5b)

```yaml
HP_SCOPE:
  PRIMARY (mlm_v2_seed7, 3 diag-seeds): [HARD_PASS, MIDDLE_BAND, HARD_FAIL, VALIDITY_BREACH]
  SECONDARY (relobj_v3 seed_7, seed_13): []   # informational only; does NOT gate the cell verdict
```

## Discriminator-fires gate (META_RULE_K / DISCRIMINATOR-MUST-SURVIVE-SCALE)

Chosen approach: **Option C (discriminator-preview arm) + Option B (analytical/measured
justification), combined.**
- Option B: the diagnostic ALREADY measured the discriminator firing at this EXACT FULL_CFG regime
  (byte-identical config, same ckpt, same DIAG_SEED=20260727) -- MEASURED@d:/AI/hd-instrument/data/
  diag_readout_limit_probe_v1/results.json: margin=0.0666, CI=[0.0277,0.1081], validity_ok=True,
  n_query=213.
- Option C: exp_dev additionally re-runs the NEW (refactored-into-shared-module) cell code on
  the SAME single unit (`mlm_v2_seed7__ds20260727`) at FULL_CFG via a debug-only env-var filter
  (`HDLAB_UNITS_OVERRIDE`, never set on the real dispatch) to confirm the refactor reproduces the
  diagnostic's number within tolerance BEFORE trusting the multi-unit FULL dispatch (this is also
  Gate D below). Reported inline in the exp_dev completion report as MEASURED (this session), not
  hypothesized.
- **Reject full dispatch if the preview unit's margin is not within tolerance of the diagnostic's
  measured number** (see Gate D tolerance below) -- a refactor bug would show up here, not 30 min
  into the real remote FULL run.

### Gate D: positive-control reproduction (SCHEMA-VET item §15.D)

```yaml
positive_control_arms:
  - arm: MLM_V2_SEED7_DS20260727_REPRODUCE
    primitive: learned_bilinear_readout_vs_cosine_NN
    cited_prior_atom: d:/AI/hd-instrument/data/diag_readout_limit_probe_v1/results.json
    cited_prior_metric: margin_over_baseline=0.0666 (bilinear), validity_ok=True, n_query=213
    cited_prior_regime: {ckpt: ckpt_seed_7.pt (mlm_v2), diag_seed: 20260727, cfg: DIAG_CFG (byte-identical to this cell's FULL_CFG)}
    test_regime: {ckpt: SAME, diag_seed: SAME, cfg: SAME (this IS the same computation, refactored into experiments/_learned_relational_readout.py)}
    tolerance: 0.02   # tight -- deterministic pipeline, same seeds, only the code path changed
    if_outside_tolerance: HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH (refactor bug; do not trust downstream units)
    regime_extension_audit: SHAPE_MATCH (identical config; no regime change)
```

## Compute architecture

- **Class: (b) sequential-CPU with justification.** Per-unit compute (probe fit: 500 Adam steps
  over ~4-16k pairs at d=512; eval: AUC over ~200-400 queries x ~16 candidates) is light matmul on
  small tensors -- CPU wall per unit ~90-150s (fit+eval only, once the ckpt-independent shared
  bundle and per-ckpt encode are cached). Batching to GPU is not warranted: this is a CPU-lightweight
  post-hoc readout comparison over ALREADY-frozen reps, explicitly designed (per USER "no local
  smokes, route all execution to remote" + "do lightweight measurements inline") to run IN PARALLEL
  with the GPU grounding run, not contend for GPU. Historical evidence: the diagnostic itself
  completed the FULL regime in 538s wall on CPU (MEASURED@results.json:elapsed_s_total).
- **Efficiency lever exploited**: `load_concept_universe` / `count_pass` / `build_split` /
  `collect_pass` / `load_adjacency` / `build_grounding_reps` are ALL ckpt-independent (verified by
  reading their signatures -- they take `cfg`/`universe`/`split`, never a model or tokenizer).
  Computed ONCE per FULL run (`build_shared_bundle`), shared across all 3 ckpts. Only
  `encode_concept_text_reps` (needs the frozen model+tokenizer) is re-run per distinct ckpt path (3
  times: mlm_v2_seed7, relobj_v3_seed7, relobj_v3_seed13); `build_train_pairs` + probe-fit + eval are
  re-run per (ckpt, diag_seed) unit (5 times total).
- **Storage strategy: no_storage / no_composition.** This is a single-hop readout-comparison eval,
  not a chained-retrieval or multi-hop composition cell; the sharded-vs-bundled storage-strategy
  gate does not apply.

## Wall-time estimate (exp_dev's own, for `--timeout`)

- Shared bundle (universe+count_pass+split+collect_pass+adjacency+grounding): ~180s (MEASURED@
  diag results.json t_stage: universe 2.2s + count_pass 78.0s + split 0.03s + collect_pass 91.0s +
  adjacency 8.6s = ~180s, ckpt-independent, computed once).
- Per-ckpt encode (3 distinct ckpts: mlm_v2_seed7, relobj_v3_seed7, relobj_v3_seed13):
  ~265s each (MEASURED@diag results.json t_stage.encode_s=264.7s) x 3 = ~795s.
- Per-unit fit+eval (5 units: 3 PRIMARY on mlm_v2_seed7 sharing its encode, 2 SECONDARY each on
  their own ckpt's encode): ~90-150s each (MEASURED@diag results.json probe_fit: diag_fit_s=40.3 +
  bilinear_fit_s=49.2 + eval (not separately timed, small) ~ 90-100s) x 5 = ~500-750s.
- **Total estimate: ~180 + 795 + 625 = ~1600s (~27 min).** `--timeout` set with margin:
  **timeout_s = 3600** (60 min; ~2.25x the estimate, covers remote-box variance / cold model-load /
  disk I/O on first corpus scan).

## progress_logging (SS17, MANDATORY -- timeout_s=3600 >= 1800)

`progress_logging: "print_flush_true"`. Every `_log()` call uses `print(..., flush=True)`.
Per-unit + per-stage log lines are emitted at each major boundary (universe/count_pass/split/
collect_pass/adjacency/encode/unit-done), plus `CellHeartbeat` (interval_s=30, `force=True` at every
stage/unit boundary) writing `_heartbeat.jsonl` for Testbed/Director hang-audit.
`progress_cadence_expected_s: 30`.

## SCHEMA-VET checklist (all fields required, see canonical exp_dev.md SS143-17)

```yaml
cell_chunked: true            # one unit = one "seed" key in experiments._seed_checkpoint
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: "passed_all_4_patterns"
final_metrics_atomicity: "per_iter_paths"   # write_partial per unit (own file) + write_metrics tmp+replace at the end
arms_differ_verified: true      # arms_must_differ_hashes() per unit, over per-query score vectors
arms_differ_exempted: []
crlb_n_a: "AUC discriminator over a held-out relational nearest-neighbor task, not a capacity/noise
  regime -- no closed-form CRLB floor applies. Reachability bound is instead the trivial AUC range
  [0.5 chance, 1.0 ceiling]; HARD_PASS_MARGIN=0.03 sits far inside that range and well below the
  MEASURED ceiling headroom (baseline ~0.56-0.64, probe ~0.63-0.65), so reachability is not a concern."
baseline_in_band: true          # BASELINE_COSINE MEASURED at 0.564-0.638 (diag results.json), well inside (0.05, 0.95)
calibration_check: "default_ok_for_this_regime"   # byte-identical cfg to the already-validated diagnostic regime
cardinality_ok: true            # EXPECTED_N_UNITS=5 gate enforced in build_verdict()
deterministic_seeding: true     # all RNG via np.random.default_rng(fixed_int) / torch.manual_seed(fixed_int); sorted() for set-derived ordering; no hash()-seeded RNG (PROT-023 / F.5)
real_code_path_exercised: [load_concept_universe, count_pass, build_split, collect_pass,
  load_adjacency, build_grounding_reps, load_frozen_encoder, encode_concept_text_reps,
  build_train_pairs, fit_diag_probe, fit_bilinear_probe, eval_relational_all_arms]
  # self-test exercises ALL of these at tiny-but-real scale (cap_eval_concepts=1200, max_lines=100000)
substrate_signature_checked: []   # no KGStore-style object with drift-prone optional kwargs in this
  # cell's dependency surface; the frozen-encoder loader binds directly against ckpt["model_cfg"]
  # keys (vocab/max_len/d_model/n_layers/n_heads/ffn_mult/pad_id), which are written by the SAME
  # v2 training script that saved the ckpt -- no local/remote signature drift surface here.
guard_baseline_validated: []     # no control-beats-baseline break-guard in this cell (validity gate
  # is a symmetric band-check [0.40,0.60] on SHUFFLE/POPULARITY controls, not a control-vs-baseline
  # break-guard subject to the POP-at-floor mis-fire class)
```

### Functional requirements (SCHEMA-VET item E)

```yaml
functional_requirements:
  - requirement: "distinguish readout-limit from representation-limit on relational placement"
    primitive: "learned linear probes (diagonal-reweighted cosine + low-rank bilinear projection),
      fit TRAIN-TRAIN only, compared to cosine-NN baseline on the SAME held-out-NEW candidate sets"
  - requirement: "leak-proofness (held-out concepts never touch the fit)"
    primitive: "build_train_pairs asserts fit-pair endpoints subset of train_eval_idx and disjoint
      from held_idx; _scrub_variants removes held-out surface mentions from all training postings
      (inherited from exp_scale_meaning_learn_arc_heldout_v2.collect_pass)"
  - requirement: "seed-robustness (does the lift replicate, not just a lucky draw)"
    primitive: "DIAG_SEED sweep (3 independent values) on the SAME ckpt + cross-training-seed check
      on v3_relobj (seed_7, seed_13) as the closest available genuine training-seed variation"
  - requirement: "reusable fair-test harness for future ckpts"
    primitive: "--ckpt-path is not hardcoded per-unit; build_units() + encode_for_ckpt() accept any
      ckpt path with the same model_cfg-driven loader (load_frozen_encoder); shared probe-fit/eval
      code lives in experiments/_learned_relational_readout.py, importable by other cells/eval
      batteries (e.g. eval_battery_relational_cloze_v7.py, flagged as a WIRE-consolidation candidate)"
```

### Composition edges (SCHEMA-VET item C)

```yaml
composition_edges:
  - from: load_frozen_encoder (ckpt["model_cfg"])
    to: encode_concept_text_reps (TinyTransformer forward)
    A_natural_output_shape: "d_model from ckpt (512 for all 3 target ckpts, read at runtime not hardcoded)"
    B_natural_input_shape: "TinyTransformer constructed with mc['d_model'] from the SAME ckpt dict"
    verdict: SHAPE_MATCH
  - from: encode_concept_text_reps (text_reps [K, d_model])
    to: fit_bilinear_probe / fit_diag_probe (Linear(d_model, r) / diag weight [d_model])
    A_natural_output_shape: "[K, d_model], d_model read from text_reps.shape[1] at runtime"
    B_natural_input_shape: "probe params sized from text_reps.shape[1] at runtime (no hardcoded 512)"
    verdict: SHAPE_MATCH
discriminating_fraction: 1.0   # MEASURED@diag results.json: margin=0.0666 sits inside the
  # discriminating band (not saturated at ceiling ~1.0, not floor ~0.0); all 5 units use the SAME
  # regime (byte-identical FULL_CFG), so 5/5 expected in-band per the already-measured evidence.
sweep_alignment_verdict: ALIGNED   # DIAG_SEED and ckpt_path are both EFFECTIVE parameters the
  # readout-fit/eval pipeline directly experiences (no upstream routing/partitioning dilutes them)
```

## Wire target (capability-integration gate, USER-locked 2026-07-25/28)

If this cell lands HARD_PASS (or HARD_PASS_MAJORITY): file a `data/capability_registry.jsonl` row
for the learned-relational-readout mechanism (`experiments/_learned_relational_readout.py`) with a
WIRE decision. Intended wire targets (to be confirmed at land-time by whoever owns registry
integration, per "WIRE DON'T ISLAND"):
  1. `experiments/eval_battery_relational_cloze_v7.py` -- ALREADY imports `load_frozen_encoder` from
     `diag_readout_limit_probe_v1` and independently re-implements a similar bilinear-fit inline per
     its own docstring/comments ("a learned leak-proof decoder (fit train-only)... matching tonight's
     diag_readout_limit_probe_v1 finding"); consolidating onto the shared module is the natural WIRE
     step (not done in this pass, to keep this cell's diff bounded to the promotion task).
  2. The main reasoning loop's relational nearest-neighbor readout (wherever the substrate currently
     does cosine-NN over concept reps for relational retrieval) -- exact call site to be identified
     by Skunkworks/Director at WIRE time; this cell's job is to VET the mechanism, not to locate
     every call site.

## Dispatch

- **Queue: `remote_cpu_queue`** (CPU-only, no torch.cuda touched, explicitly designed to run in
  parallel with the GPU grounding run per the task contract -- verified: `torch.cuda.is_available()`
  never referenced as a device selector in this cell; `device="cpu"` hardcoded in encode calls).
- **Anchor name**: `relational_readout_promote_v1`.
- **Script**: `experiments/exp_relational_readout_promote_v1.py`.
- **Timeout**: 3600s (see wall-time estimate above).
- Remote data dependencies verified present on marsh@home (`C:/dev/hd-instrument`) BEFORE dispatch:
  `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt`,
  `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_{7,13}.pt`,
  `data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt` -- all `Test-Path` TRUE (checked via ssh,
  2026-07-28, this session).
