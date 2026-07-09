# Pre-reg: grounding_binding_structured_encoder_multihop_v1

Anchor: `grounding_binding_structured_encoder_multihop_v1`
Cell: `experiments/exp_grounding_binding_structured_encoder_multihop_v1.py`
Date: 2026-07-09
Author: exp_dev
Stage: 3 (compositional understanding / grounding)
Lineage: BUILD #1 follow-up (master map `research_MASTER_MAP_language_acquisition_biology_to_substrate_2026-07-09.md`);
closes the UNTESTED gap of `grounding_bind_chain_systematicity_v1` (60f40852a) whose reach-deepening ran over a
losslessly-recovered synthetic graph + an oracle ridge on real codes -- never the ACTUAL learned encoder.

Prior-work check (substrate-KB concept-query, `binding-structured encoder typed relation bind at encode time
multi-hop grounded attribute reach`): top hit `encode`=0.29; remainder encoder-drift/production notes. NONE at
cosine>0.30. Genuinely novel; not a rediscovery.

## THE QUESTION (real-substrate, no oracle / no reconstructed-true-graph)
If typed-relation binding is folded INTO the concept code at ENCODE time (a binding-structured encoder vs the
baseline similarity-trained encoder), does the SAME grounded-attribute reach probe -- run on the ACTUAL learned
codes, over a graph RECOVERED FROM THOSE CODES -- extract multi-hop grounded-attribute reach PAST 1 hop, above
the similarity-encoder's ~1-hop cap? P genuinely uncertain; both outcomes gold.

## MECHANISM
- BINDING encoder = ProjHead + base neighbor-InfoNCE + VICReg PLUS a typed-binding-consistency InfoNCE:
  `bind(role_r, z_i)` must land on the r-typed neighbour `z_j` (in-batch negatives). Roles = fixed UNITARY HRR
  vectors (one per real ConceptNet `rel_type`; 16 types). Binding op = hdlab.binding HRR real path (verified
  bit-identical to `np_hrr_bind` in selftest). Folds typed relations into the code at encode time.
- BASELINE encoder = plain neighbor-InfoNCE + VICReg (the established ~1-hop similarity encoder; snowball pipeline).
- Reach probe (IDENTICAL structure for all arms): recover an adjacency FROM the learned codes, then D-step clamped
  label-propagation of a graph-smooth grounded attribute from sparse seeds; per-TRUE-distance-bin ordering acc;
  effective reach = farthest contiguous bin with smooth acc >= REACH_THRESH(0.55) AND margin over shuffled >=
  MARGIN_FLOOR(0.05), non-collapsed (over-smoothing gated). REACH_THRESH/MARGIN_FLOOR imported from bind-chain.
- Recovery from codes: score matrix S then directed top-k above a codebook-size-aware crosstalk floor
  `c*sqrt(2 ln n / d)` (c=1.1), union-symmetrized. Cosine read: `S=cos(z_i,z_j)`. Role read:
  `S[i,j]=max_r cos(bind(role_r,z_i), z_j)` (encode-time-binding NATIVE read).

## ARMS + HP_SCOPE
- `BASELINE_COSINE` : similarity encoder, cosine read -- the 1-hop CAP (baseline_in_band gate applies).
- `BASELINE_UNBIND` : similarity encoder, role read -- CONTROL (unbind needs encode-time binding -> must be garbage).
- `BINDING_UNBIND`  : binding encoder, role read -- PRIMARY treatment (reach gates apply here).
- `BINDING_COSINE`  : binding encoder, cosine read -- robustness (does binding help under identical cosine read).
- SHUFFLED attribute is the per-arm genuineness control (must stay flat; margin gate).

## PRE-REGISTERED BANDS (picked BEFORE the FULL run)
HARD_PASS (real win the bind-chain cell could not claim):
- reach(BINDING_UNBIND) >= 2 (REACH_HP_MIN)
- AND reach(BINDING_UNBIND) - reach(BASELINE_COSINE) >= 1 (REACH_DELTA_HP)
- AND newly-reached bin acc >= REACH_THRESH + 0.01 with margin over shuffled >= MARGIN_FLOOR (majority of seeds)
- AND non-collapsed at d_star
- AND baseline cap present (reach(BASELINE_COSINE) <= 1) AND bind recovery_ok (recall >= 0.20)
HARD_FAIL (deeper encoder-architecture finding):
- reach(BINDING_UNBIND) - reach(BASELINE_COSINE) <= 0 (encode-time binding as implemented does not make
  multi-hop grounding extractable on real learned codes)
MIDDLE_BAND: extension present but band-floor / not strictly above floor.
Guard verdicts: PRECONDITION_FAIL (attr not graph-smooth); INCONCLUSIVE_NO_ONESHOT_CAP (baseline reach > 1 ->
no fair contrast); INCONCLUSIVE_RECOVERY_FAILED (role recovery recall < 0.20 -> unattributable).

## SCHEMA-VET FIELDS
- cell_chunked: false (single-cell multi-seed; per-seed try/except + cardinality gate + write_partial)
- start_marker_written: true ; crash_diagnostic_present: true ; heartbeat_present: true (during encoder training)
- defensive_error_checking: passed_all_4_patterns
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace)
- arms_differ_verified: true (2 encoders hash-checked bit-differ; 4 reach-curve digests reported; warn-if-identical)
- cardinality_ok: true ; EXPECTED_N_UNITS = n_model_seeds (self_test 1 / smoke 2 / full 3); D-sweep coverage within seed
- crlb_n/a: "ordering-acc chance = 0.5; discriminator is shuffled-gated + over-smoothing-gated effective reach,
  not a closed-form estimator noise floor"
