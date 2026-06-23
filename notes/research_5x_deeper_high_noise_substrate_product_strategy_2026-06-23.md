# 5x DEEPER: High-noise substrate-product strategy (Shannon-floor exists, what do we DO about it)

**Date:** 2026-06-23
**Author:** Research (Opus 4.7)
**Drill type:** 5x-DEEPER — product-strategy synthesis, NOT mechanism-search
**Trigger:** Shannon-floor META (rows 675-678) is chain-grade-eligible across encoder type / M / N_DIM. Decoder-side cleanup (4 families) AND encoder-side mechanism family (per parallel `research_encoder_side_cleanup_ceiling_break_2026-06-23.md`) BOTH expected to terminate at the same information-theoretic ceiling at sigma>=1.5. Question is no longer "break the floor" — it is "what is the substrate-product's correct posture given the floor exists".
**Lit-scan calibration penalty:** applied (raw P deflated 0.15-0.25; novel-synthesis P capped at 0.50)
**Generic-terms-only queries** per query-privacy
**Avoids duplication:** option (a) encoder upgrade is covered by separate parallel drill — NOT re-scoped here.

---

## HEADLINE

**Substrate's correct posture at high noise is REFUSE-AWARE GRACEFUL DEGRADATION, not noise-breaking.** Top recommendation: **substrate-as-refuse-aware** — substrate detects when input noise exceeds its envelope and says so HONESTLY via the already-shipped `hdlab/refuse_gate.py` + `hdlab/conformal.py` primitives, instead of returning confident-but-wrong outputs. This is structurally what LLMs CANNOT do at scale (they hallucinate at high noise/OOD), which converts the Shannon-floor from a LIMITATION into a SUBSTRATE-PRODUCT DIFFERENTIATOR. P_deflated=0.55 the resulting "envelope OR refuse; never confidently-wrong" META becomes chain-grade-eligible after a ~30-min CPU production-regime sigma-sweep cell (`prod_regime_refuse_envelope_v1`). Composes with already-banked KF1 refuse_gate_audit cert evidence + 5 supporting biology/ECC/ML literature references — this is a confluence position, not a novel synthesis.

**Secondary leverage (parallel to refuse-aware, NOT alternative):** kinetic-proofreading-style 2-step substrate check (error rate^2 at energy cost; substrate-native = sample twice + agreement-gate) gives a cheap mechanical lift inside the envelope. P_deflated=0.30.

**Negative ruling on alternate options:** Option (c) ensemble/sqrt(N) averaging is REAL but requires multiple independent noisy cues per query — not available in single-shot inference; demote to "applicable when input is a stream"; Option (d) sub-bipolar / float-valued payload is REFUTED by the META branch-#3-closure (learned char-trigram encoder ALREADY tested across families; same floor); Option (e) different substrate is OUT-OF-SCOPE per project charter (HDC substrate is the bet).

---

## CHEAP DECISIVE TEST

### Primary cell: `prod_regime_refuse_envelope_v1` (substrate-as-refuse-aware confluence test)

**Premise.** If substrate fails GRACEFULLY at high noise — i.e. its OWN confidence drops with rising sigma, and the refuse_gate primitive correctly fires — then the Shannon-floor becomes a feature (calibrated refusal) not a bug (silent failure). The decisive question is binary: does substrate confidence (max-cosine over codebook) track noise sigma monotonically enough for a tau calibrated at sigma=0.5 to fire >= 0.90 of the time at sigma=1.5? If yes, ship "envelope OR refuse" as the META; if no, then refuse-aware framing is also closed at high noise and substrate must fall back to mechanical option (b) "operate within envelope only; document".

**Cell design (~30 min CPU laptop, numpy only):**
- M=200, N_DIM=2048 (matches META row 675 anchor config), n_seeds=[7,17,23,29,31] (n=5 for tighter band)
- noise sigmas: production-regime mix `[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]` (typical=0.5, stress-events=1.5)
- TWO query streams per sigma:
  - **IN-DIST**: query is `atom[i] + noise(sigma)` (the noisy true atom)
  - **OOD**: query is `random_bipolar(N_DIM)` (no overlap with codebook; should refuse)
