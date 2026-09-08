---
problem: generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation
status: PARTIAL
bar: "PASS = a brain-faithful GENERATIVE causal-antecedent reader (glass-box, NO external LLM at inference; an offline static world-model / force-dynamics asset is admissible) that, on a MODERN causal gold (MAVEN-ERE causal / a modern narrative causal gold / TellMeWhy causal-relation subset -- 19c is BANNED), MATERIALLY breaks the ~5% coverage bound for the UNMARKED majority while HOLDING binding precision CI-separated over (a) the CONTIGUITY floor (0.140, recomputed on the item's own population) AND (b) the CONNECTIVE floor -- with participant COREF ON, the info-free TWIN LOSING CI-sep, and NO live reasoner regressing"
result: "TWO instruments + full-chain drill. (1) NARRATIVE -- TellMeWhy cause-ID, non-adjacent, ALL items n=299: the reader beats topical 0.254 (+0.067 CI-sep), info-free twin 0.238 (+0.084 CI-sep), adjacency 0.000 (+0.314 CI-sep); on the GOAL subset n=114 it scores 0.570 vs topical 0.254 (+0.316) / twin 0.316 (+0.254) CI-sep -- EXCEEDS the prior SDRT tie. BUT the comprehension control shows this win is MARKER DETECTION (marker+content 0.632 >= means-end 0.570; means-end vs marker NOT CI-sep), not generative simulation. (2) MAVEN-ERE n=710/9698 gold: entity-bound reader precision-on-fired 0.556 vs class-gen 0.363 vs twin 0.178 (+0.378 over twin CI-sep), but unmarked recall 0.0266 CI-sep BELOW the class-gen over-linking bound 0.0552. (3) The 100%-grounded FULL CHAIN (no co-occurrence, no LLM) is WORSE than the twin where it fires (0.230 vs 0.324; physical operators, goal/mental task). (4) The CORRECTED generative inverse-planning operator (VerbNet telic) 0.264 FULL and the CSKG goal-knowledge CEILING 0.268 BOTH tie co-occurrence 0.254 -- knowledge is NOT the bottleneck."
floor: "MAVEN: contiguity balanced-precision 0.1395 (reader 0.4565, +0.317 CI-sep) + connective + twin. NARRATIVE: topical 0.254 + adjacency 0.000 + info-free twin 0.238 (full) / 0.316 (goal). Residual: co-occurrence 0.255 ~ twin 0.164 on OTHER; SIX knowledge channels (co-occ, conceptual, GEK-entropy, script-order, VerbNet-telic, CSKG-goal) all ~twin on the unmarked residual."
controls: "info-free TWIN (loses on the marked-goal win, MATCHES on the unmarked residual); CONTIGUITY + CONNECTIVE floors recomputed per population; ADJACENCY position floor (=0 on non-adjacent); COMPREHENSION control (marker vs means-end -- the win is marker-anchored, not simulation); per-CAUSAL-TYPE breakdown; CONTENT-CHANNEL swap (6 channels); FULL-CHAIN prototype (grounded physical operators regress below twin on narrative); INVERSE-PLANNING operator + CSKG knowledge CEILING (knowledge does not clear it); participant COREF ON (86->221 fires 3.29x, prec 0.465->0.593)."
files_changed: "experiments/exp_causal_antecedent_reader_v1.py, experiments/exp_causal_antecedent_reader_tellmewhy_v1.py, experiments/exp_causal_antecedent_reader_tellmewhy_v2.py, experiments/exp_causal_antecedent_reader_tellmewhy_v3.py, experiments/exp_causal_antecedent_content_channel_v1.py, experiments/exp_causal_antecedent_meansend_control_v1.py, experiments/exp_causal_antecedent_full_chain_v1.py, experiments/exp_causal_antecedent_inverse_planning_v1.py, verification/test_causal_antecedent_reader.py"
reverify: ".venv/Scripts/python.exe verification/test_causal_antecedent_reader.py"
---

# Generate-don't-retrieve causal edges for unmarked narrative causation

