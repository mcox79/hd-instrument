---
problem: gate_the_eventive_nominal_event_channel_by_context_wsd_event_vs_result
status: PARTIAL
bar: "The WSD-gated nominal channel keeps the lift AND restores precision, CI-separated over the UNGATED channel, on MODERN gold (TB-Dense + MAVEN, the SAME populations p2 used) ... The gated arm must retain survival/recall NEAR the ungated 0.73/0.78 (state the fraction of the lift retained) WHILE precision rises toward the verb-only channel's level. The FLOOR is the UNGATED nominal channel recomputed on the SAME population ... The info-free twin LOSES CI-separated ... NO-regress + a positive control the type rule cannot get ... The abstention band is isolated."
result: "Glass-box biased-competition per-token gate (parse-selected selectional context + selectional resting-bias), COMBINED arm. TB-Dense (22 docs, 333 multi-hop chains, TimeML gold): extraction precision 0.6517 (ungated FLOOR) -> 0.7142 gated, +0.0624 CI[+0.0419,+0.0802] SEP+ (toward verb-only 0.7871); whole-subgraph survival 0.7327 (ungated) -> 0.6577 gated (retains 77% of the lift over verb-only 0.4054), -0.0751 CI[-0.1051,-0.0480]. MAVEN-ERE (710 docs, 43599 chains): precision 0.4768 -> 0.5310, +0.0543 CI[+0.0515,+0.0573] SEP+; survival 0.7495 -> 0.6363 (retains 66% of the lift over 0.4134). Info-free twins LOSE CI-sep for the COMBINED arm on BOTH golds (shuffled-cue AND permuted-context; TB twinB +0.051, MAVEN twinB +0.0110), though the MAVEN margins are small; the FLAT-bag and parse-ONLY twins do NOT reliably lose at MAVEN scale -- the SELECTIONAL CUE is what carries the token-level signal (a required brain-foundational finding). Positive control (same lemma, both readings): the gate makes token-differentiated decisions a type lexicon cannot, but is keep-biased and only weakly separates genuinely-ambiguous polysemous tokens (the located encoding ceiling). DECISIVE END-TO-END TEST (Sec 4g): through the actual solved temporal reasoner (1586 gold pairs), answered-correct is joint_cop 0.3480 -> ungated joint_nom 0.4937 (87% of the 0.5681 gold ceiling) -> WSD-gated 0.4590 (-0.0347 CI-sep WORSE) -> dominance-gated 0.4470 (-0.0467 CI-sep worse); conditional accuracy is FLAT (~0.58). So the gate is net-NEGATIVE downstream (it only drops coverage); the brief's premise is REFUTED and the real problem is solved by turning the nominal channel ON UNGATED."
floor: "UNGATED eventive-nominal channel (joint_nom) recomputed on each gold's own population: TB-Dense precision 0.6517 / survival 0.7327 ; MAVEN-710 precision 0.4768 / survival 0.7495. (Verb+copular reference joint_cop: TB precision 0.7871 / survival 0.4054 ; MAVEN 0.6208 / 0.4134.)"
controls: "(1) info-free PERMUTED-CONTEXT twin (score the token against a random other token's sentence) -- for the COMBINED arm LOSES CI-sep on BOTH golds (TB +0.051, MAVEN +0.0110); the FLAT and parse-ONLY arms do NOT reliably lose at MAVEN scale (twinB +0.0006/+0.0007 NS). (2) SHUFFLED-CUE twin (permute the selectional cue onto wrong tokens) -- combined arm LOSES CI-sep (TB +0.018, MAVEN +0.0026). (3) info-free SHUFFLED-diagnosticity twin (permute the readout weights) -- LOSES with parse context on TB (+0.036), borderline on MAVEN. So the SELECTIONAL CUE is the load-bearing token-context signal at scale; the biased-competition readout alone is weak (the encoding ceiling). (4) NO-REGRESS additive subset property: recovered(joint_cop) SUBSET recovered(gated) SUBSET recovered(joint_nom) for every doc (the gate only ever DROPS NOM tokens; VERB/COP byte-identical). (5) CUE-ONLY reference (selectional sort, no readout): ~=ungated (TB 0.6526/0.7327; MAVEN 0.4795/0.7460) -- the cue alone does almost nothing; its value is as a resting bias combined with the readout. (6) type-level impossibility: same lemma KEPT in its event sentence and DROPPED in its object sentence."
files_changed: "experiments/_nominal_wsd_gate.py (the gate organ + grounded readout path, self-test PASS); experiments/exp_nominal_wsd_gate_v1.py (the measurement: flat/parse/combined arms + floor + twins + theta sweep + positive control); experiments/exp_nominal_overfire_enumeration_v1.py (the over-firing population enumeration); experiments/exp_nominal_gate_representation_probe_v1.py (the WHY: event/object sig cosine w2v 0.93 vs grounded 0.51); experiments/exp_nominal_gate_grounded_v1.py (the grounded-representation prototype -- REFUTED at MAVEN power); experiments/_selectional_preference.py (the DERIVED selectional-preference organ from GUM gold parses) + experiments/exp_nominal_gate_selectional_v1.py (derived vs hand cue -- TIES, data-starved at MAVEN power); experiments/exp_nominal_gate_frequency_v1.py (the omitted FREQUENCY/DOMINANCE prior -- best single precision (dom_only) but same frontier, MAVEN 23653 chains); experiments/exp_nominal_gate_endtoend_v1.py (THE DECISIVE end-to-end reasoner test -- gating is net-NEGATIVE, ungated wins 0.4937=87% of ceiling); verification/test_nominal_wsd_gate.py (scaffold-free witness, W1-W4 PASS). NO hdlab write (Q111 -- proposed diff in Sec 7)."
reverify: ".venv/Scripts/python.exe verification/test_nominal_wsd_gate.py"
---