- Three ARMS:
  - **ARM_BASE_ARGMAX** (current substrate; no refuse): pure argmax cosine; recall@1 + confidence = max-cosine raw
  - **ARM_REFUSE_GATED** (substrate-as-refuse-aware): same argmax + tau calibrated via `hdlab/refuse_gate.calibrate_refuse_threshold` on (sigma=0.5 in-dist scores) vs (sigma=0.5 ood scores); test-time accept iff max-cos >= tau, else REFUSE
  - **ARM_CONFORMAL_SET** (substrate-as-conformal-prediction-set): use `hdlab/conformal.calibrate_quantile` at alpha=0.10; output is a PREDICTION SET (top-k items satisfying nonconformity <= q) instead of a single argmax; size of set is the calibrated confidence signal — a singleton set means "I know"; an empty set means "I refuse"; a large set means "ambiguous"
- Each ARM measures, per sigma:
  - `recall@1_accepted` (recall on the accepted subset)
  - `accept_rate` (fraction of queries the ARM did NOT refuse)
  - `ood_refuse_rate` (fraction of OOD queries correctly refused)
  - `silent_error_rate` (fraction of in-dist queries WRONG-but-accepted) — KEY safety metric
  - `confidence_calibration` (Pearson rho between max-cos and noise sigma)

**Decisive metrics:**
- `silent_error_rate` at sigma=1.5 — substrate is "confidently wrong" rate
- `ood_refuse_rate` at sigma=1.5 — substrate's ability to detect "I don't know"
- `recall@1_accepted` at sigma=0.5 (typical) — substrate must STILL WORK in normal regime

---

## FALSIFIABLE PREDICTIONS

### Pre-registered HARD-PASS (substrate-as-refuse-aware becomes chain-grade-eligible META)

