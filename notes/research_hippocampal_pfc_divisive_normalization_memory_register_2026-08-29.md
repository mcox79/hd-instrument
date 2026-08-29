---
topic: is pooled divisive normalization at a hippocampal/PFC working-memory register readout PINNED or OUR-EXTENSION-UNDER-TEST
requested_by: solver problem `read_terminal_bundle_stores_normalize_per_component_not_pooled` (2x/finer drill on the fidelity label carried in its SOLVED.md adjacent-component table)
date: 2026-08-29
lit_scan_lanes: 4 (Sonnet, parallel) + Sonnet-5 synthesis
calibration: lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis capped P<=0.50
prior_thread: notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md (PINNED decision-stage divnorm in LIP/OFC/MSTd; left memory-register application as OUR-EXTENSION-UNDER-TEST — this note drills specifically into that leftover gap)
---

# Research: divisive normalization at a hippocampal/PFC working-memory register — can it be upgraded to PINNED?

## HEADLINE

**No.** Across four independent lit-scan lanes and ~28 distinct sources (12 verified via fetched primary text), **no
paper directly measures or fits a Carandini-Heeger pooled-divisor equation against real hippocampal or prefrontal
population activity during multi-item working-memory maintenance or readout.** The claim stays
**OUR-EXTENSION-UNDER-TEST**, unchanged from both the parent register problem and the prior 2026-08-29 decision-stage
note — but this drill upgrades it from an *assertion* to an *exhaustively-searched absence*, and it identifies the
single concrete, cheap path to closing the gap: **a public, already-collected human intracranial dataset (Kamiński
et al. 2017 / Kyzar et al. 2024, DANDI #469) has exactly the right structures (hippocampus + medial-frontal cortex)
and the right independent variable (item load 1–3) to test it — nobody has yet fit the equation to it.**

Separately, the negative half of the drill (per-component instantaneous magnitude erasure) is **CONFIRMED refuted**:
no fast biological mechanism of that form was found anywhere in the literature searched. That OUR-INVENTION label
(already correctly assigned in SOLVED.md) is now backed by an explicit, targeted search across five different
mechanism classes, not just the Turrigiano citation alone.

## (b) Per-question findings

### Q1 — Hippocampus (CA3/CA1/DG): is pooled divisive gain control of ensemble magnitude MEASURED at retrieval?

**No.** The single strongest MEASURED candidate is **Bhatia, Moza & Bhalla 2019 (eLife 8:e43415, PMID 31021319,
HIGH confidence — fetched full text)**, which explicitly names and measures **"Subthreshold Divisive
Normalization" (SDN)** in CA1 pyramidal neurons via in vitro patch-clamp with combinatorial optogenetic CA3 input
stimulation: increasing excitatory drive shortens the E–I delay, producing a graded, continuous divisive
compression of subthreshold response. **But this is the wrong locus for the question**: it is a single-postsynaptic-
neuron, feedforward (CA3→CA1) mechanism driven by that cell's own local E/I timing — not a shared, population-wide
denominator computed from the summed activity of a retrieved ensemble, and not CA3 recurrent-collateral pattern
completion.

PV+ basket cell / gamma-locked inhibition literature (Freund & Buzsáki 1996; Freund 2007 *Neuron* review; Royer et
al. 2012 *Nat Neurosci*, PMID 22446878, MEDIUM; Stark et al. 2014 *Neuron*, MEDIUM) frames perisomatic inhibition as
rhythm/gain/rate control or ripple-amplitude shaping — real, measured, but never formalized as a pooled
Carandini-Heeger divisor. Dentate gyrus feedforward inhibition sparsifies via coincidence-detection/thresholding —
explicitly a winner-take-all mechanism, categorically distinct from graded divisive scaling.

On the modeling side, Treves & Rolls' classic CA3 autoassociative theory (Rolls 2013, *Front Cell Neurosci*,
PMID 23805074, HIGH — fetched) uses a qualitative **"global inhibition"** term to hold the retrieved "bubble" size
roughly constant — conceptually the closest existing hippocampal use of a pooled feedback signal — but it is stated
only qualitatively, with **no formal divisive equation and no recording data cited**. A 2025 paper (Kim & Kim, PLOS
Comput Biol 21(7):e1013267, HIGH — fetched) **explicitly argues the field should move away from this
global/pooled-inhibition assumption**, replacing it with assembly-selective inhibition learned via heterosynaptic
plasticity — a modeling-trend headwind against the pooled hypothesis, not just an absence of support.

