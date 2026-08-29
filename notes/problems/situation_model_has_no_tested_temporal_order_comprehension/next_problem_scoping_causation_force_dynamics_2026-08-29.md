# Next-problem scoping: a brain-foundational CAUSATION organ (force-dynamic causal typing)

Produced while pushing the TIME-dimension problem (which SERVES causation via the precedence
constraint). This scopes the highest-leverage next problem so strategy can file it well. Grounded in a
research drill (2026-08-29) + a first-hand disk audit; NOT a solution (out of this problem's scope).

## Why this is the next problem (leverage)
Of Zwaan's five event-indexing dimensions, CAUSATION is the **least genuinely built** and the TIME work
just handed it its missing ingredient. Disk audit (verified first-hand):
- **Live organ (`experiments/_causal_network.py` / `situation_reader._read_causation`) is a PLACEHOLDER:**
  causal connectives (because/since/so) + naive most-recent-adjacency + a COARSE "agonist force -> result
  change-of-state" heuristic. Its own docstring: the adjacency baseline "FAILS where cause != most-recent";
  it is order-agnostic (the TIME serve now fixes direction: 1.000 vs 0.000 on flashback-causal).
- **NO Wolff/Talmy CAUSE-ENABLE-PREVENT typing exists** (grep confirmed: the only force-dynamic references
  are in SPATIAL/goal/SRL motion contexts, not causal typing).
- Prior causal landings (verified): `exp_causal_correlational_disambig_v1` HARD_PASS (causal-vs-correlational
  SIGN test, not TYPE), `exp_causal_bitemporal_composition_v1` HARD_PASS (**the TIME x causal composition
  reuse precedent**), `exp_arc_schema_routing_do_calculus_v1` **HARD_FAIL** (formal Pearl do-calculus routing
  did NOT lift -> importing statistical-interventional machinery wholesale already failed once; the
  force-dynamic route is the more brain-faithful bet), `exp_causal_counterfactual_replay_v1` MIDDLE_BAND.

## The brain mechanism (PINNED unless noted) -- what a faithful organ computes
Three levels, dissociable (research drill; Kang et al. 2021 meta-analysis = left IFG + left MTG + bilateral mPFC):
- **FORCE DYNAMICS (clause/lexical level, the online cue)** -- Talmy 1988; Wolff 2007. CAUSE/ENABLE/PREVENT
  fall out of a small DISCRETE truth-table over 3 (mostly binary) dims: (1) does the PATIENT tend toward the
  endstate on its own? (2) do affector & patient forces CONCUR or OPPOSE? (3) is the endstate REACHED?
  CAUSE = (no, oppose, yes); ENABLE = (yes, concur, yes); PREVENT = (yes, oppose, **NO endstate**).
  Glass-box + no LLM: affector<-agent, patient<-patient (existing extraction); the verb's force class from a
  substrate-native lexicon (**VerbNet -> Event Force Dynamics, Kalm et al. 2019; FrameNet Causation family:
  Causation / Preventing_or_letting / Thwarting / Enabling**); endstate bit from narrative outcome polarity.
- **CAUSAL NETWORK (discourse level)** -- Trabasso & van den Broek 1985: events = nodes, edges = "necessity in
  the circumstances"; more causally-connected nodes read faster + recalled more. Force dynamics LABELS the
  edges of this network (the composition is OUR-SYNTHESIS, not a published result -- label it).
- **Temporal precedence GATES; force dynamics TYPES; world-knowledge VALIDATES.** Precedence alone is the
  post-hoc fallacy. For single-pass narrative, the ranked cues are: prior-knowledge plausibility (top) >
  force-dynamic verb semantics > counterfactual necessity (as a validation test) > covariation (belongs to
  the OFF learner, needs repetition, NOT the online organ) > precedence (a gate, the TIME organ's job).

## Concrete can-fail test (a floor the connective/adjacency placeholder is STRUCTURALLY at chance on)
- **Set A -- CAUSE vs ENABLE vs PREVENT 3-way**, connective-neutral minimal pairs ("rain swelled the river ->
  flood" CAUSE; "open gates let the river through -> flood" ENABLE; "the dam held back the river -> stayed
  dry" PREVENT). The placeholder can only say "linked/most-recent" -> chance on TYPE.
- **Set B -- causal vs merely-sequential** (connective-stripped, temporally-ordered): "poured the coffee. the
  phone rang" (sequence) vs "dropped the glass. it shattered" (cause). Adjacency links both -> false positives.
- **Set C -- the PREVENT KILLER (sharpest single discriminator):** in PREVENT the endstate NEVER happens ("the
  sandbags prevented the flood" -> no flood node). A cause->outcome/most-recent baseline has nothing to link
  and mislinks/hallucinates; force dynamics is the ONLY account that represents a prevented (counterfactual)
  endstate. Needs a small NEGATION/polarity detector (flagged: must be in scope or Set C can't be scored).
- **Controls (falsifiers):** FD-label SHUFFLE (permute verb force-classes; if accuracy holds it's riding
  connective/order leakage -> falsified); PRECEDENCE-ONLY (TIME organ alone -> FD must add over it);
  frequency-matched random-label ~= the current placeholder (must beat CI-separated on Set A + Set C).
- **Gate:** CI-separated 3-way accuracy over BOTH the placeholder AND precedence-only, gated on the
  placeholder upper CI, on the gold's own population; report CI half-width + shuffle-null p95.

## Reuse / risk
- **Reuses:** the TIME before/after register (precedence gate + the composition harness from
  `exp_causal_bitemporal_composition_v1`), the existing (agent, patient, predicate) extraction, a static
  offline force-dynamic verb lexicon (foundation-is-free-to-build).
- **Risk (research P ~= 0.45, capped <= 0.50):** (a) force-dynamic lexicon COVERAGE/noise on narrative verbs
  is the main unknown -- mitigate with a curated ~40-60 verb list for the gold's predicates; (b)
  patient-role extraction is FRAGILE and coupled to causal scoring (`exp_argument_structure_patient_extraction_v1`
  = PATIENT_FIX_REJECTED_REGRESSES_CAUSAL) -- the organ must not regress it; (c) the PREVENT/sequential cells
  are the highest-confidence wins (placeholder structurally incapable); full 3-way is the riskier part.

## DE-RISK PROBE RESULT (built + measured 2026-08-29 -- `experiments/exp_causal_force_dynamics_probe_v1.py`)
A minimal glass-box proof (extraction GIVEN, isolating the TYPING mechanism; a ~45-verb curated force
lexicon + the Wolff truth-table) confirms the core bet BEFORE the full problem is filed:
- **PREVENT KILLER (Set C, n=8):** force-dynamic **1.000** vs the link-outcome placeholder **0.000** -- the
  placeholder is STRUCTURALLY incapable (a prevented outcome has no node to link to).
- **CAUSE-vs-ENABLE verb isolation (n=12, endstate held constant so ONLY the verb distinguishes):**
  force-dynamic **1.000** vs a verb-force-class-SHUFFLE twin **0.499 (chance)** -- the force-dynamic VERB
  semantics is genuinely load-bearing, not the endstate bit riding along (a control that caught the
  endstate confound: on the full 3-way the shuffle twin scores 0.81 because endstate alone identifies
  PREVENT, so the verb-isolation subset is the honest discriminator).
- Full 3-way+sequential: force-dynamic 1.000 vs majority/placeholder-ceiling 0.188 (CI-separated).
This turns the P~=0.45 estimate into a DEMONSTRATED mechanism on the isolating gold. The P~=0.45 risk now
sits entirely on the FULL problem's extras (lexicon coverage on real narrative verbs, patient-extraction
fragility, the negation/polarity detector for endstate, a real-prose serve) -- NOT on the core typing bet.

## Bottom line
Build a **force-dynamic causal-type organ**: precedence-gate (reuse TIME) -> fill affector/patient from
extraction -> TYPE the link CAUSE/ENABLE/PREVENT from a substrate-native force-dynamic verb lexicon +
outcome polarity -> validate with a light plausibility check. The killer test is PREVENT (outcome never
happens), where today's link-the-nearest-events placeholder fails by construction -- **now demonstrated
(force-dynamic 1.000 vs placeholder 0.000).**
