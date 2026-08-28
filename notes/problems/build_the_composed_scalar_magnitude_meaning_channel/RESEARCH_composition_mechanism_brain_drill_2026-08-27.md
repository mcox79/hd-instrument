# RESEARCH DRILL: how does the brain COMPOSE dimension + polarity + degree into ONE magnitude read-out?

**2026-08-27, solver session (build_the_composed_scalar_magnitude_meaning_channel).** The sub-ops are each PINNED
(integrated p3 work). The genuinely OUR-INVENTION-UNDER-TEST part of THIS problem is the COMPOSITION: how the three
sub-computations become one representation. Owner directive: be fully brain-foundational, research where unsure. So I
drilled the composition mechanism specifically (literature scan). This note records what came back and how it changes
the build. Confidence deflated; PINNED vs SPECULATIVE separated.

## THE CRUX (was genuinely open): one oriented axis, or two opponent poles?

**Answer from the data: BOTH, at different processing stages — and the brain CONSTRUCTS the one from the other.**

- **Two opponent monotonic pools UPSTREAM (PINNED).** Macaque LIP (Roitman, Brannon & Platt 2007): numerosity is
  coded MONOTONICALLY, ~45% "more" units (fire more for larger) and ~55% "less" units (fire more for smaller) — an
  opponent "more/less" pair. Nieder 2007 "summation coding" confirms monotonic units alongside peaked ones.
- **A peaked log-Gaussian PLACE code DOWNSTREAM (PINNED).** VIP/PFC number neurons (Nieder & Dehaene 2009; Piazza
  2004): bell-shaped tuning, symmetric on a LOG axis (Weber-Fechner). Neural Weber fraction ~0.18-0.24.
- **A single ORIENTED signed axis at readout/decision (PINNED).** SNARC (Dehaene, Bossini & Giraux 1993): magnitude
  maps to one left->right continuum; negative numbers extend it leftward of zero with a normal distance effect.
- **The reconciliation (Verguts & Fias 2004, a well-supported MODEL, not a direct recording): the peaked place code
  is BUILT by summing the opponent monotonic pools.** Parietal (opponent) -> PFC (peaked) -> oriented readout.

So "sign x magnitude on one axis" vs "two half-axes" is a false dichotomy. The stored/tuned form is a **place code
indexed by pole and log-magnitude**; the **signed oriented axis is the projection used for COMPARISON/decision.**

## DEGREE = LOG-DISTANCE FROM A CONTEXT-SET STANDARD (PINNED behaviorally)

- Moyer & Landauer 1967 distance effect + Holyoak 1978 / Banks 1976 reference-point model + the **semantic congruity
  effect** (polarity interacts with degree: "which is larger?" is faster for two large items) — comparison is a noisy
  magnitude subtraction **relative to a movable anchor**. The congruity effect appears in monkeys too (not purely
  linguistic).
- Kennedy & McNally / Bierwisch degree semantics (right computational level, SPECULATIVE neurally): a gradable
  adjective is a measure function returning a degree evaluated against a **contextual standard set by the comparison
  class** ("tall for a jockey"). Candidate neural implementation of setting the standard: OFC range/norm adaptation
  (Padoa-Schioppa) rescaling to the current distribution.
- **Implication:** degree ~= `log(distance(magnitude, standard))`. **Markedness (-log frequency) IS a distance from
  the unmarked default/standard** (Zipf/Horn: the unmarked term is the frequent default; marked terms are rare and far
  from it) — so our PROBE-D/F markedness degree and the reference-point standard are the SAME variable, log-compressed
  (PROBE F pinned the log via Laughlin efficient coding). This is a convergence, not a new assumption.

## THE POLE IS A CATEGORICAL LABEL, NOT A SIGN BIT (Kennedy 2001 "Polar Opposition")

