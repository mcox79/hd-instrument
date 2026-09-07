---
owner_verdict: DONE
---

SUBMISSION -- compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain
status: PARTIAL (WIP until owner_verdict: DONE). Glass-box, NO external LLM at inference. NO hdlab/ written
(Q111 -- proposed wires below). Wrote only experiments/, verification/, notes/problems/<slug>/. Ledger --check
clean (malformed 0). Reuses data/corpora/gum/ (pinned V12.1.0).

REVERIFY (6 witnesses, all green):
  .venv/Scripts/python.exe verification/test_hybrid_unified_incumbent_coref.py   # 11/11 (located negative + faithfulness)
  .venv/Scripts/python.exe verification/test_person_feature_coref_optimize.py    # 6/6  (phi live gain, real reader)
  .venv/Scripts/python.exe verification/test_coref_ceiling_drill.py              # 6/6  (residual decomposition + him-narrow)
  .venv/Scripts/python.exe verification/test_coref_gender_suppress.py            # 6/6  (the +0.082 cumulative ladder)
  .venv/Scripts/python.exe verification/test_gender_organ.py                     # 6/6  (glass-box gender organ removes gold leak)
  .venv/Scripts/python.exe verification/test_coref_closeout_drill.py             # 4/4  (residual = genuine glass-box floor)

TWO HEADLINES on MODERN gold (GUM V12.1.0, 137-doc TEST, n=1240 he/she; scorer = size-robust last-nominal identity,
== the live reader's head_to_cluster on the fragmented arm; anchors reproduce the audit EXACTLY: incumbent 0.5032,
port 0.4331):

1) THE BRIEF'S COMPOSE MECHANISM IS A RIGOROUS LOCATED NEGATIVE (a full pass per the bar; keep it OFF).
   Feeding the unified referent to the incumbent graded pool does NOT beat the live incumbent: HYBRID 0.4750 vs
   incumbent 0.5032 (delta -0.028, CI includes 0). Controls that make it rigorous: the shuffled-grouping TWIN LOSES
   (0.3556 -> the merges ARE real signal, not "any re-keying"); ORACLE (perfect gold-cluster unification) ALSO fails
   (0.4661) -> the ceiling is SUBSUMPTION, not clustering quality; the ACT-R decay d-sweep {2..6} does not recover it.
   Unification MONOTONICALLY helps the weak isolation scorer (0.3411->0.3935->0.4065) but HURTS the strong incumbent
   scorer (0.5032->0.4750->0.4661): the two brain systems are ANTAGONISTIC on this population, not complementary
   (merging inflates the protagonist's ACT-R activation and blurs the recency the tuned pick needs; generic-suppression
   already prunes the junk unification would consolidate). => keep hdlab/unified_referent.py DEFAULT-OFF.

2) THE UNDERLYING GOAL -- A LIVE COREF GAIN -- IS DELIVERED BY DIFFERENT, BRAIN-FOUNDATIONAL LEVERS. Disk outranks
   brief: the brief ASSUMED person-feature exclusion is in the incumbent pool; grep shows graded_coref_pick.phi_agreement_keep
   is LANDED-but-DORMANT (never called by _graded_pool_pick). Wiring it + two more fidelity fixes STACKS, CI-separated,
   on the ACTUAL EventCentralityReader (native scorer):
     live incumbent                                          0.5032
     + person-feature filter (phi, dormant organ)            0.5419  (+0.039)  twin loses; +0.091 in first-person genres
     + agreement-narrow on 'him' (agreement is general)      0.5581  (+0.055)  +0.176 on the him subset
     + soften generic-suppress (drop never-subject proxy)    0.5855  (+0.082 CI[0.066,0.098] CI-SEP)  16% relative lift
   All three are recall-safe / register-fidelity, additive, no new organ, no gold, no LLM.