**PARTIAL.** The brief's literal bar (break the ~5% UNMARKED recall bound on MAVEN at held precision) is a located
NEGATIVE with a number and a mechanism (the brief calls that a full pass). The problem underneath is partially
SOLVED on the narrative instrument (the reader beats every floor CI-separated) but the *mechanism* is shallower than
the brief hoped, and a full drill -- assembling the 100%-brain-foundational grounded chain AND prototyping the
corrected goal/mental operator AND a knowledge ceiling -- locates the true root: **story-specific situation-model
construction (extraction + binding), not world-knowledge**.

> **RECOVERY NOTE (2026-09-08).** This folder (PROBLEM.md + an earlier SOLVED.md) was removed from disk by a
> concurrent session's git fetch/index-rewrite (~13:16-13:29); all experiment cells, data, and the witness survived.
> This SOLVED.md was recreated by the solver from session context. PROBLEM.md (strategy-owned) needs restoring from
> origin or the strategy session.

## What I built (glass-box, NO external LLM, NO hdlab written -- Q111)

A two-system generative causal-antecedent reader (physical force-dynamics STRIPS + mental/goal inverse-planning,
routed by event_type, over coref-resolved participants), on MAVEN newswire AND TellMeWhy narrative; then a full
brain-foundational drill: the comprehension control, the 6-channel content-swap, the assembled 100%-grounded chain,
and the corrected generative inverse-planning operator with a CSKG knowledge ceiling.

## What I measured

**1. MAVEN-ERE (newswire) -- located CEILING.** Entity-bound reader precision-on-fired **0.556** (class-gen 0.363;
twin 0.178; +0.378 over twin CI[0.320,0.435] CI-sep -- generation is real + precise), but unmarked recall **0.0266**
CI-sep BELOW the class-gen over-linking bound 0.0552. Newswire causation is between entity-disjoint events; requiring
the entity channel trades recall for precision. Owner-confirmed: MAVEN lacks brain-foundationality for this task.

