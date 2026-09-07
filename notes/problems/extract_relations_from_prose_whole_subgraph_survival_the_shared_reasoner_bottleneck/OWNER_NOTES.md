---
owner_verdict: DONE
---

SUBMISSION — extract_relations_from_prose_whole_subgraph_survival_the_shared_reasoner_bottleneck
STATUS: PARTIAL (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference, NO training.
NO hdlab/ written (Q111 — a PROPOSED additive diff, not landed). Ledger: malformed/incomplete 0.
Reverify (headline): .venv/Scripts/python.exe verification/test_joint_temporal_survival.py
  Full suite: 7 witnesses / 22 checks green (survival, MAVEN generalization, real-reasoner end-to-end, third-reasoner
  + nominal-WSD, spatial located-negative, upstream/roles/no-regress). Determinism pinned (PYTHONHASHSEED guard).

WHAT I BUILT. ONE glass-box joint relation-extraction front-end (experiments/_joint_relation_frontend.py) that PARSES
EACH SENTENCE ONCE (hdlab.pos_tagger + hdlab.arc_parser) and reads events, states, spatial edges, and roles off that
SINGLE dependency structure — the brain-foundational property (a clause's relations are extracted JOINTLY in one
structural pass; PINNED — Friederici IFG structure-building -> pMTG/ATL role binding; Bach neo-Davidsonian event
variable; Talmy/Jackendoff Figure-Ground). The incumbent does the opposite: THREE separate front-ends, two of which
throw the parse away (the spatial extractor loads the parser then does a LINEAR nearest-noun scan; the temporal
extractor uses a separate tagger and TENSE-GATES events) — which is exactly why within-clause edges fail independently
and multi-hop chains die at the exponent rate. Metric = WHOLE-SUBGRAPH SURVIVAL (every edge of a >=2-hop chain
recovered), extraction ISOLATED (reasoner held at gold-perfect), paired bootstrap over chains.

RESULTS (per channel; a rigorous located negative is a full pass per the bar):
 TEMPORAL — CLEARS, and is largely closed:
  - TB-Dense (22 modern-newswire docs, 333 multi-hop BEFORE/AFTER chains): survival incumbent 0.1111 -> joint 0.4054
    (+0.2943 CI[0.2462,0.3453], null_p95 0.0601); + the WordNet eventive-NOMINAL channel -> 0.7327 (+0.6216 CI-sep);
    event recall 0.320 -> 0.891. Info-free twin 0.000 loses CI-sep. Decay lifts at every hop.
  - The COPULAR/STATIVE channel specifically lifts stative-touching OVERLAP-edge survival +0.0413 CI[0.0206,0.0649]
    (the temporal SOLVED's named P2 lever, recovered).
  - END-TO-END through the ACTUAL solved connective+tense reasoner (not a proxy): answered-correct incumbent 0.0971 ->
    joint_cop 0.3480 -> joint_nom 0.4937 (+0.3966 CI-sep) = 87% of the gold-event CEILING 0.5681; conditional accuracy
    NOT degraded by nominal over-extraction (coverage 0.58 -> 0.85 for free).
  - GENERALIZED at 100x power on MAVEN-ERE (710 modern Wikipedia docs, 43,599 chains via transitive reduction, NO LDC
    caveat): survival 0.086 -> 0.413 (cop) / 0.777 (nom), +0.3275 CI-sep, twin loses, decay holds to 24 hops.
 SPATIAL — LOCATED NEGATIVE, correctly attributed (I drilled + corrected my own first claim): the unified Figure-Ground
  frame binder matches the incumbent (6/90) with FEWER constructions; the hybrid reaches 9/90 (modest, not CI-sep at
  n=90). The wall is CONSTRUCTION COVERAGE + entity resolution (74% of the deficit), NOT parse UAS (10%) — reproducing
  the spatial SOLVED's own 74%/10% split on a fresh decomposition. My earlier "parse UAS is the residual" was WRONG.
 ROLE — served LIVE off the same one parse (agent/patient/goal/source/recipient/path). DISK-vs-BRIEF correction:
  role_route='wired' is DEFAULT-ON (situation_reader.py:838), not default-off as the brief states.
 APPRAISAL (the THIRD reasoner) — extraction lever MEASURED: the joint pass recovers the OUTCOME event on EVERY OCC gold
  item (37-39/44 -> 44/44) that the incumbent's tense-gate drops. It unstarves the EXTRACTION half; the residual is the
  appraisal SOLVED's SEMANTIC goal<->outcome matching (the reasoner's wall, not the front-end's).

CONTROLS (each excludes something): info-free TWIN at survival level (random same-size set -> 0.000) AND reasoner level
(shuffled positions -> chance) both lose CI-sep; SAME-TAGGER control (tense-agnostic on the incumbent's own tagger)
isolates the tense-GATE from the tagger; GOLD-event ceiling + recall-by-class isolate extraction from the reasoner;
NO-REGRESS (joint front-end writes nothing to hdlab; live reader reads 35 events intact, byte-identical when off).

KEY REALIZATIONS (the enabling moves):
 1) The incumbent runs three front-ends and two throw the parse away — "parse once, read all channels off the same
    tree" is both the brain-foundational fix and the anti-exponent mechanism (within-clause edges share the parse's
    fate). Finding the parse was loaded-but-ignored was the unlock.
 2) "A state is an event" and "a nominalization is an event" are the SAME brain fact — the event variable is
    category-agnostic; tense and POS were both artifacts hiding it. WordNet lexical-semantic detection (eventive sense
    + deverbal) took nominal-event recall 0.10 -> 0.70 and was the single biggest survival lever.
 3) I MIS-ATTRIBUTED the spatial wall to parse UAS, then drilled it and corrected to construction coverage — the same
    class of error as a prior problem's mis-attribution. Research a hand-waved wall and it moves.
 4) Use the ACTUAL solved reasoner, not a proxy — it raised joint_nom to 87% of ceiling and proved the nominal
    over-extraction doesn't degrade accuracy.
 5) A faithful-sounding theory can be the WRONG mechanism for a sub-task — Grimshaw's argument-structure gate CRUSHED
    nominal recall (0.70 -> 0.20 on bare news-nominals), which is itself the evidence the precision residual is
    SEMANTIC (the WSD channel), not syntactic. Testing the shortcut located the wall.
 6) A dense gold needs the right metric — MAVEN's near-transitively-closed graph yields 0 naive chains; the transitive
    REDUCTION recovers the necessary-spine chains and the result generalizes.

AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md): TIME front-end extraction wall now LARGELY CLOSED + measured via
whole-subgraph survival on two modern golds (recall 0.32->0.89, survival 0.11->0.73, end-to-end 87% of ceiling);
copular/stative overlap lever + eventive-nominal channel are the mechanisms. SPACE wall = construction coverage + entity
resolution (74%), NOT parse UAS (10%) — corrects an overstated attribution. sec.1 "front-end is the constraint" refined:
the binding constraint differs per reasoner (temporal detection = closed; spatial coverage; appraisal semantic matching).
Brief correction: predicate_argument_frontend is DEFAULT-ON (role_route='wired'), not default-off.

FOR STRATEGY (Q111 — I propose, do NOT land): promote _joint_relation_frontend.py as a shared hdlab organ that parses
each sentence once and exposes events (tense-agnostic + copular/stative + WordNet-nominal), spatial edges, and roles from
ONE ParseResult; in situation_reader, route the temporal event detector through the enriched pass (default-off flag) and
feed temporal_reasoner the enriched event set. Additive (byte-identical when off). Do NOT wire the parse-based spatial
extractor (coverage-gated, measured).

PRIORITY NEXT STEPS:
 P1 (HIGHEST, STRATEGY, ready now): LAND the enriched joint temporal event detector + wire temporal_reasoner — the ONLY
    step that makes the proven gain (survival 0.11->0.73, end-to-end 0.10->0.49) board-visible. No-regress confirmed.
 P2 (follow-on problem, SPACE): a whole-sub-graph construction+entity spatial extractor (the real lever = coverage, not
    the parser); fold the full construction inventory onto the unified frame binder + strengthen entity resolution.
 P3 (follow-on problem, MEANING): a context/WSD gate for event-vs-result nominal disambiguation (makes the nominal
    channel a safe production default; Grimshaw syntactic gating drilled + rejected).
 P4 (follow-on, AFFECT): appraisal semantic goal<->outcome matching (the appraisal SOLVED's own named next-problem; this
    front-end's extraction lever is already done/measured).
 P5 (lower): the labeled/incremental upstream parser (secondary 10% spatial lever; already a filed PARTIAL problem).

TLDR (plain English): three "thinkers" — for space, time, and how a character feels — each work almost perfectly on
clean facts but stall on real stories, because the reading step pulls out too few of the little "X relates to Y" facts
and a chain of reasoning needs every link. I built one reading step that reads each sentence once and pulls out all the
facts the way the brain does. For TIME it works strongly: the old step only counted past-tense happenings and threw away
states ("the door was open"), present-tense happenings, and events named as nouns ("the attack"); mine keeps them all —
so where the old step let the time-thinker answer about 1 in 9 whole chains, mine lets it answer about 7 in 10, and
end-to-end it now does nearly as well as if handed perfect facts, on two modern sources (news and Wikipedia, the second
100x larger), with a scrambled-facts version falling apart. For the FEELING thinker it makes sure the story's outcome is
always captured (the old step missed it 1 in 7 times); what's left is a separate common-sense step. For SPACE it does NOT
yet clear the bar, and I corrected my own first explanation — it's not mainly the grammar parser, it's that the reader
knows fewer ways of SAYING where things are ("the box holds the key", "there is a key in the box"); adding those is the
next step. The reading step changes nothing about the existing reader and feeds all three thinkers off the same reading.

QUESTIONS: none blocking. One judgement call: I marked this PARTIAL, not SOLVED — TIME clears the headline metric on two
modern golds and end-to-end; the FEELING extraction lever is measured; SPACE is a rigorous, correctly-attributed located
negative. The bar's own text gives this exact shape as a FULL PASS, so a SOLVED reading is defensible; I chose the
honest, deflated label. Promote to SOLVED if you read the bar as met.

NEXT STEPS: land P1 (the board-visible temporal win), then file P2/P3/P4 as their own briefs (each a distinct organ, not
this front-end). Nothing more to build under this slug — the mechanism work is done; what remains is landing + three
located follow-on organs.
