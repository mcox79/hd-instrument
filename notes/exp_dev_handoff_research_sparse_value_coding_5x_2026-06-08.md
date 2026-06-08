# exp_dev hand-off -- research: sparse VALUE coding within shards 5x

Filed-by: research sub-agent (Sonnet 4.6), 2026-06-08
Trigger: d:/AI/hd-instrument/notes/research_drill_sparse_value_coding_within_shards_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates,
substrate-product readings, tier hints, and why-now context. exp_dev designs all sweep
parameters, thresholds, queue routing, and pre-reg bands autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist
(or confirm with orchestrator). Do not ship if paused.

---

## Context summary

This drill addresses per-shard capacity via K-sparse VALUE vectors (K active positions
out of N=65,536 in each stored value vector), rather than the current dense {-1,+1}^N
bipolar encoding.

Key empirical foundations:
- sparse_hopfield_v1 HP cycle 180: top-5 Hopfield matches dense softmax at delta=0.000.
  Top-k cleanup works. This is the retrieval primitive for sparse VALUES.
- bundle_capacity_largeN MID: empirical K_crit exceeds N/(2 ln N) by 43-58% at large N.
  The conservative formula understates actual capacity.
- cleanup_confidence_roc HP: AUC=1.0000 abstention primitive. Sparse VALUES are predicted
  to give even sharper AUC (K^2/N near-zero overlap vs N/2 for dense).
- topk_recall HP: recall@5=1.000 at 35% bit-flip corruption. Top-k retrieval is robust.

Key theoretical finding from drill (level 2-3 matched filter analysis):
- SNR formula for dense VALUES: SNR = sqrt(N/M). Capacity: M_max ~ N/(2 ln N) ~ 1,500.
- SNR formula for K-sparse VALUES with matched-filter: SNR = sqrt(N/(M*K)).
  Capacity: M_max = N/K.
  For K=50: M_max = 65536/50 = 1,311 (slightly LESS than dense).
  For K=10: M_max = 65536/10 = 6,554 (4.4x MORE than dense).
  For K=1: M_max = 65,536 (44x more but near-one-hot -- very low info per fact).
- Storage compression is IMMEDIATE and large: K=50 VALUE vectors use 82x less storage
  per value (50 * 16 bits vs 65,536 bits). This enables 82x more KB entities in VRAM.
- GDPR deletion: per-fact deletion from sparse W is O(K) per deletion vs O(N*M) for dense.
  K=50 gives 50x faster deletion. High regulatory value.

The critical K decision point: K=50 may give slightly less recall capacity than dense
but 82x storage compression. K=10 may give 4.4x more recall capacity with 3,276x storage
compression. The empirical K-sweep is the decisive test.

---

## Anchor candidates (rank-ordered by P_actionable x effort)

### 1. Sparse-VALUE K-sweep storage-and-recall (HIGHEST PRIORITY -- decisive test)

Anchor pointer: SPARSE-VALUE-K-SWEEP-A1 (new; not yet queued)
Substrate-product reading:
  If K=50 gives recall@1 > 0.90 (HARD-PASS): sparse VALUE storage compression is
  viable TODAY with no algorithm change (Path A). Storage 82x smaller. Ship immediately.
  If K=10 gives recall@1 > 0.85 (HARD-PASS): 4.4x recall capacity multiplier confirmed.
  This is the gate for the per-shard capacity upgrade from ~1,500 to ~6,500 facts/shard.
  At N=65,536 and K=10: per-shard capacity approaches biological minicolumn scale (10^4).

  The two measurements (storage compression at K=50, capacity at K=10) are both in the
  same K-sweep experiment. One experiment, two products.

Tier hint: CPU queue; 30 min wall; N=65,536 (or N=4,096 for fast smoke, then N=65,536 full).
Why-now: sparse_hopfield_v1 HP (cycle 180) validated top-k cleanup. The cleanup primitive
  already exists. The only missing piece is the empirical K vs recall curve for the VALUE
  storage operation. This is the cheapest decisive test on file for the per-shard capacity
  ceiling question.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: K=50 recall@1 > 0.90 AND K=10 recall@1 > 0.85 at M=1500, N=65,536.
    Both storage compression and capacity gain confirmed. Path A + matched-filter path both viable.
  MIDDLE-BAND: K=50 recall@1 > 0.75 but K=10 recall@1 < 0.80.
    Storage compression viable; capacity gain is limited; pursue Path D (dense role + sparse value).
  HARD-FAIL: K=50 recall@1 < 0.70 at M=1500, N=65,536.
    Sparse VALUES are not worth complexity; stick with dense. Storage compression via
    int4 quantization (PP-106) is the better path. Close this thread.

---

### 2. Dual-level bind+retrieve with sparse VALUES (Path D)

