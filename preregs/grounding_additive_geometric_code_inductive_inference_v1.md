# PRE-REG: exp_grounding_additive_geometric_code_inductive_inference_v1

**Cell:** `experiments/exp_grounding_additive_geometric_code_inductive_inference_v1.py`
**Anchor:** `grounding_additive_geometric_inductive_v1`
**Author:** exp_dev  **Date:** 2026-07-09
**Source pre-reg (mechanism/bands):** `notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md`
(the ADDITIVE-GEOMETRIC code mechanism half of the shared inductive-inference floor; Lippl, Kay, Jensen,
Ferrera & Abbott 2024 PNAS -- norm-minimizing learning converges on additive rank codes where a novel relation
is read off geometrically). Reuses the #4 held-out construction (`exp_graph_inductive_ceiling_v1`, commit 84f46d6)
+ the learned-SR held-out split methodology (`exp_grounding_learned_sr_heldout_reasoning_v1`).

**Prior-work check (substrate KB):** substrate_query "additive geometric relation code TransE held-out inductive
inference h+r=t knowledge graph embedding" -> top hits cosine 0.31/0.30 are the cross-domain-analogy NEGATIVE 2x
drill (relation disambiguation via active inference) + a Path-C encoder note listing "Field 3: KGE for relation
types (TransE/RotatE/ComplEx/TransERR)" at 0.285. Adjacent (KGE mentioned as a candidate relation-code family) but
NO prior cell runs the DISCRETE-binding-vs-ADDITIVE-geometric HELD-OUT-inductive comparison. Genuinely novel
mechanism cell (does additive geometry enable inference the current HRR-binding codes cannot?), NOT a rediscovery.

## Claim
The substrate's current DISCRETE code is HRR MULTIPLICATIVE binding (entity codes Z from char-trigram features;
typed relations are fixed unitary HRR roles; score(h,r,t) = cosine(hrr_bind(role_r, Z_h), Z_t)) -- it has NO
additive-geometric structure, so it can traverse-known but ties random on HELD-OUT inductive inference (the #4-VET
resolved finding: learned-SR held-out margin ~0.011 over random; SIGNAL_EXISTS(>=0.85)=False for every method incl
a GNN). This cell tests whether a self-contained ADDITIVE-GEOMETRIC code (TransE h+r~=t, learned from the graph's
OWN visible edges, NO external model) INFERS held-out typed edges MATERIALLY above the discrete-code baseline AND
above random -- i.e. whether the additive-geometric MECHANISM is the inference lever the binding codes lack.

## Arms (all learn from VISIBLE typed edges only; leakage-safe; scored on WITHHELD triples via filtered tail-ranking)
- **DISCRETE_HRR_BIND** (ARM A, current mechanism): char-trigram -> ProjHead -> L2 codes + HRR role-bind, trained
  with the substrate's own binding-consistency InfoNCE. Multiplicative; no additive read-off. Expected to tie random.
- **TRANSE_ADDITIVE** (ARM B, mechanism under test): entity vectors E + relation VECTORS R, margin-ranking on
  visible edges (min ||E_h + R_r - E_t||_1 vs corrupted tails), NORM-MINIMIZED (weight_decay=1e-3, moderate dim=64,
  no sphere-renorm). Infer held-out GEOMETRICALLY: score t by -||E_h + R_r - E_t||_1. Self-contained.
- **DISTMULT_BILINEAR** (ARM C): learned MULTIPLICATIVE KGE <E_h,R_r,E_t>. Isolates "additive geometry specifically"
  from "any learned KGE" -- if DISTMULT also infers held-out well, the lever is not additive-specific.
- **RANDOM_CODES** (control): untrained TransE codes -> chance floor + codes-necessary control.
- **TRANSE_TRANSDUCTIVE** (oracle / discriminator-fires): TransE trained WITH held-out visible; MUST recover held-out
  tails (pipeline works, question well-posed). If oracle ties random -> INCONCLUSIVE (setup broken).

