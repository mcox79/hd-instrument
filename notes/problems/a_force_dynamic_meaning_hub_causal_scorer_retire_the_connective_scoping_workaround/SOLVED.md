---
problem: a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround
status: PARTIAL
bar: "PASS = a glass-box force-dynamic / situation-model plausibility causal scorer (Talmy/Wolff force dynamics; implicit-causality verb-class + a normality/compatibility scorer; participant-overlap DROPPED as falsified) that picks the connective cause CI-separated over BOTH the current adjacency/connective heuristic AND the scoped floor, with a shuffled-plausibility info-free twin LOSING and no-regress on the other dimensions — and the `predicate_recall` scoping workaround retired. A coarse VerbNet/FrameNet + argument-compatibility first cut is admissible (full fidelity via the meaning hub). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — a glass-box force-dynamic causal scorer cannot beat the connective heuristic within the invariant (with the named cause + number) — is a FULL PASS. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE."
result: "TWO results. (A) LOCATED NEGATIVE on the brief's literal route (= the FULL PASS the bar names): a glass-box force-dynamic + agentivity plausibility SELECTOR does NOT beat the connective heuristic — it is CI-sep WORSE at base density (off_plaus 0.6931 vs positional 0.9010, d=-0.2079 CI[-0.2970,-0.1268], n=101 causal QA, 16 LitBank docs), and the scoped floor cannot be beaten because the QA gold IS the positional rule (agree(gold, positional-on-OFF)=0.9010 == the OFF QA score exactly; a PERFECT-parse oracle 0.7624 and oracle-participants 0.8218 both score WORSE than positional 0.8317 — mechanism-agnostic proof). Connective cause-selection is STRUCTURAL, not plausibility; scoping is the connective-path optimum. (B) CONSTRUCTIVE CHAIN that CROSSES the underlying wall (owner push): a brain-foundational UPSTREAM event-TYPE representation (WordNet verb supersenses -> perception/cognition/emotion/communication/physical) + a DOWNSTREAM UNIFIED bridging selector (Talmy force schema for physical + folk-psych episode schema for MENTAL). On non-adjacent mixed bridges (16 items, 8 phys/8 mental) UNIFIED=1.000 EXCEEDS the physical-only FORCE selector 0.500 by +0.500 CI[+0.250,+0.750], beats MOST_RECENT (locality) by +0.875 and CONNECTIVE_ONLY by +1.000 CI-sep, and beats the shuffled-event-type null p95 0.750; FORCE covers ONLY the physical slice (1.00/0.00), UNIFIED covers BOTH (1.00/1.00). On REAL LitBank cause-ID edges the event-type representation covers 16/16 (mental 11/16) vs force dynamics' 3/16 — the mental majority a force-only scorer structurally cannot represent."
floor: "Connective path: the scoped floor (positional-on-sparse causal QA) = 0.8911 landed (reproduced 0.9010 within 1/101; the dense blanket regression reproduced EXACTLY 0.8317), n=101 over 16 LitBank docs — and it is the CEILING (every non-positional selector scores at/below it: dense-positional 0.8317, force+agentivity plausibility 0.6931, perfect-parse oracle 0.7624, oracle-participants 0.8218). Bridging path: MOST_RECENT (locality) 0.12 and CONNECTIVE_ONLY 0.00 and FORCE_ONLY 0.50 on the non-adjacent mixed set (n=16); shuffled-event-type null p95 0.750."
controls: "(1) SHUFFLED info-free twins (the bar's control): connective plausibility twin off_twin 0.6436 < off_plaus (signal points the WRONG way for connectives); bridge shuffled-plausibility twin FORCE_BRIDGE 1.000 > p95 0.750; UNIFIED shuffled-event-type twin 1.000 > p95 0.750 (the win rides the typing, not position). (2) ORACLE ISOLATION (excludes upstream parse/participants as the cause): perfect-parse structural 0.7624 and oracle participants 0.8218 both < positional 0.8317. (3) DENSITY (excludes 'plausibility is a density-robust connective fix'): plausibility drops FURTHER than positional under recall (0.6535 vs 0.8317). (4) COVERAGE BOUND: force covers 3/16 real cause verbs. (5) CIRCULARITY: agree(gold, positional)=off QA score exactly. (6) FORCE-ONLY baseline on the mental slice = 0.00 (the wall). (7) SLICE ORTHOGONALITY: FORCE covers phys-only, MENTAL covers mental-only, UNIFIED covers both. (8) NO-REGRESS (downstream consumers of causal_links): 12/12 docs connective causal QA + events + coref BYTE-IDENTICAL; goal graph a strict SUPERSET (no node/edge removed) after ordering connective links first; +214 mental links / +47 goal-enablement edges ADDED (upside)."
files_changed: "experiments/exp_causal_selection_instrument_diagnostic_v1.py (circularity + selectors at OFF/DENSE, reproduces landed scoped/blanket numbers), experiments/exp_causal_bridge_plausibility_beats_locality_v1.py (physical non-adjacent bridge dissociation), experiments/exp_causal_unified_bridge_event_type_v1.py (the UPSTREAM event-type representation + DOWNSTREAM unified bridging selector — crosses the wall), experiments/exp_causal_mental_bridge_no_regress_v1.py (mental-bridge wiring prototype + no-regress on every causal_links consumer), verification/test_causal_selection_plausibility_and_scoping.py (scaffold-free witness, 13/13). NO hdlab/ changed — proposed wire + revisit-consumer analysis below; strategy lands (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_causal_selection_plausibility_and_scoping.py"
---

