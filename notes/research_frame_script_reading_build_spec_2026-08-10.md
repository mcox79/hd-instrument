# Research: Frame/Script-Activation Reading -- BUILD SPEC for ProPara Bridging (2026-08-10)

Filed by: research (Sonnet). Trigger: mid-drill USER steer via coordinator -- charter decided (B:
build glass-box reading), and the failure mechanism sharpened: ProPara bridging capped not for lack
of knowledge but because the substrate used the WRONG mechanism (SRL "stenographer" + KB "phone
book" lookup, both blind to an UNMENTIONED participant like oxygen). Correct mechanism = FRAME/
SCRIPT ACTIVATION (Schank-Abelson scripts / Fillmore frame semantics): a trigger word associatively
activates a whole process frame, which CARRIES its unmentioned participants' fates for free; bind
the paragraph's tracked entities into the frame's slots. This note is a BUILD SPEC, not a survey.

**KB-check done first** (`bash tools/substrate_query.sh`, 3 queries: "frame semantic activation
script slot filling unmentioned participant process reading" top cosine 0.316; "self correcting
controls reasoning versus comprehension" top cosine 0.362; "FrameNet combustion process frame core
roles fire burn" top cosine 0.358) -- no direct prior note proposes THIS specific fix (graded
frame-activation replacing literal-keyword bridging-fact sourcing on ProPara); this drill extends,
not duplicates, `notes/research_psych_bridging_inference_situation_models_2026-08-09.md` (script-
slot-as-cheap-default mechanism, read in full this cycle) and the `research_comprehension_barrier_
map_brain_foundational_2026-08-10.md` B5/B8 diagnosis. Prior-art hit worth flagging: `notes/
exp_dev_handoff_research_nl_understanding_universal_unlock_3x_2026-06-11.md` and `notes/research_
drill_tier2_problem_schemas_2x_2026-06-11.md` already scoped a generic "FrameNet top-200 codebook"
idea in June -- never built, never pointed at ProPara specifically; this spec supersedes that
generic framing with a mechanism-precise, disk-grounded target.

Disk-verified this cycle (read the code, not the label): `hdlab/frame_induction.py`, `hdlab/
script_grain_acquisition_loop.py`, `hdlab/situation_model_accumulate.py`, `hdlab/schema_exemplar_
bayes.py`, `hdlab/lexical_similarity.py`, `hdlab/coreference_resolver.py`; the exact matching code
in `experiments/exp_propara_bridging_distilled_kb_endtoend_v1.py::_build_distilled_bridge_facts`
and `tools/benchmark_trap_check/build_propara_process_physics_kb_v1.py`; the metrics.json of all 6
ProPara bridging/KB-sourcing cells on disk.

---

## HEADLINE

**The USER's reframe is correct and now DISK-CONFIRMED on this substrate's own ProPara data, not
just brain analogy.** The exact failure mechanism is measured: a hand-VET'd, TRAIN-topic-derived,
18-process physics KB (`build_propara_process_physics_kb_v1.py`) sources bridging facts via LITERAL
SET-INTERSECTION at both required steps -- `len(set(signature) & text_toks)` for paragraph-to-
process matching, `p_toks & role_toks` for participant-to-role mapping -- and this recovers only
**SURVIVAL = 0.1823** of the oracle lift (`distilled_lift=0.0194 / oracle_lift=0.1062`,
`pair_recall=0.2469`, **`pair_precision=0.0905`**, `exp_propara_bridging_distilled_kb_endtoend_v1`,
HARD_FAIL). In the SAME arc, the oracle cell proves the mechanism and knowledge content ARE load-
bearing once correctly sourced (`with_f1=0.4626` vs `without_f1=0.3564`, **lift = +0.1062**,
`exp_propara_bridging_knowledge_vs_mechanism_v1`, HARD_PASS), and a broader-but-promiscuous KB
(ConceptNet co-participation) did NOT help (`cn_add=+0.0022`, domain_coverage=0.48, HARD_FAIL) --
ruling out "just needs more facts." This triangulates exactly to the USER's diagnosis: the wall is
the MATCHING MECHANISM (exact-string phone-book lookup), not the knowledge and not the downstream
reasoning. Three of the four pieces a frame-activation reader needs are already OWNED (graded
concept-similarity, an FHRR role-bind pattern for script instances, and a fully-correct situation-
model destination); the fourth (associative trigger->frame + participant->role matching) is the
one genuinely missing, small piece. Section 3 is the concrete build spec.

---

## 1. Brain grounding (concise): frame/script activation as the reading mechanism

**SHAPE.** A lexical/trigger cue associatively activates a whole pre-stored schema/frame via
similarity-based spreading activation -- NOT exact lookup. Schank & Abelson (1977) scripts are
pre-computed default slots; **Bower, Black & Turner (1979, *Cognitive Psychology* 11)** give the
direct behavioral proof: readers FALSELY recognize unmentioned-but-script-typical actions as having
been stated -- script activation supplies default content without new processing. **Graesser,
Gordon & Sawyer (1979, *JVLVB* 18)** sharpen this: near-zero recognition-memory discrimination for
typical/default actions (retrieved via a cheap "pointer") vs. reliably better discrimination for
atypical ones (which require costlier explicit tagging) -- the strongest direct evidence that script
defaults are CHEAP relative to open search, because the frame already carries them. Kintsch's
Construction-Integration (1988) supplies the two-stage mechanics: construction = broad, weak,
context-blind activation of many candidate frames/propositions; integration = fast constraint-
satisfaction settling that prunes to the context-consistent subset. This session's own 08-09 drill
(`research_psych_bridging_inference_situation_models_2026-08-09.md`, section 4) already derived the
general form: "an active goal pre-activates a small, bounded set of expected resolution-types...
this is script-slot-filling generalized... from stereotyped event sequences to arbitrary goal-
outcome pairs" -- the SAME mechanism this build spec targets, here specialized to PROCESS frames
(combustion) instead of GOAL frames.

**POSITION.** Fires as soon as a trigger cue is read -- continuous, cheap, DEFAULT, not strategic
(constructionist theory's causal-antecedent/superordinate-goal inferences are the closest validated
analogue of "runs automatically because the frame narrows the search space to begin with," per this
cycle's discourse-psychology lit-scan). Crucially, per Zacks/Franklin's SEM (2020) and this cycle's
neuro lit-scan: **temporal placement is not a separate inference step** -- a causal-discontinuity
prediction-error spike is simultaneously the trigger for inferring a cause AND for opening/updating
the current event-model slot. Translated to this substrate: the frame instance is anchored to the
SAME clause/step whose trigger word activated it, so "when did oxygen get consumed" falls out of
WHEN the frame fired, not a separate localization computation -- this is exactly why the fire/log
example in the task brief has no extra "which step" ambiguity once the frame is correctly identified.

**METRIC.** Behaviorally: false-alarm rate for unmentioned-but-typical content (the field's own
proxy). On this substrate: F1/lift on the unmentioned-participant subset under the OFFICIAL ProPara
metric -- exactly the axis the existing bridging cells already measure, so no new metric is needed.

**Neural substrate** (this cycle's lit-scan, deflated per calibration): CA3 auto-associative pattern
completion (partial cue -> full stored pattern) biased toward schema-consistent content by mPFC-held
generalized schemas (Van Kesteren SLIMM 2012/2013; Ghosh & Gilboa 2014), selected among competing
schema-consistent candidates by LIFG/pMTG semantic control (Whitney et al. 2011; the causal-
discourse-inference meta-analysis, PMC8261065, shows this network co-activates with mPFC/schema
territory specifically during cross-sentence causal bridging). **Baldassano et al. (2018, *J
Neurosci*)** is the single most direct piece of evidence for "many surface forms -> one frame": PMC/
mPFC carry SCRIPT-IDENTITY patterns that generalize across different stories sharing the same
underlying script (restaurant, airport), an HMM aligning previously-unseen narrations to the shared
schema -- literally the associative-generalization claim this build targets, demonstrated neurally.
Confidence flags per the lit-scan: HIGH that this SHAPE (pattern-completion + schema-bias +
control-selection) is real and composable; MEDIUM-LOW that fine-grained sub-step temporal placement
specifically has been isolated in any single study (flagged honestly by the neuro-lit-scan agent as
its own synthesis, not a literature-asserted finding) -- the SEM-level argument above (placement =
whenever the trigger fires) is this note's own bridge across that gap, not a verified citation.

**Contrast with what ProPara's cells actually implemented.** Read directly off
`_build_distilled_bridge_facts` (`experiments/exp_propara_bridging_distilled_kb_endtoend_v1.py`,
lines ~137-163):
```
scored = [(name, len(set(d["signature"]) & text_toks)) for name, d in procs.items()]
...
if p_toks & role_toks:
    fdict.setdefault(effect, set()).update(trigs)
```
Both the frame-IDENTIFICATION step and the participant-ROLE-MAPPING step are literal Python `set`
intersections against small hand-typed keyword lists. Zero graded similarity, zero synonym/
paraphrase generalization, zero use of the substrate's OWN concept-similarity machinery anywhere in
the sourcing path -- a phone-book lookup keyed on exact surface strings, precisely the mechanism the
USER named. This is not a knowledge problem (the oracle cell proves the facts work) and not a
"needs more facts" problem (ConceptNet-breadth didn't move it) -- it is a matching-OPERATOR problem.

---

## 2. Audit: what frame_induction / script_grain / schema organs ACTUALLY provide vs. what a
frame-reader needs

| Needed capability | Candidate organ | Verdict (read the code) |
|---|---|---|
| **(a) TRIGGER -> FRAME IDENTITY**, graded/associative, not exact-keyword | `hdlab/frame_induction.py` | **FALSE FRIEND -- despite the name, wrong kind of "frame."** It induces an OOV VERB's THEMATIC case-frame (does its subject fill AGENT or EXPERIENCER?) from syntactic construction cues (`has_scomp`, `degree_mod`, `passive`, `arg_animate`...) via `hdlab.learner`. It answers "who is the AGENT," never "which stereotyped PROCESS (combustion, erosion...) does this clause describe." Not reusable for process-frame identification -- honest naming-collision catch, worth flagging before anyone assumes it's wired-in-waiting. |
| | `hdlab/lexical_similarity.py::concept_similarity(word_a, word_b)` | **RIGHT PRIMITIVE, currently unused for this purpose.** McRae-style shared-feature-bundle cosine, already validated elsewhere at meaningful open-vocab coverage (the E3 gate found 94% coverage via its WordNet-Tier2 extension). Direct drop-in replacement for the `set() & text_toks` line: score each process-frame's signature vocabulary against paragraph tokens via mean/max `concept_similarity`, not exact membership. |
| **(b) FRAME DEFINITION STORE** (typed slots + default fillers/fates, general not per-instance) | `tools/benchmark_trap_check/build_propara_process_physics_kb_v1.py` | **REUSE VERBATIM.** 18 hand-vetted process types (combustion, photosynthesis, respiration, erosion...), each with `signature`/`consumes`/`produces`/`moves` word lists -- a real, if rudimentary, Fillmore-style frame store (consumes ~ Patient-destroyed core role, produces ~ Patient-created, moves ~ Theme). TRAIN-topic-derived, leak-safe, already proven NOT the bottleneck (its content is what the oracle cell's `+0.1062` lift is built from). No content change needed for the first build. |
| | `hdlab/script_grain_acquisition_loop.py::ScriptLibrary` | **Right SHAPE, wrong scope for THIS build.** CA3/DG soft-match-or-spawn (`iterative_attractor` over FHRR register cosine) clusters recurring script INSTANCES once given `trigger_cat`/`consequent_cat` labels -- but only 4 FIXED roles (TRIGGER/CONSEQUENT/AGENT/PATIENT), and it consumes already-typed category tags, not raw surface text. Not a drop-in frame store; a genuine future upgrade path (LEARN new process types from corpus exposure instead of hand-authoring more) once this first build is wired and measured. |
| **(c) SLOT INSTANTIATION + BINDING** (incl. spawning implicit entities for never-mentioned fillers like oxygen/ash) | `hdlab/coreference_resolver.py::TrackedEntity`, `run_match_or_allocate` | **Owned, WIRED, covers MENTIONED participants only.** No existing path allocates an implicit-entity handle for a schema-default filler that has zero textual mention -- small, genuinely new glue code (Section 3). |
| | `hdlab/script_grain_acquisition_loop.py::build_instance_register` / `_ROLE_VECS` pattern | **Reusable PATTERN, needs generalizing.** FHRR bind-then-bundle over a fixed 4-role vocab is the right SHAPE for role-filler binding; extend to an OPEN per-process-type slot vocabulary (derived directly from each KB entry's `consumes`/`produces`/`moves` keys -- no new hand-authoring beyond what's already in the KB file). |
| **(d) FEED THE SITUATION MODEL + LOOP** | `hdlab/situation_model_accumulate.py::AccumulateRegister` / `CausalLinkRegister` | **Fully owned, WIRED, exactly right, NO CHANGE NEEDED.** `bind(role, event-slot)` accumulated per entity, decoded via unbind+`cleanup_argmax`; `CausalLinkRegister` already carries typed CAUSE/EFFECT. The frame's instantiated fates are exactly the `(effect, trigger_verb_class)` shape `_build_distilled_bridge_facts` already emits into this same downstream path. This stage is already correct -- it is simply starved of correctly-sourced input, the identical diagnosis the barrier map (B5) made for the encode path generally. |
| (peripheral) | `hdlab/schema_exemplar_bayes.py::SchemaExemplarBayesIndex` | **Not load-bearing here.** A retrieval-COMPRESSION router (LSE-Bayes over k-means clusters, 10x compression at ~10% recall cost) for SCALING lookup across many facts/schemas -- useful later if the process library grows past ~18 types and needs efficient routing, irrelevant to fixing THIS matching-mechanism bug at current scale. |

**Bottom-line audit finding:** 3 of 4 needed capabilities are owned and correct as-is (frame
content, role-bind pattern, situation-model destination); the 4th (associative trigger->frame /
participant->role matching) is the one genuinely missing piece, and it is a small, well-specified
swap-in, not a new organ class.

---

## 3. Minimal first B-build spec (hand to exp_dev)

**Cell:** `exp_propara_bridging_frame_activation_v1` -- direct successor to `exp_propara_bridging_
distilled_kb_endtoend_v1`, SAME harness / SAME controls / SAME official metric; ONLY the sourcing
step changes, which makes this a clean mechanism-isolation ablation against an already-landed
comparison point.

**STEP 1 (reuse verbatim, zero changes):** the 18-process hand-vetted `signature`/`consumes`/
`produces`/`moves` KB from `build_propara_process_physics_kb_v1.py`. TRAIN-topic-derived, no
TEST-gold leakage -- unchanged discipline, already audited leak-safe.

**STEP 2 (THE FIX -- new code, both sub-steps):**
- (2a) paragraph -> frame-type: replace `len(set(signature) & text_toks)` with a graded score --
  mean or max `lexical_similarity.concept_similarity(token, signature_word)` over paragraph tokens
  x each process's signature vocabulary. Handle `concept_similarity`'s `None` return (OOV pair) with
  the same honest-abstain discipline used elsewhere in this codebase, not a silent zero.
- (2b) participant -> role: same graded-similarity replacement for `p_toks & role_toks`.
- Threshold calibration: DEV-pinned before TEST, same discipline `quality_relation.py`'s
  `OPP_THRESH`/`SAME_THRESH` constants already use (calibrate-on-DEV, apply-unchanged-to-TEST, no
  test-set peeking) -- exp_dev owns the exact threshold value.
- **MANDATORY reporting:** run BOTH the literal-match numbers (already on disk, no rerun needed --
  `data/exp_propara_bridging_distilled_kb_endtoend_v1/metrics.json`) and the new graded numbers
  side by side. Same KB content, same downstream loop, ONLY the matching operator changes -- this
  isolates whether the mechanism-swap (not new knowledge) is what recovers lift.

**STEP 3 (new, small):** implicit-entity allocation for frame-slot fillers with no textual mention.
When the matched frame names a `consumes`/`produces` filler (e.g. "oxygen", "ash") that has no
coreference-resolver mention in the paragraph, allocate a synthetic `TrackedEntity`-shaped handle
tagged `IMPLICIT` (distinct from a real mention, inspectable in the trace). Bind it via the
`script_grain_acquisition_loop` FHRR bind-then-bundle PATTERN, extended from the fixed 4-role
vocabulary to an OPEN per-process-type slot vocabulary read directly off the KB entry's own
`consumes`/`produces`/`moves` keys (no new hand-authoring required beyond what Step 1 already has).

**STEP 4 (unchanged):** feed the resulting `(effect, trigger_verb_class)` facts into the SAME
`_grids`/retrieve-validate-advance loop path `_build_distilled_bridge_facts` already feeds --
bit-identical downstream consumption, keeping this a pure sourcing-mechanism ablation.

**CONTROLS (all already implemented in the existing harness; rerun unchanged, plus one new one):**
- `prior_lesion` (content-free floor) -- unchanged.
- `without_knowledge` (ablation) -- must stay collapsed (< 0.60 per existing bands).
- `with_oracle` (ceiling, +0.1062 lift) -- unchanged, the approach-target.
- NO-LEAK: graded-frame-activation F1 must stay < 0.95 and materially below oracle's 0.4626 (same
  leak-guard the distilled cell already applied).
- **NEW, load-bearing addition:** a SCRAMBLE-the-KB-content control (deterministic hashlib-seeded
  per PROT-023/F.5 -- randomly reassign each process type's `signature`/`consumes`/`produces`/
  `moves` word lists to a DIFFERENT process type). If the graded-matching win SURVIVES a scrambled
  KB, the win is coming from something other than genuine frame-content matching (a structural
  artifact of looser thresholds finding spurious hits), exactly the discipline that caught this
  session's earlier scramble-isometry bugs (E3/E3b). This is the single most important new control
  in this spec and must gate the HARD-PASS verdict, not just be reported.

**MEASURED AGAINST (pre-registered, both numbers already on disk):**
- **Floor:** SURVIVAL = 0.1823 (`exp_propara_bridging_distilled_kb_endtoend_v1`, literal matching).
  The new mechanism must beat this by a real, pre-registered margin, not noise.
- **Ceiling:** oracle_lift = +0.1062 absolute (F1 0.4626 vs 0.3564). The target to APPROACH, not
  necessarily reach -- partial recovery is a genuine, reportable result.
- **Reference (rules out the competing hypothesis):** ConceptNet co-participation arm, SURVIVAL
  0.2228, `cn_add=+0.0022` -- more/broader knowledge did NOT help, sharpening that this spec's
  target (the matching MECHANISM) is the right lever, not knowledge breadth.

**Falsifiable bands (axis fixed here; exp_dev owns exact numeric thresholds per
[[feedback-no-experiment-design-in-prompts]]):**
- **HARD-PASS:** survival fraction (graded_lift / oracle_lift) materially exceeds 0.1823 (a real,
  pre-registered margin -- e.g. a doubling, DEV-calibrated) AND `pair_recall` improves over 0.2469
  AND `pair_precision` improves over 0.0905 (BOTH must move -- a recall-only gain with flat/worse
  precision means the threshold is just looser, not more semantically correct) AND the scramble-KB
  control collapses toward the `without_knowledge` floor AND all existing ablation/leak/prior-lesion
  guards still hold.
- **HARD-FAIL:** survival stays within noise of 0.1823 (the mechanism swap doesn't matter -- routes
  to "the 18-process KB's TEST-split coverage is the real ceiling," i.e. SUPPLY more process types,
  not fix the matcher) OR `pair_precision` does not improve (graded similarity just finds MORE
  spurious matches -- the same phone-book problem in softer clothing) OR the scramble-KB control
  does NOT collapse (any lift is structural, not genuine frame-content matching).
- **MIDDLE_BAND:** recall improves but precision doesn't (or vice versa) -- informative split,
  localizes whether the residual problem is frame-IDENTIFICATION specifically or ROLE-MAPPING
  specifically; iterate the weaker half before spending the `--full` TEST budget.

## Cheap decisive test

A `--smoke` (DEV split) run is the cheap, can-fail, one-variable gate before `--full` (TEST): does
the DEV-split graded-matching survival fraction clear the DEV-calibrated HARD-PASS band, does
`pair_precision` visibly move (not just `pair_recall`), and does the scramble-KB control collapse
on DEV? If any of the three fails on DEV, do not spend the `--full` budget -- iterate the threshold
or localize which sub-step (2a vs 2b) is weak first. This reuses the exact smoke/full discipline
every other ProPara bridging cell in this arc already follows.

---

## 4. Honest tractability verdict + the hard tail

**Per-instance, the mechanism is bounded and glass-box-tractable, and this is now disk-grounded, not
just brain-analogical.** Given a KNOWN frame (combustion) and a graded-similarity matcher, generating
its unmentioned participants' fates and binding them to the triggering step is a small, composable,
already-mostly-owned pipeline (associative match -> slot lookup -> implicit-entity bind ->
situation-model write) -- and this session's own oracle cell already PROVED the downstream mechanism
is load-bearing (+0.1062 real lift) once facts are correctly sourced. That is a genuinely stronger,
more specific basis for optimism than a literature survey alone could offer.

**The hard tail is coverage + generalization, exactly where this cycle's three independent
lit-scans converged (deflated per calibration):**
1. **Messy/novel surface -> frame grounding for processes NOT in the hand-vetted 18.** Open-domain
   frame/implicit-argument coverage is the historically hard part: the computational-tractability
   lit-scan found symbolic/feature-based implicit-argument recovery plateaus around F1 ~20-50% on
   small curated predicate sets in the published literature (SemEval-2010 best system ~0.19 on open
   genre; Gerber & Chai ~50% on 10 curated predicates), with no demonstrated open-domain-general
   version at that level, and the discourse-psychology lit-scan independently found the field's own
   50-year arc (scripts -> MOPs/TOPs retreat, the "script applicability"/frame-selection problem) is
   evidence AGAINST a small hand-built library achieving human-reader-scale coverage without either
   a much larger curated store or a statistically-learned selection/filling component.
2. **Multi-frame chains / frame composition.** A paragraph invoking two related processes (e.g.
   combustion feeding a phase-change) has no owned composition mechanism yet -- `ScriptLibrary.
   match_or_spawn` handles ONE frame instance at a time, not cross-frame composition.
3. **The scramble-KB control (Section 3) is the load-bearing honesty check** for whether this build
   is really doing graded frame-matching or just fuzzier keyword matching -- if it fails to collapse,
   the correct report is that the "fix" is not yet the mechanism the brain-grounding section claims,
   not a quiet reframe of what counts as success.

**Net:** this is NOT a full solve of the extraction/reading wall -- it is the correctly-identified
NEXT mechanism-level fix for the ProPara bridging sub-problem specifically, well-grounded in both
brain evidence (Section 1) and this session's OWN measured data (oracle lift real; literal-match
survival low; ConceptNet-breadth didn't help). Scaling past the 18 hand-vetted processes to genuine
open-domain science-process coverage is the honest hard tail and should be a separate, later,
explicitly-gated decision -- do not fold it into this build's success criteria.

**P_deflated:** for "graded-similarity frame-activation beats the 0.1823 literal-match floor by a
real, controls-clean margin on TEST" -- **P ~ 0.45** (novel-synthesis cap 0.50; undeflated ~0.60-
0.65, deflated for uncharted-combination risk on this exact harness, per calibration discipline).
This is comparatively high-confidence for this program because the failure mode is precisely
diagnosed on disk (not inferred), `concept_similarity` is independently validated elsewhere at
meaningful coverage (94% in the E3 gate), and the "more knowledge alone doesn't help" ConceptNet
control already rules out the main competing hypothesis. For "this closes MOST of the 0.82 survival
gap to oracle (e.g. survival >= 0.6)" -- lower, **P ~ 0.20** (the 18-process KB's coverage of the
TEST split's actual process diversity is untested and could cap partial recovery well short of
oracle, independent of whether the matching-mechanism fix itself works).

---

## Cross-thread synthesis

- Directly extends and sharpens `notes/research_comprehension_barrier_map_brain_foundational_
  2026-08-10.md`'s B5 (event/outcome-span extraction) / B8 (causal/bridging inference) diagnosis:
  that map named "extraction" as the binding constraint at a coarse grain; this drill localizes the
  SPECIFIC failing operator (literal keyword matching at bridging-fact sourcing) and names the
  specific fix (graded associative matching), turning a program-level diagnosis into a buildable
  cell.
- Builds directly on `notes/research_psych_bridging_inference_situation_models_2026-08-09.md`
  (read in full this cycle): that note's section 4 conclusion -- "the mechanism that makes [goal-
  outcome] inference cheap is... a goal-narrowed candidate set + activation-relaxation settling...
  script-slot-filling generalized... to arbitrary goal-outcome pairs" -- is the SAME mechanism this
  spec targets, here specialized to PROCESS frames instead of GOAL frames; both point at the same
  underlying primitive (graded concept-similarity matching replacing hand-pool/exact lookups).
- Directly reframes `notes/research_propara_content_driven_order_dependent_state_update_2026-08-10.
  md`'s finding (ARM-1's RETRIEVE step is "a single-step, memoryless BoW/mention classifier" and
  VALIDATE is "content-blind... index bookkeeping"): that drill diagnosed a SEQUENTIAL/state-
  carryover gap in the reasoning LOOP; this drill diagnoses a DIFFERENT, earlier-stage gap in
  bridging-FACT SOURCING -- the two are complementary, not competing, fixes on the same arc.
  `exp_propara_decisive_inference_arm1_v3_stateful_verb_v1` (HARD_PASS, order-dependent localization
  signal) and `exp_propara_arm2_extracted_structure_v1` (HARD_FAIL, signal vanished under real
  extraction) are the sibling cells this build spec's cell should be read alongside once landed.
