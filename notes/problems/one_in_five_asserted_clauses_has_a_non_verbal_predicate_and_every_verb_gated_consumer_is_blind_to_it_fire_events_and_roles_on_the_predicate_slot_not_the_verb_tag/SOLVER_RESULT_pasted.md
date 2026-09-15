

## pasted by the owner 2026-09-14 19:25 (raw; strategy reads this)

pri 113 -- one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag

PARTIAL (strong core + located, prototyped upstream negative). Built the PARTICIPANT INSTRUMENT pri 110 10f
specified (UD-EWT test 700; 762 subject-bearing gold clauses, 167 non-verbal; scored by ARGUMENT STRUCTURE --
does the fired event GOVERN a gold core argument -- never the tag column; twin at floor, oracle 1.0, gold-free
at decision).

COMPONENTS TOUCHED (detail + BF verdict in SOLVED.md 33a):
- Event detector (situation_reader._tense_agnostic_extract): PROPOSED diff -- fire the clause event/state on the
  copula's COMPLEMENT, is_state=True, co-indexed with the state reader. Today gates on UPOS=="VERB" (a UD-convention
  proxy, NOT BF); the fix makes it BF (one predicate per clause). PROVEN: non-verbal event recall 0.1856 -> 0.7365
  (+0.5509 CI[+0.4789,+0.6228] SEP), pooled precision 0.8358 -> 0.8244 (held), verbal unchanged 0.9950, twin 0.2635
  loses, oracle 1.0000, BOARD A/B byte-identical on all 7 dims (the board is VERB-gated too -- exactly why 10f
  asked for the participant instrument). Generalizes on GUM (12+ genres): floor 0.078 -> slot 0.571 SEP.
- Copula scan (attachment_arm.cop_predicates): PROPOSED diff -- surgical locative + clause-final fallback (ADV only
  as fallback; the ADV-inline negative is measured and avoided). BF-neutral coverage extension.
- Arc scorer (attachment_arm, heads rung): PROTOTYPED -- predicate-slot-biased re-attachment as a GRADED arc feature
  + held/reshape decode: non-verbal attachment 0.5385 -> 0.6509 (exceeds MAP ceiling), verbal flat; propagates to the
  event stream (0.6048 -> 0.7186) and entity binding (0.71 -> 0.89). MUST land with an ONLINE-learned validity
  (Rescorla-Wagner), never frozen.
- Role competition (graded_role_assigner._parent_config, _PRED_HC): PROPOSED diff -- key PRED on predicate-hood not
  the VERB/AUX tag, so a non-verbal predicate's OBLIQUES inherit predicate expectations (located gap 0.53 -> ~0.83).
  Needs a role-table rebuild (like pri 108). Subject is already 0.84.
- Entity-state route (copular_binding + state_register): PROPOSED (architectural, the REAL PATH, section 14) -- a
  Kimian state is a TYPED ATTRIBUTE on the entity, not an eventive record (which is why the event-token metric
  plateaued and the eventive board stayed byte-identical). Prototyped: typed-attribute capture 0.35 -> 0.56, holder
  0.85. Gate the write on subject-coref binding; unlocks type-licensed inference + attribute bridging/coref (fail
  SILENTLY today).
AUDIT UPDATE: situation_reader's copular-state-as-event compute is BF but ISLANDED in the temporal reasoner
(byte-identical to sm.events off/on) -- landed != live; diff 2 lands it in the main stream.

NOT MET, located upstream with numbers (the bar's OR-clause): >=0.90 recall (0.7545 strict / 0.8204
state-registered) and the CI-separated role bar. KEY LEVERS to close it (SOLVED.md 33b, ranked):
1. Glass-box learned-semantic CONTEXTUAL encoder on ALL arcs -- the #1 wall vs SOTA. POSITIVELY indicated: a weak
   form-based contextual-HRR feature already adds +0.089 (0.5385 -> 0.6272). Strategy's cross-cutting build (filed
   distributed_contextual_representations_into_the_parser), NOT a solver cell.
2. Land the heads correction with an online-learned copular-subject validity (prototype 0.65, propagates +0.18).
3. Route to the entity-state register as a typed attribute gated on coref (diff 4).
4. Close the cheap tail of the 65 (Type-2 interrogatives + Type-3 locative agreement via on-demand number-agreement);
   Type-1 true-inverse/specificational is the PRINCIPLED ceiling (discourse-givenness-bound -- needs a discourse
   tracker + morphological agreement the substrate lacks). 65 residual: HIT 123, clausal 14, inverted 10, mistag 15,
   no-copula 5.

Files: experiments/exp_nonverbal_predication_participants_v1.py, notes/problems/<slug>/{SOLVED.md,
predicate_slot_consumers_patch.diff}. No hdlab/ edited BY THIS SOLVER (proposals only; the working tree's modified
lexical_categories.py + situation_reader.py are the owner's concurrent pri-110/106 edits). Re-anchor the diffs
before git apply -- the live situation_reader.py has moved since tag comparison_pri113_base. Reverify: --self-test ;
--participant --cap 700 --gate all ; --diag65 ; --decompose ; --heads-fix ; --board --arm base|slot.