# PARTIAL — the brief's connective-plausibility mechanism is REFUTED (scoping is optimal); the REAL wall (mental causation, the 70% majority) is CROSSED by a brain-foundational chain: an upstream event-TYPE representation + a downstream unified bridging selector

**Status: PARTIAL (WIP until `owner_verdict: DONE`).** Two results: (A) a rigorous located NEGATIVE on the brief's
literal route (the FULL PASS the bar names), and (B) a constructive brain-foundational CHAIN — an upstream event-type
representation + a downstream unified (physical+mental) bridging selector — that crosses the underlying wall in
prototype, exceeds the physical-only baseline CI-separated, and regresses no downstream consumer. No `hdlab/` changed;
the mechanism is proven in `experiments/` + `verification/`; the wire + the revisit-consumers analysis are below;
strategy lands (Q111). Glass-box, NO external LLM. Research-confirmed brain-foundational at every link.

## 0. The opening move — how does the BRAIN select a cause, and WHERE is the wall?
Causal cause-selection is TWO subtasks with TWO brain systems:
- **CONNECTIVE-marked** ("X because Y"): the connective is an explicit discourse-syntactic marker that BINDS the
  cause clause — a STRUCTURAL operation, not a plausibility competition (the brief's own citation, Koornneef & Van
  Berkum 2006, says plausibility matters when structure is ABSENT/ambiguous, not that it overrides a connective).
- **BRIDGING** (unstated, no connective): the reader MUST infer the cause by plausibility — Talmy/Wolff force
  dynamics for PHYSICAL causation, and mentalizing/appraisal (mPFC/TPJ; a DISTINCT system) for MENTAL/INTENTIONAL/
  SOCIAL causation.

The brief applies the BRIDGING mechanism (plausibility) to the CONNECTIVE subtask — a category error — and the
density regression it wants fixed lives in the connective path. So Part A refutes that; Part B builds the mechanism
where it belongs (bridging) and extends it across the WALL: **most narrative causation is MENTAL, a system force
dynamics structurally cannot represent.**

## PART A — the located negative (brief's route), with three independent measured reasons
`exp_causal_selection_instrument_diagnostic_v1` (16 docs, n=101; a cached-events reimplementation that reproduces the
landed numbers):

| arm | acc | vs positional(OFF) |
|---|---|---|
| **off_pos** (positional/sparse = scoped floor) | **0.9010** | 0.0 (landed scoped 0.8911; within 1/101) |
| off_plaus (force+agentivity plausibility) | 0.6931 | **-0.2079 CI[-0.2970,-0.1268] SEP** |
| dense_pos (positional/dense = current heuristic if unscoped) | 0.8317 | -0.0693 SEP (== landed blanket EXACTLY) |
| dense_plaus | 0.6535 | -0.2475 SEP |

1. **Connective selection is STRUCTURAL, not plausibility** — plausibility is CI-sep WORSE (-0.2079), and worse than
   even the naive dense heuristic. The prior force+participant scorer regressed the same way (disk).
2. **The QA gold IS the positional rule** — `build_causal_questions` sets gold = post[0]/pre[-1] (connective-adjacent);
   agree(gold, positional-on-OFF)=0.9010 == the OFF QA score exactly (all 10 misses are ordering artifacts). Smoking
   gun: a PERFECT spaCy parse (0.7624) and oracle participants (0.8218) BOTH score worse than positional (0.8317) —
   the refutation is MECHANISM-AGNOSTIC (perfect signal loses, so any plausibility signal, incl. the brief's un-built
   normality/IC variants, loses on this instrument).