# Gating the eventive-nominal event channel by a per-token context/WSD gate (event vs result/object)

**Status: PARTIAL — but the headline is a REFUTATION of the brief's premise, earned by the decisive end-to-end test
(Sec 4g). I built the WSD gate faithfully (brain-foundational sense machinery: biased competition + selectional
restriction + frequency/dominance; precision restored CI-separated at the extraction level, twins losing) — and then,
running it through the ACTUAL solved temporal reasoner, the gate makes the reader answer FEWER timeline questions
correctly (0.4937 ungated -> 0.4590 gated, CI-separated WORSE) because conditional accuracy is flat and gating only
drops coverage. The precision "cost" the brief is built around is an EXTRACTION-INSTRUMENT ARTIFACT, not a downstream
cost. The real goal — make the biggest temporal survival lever a safe default-ON gain — is achieved by turning the
nominal channel ON UNGATED (already the downstream winner, 87% of the gold-event ceiling), NOT by gating it. The gate
is a rigorously-built located NEGATIVE. No hdlab landed (Q111); the revised recommendation (flip default-ON, don't
wire the gate) is in Sec 7.**

## 0. WHAT THE BRIEF ASKED, AND THE ONE-SCREEN ANSWER
Turn the p2 joint front-end's eventive-NOMINAL channel from a default-OFF precision liability (survival 0.41->0.73/0.78
but precision 0.79->0.65 from polysemy) into a safe default-ON gain, by a glass-box NO-LLM per-TOKEN gate that fires
the noun-event only when its committed reading in context is the EVENT cluster, reusing the landed sense machinery.

- **Over-firing population (enumerated, not searched).** Running the ungated nominal channel on both golds and grouping
  the NOM-fired gold-NON-events by lemma: **TB-Dense 284 FP vs 141 TP (NOM-fire precision 0.332), 152 over-firing
  lemmas; MAVEN 8912 FP vs 2657 TP (precision 0.230), 1245 lemmas.** Of the FP mass, **91% (TB) / 81% (MAVEN) is on
  event-vs-object POLYSEMOUS lemmas that the frozen curated hub COVERS** (0 hub-uncovered FP mass on either gold — the
  "coverage bottleneck" fork the brief anticipated is DECISIVELY CLOSED), and **9% (TB) / 19% (MAVEN) is on
  NON-polysemous eventive nouns (battle / campaign / weather) the gate structurally CANNOT flip** (their only WordNet
  cluster is eventive; they are gold-non-events for a different reason — a named-event reference, not a sense choice —
  an annotation/discourse residual, not WSD). This 9-19% is the hard cap on any WSD gate's precision gain.
- **The gate (brain-foundational).** For each NOM token, run the landed biased-competition readout
  (`hdlab.diagnostic_context_wsd`) over the token's candidate WordNet noun-sense signatures (`hdlab.meaning_foundation`)
  in context, and FIRE only if the committed (argmax) reading's coarse WordNet cluster is EVENT/ACT/PROCESS/PHENOMENON
  (`hdlab.underspecified_sense_reader.coarse_cluster`), i.e. the EVENT-vs-OBJECT biased-competition MARGIN >= theta.
  The context is the SYNTACTICALLY-SELECTED neighborhood from the p2 parse (governor + siblings + own dependents), and
  a selectional-sort resting bias (eventuality-selecting vs entity-selecting governor) is added via
  competition-integration. All PINNED brain computations; theta / w_sel / gamma / abstain-direction are swept.
- **Result (TB-Dense, the cleaner TimeML precision instrument).** precision 0.6517 (ungated FLOOR) -> **0.7142** gated
  (+0.0624 CI[+0.0419,+0.0802], SEP+ over the floor; verb-only reference 0.7871); whole-subgraph survival 0.7327 ->
  **0.6577** (retains **77%** of the lift; still +0.25 above verb-only 0.4054). **MAVEN-ERE (710 docs, 43599 chains):**
  precision 0.4768 -> **0.5310** (+0.0543 CI[+0.0515,+0.0573] SEP+); survival 0.7495 -> **0.6363** (retains **66%**).
- **The twins LOSE — but ONLY for the COMBINED (readout + selectional-cue) arm, and the SELECTIONAL CUE carries it.**
  With a FLAT sentence-bag context the info-free twins do NOT lose (the "gain" is indistinguishable from random
  NOM-dropping). Adding parse-selected context makes the twins lose on TB-Dense but NOT at MAVEN scale; it is the
  SELECTIONAL-SORT resting bias that makes the shuffled-cue AND permuted-context twins LOSE CI-separated on BOTH golds
  (TB twinB +0.051, MAVEN twinB +0.0110 — small but CI-separated over 43599 chains). **The load-bearing
  brain-foundational finding: the biased-competition readout alone barely uses token context here (the encoding
  ceiling); the argument-structure / selectional-restriction cue is what supplies the reliable token-level signal.**
- **What it does NOT do:** fully restore precision to verb-only while holding survival at ungated (no operating point
  does — Sec 4), and it separates genuinely-ambiguous same-lemma tokens only modestly above chance (the located
  contextual-input-encoding ceiling, Sec 4c). Both are located and counted.

