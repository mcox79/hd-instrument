# Pre-registration: stc_tag_decay_window_v3

Date: 2026-06-27
Author: exp_dev
Drill spec: notes/research_drill_3x_stc_v1_v2_revival_2026-06-27.md (TOP-1 / Cell 1)
Cell: experiments/exp_stc_tag_decay_window_v3.py
Anchor: stc_tag_decay_window_v3

## Question

Does substrate Hebbian + multiplicative decay + tagged-item capture into a
protected (non-decaying) sub-matrix produce a SELECTIVE retention asymmetry
in which tagged items survive while untagged items decay -- without the
protection coming from spurious quasi-orthogonality?

This is the v1/v2 revival per Research drill TOP-1. Root cause from drill:
v1/v2 HARD_FAILed because they had no untagged-decay mechanism. Substrate
Hebbian `W += x x.T` with HD-quasi-orthogonal vectors does NOT catastrophically
forget at M << N_DIM/8 -- it preserves perfectly because additive storage on
orthogonal codes is the "early-LTP without protein synthesis" steady state,
not the "decayed-untagged" state STC is supposed to protect against. v3 adds
the missing baseline mechanism: explicit multiplicative decay between writes,
with tagged items captured into a separate protected (non-decaying) matrix.

## Hypothesis

Tagged items will retain near-baseline weight-norm signal magnitude (>= 80%)
while untagged items decay to <= 30% of baseline, with selectivity (STC vs
random-tag-matched control) lift >= 10%. Baselines must diverge: no-decay
preserves both subsets at ~100%; with-decay collapses both at <= 40%.

## Arms (4)

1. **ARM_BASELINE_NO_DECAY** -- Substrate Hebbian `W += x_i x_i.T / N` with no
   decay. Reference / "max signal" baseline. Expected: both subsets at 100%
   weight-norm. Used for normalization of all other arms.

2. **ARM_BASELINE_WITH_DECAY** -- Substrate Hebbian + `W *= (1 - lambda)` per
   write step, no tag protection. Regime-fire check: should forget both
   subsets to <= 40% weight-norm. If it doesn't, lambda/M/T regime is too
   weak to test STC.

3. **ARM_STC_TAGGED_DECAY** (PRIMARY) -- Two-matrix substrate. W_decay
   receives all writes + per-step decay. W_protected receives only tagged-
   item writes and never decays. Readout W_total = W_decay + W_protected.
   Expected: tagged items at >= 80% (signal in W_protected), untagged at
   <= 30% (only in W_decay, fully decayed).

4. **ARM_RANDOM_TAG_PROTECTED** (CONTROL) -- Same two-matrix mechanism as
   STC, but with RANDOM item selection at matched density. Recall measured
   against STC's tagged_mask (the items we want to protect). Expected:
   random misses ~50% of the items STC chose, so random.tagged ~ midway
   between STC.tagged and STC.untagged. Proves SELECTIVITY (not density)
   is load-bearing.

## Regime

- N_DIM = 8192
- M_ITEMS = 200 (items stored)
- T_PRP = 50 (PRP-pulse window parameter, currently not gating; implementation
              note: tagged items captured indefinitely; T_PRP refinement = v4)
- T_POST = 200 (decay-only steps after all writes)
- LAMBDA_DECAY = 0.02 (multiplicative decay per step)
- TAG_FRACTION = 0.50 (deterministic 100 tagged of 200 via random index choice)
- SEEDS = [11, 13, 19, 23, 29] (5 seeds)
- ALPHA_LOAD = M/N = 200/8192 = 0.024 (well below Hopfield capacity 0.138 to
   avoid baseline-no-decay collapsing on capacity-saturation)
- CARDINALITY_OK: 5 seeds * 4 arms = 20 units

## Discriminators (primary: weight_norm normalized by no-decay reference)

CRITICAL FINDING from smoke verification: argmax-retrieval@1 is NOT sensitive
to multiplicative decay (decay attenuates signal AND cross-talk equally,
preserving SNR). Biological STC literature measures fEPSP AMPLITUDE
(synaptic weight magnitude); substrate-faithful translation is
`weight_norm = ||W @ x_i||`. Normalized by baseline_no_decay reference.

### HARD_PASS

ALL of:
- stc.tagged_wnorm / no_dec.tagged_wnorm >= 0.80
- stc.untagged_wnorm / no_dec.untagged_wnorm <= 0.30
- baseline_with_decay.untagged_wnorm / no_dec.untagged_wnorm <= 0.30
- baseline_no_decay.untagged_wnorm / no_dec.untagged_wnorm >= 0.80 (= 1.0 by construction)
- tag_fraction observed in [0.40, 0.55]
- stc.tagged_wnorm - random.tagged_wnorm >= 0.10 (selectivity lift)
- cv across seeds < 0.10

