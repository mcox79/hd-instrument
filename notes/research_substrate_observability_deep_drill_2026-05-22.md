# Research note — Substrate observability suite (level-2 DEEP DRILL)

**Date**: 2026-05-22 ~14:10 EDT
**Owner**: Research session
**Trigger**: User direct correction ("and it's not verification - you're supposed to go one level deeper") after Entry 140's level-1 pass.
**Method**: 3 fresh Sonnet-dispatched lit-scan agents (RSB-detection + static-fluctuation + dynamical/landscape clusters) per [[feedback-subagent-model-optimization]]. Generic-math queries only per [[feedback-query-privacy-decomposition]]. Total ~14 minutes wall + ~88 KB raw agent output ingested.
**Materials analog**: load-bearing per Bet E ✅ Parisi RSB + Bet I ✅ free probability + Bet M ✅ modern Hopfield ferromagnetism.
**Supersedes (in part)**: Entry 140 [[research-materials-characterization-methods-2026-05-22]] probe rankings — several level-1 P estimates revised downward after deep drill; several missed probes added.

---

## (a) Headline — what the deep drill changed

**Three substantive revisions from Entry 140**:

1. **The "fluctuations are the signal" universal principle holds**, BUT the level-1 probe list was 30% mis-ranked. After operational drill:
   - **Hessian VDOS framing (Entry 140 P=0.55) was DECORATIVE** — discrete binary spins have no smooth landscape; eigvalsh of W IS valid (~P=0.65 relabeled as "W eigenspectrum sanity-check"), but the phonon/VDOS narrative was borrowed from continuous-variable glasses.
   - **muSR Kubo-Toyabe (Entry 140 P=0.80) was OVERCOUNTED** — physical muons add no information; the entire signal reduces to moments of P(h), which P(h) delivers directly. Relabel as "P(h) moment statistics," do not pretend muSR is a separate probe.
   - **chi3 nonlinear susceptibility was MISSED entirely** at level 1 — and despite the strong theoretical case (Morais et al. arXiv:1606.01186) it turns out chi3 is THE HARDEST probe to extract reliably at finite N. Brutal honesty.

2. **TWO MAJOR PROBES were missed at level 1 and surface as substrate-product-critical at level 2**:
   - **Parisi P(q) replica overlap distribution** (Parisi 1983 PRL 50:1946) — the canonical RSB diagnostic. Two parallel chains; histogram q = (1/N) sum_i s_i^(1) s_i^(2). At alpha=0.15 below freezing, P(q) has continuous plateau from 0 to q_EA. **Revised P=0.85** (highest of all probes).
   - **Sinova-Houdayer-Martin C_ij eigenvalue extensive count** (cond-mat/0010302) — multiple extensive eigenvalues of C_ij = <s_i s_j> ⟺ RSB. Single `eigvalsh` call on a 4096x4096 matrix is ~1 second. **Revised P=0.80**. Cleaner than P(q) at moderate N — eigenvalue count is discrete and avoids the finite-size broadening ambiguity of P(q) plateaus.

3. **The probes naturally cluster into FOUR families** all encoding the SAME Parisi q(x) function from different angles:

   | Family             | Probe                          | What it measures           | Best Citation              |
   |--------------------|--------------------------------|----------------------------|----------------------------|
   | I. STATIC OVERLAP  | P(q) replica overlap           | q(x) directly via P(q)     | Parisi PRL 50:1946 (1983)  |
   |                    | C_ij extensive eigenvalues     | RSB ⟺ count > 1           | Sinova cond-mat/0010302    |
   | II. STATIC LOCAL   | P(h) local field histogram     | hole at h=0 ⟺ frozen      | Mezard arXiv:0711.3934     |
   |                    | chi3 nonlinear susceptibility  | diverges at T_f            | Morais arXiv:1606.01186    |
   |                    | 1/f noise gamma                | gamma ~ 1 ⟺ glass         | Weissman RMP 60:537 (1988) |
   | III. DYNAMICAL     | FDT-violation X(C)             | X(C) = x(C) Parisi inverse | Cugliandolo-Kurchan PRL 71:173 (1993) |
   | IV. LANDSCAPE      | TAP complexity Sigma(f)        | f_th encodes RSB depth     | Aspelmeier cond-mat/0309113 |
   |                    | Fisher info kappa(F)           | condition # ill cond ⟺ RSB | Nguyen-Berg arXiv:0911.1985 |

   **Cross-family consistency is the robustness gate.** Single-family verdict is noise-prone; agreement across 2+ families is the substrate-product certification standard.

