# Pre-registration: schema_relation_TEM_scorer_scaleup_envelope_v2

**Filed:** 2026-07-05 by exp_dev (cell author).
**Cell:** `experiments/exp_schema_relation_TEM_scorer_scaleup_envelope_v2.py` (self-contained;
verbatim mechanism reuse of v1 + torch-GPU scorer backend + soft-TEM arm + config-grid sweep).
**Basis:** parent `schema_relation_TEM_structural_content_binding_v1` (commit d814a43bc, smoke =
MIDDLE_BAND, genuine-nonzero inductive real_minus_shuf where the exhausted averaged-transform
family was exactly zero). Drills: `notes/research_frontier_drill_inductive_relational_transfer_unseen_entities_2026-07-05.md`,
`notes/research_mechanism_envelope_frontier_inductive_transfer_off_zero_2026-07-05.md`.

## Scientific question
The base cell moved inductive (novel-subject) `real_minus_shuf` OFF ZERO (~0.05-0.13 on
AtLocation/CausesDesire, both mechanisms, both encoders) -- the first substrate cell to do so; it
was UNDER-PARAMETERIZED (V=100, M_OP=200, small df/steps, HARD-argmax TEM). **Does ANY (arm x
scale) config push inductive `real_minus_shuf` from ~0.1 toward/past useful magnitude (>= 0.2075),
and WHERE does the curve plateau?** MAP THE CURVE; do NOT force a pass. A curve that climbs with
M_OP but plateaus below 0.21 is itself the finding (per a53f8b: useful magnitude likely needs BOTH
more data AND richer jointly-trained content; there is a general one-to-many entropy ceiling).
Load-bearing metric: REAL - SHUFFLED on INDUCTIVE eval (raw accuracy is a relation-prior trap).
Constructive build; ZERO generative-LLM calls; NOT vs-LLM.

## Mechanism map (held from research a53f8b, verified off-disk)
- **GLOBAL** = TransE / population-marginal single additive relation vector -> MUST degenerate to
  the popular object on one-to-many relations -> shuffle-invariant. Reference baseline (NOT HP).
- **TEM_HARD** = hard K-means type-prototype + per-type transform + HARD nearest-proto argmax (the
  base cell's as-built arm; discretized low-rank RESCAL / Prototypical-Net-like). Carried for contrast.
- **TEM_SOFT** (NEW, brain-aligned upgrade): posterior-weighted prototype MIXTURE.
  `softmax(beta*cos)` over ALL K prototypes (beta -> inf recovers TEM_HARD); weighted mixture of
  per-type transforms; argmax cleanup. The cheapest brain-aligned fix for the "under-realized hard
  discretization" critique WITHOUT a full recurrent-TEM rebuild (no precedent, high cost).
- **SCORER** = trained bilinear content scorer = RESCAL/DistMult, O(d^2) capacity (vs TransE O(d));
  softmax-CE full-codebook negatives. PRIMARY per a53f8b (the RESCAL/content-conditioning move).

## Scale axes (PRIMARY = M_OP, per a53f8b: only 200 of ~9366(AtLoc)/~1423(CausesDesire) in-codebook
triples were used before -> real headroom)
- **M_OP ladder (PRIMARY)**: {200, 500, 800, 1500, 3000} at V=300, df=384, steps=2000. Capped by
  available in-codebook data per relation (M_eff recorded).
- **df-scan (SECONDARY, scorer capacity)**: {96, 192, 384, 768} at M_OP=800.
- **steps-scan (SECONDARY, scorer training)**: {300, 600, 2000, 6000} at M_OP=800.
- **V-scan (SECONDARY, vocab/coverage)**: {100, 300, 1000} at M_OP=800.
Discriminator-survives-scale: SMOKE runs at FULL N=8192; only seeds/test-size/M/steps/grid shrink.

## Relations (per a53f8b -- DROP CapableOf, structurally data-starved 18541 distinct obj / 22677
triples, near one-to-one, top-100 codebook covers 4.2% -> fails regardless of mechanism)
- **Semantic, HP-eligible (real headroom)**: AtLocation, CausesDesire.
- **Surface negative-baseline WATCHDOG (NOT HP-eligible; excluded from envelope/HP tally)**:
  DerivedFrom (watch shuffle-climbs-to-real = encoding artifact).

