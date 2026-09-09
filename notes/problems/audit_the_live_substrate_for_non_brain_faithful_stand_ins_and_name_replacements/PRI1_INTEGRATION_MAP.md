# How pri-1 (the generative world-model) feeds the parser cluster AND every consumer that needs it

**Companion to `CATALOG.md` + `PARSER_SIGNAL_TRACE.md`.** The audit + the three powered parser drills converge on ONE
deep fix — pri-1 `build_the_generative_result_state_world_model`. This file makes "reference pri-1" concrete: the exact
top-down interface, per consumer, so each re-architecture follow-on is properly scoped. It does NOT rebuild pri-1.

## THE UNIFYING INSIGHT (why pri-1 is THE lever, established by the drills, not asserted)
The three drills proved the parser's reliability signal collapses out-of-register for a specific reason: **every signal
derivable from the frozen parse — peak magnitude, entropy/shape, arc-eager conf, lexical-grounded selectional
preference, in-sentence global settle — is a property of the SENTENCE + the parser's TRAINING CORPUS, and none of them
survives off that corpus** (all ~0.55 AUC OOD, near chance). The information that disambiguates the hard cases is not in
the sentence or the parser weights at all — it is the **top-down expectation from the story so far** (which participant
the discourse predicts, what result-state the last event produced, what the goal is). That expectation is **content-
derived and register-invariant** (it is about the STORY, not the training corpus), which is exactly why it is the one
signal that can hold OOD. **pri-1 is the organ that GENERATES that expectation.** So pri-1 is not "a better cue" — it is
the missing SOURCE of the register-robust, content-derived top-down signal the entire feed-forward reader lacks (the
WALL_MAP "feed-forward silos vs one recurrent top-down loop" finding, quantified here).

## WHAT pri-1 EMITS (from its brief, composing landed organs)
A content-sensitive generative rollout over the resolved participants produces a **TOP-DOWN EXPECTATION** with these
projections (each is what a downstream consumer reads):
- **E1 expected next-event / expected participant** — `generalized_event_knowledge` (`sm.predict_next_event` / GEKProjector).
- **E2 expected RESULT-STATE over resolved participants** — `force_dynamics_typer` (force→result-state) + `event_type` (mental cascade) + `affect_register` + `belief_partition`.
- **E3 goal-STATE** — `goal_register` (desire/intention → the state the agent is trying to reach).
- **E4 expected CAUSE / antecedent** — the generative cause-antecedent search (recency prior + E2 typing).
All four ride the **meaning channel** (`meaning_foundation`, currently LATENT) over **coref-resolved** participants —
so the two hard preconditions are: (a) the meaning channel wired live at read() time, (b) the C1 gold-coref leak
replaced by real online clustering (pri-6). pri-1 is starved without both.

## THE FEED, PER CONSUMER (grouped by the binding constraint from PARSER_SIGNAL_TRACE.md)

### A. ATTACHMENT-bound consumers — pri-1 supplies the top-down term that closes the recurrent loop
| consumer | pri-1 projection it consumes | the interface (how it wires) | what it resolves (trace residual) |
|---|---|---|---|
| **who-did-what / role assign** (C3 parser cluster; `graded_role_assigner` + the graded-competition attach settle) | **E1 expected patient** given the situation so far | add the expectation as a TOP-DOWN cue term in the normalized-recurrence attachment competition (the 4th move of the C3 design: posterior → commit → joint settle → **top-down loop**). The expected-patient activation biases the settle. | the **35.2% gold-not-attached / two-valid residual** that no bottom-up score and no in-sentence signal resolves; and the **OOD-robust reliability** the frozen parser lacks (E1 is content-derived, register-invariant) |
| **spatial** (`spatial_relational_model`) — but note attachment is only ~10% here | **E2 expected figure/ground result-state** + construction expectation | the expected located-entity biases the obl/figure-ground binding | the residual attachment share; the DOMINANT spatial wall (construction coverage 35% + entity recognition) is fed by B below |
| **goal bare-purpose** (`goal_register`) | **E3 goal-state** | the expected goal biases advcl(purpose)-vs-xcomp attachment on the bare tail | the attachment-gated bare-purpose tail (explicit slice already at oracle) |
| **polarity scope** (`polarity_operator`) | (indirect) a better-attached parse | the parse-aware resolver becomes usable once C3's attachment improves | the parsed resolver's current loss (0.9091<0.9318) is parser-attachment noise |

