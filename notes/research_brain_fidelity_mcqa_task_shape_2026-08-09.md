# Brain-fidelity audit: is "cluster-prototype-and-score" the right SHAPE for script-based MC QA? (2026-08-09)

Filed by: Research (Sonnet), Director-requested deep-VET drill on the MCScript2.0 HARD_FAIL
(`data/exp_mcscript2_real_benchmark_validation_v1/metrics.json`, `hdlab/script_grain_acquisition_loop.py`,
`experiments/exp_mcscript2_real_benchmark_validation_v1.py`). Question: was the whole task-approach
brain-foundational, or is "learn a scenario-cluster prototype, then score MC candidates against it" the
wrong architecture for reading-comprehension QA, independent of whether the clustering mechanism itself
works? 3 parallel Sonnet lit-scans (Kintsch CI/situation models; script instantiation + QUEST/QUD;
neural correlates of schema-guided comprehension) + direct re-derivation from the already-landed
`metrics.json`.

## HEADLINE

**DEVIATION, confirmed by both the literature and the disk-measured numbers.** No primary source in any
of the three lanes (discourse comprehension, script/QA psychology, neuroscience) supports scoring answer
candidates against a cross-episode averaged prototype as the mechanism of real-time comprehension-driven
QA. The literature's actual shape is staged and two-part: (1) build a representation SPECIFIC to the
current passage (Kintsch construction-integration; Zwaan event-indexing; the passage's own causal-network
graph), checked FIRST; (2) only when that specific representation is silent on the question, fall back to
generic schema/script-level expectations, at LOWER confidence (Bower/Black/Turner's staged "Partial Copy"
recognition model; Preston-Eichenbaum's graded vmPFC-schema/hippocampus-detail interplay). Our shipped
cell does neither part of stage 1 -- it builds no per-passage situation model at all -- and uses a
cluster-level average as the PRIMARY and ONLY scoring signal, which is architecturally the wrong stage to
be running the scoring computation at. The already-landed `metrics.json` shows exactly the harm this
predicts: on every pass where the mechanism is active, scoring against the CURRENT passage's own words
(what `TEXT_OVERLAP` does) beats scoring against the cluster prototype by 1.5-3.3 points on the identical
covered questions, and system accuracy degrades monotonically (0.5859 -> 0.5538) as coverage climbs from
0% to 98% across the 5 passes -- i.e., "degraded with exposure" is not mysterious, it is coverage of a
signal that is measurably worse than the passage's own text, on the very questions where it fires.

## Cheap decisive test

This does NOT require a new corpus pull or a new extraction build. `data/exp_mcscript2_real_benchmark_
validation_v1/metrics.json`'s `real_arm` already has `dev_key_cache`-equivalent bag-of-words vectors
computed for every DEV passage AND every candidate answer (`precompute_dev_caches`). The isolating test:
re-score ONLY the covered subset (same keying, same coverage gate, same `use_script` decisions -- change
nothing about WHICH questions get diverted from text-overlap) by swapping `item_context_prototype`
(the matched library item's bundle-of-many-tellings bag-of-words) for `dev_key_cache[inst_id]` (the
CURRENT passage's OWN bag-of-words, already computed) in `script_decide_cached`. This isolates the single
variable the theory says matters -- "score against the specific passage" vs "score against the cluster
average" -- with the keying/coverage/guard machinery held fixed, at near-zero re-compute cost (rescoring
an already-cached vector set, no re-run of `grow_and_track`).

- **HARD-PASS** (confirms the SHAPE diagnosis): passage-own-content scoring on the covered subset closes
  >=80% of the measured gap to `covered_text_baseline_acc` at every pass (2-5), i.e. the harm is
  overwhelmingly a scoring-locus problem, not a keying/coverage problem.
- **HARD-FAIL** (would falsify the shape diagnosis, redirect to keying/coverage as primary cause): passage-
  own-content scoring on the covered subset still trails `covered_text_baseline_acc` by more than 50% of
  the currently-measured gap -- would mean the coverage-gating logic itself (which questions get diverted
  at all) is the dominant problem, not what they get scored against.

## The brain's actual shape for script-guided reading-comprehension QA (primary sources)

**1. Discourse comprehension is per-passage construction, not template retrieval.** Kintsch's
Construction-Integration model (Kintsch 1988, *Psychological Review* 95(2):163-182; Kintsch 1998,
*Comprehension: A Paradigm for Cognition*, Cambridge UP) explicitly rejects fixed-schema slot-filling:
construction loosely activates LTM knowledge associated with each text proposition (including irrelevant/
inconsistent material), and integration is a constraint-satisfaction/spreading-activation process that
settles into a representation constrained by, and varying with, THIS text's specific context -- not a
stored generic prototype retrieved intact. Van Dijk & Kintsch (1983, *Strategies of Discourse
Comprehension*) formalize the three-level architecture (surface code -> textbase -> situation model) and
keep the schema/superstructure analytically SEPARATE from the situation model: the superstructure is a
generic organizational control structure; the situation model is the token-level representation of "the
events, actions, persons... the text is about," populated with THIS discourse's particular referents,
updated incrementally cycle-by-cycle in working memory. Zwaan & Radvansky's event-indexing model (Zwaan &
Radvansky 1998, *Psych Bulletin* 123(2):162-185; Zwaan, Langston & Graesser 1995, *Psych Science*
6(5):292-297) tracks five dimensions (space, time, causation, protagonist, intentionality) per the
CURRENT narrative's unfolding events, updating only the dimensions that actually change as the specific
story progresses. Multiple syntheses of this literature draw the type/token line explicitly: schemas/
scripts are TYPES (generic, semantic-memory structures); situation models are TOKENS (episodic
representations tied to a particular narrated situation), with schemas as building blocks the situation
model is constructed FROM, not the finished representation.