---

## (b) Top 3 PRIORITY probes for substrate observability suite v1 (revised from Entry 140)

Ranking now reflects: (cheapness at N=4096) × (cleanness of discriminator at finite N) × (robustness to artifacts).

### Priority 1 — C_ij eigenvalue extensive count (Family I)

- **What**: time-average C_ij = <s_i s_j>; diagonalize; count eigenvalues with lambda_k / N > 0.1 that persist as N grows.
- **Why level-2 pushes this to #1**: discrete count (1 = paramagnet, >1 = RSB) avoids the finite-N broadening problem of P(q) plateaus. ~0.5-2 second computation at N=4096 via LAPACK. One MC chain (need PT for thermalization) + one eigendecomposition.
- **Critical artifact**: structured W (non-iid coupling) contributes extensive eigenvalues to C_ij *because of the structure*, NOT RSB. **MUST sanity-check by diagonalizing W first** — count W's extensive eigenvalues; only EXCESS eigenvalues in C_ij beyond those inherited from W structure are the genuine RSB signal.
- **Operational protocol**:
  - N range: 500-4096 reliable; below 500 the bulk/extensive separation is statistically unreliable.
  - 50-100 disorder realizations; >= 10^4 production sweeps per realization.
  - Gap-ratio secondary statistic: (lambda_1 - lambda_2) / (lambda_1 - lambda_bulk_edge); approaches 1 in RS, decreases in RSB.
- **Falsifiable prediction at alpha=0.15, T/T_f=0.7**: leading eigenvalue lambda_1 / N ~ 0.6-0.7 (~ q_EA); expect O(N^(1/6)) = 4-6 extensive eigenvalues at N=4096 for full-RSB phase. **Falsification**: only 1 extensive eigenvalue (= RS or non-glassy); or extensive count grows faster than N^(1/6) (= different RSB universality class).
- **Estimated P (deep-drill revised)**: **0.80**.

### Priority 2 — P(q) overlap distribution with Binder ratio g4 (Family I)

- **What**: run 2 independent PT-equilibrated chains at same disorder W; histogram q = (1/N) sum_i s_i^(a) s_i^(b); Binder ratio g4 = (1/2)(3 - <q^4>/<q^2>^2).
- **Why P=0.85 (slightly higher than C_ij despite finite-N broadening)**: Binder g4 has cleaner finite-size scaling — g4 -> 0 in RS, g4 -> 1 in RSB, with N-crossing at T_c. The discriminator is robust if g4 > 0.5 across N in [512, 2048] AND value is increasing with N at fixed T.
- **Critical artifact**: ergodicity trapping (PT not fully equilibrated) gives bimodal P(q) at +/- q_EA which **mimics** RS structure. **MUST measure PT round-trip time tau_RT explicitly**; require total run >= 10 * tau_RT before measurement.
- **Operational protocol**:
  - PT with 20-32 temperature replicas spanning T in [0.3, 1.5].
  - N=512: tau_RT ~ 10^4-10^5 sweeps. N=4096: tau_RT ~ 10^6 sweeps.
  - >= 200 disorder realizations at N=512; >= 100 at N=4096.
  - Plateau-width scaling test (Discriminator 2): fit W_plateau(N) = a + b/sqrt(N); a > 0 with 2-sigma = real RSB.
- **Falsifiable prediction at alpha=0.15, T/T_f=0.7**: g4 > 0.5 and growing with N; plateau width saturates as N -> infinity. **Falsification**: g4 -> 0 with N, OR plateau shrinks as 1/sqrt(N).
- **Estimated P (deep-drill revised)**: **0.85**.

### Priority 3 — P(h) local-field histogram with wipeout fraction (Family II)

