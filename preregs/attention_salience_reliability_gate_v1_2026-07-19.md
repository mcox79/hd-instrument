# Pre-registration: attention/salience RELIABILITY-GATE delta (v1)

Cell: `experiments/exp_attention_salience_reliability_gate_v1.py`
Author: hdi_exp_dev. Date: 2026-07-19.
Spec sources:
- `notes/SYNTHESIS_missing_elements_prior_art_adopt_adapt_buildfresh_2026-07-20.md` (Attention/salience row:
  ADOPT Kalman-gain precision-weighting / divisive-normalization / sparsemax / IDF-Itti-Koch; "likely already
  partially built (surprise = IDF family); delta = reliability multiplier + hard-gate")
- `notes/ACCOUNTING_substrate_vs_brain_foundation_discrepancies_2026-07-20.md` (attention/selective-gating
  TOTAL GAP, item #3 cheap de-risk-real-text priority)

## PRIOR-WORK CHECK (substrate-KB concept-query discipline, exp_dev standing rule)
Ran `bash tools/substrate_query.sh "attention salience reliability gate precision weighting Kalman gain IDF
surprise"`. Top hit cosine=0.2832 ("Precision weighting: Friston (2009)... gain on prediction error signals
controlled by precision (inverse variance)...", source `notes/research_drill_continuous_truth_biology_3x_2026-06-09.md`)
-- a BIOLOGY-DRILL note, not a prior EXPERIMENT CELL, and below the 0.30 cosine threshold. **Prior-work check:
NONE at cosine>0.30 among prior arc CELLS** -- the KB's top hits are all research-drill notes on the Friston/
precision-weighting theory (expected; that's the credited prior art this cell implements), not a duplicate
implementation. Cross-checked separately (grep, not KB-search) across hdlab/experiments/backend for the actual
CODE-level surprise/salience signal, reported below.

**Located + characterized the existing surprise/salience signal (CONFIRMED IDF-family, per contract Step 1):**
- `experiments/exp_surprise_gating_b3b_synthetic_pool_recapture_v1.py:141-144`: `surprise = -np.log(probs)`,
  min-max normalized. This is the literal IDF formula (`idf = -log(p)` = `log(1/p)`; rare/low-probability
  items score high). CONFIRMS the synthesis hypothesis directly — this is not an analogy, it is the identical
  closed form. That cell's task was surprise-GATED WRITE/eviction on a Zipf memory pool; landed verdict =
  `HONEST_BOUNDED` (three named-failure-mode lifts over the un-lifted gate all landed ~0; MEASURED@
  data/surprise_gating_b3b_synthetic_pool_recapture_v1/metrics.json:verdict_msg).
- `experiments/exp_importance_6channel_brain_analog_v1.py:11`: channel 1 `NOVELTY = 1 - max_cosine_to_others`
  (norepinephrine-surprise analog, a distance/rarity family member) and channel/fusion-strategy C
  `FISHER_INFO_WEIGHTED = 1/var per-channel` (line ~480-491) — this IS a precision-weighting / Kalman-gain-
  family FUSION already coded as an arm. Landed status: only `SELFTEST_OK` on disk (MEASURED@
  data/exp_importance_6channel_brain_analog_v1/metrics.json:verdict_msg) — never landed a FULL verdict; not a
  chain-grade result to build on, but confirms the precision-weighting concept (1/variance reliability weight)
  is already present in the codebase as a design pattern, reinforcing the synthesis's "partially built" call.
- `hdlab/predictive_coding.py`: residual-gated write (Feldman-Friston free-energy framing already cited in the
  module docstring) — gates Hebbian WRITE STRENGTH by prediction-residual magnitude. This is a NOVELTY/surprise
  gate (should-we-care), not a RELIABILITY gate (can-we-trust-this-observation) — a related but distinct axis;
  confirms novelty-family machinery exists, reliability-family does not.

**Novelty call:** the SURPRISE (IDF/novelty/residual) family is CONFIRMED already built across 3 independent
modules. NONE of the 3 test a RELIABILITY estimate (an independent, per-observation trust/confidence score
uncorrelated with the observation's own novelty) used to down-weight or hard-suppress a noisy/untrustworthy
input BEFORE it contaminates a consolidated representation. This cell is the genuinely novel delta: same
"gate a stream of inputs" shape as `surprise_gating_b3b` and `predictive_coding.py`, but wired to a DIFFERENT
signal (reliability, not novelty) and a DIFFERENT downstream harm (consolidation contamination, not pool
eviction). Not a rediscovery of the b3b or predictive_coding results.

## DESIGN-GATE DISCIPLINE (per USER 2026-07-17, verified BEFORE full)

**Real baseline:** `ungated` = uniform-weight average of ALL observations per item, majority-vote sign-cleanup.
This is literally today's substrate default consolidation behavior (no reliability layer at all) — not a
strawman.

**Discriminator CAN fail:** an early prototype regime (i.i.d. incoherent corruption, N=512, r_unreliable=0.30)
saturated the baseline near ceiling (majority vote is already robust to i.i.d. random noise at those params) —
this HARD_FAIL-by-construction regime was REJECTED and the regime was hardened (lower N=128 for less argmax
headroom, lower r_unreliable=0.15, more items V=100) until baseline lands in the discriminating band. A SECOND
early prototype (reliability estimated via leave-one-out self-consistency alone, no exogenous confidence
signal) was ALSO rejected: when true observations are a minority (r<0.5), self-consistency estimation
systematically HURTS (the noise majority looks "consistent" to itself) — a real, informative negative that
matches why Kalman-gain precision-weighting in the brain uses an INDEPENDENT reliability channel (e.g.
receptor/synapse-level noise estimate), not a majority-vote-derived one. The FINAL design below uses an
exogenous, imperfect confidence signal (Beta-noise around ground-truth correctness) — informative but NOT a
ground-truth leak (AUC of confidence vs. true correctness ~0.85-0.90 in the fixed regime, not 1.0).

**Difficulty ON:** `base_unrel` (baseline accuracy restricted to the low-reliability item subset) measured in
[0.50, 0.70] across 5 dev-sim seeds (HYPOTHESIZED@this-doc pre-registration, to be MEASURED@landed metrics.json
at cell run) — comfortably inside META_RULE_AG's (0.05, 0.95) band, nowhere near saturation or floor.

**One variable differs across arms:** the WEIGHT FUNCTION applied to the (identical, shared) per-observation
confidence score before averaging into the consolidated vector. Same confidence-score computation reused
across `hard_gate` / `soft_multiplier` / the shuffled controls; only the transform (uniform / step-at-tau /
identity-clip / step-at-tau-on-shuffled / identity-clip-on-shuffled) differs. `oracle` is a diagnostic-only
ceiling arm (uses the TRUE hidden correctness label, not the confidence signal) and is explicitly OUT OF the
HARD_PASS/HARD_FAIL gate scope (HP_SCOPE below).

## THE MECHANISM

Per item i (V items, half "reliable" sources r=0.92, half "unreliable" sources r=0.15 — a per-ITEM fixed
reliability, modeling heterogeneous input sources e.g. clean vs noisy extraction pipelines): observed
`n_obs in [6,10]` times. Each observation is the TRUE bipolar code (prob r_i) or an unrelated random bipolar
"corruption" (prob 1-r_i). Each observation ALSO carries an EXOGENOUS confidence score drawn from
`Beta(8,2)` if it happens to be a true-value draw, `Beta(2,8)` if corrupted — informative but noisy (an
extraction-confidence / OCR-confidence / sensor-confidence analog), NEVER revealing the hidden correctness
label directly to the gate.

Consolidation = weighted bipolar sum -> sign cleanup: `consolidated_i = sign(sum_j w_j * obs_j)`.
- `ungated`: w_j = 1 for all j (today's default).
- `hard_gate`: w_j = 1 if conf_j >= TAU else 0 (hard suppression of low-confidence inputs).
- `soft_multiplier`: w_j = clip(conf_j, 0, 1) (continuous Kalman-gain-style precision weighting).
- `shuffled_hard_gate` / `shuffled_multiplier` (MUST-FAIL CONTROLS): identical transforms but applied to
  `conf` permuted across observations WITHIN each item (severs the confidence score from the observation it
  actually describes; retains its marginal distribution). If gating merely regularizes toward a decisive
  vote irrespective of information content, these controls would recover the same lift as the real arms; if
  the lift is genuinely information-carrying, shuffling must destroy or reverse it.
- `oracle` (diagnostic ceiling, NOT HARD_PASS-gated): w_j = hidden true-correctness label (upper bound on
  achievable lift at this regime; sanity check only).

Retrieval metric per item: nearest-neighbor cleanup of `consolidated_i` against the FULL V-item codebook
(argmax cosine); accuracy = fraction of items where argmax recovers the correct index. Reported split by
item-reliability tier (`_unrel` = low-reliability item subset = PRIMARY / LOAD-BEARING metric per contract's
"cuts harm from low-reliability inputs"; `_rel` = high-reliability subset = do-no-harm check; `_all` = overall).

## PRE-REG BANDS (envelope-fail-bands; locked BEFORE full dispatch)

Regime: V=100 (50 reliable-source items / 50 unreliable-source items), N=128, n_obs in [6,10] uniform,
r_reliable=0.92, r_unreliable=0.15, TAU=0.5, conf~Beta(8,2)|Beta(2,8). SEEDS_FULL=[7,17,23,31,41] (5 seeds).
SEEDS_SMOKE=[7] (1 seed, SAME regime params — Option A of DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke runs at
full-N; there is no separate "scaled-up" full regime here, the full run itself completes in well under 1s of
wall time, so smoke = full-regime/1-seed preview, not a reduced-N toy).

**HARD_PASS** (both required, ALL sub-conditions):
1. `mean_over_5_seeds(delta_hard_unrel) >= 0.05` AND `mean_over_5_seeds(delta_mult_unrel) >= 0.05`, where
   `delta_X_unrel = acc_X_unrel - acc_ungated_unrel`.
2. `>= 4/5 seeds` show `delta_hard_unrel > 0` AND `>= 4/5 seeds` show `delta_mult_unrel > 0` (majority-positive
   direction, not a single lucky seed).
3. Must-fail controls: `delta_shuffled_hard_unrel <= 0.00` AND `delta_shuffled_mult_unrel <= 0.00` on ALL 5
   seeds (shuffling the confidence score must not recover the lift; per dev-sim prototype the shuffled arms
   are clearly WORSE than ungated, giving ample separation margin, not a floor-hugging 0.00).
4. Do-no-harm: `mean_over_5_seeds(delta_hard_rel) >= -0.03` AND `mean_over_5_seeds(delta_mult_rel) >= -0.03`
   (gating must not meaningfully hurt already-reliable items).
5. `baseline_in_band`: `0.05 < acc_ungated_unrel < 0.95` on every seed (META_RULE_AG; difficulty genuinely on).

**HARD_FAIL** (either):
- `mean_over_5_seeds(delta_hard_unrel) <= 0.02` AND `mean_over_5_seeds(delta_mult_unrel) <= 0.02` (ties/loses
  to the ungated baseline on the load-bearing low-reliability subset) -> the reliability-multiplier + hard-gate
  delta is INERT for this substrate's consolidation primitive; genuine negative, not tortured to avoid it.
- OR `baseline_in_band` violated (saturated/floored) -> non-test, re-spec regime before re-dispatch.

**MIDDLE_BAND**: any other outcome (e.g. positive but < 0.05 mean lift, or majority-direction gate (3) fails
on 4-5 seeds, or do-no-harm violated on one arm but not the other).

**HP_SCOPE** (META_RULE_L 5b, per-arm HARD_PASS gate applicability):
```yaml
HP_SCOPE:
  ungated: []            # baseline reference, no gate applies to it
  hard_gate: [delta_hard_unrel_floor, delta_hard_unrel_direction, shuffled_hard_control, do_no_harm_hard]
  soft_multiplier: [delta_mult_unrel_floor, delta_mult_unrel_direction, shuffled_mult_control, do_no_harm_mult]
  shuffled_hard_gate: [must_fail_control_only]     # sentinel arm; HARD_PASS gates do NOT apply to it directly
  shuffled_multiplier: [must_fail_control_only]    # sentinel arm; HARD_PASS gates do NOT apply to it directly
  oracle: []              # diagnostic ceiling ONLY, explicitly excluded from HARD_PASS/HARD_FAIL decision
```

## SCHEMA-VET / CELL-TEMPLATE FIELDS

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = len(SEEDS) (5 full / 1 smoke); verdict counts len(per_seed)
arms_differ_verified: true           # hash-checked at smoke: 6 arms produce distinct consolidated-vector sets
                                      # (ungated != hard_gate != soft_multiplier != shuffled_hard != shuffled_mult != oracle)
final_metrics_atomicity: "tmp_replace"   # single-shot; whole cell (5 seeds) completes in <1s wall time; tmp+os.replace
except_ordering: "SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare/BaseException"
crlb_n_a: "not a CRLB/JL-capacity cell; V=100,N=128 argmax cross-talk margin is ample (oracle_all/_rel ~0.85-0.95,
  confirms cleanup headroom is not the bottleneck). The measured floor is CONTAMINATION of the consolidated
  vector by corrupted observations pre-cleanup, not argmax/JL noise; that's what the gate acts on."
discriminator_reachability: true
baseline_in_band: "verified at smoke (V=100,N=128, seed=7): acc_ungated_unrel=0.66 in (0.05,0.95)"
discriminator_survives_scale: "Option A -- smoke IS full-N/full-V (same regime, 1 seed); no separate scale-up exists"
cell_chunked: false           # single-shot <1s total across all 5 seeds; chunking overhead not warranted
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false      # justified: total wall time <1s, well under the 15-min heartbeat threshold (Sec 17 n/a, timeout_s well below 1800)
progress_logging: "n/a -- timeout_s < 1800 (cell completes in <5s); Sec 17 threshold not met"
defensive_error_checking: "passed_all_4_patterns (start_marker + crash_diagnostic present; heartbeat exempted per above; chunking exempted per above)"
deterministic_seeding: true   # np.random.default_rng(fixed int seed) throughout; no hash()-derived seeding; sorted() not needed (no set-based split)
calibration_check: "default_ok_for_this_regime -- TAU=0.5 sits at the Beta(8,2)/Beta(2,8) crossover (natural
  discriminating threshold given the two confidence distributions' overlap region); not adaptively tuned post-hoc"
```

## TIMEOUT / DISPATCH

Wall time: <1s total for all 5 FULL seeds (pure numpy, V=100 x N=128 x ~8 obs/item x 5 seeds). No queue
dispatch needed or used — this is a lightweight closed-form measurement run FOREGROUND to completion per
the compute-proportionality discipline (a directional gate question; a full training fit would be
over-engineering). `--timeout 60` if ever routed through queue_add.sh (generous 60x margin over measured
wall time); not applicable here since run is foreground/local, not queued.

## GOVERNANCE

Pause-flag checked before this run: `data/orchestrator_paused.flag` absent (verified 2026-07-19). No origin
push, no remote-persist, no queue_add invoked — local-only per contract. Routes to Skunkworks for adversarial
VET before any atomize/store-write.