## 1. THE BRAIN MECHANISM WE COPIED (PINNED vs OUR-INVENTION)
- **PINNED — biased competition / controlled semantic cognition.** Word-sense selection in context is not context
  averaging; the LIFG/pMTG control network amplifies the context features that DISCRIMINATE the competing senses and
  suppresses the shared topic ones (Jefferies 2013; Lambon-Ralph 2017; Rodd 2002). We reuse the landed readout that
  implements exactly this (`diagnostic_context_wsd`: diagnosticity = max-minus-mean cosine spread).
- **PINNED — underspecification by default (Frisson 2009; Rodd 2002 shared core).** The reader commits the COARSE
  cluster (event vs object), not a fine synset — which is exactly what a fire/no-fire gate needs. We commit the
  WordNet lexname supersense of the biased-competition winner (`underspecified_sense_reader.coarse_cluster`).
- **PINNED — selectional restriction / thematic fit / argument structure (McRae; Grimshaw 1990; pMTG/ATL role
  binding, Friederici 2017; Frankland & Greene 2015).** The event-vs-result reading of a deverbal nominal is fixed by
  the GOVERNING PREDICATE's selectional sort ("the building COLLAPSED" -> a physical object; "the building OF the
  bridge / that LASTED years" -> an eventuality). We read the governor + arguments off the p2 parse and enter the sort
  as a RESTING BIAS on the competition — the same competition-integration form (bias + strong-context-decides) as the
  landed Bayesian `sense_prior` knob (MacDonald 1994 / McRae). This is a TOKEN-level governor cue, NOT the banned
  Grimshaw *nominal*-complement gate (which asks whether the NOUN takes "of X"; bare event-nominals dominate news, so
  that gate crushed recall — p2's drilled negative) and NOT a type-level lemma lexicon.
- **OUR-INVENTION-UNDER-TEST (swept, never adopted).** theta (the margin threshold = the abstention band); w_sel (the
  selectional resting-bias weight); gamma/topk (the P9 precision-weighting); the fire-vs-drop abstention direction;
  the choice of vector space (the sglite-w2v the curated signatures live in). Every one is swept (Sec 4).

## 2. WHAT WE BUILT (all in experiments/ + verification/ — NO hdlab write, Q111)
- **`experiments/_nominal_wsd_gate.py`** — the gate organ. `event_margin()` (biased-competition EVENT-vs-OBJECT margin
  over the token's covered candidate senses, exposing shuffle_rng for the twin), `keeps()` (fire iff margin >= theta;
  abstain -> swept fire/drop), `selectional_context()` (the parse-selected neighborhood), `sort_cue()` (the signed
  selectional-sort governor cue). Self-test PASS: committed-reading positive control 4/4 (painting BOTH readings, attack,
  organization), REUSE-equivalence to `underspecified_sense_reader.select_sense` (event-mass matches its distribution to
  4 decimals), and the twin perturbs the margin. It REUSES the landed organs verbatim — it re-derives nothing.
- **`experiments/exp_nominal_wsd_gate_v1.py`** — the measurement. Three context variants (FLAT bag / PARSE-selected /
  PARSE+selectional-cue), each vs the ungated FLOOR, with two info-free twins, a theta sweep, the abstain knob, the
  aggregate positive control (all + polysemous-only), and paired-bootstrap CIs (survival over chains; precision over
  docs). TB-Dense + MAVEN, the same modern populations p2 used.
- **`experiments/exp_nominal_overfire_enumeration_v1.py`** — the over-firing population enumeration (Sec 0).
- **`verification/test_nominal_wsd_gate.py`** — scaffold-free witness, W1-W4 PASS (self-test; the additive subset
  no-regress property; precision-restored-over-floor + survival-above-verb-only; permuted-context twin loses).

## 3. THE MEASURED TRIPLE (floor = ungated nominal; reference = verb+copular)
**TB-Dense (22 docs, 333 multi-hop BEFORE/AFTER chains, TimeML — the cleaner precision gold), theta=0, w_sel=0.03:**

| arm | precision | recall | NOUN-event recall | survival | twinA (shuf) | twinB (perm-ctx) |
|---|---|---|---|---|---|---|
| joint_cop (verb+copular, reference) | 0.7871 | 0.7562 | 0.105 | 0.4054 | — | — |
| joint_nom (ungated, **FLOOR**) | 0.6517 | 0.8910 | 0.703 | 0.7327 | — | — |
| gated, FLAT-bag context | 0.7085 | 0.8480 | 0.521 | 0.6066 | 0.6156 (NS-fail) | 0.6066 (NS-fail) |
| gated, PARSE-selected context | 0.7156 | 0.8489 | 0.521 | 0.6396 | 0.6036 (**SEP**) | 0.6066 (**SEP**) |
| gated, **PARSE+selectional cue** | 0.7142 | 0.8528 | 0.531 | **0.6577** | 0.6396 (**SEP**) | 0.6066 (**SEP**) |

- gated (combined) vs FLOOR: **precision +0.0624 CI[+0.0419,+0.0802] SEP+**; survival -0.0751 CI[-0.1051,-0.0480]
  (retains 77% of the lift; +0.252 above verb-only).
- The FLAT-bag twins do NOT lose (the naive readout ~= random NOM-dropping); the PARSE/combined twins DO lose.

**MAVEN-ERE (710 docs, 43599 chains, Wikipedia/Wikinews), theta=0, w_sel=0.03:**

| arm | precision | recall | survival | vs FLOOR precision | vs FLOOR survival | twinA (shuf) | twinB (perm-ctx) |
|---|---|---|---|---|---|---|---|
| joint_cop | 0.6208 | 0.7560 | 0.4134 | — | — | — | — |
| joint_nom (**FLOOR**) | 0.4768 | 0.9190 | 0.7495 | — | — | — | — |
| gated, FLAT-bag context | 0.5336 | 0.8750 | 0.6258 | +0.0568 CI[+0.0540,+0.0598] SEP+ | -0.1237 | +0.0022 SEP | +0.0006 (NS-fail) |
| gated, PARSE-selected context | 0.5335 | 0.8723 | 0.6260 | +0.0567 CI[+0.0538,+0.0598] SEP+ | -0.1236 | +0.0008 (NS-fail) | +0.0007 (NS-fail) |
| gated, **PARSE+selectional cue** | 0.5310 | 0.8770 | **0.6363** | **+0.0543 CI[+0.0515,+0.0573] SEP+** | -0.1133 | +0.0026 (**SEP**) | +0.0110 (**SEP**) |

- The COMBINED arm retains **66%** of the survival lift at +0.054 precision; ONLY it has BOTH twins losing CI-sep (the
  cue is load-bearing at scale — the readout alone gives NS twins). Positive control (polysemous-only, n=301): event
  KEPT 0.641, object DROPPED 0.371 — keep-biased, weakly separating (Sec 4c). NOTE MAVEN's
  absolute precision is depressed by ANNOTATION INCOMPLETENESS (MAVEN-ERE annotates only relation-participating
  triggers, so many true eventive nominals count as FPs) — the GAIN is valid (same confound both arms) but the absolute
  level and the "restore to verb-only" target are understated; TB-Dense (TimeML annotates events densely) is the
  trustworthy precision instrument.

## 4. WHAT WE DID NOT ESTABLISH, AND WHY (the located residuals — drilled, not hand-waved)
### 4a. The Pareto tradeoff: no operating point gives BOTH verb-only precision AND ungated survival.
The theta sweep (TB-Dense, combined arm): theta=-0.05 prec 0.669 / surv 0.727 (frac 0.98); -0.02 -> 0.691 / 0.706
(0.92); 0.00 -> 0.714 / 0.658 (0.77); +0.02 -> 0.737 / 0.625 (0.67); +0.10 -> 0.775 / 0.522 (0.36). Precision reaches
verb-only (~0.79) ONLY at theta where survival collapses toward the verb-only floor (the Grimshaw-recall-crash regime).
So the abstention band is real and load-bearing (a too-permissive theta collapses to the ungated precision; a too-strict
one collapses recall), and there is a favorable knee near theta=-0.02 (TB-Dense +0.04 precision at 92% survival
retention; MAVEN-710 +0.038 precision at ~78% retention) — but
NO single point restores precision fully while holding survival at ungated. This is a property of the readout's
per-token discrimination quality, which brings us to 4c.

### 4b. ~9-19% of the FP mass is not a WSD problem at all (the hard cap).
Non-polysemous eventive nouns (battle=noun.act only; campaign, weather) are gold-non-events when they NAME/REFERENCE a
known event rather than trigger a new one ("at the Battle of Cherry Valley"). Their only WordNet cluster is eventive, so
the gate fires them by construction. This is a trigger-vs-named-reference (discourse/annotation) distinction, a DIFFERENT
organ (referring-expression / discourse-status), and it caps the achievable extraction-precision gain independent of WSD
quality.

### 4c. The distinction is ARGUMENT-STRUCTURAL, not lexical — drilled to the representation and back (the deep finding).
On genuinely event-vs-object POLYSEMOUS both-reading lemmas the gate separates event- from object-readings only weakly
and (in w2v) is KEEP-biased (TB-Dense combined event-kept 0.43 / object-dropped 0.585; MAVEN-710 n=301 event-kept 0.641 /
object-dropped 0.371). I drilled WHY to the representation and it is a decisive, measured result
(`exp_nominal_gate_representation_probe_v1`): **the event-sense and object-sense signatures of the same nominal are cos
0.93 COLLINEAR in the w2v space the readout uses** (n=29) — the readout is handed two near-identical vectors, so no
context weighting can separate them. In the GROUNDED sensorimotor space (Lancaster action/perception + Brysbaert
concreteness, `hdlab.grounded_similarity`) the same signatures are cos **0.51** (many near-orthogonal: operation -0.06,
match -0.12, attack 0.17) — because an ACT (action/temporal features) and an OBJECT (visual/spatial/concrete) are a
sensorimotor-feature distinction, which is exactly what COLLAPSES in a distributional co-occurrence space. So the readout
OPERATION is brain-foundational but its INPUT representation (distributional w2v/PPMI) is NOT the ATL's grounded
hub-and-spoke representation (Lambon-Ralph) — a genuine, located non-brain-foundational choice.
**BUT: swapping the readout to grounded signatures does NOT fix the gating at power (`exp_nominal_gate_grounded_v1`).**
TB-Dense (n=76) misleadingly un-biased (event-kept 0.43->0.60) — but MAVEN at power (18622 chains, 1874 control tokens)
REFUTES it: the grounded gate is WORSE than w2v on precision (0.536 vs 0.542), survival (0.604 vs 0.636), and its
permuted-context twin does NOT lose (d -0.021 ns) whereas the w2v-COMBINED twin DOES (+0.030 SEP). The reason: separating
the SIGNATURES is necessary but not sufficient — the CONTEXT must select between them, and the context->sense selection
signal is too weak in BOTH spaces. **Conclusion: event-vs-result is not a lexical-similarity distinction in ANY
representation; it is an ARGUMENT-STRUCTURE / selectional-restriction computation. The lexical readout is a weak
tiebreaker; the SELECTIONAL cue (argument frame) is the primary carrier of the reliable token signal (its twin loses at
power; the readout's does not).** The brain-foundational lever is therefore to make the selectional/aspectual mechanism
PRIMARY and itself brain-foundational (derive it from the substrate's event-knowledge / thematic-role organs +
morphosyntactic aspectual cues), NOT to swap the lexical representation. This RE-DIRECTS the named upstream fork
`break_the_contextual_input_encoding_ceiling_for_specific_sense_selection`: for SORTAL/aspectual distinctions the lever is
the argument-structure system, not a richer contextual sense-encoder. **We did NOT conclude "needs a neural model"; we
drilled the representation, refuted the obvious swap at power, and located the real mechanism.**

### 4d. The downstream VALUE of the precision gain is not established here (a premise caveat).
p2 measured that the nominal over-extraction does NOT degrade the temporal reasoner's conditional accuracy (0.583 vs
0.598). So the precision defect may cost the DOWNSTREAM reasoner little, in which case the ungated (max-survival) channel
could already be acceptable and the gate's precision gain buys robustness/safety rather than accuracy. The clean
default-on decision needs the END-TO-END reasoner accuracy under gated vs ungated (the strategy session's integration
measurement) — not just the extraction triple measured here. We recommend the permissive knee (Sec 8), which keeps
~78-92% of the survival lift (gold-dependent).

### 4e. The brain mechanism built TWO ways (hand list AND derived selectional preference) — neither beats the other; the ceiling is selectional-knowledge coverage, not the mechanism.
Sec 4c concluded the distinction is argument-structural, so I built the brain's ACTUAL mechanism the non-hand-coded way:
a DERIVED selectional-preference organ (`experiments/_selectional_preference.py`, Resnik selectional association /
McRae thematic fit) — P(filler is event-sort | governing verb, relation) accumulated OFFLINE from GUM GOLD dependency
parses (301 docs, 1006 reliable verb-slot preferences; sensible gradients: collapse-subj 0.20, occur-subj 0.59,
begin-obj 0.71). Head-to-head vs the hand cue (`exp_nominal_gate_selectional_v1`, MAVEN 18622 chains, 1874 control
tokens): the derived cue does **NOT** beat the hand list (der precision 0.5455 vs hand 0.5418 but survival 0.611 vs
0.636; hand+derived == hand; der's permuted-preference twin does NOT even lose, d -0.012 ns), and BOTH separate the
hard tokens only weakly (event-keep ~0.6, object-drop ~0.4 -- barely above chance). The limiter is now precisely
located and it is NOT the mechanism: (i) selectional-knowledge COVERAGE is 0.44 (GUM at 301 docs gives weak per-verb
counts; the hand list has strong priors for common governors but similar coverage); (ii) ~half the nominals are
governed by NON-verbs (copular/adjective/noun heads) where a verb-selectional cue does not apply at all; (iii) the
parse (UAS 0.79) limits governor extraction. **So the brain's mechanism is faithfully built and tested at power in two
independent forms; the residual token-level ceiling is a DATA/COVERAGE limit on selectional knowledge + parse quality,
distinct upstream organs — not this gate, not the representation, and not a neural model.** This meets the high bar for
CONVERGENCE (the mechanism is identified, replicated, and the specific reason it does not fully separate is located).

### 4f. FOUR brain-foundational cues, ONE frontier — the wall is not a missing cue (aggressive-research result).
The single most robust lexical-access cue is sense FREQUENCY / DOMINANCE (Duffy/Morris/Rayner 1988 reordered access;
the dominant sense is accessed first, context overrides). The SOLVED gate set prior_weight=0 -- omitting it -- so I
added it (`event_margin(prior_weight>0)` via the landed diagnostic_context_wsd Bayesian log-prior; `dominant_event_mass`
for the pure-dominance gate) and power-tested (`exp_nominal_gate_frequency_v1`, MAVEN 23653 chains). Dominance is REAL:
`dom_only` (a cheap TYPE-level frequency rule, NO readout) gives the single best precision (0.5484, +0.0622 over the
ungated floor -- it drops the huge non-event-DOMINANT over-firers forces/government for a precision gain). **But it does
NOT break the precision/survival frontier -- it slides along it** (dom_only +0.062 precision / 0.6096 survival vs the
SOLVED gate +0.054 / 0.6266; freq_ctx at high prior_weight trades back to +0.049 / 0.6480). **All FOUR brain-foundational
cues now tested -- biased-competition context (w2v), grounded sensorimotor representation, derived selectional
preference, and frequency/dominance -- land on the SAME frontier: precision +0.05-0.06 CI-sep, survival retained
61-74%, no point restoring precision to verb-only without a survival cost.** Four independent brain-faithful mechanisms
agreeing on one frontier is strong evidence the residual is NOT a missing cue. It is structural: (a) ~9-19% of the
over-firing is event-DOMINANT nouns used as NAMED-EVENT REFERENCES (battle/war/storm -- Sec 4b; the frequency prior
actually KEEPS these, so it cannot help), NOT a sense/frequency problem at all; and (b) the extraction-precision
INSTRUMENT is annotation-confounded (MAVEN-ERE annotates only relation-participating triggers, so a kept true
event-reading counts against precision) -- so "winning" may be UNMEASURABLE on this instrument. The decisive test is
END-TO-END reasoner accuracy (does the gate change the timeline ANSWERS?), not extraction precision -- Sec 4d/8.

### 4g. THE DECISIVE TEST — end-to-end through the SOLVED reasoner: the gate LOSES; the brief's premise is REFUTED.
Extraction precision is the wrong target (p2 found over-extraction does not degrade reasoner accuracy), so I ran the
gate through the ACTUAL solved temporal reasoner (`exp_nominal_gate_endtoend_v1`, TB-Dense, 1586 gold BEFORE/AFTER
pairs; reasoner held FIXED, extraction the only variable). ANSWERED-CORRECT (cor/tot): incumbent 0.0971 -> joint_cop
0.3480 -> **joint_nom (ungated) 0.4937** (87% of the gold-event ceiling 0.5681) -> joint_nom_wsd (gated) **0.4590**
(-0.0347 CI[-0.0435,-0.0259], CI-separated WORSE) -> joint_nom_dom (dominance) 0.4470 (-0.0467 CI-sep worse).
CONDITIONAL accuracy (cor/ans) is FLAT across arms (~0.58-0.60), so answered-correct is driven by COVERAGE
(ans/tot: ungated 0.847 -> gated 0.781) -- gating only THROWS COVERAGE AWAY. **The ungated nominal channel is already
the downstream winner; gating it -- by ANY brain-foundational cue (WSD or dominance) -- makes the reader answer FEWER
timeline questions correctly, with no gain in answer quality.** This REFUTES the brief's premise (that the precision
drop is a liability requiring a gate before default-ON): end-to-end, the precision drop is NOT a cost -- it is an
artifact of the extraction-precision instrument (MAVEN/TB gold do not annotate every eventive nominal, so a kept true
event-reading is scored as a false positive). **The real problem -- make the biggest temporal survival lever a safe
default-ON gain -- is solved by turning the nominal channel ON UNGATED (0.4937 end-to-end, cond-acc not degraded), NOT
by gating it.** The gate is a rigorously-built located NEGATIVE: faithful to the brain's sense mechanisms, it works at
the extraction level but is net-NEGATIVE at the level that matters. (TB-Dense is the reasoner's validated home gold;
a MAVEN end-to-end confirmation is a cheap follow-on.)

## 5. KEY REALIZATIONS (the enabling moves)
- **The flat sentence-bag readout is INDISTINGUISHABLE FROM RANDOM NOM-DROPPING (the twin caught it).** Random dropping
  raises overall precision purely by down-weighting the low-precision NOM channel; the info-free twin exposed that the
  naive gate's "precision gain" was this artifact. Adding parse-selected context helped on TB-Dense but NOT at MAVEN
  power; it was the SELECTIONAL-RESTRICTION cue (argument structure) that made the twins reliably LOSE on both golds —
  i.e. the load-bearing token signal is the governor's argument-frame, not context averaging (Sec 4c).
- **The committed reading is the ARGMAX sense's cluster, not the summed cluster mass.** An early summed-event-mass rule
  fired on "painting"-object because WordNet has more act-senses than artifact-senses, so mass summed high even when the
  single best sense was the artifact. Switching to the EVENT-vs-OBJECT margin (best event sense vs best object sense;
  theta=0 == argmax-is-eventive) fixed the positive control and gave a principled sweepable knob.
- **Compute the STRUCTURAL cap before reading the aggregate.** Enumerating the over-firing population first revealed that
  ~9-19% of the "false positives" are non-polysemous eventive nouns no WSD gate can flip, and that hub COVERAGE is not
  the bottleneck (0 uncovered) — so the aggregate precision ceiling and the correct located-negative were known before
  interpreting the gated number.
- **MAVEN precision is annotation-confounded; TB-Dense is the clean instrument.** MAVEN-ERE annotates only
  relation-participating triggers, so its NOM "precision" is depressed for both arms equally — valid for the GAIN, not
  for the absolute level.
- **The w2v sense signatures for event vs object are cos 0.93 collinear — the readout literally cannot see the
  distinction.** Measuring the representation (not just the accuracy) was what turned "the readout is weak" into "the
  readout is fed two identical vectors." The grounded space separates them (cos 0.51) — a decisive brain-foundational
  diagnosis of WHY.
- **But the obvious fix (grounded signatures) was REFUTED at power — and the small-n gold nearly fooled me.** TB-Dense
  (n=76) said grounded un-biases the gate; MAVEN (n=1874) said it does not (worse precision/survival, twin does not
  lose). Separating the signatures is necessary but not sufficient; the context->sense selection is the real bottleneck,
  in BOTH spaces. **The enabling realization: event-vs-result is an ARGUMENT-STRUCTURE distinction, not a lexical one —
  no representation swap fixes it; the selectional/aspectual frame is the primary mechanism.** (Always power-test a
  representation claim on the larger gold before believing it.)

## 6. CONTROLS (what each excludes) — see frontmatter `controls`
Shuffled-diagnosticity, permuted-context, and shuffled-cue twins each destroy a different part of the token->context
binding and each LOSE CI-sep with the brain-foundational context (excluding a shape/weight/lemma-identity artifact); the
FLAT-bag context FAILS the shuffled-diagnosticity twin (excludes the naive readout as sufficient); the additive subset
property excludes any VERB/COP regress; the cue-only reference excludes the selectional cue as a standalone gate (it does
almost nothing alone). The positive control (same lemma, two readings) excludes a type-level lexicon.

## 7. PROPOSED hdlab CHANGE (Q111 — strategy lands it; NOT landed here)
1. **New organ `hdlab/nominal_wsd_gate.py`**, promoted from `experiments/_nominal_wsd_gate.py` (drop the sys.path shim;
   import only `hdlab.{meaning_foundation, diagnostic_context_wsd, underspecified_sense_reader}` + wordnet). Public:
   `keeps(context_words, lemma, vec_lookup, *, theta, abstain_fire, gamma, topk) -> bool`,
   `selectional_context(words, upos, heads, idx)`, `sort_cue(words, upos, heads, idx)`.
2. **Hook it into `hdlab/situation_reader.py::_build_joint_temporal_reasoner` (lines ~3333-3336).** Where it currently
   does `loc = JF.joint_event_ranks(..., nominal=self.joint_nominal_events, ...)`, filter the NOM-provenance entries:
   for each `j` with `loc[j]=="NOM"`, keep it only if
   `nominal_wsd_gate.keeps(selectional_context(toks,up,hd,j), toks[j].lower(), vec_lookup, theta=THETA, ...)`
   (with the selectional resting-bias combined as in the combined arm). Add a flag
   `joint_nominal_wsd_gate: bool = True` (gate ON whenever the nominal channel is on) in CAPABILITY_FLAGS;
   `all_capabilities_off()` forces it False. **Additive + no-regress (proven, witness W2):** VERB/COP entries are
   untouched, so `recovered(gated)` is a strict subset of `recovered(ungated-nominal)` and a superset of
   `recovered(joint_cop)` — off-vs-on the VERB/COP event set is byte-identical.
3. **RECOMMENDATION, REVISED BY THE DECISIVE END-TO-END TEST (Sec 4g): turn `joint_nominal_events` DEFAULT-ON UNGATED;
   do NOT wire the gate.** End-to-end the ungated channel is the winner (answered-correct 0.4937, 87% of ceiling,
   conditional accuracy not degraded); the WSD gate and the dominance gate BOTH reduce answered-correct CI-separated
   (they only drop coverage). The gate organ (`_nominal_wsd_gate.py`) is a rigorously-built located NEGATIVE, kept for
   the record and for any consumer that genuinely needs extraction precision over coverage — but the temporal reasoner
   does not. So the additive hook (items 1-2) is OPTIONAL and default-OFF; the load-bearing change is flipping
   `joint_nominal_events` to True.
4. **What this costs to be sure of:** confirm the end-to-end result on MAVEN (a cheap follow-on) and, if any OTHER
   nominal-channel consumer is added later that weights precision over coverage, re-evaluate the gate for that consumer
   specifically. For the temporal reasoner the evidence is decisive: ungated wins.
- **No other consumers regress.** The only hdlab consumer of the nominal channel is `situation_reader`; spatial uses
  `joint_spatial_edges/frames` (untouched). Grep-confirmed.

## 8. ADJACENT COMPONENTS (brain-foundational status + what they seed)
- **A WELL-POWERED SELECTIONAL-PREFERENCE / THEMATIC-FIT organ — the real upstream need (Sec 4e).** The derived
  selectional preference is the brain's actual mechanism but is DATA-STARVED at GUM's 301 docs (0.44 coverage, weak
  per-verb) — it ties the hand list, no better. A selectional-preference organ built from a LARGE parsed corpus (or from
  the substrate's `generalized_event_knowledge` event store) + the morphosyntactic aspectual cues (determiner
  mass-vs-count, number singular-vs-plural, Grimshaw's non-argument diagnostics) + a cue for NON-verb governors
  (copular/adjective/noun heads, ~half the nominals) is the highest-leverage follow-on, and a candidate NEW problem. The
  prototype (`_selectional_preference.py`, `exp_nominal_gate_selectional_v1.py`) is the seed.
- **Parser quality (`arc_parser`, UAS 0.79) directly caps the governor extraction (Sec 4e).** A stronger parser lifts
  both the selectional context and the selectional preference. A live optimization target.
- **The distributional sense representation is not the ATL's — but grounded signatures are NOT the fix here (Sec 4c).**
  Measured: event/object w2v sigs are cos 0.93 collinear (grounded 0.51), so the distributional space is genuinely
  non-brain-foundational for SORTAL distinctions; but the grounded swap was REFUTED at power for THIS gate (the context
  selection, not the signature separation, is the bottleneck). For the named fork
  `break_the_contextual_input_encoding_ceiling_for_specific_sense_selection`, the grounded representation is a real lever
  for OTHER (sortal) distinctions and worth a controlled test there; for event-vs-result the argument-structure system is
  the answer. We did NOT conclude "needs a neural model".
- **The p2 parse (`arc_parser`, UAS 0.79) — the selectional context/cue depend on it.** A stronger parser directly
  improves the governor/argument selection. OUR-INVENTION-quality (a hashed-feature UD parser), a live optimization
  target.
- **The other consumers of `diagnostic_context_wsd` (the meaning-channel WSD) use FLAT sentence context.** This problem
  shows PARSE-selected (structure-selected) context makes the biased competition demonstrably use the right cue — a
  general brain-foundational upgrade those consumers should be revisited to adopt (controlled semantic cognition
  amplifies structurally-selected features, not the sentence average).
- **Referring-expression / discourse-status (trigger vs named-event reference) — Sec 4b.** The ~9-19% non-WSD FP residual
  is a distinct organ (is this token a NEW event trigger or a mention of a known event?), a candidate follow-on problem.

## AUDIT UPDATE (for strategy to fold into notes/BRAIN_FOUNDATIONAL_AUDIT.md — MEANING/WSD tier + TIME sec.2b)
The eventive-nominal channel now has a brain-foundational per-token context/WSD gate (biased competition over the curated
hub + selectional restriction, over the parse-selected neighborhood). It RESTORES extraction precision CI-separated over
the ungated channel on both modern golds (TB-Dense +0.062, MAVEN +0.054) with the info-free twins LOSING for the
combined (readout + selectional-cue) arm, retaining 66-77% of the survival lift — but does NOT fully close the precision
gap to verb-only, and I drilled WHY to the representation and back: **the event-vs-object sense signatures are cos 0.93
COLLINEAR in the distributional w2v space the meaning channel uses (grounded sensorimotor space: cos 0.51), so the
distributional representation is genuinely non-brain-foundational for SORTAL distinctions — but a grounded-signature swap
does NOT fix the gating at power (MAVEN, refuted), because event-vs-result is an ARGUMENT-STRUCTURE distinction that the
selectional/aspectual frame carries, not a lexical-similarity one in any representation.** The load-bearing token signal
is the selectional cue, not the lexical readout. Plus ~9-19% of the precision defect is a trigger-vs-named-reference
distinction (not WSD), and the hub COVERAGE fork is closed (0 uncovered). **DECISIVE (Sec 4g): end-to-end through the
solved temporal reasoner the gate is net-NEGATIVE — answered-correct ungated 0.4937 (87% of ceiling) vs gated 0.4590
(CI-sep worse), conditional accuracy flat — so the eventive-nominal channel should go DEFAULT-ON UNGATED; the precision
drop is an extraction-instrument artifact, not a downstream cost, and the WSD gate (though brain-faithful and
precision-restoring at the extraction level) should NOT be wired.** The eventive-nominal channel is thus a safe default-ON
gain as-is; the WSD-gate follow-on is retired for the temporal reasoner.

## WHAT I WOULD WITHDRAW FIRST IF WRONG
The load-bearing claim is now the end-to-end one (Sec 4g): "gating reduces answered-correct; ungated wins at 87% of the
ceiling." It is CI-separated on TB-Dense (the reasoner's validated home gold, 1586 pairs) and mechanistically clear
(conditional accuracy flat -> answered-correct tracks coverage -> gating cuts coverage), and it agrees with p2's
independent cond-acc finding — but it is ONE gold; a MAVEN end-to-end confirmation is the cheap check that would most
change the verdict if it disagreed (it should not, but it is unrun here). The earlier extraction-precision claim
("gate restores precision +0.05-0.06 CI-sep") is robust but is precisely the instrument the end-to-end test shows is
the WRONG target, so it is no longer load-bearing for the recommendation.

---

**TLDR (plain English):** Our reader recently got much better at following a story's timeline by treating certain nouns
("the attack", "the construction") as happenings — its single biggest improvement — but it over-counts words that have a
second, non-event meaning ("the building" can be the act OR the thing built), so the whole improvement was left switched
off. I built a part that looks at each such word IN ITS OWN SENTENCE and decides which meaning is intended, reusing the
meaning-in-context machinery the reader already has, and — crucially — feeding it the grammatically-relevant words picked
out by the sentence's structure rather than the whole sentence. It makes the reader measurably more accurate about which
nouns are happenings (a real, statistically-clean gain that a scrambled-context version does NOT reproduce) while keeping
most of the big timeline improvement. It does not make it perfect: about a fifth of the mistakes are a different kind of
problem (naming a known event vs reporting a new one), and telling the two meanings of the SAME word apart is genuinely
hard — I found the reason: the reader judges word meaning by which words tend to appear together, and in that view the
two meanings of "building" look 93% identical (both live around construction talk). The brain instead judges by what you
do and see (an action vs a solid visible thing), where they clearly differ — but I tested feeding the reader that
grounded view and, at scale, it did NOT help, because deciding which meaning applies is really a matter of grammar (what
the surrounding verb expects), not word-similarity in any view. I even added the strongest cue the brain uses — how
COMMON each meaning is — and it still didn't win. **The decisive discovery came from testing the thing that actually
matters: does any of this change the reader's timeline ANSWERS? It does not — in fact every version of the "be pickier"
gate makes the reader answer FEWER questions right, because it removes useful events, and the reader was already robust
to the occasional wrong one.** So the honest conclusion flips the original plan: the biggest timeline improvement should
simply be switched ON as-is; the "it's too imprecise" worry was an artifact of how we were scoring, not a real cost to
the reader. The gate was a well-built answer to the wrong question.

**QUESTIONS:** one decision is the owner's — the label. The brief's mechanism (a WSD gate to make the channel
default-on-safe) is REFUTED end-to-end, and the real goal is met a different way (default-ON UNGATED). That is a
first-class REFUTED-and-resolved outcome; I left the frontmatter at PARTIAL (a rigorously-built gate + a decisive
refutation + the resolution) but REFUTED is defensible. Your call.

**NEXT STEPS:** (1) **flip `joint_nominal_events` DEFAULT-ON UNGATED** (strategy; the decisive change — the channel is
already the downstream winner, 87% of ceiling, cond-acc not degraded) and do NOT wire the gate; (2) confirm the
end-to-end result on MAVEN (cheap follow-on); (3) the WSD gate + `_nominal_wsd_gate.py` are retired for the temporal
reasoner but kept for any future consumer that weights extraction precision over coverage; (4) still-live upstream
problems this drilling LOCATED, independent of the gate: a well-powered selectional-preference / thematic-fit organ
(Sec 4e), parser UAS 0.79 (Sec 4e), the trigger-vs-named-reference discourse organ (Sec 4b), and the grounded
representation for OTHER sortal distinctions (Sec 4c) — candidate NEW problems.