**2. Scripts are INSTANTIATED with the current episode's specific fillers, and recognition/recall is
STAGED (episode-first, schema-second).** Schank & Abelson (1977, *Scripts, Plans, Goals, and
Understanding*) define instantiation as filling a script's generic slots with the specific entities named
in the current text ("John" binds Customer, "lasagna" binds Food) -- the generic script supplies only the
shared skeleton the instance elaborates. Bower, Black & Turner (1979, *Cognitive Psychology* 11(2):
177-220) is the single most load-bearing source for this drill's exact question. They explicitly test and
REJECT a "Full Copy" model (one fully-instantiated representation per script, i.e. a collapsed prototype)
because it "has no natural or parsimonious mechanism for creating confusions between memories of two
script instances," and instead confirm a "Partial Copy" model: each episode gets its OWN episodic memory
block holding only what was actually stated, tagged back to the generic script via a pointer; the generic
script node separately accumulates cross-instance activation. Recognition is explicitly STAGED: the
system checks the SPECIFIC episodic block FIRST; only on failure does it fall back to generic-script
activation, and even then judgments are lower-confidence (Bower et al. 1979, pp.198-201, Fig. 4).
Graesser, Gordon & Sawyer (1979, *JVLVB* 18(3):319-332) independently converge on the same "script pointer
+ tag" architecture via a different paradigm. Graesser, Singer & Trabasso's constructionist theory (1994,
*Psych Review* 101(3)) frames comprehension as a text-specific "search after meaning" that explains THIS
text's events; the QUEST model of question answering (Graesser & Franklin 1990; Graesser, Lang & Roberts
1991) operationalizes question-directed search as arc-search convergence over a TEXT-SPECIFIC conceptual
graph (goal/plan hierarchy, causal network) built from the passage being read, narrowing hundreds of
candidate nodes to fewer than 10, explaining 40-75% of variance in human answer-generation and
goodness-of-answer judgments. The Question-Under-Discussion framework (Roberts 1996/2012) formalizes
Relevance relative to the discourse-instance-indexed QUD, not a generic topic-type average. Separately
(sibling drill, `notes/research_psych_bridging_inference_situation_models_2026-08-09.md`), Trabasso & van
den Broek (1985, *JML* 24(5)) and Trabasso & Sperry (1985) model each story as its OWN typed causal-network
graph (Setting/Event/Internal-Response/Goal/Attempt/Outcome nodes, 4 causal edge types), with recall/
importance predicted by connectivity WITHIN that specific graph -- the same "score against the passage's
own structure" shape, from an independent literature lane.

