# Pre-registration: exp_encoder_native_gradedcode_ret_agree_v1

Date: 2026-07-08. Owner: exp_dev. Arc: NATIVE-PATH encoder (no external teacher in
KB). Measurement/build ONLY -- no re-ingest, no operational default change, no KB
mutation.

## Question

The graded-code(m=5) finer-quantization trick closed the retrieval-agreement gap on
BGE-TEACHER geometry (ret_agree10 0.19 -> 0.45; landed
exp_encoder_gsbc_gradedcode_retrieval_v1 / marginpush_v1). That was a distilled-BGE
representation. Does the SAME graded-code resolution trick, applied to a NATIVE
no-external-teacher representation (the teacher-free relational encoder trained on
the ConceptNet graph via InfoNCE + VICReg repulsion), close ret_agree10 >= 0.30
WITHOUT BGE in the encoder or the KB?

Report WHICH is the limiter: RESOLUTION (graded fixes it -> native better reader, KB
flip becomes possible with no external model) or MEANING (native semantics too weak
-> redirect to strengthening the teacher-free encoder's semantic fidelity FIRST).

## Representation (native, teacher-free)

The ProjHead + graph-InfoNCE + VICReg encoder from
exp_teacher_free_relational_encoder_cn_subgraph_v1 (ARM_GRAPH_REPULSION;
CHAIN_GRADE this session, repulsion ablation 0.004->0.957, floor beaten 152.9
sigma), re-parameterized to code_dim=4096 so its dense output feeds the certified
graded block geometry (kb=32, blk_l=128, n_dim=4096). Surface features =
deterministic hashed char-trigram bag (substrate-native V1; NO word-meaning
supervision). NO BGE anywhere in the representation or any training loss.

## Gold (evaluation ORACLE ONLY, never ingested, never in encoder/KB)

Name-aligned BGE-large cached embeddings (bge_large_v2_name_177899;
133305 CN_ concepts). ret_agree10 is inherently "top-10 neighborhood agreement with
a gold reference"; in the BGE arc the gold WAS BGE and 0.45 was measured against it.
Keeping the SAME gold makes the 0.30 bar apples-to-apples: it is exactly the KB-flip
gate -- "can we flip the KB to native codes WITHOUT regressing the retrieval
neighborhoods the current (BGE-defined) KB provides." The native encoder never sees
BGE; BGE is only the yardstick. Substrate-knows-nothing is preserved (the
representation + KB stay teacher-free). Alignment MEASURED@smoke = 2143/2143 = 1.000.

## Arms (per seed; EXPECTED_N_UNITS = 4)

| arm | code | role |
|-----|------|------|
| NATIVE_DENSE | trained native dense (4096-d, L2) | CEILING (best native, full resolution) |
| NATIVE_COARSE | graded_block_code(dense, m=1) | must-fail DISCRIMINATOR baseline |
| NATIVE_GRADED | graded_block_code(dense, m=5) | TREATMENT (certified resolution trick) |
| NATIVE_RANDINIT | untrained native dense | FLOOR (char-trigram surface control) |

Disambiguator: the DENSE ceiling arm + per-arm graph modularity_z (Newman-analog
assortativity vs a degree-preserving null) separate RESOLUTION-limiter from
MEANING-limiter. A HIGH modularity_z with a LOW ret_agree10-vs-BGE is the decisive
"native learned REAL graph-relational structure that DIVERGES from BGE
distributional-semantic geometry" finding (meaning-limiter that is NOT
under-training).

## Bands (PASS / FAIL both documented BEFORE run)

Bar (KB-flip gate, Director hand-off): ret_agree10 >= 0.30; META_RULE_L strict band
0.335 (= 0.30 + 0.05*(1-0.30)). Per-seed verdict; cross-seed mean/min aggregated
downstream (like the gradedcode retrieval arc).

- **HARD_PASS_RESOLUTION** (native reader works): DENSE >= 0.30 AND GRADED >= 0.335
  AND GRADED - COARSE >= 0.01. Resolution was the limiter; graded closes it WITHOUT
  BGE in the representation -> path (b) works; KB flip becomes possible with no
  external model.
- **HARD_FAIL_MEANING_LIMITER**: DENSE < 0.30. Even the full-resolution native dense
  ceiling is below the bar vs BGE; graded resolution cannot rescue meaning the
  representation does not have. Decisive redirect: strengthen the teacher-free
  encoder's semantic fidelity FIRST.
- **HARD_FAIL_RESOLUTION_INSUFFICIENT**: DENSE >= 0.30 AND GRADED < 0.30. The native
  meaning is adequate but m=5 graded recovers too little; redirect to higher-m /
  GWTA-expansion (v12), not to strengthening semantics.
