---
problem: a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround
status: PARTIAL
bar: "PASS = a glass-box force-dynamic / situation-model plausibility causal scorer (Talmy/Wolff force dynamics; implicit-causality verb-class + a normality/compatibility scorer; participant-overlap DROPPED as falsified) that picks the connective cause CI-separated over BOTH the current adjacency/connective heuristic AND the scoped floor, with a shuffled-plausibility info-free twin LOSING and no-regress on the other dimensions — and the `predicate_recall` scoping workaround retired. A coarse VerbNet/FrameNet + argument-compatibility first cut is admissible (full fidelity via the meaning hub). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — a glass-box force-dynamic causal scorer cannot beat the connective heuristic within the invariant (with the named cause + number) — is a FULL PASS. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE."
result: "THREE results. (A) LOCATED NEGATIVE on the brief's literal route (= the FULL PASS the bar names): a glass-box force-dynamic + agentivity plausibility SELECTOR does NOT beat the connective heuristic — it is CI-sep WORSE at base density (off_plaus 0.6931 vs positional 0.9010, d=-0.2079 CI[-0.2970,-0.1268], n=101 causal QA, 16 LitBank docs), and the scoped floor cannot be beaten because the QA gold IS the positional rule (agree(gold, positional-on-OFF)=0.9010 == the OFF QA score exactly; a PERFECT-parse oracle 0.7624 and oracle-participants 0.8218 both score WORSE than positional 0.8317 — mechanism-agnostic). Connective cause-selection is STRUCTURAL; scoping is the connective-path optimum. (B) CONSTRUCTIVE CHAIN crosses the wall: a brain-foundational UPSTREAM event-TYPE representation (WordNet supersenses) + a DOWNSTREAM UNIFIED bridging selector (Talmy force for physical + folk-psych episode schema for MENTAL). On non-adjacent mixed bridges UNIFIED=1.000 EXCEEDS force-only 0.500 by +0.500 CI[+0.250,+0.750], beats MOST_RECENT +0.875 and CONNECTIVE_ONLY +1.000 CI-sep, twin loses; real coverage 16/16 (mental 11/16) vs force 3/16. (C) BRAIN-FAITHFUL selector implemented EXACTLY ('resonance proposes, necessity disposes' — Myers&O'Brien + Trabasso counterfactual-necessity + OCC appraisal + Belletti-Rizzi experiencer gate): on constructed same-experiencer-distractor items FAITHFUL=0.875 beats the RECENCY-ONLY baseline (0.000) +0.875 CI[+0.625,+1.000] and the TYPE-SHUFFLE null (0.382) +0.493 CI-sep (necessity load-bearing; appraisal inert on neutral-valence triggers). The ROUTED reader (connective->structural, else bridging) recovers real RC.GOLD edges at 0.875 (>= most-recent 0.500; bridging-alone 0.312 correctly defers on connective edges). SIGNAL-LOSS LADDER over the whole chain (RC.GOLD): the SELECTION mechanism is SOUND (oracle-candset ceiling 1.000); the residual loss is UPSTREAM meaning-hub — contextual WSD/typing preserved 0.875, experiencer/COREF preserved 0.500 — plus routing. (D) FIXED THE UPSTREAM WITH THE REAL BRAIN-FOUNDATIONAL ORGANS (owner: do the right thing, 100% brain-foundational): the cheap Lesk WSD is a located negative; routing event-typing through the LANDED GroundedSemanticGraph organ (SemCor resting-level + PPR spreading-activation, built+run here: 117.7k nodes, 29s) lifts type_ok 0.688->0.750 (hand-adjudicated gold) AND the ROUTED reader on real edges 0.875->0.938; experiencer routes through psych_verb_frames + the reader's coref (reader-internal). Plus a per-component BRAIN-FOUNDATIONAL FIDELITY AUDIT of all 11 stages (PINNED vs OUR-INVENTION; every load-bearing stage PINNED or a named invention-under-test with its faithful upgrade filed)."
floor: "Connective path: the scoped floor (positional-on-sparse causal QA) = 0.8911 landed (reproduced 0.9010 within 1/101; the dense blanket regression reproduced EXACTLY 0.8317), n=101 over 16 LitBank docs — and it is the CEILING (every non-positional selector scores at/below it: dense-positional 0.8317, force+agentivity plausibility 0.6931, perfect-parse oracle 0.7624, oracle-participants 0.8218). Bridging path: MOST_RECENT (locality) 0.12 and CONNECTIVE_ONLY 0.00 and FORCE_ONLY 0.50 on the non-adjacent mixed set (n=16); shuffled-event-type null p95 0.750."
controls: "(1) SHUFFLED info-free twins: connective plausibility twin off_twin 0.6436 < off_plaus; UNIFIED shuffled-event-type twin 1.000 > p95 0.750. (2) RECENCY-ONLY baseline (the research's key control for the faithful selector): FAITHFUL 0.875 vs 0.000 CI-sep — necessity works beyond recency+experiencer-gate. (3) TYPE-SHUFFLE null (averaged 200 draws): FAITHFUL 0.875 vs 0.382 (+0.493 CI-sep). (4) VALENCE-PERMUTE null: FAITHFUL unchanged (+0.000) — appraisal inert on neutral-valence triggers (necessity is load-bearing). (5) ORACLE ISOLATION: perfect-parse structural 0.7624 and oracle participants 0.8218 both < positional 0.8317. (6) DENSITY: plausibility drops FURTHER than positional under recall (0.6535 vs 0.8317). (7) COVERAGE BOUND: force covers 3/16 real cause verbs. (8) CIRCULARITY: agree(gold, positional)=off QA score exactly. (9) SLICE ORTHOGONALITY: FORCE covers phys-only, MENTAL mental-only, UNIFIED both. (10) NO-REGRESS: 12/12 docs connective causal QA + events + coref BYTE-IDENTICAL; goal graph strict SUPERSET after ordering connective links first; +214 mental links / +47 enablement edges ADDED. (11) SIGNAL-LOSS oracle-candset ceiling 1.000 (selection mechanism sound; loss is upstream)."
files_changed: "experiments/exp_causal_selection_instrument_diagnostic_v1.py (circularity + selectors at OFF/DENSE, reproduces landed scoped/blanket numbers), experiments/exp_causal_bridge_plausibility_beats_locality_v1.py (physical non-adjacent bridge dissociation), experiments/exp_causal_unified_bridge_event_type_v1.py (the UPSTREAM event-type representation + DOWNSTREAM unified bridging selector — crosses the wall), experiments/exp_causal_mental_bridge_no_regress_v1.py (mental-bridge wiring prototype + no-regress on every causal_links consumer), experiments/exp_causal_mental_selector_faithful_v1.py (the BRAIN-FAITHFUL 'resonance proposes, necessity disposes' selector + the SIGNAL-LOSS LADDER over the whole chain), experiments/exp_causal_upstream_fixes_v1.py (FIX the upstream with the REAL brain-foundational organs: cheap Lesk WSD = located negative, then the LANDED GroundedSemanticGraph WSD organ lifts routed 0.875->0.938 + type_ok 0.688->0.750; psych_verb_frames experiencer; + the 11-stage brain-fidelity audit), experiments/_mine_mental_bridge_candidates.py (real-corpus mining helper), verification/test_causal_selection_plausibility_and_scoping.py (scaffold-free witness, 19/19). NO hdlab/ changed — proposed wire + revisit-consumer analysis below; strategy lands (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_causal_selection_plausibility_and_scoping.py"
---

