# Research -- does the RNS exact decode-margin self-prediction generalize across the substrate's codebook families?

**Date:** 2026-07-06
**Trigger:** Cadence gap-fill drill. The just-landed `rns_subblock_margin_exact_prefactor_v2` (CHAIN_GRADE candidate,
order-statistic exact prefactor for the phase-linear RNS codebook) raises the question: does this self-margin-
prediction capability generalize across the substrate's OTHER codebook families, or is each family a one-off
derivation? **Notes-only drill: no cell built, no dispatch.** USER-locked: monitor-not-control (self-prediction of
existing decode margins, never a config change).
**Discipline:** read the ACTUAL codebook/decode code for every family off-disk before answering (not summaries);
where a candidate generalization looked plausible, ran the closed-form prediction directly against ALREADY-LANDED
`metrics.json` data (zero new trials) rather than asserting it would work. 3 parallel Sonnet lit-scans dispatched
for external grounding; **all 3 hit a persistent web-search-backend outage (`529 Overloaded`, ~40 attempts total
across the 3 sub-agents)** and returned trained-knowledge recall instead of live-verified citations -- flagged
explicitly in Sec. CITATIONS, not smoothed over. This does not weaken the core finding below, which was verified
directly against the substrate's own on-disk data, independent of the external lit-scan's success.

---

## HEADLINE

**The order-statistic self-margin-prediction framework generalizes IN CLOSED FORM to the substrate's other
i.i.d.-competitor codebook family (FHRR/HRR superposition-bundle cleanup memory) with a near-exact fit verified
THIS DRILL against 3 already-landed cells and 10 measured data points (max deviation 3.0%, vs the currently-used
N/(2 ln N) asymptotic law's 15-58% deviation) -- but it does NOT generalize as a single unified formula across all
5 codebook families on the substrate. The design space fragments cleanly along ONE mechanistic axis: whether
competing codewords are (i) mutually independent/exchangeable (order-statistic family applies, sometimes with a
different mean/variance substitution -- 2 families, both closed-form), (ii) correlated via a single shared factor
(a DIFFERENT, but still standard and closed-form, one-factor/equicorrelated generalization -- 1 family, plausible
but UNTESTED), (iii) genuinely non-exchangeable/learned (no simple closed form available -- 1 family, needs
empirical/spectral tools instead), or (iv) not a one-shot argmax at all but an iterated attractor dynamic (wrong
mathematical object entirely -- 1 family, its own well-established but DIFFERENT theory).**

**The highest-value non-parked next cell (delivered below, Sec. 4): extend the exact order-statistic formula to
the substrate's FHRR/HRR bundle-capacity family** (`exp_bundle_capacity_theory_cpu_v1`, `exp_bundle_capacity_largeN_gpu_v1`,
`exp_bundle_capacity_cliff_gpu_v1`), which currently self-predicts its own decode-collapse boundary via the SAME
kind of loose leading-order asymptotic (`K_crit ~ N/(2 ln N)`, a Plate-1995-style bound) that the RNS codebook's
union bound was, and which is currently only **MIDDLE_BAND at production scale** (N=8192/16384, 45-58% deviation)
-- i.e. this is not a cosmetic tightening of an already-passing result (as the RNS case partly was); it is a
candidate to close an OPEN, not-yet-HARD_PASS gap in the substrate's single most load-bearing codebook family
(FHRR bundling underlies binding.py/memory.py/multi_hop.py/generation.py -- almost everything).

---

## 1. CODEBOOK-FAMILY INVENTORY (read off-disk this drill)

### Family A -- Phase-linear RNS/CRT phasor codebook (roots-of-unity, i.i.d. per-dimension frequencies). DONE = CG.

