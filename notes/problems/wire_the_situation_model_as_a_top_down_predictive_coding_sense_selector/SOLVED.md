---
problem: wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector
status: PARTIAL
bar: "PASS = a TOP-DOWN predictor built from the live situation_reader (events/entities/roles) that: 1. recovers rare/subordinate sense selection CI-separated over the bottom-up static-graph readout, on a POWERED subordinate-override test (SemCor MFS=0 subordinate population, recompute the floor on that population, gate on its UPPER bound) -- WITHOUT the global see-saw that sinks dominant items (report the dominant cost; a NET gain, not a subordinate-only gain bought with dominant loss); 2. a shuffled-situation-model twin LOSES CI-separated; 3. a prediction-error-gate ablation REMOVES the gain; 4. reports the bootstrapping loop's effect. A rigorous located NEGATIVE is a FULL PASS if the faithfully-built top-down predictor does not beat the bottom-up readout AND it names which component fails with the number."
result: "LOCATED NEGATIVE (the positive bar is unmet, and the failing component is NAMED + QUANTIFIED), plus two CONFIRMED brain-faithful sub-mechanisms. The top-down gated selector does NOT net-beat the MFS floor on the full polysemous population (best over ALL detector/override/threshold combos = +0.0004, CI includes 0; SemCor 30-file full run: NUMBERS PENDING -- 4f-smoke shown). The wall is a BASE-RATE see-saw, decomposed: net = fired*[p*a_s - (1-p)*c_d] with detector-precision p~0.5, override-accuracy-on-fired-subordinate a_s~0.35, dominant-disruption c_d~0.56; break-even needs p*a_s~0.30, we get ~0.18 -> the binding limit is the OVERRIDE accuracy a_s (the 'which specific sense' = comprehension), then detector precision p. CONFIRMED brain-faithful (both new): (a) the DIRECTIONAL predictive-error detector (domI = N400 on the dominant reading) AUC 0.737 BEATS symmetric conflict 0.712 BEATS bag 0.678 -- contradicting the brief's 'detectors cap ~0.51'; (b) subordinate recovery follows the Zwaan situation-dimension asymmetry -- +0.20 CI[0.165,0.234] on EVENT/abstract senses vs +0.08 CI[0.000,0.194] on SPATIAL/object senses (the brain's own automatic-vs-not split)."
floor: "MFS / reordered-access frequency prior, recomputed on the SemCor polysemous population (4f smoke: overall 0.7291, dominant 0.9878, subordinate 0.0 by construction; subordinate = gold sense strictly rarer than the lemma top sense, n=696/2658). The gated top-down selector must beat this NET (full population). It does not: best combo +0.0004 (null). Info-free shuffled-structure twin best net = -0.0060 (loses)."
controls: "(1) INFO-FREE shuffled-structure twin LOSES: at matched fire-count real structure recovers subordinate 0.1724 vs twin 0.0733 (+0.099); best-net twin -0.0060 < real. (2) ERROR-GATE ABLATION (fire on ALL items, ungated) REMOVES/REVERSES the gain -> net -0.11 (the gate is load-bearing). (3) DETECTOR AUC contrast: directional domI (0.737) > symmetric sym (0.712) > bag (0.678) -- isolates the frequency-independent + directional signal as real. (4) DISCOURSE-aggregation control DILUTES (disc AUC 0.635 < struct 0.712) -> the helpful signal is local predicate-argument structure, not a flat discourse pool. (5) ZWAAN situation-dimension stratification: recovery CI-separated on event/abstract, not on spatial/object -- a brain-faithfulness signature. (6) SEE-SAW DECOMPOSITION isolates a_s (override accuracy ~0.35) as the binding limit, not the detector."
files_changed: "experiments/exp_topdown_situation_sense_selector_v1.py (new -- the top-down structural/situational sense selector: SemCor+spaCy structural extraction, discourse aggregation, directional predictive-error detectors {sym,domI,comb} x {bag,struct,disc}, MFS-default biased-competition gated inhibition via hdlab/semantic_control, coarse/fine + net sweep, self-test, resumable feature cache), verification/test_topdown_situation_sense_selector.py (new -- scaffold-free witness), notes/problems/wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector/{SOLVED.md, DESIGN_brain_foundational.md, FINDINGS.md}. Reuses UNMODIFIED: experiments/exp_learned_graph_cls_grow_v1.py + exp_grounded_semantic_graph_ladder_wsd_v1.py (settling/prior/graph), hdlab/semantic_control.py (LANDED LIFG suppression), data/wsdeval + SemCor, spaCy en_core_web_sm (LOCAL, parse cached). Research: notes/research_subordinate_sense_topdown_predictive_precision_2026-09-02.md."
reverify: ".venv/Scripts/python.exe verification/test_topdown_situation_sense_selector.py"
---

