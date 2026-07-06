# RESEARCH — Self-margin frontier synthesis + CG_META candidacy assessment (session capstone)

**Date:** 2026-07-06
**Author:** research (Opus synthesis over this session's 8-drill self-margin arc; zero new trials, pure off-disk
audit + assessment)
**Trigger:** Director capstone ask: assemble the self-margin frontier (confirmed at canonical scale across all
3 cells that were mid-VET at drill time) into one coherent taxonomy, and give an HONEST verdict on whether it
is a testable cross-capability META claim (CG_META candidate) or a descriptive reference only. Explicitly
instructed not to force a cert-claim.

**Verification method:** every tier/number below was re-read directly from `data/substrate_index/meta/
cert_ledger.jsonl` (1480 lines, tail-checked) and the cited cells' own `metrics.json` on disk at drill time
(2026-07-06, post the 17:13:41Z skunkworks landed-VET batch that finalized the last 2 pending tiers). Nothing
here is carried over from memory text uninspected.

---

## (a) HEADLINE

**The self-margin frontier is real, systematic, and now empirically closed at canonical scale on every cell
that was pending at drill start — but it is a DISCRIMINATING 3-FAMILY CLASSIFIER keyed on decode-regime, not
one universal law, and it carries a genuine (if young) prospective track record: this same session it correctly
predicted control-branching's tier (MM, not CG) BEFORE the canonical FULL landed, and it self-corrected a wrong
first guess on generation (order-statistic/PR-transfer, HARD_FAIL) into the right one (collision-count,
CHAIN_GRADE) by reclassifying the decode regime rather than re-tuning the same family. That is real
discriminating behavior, not post-hoc curve-fitting dressed up as a taxonomy. But every capability used to
demonstrate this was also used to BUILD or REFINE the classification rule itself — there is, as of this
note, no case of a capability that was (1) untouched by any self-margin work and (2) classified from its decode
mechanism ALONE, before its fit was computed. That is exactly the in-sample/held-out gap this codebase's own
methodology discipline (held-out test required before crediting a general claim) would flag for any other
capability-level law. **Verdict: CG_META-CANDIDATE, not yet cert-tierable.** File the taxonomy as a reference
now (it already is: `reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`); do not mint a
CG_META atom. A concrete, cheap (mostly zero-new-trial), pre-registered held-out test is sketched below — two
capabilities never touched by self-margin work, one predicted to CONFIRM the order-statistic/CG branch, one
predicted to RESIST all three families — and both predictions are committed to IN THIS NOTE, before any fit
is computed, so the test is genuinely falsifiable rather than retrofittable.**

---

## (b) Taxonomy table (capability x decode-regime x predictor-family x tier x firing-control)