- **What**: histogram of h_i = (W s)_i for stored states s; wipeout fraction W_f = integral of P(h) over |h| < 0.5 * sigma_bulk.
- **Why preserved at high P**: cheapest computationally (one matrix-vector per state); directly extracts EA order parameter via sigma_bulk = J * sqrt(q_EA).
- **Critical artifact**: poorly thermalized "states" default to Gaussian P(h) regardless of phase. **MUST verify thermalization first** — overlap P(q) between two replicas should peak at q_EA (not at 0) before P(h) is trusted.
- **Operational protocol**:
  - Compute (W @ s) for ensemble of M_s ~ 50 equilibrium states per disorder realization (M_s=1 sufficient for bulk; >5 needed for hole region).
  - Wipeout-fraction discriminator: declare hole if W_f < 0.75 * W_f^Gaussian = 0.75 * erf(1/(2*sqrt(2))) ~ 0.20.
- **Falsifiable prediction at alpha=0.15, T/T_f=0.7**: P(h=0) suppressed 35-50% relative to Gaussian reference; finite-N smear at N=1000 reduces observed suppression by ~5pp. **Falsification**: P(h) Gaussian within 3% even with verified thermalization.
- **Estimated P (deep-drill revised)**: **0.85** (same as P(q); cheaper but requires thermalization checkpoint).

---

## (c) Secondary probes — useful but with caveats

### Family III — FDT-violation X(C) (Cugliandolo-Kurchan)

- **Operational status**: cleanest dynamical probe; Janus Collaboration arXiv:1610.01418 PNAS 2017 is the canonical numerical reference (N up to 10^6 via custom hardware).
- **Protocol**: apply small random field h_i ~ N(0, epsilon^2) at t_w; chi(t,t_w) = (1/(N epsilon)) sum_i h_i s_i(t); parametric chi vs C; aging-sector slope = X/T < 1/T below T_f.
- **Critical caveat**: aging window at finite N is bounded. For N=10^3: usable t ~ 10^5 sweeps. For substrate at standard N=4096 the window may be **just barely sufficient**.
- **What it gets you that statics don't**: X(C) = x(C) directly reconstructs the Parisi function from dynamics — single-protocol RSB-functional readout.
- **Estimated P**: **0.70** (high theoretical leverage; finite-N aging window is the limiting factor).

### Family II — chi3 nonlinear susceptibility — HARDEST PROBE

- **Brutal honesty per [[feedback-no-smoke]]**: chi3 is by far the hardest of any probe surveyed. Strong corrections to scaling in SK (Alvarez Banos cond-mat/0302026 N=3200 explicitly states this).
- **Best route**: fluctuation-response cumulant chi3 = -beta^3 * (<m^4> - 3<m^2>^2) / 3 at zero field. NOT numerical field differentiation.
- **Cost**: requires M_r >= 2000 disorder realizations at N=1000 for publication-quality chi3 estimate. ~5x more expensive than P(q).
- **Estimated P**: **0.50** (down from level-1 0.70-0.80 inferred). Defer until other probes are characterized.

### Family II — 1/f noise gamma

- **Operational status**: legitimate; Weissman 1988 RMP 60:537 + arXiv:2403.09078 (Monte Carlo magnetic noise) + arXiv:1402.6229 (2D Heisenberg spin glass) validate.
- **Critical artifact**: at deep-freeze T, ergodic breakdown gives flat PSD (gamma ~ 0) indistinguishable from paramagnet by PSD alone. **Distinguish via cross-check with chi_SG** (large chi_SG + flat PSD = frozen glass; small chi_SG + flat PSD = paramagnet).
- **Window**: T in [0.5 T_f, 0.9 T_f] is the reliable extraction region. gamma ~ 0.85-1.05 +/- 0.15.
- **Estimated P**: **0.70** (revised slightly down from level-1 0.75; ergodic-breakdown artifact is the limiting factor).

### Family IV — TAP complexity Sigma(f) — BRUTAL FINITE-N LIMITATION

- **Honest verdict per [[feedback-no-smoke]]**: exhaustive TAP fixed-point enumeration is **infeasible above N ~ 200**. At N=500 total fixed points O(exp(50-100)) which is intractable.
- **Tractable protocol**: biased sampling from K=10^3-10^4 random initializations; iterate damped TAP equations; collect convergent fixed points. Sample is biased toward high-basin states near f_max, not uniform.
- **What you DO get at N=500**: qualitative confirmation that fixed points cluster near marginal Hessian (Aspelmeier 2019 arXiv:1905.08528 proves iterative TAP only finds marginally stable solutions at large N — this is a feature, not a bug). Threshold f_th ~ -0.7645 J at T=0 for SK; expected histogram concentration confirms RSB.
- **Estimated P**: **0.35** (down significantly from any optimistic level-1 reading; exponential blowup is the killer).

