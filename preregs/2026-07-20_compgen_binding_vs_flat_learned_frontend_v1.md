# PRE-REG: Compositional generalization -- learned front-end + fixed FHRR binding vs flat learned baseline (v1)

Date: 2026-07-20
Cell: experiments/exp_compgen_binding_vs_flat_learned_frontend_v1.py
Anchor: exp_compgen_binding_vs_flat_learned_frontend_v1
Author: hdi_exp_dev (Director-authorized design-gated cell per notes/research_brain_systematicity_binding_learned_frontend_2026-07-20.md)
Queue: LOCAL (run to completion in foreground; light torch MLPs, CPU, total wall estimated under 5 minutes)
needs_orchestrator_store_sync: True

## WHAT / WHY (the honest claim, refined by the brain-drill)

Native FHRR binding (hdlab.binding.bind/unbind + hdlab.bundling.bundle) is a BUILT-IN STRUCTURAL
PRIOR that gives a LEARNED front-end SYSTEMATIC generalization to HELD-OUT role-filler combinations
DATA-EFFICIENTLY / WITHOUT meta-learning, where a FLAT learned baseline (single-task, no meta-learning,
matched capacity) FAILS (the classic COGS/SCAN systematicity gap; CLEVR-CoGenT causal analog: NS-CL's
frozen-attribute-classifier ablation). We measure the LEARNING CURVE (held-out accuracy vs training-set
size) for both arms, not a single point.

CAVEAT (load-bearing, do not over-claim): Lake & Baroni MLC (Nature 2023) shows a fully-learned
META-LEARNED model CAN match fixed-binding systematicity. This cell does NOT claim binding is the only
route to systematicity -- it claims binding achieves it DATA-EFFICIENTLY WITHOUT meta-learning, brain-
faithful (Kymn et al. 2024: fixed structured binding + learned heteroassociative mapping in hippocampal-
entorhinal circuits). If flat matches binding here, the informative null redirects effort toward the
MLC-style fully-learned meta-learning path (a different, currently un-scoped build direction), not a
re-run-until-it-works loop.

## PRIOR ART (credit; learn-from/build-on, never steal)
- Smolensky 1990 TPR; Plate 1995 HRR -- fixed bilinear/uniform binding operator, systematicity by construction.
- NVSA (Hersche et al., Nat. Mach. Intell. 2023) -- learned front-end + fixed VSA binding + fixed reasoning.
- NS-CL (Mao et al., ICLR 2019) + CLEVR-CoGenT (Johnson et al. 2017) -- the causal ablation this design
  borrows directly: freezing the attribute/perception layer after train-split-only training preserves
  held-out generalization; re-learning attributes end-to-end on the compositional task loss entangles and
  collapses on the swapped split. THIS is the mechanism this cell's flat-vs-hybrid split isolates.
- Kymn et al. (NeurIPS 2024) -- fixed structured hippocampal-entorhinal binding + learned sensory mapping,
  the neural precedent for "learned front-end, fixed composition."
- Lake & Baroni (ICML 2018 SCAN; Nature 2023 MLC); Kim & Linzen (EMNLP 2020 COGS); Keysers et al. (ICLR
  2020 CFQ/DBCA compound-divergence) -- the failure-mode + split-discipline literature this design follows.
- Greff, van Steenkiste & Schmidhuber 2020 ("On the Binding Problem in ANNs") -- construction-determinism
  critique; the SAME lesson as our own in-house structure-derivation KILL (atom 29369): role/filler CODES
  must be random/task-agnostic, never fit to the split. This is GUARD #1 below.
- Reuses hdlab.binding.bind/unbind (native FHRR: elementwise complex mul / mul-by-conjugate) and the
  per-component-magnitude-renormalization bundle formula from hdlab.bundling.bundle (vectorized batched
  reimplementation verified numerically equivalent in self-test -- see "Positive control" below).

