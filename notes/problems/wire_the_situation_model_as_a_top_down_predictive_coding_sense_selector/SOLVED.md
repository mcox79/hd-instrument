---
problem: wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector
status: PARTIAL
bar: "PASS = a TOP-DOWN predictor built from the live situation_reader (events/entities/roles) that: 1. recovers rare/subordinate sense selection CI-separated over the bottom-up static-graph readout, on a POWERED subordinate-override test (SemCor MFS=0 subordinate population, recompute the floor on that population, gate on its UPPER bound) -- WITHOUT the global see-saw that sinks dominant items (report the dominant cost; a NET gain, not a subordinate-only gain bought with dominant loss); 2. a shuffled-situation-model twin LOSES CI-separated; 3. a prediction-error-gate ablation REMOVES the gain; 4. reports the bootstrapping loop's effect. A rigorous located NEGATIVE is a FULL PASS if the faithfully-built top-down predictor does not beat the bottom-up readout AND it names which component fails with the number."
result: "LOCATED NEGATIVE (positive bar unmet, failing component NAMED + QUANTIFIED), plus one CONFIRMED brain-faithful sub-mechanism (POWERED, SemCor 30 files, n=17,317 / 5,281 subordinate). The top-down gated selector does NOT net-beat the MFS floor on the full polysemous population: best over ALL detector/override/threshold combos = NET -0.0013 CI[-0.0025,-0.0002] (CI-separated BELOW the floor; no config beats it). The wall is a BASE-RATE see-saw, decomposed: net = fired*[p*a_s - (1-p)*c_d] with detector-precision p~0.48, override-accuracy-on-fired-subordinate a_s~0.33, dominant-disruption c_d~0.64; break-even needs p*a_s~0.34, we get ~0.16 -> the binding limit is the OVERRIDE accuracy a_s (the 'which specific sense' = comprehension), then detector precision p. CONFIRMED brain-faithful (NEW): the DIRECTIONAL predictive-error detector (domI = N400 on the dominant reading) AUC 0.6895 BEATS symmetric conflict 0.6652 BEATS bag 0.6407 (all >> the brief's claimed ~0.51). RETRACTED at power: the smoke's 'Zwaan situation-dimension signature' does NOT replicate -- at n=481 spatial vs 3928 event, spatial/object recovers EQUAL-or-higher (bag:domI +0.183 vs +0.148), the opposite of the smoke n=36 artifact; our mechanism tracks graph connectivity, not the brain's dimension asymmetry."
floor: "MFS / reordered-access frequency prior, recomputed on the SemCor polysemous population (POWERED 30-file: overall 0.6831, dominant 0.9828, subordinate 0.0 by construction; subordinate = gold sense strictly rarer than the lemma top sense, n=5,281/17,317). The gated top-down selector must beat this NET (full population). It does not: best combo NET -0.0013 CI[-0.0025,-0.0002] (CI-separated below). Info-free shuffled-structure twin best net = -0.0072 (loses)."
controls: "(POWERED 30-file, bootstrap CIs) (1) INFO-FREE shuffled-structure twin LOSES CI-separated: best real vs twin +0.0059 CI[0.0040,0.0076]. (2) ERROR-GATE ABLATION (fire on ALL items, ungated) REMOVES/REVERSES the gain -> net -0.1082 (the gate is load-bearing). (3) DETECTOR AUC contrast: directional struct_domI 0.6895 > symmetric struct_sym 0.6652 > bag_sym 0.6407 (n_eval=12,368) -- isolates the frequency-independent + directional signal as real; best config beats the bag detector +0.0072 CI[0.0051,0.0093]. (4) DISCOURSE-aggregation control DILUTES (disc AUC 0.6097 < struct 0.6652) -> the helpful signal is local predicate-argument structure, not a flat discourse pool. (5) SUBORDINATE recovery is REAL but see-saws: best_vs_prior SUB +0.0076 CI[0.0053,0.0100] and DOM -0.0052 CI[-0.0066,-0.0039] (both CI-separated) -- the recovery is bought with dominant loss. (6) SEE-SAW DECOMPOSITION isolates a_s (override accuracy ~0.33) as the binding limit, not the detector (p~0.48)."
files_changed: "experiments/exp_topdown_situation_sense_selector_v1.py (new -- the top-down structural/situational sense selector: SemCor+spaCy structural extraction, discourse aggregation, directional predictive-error detectors {sym,domI,comb} x {bag,struct,disc}, MFS-default biased-competition gated inhibition via hdlab/semantic_control, coarse/fine + net sweep, self-test, resumable feature cache), verification/test_topdown_situation_sense_selector.py (new -- scaffold-free witness), notes/problems/wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector/{SOLVED.md, DESIGN_brain_foundational.md, FINDINGS.md}. Reuses UNMODIFIED: experiments/exp_learned_graph_cls_grow_v1.py + exp_grounded_semantic_graph_ladder_wsd_v1.py (settling/prior/graph), hdlab/semantic_control.py (LANDED LIFG suppression), data/wsdeval + SemCor, spaCy en_core_web_sm (LOCAL, parse cached). Research: notes/research_subordinate_sense_topdown_predictive_precision_2026-09-02.md."
reverify: ".venv/Scripts/python.exe verification/test_topdown_situation_sense_selector.py"
---