**3. Neural correlates: schema activation supplies SCAFFOLDING that gets bound to episode-specific
content via hippocampal construction, not substituted for it.** Baldassano, Chen, Zadbood, Pillow, Hasson
& Norman (2017, *Neuron* 95(3):709-721) show hippocampal activity spikes at high-order event boundaries
and predicts SUBSEQUENT reinstatement of that JUST-COMPLETED SPECIFIC event during free recall -- indexing
encoding of the specific episode, not retrieval of a template. Baldassano, Hasson & Norman (2018,
*J Neurosci* 38(45):9689-9699) show same-schema stories (multiple "restaurant" narratives with different
characters/wording) evoke correlated mPFC/PMC patterns at schema-relevant timepoints -- described as
schema information being rapidly activated to SET UP/scaffold the representations the unfolding SPECIFIC
scene loads onto, not as replacing that scene's content. Ranganath & Ritchey's PMAT framework (2012,
*Nat Rev Neurosci* 13:713-726) casts the posterior-medial system as building contextual/relational
situation models while the anterior-temporal system carries item/entity content, with the hippocampus
BINDING both via pattern completion. Preston & Eichenbaum (2013, *Curr Biol* 23(17):R764-773) and the
CLS-update/SLIMM literature (Kumaran, Hassabis & McClelland 2016, *TICS* 20:512-534; van Kesteren et al.
2012, *TINS* 35:211-219) describe a graded interplay: schema-congruent input triggers vmPFC-accelerated
integration of the SPECIFICS with the schema (not discarding them), while schema-incongruent content
triggers a hippocampal prediction-error signal that specifically encodes the deviating detail. Zacks &
Swallow's Event Segmentation Theory (2007, *Curr Dir Psych Sci* 16:80-84; Zacks et al. 2007, *Psych Bull*
133:273-293) frames event-model updating as a continuous per-episode predict-and-correct cycle (schema-
driven predictions + boundary-triggered incorporation of new specifics), not prototype retrieval. 2020s
follow-up (Cohn-Sheehy et al. 2021, *Curr Biol*, "the hippocampus constructs narrative memories") confirms
the same direction: construction, not substitution.

**4. The one place something like prototype-blending is real: downstream, offline, partial, and NOT the
online comprehension/QA mechanism.** Bower/Black/Turner and Graesser/Gordon/Sawyer both find that LONG-
TERM MEMORY for a script-typical episode is vulnerable to blending its TYPICAL content toward the generic
prototype during LATER recall (a consolidation-era phenomenon) -- but even there, atypical/distinctive
content survives instance-tagged, and the phenomenon is about downstream memory distortion, not a
description of the real-time comprehension-time representation or the QA-scoring computation itself. No
source in any of the three lanes describes candidate-answer scoring being computed against a cross-episode
average as the PRIMARY, first-pass mechanism.

## Verdict: FOUNDATIONAL / COMPATIBLE / DEVIATION

**DEVIATION**, specifically at the answer-SCORING stage. The CA3/DG attractor-matching mechanism itself
(`hdlab.cleanup_family.iterative_attractor`, used by `ScriptLibrary.match_or_spawn`) is legitimately
brain-canonical (Treves-Rolls; matches the Baldassano schema-reinstatement finding) for ONE specific job:
recognizing WHICH generic schema/script-type the current passage belongs to. That job is COMPATIBLE with
the brain's architecture. But the shipped cell uses that SAME mechanism's output (the matched cluster's
bundled bag-of-words prototype) as the scoring target for candidate answers -- i.e. it skips stage 1
(construct a passage-specific representation) entirely and runs the QA-scoring computation directly off
the generic-type average. This is precisely the "Full Copy" model Bower, Black & Turner explicitly built
their experiment to REJECT in 1979, and precisely what Kintsch's CI model explicitly moved away from.
Nothing about the CA3/DG mechanism itself is at fault; it is being asked to do the job of stage 2
(schema-level fallback) while also being made to do the job of stage 1 (passage-specific scoring), which
no primary source licenses.

There is also a SECOND, related but separable, deviation surfaced by the disk numbers (see below):
`n_items_spawned_total=35` against `n_train_scenarios=195` -- the clustering itself collapses roughly
5.6x more scenarios into shared items than the true scenario count, with mean cluster purity
(`item_purity` `majority_frac`) of only ~0.20. This is a symptom of unbounded-superposition prototype
growth (a cluster's bundled register grows ever-more-generic as more traces accumulate, with no bounded-
capacity or pattern-separation constraint forcing new attractors to spawn once interference gets too
high) -- itself a departure from the brain's bounded-capacity, DG-pattern-separated attractor dynamics.
Fixing the scoring-stage deviation alone does not fix this; the schema-recognition stage needs its own
capacity/pattern-separation fix (see Rescue step 2) for "which script applies" to mean anything at scale.

## Direct disk evidence (already measured, no new run needed)

From `data/exp_mcscript2_real_benchmark_validation_v1/metrics.json` (`verdict=HARD_FAIL`):