- **MIDDLE_BAND**: GRADED in [0.30, 0.335).

## Smoke gate (machinery + discriminator-fires; MEANING verdict is FULL-only)

Smoke PASS = all 4 arms finite ret_agree10 in [0,1] + codes bit-distinct + gold
align_frac >= 0.50 + discriminator FIRES (must-fail COARSE ret_agree10 < 0.30 at
smoke scale, per USER saturation-vacuous rule). The DENSE-ceiling MEANING verdict is
FULL-only (needs full training scale + multi-seed).

Smoke RESULT (seed 7, MEASURED@data/exp_encoder_native_gradedcode_ret_agree_v1_smoke_seed7_smoke/metrics.json):
- verdict = HARD_PASS (SMOKE_MACHINERY_OK); discriminator fires (COARSE=0.1338 < 0.30)
- ret_agree10: DENSE=0.1990, COARSE=0.1338, GRADED=0.1886, RANDINIT=0.1311
- graded-coarse lift = +0.0547 (resolution trick TRANSFERS to native: graded
  recovers ~all of the dense signal that coarse throws away)
- modularity_z: DENSE=336.2, COARSE=384.0, GRADED=442.0, RANDINIT=65.0 (trained
  encoder massively learned graph structure; NOT under-training)
- PREVIEW READ: MEANING-limiter signature -- the native dense ceiling (0.199) sits
  below the 0.30 bar despite huge graph fidelity; the native (graph-relational)
  neighborhoods diverge from BGE (distributional-semantic) neighborhoods.

## SCHEMA-VET fields

- cardinality_ok: EXPECTED_N_UNITS=4; verdict counts len(per_arm).
- arms_differ_verified: sha256 over float32 codes of all 4 arms (MEASURED@smoke True).
- final_metrics_atomicity: tmp_replace (write_metrics os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare). Grep-clean.
- crlb_n/a: no closed-form noise floor; discriminator is ret_agree10 AGREEMENT.
  chance_floor = 10/(V-1) THEORETICAL (MEASURED@smoke 0.00467 at V=2143; bar 0.30 is
  ~64x chance). discriminator_reachability=True.
- baseline_in_band: AG saturate-high (>0.95) failure mode CANNOT occur (non-distilled
  native vs BGE will not saturate ret_agree10); band-check on DENSE ceiling; the floor
  is the live risk and IS the meaning-limiter signal (declared AG-exemption).
- discriminator survives scale: resolution transform (m=1 vs m=5) is a DETERMINISTIC
  map on the fixed trained z -> graded-vs-coarse ordering scale-invariant (option B).
  MEANING verdict FULL-scale.
- calibration_check: default_ok_for_this_regime (graded geometry pinned to certified
  m=5 operating point; only the input representation re-pointed to native).
- cell_chunked: True (one seed per cell; FULL multi-seed = sibling _seed_7/13/17).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True (MEASURED@smoke).
- progress_logging: print_flush_true (line-buffered stdout + flush=True).
- HP_SCOPE: {NATIVE_GRADED: [ret_agree10_bar]}. DENSE/COARSE/RANDINIT diagnostic/floor.

## Compute architecture

(c) MIXED with justification. Native encoder training = sequential-CPU (SGD steps
have a genuine sequential dependency; single linear ProjHead; parent teacher-free
encoder is established CPU-only; GPU speedup marginal for a one-layer encoder).
ret_agree10 top-10 neighbor computation = torch matmul (device-agnostic; runs on the
remote_cpu_queue CPU runner). Storage strategy: no_storage / no_composition (pure
per-concept re-encode + retrieval-agreement measurement; no bundling, no chained
retrieval). FULL routes to remote_cpu_queue.

## FULL dispatch (3 seeds, CHUNKED single-seed-per-cell)

queue: remote_cpu_queue. Scripts: exp_encoder_native_gradedcode_ret_agree_v1_seed_{7,13,17}.py.
timeout_s = 9000 (smoke wall 335s at V=2143/epochs=400/1seed; FULL V=12000/epochs=800;
training ~epochs*batch*feat_dim, ret_agree10 ~V^2; 1.5x margin; well under 14400 cap).

DEP-PARITY (orchestrator MUST ensure on remote before dispatch): the wrapper's
explicit import triggers queue_add.sh Pattern-6 re-SCP of
exp_teacher_free_relational_encoder_cn_subgraph_v1.py; BUT the core also imports
hdlab/gsbc_graded_encoder.py, which is NOT covered by sibling auto-SCP (hdlab
Pattern-5b allowlist = cleanup_family only). Ensure hdlab/gsbc_graded_encoder.py +
the BGE cache data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz
+ data/substrate_index/concept/relations.jsonl are present on remote.