### B. DETECTION / COVERAGE-bound consumers — pri-1 supplies the expectation that makes the missing element detectable
| consumer | pri-1 projection | the interface | what it resolves |
|---|---|---|---|
| **spatial coverage** (the real wall) | **E2 expected result-state** (where the entity ends up) | the generative expectation proposes the unstated figure/ground → construction/entity recovery | construction coverage 35% + entity recognition (74% of the spatial loss) |
| **temporal implicit order** (`temporal_reasoner`) | **E1 expected next-event** | the forward expectation OVERRIDES iconicity on implicit pairs (confident causal/irreversibility) | the 94% implicit pairs guessed at ~0.55 (the script prior's ~0.61 ceiling) |
| **causal unmarked** (`causal_reasoner`, `causation_typing`) | **E4 expected cause** over coref-resolved participants | the generative cause-antecedent proposes the unmarked edge; participant coref (E-precondition) lifts it 3.29× | unmarked causal edges (65.6% of MAVEN), coverage-bound at ~5% by retrieval |
| **copular/state detection** (`state_register`, robust_cop) | **E2 expected state predication** | the expectation of a state licenses the cop detection the labeler misses | the 29% `cop`-recall detection loss |
| **world-state recipient** (`world_state_register`) | **E2 transfer result-state** (recipient slot) + coref | the transfer schema's recipient expectation fills the iobj the parser drops | recipient-on-GIVE 0.33 (iobj LAS 0.72 + coref) |

### C. NOT parse-bound but needs the SAME discourse expectation (pri-1-adjacent)
| consumer | pri-1 projection | what it resolves |
|---|---|---|
| **pronoun coref** (`event_centrality_coref`) | E1 next-mention / coherence prior (Kehler-Rohde) | the ~19% competitive residual (a coherence/next-mention PRIOR — literally a top-down expectation) |
| **bridging** (`bridging_inference`) | E2 result-state / E4 cause bridge | the relatedness-estimator ceiling (the bridge is a generative inference, not retrieval) |
| **belief inference** (`belief_timeline`) | E2 mental result-state | (inference already exact given oracle; the observation-cue extraction it needs is upstream, not pri-1) |

### NOT fed by pri-1 (honest exclusions)
- **filler-gap** (`relcl_resolver`) — a specialised in-sentence circuit that IGNORES the general parse; pri-1 is orthogonal.
- **common-noun coref type comparator** — the residual is world-knowledge KB coverage (the type comparator), not a discourse expectation.
- **detection RECALL** (the tense-agnostic event fix) — already landed, upstream of pri-1.

## ORDERING (what must land, in what order — the top-down integration pass)
1. **Preconditions FIRST:** (a) C1 gold-coref de-leak (pri-6) — pri-1 rolls out over *resolved participants*; a leaked
   coref means the expectation is scored on a peek. (b) the meaning channel wired live at read() (DEBT-3) — pri-1's
   rollout reads result-state predicates over it.
2. **pri-1 itself** — the staged build (its own brief; scope one consumer + one modern gold first: SDRT/TellMeWhy).
3. **First consumer = the C3 parser cluster** — land moves 1-3 (globally-normalized posterior + commit + graded joint
   settle; already proven in `experiments/`), then wire E1 as the top-down term (move 4). This is where the OOD-reliability
   wall actually closes (E1 is the register-robust signal the drills proved is missing).
4. **Then B/C consumers descend** the trace's binding-constraint order (spatial coverage → temporal → causal → copular →
   world-state → coref prior → bridging), each consuming its E-projection, ONE thread at a time against a fresh board.

## HONEST BOUNDS
- pri-1 is a LARGE staged build (its own priority-1 brief) — this map is the **interface spec** that makes the audit's
  re-architecture entries (C3 and the consumer follow-ons) properly scoped, NOT the build.
- The reliability claim ("E1 is register-robust") is a **prediction from the drills' mechanism** (content-derived vs
  corpus-derived), not yet measured — the pri-1 build's own bar (a full-population OOD-robust CI-separated win with the
  info-free twin losing) is where it gets tested. The drills establish the NEGATIVE (in-sentence is exhausted) airtight;
  the POSITIVE (pri-1 closes it) is pri-1's to prove.
- Two consumers pri-1 does NOT help (filler-gap, common-noun type comparator) are named so the follow-on is not oversold.