## Primary metric
`reach@1` = filtered Hits@1 on the DETERMINATE/COMPLETABLE held-out subset (withheld typed triple (h,r,t) whose head
h AND tail t both appear in the visible graph AND relation r appears in visible edges -- so a transductive code CAN in
principle place it; the fair-test refinement from the #4 audit). Also MRR + Hits@3/10 (reported).

## Discriminator (pre-registered; primary = TRANSE_ADDITIVE reach@1 on completable held-out subset)
- **HARD_PASS_GEOMETRY_ENABLES_INFERENCE** = transe_hits1 >= discrete_hits1 + GEOM_MARGIN(0.10) AND
  transe_hits1 >= random_hits1 + GEOM_MARGIN(0.10) -> additive-geometric mechanism is the self-contained inference
  lever the binding codes lack.
- **HARD_FAIL_GEOMETRY_DOES_NOT_INFER** = transe_hits1 <= discrete_hits1 + TIE_EPS(0.02) AND
  transe_hits1 <= random_hits1 + TIE_EPS -> geometry alone does not infer either -> the limit is deeper (knowledge /
  cross-domain, not code geometry). NOTE: given #4-VET (all methods at the graph's ceiling), HARD_FAIL is the
  DEFENSIBLE prior; the naming follows the pre-reg, not desirability.
- **MIDDLE_BAND_PARTIAL_GEOMETRIC_INFERENCE** = otherwise (beats one of {discrete, random} by margin but not both,
  or beats by < margin) -> partial geometric inference.

Reported (never gated): per-arm Hits@1/3/10 + MRR, transe-vs-{discrete,random,distmult} deltas, DISCRETE far-negative
edge AUC (paired M5 ~0.70 reproduction), oracle Hits@1, n_completable / n_heldout / withheld_frac.

## Discriminator-fires / anti-triviality gates (INCONCLUSIVE if any fail)
- `enough_completable`: n_completable >= 60.
- `negatives_valid`: RANDOM reach@1 <= 0.15 (if random ranks held-out tails, the negatives are trivial).
- `oracle_fires`: TRANSE_TRANSDUCTIVE reach@1 >= random + 0.15 (the ranking machinery recovers seen edges).

## Bands (numeric, picked BEFORE the run)
`GEOM_MARGIN=0.10  TIE_EPS=0.02  RANDOM_CEIL=0.15  ORACLE_FIRE_MARGIN=0.15  HELDOUT_FRAC=0.30
MIN_HELDOUT_COMPLETABLE=60  N_RANK_NEG=99  KGE_MARGIN=1.0  KGE_NEG=15  KGE_WD=1e-3  kge_dim=64`

## Number provenance (META_RULE_AC)
- #4-VET held-out signal absent (learned-SR margin ~0.011; SIGNAL_EXISTS=False incl GNN)
  CITED@notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md
- phase-0 M5 held-out edge AUC 0.6945 @ n=1237  MEASURED@data/phase0_code_structure_precheck_result.json:per_size[0].M5_heldout_auc
- filtered Hits@1 chance floor = 1/(N_RANK_NEG+1) ~ 0.01  THEORETICAL
- additive-generalization requires norm-minimization + low-conjunctivity (weight decay + moderate dim), plain
  high-dim margin-TransE MEMORIZES  CITED@Lippl/Kay/Jensen/Ferrera/Abbott 2024 PNAS 121(28)
- self-test measured regime (norm-minimized, dim=64): additive held-out Hits@1 ~0.33, non-additive ~0.00, random ~0.01
  MEASURED@self-test (tuning probes /tmp; reproduced by `--self-test` at each dispatch)

## Self-test (mechanism; proves the metric DETECTS additive-geometric inferability and is NULL otherwise)
ADDITIVE planted graph = entities at latent scalar positions on a LINE (canonical additive-rank / transitive-
inference code, Lippl et al.); each relation = a fixed integer offset; edge (h,r,t) iff pos_t = pos_h + offset_r;
entity NAMES are random hashes uncorrelated with position (so the discrete char-feature arm carries no additive
signal). NON-ADDITIVE planted graph = each relation is a RANDOM bijection (no consistent offset). Asserts (measured
`--self-test` PASS 10.7s): TransE recovers additive held-out (Hits@1 0.333 >= 0.25), random fails (0.010 <= 0.10),
TransE null on non-additive (0.000 <= 0.15), gap 0.333 >= 0.20, arms differ. Run at the SAME kge_dim (64) the real
arms use -> discriminator-survives-scale validated at the real embedding dim.

## SCHEMA-VET checklist
- `arms_differ_verified`: True (>= 4 distinct arm score signatures per seed asserted; else ARMS_MUST_DIFFER_META_RULE_AF).
- `final_metrics_atomicity`: tmp_replace (write_metrics + os.replace; write_partial per seed).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException / no bare except) -- grep gate CLEAN.
- `crlb_floor_computed`: 0.01 (=1/(N_RANK_NEG+1)); `crlb_formula_reference`: filtered Hits@1 chance = 1/(neg+1);
  `discriminator_reachability`: True (HARD_PASS transe>=random+0.10 achievable; self-test additive arm = 0.33).
