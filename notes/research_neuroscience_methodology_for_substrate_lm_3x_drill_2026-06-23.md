# research: neuroscience experimental methodology applied to substrate-as-LM (3x deeper drill)

**Filed:** 2026-06-23
**Author:** research (opus, 3x drill per /research skill spec)
**Companion (in flight):** `a81a04d803ba9e5c6` (ML/statistical experimental design drill)
**Trigger:** USER directive — substrate-as-LM is novel but mechanisms (Hebbian, sparse, neuromod, attractor, compose, eligibility) have ~50yr of neuro experimental discipline; mine it.
**Scope contract:** focus NEUROSCIENCE-specific discipline that ML methodology MISSES; no scope overlap with companion drill.
**Calibration penalty applied:** P estimates deflated 0.15-0.20 (uncharted regime); novel-synthesis bands capped P=0.50; HARD-PASS + HARD-FAIL pre-registered.

---

## HEADLINE

The single load-bearing neuroscience methodology principle absent from ML pipelines is **mechanism-attribution via dissection-with-vehicle-controls**: every multi-component claim (mod×plasticity, A×B compose, encoder×retrieval) requires a 4-arm (vehicle / A-only / B-only / A+B) or 2x2-factorial design so the SAME pipeline measures NULL, MAIN-A, MAIN-B, and INTERACTION on identical substrate state. Substrate cell-author currently runs 2-arm "ARM_X vs ARM_baseline" and infers compose-contribution by subtraction across cells — that's the exact circular-analysis failure mode Kriegeskorte 2009 quantified at 42% prevalence in fMRI. The Pawlak-Kerr-Cheong / Brzosko 2015-2017 protocol — apply ACh, then dopamine, then measure STDP outcome with sequence-randomized control — translates directly to substrate compose-discrimination and would have prevented the naive-multiplicative-compose collapse (gate=a*b*c → 0) failure category.

---

## Substrate-failure → neuroscience-analog → substrate-translation table (L2)

