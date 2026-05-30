# Research drill: tau_pred re-derivation (commit 947b22e / v285)

Date: 2026-05-30
Trigger: v285 LABEL-VS-HONEST catch #144 -- adaptive_threshold_rescue_v2_n4096 reported
as "FIRST INSTRUMENTED CONFIRMATION substrate-physics adaptive-threshold prediction
sub-component DEGRADED" with 6/9 cells off by 1.8x-20x in tau-space. User-dispatched
~30min theory drill: can the prediction-component be re-derived?

Author: research sub-agent (Opus escalation; substrate-physics depth drill)
Note path: notes/research_tau_pred_rederivation_v1_2026-05-30.md

---

## HEADLINE

The tau_pred formula `tau_pred(M_frac, beta) = 1/sqrt(M_frac * beta)` is **labelled
heuristic in the experimental script itself** (line 109: "heuristic from cap_map") and
has **no substrate-physics derivation** to re-derive. More importantly, **the v285
empirical data does not measure an empirical tau optimum at all** -- the entire reported
"miscalibration pattern" is the formula's own structure projected against `tau_emp=0.05`,
which is the smallest tau in the sweep selected by argmax-tiebreak when the score
function returns either a constant 0.0 (3 cells) or a constant 1.0 (6 cells). The
v285 anchor is a **second-instance instrumentation failure of the same v283 class**,
not a framework-prediction degradation.

**Classification: (B) FRAMEWORK DEGRADATION READING IS WRONG.** The closest correct
classification is **(A') no original derivation existed to complete + (C') instrument
must be replaced before any reliability claim about a tau-prediction sub-component
can be made**.

**Recommended action: REVERT the v285 sub-component-degradation annotation; re-classify
as third-occurrence-of-instrumentation-failure (v283 best_score=0 / v284 ATC v1
same / v285 v2 saturated best_score=1 with tiebreak fallback) and ship `adaptive_threshold_rescue_v3`
with a non-saturating score function + extended tau sweep BEFORE any tau_pred theory
work.**

---

## 1. Provenance audit -- where did tau_pred come from?

### 1.1 Direct script inspection

`experiments/exp_adaptive_threshold_rescue_v2_n4096.py` line 107-109:

```python
def predicted_threshold(M_frac: float, beta: float) -> float:
    """tau_pred = sqrt(1 / M_frac) / sqrt(beta). Higher M or higher beta lowers tau."""
    return float((1.0 / max(0.01, M_frac)) ** 0.5 / max(0.01, beta) ** 0.5)
```

Equivalently: `tau_pred = 1 / sqrt(M_frac * beta)`.

The docstring at line 25-26 (`FORMULA SELF-TESTS`) calls this:

> predicted threshold: `tau_pred(M_frac, beta) = sqrt(1/M_frac) / beta**0.5`
> **(heuristic from cap_map -- inverse sqrt of (M_frac * beta))**

The author's own word is **heuristic**. There is no derivation cited; no anchor; no
substrate-physics scaffold. The "from cap_map" attribution does not resolve to any
explicit theoretical block in `notes/substrate_capability_map.md` (no entry of the
form "tau_pred = ..." or "adaptive-threshold derivation" appears prior to v283).

### 1.2 Provenance trace through cap_map history

Grep of `notes/substrate_capability_map.md` and `notes/substrate_capability_map_history.md`
for `tau_pred` / `adaptive_threshold` / `adaptive-threshold`:

- First mention is at v283 (commit 75c565d) **introducing the v1 experiment**
  (`adaptive_threshold_characterization_v1_n4096`).
- Prior cap_map versions (v0..v282) have no derivation, no scaling argument, no
  prior reference for any threshold-prediction formula of any shape.
- The v283 v1 was caught as LABEL-VS-HONEST #142 (test-instrument failure;
  best_score=0 in every cell). Framework-prediction sub-component reliability was
  marked UNCHANGED.
- v285 v2 (commit 947b22e) re-shipped with a "fixed" score function and was
  interpreted as the "first instrumented confirmation" of sub-component degradation.

