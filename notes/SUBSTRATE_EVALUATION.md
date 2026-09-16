# Substrate evaluation

> **LATEST REVIEW COMPLETE (2026-09-15):** Start with [Focused follow-up: time, goals and belief consistency](#focused-follow-up-time-goals-and-belief-consistency). It contains six new findings R01-R06 and optimization O01, with isolated reproductions and exact commands in A11. The earlier D/E sections are versioned history. The local status notes record D-series integration under priorities 131/132; the None sentinel guard is visible. Latest reviewed reader SHA-256: `2210b4bb21c97d2d6eed42220e2b44105d1b2ed5dbb78b50e1ed2bc718cbf517`. Source files remain unchanged by this evaluator.

**Status: COMPLETE — current-code deep static review and historical execution record, 2026-09-15.** The owner reports that the earlier findings were addressed. The active reader changed after those runs. This second pass inspected the updated implementation without launching additional models, tests or benchmarks during concurrent development. Eight current-code findings, proposed improvements and acceptance cases are below.

> **VERSION NOTICE:** D01-D08 concern the inspected current source. E01-E13 and all runtime percentages are historical and must not be presented as current open defects or current performance. The earlier reader hash was `62ee788a9c4857752c9798bd6af373b5acb88579f70465cfa69977840c52aa14`; the deep review inspected `491f5c7d13cdb58ee20c146cb5c7a564df02b2a56ce8c09eb3d5049d7f8d5598`, with `discover_pronouns=True`, `fill_card=True` and `graded_anaphora=True`. That hash remained the same at the final static check. The current section acknowledges the visible fixes; A9 records all 13 reviewed source hashes.

**Report location:** `C:/AI/hd-instrument/notes/SUBSTRATE_EVALUATION.md`.

Navigation: [Current assessment and findings](#current-code-deep-review) | [Current work order](#suggested-work-order-and-reviewable-completion-criteria) | [Current limitations](#limits-of-this-current-code-pass) | [Historical runtime assessment](#historical-runtime-assessment) | [Exact executions](#execution-appendix-exactly-what-ran) | [Current source manifest and static commands](#a9-current-code-static-review-version-manifest-and-exact-programs).

## Scope and permissions

The owner requested an independent evaluation of the current substrate, followed by a detailed, actionable report. Code, configuration, existing documentation, assets and published benchmark results are not to be edited. This report is the only repository file authorized for editing. Evaluation scripts are supplied directly to Python; small input fixtures use temporary files outside the repository. No changes are committed or pushed.

The inspected repository is `C:/AI/hd-instrument`. Initial inspected HEAD: `69ebac2f0`. The working tree already contains edits, including `hdlab/situation_reader.py`, `hdlab/coref.py`, `hdlab/referent_per_np.py` and `experiments/gum_coref.py`. Results describe the working tree actually executed, not a clean checkout of that commit. Concurrent work can change the tree; revision and asset provenance are therefore important limitations.

### Evidence labels

- **REPRODUCED:** executed during this evaluation and observed directly.
- **CODE OBSERVATION:** established by reading current source; not necessarily exercised at runtime.
- **RECORDED:** found in existing results or project notes; not independently reproduced here.
- **RECOMMENDATION:** a proposed change, not implemented or demonstrated.

Priorities in this report: **P0** = address before relying on the headline board to direct capability work; **P1** = important correctness, evidence or integration work; **P2** = reproducibility and maintenance improvements. These are research priorities, not production-incident severity labels.

## Focused follow-up: time, goals and belief consistency

**Completed 2026-09-15.** This third pass focused on whether correct component outputs remain correct when the reader stores state and answers time- or agent-constrained questions. It found **six new correctness issues and one quantified optimization opportunity**.

**Version:** C:/AI/hd-instrument, observed HEAD 951ae510cb9347a3805c217569fa5dbd9439d9a7, branch dataprep/mcguffey-graded-corpus. Findings apply to the working files, especially reader SHA-256 2210b4bb21c97d2d6eed42220e2b44105d1b2ed5dbb78b50e1ed2bc718cbf517. The final source check at 2026-09-15 23:53 UTC found the same reader hash.

### Earlier fixes: actual checkout status

The owner expected D01-D08 to be addressed. This checkout contains the D02 sentinel change from -1 to None. Its notes/STATUS.md explicitly lists D02/D05/D06 under priority 131 and D01/D03/D04/D07/D08 under priority 132, with the guard already landed. Thus the local evidence indicates **in-flight integration**, rather than all fixes present in these files.

The inspected code still shows the old polarity handoff, text-keyed sentence cache, empty belief mentions, head-keyed graded resolver, graded scoring issues and joint frontend cache/fallback behavior. D07 was not independently re-audited in this pass. These are prior backlog items, not counted among the six new findings below. A checkout clarification was requested; the review proceeded on the existing authorized path.

### Method and evidence strength

The checks used standard-library-only component loading and exact reader/driver function bodies extracted through Python AST. Extraction, parsing, perception and projection dependencies were replaced with small controlled fixtures. Source bodies were not edited. This allows deterministic checks of the handoffs without loading reader models, processing corpora or competing with active benchmark jobs.

**REPRODUCED IN ISOLATION** below means the actual selected logic produced the reported result for controlled inputs. It does not mean a complete raw-text read reproduced the same story. The fixtures deliberately supply correct upstream information to locate losses downstream. No accuracy or latency claim is made for the full reader.

| ID | Priority | Result |
|---|---|---|
| R01 | P1 | Reader writes every entity state at time zero |
| R02 | P1 | An agent-constrained explanation query returns another agent's purpose |
| R03 | P1 | Goal realization ignores target arguments and within-sentence ordering |
| R04 | P1 | Time-limited prediction consumes goals from later in the document |
| R05 | P1 | Belief events in one sentence overwrite observation identity and tie in time |
| R06 | P1 | Future testimony retroactively changes earlier knowledge |
| O01 | P2 | Belief observation repeats a full passage parse for every reality event |

### R01. Entity-state history loses all sentence timestamps

**REPRODUCED IN ISOLATION.** _read_entity_states records each EntityState.sent_idx correctly, but calls reg.apply_state(holder.lower(), prop.lower()) without t. StateRegister.apply_state defaults t to zero.

With controlled correct extraction of “door is open” at sentence 0 and “door is closed” at sentence 1, the reader method produced:

- Source sentence indices: [0, 1].
- Register spans: open [0, 0), closed [0, infinity).
- open at t=0: False; closed at t=0: True.

The control using the same register with explicit t=0 and t=1 preserves the earlier open state. This isolates a wiring defect rather than an inability of the register to represent history.

**Fix:** pass the intended time coordinate explicitly; retain within-sentence order where needed. Distinguish sentence time from event/chronological time across public APIs.

**Acceptance:** opposite states at different sentences preserve both historical answers; a query before the second state cannot see it. Include multiple updates in one sentence and repeated unchanged states.

**Source:** hdlab/situation_reader.py:4442 (_read_entity_states); hdlab/state_register.py:358,397.

### R02. “Why did Alice do this?” can return Bob's purpose

**REPRODUCED IN ISOLATION.** GoalRegister.why filters candidates by the requested agent, then uses “filtered candidates or original candidates.” When the requested agent has no matching purpose, the function restores another agent's candidates.

With only Bob's purpose for working recorded, why('work', 'bob') correctly returns Bob; why('work', 'alice') also returns Bob.

**Fix:** preserve the agent constraint. Return unavailable, or an explicitly labeled fallback belonging to the requested agent. Do not silently broaden an identity-constrained answer.

**Acceptance:** querying an absent agent never returns another agent's goal. Test two agents doing the same action for different reasons and an unconstrained query.

**Source:** hdlab/goal_register.py:393.

### R03. Goal satisfaction checks the verb/agent, but not what was achieved

**REPRODUCED IN ISOLATION.** Both track_status and track_status_thwart compare a later event's predicate and agent against the goal. They omit target arguments. Both also require the event's sentence index to be strictly greater than the goal's sentence, excluding a later action in the same sentence.

For Alice's “buy bread” goal, both functions returned:

| Supplied event | Status |
|---|---|
| Alice buys bread in the next sentence | satisfied |
| Alice buys a car in the next sentence | satisfied |
| Alice buys bread later in the goal's sentence | active |

All fixture events were positive, so this is independent of the earlier polarity issue. Goal.goal_text retains “buy bread,” but the realization predicate does not use the object.

**Fix:** represent the target proposition with relevant arguments and compare it to the realized event. Use ordered event/token positions for same-sentence realization. Treat missing target information as uncertainty rather than automatic equivalence. Apply equivalent target scoping to failure/thwart attribution.

**Acceptance:** buying a car does not satisfy buying bread; buying bread later in the same sentence can satisfy it; actor, recipient and object contrasts remain distinct. Test these after event extraction as well as in the status functions.

**Source:** hdlab/goal_register.py:88,418,553.

### R04. Time-limited prediction reads future goals

**REPRODUCED INPUT LEAK; prediction score effect not measured.** _read_prediction's passage helper respects t, but _goal_lemmas has no t argument. It enumerates agents from the full event list and reads the full-document wants register.

A controlled t=0 query had identical passage context in two cases:

- Prefix-only model: context [alice, arrived], goal evidence [].
- Full-document model with a goal at sentence 5: context [alice, arrived], goal evidence [buy, yacht].

The projector was a recorder, not a learned model. This proves the closure passes future evidence, not that a particular candidate score changed. The related theory-of-mind path also obtains desired values from an untimed wants lookup while accepting a time for belief.

**Fix:** provide goals and their status as of the query's time. Filter both agent population and goal evidence. A goal's final achieved/failed status is not necessarily its status at an earlier point.

**Acceptance:** predicting at time t gives identical model inputs for a document prefix and that same prefix with unrelated future goals appended. Repeat for predict_action with changing desires.

**Source:** hdlab/situation_reader.py:3677 (_read_prediction),3292 (_read_tom_action); hdlab/goal_register.py:379.

### R05. Same-sentence belief events share an observation key and timestamp

**REPRODUCED IN ISOLATION.** belief_reader.drive assigns each reality event chrono=float(sentence_index), then stores observation as observed[(agent, chrono)]. Two events in one sentence overwrite the same observation entry. timeline_belief and reality_at use max by chrono; tied events return the first matching value.

For ordered fixture moves of a box to kitchen then garden in sentence 0:

- Kitchen observed, garden unobserved: the second False overwrote the first True; belief became unavailable.
- Kitchen unobserved, garden observed: the final True made both events appear observed; belief returned kitchen.
- Reality returned kitchen in both cases, despite garden being the supplied second change.

**Fix:** assign each event a unique occurrence ID and a stable order within a sentence. Key observation by event identity, not a timestamp shared by multiple events. Preserve that identity for testimony and inferred updates too; the fixed +0.3 testimony offset is not a general event identifier.

**Acceptance:** two changes in one sentence preserve separate visibility and final value; tie ordering is explicit and deterministic; different facts/events cannot overwrite one another's observation flags.

**Source:** hdlab/belief_reader.py:422; hdlab/belief_timeline.py:134,143.

### R06. Later testimony makes an absent agent appear informed earlier

**REPRODUCED IN ISOLATION.** PerceptualAccessLedger._informed_after scans from the event through the rest of the passage. observed converts any later testimony into a Boolean observed flag for the original event. belief_reader.drive then attaches that flag to the event's original time.

Using the actual testimony-pattern lookup and ledger/driver control flow, with perception fixed to “Alice absent”:

| Passage | Marked observed at event 0 | Belief at time 0 |
|---|---:|---|
| Box moved to garden; no later testimony | False | unavailable |
| Same prefix, then Bob tells Alice at sentence 2 | True | garden |

The event's value and Alice's absence did not change. The later testimony was also supplied as its own later belief update, so the incorrect earlier knowledge is not necessary to support the later answer.

This is distinct from R04: it affects the epistemic timeline itself, not only goal evidence used for prediction. _epistemic_statement also searches a symmetric window around the event; its future-looking evidence should be reviewed under the same timing contract.

**Fix:** preserve when information was acquired. Direct perception can update belief at the event; testimony should update belief at the testimony event. If the ledger exposes “eventually informed,” keep it separate from “knew at time t.”

**Acceptance:** appending later testimony never changes an earlier belief answer; the later answer does update. Include deception, corrected testimony and explicitly retrospective statements.

**Source:** hdlab/perceptual_access_ledger.py:520,534,591; hdlab/belief_reader.py:422.

### O01. Full-passage parsing is multiplied by the number of belief events

**CALL COUNT REPRODUCED; runtime savings not benchmarked.** Each reality event in belief_reader.drive calls led.observed. Each observed call reparses the full passage through _parse_sents, which calls _parse_sent for every sentence. This repeats for each belief query.

A counting parser fixture with four sentences and three reality events recorded **12 sentence parses per query**, then **another 12** for a repeated query. This count excludes the driver's separate reality/assertion/inference extraction, so it is only the observation-ledger portion.

**Optimization:** parse once per document analysis and reuse that structure. Compute an agent's presence/perceptual timeline once, then answer event-observation questions from it. Cache fact-specific belief timelines with explicit document/configuration keys after fixing R05/R06.

**Acceptance:** the same fixture needs four parses to prepare the analysis and zero extra parses for its repeated observation queries. Preserve per-event evidence and time semantics. Measure latency and memory separately before claiming a speedup.

**Source:** hdlab/belief_reader.py:422; hdlab/perceptual_access_ledger.py:287,591.

### Recommended stopping point and next work

This is a complete bounded review of the selected contracts. **Stop further exploration and turn these cases into regression checks in the development session.** Suggested sequence:

1. Fix R01, R05 and R06 together around explicit event order and information-acquisition time.
2. Repair R02 and R03 around actor-scoped, argument-bearing goals.
3. Make time-limited query inputs prefix-invariant (R04).
4. Reuse the resulting document analysis to remove repeated parsing (O01).
5. After integration settles, run the small raw-text paired stories through the full reader and then the agreed end-to-end evaluation.

All findings include correct-upstream controls, but extraction failures may mask them in raw-text tests. Keep the isolated regression checks alongside end-to-end tests. Priorities 131/132 may overlap with parts of this work; reconcile with their implementation rather than creating competing edits.

**Scope limits:** no full-reader runs, model loads, corpus reads, package installation, training or benchmark runs occurred in this pass. There is no new overall capability score. Only this report was edited; other sessions' files/processes were not controlled. Exact source-inspection and probe programs, failures and outputs are in A11 below.

---


## Current-code deep review

**Review date:** 2026-09-15. **Method:** static control-flow, data-contract and lifetime review of the active source, without importing the substrate or running new model inference. D01-D08 below describe the inspected source hashes in the current-version manifest. They are separate from historical E01-E13.

### Current assessment

There is a substantial, inspectable implementation here. The reader builds explicit mentions, entities, events, locations and derived state, with separate components for reference, goals, belief, memory and causal/temporal questions. The new default pronoun discovery and feature-card path directly addresses the old input-boundary problem. The code also contains useful mechanisms for shared parsing, explicit abstentions, provenance and reuse.

**My main concern is consistency across these components.** Several downstream representations lose information that an upstream component already produced: entity identity, antecedent position, event occurrence and polarity. A locally correct answer can therefore become an incorrect world update or an ambiguous query result. This is a concrete integration problem, and the best next engineering investment is preserving those contracts through one document read.

This is not a new performance verdict. The active version has not been rerun, so this report does not establish its current accuracy, latency, memory use, generalization or improvement over the historical version. Nor does source inspection establish biological fidelity: component labels and mathematical witnesses are different evidence from a validated account of cognition.

### Acknowledged updates and verification boundary

| Earlier concern | What is visible now | Status in this review |
|---|---|---|
| Pronoun targets required gold-linked input mentions | Default discover_pronouns=True; targets come from discovered_pronoun_targets over predicted mentions | Structural change verified; historical E02 is not an active-version result |
| Predicted mentions lacked features needed by coreference | Default fill_card=True; new graded resolver consumes gender, number, role and history fields | Wiring/defaults verified; accuracy not rerun |
| Gold links could determine the inference question set | Default discovery separates _gold_alignment from predicted target construction | Separation visible; scoring issues in D06 are distinct |
| Reference records lacked a target token position | CorefResolution declares target_wpos; graded records populate it | Target location present; antecedent/entity identity remains an issue in D02/D05 |
| Space extraction had a separate mention input boundary | read() passes role_mentions into _read_space | Change verified; belief still receives empty mentions (D04) |
| Other earlier findings, including the board, backend validation and witness discovery | Owner reports these addressed | Owner-reported; not re-executed or exhaustively re-audited in this pass |

The improvements above matter. The new findings are not a request to redo the earlier fixes; they identify downstream obligations exposed by the changed interfaces.

### Active pipeline and the most important boundaries

The relevant order in SituationReader.read is:

1. Reset the reader cache and lexical document register; feed the passage and cache category outputs.
2. Discover mention spans/features and pronoun targets; cluster entities and resolve references.
3. Extract events; measure memory_roundtrip on this initial event representation.
4. Attach space/belief facilities, revise patients and apply the verb-subcategorization gate.
5. Build bound event memory and fold world state.
6. Build goals, affect and additional reasoning facilities; some query facilities initialize lazily.
7. Add event polarity and quantity metadata immediately before return.

A reader result consequently contains both snapshots computed at different stages and callbacks that may compute later. This is workable only if each consumer's input contract and revision policy are explicit.

| ID | Priority | Finding | Evidence |
|---|---|---|---|
| D01 | P1 | State, goal realization and bound event memory omit polarity | Confirmed source behavior; active semantic examples not executed |
| D02 | P1 | resolved_cluster=-1 is both a resolver sentinel and a valid live entity ID | Confirmed contract collision and incompatible consumers |
| D03 | P1 | Identical sentence text is used as identity despite context-dependent category state | Confirmed cache overwrite; prediction effect not measured |
| D04 | P1 | Belief queries receive empty mentions and use a separate extraction path | Confirmed wiring; end-to-end loss not measured |
| D05 | P1 | Graded reference resolution identifies entities by head string | Confirmed representational limitation |
| D06 | P1 | Graded coreference metrics lack an independent baseline and can misstate scoreability | Confirmed source behavior |
| D07 | P1 | Causal query graph merges distinct event occurrences by final word | Confirmed lossy normalization |
| D08 | P2 | Joint frontend repeats tagging on long inputs and incompletely clears its caches | Confirmed code paths; resource impact not measured |

### D01. Polarity does not reach state updates, goal realization or bound memory

**Evidence: CODE OBSERVATION. Confidence: high in the contract gap.**

read() invokes _read_polarity last. _read_world_state has already converted events to dictionaries containing only PRED, AGENT, PATIENT, ARG2 and OP. WorldState.apply_event reads preconditions and applies possession/open-close operations without checking whether the event is asserted, negated or unknown.

The same gap exists in goal realization. track_status and track_status_thwart reduce events to sentence, predicate and agent fields. A later matching predicate/agent can satisfy a goal regardless of event polarity; in the thwart-aware path, this matching branch returns before the thwart check.

Bound event memory also drops the distinction: BoundEventBackbone.build calls _norm_event with agent, patient, predicate and tense only. The final polarity field cannot distinguish positive and negative propositions in those stored attributes.

**Impact:** given otherwise identical extracted events, these consumers cannot distinguish “gave” from “did not give” using event polarity. A returned event can display negation while its derived state behaves as if the action happened. Reader comments acknowledge this as additive metadata; it nevertheless matters when consuming state or asking whether a goal happened.

**Proposed change:** finalize truth status before consumers that depend on occurrence, then carry it into their schemas. Define handling for asserted, negated and unknown propositions, and separately for desired, hypothetical or reported actions. Moving the existing pass earlier alone is insufficient because consumers currently discard the field.

**Acceptance cases, to run later:**

- Start with Alice owning a book; compare “Alice gave Bob the book” and “Alice did not give Bob the book.” Inspect event polarity, possession, preconditions and memory retrieval together.
- Compare “Alice wanted to leave. Alice left” with “Alice wanted to leave. Alice did not leave.” The latter must not satisfy the goal solely because the leave predicate exists.
- Unresolved polarity must not silently acquire the same status as an asserted action.
- Repeat with open/close actions and unknown/missing roles; record abstentions rather than claiming full comprehension from one clean pair.

**Source:** hdlab/situation_reader.py:2846,2916,3023,4951; hdlab/world_state_register.py:175; hdlab/goal_register.py:413,548; hdlab/bound_event_backbone.py:124,230.

### D02. The new reference output has an entity-ID collision

**Evidence: CODE OBSERVATION. Confidence: high.**

The graded _read_entities branch assigns resolved_cluster=-1 to every successful record and supplies the chosen resolved_head separately. Meanwhile, the reader converts online entity IDs to -(int(cluster) + 1). EntityResolver.cluster creates its first file with ID zero, making **-1 a valid first live entity ID**.

Two consumers interpret the output differently:

- goal_register.make_canonicalizer looks up names.get(r.resolved_cluster). A graded answer whose head names Bob can therefore map to the entity at -1, irrespective of its chosen head. If that cluster has no suitable name, canonicalization is omitted instead.
- _read_world_state, with densify_world_state=True by default, only forwards coreference clusters satisfying rc >= 0. This rejects the graded sentinel and would also reject legitimate negative online IDs.

One route can bind to the wrong entity; another loses the reference link and falls back to the binder's other behavior.

**Proposed change:** choose one predicted entity-ID contract, independent of gold IDs. Use None or an explicit unresolved result instead of a valid ID as sentinel. Return an antecedent occurrence and predicted entity ID, then update canonicalization, world state and other consumers together. Do not repair this with a special case that merely treats -1 as the first entity.

**Acceptance cases:**

- Resolve a pronoun to a later entity while a different first entity occupies online ID -1; verify canonical goal owner and possession holder agree with the selected identity.
- Test negative and nonnegative valid IDs, plus unresolved references. Validity must depend on membership/type, not sign.
- Use two pronouns with the same spelling in the same sentence but different antecedents; consumers should use occurrence positions, not just sentence and pronoun spelling.

**Source:** hdlab/situation_reader.py:1940,2946,4735; hdlab/entity_resolver.py:219; hdlab/goal_register.py:696,708,718.

### D03. Sentence caches conflate repeated occurrences with different context

**Evidence: CODE OBSERVATION. Confidence: high in the identity mismatch; prediction impact is conditional.**

The lexical category organ has document history. feed_passage advances that history while producing one posterior per sentence occurrence. The reader caches these outputs under tuple(sentence_tokens). If identical text appears twice, the later occurrence overwrites the earlier entry. _cached_tag and parse caches use the same text-only identity.

The lexical discourse register takes the opposite convention: commit records sent_key.setdefault(tuple(lows), t), retaining the **first** occurrence's time. A later begin(observe=False) without an explicit sentence index retrieves that first time.

A repeated sentence can therefore receive the last occurrence's cached posterior through the reader, while another lookup of its discourse timestamp points at the first occurrence. This does not prove the predictions differ on a particular passage; it proves the implementation cannot preserve them separately when they do.

**Proposed change:** carry document and sentence-occurrence IDs through posterior, tag and parse access. Store results by occurrence. A separate text-only cache is appropriate only for computations proven context-independent, with model/configuration included in its key.

**Acceptance cases:**

- Feed context A, sentence S, context B, sentence S. Both S occurrences retain their own forward-pass posterior and timestamp.
- Query the earlier S after completing the document; it must not read the later occurrence's cached result.
- Compare repeated reads and reordered independent documents under the intended history/reset policy.
- Count feed operations and cache hits by occurrence to catch hidden re-observation.

**Source:** hdlab/situation_reader.py:2336,2395,4598; hdlab/lexical_categories.py:339,358,748.

### D04. Belief queries do not receive the reader's discovered mentions

**Evidence: CODE OBSERVATION. Confidence: high.**

_read_belief constructs by_sent = {i: [] for i in range(len(sents))}. Both public query closures pass this empty mention map into belief_reader.drive.

extract_status_events includes a cluster-based subject match through _cluster_covering(noms, token_position), but noms is empty on this reader route. That branch cannot connect a pronoun to a tracked fact entity. Literal aliases can still match; callers can sometimes supply extra aliases, but that is not equivalent to consuming resolved mentions. Location-event extraction likewise matches a surface theme against supplied aliases.

Belief queries also run their own tag/parse extraction through space_reader._frontend, which loads PosTagger and ArcParser. The reader's category/posterior cache and extracted events are not passed through. Joint spatial/temporal parsing has another frontend/cache. These are concrete separate paths, so “the reader's own parse” does not mean one shared document analysis.

**Impact:** correct mention discovery in the main read need not benefit belief tracking. Event/state and belief answers may derive from different analyses, and each belief query repeats extraction. I have not established a current accuracy loss or a cross-document race at runtime.

**Proposed change:** pass a document-scoped analysis containing predicted mentions, entity IDs, parsed sentences and finalized events to belief extraction. Keep source/observation logic separate from text extraction. Project this analysis for fact-specific queries and record any genuinely additional inference.

**Acceptance cases:**

- Track a named object's status and then refer to it with a pronoun; query its belief timeline without adding that pronoun as a global alias.
- Include two same-gender/same-type entities so an alias list cannot substitute for reference resolution.
- Count parser calls during read and repeated belief queries; repeated queries should have a documented, bounded cost.
- Compare all answers from document A before and after reading B with the same reader, including lazy temporal/spatial/belief queries. This is a proposed independence check, not a reproduced state-leak finding.

**Source:** hdlab/situation_reader.py:2806,4066,4162; hdlab/belief_reader.py:107,158,422; hdlab/space_reader.py:222,287; hdlab/joint_relation_frontend.py:108,115.

### D05. Graded reference resolution collapses entities with the same head

**Evidence: CODE OBSERVATION. Confidence: high in the representational limitation.**

graded_pronoun_resolve keys history, latest sentence and feature cards by m['head'].lower(). It builds candidates from those head keys and returns resolved_head, with a target position but no antecedent position or entity ID.

Distinct doctors, people with the same name, or repeated common-noun heads therefore share one candidate history and feature record. Conversely, aliases of one entity can remain separate head candidates. The reader's online entity clustering is not the identity basis of this resolver.

There are useful follow-up checks around candidate legality. The function has a special reflexive/coargument restriction but does not apply a corresponding same-clause exclusion for ordinary non-reflexive pronouns; its number weight defaults to zero. These are observable choices, not evidence of a measured broad failure or a request to turn all cues into hard filters.

**Proposed change:** score predicted discourse entities while retaining the mentions that supply evidence. Return the entity, antecedent span, candidate set and relevant scores/abstention reason. Preserve graded evidence where useful; fix identity loss before tuning weights.

**Acceptance cases:**

- Two distinct “doctor” referents remain distinct through reference, goals and belief.
- A name and a valid descriptive alias resolve to the same identity without becoming two competing entities.
- Add controlled reflexive/non-reflexive and singular/plural cases, including ambiguity and abstention.
- Renaming one entity while preserving story structure does not merge or split unrelated entities.

**Source:** hdlab/coref.py:440; hdlab/situation_reader.py:1940.

### D06. Default graded coreference reporting mixes prediction and scoreability

**Evidence: CODE OBSERVATION. Confidence: high.**

Three reporting issues appear in the graded branch:

1. With no gold annotations, _gold_alignment is an empty dictionary structure rather than None. Graded records get correct=False because gc is absent. _coref_unscoreable is set only in the ungraded branch. On a fresh default reader with returned resolutions, coref_acc therefore reports zero instead of unavailable. Cross-sentence accuracy also lacks the unscoreable guard.
2. The branch returns (out, side, side), using the same correctness list for the main result and the supposed single-sentence comparator. single_sentence_xsent_acc is not an independently executed single-sentence baseline on this path.
3. _gold_alignment['head'] maps a head string to every gold cluster having that head anywhere in the document. Scoring checks whether the target's gold cluster occurs in that set. Without an antecedent position, a wrong same-head antecedent can receive credit because that head also occurs in the correct cluster elsewhere. This is scorer-side ambiguity, not demonstrated gold use in the graded decision itself.

The source comment recognizes the no-gold/zero-accuracy problem, but the assignment that handles it is below the graded early return.

**Proposed change:** use nullable scoring outcomes outside the inference result; reset scoreability per read; score antecedent span/entity alignment rather than whole-document head membership. Execute an independent comparator or omit its score and label availability.

**Acceptance cases:**

- Unannotated text yields predictions with accuracy unavailable; partially annotated text reports its scored subset explicitly.
- A deliberately wrong antecedent sharing the correct entity's head string is scored wrong.
- An independent single-sentence comparator can disagree with the discourse resolver on a designed cross-sentence case.
- Counts distinguish discovered pronouns, attempted resolutions, abstentions and scoreable examples. n_targets = len(resolutions) alone is not the total pronoun population.

**Source:** hdlab/situation_reader.py:253,1940,4744.

### D07. Causal queries lose event occurrence identity

**Evidence: CODE OBSERVATION. Confidence: high.**

_read_causal_reasoning normalizes every causal link endpoint and query argument to its rightmost lowercased word. It builds graph edges between those strings and drops links when the normalized endpoints are equal.

Different actors leaving, different purchases, or the same action occurring at two times therefore share one graph node when their normalized names match. A relation between distinct occurrences of the same action is dropped as a self-edge. Paths across otherwise separate events can be joined by the shared word.

This representation can answer questions about a graph of coarse event labels. It cannot distinguish arbitrary event occurrences in a narrative, even if upstream extraction retains sentence positions. Passing a more specific natural-language query does not help because the normalizer discards all but the final word.

**Proposed change:** build the narrative graph over stable event IDs tied to source spans. Keep verb/concept labels as searchable attributes. Resolve user-facing labels to one or more event IDs and expose ambiguity. The predictive-causal path's existing use of absolute event indices is a useful local precedent.

**Acceptance cases:**

- Independent chains containing the same verb do not acquire a connecting path.
- “Alice left because Bob left” retains two events and its causal edge when correctly extracted.
- A vague “leave” query with multiple matches returns ambiguity or explicit matches instead of merging them.
- Distinguish graph-based necessity from a stronger real-world causal claim in query provenance.

**Source:** hdlab/situation_reader.py::_read_causal_reasoning (line 3723), _read_predictive_causal.

### D08. Joint frontend cache and long-sentence behavior need bounded contracts

**Evidence: CODE OBSERVATION. Confidence: high in the code paths; operational impact unmeasured.**

For len(words) > 160, joint_relation_frontend.parse_sentence builds tags with a comprehension that calls t.tag(list(words)) once for every token. An n-token sentence causes n full-sentence tagging calls in this branch. The short-sentence branch tags once. Some reader callers skip long inputs before this function, so this is not a claim that every long reader input takes this path.

The module also retains process-global _parse_cache and _marg_cache entries keyed by sentence text. clear_cache() clears _parse_cache only; _marg_cache survives. No automatic size bound appears in this module, and no call to its clear_cache was found under hdlab in this pass.

**Proposed change:** tag once in the fallback, then define a shared bounded lifetime for parses and marginals. Clear both together, or place both in the document analysis. Document skipped/unsupported sentence lengths in results.

**Acceptance cases:**

- A counting tagger sees one call for a sentence just over the threshold.
- Clearing the cache empties both parse and marginal stores.
- A stream of distinct documents has bounded cache growth under the chosen policy.
- Long-sentence omission is visible as coverage loss, rather than a successful empty relation result.

**Source:** hdlab/joint_relation_frontend.py:55,115,801.

### Opportunities beyond individual fixes

These are recommendations for preserving and integrating existing capability, not new mechanism claims.

**1. A document analysis object as the common interface.** Give a read an ID, occurrence-indexed sentence analyses, predicted entity IDs, event IDs and source spans. Let components consume this object instead of reconstructing identities from words. This addresses D02-D05 and reduces disagreement between the main read and query-time extraction.

**2. Finalized propositions before stateful interpretation.** Separate extraction/revision from state folding. State, goals, memory and causal links should declare which truth status, modality and source they consume. Add an invalidation/version policy if later passes change facts already used by earlier consumers.

**3. Tests at the boundaries between existing components.** Prioritize paired cases: positive/negative action, two entities sharing a name, repeated sentence after new context, correct pronoun followed by a state update, and two causal events with the same verb. Test from input through affected outputs, with a component assertion to locate a failure. These complement the historical algebra and codec tests.

**4. Explicit evidence on the returned model.** Consistently expose prediction versus scoring status, abstention reasons, occurrence IDs, backend/asset provenance and incomplete-coverage markers. A caller should distinguish “no event found,” “unsupported input,” “unknown answer” and “known false.”

**5. Measure the completed representation.** memory_roundtrip is computed before patient revisions and the subcategorization gate; bound event tokens are computed later. Label that check's stage, or validate the final representation too. A successful earlier snapshot does not establish that final revised events round-trip through every memory API.

**6. Bounded query-time work and an explicit reuse policy.** Several facilities initialize lazily, and belief extraction repeats per query. Capture per-document configuration and analysis in the result. Establish whether a reader is single-use, reusable sequentially or safe for concurrent calls. This review did not test threads or establish a live service concurrency defect.

**7. Keep scientific and engineering evidence separate.** Retain can-fail representation controls, component diagnostics and provenance. Couple them to matched end-to-end outcomes for engineering decisions, while keeping brain-mechanism claims subject to their own evidence. Neither one metric nor a registry label substitutes for all those questions.

### Suggested work order and reviewable completion criteria

| Order | Work package | Done when |
|---|---|---|
| 1 | Predicted entity identity and scoring: D02, D05, D06 | No valid ID doubles as unresolved; antecedent position survives; no-gold accuracy is unavailable; comparator is independent |
| 2 | Truth status through state/goals/memory: D01 | Positive/negative stories remain different in every affected consumer |
| 3 | Document-scoped analysis and belief inputs: D03, D04 | Repeated occurrences retain context; belief receives resolved mentions; answers remain stable across reader reuse |
| 4 | Event identity in causal queries: D07 | Duplicate predicates no longer merge separate causal chains |
| 5 | Resource and coverage contracts: D08 | Fallback tags once; both caches have a bound/reset; omitted inputs are reported |
| 6 | End-to-end regression/evaluation | Run a fixed corpus and paired controls after concurrent changes settle; report eligible cases, uncertainty and provenance |

The packages overlap intentionally: one stable identity/analysis contract can solve several bugs together. They do not require replacing the underlying vector representation or importing an external comprehension model.

### Limits of this current-code pass

- Static review covers the central reader and selected reference, category, entity, world-state, goal, belief, memory and relation modules. It is not a line-by-line review of every repository file.
- No new runtime reproductions, benchmark runs, tests, corpus reads, training, package installation, asset writes or service launches were performed in this deep pass.
- Findings describe inspected working files, not a clean committed release. A multi-file read is not an atomic snapshot of an actively edited checkout.
- Failure frequency, full-story extraction behavior and latency/memory impact remain unmeasured on this revision. Acceptance examples above are proposed tests, not reported passes or failures.
- Performance percentages, witness results and timing later in this document are historical. The owner's reported fixes are not contradicted by retaining their original evidence.
- This pass does not establish production/security readiness, operational concurrency safety, corpus contamination status, or general conversational ability.
- The only persistent repository edit made by this evaluation is this report. No changes were committed or pushed, and no other session's processes or files were controlled.

---

## Historical runtime assessment

**Historical section:** the initial findings and measurements below predate the owner-reported fixes. They are retained for reproducibility, not presented as the active implementation's scorecard.


The project contains substantial implementations of inspectable event representations, reading components and experimental controls. The principal uncertainty is how much component capability survives the complete reading path. The current headline board does not directly answer that question: it assembles component evaluations rather than scoring the live reader's complete read of each document.

The strongest reproduced finding is a large, recoverable loss at the mention-input boundary. On the same five complete test documents (40 sentences, 623 tokens, 52 eligible agent questions):

| Executed path | Correct agent answers, all 52 questions counted |
|---|---:|
| Default reader, annotations removed | **9/52 (17.3%)** |
| Same default reader, unique mention spans supplied by its existing category organ | **42/52 (80.8%)** |
| Existing component scorer, its one skipped question counted as a miss | **44/52 (84.6%)** |

The predicted-mention control supplied **no gold categories and no correct coreference links**. It is an extra preprocessing pass, not an implemented fix or proof of broad generalization. Nevertheless, a 33-answer gain on the same questions is strong evidence that useful existing capability is being lost at an interface; a new reasoning architecture is not required to demonstrate this particular opportunity.

Separately, identical-text controls show that correct coreference linkage in the input determines whether the reader schedules a pronoun-resolution attempt. Invalid backend names silently select supervised alternatives; the aggregate mishandles missing comparator values; and the existing witness-discovery gate fails. These are actionable engineering/evidence defects alongside the broader research limitations.

My recommendation is to repair the annotation-free input and evaluation contracts first, recover the existing mention-dependent capability inside the reader, then use a fixed end-to-end instrument to decide which remaining parsing, reference and reasoning mechanisms need development. Preserve the inspectable representation and the existing can-fail mathematical controls.

## Historical runtime evaluation log

| Check | Status | Evidence / qualification |
|---|---|---|
| Repository and current architecture review | Completed | README, project state, live status, scorecard, board, reader, frontend, event codec and verification examples inspected. |
| Derived health report | Completed | 90 registered components: 8 BF, 76 BF_SPIRIT, 6 NOT_BF; one missing BF-update ledger entry; no owner-DONE integration backlog reported. |
| Default-reader annotation-free smoke | Completed | Correct thanking roles and literal state holder; no pronoun resolution. 21.75 seconds including 12.23 seconds of import in that fresh process. |
| Same-text annotation ablation | Completed | Canonical 12-column input: no annotations and unique mention IDs yield no pronoun resolution; linked IDs yield `she -> alice`; annotation-free repeat reproduces the initial output. |
| Five complete UD-EWT test documents | Completed | 40 sentences, 623 tokens. Verb detection 79/79; exact agent answers 9/52; exact patient answers 30/43; copular holder/property pairs 7/9. Scope and scoring caveats below. |
| Matched component scorer and additional sentence controls | Completed | Component agent scorer: 44 correct of 51 attempted / 52 eligible; reader: 9/52. Predicted unique mention spans recover the agent in two pronoun-subject controls. |
| Predicted-mention control on the same five documents | Completed | Agent 42/52; missing answers 1; pronoun agents 31/33. Unique IDs generated from predicted categories, no gold links. |
| Mathematical primitives | Completed | Four existing algebra property tests passed; event-codec reuse and round-trip/baseline self-tests passed. |
| BF registry checker | Completed | Standalone checker passed all 93 current entries and its positive control. The registry grew from 90 during evaluation, demonstrating concurrent updates. |
| Witness discovery gate | Completed, failure reproduced | Existing checker identifies 465 files without test functions/import-time asserts; 447 exceed its known-island allowlist. Its no-new-islands assertion fails. |
| Aggregate missing-baseline control | Completed, defect reproduced | Missing baseline/twin values are effectively counted as zero in their weighted averages. |
| Invalid-backend control | Completed, defect reproduced | Invalid source strings instantiate the perceptron/arc-eager alternatives. |
| Negation metadata control | Completed | `Alice did not thank Bob.` carries polarity -1 with provenance `direct_negator`. |
| Prioritized recommendations and final synthesis | Completed | Thirteen findings, explicit acceptance criteria, work order and exact execution appendix. |

## Historical findings

### E01. Headline scores do not measure the complete deployed reading path

**Priority: P0. Evidence: CODE OBSERVATION + RECORDED.**

`experiments/exp_situation_model_qa_modern_v1.py::run` calls separate coreference, salience, agent, patient, state and sense evaluation functions. Its seven headline dimensions are not scored from one shared `SituationReader.read` result. Existing problem priority 122 explicitly documents this and reports that a large improvement in name recognition through the reader left all seven rows unchanged.

The latest inspected trend entry, dated 2026-09-15 14:23:22 UTC, records an aggregate of 0.6204 against a baseline of 0.5268 over 11,361 items, with five of seven dimensions separated from the baseline under the existing tests. This is a cross-population component summary. It is **not** independently established end-to-end comprehension accuracy.

**Why it matters:** the board can miss both regressions and improvements in the real input stream, entity construction and event extraction. Optimizing it can favor improvements that never reach the deployed read.

**Recommended change:** score the output of one default reader invocation per document; isolate the answer key on the scorer side. Preserve component evaluations as diagnostics with explicit provenance. Publish new and old values on matched populations before retiring any historical interpretation.

**Acceptance criteria:** an intentional perturbation of the reader's event stream or case handling changes the corresponding score; no model answer is constructed by a second reader inside the scorer; all eligible gold questions remain in the denominator when the model misses an event, entity or answer.

**References:** `experiments/exp_situation_model_qa_modern_v1.py:2463`; `notes/BOARD_TREND.jsonl`; problem directory beginning `notes/problems/the_boards_seven_rows_never_run_the_reader_...` (priority 122).

### E02. Pronoun target construction depends on supplied mention annotations and cluster linkage

**Priority: P0. Evidence: REPRODUCED + CODE OBSERVATION.**

`SituationReader.read` obtains `coref_mentions` through `parse_litbank_conll`. That function creates mentions from brackets in the input coreference column. `build_pronoun_targets` schedules a pronoun only if there is an earlier mention bearing the same cluster ID. With a completely blank annotation column, the target list is empty.

**Reproduced example:** `Alice thanked Bob. She was happy.` supplied as cased tokens with sentence boundaries and no annotations.

- Events: `thanked(agent=alice, patient=bob)`; `happy(agent=?, patient=she)`.
- State binding: `She -> happy`.
- Entities: Alice and Bob, one mention each.
- Pronoun-resolution records: none.

The canonical-input ablation held tokens, casing and sentence boundaries constant:

| Input coreference column | Pronoun output | `happy` event agent |
|---|---|---|
| All `_` | No record | `?` |
| Alice `(0)`, Bob `(1)`, She `(2)` | No record | `she` |
| Alice `(0)`, Bob `(1)`, She `(0)` | `she -> alice` | `she` |
| All `_`, repeated after the controls | No record | `?` |

The linked condition does **not** prove the resolver simply echoes the annotated answer: the resolver may still choose independently once invoked. It proves that gold linkage controls whether the inference is invoked at all. Unique mention IDs also alter role availability, independently of supplying the correct linkage.

**Why it matters:** this interface does not independently discover and schedule pronoun questions from text. It can emit zero evaluated targets instead of recording a missed reference. Supplied coreference data also reaches the agent-candidate path through `_coref_mentions`; this is broader than scoring metadata alone.

**Recommended change:** separate inference-time mention discovery and antecedent retrieval from scorer-only gold alignment. Schedule eligible pronouns from the observed text, including cases with no suitable antecedent; emit explicit abstentions. Return source token positions for target and predicted antecedent.

**Acceptance criteria:** removing, changing or permuting gold cluster IDs cannot affect model predictions or the set of attempted text-derived queries. Gold influences correctness only. A zero-answer reader scores zero recall on a nonempty fixed question set.

**References:** `hdlab/coref.py::parse_litbank_conll`, `build_pronoun_targets`; `hdlab/situation_reader.py::read`, `_cm_agent_candidates`.

### E03. Evaluation populations and missing-answer conventions can conceal failures

**Priority: P0. Evidence: CODE OBSERVATION.**

The WiC live-wire experiment scores only pairs for which both sense calls commit. Coverage is recorded, but the reported accuracy applies to that covered subset. Other role evaluations skip items when their candidate set is empty. These conditional measurements are useful for component diagnosis but should not be presented as full-input success rates.

**Recommended change:** report total eligible items, answered items, correct items, coverage, accuracy over all eligible items, and conditional accuracy over answered items. Keep model failures in the fixed end-to-end denominator. Distinguish missing assets or execution errors from ordinary model abstention.

**Acceptance criteria:** the empty-output control loses; dropping hard items cannot improve the primary end-to-end metric; every reported percentage has its population and count beside it.

**References:** `experiments/exp_sense_wire_wic_liveness_v1.py::run`; `experiments/exp_board_agent_slot_ud_v1.py::_eval`.

### E04. Reader composition and configuration are difficult to audit

**Priority: P1. Evidence: CODE OBSERVATION + RECORDED.**

The central reader contains over 5,000 nonblank lines, many capability flags and numerous downstream integrations. The project records earlier mismatched frontend defaults, repeated reads changing document-local state, and capitalization loss. The shared frontend and per-read caches are useful repairs, but comments, switches and implementation history remain interwoven.

**Recommended change:** first stabilize observable contracts: explicit input provenance, resolved configuration, source token identities, per-stage output counts and explicit unavailable-stage diagnostics. Then extract cohesive stages behind these contracts, preserving behavior with meaningful invariants. A rewrite would obscure which behavior is changing.

**Acceptance criteria:** one configuration manifest identifies the actual tagger, parser and assets; each document advances online state once in order; repeated reads and fresh-reader reads satisfy declared reproducibility expectations; every final answer is traceable to the input and intermediate model state.

### E05. Biological status labels and mathematical verification establish different things

**Priority: P1 for claim clarity. Evidence: REPRODUCED registry counts + CODE OBSERVATION.**

The health report distinguishes BF, BF_SPIRIT and NOT_BF. Its label-presence gate is useful bookkeeping, but does not independently establish biological validity, runtime reachability or task competence. The import enumeration in the health tool is a static scan of direct imports in the reader, including imports inside functions; it is not a complete executed transitive dependency trace.

**Recommended change:** present three separate evidence tracks: mathematical/implementation correctness, justification of the biological model, and behavior of the assembled reader. Record active versus selectable diagnostic components separately.

**Acceptance criteria:** a passing tag-coverage check is never described as proof that every executed component is biologically validated; each biological claim links to its supporting model and the specific implementation it justifies.

### E06. Current health and human-facing summaries disagree

**Priority: P2. Evidence: REPRODUCED + RECORDED.**

The health tool reported aggregate 0.6185 from a canonical metrics file, while the latest inspected trend entry reports 0.6204. `HOW_WE_ARE_DOING.md` includes a 47-in-100 pronoun headline alongside later corrections to about 42-in-100 and stale running-work descriptions. These values may refer to different revisions and populations; their coexistence makes status easy to misread.

The health report also fails one bookkeeping gate: submission slug `the_mention_typer_reads_a_three_va` is missing from `BF_COMPONENT_UPDATE_LEDGER` in the inspected state. This is a ledger inconsistency, not a demonstrated reader failure.

**Recommended change:** generate status numbers from one versioned run manifest, with run identity, timestamp, population and source path displayed. Keep authored interpretation separate from generated facts.

### E07. Agent assignment loses substantial capability on annotation-free input

**Priority: P0. Evidence: REPRODUCED on a small sample, including matched component comparison.**

Five complete UD-EWT test documents, in original file order, yielded the following:

| Measurement | Count | Rate | Interpretation |
|---|---:|---:|---|
| Gold VERB tokens matched to emitted events | 79/79 | 100.0% | Correct sentence and predicate index, with surface/lemma identity check. This is recall, not precision. |
| Exact agent head | 9/52 | 17.3% | All eligible questions counted; 15 missing answers and 28 wrong nonempty answers. |
| Exact patient head | 30/43 | 69.8% | All eligible questions counted; no missing answers in this sample. |
| Exact copular holder/property pair | 7/9 | 77.8% | ADJ/NOUN/PROPN complements with a copula and referential subject; tiny denominator. |

There were 97 emitted events. The additional 18 are **not automatically false positives**: the reader also represents nonverbal predications and other events outside the gold-VERB recall definition. Event precision was not computed.

Concrete misses:

| Text / predicate | Question | Gold surface head | Reader answer |
|---|---|---|---|
| `What if Google Morphed Into GoogleOS ?` / Morphed | Agent | Google | morphed |
| `They own blogger , of course .` / own | Agent | They | `?` |
| `I 'm staying away from the stock .` / staying | Agent | I | `?` |
| `Does anybody use it for anything else ?` / use | Agent | anybody | `?` |
| `... Google's rush toward ubiquity might backfire ...` / backfire | Agent | rush | ubiquity |

The source provides a concrete candidate mechanism for part of this loss: `referent_per_np.py` excludes PRON from content-head discovery and preserves pronouns from the annotated coreference stream. With that stream blank, pronoun role candidates are absent. `_cm_agent_candidates` also returns no candidates when `_coref_mentions` is empty. These are input-path issues beyond parser accuracy.

**Matched component result:** the existing agent component evaluator on exactly these first 40 test sentences found the same 52 eligible agent questions, scored 51, and answered 44 correctly. Its published-style conditional result would be 44/51 = 86.3%; treating its one skipped item as a miss gives 44/52 = 84.6%. The annotation-free reader answered 9/52 = 17.3%. The positional component baseline also got 44 right, the full competition 39, and the shuffled-support control 12. All scored items in this particular sample were active-voice cases. Of the 52 eligible gold agents, 33 were pronouns.

Thus the difference is not merely an unmatched full-board-versus-small-sample comparison. It is a **35-answer gap on the same 52-question population** between two executed paths. It still does not isolate one cause: the component path, candidate stream, document-state handling and scorer invocation differ.

**Gold-free local intervention, without code edits:** supplying unique mention IDs for nominal/pronoun tokens selected by the existing tagger changed `They own Blogger.` from agent `?` to `they`, and `She thanked Bob.` from agent `?` to `she`. No correct coreference links or gold categories were supplied. This establishes an input/candidate-availability opportunity; it is a diagnostic preprocessing control, not a landed reader repair.

**Five-document intervention:** predicting nominal/pronoun mentions with the existing category organ's in-order `feed_passage`, encoding each as its own unique ID, and supplying that temporary input to the unchanged default reader yielded **42/52 correct agents**, versus the annotation-free 9/52. Missing answers fell from 15 to 1. On the 33 gold-pronoun agent questions, this intervention answered 31 correctly. Per-document correct counts were 2/2, 4/6, 7/11, 10/11 and 19/22. The extra pass supplies predicted spans but no true links; the effect can involve several mention-dependent consumers, so it is not evidence that simply appending pronouns at one site will recover every gain. Patient/state changes and speed tradeoffs under this intervention were not scored.

**Positive controls:** annotation-free `Alice thanked Bob.` and `Bob was thanked by Alice.` both emitted `thanked(agent=alice, patient=bob)`. `The sky is blue.` produced state `sky -> blue`. These show that the reader can handle these simple active/passive and property-binding cases; the agent failure is not universal.

**Recommended change:** make predicted mention discovery include pronouns and feed the same discovered stream to all relevant role/reference consumers. This must be part of the reader's own inference path, not an evaluator repair. First quantify how much of the loss this restores with matched, annotation-invariant tests.

**Scope warning:** this sample is five adjacent weblog documents, not a representative random sample. Exact surface-head scoring is a narrow structural proxy, not semantic equivalence. The 17.3% is **not a replacement overall capability claim** and cannot be directly subtracted from the full-population board score.

### E08. Many standalone verification scripts are invisible to ordinary pytest collection

**Priority: P1. Evidence: REPRODUCED with the project's own checker.**

Running pytest on `test_algebra.py` and `test_bf_status_tags.py` reported **four tests passed**: the four algebra tests. The BF checker exposes `main()` rather than pytest test functions, so its checks did not run in that invocation. Running the BF file directly subsequently passed.

The existing `test_no_witness_is_islanded_from_the_gate.py` checker reports 465 currently islanded files and 447 beyond its explicit allowlist. Its `test_no_new_witness_is_islanded` assertion fails. Its baseline-maintenance assertion passes. A separate static count found 622 `test_*.py` files, only 153 with top-level pytest-style test functions/classes, and 429 with a `main()` but no such test definition. These counts have different definitions and must not be conflated.

The existing subprocess wrapper `test_all_witnesses_exit_clean.py` discovers `verify_*.py` and `witness_*.py`; it does not automatically solve the `test_*.py`-with-main-only case. Some other files may be invoked by dedicated hooks or commands; the checker count does not prove they have never been run.

**Recommended change:** inventory intended checks against actual collected/executed checks. Add pytest wrappers or an explicit bounded standalone runner, with fast and corpus-dependent suites separated. Preserve the failing discovery gate rather than expanding its allowlist to hide the problem.

**Acceptance criteria:** each required witness appears in an execution manifest; modifying its assertion to fail is detected by the intended gate; test counts cannot imply execution of main-only scripts.

### E09. Missing comparison metrics are silently treated as zero by the aggregate

**Priority: P1 for metric correctness; actual published-score impact unestablished. Evidence: REPRODUCED synthetic edge case.**

The current `_agg` implementation uses the total item count of rows with a model score as the denominator for every metric. It omits missing baseline/twin values from the numerator but not the denominator.

An exact extraction and execution of the existing function with two equal-size rows produced:

- Row A: n=100, model=0.6, baseline=0.5, twin=0.1.
- Row B: n=100, model=0.6, baseline=None, twin=None.
- Result: model=0.6, baseline=0.25, twin=0.05.

This is not a matched comparison. On the available baseline population the baseline is 0.5; on the full population it is unknown. Reporting 0.25 overstates evidence against the baseline.

**Recommended change:** reject incomplete required comparisons or aggregate paired model/baseline values over the same explicitly reported subset. Keep coverage and missing-comparison counts visible.

**Acceptance criteria:** missing values remain missing; a model/comparator aggregate always names an identical eligible population; a synthetic missing-row control cannot artificially increase the reported advantage.

### E10. Invalid backend names silently select different implementations

**Priority: P1. Evidence: REPRODUCED.**

Constructing `frontend.Tagger(source='evaluation_invalid_source')` succeeded and selected the perceptron implementation. Constructing `frontend.Parser(source='evaluation_invalid_source')` succeeded and selected arc-eager. Both constructors branch on the preferred value and treat everything else as the alternative; they do not validate an explicit allowed set.

**Why it matters:** a typo can silently change the implementation under evaluation and invalidate claims about which architectural restrictions a run satisfied. This is a concrete configuration bug, not merely a documentation issue.

**Recommended change:** validate source values at the frontend boundary and raise a descriptive error for unknown names. Include resolved implementation class and source/asset hash in every benchmark manifest.

**Acceptance criteria:** invalid explicit or environment-supplied source names fail before inference; valid diagnostic alternatives remain explicitly selectable and accurately reported.

### E11. Source identity and unavailable-stage reporting need stronger contracts

**Priority: P1. Evidence: CODE OBSERVATION; runtime consequences beyond the examples above not fully characterized.**

- The reader has 17 broad `except Exception` handlers in the inspected source. Some intentionally degrade optional capabilities. Without structured diagnostics, missing assets, coding errors and ordinary model abstention can look alike.
- `_router_roles` returns an empty mapping for sentences longer than 120 tokens. This is a capability/performance boundary that should be visible in results rather than silently folded into answer quality.
- The reader documents that event-extractor token indices can differ from input token indices and computes an alignment `vp`, but the inspected wired event constructor stores `pred_idx=e.idx`. The five-document probe required a surface/lemma check and all 79 gold verbs aligned there; this does not prove stable alignment on contractions, punctuation, repeated predicates or alternative tokenizations.
- `CorefResolution` exposes a sentence index and pronoun string, but no target token position. Multiple identical pronouns in a sentence are difficult to align unambiguously from the public output alone. Common-noun resolution records expose internal mention/reference IDs without a complete public source-span mapping.

**Recommended change:** carry stable document/sentence/token/span identities through the output model; expose stage status (`ran`, `disabled`, `unsupported_input`, `asset_missing`, `failed`) and error details. Keep permissive degradation only where it is explicit and observable.

**Acceptance criteria:** an evaluator can align every answer without importing private reader internals or rerunning a parser; long-sentence skips and missing assets are counted separately; deliberate stage exceptions appear in diagnostics rather than silently becoming empty outputs.

### E12. Installation and evidence replay depend on more than the declared package

**Priority: P2. Evidence: CODE OBSERVATION; clean-machine installation not attempted.**

The README describes an editable install and original hyperdimensional instrument. The active project is now a much larger reading system with frozen assets, corpora, source-checkout paths and additional dependencies. For example, `underspecified_sense_reader.py` imports `nltk.corpus`, but `nltk` is not declared in the inspected `pyproject.toml` dependency lists. This environment has NLTK installed and the probe runs, so this is an undeclared dependency/replay risk, not a demonstrated failure in the current environment.

The wheel configuration includes `hdlab` and `reference`; it does not by itself describe how to obtain and validate the reading assets or reproduce the research environment. Broad lower-bound dependency specifications do not pin the observed package versions.

**Recommended change:** document the actual reader entry point, minimum asset set, expected asset hashes, optional capabilities, and a reproducible environment specification. Add a bounded fresh-install/read smoke that reports unavailable assets explicitly. Keep research corpora separate from runtime requirements.

**Acceptance criteria:** a new checkout can reproduce a named small read from documented inputs and assets; an incomplete installation identifies what is missing; reported benchmark manifests identify their dependency and asset versions.

### E13. Research reuse of evaluation data limits generalization claims

**Priority: P1 for future capability claims. Evidence: CODE OBSERVATION + RECORDED; training-data contamination not established.**

The WiC experiment combines development and test pairs, and existing notes repeatedly use the board to choose integrations and thresholds. This provides useful engineering feedback but does not establish performance on a newly sealed population. The diagnostic sample in this report also comes from the project's already-used test corpus.

**Recommended change:** reserve a new document-level holdout after the inference/scoring contracts are fixed. Keep it separate from design and threshold selection, audit overlap with acquisition assets, and state the unit of uncertainty (document rather than treating every within-document answer as independent). Report per-dimension results and coverage before any cross-population summary.

**Acceptance criteria:** a predeclared sampling/splitting rule, overlap report, fixed scorer and fixed configuration exist before the held-out answers are examined. Do not interpret repeated use of the existing test set as independent replication.

## What passed and should be preserved

- Four algebra property tests passed: FHRR bind/unbind inverse, HRR approximate inverse, FHRR commutativity and HRR commutativity. They exercise multiple generated dimensions/seeds under the existing Hypothesis decorators.
- Event-codec self-tests passed both byte-level reuse of role-slot primitives and round-trip checks against information-degraded thin-label and bag-of-arguments baselines. This supports the tested storage mechanism, not language understanding by itself.
- The standalone BF registry checker passed its missing/mismatched/out-of-vocabulary positive control and all 93 then-current registry entries.
- Simple active/passive role binding and copular state binding succeeded in annotation-free controls.
- The negated sentence `Alice did not thank Bob.` emitted polarity `-1` and provenance `direct_negator`; its positive-looking agent/patient tuple must not be mistaken for a failure to represent negation.
- Repeating the annotation-free Alice/Bob passage after the annotated controls reproduced its recorded events, entities, coreference and state outputs. This is one within-process reproducibility witness, not a complete order-invariance audit.

## Proposed work sequence

| Order | Work item | Why first / dependency | Completion evidence |
|---|---|---|---|
| 1 | Establish the annotation-free input/output and scorer contract (E01-E03, E11) | Without it, the score cannot identify the reader's actual limitations. | Predictions invariant to gold annotations; fixed denominators; one read per document; source positions in output. |
| 2 | Repair discovered mention supply and pronoun scheduling in the reader (E02, E07) | Runtime evidence identifies reachable existing capability that is lost at the input boundary. | Matched gains on pronoun-subject and reference questions without annotation assistance, with non-pronoun/passive controls preserved. |
| 3 | Reject invalid backend settings and fix aggregate missing-data handling (E09-E10) | Small, well-localized defects that undermine experiment identity and metric honesty. | Invalid-source negative tests and missing-baseline controls fail safely. |
| 4 | Restore executed coverage of required standalone witnesses (E08) | A green command should mean the intended checks actually ran. | Bounded execution manifest, collected/standalone coverage reconciliation, discovery gate passing without hiding failures. |
| 5 | Publish one versioned status and reproducible reader environment (E06, E12) | Prevents stale numbers and environmental drift from consuming research time. | Every headline links to one manifest and replay instructions. |
| 6 | Measure remaining parsing/reference/reasoning limits on a sealed sample (E05, E13) | Only after input and measurement defects are separated from actual model limits. | Fixed holdout, overlap audit, per-stage and per-dimension error analysis. |

Do not infer from this sequence that broader reasoning research must stop. The narrow recommendation is to resolve the demonstrated measurement and input-path defects before using the headline board to decide which mechanism needs replacing.

## Opportunities already supported by the architecture

1. **Traceable failure localization:** event records, explicit state bindings and role memory make it possible to locate whether a failure arose in extraction, assignment, reference resolution or reasoning. Make this the primary evaluation advantage.
2. **Matched component-to-reader comparisons:** run existing component arms and the assembled reader on exactly the same document/question set to quantify integration loss.
3. **Coverage-aware behavior:** existing abstention/confidence machinery can support useful reliability reporting once full-input coverage is made explicit.
4. **Annotation invariance as a regression contract:** the same text with removed or randomized annotation columns is a powerful test for accidental assistance.
5. **Reproducible configuration and asset manifests:** frozen-asset hashes and resolved flags can turn experiment histories into replayable evidence.

## Limits of this evaluation

- The new runtime checks are diagnostic probes, not a new validated benchmark or a full population rerun. They used five adjacent weblog documents; no uncertainty interval or independent replication seed is claimed.
- The UD sample uses an existing test corpus repeatedly used during the project's development; it is not a newly sealed holdout. Training-asset overlap has not yet been audited.
- Supplied token and sentence boundaries mean tokenization and sentence segmentation are not evaluated by those probes.
- Exact surface-head comparisons do not constitute complete semantic equivalence or coreference scoring.
- A biological literature review and independent scientific validation are outside the checks performed so far.
- No proposed fixes have been implemented.
- No complete runtime network-access audit, fresh-install test, missing-asset sweep, adversarial long-context evaluation, persistence/concurrency stress test or full reasoning-dimension benchmark was performed. The report does not certify these areas.
- The five-document scoring code is fully disclosed but has not been independently validated as a general-purpose benchmark. It measures exact heads on selected structural questions and does not measure free-form answer quality, entity-level semantic equivalence, hallucination rate or end-to-end event precision.
- The predicted-mention intervention was run in a later fresh process and adds a preprocessing pass; the reader source hash was unchanged, but dependency/asset/global-state equality was not exhaustively certified. The earlier within-process annotation ablation supplies a separate direct witness of annotation dependence.

## Execution appendix: exactly what ran

This appendix records the substantive executable checks, including the inline evaluation/scoring code. File navigation (`Get-Content`, `rg`, directory listings) was read-only; it is represented by the source references above rather than a transcript of every navigation command. No full-board run, full certification run, model training, parameter optimization, package installation or biological literature validation was performed.

### A0. Environment, repository state and run inventory

- Shell/cwd: PowerShell, `C:/AI`.
- Interpreter for probes/tests: `C:/AI/hd-instrument/.venv/Scripts/python.exe`, Python 3.12.10, 64-bit Windows.
- Packages observed: torch 2.12.0 (earlier torch version print included `+cpu`), numpy 2.4.5, scipy 1.17.1, nltk 3.9.4, pytest 9.0.3, hypothesis 6.152.7.
- Reader defaults printed at runtime: `HDLAB_HEADS_SOURCE=attachment_arm`, `HDLAB_TAG_SOURCE=counts`.
- Inference probe programs set `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS` to `1`. Paired/sample programs launched with `PYTHONHASHSEED=0`; the first isolated smoke did not explicitly fix that variable.
- Python `-B` disabled bytecode writes for the substantive probes. Pytest cache provider and Hypothesis example database were disabled for the focused tests.
- No new evaluation result file was written under `data/`. Results were printed to tool output and transcribed into this report. Existing imported modules may emit their own initialization messages; those messages are not additional benchmark runs.

Relevant commands executed directly:

```powershell
git -C C:\AI\hd-instrument status --short --untracked-files=no
git -C C:\AI\hd-instrument log -3 --oneline
python C:\AI\hd-instrument\tools\substrate_health.py --gaps
python C:\AI\hd-instrument\tools\substrate_health.py
& C:\AI\hd-instrument\.venv\Scripts\python.exe -c 'import sys, torch, pytest; print(sys.version); print(torch.__version__)'
& C:\AI\hd-instrument\.venv\Scripts\python.exe -B C:\AI\hd-instrument\verification\test_bf_status_tags.py | Select-Object -Last 8
```

The inline Python blocks below were passed directly to the interpreter through a PowerShell single-quoted here-string, not saved as repository scripts. For example, A2 was the contents of `$evaluationCode`, followed by:

```powershell
$env:PYTHONHASHSEED = '0'
& C:\AI\hd-instrument\.venv\Scripts\python.exe -B -u -c $evaluationCode
```

**Failed attempt disclosed:** A1 initially failed when the sandbox denied creation of its temporary `text_only.conll` input in the Windows temporary directory. The traceback also showed failed cleanup of that temporary directory. No model read occurred in that attempt. The evaluation was rerun with approval outside the sandbox and succeeded. The successful A1 program below adds `Path` import and a resolved-parent assertion before temporary cleanup; the failed program otherwise had the same input and read/print logic. Subsequent temporary-input probes also ran outside the sandbox with approval. This was an environment permission failure, not a reader defect.

**Source hashes recorded after the first sample and before the matched comparison:**

| File | SHA-256 |
|---|---|
| `hdlab/situation_reader.py` | `62ee788a9c4857752c9798bd6af373b5acb88579f70465cfa69977840c52aa14` |
| `hdlab/frontend.py` | `b608ad2e8a9ca8bdf5575defd2e6e7032ff2067f2dbc1d6d3b6e67179c3fecc4` |
| `hdlab/coref.py` | `5c49f245d9f6758d748a513ab7ece994ab6bff6fd3ad639c4a7a24b8a3b6563c` |
| `hdlab/referent_per_np.py` | `8514743e211f971c4143edeed3938a7e1a806f8bbfbc3cc61c58a5a87a7000ba` |
| `experiments/exp_situation_model_qa_modern_v1.py` | `94a115ce6a78d138c8ba15759b1519814b88fcea932d1bca44b5ca01b21f5dfb` |

The reader hash was printed again by the matched-comparison program and the environment probe and was unchanged. This does not establish that all dependencies/assets remained unchanged; they were not fully snapshotted or hashed.

### A1. Initial annotation-free smoke

PowerShell variable: `$probeCode`; invocation: `& C:\AI\hd-instrument\.venv\Scripts\python.exe -B -u -c $probeCode`.

```python
import os, sys, tempfile, time, json
from pathlib import Path
sys.path.insert(0, r'C:\AI\hd-instrument')
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
start = time.perf_counter()
print('Importing live reader', flush=True)
from hdlab.situation_reader import SituationReader
print('Imported in', round(time.perf_counter() - start, 2), 'seconds', flush=True)
sentences = [['Alice', 'thanked', 'Bob', '.'], ['She', 'was', 'happy', '.']]
with tempfile.TemporaryDirectory(prefix='substrate_eval_') as directory:
    assert Path(directory).resolve().parent == Path(tempfile.gettempdir()).resolve()
    path = os.path.join(directory, 'text_only.conll')
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        for sentence in sentences:
            for i, token in enumerate(sentence):
                handle.write('\t'.join(['document', '0', str(i), token, '_']) + '\n')
            handle.write('\n')
    reader = SituationReader()
    print('Reader constructed; reading text-only passage', flush=True)
    model = reader.read(path)
    result = {'input': 'Alice thanked Bob. She was happy.', 'input_annotations': 'none; supplied token and sentence boundaries only', 'n_sentences': model.n_sentences,
              'events': [{'sentence': e.sent_idx, 'predicate': e.predicate, 'agent': e.agent, 'patient': e.patient, 'predicate_index': e.pred_idx} for e in model.events],
              'entities': [{'heads': e.heads, 'count': e.n_mentions} for e in model.entities],
              'coref': [{'pronoun': r.pronoun, 'sentence': r.sent_idx, 'resolved_head': r.resolved_head} for r in model.coref_resolutions],
              'states': [{'sentence': s.sent_idx, 'holder': s.holder, 'property': s.property} for s in model.entity_states],
              'common_noun_resolutions': model.commonnoun_resolution,
              'seconds': round(time.perf_counter() - start, 2)}
    print('RESULT ' + json.dumps(result), flush=True)
```

The five-column transport accepted by the relevant loaders was used only in this first smoke. A2 independently repeated the observation using the repository's canonical 12-column `_write_temp_conll` helper, removing a potential input-format confound.

### A2. Canonical annotation ablation and five-document UD evaluation

PowerShell variable: `$evaluationCode`; launched with `PYTHONHASHSEED=0`, `python.exe -B -u -c $evaluationCode`.

```python
import os, sys, json, time, tempfile
from pathlib import Path
sys.path.insert(0, r'C:\AI\hd-instrument')
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
os.environ['PYTHONHASHSEED'] = '0'
from hdlab.situation_reader import SituationReader, _write_temp_conll
from hdlab.frontend import HEADS_SOURCE, TAG_SOURCE
print('CONFIG ' + json.dumps({'heads': HEADS_SOURCE, 'tags': TAG_SOURCE}), flush=True)
def execute(sentences, annotations=None):
    rows = [(si, wi, token, (annotations or {}).get((si, wi), '_')) for si, sent in enumerate(sentences) for wi, token in enumerate(sent)]
    path = _write_temp_conll(rows)
    assert Path(path).resolve().parent == Path(tempfile.gettempdir()).resolve()
    try:
        reader = SituationReader()
        start = time.perf_counter()
        model = reader.read(path)
        return model, round(time.perf_counter() - start, 3)
    finally:
        os.unlink(path)
def brief(model):
    return {'events': [(e.sent_idx, e.predicate, e.agent, e.patient) for e in model.events],
            'coref': [(r.pronoun, r.resolved_head) for r in model.coref_resolutions],
            'states': [(s.sent_idx, s.holder, s.property) for s in model.entity_states],
            'entities': [(e.heads, e.n_mentions) for e in model.entities]}
sents = [['Alice', 'thanked', 'Bob', '.'], ['She', 'was', 'happy', '.']]
for label, annotation in [('text_only', {}), ('mention_spans_unique_ids', {(0,0): '(0)', (0,2): '(1)', (1,0): '(2)'}), ('linked_annotations', {(0,0): '(0)', (0,2): '(1)', (1,0): '(0)'}), ('text_only_repeat', {})]:
    model, elapsed = execute(sents, annotation)
    print('CONTROL ' + json.dumps({'mode': label, 'seconds': elapsed, **brief(model)}), flush=True)
# Read the first five COMPLETE documents of the official UD-EWT test file, in source order.
# Only FORM + token/sentence boundaries cross the reader input boundary.
source = Path(r'C:\AI\hd-instrument\data\corpora\ud_english_ewt\en_ewt-ud-test.conllu')
docs, current, sent, docid = [], [], [], None
for line in source.read_text(encoding='utf-8').splitlines():
    if line.startswith('# newdoc id = '):
        if sent:
            current.append(sent); sent = []
        if current:
            docs.append((docid, current)); current = []
        docid = line.split(' = ', 1)[1]
    elif not line.strip():
        if sent:
            current.append(sent); sent = []
    elif not line.startswith('#'):
        c = line.split('\t')
        if c[0].isdigit():
            sent.append({'id': int(c[0]), 'form': c[1], 'lemma': c[2], 'upos': c[3], 'head': int(c[6]), 'dep': c[7]})
if sent:
    current.append(sent)
if current:
    docs.append((docid, current))
print('POPULATION ' + json.dumps({'total_docs': len(docs), 'selected': [(d, len(s)) for d,s in docs[:5]], 'claim': 'diagnostic convenience sample; test corpus previously used by project, not a fresh blind holdout'}), flush=True)
total = {'sentences': 0, 'tokens': 0, 'gold_verbs': 0, 'verbs_detected': 0, 'emitted_events': 0, 'agent_n': 0, 'agent_correct': 0, 'agent_missing': 0, 'patient_n': 0, 'patient_correct': 0, 'patient_missing': 0, 'state_n': 0, 'state_correct': 0, 'state_missing': 0}
examples = []
for docid, gold_sents in docs[:5]:
    text_sents = [[t['form'] for t in s] for s in gold_sents]
    model, elapsed = execute(text_sents)
    stats = {key: 0 for key in total}
    stats['sentences'] = len(gold_sents)
    stats['tokens'] = sum(map(len, gold_sents))
    stats['emitted_events'] = len(model.events)
    for si, sentence in enumerate(gold_sents):
        for verb in sentence:
            if verb['upos'] != 'VERB':
                continue
            stats['gold_verbs'] += 1
            # Match output events to the supplied token position, with a surface/lemma check.
            found = [e for e in model.events if e.sent_idx == si and e.pred_idx == verb['id'] - 1 and e.predicate.lower() in (verb['form'].lower(), verb['lemma'].lower())]
            event = found[0] if len(found) == 1 else None
            stats['verbs_detected'] += int(event is not None)
            children = [t for t in sentence if t['head'] == verb['id']]
            passive = any(t['dep'].startswith(('nsubj:pass', 'aux:pass')) for t in children)
            agents = [t for t in children if t['dep'].split(':')[0] == 'nsubj' and not t['dep'].startswith('nsubj:pass')] if not passive else [t for t in children if t['dep'].startswith('obl') and any(c['head'] == t['id'] and c['dep'] == 'case' and c['form'].lower() == 'by' for c in sentence)]
            patients = [t for t in children if t['dep'] == 'obj'] if not passive else [t for t in children if t['dep'].startswith('nsubj:pass')]
            for role, targets in [('agent', agents), ('patient', patients)]:
                if not targets:
                    continue
                stats[role + '_n'] += 1
                answer = getattr(event, role, None) if event else None
                ok = answer is not None and answer.lower() in {t['form'].lower() for t in targets}
                stats[role + '_correct'] += int(ok)
                stats[role + '_missing'] += int(answer in (None, '', '?'))
                if not ok and len(examples) < 8:
                    examples.append({'text': ' '.join(text_sents[si]), 'predicate': verb['form'], 'role': role, 'gold': [t['form'] for t in targets], 'answer': answer})
        for pred in sentence:
            children = [t for t in sentence if t['head'] == pred['id']]
            if pred['upos'] not in ('ADJ', 'NOUN', 'PROPN') or not any(t['dep'] == 'cop' for t in children):
                continue
            holders = [t for t in children if t['dep'] in ('nsubj', 'nsubj:pass')]
            if not holders:
                continue
            stats['state_n'] += 1
            bindings = [s for s in model.entity_states if s.sent_idx == si and s.holder.lower() in {t['form'].lower() for t in holders}]
            stats['state_correct'] += int(any(s.property.lower() == pred['form'].lower() for s in bindings))
            stats['state_missing'] += int(not bindings)
    for key in total:
        total[key] += stats[key]
    print('DOCUMENT ' + json.dumps({'id': docid, 'seconds': elapsed, **stats}), flush=True)
print('SUMMARY ' + json.dumps({'counts': total, 'miss_examples': examples, 'scope': 'text-only exact surface-head role accuracy; missing predicates/answers counted wrong; no statistical/generalization claim; supplied tokenization and sentence boundaries'}), flush=True)
```

Exact evaluated documents and outputs:

| UD-EWT document ID | Sentences / tokens | Gold verbs matched | Agent correct / eligible | Patient correct / eligible | State correct / eligible | Read seconds |
|---|---|---|---|---|---|---:|
| `weblog-blogspot.com_zentelligence_20040423000200_ENG_20040423_000200` | 3 / 39 | 2/2 | 1/2 | 0/0 | 0/0 | 41.904 |
| `weblog-blogspot.com_marketview_20050511222700_ENG_20050511_222700` | 7 / 92 | 7/7 | 1/6 | 2/4 | 2/4 | 4.481 |
| `weblog-blogspot.com_floppingaces_20041126180010_ENG_20041126_180010` | 9 / 137 | 19/19 | 1/11 | 7/11 | 1/1 | 5.968 |
| `weblog-blogspot.com_marketview_20050224181500_ENG_20050224_181500` | 5 / 154 | 19/19 | 1/11 | 7/12 | 3/3 | 9.482 |
| `weblog-blogspot.com_grandpasgripes_20060413051000_ENG_20060413_051000` | 16 / 201 | 32/32 | 5/22 | 14/16 | 1/1 | 6.447 |

These timings are observed calls on one shared process and a concurrently used machine. They mix lazy initialization and warm caches and are not a calibrated throughput benchmark. The corpus loader found 316 complete documents overall; only the first five were evaluated.

Scoring caveats beyond sample size: agent gold is a structural subject/by-agent proxy rather than a universal semantic-agent annotation; passive patient and copular definitions are stated in the code; multiword-range and empty-node CoNLL-U lines are omitted; extra or spurious emitted events are not penalized by the role-question accuracy and require a separate precision measure.

### A3. Matched existing component scorer and sentence controls

PowerShell variable: `$followupCode`; launched with `PYTHONHASHSEED=0`, `python.exe -B -u -c $followupCode`.

```python
import os, sys, json, time, tempfile, hashlib
from pathlib import Path
sys.path.insert(0, r'C:\AI\hd-instrument')
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
from hdlab.situation_reader import SituationReader, _write_temp_conll
from hdlab.frontend import tokenize
import experiments.exp_board_agent_slot_ud_v1 as AG
from hdlab import frontend as FE
root = Path(r'C:\AI\hd-instrument')
reader_path = root / 'hdlab/situation_reader.py'
print('READER_SHA ' + hashlib.sha256(reader_path.read_bytes()).hexdigest(), flush=True)
# Existing component evaluator, exactly the first 40 UD-EWT test sentences used above.
gold_sents = AG.load_ud(AG.UD_TEST)[:40]
items = AG.gold_agent_items(gold_sents)
per, tally = AG._eval(items, FE.tagger(), AG.load_given_gazetteer())
print('MATCHED_COMPONENT ' + json.dumps({'eligible_agent_questions': len(items), 'scored': sum(p[0] for p in per.values()), 'hybrid_correct': sum(p[3] for p in per.values()), 'positional_correct': sum(p[1] for p in per.values()), 'full_competition_correct': sum(p[2] for p in per.values()), 'twin_correct': sum(p[4] for p in per.values()), 'tally': tally}), flush=True)
def read_sentence(text, annotate=False):
    toks = tokenize(text)
    # Annotation control uses automatic predicted nominal/pronoun spans, NOT gold categories or links.
    # Annotation-free mode is the deployed input under test. No reader flag is changed.
    up = FE.tagger().tag(toks) if annotate else None
    rows = [(0, i, t, '(' + str(i) + ')' if annotate and up[i] in ('NOUN', 'PROPN', 'PRON') else '_') for i,t in enumerate(toks)]
    path = _write_temp_conll(rows)
    assert Path(path).resolve().parent == Path(tempfile.gettempdir()).resolve()
    try:
        reader = SituationReader()
        start = time.perf_counter()
        sm = reader.read(path)
        return {'text': text, 'mode': 'predicted_mentions_unique_ids' if annotate else 'text_only', 'seconds': round(time.perf_counter()-start, 3), 'events': [(e.predicate, e.agent, e.patient) for e in sm.events], 'states': [(s.holder,s.property) for s in sm.entity_states], 'tags': up}
    finally:
        os.unlink(path)
for text in ['They own Blogger.', 'Alice thanked Bob.', 'Bob was thanked by Alice.', 'She thanked Bob.', 'The sky is blue.', 'Alice did not thank Bob.']:
    print('SENTENCE ' + json.dumps(read_sentence(text)), flush=True)
    if text in ('They own Blogger.', 'She thanked Bob.'):
        print('SENTENCE ' + json.dumps(read_sentence(text, annotate=True)), flush=True)
# Diagnostics on the gold question distribution, not inference input.
pron = sum(1 for toks,v,a,p in items if gold_sents[next(i for i,s in enumerate(gold_sents) if [t['form'] for t in s] == toks)][a-1]['upos'] == 'PRON')
print('QUESTION_DISTRIBUTION ' + json.dumps({'agent_questions': len(items), 'gold_pronoun_agents': pron}), flush=True)
```

Observed results are reported in E07. Note that this comparison deliberately executes the existing component scorer as it stands, including its own gazetteer and tagger use. It does not pretend the two execution paths differ in only one line. The two predicted-mention controls are separate interventions using the existing tagger, not the gold categories. A3 did not print polarity metadata for the negated sentence; the positive-looking event tuple alone must not be interpreted as a negation failure.

### A4. Existing algebra tests and BF checker

The exact Python program supplied through `$testCode` to `python.exe -B -u -c $testCode` was:

```python
import sys
sys.path.insert(0, r'C:\AI\hd-instrument')
from hypothesis import settings
settings.register_profile('evaluation_read_only', database=None, derandomize=True)
settings.load_profile('evaluation_read_only')
import pytest
raise SystemExit(pytest.main([r'C:\AI\hd-instrument\verification\test_algebra.py', r'C:\AI\hd-instrument\verification\test_bf_status_tags.py', '-q', '-p', 'no:cacheprovider']))
```

Output: `4 passed, 2 warnings in 4.50s`. The warnings were `PytestAssertRewriteWarning` for already-imported Hypothesis modules. As explained in E08, this did not execute the BF checker's `main()`.

The subsequent standalone command was:

```powershell
& C:\AI\hd-instrument\.venv\Scripts\python.exe -B C:\AI\hd-instrument\verification\test_bf_status_tags.py | Select-Object -Last 8
```

Observed ending: `SUMMARY BF=8 BF_SPIRIT=79 NOT_BF=6 | 93 organs tagged`; `RESULT all PASS`. The positive control is called inside that script's `main()` before the registry checks. The pipeline displays only the last eight lines, so the exit-status claim here comes from the checker's printed `RESULT`, not treating PowerShell's pipeline exit as an independently verified Python exit code.

### A5. Witness-discovery gate, aggregate edge case and event-codec checks

PowerShell variable: `$checks`; launcher set `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, then invoked `python.exe -B -u -c $checks`.

```python
import os, sys, ast, json, importlib.util
from pathlib import Path
sys.path.insert(0, r'C:\AI\hd-instrument')
root = Path(r'C:\AI\hd-instrument')
path = root / 'verification/test_no_witness_is_islanded_from_the_gate.py'
spec = importlib.util.spec_from_file_location('witness_coverage', path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
islands = m._islanded_now(); new = sorted(islands - m.KNOWN_ISLANDED)
print('WITNESS_DISCOVERY ' + json.dumps({'islanded_by_repo_checker': len(islands), 'new_outside_known_allowlist': len(new), 'examples': new[:12]}))
for function in (m.test_no_new_witness_is_islanded, m.test_the_baseline_does_not_list_files_that_are_fine_now):
    try:
        function()
        print('CHECK ' + function.__name__ + ' PASS')
    except AssertionError as e:
        print('CHECK ' + function.__name__ + ' FAIL ' + str(e).splitlines()[0])
source = (root / 'experiments/exp_situation_model_qa_modern_v1.py').read_text(encoding='utf-8')
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == '_agg')
namespace = {}
exec(compile(ast.Module(body=[node], type_ignores=[]), '<existing_board_aggregate>', 'exec'), namespace)
rows = {'with_baseline': {'n': 100, 'model_acc': 0.6, 'strongest_floor': 0.5, 'twin_acc': 0.1}, 'without_baseline': {'n': 100, 'model_acc': 0.6, 'strongest_floor': None, 'twin_acc': None}}
print('AGGREGATE_NULL_BASELINE_CONTROL ' + json.dumps(namespace['_agg'](rows)))
from hdlab.event_bundle import _run_all_selftests
print('EVENT_BUNDLE ' + json.dumps(_run_all_selftests()))
```

This program intentionally catches the existing discovery-gate assertion to print its failure and continue independent checks. Its process exit of zero does **not** mean that assertion passed. Results: new-islands check FAIL; baseline-maintenance check PASS; aggregate baseline=0.25/twin=0.05 on the synthetic inputs; event codec checks PASS with `reuse_verified=RoleSlotSummarizer.summarize_flat`.

### A6. Static source counts and hashes

PowerShell variable: `$auditCode`; invoked with `python.exe -B -c $auditCode`.

```python
import ast, collections, pathlib, json, hashlib, sys
root = pathlib.Path(r'C:\AI\hd-instrument')
info = {}
for name in ['hdlab/situation_reader.py', 'hdlab/frontend.py', 'hdlab/coref.py', 'hdlab/referent_per_np.py', 'experiments/exp_situation_model_qa_modern_v1.py']:
    path = root / name
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    info[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'lines': len(source.splitlines()), 'broad_exception_handlers': sum(isinstance(n, ast.ExceptHandler) and isinstance(n.type, ast.Name) and n.type.id == 'Exception' for n in ast.walk(tree))}
info['verification'] = {'files': 0, 'pytest_function_or_class_files': 0, 'main_only_files': 0, 'parse_errors': 0}
for p in (root / 'verification').glob('test_*.py'):
    info['verification']['files'] += 1
    try:
        tree = ast.parse(p.read_text(encoding='utf-8-sig'))
    except (SyntaxError, UnicodeError):
        info['verification']['parse_errors'] += 1
        continue
    collected = any((isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_')) or (isinstance(n, ast.ClassDef) and n.name.startswith('Test')) for n in tree.body)
    main = any(isinstance(n, ast.FunctionDef) and n.name == 'main' for n in tree.body)
    info['verification']['pytest_function_or_class_files'] += int(collected)
    info['verification']['main_only_files'] += int(main and not collected)
print(json.dumps(info, indent=2))
```

This is a static inventory, not pytest collection. Its counts are explicitly separated from the project's own executable discovery-gate results in E08. The inspected reader had 5,332 total source lines and 17 broad exception handlers; the board file had 2,784 lines and 42 such handlers. Counts alone do not establish a defect.


### A7. Invalid backend names, environment versions and dependency observation

PowerShell variable: `$configurationProbe`; invoked with `python.exe -B -u -c $configurationProbe`.

```python
import os, sys, json, ast, hashlib, importlib.metadata
from pathlib import Path
sys.path.insert(0, r'C:\AI\hd-instrument')
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
from hdlab import frontend as F
tagger = F.Tagger(source='evaluation_invalid_source')
parser = F.Parser(source='evaluation_invalid_source')
print('INVALID_BACKEND_CONTROL ' + json.dumps({
    'requested': 'evaluation_invalid_source',
    'tagger_constructed': True,
    'selected_perceptron': tagger._pt is not None,
    'parser_constructed': True,
    'selected_arceager': parser._ae is not None}))
root = Path(r'C:\AI\hd-instrument')
versions = {}
for name in ('torch', 'numpy', 'scipy', 'nltk', 'pytest', 'hypothesis'):
    try:
        versions[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        versions[name] = None
print('ENVIRONMENT ' + json.dumps({'python': sys.version, 'executable': sys.executable, 'packages': versions}))
imports = {}
for name in ('situation_reader', 'frontend', 'meaning_foundation', 'underspecified_sense_reader', 'thematic_role_labeler', 'semantic_hub'):
    path = root / 'hdlab' / (name + '.py')
    tree = ast.parse(path.read_text(encoding='utf-8'))
    modules = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module} | {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names})
    imports[name] = [m for m in modules if m.startswith(('nltk', 'tools', 'experiments', 'sklearn'))]
print('DEPENDENCY_OBSERVATION ' + json.dumps(imports))
print('READER_SHA_END ' + hashlib.sha256((root / 'hdlab/situation_reader.py').read_bytes()).hexdigest())
```

Observed: both invalid-name constructors succeeded; the tagger selected its perceptron object and the parser its arc-eager object. Package versions and the unchanged reader hash are listed in A0. The selected static dependency scan found `nltk.corpus` in `underspecified_sense_reader`; it is not a complete transitive dependency audit.

### A8. Five-document predicted-mention intervention and negation metadata

PowerShell variable: `$predictedMentionProbe`; launched with `PYTHONHASHSEED=0`, `python.exe -B -u -c $predictedMentionProbe`.

```python
import os, sys, json, time, tempfile, hashlib
from pathlib import Path
sys.path.insert(0, r'C:\AI\hd-instrument')
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
from hdlab.situation_reader import SituationReader, _write_temp_conll
from hdlab import frontend as F
from hdlab import lexical_categories as LC
import experiments.exp_board_agent_slot_ud_v1 as A
source = A.load_ud(A.UD_TEST)[:40]
lengths = [3, 7, 9, 5, 16]
offset = 0
totals = {'eligible': 0, 'correct': 0, 'missing': 0, 'pronoun_n': 0, 'pronoun_correct': 0}
for di, count in enumerate(lengths):
    gold = source[offset:offset+count]
    offset += count
    sentences = [[t['form'] for t in s] for s in gold]
    LC.get().new_document()
    posteriors = list(LC.get().feed_passage(sentences))
    rows = []
    uid = 0
    for si, (tokens, posterior) in enumerate(zip(sentences, posteriors)):
        tags = [LC.get().tags[int(p.argmax())] for p in posterior]
        for wi, (token, tag) in enumerate(zip(tokens, tags)):
            mark = '(' + str(uid) + ')' if tag in ('NOUN', 'PROPN', 'PRON') else '_'
            rows.append((si, wi, token, mark))
            uid += 1
    path = _write_temp_conll(rows)
    assert Path(path).resolve().parent == Path(tempfile.gettempdir()).resolve()
    try:
        start = time.perf_counter()
        sm = SituationReader().read(path)
        stats = {k: 0 for k in totals}
        for si, sentence in enumerate(gold):
            items = A.gold_agent_items([sentence])
            for tokens, verb, target, passive in items:
                vt = sentence[verb-1]
                matches = [e for e in sm.events if e.sent_idx == si and e.pred_idx == verb-1 and e.predicate.lower() in (vt['form'].lower(), vt.get('lemma', vt['form']).lower())]
                answer = matches[0].agent if len(matches) == 1 else None
                ok = answer is not None and answer.lower() == tokens[target-1].lower()
                stats['eligible'] += 1
                stats['correct'] += int(ok)
                stats['missing'] += int(answer in (None, '', '?'))
                if sentence[target-1]['upos'] == 'PRON':
                    stats['pronoun_n'] += 1
                    stats['pronoun_correct'] += int(ok)
        for k in totals:
            totals[k] += stats[k]
        print('PREDICTED_MENTION_DOCUMENT ' + json.dumps({'document_index': di, 'seconds': round(time.perf_counter()-start, 2), **stats}), flush=True)
    finally:
        os.unlink(path)
print('PREDICTED_MENTION_TOTAL ' + json.dumps(totals), flush=True)
print('SCOPE: annotation input constructed from predicted categories only; unique IDs give no true cross-token links; extra preprocessing/control arm, not a deployed code fix', flush=True)
tokens = F.tokenize('Alice did not thank Bob.')
path = _write_temp_conll([(0, i, token, '_') for i, token in enumerate(tokens)])
assert Path(path).resolve().parent == Path(tempfile.gettempdir()).resolve()
try:
    sm = SituationReader().read(path)
    print('NEGATION_METADATA ' + json.dumps([{'predicate': e.predicate, 'agent': e.agent, 'patient': e.patient, 'polarity': e.polarity, 'provenance': e.polarity_provenance} for e in sm.events]), flush=True)
finally:
    os.unlink(path)
print('READER_SHA ' + hashlib.sha256(Path(r'C:\AI\hd-instrument\hdlab\situation_reader.py').read_bytes()).hexdigest())
```

This diagnostic changes only the temporary input fixture: the existing category organ predicts which observed tokens receive unique mention IDs. It does not use gold POS or gold coreference links. It does add an extra preprocessing pass, so it must not be described as the deployed annotation-free reader or as a code fix. The five document lengths reproduce the exact complete-document boundaries recorded in A2.

Observed A8 output:

| Document index (same order as A2) | Correct / eligible agents | Missing answers | Correct / eligible pronoun agents | Read seconds |
|---|---|---:|---|---:|
| 0 | 2/2 | 0 | 0/0 | 26.00 |
| 1 | 4/6 | 0 | 4/4 | 2.29 |
| 2 | 7/11 | 0 | 7/7 | 4.24 |
| 3 | 10/11 | 0 | 8/9 | 3.73 |
| 4 | 19/22 | 1 | 12/13 | 4.19 |
| Total | **42/52** | **1** | **31/33** | Not a calibrated throughput comparison |

Negation output: `predicate=thank, agent=alice, patient=bob, polarity=-1, provenance=direct_negator`. Final reader SHA-256 remained `62ee788a9c4857752c9798bd6af373b5acb88579f70465cfa69977840c52aa14`.


### A9. Current-code static review: version manifest and exact programs

This second pass used the existing Python interpreter with **-B**, importing only standard-library AST, path, hash and reporting utilities. It did not import or execute hdlab, experiments, Torch, tests or model assets. The programs below parse source into syntax trees and print selected function bodies; removing a docstring from an in-memory AST does not edit the source file. Functions requested by name but not defined in a given file produce no function output; imported functions were followed to their defining modules during navigation.

Working directory for these commands: `C:\AI`. Interpreter: `C:\AI\hd-instrument\.venv\Scripts\python.exe`. No background process or test session remains from this static pass.

**Final source check:** 2026-09-15T21:53:17.727938+00:00. All 13 files parsed successfully. Their hashes matched the versions inspected in the deep review. This is a bounded source-version check, not a claim that the entire repository or its assets stayed unchanged.

| File | SHA-256 | Lines |
|---|---|---:|
| [hdlab/belief_reader.py](../hdlab/belief_reader.py) | `9450e26f880af3e4663e2efed83251433296da1afdd17c014d0195a3dcd91952` | 493 |
| [hdlab/bound_event_backbone.py](../hdlab/bound_event_backbone.py) | `83ee0a3e5549e217895f3c2067695912555bb7cb85eeaf1d565f330156734f0b` | 256 |
| [hdlab/coref.py](../hdlab/coref.py) | `3af303cf28532693d9ead9cda7393a3637b477d5a6131fd5c95405c21e6e99ff` | 1331 |
| [hdlab/entity_resolver.py](../hdlab/entity_resolver.py) | `c968ce5a6b4bdba636a828f650423686d3ac1edab61dc06fa3ceb67913443ec6` | 735 |
| [hdlab/goal_register.py](../hdlab/goal_register.py) | `3a54c685ef256d013fe8c79303d981b7ef8e2d5002fe97abbd469e5fb64b08c7` | 814 |
| [hdlab/joint_relation_frontend.py](../hdlab/joint_relation_frontend.py) | `7417cd0c54c4cbedd55ce88a24089eb7ffc0f4bc497c445b98d39b084b99b229` | 816 |
| [hdlab/lexical_categories.py](../hdlab/lexical_categories.py) | `8bddc3668560fa4a1c1563f6720bc67c5568ed85f4478b1e6578cdff36408d88` | 1569 |
| [hdlab/perceptual_access_ledger.py](../hdlab/perceptual_access_ledger.py) | `7597772e650f365adc87868d5f52fe4bace1e0d7bca1967d2639ad75eb31d8cc` | 748 |
| [hdlab/pos_tagger.py](../hdlab/pos_tagger.py) | `6a28d9d5c0da9ddd5d78559073a2c08ed6a5ac4a8d1c5e47ab9e74b9405078e8` | 354 |
| [hdlab/referent_per_np.py](../hdlab/referent_per_np.py) | `48dcbf8270043b85b8da9426d864e0c114e09ca69d55a178d0398609a62f421a` | 308 |
| [hdlab/situation_reader.py](../hdlab/situation_reader.py) | `491f5c7d13cdb58ee20c146cb5c7a564df02b2a56ce8c09eb3d5049d7f8d5598` | 5465 |
| [hdlab/space_reader.py](../hdlab/space_reader.py) | `7f082bf161183c3f4b956be9ffdb6910a2fdd1d4efc68a0bb4a2ee1e8f76e2ec` | 806 |
| [hdlab/world_state_register.py](../hdlab/world_state_register.py) | `5f2ce0f396423a0eb964ca9d6b0e2dbfe8a706519c5e162fd79e0b67bac58a59` | 300 |

Each numbered program below was passed to the following PowerShell wrapper (replace the placeholder with that exact program):

```powershell
$staticReview = @'
<program below>
'@
& C:\AI\hd-instrument\.venv\Scripts\python.exe -B -c $staticReview
```

#### Static inspection 1

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/situation_reader.py': ['read', '_cached_tag', '_cached_tag_matrix', '_cached_tag_posterior', '_cached_parse_heads', '_cached_head_posterior', '_cached_parse_conf'],
}
for relative, names in selected.items():
    path = root / relative
    raw = path.read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 2

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/situation_reader.py': ['_read_entities', '_read_world_state', '_read_bound_event_tokens', '_read_polarity', '_read_belief', '_read_goals', '_read_predict_revise'],
    'hdlab/referent_per_np.py': ['referent_per_np_source', '_mk_referent'],
}
for relative, names in selected.items():
    path = root / relative
    raw = path.read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 3

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/world_state_register.py': ['fold', 'apply', 'step', 'has', 'holder_of', 'is_open'],
    'hdlab/bound_event_backbone.py': ['build', 'from_event', 'encode', 'resolve'],
    'hdlab/goal_register.py': ['make_canonicalizer', 'track_status', 'track_status_thwart'],
    'hdlab/situation_reader.py': ['_gold_alignment', 'discovered_pronoun_targets', 'graded_pronoun_resolve', 'retrievable_referents', '_read_entities_core'],
    'hdlab/lexical_categories.py': ['new_document', 'feed_passage', 'posterior', 'tag', 'register_generation'],
}
for relative, names in selected.items():
    path = root / relative
    raw = path.read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 4

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/coref.py': ['discovered_pronoun_targets', 'retrievable_referents', 'graded_pronoun_resolve'],
    'hdlab/lexical_categories.py': ['begin', 'commit', 'note', 'get', '_log_emit', 'update_document_register'],
    'hdlab/world_state_register.py': ['apply_event', 'classify', '_read_preconditions'],
    'hdlab/bound_event_backbone.py': ['_norm_event', 'event_token', 'cue_token'],
    'hdlab/goal_register.py': ['_named_clusters'],
}
for relative, names in selected.items():
    path = root / relative
    raw = path.read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 5

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/belief_reader.py': ['drive', 'extract_reality_events', 'extract_status_events', 'extract_location_events'],
    'hdlab/perceptual_access_ledger.py': ['__init__', '_parse_sents'],
    'hdlab/situation_reader.py': ['_read_temporal_reasoning', '_read_spatial_reasoning', '_read_causal_reasoning', '_read_predictive_causal'],
    'hdlab/goal_register.py': ['_cluster_name'],
}
for relative, names in selected.items():
    path = root / relative
    raw = path.read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 6

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/situation_reader.py': ['_build_joint_temporal_reasoner', '_cached_tag', '_cached_parse_heads'],
    'hdlab/belief_reader.py': ['_frontend'],
    'hdlab/joint_relation_frontend.py': ['_frontend', 'parse_sentence'],
    'hdlab/perceptual_access_ledger.py': ['_frontend', '_parse_sent'],
    'hdlab/coref.py': ['graded_pronoun_resolve'],
}
for relative, names in selected.items():
    path = root / relative
    raw = path.read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 7

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/situation_reader.py': ['_read_entities', '_read_world_state', '_read_belief', '_read_temporal_reasoning'],
    'hdlab/goal_register.py': ['_named_clusters', '_cluster_name', 'make_canonicalizer'],
    'hdlab/pos_tagger.py': ['tag'],
}
for relative, names in selected.items():
    raw = (root / relative).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 8

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/belief_reader.py': ['extract_status_events', 'extract_location_events'],
    'hdlab/space_reader.py': ['_frontend', '_cluster_covering'],
    'hdlab/situation_reader.py': ['_read_causal_reasoning', '_gold_alignment', '_read_bound_event_tokens'],
    'hdlab/lexical_categories.py': ['begin', 'commit', 'feed_passage'],
    'hdlab/entity_resolver.py': ['cluster'],
}
for relative, names in selected.items():
    raw = (root / relative).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Static inspection 9

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
    'hdlab/world_state_register.py': ['apply_event'],
    'hdlab/bound_event_backbone.py': ['_norm_event', 'build'],
    'hdlab/goal_register.py': ['track_status', 'track_status_thwart'],
}
for relative, names in selected.items():
    raw = (root / relative).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print('FILE', relative, 'SHA256', hashlib.sha256(raw).hexdigest())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            print('FUNCTION', node.name, 'LINE', node.lineno)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            print(ast.unparse(node))
```

#### Final manifest/syntax check

```python
import ast, datetime, hashlib, json, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
files = ['hdlab/belief_reader.py', 'hdlab/bound_event_backbone.py', 'hdlab/coref.py', 'hdlab/entity_resolver.py', 'hdlab/goal_register.py', 'hdlab/joint_relation_frontend.py', 'hdlab/lexical_categories.py', 'hdlab/perceptual_access_ledger.py', 'hdlab/pos_tagger.py', 'hdlab/referent_per_np.py', 'hdlab/situation_reader.py', 'hdlab/space_reader.py', 'hdlab/world_state_register.py']
print('VERIFIED_AT_UTC', datetime.datetime.now(datetime.timezone.utc).isoformat())
for relative in files:
    raw = (root / relative).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print(json.dumps({'file': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'lines': len(raw.splitlines()), 'syntax': 'ok'}))
```

**Invocation failure also recorded:** the first manifest attempt used the following program with the same wrapper. PowerShell/native argument handling stripped the double quotes in its file list, and Python exited 1 with `NameError: name 'hdlab' is not defined` at line 3. No source file was opened by that failed attempt. The single-quoted-list invocation above then succeeded with exit code 0.

```python
import ast, datetime, hashlib, json, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
files = ["hdlab/belief_reader.py","hdlab/bound_event_backbone.py","hdlab/coref.py","hdlab/entity_resolver.py","hdlab/goal_register.py","hdlab/joint_relation_frontend.py","hdlab/lexical_categories.py","hdlab/perceptual_access_ledger.py","hdlab/pos_tagger.py","hdlab/referent_per_np.py","hdlab/situation_reader.py","hdlab/space_reader.py","hdlab/world_state_register.py"]
print('VERIFIED_AT_UTC', datetime.datetime.now(datetime.timezone.utc).isoformat())
for relative in files:
    raw = (root / relative).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    print(json.dumps({'file': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'lines': len(raw.splitlines()), 'syntax': 'ok'}))
```

**Additional read-only navigation:** rg/rg --files located repository instruction files, definitions, callers and cache uses; Get-Content/Select-Object read source ranges, instructions and this report. An initial AST inventory enumerated reader imports and constructor defaults. These were source-inspection operations, not extra model/test executions. Relevant source locations and the function selections above record the review surface; this appendix is not a verbatim transcript of every text-navigation command.

**Report-only operations:** apply_patch created/updated this document. A report-assembly JavaScript call initially failed to parse before any tool or file operation; the corrected call succeeded. Final document validation reads this Markdown, parses its Python code blocks for syntax without executing them, and checks the current/historical section boundaries.


### A10. Final report validation

The following program was executed with the same PowerShell wrapper and interpreter as A9. It checks the report structure and parses embedded Python for syntax only. It does not execute the recorded evaluations. The first invocation used `assert 'DEEP STATIC REVIEW IN PROGRESS' not in text` on line 5 and failed because that literal appears in the checker itself; the corrected line below restricts the check to the report header. This was a report-check defect, not a substrate failure.

```python
import ast, pathlib, re
path = pathlib.Path(r'C:\AI\hd-instrument\notes\SUBSTRATE_EVALUATION.md')
text = path.read_text(encoding='utf-8')
assert '**Status: COMPLETE' in text
assert 'DEEP STATIC REVIEW IN PROGRESS' not in text.split('## Scope and permissions', 1)[0]
assert text.index('## Current-code deep review') < text.index('## Historical runtime assessment')
for number in range(1, 9):
    assert len(re.findall(r'^### D0' + str(number) + r'\.', text, re.M)) == 1
blocks = re.findall(r'^```python\r?\n(.*?)^```\s*$', text, re.M | re.S)
for number, block in enumerate(blocks, 1):
    ast.parse(block, filename='report_python_block_' + str(number))
fences = re.findall(r'^```[^\r\n]*$', text, re.M)
assert len(fences) % 2 == 0
assert '### A9. Current-code static review: version manifest and exact programs' in text
print('REPORT', str(path))
print('LINES', len(text.splitlines()))
print('PYTHON_BLOCKS_SYNTAX_OK', len(blocks))
print('CURRENT_FINDINGS', 8)
print('FENCES_BALANCED', len(fences))
print('NOTE: no embedded program was executed; this checks document structure and syntax only')
```


### A11. Focused follow-up: exact commands, controlled probes and outputs

All Python programs in this appendix used the existing interpreter, with bytecode writing disabled, from C:\AI:

```powershell
$focusReview = @'
<exact program below>
'@
& C:\AI\hd-instrument\.venv\Scripts\python.exe -B -c $focusReview
```

#### Source manifest

| File | SHA-256 |
|---|---|
| hdlab/situation_reader.py | `2210b4bb21c97d2d6eed42220e2b44105d1b2ed5dbb78b50e1ed2bc718cbf517` |
| hdlab/goal_register.py | `b5e2f567902207c21ceeaedc7d8a343db55d32b05f8271b1acfefc03861d19f6` |
| hdlab/state_register.py | `d6cd64248bb74cff6f1902e6d65ddc0a2477dfaefefeb5da4e7053a9e1d9d595` |
| hdlab/belief_reader.py | `9450e26f880af3e4663e2efed83251433296da1afdd17c014d0195a3dcd91952` |
| hdlab/belief_timeline.py | `90d6bda0b9bfa99381a276bb740f8e170af8b9689b8663fcebe08909e9d8db0e` |
| hdlab/perceptual_access_ledger.py | `7597772e650f365adc87868d5f52fe4bace1e0d7bca1967d2639ad75eb31d8cc` |
| hdlab/coref.py | `3af303cf28532693d9ead9cda7393a3637b477d5a6131fd5c95405c21e6e99ff` |
| hdlab/lexical_categories.py | `8bddc3668560fa4a1c1563f6720bc67c5568ed85f4478b1e6578cdff36408d88` |
| hdlab/joint_relation_frontend.py | `7417cd0c54c4cbedd55ce88a24089eb7ffc0f4bc497c445b98d39b084b99b229` |
| hdlab/world_state_register.py | `5f2ce0f396423a0eb964ca9d6b0e2dbfe8a706519c5e162fd79e0b67bac58a59` |
| hdlab/bound_event_backbone.py | `83ee0a3e5549e217895f3c2067695912555bb7cb85eeaf1d565f330156734f0b` |
| hdlab/theory_of_mind.py | `42b3bc28c4b21ea6ef0bf7b3ed847eff219c4885be0e033e9cb3d9da9a95866c` |

Read-only Git commands: `git -C C:\AI\hd-instrument rev-parse --show-toplevel HEAD` and `git -C C:\AI\hd-instrument worktree list --porcelain`. The active checkout reported HEAD 951ae510cb9347a3805c217569fa5dbd9439d9a7. No Git mutation was performed. Text navigation used rg, Get-Content and Select-Object on the report, source files and status notes; no benchmark/tool runner was invoked through those reads.

#### Source inspection 1

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
 'hdlab/situation_reader.py': ['read','_read_entities','_read_belief','_read_world_state'],
 'hdlab/goal_register.py': ['make_canonicalizer','track_status','track_status_thwart'],
 'hdlab/joint_relation_frontend.py': ['parse_sentence','clear_cache'],
}
for rel, names in selected.items():
 raw=(root/rel).read_bytes()
 print('FILE', rel, 'SHA256', hashlib.sha256(raw).hexdigest())
 tree=ast.parse(raw.decode('utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
   print('FUNCTION',node.name,'LINE',node.lineno)
   if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
    node.body=node.body[1:]
   print(ast.unparse(node))
```

#### Source inspection 2

```python
import ast, hashlib, pathlib
root = pathlib.Path(r'C:\AI\hd-instrument')
selected = {
 'hdlab/situation_reader.py': ['_read_entity_states','_read_predict_revise','_read_affected_entity','_read_goals','_read_tom_action','_read_prediction'],
 'hdlab/world_state_register.py': ['__init__','_set_have','_set_state','_read_preconditions','apply_event','fold','has','holder_of','is_open','unmet_preconditions'],
 'hdlab/bound_event_backbone.py': ['__init__','resolve','_segment','build'],
}
for rel,names in selected.items():
 raw=(root/rel).read_bytes()
 print('FILE',rel,'SHA256',hashlib.sha256(raw).hexdigest())
 tree=ast.parse(raw.decode('utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
   print('FUNCTION',node.name,'LINE',node.lineno)
   if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
    node.body=node.body[1:]
   print(ast.unparse(node))
```

#### Source inspection 3

```python
import ast, hashlib, pathlib
root=pathlib.Path(r'C:\AI\hd-instrument')
files=['hdlab/goal_register.py','hdlab/state_register.py','hdlab/belief_timeline.py','hdlab/theory_of_mind.py','hdlab/world_state_register.py','hdlab/situation_reader.py']
for rel in files:
 raw=(root/rel).read_bytes()
 tree=ast.parse(raw.decode('utf-8-sig'))
 print('FILE',rel,'SHA256',hashlib.sha256(raw).hexdigest())
 for node in tree.body:
  if isinstance(node,(ast.Import,ast.ImportFrom)):
   print(ast.unparse(node))
  if isinstance(node,ast.ClassDef):
   print('CLASS',node.name,node.lineno)
   if node.name in ('Goal','SingleValueTrack','Span','WorldEvent','EntityState'):
    print(ast.unparse(node))
   else:
    print([(m.name,m.lineno) for m in node.body if isinstance(m,ast.FunctionDef)])
  if isinstance(node,ast.FunctionDef):
   print('DEF',node.name,node.lineno)
```

#### Source inspection 4

```python
import ast, hashlib, pathlib
root=pathlib.Path(r'C:\AI\hd-instrument')
selected={
 'hdlab/goal_register.py': ['_lemma','_goal_span_after_to','wants','why','achieved','goals_of'],
 'hdlab/belief_timeline.py': ['initial_value','reality_at','timeline_belief','_events_about','narration_timeline_belief','fired_inference_events'],
 'hdlab/state_register.py': ['__init__','start','apply_state','apply_event','fold','_t','is_in_state','state_at','had_been','add_state','active_at'],
 'hdlab/situation_reader.py': ['_read_events_wired','_align_events_to_toks','_space_parse_provider'],
}
for rel,names in selected.items():
 raw=(root/rel).read_bytes()
 print('FILE',rel,'SHA256',hashlib.sha256(raw).hexdigest())
 tree=ast.parse(raw.decode('utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
   print('FUNCTION',node.name,'LINE',node.lineno)
   if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
    node.body=node.body[1:]
   print(ast.unparse(node))
```

#### Source inspection 5

```python
import ast, hashlib, pathlib
root=pathlib.Path(r'C:\AI\hd-instrument')
selected={
 'hdlab/belief_reader.py': ['build_events','drive','extract_reality_events','extract_belief_assertions'],
 'hdlab/state_register.py': ['_canon_value','incompatible'],
 'hdlab/situation_reader.py': ['_read_predictive_causal','_read_coherence'],
}
for rel,names in selected.items():
 raw=(root/rel).read_bytes()
 print('FILE',rel,'SHA256',hashlib.sha256(raw).hexdigest())
 tree=ast.parse(raw.decode('utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
   print('FUNCTION',node.name,'LINE',node.lineno)
   if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
    node.body=node.body[1:]
   print(ast.unparse(node))
print('STATE_REGISTER_CONSTANTS')
tree=ast.parse((root/'hdlab/state_register.py').read_text(encoding='utf-8-sig'))
for node in tree.body:
 if isinstance(node,(ast.Assign,ast.AnnAssign)):
  print(ast.unparse(node))
```

#### Source inspection 6

```python
import ast, hashlib, pathlib
root=pathlib.Path(r'C:\AI\hd-instrument')
selected={
 'hdlab/perceptual_access_ledger.py': ['__init__','_parse_sents','observed'],
 'hdlab/bound_event_backbone.py': ['resolve_episode','episode_of','_content_stream'],
 'hdlab/goal_register.py': ['_sent_texts','_is_thwarted','_norm_pred'],
 'hdlab/theory_of_mind.py': ['compose_action','attribute_belief_value'],
}
for rel,names in selected.items():
 raw=(root/rel).read_bytes()
 print('FILE',rel,'SHA256',hashlib.sha256(raw).hexdigest())
 tree=ast.parse(raw.decode('utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
   print('FUNCTION',node.name,'LINE',node.lineno)
   if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
    node.body=node.body[1:]
   print(ast.unparse(node))
```

#### Source inspection 7

```python
import ast, hashlib, pathlib
root=pathlib.Path(r'C:\AI\hd-instrument')
selected={
 'hdlab/perceptual_access_ledger.py': ['_informed_after','_epistemic_statement','_split_sentences'],
 'hdlab/belief_timeline.py': ['hindsight_invariant'],
}
for rel,names in selected.items():
 raw=(root/rel).read_bytes()
 print('FILE',rel,'SHA256',hashlib.sha256(raw).hexdigest())
 tree=ast.parse(raw.decode('utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
   print('FUNCTION',node.name,'LINE',node.lineno)
   if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):
    node.body=node.body[1:]
   print(ast.unparse(node))
```

#### Source inspection 8

```python
import ast, hashlib, pathlib
path=pathlib.Path(r'C:\AI\hd-instrument\hdlab\perceptual_access_ledger.py')
raw=path.read_bytes()
print('FILE',str(path),'SHA256',hashlib.sha256(raw).hexdigest())
tree=ast.parse(raw.decode('utf-8-sig'))
for node in tree.body:
 if isinstance(node,(ast.Import,ast.ImportFrom)):
  print(ast.unparse(node))
 if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in ('PresenceState','LedgerTrace','_testimony_patterns','_match_any'):
  print(ast.unparse(node))
for node in ast.walk(tree):
 if isinstance(node,ast.FunctionDef) and node.name=='_match_any':
  print(ast.unparse(node))
```

#### Controlled probes R01-R05

The three runpy libraries have standard-library top-level imports. Their __main__ tests were not executed. Selected reader/driver methods retain their exact function bodies, with explicit fixture dependencies and an import guard. No model assets were loaded.

```python
import ast, builtins, hashlib, json, pathlib, runpy, types
from types import SimpleNamespace as N

root = pathlib.Path(r'C:\AI\hd-instrument')
def library(rel, name):
    raw = (root / rel).read_bytes()
    print('LIBRARY', rel, hashlib.sha256(raw).hexdigest())
    return runpy.run_path(str(root / rel), run_name=name)

def method(rel, name, injected=None, imports=None):
    raw = (root / rel).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    builtins_copy = dict(vars(builtins))
    mapping = imports or {}
    def controlled_import(mod, globals=None, locals=None, fromlist=(), level=0):
        if mod == '__future__':
            return builtins.__import__(mod, globals, locals, fromlist, level)
        if mod in mapping:
            return mapping[mod]
        raise RuntimeError('Unexpected import in isolated method: ' + mod)
    builtins_copy['__import__'] = controlled_import
    ns = {'__builtins__': builtins_copy, **(injected or {})}
    header = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
    unit = ast.fix_missing_locations(ast.Module(body=[header, node], type_ignores=[]))
    exec(compile(unit, str(root / rel), 'exec'), ns)
    return ns[name]

SR = library('hdlab/state_register.py', 'review_state_library')
GR = library('hdlab/goal_register.py', 'review_goal_library')
BT = library('hdlab/belief_timeline.py', 'review_belief_library')

# R01: exercise the actual reader-to-state method with controlled extraction.
# Category/parse outputs are fixtures; the register is the real stdlib-only implementation.
entity_method = method('hdlab/situation_reader.py', '_read_entity_states',
    {'_STATE_GRADED': False, 'EntityState': N},
    {'hdlab.attachment_arm': N(state_pairs_from_slot=lambda *a: set())})
extractor = N(extract_entity_states=lambda *a, **k: {(0, 2)},
              robust_cop=lambda *a, **k: set())
reader = N(_es_mod=extractor, _es_typed=lambda *a: 'pred_adj',
           _es_reg_cls=SR['StateRegister'],
           _cached_tag=lambda toks: ['NOUN', 'AUX', 'ADJ'],
           _cached_parse_heads=lambda *a: {1: 3, 2: 3, 3: 0},
           _cached_tag_matrix=lambda *a: None,
           _cached_head_posterior=lambda *a: None)
sm = N()
entity_method(reader, sm, [['door', 'is', 'open'], ['door', 'is', 'closed']])
print('R01_READER_STATE', json.dumps({
    'source_sentences': [s.sent_idx for s in sm.entity_states],
    'spans': [(s.value, s.t_open, s.t_close) for s in sm.state_register.spans_of('door')],
    'open_at_sentence_0': sm.state_register.is_in_state('door', 'open', t=0),
    'closed_at_sentence_0': sm.state_register.is_in_state('door', 'closed', t=0)}))
control = SR['StateRegister']()
control.apply_state('door', 'open', t=0)
control.apply_state('door', 'closed', t=1)
print('R01_TIMESTAMPED_CONTROL', control.is_in_state('door', 'open', t=0),
      control.is_in_state('door', 'closed', t=1))

# R02: agent-constrained purpose lookup must not return another person's purpose.
Goal = GR['Goal']
bob_goal = Goal(agent='bob', goal_head='eat', goal_text='eat dinner',
                kind='purpose_marked', source_verb='work', sent_idx=0,
                verb_tok=1, to_tok=2)
reg = GR['GoalRegister']([bob_goal])
print('R02_WHY', json.dumps({
    'bob_control': reg.why('work', 'bob').agent,
    'alice_query_returns': reg.why('work', 'alice').agent}))

# R03: target arguments and within-sentence order are not part of goal realization.
def make_goal():
    return Goal(agent='alice', goal_head='buy', goal_text='buy bread',
                kind='desire', source_verb='want', sent_idx=0,
                verb_tok=1, to_tok=2)
cases = []
for sentence, patient in [(1, 'bread'), (1, 'car'), (0, 'bread')]:
    goal = make_goal()
    event = N(sent_idx=sentence, global_idx=1, pred_idx=7,
              predicate='buy', agent='alice', patient=patient, polarity=1)
    GR['track_status']([goal], [event])
    basic = goal.status
    goal2 = make_goal()
    GR['track_status_thwart']([goal2], [event], sents=[['plain'], ['plain']])
    cases.append({'event_sentence': sentence, 'patient': patient,
                  'basic_status': basic, 'thwart_status': goal2.status})
print('R03_GOAL_MATCHING', json.dumps(cases))

# R04: capture the goal evidence supplied by an actual time-limited prediction closure.
class Projector:
    def available(self):
        return True
    def project(self, context, goals, candidates, gain=2.0):
        return N(context=list(context), goals=list(goals))
projector = Projector()
gek = N(lemmatize=lambda text: text.lower().split())
pred_method = method('hdlab/situation_reader.py', '_read_prediction',
                     imports={'hdlab': N(generalized_event_knowledge=gek)})
future_goal = Goal(agent='alice', goal_head='buy', goal_text='buy yacht',
                   kind='desire', source_verb='want', sent_idx=5,
                   verb_tok=1, to_tok=2)
full_reg = GR['GoalRegister']([future_goal])
full = N(events=[N(agent='alice')], wants=full_reg.wants)
pred_method(N(_gek_org=projector), full, [['alice', 'arrived'], ['later', 'plans']])
fp = full.predict_next_event(['depart', 'buy yacht'], t=0)
prefix = N(events=[N(agent='alice')], wants=GR['GoalRegister']([]).wants)
pred_method(N(_gek_org=projector), prefix, [['alice', 'arrived']])
pp = prefix.predict_next_event(['depart', 'buy yacht'], t=0)
print('R04_TIME_LIMITED_INPUTS', json.dumps({
    'full_context': fp.context, 'full_goal_evidence': fp.goals,
    'prefix_context': pp.context, 'prefix_goal_evidence': pp.goals,
    'future_goal_sentence': future_goal.sent_idx}))
# No actual projection score was computed; this probe records closure inputs.

# R05: use the actual belief driver with event-level observation fixtures.
drive = method('hdlab/belief_reader.py', 'drive', {
    'WorldEvent': BT['WorldEvent'],
    'extract_belief_assertions': lambda *a: [],
    'extract_inference_edges': lambda *a: ([], {}),
})
fact = {'fact_aliases': ['box'], 'fact_type': 'location',
        'value_vocab': ['kitchen', 'garden']}
for visible in [{'kitchen': True, 'garden': False},
                {'kitchen': False, 'garden': True}]:
    ledger = N(observed=lambda *a, **kw: N(observed=visible[kw['event_location']]))
    events, observed, agent, *_ = drive([['fixture']], {0: []}, fact, ['alice'],
                                       ledger, reality_events=[('kitchen', 0), ('garden', 0)])
    print('R05_SAME_SENTENCE', json.dumps({
        'event_visibility': visible,
        'stored_observation': sorted((str(k), v) for k, v in observed.items()),
        'belief': BT['timeline_belief'](events, observed, agent, 'box', 0),
        'reality': BT['reality_at'](events, 'box', 0)}))
print('SCOPE: isolated contract probes; controlled extraction/observation/projector; no reader model, corpus, training, network or writes')
```

**Initial invocation failure:** the first attempt was identical except that controlled_import lacked these two lines:

```python
        if mod == '__future__':
            return builtins.__import__(mod, globals, locals, fromlist, level)
```

It loaded the three small libraries, then exited 1 with `RuntimeError: Unexpected import in isolated method: __future__` before any R01-R05 probe ran. Adding the explicit standard-library allowance produced exit 0. This was a harness error, not a substrate failure.

**Successful output:**

```text
LIBRARY hdlab/state_register.py d6cd64248bb74cff6f1902e6d65ddc0a2477dfaefefeb5da4e7053a9e1d9d595
LIBRARY hdlab/goal_register.py b5e2f567902207c21ceeaedc7d8a343db55d32b05f8271b1acfefc03861d19f6
LIBRARY hdlab/belief_timeline.py 90d6bda0b9bfa99381a276bb740f8e170af8b9689b8663fcebe08909e9d8db0e
R01_READER_STATE {"source_sentences": [0, 1], "spans": [["open", 0, 0], ["closed", 0, null]], "open_at_sentence_0": false, "closed_at_sentence_0": true}
R01_TIMESTAMPED_CONTROL True True
R02_WHY {"bob_control": "bob", "alice_query_returns": "bob"}
R03_GOAL_MATCHING [{"event_sentence": 1, "patient": "bread", "basic_status": "satisfied", "thwart_status": "satisfied"}, {"event_sentence": 1, "patient": "car", "basic_status": "satisfied", "thwart_status": "satisfied"}, {"event_sentence": 0, "patient": "bread", "basic_status": "active", "thwart_status": "active"}]
R04_TIME_LIMITED_INPUTS {"full_context": ["alice", "arrived"], "full_goal_evidence": ["buy", "yacht"], "prefix_context": ["alice", "arrived"], "prefix_goal_evidence": [], "future_goal_sentence": 5}
R05_SAME_SENTENCE {"event_visibility": {"kitchen": true, "garden": false}, "stored_observation": [["('alice', 0.0)", false]], "belief": null, "reality": "kitchen"}
R05_SAME_SENTENCE {"event_visibility": {"kitchen": false, "garden": true}, "stored_observation": [["('alice', 0.0)", true]], "belief": "kitchen", "reality": "kitchen"}
SCOPE: isolated contract probes; controlled extraction/observation/projector; no reader model, corpus, training, network or writes
```

#### Controlled probes R06 and O01

```python
import ast, builtins, hashlib, json, pathlib, runpy, types
from types import SimpleNamespace as N

root = pathlib.Path(r'C:\AI\hd-instrument')
def library(rel, name):
    raw = (root / rel).read_bytes()
    print('LIBRARY', rel, hashlib.sha256(raw).hexdigest())
    return runpy.run_path(str(root / rel), run_name=name)

def method(rel, name, injected=None, imports=None):
    raw = (root / rel).read_bytes()
    tree = ast.parse(raw.decode('utf-8-sig'))
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    builtins_copy = dict(vars(builtins))
    mapping = imports or {}
    def controlled_import(mod, globals=None, locals=None, fromlist=(), level=0):
        if mod == '__future__':
            return builtins.__import__(mod, globals, locals, fromlist, level)
        if mod in mapping:
            return mapping[mod]
        raise RuntimeError('Unexpected import in isolated method: ' + mod)
    builtins_copy['__import__'] = controlled_import
    ns = {'__builtins__': builtins_copy, **(injected or {})}
    header = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
    unit = ast.fix_missing_locations(ast.Module(body=[header, node], type_ignores=[]))
    exec(compile(unit, str(root / rel), 'exec'), ns)
    return ns[name]


import re
BT = library('hdlab/belief_timeline.py', 'review_belief_library')
rel = 'hdlab/perceptual_access_ledger.py'
patterns = method(rel, '_testimony_patterns')
informed = method(rel, '_informed_after',
                  {'re': re, '_PRON': {'he', 'she', 'they'}, '_testimony_patterns': patterns})
observed_method = method(rel, 'observed', {
    'PresenceState': lambda **kw: N(awake=True, location=None, **kw),
    'LedgerTrace': lambda **kw: N(per_clause=[], **kw),
})
def ledger_for(texts):
    parsed = [N(text=t) for t in texts]
    led = N(_parse_sents=lambda text: parsed,
            _alias_regex=lambda aliases: re.compile('alice', re.I),
            _subject_is_agent=lambda *a: False,
            _absence_predicate=lambda *a: True,
            _field_state_update=lambda *a: [],
            _perceptual_field=lambda *a: (False, 'controlled absence'),
            _epistemic_statement=lambda *a: None,
            _match_any=lambda pats, text: any(re.search(p, text) for p in pats))
    led._informed_after=lambda ss, aliases, event: informed(led, ss, aliases, event)
    led.observed=lambda *a, **kw: observed_method(led, *a, **kw)
    return led
prefix_sents=[['The', 'box', 'moved', 'to', 'the', 'garden', '.']]
full_sents=prefix_sents+[['Time', 'passed', '.'],
                        ['Bob', 'told', 'Alice', 'the', 'box', 'was', 'in', 'the', 'garden', '.']]
fact={'fact_aliases':['box'], 'fact_type':'location', 'value_vocab':['garden']}
for sents in [prefix_sents, full_sents]:
    texts=[' '.join(s) for s in sents]
    led=ledger_for(texts)
    testimony=[('garden', 2, 'testimony')] if len(sents)>1 else []
    drive=method('hdlab/belief_reader.py', 'drive', {
        'WorldEvent': BT['WorldEvent'],
        'extract_belief_assertions': lambda *a: testimony,
        'extract_inference_edges': lambda *a: ([], {}),
    })
    events, obs, ag, *_=drive(sents, {i:[] for i in range(len(sents))},
                             fact, ['alice'], led, reality_events=[('garden',0)])
    tr=led.observed(' '.join(texts), ['alice'], event_index=0, event_location='garden')
    print('R06_FUTURE_TESTIMONY',json.dumps({
        'sentence_count': len(sents), 'absent_at_event': not tr.present_at_event,
        'informed_somewhere': tr.informed, 'marked_observed_at_event_0': tr.observed,
        'belief_at_0':BT['timeline_belief'](events,obs,ag,'box',0),
        'belief_after_testimony':BT['timeline_belief'](events,obs,ag,'box',3)}))

# O01: count how many sentence parses the real ledger/driver loops request.
# Sentence splitting and actual parsing are fixtures; counting preserves the call structure.
counter={'parse_sent':0}
def parse_sent(tokens):
    counter['parse_sent']+=1
    return N(text=' '.join(tokens))
sents=[['fixture'] for _ in range(4)]
parse_sents=method(rel, '_parse_sents', {'_split_sentences':lambda text:sents})
led=ledger_for(['fixture']*4)
led._parse_sent=parse_sent
led._parse_sents=lambda text:parse_sents(led,text)
led._informed_after=lambda *a:None
drive=method('hdlab/belief_reader.py','drive',{
    'WorldEvent':BT['WorldEvent'],
    'extract_belief_assertions':lambda *a:[],
    'extract_inference_edges':lambda *a:([],{}),
})
for query in range(2):
    before=counter['parse_sent']
    drive(sents,{i:[] for i in range(4)},fact,['alice'],led,
          reality_events=[('garden',0),('garden',1),('garden',2)])
    print('O01_PARSE_CALLS',json.dumps({
        'query':query+1,'sentences':4,'reality_events':3,
        'parse_calls':counter['parse_sent']-before}))
print('SCOPE: extracted real ledger/driver control flow with controlled absence, parsing and testimony; no model inference')
```

**Output, exit 0:**

```text
LIBRARY hdlab/belief_timeline.py 90d6bda0b9bfa99381a276bb740f8e170af8b9689b8663fcebe08909e9d8db0e
R06_FUTURE_TESTIMONY {"sentence_count": 1, "absent_at_event": true, "informed_somewhere": false, "marked_observed_at_event_0": false, "belief_at_0": null, "belief_after_testimony": null}
R06_FUTURE_TESTIMONY {"sentence_count": 3, "absent_at_event": true, "informed_somewhere": true, "marked_observed_at_event_0": true, "belief_at_0": "garden", "belief_after_testimony": "garden"}
O01_PARSE_CALLS {"query": 1, "sentences": 4, "reality_events": 3, "parse_calls": 12}
O01_PARSE_CALLS {"query": 2, "sentences": 4, "reality_events": 3, "parse_calls": 12}
SCOPE: extracted real ledger/driver control flow with controlled absence, parsing and testimony; no model inference
```

#### Final source check

```python
import ast, datetime, hashlib, json, pathlib
root=pathlib.Path(r'C:\AI\hd-instrument')
files=['hdlab/situation_reader.py','hdlab/goal_register.py','hdlab/state_register.py',
       'hdlab/belief_reader.py','hdlab/belief_timeline.py','hdlab/perceptual_access_ledger.py',
       'hdlab/coref.py','hdlab/lexical_categories.py','hdlab/joint_relation_frontend.py',
       'hdlab/world_state_register.py','hdlab/bound_event_backbone.py','hdlab/theory_of_mind.py']
print('CHECKED_AT_UTC',datetime.datetime.now(datetime.timezone.utc).isoformat())
for rel in files:
 raw=(root/rel).read_bytes()
 ast.parse(raw.decode('utf-8-sig'))
 print(json.dumps({'file':rel,'sha256':hashlib.sha256(raw).hexdigest(),'lines':len(raw.splitlines())}))
reader=ast.parse((root/'hdlab/situation_reader.py').read_text(encoding='utf-8-sig'))
cl=next(n for n in reader.body if isinstance(n,ast.ClassDef) and n.name=='SituationReader')
init=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
pairs=zip(init.args.args[-len(init.args.defaults):],init.args.defaults)
print('RELEVANT_DEFAULTS',[(a.arg,ast.unparse(v)) for a,v in pairs if a.arg in
      {'track_belief','track_goals','track_tom_action','track_prediction','bind_entity_states',
       'track_goal_thwart','discover_pronouns','graded_anaphora'}])
```

**Output, exit 0:**

```text
CHECKED_AT_UTC 2026-09-15T23:53:04.633780+00:00
{"file": "hdlab/situation_reader.py", "sha256": "2210b4bb21c97d2d6eed42220e2b44105d1b2ed5dbb78b50e1ed2bc718cbf517", "lines": 5548}
{"file": "hdlab/goal_register.py", "sha256": "b5e2f567902207c21ceeaedc7d8a343db55d32b05f8271b1acfefc03861d19f6", "lines": 819}
{"file": "hdlab/state_register.py", "sha256": "d6cd64248bb74cff6f1902e6d65ddc0a2477dfaefefeb5da4e7053a9e1d9d595", "lines": 511}
{"file": "hdlab/belief_reader.py", "sha256": "9450e26f880af3e4663e2efed83251433296da1afdd17c014d0195a3dcd91952", "lines": 493}
{"file": "hdlab/belief_timeline.py", "sha256": "90d6bda0b9bfa99381a276bb740f8e170af8b9689b8663fcebe08909e9d8db0e", "lines": 422}
{"file": "hdlab/perceptual_access_ledger.py", "sha256": "7597772e650f365adc87868d5f52fe4bace1e0d7bca1967d2639ad75eb31d8cc", "lines": 748}
{"file": "hdlab/coref.py", "sha256": "3af303cf28532693d9ead9cda7393a3637b477d5a6131fd5c95405c21e6e99ff", "lines": 1331}
{"file": "hdlab/lexical_categories.py", "sha256": "8bddc3668560fa4a1c1563f6720bc67c5568ed85f4478b1e6578cdff36408d88", "lines": 1569}
{"file": "hdlab/joint_relation_frontend.py", "sha256": "7417cd0c54c4cbedd55ce88a24089eb7ffc0f4bc497c445b98d39b084b99b229", "lines": 816}
{"file": "hdlab/world_state_register.py", "sha256": "5f2ce0f396423a0eb964ca9d6b0e2dbfe8a706519c5e162fd79e0b67bac58a59", "lines": 300}
{"file": "hdlab/bound_event_backbone.py", "sha256": "83ee0a3e5549e217895f3c2067695912555bb7cb85eeaf1d565f330156734f0b", "lines": 256}
{"file": "hdlab/theory_of_mind.py", "sha256": "42b3bc28c4b21ea6ef0bf7b3ed847eff219c4885be0e033e9cb3d9da9a95866c", "lines": 180}
RELEVANT_DEFAULTS []
```

The constructor-default inventory printed an empty list because it inspected positional defaults rather than keyword-only defaults. It is not evidence that the capabilities are disabled. No claim in this follow-up depends on that inventory. The file hashes and syntax checks completed successfully.

#### Final follow-up document check

Executed with the same wrapper above; reads this report only:

```python
import pathlib, re
p=pathlib.Path(r'C:\AI\hd-instrument\notes\SUBSTRATE_EVALUATION.md')
s=p.read_text(encoding='utf-8')
assert 'LATEST REVIEW COMPLETE' in s
for key in ['R01','R02','R03','R04','R05','R06','O01']:
 assert len(re.findall(r'^### '+key+r'\.',s,re.M))==1
assert '### A11. Focused follow-up: exact commands, controlled probes and outputs' in s
assert s.index('## Focused follow-up:')<s.index('## Current-code deep review')
assert len(re.findall(r'^```[^\r\n]*$',s,re.M))%2==0
print('REPORT_OK',str(p))
print('FOLLOW_UP', '6 findings; 1 optimization; exact probes and outputs present')
```