| pass | coverage | commonsense system_acc | covered_system_acc | covered_text_baseline_acc | gap (baseline - system, on covered subset) |
|---|---|---|---|---|---|
| 1 | 0.0% | 0.5859 | n/a (0 covered) | n/a | n/a |
| 2 | 68.7% | 0.5756 | 0.5638 | 0.5786 | +1.48pp |
| 3 | 88.0% | 0.5559 | 0.5576 | 0.5910 | +3.34pp |
| 4 | 94.9% | 0.5538 | 0.5524 | 0.5855 | +3.31pp |
| 5 | 98.0% | 0.5538 | 0.5539 | 0.5864 | +3.25pp |

Every single pass where the mechanism is active, text-overlap-on-the-same-passage would have scored
higher on those exact same questions -- this is the "prototype-scoring is architecturally the wrong
computation" diagnosis, already sitting in the landed metrics, not a hypothesis. Pass 1's system_acc
(0.5859) is IDENTICAL to the text-overlap baseline because coverage is 0% at pass 1 (no items have reached
`min_confirm` + the intervening-pass rule yet) -- the monotonic "degradation with exposure" the Director
flagged is exactly and only the increasing coverage of a per-question-worse signal, not a mechanism that
was good and then decayed. `n_items_spawned_total=35` vs `n_train_scenarios=195`, mean `majority_frac`
~0.20 (e.g. `SITEM_0002`: 281 accumulated traces, only 2.8% share the plurality true scenario) confirms
the second, compounding keying-degeneracy issue above.

## Rescue architecture, mapped to owned organs

The literature's staged shape maps directly onto organs already built (mostly VET-confirmed, currently
just not wired together this way for this task):

1. **Build a genuine per-passage situation model (Kintsch textbase / Zwaan event-indexing / Trabasso
   causal-network shape), not a single whole-narrative bag-of-words keying vector.** Stage 1 of the
   original pre-reg already measured `hdlab.candidate_generator.CandidateGenerator` firing at 100%
   (150/150) per-SENTENCE across MCScript2.0 narratives -- but `hdlab.mcscript_extraction.
   extract_instance_tuple` currently THROWS AWAY every sentence except the first and last, keeping only
   (first-sentence root verb, last-sentence root verb, most-frequent subj, most-frequent obj). Extend it
   to extract every sentence's (root-verb, subj, obj) and bind each as an event into
   `hdlab.situation_model_accumulate.AccumulateRegister` (role=event-type-slot, event_idx=sequential
   position, `max_event_slots=8` already supports up to 8 events/passage -- MCScript narratives run ~5-7
   sentences, within range). This is the already-validated ACCUMULATE organ (atom 29609,
   `capability_registry` id `situation_model_accumulate_register_organ`), reused verbatim, not rebuilt.