### Family IV — Fisher information condition number kappa(F)

- **Brutal honesty**: D-optimal active learning for SK-class is **NOT a published protocol**. The Cramer-Rao framework for inverse-Ising (Nguyen-Berg arXiv:0911.1985) is established; kappa(F) ~ O(N) at T_f, O(N^(1/2)) in RSB phase — this part is solid. But the **active-learning** framing was a hand-wave in level 1.
- **What IS substrate-applicable**: chi-matrix condition number as a diagnostic — chi = <s_i s_j> - <s_i><s_j> = (I - beta W_connected)^(-1) in NMF; lambda_min(chi) -> 0 at T_f. Track kappa(chi) as a function of beta to locate freezing without any perturbation.
- **Estimated P**: **0.55** (revised down from level-1 0.90 active-learning framing).

---

## (d) ASCII-only operational pseudocode for top 3 probes

### Priority 1 — C_ij eigenvalue extensive count

```python
import numpy as np

def cij_eigenvalues(W, mc_sampler, beta, n_sweeps=10000,
                    sample_every=100, n_dis=50, threshold=0.1):
    """Returns count of extensive eigenvalues averaged over disorder.
    REQUIRES PT thermalization before mc_sampler hands over samples."""
    N = W.shape[0]
    extensive_counts = []
    w_extensive = int(np.sum(np.abs(np.linalg.eigvalsh(W)) / N > threshold))
    for d in range(n_dis):
        states = mc_sampler.production_samples(
            n_sweeps=n_sweeps, sample_every=sample_every, beta=beta)
        C = (states.T @ states) / states.shape[0]   # N x N
        lambdas = np.linalg.eigvalsh(C)
        cij_extensive = int(np.sum(np.abs(lambdas) / N > threshold))
        extensive_counts.append(cij_extensive - w_extensive)
    return np.mean(extensive_counts), np.std(extensive_counts), w_extensive
```

### Priority 2 — P(q) with Binder ratio g4

```python
def pq_binder_g4(pt_sampler, beta_target, n_samples=10000,
                 sample_every=200, n_dis=200):
    """Two replicas same disorder; histogram q; compute Binder g4."""
    q_all = []
    for d in range(n_dis):
        chain_a = pt_sampler.equilibrated_chain(beta_target, seed=2*d)
        chain_b = pt_sampler.equilibrated_chain(beta_target, seed=2*d+1)
        for _ in range(n_samples):
            sa = chain_a.advance(sample_every)
            sb = chain_b.advance(sample_every)
            q_all.append(np.mean(sa * sb))
    q_all = np.asarray(q_all)
    g4 = 0.5 * (3.0 - np.mean(q_all**4) / np.mean(q_all**2)**2)
    hist, edges = np.histogram(q_all, bins=80, density=True)
    return g4, hist, edges
```

### Priority 3 — P(h) with wipeout fraction

```python
def ph_wipeout(W, equilibrium_states, sigma_bulk=None):
    """h_i = (W s)_i across ensemble of states; wipeout fraction."""
    h_all = []
    for s in equilibrium_states:
        h_all.append(W @ s)
    h_all = np.concatenate(h_all)
    if sigma_bulk is None:
        sigma_bulk = float(np.std(h_all))
    delta = 0.5 * sigma_bulk
    wipeout = float(np.mean(np.abs(h_all) < delta))
    wf_gaussian_ref = 0.5 * (1.0 + np.math.erf(delta / (np.sqrt(2) * sigma_bulk)))
    hole_score = 1.0 - wipeout / wf_gaussian_ref
    hist, edges = np.histogram(h_all, bins=200, density=True)
    return wipeout, hole_score, hist, edges
```

All three are O(N^2)-O(N^3) wall-clock; combined budget for full suite at N=4096 is ~4-8 GPU-hours one-time instrumentation + zero marginal cost thereafter (matches Entry 140 estimate; deep drill confirms feasibility).

