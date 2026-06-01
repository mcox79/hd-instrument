# Strategy -> Research: Cap 2 self-monitoring confidence rehab request

**Date filed**: 2026-05-23 ~13:14 EDT (Strategy cycle 180, cap_map v160)
**Trigger**: `wave14_cap2_confidence_margin_probe_v1` FULL verdict `CAP2_MARGIN_KILL`
("HARD FAIL: corr(margin, correct) < 0.2 in ALL strata. Substrate carries no
margin-based confidence signal; Cap 2 structurally closed."). Hard-fail
threshold defined in pre-reg crossed.
**Pre-reg**: `preregs/2026-05-23_wave14_cap2_confidence_margin_probe_v1.md`
**Protocol**: PROT-004/006 closure rehab discipline + [[feedback-negative-results-2x-research]]
**Cap_map row**: Cap 2 "Self-monitoring confidence" → ❌ PROVISIONAL at v160

---

## Why this is a TRUE structural closure

Two independent metric framings of the same capability axis have failed at FULL:

1. **v153** `wave14_critical_slowing_down_self_monitor_v1` FULL =
   `CRITICAL_NO_CORRELATION`. The original Cap 2 framing tested VAMP iteration
   count tau as a confidence proxy. Refuted: tau is invariant across correct
   vs incorrect retrievals at substrate (argmax dynamics converge fast in 1-3
   iterations regardless of outcome).
2. **v160 (today)** `wave14_cap2_confidence_margin_probe_v1` FULL =
   `CAP2_MARGIN_KILL`. The Sagawa-Ueda-precedent re-axiomatization (cosine
   margin top-1 minus top-2 as confidence proxy) was the natural second
   attempt. `corr(margin, correct) < 0.2` in ALL four noise strata (p in
   {0.0, 0.05, 0.10, 0.20}). Hard-fail threshold from pre-reg crossed.

Per [[feedback-no-smoke]]: this is a closure, NOT a narrowing. Both candidate
substrate-intrinsic readouts for confidence (iteration count + cosine margin)
fail. Per [[feedback-dont-overextend-theorems]]: the closure scope is "no
margin/tau-based intrinsic confidence signal at substrate"; it does NOT close
the broader axis of "substrate carries SOME confidence-correlated signal" if
the signal lives elsewhere (endpoint-id, posterior variance, dynamic
susceptibility, hysteresis, or a downstream calibrator).

Per [[feedback-rehabilitation-after-rejection]]: 5 axis-combination rescue
sketches below. Strategy DRAFT only -- Research's 2x drill is the load-bearing
ranking.

---

## 5 axis-combination rescue sketches (DRAFT, unvetted)

### Rescue 1 -- Endpoint-ID as the confidence proxy (axis: proxy substitution)

**Premise**. v153 + v149 substrate has a 28-element endpoint partition under
W^L iteration (substrate-novel). Margin and tau both measure local-step
information; endpoint-id measures global-trajectory information. Map each
retrieval to its endpoint; correctness then partitions by endpoint, and
"confidence" can be defined as max-entropy-departure of the endpoint
distribution per query.

**Operational form**.
- For each query: run W^L to convergence (L=50 hops; cycle 137 protocol).
- Tag the endpoint cluster (1-of-28 via existing endpoint-detection).
- Compute `p(correct | endpoint_k)` empirically across calibration set.
- Per-query confidence = `p(correct | observed_endpoint)`. Wrap with conformal
  prediction for distribution-free guarantees.

**Multi-probe success criteria**.
- ROC AUC (correct vs incorrect | endpoint) >= 0.65 at 200 trials per stratum,
  3 seeds, p in {0.0, 0.05, 0.10, 0.20}.
- Calibration ECE <= 0.10 after conformal wrap.
- Improvement over margin-baseline (today's KILL) >= 0.15 AUC.

**Cost**. ~150 LOC; existing endpoint-detection code reusable from cycle 137
retraction-phase scripts; runtime ~10 min CPU at N=8192.

**Why it might work**. The 28-element partition is a SUBSTRATE-NOVEL structural
finding that survives FULL (cycle 152 PQ_DISCRETE_OTHER 15 peaks; cycle 150
ORDER_PARAM_SUB_REGION_STABLE multi-component q_overlap STABLE). Margin and tau
discard this structural information by collapsing dynamics to scalar local
measurements. Endpoint-id is the natural information-preserving alternative.

**Why it might fail**. If endpoints are themselves correlated with the underlying
data (e.g. one endpoint per concept cluster) then `p(correct | endpoint)` may be
trivially predictable from the query alone, providing no substrate-novel signal
over a downstream classifier. Test: ablate substrate (replace with random
classifier) and check if endpoint-id confidence STILL beats margin -- if yes,
substrate is not adding information.

---

### Rescue 2 -- VAMP-on-chain posterior variance certificate (axis: native uncertainty mechanism)

**Premise**. Cap 5 / Bet Z.5 VAMP-on-chain machinery natively produces posterior
variance per atom (it IS a Bayesian posterior reconstruction). The original Cap 2
framing chose VAMP iteration count tau as proxy; the natural choice is the
posterior variance directly. Substrate gives this for free at the readout step;
no extra computation.

**Operational form**.
- Replace argmax readout with VAMP-on-chain readout (cycle 162 HEADTOHEAD_EQUIVALENT
  confirms both are equivalent for accuracy at smoke; the two readouts produce
  DIFFERENT side-information).
- Extract per-query posterior variance sigma^2(x | y) from VAMP iterates at convergence.
- Confidence proxy = `-log sigma^2`. High variance = low confidence.

**Multi-probe success criteria**.
- `corr(-log sigma^2, correct) >= 0.40` in at least 2/4 noise strata at FULL.
- Variance distribution well-separated for correct vs incorrect (Cohen's d >= 0.5).
- ECE <= 0.10 after conformal wrap.

**Cost**. ~80 LOC; VAMP-on-chain code already validated cycle 162 HEADTOHEAD_EQUIVALENT;
runtime ~15 min CPU at N=8192.

**Why it might work**. VAMP's posterior variance is the textbook Bayesian
uncertainty quantity, derived from substrate-internal noise + posterior geometry.
This is the OPPOSITE of margin (a deterministic readout summary): it carries
Bayesian uncertainty information natively. Cap 5 (Gap B Online W + Robbins-Monro+SNAP)
already validated VAMP-on-chain produces calibrated uncertainty in the streaming
inference setting (cycle 173).

**Why it might fail**. VAMP posterior variance is calibrated for GAUSSIAN noise;
substrate's bit-flip noise is non-Gaussian. The variance may be miscalibrated
(over- or under-confident) and require an empirical re-scaling factor that
defeats the "native" appeal. Also: if argmax and VAMP-on-chain are TRULY
equivalent (cycle 162 HEADTOHEAD_EQUIVALENT at smoke), the posterior variance may
collapse to a degenerate quantity at convergence, carrying no extra information.

---

### Rescue 3 -- chi_4 dynamic susceptibility per-query (axis: observability suite)

**Premise**. v150 KOVACS_RS_INDEPENDENT + CHI4_RS_CONSISTENT (Observability V2,
6th cross-family RS-cert anchor) established chi_4 dynamic overlap variance as
a substrate-internal observable. Chi_4 high = unstable retrieval = low
confidence. Per Berthier 2010, chi_4 directly measures dynamical heterogeneity
in glassy systems -- a textbook uncertainty quantity.

**Operational form**.
- During retrieval, instrument the W^L iteration to record per-hop overlap with
  a small reference batch.
- Compute chi_4(t) = N * var_batch[q(t)] over the trajectory.
- Confidence proxy = `-peak(chi_4(t))` over the retrieval window.

**Multi-probe success criteria**.
- `corr(-peak_chi_4, correct) >= 0.40` in at least 2/4 noise strata.
- Per-query chi_4 well-separated for correct vs incorrect (Cohen's d >= 0.5).
- chi_4 cost < 20% wall-time overhead vs unobservable retrieval.

**Cost**. ~100 LOC; chi_4 measurement primitive already validated cycle 145
CHI4_RS_CONSISTENT; runtime ~20 min CPU at N=8192 with 5 reference batch.

**Why it might work**. Chi_4 is the SUBSTRATE-PHYSICS-NATIVE measure of
dynamical heterogeneity. v150 confirms substrate exhibits chi_4 RS-cert
structure at FULL; that means there IS heterogeneity per query (some queries
are harder than others), and chi_4 directly measures it. This is the only
rescue grounded in a substrate-physics anchor that ALREADY HOLDS at FULL.

**Why it might fail**. Chi_4 measures BATCH variance; per-query confidence needs
PER-QUERY information. If chi_4 averaged over a query batch is informative but
per-query chi_4 is too noisy (small-batch variance), the signal washes out.

---

### Rescue 4 -- Kovacs-style memory-effect probe per query (axis: hysteresis observable)

**Premise**. v150 KOVACS_RS_INDEPENDENT confirms substrate carries Kovacs
hysteresis memory effects (6th cross-family RS-cert anchor). Inject a small
temperature pulse during retrieval, observe relaxation hump amplitude.
Metastable retrievals (low-confidence basins) show LARGE recovery humps; stable
retrievals (high-confidence basins) show SMALL humps. Direct substrate-native
introspection.

**Operational form**.
- For each query: run baseline retrieval; perturb (small temperature kick or
  noise pulse) at hop L/2; observe relaxation hump amplitude A_Kovacs.
- Confidence proxy = `-A_Kovacs`. Large hump = unstable basin = low confidence.

**Multi-probe success criteria**.
- `corr(-A_Kovacs, correct) >= 0.40` in at least 2/4 noise strata.
- Cohen's d for correct-vs-incorrect Kovacs amplitude distributions >= 0.5.
- Cost <= 2x baseline retrieval wall-time.

**Cost**. ~120 LOC; Kovacs probe scripts validated cycle 145 + cycle 162;
runtime ~25 min CPU at N=8192 (2x baseline retrieval).

**Why it might work**. Kovacs memory effects DIRECTLY probe basin
stability -- the substrate-physics quantity that "confidence" was always trying
to capture. v150 RS-cert anchor proves the effect is detectable in the substrate.

**Why it might fail**. Kovacs amplitude is a global trajectory quantity; per-
query estimates may need many repetitions per query (expensive). Also: the
v153 + v149 28-element endpoint partition may align Kovacs amplitudes with
endpoint-id (Rescue 1), giving no independent information beyond endpoint
membership.

---

### Rescue 5 -- Re-axiomatize Cap 2 as a downstream conformal layer (axis: re-axiomatization to downstream calibrator)

**Premise**. Per v158 Cap 1 PRECEDENT (Sagawa-Ueda widened Cap 1 from clean-only
to a tiered SLA), the right move when an intrinsic substrate signal fails is to
ask whether a DOWNSTREAM calibration layer (not substrate-intrinsic) delivers
the customer-facing capability. Gap C ✅ (cycle 173 v153 CONFORMAL_COVERED at
FULL) already delivers conformal calibrated confidence as a substrate-product
capability. Cap 2 may be SUBSUMED by Gap C -- not a separate capability axis.

**Operational form**. Customer-facing "self-monitoring confidence" comes from:
- Gap C conformal prediction wrapper: empirical coverage guarantee (cycle 173).
- NOT from substrate-intrinsic margin/tau/endpoint signals.
- Cap 2 retires as a standalone capability and folds into Gap C's certificate.

**Multi-probe success criteria** (more a portfolio-restructure than experiment).
- Audit Gap C cap_map row; confirm scope covers what Cap 2 originally promised
  (per-query confidence + abstain decision + calibration ECE <= 0.10 + coverage).
- If yes: Cap 2 closure is FINAL (structural; not just a metric mismatch),
  product story unchanged because Gap C already covers it.
- If no: gap surfaces and Rescues 1-4 are the candidate fills.

**Cost**. ~2 hours strategy + product analysis; no new experiment.

**Why it might work**. The v158 Cap 1 precedent showed that re-axiomatizing the
metric (Sagawa-Ueda over Crooks-FT) widens the envelope without changing the
substrate. The analogous move here is to re-locate the capability claim from
"intrinsic substrate signal" to "downstream conformal wrapper around any
substrate readout". The customer doesn't care WHERE the confidence comes from,
as long as it's principled and works. Gap C already delivers.

**Why it might fail**. If Cap 2's original product-spec required intrinsic
substrate-side confidence (e.g. for a hardware-side abstain decision before
readout), Gap C's downstream wrapper doesn't cover the use case. Audit the
original Cap 2 product spec to verify.

---

## Sequencing recommendation (which Research should pick up first)

Ranked by leverage / cost / decisiveness:

1. **Rescue 5 (re-axiomatization)** -- ZERO experimental cost; cleanest portfolio
   move if Gap C already covers the use case. Strategy preference: DO THIS FIRST.
   If Cap 2 folds into Gap C, the closure becomes structural (FINAL ❌, not
   PROVISIONAL) and no experiments needed.

2. **Rescue 1 (endpoint-id confidence)** -- HIGHEST EXPECTED LEVERAGE among
   experimental rescues. Substrate-novel 28-element partition is the structural
   finding most likely to carry per-query information that margin/tau discard.
   Cheap (~10 min CPU); decisive.

3. **Rescue 2 (VAMP posterior variance)** -- TEXTBOOK Bayesian uncertainty
   quantity; if Cap 5 VAMP machinery doesn't carry it, that's surprising and
   informative either way. Cheap (~15 min CPU).

4. **Rescue 3 (chi_4 dynamic susceptibility)** -- SUBSTRATE-PHYSICS-NATIVE;
   v150 RS-cert anchor already holds. Slightly more involved (~20 min CPU,
   batch-instrumentation needed) but grounded in an existing FULL-validated
   observable.

5. **Rescue 4 (Kovacs hysteresis)** -- MOST EXPENSIVE per query (~25 min CPU,
   2x baseline); reserve for last if Rescues 1-3 all fail.

---

## Research deliverable requested

Per [[feedback-negative-results-2x-research]] this verdict crossed the hard-fail
threshold in the pre-reg: TRUE measurement-based refutation, qualifies for 2x
Research drill. Per [[feedback-lit-scan-calibration-penalty]] expect agent P
estimates to be deflated 0.15-0.25 from face value; cap novel-synthesis P at
0.50; require explicit hard-fail thresholds in each rescue's multi-probe
success criteria.

Research deliverable:
1. Vetted ranking of the 5 rescue sketches (above) with calibration-deflated P
   estimates and explicit hard-fail thresholds.
2. Lit-scan on confidence signals in dense associative memory + spin-glass
   models (chi_4 + Kovacs + posterior-variance literature). Generic-math
   framing per [[feedback-query-privacy-decomposition]]: "confidence calibration
   in iterated argmax / dense associative memory / SK-class spin glass /
   replicator dynamics".
3. One-cycle next-experiment prescription: which rescue to pick up first,
   what the falsifiable prediction is, what the hard-fail threshold is, and
   what the minimal experimental scaffold looks like.

If Research finds that Rescue 5 (re-axiomatize as Gap C subsumption) is
correct, Cap 2 closure becomes FINAL (bare ❌, not PROVISIONAL) and the
substrate-product portfolio drops from 12 to 11 demonstrated capabilities
permanently -- not a regression, just an honest accounting (Cap 2 was never a
separate axis from Gap C).

If Research recommends Rescue 1-4 as live experimental candidates, Strategy
will route the top pick to Exp Dev on the next cycle.

---

## Honest framing

Per [[feedback-no-smoke]]: Cap 2 is CLOSED, not "narrowed". Two independent
metric framings (tau v153 + margin v160) both crossed hard-fail. The substrate
does not carry margin/tau-based intrinsic confidence signal. PROVISIONAL tag
applied per PROT-004 until Research's 2x drill + first rescue experiment land.

Per [[feedback-no-papers-product-only]]: framed as substrate-product capability
closure with portfolio impact (12 -> 11 demonstrated caps), not as a paper-
worthy result.

Per [[feedback-value-creation-not-competition]]: closure honesty is the value
here; the rescue sketches are about whether the substrate has confidence
information ELSEWHERE, not about positioning vs competitors.

Per [[feedback-dont-overextend-theorems]]: closure scope is "margin/tau
substrate-intrinsic confidence proxy"; 4 of 5 rescues open new axes
(endpoint-id, VAMP variance, chi_4, Kovacs); Rescue 5 reframes as subsumption.
Do NOT extend the closure to "substrate has no confidence information at all".

---

## References

- Cap 2 original prereg (v153): `experiments/exp_wave14_critical_slowing_down_self_monitor_v1.py`
- Cap 2 margin re-probe prereg (v160): `preregs/2026-05-23_wave14_cap2_confidence_margin_probe_v1.md`
- v160 closure narrative: `notes/substrate_capability_map_history.md` v160 block
- v153 Cap 2 REFUTED row: `notes/substrate_capability_map.md` line 11929
- Gap C ✅ (conformal calibrated confidence): v153 cap_map row + cycle 173 narrative
- v158 Cap 1 Sagawa-Ueda PRECEDENT: cap_map cycle 178 v158 narrative
- Memory anchors: [[feedback-rehabilitation-after-rejection]] [[feedback-negative-results-2x-research]]
  [[feedback-dont-overextend-theorems]] [[feedback-no-smoke]] [[feedback-no-papers-product-only]]
  [[feedback-value-creation-not-competition]] [[feedback-query-privacy-decomposition]]
  [[feedback-lit-scan-calibration-penalty]]

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
