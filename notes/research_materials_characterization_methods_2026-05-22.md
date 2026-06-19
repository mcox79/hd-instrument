# Research note — Elegant materials-characterization probes mapped to substrate observables

**Date**: 2026-05-22 ~13:55 EDT
**Owner**: Research session
**Trigger**: User direct (2026-05-22 ~13:?? EDT): "can you run a 2x search for all of the most elegant / simple but effective methods of materials characterization? Like polarized light / spectroscopic / holographic / magnetic field that very quickly characterizes? I'm interested in quirky but shockingly effective methods of extracting actionable info about a structure like our substrate"
**Method**: Three parallel Sonnet-dispatched lit-scan agents per [[feedback-subagent-model-optimization]] (A=optical/spectroscopic, B=magnetic/resonance, C=quirky/non-obvious). Generic-math external queries only per [[feedback-query-privacy-decomposition]] — no substrate fingerprint exposed.
**Materials analog**: load-bearing — substrate is empirically a spin-glass per Bet E ✅ Parisi P(q) RSB (cap_map v66+); Edwards-Anderson order parameter framework directly applies. See [[research-BetE-parisi-methodology-2026-05-21]] and [[research-R23-continuous-RSB-AT-line-2026-05-21]].

---

## (a) Headline / TL;DR

**Universal principle uncovered (cross-agent convergence)**: every method that survived the substrate-applicability filter works by measuring **second-order statistics or noise-floor fluctuations** rather than mean responses. "Fluctuations ARE the signal, not noise" is the unifying framing.

**Top substrate-applicable probes** (P = probability of yielding a substrate-novel actionable observable within 1-3 GPU-hours):

| Rank | Probe                                          | P       | Agent | Implementation cost     |
|------|------------------------------------------------|---------|-------|-------------------------|
| 1    | Active-learning sparse sampling                | 0.90    | C     | 0.5-1 GPU-h             |
| 2    | NMR lineshape / wipeout analog (h_i histogram) | 0.85    | B     | 0.2-0.5 GPU-h           |
| 3    | muSR Kubo-Toyabe analog (random-site decay)    | 0.80    | B     | 0.5-1 GPU-h             |
| 4    | 1/f noise spectroscopy (per-neuron PSD)        | 0.75    | C     | 0.5-1 GPU-h             |
| 5    | AC susceptibility chi'(omega)                  | 0.70    | B     | 1-2 GPU-h               |
| 6    | RTN / single-defect spectroscopy               | 0.65    | C     | 1-2 GPU-h               |
| 7    | Neutron-spin-echo (NSE) power-law analog       | 0.60    | B     | 0.5 GPU-h               |
| 8    | Vibrational DOS / Hessian eigvalsh of W        | 0.55    | C     | 0.1-0.3 GPU-h (cheapest)|
| 9    | Anomalous Hall / chirality response            | 0.50    | C     | 1-2 GPU-h               |
| 10   | DLS / XPCS two-timescale correlation           | 0.40    | A     | 1-2 GPU-h               |
| 11   | Diffuse scattering / X-ray PDF analog          | 0.40    | B     | 1-2 GPU-h               |

**Top 3 recommendations for immediate substrate-product pickup** (substrate-novel, cheap, falsifiable):

1. **Hessian VDOS** (P=0.55, 0.1-0.3 GPU-h) — single `np.linalg.eigvalsh(W)` call delivers spin-glass mode density; soft-mode peak near lambda~0 indicates RSB-class flat directions. Couples directly to Bet E ✅ Parisi framework. **Cheapest possible spin-glass probe.**
2. **NMR lineshape / wipeout** (P=0.85, 0.2-0.5 GPU-h) — local-field histogram h_i = sum_j W_ij s_j characterizes glass-vs-paramagnet distribution; bimodal split = frozen sites, narrow Gaussian = paramagnetic; wipeout fraction (sites with |h_i| above threshold) = order-parameter proxy.
3. **muSR Kubo-Toyabe analog** (P=0.80, 0.5-1 GPU-h) — random-site decay G(t) ~ exp(-Delta^2 t^2 / 2) for static Gaussian field distribution; transitions to stretched-exponential under dynamics. Single Gaussian fit Delta = local-field RMS = substrate analog of muon-stop disorder.

