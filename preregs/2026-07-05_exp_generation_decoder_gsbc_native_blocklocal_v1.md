# Prereg: generation decoder round-trip on NATIVE GSBC fillers via the GSBC-native (block-local sparse) factorizer

Date: 2026-07-05
Anchor: `generation_decoder_gsbc_native_blocklocal_v1`
Cell: `experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py`
Design memo: `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`
Parent (reused UNCHANGED): `experiments/exp_generation_decoder_roundtrip_v1.py` (MVP dense pipeline).
Proven Stage-A: `experiments/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000.py` (HARD_PASS K=26 >=85%).
Filler pool (untracked, SCP to remote): `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz`.

## Question
The decoder MVP (MM_STANDARD, commit 1fd6f580a) round-tripped S/V/O at exact-ordered 1.000 on a BGE-randproj
bipolar STAND-IN filler. VET open gap: does the "mouth" round-trip on our REAL concept encoding? And
(coordinator course-correction 2026-07-05): use the GSBC-NATIVE factorizer -- the PROVEN block-local sparse
resonator (Frady-Sommer arXiv:2404.19126; Hersche/Terzic), which MATCHES the GSBC sparse-block geometry --
rather than binding native GSBC fillers in a DENSE bipolar-BSC multiply-bind algebra (the encoding MISMATCH
that collapses under superposition of correlated fillers).

**Does the end-to-end round-trip (Stage A factor + Stage B position-sort + Stage C lexicon cleanup) hold on
REAL correlated GSBC fillers with the block-local sparse resonator, across D<=6 / V<=1024, and where does it
degrade beyond the box?**

## Load-bearing swap (native fillers)
Filler code = the REAL deployed concept encoder's output. A BOUNDED pool (10000 of 177899 concepts, 5.6pct --
NOT a full-store re-encode, which is HELD) is pre-encoded OFFLINE with the GSBC_EXPAND2X seed7 FULL student
(`data/substrate_concept_encoder_v12_gwta_seed7/_ckpt_best_GSBC_EXPAND2X.pt`) and cached sparse. At decode-time
the native GSBC code (GSBC_DIM=8192, 192 active, unit-L1) is projected GSBC_DIM->bs (JL-preserves the real
cos-cone; MEASURED raw pairwise cos ~0.511) and sparsified top-(0.02*bs) sign -> a sparse bipolar block code
carrying the real GSBC correlation (cleanup collisions are realistic, not iid).

## Architecture (block-local sparse resonator = Stage A/B/C in one op)
N=8192 partitioned into D disjoint blocks (bs=N/D). Bind = SUM of per-block sparse codes (no multiply/
intersection collapse -> scales far past dense K~7-9). Position IS the block index (Stage B carried in the
vector, filler code shifted into block d). Recover = per-block argmax over the codebook (Stage C; blocks
disjoint -> exact-by-construction, only within-block correlated-distractor competition bites).

## Arms
Per grid point (V,D), PAIRED (same propositions across arms at a seed):
- `blocklocal_gsbc` -- NATIVE GSBC fillers, block-local sparse resonator. THE DELIVERABLE.
- `blocklocal_synth` -- random sparse bipolar codes (proven-cell construction). iid CEILING / positive control (Gate-D reproducer of the block-local resonator at the test regime).
- `noorder_ctrl` -- native GSBC, block-local, all slots bound into block 0 (position destroyed). MUST collapse.

Mechanism contrast at ANCHOR (V=1024, D=3) only, DENSE bipolar-BSC pipeline (copied UNCHANGED from MVP) on the same native GSBC concepts:
- `dense_gsbc_rolesknown` -- positions handed in. Expect HOLD (MEASURED@MVP real_rolesknown_hi exact=1.000).
- `dense_gsbc_fullreso` -- positions UNKNOWN, R=16. Expect COLLAPSE on correlated fillers (the mismatch; MEASURED@MVP real_fullreso_hi exact=0.000).
- `dense_synth_fullreso` -- iid, R=16. Expect HOLD (positive control: the dense resonator works iid).