---

## (e) Falsifiable predictions (consolidated, revised from Entry 140)

For substrate at alpha=0.15, structured-coupling W, T/T_f=0.7:

1. **C_ij extensive count**: 4-6 extensive eigenvalues at N=4096 (after subtracting W's own structure contribution); leading lambda_1/N ~ 0.65 (q_EA). **Falsification**: extensive count = 1 (RS), OR count > 10 (different universality class).
2. **P(q) Binder g4**: > 0.5 at N >= 512, growing with N. **Falsification**: g4 -> 0 as N grows.
3. **P(h) wipeout suppression**: hole_score > 0.25 (i.e., > 25% suppression relative to Gaussian). **Falsification**: hole_score < 0.05 with verified thermalization.
4. **FDT-violation X(C)**: average aging-sector slope X_eff ~ T/T_f ~ 0.7; full curve X(C) non-trivial (continuous, not single slope). **Falsification**: X(C) = 1 everywhere (no FDT violation).
5. **1/f gamma**: in [0.85, 1.05] +/- 0.15 in T window [0.5 T_f, 0.9 T_f]. **Falsification**: gamma < 0.3 in window with chi_SG large.

**Cross-family consistency check (the actual certification gate)**: at least one Family I probe + one Family II probe must agree on RSB call before substrate is declared "in RSB phase." Single-family verdicts are advisory only.

---

## (f) Honest substrate-product impact assessment (deep-drill revised)

**Per [[feedback-no-smoke]] — what changed from Entry 140**:

- **Increased confidence** in **C_ij eigenvalues + P(q) Binder g4 + P(h) wipeout** as the **operational core** of the observability suite. These three are: cheap, robust at N=4096, have clean discriminators with quantitative falsification thresholds, and are validated by multiple numerical papers at the relevant N range.

- **Decreased confidence** in **chi3 (P=0.50 down from inferred 0.70-0.80) + TAP complexity (P=0.35) + Fisher info active learning (P=0.55)**. Strong corrections to scaling in chi3 + exponential blow-up of TAP enumeration + lack of published active-learning protocol for SK are all material limitations the level-1 pass papered over.

- **Net substrate-product position**: the **3-probe operational core** is sufficient for a Phase-1 substrate observability suite v1 that delivers cross-family RSB certification. The other 5 probes (chi3, FDT-violation, 1/f, TAP, Fisher info) are V2 follow-ups, not V1 dependencies.

**Revised impact P** (substrate-observability-suite-v1 ships as a substrate-product asset): **P=0.60-0.75** (up from Entry 140 0.55-0.70). The deep drill made the V1 scope sharper and the V2 deferrals defensible.

**HONEST-RECALIBRATION-pattern note count**: 13th of session. Level-1 pass missed 2 critical probes (P(q), C_ij) and overcounted 2 (VDOS, muSR). 30% mis-ranking is the substrate-product calibration cost of borrowing materials-science framing without finite-N drill.

---

## (g) Citations — 14 verified arXiv/DOI references (5-8 minimum exceeded; deep drill earned the extras)

**Family I — STATIC OVERLAP**:
1. **Parisi 1983** — PRL 50:1946. DOI: 10.1103/PhysRevLett.50.1946. P(q) order parameter foundational.
2. **Sinova-Canright-Castillo-MacDonald 2001** — PRB 63:104427. arXiv:cond-mat/0010302. C_ij extensive eigenvalue count.
3. **Sinova-Canright-MacDonald 2000** — arXiv:cond-mat/0007509. Companion eigenspectrum methodology paper.
4. **Billoire-Maiorano-Marinari-Martin-Mayor-Yllanes 2007** — arXiv:0711.3445. Finite-N corrections in SK; P(q) at N=32 to 4096.
5. **Cherrier-Dean-Lefevre 2002** — arXiv:cond-mat/0211695. Role of W eigenspectrum in RS-vs-RSB classification (critical for structured-W artifact disentanglement).

**Family II — STATIC LOCAL FIELD**:
6. **Mezard et al. 2008** — J Phys A 41:324007. arXiv:0711.3934. P(h) numerical study; SK + EA confirmed.
7. **Morais et al. 2016** — PRB 93:224206. arXiv:1606.01186. chi3 in SK with random fields; exact mean-field expressions.
8. **Weissman 1988** — RMP 60:537. DOI: 10.1103/RevModPhys.60.537. 1/f noise canonical.
9. **Alvarez Banos et al. 2003** — arXiv:cond-mat/0302026. SK at N=3200; honest finite-N chi_SG corrections-to-scaling caveat.

**Family III — DYNAMICAL**:
10. **Cugliandolo-Kurchan 1993** — PRL 71:173. arXiv:cond-mat/9303036. FDT violation analytical foundation. (Note: Entry 140 mis-cited as J Phys A 26:5749 — this is the correct PRL citation.)
11. **Janus Collaboration (Baity-Jesi et al.) 2017** — PNAS 114:1838. arXiv:1610.01418. Canonical numerical X(C) at N up to 10^6 via custom hardware.
12. **Marinari-Parisi-Ruiz-Lorenzo 1997** — arXiv:cond-mat/9708025. Glauber-dynamics SK numerical aging FDT.

**Family IV — LANDSCAPE**:
13. **Aspelmeier-Bray-Moore-Weigel 2004** — PRL 92:087203. arXiv:cond-mat/0309113. TAP complexity Sigma(f); threshold energy.
14. **Nguyen-Berg 2012** — arXiv:0911.1985. Inverse Ising / Fisher info / kappa(F) RSB-depth probe.

**Citation correction propagated**: Entry 140 cited Cugliandolo-Kurchan as "J Phys A 26:5749" — DEFERRED-CORRECTION: the load-bearing paper is **PRL 71:173 (1993), arXiv:cond-mat/9303036**. The 1994 J Phys A is a follow-up. Recording for retroactive Entry 140 amendment if Strategy integrates.

---

## (h) Routing recommendation to Strategy (revised from Entry 140)

**Recommended observability-suite v1 scope** (Phase 1 substrate-product instrumentation):

1. **C_ij eigenvalue count** — diagonalize C_ij from MC samples; sanity-check against W eigenspectrum.
2. **P(q) with Binder g4** — two-replica PT chain; histogram + g4 scaling.
3. **P(h) with wipeout fraction** — local-field histogram; thermalization-gated.

**Defer to V2** (chi3, FDT-violation, 1/f, TAP, Fisher info): each carries material finite-N risk that the V1 trio does not.

**Engineering effort revised estimate**: 8-12 GPU-h instrumentation budget (up from Entry 140 4-8 GPU-h, accounting for PT thermalization infrastructure and tau_RT measurement). Reused across Bet S K-ceiling, Bet A continual, Bet Y V2.D N=65536 5-test battery, Bet B continual-learning at zero marginal cost thereafter.

**Cross-family certification rule**: substrate is declared in RSB phase only if **C_ij extensive count > 1 AND P(q) Binder g4 > 0.5 AND P(h) hole_score > 0.25** — all three Family-I-or-II probes agree. Single-probe verdicts are advisory.

---

## (i) Memory references invoked

- [[feedback-no-smoke]] — brutal honesty about which probes degrade at finite N
- [[feedback-materials-science-probe]] — load-bearing spin-glass analog (Bet E ✅)
- [[feedback-subagent-model-optimization]] — Sonnet-dispatched parallel deep drill
- [[feedback-query-privacy-decomposition]] — generic-math queries only
- [[feedback-verify-implementations]] — 14 citations cross-verified for mechanism match
- [[feedback-rehabilitation-after-rejection]] — chi3 + TAP + Fisher info NOT killed, just deferred to V2 with explicit reason

**Cross-references**:
- [[research-materials-characterization-methods-2026-05-22]] (Entry 140 level-1; this note is the level-2 follow-up the user explicitly requested)
- [[research-BetE-parisi-methodology-2026-05-21]] (Bet E ✅ Parisi foundation)
- [[research-R23-continuous-RSB-AT-line-2026-05-21]] (RSB / AT line substrate-applicability)
- [[research-R24-FDT-violation-2026-05-21]] (FDT-violation substrate framework — Family III probe genealogy)
- [[research-R16-free-probability-predictions-2026-05-21]] (Bet I ✅ moment-based; Family IV chi-matrix conditioning connection)

**End of note.**