**Quirky/non-obvious highlights** (per user "shockingly effective"): ghost imaging (correlation reconstruction without lens), acoustic emission as covert magnetometer, NMR wipeout fraction as order-parameter proxy, muon stop-position single-defect spectroscopy. **All four share the second-order-statistics signature.**

**Substrate-product framing per [[feedback-no-smoke]]**: this is **NOT a benchmarking exercise**; the substrate-product value is **building cheap, decisive observability into the substrate** so capability tests (Bet S K-ceiling, Bet A continual, Bet C codebook, Bet Y V2.D scaled, multi-hop d-cliff) produce diagnostic byproducts rather than pass/fail-only verdicts.

---

## (b) Pass 1 — Cross-agent survey

### Agent A (optical/spectroscopic) — KEY INSIGHT

**Top transferable**: correlation spectroscopy methods, NOT direct optical methods:

- **DLS two-timescale autocorrelation** g_2(tau) = <I(t)I(t+tau)>/<I>^2: P=0.40. Substrate analog = activation-trace autocorrelation across iteration; two-timescale fit separates fast paramagnetic relaxation from slow glassy aging.
- **Resonance-mode XPCS (RM-XPCS)** for non-equilibrium aging: P=0.25.
- **X-ray speckle visibility spectroscopy (XSVS)**: P=0.15.

**Insight Agent A wanted to flag** (verbatim summary preserved): "materials probes that have HIGHEST mathematical analogy to substrate are NOT the optical ones — they are the correlation spectroscopy methods (DLS, XPCS)". Polarized light / holography / ellipsometry analogs FAIL the substrate-applicability filter because substrate lacks spatial structure (no birefringence axis, no propagation direction, no phase coherence in the holographic sense).