- Supersedes the generic, never-built "FrameNet top-200 codebook" idea from `notes/exp_dev_handoff_
  research_nl_understanding_universal_unlock_3x_2026-06-11.md` / `notes/research_drill_tier2_
  problem_schemas_2x_2026-06-11.md` with a mechanism-precise, disk-grounded target (fix an existing,
  measured, HARD_FAIL matching step on a live benchmark) rather than a speculative new codebook.

## Substrate-product implications

If HARD-PASS: the substrate gains a validated, reusable pattern -- "associative graded-similarity
matching for trigger-to-schema and filler-to-role assignment, replacing literal keyword/exact-string
lookup wherever a KB or lexicon is consulted from real text" -- directly transferable beyond
ProPara to any future real-prose consumer of hand-authored or distilled knowledge (WIQA's polarity-
KB sourcing hit an analogous "world-knowledge SUPPLY" wall per the WIQA meta-verdict; the same
graded-matching fix is a candidate there too, though WIQA's problem was diagnosed as missing FACTS
more than a broken matcher and would need its own re-audit before assuming transfer). The glass-box
trace gets a genuinely new, inspectable node: WHICH frame was activated, WHICH slots were filled by
mention vs. implicit-allocation, and WHY (the graded score), which is a strictly richer audit trail
than the current silent literal-match/no-match binary.