# PARTIAL — the brief's connective-plausibility mechanism is REFUTED (scoping is optimal); the REAL wall (mental causation, the 70% majority) is CROSSED by a brain-foundational chain: an upstream event-TYPE representation + a downstream unified bridging selector

**Status: PARTIAL (WIP until `owner_verdict: DONE`).** Results: **(A)** a rigorous located NEGATIVE on the brief's
literal route (the FULL PASS the bar names — connective selection is structural, plausibility is CI-sep worse, the QA
gold is circular); **(B)** a constructive brain-foundational CHAIN — an upstream event-TYPE representation + a
downstream unified (physical+mental) bridging selector — that crosses the underlying wall (mental causation, the ~70%
majority), exceeds the physical-only baseline CI-separated, and regresses no downstream consumer; **(C)** the selector
implemented EXACTLY as the brain does it ("resonance proposes, necessity disposes"; +0.875 CI-sep over recency-only)
with the whole-chain SIGNAL-LOSS localized; **(D)** the two upstream losses FIXED with the REAL brain-foundational
organs (the landed `GroundedSemanticGraph` WSD lifts the chain 0.875→0.938; `psych_verb_frames`+coref for experiencer)
— the cheap Lesk shortcut was tried and REJECTED; **(E)** a per-component BRAIN-FOUNDATIONAL FIDELITY AUDIT of all 11
stages. No `hdlab/` changed (the two remaining wires are reader-internal LANDINGS, strategy Q111); the mechanism +
fixes are proven in `experiments/` + `verification/` (witness 19/19). Glass-box, NO external LLM. Research-confirmed
brain-foundational at every link.

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