Antonym poles are NOT symmetric. The unmarked pole ("tall/big/good") names the WHOLE scale and the default direction;
the marked pole ("short") is restricted and measures extent from the opposite endpoint. **A pure symmetric
sign-on-one-axis code ERASES this markedness asymmetry.** Opposition therefore carries categorical/relational
information beyond +/-1 — consistent with PROBE A (opposition is relational, raw geometry inverts antonyms) and with
valence being opponent (amygdala BLA positive/negative populations; O'Neill/Salzman) upstream of a single vmPFC value
axis (Bartra/Kable common currency) — the SAME opponent->integrated-axis shape as number.

## THE UNIFICATION — recommended composition (ranked by faithfulness)

1. **PREFERRED (stored lexical form):** bind a categorical POLE symbol to an FPE code of log-distance-from-standard,
   on a semantic-control-selected dimension:
   `adjective  ~=  DIM_i  (x)  POLE_p  (x)  FPE(log(|degree - standard|))`
   - `DIM_i` = the scale (semantic control; LIFG/pMTG — dimension selection PINNED as a network, its binding to
     magnitude SPECULATIVE). `POLE_p` in {unmarked, marked} as a DISCRETE SYMBOL (keeps the markedness asymmetry a
     sign bit loses). `FPE(log .)` = the VSA-native tuned place code (Plate/Frady-Sommer/Eliasmith SSPs); its
     similarity kernel IS the distance effect, so Moyer + congruity fall out for free.
2. **Readout/decision form:** a single log-oriented signed axis `FPE(sign . log(|degree - standard|))` — right for
   COMPARISON (SNARC + extended number line + vmPFC), but discards markedness + dimension identity, so it is a
   PROJECTION, not the store.
3. **Most literal input stage:** two opponent monotonic channels combined into (1) a la Verguts-Fias — redundant with
   (1) for a lexical store.

**Chosen: store as (1); derive (2) as the comparison readout.** This is substrate-native — `DIM_i`/`POLE_p` are
`unit_phase_vec` keys, `(x)` is `hdlab.binding.bind`, `FPE` is FHRR self-bind (already in `quality_relation` Ch.B),
the standard is an operand, comparison is `unbind`. It is exactly the memory's "store-organization fidelity lever"
(dense scalar -> bound composable symbols), and it upgrades Ch.B from linear->log AND from a bare scalar -> a
pole-bound place code.

## CAN-FAIL DISCRIMINATOR the research hands us (built as T2b)

Binding a discrete POLE symbol (form 1) should beat a bare SIGNED AXIS (form 2) SPECIFICALLY on **marked-pole items**
("short/cold/bad/tiny") and on comparison-class re-anchoring — that is where the two encodings make different
predictions. If pole-symbol binding does NOT beat the sign bit anywhere, the categorical-pole claim is unsupported and
a signed axis suffices (a real, publishable sub-result either way).

## HONEST CAVEAT (report, do not bury)

The adjective<->magnitude-neuron link is SUGGESTIVE, not pinned: van Dijck-lineage work (PMC8793294) found NULL
distance effects for adjectives and attributed the congruity effect to a DECISION stage, not magnitude-system
recruitment. So "gradable adjective = tuned magnitude neuron" is our best HYPOTHESIS-UNDER-TEST. Countervailing
positive evidence on OUR representation: the Moyer distance effect DID appear (p3 part2: valence far-near +0.318). We
report both.

## KEY SOURCES
Walsh 2003 / Bueti & Walsh 2009 (ATOM); Nieder & Dehaene 2009; Piazza 2004; Dehaene 2003 (Weber-Fechner);
Roitman/Brannon/Platt 2007 (LIP monotonic/opponent); Nieder 2007/2016 (summation vs labeled-line); Verguts & Fias
2004 (summation->peaked); Dehaene/Bossini/Giraux 1993 (SNARC); Moyer & Landauer 1967; Holyoak 1978 / Banks 1976
(reference-point / semantic congruity); Kennedy & McNally 2005, Kennedy 2001 "Polar Opposition", Bierwisch 1989;
Bartra/McGuire/Kable 2013 (vmPFC common currency); Padoa-Schioppa (OFC range adaptation); amygdala opponent valence
(O'Neill/Salzman); PMC8793294 (adjectives & the generalized magnitude system, the null-distance caveat);
Marghetis/Odic/Lourenco (partial sharing); Plate / Frady-Sommer / Eliasmith (FPE / SSP).
