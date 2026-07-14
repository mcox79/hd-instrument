# Pre-registration: map_builder_segment_library_clonal_retrieval_v1

Date: 2026-07-13. Author: exp_dev. Anchor: `map_builder_segment_library_clonal_retrieval_v1`.
Cell: `experiments/exp_map_builder_segment_library_clonal_retrieval_v1.py`.
Queue: remote_cpu_queue (device=cpu; zero SGD; one-shot Hebbian). Seeds [7,13,17]. Timeout 2400s.

## Question

Is a V(D)J-style COMBINATORIAL SEGMENT-LIBRARY construction (small typed-segment libraries combined at CONSTRUCTION
time) + POPULATION/CLONAL SOFT retrieval (the substrate's resonator/SIC-peel decode reframed as clonal selection) a
DEPLOYABLE lever that raises the recoverable-signal capacity of the inductive relational map-builder -- vs RANDOM
opaque codes and vs HARD one-shot decode -- on the held-out-entity arena? Follows the LEADING lever of
`notes/research_drillA_bio_capacity_structure_2026-07-13.md` (P_deflated=0.35): impose combinatorial structure at
construction from a small parts library + retrieve by population approximate matching, NOT single-shot algebraic
decode. Directly follows the SAME arena's residue-cell negative result (RNS_CLEAN=0.0008 ~ RANDOM = CODE-LIMITED
with arbitrary id-residue typing).

Prior-work check (substrate-KB concept-query, cosine>0.30): NONE. Top hit
`research_drill_natural_analog_immune_system_5x_2026-06-07.md::chunk008` at cosine=0.2988 (< 0.30), a lit-scan
research note on immune biology -- NOT a prior implemented cell. All 5 hits are research drill notes below 0.30. This
cell is GENUINELY NOVEL as an implementation, not a rediscovery.

DIRECTOR'S BINDING CONSTRAINT honored: segments TYPED BY REAL GRAPH STRUCTURE (relational-context fingerprint rc(e)
in R^{2*n_rel} over TRAIN+SUPPORT edges; leak-free -- never the query edge), NOT arbitrary. The residue cell typed by
(entity_id % m_k) -- an arbitrary integer residue carrying no relational structure -- which is why it was code-limited.

## Reference bars (MEASURED, on-disk)

- Monolithic opaque-atom native ORACLE by dim (O(n_dim^2) W cost): {1024:0.023083, 2048:0.118037, 4096:0.413520,
  8192:0.780600} MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.oracle_mrr_by_dim.
- Additive (SGD TransE k=24) ORACLE = 0.137293 ; realized additive compose = 0.128210
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.{ORACLE_ADDITIVE,ANCHOR_COMPOSE}.
- Residue arbitrary-id-residue ORACLE = 0.000765 (code-limited)
  MEASURED@data/exp_map_builder_residue_module_ceiling_v1/metrics.json:gates.oracle_2x2_mrr.RNS_CLEAN.

## Design

K=4 slots. 3 TYPED slots (V/D/J analog): slot k library C_k = 48 random-bipolar segments (dim d_seg=2048);
seg_k(e)=argmax_j <P_k[j], rc(e)> under a fixed random prototype matrix P_k (48 x 2*n_rel). 1 JUNCTIONAL slot (TdT
analog): seg_J(e)=hash(e)%64, weight 0.3. Per slot a REAL KGStore(n_ent=lib_k, n_rel, n_dim=d_seg) supplies C_k + a
one-shot Hebbian W_k over segment-mapped edges (seg_k(h), r, seg_k(t)). SEG W-cost = K*d_seg^2 = 16.78M; matched-cost
monolithic opaque atom at d_match=round(sqrt(K)*d_seg)=4096 (W-cost 16.78M, identical) = the same-cost bar in BOTH
regimes. SHARDED per-slot storage (each slot its own W_k) per the compositional-cell mandate.

## Two-part verdict

PRIMARY = ORACLE capacity + decode (held-out edges folded into the per-slot stores; relabeling-robust, survives
scale): does typed combinatorial-segment construction give RECOVERABLE capacity vs RANDOM and vs the residue
code-limited 0.0008 floor, and does the POPULATION soft joint decode beat the HARD one-shot per-slot argmax decode?
SECONDARY = INDUCTIVE compose (held-out codes re-assembled from support, no fold-in) + typed-assignment scramble:
does graph-structure typing give a deployable inductive lever (typing NOT params)? Reported with an inductive-lever
flag; NOT primary-gating (realized compose is inherently noisier -- type-level generalization + sparse support).
Rationale: an oracle memorizes any near-unique code, so its ceiling is nearly invariant to whether typing tracks
graph structure -- a typing scramble cannot collapse the oracle; the typing hypothesis only shows inductively.

Arms (all scored PAIRED on the same held-out QUERY edges; filtered MRR rank-vs-all-N):
MONO_PC_ORACLE (pos-control -> 0.023), MONO_MATCHED_ORACLE (capacity ceiling + oracle-fire + 1.3x bar),
SEG_SOFT_ORACLE (PRIMARY soft), SEG_HARD_ORACLE (PRIMARY hard), MONO_MATCHED_COMPOSE (realized bar),
SEG_SOFT_COMPOSE (SECONDARY soft), SEG_HARD_COMPOSE (SECONDARY hard), SEG_SCRAMBLE_COMPOSE (must-fail typed-assign
scramble), RANDOM (floor), POP (fit-independence / BROKEN guard). Internal: _SEG_RELSCRAMBLE_ORACLE (must-fail).