## Content encoding axis
- **bge_semantic**: BAAI/bge-small-en-v1.5 bounded cache -> centered unit feature + phasor.
- **gsbc**: program TARGET encoder (GSBC_EXPAND2X sparse 8192-d code). Cache-gated: absent ->
  per-unit GSBC_CACHE_MISSING; bge + mechanism axis stay valid. Both caches cover AtLocation/
  CausesDesire/DerivedFrom entities.

## Arms (PAIRED -- same triples/split/seed/clustering; only the manipulation differs)
REAL (true pairs; HP gates apply to mechanism arms) | SHUFFLED (object labels permuted within the M
train sample; for TEM, clustering on unchanged content, only per-type transform from shuffled pairs;
must stay ~chance) | MEAN_OBJECT (C-independent popular-object control). EVAL: inductive (novel-
subject, PRIMARY) + transductive (seen-subject, held-out object; gap reported).

## Pre-registered bands (LOCKED; identical thresholds to v1, applied over the config ENVELOPE)
`gain(arm)=arm_acc-1/V_eff`; primary = REAL, inductive; best-of {SCORER, TEM_HARD over K,
TEM_SOFT over K x beta} per semantic relation x encoding x config; ENVELOPE = max over the config grid.
- **HARD_PASS**: a TRUSTWORTHY mechanism family (its own synth discriminator fired) clears, on >=1
  semantic relation at SOME config, `real_minus_shuf(ind) >= 0.2075` AND `real_gain(ind) >= 0.2075`
  AND `real_minus_meanobj(ind) >= 0.05` -> useful-magnitude inductive transfer IS reachable by scale;
  headline family reported (TEM-family win = brain-aligned; SCORER-only win reported honestly).
- **HARD_FAIL**: envelope max `real_minus_shuf(ind) <= 0.05` across the WHOLE grid (M_OP ladder +
  df/steps/V scans) for ALL trustworthy families WHILE all synth discriminators fired -> scaling this
  content/mechanism does not extract subject-specific correspondence at novel entities (honest content/
  one-to-many wall).
- **MIDDLE_BAND**: `0.05 < envelope real_minus_shuf(ind) < 0.2075` from a trustworthy family (curve
  climbs then plateaus below useful magnitude -- the a53f8b-predicted honest outcome; the plateau IS
  the finding), OR a synth discriminator did not fire (uninterpretable).

**Per-family discriminator gating**: a family's real result is TRUSTWORTHY only if ITS OWN synth
discriminator fired (TEM_HARD/TEM_SOFT via SYNTH_TYPE_HARD adv >= 0.04; SCORER via SYNTH_CONTENT_MAP
adv >= 0.05). A marginal control on one family must NOT invalidate a robustly-firing other family.

## Repaired positive controls (Gate D; discriminator-fires proofs; MEASURED@smoke)
- `SYNTH_ROT_CLEAN`: GLOBAL recovers clean rotation ~1.0. MEASURED@smoke: 1.000.
- `SYNTH_TYPE_HARD` (TEM discriminator, hard AND soft): K_true=20 type-conditional rotations +
  type signature. GLOBAL below ceiling; TEM (hard/soft) must beat GLOBAL by >= 0.04.
  MEASURED@smoke(seeds 7,13): G=0.69, HARD=0.77 (adv +0.085/+0.083), SOFT=0.77 (adv +0.085/+0.083),
  fires=True for both. NOTE: the TEM edge is modest because FHRR preserves object identity
  multiplicatively through diagonal transforms (a real property; threshold set accordingly).
- `SYNTH_CONTENT_MAP` (SCORER discriminator): object = linear-map(subject content) + codebook nearest.
  GLOBAL ~chance; SCORER must beat GLOBAL by >= 0.05. MEASURED@smoke: G=0.04, SC=0.21 (adv +0.155/
  +0.170), fires=True.