**Verdict**: the formula is a 1-line guess. There is no theoretical body to re-derive
from. The v285 framing "re-derive the tau_pred scalar coefficient from substrate-physics
scaling argument" presupposes the formula has a derivation. **It does not.**

### 1.3 Why the formula has the wrong functional form for the substrate

The substrate's threshold-acceptance scoring is:

- For a probe key k: `out = k @ W.T`, then `sims = codebook @ out.T / N`, then
  `conf = softmax(beta * sims, dim=0)`; `max_conf = conf.max()`, gate `pass` iff
  `max_conf >= tau`.

The optimum operational tau lies between the OOS max-conf distribution and the stored
max-conf distribution. The substrate-physics-correct derivation requires:

1. **Codebook size C** (Kerdock 4-coset for this anchor: C = 4N = 16384). The
   no-information OOS max-conf floor is approximately `1/C + extreme-value(beta * sigma_oos)`
   where `sigma_oos = 1/sqrt(N)`. The original formula contains no C dependence.
2. **Cleanup signal strength** under W (saturates to ~1 above the beta_c=10
   transition; degrades below it). The original formula has no saturation term.
3. **Soft-max sharpening** under beta: stored max-conf approaches 1 as
   `beta * (1 - sigma_cross_max)` grows past O(log C); OOS max-conf approaches 1
   on the same scale. The relevant geometry is logarithmic in C and linear in beta,
   not inverse-sqrt in beta.

**Predicted form (substrate-physics scaling, sketch):**

`tau_opt ~ geometric_mean(stored_max_conf, oos_max_conf)`

where:

- `stored_max_conf ~ 1 / (1 + (C-1) * exp(-beta * (1 - sigma_cross)))`
- `oos_max_conf ~ exp(beta * sqrt(2 ln C / N)) / (C-1 + exp(beta * sqrt(2 ln C / N)))`
- `sigma_cross = sqrt(M / N)` (cross-talk under linear superposition)

This is monotone in `beta` (sharpening) and weakly dependent on M (through
`sigma_cross`). It is **not** of the form `1/sqrt(M*beta)`. The unit analysis alone
rules out the heuristic: confidence is a probability in [0, 1] but `1/sqrt(0.25*4)=1.0`
predicts the boundary at the upper saturation point, and `1/sqrt(4*4)=0.25` predicts
the boundary near the lower noise floor. The heuristic doesn't even respect the [0,1]
range structurally.

---

## 2. Empirical-pattern audit

### 2.1 The cell-level log2_miss values are an algebraic identity

Source: bridge `get_metrics('adaptive_threshold_rescue_v2_n4096')` returned 27 cells
(3 M_frac x 3 beta x 3 seeds), all 9 (M_frac, beta) operating points show identical
log2_miss across seeds.

Inspecting per-cell `tau_emp` values: **tau_emp = 0.05 in EVERY single cell**, where
0.05 is the smallest tau in `TAU_SWEEP_FULL = [0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 0.9]`.

Given `tau_emp = 0.05` and the formula `tau_pred = 1/sqrt(M_frac * beta)`, the
"empirical" log2_miss values are:

```
log2_miss = log2(tau_pred / tau_emp)
         = log2(tau_pred) - log2(0.05)
         = log2(20) - 0.5 log2(M_frac) - 0.5 log2(beta)
         = 4.3219 - 0.5 log2(M_frac) - 0.5 log2(beta)
```

Predicted vs reported (9 cells):

| (M_frac, beta) | predicted log2_miss | reported empirical | match? |
|---|---|---|---|
| (0.25, 4.0)  | 4.3219 | 4.32 | exact |
| (0.25, 10.0) | 3.6610 | 3.66 | exact |
| (0.25, 32.0) | 2.8219 | 2.82 | exact |
| (1.0, 4.0)   | 3.3219 | 3.32 | exact |
| (1.0, 10.0)  | 2.6610 | 2.66 | exact |
| (1.0, 32.0)  | 1.8219 | 1.82 | exact |
| (4.0, 4.0)   | 2.3219 | 2.32 | exact |
| (4.0, 10.0)  | 1.6610 | 1.66 | exact |
| (4.0, 32.0)  | 0.8219 | 0.82 | exact |