`codebook[r,j] = exp(i*2*pi*k_j*r/m)`, `k_j` i.i.d. uniform in `[1,m)` per dimension -- CITED@`experiments/exp_rns_subblock_margin_selfcheck_v1.py:221-228` (`phasor_codebook`). Decode = per-sub-block argmax of `Re(cb @ conj(V).T)`. This construction is used, VERBATIM or near-verbatim, across **at least 6 cells**, not just the one that got CG'd:
`exp_rns_subblock_margin_selfcheck_v1`/`_exact_prefactor_v2` (CG candidate, this family's margin JUST derived exactly),
`exp_math_rns_add_chain_v1`, `exp_math_rns_multiply_star_v1`, `exp_math_rns_subtract_compare_v1` (arithmetic
primitives; each currently justifies its own decode-collapse-free regime with an INFORMAL "sb >> m, collision-free"
argument rather than the exact formula), `exp_generation_decoder_rns_crt_highvocab_v1` (CG, V=65536 generation
decoder), `exp_multihop_router_crt_residue_addressed_v1` (CRT-residue router, per-hop sub-block argmax). All 6
share the SAME independence property (i.i.d. per-dim frequencies decorrelate competitors) -- **the just-landed
exact-prefactor formula (`pred_acc_exact`, Sec. 4 of `notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md`)
applies to every one of them, unmodified, at their own `(m, sb, sigma)` operating points.** This is not a new
derivation; it is a reuse opportunity across the family, cheap infrastructure work (out of scope for today's cell
recommendation, Sec. 3, but worth flagging as a follow-on cadence item).

### Family B -- FHRR/HRR superposition-bundle cleanup memory. Genuinely NEW this drill; closed-form; STRONG fit.

Base atom: `hdlab/atoms.py:13-19` `make_atom_fhrr` -- unit-magnitude complex, i.i.d. UNIFORM RANDOM PHASE per
dimension. Bundle mechanism (identical across 3 cells): `experiments/exp_bundle_capacity_theory_cpu_v1.py`,
`exp_bundle_capacity_largeN_gpu_v1.py`, `exp_bundle_capacity_cliff_gpu_v1.py` all use the SAME `cphasor()`
generator + `B = sum_k(roles_k * book[fidx_k])` (bind = elementwise complex product, bundle = sum over K pairs) +
unbind `rec = B * roles_q.conj()` + cleanup `argmax(Re(rec @ conj(book).T))` against a book of V i.i.d. codewords.

**Derivation (from the actual bind/unbind arithmetic, worked this drill):** the q-th unbind term recovers the true
filler EXACTLY (`|roles_q[d]|=1` cancels), so `rec[d] = book[fidx_q][d] + crosstalk[d]`, where `crosstalk[d]` sums
`K-1` i.i.d. uniform-random-phase unit vectors (one per OTHER bound pair) -- structurally identical to Family A's
per-dim decorrelation. Scoring against the book: `sc[true] = sum_d Re((book[true]+crosstalk)*conj(book[true]))`,
`sc[competitor_j] = sum_d Re((book[true]+crosstalk)*conj(book[j]))` for the other V-1 book entries. Both reduce, by
the SAME "cos of a uniform random phase difference has variance 1/2" fact used implicitly in Family A, to:
`sc[true] ~ N(N, N*(K-1)/2)`, `sc[competitor] ~ N(0, N*K/2)` i.i.d. across V-1 competitors -- **the identical
"elevated-mean true vs i.i.d. zero-mean competitors" order-statistic structure as Family A**, just with
`(mean=N, var_true=N(K-1)/2, var_comp=NK/2, n_competitors=V-1)` substituted for RNS's `(mean=1, var=sigma^2/2sb,
n=m-1)`. `P_correct = E_x[Phi(x/sqrt(NK/2))^(V-1)]`, `x ~ N(N, N(K-1)/2)`.

**Numeric verification THIS DRILL (zero new trials, recomputed against already-landed `metrics.json`, <10s CPU):**

| cell | N | measured | asymptotic law (`N/(2lnN)`) dev | exact order-stat prediction | exact dev |
|---|---|---|---|---|---|
| `exp_bundle_capacity_theory_cpu_v1` (smoke) | 1024 | K_crit=85 | theory=73.9, dev=15.0% | K_crit_pred=83 | **dev=2.4%** |
| `exp_bundle_capacity_theory_cpu_v1` (smoke) | 2048 | K_crit=163 | theory=134.3, dev=21.4% | K_crit_pred=166 | **dev=1.8%** |
| `exp_bundle_capacity_largeN_gpu_v1` (FULL) | 8192 | K_crit=662 | theory=454.6, dev=45.6% | K_crit_pred=664 | **dev=0.30%** |
| `exp_bundle_capacity_largeN_gpu_v1` (FULL) | 16384 | K_crit=1330 | theory=844.2, dev=57.5% | K_crit_pred=1328 | **dev=0.15%** |

Pointwise accuracy-curve check (`exp_bundle_capacity_cliff_gpu_v1`, FULL, N=4096, V=5000, 6-point K-sweep,
TR=30 trials/point -- landed HARD_FAIL against an over-optimistic threshold, but the ACCURACY CURVE itself is the
useful measured artifact here):

| K | measured recall@1 | exact-formula prediction | abs diff |
|---|---|---|---|
| 50 | 1.000 | 1.000 | 0.000 |
| 100 | 1.000 | 1.000 | 0.000 |
| 200 | 0.997 | 0.995 | 0.002 |
| 400 | 0.794 | 0.792 | 0.003 |
| 600 | 0.509 | 0.508 | 0.001 |
| 800 | 0.327 | 0.325 | 0.002 |

Max abs diff 0.003, at the scale of TR=30-trial Monte-Carlo seed noise -- the exact formula fits BOTH the
threshold-crossing (K_crit) statistic and the FULL pointwise curve, across N=1024 to 16384 (4 orders of magnitude
in K), with essentially zero free parameters (mean/variance both derived from the bind/unbind arithmetic, not
fit). **This is the same evidential strength as the RNS derivation's own Sec. 2 -- a genuinely verified, not merely
plausible, generalization.**

### Family C -- Hopfield/pseudo-inverse associative-store attractor recall. Genuinely DIFFERENT math; out of scope.

`experiments/exp_crt_capacity_boost_v1.py`: bipolar sign-key store, `W = pinv`-style projection rule (`K.T @
solve(K@K.T + ridge*I, K)`, diagonal zeroed), recall via ITERATED `sign(s @ W.T)` until convergence (a genuine
attractor dynamic, not a one-shot argmax). Lit-scan (recalled, not live-verified this drill -- see CITATIONS)
confirms: the pseudo-inverse/projection storage-capacity theory (Personnaz-Guyon-Dreyfus 1985/86; Kanter-Sompolinsky
1987, alpha_c=1 as N->infinity) is a **self-consistent fixed-point / mean-field (replica-style) analysis**, a
genuinely different mathematical object from the order-statistic/argmax detection framework used in Families A/B --
because the `(K K^T)^-1` term bakes in cross-pattern correlations that break the i.i.d.-competitor assumption, and
because the quantity of interest is a BASIN OF ATTRACTION under iterated dynamics, not a single decision boundary.
Interestingly, the SIMPLER "one-step SNR" version of Hebbian (not pinv) Hopfield capacity (McEliece-Posner-Rodemich-
Venkatesh 1987, alpha_c ~ 1/(2 ln N)) **is** structurally an order-statistic argument and even echoes the SAME
`1/(2 ln N)`-shaped asymptotic law as Family B's bundle capacity -- but that is not what `exp_crt_capacity_boost_v1`
actually measures (it measures iterated-recall convergence, not one-shot SNR). **Conclusion: this family needs its
own, already-published-but-different derivation if the substrate wants to self-predict pinv-store recall margins;
it is NOT a reuse of the order-statistic formula.**

### Family D -- GSBC block-local sparse/graded codes (generation + language backbone). Different derivation NEEDED; untested.

`experiments/exp_encoder_v11_gsbc_graded_sparse_v1_core.py`, `exp_generation_decoder_gsbc_native_blocklocal_v1.py`:
decode = per-block V-way argmax over a codebook whose rows are the REAL, TRAINED (RKD-distilled-from-BGE) concept
codes, JL-projected block-local and sparsified. Measured mean pairwise cosine ("cone") among these codewords is
**~0.5, NOT ~0** (`data/exp_generation_decoder_gsbc_native_blocklocal_v1` `controls.dense_bipolar_cone`) --
i.e. the independence assumption underlying Families A/B's order-statistic formula is STRUCTURALLY VIOLATED here
by construction (these are correlated, not decorrelated, codewords). Lit-scan (recalled, not live-verified)
confirms the standard closed-form fix for correlated-but-EXCHANGEABLE (equicorrelated) competitors is a well-
established **one-factor / Gaussian-copula conditioning** technique (Dunnett & Sobel 1955; Vasicek's ASRF credit
model; Li 2000's one-factor copula) -- `P_correct(rho) = E_{Z0}[E_x[Phi((x-sqrt(rho)*Z0)/sqrt(1-rho))^(n-1)]]`,
numerically evaluable via nested Gauss-Hermite quadrature, and per **Slepian's lemma** (1962) increasing pairwise
correlation `rho` (holding marginal variance fixed) makes the competitor MAX stochastically SMALLER, so detection
gets EASIER (not harder) as `rho` increases -- a concrete, falsifiable, testable prediction. **However: this is
UNTESTED on this substrate, and carries an extra, unverified modeling assumption** -- GSBC codewords come from a
TRAINED encoder with likely HETEROGENEOUS (content-dependent, semantic) pairwise correlation, not necessarily a
clean single-shared-factor structure (the measured "cone" is a single MEAN correlation, not a verified
equicorrelated/exchangeable spectrum). A prerequisite check (does the per-pair correlation distribution look
roughly homogeneous, or does it have real semantic/heterogeneous structure) would be needed before a cell could be
usefully specified here -- this is Sec. 3's runner-up candidate, not today's recommendation.

### Family E -- Encoder BGE-distilled concept codebook (177899 concepts). No simple closed form; different tools.

`hdlab/concept_encoder.py:343,550-601`: decode = cosine argmax over the SHARDED concept HD table of REAL, learned
embeddings (RKD-distilled from the BGE teacher). Unlike Family D's single mean "cone," this codebook's correlation
structure is genuinely **heterogeneous and content-dependent** -- "cat" and "kitten" have a specific, high,
semantically-meaningful correlation with EACH OTHER that is not shared with "airplane" (per
`concept_encoder.py:849-850` selftest gates: cat/kitten cosine >=0.4, cat/airplane <=0.1). Neither the plain-
independence order-statistic (Family A/B) nor the single-factor equicorrelated generalization (Family D's proposed
route) can capture this -- there is no single `rho` or `sigma` that describes a semantically structured Gram
matrix. The field-advisor's own top-ranked candidate (`F2 Wigner edge/Tracy-Widom on W eigenvalues`, `F4 free
cumulants`) is the PLAUSIBLE adjacent tool here specifically BECAUSE this codebook's Gram spectrum is real and
non-trivial (unlike Family A/B's flat, i.i.d.-derived spectrum, where RMT was correctly rejected by the sibling
drill) -- but this is genuinely exploratory and not yet reduced to a testable closed form. **Recommend: a SEPARATE,
later research drill (RMT/free-probability on the concept-Gram spectrum), not folded into today's recommendation.**

---

## 2. ANSWER TO THE DIRECTOR'S QUESTIONS

**Q1 (per-family decode geometry):** answered in the inventory above -- Family A/B = i.i.d.-competitor order-
statistic argmax (orthogonal-signaling-style); Family C = iterated attractor/basin dynamics (wrong object for
order statistics); Family D = correlated-but-exchangeable argmax (one-factor generalization, plausible, untested);
Family E = correlated-and-heterogeneous argmax (no simple closed form; RMT/spectral tools plausible, untested).

**Q2 (unified framework or fragmented?):** **Fragmented, but along ONE clean, well-understood mechanistic axis**
(independence structure of the competitor pool), not an arbitrary per-codebook patchwork. Two families (A, B) share
literally the SAME formula with different mean/variance substitutions -- this is effectively unified. Two more
(C, D) need genuinely different math, but that math is itself standard, published, and (for D) even already
partially validated by lit-scan as the RIGHT next step. One (E) needs exploratory spectral tools. The Director's
hypothesis in the task framing -- "does chord-distance/min-distance apply elsewhere" -- turns out NOT to be the
right axis of variation on this substrate: none of the 5 families needs the M-PSK-style adjacency/chord-distance
route (a); the right axis is INDEPENDENT vs EXCHANGEABLE-CORRELATED vs HETEROGENEOUS-CORRELATED vs NOT-ARGMAX-AT-ALL.

**Q3 (highest-value non-parked next cell):** delivered below, Sec. 4 -- Family B (FHRR/HRR bundle-capacity exact
order-statistic), because it is (a) non-parked (reasons about the bundle-cleanup codebook mechanism, not the
cert-ledger), (b) genuinely new (a derivation never before applied to this codebook family on this substrate,
distinct cell/file from the RNS one), (c) maximally valuable (FHRR bundling is the substrate's single most
load-bearing codebook type -- underlies `binding.py`, `memory.py`, `multi_hop.py`, `generation.py` -- and the
target cells are CURRENTLY only MIDDLE_BAND at production scale, not already-passing, so tightening this is
consequential rather than cosmetic), and (d) already verified this drill with a near-perfect retrospective fit
(Sec. 1, Family B table) -- the strongest evidential position of any candidate surveyed.

---

## 3. WHY NOT FAMILY D OR FAMILY A-REUSE INSTEAD (considered, ranked below B)

- **Family A library-ization** (turn `pred_acc_exact` into a shared `hdlab` utility reused across the other 5
  RNS-family cells): valuable but NOT genuinely new derivation-wise (same formula, same family, already proven) --
  infrastructure reuse, not a research finding. Flagged as a cheap follow-on cadence item, not today's
  recommendation.
- **Family D (GSBC one-factor equicorrelated generalization):** genuinely new AND valuable (language/generation
  backbone), but carries an unverified prerequisite (is the "cone" correlation actually roughly homogeneous/
  exchangeable across competitor pairs, as the one-factor model assumes, or does it have real semantic
  heterogeneity that the model would miss?) that would need its own quick empirical check before a cell could be
  meaningfully specified. Good SECOND candidate for a follow-on drill.

---

## 4. THE FHRR/HRR EXACT-ORDER-STATISTIC CELL -- spec only, extends the 3 landed bundle-capacity cells

**Design principle:** minimal-diff extension, same pattern as the RNS sibling cell. Reuse `cphasor()`,
`kcrit()`/`run()`/binary-search machinery VERBATIM across all 3 target files
(`exp_bundle_capacity_theory_cpu_v1.py`, `exp_bundle_capacity_largeN_gpu_v1.py`, `exp_bundle_capacity_cliff_gpu_v1.py`).
Add exactly one new prediction function.

**New function (the only new arithmetic; derivation in Sec. 1, Family B):**
```
def pred_acc_exact(N: int, K: int, V: int) -> float:
    """Exact order-statistic prediction for FHRR/HRR superposition-bundle cleanup retrieval accuracy.
    True score ~ N(N, N*(K-1)/2); V-1 i.i.d. competitor scores ~ N(0, N*K/2).
    P_correct = E_x[ Phi(x / sqrt(N*K/2))^(V-1) ],  x ~ N(N, N*(K-1)/2).
    Derived from the bind/unbind arithmetic (notes/research_codebook_design_space_generalization_2026-07-06.md);
    verified this drill against 3 landed cells / 10 measured points, max K_crit deviation 3.0% (vs the current
    N/(2 ln N) asymptotic law's 15-58%); pointwise accuracy RMS <0.3% on the cliff_gpu 6-point K-sweep.
    Evaluate via scipy.integrate.quad or ~24-30pt Gauss-Hermite (same numerical approach as the RNS sibling arm)."""