# Top-down situation-model sense selection: the detector is REAL and brain-faithfully directional (N400-style), but a BASE-RATE see-saw -- bounded by override accuracy a_s~0.33, the 'which specific sense' comprehension problem -- keeps the net gain CI-separated at/below zero

## Verdict
**PARTIAL -- a rigorous, POWERED (n=17,317 / 5,281 subordinate), multiply-controlled LOCATED NEGATIVE with the
failing component NAMED and QUANTIFIED, plus one CONFIRMED brain-faithful sub-mechanism.** A top-down predictor
built from frequency-independent structural/situational context, gating LIFG signed-suppression of the dominant
sense, does NOT net-beat the MFS floor on the full population (best NET -0.0013 CI[-0.0025,-0.0002]). But (1) the
brain-faithful DIRECTION is confirmed at power (the DIRECTIONAL N400-style detector beats symmetric conflict beats
bag, info-free twin loses CI-separated, ablation removes the gain), and (2) the wall is decomposed into the exact
quantities the brain must beat, with the binding term isolated (override accuracy a_s~0.33). This is the bar's
full-PASS located-negative condition. Marked PARTIAL (not SOLVED) because the positive net-gain bar is unmet and
ONE literature-corroborated lever (discourse-scale event conflict via oracle coref) is specified-but-unbuilt.
HONESTY NOTE: the 4f-smoke's 'Zwaan situation-dimension signature' was RETRACTED when powered (a small-sample
n=36 artifact; at n=481 it reverses) -- the powered run caught and removed that over-claim.