| # | Capability | Cell (atom/path) | Decode regime | Predictor family | Per-unit margin | Tier | Firing-control evidence | Scale (verified) |
|---|---|---|---|---|---|---|---|---|
| 1 | Perception codebook (RNS decode) | `exp_rns_subblock_margin_exact_prefactor_v2` | M-ary orthogonal signaling vs `m-1` competitors | ORDER-STATISTIC | closed-form `E_z[Phi(mu+z)^(m-1)]` | **CG** | exact `gm_exact`=[1.11,1.05,1.01]x vs loose union bound `gm_union`=[2.73,2.39,2.54]x (>=2.27x tightening, all 3 moduli) | FULL, cert_ledger CHAIN_GRADE 2026-07-06T05:25Z |
| 2 | Memory (FHRR bundle capacity) | `exp_fhrr_bundle_capacity_exact_margin_v1` | superposition-crowded argmax vs `V-1` competitors as K bundled pairs grow | ORDER-STATISTIC | closed-form `K_crit` | **CG** | exact `dev<=0.05` (max 0.0122) vs asymptotic `N/(2 ln N)` 10-35% off, cross-seed `cv_max`=1.54% | FULL, cert_ledger CHAIN_GRADE 2026-07-06T05:25Z |
| 3 | Reasoning (multi-hop chain depth) | `exp_reasoning_depth_exact_order_statistic_self_margin_v1` | Poisson-occupancy CAPTURE argmax (c co-colliding items), STATIONARY per-hop, chain-composed | ORDER-STATISTIC (chain, stationary) via PRODUCT-LAW composition `D*=ln(FLOOR)/ln(p_hop)` | closed-form capture partial-credit `p_hop` | **CG** | mean_ratio=0.987 unbiased (naive occupancy-binary control stayed 2.02x biased), per-op ratio-error<=1.50x at all 24 non-censored points, cv=0.1021 | FULL, cert_ledger CHAIN_GRADE 2026-07-06T06:45Z |
| 4 | Comprehension, hard regime (role/block order-recovery) | `exp_frame_order_recovery_hard_comprehension_v2` (supersedes v1 HARD_FAIL) | role->block assignment survives superposition at the cited cliff scale | ORDER-STATISTIC (2-stage), pos-ctrl regime fix over v1 | v2 formula, regime-corrected | **CG** | order_recovery=1.000 (>>chance 0.167, occupancy control stuck at 0.195); decode holds 0.870 (>=0.6, cited cliff 0.856); full-parse survives superposition 0.800 (>=0.5) | FULL, cert_ledger CHAIN_GRADE 2026-07-06T15:34Z |
| 5 | Comprehension, correlated-superposition (order-recovery cliff, D8xV1000) | `exp_comprehension_order_recovery_pr_corrected_margin_v1` | superposition-crowded argmax vs `V_ROLE-1` competitors, but competitors are CORRELATED (low effective rank, not independent) | ORDER-STATISTIC + PR(V)-1 effective-rank substitution (participation ratio, not raw `V-1`) | quadrature with `n_comp=PR(V)-1` | **MIDDLE_BAND** (genuine partial revival, not full CG) | PR mean_ratio=1.0072 in-band, improve=1.999x vs naive-`V`, cv=0.0168 tight — BUT `perseed_max`=1.088 misses the 1.50 HARD-PASS sub-gate | FULL, cert_ledger MIDDLE_BAND 2026-07-06T14:00Z |
| 6 | Generation (block-local decode) | `exp_generation_decode_selfmargin_dupclass_exact_v1` | DISJOINT single-shot argmax, one token/block, k-sparse BIPOLAR bounded-overlap codes | COLLISION-COUNT (exact duplicate-codeword tie-break) | `p1=n_distinct(codebook)/V` | **CG** | `dup_mean_ratio`=1.0021 unbiased, `dup_rerr_max`=1.0407 (every non-sat cell <=4.1%), beats falsified PR-gaussian by 2.68x and naive-independent by 2.1e16x, iidinj/decorr/GATE_D controls all fire | FULL, cert_ledger CHAIN_GRADE 2026-07-06T17:13:41Z (landed at drill time) |
| 6b | (same capability, first attempt) | `exp_generation_decode_selfmargin_pr_transfer_v1` | mis-classified as continuous/correlated-superposition (order-stat/PR family) | ORDER-STATISTIC + PR (WRONG family for this regime) | PR quadrature | **HARD_FAIL** (falsified) | `improve`=0.7139x (WORSE than naive), `naive_biased`=False — the taxonomy's own self-correction case | FULL, cert_ledger HARD_FAIL 2026-07-06T15:44:59Z |
| 7 | Control, given-decomposition (branching x depth) | `exp_control_branching_depth_chain_survival_self_margin_v1` | multi-hop argmax chain (n_ops-ary picks), per-hop margin is a LEARNED successor-representation reachability score, horizon-degrading | PRODUCT-LAW CHAIN | fitted per-hop margin, calibrated at shallow depth, projected deep | **MEASURED_MECHANISM (MM)** — predicted MM ex-ante in the prep-drill, confirmed at canonical | `rmse_horizon`=0.0776 (all 5 seeds <=0.12 HP bar), `const_gap`=0.176 (beats flat-Hick baseline, every seed >=0.10), product-law `tf_dev`=0.020 (<=0.15); score-SHUFFLE firing control collapses fit (`mu0` 4.07 -> 0.027); 7/7 gates, 5/5 seeds | FULL, cert_ledger MEASURED_MECHANISM 2026-07-06T17:13:41Z (landed at drill time) |
| 8 | Compositional math (arithmetic derivation depth) | `exp_math_compositional_derivation_depth_self_margin_v1` | exact primitive chain (add/sub lossless to D=128); mul has an absorbing-zero SELF-HEALING property the chain-survival law doesn't model | PRODUCT-LAW CHAIN (reused from reasoning-depth, NOT re-derived) | reasoning-depth's law applied as-is | **MEASURED_MECHANISM** — safe CONSERVATIVE depth bound, not tight | add/sub ratio ~1.04x (tight); mul: law over-predicts collapse (self-healing beats the naive bound) — a safe, not exact, bound | FULL, cert_ledger MEASURED_MECHANISM 2026-07-06T15:34:10Z |
| 9 | Integration (compounding_ratio) | `exp_integration_full_stack_full_fidelity_v1` | N/A — not a collapse-boundary question | N/A | N/A | **CG (already), N/A to this taxonomy** | `compounding_ratio`=0.991, stages compose near-independently; nothing left to predict | FULL, HARD_PASS |
| 10 | Perception/encoder (BGE concept-Gram spectrum) | RMT/free-probability drill (no cell — ACCEPT recommended) | continuous, heavy-tailed power-law spectrum (exponent -1.0 to -1.12, R^2=0.97-0.98), NOT bulk+spike | **NONE — resists all 3 families** | N/A | **RESISTOR (honest ACCEPT-boundary)** | covariance-matched Gaussian surrogate explains 60-95% of the collapse gap but leaves a statistically robust residual of 13-26 accuracy points (4-20 SEs), concentrated exactly at onset-of-collapse (sigma=0.10-0.16) | measured directly off real BGE embeddings, n=1500 paired queries, 2 independent V |
| 11 | Generalization | prior established work | information-theoretic one-to-many entropy ceiling — no collision/argmax-vs-competitors structure at all | **NONE** | N/A | **RESISTOR (proven bound, already closed)** | all previously-tried levers falsified | prior sessions |
| 12 | Control, AUTONOMOUS decomposition | `exp_pfc_gate_autonomous_waypoint_discovery_v1` + rescue attempt (both HARD_FAIL) | uncorrected chained argmax anchored on a possibly-WRONG prior discovered state (off-policy query to a learned value function) | **NONE — different math family**: Ross-Bagnell-style `O(epsilon*T^2)` distribution-shift compounding regret, not a stationary/horizon-decaying collision probability | N/A | **RESISTOR (already 2x-drilled + rescue-tested to an honest bound)** | matched-entropy dissociation: recovery=0.690 @ 1 step vs 0.073 @ 3 steps at IDENTICAL entropy=8.0 despite per-hop signal 5.4pp WORSE at the high-recovery point — chain LENGTH, not signal quality, is the dominant driver | prior session, re-confirmed this session's frontier map |