3. **Even in bridging, force dynamics covers a minority** — on 16 real LitBank cause edges the force lexicon classes
   only 3/16; 11/16 are MENTAL/SOCIAL (a different brain system).

**Scoping is the connective-path CEILING, not interim debt.** off_pos 0.9010 is the max any arm reaches; scoping
achieves it while keeping the dense who-did-what events. The brief's premise — "retire scoping via a plausibility
selector" — is refuted: doing so makes causal WORSE.

## PART B — crossing the wall: a brain-foundational chain (upstream event-type + downstream unified bridging)
Research (WebSearch synthesis, citation-dense) confirms the upstream is real neuroscience at the NETWORK level:
- Physical vs mental causation are DISTINCT, anticorrelated systems — Jack et al. 2013 (opposing-domains/reciprocal
  inhibition); Fischer et al. 2016 (intuitive-physics engine, responds MORE to inanimate physical interactions) vs
  Saxe & Kanwisher 2003 (rTPJ mentalizing); Campanella et al. 2022 (triple dissociation affect/mentalizing/physical
  on the SAME stories, F(4,168)=5.907, p<.001 — already cited by `hdlab/affect_register`).
- Implicit causality is PINNED — verb classes carry a causal bias used rapidly/predictively (Koornneef & Van Berkum
  2006; Ferstl et al. 2011 305-verb norms; Hartshorne & Snedeker 2013: FINE-GRAINED verb classes predict IC, coarse
  roles predict near chance).
- HONEST BOUND (flagged): the neuroscience supports the physical-vs-mental NETWORK split, NOT the VerbNet/supersense
  CLASS-level as neural categories. I claim only network-level grounding + the behavioral IC evidence for the classes.

**UPSTREAM component (glass-box, reuses substrate WordNet):** an EVENT-TYPE representation = WordNet verb SUPERSENSE
(most-frequent-sense lexname) -> {PHYSICAL, PERCEPTION, COGNITION, EMOTION, COMMUNICATION, BODY, SOCIAL, STATIVE}.
This GENERALIZES the physical-only force lexicon to the full folk-psychological ontology the mentalizing literature
implies. hdlab ALREADY has the pieces (`idiom_lexicon.lexname_to_frame`, `causation_typing._wn_lexname`) — this
promotes them to a first-class organ. Documented WSD bound: MFS mis-types the homograph 'saw'->contact and
onomatopoeic sound verbs (tick/creak->perception); the fix is contextual WSD = the meaning-hub (a named
further-upstream lever), exactly as the force lexicon carries a narrative back-off.

**DOWNSTREAM component (this problem):** a UNIFIED bridging selector. Type the outcome, route to the matching brain
schema: PHYSICAL result -> Talmy force schema (nearest prior force event); MENTAL/expressive outcome -> folk-psych
episode schema (Rumelhart/Stein&Glenn story grammar; Malle BDI; OCC appraisal): the nearest prior MENTAL TRIGGER
(perception/cognition/communication/emotion).

**It EXCEEDS** (`exp_causal_unified_bridge_event_type_v1`, non-adjacent mixed set, 16 items = 8 phys + 8 mental):

| arm | overall | phys slice | mental slice |
|---|---|---|---|
| MOST_RECENT (locality) | 0.12 | — | — |
| CONNECTIVE_ONLY | 0.00 | — | — |
| FORCE_ONLY (physical-only baseline) | 0.50 | 1.00 | **0.00** |
| MENTAL_ONLY | 0.50 | 0.00 | 1.00 |
| **UNIFIED** | **1.000** | 1.00 | 1.00 |