DEEPENING (owner push -- prototyped + drilled to the floor):
- GENDER ORGAN prototyped (glass-box: given-name gazetteer + role-noun lexicon + morphology + gated propagation).
  It exposed a HIDDEN GOLD LEAK (the harness fed entity gender from GUM's gold Gender feat) and MATCHES it with no
  loss (0.5887 vs 0.5855, 100% agreement where both fire) -> the whole +0.08 stack runs with NO gold at inference.
  It is a FIDELITY win, NOT an accuracy lever: gender is ~6%-sparse on modern nominals (the CAP). Coreferent gender
  propagation is a LOCATED NEGATIVE (-0.010 even gated). Dropping the hard agreement-narrow floods the pool (-0.036).
- CLOSE-OUT: the full-stack residual is the GENUINE GLASS-BOX FLOOR. Of reachable mispicks, 67% are same-gender
  ambiguity; the topicality cue is NOT a lever (dev-sweep picks the baseline weight, delta 0.000). Every wall is now
  drilled to either a shipped fix or the floor; the rest needs world-knowledge / a coherence prior (both no-LLM-barred
  / owner-DONE-dead x2) = the priority-1 individuation North Star, a separate program.

PROPOSED hdlab WIRES (Q111 -- strategy lands; reference impls in experiments/):
  1. LAND THE FULL STACK as ONE default-ON change in event_centrality_coref:
     (a) phi_agreement_keep(pron_low, prior_mention_heads, animacy=None) as a pool pre-filter in _graded_pool_pick
         (TIER1, recall-safe; thread a midx->head map through resolve_stream). ref: CleanReader in
         exp_person_feature_coref_optimize_gum_v1 (filter=off is byte-identical to the live reader).
     (b) apply _agreement_narrow to 'him' (add it to the narrow slots / narrow the adaptive path).
     (c) GenericDistractorFilter(..., use_struct=False) (keep use_nonref=True).
     => 0.5032 -> 0.5855, +0.082 CI-sep, recall-safe, named no-regress. Default-ON justified (no-more-default-off).
  2. KEEP hdlab/unified_referent.py DEFAULT-OFF; do NOT add a unified_referent_hybrid path (subsumption, oracle-confirmed).
  3. (fidelity) replace the gold-gender leak with GenderOrganizer (exp_gender_organ_gum_v1) -> no-gold at inference.
     Do NOT wire coreferent gender propagation.

DO NOT:
- quote the isolated +0.106 unified-referent lift as a live gain (different scorer/population).
- quote the port's 0.4331 as the hybrid's result (that's the SWAP; the hybrid is unified-pool x incumbent-scorer).
- add a hybrid unified_referent path (regresses the live incumbent -0.028; oracle also fails).
- use dominant-cluster scoring for the merged arms (size-gamed -- the shuffled twin beat the hybrid under it;
  primary scorer is last-nominal identity, which reproduces the incumbent anchor).
- wire coreferent gender propagation (net-negative even gated), or drop the hard narrow (floods).
- rely on gold Gender at inference (the organ replaces it); use a 19c corpus; use an external LLM.

KEY REALIZATIONS:
- Validate the harness against the LIVE substrate BEFORE trusting any number: forcing the reimplementation to
  reproduce the real reader's 0.5032 and the port's 0.4331 EXACTLY made the negative trustworthy and caught two
  real bugs (the port writes back ALL pronouns; it completes gender from a resolved pronoun, steering later merges).
- A scorer can be gamed by the very structure under test: dominant-cluster rewarded big merged groups, so a shuffled
  twin BEAT the hybrid; the size-robust last-nominal scorer flipped it to a clean loser and revealed the honest tie.
- The ORACLE control separates a fidelity gap from a fundamental negative: perfect unification STILL loses ->
  subsumption, not clustering -> no upstream work rescues it (answers the escalation directly).
- The disk outranked the brief and that WAS the win: the brief's wrong premise (phi already in the pool) pointed
  straight at the dormant organ that is the actual live gain.
- Drill "could it have succeeded" before "why did it fail": recall@compatible is 0.97 -> the wall is HARD-FILTER
  OVER-REMOVAL (28%), not world-knowledge (3%). That reframe surfaced the him-narrow + soften-suppress fixes.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md sec 2b, E3 coreference):
- CONFIRM unified_referent DEFAULT-OFF, reason now MECHANISTIC (subsumption + antagonism; oracle + d-sweep).
- NEW: the live incumbent pool does NOT apply person-feature exclusion (phi_agreement_keep landed-but-dormant);
  wiring it + him-narrow + soften-suppress is a +0.082 CI-sep live gain on modern gold, and a glass-box gender organ
  removes a gold-Gender leak at no cost. Live coref chain is computationally brain-foundational and now materially
  more faithful; residual is genuine ambiguity (individuation North Star), not a missing organ.

NEXT PRIORITIES:
- HIGH: land the full stack (phi + him-narrow + soften-suppress) as one default-ON change (+0.082 CI-sep). THE deliverable.
- HIGH: keep unified_referent DEFAULT-OFF; fold the mechanistic reason into the audit.
- MEDIUM: swap the gold-gender leak for the glass-box gender organ (no-gold at inference; fidelity, not accuracy).
- FOLLOW-ON PROBLEM: route the unified referent to the NON-coref consumers (entity-KB / affect / situation-model
  entity layer) -- that is where its +0.05-to-+0.11 lever actually lives, not the tuned he/she pick.

TLDR (plain English): We tried feeding the reader's "one shared record per character" idea into its already-strong way
of guessing who "he"/"she" means. It did NOT help -- it slightly hurt -- and we proved why even a perfect merge fails,
so that shelved feature stays correctly off. But we found the real win a different way: three small brain-faithful fixes
(ignore the speaker "I"/"we"; apply the gender check to "him"; stop over-filtering ordinary nouns like "the woman") take
the live guess from about 50 to 59 right in 100 -- a controlled 16% jump that a scrambled version can't fake and that
never hurts named characters, biggest on interviews/forums. We also built a small glass-box "gender guesser" so it runs
without peeking at any answer key, and chased the leftover mistakes to the bottom: they are genuine ambiguities that need
outside world-knowledge our no-outside-AI rule forbids -- the honest ceiling. All of it is a handful of one-line changes
to land.

QUESTIONS: none blocking. One judgement call: the filed problem is the shared-record COMPOSE (a located negative); the
live gain comes from DIFFERENT dormant machinery (speaker filter + agreement + suppression). If you want that landed
under its own slug rather than this one, say so -- the measurements and wires are ready either way.

NEXT STEPS: land the full stack default-ON (+0.082); keep unified_referent off; swap in the glass-box gender organ; file
the non-coref-consumer follow-on; do NOT reopen the he/she residual (genuine floor = the individuation North Star).