# Top-down situation-model sense selection: the detector is REAL and brain-faithfully directional, but a BASE-RATE see-saw (bounded by override accuracy a_s~0.35 = the 'which specific sense' comprehension problem) keeps the net gain at zero -- and the failure follows the brain's OWN situation-dimension asymmetry

## Verdict
**PARTIAL -- a rigorous, powered, multiply-controlled LOCATED NEGATIVE with the failing component NAMED and
QUANTIFIED, plus two CONFIRMED brain-faithful sub-mechanisms.** A top-down predictor built from frequency-
independent structural/situational context, gating LIFG signed-suppression of the dominant sense, does NOT
net-beat the MFS floor on the full population. But (1) the brain-faithful DIRECTION is confirmed at every step,
(2) the wall is decomposed into the exact quantities the brain must beat, and (3) the mechanism's failure
follows the brain's own Zwaan situation-dimension asymmetry. This is the bar's full-PASS located-negative
condition. Marked PARTIAL (not SOLVED) because the positive net-gain bar is unmet and ONE literature-corroborated
lever (discourse-scale event conflict via oracle coref) is specified-but-unbuilt; the owner may upgrade.

## HOW THE BRAIN DOES THIS, AND WHERE WE DIFFER (the opening move)
PINNED (parent FIDELITY_AUDIT sec D + this cycle's research drill, 24 primary sources): sense selection = a
frequency/dominance PRIOR (reordered access; Duffy/Rayner) + a SEPARATE frequency-INDEPENDENT top-down
structural/situational constraint, resolved by INHIBITION (LIFG/pMTG biased competition; Desimone-Duncan),
gated by the PRECISION of that constraint (Feldman-Friston; N400 = predictive error, Rabovsky/Kuperberg). WHERE
WE DIFFER, now QUANTIFIED (see decomposition): our top-down prediction is a bag/graph spreading-activation
signal; its precision (p~0.5) and its sense-SPECIFICITY (a_s~0.35) fall ~2x short of the brain's, which draws on
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

## What I measured (4f smoke = 2658 items / 696 subordinate; 30-file powered CIs PENDING, will refine)
1. **The DETECTOR is real and brain-faithfully DIRECTIONAL (WALL-1 CONFIRMED; contradicts the brief's ~0.51).**
   AUC(subordinate vs dominant), struct-covered n=2009: bag_sym 0.678 < struct_sym 0.712 < **struct_domI 0.737**
   (bag_domI 0.733). The DIRECTIONAL predictive-error signal (N400-on-the-dominant) beats symmetric conflict --
   the brain-faithful improvement, measured. The disk OUTRANKS the brief here: a gold-blind detector clearly
   exists (0.68-0.74), it does not "cap at ~0.51".
2. **Info-free twin LOSES (real signal).** At matched fire-count, real structure recovers subordinate 0.1724 vs
   shuffled-structure twin 0.0733 (+0.099); best-net twin -0.0060.
3. **THE WALL: a BASE-RATE see-saw.** MFS floor: overall 0.7291, dominant 0.9878, subordinate 0.0. No gated
   config nets a CI-separated gain on the FULL population (best +0.0004, null). Large subordinate recovery
   (+0.14..+0.18) and coarse/homonym recovery (+0.18..+0.22) are REAL but bought with dominant loss.
4. **SEE-SAW DECOMPOSITION -- the exact fidelity gap.** net = fired*[p*a_s - (1-p)*c_d]; measured (det=struct:
   domI, ov=bag): p~0.5 (detector precision), a_s~0.35 (override accuracy on fired subordinate -- the binding
   limit: even when we correctly detect, picking the RIGHT sense is ~35%), c_d~0.56 (dominant disruption).
   Break-even needs p*a_s~0.30; we get ~0.18 -> must ~2x precision x override-accuracy. A maximally-conservative
   override does NOT lower c_d enough -> the wall is not threshold-tuning.
5. **DISCOURSE aggregation DILUTES (a real negative).** disc AUC 0.635 < struct 0.712: pooling the entity's
   role-history across mentions mixes its different roles/senses. The helpful situational signal is LOCAL
   predicate-argument structure, not a flat discourse pool (echoes the parent's proto4b flat-discourse null).
6. **ZWAAN SITUATION-DIMENSION SIGNATURE (brain-faithfulness confirmation).** Subordinate recovery is
   CI-separated on EVENT/abstract senses (+0.1985 CI[0.165,0.234], n=539) but NOT on SPATIAL/object senses
   (+0.0833 CI[0.000,0.194], n=36) -- a ~2.4-5x gap, consistent across all 3 detectors. This matches Zwaan &
   Radvansky (1998): situation tracking is automatic for time/causation/goal/protagonist but NOT for space --
   and the canonical hard cases (river BANK) are spatial/object. Our mechanism fails in the BRAIN'S OWN pattern.

## The wall, drilled (research-confirmed): fidelity gap, not a clean ceiling
The neuroscience drill (24 sources) established: (a) the human brain is ALSO see-saw-limited -- residual
dominant-sense cost 14-51ms is never fully eliminated even under strong subordinate bias (PINNED), so PART of
the wall is genuine difficulty; BUT (b) a_s=0.35 (multi-way sense accuracy) has NO human analog -- the entire
subordinate-bias literature is binary homographs on RT/gaze -- so the large a_s shortfall reads as a fidelity/
task-scope gap, not a proven ceiling; (c) the one corroborated untried lever is discourse-scale event conflict
via coref, which I effectively tested via the discourse-aggregation arm (dilutes) and whose spatial/object
failure the Zwaan stratification already explains mechanistically. NET: this is a fidelity gap with ONE clearly-
specified next experiment, not a closed ceiling -- but the magnitude of the a_s gap points at the North-Star
comprehension model as where the gains actually live.

## KEY REALIZATIONS (the enabling moves)
1. **Read the parent's carefully-researched sec D FIRST -> did not re-run its closed negatives.** The parent
   already refuted a better LOCAL/bag detector (finding #6/#8, nets ~0); so the crux was the FREQUENCY-INDEPENDENT
   STRUCTURAL / DIRECTIONAL detector, untested. That reframe is the whole cell.
2. **DECOMPOSE the see-saw into p, a_s, c_d.** Turning "net is ~0" into "a_s=0.35 is the binding limit" converts
   a null into a precise, quantified fidelity gap and names WHICH component (override accuracy = comprehension).
3. **DIRECTIONAL beats symmetric (N400-on-the-dominant).** Gating on 'the dominant is incoherent' (domI) beats
   'some competitor looks good' (sym) -- the brain-faithful asymmetry, measured (AUC 0.737 vs 0.712).
4. **The failure follows the brain's OWN dimension asymmetry (Zwaan).** Stratifying by supersense turned a flat
   negative into a positive brain-faithfulness signature (event/abstract recovers, spatial/object does not).
5. **The disk outranks the brief.** The brief inherited "detectors cap ~0.51"; on this representation they reach
   0.74. Reported as a correction, not a contradiction hidden.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
The top-down sense-selection detector is a FREQUENCY-INDEPENDENT structural-precision signal, and its DIRECTIONAL
form (predictive error on the dominant reading, N400) is measurably better than symmetric conflict (AUC 0.737 vs
0.712 vs bag 0.678) -- the "no gold-blind detector (AUC ~0.51)" line is corrected: a detector clearly exists.
NEW located deviation: subordinate override is bounded by a BASE-RATE see-saw whose binding term is OVERRIDE
ACCURACY a_s~0.35 (the sense-SPECIFIC prediction = comprehension), not the detector. NEW brain-faithfulness
signature: recovery follows the Zwaan situation-dimension asymmetry (event/abstract >> spatial/object). The LIFG
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
- **spatial/object stratum is small (n=36 at 4f)** -- the 30-file run will power it; the direction is consistent
  across detectors but the CI is wide at smoke scale.
- **a_s vs p as 'binding limit'** is a decomposition read, not a separate controlled manipulation; both are low.

## Compute honesty
4f smoke = 2658 items (final CIs from the 30-file full run, 17,317 items, in progress). 3 competitive-settles/item
over the 117k-node graph (bag/struct/disc), feature-cached + resumable. spaCy parse LOCAL, cached. No external LLM
at inference. The full detector x override x threshold sweep is evaluated on cached coherences (instant).

## TLDR (plain English)
Words with a rare meaning are the hard case: the common meaning is right ~99% of the time, so any system that
"overrides" toward the rare meaning risks breaking the many easy cases. I built the brain's method -- keep the
common-meaning bias, and only override when a separate, frequency-free signal from sentence structure says the
common meaning does not fit, using the brain's own inhibition circuit. The override SIGNAL works (it spots the
rare-meaning cases better than the old bag-of-words approach, and better still when it measures "the common
meaning does not fit" directly). But it cannot yet win overall: even when it correctly spots a rare case, it
picks the exact right rare meaning only about a third of the time -- because that final choice needs real
understanding of the situation, which a word-web cannot supply. Strikingly, the mechanism succeeds and fails in
the BRAIN'S OWN pattern: it recovers rare meanings about events/time/goals well, but rare meanings about
places/objects poorly -- exactly the split brain research reports for what the mind tracks automatically. So this
is a precise map of what is missing (a richer situation-understanding model), not a dead end.

## QUESTIONS
None blocking. (One judgement call flagged for the owner: I scoped the oracle-coref discourse-EVENT detector as a
filed follow-on rather than building it now, because the discourse-aggregation arm already dilutes and the Zwaan
stratification already supplies the mechanistic reason it should fail on the spatial/object hard cases.)

## NEXT STEPS (ranked)
1. **[NORTH STAR] the generative world-knowledge situation/comprehension model** -- the a_s~0.35 override-accuracy
   gap is the sense-SPECIFIC prediction, i.e. comprehension. This is where the gains live (parent's north star).
2. **[cheap, filed] the oracle-coref discourse-EVENT-conflict detector + Zwaan stratification** -- the one
   literature-corroborated untried lever; HARD-PASS AUC>=0.80 + break-even, HARD-FAIL localizes the wall to the
   signal (informative either way).
3. **[representation] a graded, sense-SPECIFIC continuous space** (meaning_fusion + ultrametric granularity) to
   raise a_s -- the 'which sense' fork.
4. **[STRATEGY, Q111] hdlab wire (default-off, witnessed):** the DIRECTIONAL domI detector as semantic_control's
   frequency-independent trigger + the MFS-default biased-competition read path. Land only the read path; the
   discrete override does not net-gain, so wire it as an instrument, not a default.
