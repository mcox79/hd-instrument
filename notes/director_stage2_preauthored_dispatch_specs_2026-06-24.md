# Stage 2 pre-authored dispatch specs

Per never-go-idle mandate. When pipeline drained at any wake-up, dispatch ONE of these (in priority order).

## DISPATCH 1: Resonator multi-hop integration cell
**Anchor**: `substrate_resonator_multihop_integration_v1`
**Strategic**: closes 2-hop interference gap (0.638 → target 0.85+) via existing Resonator + confidence-tier gating
**Lane**: Lane 1 (substrate-native)
**Routing**: local_cpu_queue
**Arms** (3 seeds, synthetic concept data):
1. ARM_NAIVE_HEBBIAN_2HOP (control; reproduces 0.638)
2. ARM_RESONATOR_2HOP (wave14_multihop_resonator + confidence-tier gating)
3. ARM_RESONATOR_3HOP (extends to 3-hop)
**HARD bands**: HARD_PASS = ARM_RESONATOR_2HOP top1 ≥ 0.85; HARD_FAIL ≤ 0.70
**Timeout**: 1800s
**Apples-to-apples**: ALL arms substrate-native; ONE knob varies (resonator on/off)

## DISPATCH 2: Tau-gate refuse-training cell
**Anchor**: `substrate_tau_gate_refuse_training_v1`
**Strategic**: closes refuse-gate gap (12.7% → target 80%+) via tau-learning + joint-refusal training
**Lane**: Lane 4 (substrate-product axis)
**Routing**: local_cpu_queue
**Arms** (3 seeds, synthetic; M=500 known + M=100 unknown):
1. ARM_NAIVE_NO_REFUSE (control)
2. ARM_TAU_LEARNED (tau-learning per 61b_refuse_aware_scorer)
3. ARM_TAU_PLUS_JOINT (tau + joint-refusal training)
**HARD bands**: HARD_PASS = refuse_accuracy ≥ 0.80 on unknowns AND > 0.95 retention on knowns
**Timeout**: 1800s

## DISPATCH 3: Hub-and-spoke E1 federation encoder cell
**Anchor**: `substrate_hub_spoke_E1_encoder_v1`
**Strategic**: tests encoding drill's #1 ranked encoding (P_deflated=0.45); substrate-OWNED ATL-analog architecture
**Lane**: Lane 1 substrate-native (no external pretraining)
**Routing**: overnight_queue (GPU; matmul-heavy)
**Arms** (3 seeds, N_DIM=8192):
1. ARM_BASELINE_PATH_C_SINGLE (Path C encoder as reference; landed 7.62 BPC Hebbian)
2. ARM_HUB_SPOKE_3SPOKE (3 spokes → hub)
3. ARM_HUB_SPOKE_5SPOKE (5 spokes → hub)
4. ARM_HUB_SPOKE_WITH_CFRPE (hub-spoke + adaptive cf-RPE plasticity)
**HARD bands**: HARD_PASS = best hub-spoke ≤ 7.20 BPC (improves Path C single-spoke by ≥0.40); CHAIN_GRADE = ≤ 6.95
**Timeout**: 7200s
**Apples-to-apples**: substrate-OWNED encoders only; no word2vec

## DISPATCH 4: Isotonic confidence calibration cell
**Anchor**: `substrate_confidence_calibration_isotonic_v1`
**Strategic**: closes calibration gap (r=0.072 → target r≥0.70) via isotonic regression on cosine confidence
**Lane**: Lane 4 (substrate-product axis)
**Routing**: local_cpu_queue
**Arms** (3 seeds; M=500):
1. ARM_RAW_COSINE (control; calibration r=0.072)
2. ARM_ISOTONIC_REGRESSION (per lap4_3)
3. ARM_TEMPERATURE_SCALING (alternative; T-fit on dev)
**HARD bands**: HARD_PASS = best calibration r ≥ 0.70
**Timeout**: 1200s

## DISPATCH 5: Encoding shotgun BUGFIX cell
**Anchor**: `substrate_encoding_shotgun_native_v2_BUGFIX`
**Strategic**: v1 HARD_FAIL was cell bug (no encoder passed T1 storage; substrate-side issue). Need to re-author with correct storage primitive.
**Lane**: Lane 1
**Routing**: local_cpu_queue
**Same 6 encoders × 4 tasks as v1 but with FIXED storage primitive**
**HARD bands**: same as v1
**Timeout**: 3600s

## Dispatch priority order

1. Resonator multi-hop (closes biggest Stage 1 gap; integration of existing Store solution)
2. Tau-gate refuse (substrate-product audit story moot until refuse works)
3. Hub-and-spoke E1 (validates encoding drill's #1 recommendation; substrate-OWNED)
4. Isotonic calibration (smaller gap; complements tau-gate)
5. Encoding shotgun v2 BUGFIX (re-runs to actually answer encoder question)

## Each wake-up MUST

If pipeline drained AND no urgent landings to process:
- Dispatch DISPATCH 1 if not already in flight
- Else DISPATCH 2 if not in flight
- Else continue down priority list

If pipeline saturated OR landings to process:
- Process landings per standing rules
- Skip new dispatch
