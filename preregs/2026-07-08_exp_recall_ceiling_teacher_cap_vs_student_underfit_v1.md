# Pre-reg: recall-ceiling teacher-cap vs student-underfit (REAL BGE)

anchor: `recall_ceiling_teacher_cap_vs_student_underfit_v1`
cell: `experiments/exp_recall_ceiling_teacher_cap_vs_student_underfit_v1.py`
date: 2026-07-08
author: hdi_exp_dev

## Question (disambiguation, not a fix)
The prior decomposition (`exp_recall_ceiling_capacity_vs_semantic_decomp_v1`,
HARD_SEMANTIC) proved the ~0.5 concept-recall ceiling is SEMANTIC-fidelity-bound,
NOT capacity-bound -- but with a CONTROLLED teacher-noise PROXY (sigma_e). A proxy
teacher cannot answer the load-bearing follow-up, which has OPPOSITE fixes:
- (a) STUDENT-UNDERFIT: the substrate encoder fails to reach the retrieval fidelity
  of its own BGE teacher -> FIX THE STUDENT (train/capacity; v2 MLP distill target).
- (b) TEACHER-CAP: BGE itself tops out near ~0.5 on our concept-retrieval task, so
  distillation can never exceed it -> REPLACE the distillation objective with a
  substrate-native one.

## Design: same task, same dictionary, same cleanup; teacher arm vs student arm
REAL BGE (justification): the question is literally whether the REAL BGE tops out;
a teacher-noise proxy assumes teacher fidelity is a knob and by construction cannot
distinguish (a) from (b). Load cached BGE-large teacher embeddings
`data/substrate_index/cached_indices/bge_large_v2_name_43905_8a40445a.npz`
(`semantic` (V,1024) + `id_order_json`). One embedding per concept (composite==
semantic in cache MEASURED@calib; wordnet cache empty) so query!=key comes from the
task, not a second surface form.

Two real concept-retrieval readouts on the SAME dictionary + SAME encoders:
- TASK SP (SUPERPOSITION recall@J) = the PRODUCTION ~0.5 task (v2 distill smoke
  MEASURED bundle@J5 diag=0.420). Bundle J concept vectors (query=unit sum, genuinely
  != any key); argmax-cosine recall@J over V concepts. Operating J_OP=5.
- TASK SC (SINGLE-CONCEPT under shared-source rendering noise) = pointwise-fidelity
  cross-check. Query = concept BGE source + alpha*||src||*unit-gaussian, encoded
  THROUGH each arm; argmax-cosine recall. Operating ALPHA_OP=1.2.
- CROWDING scalar (teacher-cap witness): median teacher NN-cos + frac(>0.90).

Arms (paired, same seeds): TEACHER_FLOAT (BGE identity) vs STUDENT_REPR (canonical
sparse-bipolar HD code: random Gaussian proj Din->N=4096, top-K=128 magnitude WTA
sign, 3.125% sparse = production sparsity). STUDENT_REPR is the ZERO-TRAINING
representation-ceiling reference; the trained MLP student (v2 spearman HARD_FAIL
0.317; smoke bundle@J5 diag 0.420 CITED@ v2 smoke metrics) sits at/below it, so the
untrained code family bounds the question without coupling to a fragile checkpoint.

## Bands (PRIMARY = production superposition task; symmetric, both directions)
Let RT_sp/RS_sp = teacher/student superposition recall @J_OP; SP_gap=RT_sp-RS_sp.
Let RT_sc/RS_sc = teacher/student single-concept recall @ALPHA_OP; SC_gap=RT_sc-RS_sc.
- OBJECTIVE_MISMATCH_SUBSTRATE_NATIVE (fix b): SP_gap <= -0.15 AND RT_sp <= 0.55.
  (Matching BGE geometry caps recall low; substrate decorrelation exceeds teacher.)
- STUDENT_UNDERFIT (fix a): SP_gap >= +0.20 AND RT_sp >= 0.70.
  (Teacher has superposition fidelity the student loses.)