Anchor pointer: SPARSE-VALUE-BIND-D1 (new; should follow A1)
Substrate-product reading:
  Dense role (r) + sparse value (v_K): bind(r, v_K) gives K-sparse result. Bundle M such
  bindings. Unbind with dense query role r_q. Recover top-K positions. Compare recall vs
  pure-VALUE storage (A1) to measure the "binding penalty" on sparse VALUES.

  If binding penalty < 5% recall drop: dual-level scheme works. Dense roles route; sparse
  values store. Product: per-subject shard routing (unchanged, PP-128 HP) with K-sparse
  VALUE payloads (82-3276x compressed).

Tier hint: CPU queue; 45 min wall; depends on A1 results.
Why-now: A1 gives the pure storage baseline. D1 gives the binding-inclusive production baseline.
  The gap between A1 and D1 quantifies the binding penalty. Small gap -> ship Path D.

Pre-reg bands (research recommendation):
  HARD-PASS: bind+retrieve recall@1 within 5% of pure-VALUE storage recall (from A1).
    Binding does not significantly degrade sparse VALUE retrieval. Path D viable.
  MIDDLE-BAND: 5-15% degradation vs A1. Binding adds noise but Path D still usable with smaller K.
  HARD-FAIL: > 20% degradation vs A1. Dense role XOR washes out sparse VALUE structure.
    The matched-filter analysis is wrong; explore sparse ROLE + sparse VALUE (symmetric sparse).

---

### 3. Sparse-VALUE abstention sharpening (PATH C variant, PP-107 extension)

Anchor pointer: SPARSE-VALUE-AUC-C1 (new; should follow A1)
Substrate-product reading:
  The drill predicts that K-sparse VALUES give sharper cosine score bimodality (AUC > 0.9999
  with better in/out separation) because K^2/N cross-talk is ~10,000x lower than dense N/2.
  If abstention AUC remains 1.0000 even at higher M loads (M=5,000, M=10,000) with sparse
  VALUES: the regulatory story strengthens -- higher-load shards with same perfect abstention.

Tier hint: CPU queue; 30 min wall; requires A1 first to establish K operating point.
Why-now: PP-107 AUC=1.0000 at dense M=1,500. Sparse VALUES may maintain this AUC at M=5,000.
  That is the main regulatory differentiation (GDPR, EU AI Act Article 12 Aug 2026).

Pre-reg bands (research recommendation):
  HARD-PASS: abstention AUC >= 0.9999 at M=3,000 with K=50 sparse VALUES.
    Perfect abstention holds at 2x density. Regulatory story doubles.
  MIDDLE-BAND: AUC > 0.995 at M=3,000. Still strong; marginal vs dense for compliance narrative.
  HARD-FAIL: AUC < 0.990 at M=3,000. Sparse VALUES degrade abstention. Investigate why
    (prediction: sparse VALUES create systematic bias in out-of-distribution cosine scores).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_sparse_value_coding_within_shards_5x_2026-06-08.md
- sparse_hopfield_v1 metrics: d:/AI/hd-instrument/data/exp_sparse_hopfield_v1/metrics.json
  (HARD_PASS: dense=1.000 sparse=1.000 delta=0.000 at top-5)
- PP-107 abstention: d:/AI/hd-instrument/notes/cycle180_cap_map_append.txt
- PP-110 topk resilience: same file, cleanup_confidence_roc HP
- Cycle 183 sharding architecture: d:/AI/hd-instrument/notes/orchestrator_to_research_results_summary_2026-06-08_cycle183.md
- Prior sparse-W work (different from sparse-VALUE): notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md
  (note: sparse-W modifies the W matrix structure; sparse-VALUE modifies the stored value vectors.
  These are different axes. Sparse-W work does NOT cover the K-sparse value vector case.)

---

## Contract section

- exp_dev does NOT copy this file's pre-reg numbers verbatim. It verifies them against
  the current queue state and formula-selftests before dispatching.
- If the paused flag is set, this entire handoff waits.
- Anchor A1 must complete before D1 or C1 dispatch (D1 and C1 depend on K* from A1).
- exp_dev determines actual queue routing (CPU vs GPU), seed count, and parameter sweep ranges.

## Autonomy declaration

exp_dev is authorized to:
- Choose K values for the sweep within the range K in {1, 5, 10, 20, 50, 100, 500}
- Set M, N, and noise parameters for each anchor
- Route A1 to CPU or GPU based on queue state
- Add or remove anchors from the batch based on queue depth
- Adjust pre-reg thresholds by +/- 0.05 based on smoke gate results

exp_dev is NOT authorized to:
- Change the fundamental test design (K-sparse VALUE sweep is the decisive test)
- Pre-frame smoke gates as PASS without running them
- Dispatch D1 or C1 before A1 verdict is in