## Grid (sweep D and V; map where round-trip holds vs degrades)
DIRECT (gated deliverable box; memo HARD constraint D<=6 V<=1024): (256,3), (1024,3)=ANCHOR, (256,6), (1024,6).
BOUNDARY (capability MAP beyond box; ungated; locate the cliff): (4096,6), (8192,6), (1024,12), (1024,26), (8192,26).
Seeds: (7,13,19) FULL. N=8192 in ALL modes (discriminator-survives-scale; smoke reduces V/D/trials/seeds, never N).

## cardinality_ok (META_RULE_H)
EXPECTED_N_UNITS_FULL = 9 grid pts x 3 block-local arms x 3 seeds + 3 anchor-contrast arms x 3 seeds = 81 + 9 = **90**.
Verdict emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if `len(per_unit) < 90`. `cardinality_ok: true`.

## Compute architecture (mandatory declaration)
- Compute class: **(c) mixed with justification**. Block-local arms are numpy (per-block argmax = small matmul;
  the projection GSBC_DIM->bs is one fixed matmul per (point,seed)); dense-contrast arms reuse the MVP torch
  resonator. Total wall ~1-3 min (MEASURED smoke 9.4s; probes: block-local grid 5 pts x 3 arms single-seed 8.9s).
  Sequential-CPU justified: task-mandated CPU probe, no GPU, sub-10s per point, no batching speedup material.
- Storage strategy: **no_storage / no_composition-store**. Read-only on substrate; the propositions are
  synthesized per trial (block-superposition), not a chained-retrieval store. Sharded-vs-bundled n/a.

## Pre-reg SCHEMA-VET gates (sweep/composition)
- `sweep_alignment_verdict: ALIGNED` -- the swept params (V,D) are EXACTLY what each primitive experiences:
  block size bs=N/D and distractor count V are the real effective params of the per-block cleanup. No nominal/
  effective divergence (contrast: multihop_v3 partition-routing constant effective_V_C).
- `discriminating_fraction`: the sweep is a CAPABILITY MAP, not a per-point pass/fail discriminator. The
  DISCRIMINATOR is (a) noorder-collapse (MEASURED exact 1.000 vs 0.000 = fires hard), (b) synth iid ceiling
  recovers, (c) the mechanism contrast (block-local holds where dense_gsbc_fullreso collapses). The boundary
  map DOES vary (MEASURED cliff: V8192D26 exact=0.700 vs 1.000 elsewhere) so the sweep is not by-construction
  saturated. META_RULE_AG is satisfied by the noorder baseline (exact ~0, in-band-as-collapse) + the boundary
  cliff, not by requiring the deliverable to fail. `baseline_in_band: true` (noorder collapses; synth ceiling recovers).
- `composition_edges`: encode(block-superposition-sum) -> recover(per-block argmax). SHAPE_MATCH (each block
  holds exactly one factor; disjoint). No adapter needed.
- `positive_control_arms` (Gate-D): `blocklocal_synth` reproduces the proven block-local resonator
  (CITED@exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000 HARD_PASS K=26 >=85%) AT the test regime
  (bipolar sparse block codes, per-block cleanup). Tolerance: synth per_term >= 0.90 at every point (MEASURED 1.000).
  `dense_synth_fullreso` reproduces the MVP dense resonator iid ceiling AT the anchor regime.
- `functional_requirements`: (A) recover which fillers -> per-block argmax cleanup (Stage C); (B) recover their
  order -> block index (Stage B, disjoint-block position binding); (C) do both jointly from one bound vector ->
  block-superposition compose + per-block decode (Stage A). Each maps to the proven block-local resonator primitive.
- CRLB: `crlb_n_a` -- disjoint-block recovery has NO within-block superposition noise (only one factor per block);
  the argmax-noise floor that caps top-k under superposition does not apply. Within-block distractor competition
  (V codes in bs dims at cos-cone ~0.35 bipolar) is the only error source; MEASURED reachable (exact 1.000 in-box).

