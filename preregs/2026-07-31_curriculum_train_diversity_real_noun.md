# Pre-registration: curriculum_train_diversity_real_noun_v1

Filed 2026-07-31 (Director spawn: the corrected-frontier probe -- curriculum hypothesis IN MINIATURE).
Cell: `experiments/exp_curriculum_train_diversity_real_noun_v1.py`
Metrics: `data/exp_curriculum_train_diversity_real_noun_v1/metrics.json`

## Question (ONE variable = TRAIN-VOCAB DIVERSITY)

The grounding first-cut (09a8747ce, MIDDLE) MEASURED: the certified minimal-unfreeze entity-re-id fine-tune
(atom 29593) lifted the held-out re-id loop **+0.275 on the tight 20-COLOR set** but only **+0.074 on 120 REAL
NOUNS** (train=110). Does STRENGTHENING THE TRAINING (more varied real-noun vocabulary the entity objective is
trained on) PULL THE GRIP UP -- from the +0.074 toward the +0.275 color level -- as the USER's "the reader
learns as it reads" curriculum insight predicts? Tested cheaply in miniature.

ONE variable = the NUMBER of real-noun entities the certified fine-tune trains on. Everything else FIXED: the
encoder, the recipe (depth=1 top-layer unfreeze, reused VERBATIM via `hc._finetune_weights`), the FHRR
situation-model loop, the guard, the floors, the HELD-OUT eval nouns, the total noun palette (hence chance),
and the eval passages themselves (byte-identical across levels).

## Design

- N_NOUN palette FIXED (120 lite / 24 smoke); chance = 1/N_NOUN FIXED; FHRR codebooks FIXED.
- `(held, train_pool) = ih.color_split(SPLIT_SEED)` under the installed vocab -- the IDENTICAL split the
  grounding first-cut used (held=10 novel eval nouns; train_pool=110). A FIXED permutation (seed 20260731) of
  train_pool gives NESTED diversity prefixes `DIVERSITY_GRID_LITE = (12, 35, 70, 110)`.
- At each level the certified fine-tune trains on `perm[:n_train]` ONLY. The MAX level (n_train=110)
  REPRODUCES the grounding first-cut setting EXACTLY (built-in cross-check: its lift should be ~+0.074).
- HELD-OUT eval passages are byte-identical across every level (ent_pool=held fixed, mark_pool=FULL train_pool
  fixed, fixed eval RNG). frozen loop is diversity-INDEPENDENT (no fine-tune) -> computed ONCE per seed.
