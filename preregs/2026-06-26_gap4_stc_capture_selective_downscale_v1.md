# Pre-reg: gap4_stc_capture_selective_downscale_v1 (Frey-Morris STC w/ bounded PRP)

Filed: 2026-06-26 by hdi_exp_dev (Claude Opus 4.7)
Source notes:
- `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` (Section 3 M5 + Section 5 Cell 2)
- `notes/exp_dev_handoff_research_gap4_brain_selective_homeostasis_2026-06-26.md` (ANCHOR_2)
Sibling in flight (architectural complement): `exp_gap4_two_tier_generational_W_v1`

## Anchor + scope

- Anchor: `gap4_stc_capture_selective_downscale_v1`
- Script: `experiments/exp_gap4_stc_capture_selective_downscale_v1.py`
- Routing: remote_cpu_queue (USER directive 2026-06-26; airport travel)
- Compute estimate: ~2h18m FULL-scale wall (Fix #17 measurement strict, see Section "Fix #17 budget")
- Anchor: ANCHOR_2 from Gap 4 brain SELECTIVE homeostasis level-2 drill (P_deflated 0.45)

## Scientific question

Cell B (substrate REM-homeostasis global downscale) HARD_FAIL_DESTROYS_OLDER on 3 schedules.
Brain does NOT do global downscale -- it does Synaptic Tagging and Capture (Frey-Morris 1997).

Substrate analog tested here: three matrices alongside W:
- `W[i,j]`  Hebbian outer-product weight (as Cell A/B)
- `T[i,j]`  binary tag flag (decays after K cycles if not captured)
- `P[i,j]`  binary persistent flag (immune to downscale)

STC mechanism:
1. **At write time**: `T[i,j] := True` for entries where `|dW[i,j]| > theta_tag`.
2. **Every J_replay cycles**: sample `N_PRP` tagged-but-not-persistent entries uniformly; mark `P=True`.
3. **Every J_downscale cycles**: `W[~P] *= gamma; W[P] *= 1.0` (selective downscale).
4. **Tag decay**: `T[i,j] -> False` if `(cycle - tag_birth) > K_tag_decay` AND `P==False`.

KEY: bounded `N_PRP` enforces COMPETITION under scarce protein resources -- this is what
makes brain selectivity scarce-resource-bounded rather than threshold-bounded. ZERO substrate
prior on Frey-Morris STC with bounded PRP. Composes architecturally with TWO_TIER (STC
provides the PROMOTION CRITERION for young -> old).

## Required arms (5)

1. `ARM_BASELINE_NO_DOWNSCALE` -- rail (reproduces Cell A/B baseline drift; gamma=1.0)
2. `ARM_GLOBAL_DOWNSCALE_99_100` -- reproduces Cell B HARD_FAIL pattern (gamma=0.99 every 100; no selectivity)
3. `ARM_STC_TAG_DECAY_K100_PRP_BUDGET_100` -- main test (K=100, N_PRP=100, J_replay=100, J_downscale=100)
4. `ARM_STC_TAG_DECAY_K500_PRP_BUDGET_50` -- sparser PRP (scarcity test; longer tag-life, smaller pool)
5. `ARM_STC_TAG_DECAY_K100_PRP_BUDGET_INFINITY` -- CONTROL (no bounded PRP; tests whether bounded-pool IS the lever vs just "tag-based mask")

Discriminator: if main STC arm passes AND infinity-PRP arm fails -> bounded-pool IS the lever
(brain-novel scarce-resource competition). If both pass equally -> selectivity-mask alone
suffices (PRP-bounding not load-bearing). If both fail -> STC mechanism unhelpful at this regime.

## Pre-reg bands (LOCKED via module-init assert; sacrosanct both ways)

- `HARD_PASS_STC_SELECTIVITY_WORKS`: best_STC_arm `final_forget <= 0.20` AND `min_integrity >= 0.95`
  AND `drift_reduction (baseline_forget - best_forget) >= 0.30` AND `cv <= 0.07`
- `HARD_PASS_PARTIAL`: `drift_reduction >= 0.20` absolute but not all conditions met
- `MIDDLE_BAND`: `drift_reduction in (0.05, 0.20)`
- `HARD_FAIL_STC_DOESNT_HELP`: `drift_reduction <= 0.05` OR best STC arm worse than BASELINE
- `HARD_FAIL_DESTROYS_OLDER_LIKE_GLOBAL`: ANY STC arm WORSE than baseline by `>= 0.05`
  (reproduces Cell B failure mode; selectivity NOT working)

Forget metric: `1 - mean retrieval accuracy on first RECALL_PROBE_M oldest atoms` (forget-prone tail).
Integrity: `mean cleanup-cosine on probe set`.

## Config

- `N = 4096` (META_M7: capacity-sensitive dims IDENTICAL smoke/full)
- `N_CYCLES = 2500` (FULL); alpha at end = 2500/4096 = 0.61 (~4.4x past Hopfield 0.14 cliff)
- `SEEDS = [11, 13, 19]` (3 seeds)
- `RECALL_PROBE_M = 100`
- `CHECKPOINT_INTERVAL = 250`
- `NOISE_FRAC = 0.10`; `N_RETRIEVE_STEPS = 5`
- `theta_tag = 0.5` (bipolar atoms -> |dW|=1.0 everywhere -> all writes tag; brain-analogous)
- Substrate-only at inference (numpy + sign() Hopfield cleanup)
- Zero LLM forward calls; `ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"`

## Smoke verification (LOCAL CPU, 2026-06-26)

- Self-test (5 formula tests + bands lock): PASS
- Smoke (1 seed, 500 cycles, N=4096): runs end-to-end
- Per-arm-seed wall MEASURED (Fix #17 strict):
  - BASELINE: ~34s
  - GLOBAL: ~36s
  - STC_K100_PRP100: ~99s
  - STC_K500_PRP50: ~95s
  - STC_K100_INFINITY: ~95s
- Mechanism validated: tags fire (n_tag = 16.78M at cycle 100), capture accumulates at predictable
  rate (`n_pers = J_replay_count * N_PRP`), persistent-fraction non-trivial (400/16.78M for
  bounded arm; full saturation for INFINITY)
- Smoke verdict: `HARD_FAIL_STC_DOESNT_HELP` (EXPECTED at smoke alpha=0.122 < 0.14 Hopfield cliff:
  baseline gets perfect recall too; nothing to discriminate. FULL alpha=0.61 needed for cliff.)

## Fix #17 budget calculation

```
smoke_wall_per_arm_seed = max(99s for STC arms)
full_scaling = 2500 / 500 = 5.0 (N_CYCLES; N IDENTICAL smoke/full per META_M7)
n_arms = 5
n_seeds = 3

per_arm_seed_full = 99 * 5.0 = 495s for STC arms; 35 * 5.0 = 175s for non-STC arms
total_compute = 3 seeds * (2 * 175 + 3 * 495) = 3 * 1835 = 5505s = ~91.75 min
safety_1.5x = 91.75 * 1.5 = ~138 min = ~2h18m
```

Conservative `--timeout 14400s (4h)` to absorb remote_cpu queue overhead +
matmul jitter + checkpoint-resume overhead. PROT-021 satisfied (script imports
`_seed_checkpoint`). PROT-019 not triggered (anchor name has no `_n<N>` suffix).

## Disciplines satisfied

- ASCII only (verified)
- Substrate-only at inference (zero LLM forward calls; ENCODER_PROVENANCE stamped)
- Per-arm metrics (Fix #28: per-(arm,seed) entries in `arms_aggregate`; verdict reads
  per-arm not summary verdict_msg)
- META_M7 capacity-sensitive N IDENTICAL smoke/full
- Per-seed + sub-arm checkpoint (PROT-021 + TWO_TIER pattern)
- 5 formula self-tests + module-init bands lock + atexit flush summary
- `predispatch_check.py` PROCEED for `gap4_stc` keywords (no prior); HOLD on `stc` keywords
  due to cascade_stc_swr_v2 HARD_FAIL -- DISTINCT mechanism family (cascade STC+SWR uses
  sharp-wave-ripple replay coincidence; this cell uses Frey-Morris bounded-PRP), so proceed
  justified
- ASCII filename only

## Routing rationale

- USER directive 2026-06-26: route to `remote_cpu_queue` (USER traveling to airport)
- numpy-only cell (no torch) -> remote_cpu_queue is correct queue (PROT-020 N/A for non-GPU)
- ~2h18m budget fits remote_cpu well below 4h timeout floor
- Sub-arm checkpoint = max 1-arm wall (~8min STC arm or ~3min non-STC arm) lost on any
  resume / kill / hang

## Honest scope

Cell tests STC mechanism at single corpus (random bipolar atoms, the substrate's continual-write
microcosm from Cell A/B). Brain-fidelity of mechanism HIGH; substrate-product extrapolation to
text corpora is OPEN (Cell 3 composition test deferred per handoff: only meaningful AFTER M5 lands
HARD-PASS individually; estimated 6-8 CPU-hr long-horizon).

Failure modes anticipated:
- HARD_FAIL_DESTROYS_OLDER: PRP-saturated INFINITY arm could downscale insufficiently-distinguished
  weights and reproduce Cell B; this is the CONTROL working.
- HARD_FAIL_DOESNT_HELP: at alpha=0.61, Hopfield single-tier W may itself be too saturated for
  STC to recover the dwindling tail; would point to TWO_TIER composition as next step (which is
  in flight as ANCHOR_2 sibling).
- HARD_PASS_PARTIAL: drift_reduction 0.20-0.30 is real selectivity but capped; would trigger
  longer-horizon Cell 3 dispatch.