**Tally (this taxonomy, 12 rows / 10 distinct capabilities incl. 1 falsified sibling attempt):** 5 CG
(RNS, FHRR, reasoning-depth, hard-comprehension order-recovery v2, generation dup-class) + 1 MIDDLE_BAND
(comprehension correlated-superposition) + 2 MM (control given-decomposition, compositional-math reused bound)
+ 1 falsified-then-corrected attempt (generation PR-transfer) + 3 honest RESISTORS (encoder power-law,
generalization entropy-ceiling, control autonomous-decomposition) + 1 N/A (integration, already solved by a
different mechanism).

---

## (c) The organizing principle, stated precisely

**The substrate's capacity to predict its own capability-collapse boundary in closed form is not one law —
it is a lookup keyed on the DECODE REGIME, with the tier (CG vs MM) determined by a SEPARATE, orthogonal
question (is the per-unit margin closed-form/parameter-free, or learned/horizon-degrading):**

1. **Classify the decode regime first**, from the decode mechanism alone (readable from the cell's own code,
   zero trials needed):
   - Many terms CLT-averaged into one continuous competition (e.g. `L` tokens superposed per block) ->
     **ORDER-STATISTIC** family (Gauss-Hermite quadrature on `E_z[Phi(mu+z)^(m-1)]`-type integrals). If the
     competitors are mutually CORRELATED rather than independent (a low-effective-rank Gram, e.g. inherited
     from a heavy-tailed encoder spectrum), substitute the raw competitor count `V-1` with the participation
     ratio `PR(V)-1` before quadrature — same machinery, corrected exponent.
   - Single-shot, disjoint, BOUNDED-magnitude decode (one token/block, sparse bipolar codes where self-overlap
     equals the maximum achievable overlap) -> **COLLISION-COUNT** family: the only failure mode is an EXACT
     duplicate codeword + argmax tie-break, so `p1 = n_distinct(codebook)/V` exactly, by construction — no
     continuum of near-misses to average over.
   - Multi-hop composition (the SAME decision structure repeated across a chain/depth axis) -> **PRODUCT-LAW
     CHAIN**: `P_chain = prod_h p_hop(h)`. The per-hop term itself is usually ALSO an order-statistic (this is
     the one place the three families compose rather than partition), but the chain adds its own question:
     is `p_hop` stationary (reasoning-depth: success resets to the exact true state, so post-failure dynamics
     never matter) or horizon-degrading (control: the per-hop margin comes from a goal-distance signal that
     itself shrinks as remaining horizon grows)?
