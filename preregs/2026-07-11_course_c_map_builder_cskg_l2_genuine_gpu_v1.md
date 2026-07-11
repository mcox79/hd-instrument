# Pre-reg: Course C map-builder ON CSKG -- GPU-FITTING VARIANT (parallel early-read; distinct anchor)

- anchor_name: `course_c_map_builder_cskg_l2_genuine_gpu_v1`
- cell: `experiments/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1.py`
- metrics: `data/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1/metrics.json`
- date: 2026-07-11
- queue: overnight_queue (GPU) FULL. Runs IN PARALLEL with the CPU canonical run
  (`course_c_map_builder_cskg_l2_genuine_v1` on remote_cpu_queue). Distinct anchor + output dir -> NO
  metrics collision; different runner -> no conflict. USER wants BOTH (GPU faster/early-read; CPU full-dim/safe).
- seeds FULL: [7, 17, 23] (3); EXPECTED_N_UNITS = n_seeds
- SCIENCE: IDENTICAL to the CPU cell `preregs/2026-07-11_course_c_map_builder_cskg_l2_genuine_v1.md`
  (same CSKG dense core, same L2-genuine held-out arena [inverse/alias/sym-leak stripped], same 7 arms,
  same must-fail controls, same ORACLE-fires guard, same pre-registered bands, same FPE_ELL=0.55 / KGE
  defaults / k=24 / fpe_dim=4096 / kge_epochs=600 / replay_passes=80 / k_core=12 / MIN_SUPPORT=10 /
  MIN_CONF=0.10). Read that prereg for the full question / arena / bands / decision tree. THIS file documents
  ONLY the memory-footprint delta.

## Why a GPU-fitting variant (the OOM diagnosis)
The prior GPU FULL OOM'd TWICE on the shared 8GB GPU. BOINC holds ~5GB -> only ~2.5GB free. The first fix
chunked the (nq,N) candidate SCORING (worked). Two memory sources remained UN-chunked:
1. `fit_transe_coords` did FULL-BATCH negative sampling: the `(E, KGE_NEG, k)` intermediate is ~1.5-3 GiB at
   FULL CSKG edge counts, allocated 7x sequentially (5 geom arms + oracle + 2 backdoor refits) WITHOUT
   `torch.cuda.empty_cache()` -> the caching allocator RESERVED the peak (~the reported 4.33 GiB base).
2. DISCRETE's `Z` (N x dim complex64 ~0.84 GiB) stayed resident THROUGH the geom-arm FPE scoring, which ALSO
   materializes `S_all` (0.84 GiB) + the cos/sin/complex encode transient (~1.26 GiB).
4.33 GiB base + 1.84-3.13 GiB request > ~2.5 GiB free -> OOM before scoring even completed.

## The fix (memory only; science UNCHANGED -- self-test grid ONESHOT hits@1 BIT-IDENTICAL)
- `fit_transe_coords`: negative sampling chunked via GRADIENT ACCUMULATION (one `opt.step()` per epoch;
  loss summed over edge chunks / total_pairs -> reproduces the full-batch mean-margin gradient EXACTLY). The
  `(chunk=16384, KGE_NEG, k)` neg transient is ~15-50 MB instead of GiB-scale, and E-INDEPENDENT. ONESHOT
  stays a genuine ONE-SHOT full-batch fit.
- `fit_transe_replay`: minibatch capped (REPLAY_BS_CAP=131072) so its neg intermediate is bounded regardless of E.
- `fit_discrete_bind` + the S_all FPE encode (`_encode_all`): (N,dim) phasor tables built ROW-CHUNKED
  (ENCODE_ROW_CHUNK=4096) so the cos/sin/complex encode transient is bounded to ~0.2 GiB, never +1.26 GiB.
- DISCRETE scored FIRST and Z freed (`del Z, R` + `empty_cache`) BEFORE any geom arm materializes S_all ->
  Z and S_all NEVER co-reside.
- `torch.cuda.empty_cache()` between every sequential fit + between arms + between seeds -> the reserved pool
  tracks the (now small) live set, not the historical peak.
- The (nq,N) query-side scoring chunking (FPE_SCORE_CHUNK=256) from the CPU cell is RETAINED unchanged.
- The operator module + the CPU cell + its metrics are NOT touched (the 3 memory-heavy fit primitives are
  RE-DEFINED LOCALLY in the GPU cell; only read-only helpers imported).