**Verdict Q1: no measured pooled divisor controlling retrieved-ensemble magnitude in CA3/CA1/DG.** Closest analog
(Bhatia 2019) is measured but wrong locus (single-cell, feedforward, not recurrent-ensemble).

### Q2 — Prefrontal cortex: is divisive normalization MEASURED at WM maintenance/readout?

**Standard modeling choice, not directly measured.** Current resource-model theory explicitly uses the
Carandini-Heeger pooled form as the capacity-limiting mechanism: **Schneegans, Taylor & Bays 2024 (eLife 91034,
HIGH — fetched)** implements the WM resource as **"a global divisive normalization that constrains total spiking
activity,"** and a related rate-distortion account (Sims-lab, eLife 79450, HIGH — fetched) derives a
"divisive-normalization-like regularization" from cross-item interference. **Both authors explicitly decline to
localize the mechanism to a circuit** — Schneegans et al. call it anatomically agnostic. *(Note: two lanes converged
independently on eLife ID 91034 but disagreed on the exact author byline — one reported "Schneegans, Taylor & Bays,"
the other "Tomić & Bays." The finding (explicit CH-form pooled-normalization capacity model, published 2024, eLife
91034) is corroborated by two independent searches; the precise author list should be re-verified before quoting
externally.)*

Wei, Wang & Compte 2012 (*J Neurosci* 32:11228, MEDIUM — paywalled) built an explicit network-wide-normalization
spiking model for multi-item WM fit to behavior, not validated against single-unit recordings. Wimmer et al. 2014
(*Nat Neurosci* 17:431, MEDIUM) validated a global-inhibition bump-attractor against real monkey PFC recordings —
but only for a **single** remembered item, not multi-item normalization.

The measured side: **Buschman, Siegel, Roy & Miller 2011 (PNAS 108:11252, MEDIUM — secondary-verified)** recorded
monkey LIP/LPFC/FEF simultaneously during multi-item change-localization and found target information "reduced in
all three areas when another object was added" — a real, graded, pooled-style suppression. But the original paper
does **not** use the term "divisive normalization" (later theoretical papers applied that label), and the effect is
strongest at **encoding**, not maintenance/readout. **Hahn, Balakhonov, Fongaro, Nieder & Rose 2021 (eLife 72783,
HIGH — fetched)** is the closest genuine quantitative test: 362 real spiking neurons in crow NCL (an avian
PFC-analog), fit with an explicit divisive-normalization-rule regression — a real fit to real spikes — but **in
crows, not primate/human PFC**, and it's a regression consistent with the rule, not a full parametric CH fit.

**Verdict Q2: divisive normalization is the field's standard theoretical account of WM capacity, and is invoked as
an interpretation of real load-dependent suppression (Buschman 2011) — but no study has directly fit the pooled
equation to primate/human PFC spiking data during WM maintenance or readout.** The one real spiking-data fit
(Hahn 2021) is in a non-mammalian PFC-analog.

### Q3 — Is theta-gamma serial readout (Lisman-Idiart) coupled to a pooled gain-control term?