**ARM_REFUSE_GATED pre-reg HARD-PASS:**
- HP1: `recall@1_accepted` at sigma=0.5 >= 0.80 (substrate works in normal regime; bar set above current cert-grade norm)
- HP2: `silent_error_rate` at sigma=1.5 <= 0.05 (substrate seldom confidently-wrong at stress regime)
- HP3: `ood_refuse_rate` at sigma=1.5 >= 0.90 (substrate detects OOD honestly at stress)
- HP4: `accept_rate` at sigma=1.5 <= 0.25 (substrate KNOWS to mostly refuse at stress, doesn't pretend)
- HP5: `confidence_calibration` rho >= 0.50 (substrate's own confidence tracks noise reality)

**ARM_CONFORMAL_SET pre-reg HARD-PASS (independent):**
- HP6: empirical marginal coverage (1 - alpha) within +/- 0.03 of nominal 0.90 at sigma=0.5 and sigma=1.5 (conformal guarantee holds)
- HP7: median prediction-set size at sigma=0.5 is 1 (singleton — substrate IS confident)
- HP8: median prediction-set size at sigma=1.5 is >= 5 OR empty (substrate ADMITS ambiguity via larger set)

### Pre-registered HARD-FAIL (refuse-aware framing CLOSED; substrate must descope to envelope)

**ANY of the following triggers HARD-FAIL for the "substrate-as-refuse-aware" META:**
- HF1: `silent_error_rate` at sigma=1.5 > 0.20 (substrate gives confidently-wrong answers at stress; refuse_gate primitive insufficient at high noise; **mechanism null**)
- HF2: `ood_refuse_rate` at sigma=1.5 < 0.50 (substrate cannot reliably distinguish OOD from in-dist at high noise; calibration breaks)
- HF3: `recall@1_accepted` at sigma=0.5 < 0.50 (substrate broken in normal regime — implementation bug; rerun before mechanism conclusion)
- HF4: `confidence_calibration` rho < 0.20 (substrate confidence is NOISE-INVARIANT — fundamental signal-vs-confidence collapse; max-cosine is not a usable scalar for refusal)

### MIDDLE_BAND (refuse-aware partially works; tune-then-revisit)

If 2 of 5 HARD-PASS metrics fire but HARD-FAIL is not triggered: substrate's refuse-awareness is REAL but partial. Action: tune tau via per-sigma stratification (Mondrian conformal); re-test before atomization.

### Sanity self-test (mandatory before atomize)

- At sigma=0.0: ARM_BASE_ARGMAX must reach recall@1 = 1.000 (clean cue, by-construction). If not, cell has implementation bug.
- At sigma=0.0: ARM_REFUSE_GATED accept_rate must be >= 0.95 (substrate is confident on clean input). If not, tau is mis-calibrated.

---

## CROSS-THREAD SYNTHESIS

### L1 literature breadth (7 disparate fields scanned in parallel)

1. **Kinetic proofreading (Hopfield 1974) — biology / molecular machines.** Error rate squared (e_eff = e_0^2) by adding a single check step with energy cost. Substrate-native analog: query substrate TWICE with the same cue + an independence-perturbation; accept iff both queries return the same atom. Cheap (~2x argmax). Predicted error rate at sigma=1.5: argmax 0.977 -> 2-step 0.954 (still ~floor). **Does NOT break Shannon-floor** but tightens silent-error rate when used INSIDE the envelope. Composes with refuse_gate as a SECONDARY gate. P_deflated=0.30.
2. **Population vector decoding (Georgopoulos 1986; recent Frontiers 2025 vectorial sensorimotor decoding) — neural ensembles.** Cosine summation over MANY independently-tuned neurons; noise correlation is the limiting factor (the literature explicitly says correlated noise breaks the ensemble; substrate's all-share-the-same-cue is the WORST case for this). **Not applicable to single-shot inference**; requires ensemble of independent decoders OR stream of noisy cues. Demote.
3. **Stochastic resonance — physics / signal processing.** Optimal noise level EXISTS for sub-threshold signals; substrate could exploit this. But the META data shows substrate is ABOVE threshold at sigma=0 and drops monotonically — substrate is NOT a sub-threshold detector, so SR does not apply. **Closed as non-applicable to this regime.** (Would be interesting if substrate had a hard threshold at low noise — it does not.)
4. **Rate vs temporal coding — neuroscience.** Rate coding is more robust to noise but slower; temporal is faster but fragile. Substrate is amplitude-coded (bipolar dense), structurally closer to rate-coding. The literature offers no rate-vs-temporal trick that breaks the floor at fixed signal/noise — both saturate Shannon. **Closed.**
5. **LDPC / turbo codes — coding theory.** Capacity-approaching iterative decoders close to Shannon limit (within 0.04 dB of capacity at BER 1e-5). The catch: substrate codebook is NOT a structured ECC codebook — it is random or learned, NOT designed for capacity. To exploit LDPC-style iterative decoding, substrate would need a redesigned codebook (parity-check structure). **Open as future direction** (~weeks-of-work, novel-synthesis P_deflated=0.20 capped); NOT this drill's cheap test.
6. **Ensemble averaging — signal processing.** SNR improves by sqrt(N) with N independent measurements. Substrate inference is single-shot — requires query stream. **Demote** to "applicable when substrate-product runs continuously over a noisy stream" (not the typical inference call).
7. **Selective classification / conformal prediction with reject option — ML.** Direct match. Recent 2025-2026 work on Selective Conformal Risk Control (SCRC; arXiv:2512.12844) and "Classification with reject option via Conformal Prediction" (arXiv:2506.21802) shows the exact framing: abstain on low-confidence inputs + apply conformal risk control to accepted subset. **Substrate's `hdlab/refuse_gate.py` + `hdlab/conformal.py` ALREADY implement this.** This is the load-bearing cross-thread synthesis — the substrate has the primitives, the literature has the framing, the META has the floor. **CONFLUENCE.**

### L2 filter — which strategies survive contact with substrate constraints (no backprop; forward-only inference; HDC bipolar codebook)

| Strategy | Forward-only? | Single-shot capable? | Survives Shannon-floor at sigma>=1.5? | Substrate primitive exists? | Verdict |
|---|---|---|---|---|---|
| Kinetic proofreading (2-step gate) | YES | YES | Improves inside envelope; not above floor | NO (cheap to build) | KEEP as secondary |
| Population vector (ensemble cosine sum) | YES | NO (needs ensemble) | YES if uncorrelated | partial (D-stack substrate) | DEMOTE to streaming |
| Stochastic resonance | YES | YES | NO (not sub-threshold) | NO | CLOSED |
| Rate vs temporal coding | YES | YES | NO (Shannon-equivalent) | YES (rate) | CLOSED |
| LDPC iterative decoding | partial | YES | YES (capacity-approaching) | NO (redesign needed) | OPEN, novel-synthesis |
| Ensemble sqrt(N) averaging | YES | NO (needs stream) | YES if N grows | partial | DEMOTE to streaming |
| **Selective conformal + reject** | YES | YES | YES (refuses instead of failing) | **YES** (refuse_gate + conformal already shipped) | **PRIMARY** |

### L3 depth on top-1 (selective conformal + reject = substrate-as-refuse-aware)

The substrate's `refuse_gate.calibrate_refuse_threshold` already solves the binary accept/refuse problem from paired in-dist / ood scores; it shipped to KGStore on n8 / U1 (CERT 584/585). The substrate's `conformal.calibrate_quantile` already solves the distribution-free coverage guarantee. These TWO primitives composed give "envelope OR refuse, with calibrated coverage". The KF1 finding (zero hallucinations at production scale; refuse_gate_audit domain has 2 cert atoms) is the early empirical evidence that this is not a paper exercise — the substrate is structurally suited to it (sparse codebook, max-cosine confidence, no soft-attention smoothing that compresses high noise scores into the same range as low noise scores; LLM softmax inherently HIDES uncertainty by normalizing every token to a probability simplex).

**The KEY insight:** at sigma=1.5 the substrate's max-cosine drops from ~1.0 (sigma=0) toward chance (~1/sqrt(N) on random vectors). This means substrate confidence is ALREADY noise-dependent in the right direction — refuse_gate just thresholds it. The cell-design tests whether the calibration is tight enough to fire at HP3>=0.90 OOD-refuse-rate.

### L4 cell-design implications (mixed-sigma PRODUCTION-REGIME, not toy stress)

Production input is a MIX: typical sigma~0.5, occasional stress sigma~1.5. The cell explicitly samples this mixed distribution, NOT just the worst case. This matches the "envelope of THIS method/config, extension untested" discipline (per `feedback_measured_bounds_are_method_config_contingent_not_fundamental_USER_2026-06-16.md`). HARD-PASS bands distinguish "works in typical + refuses in stress" from "works in typical + silently wrong in stress" — the latter is the LLM-comparison wedge. The substrate-product claim is NOT "substrate beats LLM at high noise" — it is **"substrate KNOWS when it cannot answer; LLM doesn't."**

### L5 cross-substrate composition

- **Composes with KF1 refuse_gate_audit (already chain-grade-eligible).** This drill EXTENDS the existing refuse-gate evidence base from KG-retrieval (n8 / U1) to noisy-input cleanup. Substrate now has refuse-coverage across TWO query domains.
- **Composes with kinetic-proofreading secondary gate.** Inside the accepted subset, run a 2-step substrate check; this further squeezes silent_error_rate at small extra cost. Future cell composition.
- **Composes with the encoder-side drill (parallel).** If sparse-fan-in N=4096 encoder lifts the operating envelope from sigma<=1.0 to sigma<=1.5, then the same refuse-aware framing applies at the NEW envelope boundary; the META doesn't change, just the envelope moves. The two drills are orthogonal and additive.
- **Composes with conformal prediction-set ARM_CONFORMAL_SET.** A prediction set is a richer output than accept/refuse; downstream consumers (chain-of-multi-hop, KG-traversal) can use set-size as ambiguity signal AND act on it (e.g. branch on each set member).
- **DIFFERENTIATES from LLM substrates structurally.** LLM softmax always emits a normalized probability distribution; high noise just spreads it more evenly across tokens, but the highest-probability token is still EMITTED with nonzero-and-often-confidence-looking probability. LLMs have no native refuse primitive; they require external classifiers (selective classification training) bolted on. Substrate's max-cosine + refuse_gate is NATIVE — the substrate KNOWS its own confidence directly from its representation geometry, no extra training.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

### Top-line claim (chain-grade-eligible META candidate after HARD-PASS)

> **"Substrate operates within its noise envelope (sigma <= ENV) OR refuses (high accept-rate + low silent-error-rate); it is never confidently-wrong at high noise. This holds across N_DIM in [512, 16384], M in [25, 400], and codebook type in {random, learned char-trigram, hub-spoke}."**

This META atom would compose with rows 675-678 (the existing Shannon-floor evidence) to upgrade the parent META from "Shannon-floor exists; substrate descopes" to "Shannon-floor exists; substrate REFUSES instead of failing silently". The descope becomes a CALIBRATED ENVELOPE not a hard limit.

### Customer-facing posture

- **Honest envelope-disclosure.** Substrate-product ships with `envelope_disclosure` API: caller queries the substrate with their typical noise sigma; substrate returns `(envelope_within=True, expected_accept_rate=...)` or `(envelope_within=False, recommendation='reduce noise via encoder upgrade')`. This is a PRODUCT FEATURE — customers can choose to dispatch the cheap substrate-call vs the expensive LLM-call based on whether their input is in-envelope.
- **Cascading inference pipeline.** Substrate handles in-envelope queries (cheap, fast, calibrated-confidence). Refused queries cascade to a higher-cost backend (larger encoder, LLM, human review). This makes substrate the FIRST tier of a tiered-confidence inference system, NOT a competitor to LLMs at every noise level — it WHERE the substrate is honest about its strengths.
- **Safety-critical positioning.** At sigma>=1.5 substrate refuses; downstream system knows to escalate. This is the safety wedge against LLM confident-hallucination at high noise / OOD. The Shannon-floor BECOMES the safety guarantee.

### What the substrate-product is NOT claiming

- NOT claiming substrate beats LLM at high noise — it doesn't (Shannon-floor is universal).
- NOT claiming refuse-aware is novel — selective classification + conformal-with-reject are well-established (citations below).
- NOT claiming this CLOSES the bigram-gap — the bigram-gap is a separate capability axis (text8 BPC); refuse-aware is orthogonal.
- NOT claiming this removes the need for encoder upgrade — encoder upgrade EXTENDS the envelope; refuse-aware HANDLES outside-envelope.

### Tier classification

Per `feedback_capability_dev_is_goal_cert_grade_is_instrument_USER_2026-06-19.md`: the substrate-as-refuse-aware capability is INSTRUMENT (cert-grade goal) for the DEVELOPMENT goal of substrate-product trust. HARD-PASS would atomize as **MEASURED_MECHANISM** (per `by_construction_saturation` discipline — the refuse-gate primitive IS by-construction designed to refuse OOD; the cert-grade question is whether at sigma=1.5 the substrate confidence is geometrically distinguishable from OOD confidence). If yes, the META that COMPOSES "Shannon-floor + refuse-aware" goes chain-grade-eligible.

### What to ship to hdlab/ if HARD-PASS

`hdlab/noise_envelope.py` — composed primitive: argmax + refuse_gate + conformal-set, with a single `query(cue, mode='argmax_with_refuse'|'conformal_set', tau=None, q=None)` API. Wraps the two existing primitives + adds the envelope-disclosure response shape.

---

## CITATIONS (verified, 7 sources across 4 fields)

1. **Kinetic proofreading.** Hopfield, J.J. (1974). "Kinetic Proofreading: A New Mechanism for Reducing Errors in Biosynthetic Processes Requiring High Specificity." PNAS 71(10):4135-4139. Verified at https://www.pnas.org/doi/10.1073/pnas.71.10.4135 and Berkeley Garcia Lab PDF host.
2. **Population vector decoding.** Georgopoulos et al. (1986) — multiple modern reviews. "Vectorial principles of sensorimotor decoding" (Frontiers Human Neuroscience 2025; PMC12287768) and "Neuronal Population Vector" (Springer Encyclopedia of Computational Neuroscience). Noise correlation as limiting factor: Frontiers in Computational Neuroscience 2014 8:58.
3. **Stochastic resonance / SSR.** McDonnell & Stocks (2007). "Optimal stimulus and noise distributions for information transmission via suprathreshold stochastic resonance." Phys. Rev. E 75(6):061105 (arXiv:0704.0673).
4. **Rate vs temporal coding.** "Neural Coding in Spiking Neural Networks: A Comparative Study for Robust Neuromorphic Systems." Frontiers in Neuroscience 2021 15:638474 (PMC7970006). Rate-coding noise robustness + 15-50 bits/s capacity match.
5. **LDPC capacity-approaching.** Richardson, Shokrollahi, Urbanke (2001) density evolution + modern review "Channel Coding 101: LDPC vs Turbo vs Polar Codes" + arXiv:2404.14828 (GLDPC-PC for 6G). 0.04 dB-from-Shannon at BER 1e-5.
6. **Selective conformal classification.** "Selective Conformal Risk Control" (arXiv:2512.12844, 2025); "Classification with reject option: Distribution-free error guarantees via Conformal Prediction" (arXiv:2506.21802, 2025); "Know When to Abstain: Optimal Selective Classification with Likelihood Ratios" (arXiv:2505.15008, 2025). Direct framing match for substrate-as-refuse-aware.
7. **Ensemble averaging / SNR sqrt(N).** "Ensemble Averaging in Medical Signal Processing" (Towards Data Science 2024); standard result, demoted to streaming applicability.

Cross-substrate composing atoms (from prior research deliveries; not external):
- META rows 675-678 (Shannon-floor at 3-codebook x M-scan x N_DIM-scan); chain-grade-eligible parent.
- KF1 refuse_gate_audit domain (2 cert atoms; zero-hallucination at production scale; per `research_substrate_NEGATIVES_2x_negative_was_positive_3x_scour_USER_DIRECTIVE_2026-06-20.md`).
- `hdlab/refuse_gate.py` + `hdlab/conformal.py` (already-shipped primitives; verified by Read).
- `research_encoder_side_cleanup_ceiling_break_2026-06-23.md` (parallel encoder-side drill; orthogonal).

---

## P-DEFLATED ESTIMATES (lit-scan calibration penalty applied)

- P(HARD_PASS substrate-as-refuse-aware META; cell-confluence ARM_REFUSE_GATED): **0.55** (raw 0.75 deflated 0.20 for substrate-novel application of standard primitive at higher-than-tested noise sigma; this is composition of two existing chain-grade-eligible substrate primitives + 3 lit-precedent fields, NOT a novel mechanism, so capped at 0.55 not 0.50)
- P(HARD_PASS ARM_CONFORMAL_SET meeting nominal coverage at sigma=1.5): **0.50** (raw 0.70 deflated 0.20 because exchangeability assumption holds for calibration/test split BY DESIGN; the test is whether the noise dimension is in fact exchangeable)
- P(MIDDLE_BAND outcome — partial refuse-awareness; tau-tuning required): **0.25**
- P(HARD_FAIL — silent-error-rate at sigma=1.5 > 0.20): **0.15** (this is the structural-closure outcome; substrate cannot use max-cosine as a refuse signal at high noise; would re-route to LDPC redesign or accept envelope-only descope)
- P(kinetic-proofreading 2-step secondary gate gives an additional measurable lift): **0.30** (raw 0.50 deflated 0.20; cheap to build but error^2 only helps where the original error is bounded away from random)

---

## NEXT-DRILL CANDIDATE (per Trigger C adjacency-cascade)

If HARD_PASS: queue **conformal-with-Mondrian-stratification by sigma-band** — per-noise-stratum tau gives tighter coverage; matches `coding-theory` adjacent angle in field advisor. Cheap follow-up (~30 min CPU).

If HARD_FAIL: route to **redesigned-codebook with parity-check structure (LDPC-on-substrate)** — substrate codebook becomes an explicit ECC code; this is the open-mechanism path noted in L1 #5; field=coding-theory; cost = ~1 week novel-synthesis; P=0.20 capped.

If MIDDLE_BAND: tau-tuning + kinetic-proofreading composition; cheap iteration.

---

## STATUS

Note path: `notes/research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md`
Companion exp_dev handoff: `notes/exp_dev_handoff_research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md`
Status log: written via `tools/orchestrator/state.py log_event` (importance=HIGH).