### MIDDLE_BAND

- stc.tagged_wnorm in [0.50, 0.80), OR
- stc.untagged_wnorm in [0.30, 0.50], OR
- selectivity lift in [0.05, 0.10)

### HARD_FAIL

- stc.tagged_wnorm < 0.50 (mechanism doesn't preserve)
- OR stc.untagged_wnorm > 0.50 (no decay differential)
- OR baseline_with_decay.untagged_wnorm > 0.40 (REGIME_BROKEN_DECAY_DOESNT_FORGET)
- OR baseline_no_decay.untagged_wnorm < 0.80 (REGIME_BROKEN_NO_DECAY_FORGETS;
   impossible by construction but guarded)
- OR cardinality breach

## Anti-saturation regime gate (PRE-discriminator)

Before judging mechanism, the regime MUST show divergence between the two
baselines:
- BASELINE_NO_DECAY untagged_wnorm >= 0.80
- BASELINE_WITH_DECAY untagged_wnorm <= 0.40

If both don't hold, verdict = HARD_FAIL REGIME_BROKEN. This is the drill's
ANTI-SAT gate guarding against tautological "STC preserves" claims when
the baseline already preserves perfectly.

## Smoke gate (PRE-FULL-DISPATCH)

- N_DIM = 512, M = 50, lambda = 0.08, T_PRP = 10, T_POST = 50, 2 seeds.
- Lambda scaled UP at smoke (0.08 vs 0.02) so total decay over 100 steps is
  comparable to full's 400 steps (smoke: 0.92^100=0.00026; full: 0.98^400=
  0.00029) -- discriminator-survives-scale by analytical equivalence.
- Smoke must achieve the same HARD_PASS bands.
- SMOKE VERIFIED 2026-06-27 (laptop, .venv):
  nd_un=1.000, wd_un=0.004, stc_t=0.942, stc_u=0.198, rand_t=0.582,
  selectivity=0.360, tag_frac=0.500, cv=0.001 -> HARD_PASS at smoke.

## Fairness gates (META_RULE_AA)

- All 4 arms read the SAME way: weight_norm = ||W_total @ x_i|| over subset.
- Same M, T_POST, N_DIM, lambda_decay across arms (only tag-protection mechanism varies).
- Tag fraction explicitly bounded; verified ~= 0.50 at selftest+smoke.
- Smoke discriminator MUST FIRE (baseline_with_decay forgets; no_decay does not).
- Random arm reads against the SAME tagged_mask as STC, ensuring we're comparing
  protection OF THE SAME ITEMS not just protection of any subset.

## Hardening (META_RULE_X L1-L4)

- L1: STARTED metrics.json on entry (pre-init).
- L2: per-seed partial via _seed_checkpoint.write_partial_key (resumable).
- L3: outer try/except wraps main(); writes UNKNOWN sentinel on outer crash.
- L4: import-crash sentinel writes metrics.json if module import fails.
- Per-arm + per-seed metrics in metrics.json (Fix #28: prevents over-claiming
  from verdict_msg only).

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) = 5 * 4 = 20 for full.
- HARD_FAIL_CARDINALITY_BREACH if completed_units < EXPECTED_N_UNITS.
- selftest=4, smoke=8 also explicitly declared.

## Anti-mode confounds

- ASCII only; no emojis; no em-dashes.
- No silent `except:` blocks; all exceptions re-raised or recorded.
- Sub-Hopfield-capacity (alpha=0.024 << 0.138) prevents capacity-saturation confound.
- bipolar items deterministically constructed from seeded RNG.
- TAG_FRACTION designed at 0.50 to allow clean both-direction bounds.

## Result-to-application (USER 2026-06-22)

If HARD_PASS at full:
- Substrate gains BRAIN-CORRECT selective consolidation primitive.
- Atomize into Store atoms: "selective_consolidation_via_two_matrix_decay" mechanism.
- Update hdlab/ with `tag_decay_window` module: dual-matrix Hebbian + per-tag-item
  protection class for use in capacity-management + meaningful importance signals.
- Enables Stage 3 compositional-understanding work where some patterns must
  be remembered selectively across many writes.

## Sources

(per drill TOP-1)
- Frey & Morris 1997 (synaptic tagging discovery, Nature)
- Tag-Trigger-Consolidation model (PLOS Comp Bio)
- arxiv:2202.00159 (heteroassociation scaffold for catastrophic-forgetting avoidance)