**Every reported log2_miss is the formula's own image at tau_emp = 0.05.** The user's
intuition (-2.0 per 4x M_frac, -1.5 per 8x beta) is approximately the formula's
exponents: the actual deltas are -1.0 per 4x M_frac (from -0.5 * log2(4)) and
-1.5 per 8x beta (from -0.5 * log2(8)). The user-quoted -2.0 is roughly double the
true M_frac exponent; the beta exponent matches.

### 2.2 Why tau_emp = 0.05 in every cell

Three regimes:

**Regime I (beta = 4, all M_frac): "degenerate"** (3 cells: (0.25,4), (1.0,4), (4.0,4))
- `best_score = 0.0`, `score_var = 0.0` across all 3 seeds.
- At beta=4 the softmax is too flat: OOS max-conf is high (relative to threshold),
  TPR - 5*FPR is `<= 0` for every tau in sweep. The argmax over a constant-zero array
  picks tau=0.05 by index tiebreak.

**Regime II (beta = 32, all M_frac): "saturated"** (3 cells: (0.25,32), (1.0,32), (4.0,32))
- `best_score = 1.0`, `score_var = 0.0`. The score is constant 1.0 across the entire
  sweep.
- At beta=32 the softmax is so sharp that stored max-conf is essentially 1.0 and OOS
  max-conf is below 0.05 for ALL probes. Any tau in [0.05, 0.9] gives TPR=1, FPR=0,
  score=1.0. tau=0.05 wins by tiebreak.

**Regime III (beta = 10, all M_frac): "partially-discriminating"** (3 cells)
- `best_score = 1.0`, `score_var ~ 0.44`. The score reaches 1.0 at some lower tau
  (probably tau=0.05) but drops for high tau (TPR decreases when tau approaches stored
  max-conf).
- The tiebreak still selects tau=0.05 as the lowest tau where score = 1.0.

In NONE of the 9 cells did the instrument detect an empirical tau optimum in the
operational interior `(oos_max_conf, stored_max_conf)`. The "empirical optimum" is
always at the bottom edge of the sweep grid -- which is a fenced-in instrument
artifact.

### 2.3 The pattern is the formula. There is no orthogonal signal.

Once you set `tau_emp = 0.05` (constant), the reported log2_miss is uniquely determined
by the formula structure -- not by any property of the substrate. The cell-to-cell
"miscalibration pattern" is `4.32 - 0.5 log2(M_frac) - 0.5 log2(beta)`, which is exactly
`-log2(tau_pred(M_frac, beta)) - log2(0.05) = -log2(tau_pred * 0.05)`. There is zero
substrate information in this surface beyond what the formula encodes about itself.

---

## 3. Candidate corrections evaluated

### 3.1 Candidate A -- "scale tau_pred down by 20x"

Form: `tau_pred_A = (1 / sqrt(M_frac * beta)) / 20`

Result: log2_miss collapses to `log2(20) - log2(20) - 0.5 log2(M_frac) - 0.5 log2(beta)
- 0 = -0.5 log2(M_frac) - 0.5 log2(beta)`. Still cell-dependent. At (4.0, 32) we'd
have log2_miss = -3.5 (way overshooting in the other direction).

Match: **0/9 cells within +/-20%** (since tau_emp is itself stuck at 0.05; no rescue
of the metric problem).

### 3.2 Candidate B -- "replace with 1/C floor"

Form: `tau_pred_B = max(1/C, 0.05) = 0.05` for N=4096, C=16384.

Result: log2_miss = 0 in every cell. **9/9 within +/-20%.** This "passes" the gate, but
only because it trivially equals the floor tau_emp = 0.05 -- which is itself an
instrument artifact, not an optimum. **Spurious match.**

### 3.3 Candidate C -- "geometric mean of stored and OOS max-conf"

Form: `tau_pred_C = sqrt(stored_max_conf * oos_max_conf)` with stored and OOS computed
from beta_c=10 model + Kerdock cross-talk `sigma_cross = sqrt(M/N)`.

Result (rough): at (M_frac=0.25, beta=32): tau_pred_C ~ 0.024. At (M_frac=4.0, beta=32):
tau_pred_C decays as cleanup fails near saturation. At beta=4: stored_max_conf falls
below 0.001 so tau_pred_C is below the sweep floor.