## SCHEMA-VET mandatory fields
- `cardinality_ok`: EXPECTED_N_UNITS summed over the config grid (per config: rels x encs x
  (nslots x arms x eval) + [MEAN_OBJECT if mech=all]). Verdict emits CARDINALITY_BREACH if
  good_units < expected (gsbc-cache-missing tolerated). MEASURED@smoke: 288/288, 0 failed.
- `crlb_n/a`: argmax transfer has no closed-form CRLB noise floor. Chance = 1/V_eff; reachability:
  at largest V=1000, chance 0.001, HP target 0.2085 << 0.95 saturation. Declared THEORETICAL.
- `arms_differ_verified`: hash-test run on the NON-DEGENERATE synthetic DISCRIMINATING regimes
  (type-hard for GLOBAL/TEM_HARD/TEM_SOFT/MEAN_OBJECT; content-map for GLOBAL/SCORER_REAL/
  SCORER_SHUF) where arm implementations MUST differ by construction -- array-identity on the REAL
  relation is the WRONG AF regime because shuffle-invariant degeneracy (arms collapsing to the same
  popular-object prediction) is the FINDING, not a bit-identical-arm bug. MEASURED@smoke: True.
  `arms_differ_exempted`: within-TEM soft-vs-hard pairs (beta->inf recovers hard argmax).
- `final_metrics_atomicity`: tmp_replace (os.replace on metrics.json.tmp).
- `baseline_in_band`: SYNTH_TYPE_HARD GLOBAL in (0.05,0.95); controls (SHUFFLED) ~chance.
  MEASURED@smoke: GLOBAL_synth=0.69 in-band.
- `progress_logging`: print_flush_true (all progress lines flush=True; per (config,seed) timing +
  per-config real_minus_shuf line). timeout_s=7200 >= 1800 -> mandatory; satisfied.
- `defensive_error_checking`: start-marker + crash-diagnostic (Exception -> CELL_CRASHED metrics.json
  + traceback); except SystemExit: raise BEFORE except Exception (no BaseException / bare except --
  grep-verified clean).
- `cell_chunked`: false (single-cell 3-seed via _seed_checkpoint resumable partials; PROT-021
  run_config guard {N, run_mode, anchor} rejects smoke-partial contamination of the FULL path).
- `run_mode`: terminal tier = "full" literally; runner injects HDLAB_RUN_MODE=full -> RUN_MODE=full
  (no aliasing needed). --smoke / --self-test / name-_smoke -> RUN_MODE=smoke.

### §15 composition/sweep gates
- **Gate A (effective vs nominal)**: swept M_OP effective = min(M_OP, available in-codebook train
  pairs); M_eff recorded per (config,rel,enc,seed). K effective = min(K, n_train_subjects). At the
  swept scales all K << M -> ALIGNED. `sweep_alignment_verdict: ALIGNED`.
- **Gate B (discriminating band)**: discriminating metric = real_minus_shuf (not raw acc).
  MEASURED@smoke: envelope real_minus_shuf lands in (0.05, 0.2075) on AtLocation/CausesDesire x
  SCORER/TEM (S0_M200 best 0.108 -> S1_M500 best 0.200; the M_OP curve CLIMBS). >= 0.30 of grid
  points predicted in the discriminating band. `discriminating_fraction >= 0.30` satisfied.
- **Gate C (shape compatibility)**: content phasor -> bundle-centroid cluster (SHAPE_MATCH); cluster
  proto -> per-type transform (SHAPE_MATCH); novel content -> soft/hard proto classify (SHAPE_MATCH);
  transform mixture -> argmax cleanup (SHAPE_MATCH); content feature -> fixed projection -> bilinear
  (SHAPE_MATCH). No SHAPE_MISMATCH_no_adapter.
- **Gate D (positive control reproduce at test regime N=8192)**: SYNTH_ROT_CLEAN (GLOBAL>=0.90) +
  SYNTH_TYPE_HARD (TEM_hard AND TEM_soft > GLOBAL) + SYNTH_CONTENT_MAP (SCORER > GLOBAL) all at the
  test N=8192. PP-254 bundle-centroid clustering reproduced via kmeans_phasor selftest (purity>=0.85).
  Torch-scorer backend verified equal to numpy reference in self-test (final acc within 0.12).
