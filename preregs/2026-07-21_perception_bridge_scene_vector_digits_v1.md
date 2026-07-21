# Pre-reg: perception_bridge_scene_vector_digits_v1

Date: 2026-07-21. Author: exp_dev. Store: LOCAL only (no push / no remote-persist).
Cell: `experiments/exp_perception_bridge_scene_vector_digits_v1.py`

## Question
Does the mechanism `pixels -> recognize object -> CONCEPT atom -> bind to LOCATION -> bundle into
ONE scene vector -> query/factor -> ground to symbol` work, and what is its object-capacity bound?
Seed of the USER's NEST@location + EGGS@location symbolic-scene representation, using sklearn
load_digits as PROXY objects (honest: no object-labeled data locally).

## Prior-work check (KB + filesystem)
- `resonator_factorization_v1` (cosine 0.38, HARD_FAIL): synthetic FHRR factoring, NO perception.
- `pp406_visual_scene_factor_separation` (resonator + explain-away): SYNTHETIC attribute codebooks,
  NO pixels. Closest prior for the factoring machinery.
- `image_hd_encoder_digits_v1` (atom 29407): pixels->HD recognition, NO scene / location-binding / query.
NOVEL COMPOSITION: bridges real-pixel perception into a location-bound scene vector + query + grounding.
None combine perception + scene-binding + symbol-grounding. Credited + reused, not rediscovered.

## Representation
`SCENE = sum_j bsc_bind(CONCEPT_{recognized_j}, LOCATION_{cell_j})` (real-valued superposition; single
vector). CONCEPT_d = digit-d SYMBOL atom (10 near-orthogonal random bipolar). LOCATION = 6x6=36 grid
atoms. Perception (record encoder, N_perc=4000) maps pixels -> class d -> writes CONCEPT_d. The CONCEPT
atom IS the symbol atom => that identity is the grounding.

## Config
N_perc=4000, N_scene=128, grid 6x6 (G=36), 10 concepts, K in [1,2,3,4,6,8,12,16,20,24,28,32,36],
n_scenes full=150 / smoke=25. N-lever [96,128,192,256] at K=28.

## Bands (envelope-fail)
- PASS: small-K (mean K in {1,2,3}) loc->concept(vs recognized) >= 0.85 AND concept->loc >= 0.70 AND
  cross-modal symbol query >= 0.70 AND scramble collapses (<=0.25 AND clean-scramble delta >= 0.30)
  AND capacity degrades (acc(K=1) - acc(K=36) >= 0.15).
- HONEST_NEGATIVE: small-K loc->concept <= chance+0.15 OR scramble doesn't collapse OR no K-degradation.
- MIDDLE_BAND: otherwise.
- Chance: concept 0.10, location 0.028.

## Can-fail controls (MUST fire at smoke; verified)
(a) SCRAMBLE: fixed permutation of the scene vector destroys bind alignment -> query -> chance.
    MEASURED@smoke scramble=0.082, delta=0.918, collapsed=True.
(b) CAPACITY K-sweep: query + resonator accuracy degrade with K (crosstalk / superposition catastrophe).
    MEASURED@full loc->concept 1.000(K<=4) -> 0.648(K=36), degrade=0.352.

## CRLB / feasibility
Real-valued superposition: true-concept unbind dot = N_scene (deterministic); distractor dot ~ N(0, K*N);
knee at K ~ 0.16*N. At N_scene=128 the knee sits inside K in [1..36] (MEASURED@probe). discriminator_reachability = True.

## SCHEMA-VET fields
arms_differ_verified=True (clean/scramble/wrongkey query preds hash-distinct); final_metrics_atomicity=tmp_replace;
except SystemExit->raise before except Exception (no BaseException); baseline_in_band via scramble-fires + capacity-degrades;
cardinality: K-sweep 13 values * n_scenes reported per K; calibration_check=default_ok_for_this_regime;
real_code_path: self_test exercises hdlab.binding.bsc_bind/bsc_bundle/bsc_unbind (bit-identity) + hdlab.iterative_attractor.argmax_cleanup;
no-nondeterministic-seeding static scan in self_test (fixed seeds throughout).
Compute architecture: sequential-CPU (tiny primitives, N_scene<=256, no GPU speedup; perception pre-batched); wall < 30s.
Storage: bundled single scene vector is the OBJECT UNDER TEST; resonator arm = sharded-recovery counterpart.

## FULL result (MEASURED@data/exp_perception_bridge_scene_vector_digits_v1/metrics.json)
verdict=PASS. recog_acc=0.902. small-K loc->concept=1.000 concept->loc=1.000 xmodal=1.000.
scramble=0.124 (collapsed). capacity loc->concept 1.000->0.648 (degrade 0.352). resonator 0.800->0.312.
N-lever@K28: N96=0.634 N128=0.693 N192=0.835 N256=0.915 (capacity scales with N).
example_scene.npz emitted for visualization.