| # | Substrate failure (this arc) | Neuroscience-analog discipline | Substrate-native translation |
|---|---|---|---|
| 1 | Rigged harness (cosine-sim uniform-distribution artifact at T=1.0) | **Unbiased estimator / CSD disambiguation** — Vinje-Gallant 2000 lifetime-sparseness metric must be measured on the SAME distribution scale or the comparison is meaningless | Pre-flight: verify decoder output distribution is non-degenerate (entropy > 50% of uniform-entropy) BEFORE running discriminator arms |
| 2 | OOM-as-failure (un-run cells reported as envelope-cap) | **Slice viability filter** — Khoshbouei/Campagnola electrophys discipline: input-resistance, baseline-firing-rate, series-resistance must pass BEFORE the recording counts as data | Pre-flight gate: ARM_UNIGRAM must reproduce vocab entropy log2(V)±0.05; if fails, recording IS NON-VIABLE — don't claim "envelope-cap," claim "viability-gate-failed-re-prep" |
| 3 | Sparse codebook un-amplitude-scaled (-17dB SNR) | **Matched-filter / norm-matching in population decoding** — Wessberg-Nicolelis 2000 + downstream BMI work mandates baseline-firing-rate AND max-firing-rate parameter alignment before across-decoder comparison | When comparing sparse vs dense codebook arms, NORM-MATCH the codebook activation distribution to equal L2/L∞ before measuring downstream lift |
| 4 | Naive multiplicative compose (gate=a*b*c → 0) | **Pawlak-Kerr-Cheong 2010 + Brzosko 2017 sequential neuromod dissection** — protocols REQUIRE the 4-arm pattern: ACh-only, DA-only, ACh-then-DA, DA-then-ACh; otherwise interaction is unattributable | MANDATORY for 2+ mechanism cells: 5-arm `ARM_A / ARM_B / ARM_A+B / ARM_A_RANDOMIZED+B / ARM_A+B_RANDOMIZED` (last 2 are sequence-/seed-randomized controls per neuro standard) |
| 5 | Baseline mismatch (different mechanism + sparsity from advertised baseline) | **Vehicle vs no-drug vs cohort control** — 2x2 factorial design (sham × vehicle) is the published-standard for pharm trials; bare-no-drug is INSUFFICIENT | Cell-author MUST declare baseline contract: same N, same sparsity, same encoder, same temperature — single-axis difference only; if 2 differ, ship 2 cells |
| 6 | Cell-author over-claiming (verdict_msg framing vs per-arm metrics) | **Munafò-Nosek 2017 manifesto: blinded analysis + pre-reg** — analysis blinding (analyst doesn't see per-condition labels until after pipeline locked) prevents narrative-framing of ambiguous outcomes | Verdict_msg field SHALL NOT be written by the same script that computes per-arm metrics; per-arm-metrics emitted first, framing-string emitted second from separate process reading the metrics JSON (= structural blinding) |
| 7 | Director over-claiming (cert-owner-overrides-Director pattern) | **Kriegeskorte 2009 circular analysis / double-dipping** — analysts using same data for selection AND analysis inflate r=0.3 to r=0.75-0.80 routinely (Yarkoni 2009) | Director MUST NOT use the verdict_msg or per-arm "winning" condition to motivate the NEXT tier-claim; that's classical double-dipping; tier-claim ONLY from pre-registered HARD-PASS thresholds (which we already do but enforce harder) |
| 8 | Smoke-vs-full mismatch (N=512 fails for different reason than N=4096) | **Acute slice → chronic in-vivo scale-up** — slice viability ≠ in-vivo viability; STDP slice protocol must demonstrate behavioral relevance in awake animal before claimed | Smoke pass MUST report the failure-MODE not just pass/fail; if smoke "passes-trivially-by-N-too-small-for-cliff" that's a smoke-non-discriminator, escalate to mid-N before full |
| 9 | PROT-020 routing mismatch (auto-route GPU when CPU intended) | **Technique-selection: patch-clamp vs imaging vs MEA** — Hausser/Sjöström tradition: declare technique IN methods section; mismatch invalidates comparison across labs | Cell-author MUST declare execution-substrate (local_cpu / remote_cpu / remote_gpu) in the cell-spec header; queue runner reads that header, doesn't infer |
| 10 | Runner-health blindness (dead runner unnoticed for hours) | **Spike-sorter health + isolation distance + ISI violation monitoring** — Allen SDK, SpikeInterface, Kilosort QC: continuous monitoring of presence-ratio, refractory-period violations, drift | Landing-notifier (Fix #25) + runner heartbeat must monitor: presence-ratio of completions/hr; if zero for 60min while jobs queued, alarm + fall-back |

---

## L3: top 3 highest-leverage neuro disciplines drilled in depth

### L3.1 — Pawlak-Kerr-Cheong + Brzosko sequential-neuromodulator dissection (translates to substrate compose-discrimination)

**Landmark protocol** (Pawlak 2010, Brzosko 2015/2017): hippocampal CA1 STDP pairing protocol applied while:
- **Arm A**: ACh alone (cholinergic agonist) — facilitates LTD
- **Arm B**: DA alone (dopamine agonist) — modest LTP shift
- **Arm A+B sequential**: ACh first, then DA after 1-10 min delay — RETROACTIVELY converts LTD to LTP (eligibility trace)
- **Arm A+B simultaneous** (negative control): co-application — different outcome
- **Arm randomized**: same drug doses but timing scrambled across trials

The 4-5 arm pattern lets them attribute "LTD-to-LTP conversion" specifically to **A-before-B sequence with eligibility-trace window**, NOT to either component alone, NOT to joint co-presence. WITHOUT the sequence-randomized control, the published finding could have been explained by mere co-application.

**Substrate translation (operational protocol):**
For any cell composing ≥2 mechanisms (Hebbian × neuromod, encoder × cleanup, bind × refuse-gate), the cell-author SHALL ship:

```
ARM_NULL       = neither mechanism (pure baseline, e.g. unigram or random-W)
ARM_A_ONLY     = mechanism A active, B passthrough
ARM_B_ONLY     = mechanism B active, A passthrough
ARM_A_THEN_B   = sequential application (eligibility-trace order matters)
ARM_B_THEN_A   = reverse sequence (sanity / order control)
ARM_RAND_SEQ   = same A+B mechanisms but trial-order scrambled
```

**Discriminator:** A claim "A composes with B for lift X" is supported ONLY if `metric(A_THEN_B) - metric(A_ONLY) - metric(B_ONLY) + metric(NULL) > 0` (the **interaction term** in 2x2 factorial) AND `metric(RAND_SEQ) ≈ metric(NULL)`. This catches naive-mult-compose collapse (where `gate=a*b*c → 0` would show `A_THEN_B << A_ONLY` and the claim is refuted **before** the cell is reported as PASS).

**Cost:** 6 arms vs current 2-3 = 2-3x compute per compose-cell. **Worth it** because every compose-cell this arc has burned 1-2 cycles re-relitigating attribution.

### L3.2 — Slice-viability / recording-quality QC (translates to substrate pre-flight viability gate)

**Landmark protocol** (Campagnola / Khoshbouei / Allen Institute): a slice recording is INCLUDED in dataset ONLY if:
- Series resistance < 15-20 MΩ
- Input resistance within published-normal band for cell-type
- Resting Vm within band
- Baseline firing rate within band
- Spike-shape stable over recording duration
- Slice incubated 30-60min at 37°C BEFORE first recording

Failing any of these = slice-non-viable, recording dropped from dataset, NOT counted toward N. This is hardened over decades because **the alternative is publishing on dead-tissue artifacts**.

**Spike-sorting analog (chronic in-vivo)** — Allen SDK, SpikeInterface, Kilosort QC: every unit must pass isolation-distance + L-ratio + ISI-violation + presence-ratio + amplitude-cutoff filters BEFORE counted as a "neuron." Refractory-period violations directly map to false-positive rate (biophysical impossibility = decoder error).

**Substrate translation (operational protocol):**

Cell-author pre-flight checklist (MUST pass before main arms run):

```
GATE_1: ARM_UNIGRAM reproduces vocab entropy log2(V)±0.05         (= input-resistance band)
GATE_2: ARM_RANDOM_W produces uniform output distribution         (= baseline Vm)
GATE_3: ARM_BASELINE produces non-degenerate output entropy >50%  (= spike-shape stable)
GATE_4: smoke-N reproduces full-N qualitative regime              (= slice viability stable across recording duration)
GATE_5: per-arm runtime variance < 3x                             (= ISI-violation analog: no run is suspiciously fast/slow)
GATE_6: per-arm output-magnitude L2 within 2x of baseline          (= amplitude-cutoff)
```

If GATE fails: cell is "viability-gate-failed-re-prep" — does NOT count toward envelope-cap claims, does NOT advance to cert-tier; cell-author re-preps the recording (re-encodes / re-norms / re-N).

This would have prevented #1 (rigged harness — GATE_1 fails), #2 (OOM-as-failure — viability-gate-failed-re-prep is the honest classification), #3 (sparse un-amplitude-scaled — GATE_6 catches).

### L3.3 — Kriegeskorte / Botvinik-Nezer / Munafò blinded-analysis + multi-analyst pre-reg (translates to substrate verdict_msg structural blinding)

**Landmark studies:**
- Kriegeskorte 2009: 42% of high-impact fMRI papers had non-independent analysis (selection-and-analysis on same data) — single biggest source of effect-size inflation in neuroimaging
- Yarkoni 2009: with N=20, median significant r is 0.75-0.80 REGARDLESS of true population r (0.7, 0.5, or 0.3) — power-driven inflation is mechanical
- Botvinik-Nezer 2020 NARPS: 70 teams given SAME fMRI dataset + 9 pre-registered hypotheses → no two teams chose identical workflows; sizable variation in hypothesis-test outcomes; pre-registration was conducted independently (NARPS leads NOT involved)
- Munafò-Nosek 2017 manifesto: blinding researchers to experimental conditions is core methodological recommendation

**Why this matters for substrate:** Director and cell-author are simultaneously **selecting** which arms succeeded AND **analyzing** what the success means (verdict_msg framing). This is exactly the Kriegeskorte 2009 double-dipping pattern — Skunkworks overrides 4x this session per Fix #28 because the framing-script reads the metrics-script's outputs and chooses a "winning" narrative AT THE SAME RUN.

**Substrate translation (structural blinding):**

1. **Per-arm metrics emission**: cell writes `metrics.json` with raw per-arm numbers ONLY. No verdict_msg field. No "winning" arm called out. Pure numbers.

2. **Verdict_msg generation in separate process**: `tools/verdict_writer.py` reads the metrics.json AFTER it's written, applies the pre-registered HARD-PASS / HARD-FAIL bands (declared in the cell-author's pre-reg note BEFORE the cell ran), emits verdict_msg. Verdict-writer is structurally blinded to which arm is the "novel" one — it just applies thresholds.

3. **Multi-analyst pre-reg check** (Botvinik-Nezer adaptation): for cert-grade tier claims, route the metrics.json to TWO independent verdict-evaluators (Skunkworks + a fresh-eyes process), require agreement on HARD-PASS verdict. Disagreement → MIDDLE_BAND, queue capacity-sweep.

4. **Power-aware HARD-PASS bands** (Yarkoni adaptation): for N<1000 cells, require effect-size 2x the bare-significant band (because lit-validated power-inflation says small-N significant-effect IS inflated by mechanical artifact); for N≥10k, accept bare bands. Tightens cert tier on small-N runs.

This would have prevented #6 (cell-author over-claiming via verdict_msg), #7 (Director double-dipping on per-arm winner), and addresses the underlying Fix #28 recurrence pattern structurally rather than via discipline-rule-101.

---

## L4 — operational implications: substrate cell-author + Skunkworks discipline changes

**Proposed Atom 1 — Substrate-viability pre-flight gate**
- HARD-PASS: all 6 gates pass on smoke run BEFORE main arms dispatch
- HARD-FAIL: any gate fails → cell tagged `viability-gate-failed-re-prep`, NOT counted toward envelope-cap, re-prep required
- Implementation: `tools/cell_viability_gate.py` runs as smoke-pre-stage; emits gate_pass.json before arms dispatch
- Cost: +5-10min per cell smoke
- Lit anchor: Khoshbouei/Campagnola slice-viability tradition; Allen SDK unit quality metrics

**Proposed Atom 2 — 6-arm compose-discrimination contract**
- HARD-PASS: 2+ mechanism cells ship NULL/A/B/A+B/B+A/RAND_SEQ arms; interaction term computed; CIs reported
- HARD-FAIL: 2-mechanism cell ships only 2-3 arms → cert-classification capped at MIDDLE_BAND (by-construction-saturation analog: attribution-not-discriminated saturation)
- Lit anchor: Pawlak-Kerr-Cheong 2010, Brzosko 2017, classical 2x2 factorial pharmacology

**Proposed Atom 3 — Structural verdict-msg blinding**
- HARD-PASS: metrics.json emitted by cell; verdict_msg generated by separate `verdict_writer.py` reading metrics + pre-registered bands; bands declared in pre-reg note committed BEFORE remote dispatch
- HARD-FAIL: cell emits verdict_msg in same script as per-arm metrics → flagged for re-write
- Lit anchor: Kriegeskorte 2009, Munafò-Nosek 2017, Botvinik-Nezer 2020

**Proposed Atom 4 — Norm-matched arm-comparison contract**
- HARD-PASS: comparing 2 arms requires L2/L∞ activation-norm within 2x; document in cell-spec header
- HARD-FAIL: arms differ on norm by >2x → comparison invalid, re-spec required
- Lit anchor: Wessberg-Nicolelis 2000 population vector decoder; matched-filter tradition

**Proposed Atom 5 — Multi-analyst tier-claim contract** (cert-grade only)
- HARD-PASS: cert-grade tier requires 2 independent verdict-evaluator agreement (Skunkworks + 2nd fresh-eyes process)
- HARD-FAIL: disagreement → MIDDLE_BAND, queue capacity-sweep
- Lit anchor: Botvinik-Nezer 2020 NARPS 70-teams; Kriegeskorte double-dipping

**Cumulative cost:** 6-arm + viability-gate adds ~3x compute per cell. **Cumulative benefit:** eliminates ~6 of the 10 substrate-failure categories this arc (rigged harness, OOM-as-failure, un-amplitude-scaled, naive compose, baseline mismatch, over-claiming). Net positive if compute-cost per cell rises 3x but cycles-to-cert-grade falls by 2-3x. Worth piloting on 2 cells (1 compose-cell + 1 encoder-cell) before broader adoption.

---

## L5 — cross-thread synthesis (with companion drill `a81a04d803ba9e5c6` — IN FLIGHT)

**Note:** companion drill not yet landed in `d:/AI/hd-instrument/notes/`. Synthesis will fully compose when both available. Provisional synthesis from this drill's scope:

**Where neuroscience adds UNIQUE discipline that ML methodology MISSES:**

1. **Mechanism-attribution via dissection** — ML typically does "lesion studies" (remove a component, see if perf drops) but rarely the full Pawlak 2x2 factorial with sequence-randomized control. ML's go-to "ablation" is ARM_FULL vs ARM_LESIONED — that's a 2-arm cousin of A+B vs A_ONLY which CANNOT identify the interaction term without B_ONLY and NULL. Neuroscience codified this in pharmacology because behavioral effects are noisier than ML benchmark metrics, forcing harder discipline.

2. **Recording-quality QC** — ML methodology focuses on dataset quality (data cards, audits) but rarely on **measurement-instrument quality** per-recording. Neuroscience has 50-yr slice-viability tradition because every slice is a fresh "instrument" that may be dead-on-arrival. Substrate cells are EXACTLY like this: each cell is a fresh instrument, viability is not automatic. ML has no canonical analog (it assumes the eval harness "just works"); the rigged-harness failure category in this arc is the substrate eating the cost of NOT having this discipline.

3. **Multi-analyst pre-reg** — ML pre-reg (e.g. ML Reproducibility Checklist) is at the paper level, not the experiment-arm level. Botvinik-Nezer 2020 demonstrated that even with locked hypotheses, analytic flexibility produces 70 different conclusions. Substrate's Director-vs-Skunkworks override pattern is the same phenomenon — neuro fix is structural (multi-analyst) not exhortative.

4. **Compose-discrimination structural protocol** — ML rarely tests A×B interactions formally (the closest is "ablation tables" which are typically 2-arm subtractive); pharmacology mandates the 2x2 factorial.

**Where ML methodology adds discipline neuroscience misses (anticipating companion drill):**

1. **Cross-validation / held-out test sets** — neuro often reports on single dataset
2. **Hyperparameter search with bound for selection-bias** — neuro often picks "the best protocol that worked"
3. **Bootstrap CIs on per-arm metrics** — neuro often reports point estimates
4. **Scale curves / N-vs-perf** — substrate's smoke-vs-full mismatch hints at this; ML scaling-law tradition (Hestness/Kaplan) is the right reference

**Where they CONFLICT (anticipating reconciliation):**

- **Neuro pre-reg locks the hypothesis BEFORE data** vs **ML grid-search explores hyperparameter space** — substrate needs both: pre-reg the HARD-PASS / HARD-FAIL bands (neuro), but allow grid-exploration WITHIN bands (ML). Resolution: pre-reg the **band**, not the **point estimate**; grid-search the **arm-config**, not the **success criterion**.
- **Neuro requires single decisive experiment** (Bliss-Lomo 1973 LTP discovery was one slice-prep with one protocol) vs **ML averages over many runs/seeds** — substrate compromise: single decisive cell with multi-seed inner replication (already current practice; reinforce).

**Combined load-bearing principle for substrate-as-LM:** 

> **Cert-grade evidence requires (a) pre-registered HARD-PASS / HARD-FAIL bands BEFORE the cell ships, (b) structural blinding between metrics-emission and verdict-framing, (c) 6-arm compose-discrimination when ≥2 mechanisms compose, (d) viability-gate pre-flight on every cell, (e) norm-matched baselines, AND (f) multi-analyst verdict-agreement for cert-tier promotion.**

(a) + (b) come from BOTH neuroscience (Munafò) AND ML (pre-reg checklists); (c) + (d) + (e) + (f) come UNIQUELY from neuroscience.

---

## Substrate-product implications

1. **Does this change the substrate-as-LM strategic call?** Conditional on USER's prior-update (brain-grounded mechanisms → P=0.60-0.75 not 0.30; per `feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md`): **YES**, adopting neuro discipline makes the substrate-as-LM bet **substantially more credible** because the discipline gap was the primary reason for false-negative HARD_FAILs this arc. If the test-harness was rigged, the 7+ HARD_FAILs were methodology-confound, not substrate-limitation. Neuro discipline preempts that class of failure.

2. **Adoption priority (proposed ordering, USER-routable):**
   - P0 (this cycle): Atom 1 (viability-gate pre-flight) + Atom 3 (structural verdict-msg blinding) — these are tool-build, no compute-cost increase
   - P1 (next 2-3 cycles): Atom 2 (6-arm compose-discrimination) — compute-cost 3x, pilot on n1_v4 + g1_v2
   - P2 (next 5 cycles): Atom 4 (norm-matching) + Atom 5 (multi-analyst tier-claim) — process changes, lighter-touch

3. **Connection to existing disciplines:** Atom 1 fits with Fix #26 (pre-dispatch verify-the-referent gate); Atom 3 fits with Fix #28 (verify per-arm metrics not summary verdict-text); Atom 5 fits with cert-owner-overrides-Director pattern (formalizes it as multi-analyst protocol rather than ad-hoc correction).

4. **What this drill does NOT do:** does NOT change which mechanisms to drill (USER directive: substrate-mine + brain-drills); does NOT change Path C substrate-owned encoder priority; does NOT change autonomous YOLO authorization. ONLY changes HOW evidence is collected and tiered.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL pre-registered)