- TEACHER_CAP_INTRINSIC: |SP_gap| <= 0.10 AND RT_sp <= 0.55.
- MIDDLE_BAND_MIXED otherwise.
Pointwise sub-class (reported, non-gating): SC_gap >= +0.15 => substrate loses
pointwise fidelity (representation-cap on discrimination); <= -0.15 => adds it.

## Feasibility / calibration (MEASURED@ calib on 43905-concept cache before pre-reg)
- V=40000: SP@J5 teacher=0.163 student=0.825 gap=-0.662; SC@alpha0.8 teacher=1.000
  student=0.780 gap=+0.220; median NN-cos=0.904 frac>0.90=0.524.
- V=4000 (smoke): SP@J5 gap=-0.561; sign + teacher-low survive scale.
OBJECTIVE_MISMATCH needs SP_gap<=-0.15 (measured -0.56..-0.66; large margin) and
RT_sp<=0.55 (measured 0.16..0.34). Bands strictly above floor + feasible.

## SCHEMA-VET fields
- arms_differ_verified: true (sha256 teacher-dict vs student-dict; smoke MEASURED True)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise before except Exception (no BaseException; grep-clean)
- crlb_n/a: retrieval recall has no closed-form noise floor; feasibility via
  calibrated in-band operating points.
- baseline_in_band: superposition arms at J_OP in (0.05,0.95) (smoke MEASURED
  teacher 0.337 / student 0.929 in band). SC teacher ~1.0 is the SIGNAL (teacher
  pointwise headroom), declared exempt not saturation-vacuous (student differs).
- discriminator_survives_scale: smoke V=4000 fires PRIMARY (SP_gap=-0.592 MEASURED@
  smoke; calib -0.662 @V40000). Analytical: superposition of correlated vectors
  degrades with V; decorrelated code holds -> gap sign robust to V.
- calibration_check: default_ok_for_this_regime (real BGE; operating points calibrated)
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (smoke=3 full=5); verdict counts per_seed.
- discriminating_fraction: SP curve spans J{1,2,3,5,8} -> teacher {1.0,0.97,0.61,0.20,0.05}
  (calib V20000); >=3/5 points in (0.10,0.90) discriminating band.
- telemetry_sensitivity: seed moves SP recall (smoke MEASURED spT@5 0.354/0.326/0.330)
  and SC recall; self-test asserts not bit-identical.
- functional_requirements: (1) put teacher + student on SAME task/dict/cleanup ->
  paired arms; (2) reproduce the ~0.5 production number -> superposition@J5; (3)
  separate teacher-cap from student-underfit -> gap sign + teacher level bands.
- composition_edges: n/a (no primitive->primitive composition; superposition is the
  measured phenomenon, not a storage choice for a downstream chain).
- storage_strategy: bundled_as_measurement_target (TASK SP IS superposition-recall
  itself; exempt from sharded-default -- we measure bundle recall, not choose storage).
- compute_architecture: sequential-CPU (BLAS-vectorized matmul cosine; no Python-loop
  matmul; smoke wall 11s MEASURED; full <5min at V=40000). GPU batching would not
  materially speed a <5min cell; justified sequential-CPU.
- progress_logging: line_buffered_stdout (+ flush=True on progress lines).
- start_marker_written: true; crash_diagnostic_present: true (Exception->CELL_CRASHED);
  cell_chunked: false (single-cell multi-seed w/ per-seed resumable partials);
  heartbeat_present: n/a (wall < 5min; per-seed progress lines flush).

## Dispatch
FULL -> local_cpu_queue ONLY. The BGE cache npz is gitignored (data/ untracked);
remote runners pull origin/main and would NOT have the teacher cache -> data-locality
forces local. Cell is CPU-light (<5min at V=40000). timeout_s=900.
```
bash tools/orchestrator/queue_add.sh local_cpu_queue recall_ceiling_teacher_cap_vs_student_underfit_v1 experiments/exp_recall_ceiling_teacher_cap_vs_student_underfit_v1.py preregs/2026-07-08_exp_recall_ceiling_teacher_cap_vs_student_underfit_v1.md 900
```