## Pre-registered bands (BOTH; picked before the run; NOT tuned on real data)

- ORACLE-FIRES: MONO_MATCHED_ORACLE >= 3x RANDOM AND (MONO_MATCHED_ORACLE - RANDOM) >= 0.003.
- POS-CONTROL: MONO_PC_ORACLE reproduces 0.023 within +-0.010 AND RANDOM <= 0.004.
- RECOVERABLE (PASS-side, capacity present): (SEG_SOFT_ORACLE - RANDOM) >= max(0.50*0.137, 0.010) = 0.0686.
- SOFT_BEATS_HARD (PASS-side, retrieval contrast): SEG_SOFT_ORACLE - SEG_HARD_ORACLE >= 0.010.
- LEVER (PASS-side, deployable): SEG_SOFT_ORACLE >= 1.30 * MONO_MATCHED_ORACLE.

PASS bands:
- HARD_PASS_LEVER_CONSTRUCTION_PLUS_SOFT : pos-controls hold AND oracle fires AND RECOVERABLE AND SOFT_BEATS_HARD AND
  LEVER.
- MIDDLE_BAND_MARGINAL_SEGMENT_EDGE : RECOVERABLE AND SOFT_BEATS_HARD AND MONO_MATCHED_ORACLE < SEG_SOFT_ORACLE <
  1.30*MONO_MATCHED_ORACLE.
- MEASURED_CAPACITY_PRESENT_SOFT_BEATS_HARD_NO_LEVER : RECOVERABLE AND SOFT_BEATS_HARD BUT SEG_SOFT_ORACLE <=
  MONO_MATCHED_ORACLE (capacity + soft>hard real, no sub-monolithic lever).
- MEASURED_CAPACITY_PRESENT_HARD_READS_TOO : RECOVERABLE but SOFT does not beat HARD.

FAIL band:
- HARD_FAIL_CODES_ABSENT : pos-controls hold AND oracle fires AND (SEG_SOFT_ORACLE - RANDOM) < 0.010 -> arbitrary
  labels have nothing to type; capacity absent even under fold-in (like the residue cell). Still informative: rules
  out the impose-structure-at-construction family for this task.

SECONDARY (reported, not primary-gating): inductive_lever = compose_recoverable (SEG_SOFT_COMPOSE - RANDOM >= 0.010)
AND compose_soft_beats_hard (>= 0.010) AND scramble_collapses (SEG_SOFT_COMPOSE - SEG_SCRAMBLE_COMPOSE >= 0.020).

Gated INCONCLUSIVE if oracle does not fire, pos-controls fail, too few held-out queries, or POP beats RANDOM (BROKEN;
guard validated vs the RANDOM/arm floor per Gate F.4).

## Compute architecture

class (b) sequential-CPU, justified. One-shot Hebbian (no SGD, no epochs). Per seed: 4 fold-in + 4 train-only + 4
scrambled train-only segment stores (d_seg=2048) + monolithic d=1024 (pos-control) + d=4096 fold-in + d=4096
train-only = 15 real KGStore ingests. Decode = per-slot (nq x lib_k) similarity + O(nq*N*K) gather (sub-quadratic).
Residue sibling (12 stores + 8 arms) ran 3 seeds on device=cpu in 623s; this is comparable -> <~1200s. remote_cpu.
progress_logging: print_flush_true (line-buffered + per-seed/per-slot flush + heartbeat).

## Gate F / schema-vet declarations

- real_code_path (F.1): self-test constructs the REAL KGStore per slot + runs ingest_triples on segment-mapped
  triples (`_selftest_real_store_smoke`); exercised entrypoints = {KGStore, build_segment_module, ingest_triples,
  module_segment_sims}.
- substrate_signature (F.2/F.3): KGStore bound with BASE/portable kwargs only (n_ent,n_rel,n_dim,generator); no
  optional init_entities.
- guard_baseline_valid (F.4): BROKEN(POP>RANDOM) guard validated vs the RANDOM/arm floor (MONO_MATCHED_ORACLE above
  floor), not a structural-zero POP.
- arms_differ (AF): >=5 distinct score signatures per seed asserted.
- cardinality (H): EXPECTED_N_UNITS = n_seeds; per-seed all-arms + finite-W asserted; cardinality breach fail-closed.
- except SystemExit before except Exception; no bare except / no BaseException (grep-gated).
- final_metrics_atomicity: tmp_replace via _seed_checkpoint.write_metrics.
- calibration_check: default_ok_for_this_regime (all slot/lib/dim/frac/weight/tol pre-registered; CSKG split copied
  verbatim from the native + additive + residue arenas).
- VALIDITY_PREFLIGHT_MODE=enforce: 7 checks declared (positive_control, metric_moves, negative_control_margin,
  full_gates_exercised, real_code_path_F1, substrate_signature_F2_F3, guard_baseline_valid_F4).

## Smoke (self-test) result

SELFTEST_PASS under VALIDITY_PREFLIGHT_MODE=enforce (0.1s). Planted type-structured arena:
SEG_SOFT_ORACLE=0.439 >> SEG_HARD_ORACLE=0.335 >> RANDOM=0.022 (soft-random=0.417, soft-hard=0.105);
relation-scramble oracle collapses to 0.138 (soft-relscr=0.302); compose directional sanity holds (SEG_SOFT_COMPOSE
0.055 - RANDOM 0.022 = 0.033); arms_differ (uniq_frac=0.9); all 7 validity-preflight checks pass; real KGStore
segment path exercised. run_mode=self_test verified on the landed metrics.