**Not found — and this looks like a genuine, unfilled seam between two literatures that don't talk to each other,
not a documented negative.** Lisman & Idiart 1995 (*Science* 267:1512) and Lisman & Jensen 2013 (*Neuron* 77:1002,
"The Theta-Gamma Neural Code") define capacity purely as theta/gamma cycle-length ratio, with NMDA-mediated
activity-dependent depolarization doing the serial-item bookkeeping — no gain/divisor term anywhere in the model.
Axmacher et al. 2010 (PNAS 107:3228, MEDIUM) shows human hippocampal theta-gamma phase-amplitude coupling scales
with item count (measured) but reports no divisor. **Meltzer et al. 2008 (*Cereb Cortex* 18:1843, HIGH — fetched)
is a small but real complication**: gamma power *increases* with WM load rather than staying pooled/conserved —
mild evidence against (not fatal to, since power ≠ ensemble magnitude) a total-activity-conserving pooled gain
accompanying this specific readout.

The closest theoretical bridge that exists but has never been connected to this problem: **Heeger & Mackey 2019
(ORGaNICs, PNAS 116:22783, PMID 31636212, HIGH — fetched)** contains a literal pooled-divisor equation
(|y_j|² = |z_j|²/(σ² + Σ|z_k|²)) in a recurrent gain-control circuit that **also produces gamma-like oscillations as
an emergent property** — a plausible unification, built independently of Lisman-Idiart, never cited alongside it.
PING network models (shared inhibitory pool suppressing a whole ensemble) are the closest *biological* analogue to
a shared divisor, but formalized as winner-take-all/desynchronization dynamics, not a continuous divisive equation.

**Verdict Q3: the biology pairs serial phase-coded readout with interference-avoidance mechanisms (feedback
inhibition, NMDA-dependent facilitation, WTA) that qualitatively resemble "stay stable as load grows," but none are
formalized as a shared pooled divisor. This is an open theoretical seam (Heeger-Mackey's ORGaNICs is the nearest
existing bridge), not a refutation.**

### Q4 — Confirm/refute: is there ANY fast biological analogue to per-component instantaneous magnitude erasure?

**CONFIRMED — no counter-example found.** Turrigiano-style homeostatic synaptic scaling (Turrigiano 2008, *Cell*
135:422, MEDIUM-HIGH) is slow (hours–days) and explicitly *multiplicative*, preserving relative differences between
synapses rather than erasing them. Faster presynaptic homeostasis (Delvendahl, Kita & Müller 2019, PNAS 116:23783,
PMID 31685637, HIGH — fetched) operates on a minutes timescale — faster than classic scaling, but still nowhere near
sub-second, and it restores each synapse to *its own* compensatory set-point rather than performing an instantaneous
divide. Shunting inhibition / divisive normalization circuits (Prescott & De Koninck 2003, PNAS 100:2076, MEDIUM)
ARE fast (near-instantaneous, conductance-based) — but are always **pooled/shared**, one conductance dividing a
whole neuron's or population's response, never an independent per-channel rescale. Short-term synaptic
depression/facilitation is fast (ms) and genuinely per-synapse, but modulates release probability based on that
synapse's own recent history — a use-dependent gain change, not a magnitude-erasing snapshot divide. Photoreceptor
Weber-law light adaptation is per-cell and has a fast onset (~200–300ms) but full gain normalization completes over
seconds-to-minutes as temporal self-referencing to background, not an instantaneous cross-channel erasure.

**Verdict Q4: every fast biological mechanism found is either (a) a shared/pooled divisor across a population
(preserving relative structure) or (b) slow and structure-preserving. Nothing fast and per-component that erases
relative magnitude exists in the literature searched.** This directly strengthens (does not merely reconfirm) the
existing SOLVED.md/audit classification of per-component `S_i/|S_i|` renormalization as **OUR-INVENTION with no
biological analogue** — now backed by a targeted search across five distinct mechanism classes rather than the
single Turrigiano citation previously cited.

## (a) Verdict on the crux

