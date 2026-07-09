# Pre-registration: selfplay_b2_act_active_query_v1 (B2_ACT -- active-intervention query-selection)

Filed by: exp_dev. Date: 2026-07-09. Cell:
`experiments/exp_selfplay_b2_act_active_query_v1.py`. Status: SMOKE CLEAR (machinery), pre-registered for
FULL. Extends the landed B1+EXOG cell (`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py`, byte-copy
of the anchor/game/eval/perturb/companion machinery + one changed selection mechanism).

## Question
Does per-agent SELF-CHOSEN (residual-ranked, own-uncertainty-driven) sampling of the exogenous
reconstruction target -- replacing B1_EXOG's UNIFORM-random target sampling with a BALD-style acquisition
rule + the existing predict-subtract comparator -- decorrelate the two self-play halves BELOW the ~0.38
plateau (`corr(failmask) <= 0.20`) WHILE retaining grounding (`>= 0.50`) and causal grounding
(`perturb_ratio >= 2.0`)? OR does B2_ACT ALSO land at ~0.38 -> the ceiling is the shared MessageChannel
discrete-communication bottleneck, not the sampling policy.

## Trigger / on-disk grounding (Fix#28, Read not assumed)
- B1_EXOG landed FULL HARD_FAIL: `verdict = HARD_FAIL_PASSIVE_EXOG_INSUFFICIENT_REDIRECT_ACTIVE_INTERVENTION`.
  MEASURED@`data/exp_selfplay_b1_exog_predictive_anchor_v1/metrics.json:gates`:
  `b0_failmask_corr=0.7941`, `b1_failmask_corr=0.3925`, `exog_failmask_corr=0.3820`,
  `exog_grounding=0.6023`, `exog_perturb_ratio=3.6101`, `exog_improvement_over_b1=+0.0105`. Passive
  exogenous prediction GROUNDED but did NOT DECORRELATE.
- THIRD consecutive mechanism clustering at corr~0.38: DG 0.377, B1 0.393, B1_EXOG 0.382 (all MEASURED).
- Design + P estimates: `notes/research_active_intervention_query_selection_grounding_2026-07-09.md` +
  `notes/exp_dev_handoff_research_active_intervention_query_selection_2026-07-09.md`. Load-bearing ingredient
  per 4 converging literatures (active inference/BALD, sensorimotor contingency/efference copy,
  developmental manipulation, interventional causal discovery): a self-chosen PER-AGENT DISTINCT query
  target (not physical action) + a predict-subtract comparator (already present as `_anchor_loss`).

## Prior-work check (substrate-KB concept query, mandatory)
`bash tools/substrate_query.sh "active intervention query selection self-chosen sampling decorrelation
self-play grounding"` -> top hits are generic concept-atoms for the word "selection" (WordNet/ConceptNet
content) at cosine 0.40, plus one unrelated TIER5 note at 0.359. NONE at cosine>0.30 is a prior arc cell
implementing active-query-selection. B2_ACT is genuinely novel (direct redirect from the B1_EXOG HARD_FAIL),
not a rediscovery.