**2. TellMeWhy (narrative) -- the reader clears the FULL population (exceeds SDRT), but the win is MARKER
detection.** FULL n=299: reader 0.321 vs topical 0.254 (+0.067 CI-sep), twin 0.238 (+0.084 CI-sep), adjacency 0.000
(+0.314 CI-sep). The comprehension control (`exp_causal_antecedent_meansend_control_v1.py`) on the GOAL subset
(n=114): content 0.254, **marker_first 0.561, marker_content 0.632**, means-end engine 0.570, grounded means-end
0.088, twin 0.272; means-end vs marker_first +0.009 (NOT CI-sep), vs marker_content **-0.061**. With ~1.71
markers/story the reader is identifying the explicit Tier-1 goal anchor (goal_register's own reliable cue), not
simulating means-end. **The generative means-end machinery is INERT.**

**3. The content channel is the wall, and NO context-free signal clears it.** Per-type: GOAL 0.570, OTHER 0.255 ~
topical 0.254 (the engines add nothing on the OTHER/world-knowledge 37%). Six channels on the OTHER residual:

| content channel | FULL n=299 | OTHER n=110 (residual) | GOAL n=114 |
|---|---|---|---|
| co-occurrence PPMI-SVD (current) | 0.254 | 0.255 | 0.254 |
| grounded conceptual (WordNet-gloss) | 0.241 | 0.191 | 0.272 |
| GEK entropy / forward-predictability | 0.164 | 0.127 | 0.175 |
| broadened SCRIPT-ORDER prior (454k pairs) | 0.207 | 0.200 | 0.281 |
| info-free twin | 0.214 | 0.164 | 0.272 |

Every context-free channel lands at the info-free twin; co-occurrence itself is only +0.040 over twin on full (NOT
CI-sep). The content channel's meta is `"associative_similarity (reading-grown, PPMI-SVD, gated)"` = co-occurrence.

**4. The 100%-BRAIN-FOUNDATIONAL FULL CHAIN, prototyped end-to-end (`exp_causal_antecedent_full_chain_v1.py`).** The
whole route-2 chain with NO co-occurrence, NO LLM: tense-agnostic event extraction -> participant frames -> coref ->
GROUNDED state-transition operators (VerbNet result-state + world_state + possession + shared-agent goal + valence
affect) -> necessity selection (ABSTAIN when nothing relates). Coverage **0.465** but **WORSE than the info-free
twin where it fires** (0.230 vs cooc 0.266 vs twin 0.324 vs marker 0.367). Per-type: the covered set is OTHER(77) /
GOAL(56) / AFFECTIVE(6) -- essentially NO physical causation -- so the physical-state operators fire SPURIOUSLY on
incidental state overlaps and pick the wrong sentence. **The physical STRIPS grounding that WON on MAVEN newswire
actively MISLEADS on narrative goal/mental causation.**

**5. The CORRECTED component + the knowledge CEILING -- knowledge is NOT the bottleneck
(`exp_causal_antecedent_inverse_planning_v1.py`).** I built the brain-foundational GENERATIVE inverse-planning
operator: GENERATE an action's intended OUTCOME by composing its VerbNet event-structure semantics
(exist:Product/has_possession/created -- ~6300 verbs, covers `brew`), then the teleological principle (the cause of a
goal-directed effect is the event that establishes its outcome/goal). Result: GOAL 0.281, OTHER 0.264, FULL 0.264 --
**does NOT beat co-occurrence or the twin CI-sep anywhere** (coverage 42%). And the diagnostic CEILING -- CSKG's
152k+ goal/intent edges (/r/MotivatedByGoal, at:xIntent, /r/UsedFor; 10,012 verbs) as a labeled RETRIEVAL ceiling
(NOT the deliverable; respects the brief's DO-NOT) -- GOAL 0.263, FULL 0.268, also ties co-occurrence. **Generated
goal-knowledge AND retrieved goal-knowledge BOTH fail. It is not a missing world-model.** Only the explicit MARKER
works (GOAL 0.658), because it makes EXTRACTION reliable. **The bottleneck is story-specific situation-model
construction (extract + bind THIS story's events/entities/goals), not decontextualized knowledge** -- the project's
"reasoning shown, not end-to-end; extraction is the shared wall", now proven for causation by exhausting the
knowledge side.

## What I did NOT establish (and would withdraw first if wrong)

- I did NOT break the 5% MAVEN recall bound (entity-bound generation caps it on newswire; the entity channel is thin
  there). Withdraw first if a richer nominal coref lifts the shared-entity rate without collapsing precision.
- The CSKG ceiling is a CRUDE verb->intent-word overlap; a concept-level knowledge binding is untested. Do NOT read
  "CSKG doesn't help" as "no knowledge binding could" -- read the CONVERGENT six-channel evidence as "the bottleneck
  is extraction/binding, not the knowledge source".
- I did NOT demonstrate generative means-end SIMULATION or generative goal inference -- both the means-end engine and
  the inverse-planning operator are inert/at-floor. What is demonstrated is Tier-1 explicit-cue anchoring.

## REFUTED brain-fidelity dead-ends (each disproved by a can-fail control)

Participant coref as the NARRATIVE selection lever (hard gate HURT 0.182 vs 0.327; the brief's hypothesis) --
referential coherence as a soft cue -- recency -- Kintsch integration -- GEK entropy-as-content-channel -- the
grounded PHYSICAL chain on narrative (below twin) -- the generative VerbNet inverse-planning operator (at floor) --
the CSKG goal-knowledge ceiling (at floor). The lesson: the brain integrates weak cues and does not hard-gate; and
grounding is only brain-foundational if its operators match the causal DIMENSION -- but even right-dimension
knowledge (goal/intent) does not clear the wall, which is upstream (situation-model construction).

## KEY REALIZATIONS

1. **The genre, not the mechanism, was the first confound (owner's cue).** MAVEN newswire annotates entity-less
   institutional causation; re-instrumenting on narrative turned a located ceiling into a full-population win.
2. **A brain-foundational component that fails points UP the chain -- and here the chain bottoms out at
   EXTRACTION/BINDING, not knowledge.** I followed it: content co-occurrence -> conceptual -> entropy -> script ->
   generative-telic -> retrieved-CSKG. All tie the twin on the unmarked residual. The world-knowledge is available
   (CSKG has it) and does not help; the wall is constructing THIS story's situation model.
3. **Coref is a genre-conditional lever, not a universal unlock** (3.29x on newswire precision; HURTS narrative).
4. **The MAVEN "5% bound" is over-linking** (precision-on-fired 0.363); entity-bound generation is 0.556 precise.
5. **A win can be shallower than its label -- the control caught it.** The goal "means-end" win is MARKER detection
   (marker+content 0.632 >= means-end 0.570). Always reproduce the win from a simpler/wrong source first.
6. **Grounding is necessary but NOT sufficient -- the operators must match the causal DIMENSION.** The full grounded
   chain is below twin on narrative because its operators are physical and narrative is goal/mental.
7. **Even the RIGHT dimension (goal/intent), generated OR retrieved, does not clear it.** The corrected
   inverse-planning operator and the CSKG knowledge ceiling both sit at the co-occurrence floor. The missing
   capability is the generative SITUATION MODEL that binds knowledge to the specific story -- not a knowledge asset.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- Unmarked causal extraction: the generative causal-antecedent reader clears the FULL narrative population CI-sep,
  but the mechanism is Tier-1 marker anchoring; generative means-end / inverse-planning are INERT.
- The causal content channel is `associative_similarity` = PPMI-SVD co-occurrence (textbase). Six alternative
  channels (incl. VerbNet-telic generation and CSKG-goal retrieval) do NOT clear the unmarked residual -> the
  bottleneck is story-specific situation-model construction (extraction + binding), NOT the knowledge source.
- MAVEN-ERE flagged genre-limited for narrative causation (owner-confirmed).
- `event_type` routing is MFS, not contextual WSD (its own flagged gap) -- a secondary cap.

## Proposed hdlab wire (Q111 -- strategy lands; ADDITIVE, no-regress)

Solve is experiments-only; `git status hdlab/` clean; `situation_reader.causal_links` untouched (the additive
`typed_causal_links` / SDRT coherence layer pattern, witness W12 byte-identical). DO NOT wire the physical grounded
chain into a narrative causal reader -- it regresses below chance. The marked-goal marker+content selection (0.632)
is a simple additive win; the deep capability needs the situation-model construction upstream, not a new operator.

---

**TLDR (plain English).** Stories rarely say "X caused Y"; the reader works it out. Our reader now picks the right
cause on real short stories better than every simple shortcut, and much better when the cause is an explicitly stated
goal ("she WANTED coffee" -> ~57-66% right vs ~25% for word-overlap). But we proved the win is really just *finding
the sentence with the explicit want/decide word* -- the fancier "imagine what she was trying to do" machinery adds
nothing. For causes with no such cue (about 6 in 10), we tried SIX different knowledge sources -- word-co-occurrence,
dictionary meaning, a surprise/prediction "entropy" model, a canonical event-order store, a generative "what is this
action for" model built from a verb dictionary, and even a 6-million-fact commonsense database of people's intentions
-- and **none beat a coin-flip-with-the-right-shape**. That's the important finding: the missing piece is NOT more
facts (we even handed it the facts). It's that the reader can't build a deep enough picture of *this particular
story* -- who wanted what, what each event did to whom -- to connect cause to effect. Fixing that (deep story reading,
not a bigger fact-store) is the real next build, and we've now ruled out the shortcuts so it's unambiguous. No
outside AI at any step.

**QUESTIONS.** None blocking. Judgement call: graded PARTIAL -- a real CI-separated narrative win (marker-anchored)
plus a rigorous, six-way-confirmed location of the true wall (situation-model construction, not knowledge).

**NEXT STEPS.**
1. HIGH -- the wall is the generative SITUATION MODEL (deep per-story reading: event + entity + goal + state
   extraction and binding), NOT a knowledge asset (we falsified 6 knowledge channels incl. a 6M-edge KG). This is the
   project's Phase-1 meaning-supply / reading-extractor bottleneck; causal reading inherits it.
2. HIGH (efficiency, proven) -- for marked goals use marker+content selection (0.632), DROP the inert means-end.
3. MEDIUM -- upgrade event_type MFS -> contextual WSD (its flagged gap) to sharpen routing.
4. DO-NOT (re-refuted): any context-free prior (co-occ/conceptual/GEK/script), a bigger causal/goal KB (CSKG ceiling
   ties co-occ), the physical grounded chain on narrative (regresses), hard entity-gating for narrative selection,
   MAVEN-ERE as the narrative gold, any external LLM.