## Prior-work check (substrate-KB concept-query, MANDATORY before authoring)
Ran `bash tools/substrate_query.sh` on compositional-generalization / binding / held-out / systematicity
terms. Top hits (cosine 0.40-0.42) are prior RESEARCH DRILL notes (research_drill_field_VSA_NeSy_rule_
DEEPER_5x_2026-06-07.md, wave14e_hierarchical_composition_research.md) that discuss the SAME literature
(Lake & Baroni, VSA-by-construction) at the THEORY level -- no prior cosine>0.30 hit is an EXECUTED CELL
testing a learned front-end's held-out generalization with a frozen-vs-end-to-end split. This cell is
NOVEL relative to substrate-KB (the closed reasoning-CG free-algebra work tested binding COMPOSING
directly, not a learned perceptual front-end's generalization under a train/test combinatorial split) --
not a rediscovery.

## GUARD #1 (highest-confidence, decisive -- construction-determinism)
Role codes (R=6) and filler codes (F=12) are FHRR unit-phasor vectors (complex64, N=1024) generated ONCE
via FIXED, TASK-AGNOSTIC seeds (ROLE_CODE_SEED=1000, FILLER_CODE_SEED=2000) that are defined and
instantiated in code BEFORE the train/test group-split logic exists anywhere in the run. The group split
(GROUP_A={0,1,2} vs GROUP_B={3,4,5} roles; HALF1={0..5} vs HALF2={6..11} fillers) is a DATA-DESIGN choice
(which combos appear in train vs held-out, per Keysers compound-divergence discipline) applied ON TOP OF
already-fixed, arbitrary-index codes -- it never feeds back into how role_codes/filler_codes are drawn.
No code is selected, tuned, or derived to make specific held-out pairs decode well. `guard1_role_filler_
codes_random_task_agnostic: true` (verified by code inspection + self-test asserting code generation takes
no split/label arguments).

## ARMS (ONE variable = composition mechanism; front-end architecture capacity/data budget matched)
- `hybrid` (mechanism): front-end MLP (d_obs=24 -> 64 -> ReLU -> F=12 logits) trained via a DECOUPLED
  classification loss on (observation, filler_label) pairs ONLY -- it never receives role information and
  its loss never depends on the (role,filler) combination, satisfying the CLEVR-CoGenT frozen-attribute-
  classifier ablation (guard #5 below). At composition time the frontend is FROZEN; argmax-predicted
  filler id is looked up in the FIXED filler codebook, bound to the FIXED role code via native FHRR
  `hdlab.binding.bind`, all R role-filler binds bundled (native `hdlab.bundling.bundle` formula) into one
  scene vector. Query = `hdlab.binding.unbind` by the queried role code + cosine-cleanup argmax against
  the F filler codes. NO gradient-trained composition anywhere in this arm.
- `flat` (baseline, matched-or-greater capacity): MLP (R*d_obs+R=150 -> 128 -> ReLU -> 64 -> ReLU -> F=12
  logits) trained END-TO-END on the full compositional query task (all R observations + one-hot query role
  -> predicted filler), using the SAME train-split scenes and the SAME effective example count (S_train*R
  query-label pairs, matching the front-end's S_train*R observation-label pairs). No explicit bind/unbind
  operator; composition must be learned from data. This is the CLEVR-CoGenT "re-learn attributes end-to-
  end on the compositional loss" arm -- genuinely capable (same-or-more parameters, same optimizer/epochs).
- `majority` (non-compositional shortcut control, Gate #3): per-role majority-filler frequency lookup from
  that seed's training scenes; ignores the observation entirely. Must score ~0 on held-out by construction
  (majority filler for a GROUP_A role is always drawn from HALF1 in training; held-out queries GROUP_A
  roles with HALF2 fillers, guaranteed mismatch) -- confirms the split is not solvable by frequency alone.

## TASK / DATA GENERATION
- R=6 roles; GROUP_A=[0,1,2], GROUP_B=[3,4,5] (arbitrary index partition, fixed before code generation).
- F=12 fillers; HALF1=[0..5], HALF2=[6..11].
- Fixed filler prototypes: PROTO[f] in R^24, drawn once via PROTO_SEED=42 (never touched by split logic).
- Observation: obs(f) = PROTO[f] + N(0, 0.5^2 I_24) -- perceptual noise only, NO role-dependent nuisance
  (deliberately: a role-dependent bias term would let even the role-blind front-end pick up a role-proxy
  shortcut from bias alone, confounding the test; dropping it keeps the entanglement risk located ONLY in
  the flat arm's joint role+filler input, matching CLEVR-CoGenT's actual mechanism).
- TRAIN scene: each of the R roles independently draws a filler from its ALLOWED half (GROUP_A -> HALF1,
  GROUP_B -> HALF2). Query role sampled per training example (ALL R roles queried per stored scene, R
  labeled examples per scene, matching hybrid's per-observation labels 1:1).
- HELD-OUT (OOD) scene: SWAPPED assignment (GROUP_A -> HALF2, GROUP_B -> HALF1) -- the combinatorial split
  that never appears in training (Keysers DBCA: atom frequency for every (role) and every (filler) is
  IDENTICAL across train/dev/test by construction; only the (role,filler) COMPOUND differs). Gate #2 met.
- Fixed EVAL sets (generated ONCE, independent of training seed, reused across the whole sweep for
  comparability): ID_DEV = 400 scenes (in-distribution generation, held-out INSTANCES not held-out
  combos, seed=999); OOD_TEST = 400 scenes (swapped generation, seed=998). 2400 queries each.

## LEARNING CURVE SWEEP
TRAIN_SIZES (scenes) = [100, 400, 1600, 6400] (FULL); SEEDS = [7, 13, 19]. Composite per-run seed =
`100000*seed + train_size` (deterministic arithmetic combination -- NOT hash()/list(set()); PROT-023 OK).
EXPECTED_N_UNITS = len(TRAIN_SIZES) * len(SEEDS) * len(ARMS) = 4*3*3 = 36.

## PRE-REGISTERED BANDS (declared BEFORE running; evaluated at N_TRAIN_MAX=6400, the most-converged point)
- HARD_PASS: hybrid_OOD_ACC >= hybrid_ID_ACC - 0.10 AND flat_OOD_ACC <= flat_ID_ACC - 0.30 AND
  |hybrid_ID_ACC - flat_ID_ACC| <= 0.05 (capacity/tuning parity) AND majority_OOD_ACC <= 0.05 (split is
  genuinely non-trivial to shortcut). All at N_TRAIN_MAX, mean over 3 seeds.
- MIDDLE_BAND: gap direction is correct (hybrid holds up better than flat) but misses a strict threshold
  above -- e.g. ID-match gap in (0.05, 0.15], or hybrid's OOD gap in (0.10, 0.20], or flat's OOD gap in
  [0.20, 0.30). Report; do not over-claim.
- HARD_FAIL: flat_OOD_ACC >= flat_ID_ACC - 0.10 (flat ALSO generalizes -- no binding advantage; genuine
  null per the MLC/Patel-et-al. counter-evidence, NOT re-run-until-it-works) OR majority_OOD_ACC > 0.15
  (split not discriminative; redesign) OR |hybrid_ID_ACC - flat_ID_ACC| > 0.15 at N_TRAIN_MAX (capacity
  mismatch invalidates the comparison; fix and re-run before concluding).
Band-floor (META_RULE_L): chance = 1/F = 0.083; HARD_PASS's hybrid-OOD-near-ID target is far above chance,
not a floor-hugging result.

## DISCRIMINATOR-FIRES / SURVIVES-SCALE (option C: preview arm at full-N in smoke)
Smoke runs a SINGLE preview unit per arm at the FULL max training size (TRAIN_SIZES=[6400], SEEDS=[7]) --
not a smaller toy regime -- verifying the HARD_PASS-vs-HARD_FAIL gap already exists before committing to
the full 36-unit multi-seed sweep. If the flat arm's OOD gap is already <0.10 at this full-N preview, or
majority is not near-floor, STOP and do not dispatch the full sweep.

## SCHEMA-VET fields
- compute_architecture: (b) sequential-CPU with justification -- tiny torch MLPs (max hidden 128), Adam,
  <=40 epochs, batched full-vectorized FHRR bind/bundle/unbind (batch dim = scenes); total wall estimated
  under 5 minutes for the full 36-unit sweep; GPU batching would not meaningfully help at this scale.
- storage_strategy: no_storage (single-scene bundle-then-query per example; no multi-item chained storage).
- cardinality_ok: EXPECTED_N_UNITS=36 (4 sizes x 3 seeds x 3 arms); verdict counts len(per_unit), HARD_FAIL
  on shortfall (META_RULE_H).
- arms_differ_verified: True -- per-unit prediction arrays for hybrid/flat/majority hashed; must be
  pairwise distinct (META_RULE_AF); hybrid and flat additionally use structurally different code paths
  (FHRR bind/bundle/unbind vs a single MLP forward) so identity would indicate a wiring bug.
- final_metrics_atomicity: tmp_replace.
- crlb_n/a: "classification-accuracy generalization test over F=12 discrete fillers; no argmax-noise/
  capacity floor in the CRLB sense -- closed-form chance floor = 1/F = 0.083 (THEORETICAL), used as the
  discriminator context, not a CRLB."
- discriminator_reachability: True -- HARD_PASS bands (hybrid near-ID OOD acc; flat >=30pp OOD gap) are
  within the achievable range given SNR (PROTO norm ~4.9 vs noise std 0.5 per 24-dim obs) supports >0.85
  ID accuracy for a converged classifier at N_TRAIN_MAX, well above the discriminating range.
- baseline_in_band: True -- flat's ID accuracy is checked to sit in [0.30, 0.98] (not floor, not trivial
  saturation-only-in-distribution-collapse) before its OOD gap is interpreted; majority's ID accuracy is
  expected modestly above chance (small skew from finite per-half sampling), OOD forced near-floor.
- calibration_check: default_ok_for_this_regime (standard Adam/CE training; hyperparameters (epochs=40,
  lr=1e-3, batch=128) fixed BEFORE any run and identical across arms/sweep points -- not tuned per-result).
- cell_chunked: False (single process; sweep loop internal with per-unit atomic aggregation).
- start_marker_written: True; crash_diagnostic_present: True; heartbeat_present: True (per-unit progress
  prints, flushed, per SS17 -- though total wall is short, heartbeat included defensively).
- defensive_error_checking: passed_all_4_patterns.
- nondeterminism: fixed integer seeds; composite seed = arithmetic combination (100000*seed+train_size);
  NO hash()-derived seeds, NO list(set()) ordering (PROT-023 compliant); torch.manual_seed + np.random.
  default_rng both seeded from the same composite integer per unit.
- progress_logging: print_flush_true (timeout well under 1800s so §17 mandatory-heartbeat threshold does
  not strictly apply, but included defensively for audit visibility).

## Positive control (Gate D analog -- reproduce known FHRR bind/unbind exactness at the test regime)
Self-test asserts: (a) the batched/vectorized bundle formula used in `run()` is numerically equivalent
(atol=1e-5) to calling `hdlab.bundling.bundle` directly on a single (R,N) stack -- proves the "fast path"
IS the native substrate primitive, not a reimplementation drifting from it; (b) bind-then-unbind with the
EXACT (non-predicted) filler code recovers cosine similarity > 0.99 against the true filler code in a
clean single-item round trip (the well-established FHRR bind/unbind exactness property; this is the
algebra-only sanity check, decoupled from front-end learning quality).

## Functional Requirements (Gate E)
1. Learn to recognize filler identity from a noisy perceptual observation -> torch MLP front-end
   classifier trained from data (the LEARNED piece).
2. Compose role+filler into a multi-item scene and retrieve a queried role's filler -> FIXED native FHRR
   bind/bundle/unbind (hdlab.binding, hdlab.bundling) -- no learned composition (the STRUCTURAL PRIOR).
3. Demonstrate the fixed-composition system generalizes systematically to held-out role-filler
   combinations DATA-EFFICIENTLY WITHOUT meta-learning, vs a matched-capacity flat end-to-end learner ->
   THIS cell's learning-curve comparison (core measurement).
4. Rule out a non-compositional (frequency-lookup) shortcut explaining any observed gap -> majority-
   baseline arm (Gate #3).

## Guards checklist (from the brain-drill note, all addressed above)
1. Role/filler codes random, task-agnostic, fixed before split logic exists -- SATISFIED (see GUARD #1).
2. Atom (role, filler) frequency matched across train/held-out; only the compound differs -- SATISFIED
   (each role/filler individually appears with identical marginal frequency in both regimes by the
   symmetric GROUP_A/GROUP_B <-> HALF1/HALF2 swap construction).
3. Non-compositional shortcut baseline included -- SATISFIED (`majority` arm).
4. Split not solvable by a rule-based oracle with access to the generative scheme -- the generative scheme
   IS the group/half partition; an oracle with access to it would trivially solve everything (train AND
   test) since it defines the labels, so this guard is reframed as "no LEARNED arm is handed the partition
   directly" -- verified: neither MLP receives GROUP_A/GROUP_B/HALF1/HALF2 membership as a feature, only
   raw observations (+ query role identity for `flat`).
5. Front-end trained/frozen strictly on train-split pairings, no combination-level supervision, evaluated
   blind on held-out -- SATISFIED (front-end never receives role labels or query-role information at all).
6. Training-distribution-size tweak (Patel et al. 2022) tested via the learning-curve sweep itself -- if
   flat's OOD gap shrinks toward hybrid's as N_TRAIN grows, that is visible in the reported curve and
   would itself trigger the HARD_FAIL "flat generalizes" condition at N_TRAIN_MAX; not suppressed.
7. Systematicity (recombination of known atoms), not productivity, is what's tested and claimed (Fodor &
   Pylyshyn 1988) -- no productivity/unbounded-structure claim is made from this result.
8. Flat given equal-or-greater parameter budget (150->128->64->12 vs front-end's 24->64->12 + fixed
   algebra) and its own fixed training recipe identical in optimizer/epochs/lr to the hybrid's front-end
   -- SATISFIED; ID-accuracy-match gate (<=0.05 at N_TRAIN_MAX for HARD_PASS) additionally checks parity
   empirically, not just by architecture description.

## Dispatch / autonomy notes
Local, foreground, no origin push, no remote-persist. Self-test -> smoke (full-N single-seed preview) ->
if discriminator fires, FULL sweep run to completion in foreground (estimated wall <5 min; falls under
"light compute, run inline" per feedback_do_lightweight_measurements_inline_dont_over_route_to_heavyweight_
cells_USER_2026-07-14 -- NOT dispatched to local_cpu_queue, since local_cpu_queue is USER-LOCKED to SMOKE
ONLY and this FULL run is genuinely light, not a heavyweight cell requiring remote/GPU routing). Commit
cell + pre-reg + landed metrics locally by path; no origin push (exp_dev cannot push; not requested here).
Route to adversarial VET (Skunkworks) with construction-determinism (GUARD #1) as the #1 audit target.