- UNIFIED **exceeds FORCE_ONLY by +0.500 CI[+0.250,+0.750]** (covers the mental slice force can't), beats
  MOST_RECENT +0.875 and CONNECTIVE_ONLY +1.000 CI-sep, beats the shuffled-event-type null (1.0 > p95 0.750).
- REAL DATA: the event-type representation types 16/16 LitBank edges (mental 11/16) vs force dynamics' 3/16 — crossing
  the coverage wall on real narrative, not just constructed items.

## PART C — no OTHER downstream consumer of the upstream optimization regresses (owner ask)
`exp_causal_mental_bridge_no_regress_v1` wires the mental-bridge addition into a `SituationReader` subclass (fires
ONLY on non-connective sentences, where `_read_causation` currently builds nothing) and compares base vs extended on
12 docs. `sm.causal_links` has exactly two consumers — the causal readout and the goal-hierarchy graph
(`goal_hierarchy_graph._add_enablement`):

| check | result |
|---|---|
| CONNECTIVE causal QA byte-identical | **12/12** |
| events byte-identical | 12/12 |
| coref byte-identical | 12/12 |
| goal graph a strict SUPERSET (no node/edge removed) | **12/12** |
| NET ADD (the upside) | +214 mental-bridge links, +47 goal-enablement edges |

**HONEST ENGINEERING FINDING + the landing requirement.** A first run scored goal-graph superset 11/12: one doc
lost an edge because `_add_enablement` is first-parent-wins and an early non-connective mental link was processed
BEFORE a later connective link for the same goal-head outcome, changing (not just adding) that parent. FIX: emit
connective/bridge links FIRST, mental links AFTER (a two-pass ordering) -> restores 12/12 strict superset. This is a
concrete landing requirement, surfaced by the control rather than asserted.

## PART D — should the OTHER consumers be revisited to be more brain-foundational using the new upstream? (owner ask — YES, three)
1. **`causation_typing` (the SOLVED force TYPER) — the clearest upgrade.** It types CAUSE/ENABLE/PREVENT via the
   physical force lexicon and returns SEQUENTIAL for the 11/16 MENTAL causes. Adopting the event-type representation
   lets it add a MENTAL/INTENTIONAL causal type (route mental edges to a mentalizing/appraisal typer): coverage
   3/16 -> 16/16 on the real edges. This is the seed of a NEW problem (a mental/intentional-causation organ), a
   different brain system from the physical typer — NOT a competitor to it.
2. **`affect_register` — its OWN located negative is now buildable.** It flags: "INFERRED (unstated) emotion ('she
   slammed the door' -> anger) needs the OCC-appraisal channel over the causation+goal registers." The event-type +
   mental-bridge is exactly that substrate: an EMOTION/BODY outcome appraised against a preceding PERCEPTION/COGNITION
   trigger = the OCC appraisal. Revisit affect to consume it (brain-foundational; Campanella 2022 affect system).
3. **The GOAL hierarchy graph — gains a motivational spine.** It already consumes causal_links (enablement). The
   mental-bridge additions (initiating perception/cognition -> emotion/action) are the Stein&Glenn story-grammar
   "initiating event -> internal response -> goal" motivational edges it currently lacks — additive (+47 edges,
   superset-verified), so it enriches plot structure with zero regression.

## THE "ALL THE WAY UPSTREAM" CHAIN — every link brain-foundational (owner ask)
tagger/POS (P6/P7 calibrated joint decoder, filed) -> event EXTRACTION (which tokens are events; predicate_recall,
landed) -> **event-TYPE representation (WordNet supersense; THIS upstream; contextual WSD refinement = the meaning-hub,
further-upstream lever)** -> causal SELECTION (this component: STRUCTURAL for connectives; force schema for physical
bridging; folk-psych schema for mental bridging). The two named gaps (contextual WSD of the event-type; register-robust
extraction) are filed / further-upstream; neither blocks the chain crossing the wall in prototype.

## KEY REALIZATIONS
- **The gold IS the mechanism.** Reading `build_causal_questions` against `connective_cause` showed gold = the
  positional rule; agree=the QA score. A metric built from a rule cannot reward departing from it — and the
  perfect-parse-oracle-loses row proved the refutation is mechanism-agnostic.
- **Two subtasks, two brain systems.** Connective = structural; bridging = plausibility. The brief mis-applied the
  bridging mechanism to the connective subtask.
- **The real wall is REPRESENTATIONAL, not selection.** Force dynamics covers 19% of narrative causation; the 70%
  mental majority needs a DIFFERENT system. The upstream event-type representation is what unlocks it — one cheap,
  glass-box, already-in-the-substrate WordNet lookup generalizes physical-only typing to the full ontology.
- **A control caught a real ordering bug.** The goal-graph superset check (not an assertion) found that link ORDER
  changes a first-wins consumer — turning "additive by construction" into a precise landing requirement.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- **CORRECT the causal-SELECTION verdict.** Selection is TWO subtasks: connective = STRUCTURAL (plausibility is CI-sep
  WORSE, -0.2079; the prior §2b "faithful fix = force-dynamic attribution" is WRONG for the connective subtask;
  scoping is optimal). Bridging = plausibility: force dynamics (physical, demonstrated) + a MENTAL system (the 70%
  majority, NEW).
- **NEW component: an event-TYPE representation (WordNet supersense).** Upstream of causal selection AND consumed by
  affect/goal/causation-typing; generalizes the physical-only force lexicon; network-level neural grounding
  (Jack/Fischer/Saxe/Campanella), class-level is behavioral (IC: Ferstl/Hartshorne&Snedeker), WSD-bound (meaning-hub).
- **NEW result: a UNIFIED bridging selector crosses the mental wall** (+0.500 CI-sep over force-only; real coverage
  16/16 vs 3/16), additive to every causal_links consumer (12/12 no-regress).
- **The causal QA instrument is CIRCULAR for plausibility** — future causal-plausibility claims must use a
  non-circular gold (the bridging dissociation here / RC.GOLD), not the connective QA.

## What I did NOT establish / would withdraw first if wrong
- Part B's downstream is a CONTROLLED dissociation on 16 constructed items (8 phys + 8 mental; verbatim-style prose
  with injected dead-ends), not a naturalistic benchmark. It PROVES the mechanism (typed routing beats locality/force/
  connective, twin losing) and the upstream's REAL coverage is measured on the 16 real LitBank edges — but a
  real-corpus mental-bridge ACCURACY needs a mined non-adjacent gold (a foundation build), the named next step.
  UNIFIED=1.000 is a mechanism ceiling on clean items, not a field accuracy.