**"Pooled divisive normalization at a hippocampal/WM memory-register readout" stays OUR-EXTENSION-UNDER-TEST.** It
cannot be upgraded to PINNED today. **The single most-relevant paper that would close the gap if the missing
analysis existed:** Kamiński, Sullivan, Chung, Ross, Mamelak & Rutishauser 2017 (*Nat Neurosci* 20:590, PMID
28218914, PMC5374017, HIGH — fetched), now with its full public dataset released as Kyzar et al. 2024 (*Sci Data*
11:89, PMC10796636, HIGH — fetched, DANDI dataset #469, NWB format, code on GitHub). This study already recorded
the right quantity (item-selective firing-rate magnitude vs. number of concurrently-loaded items, load 1–3) in
exactly the right structures (human hippocampus, amygdala, pre-SMA/dACC) in the same subjects — it is a measured
population-response-vs-load relationship sitting in a public repository, un-fit to any divisive-normalization
equation. **This is an open, actionable analysis gap, not a completed negative result** — which is why the verdict
is "still unpinned" rather than "refuted."

## (c) Cheapest experiment to close the gap

**Reanalysis, not a new experiment — genuinely cheap (public data + existing code, pure analysis, no wet-lab or
compute-heavy step):**

1. Pull the public NWB dataset (Kyzar et al. 2024, DANDI #469 — hippocampus, amygdala, pre-SMA/dACC, vmPFC; 21
   patients, 902 Sternberg-task neurons, load 1–3).
2. For each item-selective neuron, extract trial-level firing rate to its preferred item as a function of load.
3. Fit the Carandini-Heeger pooled form R = drive^p / (σ^p + Σ_j drive_j^p) with a **single shared σ across the
   array** (using Tomić/Schneegans-Bays 2024's behavioral divisive-normalization equation as the template) against
   three alternatives: (i) additive/identity-specific suppression, (ii) a hard-capacity-step model, (iii) a flat
   null.
4. Test the diagnostic **"iso-suppression" signature**: suppression of item A's response at a given load should be
   predicted by the *summed* drive of whichever OTHER items are co-loaded, independent of their specific identity —
   the defining property of a shared pooled divisor as opposed to identity-specific pairwise competition.

This is the cheapest possible test because the data collection is already done, is free and public, and the
missing step is purely a model-comparison analysis.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**On the reanalysis above:**
- **HARD-PASS** (upgrades hippocampal/PFC divisive-norm-at-readout toward PINNED): the shared-σ pooled form beats
  both alternatives by a pre-registered margin (e.g. ≥10% AIC/BIC improvement, or p<0.01 in a nested model
  comparison) AND the iso-suppression signature holds (identity-independent, summed-drive-predicted suppression) in
  a majority (>50%) of load-sensitive neurons, matching the fraction Kamiński et al. reported as load-modulated.
- **HARD-FAIL**: the pooled form does not outperform (or is statistically indistinguishable from) the additive or
  hard-capacity-step alternatives, OR suppression is dominated by identity-specific pairwise interactions rather
  than pooled summed drive. Either result REFUTES the pooled-divisor hypothesis at this specific readout and would
  move the classification from "unpinned, open" to "tested and refuted at this locus" (still not evidence that our
  substrate's register mechanism is wrong — only that this particular brain locus doesn't implement it this way).

**On the broader "is this even the right class of computation" question (softer, theory-level):**
- **HARD-PASS**: at least one future primate/human PFC or hippocampal single-unit study explicitly fits a
  Carandini-Heeger-form equation to multi-item WM maintenance/readout data and reports a statistically favored fit
  (this note found none as of 2026-08-29 — Hahn et al. 2021's crow-NCL fit is the closest, and is NOT in hippocampus
  or primate/human PFC).
- **HARD-FAIL**: five more years of resource-model literature continue to use divisive normalization as an
  anatomically-agnostic, unlocalized theoretical device (as Schneegans/Bays 2024 and the Sims-lab paper already do)
  without ever tying it to a recorded circuit — this would suggest the computation may be real at the
  behavioral/psychophysical level while the specific neural implementation remains genuinely different from V1/MT/
  LIP/OFC/MSTd's implementation (i.e., WM capacity limits could be implemented via a different biophysical
  mechanism that produces normalization-like behavioral signatures without a literal shared-divisor circuit).

## Cross-thread synthesis

This directly extends **notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md**, which PINNED pooled
divisive normalization at DECISION/combine populations (LIP, OFC, MSTd — three independent circuit families,
11 primary-verified sources) and left "at a hippocampal/WM memory register" as OUR-EXTENSION-UNDER-TEST. This drill
went specifically after that leftover gap with four dedicated lanes (hippocampus, PFC, theta-gamma coupling,
closest-candidate-paper) rather than re-running the decision-stage question, and the answer is a clean, well-searched
**"still no" with a named, concrete, cheap path to close it** — a materially stronger epistemic state than the prior
"no citation found" note, because it now rules out several plausible near-misses explicitly (Bhatia 2019's SDN is
measured but wrong locus; Buschman 2011's suppression is measured but at encoding and unlabeled by the original
authors; Hahn 2021's DNR fit is measured but in the wrong species/region) rather than simply reporting an absence.

It also connects to `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the register-norm general rule, corrected in the
solver's SOLVED.md): the audit's existing brain-fidelity labels ("pooled divisive normalization at a
decision/combine population = PINNED... at a hippocampal/WM memory register = OUR-EXTENSION-UNDER-TEST;
per-component magnitude-erasure = OUR-INVENTION, no fast biological analogue") are **reconfirmed by this drill and
should be considered more strongly evidenced** — the OUR-INVENTION label in particular moves from "one citation
checked" to "five mechanism classes checked, zero counter-examples."

## (d) Adjacent-component flags surfaced by this drill (new, beyond the prior note)

1. **CA3 attractor-cleanup fidelity direction, flagged against `script_grain_acquisition_loop`** (the on-disk
   organ SOLVED.md names as the unmeasured CA3-attractor-analogue, "iterative attractor... Hopfield cleanup for
   CA3/DG matching"). Kim & Kim 2025 (PLOS Comput Biol) argues the *current* computational-neuroscience trend is
   AWAY from global/pooled inhibition in CA3 models and toward **assembly-selective** inhibition learned via
   heterosynaptic plasticity. If `script_grain_acquisition_loop` is ever measured under load and found to need a
   divisive-style fix (per the register's proven pattern), the *higher-fidelity* 2025-literature-consistent design
   would be a **group-wise/assembly-selective pooled divisor** (one scalar per stored assembly/pattern) rather than
   one single global scalar over the whole store — a more refined target than what the register organ currently
   implements. Flag only; not measured, not built.

2. **Encoding-stage vs. read-terminal normalization — a scope gap in the whole `read_terminal_bundle_*` problem
   family.** Buschman et al. 2011's clearest MEASURED multi-item suppression effect in primate cortex happens
   mainly **at encoding** (when a new item is added to the display), not during later maintenance/readout. The
   entire SOLVED.md analysis (and the register problem before it) tested normalization only at the READ side of the
   register (`bundling.bundle` callers, cleanup/argmax/cosine consumers). **Nobody has asked whether the register's
   WRITE/accumulate step (`AccumulateRegister`'s encode path) needs its own gain control, separate from and
   possibly different in form from the already-validated read-terminal `divnorm`.** This is a genuinely new
   candidate problem this drill surfaces, not previously named in the register or read-terminal problem chains.

3. **The Schneegans/Bays-and-Wei/Wang/Compte theoretical consensus is good news, cautiously.** The fact that
   current state-of-the-art WM-capacity *theory* independently converges on "global divisive normalization" as the
   right computational-level account (even while declining to localize it anatomically) means the register organ's
   core computation (pooled divisive gain recovering an overloaded readout) sits in good theoretical company — this
   is evidence for "the right general class of computation," distinct from and weaker than "measured in this
   circuit." Keep this distinction sharp in any future write-up: computational-level support is real and
   citable; circuit-level support is not yet available.

## Substrate-product implications

- **No hdlab change indicated.** This drill does not overturn or add to the SOLVED.md per-caller table (register +
  multibank on divnorm; typer/goal_achievement/cosine consumers stay per-component) — it only sharpens the
  brain-fidelity LABEL underneath that already-landed decision, from "asserted OUR-EXTENSION-UNDER-TEST" to
  "exhaustively-searched, still-open OUR-EXTENSION-UNDER-TEST with a named path to close it."
- **Do not claim PINNED status for the register's divnorm mechanism in any future write-up** — the label stays
  OUR-EXTENSION-UNDER-TEST until a primate/human hippocampal or PFC dataset is actually fit to the pooled equation.
- **Candidate next problem (research-scope, cheap, external):** the Kamiński/Kyzar public-dataset reanalysis above.
  This is a literature/data-reanalysis task, not an hd-instrument compute experiment — it would inform the brain-
  fidelity LABEL, not the substrate's behavior, so it is lower priority than in-substrate measurement work unless
  the label itself becomes load-bearing for a bigger design decision.
- **Candidate next problem (build-scope):** the encoding-stage/write-path normalization gap named in (d)(2) above
  — genuinely unexplored, and unlike the read-terminal sweep (which came back mostly "no change needed"), this one
  has a measured primate correlate (Buschman 2011) suggesting it could be fruitful.

## Citations (verified count)

**~28 distinct sources identified across 4 lanes. 12 verified via fetched primary full text (HIGH confidence):**
Bhatia, Moza & Bhalla 2019 (eLife 8:e43415, PMID 31021319); Kim & Kim 2025 (PLOS Comput Biol 21(7):e1013267); Rolls
2013 (Front Cell Neurosci 7:98, PMID 23805074); Schneegans/Tomić, Taylor & Bays 2024 (eLife 91034 — author byline
uncertain between lanes, DOI/eLife-ID confirmed by two independent searches); Sims-lab 2024 (eLife 79450); Hahn,
Balakhonov, Fongaro, Nieder & Rose 2021 (eLife 72783); Lisman & Idiart 1995 (Science 267:1512); Meltzer et al. 2008
(Cereb Cortex 18:1843); Heeger & Mackey 2019 (PNAS 116:22783, PMID 31636212, PMC6842604); Delvendahl, Kita & Müller
2019 (PNAS 116:23783, PMID 31685637); Kamiński et al. 2017 (Nat Neurosci 20:590, PMID 28218914, PMC5374017); Kyzar
et al. 2024 (Sci Data 11:89, PMC10796636). **~16 MEDIUM-confidence** (search-snippet or secondary-source verified,
not independently fetched this pass): Royer et al. 2012; Stark et al. 2014; Freund & Buzsáki 1996 / Freund 2007;
Rich, Liaw & Lee 2014; Wei, Wang & Compte 2012; Wimmer et al. 2014; Buschman, Siegel, Roy & Miller 2011; Axmacher et
al. 2010; Lisman & Jensen 2013; PING network model literature (unspecified specific paper); Grabenhorst bioRxiv
2022; eNeuro 2023 spiking model (unspecified authors); Turrigiano 2008; Prescott & De Koninck 2003; Synaptotagmin-7
Sci Rep 2021; Boran et al. 2020/2022 (bioRxiv/NeuroImage); Hasselmo (multiple, ACh gain-control model line); Treves
& Rolls 1991; Norman & O'Reilly 2003. **Calibration penalty applied:** the absence-of-evidence verdict (Q1/Q2/Q3 —
"not directly measured at this locus") is well-supported by convergent, independently-run, primary-verified search
across 4 lanes — held at **P=0.72** (deflated from an intuitive ~0.90-0.95 "obviously nobody's done this specific
analysis," per [[feedback-lit-scan-calibration-penalty]], because absence-of-evidence claims in fast-moving
literatures always carry residual risk of a missed paper). The Q4 confirm (no fast per-component biological
analogue) is held higher, **P=0.80**, given it searched five mechanism classes with zero counter-examples and
directly reconfirms an existing on-disk classification rather than introducing a new claim. The adjacent-component
flags in (d) are **novel synthesis, capped at P<=0.50** per the standing calibration rule.
