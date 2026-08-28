# Deep brain-foundational drill: how does the brain ACTUALLY run graded competition in parsing + role binding?

Owner-requested deeper drill (2026-08-27, "make this as brain foundational as it can be — run another deeper
drill"). Routed to the `research` agent, which fanned out FOUR parallel primary-source literature scans
(dynamics/settling-vs-racing; difficulty currency; good-enough parsing/underspecification; neural localization
of attachment vs role binding). Findings are persisted here VERBATIM-faithful with citations and
PINNED / UNDER-DEBATE tags. The four scans CHANGED the mechanism in three load-bearing ways (folded into
`experiments/exp_graded_competition_parsing_role_v1.py`); those changes are listed at the bottom.

---

## DRILL 1 — the DIFFICULTY CURRENCY (is "cycles-to-settle / margin" the right difficulty signal?)

**McRae, Spivey-Knowlton & Tanenhaus (1998), JML 38(3):283–312 — PINNED (primary-source verified, 2 mirrors +
author's 2013 chapter).** The competition-integration / **normalized-recurrence** model's **number of
cycles-to-criterion IS its processing-time proxy**: *"Processing time is assumed to be a linear function of the
duration of competition"* (p.287); *"Cycles of competition were mapped onto differences in reading times"*
(p.297). Mapped to human RT via a **linear transform of condition means** (no per-item r/R² reported). A
"dynamic criterion" (Eq.7) relaxes the settling threshold as cycles accumulate so competition doesn't run
forever. **→ our cycles-to-settle readout is the literature-standard RT proxy; it is a legitimate,
brain-faithful difficulty signal (used as a corroborating, settling-view secondary).**

**Levy (2008), Cognition 106(3):1126–1177 — PINNED (primary-source verified, full derivation).** The formal
difficulty currency of a genuinely graded model: comprehension = *"placing a probability distribution over"*
the possible structures; processing difficulty (surprisal) is **proven equal to the KL-divergence (relative
entropy) between the distribution before and after each word**, `D(P_{i+1} || P_i) = −log P_i(w_{i+1})`, an
**exact equivalence under full parallelism**. Facilitative-ambiguity effects (ambiguous read FASTER than either
disambiguation) specifically **require the distribution to remain multi-valued** and are mispredicted by
serial argmax-and-reanalyse models. **→ the ENTROPY of the maintained distribution is the pinned,
dynamics-agnostic difficulty currency; adopted as our PRIMARY signal.**

**DDM / accumulator applications to reading — SEARCH-BASED NEGATIVE.** No classical Ratcliff DDM has been fit
to word-by-word self-paced-reading / eye-tracking reading time. Closest: **SEAM (Rabe, Paape, Mertzen,
Vasishth & Engbert 2023, JML)** links Lewis-Vasishth retrieval activation to a threshold-crossing transition
rate (DDM-adjacent, not a classical Wiener diffusion). **O'Leary et al. 2025 (Mem&Cog)** fits a real DDM to
thematic-role-reversal PLAUSIBILITY JUDGMENTS (an offline decision, not online reading). E-Z Reader draws each
stage duration as a single Gamma deviate (not accumulation); SWIFT has noise-driven activation but a separate
random saccade timer. **→ no accumulator has been validated on the online sentence-difficulty measure we care
about; cycles/entropy on a settling/distribution model is as pinned as anything available.**

---

## DRILL 2 — the DYNAMICS (settling vs racing: which competition dynamics is most brain-faithful?)

**The settling-vs-racing fork is REAL and, for sentence processing, NEURALLY UNRESOLVED — the single most
important fidelity finding of the whole drill.**

- **Settling family** (mutually-coupled relaxation to a shared fixed point): Spivey-Knowlton **normalized
  recurrence** (McRae 1998, multiplicative normalize→integrate→feedback, ~20–40 cycles); **interactive
  activation** (McClelland & Rumelhart 1981 shunting update; McClelland et al. 2014); **self-organized parsing
  / GSC** (Tabor & Hutchins 2004 "digging-in"; Cho, Goldrick & Smolensky 2017 gradient symbolic — SPECULATIVE,
  equations unverified in scan).
- **Racing family** (accumulate to individual/absolute thresholds): **DDM** (Ratcliff 1978); **Leaky Competing
  Accumulator** (Usher & McClelland 2001); **ACT-R retrieval** (Lewis & Vasishth 2005).

**Key verified facts:**
1. **LCA formally subsumes both race and diffusion** (Usher & McClelland 2001, primary-source): `k=β=0` → the
   independent race model; `k=β` (net differential leak `K=0`) → the classical diffusion process. LCA is
   **PINNED for perceptual choice** (LIP/FEF ramping correspondence) but **UNTESTED for language**.
2. **Lewis-Vasishth cue-based retrieval IS A RACE, not settling** — the authors' own words: *"realizing a
   simple race model of ambiguity resolution."* Each chunk's activation `A_i = B_i + Σ W_j S_ji` (Eq.2) has
   **no term coupling it to a competitor's real-time state**; selection is a static max-A comparison; latency
   `T_i = F·e^{−A_i}` (Eq.4). Nicenboim & Vasishth (2018) reformalize it as a **"lognormal race of
   accumulators"** (ballistic — single between-trial noise draw, no within-trial diffusion).
3. **Normalized recurrence (our settling readout) is UNDER-DEBATE**: good behavioural fit, never neurally
   tested; inherits only the general (not mechanism-specific) plausibility of the interactive-activation family.
4. **No family has been neurally validated for sentence-level syntactic/thematic ambiguity.** The decisive
   discriminating test in the perceptual-choice literature (full RT-distribution shape / single-trial ramping,
   e.g. the CPP) has **never been run on garden-path / PP-attachment data.** The dominant sentence-level neural
   evidence is averaged ERPs (N400/P600), not accumulator ramps.

**→ IMPLICATION (load-bearing): the competition DYNAMICS is a genuinely open, neurally-unresolved fork. The
brain-faithful move is therefore NOT to commit to one dynamics as "the" mechanism, but to report a
dynamics-AGNOSTIC signal (the distribution's entropy, which is a property of the activation distribution, not
of any settling/racing process) as PRIMARY, and to show it agrees with BOTH a settling readout (normalized-
recurrence cycles) AND a race/distribution readout (softmax entropy). Our cell reports both, and they agree —
so the difficulty result is robust to the unresolved fork. Do NOT claim normalized-recurrence settling is
pinned; it is one defensible readout among an unresolved family. LCA is the most neurally-pinned dynamics (in
perceptual choice) and the natural successor build if a dynamics commitment is ever needed.**

---

## DRILL 3 — ARGMAX vs a MAINTAINED DISTRIBUTION (does the brain collapse to one answer?)

**"argmax = the noise→0 limit, graded is faithful only in the noise>0 regime" is HALF WRONG.** The weight of
primary evidence: the maintained state during normal incremental comprehension is **typically the
graded/distributed representation itself**; collapse-to-one-answer is a **separate, later, often
TASK-CONTINGENT** operation.

- **Swets, Desmet, Clifton & Ferreira (2008), Mem&Cog 36(1):201–216 — PINNED (primary-source verified).** RC-
  attachment ambiguity is **underspecified by default and resolved only when the task presses**: the ambiguity
  advantage (ambiguous read faster) appears under superficial questions but disappears/inverts when readers
  expect attachment questions; **even then, questions about ambiguous sentences are answered SLOWER** (~2960ms
  vs ~2660/2350ms), proving the online parse did NOT commit to a determinate attachment. Verbatim: *"the human
  sentence parsing system underspecifies attachment decisions … until it is either able or pressed to make a
  firm decision."* **→ argmax is a later, task-triggered decision layered on a default graded/underspecified
  state — exactly the reframe adopted.**
- **Levy (2008)** (above): the parser's state IS the probability distribution, consumed downstream via the
  surprisal it induces; argmax/single-parse is an approximation that only holds when the distribution is sharply
  peaked. Facilitative ambiguity REQUIRES the multi-valued distribution.
- **Spivey, Tanenhaus, Eberhard & Sedivy (2002), Cog Psych 45(4):447–481 — PINNED.** Visual-world eye-tracking
  shows **continuously-varying, simultaneously-active partial commitment to multiple candidates WITHIN a trial**
  (smooth fixation-proportion curves), not per-trial all-or-nothing.
- **Frazier & Clifton Construal** — primary (argument) relations resolved immediately by discrete preference;
  **non-primary (adjunct) relations left genuinely underspecified** until thematic/pragmatic info resolves them.
- **HONEST SECOND FAILURE MODE — Ferreira good-enough (2003; Ferreira & Patson 2007) — PINNED.** A shallow
  heuristic (NVN = agent-verb-patient) computes ONE systematically-WRONG reading (81% passive accuracy vs 99%
  active), NOT a noisy sample from the correct posterior. Ferreira & Patson explicitly REJECT the
  maintain-all-in-parallel camp as "unbounded rationality." **→ a pure "graded distribution + argmax" model
  does NOT reproduce Ferreira's systematic mis-parses; that needs a separate shallow-heuristic channel. This is
  named honestly as a limit of our model (and of the whole graded-parallel family).**

**→ IMPLICATION: reframe the native output as the MAINTAINED DISTRIBUTION (softmax over candidate activations),
consumed downstream; the discrete organ's argmax is a task-triggered COLLAPSE, not the default readout. Entropy
of that distribution = difficulty. This is strictly more faithful than "argmax==discrete at noise→0" — and it
is now the cell's framing.**

---

## DRILL 4 — ARE ATTACHMENT AND ROLE BINDING THE SAME OPERATION? (neural localization)

**Same computational PRINCIPLE (graded, cue-based, content-addressable retrieval/competition), but NOT one
literal shared pool — anatomically, temporally, and behaviourally dissociable.**

- **Matchin & Hickok (2020), Cerebral Cortex 30(3):1481–1498 — PINNED.** Three-plus-system model: **pMTG** =
  hierarchical lexical-syntactic structure-building; **ATL** = entities; **angular gyrus** = events/thematic
  relations (AG activation scales with argument-structure complexity, *"in the AG but not the ATL"*); pIFG =
  morpho-syntactic linearization. Structure-building and thematic/event representation are **functionally and
  anatomically distinct**.
- **Beber et al. (2025), Brain Communications 7(2):fcaf093 — CONTESTED CITATION (do NOT treat as
  load-bearing).** The neural-localization scan retrieved it with a specific DOI/PMC (PMC11930358), author
  list (Beber, Capasso, Maffei, Tettamanti, Miceli), and VLSM design (33 aphasia patients; morphosyntax →
  IFG/MFG/precentral; thematic-role assignment → angular + supramarginal gyrus, posterior STG, superior
  parietal). A SECOND, independent citation-verification scan searched author/title/topic and found NOTHING,
  flagging possible fabrication. UNRESOLVED here. A specific-DOI presence-claim for a very recent (2025) paper
  outranks a search-based absence-claim (recent papers are routinely missed by search), but per the caveat
  discipline the separate-pools conclusion below does NOT rest on Beber — it is independently supported by
  Matchin & Hickok 2020, Friederici 2011, and the eADM (all primary-source verified). Cite Beber only with
  this caveat until the DOI is checked first-hand.
- **Bornkessel-Schlesewsky & Schlesewsky eADM (2006/2016) — PINNED.** The most explicit rejection of "same
  operation": **dorsal stream = order-dependent SEQUENCING** (attachment-like); **ventral stream =
  order-independent DEPENDENCY/unification** where *"different participants (arguments) compete for the actor
  role … resolved via a set of cues (prominence features)"* (animacy, order, case, agreement — the Competition
  Model, graded cue-weighted competition). Two separable streams, different combinatorial primitives.
- **Friederici (2011, Physiol Rev 91(4)) — PINNED.** Dorsal pathway (complex syntax/movement) vs ventral
  (verb-argument/semantic integration); thematic role assignment sits at the BA44/45 OVERLAP; three temporal
  phases (Phase 1 local structure-building ELAN, Phase 2 thematic-role assignment LAN/N400, Phase 3 integration
  P600) — temporally/functionally dissociated.
- **Cue-based retrieval interference is a shared ALGORITHM-CLASS across dependency types** (Van Dyke & McElree
  2006/2011; Dillon et al. 2013; Glaser et al. 2013 fMRI: BA44 syntactic interference / BA47 semantic / BA45
  both / left STG both) — BUT the interference profile is **dependency-type-specific** (agreement shows
  facilitatory interference, reflexives don't; core-argument vs oblique distractors differ). Parker, Shvartsman
  & Van Dyke (2017) → a **"weighted cue-combinatorics scheme"**: one architecture, **dependency-type-specific
  cue weights**.

**→ IMPLICATION: model attachment and role binding as SEPARATE competitive pools that share the same activation-
function FORM (and may share code/parameters as a starting point) with dependency-specific cue weights — NOT one
pool where structural heads and thematic fillers literally compete. Our cell keeps them as two argmax
DIRECTIONS over the same activation form but is framed as two pools, and reports that the learned cue weights
are the shared substrate, not a single competition. Claiming "one literal shared pool" would be a conflation the
anatomy/timing/behaviour argue against.**

---

## WHAT THE DRILL CHANGED IN THE MECHANISM (folded into the cell)

1. **Difficulty currency → the maintained-distribution ENTROPY (Levy 2008) as PRIMARY**, with normalized-
   recurrence cycles-to-settle (McRae 1998) as a settling-view CORROBORATION. Reporting both spans the
   neurally-unresolved settling-vs-racing fork, and they agree.
2. **Reframed argmax as a TASK-TRIGGERED COLLAPSE (Swets 2008), not the default output.** The native output is
   the distribution; the discrete organ reads out only its argmax and discards the rest. "argmax==discrete at
   noise→0" is kept as a mathematical fact but is no longer the fidelity claim.
3. **Attachment and role binding kept as SEPARATE pools sharing the activation FORM with dependency-specific
   cue weights (Beber 2025; eADM; Parker/Van Dyke 2017)** — not one literal competition pool.

## HONEST LIMITS THIS DRILL ESTABLISHED (named, not hidden)
- The competition DYNAMICS is neurally UNRESOLVED for sentence processing; no dynamics is pinned. We report a
  dynamics-agnostic signal and flag this.
- A pure graded-distribution+argmax model does NOT reproduce Ferreira's systematic good-enough MIS-parses
  (NVN capture); that is a second, partially-independent failure mode needing a separate shallow-heuristic
  channel — out of scope here, flagged for the audit.
- MacDonald, Pearlmutter & Seidenberg (1994) and Frazier & Clifton Construal (1996) primary PDFs were not
  fetchable; triangulated via three primary sources that quote them directly. Bogacz et al. (2006) LCA/DDM
  unification verified instead against Usher & McClelland (2001) primary text.

---

## FINEST-RESOLUTION DRILL (owner-requested 2026-08-27, "as brain foundational as it can be; do we understand the limits and WHY")

A second, finer drill (4 more parallel primary-source scans + a citation-verification pass) probed the exact
combination rule, difficulty currency, why-accuracy-ties, and predictive-coding subsumption. It VALIDATED the
core mechanism as pinned-Bayesian and CORRECTED two framings. Verbatim-faithful:

**A. THE CUE-COMBINATION RULE — PINNED, and our choice is the exact Bayesian posterior (not a stand-in).**
Our additive-log-activation → softmax IS naive-Bayes / FLMP multiplicative cue integration in LOG coordinates —
an *exact algebraic identity*, not an analogy. **McClelland (2013, Frontiers in Psychology 4:503, primary-
verified):** softmax units *"can exactly compute Bayesian posterior probabilities"* when `net_i = log P(h_i) +
Σ_j log P(e_j|h_i)`, output `= softmax(net_i)`. Corroborated by Bishop PRML §4.2 and Ng & Jordan (2001/2002)
generative-discriminative pair. **Massaro & Friedman (1990) FLMP** multiplicative-truth-value-then-normalize
`P = a·v / [a·v + (1−a)(1−v)]` COINCIDES with softmax-of-log-likelihoods when cues are independent — they are
the same operation, not rivals. **The genuine rival is Ernst-Banks (2002) / Körding-Wolpert (2004) MLE LINEAR
averaging in RAW (non-log) cue-estimate space — but that is for CONTINUOUS variable estimation (depth,
position), NOT discrete hypothesis selection.** Our task is discrete selection over candidate tokens, so the
log-linear/softmax family is the correct one and the raw-linear MLE does not apply. **→ the combination rule is
brain-faithful (the pinned Bayesian posterior for discrete cue integration); only the DYNAMICS that computes it
(one-shot softmax vs normalized-recurrence SETTLING, McRae 1998) is the unresolved fork — Movellan & McClelland
(2001) show settling is only CONDITIONALLY equivalent to the log-linear family (noisy sigmoid, no pathological
self-feedback). We report both readouts, consistent with this.**

**B. THE DIFFICULTY CURRENCY — point entropy is the RIGHT currency for ERROR-flagging, and that use is NOVEL.**
Three distinct currencies: SURPRISAL (Hale 2001; Levy 2008 = backward-looking −log P(w|prefix) = KL update);
ENTROPY-REDUCTION (Hale **2003**, JPR 32:101–123 — NOT 2006; before-minus-after entropy delta); POINT/single-
step ENTROPY (uncertainty of the immediate choice). **For predicting READING TIME, surprisal and entropy-
reduction are the established currencies; POINT entropy is the weakest** — significant in Roark et al. (2009,
syntactic predictive entropy) but NOT significant anywhere in Linzen & Jaeger (2016, single-step entropy). Frank
(2013) finds surprisal and entropy-reduction statistically separable but not cognitively distinct. **BUT our
claim is NOT reading time — it is flagging WHERE the DISCRETE decision ERRS. For that, point entropy of the
decision's OWN posterior is the principled currency: P(argmax wrong) rises monotonically with the posterior
entropy.** A dedicated search found **NO prior human-comprehension paper using entropy to flag comprehension
ERROR location** (all prior entropy work calibrates against RT); this use is standard in ML confidence
estimation but NOVEL to psycholinguistics. **→ our point-entropy-as-error-flag is a genuine, principled
synthesis for the right target; surprisal/entropy-reduction (the RT currencies) are complementary and untested
here — named as such.**

**C. WHY GRADED TIES DISCRETE ON ACCURACY — a THEOREM, not a limit; and the cross-linguistic target CORRECTED.**
**MAP-optimality is PINNED (Bishop PRML §1.5, primary-verified):** under 0-1 loss, argmax of the TRUE posterior
minimizes expected error. So a graded model's argmax IS the accuracy-optimal readout of its own distribution —
**graded competition CANNOT beat its own argmax on gold accuracy by construction.** The unique value of graded
competition is the DISTRIBUTION (uncertainty / difficulty / underspecification), never the point estimate. Scope
caveats the theorem carries (all satisfied here): same-information access, calibration, finite-sample noise, and
— caveat 4 — the heuristic being itself near-Bayes-optimal for the narrow input distribution (our discrete
resolver already encodes the near-optimal conditional structure, so the tie is over-determined). **CROSS-
LINGUISTIC CORRECTION (MacWhinney, Bates & Kliegl 1984, JVLVB 23:127–150, primary-verified):** the naive "rigid
word order → single cue; free order → multi-cue" dichotomy is WRONG. English word order is near-categorical
(50% of interpretive variance; 93% NVN even against competing cues), but ITALIAN (freer order) is ALSO single-
cue-dominated (agreement, 54% variance). **Multi-cue integration wins on ACCURACY specifically where NO single
cue reaches near-ceiling validity — the genuine case is GERMAN, whose case cue is ~50% AMBIGUOUS.** So the
correct target population for a graded ACCURACY win is "no single cue near-ceiling reliable" (genuinely balanced
cue-conflict), NOT "freer word order." **English word-order dominance is a correctly-inherited INPUT FACT, not a
model deficiency.**

**D. PREDICTIVE CODING — a different Marr LEVEL, not a rival; precision = softmax temperature (applicable-to-
parsing UNDER-DEBATE).** Parsing-as-Bayesian-posterior-inference in a hierarchical generative model (Friston
2010; Kuperberg & Jaeger 2016, primary-verified — frames comprehension as multi-level probabilistic inference
and discusses reliability-weighted belief updating, though not the FEP term "precision") is an ALGORITHMIC/
implementational elaboration of the same computational-level problem, not a competing mechanism (Ohams et al.
2026 JML explicitly uses Marr's levels this way). **Precision = inverse softmax temperature is PINNED in active
inference (Friston et al. 2017 "Active Inference: A Process Theory") but has NO documented instantiation for
competing parses/cues** — applying it to parsing is a defensible extrapolation, not a documented result. **→ our
fixed softmax gain COULD be a cue-reliability / PRECISION-modulated gain — a faithful refinement that matches the
project's existing per-verb precision-weighting (predictive reader SOLVED). A genuine, small mechanism gap.**

**CITATION HYGIENE from the verification pass:** "Beber 2025" is CONTESTED (see DRILL 4 caveat) — do not rely on
it. "eADM" = Bornkessel-Schlesewsky & Schlesewsky *extended Argument Dependency Model* (Psych Review 2006),
cited correctly here. Hale entropy-reduction = **2003** (JPR), not 2006. "MacDonald, Trueswell & Tanenhaus 1994"
does not exist (a conflation of MacDonald/Pearlmutter/Seidenberg 1994 + Trueswell/Tanenhaus/Garnsey 1994) — this
note cites MacDonald/Pearlmutter/Seidenberg 1994 correctly.

## THE RESIDUAL-GAP LEDGER (do we understand the limits and WHY? — yes; each classified)

| residual gap (not fully brain-faithful) | classification | why / most brain-faithful next operation |
|---|---|---|
| graded does NOT beat discrete on gold ACCURACY | (i) THEOREM + input fact | MAP-optimality: argmax IS accuracy-optimal; graded's value is the distribution, not the point estimate. English word-order dominance (93%) is correctly inherited. NOT a deficiency. |
| accuracy win reserved for "no-single-cue-near-ceiling" populations | (i) input fact | Competition Model cue-validity: test on German-style ~50%-ambiguous-case data, not "freer word order" per se. A population choice, not a model fix. |
| the coarse 12-dim grounded space caps the thematic-fit cue | (ii) representation (p1) | the recency/thematic cue's learned validity is low here; a richer grounded space (p1) would raise it. Same p1 coupling the whole substrate has. |
| point entropy is the weakest RT currency | (ii)/(scope) | correct currency for ERROR-flagging (our target), not RT. For an RT signal, add surprisal (Levy) / entropy-reduction (Hale 2003). Complementary, untested. |
| fixed softmax gain (not precision/cue-reliability modulated) | (iii) mechanism gap | make the gain a Friston precision term (cue-reliability-weighted); reuse the predictive-reader precision-weighting. Small, faithful, buildable. |
| argmax output (not a maintained distribution consumed downstream) | (iii) mechanism gap | expose the full distribution + underspecification to downstream (Swets/Construal); resolve to one answer only under task pressure. |
| systematic good-enough NVN mis-parses not reproduced | (iii) mechanism gap | Ferreira's shallow-heuristic reading is a SECOND channel (systematically wrong, not noisy), which a graded-distribution+argmax model cannot produce. Add a shallow NVN channel. |
| settling vs racing DYNAMICS | (iv) neurally unresolved | no data adjudicates for sentence processing (LCA pinned only for perceptual choice). We report both readouts (cycles + entropy); LCA is the successor if a commitment is ever needed. |

**BOTTOM LINE ON FIDELITY:** the COMBINATION RULE is the pinned Bayesian posterior (not a stand-in); the
DIFFICULTY signal (point entropy for error-flagging) is the principled currency for our target and a novel
synthesis; the ACCURACY tie is a THEOREM, not a limit — we understand WHY it is what it is. The residual gaps
are: 3 correctly-inherited input/representation facts, 3 buildable mechanism refinements (precision gain,
distribution output, shallow-heuristic channel), and 1 neurally-unresolved fork we straddle by reporting both
readouts. Nothing is left silently on the table.

## RANKED brain-faithful build directions (most faithful first, for the strategy session)
1. **Distribution-entropy difficulty (Levy) as the shared surprisal currency** — DONE here; wire once as
   substrate difficulty infrastructure (relcl route-conflict / N400 / write-gating already consume a difficulty
   signal).
2. **Underspecification as a first-class output (Swets/Construal)** — expose the maintained distribution (not
   just argmax) to downstream, and resolve to one answer only under task pressure.
3. **LCA (Usher & McClelland 2001) as the successor dynamics** if/when a dynamics commitment is needed — it is
   the most neurally-pinned (perceptual choice) and subsumes race+diffusion; would natively yield decision-TIME
   as difficulty. NOT needed to clear the current bar.
4. **A separate shallow-heuristic (NVN) channel for Ferreira good-enough mis-parses** — a distinct failure mode
   the graded-parallel family does not cover.
