# Research: correct neural computation + non-redundancy + integration rule for the 3 consolidation-gate signals

Director drill, 2026-07-16. Sharper follow-up to `research_consolidation_gate_quantitative_signals_2026-07-16.md`
("quantum drill" — delivered per-signal FORMS: surprise=saturating Hill, schema-fit=Tse 3h/48h gate, recurrence=
ACT-R power-law, combination=Friston precision-weighting) and directly informed by the now-LANDED
`ingest_gate_combination_rule_race_v1` FULL result (`data/exp_ingest_gate_combination_rule_race_v1/metrics.json`),
which empirically tested the Friston fast/slow decomposition and found it **fails** (verdict
`SCHEMAFIT_CARRIES_the_fix`). Three parallel Sonnet lit-scans (surprise-vs-rich-predictor; schema-congruence
pairwise-mechanism; recurrence + CLS routing-logic) + director synthesis reconciling both against the landed
numbers. Research-only: no code, no cell dispatched. Generic neuroscience/math terms only in all external queries.

## HEADLINE

**The brain's three consolidation signals are not redundant, and the landed empirical result is not a refutation of
the three-signal theory — it is a precise diagnosis of an IMPLEMENTATION ERROR in how "surprise" was computed,
exactly as the working premise predicted.** The race cell measured: `flat`(raw_PE alone)=0.542 (chance, confirms
v4), `schemafit_alone`=**0.836** (strong), `brain`(raw_PE·(1-schema_fit), Friston fixed-weight form)=0.530 (chance —
*worse* than schema_fit alone), `hybrid`(calibrated 2-track weights)=0.602, `learned`(calibrated 5-feature
logistic)=0.628. Multiplying a **chance-level** raw_PE into schema_fit did not add signal, it added noise. The
reason raw_PE is chance-level is now diagnosable from lit-scan #1 (below): our `raw_PE = 1 - reciprocal_rank`
is computed against a **flat, corpus-global** predictor (the additive_map's whole-vocabulary rank), which is the
computational analog of Rescorla-Wagner over undifferentiated stimuli — the brain does NOT compute surprise this
way. Every credible account of biological prediction-error (distributional dopamine coding, OFC "cognitive map of
task space", CA3-pattern-completion-vs-CA1-mismatch) computes prediction error against a **structured, locally
state-conditioned** prediction, not a global rank. In the substrate's own arena, "derivability" IS a local
2-hop-reachability question — so a surprise signal computed locally (relative to the same reachable neighborhood
schema_fit already scans) would have been schema-conditioned by construction, exactly matching what Bayesian
surprise (KL(posterior‖prior), prior=schema) already formalizes, and exactly matching why Itti & Baldi's Bayesian
surprise needs no separate multiplicative schema term — the schema **is** the prior it is measured against. The
race cell instead multiplied a **global**, schema-blind surprise proxy against schema_fit, which is a different,
weaker experiment than the theory calls for. **This is a fixable measurement error, not evidence that surprise is
dispensable** — Part A.1's non-redundancy argument below still holds: even a perfectly schema-conditioned surprise
signal is doing a categorically different job (flagging deviation-from-prediction) than schema-fit (structural
routing) or recurrence (temporal reliability), and dropping any one of the three has a distinct, named failure mode.

## Part A — the correct computation + non-redundant role, per signal

### A1. SURPRISE — measured against what predictor, and why it can't be dropped

**Correct computation.** The brain's prediction-error signals are computed against representations that are
markedly richer than a flat/global base-rate:
- Dopamine RPE is **distributional**, not scalar: VTA neurons show heterogeneous asymmetric scaling of
  positive/negative RPE consistent with each neuron encoding a different quantile of the future-reward
  distribution (Dabney, Kurth-Nelson, Uchida et al. 2020, *Nature* 577:671-675 — primary, mouse VTA
  single-unit recording, direct empirical test of a distributional-RL prediction).
- The **state** that RPE is computed against is itself an inferred, structured "cognitive map of task space",
  not raw stimulus features (Wilson, Takahashi, Schoenbaum & Niv 2014, *Neuron* 81:267-279, primary; Behrens,
  Muller, Whittington et al. 2018, *Neuron* 100:490-509, theoretical synthesis). Prediction error against a
  richer, structure-inferring state representation is qualitatively different from prediction error against a
  flat lookup table.
- The hippocampal comparator (CA1 mismatch of CA3-completed prediction vs. actual entorhinal input; Lisman &
  Grace 2005, *Neuron* 46:703-713, theoretical/primary hypothesis paper; Kumaran & Maguire 2006/2007, *J.
  Neurosci.*, primary fMRI) compares against a **CA3 pattern-completion output** — an attractor-network
  prediction built from the *specific local relational neighborhood* of the cue, not a corpus-wide statistic.
- **Important, recent complication (flag honestly):** Varga et al. 2025, *PNAS* 122(35):e2503535122 (primary,
  3-experiment fMRI) found hippocampal mismatch tracks violations of **specific episodic memories**, while
  violations of **generalized/schematic** predictions instead engage separate semantic-control/multiple-demand
  cortical networks. This directly complicates a simple "hippocampus = one schema-conditioned comparator" story
  — there appear to be **two separate comparator systems** (episodic/local vs. schematic/generalized), which
  independently supports a ROUTE architecture (Part B) rather than a single blended surprise computation.
- Bayesian surprise = KL(posterior‖prior) (Itti & Baldi, *Vision Research* 2009, primary, beats 10 other saliency
  metrics against human gaze data) is schema-conditioned **by definition** — the "prior" it is measured against
  is the observer's current structured model, functionally identical to "schema." No primary neuroscience paper
  measures a literal KL-divergence in single neurons (confirmed gap), but the formalism is the best-supported
  *theoretical* target for what a correctly-computed surprise signal should look like: not "is this observation
  rare in general" (Shannon surprise, corpus-wide), but "how much must I revise my LOCAL structured belief."

**Non-redundant role (why 3, not 1, even with a rich/schema-conditioned surprise).** Surprise's irreducible job is
to answer "does this deviate from my best current prediction, and by how much" — a magnitude-of-mismatch quantity.
Schema-fit answers a structurally different question ("if this needs filing, is there already a template to file
it in") and recurrence answers a third, temporal-reliability question ("has this been confirmed more than once").
Even a perfect schema-conditioned surprise signal cannot substitute for either: **failure mode of dropping
surprise entirely** — a schema-fit-only system (no error/deviation signal) treats every schema-congruent item as
equally worth encoding, indiscriminately re-encoding redundant repeats of already-well-predicted information (the
substrate's own "REDUNDANT batch -> SKIP" case) and, more importantly, has no mechanism to flag *specific*
departures from an otherwise-good template — it cannot distinguish "another boring instance of a known pattern"
from "this instance broke the pattern in a meaningful way," because that distinction is a magnitude-of-error
computation, not a structural-fit computation. McClelland, McNaughton & O'Reilly 1995 (*Psychological Review*
102:419-457, primary/theoretical) supplies the strongest argument for why surprise/error, however well computed,
still cannot alone decide the LEARNING-RATE regime (fast local update vs. slow interleaved) — that is schema-fit's
job (A2), and cannot decide RELIABILITY (recurrence's job, A3).

### A2. SCHEMA-CONGRUENCE — pairwise/relational, not node-generic; correct computation + non-redundancy

**Correct computation.** Every literature strand converges: schema-fit is computed as a property of the **specific
relational configuration** being evaluated, not as an aggregate of each element's individual familiarity/degree.
- CA3's recurrent-collateral autoassociative network implements pattern completion as **basin-of-attraction**
  behavior over the whole conjunctive input vector — completion succeeds when the specific *pairing/configuration*
  of cue elements falls inside a previously-stored attractor, not when either element alone is familiar (O'Reilly
  & McClelland 1994, *Hippocampus*, primary; Rolls & Kesner 2006, *Prog. Neurobiol.*, secondary review; Guzman et
  al./Neunuebel & Knierim, PLOS Comp Biol 2014, primary, empirically confirms attractor-basin behavior as a
  function of cue overlap with the stored configuration). Two individually-familiar, well-connected elements
  combined in a genuinely novel way land **outside** any stored basin — this is the direct mechanistic argument
  against a node-generic (degree/familiarity) proxy.
- Tse et al. 2007/2011 (*Science* 316:76-82; 333:891-895, both primary, exact stats obtained) operationally score
  congruency on the **specific new flavor-place pairing**, not on the familiarity of the flavor or place alone
  (both can be independently familiar/unfamiliar regardless of whether their *pairing* fits the schema).
- Gentner 1983 (*Cognitive Science* 7:155-170, primary) and Kemp & Tenenbaum 2008 (*PNAS* 105:10687-10692,
  primary) are explicit and formal on this point: analogical fit is scored on **relations**, not attributes, with
  systematicity (higher-order relations connecting the mapped relations) governing the judgment; structural-form
  inference formalizes fit-to-an-inferred-relational-graph-grammar, not node-marginal similarity.
- The formal network-science analogy (not neuroscience data, flagged as analogy only): degree/preferential-
  attachment link-prediction scores are blind to which SPECIFIC pair is queried and are reliably beaten by
  path/relation-based proximity measures (Adamic-Adar, Resource Allocation, Katz, personalized PageRank) —
  Liben-Nowell & Kleinberg 2007 (*JASIST* 58:1019-1031, primary) and Lu & Zhou 2011 (*Physica A* 390:1150-1170,
  secondary survey). This is the exact formal shape of the substrate's OWN diagnosed problem, independently
  confirmed same-day in `notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md`: the current
  `build_schema_fit` is a per-node aggregate percentile (`0.5*(reach_pct[h]+reach_pct[t])`), discarding the
  specific h-to-t relation — the fix (already proposed there, reusing the landed `SRColumnSolver` resolvent) is a
  **pairwise, multi-path-aggregating** score. That fix is orthogonal to and compatible with this drill's finding
  about surprise (A1) — both point the same direction: stop reading GLOBAL/node-level statistics, read the
  LOCAL/relational structure.

**Non-redundant role.** Schema-fit's irreducible job is ROUTING: deciding how cheaply a flagged item can be
assimilated (does existing structure already have a slot). **Failure mode of dropping it** (surprise+recurrence
only): every reliably-repeated surprising item is treated identically regardless of whether it fits known
structure, forcing either blanket costly full restructuring (catastrophic-interference risk — McClelland 1995's
central argument against unmediated fast learning of novel structured associations into an overlapping network)
or blanket cheap slot-filling (which corrupts structure when an item genuinely does not fit any template, forcing
schema-violating exceptions into the wrong slot).

### A3. RECURRENCE — reliability/precision accumulation, and why it is not sign-flippable

**Correct computation.** Synaptic tagging and capture (STC; Frey & Morris 1997, *Nature* 385:533-536, primary;
Redondo & Morris 2011, *Nat. Rev. Neurosci.* 12:17-30, secondary review) gives the exact mechanistic reason
recurrence must be a *separate* signal: potentiation-induction sets a short-lived, protein-synthesis-independent
"tag," but durable change requires a **second, independent step** — capture of separately-synthesized
plasticity-related proteins, which can be supplied by repetition (or, separately, by a strong salience/arousal
signal — the amygdala one-shot bypass for flashbulb-type memories). Tag-setting and tag-capture are dissociable
processes; this is the mechanistic basis for a graded, accumulating "local precision" that rises with confirmed
repetition (matching both ACT-R's `B_i = ln(sum_j t_j^-d)` power-law and conjugate-Bayesian precision
accumulation — no hard floor in the literature, per the quantum drill). Cepeda et al. 2006/2008 (*Psych. Bull.*
132:354-380; *Psych. Science*, primary meta-analyses) confirm recurrence's spacing-driven benefit is measured
purely from presentation timing, independent of any surprise or schema-fit manipulation — direct empirical
support that recurrence is a genuinely orthogonal axis, not a relabeling of the other two. Sign is unambiguous and
never flips in the primary literature: more (well-spaced) recurrence -> monotonically more durable consolidation;
what is NOT graded is the *interaction* with novelty — a single very-high-salience event (amygdala/arousal
pathway) can skip the repetition requirement entirely, which is a distinct BYPASS branch, not evidence recurrence
is reversible or unnecessary in the general case.

**Non-redundant role.** Recurrence's irreducible job is a temporal-RELIABILITY check, independent of both
deviation-magnitude (surprise) and structural fit (schema). **Failure mode of dropping it** is the single most
dangerous of the three: a noisy/hallucinated/one-off event that happens to be BOTH surprising and well-fit to an
existing schema template — precisely the combination that would otherwise route to FAST, cheap, durable
consolidation — gets encoded on n=1 evidence with no chance to be disconfirmed by a second sample. This is exactly
the vulnerability STC's tag/capture separation structurally prevents (a tag alone, without capture, decays back to
baseline).

## Part B — the integration rule: gate, sum, or route? (grounded in the landed empirical result)

**Lit-scan verdict:** CLS itself is NOT a blended/weighted-sum system — McClelland, McNaughton & O'Reilly 1995 is
explicitly ANATOMICAL: hippocampus and neocortex are architecturally separate systems with fixed, different
learning-rate regimes, motivated directly by avoiding catastrophic interference (an argument *against* a single
shared/blended computation). Tse et al.'s 3h-fail/48h-pass transition is a near-step-function, not a smooth
gradient. Kumaran, Hassabis & McClelland 2016 (*Trends Cogn. Sci.* 20:512-534) incorporates schema-congruence as
a rate-modulator that lets congruent items largely bypass the slow route, but — confirmed independently a THIRD
time across three separate lit-scans now (quantum drill: 2x; this drill: 1x) — **no paper states a formal
multiplicative/additive/branching equation combining all three signals.** The best-supported reading is a
**discrete branch/route**, not a gate (single AND-threshold) and not a sum (continuous weighted blend):
1. Recurrence/salience acts as an upstream RELIABILITY GATE (bypassable by high-arousal one-shot salience) —
   this is itself a 2-way branch (repetition-gated capture vs. amygdala one-shot override), not a smooth precision
   multiplier in the general case.
2. Items that pass the reliability gate are ROUTED, not summed, into fast-cortical vs. slow-hippocampal-interleaved
   processing, keyed on schema-fit — and the Varga et al. 2025 dissociation (episodic/local mismatch vs.
   schematic/generalized violation recruiting *separate* neural systems) is independent, more recent evidence for
   a literal architectural route rather than one comparator computing one blended number.

**Reconciling this with the empirical race result.** The race cell's `brain` arm (fixed-weight multiplicative
Friston form) is a SUM-like combination (a product is still one continuous scalar blending both inputs into a
single number) applied to a task (within-schema derivability) that both the CLS architecture literature and the
landed numbers say should be a ROUTE. Once framed this way, the failure is expected on TWO independent grounds,
not one: (a) A1's diagnosis (raw_PE is a schema-blind global statistic, chance-level, so multiplying it in adds
noise) and (b) this drill's B-verdict (the correct architecture is branching/routing, not scalar blending, so even
a *good* raw_PE should not be multiplicatively fused with schema_fit into one number — it should be one axis of a
2D branch decision). The already-implemented `_four_batch_routing` cascade in
`experiments/exp_ingest_gate_combination_rule_race_v1.py` (precision-floor -> DISCARD, surprise-floor -> SKIP,
then arm-score-threshold -> FAST/SLOW) is structurally a branch/route already — its routing_accuracy numbers
(brain=0.53, schemafit=0.55, learned=0.57, all only marginally above the 0.50 random-routing baseline) show the
CURRENT branch thresholds are not yet well-tuned, consistent with "the FORM (cascaded gate-then-route) is right,
the surprise INPUT to the route is broken (A1), and the thresholds are uncalibrated" rather than "routing itself
doesn't work."