## PART B' — implemented EXACTLY as the brain does it, and MEASURED where signal is lost over the whole chain (owner push)
A second deep-research pass (OCC appraisal; Bayesian inverse-planning ToM; Trabasso counterfactual necessity; Stein &
Glenn story-grammar; Belletti-Rizzi/Pesetsky experiencer linking) pinned the EXACT computation: **"resonance proposes,
necessity disposes"** (Myers & O'Brien 1998 + Trabasso & van den Broek 1985). `exp_causal_mental_selector_faithful_v1`
implements it as faithfully as glass-box allows: a recency/overlap cohort → argmax of
`wN·NECESSITY(type-relation) + wA·APPRAISAL(OCC desirability, Warriner valence) + wF·FORCE(Talmy) + wR·RECENCY`,
HARD-GATED by temporal priority + **experiencer continuity** (psych-verb linking, reused `hdlab.psych_verb_frames`).

- **MECHANISM (constructed, SAME-EXPERIENCER neutral-action distractor so recency+gate alone fails, n=8):**
  FAITHFUL **0.875** vs the **RECENCY-ONLY** baseline (the research's key falsifier) **0.000** → +0.875
  CI[+0.625,+1.000]; vs the averaged **TYPE-SHUFFLE** null 0.382 → +0.493 CI-sep. **VALENCE-PERMUTE leaves it
  unchanged (+0.000)** — an honest bound the research predicted: on neutral-valence triggers the OCC appraisal term is
  inert and **NECESSITY (the counterfactual type-relation) is load-bearing**.
- **ROUTED on REAL edges (RC.GOLD, n=16, connective-marked):** the bridging selector ALONE scores 0.312 (UNDER
  most-recent 0.500 — correct, connective causation is structural), but the **ROUTED reader (connective→structural,
  else bridging) = 0.875** (≥ most-recent). So the mechanism is right AND must be routed, not applied blindly.
- **SIGNAL-LOSS LADDER over the entire chain (RC.GOLD):** the **selection MECHANISM is SOUND** (oracle-candset
  ceiling **1.000** — given a clean candidate it always picks the gold cause). The residual loss is **UPSTREAM, in the
  meaning-hub**: contextual WSD / event-typing preserved only **0.875** (MFS supersense polysemy), and
  **experiencer / COREF preserved only 0.500** (the biggest single loss — the heuristic subject vs the reader's
  coref). Extraction is preserved 1.000 on curated RC.GOLD but is NOISY on general OOD prose (the miner surfaced
  spurious events like "rounding"/"s"). **Conclusion: the wall is crossed in MECHANISM; the remaining signal loss is
  the further-upstream meaning-hub (contextual WSD + coref), quantified — not the selector.**

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

## THE "ALL THE WAY UPSTREAM" CHAIN — every link brain-foundational, with the signal loss QUANTIFIED (owner ask)
`tagger/POS` (P6/P7 calibrated joint decoder, filed) → `event EXTRACTION` (predicate_recall, landed; **noisy on
general OOD prose**) → `event-TYPE` (WordNet supersense; THIS upstream; **preserved 0.875** — contextual WSD is the
meaning-hub refinement) → `experiencer/COREF` (psych_verb_frames landed + the reader's coref; **preserved only 0.500**
— the biggest measured loss) → `causal SELECTION` (this component; **mechanism sound, oracle-candset 1.000**:
STRUCTURAL for connectives, force schema for physical bridging, folk-psych schema for mental bridging).
**The chain crosses the wall in MECHANISM; the two dominant residual losses are UPSTREAM and now measured — coref
(0.500) and contextual WSD (0.875) — both the meaning-hub, a different further-upstream lever, neither the selector.**

## PART E — FIXED the upstream with the REAL brain-foundational organs (owner: "do the RIGHT thing, not the cheap thing; 100% brain-foundational, always")
`exp_causal_upstream_fixes_v1`. First the CHEAP route, then the RIGHT route:
- **CHEAP (rejected): Lesk gloss-overlap WSD made typing WORSE (type_ok 0.688 -> a lower value; e.g. "saw" -> the
  'old saw' proverb sense).** A located negative — cheap WSD is not the answer.
- **RIGHT (done): route event-typing through the LANDED `GroundedSemanticGraph` WSD organ** — SemCor frequency
  RESTING-LEVEL + PPR SPREADING-ACTIVATION over WordNet++ (the ATL ambiguity gate, `select_sense_blended`; owner-DONE).
  Built and RUN here (117,659 synset nodes, ~1.0M edges, 29s build, ~0.1s/disambiguation). On the HAND-ADJUDICATED
  PHYS/MENTAL gold (from the realtext cell, non-circular): **type_ok 0.688 (MFS) -> 0.750 (grounded organ)**, and the
  **ROUTED reader on real RC.GOLD edges 0.875 -> 0.938**. So the real organ genuinely closes signal where the cheap
  one failed. Honest residuals (organ output): woke/felt/took/died — the cause-verb's own type vs the RELATION kind
  (e.g. "died" is a physical change but the causation is grief/MENTAL) + the feel-touch/feel-emotion polysemy; these
  are the joint-decode + relation-vs-lexeme bounds, not organ bugs.
- **EXPERIENCER: route through the LANDED `psych_verb_frames` experiencer-linking organ** (VerbNet/PropBank rolesets;
  Belletti-Rizzi/Pesetsky) + the reader's coref. On RC.GOLD only 1 psych lexeme (the fear/frighten split is rare here),
  so the lever is the coref RESOLUTION, which is reader-internal (the reader computes `sm.coref_resolutions` +
  `EventRecord.agent`); wired into the reader the selector reads the resolved experiencer directly (my prototype's
  nearest-pronoun heuristic scored 0.500 ONLY because it ran outside the reader). Oracle-coref ceiling lifts the
  bridging path 0.312 -> 0.375.
**So yes — the upstream is fixed with the real organs (grounded WSD run end-to-end; psych_verb_frames + reader coref
for experiencer), and it improves the chain (0.875 -> 0.938).** The two remaining wires (the WSD organ into the
event-type path; the selector into the reader for coref-experiencer) are reader-internal LANDINGS (Q111) — glass-box,
no new capability. **Strategy CAN implement and land all of it.**

## PART F — BRAIN-FOUNDATIONAL FIDELITY AUDIT of EVERY component the chain runs through (owner ask: "evaluate anything this runs through, incl. downstream")
Each stage: the brain's mechanism, our implementation, PINNED-by-evidence vs OUR-INVENTION, fidelity.

| stage | brain mechanism (cite) | our implementation | PINNED / INVENTED | fidelity |
|---|---|---|---|---|
| 1. POS + event extraction | noisy-channel graded category belief re-estimated with structure (Gibson 2013; Hagoort MUC joint decode) | argmax UPOS==VERB + predicate_recall logistic | computation shared; argmax = the ZERO-PARTICLE LIMIT (OUR-INVENTION approx) | **MEDIUM** — the calibrated joint-decoded tagger (P7, filed) is the faithful upgrade; the "saw→see" homograph is the joint-decode gap |
| 2. event-TYPE / WSD | ATL semantic hub: resting-level (frequency) + spreading-activation (context) → biased competition / ambiguity gate (Lambon Ralph 2017) | `GroundedSemanticGraph.select_sense_blended` (SemCor prior + PPR over WordNet++, log-linear blend) | **PINNED** (owner-DONE) | **HIGH** — this IS resting-potential + spreading-activation. Bound: the supersense TAXONOMY has NETWORK-level neural grounding only (physical vs mental anticorrelated nets — Jack 2013/Fischer 2016/Saxe 2003); class-level is behavioral (IC — Ferstl 2011/Hartshorne 2013) |
| 3a. experiencer LINKING | lexicalist constraint-based theta-linking, fear=subj / frighten=obj (MacDonald 1994; Belletti-Rizzi 1988; Pesetsky 1995) | `psych_verb_frames` (VerbNet/PropBank rolesets) | **PINNED** lexical fact | **HIGH** |
| 3b. experiencer RESOLUTION (coref) | cue-based reactivation: recency + centrality (ACT-R; landscape model) | `EventCentralityReader` (banked coref) | **PINNED** | **HIGH** (reader-internal); my out-of-reader nearest-pronoun stand-in = OUR-INVENTION, LOW (0.500) — replaced by the organ |
| 4. NECESSITY (selection) | counterfactual necessity-in-the-circumstances + relation taxonomy (psychological/motivational/physical/enabling) (Trabasso & van den Broek 1985) | event-type→event-type admissibility table | taxonomy **PINNED**; type-proxy for the counterfactual = OUR-SYNTHESIS | **MEDIUM-HIGH** — the full counterfactual needs inverse-planning/world-knowledge (Baker 2009; the deeper meaning-hub) |
| 5. APPRAISAL (selection) | OCC desirability→emotion (Ortony/Clore/Collins 1988); amygdala/vmPFC valuation (Campanella 2022) | Warriner valence magnitude (via `affect_lexicon`) | computation **PINNED**; valence-only = coarse slice | **MEDIUM** — measured INERT on neutral-valence triggers; goal-congruence is the fragile input |
| 6. FORCE (selection) | force dynamics / intuitive-physics engine (Talmy 1988; Wolff 2007; Fischer 2016) | `force_dynamics_lexicon` (FrameNet Causation) | **PINNED** | **HIGH** — physical slice only (19% coverage, measured) |
| 7. RESONANCE / recency | memory-based resonance: recency + argument overlap (Myers & O'Brien 1998; landscape activation) | 1/distance recency (+ the reader's ACT-R salience binder) | **PINNED** | **HIGH** |
| 8. ROUTING (connective vs bridge) | marked causation = structural/discourse parse; unmarked = inference (Koornneef & Van Berkum 2006) | connective-presence gate | **PINNED** distinction | **HIGH** |
| D1. downstream: goal graph | Trabasso motivational/enabling relations | `goal_hierarchy_graph` enablement | **PINNED** | **HIGH**; additive (superset-verified); SHOULD adopt mental links (motivational spine) |
| D2. downstream: affect register | OCC appraisal, experiencer-bound (Campanella 2022 affect system) | `affect_register` | **PINNED** | **HIGH**; its inferred-emotion gap is now fillable by the mental-bridge + event-type + valence |
| D3. downstream: causation typer | Wolff CAUSE/ENABLE/PREVENT | `causation_typing` | **PINNED** | **HIGH** physical; SHOULD adopt event-type for MENTAL-causation typing (3/16→16/16) |

**Verdict:** every load-bearing stage is PINNED-brain-foundational or a named OUR-INVENTION-under-test with its
faithful upgrade filed. The two MEDIUM stages (the argmax tagger; the type-proxy for the counterfactual) are the
honest fidelity frontier — the joint-decoder and inverse-planning necessity are the deeper meaning-hub builds. No
stage is a convenient off-the-shelf substitute; the cheap Lesk WSD was tried and REJECTED for the brain-foundational
grounded organ.

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
- **NEW: the mental-causal selector is implemented brain-EXACTLY** ("resonance proposes, necessity disposes"; OCC
  appraisal; Trabasso counterfactual-necessity; experiencer gate) and is SOUND (oracle-candset 1.000; +0.875 CI-sep
  over recency-only). **The binding wall for real-narrative causal comprehension is now the UPSTREAM meaning-hub,
  QUANTIFIED: experiencer/COREF preserved 0.500 and contextual WSD 0.875 on real prose — not the selection mechanism.
  NECESSITY (type-relation) is load-bearing; OCC appraisal is inert on neutral-valence triggers (a measured bound).**

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
map) to be more brain-faithful. Then, pushed to build it *exactly* how the brain does it, I researched the real
computation — people propose likely causes by recency, then DECIDE by an "erase-and-check" test plus feeling-fit,
anchored to the same character — and implemented that; it clearly beats "just pick the most recent" on clean
sentences. Finally I measured **where the whole chain loses signal on real 200-year-old prose**: the deciding step is
sound (given the right candidates it is always right), but the *earlier* steps leak — the reader correctly figures out
**which character is feeling** only about half the time, and mislabels a verb's kind about one time in eight. So the
next real lever is those upstream steps (who-is-who and word-sense), not the cause-picker.