- Per level MEASURED: TUNED held-out loop, ORACLE ceiling (base reading A), memorization control (loop on the
  level's OWN train entities), geometry, guard, + the three flat-diagnostics (below).
- Per seed (base unit): FROZEN loop + wc + q_agree + entcons, the 6 can-fail floors, POOLED_READER,
  MOST_RECENT, and the COLOR_ANCHOR positive control (reproduce the certified +0.275 color lift = ceiling ref).
- SEEDS_LITE=(7,13); STEPS_LITE=220 (certified); GRID_EVAL_N_LITE=120 (sized so binomial MDE(slope) < 0.05).

## Pre-registered bands (fixed BEFORE running)

`lift(k) = tuned_loop(n_train=k) - frozen_loop`, on the FIXED held-out eval nouns at fixed chance=1/N_NOUN.
`slope = mean_lift(max level) - mean_lift(min level)`. COLOR_CEILING = color-anchor lift (~+0.275 reference).

- **HARD_PASS (CURRICULUM WORKS IN MINIATURE):** `slope >= SLOPE_MIN (0.05)` AND `lift(max) >= LIFT_MIN (0.05)`
  AND `lift(max)` is the (near-)peak `[>= max(mean_lift) - TIE_BAND]` AND `capture(max) >=
  HEADROOM_CAPTURE_MIN (0.35)` AND every seed lifts at max AND guard HOLDS at max AND `mem_gap(max) <=
  MEMORIZE_GAP_MAX (0.15)` AND base reading OK at max AND floors collapse + COLOR_ANCHOR reproduces a lift.
- **MIDDLE (partial upward):** `TIE_BAND < slope < SLOPE_MIN`, or rises then plateaus below color. Report the
  slope + full trajectory = the extrapolation for the USER's curriculum-scale decision.
- **READING-WALL (HARD_FAIL tier, framed as an ENCODER observation NOT a ceiling):** base reading fails at max
  (`oracle - chance < BASE_READING_MARGIN 0.20`) -- the sweep is moot until the encoder reads the vocab.
- **INVALID:** a floor did not collapse OR POOLED reservoir-decodable OR COLOR_ANCHOR reproduces no lift OR
  `headroom(max) = oracle - frozen < CONSTRUCTION_HEADROOM_MIN (0.05)` OR held not disjoint from any train
  level OR cardinality breach.

## USER REFRAME (2026-07-31, load-bearing): a FLAT trajectory is NOT a capability ceiling

Learning-from-genuinely-new-content is EXPECTED to work if the machinery functions. So a FLAT slope means the
EXPERIMENT is broken in one of exactly THREE ways, DIAGNOSED off MEASURED evidence (baked into the cell;
`bands.flat_diagnosis`), NOT a ceiling:

- **(a) NOT ACTUALLY LEARNING** -- unfrozen-param relative L2 movement `weight_move_rel <= WEIGHT_MOVE_MIN
  (1e-3)` OR the objective did not fit the TRAIN entities `train_lift < LEARN_TRAIN_MIN (0.05)`. Also logged:
  final objective loss + `l_align`. => verdict INVALID (fix the training), NOT a ceiling.
- **(b) NO GENUINELY-NEW CONTENT** -- the train entities carry no separable signal `wc_train_frozen <=
  CONTENT_WC_FLOOR (0.005)` (near-duplicate reps; each increment adds rows not information). => verdict INVALID
  (fix the content), NOT a ceiling. [Prior: real nouns near-orthogonal, mean pairwise cos ~0.02
  CITED@grounding disk finding -- so (b) is expected to PASS = content genuinely new.]
- **(c) UNDERPOWERED** -- the minimum-detectable-effect `MDE(slope) > SLOPE_MIN`, computed as the LARGER of
  (between-seed dispersion 1.96*sqrt((s_lo^2+s_hi^2)/n_seeds)) and (binomial loop SE
  1.96*sqrt(2)*sqrt(pbar(1-pbar)/(eval_n*n_qt*n_seeds))). => verdict INVALID (add seeds/eval/steps), NOT a
  ceiling. [eval_n_lite=120 sizes binomial MDE < 0.05.]
- **CLEAN_DESIGN_LIMIT** -- learning verified + content genuinely new + adequately powered AND STILL flat =>
  verdict MIDDLE with the honest read: this OBJECTIVE/RECIPE (top-1-layer unfreeze) does not capture
  broad-vocab generalization -- a DESIGN fix (more unfreeze / harder in-batch negatives / more steps / richer
  contexts), NOT a capability ceiling. `mem_gap` reported (high = objective fit train but did not generalize).

The cell NEVER emits an "intrinsic ceiling" verdict. A flat result auto-reports its (a)/(b)/(c)/design cause.

## SCHEMA-VET gate fields

```yaml
cell_chunked: false            # sweep over (seed, n_train) units; single main() with per-unit checkpoint/resume
cardinality_ok: true           # EXPECTED_N_UNITS = n_seeds * (1 base + len(grid) tuned); verdict counts len(units)
start_marker_written: true
crash_diagnostic_present: true # except SystemExit: raise BEFORE except Exception (no BaseException)
heartbeat_present: false       # per-unit checkpoint (units.jsonl) + print_flush progress serve the same role
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
progress_logging: print_flush_true
arms_differ_verified: true     # META_RULE_AF: frozen vs tuned distinct in loop/q_agree/geometry at self-test
levels_differ_verified: true   # SWEEP discriminator-fires: two diversity levels produce distinct tuned output
baseline_in_band: true         # FROZEN loop between chance and ORACLE; 6 floors MUST collapse
calibration_check: default_ok_for_this_regime   # recipe + bars reused VERBATIM from certified atom 29593
crlb_n/a: "slope-of-lift discriminator; no quantitative noise floor. Power handled by MDE(slope) diagnostic (c)."

# sweep gates
sweep_alignment_verdict: ALIGNED          # the swept param (n_train) is EXACTLY what the fine-tune experiences
effective_vs_nominal: "n_train = the number of ENTITY reps the objective differentiates; no partition/routing"
discriminating_fraction: n/a              # not an accuracy-bracket sweep; discriminator = the slope of lift
bracket_includes_discriminating_band: "frozen in [chance, oracle]; lift can-fail flat OR climb to color ceiling"

# composition / signature gates
composition_edges: []                     # no NEW primitive composition; reuses the certified pipeline VERBATIM
positive_control_arms:
  - arm: COLOR_ANCHOR                      # reproduce the certified frozen->tuned COLOR lift AT the test recipe
    cited_prior: "grounding 09a8747ce color lift +0.275 (220 steps)"
    if_no_lift: INVALID                    # wiring/recipe broken -> do not trust the trajectory
  - arm: MAX_LEVEL_REPRODUCES_GROUNDING    # n_train=110 == grounding first-cut setting; lift should be ~+0.074
real_code_path_exercised: [RetrainableExtractor, finetune_encoder, score_extractor, within_minus_cross, build_addr_dataset]
substrate_signature_checked: [hc._finetune_weights, lt.score_extractor]   # base/portable calls; reused verbatim
guard_baseline_validated: [COLOR_ANCHOR, floor-collapse]
deterministic_seeding: true               # numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
```

## Functional requirements

1. Isolate the diversity variable -> FIXED held-out eval nouns + FIXED palette/chance + FIXED eval passages;
   only the fine-tune train-entity count varies (nested prefixes). [certified fine-tune reused verbatim]
2. Fairness -> eval entities never trained on (asserted per passage + per level). [ih.color_split held pool]
3. Ceiling reference -> COLOR_ANCHOR reproduces the certified +0.275 color lift. [positive control]
4. Flat-result honesty -> the three (a)/(b)/(c) diagnostics + CLEAN_DESIGN_LIMIT baked in. [USER reframe]
5. Validity -> 6 can-fail floors collapse; POOLED not reservoir-decodable; base-reading precondition. [floors]

## Compute architecture

mixed -- top-1-layer SGD fine-tune (batched fwd+bwd, CPU) + closed-form FHRR eval loop with batched
frozen-encoder forwards. Storage strategy: no_storage. CPU-first, push-free, INLINE-LOCAL foreground,
resumable per unit (budget-sec keeps each foreground call < 10 min).
