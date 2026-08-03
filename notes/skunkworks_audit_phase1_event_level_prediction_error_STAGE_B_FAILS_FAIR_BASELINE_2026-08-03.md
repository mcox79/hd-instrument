# Skunkworks landed-VET: Phase 1 event-level prediction-error cell (commit 2247466e2)

Auditor: hdi_skunkworks (AUDIT-ONLY). Cell under audit:
`experiments/exp_event_level_prediction_error_relation_inference_phase1_v1.py` /
`data/exp_event_level_prediction_error_relation_inference_phase1_v1/metrics.json`.

All numbers below are independently recomputed off disk (`.venv` python, bit-exact
reproduction of the cell's own seeds/pipeline), not read from the cell's verdict_msg.

## Finding 1 -- Stage B does NOT survive a fair baseline (DISQUALIFYING)

Recompute matches metrics.json bit-for-bit: `mse_test_trained=0.33236`,
`mse_test_random_init=0.64922`, `cosine_test_trained=0.5796`,
`cosine_test_random_init=0.0305`. Reproducible, deterministic, no leakage in the
train/test pair construction (verified `make_train_test_pairs`: train pairs use only
event indices `< split_idx`, test pairs only `>= split_idx`, no pair straddles the
boundary -- code matches the pre-reg's no-leakage claim).

BUT: a trivial constant "predict the training-set mean event-vector" baseline
(no context, no learning) scores `mse=0.33107` -- SLIGHTLY BETTER than the trained
predictor (0.33236), and `cosine_mean_baseline=0.5813` -- also slightly better than
the trained predictor's reported cosine (0.5796). Most decisive: the trained
predictor's per-item test-set outputs are `cosine=0.98` similar to the CONSTANT
mean-of-training-targets vector (computed directly, not estimated) -- i.e. the
"learned" predictor outputs are ~98% identical regardless of the input context.
It has converged to (very nearly) a content-blind constant, not a genuine
context-conditioned next-event-state predictor.

The `mse_test_random_init=0.64922` control used as the must-fail baseline is an
inflated strawman: an untrained random 128x128 linear map on unit-magnitude FHRR
real-encodings produces near-orthogonal output (cosine~0.03, mse~full variance),
which is a much weaker null than "predict the corpus mean" (mse=0.331,
cosine=0.581). The reported "48.8% relative MSE improvement / cosine 0.03->0.58"
is entirely explained by mean-reversion of an L2-regularized linear regressor
under weak signal, not by learned sequential/predictive structure. Two other
fair-baseline checks for context: copy-context-as-prediction mse=0.602 (worse
than mean, still much better than random-init's 0.649); zero-vector baseline
mse=0.500. All three non-learned/trivial-baselines beat or tie the RANDOM_INIT
control the cell used, and one of them (predict-train-mean) also ties/slightly
beats the TRAINED model.

`stage_b_pass=True` in metrics.json is real (the comparison it actually performed
passes), but the comparison itself is not a fair test of "did the mechanism learn
anything." Root cause = (b) trivial predict-the-mean effect, confirmed directly
(not inferred).

## Finding 2 -- random-init below-chance on Stage C: NOT a scoring bug, is small-N variance

Recompute reproduces every reported number bit-for-bit at `PREDICTOR_SEED=71001`:
unstated_goal random=2/12 (0.1667), satisfy_restate random=1/7 (0.1429),
thwart_cause random=0/6 (0.0) -- all match metrics.json exactly.

Swept 8 different predictor-init seeds (1,2,3,4,5,999,12345,71001) through the
IDENTICAL readout pipeline (same event structs, same gold items, same
`structure_overlap` / `_tie_break_pick` reused verbatim, no code changes):

```
seed=71001: unstated=2/12  satrest=1/7  thwart=0/6   <- the seed actually used
seed=1:     unstated=4/12  satrest=2/7  thwart=3/6
seed=2:     unstated=2/12  satrest=5/7  thwart=5/6
seed=3:     unstated=2/12  satrest=4/7  thwart=1/6
seed=4:     unstated=3/12  satrest=3/7  thwart=5/6
seed=5:     unstated=2/12  satrest=3/7  thwart=2/6
seed=999:   unstated=4/12  satrest=4/7  thwart=2/6
seed=12345: unstated=2/12  satrest=4/7  thwart=4/6
```

Thwart_cause ranges 0/6 to 5/6 across seeds (mean ~2.75/6 = 0.458, close to
chance 0.5); satrest ranges 1/7-5/7 (mean ~3.25/7=0.46); unstated ranges 2/12-4/12
(mean ~2.6/12=0.217, slightly under nominal 0.25 but not distinguishable from
noise at n=8 seeds). Seed 71001 happens to be the single WORST draw among the 8
sampled seeds on thwart_cause (the literal minimum, 0/6). This is ordinary
small-N binomial variance in an (on average, roughly unbiased) control, NOT a
sign-flip / tie-break / structure_overlap scoring bug. `structure_overlap` and
`_tie_break_pick` were confirmed reused verbatim from already-vetted upstream
modules (v5/v6c), no reimplementation drift found. Minor secondary caveat: the
across-seed means sit slightly below nominal chance on all three axes; worth
re-checking with more seeds if this control is ever load-bearing again, but not
disqualifying on its own.

## Finding 3 -- Interpretation audit: "mechanism sound, readout is the bottleneck" is an OVER-READ

`notes/WHERE_WE_ARE_NOW.md` (top banner, 2026-08-03) frames this result as: "Stage
B (THE mechanism, can-fail): PASSED cleanly ... the event-level prediction-error
mechanism GENUINELY LEARNS ... the honest read: the MECHANISM (Stage B) is a real
clean pass; the end-to-end signal is NARROW; readout may be buggy."

Both halves of that framing are corrected downward by the recompute above:

- Stage B is NOT a genuine clean pass. It fails a fair baseline (predict-the-mean
  ties/slightly-beats it; trained output is 98% cosine-identical to the constant
  mean). The comparison the cell ran (trained vs random-init) used an inflated
  strawman, not a fair null.
- The Stage C random-init below-chance readings are NOT evidence of a readout
  bug. Confirmed via 8-seed sweep: the control is (roughly) unbiased on average;
  seed 71001 is simply an unlucky small-N draw.

Correct honest read (symmetric anti-negativity, same rigor applied to a claimed
positive as to a negative): no genuine event-level predictive mechanism has been
demonstrated by this cell. The apparent Stage-B "win" is a mean-reversion
artifact of an unfair baseline choice; Stage C's oddities are small-N noise, not
signal about the readout's soundness. `PHASE1_MECHANISM_WORKS=False` in
metrics.json is the correct top-line verdict, but for a different and more
serious reason than the cell (and WHERE_WE_ARE_NOW.md) state:
`insufficiency_reason` should read something like
`STAGE_B_DID_NOT_BEAT_A_FAIR_TRIVIAL_BASELINE` rather than pinning the
insufficiency solely on Stage C.

## Tier and recommendation

TIER: BAD (deflated). This is closer to an honest-negative (HARD_FAIL) at Stage B
itself than to "mechanism proven, readout narrow." Not atomized as chain-grade or
proven-bound; recording here as a downward correction pending Director/cell-author
follow-up (no atoms.jsonl / cert_ledger.jsonl write performed by this audit -- the
cell's own verdict is already False and this note documents WHY, for the record).

RECOMMEND: Phase 2 (harden segmentation / build a multi-step through-model reader)
is NOT justified on this evidence. Before further investment: (1) add a FAIR
baseline arm to Stage B's can-fail gate -- predict-train-mean AND/OR
copy-context-as-prediction -- and require the trained predictor to beat BOTH, not
just an untrained random linear map; (2) if a linear delta-rule predictor over
this exact bundled 2-event window genuinely cannot beat predict-the-mean even
with more epochs/capacity, that is an honest HARD_FAIL for this specific
recipe (linear map, window=2, this event-struct encoding) -- state it as such
with explicit revival criteria (nonlinear predictor; richer/longer context;
clause-level segmentation improving signal-to-noise) rather than proceeding to
harden the readout on a foundation that has not yet demonstrated real predictive
signal.