Match: **cannot evaluate against the empirical** because there IS no empirical optimum
in the data -- the data only tells us "tau in [0.05, 0.9] works at beta>=10". A
"theory" prediction of 0.024 would log2_miss against 0.05 by `|log2(0.05/0.024)| = 1.06`
> 0.263, still failing the +/-20% gate. But this is the gate's fault, not the theory's.

### 3.4 Conclusion on candidate corrections

**No candidate correction can be validated against the v285 data**, because the
empirical "optimum" was never measured. The v285 anchor is a fenced-in
no-information measurement.

---

## 4. Cross-thread synthesis

### 4.1 Three sequential instrumentation failures, not three different signals

- **v283 ATC v1** (LABEL-VS-HONEST #142): `best_score = 0` everywhere; score function
  broken. Flagged as test-instrument failure.
- **v284 ATC v1 (re-run)**: same pattern; same test-instrument over-claim.
- **v285 v2** (LABEL-VS-HONEST #144): score function "fixed" but new failure mode --
  score saturates to 1.0 across the sweep at beta >= 10, returns 0 at beta = 4. tau_emp
  pinned to sweep floor by tiebreak. Misread as "first instrumented framework-prediction
  sub-component degradation."

**All three are the same class of failure**: the instrument cannot bracket a unique
empirical optimum. v285's "fix" replaced regime I (`score = 0`) with a mixed regime
(I + II + III) but did not produce a non-degenerate maximum in any cell.

### 4.2 Relation to beta_c = 10 invariance (v278 + v280 + v281)

The beta_c = 10 framework prediction IS confirmed by this anchor in the soft sense:
the score function jumps from constant-0 (beta=4) to non-trivial at beta=10 and
saturates at beta=32. The transition at beta_c = 10 is a substrate-physics signature
that the v285 anchor INCIDENTALLY corroborates. This is consistent with the v283 cap_map
note: "beta_c=10 character is METRIC-DEPENDENT (retention at M<M_c saturates and
cannot detect; confidence-sharpness + KF-firing metrics DO detect)" -- v285 v2's
score is exactly the confidence-sharpness regime, and it correctly identifies the
beta_c=10 transition.

### 4.3 Relation to SKAH-M class (v228 + v229)

SKAH-M (saddle-hierarchy-augmented Hopfield-modern) class predicts:
- Stored max-conf -> 1 fast above beta_c (saddle-collapse to attractor)
- OOS max-conf -> 1/C asymptotically (uniform on codebook bulk)
- Operational tau in (1/C, 1 - eps), with weak dependence on M as long as M < M_c

The v285 data is consistent with this: 6 of 9 cells have stored_max_conf in the
saturated regime (best_score = 1 at tau = 0.05 means stored max-conf >> 0.05 AND
OOS max-conf << 0.05). The "optimum tau" in the SKAH-M frame is **not a sharp peak
function of M_frac and beta** -- it's a wide plateau over (1/C, 1 - eps). The
heuristic formula `1/sqrt(M*beta)` assumed a sharp peak; SKAH-M says it's a plateau.
The "framework prediction" component being tested doesn't correspond to any actual
SKAH-M framework prediction.

### 4.4 The v283 cap_map note already said the right thing

v283 (commit 75c565d) cap_map note for ATC v1:

> "Framework-prediction-of-threshold sub-component remains untested by ATC v1; needs
> corrected metric design before reliability can be measured"

This is the correct status. v285 v2 attempted the corrected metric but produced a
new instrument failure (saturation regime I + II + III problem). The status should
remain "framework-prediction-of-threshold sub-component remains untested" -- NOT
"first instrumented confirmation degraded."

---

## 5. Substrate-product implications

### 5.1 The product DOES need an operational tau

The deletion-certificate and KF-1 hallucination-detection product features ship with
a threshold. Currently those features use a hand-tuned per-anchor tau (typical: 0.5)
that empirically works at beta = 10 production setting. No theoretical-tau-prediction
component is load-bearing in current product specs.

### 5.2 Risk: false claim of "framework-prediction component degradation"

The v285 strategy decision filed a "framework-prediction sub-component degradation"
annotation on the substrate-physics framework row and opened a new backlog row
"framework-prediction-degradation tracking" at 🔬 P=0.50. **This annotation rests
on the misread that empirical data refuted a derived prediction.** It refutes
nothing -- the empirical "optimum" is an instrument artifact.

External-facing risk: if this annotation propagates into product positioning ("our
framework has known degraded sub-components"), it would understate the actual
framework reliability without any empirical justification.

### 5.3 Recommended cap_map action

**REVERT** the v285 "adaptive-threshold sub-component DEGRADED" annotation on the
substrate-physics framework row.

**REPLACE** with the v283-style status: "adaptive-threshold operational-tau prediction
sub-component remains untested; v283 v1 + v285 v2 both failed at instrument level
(constant-zero score in v1; saturated-score-with-tiebreak-fallback in v2). Sub-component
fix path: requires a non-saturating discriminant + extended tau sweep that brackets
the operational interior `(oos_max_conf, stored_max_conf)`."

**KEEP** the substrate-physics framework reliability ranges UNCHANGED (which v285
strategy did, correctly, at the aggregate level). The annotation should track
"untested" not "degraded."

### 5.4 Adaptive-threshold capability row positioning

If the cap_map carries an explicit "adaptive-threshold" capability row (per v285
backlog), its status should be 🔬 (untested by instrument; no theoretical derivation
exists; product currently uses hand-tuned constant) NOT 🔴 (degraded). The
0-compute action is the cap_map note correction; the cheap-CPU action is to
design a non-saturating score + extended sweep grid.

---

## 6. Recommended experiment (if any)

**adaptive_threshold_rescue_v3_n4096** (CHEAP CPU, ~10-30 min):

Three fixes in one anchor:

1. **Replace score function** with a non-saturating discriminant:
   `score(tau) = AUROC(max_conf | tau-pass on stored vs OOS, gated by tau)` directly,
   OR `score(tau) = TPR * (1 - FPR)` (multiplicative, range bounded [0, 1] with unique
   maximum). The current `TPR - 5*FPR` saturates to 1 when TPR = 1, FPR = 0 -- which
   is what's killing the sweep.

2. **Extend tau sweep DOWNWARD AND UPWARD**:
   `tau_sweep_v3 = [0.0005, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.95, 0.99]`
   to capture both the OOS-discrimination floor and the stored-saturation ceiling.

3. **Add a non-degenerate selftest**: assert that the score function returns at least
   3 DISTINCT values across the sweep grid in at least 6 of 9 cells (instrument-quality
   gate before the science gate).

Pre-reg gates:
- HP: instrument produces unique argmax in `(0.05, 0.95)` interior in >= 6/9 cells
  AND empirical optima cluster in (1/C, 1 - eps) with `1/C = 0.000061` (Kerdock C=16384).
- HF: instrument again produces tau_emp on the sweep boundary in >= 6/9 cells
  (same v283 / v285 pathology).
- MIDDLE_BAND: mixed.

This anchor does NOT test any theoretical tau_pred formula -- it only tests whether
the instrument can produce a usable empirical optimum at all. **Theory-level tau_pred
re-derivation is BLOCKED on instrument repair**: there is nothing to compare the
theory against until the instrument can measure an optimum.

**Tier hint**: Tier-2 cheap CPU; no Strategy gate movement; orchestrator can ship as
instrument-repair anchor in next refill batch.

**Status if NOT shipped**: cap_map note correction (revert v285 sub-component-degraded
annotation; restore v283 sub-component-untested annotation) is sufficient as a 0-compute
action.

---

## 7. Strategic classification

| Option | Reading | Verdict |
|---|---|---|
| (A) FRAMEWORK COMPLETION | Original tau_pred derivation was incomplete and needs a missing term (capacity, beta, codebook factor). | **Partially correct**: there was no original derivation; the formula was a 1-line heuristic. So "completion" isn't quite right -- the work would be DERIVATION not COMPLETION. |
| (B) FRAMEWORK DEGRADATION | Original tau_pred derivation is structurally wrong; needs a different theoretical scaffold. | **No**: there was nothing to be degraded. The formula was never derived. |
| (C) FIXABLE WITHIN COMPONENT | Candidate corrections from step 3 work. | **Cannot determine**: empirical optimum was never measured. Until v3 instrument repair, no candidate can be evaluated. |
| (D) UNFIXABLE WITHIN COMPONENT | Empirical pattern admits no clean theoretical form; need empirical fitting. | **Cannot determine** for the same reason. |

**Best classification: instrumentation-failure-third-occurrence + framework-prediction-
component-DOES-NOT-EXIST-IN-DERIVED-FORM.** Closest single letter: **(B)** in the sense
that any framework-prediction-component reading of the data is wrong, but for the
opposite reason -- there was no prediction to be wrong about.

---

## 8. HARD-PASS / HARD-FAIL thresholds (pre-registered)

For the v3 instrument-repair anchor:

**HP**: instrument produces unique `argmax_tau score(tau)` strictly interior to the
sweep in >= 6/9 cells; score range > 0.1 in >= 6/9 cells; tau_emp distribution
cluster width < log2(4) = 2.0 across cells. (Instrument is measuring something.)

**HF**: instrument again pins tau_emp to the sweep boundary in >= 6/9 cells (the
v285 pathology returns). Verdict: tau-prediction sub-component is **structurally
unmeasurable** with the current threshold-acceptance scoring architecture; product
keeps hand-tuned constant; close as instrument-class limitation.

**MIDDLE_BAND**: 3-5 of 9 cells with interior optima; instrument partially working.
Diagnose which regime cells lie in (saturation vs degenerate vs partial); ship v4
with regime-specific instrument.

Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: P(v3 instrument
yields interior optima) deflated to **0.35-0.50** -- substrate's saturated softmax
regime at beta = 32 may be fundamentally non-bracketing for ANY tau in [0, 1]; the
beta=4 regime may be irrecoverably degenerate; only beta=10 may yield a true optimum
even with the v3 fix. The novel-synthesis P cap is **0.50** because we're proposing
a metric definition + sweep design (engineering not novel science), but the
substrate's saturation behavior is an UNCHARTED instrument-design regime.

---

## 9. Citations (verified count)

This is a substrate-physics + own-instrumentation drill. External citations: 0 (the
formula has no published source; the substrate-product architecture is internal).

Internal references (verified by read this drill):
1. `experiments/exp_adaptive_threshold_rescue_v2_n4096.py` line 107-109 (formula
   labelled "heuristic")
2. `experiments/_metric_battery.py` line 81-94 (make_substrate; codebook = Kerdock
   4-coset C=4N)
3. `testbed/codebooks.py` line 34-57 (Kerdock builder confirmed)
4. `notes/substrate_capability_map_history.md` v283 entry line 18846 ("framework-
   prediction sub-component reliability UNCHANGED" at ATC v1)
5. `notes/substrate_capability_map_history.md` v283 line 18873 ("Framework-prediction-
   of-threshold sub-component remains untested by ATC v1; needs corrected metric design
   before reliability can be measured") -- this is the correct status, which v285
   re-write incorrectly upgraded to "degraded."
6. `notes/substrate_capability_map_history.md` v285 entry line 19209-19222 (the
   "degradation" annotation under audit here)
7. Bridge `get_metrics('adaptive_threshold_rescue_v2_n4096')` -- 27 cells confirmed
   tau_emp = 0.05 in every cell.

**Verified citation count: 7 internal sources** (no external lit-scan needed -- the
formula has no published origin).

---

## 10. ONE-LINE SUMMARY

The tau_pred formula has no substrate-physics derivation to re-derive (script flags
it as "heuristic"); the v285 "empirical miscalibration pattern" is the formula's own
image at tau_emp = 0.05 (a sweep-boundary tiebreak artifact, not a measured optimum);
classification (B) framework-degradation reading IS WRONG because no prediction
existed to be degraded; recommended action is to **revert the v285 sub-component-
degradation annotation** and ship `adaptive_threshold_rescue_v3` with a non-saturating
score + extended tau sweep before any theory work resumes.

Commit hash referenced: 947b22e (v285 cap_map commit carrying the misread).