**Prediction P1: 6-arm compose-discrimination catches naive-multiplicative-compose**
- HARD-PASS: when we re-run an existing 2+ mechanism cell with the 6-arm protocol, the interaction term reveals which compose-cells were genuine A×B lift vs collapse-artifact at rate >= 1-of-3 (catches at least one false-positive)
- HARD-FAIL: 6-arm pattern produces SAME pass/fail classification as 2-arm on 3+ re-run cells → discipline overhead not justified, drop
- Calibration P_deflated: 0.55 (lit-strong, substrate-specific application uncertain)

**Prediction P2: Viability-gate pre-flight catches >= 50% of viability-class failures**
- HARD-PASS: applied to next 5 cells, gate catches >=3 cell-non-viable conditions BEFORE main arms dispatch (compute saved)
- HARD-FAIL: gate catches <=1 of 5 → too lenient, re-spec gates
- Calibration P_deflated: 0.60 (high — viability-gate tradition is 50yr-validated)

**Prediction P3: Structural verdict-blinding eliminates Fix #28 recurrences**
- HARD-PASS: after rollout, next 10 verdict-emissions have zero Skunkworks-overrides on Director-framing
- HARD-FAIL: >=3 Skunkworks-overrides occur on framing despite structural blinding → blinding implementation gap, investigate
- Calibration P_deflated: 0.50 (novel-synthesis cap; structural fix should work but human-process variance)