## DIM decision: full-dim 4096 PRESERVED (no reduction needed)
dim4096 is preserved (readout capacity: the smoke under-fits at low dim + the ORACLE must fire). Estimated
peak (arithmetic; N~25.7k, dim=4096, complex64=8B):
- single phasor table (S_all OR Z): 25700*4096*8 = 842 MiB
- Z and S_all NEVER co-reside (DISCRETE scored + freed first)
- encode row-chunk transient: ~0.2 GiB (freed before the matmul)
- fit neg transient: ~15-50 MiB (chunked, E-independent)
- worst-case cuBLAS conj materialization of `conj(S_all)`: +842 MiB
=> PEAK ~1.0 GiB typical, ~1.7 GiB worst-case (conj materialized) << 2.3 GiB target (headroom below ~2.5 GiB
free). Consistent with the CPU cell prereg's already-MEASURED "peak per geom arm ~1.7 GB" -- this variant only
REMOVES the co-resident Z and the fit-base reserved pool from that figure. NOTE: arithmetic estimate; local
laptop has no CUDA so no live peak measurement was taken (self-test + smoke ran on CPU). The ORACLE-fires gate
catches any residual under-fit as INCONCLUSIVE (never a false verdict).

FASTER FULL-DIM ALTERNATIVE (USER decision, flagged to director): free the ~5 GiB BOINC holds -> the full
~6.8 GiB budget returns and dim4096 fits trivially with the ORIGINAL cell. Dim reduction (3072/2048) is the
code-side fallback if a GPU ever has even less free memory; not needed here.

## Pre-flight gates (MEASURED, local CPU venv, 2026-07-11)
- SELF-TEST (`--self-test`, 13.5s): SELFTEST_PASS. geometry_fires=True; grid ONESHOT hits@1=0.7179
  (BIT-IDENTICAL to the CPU cell -> grad-accum reproduces the full-batch fit), ORACLE=1.0, DISCRETE=0.0513,
  POP=0.0, SCRAMBLE=0.0256, RANDOM=0.0; grid_recovers/beats_discrete/beats_pop/scramble_ok/oracle_fires all
  True; 7 distinct sigs. SYN_COMPOSITIONAL L2-genuine=150 (ONESHOT 0.287 > POP 0.173 > DISCRETE 0.047;
  SCRAMBLE/RANDOM at chance); SYN_FREQ_GUESSABLE no-manufacture (freq_geo 0.093 << freq_pop 1.0).
  MEASURED@data/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1_selftest/metrics.json
- SMOKE (`--smoke`, 21.9s, local CPU k_core=3 slice): SELFTEST_PASS geometry_fires=True. CSKG assembly
  IDENTICAL to CPU cell (3000 nodes / 16487 edges / avgdeg 11.4 / 19 rels). L2-genuine arena extracts 449
  held-out; 7 distinct arm sigs. Verdict INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT (oracle=0.007 at smoke
  k=8/dim512 -> under-fit exactly as pre-registered; the FULL k=24/dim4096 must clear ORACLE-fires before any
  geometry claim is trustworthy). No regression vs the CPU cell's smoke.
  MEASURED@data/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1_smoke/metrics.json

## FULL dispatch (handed to orchestrator; exp_dev does NOT SCP/push)
overnight_queue (GPU). device=auto -> CUDA on the GPU host (HDLAB_QUEUE != remote_cpu_queue). Runs in PARALLEL
with the CPU run. queue_add command in the exp_dev completion report; timeout 14400s (generous for a
BOINC-contended shared GPU + 3 seeds + backdoor refits). Fallback (zero code change): route to
remote_cpu_queue -> the same env-aware device selection force-CPUs (HDLAB_QUEUE==remote_cpu_queue), no 8GB wall.

## SCHEMA-VET fields
All fields are INHERITED from the CPU cell prereg (identical science) EXCEPT the memory footprint above.
cardinality_ok: True (EXPECTED_N_UNITS = n_seeds; per-seed >=5 distinct arm sigs + L2-genuine >= min_heldout).
arms_differ_verified: True (7 distinct sigs, MEASURED at self-test + smoke). final_metrics_atomicity:
tmp_replace. except SystemExit: raise BEFORE except Exception (grep-verified clean; no bare except / no
BaseException). start_marker_written / crash_diagnostic_present / heartbeat_present: True.
progress_logging: print_flush_true. cell_chunked: False (3 seeds one cell + per-seed write_partial +
cardinality gate + per-seed failure_class). discriminator_survives_scale: scale-invariant planted self-test
(grid geometry_fires + SYN no-manufacture) fires through the IDENTICAL code path; CSKG headline REPORTED at
smoke, FULL decides, gated behind ORACLE-fires. HYPOTHESIZED vs MEASURED: self-test/smoke numbers tagged
MEASURED@ paths above; peak is MEASURED-by-arithmetic (no local CUDA); bands are pre-registered thresholds
inherited from the CPU prereg; VET numbers CITED@notes VET a46eadfa.