- `baseline_in_band`: RANDOM is the anti-triviality null (must be <= 0.15; near chance ~0.01 = correct); ORACLE is the
  must-fire control (>= random + 0.15). (The mechanism arm TRANSE is the measurement, not a saturating baseline.)
- `cardinality_ok`: True; EXPECTED_N_UNITS = n_seeds (2 smoke / 3 full); HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if <.
- `discriminator survives scale`: self-test fires the additive-vs-non-additive discriminator at the real dim=64;
  real-graph outcome is the open measurement. Smoke previews on real graph (2 seeds n=1800); FULL (3 seeds n=5000).
- `HP_SCOPE`: geometry-enables-inference gate applies to TRANSE_ADDITIVE only; DISCRETE=ARM A baseline; RANDOM=null;
  ORACLE=positive-control must-fire; DISTMULT=reported control.
- `positive_control_arms` (Gate D): TRANSE_TRANSDUCTIVE reproduces the known transductive-KGE result (recovers held-out
  tails when the edge was visible; Hits@1 >> random). Secondary: DISCRETE far-negative edge AUC reproduces phase-0 M5
  ~0.69 within 0.12 on the same 30% held-out split (paired code-baseline reproduction at the test regime).
- `sweep_alignment_verdict`: ALIGNED (no routed effective-parameter; the completable filter is applied identically to
  all arms; sweep axis = arm x seed).
- `discriminating_fraction`: N/A as a threshold sweep; the self-test demonstrates the additive arm lands in a
  discriminating band (0.33) while non-additive/random are at floor (0.00/0.01) -> the metric separates.
- `composition_edges`: none (each arm is a single primitive: KGE embeddings, or char->ProjHead->HRR-bind); no
  primitive->primitive composition -> no SHAPE_MISMATCH.
- `functional_requirements`: (1) infer a held-out typed relation between KNOWN entities -> mapped to a NEW additive-
  geometric KGE mechanism (TransE) vs the existing HRR-binding primitive; both learn from visible edges only.
- `calibration_check`: default_ok_for_this_regime (HELDOUT_FRAC + completable filter + far-neg inherited from
  phase-0/#4; KGE hyperparams are pre-registered standard regularized-KGE defaults, NOT tuned on real data; the
  planted self-test verifies they generalize additive held-out and NOT non-additive).
- `paired_trials`: True (all arms share the identical held-out split + completable subset + candidate negatives/seed).
- `cell_chunked`: False (in-cell multi-seed with per-seed try/except + write_partial checkpoint; fast cell, seconds/
  seed on GPU; matches the two reused sibling cells graph_inductive_ceiling_v1 + learned_sr_heldout_v1). start_marker
  + crash_diagnostic + heartbeat present.
- `start_marker_written`/`crash_diagnostic_present`/`heartbeat_present`: True.
- `run_mode` verification post-dispatch: expect run_mode=full, elapsed>1s, size>5KB (per-seed/per-arm data).
- `progress_logging`: print_flush_true (line-buffered stdout + per-seed/per-arm/per-epoch flush prints).

## Compute architecture
class: (a) batched-GPU. KGE (TransE/DistMult) = embedding-lookup + vectorized L1/bilinear margin loss over edge
mini-batches (no python-loop matmul over independent points); discrete arm reuses batched train_binding_encoder_dev;
filtered tail-ranking builds a shared [nq, K, dim] candidate tensor scored by one batched reduction per arm (PAIRED
candidates). n<=5000, dim=64, T~16, E~15k -> seconds/seed on GPU. Storage strategy: SHARDED (each entity its own
embedding/code vector; no bundling). Routes to overnight_queue (GPU) for FULL per Director (GPU-heavy KGE). Smoke on
laptop CPU (smoke-only local, USER-locked).

## Dispatch
- Smoke: local CPU, --smoke, 2 seeds n=1800 (this file's smoke gate).
- FULL: overnight_queue (GPU), 3 seeds n=5000. queue_add command returned to orchestrator (exp_dev does not SCP-ship).