## The mechanism (single changed selection; loss/objective UNCHANGED from B1_EXOG)
`train_arm()`: B1_EXOG samples its per-branch anchor target UNIFORMLY at random within the branch's own
disjoint fold (`a_idx = rng.choice(pool, size=exog_bs, replace=False)`). B2_ACT replaces that with a
per-branch RESIDUAL-RANKED biased sample:
1. draw a candidate super-set `cand` of size `acq_super_mult * exog_batch` from the branch's OWN fold;
2. compute this branch's OWN per-index reconstruction residual `res = 0.5*(1-cos(anchor(enc(X[cand])),
   X[cand]))` (`_recon_residual_per_index`; same residual_magnitude semantics used elsewhere);
3. softmax-weight by `res / acq_tau` and sample `exog_batch` WITHOUT replacement biased toward highest own
   uncertainty (worst-reconstructed real referents).
Because `enc_s`/`enc_l` start from different inits (seed vs seed+333) on disjoint folds with separate
anchors (`seed+909`), their residual rankings diverge -> each branch runs its OWN distinct "intervention".
`acq_tau=0.07`, `acq_super_mult=4` (all profiles). Disjoint-fold discipline UNCHANGED (apples-to-apples).

Note on the research-note Anchor-2 fallback (explicit cross-branch anti-correlation over shared indices):
NOT built -- it is vacuous under the disjoint-fold structure (fold_a n fold_b = empty, so "deprioritize
indices the other branch favors" has no shared indices to act on). If B2_ACT plateaus, the pre-registered
redirect is the architecture probe below (shared MessageChannel), not the index-overlap fallback; a
content-space anti-correlation variant would be a redesign, not a minimal diff.

## STAGE 2 arms (4; B0/B1/B1_EXOG are the reproduced contrast ladder, B2_ACT is the new treatment)
- `B0_mirror` (MUST-FAIL control): tied encoder, info-access asymmetry only. Predicted HIGH corr (~0.79).
- `B1_crossfit` (CONTRAST FLOOR): separate enc, disjoint-fold cross-fit, no anchor. MUST reproduce [0.30,0.50].
- `B1_EXOG` (PLATEAU CONTRAST FLOOR that B2_ACT must beat): B1 + shared exogenous anchor, UNIFORM sampling.
  MUST reproduce its ~0.38 plateau (band [0.30,0.45]).
- `B2_ACT` (TREATMENT): B1_EXOG wiring with residual-ranked (own-uncertainty) biased acquisition.

## Discriminators
1. `failure_mask_corr` (reused verbatim): corr(1-speaker_correct, 1-listener_correct); `grounding_acc` =
   mean(listener_correct).
2. CAUSAL-PERTURBATION SCREEN (Prediction C, reused UNCHANGED): content-swap vs relation-swap normalized
   directional-sensitivity ratio; >= 2 == causal grounding. Telemetry-sensitive (self-test: content-encoder
   ratio 1390, relation-encoder ratio 0.009).
3. ACTIVE-SELECTION-FIRES (NEW mechanism-fires gate): `acq_lift` = mean over training steps of
   (mean residual of SELECTED indices - mean residual of the candidate super-set) > `ACQ_LIFT_MIN=0.005`.
   Proves the acquisition actually biases toward own-uncertainty; else B2_ACT is a no-op equal to B1_EXOG.
4. TRANSITIVE-SPREAD COMPANION (reuses snowball `label_propagation`, DIAGNOSTIC not a gate): retention check.

## Pre-registered bands (ALL; LOCKED PROSPECTIVE; the corr<=0.20 / ceiling decision is for FULL)
- **HARD_PASS** (active query-selection breaks the ~0.38 plateau -- "action IS the answer"):
  `B2_ACT corr <= 0.20` AND `grounding >= 0.50` AND `(EXOG corr - ACT corr) >= 0.10` AND
  `perturb_ratio >= 2.0` AND B0 fires (`corr >= 0.40`, in band) AND B1 reproduces (`[0.30,0.50]`) AND
  B1_EXOG reproduces (`[0.30,0.45]`) AND all codes non-degenerate (entropy >= 1.0 bit) AND both anchors
  fired (gain >= 0.03) AND active-selection fired (`acq_lift > 0.005`).
- **HARD_FAIL_STRUCTURAL_CEILING_SHARED_CHANNEL_BOTTLENECK** (THE load-bearing outcome -- also gold):
  `B2_ACT corr in [0.35,0.42]` WHILE grounding retained (`>= 0.50`) => FOURTH consecutive plateau at ~0.38
  under a structurally-distinct mechanism => the ceiling is the shared MessageChannel discrete-communication
  bottleneck, NOT the sampling policy. Redirect to a targeted architecture probe (widen/perturb the
  MessageChannel candidate-set, hold everything else fixed), NOT a fifth upstream-data mechanism.
- **HARD_FAIL_ACTIVE_SELECTION_REGRESSION**: `B2_ACT corr > 0.42` while grounding retained => active
  selection made decorrelation WORSE than the passive plateau (overfit to a few high-residual referents).
- **HARD_FAIL_ACTIVE_HOLLOW**: `perturb_ratio < 1.3` (even if corr improves) => noise/hardness without causal
  grounding (spurious decorrelation).
- **HARD_FAIL_ANCHOR_DESTROYS_GROUNDING**: `B2_ACT grounding < 0.40` => acquisition over-constrained the code.
- **MIDDLE_BAND**: B2_ACT corr in (0.20,0.35) with grounding >= 0.50, OR perturb_ratio in [1.3,2.0).
- **SATURATION_VACUOUS** / **CODE_COLLAPSE_VOID** / **ANCHOR_INERT_VOID** / **ACTIVE_SELECTION_INERT_VOID**:
  B0 corr < 0.40 or degenerate / entropy < 1.0 bit / an anchor recon not > untrained / acq_lift <= 0.005.

THE KEY REPORTED NUMBER: `B2_ACT corr(failmask)` vs the 0.38 plateau (`gates.act_vs_038_plateau`).

## HONEST FRAMING (mandatory, per research note S3)
Even a full HARD_PASS demonstrates only interventional-identifiability-style decorrelation via self-chosen
SYMBOLIC KB queries -- NOT literal embodied/enactivist grounding (Harnad/teleosemantic bars remain open
regardless; P(full embodied grounding)=0.10 CITED). The "action" here is a query-choice, not physical
intervention. Do NOT frame any pass as "the substrate now acts on the world." Both outcomes are gold:
PASS = self-chosen action decorrelates where passive prediction could not; STRUCTURAL_CEILING = a deeper,
cleaner target (the shared message channel) for the next cell. P_deflated(breaks the plateau below
corr<=0.20 while ground>=0.50 and perturb>=2.0) = 0.30 CITED@research note (three prior distinct mechanisms
all converged within 0.02 -- a genuine structural-ceiling warning).

## SMOKE result (CLEAR -- all machinery gates pass; acq_tau=0.07 final)
MEASURED@`data/exp_selfplay_b2_act_active_query_v1_smoke/metrics.json` (3 seeds, n=1237, 147.3s, 12/12
units, 0 failures, run_mode=smoke):
- B0 corr=0.793 fires=True (spk_fail=0.372 lis_fail=0.388 in band) -> assert_discriminator_fires PASS.
- B1 corr=0.327 reproduces=True; B1_EXOG corr=0.366 ground=0.439 reproduces=True (plateau contrast PASS).
- B2_ACT corr=0.329 ground=0.452; improve(EXOG-ACT)=+0.036; vs_0.38_plateau=-0.051.
- perturb_ratio(ACT=3.70 EXOG=3.78 B1=3.73) -- causal grounding retained on all arms (>2).
- anchor_fired=True gain=0.224; ACTIVE-SELECTION FIRED=True acq_lift=0.0071 (per-seed
  [0.00697,0.00718,0.00703] -- fires uniformly across seeds). codes_ok=True entropy [2.84,2.86,2.88,3.26].
  All 4 arms differ (passed META_RULE_AF assert).
- Smoke verdict MIDDLE_BAND = SCIENCE preview: at smoke scale (grounding ~0.44, well below the FULL 0.60)
  active selection shows a LEANING-POSITIVE decorrelation (+0.036 below the EXOG plateau) but nowhere near
  the corr<=0.20 HP bar. This is a genuine leaning-negative-to-modest preview consistent with P~0.30, NOT a
  machinery fault. The corr<=0.20 / structural-ceiling decision is a FULL-scale question (smoke n=1237/80ep
  vs FULL n=8000/220ep). No saturation (B0->B1 gap 0.79->0.33 large -> discriminator exercised);
  discriminator survives scale via full-branch parity, mechanism ratio fixed (lambda_exog=0.5, acq_tau=0.07).
- Tuning note: an initial smoke at acq_tau=0.10 gave acq_lift=0.0059 (thin) and improve=-0.009; sharpening
  to acq_tau=0.07 raised acq_lift to 0.0071 AND flipped the smoke decorrelation preview to +0.036 while
  holding grounding (0.452) and perturb (3.70) -- giving FULL its strongest, most-defensible shot so that a
  plateau result reads as a genuine structural-ceiling signal, not a too-soft-knob artifact.

## SCHEMA-VET fields
- `cell_chunked`: false (single cell; per-(seed,arm) loop with write_partial checkpointing + heartbeat).
- `start_marker_written`: true. `crash_diagnostic_present`: true (except SystemExit: raise BEFORE except
  Exception; NOT BaseException; grep-clean of bare except / BaseException). `heartbeat_present`: true.
  `defensive_error_checking`: passed_all_4_patterns.
- `final_metrics_atomicity`: tmp_replace (write_metrics -> os.replace).
- `arms_differ_verified`: true (4 mask-pairs hashed per seed; all differ; enforced by AF assert AND the
  acq_lift>0.005 active-selection-fires gate ruling out B2_ACT==B1_EXOG no-op).
- `cardinality_ok`: true (EXPECTED_N_UNITS = 4 arms * n_seeds; verdict emits HARD_FAIL_CARDINALITY_BREACH
  if short).
- `baseline_in_band`: true (B0 fail rates in [0.05,0.95]).
- `crlb_n/a`: discriminator = failure-mask CORRELATION vs within-cell MUST-FAIL control (B0) + normalized
  directional-sensitivity RATIO; reachability by construction (B0 fires high; treatment in [0,corr(B0)];
  HP corr<=0.20 w/ margin>=0.10 vs EXOG inside; ratio gate 2.0 with planted-encoder self-test proving
  sensitivity; acq_lift telemetry proves the new selection knob moved).
- `calibration_check`: adaptive_with_discriminator_gate (lambda_exog/K/tau/acq_tau fixed per profile;
  anti-collapse + B0-fires + baseline-in-band + anchor-fires + active-selection-fires + perturb-sensitivity
  recomputed per run).
- `progress_logging`: print_flush_true (line-buffered + per-(seed,arm) heartbeat; FULL timeout_s >= 1800).
- `multi_seed_smoke`: true (3 seeds; per-seed acq_lift + per-arm corr recorded).
- Compute architecture: (c) mixed sequential-CPU with justification (shallow linear ProjHeads + linear
  W_pred decoders; cost is the sequential self-play training loop; B2_ACT adds a bounded per-epoch no-grad
  anchor forward over acq_super_mult*exog_batch on the 4th arm only). Storage strategy: no_storage.
- HP_SCOPE: {decorrelation -> B2_ACT; screen-fires -> B0; contrast-reproduce -> B1_crossfit + B1_EXOG;
  anti-collapse -> ALL; anchor-fires -> B1_EXOG + B2_ACT; active-selection-fires + perturb-ratio HP -> B2_ACT
  (B1/EXOG perturb ratios reported as contrast)}.

## Number tags
- B1_EXOG FULL corr 0.382 / ground 0.602 / perturb 3.61, B1 0.393, mirror 0.794:
  MEASURED@`data/exp_selfplay_b1_exog_predictive_anchor_v1/metrics.json:gates`.
- DG 0.377: MEASURED@`data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json`.
- B2_ACT smoke numbers (corr 0.329, acq_lift 0.0071, improve +0.036, perturb 3.70):
  MEASURED@`data/exp_selfplay_b2_act_active_query_v1_smoke/metrics.json`.
- HARD_PASS / STRUCTURAL_CEILING bands (corr<=0.20, [0.35,0.42], margin>=0.10, ratio>=2.0):
  HYPOTHESIZED@this prereg (from the active-intervention drill's falsifiable table + the task discriminator).
- P(break plateau)=0.30, P(full embodied grounding)=0.10:
  CITED@`research_active_intervention_query_selection_grounding_2026-07-09.md`.

## Dispatch
FULL -> `remote_cpu_queue` (CPU cell; small linear nets + numpy; no GPU-batching mandate -- sequential
self-play training loop, genuine epoch dependency). ETA ~40-50 min (B1_EXOG FULL analog = 1597s for 15
units / 3 arms x 5 seeds; B2_ACT adds a 4th arm at ~1.8x per-unit from the acquisition forward -> ~20 units
effective-24, est ~2600-2800s). Timeout 7200s (generous margin vs remote-CPU variance; well under 14400 cap).
queue_add (for the orchestrator to ship + REMOTE VERIFY):
`bash tools/orchestrator/queue_add.sh remote_cpu_queue selfplay_b2_act_active_query_v1
experiments/exp_selfplay_b2_act_active_query_v1.py preregs/2026-07-09_selfplay_b2_act_active_query_v1.md 7200`