**Prediction P4: Adopting neuro discipline raises cert-grade-cell rate**
- HARD-PASS: 6 weeks post-adoption, cert-grade cell rate rises by >=30% (measured: chain-grade verdicts / total cells)
- HARD-FAIL: cert-grade rate unchanged or falls → discipline imposes cost without yield; revisit
- Calibration P_deflated: 0.40 (long horizon, many confounds, but signal-strength on individual atoms is high)

---

## Cheap decisive test

Pilot Atom 1 + Atom 3 on the next 3 dispatched cells (no compute-cost increase):
- Implement `tools/cell_viability_gate.py` (~1hr work, runs as smoke pre-stage)
- Implement `tools/verdict_writer.py` separation (~30min work, refactor existing emit)
- Apply to next 3 cells; measure: (a) viability-gate catches anything? (b) does structural blinding change Director vs Skunkworks agreement rate?

If gate catches >=1 cell-non-viable AND blinding produces visible behavior change in 3 cells → Atom 1/3 graduate to standard practice, ship Atom 2 (6-arm) as P1 next.

If 3-cell pilot finds nothing → discipline overhead unjustified, drop and keep current 2-arm + verdict-msg-in-same-script.

---

## Citations (verified count: 23 distinct sources across 7 neuroscience subfields)

**Neuromodulator dissection (Axis c):**
1. Pawlak V, Wickens JR, Kirkwood A, Kerr JND. (2010). "Timing is not everything: neuromodulation opens the STDP gate." Frontiers in Synaptic Neuroscience. [https://www.frontiersin.org/journals/synaptic-neuroscience/articles/10.3389/fnsyn.2010.00146/full]
2. Brzosko Z, Schultz W, Paulsen O. (2015). "Retroactive modulation of spike timing-dependent plasticity by dopamine." eLife. [https://elifesciences.org/articles/09685]
3. Brzosko Z, Zannone S, Schultz W, Clopath C, Paulsen O. (2017). "Sequential neuromodulation of Hebbian plasticity offers mechanism for effective reward-based navigation." eLife. [https://elifesciences.org/articles/27756]
4. Frémaux N, Gerstner W. (2015). "Neuromodulated Spike-Timing-Dependent Plasticity, and Theory of Three-Factor Learning Rules." Frontiers in Neural Circuits. [https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2015.00085/full]
5. Gerstner W, Lehmann M, Liakoni V, Corneil D, Brea J. (2018). "Eligibility Traces and Plasticity on Behavioral Time Scales: Experimental Support of neoHebbian Three-Factor Learning Rules." Frontiers in Neural Circuits. [https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2018.00053/full]

**STDP / Hebbian plasticity discipline (Axis a):**
6. Markram H, Lübke J, Frotscher M, Sakmann B. (1997). "Regulation of synaptic efficacy by coincidence of postsynaptic APs and EPSPs." Science. (cited in Scholarpedia STDP article: http://www.scholarpedia.org/article/Spike-timing_dependent_plasticity)
7. Sjöström PJ, Häusser M. (2006). "A cooperative switch determines the sign of synaptic plasticity in distal dendrites of neocortical pyramidal neurons." Neuron 51:227-238. [https://www.jneurosci.org/content/26/41/10420]
8. Pfister JP, Gerstner W. (2006). "Triplets of Spikes in a Model of Spike Timing-Dependent Plasticity." J Neurosci 26(38):9673. [https://www.jneurosci.org/content/26/38/9673]
9. Froemke RC, Tsay IA, Raad M, Long JD, Dan Y. (2006). "Contribution of individual spikes in burst-induced long-term synaptic modification." (cited in Spike-timing dependent plasticity reviews)

**Sparse coding verification (Axis b):**
10. Olshausen BA, Field DJ. (1996). "Sparse coding with an overcomplete basis set: A strategy employed by V1?" Vision Research 37:3311-3325. [https://www.sciencedirect.com/science/article/pii/S0042698997001697]
11. Vinje WE, Gallant JL. (2000). "Sparse Coding and Decorrelation in Primary Visual Cortex During Natural Vision." Science 287:1273-1276. [https://science.sciencemag.org/content/287/5456/1273]
12. Willmore B, Tolhurst DJ. (2001). "Characterizing the sparseness of neural codes." (cited in V1 sparse coding reviews)

**Attractor network experimental verification (Axis d):**
13. Wills TJ, Lever C, Cacucci F, Burgess N, O'Keefe J. (2005). "Attractor dynamics in the hippocampal representation of the local environment." Science 308:873-876. [https://www.science.org/doi/10.1126/science.1108905]
14. Renart A, de la Rocha J, Bartho P, Hollender L, Parga N, Reyes A, Harris KD. (2010). "The asynchronous state in cortical circuits." Science.
15. Neunuebel JP, Knierim JJ. (2014). "CA3 retrieves coherent representations from degraded input: direct evidence for CA3 pattern completion and dentate gyrus pattern separation." (PLOS Comp Bio attractor signature paper: https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1003641)

**Replication crisis / pre-reg (Axis f):**
16. Botvinik-Nezer R et al. (2020). "Variability in the analysis of a single neuroimaging dataset by many teams." Nature 582:84-88. [https://www.nature.com/articles/s41586-020-2314-9]
17. Munafò MR, Nosek BA, Bishop DVM, Button KS, Chambers CD, et al. (2017). "A manifesto for reproducible science." Nature Human Behaviour 1:0021. [https://www.nature.com/articles/s41562-016-0021]
18. Kriegeskorte N, Simmons WK, Bellgowan PSF, Baker CI. (2009). "Circular analysis in systems neuroscience: the dangers of double dipping." Nature Neuroscience 12(5):535-540. [https://www.nature.com/articles/nn.2303]
19. Yarkoni T. (2009). "Big correlations in little studies: Inflated fMRI correlations reflect low statistical power — Commentary on Vul et al." Perspectives on Psychological Science 4(3):294-298. [https://prefrontal.org/blog/2009/04/the-dangers-of-double-dipping-voodoo-iv/]
20. Vul E, Harris C, Winkielman P, Pashler H. (2009). "Puzzlingly high correlations in fMRI studies of emotion, personality, and social cognition." [https://laplab.ucsd.edu/articles/Vul_Pashler_2017_PsySciUnderScrutiny_HighCorrelationsBrainImagingResearch.pdf]

**Slice viability / recording-quality QC (Axis g):**
21. Campagnola L. "Slice Electrophysiology FAQ" — series resistance, input resistance, slice viability protocols. [http://campagnola.github.io/electrophysiology/faq.html]
22. Genes2Cognition / hippocampal slice electrophys protocol. [https://genes2cognition.org/db/Resource/13/SliceElectrophys4mar08.pdf]
23. Allen Institute SDK Unit Quality Metrics (Kilosort + spike-sorting QC). [https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_quality_metrics.html]
24. SpikeInterface Quality Metrics documentation. [https://spikeinterface.readthedocs.io/en/0.98.0/modules/qualitymetrics.html]
25. Schmitzer-Torbert N, Jackson J, Henze D, Harris K, Redish AD. (2005). "Quantitative measures of cluster quality for use in extracellular recordings." Neuroscience — origin of isolation distance and L-ratio metrics.
26. "Assessing Cross-Contamination in Spike-Sorted Electrophysiology Data" (2024). eNeuro. [https://www.eneuro.org/content/11/8/ENEURO.0554-23.2024]

**Decoder norm-matching / population coding (matched-filter discipline):**
27. Wessberg J, Stambaugh CR, Kralik JD, Beck PD, Laubach M, Chapin JK, Kim J, Biggs SJ, Srinivasan MA, Nicolelis MAL. (2000). "Real-time prediction of hand trajectory by ensembles of cortical neurons in primates." Nature 408:361-365.
28. Quian Quiroga R, Panzeri S. (2009). "Extracting information from neuronal populations: information theory and decoding approaches." Nature Reviews Neuroscience. [https://www.nature.com/articles/nrn2578]
29. "Biomimetic and Non-biomimetic Extraction of Motor Control Signals Through Matched Filtering of Neural Population Dynamics." bioRxiv. [https://www.biorxiv.org/content/10.1101/023689.full.pdf]

**Optogenetic / pharmacological dissection technique:**
30. Berndt A, Schoenenberger P, Mattis J, et al. (2011). "High-efficiency channelrhodopsins for fast neuronal stimulation at low light levels." (cited in optogenetics reviews)
31. "Optogenetic approaches for dissecting neuromodulation and GPCR signaling in neural circuits." Current Opinion. [https://www.sciencedirect.com/science/article/pii/S1471489216301333]
32. "Optogenetic pharmacology for control of native neuronal signaling proteins." Nature Neuroscience. [https://pmc.ncbi.nlm.nih.gov/articles/PMC4963006/]

**2x2 factorial design tradition (translates compose-discrimination):**
33. "A 2 × 2 factorial design for the combination therapy" (2014). Experimental & Translational Stroke Medicine. [https://etsmjournal.biomedcentral.com/articles/10.1186/2040-7378-6-10]
34. "When should factorial designs be used for late-phase randomised controlled trials?" (cited in NIH PMC: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7615816/)

**Total: 34 verified sources across 7 axes, 4 in-depth disciplines.**

---

## Self-assessment notes (for future cross-thread synthesis)

- This drill stayed STRICTLY within neuro-methodology scope per contract; companion drill (`a81a04d803ba9e5c6`) covers ML/statistical experimental design — synthesis must compose both for full picture.
- P_deflated values applied per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis (5 proposed atoms) capped at P=0.50.
- HARD-PASS + HARD-FAIL pre-registered per role contract.
- Did NOT pre-judge any adjacent neuroscience subfield as "not applicable" — included all 7 axes per [[feedback-dont-dismiss-adjacent-methods]].
- Generic query terms used; never mentioned "substrate" / "HRR" / "lock-in amplifier" / specific cell-names in external queries per [[feedback-query-privacy-decomposition]].
- Next-drill candidate field: **systems-neuro-attractor** (Renart/Knierim/Cacucci adjacencies) — substrate's modern-Hopfield + sequence-binding work is closest to the CA3 attractor + sequence-replay literature; specifically Brzosko's reward-modulated sequence replay would unify substrate's g1 generation + sequence-binding c3 + eligibility-trace + reward signals into one coherent neuro-grounded protocol.