- The upstream event-type is MFS-supersense (glass-box) with a measured WSD bound (saw/felt-type polysemy); the
  brain-faithful full form is contextual WSD (the meaning-hub). I would withdraw any "field-accurate typing" claim
  before the WSD refinement.
- Neural grounding is NETWORK-level (physical vs mental), NOT VerbNet-class-level; I do not claim the latter.
- Part A's off_pos reproduced 0.9010 vs landed 0.8911 (a 1/101 first-match tie-break edge); the conclusion (scoping is
  the ceiling; the gold is positional) is unaffected.
- No hdlab landed; I recommend KEEP scoping for the connective path and FILE the mental-causation organ as the
  successor. The mental-bridge wire must order connective links first (the superset requirement).

---

### TLDR (plain language)
I was asked to replace "pick the nearest earlier event as the cause" with a smarter "does this plausibly cause that"
scorer and to retire a stop-gap. I built the smarter scorer and it made the "because/so" cause questions WORSE —
because the grammar word already points at the cause, and the scoreboard we grade on was literally built from the
"nearest" rule, so nothing else can win it. So the stop-gap is the right call, not debt. Then — pushed to cross the
real wall — I found the deeper problem: most story cause-and-effect is MENTAL ("she saw the letter, then wept"), a
different kind of thinking the physical-force method can't touch (it handles under a fifth of real cases). So I built
the missing upstream piece: a cheap, no-AI dictionary lookup that labels each verb by KIND (seeing, thinking, feeling,
speaking, physical), and a reader that walks the natural chain "someone perceives/learns something -> feels/does
something," anchored to the same character. On a mixed test it gets BOTH the physical and the mental cases right
(100%) where the physical-only method gets half, a scrambled-label version fails, and on real book passages the new
labels cover all 16 cause-verbs versus the old method's 3. And I proved that switching this on changes NONE of the
existing answers (cause questions, characters, timeline all identical) while ADDING 214 new mental cause-links — it
only adds, never breaks. Same idea should upgrade three neighbours (the cause-TYPER, the emotion reader, the goal
map) to be more brain-faithful.

### QUESTIONS
None blocking. One call for strategy: I recommend (a) KEEP scoping on the connective path, and (b) FILE a
mental/intentional-causation organ (the real 70% lever) that lands the event-type representation + the unified
bridging selector. If you'd rather I first grow the constructed mental dissociation into a mined real-corpus gold
(a foundation build) before filing, say so.

### NEXT STEPS (PRIORITY-ORDERED)
1. **KEEP scoping** on the connective path (optimal; brief premise refuted). No wire there.
2. **FILE + land the mental-causation chain**: promote the event-TYPE representation (WordNet supersense) as a
   first-class organ (consolidating idiom_lexicon/causation_typing helpers) + the unified bridging selector. Wire the
   mental-bridge into `_read_causation` (connective links FIRST — the superset requirement). Additive; 12/12 no-regress.
3. **Revisit the three consumers** with the new upstream: causation_typing -> mental-causation typing (3/16->16/16);
   affect_register -> its OCC-appraisal inferred-emotion channel; goal graph -> the motivational spine (already additive).
4. **Foundation build**: mine a real-corpus non-adjacent MENTAL-bridge gold for a field accuracy, and add contextual
   WSD (the meaning-hub) to close the event-type polysemy bound.
5. **Retire the connective causal QA** as a plausibility instrument (circular); use a non-circular gold.