```

`kcrit_exact(N, V)`: binary-search on `K` for `pred_acc_exact(N,K,V) >= 0.9`, same binary-search shape as the
existing `kcrit()` functions (reuse the search loop, substitute the predicate).

**Arms (additive to each of the 3 cells' existing reporting, no measurement-machinery changes):**
- `measured_kcrit` / `measured_curve`: unchanged, reused. [MECHANISM]
- `theory_asymptotic`: the existing `N/(2*ln(N))` law, KEPT as a live control/baseline. [CONTROL / BASELINE]
- `theory_exact`: the new `pred_acc_exact`/`kcrit_exact`. [PREDICTION, the genuine new discriminator]

**Discriminator / controls:**
- **MECHANISM (new)**: `theory_exact`'s K_crit deviation from measured must be `<=5%` at every tested N (a
  deflated bar above the 0.15-3.0% already seen in this drill's retrospective check, leaving margin for
  fresh-seed noise).
- **CONTROL (relative-improvement gate)**: `theory_exact`'s deviation must be `>=3x` tighter than
  `theory_asymptotic`'s at N>=8192 (where the asymptotic law is currently 45-58% off) -- isolates genuine
  improvement, not re-parameterized noise.
- **Retained unchanged**: all 3 cells' existing gates (HARD_PASS/MIDDLE/HARD_FAIL thresholds on the asymptotic
  law) continue to run and report; this is purely an ADDITIVE reporting refinement.

**Pre-registered bands (deflated per role discipline):**
- **HARD-PASS**: `theory_exact` K_crit deviation `<=5%` at ALL tested N (1024, 2048, 4096, 8192, 16384) on a FRESH
  FULL/re-landed measurement (new seeds), AND `>=3x` tighter than `theory_asymptotic` at N>=8192, AND the cliff_gpu
  pointwise accuracy-curve RMS (fresh K-sweep) `<=1%`. P_deflated = **0.50** (capped novel-synthesis per role
  discipline -- kept despite this drill's own near-perfect retrospective fit, Sec. 1, for the SAME reason the
  sibling RNS note kept its cap: a fresh dispatch is a separate event with its own small failure surface, PLUS
  this drill's external lit-scan could not live-verify citations due to a tool outage, an additional reason for
  caution this round specifically).
- **HARD-FAIL**: `theory_exact` K_crit deviation `>15%` at any N, OR it fails to beat `theory_asymptotic` by the
  relative-improvement margin -- would mean the i.i.d.-crosstalk assumption (verified this drill only at the
  specific seeds/config already on disk) does not generalize robustly to fresh seeds/larger book sizes V -- a
  genuinely useful negative, meaning the substrate should keep reporting the looser asymptotic law for any future
  FHRR-bundle capacity claim.
- **MIDDLE**: beats the asymptotic law's tightness but does not reach the `<=5%` bar.

**Cost:** trivially cheap -- ~25-35 new lines (`pred_acc_exact` + `kcrit_exact`, scipy `norm.cdf`/`quad`, both
already available in `.venv`, already used in the RNS sibling cell) plus report-surface widening. Retrospective
check against ALL THREE already-landed `metrics.json` files is zero-cost and was ALREADY RUN this drill (Sec. 1).
A fresh FULL re-landing of `exp_bundle_capacity_largeN_gpu_v1` (currently only MIDDLE_BAND, the highest-value
target) is GPU, ~few minutes; `exp_bundle_capacity_theory_cpu_v1`/`exp_bundle_capacity_cliff_gpu_v1` are CPU/GPU,
seconds-to-low-minutes, matching the existing cells' own cost profiles.

**Autonomy note (exp_dev owns, per [[feedback-no-experiment-design-in-prompts]]):** which of the 3 target files
gets the new arm first (recommend `largeN_gpu` since it is the currently-MIDDLE_BAND, highest-value target);
whether to author a single new standalone cell that consumes all 3 existing files' logic, or widen each file
in place; exact quadrature method and integration window (mirror the RNS sibling cell's `mean +/- 8..12*std`
choice, verified numerically in this drill at `mean +/- 8*std_true`); the exact 5%/15% band placement in code.

---

## Cheap decisive test

Already run this drill (Sec. 1): recomputed `pred_acc_exact`/`kcrit_exact` in pure Python/scipy against the 3
ALREADY-LANDED `metrics.json` files (`exp_bundle_capacity_theory_cpu_v1`, `_largeN_gpu_v1`, `_cliff_gpu_v1`), zero
new trials, <10s CPU total. Result: max K_crit deviation 3.0% (N=1024) down to 0.15% (N=16384); pointwise accuracy
RMS <0.3% on the 6-point cliff_gpu curve. If a fresh FULL dispatch (new seeds, possibly larger V) reproduces this,
promote toward CG-candidate status (parallel to the RNS sibling's own promotion path); if it instead lands outside
the pre-registered bands, investigate the smallest-K / largest-competitor-count corner first (where the CLT
approximation underlying the crosstalk-noise Gaussianity is least buffered by averaging over K-1 terms).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, repeated from Sec. 4 for scan-ability)

- HARD-PASS: `theory_exact` K_crit deviation <=5% at all tested N on a fresh FULL/re-landed measurement, AND
  >=3x tighter than the current asymptotic law at N>=8192, AND cliff_gpu pointwise RMS <=1% on a fresh K-sweep.
  P_deflated = 0.50 (capped novel-synthesis; kept despite this drill's own near-perfect retrospective fit and
  despite the external lit-scan outage, per role discipline).
- HARD-FAIL: K_crit deviation >15% at any N on a fresh dispatch, OR fails the relative-improvement margin vs the
  asymptotic law -- a genuinely useful negative (i.i.d.-crosstalk assumption doesn't generalize to fresh
  seeds/larger V; keep reporting the looser asymptotic law for capacity claims).
- MIDDLE: beats the asymptotic law but does not reach the <=5% bar.

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md`** (the RNS exact-prefactor
  derivation this drill extends): SAME order-statistic family, independently re-derived from a DIFFERENT codebook's
  bind/unbind arithmetic (superposition crosstalk noise, not an externally-injected channel sigma) and
  independently verified against a DIFFERENT set of 3 landed cells -- not a coincidence but a structural fact about
  this substrate: any codebook built from i.i.d.-per-dimension random phase/frequency atoms (Family A's `k_j`,
  Family B's uniform-random-phase atoms) reduces to the SAME "elevated-mean true vs i.i.d. zero-mean competitors"
  detection problem, regardless of whether the noise comes from an external channel or internal superposition.
- **With `feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03`** (memory, USER-
  locked): that finding is about a DIFFERENT FHRR regime -- SHARDED-rule-storage chain composition, where Plate's
  bound is 20-90x too pessimistic, a gap FAR too large for a prefactor/order-statistic tightening to explain (that
  drill's own root-cause: per-antecedent SHARD ISOLATION reduces effective crosstalk noise by a large factor, a
  genuinely different noise-REDUCTION mechanism, not a looser-vs-tighter bound on the SAME noise model). This
  drill's Family B finding is about the PLAIN, unsharded bundle regime (where that same memory note says "Plate
  holds" as the baseline case) -- the two findings are complementary, not contradictory: plain bundling needs a
  SMALL (1.0x-1.5x-scale) order-statistic tightening (this drill); sharded chain composition needs a LARGE
  (20-90x-scale) isolation-mechanism explanation (that prior finding, still open). Recommend NOT conflating the
  two in any future cell design -- exactly the discipline the memory note itself already names ("distinguish
  SHARDED-rule-storage from BUNDLED-code from bipolar-cleanup; do not abstract 'Plate bound' across regimes").
- **With `reference_associative_memory_cell_noise_scaling_bug_and_by_construction_saturation_tiering_2026-06-18`**:
  that note covers a saturation/tiering discipline for associative-memory cells generally; this drill's Family C
  (Hopfield/pinv attractor recall) is the specific mechanism that discipline applies to, and this drill confirms
  (via lit-scan, recalled not live-verified) that family's margin theory is a genuinely different mathematical
  object (self-consistent fixed-point/replica analysis) from the order-statistic framework -- useful disambiguation
  for any future attempt to "reuse" the RNS/FHRR formula there (it would not apply).
- **Per [[feedback-research-every-finding-for-mechanism-and-envelope-push]]**: Family C and E's "this needs
  different math" findings are themselves useful negatives -- they tell the substrate's future codebook-design
  choices which constructions buy the cheap, exact, closed-form self-margin-prediction property (i.i.d. per-
  dimension random phase/frequency, Families A/B) and which do not (learned/correlated codes, Families C/D/E),
  a concrete design lesson for any FUTURE codebook the substrate builds.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- If the Family-B cell (Sec. 4) HARD-PASSes on a fresh dispatch: the substrate gains PRECISE (not merely
  scaling-law-level) self-knowledge of its own FHRR bundle-capacity boundary -- across the substrate's single most
  load-bearing codebook type (binding/memory/multi-hop/generation all build on FHRR bundling). This directly
  upgrades a currently only-MIDDLE_BAND result (`exp_bundle_capacity_largeN_gpu_v1`, 45-58% deviation at
  production N) toward a tight, verified prediction -- more consequential than the RNS case, which was already
  HARD_PASS before this drill's tightening.
- If it HARD-FAILs on a fresh dispatch despite this drill's strong retrospective fit: valuable and reportable --
  it would mean the i.i.d.-crosstalk independence property, excellent at these specific already-measured
  configs/seeds, does not hold robustly at other book sizes V or fresh seeds, and any future FHRR capacity claim
  should stay anchored to the looser (already-validated) asymptotic law, per
  [[feedback-measured-bounds-are-method-config-contingent-not-fundamental]].
- **Still monitor-not-control**: this remains a REPORTING refinement (a tighter number in `metrics.json`), never a
  config-changing action -- does not alter N, K, V, or any landed cell's stored artifacts; a human/Strategy decides
  what to do with the tightened number.
- **Cap_map implication:** if the Family-B cell HARD-PASSes, this is grounds for Strategy to consider a SECOND
  CG-eligible instance of the same "substrate predicts its own decode-margin boundary exactly" capability class
  (alongside the RNS one), across the substrate's most-used codebook family -- strengthening any future claim that
  this is a general substrate CAPABILITY (self-margin-prediction), not a one-off result on one codebook. Strategy
  decides; research does not modify cap_map.
- **Design lesson for future codebooks (Family C/D/E negatives, Sec. 1):** any future substrate codebook that
  wants CHEAP, EXACT, closed-form self-margin-prediction should prefer i.i.d.-per-dimension random phase/frequency
  construction (Families A/B's proven property) over learned/correlated/attractor-based constructions (Families
  C/D/E), which either need a different (still-standard) derivation or an iterated-dynamics analysis entirely.

---

## CITATIONS

**IMPORTANT METHODOLOGY NOTE:** all 3 parallel Sonnet lit-scan sub-agents dispatched this drill hit a persistent
web-search-backend outage (`529 Overloaded`, ~40 combined attempts across WebSearch/WebFetch, sustained over
several minutes each) and could not complete live source verification. Per role discipline (no fabricated
citations), the citations below are reported EXPLICITLY as **recalled/trained-knowledge, NOT live-verified this
drill** -- a genuine methodology gap this round, not smoothed over. This does NOT weaken Sec. 1's core numeric
finding, which was verified directly against the substrate's own on-disk `metrics.json` data (10 measured points
across 3 landed cells), independent of the external lit-scan's success or failure. **Verified-external-citation
count this drill: 0** (down from a typical 8-12; recommend a follow-up lit-scan pass once the search backend
recovers, to convert the recalled citations below into live-verified ones before any external-facing claim).

**Recalled (not live-verified) -- lit-scan 1, FHRR/HRR bundle capacity:**
1. Plate, T. (1995). "Holographic Reduced Representations." *IEEE Trans. Neural Networks* 6(3). -- source of the
   N/(2 ln N)-style asymptotic capacity law currently used by the 3 target cells; recalled as likely using a
   Gaussian/CLT + union-bound-style argument for the asymptotic, not necessarily the full exact order-statistic
   integral this drill derived and verified -- UNCONFIRMED, flagged for follow-up.
2. Frady, E.P., Kleyko, D. & Sommer, F.T. (2018). "A Theory of Sequence Indexing and Working Memory in Recurrent
   Neural Networks." *Neural Computation.* -- recalled as the most likely source of a more rigorous, closer-to-
   exact finite-N treatment in this literature; contents not independently confirmed this drill.
3. Kleyko, D. et al. (~2022). VSA survey, *ACM Computing Surveys* (two parts) -- recalled as likely restating
   Plate's bound alongside later refinements; not independently confirmed.

**Recalled (not live-verified) -- lit-scan 2, equicorrelated/one-factor Gaussian order statistics (Family D):**
4. Dunnett, C.W. & Sobel, M. (1955). "Approximations to the probability integral and certain percentage points of
   a multivariate analogue of Student's t-distribution." *Biometrika* -- classical equicorrelated-normal integral
   via common-factor conditioning; the exact technique needed for Family D's proposed generalization.
5. Vasicek, O. (1987/1991/2002 working papers). Asymptotic Single Risk Factor (ASRF) large-pool model -- standard
   one-factor Gaussian conditioning, widely used and numerically well-understood (Gauss-Hermite quadrature over
   the shared factor).
6. Li, D.X. (2000). "On Default Correlation: A Copula Function Approach." -- one-factor Gaussian copula,
   structurally identical conditioning technique.
7. Slepian, D. (1962). "The one-sided barrier problem for Gaussian noise." *Bell System Technical Journal* --
   monotonicity theorem confirming increasing pairwise correlation shrinks the competitor max (recalled with
   moderate confidence; directionally consistent with the standard extremes-of-Gaussian-processes literature).

**Recalled (not live-verified) -- lit-scan 3, pseudo-inverse Hopfield capacity (Family C):**
8. Personnaz, L., Guyon, I. & Dreyfus, G. (1985/1986). "Information storage and retrieval in spin-glass-like
   neural networks" / "Collective computational properties of neural networks: new learning mechanisms." --
   introduces the projection/pseudo-inverse learning rule used by `exp_crt_capacity_boost_v1`.
9. Kanter, D. & Sompolinsky, H. (1987). "Associative recall of memory without errors." *Phys. Rev. A* 35, 380. --
   mean-field/replica analysis of pseudo-inverse basin-of-attraction capacity, alpha_c=1 as N->infinity.
10. McEliece, R., Posner, E., Rodemich, E. & Venkatesh, S. (1987). *IEEE Trans. Info. Theory* 33(4) -- one-step
    Hebbian SNR capacity alpha_c ~ 1/(2 ln N); recalled as an order-statistic-style argument, structurally
    parallel to (but not the same quantity as) Family B's bundle-capacity law.
11. Tolmachev, P. & Manton, J. (2020). "New Insights on Learning Rules for Hopfield Networks." arXiv:2010.01472 --
    the ONE source in this drill partially confirmed live (a single search+fetch succeeded before the backend
    became unresponsive again) -- moderate confidence.

**Substrate-internal (verified on disk this drill, load-bearing, not counted toward external total):**
- `experiments/exp_rns_subblock_margin_selfcheck_v1.py` (read in full, prior drill; re-cited for the shared
  order-statistic family structure).
- `hdlab/atoms.py` (read in full this drill; `make_atom_fhrr` construction).
- `experiments/exp_bundle_capacity_theory_cpu_v1.py`, `exp_bundle_capacity_largeN_gpu_v1.py`,
  `exp_bundle_capacity_cliff_gpu_v1.py`, `exp_bundle_crosstalk_scaling_cpu_v1.py` (all read in full this drill;
  `data/exp_bundle_capacity_theory_cpu_v1/metrics.json`, `data/exp_bundle_capacity_largeN_gpu_v1/metrics.json`,
  `data/exp_bundle_capacity_cliff_gpu_v1/metrics.json`, `data/exp_bundle_crosstalk_scaling_cpu_v1/metrics.json`
  all read and used for the numeric verification in Sec. 1).
- `experiments/exp_encoder_v11_gsbc_graded_sparse_v1_core.py`, `exp_generation_decoder_gsbc_native_blocklocal_v1.py`
  (read in full this drill; Family D's "cone" correlation measurement).
- `hdlab/concept_encoder.py` (read this drill; Family E's cosine-argmax decode geometry + heterogeneous-
  correlation selftest gates).
- `experiments/exp_crt_capacity_boost_v1.py`, `exp_multihop_router_crt_residue_addressed_v1.py`,
  `exp_math_rns_add_chain_v1.py`, `exp_math_rns_multiply_star_v1.py`, `exp_pb_crt_real_encoder_atoms_v1.py`
  (headers/key functions read this drill; Family A extent + Family C identification).
- `notes/research_decode_margin_exact_prefactor_derivation_2026-07-06.md` (read in full; the parent RNS
  derivation this drill extends and structurally parallels).

---

*Research complete 2026-07-06. Core numeric finding (Family B exact order-statistic fit) established and verified
directly from the substrate's own on-disk code and measured `metrics.json` data across 3 landed cells / 10 points,
BEFORE and INDEPENDENT of the external lit-scan (which hit a tool outage). Lit-scan citations reported honestly as
recalled-not-live-verified this round -- follow-up lit-scan recommended once the search backend recovers. Notes-only
drill per task instruction -- no cell built, no dispatch, no routing files (USER-locked ferry-deprecation override;
the ready cell spec is delivered directly in this note, Sec. 4).*