2. **Keep `ScriptLibrary.match_or_spawn` (CA3/DG keying) but restrict its job to schema-TYPE recognition
   only** (Baldassano's mPFC/PMC scaffold-activation role) -- fix the bounded-capacity/pattern-separation
   pathology (cap cluster growth or renormalize prototypes; recalibrate the novelty threshold against
   FULL-corpus running-cluster dynamics, not just the small stratified precheck sample that currently
   passes `precheck_a` while the full run still collapses 195 scenarios into 35 clusters).
3. **Use `hdlab.sequence_memory.SequenceMatrix.chain_predict` (already chain-grade-certified, commit
   a27939c5, HARD_PASS at depths [1,3,5,7,10]; already precedented in a QA context in
   `experiments/exp_substrate_native_qa_hotpotqa_v1.py`/`v2`) seeded from the RECOGNIZED script type's
   learned event-transition structure -- but queried starting from the CURRENT PASSAGE's own extracted
   event chain (step 1's register), not a cluster average -- to generate script-typical continuation/
   gap-fill predictions. This is the legitimate "generic schema supplies predictive scaffolding" role
   (Preston-Eichenbaum; SLIMM; Zacks EST), invoked specifically to answer "commonsense" questions where
   the correct answer is NOT stated verbatim in the passage.
4. **Score each candidate answer in STAGED order, per Bower/Black/Turner's confirmed "Partial Copy"
   recognition model and QUEST's arc-search**: PRIMARY signal = cosine/overlap against the passage's OWN
   situation-model register (step 1) -- this alone should recover close to `TEXT_OVERLAP` parity since
   it is now grounded in the same content. FALLBACK signal, used only when the passage's own register is
   silent on the candidate (a genuine inferential gap) = the script's chain-predicted expectation (step 3),
   at explicitly lower confidence/weight, exactly mirroring the brain's episode-first/schema-second,
   lower-confidence-on-fallback staging.

## Honest read: will the rescue clear the baseline, or is the wall deeper?

Two separable claims, calibrated per lit-scan discipline (deflate 0.15-0.25, cap novel-synthesis P at 0.50):

- **P(the rescue stops the active harm -- covered-subset accuracy returns to at least text-overlap
  parity, a MIDDLE_BAND-or-better outcome) ~ 0.55-0.60.** This is close to a structural near-certainty on
  theoretical grounds (scoring against the passage's own content cannot do meaningfully worse than
  text-overlap since it is now approximately the same signal, restricted to the same covered subset) --
  deflated only for engineering-execution risk (extraction bugs, event_idx-slot capacity edge cases at
  the ~7-sentence high end).
- **P(the rescue clears the FULL pre-registered HARD-PASS gate on the FULL commonsense DEV subset --
  strictly beats `TEXT_OVERLAP`, non-decreasing curve, real-edge > scramble-edge) ~ 0.30-0.35 (deflated,
  novel-synthesis-capped).** Adversarial read: `TEXT_OVERLAP` is already a strong, hard-to-beat baseline
  on THIS corpus specifically because MCScript2.0's crowd-sourced everyday narratives correlate answer
  text with narrative vocabulary even on nominally "commonsense" questions (baseline commonsense
  acc=0.586, text-type acc=0.758 -- a lexically-friendly corpus by construction). A coarse per-sentence
  (root-verb + subj/obj) situation-model register is a close cousin of bag-of-words; it is unlikely to add
  MUCH signal beyond what `TEXT_OVERLAP` already exploits on its own. The genuine INCREMENTAL value has to
  come from step 3's script-based inference filling real gaps -- which requires (a) a materially richer
  per-passage event chain than currently extracted (done by step 1, but untested at this grain), (b)
  enough per-scenario exposure (7-18 tellings/scenario here) to learn an informative event-transition
  matrix, and (c) a concept-level codebook fine-grained enough to discriminate the actual 2-way answer
  text, none of which currently exist at the needed grain. This is the SAME "front-end/grounding-richness"
  wall this research arc has hit repeatedly on real prose (DesireDB extraction wall, goal_achievement
  cross-corpus parity-not-beat) -- not a new finding, but this drill confirms it is the binding constraint
  here too, distinct from and in addition to the shape deviation.

**Bottom line for the Director:** the task-approach was NOT brain-foundational as shipped -- the specific
failure is a genuine, literature-supported, disk-confirmed architecture bug (scoring against a cross-
episode prototype instead of the passage's own situation model), not evidence that script-grounded MC QA
is intrinsically out of reach for this substrate. The rescue is concrete, buildable mostly from ALREADY-
VALIDATED organs, and should at minimum eliminate the demonstrated active harm. Whether it can clear
`TEXT_OVERLAP` outright on the FULL benchmark is a separate, harder, genuinely open question that depends
on how much real inferential (not just lexical) signal script-based chain-prediction can add on top of a
corpus where the baseline is already unusually strong -- worth running the cheap decisive test above FIRST
(near-zero cost, isolates the variable) before committing to the full step 1-4 rebuild.

## Cross-thread synthesis

Consistent with `notes/research_vsa_script_representation_chaining_2026-08-09.md` (same-day sibling drill):
`SequenceMatrix.chain_predict` and `AccumulateRegister`/`RelationRegister` were already identified there as
the reusable script-chaining substrate, independent of this MC QA investigation -- this drill supplies the
missing piece: WHERE in the pipeline they need to sit (staged, passage-first) and WHY the current cluster-
prototype placement is wrong, with primary-source backing and disk confirmation. Consistent with
`notes/research_psych_bridging_inference_situation_models_2026-08-09.md`'s causal-network findings
(Trabasso & van den Broek 1985): a story's causal graph is scored as ITS OWN typed graph, not a generic-
type average, the identical shape this drill independently converges on from the discourse-comprehension
and neuroscience lanes. Also consistent with the MEMORY.md-recorded USER reframe ("the state_of_mind
BUNDLE *is* the situation-model representation... gap = grounded causal/intentional CONTENT + a chaining
step") -- this drill operationalizes exactly that framing for the MC QA task specifically: the bundle
organ (`AccumulateRegister`) is right; it was simply never populated per-passage for this cell, and the
"chaining step" (`chain_predict`) was never wired in at all (only the FHRR 4-role glass-box audit register
was built, and even that was demoted to audit-only per Amendment 1, never load-bearing).

## Substrate-product implications

A user-facing auditable-AI-memory product benefits directly from this fix even before it clears
`TEXT_OVERLAP`: a passage-grounded, staged (specific-then-generic, confidence-tagged) answer-scoring trace
is a STRONGER glass-box artifact than either the current cluster-prototype score OR a plain text-overlap
count -- it can show its work ("matched script type X; passage's own situation model says Y; falling back
to script-typical expectation Z because the passage doesn't state it") in exactly the staged, confidence-
graded form the brain's own architecture uses, which is a differentiator regardless of whether it beats
`TEXT_OVERLAP` on this specific benchmark's accuracy metric.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1** (cheap decisive test, above): passage-own-content rescoring on the already-covered
subset closes >=80% of the measured gap to `covered_text_baseline_acc` at every pass 2-5.
HARD-FAIL: closes <50% of the gap at any pass -- redirects the diagnosis toward keying/coverage, not
scoring-locus.

**Prediction 2** (full rebuild, steps 1-4 above): on the FULL commonsense DEV subset, the rebuilt pipeline
(a) reaches >= `covered_text_baseline_acc` parity on the covered subset at every pass (recovers the
demonstrated active harm), AND (b) `n_items_spawned_total` after the capacity/pattern-separation fix falls
within 20% of `n_dev_scenarios=162` (fixes the keying-degeneracy symptom) -- both required for a
MIDDLE_BAND-or-better read. HARD-FAIL: either (a) fails to reach parity even with passage-grounded primary
scoring, or (b) clustering still collapses more than 3x past the true scenario count after the fix --
either would mean a deeper problem than the two diagnosed here.

**Prediction 3** (the harder claim, full HARD-PASS gate): SYSTEM commonsense accuracy on FULL DEV strictly
beats `TEXT_OVERLAP` (0.5859), non-decreasing curve across 5 passes, real-edge > scramble-edge. Deflated
P~0.30-0.35 per the adversarial read above. HARD-FAIL: system accuracy remains <= 0.5859 despite Prediction
2 clearing -- would mean the script-inference-gap-filling step (chain_predict) adds negligible signal over
passage-grounded scoring alone on this specific corpus, i.e. the corpus's lexical-groundedness genuinely
caps what script-level inference alone can add, a different and harder finding than the shape bug.

## Citations (verified count: 19 primary + 2 secondary-synthesis sources, cross-checked across 3
independent lit-scans + 1 sibling same-day drill)

Kintsch 1988 *Psych Review* 95(2); Kintsch 1998 *Comprehension: A Paradigm for Cognition*; van Dijk &
Kintsch 1983 *Strategies of Discourse Comprehension*; Zwaan & Radvansky 1998 *Psych Bulletin* 123(2);
Zwaan, Langston & Graesser 1995 *Psych Science* 6(5); Schank & Abelson 1977 *Scripts, Plans, Goals, and
Understanding*; Bower, Black & Turner 1979 *Cognitive Psychology* 11(2); Graesser, Gordon & Sawyer 1979
*JVLVB* 18(3); Graesser, Singer & Trabasso 1994 *Psych Review* 101(3); Graesser & Franklin 1990; Graesser,
Lang & Roberts 1991 (QUEST); Roberts 1996/2012 (QUD); Baldassano et al. 2017 *Neuron* 95(3); Baldassano,
Hasson & Norman 2018 *J Neurosci* 38(45); Ranganath & Ritchey 2012 *Nat Rev Neurosci* 13; Preston &
Eichenbaum 2013 *Curr Biol* 23(17); Kumaran, Hassabis & McClelland 2016 *TICS* 20; van Kesteren et al.
2012 *TINS* 35 (SLIMM); Zacks & Swallow 2007 *Curr Dir Psych Sci* 16; Zacks et al. 2007 *Psych Bull* 133;
Cohn-Sheehy et al. 2021 *Curr Biol* (2020s follow-up). Plus Trabasso & van den Broek 1985 / Trabasso &
Sperry 1985 *JML* 24(5) (via sibling same-day drill, cross-thread synthesis). All primary-source claims
above were independently corroborated across at least 2 of the 3 parallel lit-scan lanes (discourse-
comprehension lane and script/QA lane both surfaced Bower/Black/Turner independently; discourse and
neural lanes both surfaced the type/token and construction-vs-retrieval framing independently) --
convergent, not single-source.
