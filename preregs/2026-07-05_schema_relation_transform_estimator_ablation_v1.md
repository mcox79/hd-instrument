# Pre-registration: schema_relation_transform_estimator_ablation_v1

**Filed:** 2026-07-05 by exp_dev (cell author)
**Anchor:** `schema_relation_transform_estimator_ablation_v1`
**Cell:** `experiments/exp_schema_relation_transform_estimator_ablation_v1.py`
**Queue:** remote_cpu_queue (CPU, numpy, N=8192; FULL is canonical). Smoke local only.
**Basis:** 2x-drill note `notes/research_2x_drill_what_encoding_carries_relational_structure_for_schema_transfer_2026-07-05.md`
(spec'd cell + HP/HF bands + inductive-vs-transductive risk) + PP-275 `lap3_rotate_analogy_cpu_v1`
(TRAINED RotatE transform HARD_PASS Hits@1=0.899, the existence proof) + parent negative
`schema_bundle_real_corpus_transfer_v1` (HARD_FAIL under naive-mean estimator).

**Prior-work check (substrate-KB concept-query, USER-locked):** ran
`bash tools/substrate_query.sh "trained relation transform estimator RotatE rotation negative
sampling inductive schema transfer novel entity"`. Top hits at cosine 0.36 are surface-token
collisions ('transformation' WordNet; GO 'negative regulation of ... transport') -- NONE is a
prior HDI cell on trained relation transforms (cosine<0.37, all off-topic). The genuinely
relevant prior work is internal and already cross-referenced by the 2x-drill: PP-275 (trained
RotatE, transductive) and the parent negative (naive-mean, inductive). **This cell is a genuine
novel follow-up**, not a rediscovery: it crosses the ESTIMATOR fix (PP-275's lever) with the
ENCODING fix (the VET revival criterion) and adds the make-or-break INDUCTIVE-vs-TRANSDUCTIVE
separation that neither prior cell isolated.

## Question

Does REAL-corpus schema transfer work when the relation transform is TRAINED (RotatE-style
rotation with full-codebook negative sampling) instead of naive-averaged -- and does it hold
INDUCTIVELY (novel subject never seen), not just transductively? Two independent witnesses
converge: the drill's lit-scan (naive averaging is documented-weak for one-to-many relations
regardless of encoding) and PP-275 (a trained transform works on this exact substrate/algebra).
Constructive build; ZERO generative-LLM calls (BGE is a fixed local sentence encoder used only
to SOURCE semantic content for the encoding arm; all downstream is FHRR vector algebra).

## The 2x2 (crossed factorial + parent controls)

| Axis | Levels |
|---|---|
| ESTIMATOR | `NAIVE_MEAN` (failed baseline, M_R = mean_i bind(O_i, conj(A_i))) vs `TRAINED` (per-relation rotation r=exp(i*theta); warm-start at naive-mean phase, then softmax cross-entropy over the FULL V-object codebook = negative sampling; analytic-gradient descent) |
| ENCODING | `char_trigram` (surface phasor; parent ARM_REAL) vs `bge_semantic` (bounded BGE-small-en-v1.5 cache of ONLY the ~8756 test-relation entities, centered + fixed-projected to a unit FHRR phasor) |
| EVAL_MODE | `inductive` (test subjects DISJOINT from training -- the schema ask) vs `transductive` (test subjects seen in training via OTHER codebook pairs; one held-out object each) |

Entity encoder is FIXED (deterministic per string) -> a NOVEL subject still HAS an encoding ->
the design is natively INDUCTIVE-capable; only the relation transform is trained. This is the
key departure from PP-275 (which trains per-entity embeddings -> favors transductive).

## Relations (AtLocation flagship + 2 controls)

- `AtLocation` -- one-to-many, PURE SEMANTIC; the cleanest discriminator (surface must carry nothing).
- `CausesDesire` -- semantic, small codebook. (AtLocation + CausesDesire = HP-eligible semantic relations.)
- `DerivedFrom` -- surface-morphological control; watch the shuffle-climbs-to-match-real signature
  (= char-trigram nearest-substring encoding artifact, NOT transfer). NOT HP-eligible.

## Arms (all paired: same relation triples / split / seed; only the manipulation differs)

- `REAL` -- true (subject,object) training pairs. PRIMARY (HP gates on REAL/inductive).
- `SHUFFLED` -- object labels permuted within the M sample (breaks correspondence); own TRAINED
  fit. MUST stay ~chance; if it CLIMBS to match REAL -> encoding/codebook artifact (HARD_FAIL).
- `MEAN_OBJECT` -- C-independent readout (ignore novel subject). Low-card "popular object" control.
- `RANDENC` (separate floor) -- random-phasor encoding, REAL, inductive, M_OP; structureless -> ~chance.
- `SYNTH_CLEAN` / `SYNTH_CORR_HARD` (separate positive controls) -- see Gate D.

## Pre-registered bands (LOCKED before smoke)

`gain(arm) = arm_acc - 1/V_eff`; primary = REAL, inductive, at M_OP=200; semantic relations only.

- **HARD_PASS:** `TRAINED` clears `gain(REAL,inductive) >= 0.2075` (0.20 floor + 5% band-width,
  META_RULE_L) on AtLocation OR CausesDesire AND `gain(SHUFFLED,inductive) <= 0.05` AND
  `(REAL - SHUFFLED)(inductive) >= 0.2075` (correspondence-dependent) AND
  `(REAL - MEAN_OBJECT)(inductive) >= 0.05` (subject-conditional). The winning (estimator x
  encoding) cell is the headline.
- **HARD_FAIL:** `TRAINED` on BOTH AtLocation AND CausesDesire still `gain(REAL,inductive) <= 0.05`
  (across both encodings) while synth controls fire -> estimator fix alone insufficient; the
  INDUCTIVE setting is the binding constraint -> redirect to inductive-relational-embedding methods.
- **MIDDLE_BAND:** `0.05 < gain < 0.2075`, partial gates, OR **TRANSDUCTIVE-ONLY pass** (transductive
  passes, inductive fails -> NOT a schema-transfer pass; report the gap).
- **DISCRIMINATOR-FIRES gate (SYNTH_CORR_HARD):** `trained_adv = trained_acc - naive_acc >= 0.05`,
  else the estimator axis is vacuous (trained can never beat naive) -> demote to MIDDLE_BAND, do
  not claim an estimator effect. This is the discriminator-must-fire proof for the estimator axis.
- **Sanity rails:** FHRR bind-roundtrip >= 0.90; SYNTH_CLEAN both estimators >= 0.90 (else
  HARNESS_SUSPECT -> MIDDLE_BAND, real arms uninterpretable).

**Make-or-break reporting:** the inductive-vs-transductive GAP (`real_trans - real_ind`) is
reported per cell. For a GLOBAL (subject-agnostic) transform the gap is PREDICTED small; a large
positive gap = the transform relies on having seen the subject = NOT schema generalization.

## HP_SCOPE

HARD_PASS/HARD_FAIL apply to `REAL / inductive` ONLY, per (relation x estimator x encoding) cell.
SHUFFLED / MEAN_OBJECT / RANDENC are controls (expected ~chance; no chain-grade gate). SYNTH_* are
harness / discriminator-fires gates, not substrate-capability claims.

## SCHEMA-VET mandatory fields

- `cardinality_ok`: EXPECTED_N_UNITS = relations(3) x encodings(2) x M(2) x estimators(2) x
  seeds(3) x arms(3) x eval_modes(2) = **432** (smoke 288 at 2 seeds). Verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if good_units < expected (exception: bge-cache-missing
  on host is a graceful degrade -- char_trigram + estimator axis still valid, flagged not failed).
- `arms_differ_verified`: True (hash of REAL_trained / SHUFFLED_trained / REAL_naive / MEAN_OBJECT
  inductive prediction vectors; 4/4 distinct).
- `final_metrics_atomicity`: `tmp_replace` (os.replace).
- `except SystemExit: raise` before `except Exception` (no BaseException; no bare except -- grep-verified CLEAN).
- `crlb_n/a`: argmax-transfer has no CRLB noise-floor; chance floor = 1/V_eff (~0.01);
  `discriminator_reachability`: True (HP abs threshold ~0.22 lies strictly between chance and saturation).
- `baseline_in_band` (META_RULE_AG): controls (SHUFFLED/MEAN_OBJECT/RANDENC) ~chance; REAL not saturated.
- `calibration_check`: `adaptive_with_discriminator_gate` -- baseline = 1/V_eff per relation;
  SYNTH_CORR_HARD trained>naive is the discriminator-fires proof (the estimator axis is not vacuous).
- `discriminator survives scale`: SMOKE runs at FULL N=8192 (only seeds 2->3, N_TEST 60->150,
  pool 500->1500, train-steps 150->250 differ). Both estimators + both encodings fire at N=8192 in smoke.
- `positive_control_arms` (Gate D): SYNTH_CLEAN (both estimators recover clean rotation, tolerance
  >= 0.90) + SYNTH_CORR_HARD (trained EXCEEDS naive on correlated codebook -- reproduces the
  estimator effect at the test regime). PP-275 cited MEASURED prior: Hits@1=0.899 (transductive).
- `effective_vs_nominal_parameter_audit`: M = # training pairs the transform is fit on = the
  actual parameter each estimator experiences (ALIGNED; no partition routing).
- `discriminating_fraction`: not a saturation-bracket cell; M-sweep is the SNR axis. SYNTH_CORR_HARD
  is the in-band discriminator (trained vs naive designed to separate). Gate n/a for real relations
  whose expected outcome IS the chance-vs-structure discriminator.
- `composition_edges`: single mechanism (encode -> fit transform -> bind + codebook cleanup);
  SHAPE_MATCH (unit phasors throughout).
- `functional_requirements`: (1) encode real entities with a FIXED encoder [char-trigram / bounded
  BGE phasor] so novel subjects remain encodable (inductive); (2) estimate the relation transform
  [naive-mean vs trained-rotation-with-negatives]; (3) generalize to a novel subject [bind + cleanup];
  (4) discriminate genuine structure from artifact [shuffled + mean-object + randenc controls];
  (5) separate INDUCTIVE from TRANSDUCTIVE transfer [dual test sets] -- the make-or-break requirement.
- `progress_logging`: `print_flush_true` (all progress lines flush=True). timeout_s >= 1800
  planned -> field mandatory; satisfied.
- `cell_chunked`: false (3 seeds in one cell; per-seed checkpoint via _seed_checkpoint; per-seed
  wall bounded). `start_marker_written`: true (records sem_cache_ok). `crash_diagnostic_present`: true.
  `heartbeat_present`: n/a (per-seed checkpoint + start-marker + flush'd progress lines suffice at
  per-seed sub-few-minute scale; see wall estimate below).
- `defensive_error_checking`: per-relation failure-class instrumentation (META_RULE_J); specific
  `except Exception` records failure-class + halts seed; semantic-cache-missing is a graceful
  per-unit degrade (failure_class BGE_CACHE_MISSING), not a crash.

## Compute architecture

Class (b) sequential-CPU with justification: primitives are elementwise complex mul (bind), vector
mean (bundle), and V x N cleanup matmul (V<=100 tiny). The TRAINED estimator is the cost driver:
per (relation x encoding x M x {real,shuf} x seed) it runs analytic-gradient descent (steps x two
(M x N)(N x V) BLAS matmuls). No N x N matrices; below the GPU-batching threshold; numpy BLAS
(8 threads) is the correct resource. Storage strategy: the transform IS a single vector (rotation
or mean) under test -- NOT a chained-composition cell (META_STORAGE sharded-default n/a). Route
smoke local; FULL to remote_cpu_queue.

## Semantic-encoding cache (bounded probe -- NOT a full-store re-encode)

`data/datasets/bge_small_schema_ablation_entities_v1.npz` (6.28 MB, 8756 entities x 384-dim
float16): BGE-small-en-v1.5 dense embeddings of ONLY the codebook-mapped subjects + top-100
objects of the 3 test relations. Precomputed locally via `tools/precompute_bge_schema_ablation.py`
(deterministic; offline). Cell loads it, centers (removes BGE anisotropy), fixed-projects (seed
12345, dim->N) to a unit phasor -> ZERO model dependency at runtime. **This npz MUST be present on
the remote host** (data files are read from the remote's own checkout, NOT SCP'd by queue_add.sh);
it is committed AND explicitly SCP'd to the remote at dispatch + REMOTE-VERIFIED. If absent, the
cell records BGE_CACHE_MISSING per-unit and still produces the char_trigram x estimator result
(graceful degrade, flagged not failed).

## Smoke result (LOCAL preview at FULL N=8192, 2 seeds; CANONICAL is remote FULL)

<!-- FILLED AFTER SMOKE -->

Small-metrics caveat: legitimacy gated on run_mode==full + elapsed>1 + M-curve + synth controls +
per-cell inductive/transductive numbers, not raw byte size.