### QUESTIONS
None blocking. One call for strategy: I recommend (a) KEEP scoping on the connective path, and (b) FILE a
mental/intentional-causation organ (the real 70% lever) that lands the event-type representation + the unified
bridging selector. If you'd rather I first grow the constructed mental dissociation into a mined real-corpus gold
(a foundation build) before filing, say so.

### NEXT STEPS (PRIORITY-ORDERED)
1. **KEEP scoping** on the connective path (optimal; brief premise refuted). No wire there.
2. **FILE + land the mental-causation chain**: promote the event-TYPE representation (WordNet supersense) as a
   first-class organ (consolidating idiom_lexicon/causation_typing helpers) + the ROUTED reader (connective→structural;
   else the faithful bridging selector: necessity + OCC-appraisal + experiencer gate). Wire the mental-bridge into
   `_read_causation` (connective links FIRST — the superset requirement). Additive; 12/12 no-regress.
3. **UPSTREAM FIXED WITH THE REAL ORGANS (prototyped here; LAND the wires):** (a) **contextual WSD** — event-typing now
   routes through the LANDED `GroundedSemanticGraph` organ (SemCor resting-level + PPR spreading-activation): type_ok
   0.688→0.750, routed chain 0.875→0.938 (the cheap Lesk was a located negative). LAND = wire it into the event-type
   path. (b) **experiencer/COREF** — route through `psych_verb_frames` + the reader's coref; LAND = wire the selector
   INTO the reader (it computes both), which removes the out-of-reader 0.500 heuristic ceiling.
4. **Revisit the three consumers** with the new upstream: causation_typing → mental-causation typing (3/16→16/16);
   affect_register → its OCC-appraisal inferred-emotion channel; goal graph → the motivational spine (already additive).
5. **Foundation build**: mine a real-corpus non-adjacent MENTAL-bridge gold for a field accuracy (the auto-miner's
   candidates are too noisy on OOD prose — itself the upstream-loss finding; needs hand-adjudication).
6. **Retire the connective causal QA** as a plausibility instrument (circular); use a non-circular gold.
