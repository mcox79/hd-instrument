# Pre-registration: Structure-Aware Encoder Sharpness (barrier #1 / M3-M5 diagnostic)

- anchor_name: `exp_encoder_structure_aware_sharpness_v1`
- core: `experiments/exp_encoder_structure_aware_sharpness_v1_core.py`
- per-seed wrappers (CHUNKED single-seed-per-cell): `_seed_7.py`, `_seed_13.py`, `_seed_19.py`
- date: 2026-07-09
- author: exp_dev
- target queue: `overnight_queue` (GPU; encoder training is GPU-batched matmul-heavy)

## Question

Does a STRUCTURE-AWARE encoder objective produce SHARPER codes that unlock reasoning-generalization? Attacks
barrier #1 (the encoder). The substrate's CURRENT InfoNCE/semantic codes carry the graph map only MODERATELY:
- M3 (code-cosine predicts 1-hop edge) AUC ~0.87  MEASURED@data/phase0_code_structure_precheck_result.json:per_size[1].M3_1hop_auc_full (n=4440)
- M5 (HELD-OUT-edge AUC = reasoning-generalization ruler) ~0.695  MEASURED@data/phase0_code_structure_precheck_result.json:per_size[1].M5_heldout_auc (n=4440)
- M5 does NOT improve with graph size (size_flat, deltaM5=-0.050 across n=1237->7895)  MEASURED@data/phase0_code_structure_precheck_result.json:SIZE_VERDICT

Diagnosis: reasoning bottleneck = encoder SHARPNESS (codes carry structure faintly, not too-small a graph).
Fix hypothesis: a structure-aware objective (node2vec/DeepWalk random-walk skip-gram from the graph's OWN
adjacency; self-contained, no external model) makes code-cosine SHARPLY track graph reachability.

## Arms (all measured on L2-normalized codes; reuse phase-0 M1-M5 computation VERBATIM)

- `A_baseline_semantic`  : CURRENT encoder = `train_binding_encoder_dev` (edge-InfoNCE + VICReg + HRR-bind over
  char-trigram features). REFERENCE ARM. Reproduces phase-0.
- `B_struct_node2vec`    : DeepWalk/node2vec skip-gram + negative sampling over a learnable node-identity
  embedding table. PURE graph structure; no semantic features. Self-contained (graph adjacency only).
- `C_hybrid_walk_semantic`: ProjHead over char-trigram features (semantic input) trained with the WALK-window
  co-occurrence objective (structure objective). Structure-aware over semantic input.

"structure-aware candidate" = best-of(B, C) on M5 (the structure-aware objective FAMILY unlocking generalization).

## Metrics

- M1 per-hop mean code-cosine (monotonic decrease 1>2>3 = structure)
- M3 1-hop edge-detection AUC (cosine ranks true edges above hop>=3 non-edges)
- M4 code-kNN mean graph-hop vs random (ratio << 1 = code neighbors are graph-near)
- M5 HELD-OUT-edge AUC (leakage-safe: encoder trained on kept 70% edges; withheld 30% genuinely unseen). DECISIVE.
- Downstream held-out reasoning: for withheld edges (u,v), rank all nodes by cosine(Zh[u], .); reach@10 + MRR
  of the true unseen target v ("route to the held-out neighbor"; inductive-KG-completion discriminator).

## Compute architecture

- class: (a) batched-GPU. node2vec skip-gram = embedding lookups + batched dot-products (bmm over negatives);
  baseline reuses device-aware `train_binding_encoder_dev`. All arms train on `torch.device('cuda')` on the GPU box.
- storage strategy: `no_composition` (encoder-training + metric cell; NO substrate/PartitionedStore writes).
- device default `auto` -> cuda if available else cpu; runner injects HDLAB_RUN_MODE=full.

## Pre-registered bands (evaluated at CANONICAL size n~4440, matching phase-0 baseline)