## Bands (envelope-fail-bands; gate on native block-local at ANCHOR V=1024 D=3, high-energy)
Deflated honestly for NATIVE fillers per memo + task ("native is harder than the stand-in; you decide").
MEASURED native exact_ordered=1.000 at anchor across probe seeds -> HP floor 0.85 is strict-above-floor.
- HARD_PASS: anchor `blocklocal_gsbc` exact-ordered >= **0.85** AND per_token >= **0.90** (AND synth ceiling
  per_term >= 0.90 AND noorder collapses: gsbc_exact - noorder_exact >= 0.50).
- HARD_FAIL: anchor exact-ordered < **0.50** (native cannot round-trip even in-box -> Stage A/C is the wall).
- MIDDLE_BAND: 0.50 <= exact-ordered < 0.85 (chunking wrapper needed beyond the GO region).
- HP_SCOPE: the exact/per_token gate applies to `blocklocal_gsbc` ONLY. `blocklocal_synth` = positive-control
  (>=0.90 floor). `noorder_ctrl` = collapse-control (no HP gate). Dense-contrast arms = informational.
- Discriminator-fires (all modes): synth ceiling recovers + noorder collapses; smoke additionally requires all
  arms run end-to-end at N=8192 + arms differ. Deliverable band is FULL-only (canonical = remote landing).

## Defensive error-checking / cell-template
- `cell_chunked: false` (single-cell multi-seed; fast, restartable within a run; no runner-zombie multi-seed loss risk given ~min wall).
- `start_marker_written: true`; `crash_diagnostic_present: true` (Exception -> CELL_CRASHED metrics + traceback);
  `heartbeat_present: true` (per grid-point/anchor `_heartbeat.jsonl`); `defensive_error_checking: passed_all_4_patterns`.
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException / bare except). Grep-gate clean.
- `arms_differ_verified: true` -- compares DISTINCT mechanism artifacts (codebooks/lexicons) + order-destruction
  divergence, NOT perfect-recovery outputs (native+synth legitimately emit the same truth tokens when both recover).
- `final_metrics_atomicity: tmp_replace`. `run_mode` written + asserted == mode (RUN_MODE verification).
- `progress_logging: line_buffered_stdout` (sys.stdout line-buffering + flush; per-point progress lines).
  `progress_cadence_expected_s: 30` (a log line per grid-point; whole run is minutes). timeout < 1800s so
  section-17 MANDATORY threshold not tripped, but flushing is present anyway.
- ASCII-only; no em-dashes; no emojis.

## Dispatch
- Smoke: local (queue_add gate). FULL: `remote_cpu_queue` via `tools/orchestrator/queue_add.sh` (SCP-based, no push).
- `--timeout 1200` (est FULL ~1-3 min; generous 5-10x margin for slower remote CPU + V=8192 projections; < 4h, no PROT justification needed).
- REQUIRED: SCP `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` to remote (untracked; queue_add does NOT ship it). Cell FileNotFoundErrors loudly if missing.
- No `_n<N>` anchor suffix (fast small-grid round-trip; PROT-018/019 opt-in, not applicable), matching the MVP.

## HYPOTHESIZED vs MEASURED
- native block-local exact-ordered at anchor: 1.000 MEASURED@probe (D3 V1024 native GSBC block-local, 3 seeds pending FULL).
- boundary cliff: V8192D26 exact=0.700 perterm=0.988 MEASURED@probe; V8192D6/1024D12/1024D26 exact=1.000 MEASURED@probe.
- dense mismatch: dense_gsbc_fullreso exact=0.000 MEASURED@MVP real_fullreso_hi + MEASURED@smoke; dense_synth_fullreso iid ceiling ~1.000 HYPOTHESIZED@R16 (smoke R4 gave 0.600).
- envelope ceiling GEN_svo_1k=1.000 MEASURED@data/exp_factorization_envelope_v1/metrics.json:results.GEN_svo_1k.mean.
- proven block-local K=26 >=85% CITED@data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json.
