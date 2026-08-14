# exp_forgetting_kernel_signreadout_v1 -- does the terminal sign() destroy the forgetting exponent?

STEP 2 of `notes/SUBSTRATE_STRATEGY.md` (5f850770b). Cell:
`experiments/exp_forgetting_kernel_signreadout_v1.py`.
Pre-registered BEFORE the full run. Commit the prereg and the cell together, before dispatch.

## Prior-work check

`bash tools/substrate_query.sh "forgetting curve retention log-log slope power law exponential
sign quantisation accumulator"` -> top hit `retention` cosine **0.3545** (a WordNet/atoms lexicon
entry, not prior project work); rank 2 `quantisation` 0.3438 (WordNet); rank 3 `CN_attention_getting`
0.335 (concept node). **Prior-work check: NONE above cosine 0.30 that is prior project work.** The
nearest adjacent project note is `notes/research_drill_stdp_replay_decay_model_design_2x_2026-06-04.md`
(named Benna-Fusi, filed metaplasticity as not-justified-first-pass; it never measured a retention
slope). This cell is NOVEL as a measurement, and is the operationalisation of a hypothesis raised in
`notes/drill_cascade_synapse_replay_consolidation_biology_2026-08-14.md` sec 4.4.

## The hypothesis under test (the drill's, sec 4.4, flagged there as its own and pending VET)

> "the live substrate's forgetting exponent is not absent, it is DESTROYED BY THE `sign()`."

`hdlab/reading_grounding_loop.py:465` `ConceptSpace.observe` does `self._sums[lemma] += ctx_vec` --
an unbounded additive integrator. Benna & Fusi 2016's Online Methods derive that such an integrator
ALREADY has `SNR = sqrt(N/t)`, the brain's target `t^-1/2` kernel; the paper's entire contribution is
achieving that with BOUNDED variables. `anchor_matrix:490` / `bundle:504` then apply `np.sign(...)`
one line before use, under the `GRADED_COMPARATOR` switch (`103`), default ON since 38f7a0d5c.

## THE AXIS QUESTION, ANSWERED BEFORE THE RUN (the brief's carried caveat)

The brief and the drill both flag that "our time axis (concepts ingested) is NOT their time axis
(memories stored at this synapse)". **That is correct, and it is a wrong choice of OUR axis, not an
irreconcilability.** The substrate has TWO distinct forgetting channels and only one of them is
Benna-Fusi's:

- **CHANNEL A -- within-lemma superposition. RECONCILABLE, and it is exactly their axis.**
  `_sums[lemma]` is a bank of `d=256` scalar accumulators dedicated to lemma L. Every
  `observe(L, v)` writes to all `d` of them. So **one further encounter of L = one further memory
  stored at L's synapses.** This is Benna-Fusi's `t` with no reinterpretation at all. It is the
  PRIMARY axis of this cell.
- **CHANNEL B -- anchor-dictionary growth.** As more lemmas are grounded, `anchor_matrix()` grows
  more rows and `canonicalize`'s argmax faces more distractors. **NOT a Benna-Fusi channel**: their
  N synapses superpose all memories, they have no dictionary and no argmax. Measured here as a
  SECONDARY section and reported explicitly as NON-reconcilable, never fitted against a BF
  prediction.

Declaring this now so the result cannot be retrofitted: the primary axis is encounters-of-L.

## Measurand

Transplanted verbatim from Benna & Fusi (signal = overlap of the tracked memory's intended
modification pattern with the current weights; noise = its s.d. across the ensemble of subsequently
stored, uncorrelated memories):

```
sum_t   = v0 + sum_{i=1..t} v_i             the accumulator after t further encounters
R(sum_t)= sum_t              (GRADED)
        = np.sign(sum_t)     (BINARISED)    matching ConceptSpace.bundle's own convention
S(t)    = dot(v0, R(sum_t))
N(t)    = sd over K=128 probes u from the unrelated-memory pool of dot(u, R(sum_t))
SNR(t)  = S(t) / N(t)                        <- THE PRIMARY MEASURAND
```

`||R||` cancels between S and N, so SNR is invariant to the readout's overall scale -- which is what
makes GRADED and BINARISED comparable at all.

**PRIMARY STATISTIC: the fitted log-log slope of SNR(t) vs t, with a cluster-bootstrap CI.** A slope
has range by construction and cannot be floor-pinned. No hand-scored quantity gates anything here.