- **Gate E (functional requirements)**: (1) classify novel entity by content -> PP-254 bundle-centroid
  (hard argmax OR soft softmax mixture). (2) reusable per-relation structure -> per-type transforms.
  (3) resolve specific object -> argmax cleanup / bilinear scorer. (4) trained component (satisfies
  PROVEN CONSTRAINT that untrained codebook scores 0.0) -> clustering + per-type transforms + scorer W
  all fit-from-data.

## Compute architecture
Class **(c) MIXED with justification**. SCORER (bilinear softmax-CE) on **torch, device auto ->
cuda on the GPU box**; REAL + SHUFFLED arms batched in ONE bmm pass (B=2; they share U/Vo/Ps/Po,
only y differs) -- the trivially-available GPU-batching win. At real M_OP + df + steps the scorer is a
genuine GPU-trainable matmul job (unlike the V=100 base smoke). Cross-relation batching is NOT done
(ragged V_eff/M_eff would need masking -- justified omission). The bilinear SGD inner loop is a
genuine sequential dependency (W_{t} depends on W_{t-1}) -> not batchable across steps (exempt per the
GPU-batching mandate). TEM_HARD/TEM_SOFT/GLOBAL/cleanup on **numpy-CPU** (cheap; clustering is the
brain-first CPU-cheap arm; a bit-reference). Falls back to numpy scorer if torch/cuda absent (same
analytic-gradient math; verified equal in self-test). Storage strategy: **no_storage** (in-memory
codebook algebra; no substrate write).

## Dispatch (GPU; idle overnight)
`overnight_queue` (GPU; cell `import torch` present -> passes the GPU gate; device auto->cuda).
Runner injects HDLAB_RUN_MODE=full; invokes BARE (no argv). **timeout: 7200s** (2h; MEASURED laptop
torch-CPU smoke ~33s/seed at reduced grid; the GPU-box scorer is fast, TEM numpy dominates; estimate
~15-30 min full wall; 7200 is generous margin, per-seed checkpoint-resumable). < 14400 cap.
**EXPLICIT SCP REQUIRED (gitignored caches + dataset are NOT auto-shipped by queue_add.sh; sibling-
cell import avoided by self-containment so no sibling SCP needed):**
- `data/datasets/bge_small_schema_TEM_entities_v1.npz`
- `data/datasets/gsbc_expand2x_schema_TEM_entities_v1.npz`
- `data/datasets/conceptnet5_en_100k.jsonl`
`_seed_checkpoint` auto-SCPs (Pattern 5 allow-list). If gsbc cache absent on remote, gsbc arm records
GSBC_CACHE_MISSING per-unit and bge + mechanism axis remain valid (cardinality gate tolerates).

## HYPOTHESIZED priors (calibration-penalized; per a53f8b)
- P(envelope reaches HARD_PASS real_minus_shuf >= 0.2075 on >=1 semantic relation) = 0.30
  HYPOTHESIZED@a53f8b (smoke already shows CausesDesire SCORER at 0.200 at M_OP=500/V=100 --
  encouraging but rmm-dependent and one-to-many-ceiling-limited).
- P(MIDDLE_BAND: climbs with M_OP then plateaus below 0.2075) = 0.45 HYPOTHESIZED@a53f8b (the single
  most likely honest outcome given ConceptNet's thin per-entity text + FB15k 1-to-N ceiling).
- P(HARD_FAIL: scale does not help, envelope <= 0.05) = 0.10 HYPOTHESIZED (smoke already refutes at
  smoke scale; low).
- P(TEM_SOFT closes the gap to SCORER on real data) = 0.25 HYPOTHESIZED (smoke: soft==hard on real
  ConceptNet, both below SCORER; soft's discriminator fires on synth so the mechanism is correct, but
  real ConceptNet type-structure appears weak).
- Smoke MEASURED: MIDDLE_BAND; envelope_best SCORER@S1_M500|CausesDesire rms=+0.200 gain=+0.198
  rmm=+0.192; M_OP curve climbs (S0_M200 0.108 -> S1_M500 0.200); all 3 discriminators fire.