- HARD_PASS: best-of(B,C) M5 >= baseline_A M5 + 0.10 (i.e. ~0.70 -> >=0.80) AND downstream reach@10 delta
  >= +0.05 vs baseline. -> sharper structural encoder unlocks generalization (path through barrier #1).
- HARD_FAIL: best-of(B,C) M5 <= baseline_A M5 + 0.03. -> structure-aware objective does NOT sharpen the
  reasoning-relevant map (deeper limit than the encoder objective).
- MIDDLE_BAND: between (+0.03 < deltaM5 < +0.10, or deltaM5>=0.10 but downstream reach delta < +0.05).
- HP band strictly above the HF floor by +0.07 (META_RULE_L; +0.10 target, +0.03 fail).
- HP_SCOPE: HARD_PASS/HARD_FAIL gates apply ONLY to structure-aware arms (B, C) relative to baseline (A).
  Arm A is the reference; it inherits NO pass/fail gate (it reproduces phase-0 by construction).

## Feasibility / reachability

- crlb_n/a: discriminator is an AUC / retrieval-rank quantity; no closed-form Cramer-Rao noise floor applies.
  Feasibility instead validated by the planted-graph self-test (node2vec must hit M3>=0.90, M5>=0.75 on clean
  structure) + the baseline-headroom guard (baseline M5 <= 0.90 leaves room for a +0.10 win; AUC max 1.0).
- baseline_in_band: phase-0 baseline M5 = 0.695-0.731 (0.55 < M5 < 0.90) -> +0.10 win is reachable, not saturated.
- discriminator_reachability: True (baseline 0.70 + 0.10 = 0.80 <= 1.0 AUC ceiling).

## Discriminator-survives-scale

- (B) planted self-test: node2vec achieves M3=0.994 / M5=0.945 on a clean SBM  MEASURED@self-test log (this cell).
  Untrained random-code control M3=0.492 fails the M3>=0.90 gate (discriminator fires; metric is not by-construction).
- (C) smoke preview: run at n=1237 previews the A/B/C M5 gap + enforces baseline-headroom (M5<=0.90) so a
  saturated (vacuous) smoke HARD-fails loudly. FULL runs at canonical n=4440 + n=7895 (multi-seed).
- NOTE (methodological, load-bearing): the semantic baseline arm is itself an EDGE-InfoNCE structural learner;
  on a clean dense-block SBM it ALSO generalizes to held-out edges (M5~0.95). So the A-vs-B/C discriminator has
  teeth ONLY on the real, messy KB graph (where baseline is stuck ~0.70). Planted graph tests mechanism
  correctness, NOT the A-vs-B gap; the gap is the FULL run's science on the real graph.

## SCHEMA-VET checklist

- cardinality_ok: EXPECTED_N_UNITS = len(sizes) * len(arms) = 2 * 3 = 6 (FULL); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if n_units != expected.
- arms_differ_verified: hash-test over per-size code matrices (META_RULE_AF); smoke raises on bit-identical arms.
- final_metrics_atomicity: `tmp_replace` (write_metrics + inline crash writer both os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException); grep-clean of bare `except:`.
- calibration_check: `default_ok_for_this_regime` (BASE_CFG reproduces phase-0 baseline verbatim; same loader,
  same encoder, same M1-M5 computation copied verbatim from phase-0 precheck).
- cell_chunked: true (per-seed wrappers; one process = one seed; runner-death loses only that seed).
- start_marker_written: true. crash_diagnostic_present: true (CELL_CRASHED + traceback, atomic).
- heartbeat_present: per-epoch progress log lines (flush=True) from train_* fns; runner python -u.
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: `print_flush_true` (all `_log` lines flush=True; sys.stdout line_buffering at entry).
  timeout_s >= 1800 for FULL -> this field is mandatory and satisfied.

## Positive control (Gate D)

- positive_control_arm: `A_baseline_semantic` reproduces phase-0 baseline at the test regime.
  - cited_prior_metric M3 = 0.874, M5 = 0.695  MEASURED@data/phase0_code_structure_precheck_result.json (n=4440)
  - tolerance 0.06 (identical loader/encoder/cfg; drift beyond = rail FAIL flag in landed-VET)

## Timeout

- FULL per seed: 2 sizes x 3 arms x 2 (full + held-out) = 12 encoder trainings. Baseline 80 epochs;
  node2vec/hybrid ~5 walk-epochs. On GPU est. 12-25 min/seed. Timeout set to 5400s (90 min) with margin.

## Verdict claim (HYPOTHESIZED, pre-run)

- Expectation: hybrid (C) most likely to win (semantic features + structure objective); pure node2vec (B) may
  LOSE on low-degree nodes whose only edges are withheld (unvisited-row boundary, CITED@ research note). Any
  outcome is informative and pre-registered above. HYPOTHESIZED@this prereg; MEASURED values from FULL only.