## ANALYTIC PREDICTION, DERIVED AND PRE-DECLARED (this is what makes the run a CHECK, not a fishing trip)

For random bipolar `v_i` in `d` dimensions:

- **GRADED.** `dot(v0, sum_t) = d + O(sqrt(td))`; probe overlap has mean 0 and s.d. `||sum_t||` ~
  `sqrt((t+1)d)`. So `SNR(t) = sqrt(d/(t+1))` -> **log-log slope exactly -1/2**, prefactor `sqrt(d)`.
  This is Benna-Fusi's own unbounded-perfect-integrator result.
- **BINARISED.** Per dimension, `E[v0[j] * sign(v0[j] + W_t)]` with `W_t` a t-step +-1 random walk
  `= E[sign(1 + W_t)] -> sqrt(2/(pi t))`. Signal `~ d*sqrt(2/(pi t))`; noise s.d. `= ||sign(sum_t)||
  = sqrt(d)`. So `SNR(t) ~ sqrt(d) * sqrt(2/(pi t))` -> **log-log slope ALSO -1/2**, prefactor
  reduced by `sqrt(2/pi) = 0.798`.

**Therefore the derivation predicts the drill's hypothesis is FALSE**, and predicts precisely why:
Benna-Fusi's bound is a **STORAGE** bound (information is destroyed at write time, which is what
costs an exponent), whereas our `sign()` is a **READ-OUT quantiser applied to an unbounded stored
sum** -- it costs a constant factor (~20% of SNR level) and no exponent at all. I am declaring this
BEFORE the run precisely so that a confirming result is a check on the derivation and a
disconfirming result is a real surprise. **I have not tuned anything toward this.**

The open part the derivation does NOT settle, and the reason to run: on REAL corpus contexts the
`v_i` are **correlated** (a lemma recurs in similar contexts), which the derivation assumes away. A
systematic shared component makes `sum_t ~ (t+1)*mu_L`, under which SNR should FLATTEN toward an
asymptote rather than decay -- a third shape neither theory predicts. That is measurable only.

## Arms (2 readouts x 4 streams = 8 primary units, + 2 Channel-B units)

READOUT (the flag, set via `os.environ["HD_GRADED_COMPARATOR"]` BEFORE importing hdlab, never as a
shell prefix; one process per readout arm, units sharded by `tools/exp_checkpoint.py`):
- `graded` -- `HD_GRADED_COMPARATOR=1` (default ON)
- `binarised` -- `HD_GRADED_COMPARATOR=0`

Note the flag is coherent across all four sites by design, so it also makes the per-encounter
`context_vector_masked` graded/signed. That is the live-path semantics and is deliberately kept.

STREAM (what the interfering encounters are):
- `synth` -- random bipolar draws. **KNOWN-ANSWER arm**: must reproduce the analytic slope above, or
  the harness is broken and nothing else in the cell is readable.
- `real` -- lemma L's own subsequent real simplewiki encounters, in corpus order, via
  `context_vector_masked` verbatim (the live function, not a re-implementation). THE OPERATIVE ARM.
- `scram_order` -- the identical real encounters, order shuffled. **CONTROL.**
- `scram_content` -- context vectors sampled from OTHER lemmas. **CONTROL.**

## Fit protocol, pre-declared

Response variable `y = log SNR` for both models, so the comparison is like-for-like:
- POWER LAW: `y = a + b*log t` (2 params)
- EXPONENTIAL: `y = c + e*t` (2 params)

Same response, same n, same parameter count -> **AIC is directly comparable**. Pre-declared
statistic: `dAIC = AIC_exponential - AIC_power`. **Power law wins iff dAIC > 10; exponential wins
iff dAIC < -10; |dAIC| <= 10 is AMBIGUOUS** and is reported as such, not resolved.

- FIT WINDOW: `t >= 4` (the `sqrt(2/(pi t))` asymptotic is not valid at t=1,2), up to `T_MAX`.
  The full-window fit is reported alongside as a pre-declared sensitivity.
- t-grid: ~24 log-spaced integers, `sorted(set(...))`.
- Slope CI: cluster bootstrap over TRACKED LEMMAS, 2000 resamples, percentile 2.5/97.5.

## PASS / FAIL bands (pre-declared, per the brief)