2. **Tier separately, by whether the per-unit margin is closed-form:** CG when the margin follows exactly from
   codebook/geometry parameters (`N`, `M`, `V`, sparsity `k`) with no fitted constant — RNS, FHRR,
   reasoning-depth's capture probability, hard-comprehension's regime-fixed formula, and generation's
   `n_distinct/V` are all in this bucket. MM/semi-empirical when the margin must be MEASURED (fit at shallow
   depth, or read off a learned value function) because no closed form exists in terms of the substrate's own
   geometric parameters — control-branching's SR-reachability margin and compositional-math's reused
   (not re-derived) bound both land here.
3. **A capability RESISTS the whole taxonomy** (not just misses a CG bar) when its collapse mechanism is not a
   stationary or horizon-decaying collision probability at all — a genuinely different math family. Three
   confirmed cases, three DIFFERENT reasons: a continuous heavy-tailed spectral problem (encoder), an
   information-theoretic entropy ceiling with no collision structure (generalization), and an off-policy
   distribution-shift compounding regret (autonomous decomposition). Forcing any of these into an
   order-statistic mold would be exactly the premature pattern-matching this session's own honesty gate
   exists to prevent.

---

## (d) CG_META candidacy assessment (the honest part)

**What would make this a genuine, cert-tierable cross-capability META claim:** a discriminating rule that,
given a NEW capability's decode mechanism (read from code, no fit computed yet), correctly predicts (i) which
of the 3 families governs its collapse — or that it resists all 3 — and (ii) whether the tier will land CG
or MM, VERIFIED against data the rule was not tuned on.