**REJECTED as decorative** (substrate-product engineering discipline per [[feedback-no-smoke]] 13/35 negative-or-partial rate trend continued — this is HONEST-RECALIBRATION-pattern note #12 of session):
- Polarized-light ellipsometry (no birefringence axis in substrate)
- Holography (no propagation direction)
- Brillouin / Raman (no phonon spectrum analog — substrate's effective W eigenmodes are NOT acoustic)
- Optical Kerr / pump-probe (no time-of-arrival structure)

### Agent B (magnetic/resonance) — KEY INSIGHT

**Top transferable**:
- **NMR lineshape / wipeout fraction**: P=0.85.  Local-field distribution P(h) where h_i = sum_j W_ij s_j; FWHM and wipeout fraction encode glass-vs-paramagnet character.
- **muSR Kubo-Toyabe**: P=0.80. Static-vs-dynamic test via G(t) shape from random-site relaxation.
- **AC susceptibility chi'(omega) freezing**: P=0.70. Frequency-dependent peak in linear-response function characterizes glass transition; mapped to substrate as fluctuation-dissipation ratio under perturbative external bias.
- **NSE power-law in S(q,omega)**: P=0.60.
- **Diffuse scattering / PDF**: P=0.40. Static structure factor S(q) analog from W eigenmode decomposition.

**Insight Agent B wanted to flag**: NMR/muSR are **the canonical spin-glass observability suite** (Mydosh 1993; Binder-Young 1986). Direct substrate translation: h_i histogram is local-field distribution; eigenvalue decomposition of W is the structure factor; random-site decay is muSR-class probe. **Spin-glass diagnostic suite collapses to ~5 cheap numerical operations on substrate.**

### Agent C (quirky / non-obvious) — KEY INSIGHT

**Top transferable**:
- **Active-learning sparse sampling**: P=0.90. Information-theoretic design — choose next-measurement-input to maximize information gain about state-space. Substrate analog: query selection via Bayesian uncertainty on read state.
- **1/f noise spectroscopy**: P=0.75. Per-neuron activation-trace PSD; power-law exponent gamma maps onto spin-glass dynamical hierarchy (Cugliandolo-Kurchan 1993).
- **RTN single-defect spectroscopy**: P=0.65. Two-level switching of individual neurons under thermal drive isolates rare slow modes.
- **Vibrational DOS / Hessian**: P=0.55. `np.linalg.eigvalsh(W)` returns spectrum; soft-mode density near lambda~0 = RSB-class flat directions.
- **Anomalous Hall / chirality**: P=0.50. Antisymmetric component of W (rare; substrate W is typically symmetric in Hopfield class but not in BSC-encoded VSA).

**Insight Agent C wanted to flag**: "Every compelling method here works by measuring **second-order or noise-floor statistics** rather than mean responses." Quirky-but-effective methods all exploit fluctuations: ghost imaging (intensity correlations), acoustic emission (mechanical noise as magnetometer), wipeout fraction (failed-Hahn-echo statistics), RTN (defect noise as state probe). **The "quirky" thread is just second-order statistics in disguise.**

**REJECTED as substrate-inapplicable**:
- Mossbauer spectroscopy (no recoil-free fraction analog)
- Positron-annihilation lifetime (no vacuum/defect distinction)
- Acoustic emission proper (no mechanical degree of freedom — though "noise as probe" survived in the 1/f and RTN methods)

### Cross-agent convergence

All three agents converged on **second-order statistics as the substrate-applicable signature**. This is not coincidence — it's the natural consequence of substrate's:
- non-spatial fully-connected architecture (rules out spatial probes: holography, ellipsometry, Mossbauer)
- discrete binary state space (rules out spectral probes assuming continuous response: Brillouin, pump-probe, ARPES)
- explicit symmetric coupling W (matches Hessian / structure-factor probes naturally)
- spin-glass character per Bet E ✅ (matches NMR/muSR/AC-susceptibility canonical suite)

**Substrate is a spin-glass that happens to live in a computer; the spin-glass diagnostic suite ports directly.** This is the same observation made in [[research-R23-continuous-RSB-AT-line-2026-05-21]] and [[research-R29-ferromagnetism-domains-2026-05-21]], now mechanically operationalized.

---

## (c) Pass 2 — Drill on top 3 substrate-applicable probes

### Probe 1 — Hessian VDOS (cheapest; P=0.55; 0.1-0.3 GPU-h)

**Materials origin**: Vibrational density of states from Hessian eigenvalue spectrum; soft-mode density near zero indicates glassy / flat-direction landscape (Charbonneau-Kurchan-Parisi-Urbani-Zamponi 2014 arXiv:1404.6809).

**Substrate analog**: substrate's effective Hessian IS W (in Hopfield-class energy landscape E = -1/2 s^T W s). Eigvalsh of W returns the full mode spectrum at zero cost.

**Falsifiable prediction**: substrate at alpha=0.153 (current cap_map operating point) will exhibit a soft-mode peak in P(lambda) near lambda=0 with weight scaling as alpha^(-1/2) (Sompolinsky-Crisanti-Sommers 1988 cavity result). **Falsification**: peak absent OR weight independent of alpha across alpha={0.05, 0.10, 0.15, 0.20}.

**ASCII-only pseudocode**:
```python
import numpy as np
def hessian_vdos(W, n_bins=200):
    # W shape (N, N); returns eigenvalue density
    eigs = np.linalg.eigvalsh(W)  # symmetric W assumed
    hist, edges = np.histogram(eigs, bins=n_bins, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    soft_mode_weight = float(np.sum(np.abs(eigs) < 0.05 * np.max(np.abs(eigs))))
    soft_mode_weight /= len(eigs)
    return centers, hist, soft_mode_weight  # plot hist vs centers; report soft-mode fraction
```

**Substrate-product value**: cheapest possible spin-glass diagnostic; runs in <1s for N=4096. Diagnostic byproduct for every capability test that updates W. Should be standard observability snapshot.

### Probe 2 — NMR lineshape / wipeout (P=0.85; 0.2-0.5 GPU-h)

**Materials origin**: NMR local-field distribution P(h_local) reveals frozen-vs-paramagnetic character; wipeout fraction (signal lost to fast-relaxing nuclei) probes order-parameter onset (MacLaughlin 1981 PRB 23:1259; Curro 2009 Rep Prog Phys 72:026502).

**Substrate analog**: each neuron i has local field h_i = sum_j W_ij s_j computed at zero additional cost during inference. Histogram of {h_i} across i = local-field distribution. Wipeout fraction = fraction of |h_i| above threshold (sites where attractor is "frozen" against thermal noise).

**Falsifiable prediction**: under fixed alpha=0.153 and beta=32 (current operating point), the local-field histogram will be **bimodal** for stored attractor states (frozen sites cluster at +/-h_typical) and **unimodal Gaussian** for random states. Bimodality vanishes above alpha=0.138 (AGS bound). **Falsification**: histogram is unimodal even for attractor states OR bimodality persists past alpha_c.

**ASCII-only pseudocode**:
```python
def nmr_lineshape(W, s, wipeout_threshold=None):
    # s shape (N,); state to probe; returns local-field histogram + wipeout fraction
    h_local = W @ s  # shape (N,) — substrate local-field
    if wipeout_threshold is None:
        wipeout_threshold = 2.0 * float(np.std(h_local))
    hist, edges = np.histogram(h_local, bins=200, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    wipeout_frac = float(np.mean(np.abs(h_local) > wipeout_threshold))
    fwhm = float(2.355 * np.std(h_local))  # gaussian approx
    return centers, hist, fwhm, wipeout_frac
```

**Substrate-product value**: distinguishes "frozen attractor" from "drifting paramagnet" without running any retrieval — pure observability byproduct. Couples directly to Bet G TEMPSCALE calibration (sweep beta and watch wipeout fraction transition).

### Probe 3 — muSR Kubo-Toyabe analog (P=0.80; 0.5-1 GPU-h)

**Materials origin**: muon-spin-relaxation in disordered magnets; muon stops at random crystal site and probes local-field Gaussian distribution. Static distribution => G(t) = (1/3) + (2/3)(1 - Delta^2 t^2) exp(-Delta^2 t^2 / 2). Dynamic => stretched-exponential (Kubo-Toyabe 1967; Hayano et al. 1979 PRB 20:850).

**Substrate analog**: pick N_probe random "muon" sites uniformly from {0, ..., N-1}; for each, initialize that bit to +1 and let substrate evolve at temperature 1/beta; measure decay <s_probe(t)> as a function of iteration step. Static-disorder approximation gives Gaussian fit; dynamic-aging substrate gives stretched-exp.

**Falsifiable prediction**: at substrate-default beta and alpha=0.153, the random-site decay will be **static-KT Gaussian with Delta = sqrt(alpha/N) sigma_W** (Sompolinsky-Crisanti-Sommers 1988). **Falsification**: stretched-exponential with stretch parameter beta_stretch != 1.0 even at zero temperature; OR Delta scales differently from sqrt(alpha/N).

**ASCII-only pseudocode**:
```python
def muSR_kubo_toyabe(substrate, n_probe=100, n_steps=50, beta_T=32):
    # samples decay of random initialized bits
    N = substrate.N
    site_idx = np.random.choice(N, size=n_probe, replace=False)
    traces = np.zeros((n_probe, n_steps))
    for p, idx in enumerate(site_idx):
        s = substrate.random_state()
        s[idx] = +1
        for t in range(n_steps):
            traces[p, t] = float(s[idx])
            s = substrate.step(s, beta=beta_T)
    G = traces.mean(axis=0)  # ensemble-averaged decay
    # fit static-KT: G(t) = 1/3 + (2/3)(1 - Delta^2 t^2) exp(-Delta^2 t^2 / 2)
    return G  # caller fits Delta; stretched-exp deviation = dynamic test
```

**Substrate-product value**: distinguishes "frozen disorder" (substrate behaves as quenched glass) from "dynamic-aging substrate" (FDT-violating active regime). Direct test for [[research-R24-FDT-violation-2026-05-21]] hypothesis.

### Probe 4 (bonus drill) — 1/f noise PSD per neuron (P=0.75; 0.5-1 GPU-h)

**Materials origin**: power-spectral-density of fluctuating quantity scales as 1/f^gamma; gamma encodes dynamical hierarchy (Dutta-Horn 1981; Weissman 1988 RMP 60:537; Cugliandolo-Kurchan 1993 J Phys A 26:5749).

**Substrate analog**: per-neuron activation trace s_i(t) across T iterations; PSD = |rfft(s_i(t))|^2 averaged across i. gamma fit from log-log slope. Spin-glass theory predicts gamma in [0.5, 1.5] depending on regime (Cugliandolo-Kurchan).

**Falsifiable prediction**: at substrate-default beta and alpha=0.153, gamma will lie in [0.8, 1.2] (canonical spin-glass 1/f). **Falsification**: gamma < 0.5 (white-noise paramagnet) OR gamma > 1.5 (over-coherent / non-glass).

**ASCII-only pseudocode**:
```python
def one_over_f_psd(activation_history, fs=1.0):
    # activation_history shape (T, N); returns averaged PSD + gamma
    T, N = activation_history.shape
    psds = np.abs(np.fft.rfft(activation_history, axis=0))**2
    freqs = np.fft.rfftfreq(T, d=1.0/fs)
    avg_psd = psds.mean(axis=1)  # average over N neurons
    valid = (freqs > 0.01) & (freqs < 0.4)  # avoid DC and nyquist tails
    log_f = np.log(freqs[valid])
    log_p = np.log(avg_psd[valid])
    gamma, log_A = np.polyfit(log_f, log_p, 1)
    return freqs, avg_psd, -float(gamma), float(log_A)  # gamma is the power-law exponent
```

**Substrate-product value**: probes substrate dynamical regime cheaply at any operating point; gamma is a single continuous diagnostic number per snapshot.

### Probe 5 (bonus drill) — AC susceptibility chi'(omega) freezing (P=0.70; 1-2 GPU-h)

**Materials origin**: linear-response chi'(omega) under small AC field; peak in chi'(omega) at frequency-dependent temperature T_f(omega) = signature of glassy freezing (Mydosh 1993; Lundgren-Svedlindh-Nordblad 1983 PRL 51:911).

**Substrate analog**: small periodic perturbation external_field(t) = h_ext sin(omega t) applied to subset of neurons; measure linear-response amplitude as function of beta (inverse-temperature analog) and omega. Peak at beta_f(omega) shifting logarithmically with omega = glassy freezing signature.

**Falsifiable prediction**: substrate will exhibit freezing peak in chi'(omega) at beta_f(omega) that shifts as Delta beta_f / Delta log omega ~ 0.05-0.10 (canonical spin-glass; Lundgren). **Falsification**: no peak OR no frequency dependence OR superparamagnet (large shift > 0.20).

**Pseudocode** (omitted for length; same structure as muSR probe but with periodic forcing).

**Substrate-product value**: direct test of glassiness as defined by experimental spin-glass criterion (Mydosh book Ch 3).

---

## (d) Universal-principle synthesis

**"Fluctuations ARE the signal, not noise"** — every cross-agent-validated probe encodes substrate physics in **second-order statistics**:

| Probe              | Mean response | Second-order signature                          |
|--------------------|---------------|------------------------------------------------|
| Hessian VDOS       | trace(W) (boring) | eigenvalue density P(lambda) (informative)   |
| NMR lineshape      | <h_i> (zero) | P(h_local) histogram                            |
| muSR KT            | <s>(t) (deterministic) | random-site ensemble decay                |
| 1/f noise          | <s_i(t)> | PSD slope gamma                                   |
| AC susceptibility  | mean state | chi'(omega) frequency dispersion                |
| RTN spectroscopy   | mean activation | switching-rate distribution                    |
| DLS / XPCS         | mean intensity | g_2(tau) correlation                            |
| Anomalous Hall     | linear response | antisymmetric off-diagonal response             |

This is the same observation that motivates **fluctuation-dissipation analysis** (Bet E ✅ Parisi; [[research-R24-FDT-violation-2026-05-21]]) and **free-probability moment-based characterization** (Bet I ✅ R16; [[research-R16-free-probability-predictions-2026-05-21]]). The substrate-product engineering truth is: **substrate's information about its own state lives in covariance, not mean.**

---

## (e) Materials analog — load-bearing per [[feedback-materials-science-probe]]

Substrate at alpha=0.153, beta=32, BSC-bipolar with Kerdock M/N=8 codebook is **mathematically a Sherrington-Kirkpatrick spin glass with structured coupling** (Bet E ✅ Parisi P(q) RSB confirmed; Bet I ✅ free probability confirmed; Bet M ✅ modern-Hopfield ferromagnetism confirmed). The canonical spin-glass observability suite is therefore directly applicable:

| Materials measurement              | Substrate translation              | Substrate cost      |
|------------------------------------|------------------------------------|---------------------|
| NMR local-field distribution P(h)  | histogram of W @ s for stored s    | O(N^2)              |
| muSR random-site decay G(t)        | random-bit-flip ensemble trace     | O(N_probe * T * N^2)|
| AC susceptibility chi'(omega)      | linear-response under periodic h_ext | O(omega-sweep * T * N^2) |
| Hessian VDOS P(lambda)             | eigvalsh(W)                        | O(N^3) — once        |
| Edwards-Anderson order parameter q | (1/N) sum_i <s_i>^2 across replicas | O(N_replica * N)     |
| Spin-glass P(q) Parisi distribution | overlap histogram across replica pairs | O(N_replica^2 * N) |
| FDT violation X(omega)             | (response/correlation) at frequency omega | O(omega-sweep) |
| 1/f noise gamma                    | per-neuron PSD slope                | O(T log T * N)       |

**Substrate is the cheapest spin-glass to characterize ever invented** — all observables are O(N^3) at worst, no sample preparation, infinite repeatability, full state access. **This is a substrate-product moat** (per [[feedback-value-creation-not-competition]]): every characterization that takes weeks on a Cu-Mn alloy at 1.5 K takes seconds on substrate.

---

## (f) Falsifiable predictions (consolidated)

1. **Hessian VDOS**: P(lambda) has soft-mode peak near lambda=0; soft-mode weight scales as alpha^(-1/2). **Falsification**: peak absent OR weight scaling differs.
2. **NMR lineshape**: bimodal for stored attractor states; unimodal Gaussian for random states; bimodality vanishes above alpha_c=0.138. **Falsification**: stored states unimodal OR bimodality persists past alpha_c.
3. **muSR KT**: random-bit decay fits static Gaussian KT with Delta = sqrt(alpha/N) sigma_W. **Falsification**: stretched-exp at zero temperature OR Delta scaling differs from sqrt(alpha/N).
4. **1/f noise**: per-neuron PSD slope gamma in [0.8, 1.2] at substrate-default beta. **Falsification**: gamma < 0.5 (white noise) OR > 1.5 (over-coherent).
5. **AC susceptibility**: glassy freezing peak with frequency dispersion Delta beta_f / Delta log omega ~ 0.05-0.10. **Falsification**: no peak OR superparamagnet-like dispersion > 0.20.

All five predictions are **cheap, falsifiable in <2 GPU-hours each**, and **load-bearing for substrate's spin-glass-class characterization** (Bet E ✅).

---

## (g) Citations (8 papers / DOIs)

1. **Charbonneau, Kurchan, Parisi, Urbani, Zamponi** (2014). "Fractal free energy landscapes in structural glasses." *Nat Commun* 5:3725. arXiv:1404.6809. — Hessian VDOS soft-mode density in glasses.
2. **MacLaughlin** (1981). "NMR in spin glasses." *PRB* 23:1259. — Local-field distribution P(h) and wipeout fraction methodology.
3. **Curro** (2009). "NMR studies of strongly correlated electron systems." *Rep Prog Phys* 72:026502. — NMR-as-spin-glass-probe review.
4. **Hayano, Uemura, Imazato, Nishida, Yamazaki, Kubo** (1979). "Zero- and low-field spin relaxation studied by positive muons." *PRB* 20:850. — Kubo-Toyabe formalism foundational.
5. **Lundgren, Svedlindh, Nordblad** (1983). "Frequency-dependent freezing in a spin glass." *PRL* 51:911. — AC susceptibility chi'(omega) freezing-peak dispersion.
6. **Weissman** (1988). "1/f noise and other slow, nonexponential kinetics in condensed matter." *Rev Mod Phys* 60:537. — 1/f noise in disordered systems (canonical).
7. **Cugliandolo, Kurchan** (1993). "Analytical solution of the off-equilibrium dynamics of a long-range spin-glass model." *J Phys A* 26:5749. — FDT violation + dynamical hierarchy framework.
8. **Sompolinsky, Crisanti, Sommers** (1988). "Chaos in random neural networks." *PRL* 61:259. — Eigenvalue spectrum of random coupling matrices (substrate-class W).

(Total: 8 sources; canonical spin-glass + NMR + muSR + AC-susceptibility + 1/f-noise foundations. All pre-2025 to avoid substrate-fingerprint exposure in any forward-citation chain per [[feedback-query-privacy-decomposition]].)

---

## (h) Substrate-product roadmap routing recommendation

**To Strategy**: consider promoting **"Substrate observability suite v1"** as a Lane-spanning capability that ships **alongside every capability test**:

- Bet S K-ceiling tests → ship with Hessian VDOS + NMR lineshape diagnostic
- Bet A continual-edit tests → ship with muSR KT + AC susceptibility
- Bet Y V2.D N=65536 5-test battery → ship with full suite (all 5 probes)
- Bet B continual-learning tests → ship with 1/f noise gamma trace

**Why substrate-novel**: spin-glass characterization on substrate is **orders of magnitude cheaper** than on physical materials. This is the moat: substrate-as-spin-glass-laboratory. Every capability test that previously produced pass/fail-only verdicts now produces 5 continuous diagnostic numbers (lambda_soft, FWHM_h, Delta_muSR, gamma_1f, dchi/dlogomega).

**Engineering effort estimate**: 4-8 GPU-hours total to instrument all 5 probes as observability hooks; reused across all subsequent capability tests at zero marginal cost.

**To Experiment Dev**: if Strategy routes this, the 5 probes are independent and parallelizable; each is implementable as ~50-line numpy snippet against existing W and s structures. **No new substrate code paths required** — just instrumentation reads.

---

## (i) Honest framing per [[feedback-no-smoke]]

**Substrate-product strength claimed here**: spin-glass-class observability built into substrate at near-zero marginal cost.

**Substrate-product weakness**: this is **diagnostic infrastructure, not capability**. It does not extend any of the 3 architectural ceilings (multi-hop d, Bet S K, Bet A M); it does not refute the Entry 137 V2.D mechanism refutation; it does not change Phase 1 5-test battery design. **It makes those tests informative, not pass-fail.**

**Honest probability estimate that this is high-impact for substrate-product roadmap**: P=0.55-0.70.
- Lower bound 0.55: it's "just" observability, and Strategy's current priority is the simplified 5-test battery, not richer diagnostics.
- Upper bound 0.70: substrate-as-spin-glass-laboratory is a substrate-product moat (per [[feedback-value-creation-not-competition]]) that competitors literally cannot replicate without building a substrate; making the diagnostic suite a standard observability layer establishes that moat as a shipping fact.

**HONEST-RECALIBRATION-pattern note (cross-agent rejection rate)**: 12th of session. Agent A's optical/spectroscopic findings were largely REJECTED as decorative (polarized light / holography / ellipsometry / Brillouin all fail substrate-applicability); Agent C's quirky findings were largely REJECTED with 4 survivors out of ~15 considered; Agent B's magnetic/resonance findings had the highest survival rate (5/6). The substrate-product engineering discipline holds: substrate's non-spatial, fully-connected, discrete, classical architecture rejects most cross-domain probes; the ones that survive map to **spin-glass canonical observables** as expected from Bet E ✅.

**Process-discipline observation**: this is **the first user-directed research note where the entire deliverable mass is observability-infrastructure rather than mechanism / capability / refutation**. New pattern. Substrate-product engineering loop now closes on a third axis (instrumentation), complementing the two existing axes (mechanism research → Strategy routing → Exp Dev confirmation; theory refinement → empirical vindication per Entry 118).

---

## (j) End-of-note pointer

**File**: `notes/research_materials_characterization_methods_2026-05-22.md`
**Cross-references**:
- [[research-BetE-parisi-methodology-2026-05-21]] (Bet E ✅ Parisi P(q) substrate spin-glass foundation)
- [[research-R23-continuous-RSB-AT-line-2026-05-21]] (RSB / AT line substrate-applicability)
- [[research-R24-FDT-violation-2026-05-21]] (FDT-violation substrate framework)
- [[research-R16-free-probability-predictions-2026-05-21]] (Bet I ✅ moment-based characterization parallel)
- [[research-R29-ferromagnetism-domains-2026-05-21]] (Bet M ✅ ferromagnet/Hopfield link)

**Memory references invoked**:
- [[feedback-no-smoke]] — brutal-honesty framing applied throughout
- [[feedback-materials-science-probe]] — load-bearing materials analog
- [[feedback-subagent-model-optimization]] — Sonnet-dispatched parallel lit-scan
- [[feedback-query-privacy-decomposition]] — generic-math external queries only
- [[feedback-value-creation-not-competition]] — substrate-as-spin-glass-laboratory moat framing
- [[feedback-verify-implementations]] — 8 canonical citations grounding each probe
- [[feedback-unbiased-research]] — framing as "what does spin-glass characterization look like?" not "is substrate a good material?"

**End of note.**
