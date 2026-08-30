# Research: how the brain combines force cues into patient-tendency, and the key-vs-wind wall

Drill run 2026-08-30 for the SOLVER on `causation_typing_needs_a_patient_tendency_estimator`.
Dispatched via hdi_research (cue-combination + affordance/directional as force terms). Two of Wolff's
primary PDFs (JEP:General 2007; the force-perception paper) were access-blocked; the load-bearing
content was recovered from the OPEN-ACCESS primary Wolff & Barbey (2015) Front.Hum.Neurosci. 9:1 and
from quoted snippets. PINNED = verified at primary/abstract level; SPECULATIVE = inferential bridge.

## Q1 -- CUE COMBINATION: is a force-SUM faithful? YES, with one flag. (PINNED)
- **The combination rule IS vector addition.** In Wolff's vector model the affector (A), patient (P) and
  *other* forces (O) "combine to produce a resultant force (R)"; for compound causes "a patient force is
  derived from the vector addition of all of the patient forces." **So summing the patient-side cues into
  one net patient-tendency vector is force-dynamically faithful -- the force-SUM is the right family.**
  (Wolff 2007 JEP:General 136:82-111; Wolff & Barbey 2015, open access.)
- **Not winner-take-all, not Bayesian-over-latent-forces** -- additive composition with a **qualitative**
  read-out (Wolff 2007 Exp.4: people compute the resultant by a qualitative decision rule, not exact
  arithmetic -- good for a discrete glass-box typer).
- **THE FLAG (what would make a naive sum WRONG):** the causal TYPE is NOT read off the sign of the GRAND
  resultant R = A+P+O. CAUSE and ENABLE BOTH reach the endstate. The verified truth-table:

  | Relation | Patient tends toward E | A-P concordance | Endstate reached |
  |---|---|---|---|
  | CAUSE  | No  | No  | Yes |
  | ENABLE | Yes | Yes | Yes |
  | PREVENT| Yes | No  | No  |

  The discriminator is the SIGN of the PATIENT tendency and its CONCORDANCE with A. **So the sum must be
  PATIENT-SIDE ONLY; compare its sign to the affector.** Collapsing A's own magnitude into the sum and
  reading the total destroys CAUSE/ENABLE.
- **DECISION IMPLICATION (built):** T = m + a + d is a PATIENT-SIDE sum: affordance (P internal /
  friction), directional/gravity (O), and affector-magnitude entering NOT as A's force but as an
  ABDUCTIVE inference about P (weak affector + endstate reached => P supplied the rest => +1). The
  affector, being the agent of a REACHED endstate, points to +E; therefore concordance = sign(T):
  +1 tends -> concur -> ENABLE; -1 resists -> oppose -> CAUSE.

## Q2 -- PATIENT AFFORDANCE / DISPOSITION as a force term. (PINNED general; OUR-INVENTION map)
- **PINNED:** Wolff states the patient force P "can be generated ... from gravity or **mechanisms internal
  to the patient**, or from **the patient's resistance to changes in speed or direction due to frictional
  forces or momentum**." That is an explicit in-model warrant that the patient's intrinsic physical
  disposition (resistance vs self-motion tendency) is a legitimate source of the patient vector.
- **Converging (abstract-level):** White (2006, Acta Psychologica; 2009/2012) perceived force scales with
  object properties/roles; Michotte (1963) launching; infant core physics -- inertia, gravity, solidity
  (Spelke; Baillargeon 2004; Lin/Stavans/Baillargeon 2020); Gibson (1979) affordances are ACTION-SPECIFIC.
- **SPECULATIVE = OUR-INVENTION:** the specific round/buoyant/hinged=>tends, heavy/anchored=>resists map is
  ours -- label UNPINNED-BY-EVIDENCE, gate on a can-fail control (twin + held-out + positive control), not
  face validity. **Measured wall (this cell):** WordNet TAXONOMY separates labile from inert patients
  poorly (labile recall ~0.5, misses vane/leaf/raft/log/kite); glosses lift labile recall to 0.67 but drop
  inert recall to 0.36. WHY: WordNet encodes lexical CATEGORY (a leaf is a plant-part, a raft a craft), not
  physical DISPOSITION (mass/mobility/support) -- exactly the "perception/knowledge" part a lexical
  resource structurally cannot carry. So the affordance term is a PRINCIPLED core-physics property lexicon,
  broader than any test item, validated on HELD-OUT patients -- NOT a WordNet lookup.

## Q3 -- DIRECTIONAL / GRAVITY / environmental cues. (PINNED)
- Environmental forces are first-class vectors: Wolff names GRAVITY explicitly as a generator of the
  patient force, and the model carries an "other forces (O)" term. The empirical testbed is a physics
  simulator (the inflatable-boat-in-water paradigm) where medium/gravity forces are entered as vectors and
  shape the causal-type judgment. **Treating downhill/downstream/with-the-current as +tendency and
  uphill/upstream/against as -tendency is faithful (the O/gravity role).** (Wolff 2007; Wolff & Barbey 2015.)

## THE KEY-vs-WIND WALL (the brief's flagship pair), understood
"the key opened the gate" = ENABLE; "the wind opened the gate" = CAUSE. My 3-term estimator does NOT settle
the BARE pair, and that is the CORRECT behaviour once affordance is made rest-state-honest:
- **A hinged joint affords bidirectional OSCILLATION (swing/turn/rock) freely, but a directional
  STATE-CHANGE from a stable rest (opening a CLOSED gate) needs an IMPULSE -- it is NOT spontaneously
  afforded.** So "gate" contributes a=0 for "open" (not +1). This is a real fidelity fix (Talmy/Wolff:
  ENABLE's prototype is REMOVING A RESTRAINT, not the joint moving).
- **The bare pair is under-determined (Kuhnmuench & Beller 2005, "partly linguistically CONSTRUCTED"):** a
  breeze nudging an ajar gate = ENABLE; a gale forcing a shut gate = CAUSE. The same string supports both.
  My estimator declines to invent tendency it cannot read (both fall to the verb lexicon) -- the honest
  answer, not a bug.
- **Once the construed force MAGNITUDE is stated, the estimator RESOLVES it:** "breeze opened the gate" ->
  ENABLE, "blast opened the gate" -> CAUSE (validated, positive control `gate_breeze_vs_blast`).
- **The residual, fully-general fix is a 4th Wolff term = the AFFECTOR'S ROLE** (restraint-REMOVER /
  enabling-instrument: key/latch/catch/release/switch -> ENABLE, vs force-APPLIER). PINNED (Talmy's
  "letting" = removing a barrier; Wolff ENABLE prototype). It is ORTHOGONAL to the three patient-tendency
  cues and is the highest-value adjacent follow-on -- mapped, not built here (the brief scopes 3 terms).

## Bottom line for the build
1. Force-SUM is faithful; keep it PATIENT-SIDE and read type off sign vs the affector (done).
2. Affordance + directional are legitimate Wolff force terms (done); the property map is OUR-INVENTION,
   gated on twin + held-out + control (done).
3. WordNet alone cannot supply patient disposition (measured) -> principled core-physics lexicon.
4. Key-vs-wind: bare = under-determined (honest fallback); magnitude-stated = resolved; the full fix is an
   affector-ROLE term (adjacent #1).