## Cheap decisive test

Reuse `race_seed`'s already-fitted arena (`experiments/exp_ingest_gate_combination_rule_race_v1.py`, zero new
acquisition) and ADD ONE new arm: `local_surprise` = a schema-conditioned prediction error computed only over the
SAME k=2-hop reachable neighborhood that `build_schema_fit` already scans (e.g., rank of the true target restricted
to the reachable-candidate set, rather than the whole-vocabulary rank) — this is the direct operationalization of
A1's "surprise must be measured against a local/structured predictor, not a global one." Race it as a 6th arm
against the existing 5.

- **HARD-PASS (A1 confirmed as the fix, brain-form redeemed once surprise is correctly computed):**
  `local_surprise`-alone DECONF_AUC >= 0.65 (clears chance decisively, unlike flat's 0.542), AND
  `local_surprise * schema_fit` (recomputed brain-form with the corrected surprise input) achieves DECONF_AUC
  within TIE_EPS of or above `schemafit_alone`'s 0.836 — i.e., the interaction term is no longer strictly worse
  than schema_fit alone, and ideally shows genuine incremental lift (>=0.85), which schema_fit alone as a pure
  reachability read cannot supply (it can't tell "close miss" from "far miss" among schema-fitting candidates).
- **HARD-FAIL (A1 diagnosis wrong / this task genuinely IS schema-fit-sufficient):** `local_surprise`-alone stays
  at or below 0.60 (near flat's chance level even after localizing it) — meaning the whole-vocabulary-rank problem
  was NOT the cause of raw_PE's failure, and the honest reading reverts to `SCHEMAFIT_CARRIES_the_fix` as a
  settled, substrate-specific fact (not merely an artifact of a bad surprise proxy) — route to skunkworks VET
  with that framing.
- **MIDDLE band:** `local_surprise`-alone clears 0.60-0.65 (some signal, not decisive) — informative but not
  clean; worth one calibration pass on the reachable-candidate-set definition before a third attempt.

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

1. **Non-redundancy of all 3 signals holds** (P below) even though the *specific* multiplicative combination
   tested failed — HARD-FAIL localization: if the cheap decisive test's `local_surprise` arm ALSO lands at chance,
   that would falsify the "surprise is fixable by localizing its predictor" hypothesis specifically (not the
   general 3-signal theory, which rests on independent mechanistic arguments in A1-A3 that do not depend on this
   substrate's numbers).
2. **Integration is branch/route, not sum/gate** — discriminating prediction from the lit-scan: a smooth,
   continuous consolidation-strength gradient as novelty/schema-fit/recurrence are jointly and parametrically
   varied would falsify ROUTE in favor of SUM; a sharp, bimodal/step transition (matching Tse's 3h-fail/48h-pass)
   would confirm ROUTE. **No study has run this parametric sweep — confirmed literature gap, not resolved by this
   drill.** On the substrate side, HARD-FAIL for the route hypothesis: if a smooth logistic blend of all features
   (the `learned` arm, already tested) had decisively BEATEN the branch/threshold routing_accuracy metric, that
   would favor SUM; instead `learned`'s DECONF_AUC (0.628) beat `brain` (0.530) but both are well below
   `schemafit_alone` (0.836) and none of the routing_accuracy numbers (all ~0.53-0.57) show either a sum or a
   route working well yet on the FULL 4-batch routing task specifically — this is genuinely unresolved on the
   substrate and should not be over-claimed either direction.

## Cross-thread synthesis

- Directly reconciles `research_consolidation_gate_quantitative_signals_2026-07-16.md`'s Friston-form proposal
  (P=0.40, novel synthesis) with the now-landed `ingest_gate_combination_rule_race_v1` FULL result: the proposal's
  FORM (a decomposition keyed by schema-fit) is not falsified — the specific numerical instantiation was, because
  the `raw_PE` input feeding it was schema-blind, exactly the "implementation error" framing this drill's working
  premise anticipated.
- Directly complements `research_schema_fit_derivability_signal_upgrade_2026-07-16.md` (same day): that note fixes
  schema_fit's own resolution (node-aggregate -> pairwise/multi-path via `SRColumnSolver`); this drill identifies a
  PARALLEL, independent fix needed on the surprise side (global-rank -> local/reachable-neighborhood-conditioned).
  Both moves point the same direction (stop reading global/node statistics, read local/relational structure) and
  are compatible/compositional, not competing.
- Consistent with `research_rank_vs_dimensionality_brain_check_2026-07-15.md`'s general finding that the brain
  achieves capability via several simple, low-rank components summed/routed together, rather than one complex
  operator — the branch/route architecture derived here is the same qualitative move (discrete composition of
  simple gates) applied to the consolidation-decision problem.
- Sharpens (does not overturn) the quantum drill's biggest flagged uncertainty ("is raw_PE genuinely non-redundant
  with schema_fit, P=0.30") — the landed race result answers it for THIS specific raw_PE definition (no,
  redundant/worse-than-nothing), while A1 above gives a principled reason a differently-computed raw_PE (local)
  should NOT be redundant, cheaply testable per the decisive test above.

## Substrate-product implications

1. The `brain`-form (fixed-weight Friston multiplicative decomposition) as literally specified should NOT be
   routed to skunkworks VET in its current form — it is empirically at chance and adds no value over
   `schemafit_alone`. Any VET request for this cell should be scoped to the harness-validity gates (which passed
   cleanly: POSCTRL=0.999, CONF=0.990, RANDLABEL=0.486, array-recompute exact) and the genuinely load-bearing
   POSITIVE finding (`schemafit_alone` DECONF_AUC=0.836, non-leaky at 0.836<0.95), not the brain-form claim.
2. Before building any new machinery, the single highest-leverage cheap step is the `local_surprise` arm above —
   it costs zero new acquisition (same arena, same fitted foundations) and directly tests whether A1's diagnosis
   (schema-blind global rank is the specific defect) is correct, which would either redeem the fast/slow
   decomposition (compositional win: reuse both this drill's fix and the SRColumnSolver pairwise schema_fit fix
   together) or cleanly settle that this task is schema-fit-sufficient on this substrate (equally valuable,
   avoids further sunk cost chasing the interaction term).
3. The branch/route framing (Part B) suggests the substrate's ingest-gate should be architected as an explicit
   decision cascade (precision-floor -> DISCARD; surprise-floor -> SKIP; schema-fit-threshold -> FAST/SLOW) rather
   than any single scalar "consolidation score" — which is already how `_four_batch_routing` is built; the
   remaining work is calibrating its thresholds (routing_accuracy currently only ~0.53-0.57, barely above the 0.50
   random-routing floor) rather than redesigning its cascade structure.
4. Flag for future sessions: the Varga et al. 2025 episodic-vs-schematic dissociation is recent (this year) and in
   tension with older "hippocampus = generalized schema comparator" framings used elsewhere in this project's prior
   notes — treat "hippocampal mismatch = schema-conditioned" claims in older notes as needing this caveat, not as
   settled.

## Citations (verified count: 21 distinct sources across 3 lit-scans; primary/secondary flagged inline above)

**Surprise vs. rich predictor:** Dabney, Kurth-Nelson, Uchida et al. 2020, *Nature* 577:671-675 (primary); Wilson,
Takahashi, Schoenbaum & Niv 2014, *Neuron* 81:267-279 (primary); Behrens, Muller, Whittington et al. 2018, *Neuron*
100:490-509 (theoretical synthesis); Lisman & Grace 2005, *Neuron* 46:703-713 (theoretical/primary); Kumaran &
Maguire 2006/2007, *J. Neurosci.* 27:8517 (primary fMRI); Varga et al. 2025, *PNAS* 122(35):e2503535122 (primary,
verified — direct counter-nuance to simple schema-comparator framing); Itti & Baldi 2009, *Vision Research*
(primary, Bayesian surprise vs. saliency).

**Schema-congruence pairwise mechanism:** O'Reilly & McClelland 1994, *Hippocampus* (primary); Rolls & Kesner 2006,
*Prog. Neurobiol.* (secondary review); Guzman et al./Neunuebel & Knierim, *PLOS Comp. Biol.* 2014 (primary); Tse et
al. 2007, *Science* 316:76-82, DOI 10.1126/science.1135935 (primary, exact stats); Tse et al. 2011, *Science*
333:891-895 (primary); van Kesteren, Ruiter, Fernandez & Henson 2012, *Trends Neurosci.* 35:211-219 (secondary
integrative, SLIMM); Gentner 1983, *Cognitive Science* 7:155-170 (primary); Kemp & Tenenbaum 2008, *PNAS*
105:10687-10692 (primary); Liben-Nowell & Kleinberg 2007, *JASIST* 58:1019-1031 (primary, network-science analogy
only); Lu & Zhou 2011, *Physica A* 390:1150-1170 (secondary survey, analogy only).

**Recurrence + CLS integration:** Frey & Morris 1997, *Nature* 385:533-536 (primary); Redondo & Morris 2011, *Nat.
Rev. Neurosci.* 12:17-30 (secondary review); Cepeda et al. 2006, *Psych. Bull.* 132:354-380 (primary meta-analysis);
Cepeda et al. 2008, *Psych. Science* (primary); McClelland, McNaughton & O'Reilly 1995, *Psychological Review*
102:419-457 (primary/theoretical); Kumaran, Hassabis & McClelland 2016, *Trends Cogn. Sci.* 20:512-534 (primary,
partial-confidence access).

**Substrate-internal (not external lit, cited for cross-thread accuracy):**
`data/exp_ingest_gate_combination_rule_race_v1/metrics.json` (landed FULL verdict, directly quoted numbers above);
`experiments/exp_ingest_gate_combination_rule_race_v1.py` (race design, read in full);
`notes/research_consolidation_gate_quantitative_signals_2026-07-16.md`;
`notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md`.

## Deflated confidence (lit-scan calibration: deflate 0.15-0.25; novel-synthesis capped at 0.50)

- **P(the 3-signal non-redundancy argument, as re-derived per-signal in Part A, is correct)** = **0.55** (each
  signal's non-redundant role is grounded in a primary, well-established mechanism — STC tag/capture, CA3
  attractor-basin pairwise completion, distinct RPE-vs-structural-fit computations — converging evidence across
  three independent lit-scans; deflated from an undeflated ~0.70-0.75 for the compound claim covering all three
  simultaneously).
- **P(the specific A1 diagnosis — raw_PE's chance-level failure is caused by it being a global/schema-blind
  statistic, fixable by localizing it — is correct)** = **0.40** (well-motivated by convergent brain literature
  AND by the direct structural argument that "derivability" in the v4 arena is itself a local-reachability
  question, but genuinely untested on this substrate until the cheap decisive test above runs; novel synthesis,
  capped).
- **P(integration is branch/route rather than sum/gate)** = **0.45** (the CLS anatomical-separation argument and
  Tse's near-step transition are real primary evidence, but the discriminating parametric-sweep experiment has
  never been run in the literature — this is the best-supported functional form, not a settled fact; also capped
  as it extends into director synthesis about the substrate's own cascade design).
- **P(cheap decisive test, as specified, HARD-PASSes)** = **0.35** (compound claim: local_surprise must both clear
  chance alone AND show non-redundant lift when composed with schema_fit — genuinely uncertain, this is exactly
  why it is proposed as the next cheap step rather than assumed).

## Next-drill candidate

If the cheap decisive test's `local_surprise` arm HARD-FAILs (stays at chance even once localized to the reachable
neighborhood): the honest conclusion is that within-schema derivability, on THIS substrate's arena construction, is
fully captured by structural reachability alone, and no PE-based signal adds value — next drill should shift from
"fix surprise" to "when does surprise ever add value beyond schema_fit," e.g. via a network-science field
(`network-science-graph-theory`, Tier-1 in the field advisor) probe into whether spectral/expander-mixing schema-fit
proxies leave a *residual* variance that a magnitude-of-mismatch signal could explain, versus reachability-based
proxies which may already be saturating available signal for this class of question.