- discriminator_reachability: true (selftest: planted binding-chain -> role reach 4 vs cosine -1; recall_role 1.0
  vs recall_cos 0.0; telemetry-sensitive: shuffling codes drops recall to ~0.01)
- baseline_in_band: verified at smoke (BASELINE_COSINE reach = 1, cap present; not saturated)
- calibration_check: adaptive_with_discriminator_gate (crosstalk floor = codebook-size-aware
  c*sqrt(2 ln n / d), principled extreme-value criterion applied IDENTICALLY to all arms; shuffled null per run;
  over-smoothing collapse gate proven to fire; selftest still fires after the floor calibration)
- effective_vs_nominal_parameter_audit: swept param D (propagation depth) -- effective = nominal (no partition
  routing); sweep_alignment_verdict: ALIGNED
- discriminating_fraction: reach arms span reach in {-1,0,1,2,...}; at smoke arms landed {BASE_COS=1, BASE_UNB=-1,
  BIND_UNB=1, BIND_COS=1.5} -> spread across the band, not saturated
- composition_edges: encoder -> code-recovery -> propagation; SHAPE_MATCH (codes [n,d] -> adjacency -> scalar field)
- positive_control_arms: BASELINE_COSINE reproduces the snowball ~1-hop cap AT THIS regime (real subgraph);
  BASELINE_UNBIND is the encode-time-binding-necessity control
- functional_requirements: (1) recover relational structure from learned codes [cosine / role-apply cleanup];
  (2) propagate grounded attribute multi-hop [propagate_field]; (3) distance-decay + shuffled genuineness gate
- progress_logging: print_flush_true (flush=True in _log + line_buffered stdout + heartbeat during training)
- HYPOTHESIZED vs MEASURED marking below

## COMPUTE ARCHITECTURE
Class (c) mixed CPU with justification. Encoder training = 2 tiny ProjHeads (torch CPU; sequential epoch
dependency). Recovery = numpy BLAS matmuls (n^2*d per role; BLAS-parallel). Propagation = python label-spreading
(sequential graph diffusion). Total FULL wall estimated ~5-10 min (smoke 8.2s at n=1525/2seeds; FULL ~30-40x).
Storage strategy: no_storage (no bundled/sharded item memory; codes are per-node vectors). Wall < 10 min ->
GPU batching not warranted (numpy BLAS already parallel; GPU port would add complexity for a few-minute cell).

## SMOKE EVIDENCE (MEASURED@data/exp_grounding_binding_structured_encoder_multihop_v1_smoke/metrics.json)
- verdict: HARD_FAIL_NO_EXTENSION (run_mode=smoke, 2 seeds, 8.2s, 28.9KB)
- reach(eff, mean): BASELINE_COSINE=1.00 (cap present) | BASELINE_UNBIND=-1.00 (control garbage, recall 0.005) |
  BINDING_UNBIND=1.00 (PRIMARY) | BINDING_COSINE=1.50 (seed7=2, seed13=1)
- reach_delta(BINDING_UNBIND - BASELINE_COSINE) = 0.00 ; strict_above_floor=False
- recovery edge_recall: base_cos=0.465 base_unbind=0.005 bind_unbind=0.294 bind_cos=0.410 ; bind precision=0.175
- attr_assort smooth=0.671 shuf=0.005 (precond OK) ; subgraph n=1525 E=4262 med_deg=3.0 rel_types=16
- selftest: MEASURED ok=True reuse_ok unitary_ok recovery_fires reach_fires telemetry_sensitive (reach_role=4,
  reach_cos=-1, recall_role=1.0 vs recall_cos=0.0, recall_perm=0.01)
INTERPRETATION: smoke is a VALID gate clear (baseline cap present, controls correct, discriminator fires,
recovery clean at precision 0.175). Smoke-scale verdict = HARD_FAIL (binding's native unbind does not extend
reach past baseline at n=1525/d=128/45ep). FULL tests whether the gap OPENS at d=256/n=5000/100ep (larger d
sharpens unbind cleanup SNR; BINDING_COSINE reaching 2 on one smoke seed hints latent multi-hop structure).
All smoke numbers above are MEASURED; FULL outcome HYPOTHESIZED uncertain (P~0.30-0.45 either direction).

## HONESTY FRAMING
Real-substrate multi-hop grounded-attribute PROPAGATION on learned codes. NOT "language understanding", NOT
"grounding solved". Grounded scalar is a synthetic graph-smooth field over the REAL ConceptNet subgraph (honest
stand-in for a measured attribute). PASS = necessary (not sufficient) recipe: encode-time typed binding makes
multi-hop grounded propagation extractable past the similarity 1-hop cap. FAIL = encode-time binding as
implemented is not enough on real learned codes -> deeper encoder-architecture question (NOT a substrate ceiling).

## DISPATCH
Queue: remote_cpu_queue (CPU cell; local is smoke-only per USER lock; GPU not warranted). Timeout: 5400s.
Cell defaults run_mode=full (defensive per SCHEMA-VET 16); expect landed run_mode=full, size >5KB, elapsed >1s.