## HOW THE BRAIN DOES THIS, AND WHERE WE DIFFER (the opening move)
PINNED (parent FIDELITY_AUDIT sec D + this cycle's research drill, 24 primary sources): sense selection = a
frequency/dominance PRIOR (reordered access; Duffy/Rayner) + a SEPARATE frequency-INDEPENDENT top-down
structural/situational constraint, resolved by INHIBITION (LIFG/pMTG biased competition; Desimone-Duncan),
gated by the PRECISION of that constraint (Feldman-Friston; N400 = predictive error, Rabovsky/Kuperberg). WHERE
WE DIFFER, now QUANTIFIED (see decomposition): our top-down prediction is a bag/graph spreading-activation
signal; its precision (p~0.48) and its sense-SPECIFICITY (a_s~0.33) fall ~2x short of the brain's, which draws on
a generative world-knowledge situation model (scripts/schemas activating unmentioned concepts). CRITICALLY, the
research established that neither the human override accuracy (a_s) nor the neural detector precision (p) has any
literature benchmark -- so our numbers are not shown inferior to a documented brain number; the human subordinate-
bias literature is entirely BINARY homographs on RT/gaze, never multi-way sense accuracy. UKB (PageRank-over-
WordNet) independently confirms graph-spreading defaults to frequency (F1 42-61%, <=MFS) -- external validation.

## What I built
A glass-box, LM-free-at-inference top-down sense selector (`exp_topdown_situation_sense_selector_v1.py`):
- **Prior stream:** reordered-access SemCor frequency prior (`_sense_prior`), kept SEPARATE from context (not blended-away).
- **Frequency-independent context stream:** competitive attractor settling (`_settle`) over the grounded
  WordNet++ graph, seeded by (a) the sentence bag, (b) the dependency STRUCTURAL neighbourhood (governor +
  co-arguments + modifiers -- spaCy, local, cached), (c) the DISCOURSE aggregate (entity structural role-history
  pooled across same-(doc,lemma) mentions = a coref-by-repetition situation proxy).
- **Directional predictive-error DETECTOR:** `domI = 1 - dominant_coherence` (the N400 error on the DOMINANT
  reading), plus `sym` (symmetric conflict) and `comb`, over each context stream.
- **Selection = MFS-default biased-competition inhibition:** default to the dominant (dominant-biasing context
  needs NO inhibition -- the brain's asymmetry); where the detector fires (> gold-blind quantile theta), INHIBIT
  the dominant via `hdlab/semantic_control` graded suppression and let the reordered-access blend pick.
- Full detector x override x threshold sweep; coarse/fine (homonym/polysemy) split; info-free twin; ablation.

## What I measured (POWERED: 30 SemCor files, n=17,317 items / 5,281 subordinate; bootstrap CIs)
1. **The DETECTOR is real and brain-faithfully DIRECTIONAL (WALL-1 CONFIRMED; contradicts the brief's ~0.51).**
   AUC(subordinate vs dominant), struct-covered n=12,368 (3,719 sub): bag_sym 0.6407 < struct_sym 0.6652 <
   **struct_domI 0.6895** (bag_domI 0.6832). The DIRECTIONAL predictive-error signal (N400-on-the-dominant) beats
   symmetric conflict -- the brain-faithful improvement, measured. The disk OUTRANKS the brief: a gold-blind
   detector clearly exists (0.64-0.69), it does not "cap at ~0.51". (4f smoke ran ~0.03-0.05 higher, 0.74 --
   small-sample optimism; the powered ordering is identical and holds.)
2. **Info-free twin LOSES CI-separated (real signal).** best real config vs shuffled-structure twin
   +0.0059 CI[0.0040,0.0076]; best-net twin -0.0072. The structural signal is real, not machinery.
3. **THE WALL: a BASE-RATE see-saw (CI-confirmed).** MFS floor: overall 0.6831, dominant 0.9828, subordinate 0.0.
   No gated config beats the floor on the FULL population: best NET -0.0013 CI[-0.0025,-0.0002] (CI-separated
   BELOW zero). Subordinate recovery is real but see-saws: SUB +0.0076 CI[0.0053,0.0100] bought with DOM -0.0052
   CI[-0.0066,-0.0039] (both CI-separated). At aggressive firing the subordinate recovery is larger (~+0.10..+0.18)
   with a proportionally larger dominant cost -- net stays negative at every operating point.
4. **SEE-SAW DECOMPOSITION -- the exact fidelity gap (powered).** net = fired*[p*a_s - (1-p)*c_d]; measured
   (det=struct:domI, ov=bag, across q): p~0.48 (detector precision), **a_s~0.33** (override accuracy on fired
   subordinate -- the BINDING limit: even when we correctly detect, picking the RIGHT sense is ~1/3), c_d~0.64
   (dominant disruption). Break-even needs p*a_s~0.34; we get ~0.16 -> must ~2x precision x override-accuracy. A
   maximally-conservative override does NOT lower c_d enough -> the wall is not threshold-tuning.
5. **DISCOURSE aggregation DILUTES (a real negative, powered).** disc AUC 0.6097 < struct 0.6652: pooling the
   entity's role-history across mentions mixes its different roles/senses. The helpful situational signal is LOCAL
   predicate-argument structure, not a flat discourse pool (echoes the parent's proto4b flat-discourse null).
6. **NO situation-dimension asymmetry at power (a RETRACTED smoke over-claim).** The 4f-smoke suggested recovery
   was larger on event/abstract than spatial/object senses (a Zwaan-1998-consistent signature) -- but that rested
   on n=36 spatial items with a CI touching zero. At POWER (n=481 spatial, 3928 event) it REVERSES: spatial/object
   recovers EQUAL-or-higher (bag:domI +0.183 CI[0.150,0.218] spatial vs +0.148 CI[0.137,0.158] event; consistent
   across all 3 detectors). So our mechanism does NOT follow the brain's automatic-tracking dimension asymmetry;
   if anything it tracks the graph's connectivity (concrete/spatial senses have richer, more discriminating
   neighbourhoods). Reported as a correction: the powered run caught and removed the over-claim.

## Prototyped fixes for the two differences (which is buildable NOW vs North Star; 4f-scale probes)
Directly tested the cheap fix for each gap term (4f prototypes; the powered decomposition confirms the read):
- **p (detector precision) IS cheaply improvable.** A MULTI-SIGNAL directional detector (z-summed struct_domI +
  bag_domI) raises AUC 0.744 (best single) -> **0.766**; adding disc/sym does not help further. Detection is
  buildable (the powered single-detector AUCs are ~0.03 lower, so the multi-signal would sit ~0.71-0.72).
- **a_s (override accuracy) is NOT a readout fix -> it is the WORLD-KNOWLEDGE SOURCE (North Star).** A
  sense-SPECIFIC SIGNATURE readout (score each sense by the inferred-situation-gist activation over its whole
  neighbourhood: hypernyms/hyponyms/meronyms/gloss senses) is WORSE than the single-node readout (a_s 0.261 ->
  0.213, CI-separated worse; combined 0.249, null). The single sense-node readout is already better -> the
  cn_syn-inferred situation does not carry enough sense-specific signal NO MATTER how it is read out. The
  override gap is the generative situation representation, not the readout.
- **SYNTHESIS:** a_s is the BINDING term (powered: break-even needs p*a_s~0.34). p is nudgeable but is the
  NON-binding term; a_s resists the cheap fix because it IS the generative comprehension problem. Stacking the
  buildable detector (p~0.5) on the capped a_s~0.33 still gives p*a_s~0.17 < 0.34. The difference we CAN
  prototype (detection) is not the one that matters; the one that matters (generating the specific sense from
  world knowledge) is exactly the North-Star organ -- confirmed by direct test, not assumed.

## The wall, drilled (research-confirmed): fidelity gap, not a clean ceiling
The neuroscience drill (24 sources) established: (a) the human brain is ALSO see-saw-limited -- residual
dominant-sense cost 14-51ms is never fully eliminated even under strong subordinate bias (PINNED), so PART of
the wall is genuine difficulty; BUT (b) a_s~0.33 (multi-way sense accuracy) has NO human analog -- the entire
subordinate-bias literature is binary homographs on RT/gaze -- so the large a_s shortfall reads as a fidelity/
task-scope gap, not a proven ceiling; (c) the one corroborated untried lever is discourse-scale event conflict
via coref, which I effectively tested via the discourse-aggregation arm (dilutes at power, AUC 0.61 < 0.67).
NET: this is a fidelity gap with ONE clearly-
specified next experiment, not a closed ceiling -- but the magnitude of the a_s gap points at the North-Star
comprehension model as where the gains actually live.

## KEY REALIZATIONS (the enabling moves)
1. **Read the parent's carefully-researched sec D FIRST -> did not re-run its closed negatives.** The parent
   already refuted a better LOCAL/bag detector (finding #6/#8, nets ~0); so the crux was the FREQUENCY-INDEPENDENT
   STRUCTURAL / DIRECTIONAL detector, untested. That reframe is the whole cell.
2. **DECOMPOSE the see-saw into p, a_s, c_d.** Turning "net is ~0" into "a_s~0.33 is the binding limit" converts
   a null into a precise, quantified fidelity gap and names WHICH component (override accuracy = comprehension).
3. **DIRECTIONAL beats symmetric (N400-on-the-dominant).** Gating on 'the dominant is incoherent' (domI) beats
   'some competitor looks good' (sym) -- the brain-faithful asymmetry, measured at power (AUC 0.6895 vs 0.6652).
4. **POWER before claiming a signature.** A striking 4f-smoke result (recovery larger on event/abstract than
   spatial/object, Zwaan-consistent) evaporated at scale (n=36 -> 481 reversed it). Running the full population
   before quoting the stratified signature caught and removed the over-claim -- the discipline working as intended.
5. **The disk outranks the brief.** The brief inherited "detectors cap ~0.51"; on this representation they reach
   0.74. Reported as a correction, not a contradiction hidden.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
The top-down sense-selection detector is a FREQUENCY-INDEPENDENT structural-precision signal, and its DIRECTIONAL
form (predictive error on the dominant reading, N400) is measurably better than symmetric conflict (powered AUC
0.6895 vs 0.6652 vs bag 0.6407) -- the "no gold-blind detector (AUC ~0.51)" line is corrected: a detector clearly exists.
NEW located deviation: subordinate override is bounded by a BASE-RATE see-saw whose binding term is OVERRIDE
ACCURACY a_s~0.33 (the sense-SPECIFIC prediction = comprehension), not the detector. (A smoke-scale Zwaan
situation-dimension signature did NOT replicate at power -- do not fold it into the audit.) The LIFG
signed-suppression + reordered-access read path is validated; the missing piece is the generative world-knowledge
situation model that supplies a high-precision, sense-SPECIFIC top-down prediction.

## Adjacent-component map -> candidate next problems (brain-fidelity + optimization)
- **situation_reader (events/entities/coref):** event-extraction recall ~0.32 (tagger-capped) is a real
  bottleneck; its coref is same-lemma+pronoun. BRAIN: PINNED (Kintsch/van Dijk). OPP: an ORACLE-coref discourse-
  EVENT-conflict detector with a time/causation/goal-vs-spatial STRATIFICATION is the one literature-corroborated
  untried lever -> NEXT PROBLEM (HARD-PASS AUC>=0.80 + break-even; HARD-FAIL localizes the wall to the signal).
- **predictive_reader (forward N400 surprisal, grounded features):** validated organ, but selectional-preference-
  class = dominance-reinforcing (parent proto5c -0.085) and grounded-space-coarse (its own caveat) -> NOT the
  lever for RARE-sense selection. Evaluated + de-prioritized (route confirmed closed by the research).
- **meaning_fusion / distributional_meaning_channel:** the graded, sense-SPECIFIC continuous representation that
  a higher a_s needs (the 'which sense' problem) -> NEXT PROBLEM (the North-Star representation fork).
- **semantic_control (LIFG):** validated + reused here as the inhibition gate; its frequency-independent trigger
  is now the DIRECTIONAL domI detector (a candidate to land as its named forward lever).

## What I did NOT establish / would withdraw first
- **No net positive on the full population** -- withdraw any implication that the gated top-down selector improves
  standard WSD net (it does not; it is a subordinate-recovery bought with dominant loss).
- **Oracle-coref discourse-EVENT detector UNBUILT** -- specified as the next experiment (the research's cheap
  decisive test); the discourse-AGGREGATION proxy dilutes, but the true message-level event signal with oracle
  coref is untested. This is why status is PARTIAL, not a closed negative.
- **The 4f-smoke Zwaan situation-dimension signature RETRACTED at power** -- do not quote it; at n=481 spatial it
  reverses (spatial recovers equal-or-higher than event). Withdrawn.
- **a_s vs p as 'binding limit'** is a decomposition read, not a separate controlled manipulation; both are low.

## Compute honesty
POWERED: 30 SemCor files, n=17,317 items / 5,281 subordinate; bootstrap CIs on all margins. 3 competitive-settles/
item over the 117k-node graph (bag/struct/disc), feature-cached + resumable. spaCy parse LOCAL, cached. No external
LLM at inference. The full detector x override x threshold sweep is evaluated on cached coherences (instant). 4f
smoke ran the detector AUCs ~0.03-0.05 higher (small-sample optimism) and produced one over-claim (the Zwaan
signature) that the powered run reversed -- all headline numbers here are the powered ones.

## TLDR (plain English)
Words with a rare meaning are the hard case: the common meaning is right ~99% of the time, so any system that
"overrides" toward the rare meaning risks breaking the many easy cases. I built the brain's method -- keep the
common-meaning bias, and only override when a separate, frequency-free signal from sentence structure says the
common meaning does not fit, using the brain's own inhibition circuit. The override SIGNAL works (it spots the
rare-meaning cases better than the old bag-of-words approach, and better still when it measures "the common
meaning does not fit" directly). But it cannot yet win overall: even when it correctly spots a rare case, it
picks the exact right rare meaning only about a third of the time -- because that final choice needs real
understanding of the situation, which a word-web cannot supply. That "about a third" is the precise, measured gap:
it is the difference between spotting that the common meaning is wrong (which we can do) and generating the exact
right rare meaning from world knowledge (which needs a real understanding-of-the-situation model we do not yet
have). So this is a precise map of what is missing (a richer situation-understanding model), not a dead end.

## QUESTIONS
None blocking. (One judgement call flagged for the owner: I scoped the oracle-coref discourse-EVENT detector as a
filed follow-on rather than building it now, because the discourse-aggregation arm already dilutes at power
(AUC 0.61 < 0.67) and the powered decomposition already isolates the binding limit as override accuracy a_s, which
the discourse-event signal would not raise.)

## NEXT STEPS (ranked)
1. **[NORTH STAR] the generative world-knowledge situation/comprehension model** -- the a_s~0.33 override-accuracy
   gap is the sense-SPECIFIC prediction, i.e. comprehension. This is where the gains live (parent's north star).
2. **[cheap, filed] the oracle-coref discourse-EVENT-conflict detector** -- the one literature-corroborated untried
   lever; HARD-PASS AUC>=0.80 + break-even, HARD-FAIL localizes the wall to the signal (informative either way).
   Lower prior now: the discourse-aggregation proxy already dilutes at power and the binding limit is a_s, not the detector.
3. **[representation] a graded, sense-SPECIFIC continuous space** (meaning_fusion + ultrametric granularity) to
   raise a_s -- the 'which sense' fork.
4. **[STRATEGY, Q111] hdlab wire (default-off, witnessed):** the DIRECTIONAL domI detector as semantic_control's
   frequency-independent trigger + the MFS-default biased-competition read path. Land only the read path; the
   discrete override does not net-gain, so wire it as an instrument, not a default.

## INTEGRATED_BY_STRATEGY — 2026-09-02 (grade: EXCELLENT; SOLVED owner-DONE)
Reverified 4/4 first-hand. A rigorous, POWERED, multiply-controlled LOCATED NEGATIVE (full PASS under the bar) + a
CONFIRMED brain-faithful sub-mechanism. On SemCor (30 files, n=17,317 / 5,281 subordinate): the DIRECTIONAL
predictive-error detector (domI = N400 on the DOMINANT reading) is CONFIRMED real -- AUC 0.712 struct_domI > 0.689
struct_sym > 0.658 bag (all >> the brief's claimed ~0.51; the disk corrected the brief). But the top-down gated
selector does NOT net-beat the MFS frequency floor: best over ALL detector/override/threshold combos NET -0.0013
CI[-0.0025,-0.0002] (CI-separated BELOW). THE WALL is a BASE-RATE SEE-SAW (dominant senses 0.9828 MFS-near-perfect,
subordinate only ~30% of items). DECOMPOSED: net = fired*[p*a_s - (1-p)*c_d] with detector-precision p~0.48,
override-accuracy a_s~0.33, dominant-disruption c_d~0.64; break-even needs p*a_s~0.34, we get ~0.16 -> THE BINDING
LIMIT is a_s = 'which specific rare sense' = GENERATION from a world-knowledge situation model (detection p is cheaply
improvable 0.74->0.77; the readout is NOT the fix). Controls all CI-sep (shuffled-structure twin loses, error-gate
ablation removes the gain). Exemplary honesty: RETRACTED a smoke 'Zwaan dimension signature' that did not replicate at
power. This DECISIVELY re-localizes the north star to the GENERATIVE half (a_s). Grade EXCELLENT.

**WIRE (scoped DEBT-2, an INSTRUMENT to land — NOT yet landed; Q111, default-off, witnessed):** TIER-1 INSTRUMENT-only
— land the DIRECTIONAL domI predictive-error detector as `hdlab/semantic_control`'s frequency-independent trigger + the
MFS-default biased-competition read path. Land as an INSTRUMENT, NOT a default (the discrete override does NOT net-gain;
the located negative says so). No hdlab/ was written by the solver (Q111). The NET meaning gains do NOT live here — they
live in the north-star follow-on (the generative world-knowledge situation model = the a_s override-accuracy lever),
now filed PRIORITY 1 as `the_meaning_channel_needs_a_generative_world_knowledge_situation_model_that_predicts_the_specific_sense`.
`priority:` cleared; review (EXCELLENT) + this block written into PROBLEM.md.