**Evidence FOR (genuine prospective track record, not purely post-hoc):**
- **Control-branching (row 7) was predicted MM, not CG, in the prep-drill BEFORE the canonical FULL was
  dispatched** (`research_control_branching_depth_self_margin_chain_survival_family_2026-07-06.md`: "Expected
  tier here: MM ... CG path is a separate, harder theory step"). The canonical FULL landed exactly there
  (MEASURED_MECHANISM, confirmed at drill time). This is a real ex-ante tier prediction, confirmed.
- **Generation (rows 6/6b) is a genuine self-correction, not a lucky guess.** The frontier map's FIRST
  classification (row 4, "mechanistically already covered by RNS/FHRR's continuous `mu(N,M)`") was WRONG and
  was empirically falsified at canonical scale (`exp_generation_decode_selfmargin_pr_transfer_v1`, HARD_FAIL,
  `improve`=0.7139x). The correct reclassification (disjoint/bounded-magnitude -> collision-count, not
  order-statistic) was derived from the SAME decode-regime logic, not from re-tuning the same family harder,
  and it then landed CG at 1.02-4% error. A rule that can be wrong, get falsified cleanly, and self-correct via
  reclassification (rather than parameter-patching) is doing real discriminating work.
- The 3 RESISTORS were independently confirmed via THREE DIFFERENT METHODOLOGIES (direct spectral measurement,
  established information theory, empirical rescue-attempt failure) — convergent evidence the rule's
  "this does not fit" calls are not just unexamined defaults.

**Evidence AGAINST (the honest circularity concern):**
- **Every single capability in the table above was ALSO used to build or refine the taxonomy itself.**
  Comprehension needed the PR-correction INVENTED mid-session to even reach MIDDLE_BAND; generation needed a
  full falsify-and-reclassify cycle; hard-comprehension needed a "v2, pos-ctrl regime fix" over a v1 that
  itself did not land at v1's classification. None of these are contamination in the sense of cheating, but
  they mean the rule as currently stated (`reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`)
  is FITTED TO exactly the cases used to state it. There is, as of this note, **no case of a capability that
  was untouched by any self-margin-adjacent analysis before its family+tier was committed to writing.**
- This is precisely the gap this codebase's own standing methodology rule (`[[feedback-held-out-test-
  methodology-required]]`, originally stated for macro-F1 capability claims) exists to catch: an in-sample fit,
  however principled-looking, is not evidence of generalization until it predicts something it wasn't shaped
  around. Promoting this to a CG_META atom NOW — however clean the taxonomy looks — would be exactly the kind
  of overclaim the lit-scan calibration discipline and the "don't force a cert-claim" instruction for this
  drill are designed to prevent.

**Verdict: CG_META-CANDIDATE, not yet cert-tierable.** Keep it filed as the reference it already is. Do not
mint a CG_META atom. Promote only if the held-out test below is run and clears — that test is cheap (mostly
zero-new-trials, reusing already-landed FULL data) and could plausibly run within a single future research
cycle.

### Held-out test (sketched, predictions committed NOW, before any fit is computed)

Two capabilities, both with FULL data already landed, NEITHER touched by any self-margin work to date:

**Candidate A — predicted to CONFIRM the order-statistic/CG branch.**
`exp_resonator_capacity_gpu_v1` (K-way resonator-network factorization decode: argmax success rate by number
of bound factors `K`, FULL landed HARD_FAIL — `K2`:1.0, `K3`:0.7, `K4`:0.142 at `N=4096`) and/or
`exp_capacity_cliff_graceful_full_v3` (bundle-capacity `alpha`-sweep, FULL landed HARD_PASS, monotone cliff,
`n_hp=5/5`). **Prediction, committed now:** both classify as SUPERPOSITION-crowded argmax decode against a
load parameter (`K` or `alpha`) growing the effective competitor pool — structurally the same regime as FHRR's
`K_crit` — so the taxonomy predicts ORDER-STATISTIC family, plausibly CG-tractable if a closed-form crosstalk
margin exists in `(N, K, alpha)` alone. **Named ambiguity, stated honestly rather than hidden:** resonator
decode is ITERATIVE multi-factor search, not a single-shot argmax — it may instead belong to the PRODUCT-LAW
CHAIN family (factors resolved in sequence, each conditioned on the others), which would still predict CG or MM
depending on whether the per-factor margin is closed-form, but is a genuinely different sub-call than the
bundle-capacity cliff. Both possibilities are ORDER-STATISTIC-family-adjacent, not COLLISION-COUNT or
RESISTOR — that specific, falsifiable, three-way exclusion is the actual test.

**Candidate B — predicted to RESIST all three families.**
The continual-learning / catastrophic-forgetting family, specifically a REPLAY-SCHEDULE-dependent retention
curve (not a static write-load capacity cliff — `exp_a8_continual_writes_no_catastrophic_forgetting_v1`'s
`alpha` sweep is itself likely STILL order-statistic/crosstalk-family and should NOT be used for this half of
the test, since it is structurally closer to FHRR's bundle-capacity question than to a drift process).
**Prediction, committed now, at LOWER confidence than Candidate A:** a genuine replay-rate-dependent
forgetting/consolidation curve is governed by a distribution-shift/drift process (population-genetics-adjacent
per this session's own field-advisor adjacency table, `nonequilibrium-stat-mech` / `population-genetics-
wright-fisher` rows) — structurally closer to autonomous-decomposition's Ross-Bagnell compounding regret than
to a stationary collision probability — so the taxonomy predicts this RESISTS all 3 families (a 4th resistor,
same kind of boundary as row 12). **Explicitly flagged as the weaker half of this test:** unlike Candidate A,
no specific existing cell has been verified in THIS drill to cleanly isolate a replay-schedule (not write-load)
retention curve — `exp_bet_b_genreplay_phaseD_v1_n2048` (GENREPLAY_MIDDLE_BAND) and
`exp_c2_cascade_stc_swr_continual_v2` (HARD_FAIL, "mechanism adds nothing") are candidates but their mechanism
was only skimmed, not verified to the same standard as Candidate A. **The FIRST step of running this half of
the test is confirming a suitable existing FULL cell exists before classifying it** — if none does, Candidate B
becomes a small new (still cheap, CPU-only) cell rather than a zero-new-trial recompute.

---

## (e) Cheap decisive test (for the held-out promotion path itself)

Already-runnable, zero-new-trials for Candidate A: rebuild the taxonomy's order-statistic quadrature
(reusing the exact `numpy.polynomial.hermite.hermgauss` machinery already coded three times — RNS, FHRR,
reasoning-depth) with `(N, K)` or `(N, alpha)` plugged in from `exp_resonator_capacity_gpu_v1` /
`exp_capacity_cliff_graceful_full_v3`'s own landed configs, and compare the predicted collapse curve against
the already-measured `success by K` / cliff-location numbers cited above — no new dispatch, no new seeds,
identical discipline to every promotion in this session's arc (RNS v1->v2, reasoning-depth's own MB->CG
cheap-test, generation's dupclass derivation). For Candidate B: first confirm/select the cell (see above), then
the SAME off-disk recompute-and-compare pattern applies once a candidate cell is confirmed.

---

## (f) Falsifiable predictions (HARD-PASS / HARD-FAIL) for CG_META promotion

**HARD-PASS** (promotes the taxonomy from reference to a genuine CG_META atom):
- Candidate A's off-disk order-statistic (or product-law-chain, per the named ambiguity) recompute clears the
  SAME `<=1.5x` ratio-error / unbiased-mean-in-`[0.80,1.25]` band the 5 sibling CGs cleared, AND the
  classification made in THIS note (order-statistic-family, not collision-count, not resistor) is not revised
  after seeing the fit — i.e., the three-way exclusion holds as stated, AND
- Candidate B (once a suitable cell is confirmed) genuinely resists a forced fit from all 3 families at the
  same tolerance bands used throughout this session (aggregate mean-ratio outside `[0.60,1.70]` for every
  family attempted, or the best-fitting family's own firing control fails to fire) — i.e., the rule correctly
  predicts a NEGATIVE, not just a positive, AND
- both classifications in this section were committed BEFORE the fits were computed (this note is the
  pre-registration; a future note doing the actual recompute must cite it, not silently redo the classification
  after looking at the numbers).

**HARD-FAIL** (the taxonomy is descriptive/in-sample only, not a generalizing meta-law — revert fully to
reference-only framing, do not retry the same held-out pair with a relaxed tolerance):
- Candidate A's predicted family fails to reach even MM-level fit quality (ratio-error `>2.0x` or no stable
  cross-seed correction achievable) — meaning the order-statistic default was wrong even in the "easy," most
  structurally-analogous case, OR
- Candidate B ALSO fits one of the 3 families within tolerance — meaning the taxonomy does not actually
  discriminate (it would fit almost anything with enough post-hoc family-picking), OR
- either classification in this section requires revision after the fit is seen (a recurrence of the
  circularity this assessment flags) — that outcome specifically falsifies the CLASSIFIER's prospective value,
  independent of whether the individual fits happen to look good.

**MIDDLE (plausible, honest intermediate outcome):** Candidate A confirms cleanly (extending the CG count to
6) but Candidate B's mechanism turns out, on inspection, to ALSO be order-statistic/crosstalk-family (i.e., the
"4th resistor" class was mis-anticipated and continual-forgetting is not actually a good discriminating test
case) — in that event, the taxonomy gets a real 6th CG confirmation (useful, promotable evidence) but the
DISCRIMINATING-power question (does it correctly predict resistance, not just fits) remains open and needs a
different B candidate, not a declared CG_META promotion on A alone.

---

## (g) Honest scope: the taxonomy is real and systematic but NOT universal

Three resistors bound it today (encoder power-law spectrum, generalization's entropy ceiling, control's
autonomous-decomposition compounding regret), each closed for a STRUCTURALLY DIFFERENT reason — this is itself
evidence the substrate's failure modes have genuine diversity, not one hidden master law dressed up in three
costumes. A 4th plausible resistor (replay-schedule-dependent forgetting) is flagged above but not yet
confirmed. The taxonomy should not be marketed as "the substrate predicts everything it does" — its honest,
defensible claim is narrower and, if anything, more useful: **for capabilities whose collapse is decode-driven
(single-shot, superposition, or chain-composed argmax), classifying the decode regime from code alone, before
running a single trial, tells you which of 3 known families to try and gives a real (if imperfect) prior on
whether the fit will be exact (CG) or merely well-calibrated (MM) — and for capabilities whose collapse comes
from a genuinely different process (spectral, information-theoretic, or distribution-shift), the taxonomy's own
logic says "this will resist," which is itself a useful, falsifiable, time-saving call** (this session's own
generation-decode arc shows what it costs NOT to make that call first: one full falsified attempt before the
right family was found).

---

## (h) Cross-thread synthesis

- Directly assembles and re-verifies (all off-disk, this drill) `research_capability_self_margin_frontier_map_
  2026-07-06.md` (the original 9-row inventory + honesty gate), `research_generation_decode_correlated_
  collision_exact_margin_2026-07-06.md` (the collision-count derivation + the row-4 correction), `research_
  control_branching_depth_self_margin_chain_survival_family_2026-07-06.md` (the MM tier prediction, now
  confirmed), `research_reasoning_depth_self_margin_closed_form_2026-07-06.md` (the first capability-level CG),
  `research_sub_gaussian_tail_self_margin_revival_participation_ratio_2026-07-06.md` (the PR-correction
  mechanism), and `research_encoder_rmt_spectral_self_margin_2026-07-06.md` (the encoder resistor, confirmed by
  direct measurement not just lit-scan). The taxonomy memory
  (`reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`) already captures the 3-family split;
  this note adds the CG_META honesty assessment that memory file does not attempt.
- **Two tiers finalized DURING this drill** (both at cert_ledger `ts_iso=2026-07-06T17:13:41Z`, read directly
  off `data/substrate_index/meta/cert_ledger.jsonl`'s tail): generation dup-class promoted CHAIN_GRADE
  (`dup_mean_ratio`=1.0021), control-branching landed MEASURED_MECHANISM (`rmse_horizon`=0.0776, `const_gap`=
  0.176) — exactly the tiers the two source notes predicted ex-ante. This IS the strongest piece of evidence
  in this note's CG_META argument, and it is also exactly why the argument stops short of full promotion: two
  confirmed ex-ante predictions is a real but small track record, not yet a held-out generalization test.
- Does not reopen any of the three RESISTOR closures (encoder, generalization, autonomous-decomposition) — this
  synthesis independently arrives at the same "these are structurally different, not just harder" conclusion
  each of the source notes reached separately.

## (i) Substrate-product implications

- The substrate now carries **5 exact (CG) self-margins spanning 2 codebook families (RNS/FHRR) and 3
  capability layers (reasoning-depth, hard-comprehension order-recovery, generation dup-class)**, plus 1
  genuine partial (comprehension MIDDLE_BAND), plus 2 honestly-tiered semi-empirical MM capability-margins
  (control-branching, compositional-math-as-conservative-bound), plus 3 named, mechanistically-distinct
  RESISTORS. The reusable product claim is not "the substrate predicts all its own limits" — it is the more
  defensible **"the substrate can classify, cheaply and from its own decode code alone, which of a small,
  named set of predictor families governs any given capability's collapse, and whether that prediction will be
  exact or merely well-calibrated, before spending a full derivation-and-dispatch cycle finding out the hard
  way"** — a monitor-not-control capability with a concrete cost-avoidance story (this session's own
  generation arc: one wasted PR-transfer dispatch avoided in future cases by classifying decode-boundedness
  FIRST).
- The classification checklist itself (decode-mode -> family; margin-closed-form-or-not -> tier) is now
  concrete enough to operationalize as a pre-flight step before authoring ANY future self-margin cell — cheaper
  than a lit-scan, cheaper than a failed dispatch. This is the taxonomy's real, ship-now value, independent of
  the CG_META question.
- The CG_META question itself should be treated as a scheduled follow-up (the held-out test above), not a
  blocker — the taxonomy is useful as a reference TODAY regardless of whether it is ever promoted to a
  cert-tiered meta-atom.

## (j) Citations (verified count)

Internal-synthesis drill (2x-style depth pass over this session's own already-landed cells and notes, per
`[[feedback-2x-means-depth]]`) — no new external lit-scan dispatched this cycle; all citations below are
internal, verified on-disk at drill time:
- `data/substrate_index/meta/cert_ledger.jsonl` (1480 lines; tail entries at `2026-07-06T05:25Z`,
  `T06:45Z`, `T14:00Z`, `T15:34Z`, `T15:44:59Z`, `T17:13:41Z` directly read and quoted above).
- 9 metrics.json files read directly: `exp_rns_subblock_margin_exact_prefactor_v2`,
  `exp_fhrr_bundle_capacity_exact_margin_v1`, `exp_reasoning_depth_exact_order_statistic_self_margin_v1`,
  `exp_frame_order_recovery_hard_comprehension_v2`, `exp_generation_decode_selfmargin_dupclass_exact_v1`,
  `exp_control_branching_depth_chain_survival_self_margin_v1`, `exp_resonator_capacity_gpu_v1`,
  `exp_capacity_cliff_graceful_full_v3`, `exp_a8_continual_writes_no_catastrophic_forgetting_v1`.
- 6 source research notes (2026-07-06, this session): `research_capability_self_margin_frontier_map`,
  `research_generation_decode_correlated_collision_exact_margin`,
  `research_control_branching_depth_self_margin_chain_survival_family`,
  `research_reasoning_depth_self_margin_closed_form`,
  `research_sub_gaussian_tail_self_margin_revival_participation_ratio`,
  `research_encoder_rmt_spectral_self_margin`.
- 1 memory reference file: `reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`.

**Total: 1 ledger file + 9 metrics files + 6 research notes + 1 reference memory = 17 verified internal
sources. No external citations this cycle (internal audit/synthesis drill, not a lit-scan).**

## P_deflated (calibration penalty applied)

Raw confidence the held-out test (Candidate A + B) would clear CG_META promotion if run today: ~0.55 (strong
structural precedent for A via FHRR; plausible but weaker structural case for B via the Ross-Bagnell/
Wright-Fisher adjacency, and B's specific cell is not yet confirmed). Per the mandatory novel-synthesis cap and
the additional circularity concern named in section (d) (this is a meta-level claim about a classifier's
discriminating power, a harder-to-calibrate object than a single capability's margin): **P_deflated = 0.40**,
capped below the standard 0.50 novel-synthesis ceiling because of the compounded novelty (new capability x
new classification-validity question).