If HARD-FAIL: the failure localizes cleanly to either (a) the 18-process KB's coverage of TEST-split
diversity (routes to SUPPLY more process types, a data problem) or (b) the scramble-KB control not
collapsing (routes to a deeper rethink of whether graded similarity over small hand-typed vocabularies
is discriminative enough at all, independent of matching being literal vs. graded) -- both are
actionable, bounded follow-ups, not a dead end for the frame-activation direction generally.

## Citations (verified count)

Carried from this cycle's 3 parallel Sonnet lit-scan sub-agents (discourse-psychology inference
theory; neural substrate for generative/temporal-binding inference; computational tractability of
implicit-argument/script generation) plus this session's own `research_psych_bridging_inference_
situation_models_2026-08-09.md` (read in full, not re-derived). ~45 distinct sources across the
three lit-scans with per-item HIGH/MEDIUM/LOW confidence flags preserved in the sub-agent outputs;
key items surfaced directly above: McKoon & Ratcliff 1992 (*Psych Review* 99); Graesser, Singer &
Trabasso 1994 (*Psych Review* 101); Schank & Abelson 1977; Bower, Black & Turner 1979 (*Cognitive
Psychology* 11); Graesser, Gordon & Sawyer 1979 (*JVLVB* 18); Kintsch 1988 (*Psych Review* 95);
Zacks, Speer, Swallow, Braver & Reynolds 2007 (*Psych Bulletin* 133); Franklin, Norman, Ranganath,
Zacks & Gershman 2020 (SEM, *Psych Review* 127); Baldassano, Chen, Zadbood, Pillow, Hasson & Norman
2017/2018 (*Neuron* / *J Neurosci*); Van Kesteren et al. 2012/2013 (SLIMM, *TINS*/*Neuropsychologia*);
Ghosh & Gilboa 2014 (*Neuropsychologia*); Whitney, Kirk, O'Sullivan, Lambon Ralph & Jefferies 2011
(*Cerebral Cortex*); causal-inference-in-discourse meta-analysis (PMC8261065); Ruppenhofer et al.
SemEval-2010 Task 10; Gerber & Chai 2010/2012; Chambers & Jurafsky 2008/2009 (ACL); St. John &
McClelland 1990/1992 (Story Gestalt); Bosselut et al. 2019 (COMET, ACL); Hwang et al. 2021
(COMET-ATOMIC2020, AAAI). No citation fabricated; every item traces to a specific sub-agent
WebSearch/WebFetch result or a directly-read prior session note. Applying the mandatory calibration
penalty (deflate 0.15-0.25, novel-synthesis capped at 0.50): see Section 4 P_deflated values above.

## Bottom line

The USER's reframe is correct and now disk-confirmed on this substrate's own data: the SRL+KB-lookup
approach that capped ProPara bridging-fact sourcing at survival=0.18 used literal keyword-set-
intersection at both the frame-identification and participant-role-mapping steps -- a structurally
brittle phone-book operation -- while the SAME arc's oracle cell proves the underlying knowledge and
downstream mechanism ARE load-bearing (+0.1062 real lift) once facts are correctly sourced, and a
broader-but-promiscuous KB (ConceptNet) did NOT help, ruling out "just needs more facts"; the fix
licensed jointly by the brain literature (script/frame default-slot activation, cheap because it is
associative not exhaustive) and by the owned organs (concept_similarity for graded matching,
script_grain_acquisition_loop's FHRR role-bind pattern extended to an open slot vocabulary, and the
already-correct situation_model_accumulate destination) is a small, mechanism-precise, glass-box-
tractable next build -- `exp_propara_bridging_frame_activation_v1`, fully specified in Section 3,
measured directly against the disk-verified 0.1823 floor and +0.1062 oracle ceiling, gated by a
scramble-KB control that is the load-bearing honesty check on whether this is genuine frame-content
matching or just softer keyword matching -- with the explicit, undeferred honest limitation that
open-domain coverage beyond the 18 hand-vetted processes and multi-frame composition remain a
separate, later-gated hard tail, not something this first build claims to solve.