- **CONFIRMS** (the drill's hypothesis stands): the graded arm fits a power law (`dAIC > 10`) AND
  the binarised arm does not (`dAIC <= 10`, or `dAIC < -10`), on the SAME stream. Report both
  fitted slopes with CIs.
- **REFUTES** (`sign()` is not the cause): both arms fit power law, with slope CIs overlapping and
  `|slope_graded - slope_binarised| < 0.10`. Equally: both arms fit exponential.
- **INCONCLUSIVE** is a legitimate outcome and will be reported as such rather than forced.

**Additional pre-declared band on the CONTROL, and it is a FAIL band:** if `scram_order` reproduces
the `real` curve shape (`|slope_real - slope_scram_order| < 0.05`), the curve is **not measuring
consolidation** -- it is measuring interference/dilution in an order-invariant accumulator, and must
be reported that way. I expect this to fire: `+=` is commutative, so for the GRADED arm the
accumulator is order-invariant BY CONSTRUCTION and the two curves should be numerically identical.
That is a finding about the substrate (it has no temporal structure to consolidate), not a defect of
the control.

**No band is a tuning target.** A negative closes the hypothesis cheaply, which is the point.

## Smoke gate (must pass BEFORE the full run) -- `--self-test`

The discriminator MUST FIRE at smoke, or the cell is vacuous:
1. `synth`+`graded` recovers slope in `[-0.53, -0.47]`.
2. `synth`+`binarised` recovers slope in `[-0.56, -0.44]`.
3. binarised/graded SNR LEVEL ratio at the largest common t is `0.798 +- 0.10` (the derived
   `sqrt(2/pi)`) -- this pins the PREFACTOR cost, which is the thing the sign() actually costs.

   **AMENDMENT, disclosed 2026-08-14 before any full run, after gate 3 FAILED as first written.**
   The failure was the ESTIMATOR, not the derivation. As first specified the gate used a MEDIAN
   over n=24 synthetic lemmas; the per-lemma SNR has s.d. ~1.0 by construction (signal is a sum of
   `d` terms each of unit variance), so that estimator's sampling s.d. is ~0.2 on a quantity of
   ~0.6 and it **cannot resolve a +-0.10 band at all**. Checked directly at n=400
   (`scratch/_fk_power.py`): measured means track the closed forms to 1-3 s.e. at t=16/64/512, and
   the ratio comes out 0.748/0.786/0.758 against derived 0.810/0.801/0.798. **The derivation is
   confirmed; the gate was underpowered.** Re-specified as an **n=400 MEAN at t=64** compared to
   the EXACT finite-t closed forms (`sqrt(d/(t+1))` graded; `d*C(t,t/2)/2^t/sqrt(d)` binarised,
   which tends to `sqrt(2/(pi t))`), asserting each arm within **8%** of its own closed form and
   the ratio within **0.08** of the derived ratio. This is TIGHTER than the original band, not
   looser, and no tolerance was set by looking at an outcome. Recorded here rather than silently
   edited, per the disclosure rule.
4. **A PLANTED EXPONENTIAL is correctly identified**: synthetic `SNR = exp(-t/tau)` data must return
   `dAIC < -10`. Without this the "power law wins" verdict is unfalsifiable.
5. Real context vectors are not all-zero and not all-identical (the `content_words`
   digit-dropping trap: a witness once scored 1.000 on all-zero vectors).

## Engineering

`OMP_NUM_THREADS`/`OPENBLAS_NUM_THREADS` pinned at the top of the file before `import numpy`.
Fresh output dirs (`data/exp_forgetting_kernel_signreadout_v1{,_smoke}/`), separate for smoke.
`metrics.json` written once via tmp + `os.replace`. `sorted(set())` everywhere, never `list(set())`.
Per-unit checkpoint via `tools/exp_checkpoint.py`. `hdlab/` is NOT modified by this cell.

## Timeout

Self-test ~20 s. Smoke (8 lemmas, T_MAX=64, 40k sentences scanned) ~90 s per readout arm.
Full (60 lemmas, T_MAX=1024, 400k sentences scanned): corpus scan ~200 s + 61.5k
`context_vector_masked` calls at ~1790/s ~= 35 s + fits ~30 s -> ~5 min per readout arm, ~10 min
total. `--timeout 2400` per arm (4x headroom).
